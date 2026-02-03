# External Integrations

**Analysis Date:** 2026-02-03

## APIs & External Services

**Third-party APIs:**
- None detected - Not currently integrated with external APIs

**Internal API Endpoints:**
- `/api/traits/` - REST API for traits management system
  - Location: `beckonmu/traits/urls.py` and `beckonmu/traits/` endpoints
  - Purpose: Serves trait data for web-based systems and character builders

## Data Storage

**Databases:**
- SQLite (default) or PostgreSQL (configurable)
  - Connection: Via Django database settings in `beckonmu/server/conf/settings.py`
  - Client: Django ORM (built-in)
  - Models location: `beckonmu/bbs/models.py`, `beckonmu/jobs/models.py`, `beckonmu/traits/models.py`, `beckonmu/status/models.py`, `beckonmu/boons/models.py`, `beckonmu/web/builder/models.py`

**File Storage:**
- Local filesystem only
  - Map data stored as JSONField in `BuildProject.map_data` (`beckonmu/web/builder/models.py`)
  - Batch scripts exported to filesystem via `beckonmu/web/builder/exporter.py`

**Caching:**
- Django default cache system (in-memory or database)
- Evennia attribute caching system (persistent `obj.db.*` and non-persistent `obj.ndb.*`)

## Authentication & Identity

**Auth Provider:**
- Custom Django authentication (built-in to Evennia)
  - Implementation: Django user/account system
  - Account creation via web character creation interface
  - Account typeclass: `beckonmu/typeclasses/accounts.py` (extends Evennia `DefaultAccount`)
  - Staff permissions via Django user.is_staff flag

**Web Authentication:**
- Django session-based authentication
- LoginRequiredMixin on staff-only views in `beckonmu/web/builder/views.py`
- CSRF protection enabled by default (exempted only where needed with @csrf_exempt)

## Monitoring & Observability

**Error Tracking:**
- None detected - Standard Django/Evennia logging

**Logs:**
- Evennia server logs (console output during development)
- Django application logs via Python logging
- Server logs location: `server/logs/` (created at runtime)

## CI/CD & Deployment

**Hosting:**
- Not configured - Designed for local/manual deployment
- Development: Local machine (evennia start/stop commands)
- Production-ready but not configured with specific hosting platform

**CI Pipeline:**
- None configured - No GitHub Actions or other CI/CD detected

**Deployment:**
- Manual via evennia commands
- PowerShell helper scripts for Windows: `start-evennia.ps1`, `stop-evennia.ps1`, `reload-evennia.ps1`

## Environment Configuration

**Required env vars:**
- Not detected as strictly required - Most settings in `beckonmu/server/conf/settings.py`
- Secret settings can be added via `beckonmu/server/conf/secret_settings.py` (not in repo)
- Database configuration via Django DATABASES setting (defaults to SQLite)

**Secrets location:**
- `beckonmu/server/conf/secret_settings.py` - Not committed to repo (git-ignored)
- Pattern: Import and override settings from this file if it exists

## Webhooks & Callbacks

**Incoming:**
- None detected - No webhook endpoints

**Outgoing:**
- None detected - No external service callbacks or event publishing

## Game Integration Points

**Evennia Server Integration:**
- Server startup hooks: `beckonmu/server/conf/at_server_startstop.py`
- Connection screen customization: `beckonmu/server/conf/connection_screens.py`
- Command parsing customization: `beckonmu/server/conf/cmdhandler.py`
- Lock functions: `beckonmu/server/conf/lockfuncs.py`

**Web Interface Integration:**
- Web builder exports to in-game batch scripts via `beckonmu/web/builder/exporter.py`
- Sandbox room integration: BuildProject.sandbox_room_id stores link to in-game test area
- Staff character approval: Web interface linked to account/character creation

## Data Models and Database Schema

**BBS (Bulletin Board System):**
- Models: `beckonmu/bbs/models.py`
- Board, Post, Comment models with IC/OOC classification

**Jobs System:**
- Models: `beckonmu/jobs/models.py`
- Bucket, Job, Comment, Tag models with status tracking

**Status System:**
- Models: `beckonmu/status/models.py`
- Character status and condition tracking

**Boons System:**
- Models: `beckonmu/boons/models.py`
- V5 vampire boons and benefits

**Traits System:**
- Models: `beckonmu/traits/models.py`
- V5 vampire attributes, skills, merits, etc.

**Web Builder:**
- Models: `beckonmu/web/builder/models.py`
- BuildProject (stores map_data as JSONField), RoomTemplate

## Web Interface Components

**Views:**
- `beckonmu/web/builder/views.py` - Builder dashboard, editor, project save/load
- `beckonmu/web/website/views/` - Public website views
- Admin views via `beckonmu/web/admin/urls.py`

**API Views:**
- Traits API endpoints in `beckonmu/web/api/urls.py`
- Project management endpoints in builder views (SaveProjectView, LoadProjectView, etc.)

---

*Integration audit: 2026-02-03*
