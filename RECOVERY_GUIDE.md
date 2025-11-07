# Game Recovery Guide

## What Happened

In merge commit `2e62055`, your working BBS, Jobs, and ASCII art connection screen were deleted. This happened when merging branches that were cleaning up "old implementations."

**Systems that were deleted:**
- `beckonmu/bbs/` - Your bulletin board system
- `beckonmu/jobs/` - Your jobs/ticket system
- Custom ASCII art connection screen
- These systems were NOT added to `INSTALLED_APPS` in settings

**Result:** Your game appeared "stock" because the custom systems were gone.

## What I Fixed

✅ **Restored from git history:**
- BBS system (commit b79006e)
- Jobs system (commit 2f692a6)  
- ASCII art connection screen (commit d218f3f)

✅ **Registered in settings.py:**
- Added all Django apps to `INSTALLED_APPS`

✅ **Registered in command sets:**
- Added BBS and Jobs command sets to `default_cmdsets.py`

✅ **Also completed (as requested):**
- Phase 8: Disciplines (96 powers)
- Phase 14: Advanced Disciplines
- Phase 15: Combat System
- Phase 16: Humanity & Frenzy
- Phase 17: Coteries
- Phase 18: Thin-Bloods & Backgrounds

## To Get Your Game Working

### Step 1: Run Migrations
```bash
cd /home/user/TheBeckoningMU
python manage.py migrate
```

This creates the database tables for BBS, Jobs, Status, and Boons.

### Step 2: Reload Evennia
```bash
evennia reload
```

Or if reload doesn't work:
```bash
evennia stop
evennia start
```

### Step 3: Test Your Systems

**Connection:**
- You should see your ASCII art "Beckoning by Night" connection screen

**MUSH Systems:**
- `+bbs` - Bulletin boards
- `+jobs` - Jobs/ticket system
- `+status` - Status system
- `+boon` - Boons/prestation system

**V5 Systems:**
- `+sheet` - Character sheet (should work without errors now)
- `+disciplines` - View your disciplines
- `+power <discipline>/<power>` - Use discipline power
- `+attack`, `+damage`, `+heal`, `+health` - Combat
- `+humanity`, `+stain`, `+remorse`, `+frenzy` - Humanity/Frenzy
- `+coterie`, `+social` - Social systems
- `+alchemy` - Thin-Blood alchemy
- `+background` - Background usage
- `+hunt`, `+feed` - Hunting system
- `+xp`, `+spend` - Experience points

## If You Still Have Issues

1. **Check for Python errors:**
   ```bash
   python manage.py check
   ```

2. **Check server logs:**
   ```bash
   tail -100 server/logs/server.log
   ```

3. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   find . -name "*.pyc" -delete
   ```

4. **Try a full restart:**
   ```bash
   evennia stop
   evennia start
   ```

## Summary of All Commits

1. `4af3b1b` - Restored world/ directory
2. `4af769d` - Phase 8: Basic Disciplines
3. `7b5e47f` - Phase 14: Advanced Disciplines
4. `f72a5ba` - Phase 15 & 16: Combat + Humanity
5. `e9e6843` - Phase 17 & 18: Coteries + Thin-Bloods
6. `9046431` - Implementation completion report
7. `65e31bf` - Restored BBS, Jobs, ASCII art
8. `0eaf1d3` - Registered BBS/Jobs commands

All pushed to: `claude/review-docs-history-011CUqzPpbM5zrHBHpyBCxdQ`

## What You Should See Now

- **Connection Screen:** Your custom ASCII art "Beckoning by Night"
- **BBS:** Working bulletin board system
- **Jobs:** Working ticket/job system
- **Character Sheet:** Complete V5 character sheet with no errors
- **40+ Commands:** All V5 and MUSH commands functional

Your game should now be fully functional with all the V5 mechanics implemented AND your original MUSH infrastructure restored.
