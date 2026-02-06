---
phase: 01-review-and-hardening
plan: 02
subsystem: api
tags: [csrf, concurrency, injection, validation, django, builder, security]

# Dependency graph
requires:
  - phase: 01-01
    provides: "CSRF/auth hardening pattern established in traits API"
provides:
  - "CSRF protection on all 3 builder mutation endpoints (Django middleware enforced)"
  - "Optimistic concurrency control on project saves (version field, 409 on conflict)"
  - "schema_version in new project map_data defaults"
  - "Exporter free of @py code injection vector"
  - "Safe .get() access on all user-provided dictionary keys in exporter"
  - "Shape validation for rooms and exits in validator"
affects: [01-03, 05-sandbox-building]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Optimistic concurrency via version field comparison and 409 Conflict response"
    - "Safe dictionary access with .get() and skip-on-missing for user-provided JSON data"
    - "Shape validation before connectivity validation in builder validator"

key-files:
  created:
    - "beckonmu/web/builder/migrations/0002_buildproject_version.py"
  modified:
    - "beckonmu/web/builder/views.py"
    - "beckonmu/web/builder/exporter.py"
    - "beckonmu/web/builder/validators.py"
    - "beckonmu/web/builder/models.py"

key-decisions:
  - "Replaced @py logging with @set attributes for build completion tracking -- eliminates code execution vector entirely"
  - "Optimistic concurrency uses version field comparison (not database-level locking) for simplicity"
  - "Malformed exits/objects in exporter are silently skipped rather than raising errors -- validator catches these upstream"

patterns-established:
  - "Optimistic concurrency: client sends version, server compares, returns 409 on mismatch"
  - "Safe JSON key access: .get() with validation guard, skip iteration on missing required fields"
  - "Shape-then-connectivity validation order in builder validator"

# Metrics
duration: 3min
completed: 2026-02-03
---

# Phase 1 Plan 02: Builder Hardening Summary

**Removed 3 CSRF exemptions from builder views, eliminated @py injection in exporter, replaced unsafe dictionary key access with .get(), added optimistic concurrency control with version field, added schema_version to new projects, and added room/exit shape validation**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-03T22:41:03Z
- **Completed:** 2026-02-03T22:44:32Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- All 3 builder mutation views (Save, Delete, Build) now enforce Django CSRF middleware
- SaveProjectView implements optimistic concurrency: compares client version to server version, returns 409 Conflict on mismatch, increments version on each save
- Exporter no longer contains @py code execution -- replaced with safe @set commands for build completion tracking
- All direct dictionary key access on user-provided exit_data and obj_data replaced with .get() and validation guards
- Validator now checks room and exit data shapes (dict type, required fields) before connectivity analysis
- New projects include schema_version: 1 in their map_data defaults

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove @csrf_exempt and add optimistic concurrency control** - `078b422` (fix)
2. **Task 2: Fix exporter @py injection and unsafe key access** - `f0463a5` (fix)
3. **Task 3: Improve validator to check room data shape** - `5a9bf7f` (fix)

## Files Created/Modified
- `beckonmu/web/builder/views.py` - Removed 3 @csrf_exempt decorators, added optimistic concurrency control to SaveProjectView (version comparison, 409 on conflict, version in response)
- `beckonmu/web/builder/models.py` - Added version field (PositiveIntegerField, default=1), added schema_version: 1 to get_default_map_data()
- `beckonmu/web/builder/exporter.py` - Replaced @py injection line with safe @set commands, replaced exit_data['source']/['target'] and obj_data['room'] with .get() and validation
- `beckonmu/web/builder/validators.py` - Added shape validation for rooms (dict type, name required) and exits (dict type, source/target required) before connectivity checks
- `beckonmu/web/builder/migrations/0002_buildproject_version.py` - Migration to add version field to BuildProject

## Decisions Made
- **@py replacement:** Replaced code execution line with @set attribute commands. The @py line allowed arbitrary Python execution with user-controlled project name interpolation. @set commands are safe and provide the same build-completion tracking.
- **Optimistic concurrency approach:** Used application-level version field comparison rather than database-level row locking. Simpler, works across all database backends, and sufficient for the expected concurrency level (staff-only access).
- **Skip-on-missing in exporter:** Malformed exits (missing source/target) and objects (missing room) are silently skipped in the exporter rather than raising errors. The validator catches these upstream, and defensive coding in the exporter prevents KeyError crashes.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

**Migration required:** After deployment, run `evennia migrate` to apply the new version field migration (0002_buildproject_version). Existing projects will default to version=1.

## Next Phase Readiness
- All builder API endpoints are now secured (CSRF enforced, concurrency control active)
- Exporter is injection-safe and handles malformed data gracefully
- Validator catches malformed room/exit data before it reaches the exporter
- Plan 01-03 (remaining security items) can proceed
- Phase 5 (Sandbox Building) will benefit from schema_version field for future data migrations

---
*Phase: 01-review-and-hardening*
*Completed: 2026-02-03*
