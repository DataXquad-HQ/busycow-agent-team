---
name: logging-sales-activities
description: >
  Log a sales interaction (call, meeting, demo, WhatsApp, follow-up) into the
  Activities table in the Sales CRM Base. Use when user describes a business
  interaction they just had or want to record. Always probe for full context
  before saving. If a clear next action emerges, create a task.
triggers:
  - "剛跟"
  - "打了電話"
  - "開了會"
  - "見了"
  - "follow up"
  - "demo 完"
  - "發了訊息"
  - "log 一下"
  - "記錄一下這次"
---

# Logging Sales Activities

## Sales CRM Base
- App token and table IDs: stored in Memory as "Sales CRM Base"
- **Activities table** is the target

## Activities Table Fields
| Field | Notes |
|-------|-------|
| Summary | One-line: `[Type] [Contact] @ [Account] — [outcome]` |
| Account | Company name |
| Contact | Person spoken to |
| Type | Call / Meeting / Demo / Email / WhatsApp / Site Visit / Other |
| Client Response | What they said / their reaction |
| Stage Advanced? | Did the deal move forward? (boolean) |
| Next Action | What needs to happen next |
| Date | When it happened (ms timestamp) |
| Owner | Who conducted the interaction |

---

## Mandatory Probing — 7 Questions (never skip)

```
1. WHO    — Name + company
2. HOW    — Call / WhatsApp / Meeting / Email / Demo?
3. DATE   — When? (default today)
4. WHAT   — What was discussed? Key points?
5. REACTION — How did they respond? Positive/negative signals?
             Budget, timeline, decision-maker mentioned?
6. OUTCOME — Did the deal move forward?
7. NEXT STEP — Who does what, by when?
```

If user gives vague answers on 4, 5, or 7 — ask again. These three are most important.

---

## Logging Steps

1. Collect all 7 answers
2. Build Summary: `[Type] [Contact] @ [Account] — [one-line outcome]`
3. Create record in Activities table via Lark API
4. Confirm: "✅ 已記錄：[Summary]"

---

## GBrain Write (after Lark save)

If the interaction revealed meaningful intel:
```
extract_facts(turn_text="[Contact] @ [Company], [Date]\n[Client Response]\nNext: [Next Action]")
```

If stage advanced:
```
add_timeline_entry(slug="companies/[shortname]", date="YYYY-MM-DD",
  summary="[Type] with [Contact] — [outcome]", detail="[full response + next action]")
```

Skip GBrain write if: generic "touched base, waiting" with no new signals.

---

## Task Creation

After logging, if Next Action contains: someone + something specific + a timeframe → create a task.

Skip task if: "等對方回覆", "待確認" (vague / waiting on other party).

---

## Pitfalls
- Type must match existing SingleSelect options exactly
- Date = millisecond timestamp UTC
- Stage Advanced? = boolean True/False, not string
- If Account doesn't exist in CRM yet → log in activity anyway, then suggest adding via capturing-sales-intel
