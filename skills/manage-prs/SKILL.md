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
Default merge: `--squash --delete-branch`. Check `AGENTS.md` if it exists — it overrides merge defaults.

## DO NOT

- Explore the repo (`ls`, `tree`, `git branch`, check directories) — irrelevant to PR management
- Do exploratory research before triaging — go straight to gathering PRs
- Ask the user "which approach" — determine workflow from context, then execute it
- Skip reading diffs — CI green alone is NOT sufficient
- Merge when mergeable is `UNKNOWN` — re-query until it resolves (see gotchas below)

---

## Gotchas

**`UNKNOWN` mergeability is a hard block.** GitHub computes this async. Re-query up to 3×:
`gh pr view <n> --json mergeable` — wait a few seconds between. Never merge `UNKNOWN`.

**`--json comments` crashes `gh pr view`.** Use `--json body,comments` — not the `--comments` flag.

**`gh pr update-branch` does not exist.** Use the API instead:
`gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=squash`

**`gh pr list` silently caps at 100.** Always use `--limit 100`. Warn user if count hits 100.

**Always comment when closing.** `gh pr close <n> --comment "Closing because..."` — never silently.

**`gh pr create` body must use `--body-file`.** Write body to a tmpfile, pass `--body-file`. Never inline `--body`.

---

## Single-PR Workflow

Use when the user names a specific PR (e.g. "merge PR #42", "close PR #7").

1. **Health check**: `gh pr view <n> --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,body`
   — Verify mergeable is `MERGEABLE`. If `UNKNOWN`, re-query up to 3×.
2. **Read diff**: `gh pr diff <n>` — verify logic, imports, API usage. For bot/AI PRs, grep unfamiliar identifiers.
3. **Act**: merge (`gh pr merge <n> --squash --delete-branch`), close with comment, or hand off to `review-pr`.

---

## Batch Triage Workflow

Use when managing multiple PRs (e.g. "triage PRs", "clean up PR queue").

### Step 1: Gather
```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files \
  --limit 100 > prs.json
```
The `files` field is required for overlap detection. Also read `AGENTS.md` for merge overrides if it exists.

### Step 2: Detect overlaps
```bash
python3 -c "
import json, collections
data = json.load(open('prs.json'))
by_file = collections.defaultdict(list)
for pr in data:
    for f in pr.get('files', []):
        if isinstance(f, dict) and 'path' in f:
            by_file[f['path']].append(pr['number'])
for p, ns in sorted(by_file.items(), key=lambda x: -len(x[1])):
    if len(ns) > 1: print(f'{p}: {ns}')
"
```
Overlapping PRs need sequenced merging — merge the simpler one first, re-check conflicts on the other.

### Step 3: Per-PR health check
For each PR:
1. **Mergeability** — must be `MERGEABLE`. Re-query `UNKNOWN` up to 3×, skip `CONFLICTING`.
2. **CI** — all status checks green?
3. **Review** — `reviewDecision` approved? (skip if repo doesn't require reviews)
4. **Staleness** — no activity >14 days? Recommend ping or close.
5. **Diff** — `gh pr diff <n>`: logic correct, no obvious breakage?
6. **Bot/AI** — if automated author, grep unfamiliar identifiers in the codebase.

### Step 4: Triage report
Write results to a plan file. Group PRs into:
- ✅ **Merge-ready** — CI green, diff verified, no conflicts
- ⚠️ **Needs action** — blocked by conflict / CI / review
- 🔁 **Stale** — no activity > threshold
- 🔀 **Overlapping** — file conflict risk with affected files listed
- ❌ **Close candidates** — superseded, duplicate, or abandoned

Then walk through each PR one-by-one for merge / comment / close decision.

---

## Cross-Skill Routing

| Situation | Hand off to |
|-----------|-------------|
| PR needs structured code review before merge | `review-pr` |
| PR has unresolved review threads to address | `resolve-pr-feedback` |
