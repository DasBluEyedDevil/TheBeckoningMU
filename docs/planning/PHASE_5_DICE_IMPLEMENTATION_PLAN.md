# Phase 5: Dice Rolling Engine - Implementation Plan

**Date**: 2025-10-26
**Quadrumvirate Pattern**: Gemini (Analysis) → Claude (Orchestration) → Cursor/Copilot (Implementation)

---

## Analysis Complete ✅

### Gemini Agent 1: Evennia Dice Contrib Analysis
- **Location**: `.venv/Lib/site-packages/evennia/contrib/rpg/dice/`
- **Key Findings**:
  - ✅ Core `roll()` function with flexible input parsing
  - ✅ Safe evaluation with `simple_eval()`
  - ✅ MuxCommand structure with `/secret`, `/hidden` switches
  - ✅ Room messaging patterns
  - ✅ Return tuple pattern for detailed results
  - ❌ NO success counting (uses sum, not 6+ threshold)
  - ❌ NO hunger dice mechanics
  - ❌ NO critical detection (pairs of 10s)

### Gemini Agent 2: V5 Mechanics Specification
- **Source**: `docs/reference/V5_MECHANICS.md`
- **Extracted**:
  - ✅ Complete dice mechanics (6+ = success, 10 = 2 successes, pairs of 10s = critical)
  - ✅ Hunger dice system (Bestial Failure, Messy Critical)
  - ✅ Rouse check mechanics (1d10, 6+ success)
  - ✅ All 103 discipline powers with dice pools
  - ✅ Contested rolls, willpower re-rolls, Blood Potency bonuses
  - ✅ Edge cases (zero pool, max Hunger, frenzy)

---

## Implementation Architecture

### File Structure

```
beckonmu/dice/
├── __init__.py
├── apps.py
├── models.py                  # RollHistory for logging
├── dice_roller.py            # Core V5 dice engine
├── roll_result.py            # Result parsing and interpretation
├── discipline_roller.py      # Discipline-specific rolls
├── rouse_checker.py          # Rouse check logic
├── commands.py               # Dice commands
├── cmdset.py                 # DiceCmdSet
└── tests.py                  # Comprehensive tests
```

### Dependencies

```python
# Leverage Evennia
from evennia.contrib.rpg.dice import roll as evennia_roll  # For basic rolling
from evennia.utils.utils import simple_eval  # For safe math
from evennia.commands.default.muxcommand import MuxCommand

# Integrate with traits
from traits.models import Trait, DisciplinePower, CharacterTrait
from traits.utils import get_character_trait_value
```

---

## Implementation Tasks

### Task 1: Core Dice Roller (`dice_roller.py`)

**Functions to Implement**:

```python
def roll_v5_pool(pool_size, hunger=0, difficulty=0):
    """
    Roll a V5 dice pool with Hunger dice.

    Args:
        pool_size (int): Total number of dice (1-20)
        hunger (int): Current Hunger level (0-5)
        difficulty (int): Number of successes needed (0+)

    Returns:
        RollResult: Comprehensive result object
    """
    # 1. Validate inputs (pool_size >= 1, 0 <= hunger <= 5, hunger <= pool_size)
    # 2. Split dice into regular and hunger
    # 3. Roll using random.randint(1, 10)
    # 4. Create RollResult object
    # 5. Return result

def roll_rouse_check():
    """
    Roll a single d10 for Rouse check.

    Returns:
        dict: {
            'roll': int (1-10),
            'success': bool (6+),
            'hunger_change': int (0 or +1)
        }
    """
    # 1. Roll 1d10
    # 2. Check if >= 6
    # 3. Return result

def roll_contested(pool1, hunger1, pool2, hunger2):
    """
    Roll two pools against each other.

    Returns:
        dict: {
            'roller1_result': RollResult,
            'roller2_result': RollResult,
            'winner': 1 or 2 or None (tie),
            'margin': int
        }
    """
    # 1. Roll both pools
    # 2. Compare successes
    # 3. Calculate margin
    # 4. Return winner

def apply_willpower_reroll(result, num_rerolls=3):
    """
    Reroll up to 3 failed regular dice (not Hunger dice).

    Args:
        result (RollResult): Original roll result
        num_rerolls (int): Number of dice to reroll (1-3)

    Returns:
        RollResult: New result with rerolled dice
    """
    # 1. Identify failed regular dice (< 6)
    # 2. Reroll up to num_rerolls of them
    # 3. Create new RollResult
    # 4. Track which dice were rerolled
    # 5. Return new result
```

