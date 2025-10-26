# Evennia Typeclasses - Deep Dive

## Overview

This skill provides comprehensive guidance on creating, modifying, and working with Evennia typeclasses. Use this when implementing game entities, customizing behavior, or working with the typeclass system.

---

## What Are Typeclasses?

Typeclasses are **Django proxy models** that enable representing diverse game entities as Python classes without modifying the database schema. They form Evennia's foundational data storage system.

**Key Insight**: Only four "real" database models exist (`ObjectDB`, `AccountDB`, `ScriptDB`, `ChannelDB`). All other typeclasses are proxies extending functionality through Python code without altering database structure.

---

## Three-Level Inheritance Hierarchy

### Level 1: Database Models (The Foundation)
- `ObjectDB` - Base for all in-world objects
- `AccountDB` - Player account data
- `ScriptDB` - Automated processes
- `ChannelDB` - Communication channels

**These are the ONLY real database tables.**

### Level 2: Evennia Defaults (Built-in Implementations)
- `DefaultObject` - Evennia's default object implementation
- `DefaultCharacter` - Default character (inherits from `DefaultObject`)
- `DefaultRoom` - Default room
- `DefaultExit` - Default exit
- `DefaultAccount` - Default account
- `DefaultScript` - Default script
- `DefaultChannel` - Default channel

**These provide hook methods and standard functionality.**

### Level 3: Game Directory (Your Custom Classes)
Located in `beckonmu/typeclasses/`:
- `Object` (your base) → inherits from → `ObjectParent` + `DefaultObject`
- `Character` → inherits from → `ObjectParent` + `DefaultCharacter`
- `Room` → inherits from → `ObjectParent` + `DefaultRoom`
- `Exit` → inherits from → `ObjectParent` + `DefaultExit`

**This is where you implement game-specific behavior.**

---

## Core Typeclass Types

### Objects (Base for Physical Entities)
**Location**: `beckonmu/typeclasses/objects.py`

**Purpose**: Base class for all in-game items.

**Key Features**:
- Has a location in the game world
- Can be picked up, dropped, examined
- Parent for Characters, Exits, and other physical entities

**Example skeleton**:
```python
from evennia import DefaultObject
from .objects import ObjectParent

class Object(ObjectParent, DefaultObject):
    """
    Base typeclass for all objects in TheBeckoningMU.
    """
    pass
```

### Characters (Player-Controlled Entities)
**Location**: `beckonmu/typeclasses/characters.py`

**Purpose**: Represents player characters and NPCs.

**Inherits from**: Objects (so has all Object functionality)

**Key Features**:
- Can be puppeted by Accounts
- Has additional character-specific hooks
- Typically has inventory, stats, skills

**Example**:
```python
from evennia import DefaultCharacter
from .objects import ObjectParent

class Character(ObjectParent, DefaultCharacter):
    """
    Character typeclass for TheBeckoningMU.
    """
    def at_object_creation(self):
        """Called when character is first created."""
        self.db.health = 100
        self.db.mana = 50
```

### Rooms (Locations)
**Location**: `beckonmu/typeclasses/rooms.py`

**Purpose**: Locations in the game world.

**Key Features**:
- Container for objects and characters
- Defines environment and atmosphere
- Connected by Exits

**Example**:
```python
from evennia import DefaultRoom
from .objects import ObjectParent

class Room(ObjectParent, DefaultRoom):
    """
    Room typeclass for TheBeckoningMU.
    """
    def return_appearance(self, looker, **kwargs):
        """Customize how room appears to looker."""
        text = super().return_appearance(looker, **kwargs)
        # Add custom formatting
        return text
```

### Exits (Connections Between Rooms)
**Location**: `beckonmu/typeclasses/exits.py`

**Purpose**: Connections between locations.

**Key Features**:
- Links two rooms (source and destination)
- Can have custom traversal logic
- Can be locked/hidden

**Example**:
```python
from evennia import DefaultExit
from .objects import ObjectParent

class Exit(ObjectParent, DefaultExit):
    """
    Exit typeclass for TheBeckoningMU.
    """
    def at_traverse(self, traversing_object, target_location):
        """Called when exit is used."""
        # Add custom traversal logic
        super().at_traverse(traversing_object, target_location)
```

### Accounts (Player Accounts - OOC)
**Location**: `beckonmu/typeclasses/accounts.py`

**Purpose**: Out-of-character player accounts.

**Key Features**:
- Represents the player (not the character)
- Handles login/logout
- Can puppet multiple characters

