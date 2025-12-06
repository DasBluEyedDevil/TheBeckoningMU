# Web Builder Design Document

**Date:** 2025-12-06
**Status:** Approved
**Author:** Claude Code (Brainstorming Session)

## Overview

A web-based visual builder for creating MUSH areas. Provides a grid/graph paper interface where staff builders can map rooms, configure exits, add objects, and set V5-specific attributes. Built areas are staged in a sandbox for verification before promotion to the live game world.

## Target Users

**Staff/Builders only** - Trusted users with `is_staff` permission who already understand MUSH building concepts. No approval workflow needed for the builder itself.

## Scope

Full building suite:
- Rooms with descriptions and V5 attributes
- Exits with aliases, descriptions, and locks
- Objects (prototype-based and custom)
- Basic triggers (no custom code)
- Project saving and shared viewing

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Grid Canvas │  │  Sidebar    │  │  Toolbar        │  │
│  │ (rooms/     │  │  (property  │  │  (save/load/    │  │
│  │  exits)     │  │   editor)   │  │   build/export) │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │ REST API
┌───────────────────────────┼─────────────────────────────┐
│                    Django Backend                       │
│  ┌─────────────┐  ┌───────┴─────┐  ┌─────────────────┐  │
│  │ Models      │  │ API Views   │  │ Batch Generator │  │
│  │ (projects,  │  │ (CRUD,      │  │ (JSON → .ev     │  │
│  │  templates) │  │  execute)   │  │  script)        │  │
│  └─────────────┘  └─────────────┘  └────────┬────────┘  │
└─────────────────────────────────────────────┼───────────┘
                                              │
┌─────────────────────────────────────────────┼───────────┐
│                 Evennia Game Server                     │
│  ┌─────────────────┐  ┌─────────────────────┴─────────┐ │
│  │ Builder Sandbox │  │ @batchcommand processor       │ │
│  │ (staging zone)  │  │ (executes .ev scripts)        │ │
│  └─────────────────┘  └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. Builder creates/edits project in browser → saved as JSON to Django
2. Builder clicks "Build" → Django generates `.ev` script → Evennia executes in Sandbox
3. Builder verifies in-game → promotes to final location via command

---

## Data Models

### Django Models

