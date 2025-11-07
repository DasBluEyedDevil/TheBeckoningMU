"""
V5 Dice Rolling Engine (Skeleton)

This module will contain the core dice rolling mechanics for V5:
- Normal dice pools (d10, success on 6+, critical on 10)
- Hunger dice (replace normal dice based on Hunger level)
- Rouse checks (single d10 vs difficulty 6)
- Messy Criticals (paired 10s including Hunger dice)
- Bestial Failures (total failure with Hunger dice)

FULL IMPLEMENTATION: Phase 5 (Dice Rolling Engine)

This skeleton defines the API and basic structure only.
See V5_REFERENCE_DATABASE.md for complete dice mechanics.
"""

import random
from typing import Dict, List, Tuple, Optional


class DiceResult:
    """
    Represents the result of a dice roll.

    Attributes:
        normal_dice (List[int]): Results of normal dice (1-10)
        hunger_dice (List[int]): Results of Hunger dice (1-10)
        successes (int): Total successes (6+ on any die)
        criticals (int): Number of critical pairs (pairs of 10s)
        is_messy (bool): True if any Hunger die rolled a 10 in a critical pair
        is_bestial (bool): True if total failure with Hunger dice present
        margin (int): Successes minus difficulty
    """

    def __init__(
        self,
        normal_dice: List[int],
        hunger_dice: List[int],
        difficulty: int = 0
    ):
        self.normal_dice = normal_dice
        self.hunger_dice = hunger_dice
        self.difficulty = difficulty

        # Calculate successes (6+ on any die)
        self.normal_successes = sum(1 for d in normal_dice if d >= 6)
        self.hunger_successes = sum(1 for d in hunger_dice if d >= 6)
        self.successes = self.normal_successes + self.hunger_successes

        # Calculate criticals (pairs of 10s)
        normal_tens = sum(1 for d in normal_dice if d == 10)
        hunger_tens = sum(1 for d in hunger_dice if d == 10)
        total_tens = normal_tens + hunger_tens
        self.criticals = total_tens // 2  # Each pair = 1 critical (+2 successes)

        # Messy Critical: At least one pair includes a Hunger die
        self.is_messy = (self.criticals > 0) and (hunger_tens > 0)

        # Bestial Failure: Total failure (0 successes) with Hunger dice present
        self.is_bestial = (self.successes == 0) and (len(hunger_dice) > 0)

        # Margin: Successes (including critical bonuses) minus difficulty
        total_successes_with_crits = self.successes + (self.criticals * 2)
        self.margin = total_successes_with_crits - difficulty

    def is_success(self) -> bool:
        """Returns True if the roll meets or exceeds difficulty."""
        return self.margin >= 0

    def is_critical_success(self) -> bool:
        """Returns True if the roll has any critical pairs."""
        return self.criticals > 0

    def __repr__(self):
        return (
            f"DiceResult(normal={self.normal_dice}, hunger={self.hunger_dice}, "
            f"successes={self.successes}, criticals={self.criticals}, "
            f"messy={self.is_messy}, bestial={self.is_bestial})"
        )


def roll_pool(
    pool: int,
    hunger: int = 0,
    difficulty: int = 0,
    willpower: bool = False
) -> DiceResult:
    """
    Roll a dice pool with optional Hunger dice.

    Args:
        pool (int): Total dice in the pool
        hunger (int): Hunger level (0-5), determines how many dice are Hunger dice
        difficulty (int): Difficulty of the roll (number of successes needed)
        willpower (bool): If True, add +3 dice to the pool (re-roll once per scene)

    Returns:
        DiceResult: Object containing roll results and analysis

    Implementation Note:
        This is a SKELETON. Full implementation in Phase 5.
        Currently returns random results for testing.
    """
    # Apply willpower bonus
    if willpower:
        pool += 3

    # Determine how many dice are Hunger dice
    # Hunger dice replace normal dice, up to the pool size
    num_hunger_dice = min(hunger, pool)
    num_normal_dice = pool - num_hunger_dice

    # Roll dice (SKELETON: just random for now)
    normal_dice = [random.randint(1, 10) for _ in range(num_normal_dice)]
    hunger_dice = [random.randint(1, 10) for _ in range(num_hunger_dice)]

    # Create and return result
    return DiceResult(normal_dice, hunger_dice, difficulty)


