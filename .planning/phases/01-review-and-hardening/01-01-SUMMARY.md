---
phase: 01-review-and-hardening
plan: 01
subsystem: api
tags: [csrf, authentication, authorization, v5-validation, django, security]

# Dependency graph
requires: []
provides:
  - "CSRF protection on all 11 traits API endpoints (Django middleware enforced)"
  - "Authentication required on all traits API views"
  - "Staff-only gate on CharacterImportAPI"
  - "Ownership-or-staff gates on CharacterExportAPI and CharacterAvailableTraitsAPI"
  - "Idempotent approval (409 Conflict on double-approve) in CharacterApprovalAPI"
  - "Generic error messages (no ORM detail leakage)"
  - "Server-side V5 chargen pool validation (attributes, skills, disciplines, advantages, flaws)"
affects: [01-02, 01-03, 02-character-creation-ux]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-method auth checks in Django CBVs (match existing PendingCharactersAPI/CharacterDetailAPI pattern)"
    - "Ownership-or-staff authorization pattern: character.db_account != request.user and not request.user.is_staff"
    - "V5 chargen pool validation as early-return guard in enhanced_import_character_from_json"

key-files:
  created: []
  modified:
    - "beckonmu/traits/api.py"
    - "beckonmu/traits/utils.py"

key-decisions:
  - "Auth checks added per-method (not via mixin) to match existing codebase pattern"
  - "In-clan discipline validation deferred -- needs clan-discipline mapping model not currently in schema"
  - "Pool validation returns early before trait processing to avoid partial imports on invalid data"

patterns-established:
  - "Auth check pattern: if not request.user.is_authenticated: return JsonResponse({error}, status=401)"
  - "Ownership pattern: if char.db_account != request.user and not request.user.is_staff: return 403"
  - "V5_CHARGEN_RULES constant dict as single source of truth for chargen limits"

# Metrics
duration: 7min
completed: 2026-02-03
---

# Phase 1 Plan 01: Traits API Security Hardening Summary

**Removed all 11 CSRF exemptions, added auth/ownership/staff gates to all traits API endpoints, added idempotent approval protection, sanitized error messages, and added server-side V5 chargen pool validation**

## Performance

- **Duration:** 7 min
- **Started:** 2026-02-03T22:36:47Z
- **Completed:** 2026-02-03T22:43:40Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- All 11 traits API views now enforce Django CSRF middleware (no more @csrf_exempt bypass)
- All 11 views require authentication; CharacterImportAPI requires staff; CharacterExportAPI and CharacterAvailableTraitsAPI enforce ownership-or-staff
- CharacterApprovalAPI returns 409 Conflict on double-approval (race condition prevention)
- Error messages sanitized to not leak ORM internals (account names, exception details)
- Server-side V5 chargen pool validation rejects invalid attribute (15 additional), skill (27), discipline (3), advantage (7), and flaw (max 2) totals before any trait import occurs

## Task Commits

Each task was committed atomically:

1. **Task 1a: Remove CSRF exemptions, add auth checks, sanitize errors** - `ca64164` (fix)
2. **Task 1b: Add authorization checks, ownership gates, idempotent approval** - `00ab5f8` (fix)
3. **Task 2: Add server-side V5 chargen pool validation** - `29b0430` (feat)

## Files Created/Modified
- `beckonmu/traits/api.py` - All 11 API views hardened with CSRF, auth, authorization, idempotent approval, and sanitized error messages
- `beckonmu/traits/utils.py` - V5_CHARGEN_RULES constants, V5_ATTRIBUTES/V5_SKILLS lists, validate_v5_chargen_pools() function, and wiring into enhanced_import_character_from_json

## Decisions Made
- **Auth check placement:** Added per-method checks (not via mixin or dispatch override) to match the existing pattern used by PendingCharactersAPI and CharacterDetailAPI. Keeps codebase consistent.
- **In-clan discipline validation deferred:** The Trait model's splat_restriction field tracks vampire/ghoul/mortal, not per-clan discipline availability. The clan-to-discipline mapping only exists in the frontend CLANS JavaScript object. Until a ClanDiscipline model is created, this check cannot be performed server-side. Staff review catches invalid combinations.
- **Pool validation as early return:** validate_v5_chargen_pools runs before individual trait processing in enhanced_import_character_from_json. If pools are invalid, the function returns immediately with errors -- no partial trait import occurs.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All traits API endpoints are now secured. Plans 01-02 (grid builder) and 01-03 (remaining security) can proceed.
- The V5 pool validation is active for both CharacterCreateAPI and CharacterValidationAPI paths.
- In-clan discipline validation is a known gap that can be addressed when a ClanDiscipline model is added (not blocking for Phase 1).

---
*Phase: 01-review-and-hardening*
*Completed: 2026-02-03*