**BuildProject** - Main project container:
```python
class BuildProject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    map_data = models.JSONField(default=dict)
    is_public = models.BooleanField(default=True)  # Visible to other builders
    sandbox_room_id = models.IntegerField(null=True, blank=True)
    promoted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**RoomTemplate** - Reusable room templates:
```python
class RoomTemplate(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    template_data = models.JSONField(default=dict)
    is_shared = models.BooleanField(default=False)
```

### V5 Location Constants

New file: `beckonmu/world/v5_locations.py`

```python
LOCATION_TYPES = [
    ("haven", "Haven"),
    ("elysium", "Elysium"),
    ("rack", "Rack (Feeding Ground)"),
    ("hostile", "Hostile Territory"),
    ("neutral", "Neutral Ground"),
    ("mortal", "Mortal Establishment"),
    ("supernatural", "Supernatural Site"),
]

DAY_NIGHT_ACCESS = [
    ("always", "Always Accessible"),
    ("day_only", "Day Only (Mortals)"),
    ("night_only", "Night Only"),
    ("restricted", "Restricted Access"),
]

DANGER_LEVELS = [
    ("safe", "Safe"),
    ("low", "Low Risk"),
    ("moderate", "Moderate Risk"),
    ("high", "High Risk"),
    ("deadly", "Deadly"),
]

HAVEN_RATINGS = [
    "security",
    "size",
    "luxury",
    "warding",
    "location_hidden",
]
```

### map_data JSON Structure

```json
{
  "rooms": {
    "r1": {
      "name": "Club Entrance",
      "description": "Heavy bass thumps through the reinforced door...",
      "grid_x": 2,
      "grid_y": 3,
      "tags": ["ooc"],
      "v5": {
        "location_type": "rack",
        "day_night": "night_only",
        "danger_level": "low",
        "hunting_modifier": -1,
        "territory_owner": null,
        "haven_ratings": null
      },
      "triggers": [
        {
          "event": "on_enter",
          "action": "message",
          "params": {"text": "The bouncer eyes you..."}
        }
      ],
      "builder_notes": "Main entry point for the district"
    }
  },
  "exits": {
    "e1": {
      "name": "north",
      "aliases": ["n"],
      "source": "r1",
      "target": "r2",
      "description": "A velvet rope blocks the way.",
      "locks": "traverse:all()",
      "tags": []
    }
  },
  "objects": {
    "o1": {
      "room": "r1",
      "prototype": "BARSTOOL",
      "name": "worn barstool",
      "description": "Leather with cigarette burns.",
      "custom_attrs": {}
    },
    "o2": {
      "room": "r1",
      "prototype": null,
      "typeclass": "typeclasses.objects.Object",
      "name": "neon sign",
      "description": "Flickering red neon.",
      "custom_attrs": {"powered": true}
    }
  }
}
```

**Haven ratings sub-structure** (when `location_type` is "haven"):
```json
"haven_ratings": {
  "security": 2,
  "size": 1,
  "luxury": 0,
  "warding": 0,
  "location_hidden": true
}
```

---

## Frontend Interface

### Layout

```
┌────────────────────────────────────────────────────────────────┐
│  [Project: Downtown District ▼]  [Save] [Build to Sandbox] [⚙]│ ← Toolbar
├──────────────────────────────────────────┬─────────────────────┤
│                                          │ Properties Panel    │
│     ┌───┐       ┌───┐                    │                     │
│     │ R1├───────┤ R2│                    │ Room: Club Entrance │
│     └─┬─┘       └───┘                    │ ─────────────────── │
│       │                                  │ Name: [___________] │
│     ┌─┴─┐                                │ Desc: [___________] │
│     │ R3│                                │                     │
│     └───┘                                │ ▼ V5 Settings       │
│                                          │   Type: [Rack    ▼] │
│          Grid Canvas                     │   Access: [Night ▼] │
│    (dot grid background)                 │   Danger: [Low   ▼] │
│                                          │   Hunting: [-1____] │
│                                          │                     │
│    [+Room] [+Exit] [Compass Mode]        │ ▼ Triggers (1)      │
│                                          │   [+ Add Trigger]   │
│                                          │                     │
├──────────────────────────────────────────┴─────────────────────┤
│  Rooms: 3  │  Exits: 2  │  Objects: 5  │  Last saved: 2 min   │ ← Status
└────────────────────────────────────────────────────────────────┘
```

### Grid System

- Fixed grid snap (visual aid only - positions not exported to game)
- Rooms snap to grid intersections
- Dot grid background matching existing dark theme
- Rooms are abstract spaces - size/position is arbitrary

### Interaction Modes

1. **Select Mode** (default) - Click room/exit/object to edit properties
2. **Room Mode** - Click grid to place new room
3. **Exit Mode** - Click source room, click target room, creates exit
4. **Compass Mode** - Click room, click compass direction (N/S/E/W/NE/NW/SE/SW/U/D), auto-creates adjacent room with standard exit names

### Property Panel Sections

- **Basic** - Name, description, aliases
- **V5 Settings** - Location type, day/night access, danger level, hunting modifier, territory owner
- **Haven Ratings** - Only visible when location_type is "haven"
- **Triggers** - List with add/remove buttons
- **Objects** - List of objects in this room, click to edit
- **Builder Notes** - Private notes for the builder

---

## Trigger System

Basic triggers without custom code. Form-based configuration only.

### Available Events

| Event | Fires When |
|-------|------------|
| `on_enter` | Character enters the room |
| `on_exit` | Character leaves the room |
| `on_look` | Character looks at the room |
| `on_examine` | Character examines specific object |
| `on_time` | Specific in-game hour (e.g., sunset) |

### Available Actions

| Action | Effect | Parameters |
|--------|--------|------------|
| `message` | Display text to character | `text` |
| `message_room` | Display text to all in room | `text` |
| `reveal_exit` | Make hidden exit visible | `exit_id` |
| `hide_exit` | Make exit invisible | `exit_id` |
| `set_flag` | Set a flag on the character | `flag_name`, `value` |
| `check_flag` | Only proceed if flag matches | `flag_name`, `value` |

### Example Triggers

```json
{
  "triggers": [
    {
      "event": "on_enter",
      "action": "message",
      "params": {"text": "The smell of blood lingers here..."}
    },
    {
      "event": "on_examine",
      "target": "old painting",
      "action": "reveal_exit",
      "params": {"exit_id": "e5"}
    },
    {
      "event": "on_time",
      "params": {"hour": 6},
      "action": "message_room",
      "params": {"text": "Dawn light creeps through the cracks..."}
    }
  ]
}
```

---

## Batch Script Generation

The exporter converts JSON map data to Evennia `.ev` batch scripts.

### Critical Syntax Rules

- Every command MUST be separated by at least one `#` comment line
- Semicolons (`;`) separate name from aliases: `name;alias1;alias2`
- Colons (`:`) separate aliases from typeclass: `name;alias:typeclass.path`
- Temp aliases use format: `_bld_<project_id>_<room_id>`

### Generated Script Structure

```python
# Generated by BeckoningMU Web Builder
# Project: Downtown District
# Builder: staffname
# Date: 2025-12-06
#
# ─────────────────────────────────────
# PHASE 1 - Create sandbox container
#
@dig Builder Sandbox: Downtown District;_sandbox_42 : typeclasses.rooms.Room
#
@tel _sandbox_42
#
# ─────────────────────────────────────
# PHASE 2 - Create all rooms
#
@dig Club Entrance;_bld_42_r1 : typeclasses.rooms.Room
#
@desc _bld_42_r1 = Heavy bass thumps through the reinforced door...
#
@set _bld_42_r1/location_type = rack
#
@set _bld_42_r1/day_night = night_only
#
@set _bld_42_r1/danger_level = low
#
@set _bld_42_r1/hunting_modifier = -1
#
# ─────────────────────────────────────
# PHASE 3 - Create exits
#
@tel _bld_42_r1
#
@open north;n = _bld_42_r2
#
@desc north = A velvet rope blocks the way.
#
# ─────────────────────────────────────
# PHASE 4 - Create objects
#
@tel _bld_42_r1
#
@spawn BARSTOOL
#
# ─────────────────────────────────────
# PHASE 5 - Apply triggers
#
@set _bld_42_r1/triggers = [{"event": "on_enter", "action": "message", "params": {"text": "The bouncer eyes you..."}}]
#
# BUILD COMPLETE
```

### Security Measures

- All user input sanitized (no `;`, `@`, or unescaped newlines in strings)
- Descriptions wrapped in safe quoting
- Temp aliases prefixed with `_bld_<project_id>_` to prevent collision
- Builder identity tagged on all created objects

---

## Staged Workflow

### Stage 1: Build to Sandbox

1. Builder clicks "Build to Sandbox" in Web UI
2. Django generates `.ev` batch script
3. Script executed via Evennia's `@batchcommand`
4. Creates container room: `Builder Sandbox: <Project Name>`
5. All project rooms created inside container
6. Builder notified with sandbox room dbref
7. Project's `sandbox_room_id` field updated

### Stage 2: In-Game Verification

1. Builder uses `@tel` to visit sandbox
2. Walks through rooms, tests exits, checks descriptions
3. Can make minor in-game tweaks if needed
4. If major changes needed → return to Web Builder, rebuild

### Stage 3: Promote to Live

New in-game command:
```
@promote <sandbox_dbref> = <destination>
```

Example:
```
@promote #1234 = #567
```

This command:
1. Moves all rooms from sandbox container to destination
2. Updates project record (`sandbox_room_id` cleared, `promoted_at` set)
3. Deletes empty sandbox container
4. Logs promotion for audit

### Alternative: Abandon

```
@abandon <sandbox_dbref>
```

- Deletes all rooms in the sandbox
- Clears project's `sandbox_room_id`
- Project remains in Web Builder for future rebuilds

### Permissions

- Build to Sandbox: `is_staff`
- Promote to Live: `is_staff` + destination must be valid container
- Abandon: `is_staff` + must own the project

---

## Error Handling

### Build-Time Validation

| Check | Severity | Message |
|-------|----------|---------|
| Room with no exits | Warning | "Room 'X' has no exits - isolated room" |
| Exit to non-existent room | Block | "Exit 'north' targets missing room" |
| Duplicate room names | Warning | "Multiple rooms named 'X' - may cause confusion" |
| Empty description | Warning | "Room 'X' has no description" |
| Circular-only exits | Warning | "Room 'X' only accessible from itself" |

### Execution Failures

- If `@batchcommand` fails mid-script, partial builds may exist
- Web UI shows: "Build failed at step 23: [error]. Use @abandon to clean up."
- All failures logged with project ID and step number

### Project Conflicts

- Rebuilding while sandbox exists → prompt: "Existing sandbox found. Abandon and rebuild?"
- Two builders cannot edit same project (view-only sharing)

### Name Collision Prevention

- All temp aliases use `_bld_<project_id>_<room_id>` format
- Example: `_bld_42_r1` instead of just `_bld_r1`
- Prevents collision between concurrent builds by different builders

### Orphan Cleanup

- Nightly script scans for sandbox rooms older than 7 days
- Notifies owner: "Your sandbox 'X' is 7 days old. Promote or abandon?"
- Auto-abandon after 14 days with warning

---

## Collaboration Model

- **Personal projects** - Each builder has their own projects
- **Shared viewing** - Builders can view each other's public projects for reference/learning
- **No concurrent editing** - Only owner can edit; others view-only
- `is_public` flag controls visibility to other builders

---

## New Files Required

### Django App Structure

```
beckonmu/web/builder/
├── __init__.py
├── models.py          # BuildProject, RoomTemplate
├── views.py           # Dashboard, Editor, API views
├── urls.py            # URL routing
├── exporter.py        # JSON → .ev batch script generator
├── validators.py      # Build-time validation logic
└── admin.py           # Django admin integration
```

### Templates

```
beckonmu/web/templates/builder/
├── dashboard.html     # Project list
└── editor.html        # Main builder interface
```

### Other Files

- `beckonmu/world/v5_locations.py` - V5 location type constants
- `beckonmu/commands/builder.py` - `@promote`, `@abandon` commands
- `beckonmu/typeclasses/scripts.py` - RoomTrigger script class (extend existing)

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/builder/` | Dashboard - list projects |
| GET | `/builder/edit/` | Create new project |
| GET | `/builder/edit/<id>/` | Edit existing project |
| POST | `/builder/api/save/` | Save project (create or update) |
| GET | `/builder/api/project/<id>/` | Get project data |
| DELETE | `/builder/api/project/<id>/` | Delete project |
| POST | `/builder/api/build/<id>/` | Build project to sandbox |
| GET | `/builder/export/<id>/` | Download .ev file |
| GET | `/builder/api/prototypes/` | List available prototypes |
| GET | `/builder/api/templates/` | List room templates |

---

## Implementation Phases

### Phase 1: Foundation
- Create Django app structure
- Add BuildProject model with migrations
- Wire up URL routing
- Create empty dashboard template

### Phase 2: Core Editor
- Grid canvas with room drag-and-drop
- Room property sidebar (name, desc, attributes)
- Save/load project API endpoints
- Basic styling matching existing theme

### Phase 3: Exits & Connections
- Exit drawing between rooms (click-drag mode)
- Compass mode for quick room creation
- Exit property editing (name, aliases, description, locks)

### Phase 4: V5 Integration
- V5 location constants
- V5 settings panel in sidebar
- Haven ratings sub-panel
- Day/night access configuration

### Phase 5: Objects & Triggers
- Object placement within rooms
- Prototype selector
- Custom object creation
- Trigger system UI (events, actions, params)

### Phase 6: Export & Execute
- Batch script generator with proper sanitization
- Build to sandbox functionality
- `@promote` and `@abandon` commands
- Sandbox → live workflow

### Phase 7: Polish
- Builder permission checks
- Project versioning/history
- Shared viewing for other builders
- Help tooltips and documentation
- Orphan cleanup script

---

## Success Criteria

- Staff can create a 10-room area in under 30 minutes
- Generated batch scripts execute without errors
- Sandbox verification catches issues before live deployment
- Existing Evennia building knowledge transfers to web interface
- Dark theme matches existing character creation UI
