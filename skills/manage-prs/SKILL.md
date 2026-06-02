---
name: manage-prs
description: Triage, review, and merge GitHub PRs, including AI-generated PRs. Use for batch triage or single PR merges.
disable-model-invocation: true
---

# Manage PRs

Use `gh` for all operations. Stop and ask the user on: 401, 403, 422, or network timeout.
Default merge method: `--squash --delete-branch`. Check `AGENTS.md` first — it overrides all merge method defaults.

## Gotchas & Landmines

### `--json comments` crashes `gh pr view`
Use `--json body,comments` — **not** the `--comments` flag. The flag crashes.

### `UNKNOWN` mergeability is a hard block
GitHub computes mergeability asynchronously and temporarily returns `UNKNOWN`. **Never merge `UNKNOWN`.** Re-query with `gh pr view <n> --json mergeable` until it resolves to `MERGEABLE` before proceeding.

### `BEHIND` must be updated before merge
A PR with `BEHIND` mergeability will produce a messy history or fail. Always run `gh pr update-branch <n>` first.
Fallback if that fails: `gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase`

### Script path is runtime-dynamic
Do not assume a fixed install path for `pr-overlap.py`. Discover it at runtime:
```bash
python3 $(find ~ -name pr-overlap.py -maxdepth 8 2>/dev/null | head -1) prs.json
```
Fallback one-liner if the script is missing:
```bash
python3 -c "import json, collections; data = json.load(open('prs.json')); by_file = collections.defaultdict(list); [(by_file[f['path']].append(pr['number']) for f in pr.get('files', []) if isinstance(f, dict) and 'path' in f) for pr in data if 'number' in pr]; [print(f'{p}: {ns}') for p, ns in sorted(by_file.items(), key=lambda x: -len(x[1])) if len(ns) > 1]"
```

### `gh pr list` silently caps at 100
Add `--limit 100` explicitly. If the repo has more open PRs, warn the user — triage will be incomplete.

### Never merge without reading the diff
Do not bucket a PR as Merge-ready based on CI status alone. Always run `gh pr diff <n>` and verify the logic.

### Bot/AI PRs: verify imports and APIs
For automated PRs (e.g. Jules), `grep` any unfamiliar identifiers in the codebase before approving. Do not trust the description.

### Always comment when closing
`gh pr close <n> --comment "Closing because..."` — never close silently.

## Overlap detection
`gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100 > prs.json`
Then run the overlap script (see path discovery above).

## Additional resources
- [scripts/pr-overlap.py](scripts/pr-overlap.py)
