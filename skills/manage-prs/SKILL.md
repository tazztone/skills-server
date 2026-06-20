---
name: manage-prs
description: >
  Triage, review, and merge GitHub PRs, including AI-generated PRs.
  Use for batch triage, single PR merge, PR queue cleanup, closing stale PRs,
  or when user mentions "manage PRs", "merge PR", "triage PRs", "PR backlog".
disable-model-invocation: true
---

# Manage PRs

Use `gh` for GitHub API operations: `pr list`, `pr diff`, `pr view`, `pr merge`, `pr comment`, `pr close`.
Use `git` for all local work: fetch, checkout, rebase, push. Never mix.

Default merge: `--squash --delete-branch`.
Stop and ask only on: auth errors (401/403), network timeouts, or irreversible cross-subsystem decisions.

## Principles

- **Diffs-only until the plan is written.** Read every diff before acting. CI green is not sufficient. During batch triage, never open source files — work from `pr-<n>.diff` only.
- **Autonomous.** Decide from the diff; document why. Don't ask the user about content decisions or merge strategy.
- **Comment, don't close.** Leave specific actionable feedback and keep the PR open. Only close PRs that are truly abandoned, superseded, or duplicate.
- **Verify once at the end.** Never run tests mid-triage or on individual PR branches. After all merges and conflict resolutions are complete, run the repo's verification commands once on final main. See [REFERENCE.md](REFERENCE.md) for the detection heuristic.

## DO NOT

- Explore the repo (`ls`, `tree`) — irrelevant to PR management
- Ask the user to decide on PR content or confirm merge strategy
- Mark a PR "diff verified" without running `gh pr diff <n>`
- Re-fetch PR metadata when `prs.json` already has it
- Merge when mergeable is `UNKNOWN` — re-query up to 3× first
- Use `gh pr checkout` — it segfaults on some environments; use `git fetch origin pull/<n>/head:pr-<n>` instead
- Read source files during batch triage — diffs-only until the plan is written
- Run tests on individual PR branches — verify once on final main
- Leave workspace artifacts — delete `prs.json`, `pr-*.diff`, and temp branches at session end

## Gotchas

Read [REFERENCE.md](REFERENCE.md) before your first `gh` command. Critical ones:

- **`UNKNOWN` mergeability**: re-query up to 3×, never merge `UNKNOWN`
- **`gh pr update-branch` doesn't exist**: use `gh api repos/{owner}/{repo}/pulls/{n}/update-branch`
- **`gh pr list` caps at 100**: always `--limit 100`, warn if hit
- **Comment before closing**: if you must close, `gh pr close <n> --comment "Reason"` — never silently
- **`--body-file` for `gh pr create`**: never inline `--body`
- **`gh pr checkout` panics**: never use it — see REFERENCE.md for the safe alternative

---

## Conflict Resolution

This is the authoritative description of the conflict resolution flow. Both single-PR and batch workflows reference this section — they do not restate it.

When a PR shows `CONFLICTING`:

1. **Investigate**: read `pr-<n>.diff` (batch) or `gh pr diff <n>` (single) — understand what the PR intended.
2. **Decide**: if superseded or truly abandoned → close with comment. If fixable by the author → comment with specific rebase instructions. If valuable and resolvable → do it locally.
3. **Resolve locally**: `git fetch origin pull/<n>/head:pr-<n>`, checkout, `git rebase origin/<base>`, resolve using diff context, push. For fork PRs, see [REFERENCE.md](REFERENCE.md) for pushback instructions.
4. **Re-check**: verify mergeability after push, merge once clean.

Verification happens at the end (Phase 4), not here.

Read [REFERENCE.md](REFERENCE.md) for the full rebase script, abort criteria, and fork PR pushback commands.

---

## Single-PR Workflow

1. **Health check**: `gh pr view <n> --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,body`
2. **Read diff**: `gh pr diff <n>` — verify logic. For bot/AI PRs, grep unfamiliar identifiers in the codebase.
3. **Act**: clean → `gh pr merge <n> --squash --delete-branch` · conflicts → follow Conflict Resolution section · needs work → comment with specific feedback.
4. **Verify** (if you resolved conflicts or made local changes): detect and run the repo's verification commands before pushing. See [REFERENCE.md](REFERENCE.md) for heuristic. Skip for clean CI-green PRs.

---

## Batch Triage Workflow

### Phase 1 — Collect (diffs-only, no analysis)

1. Fetch PR list:
   ```bash
   gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files,updatedAt \
     --limit 100 | tee prs.json
   ```
2. Collect all diffs — read [REFERENCE.md](REFERENCE.md) for the diff collection loop.
3. Detect overlaps — read [REFERENCE.md](REFERENCE.md) for the overlap detection command.

✅ **Phase 1 done when:** `prs.json` exists AND a `pr-<n>.diff` file exists for every PR number in it.

### Phase 2 — Plan (produce merge plan)

4. Read all `pr-<n>.diff` files and overlap output. Classify every PR using the categories below. For overlapping pairs, annotate with merge order (e.g. "merge #92 before #94"). Write the result as an `implementation_plan.md` artifact using the merge plan template from [REFERENCE.md](REFERENCE.md). Request user feedback on the artifact.

✅ **Phase 2 done when:** every PR from `prs.json` appears exactly once in the plan, all overlapping pairs have an explicit merge order, and the plan is written as an artifact awaiting user approval.

**Stop after writing the merge plan artifact. Do not proceed to Phase 3 until the user approves.**

**Triage categories:**
- ✅ **Merge-ready** — `MERGEABLE`, CI green
- 🔧 **Conflicts — resolvable** — worth keeping, resolve locally
- ⚠️ **Needs action** — blocked by CI or review
- 🔁 **Stale** — no activity >14 days
- 💬 **Needs author action** — comment with specific feedback, leave open
- ❌ **Close candidates** — truly superseded, duplicate, or abandoned (not just needing work)

Overlapping PRs are annotated within their category (e.g. "✅ overlaps #94 — merge first"), not given a separate category.

### Phase 3 — Execute (one category at a time, requires user approval)


5. **✅ Merge-ready**: `gh pr merge <n> --squash --delete-branch` for each. Log: `"Merged: #X, #Y"`
6. **🔧 Conflicts**: follow Conflict Resolution section for each. Log: `"Resolved: #X"`
7. **💬 / ⚠️**: comment on each with actionable feedback. Log: `"Commented: #X, #Y"`
8. **❌**: close with comment. Log: `"Closed: #X"`

✅ **Phase 3 done when:** every PR in the table has a logged outcome.

### Phase 4 — Verify & Cleanup

9. Run repo verification commands once on final main. See [REFERENCE.md](REFERENCE.md) for heuristic.
10. **If verification fails**: check if the failure is pre-existing (exists on main before your merges) or caused by your changes. Pre-existing → note it and proceed. Caused by your changes → investigate which merge introduced it, revert if needed, and report.
11. Clean up: read [REFERENCE.md](REFERENCE.md) for the cleanup commands.

✅ **Phase 4 done when:** verification passes (or pre-existing failures documented) and no workspace artifacts remain (`prs.json`, `pr-*.diff`, temp branches all deleted).

---

## Cross-Skill Routing

| Situation | Hand off to |
|-----------|-------------|
| PR needs structured code review before merge | `review-pr` |
| PR has unresolved review threads to address | `resolve-pr-feedback` |
