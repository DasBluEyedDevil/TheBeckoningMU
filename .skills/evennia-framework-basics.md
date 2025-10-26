# Evennia Framework Basics

## Overview

Evennia is a Python framework for building MUDs (Multi-User Dungeons) and multiplayer text-based games. This skill covers core Evennia concepts and architecture for TheBeckoningMU project.

---

## System Requirements

- **Python Version**: 3.10, 3.11, or 3.12 (TheBeckoningMU uses 3.13+)
- **Virtual Environment**: Use lightweight virtualenv (`.venv` directory)
- **Package Management**: Poetry (`poetry.toml`, `pyproject.toml`)
- **Database**: SQLite3 (default) or configurable alternatives

**Warning**: Never install Evennia as administrator/superuser.

---

## Core Architecture

### The Typeclass System

Evennia uses a **typeclass pattern** for game entities. Typeclasses are Django proxy models that allow representing diverse game objects as Python classes without modifying database schema.

**Three-Level Inheritance Hierarchy**:
1. **Database Models** (Level 1): `ObjectDB`, `AccountDB`, `ScriptDB`, `ChannelDB` - Django models representing database tables
2. **Defaults** (Level 2): `DefaultObject`, `DefaultAccount`, `DefaultScript`, `DefaultChannel` - Evennia's implementations with hook methods
3. **Game Directory** (Level 3): Your custom classes inheriting from Level 2 defaults

**Key Insight**: All typeclasses are proxies to the four base DB classes. Only those four represent actual database tables.

### Main Typeclass Types

All entities with a location inherit from `DefaultObject` at some level:

- **Objects** (`typeclasses/objects.py`): Base class for all in-game items
- **Characters** (`typeclasses/characters.py`): Player-controlled entities (inherit from Objects)
- **Rooms** (`typeclasses/rooms.py`): Locations in the game world
- **Exits** (`typeclasses/exits.py`): Connections between rooms

Other core typeclasses:
- **Accounts** (`typeclasses/accounts.py`): Player accounts (OOC entities)
- **Scripts** (`typeclasses/scripts.py`): Time-based or persistent game logic
- **Channels** (`typeclasses/channels.py`): Communication channels

### ObjectParent Mixin Pattern

**TheBeckoningMU-Specific**: The `ObjectParent` class in `typeclasses/objects.py` is a mixin used to override behavior for ALL entities inheriting from `DefaultObject` (Objects, Exits, Characters, Rooms).

**Usage**: Add methods to `ObjectParent` to affect all game entities with a location.

---

## Database and Persistence

### Attribute Systems

Evennia provides two attribute systems for storing data on objects:

**Persistent Attributes (`self.db.*`)**:
- Stored in database
- Survive server reloads/reboots
- Use for long-term game state
- Cached aggressively for performance
```python
obj.db.foo = [1, 2, 3, "bar"]
obj.attributes.add("myattr", 1234, category="bar")
```

**Non-Persistent Attributes (`self.ndb.*`)**:
- Memory-only storage
- Cleared on server reload
- Use for temporary/throwaway data
- No database overhead
- No serialization limits
```python
obj.ndb.temporary_data = True
obj.nattributes.add("cache", some_value)
```

**Performance Note**: Database concerns are typically overblown. Reading from cached Attributes is as fast as reading any Python property due to Evennia's aggressive caching.

**Best Practice**: Mix both strategically—`.db` for persistence, `.ndb` for temporary data. Clean code style makes data lifespan clear.

### Universal Fields (All Typeclasses)

- `key` (str): Main identifier (use this, not `db_key`)
- `date_created` (datetime): Creation timestamp
- `typeclass_path` (str): Python path to the class
- `id` / `dbid` / `pk` / `dbref` (int): Unique database identifier

**Database Fields vs Properties**: Fields have `db_` prefixes (e.g., `db_key`), but use wrapper properties without prefixes (e.g., `key`) as they handle saving automatically.

### Common Handlers (All Typeclasses)

- `tags` - TagHandler for categorization
- `locks` - LockHandler for access control
- `attributes` / `db` - Persistent AttributeHandler
- `nattributes` / `ndb` - Non-persistent AttributeHandler

---

## Hooks System

Hooks are methods Evennia calls automatically at specific times. Override these in your typeclasses to customize behavior.

**Object Lifecycle Hooks**:
- `at_object_creation()`: Called once when object is first created
- `at_object_delete()`: Called before object is deleted
- `at_init()`: Called when object is loaded from cache

**Display/Appearance Hooks**:
- `return_appearance(looker, **kwargs)`: Main hook for visual description
- `get_display_name(looker, **kwargs)`: Returns object's name
- `get_display_desc(looker, **kwargs)`: Returns object description
- `get_display_header(looker, **kwargs)`: Custom header content
- `get_display_footer(looker, **kwargs)`: Custom footer content
- `format_appearance(string, looker, **kwargs)`: Final formatting adjustments

**Movement Hooks**:
- `at_pre_move()`: Before object moves
- `announce_move_from()`: Announce departure
- `at_post_move()`: After object moves

**Puppeting Hooks**:
- `at_pre_puppet()`: Before account controls character
- `at_post_puppet()`: After puppeting starts
- `at_pre_unpuppet()`: Before unpuppeting