**Example**:
```python
from evennia import DefaultAccount

class Account(DefaultAccount):
    """
    Account typeclass for TheBeckoningMU.
    """
    def at_post_login(self, session=None, **kwargs):
        """Called after successful login."""
        super().at_post_login(session, **kwargs)
        # Custom login logic
```

### Scripts (Automated Processes)
**Location**: `beckonmu/typeclasses/scripts.py`

**Purpose**: Time-based or persistent game logic.

**Key Features**:
- Can run on timers (repeating or one-time)
- Global or attached to objects
- Survives server reloads

**Example**:
```python
from evennia import DefaultScript

class Script(DefaultScript):
    """
    Script typeclass for TheBeckoningMU.
    """
    def at_script_creation(self):
        self.key = "weather_system"
        self.interval = 3600  # Run every hour
        self.persistent = True

    def at_repeat(self):
        """Called every interval."""
        # Update weather
        pass
```

### Channels (Communication)
**Location**: `beckonmu/typeclasses/channels.py`

**Purpose**: In-game communication channels.

**Example**: Public chat, guild channels, admin channels.

---

## ObjectParent Mixin Pattern (TheBeckoningMU-Specific)

### What Is ObjectParent?

**Location**: `beckonmu/typeclasses/objects.py`

**Purpose**: A mixin class used to override behavior for ALL entities inheriting from `DefaultObject` (Objects, Characters, Rooms, Exits).

**Key Insight**: Because Characters, Rooms, and Exits all ultimately inherit from Objects, adding methods to `ObjectParent` affects ALL of them.

### When to Use ObjectParent

Use `ObjectParent` when you want to:
- Add functionality to all game entities with a location
- Override default Evennia behavior globally
- Implement project-wide patterns

### Example ObjectParent Usage

```python
# In typeclasses/objects.py

class ObjectParent:
    """
    Mixin parent for all Objects, Characters, Rooms, Exits.
    """

    def get_display_name(self, looker, **kwargs):
        """
        Customize name display for ALL game entities.
        """
        if self.locks.check_lockstring(looker, "perm(Admin)"):
            return f"[#{self.id}] {self.key}"
        return self.key

    def announce_move_from(self, destination, msg=None, mapping=None, **kwargs):
        """
        Custom movement announcements for ALL entities.
        """
        if not msg:
            msg = f"{self.key} leaves."
        super().announce_move_from(destination, msg, mapping, **kwargs)
```

**Result**: ALL Objects, Characters, Rooms, and Exits now have this behavior.

---

## Typeclass Constraints and Best Practices

### Three Critical Constraints

1. **Database Integration**: Some properties are database fields accepting only specific data types. Don't try to store arbitrary Python objects in DB fields—use Attributes instead.

2. **Unique Naming**: Class names must be globally unique across the entire server to avoid conflicts.

3. **Initialization Restrictions**: **DO NOT override `__init__`**. Use hooks instead:
   - `at_object_creation()`: For initial setup (called once)
   - `at_init()`: For cached-load operations (called on reload)

### Why You Can't Override `__init__`

Evennia's idmapper system manages typeclass instantiation. Overriding `__init__` breaks this system. Always use hooks.

**❌ Wrong**:
```python
class MyObject(DefaultObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_attribute = 10  # DON'T DO THIS
```

**✅ Correct**:
```python
class MyObject(DefaultObject):
    def at_object_creation(self):
        """Called once when object is first created."""
        self.db.custom_attribute = 10  # Store in database

    def at_init(self):
        """Called when object loads from cache."""
        self.ndb.temporary_cache = {}  # Non-persistent setup
```

---

## Creating Typeclass Instances

### Always Use Creation Functions

**Never** instantiate typeclasses directly. Use Evennia's creation functions.

**✅ Correct**:
```python
from evennia import create_object

# Create an object
chair = create_object(
    "typeclasses.objects.Furniture",
    key="Chair",
    location=room,
    attributes=[("material", "wood"), ("weight", 20)]
)

# Create a character
from evennia import create_account
account = create_account("PlayerName", "email@example.com", "password")
character = account.create_character(
    key="CharName",
    typeclass="typeclasses.characters.Character"
)
```

**❌ Wrong**:
```python
chair = Furniture()  # DON'T DO THIS
```

### Creation Function Parameters

Common parameters:
- `typeclass`: String path or class reference
- `key`: Object's name/identifier
- `location`: Where object is created
- `home`: Object's home location
- `attributes`: List of tuples `[(key, value), ...]`
- `locks`: Lock string
- `permissions`: List of permissions
- `tags`: List of tags

