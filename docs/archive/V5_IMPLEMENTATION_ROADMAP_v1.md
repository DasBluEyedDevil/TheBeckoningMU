# V5 Implementation Roadmap for TheBeckoningMU

**Version**: 1.0
**Created**: 2025-10-19
**Purpose**: Dependency-ordered implementation plan for V5 mechanics in Evennia

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

**REPLICATE** (from successful BBS refactor):
- ✅ Small, single-responsibility commands
- ✅ Shared utility modules
- ✅ Database-driven configuration
- ✅ Test-driven development
- ✅ Clear separation of concerns

### V5 Data Storage Architecture

All V5-specific data stored on `Character.db.*`:

```python
# On Character typeclass (beckonmu/typeclasses/characters.py)
char.db.stats = {
    "attributes": {
        "physical": {"strength": 2, "dexterity": 2, "stamina": 2},
        "social": {"charisma": 2, "manipulation": 2, "composure": 2},
        "mental": {"intelligence": 2, "wits": 2, "resolve": 2}
    },
    "skills": {
        "physical": {},
        "social": {},
        "mental": {}
    },
    "disciplines": {}  # name: {level: int, powers: []}
}

char.db.vampire = {
    "clan": "Brujah",
    "generation": 13,
    "blood_potency": 1,
    "hunger": 1,  # 0-5
    "humanity": 7,
    "predator_type": "Scene Queen"
}

char.db.pools = {
    "health": 5,  # Stamina + 3
    "willpower": 4,  # Composure + Resolve
    "current_health": 5,
    "current_willpower": 4
}
```

### Command Organization Pattern

Following refactored BBS pattern:

```
beckonmu/commands/v5/
├── __init__.py
├── chargen.py        # Small, focused chargen commands
├── dice.py           # Dice rolling commands
├── sheet.py          # Character sheet display
├── blood.py          # Blood/feeding commands
├── disciplines.py    # Discipline activation
└── utils/
    ├── __init__.py
    ├── dice_utils.py      # Dice rolling logic
    ├── chargen_utils.py   # Character creation helpers
    ├── trait_utils.py     # Trait validation/lookup
    └── display_utils.py   # Formatting/display helpers
```

### Trait System Architecture

**Database-Driven Configuration** (NOT hardcoded):

```python
# beckonmu/world/v5_data.py - Configuration only, editable without restart
V5_CLANS = {
    "Brujah": {
        "disciplines": ["Celerity", "Potence", "Presence"],
        "bane": "Rage simmers beneath surface",
        "compulsion": "Rebellion"
    },
    # ...
}

V5_ATTRIBUTES = ["strength", "dexterity", "stamina", ...]
V5_SKILLS = {
    "physical": ["athletics", "brawl", "craft", ...],
    # ...
}
```

### Dice Engine Architecture

```python
# beckonmu/world/v5_dice.py
class V5DiceRoller:
    """Handles all V5 dice mechanics"""

    def roll_pool(self, pool_size, hunger=0, difficulty=0):
        """
        Roll dice pool with Hunger dice.
        Returns: {
            'successes': int,
            'critical': bool,
            'messy_critical': bool,
            'bestial_failure': bool,
            'results': [(die_value, is_hunger), ...]
        }
        """
        pass

    def rouse_check(self, character):
        """Perform Rouse check, potentially increase Hunger"""
        pass
```

---

## Implementation Phases

### Phase 0: Project Setup & Architecture
**Goal**: Establish foundation before feature development
**Complexity**: Simple
**Dependencies**: None

**Deliverables**:
- [ ] Create `beckonmu/commands/v5/` directory structure
- [ ] Create `beckonmu/commands/v5/utils/` for shared logic
- [ ] Create `beckonmu/world/v5_data.py` (configuration)
- [ ] Create `beckonmu/world/v5_dice.py` (dice engine)
- [ ] Set up test directory: `beckonmu/tests/v5/`
- [ ] Document architectural decisions in `beckonmu/commands/v5/README.md`

**Testing**: Directory structure exists, imports work

---

### Phase 1: Trait System Foundation
**Goal**: Database-driven trait system for attributes and skills
**Complexity**: Medium
**Dependencies**: Phase 0

