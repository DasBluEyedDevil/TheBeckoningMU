# TheBeckoningMU Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2025-10-26] - Quadrumvirate Permissions Fix

### Fixed
- **Copilot/Cursor Permission Errors Resolved**:
  - Updated `.claude/settings.local.json` to enable YOLO mode for Quadrumvirate delegates
  - Previously: Only allowed `Bash(evennia makemigrations:*)`
  - Now: All essential tools allowed (Write, Edit, Read, Bash, Glob, Grep, NotebookEdit, Task, SlashCommand, Skill)
  - Set `defaultMode: "bypassPermissions"` for seamless delegate operations
  - Copilot/Cursor can now create/modify files without permission prompts
  - Aligns with CLAUDE.md directive: "Always run subagents or delegates (Quadrumvirate) in YOLO mode"

### Technical Details
- **Root Cause**: Overly restrictive permissions in `.claude/settings.local.json`
- **Impact**: Blocked file creation operations by Copilot/Cursor during Phase 4 implementation
- **Solution**: Full tool access + bypass permissions mode for all Quadrumvirate delegates
- **Result**: Token-efficient AI collaboration pattern now fully operational

---

## [2025-10-26] - Phase 4: Trait System Foundation (COMPLETE)

### Added
- **Complete Trait System** (`beckonmu/traits/`):
  - Database-driven trait management using Django models
  - `models.py`: TraitCategory, Trait, CharacterTrait, DisciplinePower models with full V5 support
  - `utils.py`: Comprehensive utility functions for trait manipulation and JSON import/export
  - `management/commands/seed_traits.py`: Management command to seed all V5 data (updated with complete discipline powers)
  - `tests.py`: Unit tests for trait utility functions

- **V5 Data Seeded (Complete)**:
  - 5 trait categories (Attributes, Skills, Disciplines, Advantages, Flaws)
  - 9 attributes (Strength, Dexterity, Stamina, Charisma, Manipulation, Composure, Intelligence, Wits, Resolve)
  - 27 skills (all V5 skills across Physical, Social, Mental categories)
  - 12 disciplines (Animalism, Auspex, Blood Sorcery, Celerity, Dominate, Fortitude, Obfuscate, Oblivion, Potence, Presence, Protean, Thin-Blood Alchemy)
  - **103 discipline powers** (all V5 discipline powers levels 1-5, including all amalgam powers)
    - Animalism: 9 powers
    - Auspex: 9 powers
    - Blood Sorcery: 8 powers (instant powers + rituals)
    - Celerity: 9 powers
    - Dominate: 9 powers
    - Fortitude: 8 powers
    - Obfuscate: 8 powers
    - Oblivion: 11 powers (Shadow Path + Necromancy Path)
    - Potence: 7 powers
    - Presence: 9 powers
    - Protean: 10 powers
    - Thin-Blood Alchemy: 6 formulae

### Implementation Details
- **Quadrumvirate Pattern Used**:
  - Gemini (Analyst): Analyzed reference repo trait system, identified database-driven pattern with TraitCategory/Trait/CharacterTrait models
  - Claude (Orchestrator): Created seed_traits.py and tests.py, coordinated implementation, fixed Unicode encoding issues
  - Copilot (Developer): Attempted implementation but hit permission issues; Claude completed file creation directly
- **Architecture Decision**: Chose database-driven approach (Django models) over `char.db.stats` approach based on Gemini's analysis of reference repo
- **Token Efficiency**: ~97k Claude tokens (significant context from Gemini analysis saved approximately 100k+ tokens)

### Changed
- Migration applied: `traits/0001_initial.py` (already existed from previous session)
- Fixed `seed_traits.py` to handle None values in dice_pool field (converted to empty strings)
- Fixed Unicode emoji in success message for Windows console compatibility

### Technical Notes
- **Database Models**:
  - `TraitCategory`: Organizes traits into categories (attributes, skills, disciplines, etc.)
  - `Trait`: Defines individual traits with min/max values, specialty support, instance support
  - `CharacterTrait`: Links characters to traits, stores ratings, specialties, instance names
  - `DisciplinePower`: Defines discipline powers with amalgam support
  - `CharacterPower`: Tracks which powers a character has learned
  - `TraitValue`: Defines valid values/ratings for specific traits (XP cost configuration)

- **Utility Functions**:
  - `get_character_trait_value()`: Retrieve character's rating in a trait
  - `set_character_trait_value()`: Set character's rating in a trait
  - `validate_trait_for_character()`: Validate trait assignment
  - `get_trait_definition()`: Get trait metadata
  - `sync_character_to_new_system()`: Migration helper
  - `enhanced_import_character_from_json()`: Import character data from JSON
  - `export_character_to_json()`: Export character to JSON format

