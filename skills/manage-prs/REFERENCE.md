# Manage PRs — Reference

Gotchas, command patterns, conflict resolution mechanics, and reusable scripts.

---

## Gotchas & Landmines

### `UNKNOWN` mergeability is a hard block
GitHub computes mergeability asynchronously and temporarily returns `UNKNOWN`. Never merge `UNKNOWN`.
Re-query until resolved:
```bash
gh pr view <n> --json mergeable
```
Retry up to 3 times with 2–3 seconds between queries. If still `UNKNOWN`, report to the user.

### `gh pr merge` transient API race conditions
When merging PRs sequentially or immediately after a force push, GitHub GraphQL API may return `GraphQL: Base branch was modified. Review and try the merge again` or `GraphQL: Pull Request has merge conflicts`.
This is often a transient caching race. Wait 2–3 seconds and retry the command up to 3–5 times before failing.

### `gh pr checkout` panics on some environments
Never use `gh pr checkout` — it can segfault or panic across platforms. Always fetch and checkout manually:
```bash
git fetch origin pull/<n>/head:pr-<n>
git checkout pr-<n>
```

### `gh pr update-branch` does not exist
The native CLI command does not exist. Use the raw GitHub API:
```bash
gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=squash
```
Fallback if squash is not supported on the target repo:
```bash
gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase
```

### `gh pr list` silently caps at 100
Always specify `--limit 100`. If the returned list contains exactly 100 PRs, warn the user that additional PRs exist beyond the batch cap.

### `git rebase --continue` hangs on interactive editor prompts
In non-interactive agent environments, `git rebase --continue` will hang waiting for an editor.
Always prefix with `GIT_EDITOR=true` to reuse the existing commit message:
```bash
GIT_EDITOR=true git rebase --continue
```

### Delay between batch merges
Insert a short delay (`sleep 2`) between consecutive `gh pr merge` calls in batch queues to avoid triggering base branch update race conditions on GitHub's API.

### Bot / AI PR verification
For automated PRs (e.g. Jules, Dependabot, Copilot), `grep` unfamiliar identifiers or newly imported packages in the codebase before approving. Do not trust the description alone.

---

## Diff Collection Loop

Run from the repository root after `prs.json` is generated:

```bash
for n in $(jq -r '.[].number' prs.json); do
  gh pr diff "$n" > "pr-${n}.diff"
  echo "Collected pr-${n}.diff"
done
```

---

## Overlap Detection

Run this self-contained Python script to detect file-level collisions and subset PRs across the queue:

```bash
python3 -c "
import json, collections, itertools, sys

try:
    data = json.load(open('prs.json'))
except Exception as e:
    sys.exit(f'Error reading prs.json: {e}')

by_base = collections.defaultdict(list)
for pr in data:
    if 'number' in pr:
        by_base[pr.get('baseRefName', 'main')].append(pr)

for base, prs in by_base.items():
    if len(prs) < 2:
        continue
    print(f'=== Target Branch: {base} ===')
    pr_files = {pr['number']: {f['path'] for f in pr.get('files', []) if isinstance(f, dict) and 'path' in f} for pr in prs}
    titles = {pr['number']: pr.get('title', '') for pr in prs}
    found = False
    for a, b in itertools.combinations(sorted(pr_files), 2):
        shared = pr_files[a] & pr_files[b]
        if not shared:
            continue
        found = True
        print(f'#{a} <-> #{b} shared: ' + ', '.join(sorted(shared)))
        if pr_files[a] and pr_files[b]:
            if pr_files[b].issubset(pr_files[a]):
                print(f'  * Duplicate Candidate: #{b} is a subset of #{a}')
            elif pr_files[a].issubset(pr_files[b]):
                print(f'  * Duplicate Candidate: #{a} is a subset of #{b}')
        print(f'  #{a}: {titles[a][:72]}')
        print(f'  #{b}: {titles[b][:72]}')
    if not found:
        print(f'No overlapping files on {base}.')
"
```

---

