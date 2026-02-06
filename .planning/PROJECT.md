# TheBeckoningMU Web Portal

## What This Is

A web portal for TheBeckoningMU, an Evennia-based Vampire: The Masquerade V5 MUD. The portal provides browser-based character creation (with staff approval workflow) and a visual grid builder (with approval, sandbox testing, and promotion to live). It replaces tedious text-only in-game commands with a proper UI for players and builders.

## Core Value

Players and builders can do the complex, multi-step tasks (character creation and area building) through an intuitive web interface instead of memorizing text commands.

## Current State (v1.0 Shipped)

**Shipped:** 2026-02-05  
**Milestone:** v1.0 Web Portal Foundation  
**See:** `.planning/milestones/v1.0-ROADMAP.md` for full details

### What's Working

- **Character Creation:** Full V5 character creation with clan, attributes, skills, disciplines, advantages, flaws
- **Character Approval:** Complete workflow with rejection feedback, background/backstory, auto-placement, in-game notifications
- **Grid Builder:** Visual editor with room creation, exit connections, V5 room settings
- **Builder Workflow:** State machine (draft→submitted→approved→built→live) with staff review
- **Sandbox Building:** Auto-creates Evennia rooms/exits in isolated test areas
- **Live Promotion:** Connects tested builds to the live game world at specified connection points
- **Trigger System:** Entry/exit/timed/interaction triggers with V5 conditions and web editor UI

### Tech Stack

- Evennia-based MUD running Python 3.13+ with Django 4.2+
- Web frontend uses vanilla JavaScript (ES6+), Bootstrap 5.1.3, Django templates -- no JS framework
- 36,723 lines of Python code
- 69 commits across 3 days

## Requirements

### Validated (v1.0)

**Character Creation (Existing + v1.0):**
- [x] **CHARGEN-01**: Player can create a V5 character via web form with clan, attributes, skills, disciplines, advantages, flaws
- [x] **CHARGEN-02**: Priority-based attribute/skill allocation with real-time dot tracking
- [x] **CHARGEN-03**: V5 rule validation (discipline dots, advantage points, flaw limits)
- [x] **CHARGEN-04**: Staff can view pending characters and approve/reject with notes
- [x] **CHAR-01**: Player can view rejection notes and edit/resubmit a rejected character without starting over — v1.0
- [x] **CHAR-02**: CharacterBio includes background text field for free-text backstory — v1.0
- [x] **CHAR-03**: Approved character is auto-placed in the starting room — v1.0
- [x] **CHAR-04**: Player receives in-game notification when character is approved or rejected — v1.0
- [x] **CHAR-05**: Player can save partial chargen progress and resume later — v1.0

**Builder System (Existing + v1.0):**
- [x] **BUILD-01**: Builder dashboard lists user's projects and public projects
- [x] **BUILD-02**: Visual grid editor with room creation, positioning, and properties
- [x] **BUILD-03**: Exit creation between rooms with SVG line visualization
- [x] **BUILD-04**: V5 room settings (location type, day/night access, danger level, hunting modifier, haven ratings)
- [x] **BUILD-05**: Export project as .ev batch script with sanitized input
- [x] **BUILD-06**: Save/load projects with JSON map data
- [x] **BLDX-01**: Compass rose overlay shows exit directions on room nodes — v1.0
- [x] **BLDX-02**: Exit auto-naming infers cardinal direction from grid position — v1.0
- [x] **BLDX-03**: V5 room template presets (Elysium, Haven, Rack, etc.) — v1.0
- [x] **BLDX-04**: Template dropdown in editor to apply preset — v1.0
- [x] **BLDX-05**: Map orientation indicator on canvas corner — v1.0
- [x] **BLDW-01**: BuildProject has explicit status field — v1.0
- [x] **BLDW-02**: Builder can submit project for staff review — v1.0
- [x] **BLDW-03**: Staff review interface with map preview — v1.0
- [x] **BLDW-04**: Auto-sandbox creates rooms/exits via Evennia API — v1.0
- [x] **BLDW-05**: Builder can walk through sandbox to test — v1.0
- [x] **BLDW-06**: Sandbox cleanup deletes all rooms/exits — v1.0
- [x] **BLDW-07**: Builder specifies connection point for live promotion — v1.0
- [x] **BLDW-08**: Promotion auto-links sandbox rooms into live world — v1.0

**Trigger System (v1.0):**
- [x] **TRIG-01**: Entry triggers fire when character enters room — v1.0
- [x] **TRIG-02**: Exit triggers fire when character leaves room — v1.0
- [x] **TRIG-03**: Timed triggers fire on configurable intervals — v1.0
- [x] **TRIG-04**: Interaction triggers fire on player actions — v1.0
- [x] **TRIG-05**: Trigger editor UI in web builder — v1.0
- [x] **TRIG-06**: V5-aware trigger conditions (hunger, clan, time-of-night) — v1.0
- [x] **TRIG-07**: Whitelisted trigger actions only — v1.0

