# Project Research Summary

**Project:** TheBeckoningMU Web Portal (Character Creation + Grid Builder + Approval Workflows)
**Domain:** Evennia-based MUD web portal system with V5 Vampire theming
**Researched:** 2026-02-03
**Confidence:** HIGH

## Executive Summary

TheBeckoningMU is building a web-based administration portal for a Vampire: The Masquerade V5 MUD that integrates with an existing Evennia 5.0.1 framework. The research reveals this is a unique intersection of three domains: (1) traditional MUD builder tools (grid-based room editing, exit management), (2) tabletop RPG character sheet management (V5 ruleset enforcement, approval workflows), and (3) modern web development patterns (server-driven UI with htmx, progressive enhancement). The existing codebase has strong foundations—a working visual grid builder, comprehensive V5 character creation, and API-driven architecture—but lacks critical workflow features (sandbox testing, live promotion, trigger systems) and has significant technical debt (CSRF protection disabled, no concurrency controls, thread-unsafe object creation patterns).

The recommended approach is to build iteratively through five distinct phases: (1) complete the character approval workflow gaps, (2) add builder approval queues with state machines, (3) implement sandbox-to-live promotion using direct Evennia API calls, (4) build the trigger system with whitelisted actions, and (5) add compass rose UI enhancements. The stack should remain minimal—htmx 2.0.8 for server-driven updates, Alpine.js 3.15.3 for local UI state, Bootstrap 5.3.8 upgrade for dark mode, django-fsm-2 4.1.0 for approval state machines, and django-htmx 1.27.0 for request detection—avoiding the complexity of React/Vue or build toolchains entirely.

The critical risks are thread-unsafe object creation (creating Evennia game objects from Django views requires `run_in_main_thread()`), JSON map data race conditions (two staff members editing the same project can silently overwrite changes), and trigger system code injection (allowing arbitrary Python execution through triggers). All three are preventable with documented patterns: service layer wrapping all Evennia API calls, optimistic concurrency control with version fields, and whitelisted trigger actions instead of expression evaluation.

## Key Findings

### Recommended Stack

The existing stack (Python 3.13, Evennia 5.0.1, Django 5.2.7, Bootstrap 5.1.3, vanilla JavaScript) is fundamentally sound and should not be replaced. The recommended additions enhance what exists rather than requiring rewrites.

**Core technologies:**
- **htmx 2.0.8**: Server-driven partial page updates via HTML attributes—replaces hand-rolled fetch() calls in approval workflows without requiring framework migration. Zero build step.
- **django-htmx 1.27.0**: Middleware for detecting htmx requests, enables views to return full pages OR fragments conditionally. Critical for progressive enhancement pattern.
- **django-fsm-2 4.1.0**: Finite state machine for approval workflows (draft → submitted → approved → sandboxed → promoted). Prevents invalid state transitions that the current boolean flags cannot enforce.
- **Alpine.js 3.15.3**: Lightweight reactive UI for builder editor interactions (compass rose, trigger editor, room template picker). Complements htmx by handling local client state.
- **Bootstrap 5.3.8 (upgrade)**: Adds native dark mode support via `data-bs-theme="dark"` to replace custom dark theme CSS. Minimal migration risk (5.1 → 5.3 is minor version bump).

**Explicitly rejected alternatives:**
- React/Vue/Svelte: Would require rewriting 2,300+ lines of existing template HTML and adding a build step. The project has no node_modules and no bundler—htmx + Alpine achieve the same goals without the complexity.
- Tailwind CSS: Requires PostCSS build step and rewriting all Bootstrap-based templates.
- GraphQL: Overkill for 15 API endpoints. REST + htmx partials is simpler.
- Celery task queue: Sandbox building via Evennia's batch processor executes fast enough synchronously. Premature optimization.

### Expected Features

Research identified a clear split between table stakes (features users expect) and differentiators (features that distinguish this from competitors like AresMUSH).

**Must have (table stakes):**
- **Rejection resubmission flow**: Players can view rejection notes and edit rejected characters without starting over. Currently missing—rejected players must start from scratch. Every WoD MU has this.
- **Background text field**: Free-text backstory beyond mechanical stats. WoD MUs universally require written backgrounds for narrative review. Currently only concept/ambition/desire fields exist.
- **Character location assignment on approval**: Approved characters need to be placed in the starting room. Currently creates characters with `location=None`.
- **In-game notifications**: Players should be notified when characters are approved/rejected. Currently no notification mechanism exists.
- **Build approval workflow**: Non-admin builders submit builds for staff review before sandbox/promotion. Currently any staff can build directly with no gating.
- **Auto-sandbox**: Build project to isolated in-game area for testing. Currently returns "manual_required"—no automatic execution exists.
- **Promotion to live grid**: Move approved sandbox builds to main game world. Currently `promoted_at` field exists but no promotion logic.