**Deliverables**:
- [ ] `beckonmu/commands/v5/utils/trait_utils.py`
  - `get_trait_value(character, trait_type, trait_name)`
  - `set_trait_value(character, trait_type, trait_name, value)`
  - `validate_trait(trait_type, trait_name, value)`
  - `get_trait_pool(character, attribute, skill)`
- [ ] `beckonmu/world/v5_data.py` - Define all attributes/skills
- [ ] Modify `beckonmu/typeclasses/characters.py`:
  - Add `at_object_creation()` to initialize `char.db.stats`
  - Add helper methods for trait access

**Files Modified**:
- `beckonmu/typeclasses/characters.py`

**Files Created**:
- `beckonmu/commands/v5/utils/trait_utils.py`
- `beckonmu/world/v5_data.py`
- `beckonmu/tests/v5/test_trait_utils.py`

**Testing Checkpoints**:
- Unit tests for all trait_utils functions
- Test invalid trait names/values
- Test trait pool calculation

---

### Phase 2: Dice Rolling Engine
**Goal**: Complete V5 dice mechanics (Hunger dice, Rouse checks)
**Complexity**: Complex
**Dependencies**: Phase 1 (needs trait system)

**Deliverables**:
- [ ] `beckonmu/world/v5_dice.py` - Complete `V5DiceRoller` class
  - Basic pool rolling (d10, successes on 6+, criticals on 10)
  - Hunger dice integration
  - Messy Critical detection
  - Bestial Failure detection
  - Rouse check mechanic
- [ ] `beckonmu/commands/v5/dice.py` - Dice commands
  - `CmdRoll` - Generic dice roll
  - `CmdRollStat` - Roll attribute + skill
  - `CmdRouseCheck` - Manual Rouse check (testing/admin)

**Files Created**:
- `beckonmu/world/v5_dice.py`
- `beckonmu/commands/v5/dice.py`
- `beckonmu/tests/v5/test_dice.py`

**Testing Checkpoints**:
- Test basic d10 rolling (100+ rolls, verify distribution)
- Test Hunger dice marking
- Test Messy Critical (Hunger dice in critical)
- Test Bestial Failure (only Hunger dice show 1s on failure)
- Test Rouse check (50% success rate over 1000 trials)

---

### Phase 3: Blood Systems (Hunger, Blood Potency, Feeding)
**Goal**: Core vampire resource management
**Complexity**: Medium
**Dependencies**: Phase 2 (needs Rouse checks)

**Deliverables**:
- [ ] Modify `beckonmu/typeclasses/characters.py`:
  - Add `char.db.vampire` structure
  - Add Hunger manipulation methods
  - Add Blood Potency calculations
- [ ] `beckonmu/commands/v5/blood.py`:
  - `CmdFeed` - Feeding mechanics
  - `CmdHunger` - Check/set Hunger (admin)
  - `CmdBloodSurge` - Spend blood for bonuses
- [ ] `beckonmu/commands/v5/utils/blood_utils.py`:
  - `increase_hunger(character, amount=1)`
  - `decrease_hunger(character, amount, source="mortal")`
  - `get_blood_potency_benefits(character)`
  - `calculate_feeding_penalty(character)`

**Files Modified**:
- `beckonmu/typeclasses/characters.py`

**Files Created**:
- `beckonmu/commands/v5/blood.py`
- `beckonmu/commands/v5/utils/blood_utils.py`
- `beckonmu/tests/v5/test_blood.py`

**Testing Checkpoints**:
- Test Hunger clamping (0-5)
- Test Blood Potency feeding penalties
- Test feeding reducing Hunger correctly
- Test Rouse check integration

---

### Phase 4: Clan System
**Goal**: Clan selection, banes, compulsions
**Complexity**: Medium
**Dependencies**: Phase 3 (clans affect blood mechanics)

**Deliverables**:
- [ ] Expand `beckonmu/world/v5_data.py` - All 13+ clans
- [ ] `beckonmu/commands/v5/utils/clan_utils.py`:
  - `get_clan_info(clan_name)`
  - `validate_clan_disciplines(character, discipline)`
  - `apply_clan_bane(character, context)`
  - `trigger_compulsion(character)`