---

## Working with Attributes

### Persistent Attributes (`.db`)

Use for data that must survive server reloads.

```python
# Setting attributes
obj.db.health = 100
obj.db.inventory = ["sword", "shield"]
obj.db.settings = {"volume": 50, "theme": "dark"}

# Getting attributes
health = obj.db.health
if not obj.db.initialized:
    obj.db.initialized = True

# Advanced attribute usage with categories
obj.attributes.add("skill_swords", 5, category="skills")
obj.attributes.add("skill_magic", 3, category="skills")

# Get all attributes in category
skills = obj.attributes.get(category="skills")
```

### Non-Persistent Attributes (`.ndb`)

Use for temporary data, caches, or runtime-only storage.

```python
# No database overhead
obj.ndb.combat_target = enemy
obj.ndb.casting_spell = True
obj.ndb.temporary_cache = {}

# Cleared on server reload
```

### Performance Considerations

**Myth**: "Database access is slow."

**Reality**: Evennia aggressively caches attributes. Reading from cached attributes is as fast as reading any Python property.

**Best Practice**: Use `.db` for persistence, `.ndb` for temporary data. Don't prematurely optimize by avoiding `.db`.

---

## Hooks Deep Dive

### What Are Hooks?

Hooks are methods Evennia calls automatically at specific times. You override them to customize behavior.

### Object Lifecycle Hooks

**`at_object_creation()`**:
- Called **once** when object is first created
- Use for initializing attributes, setting defaults
- **Best Practice**: Put all default attributes here for easy updates

```python
def at_object_creation(self):
    """Initialize object with defaults."""
    self.db.health = 100
    self.db.mana = 50
    self.db.level = 1
```

**`at_init()`**:
- Called when object loads from cache (on server reload)
- Use for setting up non-persistent data
- **Not** called on first creation

```python
def at_init(self):
    """Set up runtime data."""
    self.ndb.combat_handler = CombatHandler(self)
    self.ndb.active_spells = []
```

**`at_object_delete()`**:
- Called before object is deleted
- Use for cleanup (remove references, notify other objects)

```python
def at_object_delete(self):
    """Clean up before deletion."""
    if self.db.owner:
        self.db.owner.msg(f"{self.key} has been destroyed.")
    return super().at_object_delete()
```

### Movement Hooks

**`at_pre_move(destination, **kwargs)`**:
- Called before object moves
- Return `False` to abort movement

```python
def at_pre_move(self, destination, **kwargs):
    """Check if movement is allowed."""
    if self.db.is_stunned:
        self.msg("You cannot move while stunned!")
        return False
    return True
```

**`announce_move_from(destination, msg=None, **kwargs)`**:
- Announce departure to current location

```python
def announce_move_from(self, destination, msg=None, **kwargs):
    """Customize departure message."""
    if not msg:
        msg = f"{self.key} strides confidently towards {destination.key}."
    super().announce_move_from(destination, msg, **kwargs)
```

**`announce_move_to(source_location, msg=None, **kwargs)`**:
- Announce arrival at new location

**`at_post_move(source_location, **kwargs)`**:
- Called after successful move
- Use for side effects (trigger traps, update status)

```python
def at_post_move(self, source_location, **kwargs):
    """Handle arrival effects."""
    super().at_post_move(source_location, **kwargs)
    if self.location.tags.get("trap"):
        self.location.trigger_trap(self)
```

### Display/Appearance Hooks

**`return_appearance(looker, **kwargs)`**:
- Main hook for visual description
- Returns string shown when looker examines object

```python
def return_appearance(self, looker, **kwargs):
    """Customize appearance."""
    text = super().return_appearance(looker, **kwargs)
    if self.db.health < 30:
        text += "\n|rThey appear badly wounded.|n"
    return text
```

**`get_display_name(looker, **kwargs)`**:
- Returns object's name as shown to looker
- Use for colored names, titles, disguises

```python
def get_display_name(self, looker, **kwargs):
    """Show name with color based on relationship."""
    name = self.key
    if looker.db.allies and self in looker.db.allies:
        return f"|g{name}|n"  # Green for allies
    elif looker.db.enemies and self in looker.db.enemies:
        return f"|r{name}|n"  # Red for enemies
    return name
```

