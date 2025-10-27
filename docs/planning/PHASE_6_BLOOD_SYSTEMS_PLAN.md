# Phase 6: Blood Systems Implementation Plan

**Phase**: 6 - Blood Systems (Hunger, Blood Potency, Resonance)
**Status**: Ready to Implement
**Created**: 2025-10-27
**Dependencies**: Phase 5 (Dice System) ✅ COMPLETE

---

## Overview

Phase 6 implements the core vampire resource management systems: feeding mechanics, blood surge, resonance tracking, and proper vampire data structures. This builds on the Hunger and Blood Potency mechanics already implemented in Phase 5's dice system.

### What's Already Done (from Phase 5)

✅ **Hunger Tracking**:
- `character.db.hunger` storage
- Hunger levels 0-5
- Hunger dice in rolls
- `rouse` command functional
- Blood Potency rerolls for Rouse checks

✅ **Blood Potency**:
- Stored in traits system
- Bonus dice for discipline rolls (+0 to +5)
- Reroll eligibility for Rouse checks
- Integration with discipline_roller

### What Needs Implementation (Phase 6)

❌ **Feeding System**:
- `CmdFeed` command for hunting/feeding
- Hunger reduction mechanics
- Resonance tracking during feeding
- Feeding complications (Messy Criticals)

❌ **Blood Surge**:
- `CmdBloodSurge` command
- Rouse check for activation
- Temporary attribute/skill bonuses
- Duration tracking

❌ **Vampire Data Structure**:
- Proper `char.db.vampire` structure
- Blood Potency metadata
- Resonance tracking
- Bane and compulsion storage

❌ **Hunger Management**:
- `CmdHunger` view command
- Visual Hunger display (already in dice system, extend)
- Hunger effects description

❌ **Backend Utilities**:
- `blood_utils.py` for shared logic
- Resonance mechanics
- Blood Surge effects
- Feeding resolution

---

## Implementation Tasks

### Task 1: Vampire Data Structure

**File**: `beckonmu/typeclasses/characters.py`

**Modify `at_object_creation()`** to initialize:

```python
def at_object_creation(self):
    """Called when character is first created."""
    super().at_object_creation()

    # Initialize vampire data structure
    self.db.vampire = {
        "clan": None,  # Set during chargen
        "generation": 13,  # Default for neonates
        "blood_potency": 0,  # Separate from trait (0-10 scale)
        "hunger": 1,  # 0-5, starts at 1
        "humanity": 7,  # 0-10, default 7
        "predator_type": None,  # Set during chargen
        "current_resonance": None,  # Last feeding resonance
        "resonance_intensity": 0,  # 0=none, 1=fleeting, 2=intense, 3=dyscrasia
        "bane": None,  # Clan bane description
        "compulsion": None,  # Current compulsion
    }

    # Blood surge tracking
    self.db.blood_surge_active = False
    self.db.blood_surge_expires = None  # Timestamp
```

**Migration**: Add utility to migrate existing characters with `db.hunger` to new structure.

---

### Task 2: Blood Utilities Module

**File**: `beckonmu/commands/v5/utils/blood_utils.py`

**Functions to Implement**:

```python
def reduce_hunger(character, amount=1):
    """Reduce character's Hunger level (from feeding)."""
    # Clamp to 0-5
    # Update character.db.vampire['hunger']
    # Return new hunger level

def increase_hunger(character, amount=1):
    """Increase character's Hunger level."""
    # Clamp to 0-5
    # Trigger warnings at Hunger 4-5
    # Return new hunger level

def get_hunger_level(character):
    """Get character's current Hunger level."""
    # Check character.db.vampire['hunger']
    # Fall back to character.db.hunger for legacy
    # Return 0-5

def set_resonance(character, resonance_type, intensity=1):
    """Set character's current resonance from feeding."""
    # Types: Choleric, Melancholic, Phlegmatic, Sanguine
    # Intensity: 1=fleeting, 2=intense, 3=dyscrasia
    # Store in character.db.vampire

def get_resonance_bonus(character, discipline):
    """Get resonance bonus dice for discipline."""
    # Choleric → Potence, Celerity
    # Melancholic → Fortitude, Obfuscate
    # Phlegmatic → Auspex, Dominate
    # Sanguine → Presence, Blood Sorcery
    # Returns +1 die if resonance matches discipline

def activate_blood_surge(character, trait_type, trait_name):
    """Activate Blood Surge to boost trait."""
    # Perform Rouse check
    # Add temporary bonus (Blood Potency dice)
    # Set expiration (one scene / 1 hour)
    # Return result dict

def deactivate_blood_surge(character):
    """End Blood Surge effect."""
    # Clear surge flags
    # Log deactivation

def get_blood_surge_bonus(character):
    """Get active Blood Surge bonus dice."""
    # Check if surge active
    # Return bonus amount (= Blood Potency)

def format_hunger_display(character):
    """Format Hunger for display (already in dice system, centralize here)."""
    # Visual: ■■■□□
    # Color-coded by severity
    # Return formatted string
```

