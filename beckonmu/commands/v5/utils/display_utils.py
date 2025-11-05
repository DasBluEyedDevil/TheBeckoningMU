"""
Display Utility Functions for V5 System

Character sheet formatted to match official V5 character sheet layout
with gothic ANSI theming.

Layout matches the official 2-page V5 character sheet structure:
- Header: Name, Concept, Chronicle, Predator, etc.
- 3-column layout for efficiency
- Attributes grouped vertically (Physical/Social/Mental)
- Skills in compact columns
- Disciplines, Humanity, Advantages sections
"""

from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY, DEEP_PURPLE,
    MIDNIGHT_BLUE, BONE_WHITE, DECAY_GREEN, GOLD, RESET,
    HUNGER_0, HUNGER_1_2, HUNGER_3_4, HUNGER_5,
    get_hunger_color,
    DBOX_H, DBOX_V, DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR,
    BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_L, BOX_R,
    CIRCLE_FILLED, CIRCLE_EMPTY, DIAMOND, FLEUR_DE_LIS
)

from .clan_utils import get_clan, get_clan_info
from .blood_utils import get_hunger, get_blood_potency


def format_character_sheet(character):
    """
    Create character sheet matching official V5 layout with gothic theming.

    Official V5 sheet structure:
    - Top: Name, Concept, Predator, Ambition, etc.
    - Left: Attributes (vertical), Health, Willpower
    - Center: Skills (compact columns), Specialties
    - Right: Disciplines, Humanity (Convictions/Touchstones)
    - Bottom: Advantages, Blood Potency, Experience

    Args:
        character: Character object

    Returns:
        str: Formatted character sheet
    """
    lines = []

    # Gothic header banner
    lines.append(_format_header_banner())
    lines.append("")

    # Character info section (Name, Concept, Chronicle, etc.)
    lines.append(_format_character_info(character))
    lines.append("")

    # Main 3-column layout: Attributes | Skills | Disciplines
    lines.append(_format_main_section(character))
    lines.append("")

    # Bottom section: Advantages, Blood Potency, Experience
    lines.append(_format_bottom_section(character))

    return "\n".join(lines)


def _format_header_banner():
    """Gothic header banner."""
    return f"""{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}
{DBOX_V} {BLOOD_RED}{FLEUR_DE_LIS}{RESET}  {BONE_WHITE}VAMPIRE: THE MASQUERADE{RESET} {SHADOW_GREY}Fifth Edition{RESET}{' ' * 28}{DARK_RED}{DBOX_V}
{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}"""


