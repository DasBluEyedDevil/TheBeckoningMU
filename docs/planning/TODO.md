# Implementation TODO & Notes

This document tracks important future implementation tasks and notes for TheBeckoningMU.

## CRITICAL: AI Quadrumvirate Usage Pattern

**ALWAYS FOLLOW THIS PATTERN TO PRESERVE CLAUDE'S TOKENS**

### The Four Roles

1. **Claude Code (Orchestrator)** - Planning & decision-making only
   - Gather requirements
   - Query Gemini for analysis
   - Delegate implementation
   - Verify results
   - **NEVER read large files (>100 lines) - ask Gemini**
   - **NEVER implement complex features - delegate**
   - **ONLY trivial edits (<5 lines)**

2. **Gemini CLI (Analyst)** - 1M+ context window
   - Analyze entire codebase
   - Trace bugs across files
   - Answer architectural questions
   - Security & performance audits
   - **Note**: Has automatic fallback to Flash model when Pro quota exhausted
   - Both Pro and Flash models can hit rate limits (429 errors)
   - Use `-m, --model` flag to explicitly specify model if needed

3. **Cursor CLI (Developer #1)** - UI/visual work
   - Implement UI components
   - Complex reasoning tasks
   - Visual validation with screenshots
   - Cross-check Copilot's work
   - **Run via WSL wrapper**: `wsl.exe bash -c "cd '/mnt/c/path' && cursor-agent -p --model sonnet-4.5 --output-format text --force 'TASK'"`

4. **Copilot CLI (Developer #2)** - Backend work
   - Implement backend features
   - GitHub operations (gh commands)
   - Terminal tasks
   - Cross-check Cursor's work
   - **Usage**: `copilot -p "TASK" --allow-all-tools`

### Token Efficiency Targets

- Feature development: <5k Claude tokens (86% savings vs 35k)
- Bug fixes: <2k Claude tokens (93% savings vs 28k)
- Code reviews: <1k Claude tokens (96% savings vs 28k)

---

## High Priority Implementation Tasks

### 1. Web-Based Character Creation (JSON Import)

**Status**: ✅ **ANALYSIS COMPLETE** - See `WEB_CHARGEN_ANALYSIS.md`

**Objective**: Integrate web-based character creation form that exports JSON for server import

**Reference**:
- Web form: https://beckon.vineyard.haus/character-creation-new.html
- Reference repo implementation at: `reference repo/BeckoningMU-master/`
- **Complete Documentation**: `WEB_CHARGEN_ANALYSIS.md` (720+ lines)

**Implementation Phases**:

**Phase 1 (MVP - HIGH PRIORITY)**:
- [ ] Copy Django models from reference repo (`traits/models.py`)
- [ ] Copy enhanced import utilities (`traits/utils.py`)
- [ ] Copy RESTful API endpoints (`traits/api.py`)
- [ ] Implement `import` command in chargen cmdset
- [ ] Create `server/conf/character_imports/` directory
- [ ] Test with sample V5 character JSON

**Phase 2 (API Integration - MEDIUM)**:
- [ ] Add API URL routes to `web/urls.py`
- [ ] Add session-based authentication
- [ ] Add rate limiting
- [ ] Add CSRF protection (remove @csrf_exempt)
- [ ] Test API endpoints with curl/Postman

**Phase 3 (Web Form - LOW)**:
- [ ] Copy web forms to `beckonmu/web/static/chargen/`
- [ ] Add missing 4 clans (Banu Haqim, Hecata, Lasombra, Ministry)
- [ ] Add discipline power selection UI
- [ ] Add specialties interface
- [ ] Replace localStorage with AJAX API calls
- [ ] Add session integration
- [ ] Auto-create character object on form load
- [ ] Auto-submit approval job on import

**Files to Create/Modify**:
- `beckonmu/traits/models.py` - Django ORM for character traits
- `beckonmu/traits/utils.py` - Enhanced import/validation
- `beckonmu/traits/api.py` - RESTful endpoints (7 total)
- `beckonmu/commands/chargen.py` - Add `CmdImportCharacter` class
- `beckonmu/web/static/chargen/` - Web form files (Phase 3)

**Security Considerations** (see analysis doc for details):
- File path validation (prevent directory traversal)
- Authentication required for API endpoints
- Input sanitization for JSON fields
- Authorization checks (only import to own characters)

---

### 2. Enhanced Grid Building System (Athens Setting)

**Status**: 🆕 **PRIORITY: HIGH**

**Objective**: Create intuitive, dynamic building system for Athens grid far superior to stock Evennia/traditional MU*s

**Requirements**:
- Modern day Athens as the primary setting
- Easy room creation with minimal commands
- Dynamic/customizable room descriptions
- Template-based building (room types: Street, Building, Haven, Elysium, etc.)
- Batch building support for city blocks/districts
- Visual grid map generation
- Copy/paste/modify room patterns
- Import from spreadsheet/JSON for bulk creation

**Potential Approaches**:
1. **Evennia Batch Code System** (`.ev` files)
   - Reference: `world/batch_cmds.ev` in reference repo
   - Pro: Built-in, version controlled, repeatable
   - Con: Syntax can be clunky

2. **Custom Build Commands** (MUX-style enhanced)
   - `+dig <name>=<exit to>,<exit from>`
   - `+desc/set <location>=<template>` with variable substitution
   - `+clone <source>` to duplicate room patterns
   - Pro: Familiar to MU* builders, fast for experienced staff
   - Con: Still command-line based

3. **Web-Based Grid Builder** (BEST FOR YOUR GOALS)
   - Visual drag-and-drop interface
   - Template selection from library
   - Batch operations (create entire district)
   - Preview before committing
   - Export/import grid layouts
   - Pro: Most user-friendly, modern UX
   - Con: Requires frontend development

4. **Spreadsheet Import System**
   - Define grid in Excel/Google Sheets (Room Name, Description, Exits, Type)
   - Upload CSV/JSON
   - Auto-generate entire city district
   - Pro: Non-technical staff can build, easy collaboration
   - Con: Less interactive

**Recommended Hybrid Approach**:
- Phase 1: Enhanced batch code system with templates
- Phase 2: Spreadsheet import for bulk creation
- Phase 3: Web-based visual builder

**Features to Include**:
- [ ] Room templates (Street, Cafe, Nightclub, Haven, Elysium, etc.)
- [ ] Variable substitution in descriptions (time of day, weather, season)
- [ ] Auto-generate exits with proper reverse exits
- [ ] District organization (Plaka, Monastiraki, Kolonaki, etc.)
- [ ] Landmark system (Acropolis, Syntagma Square, etc.)
- [ ] Random description variations (prevent repetition)
- [ ] Object spawning (furniture, props)
- [ ] Lighting system (day/night descriptions)
- [ ] Access control (public, private, vampire-only)
- [ ] Grid visualization (ASCII map or web-based)

**Evennia Tools to Leverage**:
- `evennia.prototypes` - Object templates
- `evennia.utils.batchprocessors` - Batch building
- `evennia.contrib.grid` - Grid contrib (if available)
- `evennia.utils.create` - Programmatic object creation

**Athens-Specific Details to Include**:
- Modern Greek street names
- Authentic neighborhood descriptions
- Historical landmarks (Parthenon, Agora, etc.)
- Modern venues (clubs, cafes, tech hubs)
- Hidden Camarilla locations
- Nosferatu tunnels beneath the city
- Elysium locations (museums, galleries, theaters)

**Files to Create**:
- `beckonmu/world/athens_templates.py` - Room templates for Athens
- `beckonmu/world/grid_builder.py` - Enhanced building utilities
- `beckonmu/commands/building.py` - Custom build commands
- `beckonmu/web/grid/` - Web-based grid builder (Phase 3)
- `beckonmu/world/batch_files/athens_plaka.ev` - Example district

---

### 3. Evennia Contribs Integration

**Status**: Research complete - Reference repo uses 4 contribs

**Objective**: Leverage Evennia contrib packages instead of building from scratch

**Contribs Used in Reference Repo**:
1. ✅ **`evennia.contrib.base_systems.color_markups`** - MUX-style ANSI color codes
   - Already configured in reference repo's `settings.py`
   - Provides `|W`, `|y`, `|[R`, `|n` etc. color syntax
   - **Action**: Copy color config from reference repo

2. ✅ **`evennia.contrib.game_systems.multidescer`** - Multiple description system
   - Used in `commands/character_customization.py`
   - Allows characters to have multiple descriptions (outfits, poses)
   - **Action**: Import `CmdMultiDesc` into custom cmdset

3. ✅ **`evennia.contrib.game_systems.mail`** - In-game mail system
   - Used in `commands/comms.py`
   - Provides `CmdMail` for player-to-player messages
   - **Action**: Import `CmdMail` into communication cmdset

4. ✅ **`evennia.contrib.utils.git_integration`** - Git version control
   - Used in `commands/default_cmdsets.py`
   - Provides in-game Git commands for staff
   - **Action**: Import `GitCmdSet` for developer cmdset

**Potentially Useful Contribs** (not yet in reference repo):
- [ ] `evennia.contrib.grid.xyzgrid` - Spatial grid system (for Athens map)
- [ ] `evennia.contrib.game_systems.crafting` - Crafting system (Blood Alchemy?)
- [ ] `evennia.contrib.game_systems.dice` - Dice rolling system (V5 dice pools)
- [ ] `evennia.contrib.rpg.traits` - Character trait system (alternative to custom traits)
- [ ] `evennia.contrib.tutorials.tutorial_world` - Reference for room building patterns

**Tasks**:
- [x] Identify contribs used in reference repo
- [ ] Copy color markup configuration
- [ ] Import multidescer for character customization
- [ ] Import mail system for IC communication
- [ ] Import Git integration for staff development
- [ ] Research xyzgrid for Athens spatial mapping
- [ ] Evaluate dice contrib vs custom V5 dice system

**Reference**: https://www.evennia.com/docs/latest/Contribs/Contribs-Overview.html

**Potential Contribs to Explore**:
- Character sheet display systems
- Dice rolling systems (compare with our V5 dice engine)
- Menu systems for chargen
- Extended Room features
- Combat systems
- Mail/messaging systems
- Any MUSH-related contribs

**Tasks**:
- [ ] Review Evennia contribs documentation (Gemini)
- [ ] Identify useful contribs for V5 MUSH
- [ ] Evaluate vs custom implementation
- [ ] Integrate or adapt relevant contribs
- [ ] Document decisions in CLAUDE.md

---

### 3. ASCII Art & Border Styles Library

**Status**: Reference collected

**Objective**: Create reusable ASCII border styles for help files and output

**Border Style Examples Collected**:
```
+===================================================================+  # Current style
*******************************************************************
/-----------------------------------------------------------------\
.~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.
oOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOoOo
-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-~=x|x=~-
,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-,.'-.
[|=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=|]
╔═════════════════════════════════════════════════════════════╗  # May not render on all clients
```

**Reference**:
- https://asciiart.website/cat.php?category_id=85
- User-provided examples in conversation

**Tasks**:
- [ ] Create `beckonmu/world/ansi_borders.py` with border templates
- [ ] Functions for generating bordered text blocks
- [ ] Support for different themes (gothic, tech, classic)
- [ ] Integration with help system
- [ ] Integration with character sheet output

---

## Medium Priority Tasks

### 4. V5 Data Models Implementation

**Status**: Reference database complete, implementation pending

**Reference**: V5_REFERENCE_DATABASE.md (if exists in reference repo)

**Tasks**:
- [ ] Create `beckonmu/world/v5_traits.py` - Trait system (attrs/skills)
- [ ] Create `beckonmu/world/v5_mechanics.py` - Core mechanics (Hunger, BP)
- [ ] Implement Character typeclass V5 extensions
- [ ] Add db attribute schema
- [ ] Create validation functions
- [ ] Unit tests for all V5 mechanics

---

### 5. Command Implementation (Follow Refactored BBS Pattern)

**Status**: Architecture defined, implementation pending

**Pattern**: Small single-responsibility commands + shared utility modules

**Reference**: `reference repo/BeckoningMU-master/bbs/new_commands.py` (gold standard)

**Tasks**:
- [ ] Implement +roll command (dice rolling)
- [ ] Implement +check command (quick roll)
- [ ] Implement +rouse command (Rouse checks)
- [ ] Implement +sheet command (character sheet display)
- [ ] Implement +spend command (XP spending)
- [ ] Create command utilities module

---

## Low Priority / Future Enhancements

### 6. Enhanced Help System Features

**Tasks**:
- [ ] Add help search functionality
- [ ] Add help aliases (e.g., "help vamp" → "help vampire")
- [ ] Create help index by topic
- [ ] Add "related topics" auto-linking
- [ ] Implement help voting/rating

---

### 7. Admin Tools

**Tasks**:
- [ ] Staff commands for character approval
- [ ] +grant command (XP, status, boons)
- [ ] +inspect command (detailed character data)
- [ ] Logging system for staff actions
- [ ] Audit trail for character changes

---

## Completed Tasks

### ✅ Phase 0: Help System (2025-10-20)
- [x] Configure FILE_HELP_ENTRY_MODULES in settings.py
- [x] Create help_entries.py with directory walker
- [x] Create 10 comprehensive help files:
  - general/welcome.txt
  - commands/commands.txt
  - v5/v5.txt, v5/hunger.txt, v5/disciplines.txt
  - v5/clans.txt, v5/status.txt, v5/boons.txt
  - v5/chargen.txt, v5/roll.txt
- [x] Use simple ASCII borders (+===+) with ANSI color codes
- [x] Add principle #0 to V5 Commands README (leverage Evennia built-ins)
- [x] Commit to git

---

## Development Guidelines Reminders

### When NOT to Use Claude Code Directly

❌ Reading files >100 lines → Use Gemini
❌ Implementing complex features → Delegate to Cursor/Copilot
❌ Analyzing large codebases → Use Gemini
❌ UI/visual work → Delegate to Cursor
❌ Backend implementation → Delegate to Copilot

### When TO Use Claude Code

✅ Gathering requirements
✅ Planning implementation approach
✅ Querying Gemini for analysis
✅ Delegating to Cursor/Copilot
✅ Trivial edits (<5 lines)
✅ Verifying final results
✅ Creating TODO lists and plans

---

## Notes

- Keep this file updated as new tasks are identified
- Use TodoWrite tool for active task tracking
- Reference this document when planning work
- Always check "Completed Tasks" before starting work
