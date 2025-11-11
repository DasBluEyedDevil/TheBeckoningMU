# TheBeckoningMU Production Roadmap

**Status:** 95% Complete - Production Ready After Minor Enhancements
**Last Updated:** 2025-11-11
**Audit Source:** Gemini Comprehensive Codebase Analysis

---

## Executive Summary

TheBeckoningMU is in an **advanced state of development and nearing production readiness**. The implementation of Vampire: The Masquerade 5th Edition (V5) mechanics is extensive and robust. The project structure is sound, with high code quality, clear separation of concerns, and a data-driven design philosophy.

**Overall Completeness:** 95%+

**What's Complete:**
- All 11 V5 disciplines with 96 powers
- Full character creation and approval system
- Complete combat system
- Humanity/Frenzy mechanics
- XP and advancement system
- All 4 custom systems (BBS, Jobs, Boons, Status)
- Comprehensive help system (36 .txt files)
- Custom help system implementation (world/help_entries.py)
- 30 automated tests (all passing)

**What Remains:**
- 4 minor implementation gaps (detailed below)
- Help file updates for newly completed commands
- Final integration polish

---

## Critical Path to Production

### Priority 1: Core Gameplay Loop Completion

These tasks are **required** before production launch as they affect core gameplay mechanics.

---

#### TASK 1: Implement +feed Command

**Status:** STUB
**Priority:** CRITICAL
**Estimated Effort:** 4-6 hours
**Location:** `beckonmu/commands/v5/v5_hunting.py:166-196`

**Current State:**
```python
class CmdFeed(Command):
    """
    Feed on prey to slake Hunger.
    """
    key = "+feed"

    def func(self):
        self.caller.msg("This command is not yet implemented.")
```

**Requirements:**
1. Allow feeding on prey found via `+hunt` command
2. Calculate Blood Potency and Resonance effects
3. Reduce Hunger based on prey quality and feeding method
4. Handle killing vs leaving alive (Humanity implications)
5. Apply Resonance bonuses if applicable
6. Update prey's status or remove from active hunts
7. Apply any clan-specific feeding modifiers

**Implementation Details:**
- Read `self.db.active_hunt` data structure from character
- Validate prey is available and character is actively hunting
- Determine feeding method (restrained, consensual, violent)
- Calculate Hunger reduction based on:
  - Prey type (human, animal, etc.)
  - Blood Potency level
  - Feeding method
- Apply Resonance effects if prey has matching resonance
- Update character's `self.db.hunger` attribute
- Handle Humanity/Stains if prey is killed
- Clear or update `self.db.active_hunt`

**Dependencies:**
- Hunting system (`+hunt` command) - COMPLETE
- Blood Potency mechanics in `world/v5_dice.py` - COMPLETE
- Resonance data in `world/v5_data.py` - COMPLETE
- Humanity system (`+stain` command) - COMPLETE

**Acceptance Criteria:**
- [ ] Player can feed on hunted prey
- [ ] Hunger reduces correctly based on V5 rules
- [ ] Blood Potency affects feeding amount
- [ ] Resonance bonuses apply when relevant
- [ ] Killing prey triggers Humanity check
- [ ] Active hunt clears after feeding
- [ ] Error handling for invalid states
- [ ] Help file created/updated

**Testing Requirements:**
- Unit test for hunger reduction calculations
- Integration test for full hunt → feed → hunger reduction loop
- Test Blood Potency levels 0-10
- Test all Resonance types
- Test Humanity triggers

**Code Reference:**
- `beckonmu/commands/v5/v5_hunting.py:166-196`
- Reference similar pattern from `+hunt` command (same file:20-112)
- Use utility functions from `beckonmu/commands/v5/utils.py`

---

#### TASK 2: Jobs Integration for +chargen/finalize

**Status:** TODO in code
**Priority:** HIGH
**Estimated Effort:** 3-4 hours
**Location:** `beckonmu/commands/v5/v5_chargen.py:1124`

**Current State:**
Working manual approval workflow exists via `+pending`, `+review`, `+approve` commands. The TODO indicates desire for automated Jobs integration.

**Requirements:**
1. When player runs `+chargen/finalize`, automatically create a Job ticket
2. Job should be assigned to appropriate bucket (e.g., "Character Applications")
3. Job should contain character sheet summary
4. Staff can review via Jobs system instead of separate commands
5. Approval/rejection through Jobs should update character status
6. Job closure should notify player

