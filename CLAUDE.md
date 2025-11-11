# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Session Start Protocol

**MANDATORY: Always start each session by:**
1. Reading `.devilmcp/LAST_SESSION.md` for immediate context
2. Reading recent entries in `.devilmcp/CHANGELOG.md` (last 3-5 sessions)
3. Checking `git status` for current working state
4. Reviewing `.devilmcp/PROJECT_CONTEXT.md` for architectural reference (as needed)

## Session End Protocol

**MANDATORY: Always end each session by:**
1. Updating `.devilmcp/CHANGELOG.md` with all changes made
2. Updating `.devilmcp/LAST_SESSION.md` with current state and context
3. Documenting any incomplete work or next steps
4. Running tests if significant changes were made (when applicable)
5. Committing changes if requested by user

## DevilMCP Context Management

This project uses **DevilMCP** (Model Context Protocol) for comprehensive project context management and decision tracking.

### DevilMCP Storage
- **Location:** `.devilmcp/` directory in project root
- **PROJECT_CONTEXT.md:** Comprehensive architectural documentation
- **CHANGELOG.md:** Session-based change history (append-only)
- **LAST_SESSION.md:** Quick context for session resumption (overwrite each session)

### When to Update DevilMCP Files
- **Always:** Update LAST_SESSION.md at end of session
- **Always:** Append to CHANGELOG.md for significant changes
- **When needed:** Update PROJECT_CONTEXT.md for architectural changes
- **Best practice:** Use DevilMCP tools for decision tracking and impact analysis

### DevilMCP Tools Available
If DevilMCP server is running, you have access to 30+ tools:
- Project structure analysis
- Decision logging and tracking
- Change impact assessment
- Cascade failure detection
- Thought process management

**See:** DevilMCP README at `C:\Users\dasbl\AndroidStudioProjects\DevilMCP\README.md`

## Project Overview

TheBeckoningMU is an Evennia-based MUD (Multi-User Dungeon) game project. Evennia is a Python framework for building MUDs and other multiplayer text-based games. This project uses Python 3.13+ and Poetry for dependency management.

## Essential Commands

### Initial Setup
```bash
# Initialize the database (first time only)
evennia migrate

# Create superuser when prompted during first start
evennia start
```

### Development Workflow
```bash
# Start the server (logs to console)
evennia start

# Stop the server
evennia stop

# Restart the server
evennia restart

# Reload the server (without full restart, preserves sessions)
evennia reload

# Check server status
evennia status

# Run tests
evennia test

# Access Python shell with Evennia context
evennia shell
```

### Server Access
- MUD client: `localhost:4000`
- Web client: `http://localhost:4001`
- Web character creation: `http://localhost:4001/character-creation/`
- Staff character approval: `http://localhost:4001/staff/character-approval/`
- Admin interface: `http://localhost:4001/admin`

## Architecture

### Evennia Typeclass System

Evennia uses a "typeclass" pattern where game entities inherit from base classes. All entities with a location in the game world inherit from `DefaultObject` at some level.

**Key Typeclasses:**
- **Objects** (`typeclasses/objects.py`): Base class for all in-game items
- **Characters** (`typeclasses/characters.py`): Player-controlled entities (inherit from Objects)
- **Rooms** (`typeclasses/rooms.py`): Locations in the game world
- **Exits** (`typeclasses/exits.py`): Connections between rooms
- **Accounts** (`typeclasses/accounts.py`): Player accounts (OOC entities)
- **Scripts** (`typeclasses/scripts.py`): Time-based or persistent game logic
- **Channels** (`typeclasses/channels.py`): Communication channels

### ObjectParent Mixin Pattern

The `ObjectParent` class in `typeclasses/objects.py` is a mixin used to override behavior for ALL entities inheriting from `DefaultObject` (Objects, Exits, Characters, Rooms). Add methods here to affect all game entities with a location.

### Directory Structure