**Should have (competitive):**
- **V5 room template presets**: One-click room creation with correct V5 attributes (Elysium, Haven, Rack). Model exists, implementation is 501. Genuine differentiator—no other Evennia game has pre-configured WoD room templates.
- **Room trigger system**: Entry/exit/timed/interaction triggers configured via web UI with V5-aware conditions (hunger level, clan check). MUSH/MUX precedent is strong (@aenter, @aleave), but web-based configuration is novel.
- **Compass rose for exits**: Direction-aware exit creation with auto-naming (spatial relationship determines "north"/"south"). Standard in MUD map editors (Mudlet Mapper, MUD Map Builder) but not in Evennia web builders.
- **Draft save/resume for chargen**: Players can save partial character sheets and return later. AresMUSH supports this; current implementation is all-or-nothing.

**Defer (v2+):**
- Template inheritance (room templates inheriting from other templates)
- Approval history log (multiple revision cycles)
- Staff comments on specific traits
- Interaction triggers (more complex than entry/exit/timed)

### Architecture Approach

The fundamental architectural challenge is bridging Django web state with Evennia game state. The existing pattern—`BuildProject.map_data` stores JSON, `exporter.py` generates batch scripts—works but is limited because Evennia's batch command processor has no Python API for programmatic execution (requires in-game session).

**Major components:**
1. **Bridge Layer** (`builder/sandbox_builder.py`) — Converts web map data to Evennia objects using `evennia.create_object()` directly (not batch scripts). Wraps all calls in `run_in_main_thread()` to avoid thread-unsafe object creation. Responsible for sandbox creation, promotion, and teardown.
2. **State Machine Layer** (django-fsm-2 on `BuildProject` and `CharacterBio`) — Enforces valid state transitions for approval workflows. Prevents impossible states (approved AND rejected, sandboxed without approval, promoted without sandbox).
3. **Trigger System** (hybrid approach) — Room attributes for synchronous triggers (entry/exit checked in `at_object_receive` hook), Evennia Scripts for asynchronous triggers (timed interval-based execution). Whitelisted actions only—no eval/exec.
4. **Approval Queue UI** (mirrors existing character approval) — Reuses the pattern from `character_approval.html` and `traits/api.py` for build approval. Consistent UX, proven architecture.
5. **Compass Logic** (pure frontend JavaScript) — Direction resolution and spatial validation in editor. Backend receives exits with name/aliases already set—no server-side compass awareness needed.

**Critical pattern: Mirror character approval for build approval.** The codebase already has a working approval workflow (`PendingCharactersAPI`, `CharacterApprovalAPI`, approval page). Reusing this pattern for builds ensures consistency and reduces risk.

### Critical Pitfalls

Research identified five critical pitfalls that would cause data corruption, security breaches, or require rewrites if encountered:

1. **Thread-unsafe object creation** — Creating Evennia game objects from Django views without `run_in_main_thread()` produces instances that exist in database but are invisible to the live game's idmapper cache. Objects appear to "vanish" until @reload. **Prevention:** Service layer wrapping all `create_object()` / `create_script()` calls in `run_in_main_thread()`.

2. **JSON map data race conditions** — Two staff members editing the same project read, modify, and write `BuildProject.map_data` independently. Last write silently overwrites first, discarding changes. **Prevention:** Add `version` integer field to BuildProject, implement optimistic concurrency control (reject save if database version is higher).

3. **Trigger system code injection** — If triggers can contain Python expressions or `@py` commands, builders with web access can inject arbitrary code executing with server-level privileges. **Prevention:** Whitelist predefined trigger actions (`send_message`, `move_object`, etc.). Never use eval/exec. Validate JSON schema at save time.

4. **Sandbox rooms leak into live world** — Sandbox rooms become reachable from live game via accidental exits, `@tel` commands, or home location assignments. **Prevention:** Tag all sandbox objects, add `traverse:pperm(Builder)` locks, implement `SandboxRoom` typeclass that blocks non-staff entry, validate promotion does not create cross-boundary exits.