- [ ] Modify `beckonmu/typeclasses/characters.py`:
  - Clan-based discipline validation

**Files Modified**:
- `beckonmu/world/v5_data.py`
- `beckonmu/typeclasses/characters.py`

**Files Created**:
- `beckonmu/commands/v5/utils/clan_utils.py`
- `beckonmu/tests/v5/test_clan.py`

**Testing Checkpoints**:
- Test all clan data loads correctly
- Test in-clan vs out-of-clan discipline costs
- Test clan bane mechanics (per clan)

---

### Phase 5: Discipline Framework
**Goal**: Discipline powers, activation, costs
**Complexity**: Complex
**Dependencies**: Phase 4 (clan determines discipline access)

**Deliverables**:
- [ ] `beckonmu/world/v5_data.py` - All discipline powers (levels 1-5)
- [ ] `beckonmu/commands/v5/disciplines.py`:
  - `CmdActivatePower` - Use discipline power
  - `CmdListDisciplines` - Show available powers
- [ ] `beckonmu/commands/v5/utils/discipline_utils.py`:
  - `get_available_powers(character, discipline)`
  - `activate_power(character, power_name, target=None)`
  - `check_power_prerequisites(character, power_name)`
  - `apply_power_effect(power, character, target=None)`

**Files Modified**:
- `beckonmu/world/v5_data.py`

**Files Created**:
- `beckonmu/commands/v5/disciplines.py`
- `beckonmu/commands/v5/utils/discipline_utils.py`
- `beckonmu/tests/v5/test_disciplines.py`

**Testing Checkpoints**:
- Test power activation triggers Rouse check
- Test amalgam prerequisite checking
- Test power effects (start with passive powers)
- Test in-clan vs out-of-clan costs

**Note**: Start with simple/passive powers first (Celerity passive, Fortitude Resilience), defer complex powers (Dominate, Obfuscate) to Phase 9.

---

### Phase 6: Character Creation Flow
**Goal**: Integrated chargen using all V5 systems
**Complexity**: Complex
**Dependencies**: Phases 1-5 (needs all core systems)

**Deliverables**:
- [ ] `beckonmu/commands/v5/chargen.py`:
  - `CmdChargenStart` - Begin character creation
  - `CmdChargenClan` - Select clan
  - `CmdChargenAttributes` - Allocate attributes (7/5/3)
  - `CmdChargenSkills` - Allocate skills (13/9/5)
  - `CmdChargenDisciplines` - Choose disciplines (2 in-clan, 1 any)
  - `CmdChargenPredator` - Select predator type (Phase 8)
  - `CmdChargenAdvantages` - Spend 7 advantage dots
  - `CmdChargenFinalize` - Complete and verify character
- [ ] `beckonmu/commands/v5/utils/chargen_utils.py`:
  - `validate_attribute_allocation(attributes_dict)`
  - `validate_skill_allocation(skills_dict)`
  - `calculate_derived_stats(character)`
  - `apply_predator_type(character, predator)`

**Files Created**:
- `beckonmu/commands/v5/chargen.py`
- `beckonmu/commands/v5/utils/chargen_utils.py`
- `beckonmu/tests/v5/test_chargen.py`

**Testing Checkpoints**:
- Test 7/5/3 attribute validation
- Test 13/9/5 skill validation
- Test discipline point allocation
- Test derived stat calculation (Health, Willpower)
- End-to-end chargen test creating valid character

---

### Phase 7: Character Sheet Display
**Goal**: Comprehensive character sheet viewing
**Complexity**: Simple
**Dependencies**: Phase 6 (needs complete character data)

**Deliverables**:
- [ ] `beckonmu/commands/v5/sheet.py`:
  - `CmdSheet` - Display full character sheet
  - `CmdSheetShort` - Abbreviated vital stats
- [ ] `beckonmu/commands/v5/utils/display_utils.py`:
  - `format_character_sheet(character)`
  - `format_trait_block(traits_dict, title)`
  - `format_disciplines(character)`
  - `format_blood_status(character)`