**`get_display_desc(looker, **kwargs)`**: Returns description
**`get_display_header(looker, **kwargs)`**: Custom header
**`get_display_footer(looker, **kwargs)`**: Custom footer
**`format_appearance(string, looker, **kwargs)`**: Final formatting

### Puppeting Hooks (Characters/Accounts)

**`at_pre_puppet(account, session, **kwargs)`**:
- Before account puppets character
- Return `False` to prevent puppeting

**`at_post_puppet(**kwargs)`**:
- After puppeting begins
- Use to show character status, location description

```python
def at_post_puppet(self, **kwargs):
    """Show info after login."""
    super().at_post_puppet(**kwargs)
    self.msg(f"Welcome back, {self.key}!")
    self.execute_cmd("look")
```

**`at_pre_unpuppet(**kwargs)`**: Before unpuppeting
**`at_post_unpuppet(account, session, **kwargs)`**: After unpuppeting

### Interaction Hooks

**`at_traverse(traversing_object, target_location, **kwargs)`** (Exits):
- Called when exit is used

**`at_get(getter, **kwargs)`** (Objects):
- Called when object is picked up

**`at_drop(dropper, **kwargs)`** (Objects):
- Called when object is dropped

**`at_say(speaker, message, **kwargs)`** (Characters/Rooms):
- Called during speech

### Server Event Hooks

**`at_server_reload(**kwargs)`**:
- Called on server reload

**`at_server_shutdown(**kwargs)`**:
- Called on server shutdown

### Hook Reference

For complete list: See `evennia.objects.objects` in codebase or Evennia API docs.

---

## Querying Typeclasses

### Direct Queries (Only Direct Subclasses)

```python
# Find specific object
chair = Furniture.objects.get(db_key="Chair")

# Filter objects
all_furniture = Furniture.objects.filter(db_location=room)
```

**Limitation**: Only finds direct instances of `Furniture`, not subclasses.

### Family Queries (Include Subclasses)

```python
# Finds Furniture and all subclasses
matches = Furniture.objects.filter_family(db_key__startswith="Chair")
```

### Model-Level Queries (All Typeclasses of Base Type)

```python
from evennia import ObjectDB, ScriptDB

# Find all Objects regardless of typeclass
all_objects = ObjectDB.objects.filter(db_location=room)

# Find all Scripts
all_scripts = ScriptDB.objects.filter(db_key__contains="Combat")
```

### Search Functions

```python
from evennia import search_object, search_account

# Search for objects by key
results = search_object("Chair")

# Search with typeclass filter
results = search_object("Chair", typeclass="typeclasses.objects.Furniture")

# Search in specific location
results = search_object("Chair", location=room)
```

---

## Updating Existing Typeclass Instances

### Automatic Code Updates

When you change typeclass **code**, changes apply automatically on server reload.

### Manual Attribute Updates

When you add **new attributes** or change **data structure**, existing objects need manual updates.

**In-game command** (single object):
```
@py self.at_object_creation()
```

**Python shell** (all objects of type):
```python
from typeclasses.characters import Character

for char in Character.objects.all():
    if not hasattr(char.db, 'new_attribute'):
        char.at_object_creation()  # Re-run initialization
```

**Script for complex updates**:
```python
def update_all_characters():
    """Update all characters to new structure."""
    from typeclasses.characters import Character

    for char in Character.objects.all():
        # Migrate old attribute structure to new
        if char.db.old_stats:
            char.db.health = char.db.old_stats.get('hp', 100)
            char.db.mana = char.db.old_stats.get('mp', 50)
            del char.db.old_stats

        # Add new attributes
        if not char.db.experience:
            char.db.experience = 0
```

**Best Practice**: Keep initialization logic in `at_object_creation()` for consistent updates.

---

## Swapping Typeclasses

### Why Swap?

Change an object's typeclass without recreating it (preserves DB id and references).

### In-Game Command

```
@typeclass <object> = path.to.NewTypeclass
```

**Useful switches**:
- `/reset`: Purges all attributes and reruns `at_object_creation()`
- `/force`: Required when swapping to the same typeclass (for re-initialization)

### Programmatically

```python
obj.swap_typeclass(
    "typeclasses.objects.NewTypeclass",
    clean_attributes=True,  # Remove old attributes
    run_start_hooks=True    # Run at_object_creation
)
```

### Example Use Cases

1. **Upgrading NPCs**: Transform basic NPC to boss NPC
2. **Item evolution**: Transform basic sword to magic sword
3. **Room changes**: Transform safe room to combat room
4. **Testing**: Quickly test different typeclass implementations

---

## Advanced Patterns

