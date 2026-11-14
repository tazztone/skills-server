---
name: agy-retrospective
description: 'Audit session friction, issues, next steps, and takeaways; curate workspace SUGGESTIONS.md and propose minimal Repo Doc or AGENTS.md diffs via learning_proposal.md. Trigger after writing walkthrough.md, on /agy-retrospective, or on /learn.'
---

# Antigravity Retrospective

Audit the session into four concise sections, maintain `<workspace>/SUGGESTIONS.md` as a living backlog, and propose systemic documentation or `AGENTS.md` updates via an approval-gated artifact.

## 1. Audit & Triage Session

Inspect the session for:
- **Friction & Roadblocks**: Tool/command failures (non-zero exits, bad flags, path errors, loops), agent misunderstandings (hallucinations, wrong assumptions, missed paths), and user interventions (corrections, overrides, constraints).
- **Issues & Room for Improvement**: Bugs, rough edges, or tech debt noticed in the codebase (`file:line` context).
- **What's Next**: Concrete remaining tasks in priority order.
- **Triage takeaways (signal vs. noise)**: Discard ephemeral one-offs (network blips, typos, external outages, scratch experiments). Retain systemic findings (undocumented conventions, silent edge cases, non-obvious constraints, repeat preferences) and assign each to `SUGGESTIONS.md`, Repo Docs, or `AGENTS.md` / `GEMINI.md`.

Output all 4 sections concisely to the user (omit section 4 if nothing passes triage):
1. **Friction & Roadblocks** (root cause and pivotal resolution per item, or brief note if none)
2. **Issues & Room for Improvement**
3. **What's Next**
4. **Reusable Takeaways** (with target tier)

- **Completion criterion:** Every friction item, open issue, prioritized next step, and retained takeaway is accounted for in the output.

## 2. Curate `<workspace>/SUGGESTIONS.md`

Maintain `<workspace>/SUGGESTIONS.md` at the active project root directly via `edit_file` or `write_file`:

1. Read existing `<workspace>/SUGGESTIONS.md` if present.
2. Prune resolved items from `What's Next` and `Issues & Room for Improvement`; merge overlapping items; drop one-off noise.
3. Update under three curated headings (keep empty headings clean):
   ```markdown
   # Suggestions & Backlog

   ## What's Next
   - [Priority-ordered concrete remaining tasks]

   ## Issues & Room for Improvement
   - [Open bugs, rough edges, or tech debt with `file:line` context]

   ## Reusable Takeaways
   - [Durable workspace-level rules, gotchas, or patterns]
   ```

- **Completion criterion:** `<workspace>/SUGGESTIONS.md` reflects current open tasks, unresolved issues, and workspace takeaways with zero duplicates.

## 3. Propose Systemic Doc / `AGENTS.md` Updates

If no retained takeaways warrant promotion to Repo Docs or `AGENTS.md` / `GEMINI.md`, finish cleanly without creating an artifact.

### Routing & Minimalism Rules
- **Scope**: Route strictly to existing **Repo Docs / Specs / Runbooks** (preferred for local quirks, flags, domain context) or root **`AGENTS.md` / `GEMINI.md`** (universal invariants); leave skills, plugins, and MCP configs unchanged.
- **Update first**: Edit existing sections, docs, or numbered rules concisely before creating new files or rules.
- **Keep `AGENTS.md` minimal**: Read `skills/create-agentsmd/SKILL.md` (when available) and apply its **Three-Condition Filter**—include an instruction only if it is **uninferable**, **critical**, and **undocumented**; keep root `AGENTS.md` concise (<10 bullets, zero prose rationale, no standard commands).

### Artifact Proposal (Approval-Gated)
1. Leave Repo Docs and `AGENTS.md` / `GEMINI.md` untouched until the user explicitly approves.
2. Write `<appDataDir>/brain/<conversation-id>/learning_proposal.md` with `ArtifactMetadata` (`RequestFeedback: true`, `UserFacing: true`) containing:
   - Friction summary (what broke or required correction).
   - Target file(s) and routing rationale.
   - Exact unified diff blocks for every proposed edit.
3. Ask the user to review `learning_proposal.md` and wait for approval before applying edits.

- **Completion criterion:** Either exited cleanly with no doc/`AGENTS.md` candidates, or `learning_proposal.md` created with unified diffs while Repo Docs and `AGENTS.md` remain unedited pending approval.
