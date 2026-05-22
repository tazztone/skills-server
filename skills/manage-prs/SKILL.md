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

- [ ] `gh pr list --json number,title,author,reviewDecision,statusCheckRollup,isDraft,baseRefName,files` — get full picture
- [ ] Check for cross-PR file overlap: if two PRs touch the same files, flag them as a dependency pair
- [ ] Classify each PR into one of four buckets (see below)
- [ ] Present the buckets to the user with a recommended merge order
- [ ] Wait for user confirmation before acting on any PR

**Buckets:**

| Bucket | Criteria |
|---|---|
| ✅ **Merge-ready** | CI passing, approved, no conflicts, not draft |
| 🔍 **Needs review** | No review yet, or changes requested |
| ⚠️ **Blocked** | CI failing, merge conflicts, or overlaps with another open PR |
| 🗑️ **Reject** | Stale, out of scope, duplicates another PR, or fails AI-generated PR checks |

**Merge order heuristic:** fixes before features, smaller PRs before larger, unblock dependencies first. When two PRs overlap, merge the simpler one first.

### 2. Review — read and comment on a PR

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

### 5. Reject — close a bad PR

- [ ] Post a review requesting changes: `gh pr review <number> --request-changes --body "..."`
- [ ] If clearly out of scope or a duplicate, close it: `gh pr close <number> --comment "..."`
- [ ] Use the rejection comment template below

**Rejection comment template:**

```markdown
**Reason for closing / requesting changes:**

- <specific reason>

**What would need to change to get this merged:**

- <actionable fix, or "this is out of scope because...">
```

## Safety rules

- Never merge a draft PR (`isDraft: true`)
- Never merge if any required CI check is failing
- Never merge into a non-default base branch without confirming with the user
- Never close a PR without leaving a comment explaining why
- Always present a plan and wait for user approval before merging multiple PRs in one go
