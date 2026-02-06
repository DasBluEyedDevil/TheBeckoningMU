# Phase 1: Review & Hardening - Research

**Researched:** 2026-02-03
**Domain:** Security hardening, V5 validation correctness, grid builder data integrity
**Confidence:** HIGH

## Summary

Phase 1 is a brownfield audit phase -- there is no new architecture to design, no new libraries to install. The work is reviewing existing code across three subsystems (character creation, grid builder, API layer) and fixing specific issues identified through direct source code analysis. The codebase is approximately 900 lines of Python views/models/validators, 270 lines of batch exporter, and 1,470 lines of character creation HTML/JS.

The most critical finding is that CSRF protection is disabled via `@csrf_exempt` on **every single API endpoint** -- 11 endpoints in `traits/api.py` and 3 in `builder/views.py`. This is despite the frontends already sending CSRF tokens correctly in `X-CSRFToken` headers. The fix is removing the decorator, not adding new infrastructure. The second critical finding is that several character-creation API endpoints have no authentication check at all, meaning any anonymous user can read trait catalogs, export character data by guessing IDs, and validate character builds. The third area is the grid builder's save/load round-trip, which currently has no concurrency protection and uses inconsistent key access patterns that could cause `KeyError` on older project data.

**Primary recommendation:** Remove all `@csrf_exempt` decorators, add authentication checks to unprotected endpoints, fix builder data access to use `.get()` consistently, and add server-side V5 rule validation to match the frontend validation logic.

## Standard Stack

This phase does NOT add any new libraries. It fixes existing code using the current stack.

### Core (Already Installed)
| Library | Version | Purpose | Role in Phase 1 |
|---------|---------|---------|-----------------|
| Django | 5.2.7 | Web framework | CSRF middleware already active; just remove `@csrf_exempt` |
| Evennia | 5.0.1 | MUD framework | Character object creation in `CharacterCreateAPI` |
| Bootstrap | 5.1.3 | CSS framework | No changes needed |
| Vanilla JS | ES6+ | Frontend | Already sends CSRF tokens correctly |

### Supporting (No New Installs)
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `django.test.Client` | Write tests for API endpoints | Verify auth checks and CSRF enforcement |
| `django.test.override_settings` | Test with `enforce_csrf_checks=True` | Ensure CSRF is not accidentally bypassed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Manual auth checks | Django LoginRequiredMixin | Mixin is cleaner but requires refactoring all API views from function-decorated to class-based; current pattern works |
| Manual CSRF cookie reading | `django.views.decorators.csrf.ensure_csrf_cookie` | Only needed if views don't render templates; our API views are called from template pages that already set the cookie |

**Installation:** None needed. All tools are already in the stack.

## Architecture Patterns

### Existing Project Structure (Relevant Files)
```
beckonmu/
  traits/
    api.py              # 11 API views -- ALL have @csrf_exempt, 7 lack auth checks
    models.py           # CharacterBio, CharacterTrait, Trait, DisciplinePower, etc.
    utils.py            # enhanced_import_character_from_json, validate_trait_for_character
    urls.py             # URL routing for traits API
  web/
    builder/
      views.py          # 3 views with @csrf_exempt (SaveProject, DeleteProject, BuildProject)
      models.py         # BuildProject, RoomTemplate
      validators.py     # validate_project -- connectivity only, no data shape validation
      exporter.py       # generate_batch_script -- contains @py injection risk
      urls.py           # URL routing for builder
    website/
      views/
        __init__.py     # CharacterApprovalView, CharacterCreationView (template views)
    templates/
      character_creation.html   # 1,470 lines -- V5 chargen form with client-side validation
      character_approval.html   # Staff approval interface
      builder/
        editor.html     # Grid builder editor
        dashboard.html  # Builder dashboard
```

