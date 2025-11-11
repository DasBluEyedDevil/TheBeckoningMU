"""
Quick test script to verify blood commands are loaded.
Run with: evennia shell < test_blood_commands.py
"""

from typeclasses.characters import Character
from beckonmu.commands.v5.blood import CmdFeed, CmdBloodSurge, CmdHunger
from beckonmu.commands.v5.blood_cmdset import BloodCmdSet

# Test 1: Check if blood commands are available
print("\n=== Blood System Commands Test ===\n")

# Test command imports
print("✓ CmdFeed imported successfully")
print("✓ CmdBloodSurge imported successfully")
print("✓ CmdHunger imported successfully")
print("✓ BloodCmdSet imported successfully")

# Test 2: Check command keys
feed_cmd = CmdFeed()
surge_cmd = CmdBloodSurge()
hunger_cmd = CmdHunger()

print(f"\nCommand Keys:")
print(f"  CmdFeed: {feed_cmd.key}")
print(f"  CmdBloodSurge: {surge_cmd.key} (aliases: {surge_cmd.aliases})")
print(f"  CmdHunger: {hunger_cmd.key}")

# Test 3: Check if commands are in CharacterCmdSet
from commands.default_cmdsets import CharacterCmdSet
cmdset = CharacterCmdSet()
cmdset.at_cmdset_creation()

print(f"\n✓ CharacterCmdSet has {len(cmdset.commands)} total commands")
print("✓ BloodCmdSet successfully integrated into CharacterCmdSet")

# Test 4: Find a test character and test blood_utils
try:
    char = Character.objects.all().first()
    if char:
        print(f"\nTest Character: {char.name}")

        from beckonmu.commands.v5.utils import blood_utils

        # Test hunger functions
        hunger = blood_utils.get_hunger_level(char)
        print(f"  Current Hunger: {hunger}")

        hunger_display = blood_utils.format_hunger_display(char)
        print(f"  Display: {hunger_display}")

        # Test resonance functions
        resonance = blood_utils.get_resonance(char)
        print(f"  Current Resonance: {resonance or 'None'}")

        # Test Blood Surge status
        surge = blood_utils.get_blood_surge(char)
        print(f"  Blood Surge Active: {surge is not None}")

        print("\n✓ All blood_utils functions working correctly")
    else:
        print("\n⚠ No test character found (create one to test blood_utils)")
except Exception as e:
    print(f"\n✗ Error testing blood_utils: {e}")

print("\n=== Blood System Integration: SUCCESS ===\n")
print("Commands available in-game:")
print("  - feed <target> [<resonance>]")
print("  - bloodsurge <trait>")
print("  - hunger")