---

### Task 3: CmdFeed Command

**File**: `beckonmu/commands/v5/blood.py`

**Command**: `feed <target> [resonance]`

**Features**:
- Roll to hunt/feed (depends on Predator Type)
- Success reduces Hunger by 1-3
- Messy Critical = Hunger reduced but complication
- Bestial Failure = frenzy risk, Humanity stain
- Track resonance from victim
- Apply resonance intensity based on roll quality

**Syntax**:
```
feed mortal                    # Hunt generic mortal
feed mortal choleric           # Hunt for specific resonance
feed mortal/slake              # Feed to Hunger 0 (risky)
feed <player>                  # Consensual feeding (diablerie risk)
```

**Dice Pool**: Varies by Predator Type
- Alleycat: Strength + Brawl
- Scene Queen: Manipulation + Subterfuge
- Sandman: Intelligence + Medicine
- etc.

**Implementation**:
```python
class CmdFeed(Command):
    """
    Feed on a mortal or willing vampire.

    Usage:
      feed <target> [<resonance>]
      feed/slake <target>

    Examples:
      feed mortal                  # Hunt generic mortal
      feed mortal choleric         # Hunt choleric resonance
      feed/slake mortal            # Feed to Hunger 0 (dangerous!)
    """

    key = "feed"
    locks = "cmd:all()"
    help_category = "Blood"

    def func(self):
        # 1. Validate target
        # 2. Determine dice pool based on Predator Type
        # 3. Roll dice (use beckonmu.dice.dice_roller)
        # 4. Resolve feeding:
        #    - Success: Reduce Hunger 1-3 (based on margin)
        #    - Messy Critical: Reduce Hunger but add complication
        #    - Bestial Failure: Frenzy risk, possible Humanity loss
        # 5. Set resonance if specified/rolled
        # 6. Display result with ANSI formatting
```

---

### Task 4: CmdBloodSurge Command

**File**: `beckonmu/commands/v5/blood.py`

**Command**: `bloodsurge <trait>`

**Features**:
- Perform Rouse check
- Add Blood Potency dice to specified trait
- Duration: One scene (1 hour) or until next roll
- Can surge Attributes or Physical Skills
- Cannot surge Disciplines (separate mechanics)

**Syntax**:
```
bloodsurge strength           # +BP dice to Strength for one scene
bloodsurge brawl              # +BP dice to Brawl
```

**Implementation**:
```python
class CmdBloodSurge(Command):
    """
    Surge your blood to temporarily enhance a trait.

    Usage:
      bloodsurge <attribute or physical skill>

    Examples:
      bloodsurge strength         # Boost Strength by Blood Potency
      bloodsurge brawl            # Boost Brawl by Blood Potency

    Blood Surge adds dice equal to your Blood Potency to the
    specified trait for one scene. Requires a Rouse check.
    """

    key = "bloodsurge"
    aliases = ["surge"]
    locks = "cmd:all()"
    help_category = "Blood"

    def func(self):
        # 1. Parse trait name
        # 2. Validate trait type (Attribute or Physical Skill only)
        # 3. Perform Rouse check (use beckonmu.dice.rouse_checker)
        # 4. Apply Blood Surge effect (store in character.db.blood_surge_active)
        # 5. Set expiration time
        # 6. Display result
```

---

### Task 5: CmdHunger Command

**File**: `beckonmu/commands/v5/blood.py`

**Command**: `hunger`

**Features**:
- Display current Hunger level
- Show visual Hunger bar (■■■□□)
- Explain Hunger effects at current level
- Show current resonance (if any)
- Show Blood Surge status (if active)

**Syntax**:
```
hunger                        # View your Hunger status
```

