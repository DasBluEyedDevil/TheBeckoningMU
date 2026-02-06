# Codebase Structure

**Analysis Date:** 2026-02-03

## Directory Layout

```
TheBeckoningMU/
├── beckonmu/                    # Main game package
│   ├── typeclasses/             # Game entity definitions (Objects, Characters, Rooms, Exits, Accounts)
│   ├── commands/                # Command implementations and CommandSet definitions
│   │   └── v5/                  # V5 Vampire mechanics commands
│   ├── traits/                  # Django app: trait/attribute database system
│   ├── status/                  # Django app: character status and Camarilla positions
│   ├── boons/                   # Django app: political favor (prestation) tracking
│   ├── jobs/                    # Django app: task/ticket management system
│   ├── bbs/                     # Django app: bulletin board system
│   ├── dice/                    # Dice roller implementation
│   ├── world/                   # Game data, help entries, prototypes, and configuration
│   ├── server/                  # Evennia server configuration
│   │   └── conf/                # settings.py, hooks, connections
│   │   └── .static/             # Generated web static files
│   ├── web/                     # Web interface
│   │   ├── website/             # Public-facing website
│   │   ├── webclient/           # Browser-based MUD client
│   │   ├── admin/               # Staff administrative interface
│   │   ├── api/                 # REST API endpoints
│   │   └── builder/             # Visual world builder (Django app)
│   └── README.md                # Game overview
├── pyproject.toml               # Poetry dependencies (Python 3.13+)
├── .devilmcp/                   # DevilMCP context tracking
├── .planning/                   # Planning documents
└── .venv/                       # Python virtual environment
```

## Directory Purposes