**Files Created**:
- `beckonmu/commands/v5/sheet.py`
- `beckonmu/commands/v5/utils/display_utils.py`
- `beckonmu/tests/v5/test_sheet.py`

**Testing Checkpoints**:
- Test sheet displays all stats correctly
- Test formatting is readable
- Test sheet shows Hunger, Blood Potency
- Test discipline powers listed

---

### Phase 8: Predator Types
**Goal**: Predator type selection and effects
**Complexity**: Medium
**Dependencies**: Phase 6 (integrates with chargen)

**Deliverables**:
- [ ] Expand `beckonmu/world/v5_data.py` - All predator types
- [ ] Integrate with `CmdChargenPredator` (from Phase 6)
- [ ] `beckonmu/commands/v5/utils/predator_utils.py`:
  - `get_predator_info(predator_name)`
  - `apply_predator_bonuses(character, predator)`
  - `apply_predator_flaws(character, predator)`

**Files Modified**:
- `beckonmu/world/v5_data.py`
- `beckonmu/commands/v5/chargen.py` (add predator selection)

**Files Created**:
- `beckonmu/commands/v5/utils/predator_utils.py`
- `beckonmu/tests/v5/test_predator.py`

**Testing Checkpoints**:
- Test predator type grants correct bonuses
- Test predator flaws applied
- Test starting Humanity variations

---

### Phase 9: Advanced Disciplines (Amalgams, Rituals)
**Goal**: Complex discipline powers
**Complexity**: Complex
**Dependencies**: Phase 5 (basic disciplines)

**Deliverables**:
- [ ] Implement complex discipline effects:
  - Dominate (mind control mechanics)
  - Obfuscate (invisibility, detection checks)
  - Blood Sorcery rituals
  - Oblivion paths
- [ ] `beckonmu/commands/v5/utils/discipline_effects.py`:
  - Effect handlers for each complex power
  - Duration tracking for ongoing effects
  - Contested roll mechanics

**Files Created**:
- `beckonmu/commands/v5/utils/discipline_effects.py`
- `beckonmu/tests/v5/test_advanced_disciplines.py`

**Testing Checkpoints**:
- Test amalgam prerequisite checking
- Test ritual mechanics
- Test ongoing effect duration
- Test contested discipline rolls

---

### Phase 10: Combat & Conflict Resolution
**Goal**: V5 combat mechanics (optional for MUSH)
**Complexity**: Complex
**Dependencies**: Phase 9 (needs all disciplines)

**Deliverables**:
- [ ] `beckonmu/commands/v5/combat.py`:
  - `CmdAttack` - Melee/ranged attacks
  - `CmdDefend` - Dodge/defense
  - `CmdDamage` - Apply damage
  - `CmdHeal` - Mend damage with vitae
- [ ] `beckonmu/commands/v5/utils/combat_utils.py`:
  - Attack resolution
  - Damage calculation (Superficial vs Aggravated)
  - Health tracking
  - Impairment/Torpor checks

**Files Created**:
- `beckonmu/commands/v5/combat.py`
- `beckonmu/commands/v5/utils/combat_utils.py`
- `beckonmu/tests/v5/test_combat.py`

**Testing Checkpoints**:
- Test attack resolution
- Test damage types
- Test torpor threshold
- Test healing mechanics

**Note**: This phase may be deferred or simplified depending on MUSH playstyle (narrative vs mechanical combat).

---

### Phase 11: Humanity & Touchstones
**Goal**: Humanity system, Stains, Touchstones
**Complexity**: Medium
**Dependencies**: Phase 3 (humanity affects frenzy)

**Deliverables**:
- [ ] `beckonmu/commands/v5/humanity.py`:
  - `CmdConvictions` - Set convictions
  - `CmdTouchstones` - Manage touchstones
  - `CmdRemorse` - Remorse roll mechanics
- [ ] `beckonmu/commands/v5/utils/humanity_utils.py`:
  - `apply_stain(character, severity)`
  - `remorse_check(character)`
  - `lose_humanity(character, amount=1)`
  - `check_touchstone(character, touchstone_id)`

