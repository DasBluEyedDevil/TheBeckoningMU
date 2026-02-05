# Requirements: TheBeckoningMU Web Portal

**Defined:** 2026-02-03
**Core Value:** Players and builders can do complex, multi-step tasks (character creation and area building) through an intuitive web interface instead of memorizing text commands.

## v1 Requirements

### Review & Hardening

- [x] **REVW-01**: Review character creation for V5 rule correctness (validation rules, edge cases, data integrity)
- [x] **REVW-02**: Review grid builder for correctness (save/load, export accuracy, UI behavior)
- [x] **REVW-03**: Review API endpoints for security (fix csrf_exempt, add concurrency controls, verify auth checks)

### Character Creation & Approval

- [x] **CHAR-01**: Player can view rejection notes and edit/resubmit a rejected character without starting over
- [x] **CHAR-02**: CharacterBio includes background text field for free-text backstory
- [x] **CHAR-03**: Approved character is auto-placed in the starting room
- [x] **CHAR-04**: Player receives in-game notification when character is approved or rejected
- [x] **CHAR-05**: Player can save partial chargen progress and resume later (draft save/resume)

### Builder UX

- [x] **BLDX-01**: Compass rose overlay shows exit directions (N/S/E/W/NE/NW/SE/SW/U/D) on room nodes
- [x] **BLDX-02**: Exit auto-naming infers cardinal direction from grid position and sets exit name + aliases
- [x] **BLDX-03**: V5 room template presets (Elysium, Haven, Rack, etc.) that pre-fill V5 settings
- [x] **BLDX-04**: Template dropdown in editor to apply preset to new or existing room
- [x] **BLDX-05**: Map orientation indicator (N/S/E/W labels) on canvas corner

### Builder Workflow

- [x] **BLDW-01**: BuildProject has explicit status field (Draft, Submitted, Approved, Built, Live)
- [x] **BLDW-02**: Builder can submit project for staff review
- [x] **BLDW-03**: Staff review interface for builds (map preview + approve/reject with notes)
- [x] **BLDW-04**: Auto-sandbox creates rooms/exits in isolated sandbox area via Evennia API (not batch file)
- [x] **BLDW-05**: Builder can walk through sandbox to test their build in-game
- [x] **BLDW-06**: Sandbox cleanup deletes all sandbox rooms/exits tagged to a project
- [ ] **BLDW-07**: Builder specifies connection point for live promotion
- [ ] **BLDW-08**: Promotion auto-links sandbox rooms into the live game world at the specified connection point

### Triggers

- [ ] **TRIG-01**: Entry triggers fire when a character enters a room (atmospheric messages, danger notifications)
- [ ] **TRIG-02**: Exit triggers fire when a character leaves a room (tracking, narrative messages)
- [ ] **TRIG-03**: Timed triggers fire on configurable intervals (weather, ambient messages, respawning)
- [ ] **TRIG-04**: Interaction triggers fire on specific player actions in a room (look at object, use item)
- [ ] **TRIG-05**: Trigger editor UI in web builder (type selector, condition editor, action editor)
- [ ] **TRIG-06**: V5-aware trigger conditions (hunger level, clan, time-of-night, danger level)
- [ ] **TRIG-07**: Whitelisted trigger actions only (no arbitrary code execution)

## v2 Requirements

### Character Creation

- **CHAR-06**: Player-facing character sheet view on web (read-only)
- **CHAR-07**: Staff comments on specific traits during review
- **CHAR-08**: Approval history log (track all approve/reject actions across revisions)

### Builder

- **BLDX-06**: Custom template creation and sharing between builders
- **BLDX-07**: Template inheritance (e.g., Dark Alley inherits from Street)

### Triggers

- **TRIG-08**: Custom trigger action development guide for developers

## Out of Scope

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

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| REVW-01 | Phase 1: Review & Hardening | Complete |
| REVW-02 | Phase 1: Review & Hardening | Complete |
| REVW-03 | Phase 1: Review & Hardening | Complete |
| CHAR-01 | Phase 2: Character Approval Completion | Complete |
| CHAR-02 | Phase 2: Character Approval Completion | Complete |
| CHAR-03 | Phase 2: Character Approval Completion | Complete |
| CHAR-04 | Phase 2: Character Approval Completion | Complete |
| CHAR-05 | Phase 2: Character Approval Completion | Complete |
| BLDX-01 | Phase 3: Builder UX | Complete |
| BLDX-02 | Phase 3: Builder UX | Complete |
| BLDX-03 | Phase 3: Builder UX | Complete |
| BLDX-04 | Phase 3: Builder UX | Complete |
| BLDX-05 | Phase 3: Builder UX | Complete |
| BLDW-01 | Phase 4: Builder Approval Workflow | Complete |
| BLDW-02 | Phase 4: Builder Approval Workflow | Complete |
| BLDW-03 | Phase 4: Builder Approval Workflow | Complete |
| BLDW-04 | Phase 5: Sandbox Building | Complete |
| BLDW-05 | Phase 5: Sandbox Building | Complete |
| BLDW-06 | Phase 5: Sandbox Building | Complete |
| BLDW-07 | Phase 6: Live Promotion | Pending |
| BLDW-08 | Phase 6: Live Promotion | Pending |
| TRIG-01 | Phase 7: Trigger System | Pending |
| TRIG-02 | Phase 7: Trigger System | Pending |
| TRIG-03 | Phase 7: Trigger System | Pending |
| TRIG-04 | Phase 7: Trigger System | Pending |
| TRIG-05 | Phase 7: Trigger System | Pending |
| TRIG-06 | Phase 7: Trigger System | Pending |
| TRIG-07 | Phase 7: Trigger System | Pending |

**Coverage:**
- v1 requirements: 28 total
- Mapped to phases: 28
- Unmapped: 0

---
*Requirements defined: 2026-02-03*
*Last updated: 2026-02-05 after Phase 5 completion*
