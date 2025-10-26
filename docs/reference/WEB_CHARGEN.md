# Web-Based Character Creation System Analysis

**Status**: Manual analysis (Gemini rate-limited)
**Source**: reference repo/BeckoningMU-master
**Date**: 2025-10-20

## Executive Summary

The reference repository implements a **RESTful JSON-based web character creation system** that allows players to create characters in a web form, export to JSON, and import into the MUD via command. This system uses Django REST API endpoints and a dual-storage model.

---

## Architecture Overview

### 1. **Dual Storage System**

The system maintains **two parallel data stores**:

**A. Legacy System** (`character.db.stats`)
- Evennia attribute system
- Dictionary stored in: `character.db.stats`
- Structure from `world/data.py`:
  - `stats['attributes']` - Physical/Social/Mental attributes
  - `stats['skills']` - 27 skills
  - `stats['disciplines']` - Vampire powers
  - `stats['specialties']` - Skill specializations
  - `stats['bio']` - Character biographical data
  - `stats['pools']` - Willpower, Humanity, Blood Potency
  - `stats['approved']` - Boolean approval status

**B. New Traits System** (Django Models)
- Database-driven with proper relational modeling
- Models in `traits/models.py`:
  - `TraitCategory` - Categories (Attributes, Skills, Disciplines, etc.)
  - `Trait` - Trait definitions with VtM 5e rules
  - `DisciplinePower` - Individual discipline powers with amalgam support
  - `CharacterTrait` - Many-to-many relationship (Character → Trait)
  - `CharacterPower` - Many-to-many relationship (Character → DisciplinePower)
  - `CharacterBio` - Biographical data (clan, sire, concept, etc.)

### 2. **Synchronization Bridge**

**File**: `traits/utils.py`

Provides dual-read/dual-write functions:
- `get_character_trait_value()` - Checks new system first, falls back to legacy
- `set_character_trait_value()` - Writes to both systems simultaneously
- `enhanced_import_character_from_json()` - Imports to both systems with validation

---

## JSON Character Format

### Example Structure

```json
{
  "name": "Victoria Ashwood",
  "splat": "vampire",
  "bio": {
    "clan": "Toreador",
    "concept": "Struggling Artist",
    "sire": "Marcus the Magnanimous",
    "generation": 13,
    "predator_type": "Scene Queen",
    "chronicle": "The Beckoning - Chicago"
  },
  "attributes": {
    "strength": 2,
    "dexterity": 3,
    "stamina": 2,
    "charisma": 4,
    "manipulation": 2,
    "composure": 3,
    "intelligence": 2,
    "wits": 3,
    "resolve": 2
  },
  "skills": {
    "academics": 1,
    "athletics": 2,
    "awareness": 2,
    "etiquette": 3,
    "performance": 4,
    "persuasion": 3,
    "streetwise": 1,
    "subterfuge": 2
  },
  "disciplines": {
    "Auspex": 1,
    "Celerity": 2,
    "Presence": 2
  },
  "discipline_powers": [
    {"name": "Heightened Senses", "discipline": "Auspex", "level": 1},
    {"name": "Fleetness", "discipline": "Celerity", "level": 1},
    {"name": "Cat's Grace", "discipline": "Celerity", "level": 2},
    {"name": "Awe", "discipline": "Presence", "level": 1},
    {"name": "Daunt", "discipline": "Presence", "level": 1}
  ],
  "specialties": {
    "performance": {"singing": 2},
    "persuasion": {"seduction": 1}
  },
  "pools": {
    "humanity": 7,
    "willpower": 5,
    "blood_potency": 1
  },
  "advantages": [
    {"name": "Resources", "value": 2},
    {"name": "Haven", "value": 1}
  ],
  "flaws": [
    {"name": "Enemy", "value": 2, "description": "Rival Toreador in Chicago"}
  ],
  "notes": "Victoria was embraced during an art gallery opening..."
}
```

### Required Fields
- `splat` - Must be valid from SPLATS list (vampire, mortal, ghoul, etc.)

### Optional Fields
- All others are optional but validated if present

---

## API Endpoints

**File**: `traits/api.py`

### Trait Browsing
- `GET /api/traits/categories/` - List all trait categories
- `GET /api/traits/?category=<code>&splat=<splat>` - Get traits by category/splat
- `GET /api/discipline-powers/?discipline=<name>&level=<1-5>` - Get discipline powers

