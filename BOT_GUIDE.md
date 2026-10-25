# Bot and API Guide (Current)

This guide records behavior verified in `src/BOOKzMA/`, migrations, and configuration. See [ARCHITECTURE.md](ARCHITECTURE.md) for runtime topology and [docs/LOCAL_DEV.md](docs/LOCAL_DEV.md) for the owner-specific launcher; `dev_run.py` was not read.

## Commands and Bot Interface

`bot.py` registers `/start`, `/reminders`, `/timezone`, `/profile`, and `/support` for all users. Configured admins also receive `/admin` in their chat command scope. `/start` shows the persistent Persian reply keyboard; contextual flows continue to use inline keyboards. Admin entry points are checked against `ADMIN_TELEGRAM_IDS` in handlers, independently of menu visibility.

`/start` branches by onboarding state (`users.onboarded_at`, U-01): a user who has not completed the intro flow gets a short welcome message with a first-reminder choice instead of the home screen, and the same flow starts after passing the channel gate via `check_join`. Existing users were backfilled with `onboarded_at` in migration `0007`, so only new accounts see the intro. A returning reader — someone with reading history whose last local reading day is more than seven days old (U-02) — receives a blame-free welcome-back line before the home screen; this fires only on `/start`.

Callback payloads implemented in handlers/keyboards:

| Payload | Behavior |
| --- | --- |
| `onb:<HHMM>` | Onboarding: add the chosen preset reminder and mark the intro complete (validated against `PRESET_TIMES`) |
| `onb:skip` | Onboarding: skip the first reminder and mark the intro complete |
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
| `broadcast:start:<id>` | Confirm an owned campaign |
| `broadcast:status:<id>` | Show counts for an owned campaign |
| `broadcast:cancel:<id>` | Cancel an owned campaign |

FSM states are `handlers.reminders.AddTime.waiting`, `handlers.admin.NewBroadcast.waiting_for_text`, and `handlers.account.DeleteAccount.waiting_word`; FSM storage remains in-memory. The onboarding flow is stateless callback-driven and needs no FSM state. Arbitrary reminder times are parsed as 24-hour `HH[:MM]` with Persian or Arabic digits accepted.

Account deletion (`N-04`) is a four-step wizard started from the profile: a warning screen, a deletion-reason choice, a typed confirmation word (`حذف`), and a final button. Deletion removes the `users` row (cascading to all related tables) and inserts a `deleted_accounts` tombstone in the same transaction. The membership middleware intercepts tombstoned users before handlers run — they get a neutral start prompt (no mention of a previous account) and no activity or start is recorded for them; the `account_restore` callback clears the tombstone. The API exposes the same behavior through `DELETE /api/v1/me`, and authenticated requests for tombstoned users return 401 until they re-register via the bot.

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
| `users` | Telegram ID primary key; optional display name/username; timezone defaults to `Asia/Tehran`; first-start and onboarding-completion timestamps; comeback state (`broken_streak_days`, `comeback_bonus_days`, `comeback_base_day`); leaderboard opt-out and permanent broadcast-unavailable flags |
| `reading_logs` | `(user_id, day)` composite primary key; user foreign key cascades on delete |
| `streak_freezes` | Earned/used freeze events, separate from reading logs; unique `(user_id, kind, day)` |
| `activity_days` | One row per user and UTC date; cascades with user deletion |
| `streak_alerts` | Daily dedup for streak-at-risk alerts; composite `(user_id, day)` primary key; cascades with user deletion |
| `deleted_accounts` | Deletion tombstone: Telegram ID primary key (no foreign key), deletion timestamp, optional reason code from `DELETE_REASONS`; prevents silent re-registration |
| `broadcast_campaigns` | Admin-owned text campaign and state |
| `broadcast_deliveries` | Per-campaign/per-user state, attempt count and last error; cascades on user/campaign deletion. Users with permanent Telegram delivery failures are excluded from later broadcasts. |
| `reminders` | Integer primary key; user foreign key; time; last-sent date; retry date/count/deadline; unique `(user_id, remind_at)` |

