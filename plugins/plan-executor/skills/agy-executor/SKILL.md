---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) in a non-Orchestrator session before editing files or spawning workers.'
---

# Antigravity Plan Executor

> **Gate Rule**: Editing files, picking default models, or spawning workers before the mode/preset prompt completes violates this skill.

## 1. Lookup Quota and Ask Once

1. Call `swarm{action:"models", all:true}` first, keeping `quota_remaining > 0%` and excluding `gemini-pro-orchestrator-*` from Swarm presets (avoids nested `planexecute`).
2. Call `ask_question` **once** with live quota `%`, omitting any `0%` preset:
   - `(Recommended) Inline (current session)`
   - `Swarm: Argon High -> Hydrogen Low` (`gemini-4-argon-high` + `gemini-4-hydrogen-low`)
   - `Swarm: Argon High -> Hydrogen Med` (`gemini-4-argon-high` + `gemini-4-hydrogen-medium`)
   - `Swarm: Argon High -> 3.8 Flash Med` (`gemini-4-argon-high` + `gemini-3.8-flash-medium`)
   - `Swarm: Argon High -> Sonnet Med` (`gemini-4-argon-high` + `claude-sonnet-5-5-medium`)
   - `Swarm: Neon High -> Hydrogen Low` (`gemini-4-neon-high` + `gemini-4-hydrogen-low`)
   - `Swarm: Current -> Hydrogen Low`
   - `Swarm: Current -> Hydrogen Med`
   - `Custom Swarm (pick Coordinator + Worker)...`
3. If `Custom Swarm` is chosen, call `ask_question` **once** with:
   - **Q1 — Coordinator**: `(Recommended) Keep current model`, plus available non-orchestrator `high`/`xhigh` models.
   - **Q2 — Worker**: available **Hydrogen**, **3.8 Flash**, and **Sonnet** variants ordered **`low` -> `high`** (other non-exhausted models only as fallback).

## 2. Execute

- **Inline**: Implement, verify, and commit directly in the current session (never call `swarm`).
- **Swarm**:
  1. Hand off topology, `workspace`, `brief`, and `kill` to vanilla `/swarm` pinned to the chosen worker model with the approved plan artifact path.
  2. If Coordinator model differs from the active session model, call `swarm{action:"model", model:"<coordinator-model>"}` **after** `swarm{action:"add"}`.
  3. On Turn-2 coordinator self-wakeup (`"You switched to the model ... Continue coordinating"`), call `swarm_wait{since: <brief_seq>}` — do **not** re-brief.
  4. Review final diffs/commits on Coordinator before killing workers.
