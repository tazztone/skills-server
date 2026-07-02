# Skills Server

The canonical home for all agent skills — both the skill definitions and the FastMCP server that exposes them over MCP.

Skills are compatible with any agent that supports the [skills.sh](https://skills.sh/docs) open format (Cursor, Copilot, Claude, Gemini CLI, Aider, and others).

## Skill Index

| Slug | Description |
|------|-------------|
| [`create-agentsmd`](./skills/create-agentsmd/SKILL.md) | Generate a minimal, high-signal `AGENTS.md` file at the repository root |
| [`agentic-engineering`](./skills/agentic-engineering/SKILL.md) | Transition from casual vibe coding to disciplined agentic engineering |
| [`davinci-resolve`](./skills/davinci-resolve/SKILL.md) | Scripting, automation, and plugin development for DaVinci Resolve (Python/Lua, Electron, Fuses) |
| [`gnome-extension-dev`](./skills/gnome-extension-dev/SKILL.md) | Build, debug, and package GNOME Shell extensions using GJS and ESModules |
| [`manage-prs`](./skills/manage-prs/SKILL.md) | Triage, review, and merge multiple GitHub PRs in structured, safe batches |
| [`signal-stickers`](./skills/signal-stickers/SKILL.md) | Prepare, design, and upload custom animated/static sticker packs to Signal |

## Detailed Skill Overviews

### 📑 [create-agentsmd](./skills/create-agentsmd/SKILL.md)
* **Purpose**: Automatically generates a minimal, high-signal `AGENTS.md` file at the root of a repository. It filters out obvious or already documented instructions, capturing only critical, uninferable rules to prevent AI agents from running into common mistakes.
* **Key Features**:
  - Uses the **Three-Condition Filter**: Instructions must be *uninferable* (cannot be guessed), *critical* (prevents failure), and *undocumented* (not found in other files).
  - Automatically audits project layouts, configurations, and dependency manifests.
  - Verifies commands in the shell to ensure they are correct before adding them.

### 🤖 [agentic-engineering](./skills/agentic-engineering/SKILL.md)
* **Purpose**: Process guide to transition from casual vibe coding (ad-hoc prompting) to disciplined agentic engineering (using models within structured constraints, feedback loops, and verification gates).
* **Key Features**:
  - **Spec & Design Intent First**: Stop immediate implementation, decompose tasks, and design unit/integration tests before writing code.
  - **Harness Setup**: Configure static context rules (`AGENTS.md`), MCP tools, sandboxes, and observability.
  - **Context Optimization**: Keep static context footprints low, and push complex procedures to Dynamic Context (skills/scripts).
  - **Factory Loop**: Run a continuous development loop (generate-test-correct) and setup evals for non-deterministic results.
  - **QA & Error Audit**: Audit logic paths, swallowed errors, and hallucinated dependencies.

### 🎬 [davinci-resolve](./skills/davinci-resolve/SKILL.md)
* **Purpose**: Comprehensive handbook for scripting, automation, and plugin/fuse development for DaVinci Resolve.
* **Key Features**:
  - **Scripting API**: Integrations using Python 3.6–3.12 and Lua to automate project timelines, media ingestion, color grading, and rendering.
  - **Workflow Integrations**: Creating Studio-only custom Electron (JS) panels inside the Resolve UI.
  - **Fusion Fuse Plugins**: Creating custom image-processing and effect nodes using Lua.
  - Documents API boundaries, known quirks (like 1-based node indexing), and OS-specific setup steps.

### 👤 [gnome-extension-dev](./skills/gnome-extension-dev/SKILL.md)
* **Purpose**: Comprehensive handbook for creating, testing, debugging, and packaging GNOME Shell extensions (45+) using GJS with ESModules.
* **Key Features**:
  - **Extension Components**: Design patterns for St widgets, Clutter layout, Quick Settings toggles, panel buttons, and popup menus.
  - **Preferences (GTK4/Adwaita)**: Subclassing `ExtensionPreferences` and binding GSettings schemas to GTK/Adwaita settings controls.
  - **Advanced Topics**: Calling or exposing D-Bus services and managing localization with Gettext (PO/MO translations).
  - **TypeScript & LSP Autocomplete**: Setting up editor autocompletion with `@girs/gnome-shell` type definitions.
  - **Local Deployment & Testing**: Deploying locally and running isolated nested GNOME Shell instances (`dbus-run-session`) for testing.

### 🔀 [manage-prs](./skills/manage-prs/SKILL.md)
* **Purpose**: Orchestrates a complete, safe workflow to batch triage, review, and merge multiple GitHub PRs with conflict resolution and verification.
* **Key Features**:
  - **Phase-Gated Process**: Runs from collection/analysis to planning, local merge execution, and final test suite verification.
  - **Conflict Resolution**: Safely handles git conflicts locally and checks for overlapping changes between pull requests.
  - **Safe Execution**: Uses explicit command guidelines to avoid shell bugs (e.g. avoiding segfaulting commands like `gh pr checkout`).
  - **Interactive Gate**: Ensures human approval via an `implementation_plan.md` artifact before any branch modifications or merges are made.

### 🎨 [signal-stickers](./skills/signal-stickers/SKILL.md)
* **Purpose**: Design, formatting, and publishing handbook for creating and uploading custom static and animated sticker packs to Signal.
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

## References

- [skills.sh docs](https://skills.sh/docs) — CLI reference, install commands, leaderboard
- [vercel-labs/skills](https://github.com/vercel-labs/skills) — the open-source CLI
