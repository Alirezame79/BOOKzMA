# Testing

The current suite has pure tests for streak/date calculations, time parsing, Persian digits, API auth/helpers/routes, and a PostgreSQL concurrency test for the five-reminder limit. The latter is skipped unless `TEST_DATABASE_URL` points to a disposable PostgreSQL database. Do not use production data or credentials.

## Audit Environment Snapshot

At the documentation audit, both the host and existing `.venv` used Python 3.14.8, while `pyproject.toml` and CI target Python 3.12. Ruff passed. Pytest collection stopped in `tests/test_api.py`: the installed Starlette `TestClient` requested `httpx2`, which was not installed. No packages were installed. Re-run checks in a fresh supported Python 3.12 environment; do not treat this snapshot as a pass or as proof CI fails.

| Change | Minimum verification |
| --- | --- |
| Pure date/time logic | Unit tests for boundaries, timezone changes, DST, missed days, duplicates, and current-day behavior as applicable |
| Repository or transaction behavior | Integration test against disposable PostgreSQL; include duplicate/concurrent writes and relevant constraints |
| Bot handler or callback | Pure parsing/validation tests where practical; manual smoke test with the separate test bot, including invalid input and Telegram failures |
| API route or authentication | Unit/helper and route tests for authorization, invalid/expired input, ownership, validation, and response contract |
| Alembic migration | Compare migration with models; apply to an empty disposable PostgreSQL DB and verify schema. Never target production |
| Docker, Compose, or entrypoint | `docker compose up -d --build` only in a safe local environment; check startup and logs |
| Local launcher, config, or proxy workflow | Owner-run check with `dev_run.py`; the file must not be opened or changed by the agent |

Tests must be deterministic and use synthetic identities/data. Avoid dependence on today's real date, network availability, bot tokens, or live Telegram. Write a failing regression test before fixing a reproducible bug. Do not delete or weaken tests to get a pass. For concurrency, rely on database constraints/locking and verify the outcome with the integration test.

When shared streak logic changes, also review reading registration, weekly summaries, reminders, and API responses. Current CI starts PostgreSQL and sets `TEST_DATABASE_URL`; `test_reminder_limit.py` uses it for the concurrent reminder-cap test. Future work may expand PostgreSQL coverage, add fabricated aiogram update tests, and rehearse backup restoration; those additions are not implemented now.

Before finishing, run `ruff check . && pytest` and report the exact command and observed summary. “Should pass” is not a test result. If an environment mismatch, missing dependency, database, Docker, or Telegram access prevents a check, report it as not run or blocked.