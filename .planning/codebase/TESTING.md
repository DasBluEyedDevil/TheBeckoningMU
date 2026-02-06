# Testing Patterns

**Analysis Date:** 2026-02-03

## Test Framework

**Runner:**
- `unittest` (Python standard library)
- Evennia's `EvenniaTest` base class (extends Django's `TestCase`)
- Tests run via `evennia test` command

**Assertion Library:**
- `unittest.TestCase` assertion methods (`assertEqual()`, `assertTrue()`, `assertFalse()`, etc.)
- `assertIsNone()`, `assertIsNotNone()` for None checks
- `assertGreater()`, `assertLess()`, `assertGreaterEqual()`, `assertLessEqual()` for comparisons
- `assertAlmostEqual(a, b, delta=tolerance)` for floating-point comparisons

**Run Commands:**
```bash
evennia test                    # Run all tests
evennia test beckonmu.tests     # Run specific test module
evennia test --settings=...     # Run with custom settings
```

## Test File Organization

**Location:**
- Co-located with source code in `tests/` subdirectories and `tests.py` files
- Mixed pattern: some modules use `tests.py` files, some use `tests/` directories

**Examples:**
- `beckonmu/commands/v5/tests/test_v5_dice.py` - Separate `tests/` directory
- `beckonmu/dice/tests.py` - Single `tests.py` file in module
- `beckonmu/jobs/tests.py` - Single `tests.py` file in module
- `beckonmu/tests/v5/test_blood_utils.py` - Centralized test directory
- `beckonmu/traits/tests.py` - Single `tests.py` file in module

**Naming:**
- Prefix with `test_`: `test_v5_dice.py`, `test_blood_utils.py`
- Or use: `tests.py`, `*_tests.py`

**Structure:**
```
beckonmu/
├── commands/
│   └── v5/
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── test_v5_dice.py
│       │   └── test_trait_utils.py
│       └── blood.py
├── tests/
│   ├── __init__.py
│   ├── test_character_vampire_data.py
│   └── v5/
│       ├── __init__.py
│       ├── test_blood_commands.py
│       └── test_blood_utils.py
└── dice/
    ├── dice_roller.py
    └── tests.py
```

## Test Structure

**Suite Organization - Standard Pattern:**

```python
"""
Module docstring describing what's tested.

Lists all test classes and their purposes.
"""

import unittest
from unittest.mock import Mock, patch

from evennia.utils.test_resources import EvenniaTest
from beckonmu.commands.v5.utils import blood_utils


class HungerManagementTests(EvenniaTest):
    """Test Hunger level management functions."""

    def setUp(self):
        """Set up test fixtures before each test."""
        super().setUp()
        self.char = self.char1

    def test_get_hunger_level_default(self):
        """Test getting default Hunger level when not set."""
        # Arrange: Clear any existing hunger
        if hasattr(self.char.db, 'hunger'):
            del self.char.db.hunger

        # Act: Call function
        hunger = blood_utils.get_hunger_level(self.char)

        # Assert: Verify result
        self.assertEqual(hunger, 1, "Default Hunger should be 1")

    def tearDown(self):
        """Clean up after each test (if needed)."""
        super().tearDown()
```

**Patterns:**
- `setUp()`: Initialize test fixtures before each test
- `tearDown()`: Clean up after each test (optional, usually handled by base class)
- `setUpClass()`: Initialize class-level fixtures (rare)
- Each test method starts with `test_` prefix
- Each test has single responsibility

## Mocking

**Framework:** `unittest.mock` module

**Patterns:**

**1. Mock Objects for Attributes:**
```python
from unittest.mock import Mock

def setUp(self):
    self.character = Mock()
    self.character.db = Mock()
    self.character.db.stats = {
        'attributes': {
            'physical': {'strength': 3, 'dexterity': 2}
        }
    }
```

**2. Patch Decorators for Functions:**
```python
from unittest.mock import patch

@patch('beckonmu.dice.rouse_checker.perform_rouse_check')
def test_blood_surge(self, mock_rouse):
    """Test with mocked rouse check."""
    mock_rouse.return_value = {
        'success': True,
        'hunger_after': 2
    }
    # Test code here
    mock_rouse.assert_called_once()
```

