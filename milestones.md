# FieldSense AI — Milestones & submission plan

Hackathon: AssemblyAI Voice Agent Hackathon (lablab.ai), Sep 1–30, 2026.
Submissions close **Sep 30, 8:30 PM IST**. Today is Sep 5.

**Chosen path:** Voice Agent API (not Realtime STT + bring-your-own
orchestration). AssemblyAI owns STT, LLM routing, turn-taking, VAD, tool
calling, and voice output over a single connection — the right fit for a
hands-free field-tech agent where natural turn-taking and low latency
matter more than owning every layer of the stack.

## Milestone schedule

| Dates (2026) | Milestone | Deliverable / exit condition | Judging criteria it feeds |
| --- | --- | --- | --- |
| Sep 5–7 | M0: Repository & instructions | Public repo, `CLAUDE.md`/`AGENTS.md` working agreement, `.env.example`, safe `.gitignore`, documented run/test commands | — (foundation) |
| Sep 5–7 | M1: Thin vertical slice | One asset (`AC-104`), one telemetry tool, one manual lookup, one work-order creation, minimal browser UI, backend tests. Done when a request traverses UI → backend → tools → DB without AssemblyAI | Application of Technology |
| Sep 8–10 | M2: AssemblyAI voice loop | Voice Agent API session established, mic streamed in, audio played back, transcript + agent state shown, disconnect/error handling | Application of Technology |
| Sep 11–14 | M3: Tool calling | Strict JSON-Schema tools registered, tool calls received/validated/executed, structured results returned, tool activity visible on dashboard | Application of Technology, Presentation |
| Sep 15–17 | M4: RAG | Manual ingested into Chroma with metadata, retrieval filtered by asset model, sources (document/section/page) shown on dashboard | Application of Technology, Originality |
| Sep 18–20 | M5: Complete demo scenarios | Overheating, dangerous vibration, and low-pressure scenarios implemented with deterministic simulator controls | Business Value, Originality |
| Sep 21–23 | M6: Safety & interruption | Risk classification implemented, barge-in tested mid-speech, flow changes on dangerous telemetry, explicit confirmation for controlled ops, structured specialist handover generated | Originality, Business Value |
| Sep 24–25 | M7: Deployment | Backend on Railway (WebSockets verified), frontend on Vercel (HTTPS/WSS configured), Neon + Chroma Cloud + secrets configured, synthetic data seeded, full demo run on a clean browser + mobile device | Presentation |
| Sep 26–27 | Submission content | Cover image, slide deck, video presentation, written descriptions and tags drafted | Presentation |
| Sep 28–29 | Final recording & clean-env test | Backup video recorded, full run-through on a genuinely clean browser/device, no reliance on a developer laptop staying online | Presentation |
| **Sep 30, before ~6 PM IST** | **Submit** | Everything below is filed with margin before the 8:30 PM cutoff | — |

## Submission checklist (verbatim from the hackathon brief)

- [ ] Project title
- [ ] Short description
- [ ] Long description
- [ ] Technology & category tags
- [ ] Cover image
- [ ] Video presentation
- [ ] Slide presentation
- [ ] Public GitHub repository
- [ ] Demo application platform *(name Railway + Vercel explicitly — easy to miss since it's a separate field from the URL)*
- [ ] Application URL

Extras beyond the bare checklist that strengthen Presentation and
Application of Technology scoring, per the README's own hackathon
alignment notes:
- [ ] Architecture diagram (`docs/architecture.md`)
- [ ] Tested backup video (in case live demo WiFi/mic fails at judging time)

## Judging criteria — where each one is actually won

| Criteria | Primarily won in |
| --- | --- |
| Application of Technology | M1–M4 — visible tool calls, real Universal-3 Pro STT, JSON-Schema tool calling, turn-taking/barge-in |
| Presentation | M7 + submission content — clear alarm-to-resolution story, visible tool calls and telemetry, a memorable interruption, a completed work order |
| Business Value | M5–M6 — reduced search time, faster escalation, complete maintenance records, reduced downtime, demonstrated concretely through the three fault scenarios |
| Originality | M4–M6 — the combination of voice + live asset context + manual RAG + maintenance actions + human-controlled safety workflow, not any single piece alone |

## Buffer discipline

The Sep 30 slot is submission-only, not development time. If M5 or M6
slips, the dates to compress are Sep 26–27 (submission content can be
drafted in parallel with M7 deployment, not strictly after it) — never
the Sep 28–29 clean-environment test. A demo that only works on the
developer's laptop fails the "no dependency on a developer laptop
remaining online" hosting requirement and the Presentation criterion
at once.
