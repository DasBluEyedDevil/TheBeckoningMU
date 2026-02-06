# Architecture Patterns: Web Builder Portal Systems

**Domain:** MUD web portal -- approval queues, sandbox building, live promotion, triggers, compass UI
**Researched:** 2026-02-03
**Confidence:** HIGH (based on direct codebase analysis + verified Evennia official documentation)

## Executive Summary

The five subsystems under investigation (approval queues, sandbox building, live promotion, triggers, compass exits) all share a common architectural challenge: bridging Django web state with Evennia game state. The existing codebase already has the skeleton for this bridge -- `BuildProject.map_data` stores web-side JSON, `exporter.py` converts to batch commands, `builder.py` commands handle in-game promotion/abandonment. The gap is that these bridges are currently manual (export a file, run it in-game) rather than automated (web action creates game objects directly).

The recommended architecture uses **direct Evennia API calls from Django views** (`evennia.create_object()`, `evennia.create_script()`) instead of batch command generation. This avoids the fundamental limitation that Evennia's batch command processor has no Python API for programmatic execution -- it requires an in-game session to run commands.

## Recommended Architecture

```
+------------------------------------------------------------------+
|                    WEB LAYER (Django Views)                       |
|                                                                   |
|  Dashboard  -->  Editor  -->  Approval Queue  -->  Sandbox Mgmt  |
|  (list)         (map_data)   (staff review)       (build/promote)|
+------------------------------------------------------------------+
        |               |              |                  |
        v               v              v                  v
+------------------------------------------------------------------+
|                 BUILDER API LAYER (Django Views)                  |
|                                                                   |
|  SaveProject   GetProject   SubmitForApproval   BuildToSandbox   |
|  DeleteProject ExportProject ApproveProject     PromoteToLive    |
+------------------------------------------------------------------+
        |                              |                  |
        v                              v                  v
+------------------------------------------------------------------+
|               DATA LAYER (Django Models)                         |
|                                                                   |
|  BuildProject  -->  BuildApproval  -->  SandboxMapping           |
|  (map_data JSON)   (status, notes)     (web_id -> evennia_dbref) |
|  RoomTemplate                                                    |
+------------------------------------------------------------------+
        |                                                 |
        v                                                 v
+------------------------------------------------------------------+
|              BRIDGE LAYER (Python module)                         |
|                                                                   |
|  sandbox_builder.py                                               |
|  - create_sandbox_from_project(project) -> room_dbrefs           |
|  - promote_sandbox_to_live(project, connection_room) -> success  |
|  - destroy_sandbox(project) -> success                           |
|  - create_trigger_scripts(room, trigger_data) -> script_dbrefs   |
+------------------------------------------------------------------+
        |                                                 |
        v                                                 v
+------------------------------------------------------------------+
|              EVENNIA LAYER (Typeclass System)                     |
|                                                                   |
|  Room (typeclasses.rooms.Room)                                   |
|  Exit (typeclasses.exits.Exit)                                   |
|  Script (typeclasses.scripts.Script)                             |
|  - TriggerScript subclasses (entry, timed, interaction)          |
|  Tags: web_builder, project_{id}, sandbox, promoted              |
+------------------------------------------------------------------+
```

### Component Boundaries

| Component | Responsibility | Communicates With | Implementation |
|-----------|---------------|-------------------|----------------|
| **Editor Frontend** | Visual map editing, compass assignment, trigger config | Builder API (fetch/save JSON) | Vanilla JS in editor.html |
| **Builder API Views** | CRUD for projects, approval submission, build/promote triggers | Data Layer (Django ORM), Bridge Layer | Django views in builder/views.py |
| **BuildProject Model** | Store map_data JSON, project metadata, lifecycle state | Django ORM only | builder/models.py |
| **BuildApproval Model** | Track approval state, reviewer, notes, timestamps | Django ORM only | builder/models.py (new) |
| **SandboxMapping** | Map web room IDs to Evennia dbrefs after sandbox creation | Django ORM only | builder/models.py (new) or JSON on BuildProject |
| **Bridge Layer** | Convert web data to Evennia objects using `create_object`/`create_script` | Evennia API directly | builder/sandbox_builder.py (new) |
| **TriggerScript** | Execute game logic on events (entry, timer, interaction) | Evennia Script system | typeclasses/scripts.py (new subclasses) |
| **Compass Logic** | Compute exit names/aliases from compass direction + spatial position | Editor frontend (pure JS calculation) | editor.html JS |

