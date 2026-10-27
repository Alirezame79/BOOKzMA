# Testing

The current suite has pure tests for streak/date calculations and freezes, admin configuration/callback parsing, time parsing, Persian digits, and API auth/helpers/routes. PostgreSQL integration tests cover same-day reading-registration concurrency, reminder limits, account deletion and restoration, streak-freeze persistence, broadcast confirmation/cancellation, badges, onboarding, comeback analytics, study buddies, and Mesbak persistence/social limits. Database tests are skipped unless `TEST_DATABASE_URL` points to a disposable PostgreSQL database. Do not use production data or credentials.

## Local Environment Snapshot

The current host and `.venv` use Python 3.14, while `pyproject.toml` and CI target Python 3.12. `requirements-dev.txt` includes `httpx2` for the installed FastAPI/Starlette TestClient. The suite passes locally after installing dev requirements; PostgreSQL integration tests skip unless `TEST_DATABASE_URL` points to a disposable database. CI runs migrations and tests on Python 3.12 with PostgreSQL, which remains the authoritative migration check.

| Change | Minimum verification |
| --- | --- |
| Pure date/time logic | Unit tests for boundaries, timezone changes, DST, missed days, duplicates, and current-day behavior as applicable |
| Repository or transaction behavior | Integration test against disposable PostgreSQL; include duplicate/concurrent writes and relevant constraints |
| Durable broadcast worker | Fake Telegram responses for pacing, RetryAfter, bounded retry, blocked recipients, cancel/restart recovery and the duplicate-delivery failure window |
| Bot handler or callback | Pure parsing/validation tests where practical; manual smoke test with the separate test bot, including invalid input and Telegram failures |
| API route or authentication | Unit/helper and route tests for authorization, invalid/expired input, ownership, validation, and response contract |
| Alembic migration | Compare migration with models; apply to an empty disposable PostgreSQL DB and verify schema. Never target production |
| Docker, Compose, or entrypoint | `docker compose up -d --build` only in a safe local environment; check startup and logs |
| Local launcher, config, or proxy workflow | Owner-run check with `dev_run.py`; the file must not be opened or changed by the agent |

Tests must be deterministic and use synthetic identities/data. Avoid dependence on today's real date, network availability, bot tokens, or live Telegram. Write a failing regression test before fixing a reproducible bug. Do not delete or weaken tests to get a pass. For concurrency, rely on database constraints/locking and verify the outcome with the integration test.

When shared streak logic changes, also review reading registration, weekly summaries, reminders, and API responses. Current CI starts PostgreSQL and sets `TEST_DATABASE_URL`; database tests use it for persistence, constraints, idempotency, and concurrent-write contracts. The initial F-03 slice adds a concurrent same-day `mark_read` contract test; broader repository/migration coverage should be based on separately identified gaps rather than duplicating existing tests. Future work may add fabricated aiogram update tests and rehearse backup restoration; those additions are not implemented now.

Before finishing, run `ruff check . && pytest` and report the exact command and observed summary. “Should pass” is not a test result. If an environment mismatch, missing dependency, database, Docker, or Telegram access prevents a check, report it as not run or blocked.
