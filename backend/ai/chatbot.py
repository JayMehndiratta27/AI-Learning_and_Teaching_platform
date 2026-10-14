"""AI tutor: OpenAI when configured, else rich offline academic fallback (no API key required)."""
from __future__ import annotations

import os
import re
from typing import List

from config import get_settings
import httpx

try:
    from openai import OpenAI
    from openai import APIConnectionError, AuthenticationError, RateLimitError
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore
    APIConnectionError = Exception  # type: ignore
    AuthenticationError = Exception  # type: ignore
    RateLimitError = Exception  # type: ignore


FALLBACK_SYSTEM = (
    "You are LearnFlow Tutor, a concise STEM and CS teaching assistant. "
    "Give short structured answers with bullet points when helpful."
)

_OFFLINE_TOPIC_MENU = (
    "**LearnFlow Tutor (offline)** — no API key needed.\n\n"
    "Ask naturally, or try one of these:\n"
    "- **Math:** algebra, calculus, trigonometry, word problems\n"
    "- **Physics / science:** motion, forces, energy, units\n"
    "- **Literature / English:** themes, thesis, close reading\n"
    "- **CS / DSA:** Big-O, arrays, trees, graphs, heaps\n"
    "- **OS:** deadlock, scheduling, paging, virtual memory\n"
    "- **Quiz help:** how to eliminate wrong MCQ options\n"
    "- **Summary:** paste a paragraph and say “summarize”\n\n"
    "Below is tailored help for your message."
)

def _openai_error_notice(exc: Exception) -> str:
    if isinstance(exc, AuthenticationError):
        return (
            "**OpenAI key error**\n\n"
            "Your API key was rejected. Re-check `OPENAI_API_KEY` in `backend/.env`, then restart the backend."
        )
    if isinstance(exc, RateLimitError):
        return (
            "**OpenAI quota reached**\n\n"
            "Your OpenAI account/project has insufficient quota or billing is not active. "
            "Please enable billing or switch to a funded key/project."
        )
    if isinstance(exc, APIConnectionError):
        return (
            "**OpenAI connection issue**\n\n"
            "The backend could not reach OpenAI right now. Check internet/proxy/firewall and try again."
        )
    return "**OpenAI unavailable right now**\n\nFalling back to offline tutor."


def _fallback_reply(user_message: str) -> str:
    msg = user_message.lower().strip()
    if not msg:
        return _OFFLINE_TOPIC_MENU

    # Quiz / exam explanations (deep links from LearnFlow quiz review)
    if (
        "offline tutor" in msg
        or ("explain" in msg and ("quiz" in msg or "question" in msg or "correct answer" in msg))
        or ("review this quiz" in msg)
    ):
        return (
            "**Quiz review (offline tutor)**\n\n"
            "- **Restate** the stem: what concept or formula is being tested?\n"
            "- **Work from definitions:** write the rule, then apply it line by line.\n"
            "- **Contrast** your answer with the key: which step or assumption differs?\n"
            "- **Redo** the item without notes, then check — that locks in the fix.\n\n"
            "The question text you sent is saved above; combine that with your course notes "
            "for the exact proof or calculation your instructor expects."
        )

    # Literature / English
    if any(
        k in msg
        for k in [
            "literature",
            "novel",
            "poem",
            "poetry",
            "shakespeare",
            "theme",
            "thesis",
            "essay",
            "writing",
            "grammar",
        ]
    ):
        return (
            "**Literature & writing (offline)**\n\n"
            "- **Thesis:** one arguable claim the whole piece supports.\n"
            "- **Close reading:** diction, imagery, tone, structure — tie each to meaning.\n"
            "- **Theme vs plot:** plot is what happens; theme is what it suggests about life.\n"
            "- **Essay skeleton:** claim → 2–3 evidence chunks with quotes → explain *why* each quote matters.\n"
            "Paste a short passage + your draft claim for tighter feedback."
        )

    # Physics / motion
    if any(
        k in msg
        for k in [
            "physics",
            "velocity",
            "acceleration",
            "force",
            "newton",
            "energy",
            "momentum",
            "kinematic",
            "projectile",
        ]
    ):
        return (
            "**Physics intuition (offline)**\n\n"
            "- **Kinematics:** v = Δx/Δt; acceleration changes velocity (not position directly).\n"
            "- **Forces:** draw a free-body diagram; net force along each axis.\n"
            "- **Energy:** track forms (KE, PE, thermal); conserved if only conservative forces do work.\n"
            "- **Units:** always carry meters, seconds, kg; cancel dimensions on both sides of an equation.\n"
            "State the exact problem (given / find) for a step-by-step sketch."
        )

    if "summary" in msg or "summarize" in msg:
        return (
            "**Summary mode (offline)**\n\n"
            "Paste 3–10 sentences in the box, then tap **AI summary**. I’ll pull out main ideas as bullets "
            "without an OpenAI key. For deeper rewriting, set `OPENAI_API_KEY` in `backend/.env`."
        )

    if "quiz" in msg or "mcq" in msg or "exam" in msg:
        return (
            "**Quiz tactics (offline)**\n\n"
            "- Read the stem twice; underline **not/except** qualifiers.\n"
            "- Eliminate answers that contradict a definition or unit analysis.\n"
            "- For **T/F**, suspect absolutes (“always”, “never”) unless the statement is a definition.\n"
            "- For **numeric** blanks, sanity-check magnitude and sign.\n"
            "After a quiz, use **Review** → **Ask AI Tutor** with the question text for a worked explanation."
        )

    if any(k in msg for k in ["dsa", "data structure", "graph", "tree", "heap", "bst", "hash"]):
        return (
            "**Data structures (offline)**\n\n"
            "- **Pick the ADT** first (queue vs stack vs map vs heap).\n"
            "- **BST:** in-order is sorted; delete has three cases (0/1/2 children).\n"
            "- **Heap:** parent dominates children (min-heap: parent ≤ children).\n"
            "- **Graphs:** BFS layer-by-layer; DFS for cycles / topo when directed.\n"
            "- **Complexity:** state *average* vs *worst*; mention space for recursion stack."
        )

    if any(k in msg for k in ["os", "operating system", "deadlock", "scheduling", "paging", "virtual memory"]):
        return (
            "**Operating systems (offline)**\n\n"
            "- **Deadlock:** mutual exclusion, hold-and-wait, no preemption, circular wait — break one.\n"
            "- **Scheduling:** FCFS simple; SJF can starve; RR needs a time quantum tradeoff.\n"
            "- **Paging:** virtual page → frame; TLB caches translations; page fault cost dominates.\n"
            "- **Thrashing:** too many active pages — need working-set or frame allocation fixes."
        )

    if any(k in msg for k in ["algebra", "calculus", "trig", "derivative", "integral", "equation"]):
        return (
            "**Math study path (offline)**\n\n"
            "- **Algebra:** isolate the variable; do the same operation both sides; check extraneous solutions.\n"
            "- **Calculus:** derivative = slope / rate; integral = accumulation / area (FTC links them).\n"
            "- **Trig:** draw the triangle; use identities to simplify before differentiating.\n"
            "Send one specific equation or word problem for a worked template."
        )

    if any(k in msg for k in ["python", "code", "debug", "loop", "recursion", "syntax"]):
        return (
            "**CS / Python patterns (offline)**\n\n"
            "- **Loops:** for = definite iteration; while = guard condition (avoid infinite loops).\n"
            "- **Recursion:** base case first; trust the call returns the right subproblem size.\n"
            "- **Debugging:** reproduce minimal input; print mid-values; check types and edge cases.\n"
            "Paste a short snippet + error text for line-by-line reasoning."
        )

    if any(k in msg for k in ["hello", "hi ", "hey", "start", "help me"]):
        return _OFFLINE_TOPIC_MENU

    # Default: echo + menu
    preview = user_message[:400].replace("\n", " ")
    return (
        _OFFLINE_TOPIC_MENU
        + "\n\n---\n\n"
        + f"**You wrote:** “{preview}”\n\n"
        + "I matched general **offline** guidance. Rephrase with a topic keyword "
        "(e.g. *deadlock*, *derivative*, *theme in Hamlet*) for a deeper offline answer, "
        "or add `OPENAI_API_KEY` for full LLM replies."
    )


