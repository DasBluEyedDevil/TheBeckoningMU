"""
Display Utility Functions for V5 System

Character sheet formatted to precisely match official V5 character sheet layout.

Official V5 Sheet Structure (in order):
1. TOP: Name, Concept, Chronicle, Ambition, Desire, Predator
2. UPPER LEFT: Attributes (Physical, Social, Mental in 3x3 grid)
3. UPPER CENTER: Skills (Physical, Social, Mental listed vertically)
4. UPPER RIGHT: Disciplines (listed with dots)
5. MIDDLE LEFT: Health, Willpower trackers
6. MIDDLE CENTER: (continuation of Skills if needed)
7. MIDDLE RIGHT: Hunger, Humanity, Blood Potency, Resonance
8. LOWER: Clan (Bane, Compulsion), Convictions, Touchstones, Chronicle Tenets
9. BOTTOM: Advantages (Backgrounds, Merits, Flaws), Total Experience
"""

from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY, DEEP_PURPLE,
    MIDNIGHT_BLUE, BONE_WHITE, DECAY_GREEN, GOLD, VAMPIRE_GOLD, RESET,
    HUNGER_0, HUNGER_1_2, HUNGER_3_4, HUNGER_5,
    get_hunger_color,
    DBOX_H, DBOX_V, DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR,
    BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_L, BOX_R,
    CIRCLE_FILLED, CIRCLE_EMPTY, DIAMOND, FLEUR_DE_LIS
)

from .clan_utils import get_clan, get_clan_info
from .blood_utils import get_hunger, get_blood_potency
from . import social_utils


def format_character_sheet(character):
    """
    Create character sheet matching official V5 layout exactly.

    Args:
        character: Character object

    Returns:
        str: Formatted character sheet
    """
    lines = []

    # Gothic header
    lines.append(_format_header())
    lines.append("")

    # Section 1: Character Info (Name, Concept, Chronicle, etc.)
    lines.append(_format_character_info(character))
    lines.append("")

    # Section 2: ATTRIBUTES (left), SKILLS (center), DISCIPLINES (right)
    lines.append(_format_attributes_skills_disciplines(character))
    lines.append("")

    # Section 3: HEALTH/WILLPOWER (left), [space] (center), HUNGER/HUMANITY/BLOOD (right)
    lines.append(_format_trackers(character))
    lines.append("")

    # Section 4: CLAN (Bane & Compulsion)
    lines.append(_format_clan_section(character))
    lines.append("")

    # Section 4.5: STATUS (Position & Standing)
    status_section = _format_status_section(character)
    if status_section:
        lines.append(status_section)
        lines.append("")

    # Section 5: HUMANITY DETAILS (Convictions & Touchstones)
    lines.append(_format_humanity_details(character))
    lines.append("")

    # Section 6: ADVANTAGES (Backgrounds, Merits, Flaws)
    lines.append(_format_advantages(character))
    lines.append("")

    # Section 6.5: BOONS (Political Favors & Debts)
    boons_section = _format_boons_section(character)
    if boons_section:
        lines.append(boons_section)
        lines.append("")

    # Section 6.6: COTERIE (Group Membership)
    coterie_section = _format_coterie_section(character)
    if coterie_section:
        lines.append(coterie_section)
        lines.append("")

    # Section 7: EXPERIENCE
    lines.append(_format_experience(character))

    return "\n".join(lines)


def _format_header():
    """Gothic header."""
    return f"""{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}
{DBOX_V} {BLOOD_RED}{FLEUR_DE_LIS}{RESET}  {BONE_WHITE}VAMPIRE: THE MASQUERADE{RESET} {SHADOW_GREY}Fifth Edition{RESET}{' ' * 28}{DARK_RED}{DBOX_V}
{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}"""


