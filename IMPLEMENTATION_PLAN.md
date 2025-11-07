# Implementation Plan - Complete Roadmap Finalization
## TheBeckoningMU Gap Closure

**Created**: 2025-11-07
**Goal**: Implement all identified gaps to achieve 100% roadmap completion
**Current Status**: 95% → Target: 100%
**Approach**: AI Quadrumvirate Pattern (delegate to Cursor/Copilot)

---

## EXECUTION STRATEGY

Based on the comprehensive gap analysis, we will implement features in priority order:

1. **Priority 1**: CRITICAL - News System (reach 100% roadmap)
2. **Priority 2**: HIGH - Scene System, Active Effects, Auto Stains (optimize UX)
3. **Priority 3**: MEDIUM - Social Conflict, Status Bonuses, Rituals (add depth)
4. **Priority 4**: LOW - Polish items (BBS anon, +where, etc.)

**Implementation Principle**: NO DELETIONS - Only additions and completions.

---

## PHASE 1: CRITICAL - NEWS SYSTEM
**Timeline**: 2-3 hours
**Goal**: Reach 100% roadmap completion (20/20 phases)

### Implementation: Phase 1b - News System

**Files to Create**:

1. **`beckonmu/world/news_entries.py`** (similar to help_entries.py)
```python
# Load news files from beckonmu/world/news/ directory
# Register with Evennia FILE_NEWS_ENTRY_MODULES setting
```

2. **`beckonmu/world/news/` directory structure**:
```
beckonmu/world/news/
├── general/
│   ├── welcome.txt      # Welcome message for new players
│   ├── theme.txt        # Game theme and setting
│   └── getting_started.txt  # New player guide
├── updates/
│   ├── 2025_11.txt      # November 2025 updates
│   └── changelog.txt    # Code changes log
└── policy/
    ├── rules.txt        # Game rules
    ├── rp_policy.txt    # RP expectations
    └── chargen_policy.txt  # Character creation rules
```

3. **`beckonmu/commands/news.py`** - CmdNews command
```python
class CmdNews(Command):
    """
    Read game news and announcements

    Usage:
      news                    - List news categories
      news <category>         - List news in category
      news <category>/<topic> - Read specific news file

    Examples:
      news
      news general
      news general/welcome
      news updates
    """
```

4. **Initial Content Files**:
- `general/welcome.txt` - Welcome to TheBeckoningMU
- `general/theme.txt` - V5 Vampire game theme
- `updates/2025_11.txt` - Initial system announcement
- `policy/rules.txt` - Basic game rules

**Settings Configuration**:
```python
# In settings.py
FILE_NEWS_ENTRY_MODULES = ["world.news_entries"]
```

**Testing Checklist**:
- [ ] `news` lists categories
- [ ] `news general` lists general news topics
- [ ] `news general/welcome` displays welcome.txt
- [ ] News files support ANSI colors
- [ ] Help file for news command exists

**Delegate To**: Copilot CLI (backend/file operations)

---

## PHASE 2: HIGH-PRIORITY INTEGRATIONS
**Timeline**: 8-10 hours
**Goal**: Optimize player experience with existing systems

### 2A. Scene System with Effect Management (5-6 hours)

**Problem**: Scene-based discipline effects have no expiration mechanism.

**Files to Create/Modify**:

1. **`beckonmu/commands/v5/scene.py`** - Scene management commands
```python
class CmdScene(Command):
    """
    Manage roleplay scenes

    Usage:
      +scene/start <title>      - Start a new scene
      +scene/end                - End current scene
      +scene/join <scene>       - Join an existing scene
      +scene/leave              - Leave current scene
      +scene                    - Show current scene info
      +scene/list               - List active scenes

    Staff:
      +scene/end <scene>        - End any scene (ST)
    """
```

2. **`beckonmu/commands/v5/utils/scene_utils.py`**
```python
def start_scene(character, title, description=""):
    """Create new scene, return scene dict"""

def end_scene(scene_id):
    """End scene, expire all scene-duration effects"""
    # Get all characters in scene
    # Call remove_effect() for scene-duration effects
    # Notify all participants

def get_active_scenes():
    """Return list of active scenes"""

def get_character_scene(character):
    """Get scene character is currently in"""
```

3. **`beckonmu/scenes/models.py`** (optional - database-driven)
```python
class Scene(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(AccountDB)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    participants = models.ManyToManyField(ObjectDB)
```

**Integration Points**:
- Modify `discipline_effects.py` to check scene boundaries
- When scene ends, call `remove_effect()` for all scene-duration effects
- Notify players of expired effects

**Testing Checklist**:
- [ ] Can start/end scenes
- [ ] Scene-duration effects expire when scene ends
- [ ] Players notified of effect expirations
- [ ] Multiple concurrent scenes supported

**Delegate To**: Cursor CLI (UI/complex reasoning)

---

### 2B. Active Effects Display in +sheet (1-2 hours)

