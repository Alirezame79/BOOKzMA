# Architecture (Current)

This repository contains a Persian Telegram reading bot and a FastAPI HTTP API. The API authenticates Telegram Web App `initData`, issues one-hour bearer tokens, and exposes account, reading, and reminder endpoints. The Docker application runs Uvicorn; its default lifespan also starts Telegram long polling and the reminder task in the same process.

## Runtime Flow

- `src/BOOKzMA/__main__.py` starts `BOOKzMA.api:create_app` through Uvicorn. `Dockerfile` uses the same factory and binds port 8000 inside the container.
- `create_app()` runs Alembic upgrades at startup by default, creates an async SQLAlchemy engine/session pool, and starts the bot unless its factory options disable those behaviors.
- `bot.py` creates an aiogram `Dispatcher`, registers `DbSessionMiddleware` at update scope, and registers `MembershipMiddleware` for messages and callback queries. The middleware exempts configured admin IDs from the membership gate and records UTC daily interaction. The bot scopes `/admin` to admins and starts polling, reminder, and durable broadcast tasks.
- Bot handlers live in `handlers/`; API routes are declared inside `api.create_app()`. Both paths call repositories directly and commit their own writes. `services/streak.py` contains date-based calculations; the reminder scheduler is asynchronous but depends on aiogram and repositories.
- `repositories/` contains SQLAlchemy queries and PostgreSQL upserts. `db/` contains the declarative base, models, and async session-pool factory.
- `texts.py` holds user-facing Persian bot messages; `keyboards.py` constructs inline keyboards.

## Data and State

- SQLAlchemy async models persist users, local reading dates, and reminders in PostgreSQL. Exact columns, constraints, and externally visible limits are listed in [BOT_GUIDE.md](BOT_GUIDE.md).
- Alembic revisions `0001`–`0005` add freeze events, daily activity/profile fields, and durable broadcast state. Do not edit an applied revision; add a new migration for schema changes.
- Freeze events remain separate from reading logs. Analytics read UTC activity and reading data; broadcast campaigns use per-recipient durable delivery records.
- Conversation state and membership cache are process-local; exact bot state and cache behavior are documented in [BOT_GUIDE.md](BOT_GUIDE.md).

## Operational Limits

- `reminder_loop` checks reminders in the same process as the bot and may perform additional database queries per candidate. Detailed timing and retry behavior are in [BOT_GUIDE.md](BOT_GUIDE.md); the observed query hot path is in [docs/PERFORMANCE.md](docs/PERFORMANCE.md).
- Polling, reminder/broadcast tasks, FSM state, membership cache, and the broadcast start lock are process-local. The current deployment is designed for one application instance; replicas would duplicate polling and background work and would not share FSM/cache/lock state.
- The API health endpoint reports process-level `{"status":"ok"}` and does not verify database or Telegram availability.

## Local and Production

Production Compose runs PostgreSQL and the API/bot application together as containers. The host publishes PostgreSQL on `127.0.0.1:5433` and the application on `127.0.0.1:8000`. The Docker image runs as UID 10001 and copies only requirements, `src/`, `migrations/`, and `alembic.ini`.

The owner reports that local development starts the database with Compose and runs a separate local launcher, `dev_run.py`, using a separate test bot token and local proxy settings. That file is intentionally ignored and was not opened; its implementation is therefore unverified. See [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md) before changing entrypoints, configuration, or deployment.

For interface details, environment variables, commands, callbacks, and constraints, see [BOT_GUIDE.md](BOT_GUIDE.md). For current decisions and future ideas, see [docs/DECISIONS.md](docs/DECISIONS.md) and [docs/ROADMAP.md](docs/ROADMAP.md).