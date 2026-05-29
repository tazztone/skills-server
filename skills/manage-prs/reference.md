# Manage PRs — Reference

## gh Fields
- `gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100`
- `gh pr view <n> --json isDraft,mergeable,reviewDecision,statusCheckRollup,state,mergedAt`

| Field | Meaning |
|---|---|
| `isDraft` | Must be `false` |
| `mergeable` | `MERGEABLE` or `BEHIND`. `CONFLICTING` blocks |
| `statusCheckRollup` | Check `FAILURE`/`ERROR` on required contexts |
| `files` | File paths for overlap checking |

- Check required statuses via `gh pr checks <n>` if unclear.

## Merge Methods
- `--squash` (default for features) | `--merge` (releases) | `--rebase` (on request/config).
- Always include `--delete-branch`.

## Overlaps & Duplicates
- **Overlap**: Shared file paths in `files` → block and sequence.
- **Duplicate**: Same title/description, or file set is subset of another. Merge complete PR, close subset.
- **Overlap Script**: `gh pr list --json number,title,files --limit 100 > /tmp/prs.json && python scripts/pr-overlap.py /tmp/prs.json`

## Branch Updates
- If branch is `BEHIND`: `gh pr update-branch <n>`.
- Fallback: `gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase`

## Post-merge Verify
- `gh pr view <n> --json state,mergedAt` (should be `MERGED`).
