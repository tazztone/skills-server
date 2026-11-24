---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) outside native Orchestrator, before editing or spawning.'
---

# Plan Executor

**Gate**: Never edit, pick defaults, or spawn before Q1 finishes.

## 1. Ask Mode (Q1)
Call `ask_question` once with short labels (omit raw IDs in UI; do **not** call `swarm{action:"models"}` beforehand):
- `(Recommended) Inline (current session)`
- `Swarm: Neon Med -> Hydrogen Low` (`gemini-4-neon-medium` / `gemini-4-hydrogen-low`)
- `Swarm: Neon High -> Hydrogen Low` (`gemini-4-neon-high` / `gemini-4-hydrogen-low`)
- `Swarm: Neon High -> Hydrogen Med` (`gemini-4-neon-high` / `gemini-4-hydrogen-medium`)
- `Swarm: Neon XHigh -> Hydrogen Med` (`gemini-4-neon-xhigh` / `gemini-4-hydrogen-medium`)
- `Swarm: Neon Med -> Sonnet Med` (`gemini-4-neon-medium` / `claude-sonnet-5-5-medium`)
- `Swarm: Argon High -> Hydrogen Low` (`gemini-4-argon-high` / `gemini-4-hydrogen-low`)
- `Swarm: Current -> Hydrogen Low` (`gemini-4-hydrogen-low`)
- `Swarm: Current -> Hydrogen Med` (`gemini-4-hydrogen-medium`)
- `Custom Swarm (Coordinator + Worker)...`

On `Custom Swarm`: call `swarm{action:"models", all:true}`, then `ask_question` (`quota_remaining > 0%`, never `gemini-pro-orchestrator*`):
- **Coordinator**: `(Recommended) Current`, plus available `high`/`xhigh` models.
- **Worker**: available Hydrogen, 3.8 Flash, Sonnet (`low` -> `high`; others fallback).

## 2. Execute
- **Inline**: Work directly here; never call `swarm`.
- **Swarm** (never `gemini-pro-orchestrator*` for Coordinator or Worker):
  - Call `swarm{action:"add", model:"<worker>"}` with the approved plan path.
  - If quota rejects `add`/`model`, call `swarm{action:"models", all:true}` to switch or re-ask.
  - If Coordinator != active model, call `swarm{action:"model", model:"<coordinator>"}` **after** `add`; on Turn-2 self-wakeup, call `swarm_wait{since:<brief_seq>}` without re-briefing.
