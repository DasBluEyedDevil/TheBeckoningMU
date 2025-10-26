# Evennia Commands System

## Overview

Commands are the primary user interface in Evennia games. This skill covers creating, organizing, and managing commands in TheBeckoningMU. Use this when implementing player commands, admin commands, or custom command systems.

---

## What Are Commands?

Commands are Python classes that inherit from `evennia.commands.command.Command`. They enable players to interact with the game world through text input.

**Examples**: `look`, `get`, `drop`, `say`, `inventory`, `attack`

---

## Command Structure

### Essential Class Properties

```python
from evennia import Command

class CmdExample(Command):
    """
    Example command showing all key properties.
    """
    key = "example"
    aliases = ["ex", "test"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        """Main command logic."""
        self.caller.msg("Command executed!")
```

**Property Descriptions**:
- **`key`** (str): Primary command name (e.g., "look")
- **`aliases`** (list): Alternative names (e.g., ["l", "glance"])
- **`locks`** (str): Access control (e.g., "cmd:all()" for everyone, "cmd:perm(Admin)" for admins)
- **`help_category`** (str): Organizes commands in help system (defaults to "General")

---

## Command Methods

Commands implement hook methods in a specific execution sequence:

### 1. `at_pre_cmd()` - Pre-Execution Hook

Called first, before parsing or execution. Return `True` to abort command execution.

```python
def at_pre_cmd(self):
    """Check if command can execute."""
    if self.caller.db.is_stunned:
        self.caller.msg("You cannot act while stunned!")
        return True  # Abort execution
    return False  # Continue
```

**Use Cases**:
- Check status conditions (stunned, silenced, etc.)
- Cooldown timers
- Permission checks beyond locks

### 2. `parse()` - Argument Parsing

Processes `self.args` (the raw argument string) and stores results as instance variables.

```python
def parse(self):
    """Parse command arguments."""
    # Split arguments
    args = self.args.strip().split()

    # Store parsed values
    self.target = args[0] if args else None
    self.amount = int(args[1]) if len(args) > 1 else 1
```

**Use Cases**:
- Split arguments into components
- Parse switches (see MuxCommand section)
- Validate input format
- Pre-process arguments

**Note**: Don't send messages to caller in `parse()`, only prepare data.

### 3. `func()` - Main Execution (Required)

The main command body that performs actual functionality. This is the only required method.

```python
def func(self):
    """
    Main command logic. This method is required.
    """
    if not self.args:
        self.caller.msg("Usage: example <target>")
        return

    self.caller.msg(f"You execute the command on {self.args}.")
```

**Use Cases**:
- Perform command actions
- Send messages to caller and others
- Modify game state
- Handle errors and edge cases

### 4. `at_post_cmd()` - Post-Execution Hook

Called after `func()` completes successfully. Used for cleanup or side effects.

```python
def at_post_cmd(self):
    """Clean up after command execution."""
    # Remove temporary flags
    if hasattr(self.caller.ndb, 'temp_flag'):
        del self.caller.ndb.temp_flag
```

**Use Cases**:
- Cleanup operations
- Logging
- Statistics tracking
- Trigger follow-up events

---

## Runtime Properties

Evennia automatically assigns these properties when command executes:

- **`self.caller`**: Object executing the command (usually a Character)
- **`self.session`**: Player's session (if applicable)
- **`self.cmdstring`**: The matched command name used (key or alias)
- **`self.args`**: Arguments following the command name (raw string)
- **`self.obj`**: Object the command is attached to (for object commands)

### Example Usage

```python
def func(self):
    # Get who executed command
    caller = self.caller

    # Send message to caller
    caller.msg(f"You used the '{self.cmdstring}' command.")

    # Get arguments
    target_name = self.args.strip()

    # Get caller's location
    location = caller.location

    # Message everyone in location except caller
    location.msg_contents(
        f"{caller.key} uses {self.cmdstring}!",
        exclude=caller
    )
```

