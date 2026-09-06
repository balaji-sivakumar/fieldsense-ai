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