- **`beckonmu/typeclasses/`**: Game entity definitions (Objects, Characters, Rooms, etc.)
  - Each module contains skeleton classes that inherit from Evennia defaults
  - Override methods in these classes to customize behavior

- **`beckonmu/commands/`**: Command definitions and command sets
  - `command.py`: Base command class for this game
  - `default_cmdsets.py`: Command set definitions
  - Commands use MUX-style syntax: `command[/switch] arg1, arg2 = value1, value2`

- **`beckonmu/world/`**: Game-specific code (economy, combat, batch scripts)
  - `prototypes.py`: Object prototypes for spawning
  - `help_entries.py`: Custom help entries

- **`beckonmu/server/conf/`**: Server configuration
  - `settings.py`: Main configuration file (overrides Evennia defaults)
  - `secret_settings.py`: Secret/server-specific settings (gitignored)
  - Other conf files: hooks, lock functions, input/inline functions, connection screens

- **`beckonmu/web/`**: Web interface customization
  - Django-based web application
  - `website/`: Public-facing website
  - `webclient/`: Web-based MUD client
  - `admin/`: Admin interface customization
  - `api/`: REST API endpoints

### Command System

Commands inherit from `evennia.commands.command.Command` or its MuxCommand variant. Each command implements:

1. **`at_pre_cmd()`**: Pre-execution hook (abort if returns truthy)
2. **`parse()`**: Parse `self.args` into useful attributes (switches, lhs/rhs, etc.)
3. **`func()`**: Main command logic (required)
4. **`at_post_cmd()`**: Post-execution hook

Commands are organized into Command Sets (cmdsets) which are attached to objects dynamically.

### Database and Persistence

Evennia uses Django ORM for database operations. Game objects have two attribute systems:

- **`self.db.*`**: Persistent attributes (stored in database)
- **`self.ndb.*`**: Non-persistent attributes (memory only, cleared on reload)

### Hooks System

Evennia provides numerous hooks (methods called at specific times):

- **Object lifecycle**: `at_object_creation()`, `at_object_delete()`, `at_init()`
- **Movement**: `at_pre_move()`, `announce_move_from()`, `at_post_move()`
- **Puppeting**: `at_pre_puppet()`, `at_post_puppet()`, `at_pre_unpuppet()`
- **Server events**: `at_server_reload()`, `at_server_shutdown()`
- **Interaction**: `at_traverse()` (exits), `at_get()`, `at_drop()`, `at_say()`

Override these hooks in typeclasses to customize behavior.

## Configuration

