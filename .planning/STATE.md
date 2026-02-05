# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-03)

**Core value:** Players and builders can do complex, multi-step tasks (character creation and area building) through an intuitive web interface instead of memorizing text commands.
**Current focus:** Phase 4 -- Builder Approval Workflow

## Current Position

Phase: 4 of 7 (Builder Approval Workflow)
Plan: 1 of 1 in current phase
Status: Phase complete
Last activity: 2026-02-05 -- Completed 04-01-PLAN.md (Builder Approval Workflow)

Progress: [##########____] 71% (10/14 plans)

## Performance Metrics

**Velocity:**
- Total plans completed: 9
- Average duration: 5 min
- Total execution time: 47 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-review-and-hardening | 3/3 | 22 min | 7 min |
| 02-character-approval-completion | 4/4 | 20 min | 5 min |
| 03-builder-ux | 2/2 | 10 min | 5 min |
| 04-builder-approval-workflow | 1/1 | 7 min | 7 min |

**Recent Trend:**
- Last 5 plans: 02-02 (5 min), 02-03 (8 min), 02-04 (3 min), 03-01 (2 min), 03-02 (8 min)
- Trend: stable

*Updated after each plan completion*

## Performance Metrics

**Velocity:**
- Total plans completed: 6
- Average duration: 6 min
- Total execution time: 37 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-review-and-hardening | 3/3 | 22 min | 7 min |
| 02-character-approval-completion | 4/4 | 20 min | 5 min |

**Recent Trend:**
- Last 5 plans: 01-03 (12 min), 02-01 (2 min), 02-02 (5 min), 02-03 (8 min)
- Trend: stable

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Review & hardening phase before any new features (brownfield safety)
- [Roadmap]: Builder approval workflow before sandbox/promotion (gate unsafe operations)
- [Roadmap]: Trigger system last (depends on bridge layer from sandbox phase)
- [01-01]: Auth checks added per-method (not via mixin) to match existing codebase pattern
- [01-01]: In-clan discipline validation deferred -- needs clan-discipline mapping model
- [01-01]: Pool validation returns early before trait processing to avoid partial imports
- [01-02]: Replaced @py logging with @set attributes -- eliminates code execution vector
- [01-02]: Optimistic concurrency uses version field comparison (not database locking)
- [01-02]: Malformed exits/objects in exporter silently skipped -- validator catches upstream
- [02-01]: Default status is 'submitted' (not 'draft') -- existing CharacterCreateAPI creates at submission time
- [02-01]: approved @property for backward-compatible reads, all writes use bio.status
- [02-01]: PendingCharactersAPI shows both submitted and rejected (not just submitted)
- [02-02]: Helper functions (notify_account, place_approved_character) live in traits/api.py, shared by web API and commands
- [02-02]: Notifications stored as list of dicts on account.db.pending_notifications
- [02-02]: Resubmission deletes all CharacterTrait/CharacterPower rows before re-import
- [02-03]: Rejection modal uses Bootstrap 5 Modal API (vanilla JS, no jQuery)
- [02-03]: Draft keyed by chargen_draft_<id> for edit, chargen_draft_new for create
- [02-03]: Draft TTL is 7 days; edit mode loads from API not localStorage
- [03-01]: Direction calculation uses 8-point compass with grid delta mapping
- [03-01]: Exits auto-created bidirectionally with opposite directions
- [03-01]: Direction labels use abbreviated forms (n, s, e, w, ne, nw, se, sw)
- [03-02]: Templates defined as Python dictionary (not database) for simplicity
- [03-02]: Haven template includes default haven_ratings for convenience
- [03-02]: Confirmation dialog only for rooms with existing V5 settings
- [04-01]: Status choices use 5 states: draft/submitted/approved/built/live
- [04-01]: Rejection returns to draft (not separate rejected state)
- [04-01]: Map preview uses canvas with simple room/exit rendering
- [04-01]: Rejection notes have 10 character minimum

### Pending Todos

- Run `evennia migrate` to apply 0002_buildproject_version migration on deployment
- Run `evennia migrate` to apply 0003_buildproject_status_fields migration on deployment
- ~~Run `evennia migrate` to apply 0002_characterbio_status_background migration on deployment~~ (Applied during 02-04)

### Blockers/Concerns

- [Research]: Phase 5 (Sandbox) needs run_in_main_thread() integration testing -- highest architectural risk
- [Research]: Phase 7 (Triggers) V5 condition system is novel -- needs design research during planning
- [Research]: JSON map_data needs schema versioning before Phase 5 -- ADDRESSED: schema_version added to defaults
- [01-01]: In-clan discipline server-side validation needs ClanDiscipline model (deferred, staff review catches it)
- [02-03]: beckonmu/web/templates/ is an NTFS junction to web/templates/ -- git tracks both paths, causing duplicate diffs
- [02-04]: Python 3.14/cryptography incompatibility prevents Evennia server startup (`_cffi_backend` error) -- Use Python 3.12 or 3.13 for testing

## Session Continuity

Last session: 2026-02-05
Stopped at: Completed 04-01-PLAN.md (Builder Approval Workflow) - Phase 4 Complete
Resume file: None
