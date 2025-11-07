# Web-Based Character Creation System

## Overview

TheBeckoningMU provides a comprehensive web-based character creation and approval system for Vampire: The Masquerade 5th Edition. Players can create characters through an intuitive web interface, and staff can review and approve them through a dedicated staff portal.

## System Components

### For Players

#### Character Creation Interface
- **URL**: `http://localhost:4001/character-creation/`
- **Requirements**: Must be logged in to the web portal

**Features**:
- Interactive form with V5 gothic theming
- Visual dot-based trait selection
- Real-time validation of character builds
- Point allocation tracking for attributes, skills, and disciplines
- Clan selection with automatic discipline assignment
- Predator type selection
- Merit, flaw, and background selection
- Biography fields (Concept, Ambition, Desire, Chronicle)

**Character Creation Process**:
1. Navigate to `http://localhost:4001/character-creation/`
2. Fill out character name and biographical information
3. Select clan (this determines available disciplines)
4. Select predator type
5. Allocate attribute dots (7/5/3 distribution)
6. Allocate skill dots (11/7/4 distribution)
7. Select discipline dots (2 from clan disciplines)
8. Choose merits and flaws (up to 7 points in merits)
9. Allocate background dots (3 dots total)
10. Submit character for staff approval

### For Staff

#### Character Approval Interface
- **URL**: `http://localhost:4001/staff/character-approval/`
- **Requirements**: Must be logged in as staff member

**Features**:
- List of all pending character applications
- Detailed character sheet view
- Side-by-side comparison of character data
- Approve or reject with feedback
- Character status tracking
- Edit capabilities for making adjustments before approval

**Approval Process**:
1. Navigate to `http://localhost:4001/staff/character-approval/`
2. View list of pending characters in the sidebar
3. Click on a character to view full details
4. Review character build for rules compliance
5. Either:
   - **Approve**: Character is activated and placed in game
   - **Reject**: Return to player with feedback for corrections

## API Endpoints

The web interface uses the following RESTful API endpoints:

### Trait Data Endpoints
- `GET /api/traits/` - Fetch available traits (filtered by category)
  - Parameters: `category` (disciplines, advantages, flaws)
- `GET /api/traits/categories/` - Fetch all trait categories
- `GET /api/traits/discipline-powers/` - Fetch discipline powers

### Character Management Endpoints
- `POST /api/traits/character/create/` - Create new character from web form
- `GET /api/traits/pending-characters/` - List all pending characters (staff only)
- `GET /api/traits/character/<id>/detail/` - Get character details (staff only)
- `POST /api/traits/character/<id>/approval/` - Approve or reject character (staff only)
- `GET /api/traits/character/<id>/export/` - Export character as JSON
- `POST /api/traits/character/import/` - Import character from JSON
- `POST /api/traits/character/validate/` - Validate character build

## Integration with In-Game Commands

Web-created characters integrate seamlessly with the in-game command system:

### After Approval
Once a character is approved through the web interface:
1. Character object is created in the game world
2. All traits are stored in the character's database attributes
3. Player can use `+sheet` to view their character
4. All V5 commands (`+roll`, `+disciplines`, `+blood`, etc.) work immediately
5. Character can be puppeted normally through the MUD client

### Staff Commands
Staff can also manage characters using in-game commands:
- `+pending` - List characters awaiting approval
- `+approve <character>` - Approve a character application
- `+reject <character> = <reason>` - Reject with feedback
- `+chargen/view <character>` - View character application details

## Technical Details

### File Structure
```
beckonmu/
├── web/
│   ├── templates/
│   │   ├── character_creation.html    # Player creation interface
│   │   └── character_approval.html    # Staff approval interface
│   ├── website/
│   │   ├── views/
│   │   │   └── __init__.py            # Django views
│   │   └── urls.py                    # Website URL routing
│   └── urls.py                        # Main web URL config
├── traits/
│   ├── api.py                         # RESTful API views
│   ├── urls.py                        # API URL routing
│   ├── models.py                      # Database models
│   └── utils.py                       # Helper functions
└── commands/
    ├── chargen.py                     # Staff approval commands
    └── v5/
        └── chargen.py                 # Player chargen commands
```

### Database Models
- **CharacterBio**: Stores biographical information and approval status
- **CharacterTrait**: Stores trait values (attributes, skills, etc.)
- **CharacterPower**: Stores discipline powers learned
- **Trait**: Master list of available traits
- **TraitCategory**: Organizational categories for traits
- **DisciplinePower**: Master list of discipline powers

### Authentication
- Player character creation requires login (`@login_required`)
- Staff approval interface requires staff permissions (`@staff_member_required`)
- API endpoints validate user authentication before processing

## Validation Rules

The system enforces V5 character creation rules:

### Attributes
- Three categories: Physical, Social, Mental
- Dot distribution: 7 in primary, 5 in secondary, 3 in tertiary
- Valid values: 1-5 dots per attribute

### Skills
- Three categories: Physical, Social, Mental
- Dot distribution: 11 in primary, 7 in secondary, 4 in tertiary
- Valid values: 0-5 dots per skill

### Disciplines
- 2 dots total at character creation
- Must be from clan disciplines (in-clan)
- Thin-Bloods use Alchemy instead

### Merits & Flaws
- Merits: Maximum 7 dots
- Flaws: Optional, provide bonus points
- Instanced merits require specific instances

### Backgrounds
- 3 dots total
- Valid backgrounds: Allies, Contacts, Fame, Haven, Herd, Influence, Mask, Resources, Retainers, Status

## Troubleshooting

### "API endpoint not found" error
- Ensure `beckonmu.traits` is in `INSTALLED_APPS` in settings.py
- Verify `beckonmu.traits.urls` is included in `beckonmu/web/urls.py`
- Restart the Evennia server after making changes

### "Template does not exist" error
- Verify templates are in `beckonmu/web/templates/`
- Check that `TEMPLATE_DIRS` in settings.py includes this directory
- Restart the Evennia server

### CSRF token errors
- Ensure middleware includes `django.middleware.csrf.CsrfViewMiddleware`
- Templates use `{% csrf_token %}` in forms
- JavaScript includes `X-CSRFToken` header in fetch requests

### Character not appearing after approval
- Check that character's `approved` flag is True in database
- Verify character has a `home` location set
- Use `+pending` command to see current approval status

## Starting the System

1. **Start Evennia**:
   ```bash
   evennia start
   ```

2. **Access Web Interface**:
   - Web client: `http://localhost:4001`
   - Character creation: `http://localhost:4001/character-creation/`
   - Staff approval: `http://localhost:4001/staff/character-approval/`

3. **Create Admin Account** (first time):
   ```bash
   evennia createsuperuser
   ```

## Future Enhancements

Potential improvements for future versions:
- Character template system (pre-built archetypes)
- In-browser character sheet editing
- XP spend interface for character advancement
- Real-time collaboration (ST helping player build character)
- Mobile-responsive design improvements
- Character export/import between games

---

**Note**: This system provides an alternative to command-based character creation. Players can choose either:
- Web-based creation (this system) - more visual and user-friendly
- Command-based creation (`+chargen` commands) - for experienced MUSH players

Both methods result in identical characters and use the same approval workflow.
