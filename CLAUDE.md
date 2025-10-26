# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TheBeckoningMU is an Evennia-based MUD (Multi-User Dungeon) game project. Evennia is a Python framework for building MUDs and other multiplayer text-based games. This project uses Python 3.13+ and Poetry for dependency management.

## Evennia Framework

TheBeckoningMU is built on Evennia, a Python framework for MUDs and multiplayer text games.

### Essential Skills

For comprehensive Evennia guidance, see the `.skills/` directory:
- **`evennia-framework-basics`**: Core concepts, architecture, typeclasses, attributes, hooks, configuration
- **`evennia-development-workflow`**: Server commands, testing, debugging, deployment
- **`evennia-typeclasses`**: Creating and working with Objects, Characters, Rooms, Exits, etc.
- **`evennia-commands`**: Command system, MuxCommand syntax, command sets

### Quick Command Reference

```bash
evennia start     # Start server
evennia stop      # Stop server
evennia reload    # Apply code changes (fast)
evennia test      # Run tests
evennia shell     # Django shell with Evennia context
```

**Server Access**: MUD client (localhost:4000), Web client (http://localhost:4001), Admin (http://localhost:4001/admin)

## Project Structure

```
beckonmu/
├── typeclasses/        # Game entity definitions (Objects, Characters, Rooms, Exits)
├── commands/           # Command definitions and command sets
├── world/              # Game-specific code (prototypes, help entries)
├── server/conf/        # Server configuration (settings.py, secret_settings.py)
├── web/                # Web interface (Django app)
└── traits/             # Vampire: The Masquerade 5e trait system
```

**Key Patterns**:
- **ObjectParent mixin** (`typeclasses/objects.py`): Methods here affect ALL game entities with a location
- **MuxCommand syntax**: Commands support MUX-style switches: `command/switch arg = value`
- **Attributes**: Use `.db` for persistent data (survives reloads), `.ndb` for temporary data
- **Hooks**: Override methods like `at_object_creation()`, `at_post_move()`, etc. to customize behavior

See Evennia skills for complete details on typeclasses, commands, hooks, and configuration.

## AI Development Workflow

**CRITICAL**: This project uses the AI Quadrumvirate pattern for token-efficient development.

For complete usage instructions, see the `.skills/` directory:
- **`ai-quadrumvirate-coordination.md`**: Core coordination patterns and workflows
- **`gemini-cli-codebase-analysis.md`**: How to query Gemini for codebase analysis
- **`cursor-agent-advanced-usage.md`**: How to delegate to Cursor CLI
- **`github-copilot-cli-usage.md`**: How to delegate to Copilot CLI

**Quick Summary**: Claude orchestrates; Gemini analyzes code (unlimited context); Cursor/Copilot implement (expendable tokens).

## Available Documentation

### Skills (`.skills/` directory)

**Evennia Framework**:
- `evennia-framework-basics.md`: Core concepts, architecture, typeclasses, attributes, hooks
- `evennia-development-workflow.md`: Server commands, testing, debugging, deployment
- `evennia-typeclasses.md`: Deep dive on Objects, Characters, Rooms, Exits, hooks
- `evennia-commands.md`: Command system, MuxCommand, command sets, patterns

**AI Development Workflow**:
- `ai-quadrumvirate-coordination.md`: Token-efficient development with Claude/Gemini/Cursor/Copilot
- `gemini-cli-codebase-analysis.md`: Using Gemini for unlimited-context code analysis
- `cursor-agent-advanced-usage.md`: Delegating UI/visual work to Cursor CLI
- `github-copilot-cli-usage.md`: Delegating backend work to Copilot CLI

### Project Documentation (`docs/` directory)

**Planning** (`docs/planning/`):
- `ROADMAP.md`: Complete 20-phase implementation plan (Phases 0-18b)
- `TODO.md`: Active tasks and implementation notes
- `STATUS.md`: Current project status and progress

**Reference** (`docs/reference/`):
- `V5_MECHANICS.md`: Complete V5 game mechanics database
- `THEMING.md`: ANSI art and gothic aesthetics guide
- `WEB_CHARGEN.md`: Web-based character creation analysis

**Guides** (`docs/guides/`):
- `GIT_SETUP.md`: Git configuration and workflow
- `IMPORT_COMMAND_TEST.md`: Testing character import commands

See **[docs/README.md](docs/README.md)** for complete documentation index.

## Resources

- **Evennia Documentation**: https://www.evennia.com/docs/latest/index.html
- **Evennia Wiki**: https://github.com/evennia/evennia/wiki
- **Evennia Tutorials**: https://github.com/evennia/evennia/wiki/Tutorials
- **Default Settings**: https://www.evennia.com/docs/latest/Setup/Settings-Default.html
- Always use "copilot" to engage Copilot CLI, not "gh copilot"
- You can delegate tasks to copilot and to cursor, it doesn't have to be one or the other, they can work in parallel
- Always grant Copilot/Cursor/Gemini full permissions when engaging them
- Never include "beckonmu." in the name of apps, as it causes migration errors