---

## MuxCommand - MUX-Style Syntax

Most Evennia commands inherit from `MuxCommand`, which supports MUX-like syntax.

### MuxCommand Features

```python
from evennia import CmdSet
from evennia.commands.default.muxcommand import MuxCommand

class CmdGive(MuxCommand):
    """
    Give an item to someone.

    Usage:
      give <item> to <target>
      give/quiet <item> to <target>

    Switches:
      quiet - Don't announce the action
    """
    key = "give"
    locks = "cmd:all()"

    def parse(self):
        """Parse MUX-style syntax."""
        # Access switches
        self.quiet = "quiet" in self.switches

        # Parse "to" separator
        if " to " in self.args:
            self.item_name, self.target_name = self.args.split(" to ", 1)
        else:
            self.item_name = self.args
            self.target_name = None

    def func(self):
        if not self.item_name or not self.target_name:
            self.caller.msg("Usage: give <item> to <target>")
            return

        # Find item and target
        item = self.caller.search(self.item_name.strip(), location=self.caller)
        target = self.caller.search(self.target_name.strip())

        if not item or not target:
            return

        # Perform action
        item.location = target
        self.caller.msg(f"You give {item.key} to {target.key}.")

        if not self.quiet:
            target.msg(f"{self.caller.key} gives you {item.key}.")
```

### MuxCommand Parsed Properties

After `parse()` runs, MuxCommand provides:

- **`self.switches`** (list): Command switches (e.g., `["/quiet", "/force"]` from `cmd/quiet/force`)
- **`self.lhs`**: Left-hand side of `=` (e.g., "arg1" from `cmd arg1 = value1`)
- **`self.rhs`**: Right-hand side of `=` (e.g., "value1")
- **`self.lhslist`**: List split by commas (e.g., `["arg1", "arg2"]` from `cmd arg1, arg2 = ...`)
- **`self.rhslist`**: List split by commas

### MUX Syntax Examples

```
command                          # Simple command
command arg                      # Command with argument
command/switch                   # Command with switch
command/switch1/switch2          # Multiple switches
command arg = value              # Command with lhs/rhs
command arg1, arg2 = val1, val2  # Multiple args/values
command/switch arg = value       # Combination
```

---

## Creating Custom Commands

### Step-by-Step Process

#### 1. Create Command Class

Create command in `beckonmu/commands/` directory:

```python
# beckonmu/commands/custom.py

from evennia.commands.default.muxcommand import MuxCommand

class CmdShout(MuxCommand):
    """
    Shout a message to everyone in the area.

    Usage:
      shout <message>

    This command broadcasts a message to everyone
    in your current location and adjacent rooms.
    """

    key = "shout"
    aliases = ["yell", "scream"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        """Execute the shout."""
        if not self.args:
            self.caller.msg("Shout what?")
            return

        message = self.args.strip()
        caller_name = self.caller.key

        # Message to caller
        self.caller.msg(f'You shout, "{message}"')

        # Message to location
        self.caller.location.msg_contents(
            f'{caller_name} shouts, "{message}"',
            exclude=self.caller
        )

        # Message to adjacent rooms
        for exit in self.caller.location.exits:
            if exit.destination:
                exit.destination.msg_contents(
                    f'You hear someone shout from nearby, "{message}"'
                )
```

#### 2. Add to Command Set

Add command to appropriate command set in `beckonmu/commands/default_cmdsets.py`:

```python
# beckonmu/commands/default_cmdsets.py

from evennia import default_cmds
from commands import custom  # Import your custom commands module

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    Command set for characters.
    """
    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """Populate the cmdset."""
        super().at_cmdset_creation()

        # Add custom commands
        self.add(custom.CmdShout())
```

#### 3. Reload Server

```bash
evennia reload
```

Command is now available to all characters.

---

## Command Sets (CmdSets)

### What Are Command Sets?

