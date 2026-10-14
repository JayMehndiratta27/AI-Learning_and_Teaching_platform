"""Teacher and admin analytics views."""
from fastapi import APIRouter, Depends

from database import get_database
from middleware.auth_deps import require_roles

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/overview", dependencies=[Depends(require_roles("teacher", "admin"))])
async def teacher_overview():
    db = get_database()
    total_users = await db.users.count_documents({})
    total_results = await db.quiz_results.count_documents({})
    avg_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$score_pct"}}}]
    agg = await db.quiz_results.aggregate(avg_pipeline).to_list(1)
    platform_avg = round(agg[0]["avg"], 1) if agg else 0.0
    uploads = await db.materials.count_documents({})
    return {
        "total_users": total_users,
        "quiz_attempts": total_results,
        "platform_avg_score": platform_avg,
        "uploaded_materials": uploads,
    }


admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/stats", dependencies=[Depends(require_roles("admin"))])
async def admin_stats():
    db = get_database()
    return {
        "users": await db.users.count_documents({}),
        "courses": await db.courses.count_documents({}),
        "quizzes": await db.quizzes.count_documents({}),
        "notifications": await db.notifications.count_documents({}),
    }
