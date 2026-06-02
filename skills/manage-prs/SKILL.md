---
name: manage-prs
description: >
  Triage, review, and merge GitHub PRs, including AI-generated PRs.
  Use for batch triage, single PR merge, PR queue cleanup, closing stale PRs,
  or when user mentions "manage PRs", "merge PR", "triage PRs", "PR backlog".
disable-model-invocation: true
---

# Manage PRs

Use `gh` for all operations. Stop and ask the user on: 401, 403, 422, or network timeout.
Default merge method: `--squash --delete-branch`. Check `AGENTS.md` first — it overrides merge defaults.

**Before running any `gh` command**, read [REFERENCE.md](REFERENCE.md) for critical gotchas that cause silent failures.

---

## Single-PR Workflow

Use when the user names a specific PR (e.g. "merge PR #42", "close PR #7").

### Step 1: Health check
```bash
gh pr view <n> --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,body
```
Evaluate: mergeable (`MERGEABLE` required — see REFERENCE.md), CI green, review decision, draft status.

### Step 2: Read the diff
```bash
gh pr diff <n>
```
CI green is not sufficient. Verify logic, imports, and API usage. For bot/AI PRs, grep unfamiliar identifiers in the codebase.

### Step 3: Act
- **Merge**: `gh pr merge <n> --squash --delete-branch`
- **Close**: `gh pr close <n> --comment "Closing because..."` — never close silently
- **Request changes**: comment with findings, or hand off to `review-pr` skill for structured review

---

## Batch Triage Workflow

Use when managing multiple PRs (e.g. "triage PRs", "clean up PR queue").

### Step 1: Gather
```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files \
  --limit 100 > prs.json
```
Also read `AGENTS.md` for merge method overrides. If 100 PRs returned, warn user — triage is incomplete.

### Step 2: Detect overlaps
Run the overlap script from REFERENCE.md against `prs.json`. Overlapping PRs need sequenced merging.

### Step 3: Batch by theme
Group PRs into batches of 4–6:
- Dependency bumps / automated (Dependabot, Jules, Renovate)
- Feature additions / bug fixes
- Refactors / style
- Structural / config / cache (high-risk — see REFERENCE.md)

### Step 4: Per-PR health check
For each PR, evaluate:
1. **Mergeability** — `MERGEABLE` required (see REFERENCE.md for `UNKNOWN` handling)
2. **CI status** — all checks green?
3. **Review readiness** — `reviewDecision` approved?
4. **Staleness** — no activity > 14 days? Ping author or close
5. **Diff read** — `gh pr diff <n>`: logic correct?
6. **Bot/AI PRs** — grep unfamiliar identifiers if automated author

### Step 5: Triage report
Present grouped results to user:
- ✅ **Merge-ready** — CI green, diff verified, reviewed, no conflicts
- ⚠️ **Needs action** — blocked by conflict / CI failure / missing review
- 🔁 **Stale** — no activity > threshold
- 🔀 **Overlapping** — file conflict risk; list affected files
- 🤖 **Bot/AI** — needs import/API verification
- ❌ **Close candidates** — superseded, duplicate, or abandoned

Walk through each PR for merge / comment / close decision.

---

## Cross-Skill Routing

| Situation | Hand off to |
|-----------|-------------|
| PR needs structured multi-perspective code review | `review-pr` |
| PR has unresolved review threads to address | `resolve-pr-feedback` |
| User wants to create a new PR | Use `--body-file` pattern (see REFERENCE.md) |
