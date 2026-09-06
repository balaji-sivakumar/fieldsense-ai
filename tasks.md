# FieldSense AI — Task list by milestone

Derived from `README.md`, `architecture.md`, and `milestones.md`. Each
milestone lists concrete tasks and its exit condition. Work top to
bottom — do not start a milestone's tasks before the previous
milestone's exit condition is met.

This file is the live tracker: checkboxes get ticked and the status
table below gets updated as each milestone progresses, committed
along with the work that completed it.

## Status

| Milestone | Dates | Status |
| --- | --- | --- |
| M0 — Repository & instructions | Sep 5–7 | Complete |
| M1 — Thin vertical slice | Sep 5–7 | Complete |
| M2 — AssemblyAI voice loop | Sep 8–10 | Not started |
| M3 — Tool calling | Sep 11–14 | Not started |
| M4 — RAG | Sep 15–17 | Not started |
| M5 — Complete demo scenarios | Sep 18–20 | Not started |
| M6 — Safety and interruption | Sep 21–23 | Not started |
| M7 — Deployment | Sep 24–25 | Not started |
| Submission content | Sep 26–27 | Not started |
| M8 — Final recording & submission | Sep 28–30 | Not started |

## M0 — Repository & instructions (Sep 5–7)

- [x] `git init`, first commit, made locally (remote deferred to M7/M8 by choice)
- [x] Keep `README.md` as canonical; `FieldSense_AI_README.md` deleted
- [x] Write `CLAUDE.md` with the working agreement + MVP constraints (from README §"Claude Code working agreement")
- [x] Add `.gitignore` (`.env`, `__pycache__/`, `venv/`, `node_modules/`, `dist/`, `.DS_Store`, `.idea/`)
- [x] Add `.env.example` with empty values for all 7 vars (`ASSEMBLYAI_API_KEY`, `DATABASE_URL`, `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`, `ALLOWED_ORIGINS`, `APP_ENV`)
- [x] Document exact local run/test commands (backend + frontend) in `dev.md`
- [x] Skipped folder skeleton by design — deferred entirely to M1, per README's "don't scaffold prematurely" rule

**Exit condition:** repo is cloneable, documented, and has no secrets committed.

## M1 — Thin vertical slice (Sep 5–7)

- [x] `backend/app.py` — FastAPI app with `/health`, `/assets/{asset_id}`, and `/tools/*` endpoints
- [x] `backend/database.py` + `backend/models.py` — SQLAlchemy on SQLite for local dev, `assets` + `work_orders` tables
- [x] `backend/data/seed_data.json` — seed asset `AC-104` (model `ACX-200`)
- [x] `get_live_telemetry` — deterministic synthetic reading
- [x] `search_manual` stub — hardcoded manual lookup result (real RAG in M4)
- [x] `create_work_order` tool + `work_orders` table
- [x] `backend/tool_registry.py` — pre-shaped dispatch pattern (`TOOLS` dict + `dispatch()`), no schema validation yet (M3 adds that)
- [x] Real React/Vite/TS frontend (`frontend/`): asset details, telemetry, manual stub, and work-order creation buttons, each rendering its JSON result
- [x] Backend tests (pytest, 8 tests) covering all tools, DB writes, and the unknown-asset error path — all passing
- [x] Manually verified in an actual browser (Chrome via claude-in-chrome): all four buttons work end-to-end against the real backend/DB, no console errors

**Exit condition:** met — verified live in a browser, not just by tests. One request traverses UI → backend → tools → DB successfully, with no AssemblyAI involved.

## M2 — AssemblyAI voice loop (Sep 8–10)

- [ ] `backend/assemblyai_gateway.py` — establish and hold the Voice Agent API session
- [ ] `backend/session_manager.py` — track per-session state (asset, risk tier, active work order)
- [ ] `/ws/voice` endpoint — stream mic audio in from the frontend
- [ ] Play synthesized audio back in the frontend
- [ ] Display transcript and agent state (listening / thinking / speaking) in the UI
- [ ] Handle disconnects and surface clear connection errors in the UI
- [ ] Manual test: deny mic permission, kill the AssemblyAI connection mid-session

**Exit condition:** a technician can speak, hear a spoken response, and see live transcript/state — no tool calls wired yet.

## M3 — Tool calling (Sep 11–14)

- [ ] Write strict JSON Schemas for all 9 tools listed in README §"Initial tool contracts"
- [ ] `backend/tool_registry.py` — validate incoming tool calls, dispatch, return structured JSON
- [ ] Implement remaining tools: `get_asset_details`, `get_maintenance_history`, `check_parts_inventory`, `record_observation`, `escalate_to_specialist`, `complete_work_order` (schema-complete; `search_manual` stays stubbed until M4)
- [ ] Audit every tool call to `tool_audit_log` (tool name, sanitized args, result status, session ID, timestamp)
- [ ] Structured error returned on missing/invalid data or timeout — never let a raw exception reach AssemblyAI
- [ ] `/ws/dashboard` endpoint, separate from `/ws/voice`; broadcast tool calls/results to connected dashboard sockets
- [ ] Dashboard UI: live tool call/argument/result feed
- [ ] Tests: schema validation, valid/invalid asset IDs, tool timeouts, malformed args

