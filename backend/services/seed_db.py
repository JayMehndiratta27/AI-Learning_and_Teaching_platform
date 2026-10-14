"""Seed MongoDB with demo courses, quizzes, notifications, and PDF assets."""
from __future__ import annotations

import os
import hashlib
import random
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from database import get_database


def _public_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "public" / "pdfs"


def ensure_sample_pdfs() -> None:
    """Create valid PDFs for each subject area.

    These are offline/demo materials (short formulae + notes). We overwrite any existing PDFs
    so the content stays in sync with the latest templates.
    """
    out = _public_dir()
    out.mkdir(parents=True, exist_ok=True)
    catalog = [
        ("algebra_basics.pdf", "Mathematics — Algebra Basics"),
        ("calculus_intro.pdf", "Mathematics — Calculus Introduction"),
        ("trigonometry_notes.pdf", "Mathematics — Trigonometry Notes"),
        ("physics_basics.pdf", "Science — Physics Basics"),
        ("chemistry_reactions.pdf", "Science — Chemistry Reactions"),
        ("biology_diagrams.pdf", "Science — Biology Diagrams"),
        ("english_grammar.pdf", "English — Grammar Guide"),
        ("english_vocabulary.pdf", "English — Vocabulary Notes"),
        ("writing_skills.pdf", "English — Writing Skills"),
        ("dbms_notes.pdf", "Computer Science — DBMS Notes"),
        ("os_notes.pdf", "Computer Science — Operating Systems"),
        ("cn_notes.pdf", "Computer Science — Computer Networks"),
        ("dsa_arrays.pdf", "Computer Science — DSA: Arrays & Complexity"),
        ("dsa_graphs.pdf", "Computer Science — DSA: Graph Algorithms"),
        ("ai_intro.pdf", "Artificial Intelligence — Introduction"),
        ("ds_structures.pdf", "Data Structures — Core Structures"),
        ("os_scheduling.pdf", "Operating Systems — CPU Scheduling"),
    ]

    # Keep each line short so it fits the default reportlab font without wrapping.
    content_options: dict[str, list[str]] = {
        "algebra_basics.pdf": [
            "Solve: ax + b = 0  =>  x = -b/a",
            "Quadratic: ax^2 + bx + c = 0",
            "x = (-b ± sqrt(b^2 - 4ac)) / (2a)",
            "Distributive: a(b + c) = ab + ac",
            "Exponent: a^m * a^n = a^(m+n)",
            "Check answers for restrictions/extraneous roots",
            "Linear inequalities: flip sign when multiplying by negatives",
        ],
        "calculus_intro.pdf": [
            "Derivative: f'(x) = lim_{h->0} (f(x+h)-f(x))/h",
            "Rules: (u+v)'=u'+v', (uv)'=u'v+uv'",
            "Integral: ∫ f(x) dx = F(x) + C",
            "FTC: d/dx ∫_a^x f(t) dt = f(x)",
            "Area idea: integral as 'accumulated' slices",
            "Slope/Rate connects graphs to formulas",
            "Practice: differentiate then substitute numbers",
        ],
        "trigonometry_notes.pdf": [
            "Identity: sin^2 x + cos^2 x = 1",
            "tan x = sin x / cos x",
            "Pythagorean forms help simplify expressions",
            "Double-angle: sin(2x)=2sinx cosx",
            "Double-angle: cos(2x)=cos^2x - sin^2x",
            "Use unit circle for signs in different quadrants",
            "Simplify first, then solve equations",
        ],
        "physics_basics.pdf": [
            "Newton 1: ΣF = 0 => velocity is constant",
            "Newton 2: F_net = m a",
            "Newton 3: forces come in action-reaction pairs",
            "Kinematics: v = u + a t",
            "Kinematics: s = u t + (1/2) a t^2",
            "Energy: KE + PE + thermal = bookkeeping",
            "Momentum: p = m v (conserved in collisions)",
        ],
        "chemistry_reactions.pdf": [
            "Balance equations: atoms conserved",
            "Mole concept: n = m / M",
            "Gas law: PV = nRT",
            "pH = -log10([H+])",
            "Rate: faster when concentration is higher",
            "Equilibrium shifts with Le Chatelier's principle",
            "Redox: oxidation loses e-, reduction gains e-",
        ],
        "biology_diagrams.pdf": [
            "Central dogma: DNA -> RNA -> protein",
            "Cell energy: ATP is the energy currency",
            "Mitosis: one cell becomes two identical cells",
            "Meiosis: produces gametes with half the chromosomes",
            "Enzymes: lower activation energy",
            "DNA replication copies the genome before division",
            "Organ systems work together to maintain homeostasis",
        ],
        "english_grammar.pdf": [
            "Parts of speech: Noun, Verb, Adj, Adv, Pronoun",
            "Subject-verb agreement: singular + singular",
            "Punctuation: comma before 'but' in complex sentences",
            "Tenses: keep verb tense consistent in a paragraph",
            "Pronouns: match number and person (he/they, etc.)",
            "Use active voice to improve clarity",
            "Proofread: check spelling + repeated words",
        ],
        "english_vocabulary.pdf": [
            "Context clues: definition, example, contrast",
            "Prefixes: un-, re-, pre-, inter-",
            "Suffixes: -tion, -ment, -able, -less",
            "Synonyms: meanings close, but not always identical",
            "Antonyms: exact opposites are rare; use best match",
            "Chunking helps: learn words with patterns",
            "Practice: use new words in one sentence each",
        ],
        "writing_skills.pdf": [
            "Thesis: one arguable claim (not a topic)",
            "PEEL paragraph: Point, Evidence, Explain, Link",
            "Use transitions: however, therefore, for example",
            "Evidence: quote or data + cite source",
            "Explain 'why' the evidence proves your point",
            "Conclusion: restate claim + what it means",
            "Edit: cut filler; strengthen verbs and specifics",
        ],
        "dbms_notes.pdf": [
            "ACID: Atomicity, Consistency, Isolation, Durability",
            "SQL: SELECT ... FROM ... WHERE ...",
            "Primary key: uniquely identifies a row",
            "Index speeds lookup but costs storage",
            "Joins: INNER join matches, OUTER keeps non-matches",
            "Normalization reduces redundancy",
            "Transactions ensure correctness under failures",
        ],
        "os_notes.pdf": [
            "OS roles: process, memory, files, scheduling",
            "Process vs thread: thread shares memory within a process",
            "System calls are the 'API' to request OS services",
            "Deadlock condition set: mutual exclusion, hold & wait, no preemption, circular wait",
            "Avoid deadlock: resource ordering, timeouts, detection",
            "Paging supports virtual memory with frames/pages",
            "Think in: ready/blocked/waiting queues",
        ],
        "cn_notes.pdf": [
            "IP address identifies a host",
            "TCP handshake: SYN -> SYN/ACK -> ACK",
            "UDP is connectionless; lower overhead",
            "Latency ≈ distance / speed + processing delays",
            "Bandwidth limits throughput",
            "DNS translates names to IPs",
            "Ports: application endpoints on a host",
        ],
        "dsa_arrays.pdf": [
            "Array indexing: O(1) random access",
            "Binary search: O(log n) when array is sorted",
            "Two pointers: O(n) for many subarray problems",
            "Prefix sums turn range queries into O(1) each",
            "Complexity counts operations, not wall-clock time",
            "Space tradeoff: extra memory for faster queries",
            "Practice pattern: sort + scan",
        ],
        "dsa_graphs.pdf": [
            "BFS visits by layers: shortest path in unweighted graphs",
            "DFS explores deep first; useful for cycles and topological sort",
            "Topological sort works for DAGs",
            "Connectivity: components in undirected graphs",
            "Edge cases: disconnected graphs and isolated nodes",
            "Complexity: O(V+E) typical for BFS/DFS",
            "Use visited/parent to reconstruct paths",
        ],
        "ai_intro.pdf": [
            "Supervised: learn f(x)->y from (x,y) pairs",
            "Loss measures prediction error",
            "Gradient descent minimizes loss over parameters",
            "Overfitting: training good, validation poor",
            "Regularization: reduce complexity, improve generalization",
            "Classification: choose class with highest score",
            "Don't forget: train/val/test split",
        ],
        "ds_structures.pdf": [
            "Stack: LIFO  (push/pop)",
            "Queue: FIFO (enqueue/dequeue)",
            "HashMap average lookup: O(1)",
            "Tree: hierarchical search, ordered by comparisons",
            "BST in-order traversal gives sorted order",
            "Heaps: parent dominates children (min/max heap)",
            "Complexity varies: average vs worst-case",
        ],
        "os_scheduling.pdf": [
            "FCFS: simple, can suffer from 'convoy effect'",
            "SJF: shortest job first; can starve long tasks",
            "Round Robin: quantum balances response time",
            "Starvation prevention: aging/priority boost",
            "Turnaround time = completion - arrival",
            "Waiting time accumulates in ready queue",
            "Scheduling is a tradeoff: fairness vs throughput",
        ],
    }

    def _pick_random_lines(filename_key: str, options: list[str], count: int) -> list[str]:
        # Deterministic 'random' so the same PDF is stable across runs.
        seed = int(hashlib.sha256(filename_key.encode("utf-8")).hexdigest(), 16) % (2**32)
        rnd = random.Random(seed)
        if len(options) <= count:
            return options
        indices = list(range(len(options)))
        rnd.shuffle(indices)
        picked = indices[:count]
        # Keep original order for readability.
        picked_sorted = sorted(picked)
        return [options[i] for i in picked_sorted]

    for filename, title in catalog:
        path = out / filename
        c = canvas.Canvas(str(path), pagesize=letter)
        width, height = letter
        c.setTitle(title)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, title)

        c.setFont("Helvetica", 11)
        c.drawString(72, height - 105, "Quick offline notes (study-ready formulae + key ideas):")

        options = content_options.get(filename, [])
        lines = _pick_random_lines(filename, options, count=6) if options else []
        y = height - 140
        line_height = 16
        for line in lines:
            c.drawString(72, y, line[:110])
            y -= line_height

        # Tiny footer for the demo PDFs
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(72, 60, "Tip: open the PDF and try 3 practice questions from your course notes.")

        c.showPage()
        c.save()