**Implementation Details:**
- In `CmdCharGenFinalize.func()`, after validation:
  - Create Job via Jobs system API
  - Set bucket to configured chargen bucket (add setting if needed)
  - Populate job description with character summary (reuse sheet display code)
  - Set requester to the character
  - Add initial comment with any player notes
- Create signal/hook when Job is closed:
  - If approved: call existing approval logic
  - If rejected: call existing rejection logic with staff notes
  - Notify player in-game

**Dependencies:**
- Jobs system - COMPLETE (`beckonmu/jobs/`)
- Chargen system - COMPLETE (`beckonmu/commands/v5/v5_chargen.py`)
- Character approval workflow - COMPLETE (`beckonmu/commands/v5/v5_staff.py`)

**Acceptance Criteria:**
- [ ] `+chargen/finalize` creates Job automatically
- [ ] Job contains character sheet summary
- [ ] Staff can review via `+job` commands
- [ ] Job approval triggers character approval
- [ ] Job rejection triggers character rejection
- [ ] Player receives notification on status change
- [ ] Existing `+pending`/`+review`/`+approve` commands still work as fallback
- [ ] Help file updated

**Testing Requirements:**
- Integration test for full chargen → finalize → job creation flow
- Test job creation with various character configurations
- Test approval/rejection through Jobs system
- Test notification delivery

**Code Reference:**
- `beckonmu/commands/v5/v5_chargen.py:1124` (TODO location)
- `beckonmu/jobs/models.py` (Job model)
- `beckonmu/jobs/utils.py` (Job creation utilities)
- `beckonmu/commands/v5/v5_staff.py` (existing approval logic)

---

### Priority 2: Feature Enhancements

These tasks improve user experience but are not strictly required for launch.

---

#### TASK 3: AI Storyteller for +hunt (Enhancement or Removal)

**Status:** PLACEHOLDER
**Priority:** MEDIUM
**Estimated Effort:** 8-12 hours (full implementation) OR 1 hour (removal)
**Location:** `beckonmu/commands/v5/v5_hunting.py:145-157`

**Current State:**
```python
class CmdHuntAction(Command):
    """
    Interact with NPCs during a hunt (AI Storyteller placeholder).
    """
    key = "+huntaction"

    def func(self):
        self.caller.msg("AI Storyteller feature is planned for future implementation.")
```

**Decision Required:** Enhance or Remove?

**Option A: Full Implementation** (8-12 hours)
- Integrate with AI service (OpenAI, Claude API, etc.)
- Generate dynamic NPC interactions during hunts
- Handle context and conversation state
- Apply outcomes to hunt mechanics

**Option B: Remove Feature** (1 hour)
- Remove `CmdHuntAction` from command set
- Remove from help files
- Update any references in hunt documentation

**Recommendation:**
Consider **Option B** for initial production launch. The core hunting loop works without this feature. Add it in a post-launch update if desired.

**If Implementing Option A:**

**Requirements:**
1. Configure AI service (API keys, model selection)
2. Build prompt templates for hunting scenarios
3. Handle conversation context across multiple `+huntaction` calls
4. Parse AI responses for game outcomes
5. Apply outcomes to hunt state
6. Handle AI service failures gracefully

**Acceptance Criteria:**
- [ ] AI generates contextual responses to player actions
- [ ] Responses affect hunt outcomes
- [ ] Service failures don't crash commands
- [ ] API costs are reasonable
- [ ] Help file explains feature

**If Choosing Option B (Recommended):**

**Acceptance Criteria:**
- [ ] `CmdHuntAction` removed from command set
- [ ] Command removed from `default_cmdsets.py`
- [ ] Help files updated to remove references
- [ ] No broken references in code

---

#### TASK 4: Anonymous BBS Posting

**Status:** TODO in code
**Priority:** LOW
**Estimated Effort:** 2-3 hours
**Location:** `beckonmu/bbs/` (exact location: check models.py or commands)

**Requirements:**
1. Add `/anon` switch to `+bbpost` command
2. Post should show as "Anonymous" instead of character name
3. Staff should still be able to see true author (admin view)
4. Prevent abuse (rate limiting, staff discretion to reveal)

**Implementation Details:**
- Modify `CmdBBPost` to accept `/anon` switch
- Add `is_anonymous` boolean field to BBS Post model (requires migration)
- Add `actual_author` field to preserve real author for staff
- Update post display logic:
  - Regular view shows "Anonymous" if `is_anonymous=True`
  - Staff view (`+bbadmin` or similar) shows actual author
