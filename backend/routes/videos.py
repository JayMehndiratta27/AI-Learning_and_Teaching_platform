"""Video catalog and watch history."""
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends

from database import get_database
from middleware.auth_deps import get_current_user

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("")
async def list_videos(subject: Optional[str] = None):
    db = get_database()
    q = {}
    if subject:
        q["subject"] = subject
    out = []
    async for v in db.videos.find(q):
        v["_id"] = str(v["_id"])
        out.append(v)
    return out


@router.post("/watch-history")
async def add_watch(
    body: dict,
    user: Annotated[dict, Depends(get_current_user)],
):
    db = get_database()
    doc = {
        "user_id": str(user["_id"]),
        "video_id": body.get("video_id"),
        "title": body.get("title"),
        "subject": body.get("subject"),
        "youtube_id": body.get("youtube_id"),
        "watched_at": datetime.now(timezone.utc),
    }
    await db.watch_history.insert_one(doc)
    return {"message": "saved"}


@router.get("/watch-history")
async def get_history(user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    items = (
        await db.watch_history.find({"user_id": str(user["_id"])})
        .sort("watched_at", -1)
        .limit(30)
        .to_list(30)
    )
    for i in items:
        i["_id"] = str(i["_id"])
    return items
