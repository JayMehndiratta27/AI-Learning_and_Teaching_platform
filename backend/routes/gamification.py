"""XP, badges, daily challenges."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from database import get_database
from middleware.auth_deps import get_current_user

router = APIRouter(prefix="/gamification", tags=["gamification"])


BADGES = [
    {"id": "first-quiz", "name": "First Steps", "rule": lambda u: u.get("xp", 0) >= 25},
    {"id": "streak-3", "name": "On Fire", "rule": lambda u: u.get("streak_days", 0) >= 3},
    {"id": "xp-200", "name": "Scholar", "rule": lambda u: u.get("xp", 0) >= 200},
]


@router.get("/me")
async def gamification_me(user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    fresh = await db.users.find_one({"_id": user["_id"]})
    xp = int(fresh.get("xp", 0))
    streak = int(fresh.get("streak_days", 0))
    earned = []
    for b in BADGES:
        if b["rule"](fresh):
            earned.append({"id": b["id"], "name": b["name"]})
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"badges": [e["id"] for e in earned]}})
    challenges = await db.challenges.find({}).to_list(20)
    completed = fresh.get("completed_challenges", []) or []
    return {"xp": xp, "streak_days": streak, "badges": earned, "challenges": challenges, "completed": completed}


@router.post("/challenges/complete")
async def complete_challenge(body: dict, user: Annotated[dict, Depends(get_current_user)]):
    cid = body.get("challenge_id")
    if not cid:
        raise HTTPException(400, "challenge_id required")
    db = get_database()
    ch = await db.challenges.find_one({"challenge_id": cid})
    if not ch:
        raise HTTPException(404, "challenge not found")
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$addToSet": {"completed_challenges": cid}, "$inc": {"xp": int(ch.get("xp", 30))}},
    )
    await db.notifications.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Challenge complete",
            "body": f"+{ch.get('xp', 30)} XP — {ch.get('title')}",
            "type": "milestone",
            "read": False,
            "created_at": datetime.now(timezone.utc),
        }
    )
    return {"message": "completed", "xp_awarded": ch.get("xp", 30)}
