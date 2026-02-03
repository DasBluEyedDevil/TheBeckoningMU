# Technology Stack

**Analysis Date:** 2026-02-03

## Languages

**Primary:**
- Python 3.13+ - Core server and game logic
- JavaScript/HTML/CSS - Web client and builder frontend
- SQL - Database queries via Django ORM

## Runtime

**Environment:**
- Python 3.13+ (tested with Python 3.14.2)
- Virtual environment in-project: `.venv/` directory

**Package Manager:**
- Poetry 1.8.0
- Lockfile: `poetry.lock` (present, minimal dependencies - only python ^3.13)

## Frameworks

**Core:**
- Evennia (installed via venv, not in pyproject.toml) - Python MUD framework and server
- Django 4.2+ (via Evennia) - Web framework for web interface and admin

**Web/Frontend:**
- Django Templates - Server-side HTML rendering
- Django REST Framework (via Evennia) - API endpoints
- Bootstrap (implied from web templates) - CSS framework

**Testing:**
- Evennia test runner - Built into evennia test command
- Django TestCase - Database testing

**Build/Dev:**
- Poetry - Dependency management (currently minimal usage)

## Key Dependencies

**Critical:**
- Evennia - Multiplayer text-based game framework (provides MUD server, Django integration, typeclasses)

**Infrastructure:**
- Django - Web framework for web interface, admin panel, APIs
- SQLite (default) or PostgreSQL (configurable) - Database backend via Django ORM

## Configuration

**Environment:**
- Configuration in `beckonmu/server/conf/settings.py` - Evennia settings override
- Secret settings: `beckonmu/server/conf/secret_settings.py` (not in repo, git-ignored)
- Default Evennia settings provide base configuration

**Build:**
- `pyproject.toml` - Poetry project manifest (minimal, only Python version constraint)
- `.venv/` - Virtual environment (in-project per poetry.toml)

## Platform Requirements

**Development:**
- Windows (PowerShell helper scripts for start/stop/reload: `start-evennia.ps1`, `stop-evennia.ps1`, `reload-evennia.ps1`)
- Any OS with Python 3.13+ (Unix/Linux/macOS also supported by Evennia)

**Production:**
- Any OS supporting Python 3.13+ and Evennia
- SQLite (default) or PostgreSQL database
- Port 4000 for MUD telnet interface
- Port 4001 for web interface

## Custom Django Apps

Installed as custom apps in `INSTALLED_APPS` in `beckonmu/server/conf/settings.py`:

- `beckonmu.bbs` - Bulletin board system (IC/OOC posts)
- `beckonmu.jobs` - Job/ticket system with buckets and comments
- `beckonmu.status` - Character status tracking
- `beckonmu.boons` - Vampire V5 boons system
- `beckonmu.traits` - Vampire V5 traits system
- `beckonmu.web.builder` - Web-based visual map builder for areas/zones
- `beckonmu.dice` - Dice rolling and rouse checks system

## Web Components

**Web Server:**
- Evennia's built-in Django web server (development mode)
- Production should use proper WSGI server (Gunicorn, uWSGI, etc.)

**Web Endpoints:**
- `/` - Public website
- `/webclient/` - Web-based MUD client
- `/admin/` - Django admin interface
- `/api/` - REST API (traits endpoints)
- `/builder/` - Web-based map builder for staff
- `/character-creation/` - Character creation flow
- `/staff/character-approval/` - Staff character approval interface

## Data Storage

**Database:**
- Default: SQLite (file-based, in `server/` directory)
- Configurable: PostgreSQL via Django settings
- ORM: Django ORM (Evennia wraps Evennia-specific models)
- Migrations: Django migrations system in each app's `migrations/` directory

**Session/Cache:**
- Django default cache (in-memory or database)
- Evennia attribute storage system (`obj.db.*` and `obj.ndb.*`)

## File Structure Relevant to Tech Stack

- `beckonmu/server/conf/settings.py` - Main configuration
- `beckonmu/server/conf/secret_settings.py` - Secrets (not in repo)
- `beckonmu/web/` - Web interface code
- `beckonmu/typeclasses/` - Evennia game entity definitions
- `beckonmu/commands/` - Game command implementations
- `beckonmu/world/` - Game data and logic
- `beckonmu/bbs/`, `beckonmu/jobs/`, etc. - Custom Django apps
- `.venv/` - Virtual environment with Evennia and dependencies

---

*Stack analysis: 2026-02-03*
