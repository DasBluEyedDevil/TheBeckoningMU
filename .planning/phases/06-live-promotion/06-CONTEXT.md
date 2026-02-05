# Phase 6: Live Promotion - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Builders can promote a tested sandbox build into the live game world, automatically connecting it at a specified point. After successful promotion, sandbox copies are cleaned up.

</domain>

<decisions>
## Implementation Decisions

### Connection point selection
- Room picker interface showing live world rooms builder has access to
- Builder selects from rooms they own or have builder permissions on
- Connection point stored as (room_id, direction) pair before promotion

### Promotion workflow
- Single-click promotion with confirmation modal
- Modal shows: connection room name, direction, room count being promoted
- "Promote to Live" button triggers the operation
- No multi-step wizard — keep it simple

### Direction mapping
- Builder explicitly chooses direction from dropdown (N/S/E/W/NE/NW/SE/SW/U/D)
- Auto-detect suggested direction based on relative position if available
- System validates no exit conflict exists in that direction before allowing promotion

### Post-promotion cleanup
- Immediate sandbox cleanup on successful promotion
- No grace period — sandbox is the test area, live is production
- If promotion fails partway, partial build stays in live, sandbox preserved for retry
- Project status changes from 'built' to 'live'

### Visibility & notifications
- New area immediately accessible to all players through the connection point
- Builder receives success notification
- Staff receive notification that [Builder] promoted [Project] to live
- No player broadcast — discovery is organic

### OpenCode's Discretion
- Exact room picker UI implementation (modal vs inline)
- Confirmation modal styling and content
- Notification message wording
- Error message formatting if promotion fails

</decisions>

<specifics>
## Specific Ideas

- Connection picker should feel like the existing builder dashboard — consistent UI patterns
- Direction dropdown should show both abbreviation and full name ("N - North")
- Confirmation modal should show a mini summary: "This will promote 12 rooms to live world, connecting from Central Plaza to the North"

</specifics>

<deferred>
## Deferred Ideas

- Rollback capability after promotion — would need versioning/backup system
- Staged promotion (preview mode before going live) — adds complexity, sandbox is already the preview
- Promotion scheduling ("go live at midnight") — future enhancement

</deferred>

---

*Phase: 06-live-promotion*
*Context gathered: 2026-02-05*
