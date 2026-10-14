"""Authentication routes: register, login, JWT, password reset."""
from datetime import datetime, timedelta, timezone
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from pymongo.errors import PyMongoError

from database import get_database
from middleware.auth_deps import get_current_user
from models.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    db = get_database()
    try:
        existing = await db.users.find_one({"email": payload.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        doc = {
            "email": payload.email,
            "full_name": payload.full_name,
            "hashed_password": hash_password(payload.password),
            "role": payload.role,
            "created_at": datetime.now(timezone.utc),
            "xp": 0,
            "streak_days": 0,
            "badges": [],
            "last_active": None,
            "weak_subjects": [],
            "notification_prefs": {
                "quiz_reminders": True,
                "new_uploads": True,
                "ai_recommendations": True,
                "milestones": True,
            },
            "avatar_url": "",
        }
        await db.users.insert_one(doc)
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Start MongoDB on localhost:27017 (e.g. docker compose up -d), then retry.",
        )
    token = create_access_token({"sub": payload.email, "role": payload.role})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    db = get_database()
    try:
        user = await db.users.find_one({"email": payload.email})
    except PyMongoError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Start MongoDB on localhost:27017, then retry.",
        )
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_active": datetime.now(timezone.utc)}},
    )
    token = create_access_token({"sub": user["email"], "role": user.get("role", "student")})
    return TokenResponse(access_token=token)


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    """Issue a reset token (returned in response for demo; email integration omitted)."""
    db = get_database()
    user = await db.users.find_one({"email": body.email})
    if not user:
        return {"message": "If the account exists, reset instructions have been sent."}
    raw = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"reset_token": raw, "reset_expires": expires}},
    )
    return {"message": "Password reset token issued.", "reset_token": raw}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    db = get_database()
    user = await db.users.find_one({"reset_token": body.token})
    if not user or not user.get("reset_expires") or user["reset_expires"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    await db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"hashed_password": hash_password(body.new_password)},
            "$unset": {"reset_token": "", "reset_expires": ""},
        },
    )
    return {"message": "Password updated"}


@router.get("/me")
async def me(user: Annotated[dict, Depends(get_current_user)]):
    user.pop("hashed_password", None)
    user.pop("reset_token", None)
    user.pop("reset_expires", None)
    user["_id"] = str(user.get("_id", ""))
    return user
