---
name: running-strategic-council
description: >
  Run a multi-agent strategic council to pressure-test a business goal before acting.
  Use when user says "幫我想清楚這件事", "strategic review", "OKR", "help me plan X",
  or when a goal needs adversarial debate before committing. Spawns Architect, Critic,
  Executor, and Market Scout agents in parallel. Includes BusyCow and [your product] $1M ARR
  session learnings as hard-won pitfalls.
triggers:
  - "strategic discussion"
  - "goal achievement"
  - "multi-agent planning"
  - "debate this"
  - "help me achieve"
  - "strategic review"
  - "plan and execute"
  - "OKR"
  - "north star goal"
category: autonomous-ai-agents
version: "1.3"
---

# Strategic Goal Achiever — Skill

A structured multi-agent discussion framework that separates **Strategic Planning** from **Execution**, drawing from Chief Agent Framework, MCP-RLM, Pew Pew Plaza Packs, and goal-driven LLM research.

---

## Core Philosophy

> **"Clarity before action. Criteria before strategy. Review before execution."**

Three sources of failure in goal achievement:
1. **Fuzzy goals** — no shared definition of "done"
2. **Unchallenged plans** — good ideas never tested against adversarial thinking
3. **Premature execution** — acting before the plan is sound

This skill fixes all three by enforcing a structured, multi-agent process.

---

## Cognitive Frameworks (Mandatory — Applied by All Agents)

Every agent in the council must process the goal through these mental models **before** producing output. These are not optional — they prevent yes-man behavior and surface hidden friction.

| Framework | How to Apply |
|---|---|
| **First Principles** | Strip the goal to its atomic mathematical/physical truths. What is actually required (revenue, customers, time, people)? Base strategy on those numbers, not analogies or wishes. |
| **MECE** | When breaking down problems or solutions: are categories mutually exclusive (no overlap)? Are they collectively exhaustive (nothing left out)? Every milestone breakdown must pass MECE. |
| **Pareto 80/20** | Identify the 1–3 actions that drive 80% of results. Ruthlessly cut low-ROI tasks. Every plan must have an explicit "80/20 Levers" section. |
| **Pre-Mortem (Inversion)** | Before finalizing any plan: "If this fails in 6 months, what was the most likely cause?" Build contingencies for those exact failure points. The Critic agent leads this — but all agents apply it. |

**Behavioral Rules (apply to all agents and the orchestrator):**
- **Challenge Unrealistic Goals:** If the goal violates resource constraints or mathematical reality, say so explicitly and propose a grounded alternative. Do not validate wishful thinking.
- **No Fluff:** No corporate jargon. Be concise, information-dense, ruthlessly practical.
- **Acknowledge Friction:** Always highlight the hardest part of the plan. Do not pretend execution is easy.
- **Silent Pre-Processing:** Before producing any output, each agent must silently run through: (1) Deconstruction — what atomic metrics does this require? (2) Resource Audit — what time/budget/people are realistically needed? (3) Constraint Mapping — what are the hard limits and bottlenecks? (4) Strategic Sequencing — what must happen first, second, third?

---

## The Six-Phase Protocol

```
Phase 0:   ORGANIZATIONAL REALITY CHECK  → GBrain context, prior decisions
Phase 0.5: MARKET INTELLIGENCE LAYER     → TAM/SAM/SOM, positioning, ICP, competition
Phase 1:   GOAL CRYSTALLIZATION          → Define what "done" looks like (8 questions)
Phase 2:   PARALLEL AGENT COUNCIL        → 4 agents debate from different lenses
Phase 3:   PLAN REVIEW (Red Team)        → Adversarial check before action
Phase 4:   EXECUTION ROADMAP             → Milestone breakdown with owners
Phase 5:   VERIFICATION GATE             → How we know the goal was achieved
Phase 5.5: DECISION LOGGING              → Log to GBrain for future sessions
```

> **Why Phase 0.5 was added (learned from [your product] session, May 2026):**
> A council debating how to hit $1M revenue without first sizing the market will confidently plan toward a ceiling that doesn't exist. [your product]'s existing plan forecast $157k — the $843k gap was invisible until market sizing was done. Positioning determines ICP, ICP determines channel, channel determines achievable SOM. None of this can be assumed — it must be researched before agents are spawned.

---

## Agent Roles (The Council)

| Role | Persona | Responsibility |
|------|---------|----------------|
| 🏛️ **The Architect** | Chief Planner | Decomposes goal into milestones, defines constraints, owns the plan |
| ⚔️ **The Critic** | Devil's Advocate | Finds logical contradictions, resource gaps, procurement/cycle risks |
| 🔧 **The Executor** | Pragmatist | Translates plans into concrete actions, flags what's actually buildable |
| 🔬 **The Verifier** | Scientist | Defines measurable acceptance criteria, checks if outcomes are provable |
| 🗺️ **The Market Scout** | Market Intelligence | Sizes TAM/SAM/SOM, maps competition, defines ICP, validates channel fit |