def _format_character_info(character):
    """Section 1: Character information (matches official sheet top section)."""
    name = character.key
    vamp = character.db.vampire if (hasattr(character.db, 'vampire') and character.db.vampire) else {}

    concept = vamp.get('concept', '—')
    chronicle = vamp.get('chronicle', 'The Beckoning - Athens')
    ambition = vamp.get('ambition', '—')
    desire = vamp.get('desire', '—')
    predator = vamp.get('predator_type', 'Unknown')

    clan = get_clan(character) or "Unknown"
    sire = vamp.get('sire', '—')
    generation = vamp.get('generation', 13)

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Name:{RESET} {BONE_WHITE}{name:<70}{RESET} {SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Concept:{RESET} {concept:<35} {GOLD}Chronicle:{RESET} {chronicle:<22} {SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Ambition:{RESET} {ambition:<34} {GOLD}Desire:{RESET} {desire:<25} {SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Predator:{RESET} {predator:<67} {SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Clan:{RESET} {DARK_RED}{clan:<24}{RESET} {GOLD}Sire:{RESET} {sire:<24} {GOLD}Generation:{RESET} {generation:<8} {SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_attributes_skills_disciplines(character):
    """
    Section 2: Vertically stacked sections (matching official V5 layout)

    ATTRIBUTES (3-column grid: Physical | Social | Mental)
    SKILLS (3-column grid: Physical | Social | Mental)
    DISCIPLINES (horizontal list)

    Official sheet layout:
    - Attributes in 3-column grid (Physical, Social, Mental)
    - Skills in 3-column grid below attributes
    - Disciplines listed horizontally below skills
    """
    lines = []

    # ATTRIBUTES Section
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}ATTRIBUTES{' ' * 66}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
    lines.extend(_build_attributes_grid(character))
    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")
    lines.append("")

    # SKILLS Section
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}SKILLS{' ' * 70}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
    lines.extend(_build_skills_grid(character))
    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")
    lines.append("")

    # DISCIPLINES Section
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}DISCIPLINES{' ' * 64}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
    lines.extend(_build_disciplines_horizontal(character))
    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _build_attributes_grid(character):
    """Build attributes in 3-column grid (Physical | Social | Mental)."""
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        lines.append(f"{SHADOW_GREY}{BOX_V} (No attributes){' ' * 60}{BOX_V}{RESET}")
        return lines

    attrs = character.db.stats.get('attributes', {})
    phys = attrs.get('physical', {})
    soc = attrs.get('social', {})
    ment = attrs.get('mental', {})

    # Category headers
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Physical{' ' * 16}"
        f"{BOX_V} {PALE_IVORY}Social{' ' * 18}"
        f"{BOX_V} {PALE_IVORY}Mental{' ' * 17}{BOX_V}{RESET}"
    )
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 24}{BOX_R}{BOX_H * 24}{BOX_R}{BOX_H * 27}{BOX_R}{RESET}")

    # Row 1: Strength, Charisma, Intelligence
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Strength{RESET}     {_dots(phys.get('strength', 1)):<8}"
        f"{BOX_V} {GOLD}Charisma{RESET}     {_dots(soc.get('charisma', 1)):<8}"
        f"{BOX_V} {GOLD}Intelligence{RESET} {_dots(ment.get('intelligence', 1)):<8}{BOX_V}{RESET}"
    )

    # Row 2: Dexterity, Manipulation, Wits
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Dexterity{RESET}    {_dots(phys.get('dexterity', 1)):<8}"
        f"{BOX_V} {GOLD}Manipulation{RESET} {_dots(soc.get('manipulation', 1)):<8}"
        f"{BOX_V} {GOLD}Wits{RESET}         {_dots(ment.get('wits', 1)):<8}{BOX_V}{RESET}"
    )

    # Row 3: Stamina, Composure, Resolve
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Stamina{RESET}      {_dots(phys.get('stamina', 1)):<8}"
        f"{BOX_V} {GOLD}Composure{RESET}    {_dots(soc.get('composure', 1)):<8}"
        f"{BOX_V} {GOLD}Resolve{RESET}      {_dots(ment.get('resolve', 1)):<8}{BOX_V}{RESET}"
    )

    return lines


