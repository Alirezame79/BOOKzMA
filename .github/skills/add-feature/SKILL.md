---
name: add-feature
description: Plan and implement an approved BOOKzMA feature from a spec, preserving existing bot/API behavior and local-owner constraints.
---

# Add Feature

1. Read `AGENTS.md`, the relevant guides, `docs/DECISIONS.md`, and the approved spec. Confirm the ROADMAP item is approved; an idea is not authorization.
2. Before edits, list affected layers/files and effects on data, API/callbacks, auth, performance, tests, docs, Docker, and local `dev_run.py` compatibility. Present options with pros/cons and get owner approval for the plan.
3. Implement reusable logic and tests first, then repository work, bot text in `texts.py`, keyboards in `keyboards.py`, and the handler/router or API route. Validate and bound external input; escape values in Telegram HTML; enforce authorization server-side.
4. Add a new migration if schema changes; never edit an applied revision. Do not add dependencies or expand architecture without owner approval.
5. Run `ruff check . && pytest`, report actual output, update current-behavior docs and ROADMAP, and report any local/Docker check not performed. Never inspect or change `dev_run.py`.