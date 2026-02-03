# Feature Landscape: MUD Web Portal, Builder, Chargen, and Workflow Systems

**Domain:** Evennia-based V5 Vampire MUD -- web portal features for character creation, area building, approval workflows, triggers, and sandbox/promotion flows
**Researched:** 2026-02-03
**Overall confidence:** MEDIUM-HIGH (based on codebase inspection + ecosystem research of AresMUSH, Evennia docs, MUSH/MUX precedent, and WoD MU community patterns)

---

## Current State (What Already Exists)

Before categorizing features, here is what TheBeckoningMU already has in place. All features below are assessed relative to this baseline.

| System | Status | Notes |
|--------|--------|-------|
| Web character creation form | **Built** | Full V5 dot-picker UI (attributes, skills, disciplines, advantages, flaws), clan info, priority system, client-side validation, posts to `/api/traits/character/create/` |
| Staff character approval page | **Built** | Lists pending characters, shows full sheet (bio + traits + powers), approve/reject with notes |
| Traits API layer | **Built** | 11 endpoints covering categories, traits, discipline powers, character CRUD, validation, approval |
| Web grid builder editor | **Built** | Canvas with room nodes, SVG exit lines, grid snapping, drag-and-drop, room properties sidebar |
| V5 room settings in builder | **Built** | Location type, day/night access, danger level, hunting modifier, haven ratings |
| Batch script exporter | **Built** | Generates `.ev` batch files from map_data JSON, with whitelist sanitization |
| Build project model | **Built** | `BuildProject` with `map_data` JSONField, `sandbox_room_id`, `promoted_at` |
| Room template model | **Built** | `RoomTemplate` model exists, API returns 501 (not implemented) |
| Dashboard with project list | **Built** | Shows own projects + public projects, status badges (Draft/In Sandbox/Live) |
| Trigger UI placeholder | **Stub** | Button says "Trigger editor coming in Phase 5", `updateTriggersDisplay()` and `addTrigger()` are TODOs |
| Build to Sandbox | **Stub** | Button exists, returns "manual_required" from API (auto-execution not implemented) |
| Compass mode | **Stub** | Button exists in toolbar, no implementation |

---

## Table Stakes

Features users expect. Missing = product feels incomplete or amateurish compared to established MU* games.

### Character Creation & Approval

| Feature | Why Expected | Complexity | Existing? | Notes |
|---------|--------------|------------|-----------|-------|
| V5-compliant chargen form with dot pickers | Players expect to build characters with accurate V5 rules (priority system, clan disciplines, advantages/flaws) | High | **YES** | Already built. Comprehensive V5 form with client-side validation. |
| Server-side character validation | Prevent invalid sheets from being submitted (wrong dot totals, disallowed discipline combos) | Medium | **PARTIAL** | `CharacterValidationAPI` exists and calls `enhanced_import_character_from_json` with `validate_only=True`. Needs verification that all V5 rules are enforced server-side. |
| Pending character queue for staff | Staff must be able to see who is waiting for approval | Low | **YES** | `PendingCharactersAPI` and approval page both working. |
| Approve/reject with notes | Staff must communicate reasons for rejection and any notes on approval | Low | **YES** | `CharacterApprovalAPI` supports action + notes. Notes stored on character. |
| Rejection resubmission flow | After rejection, player should be able to edit and resubmit without starting over | Medium | **NO** | Critical gap. Currently no way for players to view rejection notes or edit a rejected character. AresMUSH treats this as core -- players can revise and resubmit. Without this, rejected players must start from scratch. |
| In-game notification on approval/rejection | Player should be notified in-game (or via web) when their character is approved or rejected | Low | **NO** | AresMUSH creates a job, sends @mail, and posts to forum. Current system has no notification mechanism. |
| Character location assignment on approval | Approved character needs to be placed in the starting room | Low | **NO** | Current `CharacterCreateAPI` creates character with `location=None, home=None`. No post-approval hook sets location. |
| Background/RP hooks text fields | Players need free-text areas for character backstory beyond mechanical stats | Low | **PARTIAL** | Bio model has `concept`, `ambition`, `desire` but no general `background` or `rp_hooks` field. WoD MU* games universally require a written background. |
| Character sheet view (for player) | Players should be able to view their own sheet on the web | Low | **NO** | Only staff can view via `CharacterDetailAPI`. No player-facing sheet view. |

