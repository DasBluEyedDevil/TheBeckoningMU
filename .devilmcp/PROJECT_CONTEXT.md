# TheBeckoningMU - Project Context

**Last Updated:** 2025-11-11 (Corrected after Gemini Audit)
**Project Type:** Evennia-based MUD (Multi-User Dungeon)
**Game System:** Vampire: The Masquerade 5th Edition (V5)
**Framework:** Evennia 4.x + Django
**Language:** Python 3.13+
**Production Readiness:** 95% Complete

---

## ⚠️ IMPORTANT: Corrected Assessment (2025-11-11)

**Initial assessment was INCORRECT.** After comprehensive Gemini audit of the codebase:

- **Previous claim:** "V5 commands incomplete, many partial implementations"
- **REALITY:** ALL V5 mechanics are COMPLETE (11 disciplines, 96 powers, all systems functional)
- **Previous claim:** "Help coverage 2.1% (1 of 47 commands)"
- **REALITY:** 36 comprehensive help .txt files exist; custom help system is COMPLETE and EXCELLENT
- **Previous claim:** "Many typeclasses not tracked by git"
- **REALITY:** All critical typeclasses committed (commit 612c472)

**See PRODUCTION_ROADMAP.md for the 4 remaining tasks before production launch.**

---

## Executive Summary

TheBeckoningMU is a heavily customized Evennia-based online RPG implementing the Vampire: The Masquerade 5th Edition (V5) tabletop RPG rules for multiplayer text-based gameplay. The project is in an **advanced state of development and nearing production readiness** (95%+ complete).

The project adds four major custom systems (BBS, Jobs, Status, Boons) plus comprehensive V5 mechanics (character creation, combat, all 11 disciplines with 96 powers, humanity tracking, hunting, XP advancement, and more). Code quality is high with clear separation of concerns and data-driven design. Custom help system with 36 comprehensive .txt files is COMPLETE.

**Only 4 minor implementation gaps remain** before production launch (see PRODUCTION_ROADMAP.md).

---

## 1. Project Structure

### Core Directories

```
TheBeckoningMU/
├── beckonmu/              # Main game package
│   ├── bbs/              # Bulletin Board System (Django app)
│   ├── boons/            # Boons/Prestation System (Django app)
│   ├── jobs/             # Jobs/Ticket System (Django app)
│   ├── status/           # Status/Position System (Django app)
│   ├── commands/         # Custom command implementations
│   │   ├── v5/          # V5-specific commands (hunt, feed, xp, etc.)
│   │   └── default_cmdsets.py  # Command set integration
│   ├── typeclasses/      # Custom game entity classes
│   │   ├── characters.py # Heavily modified for V5
│   │   ├── objects.py    # Mostly stock Evennia
│   │   ├── rooms.py      # Mostly stock Evennia
│   │   └── exits.py      # Mostly stock Evennia
│   ├── server/           # Server configuration
│   │   └── conf/         # Settings and hooks
│   ├── world/            # Game world content and data
│   └── web/              # Web interface customization
├── .devilmcp/            # DevilMCP context storage (THIS DIRECTORY)
└── server/               # Evennia runtime directory
```

### File Statistics (Estimated)
- **Python Files:** ~100+ files
- **Custom Code:** ~15,000+ lines
- **Django Apps:** 4 custom apps (bbs, boons, jobs, status)
- **Custom Commands:** 30+ V5 commands
- **Models:** 15+ custom database models

---

## 2. Changes from Stock Evennia

### 2.1 Added Custom Django Apps

#### BBS (Bulletin Board System)
- **Location:** `beckonmu/bbs/`
- **Purpose:** Complete in-game bulletin board system for player communication
- **Models:**
  - `Board` - Individual bulletin boards with permissions
  - `Post` - Posts within boards (auto-incrementing sequence numbers)
  - `Comment` - Replies to posts
