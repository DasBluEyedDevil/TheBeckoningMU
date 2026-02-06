---
phase: 06-live-promotion
verified: 2026-02-05T21:25:00Z
status: passed
score: 5/5 must-haves verified
gaps: []
human_verification: []
---

# Phase 06: Live Promotion Verification Report

**Phase Goal:** Builders can promote a tested sandbox build into the live game world, automatically connecting it at a specified point

**Verified:** 2026-02-05T21:25:00Z
**Status:** ✅ PASSED
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | Builder can select a connection room and direction before promoting | ✅ VERIFIED | `ListConnectionRoomsView` returns all non-sandbox rooms; `PromoteProjectView` accepts `connection_room_id` and `connection_direction` parameters; UI modal with room picker dropdown and direction selector in dashboard.html |
| 2   | Promotion creates exits linking the live world to the new area | ✅ VERIFIED | `_do_promotion_in_main_thread` creates forward exit from connection room to entry room and return exit with opposite direction; lines 129-188 in promotion.py |
| 3   | Sandbox rooms are moved (not copied) to live world with all V5 attributes preserved | ✅ VERIFIED | `room.tags.remove("sandbox")` removes sandbox tag preserving all other attributes; rooms keep their dbrefs and V5 data; lines 119-127 in promotion.py |
| 4   | Original sandbox is cleaned up after successful promotion | ✅ VERIFIED | `cleanup_sandbox_for_project(project_id)` called after successful promotion; `project.sandbox_room_id = None` cleared; lines 290-294 and 307-308 in promotion.py |
| 5   | Project status changes from 'built' to 'live' | ✅ VERIFIED | `project.mark_live()` called on line 300; status transition validated via `can_transition_to('live')` in models.py line 108 |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `beckonmu/web/builder/promotion.py` | Thread-safe promotion engine that moves rooms and creates connection exits | ✅ VERIFIED | 315 lines, exports `promote_project_to_live`, uses `run_in_main_thread` for thread-safe Evennia operations |
| `beckonmu/web/builder/views.py` | Promotion API endpoints for connection room list and promotion trigger | ✅ VERIFIED | `ListConnectionRoomsView` (lines 614-655) and `PromoteProjectView` (lines 658-747) implemented |
| `beckonmu/web/builder/models.py` | BuildProject fields for connection point storage | ✅ VERIFIED | `connection_room_id` (line 70) and `connection_direction` (line 73) fields present; `mark_live()` method (lines 174-182) |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| `PromoteProjectView` | `promote_project_to_live` | POST handler calling promotion engine | ✅ WIRED | Line 724-725 in views.py: `promote_project_to_live(project.id, connection_room_id, connection_direction)` |
| `promote_project_to_live` | `sandbox_cleanup` | Cleanup called after successful promotion | ✅ WIRED | Line 290 in promotion.py: `cleanup_sandbox_for_project(project_id)` called after successful promotion |
| `promotion.py` | `Room.tags` | Remove 'sandbox' tag, keep 'web_builder' and 'project_{id}' tags | ✅ WIRED | Line 123: `room.tags.remove("sandbox")`; lines 140-141 and 171-172: tags added to created exits |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
| ----------- | ------ | -------------- |
| Connection room selection API | ✅ SATISFIED | `ListConnectionRoomsView` implemented |
| Direction validation | ✅ SATISFIED | 10 valid directions (n/s/e/w/ne/nw/se/sw/u/d) validated |
| Bidirectional exit creation | ✅ SATISFIED | Forward and return exits created with opposite directions |
| Thread-safe promotion | ✅ SATISFIED | `run_in_main_thread` wrapper used |
| Status transition to 'live' | ✅ SATISFIED | `mark_live()` method with validation |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| None | — | — | — | — |

No anti-patterns detected. All code is substantive with no TODOs, FIXMEs, or placeholder implementations.

### Human Verification Required

None. All verification items can be confirmed programmatically.

### Implementation Details Verified

**promotion.py (315 lines):**
- `DIRECTION_OPPOSITES` mapping for bidirectional exits (lines 18-29)
- `_get_opposite_direction()` helper (lines 32-42)
- `_do_promotion_in_main_thread()` performs the actual promotion work (lines 45-199)
- `promote_project_to_live()` validates and orchestrates promotion (lines 202-314)
- Thread-safe execution via `run_in_main_thread` (line 277)
- Proper error handling and logging throughout

**views.py additions:**
- `ListConnectionRoomsView` filters out sandbox rooms (lines 614-655)
- `PromoteProjectView` validates project status and parameters (lines 658-747)
- Proper permission checks (ownership verification)
- JSON request/response handling

**models.py fields:**
- `connection_room_id`: IntegerField for live room dbref (line 70)
- `connection_direction`: CharField(max_length=10) for direction (line 73)
- `promoted_at`: DateTimeField for tracking promotion time (line 80)
- `mark_live()`: Status transition method with validation (lines 174-182)

**URL routing (urls.py):**
- `GET /builder/api/connection-rooms/` → `ListConnectionRoomsView`
- `POST /builder/api/build/{pk}/promote/` → `PromoteProjectView`

**UI integration (dashboard.html):**
- "Promote to Live" button visible when `project.status == 'built'` (lines 91-96)
- Modal with room picker populated from API (lines 195-241)
- Direction dropdown with 10 valid options (lines 216-229)
- JavaScript handlers for loading rooms and submitting promotion (lines 304-377)

### Migration Verified

`0004_buildproject_connection_fields.py`:
- Adds `connection_room_id` field (IntegerField, nullable)
- Adds `connection_direction` field (CharField max_length=10, nullable)
- Proper help_text for both fields

---

_Verified: 2026-02-05T21:25:00Z_
_Verifier: OpenCode (gsd-verifier)_
