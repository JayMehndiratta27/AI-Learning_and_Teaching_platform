"""
SQLite fallback when MongoDB is unavailable — Mongo-like async API for LearnFlow routes.
Uses bson.json_util for datetimes / ObjectId in JSON.
"""
from __future__ import annotations

import asyncio
import copy
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

import aiosqlite
from bson import ObjectId, json_util


def _sid(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    return str(v)


def _doc_matches(doc: Dict[str, Any], q: Dict[str, Any]) -> bool:
    if not q:
        return True
    for key, cond in q.items():
        if key == "_id":
            if _sid(doc.get("_id")) != _sid(cond):
                return False
            continue
        if isinstance(cond, dict):
            if "$gte" in cond:
                dv = doc.get(key)
                if dv is None:
                    return False
                thr = cond["$gte"]
                if isinstance(dv, datetime) and isinstance(thr, datetime):
                    if dv < thr:
                        return False
                elif str(dv) < str(thr):
                    return False
                continue
        if doc.get(key) != cond:
            return False
    return True


def _apply_update(doc: Dict[str, Any], update: Dict[str, Any]) -> None:
    if "$set" in update:
        for k, v in update["$set"].items():
            doc[k] = v
    if "$unset" in update:
        for k in update["$unset"]:
            doc.pop(k, None)
    if "$inc" in update:
        for k, delta in update["$inc"].items():
            doc[k] = int(doc.get(k, 0)) + int(delta)
    if "$addToSet" in update:
        for k, v in update["$addToSet"].items():
            arr = doc.setdefault(k, [])
            if not isinstance(arr, list):
                arr = []
                doc[k] = arr
            if v not in arr:
                arr.append(v)
    if "$pull" in update:
        for k, v in update["$pull"].items():
            if k in doc and isinstance(doc[k], list):
                doc[k] = [x for x in doc[k] if x != v]


def _upsert_doc_from_filter_and_update(filt: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    doc: Dict[str, Any] = {}
    for k, v in filt.items():
        if not k.startswith("$"):
            doc[k] = copy.deepcopy(v)
    if "_id" not in doc:
        doc["_id"] = ObjectId()
    _apply_update(doc, update)
    return doc


class SqliteFindCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self._docs = docs
        self._sort_key: Optional[str] = None
        self._sort_dir = 1
        self._lim: Optional[int] = None

    def sort(self, key: str, direction: int = 1) -> "SqliteFindCursor":
        self._sort_key = key
        self._sort_dir = direction
        return self

    def limit(self, n: int) -> "SqliteFindCursor":
        self._lim = n
        return self

    def _materialize(self) -> List[Dict[str, Any]]:
        rows = list(self._docs)
        if self._sort_key:

            def _key(d: Dict[str, Any]) -> Any:
                v = d.get(self._sort_key)
                if isinstance(v, datetime):
                    return v.timestamp()
                return str(v) if v is not None else ""

            rows.sort(key=_key, reverse=self._sort_dir < 0)
        if self._lim is not None:
            rows = rows[: self._lim]
        return rows

    def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        async def _gen():
            for d in self._materialize():
                yield d

        return _gen()

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        rows = self._materialize()
        if length is not None:
            return rows[:length]
        return rows


class SqliteCollection:
    def __init__(self, db: "SqliteDatabase", name: str):
        self._db = db
        self._name = name

    async def _load_all(self) -> List[Dict[str, Any]]:
        async with self._db._lock:
            async with self._db._conn.execute(
                "SELECT data FROM docs WHERE collection = ?", (self._name,)
            ) as cur:
                rows = await cur.fetchall()
        out: List[Dict[str, Any]] = []
        for (blob,) in rows:
            try:
                out.append(json_util.loads(blob))
            except Exception:
                continue
        return out

    async def _save(self, doc: Dict[str, Any]) -> None:
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        key = _sid(doc["_id"])
        blob = json_util.dumps(doc)
        async with self._db._lock:
            await self._db._conn.execute(
                "INSERT OR REPLACE INTO docs (collection, id, data) VALUES (?, ?, ?)",
                (self._name, key, blob),
            )
            await self._db._conn.commit()

    async def _delete_by_id(self, doc_id: str) -> None:
        async with self._db._lock:
            await self._db._conn.execute(
                "DELETE FROM docs WHERE collection = ? AND id = ?", (self._name, doc_id)
            )
            await self._db._conn.commit()

    async def find_one(self, filt: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for d in await self._load_all():
            if _doc_matches(d, filt):
                return copy.deepcopy(d)
        return None

    def find(self, filt: Dict[str, Any]) -> SqliteFindCursor:
        # sync wrapper — materialize lazily in cursor
        async def _load():
            return [copy.deepcopy(d) for d in await self._load_all() if _doc_matches(d, filt)]

        # SqliteFindCursor needs list — use async bridge via storing coroutine is messy.
        # Use empty list and populate in __aiter__ by storing ref to collection + filt
        return SqliteFindCursorProxy(self, filt)

    async def insert_one(self, doc: Dict[str, Any]) -> Any:
        d = copy.deepcopy(doc)
        if "_id" not in d:
            d["_id"] = ObjectId()
        await self._save(d)

        class R:
            inserted_id = d["_id"]

        return R()

    async def insert_many(self, docs: List[Dict[str, Any]]) -> None:
        for doc in docs:
            await self.insert_one(doc)

    async def update_one(self, filt: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> None:
        all_docs = await self._load_all()
        for i, d in enumerate(all_docs):
            if _doc_matches(d, filt):
                merged = copy.deepcopy(d)
                _apply_update(merged, update)
                await self._save(merged)
                return
        if upsert:
            new_d = _upsert_doc_from_filter_and_update(filt, update)
            await self._save(new_d)

    async def delete_one(self, filt: Dict[str, Any]) -> None:
        for d in await self._load_all():
            if _doc_matches(d, filt):
                await self._delete_by_id(_sid(d["_id"]))
                return

    async def count_documents(self, filt: Dict[str, Any]) -> int:
        n = 0
        for d in await self._load_all():
            if _doc_matches(d, filt):
                n += 1
        return n

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> SqliteAggregateCursor:
        return SqliteAggregateCursorProxy(self, pipeline)


class SqliteFindCursorProxy(SqliteFindCursor):
    """Deferred find — loads on first iteration / to_list."""

    def __init__(self, coll: SqliteCollection, filt: Dict[str, Any]):
        super().__init__([])
        self._coll = coll
        self._filt = filt
        self._loaded: Optional[List[Dict[str, Any]]] = None

    async def _ensure(self) -> None:
        if self._loaded is None:
            raw = await self._coll._load_all()
            self._loaded = [copy.deepcopy(d) for d in raw if _doc_matches(d, self._filt)]
            self._docs = self._loaded

    def __aiter__(self) -> AsyncIterator[Dict[str, Any]]:
        async def _gen():
            await self._ensure()
            for d in self._materialize():
                yield d

        return _gen()

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        await self._ensure()
        rows = self._materialize()
        if length is not None:
            return rows[:length]
        return rows


class SqliteAggregateCursorProxy:
    def __init__(self, coll: SqliteCollection, pipeline: List[Dict[str, Any]]):
        self._coll = coll
        self._pipeline = pipeline

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        # Support leaderboard pipeline: $group avg score_pct by user_id, sort, limit
        if not self._pipeline:
            return []
        group_stage = None
        sort_stage = None
        limit_n = 10
        for st in self._pipeline:
            if "$group" in st:
                group_stage = st["$group"]
            elif "$sort" in st:
                sort_stage = st["$sort"]
            elif "$limit" in st:
                limit_n = st["$limit"]
        if not group_stage or group_stage.get("_id") != "$user_id":
            return []
        raw = await self._coll._load_all()
        buckets: Dict[str, List[float]] = {}
        for d in raw:
            uid = d.get("user_id")
            if uid is None:
                continue
            buckets.setdefault(str(uid), []).append(float(d.get("score_pct", 0)))
        rows = []
        for uid, scores in buckets.items():
            rows.append({"_id": uid, "avg": sum(scores) / len(scores), "count": len(scores)})
        key = "avg"
        rev = True
        if sort_stage:
            key = list(sort_stage.keys())[0]
            rev = sort_stage[key] < 0
        rows.sort(key=lambda r: r[key], reverse=rev)
        return rows[:limit_n]


class SqliteDatabase:
    """Drop-in replacement for AsyncIOMotorDatabase attribute access (db.users, db.courses, ...)."""

    def __init__(self, conn: aiosqlite.Connection, lock: asyncio.Lock):
        self._conn = conn
        self._lock = lock

    @classmethod
    async def create(cls, path: str) -> "SqliteDatabase":
        path = path or "data/learnflow.db"
        import os

        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        conn = await aiosqlite.connect(path)
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS docs (
                collection TEXT NOT NULL,
                id TEXT NOT NULL,
                data TEXT NOT NULL,
                PRIMARY KEY (collection, id)
            )"""
        )
        await conn.commit()
        return cls(conn, asyncio.Lock())

    async def close(self) -> None:
        await self._conn.close()

    def __getattr__(self, name: str) -> SqliteCollection:
        return SqliteCollection(self, name)
