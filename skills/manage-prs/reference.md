# Manage PRs — Reference

## `gh` JSON fields

**List (triage):**

```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100
```

**Single PR (pre-merge):**

```bash
gh pr view <n> --json isDraft,mergeable,reviewDecision,statusCheckRollup,state,mergedAt
```

| Field | Use |
|-------|-----|
| `isDraft` | Must be `false` to merge |
| `mergeable` | `MERGEABLE` ok; `CONFLICTING` → blocked |
| `reviewDecision` | Need approval when branch protection requires it |
| `statusCheckRollup` | Array of checks; treat `FAILURE` / `ERROR` on required contexts as blocking |
| `files` | Paths for overlap detection |

### CI / required checks

- Prefer checks with `state` in `FAILURE`, `ERROR`, or pending `IN_PROGRESS` on contexts that block merge.
- If you cannot tell which checks are required, run `gh pr checks <n>` and ask the user before merging.

## Merge methods

| Flag | When |
|------|------|
| `--squash` | Default for feature branches |
| `--merge` | Release branches or user/repo convention |
| `--rebase` | Only when user requests |

Always pass `--delete-branch` unless the user says otherwise.

## Overlap and duplicates

**Overlap (dependency pair):** two open PRs share at least one path in `files` → mark both **Blocked** until ordered; merge/update order matters.

**Duplicate candidates:**
- Same or near-identical titles/descriptions
- One PR’s changed-file set is a subset of another’s
- Same functional change after reading diffs (not just shared files)

**Subset:** if PR B’s files ⊆ PR A’s files and the description matches, prefer merging the more complete PR (usually A) and close B.

### Overlap script

After saving list JSON to scratch (run from the skill directory or pass the full path to the script):

```bash
gh pr list --json number,title,files --limit 100 > /tmp/prs.json
python scripts/pr-overlap.py /tmp/prs.json
```

Output: pairs of PR numbers that share files. Use only for triage; do not commit `/tmp` artifacts.

## Branch updates before merge

When `mergeable` is `BEHIND` or checks failed after base moved:

```bash
gh pr update-branch <n>
```

Wait for CI, re-run safety checks, then merge.

## Permissions

- **Review / comment / close:** read access to repo; `gh auth` with `repo` or `public_repo` as appropriate.
- **Merge:** merge rights on the target branch; may need `workflow` scope if merging triggers Actions you cannot see.

## Post-merge verification

```bash
gh pr view <n> --json state,mergedAt
# state should be MERGED; mergedAt non-null
```
