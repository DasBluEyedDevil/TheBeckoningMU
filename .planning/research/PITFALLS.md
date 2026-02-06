# Domain Pitfalls: MUD Web Builder Portal

**Domain:** Evennia MUD web-based builder tools, approval workflows, sandbox/promotion systems, trigger editors
**Project:** TheBeckoningMU (Vampire: The Masquerade V5)
**Researched:** 2026-02-03
**Overall Confidence:** MEDIUM-HIGH (verified against Evennia source code and official docs)

---

## Critical Pitfalls

Mistakes that cause data corruption, security breaches, or require rewrites.

---

### Pitfall C1: Thread-Unsafe Game Object Creation from Django Views

**What goes wrong:** Creating Evennia game objects (rooms, exits, objects) directly from Django web views using `create_object()` or `DefaultRoom.create()` without routing through the Twisted reactor thread. The web WSGI layer runs in a separate threadpool from the Twisted reactor. Evennia's idmapper caches all typeclass instances in memory; creating objects from the wrong thread produces instances that exist in the database but are invisible to the live game's cache, or worse, creates cache inconsistencies that cause attribute writes to silently fail or overwrite each other.

**Why it happens:** Django views look like normal Python -- developers call `create_object()` the same way they would in a command's `func()` and it appears to work in testing (single user, no concurrent access). The idmapper's `SharedMemoryModel` masks the threading issue until objects start behaving inconsistently under load.

**Consequences:**
- Rooms exist in database but are not traversable in-game until `@reload`
- Exits point to cached stale instances, causing "destination not found" errors
- Attribute writes from web view and game server overwrite each other (last-write-wins on the same object)
- Objects appear to "vanish" because the reactor thread's cache does not know about them

**Prevention:**
- **Always use `evennia.utils.utils.run_in_main_thread()`** for any operation that creates, modifies, or deletes Evennia game objects from a Django view. Verified in Evennia source at `evennia/utils/utils.py:2862`: this function checks `_IS_MAIN_THREAD` and if false, uses `threads.blockingCallFromThread(reactor, ...)` to safely schedule the call on the reactor.
- Build a service layer (e.g., `builder/services.py`) that wraps all game-object-mutating operations in `run_in_main_thread()`, so views never call Evennia APIs directly.
- Write integration tests that verify objects created via web views are visible in the game's idmapper cache without a reload.

**Detection (warning signs):**
- Objects visible in Django admin but not findable with `@find` in-game
- `@reload` "fixes" missing objects
- Intermittent attribute value corruption (value reverts to old state)
- Errors referencing "NoneType" when accessing `.location` on recently created objects

**Confidence:** HIGH -- verified by reading Evennia source code (`utils.py:2862-2877`, `objects.py` create methods, idmapper implementation)

**Phase relevance:** Sandbox Creation phase -- this is the first place the codebase will attempt to create live game objects from a web view.

---

### Pitfall C2: Map Data Corruption via Concurrent JSONField Writes

**What goes wrong:** Two browser tabs, two staff members, or an autosave firing while a manual save is in progress both read the `BuildProject.map_data` JSONField, modify it independently, and write it back. The last write silently overwrites the first, discarding changes. Unlike normal Django model fields, `F()` expressions do not work with JSONField, so there is no atomic increment/update path.

**Why it happens:** The current `SaveProjectView` (in `views.py:74`) reads the JSON blob from the POST body and writes it wholesale to the model with `project.save()`. There is no optimistic concurrency check (version field), no `select_for_update()`, and no merge logic. This is a read-modify-write cycle with a wide race window because map editing sessions last minutes to hours.

**Consequences:**
- Entire rooms, exits, or objects silently disappear from map data
- Builder loses hours of work with no way to recover
- Map data becomes internally inconsistent (exits referencing deleted rooms)
- Trust in the tool erodes -- builders stop using the web interface

