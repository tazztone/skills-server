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
- **Resolve conflicts locally when the PR has value.** Investigate the diff. If worthwhile, checkout, rebase, resolve, force-push. Only close PRs whose changes are no longer relevant.
- **Prefer local git over gh for branch manipulation.** `gh pr merge` for clean merges. For anything involving branches, rebases, or conflicts — use git directly.

## DO NOT

- Explore the repo (`ls`, `tree`) — irrelevant to PR management
- Ask the user to decide on PR content or confirm merge strategy
- Mark a PR "diff verified" without running `gh pr diff <n>`
- Re-fetch PR metadata when `prs.json` already has it
- Merge when mergeable is `UNKNOWN` — re-query up to 3× first
- Close a conflicting PR without first investigating if changes are worth keeping

## Gotchas

See [REFERENCE.md](REFERENCE.md) for full details. Critical ones:

- **`UNKNOWN` mergeability**: re-query up to 3×, never merge `UNKNOWN`
- **`gh pr update-branch` doesn't exist**: use `gh api repos/{owner}/{repo}/pulls/{n}/update-branch`
- **`gh pr list` caps at 100**: always `--limit 100`, warn if hit
- **Always comment when closing**: `gh pr close <n> --comment "Reason"`
- **`--body-file` for `gh pr create`**: never inline `--body`

---

## Conflict Resolution

When a PR shows `CONFLICTING`:

1. **Investigate**: `gh pr diff <n>` — understand what the PR intended.
2. **Decide**: if superseded or irrelevant — close with comment. If valuable — resolve locally.
3. **Resolve locally**: checkout branch, `git rebase origin/<base>`, resolve using diff context, `git push --force-with-lease`.
4. **Verify**: re-check mergeability, merge once clean.

See [REFERENCE.md](REFERENCE.md) for the full rebase script and abort criteria.

---

## Single-PR Workflow

1. **Health check**: `gh pr view <n> --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,body`
2. **Read diff**: `gh pr diff <n>` — verify logic. For bot/AI PRs, grep unfamiliar identifiers.
3. **Act**: clean → `gh pr merge <n> --squash --delete-branch` · conflicts → resolve locally · reject → close with comment.

---

## Batch Triage Workflow

### Step 1: Gather and detect overlaps
```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files \
  --limit 100 | tee prs.json
```
Run overlap detection — see [REFERENCE.md](REFERENCE.md) for the script.

### Step 2: Collect diff evidence
Fetch diffs for every PR with hash verification — see [REFERENCE.md](REFERENCE.md) for the loop.

### Step 3: Triage report
Classify each PR. **Each merge-ready PR must include its `sha256:` hash.**
- ✅ **Merge-ready** — `MERGEABLE`, CI green, diff hash present
- 🔧 **Conflicts — resolvable** — worth keeping, resolve locally
- ⚠️ **Needs action** — blocked by CI or review
- 🔁 **Stale** — no activity >14 days
- 🔀 **Overlapping** — file conflict risk, merge order specified
- ❌ **Close candidates** — superseded, duplicate, abandoned

After writing the plan, execute. Merge clean PRs first, then resolve conflicts locally, then close rejects.

---

## Cross-Skill Routing

| Situation | Hand off to |
|-----------|-------------|
| PR needs structured code review before merge | `review-pr` |
| PR has unresolved review threads to address | `resolve-pr-feedback` |
