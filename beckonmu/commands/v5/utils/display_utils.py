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

    # Section 5: HUMANITY DETAILS (Convictions & Touchstones)
    lines.append(_format_humanity_details(character))
    lines.append("")

    # Section 6: ADVANTAGES (Backgrounds, Merits, Flaws)
    lines.append(_format_advantages(character))
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
    vamp = character.db.vampire if hasattr(character.db, 'vampire') else {}

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
    Section 2: Three-column layout
    ATTRIBUTES (left) | SKILLS (center) | DISCIPLINES (right)

    Official sheet layout:
    - Attributes in 3x3 grid (9 attributes total)
    - Skills listed vertically by category
    - Disciplines listed with dot ratings
    """
    attrs_lines = _build_attributes_section(character)
    skills_lines = _build_skills_section(character)
    disciplines_lines = _build_disciplines_section(character)

    # Pad to same height
    max_height = max(len(attrs_lines), len(skills_lines), len(disciplines_lines))
    attrs_lines += [""] * (max_height - len(attrs_lines))
    skills_lines += [""] * (max_height - len(skills_lines))
    disciplines_lines += [""] * (max_height - len(disciplines_lines))

    lines = []
    lines.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}{RESET}")

    # Headers
    lines.append(
        f"{SHADOW_GREY}{BOX_V} {BONE_WHITE}ATTRIBUTES{' ' * 14}"
        f"{BOX_V} {BONE_WHITE}SKILLS{' ' * 20}"
        f"{BOX_V} {BONE_WHITE}DISCIPLINES{' ' * 13}{BOX_V}{RESET}"
    )
    lines.append(f"{SHADOW_GREY}{BOX_L}{BOX_H * 24}{BOX_R}{BOX_H * 26}{BOX_R}{BOX_H * 25}{BOX_R}{RESET}")

    # Content rows
    for i in range(max_height):
        attr_line = attrs_lines[i] if i < len(attrs_lines) else ""
        skill_line = skills_lines[i] if i < len(skills_lines) else ""
        disc_line = disciplines_lines[i] if i < len(disciplines_lines) else ""

        lines.append(
            f"{SHADOW_GREY}{BOX_V} {attr_line:<31}"
            f"{BOX_V} {skill_line:<33}"
            f"{BOX_V} {disc_line:<32}{BOX_V}{RESET}"
        )

    lines.append(f"{SHADOW_GREY}{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")

    return "\n".join(lines)


def _build_attributes_section(character):
    """Build attributes section (matches official 3x3 layout)."""
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ["(No attributes)"]

    attrs = character.db.stats.get('attributes', {})
    phys = attrs.get('physical', {})
    soc = attrs.get('social', {})
    ment = attrs.get('mental', {})

    # Physical attributes
    lines.append(f"{PALE_IVORY}Physical{RESET}")
    lines.append(f"  {GOLD}Strength{RESET}     {_dots(phys.get('strength', 1))}")
    lines.append(f"  {GOLD}Dexterity{RESET}    {_dots(phys.get('dexterity', 1))}")
    lines.append(f"  {GOLD}Stamina{RESET}      {_dots(phys.get('stamina', 1))}")
    lines.append("")

    # Social attributes
    lines.append(f"{PALE_IVORY}Social{RESET}")
    lines.append(f"  {GOLD}Charisma{RESET}     {_dots(soc.get('charisma', 1))}")
    lines.append(f"  {GOLD}Manipulation{RESET} {_dots(soc.get('manipulation', 1))}")
    lines.append(f"  {GOLD}Composure{RESET}    {_dots(soc.get('composure', 1))}")
    lines.append("")

    # Mental attributes
    lines.append(f"{PALE_IVORY}Mental{RESET}")
    lines.append(f"  {GOLD}Intelligence{RESET} {_dots(ment.get('intelligence', 1))}")
    lines.append(f"  {GOLD}Wits{RESET}         {_dots(ment.get('wits', 1))}")
    lines.append(f"  {GOLD}Resolve{RESET}      {_dots(ment.get('resolve', 1))}")

    return lines


def _build_skills_section(character):
    """Build skills section (official sheet: all skills listed by category)."""
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ["(No skills)"]

    skills = character.db.stats.get('skills', {})
    specialties = character.db.stats.get('specialties', {})

    # Physical skills
    lines.append(f"{PALE_IVORY}Physical{RESET}")
    phys_skills = skills.get('physical', {})
    for skill_name in sorted(phys_skills.keys()):
        value = phys_skills[skill_name]
        if value > 0:  # Only show skills with dots
            display_name = skill_name.replace('_', ' ').title()
            spec = specialties.get(skill_name, "")
            spec_str = f" ({spec})" if spec else ""
            lines.append(f"  {GOLD}{display_name:<13}{RESET}{_dots(value)}{spec_str}")

    if not any(v > 0 for v in phys_skills.values()):
        lines.append(f"  {SHADOW_GREY}—{RESET}")
    lines.append("")

    # Social skills
    lines.append(f"{PALE_IVORY}Social{RESET}")
    soc_skills = skills.get('social', {})
    for skill_name in sorted(soc_skills.keys()):
        value = soc_skills[skill_name]
        if value > 0:
            display_name = skill_name.replace('_', ' ').title()
            spec = specialties.get(skill_name, "")
            spec_str = f" ({spec})" if spec else ""
            lines.append(f"  {GOLD}{display_name:<13}{RESET}{_dots(value)}{spec_str}")

    if not any(v > 0 for v in soc_skills.values()):
        lines.append(f"  {SHADOW_GREY}—{RESET}")
    lines.append("")

    # Mental skills
    lines.append(f"{PALE_IVORY}Mental{RESET}")
    ment_skills = skills.get('mental', {})
    for skill_name in sorted(ment_skills.keys()):
        value = ment_skills[skill_name]
        if value > 0:
            display_name = skill_name.replace('_', ' ').title()
            spec = specialties.get(skill_name, "")
            spec_str = f" ({spec})" if spec else ""
            lines.append(f"  {GOLD}{display_name:<13}{RESET}{_dots(value)}{spec_str}")

    if not any(v > 0 for v in ment_skills.values()):
        lines.append(f"  {SHADOW_GREY}—{RESET}")

    return lines


def _build_disciplines_section(character):
    """Build disciplines section (right column of upper section)."""
    lines = []

    if not hasattr(character.db, 'stats') or not character.db.stats:
        return ["(No disciplines)"]

    disciplines = character.db.stats.get('disciplines', {})

    if not disciplines:
        lines.append(f"{SHADOW_GREY}(None){RESET}")
    else:
        for disc_name, disc_data in sorted(disciplines.items()):
            level = disc_data.get('level', 0)
            display_name = disc_name.replace('_', ' ').title()
            lines.append(f"{DARK_RED}{display_name:<16}{RESET}{_dots(level)}")

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

    pools = character.db.pools if hasattr(character.db, 'pools') else {}

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

    vamp = character.db.vampire if hasattr(character.db, 'vampire') else {}

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
    hum_data = character.db.humanity_data if hasattr(character.db, 'humanity_data') else {}
    stains = hum_data.get('stains', 0)
    if stains > 0:
        lines.append(f"  {BLOOD_RED}Stains:{RESET} {_dots(stains, 10)}")
    lines.append("")

    # Blood Potency
    bp = vamp.get('blood_potency', 0)
    lines.append(f"{BONE_WHITE}BLOOD POTENCY{RESET}")
    lines.append(f"  {_dots(bp, 10)}")

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


def _format_humanity_details(character):
    """Section 5: Convictions and Touchstones."""
    hum_data = character.db.humanity_data if hasattr(character.db, 'humanity_data') else {}
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
    advantages = character.db.advantages if hasattr(character.db, 'advantages') else {}
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


def _format_experience(character):
    """Section 7: Experience."""
    experience = character.db.experience if hasattr(character.db, 'experience') else {}
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
    vamp = character.db.vampire if hasattr(character.db, 'vampire') else {}
    generation = vamp.get('generation', 13)
    hunger = vamp.get('hunger', 0)

    hunger_color = get_hunger_color(hunger)
    hunger_dots = f"{hunger_color}{CIRCLE_FILLED * hunger}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - hunger)}{RESET}"

    pools = character.db.pools if hasattr(character.db, 'pools') else {}
    health = pools.get('current_health', pools.get('health', 0))
    willpower = pools.get('current_willpower', pools.get('willpower', 0))

    return (
        f"{BONE_WHITE}{name}{RESET} "
        f"({DARK_RED}{clan}{RESET} Gen {generation}) "
        f"Hunger: {hunger_dots} "
        f"Health: {health} Willpower: {willpower}"
    )