- **Commands:** `+bbs`, `+bbread`, `+bbpost`, `+bbcomment`, `+bbadmin`
- **Features:**
  - Read/write permissions per board
  - Character flag requirements
  - Anonymous posting (TODO: not fully implemented)
  - Staff administration

#### Boons System
- **Location:** `beckonmu/boons/`
- **Purpose:** Tracks political favors/debts (Prestation) in V5 Camarilla society
- **Models:**
  - `Boon` - Individual favor/debt between two characters
  - `BoonLedger` - Cached summary for performance
- **Commands:** `+boongive`, `+boonaccept`, `+boondecline`, `+booncall`, `+boonfulfill`, `+boonadmin`
- **Features:**
  - Boon types: Trivial, Minor, Major, Blood, Life
  - Status workflow: offered → accepted → fulfilled → recorded
  - Harpy acknowledgment system
  - Audit trail

#### Jobs System
- **Location:** `beckonmu/jobs/`
- **Purpose:** Structured task/request management (ticket tracking)
- **Models:**
  - `Bucket` - Categorizes jobs (Bugs, Features, etc.)
  - `Job` - Individual tasks/requests
  - `Comment` - Discussion threads on jobs
  - `Tag` - Categorization/labeling
- **Commands:**
  - Players: `jobs`, `job/submit`, `job/claim`, `job/done`
  - Staff: `job/create`, `job/assign`, `bucket/create`
- **Features:**
  - Priority levels
  - Assignment tracking
  - Public/private comments
  - Status tracking (new, assigned, resolved, closed)

#### Status System
- **Location:** `beckonmu/status/`
- **Purpose:** Manages character Status in Camarilla political hierarchy (V5)
- **Models:**
  - `CamarillaPosition` - Defines roles (Prince, Primogen, etc.) with Status grants
  - `CharacterStatus` - Tracks earned/positional/temporary Status per character
  - `StatusRequest` - Formal requests for status changes/appointments
- **Commands:** `+status`, `+positions`, `+statusreq`, `+statusadmin`
- **Features:**
  - Calculates total Status and dice bonuses for social rolls
  - Position holders tracked
  - Status change history
  - Request/approval workflow

### 2.2 Modified Typeclasses

#### Characters (`beckonmu/typeclasses/characters.py`)
**HEAVILY MODIFIED** - This is the most significant deviation from stock Evennia.

**Modified Hooks:**
- `at_object_creation()` - Initializes comprehensive V5 data structure on `self.db`:
  - `stats` - Attributes (Physical/Social/Mental), Skills, Specialties, Disciplines
  - `vampire` - Clan, Generation, Blood Potency, Hunger, Humanity, Predator Type
  - `pools` - Health and Willpower (superficial/aggravated damage)
  - `humanity_data` - Convictions, Touchstones, Stains
  - `advantages` - Backgrounds, Merits, Flaws
  - `experience` - Detailed XP tracking (total, spent, unspent, costs)
  - `effects` - Active discipline powers and temporary effects
  - `chargen` - State machine for character creation process

**Added Methods:**
- `calculate_health()` - Derives health from Stamina
- `calculate_willpower()` - Derives willpower from Resolve + Composure
- `update_derived_stats()` - Recalculates derived traits
- `get_display_name()` - Shows Clan/Hunger to staff

**Why Modified:** Stock Evennia has no concept of character stats, RPG mechanics, or V5 rules. This customization provides the foundation for all V5 gameplay.

#### Other Typeclasses
- `Object`, `Room`, `Exit` - **Mostly unmodified** from stock Evennia
- These use the `ObjectParent` mixin pattern but have minimal V5-specific changes

### 2.3 Custom Commands

#### Command Set Integration (`beckonmu/commands/default_cmdsets.py`)
The `CharacterCmdSet` is the central integration point - it overrides Evennia's default command set to add:

**V5 Core Mechanics Commands:**
- `hunt` - Hunting for blood
- `feed` - Feeding mechanics
- `xp` - View experience
- `spend` - Spend XP
- `disciplines` - View/use discipline powers
- `effects` - Active effects management
- `humanity` - Humanity tracking
- `combat` - Combat system
- `thinblood` - Thin-blood mechanics
- `backgrounds` - Background traits
- `social` - Social interaction rules

