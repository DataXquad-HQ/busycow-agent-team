---
name: routing-report-delivery
description: >
  Design reporting workflows that can run both manually and by cron without duplicating long output.
  Use when the same logic lives in a skill, but cron should deliver the full human report to a business
  channel and return only a short execution receipt to the system/backend channel.
triggers:
  - "manual and cron reporting"
  - "avoid duplicate cron report"
  - "cron receipt vs full report"
  - "same skill manual and scheduled"
  - "report should go to channel but cron stay short"
  - "avoid duplicated cron report"
  - "shared manual and scheduled report"
  - "backend receipt"
version: "1.0"
---

# Routing Report Delivery

## When to Use

Use this pattern when a workflow can be run in two modes:
1. **Manual** — a human asks for the report right now
2. **Scheduled** — a cron job runs the same logic automatically

The goal is to keep **one canonical report format** in the skill while preventing cron runs from posting the same long report twice.

---

## Core Principle

**The skill owns the logic and the full report format.**
**The cron job owns delivery and returns only a short receipt.**

Do not treat the cron final response as the formal report body.
The cron final response is only a delivery receipt / ops summary.

---

## Standard Output Contract

Every dual-mode reporting workflow should have three layers:

### 1. Full Human Report
The real report people should read.
Examples:
- Weekly pipeline health report
- Monthly strategy check
- Daily ops briefing
- Customer health review

### 2. Delivery Notice (optional)
A one-line intro sent with the report when useful.
Examples:
- `📊 Weekly pipeline health check ready`
- `🧭 Monthly strategy check complete`

### 3. Cron Receipt / Ops Summary
A short execution summary for the backend/system channel.
Include only:
- success / failure
- delivery target
- top-line status
- counts analyzed
- tasks or alerts created
- blockers / fallbacks / errors

Never paste the full report body here.

---

## Mode Rules

## Manual Mode
When a human directly asks for the report:
- Run the reporting logic
- Return the **full report** in the current conversation
- Do not create a second backend-style receipt unless explicitly asked

In manual mode:
**full report = final response**

## Cron Mode
When the same workflow runs from cron:
- Run the same reporting logic
- Send the **full report** to the designated business channel
- Return only a **short receipt** in the cron final response
- Route that receipt to the system/backend destination

In cron mode:
**full report ≠ final response**

---

## Canonical Pattern

### Skill responsibilities
The skill should define:
- what data to gather
- how to analyze it
- what the formal report format is
- quality checks
- fallbacks
- what counts as the top-line result

### Cron prompt responsibilities
The cron prompt should define:
- where the full report is delivered
- where the cron receipt goes
- that the final response must stay short
- what fields the receipt should include

---

## Cron Prompt Template

Use this structure when a cron job runs a reporting skill:

```text
Load the [skill-name] skill and follow its report logic.

Generate the full human-facing report and deliver it to [business channel].
Do not repeat the full report in your final response.

Your final response must be a short backend receipt only, containing:
- delivery status
- target channel
- top-line result
- number of items analyzed
- tasks / alerts created
- blockers, fallbacks, or errors
```

If the workflow also needs a short intro in the business channel, say so explicitly:

```text
Send the full report to [business channel] with a one-line intro:
"📊 Weekly pipeline health check ready"
```

---

## Receipt Template

Use this shape for cron final responses:

```md
✅ [Report name] generated and delivered.
- Target: [channel]
- Top-line result: [e.g. WATCH / ON_TRACK / 3 blockers]
- Items analyzed: [count]
- Tasks / alerts created: [count]
- Fallbacks / errors: [brief note or "none"]
```

If delivery fails:

```md
❌ [Report name] not fully delivered.
- Intended target: [channel]
- Stage reached: [generated / partial send / failed before send]
- Items analyzed: [count]
- Tasks / alerts created: [count if any]
- Blocking issue: [exact error]
- Retry guidance: [what to do next]
```

---

## Channel Separation Rule

Use this separation consistently:

| Content type | Destination |
|---|---|
| Full business report | Business-facing channel |
| Short receipt / ops summary | System / Backend Report |
| Raw machine noise | System / Backend Report only |

Do not mix them.
If humans need the report, send the report once to the business channel.
If operators need traceability, send the short receipt once to backend.

---

## Examples

### Example A — Weekly Pipeline Health Report
- **Skill** defines the full health report structure
- **Cron** sends full report to `[Sales] Pipeline and Strategy`
- **Cron final response** goes to `[System] Backend Report` with only:
  - overall health
  - opportunities analyzed
  - partnerships analyzed
  - missing-data tasks created
  - any failures

### Example B — Daily Ops Briefing
- **Skill** defines the morning briefing body
- **Cron** sends full briefing to `[Ops] Internal Operations`
- **Cron final response** says only whether delivery succeeded and what fallback sources were used

---

## Decision Rule: Split Skill or Not?

Usually, **do not split** into separate manual and cron skills.

Prefer:
- one core reporting skill
- one or more cron prompts that wrap it differently

Only split into two skills if the cron run is doing a meaningfully different job.
Examples:
- manual mode = full analytical report
- cron mode = lightweight scan + alert only

If the underlying logic is the same, keep one skill.

---

## Quality Bar

Before using this pattern in a skill or cron design:
- The full report has exactly one canonical home — the skill — not duplicated across the skill and cron prompt?
- Manual mode clearly returns the full report directly, without creating unnecessary backend noise?
- Cron mode clearly separates **full report delivery** from **short final receipt**?
- The cron final response is short enough to scan in seconds and contains no duplicated long-form report sections?
- Business-facing and backend-facing channels are different unless there is an explicit reason to merge them?
- If someone reads only the backend receipt, they can still tell whether the run succeeded, where the report went, and whether any fallbacks were used?

If any check fails, tighten the skill or cron prompt before shipping.

---

## Fallback Behavior

- **If report generation succeeds but channel delivery fails**: do not dump the full report into the cron final response as a fallback. Return a failure receipt with the exact delivery error and say where the report was supposed to go.
- **If one data source fails but the report still runs**: deliver the full report with gaps clearly labelled, and mention the fallback in the short receipt.
- **If both business-channel delivery and backend delivery fail**: save the shortest possible failure summary in the cron output and retry or escalate through the next available system path.
- **If the workflow is manually invoked while also scheduled by cron**: manual mode still returns the full report directly. Do not force backend-style brevity into the interactive response.

---

## Pitfalls

- **Do not paste the full report twice.** This is the failure mode the pattern is meant to prevent.
- **Do not move report logic into the cron prompt.** The prompt should wrap delivery, not redefine analysis.
- **Do not let backend receipts become mini-reports.** If the receipt grows into a second report, cut it back.
- **Do not use the same channel for the formal report and noisy execution log** unless the audience truly wants both mixed together.
- **Do not split one workflow into separate manual/crons skills too early.** One core skill is easier to maintain.
- **Do not hide delivery failures by stuffing the full report into the receipt.** A failed send should look like a failed send.