**beckonmu/typeclasses/**
- Purpose: Define core game entity classes
- Contains:
  - `objects.py` - ObjectParent mixin, Object class (items)
  - `characters.py` - Character class (player-controlled entities)
  - `rooms.py` - Room class (locations)
  - `exits.py` - Exit class (movement between rooms)
  - `accounts.py` - Account class (player accounts, OOC)
  - `scripts.py` - Script class (timed game logic)
  - `channels.py` - Channel class (communication)
- Key files: `objects.py` (ObjectParent mixin affects ALL game entities)
- Pattern: Each class inherits ObjectParent + Evennia default; implements hooks like at_object_creation()

**beckonmu/commands/**
- Purpose: Define all player-executable commands
- Contains: Base Command class, system commands, V5 specialized commands
- Key files:
  - `command.py` - Base Command class with styled_error(), styled_usage()
  - `default_cmdsets.py` - CharacterCmdSet (adds all character commands), AccountCmdSet, UnloggedinCmdSet, SessionCmdSet
  - `system_commands.py` - System-level commands (error messages)
- Structure: Commands added to cmdsets in at_cmdset_creation(); character gets CharacterCmdSet at login

**beckonmu/commands/v5/**
- Purpose: Implement V5 Vampire mechanics as player-facing commands
- Contains:
  - `sheet.py` - CmdSheet (display character sheet), CmdSheetShort (abbreviated)
  - `chargen.py` - CmdChargen (character generation process)
  - `combat.py` - CmdAttack, CmdDamage, CmdHeal, CmdHealth (combat system)
  - `disciplines.py` - CmdDisciplines, CmdActivatePower, CmdDisciplineInfo (vampire powers)
  - `hunt.py` - CmdHunt, CmdHuntingInfo (feeding system)
  - `blood.py` - Blood Surge, Hunger mechanics
  - `humanity.py` - CmdHumanity, CmdStain, CmdRemorse, CmdFrenzy (morality system)
  - `xp.py` - CmdXP, CmdSpend, CmdXPAward (experience points)
  - `backgrounds.py` - CmdBackground (character advantages)
  - `effects.py` - CmdEffects (active conditions/powers)
  - `social.py` - CmdCoterie, CmdSocial (group mechanics)
  - `thinblood.py` - CmdAlchemy, CmdDaylight (thin-blood powers)
  - `utils/` - Shared utilities (dice rolling, calculations, formatting)
  - `tests/` - Unit tests for V5 commands
- Key pattern: Commands read character.db.* for game state; use Trait models for mechanic definitions

**beckonmu/traits/**
- Purpose: Django app providing database-driven trait/attribute system
- Contains:
  - `models.py` - TraitCategory, Trait, TraitValue (game mechanics data)
  - `api.py` - REST endpoints for trait data
  - `utils.py` - Trait helper functions
  - `management/commands/` - load_traits.py, seed_traits.py (data loading)
  - `migrations/` - Database schema versions
- Key purpose: Centralizes game mechanics in database (attributes, skills, disciplines, advantages) so they can be modified without code changes

**beckonmu/status/**
- Purpose: Django app for Camarilla positions and character status tracking
- Contains:
  - `models.py` - CamarillaPosition, CharacterStatus (game state)
  - `commands.py` - CmdStatus, CmdPositions, CmdStatusRequest, CmdStatusAdmin (player commands)
  - `utils.py` - Status logic helpers
  - `migrations/` - Database schema

**beckonmu/boons/**
- Purpose: Django app for political favor (prestation) management
- Contains:
  - `models.py` - Boon (represents a favor owed between characters)
  - `commands.py` - CmdBoon, CmdBoonGive, CmdBoonAccept, CmdBoonDecline, CmdBoonCall, CmdBoonFulfill, CmdBoonAdmin
  - `utils.py` - Boon logic
  - `migrations/` - Database schema

**beckonmu/jobs/**
- Purpose: Django app for task/ticket management (staff-facing)
- Contains:
  - `models.py` - Bucket, Job, Tag, Comment (organization)
  - `commands.py` - CmdJobs and related commands
  - `utils.py` - Job operations
  - `cmdset.py` - JobsCmdSet for character command set
  - `migrations/` - Database schema
  - `tests.py` - Job system tests

**beckonmu/bbs/**
- Purpose: Django app for bulletin board system
- Contains:
  - `models.py` - BBSPost, BBSForum (discussion)
  - `commands.py` - CmdBBS commands
  - `utils.py` - Post/forum logic
  - `cmdset.py` - BBSCmdSet for character command set
  - `migrations/` - Database schema

**beckonmu/dice/**
- Purpose: Dice rolling system (V5 uses d10 pools)
- Contains:
  - `v5_dice.py` - Dice roller logic (handled by world/)
  - `cmdset.py` - DiceCmdSet for character command set
  - Integrates with command parser for MUX-style syntax

**beckonmu/world/**
- Purpose: Game data, configuration, and helpers
- Contains:
  - `v5_data.py` - Complete V5 mechanics reference data (attributes, skills, clans, disciplines, banes, compulsions)
  - `v5_dice.py` - Dice rolling functions
  - `ansi_theme.py` - ANSI color codes and text styling
  - `prototypes.py` - Evennia prototypes for object creation
  - `help_entries.py` - In-game help system entries
  - `news_entries.py` - In-game news system
  - `help/` - Help text files
  - `news/` - News content
  - `batch_cmds.ev` - Batch commands for initial setup
- Key principle: Data is defined here for reference; actual game logic queries Trait models (database)

**beckonmu/server/conf/**
- Purpose: Evennia server configuration and hooks
- Contains:
  - `settings.py` - Main configuration (SERVERNAME, INSTALLED_APPS, help modules, etc.)
  - `at_server_startstop.py` - Server startup/shutdown hooks (currently minimal)
  - `connection_screens.py` - Login screen text
  - `lockfuncs.py` - Custom lock verification functions
  - `cmdhandler.py` - Custom command parsing (if used)
  - `secret_settings.py` - Local/secret overrides (gitignored)
- Key: settings.py registers all custom Django apps (traits, status, boons, jobs, bbs, builder)

**beckonmu/web/website/**
- Purpose: Public-facing web pages (signup, character info, etc.)
- Contains: Django views, templates, URL routing
- Key: Provides HTTP interface to game information

**beckonmu/web/webclient/**
- Purpose: Browser-based MUD client
- Contains: WebSocket communication, terminal emulation, command input
- Key: Allows playing game in web browser without external client

**beckonmu/web/admin/**
- Purpose: Staff administrative interface
- Contains: Django admin customizations for game objects, accounts, etc.
- Key: Power user interface for managing game state

**beckonmu/web/api/**
- Purpose: REST API endpoints for game systems
- Contains:
  - `urls.py` - API route definitions
  - Endpoints for: traits, boons, jobs, status, bbs data
- Key: Machine-readable interface for external tools or web builder

**beckonmu/web/builder/**
- Purpose: Visual world building tool (zone editor)
- Contains:
  - `models.py` - BuildProject, RoomTemplate (map data storage)
  - `views.py` - HTTP endpoints for builder UI
  - `urls.py` - Builder URL routing
  - `exporter.py` - Converts map_data JSON to Evennia prototypes
  - `validators.py` - Input validation for builder
  - `admin.py` - Django admin customizations
  - `migrations/` - Database schema
- Key flow: Build in UI → BuildProject.map_data → export → spawn in sandbox room → promote to live
- Key: Enables non-coders to create game areas via visual editor

## Key File Locations

**Entry Points:**

- `beckonmu/server/conf/settings.py` - Evennia server main configuration; registers all apps
- `beckonmu/typeclasses/characters.py` - Character.at_object_creation() sets up new characters
- `beckonmu/commands/default_cmdsets.py` - CharacterCmdSet.at_cmdset_creation() attaches all commands to character
- `beckonmu/web/urls.py` - Root URL configuration for web interface
- `beckonmu/server/conf/connection_screens.py` - Login screen display

**Configuration:**

- `beckonmu/server/conf/settings.py` - INSTALLED_APPS, help modules, news modules
- `beckonmu/server/conf/at_server_startstop.py` - Server lifecycle hooks
- `beckonmu/world/v5_data.py` - Game mechanics reference (not used directly; data is in traits database)
- `beckonmu/world/ansi_theme.py` - Color codes and styling

**Core Logic:**

- `beckonmu/typeclasses/objects.py` - ObjectParent mixin; display methods used by all entities
- `beckonmu/typeclasses/characters.py` - Character initialization; character.db.* structure definition
- `beckonmu/commands/v5/` - All V5 mechanic implementations
- `beckonmu/traits/models.py` - TraitCategory, Trait database; queried by commands for mechanic rules

**Testing:**

- `beckonmu/commands/v5/tests/` - V5 command unit tests
- `beckonmu/traits/tests.py` - Trait system tests
- `beckonmu/jobs/tests.py` - Job system tests
- `beckonmu/bbs/tests.py` - BBS system tests

## Naming Conventions

**Files:**

- Commands: `{feature}.py` (e.g., `combat.py`, `disciplines.py`, `blood.py`)
- Models: `models.py` (Django convention)
- Utilities: `utils.py` (shared logic)
- Tests: `tests.py` or `test_{feature}.py`
- Management commands: `management/commands/{command_name}.py`

**Directories:**

- Game systems: lowercase plural (e.g., `traits/`, `status/`, `boons/`, `jobs/`)
- Version systems: `v5/` (Vampire v5 commands namespace)
- Django apps: lowercase (e.g., `web/`, `builder/`)

**Commands:**

- Classes: `Cmd{FeatureName}` (e.g., `CmdSheet`, `CmdAttack`, `CmdDisciplines`)
- Methods: snake_case (e.g., `func()`, `at_pre_cmd()`, `parse()`)

**Models:**

- Classes: PascalCase (e.g., `TraitCategory`, `Boon`, `CamarillaPosition`)
- Fields: snake_case with descriptive names (e.g., `min_value`, `boon_type`, `hierarchy_level`)

**Functions/Methods:**

- snake_case (e.g., `get_display_tags()`, `styled_error()`, `_create_attribute_dict()`)
- Private: leading underscore (e.g., `_create_attribute_dict()`)

## Where to Add New Code

**New V5 Mechanic Command:**
- Primary code: `beckonmu/commands/v5/{feature}.py`
- Create Cmd class inheriting from `beckonmu/commands/command.py:Command`
- Add to CharacterCmdSet in `beckonmu/commands/default_cmdsets.py` at_cmdset_creation()
- Tests: `beckonmu/commands/v5/tests/test_{feature}.py`

**New Game System (Status, Boons, Jobs pattern):**
- Create Django app in `beckonmu/{system_name}/`
- Minimum files:
  - `models.py` - Define game state models
  - `commands.py` - Define player-facing commands
  - `utils.py` - Shared logic
  - `apps.py` - Django app config
  - `migrations/` - Database schema
- Register in `beckonmu/server/conf/settings.py` INSTALLED_APPS
- Add cmdset in `beckonmu/commands/default_cmdsets.py` CharacterCmdSet.at_cmdset_creation()

**New Trait/Attribute:**
- Add to TraitCategory in `beckonmu/traits/models.py`
- Optionally define in `beckonmu/world/v5_data.py` for reference
- Load via `beckonmu/traits/management/commands/seed_traits.py`
- Query in commands: `from beckonmu.traits.models import Trait; trait = Trait.objects.get(name="...")`

**Web Endpoint (REST API):**
- Add to `beckonmu/web/api/views.py` or create new viewset
- Register in `beckonmu/web/api/urls.py`
- Test via `/api/` endpoint

**Web Page (Django View):**
- Create view in appropriate web subpackage (`website/`, `admin/`, etc.)
- Create template in `beckonmu/web/templates/`
- Register URL in subdirectory `urls.py`
- Include in `beckonmu/web/urls.py`

**Character Data (on character.db):**
- Initialize in `beckonmu/typeclasses/characters.py:Character.at_object_creation()`
- Access in commands: `self.caller.db.{attribute}`
- Access in templates: `{{ character.db.attribute }}`
- Structure: Use nested dicts/lists for organization (e.g., character.db.stats["attributes"]["physical"]["strength"])

**Utilities/Helpers:**
- Shared logic: `beckonmu/{system}/utils.py`
- Shared calculation logic: `beckonmu/commands/v5/utils/` (create subdirectory if needed)
- Global helpers: `beckonmu/world/{module}.py`

## Special Directories

**beckonmu/server/.static/**
- Purpose: Collected static files for web interface (CSS, JS, images)
- Generated: Yes (django collectstatic)
- Committed: No (gitignored in most Django projects)
- What goes here: Compiled/collected web assets only; source files go in app-specific static/ directories

**beckonmu/web/templates/**
- Purpose: HTML templates for web views
- Generated: No
- Committed: Yes
- What goes here: Django templates with .html extension; referenced by views.py in render() calls

**beckonmu/world/help/ and beckonmu/world/news/**
- Purpose: Help text and news content files
- Generated: No
- Committed: Yes
- What goes here: Text files loaded by Evennia's help and news systems

**beckonmu/commands/v5/tests/**
- Purpose: Unit tests for V5 commands
- Generated: No
- Committed: Yes
- What goes here: test_{feature}.py files with test classes inheriting from TestCase

**beckonmu/jobs/server/logs/**
- Purpose: Job system background task logs (if jobs are async)
- Generated: Yes (during job processing)
- Committed: No
- What goes here: Log files from background job execution
