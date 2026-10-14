"""Global search across courses, materials, videos, quizzes."""
from typing import Any, List

from fastapi import APIRouter, Query

from database import get_database

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search(q: str = Query("", min_length=1, max_length=120)):
    db = get_database()
    needle = q.lower()
    results: List[dict[str, Any]] = []

    async for c in db.courses.find({}):
        blob = (c.get("title", "") + " " + c.get("description", "")).lower()
        if needle in blob:
            results.append({"type": "course", "id": str(c["_id"]), "title": c.get("title")})

    async for m in db.materials.find({}):
        blob = (m.get("title", "") + " " + m.get("subject", "")).lower()
        if needle in blob:
            results.append(
                {"type": "pdf", "id": m.get("id"), "title": m.get("title"), "subject": m.get("subject")}
            )

    async for v in db.videos.find({}):
        blob = (v.get("title", "") + " " + v.get("subject", "")).lower()
        if needle in blob:
            results.append(
                {
                    "type": "video",
                    "id": v.get("video_id"),
                    "title": v.get("title"),
                    "subject": v.get("subject"),
                }
            )

    async for z in db.quizzes.find({}):
        blob = (z.get("title", "") + " " + z.get("subject", "")).lower()
        if needle in blob:
            results.append({"type": "quiz", "id": z.get("quiz_id"), "title": z.get("title")})

    return {"query": q, "results": results[:40]}
