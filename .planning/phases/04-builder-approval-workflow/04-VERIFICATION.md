---
phase: 04-builder-approval-workflow
verified: 2026-02-05T13:55:00Z
status: passed
score: 8/8 must-haves verified
gaps: []
human_verification:
  - test: "Create a test project and submit it for review"
    expected: "Project status changes from Draft to Submitted, Submit button disappears"
    why_human: "Requires UI interaction and database state change verification"
  - test: "View submitted project as staff at /builder/review/"
    expected: "Project appears with map preview canvas showing rooms/exits"
    why_human: "Visual rendering verification - canvas drawing can't be verified programmatically"
  - test: "Reject a project with notes"
    expected: "Project returns to Draft status, rejection notes visible to builder"
    why_human: "End-to-end workflow requires human to verify both staff and builder views"
  - test: "Approve a project"
    expected: "Project status changes to Approved, disappears from review list"
    why_human: "State transition verification requires checking both views"
---

# Phase 04: Builder Approval Workflow Verification Report

**Phase Goal:** Builder projects follow a gated lifecycle -- draft to submitted to approved -- with staff review before anything gets built in-game

**Verified:** 2026-02-05T13:55:00Z
**Status:** ✓ PASSED
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | Builder can see project status (Draft/Submitted/Approved/Built/Live) on dashboard | ✓ VERIFIED | dashboard.html lines 62-81: Status badges with correct colors for all 5 states |
| 2   | Builder can submit a Draft project for staff review | ✓ VERIFIED | dashboard.html lines 85-90: Submit button only for draft; lines 189-245: submitProject() function with modal and API call to /builder/api/project/<id>/submit/ |
| 3   | Staff can view all submitted projects in a dedicated review interface | ✓ VERIFIED | review.html exists; views.py BuildReviewDashboardView at line 514; URL pattern /builder/review/ in urls.py line 29 |
| 4   | Staff can see map preview of submitted project before approval | ✓ VERIFIED | review.html lines 158-241: renderMiniMap() function draws rooms/exits on canvas; lines 305-306: canvas element per project |
| 5   | Staff can approve a project with optional notes | ✓ VERIFIED | views.py ApproveRejectProjectView lines 432-511: approve action at line 459-477 calls project.approve(request.user) |
| 6   | Staff can reject a project with required notes explaining why | ✓ VERIFIED | views.py lines 479-511: reject action requires notes (line 489), validates length (not empty), calls project.reject(); review.html lines 32-56: reject modal with 10 char minimum |
| 7   | Rejected project returns to Draft status with rejection notes visible to builder | ✓ VERIFIED | models.py reject() method lines 128-152: sets status='draft', stores notes, increments count; dashboard.html lines 64-72: displays rejection count and notes tooltip for rejected projects |
| 8   | Invalid status transitions are blocked (e.g., cannot submit an already-approved project) | ✓ VERIFIED | models.py can_transition_to() lines 82-101: validates all transitions; submit/approve/reject methods all check can_transition_to() before proceeding; views.py SubmitProjectView line 359 checks can_transition_to('submitted') |

**Score:** 8/8 truths verified

### Required Artifacts

| Artifact | Expected    | Status | Details |
| -------- | ----------- | ------ | ------- |
| `beckonmu/web/builder/models.py` | BuildProject with status field, state machine | ✓ VERIFIED | 208 lines. STATUS_CHOICES with 5 states (lines 13-19), status field (lines 38-43), can_transition_to() (lines 82-101), submit()/approve()/reject()/mark_built()/mark_live() methods (lines 103-172) |
| `beckonmu/web/builder/migrations/0003_buildproject_status_fields.py` | Migration for status fields | ✓ VERIFIED | 83 lines. Adds status, rejection_notes, rejection_count, reviewed_by, reviewed_at, submission_notes fields |
| `beckonmu/web/builder/views.py` | API endpoints for submission and review | ✓ VERIFIED | 519 lines. SubmitProjectView (lines 346-393), BuildReviewView (lines 396-429), ApproveRejectProjectView (lines 432-511), BuildReviewDashboardView (lines 514-518) |
| `beckonmu/web/builder/urls.py` | URL patterns for all endpoints | ✓ VERIFIED | 46 lines. submit_project (line 21-24), build_review (line 29), review_projects (line 31-32), approve_project (line 33-37), reject_project (line 38-42) |
| `beckonmu/web/templates/builder/dashboard.html` | Builder dashboard with status UI | ✓ VERIFIED | 270 lines. Status badges (lines 62-81), Submit button (lines 85-90), rejection notes display (lines 64-72), submission modal (lines 165-187), submitProject() function (lines 212-245) |
| `beckonmu/web/templates/builder/review.html` | Staff review page with map preview | ✓ VERIFIED | 356 lines. Project cards (lines 271-321), map preview canvas (lines 305-306), renderMiniMap() (lines 158-241), approve/reject buttons (lines 309-314), reject modal (lines 32-56) |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| dashboard.html | /builder/api/project/<id>/submit/ | fetch POST | ✓ WIRED | Line 225: fetch(`/builder/api/project/${currentProjectId}/submit/`) with CSRF token and JSON body |
| dashboard.html | /builder/review/ | href link | ✓ WIRED | Line 24: Link visible to staff users with pending count badge |
| review.html | /builder/api/review/projects/ | fetch GET | ✓ WIRED | Line 252: fetch('/builder/api/review/projects/') loads submitted projects |
| review.html | /builder/api/review/<id>/approve/ | fetch POST | ✓ WIRED | Line 138: fetch(`/builder/api/review/${id}/approve/`) in approveProject() function |
| review.html | /builder/api/review/<id>/reject/ | fetch POST | ✓ WIRED | Line 109: fetch(`/builder/api/review/${currentProjectId}/reject/`) with notes in body |
| review.html | /builder/api/project/<id>/ | fetch GET | ✓ WIRED | Line 328: fetch(`/builder/api/project/${project.id}/`) to load map data for preview |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
| ----------- | ------ | -------------- |
| BLDW-01: BuildProject has explicit status field (Draft, Submitted, Approved, Built, Live) | ✓ SATISFIED | models.py STATUS_CHOICES lines 13-19, status field lines 38-43 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| None | - | - | - | No anti-patterns detected |