### Pattern 1: CSRF Fix Pattern (Remove Decorator, Verify Frontend)
**What:** Remove `@csrf_exempt` from all API views. The frontends already send the token.
**When to use:** Every mutation endpoint.
**Example:**
```python
# BEFORE (BROKEN):
@method_decorator(csrf_exempt, name='dispatch')
class SaveProjectView(StaffRequiredMixin, View):
    ...

# AFTER (FIXED):
class SaveProjectView(StaffRequiredMixin, View):
    # No csrf_exempt -- Django middleware handles CSRF automatically
    # Frontend already sends X-CSRFToken header (verified in editor.html:810)
    ...
```

### Pattern 2: Authentication Check Pattern
**What:** Add explicit auth checks to API views that currently lack them.
**When to use:** Any endpoint that returns user-specific or sensitive data.
**Example:**
```python
# BEFORE (BROKEN -- no auth check):
class CharacterExportAPI(BaseAPIView):
    def get(self, request, character_id):
        character = ObjectDB.objects.get(id=character_id, ...)
        return JsonResponse(export_character_to_json(character))

# AFTER (FIXED):
class CharacterExportAPI(BaseAPIView):
    def get(self, request, character_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        character = ObjectDB.objects.get(id=character_id, ...)
        # Also verify user has permission to see this character
        if character.db_account != request.user and not request.user.is_staff:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        return JsonResponse(export_character_to_json(character))
```

### Pattern 3: Safe JSON Key Access
**What:** Use `.get()` with defaults instead of direct key access on JSON data.
**When to use:** All access to `map_data` fields in exporter and validators.
**Example:**
```python
# BEFORE (BROKEN -- raises KeyError on old data):
source_alias = f"_bld_{project_id}_{exit_data['source']}"

# AFTER (FIXED):
source_id = exit_data.get('source')
if not source_id:
    errors.append(f"Exit '{exit_id}' missing source room")
    continue
source_alias = f"_bld_{project_id}_{source_id}"
```

### Anti-Patterns to Avoid
- **Blanket `@csrf_exempt` on class dispatch:** This completely disables CSRF for all methods (GET, POST, DELETE). If CSRF exemption is genuinely needed for a specific method, use `csrf_exempt` on just that method, not the whole dispatch.
- **Checking `request.user.is_staff` without checking `request.user.is_authenticated` first:** An anonymous user's `is_staff` is `False`, but Django's `AnonymousUser` can behave unexpectedly in some contexts. Always check `is_authenticated` first.
- **Returning error details that leak implementation info:** `return JsonResponse({'error': f'Not found: {e}'}, status=404)` exposes ORM query details. Use generic messages.
- **Using `character.delete()` in except blocks without logging:** The `CharacterCreateAPI` catches exceptions and deletes partially-created characters, but a broad `except Exception` can mask real bugs. Log the traceback before cleaning up.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CSRF protection | Custom token validation | Django's built-in `CsrfViewMiddleware` | Already active in middleware stack; just stop bypassing it |
| Authentication checks | Per-method `if not request.user.is_authenticated` | Django's `LoginRequiredMixin` or `login_required` decorator | Consistent, handles redirects, DRY |
| JSON schema validation | Manual key-by-key checking | `jsonschema` library or Pydantic | Declarative schemas catch drift automatically |
| V5 rule validation on server | Duplicate frontend JS logic in Python | Shared validation constants between frontend and backend | Single source of truth for dot pools, maximums |
| Input sanitization for export | Custom regex patterns | Keep existing `sanitize_string()` but expand test coverage | The existing approach is sound; it just needs edge case testing |

**Key insight:** Phase 1 is about removing bad practices (csrf_exempt, missing auth), not adding new infrastructure. The Django framework already provides everything needed.

## Common Pitfalls