**Files Modified**:
- `beckonmu/typeclasses/characters.py` (add Convictions, Touchstones, Stains)

**Files Created**:
- `beckonmu/commands/v5/humanity.py`
- `beckonmu/commands/v5/utils/humanity_utils.py`
- `beckonmu/tests/v5/test_humanity.py`

**Testing Checkpoints**:
- Test Stain accumulation
- Test Remorse rolls
- Test Humanity loss
- Test Touchstone mechanics

---

### Phase 12: Social Systems (Status, Boons, Prestation)
**Goal**: Vampire political/social mechanics
**Complexity**: Medium
**Dependencies**: Phase 11 (complete character systems)

**Deliverables**:
- [ ] `beckonmu/commands/v5/social.py`:
  - `CmdStatus` - Manage Status backgrounds
  - `CmdBoon` - Track boons owed/held
  - `CmdCoterie` - Coterie management
- [ ] `beckonmu/commands/v5/utils/social_utils.py`:
  - Boon tracking
  - Status calculation
  - Influence mechanics

**Files Created**:
- `beckonmu/commands/v5/social.py`
- `beckonmu/commands/v5/utils/social_utils.py`
- `beckonmu/tests/v5/test_social.py`

**Testing Checkpoints**:
- Test boon creation/resolution
- Test Status effects
- Test Coterie mechanics

**Note**: This phase is highly MUSH-specific and may need significant customization based on game theme/setting.

---

## File Organization

### Complete Directory Structure

```
beckonmu/
├── commands/
│   └── v5/
│       ├── __init__.py
│       ├── README.md              # Architectural docs
│       ├── chargen.py             # Phase 6
│       ├── dice.py                # Phase 2
│       ├── sheet.py               # Phase 7
│       ├── blood.py               # Phase 3
│       ├── disciplines.py         # Phase 5, 9
│       ├── combat.py              # Phase 10 (optional)
│       ├── humanity.py            # Phase 11
│       ├── social.py              # Phase 12
│       └── utils/
│           ├── __init__.py
│           ├── trait_utils.py     # Phase 1
│           ├── dice_utils.py      # Phase 2 (if needed)
│           ├── chargen_utils.py   # Phase 6
│           ├── blood_utils.py     # Phase 3
│           ├── clan_utils.py      # Phase 4
│           ├── discipline_utils.py # Phase 5
│           ├── discipline_effects.py # Phase 9
│           ├── predator_utils.py  # Phase 8
│           ├── display_utils.py   # Phase 7
│           ├── combat_utils.py    # Phase 10
│           ├── humanity_utils.py  # Phase 11
│           └── social_utils.py    # Phase 12
│
├── typeclasses/
│   └── characters.py              # Modified in Phases 1, 3, 4, 11
│
├── world/
│   ├── v5_data.py                 # Phases 1, 4, 5, 8 (configuration)
│   └── v5_dice.py                 # Phase 2 (dice engine)
│
└── tests/
    └── v5/
        ├── __init__.py
        ├── test_trait_utils.py    # Phase 1
        ├── test_dice.py           # Phase 2
        ├── test_blood.py          # Phase 3
        ├── test_clan.py           # Phase 4
        ├── test_disciplines.py    # Phase 5
        ├── test_chargen.py        # Phase 6
        ├── test_sheet.py          # Phase 7
        ├── test_predator.py       # Phase 8
        ├── test_advanced_disciplines.py # Phase 9
        ├── test_combat.py         # Phase 10
        ├── test_humanity.py       # Phase 11
        └── test_social.py         # Phase 12
```

---

## Data Models

### Character.db Structure

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
        },
        "Presence": {
            "level": 1,
            "powers": ["Awe"]
        }
    }
}

char.db.vampire = {
    "clan": "Brujah",
    "generation": 13,
    "blood_potency": 1,
    "hunger": 1,                # 0-5
    "humanity": 7,              # 0-10
    "predator_type": "Scene Queen",
    "sire": "Elder Brujah Name",
    "embrace_date": "2020-05-15",
    "bane": "Rage simmers beneath surface",
    "compulsion": "Rebellion"
}

