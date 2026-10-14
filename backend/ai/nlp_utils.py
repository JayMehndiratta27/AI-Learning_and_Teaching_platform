"""Optional local NLP utilities (NLTK) — safe no-op if corpora missing."""
from __future__ import annotations

import re
from typing import List

try:
    import nltk
    from nltk.tokenize import word_tokenize
except Exception:  # pragma: no cover
    nltk = None
    word_tokenize = None


def tokenize(text: str) -> List[str]:
    if word_tokenize:
        try:
            return word_tokenize(text.lower())
        except LookupError:
            # Corpora not downloaded — regex fallback
            pass
    return re.findall(r"[a-z0-9]+", text.lower())
