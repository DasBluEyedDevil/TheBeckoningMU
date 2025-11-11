# TheBeckoningMU - Project Structure and Patterns

## Overview
TheBeckoningMU is an Evennia-based MUD implementing Vampire: The Masquerade 5th Edition (V5) mechanics. This document describes the project organization, key patterns, and conventions.

## Technology Stack
- **Language**: Python 3.13+
- **Framework**: Evennia (MUD/text-game framework built on Django)
- **Dependency Management**: Poetry
- **Game System**: V5 (Vampire: The Masquerade 5th Edition)

## Directory Structure

```
TheBeckoningMU/
├── beckonmu/                    # Main game package
│   ├── commands/                # Command implementations
│   │   ├── blood.py            # Blood Point & Hunger commands (+feed, +surge, etc.)
│   │   ├── dice.py             # V5 dice rolling commands
│   │   ├── jobs.py             # Jobs system commands (+job/create, +job/submit)
│   │   └── default_cmdsets.py  # Command set organization
│   │
│   ├── typeclasses/            # Game entity definitions
│   │   ├── characters.py       # Character typeclass (extends Evennia Character)
│   │   ├── objects.py          # Object typeclass with ObjectParent mixin
│   │   ├── rooms.py            # Room typeclass
│   │   └── exits.py            # Exit typeclass
│   │
│   ├── traits/                 # V5 trait system implementation
│   │   ├── blood.py            # Blood Point & Hunger mechanics
│   │   ├── disciplines.py      # Discipline powers
│   │   ├── attributes.py       # Physical/Social/Mental attributes
│   │   └── skills.py           # Skill ratings
│   │
│   ├── world/                  # Game content and data
│   │   ├── prototypes.py       # Object prototypes
│   │   ├── help_entries.py     # In-game help system
│   │   └── batch_cmds.py       # World-building batch commands
│   │
│   ├── server/                 # Server configuration
│   │   └── conf/
│   │       ├── settings.py     # Main settings (extends Evennia defaults)
│   │       └── secret_settings.py  # Secret keys (gitignored)
│   │
│   └── web/                    # Web interface (Django app)
│       ├── character/          # Character management
│       └── static_overrides/   # Custom CSS/JS
│
├── docs/                       # Project documentation
│   ├── planning/              # Roadmaps, TODOs, status
│   ├── reference/             # V5 mechanics, theming guides
│   └── guides/                # How-to guides
│
├── .skills/                   # AI Quadrumvirate skills
│   ├── README.md              # Quadrumvirate overview
│   ├── Claude-Orchestrator.md # Your orchestration role
│   ├── evennia-*.md           # Evennia framework skills
│   └── *.wrapper.sh           # CLI wrappers (gemini, cursor, copilot)
│
├── pyproject.toml             # Poetry dependencies
├── CLAUDE.md                  # Entry point for Claude Code
└── README.md                  # Project README
```

## Key Evennia Patterns Used

### 1. Typeclasses
**Pattern**: All game entities inherit from Evennia base typeclasses
```python
# beckonmu/typeclasses/characters.py
from evennia import DefaultCharacter

class Character(DefaultCharacter):
    """
    Character typeclass for VTM characters.
    All methods here apply to ALL characters in the game.
    """
    def at_object_creation(self):
        # Called once when character is first created
        self.db.blood_pool = 0
        self.db.hunger = 1
```

**Where Used**:
- `typeclasses/characters.py` - Character entities (PCs, NPCs)
- `typeclasses/objects.py` - Objects with ObjectParent mixin
- `typeclasses/rooms.py` - Game locations
- `typeclasses/exits.py` - Connections between rooms

**Key Hook Methods**:
- `at_object_creation()` - First-time initialization
- `at_pre_move()` - Before moving object
- `at_post_move()` - After moving object
- `at_object_receive()` - When receiving an object

### 2. ObjectParent Mixin
**Pattern**: Methods in `typeclasses/objects.py:ObjectParent` affect ALL game entities with a location

```python
# beckonmu/typeclasses/objects.py
class ObjectParent:
    """
    Mixin inherited by all entities with a location.
    Methods here apply to Characters, Objects, Exits, etc.
    """
    def return_appearance(self, looker, **kwargs):
        # Customizes how ALL objects appear when looked at
        pass
```

**Critical**: Changes here affect EVERYTHING in the game. Be cautious.

### 3. MuxCommand Pattern
**Pattern**: All commands follow MuxCommand syntax with switches

