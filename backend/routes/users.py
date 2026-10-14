"""User profile, password, settings."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from database import get_database
from middleware.auth_deps import get_current_user, require_roles
from models.schemas import PasswordChange, ProfileUpdate, SettingsUpdate
from utils.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me")
async def update_profile(payload: ProfileUpdate, user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if updates:
        await db.users.update_one({"_id": user["_id"]}, {"$set": updates})
    fresh = await db.users.find_one({"_id": user["_id"]})
    fresh.pop("hashed_password", None)
    fresh["_id"] = str(fresh["_id"])
    return fresh


@router.post("/me/password")
async def change_password(payload: PasswordChange, user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    db_user = await db.users.find_one({"_id": user["_id"]})
    if not db_user or not verify_password(payload.current_password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password incorrect")
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": hash_password(payload.new_password)}},
    )
    return {"message": "Password updated"}


@router.patch("/me/settings")
async def update_settings(payload: SettingsUpdate, user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    if payload.notification_prefs:
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"notification_prefs": payload.notification_prefs.model_dump()}},
        )
    return {"message": "Settings saved"}


@router.get("/admin/list", dependencies=[Depends(require_roles("admin"))])
async def list_users_admin():
    db = get_database()
    users = []
    async for u in db.users.find({}):
        u.pop("hashed_password", None)
        u["_id"] = str(u["_id"])
        users.append(u)
    return users


@router.delete("/admin/{email}", dependencies=[Depends(require_roles("admin"))])
async def delete_user_admin(email: str):
    db = get_database()
    await db.users.delete_one({"email": email})
    return {"message": "deleted"}