### Data Flow

#### 1. Approval Queue Flow

```
Builder saves project
       |
       v
Builder clicks "Submit for Review"
       |
       v
API: SubmitForApprovalView
  - Validates project (validators.py)
  - Creates BuildApproval(status='pending')
  - Sets BuildProject status field
       |
       v
Staff opens Approval Dashboard
  - Fetches pending BuildApprovals
  - Reviews map_data (read-only editor view)
       |
       v
Staff clicks Approve/Reject
  - API: ApproveProjectView
  - Updates BuildApproval(status='approved', reviewer, notes)
       |
       v
Builder sees "Approved" status on dashboard
  - "Build to Sandbox" button now enabled
```

**Data direction:** Web Frontend --> Django API --> Django Models --> Web Frontend (poll/refresh)

**Key principle:** This mirrors the existing `CharacterApprovalAPI` pattern exactly. The traits app uses `CharacterBio.approved` boolean + `approved_by` + `approved_at`. The builder should use a similar pattern but with a dedicated `BuildApproval` model for richer state tracking (pending/approved/rejected/revision_requested).

#### 2. Sandbox Building Flow

```
Builder clicks "Build to Sandbox" (only available after approval)
       |
       v
API: BuildToSandboxView
  - Checks: approval status == 'approved'
  - Checks: no existing sandbox (project.sandbox_room_id is null)
       |
       v
Bridge: sandbox_builder.create_sandbox_from_project(project)
  1. Create sandbox container room:
     sandbox = evennia.create_object(
         typeclass="typeclasses.rooms.Room",
         key=f"Builder Sandbox: {project.name}",
         tags=[("web_builder", None), (f"project_{project.id}", None), ("sandbox", None)],
         attributes=[("desc", f"Sandbox for project: {project.name}")]
     )
  2. For each room in map_data["rooms"]:
     room = evennia.create_object(
         typeclass="typeclasses.rooms.Room",
         key=room_data["name"],
         location=sandbox,
         tags=[("web_builder", None), (f"project_{project.id}", None)],
         attributes=[
             ("desc", room_data["description"]),
             ("location_type", v5_data.get("location_type")),
             ...v5 attributes...
         ]
     )
     Store mapping: web_room_id -> room.dbref
  3. For each exit in map_data["exits"]:
     source_dbref = mapping[exit["source"]]
     target_dbref = mapping[exit["target"]]
     exit_obj = evennia.create_object(
         typeclass="typeclasses.exits.Exit",
         key=exit["name"],
         location=source_room,
         destination=target_room,
         aliases=exit.get("aliases", []),
         tags=[("web_builder", None), (f"project_{project.id}", None)]
     )
  4. For each room with triggers:
     create_trigger_scripts(room_obj, room_data["triggers"])
  5. Return sandbox.dbref
       |
       v
API updates:
  - project.sandbox_room_id = sandbox.dbref
  - Stores room mapping (web_id -> dbref) in project.map_data["_sandbox_mapping"]
       |
       v
Response to frontend with success + sandbox dbref
```

**Data direction:** Web Frontend --> Django API --> Bridge Layer --> Evennia `create_object` API --> Database

**Critical design decision:** Use `evennia.create_object()` directly, NOT batch command generation + execution. Reasons:
1. Batch command processor requires an in-game session -- no Python API for headless execution (verified via official docs)
2. `create_object()` returns the created object immediately, allowing us to build the dbref mapping
3. `create_object()` works from Django views because Evennia shares the same Django database
4. Error handling is straightforward (Python exceptions) vs. batch processor which "will not stop if commands fail"

#### 3. Live Promotion Flow

```
Builder opens approved+sandboxed project
  - Sees "Promote to Live" button
  - Must specify connection point (existing game room + exit direction)
       |
       v
Frontend: Promotion dialog
  - Search for target room (by name or dbref)
  - Select exit direction from sandbox entry room to target
  - Select exit direction from target room back to sandbox entry
       |
       v
API: PromoteToLiveView
  - Validates: project is approved + has sandbox
  - Validates: target room exists and caller has permission
       |
       v
Bridge: sandbox_builder.promote_sandbox_to_live(project, target_room, exit_config)
  1. Find all rooms tagged with project_{id}
  2. Remove "sandbox" tag from all rooms
  3. Add "promoted" tag to all rooms
  4. Move rooms out of sandbox container:
     For each room in sandbox.contents:
       room.location = None  (rooms have no location normally)
  5. Create connecting exits:
     - Exit from target_room to project entry room (named per exit_config)
     - Exit from project entry room to target_room (return path)
  6. Delete empty sandbox container
  7. Update BuildProject:
     project.sandbox_room_id = None
     project.promoted_at = timezone.now()
       |
       v
Response: success + list of promoted room dbrefs
```