**Prevention:**
- **Add a `version` integer field** to `BuildProject`. Increment it on every save. In `SaveProjectView`, require the client to send the version it loaded; reject the save if the database version is higher (optimistic concurrency control). Return the current data so the client can merge.
- **Use `select_for_update()` inside `transaction.atomic()`** as a belt-and-suspenders measure for the save operation.
- **Add an `updated_at` timestamp comparison** as a simpler initial guard: if the timestamp in the database is newer than what the client loaded, warn the user before overwriting.
- Consider using PostgreSQL's `jsonb_set()` for surgical updates to specific paths within the JSON blob (e.g., updating a single room's description without rewriting the entire blob), though this adds complexity.

**Detection (warning signs):**
- Builders report "my changes disappeared"
- `next_room_id` / `next_exit_id` counters go backward
- Exits reference room IDs that no longer exist in the rooms dict
- Multiple staff members editing the same project

**Confidence:** HIGH -- verified by reading current `SaveProjectView` source code (no concurrency protection) and Django documentation on JSONField race conditions

**Phase relevance:** Builder Editor phase (earliest) -- must be addressed before multiple staff members use the tool.

---

### Pitfall C3: Trigger System Enables Arbitrary Code Execution

**What goes wrong:** The trigger system stores trigger definitions as JSON on room attributes (see `exporter.py:162-165`). If triggers can contain Python expressions, Evennia `@py` commands, or callbacks that get `eval()`'d at runtime, a builder with web access can inject arbitrary code that executes with server-level privileges. Even without `eval()`, if the trigger system interprets trigger actions as Evennia commands, a builder could embed `@py import os; os.system(...)` in a trigger action string.

**Why it happens:** Trigger systems are attractive because they feel like "just data" -- JSON blobs describing "when X happens, do Y." But the "do Y" part must eventually execute code. The temptation is to use `eval()`, `exec()`, or Evennia's `@py` command dispatcher to make triggers flexible. Even restricted expression evaluators (like `simpleeval`, which Evennia already uses) can have escape vectors if not carefully constrained.

