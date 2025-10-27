#!/usr/bin/env python
"""
Quick test script for dice commands.
Run with: evennia shell < test_dice_commands.py
"""

from evennia.utils import create
from evennia import ObjectDB, AccountDB
from traits.models import TraitCategory, Trait, CharacterTrait, DisciplinePower, CharacterPower, Discipline
from traits.utils import get_character_trait_value

print("\n=== Testing Dice System ===\n")

# Get or create a test character
try:
    test_char = ObjectDB.objects.get(db_key="TestCharacter")
    print(f"Found existing test character: {test_char}")
except ObjectDB.DoesNotExist:
    # Create test character
    test_char = create.create_object(
        "typeclasses.characters.Character",
        key="TestCharacter",
        location=None
    )
    print(f"Created new test character: {test_char}")

# Set up basic traits for testing
test_char.db.hunger = 2

# Get or create trait categories
attr_cat, _ = TraitCategory.objects.get_or_create(name="Attributes")
skill_cat, _ = TraitCategory.objects.get_or_create(name="Skills")
disc_cat, _ = TraitCategory.objects.get_or_create(name="Disciplines")

# Get or create basic traits
strength, _ = Trait.objects.get_or_create(name="Strength", category=attr_cat)
resolve, _ = Trait.objects.get_or_create(name="Resolve", category=attr_cat)
brawl, _ = Trait.objects.get_or_create(name="Brawl", category=skill_cat)
blood_potency, _ = Trait.objects.get_or_create(name="Blood Potency", category=disc_cat)

# Set character traits
CharacterTrait.objects.update_or_create(
    character=test_char, trait=strength, defaults={'rating': 4}
)
CharacterTrait.objects.update_or_create(
    character=test_char, trait=resolve, defaults={'rating': 3}
)
CharacterTrait.objects.update_or_create(
    character=test_char, trait=brawl, defaults={'rating': 3}
)
CharacterTrait.objects.update_or_create(
    character=test_char, trait=blood_potency, defaults={'rating': 2}
)

print(f"\nCharacter traits:")
print(f"  Strength: {get_character_trait_value(test_char, 'Strength')}")
print(f"  Resolve: {get_character_trait_value(test_char, 'Resolve')}")
print(f"  Brawl: {get_character_trait_value(test_char, 'Brawl')}")
print(f"  Blood Potency: {get_character_trait_value(test_char, 'Blood Potency')}")
print(f"  Hunger: {test_char.db.hunger}")

# Test dice commands
print("\n=== Testing CmdRoll ===")
from beckonmu.dice.commands import CmdRoll
cmd_roll = CmdRoll()
cmd_roll.caller = test_char
cmd_roll.args = "5 2"
try:
    cmd_roll.func()
    print("✓ CmdRoll executed successfully")
except Exception as e:
    print(f"✗ CmdRoll failed: {e}")

print("\n=== Testing CmdRouse ===")
from beckonmu.dice.commands import CmdRouse
cmd_rouse = CmdRouse()
cmd_rouse.caller = test_char
cmd_rouse.args = "Test"
try:
    cmd_rouse.func()
    print("✓ CmdRouse executed successfully")
except Exception as e:
    print(f"✗ CmdRouse failed: {e}")

print("\n=== Testing CmdShowDice ===")
from beckonmu.dice.commands import CmdShowDice
cmd_showdice = CmdShowDice()
cmd_showdice.caller = test_char
cmd_showdice.args = ""
try:
    cmd_showdice.func()
    print("✓ CmdShowDice executed successfully")
except Exception as e:
    print(f"✗ CmdShowDice failed: {e}")

# Test discipline power command (need a power first)
print("\n=== Setting up discipline power for testing ===")
try:
    potence, _ = Discipline.objects.get_or_create(name="Potence")
    power, _ = DisciplinePower.objects.get_or_create(
        name="Lethal Body",
        discipline=potence,
        defaults={
            'level': 1,
            'dice_pool': 'Strength + Brawl',
            'cost': 'One Rouse Check',
            'description': 'Your unarmed attacks deal +1 damage.'
        }
    )
    CharacterPower.objects.get_or_create(character=test_char, power=power)
    print(f"✓ Created/found discipline power: {power.name}")

    print("\n=== Testing CmdRollPower ===")
    from beckonmu.dice.commands import CmdRollPower
    cmd_power = CmdRollPower()
    cmd_power.caller = test_char
    cmd_power.args = "Lethal Body"
    cmd_power.func()
    print("✓ CmdRollPower executed successfully")
except Exception as e:
    print(f"✗ CmdRollPower setup/test failed: {e}")

print("\n=== All Tests Complete ===\n")
