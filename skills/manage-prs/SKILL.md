---
name: manage-prs
description: Review, triage, approve, reject, and merge GitHub pull requests, including AI-generated PRs. Use when the user wants to review PRs, merge a PR, assess all open PRs, close a bad PR, request changes, auto-merge clean PRs, or plan a merge strategy across a repository. Do not use for babysitting a single PR through CI and comments — use babysit instead.
disable-model-invocation: true
---

# Manage PRs

GitHub PR operations across one or many pull requests. Read repo-specific rules from `AGENTS.md` at the repository root when present.

`gh` needs network access and appropriate repo permissions (read for review; merge rights for merge workflows).

## Scope

| Use this skill | Use another skill |
|----------------|-------------------|
| Triage all open PRs, merge planning, approve/close/merge | **babysit** — one PR stuck on CI, conflicts, or review threads |
| Review verdicts and GitHub actions | **review** — deep code-quality review without GitHub ops (if available) |

For `gh pr create` and HEREDOC bodies, follow project or user PR-creation rules when they exist.

## When to use which workflow

| User intent | Workflow | Merge? |
|-------------|----------|--------|
| "Triage open PRs" / "plan merges" | 1. Triage | No — plan only |
| "Review #N" | 2. Review | No — unless user also asks to merge |
| "Auto-merge #N" / "merge if clean" | 3. Auto-merge | Yes — single PR only |
| "Merge #N" (already approved) | 4. Merge | Yes — single PR |
| Close / reject handling | 5. Handle rejected | Close only when appropriate |
| "Execute the plan" / "run the merges" | 6. Execute plan | Yes — after explicit user confirmation |

Never merge during triage (workflow 1). Never batch-merge without user confirmation (workflow 6).

## Quick start

```bash
gh pr list
gh pr diff 42
gh pr view 42 --comments
gh pr view 42 --json mergeable,isDraft,reviewDecision,statusCheckRollup
```

## Detect AI-generated PRs

Run the AI checklist when any of these apply:

- `author.login` ends with `[bot]` or is a known agent account (e.g. `jules`, `cursor`, `dependabot`)
- PR body/description contains "created automatically by Jules", "Co-authored-by: ...[bot]", or similar indicator of agent creation
- Commits are authored by `google-labs-jules[bot]` (or similar) even when the PR author is listed as a human
- PR labels mention an agent or automation
- Description/body states the PR was opened by an agent

When unsure, treat as AI-generated and apply the checklist.

## AI-generated PR checklist

Run **before** the standard review rubric when the PR is AI-generated (see above).

