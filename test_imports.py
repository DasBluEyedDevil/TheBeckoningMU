#!/usr/bin/env python3
"""
Import test script to identify import errors across the codebase.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing all critical modules."""
    modules_to_test = [
        # World modules
        'world.v5_data',
        'world.ansi_theme',
        'world.v5_dice',

        # V5 Commands
        'beckonmu.commands.v5.sheet',
        'beckonmu.commands.v5.chargen',
        'beckonmu.commands.v5.xp',
        'beckonmu.commands.v5.hunt',
        'beckonmu.commands.v5.disciplines',
        'beckonmu.commands.v5.effects',
        'beckonmu.commands.v5.combat',
        'beckonmu.commands.v5.humanity',
        'beckonmu.commands.v5.social',
        'beckonmu.commands.v5.thinblood',
        'beckonmu.commands.v5.backgrounds',

        # V5 Utils
        'beckonmu.commands.v5.utils.trait_utils',
        'beckonmu.commands.v5.utils.chargen_utils',
        'beckonmu.commands.v5.utils.xp_utils',
        'beckonmu.commands.v5.utils.blood_utils',
        'beckonmu.commands.v5.utils.clan_utils',
        'beckonmu.commands.v5.utils.discipline_utils',
        'beckonmu.commands.v5.utils.discipline_effects',
        'beckonmu.commands.v5.utils.combat_utils',
        'beckonmu.commands.v5.utils.humanity_utils',
        'beckonmu.commands.v5.utils.social_utils',
        'beckonmu.commands.v5.utils.thin_blood_utils',
        'beckonmu.commands.v5.utils.background_utils',
        'beckonmu.commands.v5.utils.display_utils',
        'beckonmu.commands.v5.utils.hunting_utils',
    ]

    passed = []
    failed = []

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            passed.append(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            failed.append((module_name, str(e)))
            print(f"✗ {module_name}: {e}")
        except Exception as e:
            failed.append((module_name, f"Non-import error: {e}"))
            print(f"⚠ {module_name}: {e}")

    print(f"\n{'='*60}")
    print(f"PASSED: {len(passed)}/{len(modules_to_test)}")
    print(f"FAILED: {len(failed)}/{len(modules_to_test)}")

    if failed:
        print(f"\n{'='*60}")
        print("FAILED IMPORTS:")
        for module, error in failed:
            print(f"  {module}")
            print(f"    → {error}")

    return len(failed) == 0

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