**Confidence: HIGH** -- Based on direct codebase inspection plus AresMUSH/WoD MU* community standards. Every WoD MU* requires these features.

### Web Grid Builder

| Feature | Why Expected | Complexity | Existing? | Notes |
|---------|--------------|------------|-----------|-------|
| Visual room placement with drag-and-drop | Builders expect to visually lay out rooms on a canvas | Medium | **YES** | Working. Grid-snapped placement, SVG exit lines, selection. |
| Room properties editing (name, desc, V5 settings) | Must be able to configure each room's attributes | Medium | **YES** | Full sidebar with Basic, V5 Settings, Haven Ratings, Builder Notes sections. |
| Exit creation by clicking source then target | Standard pattern for visual builders | Low | **YES** | Working. Exit mode click-to-connect. |
| Batch export to Evennia format | Must produce runnable build scripts | Medium | **YES** | `.ev` batch file generation with sanitized output. |
| Save/load projects | Builders need persistence | Low | **YES** | `SaveProjectView` / `GetProjectView` with JSON storage. |
| Room deletion (with connected exit cleanup) | Must be able to remove mistakes | Low | **YES** | `deleteSelected()` removes room and all connected exits. |
| Validation warnings (isolated rooms, missing descriptions) | Builder should see warnings before exporting | Low | **YES** | `validate_project()` checks for isolated rooms, invalid exit refs, empty descriptions, duplicate names. |

**Confidence: HIGH** -- Based on codebase inspection. Core builder already works.

### Approval Workflow for Builds

| Feature | Why Expected | Complexity | Existing? | Notes |
|---------|--------------|------------|-----------|-------|
| Build submission for staff review | Non-admin builders must submit builds for approval before they go live | Medium | **NO** | Currently any staff user can build directly. No submission/review step for builds. The `is_public` field allows visibility but not approval gating. |
| Staff review interface for builds | Staff needs to preview builds before approving | Medium | **NO** | No equivalent of the character approval page for builds. Would need a map preview + approval actions. |
| Build status tracking (Draft -> Submitted -> Approved -> Built) | Clear lifecycle states | Low | **PARTIAL** | Model has `sandbox_room_id` and `promoted_at` but no explicit status field. No "submitted for review" state. |

**Confidence: MEDIUM** -- Based on MUSH/MUX ecosystem patterns. In traditional MU*, builder approval is handled via quotas, building permissions, or zone-based trust. Web-based approval for builds is less standardized than chargen approval, but a natural extension given the existing model.

### Sandbox and Promotion

| Feature | Why Expected | Complexity | Existing? | Notes |
|---------|--------------|------------|-----------|-------|
| Auto-sandbox (build project to isolated in-game area) | Builders must be able to test their builds in-game before going live | High | **STUB** | `BuildProjectView` returns "manual_required". `sandbox_room_id` field exists on model but no automatic execution. Need: create rooms via Evennia API (not batch file), link to project, tag for tracking. |
| Walk-through testing in sandbox | Builder must be able to enter the sandbox and walk around their build | Low | **NO** (depends on sandbox) | Once sandbox rooms exist in-game, walking is native Evennia. Need: teleport builder to sandbox entry point. |
| Promotion to live grid | Move approved builds from sandbox to the main game world | High | **NO** | `promoted_at` field exists but no promotion logic. Need: re-parent sandbox rooms to target location, remove sandbox container, update tags, record promotion. |
| Sandbox cleanup/abandonment | Ability to tear down a sandbox | Medium | **NO** | Exporter mentions "@abandon in-game" but no implementation exists. Need: delete all rooms/exits tagged with project ID. |