### Custom Typeclass Families

```python
# Base furniture class
class Furniture(Object):
    """Base for all furniture."""
    def at_object_creation(self):
        self.db.weight = 10
        self.locks.add("get:false()")  # Can't be picked up

# Specific furniture types
class Chair(Furniture):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.seats = 1
        self.db.occupied = False

class Table(Furniture):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.surface_items = []
```

### Mixins for Shared Functionality

```python
class CombatantMixin:
    """Mixin for anything that can fight."""
    def take_damage(self, amount, attacker=None):
        self.db.health -= amount
        if self.db.health <= 0:
            self.die(attacker)

    def die(self, killer=None):
        self.location.msg_contents(f"{self.key} has died!")
        self.delete()

class Monster(CombatantMixin, Character):
    """Monster that can fight."""
    def at_object_creation(self):
        super().at_object_creation()
        self.db.health = 200
        self.db.attack_power = 15
```

### Typeclass Registry Pattern

```python
# Global registry of typeclass paths
TYPECLASS_PATHS = {
    "basic_sword": "typeclasses.objects.weapons.BasicSword",
    "magic_sword": "typeclasses.objects.weapons.MagicSword",
    "goblin": "typeclasses.characters.monsters.Goblin",
}

# Easy creation
def spawn_by_name(name, location):
    typeclass = TYPECLASS_PATHS.get(name)
    if typeclass:
        return create_object(typeclass, key=name, location=location)
```

---

## Common Patterns and Recipes

### Pattern: Stat System

```python
class Character(ObjectParent, DefaultCharacter):
    def at_object_creation(self):
        self.db.stats = {
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
        }
        self.db.health = self.get_max_health()

    def get_max_health(self):
        return self.db.stats["strength"] * 10

    def get_stat(self, stat_name):
        return self.db.stats.get(stat_name, 10)

    def modify_stat(self, stat_name, amount):
        if stat_name in self.db.stats:
            self.db.stats[stat_name] += amount
```

### Pattern: Inventory Management

```python
class Character(ObjectParent, DefaultCharacter):
    def add_to_inventory(self, obj):
        obj.location = self
        self.msg(f"You pick up {obj.key}.")

    def remove_from_inventory(self, obj):
        if obj.location == self:
            obj.location = self.location
            self.msg(f"You drop {obj.key}.")

    def get_inventory(self):
        return [obj for obj in self.contents if not obj.has_account]
```

### Pattern: Custom Room Behavior

```python
class DangerousRoom(Room):
    """Room that damages characters over time."""
    def at_object_creation(self):
        super().at_object_creation()
        self.db.damage_per_tick = 5
        # Create script for periodic damage
        from evennia import create_script
        create_script(
            "typeclasses.scripts.RoomDamage",
            obj=self,
            interval=60,  # Every minute
            autostart=True
        )
```

---

## Troubleshooting

### Issue: Changes Not Applying

**Cause**: Server not reloaded or changes in database data.

**Solution**:
1. Run `evennia reload`
2. If still not working, manually update: `obj.at_object_creation()`

### Issue: Can't Create Object

**Cause**: Typeclass path wrong or initialization error.

**Solution**:
1. Check typeclass path string
2. Check `at_object_creation()` for errors
3. Look at server logs: `evennia -l`

### Issue: Attribute Not Persisting

**Cause**: Using `.ndb` instead of `.db`.

**Solution**: Use `.db` for persistent data:
```python
self.db.health = 100  # ✅ Persists
self.ndb.health = 100  # ❌ Lost on reload
```

### Issue: Import Errors

**Cause**: Circular imports or missing `__init__.py`.

**Solution**:
1. Add `__init__.py` to directories
2. Use lazy imports in methods instead of module level
3. Check import paths

---

## Summary

**Key Concepts**:
- Typeclasses = Django proxy models
- Three levels: DB models → Defaults → Custom
- Use creation functions, never direct instantiation
- Don't override `__init__`, use hooks
- ObjectParent affects ALL game entities

**Best Practices**:
- Put defaults in `at_object_creation()`
- Use `.db` for persistent, `.ndb` for temporary
- Override hooks, don't add new lifecycle methods
- Use mixins for shared functionality
- Query with family methods when needed

**Common Hooks**:
- `at_object_creation()`: Initialize new objects
- `at_init()`: Set up non-persistent data
- `return_appearance()`: Customize display
- `at_pre_move()` / `at_post_move()`: Handle movement
- `at_post_puppet()`: Character login actions