5. **Promotion creates broken exit connections** — Promotion must re-map internal exit connections from sandbox aliases to promoted aliases. If mapping is incomplete, exits point to nonexistent destinations or sandbox copies. **Prevention:** Two-phase promotion (create all rooms, record mapping, create all exits using mapping, validate destinations exist, then cleanup sandbox). Do NOT destroy sandbox until validation passes.

## Implications for Roadmap

Based on research, suggested phase structure with clear dependency ordering:

### Phase 1: Complete Character Approval Workflow
**Rationale:** Chargen is customer-facing and closest to launch-ready. Filling table stakes gaps here unblocks player onboarding and validates the approval workflow pattern before applying it to builds.

**Delivers:**
- Rejection resubmission flow (view notes, edit, resubmit)
- Background text field in CharacterBio model and form
- Character location assignment on approval
- In-game notification via Evennia msg system
- Player-facing character sheet view (read-only)

**Addresses:** Five table stakes features from FEATURES.md (rejection resubmission, background field, location assignment, notifications, sheet view)

**Avoids:** Pitfall M1 (CSRF protection) by removing `@csrf_exempt` from character approval endpoints before adding new approval features

**Research flag:** NO—character approval pattern is already implemented. This phase extends existing code rather than introducing new patterns.

---

### Phase 2: Build Approval Queue + State Machine
**Rationale:** Establishes approval workflow for builds before implementing sandbox/promotion. State machine prevents invalid transitions that later phases depend on (cannot build to sandbox without approval, cannot promote without sandbox).

**Delivers:**
- `status` field on BuildProject with django-fsm-2 state machine
- `BuildApproval` model tracking review history
- Submission API endpoint (builder submits project for review)
- Staff approval dashboard (mirrors character approval page)
- Approval actions API (approve/reject/request revision)

**Addresses:** Table stakes feature "build approval workflow" from FEATURES.md

**Uses:** django-fsm-2 4.1.0 from STACK.md, htmx for approval dashboard updates

**Implements:** State Machine Layer from ARCHITECTURE.md

**Avoids:** Pitfall M2 (approval double-action race) by using atomic state transitions (`UPDATE ... WHERE status = 'pending'`)

**Research flag:** NO—mirrors existing character approval pattern with proven django-fsm-2 library.

---

### Phase 3: Sandbox Building via Direct Evennia API
**Rationale:** Must come after approval workflow (Phase 2) because sandbox creation requires approved projects. This is the highest-risk phase architecturally due to thread safety concerns and Evennia integration complexity.

**Delivers:**
- Bridge layer module (`builder/sandbox_builder.py`)
- `create_sandbox_from_project()` function using `evennia.create_object()` wrapped in `run_in_main_thread()`
- Sandbox room/exit creation with tag-based tracking (`project_{id}`, `sandbox`)
- ID mapping storage (web room IDs → Evennia dbrefs)
- Trigger script creation for rooms with trigger data
- Sandbox teardown/cleanup function

**Addresses:** Table stakes feature "auto-sandbox" from FEATURES.md

**Implements:** Bridge Layer from ARCHITECTURE.md

**Avoids:**
- Pitfall C1 (thread-unsafe creation) by wrapping all Evennia API calls in service layer with `run_in_main_thread()`
- Pitfall C4 (sandbox leaks) by tagging all objects, adding traverse locks, validating no cross-boundary exits
- Pitfall M4 (no undo) by recording build manifest for rollback
- Pitfall M5 (@reload required) by forcing cmdset refresh after exit creation

**Research flag:** YES—this phase needs deeper research for:
- Evennia `run_in_main_thread()` integration patterns
- Exit cmdset cache behavior after programmatic creation
- Tag-based object querying performance at scale

---

### Phase 4: Live Promotion + Connection
**Rationale:** Depends on Phase 3 (must have sandbox to promote). This phase has moderate architectural complexity due to exit re-mapping and validation requirements.

**Delivers:**
- `promote_sandbox_to_live()` function with two-phase commit pattern
- Promotion dialog UI (search target room, select exit directions)
- Old-to-new ID mapping and validation
- Exit creation between promoted area and live world
- Sandbox cleanup after successful promotion

**Addresses:** Table stakes feature "promotion to live grid" from FEATURES.md

**Avoids:** Pitfall C5 (broken exits) by implementing two-phase promotion with validation before sandbox cleanup

**Research flag:** NO—architecture pattern is well-defined. Implementation is straightforward given Phase 3 bridge layer.

---