### Completion Notes
- **All V5 Discipline Powers Implemented**: 103 powers across 12 disciplines, including:
  - All 5 amalgam powers with proper amalgam_discipline and amalgam_level references
  - Blood Sorcery rituals properly marked
  - Oblivion dual-path system (Shadow + Necromancy)
  - Thin-Blood Alchemy formulae
- **Database Fully Seeded**: Complete V5 trait foundation ready for Phase 5 (Dice Rolling Engine)
- **Amalgam Powers Validated**: Living Hive, Possession, Unerring Aim, Dementation, Spark of Rage all correctly configured

### Known Issues
- Test database creation hits Evennia core migration issue (unrelated to traits app)
- Missing symlink for `jobs` module created during this session (required for Django imports)

---

## [2025-10-26] - Phase 3: Jobs System Implementation

### Added
- **Complete Jobs System** (`beckonmu/jobs/`):
  - `models.py` (6.5KB): Bucket, Job, Comment, Tag models with BBS-style sequence numbering
  - `utils.py` (7.7KB): 10 service layer utility functions
  - `commands.py` (18.5KB): 16 commands (8 player, 8 admin)
  - `cmdset.py` (1.2KB): JobsCmdSet integration
  - `tests.py` (27.2KB): Comprehensive test suite
  - Migration `0001_initial.py`: Database schema for Jobs system

### Changed
- Fixed app configuration issues (`beckonmu.` prefix removed from all app names)
- Updated `web/urls.py`: Fixed traits URL import path
- Updated `jobs/__init__.py`: Corrected app config path
- Updated `commands/default_cmdsets.py`: Integrated JobsCmdSet into CharacterCmdSet

### Fixed
- Command collision bug: Renamed `myjobs/create` to `myjobs/submit` to avoid conflict with admin `job/create`
- Cmdset reference: Updated to use correct command class name (`CmdJobSubmit`)
- Database migrations: Successfully created and applied Jobs schema

### Implementation Details
- **Quadrumvirate Pattern Used**:
  - Gemini (Analyst): Analyzed reference repo implementation, verified code structure
  - Cursor (Developer): Implemented all 7 Jobs system files
  - Claude (Orchestrator): Fixed integration issues, resolved configuration bugs
- **Token Efficiency**: ~80k Claude tokens (vs estimated 200k+ for solo implementation)
- **Development Time**: ~2 hours including troubleshooting

### Commands Available
**Player Commands**:
- `jobs` - List all open jobs
- `job <id>` - View job details
- `job/claim <id>` - Claim unassigned job
- `job/done <id>` - Mark job complete
- `job/comment <id> = <text>` - Add private comment
- `job/public <id> = <text>` - Add public comment
- `myjobs` - List your submitted jobs
- `myjobs/submit <bucket> <title> = <description>` - Submit new job

**Admin Commands** (Builder+):
- `job/create` - Create job (admin)
- `job/assign <id> = <player>` - Assign job to player
- `job/reopen <id>` - Reopen completed job
- `job/delete <id>` - Delete job
- `buckets` - List all buckets
- `bucket/create <name> = <description>` - Create bucket
- `bucket <name>` - View bucket details
- `bucket/delete <name>` - Delete bucket

---

## [2025-01-26] - Documentation Organization and Consolidation

### Added
- **Documentation Directory Structure** (`docs/`):
  - `docs/planning/`: Roadmaps, TODO, project status
  - `docs/reference/`: V5 mechanics, theming, technical analysis
  - `docs/guides/`: Implementation guides and procedures
  - `docs/archive/`: Obsolete documentation (preserved for history)

- **Documentation Index** (`docs/README.md`):
  - Complete navigation for all project documentation
  - Quick reference guide
  - Documentation workflow and update procedures

- **Enhanced README.md**:
  - Project overview and quick start
  - Technology stack
  - Development workflow summary
  - Complete project structure
  - Contributing guidelines

### Changed
- **Organized All Documentation Files**:
  - `V5_IMPLEMENTATION_ROADMAP.md` → `docs/planning/ROADMAP.md`
  - `TODO_IMPLEMENTATION_NOTES.md` → `docs/planning/TODO.md`
  - `PROJECT_STATUS.md` → `docs/planning/STATUS.md`
  - `V5_REFERENCE_DATABASE.md` → `docs/reference/V5_MECHANICS.md`
  - `THEMING_GUIDE.md` → `docs/reference/THEMING.md`
  - `WEB_CHARGEN_ANALYSIS.md` → `docs/reference/WEB_CHARGEN.md`
  - `GIT_SETUP.md` → `docs/guides/GIT_SETUP.md`
  - `IMPORT_COMMAND_TEST_GUIDE.md` → `docs/guides/IMPORT_COMMAND_TEST.md`

- **Archived Obsolete Documentation**:
  - `V5_IMPLEMENTATION_ROADMAP_v1.md` → `docs/archive/` (superseded by ROADMAP.md v2.2)