- Main settings: `beckonmu/server/conf/settings.py`
- Game name: Set via `SERVERNAME` in settings.py
- Default settings: https://www.evennia.com/docs/latest/Setup/Settings-Default.html
- Only override settings you actually need to change (don't copy entire default file)

## Important Notes

- **Virtual environment**: The project uses a `.venv` directory for Python packages
- **Poetry**: This project uses Poetry for dependency management (`poetry.toml`, `pyproject.toml`)
- **Server structure**: Do NOT restructure the `server/` directory—Evennia expects its layout
- **Module discovery**: New subdirectories require `__init__.py` files
- **Settings paths**: Use `GAME_DIR` and `EVENNIA_DIR` for file paths in settings
- **Evennia version**: Installed in virtualenv at `.venv/Scripts/evennia`

## Development Patterns

### Creating Custom Commands

1. Create command class in `commands/` inheriting from `Command`
2. Implement `func()` method with command logic
3. Add to appropriate command set in `default_cmdsets.py`
4. Update settings if using custom cmdset location

### Creating Custom Typeclasses

1. Define class in appropriate `typeclasses/` module
2. Inherit from `ObjectParent` mixin + Evennia default class
3. Override `at_object_creation()` for initialization
4. Override other hooks as needed for custom behavior

### Modifying All Game Entities

Add methods to `ObjectParent` mixin in `typeclasses/objects.py`. These affect Objects, Characters, Rooms, and Exits.

## AI Quadrumvirate Coordination (CRITICAL)

**YOU MUST FOLLOW THIS PATTERN TO PRESERVE TOKEN COUNT**

This project uses the AI Quadrumvirate pattern for token-efficient development. See `.skills/ai-quadrumvirate-coordination.md` for complete details.

### The Four Roles

1. **Claude Code (You)**: Orchestrator and decision-maker
   - Gather requirements and create plans
   - Query Gemini for analysis
   - Delegate implementation to Cursor/Copilot
   - Verify final results
   - **NEVER read large files (>100 lines) - ask Gemini**
   - **NEVER implement complex features - delegate**
   - **ONLY perform trivial edits (<5 lines)**

2. **Gemini CLI**: Unlimited code analyst (1M+ context)
   - Analyze entire codebase before implementation
   - Trace bugs across files
   - Answer architectural questions
   - Security and performance audits

3. **Cursor CLI**: UI/visual developer (expendable tokens)
   - Implement UI components
   - Complex reasoning tasks (with thinking models)
   - Take screenshots for validation
   - Cross-check Copilot's work

4. **Copilot CLI**: Backend developer (expendable tokens)
   - Implement backend features
   - GitHub operations
   - Terminal tasks
   - Cross-check Cursor's work

### Mandatory Workflow for All Tasks

**Phase 1: Requirements & Planning** (Claude - minimal tokens)
```
1. Gather user requirements
2. Use superpowers:brainstorming if applicable
3. Create TodoWrite plan
```

**Phase 2: Codebase Analysis** (Gemini - 0 Claude tokens)
```bash
gemini -p "@beckonmu/
Task: [description]

Questions:
1. What files will be affected?
2. Are there similar patterns already implemented?
3. What is the recommended approach?
4. What are the risks?

Provide file paths and code excerpts."
```

**Phase 3: Implementation** (Cursor/Copilot - 0 Claude tokens)
```bash
# For UI/visual work - delegate to Cursor
wsl.exe bash -c "cd '/mnt/c/Users/dasbl/PycharmProjects/TheBeckoningMU' && cursor-agent -p --model sonnet-4.5 'TASK: [spec with Gemini context]'"

# For backend/terminal work - delegate to Copilot
copilot -p "TASK: [spec with Gemini context]"
```

**Phase 4: Verification** (Claude + Gemini - minimal tokens)
```bash
# Ask Gemini to verify architectural consistency
gemini -p "@beckonmu/ Verify changes: [summary from developers]"

# Use superpowers for final validation
superpowers:verification-before-completion
```

### Token Efficiency Targets

- Feature development: <5k Claude tokens (vs 35k old way = **86% savings**)
- Bug fixes: <2k Claude tokens (vs 28k old way = **93% savings**)
- Code reviews: <1k Claude tokens (vs 28k old way = **96% savings**)

### Success Criteria

You're doing it right when:
- ✅ Claude tokens <5k per task
- ✅ Gemini queried before reading files
- ✅ Cursor/Copilot do all implementation
- ✅ Developers cross-check each other
- ✅ Superpowers skills used for structure
- ✅ TodoWrite tracks progress

### Available AI Tools

Check `.skills/` directory for detailed guides:
- `ai-quadrumvirate-coordination.md`: Complete coordination patterns
- `gemini-cli-codebase-analysis.md`: How to query Gemini effectively
- `cursor-agent-advanced-usage.md`: Cursor CLI delegation patterns
- `github-copilot-cli-usage.md`: Copilot CLI usage

## Resources

- Evennia Documentation: https://github.com/evennia/evennia/wiki
- Evennia Tutorials: https://github.com/evennia/evennia/wiki/Tutorials
- Directory Overview: https://github.com/evennia/evennia/wiki/Directory-Overview#the-game-directory
- Default Settings: https://www.evennia.com/docs/latest/Setup/Settings-Default.html
