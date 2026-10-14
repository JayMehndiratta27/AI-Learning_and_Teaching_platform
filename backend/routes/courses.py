"""Courses, materials, bookmarks, download center."""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException

from database import get_database
from middleware.auth_deps import get_current_user

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("")
async def list_courses():
    db = get_database()
    out = []
    async for c in db.courses.find({}):
        c["_id"] = str(c["_id"])
        out.append(c)
    return out


@router.get("/{course_id}")
async def get_course(course_id: str):
    db = get_database()
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        oid = ObjectId(course_id)
    except InvalidId:
        oid = None
    query = {"_id": oid} if oid else {"title": course_id}
    c = await db.courses.find_one(query)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    c["_id"] = str(c["_id"])
    return c


material_router = APIRouter(prefix="/materials", tags=["materials"])


@material_router.get("")
async def list_materials(subject: Optional[str] = None):
    db = get_database()
    q = {}
    if subject:
        q["subject"] = subject
    items = []
    async for m in db.materials.find(q):
        m["_id"] = str(m["_id"])
        items.append(m)
    return items


@material_router.get("/downloads")
async def download_center():
    db = get_database()
    items = []
    async for m in db.materials.find({}):
        m["_id"] = str(m["_id"])
        items.append(m)
    return {"materials": items}


@material_router.get("/bookmarks")
async def list_bookmarks(user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    doc = await db.bookmarks.find_one({"user_id": str(user["_id"])})
    return {"ids": doc.get("material_ids", []) if doc else []}


@material_router.post("/bookmarks")
async def add_bookmark(
    body: dict,
    user: Annotated[dict, Depends(get_current_user)],
):
    mid = body.get("material_id")
    if not mid:
        raise HTTPException(400, "material_id required")
    db = get_database()
    uid = str(user["_id"])
    await db.bookmarks.update_one(
        {"user_id": uid},
        {"$addToSet": {"material_ids": mid}},
        upsert=True,
    )
    return {"message": "saved"}


@material_router.delete("/bookmarks/{material_id}")
async def remove_bookmark(material_id: str, user: Annotated[dict, Depends(get_current_user)]):
    db = get_database()
    await db.bookmarks.update_one(
        {"user_id": str(user["_id"])},
        {"$pull": {"material_ids": material_id}},
    )
    return {"message": "removed"}
