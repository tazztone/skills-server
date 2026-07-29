# Skills Server

The canonical home for all agent skills — both the skill definitions and the FastMCP server that exposes them over MCP.

Skills are compatible with any agent that supports the [skills.sh](https://skills.sh/docs) open format (Cursor, Copilot, Claude, Gemini CLI, Aider, and others).

## Skill Index

| Slug | Description | Install Command |
|------|-------------|-----------------|
| [`agentic-engineering`](./skills/agentic-engineering/SKILL.md) | Transition from casual vibe coding to disciplined agentic engineering | `npx skills add tazztone/skills-server/skills --skill agentic-engineering` |
| [`agy-delegate`](./skills/agy-delegate/SKILL.md) | Delegate coding tasks to Google Antigravity CLI (`agy`) as a background implementer with structured status handling and worktree safety | `npx skills add tazztone/skills-server/skills --skill agy-delegate` |
| [`create-agentsmd`](./skills/create-agentsmd/SKILL.md) | Generate a minimal, high-signal `AGENTS.md` file at the repository root | `npx skills add tazztone/skills-server/skills --skill create-agentsmd` |
| [`davinci-resolve`](./skills/davinci-resolve/SKILL.md) | Scripting, automation, and plugin development for DaVinci Resolve (Python/Lua, Electron, Fuses) | `npx skills add tazztone/skills-server/skills --skill davinci-resolve` |
| [`gnome-extension-dev`](./skills/gnome-extension-dev/SKILL.md) | Build, debug, and package GNOME Shell extensions using GJS and ESModules | `npx skills add tazztone/skills-server/skills --skill gnome-extension-dev` |
| [`manage-prs`](./skills/manage-prs/SKILL.md) | Triage, review, and merge multiple GitHub PRs in structured, safe batches | `npx skills add tazztone/skills-server/skills --skill manage-prs` |
| [`signal-stickers`](./skills/signal-stickers/SKILL.md) | Prepare, design, and upload custom animated/static sticker packs to Signal | `npx skills add tazztone/skills-server/skills --skill signal-stickers` |

## Detailed Skill Overviews

### 🤖 [agentic-engineering](./skills/agentic-engineering/SKILL.md)
* **Purpose**: Process guide to transition from casual vibe coding (ad-hoc prompting) to disciplined agentic engineering (using models within structured constraints, feedback loops, and verification gates).
* **Install**:
  ```bash
  npx skills add tazztone/skills-server/skills --skill agentic-engineering
  ```
* **Key Features**:
  - **Spec & Design Intent First**: Stop immediate implementation, decompose tasks, and design unit/integration tests before writing code.
  - **Harness Setup**: Configure static context rules (`AGENTS.md`), MCP tools, sandboxes, and observability.
  - **Context Optimization**: Keep static context footprints low, and push complex procedures to Dynamic Context (skills/scripts).
  - **Factory Loop**: Run a continuous development loop (generate-test-correct) and setup evals for non-deterministic results.
  - **QA & Error Audit**: Audit logic paths, swallowed errors, and hallucinated dependencies.

### ⚡ [agy-delegate](./skills/agy-delegate/SKILL.md)
* **Purpose**: Delegate bounded coding tasks to the Google Antigravity CLI (`agy`) as a background implementer, while maintaining strict orchestrator review, dirty-worktree protection, and explicit execution tracking. (Based on [amElnagdy/delegate-skills](https://github.com/amElnagdy/delegate-skills/tree/master/skills/agy-delegate) with custom relay tweaks).
* **Install**:
  ```bash
  npx skills add tazztone/skills-server/skills --skill agy-delegate
  ```
* **Key Features**:
  - **Relay Dispatcher (`relay.mjs`)**: Wraps `agy --print` to run tasks asynchronously and output a structured `result.json` report.
  - **Granular Execution Statuses**: Distinguishes `completed`, `completed_without_report`, `blocked_by_permission`, and `failed` states rather than relying on CLI exit codes alone.
  - **Worktree Baseline Protection**: Refuses execution in dirty worktrees by default (overrideable via `--allow-dirty`) and records `baselineTouchedFiles` to cleanly isolate changes.
  - **Permission & Preflight Diagnostics**: Detects permission denial messages and sandboxing requirements without misrepresenting blocked runs as successful.
  - **Explicit Session Retries**: Prefers `--conversation <id>` retry targeting over `--resume-last` session guessing.

### 📑 [create-agentsmd](./skills/create-agentsmd/SKILL.md)
* **Purpose**: Automatically generates a minimal, high-signal `AGENTS.md` file at the root of a repository. It filters out obvious or already documented instructions, capturing only critical, uninferable rules to prevent AI agents from running into common mistakes.
* **Install**:
  ```bash
  npx skills add tazztone/skills-server/skills --skill create-agentsmd
  ```
* **Key Features**:
  - Uses the **Three-Condition Filter**: Instructions must be *uninferable* (cannot be guessed), *critical* (prevents failure), and *undocumented* (not found in other files).
  - Automatically audits project layouts, configurations, and dependency manifests.
  - Verifies commands in the shell to ensure they are correct before adding them.

### 🎬 [davinci-resolve](./skills/davinci-resolve/SKILL.md)
* **Purpose**: Comprehensive handbook for scripting, automation, and plugin/fuse development for DaVinci Resolve.
* **Install**:
  ```bash
  npx skills add tazztone/skills-server/skills --skill davinci-resolve
  ```
* **Key Features**:
  - **Scripting API**: Integrations using Python 3.6–3.12 and Lua to automate project timelines, media ingestion, color grading, and rendering.
  - **Workflow Integrations**: Creating Studio-only custom Electron (JS) panels inside the Resolve UI.
  - **Fusion Fuse Plugins**: Creating custom image-processing and effect nodes using Lua.
  - Documents API boundaries, known quirks (like 1-based node indexing), and OS-specific setup steps.

### 👤 [gnome-extension-dev](./skills/gnome-extension-dev/SKILL.md)
* **Purpose**: Comprehensive handbook for creating, testing, debugging, and packaging GNOME Shell extensions (45+) using GJS with ESModules.
* **Install**:
  ```bash
  npx skills add tazztone/skills-server/skills --skill gnome-extension-dev
  ```
* **Key Features**:
  - **Extension Components**: Design patterns for St widgets, Clutter layout, Quick Settings toggles, panel buttons, and popup menus.
  - **Preferences (GTK4/Adwaita)**: Subclassing `ExtensionPreferences` and binding GSettings schemas to GTK/Adwaita settings controls.
  - **Advanced Topics**: Calling or exposing D-Bus services and managing localization with Gettext (PO/MO translations).
  - **TypeScript & LSP Autocomplete**: Setting up editor autocompletion with `@girs/gnome-shell` type definitions.
  - **Local Deployment & Testing**: Deploying locally and running isolated nested GNOME Shell instances (`dbus-run-session`) for testing.

### 🔀 [manage-prs](./skills/manage-prs/SKILL.md)
* **Purpose**: Orchestrates a complete, safe workflow to batch triage, review, and merge multiple GitHub PRs with conflict resolution and verification.
* **Install**:
  ```bash
  npx skills add tazztone/skills-server/skills --skill manage-prs
  ```
* **Key Features**:
  - **Phase-Gated Process**: Runs from collection/analysis to planning, local merge execution, and final test suite verification.
  - **Conflict Resolution**: Safely handles git conflicts locally and checks for overlapping changes between pull requests.
  - **Safe Execution**: Uses explicit command guidelines to avoid shell bugs (e.g. avoiding segfaulting commands like `gh pr checkout`).
  - **Interactive Gate**: Ensures human approval via an `implementation_plan.md` artifact before any branch modifications or merges are made.

### 🎨 [signal-stickers](./skills/signal-stickers/SKILL.md)
* **Purpose**: Design, formatting, and publishing handbook for creating and uploading custom static and animated sticker packs to Signal.
* **Install**:
  ```bash
  npx skills add tazztone/skills-server/skills --skill signal-stickers
  ```
* **Key Features**:
  - **Canvas & File Requirements**: Guides on canvas sizing (512x512px), file formats (PNG, WebP, APNG), size limits (300KB), and animation duration limits (3s max, no GIFs).
  - **Best Practices**: Safe zones/margins, transparency, and stroke outlines for seamless rendering in both light and dark modes.
  - **Publishing**: Assigning emojis to stickers for in-chat auto-suggestions, and uploading packs via Signal Desktop.


## Structure

```
skills-server/
  my_server.py        # FastMCP server entry point
  requirements.txt
  skills/
    <skill-name>/
      SKILL.md        # One folder per skill — add as many as you like
```

The server uses `SkillsDirectoryProvider`, which auto-discovers every subdirectory under `skills/`. To add a new skill, just create a new folder with a `SKILL.md` inside — no server changes needed.

## Add a skill

Create a new subfolder under `skills/` with a `SKILL.md` file inside:

```yaml
---
name: your-slug
description: 'One sentence covering WHAT it does AND WHEN to use it.'
---

# Skill instructions here
```

## Run locally

```bash
pip install -r requirements.txt
fastmcp run my_server.py:mcp
```

## Deploy

Connect this repo to [Prefect Horizon](https://www.prefect.io/horizon/deploy) and use `my_server.py:mcp` as the entrypoint.

## Installation & Usage (`npx skills`)

Skills from this repository can be installed or run using the [`skills.sh`](https://skills.sh) CLI.

### List available skills in this repo
```bash
npx skills add tazztone/skills-server/skills --list
```

### Install skills
```bash
# Interactive install (select skills and target agents)
npx skills add tazztone/skills-server/skills

# Install all skills for all agents automatically
npx skills add tazztone/skills-server/skills --all

# Install a specific skill from this repo
npx skills add tazztone/skills-server/skills --skill agy-delegate
npx skills add tazztone/skills-server/skills --skill create-agentsmd
npx skills add tazztone/skills-server/skills --skill manage-prs

# Install globally (user-level) instead of project-level
npx skills add tazztone/skills-server/skills -g
```

### Use a skill without installing
```bash
npx skills use tazztone/skills-server/skills@manage-prs
npx skills use tazztone/skills-server/skills@create-agentsmd
```

## References

- [skills.sh docs](https://skills.sh/docs) — CLI reference, install commands, leaderboard
- [vercel-labs/skills](https://github.com/vercel-labs/skills) — the open-source CLI