**Exit condition:** AssemblyAI can call any of the 9 tools and get back a structured, audited, spoken-ready result; the dashboard shows it live.

## M4 — RAG (Sep 15–17)

- [ ] Write or source one synthetic/openly-licensed compressor manual (e.g. "ACX-200 Service Manual")
- [ ] Chunk the manual and load it into Chroma Cloud with the metadata schema from README §"Chroma Cloud" (`equipment_type`, `manufacturer`, `model`, `document`, `section`, `page`, `content_type`)
- [ ] Implement real `search_manual(asset_model, fault_code, question)` — filter by `asset_model` first, then query
- [ ] Every result returns `document`, `section`, `page`, `content_type`, and text
- [ ] Dashboard: show retrieved manual sources per query
- [ ] Tests: retrieval never leaks results from another asset model

**Exit condition:** a spoken fault-code question returns model-filtered manual evidence with visible citations on the dashboard.

## M5 — Complete demo scenarios (Sep 18–20)

- [ ] Telemetry simulator: deterministic per-scenario controls (temperature, vibration, discharge pressure)
- [ ] Scenario 1 (overheating): correlate elevated temperature with maintenance history → surface overdue intake-filter replacement
- [ ] Scenario 2 (dangerous vibration): reading beyond permitted limit → stop routine troubleshooting → trigger escalation path
- [ ] Scenario 3 (low discharge pressure): combine telemetry + history + manual guidance → identify probable air leak
- [ ] Manual test: run each of the 3 scenarios end-to-end by voice

**Exit condition:** all 3 fault scenarios from README §"Demo scenarios" work end-to-end via voice.

## M6 — Safety and interruption (Sep 21–23)

- [ ] Implement the 5-tier risk classification (Observation → Low-risk inspection → Lockout required → Specialist required → Dangerous condition) in `session_manager.py`
- [ ] `escalate_to_specialist` packages asset, symptoms, readings, history, sources, and actions-already-taken into a structured handover
- [ ] Test barge-in: technician interrupts agent mid-speech, AssemblyAI surfaces it, session manager reclassifies risk and changes flow
- [ ] Require explicit confirmation for "Lockout required" (site procedure completed + independently verified)
- [ ] Dashboard: live risk-classification display, updated as it changes
- [ ] Tests: safety escalation rules, mid-flow measurement change, dangerous reading during routine flow

**Exit condition:** the primary demonstration script's steps 7–9 (interruption → reclassification → specialist handover) work reliably.

## M7 — Deployment (Sep 24–25)

- [ ] Deploy backend to Railway; verify long-lived WebSocket connections survive in that environment
- [ ] Deploy frontend to Vercel; point it at the deployed backend's HTTPS/WSS URLs
- [ ] Configure Neon `DATABASE_URL`, Chroma Cloud credentials, `ALLOWED_ORIGINS` CORS allowlist in Railway/Vercel env vars
- [ ] Seed synthetic data (3 assets, fault scenarios) in the deployed Neon database
- [ ] Confirm health endpoint responds
- [ ] Implement clear degraded-state UI for when AssemblyAI/Postgres/Chroma is unreachable
- [ ] Run the full demo from a clean browser and a mobile device against the deployed URL

**Exit condition:** the demo runs end-to-end on the public URL with no dependency on a developer laptop staying online.

## Submission content (Sep 26–27, can overlap M7)

- [ ] Project title, short description, long description
- [ ] Technology & category tags
- [ ] Cover image
- [ ] Slide presentation
- [ ] Architecture diagram (export from `architecture.md`'s mermaid diagram)
- [ ] Draft video presentation script following the primary demonstration script in README

## M8 — Final recording, clean-env test, submission (Sep 28–30)

- [ ] Record the video presentation
- [ ] Record a tested backup video (in case live mic/WiFi fails at judging time)
- [ ] Full run-through on a genuinely clean browser/device — no reliance on developer laptop
- [ ] Fill the submission checklist verbatim from `milestones.md` (title, descriptions, tags, cover image, video, slides, public repo, demo platform — name Railway + Vercel explicitly, application URL)
- [ ] Submit with margin before the Sep 30, 8:30 PM IST cutoff (target ~6 PM IST)

**Buffer discipline:** if M5 or M6 slips, compress Sep 26–27 (submission content can be drafted in parallel with M7) — never compress Sep 28–29's clean-environment test.
