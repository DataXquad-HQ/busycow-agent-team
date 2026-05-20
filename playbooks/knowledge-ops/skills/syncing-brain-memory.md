---
name: syncing-brain-memory
description: >
  Sync local GBrain vault and Hermes memory files to GitHub. Copies MEMORY.md and USER.md
  into the brain repo, then commits and pushes everything to GitHub. Use after gbrain dream
  completes, or when user says "push brain", "sync memory to github", "記憶備份".
triggers:
  - "push brain"
  - "sync memory to github"
  - "記憶備份"
  - "push to github"
  - "brain sync"
---

# Syncing Brain & Memory to GitHub

## Purpose
Copy Hermes memory files into the brain repo, then push the full vault to GitHub.

## Paths
- Brain vault: `~/brain`
- Memory files: `~/.hermes/memories/MEMORY.md` and `~/.hermes/memories/USER.md`
- Target dir in brain: `~/brain/hermes-memory/`
- GitHub remote: `origin main`

## Steps

### 1. Copy Memory Files
```bash
mkdir -p ~/brain/hermes-memory
cp ~/.hermes/memories/MEMORY.md ~/brain/hermes-memory/MEMORY.md
cp ~/.hermes/memories/USER.md ~/brain/hermes-memory/USER.md
```

### 2. Git Add + Commit + Push
```bash
cd ~/brain
git add -A
git diff --cached --stat
git commit -m "sync: nightly memory + brain $(date '+%Y-%m-%d')" --allow-empty
git push origin master 2>&1
```

### 3. Report Result
Return structured summary:
```
✅ Brain Sync 完成
- Files copied: MEMORY.md, USER.md
- Commit: [hash] — [stat summary]
- Push: origin/main ✓
```

If push fails (auth error, network), return ❌ with full error output and suggest checking git credentials.

## Pitfalls
- Git credentials stored in `~/.git-credentials` — if push fails check token expiry
- `--allow-empty` ensures commit always runs even if no changes (idempotent)
- Never skip the `cp` step — memory files live outside the brain repo and must be explicitly copied
- If `git push` fails with "non-fast-forward", run `git pull --rebase origin main` first then retry
