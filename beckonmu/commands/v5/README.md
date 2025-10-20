# V5 Commands Architecture

**Phase 0 Architectural Documentation**

This document outlines the architectural decisions and patterns for V5 command implementation in TheBeckoningMU.

---

## Core Principles

### 1. Small Single-Responsibility Commands

**DO THIS:**
```python
# beckonmu/commands/v5/dice_commands.py
class CmdRoll(Command):
    """Roll dice using V5 mechanics."""
    key = "roll"

    def func(self):
        # Single responsibility: parse and execute ONE dice roll
        pass

class CmdRouseCheck(Command):
    """Perform a Rouse check."""
    key = "rouse"

    def func(self):
        # Single responsibility: Rouse check only
        pass
```

**DON'T DO THIS:**
```python
# ANTI-PATTERN from reference repo
class CmdDice(Command):
    """Mega-command with 15+ switches."""
    key = "dice"

    def func(self):
        if self.switches == "roll": ...
        elif self.switches == "rouse": ...
        elif self.switches == "contested": ...
        # 500+ lines of unmaintainable switch logic
```

### 2. Shared Utility Modules

**Pattern:** Commands are thin wrappers around shared utility functions.

```python
# beckonmu/commands/v5/utils/dice_utils.py
def roll_pool(pool, hunger, difficulty):
    """Shared dice rolling logic used by multiple commands."""
    # Core logic here
    pass

# beckonmu/commands/v5/dice_commands.py
from .utils.dice_utils import roll_pool

class CmdRoll(Command):
    def func(self):
        # Parse arguments
        pool = self.parse_pool()
        # Delegate to shared utility
        result = roll_pool(pool, self.caller.db.hunger, difficulty)
        # Display result
        self.msg(format_result(result))
```

### 3. Database-Driven Configuration

**DO THIS:**
```python
# Data stored in database attributes
char.db.hunger = 3
char.db.blood_potency = 2
char.db.stats = {
    "attributes": {"Strength": 3, "Dexterity": 2, ...},
    "skills": {"Athletics": 2, "Brawl": 3, ...}
}

# Game logic queries the database
def get_attribute(char, attr_name):
    return char.db.stats["attributes"].get(attr_name, 1)
```

**DON'T DO THIS:**
```python
# ANTI-PATTERN: Hardcoded data in Python files
CLANS = {
    "Brujah": {"disciplines": ["Celerity", "Potence", "Presence"]}
}

# This makes it impossible to add clans without code changes!
```

**Clarification:** The `v5_data.py` file contains **template/structure definitions** that are loaded INTO the database during initial setup. It's not queried directly during gameplay.

### 4. Test-Driven Development (TDD)

**RED → GREEN → REFACTOR**

```python
# beckonmu/tests/v5/test_dice.py

# RED: Write test FIRST (it fails)
def test_roll_pool_basic():
    result = roll_pool(pool=5, hunger=0, difficulty=3)
    assert isinstance(result, DiceResult)
    assert len(result.normal_dice) == 5
    assert len(result.hunger_dice) == 0

# GREEN: Write minimal code to pass
def roll_pool(pool, hunger, difficulty):
    normal_dice = [random.randint(1,10) for _ in range(pool)]
    hunger_dice = []
    return DiceResult(normal_dice, hunger_dice, difficulty)

# REFACTOR: Improve while keeping tests green
def roll_pool(pool, hunger, difficulty):
    num_hunger_dice = min(hunger, pool)
    num_normal_dice = pool - num_hunger_dice
    normal_dice = [random.randint(1,10) for _ in range(num_normal_dice)]
    hunger_dice = [random.randint(1,10) for _ in range(num_hunger_dice)]
    return DiceResult(normal_dice, hunger_dice, difficulty)
```

---

## Data Storage Architecture

### Character Data Model

V5 character data is stored in `character.db.*` attributes:

```python
# Core stats
char.db.hunger = 1              # int (0-5)
char.db.blood_potency = 0       # int (0-10)
char.db.humanity = 7            # int (0-10)
char.db.willpower = 5           # int (current pool)
char.db.willpower_max = 5       # int (max pool)
char.db.health = 7              # int (current health)
char.db.health_max = 7          # int (max health)

# Structured data
char.db.stats = {
    "attributes": {
        "Physical": {"Strength": 3, "Dexterity": 2, "Stamina": 3},
        "Social": {"Charisma": 2, "Manipulation": 2, "Composure": 3},
        "Mental": {"Intelligence": 3, "Wits": 2, "Resolve": 2}
    },
    "skills": {
        "Physical": {"Athletics": 2, "Brawl": 3, "Stealth": 1},
        "Social": {"Intimidation": 2, "Persuasion": 1},
        "Mental": {"Academics": 2, "Investigation": 3}
    }
}

# Clan and bloodline
char.db.clan = "Brujah"
char.db.generation = 13

# Disciplines
char.db.disciplines = {
    "Celerity": 2,
    "Potence": 1,
    "Presence": 1
}

# Backgrounds
char.db.backgrounds = {
    "Resources": 2,
    "Contacts": 3,
    "Herd": 1
}

# Merits/Flaws
char.db.merits = ["Eat Food", "Blush of Health"]
char.db.flaws = ["Enemy"]

# Predator type
char.db.predator_type = "Alleycat"

# Touchstones (Phase 11)
char.db.touchstones = [
    {"name": "Sarah Miller", "conviction": "Protect the innocent"}
]

# Status (Phase 12)
char.db.status = {
    "Camarilla": 2,
    "titles": ["Neonate"]
}

# Boons (Phase 12)
char.db.boons_owed = []  # List of {creditor: name, boon: type, description: str}
char.db.boons_held = []  # List of {debtor: name, boon: type, description: str}
```