**Confidence: MEDIUM** -- The sandbox/promotion pattern is well-established in software development (dev -> staging -> production) but rarely implemented in MUD builders. This is novel territory for Evennia. The Agile Data sandbox model (dev -> integration -> demo -> pre-prod -> production) maps well but needs adaptation for MUD context.

---

## Differentiators

Features that set TheBeckoningMU apart. Not expected by every MU* player, but significantly valued.

### Room Templates (V5 Presets)

| Feature | Value Proposition | Complexity | Existing? | Notes |
|---------|-------------------|------------|-----------|-------|
| V5 location presets (Elysium, Haven, Rack, etc.) | One-click room creation with correct V5 attributes pre-filled. Saves builders from knowing all V5 room settings by heart. | Low | **MODEL EXISTS** | `RoomTemplate` model defined. `TemplatesView` returns 501. Need: seed V5 presets, expose in editor as dropdown/palette. |
| Custom template creation/sharing | Builders can save their own room configurations as reusable templates | Medium | **MODEL EXISTS** | `is_shared` field on `RoomTemplate`. Need: save-as-template UI, template browser in editor. |
| Template inheritance | "Dark Alley" inherits from "Street" but overrides danger_level | Medium | **NO** | Would leverage Evennia's prototype inheritance pattern. Nice-to-have, not essential. |

**Confidence: HIGH** -- The model exists in code. Implementation is straightforward. V5 presets are a genuine differentiator because no other Evennia game has pre-configured WoD room templates in a web builder.

### Room Trigger System

| Feature | Value Proposition | Complexity | Existing? | Notes |
|---------|-------------------|------------|-----------|-------|
| Entry triggers (fire when character enters room) | Enable atmospheric messages, quest progression, ambush encounters, V5 danger notifications | Medium | **PLACEHOLDER** | Triggers stored as JSON in room data. Export writes `@set room/triggers = {json}`. No in-game trigger execution. Need: a TriggerHandler script on Room typeclass that reads trigger data and fires on `at_object_receive`. |
| Exit triggers (fire when character leaves) | Tracking, narrative ("The door slams shut behind you"), territory alerts | Medium | **NO** | Need: `at_object_leave` hook on Room typeclass. |
| Timed triggers (fire on interval) | Atmospheric cycling ("Fog rolls in..."), respawning, patrols | Medium | **NO** | Need: Evennia Script with `at_repeat` attached to room. |
| Interaction triggers (fire on specific commands in room) | "look painting" triggers a clue reveal, "push button" opens secret door | High | **NO** | Need: custom command or `at_say`/`at_look` hooks. More complex -- probably Phase 2. |
| Trigger editor UI in web builder | Visually configure triggers without writing code | Medium | **STUB** | `addTrigger()` shows alert "coming in Phase 5". Trigger count displayed. Need: trigger type selector, condition editor, action editor. |
| Trigger conditions (time-of-day, hunger level, clan check) | V5-specific conditions that make triggers game-aware | High | **NO** | Unique differentiator. No other MU* builder offers WoD-aware trigger conditions in a visual editor. |

**Confidence: MEDIUM** -- The MUSH/MUX precedent for room triggers is very well established (@aenter, @aleave, @listen, MobProgs). Evennia's `at_object_receive` and `at_object_leave` hooks provide the foundation. The V5-specific condition system is novel and needs careful design. The web-based trigger editor is the differentiator -- MUSH triggers are configured via cryptic @-commands.

### Compass Rose for Exit Directions

| Feature | Value Proposition | Complexity | Existing? | Notes |
|---------|-------------------|------------|-----------|-------|
| Compass rose overlay on room nodes | Shows which cardinal directions have exits, oriented correctly on the map | Medium | **STUB** | "Compass" mode button exists but no implementation. Need: render N/S/E/W/NE/NW/SE/SW/U/D indicators on room nodes or as an overlay. |
| Exit direction auto-naming | When connecting rooms in compass mode, auto-name exits "north"/"south" based on spatial relationship | Medium | **NO** | Currently exits default to "exit" with no direction. Compass mode should infer direction from grid positions and auto-populate exit name + aliases (e.g., "north;n"). |
| Direction-aware exit creation | Click a compass point on a room to start an exit in that direction | Medium | **NO** | Instead of generic "click source, click target", compass mode lets you click a directional port on the room node. More intuitive for grid-based maps. |
| Map orientation display | Show N/S/E/W labels on the canvas so builders know orientation | Low | **NO** | Simple compass indicator in a corner of the canvas. |

