# Dispatch and poll

`scripts/relay.mjs` is the dispatch layer. It wraps `agy --print`, runs the brief in Antigravity,
captures the final response, and writes a structured `result.json`. Your job collapses to: run one
command, then read one file.

## Before the first run: check the binary and permissions

```bash
command -v agy
agy help
agy models
```

- `agy help` confirms the binary is installed and operational.
- `agy models` proves the CLI can authenticate, list available model labels, write logs, and open local sockets outside the sandbox.
- **Headless Permissions:** Ensure `permissions.allow` rules exist for command and file operations. Antigravity headless mode requires explicit command approvals (e.g., `command(*)` or specific command rules). `--sandbox` mode alone does not guarantee execution if commands are blocked by permissions.
- **Managed Cache Directories:** In environments where default user caches (such as `~/.cache/uv`) are read-only, set `UV_CACHE_DIR=/tmp/...` in the execution environment prior to running tool commands.
- The relay records the version it can infer from `agy changelog` into `result.json`.

## Dispatching

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
```

(`<skill-dir>` is wherever this skill is installed - the folder containing its `SKILL.md`.)

Options:

| Flag | Effect |
| --- | --- |
| `--brief <file>` | The brief. Omit it to read the brief from stdin before passing it to `agy --print`. |
| `--cd <dir>` | Working root for Antigravity (default: current directory). |
| `--model <name>` | Antigravity model label. Optional; a fresh run can use Antigravity's configured default. |
| `--project <id>` | Use an existing Antigravity project. |
| `--new-project` | Force a fresh Antigravity project. This is the default for fresh dispatches. |
| `--resume-last` | Continue the most recent Antigravity conversation; send only the delta brief. |
| `--conversation <id>` | Continue a specific Antigravity conversation; send only the delta brief. |
| `--sandbox` | Enable Antigravity's terminal sandbox for the run. |
| `--allow-dirty` | Allow dispatch from a non-clean git worktree; the baseline is recorded in `result.json`. |
| `--dangerously-skip-permissions` | Pass Antigravity's permission-bypass flag. Never use this unless the human explicitly accepts it. |
| `--print-timeout <duration>` | Timeout for print mode (default: `30m`). |
| `--add-dir <dir>` | Add an extra workspace directory. Repeatable; relative paths resolve against `--cd`. Fresh runs always add the `--cd` repo (absolute path) as a workspace dir. Edits inside extra workspaces are not reported in `touchedFiles`. |
| `--out-dir <dir>` | Where artifacts go (default: a fresh dir under the system temp dir). |

Artifacts default to the system temp dir on purpose: the repo under review stays clean, so under the
default clean-baseline mode the touched-files report shows only Antigravity's edits and nothing of the
helper's own. With `--allow-dirty`, compare it with `baselineTouchedFiles`.

## The result

`<out-dir>/result.json` is the contract. Fields:

- `schema` - the result-format version (currently `delegate-relay.result.v1`)
- `tool` - `agy`
- `status` - `completed` | `completed_without_report` | `blocked_by_permission` | `failed` | `timeout` | `aborted` | `agy_unavailable`
- `exitCode` - mirrors Antigravity's exit code; `128` plus the signal number if the child was killed; `127` if `agy` is not on PATH; on a `timeout` the relay forces a non-zero code even when the child exited `0` after the watchdog's SIGTERM
- `signal` - the signal that killed the child, otherwise `null`
- `agyVersion` - inferred from `agy changelog` when available
- `projectId` / `conversationId` - parsed from the Antigravity log when present
- `finalMessage` - Antigravity's stdout response
- `touchedFiles` - `git status --porcelain` lines in the working root: your review starting point.
  `null` (not `[]`) when git cannot report; `[]` means git ran and the tree is clean
- `baselineTouchedFiles` - the worktree status captured before dispatch. It is empty for the default
  clean-baseline mode and may be non-empty only with `--allow-dirty`.
- `briefPath` / `finalPath` / `logPath` / `stderrPath` - the exact brief, final message, Antigravity
  log, and stderr capture
- `workdir`, `model`, `project` (the `--project` you passed, vs `projectId` parsed from the log),
  `sandbox`, `dangerouslySkipPermissions`, `resumed` (true for a `--resume-last` or `--conversation`
  run), `startedAt`, `finishedAt`
- `stderrTail` - last ~20 stderr lines; present on every run that did not complete (`failed`, `timeout`, `aborted`), except a launch failure, which reports `failed` with no `stderrTail`
- `error` - present on a launch failure, incomplete handoff (`completed_without_report` or
  `blocked_by_permission`), `timeout`, and `aborted` runs

The helper also prints a summary to stdout and exits non-zero for incomplete or failed relay outcomes,
including `completed_without_report` and `blocked_by_permission`, so a wrapping script can branch on
the relay's verified handoff status directly.

## Waiting for completion

The helper blocks until Antigravity finishes. Back it with whatever your orchestrator offers:

- **Claude Code:** run the Bash call with `run_in_background: true`; you're notified on completion,
  then read `result.json`.
- **Plain shell / other agents:** foreground for short tasks, or background and poll. A run is done
  when `result.json` exists with a `status`. A pre-run usage error exits with code 2 before writing any
  file, so check the exit code too. A missing `agy` binary exits 127 and writes `result.json` with
  `status: agy_unavailable`.

Trust the working tree and the process state over any progress display. A run is finished when the
process has exited and `result.json` is written.

## When a run misbehaves

- **`status: agy_unavailable` (exit 127):** `agy` is not on PATH. Install the Antigravity CLI and run
  its first-launch setup, then re-dispatch.
- **`status: timeout`:** the `--print-timeout` watchdog killed the run. The working tree may hold a
  half-applied change — inspect it before deciding between a longer `--print-timeout`, a smaller
  brief, or a resume.
- **`status: aborted`:** the relay itself was killed (its parent's timeout, a stopped task, a
  closed terminal) and forwarded the kill to agy. The result is written before the relay exits;
  inspect the working tree before re-dispatching. On native Windows a hard kill of the relay is
  uncatchable (Node supports no `SIGTERM` handler there), so this status may never get written -
  a relay process that is gone without a `result.json` is an aborted run; inspect the working
  tree and `events.jsonl` directly.
- **`status: failed` with `signal: "SIGKILL"`:** the host ended the child - commonly the OOM killer
  or a supervisor timeout, not an implementer error. Free up host memory or split the task into
  smaller briefs, then re-dispatch.
- **`status: failed`:** read `result.json`'s `stderrTail`, `stderrPath`, and `logPath` for the cause.
  Common causes: auth lapse, an unknown model label, timeout, or a permission the run needed.
- **`status: blocked_by_permission`:** inspect `stderrTail`, `stderrPath`, and `error`. Configure an
  Antigravity headless allow-rule or ask the human whether to re-run with
  `--dangerously-skip-permissions`; do not treat exit code `0` as completion.
- **`status: completed_without_report`:** agy exited zero but emitted no final report. Inspect the
  working tree, compare `baselineTouchedFiles` with `touchedFiles`, and review the logs before deciding
  whether to keep or re-dispatch.
- **Empty `finalMessage` with another status:** Antigravity finished without emitting a closing text
  summary. The edits may still be correct, but the result is not a complete handoff.

## What the helper is doing

Under the hood the helper runs roughly:

```bash
agy --new-project --add-dir <repo> --print-timeout 30m --print=<brief>
agy --continue --print-timeout 30m --print=<delta brief>
agy --conversation <id> --print-timeout 30m --print=<delta brief>
```

`agy --print` requires the prompt as a flag argument, so keep briefs focused. The relay still accepts
stdin or `--brief <file>` for your convenience; it reads the text first, then passes it to `agy` as
`--print=<brief>` (the `=` form so a brief that begins with a bare flag like `--help` still runs).
Two consequences of the brief riding the command line: it is visible in the host process list (`ps`),
so on a shared machine keep secrets out of it; and a brief over ~120 KB is rejected up front (the OS
caps a single argument), so have `agy` read large context from the workspace instead of inlining it.

## The commit boundary

The helper never commits - by design, not omission. The robust contract is: Antigravity edits the
working tree, the orchestrator reviews and commits. See [review-and-land.md](review-and-land.md).
