# Character Creation Workflows

TheBeckoningMU supports **two character creation workflows** that work together seamlessly:

## 1. Web-Based Character Creation (Recommended)

**URL**: https://beckon.vineyard.haus/character-creation-new.html

### Workflow:
1. **Create character** on the web form
2. **Export JSON** from the web interface
3. **Upload JSON** to `server/conf/character_imports/` on the server
4. **Log into game** and puppet your character
5. **Run command**: `+import <filename>.json`
6. **Submit for approval**: Your character is automatically submitted to staff

### Advantages:
- ✅ Visual interface with dropdowns and validation
- ✅ Automatic calculation of pools and dots
- ✅ Can save/load work in progress
- ✅ Pre-validates V5 rules before export
- ✅ Automatically syncs to both Django models AND char.db.stats

### JSON Format:
```json
{
  "name": "Character Name",
  "concept": "Street-Smart Brujah",
  "splat": "vampire",
  "clan": "Brujah",
  "generation": 13,
  "sire": "Sire Name",
  "predator_type": "Scene Queen",
  "attributes": {
    "strength": 2,
    "dexterity": 3,
    "stamina": 2,
    "charisma": 2,
    "manipulation": 2,
    "composure": 3,
    "intelligence": 2,
    "wits": 3,
    "resolve": 2
  },
  "skills": {
    "athletics": 2,
    "brawl": 3,
    "streetwise": 2,
    "intimidation": 2
  },
  "disciplines": {
    "celerity": 1,
    "potence": 2
  },
  "specialties": {
    "brawl": {
      "Grappling": 1
    }
  }
}
```

---

## 2. In-Game Character Creation

### Workflow:
1. **Log into game** and create/puppet a character
2. **Start chargen**: `+chargen/start`
3. **Select clan**: `+chargen/clan Brujah`
4. **Select predator**: `+chargen/predator Scene Queen`
5. **Set attributes**: `+setstat strength = 3`
6. **Set skills**: `+setstat brawl = 2`
7. **Set disciplines**: `+setdisc celerity = 2`
8. **Set specialties**: `+setstat/specialty brawl = Grappling`
9. **Check progress**: `+chargen`
10. **Finalize**: `+chargen/finalize`

### Advantages:
- ✅ No external tools needed
- ✅ Real-time validation and feedback
- ✅ Progress tracking shows what's missing
- ✅ Can pause and resume anytime
- ✅ Automatically syncs to both char.db.stats AND Django models

### Commands Reference:
```
+chargen                      - Show progress
+chargen/start                - Begin character creation
+chargen/clan <name>          - Select clan
+chargen/predator <type>      - Select predator type
+chargen/finalize             - Submit for approval
+chargen/reset confirm        - Reset character (WARNING: deletes all data)

+setstat <trait> = <value>    - Set attribute or skill
+setstat/specialty <skill> = <specialty>  - Set specialty
+setdisc <discipline> = <level>  - Set discipline

+sheet                        - View character sheet
+st                          - View abbreviated stats
```

---

## How The Systems Work Together

### Data Storage Architecture

TheBeckoningMU uses a **dual-layer data system**:

1. **Django Models** (`beckonmu/traits/models.py`)
   - Persistent database storage
   - Used by web import system
   - Provides data validation and relationships
   - Models: `CharacterTrait`, `DisciplinePower`, `CharacterBio`

2. **Character Attributes** (`character.db.stats`)
   - Evennia's native attribute system
   - Fast in-memory access during gameplay
   - Used by dice rolling and game mechanics
   - Structure defined in `typeclasses/characters.py`

### Bridge System

The **bridge functions** in `beckonmu/traits/utils.py` keep both systems synchronized:

- `get_character_trait_value()` - Checks Django models first, falls back to char.db.stats
- `set_character_trait_value()` - Updates BOTH Django models AND char.db.stats
- `sync_character_to_new_system()` - Syncs char.db.stats to Django models

### When Data Syncs

**Automatic Sync:**
- ✅ When importing from JSON (`+import`)
- ✅ When using in-game chargen commands (`+setstat`, `+setdisc`)
- ✅ When staff edits via `+charedit`

**Both systems are always in sync** - you can use either workflow and the data will be available to all game systems.

---

## Staff Character Approval

Both workflows feed into the same approval process:

### Staff Commands:
```
+pending                      - List characters awaiting approval
+review <character>           - Review full character sheet
+charedit <char>/<field>=<value>  - Edit character data
+approve <character>[=<message>]  - Approve character
+reject <character>=<reason>  - Reject with feedback
```

### Approval Workflow:
1. Player submits character (via web import OR in-game chargen)
2. Staff reviews with `+review <character>`
3. Staff can edit with `+charedit` if needed
4. Staff approves with `+approve` or rejects with `+reject`
5. Player is notified of approval/rejection
6. Approved characters can begin play

---

## Technical Details

### File Locations:
- **Web import directory**: `beckonmu/server/conf/character_imports/`
- **Django models**: `beckonmu/traits/models.py`
- **Bridge functions**: `beckonmu/traits/utils.py`
- **Character typeclass**: `beckonmu/typeclasses/characters.py`
- **In-game chargen commands**: `beckonmu/commands/v5/chargen.py`
- **Chargen utilities**: `beckonmu/commands/v5/utils/chargen_utils.py`

### Data Flow:

**Web Import Flow:**
```
Web Form → JSON Export → +import command → Django Models → Bridge → char.db.stats
```

**In-Game Chargen Flow:**
```
+setstat/+setdisc → Bridge Functions → Django Models + char.db.stats
```

**Gameplay Flow:**
```
Dice rolls, disciplines, etc. → char.db.stats (fast in-memory access)
```

---

## FAQ

**Q: Can I use both workflows for the same character?**
A: Yes! You can start with web import and finish in-game, or vice versa. The data syncs automatically.

**Q: What if I make a mistake during chargen?**
A: Use `+chargen/reset confirm` to start over (WARNING: deletes all data), or ask staff to edit specific traits with `+charedit`.

**Q: Do I need to use the web form?**
A: No, you can create characters entirely in-game. The web form is just a convenience tool.

**Q: Can I export my in-game character to JSON?**
A: Not yet implemented, but it's on the roadmap.

**Q: What happens if the systems get out of sync?**
A: They shouldn't - the bridge functions ensure both are updated simultaneously. If you suspect a sync issue, contact staff.

---

## For Developers

### Adding New Traits:
1. Add to Django models via Django admin or migrations
2. Add to `world/v5_data.py` for reference
3. The bridge functions will handle the rest

### Testing Import:
```bash
# Place test JSON in character_imports/
# In game:
+import test_character.json
+sheet
```

### Bridge Function Reference:
```python
from traits.utils import (
    get_character_trait_value,  # Get trait value (checks both systems)
    set_character_trait_value,  # Set trait value (updates both systems)
    sync_character_to_new_system,  # Sync char.db → Django models
    enhanced_import_character_from_json,  # Import from JSON
)
```

---

**Both workflows are fully supported and production-ready!** Choose the one that works best for you.
