# Manage PRs — Reference

## gh Fields
- `gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100`
- `gh pr view <n> --json isDraft,mergeable,reviewDecision,statusCheckRollup,state,mergedAt`

| Field | Meaning / Possible Values |
|---|---|
| `isDraft` | Must be `false` to merge. |
| `mergeable` | `MERGEABLE` or `BEHIND` (needs update). `CONFLICTING` blocks merge. |
| `reviewDecision` | `APPROVED` (ok to merge), `REVIEW_REQUIRED` (needs review), `CHANGES_REQUESTED` (blocked by review). |
| `statusCheckRollup` | Check `FAILURE`/`ERROR` on required contexts. |
| `files` | File paths for overlap checking. |

- Check required statuses via `gh pr checks <n>` if unclear.

## Merge Methods & Precedence
- **Precedence**: Always prioritize merge methods specified in `AGENTS.md` or repository settings. If none are specified, use the defaults below:
  - `--squash` (default for standard feature branches).
  - `--merge` (default for release branches or sync commits).
  - `--rebase` (use when explicitly requested or enabled on the repo).
- Always include `--delete-branch` to keep remote clean.

## Overlaps & Duplicates
- **Overlap**: Shared file paths in `files` for PRs targeting the same `baseRefName` → block and sequence.
- **Duplicate**: Same title/description, or files set is subset of another. Merge complete PR, close subset.
- **Overlap Script**: Discovered dynamically (e.g. `python $(find ~ -name pr-overlap.py -maxdepth 8 2>/dev/null | head -1) <path_to_prs_json>`).

## Branch Updates
- If branch is `BEHIND`: `gh pr update-branch <n>`.
- Fallback: `gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase`

## Post-merge Verify
- `gh pr view <n> --json state,mergedAt` (should be `MERGED`).
- Verify branch deletion: `gh pr view <n> --json headRefName` to ensure the remote branch is gone, or run `git branch -r` to check remote state.