Command Sets are containers for commands. They determine which commands are available to which objects.

**Key Insight**: Commands must be in a CmdSet attached to an object before they're usable.

### Default Command Sets

Located in `beckonmu/commands/default_cmdsets.py`:

- **`CharacterCmdSet`**: Commands available to characters
- **`AccountCmdSet`**: Commands available to accounts (OOC)
- **`UnloggedinCmdSet`**: Commands available before login

### Creating Custom Command Sets

```python
from evennia import CmdSet

class AdminCmdSet(CmdSet):
    """
    Command set for admin-only commands.
    """
    key = "admin_commands"
    priority = 10  # Higher priority overrides duplicates

    def at_cmdset_creation(self):
        """Populate the cmdset."""
        self.add(CmdTeleport())
        self.add(CmdInvisible())
        self.add(CmdGodMode())
```

### Adding CmdSets to Objects

**Permanent** (on creation):
```python
# In typeclass's at_object_creation()
from commands.admin import AdminCmdSet

def at_object_creation(self):
    self.cmdset.add(AdminCmdSet, persistent=True)
```

**Temporary** (until reload):
```python
# Add cmdset temporarily
character.cmdset.add(AdminCmdSet)

# Remove cmdset
character.cmdset.remove(AdminCmdSet)
```

**In-game**:
```
@cmdset/add Character = commands.admin.AdminCmdSet
```

### CmdSet Priority

When multiple cmdsets contain commands with the same key, priority determines which executes.

```python
class HighPriorityCmdSet(CmdSet):
    priority = 100  # Higher number = higher priority
```

---

## Advanced Command Features

### Dynamic Pauses (Async)

Commands can pause execution without blocking the server:

```python
from evennia import Command

class CmdCast(Command):
    """
    Cast a spell with casting time.
    """
    key = "cast"

    def func(self):
        self.caller.msg("You begin casting...")

        # Pause for 3 seconds
        yield 3

        self.caller.msg("The spell is complete!")
        # Execute spell effects
```

### User Input During Execution

Request input from user mid-command:

```python
class CmdConfirm(Command):
    """
    Command that asks for confirmation.
    """
    key = "dangerous"

    def func(self):
        self.caller.msg("This is a dangerous action!")

        # Ask for confirmation
        answer = yield("Are you sure? (yes/no)")

        if answer.lower() == "yes":
            self.caller.msg("Proceeding with dangerous action...")
            # Do dangerous thing
        else:
            self.caller.msg("Action cancelled.")
```

### Command State Persistence

Command instances are cached and reused, enabling state persistence:

```python
class CmdMultiStep(Command):
    """
    Multi-step command that remembers state.
    """
    key = "multistep"

    def func(self):
        # Access persistent state (survives until reload)
        if not hasattr(self, 'step'):
            self.step = 1

        if self.step == 1:
            self.caller.msg("Step 1 complete.")
            self.step = 2
        elif self.step == 2:
            self.caller.msg("Step 2 complete.")
            self.step = 1  # Reset
```

---

## Common Command Patterns

### Pattern: Search and Target

```python
class CmdAttack(MuxCommand):
    """Attack a target."""
    key = "attack"
    aliases = ["hit", "strike"]

    def func(self):
        if not self.args:
            self.caller.msg("Attack whom?")
            return

        # Search for target in location
        target = self.caller.search(
            self.args.strip(),
            location=self.caller.location
        )

        if not target:
            return  # search() already sent error message

        if target == self.caller:
            self.caller.msg("You cannot attack yourself!")
            return

        # Perform attack
        self.caller.msg(f"You attack {target.key}!")
        target.msg(f"{self.caller.key} attacks you!")
```

### Pattern: Admin Command with Permissions