def _format_character_info(character):
    """Top section: Name, Concept, Chronicle, Predator, Ambition, etc."""
    name = character.key
    vamp = character.db.vampire if hasattr(character.db, 'vampire') else {}

    clan = get_clan(character) or "Unknown"
    generation = vamp.get('generation', 13)
    sire = vamp.get('sire', 'Unknown')
    concept = vamp.get('concept', 'Unknown')
    predator = vamp.get('predator_type', 'Unknown')

    # Chronicle/Ambition could be stored in character.db if needed
    chronicle = "The Beckoning - Athens"
    ambition = vamp.get('ambition', '—')
    desire = vamp.get('desire', '—')

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")

    # Line 1: Name and Clan
    name_display = f"{BONE_WHITE}{name}{RESET}"
    clan_display = f"{DARK_RED}{clan}{RESET}"
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Name:{RESET} {name_display:<40} "
        f"{GOLD}Clan:{RESET} {clan_display:<16} {SHADOW_GREY}{BOX_V}{RESET}"
    )

    # Line 2: Concept and Generation
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Concept:{RESET} {concept:<37} "
        f"{GOLD}Generation:{RESET} {generation:<13} {SHADOW_GREY}{BOX_V}{RESET}"
    )

    # Line 3: Predator and Sire
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Predator:{RESET} {predator:<36} "
        f"{GOLD}Sire:{RESET} {sire:<17} {SHADOW_GREY}{BOX_V}{RESET}"
    )

    # Line 4: Chronicle
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Chronicle:{RESET} {chronicle:<63} {SHADOW_GREY}{BOX_V}{RESET}"
    )

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_main_section(character):
    """
    Main 3-column section matching official sheet:
    | ATTRIBUTES    | SKILLS            | DISCIPLINES    |
    | Health/Will   | Specialties       | Humanity       |
    """
    # Get all data
    attrs_lines = _get_attributes_column(character)
    skills_lines = _get_skills_column(character)
    disciplines_lines = _get_disciplines_column(character)

    # Make all columns same height by padding
    max_height = max(len(attrs_lines), len(skills_lines), len(disciplines_lines))

    attrs_lines += [""] * (max_height - len(attrs_lines))
    skills_lines += [""] * (max_height - len(skills_lines))
    disciplines_lines += [""] * (max_height - len(disciplines_lines))

    # Combine into 3-column layout
    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")

    # Section headers
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}ATTRIBUTES{' ' * 15}"
        f"{BOX_V} {BONE_WHITE}SKILLS{' ' * 21}"
        f"{BOX_V} {BONE_WHITE}DISCIPLINES{' ' * 12}{BOX_V}{RESET}"
    )
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 24}{BOX_R}{BOX_H * 27}{BOX_R}{BOX_H * 24}{BOX_R}{RESET}")

    # Data rows
    for i in range(max_height):
        attr_text = attrs_lines[i] if i < len(attrs_lines) else ""
        skill_text = skills_lines[i] if i < len(skills_lines) else ""
        disc_text = disciplines_lines[i] if i < len(disciplines_lines) else ""

        # Pad each column to proper width (accounting for ANSI codes is tricky, so use fixed padding)
        lines.append(
            f"{SHADOW_GREY}{BOX_V} {attr_text:<32}"
            f"{BOX_V} {skill_text:<35}"
            f"{BOX_V} {disc_text:<32}{BOX_V}{RESET}"
        )

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _get_attributes_column(character):
    """
    Get attributes column (left side).
    Format matches official sheet: vertical grouping by category.
    """
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ["(No attributes set)"]

    attrs = character.db.stats.get('attributes', {})
    pools = character.db.pools if hasattr(character.db, 'pools') else {}

    # Physical
    lines.append(f"{PALE_IVORY}Physical:{RESET}")
    phys = attrs.get('physical', {})
    lines.append(f"  {GOLD}Str{RESET} {_dots(phys.get('strength', 1))}")
    lines.append(f"  {GOLD}Dex{RESET} {_dots(phys.get('dexterity', 1))}")
    lines.append(f"  {GOLD}Sta{RESET} {_dots(phys.get('stamina', 1))}")
    lines.append("")

    # Social
    lines.append(f"{PALE_IVORY}Social:{RESET}")
    soc = attrs.get('social', {})
    lines.append(f"  {GOLD}Cha{RESET} {_dots(soc.get('charisma', 1))}")
    lines.append(f"  {GOLD}Man{RESET} {_dots(soc.get('manipulation', 1))}")
    lines.append(f"  {GOLD}Com{RESET} {_dots(soc.get('composure', 1))}")
    lines.append("")

    # Mental
    lines.append(f"{PALE_IVORY}Mental:{RESET}")
    ment = attrs.get('mental', {})
    lines.append(f"  {GOLD}Int{RESET} {_dots(ment.get('intelligence', 1))}")
    lines.append(f"  {GOLD}Wit{RESET} {_dots(ment.get('wits', 1))}")
    lines.append(f"  {GOLD}Res{RESET} {_dots(ment.get('resolve', 1))}")
    lines.append("")

    # Health tracker
    health = pools.get('health', 0)
    current_health = pools.get('current_health', health)
    superficial = pools.get('superficial_damage', 0)
    aggravated = pools.get('aggravated_damage', 0)

    lines.append(f"{PALE_IVORY}Health:{RESET}")
    health_display = _health_tracker(health, superficial, aggravated)
    lines.append(f"  {health_display}")
    lines.append("")

    # Willpower tracker
    willpower = pools.get('willpower', 0)
    current_willpower = pools.get('current_willpower', willpower)

    lines.append(f"{PALE_IVORY}Willpower:{RESET}")
    willpower_display = _tracker_boxes(current_willpower, willpower)
    lines.append(f"  {willpower_display}")

    return lines


