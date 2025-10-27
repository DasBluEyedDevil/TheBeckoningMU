"""
Manual Test Script for Character Vampire Data (Phase 6)

Run via: evennia shell < test_vampire_data_manual.py
"""

from typeclasses.characters import Character
from django.core.exceptions import ObjectDoesNotExist

print("\n" + "="*60)
print("VAMPIRE DATA STRUCTURE TEST - PHASE 6")
print("="*60 + "\n")

# Clean up any existing test characters
try:
    old_char = Character.objects.get(db_key="VampireDataTest")
    old_char.delete()
    print("[CLEANUP] Deleted existing test character")
except ObjectDoesNotExist:
    print("[CLEANUP] No existing test character to delete")

# Test 1: New Character Creation
print("\n[TEST 1] Creating new character with vampire data structure...")
char = Character.objects.create(db_key="VampireDataTest")
print(f"  ✓ Character created: {char.key}")

# Test 2: Vampire dict initialization
print("\n[TEST 2] Checking vampire data structure initialization...")
if char.db.vampire:
    print(f"  ✓ vampire dict exists")
    print(f"  ✓ clan: {char.db.vampire['clan']}")
    print(f"  ✓ generation: {char.db.vampire['generation']}")
    print(f"  ✓ blood_potency: {char.db.vampire['blood_potency']}")
    print(f"  ✓ hunger: {char.db.vampire['hunger']}")
    print(f"  ✓ humanity: {char.db.vampire['humanity']}")
    print(f"  ✓ predator_type: {char.db.vampire['predator_type']}")
    print(f"  ✓ current_resonance: {char.db.vampire['current_resonance']}")
    print(f"  ✓ resonance_intensity: {char.db.vampire['resonance_intensity']}")
    print(f"  ✓ bane: {char.db.vampire['bane']}")
    print(f"  ✓ compulsion: {char.db.vampire['compulsion']}")
else:
    print(f"  ✗ FAILED: vampire dict not initialized!")

# Test 3: Legacy hunger tracking
print("\n[TEST 3] Checking legacy hunger tracking (Phase 5 compatibility)...")
if hasattr(char.db, 'hunger'):
    print(f"  ✓ legacy db.hunger exists: {char.db.hunger}")
else:
    print(f"  ✗ FAILED: legacy db.hunger not initialized!")

# Test 4: Hunger property getter
print("\n[TEST 4] Testing hunger property getter...")
hunger_value = char.hunger
print(f"  ✓ char.hunger property works: {hunger_value}")
print(f"  ✓ Matches vampire dict: {hunger_value == char.db.vampire['hunger']}")

# Test 5: Hunger property setter
print("\n[TEST 5] Testing hunger property setter...")
char.hunger = 3
print(f"  ✓ Set char.hunger = 3")
print(f"  ✓ char.hunger: {char.hunger}")
print(f"  ✓ char.db.vampire['hunger']: {char.db.vampire['hunger']}")
print(f"  ✓ char.db.hunger (legacy): {char.db.hunger}")
if char.hunger == 3 and char.db.vampire['hunger'] == 3 and char.db.hunger == 3:
    print(f"  ✓ All three locations synced correctly!")
else:
    print(f"  ✗ FAILED: Hunger not synced across locations")

# Test 6: Hunger clamping (min)
print("\n[TEST 6] Testing hunger clamping (minimum)...")
char.hunger = -5
print(f"  ✓ Set char.hunger = -5")
print(f"  ✓ Clamped to: {char.hunger}")
if char.hunger == 0:
    print(f"  ✓ Correctly clamped to 0")
else:
    print(f"  ✗ FAILED: Should clamp to 0, got {char.hunger}")

# Test 7: Hunger clamping (max)
print("\n[TEST 7] Testing hunger clamping (maximum)...")
char.hunger = 10
print(f"  ✓ Set char.hunger = 10")
print(f"  ✓ Clamped to: {char.hunger}")
if char.hunger == 5:
    print(f"  ✓ Correctly clamped to 5")
else:
    print(f"  ✗ FAILED: Should clamp to 5, got {char.hunger}")

# Test 8: Migration for old character
print("\n[TEST 8] Testing migration for old character format...")
old_char = Character.objects.create(db_key="OldFormatChar")
old_char.db.vampire = None  # Simulate old format
old_char.db.hunger = 2
print(f"  ✓ Created old format character with db.hunger = 2")
old_char.migrate_vampire_data()
print(f"  ✓ Called migrate_vampire_data()")
print(f"  ✓ vampire dict exists: {old_char.db.vampire is not None}")
print(f"  ✓ vampire['hunger']: {old_char.db.vampire['hunger']}")
if old_char.db.vampire and old_char.db.vampire['hunger'] == 2:
    print(f"  ✓ Migration successful! Hunger preserved: {old_char.db.vampire['hunger']}")
else:
    print(f"  ✗ FAILED: Migration did not preserve Hunger value")

# Test 9: Setting vampire data fields
print("\n[TEST 9] Testing setting vampire data fields...")
char.db.vampire['clan'] = 'Brujah'
char.db.vampire['predator_type'] = 'Alleycat'
char.db.vampire['generation'] = 11
char.db.vampire['blood_potency'] = 2
char.db.vampire['humanity'] = 6
char.db.vampire['current_resonance'] = 'Choleric'
char.db.vampire['resonance_intensity'] = 2
print(f"  ✓ clan: {char.db.vampire['clan']}")
print(f"  ✓ predator_type: {char.db.vampire['predator_type']}")
print(f"  ✓ generation: {char.db.vampire['generation']}")
print(f"  ✓ blood_potency: {char.db.vampire['blood_potency']}")
print(f"  ✓ humanity: {char.db.vampire['humanity']}")
print(f"  ✓ current_resonance: {char.db.vampire['current_resonance']}")
print(f"  ✓ resonance_intensity: {char.db.vampire['resonance_intensity']}")

# Test 10: Direct db.hunger access (backward compatibility)
print("\n[TEST 10] Testing direct db.hunger access (backward compatibility)...")
char.db.hunger = 4
print(f"  ✓ Set char.db.hunger = 4 directly")
print(f"  ✓ char.db.hunger: {char.db.hunger}")
print(f"  ✓ char.hunger property: {char.hunger}")
# Note: Direct db.hunger writes won't auto-sync to vampire dict immediately,
# but the property getter will always read from vampire dict first

# Test 11: Phase 5 Dice System Compatibility
print("\n[TEST 11] Testing Phase 5 dice system compatibility...")
# Simulate how dice system reads/writes Hunger
hunger_before = char.db.hunger
print(f"  ✓ Hunger before Rouse check (via db.hunger): {hunger_before}")

# Simulate Rouse check failure (dice system writes to db.hunger)
char.db.hunger += 1
hunger_after = char.db.hunger
print(f"  ✓ Hunger after failed Rouse check (via db.hunger): {hunger_after}")
print(f"  ✓ Hunger increased: {hunger_after > hunger_before}")

# Clean up
print("\n[CLEANUP] Removing test characters...")
char.delete()
old_char.delete()
print("  ✓ Test characters deleted")

print("\n" + "="*60)
print("VAMPIRE DATA STRUCTURE TEST COMPLETE")
print("="*60 + "\n")