**Confidence: MEDIUM** -- Based on Mudlet Mapper (which has direction-aware exits), MUD Map Builder, and MUSH building conventions. Standard MUD directions (N/S/E/W/NE/NW/SE/SW/U/D) are universally expected. The Aarchon MapMaker and Mud-Mapper both support compass directions.

### Enhanced Chargen Workflow

| Feature | Value Proposition | Complexity | Existing? | Notes |
|---------|-------------------|------------|-----------|-------|
| Draft save/resume | Player can save progress and return later to finish chargen | Medium | **NO** | Currently all-or-nothing submission. Would need to store partial character data (perhaps in session or a separate model). AresMUSH supports this. |
| Staff comments on specific traits | Instead of just approve/reject notes, staff can flag individual traits ("Explain why Allies 4") | Medium | **NO** | Would require a per-trait annotation model or a structured notes format. |
| V5 rule hints in chargen | Contextual tooltips explaining V5 mechanics (e.g., what Blood Potency means, what each Predator Type grants) | Low | **PARTIAL** | Clan bane descriptions shown. Predator Type bonuses not shown. No tooltips on attributes/skills. |
| Background text requirement | Require a minimum-length background before submission | Low | **NO** | No background field exists. AresMUSH enforces minimum background length. WoD MU* universally require backgrounds. |
| Approval history log | Track all approval/rejection actions with timestamps and staff names | Low | **PARTIAL** | `approved_by` and `approved_at` stored but no history -- only latest action. Multiple revision cycles would overwrite. |

**Confidence: MEDIUM-HIGH** -- Based on AresMUSH feature set and WoD MU* community expectations.

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Full in-browser MUD client replacement | Web portal should complement the telnet/webclient experience, not replace it. Building a full web-based MUD client is a massive scope trap. Evennia's existing webclient handles gameplay. | Keep web portal focused on out-of-game workflows: chargen, building, approval, reference. The game itself is played in the MUD client. |
| WYSIWYG room description editor with rich text | MUD rooms use plain text or ANSI/MXP markup. A rich text editor adds complexity and produces output incompatible with telnet clients. | Plain textarea for descriptions. Optionally add ANSI color preview but keep the source format as plain text. |
| Automated stat optimization / min-maxing assistant | Recommending "optimal" builds undermines roleplaying spirit of V5. WoD MU* games deliberately avoid this. | Show rules enforcement only (point totals, allowed ranges). Never suggest "best" builds. |
| Real-time collaborative building | Multiple builders editing the same project simultaneously (Google Docs style) is enormously complex for minimal benefit. MU* building is typically a solo or sequential activity. | Single editor with project ownership. Public view-only for others. Use the existing `is_public` flag. If collaboration is needed later, add a "copy project" feature. |
| In-game building commands that duplicate the web builder | Maintaining two parallel building interfaces (web + in-game commands) is a maintenance nightmare. Pick one and make it good. | Web builder is the primary building tool. In-game commands (`@dig`, `@desc`) remain for quick fixes. The web builder generates batch scripts that run in-game. |
| Automatic character approval (no human review) | V5 characters require narrative review (is the background sensible? does the clan choice make sense thematically?). Pure mechanical validation cannot catch everything. | Keep staff review mandatory. Enhance the review UI to make it faster, but never bypass it. |
| Complex trigger scripting language | Inventing a custom scripting language for triggers creates a learning curve and maintenance burden. Builders should not need to learn a DSL. | Use a structured trigger editor with dropdowns for type/condition/action. Map these to Python hooks on the backend. Builders configure via UI, developers implement new trigger types in Python. |
| Free-form Python execution in triggers | Allowing builders to run arbitrary Python code via triggers is a massive security risk (the Evennia docs explicitly warn about `@batchcode`). | Whitelist trigger actions. Each action is a pre-built Python function. Builders can only select from available actions, not write code. |

