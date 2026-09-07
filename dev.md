# Local development

No application code exists yet (as of M0) — these are the commands
M1 must make true, documented now so scaffolding has a fixed target.

## Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # fill in real values; never commit .env
uvicorn app:app --reload
```

Health check: `curl http://localhost:8000/health`

## Backend tests

```bash
cd backend
pytest
```

## Validate tools against a running backend

`tests/test_tools.py` calls `tool_registry.dispatch()` directly against
an isolated test DB. To sanity-check the actual running server instead
(real HTTP, real dev DB) — e.g. after starting the backend, or after a
tool change — run:

```bash
cd backend
python scripts/validate_tools.py
```

Exercises all 9 tools plus a couple of error paths, prints PASS/FAIL
per check, exits non-zero if anything failed. Set `BACKEND_URL` to
point at a non-default host.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

See `.env.example` for the full list. For local development without
AssemblyAI/Neon/Chroma (M1 only), `DATABASE_URL` can point at a local
SQLite file and the other keys can stay empty until M2–M4 need them.
