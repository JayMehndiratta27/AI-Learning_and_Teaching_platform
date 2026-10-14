"""Quiz listing, submission, scoring, leaderboard."""
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from ai.chatbot import generate_quiz_suggestions
from database import get_database
from middleware.auth_deps import get_current_user
from models.schemas import QuizSubmit

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


def _normalize_answer(s: str) -> str:
    """Normalize for fair auto-grading (case, spacing, punctuation)."""
    t = str(s).strip().lower().rstrip(".")
    t = "".join(t.split())  # "O(log n)" and "o(logn)" both become "o(logn)"
    return t


@router.get("")
async def list_quizzes(subject: Optional[str] = None):
    db = get_database()
    q = {}
    if subject:
        q["subject"] = subject
    out = []
    async for z in db.quizzes.find(q):
        z["_id"] = str(z["_id"])
        # strip answers for client listing
        public_q = []
        for qq in z.get("questions", []):
            public_q.append({k: v for k, v in qq.items() if k != "answer"})
        z["questions"] = public_q
        out.append(z)
    return out


@router.get("/{quiz_id}")
async def get_quiz(quiz_id: str):
    db = get_database()
    z = await db.quizzes.find_one({"quiz_id": quiz_id})
    if not z:
        raise HTTPException(404, "Quiz not found")
    z["_id"] = str(z["_id"])
    z["questions"] = [{k: v for k, v in qq.items() if k != "answer"} for qq in z.get("questions", [])]
    return z


@router.post("/submit")
async def submit_quiz(payload: QuizSubmit, user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    z = await db.quizzes.find_one({"quiz_id": payload.quiz_id})
    if not z:
        raise HTTPException(404, "Quiz not found")
    answers_map = {a.question_id: a.answer for a in payload.answers}
    correct = 0
    details: List[Dict[str, Any]] = []
    for qq in z.get("questions", []):
        qid = qq["id"]
        expected = _normalize_answer(str(qq.get("answer", "")))
        got = _normalize_answer(str(answers_map.get(qid, "")))
        ok = got == expected
        if ok:
            correct += 1
        details.append(
            {
                "question_id": qid,
                "correct": ok,
                "your_answer": answers_map.get(qid, ""),
                "expected": qq.get("answer"),
            }
        )
    total = len(z.get("questions", [])) or 1
    score_pct = round(100 * correct / total, 1)
    weak_flag = score_pct < 70
    weak_subjects = list(user.get("weak_subjects") or [])
    if weak_flag and z.get("subject") not in weak_subjects:
        weak_subjects.append(z["subject"])
    elif not weak_flag and z.get("subject") in weak_subjects:
        weak_subjects.remove(z["subject"])
    xp_gain = 25 + correct * 5
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$inc": {"xp": xp_gain}, "$set": {"weak_subjects": weak_subjects}},
    )
    feedback = (
        "Strong performance — try a harder mixed quiz next."
        if score_pct >= 80
        else "Review incorrect items, then retry with Explain mode in the AI Tutor."
    )
    result_doc = {
        "user_id": str(user["_id"]),
        "quiz_id": payload.quiz_id,
        "subject": z.get("subject"),
        "score_pct": score_pct,
        "correct": correct,
        "total": total,
        "details": details,
        "duration_seconds": payload.duration_seconds,
        "created_at": datetime.now(timezone.utc),
        "ai_feedback": feedback,
    }
    await db.quiz_results.insert_one(result_doc)
    # milestone notification
    if score_pct == 100:
        await db.notifications.insert_one(
            {
                "user_id": str(user["_id"]),
                "title": "Perfect score!",
                "body": f"You cleared {z.get('title')}",
                "type": "milestone",
                "read": False,
                "created_at": datetime.now(timezone.utc),
            }
        )
    suggestions = generate_quiz_suggestions(z.get("subject", ""), weak_subjects)
    wrong_for_tutor = [
        {
            "prompt": next((qq["prompt"] for qq in z.get("questions", []) if qq["id"] == d["question_id"]), ""),
            "expected": d.get("expected"),
            "your_answer": d.get("your_answer"),
        }
        for d in details
        if not d["correct"]
    ]
    return {
        "score_pct": score_pct,
        "correct": correct,
        "total": total,
        "details": details,
        "ai_feedback": feedback,
        "xp_gained": xp_gain,
        "ai_quiz_suggestions": suggestions,
        "subject": z.get("subject"),
        "quiz_title": z.get("title"),
        "wrong_for_tutor": wrong_for_tutor,
    }


@router.get("/leaderboard/summary")
async def leaderboard(limit: int = 10):
    db = get_database()
    pipeline = [
        {"$group": {"_id": "$user_id", "avg": {"$avg": "$score_pct"}, "count": {"$sum": 1}}},
        {"$sort": {"avg": -1}},
        {"$limit": limit},
    ]
    rows = await db.quiz_results.aggregate(pipeline).to_list(length=limit)
    enriched = []
    for r in rows:
        name = r["_id"]
        try:
            u = await db.users.find_one({"_id": ObjectId(r["_id"])})
            if u:
                name = u.get("full_name") or u.get("email")
        except InvalidId:
            u = await db.users.find_one({"email": r["_id"]})
            if u:
                name = u.get("full_name") or u.get("email")
        enriched.append({"user_label": name, "avg_score": round(r["avg"], 1), "attempts": r["count"]})
    return enriched