> **Why 4 agents became 5 (learned from [your product] session):**
> The original 3-agent council produced plans that were internally consistent but externally wrong — they didn't know the market size, the competitive landscape, or the precise buyer. The Market Scout agent exists to ground the council in market reality before the Architect builds a plan on top of it.

---

## Step-by-Step Instructions

### Phase 0: ORGANIZATIONAL REALITY CHECK (NEW — learned from GBrain CEO Review)

**Before crystallizing the goal**, query GBrain for existing organizational context. This prevents the council from debating in a vacuum.

```
1. gbrain query "decisions related to [goal domain] in the last 90 days"
   → Are there prior decisions that constrain or inform this goal?

2. gbrain query "skill gaps in [relevant domains]"
   → Is the team actually capable of executing the plan?

3. gbrain query "bus risks" (severity: critical or high)
   → Are there single points of failure that would block execution?

4. gbrain query "who is accountable for [goal domain]"
   → Who must sign off? Who needs to be consulted? Who gets informed?
```

If GBrain is not available, ask the user these 4 questions directly before proceeding.

Surface findings to the user before Phase 1:
> "Before we set strategy, here's what our organizational memory shows: [findings]. Does this change the goal or constraints?"

---

---

### Phase 0.5: MARKET INTELLIGENCE LAYER (NEW — learned from [your product] session)

**Run this BEFORE Phase 1 goal crystallization** for any revenue, product, or market-entry goal.
Skip only if the market is already well-understood and documented in GBrain.

This phase spawns the **Market Scout agent** independently, or the orchestrator researches directly.

#### What to research:

```
1. MARKET SIZING (TAM/SAM/SOM)
   - TAM: Total addressable market for this product/service globally or in target region
   - SAM: Serviceable addressable market — buyers you can realistically reach
   - SOM: Serviceable obtainable market — what this team can close in the timeframe
   - Revenue ceiling check: Does the SOM support the revenue goal? If not, goal needs redesign.

2. PRODUCT POSITIONING
   - What segment is the product positioned IN? (e.g. cloud vs on-premise, SME vs enterprise)
   - What segment is it deliberately positioned AGAINST? (deliberate exclusion matters)
   - What does "positioned against" mean for messaging? (e.g. "every competitor needs internet — we don't")
   - Positioning determines ICP. ICP determines channel. Channel determines SOM. Get this right first.

3. ICP DEFINITION (Ideal Customer Profile)
   - Exact job title of the economic buyer (who signs the PO)
   - Exact job title of the user/champion (who uses it daily)
   - Company/agency type and size
   - TRIGGER EVENT — what specific event makes them buy NOW vs later?
     (e.g. "they just had a flood and the cloud tools didn't work")
   - Budget range and approval process (who else must sign?)
   - Procurement cycle length (weeks for commercial, months/years for government)
   - What they currently use to solve this problem (the "before" state)
   - Where they search for solutions (Google keywords, communities, events)

4. COMPETITION LANDSCAPE
   - Who are the direct competitors in this specific positioning?
   - Who are the indirect/substitute competitors?
   - What are competitors' prices, procurement models, and weaknesses?
   - Is there a "gap" in the competitive landscape that [your product]/product occupies alone?
   - Who could credibly copy this positioning in 12–24 months?
   - What certifications, partnerships, or reference customers create a moat?

5. CHANNEL FIT CHECK
   - Does the proposed channel actually reach the ICP?
   - What is the procurement cycle of the channel's end buyer?
   - Does the channel partner have economic incentive at this price point?
   - Hardware/product bundles: Is a manufacturer bundle strategy viable?
     (e.g. [your product] + Wingtra drone = complete offline survey system)
   - Entry product buyer check: If using an entry product to land-and-expand,
     does the entry product buyer = the core product buyer? If not, redesign.
```

