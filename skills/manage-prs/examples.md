# Manage PRs — Examples

## Sample triage output

```markdown
# PR triage — acme/widgets — [date]

## Merge order
1. #38 — fix auth regression; blocks #42 on `src/foo.ts`
2. #40 — small docs-only; no overlaps
3. #42 — feature after #38 lands

## Table

| PR | Author | Bucket | CI | Overlaps | Notes | Action |
|----|--------|--------|----|----------|-------|--------|
| #38 | @alice | Merge-ready | pass | #42 | Correct fix for TOKEN_EXPIRED | Merge first |
| #40 | @bob | Merge-ready | pass | — | README only | Merge anytime |
| #42 | @jules[bot] | Blocked | pass | #38 | Imports `validateSession` — exists; logic OK after #38 | Merge after #38 |
| #39 | @jules[bot] | Reject | pass | subset of #38 | Same files as #38, smaller diff | Close in favour of #38 |

## Risks
- #42 and #38 both touch `src/foo.ts` — update #42 branch after #38 merges.
```

## Sample review comment

```markdown
## Summary
Adds retry logic to the payment webhook handler. Approach is sound; two blockers before merge.

## Blockers
1. **`src/webhook.ts:88`** — retries on 4xx responses; should only retry 5xx/timeouts.
2. **Missing test** — no case for exhausted retries (max 3).

## Suggestions
- Extract magic number `3` to named constant matching existing `MAX_RETRIES` in `src/config.ts`.

## AI checklist
- No hallucinated imports; `stripe.Webhook` usage matches lockfile.
- No committed artefacts.

## Verdict
**Request changes** — fix blockers 1–2, then good to merge.
```

Post with:

```bash
gh pr review 42 --request-changes --body "$(cat <<'EOF'
[paste structured comment]
EOF
)"
```

## Sample close comment (duplicate)

```bash
gh pr close 39 --comment "Closing in favour of #38, which includes the same auth fix with tests."
```