char.db.pools = {
    "health": 5,                # Stamina + 3
    "willpower": 4,             # Composure + Resolve
    "current_health": 5,
    "current_willpower": 4,
    "superficial_damage": 0,
    "aggravated_damage": 0,
    "willpower_damage": 0
}

char.db.humanity_data = {
    "convictions": [
        "Art should speak truth to power",
        "Protect the scene from corporate sellouts"
    ],
    "touchstones": [
        {
            "name": "Best friend from mortal days",
            "conviction_index": 0,
            "relationship": "Still plays music together"
        }
    ],
    "stains": 0,                # Temporary moral failing
    "chronicle": "Anarch game"
}

char.db.advantages = {
    "backgrounds": {
        "Fame": 1,
        "Contacts": 2,
        "Resources": 1,
        "Haven": 1
    },
    "merits": {
        "Beautiful": 2
    },
    "flaws": {
        "Rival": 1               # Competing band's frontman
    }
}

char.db.experience = {
    "total_earned": 0,
    "total_spent": 0,
    "current": 0
}

# Ongoing effects (Phase 9+)
char.db.effects = [
    {
        "name": "Heightened Senses",
        "discipline": "Auspex",
        "duration": -1,          # -1 = permanent/manual toggle
        "effect_data": {...}
    }
]
```

---

## Testing Strategy

### Test-Driven Development Approach

Following lessons from reference repo:

1. **Write tests FIRST** before implementing features
2. **Run tests** to verify they fail (RED)
3. **Implement** minimal code to pass tests (GREEN)
4. **Refactor** while keeping tests green (REFACTOR)

### Unit Testing

Each utility module must have comprehensive unit tests:

```python
# Example: beckonmu/tests/v5/test_trait_utils.py
from evennia.utils.test_resources import BaseEvenniaTest
from commands.v5.utils.trait_utils import get_trait_value, set_trait_value

class TraitUtilsTestCase(BaseEvenniaTest):
    def setUp(self):
        super().setUp()
        self.char = self.char1  # Evennia test character

    def test_get_attribute_value(self):
        """Test retrieving attribute value"""
        value = get_trait_value(self.char, "attribute", "strength")
        self.assertEqual(value, 1)  # Default

    def test_set_attribute_value(self):
        """Test setting attribute value"""
        set_trait_value(self.char, "attribute", "strength", 3)
        value = get_trait_value(self.char, "attribute", "strength")
        self.assertEqual(value, 3)

    def test_invalid_trait_name(self):
        """Test that invalid trait names raise error"""
        with self.assertRaises(ValueError):
            set_trait_value(self.char, "attribute", "INVALID", 3)
```

### Integration Testing

Test commands end-to-end:

```python
# Example: beckonmu/tests/v5/test_dice.py
class DiceCommandTestCase(BaseEvenniaCommandTest):
    def test_basic_roll(self):
        """Test basic dice roll command"""
        self.call(
            dice.CmdRoll(),
            "5",
            "You rolled 5 dice: [results]"
        )

    def test_hunger_roll(self):
        """Test roll with Hunger dice"""
        self.char.db.vampire = {"hunger": 2}
        self.call(
            dice.CmdRoll(),
            "5",
            "You rolled 5 dice (2 Hunger): [results]"
        )
