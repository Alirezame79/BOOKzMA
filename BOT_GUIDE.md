# Bot and API Guide (Current)

This guide records behavior verified in `src/BOOKzMA/`, migrations, and configuration. See [ARCHITECTURE.md](ARCHITECTURE.md) for runtime topology and [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md) for the owner-specific launcher; `dev_run.py` was not read.

## Commands and Bot Interface

`bot.py` registers `/start`, `/reminders`, `/timezone`, `/profile`, and `/support` for all users. Configured admins also receive `/admin` in their chat command scope. `/start` shows the persistent Persian reply keyboard; contextual flows continue to use inline keyboards. Admin entry points are checked against `ADMIN_TELEGRAM_IDS` in handlers, independently of menu visibility.

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
| `leaderboard:toggle` | Toggle the user's public leaderboard presence |
| `leaderboard` | Show the current-streak leaderboard (display names only) |
| `account_del:start` | Start the account-deletion wizard from the profile |
| `account_del:why` | Show the deletion-reason choices |
| `account_del:reason:<index>` | Record a reason (validated against `DELETE_REASONS`) and ask for the typed confirmation word |
| `account_del:go` | Final confirmation: delete the account and all of its data |
| `account_del:cancel` | Cancel the deletion flow at any step and return to the profile |
| `account_restore` | Explicit re-registration: clear the deletion tombstone and start fresh |
| `admin:stats` | Show admin analytics; server-side admin check required |
| `admin:broadcast` | Start a text campaign draft; server-side admin check required |
| `admin:backup` | Open the backup menu (latest backup, on-demand backup, restore); server-side admin check required |
| `admin:backup_now` | Run an on-demand `pg_dump` through `services/backup.py`; server-side admin check required |
| `admin:backup_restore` | List local backup files; server-side admin check required |
| `admin:restore_ask:<index>` | Show the destructive-restore warning for the listed backup (index into the current `list_backups` order, never free text) |
| `admin:restore_ready:<index>` | Ask for the typed confirmation word and arm the restore FSM state |
| `broadcast:start:<id>` | Confirm an owned campaign |
| `broadcast:status:<id>` | Show counts for an owned campaign |
| `broadcast:cancel:<id>` | Cancel an owned campaign |

FSM states are `handlers.reminders.AddTime.waiting`, `handlers.admin.NewBroadcast.waiting_for_text`, `handlers.admin.BackupRestore.waiting_for_confirm`, and `handlers.account.DeleteAccount.waiting_word`; FSM storage remains in-memory. Arbitrary reminder times are parsed as 24-hour `HH[:MM]` with Persian or Arabic digits accepted.

Account deletion (`N-04`) is a four-step wizard started from the profile: a warning screen, a deletion-reason choice, a typed confirmation word (`حذف`), and a final button. Deletion removes the `users` row (cascading to all related tables) and inserts a `deleted_accounts` tombstone in the same transaction. The membership middleware intercepts tombstoned users before handlers run — they get a neutral start prompt (no mention of a previous account) and no activity or start is recorded for them; the `account_restore` callback clears the tombstone. The API exposes the same behavior through `DELETE /api/v1/me`, and authenticated requests for tombstoned users return 401 until they re-register via the bot.

Database backup and restore (`N-05`, decision D-09): the admin panel's backup section runs `pg_dump -Fc` over TCP to the database from inside the bot container (the image installs `postgresql-client`) into `BACKUP_DIR` (`/backups` in Compose, bind-mounted from `BOOKZMA_BACKUP_DIR` on the host), keeping only `BACKUP_KEEP_LOCAL` (default 1) newest dumps named `bookzma-YYYY-MM-DD-HHMMSS.dump`. Restore is destructive: warning screen, typed confirmation word (`بازیابی`), then `pg_restore --clean --no-owner --no-acl` against the current database; a restart (`docker compose restart bot`) is recommended afterwards and stated in the completion message. Restore file names are validated against the backup-name pattern (no path traversal) and can only be selected by index from the real file listing. All backup callbacks re-check the admin allowlist server-side. Daily scheduling and Google Drive upload are host-side (`scripts/backup.py`); see [docs/BACKUP.md](docs/BACKUP.md) for the runbook.

## HTTP API

The existing FastAPI app is in `api.py`; the container runs it through Uvicorn. Authentication validates Telegram Web App `initData`, then returns an HS256 bearer token derived from the bot token with a one-hour lifetime. Protected routes identify users from that token.

| Method and path | Purpose |
| --- | --- |
| `GET /health` | Process-level status response |
| `POST /api/v1/auth/telegram` | Exchange signed Telegram `initData` for a bearer token |
| `GET /api/v1/me` | Read/create the authenticated user profile |
| `PUT /api/v1/me/timezone` | Update timezone |
| `DELETE /api/v1/me` | Delete the authenticated account and all of its data; later requests return 401 |
| `GET /api/v1/me/weekly-summary` | Read the seven-day summary |
| `POST /api/v1/me/read` | Record today's reading |
| `GET /api/v1/me/reminders` | List the authenticated user's reminders |
| `POST /api/v1/me/reminders` | Add a reminder; returns conflict for duplicate/limit |
| `DELETE /api/v1/me/reminders/{reminder_id}` | Delete the authenticated user's reminder |

`WEB_ORIGINS` is a comma-separated CORS allowlist; CORS middleware is only installed when it contains an origin. `/docs` is FastAPI's interactive schema UI. The health route does not check database or Telegram health. The API routes do not use the bot's channel-membership middleware.

## Data and Limits

