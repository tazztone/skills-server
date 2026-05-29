# Manage PRs — Examples

## Sample Triage
# PR triage — acme/widgets — [date]
### Merge order
1. #38 — fix auth; blocks #42
2. #40 — docs only
3. #42 — feature (after #38)

| PR | Author | Bucket | CI | Overlaps | Action |
|---|---|---|---|---|---|
| #38 | @alice | Merge-ready | pass | #42 | Merge first |
| #40 | @bob | Merge-ready | pass | — | Merge anytime |
| #42 | @jules[bot] | Blocked | pass | #38 | Merge after #38 |
| #39 | @jules[bot] | Reject | pass | subset of #38 | Close |

## Sample Review Comment
### Summary
Adds retry logic to webhooks. Sound approach. Two blockers.
### Blockers
1. `src/webhook.ts:88` — retries on 4xx; should be 5xx.
2. Missing max retries test.
### AI checklist
No hallucinated imports. Webhook API verified. No artefacts.
### Verdict
**Request changes** — fix blockers.

## Sample Workflow 6 Execution Log
```bash
# Verify mergeability of first PR in queue
gh pr view 38 --json mergeable
# Merge with squash and delete the head branch
gh pr merge 38 --squash --delete-branch
# Update the subsequent PR branch which is now BEHIND
gh pr update-branch 42
# Merge updated PR after CI/local test passes
gh pr merge 42 --squash --delete-branch
# Verify on local main branch
git checkout main && git pull
npm test
```