#### MARKET SCOUT Agent Prompt Template:
```
You are THE MARKET SCOUT — a market intelligence agent in a multi-agent goal council.
Your job is to ground the council in market reality BEFORE the plan is built.
Bad plans are built on assumed markets. Your job is to replace assumptions with facts.

PRODUCT/SERVICE: {product_description}
GOAL: {revenue_or_market_goal}
GEOGRAPHY: {target_markets}
TIMEFRAME: {timeline}

Research and answer ALL of the following. Use web search for real data.

1. TAM/SAM/SOM
   - TAM: What is the total addressable market for this product in the target geography?
     Give a number with a source or reasoning, not a vague range.
   - SAM: How many buyers can realistically be reached given the team size, channels,
     and geography? Filter TAM by realistic access.
   - SOM: Given [team size] and [timeframe], how many deals can realistically close?
     State the math: deals × avg deal size = SOM.
   - REVENUE CEILING CHECK: Does the SOM support the stated revenue goal?
     If SOM < goal: say so explicitly. The goal requires redesign or a different model.

2. POSITIONING
   - What is the product's defensible positioning? (what makes it different and hard to copy)
   - What segment is it deliberately NOT competing in? Name the competitors left behind
     and why that's correct.
   - Positioning statement (one sentence): "For [ICP], [product] is the only [category]
     that [key differentiator], unlike [alternatives] which [key weakness]."

3. ICP (define TWO if there are primary and secondary buyers)
   For each ICP:
   - Job title (buyer) + job title (user/champion)
   - Company/agency type and size
   - Top 2 trigger events that make them buy NOW
   - Procurement cycle (weeks? months? years?)
   - Budget range and approval process
   - Current solution they use (the "before" state)

4. COMPETITION
   - List top 3–5 direct competitors in THIS specific positioning segment
   - For each: pricing, offline/cloud status, key weakness, Asia presence
   - Identify any gap in the competitive landscape that the product uniquely fills
   - Who could copy this in 12–24 months? How defensible is the moat?

5. CHANNEL VALIDATION
   - For each proposed channel: can it actually reach the ICP?
   - Procurement cycle of the channel's end buyer?
   - Economic incentive for the channel partner at this price point?
   - Is a hardware/product bundle strategy viable? Name specific manufacturers.
   - Does the entry product (if any) land with the same buyer as the core product?
     If not, flag it — this is a critical GTM failure mode.

Output format:
### Market Reality Summary
[3-sentence bottom line: market size, positioning verdict, ICP in plain language]

### TAM / SAM / SOM
[Numbers with reasoning. Revenue ceiling check vs stated goal.]

### Positioning Statement
[One sentence. Name what you're not competing with.]

### ICP #1 — [Name]
[Table: title, trigger, cycle, budget, current solution]

### ICP #2 — [Name] (if applicable)
[Same format]

### Competition Landscape
[Table: competitor, pricing, weakness, Asia presence]
[Gap analysis: what space does the product uniquely occupy?]

### Channel Validation
[For each proposed channel: reach ✅/❌, cycle, incentive, verdict]
[Bundle opportunity: yes/no, with whom, revenue model]

### Market Scout Verdict
MARKET VALIDATED / MARKET TOO SMALL / WRONG POSITIONING / REDESIGN CHANNEL
[Exact reasoning — 3 sentences]
```

#### After Market Scout runs, surface findings before Phase 1:
> "Before we lock the goal, here's the market reality: [TAM/SAM/SOM summary].
> The revenue ceiling for this positioning is approximately [SOM].
> [If SOM < goal]: The goal requires either a different market, a different channel,
> or a larger deal size. Shall we adjust before proceeding?"

**If SOM < stated revenue goal — resolve this before Phase 1. Do not proceed.**

---

### Phase 1: GOAL CRYSTALLIZATION (GStack-Style Structured Questions)

**Inspired by GStack /office-hours:** Before spawning any agents, run a mandatory structured question ritual. Do NOT skip or merge questions. Ask them one at a time or as a numbered list, but require answers to all before proceeding.

**The 8 Questions (must answer all — expanded from 6):**

```
Q1. North Star: What does success look like in ONE concrete sentence?
Q2. Deadline: By when must this be achieved? (hard deadline or target date)
Q3. Constraints: What are the hard limits? (budget, people, technology, procurement cycles)
Q4. Stakeholders: Who is Accountable? Who must be Consulted? Who gets Informed?
Q5. Current State: What exists today? What has already been tried? What is current revenue/traction?
Q6. Acceptance Criteria: How will we VERIFY it's done — what evidence, metric, or event proves success?
Q7. Positioning: What market segment are we IN, and what are we deliberately NOT competing in?
     (e.g. "on-premise disaster response, NOT cloud-based commercial mapping")
     If unclear: run Phase 0.5 Market Scout first.
Q8. ICP: Who is the economic buyer — exact job title, company type, and what triggers their purchase NOW?
     If unclear: run Phase 0.5 Market Scout first.
```

> **Why Q7 and Q8 were added (learned from BusyCow and [your product] sessions):**
> Q7 (positioning) prevents agents from accidentally competing in the wrong segment.
> [your product] almost competed against cloud platforms — a market too crowded and expensive.
> Deliberate exclusion is as important as deliberate inclusion.
> Q8 (ICP trigger) prevents agents from building a plan for a buyer who doesn't exist yet.
> "Government agencies" is not an ICP. "Taiwan county fire bureau director, triggered by
> a recent earthquake that revealed their cloud tools failed" is an ICP.

**Completeness Score (learned from GStack):** After collecting answers, rate the goal definition:
> "Goal Completeness: [N]/10 — [what's still fuzzy or missing]"

