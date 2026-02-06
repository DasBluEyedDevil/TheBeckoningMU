# Codebase Concerns

**Analysis Date:** 2026-02-03

## Incomplete Feature Implementations

### Willpower Reroll System (MEDIUM PRIORITY)

**Issue:** Willpower reroll feature is partially implemented with UI but no backend logic

**Files:**
- `beckonmu/dice/commands.py`
- `beckonmu/dice/WILLPOWER_REROLL_TODO.md`

**Current State:**
- Dice rolls display message: "You may spend 1 Willpower to reroll up to 3 failed dice"
- Command `willpower reroll` does not exist yet
- Infrastructure for state management is missing

**Impact:**
- Players see UI prompts but cannot execute rerolls
- Feature partially implemented creates confusion

**Fix Approach:**
1. Store last roll state in `character.ndb.last_roll` (non-persistent, 30-second timeout)
2. Create `CmdWillpowerReroll` command class
3. Integrate with character Willpower tracking (`character.db.willpower_current`)
4. Add timeout cleanup to clear stale roll states
5. Add comprehensive test coverage (state management, timeouts, edge cases)

**Estimated Effort:** 2-3 hours implementation + testing

---

## Web Builder Incomplete Features

### Trigger UI Not Implemented (MEDIUM PRIORITY)

**Issue:** Trigger system has data model and backend but frontend UI is a stub

**Files:**
- `beckonmu/web/templates/builder/editor.html` (lines 790, 794)
- `WEB_BUILDER_IMPLEMENTATION_PLAN.md`

**Current State:**
```javascript
// In editor.html
function updateTriggersDisplay(triggers) {
    // TODO: Implement trigger list UI
}

function addTrigger() {
    // TODO: Implement trigger creation UI
    alert('Trigger editor coming in Phase 5');
}
```

**Impact:**
- Users cannot manage triggers from web builder
- Triggers can be created via batch scripts but not edited through UI
- Phase 5 promised but not delivered

**Fix Approach:**
1. Implement trigger list UI component
2. Create trigger editor modal/form
3. Add trigger deletion and validation UI
4. Connect to backend trigger endpoints

**Status:** Deferred - Phase 5 incomplete

---

## Test Coverage Gaps

### Core Systems Untested (HIGH PRIORITY)

**Issue:** Multiple critical game systems lack automated test coverage

**Files Without Tests:**
- `beckonmu/dice/tests.py` - Empty skeleton
- `beckonmu/jobs/tests.py` - Minimal coverage
- `beckonmu/bbs/tests.py` - Missing (reference repo had issues noted)
- `beckonmu/boons/tests.py` - Missing (reference repo had issues noted)
- `beckonmu/status/tests.py` - Missing

**What's Missing:**
- Dice system core rolls (DiceResult calculation, edge cases)
- Rouse check mechanics with Blood Potency re-rolls
- Job workflow (create, comment, close cycles)
- BBS operations (create, edit, delete, permissions)
- Boon offer/accept/fulfill lifecycle
- Status gain/loss and political implications

**Impact:**
- Regressions not caught automatically
- Refactoring dangerous without test safety net
- Game-breaking bugs can slip to players

**Fix Approach:**
1. Create test framework for each subsystem
2. Add baseline coverage for happy path scenarios
3. Add edge case tests (boundary conditions, error states)
4. Target 80%+ coverage for core systems
5. Integrate into CI/CD pipeline

**Priority:** Do before major refactoring work

---

## Code Quality Issues

### Large Methods with Multiple Responsibilities (MEDIUM PRIORITY)

**Issue:** Several command implementations combine parsing, validation, execution, and formatting in single large methods

**Examples from Reference Codebase:**
- `CmdStat.func()` in `beckonmu/commands/chargen.py` (350+ lines)
- `CmdBBS` (dispatcher class handling multiple sub-commands)
- `CmdBoons` (dispatcher class handling multiple sub-commands)
- `CmdJobs` (dispatcher class handling multiple sub-commands)

**Impact:**
- Difficult to test individual logic pieces
- High cyclomatic complexity
- Tight coupling between concerns
- Error handling buried in large blocks

**Fix Approach:**
1. Break into smaller functions:
   - `parse_arguments()` - Argument parsing and validation
   - `validate_preconditions()` - Check permissions, state
   - `execute_action()` - Core logic
   - `format_response()` - Output generation
2. Create separate command classes for each action (CmdJobsList, CmdJobsCreate, etc.)
3. Keep methods under 50 lines where practical

**Priority:** Medium - refactor alongside test addition

---

## Data Architecture Concerns

### Hardcoded Game Data (MEDIUM PRIORITY)

**Issue:** Game data (clans, skills, attributes, disciplines) hardcoded in Python dictionaries

**Files:**
- `beckonmu/world/v5_data.py` - Centralized but still hardcoded
- `beckonmu/commands/chargen.py` - Imports from v5_data
- `beckonmu/traits/management/commands/seed_traits.py` - Uses v5_data

**Current State:** Data consolidated to v5_data.py as single source of truth (Session 19 improvement)

**Limitations:**
- Game designers cannot add clans/skills without code changes
- No dynamic validation in admin interface
- Data changes require redeployment
- Migrations needed for new fields

**Impact:**
- Game content not updateable in production
- Staff cannot quickly add/modify traits
- Delays gameplay improvements

