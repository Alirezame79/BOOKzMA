# Bot and API Guide (Current)

This guide records behavior verified in `src/BOOKzMA/`, migrations, and configuration. See [ARCHITECTURE.md](ARCHITECTURE.md) for runtime topology and [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md) for the owner-specific launcher; `dev_run.py` was not read.

## Commands and Bot Interface

`bot.py` registers these Telegram commands with `set_my_commands`: `/start`, `/reminders`, `/timezone`. There is no `MenuButton` or `ReplyKeyboardMarkup`; the bot uses inline keyboards.

Callback payloads implemented in handlers/keyboards:

| Payload | Behavior |
| --- | --- |
| `home` | Clear FSM state and render home |
| `check_join` | Recheck required channel membership |
| `read` | Record today's reading idempotently |
| `weekly` | Show seven-day summary |
| `rem` | Open reminder management |
| `rem_add:<HHMM>` | Add one of the configured preset times |
| `rem_del:<id>` | Delete the current user's reminder |
| `rem_custom` | Request a custom reminder time |
| `tz` | Show timezone choices |
| `tz_set:<index>` | Set one of the configured timezone choices |

The only declared FSM state is `handlers.reminders.AddTime.waiting`; arbitrary reminder times are parsed as 24-hour `HH[:MM]` with Persian or Arabic digits accepted. The default aiogram FSM storage is in-memory.

## HTTP API

The existing FastAPI app is in `api.py`; the container runs it through Uvicorn. Authentication validates Telegram Web App `initData`, then returns an HS256 bearer token derived from the bot token with a one-hour lifetime. Protected routes identify users from that token.

| Method and path | Purpose |
| --- | --- |
| `GET /health` | Process-level status response |
| `POST /api/v1/auth/telegram` | Exchange signed Telegram `initData` for a bearer token |
| `GET /api/v1/me` | Read/create the authenticated user profile |
| `PUT /api/v1/me/timezone` | Update timezone |
| `GET /api/v1/me/weekly-summary` | Read the seven-day summary |
| `POST /api/v1/me/read` | Record today's reading |
| `GET /api/v1/me/reminders` | List the authenticated user's reminders |
| `POST /api/v1/me/reminders` | Add a reminder; returns conflict for duplicate/limit |
| `DELETE /api/v1/me/reminders/{reminder_id}` | Delete the authenticated user's reminder |

`WEB_ORIGINS` is a comma-separated CORS allowlist; CORS middleware is only installed when it contains an origin. `/docs` is FastAPI's interactive schema UI. The health route does not check database or Telegram health. The API routes do not use the bot's channel-membership middleware.

## Data and Limits

| Table | Current shape and invariant |
| --- | --- |
| `users` | Telegram ID primary key; optional username; timezone defaults to `Asia/Tehran`; creation timestamp |
| `reading_logs` | `(user_id, day)` composite primary key; user foreign key cascades on delete |
| `reminders` | Integer primary key; user foreign key; time; last-sent date; retry date/count/deadline; unique `(user_id, remind_at)` |

Streak is computed from reading dates in the user's local timezone; it is not stored. A streak remains current through today if the user read yesterday. Weekly summaries cover today and the preceding six local dates. Reminders are capped at five per user; presets are `08:00`, `13:00`, `18:00`, `21:00`, and `23:00`. The scheduler scans every 30 seconds, skips sends over ten minutes late, and caps retries at three per reminder per local day.

Membership checks run for bot messages and callbacks, except the `check_join` callback itself. Required channels come from `REQUIRED_CHANNELS`, defaulting to an empty list if unset. Only successful checks are cached, per process, for 300 seconds. A membership-check Telegram error is treated as not joined.

## Environment

| Variable | Read by | Current behavior |
| --- | --- | --- |
| `BOT_TOKEN` | `Settings` | Required; stored as `SecretStr` |
| `POSTGRES_PASSWORD` | Compose | Required to configure the PostgreSQL container and bot `DATABASE_URL` |
| `DATABASE_URL` | `DatabaseSettings` / Compose | Optional in local settings (default points to local PostgreSQL); Compose constructs the bot URL from the password |
| `REQUIRED_CHANNELS` | `constants.py` | Optional comma-separated channel identifiers; defaults to none |
| `WEB_ORIGINS` | `Settings` / API | Optional comma-separated CORS origins |
| `LOG_LEVEL` | `Settings` | Defaults to `INFO`; no logging configuration consuming it was found |

`.env.sample` documents the variables above and an optional placeholder `DATABASE_URL` for local tools. Code supplies a default and Compose overrides it for the bot container.

## Verified Caveats

- The application runs migrations automatically during API lifespan startup by default.
- Telegram polling, reminder work, FSM storage, and membership cache are process-local; use one application instance.
- Reminder delivery holds a DB session while scanning and sending. Each candidate may cause additional reads; consult [docs/PERFORMANCE.md](docs/PERFORMANCE.md) before changing this path.
- No rate limiter for HTTP endpoints was found. Callback handlers validate preset values, numeric IDs, and timezone indexes, but changes must continue to enforce payload parsing and Telegram's 64-byte callback-data limit.