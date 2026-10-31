# LearnFlow — AI Learning & Teaching Platform

LearnFlow is a full-stack EdTech platform built as a B.Tech major project. Students learn from courses, study PDFs and videos, take quizzes, chat with an AI tutor and track their progress, while teachers and admins monitor activity through their own dashboards. The system is built as an **Angular 19** single-page application talking to a **FastAPI** REST backend, with role-based access control, an AI tutor, and a machine-learning recommendation engine.

## My contribution

I worked on the **Python (FastAPI) backend**, designing and building the REST APIs that supply quizzes and learning material to the Angular frontend: quiz listing, quiz attempts, automatic scoring and leaderboards, and the course, material and bookmark endpoints.

## Features

| Area | What it does |
|------|--------------|
| **Authentication** | Signup and login with JWT tokens and bcrypt-hashed passwords. Three roles: Student, Teacher, Admin. |
| **Courses & materials** | Subject-wise courses with study PDFs, in-browser PDF preview, a downloads page and bookmarks. |
| **Videos** | YouTube video library with per-user watch history. |
| **Quizzes** | Take quizzes, automatic scoring with per-question feedback, results history and a leaderboard. |
| **AI tutor** | Chat with saved history and text summaries, powered by OpenAI with a built-in offline tutor as fallback. |
| **Recommendations** | Suggests PDFs, videos and quizzes matched to a student's weak subjects. |
| **Progress tracking** | Bar, pie and line charts of study time and quiz performance over selectable time ranges. |
| **Gamification** | XP points, daily streaks, badges and challenges. |
| **Teacher & Admin dashboards** | Teachers see class-wide analytics; admins see platform statistics and the full user list. |
| **Search** | Search across courses, study materials and videos. |
| **Notifications** | In-app notifications that can be marked as read. |
| **Settings** | Update profile, change password and set notification preferences. |
| **Theme** | Light, dark, or follow the operating system setting. |
| **Sample content** | 17 study PDFs plus sample courses, quizzes and videos are seeded automatically. |

## Subjects covered

Mathematics (algebra, calculus, trigonometry), Physics, Chemistry, Biology, English (grammar, vocabulary, writing), and Computer Science (DSA, data structures, DBMS, operating systems, computer networks, AI).

## Technical highlights

### Backend architecture
- **FastAPI** application with feature-based routers (auth, users, courses, materials, videos, quizzes, chat, analytics, recommendations, gamification, notifications, search, teacher, admin), all under `/api`.
- **Pydantic** models validate every request, and settings are loaded from environment variables with `pydantic-settings`.
- Fully **asynchronous** request handling with `async`/`await` throughout.
- Automatic **OpenAPI/Swagger** documentation generated from the code.

### Security
- Passwords hashed with **bcrypt** (passlib); plain-text passwords are never stored.
- **JWT** access tokens signed with HS256 and a configurable expiry.
- **Role-based access control** through a reusable `require_roles(...)` dependency: protected endpoints return `403 Forbidden` for the wrong role, so restrictions are enforced on the server, not just hidden in the UI.
- Chat input is **HTML-escaped** before storage to prevent script injection.
- **CORS** is restricted to configured frontend origins.

### Database layer
- Primary storage is **MongoDB** through the async **Motor** driver.
- Includes a custom **SQLite storage engine** (`sqlite_backend.py`) that reproduces the MongoDB query interface (`find`, `find_one`, `insert_one`, `update_one` with upsert, `count_documents`, sorting, limits and aggregation). It supports the update operators `$set`, `$unset`, `$inc`, `$addToSet` and `$pull`, so every route runs unchanged on either database.
- Documents are stored as BSON-compatible JSON, preserving dates and ObjectIds.

### Quiz engine
- Answers are normalised before comparison and each question returns correct/incorrect feedback.
- Score is calculated as a percentage; a score **below 70%** automatically marks that subject as a **weak subject** for the student, and a later pass removes it.
- Each attempt awards XP (25 base + 5 per correct answer).
- The **leaderboard** is built with an aggregation pipeline (`$group` → average score and attempt count per user, `$sort`, `$limit`).

### Recommendation engine (machine learning)
- Built with **scikit-learn**: the student's profile (weak subjects and interests) and every PDF, video and quiz are converted to **TF-IDF vectors** (English stop words removed).
- Items are ranked by **cosine similarity** to the profile and the top matches are returned with their scores.

### AI tutor
- Integrates the **OpenAI API** (`gpt-4o-mini`) for tutoring replies and text summaries, using recent chat history as context.
- **Graceful fallback:** if no API key is set, or if OpenAI returns an authentication, quota or connection error, the tutor explains the problem and switches to a built-in offline tutor instead of failing.
- The offline tutor gives subject-specific study guidance, and the offline summariser produces an **extractive sentence summary**.
- Optional **NLTK** tokenisation with a regex fallback when language data is unavailable.
- Chat history is stored per user (last 40 messages) and can be cleared.

### Gamification and analytics
- **Streaks** are calculated from daily activity: studying on consecutive days extends the streak, and a missed day resets it.
- **Badges** are awarded by rules: *First Steps* (25 XP), *On Fire* (3-day streak) and *Scholar* (200 XP).
- Analytics combine study minutes and quiz results into daily totals for charting.

### Content generation
- Study PDFs are generated programmatically with **reportlab** and served as static files.
- The database is **seeded automatically** with courses, materials, quizzes and videos when it is empty.

### Frontend (Angular 19)
- Built entirely with **standalone components** and Angular **signals**.
- **Route guards** protect logged-in pages and keep logged-in users away from login and signup pages.
- An **HTTP interceptor** attaches the JWT to every API request automatically.
- Separate **services** for authentication, learning content, chat and theme keep logic out of components.
- **Angular Material** components and **Tailwind CSS** for a responsive layout.
- **Chart.js** for interactive progress charts.
- Theme service with **light, dark and system** modes, remembered between visits.
- Role-aware dashboard that shows extra teacher and admin panels depending on the logged-in user's role.

## Repository layout

| Path | Description |
|------|-------------|
| `frontend/src/app/pages/` | One folder per screen: dashboard, courses, videos, quizzes, chat, progress, search, notifications, settings, auth. |
| `frontend/src/app/core/` | Auth and theme services, route guards and the HTTP interceptor. |
| `frontend/src/app/services/` | API services for learning content and chat. |
| `backend/routes/` | REST API endpoints, one file per feature area. |
| `backend/ai/` | AI tutor (`chatbot.py`), recommendation engine (`recommendations.py`), NLP helpers (`nlp_utils.py`). |
| `backend/middleware/` | Authentication and role-checking dependencies. |
| `backend/utils/` | Password hashing, JWT handling and input sanitisation. |
| `backend/services/seed_db.py` | PDF generation and sample-data seeding. |
| `backend/database.py`, `sqlite_backend.py` | Storage layer: MongoDB, or SQLite with the same query interface. |

## Tech stack

**Frontend:** Angular 19, Angular Material, Tailwind CSS, Chart.js, RxJS, TypeScript
**Backend:** Python, FastAPI, Pydantic, Motor (MongoDB), aiosqlite (SQLite), python-jose (JWT), passlib/bcrypt, scikit-learn, NLTK, reportlab, OpenAI SDK
