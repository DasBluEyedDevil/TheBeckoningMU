# The Beckoning - Vampire: The Masquerade Website

A website for "The Beckoning", an Athens By Night Vampire: The Masquerade chronicle. The site includes an interactive character creation tool that generates JSON data for import into an Evennia-based MU*.

## Features

- Interactive Vampire: The Masquerade 5th Edition character creation
- Rule validation to ensure characters follow V5 creation guidelines
- JSON export for character data
- Integration with Evennia-based MU* systems

## Character Creation Tool

The character creation tool allows players to create Vampire: The Masquerade 5th Edition characters following the official rules. The tool includes:

- Character information (name, concept, etc.)
- Clan selection with automatic discipline assignment
- Attribute distribution (following the 4/3/2 dot rule)
- Skill distribution (following the 13/9/5 dot rule)
- Discipline selection based on clan
- Background selection
- JSON export for integration with Evennia

### Using the Character Creation Tool

1. Navigate to the character creation page by clicking the "Create a Character" button on the homepage
2. Fill out the character information
3. Select a clan
4. Distribute attribute dots (4/3/2 across Physical, Social, Mental)
5. Distribute skill dots (13/9/5 across Physical, Social, Mental)
6. Assign discipline dots based on clan
7. Select backgrounds
8. Click "Generate JSON" to create the character data
9. Copy the JSON data for import into the Evennia-based MU*

### Evennia Integration

The character creation tool generates a JSON representation of the character that can be imported into an Evennia-based MU*. The JSON structure includes all necessary character information:

```json
{
  "name": "Character Name",
  "concept": "Character Concept",
  "chronicle": "The Beckoning",
  "clan": "Clan Name",
  "attributes": {
    "physical": { "strength": 2, "dexterity": 3, "stamina": 2 },
    "social": { "charisma": 3, "manipulation": 2, "composure": 2 },
    "mental": { "intelligence": 3, "wits": 2, "resolve": 3 }
  },
  "skills": {
    "physical": { ... },
    "social": { ... },
    "mental": { ... }
  },
  "disciplines": { ... },
  "backgrounds": { ... },
  "derived": {
    "health": 5,
    "willpower": 5,
    "humanity": 7,
    "bloodPotency": 1,
    "hunger": 1
  }
}
```

To import this data into your Evennia-based MU*, you'll need to implement a command that:

1. Accepts the JSON data
2. Validates the data
3. Creates a character with the specified attributes
4. Assigns the appropriate skills, disciplines, and backgrounds

## Development

### Project Structure

- `index.html` - Main landing page
- `character-creation.html` - Character creation interface
- `assets/css/` - CSS stylesheets
  - `main.css` - Main site styles
  - `character-sheet.css` - Character sheet specific styles
- `assets/js/` - JavaScript files
  - `main.js` - Main site functionality
  - `character-sheet.js` - Character creation functionality
- `references/` - V5 reference materials

### Technologies Used

- HTML5
- CSS3
- JavaScript (ES6)
- No external libraries or frameworks required

## License

This project uses content from Vampire: The Masquerade 5th Edition, which is owned by Paradox Interactive. The website code is available under the MIT license.
