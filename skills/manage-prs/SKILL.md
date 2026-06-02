---
name: manage-prs
description: >
  Triage, review, and merge GitHub PRs, including AI-generated PRs.
  Use for batch triage or single PR merges.
disable-model-invocation: true
---

# Manage PRs

Use `gh` for all operations. Stop and ask the user on: 401, 403, 422, or network timeout.
Default merge method: `--squash --delete-branch`. Check `AGENTS.md` first — it overrides all merge method defaults.

---

## Gotchas & Landmines

### `--json comments` crashes `gh pr view`
Use `--json body,comments` — **not** the `--comments` flag. The flag crashes.

### `UNKNOWN` mergeability is a hard block
GitHub computes mergeability asynchronously and temporarily returns `UNKNOWN`. **Never merge `UNKNOWN`.**
Re-query with `gh pr view <n> --json mergeable` until it resolves to `MERGEABLE` before proceeding.

### `gh pr update-branch` does not exist
The native command `gh pr update-branch` will fail with an unknown command error.
* **Correct update path:** Always use the raw GitHub API endpoint:
  ```bash
  gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=squash
  ```
* **Fallback (rebase):** If a clean fast-forward update fails:
  ```bash
  gh api repos/{owner}/{repo}/pulls/{n}/update-branch -f merge_method=rebase
  ```

### `gh pr create` body must use `--body-file`
Never pipe PR body content via stdin or inline `--body`. Write to a temp file first:
```bash
BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/pr-body.XXXXXX")
cat > "$BODY_FILE" <<'__END__'
<body content here>
__END__
gh pr create --title "<TITLE>" --body-file "$BODY_FILE"
```

### Structural/cache-layer PRs are systemic blockers
PRs altering service workers (`sw.js`), architectural caching, or app-layer config have cascading side effects.
Group these, isolate the ideal structural layout first, and reject/close alternates — don't chain-merge blindly.

### Avoid sequential multi-query bloat
Do not re-fetch `gh pr list` and loop every metadata profile after every merge.
Group non-overlapping merge-ready PRs into a batch queue, test once, execute sequentially, sync at the end.

### Script path is runtime-dynamic
Do not assume a fixed install path for `pr-overlap.py`. Discover it at runtime:
```bash
python3 $(find ~ -name pr-overlap.py -maxdepth 8 2>/dev/null | head -1) prs.json
```
Fallback one-liner if the script is missing:
```bash
python3 -c "import json, collections; data = json.load(open('prs.json')); by_file = collections.defaultdict(list); [(by_file[f['path']].append(pr['number']) for f in pr.get('files', []) if isinstance(f, dict) and 'path' in f) for pr in data if 'number' in pr]; [print(f'{p}: {ns}') for p, ns in sorted(by_file.items(), key=lambda x: -len(x[1])) if len(ns) > 1]"
```

### `gh pr list` silently caps at 100
Always pass `--limit 100`. If the repo has more open PRs, warn the user — triage will be incomplete.

### Never merge without reading the diff
CI green is not sufficient. Always run `gh pr diff <n>` and verify the logic.

### Bot/AI PRs: verify imports and APIs
For automated PRs (e.g. Jules, Dependabot), `grep` any unfamiliar identifiers in the codebase before approving.
Do not trust the PR description alone.

### Always comment when closing
`gh pr close <n> --comment "Closing because..."` — never close silently.

---

## Batch Triage Workflow

### Step 1: Gather PRs
```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files \
  --limit 100 > prs.json
```
Also fetch open issues and read `AGENTS.md` for merge method overrides.

### Step 2: Batch by Theme
Group PRs into batches of 4–6 by type:
- Dependency bumps / automated (Dependabot, Jules, Renovate)
- Feature additions
- Bug fixes
- Refactors / style
- Structural / config / cache (high-risk — see landmine above)

### Step 3: Per-PR Health Check
For each PR, evaluate:
1. **Review readiness** — `reviewDecision` approved or required approvals met?
2. **Staleness** — last activity > N days? Ping author or close.
3. **Mergeability** — `MERGEABLE` / `CONFLICTING` / `UNKNOWN` (see landmine above)
4. **CI status** — all checks green? Any blocking failures?
5. **Diff read** — `gh pr diff <n>`: logic correct, no obvious breakage
6. **Bot/AI verification** — grep unfamiliar identifiers if automated author
7. **Overlap detection** — run overlap script against `prs.json`

### Step 4: Cross-Reference Issues
Match PRs to linked issues. Build mapping: `| Issue | PR | Relation |`

### Step 5: Triage Report
Group output into categories:
- ✅ **Merge-ready** — conflicts clear, CI green, diff verified, reviewed
- ⚠️ **Needs action** — blocked by conflict / CI failure / missing review
- 🔁 **Stale** — no activity > threshold; recommend ping or close
- 🔀 **Overlapping** — file conflict risk; list affected files
- 🤖 **Bot/AI PRs** — flagged items needing import/API verification
- ❌ **Close candidates** — superseded, duplicate, or abandoned

Walk through each PR one-by-one for merge / comment / close decision.

---

## Overlap Detection

```bash
gh pr list --json number,title,author,isDraft,mergeable,reviewDecision,statusCheckRollup,baseRefName,files \
  --limit 100 > prs.json
```
Then run the overlap script (see path discovery above).

---

## Additional Resources

- [scripts/pr-overlap.py](scripts/pr-overlap.py)