**Data direction:** Web Frontend --> Django API --> Bridge Layer --> Evennia object manipulation --> Database

**Key subtlety:** When rooms are promoted, they need `location = None` because Evennia rooms by convention have no location (they ARE locations). The sandbox container is a temporary parent -- during sandbox mode, rooms live "inside" the container for isolation. On promotion, they become proper top-level rooms connected to the game world via exits.

**The existing `CmdPromote` command in `builder.py` has a bug:** It moves all contents from sandbox to destination, but rooms should not have a location after promotion. The web-based promotion should set `room.location = None` for each room rather than moving them to another container.

#### 4. Trigger System Flow

```
Editor Frontend: Trigger configuration panel
  - User selects trigger type (entry, timed, interaction)
  - Configures trigger parameters
  - Trigger data stored in room's map_data
       |
       v
map_data["rooms"][id]["triggers"] = [
  {
    "type": "entry",
    "event": "on_enter",          // or "on_exit"
    "action": "message",          // action type
    "message": "A chill runs...", // action parameter
    "target": "character",        // who receives
    "conditions": {...}           // optional conditions
  },
  {
    "type": "timed",
    "interval": 300,              // seconds
    "action": "message",
    "message": "Wind howls...",
    "target": "room"
  },
  {
    "type": "interaction",
    "verb": "look",               // triggering verb
    "object_name": "statue",      // what they interact with
    "action": "message",
    "message": "The statue's eyes..."
  }
]
       |
       v
Bridge: create_trigger_scripts(room_obj, trigger_list)
  For each trigger:
    If type == "entry":
      - No Script needed -- implement via Room.at_object_receive() hook
      - Store trigger config as room attribute: room.db.entry_triggers = [...]
      - Room typeclass checks room.db.entry_triggers in at_object_receive()

    If type == "timed":
      - Create Script:
        script = evennia.create_script(
            typeclass="typeclasses.scripts.TimedTriggerScript",
            key=f"trigger_{room.dbref}_{index}",
            obj=room_obj,
            interval=trigger["interval"],
            persistent=True,
            attributes=[("trigger_config", trigger)]
        )

    If type == "interaction":
      - Store as room attribute: room.db.interaction_triggers = [...]
      - Room typeclass checks these in relevant hooks (at_look, custom verbs)
```

**Architecture decision: Hybrid approach for triggers.**
- **Entry/Exit triggers:** Room attributes checked in typeclass hooks. No Script overhead. The Room.at_object_receive() and Room.at_object_leave() hooks are the natural attachment points.
- **Timed triggers:** Evennia Scripts with interval. Scripts are designed exactly for this -- periodic execution attached to an object.
- **Interaction triggers:** Room attributes checked in command hooks or Room.return_appearance(). For "look at object" triggers, override get_display_things() or hook into the look command.

This avoids creating a Script for every trigger type (which would be expensive for entry/exit triggers that fire synchronously) while using Scripts where their timer functionality is genuinely needed.

#### 5. Compass Direction Assignment Flow

```
Editor Frontend: Compass mode activated
       |
       v
User selects an exit line in the editor
       |
       v
Compass rose widget appears:
  [NW] [N] [NE]
  [W]  [*] [E]
  [SW] [S] [SE]
  [U]      [D]
       |
       v
User clicks direction (e.g., "N")
       |
       v
JS logic:
  - Sets exit.name to canonical name ("North")
  - Sets exit.aliases to standard aliases (["north", "n"])
  - Updates visual: arrow/line gains direction indicator
  - Stores in map_data: exit.direction = "north"
       |
       v
On export/build:
  - Exit created with name "North" and alias ["north", "n"]
  - This is standard MUD convention -- no special Evennia config needed
```

**Direction mapping (constant in JS and Python):**

