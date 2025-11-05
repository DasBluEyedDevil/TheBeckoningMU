"""
Display Utility Functions for V5 System

Provides formatting functions for character sheets, dice rolls, and other
user-facing displays using the gothic V:tM theme.

Uses ansi_theme.py color constants and box-drawing characters for
consistent atmospheric presentation.
"""

from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY, DEEP_PURPLE,
    MIDNIGHT_BLUE, BONE_WHITE, DECAY_GREEN, GOLD, RESET,
    HUNGER_0, HUNGER_1_2, HUNGER_3_4, HUNGER_5,
    get_hunger_color,
    DBOX_H, DBOX_V, DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR, DBOX_L, DBOX_R,
    BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_L, BOX_R,
    CIRCLE_FILLED, CIRCLE_EMPTY, DIAMOND, FLEUR_DE_LIS, CROWN,
    make_header, make_separator, trait_dots
)

from .clan_utils import get_clan, get_clan_info
from .blood_utils import get_hunger, format_hunger_display, get_blood_potency


def format_character_sheet(character):
    """
    Create a comprehensive, themed character sheet.

    Args:
        character: Character object

    Returns:
        str: Fully formatted character sheet
    """
    lines = []

    # Header
    lines.append(_format_sheet_header(character))
    lines.append("")

    # Vampire vitals section
    lines.append(_format_vampire_section(character))
    lines.append("")

    # Attributes section
    lines.append(_format_attributes_section(character))
    lines.append("")

    # Skills section
    lines.append(_format_skills_section(character))
    lines.append("")

    # Disciplines section
    lines.append(_format_disciplines_section(character))
    lines.append("")

    # Advantages section (backgrounds, merits, flaws)
    lines.append(_format_advantages_section(character))
    lines.append("")

    # Humanity section (convictions, touchstones)
    lines.append(_format_humanity_section(character))
    lines.append("")

    # Footer
    lines.append(_format_sheet_footer(character))

    return "\n".join(lines)


def _format_sheet_header(character):
    """Create gothic header for character sheet."""
    name = character.key
    clan = get_clan(character) or "Unknown"

    header = f"{DARK_RED}{DBOX_TL}{DBOX_H * 68}{DBOX_TR}{RESET}\n"
    header += f"{DARK_RED}{DBOX_V}  {BLOOD_RED}{FLEUR_DE_LIS}  {BONE_WHITE}T H E   B E C K O N I N G{RESET}  {SHADOW_GREY}-  Character Dossier{' ' * 18}{DARK_RED}{DBOX_V}{RESET}\n"
    header += f"{DARK_RED}{DBOX_BL}{DBOX_H * 68}{DBOX_BR}{RESET}\n"
    header += f"\n"
    header += f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}\n"
    header += f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}{name:<30}{RESET}  {PALE_IVORY}Clan:{RESET} {DARK_RED}{clan:<26}{SHADOW_GREY}{BOX_V}{RESET}\n"
    header += f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}"

    return header


