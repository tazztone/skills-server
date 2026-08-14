---
name: manage-prs
description: Triage, review, rebase, and merge GitHub PRs.
disable-model-invocation: true
---

# Manage PRs

Use `gh` for GitHub API operations (`list`, `diff`, `view`, `merge`, `comment`, `close`).
Use `git` for local repository operations (`fetch`, `checkout`, `rebase`, `push`). Never mix.

Default merge: `gh pr merge <n> --squash --delete-branch`.
Stop and ask only on auth errors (401/403), network timeouts, or irreversible cross-subsystem decisions.

## Principles

- **Diffs-only until planned**: Work strictly from `pr-<n>.diff` during triage. Inspect diffs before acting; CI green alone is never sufficient.
- **Autonomous decision-making**: Decide merges, feedback, and closures from diff inspection and primary sources; document rationales without querying the user for content choices.
- **Comment over close**: Leave specific, actionable feedback on PRs needing work. Reserve closure strictly for superseded, duplicate, or abandoned PRs.
- **Clean verification**: Skip test runs on clean CI-green branches during triage (verify once on final `main`). For locally rebased conflict branches, verify before force-pushing. See [REFERENCE.md](REFERENCE.md) for heuristics.

Read [REFERENCE.md](REFERENCE.md) for command loops, conflict rebase flows, overlap scripts, and API gotchas (`UNKNOWN` mergeability retries, GraphQL race handling, `GIT_EDITOR=true` rebase bypass).

---

## Single-PR Workflow

1. **Health check**: `gh pr view <n> --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,body`
2. **Read diff**: `gh pr diff <n>` — inspect logic. For bot/AI PRs, grep unfamiliar identifiers in the codebase.
3. **Act**:
   - *Clean & CI green* → `gh pr merge <n> --squash --delete-branch`
   - *Conflicting* → Follow [Conflict Resolution](#conflict-resolution) branch.
   - *Needs work* → `gh pr comment <n> --body "..."` with actionable feedback.
   - *Abandoned / duplicate* → `gh pr close <n> --comment "..."`
4. **Verify & Clean** (if modified locally): Run repo verification checks before pushing. Delete local branch (`git branch -D pr-<n>`).

✅ **Single-PR done when:** PR outcome is executed (merged, commented, or closed), local tracking branches are deleted, and verified on target branch if changes were made.

---

## Batch Triage Workflow

### Phase 1 — Collect (diffs-only, no analysis)

1. Fetch PR metadata:

   ```bash
   gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,headRefName,headRepositoryOwner,files,updatedAt \
     --limit 100 | tee prs.json
   ```

2. Collect all diffs via diff collection loop in [REFERENCE.md](REFERENCE.md).
3. Run overlap detection script from [REFERENCE.md](REFERENCE.md).

✅ **Phase 1 done when:** `prs.json` exists, a `pr-<n>.diff` exists for every PR in it, and the file overlap report has been generated.

### Phase 2 — Plan (produce merge plan)

1. Read all `pr-<n>.diff` files and overlap output. Classify every PR into triage categories. For overlapping pairs, annotate merge sequence order (e.g. "merge #92 before #94").
2. Write the result as an `implementation_plan.md` artifact using the merge plan template from [REFERENCE.md](REFERENCE.md). Request user feedback on the artifact.

✅ **Phase 2 done when:** Every PR in `prs.json` appears exactly once in the plan, all overlapping pairs have an explicit merge order, and the plan is written as an artifact awaiting user approval.

**Stop after writing the merge plan artifact. Do not proceed to Phase 3 until the user approves.**

**Triage categories:**

- ✅ **Merge-ready** — `MERGEABLE`, CI green
- 🔧 **Conflicts — resolvable** — worth keeping, resolve locally
- ⚠️ **Needs action** — blocked by CI or review
- 🔁 **Stale** — no activity >14 days
- 💬 **Needs author action** — comment with specific feedback, leave open
- ❌ **Close candidates** — truly superseded, duplicate, or abandoned (not just needing work)

Overlapping PRs are annotated within their category row (e.g. "✅ overlaps #94 — merge first"), not given a separate category.

### Phase 3 — Execute (one category at a time, requires user approval)

1. **✅ Merge-ready**: `gh pr merge <n> --squash --delete-branch` for each. Log: `"Merged: #X, #Y"`
2. **🔧 Conflicts**: Follow [Conflict Resolution](#conflict-resolution) for each. Log: `"Resolved: #X"`
3. **💬 / ⚠️**: `gh pr comment <n> --body "..."` with actionable feedback. Log: `"Commented: #X, #Y"`
4. **❌**: `gh pr close <n> --comment "..."`. Log: `"Closed: #X"`

✅ **Phase 3 done when:** Every PR in the plan has an executed and logged outcome.

### Phase 4 — Verify & Cleanup

1. Run repo verification commands once on final `main`. See [REFERENCE.md](REFERENCE.md) for heuristic.
2. **If verification fails**: Check whether the failure is pre-existing on `main` or caused by merged changes. Pre-existing → document and proceed. Merge regression → isolate offending PR, revert if necessary, and report.
3. Clean up workspace artifacts and temp branches using the cleanup commands in [REFERENCE.md](REFERENCE.md).

✅ **Phase 4 done when:** Verification passes (or pre-existing failures are documented) and all workspace artifacts (`prs.json`, `pr-*.diff`, temp `pr-*` branches) are removed.

---

## Conflict Resolution

Authoritative branch for PRs showing `CONFLICTING`:

1. **Investigate primary sources**: Inspect `pr-<n>.diff` and PR body for author intent. Inspect git history of conflicting base files (`git log -n 5 --oneline origin/<base> -- <file>`) for base branch intent.
2. **Select resolution strategy**:
   - *Superseded / abandoned* → Close with explanation.
   - *Complex cross-cutting (5+ files or domain refactor)* → Comment with rebase guidance and abort criteria from [REFERENCE.md](REFERENCE.md).
   - *Valuable & resolvable* → Resolve hunk-by-hunk. Preserve both intents where orthogonal. On direct collision, pick the change matching the PR's stated goal and note the trade-off. Zero invented behaviour.
3. **Rebase & verify**: Fetch branch manually (`git fetch origin pull/<n>/head:pr-<n>`), checkout `pr-<n>`, and rebase onto `origin/<base>`. Resolve each hunk, stage, and continue with `GIT_EDITOR=true git rebase --continue`. Run local checks before pushing.
4. **Push & merge**: Push back (`git push --force-with-lease`), re-query mergeability until `MERGEABLE`, then merge. For fork PRs, see [REFERENCE.md](REFERENCE.md) for pushback syntax.

---

## Cross-Skill Routing

| Situation | Hand off to |
|-----------|-------------|
| PR needs structured code review before merge | `review-pr` |
| PR has unresolved review threads to address | `resolve-pr-feedback` |
