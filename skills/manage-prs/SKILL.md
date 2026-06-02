---
name: manage-prs
description: Triage, review, and merge GitHub PRs, including AI-generated PRs. Use for batch triage or single PR merges.
disable-model-invocation: true
---

# Manage PRs

Multi-PR triage and merges via `gh`. If `gh` fails with auth (401), permission (403), unprocessable content (422), or network timeout errors, stop and ask the user. Default merge method: `--squash`.

## Scope
- **Use this**: Batch triage, merge planning, and sequential merges/closes.
- **Do not use for**: Continuous polling of a single PR stuck on CI or active conflict resolution.

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
gh pr view 42 --json mergeable,isDraft,reviewDecision,statusCheckRollup,body,comments
```

## AI & Safety Checklist
For automated/bot PRs (e.g. Jules):
- **Hallucinations**: Verify all imports/APIs. `grep` unfamiliar identifiers.
- **Diff Limits**: Diff must not exceed description. No debug/temp files.
- **Standard Rubric**: Logic correct, tests pass, config/secrets safe.

## Quick Commands
- **Approve**: `gh pr review <n> --approve`
- **Request changes**: `gh pr review <n> --request-changes --body "..."`
- **Comment/Reject**: `gh pr comment <n> --body "..."` / `gh pr close <n> --comment "..."`

## 1. Triage
*Do not bucket a PR without reading its diff and verifying the logic.*

1. **Gather**: `gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100` > `prs.json`
2. **Detect Overlaps**: Run the helper script located in the parent directory of this skill:
   ```bash
   python3 <path_to_manage-prs_skill>/scripts/pr-overlap.py prs.json
   ```
   *Fallback (if script is missing/inaccessible):*
   ```bash
   python3 -c "import json, collections; data = json.load(open('prs.json')); by_file = collections.defaultdict(list); [(by_file[f['path']].append(pr['number']) for f in pr.get('files', []) if isinstance(f, dict) and 'path' in f) for pr in data if 'number' in pr]; [print(f'{p}: {ns}') for p, ns in sorted(by_file.items(), key=lambda x: -len(x[1])) if len(ns) > 1]"
   ```
3. **Inspect each PR**:
   - `gh pr diff <n>` — verify code correctness.
   - `gh pr view <n> --json body,comments` — read description and comments (avoid `--comments` crash).
   - Use `grep` to verify unfamiliar calls/imports in the codebase.
4. **Bucket & Order**: Assign to a bucket and sequence the merge order.
5. **Deliver Plan**: Write to `/tmp/pr-triage-[repo]-YYYYMMDD-[suffix].md`. Do not merge without approval.

### Buckets
- **Merge-ready**: Reviewed, logic correct, no safety issues, and explicitly `MERGEABLE`.
- **Needs review**: Not yet read, or requires feedback/fixes.
- **Blocked**: `CONFLICTING`, `UNKNOWN` (re-check with `gh pr view <n> --json mergeable` before merging), failing CI, or overlaps.
- **Reject**: Duplicate, empty diff, stale, or buggy.

> [!IMPORTANT]
> **Safety Rule on `UNKNOWN` Mergeability**: If a PR has `UNKNOWN` mergeability, it MUST be bucketed as **Blocked** (never **Merge-ready**). Do not mark it as Merge-ready until you re-query `gh pr view <n> --json mergeable` and confirm it returns `MERGEABLE`.

### Merge Order & Method
- **Sequence**: Security → bugs → perf → refactor/chore → features → tests/docs.
- **Conflicts**: Production code before tests. Opposite intents on same file: close lesser.
- **Method**: `AGENTS.md` override → repo settings → default `--squash` (always use `--delete-branch`).

### Triage Plan Format
Write the plan using this exact format:
```markdown
# PR triage — [repo] — [date]
## CI status: [green / failing / none (local-only)]
## Merge method: [squash / merge / rebase — why]
## PRs
| # | Title | Author | Bucket | CI | Overlaps | Verdict summary |
|---|---|---|---|---|---|---|
| #1 | Example PR | @x | [Merge-ready/Blocked/Reject] | pass | — | Rationale (Diff read!). WARNING: If mergeable is UNKNOWN, bucket as Blocked. |
| #2 | Uncomputed PR | @y | Blocked ⚠️ UNKNOWN | — | — | Re-query mergeable before merging! |

## File overlap hotspots
- `path/to/file`: #A, #B, #C

## Suggested merge order
1. #1 — security fix

## Blocked / needs action
- #2: re-check mergeability
```

## 2. Review
1. **Context**: `gh pr view <number> --json body,comments` (avoid `--comments` crash) or `gh api repos/{owner}/{repo}/issues/<number>/comments`.
2. **Diff & Verify**: `gh pr diff <number>`. `grep` unfamiliar identifiers.
3. **Verdict**: Comment on exact lines if needed. Submit: `gh pr review <number> --approve` or `--request-changes --body "..."`.

## 3. Auto-merge
- Perform full Review. If safe, approve and merge: `gh pr merge <number> --squash --delete-branch`.

## 4. Merge & 5. Close/Comment
- **Merge**: `gh pr merge <number> --squash --delete-branch` (confirm base has not drifted).
- **Close**: `gh pr close <number> --comment "Closing because..."`. Always explain.

## 6. Execute Plan
- Sequentially merge/close as approved. Update behind branches: `gh pr update-branch <n>` (fallback: use `gh api .../update-branch -f merge_method=rebase`).
- **Post-merge**: Checkout `main`, pull, run tests, verify remote branch deletion. Deliver report:
```markdown
### Execution report
- **Merged**: #... | **Closed**: #... | **Skipped**: #...
- **Verification**: Tests [pass/fail]. Branch deletion [confirmed/pending]. Commits: [shas]
```

## Safety Rules
- **Never merge** drafts, `CONFLICTING`, or `UNKNOWN` (re-query `UNKNOWN` to verify).
- **CI Failure**: Never merge if required CI checks fail.
- **No CI fallback**: If empty, run tests locally before/after merges; note as `none (local only)`.
- **Approval**: Never batch merge or merge to non-default base without user approval.
- **Closing**: Always comment when closing a PR.

## Additional resources
- [examples.md](examples.md) — sample triage table, execution logs, and review comments
- [reference.md](reference.md) — CI fields, merge methods, overlap/duplicate rules
- [scripts/pr-overlap.py](scripts/pr-overlap.py) — overlap detection script