```javascript
const COMPASS_DIRECTIONS = {
    "n":  { name: "North",     aliases: ["north", "n"],     reverse: "s"  },
    "ne": { name: "Northeast", aliases: ["northeast", "ne"], reverse: "sw" },
    "e":  { name: "East",      aliases: ["east", "e"],      reverse: "w"  },
    "se": { name: "Southeast", aliases: ["southeast", "se"], reverse: "nw" },
    "s":  { name: "South",     aliases: ["south", "s"],     reverse: "n"  },
    "sw": { name: "Southwest", aliases: ["southwest", "sw"], reverse: "ne" },
    "w":  { name: "West",      aliases: ["west", "w"],      reverse: "e"  },
    "nw": { name: "Northwest", aliases: ["northwest", "nw"], reverse: "se" },
    "u":  { name: "Up",        aliases: ["up", "u"],        reverse: "d"  },
    "d":  { name: "Down",      aliases: ["down", "d"],      reverse: "u"  }
};
```

**Compass logic is purely frontend.** No special backend support needed. The compass widget sets exit name + aliases according to the standard direction convention. Evennia treats exits as objects with a name (the command to traverse) and aliases. Naming an exit "North" with alias "n" is the universal MUD pattern for compass navigation.

**Auto-reverse:** When user assigns direction "N" to an exit from Room A to Room B, the editor should automatically create the reverse exit from Room B to Room A with direction "S" (if it does not already exist). This is the MUD convention that `@dig` and `@tunnel` follow.

**Spatial validation:** The compass rose should validate that direction assignments are spatially consistent with the visual grid. If Room B is visually to the right of Room A, the exit from A to B should be "East" (or similar). The editor can suggest directions based on relative grid positions but should allow manual override.

## Patterns to Follow

### Pattern 1: Direct Evennia API from Django Views

**What:** Use `evennia.create_object()`, `evennia.create_script()`, `evennia.search_tag()` directly in Django view code instead of generating batch scripts.

**When:** Any time the web interface needs to create, modify, or query game objects.

**Why:** Evennia and Django share the same database and process. The creation functions are standard Python calls that work from any context.

**Confidence:** HIGH -- verified from official Evennia docs (`evennia.utils.create` API)

**Example:**
```python
# In builder/sandbox_builder.py
import evennia

def create_sandbox_room(project, room_data):
    """Create a single room from web builder data."""
    room = evennia.create_object(
        typeclass="typeclasses.rooms.Room",
        key=room_data["name"],
        tags=[
            ("web_builder", None),
            (f"project_{project.id}", None),
        ],
        attributes=[
            ("desc", room_data.get("description", "")),
            ("location_type", room_data.get("v5", {}).get("location_type", "")),
            ("danger_level", room_data.get("v5", {}).get("danger_level", "safe")),
        ]
    )
    return room
```

### Pattern 2: Tag-Based Object Grouping

**What:** Use Evennia tags to group all objects belonging to a build project, enabling bulk operations (find all rooms in project, delete sandbox, promote).

**When:** Any operation that needs to find "all objects related to this project."

**Why:** Evennia's `search_tag()` returns Django QuerySets, enabling efficient bulk queries. Tags are the idiomatic Evennia way to group objects.

**Confidence:** HIGH -- verified from official Evennia Tags documentation

**Example:**
```python
# Find all rooms in a project
project_rooms = evennia.search_tag(f"project_{project_id}", category=None)

# Find all sandbox rooms specifically
sandbox_rooms = evennia.search_tag("sandbox")
```

### Pattern 3: Mirror Character Approval Pattern

**What:** Model the builder approval workflow identically to the existing character approval workflow.

**When:** Building the approval queue feature.

**Why:** The codebase already has a working approval pattern (`CharacterApprovalAPI`, `PendingCharactersAPI`, `character_approval.html`). Reusing this pattern means consistent UX and reduces architectural risk.

**Confidence:** HIGH -- based on direct codebase analysis of existing `traits/api.py`

**Example pattern to follow:**
```
traits/api.py: PendingCharactersAPI.get()   -->  builder: PendingProjectsView.get()
traits/api.py: CharacterDetailAPI.get()     -->  builder: ProjectDetailView.get() (read-only editor)
traits/api.py: CharacterApprovalAPI.post()  -->  builder: ApproveProjectView.post()
character_approval.html (sidebar + detail)  -->  builder: approval_dashboard.html (sidebar + map preview)
```

### Pattern 4: Hybrid Trigger Architecture

**What:** Use Room attributes for synchronous triggers (entry/exit, interaction) and Scripts for asynchronous triggers (timed).

**When:** Implementing the trigger system.

**Why:** Entry triggers fire when a character enters a room -- this is a synchronous hook (`at_object_receive`). Creating a Script for every room with an entry trigger would be wasteful. Timed triggers genuinely need Scripts because they fire on an interval independent of player action.