**3. Multiple Patches:**
```python
@patch('traits.utils.get_character_trait_value')
@patch('beckonmu.dice.rouse_checker.perform_rouse_check')
def test_blood_surge_with_traits(self, mock_rouse, mock_trait):
    """Test with multiple mocks (applied bottom-to-top)."""
    mock_trait.return_value = 3
    mock_rouse.return_value = {'success': True}
    # Test code
```

**4. MagicMock for Complex Behavior:**
```python
from unittest.mock import MagicMock

mock_command = MagicMock()
mock_command.caller.msg.return_value = None
# Test can now call mock_command and verify calls were made
```

**What to Mock:**
- External service calls (database lookups, API calls)
- Time-dependent functions (use `@patch('time.time')`)
- Random functions (dice rolls often patched to control results)
- Complex dependencies (other utility modules)

**What NOT to Mock:**
- Functions being tested themselves
- Simple data structures (dictionaries, lists)
- Built-in functions (len, str, int, etc.)
- Internal helper functions (test them directly instead)

## Fixtures and Factories

**Test Data:**

**1. Evennia Base Class Fixtures:**
```python
from evennia.utils.test_resources import EvenniaTest

class MyTest(EvenniaTest):
    def setUp(self):
        super().setUp()
        # Available fixtures:
        self.char1      # Created character
        self.char2      # Second character
        self.account    # Player account
        self.room1      # Game room
        self.obj        # Game object
```

**2. Mock Character Dictionary Setup:**
```python
def setUp(self):
    self.character = Mock()
    self.character.db = Mock()
    self.character.db.stats = {
        'attributes': {
            'physical': {'strength': 3, 'dexterity': 2, 'stamina': 3},
            'social': {'charisma': 2, 'manipulation': 2, 'composure': 3},
            'mental': {'intelligence': 4, 'wits': 3, 'resolve': 3}
        },
        'skills': {
            'physical': {'athletics': 2, 'brawl': 3, 'drive': 0},
            'social': {'intimidation': 2, 'persuasion': 1},
            'mental': {'academics': 3, 'investigation': 2, 'occult': 1}
        },
        'disciplines': {
            'potence': {'level': 2, 'powers': []},
            'fortitude': {'level': 1, 'powers': []}
        }
    }
    self.character.db.advantages = {
        'backgrounds': {'herd': 2, 'resources': 3},
        'merits': {},
        'flaws': {}
    }
```

**Location:**
- Fixtures defined in `setUp()` methods
- No separate factory files found
- Evennia's `EvenniaTest` provides base character/room/object fixtures

## Coverage

**Requirements:** No enforced coverage target detected

**View Coverage:**
```bash
evennia test --coverage                  # May work with evennia test
python -m coverage run manage.py test    # Alternative if available
python -m coverage report                # View coverage report
python -m coverage html                  # Generate HTML report
```

## Test Types

**Unit Tests:**
- Test individual functions in isolation
- Mock external dependencies
- Located in `test_*.py` files
- Focus on a single function or small feature
- Examples: `test_v5_dice.py`, `test_blood_utils.py`, `test_trait_utils.py`

**Integration Tests:**
- Test multiple components working together
- Use Evennia's `EvenniaTest` base class
- Access real character/room/object fixtures
- Examples: `test_blood_commands.py` tests commands + blood_utils together

**E2E Tests:**
- Not detected in codebase
- Would test full game flows (login, chargen, play)

## Common Patterns

**Async Testing:**
Not prevalent in codebase. Evennia handles async at framework level.

**Error Testing:**

```python
def test_get_trait_not_found(self):
    """Test that unknown traits return 0."""
    value = trait_utils._db_get_trait(self.character, 'nonexistent_trait')
    self.assertEqual(value, 0, "Unknown trait should return 0")

def test_set_trait_not_found(self):
    """Test that setting unknown trait returns False."""
    success = trait_utils._db_set_trait(self.character, 'nonexistent', 5)
    self.assertFalse(success, "Setting unknown trait should return False")
```

**Boundary/Edge Case Testing:**

