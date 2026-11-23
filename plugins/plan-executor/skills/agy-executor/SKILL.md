---
name: agy-executor
description: 'Use when a /plan artifact is approved (Proceed or [Approved] plan.md) in a non-Orchestrator session before editing files or spawning workers.'
---

# Antigravity Plan Executor

> **Gate Rule**: Editing files, picking default models, or spawning workers before the mode/model prompt completes violates this skill.

## 1. Ask Mode First

Ask **once** via `ask_question`:
- `(Recommended) Inline (current session)`
- `Swarm`

Do **not** call `swarm` before this step.

## 2. Execute

### If `Inline`
Implement, verify, and commit directly in the current session (never call `swarm`).

### If `Swarm`
1. Call `swarm{action:"models", all:true}` (`quota_remaining > 0%`).
2. Ask **once** via `ask_question` for **Worker Model**, proposing available **Hydrogen** (`gemini-4-hydrogen-*`), **3.8 Flash** (`gemini-3.8-flash-*`), and **Sonnet** (`claude-sonnet-*`) variants ordered **`low` -> `high`** (use other non-exhausted models only as fallback).
3. Keep the current session model as Coordinator (never switch Coordinator model).
4. Hand off execution (topology, `workspace`, `brief`, `kill`) to vanilla `/swarm` pinned to the chosen worker model with the approved plan artifact path, then review final diffs/commits on Coordinator.