If score < 7/10, surface the gaps and ask for clarification before proceeding.

**If any field is missing — ASK before proceeding. Do not assume.**

Locked goal template (fill before Phase 2):
```markdown
## Goal Lock
- **North Star:** [1 sentence]
- **Deadline:** [date/timeframe]
- **Constraints:** [list — include procurement cycle if B2G]
- **RACI:** Accountable=[name], Consulted=[names], Informed=[names]
- **Current State:** [what exists, current revenue/traction]
- **Acceptance Criteria:** [measurable, verifiable — SMART format]
- **Completeness Score:** [N]/10
- **Positioning:** [segment IN] vs [segment deliberately NOT competing in]
- **ICP:** [job title] at [company type], triggered by [specific event]
- **TAM / SAM / SOM:** [from Market Scout — revenue ceiling confirmed]
- **Competition Gap:** [what space product uniquely occupies]
- **Prior Decisions:** [from GBrain, or "none found"]
- **Known Skill Gaps:** [from GBrain, or "none found"]
- **Active Bus Risks:** [from GBrain, or "none found"]
```

---

### Phase 2: PARALLEL AGENT COUNCIL

Spawn 3 agents in parallel using `delegate_task` with distinct personas:

```python
delegate_task(tasks=[
    {
        "goal": ARCHITECT_PROMPT,
        "toolsets": ["web"]  # or terminal/file as needed
    },
    {
        "goal": CRITIC_PROMPT,
        "toolsets": ["web"]
    },
    {
        "goal": EXECUTOR_PROMPT,
        "toolsets": ["web"]
    }
])
```

#### ARCHITECT Agent Prompt Template:
```
You are THE ARCHITECT — a strategic planner agent in a multi-agent goal council.
Apply MECE thinking (mutually exclusive, collectively exhaustive) to all breakdowns.
Apply First Principles: base the plan on mathematical/resource reality, not assumptions.
Before writing anything, silently process: (1) What atomic metrics does this goal require?
(2) What resources are realistically needed? (3) What are the hard constraints?
(4) What is the critical sequence?

GOAL: {north_star_goal}
DEADLINE: {deadline}
CONSTRAINTS: {constraints}
CURRENT STATE: {current_state}
POSITIONING: {positioning_in} — deliberately NOT competing in: {positioning_out}
ICP: {icp_title} at {icp_company}, triggered by {icp_trigger}
TAM/SAM/SOM: TAM={tam}, SAM={sam}, SOM={som} — revenue ceiling = {som}
COMPETITION GAP: {competition_gap}
PRIOR DECISIONS (from GBrain): {prior_decisions}
KNOWN SKILL GAPS: {skill_gaps}

Your job:
1. REALITY CHECK — does the math work? State: goal={revenue_goal}, SOM={som}.
   If SOM < goal, the plan must explain HOW to expand the SOM, not just assume it.
2. POSITIONING LOCK — confirm the product is competing in the right segment.
   Name what it is NOT competing against and why that's the correct choice.
3. CHANNEL-ICP FIT — does each proposed channel actually reach the ICP?
   State the procurement cycle length for each channel's end buyer.
   Flag any entry product whose buyer ≠ core product buyer.
4. Identify the 80/20 LEVERS — the 1-3 actions that drive 80% of results.
5. Decompose into 3-5 MILESTONES (MECE), each with a measurable success signal.
6. FLAG PROCUREMENT CYCLE RISK — for B2G goals, map which deals must enter
   procurement by what date to close within the timeline. Any deal started after
   [deadline minus avg cycle] is a 2028 deal, not a 2027 deal. Say this explicitly.
7. Flag RESOURCE REQUIREMENTS with realistic estimates (not optimistic ones).
8. If the goal is unrealistic given SOM or procurement cycles, say so and propose
   a grounded alternative.

Output format:
### I. Reality Check
[Math: goal vs SOM. Procurement cycle analysis. Honest verdict on achievability.]

### II. Positioning Lock
[Confirm segment. Name what's excluded and why it's right.]

### III. 80/20 Strategic Levers
[1-3 highest-impact actions. Everything else explicitly labeled secondary.]

### IV. Channel-ICP Fit
[For each channel: reaches ICP? procurement cycle? entry product buyer match?]

### V. Milestone Breakdown (MECE)
#### M1: [Name] — Due: [date]
- Success Signal: [measurable]
- Tasks (critical path order): [list]
- Dependencies: [what must exist first]
- Procurement deadline: [latest date to enter process and close in time]
[repeat M2-M5]

### VI. Resource Map
[Time / budget / people — realistic, not optimistic]

### VII. Confidence Assessment
[Highest-risk assumption. What must be true for the plan to work?]
```

