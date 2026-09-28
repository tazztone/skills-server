---
name: learn
description: Audit session friction and save systemic takeaways as project notes, rules, or skills.
disable-model-invocation: true
---

# Learn

Start from roadblocks, keep only what recurs, then propose one diff per takeaway.

## Audit friction

1. List tool and command failures: non-zero exits, wrong flags, missing dependencies, path errors.
2. List agent misunderstandings: hallucinated locations, wrong assumptions, repeated loops.
3. List user interventions: corrections, constraints, overrides ("no", "instead", "that failed").
4. Completion criterion: a friction list with the pivotal change quoted per item, or stop and say why nothing is reusable.

## Triage signal vs. noise

- Discard the ephemeral: one-off network blips, typos, external outages, throwaway experiments.
- Retain the systemic: undocumented conventions, silent failure modes, non-obvious constraints, repeated preferences.
- Completion criterion: every friction point labeled discard or retain; each retained takeaway names its root cause and whether it is universal or one-domain.

## Route to the least intrusive destination

- Project note (owning repo's README, docs, or runbook): repo-specific gotchas, environment quirks, build prerequisites.
- Guardrail (Rule in `skills/RULES.md`): universal constraint or formatting invariant.
- Playbook (Skill in `skills/<slug>/SKILL.md`): multi-step tool chain, flag combination, or cheatsheet.
- Completion criterion: one destination plus its target file per retained takeaway.

## Update first

- Update the existing note, guardrail, or playbook when it was used but failed, is outdated, missed the case, or diverges from what worked.
- Create new only when no existing file covers the case.
- Completion criterion: one target file plus one sentence of rationale per takeaway.

## Propose before editing

Propose before editing; edit only after explicit user approval.

1. Match the target file and one sibling under `skills/` for frontmatter, headings, and directory conventions; do not restate schema from memory.
2. Present the friction summary, classification, rationale, and exact diff, then wait.
- Completion criterion: the user approves or rejects the exact diff; make no file edits before approval.
