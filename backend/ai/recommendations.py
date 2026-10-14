"""Lightweight recommendation signals using scikit-learn TF-IDF similarity."""
from __future__ import annotations

from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rank_items(
    user_profile_text: str,
    candidates: List[Dict[str, Any]],
    text_key: str = "description",
    top_k: int = 8,
) -> List[Dict[str, Any]]:
    """Return candidates sorted by cosine similarity to user_profile_text."""
    if not candidates:
        return []
    corpus = [user_profile_text] + [c.get(text_key) or c.get("title") or "" for c in candidates]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=256)
    try:
        mat = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(mat[0:1], mat[1:]).flatten()
    except ValueError:
        return candidates[:top_k]
    order = sims.argsort()[::-1]
    out: List[Dict[str, Any]] = []
    for i in order[:top_k]:
        item = dict(candidates[int(i)])
        item["score"] = float(sims[int(i)])
        out.append(item)
    return out
