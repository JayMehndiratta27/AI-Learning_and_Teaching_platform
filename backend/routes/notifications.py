"""Notifications list and mark read."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from database import get_database
from middleware.auth_deps import get_current_user, require_roles

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    items = (
        await db.notifications.find({"user_id": str(user["_id"])})
        .sort("created_at", -1)
        .limit(50)
        .to_list(50)
    )
    for n in items:
        n["_id"] = str(n["_id"])
    return items


@router.patch("/{notif_id}/read")
async def mark_read(notif_id: str, user: Annotated[dict, Depends(get_current_user)]):
    from bson import ObjectId
    from bson.errors import InvalidId

    db = get_database()
    try:
        oid = ObjectId(notif_id)
    except InvalidId:
        raise HTTPException(400, "bad id")
    await db.notifications.update_one(
        {"_id": oid, "user_id": str(user["_id"])},
        {"$set": {"read": True}},
    )
    return {"message": "ok"}


@router.post("/seed-reminder", dependencies=[Depends(require_roles("admin", "teacher"))])
async def seed_reminder_for_all():
    """Demo endpoint: push a quiz reminder to every user (for screenshots/testing)."""
    db = get_database()
    now = datetime.now(timezone.utc)
    async for u in db.users.find({}):
        await db.notifications.insert_one(
            {
                "user_id": str(u["_id"]),
                "title": "Quiz reminder",
                "body": "Try today's mixed quiz to keep your streak.",
                "type": "quiz_reminder",
                "read": False,
                "created_at": now,
            }
        )
    return {"message": "reminders inserted"}