**Problem**: Players can't see active discipline effects on character sheet.

**Files to Modify**:

1. **`beckonmu/commands/v5/sheet.py`**
```python
# Add to CmdSheet.func():
from commands.v5.utils.discipline_effects import get_active_effects

# After displaying main stats, add:
active_effects = get_active_effects(self.caller)
if active_effects:
    self.caller.msg("\n" + display_active_effects_section(active_effects))
```

2. **`beckonmu/commands/v5/utils/display_utils.py`**
```python
def display_active_effects_section(effects):
    """
    Format active effects for character sheet display

    Returns formatted string with:
    - Effect name
    - Duration remaining
    - Source (discipline power)
    """
```

**Testing Checklist**:
- [ ] +sheet shows "Active Effects" section
- [ ] Displays effect name, duration, source
- [ ] Empty section hidden when no active effects
- [ ] ANSI formatting matches sheet style

**Delegate To**: Copilot CLI (simple integration)

---

### 2C. Automatic Messy Critical Stains (2 hours)

**Problem**: Messy Criticals don't automatically add Stains.

**Files to Modify**:

1. **`beckonmu/commands/v5/utils/discipline_utils.py`**
```python
# In activate_discipline_power() function:
from commands.v5.utils.humanity_utils import add_stain

# After dice roll:
if result.is_messy_critical:
    stain_result = add_stain(character, 1)
    # Notify character of Stain gain
    character.msg(f"|r[MESSY CRITICAL]|n You gain 1 Stain from your bestial action.")
```

2. **`beckonmu/world/v5_dice.py`**
```python
# Ensure DiceResult has is_messy_critical property
# (may already exist from Phase 5)
```

**Testing Checklist**:
- [ ] Discipline with Messy Critical adds Stain automatically
- [ ] Character notified of Stain gain
- [ ] +humanity shows increased Stains
- [ ] Works for all discipline activations

**Delegate To**: Copilot CLI (simple integration)

---

## PHASE 3: MEDIUM-PRIORITY ENHANCEMENTS
**Timeline**: 15-20 hours
**Goal**: Add gameplay depth and mechanical completeness

### 3A. Social Conflict System (4-5 hours)

**Files to Create**:

1. **`beckonmu/commands/v5/social_conflict.py`**
```python
class CmdPersuade(Command): pass
class CmdIntimidate(Command): pass
class CmdSeduce(Command): pass
class CmdDebate(Command): pass
```

2. **`beckonmu/commands/v5/utils/social_conflict_utils.py`**
```python
def social_contest(attacker, defender, attack_type, modifiers={}):
    """Resolve social conflict with contested rolls"""
```

**Delegate To**: Cursor CLI (complex mechanics)

---

### 3B. Status Mechanical Bonuses (2-3 hours)

**Files to Modify**:

1. **`beckonmu/status/utils.py`**
```python
def get_status_bonus(character, roll_type="social"):
    """
    Calculate dice bonus from Status

    Returns: +1 die per 2 Status dots for social rolls
    """
```

2. **`beckonmu/dice/dice_roller.py`**
```python
# In roll_dice() or roll_pool():
# Check for Status bonuses and apply to social rolls
```

**Delegate To**: Copilot CLI (simple integration)

---

### 3C. Combat Turn-Based Effect Ticking (3-4 hours)

**Files to Modify**:

1. **`beckonmu/commands/v5/combat.py`**
```python
# Add turn tracking to combat system
# At end of each turn, call:
from commands.v5.utils.discipline_effects import tick_effects
tick_effects(character, "turn")
```

**Delegate To**: Copilot CLI (integration)

---

### 3D. Full Blood Sorcery Ritual Library (6-8 hours)

**Files to Create**:

1. **`beckonmu/world/v5_rituals.py`**
```python
RITUALS = {
    1: [  # Level 1 rituals
        {
            "name": "Ward Against Ghouls",
            "level": 1,
            "cost": "One Rouse check",
            "ingredients": ["vampire blood", "salt"],
            "casting_time": "5 minutes",
            "duration": "One night",
            "effect": "..."
        },
        # ... more level 1 rituals
    ],
    # ... levels 2-5
}
```

2. **Modify `beckonmu/commands/v5/utils/discipline_utils.py`**
```python
def perform_ritual(character, ritual_name):
    """Enhanced ritual system with ingredients, casting time"""
```

**Delegate To**: Cursor CLI (content creation + mechanics)

---

## PHASE 4: LOW-PRIORITY POLISH
**Timeline**: 8-15 hours
**Goal**: Complete enhancements and polish

### 4A. BBS Anonymous Posting (1 hour)

**File to Modify**:
- `beckonmu/bbs/commands.py` line 187
- Add `/anon` switch to CmdBBPost

**Delegate To**: Copilot CLI

---

### 4B. +where Command (1-2 hours)

**File to Create**:
- `beckonmu/commands/where.py`

**Delegate To**: Copilot CLI

