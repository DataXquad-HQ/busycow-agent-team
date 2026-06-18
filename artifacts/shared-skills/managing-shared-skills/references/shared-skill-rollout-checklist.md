# Shared Skill Rollout Checklist

Use this checklist every time Iris promotes a skill into the shared layer.

## Before rollout
- [ ] Confirm the skill is truly shared, not just reusable in theory
- [ ] Remove hardcoded profile-specific assumptions from the canonical source
- [ ] Decide the sync policy: overwrite / manual review / forked
- [ ] Decide which profiles receive this rollout now

## Rollout
- [ ] Update the canonical source first
- [ ] Copy the skill into target profile `skills/` directories
- [ ] Verify each profile copy contains `SKILL.md`
- [ ] If overwriting an existing profile copy, back it up first if needed

## After rollout
- [ ] Record which profiles were updated
- [ ] Note whether any profile is now a deliberate fork
- [ ] If the skill should later be packaged, add it to `shared-skills/` in the package repo
