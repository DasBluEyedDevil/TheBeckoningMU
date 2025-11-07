# Dice Commands Integration Guide

This document explains how to integrate the new V5 dice commands into your Evennia game.

## Overview

The new dice system in `beckonmu/dice/` provides comprehensive V5 mechanics with:
- **CmdRoll**: Basic dice pool rolling with Hunger, difficulty, Willpower rerolls
- **CmdRollPower**: Automatic discipline power rolling with trait integration
- **CmdRouse**: Standalone Rouse checks with Blood Potency rerolls
- **CmdShowDice**: In-game reference for dice mechanics

## Quick Integration

### Option 1: Add the DiceCmdSet (Recommended)

Edit `beckonmu/commands/default_cmdsets.py`:

```python
class CharacterCmdSet(cmdset_character.CharacterCmdSet):
    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()

        # Add V5 dice commands (NEW SYSTEM)
        from beckonmu.dice.cmdset import DiceCmdSet
        self.add(DiceCmdSet)

        # ... other command sets ...
```

### Option 2: Add Individual Commands

If you prefer to add commands individually:

```python
from beckonmu.dice.commands import CmdRoll, CmdRollPower, CmdRouse, CmdShowDice

class CharacterCmdSet(cmdset_character.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()

        self.add(CmdRoll())
        self.add(CmdRollPower())
        self.add(CmdRouse())
        self.add(CmdShowDice())
```

## Replacing Old Commands

The current system has older, simpler dice commands in `commands/v5/dice.py`:
- `CmdRoll` (key: "+roll")
- `CmdRollStat` (key: "+rollstat")
- `CmdRouseCheck` (key: "+rouse")

To replace them with the new system:

### Step 1: Remove old command imports

In `beckonmu/commands/default_cmdsets.py`, **remove or comment out**:

```python
# OLD SYSTEM - Remove these lines:
# from commands.v5.dice import CmdRoll, CmdRollStat, CmdRouseCheck
# self.add(CmdRoll)
# self.add(CmdRollStat)
# self.add(CmdRouseCheck)
```

### Step 2: Add new command set

Replace with:

```python
# NEW SYSTEM - Add this:
from beckonmu.dice.cmdset import DiceCmdSet
self.add(DiceCmdSet)
```

### Step 3: Reload the server

```bash
evennia reload
```

## Command Comparison

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `+roll <pool>` | `roll <pool> [<hunger>] [vs <difficulty>]` | Much more comprehensive |
| `+rollstat attr+skill` | `power <power_name>` | Automatic trait lookup + Blood Potency |
| `+rouse` | `rouse [<reason>]` | Includes Blood Potency rerolls |
| N/A | `showdice` | New: In-game mechanics reference |

## New Features

The new dice system adds:

1. **Full V5 Mechanics**:
   - Hunger dice with visual differentiation
   - Critical wins (pair of 10s)
   - Messy Criticals (critical with Hunger 10)
   - Bestial Failures (failure with only Hunger 1s)
   - Proper success counting (6-9 = 1, 10 = 2)

2. **Discipline Powers**:
   - Automatic dice pool calculation from character traits
   - Blood Potency bonus dice
   - Integrated Rouse checks
   - Power database lookup

3. **Rouse Checks**:
   - Blood Potency reroll mechanics
   - Automatic Hunger tracking
   - Visual Hunger display

4. **Beautiful Output**:
   - ANSI color-coded dice results
   - Detailed breakdowns
   - Narrative result descriptions
   - Room broadcast for visibility

5. **Advanced Options**:
   - `/willpower` switch for reroll offers
   - `/secret` switch for private rolls
   - `/norouse` switch for free powers

## Testing the Commands

After integration, test the commands:

```
# Basic roll
roll 5

# Roll with Hunger
roll 5 2

# Roll vs difficulty
roll 7 3 vs 4

# Roll with switches
roll/willpower 4 2 vs 3
roll/secret 6 1

# Discipline power (requires character with powers)
power Heightened Senses
power Corrosive Vitae vs 3

# Rouse check
rouse
rouse Blood Surge

# Dice reference
showdice
showdice hunger
showdice criticals
```

## Troubleshooting

### Import Errors

If you get import errors, ensure:
1. All files in `beckonmu/dice/` are present
2. The `traits` app is properly installed
3. You've run `evennia reload` after adding commands

### Character Not Found

Commands require a Character object. If you get "must be in character":
1. Ensure you're puppeting a character (not just logged into an Account)
2. Check that your character inherits from `typeclasses.characters.Character`

### Missing Traits

If `power` command fails with "trait not found":
1. Ensure character has traits set up via the `traits` system
2. Check that discipline powers exist in the database
3. Verify character has `CharacterPower` entries for known powers

### Hunger Not Tracking

If Hunger doesn't update:
1. Check `character.db.hunger` is set (default should be 1)
2. Verify `rouse_checker.set_hunger_level()` is working
3. Check that character object persists changes

## Architecture

The dice system is organized into modules:

- `dice_roller.py`: Core V5 rolling mechanics (pure functions)
- `roll_result.py`: Result parsing and formatting
- `discipline_roller.py`: Discipline power integration with traits
- `rouse_checker.py`: Rouse check mechanics with Blood Potency
- `commands.py`: Evennia MuxCommand implementations
- `cmdset.py`: Command set grouping

This separation allows you to:
- Use dice functions programmatically without commands
- Extend commands with custom behavior
- Add new commands that use existing dice mechanics

## Next Steps

After integration, consider:

1. **Willpower Reroll Implementation**: Add a `willpower reroll` command that actually consumes Willpower and performs rerolls
2. **Contested Rolls**: Add `CmdContest` for opposed rolls between characters
3. **Roll Macros**: Allow players to save common rolls as shortcuts
4. **Roll History**: Track recent rolls for debugging and verification
5. **Dice Pools Display**: Show character's dice pools for all traits/powers

## See Also

- `beckonmu/dice/README.md` - Dice system overview
- Phase 5 implementation plan - Original design document
- V5 Core Rulebook - Full game mechanics reference