### Character Operations
- `POST /api/character/validate/` - Validate JSON without importing
  - Request: `{"character_data": {...}}`
  - Response: `{"valid": true/false, "errors": [], "warnings": []}`

- `POST /api/character/import/` - Import character JSON
  - Request: `{"character_name": "Victoria", "account_name": "player1", "character_data": {...}}`
  - Response: `{"success": true, "imported": {...}, "errors": [], "warnings": []}`

- `GET /api/character/<id>/export/` - Export character to JSON
  - Response: `{"character_data": {...}, "character_name": "Victoria"}`

- `GET /api/character/<id>/available-traits/` - Get traits available for character's splat

### CSRF Exemption
All API views use `@csrf_exempt` for external JSON clients.

---

## In-Game Import Command

**File**: `commands/chargen.py` (lines 686-986)

### Command: `import`

**Usage**:
```
import <filename>             - Import character from JSON file
import/list                   - List available JSON files
import/check <filename>       - Validate JSON without importing
```

**File Location**: `server/conf/character_imports/`

**Process**:
1. Check caller is in chargen area or is Admin
2. Check character not already approved
3. Load JSON file from `character_imports/` directory
4. Validate data using `enhanced_import_character_from_json(..., validate_only=True)`
5. Apply data using `enhanced_import_character_from_json(character, data)`
6. Report import results (traits, specialties, powers imported)

**Enhanced Validation** (from `traits/utils.py`):
- VtM 5e clan restrictions (e.g., only Tremere can take Blood Sorcery)
- Discipline level requirements (must have Discipline 1 before Discipline 2)
- Amalgam prerequisites (e.g., Cloud Memory requires Dominate 3 + Obfuscate 1)
- Attribute/skill value ranges (Attributes: 1-5, Skills: 0-5)
- Splat restrictions (only vampires can have disciplines)

---

## Approval Workflow

### Step 1: Character Submission

**Command**: `submit`
**File**: `commands/chargen.py:598-643`

**Process**:
1. Check character is in chargen area
2. Check not already submitted
3. Create job in Jobs system:
   - Bucket: "CGEN"
   - Title: "Character Generation"
   - Description: "{name} has submitted an application."
   - Created by: Character
4. Set `character.db.submitted = True`

### Step 2: Staff Approval

**Command**: `approve <character>`
**File**: `commands/chargen.py:645-684`
**Lock**: `cmd:perm(Builder)`

**Process**:
1. Search for character by name
2. Check not already approved
3. Set `character.db.stats['approved'] = True`
4. Set `character.db.stats['approved_by'] = <staff_name>`

**Integration with Jobs System**:
- Uses `jobs.new_commands.CmdJobs.create_job()`
- Jobs are tracked in separate `jobs/` app
- Staff review character via Jobs interface
- Staff approve using `approve` command
- **TODO**: Enhance to auto-close job on approval

---

## Web Form Integration

### Files Found
- `reference repo/public_html/character-creation.html` - Basic form (older version)
- `reference repo/public_html/character-creation-new.html` - Enhanced form with validation
- `reference repo/public_html/assets/js/character-sheet-new.js` - Full validation logic (1000+ lines)
- `reference repo/public_html/assets/css/character-sheet-new.css` - Styling

### Technology Stack
**Pure HTML/CSS/JavaScript** - No framework dependencies
- Vanilla JavaScript with DOM manipulation
- CSS Grid for layout
- localStorage for temporary character storage
- No server-side dependency (fully client-side)

### Features Implemented

#### 1. **Interactive Dot-Based System**
```javascript
// Visual dot selection for attributes/skills
<div class="dots" data-category="physical" data-attribute="strength">
    <span class="dot" data-value="1"></span>
    <span class="dot" data-value="2"></span>
    <span class="dot" data-value="3"></span>
    <span class="dot" data-value="4"></span>
    <span class="dot" data-value="5"></span>
</div>
```

#### 2. **Point-Buy Validation** (V5 Rules)
```javascript
const validationRules = {
    attributes: {
        totalDots: 9,  // 4/3/2 distribution
        priorityDots: { high: 4, medium: 3, low: 2 }
    },
    skills: {
        totalDots: 27,  // 13/9/5 distribution
        maxAtCreation: 3,
        priorityDots: { high: 13, medium: 9, low: 5 }
    },
    disciplines: {
        max: 5,
        maxAtCreation: 2,
        totalDots: 3  // 3 dots total at chargen
    },
    backgrounds: {
        max: 5,
        totalDots: 7  // 7 dots for advantages
    }
};
```

