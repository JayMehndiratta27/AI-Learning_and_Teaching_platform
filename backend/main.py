"""LearnFlow FastAPI application entrypoint."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import get_settings
from database import close_db, init_database, storage_label
from routes import analytics, auth, chat, courses, gamification, notifications, quizzes, search, teacher, users, videos
from services.seed_db import seed_if_empty, static_mount_path

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    try:
        await seed_if_empty()
    except Exception as exc:
        logger.warning("Seed skipped or partial (%s)", exc)
    yield
    await close_db()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="LearnFlow API", version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=static_mount_path()), name="static")

    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(courses.router, prefix="/api")
    app.include_router(courses.material_router, prefix="/api")
    app.include_router(quizzes.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
    app.include_router(analytics.rec_router, prefix="/api")
    app.include_router(notifications.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(videos.router, prefix="/api")
    app.include_router(gamification.router, prefix="/api")
    app.include_router(teacher.router, prefix="/api")
    app.include_router(teacher.admin_router, prefix="/api")

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "storage": storage_label()}

    return app


app = create_app()
