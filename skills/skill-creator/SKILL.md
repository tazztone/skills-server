---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run the AI-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Present the results for the user to review, alongside quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always be flexible and if the user is like "I don't need to run a bunch of evaluations, just vibe with me", you can do that instead.

Then after the skill is done (but again, the order is flexible), you can also run the skill description optimization step to improve triggering accuracy.

Cool? Cool.

## Communicating with the user

The skill creator is liable to be used by people across a wide range of familiarity with coding jargon. There's a trend now where the power of AI is inspiring people with no traditional coding background to open up their terminals. On the other hand, the bulk of users are probably fairly computer-literate.

So please pay attention to context cues to understand how to phrase your communication! In the default case, just to give you some idea:

- "evaluation" and "benchmark" are borderline, but OK
- for "JSON" and "assertion" you want to see serious cues from the user that they know what those things are before using them without explaining them

It's OK to briefly explain terms if you're in doubt, and feel free to clarify terms with a short definition if you're unsure if the user will get it.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

1. What should this skill enable the AI to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Research relevant context (docs, best practices, similar skills) as needed. Come prepared with context to reduce burden on the user.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. This is the primary triggering mechanism — include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Note: AI assistants have a tendency to "undertrigger" skills — to not use them when they'd be useful. To combat this, make the skill descriptions a little bit "pushy". So for instance, instead of "How to build a simple fast dashboard to display data.", you might write "How to build a simple fast dashboard to display data. Make sure to use this skill whenever the user mentions dashboards, data visualization, or wants to display any kind of data, even if they don't explicitly ask for a 'dashboard.'"
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

### Skill Writing Guide

#### Anatomy of a Skill

skill-name/
├── SKILL.md (required)
│ ├── YAML frontmatter (name, description required)
│ └── Markdown instructions
└── Bundled Resources (optional)
├── scripts/ - Executable code for deterministic/repetitive tasks
├── references/ - Docs loaded into context as needed
└── assets/ - Files used in output (templates, icons, fonts)
text

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** — As needed (unlimited, scripts can execute without loading)

These word counts are approximate and you can feel free to go longer if needed.

**Key patterns:**
- Keep SKILL.md under 500 lines; if you're approaching this limit, add an additional layer of hierarchy along with clear pointers about where the model using the skill should go next to follow up.
- Reference files clearly from SKILL.md with guidance on when to read them
- For large reference files (>300 lines), include a table of contents

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant:
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
├── aws.md
├── gcp.md
└── azure.md
text
The AI reads only the relevant reference file.

#### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities.

#### Writing Patterns

Prefer using the imperative form in instructions.

**Defining output formats** — You can do it like this:
```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** — It's useful to include examples. You can format them like this:
```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Writing Style

Try to explain to the model *why* things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.

### Test Cases

After writing the skill draft, come up with 2–3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `assertions` field, which you'll add later).

---

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.). Don't create all of this upfront — just create directories as you go.

### Step 1: Run all evals (with-skill AND baseline)

For each test case, produce two runs — one following the skill, one without. Do them in the same pass so results are ready around the same time.

**With-skill run:** Read the skill's SKILL.md, then follow its instructions to accomplish the test prompt. Save outputs to:
<workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
text

**Baseline run** (same prompt, but without the skill — or using the previous version when improving):
- **Creating a new skill**: complete the prompt without consulting the skill at all. Save to `without_skill/outputs/`.
- **Improving an existing skill**: snapshot the current skill before editing, use the snapshot as the baseline. Save to `old_skill/outputs/`.

> **Note on parallelism**: If your environment supports running tasks in parallel (e.g., via subagents), spawn with-skill and baseline runs simultaneously. If not, run them sequentially — the qualitative comparison is still valuable.

Write an `eval_metadata.json` for each test case (assertions can be empty for now). Give each eval a descriptive name based on what it's testing.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While runs are in progress, draft assertions

Don't just wait for runs to finish — draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions once drafted. Also explain to the user what they'll see — both the qualitative outputs and the quantitative benchmarks.

### Step 3: Present results to the user

Once all runs are done, present the results clearly. Options depending on what's available in your environment:

- **If you have a filesystem and can run scripts**: Run `eval-viewer/generate_review.py` to produce an HTML review page. If a browser is available, open it; otherwise write a `--static <output_path>` HTML file the user can download and open locally.
- **If no filesystem or scripting is available**: Present results inline in the conversation — for each test case, show the prompt, the with-skill output, and the baseline output side by side. Ask for feedback directly.

Either way, tell the user something like: "Here are the results. There are two things to look at — the qualitative outputs for each test case, and the quantitative pass/fail summary. Let me know what you think."

### Step 4: Grade, aggregate, and analyze

1. **Grade each run** — evaluate each assertion against the outputs. Save results to `grading.json` in each run directory. The `grading.json` expectations array must use the fields `text`, `passed`, and `evidence`. For assertions that can be checked programmatically, write and run a script.

2. **Aggregate into benchmark** — produce `benchmark.json` and `benchmark.md` with pass rate, time, and tokens for each configuration, with mean ± stddev and the delta. See `references/schemas.md` for the exact schema.

3. **Do an analyst pass** — surface patterns the aggregate stats might hide: assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

### Step 5: Read the feedback

When the user tells you they're done, gather their feedback (from `feedback.json` if using the viewer, or from the conversation if inline). Empty feedback means the user thought it was fine. Focus improvements on the test cases where the user had specific complaints.

---

## Improving the skill

This is