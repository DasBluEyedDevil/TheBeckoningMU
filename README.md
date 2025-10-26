# TheBeckoningMU

A Vampire: The Masquerade 5th Edition MUSH built on the Evennia framework.

---

## Quick Start

### Running the Server

```bash
evennia start     # Start server
evennia stop      # Stop server
evennia reload    # Apply code changes (fast)
evennia test      # Run tests
```

**Server Access**:
- MUD client: `localhost:4000`
- Web client: `http://localhost:4001`
- Admin panel: `http://localhost:4001/admin`

---

## Documentation

### For Developers

- **[CLAUDE.md](CLAUDE.md)** - Evennia framework guide and AI development workflow
- **[docs/](docs/)** - Complete documentation index

### Key Documents

- **[docs/planning/ROADMAP.md](docs/planning/ROADMAP.md)** - 20-phase implementation plan
- **[docs/planning/TODO.md](docs/planning/TODO.md)** - Active tasks
- **[docs/reference/V5_MECHANICS.md](docs/reference/V5_MECHANICS.md)** - Game mechanics reference
- **[CHANGELOG.md](CHANGELOG.md)** - Project history
- **[SESSION_NOTES.md](SESSION_NOTES.md)** - Most recent session context

---

## Project Overview

TheBeckoningMU is a modern MUSH (Multi-User Shared Hallucination) implementing Vampire: The Masquerade 5th Edition mechanics with:

- **Complete V5 Systems**: Hunger, Blood Potency, Disciplines, Clans, Resonance
- **MUSH Infrastructure**: BBS, Jobs, Help system, Status tracking
- **Modern Development**: Test-driven, modular architecture, AI-assisted workflows
- **Professional Theming**: Gothic ANSI art and atmospheric presentation

---

## Technology Stack

- **Framework**: [Evennia](https://www.evennia.com/) (Python MUD framework)
- **Language**: Python 3.13+
- **Package Management**: Poetry
- **Database**: SQLite3 (default) / configurable
- **Web Interface**: Django-based
- **Version Control**: Git

---

## Development Status

**Current Phase**: Documentation Organization Complete

See [docs/planning/STATUS.md](docs/planning/STATUS.md) for detailed progress.

---

## Project Structure

```
TheBeckoningMU/
├── README.md              # This file
├── CLAUDE.md              # Developer guide (Evennia + AI workflow)
├── CHANGELOG.md           # Project history
├── SESSION_NOTES.md       # Recent work context
├── docs/                  # Organized documentation
│   ├── planning/          # Roadmaps, TODO, status
│   ├── reference/         # Game mechanics, theming
│   ├── guides/            # How-to guides
│   └── archive/           # Obsolete docs
├── .skills/               # AI development skills
├── beckonmu/              # Evennia game directory
│   ├── commands/          # Command definitions
│   ├── typeclasses/       # Game entity classes
│   ├── world/             # Game data and logic
│   ├── web/               # Web interface
│   └── server/conf/       # Configuration
└── reference repo/        # Reference implementation (read-only)
```

---

## Development Workflow

This project uses the **AI Quadrumvirate** pattern for token-efficient development:

1. **Claude Code** - Orchestrator and decision-maker
2. **Gemini CLI** - Unlimited-context code analyst
3. **Cursor CLI** - UI/visual developer
4. **Copilot CLI** - Backend developer

See [CLAUDE.md](CLAUDE.md) for complete workflow details.

---

## Contributing

### Before Starting Work
1. Review [SESSION_NOTES.md](SESSION_NOTES.md) for context
2. Check [docs/planning/TODO.md](docs/planning/TODO.md) for active tasks
3. Follow the [docs/planning/ROADMAP.md](docs/planning/ROADMAP.md) phase structure

### After Completing Work
1. Update [CHANGELOG.md](CHANGELOG.md)
2. Update [SESSION_NOTES.md](SESSION_NOTES.md)
3. Commit with descriptive messages

### Development Standards
- Follow strict phase ordering (no skipping ahead)
- Test-driven development (TDD) is mandatory
- Small, focused commits
- Reference file paths with line numbers in commits

---

## Resources

- **Evennia Documentation**: https://www.evennia.com/docs/latest/
- **V5 Core Rulebook**: Official Vampire: The Masquerade 5th Edition
- **Project Documentation**: [docs/README.md](docs/README.md)

---

## License

(Add license information here)

---

## Contact

(Add contact information here)

---

**Last Updated**: 2025-01-26
