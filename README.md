# LearnFlow — AI Learning & Teaching Platform

LearnFlow is a full-stack EdTech platform built as a B.Tech major project. The frontend uses **Angular 19**, **Angular Material**, **Tailwind CSS** and **Chart.js**. The backend uses **FastAPI**, **MongoDB** (with an automatic **SQLite** fallback when MongoDB is unavailable), **JWT** authentication, **scikit-learn** for recommendations, and **OpenAI** (optional) for the AI tutor. It follows a clear separation of concerns with REST APIs and role-based access.

## Features

| Area | What it does |
|------|--------------|
| **Authentication** | Signup and login with JWT tokens and hashed passwords. Roles: Student, Teacher, Admin. |
| **Courses & materials** | Subject-wise courses with study PDFs, in-browser PDF preview, a downloads page and bookmarks. |
| **Videos** | YouTube video library with per-user watch history. |
| **Quizzes** | Take quizzes, automatic scoring, results history and a leaderboard. |
| **AI tutor** | Chat with saved history and text summaries. Uses OpenAI when configured, otherwise a built-in offline tutor. |
| **Recommendations** | Suggests PDFs, videos and quizzes matched to a student's weak subjects using TF-IDF and cosine similarity. |
| **Progress tracking** | Progress page with Chart.js bar, pie and line charts of study time and quiz performance. |
| **Gamification** | XP points, daily streaks, badges and challenges. |
| **Teacher & Admin dashboards** | Teachers see class overview analytics; admins see platform stats and the user list. |
| **Search** | Search across courses, study materials and videos. |
| **Notifications** | In-app notifications that can be marked as read. |
| **Settings** | Update profile, change password and set notification preferences. |
| **Theme** | Light and dark mode. |
| **Sample content** | 17 study PDFs plus sample courses, quizzes and videos are seeded automatically on first start. |

## Subjects covered

Mathematics (algebra, calculus, trigonometry), Physics, Chemistry, Biology, English (grammar, vocabulary, writing), and Computer Science (DSA, data structures, DBMS, operating systems, computer networks, AI).

## Repository layout

| Path | Description |
|------|-------------|
| `frontend/` | Angular single-page app: standalone components, route guards, HTTP interceptor, pages under `src/app/pages`. |
| `backend/routes/` | REST API endpoints, one file per feature area. |
| `backend/ai/` | AI tutor (`chatbot.py`), recommendation engine (`recommendations.py`), NLP helpers (`nlp_utils.py`). |
| `backend/services/seed_db.py` | Generates the sample PDFs and seeds courses, quizzes and videos. |
| `backend/database.py`, `sqlite_backend.py` | Storage layer: MongoDB, or SQLite with the same query interface. |
| `backend/public/pdfs/` | The generated study PDFs. |

## API overview

All endpoints are under `/api`:

| Group | Endpoints |
|-------|-----------|
| Auth | `register`, `login`, `me` |
| Users | update profile, change password, update settings, admin user list |
| Courses & materials | course list and detail, materials, bookmarks |
| Videos | video list, watch history |
| Quizzes | list, take, submit, leaderboard |
| Chat | send message, history, clear history, summary |
| Analytics | record progress, personal analytics, recommendations |
| Gamification | stats, complete challenge |
| Notifications | list, mark as read |
| Search | global search |
| Teacher / Admin | `teacher/overview` (teacher, admin), `admin/stats` (admin) |

Role-restricted endpoints are protected on the backend, not just hidden in the UI.

## Tech stack

**Frontend:** Angular 19, Angular Material, Tailwind CSS, Chart.js, RxJS, TypeScript
**Backend:** FastAPI, Motor (MongoDB), aiosqlite, python-jose (JWT), passlib/bcrypt, scikit-learn, NLTK, reportlab, OpenAI SDK