# Curated for embed playback (replace IDs if a video is region-blocked or removed).
DEMO_VIDEO_CATALOG = [
    ("Mathematics", "Khan Academy — Variables, expressions, equations", "f15zA0PhSek"),
    ("Mathematics", "3Blue1Brown — Essence of Calculus", "WUvTyaaNkzM"),
    ("Computer Science", "freeCodeCamp — Python Full Course", "rfscVS0vtbw"),
    ("Computer Science", "MIT OpenCourseWare — Linear Algebra (Lecture 1)", "ZK3O402wf1c"),
    ("Science", "Khan Academy — One-dimensional motion (physics)", "uIojjqSm0m4"),
    ("English", "Crash Course Literature — How and Why We Read", "MSYw502dJNY"),
    ("Artificial Intelligence", "3Blue1Brown — Neural Networks", "aircAruvnKk"),
]


SUBJECTS = [
    "Mathematics",
    "Science",
    "English",
    "Computer Science",
    "Artificial Intelligence",
    "Data Structures",
    "Operating Systems",
]


def _modules_for_subject(subject: str) -> list[dict]:
    base_path = "/static/pdfs"
    common = {
        "notes": True,
        "has_video": True,
        "has_assignment": True,
    }
    if subject == "Mathematics":
        return [
            {
                "id": "m-alg",
                "title": "Algebra Foundations",
                "pdfs": [
                    {"id": "pdf-alg", "title": "Algebra Basics", "file": f"{base_path}/algebra_basics.pdf"},
                ],
                **common,
            },
            {
                "id": "m-calc",
                "title": "Calculus Intro",
                "pdfs": [
                    {"id": "pdf-calc", "title": "Calculus Introduction", "file": f"{base_path}/calculus_intro.pdf"},
                ],
                **common,
            },
            {
                "id": "m-trig",
                "title": "Trigonometry",
                "pdfs": [
                    {"id": "pdf-trig", "title": "Trigonometry Notes", "file": f"{base_path}/trigonometry_notes.pdf"},
                ],
                **common,
            },
        ]
    if subject == "Science":
        return [
            {
                "id": "s-phy",
                "title": "Physics Basics",
                "pdfs": [{"id": "pdf-phy", "title": "Physics Basics", "file": f"{base_path}/physics_basics.pdf"}],
                **common,
            },
            {
                "id": "s-che",
                "title": "Chemistry Reactions",
                "pdfs": [
                    {"id": "pdf-che", "title": "Chemistry Reactions", "file": f"{base_path}/chemistry_reactions.pdf"}
                ],
                **common,
            },
            {
                "id": "s-bio",
                "title": "Biology Diagrams",
                "pdfs": [{"id": "pdf-bio", "title": "Biology Diagrams", "file": f"{base_path}/biology_diagrams.pdf"}],
                **common,
            },
        ]
    if subject == "English":
        return [
            {
                "id": "e-gram",
                "title": "Grammar Guide",
                "pdfs": [{"id": "pdf-gram", "title": "Grammar Guide", "file": f"{base_path}/english_grammar.pdf"}],
                **common,
            },
            {
                "id": "e-vocab",
                "title": "Vocabulary",
                "pdfs": [
                    {"id": "pdf-vocab", "title": "Vocabulary Notes", "file": f"{base_path}/english_vocabulary.pdf"}
                ],
                **common,
            },
            {
                "id": "e-write",
                "title": "Writing Skills",
                "pdfs": [{"id": "pdf-write", "title": "Writing Skills", "file": f"{base_path}/writing_skills.pdf"}],
                **common,
            },
        ]
    if subject == "Computer Science":
        return [
            {
                "id": "cs-dbms",
                "title": "DBMS",
                "pdfs": [{"id": "pdf-dbms", "title": "DBMS Notes", "file": f"{base_path}/dbms_notes.pdf"}],
                **common,
            },
            {
                "id": "cs-os",
                "title": "Operating Systems",
                "pdfs": [{"id": "pdf-osn", "title": "OS Notes", "file": f"{base_path}/os_notes.pdf"}],
                **common,
            },
            {
                "id": "cs-cn",
                "title": "Computer Networks",
                "pdfs": [{"id": "pdf-cn", "title": "CN Notes", "file": f"{base_path}/cn_notes.pdf"}],
                **common,
            },
            {
                "id": "cs-dsa",
                "title": "Data Structures & Algorithms",
                "pdfs": [
                    {"id": "pdf-dsa1", "title": "DSA: Arrays & Complexity", "file": f"{base_path}/dsa_arrays.pdf"},
                    {"id": "pdf-dsa2", "title": "DSA: Graph Algorithms", "file": f"{base_path}/dsa_graphs.pdf"},
                ],
                **common,
            },
        ]
    if subject == "Artificial Intelligence":
        return [
            {
                "id": "ai-intro",
                "title": "AI Introduction",
                "pdfs": [{"id": "pdf-ai", "title": "AI Introduction", "file": f"{base_path}/ai_intro.pdf"}],
                **common,
            },
        ]
    if subject == "Data Structures":
        return [
            {
                "id": "ds-core",
                "title": "Core Structures",
                "pdfs": [
                    {"id": "pdf-ds", "title": "Core Data Structures", "file": f"{base_path}/ds_structures.pdf"},
                    {"id": "pdf-dsa1", "title": "DSA: Arrays & Complexity", "file": f"{base_path}/dsa_arrays.pdf"},
                ],
                **common,
            },
        ]
    if subject == "Operating Systems":
        return [
            {
                "id": "os-core",
                "title": "OS Foundations",
                "pdfs": [
                    {"id": "pdf-osn", "title": "OS Notes", "file": f"{base_path}/os_notes.pdf"},
                    {"id": "pdf-sched", "title": "CPU Scheduling", "file": f"{base_path}/os_scheduling.pdf"},
                ],
                **common,
            },
        ]
    return [
        {
            "id": "gen-1",
            "title": f"{subject} Overview",
            "pdfs": [],
            **common,
        }
    ]


