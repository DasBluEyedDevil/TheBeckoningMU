#!/usr/bin/env python
"""
Test script for character JSON import functionality.
Run with: evennia shell < test_import.py
"""

import json
import os

# Import Evennia modules
from evennia.objects.models import ObjectDB
from beckonmu.traits.utils import enhanced_import_character_from_json

# Load test JSON
json_path = os.path.join('beckonmu', 'server', 'conf', 'character_imports', 'test_character.json')
with open(json_path, 'r', encoding='utf-8') as f:
    test_data = json.load(f)

print("=" * 70)
print("TESTING CHARACTER JSON IMPORT")
print("=" * 70)

# Create or find test character
test_char_name = "TestImportChar"
test_chars = ObjectDB.objects.filter(db_key=test_char_name)

if test_chars.exists():
    test_char = test_chars.first()
    print(f"Using existing test character: {test_char}")
else:
    # Create test character
    from evennia.utils import create
    test_char = create.create_object(
        typeclass="beckonmu.typeclasses.characters.Character",
        key=test_char_name,
        location=None
    )
    print(f"Created new test character: {test_char}")

print(f"\nTest JSON data preview:")
print(f"  Name: {test_data.get('name')}")
print(f"  Concept: {test_data.get('concept')}")
print(f"  Clan: {test_data.get('clan')}")
print(f"  Attributes: {len(test_data.get('attributes', {}))} defined")
print(f"  Skills: {len(test_data.get('skills', {}))} defined")
print(f"  Disciplines: {len(test_data.get('disciplines', {}))} defined")

# Perform import
print(f"\nCalling enhanced_import_character_from_json()...")
try:
    results = enhanced_import_character_from_json(test_char, test_data, validate_only=False)

    print(f"\n{'SUCCESS' if results['success'] else 'FAILED'}!")
    print(f"\nResults:")
    print(f"  Success: {results['success']}")
    print(f"  Imported: {results['imported']}")
    print(f"  Errors: {len(results['errors'])}")
    print(f"  Warnings: {len(results['warnings'])}")

    if results['errors']:
        print(f"\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")

    if results['warnings']:
        print(f"\nWarnings:")
        for warning in results['warnings']:
            print(f"  - {warning}")

    # Verify character stats
    print(f"\nVerifying character.db.stats:")
    if hasattr(test_char.db, 'stats'):
        stats = test_char.db.stats
        print(f"  Attributes.strength: {stats.get('attributes', {}).get('strength')}")
        print(f"  Skills.brawl: {stats.get('skills', {}).get('brawl')}")
        print(f"  Disciplines.celerity: {stats.get('disciplines', {}).get('celerity')}")
        print(f"  Clan: {stats.get('clan')}")
    else:
        print(f"  ERROR: character.db.stats not set!")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

except Exception as e:
    print(f"\nEXCEPTION OCCURRED: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()
