# Technical Decisions

Each entry records current intent, not a claim that future work is implemented.

## D-01 — Existing API; Bot and Current Clients First

**Status:** Existing FastAPI implementation; further API expansion deferred.

**Context:** `src/BOOKzMA/api.py`, `requirements.txt`, `Dockerfile`, and `__main__.py` confirm an existing FastAPI app that runs alongside the Telegram bot. This is not a decision to add FastAPI from scratch.

**Decision:** Prioritize reliability and quality of the existing bot and API. Do not add endpoints, another client, or architecture layers for a hypothetical future. Keep shared business rules out of handlers/routes where practical; repositories remain independent of aiogram. Current API handlers are inside `api.py`, and some route logic is not yet extracted into services.

**Why:** New HTTP clients require maintained authentication, schemas, versioning, tests, and deployment. No evidence of a second live client was found in the repository; whether one exists outside this workspace is unverified.

**Alternatives:** Remove the current API (breaking existing behavior); expand the API in anticipation of clients (more maintenance); defer expansion while maintaining the existing interface (chosen).

**Revisit when:** A second client is actively being built, an existing API consumer needs a change, or measured requirements justify architectural work. Write a spec and review compatibility before changing routes.

## D-02 — `dev_run.py` Is Owner-Local

**Status:** Owner-provided constraint; file is present, ignored, and untracked. Its contents were not inspected.

**Context:** The owner reports using it to configure a local proxy and a separate test bot token while running the database in Compose.

**Decision:** Never read, import, commit, rewrite, delete, or replace it. Do not move proxy configuration into `src/`. Changes to entrypoints, settings, dependencies, or deployment must preserve both Docker operation and the owner's local workflow and call out that compatibility check.

**Why:** The launcher contains machine-specific configuration and is intentionally outside Git.

**Alternatives:** Put proxy logic in the application (rejected); later publish a separately approved `scripts/dev_run.example.py` containing placeholders only.

**Revisit when:** The owner explicitly requests a tracked example or changes local setup.

## D-03 — Streak Is Computed, Not Stored

**Status:** Implemented.

**Context:** `ReadingLog` stores one row per user and local calendar date; `services/streak.py` derives current and longest streaks.

**Decision:** Keep streak values derived from reading dates unless a reviewed spec establishes a different model.

**Why:** The date log is the source of truth and uniqueness makes same-day recording idempotent.

**Alternatives:** Store a mutable streak counter (adds consistency and concurrency risks).

**Revisit when:** A product requirement needs new target-day, rest-day, or freeze semantics.

## D-04 — Long Polling, Single Application Instance

**Status:** Implemented deployment assumption.

**Context:** `bot.py` starts aiogram polling; FSM storage and membership cache are process-local; the reminder loop scans reminders in the same app process.

**Decision:** Operate one application instance. Do not add replicas or webhook mode without first designing shared FSM/cache state and single-delivery ownership for reminders.

**Why:** Multiple instances could conflict on polling, lose cross-instance state, and send duplicate reminders.

**Alternatives:** Shared FSM/cache and distributed reminder claiming (more infrastructure and coordination); one process (current).

**Revisit when:** Measured load or availability requirements require multiple instances.

## Open Decisions (Owner Only)

- Exact streak rules for weekly targets, rest days, and Freeze/Shield.
- Definition of an active user for analytics.
- Book-search sources and copyright/licensing constraints.
- Reward model and anti-abuse rules.
- Simple support contact versus an in-bot ticket system.
- Backup retention period, location, encryption, and off-site copy.
- Whether the Telegram command menu should also use `MenuButtonCommands`, a reply keyboard, or both. `set_my_commands` already exists.