Streak is computed from read dates plus explicitly used freeze dates; freeze days are not reported as reading. Users start with zero freezes, earn one per seven consecutive real reading days, and hold at most two. One missed day is automatically protected when reading resumes the next day; freezes cannot cover consecutive missed days. Weekly summaries cover today and the preceding six local dates. Reminders are capped at five per user; presets are `08:00`, `13:00`, `18:00`, `21:00`, and `23:00`. The scheduler scans every 30 seconds, skips sends over ten minutes late, and caps retries at three per reminder per local day.

Comeback streak (`S-07`): when a displayed streak of three or more days breaks, the next reading day opens a comeback window on `users` (`broken_streak_days`, `comeback_base_day`, `comeback_bonus_days`). Three consecutive reading days award half of the broken streak (floor, capped at 30) as a bonus. Surfaces that display the streak (home, profile, weekly summary, leaderboard, reminder pushes, read toast) show the raw streak plus the bonus via `displayed_streak`; the bonus becomes inert once the chain that earned it breaks and never affects `longest_streak`, freeze earning, or admin analytics (which use the raw streak). A frozen day covering the break keeps the streak alive, so no comeback window opens.

Streak-at-risk alerts (`S-08`): a third background loop (`services/risk_alert.py`, 60-second interval) messages users at 21:00–21:10 local time when their raw streak is at least two days, the chain is intact through yesterday, and today is unread. Sends are deduplicated per user and local day in `streak_alerts`; a send failure marks the day as alerted anyway, and a downtime window longer than ten minutes skips that day entirely.

Admin analytics count starts recorded from the new deployment onward, UTC daily interactions after successful membership checks, and reading logs separately. The dashboard also reports onboarding completions (`users.onboarded_at`, meaningful from the migration `0007` deploy date onward because existing users were backfilled), streak-at-risk alerts sent in the last seven UTC days, and the number of users holding a comeback bonus. Streak KPIs use the raw derived streak without the comeback bonus. D1/D7/D30 return rates use only users with enough post-deployment observation time. The displayed seven-day chart is text-based. The dashboard also reports total deleted accounts and deletions in the last seven UTC days from the tombstone table. Broadcast campaigns are text-only, confirmed by an admin, serialized to one active campaign in the single application process, and sent at 5 messages/second with bounded retries and persisted `RetryAfter` deadlines. Delivery state is persisted and inflight deliveries are retried after restart; a crash after Telegram accepts a message but before the DB update can cause a duplicate. Deleting an account mid-campaign or mid-reminder-sweep is safe: updates to deleted rows are no-ops and counts reflect remaining recipients.

Membership checks run for bot messages and callbacks, except the `check_join` callback itself and the `account_restore` callback. Required channels come from `REQUIRED_CHANNELS`, defaulting to an empty list if unset. Only successful checks are cached, per process, for 300 seconds. A membership-check Telegram error is treated as not joined. Every update also performs one indexed tombstone lookup (`deleted_accounts`) before handlers run, so deleted users never reach `get_or_create`.

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
| `LOG_LEVEL` | `Settings` | Defaults to `INFO`; no logging configuration consuming it was found |

`.env.sample` documents the variables above and an optional placeholder `DATABASE_URL` for local tools. Set the real owner ID and support destinations in the runtime environment; do not commit them. Code supplies a default database URL and Compose overrides it for the bot container.

## Verified Caveats

- The application runs migrations automatically during API lifespan startup by default.
- Telegram polling, reminder work, FSM storage, and membership cache are process-local; use one application instance.
- Reminder delivery holds a DB session while scanning and sending. Each candidate may cause additional reads; consult [docs/PERFORMANCE.md](docs/PERFORMANCE.md) before changing this path.
- No rate limiter for HTTP endpoints was found. Callback handlers validate preset values, numeric IDs, and timezone indexes, but changes must continue to enforce payload parsing and Telegram's 64-byte callback-data limit.