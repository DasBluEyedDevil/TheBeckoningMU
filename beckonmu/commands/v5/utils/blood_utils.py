"""
Blood System Utility Functions for V5

Handles Hunger, Blood Potency, Resonance, and feeding mechanics.
"""

from world.v5_data import BLOOD_POTENCY


def get_hunger(character):
    """
    Get character's current Hunger level.

    Args:
        character: Character object

    Returns:
        int: Hunger level (0-5)
    """
    return character.db.vampire.get("hunger", 1)


def set_hunger(character, value):
    """
    Set character's Hunger level, clamped to 0-5.

    Args:
        character: Character object
        value (int): New Hunger value

    Returns:
        int: Actual Hunger value set (after clamping)
    """
    # Clamp to valid range
    value = max(0, min(5, value))
    character.db.vampire["hunger"] = value
    return value


def increase_hunger(character, amount=1):
    """
    Increase Hunger by specified amount.

    Args:
        character: Character object
        amount (int): Amount to increase (default 1)

    Returns:
        int: New Hunger level
    """
    current = get_hunger(character)
    return set_hunger(character, current + amount)


def decrease_hunger(character, amount=1):
    """
    Decrease Hunger by specified amount.

    Args:
        character: Character object
        amount (int): Amount to decrease (default 1)

    Returns:
        int: New Hunger level
    """
    current = get_hunger(character)
    return set_hunger(character, current - amount)


def get_blood_potency(character):
    """
    Get character's Blood Potency level.

    Args:
        character: Character object

    Returns:
        int: Blood Potency level (0-10)
    """
    return character.db.vampire.get("blood_potency", 0)


def set_blood_potency(character, value):
    """
    Set character's Blood Potency level.

    Args:
        character: Character object
        value (int): New Blood Potency value (0-10)

    Returns:
        int: Actual value set (after clamping)
    """
    value = max(0, min(10, value))
    character.db.vampire["blood_potency"] = value
    return value


def get_blood_potency_bonuses(character):
    """
    Get Blood Potency bonuses for character.

    Returns:
        dict: Blood Potency modifiers
            - blood_surge: Bonus dice for Blood Surge
            - mend_amount: Amount healed per Rouse check
            - power_bonus: Bonus dice to Discipline powers
            - rouse_reroll: Can reroll failed Rouse checks for powers <= this level
            - feeding_penalty: Penalty to feed from animals/bags
            - bane_severity: Severity of clan bane
    """
    bp = get_blood_potency(character)

    # Use data from v5_data.py if available, otherwise use defaults
    if bp in BLOOD_POTENCY:
        bp_data = BLOOD_POTENCY[bp]
        return {
            "blood_surge": bp_data.get("blood_surge_bonus", 0),
            "mend_amount": bp_data.get("mend_amount", 1),
            "power_bonus": bp_data.get("power_bonus", 0),
            "rouse_reroll": bp_data.get("rouse_reroll", 0),
            "feeding_penalty": bp_data.get("feeding_penalty", 0),
            "bane_severity": bp_data.get("bane_severity", 0)
        }
    else:
        # Fallback defaults for BP 0
        return {
            "blood_surge": 2,
            "mend_amount": 1,
            "power_bonus": 0,
            "rouse_reroll": 0,
            "feeding_penalty": 0,
            "bane_severity": 0
        }


def format_hunger_display(character, show_numeric=True):
    """
    Create visual Hunger display with filled/empty circles.

    Args:
        character: Character object
        show_numeric (bool): Whether to show numeric value

    Returns:
        str: Formatted Hunger display

    Examples:
        "Hunger: |r●●●|n|x○○|n (3)"
        "Hunger: |r●●●●●|n (5) |rSTARVING|n"
    """
    hunger = get_hunger(character)

    # Filled circles (red)
    filled = "|r" + "●" * hunger + "|n"
    # Empty circles (grey)
    empty = "|x" + "○" * (5 - hunger) + "|n"

    display = f"Hunger: {filled}{empty}"

    if show_numeric:
        display += f" ({hunger})"

    # Add warning for high Hunger
    if hunger >= 4:
        display += " |rDANGER|n"
    elif hunger >= 3:
        display += " |yHungry|n"

    return display


def get_resonance(character):
    """
    Get character's current Resonance from last feeding.

    Args:
        character: Character object

    Returns:
        dict: Resonance data
            - type: Resonance type (Choleric, Melancholic, etc.) or None
            - intensity: 0-3 (none, fleeting, intense, dyscrasia)
    """
    return {
        "type": character.db.vampire.get("current_resonance", None),
        "intensity": character.db.vampire.get("resonance_intensity", 0)
    }


def set_resonance(character, resonance_type, intensity=1):
    """
    Set character's current Resonance.

    Args:
        character: Character object
        resonance_type (str): Type of Resonance (Choleric, Melancholic, Phlegmatic, Sanguine)
        intensity (int): 0=none, 1=fleeting, 2=intense, 3=dyscrasia

    Returns:
        dict: Resonance data
    """
    valid_types = ["Choleric", "Melancholic", "Phlegmatic", "Sanguine", "Animal"]

    if resonance_type and resonance_type not in valid_types:
        raise ValueError(f"Invalid resonance type: {resonance_type}. Must be one of {valid_types}")

    intensity = max(0, min(3, intensity))

    character.db.vampire["current_resonance"] = resonance_type
    character.db.vampire["resonance_intensity"] = intensity

    return get_resonance(character)


