# Git Setup Instructions for TheBeckoningMU

## Issues Resolved

✅ **Fixed `.gitignore`** - Now properly excludes:
- IDE files (.idea/, .vscode/)
- Python cache (__pycache__/)
- Evennia database files (*.db3)
- Reference repository (read-only)
- Local config files (*.local.json)
- Invalid files (nul)
- Backup files (*_v1.md)

✅ **Configured CRLF handling** - Set `core.autocrlf = true` globally

## Initial Git Setup

Run these commands in Git Bash or PowerShell:

```bash
# Navigate to project
cd "C:\Users\dasbl\PycharmProjects\TheBeckoningMU"

# Remove the invalid 'nul' file if it still exists
rm -f nul 2>/dev/null || del nul 2>nul

# Initialize git (if not already done)
git init

# Configure git for this project
git config core.autocrlf true
git config core.safecrlf warn

# Add all files (now properly filtered by .gitignore)
git add .

# Check status
git status
```

## Expected Git Status

You should see these files staged:
```
CLAUDE.md
GIT_SETUP.md
PROJECT_STATUS.md
README.md
THEMING_GUIDE.md
V5_IMPLEMENTATION_ROADMAP.md
V5_REFERENCE_DATABASE.md
beckonmu/
cursor-agent-wrapper.sh
poetry.toml
pyproject.toml
```

You should NOT see:
- `reference repo/` (excluded by .gitignore)
- `.idea/` (excluded by .gitignore)
- `.claude/` (excluded by .gitignore)
- `nul` (excluded and deleted)
- `V5_IMPLEMENTATION_ROADMAP_v1.md` (backup, excluded)
- `poetry.lock` (excluded by .gitignore)

## Initial Commit

```bash
# Create initial commit
git commit -m "Initial commit: Complete V5 MUSH planning phase

- V5_REFERENCE_DATABASE.md: Complete V5 mechanics reference (1093 lines)
- V5_IMPLEMENTATION_ROADMAP.md: 20-phase implementation plan (890+ lines)
- THEMING_GUIDE.md: ANSI art and gothic aesthetics
- PROJECT_STATUS.md: Planning phase summary
- CLAUDE.md: Evennia architecture + AI Quadrumvirate workflow
- .gitignore: Proper exclusions for Evennia/Python project

Planning phase complete. Ready to begin Phase 0 implementation."
```

## CRLF Warning Explanation

The warnings you saw:
```
warning: in the working copy of 'X', LF will be replaced by CRLF the next time Git touches it
```

This is **NORMAL** on Windows and **NOT an error**. It means:
- Git will store files with LF (Unix line endings) in the repository
- Git will convert to CRLF (Windows line endings) in your working directory
- This is the correct behavior set by `core.autocrlf = true`

## Recommended Next Steps

### 1. Create GitHub Repository (Optional)

```bash
# Create repo on GitHub, then:
git remote add origin https://github.com/YourUsername/TheBeckoningMU.git
git branch -M main
git push -u origin main
```

### 2. Set Up Git Branches for Development

```bash
# Create development branch
git checkout -b develop

# For each phase, create a feature branch
git checkout -b phase-0-setup

# When phase complete:
git checkout develop
git merge phase-0-setup
git branch -d phase-0-setup
```

### 3. Git Workflow Per Phase

For each implementation phase:

```bash
# Start new phase
git checkout develop
git checkout -b phase-X-name

# Work on deliverables
# ... create files, write code, run tests ...

# Commit frequently (one deliverable per commit)
git add beckonmu/commands/v5/dice.py
git commit -m "Phase 5: Implement basic dice rolling

- Created CmdRoll command
- Implemented pool rolling (d10, success on 6+)
- Added tests for basic rolls"

# When ALL phase deliverables complete and tests pass
git checkout develop
git merge phase-X-name
git tag -a v0.X -m "Phase X: [Phase Name] complete"
git branch -d phase-X-name
```

## .gitignore Categories Explained

### Evennia Server Files
- Database files (*.db3) - regenerated on `evennia migrate`
- Logs - runtime output, not source code

### Python
- Standard Python excludes (__pycache__, *.pyc)
- Virtual environment (.venv/)

### IDEs
- .idea/ - PyCharm/IntelliJ settings (user-specific)
- .vscode/ - VS Code settings (user-specific)

### Reference Repository
- `reference repo/` - Read-only analysis, don't track changes

### Local Configuration
- *.local.json - User-specific Claude Code settings
- secret_settings.py - Evennia secrets (passwords, API keys)

### Backup Files
- *_v1.md - Old versions (V5_IMPLEMENTATION_ROADMAP_v1.md)
- *.backup, *.bak - Temporary backups

## Troubleshooting

### "nul" file keeps reappearing
This was likely created by a buggy command. It's now in .gitignore and deleted.

### Still seeing CRLF warnings
This is normal on Windows. To suppress the warnings:
```bash
git config core.safecrlf false
```

### Want to see what's ignored
```bash
git status --ignored
```

### Accidentally committed something
```bash
# Before pushing:
git reset --soft HEAD~1  # Undo last commit, keep changes

# After pushing (dangerous):
git revert <commit-hash>  # Create new commit that undoes changes
```

## Git Best Practices for This Project

1. **Commit Early, Commit Often**: One deliverable per commit
2. **Write Descriptive Messages**: Reference phase and deliverable
3. **Test Before Committing**: All tests must pass
4. **Use Branches**: One branch per phase
5. **Tag Milestones**: Tag each completed phase
6. **Never Commit**:
   - Database files (*.db3)
   - Passwords/secrets (secret_settings.py)
   - IDE settings (.idea/)
   - Generated files (__pycache__/)

---

**Your git repository is now properly configured and ready for Phase 0 development.**
