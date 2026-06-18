# TEAM MANIFEST
# ============================================================
# Fill this out completely before activating team-gstack or team-gbrain.
# Save this file as TEAM_MANIFEST.md in your project root.
# This file is the single source of truth for your team's AI orchestration.
# Version this file in git — changes must be logged as decisions.
# ============================================================

version: "1.0"
last_updated: YYYY-MM-DD
team_name: "[Your Team / Organization Name]"
project_name: "[Current Project or Product Name]"
project_mission: >
  [One sentence: what does this team exist to accomplish?
  e.g., "Deploy AI-powered workflow automation for SMEs in Southeast Asia."]

current_sprint_goal: >
  [What is the team focused on right now?
  e.g., "Launch v1.0 of the client onboarding flow by end of month."]

current_blockers:
  - "[Describe any active blockers. e.g., 'Waiting on API credentials from vendor X']"
  - "[Add more as needed]"

---

## TEAM MEMBERS

# Copy this block for each team member.
# RACI key: R=Responsible, A=Accountable, C=Consulted, I=Informed
# A person can have different RACI roles in different domains.

- name: "[Full Name]"
  role: "[Job Title / Function — e.g., CEO, Lead Engineer, Sales Lead]"
  seniority: "[e.g., Founder, Senior, Mid, Junior]"
  domains:
    - name: "[Domain Name — e.g., Product Strategy]"
      raci: "A"  # This person is Accountable for this domain
    - name: "[Domain Name — e.g., Backend Architecture]"
      raci: "C"  # This person is Consulted on this domain
  skills:
    - "[e.g., Python, React, Sales, Marketing, DevOps]"
  communication:
    preferred_channel: "[WhatsApp / Slack / Email / Telegram / Lark]"
    style: "[e.g., Concise bullet points, needs technical detail first, prefers async]"
    timezone: "[e.g., UTC+8 (HKT), UTC-5 (EST)]"
    availability: "[e.g., Mon-Fri 9am-6pm HKT, responds within 2h]"
  notes: "[Any relevant context — e.g., currently on leave until X, leads client relationships in Region Y]"

- name: "[Full Name]"
  role: "[Job Title / Function]"
  seniority: "[e.g., Senior, Mid, Junior]"
  domains:
    - name: "[Domain Name]"
      raci: "R"
    - name: "[Domain Name]"
      raci: "I"
  skills:
    - "[Skill 1]"
    - "[Skill 2]"
  communication:
    preferred_channel: "[Channel]"
    style: "[Style notes]"
    timezone: "[Timezone]"
    availability: "[Hours]"
  notes: "[Notes]"

# Add more team members as needed...

---

## AI AGENT ROLES

# Define what the AI agent is allowed to do and what requires human approval.

- agent_name: "[Agent Name — e.g., Hermes, BusyCow AI]"
  role: "Orchestrator / Team Liaison"
  authorities:
    can_do:
      - "[e.g., Update CRM records in Notion]"
      - "[e.g., Draft emails and messages for review]"
      - "[e.g., Summarize meeting notes and log decisions]"
      - "[e.g., Run code reviews and surface issues]"
      - "[e.g., Route information to team members via preferred channels]"
      - "[e.g., Track Bus Factor risks and Skill Gaps]"
    cannot_do_without_human_approval:
      - "[e.g., Send external emails]"
      - "[e.g., Approve budget spend]"
      - "[e.g., Make hiring or firing decisions]"
      - "[e.g., Publish to production]"
      - "[e.g., Delete data]"
  escalation_path: "[Who does the agent escalate to when unsure? e.g., always escalate to [Name] for anything touching clients]"

---

## DOMAINS & OWNERSHIP

# Each domain should have exactly ONE Accountable person.
# Multiple people can be Responsible or Consulted.

- domain: "[Domain Name — e.g., Product Strategy]"
  description: "[What decisions and work fall under this domain?]"
  accountable: "[Person Name]"
  responsible: ["[Person Name]", "[Person Name]"]
  consulted: ["[Person Name]"]
  informed: ["[Person Name]", "[Person Name]"]
  key_components:
    - "[e.g., Product roadmap, feature prioritization, user research]"

- domain: "[Domain Name — e.g., Engineering / Backend]"
  description: "[Description]"
  accountable: "[Person Name]"
  responsible: ["[Person Name]"]
  consulted: ["[Person Name]"]
  informed: ["[Person Name]"]
  key_components:
    - "[e.g., API design, database schema, deployment pipeline]"

- domain: "[Domain Name — e.g., Sales & Client Relations]"
  description: "[Description]"
  accountable: "[Person Name]"
  responsible: ["[Person Name]"]
  consulted: ["[Person Name]"]
  informed: ["[Person Name]"]
  key_components:
    - "[e.g., Lead pipeline, client onboarding, account management]"

# Add more domains as needed...

---

## COMMUNICATION CHANNELS

# Where does the team communicate? This tells the agent where to route information.

platforms:
  - name: "[e.g., Slack / Telegram / Lark / WhatsApp]"
    purpose: "[e.g., Day-to-day async communication]"
    channels:
      - name: "[#channel-name or group name]"
        purpose: "[e.g., Engineering decisions, Client updates, General]"
        audience: "[e.g., All engineers, Founding team only, All hands]"

  - name: "[e.g., Notion / Confluence]"
    purpose: "[e.g., Documentation, CRM, Decision logs]"

  - name: "[e.g., GitHub / Linear]"
    purpose: "[e.g., Code, issue tracking, sprint management]"

escalation_contacts:
  - situation: "[e.g., Production outage]"
    contact: "[Person Name]"
    channel: "[e.g., WhatsApp direct message]"
  - situation: "[e.g., Client complaint]"
    contact: "[Person Name]"
    channel: "[e.g., Telegram DM]"

---

## KNOWN BUS RISKS (OPTIONAL — fill in if already known)

# List any components where only one person holds critical knowledge or access.

- component: "[e.g., Production deployment]"
  sole_owner: "[Person Name]"
  severity: "critical|high|medium"
  mitigation_plan: "[e.g., Document runbook by [date], pair with [Person]]"

---

## KNOWN SKILL GAPS (OPTIONAL — fill in if already known)

- domain: "[e.g., DevOps]"
  missing_skill: "[e.g., Kubernetes cluster management]"
  severity: "critical|high|medium|low"
  mitigation: "[e.g., Use managed service, train [Person], hire contractor]"

---

## ACTIVATION CHECKLIST

Before using team-gstack or team-gbrain, confirm:

- [ ] All team members listed with correct RACI assignments
- [ ] All domains have exactly one Accountable person
- [ ] AI agent authorities clearly defined (can do / cannot do)
- [ ] Communication channels and preferences filled in
- [ ] Escalation contacts defined
- [ ] File saved as TEAM_MANIFEST.md in project root
- [ ] File committed to git (version controlled)
- [ ] If using GBrain: run ingestion to load manifest into knowledge base

---

## USAGE NOTES

- **Update this file** whenever a team member joins, leaves, or changes role
- **Every update** should be logged as a decision in GBrain: `decisions/YYYY-MM-DD-team-manifest-update.md`
- **RACI conflicts** (two people both listed as Accountable for same domain) must be resolved immediately
- **The agent uses this file** to determine who to consult, who to inform, and who has authority to approve actions