def _build_skills_grid(character):
    """Build skills in 3-column grid (Physical | Social | Mental)."""
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        lines.append(f"{SHADOW_GREY}{BOX_V} (No skills){' ' * 64}{BOX_V}{RESET}")
        return lines

    skills = character.db.stats.get('skills', {})
    specialties = character.db.stats.get('specialties', {})

    phys_skills = skills.get('physical', {})
    soc_skills = skills.get('social', {})
    ment_skills = skills.get('mental', {})

    # Get lists of skills with values > 0
    phys_list = [(name, val, specialties.get(name, ""))
                 for name, val in sorted(phys_skills.items()) if val > 0]
    soc_list = [(name, val, specialties.get(name, ""))
                for name, val in sorted(soc_skills.items()) if val > 0]
    ment_list = [(name, val, specialties.get(name, ""))
                 for name, val in sorted(ment_skills.items()) if val > 0]

    # Category headers
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Physical{' ' * 16}"
        f"{BOX_V} {PALE_IVORY}Social{' ' * 18}"
        f"{BOX_V} {PALE_IVORY}Mental{' ' * 17}{BOX_V}{RESET}"
    )
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 24}{BOX_R}{BOX_H * 24}{BOX_R}{BOX_H * 27}{BOX_R}{RESET}")

    # Determine max rows needed
    max_rows = max(len(phys_list) if phys_list else 1,
                   len(soc_list) if soc_list else 1,
                   len(ment_list) if ment_list else 1)

    # Build rows
    for i in range(max_rows):
        # Physical column
        if i < len(phys_list):
            name, val, spec = phys_list[i]
            display_name = name.replace('_', ' ').title()
            spec_str = f"({spec[:5]})" if spec else ""
            phys_cell = f"{GOLD}{display_name:<11}{RESET} {_dots(val)} {spec_str}"
        elif i == 0:
            phys_cell = f"{SHADOW_GREY}—{RESET}"
        else:
            phys_cell = ""

        # Social column
        if i < len(soc_list):
            name, val, spec = soc_list[i]
            display_name = name.replace('_', ' ').title()
            spec_str = f"({spec[:5]})" if spec else ""
            soc_cell = f"{GOLD}{display_name:<11}{RESET} {_dots(val)} {spec_str}"
        elif i == 0:
            soc_cell = f"{SHADOW_GREY}—{RESET}"
        else:
            soc_cell = ""

        # Mental column
        if i < len(ment_list):
            name, val, spec = ment_list[i]
            display_name = name.replace('_', ' ').title()
            spec_str = f"({spec[:5]})" if spec else ""
            ment_cell = f"{GOLD}{display_name:<11}{RESET} {_dots(val)} {spec_str}"
        elif i == 0:
            ment_cell = f"{SHADOW_GREY}—{RESET}"
        else:
            ment_cell = ""

        lines.append(
            f"{SHADOW_GREY}{BOX_V} {phys_cell:<31}"
            f"{BOX_V} {soc_cell:<31}"
            f"{BOX_V} {ment_cell:<34}{BOX_V}{RESET}"
        )

    return lines


def _build_disciplines_horizontal(character):
    """Build disciplines in horizontal layout."""
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        lines.append(f"{SHADOW_GREY}{BOX_V} (No disciplines){' ' * 60}{BOX_V}{RESET}")
        return lines

    disciplines = character.db.stats.get('disciplines', {})

    if not disciplines:
        lines.append(f"{SHADOW_GREY}{BOX_V} {SHADOW_GREY}(None){' ' * 71}{BOX_V}{RESET}")
    else:
        # Display disciplines in rows, 2 per row
        disc_items = sorted(disciplines.items())
        for i in range(0, len(disc_items), 2):
            disc1_name, disc1_data = disc_items[i]
            disc1_level = disc1_data.get('level', 0)
            disc1_display = disc1_name.replace('_', ' ').title()

            left_cell = f"{DARK_RED}{disc1_display:<18}{RESET}{_dots(disc1_level)}"

            if i + 1 < len(disc_items):
                disc2_name, disc2_data = disc_items[i + 1]
                disc2_level = disc2_data.get('level', 0)
                disc2_display = disc2_name.replace('_', ' ').title()
                right_cell = f"{DARK_RED}{disc2_display:<18}{RESET}{_dots(disc2_level)}"
            else:
                right_cell = ""

            lines.append(
                f"{SHADOW_GREY}{BOX_V} {left_cell:<36}{BOX_V} {right_cell:<38}{BOX_V}{RESET}"
            )

    return lines