### Pitfall 1: Removing @csrf_exempt Breaks API Calls from Templates Without CSRF Token
**What goes wrong:** Removing `@csrf_exempt` causes 403 errors for any fetch() call that does not include the `X-CSRFToken` header.
**Why it happens:** Not all frontend fetch() calls were written with CSRF tokens. Developers assumed the exemption would stay.
**How to avoid:** Before removing each `@csrf_exempt`, verify the frontend sends the token. The character_creation.html (line 1412) and character_approval.html (line 353) BOTH already send `X-CSRFToken`. The builder editor.html (line 810) also sends it. The traits API GET endpoints do not need CSRF (GET is safe). The dashboard.html does not make fetch() calls.
**Warning signs:** 403 Forbidden responses after the fix. Test each endpoint manually after removing the decorator.

### Pitfall 2: CharacterCreateAPI Uses create_object Without run_in_main_thread
**What goes wrong:** The `CharacterCreateAPI.post()` method calls `create.create_object()` directly from a Django view without `run_in_main_thread()`. This creates a character in the database but the Evennia idmapper cache may not know about it.
**Why it happens:** Character creation "works" in single-user testing because the web view and game server share the same database. The issue only appears when the game server tries to interact with the character object.
**How to avoid:** Wrap the `create.create_object()` call in `run_in_main_thread()`. However, for character creation specifically, this may be acceptable since characters are not used in-game until approved (they have `location=None`). The risk is LOW for chargen but should be documented as a known limitation. The real fix is needed in Phase 5 (sandbox building) where objects need to be immediately interactive.
**Warning signs:** Characters visible in Django admin but not findable with `@find` in-game without `@reload`.

### Pitfall 3: Exporter @py Line Allows Potential Injection
**What goes wrong:** Line 264 of `exporter.py` generates `@py from evennia import logger; logger.log_info('Web Builder: Project {project_id} ({project.name}) built successfully')`. The `project.name` is interpolated into a `@py` command via f-string. If `project.name` contains crafted content (e.g., single quotes followed by Python code), it could break out of the string.
**Why it happens:** The `project.name` passes through `sanitize_string()` for room names but is used raw in the `@py` line. The sanitizer removes `@` but does not remove single quotes (they are in the allowed character set).
**How to avoid:** Remove the `@py` line entirely. Replace with a `@set` command to tag the sandbox room with a completion timestamp. Or use `sanitize_string()` on the project name in the `@py` line too.
**Warning signs:** Grep for `@py` in exporter output.

### Pitfall 4: Client-Side Validation Not Mirrored on Server
**What goes wrong:** The `character_creation.html` has comprehensive V5 validation (attribute priority pools of 7/5/3, skill pools of 13/9/5, discipline dots exactly 3 with in-clan requirement, advantages exactly 7 points, flaws max 2). But the server-side `enhanced_import_character_from_json()` only validates individual trait min/max values -- it does NOT validate total dot pools, priority distributions, or discipline in-clan requirements.
**Why it happens:** The frontend was built first as a user-facing tool. Server-side validation was deferred. A malicious user can bypass frontend validation by sending a crafted POST directly to the API.
**How to avoid:** Add server-side validation in `CharacterCreateAPI.post()` or in `enhanced_import_character_from_json()` that checks:
  - Total attribute dots match V5 distribution (7+5+3 = 15 additional dots above base 9)
  - Total skill dots match V5 distribution (13+9+5 = 27 total dots)
  - Total discipline dots = 3, with at least 2 in-clan (for non-Caitiff)
  - Total advantage points = 7, flaw points <= 2
  - Individual trait ratings within min/max bounds (this already works)
**Warning signs:** Characters approved with impossible stat distributions (e.g., all attributes at 5).

### Pitfall 5: Builder Ownership Check Missing on Some Views
**What goes wrong:** `GetProjectView` and `ExportProjectView` check `is_public or project.user == request.user` for read access, but there is no check preventing a staff member from reading another staff member's private project if they know the ID. In a MUD context where builders may be working on secret areas, this leaks project data.
**Why it happens:** Staff members are trusted in the Django admin paradigm, but builder projects may contain narrative spoilers that should be access-controlled.
**How to avoid:** This is a minor concern for Phase 1. Document the current behavior and address if the project owner requests access controls. The current `is_public` flag is the intended access control mechanism.
**Warning signs:** Staff members accessing private projects they do not own via direct URL.

