# Phase 1: Review & Hardening - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Verify and fix existing character creation, grid builder, and API code before new features build on it. This phase audits correctness, security, and reliability of the current codebase. No new features are added — only bugs fixed and security gaps closed.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion

The user trusts Claude's judgment across all review areas. The following guidelines apply:

**Issue severity & handling:**
- Fix bugs that would block downstream phases or compromise data integrity
- Defer cosmetic or minor UX issues that don't affect correctness
- The bar for moving to Phase 2: all success criteria must pass, no known security vulnerabilities, no data-loss bugs

**V5 rule correctness:**
- Validate against the rules as currently implemented in the codebase
- Flag edge cases found during review but use reasonable defaults rather than blocking on ambiguous rules
- If a V5 rule interpretation is genuinely ambiguous, document the choice made

**Builder data fidelity:**
- Round-trip means: save a project, load it back, and the map data is identical (no field loss, no coordinate drift, no missing exits)
- If legacy/malformed data is found, document it and handle gracefully (don't crash) — migration can be a separate concern if needed

**API security posture:**
- Must-have: authentication on all endpoints, CSRF protection, proper error responses, no unauthorized cross-user data access
- Should-have: input validation/sanitization at API boundaries
- Nice-to-have (defer if scope grows): rate limiting, request size limits — these are operational concerns for later

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. User expressed full trust in Claude's judgment for review standards and issue handling.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-review-hardening*
*Context gathered: 2026-02-03*
