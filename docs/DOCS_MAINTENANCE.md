# Documentation Maintenance

Update documentation in the same change as the behavior. Each fact should have one canonical home; other files link to it. `ARCHITECTURE.md` and `BOT_GUIDE.md` describe verified current behavior only. Put proposals in `docs/ROADMAP.md` or `docs/DECISIONS.md` and label them clearly.

| Changed area | Update |
| --- | --- |
| Runtime structure or request flow | `ARCHITECTURE.md` |
| Command, callback, FSM state, route, table, env variable, or limit | `BOT_GUIDE.md` and, when needed, `.env.sample` |
| Local setup, entrypoint, Docker, or Compose | `docs/LOCAL_DEV.md` and `README.md` |
| Technical decision or rejected alternative | `docs/DECISIONS.md` |
| Feature status | `docs/ROADMAP.md` |
| Test workflow or coverage | `docs/TESTING.md` |
| Security behavior or threat model | `docs/SECURITY_PRACTICES.md` |
| Agent rules | `AGENTS.md` and pointer-only tool files |
| Owner workflow with AI | `docs/vibe/` |
| Spec process or acceptance criteria | `docs/specs/TEMPLATE.md` |

Keep `AGENTS.md` under roughly 100 lines. When adding a rule, consolidate or remove duplication. Tool-specific files point to `AGENTS.md`; they are not copies. Remove or revise docs when the corresponding behavior is removed. Before a release, or monthly, run the P-12 documentation audit in `docs/vibe/PROMPTS.md`.