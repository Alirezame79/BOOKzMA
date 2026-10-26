# Local Development

The local workflow keeps PostgreSQL in Compose and runs the application from the host with the tracked `dev_run.py`. The launcher uses `TELEGRAM_PROXY` to configure aiogram's HTTP/SOCKS session; credentials and proxy values remain in local environment configuration.

| Concern | Local owner workflow (reported) | Production Compose (verified) |
| --- | --- | --- |
| Application process | `python dev_run.py`; host Uvicorn runs the shared FastAPI factory with an optional proxy session | Uvicorn runs the FastAPI factory; its lifespan starts bot polling and reminders |
| Database | Compose `db` service, host port `5433` | Compose `db` service and named `pgdata` volume |
| Telegram access | Separate test bot token and optional `TELEGRAM_PROXY` from `.env` | Direct Telegram access; no proxy is configured in Compose |
| Migrations | FastAPI lifespan runs Alembic `upgrade head` at startup against the configured local database | FastAPI lifespan runs Alembic `upgrade head` at application startup |
| Entrypoint | Tracked developer launcher; graceful shutdown deadline is 5 seconds | `uvicorn BOOKzMA.api:create_app --factory ...` from `Dockerfile` |

## Owner-Reported Setup

Use Python 3.12, matching `pyproject.toml` and CI. The reported command sequence is:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.sample .env
docker compose up -d db
docker compose stop bot
PYTHONPATH=src python dev_run.py
```

The admin backup and restore actions also require the host PostgreSQL client tools. On Fedora, install them with `sudo dnf install postgresql`; on Debian/Ubuntu use `sudo apt install postgresql-client`. Docker images already include the client tools.

در `.env` از bot token جداگانهٔ تست استفاده کن، `TELEGRAM_PROXY` را با آدرس proxy خودت تنظیم کن، و `DATABASE_URL` را به `127.0.0.1:5433` وصل کن؛ hostname `db` فقط داخل شبکهٔ Docker resolve می‌شود. سپس با فرمان‌های بالا فقط PostgreSQL را در Docker بالا بیاور، کانتینر bot را متوقف کن و برنامه را از میزبان اجرا کن. launcher همان app را اجرا می‌کند و migration را هنگام startup انجام می‌دهد. اگر `.env` هنوز placeholderهای `.env.sample` را دارد، پیش از اجرا آن‌ها را با مقادیر local/test جایگزین کن.

Before starting, ensure `DATABASE_URL` targets the local Compose database and `POSTGRES_PASSWORD` matches that database. Never use the production bot token locally. Do not run the Compose bot and local launcher simultaneously with the same token; Telegram permits only one long-polling consumer per bot. `dev_run.py` has no embedded credentials; configure a test bot token and optional proxy through environment settings.

Use a separate test bot. Do not poll the same token from both local and production instances. The test bot must have the channel permissions required by the configured membership gate. Do not expose private token or proxy values in logs or issue reports.

Local (non-Docker) backups: the backup service writes to `BACKUP_DIR` (default `backups`, resolved relative to the project root). The default location is `<project-root>/backups`; absolute paths are also accepted. The Compose variable `BOOKZMA_BACKUP_DIR` is only needed for `docker compose up` of the full stack, where the host directory is mounted at `/backups`.

## Compatibility Boundary

Changes must preserve Docker execution and the local workflow. The optional `bot_session` is unset in Compose, so Docker keeps its existing direct session. Local `dev_run.py` builds an aiogram session from `TELEGRAM_PROXY` and runs the same app on the host. The local Uvicorn launcher allows five seconds for graceful shutdown; the application bounds background-task shutdown to the same interval. Update this file, `BOT_GUIDE.md`, and `.env.sample` when changing settings or entrypoints.

Committed `src/BOOKzMA/__main__.py` starts Uvicorn without a proxy. The local launcher creates an optional aiogram `AiohttpSession` and injects it into the shared app; run it with a test token and local DB only.

## Local Launcher Boundary

`dev_run.py` only loads `Settings`, creates the aiogram session from the optional `TELEGRAM_PROXY` value, and starts the shared app. It contains no literal bot token or duplicate business logic. Never put real tokens or proxy credentials in the launcher.

برای روال اجباری branch، تست، PR، tag و deploy هر feature، [docs/WORKFLOW.md](WORKFLOW.md) را ببین.