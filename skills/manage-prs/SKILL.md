---
name: manage-prs
description: Triage, review, and merge GitHub PRs, including AI-generated PRs. Use for batch triage or single PR merges.
disable-model-invocation: true # Forces manual shell execution to keep agent control.
---

# Manage PRs

Multi-PR triage and merges via `gh`. If `gh` auth expires (401), stop and ask user. Read `AGENTS.md` at root for custom merge rules, CI gates, and reviewer rules.

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
3. **Overlaps**: Run `python <skill_dir>/scripts/pr-overlap.py <path_to_json>`.
4. **Analyse**: Apply checklists. If empty diff, verify via `git show <head-sha> --stat`, classify as **Reject**, and close.
5. **Semantic Conflicts**: Mark **Blocked** if:
   - Behavior changes but other PR tests old behavior.
   - Logging is silenced but other PR asserts it.
6. **Deliver Plan**: Write to `/tmp/pr-triage-[repo]-YYYYMMDD-[suffix].md`. Do not merge without user approval.

### Buckets
- **Merge-ready**: Approved, CI green, `MERGEABLE`.
- **Needs review**: Untriaged or needs fixes.
- **Blocked**: Failing CI, git conflicts, file overlaps, or semantic conflicts.
- **Reject**: Duplicate, empty, stale, or buggy.

### Merge Order
- Fixes → features. Smaller → larger. Unblock deps.
- For same file: merge production code before tests.
- Opposite intents: close/rebase test PR; do not merge both.

## 2. Review
- Run AI + Standard rubrics on diff + comments.
- Submit review with exact verdict.

## 3. Auto-merge
- Run full Review. Verify safety rules.
- Approve and merge using repo/AGENTS.md method (`--squash`, `--rebase`, `--merge`) and `--delete-branch`.

## 4. Merge
- Verify safety rules. Merge using repo/AGENTS.md method + `--delete-branch`.

## 5. Close/Comment
- **Fixable**: Comment on fixes via plain `gh pr comment`. Keep open.
- **Duplicate/Out of Scope**: Close with clear comment citing winner.

## 6. Execute Plan
- Sequentially merge/close as approved.
- Update behind branches: `gh pr update-branch <n>`. Fallback: `gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase`.
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
- [examples.md](examples.md) — sample triage table and review comment
- [reference.md](reference.md) — CI fields, merge methods, overlap/duplicate rules, overlap script
