---
phase: 05-sandbox-building
plan: 02
subsystem: api
tags: [evennia, django, sandbox, isolation, commands]

# Dependency graph
requires:
  - phase: 05-sandbox-building
    plan: 01
    provides: Bridge layer and sandbox room/exit creation
provides:
  - In-game commands for sandbox navigation (@goto_sandbox, @list_sandboxes, @cleanup_sandbox)
  - Sandbox room isolation via access() override
  - Programmatic cleanup via sandbox_cleanup module
  - Web API endpoint for sandbox cleanup
  - Project status reset after cleanup (built → approved)
affects:
  - Phase 6 (Live Promotion - needs sandbox_room_id to be cleared after cleanup)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Room access override for sandbox isolation using tags"
    - "Thread-safe cleanup with run_in_main_thread wrapper"
    - "Builder commands package structure"

key-files:
  created:
    - beckonmu/commands/builder/__init__.py
    - beckonmu/commands/builder/sandbox.py
    - beckonmu/commands/builder/promote_abandon.py
    - beckonmu/web/builder/sandbox_cleanup.py
  modified:
    - beckonmu/typeclasses/rooms.py
    - beckonmu/commands/default_cmdsets.py
    - beckonmu/web/builder/views.py
    - beckonmu/web/builder/urls.py

key-decisions:
  - "Sandbox isolation uses Room.access() override checking 'sandbox' tag and project_{id} tag"
  - "Builder package converted from single file to package for better organization"
  - "CmdListSandboxes uses Admin lock but added to CharacterCmdSet (permission-checked at runtime)"
  - "Cleanup deletes exits first, then objects, then rooms to avoid reference errors"
  - "Project status resets from 'built' to 'approved' after cleanup (not to 'draft')"

patterns-established:
  - "Builder commands as package: beckonmu/commands/builder/ with submodules"
  - "Tag-based object lookup for project-scoped operations"
  - "Thread-safe Evennia operations via run_in_main_thread with threading.Event"

# Metrics
duration: 5min
completed: 2026-02-05
---

# Phase 5 Plan 2: Sandbox Isolation, Walkthrough, and Cleanup Summary

**Sandbox isolation with in-game navigation commands and programmatic cleanup for builder testing**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-05T20:25:00Z
- **Completed:** 2026-02-05T20:30:00Z
- **Tasks:** 3/3
- **Files modified:** 8

## Accomplishments

- Created `beckonmu/commands/builder/sandbox.py` with three in-game commands:
  - `@goto_sandbox` / `@gsb`: Teleport builder to their sandbox entry room
  - `@list_sandboxes` / `@lsb`: Staff command to list all active sandboxes
  - `@cleanup_sandbox` / `@csb`: Delete sandbox rooms and reset project status
- Created `beckonmu/web/builder/sandbox_cleanup.py` with thread-safe cleanup function
- Added sandbox isolation to `Room.access()` - blocks regular players from entering sandbox rooms
- Added `CleanupSandboxView` API endpoint at POST `/builder/api/build/{id}/cleanup/`
- Converted `beckonmu/commands/builder.py` to `beckonmu/commands/builder/` package

## Task Commits

Each task was committed atomically:

1. **Task 1: Create sandbox.py commands** - `73048d4` (feat)
2. **Task 2: Create sandbox_cleanup.py** - `a7d2208` (feat)
3. **Task 3: Add isolation locks and wire commands** - `f0f281f` (feat)

**Plan metadata:** [pending]

## Files Created/Modified

- `beckonmu/commands/builder/__init__.py` - Package init exporting all builder commands
- `beckonmu/commands/builder/sandbox.py` - Three sandbox management commands
- `beckonmu/commands/builder/promote_abandon.py` - Moved from builder.py (existing commands)
- `beckonmu/web/builder/sandbox_cleanup.py` - Thread-safe cleanup with status reset
- `beckonmu/typeclasses/rooms.py` - Added access() override for sandbox isolation
- `beckonmu/commands/default_cmdsets.py` - Added sandbox commands to CharacterCmdSet
- `beckonmu/web/builder/views.py` - Added CleanupSandboxView API endpoint
- `beckonmu/web/builder/urls.py` - Added URL pattern for cleanup endpoint

## Decisions Made

- **Sandbox isolation via access() override**: Check for 'sandbox' tag and project ownership
- **Builder package structure**: Converted single file to package for better organization
- **CmdListSandboxes placement**: Added to CharacterCmdSet with Admin lock (runtime permission check)
- **Cleanup order**: Exits first, then objects, then rooms to avoid reference errors
- **Status reset**: built → approved (not draft) to allow rebuilding without resubmission

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Converted builder.py to builder/ package**

- **Found during:** Task 3
- **Issue:** Plan specified creating `beckonmu/commands/builder/sandbox.py` but `beckonmu/commands/builder.py` already existed as a module
- **Fix:** Converted builder module to package: created `builder/` directory, moved existing commands to `promote_abandon.py`, created `__init__.py` to export all commands
- **Files modified:** beckonmu/commands/builder.py (deleted), beckonmu/commands/builder/__init__.py (new), beckonmu/commands/builder/promote_abandon.py (new)
- **Verification:** Import statements in default_cmdsets.py work correctly
- **Committed in:** f0f281f (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Package structure is cleaner and follows Python conventions. No functional changes.

## Issues Encountered

None.

## Next Phase Readiness

This plan delivers the sandbox lifecycle management needed for:

- **Phase 6** (Live Promotion): Builders can test in sandbox, then cleanup when ready for promotion
- **Phase 7** (Trigger System): Sandbox rooms can have triggers attached for testing

**Blockers for next phase:** None. Ready to proceed with 06-01-PLAN.md.

---
*Phase: 05-sandbox-building*
*Completed: 2026-02-05*
