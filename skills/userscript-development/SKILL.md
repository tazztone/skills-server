---
name: userscript-development
description: Develop, debug, and test userscripts for Tampermonkey, Violentmonkey, and ScriptCat. Use when building foreground DOM automations, Shadow DOM UI, storage migrations, Playwright userscript tests, ScriptCat @background or @crontab workers, and UserSubscribe bundles.
---

# Userscript Development

Scripts fail most often at three seams: the runtime/metadata boundary, the DOM-selector boundary, and the test/installation boundary. Work outward from each seam in order.

## Workflow

### 1. Inventory

Read the repository before asking questions or editing:

- Locate existing scripts, research logs, READMEs, mocks, test commands, and package manifests.
- Read the current userscript, its tests, its research log, and [REFERENCE.md](references/REFERENCE.md).
- Record the runtime, matched hosts, granted APIs, persistent keys, user-visible behavior, test command, and any cleanup/migration scope.

> **Completion criterion:** Target files, existing behavior, verification commands, and cleanup/migration scope are identified and recorded from repository evidence.

### 2. Choose Runtime & Minimize Metadata

Choose exactly one runtime branch before writing logic:

- **Foreground DOM script** — standard `==UserScript==` metadata for page UI, DOM scraping, and event handling. Details: [REFERENCE.md](references/REFERENCE.md).
- **ScriptCat background / crontab script** — use `@background` or `@crontab` when work runs persistently or on schedule without DOM access; async operations must return a settling `Promise`. Details: [SCRIPTCAT.md](references/SCRIPTCAT.md).
- **ScriptCat subscription package** — use `==UserSubscribe==` (`.user.sub.js`) when distributing multiple scripts as a single bundle. Details: [SCRIPTCAT.md](references/SCRIPTCAT.md).

Preflight constraints:
- On Manifest V3 browsers, confirm extension developer mode or "Allow User Scripts" is enabled if injection fails.
- Declare the minimal `@match`, `@run-at`, `@grant`, `@connect`, and `@require` surface. Pin exact library versions in `@require`. Keep user-tunable `CONFIG` outside the IIFE; keep runtime implementation and UI encapsulation inside.

> **Completion criterion:** Runtime branch selected, preflight constraints verified, and every declared permission justified by a concrete implementation use.

### 3. Research the Page

For foreground scripts, create or update `RESEARCH_LOG.md` (template in [example_research_log.md](references/example_research_log.md)) before writing selectors. Document:

1. **Trigger and target elements** — primary and fallback selectors.
2. **Non-destructive text matching** — use `TreeWalker` (`NodeFilter.SHOW_TEXT`) to preserve framework event listeners.
3. **Positive signals and exclusions** — filter out `input`, `textarea`, `[contenteditable]`, and script-owned roots.
4. **Visibility and state checks** — verify element presence, computed visibility, non-zero dimensions, and enabled state.
5. **Event dispatch** — determine whether `.click()` suffices or if full synthetic `PointerEvent`/`MouseEvent` sequences are required.
6. **SPA dynamics** — document navigation transitions, DOM replacement, cooldown periods, and recovery behaviors.

> **Completion criterion:** Every automated action has a documented target selector, exclusion rule, non-destructive traversal method, event sequence, and failure recovery path.

### 4. Deep Modules & Orchestration

Separate concerns cleanly within the script closure:

- **Storage & configuration** — canonical keys, defaults, type validation, and migration adapters.
- **Normalization & adapters** — non-destructive traversal, visibility filters, and synthetic event dispatchers.
- **Batched DOM mutators** — slice multi-element operations with `requestAnimationFrame`, yield via `globalThis.scheduler?.yield()`, and guard batches with monotonic cancellation tokens (`runId`).
- **Encapsulated UI** — apply the Dual-Layer Style Architecture (host element styles in `document.head`, injected controls in an open Shadow Root) and render settings modals in the browser Top Layer via native `<dialog popover="auto">`. Details: [REFERENCE.md](references/REFERENCE.md).
- **Shared orchestrator** — manage one debounced `MutationObserver` (observing `childList`/`subtree`), one navigation listener with fallback, and one safety interval. Feature modules expose narrow operations and leave scheduling to the orchestrator.

> **Completion criterion:** Execution is idempotent; repeated triggers, route changes, and DOM mutations cause no duplicate controls, duplicate timers, or stuck locks; UI is isolated in Shadow DOM; and multi-element operations yield to protect main-thread responsiveness.

### 5. Storage Migration

- Use canonical, namespaced keys with dual-layer persistence (GM storage + page `localStorage`). Reseed GM storage from `localStorage` when GM storage is empty.
- Treat cross-script GM storage as isolated by default; support legacy page `localStorage` migration and provide manual settings fallbacks.
- When consolidating scripts, preserve default values, use new canonical prefixes, and instruct users to disable old scripts before enabling replacements.

> **Completion criterion:** Each setting has a canonical key, default value, type/range validation, read precedence, write behavior, migration source, and documented limitation.

### 6. Tests

Maintain an integrated mock page under `tests/` and inject the userscript source directly using Playwright (`page.evaluate()`). Reserve extension manager installation tests strictly for manager-specific functionality.

Cover user-visible behavior and edge cases:
- Initial state application, non-destructive DOM matching, and event dispatch.
- Shadow DOM UI rendering, piercing interactions (`#host >> #target`), and Top Layer `<dialog>` behavior.
- Toggle transitions, countdown pauses/resumptions, and cancellation on element removal.
- Duplicate mutation deduplication, route resets, and storage migration.
- Element exclusion rules (hidden items, locked controls, inputs, and script UI roots).
- Condition-based waits (`wait_for_selector`, `wait_for_function`) with `state='attached'` for elements hidden by filter rules (`display: none`).

> **Completion criterion:** Test suite executes via the documented command, validates all features and failure modes, and uses condition-based assertions without arbitrary sleeps.

### 7. Verify and Clean Up

Execute verification checks:

```bash
node --check path/to/script.user.js
pytest -o cache_dir=/tmp/.pytest_cache --import-mode=importlib path/to/tests/
git diff --check
```

- Verify that README (following [example_readme.md](references/example_readme.md)), research log, and inventory documentation match final changes.
- If dependencies or environment constraints block a test, report the exact blocked command.
- Remove legacy files only after replacements pass syntax and behavior checks.

> **Completion criterion:** Syntax checks pass, tests execute cleanly or report explicit environment blockers, modified documentation matches the changes, and cleanup matches the requested scope.

## References

- [REFERENCE.md](references/REFERENCE.md) — Runtime metadata, GM API quirks, Shadow DOM & Top Layer, storage patterns, and Playwright recipes.
- [SCRIPTCAT.md](references/SCRIPTCAT.md) — ScriptCat background workers, crontab lifecycle, `==UserConfig==` YAML, and subscription bundles.
- [example.user.js](references/example.user.js) — Reference foreground script with Shadow DOM UI, yielding, and orchestrator.
- [example_research_log.md](references/example_research_log.md) — Research log template for DOM and selector analysis.
- [example_readme.md](references/example_readme.md) — Standard userscript package README template.