#### 3. **Clan Selection with Auto-Populate**
```javascript
const clanData = {
    brujah: {
        disciplines: ['potence', 'presence', 'celerity'],
        bane: 'Brujah have a harder time controlling their anger...',
        compulsion: 'Rebellion: The vampire refuses to bow to any authority...'
    },
    // ... all clans with disciplines, banes, compulsions
};

// When clan selected, auto-populate disciplines and show clan details
```

#### 4. **Real-Time Point Tracking**
```javascript
const pointTrackers = {
    attributes: { total: 9, used: 0, remaining: 9 },
    skills: { total: 27, used: 0, remaining: 27 },
    disciplines: { total: 3, used: 0, remaining: 3 },
    backgrounds: { total: 7, used: 0, remaining: 7 }
};

// Updates displayed as: "Points remaining: 9"
```

#### 5. **Predator Type Selection**
- 10 predator types: Alleycat, Bagger, Blood Leech, Cleaver, Consensualist, Farmer, Osiris, Sandman, Scene Queen, Siren
- Dropdown selection stored in bio data

#### 6. **Client-Side Validation**
```javascript
function validateCharacter() {
    // Check name and concept filled
    if (!character.name.trim()) {
        showError("Please enter a character name.");
        return false;
    }

    // Check clan selected
    if (!character.clan) {
        showError("Please select a clan.");
        return false;
    }

    // Validate point allocation
    // Validate required fields
    // Return true/false
}
```

#### 7. **JSON Export**
```javascript
function formatCharacterData(char) {
    return {
        splat: "vampire",
        bio: {
            "full name": char.name,
            concept: char.concept,
            clan: char.clan,
            generation: char.generation,
            predator: char.predator
        },
        attributes: {
            strength: char.attributes.physical.strength,
            dexterity: char.attributes.physical.dexterity,
            // ... all 9 attributes
        },
        skills: {
            // Only includes skills with values > 0
        },
        disciplines: {
            // Only includes disciplines with values > 0
        },
        specialties: {},
        advantages: {},
        flaws: {},
        pools: {
            health: char.health,
            willpower: char.willpower,
            humanity: char.humanity,
            "blood potency": char.bloodPotency
        },
        notes: char.notes
    };
}

// Export button: JSON.stringify(formattedData, null, 2)
```

#### 8. **User Experience Flow**
1. **Character Info**: Enter name, concept, chronicle
2. **Clan Selection**: Choose clan → auto-populate disciplines, show bane/compulsion
3. **Predator Type**: Select feeding style
4. **Attributes**: Distribute 9 dots using 4/3/2 priority system
5. **Skills**: Distribute 27 dots using 13/9/5 priority system
6. **Disciplines**: Allocate 3 dots from in-clan disciplines
7. **Backgrounds**: Allocate 7 dots to advantages
8. **Flaws**: Optional (can increase points)
9. **Export**: Click "Generate JSON" → copy to clipboard or download

### Integration with Evennia

**Current Implementation**: Standalone HTML files
- Not integrated with Evennia web server
- Must manually download JSON and upload to MUD

**Recommended Integration** (Phase 3):

1. **Move to Evennia Web Directory**
   ```
   beckonmu/web/static/chargen/
   ├── character-creation.html
   ├── assets/
   │   ├── js/character-sheet.js
   │   └── css/character-sheet.css
   ```

2. **Add Django URL Route**
   ```python
   # beckonmu/web/urls.py
   path('chargen/', TemplateView.as_view(template_name='chargen/character-creation.html'))
   ```

3. **Add AJAX Submission**
   ```javascript
   // Instead of localStorage, POST to /api/character/import/
   fetch('/api/character/import/', {
       method: 'POST',
       headers: {
           'Content-Type': 'application/json',
           'X-CSRFToken': getCookie('csrftoken')
       },
       body: JSON.stringify({
           character_name: character.name,
           account_name: currentUser.username,
           character_data: formattedData
       })
   })
   .then(response => response.json())
   .then(data => {
       if (data.success) {
           showSuccess("Character submitted for approval!");
       } else {
           showError(data.errors.join(", "));
       }
   });
   ```

4. **Session Integration**
   - Require logged-in session
   - Auto-fill account_name from session
   - Create character object before allowing chargen
   - Auto-submit job after successful import

