# Project Milestones: TheBeckoningMU Web Portal

## v1.0 Web Portal Foundation (Shipped: 2026-02-05)

**Delivered:** A production-ready web portal for Evennia-based Vampire: The Masquerade V5 MUD with character creation/approval workflow, visual grid builder with approval-to-sandbox-to-live pipeline, and dynamic room trigger system.

**Phases completed:** 1-7 (16 plans total)

**Key accomplishments:**

- Hardened existing character creation and grid builder with CSRF protection, auth checks, and V5 validation
- Built complete character approval workflow with rejection feedback, background/backstory, auto-placement, and in-game notifications
- Enhanced builder UX with compass rose navigation, exit auto-naming, and V5 room template presets
- Implemented builder approval workflow with state machine (draft→submitted→approved→built→live) and staff review interface
- Created sandbox building system that auto-creates Evennia rooms/exits in isolated test areas
- Built live promotion engine that connects tested sandbox builds to the live game world
- Delivered complete trigger system with entry/exit/timed/interaction triggers, V5 conditions, and web editor UI

**Stats:**

- 69 commits from 2026-02-03 to 2026-02-05
- 36,723 lines of Python code
- 7 phases, 16 plans, ~50 tasks
- 3 days from first commit to ship

**Git range:** `feat(01-01)` → `feat(07-03)`

**What's next:** v2.0 features including character sheet viewer, custom templates, approval history log

---

*For milestone details, see `.planning/milestones/v1.0-ROADMAP.md`*