**Fix Approach:**
1. Create Django models for game data:
   - `ClanDefinition` with restrictions
   - `TraitDefinition` with validation rules
   - `DisciplineDefinition` with power requirements
2. Implement admin interface for trait management
3. Add management commands for data import/export
4. Migrate existing v5_data.py to database

**Priority:** Low - Game content is stable; not blocking new features

---

## Security Improvements Completed

### Web Builder Input Sanitization (RESOLVED)

**Status:** Fixed in Session 19 (Commit ea3785e)

**What Was Done:**
- Replaced blacklist regex with whitelist approach in `sanitize_string()`
- Added `sanitize_alias()` for alias validation
- Added `sanitize_lock()` for lock string parsing
- Added `sanitize_typeclass()` for typeclass path validation
- Fixed all injection vectors in `generate_batch_script()`

**Files Updated:** `beckonmu/web/builder/exporter.py`

**Remaining Consideration:** Monitor for batch script edge cases in production

---

## Exception Handling Improvements Completed

### Broad Exception Catches (RESOLVED)

**Status:** Fixed in Session 19 (Commit 9b37e4c)

**What Was Done:**
- Replaced `except Exception` with specific exception types in:
  - `bbs/commands.py` (IntegrityError, ValidationError, OperationalError)
  - `traits/api.py` (ValueError, KeyError, ObjectDoesNotExist)
  - `dice/commands.py` (ValueError, AttributeError, KeyError)
- Fixed bare `except:` clauses to use `except Exception:`

**Impact:** Better error tracking, hidden bugs now surface

---

## Known Bugs from Reference Audit

**Reference Document:** `reference repo/BeckoningMU-master/CODEBASE_FIXES_TODO.md`

### BUG-002: Trait Utilities Bridge Functions

**Status:** Tests added (test_trait_utils.py indicates fix verified)

**Files:** `beckonmu/commands/v5/utils/trait_utils.py`

### BUG-004, BUG-005: Discipline Rouse Check Integration

**Status:** Tests added (test_discipline_utils.py indicates fixes verified)

**Files:** `beckonmu/commands/v5/utils/discipline_utils.py`

---

## Documentation Gaps

### System Design Undocumented (LOW PRIORITY)

**Issue:** Complex systems lack design documentation for maintainers

**Missing Documentation:**
- Dice rolling probability tables and edge cases
- Blood Potency re-roll mechanics
- Status system calculation and limits
- Boon fulfillment state machine
- V5 rules interpretation for house rules

**Files Needing Docs:**
- `beckonmu/world/v5_dice.py` - Dice mechanics
- `beckonmu/commands/v5/utils/blood_utils.py` - Blood mechanics
- `beckonmu/boons/models.py` - Boon lifecycle
- `beckonmu/status/models.py` - Status system

**Fix Approach:**
1. Add detailed docstrings to complex functions
2. Create `DESIGN.md` files in each subsystem
3. Include examples and edge cases
4. Document V5 rule interpretations

**Priority:** Low - code is functional but hard to maintain

---

## Performance Considerations

### Database Query Optimization (LOW PRIORITY)

**Issue:** No analysis has been done for N+1 query problems

**Areas at Risk:**
- Character attribute/skill loading (could load all at once)
- Boon listing with creditor/debtor lookups
- Job comments with user lookups
- Status visibility calculations

**Fix Approach:**
1. Profile hot code paths with django-debug-toolbar
2. Add database indexes for common filters
3. Use `select_related()` and `prefetch_related()` in querysets
4. Cache frequently-accessed data (traits, disciplines)

**Priority:** Low - Not blocking; monitor if player counts increase

---

## Scaling Limits

### Codebase Structure Assumptions (LOW PRIORITY)

**Issue:** Code assumes single-instance deployment, not horizontally scalable

**Assumptions:**
- `character.ndb.*` (non-persistent attributes) stored in memory only
- Roll state stored in `character.ndb.last_roll` - lost on server restart
- No distributed locking for concurrent command execution
- No session sharing mechanism

**Impact:**
- Multi-server deployments would lose non-persistent state
- Horizontal scaling would require refactoring
- Load balancing requires sticky sessions

**Current Status:** Single-instance deployment on record, not limiting

**Fix Approach for Future:**
1. Migrate `ndb` state to redis cache with TTL
2. Add distributed locking for command serialization
3. Implement session affinity or session server

**Priority:** Deferred - Not relevant until scaling needed

---

## Technical Debt Summary

| Area | Severity | Status | Effort | Blocker |
|------|----------|--------|--------|---------|
| Willpower Reroll Implementation | MEDIUM | Incomplete | 2-3h | No |
| Web Builder Trigger UI | MEDIUM | Incomplete | 4-6h | No |
| Test Coverage (Core Systems) | HIGH | Missing | 3-4d | Yes* |
| Large Method Refactoring | MEDIUM | Identified | 1-2d | No |
| Hardcoded Game Data | MEDIUM | Mitigated | 2-3d | No |
| Database Query Optimization | LOW | Unaddressed | 1-2d | No |
| Horizontal Scaling | LOW | Not Needed | TBD | No |

**\*Blocks:** Safe refactoring; production deployments without safety net

---

*Concerns audit: 2026-02-03*
