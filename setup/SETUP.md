# Hermes + Lark + GBrain — Stack Setup

Run this once after completing Step 0 (Prerequisites) in the root README.

This setup:
1. Writes `SOUL.md` — installs knowledge routing rules into Hermes
2. Scaffolds `MEMORY.md` — initialises memory structure

---

## Step 1 — Write SOUL.md

Fetch the template and write to `~/.hermes/SOUL.md`:

```
Fetch: https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/setup/templates/SOUL.md
Write to: ~/.hermes/SOUL.md
```

This installs the knowledge routing rules — where to store and where to read data across Memory, GBrain, Skills, and session history.

---

## Step 2 — Initialise MEMORY.md

Ask the user the following questions, then fill in and write `~/.hermes/MEMORY.md`:

```
Questions to ask:
1. What is your company name and what does it do? (one sentence)
2. What is the Lark Base token for your main operations base?
3. What is your preferred language for Hermes responses? (English / Chinese / other)
4. Any other platforms or tools Hermes should know about? (Telegram, WhatsApp, Notion, etc.)
```

Then fetch the template and fill in the answers:
```
Fetch: https://raw.githubusercontent.com/DataXquad-HQ/busycow-playbooks/main/setup/templates/MEMORY.md
Fill in the {{placeholders}} with user's answers
Write to: ~/.hermes/MEMORY.md
```

---

## Step 3 — Verify

Ask the agent:
- "What are the routing rules for storing information?" → should describe Memory/GBrain/Skill decision tree
- "What company am I working with?" → should return the company name from Memory

---

## Next Step

Proceed to `core/SETUP.md`.