```python
# beckonmu/commands/blood.py
from evennia import Command

class CmdFeed(Command):
    """
    Feed from a target to restore Blood Points.

    Usage:
        +feed <target>
        +feed/messy <target>    # Messy Critical
    """
    key = "+feed"
    aliases = ["feed"]
    locks = "cmd:all()"

    def func(self):
        # Parse self.switches for /messy etc.
        # Parse self.args for target
        pass
```

**Syntax**: `command/switch arg = value`
- `/switch` - Command variants (e.g., `/messy`, `/list`)
- `arg` - Primary argument
- `= value` - Assignment syntax for some commands

**Where Used**: All files in `commands/` directory

### 4. Persistent Attributes
**Pattern**: Use `.db` for permanent data, `.ndb` for temporary data

```python
# Persistent (survives server reload)
character.db.blood_pool = 5
character.db.hunger = 2

# Temporary (cleared on reload)
character.ndb.in_combat = True
character.ndb.last_roll = [3, 4, 5, 8]
```

**Storage**:
- `.db.*` → Django database (persistent across server restarts)
- `.ndb.*` → In-memory (cleared on `evennia reload`)

**Naming Convention**: Use descriptive snake_case names

### 5. Command Sets
**Pattern**: Commands organized into logical sets

```python
# beckonmu/commands/default_cmdsets.py
from evennia import CmdSet
from commands.blood import CmdFeed, CmdSurge

class CharacterCmdSet(CmdSet):
    """
    Commands available to all characters.
    """
    def at_cmdset_creation(self):
        self.add(CmdFeed())
        self.add(CmdSurge())
```

**Organization**:
- `CharacterCmdSet` - Available to all characters
- `PlayerCmdSet` - OOC commands for players
- Custom sets for special states (combat, Haven, etc.)

## V5 Game System Organization

### Blood & Hunger System
**Location**: `traits/blood.py` + `commands/blood.py`
```
traits/blood.py        → Core mechanics (calculation, validation)
commands/blood.py      → Player commands (+feed, +surge, +mend)
```

### Dice System
**Location**: `commands/dice.py`
```
+roll <pool>           → Roll dice pool
+roll/hunger <pool>=<hunger>  → Roll with Hunger dice
+roll/wp <pool>        → Roll with Willpower reroll
```

### Traits System
**Location**: `traits/` directory
```
traits/attributes.py   → Strength, Dexterity, Stamina, etc.
traits/skills.py       → Athletics, Brawl, Firearms, etc.
traits/disciplines.py  → Vampire powers (Celerity, Potence, etc.)
```

### Jobs System
**Location**: `commands/jobs.py`
```
+job/create <title>    → Create job for character action
+job/submit <id>       → Submit job for ST approval
+job/list              → View your jobs
```

## Important Conventions

### 1. Avoid "beckonmu." Prefix
**Issue**: Django migrations fail with nested app names
```python
# ❌ WRONG
INSTALLED_APPS = ['beckonmu.web.character']

# ✅ CORRECT
INSTALLED_APPS = ['web.character']
```

### 2. Test Before Commit
```bash
evennia test           # Run all tests
evennia reload         # Hot reload code (faster than restart)
```

### 3. V5 Accuracy
All game mechanics must match V5 corebook rules exactly:
- Blood Surge: +2 dice, Hunger increases by 1
- Hunger caps at 5
- Disciplines cost XP: (level × 5) in-clan, (level × 7) out-of-clan

### 4. Command Naming
Use `+` prefix for IC commands: `+feed`, `+surge`, `+roll`
Use `/` for command switches: `+roll/hunger`, `+job/create`

## File Locations Quick Reference

| What | Where | Example |
|------|-------|---------|
| New command | `commands/*.py` | `commands/blood.py` |
| Game entity | `typeclasses/*.py` | `typeclasses/characters.py` |
| Game mechanics | `traits/*.py` | `traits/blood.py` |
| World content | `world/*.py` | `world/prototypes.py` |
| Server config | `server/conf/*.py` | `server/conf/settings.py` |
| Tests | Same dir as code | `commands/test_blood.py` |

## Integration with AI Quadrumvirate

When delegating tasks:
- **Gemini**: "Read project-structure.md and explain where Haven code should go"
- **Cursor**: "Following project-structure.md patterns, refactor XP system"
- **Copilot**: "Create new command in commands/ following project patterns"

## Additional Resources

- **Evennia Docs**: https://www.evennia.com/docs/latest/
- **V5 Mechanics**: `docs/reference/V5_MECHANICS.md`
- **Project Roadmap**: `docs/planning/ROADMAP.md`
- **Framework Skills**: `.skills/evennia-*.md`