**Special Cases**:
- **Zero Pool**: Roll 1 die (chance die), only 10 succeeds
- **Hunger 5**: All dice are Hunger dice
- **Hunger 0**: No Hunger dice, cannot have Bestial/Messy results

---

### Task 2: Roll Result Parser (`roll_result.py`)

**Class to Implement**:

```python
class RollResult:
    """
    Comprehensive V5 roll result with all analysis.
    """

    def __init__(self, regular_dice, hunger_dice, difficulty=0):
        """
        Args:
            regular_dice (list[int]): Regular dice results (1-10)
            hunger_dice (list[int]): Hunger dice results (1-10)
            difficulty (int): Target successes
        """
        self.regular_dice = regular_dice
        self.hunger_dice = hunger_dice
        self.all_dice = regular_dice + hunger_dice
        self.difficulty = difficulty

        # Core calculations
        self.total_successes = self._count_successes()
        self.is_success = self.total_successes >= difficulty
        self.margin = self.total_successes - difficulty

        # Special results
        self.is_critical = self._check_critical()
        self.is_messy_critical = self._check_messy_critical()
        self.is_bestial_failure = self._check_bestial_failure()

        # Result interpretation
        self.result_type = self._interpret_result()

    def _count_successes(self):
        """Count total successes: 6-9 = 1, 10 = 2."""
        successes = 0
        for die in self.all_dice:
            if die >= 6:
                successes += 2 if die == 10 else 1
        return successes

    def _check_critical(self):
        """Check for pair of 10s (critical win)."""
        tens = sum(1 for die in self.all_dice if die == 10)
        return tens >= 2

    def _check_messy_critical(self):
        """Check if critical includes Hunger die."""
        if not self.is_critical:
            return False
        hunger_tens = sum(1 for die in self.hunger_dice if die == 10)
        return hunger_tens >= 1

    def _check_bestial_failure(self):
        """Check if only Hunger dice show 1s on failed roll."""
        if self.is_success or not self.hunger_dice:
            return False

        # Check if total successes == 0
        if self.total_successes > 0:
            return False

        # Check if only Hunger dice have 1s
        hunger_ones = sum(1 for die in self.hunger_dice if die == 1)
        regular_ones = sum(1 for die in self.regular_dice if die == 1)

        return hunger_ones > 0 and regular_ones == 0

    def _interpret_result(self):
        """Interpret overall result type."""
        if not self.is_success:
            return 'bestial_failure' if self.is_bestial_failure else 'failure'
        elif self.is_messy_critical:
            return 'messy_critical'
        elif self.is_critical:
            return 'critical_success'
        else:
            return 'success'

    def format_result(self, show_details=True):
        """Format result for display."""
        # TODO: Implement rich text formatting
        pass
```

---

### Task 3: Discipline Roller (`discipline_roller.py`)

**Functions to Implement**:

```python
def roll_discipline_power(character, power_name, difficulty=0, with_rouse=True):
    """
    Roll a discipline power for a character.

    Args:
        character: Character object
        power_name (str): Name of discipline power
        difficulty (int): Target successes
        with_rouse (bool): Perform Rouse check if required

    Returns:
        dict: {
            'power': DisciplinePower,
            'rouse_result': dict or None,
            'roll_result': RollResult,
            'hunger_after': int
        }
    """
    # 1. Get discipline power from database
    # 2. Parse dice pool string (e.g., "Strength + Brawl")
    # 3. Get character's trait values
    # 4. Calculate total pool (including Blood Potency bonus)
    # 5. Perform Rouse check if required
    # 6. Roll dice pool with character's Hunger
    # 7. Return comprehensive result

def parse_dice_pool(pool_string):
    """
    Parse dice pool string into trait names.

    Args:
        pool_string (str): e.g., "Charisma + Animal Ken" or "Strength + Brawl"

    Returns:
        list[str]: Trait names, e.g., ['Charisma', 'Animal Ken']
    """
    # 1. Split on ' + ' or '/'
    # 2. Clean whitespace
    # 3. Return list of trait names

def calculate_pool_from_traits(character, trait_names):
    """
    Calculate total dice pool from trait values.

    Args:
        character: Character object
        trait_names (list[str]): Trait names

    Returns:
        int: Total pool size
    """
    # 1. Get trait values from character
    # 2. Sum them
    # 3. Add Blood Potency bonus if applicable
    # 4. Return total

def get_blood_potency_bonus(character, discipline_name):
    """
    Get Blood Potency bonus dice for discipline.

    Args:
        character: Character object
        discipline_name (str): Discipline name

    Returns:
        int: Bonus dice (0-5)
    """
    # Blood Potency 2-3: +1
    # Blood Potency 4-5: +2
    # Blood Potency 6-7: +3
    # Blood Potency 8-9: +4
    # Blood Potency 10: +5
```

---

### Task 4: Rouse Checker (`rouse_checker.py`)

**Functions to Implement**:

```python
def perform_rouse_check(character, reason='', power_level=1):
    """
    Perform a Rouse check and update character Hunger.

    Args:
        character: Character object
        reason (str): Why the Rouse check is happening
        power_level (int): Level of power being used (for Blood Potency reroll)

    Returns:
        dict: {
            'roll': int,
            'success': bool,
            'hunger_before': int,
            'hunger_after': int,
            'reroll_used': bool,
            'reason': str
        }
    """
    # 1. Get current Hunger
    # 2. Roll 1d10
    # 3. Check Blood Potency reroll eligibility
    # 4. If eligible and failed, offer reroll
    # 5. Update Hunger if failed
    # 6. Save character
    # 7. Return result

def can_reroll_rouse(character, power_level):
    """
    Check if character can reroll failed Rouse check.

    Based on Blood Potency and power level.
    """
    # Blood Potency 1-2: Level 1 powers
    # Blood Potency 3: Level 1-2 powers
    # Blood Potency 4-5: Level 1-2 powers
    # Blood Potency 6-7: Level 1-3 powers
    # Blood Potency 8-9: Level 1-4 powers
    # Blood Potency 10: Level 1-5 powers
```

---

### Task 5: Dice Commands (`commands.py`)

**Commands to Implement**:

```python
class CmdRoll(MuxCommand):
    """
    Roll dice using V5 mechanics.

    Usage:
        roll <pool> [<difficulty>]
        roll <pool> hunger <hunger> [<difficulty>]
        roll/willpower <pool> [<difficulty>]
        roll/secret <pool> [<difficulty>]
        roll/hidden <pool> [<difficulty>]

    Examples:
        roll 5              # Roll 5 dice vs difficulty 0
        roll 5 3            # Roll 5 dice vs difficulty 3
        roll 7 hunger 2     # Roll 7 dice (2 Hunger) vs difficulty 0
        roll 7 hunger 2 3   # Roll 7 dice (2 Hunger) vs difficulty 3
        roll/willpower 5 3  # Roll with willpower reroll option
        roll/secret 5       # Private roll
    """
    key = "roll"
    aliases = ["dice"]
    locks = "cmd:all()"
    help_category = "Dice"

    def func(self):
        # 1. Parse arguments (pool, hunger, difficulty)
        # 2. Get character's current Hunger if not specified
        # 3. Perform roll
        # 4. Handle willpower reroll if requested
        # 5. Format and display result
        # 6. Handle secret/hidden switches
        pass

class CmdRollPower(MuxCommand):
    """
    Roll a discipline power automatically.

    Usage:
        power <power name> [<difficulty>]
        power/willpower <power name> [<difficulty>]
        power/norouse <power name> [<difficulty>]

    Examples:
        power Corrosive Vitae           # Roll power with Rouse check
        power Corrosive Vitae 3         # Roll power vs difficulty 3
        power/willpower Awe             # Roll with willpower reroll option
        power/norouse Heightened Senses # Roll without Rouse (for free powers)
    """
    key = "power"
    aliases = ["discipline", "disc"]
    locks = "cmd:all()"
    help_category = "Disciplines"

    def func(self):
        # 1. Find discipline power by name
        # 2. Check if character knows the power
        # 3. Perform Rouse check if required
        # 4. Roll discipline dice pool
        # 5. Format and display result
        # 6. Update character state (Hunger, etc.)
        pass

class CmdRouse(MuxCommand):
    """
    Perform a Rouse check.

    Usage:
        rouse [<reason>]

    Examples:
        rouse                    # Basic Rouse check
        rouse Blood Surge        # Rouse for Blood Surge
    """
    key = "rouse"
    locks = "cmd:all()"
    help_category = "Dice"

    def func(self):
        # 1. Perform Rouse check
        # 2. Update Hunger
        # 3. Display result
        pass

class CmdShowDice(MuxCommand):
    """
    Show dice statistics and mechanics help.

    Usage:
        showdice
        showdice hunger
        showdice criticals
    """
    key = "showdice"
    aliases = ["dicestats"]
    locks = "cmd:all()"
    help_category = "Dice"

    def func(self):
        # Display V5 dice mechanics reference
        pass
```

---

### Task 6: Models (`models.py`)

**Optional: Roll History Logging**:

```python
from django.db import models
from evennia.typeclasses.models import TypedObject

class RollHistory(models.Model):
    """
    Log of dice rolls for review and debugging.
    """
    character = models.ForeignKey(
        TypedObject,
        on_delete=models.CASCADE,
        related_name='roll_history'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    roll_type = models.CharField(max_length=50)  # 'basic', 'discipline', 'rouse', 'contested'
    pool_size = models.IntegerField()
    hunger = models.IntegerField()
    difficulty = models.IntegerField()
    regular_dice = models.JSONField()  # List of ints
    hunger_dice = models.JSONField()   # List of ints
    total_successes = models.IntegerField()
    result_type = models.CharField(max_length=50)  # 'success', 'failure', 'critical', etc.

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Roll histories'

    def __str__(self):
        return f"{self.character.key} - {self.roll_type} - {self.timestamp}"
```

---

### Task 7: Tests (`tests.py`)

**Test Coverage Required**:

```python
from evennia.utils.test_resources import EvenniaTest
from dice.dice_roller import roll_v5_pool, roll_rouse_check
from dice.roll_result import RollResult

class DiceRollerTestCase(EvenniaTest):
    """Test core dice rolling mechanics."""

    def test_basic_roll(self):
        """Test basic dice pool rolling."""
        pass

    def test_success_counting(self):
        """Test that 6-9 = 1 success, 10 = 2 successes."""
        pass

    def test_hunger_dice_substitution(self):
        """Test that Hunger dice replace regular dice."""
        pass

    def test_critical_detection(self):
        """Test pair of 10s creates critical."""
        pass

    def test_messy_critical(self):
        """Test Hunger 10 in critical = messy."""
        pass

    def test_bestial_failure(self):
        """Test only Hunger 1s on failure = bestial."""
        pass

    def test_rouse_check(self):
        """Test 1d10 Rouse mechanics."""
        pass

    def test_willpower_reroll(self):
        """Test rerolling up to 3 dice."""
        pass

    def test_zero_pool(self):
        """Test chance die (1 die, only 10 succeeds)."""
        pass

    def test_hunger_five(self):
        """Test all Hunger dice at Hunger 5."""
        pass
```

---

## Integration with Traits System

### Character Methods Needed

Add to `beckonmu/typeclasses/characters.py`:

```python
@property
def hunger(self):
    """Get current Hunger level (0-5)."""
    return self.db.hunger or 1

@hunger.setter
def hunger(self, value):
    """Set Hunger level (clamped 0-5)."""
    self.db.hunger = max(0, min(5, value))

@property
def willpower_current(self):
    """Get current Willpower points."""
    return self.db.willpower_current or self.willpower_max

@willpower_current.setter
def willpower_current(self, value):
    """Set current Willpower (clamped 0-max)."""
    self.db.willpower_current = max(0, min(self.willpower_max, value))

@property
def willpower_max(self):
    """Calculate max Willpower (Composure + Resolve)."""
    composure = get_character_trait_value(self, 'Composure')
    resolve = get_character_trait_value(self, 'Resolve')
    return composure + resolve

def get_discipline_pool(self, power_name):
    """Get dice pool for discipline power."""
    from dice.discipline_roller import roll_discipline_power
    # Implementation
    pass
```

---

## Display Formatting

### Output Examples

**Basic Roll**:
```
> roll 5 hunger 2 3

You roll 5 dice (Hunger 2) vs difficulty 3...
Regular: [8, 7, 3]
Hunger: [10, 6]

Successes: 5 (6, 7, 8, 10x2, 6 from Hunger die)
Result: MESSY CRITICAL
You succeed dramatically with 5 successes (margin +2),
but your Beast shows through. The Storyteller will
introduce a complication related to your vampiric nature.
```

**Discipline Power**:
```
> power Corrosive Vitae 2

Activating Corrosive Vitae (Blood Sorcery Level 1)...
Rouse Check: [8] - Success! Hunger remains at 1

Rolling Strength + Blood Sorcery (5 dice, Hunger 1)...
Regular: [9, 7, 6, 4]
Hunger: [3]

Successes: 3 (margin +1)
Result: SUCCESS
Your vitae burns like acid as you spit it at your target!
```

**Rouse Check**:
```
> rouse

Rouse Check: [4] - Failed
Your Hunger increases from 2 to 3.
You feel the Beast stirring...
```

---

## Implementation Order

1. **Core Roller** (`dice_roller.py`) - Foundation
2. **Result Parser** (`roll_result.py`) - Analysis
3. **Rouse Checker** (`rouse_checker.py`) - Simple mechanic
4. **Discipline Roller** (`discipline_roller.py`) - Complex integration
5. **Commands** (`commands.py`) - User interface
6. **Tests** (`tests.py`) - Verification
7. **Character Integration** - Add properties to Character typeclass
8. **Command Set** - Add DiceCmdSet to CharacterCmdSet

---

## Success Criteria

✅ Users can roll basic dice pools with Hunger: `roll 5 hunger 2 3`
✅ Users can roll discipline powers by name: `power Corrosive Vitae`
✅ System auto-calculates dice pools from traits
✅ Rouse checks work correctly (1d10, 6+, Hunger increase)
✅ Critical detection works (pair of 10s = 4 successes)
✅ Messy Critical detected (Hunger die in critical)
✅ Bestial Failure detected (only Hunger 1s on fail)
✅ Willpower rerolls work (up to 3 dice)
✅ Blood Potency bonuses apply
✅ Secret/hidden rolls work
✅ Results displayed beautifully with ANSI colors
✅ All 103 discipline powers work correctly
✅ State changes persist (Hunger, Willpower)
✅ Comprehensive test coverage (>90%)

---

## Token Efficiency Strategy

**Claude (Orchestrator)**:
- ✅ Created this plan (~5k tokens)
- Will review implementation for correctness
- Will update documentation

**Cursor/Copilot (Implementers)**:
- Will write all 7 Python files (~2000 lines total)
- Will write comprehensive tests
- Will integrate with existing systems

**Expected Token Savings**: ~150k Claude tokens saved by delegating implementation to Cursor/Copilot

---

## Next Steps

1. **Claude**: Review this plan with user for approval
2. **Cursor/Copilot**: Implement files in order listed above
3. **Claude**: Review implementation, run tests, verify integration
4. **Update**: CHANGELOG.md, SESSION_NOTES.md, docs/planning/ROADMAP.md

Ready to delegate to Cursor/Copilot for implementation! 🎲