**Confidence: HIGH** -- Based on security warnings in Evennia docs, MUSH/MUX community wisdom about scope creep, and WoD MU* culture around approval processes.

---

## Feature Dependencies

```
Character Creation & Approval (existing)
  |
  +-- Rejection resubmission flow (depends on: existing chargen)
  |     +-- Draft save/resume (depends on: resubmission model)
  |
  +-- Background text field (depends on: CharacterBio model update)
  |
  +-- Player-facing sheet view (depends on: existing CharacterDetailAPI)
  |
  +-- In-game notification on approval (depends on: Evennia msg system)
  |     +-- Post-approval hooks (depends on: notification + location assignment)
  |
  +-- Character location assignment (depends on: approval API update)

Web Grid Builder (existing)
  |
  +-- Compass Rose (depends on: existing editor UI)
  |     +-- Direction auto-naming (depends on: compass rose)
  |
  +-- Room Templates (depends on: existing RoomTemplate model)
  |     +-- V5 presets (depends on: template system)
  |
  +-- Trigger Editor UI (depends on: existing editor)
  |     +-- Entry triggers backend (depends on: Room typeclass hooks)
  |     +-- Exit triggers backend (depends on: Room typeclass hooks)
  |     +-- Timed triggers backend (depends on: Evennia Scripts)
  |     +-- V5-aware conditions (depends on: trigger backend + V5 data)
  |
  +-- Build Approval Workflow (depends on: model status field)
  |     +-- Staff review interface for builds (depends on: approval model)
  |
  +-- Auto-Sandbox (depends on: Evennia API for room creation)
  |     +-- Walk-through testing (depends on: sandbox rooms existing)
  |     +-- Sandbox cleanup (depends on: tagging system)
  |
  +-- Promotion to Live (depends on: sandbox + approval workflow)
        +-- Re-parenting rooms (depends on: Evennia room hierarchy)
```

---

## MVP Recommendation (Next Milestone)

For the next milestone, prioritize in this order:

### Phase 1: Complete Chargen Workflow (Table Stakes Gaps)
1. **Rejection resubmission flow** -- Players can view rejection notes, edit, and resubmit. Without this, the chargen workflow is incomplete.
2. **Background text field** -- Add to CharacterBio model and chargen form. Required by every WoD MU*.
3. **Character location assignment on approval** -- Approved characters get placed in starting room.
4. **In-game notification** -- @mail or msg to player on approval/rejection.
5. **Player-facing character sheet view** -- Read-only web view of own character.

### Phase 2: Compass Rose + Room Templates (High-Value, Low-Risk)
1. **Compass rose on room nodes** -- Direction indicators on the visual builder.
2. **Direction auto-naming for exits** -- Infer "north"/"south" from grid position.
3. **V5 room template presets** -- Seed Elysium, Haven, Rack, etc. templates.
4. **Template dropdown in editor** -- Apply template to new room.

### Phase 3: Build Approval + Sandbox
1. **Build status field + submission** -- Add status enum to BuildProject, staff review queue.
2. **Auto-sandbox via Evennia API** -- Create rooms directly instead of batch file.
3. **Sandbox cleanup** -- Delete sandbox rooms by tag.
4. **Promotion to live** -- Move rooms to target location.

### Phase 4: Trigger System
1. **Entry trigger backend** -- `at_object_receive` handler on Room typeclass.
2. **Trigger editor UI** -- Configure trigger type, condition, action in sidebar.
3. **Exit triggers + timed triggers** -- Expand trigger types.
4. **V5-aware conditions** -- Hunger, clan, time-of-night checks.