### Phase 5: Room Templates + Compass Rose
**Rationale:** Can be developed in parallel with Phases 3-4 (no backend dependencies). Enhances builder UX without blocking critical workflow features.

**Delivers:**
- Seed V5 room template presets (Elysium, Haven, Rack, Street, Alley)
- Template dropdown in editor UI
- Apply template to selected room
- Compass rose widget on room nodes
- Direction auto-naming based on grid position
- Auto-reverse exit creation (A→B creates B→A automatically)

**Addresses:** Competitive features "V5 room templates" and "compass rose" from FEATURES.md

**Uses:** Alpine.js 3.15.3 for compass rose reactive UI

**Research flag:** NO—room templates use existing `RoomTemplate` model, compass logic is pure frontend.

---

### Phase 6: Trigger System (Entry/Exit/Timed)
**Rationale:** Can start after Phase 3 completes (triggers created during sandbox build). Most complex phase due to security requirements and V5-specific condition system.

**Delivers:**
- `TriggerScript` typeclass for timed triggers
- Room typeclass hooks (`at_object_receive`, `at_object_leave`) for entry/exit triggers
- Trigger editor UI in builder sidebar
- Trigger type selector (entry/exit/timed)
- Whitelisted action system (send_message, move_object, set_attribute)
- JSON schema validation for trigger data
- V5-aware condition checks (hunger level, clan, time-of-night)

**Addresses:** Competitive feature "room trigger system" from FEATURES.md

**Avoids:** Pitfall C3 (code injection) by whitelisting trigger actions, no eval/exec, schema validation at save time

**Research flag:** YES—this phase needs deeper research for:
- V5-specific condition system design
- Trigger action whitelist definition
- Interaction trigger patterns (deferred to Phase 7+)

---

### Phase 7: Enhanced Chargen UX (Post-MVP)
**Rationale:** Defer until core workflows are stable and seeing production use. These features improve UX but are not blocking.

**Delivers:**
- Draft save/resume for chargen (partial character persistence)
- Staff comments on specific traits
- Approval history log (multiple revision tracking)
- V5 rule hints and tooltips

**Research flag:** YES—draft save/resume needs session management research.

---

### Phase Ordering Rationale

**Linear dependencies (critical path):**
- Phase 1 → Phase 2 → Phase 3 → Phase 4
- Cannot build sandbox without approval workflow (Phase 2 gates Phase 3)
- Cannot promote without sandbox (Phase 3 gates Phase 4)
- Character approval pattern must be proven before extending to builds (Phase 1 validates for Phase 2)

**Parallelizable work:**
- Phase 5 (templates + compass) can start immediately—pure frontend with no backend dependencies
- Phase 6 (triggers) can start after Phase 3—triggers integrate into sandbox creation

**Grouping logic:**
- Phases 1-2: Approval workflows (character then build, proving pattern)
- Phases 3-4: Sandbox lifecycle (create then promote, proving bridge layer)
- Phases 5-6: Builder UX enhancements (independent features)
- Phase 7+: Polish and optimization

**Pitfall avoidance:**
- Phase 2 before Phase 3 prevents building without approval
- Phase 3 service layer addresses thread safety before any object creation happens
- Phase 4 validation prevents broken promotions
- Phase 6 whitelist approach prevents code injection from the start

### Research Flags

**Phases needing deeper research during planning:**

- **Phase 3 (Sandbox Building):** Complex Evennia integration, thread safety patterns, cmdset cache behavior, tag-based querying performance. Most architecturally risky phase.

- **Phase 6 (Trigger System):** V5-specific condition system is novel, trigger action whitelist needs careful design, security implications require validation.

- **Phase 7 (Draft Save/Resume):** Session management and partial character persistence patterns need investigation.

**Phases with standard patterns (skip research-phase):**

- **Phase 1 (Character Approval):** Extends existing proven pattern. No new architectural concepts.

- **Phase 2 (Build Approval):** Mirrors Phase 1 pattern. django-fsm-2 is well-documented with clear examples.

- **Phase 4 (Promotion):** Architecture is well-defined in ARCHITECTURE.md. Implementation is straightforward given Phase 3 bridge layer.