def rouse_check(blood_potency: int = 0) -> Tuple[bool, int]:
    """
    Perform a Rouse check to activate disciplines or powers.

    A Rouse check is a single d10 roll:
    - Success (6+): No Hunger increase
    - Failure (1-5): Hunger increases by 1

    Blood Potency may allow re-rolls (see v5_data.py BLOOD_POTENCY table).

    Args:
        blood_potency (int): Character's Blood Potency (0-10)

    Returns:
        Tuple[bool, int]: (success, die_result)

    Implementation Note:
        This is a SKELETON. Full implementation in Phase 6 (Blood Systems).
        Currently returns random result for testing.
    """
    die_result = random.randint(1, 10)
    success = die_result >= 6

    # TODO Phase 6: Implement Blood Potency re-rolls
    # bp_data = BLOOD_POTENCY[blood_potency]
    # rerolls_available = bp_data['rouse_reroll']

    return (success, die_result)


def format_dice_result(result: DiceResult, character_name: str = "You") -> str:
    """
    Format a DiceResult as themed output using ansi_theme.py.

    Args:
        result (DiceResult): The dice roll result to format
        character_name (str): Name of the character rolling

    Returns:
        str: Formatted output with ANSI colors and symbols

    Implementation Note:
        This is a SKELETON. Full implementation in Phase 5.
        Will use THEMING_GUIDE.md specifications for dice display.
    """
    # TODO Phase 5: Import ansi_theme constants
    # from beckonmu.world.ansi_theme import (
    #     DICE_SUCCESS_NORMAL, DICE_CRITICAL_NORMAL,
    #     DICE_SUCCESS_HUNGER, DICE_CRITICAL_HUNGER,
    #     DICE_FAILURE, MESSY_CRITICAL_BANNER, BESTIAL_FAILURE_BANNER
    # )

    output = f"{character_name} rolls {len(result.normal_dice + result.hunger_dice)} dice...\n"
    output += f"Successes: {result.successes}\n"

    if result.is_messy:
        output += "*** MESSY CRITICAL! ***\n"
    elif result.is_bestial:
        output += "*** BESTIAL FAILURE! ***\n"
    elif result.is_critical_success():
        output += "*** CRITICAL SUCCESS! ***\n"

    return output


def calculate_contested_roll(
    attacker_result: DiceResult,
    defender_result: DiceResult
) -> Dict[str, any]:
    """
    Calculate the outcome of a contested roll (attacker vs defender).

    In contested rolls, both parties roll and compare margins.
    The higher margin wins. Ties go to the defender.

    Args:
        attacker_result (DiceResult): Attacker's roll
        defender_result (DiceResult): Defender's roll

    Returns:
        Dict: Contains 'winner', 'margin_difference', and special outcomes

    Implementation Note:
        This is a SKELETON. Full implementation in Phase 10 (Combat).
    """
    # TODO Phase 10: Full contested roll logic
    if attacker_result.margin > defender_result.margin:
        return {
            "winner": "attacker",
            "margin_difference": attacker_result.margin - defender_result.margin
        }
    else:
        return {
            "winner": "defender",
            "margin_difference": defender_result.margin - attacker_result.margin
        }


# ============================================================================
# FUTURE FUNCTIONS (Defined in later phases)
# ============================================================================

def apply_discipline_modifiers(pool: int, discipline: str, level: int) -> int:
    """
    Apply discipline-based modifiers to a dice pool.
    IMPLEMENTATION: Phase 8 (Discipline Framework)
    """
    # TODO Phase 8
    return pool


def check_frenzy(
    character,
    trigger: str,
    difficulty: int = 3
) -> Tuple[bool, Optional[str]]:
    """
    Check if a character resists frenzy.
    IMPLEMENTATION: Phase 11 (Humanity/Touchstones)
    """
    # TODO Phase 11
    return (True, None)


def apply_hunger_penalties(pool: int, hunger: int) -> int:
    """
    Apply penalties to dice pool based on Hunger level (if any).
    IMPLEMENTATION: Phase 6 (Blood Systems)

    Note: V5 doesn't have direct Hunger penalties to pools,
    but some powers or situations might impose them.
    """
    # TODO Phase 6
    return pool
