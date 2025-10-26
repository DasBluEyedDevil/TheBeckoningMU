# CmdImportCharacter Implementation - Testing Guide

## Implementation Summary

Successfully implemented the `CmdImportCharacter` command for Phase 1 MVP character import functionality.

### Files Modified
- `beckonmu/commands/chargen.py` - Added CmdImportCharacter command class

### Files Created
- `beckonmu/server/conf/character_imports/test_character.json` - Sample JSON file for testing
- `beckonmu/server/conf/character_imports/README.md` - User documentation

### Key Features Implemented

1. **Command Interface**
   - Command: `+import <filename>`
   - Aliases: `import`
   - Help category: "Character"
   - Available to all players (locks: "cmd:all()")

2. **Security Features**
   - Directory traversal prevention (blocks `..`, `/`, `\` in filenames)
   - File location restricted to `server/conf/character_imports/`
   - Only allows importing to caller's own character
   - Cross-platform path handling using `os.path.join()`

3. **Error Handling**
   - File existence validation
   - JSON parsing error catching
   - Puppeting requirement check
   - Detailed error messages to user

4. **Integration**
   - Uses `enhanced_import_character_from_json()` utility from `beckonmu/traits/utils.py`
   - Added to `ChargenCmdSet` for automatic availability
   - Follows existing command patterns from chargen.py

5. **User Feedback**
   - Formatted results table showing:
     - Number of traits imported
     - Number of specialties imported
     - Number of powers imported
     - Validation errors (if any)
     - Import errors (if any)
     - Warnings (if any)

## Testing Instructions

### 1. Start the Evennia Server

```bash
evennia start
```

### 2. Connect and Create a Test Character

Connect via MUD client to `localhost:4000` or web client at `http://localhost:4001`

```
@charcreate TestChar
@ic TestChar
```

### 3. Test the Import Command

#### Test with the provided sample file:
```
+import test_character.json
```

or without extension:
```
+import test_character
```

#### Expected Output:
```
Importing character data...
==============================================================================
Character Import Results
==============================================================================
Import completed successfully!

  Traits imported: 14
  Specialties imported: 1
  Powers imported: 0

==============================================================================
```

### 4. Test Error Conditions

#### Test file not found:
```
+import nonexistent.json
```

Expected: Error message showing file not found

#### Test directory traversal attempt:
```
+import ../../../etc/passwd
```

Expected: Error message about invalid filename

#### Test without arguments:
```
+import
```

Expected: Usage message

### 5. Verify Import Results

Use the `+review` command (if you have staff permissions) or check your character sheet to verify the imported traits.

```
+review TestChar
```

## JSON File Format

Place JSON files in: `beckonmu/server/conf/character_imports/`

Example structure (see test_character.json):

```json
{
  "name": "Character Full Name",
  "concept": "Character Concept",
  "splat": "vampire",
  "clan": "Brujah",
  "generation": 13,
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
    "intimidation": 2,
    "awareness": 1
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

## Command Help

Players can access help in-game:
```
help +import
```

## Integration with Web Character Generator

This command is designed to work with JSON files exported from the web-based character generator. Players can:

1. Create characters using the web interface
2. Export to JSON
3. Place file in `server/conf/character_imports/`
4. Import using `+import <filename>`

## Next Steps

- Test with web-generated character JSON files
- Add to Phase 1 MVP completion checklist
- Document in player help files
- Consider adding staff notification on character import
- Consider adding import history/audit trail