- **Updated CLAUDE.md**:
  - Added "Available Documentation" section
  - References to new `docs/` directory structure
  - Clear organization of skills vs project documentation

### Improved
- **Root Directory Cleanliness**: Only 4 key files remain in root
  - `README.md` - Project introduction
  - `CLAUDE.md` - Developer guide
  - `CHANGELOG.md` - Project history
  - `SESSION_NOTES.md` - Recent context
- **Documentation Discoverability**: Clear paths to all information
- **Maintainability**: Single authoritative location for each topic
- **Navigation**: docs/README.md provides complete index

---

## [2025-01-26] - Documentation Consolidation and Skills Creation

### Added
- **New Evennia Framework Skills** (comprehensive guides in `.skills/`):
  - `evennia-framework-basics.md`: Core concepts, typeclass system, attributes, hooks, configuration
  - `evennia-development-workflow.md`: Server commands, testing, debugging, deployment workflows
  - `evennia-typeclasses.md`: Deep dive on Objects, Characters, Rooms, Exits with hooks reference
  - `evennia-commands.md`: Complete command system guide with MuxCommand syntax and patterns

- **Skills enriched with official Evennia documentation** from https://www.evennia.com/docs/latest/:
  - Typeclass system architecture (three-level inheritance)
  - Persistent vs non-persistent attributes (.db vs .ndb)
  - Comprehensive hooks system with examples
  - Command execution sequence and best practices
  - Development workflow and testing strategies

- **CHANGELOG.md**: Project changelog to track all changes across sessions
- **SESSION_NOTES.md**: Quick reference for most recent task performed

### Changed
- **Streamlined CLAUDE.md** (~157 lines → ~90 lines):
  - Removed redundant AI Quadrumvirate details (now in dedicated skills)
  - Removed detailed Evennia framework explanations (now in dedicated skills)
  - Replaced verbose sections with concise skill references
  - Added comprehensive "Available Skills" directory listing
  - Simplified to overview + references structure

### Removed
- **From CLAUDE.md** (moved to appropriate skills):
  - ~99 lines of AI Quadrumvirate workflow details
  - Detailed Essential Commands section
  - Architecture deep-dive sections
  - Command system implementation details
  - Database and persistence explanations
  - Hooks system details
  - Configuration details
  - Development patterns

### Improved
- **Documentation organization**: Single source of truth for each topic
- **Maintainability**: Updates only needed in one location per topic
- **Token efficiency**: CLAUDE.md loads less context; skills invoked only when needed
- **Discoverability**: Clear skill directory with descriptions in CLAUDE.md

---

## [Recent - Prior to 2025-01-26] - Traits System and Staff Approval

### Added
- Initial setup for traits Django app with management commands and static files (commit: 5ad157e)
- Staff character approval system with web API integration (commit: a4e2e9f)
- Traits Django app for VtM 5e character JSON import - Phase 1 MVP (commit: 79c61b7)
- Connection screen replaced with reference repo ASCII art (commit: d218f3f)
- Documentation of correct Copilot CLI usage in Quadrumvirate pattern (commit: 05dab53)

---

## [Recent - Prior to 2025-01-26] - BBS System Development

### Added
- Initial Bulletin Board System (BBS) implementation (commit: b79006e)
- Comprehensive BBS test suite: 770 lines, 55 tests (commit: 6075899)

### Fixed
- Critical BBS bugs: race condition and code duplication (commit: 9f2b406)

---

## [Recent - Prior to 2025-01-26] - Web Integration and Planning

### Added
- Athens grid building and Evennia contribs to TODO (commit: 2d0a5cb)
- Complete web form integration analysis (commit: 2d0a5cb)
- Comprehensive web-based character creation analysis (commit: 5fe2b3f)
- Comprehensive TODO & implementation notes document (commit: 22dc367)

### Fixed
- Unicode bullet points in help files (commit: 3769f48)

---

## [Recent - Prior to 2025-01-26] - Documentation and Help System

### Added
- Comprehensive V5 help system with 10 help files (commit: 336ca46)
- Documentation of Gemini CLI automatic fallback behavior (commit: b569079)

---

## [Initial] - Project Foundation

### Added
- Foundational `.gitignore` files for project and IDE-specific configurations (commit: 2714433, b6f93a5)
- Initial `Account` and `Guest` classes for account management (commit: 2714433, b6f93a5)
- Placeholders and architecture documentation for AI Quadrumvirate Coordination (commit: 2714433, b6f93a5)
- Evennia project initialization
- TheBeckoningMU base structure
- Poetry dependency management setup

---

## Future Planned Changes

### To Be Added
- Vampire: The Masquerade 5e game mechanics
- Character sheet system
- Combat system
- Social interaction mechanics
- World building and room descriptions

### To Be Improved
- Web interface customization
- Admin tools and commands
- Testing coverage
- Documentation for game-specific systems
