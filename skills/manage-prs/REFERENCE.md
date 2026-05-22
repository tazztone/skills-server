# Manage PRs — Reference

## AI-generated PR checklist

Run this **before** the standard review rubric when the PR author is an AI agent (e.g. Jules).

- **Hallucinated imports / functions** — do all imported modules, functions, and types actually exist in the codebase? `grep` for any unfamiliar identifiers.
- **Over-scoping** — does the diff touch more files than the task description justifies? Flag any changes unrelated to the stated goal.
- **Cross-PR conflicts** — does this PR overlap with another open PR on the same files? Check the file list from triage.
- **Invented APIs** — does the code call methods on libraries that don't match the installed version? Check `package.json` / lockfile.
- **Plausible-but-wrong logic** — AI code often compiles and passes linting but has subtle logic errors. Read the core logic path carefully, not just the diff surface.
- **Committed artefacts** — check for files that should not be in source control: `.orig`, `.diff`, debug output, temp files. If present → reject and ask the agent to remove them.

If any of these fail → **reject**, not just request-changes. AI agents should rewrite from scratch, not patch.

## Standard review rubric

- **Correctness** — does the code do what the PR description claims?
- **Tests** — are new behaviours covered? Are existing tests still passing?
- **Breaking changes** — does it change a public API, config format, or DB schema without a migration path?
- **Scope creep** — does the diff contain unrelated changes? Flag them.
- **Security** — any hardcoded secrets, unchecked inputs, or new dependencies with known vulnerabilities?
- **Style** — consistent with surrounding code? (Don't block on nits — comment but approve.)

## Merge method guide

| Situation | Flag | Reason |
|---|---|---|
| Feature branch into main | `--squash` | Clean linear history |
| Release / long-lived branch | `--merge` | Preserves full commit context |
| User requests linear history | `--rebase` | No merge commit |

## Cross-PR conflict resolution

If PR A and PR B both touch the same files, merge the smaller/simpler one first, then rebase the other:

```bash
gh pr checkout <larger-pr-number>
git fetch origin main
git rebase origin/main
git push --force-with-lease
```

Re-run CI after the rebase before merging.
