"""Basic HTML stripping for user-provided strings (defense in depth)."""
import html
import re


def strip_html(text: str, max_length: int = 8000) -> str:
    if not text:
        return ""
    text = html.escape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text[:max_length]