### Accessing Character Data

```python
# In commands
class CmdSheet(Command):
    def func(self):
        char = self.caller

        # Direct access
        hunger = char.db.hunger

        # Safe access with defaults
        blood_potency = char.db.blood_potency or 0

        # Structured access
        strength = char.db.stats["attributes"]["Physical"]["Strength"]

        # Using utility functions (preferred)
        from .utils.trait_utils import get_attribute, get_skill
        strength = get_attribute(char, "Strength")
        athletics = get_skill(char, "Athletics")
```

---

## Command Organization

### Directory Structure

```
beckonmu/commands/v5/
├── __init__.py                 # Package initialization
├── README.md                   # This file
├── dice_commands.py            # +roll, +rouse commands
├── sheet_commands.py           # +sheet, +stats commands
├── blood_commands.py           # +feed, +slake commands
├── discipline_commands.py      # Discipline activation commands
├── chargen_commands.py         # Character creation commands
├── admin_commands.py           # Staff-only V5 admin commands
└── utils/                      # Shared utility modules
    ├── __init__.py
    ├── dice_utils.py           # Dice rolling logic
    ├── trait_utils.py          # Attribute/skill access
    ├── display_utils.py        # Formatted output (uses ansi_theme)
    ├── blood_utils.py          # Hunger/feeding logic
    └── validation_utils.py     # Input validation
```

### Command Set Registration

```python
# beckonmu/commands/default_cmdsets.py

from evennia import default_cmds
from commands.v5 import dice_commands, sheet_commands

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """Adds V5 commands to all characters."""

    def at_cmdset_creation(self):
        super().at_cmdset_creation()

        # Add V5 commands
        self.add(dice_commands.CmdRoll())
        self.add(dice_commands.CmdRouseCheck())
        self.add(sheet_commands.CmdSheet())
        # ... more commands
```

---

## Utility Module Patterns

### Dice Utilities (`dice_utils.py`)

```python
# beckonmu/commands/v5/utils/dice_utils.py

from beckonmu.world.v5_dice import roll_pool, DiceResult
from beckonmu.world.ansi_theme import *

def roll_attribute_skill(char, attribute, skill, difficulty=0):
    """
    Roll an Attribute + Skill pool with character's current Hunger.

    Args:
        char: Character object
        attribute (str): Attribute name ("Strength", "Charisma", etc.)
        skill (str): Skill name ("Athletics", "Persuasion", etc.)
        difficulty (int): Number of successes needed

    Returns:
        DiceResult: The roll result
    """
    from .trait_utils import get_attribute, get_skill

    attr_value = get_attribute(char, attribute)
    skill_value = get_skill(char, skill)
    pool = attr_value + skill_value
    hunger = char.db.hunger or 0

    return roll_pool(pool, hunger, difficulty)

def format_roll_result(result, character_name="You"):
    """Format DiceResult with themed ANSI output."""
    # Implementation uses ansi_theme constants
    pass
```

### Trait Utilities (`trait_utils.py`)

```python
# beckonmu/commands/v5/utils/trait_utils.py

def get_attribute(char, attr_name):
    """
    Safely get an attribute value.

    Args:
        char: Character object
        attr_name (str): Attribute name

    Returns:
        int: Attribute value (default 1 if not found)
    """
    if not hasattr(char.db, 'stats') or not char.db.stats:
        return 1

    for category in ["Physical", "Social", "Mental"]:
        if attr_name in char.db.stats["attributes"][category]:
            return char.db.stats["attributes"][category][attr_name]

    return 1  # Default starting value

def get_skill(char, skill_name):
    """Safely get a skill value (default 0)."""
    # Similar pattern
    pass

def set_attribute(char, attr_name, value):
    """Safely set an attribute value with validation."""
    if value < 1 or value > 5:
        raise ValueError("Attributes must be 1-5")
    # Set value
    pass

def calculate_dice_pool(char, attribute, skill, modifiers=0):
    """Calculate total dice pool including modifiers."""
    return get_attribute(char, attribute) + get_skill(char, skill) + modifiers
```

### Display Utilities (`display_utils.py`)

```python
# beckonmu/commands/v5/utils/display_utils.py

from beckonmu.world.ansi_theme import *

def format_trait_line(trait_name, value, max_dots=5):
    """
    Format a trait line for character sheet.

    Example output: "Strength    ●●●○○"
    """
    dots = trait_dots(value, max_dots)
    return f"{trait_name:<12} {dots}"

def format_character_sheet(char):
    """Generate full character sheet output."""
    # Uses SHEET_TEMPLATE from THEMING_GUIDE.md
    pass
```

