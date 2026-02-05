# Roadmap: TheBeckoningMU Web Portal

## Overview

This roadmap takes the existing Evennia-based web portal -- which already has working character creation, grid builder, and API endpoints -- from a functional prototype to a production-ready system. The journey starts with hardening existing code, then completes the character approval workflow, enhances the builder editor UX, builds the approval-to-sandbox-to-live pipeline for builder projects, and finishes with the trigger system for dynamic room behavior. Seven phases deliver 28 requirements across five functional areas.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Review & Hardening** - Verify and fix existing chargen, builder, and API code before building on it
- [x] **Phase 2: Character Approval Completion** - Players can submit, get rejected, revise, and get approved with full workflow
- [ ] **Phase 3: Builder UX** - Compass rose navigation and V5 room templates enhance the grid editor
- [ ] **Phase 4: Builder Approval Workflow** - Builders submit projects for staff review with state machine lifecycle
- [ ] **Phase 5: Sandbox Building** - Approved projects auto-build into isolated sandbox areas for testing
- [ ] **Phase 6: Live Promotion** - Tested sandbox builds connect into the live game world
- [ ] **Phase 7: Trigger System** - Rooms respond to events with entry/exit, timed, and interaction triggers

## Phase Details

### Phase 1: Review & Hardening
**Goal**: Existing chargen, builder, and API code is verified correct, secure, and reliable before new features build on it
**Depends on**: Nothing (first phase)
**Requirements**: REVW-01, REVW-02, REVW-03
**Success Criteria** (what must be TRUE):
  1. Character creation validates all V5 rules correctly -- no invalid character can be submitted, no valid character is rejected by validation
  2. Grid builder save/load round-trips perfectly -- saving a project and loading it produces identical map data with no data loss
  3. Builder export generates correct Evennia batch commands that match the visual map layout
  4. All API endpoints require authentication, use CSRF protection, and return proper error responses for invalid input
  5. No API endpoint allows unauthorized access to another user's data
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md -- Harden character creation API: remove CSRF exemptions, add auth checks, add V5 server-side pool validation
- [x] 01-02-PLAN.md -- Harden grid builder: remove CSRF exemptions, fix exporter injection, add concurrency control, improve validator
- [x] 01-03-PLAN.md -- Verify all hardening changes work end-to-end (automated checks + human smoke test)

### Phase 2: Character Approval Completion
**Goal**: Players experience a complete character creation lifecycle -- from first draft through rejection feedback to approval and entering the game
**Depends on**: Phase 1 (security fixes must land before adding approval features)
**Requirements**: CHAR-01, CHAR-02, CHAR-03, CHAR-04, CHAR-05
**Success Criteria** (what must be TRUE):
  1. Player whose character was rejected can see the rejection notes, edit their character, and resubmit without starting over
  2. Player can write a free-text background/backstory as part of character creation
  3. Approved character appears in the game's starting room -- player can immediately log in and play
  4. Player receives an in-game notification when their character is approved or rejected
  5. Player can save a partially completed character and return later to finish it
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md -- Model extension: add status/background/rejection fields to CharacterBio, migrate from boolean, refactor all call sites
- [x] 02-02-PLAN.md -- New API endpoints (my-characters, for-edit, resubmit), auto-placement, notification helpers, chargen command updates
- [x] 02-03-PLAN.md -- Frontend: approval UI rejection modal + background display; creation UI edit mode + background field + draft save/resume
- [x] 02-04-PLAN.md -- Run migration and end-to-end verification (automated checks + human smoke test of full lifecycle)

### Phase 3: Builder UX
**Goal**: Builders can orient their maps spatially and apply V5 room presets, making the grid editor faster and more intuitive
**Depends on**: Phase 1 (builder correctness fixes must land first)
**Requirements**: BLDX-01, BLDX-02, BLDX-03, BLDX-04, BLDX-05
**Success Criteria** (what must be TRUE):
  1. Builder can see compass direction labels (N/S/E/W/NE/NW/SE/SW/U/D) on exits between rooms
  2. Creating an exit between two rooms auto-assigns a cardinal direction name and aliases based on grid position
  3. Builder can apply a V5 room template (Elysium, Haven, Rack, etc.) to a room, and it pre-fills all V5 settings
  4. Map canvas shows a north/south/east/west orientation indicator so builders know which direction is which
**Plans**: TBD

