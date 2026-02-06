---
phase: 06-live-promotion
plan: 01
subsystem: api
tags: [evennia, django, promotion, sandbox, live-world]

# Dependency graph
requires:
  - phase: 05-sandbox-building
    plan: 02
    provides: Sandbox isolation, cleanup, and in-game commands
provides:
  - Connection point selection API for live world rooms
  - Thread-safe promotion engine that moves rooms from sandbox to live
  - Bidirectional exit creation between live world and promoted area
  - Automatic sandbox cleanup after successful promotion
  - Project status transition from 'built' to 'live'
  - Promotion UI modal with room picker and direction selector
affects:
  - Phase 7 (Trigger System - promoted rooms can have triggers)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Promotion engine using run_in_main_thread for thread-safe Evennia operations"
    - "Bidirectional exit creation with opposite direction mapping"
    - "Tag-based room filtering (remove 'sandbox' tag to promote)"
    - "Modal-based UI for complex multi-field operations"

key-files:
  created:
    - beckonmu/web/builder/promotion.py
    - beckonmu/web/builder/migrations/0004_buildproject_connection_fields.py
  modified:
    - beckonmu/web/builder/models.py
    - beckonmu/web/builder/views.py
    - beckonmu/web/builder/urls.py
    - beckonmu/web/templates/builder/dashboard.html
    - beckonmu/web/builder/sandbox_bridge.py
    - beckonmu/web/builder/sandbox_cleanup.py

key-decisions:
  - "Promotion moves rooms (removes 'sandbox' tag) rather than copying - preserves dbrefs and V5 attributes"
  - "Connection room selection returns all non-sandbox rooms (ownership filter can be added later)"
  - "Bidirectional exits created automatically - forward from live room, return from project entry"
  - "Entry room determined by lowest room ID (simple heuristic, can be enhanced)"
  - "Promotion preserves sandbox on failure - allows retry without rebuilding"

patterns-established:
  - "Promotion workflow: validate -> promote in main thread -> cleanup -> update status"
  - "Direction mapping dictionary for opposite directions (n<->s, ne<->sw, etc.)"
  - "Graceful degradation - promotion can succeed even if cleanup fails"

# Metrics
duration: 8min
completed: 2026-02-05
---

# Phase 6 Plan 1: Live Promotion Summary

**Thread-safe promotion engine that moves sandbox builds to live world with bidirectional exit creation and automatic cleanup**

## Performance

- **Duration:** 8 min
- **Started:** 2026-02-05T21:13:49Z
- **Completed:** 2026-02-05T21:21:49Z
- **Tasks:** 3/3
- **Files modified:** 8

## Accomplishments

- Created `beckonmu/web/builder/promotion.py` with thread-safe promotion engine:
  - `_do_promotion_in_main_thread`: Finds sandbox rooms, validates connection, removes 'sandbox' tags, creates bidirectional exits
  - `promote_project_to_live`: Validates project, calls promotion engine, cleans up sandbox, updates status to 'live'
  - `_get_opposite_direction`: Maps directions for return exit creation
- Added connection point fields to BuildProject model (connection_room_id, connection_direction)
- Created migration 0004_buildproject_connection_fields.py
- Added API endpoints:
  - `GET /builder/api/connection-rooms/` - Lists all live world rooms (non-sandbox)
  - `POST /builder/api/build/{id}/promote/` - Triggers promotion with room_id and direction
- Added promotion UI to dashboard:
  - "Promote to Live" button visible when project.status == 'built'
  - Modal with room picker (populated from API) and direction dropdown
  - Warning message about irreversible action
  - Success/error handling with page reload
- Fixed run_in_main_thread import in sandbox_bridge.py and sandbox_cleanup.py (changed from evennia.server.sessionhandler to evennia.utils.utils)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add connection point fields to BuildProject model** - `eaf3218` (feat)
2. **Task 2: Create promotion engine module** - `50eb619` (feat)
3. **Task 3: Add promotion API endpoints and UI integration** - `4654be2` (feat)

**Plan metadata:** [pending]

## Files Created/Modified

- `beckonmu/web/builder/promotion.py` - Thread-safe promotion engine with room moving and exit creation
- `beckonmu/web/builder/migrations/0004_buildproject_connection_fields.py` - Migration for connection_room_id and connection_direction fields
- `beckonmu/web/builder/models.py` - Added connection point fields to BuildProject
- `beckonmu/web/builder/views.py` - Added ListConnectionRoomsView and PromoteProjectView
- `beckonmu/web/builder/urls.py` - Added URL patterns for promotion endpoints
- `beckonmu/web/templates/builder/dashboard.html` - Added promotion button and modal with room picker
- `beckonmu/web/builder/sandbox_bridge.py` - Fixed run_in_main_thread import
- `beckonmu/web/builder/sandbox_cleanup.py` - Fixed run_in_main_thread import

## Decisions Made

- **Promotion moves rooms (not copies)**: Removes 'sandbox' tag to make rooms live, preserving all V5 attributes and dbrefs
- **Entry room selection**: Uses room with lowest ID as entry point (simple heuristic)
- **Bidirectional exits**: Automatically creates return exit with opposite direction
- **Graceful failure handling**: If promotion succeeds but cleanup fails, rooms are still live (manual cleanup possible)
- **Connection room list**: Returns all non-sandbox rooms (ownership filtering can be added later)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed run_in_main_thread import path**

- **Found during:** Task 2 (Creating promotion engine)
- **Issue:** Plan specified `from evennia.server.sessionhandler import run_in_main_thread` but this function doesn't exist in Evennia 5.0
- **Fix:** Changed import to `from evennia.utils.utils import run_in_main_thread` (correct location in Evennia 5.0)
- **Files modified:** 
  - beckonmu/web/builder/promotion.py
  - beckonmu/web/builder/sandbox_bridge.py
  - beckonmu/web/builder/sandbox_cleanup.py
- **Verification:** All imports work correctly with Django setup
- **Committed in:** 50eb619 and 4654be2

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Import path correction required for Evennia 5.0 compatibility. No functional changes.

## Issues Encountered

None.

## Next Phase Readiness

This plan completes the builder workflow:

- **Phase 5** (Sandbox): Builders can create, test, and cleanup sandboxes
- **Phase 6** (Live Promotion): Builders can promote tested builds to live world

The builder workflow is now complete:
1. Create project → 2. Build map → 3. Submit for review → 4. Staff approves → 5. Auto-build sandbox → 6. Test in sandbox → 7. Promote to live

**Ready for Phase 7** (Trigger System): Promoted rooms can have entry/exit/timed/interaction triggers attached.

---
*Phase: 06-live-promotion*
*Completed: 2026-02-05*
