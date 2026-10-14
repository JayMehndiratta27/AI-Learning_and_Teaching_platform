"""Analytics, recommendations, progress events."""
from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Dict, List, Optional

from fastapi import APIRouter, Depends, Query

from ai.recommendations import rank_items
from database import get_database
from middleware.auth_deps import get_current_user
from models.schemas import ProgressEventIn

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _to_aware_utc(value: object) -> Optional[datetime]:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        # support "...Z" timestamps too
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            return None
    return None


@router.post("/progress")
async def log_progress(payload: ProgressEventIn, user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    await db.progress_events.insert_one(
        {
            "user_id": str(user["_id"]),
            "subject": payload.subject,
            "minutes": payload.minutes,
            "activity_type": payload.activity_type,
            "created_at": datetime.now(timezone.utc),
        }
    )
    # Streak: first activity on a new UTC day extends streak if previous day was active
    today = datetime.now(timezone.utc).date().isoformat()
    last = user.get("last_streak_date")
    streak = int(user.get("streak_days") or 0)
    if last == today:
        return {"message": "logged", "streak_days": streak}
    if not last:
        streak = max(1, streak or 1)
    else:
        try:
            last_d = date.fromisoformat(str(last))
            delta = datetime.now(timezone.utc).date() - last_d
            streak = streak + 1 if delta.days == 1 else 1
        except ValueError:
            streak = 1
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"streak_days": streak, "last_streak_date": today}},
    )
    return {"message": "logged", "streak_days": streak}


@router.get("/me")
async def my_analytics(
    user: Annotated[dict, Depends(get_current_user)],
    days: int = Query(default=30, ge=0, le=365),
):
    db = get_database()
    uid = str(user["_id"])
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days) if days > 0 else None
    # Pull by user first and filter in Python to avoid sqlite timezone-compare edge cases.
    raw_events = await db.progress_events.find({"user_id": uid}).to_list(2000)
    raw_results = await db.quiz_results.find({"user_id": uid}).sort("created_at", -1).limit(200).to_list(200)

    events = []
    for e in raw_events:
        created_at = _to_aware_utc(e.get("created_at"))
        if not created_at:
            continue
        if since and created_at < since:
            continue
        events.append({**e, "created_at": created_at})

    results = []
    for r in raw_results:
        created_at = _to_aware_utc(r.get("created_at"))
        if since and created_at and created_at < since:
            continue
        results.append({**r, "created_at": created_at})

    daily: Dict[str, int] = {}
    for e in events:
        day = e["created_at"].date().isoformat()
        daily[day] = daily.get(day, 0) + int(e.get("minutes", 0))
    subject_minutes: Dict[str, int] = {}
    for e in events:
        subject_minutes[e["subject"]] = subject_minutes.get(e["subject"], 0) + int(e.get("minutes", 0))

    total_minutes = sum(int(e.get("minutes", 0)) for e in events)
    study_days = len(daily)
    avg_per_day = round(total_minutes / study_days, 1) if study_days else 0.0
    recent_scores = [float(r.get("score_pct", 0) or 0) for r in results]
    avg_score = round(sum(recent_scores) / len(recent_scores), 1) if recent_scores else 0.0

    return {
        "window_days": days,
        "totals": {
            "minutes": total_minutes,
            "study_days": study_days,
            "avg_minutes_per_day": avg_per_day,
            "avg_score_pct": avg_score,
            "quiz_attempts": len(results),
        },
        "daily_minutes": daily,
        "subject_minutes": subject_minutes,
        "recent_quiz_results": [
            {
                "quiz_id": r.get("quiz_id"),
                "score_pct": r.get("score_pct"),
                "subject": r.get("subject"),
                "created_at": r.get("created_at").isoformat() if isinstance(r.get("created_at"), datetime) else None,
            }
            for r in results
        ],
    }


rec_router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@rec_router.get("")
async def recommendations(user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    profile_parts: List[str] = []
    if user.get("weak_subjects"):
        profile_parts.append("weak: " + ", ".join(user["weak_subjects"]))
    profile_parts.append("interests: learning, quizzes, stem")
    profile = " ".join(profile_parts)
    mats = await db.materials.find({}).to_list(200)
    vids = await db.videos.find({}).to_list(200)
    quizzes = await db.quizzes.find({}).to_list(50)
    mat_candidates = [
        {"kind": "pdf", "id": m["id"], "title": m["title"], "subject": m["subject"], "description": m["title"]}
        for m in mats
    ]
    vid_candidates = [
        {
            "kind": "video",
            "id": v["video_id"],
            "title": v["title"],
            "subject": v["subject"],
            "description": v["title"] + " " + v["subject"],
            "youtube_id": v["youtube_id"],
        }
        for v in vids
    ]
    quiz_candidates = [
        {
            "kind": "quiz",
            "id": q["quiz_id"],
            "title": q["title"],
            "subject": q["subject"],
            "description": q["title"] + " " + q["subject"],
        }
        for q in quizzes
    ]
    ranked_pdf = rank_items(profile, mat_candidates, top_k=5)
    ranked_vid = rank_items(profile, vid_candidates, top_k=5)
    ranked_quiz = rank_items(profile, quiz_candidates, top_k=5)
    await db.recommendations.update_one(
        {"user_id": str(user["_id"])},
        {
            "$set": {
                "items": ranked_pdf[:3] + ranked_vid[:3] + ranked_quiz[:3],
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    return {"items": ranked_pdf[:4] + ranked_vid[:4] + ranked_quiz[:4]}