### Pitfall 6: CharacterApprovalAPI Has No Double-Action Protection
**What goes wrong:** Two staff members can approve the same character simultaneously. Both POST requests read `bio.approved = False`, both set it to `True`, both save. No error occurs, but if approval triggers side effects (future: placing character in starting room, sending notification), those run twice.
**Why it happens:** No optimistic locking or atomic state check. The approval view does a simple boolean toggle.
**How to avoid:** For Phase 1, add a check: `if bio.approved: return JsonResponse({'error': 'Already approved'}, status=409)`. For a robust fix in Phase 2, use django-fsm-2 with atomic transitions.
**Warning signs:** Audit logs showing double approval timestamps.

## Code Examples

### Example 1: Removing @csrf_exempt from Builder Views
```python
# Source: Direct codebase analysis of beckonmu/web/builder/views.py

# REMOVE these three decorators (lines 70, 146, 167):
# @method_decorator(csrf_exempt, name="dispatch")  -- SaveProjectView
# @method_decorator(csrf_exempt, name="dispatch")  -- DeleteProjectView
# @method_decorator(csrf_exempt, name="dispatch")  -- BuildProjectView

# The frontend already sends CSRF token:
# editor.html line 810: 'X-CSRFToken': '{{ csrf_token }}'

# No other changes needed in the frontend for builder.
```

### Example 2: Removing @csrf_exempt from Traits API Views
```python
# Source: Direct codebase analysis of beckonmu/traits/api.py

# REMOVE @csrf_exempt from ALL 11 views:
# Lines 43, 64, 106, 149, 179, 226, 248, 279, 309, 385, 493

# For GET-only views (TraitCategoriesAPI, TraitsAPI, DisciplinePowersAPI,
# CharacterExportAPI, CharacterAvailableTraitsAPI, PendingCharactersAPI,
# CharacterDetailAPI), CSRF is not checked on GET anyway, so removing
# the decorator has no functional impact.

# For POST views (CharacterValidationAPI, CharacterImportAPI,
# CharacterCreateAPI, CharacterApprovalAPI), the frontend already
# sends X-CSRFToken:
#   - character_creation.html line 1412
#   - character_approval.html line 353
```

### Example 3: Adding Auth Checks to Unprotected Endpoints
```python
# Source: Direct codebase analysis -- these endpoints have NO auth check:
# 1. TraitCategoriesAPI.get()      -- returns all categories (public data, LOW risk)
# 2. TraitsAPI.get()               -- returns all traits (public data, LOW risk)
# 3. DisciplinePowersAPI.get()     -- returns all powers (public data, LOW risk)
# 4. CharacterValidationAPI.post() -- validates char data (no mutation, LOW risk)
# 5. CharacterImportAPI.post()     -- imports char data (MUTATION, HIGH risk)
# 6. CharacterExportAPI.get()      -- exports char by ID (DATA LEAK, MEDIUM risk)
# 7. CharacterAvailableTraitsAPI.get() -- available traits by char ID (DATA LEAK, MEDIUM risk)

# Priority fixes:
# HIGH: CharacterImportAPI -- allows overwriting any character's traits with no auth
# MEDIUM: CharacterExportAPI, CharacterAvailableTraitsAPI -- leak char data by ID
# LOW: Read-only trait catalog endpoints -- public game data, auth optional

# Pattern for CharacterImportAPI fix:
class CharacterImportAPI(BaseAPIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not request.user.is_staff:
            return JsonResponse({'error': 'Staff permissions required'}, status=403)
        # ... existing logic ...
```

### Example 4: Exporter @py Removal
```python
# Source: beckonmu/web/builder/exporter.py line 264

# BEFORE:
lines.append(f"@py from evennia import logger; logger.log_info('Web Builder: Project {project_id} ({project.name}) built successfully')")

# AFTER (option 1 -- just remove it):
# lines.append(f"# Build complete for project {project_id}")

# AFTER (option 2 -- use @set instead of @py):
# lines.append(f"@set {sandbox_alias}/build_completed = True")
```

