# TheBeckoningMU Documentation

Organized documentation for the TheBeckoningMU Vampire: The Masquerade 5th Edition MUSH project.

---

## Quick Navigation

### 📋 Planning & Roadmaps
- **[ROADMAP.md](planning/ROADMAP.md)** - Complete 20-phase implementation plan (Phases 0-18b)
- **[TODO.md](planning/TODO.md)** - Active tasks and implementation notes
- **[STATUS.md](planning/STATUS.md)** - Current project status and progress

### 📚 Reference Guides
- **[V5_MECHANICS.md](reference/V5_MECHANICS.md)** - Complete V5 game mechanics database (clans, disciplines, traits)
- **[THEMING.md](reference/THEMING.md)** - ANSI art and gothic aesthetics guide
- **[WEB_CHARGEN.md](reference/WEB_CHARGEN.md)** - Web-based character creation analysis

### 🛠️ Implementation Guides
- **[GIT_SETUP.md](guides/GIT_SETUP.md)** - Git configuration and workflow
- **[IMPORT_COMMAND_TEST.md](guides/IMPORT_COMMAND_TEST.md)** - Testing character import commands

### 📦 Archive
- **[V5_IMPLEMENTATION_ROADMAP_v1.md](archive/V5_IMPLEMENTATION_ROADMAP_v1.md)** - Original roadmap (superseded by planning/ROADMAP.md)

---

## Document Organization

### Planning Documents (`planning/`)
Strategic planning, roadmaps, and active task tracking. **Update these regularly** as the project progresses.

- **ROADMAP.md**: The authoritative implementation plan with 20 phases
- **TODO.md**: Active tasks, web chargen integration, Athens grid building
- **STATUS.md**: Project milestones and current state

### Reference Documents (`reference/`)
Static reference material for game mechanics and design. **Consult these during implementation**.

- **V5_MECHANICS.md**: Vampire game rules (attributes, skills, disciplines, clans, etc.)
- **THEMING.md**: Visual design standards (ANSI colors, ASCII art, borders)
- **WEB_CHARGEN.md**: Technical analysis of web character creation integration

### Implementation Guides (`guides/`)
How-to guides for specific tasks and workflows. **Follow these for standard procedures**.

- **GIT_SETUP.md**: Version control configuration
- **IMPORT_COMMAND_TEST.md**: Character import testing procedures

### Archive (`archive/`)
Obsolete documentation preserved for historical reference. **Do not use for active development**.

---

## Root Directory Files

**Project-Level Documentation** (in project root):
- `README.md` - Project introduction and quick start
- `CLAUDE.md` - Evennia framework guide and AI Quadrumvirate workflow
- `CHANGELOG.md` - Complete project history
- `SESSION_NOTES.md` - Most recent session details for context persistence

---

## Documentation Workflow

### When Starting a Session
1. Read `SESSION_NOTES.md` for context
2. Check recent `CHANGELOG.md` entries
3. Review `docs/planning/TODO.md` for active tasks
4. Check `docs/planning/STATUS.md` for current phase

### During Development
1. Follow `docs/planning/ROADMAP.md` phase structure
2. Reference `docs/reference/` guides as needed
3. Track progress with TodoWrite tool

### When Completing a Session
1. Update `CHANGELOG.md` with changes
2. Update `SESSION_NOTES.md` with most recent task
3. Update `docs/planning/STATUS.md` if phase progressed
4. Update `docs/planning/TODO.md` to reflect completed/new tasks

---

## Finding Information

**Need to...**

- **Understand the implementation plan?** → `planning/ROADMAP.md`
- **Know what to work on next?** → `planning/TODO.md`
- **Check project progress?** → `planning/STATUS.md`
- **Look up V5 game rules?** → `reference/V5_MECHANICS.md`
- **Apply consistent theming?** → `reference/THEMING.md`
- **Integrate web character creation?** → `reference/WEB_CHARGEN.md`
- **Set up git properly?** → `guides/GIT_SETUP.md`
- **Test import commands?** → `guides/IMPORT_COMMAND_TEST.md`
- **Understand Evennia framework?** → `../CLAUDE.md` (project root)

---

## Keeping Documentation Current

### Update Frequency

- **SESSION_NOTES.md**: After every session
- **CHANGELOG.md**: After every significant change
- **planning/TODO.md**: When tasks change (weekly minimum)
- **planning/STATUS.md**: When phases complete
- **planning/ROADMAP.md**: Rarely (only for major scope changes)
- **reference/**: Rarely (game mechanics are stable)
- **guides/**: As needed when procedures change

### Documentation Standards

- Use clear, descriptive headings
- Include file paths and line numbers for code references
- Keep examples concise and relevant
- Update cross-references when moving files
- Archive obsolete docs instead of deleting

---

## Contributing

When adding new documentation:
1. Place in appropriate directory
2. Update this README.md with link
3. Update SESSION_NOTES.md noting the addition
4. Commit with descriptive message

---

Last Updated: 2025-01-26
