# Coding Conventions

**Analysis Date:** 2026-02-03

## Naming Patterns

**Files:**
- Module files: `snake_case.py` (e.g., `blood_utils.py`, `trait_utils.py`)
- Test files: `test_*.py` or `*_tests.py` (e.g., `test_blood_utils.py`, `dice/tests.py`)
- Utility modules: `*_utils.py` (e.g., `blood_utils.py`, `background_utils.py`)
- Command files: descriptive names (e.g., `backgrounds.py`, `blood.py`, `combat.py`)

**Functions:**
- Use `snake_case` for all function names
- Private/internal functions: prefix with `_` (e.g., `_db_get_trait()`, `_validate_pool_params()`)
- Public APIs: no prefix (e.g., `get_hunger_level()`, `activate_blood_surge()`)
- Getter functions: `get_*` pattern (e.g., `get_hunger_level()`, `get_blood_surge()`)
- Setter functions: `set_*` pattern (e.g., `set_hunger_level()`, `set_resonance()`)
- Modifier functions: `increase_*`, `reduce_*` patterns (e.g., `increase_hunger()`, `reduce_hunger()`)
- Display/format functions: `format_*` pattern (e.g., `format_hunger_display()`, `format_resonance_display()`)

**Variables:**
- Local variables: `snake_case` (e.g., `hunger_level`, `character_trait`, `blood_potency`)
- Constants: `UPPER_CASE` (e.g., `RESONANCE_DISCIPLINES`, `RESONANCE_INTENSITY`)
- Dictionary keys: `snake_case` (e.g., `character.db.stats`, `char.db.vampire['hunger']`)
- Parameters: `snake_case` (e.g., `hunger`, `trait_name`, `intensity`, `duration`)

**Types/Classes:**
- Classes: `PascalCase` (e.g., `Command`, `Character`, `DiceResult`)
- Exception types: `PascalCase` ending with `Error` or `Exception`
- Model classes: `PascalCase` (e.g., `TraitCategory`, `CharacterTrait`, `DisciplinePower`)

## Code Style

**Formatting:**
- Python version: 3.13+
- No specific linter/formatter detected (no `.flake8`, `.black`, `pyproject.toml` config)
- Line length: appears to follow conventional ~100 character limit
- Indentation: 4 spaces (standard Python)

**Linting:**
- No linting configuration found in repository
- Follow PEP 8 conventions implicitly

## Import Organization

**Order:**
1. Standard library imports (e.g., `import time`, `import unittest`)
2. Third-party imports (e.g., `from unittest.mock import Mock`, `from django.db import models`)
3. Evennia framework imports (e.g., `from evennia import Command`, `from evennia.utils.test_resources import EvenniaTest`)
4. Local/relative imports (e.g., `from .models import Board`, `from beckonmu.commands.v5.utils import blood_utils`)

**Pattern observed in codebase:**
```python
"""Module docstring."""

import time
from typing import Dict, Any, Optional
from unittest.mock import patch, Mock

from django.db import models
from evennia.utils.test_resources import EvenniaTest

from beckonmu.commands.v5.utils import blood_utils
from .models import Character
```

**Path Aliases:**
- No aliases detected in `pyproject.toml`
- Relative imports used within packages: `from .models import`, `from .utils import`
- Absolute imports for cross-module access: `from beckonmu.commands.v5.utils import blood_utils`

## Error Handling

**Patterns:**
- Use specific exception types instead of bare `except:` or `except Exception:`
- Common patterns in codebase:
  - `except AttributeError:` for missing attributes
  - `except TypeError:` for type issues
  - `except ObjectDoesNotExist:` for Django model queries
  - `except Trait.DoesNotExist:` for model-specific exceptions
  - `except ValidationError:` for validation failures
  - `except ImportError:` for optional imports

**Example from `blood_utils.py`:**
```python
try:
    # Try new vampire data structure first
    vampire_data = getattr(character.db, 'vampire', None)
    if vampire_data and isinstance(vampire_data, dict):
        hunger = vampire_data.get('hunger', 1)
    else:
        # Fall back to legacy structure
        hunger = getattr(character.db, 'hunger', 1)
except (AttributeError, TypeError):
    hunger = 1

# Handle None case
if hunger is None:
    hunger = 1
```