### Example 5: V5 Server-Side Validation Constants
```python
# Source: character_creation.html lines 319-345 (attribute priorities),
#         lines 404-431 (skill priorities), lines 557-558 (disciplines)

# V5 Character Creation Rules (must be enforced server-side):
V5_CHARGEN_RULES = {
    'attribute_pools': {
        'primary': 7,     # 7 additional dots above base 1
        'secondary': 5,
        'tertiary': 3,
        'total_additional': 15,  # 7 + 5 + 3
        'base_per_attribute': 1,
        'total_attributes': 9,
        'total_dots': 24,  # 9 (base) + 15 (additional)
    },
    'skill_pools': {
        'primary': 13,
        'secondary': 9,
        'tertiary': 5,
        'total': 27,  # 13 + 9 + 5
    },
    'disciplines': {
        'total_dots': 3,
        'min_in_clan': 2,   # At least 2 dots must be in-clan
        'max_per_discipline': 3,
    },
    'advantages': {
        'total_points': 7,
    },
    'flaws': {
        'max_points': 2,
    },
    'attribute_max': 5,
    'skill_max': 5,
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@csrf_exempt` on all API views | Send `X-CSRFToken` header; let middleware validate | Django 1.2+ (always available) | Frontends already do this; just need to stop exempting |
| Boolean `approved` field | State machine with django-fsm-2 | Phase 2 | Phase 1 adds idempotency checks; Phase 2 adds full FSM |
| Client-only V5 validation | Server-side + client-side validation | Phase 1 (this phase) | Prevents invalid characters from being submitted |
| Direct key access on JSON | `.get()` with defaults + schema validation | Phase 1 (this phase) | Prevents KeyError on older project data |

**Deprecated/outdated:**
- `@csrf_exempt` on any mutation endpoint: Should never have been used in a session-authenticated system. Django's CSRF middleware handles everything automatically when the frontend sends the token.
- `@py` in batch exports: Establishes a dangerous pattern. Remove and replace with safe alternatives.

## Open Questions

1. **Should trait catalog endpoints (categories, traits, powers) require authentication?**
   - What we know: These return game rule data (what traits exist, what disciplines are available). This is essentially public game data.
   - What's unclear: Does the game admin want these locked behind login, or are they acceptable as public reference data?
   - Recommendation: Add `login_required` as a low-cost safety measure. If public access is later desired, it can be removed.

2. **How thorough should server-side V5 validation be?**
   - What we know: Frontend validates dot pools, in-clan disciplines, advantage/flaw totals. Server validates individual trait ranges but not totals.
   - What's unclear: Should the server validate ALL V5 rules (priority distribution, in-clan requirements) or just enough to prevent obviously invalid characters?
   - Recommendation: Validate totals (attribute dots, skill dots, discipline dots, advantage/flaw points) and in-clan discipline requirement. Do NOT try to validate priority assignment (which category gets 7/5/3) -- this is hard to reverse-engineer from flat trait data and staff review catches it anyway.

3. **Should the BuildProject.map_data get a schema_version field in Phase 1?**
   - What we know: Prior research flagged JSON schema drift as a moderate pitfall. Adding `schema_version` early prevents migration headaches later.
   - What's unclear: Is this scope creep for Phase 1, or is it foundational enough to include?
   - Recommendation: Add `schema_version: 1` to `get_default_map_data()` and to saved projects, but do NOT build a migration system yet. Just plant the field for Phase 2+ to use.

4. **Should the builder editor save endpoint add concurrency protection in Phase 1?**
   - What we know: The `SaveProjectView` has no optimistic concurrency control. Two simultaneous saves will lose data. Prior research identified this as Critical pitfall C2.
   - What's unclear: Is this a Phase 1 concern (security/correctness) or Phase 2+ concern (builder workflow)?
   - Recommendation: Add a `version` field to `BuildProject` model and basic optimistic concurrency check (reject save if version mismatch). This is a small model change with high safety payoff.

