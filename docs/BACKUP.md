# Backup and Restore Design

This document is a design, not an implemented backup job. No script, cron entry, or backup automation is added here.

## Proposed Baseline

- Take a regular PostgreSQL logical backup, initially daily, using `pg_dump -Fc` from the Compose `db` service. The verified service is `db`; the database and user are `bookzma`.
- The owner must choose the number of daily and weekly generations to retain; no retention count is decided here.
- Store backups outside the repository and outside the database volume, under restricted ownership/permissions (for example, mode `600`). The owner decides encryption and off-server replication.
- Detect failure using the command exit status, a non-empty output file, and an operational log. A future implementation may alert an administrator.
- Never commit or place backups in the Docker build context.

Illustrative local command (choose a safe destination outside the repository; this is not a scheduled job):

```sh
docker compose exec -T db pg_dump -U bookzma -Fc bookzma > /secure/backup/path/bookzma-YYYY-MM-DD.dump
```

## Restore Rehearsal

Restore into an empty database on a temporary PostgreSQL instance, for example with `pg_restore --no-owner --no-acl --dbname=<temporary-database> <backup-file>`. Verify expected tables and representative synthetic records, then smoke-test using the separate test bot. Record the commands, elapsed time, and result. Never rehearse against production or overwrite the only backup.

Account deletion must account for older backups: data may remain until those backups expire. Document that limitation to users, and reapply deletion records made after the restored backup.

Integrating backup controls into the bot requires a separate approved spec, server-side authorization, confirmation for destructive actions, and an audited restore design.