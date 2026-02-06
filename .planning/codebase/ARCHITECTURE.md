# Architecture

**Analysis Date:** 2026-02-03

## Pattern Overview

**Overall:** Layered Evennia-based MUD (Multi-User Dungeon) with Django ORM backend and web interface

**Key Characteristics:**
- Evennia typeclass system for game entities (Objects, Characters, Rooms, Exits, Accounts, Scripts)
- Django-based persistence layer with extended models for game systems
- Command-driven interaction pattern (MUX-style syntax)
- Mixin-based polymorphism via ObjectParent for entity customization
- Vampire: The Masquerade v5 mechanics as primary game ruleset
- Modular command system via CommandSets
- Web builder interface for content creation alongside text-based commands

## Layers

**Typeclass Layer (Game Entities):**
- Purpose: Define and manage all game objects with location and persistence
- Location: `beckonmu/typeclasses/`
- Contains: Object, Character, Room, Exit, Account, Channel, Script classes
- Depends on: Evennia DefaultObject/DefaultCharacter base classes, ObjectParent mixin
- Used by: Commands, Scripts, Server hooks, Web Builder

**ObjectParent Mixin Layer:**
- Purpose: Provide shared behavior for ALL entities with a location in the game world
- Location: `beckonmu/typeclasses/objects.py` (ObjectParent class)
- Contains: display_tags, display_name formatting, client width detection
- Depends on: None (pure mixin)
- Used by: All game entities (Objects, Characters, Rooms, Exits inherit from this indirectly)

**Character Data Layer:**
- Purpose: Store and manage V5 Vampire mechanics data on character database attributes
- Location: Character initialization in `beckonmu/typeclasses/characters.py`
- Contains: Attributes, Skills, Disciplines, Clans, Health/Willpower pools, Humanity, XP, Effects
- Depends on: Character.db.* persistent attribute storage
- Used by: V5 command modules, character sheet, combat system

**Command Layer:**
- Purpose: Parse and execute player actions with consistent error handling
- Location: `beckonmu/commands/`
- Contains: Base Command class, V5 specialized commands (sheet, chargen, combat, disciplines, etc.)
- Depends on: Evennia Command base, character data layer
- Used by: Command Sets, character objects at runtime

**Game System Modules:**
- Purpose: Implement specific game mechanics independent of command execution
- Location: Separate Django apps per system
- Contains:
  - **Traits System** (`beckonmu/traits/`): Database-driven trait/attribute definitions
  - **Status System** (`beckonmu/status/`): Camarilla positions and character status tracking
  - **Boons System** (`beckonmu/boons/`): Political favor (prestation) management
  - **Jobs System** (`beckonmu/jobs/`): Task/ticket management with buckets and tags
  - **BBS System** (`beckonmu/bbs/`): Bulletin board posts and forums
  - **Dice System** (`beckonmu/dice/`): Roller implementation
- Depends on: Django ORM, Evennia object references
- Used by: Commands, Web views, Admin interface

**Web Interface Layer:**
- Purpose: Provide HTTP/REST access to game systems
- Location: `beckonmu/web/`
- Contains:
  - **Website** (`web/website/`): Public-facing pages
  - **Webclient** (`web/webclient/`): Browser-based MUD client
  - **Admin** (`web/admin/`): Staff administrative interface
  - **API** (`web/api/`): REST endpoints for traits, boons, jobs, etc.
  - **Builder** (`web/builder/`): Visual world builder with map editor
- Depends on: Django Views/Serializers, game system models
- Used by: Web browsers, external tools

**Data Configuration Layer:**
- Purpose: Define game mechanics constants and initial data
- Location: `beckonmu/world/`
- Contains: `v5_data.py` (attributes, skills, clans, disciplines), `prototypes.py` (object templates), `ansi_theme.py` (color codes)
- Depends on: None (pure data)
- Used by: Trait initialization, command logic, display formatting

