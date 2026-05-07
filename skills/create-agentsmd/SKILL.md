---
name: create-agentsmd
description: 'Generate a minimal, high-signal AGENTS.md for a repository. Prioritizes brevity over completeness — unnecessary context increases inference cost and reduces agent task success rates.'
---

# Create a minimal, high-signal AGENTS.md

You are a code agent. Your task is to create a concise, accurate AGENTS.md at the root of this repository.

> **Warning**: Comprehensive context files increase inference cost and reduce agent task success rates. Every line you add must clear a high bar. When in doubt, omit it.

AGENTS.md is an open format that gives coding agents the non-obvious, repo-specific context they need to work effectively — context that cannot be inferred by reading the code.

## What is AGENTS.md?

AGENTS.md is a Markdown file that serves as a "README for agents" — a predictable place for instructions that are not already discoverable from the codebase. It complements README.md without duplicating it.

## Key Principles

- **Minimal by default**: Every section must justify its presence. If an agent can infer it from the repo, omit it.
- **Non-redundant**: If it's already in README.md, package.json scripts, CI config, or is a standard convention for the stack, leave it out.
- **Standardized location**: Placed at repository root (or subproject roots for monorepos).
- **Open format**: Standard Markdown, flexible structure.
- **Ecosystem compatibility**: Works across 20+ AI coding tools and agents.

## What to Include / What NOT to Include

Only include a piece of information if **all three** of the following are true:
1. An agent cannot infer it by reading the codebase or standard tooling docs.
2. Getting it wrong would cause a real failure (broken tests, broken build, security issue).
3. It cannot be found in an existing file (README, package.json, Makefile, CI config).

**What NOT to include:**
- Standard install/build/test commands that match the package manager's defaults (e.g. `npm install`, `npm test`)
- Explanations of why steps are needed — agents don't benefit from prose rationale
- Architecture overviews already covered in README.md
- Generic code style rules (e.g. "use meaningful variable names")
- Anything that would be obvious to any competent developer on this stack

## Example Template

A good AGENTS.md is often just a few lines:

```markdown
## Testing

- Run a single test: `pnpm vitest run -t "<test name>"`
- Integration tests require a local Postgres instance: `docker compose up -d db`

## PR instructions

- Title format: [component] Brief description
```

If you find yourself writing more than ~10 bullet points total, stop and apply the three-condition filter again.

## Implementation Steps

1. **Analyze the project structure**: languages, frameworks, package manager, test runner, CI config.
2. **Read existing documentation**: README.md, package.json scripts, Makefile, `.github/workflows/`.
3. **Apply the redundancy check**: for each candidate instruction, ask "Is this already documented somewhere discoverable?" If yes, omit it.
4. **Write only what survives the filter**: non-obvious, failure-critical, not-already-documented instructions.
5. **Verify all commands work** as documented before including them.

## Best Practices

- **Be specific**: exact commands only, no vague descriptions
- **Use code blocks**: wrap all commands in backticks
- **Omit context explanations**: write what to run, not why
- **Prefer fewer sections**: one focused section beats six thin ones
- **Update as the project evolves**: stale instructions are worse than none

## Monorepo Considerations

- Place a root AGENTS.md only for cross-cutting, non-obvious instructions.
- Create subproject AGENTS.md files only where subprojects have genuinely unique, non-obvious requirements.
- The closest AGENTS.md takes precedence for any given location.

When creating the AGENTS.md file, prioritize **precision and brevity over completeness**. A shorter file with only high-signal instructions outperforms a comprehensive one that buries critical details in noise.