### Defer to Post-MVP:
- **Draft save/resume for chargen**: Nice-to-have but complex session management. Defer until chargen sees heavy use.
- **Staff comments on specific traits**: Approval notes field is sufficient for now.
- **Interaction triggers**: Complex and niche. Entry/exit/timed covers 90% of use cases.
- **Template inheritance**: Nice architectural pattern but not needed until template library grows.
- **Approval history log**: Single approve/reject is fine for launch. Add history tracking if revision cycles become common.

---

## Complexity Estimates

| Feature | Frontend | Backend | Integration | Total |
|---------|----------|---------|-------------|-------|
| Rejection resubmission | Medium | Low | Low | **Medium** |
| Background text field | Low | Low | Low | **Low** |
| Location on approval | None | Low | Medium | **Low** |
| In-game notification | None | Medium | Medium | **Medium** |
| Player sheet view | Medium | Low | Low | **Medium** |
| Compass rose | Medium | None | None | **Medium** |
| Direction auto-naming | Medium | Low | Low | **Medium** |
| V5 room templates | Low | Low | Low | **Low** |
| Template dropdown | Low | Low | None | **Low** |
| Build status + submission | Low | Medium | Low | **Medium** |
| Auto-sandbox | Low | High | High | **High** |
| Sandbox cleanup | Low | Medium | Medium | **Medium** |
| Promotion to live | Low | High | High | **High** |
| Entry trigger backend | None | High | Medium | **High** |
| Trigger editor UI | High | Low | Medium | **High** |
| Exit/timed triggers | None | Medium | Medium | **Medium** |
| V5-aware conditions | Medium | High | High | **High** |

---

## Sources

### Codebase (HIGH confidence -- direct inspection)
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\web\builder\models.py` -- BuildProject, RoomTemplate models
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\web\builder\views.py` -- All builder views including stubs
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\web\builder\exporter.py` -- Batch script generation
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\web\builder\validators.py` -- Project validation
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\web\templates\builder\editor.html` -- Full editor UI
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\web\templates\character_creation.html` -- Chargen form
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\web\templates\character_approval.html` -- Approval UI
- `C:\Users\dasbl\PycharmProjects\TheBeckoningMU\beckonmu\traits\api.py` -- All API endpoints

### Ecosystem Research (MEDIUM confidence -- web search verified with official docs)
- [Evennia Prototypes Documentation](https://www.evennia.com/docs/latest/Components/Prototypes.html) -- Prototype system, OLC, inheritance
- [Evennia Scripts Documentation](https://www.evennia.com/docs/4.x/Components/Scripts.html) -- Timer scripts, at_repeat hooks
- [Evennia NPC Reacting Tutorial](https://www.evennia.com/docs/latest/Howtos/Tutorial-NPC-Reacting.html) -- at_object_receive pattern
- [AresMUSH Chargen Configuration](https://aresmush.com/tutorials/config/chargen.html) -- Approval workflow, post-approval automation
- [AresMUSH Custom Approval Triggers](https://www.aresmush.com/tutorials/code/hooks/approval-triggers.html) -- Automated post-approval actions
- [AresMUSH Web Portal](https://aresmush.com/web-portal/) -- Feature set of primary competitor

### MU* Community Patterns (MEDIUM confidence -- multiple sources agree)
- MUSH Manual -- @aenter, @aleave, @listen trigger patterns
- [City of Hope MUSH Chargen](https://cityofhopemush.net/index.php/Character_Generation) -- WoD chargen + approval flow
- [MU Soapbox V5 Discussion](https://musoapbox.net/topic/3830/world-of-darkness-5th-edition-experiment) -- V5 MU* community feedback

### Map Builder Tools (LOW-MEDIUM confidence -- surveyed but not deeply verified)
- [MUDMapBuilder](https://mudmapbuilder.github.io/) -- JSON-based map generation
- [Mudlet Mapper](https://wiki.mudlet.org/w/Manual:Mapper) -- Direction-aware room mapping
- [Mud-Mapper (GitHub)](https://github.com/Bakajan/Mud-Mapper) -- Web-based MUD map maker