def _format_trackers(character):
    """
    Section 3: Trackers
    HEALTH & WILLPOWER (left) | [empty] (center) | HUNGER, HUMANITY, BLOOD POTENCY (right)
    """
    tracker_left = _build_health_willpower(character)
    tracker_right = _build_hunger_humanity_blood(character)

    # Pad to same height
    max_height = max(len(tracker_left), len(tracker_right))
    tracker_left += [""] * (max_height - len(tracker_left))
    tracker_right += [""] * (max_height - len(tracker_right))

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")

    for i in range(max_height):
        left_line = tracker_left[i] if i < len(tracker_left) else ""
        right_line = tracker_right[i] if i < len(tracker_right) else ""

        lines.append(
            f"{SHADOW_GREY}{BOX_V} {left_line:<50}"
            f"{BOX_V} {right_line:<24}{BOX_V}{RESET}"
        )

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _build_health_willpower(character):
    """Build Health and Willpower trackers."""
    lines = []

    pools = character.db.pools or {}

    # Health
    health = pools.get('health', 0)
    superficial = pools.get('superficial_damage', 0)
    aggravated = pools.get('aggravated_damage', 0)

    lines.append(f"{BONE_WHITE}HEALTH{RESET}")
    health_display = _health_tracker(health, superficial, aggravated)
    lines.append(f"  {health_display}")
    lines.append("")

    # Willpower
    willpower = pools.get('willpower', 0)
    current_willpower = pools.get('current_willpower', willpower)

    lines.append(f"{BONE_WHITE}WILLPOWER{RESET}")
    willpower_display = _tracker_boxes(current_willpower, willpower)
    lines.append(f"  {willpower_display}")

    return lines


def _build_hunger_humanity_blood(character):
    """Build Hunger, Humanity, and Blood Potency section (right side)."""
    lines = []

    vamp = character.db.vampire or {}

    # Hunger
    hunger = vamp.get('hunger', 0)
    hunger_color = get_hunger_color(hunger)
    lines.append(f"{BONE_WHITE}HUNGER{RESET}")
    hunger_display = f"{hunger_color}{CIRCLE_FILLED * hunger}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - hunger)}{RESET}"
    lines.append(f"  {hunger_display}")
    lines.append("")

    # Humanity
    humanity = vamp.get('humanity', 7)
    lines.append(f"{BONE_WHITE}HUMANITY{RESET}")
    lines.append(f"  {_dots(humanity, 10)}")

    # Stains
    hum_data = character.db.humanity_data or {}
    stains = hum_data.get('stains', 0)
    if stains > 0:
        lines.append(f"  {BLOOD_RED}Stains:{RESET} {_dots(stains, 10)}")
    lines.append("")

    # Blood Potency
    bp = vamp.get('blood_potency', 0)
    lines.append(f"{BONE_WHITE}BLOOD POTENCY{RESET}")
    lines.append(f"  {_dots(bp, 10)}")
    lines.append("")

    # Blood Resonance
    current_res = vamp.get('current_resonance', None)
    res_intensity = vamp.get('resonance_intensity', 0)
    if current_res and res_intensity > 0:
        intensity_names = ["None", "Fleeting", "Intense", "Dyscrasia"]
        intensity_str = intensity_names[res_intensity] if res_intensity < len(intensity_names) else "Unknown"
        res_color = BLOOD_RED if res_intensity >= 2 else GOLD
        lines.append(f"{BONE_WHITE}RESONANCE{RESET}")
        lines.append(f"  {res_color}{current_res}{RESET} ({intensity_str})")

    return lines


