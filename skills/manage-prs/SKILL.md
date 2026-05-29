---
name: manage-prs
description: Triage, review, and merge GitHub PRs, including AI-generated PRs. Use for batch triage or single PR merges.
disable-model-invocation: true # Forces manual shell execution to keep agent control.
---

# Manage PRs

Multi-PR triage and merges via `gh`. If `gh` fails with auth (401), permission (403), unprocessable content (422), or network timeout errors, stop and ask the user. Read `AGENTS.md` at root for custom rules. If `AGENTS.md` is absent or unspecified, default to `--squash` for standard merges.

## Scope
- **Use this**: Batch triage, merge planning, and sequential merges/closes.
- **Use babysit**: Single PR stuck on CI, conflicts, or comment threads.

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
1. **Gather**: `gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100` (increase `--limit` for large repos).
2. **Diffs**: `gh pr diff <n>` for each.
3. **Overlaps**: Locate the script dynamically and run: `python $(find ~ -name pr-overlap.py -maxdepth 8 2>/dev/null | head -1) <path_to_json>`.
4. **Analyse**: Apply checklists. If empty diff, verify via `git show <head-sha> --stat`, classify as **Reject**, and close.
5. **Semantic Conflicts**: Check if any PR modifies/silences an API, configuration, or log level. Run `grep` or `git grep` on other PR files to see if they assert old behavior, verify old signatures, or expect old output. Mark **Blocked** if conflicts exist.
6. **Deliver Plan**: Write to `/tmp/pr-triage-[repo]-YYYYMMDD-[suffix].md` (use suffix to avoid concurrent race conditions). Do not merge without user approval.

### Buckets
- **Merge-ready**: Approved, CI green, `MERGEABLE`.
- **Needs review**: Untriaged or needs fixes.
- **Blocked**: Failing CI, git conflicts, file overlaps, or semantic conflicts.
- **Reject**: Duplicate, empty, stale, or buggy.

### Merge Order
- Fixes → features. Smaller → larger. Unblock deps. Determine merge method following precedence rules: `AGENTS.md` -> repo settings -> default `--squash`.
- For same file: merge production code before tests.
- Opposite intents: close/rebase test PR; do not merge both.

## 2. Review
1. **Context**: Fetch comments using `gh pr view <number> --comments` and description.
2. **Diff**: Inspect full changes with `gh pr diff <number>`.
3. **Rubrics**: Run the Standard Rubric and AI Checklist.
4. **Verify**: Use local files/tools or `grep` to trace unfamiliar calls and verify imports/types.
5. **Deliver verdict**:
   - For specific line-level issues, comment on exact lines.
   - For general verdicts, post a top-level review via `gh pr review <number> --approve` or `gh pr review <number> --request-changes --body "..."`.

## 3. Auto-merge
- Run full Review. Verify safety rules.
- Approve and merge using repo/AGENTS.md method (defaulting to `--squash` if unspecified) and `--delete-branch`.

## 4. Merge
- **Pre-flight**: Run a quick review pass to ensure the base branch hasn't drifted since approval and all safety rules still pass.
- Merge using repo/AGENTS.md method (defaulting to `--squash`) + `--delete-branch`.

## 5. Close/Comment
- **Fixable**: Comment on fixes via plain `gh pr comment`. Keep open.
- **Duplicate/Out of Scope**: Close with clear comment citing winner.

## 6. Execute Plan
- Sequentially merge/close as approved.
- Update behind branches: `gh pr update-branch <n>`. Resolve merge method following precedence rules: `AGENTS.md` -> repo settings -> default `--squash`. Fallback: `gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase`.
- **Post-merge**: Checkout/pull default branch, run tests (e.g. `npm test`), fix any breakage.
- Deliver execution report:
```markdown
### Execution report
- **Merged**: #...
- **Closed**: #...
- **Skipped**: #...
- **Post-merge verification**: Tests [pass/fail]. Commits: [shas]
```

## Safety Rules
- Never merge drafts or branches that are `BEHIND` / `CONFLICTING` without updating first.
- Never merge if required CI fails.
- No CI gate fallback: If `statusCheckRollup` is empty, run tests locally before and after merges; note CI in table as `none (local only)`.
- Never merge to non-default base or batch merge without user approval.
- Always comment when closing.

## Additional resources
- [examples.md](examples.md) — sample triage table, execution logs, and review comments
- [reference.md](reference.md) — CI fields, merge methods, overlap/duplicate rules, overlap script
