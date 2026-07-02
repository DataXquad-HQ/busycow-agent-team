# Memory and Sharing Model

This document explains how agents should use personal memory, shared memory, and canonical knowledge together.

## Core split

| Layer | Purpose | Sharing level |
|---|---|---|
| Personal Hindsight bank | role-scoped working memory | private to one agent or one human profile |
| Shared Hindsight bank | shared soft context for a team or domain | governed shared access |
| GBrain canonical | approved durable org truth | org-wide durable truth |
| GBrain evidence | durable source trail | org-wide, but evidence not policy |

## Personal vs shared memory

### Personal Hindsight banks
Use personal banks for:
- role-specific working patterns
- recent conversational continuity
- soft nuance that is helpful but not yet org policy
- memory that should not be treated as company-wide truth

Typical examples:
- `[org]-agent-iris`
- `[org]-agent-leo`
- `[org]-agent-maya`
- `[org]-human-founder`

### Shared Hindsight banks
Use shared banks for:
- reusable team context that multiple agents need
- operating patterns that are not yet canonical policy
- cross-functional memory that benefits from continuity
- domain-level shared memory such as pipeline, customer voice, or product feedback

Typical examples:
- `[org]-global`
- `[org]-internal`
- `[org]-pipeline`
- `[org]-customer-voice`
- `[org]-product-feedback`

## Governance rule

Shared memory is **not** a freeform scratchpad.
Only put information there when:
- the destination bank is clearly the right audience
- the item is traceable to a real source
- the item is durable enough to help later work
- the item is not actually current-state truth that belongs in a system of record

If the information looks like policy, source-of-truth definition, or long-term company knowledge, route it to review or GBrain instead.

## Recommended usage by role

| Role | Reads most from | Writes most to | Notes |
|---|---|---|---|
| Iris / Chief of Staff | structured state, GBrain, personal bank, shared banks | GBrain evidence/canonical, Iris personal bank, governed shared banks | Iris is the main governance layer for context promotion |
| Specialist agent | structured state, role bank, selected shared banks | role bank, structured systems, domain evidence | should not invent org policy in memory |
| Human founder profile | canonical knowledge, evidence, human bank | founder bank, approved decision artifacts | strategic judgments should eventually land in GBrain if durable |
| Installer / operator agent | playbooks, artifacts, workspace | workspace, review, setup docs | should document setup truth explicitly before activation |

## Agent sharing rules

1. **Private nuance stays private unless there is a reason to share it.**
2. **Cross-agent reusable context belongs in a shared bank only when source-traceable.**
3. **Anything that changes operating policy should be reviewed before canonical promotion.**
4. **Task ownership, deadlines, and stages do not belong in memory.**
5. **Evidence-backed durable facts should end up in GBrain, not only in Hindsight.**

## Promotion rules

Use this ladder:
1. chat or workspace note
2. personal memory or evidence capture
3. shared memory if cross-functional and still soft
4. review queue if it may become policy or durable org truth
5. GBrain canonical once approved

## Anti-patterns

Avoid these mistakes:
- using shared memory as a replacement for a CRM or task system
- storing approvals only in Hindsight
- treating repeated memory as confirmed policy
- putting temporary scratch analysis into durable shared memory
- skipping evidence capture and retaining only the summary
