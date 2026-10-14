# LearnFlow — AI Learning & Teaching Platform

LearnFlow is a full-stack EdTech demo: **Angular 19** + **Angular Material** + **Tailwind CSS** + **Chart.js** on the frontend, and **FastAPI** + **MongoDB or embedded SQLite** + **JWT** + **OpenAI (optional)** on the backend. With default `DATABASE_MODE=auto`, if MongoDB is not running the API **automatically uses SQLite** (`backend/data/learnflow.db`) so signup works without Docker. It is structured for a B.Tech major project with clear separation of concerns, REST APIs, role-based access, and deployment-oriented configuration.

## Repository layout

| Path | Description |
|------|-------------|
| `frontend/` | Angular SPA (standalone components, guards, HTTP interceptor, dashboards, quizzes, chat, charts). |
| `backend/` | FastAPI API, Mongo (Motor) or SQLite fallback, PDF seeding, AI tutor + sklearn recommendations. |
| `docker-compose.yml` | Local **MongoDB 7** for development. |

## Prerequisites

- **Node.js 20+** and npm (for Angular CLI and build).
- **Python 3.10+** recommended (3.9 may work if dependencies resolve; the repo targets modern Python typing).
- **MongoDB** (optional) — Docker Compose or Atlas. If omitted, the backend uses **SQLite** automatically.

## Quick start (local)

### 1. MongoDB (optional)

For a shared Mongo instance instead of SQLite:

```bash
cd "/Users/jaymehndiratta/Desktop/End_sem project"
docker compose up -d
```

Default URI: `mongodb://localhost:27017` (database name `learnflow`). Set `DATABASE_MODE=mongo` in `backend/.env` to require Mongo.

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Optional: set OPENAI_API_KEY in .env for live LLM replies (otherwise offline tutor text).
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API base: `http://localhost:8000` — OpenAPI docs at `http://localhost:8000/docs`.

Static PDFs are served from `GET /static/pdfs/...` (files are generated on first startup under `backend/public/pdfs/`).

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

App: `http://localhost:4200` — expects API at `http://localhost:8000` (see `src/environments/environment.ts`). Production build replaces this with `environment.prod.ts` (`angular.json` `fileReplacements`).

## Environment variables (backend)

| Variable | Purpose |
|----------|---------|
| `DATABASE_MODE` | `auto` (default), `mongo`, or `sqlite`. |
| `SQLITE_PATH` | SQLite file path when using SQLite (default `data/learnflow.db`). |
| `MONGODB_URI` | Mongo connection string. |
| `MONGODB_DB_NAME` | Database name (default `learnflow`). |
| `JWT_SECRET` | **Change in production** — signing key for access tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime (default one week for demos). |
| `OPENAI_API_KEY` | If set, AI tutor and summary endpoints use OpenAI; else safe offline responses. |
| `CORS_ORIGINS` | Comma-separated allowed origins (e.g. `http://localhost:4200`). |

## Roles & demo accounts

Register via **Signup** (`/signup`) and choose **Student**, **Teacher**, or **Admin**. Teacher/Admin dashboards call extra analytics endpoints (`/api/teacher/overview`, `/api/admin/stats`, `/api/users/admin/list`).

## Optional ML stack

Core installs include **nltk**, **scikit-learn**, and **numpy**. For heavier NLP (as in many project reports), add separately to avoid bloating every machine:

```text
# Example (not installed by default):
transformers
spacy
```

Download spaCy models after install: `python -m spacy download en_core_web_sm`.

## Deployment notes

- **Frontend:** `cd frontend && npm run build` — deploy `dist/learnflow-frontend` to **Netlify** or **Vercel** (SPA fallback to `index.html`).
- **Backend:** Run Uvicorn on **Render** / **Railway** with `MONGODB_URI` pointing to Atlas; set `CORS_ORIGINS` to your frontend URL.
- **MongoDB Atlas:** Whitelist your host IP or `0.0.0.0/0` for demos only.

## Screenshots

Add your own screenshots under `docs/screenshots/` and link them here for the project report (landing, dashboard, quiz results, AI tutor, dark mode).

## Security (production checklist)

- Rotate `JWT_SECRET` and use HTTPS everywhere.
- Do not expose password reset tokens in API responses in production (the demo `forgot-password` response may include a token for local testing).
- Replace placeholder PDFs with institution-licensed content.

## License

Educational use for your coursework; replace branding and content as required by your institution.