```python
class CmdTeleport(MuxCommand):
    """
    Teleport to a location.

    Usage:
      teleport <location>
    """
    key = "@teleport"
    aliases = ["@tel"]
    locks = "cmd:perm(Builder)"  # Only for Builders and higher
    help_category = "Admin"

    def func(self):
        if not self.args:
            self.caller.msg("Teleport where?")
            return

        # Search for location
        location = self.caller.search(self.args, global_search=True)

        if not location:
            return

        # Move caller
        old_location = self.caller.location
        self.caller.move_to(location)

        self.caller.msg(f"Teleported from {old_location.key} to {location.key}.")
```

### Pattern: Object Manipulation

```python
class CmdEnchant(MuxCommand):
    """
    Enchant an item.

    Usage:
      enchant <item> = <property>, <value>
    """
    key = "enchant"
    locks = "cmd:holds(magic_wand)"  # Must hold magic wand

    def func(self):
        if not self.lhs or not self.rhslist:
            self.caller.msg("Usage: enchant <item> = <property>, <value>")
            return

        # Find item in inventory
        item = self.caller.search(self.lhs, location=self.caller)
        if not item:
            return

        # Parse property and value
        prop = self.rhslist[0].strip()
        value = self.rhslist[1].strip() if len(self.rhslist) > 1 else ""

        # Enchant item
        item.db.enchantments = item.db.enchantments or {}
        item.db.enchantments[prop] = value

        self.caller.msg(f"You enchant {item.key} with {prop} = {value}.")
```

### Pattern: Information Display

```python
class CmdStats(MuxCommand):
    """
    Display your character statistics.

    Usage:
      stats
      stats <character>
    """
    key = "stats"
    aliases = ["score", "sheet"]

    def func(self):
        # Target is self or specified character
        if self.args:
            target = self.caller.search(self.args)
            if not target:
                return
        else:
            target = self.caller

        # Build stats display
        stats = target.db.stats or {}

        output = f"|wCharacter Stats: {target.key}|n\n"
        output += "-" * 40 + "\n"
        output += f"Health: {target.db.health}/{target.get_max_health()}\n"
        output += f"Level: {target.db.level}\n"
        output += "\n|wAttributes:|n\n"

        for stat, value in stats.items():
            output += f"  {stat.capitalize()}: {value}\n"

        self.caller.msg(output)
```

### Pattern: Toggle Command

```python
class CmdToggleCombat(MuxCommand):
    """
    Toggle combat mode on/off.

    Usage:
      combat
    """
    key = "combat"

    def func(self):
        # Toggle combat mode
        current_mode = self.caller.db.combat_mode or False
        self.caller.db.combat_mode = not current_mode

        if self.caller.db.combat_mode:
            self.caller.msg("|rCombat mode ENABLED.|n")
            # Enable combat cmdset
            from commands.combat import CombatCmdSet
            self.caller.cmdset.add(CombatCmdSet)
        else:
            self.caller.msg("|gCombat mode DISABLED.|n")
            # Remove combat cmdset
            from commands.combat import CombatCmdSet
            self.caller.cmdset.remove(CombatCmdSet)
```

---

## Command Organization

### Recommended Directory Structure

```
beckonmu/commands/
├── __init__.py
├── command.py              # Base command class
├── default_cmdsets.py      # Default cmdsets
├── custom.py               # General custom commands
├── communication.py        # Say, shout, whisper, etc.
├── combat.py               # Combat commands
├── admin.py                # Admin commands
├── building.py             # Builder commands
└── tests.py                # Command tests
```

### Organizing by Category

Create modules for related commands:

```python
# beckonmu/commands/communication.py

class CmdSay(MuxCommand):
    key = "say"
    # ...

class CmdWhisper(MuxCommand):
    key = "whisper"
    # ...

class CmdShout(MuxCommand):
    key = "shout"
    # ...
```

Then import in cmdsets:

```python
# beckonmu/commands/default_cmdsets.py

from commands import communication

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(communication.CmdSay())
        self.add(communication.CmdWhisper())
        self.add(communication.CmdShout())
```

---

## Testing Commands

### Using EvenniaTest