def _demo_quizzes() -> list[dict]:
    now = datetime.now(timezone.utc)
    quizzes = []
    qid = 0

    def add_quiz(subject: str, title: str, questions: list[dict]):
        nonlocal qid
        qid += 1
        quizzes.append(
            {
                "quiz_id": f"quiz-{qid}",
                "subject": subject,
                "title": title,
                "time_limit_minutes": 12,
                "questions": questions,
                "created_at": now,
            }
        )

    add_quiz(
        "Mathematics",
        "Algebra Quick Check",
        [
            {
                "id": "mq1",
                "type": "mcq",
                "prompt": "Solve for x: 2x + 6 = 14",
                "options": ["x=3", "x=4", "x=5", "x=6"],
                "answer": "x=4",
            },
            {
                "id": "mq2",
                "type": "true_false",
                "prompt": "The slope of a horizontal line is 0.",
                "options": ["True", "False"],
                "answer": "True",
            },
            {
                "id": "mq3",
                "type": "fib",
                "prompt": "Derivative of x^2 is ____ x . (one word)",
                "options": [],
                "answer": "2",
            },
        ],
    )
    add_quiz(
        "Computer Science",
        "DSA Basics",
        [
            {
                "id": "cq1",
                "type": "mcq",
                "prompt": "Average time search in a balanced BST is",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
                "answer": "O(log n)",
            },
            {
                "id": "cq2",
                "type": "true_false",
                "prompt": "A queue is LIFO.",
                "options": ["True", "False"],
                "answer": "False",
            },
            {
                "id": "cq3",
                "type": "fib",
                "prompt": "Hash map average lookup is O(____). (1 or log n or n)",
                "options": [],
                "answer": "1",
            },
        ],
    )
    add_quiz(
        "Operating Systems",
        "OS Concepts",
        [
            {
                "id": "oq1",
                "type": "mcq",
                "prompt": "Which prevents deadlock by ordering resources?",
                "options": ["Banker's algorithm", "Circular wait elimination", "Thrashing", "Paging"],
                "answer": "Circular wait elimination",
            },
            {
                "id": "oq2",
                "type": "true_false",
                "prompt": "Round-robin scheduling can cause starvation.",
                "options": ["True", "False"],
                "answer": "False",
            },
            {
                "id": "oq3",
                "type": "fib",
                "prompt": "Four conditions of deadlock: mutual exclusion, hold and wait, no preemption, and ____ wait.",
                "options": [],
                "answer": "circular",
            },
        ],
    )
    return quizzes