def generate_chat_reply(history: List[dict], user_message: str) -> str:
    settings = get_settings()
    key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
    if key and OpenAI:
        try:
            # Ignore inherited proxy env vars (HTTP_PROXY/HTTPS_PROXY) that can break API access.
            client = OpenAI(api_key=key, http_client=httpx.Client(trust_env=False))
            messages = [{"role": "system", "content": FALLBACK_SYSTEM}]
            for h in history[-12:]:
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": user_message})
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.4,
                max_tokens=900,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            # Never fail the chat endpoint; fall back to offline tutor if OpenAI is misconfigured or unavailable.
            return _openai_error_notice(exc) + "\n\n---\n\n" + _fallback_reply(user_message)
    return _fallback_reply(user_message)


def generate_quiz_suggestions(subject: str, weak_topics: List[str]) -> List[str]:
    base = [
        f"Timed MCQ sprint: {subject} fundamentals (10 questions)",
        f"Mixed review: connect {subject} definitions to short applications",
    ]
    for t in weak_topics[:3]:
        base.append(f"Drill: {t} — explain-then-quiz pattern (5 min)")
    return base[:6]


def generate_summary(text: str) -> str:
    settings = get_settings()
    key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
    if key and OpenAI:
        try:
            client = OpenAI(api_key=key, http_client=httpx.Client(trust_env=False))
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Summarize clearly in 5-8 bullets."},
                    {"role": "user", "content": text[:12000]},
                ],
                temperature=0.2,
                max_tokens=600,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            prefix = _openai_error_notice(exc)
            # Keep summary usable by falling back to offline extraction.
            text = re.sub(r"\s+", " ", text).strip()
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 8]
            picked = sentences[:8]
            bullets = "\n".join(f"- {s}" for s in picked)
            extras = []
            if len(sentences) > 8:
                extras.append(f"- _…and {len(sentences) - 8} more sentences in your paste._")
            fallback = "\n".join([bullets] + extras) if bullets else "- Paste a bit more text (full sentences work best)."
            return prefix + "\n\n---\n\n**Offline summary (sentence extract)**\n\n" + fallback
    text = re.sub(r"\s+", " ", text).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 8]
    picked = sentences[:8]
    bullets = "\n".join(f"- {s}" for s in picked)
    extras = []
    if len(sentences) > 8:
        extras.append(f"- _…and {len(sentences) - 8} more sentences in your paste._")
    return "**Offline summary (sentence extract)**\n\n" + (
        "\n".join([bullets] + extras) if bullets else "- Paste a bit more text (full sentences work best)."
    )