## Local Conflict Resolution — Details

### Primary Sources Investigation
Inspect both sides before attempting resolution:
- **PR author intent**: `gh pr view <n> --json title,body` and diff file `pr-<n>.diff`.
- **Target base intent**: Inspect commit history of the conflicting file on the base branch:
  ```bash
  git log -n 5 --oneline origin/<base-branch> -- <conflicting-file>
  git show <commit-hash>
  ```

### Hunk Resolution Rules
- **Preserve orthogonal intents**: Keep independent additions, non-conflicting imports, and separate function declarations from both branches.
- **Align with PR goal on direct collision**: When changes compete directly, pick the change that fulfills the PR's stated objective while maintaining base branch invariants. Document the trade-off.
- **Zero invented behaviour**: Never refactor adjacent code, change unrelated formatting, or introduce unrequested logic during conflict resolution.

### Standard Rebase Execution

```bash
# 1. Fetch PR branch
git fetch origin pull/<n>/head:pr-<n>
git checkout pr-<n>

# 2. Start rebase against base branch
git rebase origin/<base-branch>

# 3. For each conflicted commit:
#    a. Inspect conflicts: git status, git diff
#    b. Resolve hunks in editor (preserve both intents, zero invented behaviour)
#    c. Stage resolved files: git add <resolved-files>
#    d. Continue rebase:
GIT_EDITOR=true git rebase --continue

# 4. Run automated checks before pushing (see Repo Verification Heuristic below)

# 5. Push resolved branch back
# Note: <head-ref-name> is the branch name from prs.json
git push --force-with-lease origin pr-<n>:<head-ref-name>

# 6. Clean up local tracking branch
git checkout <base-branch>
git branch -D pr-<n>
```

### Fork PR Pushback
When the PR originates from a fork, push directly to the fork's remote URL:

```bash
PUSH_URL=$(gh pr view <n> --json headRepository \
  --jq '"https://github.com/" + .headRepository.owner.login + "/" + .headRepository.name + ".git"')
BRANCH=$(gh pr view <n> --json headRefName --jq '.headRefName')
git push --force-with-lease "$PUSH_URL" "pr-<n>:$BRANCH"
git branch -D pr-<n>
```

### Abort Criteria for Local Resolution
Leave the PR open and comment with specific guidance when:
- Conflicts span 5+ files with major architectural collisions.
- Rebase produces missing dependencies or removed core APIs requiring domain redesign.
- PR changes are superseded by a newer merged PR or direct commit (in which case, close with explanation).

### Batch Automation
When handling large queues (>5 PRs), write a temporary scratch script (e.g. `scratch/merge_batch.py`) to automate sequential rebasing, running check commands, force-pushing, and merging. Always use `GIT_EDITOR=true`.

---

## Repo Verification Heuristic

Run the first matching command once on final `main` after all merges are complete:

| Signal file | Verification Command |
|-------------|----------------------|
| `package.json` | `npm test && npm run lint` |
| `Makefile` | `make test` |
| `pytest.ini` or `pyproject.toml` | `pytest` |
| `build.gradle` or `gradlew` | `./gradlew testDebugUnitTest` |
| CI config (`.github/workflows/`) | Check workflow step corresponding to tests |

---

## Session Cleanup

Run at the end of every session (Phase 4):

```bash
rm -f prs.json pr-*.diff
git branch -D $(git branch --list 'pr-*') 2>/dev/null || true
```

---

## Merge Plan Template

Write as an `implementation_plan.md` artifact awaiting user review before Phase 3 execution:

```markdown
# PR Merge Plan — {repo} ({date})

### ✅ Merge-Ready
| PR | Title | Author | CI | Review | Notes |
|----|-------|--------|----|--------|-------|

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

### ❌ Close Candidates (truly abandoned/superseded only)
| PR | Title | Reason |
|----|-------|--------|
```

> Overlapping PRs are annotated in the Notes column of their category row (e.g. "overlaps #94 — merge first"), not listed in a separate category.