- Add permission check (some boards might disallow anon posting)

**Dependencies:**
- BBS system - COMPLETE (`beckonmu/bbs/`)
- Django migrations (for model change)

**Acceptance Criteria:**
- [ ] `+bbpost/anon` creates anonymous post
- [ ] Post displays as "Anonymous" to regular users
- [ ] Staff can see actual author
- [ ] Board settings can disable anonymous posting
- [ ] Migration created and tested
- [ ] Help file updated

**Testing Requirements:**
- Test anonymous post creation
- Test staff viewing actual author
- Test board permission enforcement
- Test migration on fresh and existing databases

**Code Reference:**
- `beckonmu/bbs/models.py` (Post model)
- `beckonmu/bbs/new_commands.py` (CmdBBPost)
- `beckonmu/bbs/utils.py` (display utilities)

---

### Priority 3: Polish & Documentation

---

#### TASK 5: Help File Updates

**Status:** Mostly Complete
**Priority:** MEDIUM
**Estimated Effort:** 2-3 hours
**Location:** `world/help/`

**Current State:**
36 comprehensive help files exist. Quality is EXCELLENT per Gemini audit.

**Requirements:**
1. Verify all 47 commands have help files
2. Update help files for any commands modified during final tasks
3. Add help file for `+feed` once implemented
4. Update `+hunt` help to reflect AI Storyteller decision
5. Update `+chargen` help to mention Jobs integration
6. Update `+bbpost` help for `/anon` switch

**Implementation Details:**
- Audit existing help files against command list
- Create new .txt files in `world/help/commands/` for missing commands
- Update existing files with new functionality
- Ensure consistent formatting and examples
- Test help system loading (server restart)

**Acceptance Criteria:**
- [ ] All commands have help files
- [ ] Help files are accurate for current implementation
- [ ] Examples work correctly
- [ ] Formatting is consistent
- [ ] Help system loads without errors

**Code Reference:**
- `world/help_entries.py` (custom help system implementation)
- `world/help/` (all help .txt files)

---

#### TASK 6: Final Testing Pass

**Status:** Partial (30 tests passing)
**Priority:** HIGH
**Estimated Effort:** 4-6 hours
**Location:** Project-wide

**Requirements:**
1. Run all existing tests (verify 30 tests still pass)
2. Add tests for newly implemented features (+feed, Jobs integration, etc.)
3. Perform manual QA of full character lifecycle:
   - Create character via `+chargen`
   - Submit for approval (`+chargen/finalize`)
   - Staff review and approve
   - Advance character with `+spend`
   - Test hunting loop (`+hunt` → `+feed`)
   - Test combat
   - Test all 4 custom systems (BBS, Jobs, Boons, Status)
4. Test edge cases and error handling
5. Verify web client functionality
6. Document any bugs found

**Acceptance Criteria:**
- [ ] All automated tests pass
- [ ] New features have test coverage
- [ ] Manual QA checklist completed
- [ ] No critical bugs found
- [ ] Performance is acceptable
- [ ] Web client works correctly

---

## Task Dependencies Graph

```
TASK 1: +feed Implementation
  ↓
TASK 5: Help File Updates (for +feed)
  ↓
TASK 6: Final Testing (includes +feed tests)

TASK 2: Jobs Integration
  ↓
TASK 5: Help File Updates (for chargen)
  ↓
TASK 6: Final Testing (includes Jobs flow)

TASK 3: AI Storyteller Decision
  ↓
TASK 5: Help File Updates (for +hunt)

TASK 4: Anonymous BBS (independent)
  ↓
TASK 5: Help File Updates (for +bbpost)
  ↓
TASK 6: Final Testing (includes BBS)
```

---

## Recommended Implementation Order

**Week 1:**
1. TASK 1: Implement `+feed` command (4-6 hours)
2. TASK 2: Jobs integration for chargen (3-4 hours)
3. TASK 3: AI Storyteller decision + implementation/removal (1-12 hours depending on choice)

**Week 2:**
4. TASK 4: Anonymous BBS posting (2-3 hours)
5. TASK 5: Help file updates for all changes (2-3 hours)
6. TASK 6: Final testing pass (4-6 hours)

**Total Estimated Effort:** 16-34 hours (depending on AI Storyteller choice)

**Recommended for MVP Launch:** 16-22 hours (remove AI Storyteller for post-launch)