- **Hallucinated imports / functions** — do all imported modules, functions, and types exist? `grep` unfamiliar identifiers.
- **Over-scoping** — does the diff exceed what the description justifies? (Also covered under scope creep in the standard rubric.)
- **Cross-PR conflicts** — does this PR overlap another open PR on the same files? Use triage file lists or [overlap detection](reference.md#overlap-and-duplicates).
- **Invented APIs** — do library calls match the installed version? Check `package.json` / lockfile / docs.
- **Plausible-but-wrong logic** — read the core logic path, not just the diff surface.
- **Committed artefacts** — `.orig`, `.diff`, debug output, temp files → comment; do not merge until removed.

## Standard review rubric

- **Correctness** — does the code match the PR description?
- **Tests** — new behaviour covered? Existing tests still passing?
- **Breaking changes** — public API, config, or schema without migration?
- **Scope creep** — unrelated changes in the diff?
- **Security** — secrets, unchecked inputs, risky new dependencies?
- **Style** — consistent with surrounding code? (Nits: comment, don’t block.)

## Verdicts and `gh` commands

| Verdict | Meaning | Action |
|---------|---------|--------|
| **Approve** | Ready to merge (subject to safety rules) | `gh pr review <n> --approve` |
| **Request changes** | Fixable issues; keep PR open | `gh pr review <n> --request-changes --body "..."` |
| **Comment only** | Feedback without blocking | `gh pr review <n> --comment --body "..."` |
| **Reject (close)** | Duplicate, out of scope, or unrecoverable | Workflow 5 — `gh pr close` with explanation |

"Reject" is not a `gh pr review` flag. Use request-changes for fixable work; close only when appropriate.

## Triage output template

Write to a **scratch path only** (never commit): e.g. `/tmp/pr-triage-YYYY-MM-DD.md`

```markdown
# PR triage — [repo] — [date]

## Merge order
1. #… — reason
2. #…

## Table

| PR | Author | Bucket | CI | Overlaps | Notes | Action |
|----|--------|--------|----|-----------|-------|--------|
| #42 | @jules[bot] | Blocked | failing | #38 (`src/foo.ts`) | … | Merge after #38 |

Buckets: **Merge-ready** | **Needs review** | **Blocked** | **Reject**
```

See [examples.md](examples.md) for a filled-in sample.

## Workflows

### 1. Triage — assess all open PRs

**Step 1 — Gather (one pass):**
- [ ] `gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files --limit 100`
- [ ] For each PR: `gh pr diff <number>` — complete all diffs before concluding
- [ ] Optional overlap report: save JSON to scratch, run `python scripts/pr-overlap.py scratch/prs.json` (see [reference.md](reference.md))
- [ ] Helper scripts and intermediate JSON stay in scratch — never commit to the repo

**Step 2 — Analyse:**
- [ ] AI checklist on every AI-generated PR
- [ ] If `files` is empty or `gh pr diff` is empty, verify using `git show <head-sha> --stat`. If diff is truly empty, classify into **Reject** bucket and close with an explanation.
- [ ] File overlaps and duplicates per [reference.md](reference.md#overlap-and-duplicates)
- [ ] **Semantic conflict pairs** — check for non-git logical conflicts between PRs:
  - **Behavior vs test PRs** — one PR removes/changes an API/behavior, while another adds tests for that old behavior (targeting the same component/file).
  - **Logging vs assertions** — one PR silences or removes errors/logging, while another asserts `console.error` or specific log output.
  - Action: Flag as **Blocked** until resolved, combined, or reordered (e.g. implementing the behavior change first, or merging as a single PR).
- [ ] Classify each PR (buckets below)

**Step 3 — Deliver plan:**
- [ ] Write triage doc using template above
- [ ] Wait for user confirmation before any merge/close/approve

**Buckets:**

| Bucket | Criteria |
|--------|----------|
| Merge-ready | CI passing, approved, `mergeable` not `CONFLICTING`, not draft |
| Needs review | No approval yet, or changes requested |
| Blocked | CI failing, conflicts, file overlap, or semantic conflicts with another open PR |
| Reject | Stale, out of scope, duplicate/subset, empty diff/commit, or unfixable quality |

**Merge order:**
- Fixes before features; smaller before larger; unblock dependencies first.
- When two PRs overlap, merge the simpler one first.
- For the same file: merge **production code** before **tests** that target old behavior, or merge only the PR that combines/handles both correctly.
- When one PR removes behavior and another tests that removed behavior: **close/rebase** the test PR; do not merge both.

### 2. Review — read and comment on a PR

- [ ] `gh pr diff <number>` and `gh pr view <number> --comments`
- [ ] AI checklist if AI-generated
- [ ] Standard rubric
- [ ] Post review: `gh pr review <number> --comment --body "..."` (or `--approve` / `--request-changes`)
- [ ] State verdict using table above — do not merge unless user asked

### 3. Auto-merge — review and merge one PR

Only when the user explicitly requests auto-merge or "merge if clean" for **one** PR.

- [ ] Full workflow 2
- [ ] All [safety rules](#safety-rules) pass
- [ ] `gh pr review <number> --approve`
- [ ] `gh pr merge <number> --squash --delete-branch` (or method per [reference.md](reference.md#merge-methods))
- [ ] Verify: `gh pr view <number> --json state,mergedAt`
- [ ] If not approve → stop; do not merge

### 4. Merge — already-approved PR

- [ ] `gh pr view <number> --json isDraft,mergeable,reviewDecision,statusCheckRollup`
- [ ] Safety rules pass
- [ ] `gh pr merge <number> --squash --delete-branch` (default; see reference for alternatives)
- [ ] Verify merged state (same as workflow 3)

### 5. Handle rejected PRs

**Fixable** — comment with exact fixes; leave open:
`gh pr comment <number> --body "..."`

**Duplicate / subset** — close naming the winning PR:
`gh pr close <number> --comment "Closing in favour of #X …"`

**Out of scope / unrecoverable** — close with clear reason (always comment)

### 6. Execute merge plan

After user confirms workflow 1 plan:

- [ ] Task list: one item per merge, comment, or close
- [ ] Sequential execution; `gh pr update-branch <number>` when branch is behind base. If `gh pr update-branch` is unavailable in the environment, fallback to:
  - `gh api repos/{owner}/{repo}/pulls/{number}/update-branch -f merge_method=rebase` (when enabled on the repository), or
  - Note in the execution report that the branch will merge with a merge commit, or that manual rebasing is required.
- [ ] Re-check safety rules before each merge
- [ ] On failure → stop and report; do not continue

After the last merge (Post-merge verification):
- [ ] `git checkout main && git pull` (or the default base branch)
- [ ] Run the repository test command (e.g., `npm test`, `npm run test`, or equivalent test script). If tests fail, stop and repair the failure before declaring completion.
- [ ] Formulate and deliver an [Execution report](#execution-report) listing merged count, closed count, final test result, and any direct commits made to repair the branch.

## Execution report template

When delivering the final status after executing a merge plan:

```markdown
### Execution report
- **Merged**: #… (in order: squash/rebase)
- **Closed**: #… (reason: empty/duplicate/bad-logic)
- **Skipped**: #… (reason: conflicts/needs manual work)
- **Post-merge verification**:
  - Tests run: [pass/fail]
  - Commits pushed to main: e.g. `04371ee` (repair of failing test)
```

## Safety rules

- Never merge a draft (`isDraft: true`)
- Never merge if required CI checks are failing (if branch protection is unclear, list failing checks and ask)
- If `statusCheckRollup` is empty and no required checks are configured on the repo: treat as **no CI gate**. Require local test runs (`npm test` or equivalent) before and after batch merges, and note in the triage table CI column as `none (local only)`.
- Never merge to a non-default base without user confirmation
- Always comment when closing a PR (authors may be agents that read comments to self-correct)
- Batch merges only after explicit user approval of the triage plan

## Additional resources

- [examples.md](examples.md) — sample triage table and review comment
- [reference.md](reference.md) — CI fields, merge methods, overlap/duplicate rules, overlap script