def _get_skills_column(character):
    """
    Get skills column (center).
    Compact display with specialties.
    """
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ["(No skills set)"]

    skills = character.db.stats.get('skills', {})
    specialties = character.db.stats.get('specialties', {})

    # Group by category but display compactly
    categories = [
        ("Physical", skills.get('physical', {})),
        ("Social", skills.get('social', {})),
        ("Mental", skills.get('mental', {}))
    ]

    for cat_name, cat_skills in categories:
        lines.append(f"{PALE_IVORY}{cat_name}:{RESET}")

        # Only show skills with dots
        has_skills = False
        for skill_name, value in sorted(cat_skills.items()):
            if value > 0:
                has_skills = True
                display_name = skill_name.replace('_', ' ').title()[:12]  # Truncate long names
                spec = specialties.get(skill_name, "")
                spec_display = f" ({spec})" if spec else ""

                lines.append(f"  {GOLD}{display_name:<12}{RESET} {_dots(value)}{spec_display}")

        if not has_skills:
            lines.append(f"  {SHADOW_GREY}—{RESET}")

        lines.append("")

    return lines


def _get_disciplines_column(character):
    """
    Get disciplines column (right side).
    Shows disciplines and Humanity/Touchstones.
    """
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ["(No data)"]

    disciplines = character.db.stats.get('disciplines', {})

    # Disciplines
    if disciplines:
        for disc_name, disc_data in sorted(disciplines.items()):
            level = disc_data.get('level', 0)
            display_name = disc_name.replace('_', ' ').title()[:15]
            lines.append(f"{DARK_RED}{display_name}{RESET} {_dots(level)}")
    else:
        lines.append(f"{SHADOW_GREY}No disciplines{RESET}")

    lines.append("")
    lines.append(f"{PALE_IVORY}{'─' * 22}{RESET}")
    lines.append("")

    # Humanity
    vamp = character.db.vampire if hasattr(character.db, 'vampire') else {}
    humanity = vamp.get('humanity', 7)
    lines.append(f"{PALE_IVORY}Humanity:{RESET} {_dots(humanity, 10)}")

    # Stains
    hum_data = character.db.humanity_data if hasattr(character.db, 'humanity_data') else {}
    stains = hum_data.get('stains', 0)
    if stains > 0:
        lines.append(f"{BLOOD_RED}Stains:{RESET} {_dots(stains, 10)}")

    lines.append("")

    # Convictions (first 2)
    convictions = hum_data.get('convictions', [])
    if convictions:
        lines.append(f"{PALE_IVORY}Convictions:{RESET}")
        for conv in convictions[:2]:
            lines.append(f"  {CIRCLE_FILLED} {conv[:18]}")  # Truncate long text

    lines.append("")

    # Touchstones (first 2)
    touchstones = hum_data.get('touchstones', [])
    if touchstones:
        lines.append(f"{PALE_IVORY}Touchstones:{RESET}")
        for ts in touchstones[:2]:
            ts_name = ts.get('name', 'Unknown')[:18]
            lines.append(f"  {CIRCLE_FILLED} {ts_name}")

    return lines


def _format_bottom_section(character):
    """
    Bottom section: Hunger, Blood Potency, Advantages, Experience.
    Matches official sheet bottom sections.
    """
    lines = []

    # Hunger and Blood Potency bar
    lines.append(_format_hunger_blood_potency(character))
    lines.append("")

    # Advantages (Backgrounds, Merits, Flaws) + Experience
    lines.append(_format_advantages_experience(character))

    return "\n".join(lines)