### Assessment

#### ✅ What Works Well
- **Comprehensive V5 rules**: 4/3/2 attributes, 13/9/5 skills, 3 discipline dots
- **Visual feedback**: Dot-based selection feels like tabletop character sheet
- **Clan integration**: Auto-populates disciplines based on clan
- **Real-time validation**: Points tracker updates live
- **No dependencies**: Pure vanilla JavaScript, works anywhere

#### ⚠️ Improvements Needed
1. **Missing Clans**: Only 9 clans, should have all 13 (no Banu Haqim, Hecata, Lasombra, Ministry, Tzimisce, Ravnos)
2. **No Discipline Powers**: Only tracks discipline dots, not individual powers
3. **No Specialties UI**: Specialties data structure exists but no UI to add them
4. **No XP Tracking**: Doesn't calculate XP costs for out-of-clan disciplines
5. **localStorage Only**: No server integration, manual JSON download
6. **No Character List**: Can't view previously created characters
7. **Missing V5 Mechanics**:
   - Touchstones (Humanity tracking)
   - Convictions (Humanity system)
   - Ambition/Desire (Chronicle tenets)
   - True Age (vs apparent age)

#### 🔧 Recommended Enhancements
1. **Add missing clans** with proper disciplines
2. **Discipline power selection** UI after allocating dots
3. **Specialties modal** for adding skill specializations
4. **Character list page** showing all submitted characters
5. **Staff approval interface** in web UI (not just command-line)
6. **Auto-save to localStorage** every 30 seconds (prevent data loss)
7. **Import from JSON** button to resume editing
8. **Print stylesheet** for physical character sheet

### Deployment Strategy

**Phase 1 (Current)**: Standalone HTML
- Host on external site or use as-is
- Manual JSON download/upload

**Phase 2 (MVP Integration)**: Static files in Evennia
- Copy to `beckonmu/web/static/chargen/`
- Add URL route in Django
- Still use manual JSON download, but hosted in-game

**Phase 3 (Full Integration)**: AJAX API calls
- Replace localStorage with API calls
- Session-based authentication
- Auto-create character object
- Auto-submit approval job
- Staff approval interface in web UI

---

## Code Quality Assessment

### ✅ What Works Well

1. **Dual Storage Strategy**
   - Preserves legacy data while migrating to new system
   - Backward compatible with existing characters
   - Gradual migration path

2. **Enhanced Validation**
   - VtM 5e rule enforcement at API level
   - Prevents invalid character creation
   - Clear error messages for players

3. **RESTful API Design**
   - Clean separation of concerns
   - Reusable endpoints for multiple clients
   - JSON standard format

4. **Import Command Flexibility**
   - List/check/import switches
   - Validation before import
   - Detailed import reporting

### ⚠️ Issues to Fix

1. **Security Concerns**
   - CSRF exemption on all API endpoints
   - No authentication required for trait browsing
   - File upload directory not validated (directory traversal risk)
   - **FIX**: Add token-based auth, validate file paths

2. **Jobs System Integration**
   - Submit creates job but approval doesn't close it
   - No auto-notification to player on approval
   - **FIX**: Hook approval command to Jobs system

3. **Validation Gaps**
   - No point-buy validation (e.g., 7/5/3 for attributes in V5)
   - No XP cost calculation
   - Discipline clan restrictions not checked at import
   - **FIX**: Add CharacterValidationService with full V5 chargen rules

4. **File Management**
   - JSON files accumulate in character_imports/
   - No auto-cleanup after import
   - **FIX**: Archive or delete after successful import

5. **Error Handling**
   - Generic exception catching in some places
   - Insufficient logging of validation failures
   - **FIX**: Add structured logging, specific error types

### 🔧 Edge Cases Not Handled

1. **Concurrent Import**: Two players import same character name simultaneously
2. **Partial Failure**: Some traits imported, others fail - rollback needed?
3. **Name Conflicts**: Character name in JSON doesn't match character object
4. **Legacy Characters**: Old characters without bio data - migration needed?

---

## Recommendations for Implementation

### Phase 1: Core JSON Import (MVP)
**Priority**: HIGH

1. **Copy Enhanced Import System**
   - `traits/models.py` → `beckonmu/traits/models.py`
   - `traits/utils.py` → `beckonmu/traits/utils.py`
   - `traits/api.py` → `beckonmu/traits/api.py`

