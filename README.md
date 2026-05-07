# Skills Server

The canonical home for all agent skills — both the skill definitions and the FastMCP server that exposes them over MCP.

Skills are compatible with any agent that supports the [skills.sh](https://skills.sh/docs) open format (Cursor, Copilot, Claude, Gemini CLI, Aider, and others).

## Skill Index

| Slug | Description |
|------|-------------|
| [`create-agentsmd`](./skills/create-agentsmd/SKILL.md) | Generate a minimal, high-signal `AGENTS.md` — prioritizes brevity over completeness |
| [`davinci-resolve`](./skills/davinci-resolve/SKILL.md) | Scripting, automation, and plugin development for DaVinci Resolve (Python/Lua scripting API, Workflow Integrations, Fusion Fuses) |
| [`find-skills`](./skills/find-skills/SKILL.md) | Find and install agent skills from the skills.sh ecosystem |
| [`review`](./skills/review/SKILL.md) | Code review skill |
| [`skill-creator`](./skills/skill-creator/SKILL.md) | Create new skills, modify and improve existing skills, and measure skill performance with evals and benchmarks |

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
