# Skills Server

A FastMCP server that serves `SKILL.md` files as MCP resources.

## Structure

```
skills-server/
  my_server.py        # FastMCP server entry point
  requirements.txt
  skills/
    <skill-name>/
      SKILL.md        # One folder per skill
```

## Add a skill

Create a new subfolder under `skills/` with a `SKILL.md` file inside.

## Run locally

```bash
pip install -r requirements.txt
fastmcp run my_server.py:mcp
```

## Deploy

Connect this repo to [Prefect Horizon](https://www.prefect.io/horizon/deploy) and use `my_server.py:mcp` as the entrypoint.
