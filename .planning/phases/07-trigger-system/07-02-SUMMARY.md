---
phase: 07-trigger-system
plan: 02
subsystem: trigger-system
tags: [triggers, evennia, scripts, timed-triggers]

# Dependency graph
requires:
  - phase: 07-01
    provides: Entry/exit trigger engine with whitelisted actions
provides:
  - RoomTriggerScript typeclass for timed triggers
  - Trigger script management module
  - Integration with sandbox building and cleanup
  - Minimum interval enforcement (10 seconds)
affects:
  - 07-03-interaction-triggers

tech-stack:
  added: []
  patterns:
    - "Evennia Script typeclass for timed execution"
    - "Script lifecycle management (create/delete/sync)"
    - "Integration with existing trigger engine"

key-files:
  created:
    - beckonmu/web/builder/trigger_scripts.py
  modified:
    - beckonmu/typeclasses/scripts.py
    - beckonmu/web/builder/trigger_engine.py
    - beckonmu/web/builder/sandbox_builder.py
    - beckonmu/web/builder/sandbox_cleanup.py

key-decisions:
  - "RoomTriggerScript uses interval=300s (5 min) default, overridable per trigger"
  - "Scripts attached to room via obj=room parameter"
  - "trigger_id filtering in execute_triggers() for targeted timed execution"
  - "10-second minimum interval prevents abuse"
  - "is_valid() checks room.db.triggers to auto-stop orphaned scripts"

patterns-established:
  - "Script-based timed triggers: Evennia Scripts with at_repeat() for periodic execution"
  - "Lifecycle management: create_timed_trigger(), delete_timed_triggers_for_room(), sync_timed_triggers_for_room()"
  - "Cleanup integration: Trigger scripts deleted before rooms during sandbox cleanup"

# Metrics
duration: 17min
completed: 2026-02-05
---

# Phase 7 Plan 2: Timed Triggers via Evennia Scripts Summary

**Timed trigger system using Evennia Scripts that fire at configurable intervals, integrated with sandbox building and cleanup**

## Performance

- **Duration:** 17 min
- **Started:** 2026-02-05T22:29:21Z
- **Completed:** 2026-02-05T22:46:55Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Created RoomTriggerScript typeclass with at_repeat() hook for timed execution
- Built trigger_scripts.py module with full lifecycle management (create, delete, sync)
- Integrated timed trigger creation into sandbox building process
- Added trigger script cleanup to sandbox deletion workflow
- Updated trigger engine to support trigger_id filtering for targeted execution
- Implemented 10-second minimum interval to prevent abuse

## Task Commits

Each task was committed atomically:

1. **Task 1: Create RoomTriggerScript typeclass** - `c626134` (feat)
2. **Task 2: Create trigger script management module** - `4ec7a9f` (feat)
3. **Task 3: Integrate timed triggers into sandbox building** - `0668169` (feat)

## Files Created/Modified

- `beckonmu/typeclasses/scripts.py` - Added RoomTriggerScript typeclass with at_repeat(), is_valid(), and trigger configuration storage
- `beckonmu/web/builder/trigger_scripts.py` - New module with create_timed_trigger(), delete_timed_trigger(), delete_timed_triggers_for_room(), sync_timed_triggers_for_room()
- `beckonmu/web/builder/trigger_engine.py` - Added trigger_id parameter to execute_triggers() for filtering
- `beckonmu/web/builder/sandbox_builder.py` - Creates timed trigger scripts during room creation
- `beckonmu/web/builder/sandbox_cleanup.py` - Deletes trigger scripts before deleting rooms

## Decisions Made

- **Default interval:** 300 seconds (5 minutes) with ability to override per trigger
- **Minimum interval:** 10 seconds enforced to prevent performance abuse
- **Script attachment:** Scripts attached to room via obj=room, enabling room.db access
- **Trigger identification:** Unique trigger_id stored in script.db.trigger_id for filtering
- **Auto-cleanup:** is_valid() checks if trigger still exists in room.db.triggers, stops orphaned scripts
- **Execution flow:** at_repeat() calls execute_triggers() with trigger_id to execute specific trigger

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tasks completed smoothly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 07-03-PLAN.md (Interaction triggers, V5 conditions, and trigger editor UI):
- Timed trigger foundation complete with RoomTriggerScript typeclass
- Trigger engine supports all trigger types (entry, exit, timed, interaction)
- Script management module provides full lifecycle control
- Sandbox integration ensures triggers are created during build and cleaned up during deletion
- Can extend with V5 conditions (clan, hunger, time-of-night) and web editor UI

---
*Phase: 07-trigger-system*
*Completed: 2026-02-05*