```python
def test_hunger_edge_case_zero_to_five(self):
    """Test full range transition from 0 to 5."""
    self.char.db.hunger = 0
    for expected in range(1, 6):
        new_hunger = blood_utils.increase_hunger(self.char, 1)
        self.assertEqual(new_hunger, expected)

def test_hunger_edge_case_five_to_zero(self):
    """Test full range transition from 5 to 0."""
    self.char.db.hunger = 5
    for expected in range(4, -1, -1):
        new_hunger = blood_utils.reduce_hunger(self.char, 1)
        self.assertEqual(new_hunger, expected)
```

**Clamping/Boundary Testing:**

```python
def test_set_hunger_level_clamps_upper(self):
    """Test Hunger level clamping at upper bound."""
    hunger = blood_utils.set_hunger_level(self.char, 10)
    self.assertEqual(hunger, 5, "Hunger should be clamped to 5")

def test_set_hunger_level_clamps_lower(self):
    """Test Hunger level clamping at lower bound."""
    hunger = blood_utils.set_hunger_level(self.char, -5)
    self.assertEqual(hunger, 0, "Hunger should be clamped to 0")
```

**State Verification:**

```python
def test_resonance_replaces_previous(self):
    """Test that setting new resonance replaces previous."""
    blood_utils.set_resonance(self.char, 'Choleric', intensity=1)
    blood_utils.set_resonance(self.char, 'Melancholic', intensity=2)

    resonance = blood_utils.get_resonance(self.char)
    self.assertEqual(resonance['type'], 'Melancholic')
    self.assertEqual(resonance['intensity'], 2)
```

**Mock Assertion Patterns:**

```python
def test_blood_surge_performs_rouse_check(self, mock_rouse, mock_trait):
    """Test Blood Surge performs Rouse check."""
    mock_trait.return_value = 1
    mock_rouse.return_value = {'success': True, 'hunger_after': 2}

    blood_utils.activate_blood_surge(self.char, 'attribute', 'Dexterity')

    # Verify mock was called
    mock_rouse.assert_called_once()
    call_args = mock_rouse.call_args
    self.assertEqual(call_args[0][0], self.char)
    self.assertIn('Dexterity', call_args[1]['reason'])
```

**Statistical Testing (for randomness):**

```python
def test_rouse_check_success_threshold(self):
    """Test that success is True for 6+ and False for 1-5."""
    successes = 0
    failures = 0
    for _ in range(100):
        success, die_value = rouse_check(blood_potency=0)
        if success:
            successes += 1
            self.assertGreaterEqual(die_value, 6)
        else:
            failures += 1
            self.assertLessEqual(die_value, 5)

    # With 100 rolls, we should have both outcomes
    self.assertGreater(successes, 0)
    self.assertGreater(failures, 0)
```

## Test Organization Best Practices

**1. Descriptive Test Names:**
- Format: `test_<function>_<condition>_<expected_result>`
- Examples:
  - `test_get_hunger_level_default`
  - `test_set_hunger_level_clamps_upper`
  - `test_blood_surge_replaces_previous`

**2. Test Docstrings:**
- Every test has a docstring explaining what it validates
- Format: Short sentence describing the test
- Example:
  ```python
  def test_critical_pairs(self):
      """Test that critical pairs are calculated correctly."""
  ```

**3. Arrange-Act-Assert Pattern:**
```python
def test_example(self):
    """Test description."""
    # Arrange: Set up test data
    self.char.db.hunger = 3

    # Act: Execute function
    new_hunger = blood_utils.increase_hunger(self.char, 2)

    # Assert: Verify results
    self.assertEqual(new_hunger, 5)
    self.assertEqual(self.char.db.hunger, 5)
```

**4. Comment Changes:**
- Use inline comments to explain test data that isn't obvious
- Example:
  ```python
  # Two 10s = 1 critical pair
  result = DiceResult(normal_dice=[10, 10, 5, 3])
  ```

**5. Test Grouping:**
- Group related tests in test classes
- One test class per function/feature set
- Examples: `HungerManagementTests`, `BloodSurgeManagementTests`, `EdgeCaseTests`

## Test Execution

**Running Tests:**
```bash
# Run all tests
evennia test

# Run specific module
evennia test beckonmu.tests.v5.test_blood_utils

# Run specific test class
evennia test beckonmu.tests.v5.test_blood_utils.HungerManagementTests

# Run specific test method
evennia test beckonmu.tests.v5.test_blood_utils.HungerManagementTests.test_get_hunger_level_default
```

---

*Testing analysis: 2026-02-03*