Plans:
- [ ] 03-01: Compass rose and exit auto-naming
- [ ] 03-02: V5 room templates and template application

### Phase 4: Builder Approval Workflow
**Goal**: Builder projects follow a gated lifecycle -- draft to submitted to approved -- with staff review before anything gets built in-game
**Depends on**: Phase 1 (security fixes), Phase 3 is NOT required (approval workflow is independent of UX enhancements)
**Requirements**: BLDW-01, BLDW-02, BLDW-03
**Success Criteria** (what must be TRUE):
  1. BuildProject has an explicit status visible to the builder (Draft, Submitted, Approved, Built, Live) and only valid transitions are allowed
  2. Builder can submit a project for staff review from the builder dashboard
  3. Staff can view submitted projects with a map preview and approve or reject with notes
**Plans**: TBD

Plans:
- [ ] 04-01: State machine and submission/review workflow

### Phase 5: Sandbox Building
**Goal**: Approved builder projects automatically create real Evennia rooms and exits in an isolated sandbox area where builders can walk through and test their build
**Depends on**: Phase 4 (must have approval workflow -- only approved projects can be sandboxed)
**Requirements**: BLDW-04, BLDW-05, BLDW-06
**Success Criteria** (what must be TRUE):
  1. Approving a project and triggering sandbox build creates actual Evennia rooms and exits matching the web map layout
  2. Builder can connect via MUD client and walk through the sandbox rooms, testing exits and room descriptions
  3. Sandbox rooms are isolated -- regular players cannot accidentally reach them from the live game world
  4. Builder or staff can tear down a sandbox, cleanly deleting all rooms and exits created for that project
**Plans**: TBD

Plans:
- [ ] 05-01: Bridge layer and sandbox room/exit creation
- [ ] 05-02: Sandbox isolation, walkthrough, and cleanup

### Phase 6: Live Promotion
**Goal**: Builders can promote a tested sandbox build into the live game world, automatically connecting it at a specified point
**Depends on**: Phase 5 (must have sandbox to promote from)
**Requirements**: BLDW-07, BLDW-08
**Success Criteria** (what must be TRUE):
  1. Builder can specify which existing live room their build should connect to and which direction
  2. Promoting a build moves rooms from sandbox into the live world with all exits correctly re-mapped
  3. Players in the live game world can walk into the promoted area through the connection point
  4. After successful promotion, sandbox copies are cleaned up
**Plans**: TBD

Plans:
- [ ] 06-01: Connection point selection and promotion engine

### Phase 7: Trigger System
**Goal**: Builders can add dynamic behavior to rooms -- atmospheric messages on entry, timed weather events, and responses to player actions -- all through the web editor
**Depends on**: Phase 5 (triggers are created during sandbox building; trigger scripts need the bridge layer)
**Requirements**: TRIG-01, TRIG-02, TRIG-03, TRIG-04, TRIG-05, TRIG-06, TRIG-07
**Success Criteria** (what must be TRUE):
  1. When a character enters a room with an entry trigger, the trigger fires (e.g., atmospheric message appears)
  2. When a character leaves a room with an exit trigger, the trigger fires (e.g., tracking notification)
  3. Timed triggers fire on their configured interval (e.g., weather message every 5 minutes)
  4. Interaction triggers fire when a player performs a specific action in the room (e.g., looking at a specific object)
  5. Builder can create and configure triggers through the web editor UI with type selector, conditions, and actions
  6. Trigger conditions can reference V5 game state (hunger level, clan, time-of-night, danger level)
  7. Only whitelisted trigger actions are available -- no arbitrary code execution is possible
**Plans**: TBD

Plans:
- [ ] 07-01: Entry/exit trigger engine and room hooks
- [ ] 07-02: Timed triggers via Evennia Scripts
- [ ] 07-03: Interaction triggers, V5 conditions, and trigger editor UI

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7
Note: Phase 3 (Builder UX) can run in parallel with Phase 2 (Character Approval) since they are independent.

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. Review & Hardening | 3/3 | Complete | 2026-02-03 |
| 2. Character Approval Completion | 4/4 | Complete | 2026-02-05 |
| 3. Builder UX | 0/2 | Not started | - |
| 4. Builder Approval Workflow | 0/1 | Not started | - |
| 5. Sandbox Building | 0/2 | Not started | - |
| 6. Live Promotion | 0/1 | Not started | - |
| 7. Trigger System | 0/3 | Not started | - |