```

### Testing Checklist Per Phase

Each phase must verify:
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Edge cases handled (invalid input, boundary values)
- [ ] Error messages are clear and helpful
- [ ] No bare exceptions
- [ ] Documentation strings on all public functions

---

## Risks & Mitigations

### Risk 1: Scope Creep (Repeating Reference Repo Mistake)

**Risk**: Attempting too many features at once without finishing core systems.

**Mitigation**:
- Strict phase ordering - NO skipping ahead
- Each phase has "Done" criteria
- Testing checkpoints MUST pass before next phase
- Focus on MVP (Minimum Viable Product) per phase

### Risk 2: Hardcoded Data (Reference Repo Anti-Pattern)

**Risk**: Slipping into hardcoded Python data instead of database-driven.

**Mitigation**:
- Configuration in `v5_data.py` is READ-ONLY data (like spell definitions)
- Character-specific data ALWAYS in `char.db.*`
- Code review: Flag any hardcoded game balance numbers
- Future: Migrate `v5_data.py` to database tables if needed

### Risk 3: Monolithic Commands (Reference Repo Anti-Pattern)

**Risk**: Commands growing too large with switch-based logic.

**Mitigation**:
- Follow BBS refactor pattern religiously
- Each command does ONE thing
- Shared logic goes in utils/
- Code review: Flag any command >100 lines
- Refactor immediately if command handles >3 switches

### Risk 4: Missing Test Coverage

**Risk**: Skipping tests to "move faster" leads to brittle code.

**Mitigation**:
- TDD is non-negotiable
- Each PR requires tests
- Track test coverage (aim for >80% per module)
- Automated test runs in CI/CD (if available)

### Risk 5: Discipline Complexity Explosion

**Risk**: Implementing all discipline powers is massive scope.

**Mitigation**:
- Phase 5: Only simple/passive powers (Celerity, Fortitude, Potence)
- Phase 9: Complex powers (Dominate, Obfuscate, Blood Sorcery)
- Phase 10+: Defer rarely-used powers
- Document "Not Yet Implemented" powers clearly
- Allow storyteller adjudication for unimplemented powers

### Risk 6: Data Migration Pain

**Risk**: Changing data models mid-development breaks existing characters.

**Mitigation**:
- Design data models COMPLETELY in Phase 0-1
- Write migration scripts if schema changes
- Version the data model (`char.db.v5_version = 1`)
- Provide upgrade path for old characters

### Risk 7: Evennia Version Compatibility

**Risk**: Evennia updates break our code.

**Mitigation**:
- Pin Evennia version in `pyproject.toml`
- Test upgrades in separate branch
- Follow Evennia deprecation warnings
- Subscribe to Evennia dev mailing list

### Risk 8: Reference Repo Code Reuse Temptation

**Risk**: Copying broken patterns from reference repo.

**Mitigation**:
- Reference repo is READ-ONLY for learning mistakes
- DO NOT copy-paste code from reference repo
- Use reference repo only for:
  - Understanding V5 mechanics implemented
  - Learning what NOT to do architecturally
  - Identifying edge cases/bugs to avoid

---

## Success Criteria

### Per-Phase Success

Each phase is "done" when:
- ✅ All deliverables created
- ✅ All tests pass (unit + integration)
- ✅ Code reviewed (if team development)
- ✅ Documentation updated
- ✅ No known bugs

### Overall Project Success

Project is "complete" when:
- ✅ Phases 0-7 fully implemented (core functionality)
- ✅ Character creation works end-to-end
- ✅ Dice rolling works with Hunger mechanics
- ✅ Character sheets display correctly
- ✅ All tests passing
- ✅ Zero critical bugs
- ✅ Playable V5 MUSH

Phases 8-12 can be deferred to post-launch iterations.

---

## Appendix: Phase Dependencies Graph

```
Phase 0: Setup
    ↓
Phase 1: Trait System ←─────┐
    ↓                       │
Phase 2: Dice Engine        │
    ↓                       │
Phase 3: Blood Systems      │
    ↓                       │
Phase 4: Clans              │
    ↓                       │
Phase 5: Basic Disciplines  │
    ↓                       │
Phase 6: Character Creation ┘ (depends on 1-5)
    ↓
Phase 7: Character Sheet
    ↓
Phase 8: Predator Types (can be done anytime after Phase 3)
    ↓
Phase 9: Advanced Disciplines (depends on Phase 5)
    ↓
Phase 10: Combat (optional, depends on Phase 9)
    ↓
Phase 11: Humanity (can be done anytime after Phase 3)
    ↓
Phase 12: Social Systems (depends on Phase 11)
```

---

## Conclusion

This roadmap provides the structured, dependency-ordered plan that the reference repository desperately needed. By following these phases strictly, avoiding the identified anti-patterns, and maintaining test-driven development, TheBeckoningMU will succeed where the reference implementation failed.

**Key Takeaway**: DISCIPLINE in following the plan is more important than SPEED in coding. Build it right, build it once.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-19
**Next Review**: After Phase 3 completion
