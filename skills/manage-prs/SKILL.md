---
name: manage-prs
description: >
  Triage, review, and merge GitHub PRs, including AI-generated PRs.
  Use for batch triage, single PR merge, PR queue cleanup, closing stale PRs,
  or when user mentions "manage PRs", "merge PR", "triage PRs", "PR backlog".
disable-model-invocation: true
---

# Manage PRs

Use `gh` for fetching PR metadata, diffs, and CI status. Use local `git` for checkout, rebase, conflict resolution, and merge — it is more reliable for hands-on work.

Default merge: `--squash --delete-branch`.
Stop and ask only on: auth errors (401/403), network timeouts, or irreversible cross-subsystem decisions.

## Principles

- **Read every diff before acting.** CI green is not sufficient — `gh pr diff <n>` and verify logic.
- **Decide autonomously.** You have the diff — decide and document why. Don't ask the user about content decisions.
- **Comment, don't close.** When a PR needs work, leave a specific actionable comment explaining what to fix — don't close it. The author (human or agent) can iterate in the existing PR. Only close PRs that are truly abandoned, superseded, or duplicate.
- **Resolve conflicts locally when the PR has value.** Investigate the diff. If worthwhile, checkout, rebase, resolve, force-push.
- **Verify at every gate.** Run lint, tests, and/or build checks after conflict resolution, after any local changes, and before merging. Don't merge without a green local verification.
- **Prefer local git over gh for branch manipulation.** `gh pr merge` for clean merges. For anything involving branches, rebases, or conflicts — use git directly.

## DO NOT

- Explore the repo (`ls`, `tree`) — irrelevant to PR management
- Ask the user to decide on PR content or confirm merge strategy
- Mark a PR "diff verified" without running `gh pr diff <n>`
- Re-fetch PR metadata when `prs.json` already has it
- Merge when mergeable is `UNKNOWN` — re-query up to 3× first
- Close a conflicting PR without first investigating if changes are worth keeping
- Close a PR when commenting with actionable feedback would suffice
- Merge without running at least a basic verification (lint, test, or build)

## Gotchas

See [REFERENCE.md](REFERENCE.md) for full details. Critical ones:

- **`UNKNOWN` mergeability**: re-query up to 3×, never merge `UNKNOWN`
- **`gh pr update-branch` doesn't exist**: use `gh api repos/{owner}/{repo}/pulls/{n}/update-branch`
- **`gh pr list` caps at 100**: always `--limit 100`, warn if hit
- **Comment before closing**: if you must close, `gh pr close <n> --comment "Reason"` — never silently
- **`--body-file` for `gh pr create`**: never inline `--body`

---

## Conflict Resolution

When a PR shows `CONFLICTING`:

1. **Investigate**: `gh pr diff <n>` — understand what the PR intended.
2. **Decide**: if superseded or truly abandoned — close with comment. If fixable by the author — comment with specific rebase instructions. If valuable and you can resolve — do it locally.
3. **Resolve locally**: checkout branch, `git rebase origin/<base>`, resolve using diff context, `git push --force-with-lease`.
4. **Verify locally**: run lint/tests/build on the resolved branch before pushing.
5. **Re-check**: verify mergeability after push, merge once clean.

See [REFERENCE.md](REFERENCE.md) for the full rebase script and abort criteria.

---

## Single-PR Workflow

1. **Health check**: `gh pr view <n> --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,body`
2. **Read diff**: `gh pr diff <n>` — verify logic. For bot/AI PRs, grep unfamiliar identifiers.
3. **Verify**: checkout the branch locally. Run lint, tests, or build as appropriate.
4. **Act**: clean → `gh pr merge <n> --squash --delete-branch` · conflicts → resolve locally · needs work → comment with specific feedback.

---

## Batch Triage Workflow

### Step 1: Gather and detect overlaps
```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files \
  --limit 100 | tee prs.json
```
Run overlap detection — see [REFERENCE.md](REFERENCE.md) for the script.

### Step 2–3: Diff evidence → triage
Fetch diffs with hash verification (see [REFERENCE.md](REFERENCE.md)), then classify. **Each merge-ready PR must include its `sha256:` hash.**
- ✅ **Merge-ready** — `MERGEABLE`, CI green, diff hash present
- 🔧 **Conflicts — resolvable** — worth keeping, resolve locally
- ⚠️ **Needs action** — blocked by CI or review
- 🔁 **Stale** — no activity >14 days
- 🔀 **Overlapping** — file conflict risk, merge order specified
- 💬 **Needs author action** — comment with specific feedback, leave open
- ❌ **Close candidates** — truly superseded, duplicate, or abandoned (not just needing work)

After writing the plan, execute:
1. Merge clean PRs (run local verification before each merge).
2. Resolve conflicts locally, verify, push, merge.
3. Comment on PRs that need author action.
4. Close only true rejects.
5. **Re-check at session end**: re-query PRs you commented on — authors often push fixes quickly. Merge any that are now clean.

---

## Cross-Skill Routing

| Situation | Hand off to |
|-----------|-------------|
| PR needs structured code review before merge | `review-pr` |
| PR has unresolved review threads to address | `resolve-pr-feedback` |