def _format_clan_section(character):
    """Section 4: Clan with Bane and Compulsion."""
    clan = get_clan(character) or "Unknown"
    clan_info = get_clan_info(clan)

    if not clan_info:
        return ""

    bane = clan_info.get('bane', '—')
    compulsion = clan_info.get('compulsion', '—')

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}CLAN:{RESET} {DARK_RED}{clan:<69}{RESET} {SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")

    # Bane (wrap if needed)
    bane_wrapped = _wrap_text(bane, 70)
    for line in bane_wrapped:
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Bane:{RESET} {line:<71} {SHADOW_GREY}{BOX_V}{RESET}")
        if line == bane_wrapped[0]:  # Only show label on first line
            pass

    # Compulsion (wrap if needed)
    comp_wrapped = _wrap_text(compulsion, 70)
    for i, line in enumerate(comp_wrapped):
        label = f"{GOLD}Compulsion:{RESET}" if i == 0 else " " * 11
        lines.append(f"{SHADOW_GREY}{BOX_V} {label} {line:<65} {SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_status_section(character):
    """Section 4.5: Status (Position & Standing in Kindred Society)."""
    try:
        from beckonmu.status.utils import get_character_status
    except ImportError:
        # Status system not installed/migrated yet
        return ""

    char_status = get_character_status(character)

    if not char_status:
        return ""

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}STATUS{RESET}{' ' * 70}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")

    # Total Status
    total = char_status.total_status
    status_dots = f"{GOLD}{CIRCLE_FILLED * total}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - total)}{RESET}"

    breakdown_parts = []
    if char_status.earned_status > 0:
        breakdown_parts.append(f"Earned: {char_status.earned_status}")
    if char_status.position_status > 0:
        breakdown_parts.append(f"Position: {char_status.position_status}")
    if char_status.temporary_status != 0:
        breakdown_parts.append(f"Temporary: {char_status.temporary_status:+d}")

    breakdown = f" ({', '.join(breakdown_parts)})" if breakdown_parts else ""

    lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Total:{RESET} {status_dots} ({total}){breakdown:<40} {SHADOW_GREY}{BOX_V}{RESET}")

    # Position
    if char_status.position:
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Position:{RESET} {GOLD}{char_status.position.name:<60}{RESET} {SHADOW_GREY}{BOX_V}{RESET}")

    # Sect
    lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Sect:{RESET} {char_status.sect:<66} {SHADOW_GREY}{BOX_V}{RESET}")

    # Mechanical bonus
    bonus = char_status.get_status_bonus()
    if bonus > 0:
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Social Bonus:{RESET} +{bonus} dice{'':58} {SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_humanity_details(character):
    """Section 5: Convictions and Touchstones."""
    hum_data = character.db.humanity_data or {}
    convictions = hum_data.get('convictions', [])
    touchstones = hum_data.get('touchstones', [])

    # Skip if no data
    if not convictions and not touchstones:
        return ""

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}CONVICTIONS & TOUCHSTONES{' ' * 51}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")

    # Convictions
    if convictions:
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Convictions:{RESET}{' ' * 65}{SHADOW_GREY}{BOX_V}{RESET}")
        for conv in convictions:
            conv_text = conv[:70]  # Truncate if too long
            lines.append(f"{SHADOW_GREY}{BOX_V}   {CIRCLE_FILLED} {conv_text:<72} {SHADOW_GREY}{BOX_V}{RESET}")

    # Touchstones
    if touchstones:
        if convictions:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 78}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Touchstones:{RESET}{' ' * 65}{SHADOW_GREY}{BOX_V}{RESET}")
        for ts in touchstones:
            ts_name = ts.get('name', 'Unknown')[:70]
            lines.append(f"{SHADOW_GREY}{BOX_V}   {CIRCLE_FILLED} {ts_name:<72} {SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_advantages(character):
    """Section 6: Advantages (Backgrounds, Merits, Flaws)."""
    advantages = character.db.advantages or {}
    backgrounds = advantages.get('backgrounds', {})
    merits = advantages.get('merits', {})
    flaws = advantages.get('flaws', {})

    # Skip if all empty
    if not backgrounds and not merits and not flaws:
        return ""

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}ADVANTAGES{' ' * 68}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")

    # Backgrounds
    if backgrounds:
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Backgrounds:{RESET}{' ' * 65}{SHADOW_GREY}{BOX_V}{RESET}")
        for bg_name, bg_val in sorted(backgrounds.items()):
            display_name = bg_name.replace('_', ' ').title()
            lines.append(f"{SHADOW_GREY}{BOX_V}   {GOLD}{display_name:<30}{RESET} {_dots(bg_val)}{' ' * 36}{SHADOW_GREY}{BOX_V}{RESET}")

    # Merits
    if merits:
        if backgrounds:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 78}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Merits:{RESET}{' ' * 70}{SHADOW_GREY}{BOX_V}{RESET}")
        for merit_name, merit_val in sorted(merits.items()):
            display_name = merit_name.replace('_', ' ').title()
            lines.append(f"{SHADOW_GREY}{BOX_V}   {GOLD}{display_name:<30}{RESET} {_dots(merit_val)}{' ' * 36}{SHADOW_GREY}{BOX_V}{RESET}")

    # Flaws
    if flaws:
        if backgrounds or merits:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 78}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Flaws:{RESET}{' ' * 71}{SHADOW_GREY}{BOX_V}{RESET}")
        for flaw_name, flaw_val in sorted(flaws.items()):
            display_name = flaw_name.replace('_', ' ').title()
            lines.append(f"{SHADOW_GREY}{BOX_V}   {BLOOD_RED}{display_name:<30}{RESET} {_dots(flaw_val)}{' ' * 36}{SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_boons_section(character):
    """Section 6.5: Boons (Political Favors & Debts)."""
    try:
        from beckonmu.boons.utils import get_or_create_ledger
    except ImportError:
        # Boons system not installed/migrated yet
        return ""

    ledger = get_or_create_ledger(character)

    # Only show if there are boons
    if ledger.total_debt_weight == 0 and ledger.total_credit_weight == 0:
        return ""

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}BOONS{RESET}{' ' * 71}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")

    # Debts
    debts = []
    if ledger.life_owed > 0:
        debts.append(f"Life: {ledger.life_owed}")
    if ledger.blood_owed > 0:
        debts.append(f"Blood: {ledger.blood_owed}")
    if ledger.major_owed > 0:
        debts.append(f"Major: {ledger.major_owed}")
    if ledger.minor_owed > 0:
        debts.append(f"Minor: {ledger.minor_owed}")
    if ledger.trivial_owed > 0:
        debts.append(f"Trivial: {ledger.trivial_owed}")

    debt_str = ", ".join(debts) if debts else "None"
    lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Debts:{RESET} {debt_str} (Weight: {ledger.total_debt_weight}){'':30} {SHADOW_GREY}{BOX_V}{RESET}")

    # Credits
    credits = []
    if ledger.life_held > 0:
        credits.append(f"Life: {ledger.life_held}")
    if ledger.blood_held > 0:
        credits.append(f"Blood: {ledger.blood_held}")
    if ledger.major_held > 0:
        credits.append(f"Major: {ledger.major_held}")
    if ledger.minor_held > 0:
        credits.append(f"Minor: {ledger.minor_held}")
    if ledger.trivial_held > 0:
        credits.append(f"Trivial: {ledger.trivial_held}")

    credit_str = ", ".join(credits) if credits else "None"
    lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Credits:{RESET} {credit_str} (Weight: {ledger.total_credit_weight}){'':28} {SHADOW_GREY}{BOX_V}{RESET}")

    # Net position
    if ledger.net_weight > 0:
        net_str = f"{GOLD}+{ledger.net_weight} (In credit){RESET}"
    elif ledger.net_weight < 0:
        net_str = f"{BLOOD_RED}{ledger.net_weight} (In debt){RESET}"
    else:
        net_str = f"{SHADOW_GREY}Balanced{RESET}"

    lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Net:{RESET} {net_str}{'':50} {SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_coterie_section(character):
    """Section 6.6: Coterie (Group Membership)."""
    coterie = social_utils.get_coterie_info(character)

    if not coterie:
        return ""

    role = social_utils.get_character_role(character)

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}COTERIE{RESET}{' ' * 70}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")

    # Name and role
    coterie_name = coterie.get('name', 'Unknown')
    role_display = role.capitalize() if role else "Member"
    role_color = DARK_RED if role == 'leader' else GOLD if role == 'lieutenant' else PALE_IVORY

    lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Name:{RESET} {DARK_RED}{coterie_name:<69}{RESET} {SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Your Role:{RESET} {role_color}{role_display:<65}{RESET} {SHADOW_GREY}{BOX_V}{RESET}")

    # Resources (if leader or lieutenant)
    if role in ['leader', 'lieutenant']:
        resources = coterie.get('resources', {})
        if any(resources.values()):
            lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
            lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Resources:{RESET}{' ' * 65}{SHADOW_GREY}{BOX_V}{RESET}")

            resource_display = []
            for res_type in ['domain', 'haven', 'herd', 'contacts']:
                value = resources.get(res_type, 0)
                if value > 0:
                    resource_display.append(f"{res_type.capitalize()}: {value}")

            if resource_display:
                resource_str = ", ".join(resource_display)
                lines.append(f"{SHADOW_GREY}{BOX_V}   {GOLD}{resource_str:<73}{RESET} {SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_experience(character):
    """Section 7: Experience."""
    experience = character.db.experience or {}
    current_xp = experience.get('current', 0)
    total_xp = experience.get('total_earned', 0)
    spent_xp = experience.get('total_spent', 0)

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}TOTAL EXPERIENCE{RESET}{' ' * 61}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Current:{RESET} {current_xp} XP   "
        f"{GOLD}Earned:{RESET} {total_xp}   "
        f"{GOLD}Spent:{RESET} {spent_xp}{' ' * 30}{SHADOW_GREY}{BOX_V}{RESET}"
    )
    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _dots(value, maximum=5):
    """Create dot display."""
    return f"{CIRCLE_FILLED * value}{SHADOW_GREY}{CIRCLE_EMPTY * (maximum - value)}{RESET}"


