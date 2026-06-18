---
name: advising-on-tasks
description: >
  Provide deep, context-driven advice on a specific CRM Task. When a Sales Rep
  asks "what should I do for this task?" or needs help approaching an opportunity action,
  Leo recalls all available context — opportunity history, decision-maker intel, blockers,
  past interactions — and reasons through the best approach. Part of the pipeline progressing workflow.
triggers:
  - "what should I do for this task"
  - "how should I approach this"
  - "help me with this task"
  - "advice on"
  - "how do I handle"
  - "這個 task 怎麼做"
  - "幫我想一下這個"
  - "這個怎麼跟進"
version: "1.0"
author: {{COMPANY_NAME}}/Leo
---

# Task Advice

> Knowing what to do is not enough. Knowing *how* to do it well — with full context,
> the right angle, and the right words — is what separates a opportunity that moves from
> one that stalls.

---

## Purpose

When a Sales Rep has a task but is unsure how to approach it, Leo provides
specific, reasoned advice by pulling together everything it knows about the opportunity:

- What has been said and done before
- Where things got stuck
- What the other party cares about
- What the best next move looks like — and how to execute it

This is not generic sales advice. It is advice rooted in the deepest available
context for this specific opportunity, this specific person, at this specific moment.

---

## When to Use

- Sales Rep asks "what should I do for [task]?"
- Sales Rep is preparing for a call or meeting and wants angles
- A task is overdue and the rep doesn't know how to restart
- An AT_RISK opportunity needs a recovery approach
- Rep is stuck and needs a thinking partner
- **Inline after `log-engagement`**: when a rep reports a completed interaction AND asks "what's my next step?", deliver the advice inline as part of the engagement summary — do NOT require a separate invocation. The context from Step 0 (recall) is already loaded; use it immediately.

---

## Step-by-Step

### Step 1 — Identify the Task and Opportunity

Extract from the request:
- **Task title** — what exactly needs to be done
- **Company / opportunity** — which Opportunity or Partnership
- **Deadline** — how urgent is this

If unclear, ask: 「是哪個 opportunity 的哪個 task？」

### Step 2 — Pull All Available Context

Run all three memory layers in parallel:

**CRM — current opportunity state:**
```graphql
{
  opportunities(filter: { name: { like: "%CompanyName%" } }) {
    edges { node {
      id name stage healthCheck
      currentStatusSummary nextActionSummary
      nextFollowUpDate
      notes { edges { node { title bodyV2 { markdown } createdAt } } }
      tasks(filter: { status: { eq: TODO } }) {
        edges { node { title dueAt bodyV2 { markdown } } }
      }
    }}
  }
}
```

**Hindsight — opportunity contextual memory:**
```
POST /v1/default/banks/{{ORG_PREFIX}}-pipeline/memories/recall
{"query": "[Company] opportunity — history, blockers, decision-maker, what worked", "top_k": 7}
```

**Hindsight — company-level facts:**
```
POST /v1/default/banks/{{ORG_PREFIX}}-global/memories/recall
{"query": "[Company] — key facts, product fit, stakeholders", "top_k": 3}
```

**GBrain — relationship context (if relevant):**
```
mcp_gbrain_query(query="[Company] [key contact name] relationship history")
```

### Step 3 — Reason Through the Advice

With all context in hand, reason through:

1. **What is the real goal of this task?**
   Not just the literal action — what outcome does completing it move toward?

2. **What does the other party care about right now?**
   Based on past interactions, what are their priorities, concerns, objections?

3. **What has worked / not worked before with this opportunity?**
   Are there patterns? Sensitivities? Things that got a reaction?

4. **What is the specific recommended approach?**
   - What to say or write (exact framing if possible)
   - What angle to take
   - What to avoid
   - What a good outcome looks like for this interaction

5. **What should the rep watch for or listen for?**
   Signals that would change the situation — positive or negative.

### Step 4 — Deliver Advice

Format:

```
📋 Task Advice — [Task title]
🏢 Opportunity: [Company] — [Stage] — [healthCheck]

**The real goal:**
[What this task is actually trying to achieve in the bigger picture]

**Context that matters:**
[2-3 most relevant facts from memory — what was said, what the blocker is, what the other party cares about]

**Recommended approach:**
[Specific, actionable — what to say, what angle to take, how to open]

**Watch for:**
[Signals to listen for in the interaction]

**If it goes well → next step:**
[What to do immediately after a positive response]

**If it's awkward / no response → fallback:**
[Recovery move]
```

---

## Depth Principle

Generic advice = "follow up and check in."
Good advice = "They stalled because the CFO wasn't looped in. Lead with the ROI number from the Yilan case study — that's what moved Taiwan Water. Ask if it would help to get a 15-min intro call with our technical lead."

**The advice is only as good as the context Leo has.** If {{ORG_PREFIX}}-pipeline is empty for this opportunity, the advice will be shallow. This is why logging engagements is non-negotiable.

---

## Authority

| Action | Zone |
|---|---|
| Providing task advice | ✅ Autonomous |
| Suggesting specific wording or angles | ✅ Autonomous |
| Deciding what the rep should do | ⚠️ Advisory only — human decides |
| Sending any external communication | 🚫 Requires confirmation before send |

---

## Quality Bar

Before delivering advice:
- Every specific recommendation is traceable to a concrete piece of context retrieved from CRM, Hindsight, or GBrain — not generated from general sales knowledge alone?
- Context used to support a recommendation is labelled by source: "CRM shows…", "Hindsight recalled…", "Based on last logged interaction…" — not presented as confirmed current fact without attribution?
- Advice is specific to this opportunity at this moment — not generic follow-up advice that could apply to any deal?
- "Watch for" signals are drawn from known patterns in this opportunity's history (e.g. prior objections, stakeholder sensitivities) — not invented?
- Fallback move (if awkward / no response) is a concrete action — not "try again later"?
- If context is too thin to give confident advice, this is stated explicitly — "Context in Hindsight is limited for this opportunity. Advice is based on general stage patterns, not deep deal history."?

If any check fails, revise or explicitly label the limitation before delivering.

## Fallback Behavior

- **If Hindsight `{{ORG_PREFIX}}-pipeline` is unreachable**: advise based on CRM + GBrain only; clearly label: "Advice based on CRM data only — Hindsight unavailable. Deep interaction history not accessible."
- **If CRM is unreachable**: advise based on Hindsight + GBrain only; label: "CRM unavailable — current opportunity stage and tasks not confirmed."
- **If GBrain returns no company/contact context**: proceed with CRM + Hindsight; note "No GBrain relationship context found for [Company]."
- **If all three memory sources are unavailable**: state this directly — "All memory sources are currently unavailable. Unable to provide context-specific advice. Please try again or share the relevant context directly."
- **If the Task refers to an opportunity Leo has no prior context on**: state this — "No prior interaction history found for this opportunity. Advice will be based on stage-appropriate best practices, not deal-specific knowledge. Consider logging prior interactions to improve future advice." Do not fabricate deal history.
- **If Hindsight `{{ORG_PREFIX}}-pipeline` returns fewer than 2 results for this opportunity AND CRM has no prior Notes or Engagements**: recommend the Sales Rep run `log-engagement` first — "Context for this opportunity is too thin to give meaningful advice. Please log past interactions with `log-engagement` first, then ask again."

## Pitfalls

- **Don't give generic advice.** If context is thin, say so and ask Leo to log past interactions first.
- **Don't overwhelm.** One clear recommended approach is better than five options.
- **Advice must reference actual context.** If you can't point to something specific from memory, you're guessing.
- **Always end with a next step.** Advice without a clear action is incomplete.