2. **Implement Import Command**
   - Copy `CmdImportCharacter` from `commands/chargen.py:686-986`
   - Add to ChargenCmdSet
   - Create `server/conf/character_imports/` directory

3. **Run Migrations**
   - Create initial migration for Trait models
   - Sync existing characters: `python manage.py migrate`

4. **Test with Sample JSON**
   - Create sample V5 vampire JSON
   - Import using `import sample.json`
   - Verify data in both legacy and new systems

### Phase 2: RESTful API
**Priority**: MEDIUM

1. **Add API URLs**
   - Include `traits.api.get_api_urls()` in main `urls.py`
   - Test endpoints with Postman/curl

2. **Add Authentication**
   - Replace `@csrf_exempt` with session auth or tokens
   - Require logged-in account for character import

3. **Add Rate Limiting**
   - Prevent API abuse
   - Use django-ratelimit or similar

### Phase 3: Web Form
**Priority**: LOW (can defer to later)

1. **Choose Framework**: React or Vue.js
2. **Build Form**: Multi-step character creation wizard
3. **Add Validation**: Client-side + server-side validation
4. **Export Button**: Download character JSON
5. **Integration**: Host on Evennia web server at `/chargen`

### Phase 4: Validation Enhancements
**Priority**: MEDIUM

1. **Point-Buy System**
   - Implement V5 chargen point allocation rules
   - 7/5/3 for Attributes, 13/9/5 for Skills
   - 3 discipline dots for in-clan, out-of-clan restrictions

2. **Amalgam Prerequisites**
   - Validate amalgam discipline requirements
   - Check prerequisite powers

3. **Clan Restrictions**
   - Only allow in-clan disciplines at chargen
   - Enforce clan banes/compulsions

### Phase 5: Jobs Integration
**Priority**: LOW

1. **Approval Hook**: Auto-close job on `approve`
2. **Notification**: Notify player on approval
3. **Rejection**: Add `reject <character>=<reason>` command

---

## Migration Strategy

### Step 1: Database Models
Create Django models for traits system, migrate database.

### Step 2: Dual-Write Implementation
Update all chargen commands to write to both systems.

### Step 3: Synchronization Migration
Run migration to sync all existing characters to new system.

### Step 4: Legacy Deprecation (Future)
Eventually remove legacy `character.db.stats` in favor of database-only.

---

## Security Considerations

1. **File Upload Validation**
   - Restrict file types to `.json`
   - Validate JSON structure before parsing
   - Limit file size (e.g., 100KB max)

2. **Path Traversal Prevention**
   - Use `pathlib.Path.resolve()` to prevent `../` attacks
   - Restrict import directory to `server/conf/character_imports/`

3. **Authentication**
   - API endpoints should require valid session
   - Import command should only work on caller's own characters (unless Admin)

4. **Authorization**
   - Only Builders+ can approve characters
   - Only account owners can import to their characters

5. **Input Sanitization**
   - Validate all JSON fields against whitelist
   - Sanitize strings to prevent injection attacks

---

## Next Steps

1. **Create `beckonmu/traits/` Django app**
2. **Copy models, utils, api from reference repo**
3. **Implement import command in chargen cmdset**
4. **Create sample V5 character JSON for testing**
5. **Test import workflow end-to-end**
6. **Add validation enhancements**
7. **Build web form (later phase)**

---

## File References

### Reference Repository Files
- `commands/chargen.py` - Import command (lines 686-986)
- `traits/models.py` - Django models for traits
- `traits/utils.py` - Enhanced import/export functions
- `traits/api.py` - RESTful API endpoints (lines 1-290)
- `world/data.py` - Legacy STATS dictionary structure
- `jobs/new_commands.py` - Jobs system integration

### Sample Commands Usage
```bash
# In-game import workflow
submit                           # Submit for approval
import/list                      # See available JSON files
import/check my_character.json   # Validate JSON
import my_character.json         # Import character data

# Staff approval
approve Victoria                 # Approve character
```

### API Testing
```bash
# Validate character JSON
curl -X POST http://localhost:4001/api/character/validate/ \
  -H "Content-Type: application/json" \
  -d '{"splat": "vampire", "bio": {"clan": "Toreador"}, ...}'

# Import character
curl -X POST http://localhost:4001/api/character/import/ \
  -H "Content-Type: application/json" \
  -d '{"character_name": "Victoria", "account_name": "player1", "character_data": {...}}'
```