**API (Existing + v1.0):**
- [x] **API-01**: Trait listing API (categories, traits by splat, discipline powers)
- [x] **API-02**: Character creation API (create, validate, import, export)
- [x] **API-03**: Character approval API (pending list, detail view, approve/reject)
- [x] **REVW-01**: Review character creation for V5 rule correctness — v1.0
- [x] **REVW-02**: Review grid builder for correctness — v1.0
- [x] **REVW-03**: Review API endpoints for security — v1.0

### Active (v2.0 Candidates)

- [ ] **CHAR-06**: Player-facing character sheet view on web (read-only)
- [ ] **CHAR-07**: Staff comments on specific traits during review
- [ ] **CHAR-08**: Approval history log (track all approve/reject actions across revisions)
- [ ] **BLDX-06**: Custom template creation and sharing between builders
- [ ] **BLDX-07**: Template inheritance (e.g., Dark Alley inherits from Street)
- [ ] **TRIG-08**: Custom trigger action development guide for developers

### Out of Scope

| Feature | Reason |
|---------|--------|
| Full web MUD client replacement | Web portal complements the telnet/webclient, not replaces it |
| Rich text/WYSIWYG room descriptions | MUDs use plain text; ANSI preview at most |
| Stat optimization assistant | Undermines V5 roleplaying spirit |
| Real-time collaborative building | Enormous complexity, minimal benefit for MU* building |
| Automated character approval | V5 characters require narrative review by staff |
| Free-form Python in triggers | Security risk; use whitelisted actions only |
| Mobile-specific responsive design | Desktop browser is primary target |
| Player dashboard (messages, notifications) | MUD client handles this |
| Game wiki/help system on web | In-game help is sufficient |
| Up/Down vertical exits in compass | 2D grid covers majority of use cases; can create manually |

## Context

- Evennia-based MUD running Python 3.13+ with Django 4.2+
- Web frontend uses vanilla JavaScript (ES6+), Bootstrap 5.1.3, Django templates -- no JS framework
- Builder stores map state as JSON blob in BuildProject.map_data
- Character creation uses traits Django app with TraitCategory, Trait, DisciplinePower models
- Thread-safe Django-to-Evennia bridge for sandbox building and promotion
- Whitelisted trigger actions prevent arbitrary code execution

## Constraints

- **Tech stack**: Must use existing Evennia/Django stack with vanilla JS frontend -- no new JS frameworks
- **Game system**: V5 (Vampire: The Masquerade 5th Edition) rules must be followed exactly
- **Evennia patterns**: Must use Evennia typeclass system, command patterns, and batch script format for sandbox/promotion
- **Builder access**: Players with builder permission + staff can use the builder; permission is grantable
- **Approval flow**: Both character creation and builder projects require staff approval before going live

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Vanilla JS over framework | Existing codebase uses no JS framework; consistency and simplicity | ✅ Good — maintained consistency, no framework bloat |
| Approval queue for builder (not immediate build) | Prevents griefing/mistakes; mirrors character approval pattern | ✅ Good — staff oversight prevents bad builds |
| Auto-connect on promotion (builder specifies connection point) | Reduces staff manual work; builder knows where their area should connect | ✅ Good — streamlined promotion workflow |
| V5 presets for templates (not full room definitions) | Simpler to implement; most room customization is in the editor itself | ✅ Good — templates provide quick starting points |
| All three trigger types in v1 | Entry/exit, timed, and interaction triggers are all needed for functional areas | ✅ Good — complete trigger system delivered |
| Thread-safe Django-to-Evennia bridge | Evennia runs in main thread; Django web requests need safe cross-thread communication | ✅ Good — reliable sandbox building and promotion |

## Technical Debt

- Up/Down (U/D) vertical exits not fully implemented — 8 horizontal directions work, vertical can be created manually
- Minor code duplication in scripts.py is_valid method
- In-clan discipline validation deferred (needs ClanDiscipline model)
- Python 3.14/cryptography incompatibility documented (requires Python 3.12/3.13)

## Next Milestone Goals (v2.0)

1. **Character Sheet Viewer** — Read-only web view of approved characters
2. **Staff Review Enhancements** — Trait-level comments, approval history log
3. **Custom Templates** — Builder-created templates with inheritance
4. **Trigger Documentation** — Developer guide for custom trigger actions

---

*Last updated: 2026-02-05 after v1.0 milestone completion*