**Confidence:** HIGH -- based on Evennia Script documentation confirming Scripts are designed for timer-based behavior

### Pattern 5: ID Mapping via Project Metadata

**What:** Store the mapping between web editor room IDs (e.g., "r1", "r2") and Evennia dbrefs (e.g., #45, #46) in the BuildProject model after sandbox creation.

**When:** After sandbox building, and during promotion, so the system knows which Evennia objects correspond to which web editor elements.

**Why:** The web editor uses its own ID scheme (sequential IDs within map_data). After `create_object()` creates real Evennia objects, we need to track which is which for updates, rebuilds, and promotions.

**Example storage:**
```python
# After sandbox build, store mapping
project.map_data["_sandbox_mapping"] = {
    "r1": 45,  # web room ID -> Evennia dbref
    "r2": 46,
    "r3": 47,
    "sandbox_container": 44,
}
project.save()
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Batch Script Execution from Web

**What:** Generating .ev batch scripts and trying to execute them programmatically.

**Why bad:** Evennia's batch command processor requires an in-game session (a puppeted character executing `@batchcommand`). There is no Python API to run batch commands headlessly. Attempting to simulate this would require creating a fake session or scripting through the command handler -- fragile, hard to debug, and the batch processor itself "will not stop if commands fail."

**Instead:** Use `evennia.create_object()` and `evennia.create_script()` directly. These are clean Python APIs that return created objects, support error handling, and work from any Python context.

**Confidence:** HIGH -- verified via Evennia batch processor documentation which states no programmatic API exists

### Anti-Pattern 2: Room-as-Container for Promoted Areas

**What:** Keeping promoted rooms inside a container room (as the current `CmdPromote` does with `obj.move_to(dest)`).

**Why bad:** Evennia rooms by convention have `location = None`. A room inside another room breaks the room/exit navigation model. Players would need to traverse into the container first, then into rooms inside it. The room topology becomes nested rather than flat.

**Instead:** On promotion, set `room.location = None` for each project room, then create exits connecting the project's entry room to the target live game room. This makes promoted rooms first-class citizens in the game world topology.

### Anti-Pattern 3: Separate Script Per Trigger

**What:** Creating an Evennia Script for every trigger type (entry, exit, timed, interaction).

**Why bad:** Scripts have persistent database entries and lifecycle overhead. Entry triggers fire synchronously when a character enters a room -- this is already handled by the `at_object_receive()` hook. Creating a Script that watches for entries would duplicate existing functionality and add overhead.

**Instead:** Use Room typeclass hooks for synchronous events (entry/exit/interaction) with trigger config stored as room attributes. Use Scripts only for timed triggers that genuinely need interval-based execution.

### Anti-Pattern 4: Compass Logic in Backend

**What:** Building compass direction resolution and spatial validation on the server side.

**Why bad:** Compass direction assignment is a visual editing operation. The grid positions are in the web editor's coordinate space. Pushing this logic to the backend would require round-trips for every direction change and would duplicate grid-awareness between frontend and backend.

**Instead:** Keep compass logic entirely in the frontend JavaScript. The backend receives exit data with name/aliases already set to the correct direction. The backend does not need to know or validate compass directions -- it just creates exits with whatever name the builder specified.

### Anti-Pattern 5: Approval Gate on Every Operation

**What:** Requiring re-approval every time a project is modified after initial approval.

**Why bad:** Builders iterate. If every save resets approval status, the workflow becomes painfully slow. Builders would be afraid to fix typos.

**Instead:** Approval gates should exist at two transition points only: (1) Draft -> Ready for Review (builder submits), and (2) Approved -> Built to Sandbox (builder triggers build). After sandbox creation, changes to map_data should be flagged as "out of sync with sandbox" but not require re-approval for minor edits. Significant changes (adding/removing rooms) should require a sandbox rebuild (which destroys the old sandbox first).

## Model Changes Required

### New/Modified Models

```python
# builder/models.py additions

class BuildProject(models.Model):
    # Existing fields stay...

    # NEW: Status tracking
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision_requested', 'Revision Requested'),
        ('sandboxed', 'Built to Sandbox'),
        ('promoted', 'Promoted to Live'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # NEW: Connection point for promotion
    # Stored as dbref int of the room to connect to when promoting
    connection_room_id = models.IntegerField(null=True, blank=True)
    connection_exit_direction = models.CharField(max_length=10, blank=True, default='')


class BuildApproval(models.Model):
    """Tracks review history for a build project."""
    project = models.ForeignKey(BuildProject, on_delete=models.CASCADE, related_name='approvals')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # 'approved', 'rejected', 'revision_requested'
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "builder"
        ordering = ["-created_at"]
```

### New API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `builder/api/submit/<pk>/` | POST | Submit project for review |
| `builder/api/pending/` | GET | List pending projects (staff) |
| `builder/api/project/<pk>/review/` | GET | Get project data for review (staff) |
| `builder/api/project/<pk>/approve/` | POST | Approve/reject project (staff) |
| `builder/api/build/<pk>/` | POST | Build approved project to sandbox |
| `builder/api/promote/<pk>/` | POST | Promote sandbox to live |
| `builder/api/abandon/<pk>/` | POST | Destroy sandbox |

## Build Order (Dependencies)

The subsystems have clear dependency ordering:

```
Phase 1: Model Changes + Approval Queue
  - Add status field to BuildProject
  - Add BuildApproval model
  - Add approval API endpoints
  - Add approval dashboard UI
  - NO dependency on sandbox/promotion/triggers

Phase 2: Sandbox Building (Bridge Layer)
  - Create sandbox_builder.py module
  - Implement create_sandbox_from_project()
  - Wire BuildToSandboxView to use bridge instead of batch export
  - DEPENDS ON: Phase 1 (approval must be approved before build)

Phase 3: Live Promotion
  - Implement promote_sandbox_to_live() in bridge
  - Add promotion dialog in frontend (room search, direction selection)
  - Wire PromoteToLiveView
  - DEPENDS ON: Phase 2 (must have sandbox to promote)

Phase 4: Trigger System
  - Define TriggerScript typeclasses
  - Implement trigger config UI in editor
  - Integrate trigger creation into sandbox builder
  - Room typeclass hooks for entry/interaction triggers
  - CAN be developed in parallel with Phase 3 (independent)
  - DEPENDS ON: Phase 2 (triggers created during sandbox build)

Phase 5: Compass Rose
  - Implement compass direction widget in editor JS
  - Auto-reverse exit creation logic
  - Spatial suggestion based on grid position
  - NO backend dependency (pure frontend)
  - CAN be developed in parallel with Phases 2-4
```

**Critical path:** Phase 1 -> Phase 2 -> Phase 3 (linear dependency)

**Parallelizable:** Phase 5 can start immediately. Phase 4 can start alongside Phase 3 after Phase 2 is complete.

## Scalability Considerations

| Concern | At 10 builders | At 100 builders | At 500 builders |
|---------|---------------|-----------------|-----------------|
| Project storage | JSON blobs fine | JSON blobs fine | May need map_data size limits |
| Sandbox rooms | ~100 rooms | ~1000 rooms | Tag-based queries need indexing |
| Trigger scripts | ~50 scripts | ~500 scripts | Script count affects server reload time |
| Approval queue | Simple list | Pagination needed | Category/priority filtering |
| Simultaneous builds | Sequential fine | Async task queue recommended | Async task queue required |

**Note:** For this MUD's expected scale (tens of builders, not hundreds), the synchronous approach in Django views is fine. If sandbox building takes more than a few seconds (large projects with many rooms), consider wrapping the bridge calls in Django's `async` views or a background task, but this is an optimization -- not a requirement for initial implementation.

## Sources

- **Evennia `create_object` API:** https://www.evennia.com/docs/latest/api/evennia.utils.create.html [HIGH confidence -- official docs]
- **Evennia Script system:** https://www.evennia.com/docs/latest/Components/Scripts.html [HIGH confidence -- official docs]
- **Evennia Tags system:** https://www.evennia.com/docs/latest/Components/Tags.html [HIGH confidence -- official docs]
- **Evennia Batch Processor:** https://www.evennia.com/docs/latest/Components/Batch-Command-Processor.html [HIGH confidence -- official docs, confirms no Python API]
- **Evennia Prototypes/Spawner:** https://www.evennia.com/docs/latest/Components/Prototypes.html [HIGH confidence -- official docs]
- **Evennia Building Quickstart:** https://www.evennia.com/docs/latest/Howtos/Beginner-Tutorial/Part1/Beginner-Tutorial-Building-Quickstart.html [HIGH confidence -- official docs]
- **Existing codebase analysis:** Direct reading of `builder/models.py`, `builder/views.py`, `builder/exporter.py`, `commands/builder.py`, `traits/api.py`, `typeclasses/*.py` [HIGH confidence -- primary source]
