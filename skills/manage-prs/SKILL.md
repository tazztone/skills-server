---
name: manage-prs
description: Review, triage, approve, reject, and merge GitHub pull requests, including AI-generated PRs. Use when the user wants to review PRs, merge a PR, assess all open PRs, close a bad PR, request changes, auto-merge clean PRs, or plan a merge strategy across a repository.
---

# Manage PRs

PRs in this repo may be authored by an AI agent (e.g. Jules). Apply extra scrutiny to AI-generated PRs — see the AI-generated PR checklist in [REFERENCE.md](REFERENCE.md).

## Quick start

```bash
# List open PRs
gh pr list

# Review a specific PR
gh pr diff 42
gh pr view 42 --comments
```

## Workflows

### 1. Triage — assess all open PRs

Run when asked to "review open PRs" or "plan merges".

**Step 1 — Read reference docs first:**
- [ ] Read [REFERENCE.md](REFERENCE.md) before reviewing any diff

**Step 2 — Gather all PR data in one pass:**
- [ ] `gh pr list --json number,title,author,reviewDecision,statusCheckRollup,isDraft,baseRefName,files --limit 100`
- [ ] For each PR, run `gh pr diff <number>` — do all diffs before drawing any conclusions
- [ ] If you need a helper script to process the data (e.g. overlap matrix), write it to `/tmp/process_prs.py` and run it from there — these are throwaway scripts and must never be committed to the repo
- [ ] If the script produces intermediate data (e.g. a JSON file), write that to `/tmp/` as well

**Step 3 — Analyse:**
- [ ] Identify cross-PR file overlaps: any two PRs touching the same file are a dependency pair
- [ ] Identify duplicates and subsets (identical diffs, or one diff is a subset of another)
- [ ] Classify each PR into one of four buckets (see below)

**Step 4 — Present plan in the chat:**
- [ ] Write the triage table and recommended merge order directly in your response to the user
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

- [ ] Read [REFERENCE.md](REFERENCE.md) if not already done
- [ ] `gh pr diff <number>` — read the full diff
- [ ] `gh pr view <number> --comments` — read existing discussion
- [ ] If PR is AI-generated, run the AI-generated PR checklist first (see [REFERENCE.md](REFERENCE.md))
- [ ] Evaluate against the standard review rubric (see [REFERENCE.md](REFERENCE.md))
- [ ] Post a structured review comment via `gh pr review <number> --comment --body "..."`
- [ ] Conclude with a clear verdict: **approve**, **request changes**, or **reject**

### 3. Auto-merge — review and merge in one step

Use when a PR looks clean and you want to approve and merge without a separate confirmation.

- [ ] Run the full Review checklist (workflow 2)
- [ ] If verdict is **approve** and all safety rules pass:
  - [ ] `gh pr review <number> --approve`
  - [ ] `gh pr merge <number> --squash --delete-branch` (adjust flag per method in [REFERENCE.md](REFERENCE.md))
  - [ ] Confirm success to user
- [ ] If verdict is anything other than **approve**, stop and report to user — do not merge

### 4. Merge — merge an already-approved PR

- [ ] Confirm PR is not a draft: `gh pr view <number> --json isDraft`
- [ ] Confirm CI is passing: check `statusCheckRollup` — abort if any required check fails
- [ ] Confirm at least one approval: check `reviewDecision`
- [ ] Confirm no conflicts: `mergeable` must not be `CONFLICTING`
- [ ] Choose merge method (see [REFERENCE.md](REFERENCE.md))
- [ ] `gh pr merge <number> --squash --delete-branch`
- [ ] Confirm success to user

### 5. Handle rejected PRs

Not all rejections are the same — pick the right response:

**Fixable quality issue** (e.g. committed artefacts, wrong scope, bad logic)
- [ ] Leave a comment explaining exactly what needs fixing: `gh pr comment <number> --body "..."`
- [ ] Leave the PR open so the author can fix and repush

**Duplicate or subset** (another open PR covers the same change)
- [ ] Merge the better PR; the duplicate will go stale on its own — no comment needed

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
- Never close a PR without leaving a comment explaining why
- Always present a plan and wait for user approval before merging multiple PRs in one go