```python
# beckonmu/commands/tests.py

from evennia.utils.test_resources import EvenniaTest
from commands.custom import CmdShout

class TestCmdShout(EvenniaTest):
    """Test the shout command."""

    def test_shout_no_args(self):
        """Test shout without arguments."""
        self.call(CmdShout(), "", "Shout what?")

    def test_shout_with_message(self):
        """Test shout with message."""
        self.call(
            CmdShout(),
            "Hello everyone!",
            'You shout, "Hello everyone!"'
        )
```

### Running Command Tests

```bash
evennia test beckonmu.commands.tests
```

---

## Troubleshooting

### Issue: Command Not Found

**Causes**:
- Command not added to cmdset
- Cmdset not attached to character
- Name collision with higher priority command

**Solutions**:
1. Check cmdset includes command
2. Verify cmdset attached: `examine self/cmdsets`
3. Check command priority

### Issue: Command Not Executing

**Causes**:
- Lock preventing execution
- Error in `at_pre_cmd()` returning True
- Exception in `func()`

**Solutions**:
1. Check locks: `cmd:all()` vs `cmd:perm(Admin)`
2. Check server logs for errors
3. Add debug messages to narrow down issue

### Issue: Arguments Not Parsing

**Causes**:
- `parse()` method has errors
- MuxCommand syntax not understood

**Solutions**:
1. Debug `parse()` with print statements
2. Check MuxCommand documentation
3. Test with simple arguments first

---

## Best Practices

### 1. Always Validate Input

```python
def func(self):
    if not self.args:
        self.caller.msg("Usage: command <argument>")
        return

    # Continue with validated input
```

### 2. Use search() for Finding Objects

```python
# Let Evennia handle search errors
target = self.caller.search(self.args)
if not target:
    return  # search() already sent error message
```

### 3. Provide Clear Feedback

```python
# Good: Clear, informative messages
self.caller.msg("|gYou successfully cast the spell!|n")
target.msg(f"|r{self.caller.key} casts a spell on you!|n")

# Bad: Vague or no feedback
self.caller.msg("Done.")
```

### 4. Handle Edge Cases

```python
def func(self):
    # Can't target self
    if target == self.caller:
        self.caller.msg("You cannot target yourself!")
        return

    # Can't use if stunned
    if self.caller.db.stunned:
        self.caller.msg("You are stunned!")
        return

    # Must be in same location
    if target.location != self.caller.location:
        self.caller.msg("They are not here!")
        return
```

### 5. Use Locks for Permissions

```python
# Instead of checking in func()
class CmdAdminTool(Command):
    key = "admintool"
    locks = "cmd:perm(Admin)"  # Lock handles permission

    def func(self):
        # No need to check permissions here
        pass
```

### 6. Document Commands Well

```python
class CmdExample(MuxCommand):
    """
    Short description of command.

    Usage:
      example <arg>
      example/switch <arg>

    Longer description explaining what the command
    does, any special behavior, and examples.

    Examples:
      example test
      example/quiet test

    Switches:
      quiet - Don't announce action
    """
```

---

## Summary

**Key Concepts**:
- Commands = Python classes inheriting from `Command` or `MuxCommand`
- Must be in a CmdSet attached to an object
- Execution sequence: `at_pre_cmd()` → `parse()` → `func()` → `at_post_cmd()`
- MuxCommand supports switches and `=` syntax

**Common Properties**:
- `self.caller`: Who executed command
- `self.args`: Raw argument string
- `self.switches`: List of switches (MuxCommand)
- `self.lhs` / `self.rhs`: Left/right of `=` (MuxCommand)

**Best Practices**:
- Validate input
- Use `search()` for finding objects
- Provide clear feedback
- Handle edge cases
- Use locks for permissions
- Document thoroughly

**Command Workflow**:
1. Create command class
2. Add to cmdset
3. Attach cmdset to character/object
4. Reload server
5. Test command
