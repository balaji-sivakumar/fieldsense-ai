# Working agreement — FieldSense AI

This file is the persistent rule set for Claude Code in this repo.
`README.md` is the product source of truth; `architecture.md` expands
its architecture section; `milestones.md` has calendar dates and
judging-criteria mapping; `tasks.md` has the per-milestone task
checklist. Read the relevant one before starting work — don't
re-derive scope from memory.

## Rules

1. Work on one milestone at a time (see `tasks.md` for the current one).
2. Before editing, inspect the repository and state the smallest proposed change.
3. Do not add features outside the current milestone's MVP scope without explicit approval.
4. Keep tool outputs structured and deterministic.
5. Keep credentials server-side and never commit secrets. `.env` is gitignored; only `.env.example` (empty values) is tracked.
6. Add or update tests with every behavior change.
7. Run relevant tests and report their results before completing a task.
8. Preserve existing working behavior and avoid unrelated refactoring.
9. Prefer simple implementations suitable for a reliable hackathon demo.
10. Update `tasks.md` (check off completed items) and the README's Progress Log / Next Task after completing a milestone.

## MVP boundary

One equipment type (industrial air compressor), 3 sample assets, 3
deterministic fault scenarios, one synthetic/openly-licensed manual,
simulated telemetry/maintenance history/parts inventory, work-order
creation and completion, manual/runbook RAG, voice via the
AssemblyAI Voice Agent API, mobile-friendly technician UI, judge-facing
dashboard.

Do not integrate real industrial hardware, production systems,
Informatica, Control-M, Kafka, proprietary manuals, or MCP in the
runtime path (AssemblyAI uses its own native tool-call protocol —
MCP is dev-tooling only, e.g. the AssemblyAI docs MCP server).

## Safety model

Risk classification is tracked per session: Observation → Low-risk
inspection → Lockout required → Specialist required → Dangerous
condition. The agent must never claim verbal confirmation proves a
physical environment is safe, bypass site procedures, give unapproved
repair instructions, or execute a safety-critical physical action
itself. Tools only ever touch simulated data — no real actuation
exists in this system.

## Tool contracts

Every tool must: validate input strictly against its JSON Schema,
return structured JSON (never prose), use deterministic synthetic
data, emit an audit event to `tool_audit_log` (tool name, sanitized
args, result status, session ID, timestamp), and return a safe
structured error on missing/invalid data or timeout.
