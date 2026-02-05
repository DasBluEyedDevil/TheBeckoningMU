---
phase: 05-sandbox-building
plan: 01
subsystem: api
tags: [evennia, django, sandbox, bridge, threading]

# Dependency graph
requires:
  - phase: 04-builder-approval-workflow
    provides: BuildProject status lifecycle and approval workflow
provides:
  - Thread-safe Django-to-Evennia bridge (run_sync_in_main_thread)
  - Sandbox room/exit creation from map_data
  - BuildSandboxView API endpoint for triggering sandbox builds
  - Automatic project status transition (approved → built)
affects:
  - Phase 5 Plan 2 (sandbox isolation and cleanup)
  - Phase 6 (live promotion - needs sandbox_room_id)
  - Phase 7 (trigger system - depends on bridge layer)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Thread-safe Evennia API calls via run_in_main_thread wrapper"
    - "Service layer pattern: bridge → builder → Evennia API"
    - "Error handling with partial success tracking"

key-files:
  created:
    - beckonmu/web/builder/sandbox_bridge.py
    - beckonmu/web/builder/sandbox_builder.py
  modified:
    - beckonmu/web/builder/views.py
    - beckonmu/web/builder/urls.py

key-decisions:
  - "Use 30-second timeout for main thread operations to prevent indefinite blocking"
  - "Continue building on per-room/per-exit errors for partial success"
  - "Create sandbox container room as entry point with _sandbox_{project_id} alias"
  - "Tag all objects with web_builder, project_{id}, and sandbox for tracking"

patterns-established:
  - "run_sync_in_main_thread: Generic wrapper for thread-safe Evennia calls"
  - "create_sandbox_from_project: High-level API with validation and status management"
  - "build_sandbox_area: Low-level object creation with error recovery"

# Metrics
duration: 3min
completed: 2026-02-05
---

# Phase 5 Plan 1: Bridge Layer and Sandbox Building Summary

**Thread-safe Django-to-Evennia bridge with automatic sandbox creation for approved builder projects**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-05T20:22:05Z
- **Completed:** 2026-02-05T20:25:05Z
- **Tasks:** 3/3
- **Files modified:** 4

## Accomplishments

- Created `sandbox_bridge.py` with `run_sync_in_main_thread()` wrapper for thread-safe Evennia API calls
- Created `sandbox_builder.py` with `build_sandbox_area()` function that creates rooms with V5 attributes and exits
- Added `BuildSandboxView` API endpoint at POST `/builder/api/build/{id}/build-sandbox/`
- Implemented automatic project status transition from "approved" to "built" on successful sandbox creation
- All created objects tagged with `web_builder`, `project_{id}`, and `sandbox` for identification and cleanup

## Task Commits

Each task was committed atomically:

1. **Task 1: Create sandbox_bridge.py** - `fac7cf5` (feat)
2. **Task 2: Create sandbox_builder.py** - `ffe0419` (feat)
3. **Task 3: Add BuildSandboxView API endpoint** - `7b319a1` (feat)

**Plan metadata:** [pending] (docs: complete plan)

## Files Created/Modified

- `beckonmu/web/builder/sandbox_bridge.py` - Thread-safe bridge with run_sync_in_main_thread wrapper and create_sandbox_from_project function
- `beckonmu/web/builder/sandbox_builder.py` - Room/exit creation logic with V5 attribute handling
- `beckonmu/web/builder/views.py` - Added BuildSandboxView class and import for create_sandbox_from_project
- `beckonmu/web/builder/urls.py` - Added URL pattern for build-sandbox endpoint

## Decisions Made

- **30-second timeout** for main thread operations to prevent indefinite blocking on errors
- **Partial success handling**: Continue building rooms/exits even if individual objects fail
- **Sandbox container room**: Created as entry point with `_sandbox_{project_id}` alias
- **Triple tagging**: All objects get `web_builder`, `project_{id}`, and `sandbox` tags for flexible querying
- **Haven ratings**: Only set when `location_type == "haven"` to avoid unnecessary attributes

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

This plan delivers the critical bridge infrastructure needed for:

- **Phase 5 Plan 2** (Sandbox Isolation): Can now build on the sandbox creation to add isolation controls, @goto_sandbox command, and cleanup
- **Phase 6** (Live Promotion): The `sandbox_room_id` field is populated and can be used for promotion logic
- **Phase 7** (Trigger System): The bridge layer pattern can be reused for trigger script creation

**Blockers for next phase:** None. Ready to proceed with 05-02-PLAN.md.

---
*Phase: 05-sandbox-building*
*Completed: 2026-02-05*
