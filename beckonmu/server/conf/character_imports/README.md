# Character Import Directory

This directory is used for importing character data from JSON files into the game.

## Usage

1. Place your character JSON file in this directory
2. Log into the game and puppet your character
3. Run the command: `+import <filename>`

Example:
```
+import mycharacter.json
```

## JSON Format

Your JSON file should follow this structure:

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
    "streetwise": 2
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

## Security

- Only simple filenames are allowed (no path separators)
- Files must be in this directory
- You can only import to your own character

## Notes

- The `.json` extension is optional when using the command
- Import validation will check trait limits and requirements
- Any errors or warnings will be displayed after import
