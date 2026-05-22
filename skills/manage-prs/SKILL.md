---
name: manage-prs
description: Review, triage, approve, reject, and merge GitHub pull requests, including AI-generated PRs. Use when the user wants to review PRs, merge a PR, assess all open PRs, close a bad PR, request changes, auto-merge clean PRs, or plan a merge strategy across a repository.
---

# Manage PRs

PRs in this repo may be authored by an AI agent (e.g. Jules). Apply extra scrutiny to AI-generated PRs — see the AI-generated PR checklist below.

## Quick start

```bash
# List open PRs
gh pr list

# Review a specific PR
gh pr diff 42
gh pr view 42 --comments
```

## AI-generated PR checklist

Run this **before** the standard review rubric when the PR author is an AI agent (e.g. Jules).

- **Hallucinated imports / functions** — do all imported modules, functions, and types actually exist in the codebase? `grep` for any unfamiliar identifiers.
- **Over-scoping** — does the diff touch more files than the task description justifies? Flag any changes unrelated to the stated goal.
- **Cross-PR conflicts** — does this PR overlap with another open PR on the same files? Check the file list from triage.
- **Invented APIs** — does the code call methods on libraries that don’t match the installed version? Check `package.json` / lockfile.
- **Plausible-but-wrong logic** — AI code often compiles and passes linting but has subtle logic errors. Read the core logic path carefully, not just the diff surface.
- **Committed artefacts** — check for files that should not be in source control: `.orig`, `.diff`, debug output, temp files. If present → comment and ask the agent to remove them before merging.

## Standard review rubric

- **Correctness** — does the code do what the PR description claims?
- **Tests** — are new behaviours covered? Are existing tests still passing?
- **Breaking changes** — does it change a public API, config format, or DB schema without a migration path?
- **Scope creep** — does the diff contain unrelated changes? Flag them.
- **Security** — any hardcoded secrets, unchecked inputs, or new dependencies with known vulnerabilities?
- **Style** — consistent with surrounding code? (Don’t block on nits — comment but approve.)

## Workflows

### 1. Triage — assess all open PRs

Run when asked to "review open PRs" or "plan merges".

**Step 1 — Gather all PR data in one pass:**
- [ ] `gh pr list --json number,title,author,reviewDecision,statusCheckRollup,isDraft,baseRefName,files --limit 100`
- [ ] For each PR, run `gh pr diff <number>` — do all diffs before drawing any conclusions
- [ ] If you need a helper script to process the data (e.g. overlap matrix), write it to a scratch/temp folder and run it from there — these are throwaway scripts and must never be committed to the repo
- [ ] Any intermediate data files (e.g. JSON output) go in the same scratch folder

**Step 2 — Analyse:**
- [ ] Run the AI-generated PR checklist above on any PR authored by an AI agent
- [ ] Identify cross-PR file overlaps: any two PRs touching the same file are a dependency pair
- [ ] Identify duplicates and subsets (identical diffs, or one diff is a subset of another)
- [ ] Classify each PR into one of four buckets (see below)

**Step 3 — Save plan for review:**
- [ ] Write the triage table and recommended merge order to a file (e.g. `implementation_plan.md`) so the user can review it
- [ ] Wait for user confirmation before acting on any PR

**Buckets:**

| Bucket | Criteria |
|---|---|
| ✅ **Merge-ready** | CI passing, approved, no conflicts, not draft |
| 🔍 **Needs review** | No review yet, or changes requested |
| ⚠️ **Blocked** | CI failing, merge conflicts, or overlaps with another open PR |
| 🗑️ **Reject** | Stale, out of scope, fixable quality issue, or duplicate |

**Merge order heuristic:** fixes before features, smaller PRs before larger, unblock dependencies first. When two PRs overlap, merge the simpler one first.

### 2. Review — read and comment on a PR

- [ ] `gh pr diff <number>` — read the full diff
- [ ] `gh pr view <number> --comments` — read existing discussion
- [ ] If PR is AI-generated, run the AI-generated PR checklist above first
- [ ] Evaluate against the standard review rubric above
- [ ] Post a structured review comment via `gh pr review <number> --comment --body "..."`
- [ ] Conclude with a clear verdict: **approve**, **request changes**, or **reject**

### 3. Auto-merge — review and merge in one step

Use when a PR looks clean and you want to approve and merge without a separate confirmation.

- [ ] Run the full Review checklist (workflow 2)
- [ ] If verdict is **approve** and all safety rules pass:
  - [ ] `gh pr review <number> --approve`
  - [ ] `gh pr merge <number> --squash --delete-branch`
  - [ ] Confirm success to user
- [ ] If verdict is anything other than **approve**, stop and report to user — do not merge

### 4. Merge — merge an already-approved PR

- [ ] Confirm PR is not a draft: `gh pr view <number> --json isDraft`
- [ ] Confirm CI is passing: check `statusCheckRollup` — abort if any required check fails
- [ ] Confirm at least one approval: check `reviewDecision`
- [ ] Confirm no conflicts: `mergeable` must not be `CONFLICTING`
- [ ] Choose merge method: `--squash` for feature branches, `--merge` for release branches, `--rebase` if user requests
- [ ] `gh pr merge <number> --squash --delete-branch`
- [ ] Confirm success to user

### 5. Handle rejected PRs

Not all rejections are the same — pick the right response:

**Fixable quality issue** (e.g. committed artefacts, wrong scope, bad logic)
- [ ] Leave a comment explaining exactly what needs fixing: `gh pr comment <number> --body "..."`
- [ ] Leave the PR open so the author can fix and repush

**Duplicate or subset** (another open PR covers the same change)
- [ ] Close with a comment naming the PR that was merged instead: `gh pr close <number> --comment "Closing in favour of #X which covers the same change."`

**Genuinely out of scope or unrecoverable**
- [ ] Close with a comment: `gh pr close <number> --comment "..."`

### 6. Execute a merge plan — run approved merges sequentially

Run after the user has confirmed the triage plan from workflow 1.

- [ ] Write a task list with one item per planned action (merge, comment, close)
- [ ] Execute the actions in order; rebase with `gh pr update-branch <number>` before merging if needed
- [ ] If a step fails, stop and report to the user — do not continue

## Safety rules

- Never merge a draft PR (`isDraft: true`)
- Never merge if any required CI check is failing
- Never merge into a non-default base branch without confirming with the user
- Always leave a comment when closing any PR, regardless of reason — the author may be an AI agent that reads comments to self-correct
- Always present a plan and wait for user approval before merging multiple PRs in one go