## Detailed Audit Findings

### REVW-01: Character Creation System

**Files:** `traits/api.py`, `traits/utils.py`, `traits/models.py`, `web/templates/character_creation.html`

| Finding | Severity | Issue | Fix |
|---------|----------|-------|-----|
| All traits API endpoints have `@csrf_exempt` | HIGH | CSRF protection completely disabled | Remove decorator; frontend already sends token |
| `CharacterImportAPI` has no auth check | HIGH | Any anonymous user can overwrite character traits | Add `is_authenticated` + `is_staff` check |
| `CharacterExportAPI` has no auth check | MEDIUM | Any user can export any character's data by ID | Add `is_authenticated` + ownership/staff check |
| `CharacterAvailableTraitsAPI` has no auth check | MEDIUM | Leaks character data by ID | Add `is_authenticated` check |
| `CharacterValidationAPI` has no auth check | LOW | Allows anonymous validation (no data mutation) | Add `is_authenticated` check (low priority) |
| No server-side V5 dot pool validation | HIGH | Invalid characters can be submitted via API bypass | Add total dots validation for attributes/skills/disciplines/advantages/flaws |
| `CharacterCreateAPI` calls `create_object` without `run_in_main_thread()` | LOW | Character may not be visible in idmapper cache | Document as known limitation; fix in Phase 5 when it matters for sandbox |
| `CharacterBio.approved` is a simple boolean | MEDIUM | No rejection notes field, no resubmission workflow | Phase 2 adds FSM; Phase 1 adds idempotent approval check |
| Character created with `location=None`, `home=None` | OK | Intentional -- character not placed until approved | Confirmed correct behavior for pending characters |
| `CharacterCreateAPI` exception handling leaks details | LOW | `f'Not found: {e}'` exposes ORM internals | Use generic error messages |

### REVW-02: Grid Builder System

**Files:** `web/builder/views.py`, `web/builder/models.py`, `web/builder/validators.py`, `web/builder/exporter.py`

| Finding | Severity | Issue | Fix |
|---------|----------|-------|-----|
| `SaveProjectView` has `@csrf_exempt` | HIGH | CSRF protection disabled on save | Remove decorator; editor.html already sends token |
| `DeleteProjectView` has `@csrf_exempt` | HIGH | CSRF protection disabled on delete | Remove decorator |
| `BuildProjectView` has `@csrf_exempt` | HIGH | CSRF protection disabled on build | Remove decorator |
| No concurrency control on `SaveProjectView` | MEDIUM | Last-write-wins on simultaneous saves | Add `version` field to model, check on save |
| Exporter line 264 uses `@py` with unsanitized project name | MEDIUM | Potential injection in batch script | Remove `@py` line entirely |
| Exporter line 180 uses direct key access `exit_data['source']` | MEDIUM | `KeyError` if exit data is malformed | Use `.get()` with validation |
| Exporter lines 205-207 use exit name for `@desc`/`@lock` targeting | LOW | Targets wrong object if duplicate names exist | Document; resolved when switching to direct API in Phase 5 |
| Validator only checks room/exit connectivity | LOW | No validation of room data shape (name, description fields) | Add basic shape validation |
| `map_data` has no `schema_version` field | LOW | Future migrations will be harder without version tracking | Add `schema_version: 1` to default data |
| `BuildProject.get_default_map_data()` structure is undocumented | LOW | No formal schema definition | Document expected structure |

### REVW-03: API Security

**Files:** All API views across `traits/api.py` and `web/builder/views.py`