#### CRITIC Agent Prompt Template:
```
You are THE CRITIC — a devil's advocate agent in a multi-agent goal council.
Apply Pre-Mortem thinking: "If this plan fails in [timeframe], what was the most likely cause?"
Apply First Principles: strip away optimistic assumptions and check what the numbers actually say.
Do NOT be diplomatic — honest friction identification is more valuable than encouragement.

GOAL: {north_star_goal}
DEADLINE: {deadline}
CONSTRAINTS: {constraints}
STAKEHOLDERS: {stakeholders}
SOM (from Market Scout): {som}
POSITIONING: {positioning_in} — NOT competing in: {positioning_out}
ICP: {icp_definition}
COMPETITION GAP: {competition_gap}
PROCUREMENT CYCLE (avg): {procurement_cycle}

Your job:
1. PRE-MORTEM: "This plan failed. What were the top 3 causes?" Be specific.
2. PROCUREMENT CYCLE MATH: Given the avg procurement cycle, what is the LAST DATE
   a new deal can enter the process and still close before the deadline?
   Any deal started after that date is future-year revenue. State this explicitly.
3. SOM CHALLENGE: Is the SOM realistic? What assumption inflates it?
   (e.g. "assumes 20% close rate — is that supported by any evidence?")
4. POSITIONING CHALLENGE: Is the "not competing in X" decision truly defensible?
   Could the excluded segment retaliate or copy the positioning?
5. ICP CHALLENGE: Is the ICP actually reachable via the proposed channels?
   Are there structural barriers (clearance, local entity, certification) blocking access?
6. CHANNEL CHALLENGE: Will proposed channel partners actually sell this, or just agree
   and then do nothing? What is the evidence they will prioritize [your product]?
7. COMPETITION MOAT: How long before a well-resourced competitor copies the positioning?
   What is BusyCow/BusyCow doing to extend the moat before that happens?
8. MOST DANGEROUS ASSUMPTION: The single belief the team holds that, if wrong, collapses
   the entire plan. Name it.
9. MITIGATION for each failure mode.

Output format:
### Pre-Mortem: Top 3 Failure Modes

#### Failure Mode 1: [Name]
- Likelihood: High/Medium/Low
- Impact: Catastrophic/Significant/Minor
- Root cause: [specific, not vague]
- Mitigation: [concrete action]

[FM2, FM3]

### Procurement Cycle Analysis
[Last entry date for deals to close in time. How many deals are already past that date?]

### SOM Challenge
[What assumption inflates the SOM? What is the conservative floor?]

### ICP Access Challenge
[Structural barriers to reaching the ICP. What is most likely to block the first sale?]

### Competition Moat Challenge
[Timeline before moat is threatened. What extends it?]

### Most Dangerous Assumption
[One sentence. The load-bearing belief that collapses everything if wrong.]

### Verdict
PROCEED / PROCEED WITH CAUTION / REDESIGN NEEDED
[Exact reasoning — 3 sentences max]
```

GOAL: {north_star_goal}
DEADLINE: {deadline}
CONSTRAINTS: {constraints}
STAKEHOLDERS: {stakeholders}

Your job:
1. Run the PRE-MORTEM: "This plan failed in 6 months. What were the top 3 causes?"
2. Find LOGICAL CONTRADICTIONS — does the goal conflict with its own constraints?
3. Challenge the RESOURCE ASSUMPTIONS — what is being assumed that may not be available?
4. Challenge the TIME HORIZON — is this realistic given the milestones required?
5. Identify STAKEHOLDER RISKS — who could block this and why?
6. Identify what the ARCHITECT likely got wrong (the most common planning bias: over-optimism on speed, under-estimation of dependencies)
7. Propose MITIGATION for each failure mode

Output format:
### Pre-Mortem: Top 3 Failure Modes

#### Failure Mode 1: [Name]
- Likelihood: High / Medium / Low
- Impact: Catastrophic / Significant / Minor
- Root cause: [specific, not vague — "they ran out of budget in month 2 because X"]
- Mitigation: [concrete action that prevents or recovers from this]

[repeat for FM2, FM3]

### Logical Contradictions Found
[Where does the goal contradict its constraints? Be specific.]

### Most Dangerous Assumptions in the Plan
[What is the plan silently assuming that may be false?]

### Verdict
PROCEED / PROCEED WITH CAUTION / REDESIGN NEEDED
[Exact reasoning — 2-3 sentences max]
```

#### EXECUTOR Agent Prompt Template:
```
You are THE EXECUTOR — a pragmatist agent in a multi-agent goal council.
Apply the 80/20 rule ruthlessly: identify the 1-3 actions that drive 80% of results.
Acknowledge friction — do NOT pretend execution is easy. Call out the hardest part.
You translate strategy into what can ACTUALLY be done given real constraints.

GOAL: {north_star_goal}
DEADLINE: {deadline}
CONSTRAINTS: {constraints}
CURRENT STATE: {current_state}

