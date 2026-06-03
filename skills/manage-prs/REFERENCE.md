# Manage PRs — Reference

Gotchas, command patterns, conflict resolution details, and the overlap detection script.

---

## Gotchas & Landmines

### `UNKNOWN` mergeability is a hard block
GitHub computes mergeability asynchronously and temporarily returns `UNKNOWN`. **Never merge `UNKNOWN`.**
Re-query until it resolves:
```bash
gh pr view <n> --json mergeable
```
Retry up to 3 times with a few seconds between. If still `UNKNOWN`, report to the user.

### `--json comments` crashes `gh pr view`
Use `--json body,comments` — **not** the `--comments` flag. The flag crashes.

### `gh pr update-branch` does not exist
The native command will fail. Use the raw API:
```bash
gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=squash
```
Fallback if squash fails:
```bash
gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase
```

### `gh pr create` body must use `--body-file`
Never pipe PR body via stdin or inline `--body`. Write to a temp file:
```bash
BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/pr-body.XXXXXX")
cat > "$BODY_FILE" <<'__END__'
<body content here>
__END__
gh pr create --title "<TITLE>" --body-file "$BODY_FILE"
```

### `gh pr list` silently caps at 100
Always pass `--limit 100`. If the count hits 100, warn the user — triage will be incomplete.

### Structural/cache-layer PRs are systemic blockers
PRs altering service workers (`sw.js`), architectural caching, or app-layer config have cascading side effects.
Group these, isolate the ideal structural layout first, and reject/close alternates — don't chain-merge blindly.

### Never merge without reading the diff
CI green is not sufficient. Always run `gh pr diff <n>` and verify the logic.

### Bot/AI PRs: verify imports and APIs
For automated PRs (e.g. Jules, Dependabot), `grep` any unfamiliar identifiers in the codebase before approving.
Do not trust the PR description alone.

### Prefer commenting over closing
When a PR needs work, comment with specific actionable feedback and leave it open — the author can iterate in place. Only close PRs that are truly abandoned, superseded, or duplicate. If you must close: `gh pr close <n> --comment "Closing because..."` — never silently.

### Avoid sequential multi-query bloat
Do not re-fetch `gh pr list` after every merge.
Group non-overlapping merge-ready PRs into a batch queue, execute sequentially, sync at the end.

---

## Local Conflict Resolution — Details

When the diff investigation shows a PR's changes are worth preserving, resolve locally:

### Standard rebase flow
```bash
# fetch latest state
git fetch origin

# checkout the PR branch
git checkout -b pr-<n>-rebase origin/<pr-branch-name>

# rebase onto target
git rebase origin/<base-branch>

# resolve each conflict using your diff investigation context
# — you know what the author intended, honour that intent
git add <resolved-files>
git rebase --continue

# verify the resolved state before pushing
# run whatever is appropriate: lint, tests, build
npm run lint 2>&1 || true
npm test 2>&1 || true

# push the resolved branch back
git push --force-with-lease origin <pr-branch-name>

# clean up local branch
git checkout <base-branch>
git branch -D pr-<n>-rebase
```

### When to abort local resolution
- Conflict spans 5+ files with unrelated cross-cutting changes — comment with analysis, leave open for author.
- PR's changes are superseded by a newer PR or direct commit — close with explanation.
- Rebase produces a state where lint/tests clearly fail (missing deps, removed APIs) — comment with what broke and why, leave open.

### After resolution
1. Verify locally: run lint, tests, and/or build. Fix anything the resolution broke.
2. Push: `git push --force-with-lease origin <pr-branch-name>`
3. Re-check mergeability: `gh pr view <n> --json mergeable`
4. Once `MERGEABLE`, merge: `gh pr merge <n> --squash --delete-branch`

---

## Overlap Detection

After gathering PRs to `prs.json`, detect file overlaps to sequence merges safely.

Write the following script to a temp file and run it:

```bash
OVERLAP_SCRIPT=$(mktemp "${TMPDIR:-/tmp}/pr-overlap.XXXXXX.py")
cat > "$OVERLAP_SCRIPT" <<'PYEOF'
#!/usr/bin/env python3
"""Find file overlaps and duplicate subsets among PRs grouped by baseRefName."""
import json, sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: pr-overlap.py <prs.json>", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text())
    except Exception as e:
        print(f"Error reading JSON: {e}", file=sys.stderr)
        return 1
    if not isinstance(data, list):
        print("Invalid input: expected a JSON list of PRs.", file=sys.stderr)
        return 1

    by_base = defaultdict(list)
    for pr in data:
        if "number" not in pr:
            continue
        by_base[pr.get("baseRefName", "unknown")].append(pr)

    for base, prs in by_base.items():
        if len(prs) < 2:
            continue
        print(f"=== Target Branch: {base} ===")
        pr_files = {}
        titles = {}

        for pr in prs:
            num = pr["number"]
            titles[num] = pr.get("title", "")
            files = pr.get("files", [])
            if not files:
                print(f"  Warning: PR #{num} has no files.", file=sys.stderr)
            pr_files[num] = {f["path"] for f in files if isinstance(f, dict) and "path" in f}

        found = False
        for a, b in combinations(sorted(pr_files), 2):
            shared = pr_files[a] & pr_files[b]
            if not shared:
                continue
            found = True
            print(f"#{a} <-> #{b}: {', '.join(sorted(shared))}")
            if pr_files[b].issubset(pr_files[a]):
                print(f"  * Duplicate Candidate: #{b} is a subset of #{a}")
            elif pr_files[a].issubset(pr_files[b]):
                print(f"  * Duplicate Candidate: #{a} is a subset of #{b}")
            print(f"  #{a}: {titles.get(a, '')[:72]}")
            print(f"  #{b}: {titles.get(b, '')[:72]}")
        if not found:
            print(f"No overlaps on {base}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
PYEOF
python3 "$OVERLAP_SCRIPT" prs.json
```

### Quick fallback one-liner
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
    if len(ns) > 1:
        print(f'{p}: {ns}')
"
```

---

## Triage Report Template

```
## PR Triage Report — {repo} ({date})

### ✅ Merge-Ready
| PR | Title | Author | CI | Review |
|----|-------|--------|----|--------|

### 🔧 Conflicts — Resolvable
| PR | Title | Conflict Summary | Resolution Plan |
|----|-------|------------------|-----------------|

### 💬 Needs Author Action
| PR | Title | Comment Left | Status |
|----|-------|-------------|--------|

### ⚠️ Needs Action
| PR | Title | Blocker |
|----|-------|---------|

### 🔁 Stale (>{N} days inactive)
| PR | Title | Last Activity | Recommendation |
|----|-------|---------------|----------------|

### 🔀 Overlapping
| PR A | PR B | Shared Files |
|------|------|--------------|

### 🤖 Bot/AI PRs
| PR | Author | Verification Status |
|----|--------|---------------------|

### ❌ Close Candidates (truly abandoned/superseded only)
| PR | Title | Reason |
|----|-------|--------|
```
