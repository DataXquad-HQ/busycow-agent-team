# Skills — Growth Agent (Maya)

Each skill is a self-contained folder. Copy the entire folder when installing — not just `SKILL.md`.

```bash
cp -r artifacts/agents/maya/skills/* ~/.hermes/profiles/<your-agent>/skills/
```

After copying, restart your Hermes session. Replace any target-environment assumptions before first use.

---

## Active packaged skill

| Skill | What it does | Capability |
|---|---|---|
| `blog-content-crew` | Run a 4-agent CrewAI flow to research, draft, and review a long-form blog post from a brief | C2 — Long-form Content & Newsletter |

---

## Notes

- This artifact currently packages Maya's core long-form drafting skill first.
- Shared reusable copies also live under `../../shared-skills/blog-content-crew/`.
- Publishing, backlog intake, and cron wrappers should be installed separately in the target environment.