**Consequences:**
- Remote code execution on the server
- Database tampering (deleting all objects, modifying other players' characters)
- Server compromise (file system access, credential theft)
- Even in the "benign" case: a buggy trigger creates an infinite loop that freezes the Twisted reactor, hanging the entire MUD for all players

**Prevention:**
- **Use a whitelist of predefined trigger actions** rather than arbitrary expression evaluation. Define an enum of allowed actions: `send_message`, `move_object`, `set_attribute`, `play_sound`, `check_lock`, etc. Each action has typed parameters validated at save time.
- **Never pass trigger content through `eval()`, `exec()`, `@py`, or the batch code processor.**
- **Validate trigger JSON schema at save time** (not just at export time). Reject any trigger with unrecognized action types or parameters that fail validation.
- **Impose execution limits:** triggers per room (e.g., max 10), trigger chain depth (prevent trigger A firing trigger B firing trigger A), and per-trigger cooldown to prevent rapid-fire loops.
- **Use `simpleeval` with a minimal function whitelist** if conditional expressions are needed (e.g., "if hunger > 3"). Restrict available names to the specific context variables. Never expose builtins.
- **Log all trigger firings** in development so infinite loops and abuse are detectable.

**Detection (warning signs):**
- Triggers contain Python syntax (`import`, `__`, `eval`, `exec`, `os.`, `sys.`)
- Triggers reference `@py` or `@batchcode`
- A single room has dozens of triggers
- Server hangs or CPU spikes correlate with player entering a specific room

**Confidence:** HIGH -- this is a well-documented class of vulnerability in MUD scripting systems (DGScripts, MobProgs, LPC all had variants of this). The existing exporter already includes `@py` in its output (line 264 of `exporter.py`), demonstrating the pattern exists in the codebase.

**Phase relevance:** Trigger Editor phase -- must be designed correctly from the start. Retrofitting security onto an expression-based trigger system is extremely painful.

---

### Pitfall C4: Sandbox Rooms Leak Into the Live Game World

**What goes wrong:** Sandbox rooms, intended to be isolated testing environments, become reachable from the live game world through one of several vectors: (a) an exit is accidentally created from a live room to a sandbox room; (b) a `@tel` command moves a character to a sandbox room and they create exits back; (c) the promotion process creates exits to sandbox rooms instead of to the promoted copies; (d) home locations are set to sandbox rooms, so deleted sandbox rooms orphan characters.

**Why it happens:** Evennia has a flat namespace for rooms -- all rooms exist in the same ObjectDB table. There is no built-in concept of "sandbox" vs "live." The current model stores `sandbox_room_id` as a simple integer field on `BuildProject`, but there are no locks, tags, or structural barriers preventing cross-connection. The batch script exporter creates a sandbox container room but connects builder rooms to each other inside it -- nothing prevents an admin from `@open`ing an exit from a live room to a sandbox alias.

**Consequences:**
- Players wander into half-built, untested areas
- Sandbox room deletion (via `clear_exits()` / `clear_contents()`) cascades into deleting exits that connect to live rooms
- Characters whose `home` is a sandbox room get teleported to Limbo when sandbox is destroyed
- Immersion-breaking experience for players ("Why is this room called `_bld_42_3`?")

**Prevention:**
- **Tag all sandbox objects** with a `sandbox` tag and a `project_{id}` tag (the exporter already does the latter). Add a lock on sandbox rooms: `traverse:pperm(Builder)` so non-staff cannot enter.
- **Implement a `SandboxRoom` typeclass** (or use Evennia tags + a custom `at_traverse` hook) that prevents non-builder characters from entering, and that prevents exit creation from non-sandbox rooms.
- **Validate on promotion** that no exits in the promoted area point to sandbox rooms, and no exits in the live world point to sandbox rooms.
- **Set `home` for sandbox objects to a designated builder limbo room**, not to the sandbox rooms themselves, so deletion does not orphan objects.
- **Block `@open` and `@dig` commands** from creating cross-boundary connections (sandbox-to-live or live-to-sandbox) via a custom lock function or command override.

**Detection (warning signs):**
- `@find` returns rooms with `_bld_` prefix aliases
- Players report rooms with no description or with builder-internal names
- `@tel` audit logs show staff visiting sandbox rooms frequently without using the web interface
- Room destruction triggers unexpected cascading deletes

**Confidence:** MEDIUM-HIGH -- the flat-namespace architecture is verified in Evennia source. The specific cross-connection vectors are architectural analysis rather than documented incidents.

**Phase relevance:** Sandbox Creation phase and Promotion phase -- sandbox isolation must be established before the first sandbox is created, and promotion must validate boundaries.

---

### Pitfall C5: Promotion Creates Duplicate or Broken Exit Connections

**What goes wrong:** The promotion process (moving sandbox rooms into the live game world) must re-map internal exit connections from sandbox aliases to promoted aliases, AND create new exits from the live world into the promoted area. If the promotion code re-uses sandbox object IDs/aliases, promoted rooms still reference sandbox metadata. If it creates new copies, internal exits may point to the old sandbox copies instead of the new promoted ones. If the entry-point exits are not created atomically with the internal re-mapping, there is a window where exits point to nonexistent destinations.

**Why it happens:** The current architecture uses batch scripts with aliases like `_bld_{project_id}_{room_id}`. Promotion requires either (a) renaming these aliases and moving rooms to live locations, or (b) creating fresh rooms from the JSON data and connecting them. Both approaches have a re-mapping step where internal references must be updated, and this step is error-prone because it requires tracking the old-to-new ID mapping for every room, exit, and object.

**Consequences:**
- Exits that go nowhere (destination object was the sandbox copy, now deleted)
- Duplicate rooms (sandbox copy still exists alongside promoted copy)
- Exits with wrong names (sandbox alias visible to players)
- Partial promotion (some rooms promoted, some not, exits broken between them)
- Cannot roll back a failed promotion because sandbox was already destroyed

**Prevention:**
- **Use a two-phase promotion pattern:**
  1. Phase A: Create all new rooms and objects from `map_data` JSON (not by moving sandbox objects). Record old-to-new ID mapping.
  2. Phase B: Create all exits using the new ID mapping. Validate all exit destinations exist before committing.
  3. Phase C: Create entry-point exits from the designated live-world room(s) into the promoted area.
  4. Phase D: Only after validation passes, mark the sandbox for cleanup.
- **Wrap the entire promotion in a transaction** so partial failures roll back cleanly.
- **Do NOT destroy the sandbox until promotion is validated.** Keep the sandbox tagged as `promoted` and schedule cleanup separately (or let staff manually confirm).
- **Store the old-to-new mapping on the BuildProject** so the promotion can be audited or reversed.
- **Validate after promotion:** walk all exits in the promoted area and confirm every destination is a promoted room (not a sandbox room, not None).

**Detection (warning signs):**
- Exits in the promoted area have `_bld_` prefix aliases
- `@examine` on an exit shows `destination: None`
- Players report being teleported to Limbo when using exits in newly promoted areas
- Two rooms with the same name exist (sandbox and promoted copies)

**Confidence:** MEDIUM -- this is architectural analysis based on the current exporter pattern and Evennia's object model. No promotion code exists yet to verify against.

**Phase relevance:** Promotion phase -- this is the core challenge of that phase.

---

## Moderate Pitfalls

Mistakes that cause delays, technical debt, or degraded user experience.

---

### Pitfall M1: CSRF Protection Disabled on Mutation Endpoints

**What goes wrong:** The current builder views use `@csrf_exempt` on `SaveProjectView`, `DeleteProjectView`, and `BuildProjectView` (verified in `views.py:70,146,167`). This means any external site can forge requests on behalf of an authenticated staff member, potentially saving malicious map data, deleting projects, or triggering builds.

**Why it happens:** During development, CSRF token handling with fetch API requires sending the token in headers. Developers add `@csrf_exempt` to "fix" 403 errors and forget to remove it. The current frontend uses vanilla JS and the CSRF token is available from the template context (`{{ csrf_token }}`), but the fetch calls may not be sending it consistently.

**Consequences:**
- An attacker who knows a staff member is logged in can craft a page that deletes builder projects or overwrites map data
- Particularly dangerous combined with trigger injection (C3) -- attacker saves a project with malicious triggers via CSRF, then tricks a staff member into building it

**Prevention:**
- **Remove `@csrf_exempt`** from all mutation endpoints. Instead, ensure the JavaScript frontend sends the CSRF token in the `X-CSRFToken` header on all POST/PUT/DELETE requests. The character approval page already demonstrates this pattern correctly (see `character_approval.html:178,349`).
- For API endpoints that need to be accessed by non-browser clients, use Django REST Framework's token authentication instead of disabling CSRF entirely.
- Add a pre-merge check (linter rule or code review checklist item) that flags any new `csrf_exempt` decorators.

**Detection (warning signs):**
- Grep for `csrf_exempt` in the codebase
- Staff reports of unexpected project modifications they did not make
- Security scanner flags missing CSRF protection

**Confidence:** HIGH -- verified by reading current source code

**Phase relevance:** Immediate -- should be fixed before any new builder features ship.

---

### Pitfall M2: Approval Queue Double-Action Race Condition

**What goes wrong:** Two staff members view the same pending build/character in the approval queue. Both click "Approve" (or one approves while the other rejects). The second action either succeeds (creating a contradictory state) or fails with an unhelpful error. In the worst case, both approval actions trigger side effects (e.g., promotion to live, notifications sent) before the conflict is detected.

**Why it happens:** The approval action is a simple POST that checks the current status and transitions it. Without optimistic locking or a state machine with atomic transitions, two concurrent requests can both read "pending" and both write "approved."

**Consequences:**
- Build promoted twice (duplicate rooms in the live world)
- Contradictory state: approved AND rejected
- Notifications sent for both approve and reject
- Audit trail is confusing or misleading

**Prevention:**
- **Use a state machine with atomic transitions:** `UPDATE ... SET status = 'approved' WHERE id = X AND status = 'pending'`. Check the affected row count -- if 0, the status already changed and the action should be rejected with a clear message.
- **Use `select_for_update()`** in the approval view to lock the record during the transition.
- **Show real-time status in the UI:** when a staff member is reviewing an item, use polling or WebSocket to show if another staff member has already acted.
- **Make approval side effects idempotent:** if promoting a build, check if promotion already happened before creating objects.

**Detection (warning signs):**
- Audit log shows the same item approved/rejected twice
- Staff members report "I approved it but it was already approved"
- Duplicate rooms appear after approval

**Confidence:** MEDIUM -- the character approval system exists and has this pattern, but the builder approval queue does not exist yet. The risk is well-established in workflow system design.

**Phase relevance:** Approval Queue phase -- must be designed with atomic transitions from the start.

---

### Pitfall M3: Batch Script Export Contains Unsanitized @py Command

**What goes wrong:** The current exporter embeds an `@py` command in the batch script footer (line 264 of `exporter.py`): `@py from evennia import logger; logger.log_info(...)`. While this specific instance is safe because it is hardcoded, it establishes a pattern where `@py` usage in exported scripts is normalized. Future developers may add dynamic `@py` calls that include user-supplied data (project name, room descriptions) without realizing they are creating a code injection vector. The `project.name` in that line is not sanitized through `sanitize_string()` because it is in a Python f-string, not in a batch command argument position.

**Why it happens:** `@py` is a convenient way to execute arbitrary Python in batch scripts. Once it appears in one place, developers copy the pattern without understanding the security implications.

**Consequences:**
- If `project.name` contains crafted Python code and the f-string interpolation reaches `@py`, it could execute arbitrary commands
- Future additions of `@py` calls with user-supplied data create direct code execution paths

**Prevention:**
- **Remove the `@py` line from the exporter entirely.** Use Evennia's logging hooks or tag the sandbox room with a completion marker instead.
- **Add a linting check** that rejects any `@py` or `@batchcode` strings in generated batch scripts.
- **Document the rule:** "Generated batch scripts must NEVER contain `@py` or `@batchcode` commands."
- If server-side logging is needed after batch execution, implement it as a post-build callback in the web view, not in the batch script itself.

**Detection (warning signs):**
- Grep for `@py` in any generated or template batch script
- Code review catches f-string interpolation into `@py` arguments

**Confidence:** HIGH -- verified by reading `exporter.py:264`. The current risk is low (hardcoded logger call) but the pattern risk is significant.

**Phase relevance:** Immediate -- should be cleaned up before the sandbox creation phase.

---

### Pitfall M4: No Undo/Rollback for Sandbox or Promoted Builds

**What goes wrong:** Once a build is executed (sandbox created) or promoted (moved to live), there is no automated way to undo the action. A staff member who realizes the build has errors must manually find and delete every room, exit, and object created by the build. With the current tagging approach (`project_{id}`), finding objects is possible, but the deletion order matters: deleting a room before its exits causes cascading cleanup that may affect unrelated rooms if exits were manually cross-connected.

**Why it happens:** Build/promote operations are treated as "fire and forget." The batch command processor runs sequentially and does not track what it created. The web interface stores `sandbox_room_id` (singular) but a build creates many rooms. There is no manifest of created objects.

**Consequences:**
- Hours of manual cleanup after a bad build
- Accidental deletion of live-world objects during cleanup
- Staff avoids using the builder because mistakes are too costly
- Orphaned objects accumulate in the database over time

**Prevention:**
- **Record a build manifest:** when creating objects (whether via batch script or direct API), record every object ID created in a `BuildManifest` model linked to the `BuildProject`. Store the creation order.
- **Implement `teardown_sandbox(project_id)`:** a function that reads the manifest and deletes objects in reverse creation order (objects first, then exits, then rooms).
- **Implement `rollback_promotion(project_id)`:** uses the stored old-to-new mapping to delete promoted objects and restore the sandbox from `map_data`.
- **Tag all created objects** with both `web_builder` and `project_{id}` tags (the exporter already does this -- keep this pattern when switching to direct creation).

**Detection (warning signs):**
- Staff asks "how do I undo this build?"
- Growing count of objects with `_bld_` aliases that nobody claims
- `@find tag=web_builder` returns unexpectedly high numbers

**Confidence:** MEDIUM-HIGH -- the lack of undo is evident from the current code; the manifest pattern is a standard solution in deployment systems.

**Phase relevance:** Sandbox Creation phase -- the manifest should be built into the first version of direct object creation.

---

### Pitfall M5: Evennia @reload Required After Direct Object Creation

**What goes wrong:** Even when using `run_in_main_thread()` correctly, certain Evennia operations may require an `@reload` before they fully take effect. Exit commands, in particular, are dynamically created cmdsets (see `DefaultExit.create_exit_cmdset()` in `objects.py:3539`) that attach to rooms. If the cmdset cache for a room is stale, newly created exits may not be traversable until the room's cmdset is refreshed.

**Why it happens:** Evennia's exit system works by creating a command with the same name as the exit and adding it to the exit's cmdset. When a player enters a room, the room's contents (including exits) contribute their cmdsets. But if the room was already loaded in the idmapper cache and a new exit is added, the room's cached cmdset merger may not include the new exit until the cache is refreshed.

**Consequences:**
- Newly built sandbox rooms have exits that "don't work" -- typing the exit name does nothing
- Staff must `@reload` after every build, which interrupts all connected players
- Inconsistent behavior: sometimes exits work immediately, sometimes they do not

**Prevention:**
- **After creating exits programmatically, force a cmdset update on the source room:** call `source_room.cmdset.update()` or use `source_room.at_init()` to re-initialize the room's cmdsets.
- **Test exit traversability immediately after creation** in the build service layer.
- **If using batch scripts:** the batch command processor executes commands as a player, which naturally triggers cmdset updates. Direct API creation bypasses this.
- **Document the requirement:** any code that creates exits via the API (not via in-game commands) must explicitly refresh cmdsets.

**Detection (warning signs):**
- Exits appear in `@examine` of a room but typing the exit name does nothing
- `@reload` fixes exit traversal
- Exits created via web builder work inconsistently compared to exits created via `@dig`

**Confidence:** MEDIUM -- this is an architectural inference from how Evennia's exit cmdset system works. The exact cache invalidation behavior may vary between Evennia versions. Needs testing.

**Phase relevance:** Sandbox Creation phase -- must be validated during the first implementation of direct object creation.

---

### Pitfall M6: JSON Map Data Schema Drift

**What goes wrong:** The `map_data` JSONField has no enforced schema. As features are added (V5 attributes, triggers, room templates, object prototypes, haven ratings), the JSON structure grows organically. Older projects lack new fields; newer code assumes they exist. A frontend update changes the structure, but backend validation does not catch the mismatch. Migrations are impossible because the data is in a JSON blob, not in typed columns.

**Why it happens:** JSON schemas are flexible, which is their appeal and their danger. There is no Django migration that validates JSON structure. The validator (`validators.py`) checks for rooms, exits, and basic connectivity but does not validate the internal structure of rooms (V5 attributes, triggers, haven ratings).

**Consequences:**
- `KeyError` when the exporter or sandbox creator accesses `room["v5"]["location_type"]` on an old project that lacks the `v5` key
- Frontend and backend disagree on field names (e.g., `description` vs `desc`)
- "Saved successfully" but export/build fails because the data does not match expected schema
- Old projects cannot be loaded in new frontend versions

**Prevention:**
- **Define a JSON schema** (using `jsonschema` library or Pydantic models) for `map_data`. Validate on save, on load, and before export/build.
- **Version the schema:** add a `schema_version` field to `map_data`. Write migration functions that upgrade old-format data to new-format data.
- **Use `.get()` with defaults everywhere** in the exporter and builder service (the current exporter does this in some places but not consistently -- e.g., `exit_data['source']` on line 180 will raise `KeyError` if `source` is missing).
- **Add comprehensive validation** to `validators.py` that checks not just connectivity but also the shape of room/exit/object data.

**Detection (warning signs):**
- `KeyError` or `TypeError` in exporter for old projects
- Frontend loads a project but fields are missing or wrong
- "This project was created with an older version" with no migration path

**Confidence:** HIGH -- verified by examining the current validator (only checks room/exit presence and connectivity) and exporter (some `.get()` with defaults, some direct key access).

**Phase relevance:** Builder Editor phase -- schema validation should be added before any new data structures (triggers, V5 attributes) are introduced.

---

## Minor Pitfalls

Mistakes that cause annoyance but are fixable without major rework.

---

### Pitfall m1: Exported Batch Script Room Name Collisions

**What goes wrong:** The batch script uses `@desc {exit_name} = {desc}` and `@name {prototype.lower()} = {obj_name}` which rely on name-based object matching. If two rooms have the same name, or if a room name matches an existing live-world room, the wrong object gets described/modified. The exporter uses aliases (`_bld_{project_id}_{room_id}`) for `@dig` and `@tel` but switches to name-based targeting for descriptions and locks (lines 125, 205-207).

**Prevention:**
- Use aliases consistently for all object targeting in batch scripts, not just for `@dig`/`@tel`.
- Or better: when switching to direct API creation, use object references (pk/dbref) instead of name-based lookup.

**Confidence:** HIGH -- verified by reading `exporter.py` lines 125, 205-211.

**Phase relevance:** Sandbox Creation phase -- this issue goes away when switching from batch scripts to direct API creation.

---

### Pitfall m2: Builder Permission Scope Creep

**What goes wrong:** The builder requires `is_staff` (Django staff flag), which grants access to the Django admin panel and potentially all other staff-only views. A user who should only have builder access gets full staff access.

**Prevention:**
- Create a dedicated `builder` permission (Django permission or Evennia permission level) rather than using `is_staff`.
- Use `@permission_required('builder.can_build')` instead of `@staff_member_required`.

**Confidence:** HIGH -- verified in `views.py` (all views use `StaffRequiredMixin` or `@staff_member_required`).

**Phase relevance:** Any phase -- can be addressed independently.

---

### Pitfall m3: No Rate Limiting on Save/Build Endpoints

**What goes wrong:** A misbehaving client (buggy autosave, accidental rapid clicks, or intentional abuse) floods the save or build endpoint, creating excessive database writes or (when sandbox creation is implemented) spawning many game objects rapidly.

**Prevention:**
- Add rate limiting via Django middleware or a decorator (e.g., `django-ratelimit`).
- Debounce autosave on the frontend (minimum 5-second interval).
- Add a cooldown to the build endpoint (e.g., one build per project per 60 seconds).

**Confidence:** MEDIUM -- no rate limiting observed in current code, but the impact depends on traffic patterns.

**Phase relevance:** Sandbox Creation phase -- most important when build endpoint actually creates game objects.

---

### Pitfall m4: Lock String Sanitization Allows Overly Permissive Locks

**What goes wrong:** The current `sanitize_lock()` function (`exporter.py:46-54`) allows alphanumeric characters, parentheses, colons, ampersands, pipes, underscores, and spaces. This permits lock strings like `traverse:all()` which makes an exit universally traversable, or `control:id(1)` which grants control to the superuser. A builder could craft lock strings that bypass intended access controls.

**Prevention:**
- Validate lock strings against a whitelist of allowed lock functions (e.g., only `perm()`, `pperm()`, `attr()`, `tag()`, `id()`), not just allowed characters.
- Reject lock strings that contain `all()` unless the builder has explicit permission.
- Validate that lock string patterns match expected forms (e.g., `locktype:lockfunc(args)`) using a proper parser, not just character filtering.

**Confidence:** MEDIUM -- the sanitization prevents special character injection but does not validate semantic content.

**Phase relevance:** Sandbox Creation phase -- when locks start being applied to real game objects.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Severity | Mitigation |
|-------------|---------------|----------|------------|
| Builder Editor (saving) | C2: JSONField race conditions | Critical | Add version field, optimistic concurrency |
| Builder Editor (schema) | M6: Schema drift | Moderate | Define JSON schema, validate on save |
| Sandbox Creation | C1: Thread-unsafe object creation | Critical | Use `run_in_main_thread()` service layer |
| Sandbox Creation | C4: Sandbox leaks into live world | Critical | SandboxRoom typeclass + traverse locks |
| Sandbox Creation | M4: No undo/rollback | Moderate | Build manifest pattern |
| Sandbox Creation | M5: @reload required for exits | Moderate | Force cmdset update after exit creation |
| Trigger Editor | C3: Arbitrary code execution | Critical | Whitelist trigger actions, no eval/exec |
| Approval Queue | M2: Double-action race condition | Moderate | Atomic state transitions |
| Promotion | C5: Broken exit connections | Critical | Two-phase promotion with mapping + validation |
| All mutation endpoints | M1: CSRF disabled | Moderate | Remove csrf_exempt, send token in headers |
| All phases | m3: No rate limiting | Minor | Add rate limiting middleware |

---

## Sources

### Verified Against Source Code (HIGH Confidence)
- `evennia/utils/utils.py:2862-2877` -- `run_in_main_thread()` implementation
- `evennia/objects/objects.py:1535-1584` -- `DefaultObject.delete()` and cleanup behavior
- `evennia/objects/objects.py:3352-3430` -- `DefaultRoom.create()` implementation
- `evennia/objects/objects.py:3516-3595` -- `DefaultExit` and `create_exit_cmdset()`
- `evennia/objects/objects.py:1336-1345` -- `clear_exits()` implementation
- `beckonmu/web/builder/exporter.py` -- current batch script generation
- `beckonmu/web/builder/views.py` -- current views with `csrf_exempt` decorators
- `beckonmu/web/builder/models.py` -- `BuildProject` model with JSONField
- `beckonmu/web/builder/validators.py` -- current validation (connectivity only)

### Official Documentation (MEDIUM-HIGH Confidence)
- [Evennia Batch Command Processor](https://www.evennia.com/docs/latest/Components/Batch-Command-Processor.html) -- batch script security model
- [Evennia REST API](https://www.evennia.com/docs/latest/Components/Web-API.html) -- API authentication and permissions
- [Evennia Webserver Architecture](https://www.evennia.com/docs/latest/Components/Webserver.html) -- WSGI threading model
- [Evennia Typeclasses and Idmapper](https://www.evennia.com/docs/latest/Components/Typeclasses.html) -- cache behavior
- [Evennia Security Practices](https://www.evennia.com/docs/3.x/Setup/Security-Practices.html) -- injection risks

### Community/Search (MEDIUM Confidence)
- [Django Forum: JSONField race conditions](https://forum.djangoproject.com/t/preventing-race-conditions-when-updating-jsonfield/19935) -- F() expressions do not work with JSONField
- [Django race condition techniques](https://medium.com/@anas-issath/how-to-avoid-race-conditions-in-django-10-proven-techniques-29645d7311b4) -- select_for_update, optimistic concurrency
- [Evennia idmapper discussion](https://groups.google.com/g/evennia/c/rXwRqwxgAKc/m/d0XdC_PDl2cJ) -- memory and cache concerns

### Training Knowledge (Requiring Validation)
- MUD trigger system vulnerability patterns (DGScripts, MobProgs, LPC) -- LOW confidence, based on general domain knowledge
- Exit cmdset cache invalidation behavior after programmatic creation -- MEDIUM-LOW confidence, needs empirical testing