Your job:
1. State THE HARDEST PART of executing this plan — the one thing people underestimate
2. Define the MINIMUM VIABLE ACTION — what is the smallest action that proves this is achievable?
3. Identify QUICK WINS — what can be done in Week 1-2 to build momentum and validate the approach?
4. Define the CRITICAL PATH — the single sequence where any delay breaks everything
5. Flag EXECUTION BLOCKERS — decisions/resources that must be resolved before Day 1
6. Propose a WEEK-BY-WEEK plan for the first 30 days (realistic, not optimistic)

Output format:
### The Hardest Part
[Be honest. What do plans like this consistently underestimate or get wrong in execution?]

### Minimum Viable Action
[Smallest proof-of-concept — what takes 1-3 days and validates the core assumption?]

### Quick Wins (Week 1-2)
- [action] → [specific expected outcome]

### Critical Path
[The must-not-delay sequence. If step N slips, everything after it slips.]

### Execution Blockers (Resolve Before Day 1)
- [blocker]: [who owns resolution] [deadline to resolve]

### 30-Day Action Plan
Week 1: [what gets done — specific, not vague]
Week 2: [what gets done]
Week 3: [what gets done]
Week 4: [what gets done — what does "Month 1 done" look like?]
```

---

### Phase 3: PLAN REVIEW (Red Team Gate)

After collecting all 3 agent outputs, YOU synthesize and run a **fourth check**:

Either:
- Spawn a **Verifier agent** with all 3 outputs as context, asking it to define measurable acceptance criteria and identify conflicts between Architect/Critic/Executor views
- OR do this synthesis yourself as orchestrator

#### VERIFIER Agent Prompt Template:
```
You are THE VERIFIER — a scientific reviewer in a multi-agent goal council.
You have received 3 strategic perspectives on the same goal. Your job is SYNTHESIS + VERIFICATION.

GOAL: {north_star_goal}
ACCEPTANCE CRITERIA DEFINED: {acceptance_criteria}

[ARCHITECT OUTPUT]: {architect_output}
[CRITIC OUTPUT]: {critic_output}
[EXECUTOR OUTPUT]: {executor_output}

Your job:
1. Find AGREEMENTS — where do all 3 agents align? These are high-confidence elements.
2. Find CONFLICTS — where do they disagree? These need human decision.
3. Refine ACCEPTANCE CRITERIA — make them SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
4. Issue a FINAL RECOMMENDATION: adjusted plan that incorporates the best of all 3

Output format:
## Council Agreements (High Confidence)
- [point of agreement]

## Council Conflicts (Needs Decision)
- [conflict]: Architect says X, Executor says Y → Recommended: Z because [reason]

## Refined Acceptance Criteria
- [ ] [Criterion 1 — measurable, time-bound]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Final Recommendation
[Synthesized plan — max 300 words]

## Go / No-Go Gate
GO / NO-GO
[Reason]
```

---

### Phase 4: EXECUTION ROADMAP

After Phase 3, present to the user using this mandatory 5-section format (learned from the Strategic Operations Director framework):

```markdown
# Strategic Goal Council — Results

## 🎯 I. Reality Check
[Brutally honest assessment of the goal — does the math work?
If the goal needed adjustment, state what changed and why.]
Goal Completeness: [N]/10

## 🔑 II. 80/20 Strategic Levers
[The 1-3 highest-impact actions that will drive 80% of results.
Everything else is explicitly labeled secondary.]

## ⚠️ III. Pre-Mortem: Top Failure Modes
[Top 2-3 reasons this plan will fail — with mitigations.
These are the things to watch first.]

## 🗺️ IV. Tactical Execution Map
[Synthesized milestone plan from Architect + Executor.
Sequenced critical path. Measurable milestones. 30-day Week-by-Week.]

## ✅ V. Acceptance Criteria (Locked)
[Refined SMART criteria from Verifier]
- [ ] [Criterion 1 — specific, measurable, time-bound]
- [ ] [Criterion 2]

## ❓ Decisions Needed From You
[Conflicts from Verifier — needs human input before proceeding]
Accountable owner: [name from RACI]

## 🚀 Start Here (Day 1 Action)
[Single minimum viable action to take in the next 48 hours]
```

**Do not begin execution until the user confirms the plan and resolves open decisions.**

---

### Phase 5: VERIFICATION GATE

After each milestone is reached, run a lightweight check:

```
For Milestone [N]:
- Success Signal defined: [X]
- Evidence collected: [Y]
- Signal met? YES / NO / PARTIAL
- Next milestone unlocked? YES / NO
```

If NO or PARTIAL — loop back to Phase 2 with updated context before proceeding.

---

### REDESIGN LOOP (NEW — for when Critic issues REDESIGN NEEDED verdict)

When the Critic issues a REDESIGN NEEDED verdict, do NOT abandon the session.
Follow this protocol:

```
Step 1: Surface the specific reason for REDESIGN to the user in plain language.
        "The Critic found that [specific problem]. This means the current plan
        cannot achieve the goal as stated. Here are the options:"

