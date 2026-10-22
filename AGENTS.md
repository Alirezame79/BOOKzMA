# BOOKzMA Agent Rules

BOOKzMA is a Python 3.12 Persian Telegram reading bot with an existing FastAPI API, SQLAlchemy async persistence, PostgreSQL, Alembic, and Docker Compose. The container runs the API, Telegram long polling, and reminder loop in one Uvicorn process.

## Read First

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) before changing runtime structure.
2. Read [BOT_GUIDE.md](BOT_GUIDE.md) before changing commands, callbacks, FSM state, API routes, tables, or environment variables.
3. Read [docs/DECISIONS.md](docs/DECISIONS.md) before proposing a different technology or architecture.
4. Read [docs/ROADMAP.md](docs/ROADMAP.md); an idea is not authorization to implement it.
5. Read the relevant topic guide: [LOCAL_DEV](docs/LOCAL_DEV.md), [TESTING](docs/TESTING.md), [SECURITY_PRACTICES](docs/SECURITY_PRACTICES.md), [PERFORMANCE](docs/PERFORMANCE.md), [BACKUP](docs/BACKUP.md), [DOCS_MAINTENANCE](docs/DOCS_MAINTENANCE.md), and [spec template](docs/specs/TEMPLATE.md). For owner workflows, see [vibe guide](docs/vibe/GUIDE.md) and [prompt library](docs/vibe/PROMPTS.md).

Never assume: open the actual file and verify the behavior before documenting or changing it.

## Commands

- Lint and tests: `ruff check . && pytest`. Run them before finishing and report actual output; never claim an unrun check passed.
- Docker build/start: `docker compose up -d --build`. This starts the configured application and database; do not use it against an owner's production host.
- Migration on a disposable/local database only: `alembic upgrade head`. The application also runs migrations at startup by default. Never run Alembic against production.
- CI uses Python 3.12, Ruff, Alembic, pytest, and a PostgreSQL service; see `.github/workflows/ci.yml`.

## Current Layout and Change Boundaries

- Bot handlers are in `src/BOOKzMA/handlers/`; they orchestrate repositories and services. Keep SQL in repositories. Register a new bot router in `src/BOOKzMA/handlers/__init__.py`.
- API routes are currently declared inside `src/BOOKzMA/api.py`. The API and bot share repositories and the application lifespan.
- `repositories/` has SQLAlchemy queries and no aiogram imports. `services/streak.py` contains reusable date calculations; `services/scheduler.py` is an asynchronous Telegram delivery loop, not a framework-independent service.
- User-facing bot text belongs in `texts.py`; inline keyboards belong in `keyboards.py`. `utils.py` contains parsing, digit conversion, and timezone helpers.
- Bot middleware provides one async DB session per update; handlers commit their writes. API routes manage commits explicitly.

## Hard Rules

- Preserve the `BOOKzMA` package name and Python 3.12 compatibility. Ruff line length is 100.
- Keep proxy code out of `src/`. `dev_run.py` is an owner's ignored local launcher: never read, import, commit, rewrite, delete, or replace it. Keep local and Docker execution compatible; see [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md).
- Never put real tokens, passwords, keys, DSNs, server details, user data, or database backups in source, tests, docs, issues, prompts, or Git. Never log bot tokens. Do not read `.env` or `dev_run.py`.
- Escape user/external values before inserting them into HTML-mode Telegram messages. Validate callback payloads, including Telegram's 64-byte limit. Any future privileged action must authorize on the server, not merely hide a button.
- Schema changes require a new Alembic revision; never edit an applied migration. Do not use `Base.metadata.create_all()`.
- Avoid blocking work and avoid repeated per-item queries in handlers or request loops. Keep database writes safe under duplicate/concurrent requests.
- Do not add dependencies, expand the API, add Redis/webhooks/admin panels, or implement roadmap items without an approved spec and owner approval.
- Never connect to production, inspect private configuration, run the bot with a real token, or run destructive data commands. Never run `docker compose down -v` unless the owner confirms the data is disposable.

## Stop and Ask

Ask before adding a dependency, changing schema or deployment configuration, changing streak/reminder semantics or membership/access behavior, deleting data/files, sending messages at scale, or requiring a secret. Bug fixes within an existing layer, focused tests, copy edits, behavior-preserving refactors, and documentation updates may proceed.

## Keep Docs in Sync

Update [ARCHITECTURE.md](ARCHITECTURE.md) and/or [BOT_GUIDE.md](BOT_GUIDE.md) in the same change when structure, commands, callbacks, state, tables, or environment variables change. Follow [docs/DOCS_MAINTENANCE.md](docs/DOCS_MAINTENANCE.md) for other triggers. A change is incomplete while its docs contradict the code.

Bot text should be natural, clear, modern Persian: neither stiff nor AI-sounding.

## End-of-Task Report

List changed files, checks actually run and their results, unverified areas, updated docs, and owner decisions still needed. Do not commit or push unless explicitly asked.