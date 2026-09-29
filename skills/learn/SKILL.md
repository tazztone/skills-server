---
name: learn
description: Audit session friction and persist systemic takeaways to repo docs or AGENTS.md
disable-model-invocation: true
---

# Learn

Start from session roadblocks, filter out the noise, and bundle retained takeaways into a single structured proposal artifact.

## Scope Constraint

- **Do NOT create new skills, plugins, or MCP configs.**
- Learnings are strictly routed to existing **repository documentation** or the project's **`AGENTS.md`** guardrails.

## 1. Audit Friction

1. **Tool and command failures**: Non-zero exits, bad flags, path errors, excessive loops.
2. **Agent misunderstandings**: Hallucinations, wrong assumptions, missed file locations.
3. **User interventions**: Explicit corrections, overrides, or constraints ("no", "instead", "failed").
- *Completion criterion*: A friction list citing the root cause and pivotal resolution per item, or a 2-sentence note stating why nothing needs saving.

## 2. Triage Signal vs. Noise

- **Discard ephemeral**: One-off network blips, typos, external API outages, scratch experiments.
- **Retain systemic**: Undocumented conventions, silent edge cases, non-obvious constraints, repeat preferences.
- *Completion criterion*: Every friction point tagged discard or retain. If all are discarded, terminate cleanly.

## 3. Route to Least Intrusive Destination

Route each retained takeaway strictly to:
1. **Repo Docs / Specs / Runbooks** (Preferred for gotchas): Put local quirks, tool flag tricks, or domain context directly where the code or docs live.
2. **Root `AGENTS.md` / `GEMINI.md`** (For universal guardrails): For project-wide rules and invariants that every agent must know (see `create-agentsmd` skill).

## 4. Update First (Anti-Bloat)

- Always edit existing sections, docs, or numbered rules before creating new files or adding new rules.
- Keep additions concise, actionable, and minimal.

## 5. Propose via Artifact (No Edits Before Approval)

1. Do NOT edit any repository files immediately.
2. Create `learning_proposal.md` in the artifact directory (`<appDataDir>/brain/<conversation-id>/learning_proposal.md`) with `ArtifactMetadata` setting `RequestFeedback: true` and `UserFacing: true`.
3. In the artifact, provide:
   - Friction summary (what broke / what was corrected).
   - Target file(s) and rationale.
   - Exact unified diff blocks showing the proposed changes.
4. Notify the user to review the proposal and wait for explicit approval before modifying any files.
