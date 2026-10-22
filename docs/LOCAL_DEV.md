# Local Development

The owner reports a local workflow where Compose runs PostgreSQL and an ignored `dev_run.py` launches a separate test bot with local proxy settings. The file is private and was not opened, so its implementation, exact proxy setup, and compatibility with the current package are unverified.

| Concern | Local owner workflow (reported) | Production Compose (verified) |
| --- | --- | --- |
| Application process | `python dev_run.py`; exact behavior unverified | Uvicorn runs the FastAPI factory; its lifespan starts bot polling and reminders |
| Database | Compose `db` service, host port `5433` | Compose `db` service and named `pgdata` volume |
| Telegram access | Separate test bot token; local proxy settings are reported | Production bot token from `.env`; no proxy code in `src/` |
| Migrations | Run `alembic upgrade head` against the local database before bot use if needed | FastAPI lifespan runs Alembic `upgrade head` at application startup |
| Entrypoint | Private launcher; do not inspect or replace | `uvicorn BOOKzMA.api:create_app --factory ...` from `Dockerfile` |

## Owner-Reported Setup

Use Python 3.12, matching `pyproject.toml` and CI. The reported command sequence is:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.sample .env
docker compose up -d db
alembic upgrade head
python dev_run.py
```

Before the last three commands, configure only local/test values in the local `.env` and ensure `DATABASE_URL` targets the disposable/local Compose database. Never use the production bot token locally. Run `alembic upgrade head` only against that local database. Do not inspect, commit, import, rewrite, or delete the ignored `dev_run.py`.

Use a separate test bot. Do not poll the same token from both local and production instances. The test bot must have the channel permissions required by the configured membership gate. Do not expose private token or proxy values in logs or issue reports.

## Compatibility Boundary

Changes must preserve Docker execution and the owner's local workflow. Before changing settings, entrypoints, dependencies, Dockerfile, or Compose, report the impact and update this file, `BOT_GUIDE.md`, and `.env.sample` where applicable.

Committed `src/BOOKzMA/__main__.py` starts Uvicorn, and no package-level `main()` function was found. Whether `dev_run.py` invokes a different internal entrypoint is unverified because the private file must not be read. Do not claim local proxy compatibility based only on committed code; ask the owner to run the relevant local check.

## Local Launcher Boundary

The expected boundary, based on the owner's setup description, is that `dev_run.py` only loads local environment values, configures the aiogram proxy from an environment variable, and starts the same application implementation; it must not contain a bot token or duplicate business logic. This is an intended contract, not a verified description of the private file. The committed package currently exposes Uvicorn startup through `__main__.py` and has no package-level `main()` function, so how the local launcher invokes the shared implementation remains an owner-confirmed open point.

Keep the launcher outside Git. If the owner later requests a public example, propose a separate script with placeholders and obtain approval first. Never put real tokens or proxy credentials in a tracked example.