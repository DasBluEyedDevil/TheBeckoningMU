# TheBeckoningMU Web Portal

## What This Is

A web portal for TheBeckoningMU, an Evennia-based Vampire: The Masquerade V5 MUD. The portal provides browser-based character creation (with staff approval workflow) and a visual grid builder (with approval, sandbox testing, and promotion to live). It replaces tedious text-only in-game commands with a proper UI for players and builders.

## Core Value

Players and builders can do the complex, multi-step tasks (character creation and area building) through an intuitive web interface instead of memorizing text commands.

## Requirements

### Validated

- [x] **CHARGEN-01**: Player can create a V5 character via web form with clan, attributes, skills, disciplines, advantages, flaws -- existing
- [x] **CHARGEN-02**: Priority-based attribute/skill allocation with real-time dot tracking -- existing
- [x] **CHARGEN-03**: V5 rule validation (discipline dots, advantage points, flaw limits) -- existing
- [x] **CHARGEN-04**: Staff can view pending characters and approve/reject with notes -- existing
- [x] **BUILD-01**: Builder dashboard lists user's projects and public projects -- existing
- [x] **BUILD-02**: Visual grid editor with room creation, positioning, and properties -- existing
- [x] **BUILD-03**: Exit creation between rooms with SVG line visualization -- existing
- [x] **BUILD-04**: V5 room settings (location type, day/night access, danger level, hunting modifier, haven ratings) -- existing
- [x] **BUILD-05**: Export project as .ev batch script with sanitized input -- existing
- [x] **BUILD-06**: Save/load projects with JSON map data -- existing
- [x] **API-01**: Trait listing API (categories, traits by splat, discipline powers) -- existing
- [x] **API-02**: Character creation API (create, validate, import, export) -- existing
- [x] **API-03**: Character approval API (pending list, detail view, approve/reject) -- existing

### Active

- [ ] **REVIEW-01**: Review character creation system for correctness (validation rules, edge cases, data integrity)
- [ ] **REVIEW-02**: Review grid builder for correctness (save/load, export accuracy, UI behavior)
- [ ] **REVIEW-03**: Review API endpoints for security and error handling
- [ ] **BUILD-07**: Approval workflow for builder projects (submit for review, staff approves, builds to sandbox)
- [ ] **BUILD-08**: Auto-sandbox building (approved project creates rooms/exits in sandbox area automatically)
- [ ] **BUILD-09**: Auto-promotion (builder specifies connection point, promotion links sandbox rooms into live game world)
- [ ] **BUILD-10**: Room templates as V5 presets (haven, elysium, rack, etc.) that pre-fill V5 settings
- [ ] **BUILD-11**: Trigger system -- entry/exit triggers (run script on room enter/leave)
- [ ] **BUILD-12**: Trigger system -- timed triggers (periodic events: weather, ambient messages)
- [ ] **BUILD-13**: Trigger system -- interaction triggers (player actions: look at object, use item)
- [ ] **BUILD-14**: Compass rose -- assign cardinal directions (N/S/E/W/NE/NW/SE/SW/U/D) to exits visually
- [ ] **BUILD-15**: Compass rose -- orient/rotate grid map for spatial consistency

### Out of Scope

- Character sheet viewer/editor via web -- focus on creation flow only for this milestone
- Player dashboard (messages, notifications) -- MUD client handles this
- Game wiki/help system on web -- in-game help is sufficient
- Mobile-specific responsive design -- desktop browser is primary target
- Real-time collaborative building -- single-user editing per project

## Context

- Evennia-based MUD running Python 3.13+ with Django 4.2+
- Web frontend uses vanilla JavaScript (ES6+), Bootstrap 5.1.3, Django templates -- no JS framework
- Builder stores map state as JSON blob in BuildProject.map_data
- Existing exporter.py converts map data to Evennia batch commands with input sanitization
- Character creation uses traits Django app with TraitCategory, Trait, DisciplinePower models
- Builder has partial stubs for triggers (UI skeleton, "Phase 5" label), templates (model exists, API returns 501), compass rose (mode button exists, no functionality)
- Builder permission model: BuildProject.user = creator, is_public flag for sharing

## Constraints

- **Tech stack**: Must use existing Evennia/Django stack with vanilla JS frontend -- no new JS frameworks
- **Game system**: V5 (Vampire: The Masquerade 5th Edition) rules must be followed exactly
- **Evennia patterns**: Must use Evennia typeclass system, command patterns, and batch script format for sandbox/promotion
- **Builder access**: Players with builder permission + staff can use the builder; permission is grantable
- **Approval flow**: Both character creation and builder projects require staff approval before going live

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vanilla JS over framework | Existing codebase uses no JS framework; consistency and simplicity | -- Pending |
| Approval queue for builder (not immediate build) | Prevents griefing/mistakes; mirrors character approval pattern | -- Pending |
| Auto-connect on promotion (builder specifies connection point) | Reduces staff manual work; builder knows where their area should connect | -- Pending |
| V5 presets for templates (not full room definitions) | Simpler to implement; most room customization is in the editor itself | -- Pending |
| All three trigger types in v1 | Entry/exit, timed, and interaction triggers are all needed for functional areas | -- Pending |

---
*Last updated: 2026-02-03 after initialization*