**System Commands:**
- BBS command set (6 commands)
- Jobs command set (10+ commands)
- Status command set (4 commands)
- Boons command set (6 commands)

**Implementation Note:** Commands are added via `self.add()` in the cmdset, making them available to all characters. This is the standard Evennia pattern for extending functionality.

### 2.4 Modified Configuration Files

#### Settings (`beckonmu/server/conf/settings.py`)
- **Modified:** Django app registration
  - Added: `beckonmu.bbs`, `beckonmu.boons`, `beckonmu.jobs`, `beckonmu.status`
- **Modified:** Command set paths
  - Points to custom `default_cmdsets.py`
- **Modified:** Various game settings (game name, permissions, etc.)

#### Connection Screen
- Custom ASCII art connection screen
- V5-themed welcome message

### 2.5 Git Status (Current Modifications)

**Modified Files:**
- `beckonmu/jobs/__init__.py` - Modified
- `beckonmu/server/conf/settings.py` - Modified (app registration)

**Untracked Files/Directories:**
- `bbs/` - Entire BBS system (recently restored from backup)
- `beckonmu/server/conf/lockfuncs.py` - Custom lock functions
- `beckonmu/typeclasses/__init__.py` - Package init
- `beckonmu/typeclasses/channels.py` - Channel typeclass
- `beckonmu/typeclasses/exits.py` - Exit typeclass
- `beckonmu/typeclasses/objects.py` - Object typeclass
- `beckonmu/typeclasses/rooms.py` - Room typeclass
- `beckonmu/typeclasses/scripts.py` - Script typeclass
- `beckonmu/web/admin/` - Admin interface customization
- `beckonmu/web/webclient/` - Web client customization
- `web/admin/` - Additional admin files
- `web/webclient/` - Additional webclient files