| Table | Current shape and invariant |
| --- | --- |
| `users` | Telegram ID primary key; optional display name/username; timezone defaults to `Asia/Tehran`; first-start time; leaderboard opt-out and permanent broadcast-unavailable flags |
| `reading_logs` | `(user_id, day)` composite primary key; user foreign key cascades on delete |
| `streak_freezes` | Earned/used freeze events, separate from reading logs; unique `(user_id, kind, day)` |
| `activity_days` | One row per user and UTC date; cascades with user deletion |
| `deleted_accounts` | Deletion tombstone: Telegram ID primary key (no foreign key), deletion timestamp, optional reason code from `DELETE_REASONS`; prevents silent re-registration |
| `broadcast_campaigns` | Admin-owned text campaign and state |
| `broadcast_deliveries` | Per-campaign/per-user state, attempt count and last error; cascades on user/campaign deletion. Users with permanent Telegram delivery failures are excluded from later broadcasts. |
| `reminders` | Integer primary key; user foreign key; time; last-sent date; retry date/count/deadline; unique `(user_id, remind_at)` |

Streak is computed from read dates plus explicitly used freeze dates; freeze days are not reported as reading. Users start with zero freezes, earn one per seven consecutive real reading days, and hold at most two. One missed day is automatically protected when reading resumes the next day; freezes cannot cover consecutive missed days. Weekly summaries cover today and the preceding six local dates. Reminders are capped at five per user; presets are `08:00`, `13:00`, `18:00`, `21:00`, and `23:00`. The scheduler scans every 30 seconds, skips sends over ten minutes late, and caps retries at three per reminder per local day.

Admin analytics count starts recorded from the new deployment onward, UTC daily interactions after successful membership checks, and reading logs separately. D1/D7/D30 return rates use only users with enough post-deployment observation time. The displayed seven-day chart is text-based. The dashboard also reports total deleted accounts and deletions in the last seven UTC days from the tombstone table. Broadcast campaigns are text-only, confirmed by an admin, serialized to one active campaign in the single application process, and sent at 5 messages/second with bounded retries and persisted `RetryAfter` deadlines. Delivery state is persisted and inflight deliveries are retried after restart; a crash after Telegram accepts a message but before the DB update can cause a duplicate. Deleting an account mid-campaign or mid-reminder-sweep is safe: updates to deleted rows are no-ops and counts reflect remaining recipients.

Membership checks run for bot messages and callbacks, except the `check_join` callback itself and the `account_restore` callback. Required channels come from `REQUIRED_CHANNELS`, defaulting to an empty list if unset. Only successful checks are cached, per process, for 300 seconds. A membership-check Telegram error is treated as not joined. Every update also performs one indexed tombstone lookup (`deleted_accounts`) before handlers run, so deleted users never reach `get_or_create`.

A per-process rate-limit middleware (`middlewares/rate_limit.py`, decision D-10) runs before the membership middleware for messages and callbacks: a user may send at most `RATE_LIMIT_MAX_UPDATES` updates (default 20) per `RATE_LIMIT_WINDOW_SECONDS` (default 10). Admins are exempt. A blocked update never reaches a handler or the DB session; the user gets the rate-limit text at most once per window and the event is logged (`log.warning`), not counted in admin analytics. The window state is in-memory and resets on restart.

## Environment

| Variable | Read by | Current behavior |
| --- | --- | --- |
| `BOT_TOKEN` | `Settings` | Required; stored as `SecretStr` |
| `POSTGRES_PASSWORD` | Compose | Required to configure the PostgreSQL container and bot `DATABASE_URL` |
| `DATABASE_URL` | `DatabaseSettings` / Compose | Optional in local settings (default points to local PostgreSQL); Compose constructs the bot URL from the password |
| `REQUIRED_CHANNELS` | `constants.py` | Optional comma-separated channel identifiers; defaults to none |
| `WEB_ORIGINS` | `Settings` / API | Optional comma-separated CORS origins |
| `ADMIN_TELEGRAM_IDS` | `Settings` / bot | Optional comma-separated numeric Telegram IDs; empty means no admins |
| `GITHUB_URL` | `Settings` / support menu | Optional GitHub project URL; only GitHub repository URLs are shown |
| `SUPPORT_TELEGRAM_USERNAME` | `Settings` / support menu | Optional Telegram username for private financial-support contact |
| `BOOKZMA_BACKUP_DIR` | Compose | Required by Compose; host folder bind-mounted into the bot at `/backups`; must be outside the repository |
| `BACKUP_DIR` | `Settings` / backup service | Backup folder inside the container; defaults to `/backups` |
| `BACKUP_KEEP_LOCAL` | `Settings` / backup service | Number of newest local backups to keep after rotation; defaults to 1 |
| `RATE_LIMIT_MAX_UPDATES` | `Settings` / rate-limit middleware | Optional; max updates per user per window across messages and callbacks; defaults to 20 |
| `RATE_LIMIT_WINDOW_SECONDS` | `Settings` / rate-limit middleware | Optional; fixed window length in seconds; defaults to 10 |
| `LOG_LEVEL` | `Settings` | Defaults to `INFO`; no logging configuration consuming it was found |

`.env.sample` documents the variables above and an optional placeholder `DATABASE_URL` for local tools. Set the real owner ID and support destinations in the runtime environment; do not commit them. Code supplies a default database URL and Compose overrides it for the bot container.

## Verified Caveats

- The application runs migrations automatically during API lifespan startup by default.
- Telegram polling, reminder work, FSM storage, membership cache, and rate-limit windows are process-local; use one application instance.
- Reminder delivery holds a DB session while scanning and sending. Each candidate may cause additional reads; consult [docs/PERFORMANCE.md](docs/PERFORMANCE.md) before changing this path.
- Bot updates are rate-limited per user (D-10); no rate limiter for HTTP endpoints was found. Callback handlers validate preset values, numeric IDs, and timezone indexes, but changes must continue to enforce payload parsing and Telegram's 64-byte callback-data limit.