**Implementation**:
```python
class CmdHunger(Command):
    """
    View your current Hunger level and blood status.

    Usage:
      hunger

    Displays:
    - Current Hunger level (0-5)
    - Visual Hunger bar
    - Hunger effects
    - Current resonance (if any)
    - Blood Surge status (if active)
    """

    key = "hunger"
    locks = "cmd:all()"
    help_category = "Blood"

    def func(self):
        # 1. Get hunger level
        # 2. Format visual display with ANSI colors
        # 3. Show Hunger effects:
        #    - Hunger 0: Well-fed
        #    - Hunger 1-2: Minor cravings
        #    - Hunger 3: Moderate hunger
        #    - Hunger 4: Severe hunger
        #    - Hunger 5: Ravenous (cannot use most powers)
        # 4. Show resonance info
        # 5. Show Blood Surge status
```

---

### Task 6: Resonance System

**Resonance Types** (from V5_MECHANICS.md):

| Resonance | Associated Emotion | Bonus Disciplines |
|-----------|-------------------|-------------------|
| **Choleric** | Angry, violent | Potence, Celerity |
| **Melancholic** | Sad, depressed | Fortitude, Obfuscate |
| **Phlegmatic** | Calm, apathetic | Auspex, Dominate |
| **Sanguine** | Happy, passionate | Presence, Blood Sorcery |

**Intensity Levels**:
- **Fleeting** (1): +1 die for one roll
- **Intense** (2): +1 die for one scene
- **Dyscrasia** (3): +2 dice for one scene (rare, special feeding)

**Integration**:
- Feeding sets resonance type and intensity
- Discipline rolls check for matching resonance (via `discipline_roller.py`)
- Resonance fades after use or time

---

### Task 7: Blood Command Set

**File**: `beckonmu/commands/v5/blood_cmdset.py`

```python
from evennia import CmdSet
from .blood import CmdFeed, CmdBloodSurge, CmdHunger

class BloodCmdSet(CmdSet):
    """
    Blood system commands for vampire resource management.
    """
    key = "BloodCmdSet"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdFeed())
        self.add(CmdBloodSurge())
        self.add(CmdHunger())
```

**Integration**: Add to CharacterCmdSet in `beckonmu/commands/default_cmdsets.py`

---

### Task 8: Testing

**File**: `beckonmu/tests/v5/test_blood_utils.py`

**Test Cases**:
```python
class BloodUtilsTestCase(EvenniaTest):
    def test_reduce_hunger(self):
        """Test Hunger reduction clamps to 0-5."""

    def test_increase_hunger(self):
        """Test Hunger increase clamps to 0-5."""

    def test_set_resonance(self):
        """Test resonance setting and retrieval."""

    def test_get_resonance_bonus(self):
        """Test resonance bonus for matching disciplines."""

    def test_activate_blood_surge(self):
        """Test Blood Surge activation and Rouse check."""

    def test_blood_surge_expiration(self):
        """Test Blood Surge expires after duration."""
```

**File**: `beckonmu/tests/v5/test_blood_commands.py`

**Test Cases**:
```python
class BloodCommandsTestCase(EvenniaTest):
    def test_feed_command(self):
        """Test feeding reduces Hunger."""

    def test_feed_resonance(self):
        """Test feeding sets resonance."""

    def test_blood_surge_command(self):
        """Test Blood Surge command activates bonus."""

    def test_hunger_command(self):
        """Test Hunger display command."""
```

---

## Integration with Phase 5 (Dice System)

### Resonance Bonus in Discipline Rolls

**Modify**: `beckonmu/dice/discipline_roller.py`

Add resonance check in `roll_discipline_power()`:

```python
# After calculating base_pool:
resonance_bonus = blood_utils.get_resonance_bonus(character, power.discipline.name)
if resonance_bonus > 0:
    pool_breakdown['Resonance Bonus'] = resonance_bonus
    total_pool += resonance_bonus
```

### Blood Surge Bonus in Rolls

**Modify**: `beckonmu/dice/dice_roller.py` or create wrapper

Check for active Blood Surge when rolling traits:

```python
surge_bonus = blood_utils.get_blood_surge_bonus(character)
if surge_bonus > 0 and trait_in_surge:
    pool += surge_bonus
```

---

## Enhancement: Nightly Blood Expenditure (Optional)

**File**: `beckonmu/world/v5_scripts.py`

**Script**: NightlyRouseScript

```python
from evennia import DefaultScript
from beckonmu.dice import rouse_checker

class NightlyRouseScript(DefaultScript):
    """
    Triggers automatic Rouse checks for all characters at "sunset".

    Simulates the nightly blood expenditure as vampires wake.
    """

    def at_script_creation(self):
        self.key = "nightly_rouse_script"
        self.desc = "Nightly blood expenditure system"
        self.interval = 86400  # 24 hours (or configured sunset time)
        self.persistent = True
        self.start_delay = True

    def at_repeat(self):
        """Trigger Rouse checks for all active vampires."""
        from typeclasses.characters import Character

        for char in Character.objects.all():
            if char.db.vampire:  # Only vampires
                result = rouse_checker.perform_rouse_check(
                    char,
                    reason="Rising for the night",
                    power_level=1
                )
                # Optionally notify player if logged in
                if char.sessions.all():
                    char.msg(result['message'])
```

