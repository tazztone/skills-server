# Manage PRs — Reference

Gotchas, command patterns, conflict resolution details, and reusable scripts.

---

## Gotchas & Landmines

### `gh pr checkout` panics on some environments
Never use `gh pr checkout` — it segfaults. Always fetch manually:
```bash
git fetch origin pull/<n>/head:pr-<n>
git checkout pr-<n>
```

### `gh` vs `git` boundary
Use `gh` for GitHub API operations: `pr list`, `pr diff`, `pr view`, `pr merge`, `pr comment`, `pr close`.
Use `git` for all local work: fetch, checkout, rebase, push. Never mix.

### `UNKNOWN` mergeability is a hard block
GitHub computes mergeability asynchronously and temporarily returns `UNKNOWN`. **Never merge `UNKNOWN`.**
Re-query until it resolves:
```bash
gh pr view <n> --json mergeable
```
Retry up to 3 times with a few seconds between. If still `UNKNOWN`, report to the user.

### `gh pr merge` fails with base branch modified or merge conflict errors
When merging multiple PRs sequentially or right after a force push, the GitHub GraphQL API might return `GraphQL: Base branch was modified. Review and try the merge again` or `GraphQL: Pull Request has merge conflicts`.
This is often a transient caching issue. Wait 2-3 seconds and retry the command up to 3-5 times before giving up.

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

### `git rebase --continue` hangs on interactive editor prompts
By default, `git rebase --continue` opens the default editor to let you modify commit messages. In headless/non-interactive agent environments, this will hang.
Prefix the command with `GIT_EDITOR=true` (i.e. `GIT_EDITOR=true git rebase --continue`) to bypass the editor screen and reuse the existing commit message.

### Structural/cache-layer PRs are systemic blockers
PRs altering service workers (`sw.js`), architectural caching, or app-layer config have cascading side effects.
Group these, isolate the ideal structural layout first, and reject/close alternates — don't chain-merge blindly.

### Never merge without reading the diff
CI green is not sufficient. Always run `gh pr diff <n>` (single-PR) or read `pr-<n>.diff` (batch) and verify the logic.

### Bot/AI PRs: verify imports and APIs
For automated PRs (e.g. Jules, Dependabot), `grep` any unfamiliar identifiers in the codebase before approving.
Do not trust the PR description alone.

### Prefer commenting over closing
When a PR needs work, comment with specific actionable feedback and leave it open — the author can iterate in place. Only close PRs that are truly abandoned, superseded, or duplicate. If you must close: `gh pr close <n> --comment "Closing because..."` — never silently.

### Avoid sequential multi-query bloat
Do not re-fetch `gh pr list` after every merge.
Group non-overlapping merge-ready PRs into a batch queue, execute sequentially, and sync at the end. Insert a short delay (e.g. `sleep 2`) between consecutive `gh pr merge` calls to prevent transient base branch update errors.

---

## Repo Verification Heuristic

After all merges and resolutions are complete, detect and run the repo's verification commands once on final main:

| Signal file | Command |
|-------------|---------|
| `package.json` | `npm test && npm run lint` |
| `Makefile` | `make test` |
| `pytest.ini` or `pyproject.toml` | `pytest` |
| `build.gradle` or `gradlew` | `./gradlew testDebugUnitTest` |
| CI config (`.github/workflows/`) | Check for the test job's `run:` step |

Run the first matching command. If none match, check the CI config.

---

## Diff Collection Loop

Run from the repo root after `prs.json` exists:

```bash
for n in $(jq -r '.[].number' prs.json); do
  gh pr diff "$n" > "pr-${n}.diff"
  echo "Collected pr-${n}.diff"
done
```

---

## Overlap Detection

After collecting diffs and `prs.json`, detect file overlaps to sequence merges safely.

If triaging within the skill-server workspace itself:
```bash
python3 scripts/pr-overlap.py prs.json
```

If triaging in another target repository, use the quick fallback one-liner (or resolve the absolute path to the skill's `scripts/pr-overlap.py`):

### Quick fallback one-liner (Recommended for other repos)
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

## Local Conflict Resolution — Details

When the diff investigation shows a PR's changes are worth preserving, resolve locally.

### Investigating primary sources
Never guess intent from raw conflict markers alone. Inspect both sides:
- **PR intent**: Read `gh pr view <n> --json title,body` and the PR diff (`pr-<n>.diff` or `gh pr diff <n>`).
- **Base intent**: Inspect the commits that touched the conflicting file on the base branch:
  ```bash
  git log -n 5 --oneline origin/<base-branch> -- <conflicting-file>
  git show <commit-hash>
  ```

### Hunk-by-hunk resolution rules
- **Preserve both intents**: If changes are orthogonal (e.g. concurrent additions, independent imports, separate functions), keep both.
- **Align with PR goal on collision**: If changes directly compete, choose the change that achieves the PR's stated goal while respecting base invariants. Note the trade-off in the merge/PR comment.
- **Zero invented behaviour**: Do not refactor adjacent code, change unrelated formatting, or add unrequested features while resolving conflicts.

### Standard rebase flow

```bash
# Fetch the PR branch (works for both origin and fork PRs)
git fetch origin pull/<n>/head:pr-<n>
git checkout pr-<n>

# Start rebase onto target base
git rebase origin/<base-branch>

# While conflicts exist across commits:
# 1. Inspect conflict: git status, git diff
# 2. Inspect primary sources for both sides
# 3. Resolve each hunk preserving both intents (zero invented behaviour)
# 4. Stage resolved files: git add <resolved-files>
# 5. Continue rebase:
GIT_EDITOR=true git rebase --continue
# (Repeat steps until rebase completes cleanly)

# Run automated checks before pushing (see Repo Verification Heuristic)
# e.g., npm test && npm run lint / pytest / make test

# Push the resolved branch back
# Note: <head-ref-name> is the head branch name from prs.json
git push --force-with-lease origin pr-<n>:<head-ref-name>

# Clean up local branch
git checkout <base-branch>
git branch -D pr-<n>
```

### Automation for large batches
If triaging or merging a large batch of PRs (e.g., >5), write a temporary Python script in the scratch directory (e.g. `merge_helper.py`) to automate checkout, rebase, automatic resolution of trivial conflicts, running checks, force-pushing, merging, and cleaning up. This saves time and avoids copy-paste command errors. Use `GIT_EDITOR=true` in any automated git rebase commands.

### Fork PR pushback

When the PR is from a fork, you cannot push to `origin/<branch>`. Get the fork's push URL:

```bash
PUSH_URL=$(gh pr view <n> --json headRepository \
  --jq '"https://github.com/" + .headRepository.owner.login + "/" + .headRepository.name + ".git"')
BRANCH=$(gh pr view <n> --json headRefName --jq '.headRefName')
git push --force-with-lease "$PUSH_URL" "pr-<n>:$BRANCH"
git branch -D pr-<n>
```

### When to abort local resolution
- Conflict spans 5+ files with unrelated cross-cutting changes — comment with analysis, leave open for author.
- PR's changes are superseded by a newer PR or direct commit — close with explanation.
- Rebase produces a state where verification clearly fails (missing deps, removed APIs) — comment with what broke and why, leave open.

---

## Session Cleanup

Run at the end of every session (Phase 4):

```bash
rm -f prs.json pr-*.diff
git branch -l 'pr-*' | xargs -r git branch -D
```

---

## Merge Plan Template

Write this as an `implementation_plan.md` artifact. Request user feedback on the artifact.

```
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