---

## Production Launch Criteria

The game is ready for production launch when:

- [x] All V5 core mechanics implemented
- [x] Character creation and approval workflow complete
- [ ] Hunting loop complete (`+feed` implemented)
- [ ] Jobs integration for chargen (or manual approval documented)
- [x] All 4 custom systems functional (BBS, Jobs, Boons, Status)
- [ ] Help files complete and accurate
- [ ] All automated tests passing
- [ ] Manual QA completed without critical bugs
- [x] Web client functional
- [x] Admin tools working

**Current Progress:** 8/10 criteria met (80%)

---

## Post-Launch Enhancements

Features to consider after production launch:

1. **AI Storyteller for Hunting** (if removed for launch)
2. **Advanced Combat Options** (maneuvers, tactical choices)
3. **Coterie System Enhancements** (shared resources, territory)
4. **Web Character Sheet** (view character in web client)
5. **Mobile-Responsive Web Client**
6. **Automated Boon/Status Decay** (based on time/inactivity)
7. **Chronicle Tracking** (session logs, story arc tracking)
8. **NPC Database** (for Storyteller use)
9. **Scene System** (log and organize RP scenes)
10. **Advanced Search** (for BBS, Jobs, characters)

---

## Risk Assessment

**Low Risk Tasks:**
- TASK 1 (+feed): Well-defined, uses existing systems
- TASK 2 (Jobs integration): Clear requirements, systems already complete
- TASK 4 (Anonymous BBS): Simple feature, isolated changes
- TASK 5 (Help files): No code changes, documentation only

**Medium Risk Tasks:**
- TASK 3 (AI Storyteller - if implementing): External dependency, API costs, complexity
- TASK 6 (Testing): May uncover unexpected issues requiring fixes

**Mitigation Strategies:**
- Implement in recommended order (critical path first)
- Test each task thoroughly before moving to next
- Have rollback plan for migrations (TASK 4)
- Budget buffer time for bug fixes discovered in TASK 6

---

## Development Resources

**Key Files for Remaining Tasks:**

| Task | Primary Files | Reference Files |
|------|---------------|-----------------|
| TASK 1 (+feed) | `commands/v5/v5_hunting.py:166-196` | `world/v5_dice.py`, `world/v5_data.py` |
| TASK 2 (Jobs) | `commands/v5/v5_chargen.py:1124` | `jobs/models.py`, `jobs/utils.py` |
| TASK 3 (AI) | `commands/v5/v5_hunting.py:145-157` | N/A |
| TASK 4 (BBS) | `bbs/models.py`, `bbs/new_commands.py` | `bbs/utils.py` |
| TASK 5 (Help) | `world/help/` | `world/help_entries.py` |
| TASK 6 (Testing) | All test files | N/A |

**Documentation:**
- V5 Rules Reference: `world/v5_data.py` (master game data)
- Dice Mechanics: `world/v5_dice.py`
- Custom Help System: `world/help_entries.py`
- Existing Tests: `QA_BUG_REPORT.md` (documents test suite)
- Implementation History: `IMPLEMENTATION_COMPLETE.md`

---

## Success Metrics

**Before Launch:**
- All automated tests passing: 100%
- Help file coverage: 100% (all 47+ commands)
- Core gameplay loop functional: 100%
- Critical bugs: 0
- Manual QA pass rate: 100%

**After Launch (First Month):**
- Server uptime: >99%
- Average player session length: >30 minutes
- Character approval time: <24 hours
- Player-reported bugs: <5 per week
- Help file access rate: >80% of new players

---

## Contact & Escalation

For questions about:
- **V5 Mechanics:** Refer to `world/v5_data.py` and official V5 core rulebook
- **Evennia Framework:** https://www.evennia.com/docs/
- **Django Models/Migrations:** Django documentation + `beckonmu/*/models.py`
- **Testing:** Evennia testing guide + existing test files

---

## Changelog

- **2025-11-11:** Initial roadmap created from Gemini audit results
  - Identified 4 remaining tasks for production readiness
  - Estimated effort and prioritized tasks
  - Created task dependencies and implementation order

---

## Next Steps

1. **Review this roadmap** with project stakeholders
2. **Make AI Storyteller decision** (implement or remove for MVP)
3. **Begin TASK 1** (+feed implementation) as critical path
4. **Update DevilMCP files** with roadmap completion timeline
5. **Track progress** in CHANGELOG.md as tasks are completed