async def seed_if_empty() -> None:
    ensure_sample_pdfs()
    db = get_database()
    if await db.courses.count_documents({}) == 0:
        courses = []
        for subject in SUBJECTS:
            courses.append(
                {
                    "title": subject,
                    "subject": subject,
                    "description": f"Structured LearnFlow pathway for {subject} with notes, videos, and quizzes.",
                    "modules": _modules_for_subject(subject),
                    "created_at": datetime.now(timezone.utc),
                }
            )
        await db.courses.insert_many(courses)

    if await db.quizzes.count_documents({}) == 0:
        await db.quizzes.insert_many(_demo_quizzes())

    # Flatten materials collection for search/downloads
    if await db.materials.count_documents({}) == 0:
        materials = []
        for subject in SUBJECTS:
            for mod in _modules_for_subject(subject):
                for pdf in mod.get("pdfs", []):
                    materials.append(
                        {
                            "id": pdf["id"],
                            "title": pdf["title"],
                            "subject": subject,
                            "module_id": mod["id"],
                            "file": pdf["file"],
                            "type": "pdf",
                        }
                    )
        if materials:
            await db.materials.insert_many(materials)

    # Demo videos: insert if empty, always refresh YouTube IDs / titles for known slots
    if await db.videos.count_documents({}) == 0:
        docs = [
            {
                "video_id": f"vid-{i}",
                "subject": s,
                "title": t,
                "youtube_id": y,
                "tags": ["education", "learnflow"],
            }
            for i, (s, t, y) in enumerate(DEMO_VIDEO_CATALOG)
        ]
        await db.videos.insert_many(docs)
    else:
        for i, (s, t, y) in enumerate(DEMO_VIDEO_CATALOG):
            await db.videos.update_one(
                {"video_id": f"vid-{i}"},
                {"$set": {"subject": s, "title": t, "youtube_id": y, "tags": ["education", "learnflow"]}},
            )

    # Daily challenges
    if await db.challenges.count_documents({}) == 0:
        await db.challenges.insert_many(
            [
                {
                    "challenge_id": "dc-1",
                    "title": "10-minute Algebra sprint",
                    "xp": 40,
                    "subject": "Mathematics",
                },
                {
                    "challenge_id": "dc-2",
                    "title": "Read one OS note section",
                    "xp": 30,
                    "subject": "Operating Systems",
                },
            ]
        )


def static_mount_path() -> str:
    p = Path(__file__).resolve().parent.parent / "public"
    p.mkdir(parents=True, exist_ok=True)
    return str(p)