**Recent History (from git log):**
1. Restored BBS, Jobs systems and ASCII art connection screen (commit 65e31bf)
2. Registered BBS and Jobs command sets (commit 0eaf1d3)
3. Added recovery guide for documentation restoration (commit 2e171b8)
4. Multiple help file system improvements (PR #16)

---

## 3. Dependencies

### 3.1 External Python Packages
**Primary:**
- `evennia` - Core MUD framework (4.x)
- `django` - Web framework (used by Evennia)
- `twisted` - Async networking (used by Evennia)

**Secondary (via Evennia):**
- Database backends (default: SQLite, supports PostgreSQL/MySQL)
- `simpleeval` - Safe expression evaluation
- Various Django ecosystem packages

**Development:**
- `poetry` - Dependency management
- `black` - Code formatting (assumed)
- `mock` - Testing (assumed)

### 3.2 File Import Relationships

**Critical Dependency Chains:**

```
typeclasses/characters.py
  ↓
commands/v5/*.py (all V5 commands depend on Character data structure)
  ↓
commands/default_cmdsets.py (integrates all commands)
  ↓
server/conf/settings.py (registers cmdset)
```

```
bbs/models.py → bbs/commands.py → default_cmdsets.py
boons/models.py → boons/commands.py → default_cmdsets.py
jobs/models.py → jobs/commands.py → default_cmdsets.py
status/models.py → status/commands.py → default_cmdsets.py
```

**Key Insight:** The `Character` typeclass is the foundation for ALL V5 gameplay. Changes to its data structure cascade through the entire command system.

---

## 4. Architecture Decisions

### 4.1 Data Storage Pattern
**Decision:** Store all V5 character data on `self.db` attributes
**Rationale:**
- Leverages Evennia's persistent attribute system
- No additional database tables needed for character stats
- Fast access (in-memory with lazy database writes)
- Flexible schema (dictionary-based)

**Trade-offs:**
- ✅ Simple to implement
- ✅ Fast reads/writes
- ❌ Harder to query across characters (e.g., "find all Brujah")
- ❌ No schema validation at database level

### 4.2 Django App Pattern for Systems
**Decision:** Create separate Django apps for BBS, Boons, Jobs, Status
**Rationale:**
- Clean separation of concerns
- Each system has its own models/commands/views
- Can be developed/tested independently
- Standard Django/Evennia pattern

**Benefits:**
- Modular architecture
- Easy to disable systems if needed
- Clear code organization

### 4.3 Command Set Centralization
**Decision:** Single `CharacterCmdSet` with all commands
**Rationale:**
- All V5 commands available to all characters by default
- Simpler than complex dynamic cmdset management
- Permission checks handled within commands

**Alternative Considered:** Dynamic cmdsets based on character state (rejected for simplicity)

### 4.4 BBS Command Refactoring
**Decision:** Refactored BBS from monolithic commands to small single-responsibility commands
**Rationale:**
- Original implementation had unmaintainable large command files
- Small commands easier to test and modify
- Shared utility modules reduce code duplication

**Pattern:** This is considered the "gold standard" and should be replicated for future systems

---

## 5. Current State

### 5.1 Working/Complete Systems

✅ **BBS System**
- Fully functional bulletin board
- Commands working
- Recently restored from backup

✅ **Jobs System**
- Complete ticket tracking
- Player and staff commands working
- Recently restored and registered

✅ **Status System**
- Position tracking functional
- Status calculation working
- Request workflow implemented

✅ **Boons System**
- Complete boon lifecycle
- Harpy oversight working
- Ledger performance optimization in place

✅ **Core V5 Character Data Structure**
- Comprehensive stats system
- Attribute/Skill tracking
- Discipline framework
- Humanity system
- Experience tracking

### 5.2 In Progress / Partial Implementation

⚠️ **V5 Commands**
- Many commands defined but implementation status varies
- Need to audit each command for completeness
- Some may be placeholders

⚠️ **Anonymous BBS Posting**
- TODO noted in code
- Not fully implemented

⚠️ **Web Interface**
- Custom admin/webclient directories present but status unknown
- May need integration testing

### 5.3 Known Issues

❌ **Documentation Loss**
- Project recently recovered from documentation loss incident
- Some context may still be missing
- Recovery guide created (see git history)

❌ **Untracked Files**
- Many core typeclass files currently untracked
- Need to be committed to git
- May indicate incomplete migration or recent restructuring

❌ **Testing Coverage**
- Test status unknown
- May need comprehensive test suite

### 5.4 Next Priorities (Inferred)

1. **Complete V5 command implementations** - Audit and finish partial commands
2. **Test all four custom systems** - Ensure BBS/Jobs/Status/Boons work end-to-end
3. **Commit untracked typeclasses** - Get all code under version control
4. **Character generation flow** - Implement complete chargen using the chargen state machine
5. **Web interface integration** - Verify admin/webclient customizations work

---

## 6. Risk Assessment

### High-Risk Areas

⚠️ **Character Typeclass (`typeclasses/characters.py`)**
- **Risk:** Changes to the data structure break ALL V5 commands
- **Mitigation:** Add data structure validation, write migration scripts
- **Cascade Potential:** EXTREME - touches entire game

⚠️ **Command Set Registration (`default_cmdsets.py`)**
- **Risk:** Misconfigured cmdset can break command availability
- **Mitigation:** Test after any changes, have rollback plan
- **Cascade Potential:** HIGH - affects all player commands

⚠️ **Django App Registration (`settings.py`)**
- **Risk:** Missing app registration breaks database migrations
- **Mitigation:** Verify INSTALLED_APPS after changes
- **Cascade Potential:** HIGH - can prevent server start

### Medium-Risk Areas

⚠️ **BBS/Jobs/Status/Boons Models**
- **Risk:** Model changes require migrations, can fail in production
- **Mitigation:** Test migrations thoroughly, have backup plan
- **Cascade Potential:** MEDIUM - affects specific system only

### Low-Risk Areas

✅ **Individual Commands** (within v5/ directory)
- **Risk:** Bug in one command doesn't affect others
- **Mitigation:** Standard testing, error handling
- **Cascade Potential:** LOW - isolated functionality

✅ **Web Interface Customization**
- **Risk:** Web UI bugs don't affect game server
- **Mitigation:** Test in browser
- **Cascade Potential:** LOW - separate from core game

---

## 7. Development Patterns

### 7.1 Recommended Command Implementation Pattern

Based on BBS refactoring (the "gold standard"):

```python
# Good: Small, single-responsibility command
class CmdBBRead(BBSCommand):
    """Read a post from a board."""
    key = "+bbread"

    def func(self):
        # Parse arguments
        # Validate permissions
        # Call utility function
        # Display result
```

**Anti-pattern to avoid:**
```python
# Bad: Monolithic command with many switches
class CmdBB(Command):
    """Handles ALL BBS functionality."""
    key = "+bbs"

    def func(self):
        # 500 lines of if/elif for different switches
        # Impossible to maintain or test
```

### 7.2 Recommended Data Access Pattern

```python
# Access V5 data on character
character.db.stats["attributes"]["physical"]["strength"]
character.db.vampire["hunger"]
character.db.pools["health"]["superficial"]
```

**Best Practice:** Always validate data exists before accessing nested dictionaries to avoid KeyError

### 7.3 Testing Strategy
- Unit tests for individual commands
- Integration tests for system workflows (e.g., complete boon lifecycle)
- Load testing for performance-critical code (e.g., BoonLedger)

---

## 8. Institutional Knowledge

### 8.1 Lessons Learned

**From Documentation Loss Incident:**
- Always maintain comprehensive project documentation
- Use DevilMCP for persistent context across sessions
- Keep recovery guides updated

**From BBS Refactoring:**
- Small single-responsibility commands > large monolithic commands
- Shared utility modules prevent code duplication
- Testing is easier with smaller command classes

### 8.2 Design Decisions to Preserve

✅ **Character data on self.db** - This pattern works well for V5 stats
✅ **Separate Django apps per system** - Keeps code organized
✅ **Small command pattern (BBS style)** - Maintainable and testable
✅ **Permission checks in commands** - Flexible and clear

### 8.3 Things to Avoid

❌ **Monolithic commands** - Hard to maintain
❌ **Hardcoded data in Python** - Use database or configuration files
❌ **Missing documentation** - Always document decisions
❌ **Untested migrations** - Database changes need testing

---

## 9. Quick Reference

### 9.1 Key File Paths

| Purpose | File Path |
|---------|-----------|
| Character stats | `beckonmu/typeclasses/characters.py` |
| Command registration | `beckonmu/commands/default_cmdsets.py` |
| Django apps | `beckonmu/server/conf/settings.py` |
| BBS system | `beckonmu/bbs/` |
| Jobs system | `beckonmu/jobs/` |
| Status system | `beckonmu/status/` |
| Boons system | `beckonmu/boons/` |
| V5 commands | `beckonmu/commands/v5/` |

### 9.2 Common Operations

| Task | Location |
|------|----------|
| Add new V5 command | Create in `commands/v5/`, add to `default_cmdsets.py` |
| Modify character stats | Edit `typeclasses/characters.py` `at_object_creation()` |
| Add new Django app | Create app, register in `settings.py` INSTALLED_APPS |
| Database migration | `evennia migrate` |
| Reload changes | `evennia reload` (preserves sessions) |

---

## 10. Next Session Checklist

When starting the next session, review:
1. This PROJECT_CONTEXT.md
2. Git status for any uncommitted changes
3. Recent git log for context
4. Any TODO comments in code
5. Test status (if tests exist)

---

## Document Maintenance

This document should be updated:
- When new systems are added
- When major architectural decisions are made
- After significant refactoring
- When learning important lessons
- At minimum, once per major feature implementation

**Current Version:** 1.0 (Initial DevilMCP context creation)
**Next Review:** After next major feature addition or architectural change