**Configuration**: Add to `settings.py`:
```python
# V5 Blood System Settings
NIGHTLY_ROUSE_ENABLED = True
NIGHTLY_ROUSE_TIME = "20:00"  # 8 PM server time
```

---

## File Summary

### New Files (6 files):
1. **beckonmu/commands/v5/blood.py** (~500 lines)
   - CmdFeed, CmdBloodSurge, CmdHunger

2. **beckonmu/commands/v5/blood_cmdset.py** (~20 lines)
   - BloodCmdSet

3. **beckonmu/commands/v5/utils/blood_utils.py** (~300 lines)
   - Hunger management, resonance, Blood Surge logic

4. **beckonmu/world/v5_scripts.py** (~100 lines)
   - NightlyRouseScript (optional)

5. **beckonmu/tests/v5/test_blood_utils.py** (~200 lines)
   - Unit tests for blood_utils

6. **beckonmu/tests/v5/test_blood_commands.py** (~300 lines)
   - Integration tests for commands

7. **docs/planning/PHASE_6_BLOOD_SYSTEMS_PLAN.md** (this file)

### Modified Files (3 files):
1. **beckonmu/typeclasses/characters.py**
   - Add char.db.vampire structure

2. **beckonmu/dice/discipline_roller.py**
   - Add resonance bonus check

3. **beckonmu/commands/default_cmdsets.py**
   - Add BloodCmdSet

---

## Deliverables Checklist

- [ ] `blood_utils.py` with hunger/resonance/surge logic
- [ ] `blood.py` with CmdFeed, CmdBloodSurge, CmdHunger
- [ ] `blood_cmdset.py` with BloodCmdSet
- [ ] Modify `characters.py` with vampire structure
- [ ] Integrate resonance with `discipline_roller.py`
- [ ] Write tests for blood_utils
- [ ] Write tests for blood commands
- [ ] (Optional) Implement NightlyRouseScript
- [ ] Update CHANGELOG.md
- [ ] Update SESSION_NOTES.md

---

## Testing Checklist

- [ ] Hunger increases/decreases correctly (0-5 clamp)
- [ ] Feeding reduces Hunger by appropriate amount
- [ ] Resonance tracked during feeding
- [ ] Resonance bonus applies to matching disciplines
- [ ] Blood Surge performs Rouse check
- [ ] Blood Surge adds correct bonus dice
- [ ] Blood Surge expires after duration
- [ ] Hunger command displays correctly
- [ ] Integration with existing dice system works
- [ ] No regression in Phase 5 functionality

---

## Estimated Complexity

- **Lines of Code**: ~1,400 lines total
- **New Systems**: Feeding, Blood Surge, Resonance
- **Integration Points**: Dice system, trait system, character structure
- **Complexity**: Medium
- **Estimated Time**:
  - Implementation: 6-8 hours
  - Testing: 2-3 hours
  - Integration & debugging: 2-3 hours
  - **Total**: 10-14 hours

---

## Token Efficiency Strategy

**Recommended Approach**: Use Quadrumvirate pattern

1. **Claude**: Create implementation plan (done), oversee integration
2. **Cursor/Copilot**: Implement commands and utilities (parallel tasks)
3. **Claude**: Test integration, verify mechanics
4. **Gemini**: Review for V5 mechanics accuracy (if needed)

**Parallel Tasks for Delegates**:
- Task A: Implement blood_utils.py + tests
- Task B: Implement CmdFeed + tests
- Task C: Implement CmdBloodSurge + CmdHunger + tests
- Task D: Character structure modifications

---

## Success Criteria

Phase 6 is complete when:
- ✅ Characters can feed to reduce Hunger
- ✅ Feeding tracks resonance
- ✅ Blood Surge temporarily boosts traits
- ✅ Resonance provides bonus dice to matching disciplines
- ✅ All tests pass
- ✅ Integration with Phase 5 dice system is seamless
- ✅ No regression in existing functionality

---

**Ready to implement!** Let me know if you want to:
1. Proceed with Cursor/Copilot delegation (recommended)
2. Review/adjust the plan
3. Implement incrementally (one system at a time)
