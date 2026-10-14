"""AI tutor chat endpoints and history."""
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from ai.chatbot import generate_chat_reply, generate_summary
from database import get_database
from middleware.auth_deps import get_current_user
from models.schemas import ChatMessageIn
from utils.sanitize import strip_html

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat_turn(payload: ChatMessageIn, user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    uid = str(user["_id"])
    doc = await db.chat_sessions.find_one({"user_id": uid})
    history = doc.get("messages", []) if doc else []
    clean = strip_html(payload.message)
    history.append({"role": "user", "content": clean, "created_at": datetime.now(timezone.utc)})
    reply = generate_chat_reply(history[:-1], clean)
    history.append({"role": "assistant", "content": reply, "created_at": datetime.now(timezone.utc)})
    await db.chat_sessions.update_one(
        {"user_id": uid},
        {"$set": {"messages": history[-40:], "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {"reply": reply, "messages": history[-40:]}


@router.get("/history")
async def chat_history(user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    doc = await db.chat_sessions.find_one({"user_id": str(user["_id"])})
    return {"messages": doc.get("messages", []) if doc else []}


@router.delete("/history")
async def clear_history(user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    await db.chat_sessions.delete_one({"user_id": str(user["_id"])})
    return {"message": "cleared"}


@router.post("/summary")
async def summary_endpoint(body: dict, user: Annotated[dict, Depends(get_current_user)]):
    text = strip_html(str(body.get("text", "")), max_length=12000)
    return {"summary": generate_summary(text)}
