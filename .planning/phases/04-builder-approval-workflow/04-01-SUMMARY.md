---
phase: 04-builder-approval-workflow
plan: 01
subsystem: builder-workflow
tags: [django-models, status-lifecycle, api-endpoints, bootstrap, javascript, canvas]
depends_on:
  requires: ["01-review-and-hardening"]
  provides: ["BuildProject status lifecycle", "Builder submission flow", "Staff review interface", "Map preview canvas"]
  affects: ["05-01", "05-02"]
tech-stack:
  added: []
  patterns: ["Status state machine with can_transition_to()", "Canvas-based map preview", "Bootstrap 5 modal for user input", "CSRF token handling in vanilla JS"]
key-files:
  created:
    - beckonmu/web/builder/migrations/0003_buildproject_status_fields.py
    - beckonmu/web/templates/builder/review.html
  modified:
    - beckonmu/web/builder/models.py
    - beckonmu/web/builder/views.py
    - beckonmu/web/builder/urls.py
    - beckonmu/web/templates/builder/dashboard.html
decisions:
  - id: "04-01-01"
    decision: "Status choices use 5 states: draft/submitted/approved/built/live"
    rationale: "Matches the full approval-to-sandbox-to-live lifecycle"
  - id: "04-01-02"
    decision: "Rejection returns to draft (not separate rejected state)"
    rationale: "Matches CharacterBio pattern - builder can edit and resubmit immediately"
  - id: "04-01-03"
    decision: "Map preview uses canvas with simple room/exit rendering"
    rationale: "Lightweight, no external libraries needed, sufficient for staff review"
  - id: "04-01-04"
    decision: "Rejection notes have 10 character minimum"
    rationale: "Ensures staff provides meaningful feedback, not just 'no'"
metrics:
  duration: "7 min"
  completed: "2026-02-05"
---

# Phase 04 Plan 01: Builder Approval Workflow Summary

**One-liner:** BuildProject status lifecycle (draft → submitted → approved → built → live) with builder submission from dashboard, staff review page with canvas map preview, and approve/reject actions.

## Performance

- **Duration:** 7 min
- **Started:** 2026-02-05T18:43:20Z
- **Completed:** 2026-02-05T18:50:58Z
- **Tasks:** 4/4 completed
- **Files modified:** 5

## Accomplishments

- Extended BuildProject model with status field and state machine methods
- Created migration 0003_buildproject_status_fields.py with all new fields
- Added API endpoints for submission (/submit/), review list (/review/projects/), approve/reject
- Updated builder dashboard with status badges and Submit button
- Created staff review page with map preview canvas and approve/reject modals

## Task Commits

| Hash | Type | Description |
|------|------|-------------|
| eac3dfc | feat | Extend BuildProject model with status state machine |
| b46e5ba | feat | Add submission and review API endpoints |
| 60b542f | feat | Update builder dashboard with status and submission UI |
| eed55e0 | feat | Create staff review page with map preview |

**Plan metadata:** [pending after docs commit]

## Files Created/Modified

- `beckonmu/web/builder/models.py` - Added STATUS_CHOICES, status field, rejection_notes, rejection_count, reviewed_by, reviewed_at, submission_notes. Added can_transition_to(), submit(), approve(), reject(), mark_built(), mark_live() methods.
- `beckonmu/web/builder/migrations/0003_buildproject_status_fields.py` - Migration adding all status-related fields
- `beckonmu/web/builder/views.py` - Added SubmitProjectView, BuildReviewView, ApproveRejectProjectView, BuildReviewDashboardView
- `beckonmu/web/builder/urls.py` - Added URL patterns for submit, review, approve, reject endpoints
- `beckonmu/web/templates/builder/dashboard.html` - Updated status column with badges, added Submit button, rejection notes display, submission modal
- `beckonmu/web/templates/builder/review.html` - New staff review interface with project cards, map preview canvas, approve/reject functionality

## Decisions Made

1. **Status choices use 5 states:** draft, submitted, approved, built, live - covers full lifecycle
2. **Rejection returns to draft:** Matches CharacterBio pattern for immediate resubmission
3. **Canvas map preview:** Simple rendering without external libraries
4. **10 character minimum for rejection notes:** Ensures meaningful feedback

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None significant. LSP errors are false positives from type checker not understanding Django ORM patterns.

## Next Phase Readiness

Phase 5 (Sandbox Building) can now proceed. The approval workflow is complete:
- Projects can be submitted by builders
- Staff can review with map preview
- Approved projects can proceed to sandbox creation
- Status field tracks progress through lifecycle

### Key Integration Points for Sandbox Phase
- BuildProject.approve() sets status='approved' - trigger for sandbox creation
- BuildProject.mark_built() will be called after sandbox rooms created
- BuildProject.mark_live() will be called after promotion to production

---
*Phase: 04-builder-approval-workflow*
*Completed: 2026-02-05*