**Server Configuration Layer:**
- Purpose: Configure Evennia server behavior and hooks
- Location: `beckonmu/server/conf/`
- Contains: `settings.py` (game config), `at_server_startstop.py` (lifecycle hooks), `connection_screens.py`, `lockfuncs.py`
- Depends on: Evennia defaults
- Used by: Evennia server startup

## Data Flow

**Player Login Flow:**

1. Session connects to MUD port (4000) or web client (4001)
2. Connection screen shown (`connection_screens.py`)
3. Account created or logged in (handled by Evennia default commands)
4. Account puppets Character (selected from account's character list)
5. Character's ObjectParent mixin + CharacterCmdSet applied
6. Character appears in game world

**Command Execution Flow:**

1. Player enters command (MUX syntax: `command[/switch] arg1, arg2 = val1, val2`)
2. Evennia command handler parses command string
3. Matching command found in active CommandSet (CharacterCmdSet)
4. Command.parse() processes arguments
5. Command.func() executes logic
   - Reads/modifies character.db.* attributes
   - Queries game system models (Status, Boons, Traits, etc.)
   - Sends styled output to character
6. Command.at_post_cmd() hook called
7. Result sent to character's session

**Character Sheet Data Access Flow:**

1. CmdSheet invoked
2. Reads Character.db.stats, Character.db.vampire, Character.db.pools, Character.db.advantages
3. Formats display with ObjectParent.get_display_tags() and color codes
4. Uses TraitCategory/Trait models to fetch trait definitions and XP costs
5. Renders with ANSI formatting (colors from `ansi_theme.py`)

**Web Builder Export Flow:**

1. User creates/edits BuildProject in web builder UI
2. BuildProject.map_data contains frontend state (rooms, exits, objects, coordinates)
3. exporter.py converts map_data to Evennia prototypes
4. Prototypes spawned in sandbox room via command
5. Builder can promote sandbox to live game world

**State Management:**

- **Persistent (Database)**: Character stats, advantages, status, boons, XP, health - stored in Character.db.* attributes and game system models
- **Non-Persistent (Memory)**: Temporary flags, combat state, active effects - stored in Character.ndb.* attributes
- **Configuration**: Trait definitions, position definitions, clan mechanics - loaded from database at startup from `v5_data.py`

## Key Abstractions

**Character Abstraction:**
- Purpose: Represent a player-controlled vampire entity with full V5 mechanics
- Examples: `beckonmu/typeclasses/characters.py`, Character class
- Pattern: Inherits ObjectParent + DefaultCharacter; data stored as nested dicts in character.db attributes
- Data structure: character.db.stats, character.db.vampire, character.db.pools, character.db.humanity_data, character.db.advantages, character.db.experience, character.db.effects

**Command Abstraction:**
- Purpose: Parse and execute a single player action with consistent error handling
- Examples: `beckonmu/commands/v5/sheet.py`, `beckonmu/commands/v5/combat.py`, `beckonmu/commands/v5/disciplines.py`
- Pattern: Inherit Command base class; implement parse() for argument processing, func() for logic
- Execution hook: func() accesses self.caller (Character object), accesses character.db.* data, sends output via self.caller.msg()

**CommandSet Abstraction:**
- Purpose: Dynamically attach/detach groups of related commands to game objects
- Examples: `beckonmu/commands/default_cmdsets.py` (CharacterCmdSet, AccountCmdSet)
- Pattern: Inherit CmdSet; at_cmdset_creation() adds command instances
- Applied to: Characters get CharacterCmdSet + system-specific cmdsets (BloodCmdSet, DiceCmdSet, etc.)

**Game System Module Abstraction:**
- Purpose: Encapsulate a specific game mechanic with models, commands, and utilities
- Examples: `beckonmu/status/`, `beckonmu/boons/`, `beckonmu/jobs/`
- Pattern: Django app with models.py (database), commands.py (player-facing), utils.py (logic), api.py (REST), migrations/
- Separation: Models define state; commands define interaction; utilities provide shared logic

**Web Builder Model Abstraction:**
- Purpose: Represent a game area/zone being built in visual editor
- Examples: BuildProject, RoomTemplate (in `beckonmu/web/builder/models.py`)
- Pattern: Store entire map state as JSONField; exporter converts to Evennia prototypes
- Lifecycle: Create in builder UI → save to BuildProject.map_data → export via exporter.py → spawn in sandbox

## Entry Points

**Server Start:**
- Location: `beckonmu/server/conf/settings.py`
- Triggers: evennia start
- Responsibilities:
  - Load INSTALLED_APPS (game system modules)
  - Load FILE_HELP_ENTRY_MODULES and FILE_NEWS_ENTRY_MODULES
  - Run migrations for database schema
  - Apply settings overrides

**Server Lifecycle Hooks:**
- Location: `beckonmu/server/conf/at_server_startstop.py`
- Triggers: at_server_start(), at_server_stop()
- Responsibilities: Custom initialization (currently empty but available for data loading)

**Character Creation:**
- Location: Character.at_object_creation() in `beckonmu/typeclasses/characters.py`
- Triggers: When character first created (during character creation flow)
- Responsibilities: Initialize character.db.stats, character.db.vampire, character.db.pools, character.db.humanity_data, character.db.advantages, character.db.experience, character.db.effects with default V5 values

**Character Login:**
- Location: Character.at_post_puppet() (not yet overridden, uses Evennia default)
- Triggers: When account puppets character
- Responsibilities: Apply CharacterCmdSet (via CharacterCmdSet.at_cmdset_creation())

**Web Endpoints:**
- Location: `beckonmu/web/urls.py`
- Entry patterns:
  - `/` → web.website (public pages)
  - `/webclient/` → web.webclient (browser MUD client)
  - `/admin/` → web.admin (staff interface)
  - `/api/` → beckonmu.web.api (REST endpoints)
  - `/builder/` → beckonmu.web.builder (visual world editor)

## Error Handling

**Strategy:** Commands use try-except for graceful failures; styled error messages to player

**Patterns:**

- **Command Validation**: Check arguments in parse(); raise exception if invalid
- **Data Access**: Query game system models; catch ObjectDoesNotExist if not found
- **Character Data**: Check character.db.* for None/missing fields; use defaults
- **Lock Checks**: Access-based validation via Evennia's lock system (applied to objects)
- **Typed Errors**: Replace broad Exception catches with specific error types (see: recent security commit on builder branch)

Example pattern in v5 commands:
```python
def func(self):
    try:
        # Parse and validate
        # Access character data
        # Perform action
        # Send styled success message
    except ValueError as e:
        self.styled_error(f"Invalid input: {e}")
    except Character.DoesNotExist as e:
        self.styled_error(f"Target not found: {e}")
```

## Cross-Cutting Concerns

**Logging:** Evennia's built-in logging (logs to console and game/logs/)

**Validation:**
- Input validation in command.parse()
- Model validation via Django validators (MinValueValidator, MaxValueValidator on trait values)
- Web builder validators in `beckonmu/web/builder/validators.py`

**Authentication:**
- Account system via Evennia default
- Character ownership verified by account puppet relationship
- Staff commands check character.is_superuser

**Authorization:**
- Lock system for object access control
- Staff status for admin commands (CmdStatusAdmin, CmdBoonAdmin)
- Builder permissions: BuildProject.user = creator; is_public flag for sharing

**Data Consistency:**
- Atomic transactions for multi-step operations (Jobs bucket operations use Django transaction)
- Character.db.* attributes auto-saved by Evennia after command execution
- Game system models use Django ORM for consistency

**Performance:**
- Django ORM select_related/prefetch_related for N+1 avoidance
- Evennia caches character objects in memory; db attributes lazy-loaded
- Web builder stores entire map as JSON blob (BuildProject.map_data) for atomicity