**Server Event Hooks**:
- `at_server_reload()`: When server reloads
- `at_server_shutdown()`: When server shuts down

**Interaction Hooks**:
- `at_traverse()`: When exit is used
- `at_get()`: When object is picked up
- `at_drop()`: When object is dropped
- `at_say()`: When character speaks

**Reference**: See `evennia.objects.objects` in the codebase for complete list.

---

## Configuration

### Settings File

**Location**: `beckonmu/server/conf/settings.py`

**Important Paths**:
- `GAME_DIR`: Path to game directory (use for file paths in settings)
- `EVENNIA_DIR`: Path to Evennia installation
- `SERVERNAME`: Game name

**Best Practice**: Only override settings you need to change. Don't copy entire default file.

**Default Settings Reference**: https://www.evennia.com/docs/latest/Setup/Settings-Default.html

### Secret Settings

**Location**: `beckonmu/server/conf/secret_settings.py` (gitignored)

Use for server-specific or sensitive configuration.

### Other Configuration Files

Located in `beckonmu/server/conf/`:
- Connection screens
- Lock functions
- Input/inline functions
- Server hooks

---

## Working with Typeclasses

### Creating Instances

**Always use creation functions**, never manual instantiation:
```python
from evennia import create_object
chair = create_object("furniture.Furniture", key="Chair")
```

### Typeclass Constraints

1. **Database Integration**: Some properties are database fields accepting only specific data types
2. **Unique Naming**: Class names must be globally unique across entire server
3. **Initialization Restrictions**: Don't override `__init__`. Use hooks instead:
   - `at_object_creation()`: For initial setup
   - `at_init()`: For cached-load operations

### Idmapper System

Evennia caches typeclass instances in memory, preserving on-object handlers and properties throughout server runtime. This differs from vanilla Django's default behavior.

### Querying Typeclasses

**Direct Django queries** (only direct subclasses):
```python
matches = Furniture.objects.get(db_key="Chair")
```

**Family queries** (includes subclasses):
```python
matches = Furniture.objects.filter_family(db_key__startswith="Chair")
```

**Model-level queries** (all typeclasses of base type):
```python
from evennia import ScriptDB
matches = ScriptDB.objects.filter(db_key__contains="Combat")
```

### Updating Existing Instances

Code changes apply automatically on server reload, but database-saved data requires manual updates:
```python
for obj in Furniture.objects.all():
    if not obj.db.worth:
        obj.at_object_creation()  # Re-initialize
```

**Best Practice**: Place attributes in creation hooks to minimize retroactive modifications.

### Swapping Typeclasses

**In-game command**: `@typeclass <object> = new.TypeClass[/switches]`

**Programmatically**: `obj.swap_typeclass()`

**Useful switches**:
- `/reset`: Purges attributes and reruns creation hooks
- `/force`: Required when swapping to same typeclass

---

## Directory Structure

**`beckonmu/typeclasses/`**: Game entity definitions
- Each module contains skeleton classes inheriting from Evennia defaults
- Override methods to customize behavior

**`beckonmu/commands/`**: Command definitions and command sets
- `command.py`: Base command class for this game
- `default_cmdsets.py`: Command set definitions

**`beckonmu/world/`**: Game-specific code
- `prototypes.py`: Object prototypes for spawning
- `help_entries.py`: Custom help entries

**`beckonmu/server/conf/`**: Server configuration
- `settings.py`: Main configuration
- `secret_settings.py`: Secrets (gitignored)
- Connection screens, hooks, lock functions

**`beckonmu/web/`**: Web interface customization (Django)
- `website/`: Public-facing website
- `webclient/`: Web-based MUD client
- `admin/`: Admin interface customization
- `api/`: REST API endpoints

**Important**: Do NOT restructure `server/` directory—Evennia expects its layout.

---

## Module Discovery

New subdirectories require `__init__.py` files for Python module discovery.

---

## Technical Notes

### DBref Sustainability

Evennia never reuses dbrefs (database references). SQLite3's maximum dbref value would take approximately 60 million years to exhaust at a rate of 10,000 new objects per second—a non-concern for practical development.

### Evennia Installation Location

TheBeckoningMU project: `.venv/Scripts/evennia`

---

## Resources

- **Main Documentation**: https://www.evennia.com/docs/latest/index.html
- **Evennia Wiki**: https://github.com/evennia/evennia/wiki
- **Tutorials**: https://github.com/evennia/evennia/wiki/Tutorials
- **Directory Overview**: https://github.com/evennia/evennia/wiki/Directory-Overview#the-game-directory
- **Default Settings**: https://www.evennia.com/docs/latest/Setup/Settings-Default.html
- **API Reference**: Check `evennia.objects.objects` for complete hooks list

---

## Summary

**Key Concepts**:
- Typeclasses = Django proxy models for game entities
- Three-level inheritance: DB models → Defaults → Custom
- Two attribute systems: `.db` (persistent) vs `.ndb` (temporary)
- Hooks = Methods called automatically at specific times
- ObjectParent mixin affects ALL game entities with location

**Best Practices**:
- Use creation functions, not manual instantiation
- Don't override `__init__`, use hooks
- Use wrapper properties (e.g., `key`) not DB fields (e.g., `db_key`)
- Mix `.db` and `.ndb` strategically
- Only override needed settings
- Place attributes in creation hooks
