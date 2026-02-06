---
phase: 02-character-approval-completion
plan: 02
subsystem: traits-api
tags: [api-endpoints, notifications, auto-placement, resubmission, chargen-commands]
depends_on:
  requires: [02-01]
  provides: [my-characters-api, edit-data-api, resubmit-api, notify-account, place-approved-character, at-post-login-delivery]
  affects: [02-03, 02-04]
tech-stack:
  added: []
  patterns: [helper-function-sharing, offline-notification-queue, trait-delete-reimport]
key-files:
  created: []
  modified:
    - beckonmu/traits/api.py
    - beckonmu/traits/urls.py
    - beckonmu/typeclasses/accounts.py
    - beckonmu/commands/chargen.py
    - beckonmu/web/website/views/__init__.py
decisions:
  - id: 02-02-01
    decision: "Helper functions (notify_account, place_approved_character) live in traits/api.py, shared by both web API and in-game commands"
    reason: "Both web and command paths need the same behavior; single source of truth avoids drift"
  - id: 02-02-02
    decision: "Notifications stored as list of dicts on account.db.pending_notifications with read/unread tracking"
    reason: "Evennia db attributes are persistent and simple; no additional model needed for notification queue"
  - id: 02-02-03
    decision: "Resubmission deletes all CharacterTrait and CharacterPower rows before re-import"
    reason: "Prevents duplicate traits from accumulating across resubmissions (Pitfall 2 from research)"
metrics:
  duration: "5 min"
  completed: "2026-02-04"
---

# Phase 02 Plan 02: API Endpoints, Notifications, and Auto-Placement Summary

**One-liner:** Three new player-facing API endpoints (my-characters, for-edit, resubmit) with shared helper functions for auto-placement and offline notification delivery, used by both web API and in-game commands.

## What Was Done

### Task 1: Helper Functions and New API Endpoints (fec211d)

**Helper functions added to `beckonmu/traits/api.py`:**

- `notify_account(account, message, notification_type)` -- Stores notification in `account.db.pending_notifications` list and attempts immediate delivery if player is online via `account.sessions.count()`.
- `place_approved_character(character)` -- Reads `settings.START_LOCATION` (default `#2`), resolves to ObjectDB room, sets `character.home` and calls `character.move_to(start_room, quiet=True)`.

**Three new API view classes:**

- `MyCharactersAPI` (GET `/api/traits/my-characters/`) -- Returns all characters owned by the authenticated user with status, clan, concept, rejection_notes (only if rejected), rejection_count, timestamps.
- `CharacterEditDataAPI` (GET `/api/traits/character/<id>/for-edit/`) -- Returns full character data (via `export_character_to_json` + bio fields) for a rejected character owned by the requester. Enforces ownership and rejected status.
- `CharacterResubmitAPI` (POST `/api/traits/character/<id>/resubmit/`) -- Accepts `character_data`, deletes existing CharacterTrait/CharacterPower rows, re-imports via `enhanced_import_character_from_json`, updates bio fields, sets status to `submitted`, clears rejection_notes.

**Updated existing `CharacterApprovalAPI.post()`:**
- On approve: calls `place_approved_character()` and `notify_account()` with approval message.
- On reject: calls `notify_account()` with rejection message including staff feedback.

**Updated URL routing in `beckonmu/traits/urls.py`:**
- Added routes for `my-characters/`, `character/<id>/for-edit/`, `character/<id>/resubmit/`.

**Updated `CharacterCreationView` in `beckonmu/web/website/views/__init__.py`:**
- Reads `?edit=<id>` query parameter and passes `edit_character_id` to template context.

### Task 2: Chargen Commands and Login Notification Delivery (92db7db)

**Updated `beckonmu/commands/chargen.py`:**
- `CmdApprove.func()` now calls `place_approved_character(character)` after bio.save() for auto-placement.
- `CmdApprove.func()` replaced inline notification with `notify_account()` for offline-safe delivery.
- `CmdReject.func()` replaced inline notification with `notify_account()` for offline-safe delivery.
- Both commands import helpers from `beckonmu.traits.api`.

**Updated `beckonmu/typeclasses/accounts.py`:**
- Added `at_post_login(session, **kwargs)` to `Account` class.
- On login, reads `self.db.pending_notifications`, displays unread notifications with header/footer, marks as read, removes delivered notifications from the list.

## Deviations from Plan

None -- plan executed exactly as written.

## Decisions Made

1. **Helper functions in api.py** (02-02-01): `notify_account` and `place_approved_character` placed in `beckonmu/traits/api.py` and imported by chargen commands. This keeps a single source of truth for both web and in-game paths.
2. **Notification storage format** (02-02-02): List of dicts with `message`, `type`, `timestamp`, `read` fields on `account.db.pending_notifications`. Uses Evennia's built-in persistent attributes.
3. **Trait deletion before resubmit** (02-02-03): `CharacterResubmitAPI` deletes all `CharacterTrait` and `CharacterPower` rows for the character before calling `enhanced_import_character_from_json`. This prevents duplicate traits accumulating across resubmissions.

## Verification Results

| # | Check | Result |
|---|-------|--------|
| 1 | GET /api/traits/my-characters/ returns character list with status | PASS |
| 2 | GET /api/traits/character/<id>/for-edit/ returns full data for rejected character | PASS |
| 3 | POST /api/traits/character/<id>/resubmit/ re-imports traits, updates status | PASS |
| 4 | CharacterApprovalAPI.post() calls place_approved_character() on approve | PASS |
| 5 | CharacterApprovalAPI.post() calls notify_account() on approve and reject | PASS |
| 6 | CmdApprove calls place_approved_character() after bio.save() | PASS |
| 7 | CmdApprove and CmdReject call notify_account() | PASS |
| 8 | Account.at_post_login reads and delivers pending_notifications | PASS |
| 9 | CharacterCreationView passes edit_character_id when ?edit=N in URL | PASS |
| 10 | Resubmission deletes old traits before re-importing | PASS |
| 11 | CharacterDetailAPI bio_data includes background field | PASS (already existed from 02-01) |

## Next Phase Readiness

**Ready for 02-03 (frontend integration):** All backend endpoints are in place. The frontend can:
- List player's characters via `/api/traits/my-characters/`
- Load rejected character data for editing via `/api/traits/character/<id>/for-edit/`
- Resubmit edited character via `/api/traits/character/<id>/resubmit/`
- Link to character creation page with `?edit=<id>` for pre-population

**No blockers identified.**