def _format_hunger_blood_potency(character):
    """Hunger and Blood Potency section (prominent display)."""
    vamp = character.db.vampire if hasattr(character.db, 'vampire') else {}
    hunger = vamp.get('hunger', 0)
    bp = vamp.get('blood_potency', 0)

    hunger_color = get_hunger_color(hunger)
    hunger_dots = f"{hunger_color}{CIRCLE_FILLED * hunger}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - hunger)}{RESET}"

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Hunger:{RESET} {hunger_dots}   "
        f"{GOLD}Blood Potency:{RESET} {_dots(bp, 10)}{' ' * 32}{SHADOW_GREY}{BOX_V}{RESET}"
    )

    # Clan Bane and Compulsion
    clan_info = get_clan_info(get_clan(character))
    if clan_info:
        bane = clan_info.get('bane', '')[:60]
        compulsion = clan_info.get('compulsion', '')[:60]
        lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Bane:{RESET} {bane:<70} {SHADOW_GREY}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Compulsion:{RESET} {compulsion:<64} {SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_advantages_experience(character):
    """Advantages and Experience section."""
    advantages = character.db.advantages if hasattr(character.db, 'advantages') else {}
    backgrounds = advantages.get('backgrounds', {})
    merits = advantages.get('merits', {})
    flaws = advantages.get('flaws', {})

    experience = character.db.experience if hasattr(character.db, 'experience') else {}
    current_xp = experience.get('current', 0)
    total_xp = experience.get('total_earned', 0)
    spent_xp = experience.get('total_spent', 0)

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}ADVANTAGES{' ' * 68}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")

    # Backgrounds
    if backgrounds:
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Backgrounds:{RESET}{' ' * 65}{SHADOW_GREY}{BOX_V}{RESET}")
        for bg_name, bg_val in sorted(backgrounds.items())[:5]:  # Show first 5
            display_name = bg_name.replace('_', ' ').title()[:20]
            lines.append(f"{SHADOW_GREY}{BOX_V}   {GOLD}{display_name:<20}{RESET} {_dots(bg_val)}{' ' * 47}{SHADOW_GREY}{BOX_V}{RESET}")

    # Merits
    if merits:
        if backgrounds:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 78}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Merits:{RESET}{' ' * 70}{SHADOW_GREY}{BOX_V}{RESET}")
        for merit_name, merit_val in sorted(merits.items())[:5]:
            display_name = merit_name.replace('_', ' ').title()[:20]
            lines.append(f"{SHADOW_GREY}{BOX_V}   {GOLD}{display_name:<20}{RESET} {_dots(merit_val)}{' ' * 47}{SHADOW_GREY}{BOX_V}{RESET}")

    # Flaws
    if flaws:
        if backgrounds or merits:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 78}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Flaws:{RESET}{' ' * 71}{SHADOW_GREY}{BOX_V}{RESET}")
        for flaw_name, flaw_val in sorted(flaws.items())[:5]:
            display_name = flaw_name.replace('_', ' ').title()[:20]
            lines.append(f"{SHADOW_GREY}{BOX_V}   {BLOOD_RED}{display_name:<20}{RESET} {_dots(flaw_val)}{' ' * 47}{SHADOW_GREY}{BOX_V}{RESET}")

    # Experience
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 78}{BOX_R}{RESET}")
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Experience:{RESET} {current_xp} XP   "
        f"(Total Earned: {total_xp}, Spent: {spent_xp}){' ' * 28}{SHADOW_GREY}{BOX_V}{RESET}"
    )

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _dots(value, maximum=5):
    """Create dot display."""
    return f"{CIRCLE_FILLED * value}{SHADOW_GREY}{CIRCLE_EMPTY * (maximum - value)}{RESET}"


def _tracker_boxes(current, maximum):
    """Create tracker boxes (like Health/Willpower on official sheet)."""
    filled = f"{CIRCLE_FILLED}" * current
    empty = f"{SHADOW_GREY}{CIRCLE_EMPTY}{RESET}" * (maximum - current)
    return f"{filled}{empty}"


def _health_tracker(maximum, superficial=0, aggravated=0):
    """
    Health tracker showing superficial and aggravated damage.
    Official sheet style: boxes with / for superficial, X for aggravated.
    """
    # For text display, use symbols
    agg = f"{BLOOD_RED}X{RESET}" * aggravated
    sup = f"{GOLD}/{RESET}" * superficial
    empty_boxes = maximum - superficial - aggravated
    empty = f"{SHADOW_GREY}{CIRCLE_EMPTY}{RESET}" * empty_boxes

    return f"{agg}{sup}{empty}"


def format_short_sheet(character):
    """
    Compact one-line status display.

    Args:
        character: Character object

    Returns:
        str: Compact character status
    """
    name = character.key
    clan = get_clan(character) or "Unknown"
    vamp = character.db.vampire if hasattr(character.db, 'vampire') else {}
    generation = vamp.get('generation', 13)
    hunger = vamp.get('hunger', 0)

    # Hunger dots
    hunger_color = get_hunger_color(hunger)
    hunger_dots = f"{hunger_color}{CIRCLE_FILLED * hunger}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - hunger)}{RESET}"

    # Health and Willpower
    pools = character.db.pools if hasattr(character.db, 'pools') else {}
    health = pools.get('current_health', pools.get('health', 0))
    willpower = pools.get('current_willpower', pools.get('willpower', 0))

    return (
        f"{BONE_WHITE}{name}{RESET} "
        f"({DARK_RED}{clan}{RESET} Gen {generation}) "
        f"Hunger: {hunger_dots} "
        f"Health: {health} Willpower: {willpower}"
    )