**Notes:**
- No TODO/FIXME comments found
- No placeholder implementations
- No empty return statements
- All methods have substantive implementations

### Authentication Verification

| Endpoint | Authentication | Authorization | Status |
|----------|---------------|---------------|--------|
| /builder/api/project/<id>/submit/ | StaffRequiredMixin | is_staff required | ✓ VERIFIED |
| /builder/api/review/projects/ | @method_decorator(staff_member_required) | is_staff required | ✓ VERIFIED |
| /builder/api/review/<id>/approve/ | @method_decorator(staff_member_required) | is_staff required | ✓ VERIFIED |
| /builder/api/review/<id>/reject/ | @method_decorator(staff_member_required) | is_staff required | ✓ VERIFIED |
| /builder/review/ | @method_decorator(staff_member_required) + LoginRequiredMixin | is_staff required | ✓ VERIFIED |

All API endpoints require proper staff authentication via either `StaffRequiredMixin` or `@method_decorator(staff_member_required)`.

### State Machine Verification

**Valid Transitions (from can_transition_to method):**

| From Status | To Status | Valid? | Use Case |
|-------------|-----------|--------|----------|
| draft | submitted | ✓ | Builder submits for review |
| submitted | approved | ✓ | Staff approves project |
| submitted | draft | ✓ | Staff rejects project |
| approved | built | ✓ | Sandbox created |
| built | live | ✓ | Promoted to production |
| live | built | ✓ | Demotion (rare) |
| built | approved | ✓ | Sandbox deleted |

**Invalid Transitions (correctly blocked):**
- draft → approved (must submit first)
- draft → built (must be approved first)
- approved → submitted (can't un-approve)
- live → draft (must go through built)

### Human Verification Required

The following tests require human interaction to fully verify:

1. **Create and Submit Project**
   - **Test:** Log in as builder, create project, click Submit
   - **Expected:** Status changes to "Submitted" (yellow badge), Submit button disappears
   - **Why human:** Requires UI interaction and visual confirmation

2. **Staff Review Page**
   - **Test:** Log in as staff, navigate to /builder/review/
   - **Expected:** Submitted project appears with map preview canvas showing rooms/exits
   - **Why human:** Canvas rendering is visual - can't verify programmatically

3. **Reject Project Flow**
   - **Test:** Click Reject, enter notes (10+ chars), submit
   - **Expected:** Project disappears from review list; as builder, see "Rejected 1 time(s)" with notes tooltip
   - **Why human:** End-to-end workflow spans two user roles

4. **Approve Project Flow**
   - **Test:** Submit another project, click Approve
   - **Expected:** Project disappears from review list, status changes to "Approved" (blue badge)
   - **Why human:** State transition verification requires checking both views

5. **Invalid Transition Blocking**
   - **Test:** Try to submit an already-approved project (via API or UI)
   - **Expected:** Error message: "Cannot submit project in 'approved' status"
   - **Why human:** Edge case testing

### Gaps Summary

No gaps found. All must-haves from the PLAN frontmatter have been verified:

- ✓ BuildProject has status field with 5 valid states
- ✓ State machine validates transitions via can_transition_to()
- ✓ Builder can submit draft projects via dashboard
- ✓ Staff can view submitted projects at /builder/review/
- ✓ Staff can approve/reject projects
- ✓ Rejection notes are visible to builder via tooltip
- ✓ Map preview renders on review page via canvas
- ✓ All API endpoints require proper staff authentication

---

_Verified: 2026-02-05T13:55:00Z_
_Verifier: OpenCode (gsd-verifier)_
