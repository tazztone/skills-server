---
name: agy-retrospective
description: 'Summarize session friction, remaining issues, next steps, and reusable knowledge, then curate findings into workspace SUGGESTIONS.md. Trigger after writing walkthrough.md or on /agy-retrospective.'
---

# Antigravity Retrospective

Audit the session into four concise sections and curate durable findings into `<workspace>/SUGGESTIONS.md` without bloat or duplicates.

## 1. Output 4-Section Session Audit

Output directly to the user:

1. **Friction & Roadblocks:** Root causes of tool errors, wrong assumptions, or wasted turns.
2. **Issues & Room for Improvement:** Bugs, rough edges, or tech debt noticed in the codebase during this session.
3. **What's Next:** Concrete remaining tasks in priority order.
4. **Reusable Takeaways:** Only rules, gotchas, or patterns worth saving to `SUGGESTIONS.md` so they don't repeat. Omit if nothing meets that bar.

- **Completion criterion:** All 4 sections (or 1–3 if section 4 is empty) are output concisely to the user.

## 2. Curate `<workspace>/SUGGESTIONS.md`

Maintain `<workspace>/SUGGESTIONS.md` (at the active project/repository root) as a short, deduplicated living document rather than an append-only log:

1. **Read existing state**: Read `<workspace>/SUGGESTIONS.md` if it exists.
2. **Prune & deduplicate**:
   - Remove items under `What's Next` or `Issues & Room for Improvement` that were resolved during this session.
   - Merge overlapping items instead of adding duplicate bullets.
   - Keep only high-signal, actionable entries; drop one-off noise.
3. **Update sections**: Organize `<workspace>/SUGGESTIONS.md` under three curated headings:
   ```markdown
   # Suggestions & Backlog

   ## What's Next
   - [Priority-ordered concrete remaining tasks]

   ## Issues & Room for Improvement
   - [Open bugs, rough edges, or tech debt with `file:line` context]

   ## Reusable Takeaways
   - [Durable rules, gotchas, or patterns]
   ```
4. **Write file**: Update `<workspace>/SUGGESTIONS.md` via `edit_file` or `write_file`. (If no open items or takeaways remain, keep the headings clean).

- **Completion criterion:** `<workspace>/SUGGESTIONS.md` reflects current unresolved tasks, open issues, and reusable takeaways with resolved items pruned and zero duplicate entries.