| Endpoint | Auth Check | CSRF | Ownership Check | Status |
|----------|-----------|------|----------------|--------|
| `TraitCategoriesAPI.get()` | NONE | Exempt (GET) | N/A | Add login_required |
| `TraitsAPI.get()` | NONE | Exempt (GET) | N/A | Add login_required |
| `DisciplinePowersAPI.get()` | NONE | Exempt (GET) | N/A | Add login_required |
| `CharacterValidationAPI.post()` | NONE | **EXEMPT** | N/A | Add login_required, remove csrf_exempt |
| `CharacterImportAPI.post()` | NONE | **EXEMPT** | NONE | **CRITICAL**: Add staff_required, remove csrf_exempt |
| `CharacterExportAPI.get()` | NONE | Exempt (GET) | NONE | Add login + ownership/staff check |
| `CharacterAvailableTraitsAPI.get()` | NONE | Exempt (GET) | NONE | Add login + ownership/staff check |
| `PendingCharactersAPI.get()` | Staff | Exempt (GET) | N/A | Remove csrf_exempt (no-op for GET) |
| `CharacterDetailAPI.get()` | Staff | Exempt (GET) | N/A | Remove csrf_exempt (no-op for GET) |
| `CharacterCreateAPI.post()` | Login | **EXEMPT** | Self | Remove csrf_exempt (frontend sends token) |
| `CharacterApprovalAPI.post()` | Staff | **EXEMPT** | N/A | Remove csrf_exempt, add idempotency check |
| `SaveProjectView.post()` | Staff | **EXEMPT** | Owner | Remove csrf_exempt (frontend sends token) |
| `GetProjectView.get()` | Staff | OK (GET) | Public/Owner | OK |
| `DeleteProjectView.delete()` | Staff | **EXEMPT** | Owner | Remove csrf_exempt |
| `BuildProjectView.post()` | Staff | **EXEMPT** | Owner | Remove csrf_exempt |
| `ExportProjectView.get()` | Staff | OK (GET) | Public/Owner | OK |

## Sources

### Primary (HIGH confidence)
- Direct source code analysis of `beckonmu/traits/api.py` (540 lines) -- all 11 API views examined
- Direct source code analysis of `beckonmu/web/builder/views.py` (229 lines) -- all 9 views examined
- Direct source code analysis of `beckonmu/web/builder/exporter.py` (267 lines) -- full exporter examined
- Direct source code analysis of `beckonmu/web/builder/validators.py` (60 lines) -- full validator examined
- Direct source code analysis of `beckonmu/traits/utils.py` (597 lines) -- validation and import functions examined
- Direct source code analysis of `beckonmu/web/templates/character_creation.html` (1,471 lines) -- CSRF handling and V5 validation logic examined
- Direct source code analysis of `beckonmu/web/templates/character_approval.html` -- CSRF handling verified (line 353)
- Direct source code analysis of `beckonmu/web/templates/builder/editor.html` -- CSRF handling verified (line 810)
- [Django CSRF documentation](https://docs.djangoproject.com/en/5.2/howto/csrf/) -- verified X-CSRFToken header pattern

### Secondary (MEDIUM confidence)
- Prior project research in `.planning/research/PITFALLS.md` -- CSRF, concurrency, and injection pitfalls
- Prior project research in `.planning/research/ARCHITECTURE.md` -- approval patterns and bridge layer
- Prior project research in `.planning/research/SUMMARY.md` -- stack verification and phase ordering

### Tertiary (LOW confidence)
- V5 chargen rules extracted from frontend JavaScript constants -- need cross-reference with V5 rulebook

## Metadata

**Confidence breakdown:**
- CSRF findings: HIGH -- verified by direct grep of `csrf_exempt` across entire codebase (14 instances found) and verification that frontends send tokens
- Authentication findings: HIGH -- verified by reading every API view's dispatch/method code
- V5 validation gap: HIGH -- verified by comparing frontend JS validation logic vs server-side `enhanced_import_character_from_json()`
- Builder data integrity: HIGH -- verified by reading exporter key access patterns and validator scope
- Concurrency concern: MEDIUM -- architectural analysis; no production data on actual concurrency issues

**Research date:** 2026-02-03
**Valid until:** 2026-03-03 (stable codebase, no fast-moving dependencies)
