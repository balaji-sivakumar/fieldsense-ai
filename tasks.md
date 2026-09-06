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
| M2 — AssemblyAI voice loop | Sep 8–10 | Complete |
| M3 — Tool calling | Sep 11–14 | Complete |
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

- [x] `backend/assemblyai_gateway.py` — connects directly to `wss://agents.assemblyai.com/v1/ws` with the raw API key (server-to-server, no browser token flow needed), configures the session inline via `session.update` (no pre-created agent)
- [x] `backend/session_manager.py` — minimal per-session record (id, state); risk tier / active work order deferred to M6 as planned
- [x] `/ws/voice` endpoint (`backend/voice_ws.py`) — bidirectional relay: binary PCM16 browser→backend→AssemblyAI, translated JSON events AssemblyAI→backend→browser
- [x] Frontend mic capture (`frontend/src/voice.ts` `MicStreamer`) and streamed playback (`AudioPlayer`) — 24kHz mono PCM16 both directions
- [x] Transcript and agent state (idle/connecting/ready/listening/thinking/speaking/error/closed) displayed live in `VoicePanel.tsx`
- [x] Disconnects and errors surfaced clearly in the UI
- [x] Manual test: bad/missing API key (verified live — clean `error` state, no crash)
- [x] Manual test: abrupt disconnect mid-session (tab closed mid-greeting — verified backend tears down in ~1s, no orphaned AssemblyAI session)
- [x] Error-path review (asyncio.gather not cancelling sibling task → orphaned tasks + billing leak on abandoned sessions; session_manager leak on close failure; 2 minor frontend hardening gaps) — all fixed and re-verified live

**Exit condition:** met — verified live in a browser (not just tests): heard the configured greeting spoken, watched state progress idle→connecting→speaking→listening, saw transcript populate. Correctly cannot answer asset questions yet (no tools registered) — expected, that's M3's job. No AssemblyAI docs MCP server was needed at runtime; it was added as a dev-tooling aid per CLAUDE.md's MCP rule.

## M3 — Tool calling (Sep 11–14)

- [x] Write strict JSON Schemas for all 9 tools (`backend/tool_schemas.py`)
- [x] `backend/tool_registry.py` — validates args via `jsonschema`, dispatches with a 10s timeout, records audit + broadcasts to dashboard; single chokepoint for both REST and voice
- [x] Implement remaining tools: `get_maintenance_history`, `check_parts_inventory`, `record_observation`, `escalate_to_specialist`, `complete_work_order` (`search_manual` still stubbed until M4, as planned)
- [x] Audit every tool call to `tool_audit_log` (tool name, args JSON, status, session ID, timestamp)
- [x] Structured error on missing/invalid args (JSON-Schema validation) and on timeout (`asyncio.wait_for`) — never a raw exception reaching AssemblyAI
- [x] `/ws/dashboard` endpoint (`dashboard_hub.py`) — broadcasts every tool call/result live, from REST or voice
- [x] Dashboard UI: live tool call feed (`frontend/src/Dashboard.tsx`)
- [x] Tests: 18 pytest cases — all 9 tools, schema validation failures (missing field, wrong type), unknown tool, unknown asset/work-order-id errors
- [x] Architecture decision (grounded in AssemblyAI's live docs, not assumed): **client-side function tools**, not HTTP tools — HTTP tools need AssemblyAI's servers to reach a public URL, unreachable from `localhost` before M7; client-side tools keep the whole call/result round trip inside the one WebSocket connection already open, matching both the hackathon's "single connection" requirement and the rule that the LLM only *decides*, execution stays backend-controlled
- [x] `tool.result` sent only after `reply.done` per AssemblyAI's required ordering (queued in `voice_ws.py`, flushed on `reply.done`)

**Exit condition:** met — verified live by voice, not just tests. Real `tool_audit_log` rows carry the actual voice session's UUID: `get_live_telemetry({"asset_id":"AC-1"})` correctly errored (misheard asset ID), then `get_live_telemetry({"asset_id":"AC-104"})` and `get_maintenance_history({"asset_id":"AC-104"})` both succeeded — self-correction handled cleanly, spoken answer grounded in real tool results, dashboard updated live throughout.

**Bug found and fixed during this milestone:** `/ws/dashboard` had the same disconnect-handling mistake as `voice_ws.py` had before the M2 review — raw `websocket.receive()` without checking for `"websocket.disconnect"`, causing an unhandled `RuntimeError` when a dashboard tab closed. Fixed with the same pattern already used in `voice_ws.py`.

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