---

## Testing Strategy

### Test Organization

```
beckonmu/tests/v5/
├── __init__.py
├── test_dice.py                # Dice rolling tests
├── test_traits.py              # Attribute/skill tests
├── test_blood.py               # Hunger/feeding tests
├── test_disciplines.py         # Discipline tests
├── test_chargen.py             # Character creation tests
└── test_commands.py            # Command integration tests
```

### Example Test File

```python
# beckonmu/tests/v5/test_dice.py

from evennia.utils.test_resources import EvenniaTest
from beckonmu.world.v5_dice import roll_pool, rouse_check, DiceResult

class TestDiceRolling(EvenniaTest):
    """Test V5 dice rolling mechanics."""

    def test_roll_pool_creates_correct_dice_counts(self):
        """Roll pool should split dice between normal and Hunger correctly."""
        result = roll_pool(pool=5, hunger=2, difficulty=0)

        self.assertEqual(len(result.normal_dice), 3)
        self.assertEqual(len(result.hunger_dice), 2)

    def test_roll_pool_with_zero_hunger(self):
        """Roll with no Hunger should have all normal dice."""
        result = roll_pool(pool=5, hunger=0, difficulty=0)

        self.assertEqual(len(result.normal_dice), 5)
        self.assertEqual(len(result.hunger_dice), 0)

    def test_successes_counted_correctly(self):
        """Successes are 6+ on any die."""
        # Mock dice results for deterministic testing
        result = DiceResult(
            normal_dice=[6, 7, 8, 4, 3],
            hunger_dice=[10, 5],
            difficulty=0
        )

        self.assertEqual(result.successes, 4)  # 6,7,8,10 are successes

    def test_messy_critical_detection(self):
        """Messy Critical occurs when Hunger die is in a critical pair."""
        result = DiceResult(
            normal_dice=[10, 7, 6],
            hunger_dice=[10, 5],
            difficulty=0
        )

        self.assertTrue(result.is_messy)
        self.assertEqual(result.criticals, 1)  # One pair of 10s

    def test_bestial_failure_detection(self):
        """Bestial Failure occurs on total failure with Hunger dice."""
        result = DiceResult(
            normal_dice=[3, 2, 1],
            hunger_dice=[4, 2],
            difficulty=0
        )

        self.assertTrue(result.is_bestial)
        self.assertEqual(result.successes, 0)

    def test_rouse_check_success(self):
        """Rouse check succeeds on 6+."""
        # Run multiple times to test randomness
        successes = 0
        trials = 1000

        for _ in range(trials):
            success, _ = rouse_check(blood_potency=0)
            if success:
                successes += 1

        # Should be roughly 50% success rate (6-10 out of 1-10)
        self.assertGreater(successes, 400)
        self.assertLess(successes, 600)
```

### Running Tests

```bash
# Run all tests
evennia test

# Run specific test file
evennia test beckonmu.tests.v5.test_dice

# Run specific test class
evennia test beckonmu.tests.v5.test_dice.TestDiceRolling

# Run specific test method
evennia test beckonmu.tests.v5.test_dice.TestDiceRolling.test_messy_critical_detection
```

---

## Phase Implementation Order

Per V5_IMPLEMENTATION_ROADMAP.md:

1. **Phase 0** ✓ (Current): Architecture and skeletons
2. **Phase 1**: Help System (documentation foundation)
3. **Phase 2**: BBS System (communication)
4. **Phase 3**: Jobs System (staff workflow)
5. **Phase 4**: Trait System (attributes, skills, database-driven)
6. **Phase 5**: Dice Rolling Engine (complete v5_dice.py)
7. **Phase 6**: Blood Systems (Hunger, feeding, Rouse)
8. **Phase 7**: Clan System (clan data, banes, compulsions)
9. **Phase 8**: Discipline Framework (powers)
10. **Phase 9**: Character Creation (integrated chargen)
11. **Phase 10**: Character Sheet Display
12. **Phase 11+**: Advanced systems

---

## Success Criteria for Phase 0

- [x] Directory structure created
- [x] `ansi_theme.py` with color constants and helpers
- [x] `connection_screens.py` with V:tM themed ASCII art
- [x] `v5_data.py` configuration skeleton
- [x] `v5_dice.py` dice engine skeleton
- [x] This architectural documentation (README.md)
- [ ] Test directory structure
- [ ] Core Evennia commands verified
- [ ] Directory imports tested

---

## Key Takeaways

1. **Keep commands small** - One command, one job
2. **Share logic in utils** - Don't repeat yourself
3. **Store data in database** - Not in Python files
4. **Write tests first** - RED → GREEN → REFACTOR
5. **Use ansi_theme** - Consistent gothic aesthetics
6. **Follow the roadmap** - Dependencies matter

---

**Next Step:** Phase 1 (Help System) - Establish documentation foundation before implementing mechanics.