Step 2: Offer 3 redesign paths:
        A) Adjust the GOAL (lower target, longer timeline, narrower scope)
        B) Adjust the MODEL (different pricing, different channel, different ICP)
        C) Adjust the RESOURCES (add headcount, raise capital, acquire IP)

Step 3: User picks a path. Update the Goal Lock template with the change.

Step 4: Re-run Phase 0.5 Market Scout if the model or ICP changed.
        Re-run Phase 2 agents with the updated context.
        Do NOT re-run if only the timeline changed — update milestones only.

Step 5: Verifier checks: "Does the redesigned plan address the specific failure mode
        the Critic identified?" If yes → GO. If no → surface remaining gap.
```

> **Why this loop exists (learned from [your product] session):**
> The Critic issued REDESIGN NEEDED. The session almost ended there.
> But "redesign" is not a dead end — it is a redirect. The goal (USD 1M by 2027)
> survived. The model changed (commercial-first positioning, new channels,
> hardware bundle strategy). The redesign loop made this explicit rather than
> leaving the user without a path forward.

---

## Phase 5.5: DECISION LOGGING (NEW — learned from GBrain CEO Review)

After every completed council session, log the outcome to GBrain as a formal decision. This feeds future sessions and the CEO review.

```markdown
# Decision: [Goal Short Title]
date: [YYYY-MM-DD]
domain: [business domain]
accountable: [name from RACI]
consulted: [names]

## Goal
[North Star from Phase 1]

## Council Verdict
GO / NO-GO / REDESIGN

## Accepted Plan Summary
[Milestone breakdown — max 200 words]

## Key Risks Accepted
[Top 3 from Critic, with owner of each mitigation]

## Acceptance Criteria (locked)
- [ ] [criterion 1]
- [ ] [criterion 2]

