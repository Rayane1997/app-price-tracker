# Repository Guidelines

## Project Structure & Module Organization
- `backend/app/` houses FastAPI routers, schemas, Celery workers, and helper utilities; stick to feature-based subpackages (`api/`, `schemas/`, `utils/`).
- `backend/alembic/` tracks migrations (new scripts go in `versions/`), while `backend/tests/` contains unit, integration, and worker-flow suites.
- `frontend/` is a Vue 3 + Vite SPA with components in `src/components/`, Pinia stores in `src/stores/`, and shared helpers in `src/utils/formatters.js`.
- Root-level assets (`docker-compose.yml`, `test_phase_k.sh`, `README.md`) document orchestration, CI smoke tests, and contributor docs; keep them updated when you add services or flows.

## Build, Test, and Development Commands
- Full stack via Docker: `docker-compose up --build` brings up API, worker, beat, PostgreSQL, Redis, and the frontend.
- Manual backend loop: `cd backend && pip install -r requirements.txt && playwright install chromium && uvicorn app.main:app --reload` (run Celery worker/beat in parallel with `celery -A app.workers.celery_app worker` and `celery -A app.workers.celery_app beat`).
- Manual frontend loop: `cd frontend && npm install && npm run dev` (served at `http://localhost:5173` with `VITE_API_BASE_URL` pointing to the backend).
- Run backend tests with `cd backend && pytest` or `pytest --cov=app --cov-report=term` for coverage; build the SPA with `npm run build`.

## Coding Style & Naming Conventions
- Python follows PEP 8, 100-character lines, and full type hints; use `snake_case` for modules/functions, `PascalCase` for models/schemas, and keep FastAPI routes grouped by domain.
- Vue components live in `PascalCase` files (e.g., `AlertCard.vue`), composables or stores use camelCase exports, and prefer `const` with Composition API scripts.
- Run Black/ruff locally if configured, ESLint/Tailwind defaults via Vite, and keep environment files (`.env`, `.env.example`) free of secrets.

## Testing Guidelines
- Tests use `pytest`, `pytest-asyncio`, and `pytest-cov`; place new unit tests beside related modules (e.g., `backend/tests/test_promo_detector.py`), and create integration cases under `backend/tests/integration/`.
- Name tests `test_<area>.py` with descriptive function names, mock network calls where possible, and keep coverage near existing levels (~85% per README).
- For worker or parser changes, run targeted suites such as `pytest tests/integration/test_worker_flows.py` plus any relevant unit modules before opening a PR.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat(parser): ...`, `fix(api): ...`); describe broad updates succinctly (e.g., `docs: refresh README quick start`).
- Branch from `main` using `feature/<summary>` or `fix/<issue>` (avoid committing directly to `main`); keep commits scoped and rebased.
- Every PR should link the motivating issue, summarize backend/frontend impacts, attach screenshots for UI tweaks, note migrations, and confirm `pytest` + frontend build results; update `CHANGELOG.md` and README sections touched by your change.

## Security & Configuration Tips
- Copy `.env.example` to `.env` for backend secrets and `frontend/.env` for the API base URL; never commit personal credentials or Playwright artifacts.
- When adding services, mirror their configuration in `docker-compose.yml` and document required environment variables in `README.md` and `QUICKSTART.md`.
- Run `alembic upgrade head` after introducing migrations and coordinate schema changes with frontend data contracts (`frontend/src/services/*`).