- **Phase 5 (Templates + Compass):** Templates use existing model, compass is pure frontend JavaScript with no backend complexity.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified via PyPI, npm, official docs. Django 5.2.7 and Python 3.13 compatibility confirmed for all components. |
| Features | HIGH | Table stakes features verified via codebase inspection and AresMUSH/WoD MU community standards. Differentiators validated against MUSH/MUX precedent and map builder tool survey. |
| Architecture | HIGH | Bridge layer pattern verified against Evennia source code (`create_object` API, `run_in_main_thread` implementation). State machine and trigger patterns well-documented. |
| Pitfalls | HIGH | Thread safety, JSON race conditions, and code injection verified via Evennia source code and official security documentation. Sandbox isolation and promotion patterns are architectural analysis (medium-high confidence). |

**Overall confidence:** HIGH

### Gaps to Address

Despite high overall confidence, three areas need validation during implementation:

- **Exit cmdset cache behavior after programmatic creation:** The research identified that cmdsets may need explicit refresh after creating exits via API (not via in-game commands). This is architectural inference from Evennia's exit cmdset system—needs empirical testing in Phase 3. Mitigation: Test exit traversability immediately after creation, document cmdset refresh requirement.

- **V5-aware trigger condition system:** The trigger system's condition framework (checking hunger level, clan, time-of-night) is novel and not documented in existing MU systems. Needs design research in Phase 6. Mitigation: Start with simple conditions (attribute checks, tag checks) and expand based on V5 data model.

- **JSON schema versioning and migration:** As features are added (triggers, V5 attributes, templates), the `map_data` JSON structure will evolve. No migration path exists for old projects. Needs schema versioning strategy. Mitigation: Add `schema_version` field to `map_data` before Phase 3, write migration functions as schema evolves.

- **Concurrency control for map editing:** The research identified JSONField race conditions as critical risk but did not specify optimal implementation (version field vs timestamp vs PostgreSQL jsonb_set). Needs decision in Phase 2 or earlier. Mitigation: Start with simple version field approach, measure if contention is actually a problem in practice.

## Sources

### Primary (HIGH confidence)

**Stack Research:**
- Evennia 5.0.1 metadata (`.dist-info/METADATA`) — verified installed version and Django 5.2.7 requirement
- django-htmx on PyPI (version 1.27.0, released 2025-11-28) — verified Django 5.2/Python 3.13 compatibility
- django-fsm-2 on PyPI (version 4.1.0, released 2025-11-03) — verified Django 5.2/Python 3.13 compatibility
- htmx releases on GitHub (version 2.0.8) — verified CDN availability
- Alpine.js releases on GitHub (version 3.15.3) — verified CDN availability
- Bootstrap blog (5.3.8 release) — verified dark mode support

**Feature Research:**
- Codebase inspection: `builder/models.py`, `builder/views.py`, `builder/exporter.py`, `traits/api.py`, `typeclasses/`, `web/templates/` — verified existing features and gaps
- Evennia Prototypes Documentation — verified prototype system and inheritance patterns
- AresMUSH Chargen Configuration — verified approval workflow and post-approval automation patterns

**Architecture Research:**
- Evennia source code: `evennia/utils/utils.py:2862-2877` — verified `run_in_main_thread()` implementation
- Evennia source code: `evennia/objects/objects.py` — verified `create_object()`, `DefaultRoom.create()`, `DefaultExit`, exit cmdset behavior
- Evennia Batch Command Processor docs — verified no Python API exists for programmatic execution
- Evennia Scripts Documentation — verified timer script patterns and `at_repeat` hooks

**Pitfall Research:**
- Evennia source code: idmapper, typeclass system, threading model — verified cache behavior and thread safety requirements
- Evennia Security Practices documentation — verified injection risks and recommended patterns
- Codebase inspection: `exporter.py`, `views.py` — verified CSRF protection gaps, `@py` usage, sanitization patterns

### Secondary (MEDIUM confidence)

- Evennia NPC Reacting Tutorial — entry trigger pattern with `at_object_receive`
- AresMUSH Web Portal feature documentation — comparative analysis for feature expectations
- MUSH Manual — trigger patterns (@aenter, @aleave, @listen)
- City of Hope MUSH Chargen — WoD chargen workflow example
- MUDMapBuilder, Mudlet Mapper, Mud-Mapper — compass direction patterns in map builders
- Django Forum: JSONField race conditions — F() expressions do not work with JSONField
- Django race condition techniques — select_for_update, optimistic concurrency patterns

### Tertiary (LOW confidence, needs validation)

- MUD trigger system vulnerability patterns (DGScripts, MobProgs, LPC) — general domain knowledge, no specific sources
- MU Soapbox V5 Discussion — community feedback on V5 MU design (anecdotal)

---

*Research completed: 2026-02-03*
*Ready for roadmap: yes*