## Review Date
[When to check if milestones are on track]
```

Log via:
```
gbrain put_page "decisions/[YYYY-MM-DD]-[short-title].md" [content above]
gbrain add_tag "decisions/[YYYY-MM-DD]-[short-title].md" "decision"
gbrain add_link "decisions/..." "people/[accountable-person]"
```

---

## Quick-Start Usage

### Trigger phrase:
> "Let's run a strategic council on [GOAL]"

### Orchestrator checklist:
- [ ] Goal crystallized (North Star, deadline, constraints, stakeholders, acceptance criteria)
- [ ] 3 parallel agents spawned (Architect, Critic, Executor)
- [ ] Verifier synthesis run
- [ ] Conflicts surfaced to user
- [ ] User confirmed Go/No-Go
- [ ] Week-1 actions locked

---

## Architecture Notes

### Why NOT real-time agent chat?
Hermes uses **hub-and-spoke**, not peer-to-peer. Agents don't talk directly to each other. Instead:
- The **orchestrator** (main Hermes instance) passes context between agents
- Each agent's output becomes the next agent's input (when sequential) or all run in parallel and the orchestrator synthesizes (when parallel)
- This is actually **more reliable** than real-time chat — no echo chambers, no one agent dominating

### Parallel vs Sequential
- **Parallel (default):** Architect + Critic + Executor run simultaneously → fastest, unbiased by each other
- **Sequential:** Architect → Critic reviews Architect → Executor adapts → more iterative but slower
- **Hybrid:** Parallel first round → Verifier synthesizes → targeted second round on conflict areas

### Context Passing
Always include in each agent's prompt:
1. The verbatim goal + constraints
2. Their specific role and output format
3. Explicit instruction to output structured markdown for synthesis

---

## Pitfalls

1. **Don't skip Phase 0 GBrain check** — agents debating without organizational memory produce plans that contradict prior decisions or ignore known constraints
2. **Don't skip Phase 1's 6 questions** — vague goals produce confident-sounding but useless plans; completeness < 7/10 means you're not ready
3. **Don't merge roles** — if you give one agent both Architect and Critic duties, the Critic will be weak (cognitive role conflict)
4. **Don't act on Architect output alone** — the Critic exists precisely because the Architect is optimistic
5. **Don't resolve Verifier conflicts yourself** — surface them to the user; they may have context agents don't
6. **Don't skip RACI** — "who owns this" must be answered before Phase 2 or no one is accountable for the outcome
7. **Don't forget to log the decision** — if it's not in GBrain, it didn't happen; the next council session will re-debate the same ground
8. **Token budget awareness** — 4-agent council with full context can be heavy; summarize past milestone outputs before reusing in new rounds
9. **Avoid echo chambers** — give each agent ONLY their role prompt, not the other agents' outputs, in the parallel phase
10. **Skill gaps and Bus Risks are non-negotiable inputs** — if a plan assumes a capability the team doesn't have, it will fail at execution

### Pitfalls Learned from Live Use (BusyCow + [your product] sessions, May 2026)

11. **Pricing model ≠ pricing number** — changing the price without changing the offering is not a real pivot. The Architect must ask: "What does the client believe they are buying at this price, and does the current offering actually deliver that?"

12. **Revenue model sanity check: who actually pays and when** — agents model against the total addressable pool (e.g. full AR book) rather than the actual trigger (e.g. only aged/stuck invoices). Always verify: is the revenue model based on what the client will activate, or the theoretical maximum?

13. **Entry product buyer must match core product buyer** — a low-friction entry product attracting a different buyer persona produces low-conversion pipelines. A blog engine attracts marketers; an AR health audit attracts CFOs. Match the buyer, not just the company.

14. **Check if the new model has the same structural bottleneck as the old one** — when redesigning to solve a scaling problem, agents propose a new model that looks different but embeds the same bottleneck. Always ask: "At 150 clients under this model, what does the team's day look like?"

15. **TAM is not SOM — and confusing them produces false confidence** — [your product]'s defense TAM was $2.5–4B on paper, but SOM was near zero due to structural access barriers. Always trace the path from TAM → SAM → SOM with specific filters. A large TAM with no access path is not an opportunity.

16. **Procurement cycle length is a hard mathematical constraint, not a risk** — for B2G goals, calculate: deadline minus average procurement cycle = last date a new deal can enter the process. Any deal started after that date is next year's revenue. State this explicitly. Agents tend to treat cycle length as a risk to mitigate rather than a constraint to calculate.

17. **Positioning must name what you're NOT competing with** — "on-premise disaster response" is only meaningful when contrasted with "cloud-based commercial mapping." Deliberate exclusion creates clarity for buyers, channels, and agents. Without it, agents will drift toward competing in the larger, more competitive segment by default.

18. **Hardware bundle strategy changes the channel motion entirely** — an OEM agreement with a drone manufacturer (Wingtra, Quantum Trinity) turns [your product] from "product that needs to be sold" to "product included in what customers already buy." This is a fundamentally different motion. Always evaluate hardware/product bundle as a channel option before designing a direct sales motion.

19. **"REDESIGN NEEDED" is not the end of the session** — it is a redirect. Follow the REDESIGN LOOP protocol. Surface the specific failure mode, offer 3 redesign paths, get user choice, update the Goal Lock, and re-run relevant agents. Do not leave the user without a path forward.

---

## References & Sources

- **Chief Agent Framework** (thaitype/chief): Milestone-based goal decomposition, Markdown-as-rules, human-AI-rules triad
- **MCP-RLM** (MuhammadIndar/MCP-RLM): Root Planner + Sub-Agent hierarchy, recursive logical models
- **Pew Pew Plaza Packs**: North Star goal, Deliverables + Acceptance Criteria as mandatory fields
- **NousResearch/hermes-agent-self-evolution**: DSPy + GEPA prompt evolution, execution trace analysis
- **MetaGPT**: Role-based agent assignment, SOP (Standard Operating Procedure) enforcement
- **CAMEL**: Role-playing agent conversations with structured debate
- **AutoGen**: Adversarial multi-agent patterns, human-in-the-loop confirmation gates
- **BusyCow $1M ARR session (May 2026)**: Live use — discovered pitfalls 11–14 around pricing model vs. offering alignment, revenue model over-estimation, buyer persona mismatch in entry products, and structural bottleneck recurrence in new model designs. Final strategy: ReminderCow ($79-249/mo flat SaaS by debtor count) + CollectionCow (contingency: 60-90d=8%, 90-120d=10%, 120-180d=13%, 180d+=15%). Entry funnel: AR Health Audit (free) → CFO Weekly Digest ($79/mo) → ReminderCow → CollectionCow. Channel: [Client] (MY, Gold Odoo partner, 25% recurring commission) + [Client] (HK, dual client+reseller). Decision logged to GBrain: busycow/busycow-1m-arr-strategy-2026.
- **[your product] $1M Revenue session (May 2026)**: Live use — discovered pitfalls 15–19 around TAM≠SOM confusion, procurement cycle as hard math constraint, deliberate positioning exclusion (on-premise only, NOT cloud), hardware bundle channel strategy, and REDESIGN LOOP protocol. Final strategy: Taiwan fire dept pilot (Nantou/Hualien county-first, 20 units = $161k → cascade to 5 counties), Blue Innovation Japan exclusivity (30% margin), Wingtra/Quantum Trinity OEM bundle (~$300k/yr passive), Sky-shine MY + Drone Entry TH (40-80 units combined). Critical non-negotiables: SkyDynamic agreement legal audit (before $100k cumulative), UNGM registration (this week, free). Decision logged to GBrain: geokernel/geokernel-1m-revenue-strategy-2026.
