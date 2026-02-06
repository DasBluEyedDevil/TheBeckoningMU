---
phase: 02-character-approval-completion
plan: 01
subsystem: traits-models
tags: [django-models, migration, status-lifecycle, backward-compat]
depends_on:
  requires: [01-review-and-hardening]
  provides: [status-field, background-field, rejection-tracking, approved-property]
  affects: [02-02, 02-03, 02-04]
tech-stack:
  added: []
  patterns: [status-enum-field, backward-compat-property, data-migration]
key-files:
  created:
    - beckonmu/traits/migrations/0002_characterbio_status_background.py
  modified:
    - beckonmu/traits/models.py
    - beckonmu/traits/api.py
    - beckonmu/commands/chargen.py
decisions:
  - id: 02-01-01
    summary: "Default status is 'submitted' (not 'draft') because existing CharacterCreateAPI creates bios at submission time"
  - id: 02-01-02
    summary: "approved @property provides backward-compatible read-only access -- all writes use bio.status"
  - id: 02-01-03
    summary: "PendingCharactersAPI shows both submitted and rejected characters (not just submitted)"
metrics:
  duration: 2 min
  completed: 2026-02-04
---

# Phase 02 Plan 01: Model Extension and Call-Site Refactor Summary

Extended CharacterBio with status lifecycle field (replacing boolean approved), background text field, and rejection tracking fields, then refactored all Python write sites to use bio.status.

## One-liner

Status lifecycle field replacing boolean approved with draft/submitted/rejected/approved states, plus rejection tracking and background field.

## What Was Done

### Task 1: Add status, background, rejection fields to CharacterBio model and create migration

**Commit:** `8966cbf` (pre-existing, verified)

- Added `STATUS_CHOICES` constant with draft/submitted/rejected/approved states
- Added `status` CharField (default='submitted'), `background` TextField, `rejection_notes` TextField, `rejection_count` PositiveIntegerField
- Removed `approved = models.BooleanField(default=False)` field declaration
- Added `@property approved` returning `self.status == 'approved'` for backward-compatible reads
- Created migration `0002_characterbio_status_background.py` with:
  - AddField operations for all 4 new fields
  - RunPython data migration (approved=True -> status='approved', approved=False -> status='submitted')
  - RemoveField for the old boolean approved field

### Task 2: Refactor all API and command call sites from bio.approved boolean writes to bio.status string writes

**Commit:** `64d83d8`

**In `beckonmu/traits/api.py`:**
- `CharacterCreateAPI.post()`: Changed `approved=False` to `status='submitted'` in CharacterBio.objects.create, added `background=` field
- `CharacterApprovalAPI.post()`: Changed `bio.approved = True/False` to `bio.status = 'approved'/'rejected'`, added rejection_notes and rejection_count tracking on reject, updated idempotent check to use `bio.status == 'approved'`
- `PendingCharactersAPI.get()`: Changed `CharacterBio.objects.filter(approved=False)` to `filter(status__in=['submitted', 'rejected'])`, added `status` to response data
- `CharacterDetailAPI.get()`: Added `status`, `background`, `rejection_notes`, `rejection_count` to bio_data dict

**In `beckonmu/commands/chargen.py`:**
- `CmdPending.func()`: Changed `filter(approved=False)` to `filter(status__in=['submitted', 'rejected'])`
- `CmdApprove.func()`: Changed `bio.approved = True` to `bio.status = 'approved'`, updated already-approved check to use `bio.status == 'approved'`
- `CmdReject.func()`: Added `bio.status = 'rejected'`, `bio.rejection_notes = reason`, `bio.rejection_count += 1`, `bio.save()`
- Fixed Comment field name bug in both CmdApprove and CmdReject: `text=comment_text` -> `content=comment_text` (matches Comment model's actual field name)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed Comment.objects.create field name**

- **Found during:** Task 2
- **Issue:** Both CmdApprove (line 504) and CmdReject (line 615) used `text=comment_text` but the Comment model's field is named `content`, not `text`. This would cause a TypeError at runtime when approving/rejecting characters with Jobs integration enabled.
- **Fix:** Changed `text=comment_text` to `content=comment_text` in both locations
- **Files modified:** beckonmu/commands/chargen.py
- **Commit:** 64d83d8

**2. [Rule 2 - Missing Critical] CmdReject was not persisting rejection to model**

- **Found during:** Task 2
- **Issue:** CmdReject only notified the player and logged to character.db.staff_actions but never set `bio.status`, `bio.rejection_notes`, or `bio.rejection_count` on the CharacterBio model. This meant the rejection was not queryable through Django ORM and the PendingCharactersAPI would not show the correct status.
- **Fix:** Added `bio.status = 'rejected'`, `bio.rejection_notes = reason`, `bio.rejection_count += 1`, `bio.save()` to CmdReject.func()
- **Files modified:** beckonmu/commands/chargen.py
- **Commit:** 64d83d8

## Verification Results

| Check | Result |
|-------|--------|
| CharacterBio has STATUS_CHOICES, status, background, rejection_notes, rejection_count, approved @property | PASS |
| Migration has AddField + RunPython + RemoveField | PASS |
| No `bio.approved = True/False` assignment in any Python file | PASS |
| No `approved=False` in create/filter calls (only in migration reverse) | PASS |
| PendingCharactersAPI filters by status__in | PASS |
| CharacterApprovalAPI sets bio.status and stores rejection_notes | PASS |
| CmdReject writes rejection_notes and increments rejection_count | PASS |
| Comment.objects.create uses content= not text= | PASS |

## Next Phase Readiness

- Migration must be applied: `evennia migrate` (adds to existing pending migration todo)
- All downstream plans (02-02 through 02-04) can now use the status field, background field, and rejection tracking
- The approved @property ensures existing read-only code continues working without changes