def _tracker_boxes(current, maximum):
    """Create tracker boxes for Health/Willpower."""
    filled = f"{CIRCLE_FILLED}" * current
    empty = f"{SHADOW_GREY}{CIRCLE_EMPTY}{RESET}" * (maximum - current)
    return f"{filled}{empty}"


def _health_tracker(maximum, superficial=0, aggravated=0):
    """
    Health tracker with damage types.
    X = Aggravated, / = Superficial, ○ = Empty
    """
    agg = f"{BLOOD_RED}X{RESET}" * aggravated
    sup = f"{GOLD}/{RESET}" * superficial
    empty_boxes = maximum - superficial - aggravated
    empty = f"{SHADOW_GREY}{CIRCLE_EMPTY}{RESET}" * max(0, empty_boxes)

    return f"{agg}{sup}{empty}"


def _wrap_text(text, width):
    """Simple text wrapping."""
    if len(text) <= width:
        return [text]

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def format_short_sheet(character):
    """Compact one-line status display."""
    name = character.key
    clan = get_clan(character) or "Unknown"
    vamp = character.db.vampire or {}
    generation = vamp.get('generation', 13)
    hunger = vamp.get('hunger', 0)

    hunger_color = get_hunger_color(hunger)
    hunger_dots = f"{hunger_color}{CIRCLE_FILLED * hunger}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - hunger)}{RESET}"

    pools = character.db.pools or {}
    health = pools.get('current_health', pools.get('health', 0))
    willpower = pools.get('current_willpower', pools.get('willpower', 0))

    return (
        f"{BONE_WHITE}{name}{RESET} "
        f"({DARK_RED}{clan}{RESET} Gen {generation}) "
        f"Hunger: {hunger_dots} "
        f"Health: {health} Willpower: {willpower}"
    )
