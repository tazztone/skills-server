# Universal Engineering Rules

## Lazy Senior Dev Mode

- Before writing any code, ask: does it need to exist at all (YAGNI)? Does the standard library do it? A native platform feature? Can it be one line? Build the minimum that works.

## Code Quality

- Write for local reasoning: precise names, one concept per term, happy path readable, mutation explicit.
- Keep functions small, focused, at one abstraction level; separate setup, validation, computation, and side effects.
- Expose behavior not raw representation; keep APIs small, explicit, and hard to misuse.
- Use comments only for rationale, contracts, warnings, or invariants the code cannot express.
- Remove the highest-cost smell on every touch: duplication, deep nesting, misleading names, hidden dependency.

## Construction & Defensive Coding

- Treat construction quality as defect prevention; choose clarity and explicitness over clever compactness.
- Validate inputs at trust boundaries; assert programmer assumptions; make invalid states visible.
- Handle errors at the right level, preserve diagnostic context, keep the normal path readable.
- Build in small, verifiable increments; review for rising complexity while constructing.

## Design & Complexity

- Treat complexity as the main design metric; prefer changes that reduce cognitive load and change amplification.
- Prefer deep modules: small interfaces that hide meaningful internal complexity over pass-through layers.
- Pull complexity downward into the owning module instead of pushing it onto every caller.
- When a change feels awkward, fix the abstraction strategically instead of adding local exceptions.

## Architecture & Boundaries

- Enforce the dependency rule: source dependencies point toward policy, never toward frameworks or delivery.
- Keep the domain pure; business rules must not touch HTTP objects, ORM models, or vendor payloads directly.
- Treat infrastructure as replaceable detail behind ports or gateways.
- Prefer feature-oriented structure so use-case boundaries stay visible.

## Domain Modeling

- Use one ubiquitous language per bounded context; make implicit concepts explicit when language causes ambiguity.
- Keep aggregates small around true invariants and transactional consistency, not object-graph convenience.
- Reference other aggregates by identity; coordinate across boundaries via domain events and application services.
- Keep application services thin: they orchestrate, the domain owns business rules.
- Apply rich modeling only where business complexity justifies it; use simpler patterns everywhere else.

## Data & Consistency

- Give each fact one clear source of truth and owner; make consistency semantics explicit per write path.
- Require idempotency and replay safety for retried, queued, or event-driven writes.
- Treat caches, indexes, and projections as derived data that may lag and must be rebuildable.
- Make cross-partition or cross-service coordination an explicit design choice, not an accidental side effect.

## Refactoring

- Refactoring preserves observable behavior; keep behavioral delta distinct from structural cleanup.
- Get a safety net first (tests, characterization checks, types) before major structural edits.
- Use small verified steps and known moves: rename, extract, move, inline, split phase.
- Stop when the requested change is safe and clear; do not keep refactoring beyond the useful point.

## Legacy Code

- The first move is control, not elegance; make change safe before making it clean.
- Characterize behavior before changing code you do not fully understand.
- Find or create seams to observe and change behavior without touching the entire dependency tangle.
- Prefer sprout, wrap, and extract-and-override over risky direct surgery.

## Production Reliability

- Put timeouts on every network and external call by default; assume any dependency can fail or stall.
- Retry only idempotent operations; bound retries with backoff or jitter; never create retry storms.
- Isolate failure with circuit breakers and bulkheads; design for backpressure, queue limits, and load shedding.
- Make logs, metrics, and traces sufficient to diagnose degradation, overload, and partial outages.
- never use browser subagent before asking the user.

## Engineering Practices

- DRY means one authoritative source of knowledge; do not duplicate business rules across layers.
- Preserve orthogonality: separate policy from mechanism and avoid hidden couplings.
- Shorten feedback loops: prefer cheap early failure signals through tests, types, and linters.
- Automate repetitive error-prone work: build, test, release, and validation must be reproducible.
- Apply the broken windows rule: leave touched code slightly better than before.

## Universal Final Checklist

- Complexity reduced or contained?
- Boundaries, ownership, and contracts explicit?
- Observable behavior preserved (if refactoring)?
- Safe under retry, replay, and failure?
- Touched area slightly better?
- (optional) updated `AGENTS.md` containing only critical, non-discoverable, non-reduntant instructions for avoiding future roadblocks.
