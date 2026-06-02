---
name: manage-prs
description: Triage, review, and merge GitHub PRs, including AI-generated PRs. Use for batch triage or single PR merges.
disable-model-invocation: true # Forces manual shell execution to keep agent control.
---

# Manage PRs

Multi-PR triage and merges via `gh`. If `gh` fails with auth (401), permission (403), unprocessable content (422), or network timeout errors, stop and ask the user. Default merge method: `--squash`.

## Scope
- **Use this**: Batch triage, merge planning, and sequential merges/closes.
- **Do not use for**: Continuous polling/babysitting of a single PR stuck on CI or active conflict resolution (use `git mergetool` / IDE merge editor for that).

## Workflows

| Intent | Workflow | Merges? |
|---|---|---|
| Triage / plan | 1. Triage | No |
| Review #N | 2. Review | No |
| Auto-merge #N | 3. Auto-merge | Yes (single) |
| Merge #N | 4. Merge | Yes (single) |
| Close / Reject | 5. Close/Comment | Close only |
| Execute plan | 6. Execute plan | Yes (after confirmation) |

## Quick start
```bash
gh pr list
gh pr diff 42
gh pr view 42 --comments --json mergeable,isDraft,reviewDecision,statusCheckRollup
```

## AI Checklist
Run when `author` is bot, description has bot signature (e.g. Jules), commits are by `google-labs-jules[bot]`, or labeled automated.
- **Hallucinations**: Verify all imports, APIs, and libraries. `grep` unfamiliar identifiers.
- **Over-scoping**: Diff must not exceed description.
- **Conflicts**: Check overlaps on same files.
- **Wrong logic**: Read core logic, not just diff.
- **Artefacts**: Ensure no debug or temp files.

## Standard Rubric
- **Correctness**: Diff matches description.
- **Tests**: New behavior covered; existing tests pass.
- **Safety**: No secrets, breaking config, or unvetted dependencies.

## Verdicts & Commands
- **Approve**: `gh pr review <n> --approve`
- **Request changes**: `gh pr review <n> --request-changes --body "..."`
- **Comment**: `gh pr comment <n> --body "..."` (plain comment for small nits/drafts).
- **Reject**: `gh pr close <n> --comment "Closing because..."`

## 1. Triage

**Triage means reading and understanding each PR — not just scanning metadata.** Do not classify a PR without reading its diff and verifying the logic.

1. **Gather**: `gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100` (increase `--limit` for large repos).
2. **Overlaps**: Save the JSON and run:
   ```bash
   python3 $(find ~ -name pr-overlap.py -maxdepth 10 2>/dev/null | head -1) prs.json
   ```
3. **For each PR — read the diff and apply rubrics**:
   - `gh pr diff <n>` — read the actual code changes.
   - `gh pr view <n> --comments` — read description and discussion.
   - Apply Standard Rubric and AI Checklist (if bot author).
   - Use `grep` / `git grep` to verify unfamiliar calls, imports, or identifiers in the codebase.
   - Check for semantic conflicts: does this PR silently change an API, log level, or config that another open PR depends on?
4. **Classify each PR into a bucket** (see below). Bucket assignment must be based on what you read in the diff, not just metadata.
5. **Deliver Plan**: Write to `/tmp/pr-triage-[repo]-YYYYMMDD-[suffix].md`. Do not merge without user approval.

### Buckets
- **Merge-ready**: Reviewed, logic correct, no safety issues, `MERGEABLE`.
- **Needs review**: Not yet read, or needs fixes identified during review.
- **Blocked**: `CONFLICTING`, `UNKNOWN` (mergeability not yet computed — re-check before merging), failing CI, file overlaps, or semantic conflicts.
- **Reject**: Duplicate, empty diff, stale, or buggy.

### Merge Order
Within Merge-ready, sequence as: security fixes → bug fixes → perf → refactor/chore → features → tests/docs. For same file: production code before tests. Opposite intents on same file: close the lesser one.

### Merge Method Precedence
`AGENTS.md` (if present) → repo settings → default `--squash`.

### Triage Plan Format
```markdown
# PR triage — [repo] — [date]

## CI status
[green / failing / none (local-only)]

## Merge method
[squash / merge / rebase — and why]

## PRs
| # | Title | Author | Bucket | CI | Overlaps | Verdict summary |
|---|---|---|---|---|---|---|
| #N | ... | @x | Merge-ready | pass | — | One-line rationale from reading the diff |

## File overlap hotspots
- `path/to/file`: #A, #B, #C

## Suggested merge order
1. #N — reason

## Blocked / needs action
- #N: what needs to happen before it can merge
```

## 2. Review
1. **Context**: `gh pr view <number> --comments` — read description and discussion.
2. **Diff**: `gh pr diff <number>` — read every changed line.
3. **Rubrics**: Apply Standard Rubric and AI Checklist.
4. **Verify**: Use `grep` / local files to trace unfamiliar calls and verify imports/types.
5. **Deliver verdict**:
   - Line-level issues: comment on exact lines.
   - General verdict: `gh pr review <number> --approve` or `--request-changes --body "..."`.

## 3. Auto-merge
- Run full Review. Verify safety rules.
- Approve and merge (resolved merge method + `--delete-branch`).

## 4. Merge
- **Pre-flight**: Confirm base hasn't drifted and all safety rules still pass.
- Merge (resolved merge method + `--delete-branch`).

## 5. Close/Comment
- **Fixable**: `gh pr comment` with specific fixes. Keep open.
- **Duplicate/Out of Scope**: Close with clear comment citing winner.

## 6. Execute Plan
- Sequentially merge/close as approved.
- Update behind branches: `gh pr update-branch <n>`. Fallback: `gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase`.
- **Post-merge**: Checkout/pull default branch, run tests, fix any breakage.
- **Verify branch deletion**: `gh pr view <n> --json headRefName` — remote branch should be absent.
- Deliver execution report:
```markdown
### Execution report
- **Merged**: #...
- **Closed**: #...
- **Skipped**: #...
- **Post-merge verification**: Tests [pass/fail]. Branch deletion: [confirmed/pending]. Commits: [shas]
```

## Safety Rules
- Never merge drafts, `CONFLICTING`, or `UNKNOWN` (re-check `UNKNOWN` with `gh pr view <n> --json mergeable` before merging).
- Never merge if required CI fails.
- No CI gate fallback: If `statusCheckRollup` is empty, run tests locally before and after merges; note CI in table as `none (local only)`.
- Never merge to non-default base or batch merge without user approval.
- Always comment when closing.

## Additional resources
- [examples.md](examples.md) — sample triage table, execution logs, and review comments
- [reference.md](reference.md) — CI fields, merge methods, overlap/duplicate rules, overlap script
- [scripts/pr-overlap.py](scripts/pr-overlap.py) — overlap detection script
