"""
V:tM Gothic ANSI Color Theme

This module defines the color palette and theming standards for TheBeckoningMU.
All user-facing output should use these constants for consistent gothic atmosphere.

See: THEMING_GUIDE.md for complete aesthetics specification
"""

# ============================================================================
# PRIMARY COLORS (V:tM Gothic Theme)
# ============================================================================

BLOOD_RED = "|r"           # Hunger, damage, warnings
DARK_RED = "|[R"           # Clan names, disciplines
PALE_IVORY = "|w"          # Text, descriptions
SHADOW_GREY = "|x"         # Borders, separators
DEEP_PURPLE = "|m"         # Mystical (Auspex, Blood Sorcery)
MIDNIGHT_BLUE = "|b"       # Night, status, nobility
BONE_WHITE = "|W"          # Headers, emphasis
DECAY_GREEN = "|g"         # Necromancy, decay (Oblivion)
GOLD = "|y"                # Status, boons, highlights

# ============================================================================
# SEMANTIC COLORS (Context-Specific)
# ============================================================================

SUCCESS = "|g"             # Successful actions
FAILURE = "|r"             # Failed actions
MESSY = "|[R|h"            # Messy critical (bright red, hilite)
BESTIAL = "|[r|h"          # Bestial failure (dark red, hilite)
CRITICAL = "|y|h"          # Critical success (gold, hilite)

# ============================================================================
# HUNGER LEVEL COLORS (Gradient from white to red)
# ============================================================================

HUNGER_0 = "|W"            # Sated (white)
HUNGER_1_2 = "|w"          # Peckish/Hungry (pale)
HUNGER_3_4 = "|y"          # Ravenous/Famished (gold)
HUNGER_5 = "|[R|h"         # Starving (bright red, hilite)

def get_hunger_color(hunger_level):
    """
    Returns the appropriate color code for a given Hunger level.

    Args:
        hunger_level (int): Hunger level (0-5)

    Returns:
        str: ANSI color code
    """
    if hunger_level == 0:
        return HUNGER_0
    elif hunger_level in (1, 2):
        return HUNGER_1_2
    elif hunger_level in (3, 4):
        return HUNGER_3_4
    else:  # hunger_level == 5
        return HUNGER_5

# ============================================================================
# RESET CODE
# ============================================================================

RESET = "|n"               # Reset all formatting

# ============================================================================
# BOX DRAWING CHARACTERS
# ============================================================================

# Single line
BOX_H = "─"                # Horizontal
BOX_V = "│"                # Vertical
BOX_TL = "┌"               # Top-left corner
BOX_TR = "┐"               # Top-right corner
BOX_BL = "└"               # Bottom-left corner
BOX_BR = "┘"               # Bottom-right corner
BOX_T = "┬"                # T-junction top
BOX_B = "┴"                # T-junction bottom
BOX_L = "├"                # T-junction left
BOX_R = "┤"                # T-junction right
BOX_X = "┼"                # Cross

# Double line (for headers/emphasis)
DBOX_H = "═"               # Horizontal
DBOX_V = "║"               # Vertical
DBOX_TL = "╔"              # Top-left corner
DBOX_TR = "╗"              # Top-right corner
DBOX_BL = "╚"              # Bottom-left corner
DBOX_BR = "╝"              # Bottom-right corner
DBOX_T = "╦"               # T-junction top
DBOX_B = "╩"               # T-junction bottom
DBOX_L = "╠"               # T-junction left
DBOX_R = "╣"               # T-junction right
DBOX_X = "╬"               # Cross

# ============================================================================
# THEMATIC SYMBOLS
# ============================================================================

# Vampire/Gothic
FLEUR_DE_LIS = "⚜"         # Camarilla symbol
CROWN = "♛"                # Royalty, Prince
QUEEN = "♕"                # Alternative crown
ROSE = "❦"                 # Toreador, romance
COFFIN = "⚰"               # Death
CROSS = "†"                # Faith
CROSS_ALT = "✝"            # Alternative cross

# Status/Power
DIAMOND = "◆"              # Critical success, value
CIRCLE_FILLED = "●"        # Dot filled (traits, successes)
CIRCLE_EMPTY = "○"         # Dot empty (missing traits)
DIAMOND_EMPTY = "◇"        # Empty diamond

# Warning/Danger
WARNING = "⚠"              # Warnings, caution
NO_ENTRY = "⛔"            # Forbidden
LIGHTNING = "⚡"           # Power, Brujah

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def colorize(text, account=None):
    """
    Apply color codes to text, respecting user's color preference.

    Args:
        text (str): Text with ANSI codes
        account (Account): Evennia account object

    Returns:
        str: Colored text or plain text if colors disabled
    """
    if account and hasattr(account.db, 'use_color') and not account.db.use_color:
        # Strip ANSI codes for users with color disabled
        import re
        return re.sub(r'\|[xrRgGbBmMcCyYwW\[\]]|\|h|\|n', '', text)
    return text

def make_header(title, width=65, style="double"):
    """
    Create a themed header box.

    Args:
        title (str): Header text
        width (int): Total width of header
        style (str): "single" or "double"

    Returns:
        str: Formatted header
    """
    if style == "double":
        tl, tr, bl, br = DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR
        h, v = DBOX_H, DBOX_V
        color = DARK_RED
    else:
        tl, tr, bl, br = BOX_TL, BOX_TR, BOX_BL, BOX_BR
        h, v = BOX_H, BOX_V
        color = SHADOW_GREY

    line = h * (width - 2)
    title_line = f" {BONE_WHITE}{title}{color}"
    padding = " " * (width - len(title) - 3)

    return f"""{color}{tl}{line}{tr}
{v}{title_line}{padding}{v}
{bl}{line}{br}{RESET}"""

def make_separator(width=65):
    """
    Create a horizontal separator line.

    Args:
        width (int): Total width

    Returns:
        str: Separator line
    """
    return f"{SHADOW_GREY}{BOX_H * width}{RESET}"

def trait_dots(current, maximum=5, filled_symbol=CIRCLE_FILLED, empty_symbol=CIRCLE_EMPTY):
    """
    Create a visual representation of trait dots.

    Args:
        current (int): Current dots
        maximum (int): Maximum dots
        filled_symbol (str): Symbol for filled dots
        empty_symbol (str): Symbol for empty dots

    Returns:
        str: Dot representation (e.g., "●●●○○")
    """
    filled = filled_symbol * current
    empty = empty_symbol * (maximum - current)
    return f"{filled}{empty}"

# ============================================================================
# DICE SYMBOLS
# ============================================================================

DICE_SUCCESS_NORMAL = f"{BONE_WHITE}{CIRCLE_FILLED}{RESET}"
DICE_CRITICAL_NORMAL = f"{GOLD}{DIAMOND}{RESET}"
DICE_SUCCESS_HUNGER = f"{BLOOD_RED}{CIRCLE_FILLED}{RESET}"
DICE_CRITICAL_HUNGER = f"{MESSY}{DIAMOND}{RESET}"
DICE_FAILURE = f"{SHADOW_GREY}{CIRCLE_EMPTY}{RESET}"