---

### 4C. Additional Polish Items
- Boons Display in +sheet (1-2 hours) - Copilot
- Amalgam Prerequisite Checking (2 hours) - Copilot
- +ooc / +ic Toggling (1 hour) - Copilot
- Clan ASCII Sigils (2 hours) - Cursor (visual)

---

## PHASE 5: OPTIONAL LONG-TERM
**Timeline**: 25-40 hours
**Goal**: Advanced features and automation

- Automated Nightly Blood Ticker (3-4 hours)
- +mail System (4-5 hours)
- Combat Initiative System (4-5 hours)
- Wiki Integration (8-10 hours)
- Weapon & Armor Systems (6-8 hours)
- Background Time-Based Refresh (3-4 hours)

**Deferred**: Can be implemented post-launch based on player feedback.

---

## DELEGATION STRATEGY

### Copilot CLI (Backend Developer)
- Phase 1: News System (2-3 hours)
- Phase 2B: Active Effects Display (1-2 hours)
- Phase 2C: Auto Messy Critical Stains (2 hours)
- Phase 3B: Status Mechanical Bonuses (2-3 hours)
- Phase 3C: Combat Turn Effect Ticking (3-4 hours)
- Phase 4: All polish items (8-15 hours)

**Total Copilot**: ~18-30 hours

### Cursor CLI (UI/Complex Developer)
- Phase 2A: Scene System (5-6 hours)
- Phase 3A: Social Conflict System (4-5 hours)
- Phase 3D: Blood Sorcery Ritual Library (6-8 hours)

**Total Cursor**: ~15-19 hours

---

## IMPLEMENTATION SEQUENCE

**Week 1: Critical Path (100% Roadmap)**
1. News System (Copilot) - 2-3 hours → **100% ROADMAP COMPLETE**

**Week 2: High-Impact UX**
2. Scene System (Cursor) - 5-6 hours
3. Active Effects Display (Copilot) - 1-2 hours
4. Auto Messy Critical Stains (Copilot) - 2 hours

**Week 3: Gameplay Depth**
5. Social Conflict System (Cursor) - 4-5 hours
6. Status Mechanical Bonuses (Copilot) - 2-3 hours
7. Combat Turn Effect Ticking (Copilot) - 3-4 hours

**Week 4: Content & Polish**
8. Blood Sorcery Ritual Library (Cursor) - 6-8 hours
9. BBS Anonymous Posting (Copilot) - 1 hour
10. +where Command (Copilot) - 1-2 hours
11. Other polish items (Both) - 5-10 hours

**Week 5+: Optional Features**
12. Long-term enhancements as time permits

---

## SUCCESS CRITERIA

### Phase 1 Complete (Critical):
- ✅ News system functional
- ✅ 20/20 phases complete (100%)
- ✅ Players can read news files
- ✅ Help file for news exists

### Phase 2 Complete (High-Priority):
- ✅ Scene system with effect expiration
- ✅ Active effects display on +sheet
- ✅ Messy Criticals auto-add Stains
- ✅ No regressions in existing features

### Phase 3 Complete (Medium-Priority):
- ✅ Social conflict mechanics functional
- ✅ Status provides dice bonuses
- ✅ Combat turns tick effects
- ✅ Blood Sorcery ritual library complete

### Phase 4 Complete (Polish):
- ✅ All minor features implemented
- ✅ All TODOs resolved
- ✅ Full feature parity with other V:tM MUSHes

---

## VERIFICATION PROTOCOL

After each implementation phase:

1. **Syntax Check**: All Python files compile
2. **Import Check**: No circular dependencies
3. **Server Reload**: `evennia reload` succeeds
4. **Feature Test**: New features work as specified
5. **Regression Test**: Existing features still work
6. **Documentation**: Help files updated

**Use**: `superpowers:verification-before-completion` skill

---

## RISK MITIGATION

### Potential Risks:
1. **Breaking Existing Features**: Mitigation - NO DELETIONS, only additions
2. **Integration Conflicts**: Mitigation - Test after each phase
3. **Time Overruns**: Mitigation - Prioritized implementation, can stop after any phase
4. **Scope Creep**: Mitigation - Stick to defined gaps only

### Rollback Plan:
- Git branch for each phase
- Can revert individual phases if issues arise
- All work on `claude/vtm-roadmap-gap-analysis-011CUtpsRApexmRp14pi8ZUB` branch

---

## NEXT STEPS

1. ✅ Gap Analysis Complete
2. ✅ Implementation Plan Created
3. **→ Begin Phase 1: News System Implementation** (delegate to Copilot)
4. Verify Phase 1 Complete
5. Begin Phase 2: High-Priority Integrations
6. Continue through phases in priority order

---

**Plan Created By**: Claude Code (AI Quadrumvirate Pattern)
**Ready to Execute**: YES
**First Delegation**: Copilot CLI - Phase 1b News System

---

END OF IMPLEMENTATION PLAN