**Error message style:**
- Styled error messages in commands use `|r` (red) for errors, `|y` (yellow) for usage
- Example: `self.caller.msg(f"|r{message}|n")`

## Logging

**Framework:** `console` messaging via Evennia's command system
- Commands use `self.caller.msg()` for messaging
- No centralized logging module found
- Error output follows ANSI color conventions (`|r` red, `|y` yellow, `|g` green, `|c` cyan, `|h` bright)

## Comments

**When to Comment:**
- Module docstrings: always include (describe purpose, provide examples if needed)
- Class docstrings: always include (describe purpose and key attributes)
- Function docstrings: always use triple-quoted docstrings with Args, Returns, Examples sections
- Complex logic: comment why something is done, not what is being done
- Workarounds: comment when using non-obvious approaches

**Docstring Format (Google-style):**
```python
def get_hunger_level(character) -> int:
    """
    Get character's current Hunger level.

    Supports both new vampire data structure (character.db.vampire['hunger'])
    and legacy structure (character.db.hunger).

    Args:
        character: Character object

    Returns:
        int: Hunger level (0-5), defaults to 1 if not set
    """
```

**Type Hints:**
- Used in function signatures (e.g., `def get_hunger_level(character) -> int:`)
- Used in parameter lists: `hunger: int`, `trait_name: str`
- Used in return types explicitly
- Dictionary hints: `Dict[str, Any]`, `Optional[Dict]`

## Function Design

**Size:**
- Functions generally kept small and focused on single responsibility
- Complex functions broken into smaller helper functions (e.g., `_db_get_trait()`)
- Utility functions 30-100 lines typical

**Parameters:**
- Named parameters preferred over positional
- Optional parameters with sensible defaults (e.g., `duration=3600`)
- Avoid excessive parameter lists; use objects when needed

**Return Values:**
- Single return type per function (no conditional types)
- Commonly return:
  - Simple values (int, bool, str)
  - Dictionaries for complex results (e.g., rouse check returns `{'success': bool, 'message': str}`)
  - None for operations with side effects
  - Tuples for multiple return values (rare, e.g., `(success, die_value)`)

## Module Design

**Exports:**
- Utils modules export public functions (no `__all__` found, but convention is clear)
- Private functions start with `_` (e.g., `_db_get_trait()`)
- Commands import specific functions needed

**Structure Pattern:**
- Docstring at top describing module purpose
- Constants defined after docstring (e.g., `RESONANCE_DISCIPLINES = {...}`)
- Internal/private functions with `_` prefix before public functions
- Public API functions at module level
- Section headers with separators for organization:
  ```python
  # ============================================================================
  # Internal Bridge Functions
  # ============================================================================
  ```

**Example from `trait_utils.py`:**
```python
"""
Trait Utility Functions for V5 System

Provides functions for safely getting and setting character traits...
"""

# ============================================================================
# Internal Bridge Functions
# ============================================================================

def _db_get_trait(character, trait_name):
    """Internal function..."""

def _db_set_trait(character, trait_name, value):
    """Internal function..."""

# ============================================================================
# Public API Functions
# ============================================================================

def get_trait_value(character, trait_name, category=None):
    """Public function..."""
```

## Data Structures

**Character data organization:**
- `character.db.stats`: Contains attributes, skills, specialties, disciplines
- `character.db.vampire`: Clan, generation, blood potency, hunger, humanity
- `character.db.pools`: Health, willpower, damage tracking
- `character.db.advantages`: Backgrounds, merits, flaws
- `character.db.effects`: Active discipline effects
- `character.ndb.*`: Non-persistent (memory-only) attributes

**Dictionary key conventions:**
- Snake_case for keys (e.g., `character.db.stats['attributes']`)
- Hierarchical nesting for related data
- Validation with `.get()` for optional keys with defaults

## Command Structure

**Base inheritance:**
- Custom commands inherit from `beckonmu.commands.command.Command` base class
- Override `func()` method for command logic
- Use `self.caller` to send messages to executor

**Helper methods from custom Command class:**
- `self.styled_error(message)`: Send red error message
- `self.styled_usage()`: Display usage information
- `self.syntax_error(custom_message)`: Show syntax error with usage

---

*Convention analysis: 2026-02-03*
