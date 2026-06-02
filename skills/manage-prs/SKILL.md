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
- Ask the user to confirm or choose a merge strategy — write the plan, then execute it
- Mark a PR "diff verified" without running `gh pr diff <n>` — read every diff before classifying
- Re-fetch individual PR metadata via `gh pr view` when `prs.json` already has the data
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

**"Base branch was modified" on merge.** Each merge changes the base branch, so the next merge may fail.
Merge PRs one at a time. On this error, simply retry the same merge command.

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

### Step 1: Gather and detect overlaps
```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files \
  --limit 100 | tee prs.json | python3 -c "
import json, sys, collections
data = json.load(sys.stdin)
by_file = collections.defaultdict(list)
for pr in data:
    for f in pr.get('files', []):
        if isinstance(f, dict) and 'path' in f:
            by_file[f['path']].append(pr['number'])
overlaps = [(p, ns) for p, ns in by_file.items() if len(ns) > 1]
if overlaps:
    print('OVERLAPPING FILES:')
    for p, ns in sorted(overlaps, key=lambda x: -len(x[1])):
        print(f'  {p}: PRs {ns}')
else:
    print('No file overlaps detected.')
"
```
This saves `prs.json` AND pipes to overlap detection in one shot.
Overlapping PRs need sequenced merging — merge the simpler one first, re-check conflicts on the other.
Also read `AGENTS.md` for merge overrides if it exists.

### Step 2: Collect diff evidence
Run this for every PR. It fetches diffs, hashes them, and extracts a preview — producing verifiable evidence:
```bash
for n in $(jq -r '.[].number' prs.json); do
  DIFF=$(gh pr diff "$n" 2>&1)
  HASH=$(printf '%s' "$DIFF" | sha256sum | cut -d' ' -f1)
  ADDS=$(printf '%s' "$DIFF" | grep -c '^+[^+]' 2>/dev/null || echo 0)
  DELS=$(printf '%s' "$DIFF" | grep -c '^-[^-]' 2>/dev/null || echo 0)
  FILES=$(printf '%s' "$DIFF" | grep -c '^diff --git' 2>/dev/null || echo 0)
  echo "=== PR #${n} | sha256:${HASH:0:16} | +${ADDS}/-${DELS} | ${FILES} files ==="
  printf '%s' "$DIFF" | grep '^[+-][^+-]' | head -5
  echo ""
done
```
Each PR gets: a truncated SHA-256 hash (proof the diff was fetched), change stats, and a 5-line code preview.
Review the preview lines for correctness. For bot/AI PRs, grep unfamiliar identifiers in the codebase.

### Step 3: Triage report
Use data from `prs.json` (mergeability, CI, review) plus the diff evidence from Step 2.
Write results to a plan file. **Each merge-ready PR must include its `sha256:` hash from Step 2.**
- ✅ **Merge-ready** — `MERGEABLE`, CI green, diff evidence hash present
- ⚠️ **Needs action** — blocked by conflict / CI / review
- 🔁 **Stale** — no activity >14 days
- 🔀 **Overlapping** — file conflict risk with merge order specified
- ❌ **Close candidates** — superseded, duplicate, or abandoned

After writing the plan, proceed to merge — do not stop and ask for confirmation.

---

## Cross-Skill Routing

| Situation | Hand off to |
|-----------|-------------|
| PR needs structured code review before merge | `review-pr` |
| PR has unresolved review threads to address | `resolve-pr-feedback` |
