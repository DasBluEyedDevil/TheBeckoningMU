# V5 Implementation Roadmap for TheBeckoningMU

**Version**: 2.0 (Revised)
**Created**: 2025-10-19
**Purpose**: Dependency-ordered implementation plan integrating core MUSH infrastructure with V5 mechanics, based on analysis of the reference repository.

---

## Table of Contents
1. [Architectural Foundations](#architectural-foundations)
2. [Implementation Phases](#implementation-phases)
3. [File Organization](#file-organization)
4. [Data Models](#data-models)
5. [Testing Strategy](#testing-strategy)
6. [Risks & Mitigations](#risks--mitigations)

---

## Architectural Foundations

### Core Design Principles (Learned from Reference Repo Failures)

**AVOID**:
- ❌ Monolithic switch-based commands
- ❌ Hardcoded game data in Python files
- ❌ Recording stats without implementing mechanics
- ❌ Bare exception handling
- ❌ Development without tests

**REPLICATE** (from successful reference repo refactors):
- ✅ Small, single-responsibility commands
- ✅ Shared utility modules (`utils.py`)
- ✅ Database-driven models for game systems (`models.py`)
- ✅ Test-driven development
- ✅ Clear separation of concerns (commands, models, utils)

### V5 Data Storage Architecture

All V5-specific data will be stored on `Character.db.*` as planned. This remains a sound approach.

### Command Organization Pattern

The V5 command structure will follow the established pattern. MUSH infrastructure systems will be organized into their own app-like directories (e.g., `beckonmu/bbs/`, `beckonmu/jobs/`) to maintain modularity, mirroring the successful patterns in the reference repository.

---

## Implementation Phases

The roadmap is now divided into MUSH infrastructure setup, core V5 mechanics, and advanced social/mechanical systems.

### **PART I: MUSH INFRASTRUCTURE**

### Phase 0: Project Setup & Architecture
**Goal**: Establish foundation before feature development.
**Complexity**: Simple
**Dependencies**: None
**Type**: New Code

**Deliverables**:
- [ ] Create `beckonmu/commands/v5/` directory structure.
- [ ] Create `beckonmu/commands/v5/utils/` for shared logic.
- [ ] Create `beckonmu/world/v5_data.py` (configuration) and `v5_dice.py` (dice engine).
- [ ] Set up test directory: `beckonmu/tests/v5/`.
- [ ] Document architectural decisions in `beckonmu/commands/v5/README.md`.

**Testing**: Directory structure exists, imports work.

---

### Phase 1: Help System
**Goal**: Implement a file-based help entry system for easy documentation.
**Complexity**: Low
**Dependencies**: Phase 0
**Type**: Adapted from Reference Repo

**Reference Repo Pattern**: `reference-repo/world/help_entries.py`

**Deliverables**:
- [ ] Create `beckonmu/world/help_entries.py` to load help files from `beckonmu/world/help/`.
- [ ] Configure `settings.FILE_HELP_ENTRY_MODULES` to point to the new module.
- [ ] Create initial help file structure in `beckonmu/world/help/general/`.
- [ ] Write a test help file (e.g., `connect.txt`).

**Testing**: `help connect` command displays the content from the text file.

---

### Phase 2: BBS System
**Goal**: Implement a bulletin board system for player communication.
**Complexity**: Medium
**Dependencies**: Phase 0
**Type**: Adapted from Reference Repo

**Reference Repo Pattern**: `reference-repo/bbs/new_commands.py`, `reference-repo/bbs/models.py`, `reference-repo/bbs/bbs_utils.py`

**Deliverables**:
- [ ] Create `beckonmu/bbs/` application directory.
- [ ] Port `Board`, `Post`, `Comment` models to `beckonmu/bbs/models.py`.
- [ ] Adapt `bbs_utils.py` logic into `beckonmu/bbs/utils.py`.
- [ ] Implement focused commands (`CmdBBS`, `CmdBBSRead`, `CmdBBSPost`) in `beckonmu/bbs/commands.py`.
- [ ] Create a `BBSCmdSet` and add it to default character cmdsets.

**Testing**: Can create boards (`+bbadmin`), post messages (`+bbpost`), read messages (`+bbs`), and comment (`+bbcomment`).

---

### Phase 3: Jobs System
**Goal**: Implement a ticket/job tracking system for admin requests and chargen approval.
**Complexity**: Medium
**Dependencies**: Phase 0
**Type**: Adapted from Reference Repo

**Reference Repo Pattern**: `reference-repo/jobs/new_commands.py`, `reference-repo/jobs/models.py`, `reference-repo/jobs/utils.py`

**Deliverables**:
- [ ] Create `beckonmu/jobs/` application directory.
- [ ] Port `Job`, `Bucket`, `Comment` models to `beckonmu/jobs/models.py`.
- [ ] Adapt `utils.py` logic into `beckonmu/jobs/utils.py`.
- [ ] Implement player (`myjobs/create`) and admin (`job/assign`) commands in `beckonmu/jobs/commands.py`.
- [ ] Create a `JobsCmdSet` and add to default cmdsets.
- [ ] **Integration Point**: `CmdChargenFinalize` (Phase 9) will be modified to create a job in an "Approval" bucket.

**Testing**: Can create a job (`myjobs/create`), admin can see and assign it.

---

### **PART II: CORE V5 MECHANICS**

### Phase 4: Trait System Foundation
**Goal**: Database-driven trait system for attributes and skills.
**Complexity**: Medium
**Dependencies**: Phase 0
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/utils/trait_utils.py` with trait manipulation functions.
- [ ] `beckonmu/world/v5_data.py` - Define all attributes/skills.
- [ ] Modify `beckonmu/typeclasses/characters.py`: `at_object_creation()` to initialize `char.db.stats`.

**Testing**: Unit tests for all `trait_utils.py` functions.

---

### Phase 5: Dice Rolling Engine
**Goal**: Complete V5 dice mechanics (Hunger dice, Rouse checks).
**Complexity**: Complex
**Dependencies**: Phase 4
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/world/v5_dice.py` - Complete `V5DiceRoller` class.
- [ ] `beckonmu/commands/v5/dice.py` - `CmdRoll`, `CmdRollStat`, `CmdRouseCheck`.

**Testing**: Rigorous unit tests for all dice outcomes (criticals, messy criticals, bestial failures).

---

### Phase 6: Blood Systems (Hunger, Blood Potency, Resonance)
**Goal**: Core vampire resource management.
**Complexity**: Medium
**Dependencies**: Phase 5
**Type**: New Code

**Deliverables**:
- [ ] Modify `beckonmu/typeclasses/characters.py` with `char.db.vampire` structure.
- [ ] `beckonmu/commands/v5/blood.py`: `CmdFeed`, `CmdHunger`, `CmdBloodSurge`.
- [ ] `beckonmu/commands/v5/utils/blood_utils.py` for backend logic.
- [ ] **Add Resonance tracking**: Store resonance type when feeding.

**Testing**: Hunger clamps to 0-5, Rouse checks increase Hunger, feeding reduces it and tracks Resonance.

---

### Phase 7: Clan System
**Goal**: Clan selection, banes, and compulsions.
**Complexity**: Medium
**Dependencies**: Phase 6
**Type**: New Code

**Deliverables**:
- [ ] Expand `beckonmu/world/v5_data.py` with all clan data.
- [ ] `beckonmu/commands/v5/utils/clan_utils.py` for clan-specific logic.
- [ ] Modify `characters.py` to handle clan discipline validation.

**Testing**: In-clan vs. out-of-clan discipline costs are different.

---

### Phase 8: Basic Discipline Framework
**Goal**: A framework for discipline powers, activation, and costs.
**Complexity**: Complex
**Dependencies**: Phase 7
**Type**: New Code

**Deliverables**:
- [ ] Expand `beckonmu/world/v5_data.py` with discipline powers (Levels 1-5).
- [ ] `beckonmu/commands/v5/disciplines.py`: `CmdActivatePower`.
- [ ] `beckonmu/commands/v5/utils/discipline_utils.py` for activation logic.
- [ ] **Check Resonance bonuses** when activating discipline powers.
- **Note**: Start with simple/passive powers (e.g., Celerity passive, Fortitude Resilience).

**Testing**: Power activation triggers a Rouse check and applies simple effects. Resonance grants +1 die.

---

### Phase 9: Character Creation Flow
**Goal**: Integrated chargen using all implemented V5 systems.
**Complexity**: Complex
**Dependencies**: Phases 3, 4, 5, 6, 7, 8
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/chargen.py` with a full suite of chargen commands.
- [ ] `beckonmu/commands/v5/utils/chargen_utils.py` for validation logic.
- [ ] **Add Predator Type selection** (merge Phase 11 here).
- [ ] **Add Skill Specialties selection**.
- [ ] **Integration**: `CmdChargenFinalize` creates a job in the "Approval" bucket (from Phase 3).

**Testing**: End-to-end chargen test that creates a valid character and an approval job.

---

### Phase 10: Character Sheet Display
**Goal**: Comprehensive character sheet viewing.
**Complexity**: Simple
**Dependencies**: Phase 9
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/sheet.py`: `CmdSheet`.
- [ ] `beckonmu/commands/v5/utils/display_utils.py` for formatting.

**Testing**: Sheet correctly displays all data from a fully generated character.

---

### **PART III: ADVANCED & SOCIAL SYSTEMS**

### Phase 11: Status System
**Goal**: Implement a system for tracking Camarilla political status.
**Complexity**: Medium
**Dependencies**: Phase 9
**Type**: Adapted from Reference Repo

**Reference Repo Pattern**: `reference-repo/status/new_commands.py`, `reference-repo/status/models.py`, `reference-repo/status/utils.py`

**Deliverables**:
- [ ] Create `beckonmu/status/` application directory.
- [ ] Port `CharacterStatus`, `CamarillaPosition`, `StatusRequest` models to `beckonmu/status/models.py`.
- [ ] Adapt `utils.py` logic into `beckonmu/status/utils.py`.
- [ ] Implement `CmdStatus`, `CmdStatusRequest`, and admin commands in `beckonmu/status/commands.py`.
- [ ] **Integration**: Add Status display to `CmdSheet` (Phase 10).

**Testing**: Can view status, request changes, and admins can approve/deny requests.

---

### Phase 12: Boons System
**Goal**: Implement a system for tracking political favors and debts.
**Complexity**: Medium
**Dependencies**: Phase 11
**Type**: Adapted from Reference Repo

**Reference Repo Pattern**: `reference-repo/boons/new_commands.py`, `reference-repo/boons/models.py`, `reference-repo/boons/utils.py`

**Deliverables**:
- [ ] Create `beckonmu/boons/` application directory.
- [ ] Port `Boon`, `BoonType` models to `beckonmu/boons/models.py`.
- [ ] Adapt `utils.py` logic into `beckonmu/boons/utils.py`.
- [ ] Implement `CmdBoon`, `CmdBoonOffer`, `CmdBoonAccept`, etc., in `beckonmu/boons/commands.py`.
- [ ] **Integration**: Add boon summary to `CmdSheet` (Phase 10).

**Testing**: Can offer, accept, decline, and fulfill boons between characters.

---

### Phase 13: XP/Advancement System
**Goal**: Create a system for awarding and spending experience points.
**Complexity**: Medium
**Dependencies**: Phase 9
**Type**: New Code

**Deliverables**:
- [ ] Add `char.db.experience` dictionary to `characters.py`.
- [ ] Create `CmdXP` (view) and `CmdSpend` (spend XP on traits).
- [ ] Create `beckonmu/commands/v5/utils/xp_utils.py` with cost calculation logic.
- [ ] Create `CmdXPAdmin` for staff to award XP.

**Testing**: Can award XP, view it, and spend it to raise traits with correct costs from V5_REFERENCE_DATABASE.md.

---

### Phase 14: Advanced Disciplines (Amalgams, Rituals)
**Goal**: Implement complex discipline powers.
**Complexity**: Complex
**Dependencies**: Phase 8
**Type**: New Code

**Deliverables**:
- [ ] Implement effects for Dominate, Obfuscate, Blood Sorcery, etc.
- [ ] `beckonmu/commands/v5/utils/discipline_effects.py` for effect handlers and duration tracking.
- [ ] **Amalgam prerequisite checking** in `discipline_utils.py`.

**Testing**: Test amalgam prerequisites, ritual mechanics, and contested rolls.

---

### Phase 15: Combat & Conflict Resolution
**Goal**: V5 combat mechanics (can be narrative-focused).
**Complexity**: Complex
**Dependencies**: Phase 14
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/combat.py`: `CmdAttack`, `CmdDamage`, `CmdHeal`.
- [ ] `beckonmu/commands/v5/utils/combat_utils.py` for damage calculation and health tracking.

**Testing**: Test attack resolution, damage types (superficial vs. aggravated), and healing.

---

### Phase 16: Humanity & Touchstones
**Goal**: Implement the Humanity system, Stains, and Touchstones.
**Complexity**: Medium
**Dependencies**: Phase 6
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/humanity.py`: `CmdTouchstones`, `CmdRemorse`.
- [ ] `beckonmu/commands/v5/utils/humanity_utils.py` for stain and remorse logic.
- [ ] Modify `characters.py` to store `char.db.humanity_data`.

**Testing**: Test Stain accumulation, Remorse rolls, and Humanity loss.

---

### Phase 17: Coterie & Prestation
**Goal**: Formalize group mechanics for coteries and prestation.
**Complexity**: Medium
**Dependencies**: Phase 12
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/social.py`: `CmdCoterie`.
- [ ] `beckonmu/commands/v5/utils/social_utils.py` for coterie management.
- [ ] This phase formalizes the social contracts building on Status and Boons.

**Testing**: Can create and manage coteries, track group resources.

---

### Phase 18: Thin-Bloods (Optional)
**Goal**: Implement Thin-Blood mechanics and Alchemy.
**Complexity**: Medium
**Dependencies**: Phase 9
**Type**: New Code

**Deliverables**:
- [ ] Expand `v5_data.py` with Thin-Blood Alchemy formulae.
- [ ] Create `thin_blood_utils.py` for Alchemy mechanics.
- [ ] Modify chargen to support Thin-Blood option.

**Testing**: Can create Thin-Blood character, use Alchemy, experience sunlight differently.

---

## File Organization (Revised)

```
beckonmu/
├── bbs/
│   ├── commands.py
│   ├── models.py
│   └── utils.py
├── boons/
│   ├── commands.py
│   ├── models.py
│   └── utils.py
├── jobs/
│   ├── commands.py
│   ├── models.py
│   └── utils.py
├── status/
│   ├── commands.py
│   ├── models.py
│   └── utils.py
├── commands/
│   └── v5/
│       ├── chargen.py
│       ├── dice.py
│       ├── sheet.py
│       ├── blood.py
│       ├── disciplines.py
│       ├── combat.py
│       ├── humanity.py
│       ├── social.py
│       └── utils/
│           ├── trait_utils.py
│           ├── chargen_utils.py
│           ├── blood_utils.py
│           ├── clan_utils.py
│           ├── discipline_utils.py
│           ├── xp_utils.py
│           └── ... (etc.)
├── typeclasses/
│   └── characters.py
├── world/
│   ├── help_entries.py
│   ├── v5_data.py
│   └── v5_dice.py
└── tests/
    ├── test_bbs.py
    ├── test_jobs.py
    ├── test_status.py
    ├── test_boons.py
    └── v5/
        ├── test_trait_utils.py
        ├── test_dice.py
        └── ... (etc.)
```

---

## Data Models

### Character.db Structure (Complete)

```python
# Complete V5 data model on Character typeclass

char.db.stats = {
    "attributes": {
        "physical": {"strength": 2, "dexterity": 2, "stamina": 2},
        "social": {"charisma": 2, "manipulation": 2, "composure": 2},
        "mental": {"intelligence": 2, "wits": 2, "resolve": 2}
    },
    "skills": {
        "physical": {"athletics": 1, "brawl": 2, ...},
        "social": {"persuasion": 3, ...},
        "mental": {"academics": 1, ...}
    },
    "specialties": {
        "performance": "Guitar",  # skill: specialty_name
        "brawl": "Grappling"
    },
    "disciplines": {
        "Celerity": {
            "level": 2,
            "powers": ["Cat's Grace", "Fleetness"]
        }
    },
    "approved": False  # For chargen approval workflow
}

char.db.vampire = {
    "clan": "Brujah",
    "generation": 13,
    "blood_potency": 1,
    "hunger": 1,                # 0-5
    "humanity": 7,              # 0-10
    "predator_type": "Scene Queen",
    "current_resonance": "Choleric",  # Tracks last feeding
    "resonance_intensity": 1,   # 0=none, 1=fleeting, 2=intense, 3=dyscrasia
    "bane": "Rage simmers beneath surface",
    "compulsion": "Rebellion"
}

char.db.pools = {
    "health": 5,                # Stamina + 3
    "willpower": 4,             # Composure + Resolve
    "current_health": 5,
    "current_willpower": 4,
    "superficial_damage": 0,
    "aggravated_damage": 0
}

char.db.humanity_data = {
    "convictions": [
        "Art should speak truth to power"
    ],
    "touchstones": [
        {
            "name": "Best friend from mortal days",
            "conviction_index": 0
        }
    ],
    "stains": 0
}

char.db.advantages = {
    "backgrounds": {
        "Fame": 1,
        "Contacts": 2
    },
    "merits": {
        "Beautiful": 2
    },
    "flaws": {
        "Rival": 1
    }
}

char.db.experience = {
    "total_earned": 0,
    "total_spent": 0,
    "current": 0
}

char.db.effects = []  # Ongoing discipline effects
```

---

## Testing Strategy

### Test-Driven Development Approach

Following lessons from reference repo:

1. **Write tests FIRST** before implementing features
2. **Run tests** to verify they fail (RED)
3. **Implement** minimal code to pass tests (GREEN)
4. **Refactor** while keeping tests green (REFACTOR)

### Unit Testing Example

```python
# Example: beckonmu/tests/v5/test_trait_utils.py
from evennia.utils.test_resources import BaseEvenniaTest
from commands.v5.utils.trait_utils import get_trait_value, set_trait_value

class TraitUtilsTestCase(BaseEvenniaTest):
    def test_get_attribute_value(self):
        """Test retrieving attribute value"""
        value = get_trait_value(self.char1, "attribute", "strength")
        self.assertEqual(value, 1)  # Default
```

### Testing Checklist Per Phase

Each phase must verify:
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Edge cases handled
- [ ] Clear error messages
- [ ] No bare exceptions
- [ ] Documentation strings

---

## Risks & Mitigations

### Risk 1: Scope Creep
**Mitigation**: Strict phase ordering, no skipping ahead.

### Risk 2: Hardcoded Data
**Mitigation**: Configuration in `v5_data.py` is read-only reference data.

### Risk 3: Monolithic Commands
**Mitigation**: Follow BBS refactor pattern, each command ONE thing.

### Risk 4: Missing Test Coverage
**Mitigation**: TDD is non-negotiable, aim for >80% coverage.

### Risk 5: Data Migration Pain
**Mitigation**: Design data models completely upfront, write migration scripts.

---

## Appendix: Revised Phase Dependencies Graph

```
Phase 0: Setup
    ├─→ Phase 1: Help System
    ├─→ Phase 2: BBS System
    └─→ Phase 3: Jobs System
         ↓
Phase 4: Trait System
    ↓
Phase 5: Dice Engine
    ↓
Phase 6: Blood Systems + Resonance
    ↓
Phase 7: Clans
    ↓
Phase 8: Basic Disciplines
    ↓
Phase 9: Character Creation (includes Predator Types, depends on 3-8)
    ↓
Phase 10: Character Sheet
    ↓
Phase 11: Status System
    ↓
Phase 12: Boons System
    ↓
Phase 13: XP/Advancement
    ↓
Phase 14: Advanced Disciplines
    ↓
Phase 15: Combat
    ↓
Phase 16: Humanity/Touchstones
    ↓
Phase 17: Coterie/Prestation
    ↓
Phase 18: Thin-Bloods (optional)
```

---

## Success Criteria

### Minimum Viable Product (MVP)
Phases 0-10 complete = playable V5 MUSH with:
- ✅ MUSH infrastructure (BBS, Jobs, Help)
- ✅ Character creation with approval workflow
- ✅ Dice rolling with Hunger mechanics
- ✅ Basic disciplines
- ✅ Character sheets

### Full Launch
Phases 0-17 complete adds:
- ✅ Political systems (Status, Boons)
- ✅ Character advancement (XP)
- ✅ Advanced disciplines
- ✅ Humanity system

---

**Document Version**: 2.0
**Last Updated**: 2025-10-19
**Next Review**: After Phase 3 completion

**Key Changes from v1.0**:
- Added MUSH infrastructure phases (1-3) at the beginning
- Integrated Predator Types into Phase 9 (Character Creation)
- Added Resonance tracking to Phase 6
- Added XP/Advancement as Phase 13
- Added Thin-Bloods as optional Phase 18
- Reorganized social systems (Status, Boons) to come after basic V5 mechanics
- Updated dependency graph to reflect new phase order

---

## ADDENDUM: Missing MUSH Essential Systems

Based on comprehensive MUSH requirements validation, the following systems need to be added:

### Phase 0 Enhancement: Core Evennia Command Verification
**Addition to Phase 0 Deliverables**:
- [ ] Verify core Evennia commands are enabled: `page`, `who`, `look`, `say`, `pose`
- [ ] Test inter-player communication works out-of-box
- [ ] Document any customizations needed for V:tM theme

### Phase 1b: News System (NEW)
**Goal**: Implement read-only news file system for announcements
**Complexity**: Low
**Dependencies**: Phase 1 (Help System)
**Type**: New Code (modeled on Help System)

**Deliverables**:
- [ ] Create `beckonmu/world/news_entries.py` (similar to `help_entries.py`)
- [ ] Create `beckonmu/world/news/` directory for text files
- [ ] Configure `settings.FILE_NEWS_ENTRY_MODULES`
- [ ] Implement `CmdNews` command with categories (general, updates, policy)
- [ ] Write initial news files (welcome.txt, theme.txt)

**Testing**: `news` and `news updates` display content from text files

---

### Phase 6 Enhancement: Automated Blood/Hunger Systems
**Addition to Phase 6 Deliverables**:
- [ ] Create nightly blood expenditure ticker (Evennia Script)
  - Automatically triggers Rouse check when character wakes
  - Handles "rising for the night" mechanic
  - Configurable in `settings.py` (e.g., NIGHTLY_ROUSE_CHECKS = 1)
- [ ] `beckonmu/world/v5_scripts.py` - Persistent game scripts
  - `NightlyRouseScript` - Runs at configured "sunset" time
  - Logs automatic Hunger increases

**Testing**: Character automatically gains Hunger when "day" turns to "night"

---

### Phase 9 Enhancement: Social Conflict System (NEW)
**Goal**: Implement social combat mechanics for debates, interrogations, seductions
**Complexity**: Medium  
**Dependencies**: Phase 5 (Dice Engine), Phase 9 (Character Creation)
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/social_conflict.py`:
  - `CmdPersuade` - Contested Manipulation + Persuasion
  - `CmdIntimidate` - Contested Manipulation + Intimidation  
  - `CmdSeduce` - Contested Charisma + Persuasion/Subterfuge
  - `CmdDebate` - Extended contested social roll
- [ ] `beckonmu/commands/v5/utils/social_conflict_utils.py`:
  - `resolve_social_contest(attacker, defender, skill)`
  - `apply_social_damage(character, damage_type)` - reputation, willpower
  - `check_social_defense(character, attack_type)`

**Integration**: Works with Status system (Phase 11) - victories/defeats affect Status

**Testing**: 
- Social contests resolve with appropriate dice pools
- Outcomes affect character state (willpower, status)
- Extended social conflicts track progress

---

### Phase 11 Enhancement: Status Mechanical Effects
**Addition to Phase 11 Deliverables**:
- [ ] Implement mechanical benefits of Status:
  - `status_utils.py`: `get_status_bonus(character, context)`
  - Apply +1 die per 2 Status dots to relevant Social rolls
  - Grant access control (IC locations, Resources)
  - Integration with Influence Background
- [ ] Add Status effects to social conflict (Phase 9 integration)
- [ ] Display Status bonuses in dice roll output

**Testing**: 
- High-Status character gets dice bonuses in social situations
- Status affects access to IC resources/locations

---

### Phase 16 Enhancement: Frenzy System
**Addition to Phase 16 Deliverables**:
- [ ] `beckonmu/commands/v5/frenzy.py`:
  - `CmdFrenzyCheck` - Resist frenzy (admin/automated)
  - `CmdRideTheWave` - Control frenzy direction
- [ ] `beckonmu/commands/v5/utils/frenzy_utils.py`:
  - `trigger_frenzy_check(character, frenzy_type, difficulty)`
  - `apply_frenzy_effects(character, frenzy_type)` - Fury vs Terror
  - `frenzy_actions(character)` - Automated Beast behavior
- [ ] Frenzy triggers:
  - Fire/sunlight exposure
  - Starvation (Hunger 5)
  - Provocation (insult, attack)
  - Failed Humanity checks

**Integration**: 
- Humanity level affects frenzy resistance (lower Humanity = harder to resist)
- Beast actions can trigger Stains (Phase 16 Humanity system)

**Testing**:
- Frenzy checks trigger at appropriate times
- Different frenzy types have different effects
- Riding the Wave allows partial control

---

### Phase 18b: Background Mechanical Effects (NEW)
**Goal**: Implement mechanical benefits for Backgrounds
**Complexity**: Medium
**Dependencies**: Phase 9 (Chargen), Phase 13 (XP)
**Type**: New Code

**Deliverables**:
- [ ] `beckonmu/commands/v5/backgrounds.py`:
  - `CmdContacts` - Ask contacts for information
  - `CmdInfluence` - Use Influence to affect mortal world
  - `CmdResources` - Access wealth/equipment
  - `CmdHerd` - Feed from Herd (reduce Hunger without hunting)
- [ ] `beckonmu/commands/v5/utils/background_utils.py`:
  - `use_background(character, bg_type, dots_spent, action)`
  - `refresh_background(character, bg_type)` - Time-based recharge
  - `check_background_availability(character, bg_type)`

**Integration**:
- Herd Background integrates with Blood Systems (Phase 6)
- Influence integrates with Status (Phase 11)
- Resources affects equipment availability

**Testing**:
- Backgrounds provide tangible in-game benefits
- Usage is limited (dots spent, time-based refresh)
- Background use can be ICly tracked/logged

---

## Revised Phase Count

With these additions, the roadmap now has:
- **Phase 0**: Setup (enhanced)
- **Phase 1**: Help System
- **Phase 1b**: News System (NEW)
- **Phases 2-8**: MUSH infrastructure + Core V5 (unchanged)
- **Phase 9**: Character Creation + Social Conflict System (NEW)
- **Phase 10**: Character Sheet (unchanged)
- **Phases 11-12**: Status + Boons (enhanced)
- **Phase 13**: XP/Advancement (unchanged)
- **Phases 14-15**: Advanced Disciplines + Combat (unchanged)
- **Phase 16**: Humanity + Frenzy System (enhanced)
- **Phase 17**: Coterie/Prestation (unchanged)
- **Phase 18**: Thin-Bloods (unchanged)
- **Phase 18b**: Background Mechanical Effects (NEW)

**Total Phases**: 0-18b (effectively 20 phases)

---

## Updated Success Criteria

### Minimum Viable Product (MVP)
**Phases 0-10** complete = playable V5 MUSH with:
- ✅ MUSH infrastructure (BBS, Jobs, Help, News)
- ✅ Character creation with approval workflow
- ✅ Dice rolling with Hunger mechanics
- ✅ Automated nightly blood expenditure
- ✅ Social conflict system
- ✅ Basic disciplines
- ✅ Character sheets

### Full MUSH-Standard Launch  
**Phases 0-18b** complete adds:
- ✅ Political systems (Status with mechanical effects, Boons)
- ✅ Character advancement (XP)
- ✅ Advanced disciplines
- ✅ Humanity + Frenzy system
- ✅ Background mechanical effects
- ✅ Complete V:tM MUSH experience

---

**Document Version**: 2.1 (Final - All MUSH Essentials)
**Last Updated**: 2025-10-19
**Addendum Added**: To address missing MUSH standard features

**Changes in v2.1**:
- Added Phase 1b (News System)
- Enhanced Phase 0 (Evennia command verification)
- Enhanced Phase 6 (Automated blood/hunger with tickers)
- Added Phase 9 enhancement (Social Conflict System)
- Enhanced Phase 11 (Status mechanical effects)
- Enhanced Phase 16 (Frenzy system)
- Added Phase 18b (Background mechanical effects)
- Updated success criteria to reflect complete MUSH standard

**All 17 MUSH Essential Systems Now Covered**: ✅



---

## APPENDIX A: V:tM Theming & Aesthetics

**See THEMING_GUIDE.md for complete theming standards**

All phases that create user-facing output MUST follow the theming guidelines:

### Required Theming Deliverables by Phase:

**Phase 0**: 
- [ ] Create `beckonmu/world/ansi_theme.py` with color constants
- [ ] Create `beckonmu/server/conf/connection_screens.py` with ASCII logo

**Phase 1**: 
- [ ] Theme help files with gothic borders

**Phase 2**: 
- [ ] Theme BBS with `⚜` symbols and professional box-drawing borders

**Phase 5**: 
- [ ] Dice roll output with dramatic Messy Critical/Bestial Failure banners
- [ ] Color-coded dice results (normal vs Hunger dice)

**Phase 6**: 
- [ ] Hunger bar visualization with color gradient (white→gold→red)

**Phase 7**: 
- [ ] Clan sigils (ASCII art) for each of the 13 clans

**Phase 9**: 
- [ ] Chargen screens with themed borders and clan symbols

**Phase 10**: 
- [ ] Full character sheet with gothic header and organized sections
- [ ] Hunger bar, Status, and Boons display integration

**Phase 11**: 
- [ ] Status hierarchy display with `♛` symbols

**Phase 12**: 
- [ ] Boons tracker with favor/debt visualization

### Core Theming Principles:

- **Gothic Color Palette**: Dark reds, greys, purples, midnight blues
- **ANSI Safety**: Test on multiple clients, provide color-off option
- **Professional Borders**: Use box-drawing characters (`═ ║ ╔ ╗ ╚ ╝`)
- **Thematic Symbols**: `⚜ ♛ ⚠ ● ◆` for visual interest
- **Accessibility**: Always provide `+config color off` option

---

**Document Version**: 2.2 (Final with Theming Reference)
**See Also**: THEMING_GUIDE.md (complete aesthetics specification)