def _format_vampire_section(character):
    """Format vampire vitals (generation, blood potency, hunger, humanity)."""
    if not hasattr(character.db, 'vampire') or not character.db.vampire:
        return ""

    vamp = character.db.vampire
    generation = vamp.get('generation', 13)
    bp = vamp.get('blood_potency', 0)
    hunger = vamp.get('hunger', 0)
    humanity = vamp.get('humanity', 7)
    predator = vamp.get('predator_type', 'Not Set')

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}VAMPIRE VITALS{' ' * 54}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")

    # Line 1: Generation, Blood Potency, Humanity
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Generation:{RESET} {generation:<3}  "
        f"{PALE_IVORY}Blood Potency:{RESET} {bp:<2}  "
        f"{PALE_IVORY}Humanity:{RESET} {humanity:<2}  "
        f"{PALE_IVORY}Predator:{RESET} {predator:<15} {SHADOW_GREY}{BOX_V}{RESET}"
    )

    # Line 2: Hunger bar
    hunger_display = format_hunger_display(character, show_numeric=False)
    lines.append(f"{SHADOW_GREY}{BOX_V} {hunger_display:<77}{SHADOW_GREY}{BOX_V}{RESET}")

    # Clan info (bane and compulsion)
    clan_info = get_clan_info(get_clan(character))
    if clan_info:
        lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")
        bane = clan_info.get('bane', 'Unknown')
        compulsion = clan_info.get('compulsion', 'Unknown')

        # Word wrap long text
        bane_wrapped = _wrap_text(f"{GOLD}Bane:{RESET} {bane}", 64)
        comp_wrapped = _wrap_text(f"{GOLD}Compulsion:{RESET} {compulsion}", 64)

        for line in bane_wrapped:
            lines.append(f"{SHADOW_GREY}{BOX_V} {line:<77}{SHADOW_GREY}{BOX_V}{RESET}")
        for line in comp_wrapped:
            lines.append(f"{SHADOW_GREY}{BOX_V} {line:<77}{SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_attributes_section(character):
    """Format attributes display."""
    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ""

    attrs = character.db.stats.get('attributes', {})

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}ATTRIBUTES{' ' * 57}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")

    # Physical
    phys = attrs.get('physical', {})
    str_val = phys.get('strength', 1)
    dex_val = phys.get('dexterity', 1)
    sta_val = phys.get('stamina', 1)

    lines.append(
        f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Physical{RESET}   "
        f"{GOLD}Strength{RESET} {trait_dots(str_val)} {str_val}  "
        f"{GOLD}Dexterity{RESET} {trait_dots(dex_val)} {dex_val}  "
        f"{GOLD}Stamina{RESET} {trait_dots(sta_val)} {sta_val}  "
        f"{SHADOW_GREY}{BOX_V}{RESET}"
    )

    # Social
    soc = attrs.get('social', {})
    cha_val = soc.get('charisma', 1)
    man_val = soc.get('manipulation', 1)
    com_val = soc.get('composure', 1)

    lines.append(
        f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Social{RESET}     "
        f"{GOLD}Charisma{RESET} {trait_dots(cha_val)} {cha_val}  "
        f"{GOLD}Manipulation{RESET} {trait_dots(man_val)} {man_val}  "
        f"{GOLD}Composure{RESET} {trait_dots(com_val)} {com_val}  "
        f"{SHADOW_GREY}{BOX_V}{RESET}"
    )

    # Mental
    ment = attrs.get('mental', {})
    int_val = ment.get('intelligence', 1)
    wit_val = ment.get('wits', 1)
    res_val = ment.get('resolve', 1)

    lines.append(
        f"{SHADOW_GREY}{BOX_V} {PALE_IVORY}Mental{RESET}     "
        f"{GOLD}Intelligence{RESET} {trait_dots(int_val)} {int_val}  "
        f"{GOLD}Wits{RESET} {trait_dots(wit_val)} {wit_val}  "
        f"{GOLD}Resolve{RESET} {trait_dots(res_val)} {res_val}  "
        f"{SHADOW_GREY}{BOX_V}{RESET}"
    )

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_skills_section(character):
    """Format skills display (only showing skills with dots)."""
    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ""

    skills = character.db.stats.get('skills', {})
    specialties = character.db.stats.get('specialties', {})

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}SKILLS{' ' * 61}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")

    # Collect all skills with dots
    all_skills = []
    for category, skill_dict in skills.items():
        for skill_name, value in skill_dict.items():
            if value > 0:
                specialty = specialties.get(skill_name, None)
                all_skills.append((skill_name, value, category, specialty))

    # Sort alphabetically
    all_skills.sort(key=lambda x: x[0])

    if not all_skills:
        lines.append(f"{SHADOW_GREY}{BOX_V} {SHADOW_GREY}(No skills assigned){' ' * 47}{BOX_V}{RESET}")
    else:
        # Display skills in columns (2 per row)
        for i in range(0, len(all_skills), 2):
            skill1_name, skill1_val, skill1_cat, skill1_spec = all_skills[i]
            skill1_display = skill1_name.replace('_', ' ').title()
            if skill1_spec:
                skill1_display += f" ({skill1_spec})"

            skill1_text = f"{GOLD}{skill1_display:<20}{RESET} {trait_dots(skill1_val)} {skill1_val}"

            # Check if there's a second skill in this row
            if i + 1 < len(all_skills):
                skill2_name, skill2_val, skill2_cat, skill2_spec = all_skills[i + 1]
                skill2_display = skill2_name.replace('_', ' ').title()
                if skill2_spec:
                    skill2_display += f" ({skill2_spec})"

                skill2_text = f"{GOLD}{skill2_display:<20}{RESET} {trait_dots(skill2_val)} {skill2_val}"
                lines.append(f"{SHADOW_GREY}{BOX_V} {skill1_text}  {skill2_text:<24}{SHADOW_GREY}{BOX_V}{RESET}")
            else:
                lines.append(f"{SHADOW_GREY}{BOX_V} {skill1_text}{' ' * 34}{SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_disciplines_section(character):
    """Format disciplines display."""
    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ""

    disciplines = character.db.stats.get('disciplines', {})

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}DISCIPLINES{' ' * 56}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")

    if not disciplines:
        lines.append(f"{SHADOW_GREY}{BOX_V} {SHADOW_GREY}(No disciplines learned){' ' * 44}{BOX_V}{RESET}")
    else:
        for disc_name, disc_data in sorted(disciplines.items()):
            level = disc_data.get('level', 0)
            powers = disc_data.get('powers', [])

            disc_display = disc_name.replace('_', ' ').title()
            disc_line = f"{DARK_RED}{disc_display:<20}{RESET} {trait_dots(level)} {level}"

            lines.append(f"{SHADOW_GREY}{BOX_V} {disc_line}{' ' * 39}{SHADOW_GREY}{BOX_V}{RESET}")

            # Show known powers (if any)
            if powers:
                for power in powers[:3]:  # Show first 3 powers
                    lines.append(f"{SHADOW_GREY}{BOX_V}   {SHADOW_GREY}{CIRCLE_FILLED} {PALE_IVORY}{power}{' ' * (62 - len(power))}{SHADOW_GREY}{BOX_V}{RESET}")
                if len(powers) > 3:
                    lines.append(f"{SHADOW_GREY}{BOX_V}   {SHADOW_GREY}... and {len(powers) - 3} more{' ' * 43}{SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_advantages_section(character):
    """Format backgrounds, merits, and flaws."""
    if not hasattr(character.db, 'advantages') or not character.db.advantages:
        return ""

    advantages = character.db.advantages
    backgrounds = advantages.get('backgrounds', {})
    merits = advantages.get('merits', {})
    flaws = advantages.get('flaws', {})

    # Skip if all empty
    if not backgrounds and not merits and not flaws:
        return ""

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}BACKGROUNDS & ADVANTAGES{' ' * 43}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")

    # Backgrounds
    if backgrounds:
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Backgrounds:{' ' * 56}{SHADOW_GREY}{BOX_V}{RESET}")
        for bg_name, bg_val in sorted(backgrounds.items()):
            bg_display = bg_name.replace('_', ' ').title()
            lines.append(f"{SHADOW_GREY}{BOX_V}   {PALE_IVORY}{bg_display:<30}{RESET} {trait_dots(bg_val)} {bg_val}{' ' * 25}{SHADOW_GREY}{BOX_V}{RESET}")

    # Merits
    if merits:
        if backgrounds:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 68}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Merits:{' ' * 60}{SHADOW_GREY}{BOX_V}{RESET}")
        for merit_name, merit_val in sorted(merits.items()):
            merit_display = merit_name.replace('_', ' ').title()
            lines.append(f"{SHADOW_GREY}{BOX_V}   {PALE_IVORY}{merit_display:<30}{RESET} {trait_dots(merit_val)} {merit_val}{' ' * 25}{SHADOW_GREY}{BOX_V}{RESET}")

    # Flaws
    if flaws:
        if backgrounds or merits:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 68}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Flaws:{' ' * 61}{SHADOW_GREY}{BOX_V}{RESET}")
        for flaw_name, flaw_val in sorted(flaws.items()):
            flaw_display = flaw_name.replace('_', ' ').title()
            lines.append(f"{SHADOW_GREY}{BOX_V}   {BLOOD_RED}{flaw_display:<30}{RESET} {trait_dots(flaw_val)} {flaw_val}{' ' * 25}{SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_humanity_section(character):
    """Format humanity, convictions, and touchstones."""
    if not hasattr(character.db, 'humanity_data') or not character.db.humanity_data:
        return ""

    hum_data = character.db.humanity_data
    convictions = hum_data.get('convictions', [])
    touchstones = hum_data.get('touchstones', [])
    stains = hum_data.get('stains', 0)

    # Skip if no convictions/touchstones set
    if not convictions and not touchstones:
        return ""

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}HUMANITY & TOUCHSTONES{' ' * 45}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")

    # Stains
    if stains > 0:
        lines.append(f"{SHADOW_GREY}{BOX_V} {BLOOD_RED}Stains:{RESET} {trait_dots(stains, 10, CIRCLE_FILLED, CIRCLE_EMPTY)} {stains}/10{' ' * 42}{SHADOW_GREY}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 68}{BOX_V}{RESET}")

    # Convictions
    if convictions:
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Convictions:{' ' * 55}{SHADOW_GREY}{BOX_V}{RESET}")
        for conviction in convictions:
            wrapped = _wrap_text(f"  {PALE_IVORY}{CIRCLE_FILLED} {conviction}", 64)
            for line in wrapped:
                lines.append(f"{SHADOW_GREY}{BOX_V} {line:<77}{SHADOW_GREY}{BOX_V}{RESET}")

    # Touchstones
    if touchstones:
        if convictions:
            lines.append(f"{SHADOW_GREY}{BOX_V}{' ' * 68}{BOX_V}{RESET}")
        lines.append(f"{SHADOW_GREY}{BOX_V} {GOLD}Touchstones:{' ' * 55}{SHADOW_GREY}{BOX_V}{RESET}")
        for touchstone in touchstones:
            ts_name = touchstone.get('name', 'Unknown')
            wrapped = _wrap_text(f"  {PALE_IVORY}{CIRCLE_FILLED} {ts_name}", 64)
            for line in wrapped:
                lines.append(f"{SHADOW_GREY}{BOX_V} {line:<77}{SHADOW_GREY}{BOX_V}{RESET}")

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _format_sheet_footer(character):
    """Create footer with pools and experience."""
    pools = character.db.pools if hasattr(character.db, 'pools') else {}
    experience = character.db.experience if hasattr(character.db, 'experience') else {}

    health = pools.get('health', 0)
    current_health = pools.get('current_health', health)
    willpower = pools.get('willpower', 0)
    current_willpower = pools.get('current_willpower', willpower)

    total_xp = experience.get('total_earned', 0)
    spent_xp = experience.get('total_spent', 0)
    current_xp = experience.get('current', 0)

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 68}{BOX_TR}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}POOLS & EXPERIENCE{' ' * 49}{SHADOW_GREY}{BOX_V}{RESET}")
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 68}{BOX_R}{RESET}")
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {GOLD}Health:{RESET} {current_health}/{health}  "
        f"{GOLD}Willpower:{RESET} {current_willpower}/{willpower}  "
        f"{GOLD}Experience:{RESET} {current_xp} XP (Earned: {total_xp}, Spent: {spent_xp}){' ' * 5}{SHADOW_GREY}{BOX_V}{RESET}"
    )
    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 68}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _wrap_text(text, width):
    """
    Wrap text to specified width, preserving ANSI codes.

    Args:
        text (str): Text to wrap (may contain ANSI codes)
        width (int): Maximum width

    Returns:
        list: List of wrapped lines
    """
    # Simple implementation - doesn't count ANSI codes in length
    # For production, would need more sophisticated ANSI-aware wrapping
    if len(text) <= width:
        return [text]

    # Basic wrapping (TODO: improve to be ANSI-aware)
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_len = len(word)  # TODO: strip ANSI codes for accurate length
        if current_length + word_len + 1 <= width:
            current_line.append(word)
            current_length += word_len + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_len

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def format_short_sheet(character):
    """
    Create a compact one-line status display.

    Args:
        character: Character object

    Returns:
        str: Compact character status
    """
    name = character.key
    clan = get_clan(character) or "Unknown"
    generation = character.db.vampire.get('generation', 13) if hasattr(character.db, 'vampire') else 13
    hunger = get_hunger(character)

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