def clear_resonance(character):
    """
    Clear character's current Resonance.

    Args:
        character: Character object
    """
    character.db.vampire["current_resonance"] = None
    character.db.vampire["resonance_intensity"] = 0


def get_resonance_discipline_bonus(character, discipline_name):
    """
    Check if character has Resonance bonus for a discipline.

    Resonance provides +1 die to related Discipline powers:
    - Choleric: Potence, Celerity
    - Melancholic: Fortitude, Obfuscate
    - Phlegmatic: Auspex, Dominate
    - Sanguine: Presence, Blood Sorcery

    Args:
        character: Character object
        discipline_name (str): Name of the discipline

    Returns:
        int: Bonus dice (0, 1, or 2 for intense/dyscrasia)
    """
    resonance = get_resonance(character)

    if not resonance["type"] or resonance["intensity"] == 0:
        return 0

    discipline_name = discipline_name.lower()

    # Map resonance types to disciplines
    resonance_map = {
        "Choleric": ["potence", "celerity"],
        "Melancholic": ["fortitude", "obfuscate"],
        "Phlegmatic": ["auspex", "dominate"],
        "Sanguine": ["presence", "blood_sorcery"]
    }

    # Check if discipline benefits from this resonance
    for res_type, disciplines in resonance_map.items():
        if resonance["type"] == res_type and discipline_name in disciplines:
            # Fleeting = +1, Intense/Dyscrasia = +2
            return 1 if resonance["intensity"] == 1 else 2

    return 0


def feed(character, vessel_type="human", slake=1, resonance_type=None, resonance_intensity=1):
    """
    Character feeds, reducing Hunger and potentially gaining Resonance.

    Args:
        character: Character object
        vessel_type (str): Type of vessel (human, animal, bag)
        slake (int): How much Hunger to reduce (default 1, full feeding can be more)
        resonance_type (str, optional): Resonance type gained
        resonance_intensity (int): Intensity of Resonance (default 1)

    Returns:
        dict: Feeding results
            - hunger_reduced: Amount of Hunger reduced
            - new_hunger: New Hunger level
            - resonance: Resonance gained (if any)
            - message: Narrative message
    """
    old_hunger = get_hunger(character)

    # Apply feeding penalty for Blood Potency (animals/bags are less satisfying)
    bp_bonuses = get_blood_potency_bonuses(character)
    penalty = bp_bonuses["feeding_penalty"]

    if vessel_type in ["animal", "bag"] and penalty > 0:
        # High BP characters can't effectively feed from animals/bags
        if penalty >= slake:
            return {
                "hunger_reduced": 0,
                "new_hunger": old_hunger,
                "resonance": None,
                "message": f"|rYour Blood Potency is too high to feed from {vessel_type}s effectively.|n"
            }
        else:
            slake -= penalty

    # Reduce Hunger
    new_hunger = decrease_hunger(character, slake)
    hunger_reduced = old_hunger - new_hunger

    # Set Resonance (if applicable)
    if resonance_type:
        set_resonance(character, resonance_type, resonance_intensity)
        resonance_msg = f" You gain |y{resonance_type}|n Resonance."
    else:
        clear_resonance(character)
        resonance_msg = ""

    # Build message
    message = f"You feed from the {vessel_type}. "
    message += f"Hunger reduced by {hunger_reduced} (now {new_hunger})."
    message += resonance_msg

    return {
        "hunger_reduced": hunger_reduced,
        "new_hunger": new_hunger,
        "resonance": get_resonance(character) if resonance_type else None,
        "message": message
    }


def can_use_disciplines(character):
    """
    Check if character's Hunger allows discipline use.

    At Hunger 5, most disciplines cannot be used.

    Args:
        character: Character object

    Returns:
        tuple: (bool, str) - (can_use, reason)
    """
    hunger = get_hunger(character)

    if hunger >= 5:
        return (False, "Your Hunger is too high to use most Disciplines safely.")

    return (True, "")


def blood_surge(character):
    """
    Perform a Blood Surge to add bonus dice to a Physical roll.

    Requires a Rouse check. Adds bonus dice based on Blood Potency.

    Args:
        character: Character object

    Returns:
        dict: Blood Surge results
            - bonus_dice: Number of bonus dice added
            - rouse_required: Whether a Rouse check is needed
            - message: Narrative message
    """
    bp_bonuses = get_blood_potency_bonuses(character)
    bonus_dice = bp_bonuses["blood_surge"]

    return {
        "bonus_dice": bonus_dice,
        "rouse_required": True,
        "message": f"You surge your Blood! Add |y{bonus_dice} dice|n to your Physical roll. (Requires Rouse check)"
    }


def mend_damage(character):
    """
    Mend Superficial damage.

    Requires a Rouse check. Heals amount based on Blood Potency.

    Args:
        character: Character object

    Returns:
        dict: Mend results
            - amount_healed: Superficial damage healed
            - rouse_required: Whether a Rouse check is needed
            - message: Narrative message
    """
    bp_bonuses = get_blood_potency_bonuses(character)
    heal_amount = bp_bonuses["mend_amount"]

    superficial = character.db.pools.get("superficial_damage", 0)

    if superficial == 0:
        return {
            "amount_healed": 0,
            "rouse_required": False,
            "message": "You have no Superficial damage to mend."
        }

    actual_healed = min(heal_amount, superficial)
    character.db.pools["superficial_damage"] -= actual_healed

    return {
        "amount_healed": actual_healed,
        "rouse_required": True,
        "message": f"You mend |g{actual_healed}|n Superficial damage. (Requires Rouse check)"
    }
