"""
Status System Utility Functions

Helper functions for managing Status, calculating bonuses, and handling positions.
"""

from .models import CharacterStatus, CamarillaPosition, StatusRequest
from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY,
    BONE_WHITE, MIDNIGHT_BLUE, GOLD, RESET,
    DBOX_H, DBOX_V, DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR,
    BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR,
    FLEUR_DE_LIS, CROWN, CIRCLE_FILLED, CIRCLE_EMPTY
)


def get_or_create_character_status(character):
    """
    Get or create CharacterStatus for a character.

    Args:
        character: Character object

    Returns:
        CharacterStatus: Character's status record
    """
    char_status, created = CharacterStatus.objects.get_or_create(
        character=character,
        defaults={
            'earned_status': 0,
            'position_status': 0,
            'temporary_status': 0,
            'sect': 'Camarilla',
            'reputation': ''
        }
    )

    return char_status


def get_character_status(character):
    """
    Get character's Status record (returns None if doesn't exist).

    Args:
        character: Character object

    Returns:
        CharacterStatus or None
    """
    try:
        return CharacterStatus.objects.get(character=character)
    except CharacterStatus.DoesNotExist:
        return None


def get_total_status(character):
    """
    Get character's total Status rating.

    Args:
        character: Character object

    Returns:
        int: Total Status (0-5)
    """
    char_status = get_character_status(character)
    if not char_status:
        return 0

    return char_status.total_status


def get_status_bonus(character, context="social"):
    """
    Get dice bonus from Status for rolls.

    Status provides +1 die per 2 Status dots for relevant social rolls.

    Args:
        character: Character object
        context (str): Context of roll ("social", "intimidate", "command", etc.)

    Returns:
        int: Bonus dice
    """
    char_status = get_character_status(character)
    if not char_status:
        return 0

    # Base bonus: +1 die per 2 Status
    base_bonus = char_status.total_status // 2

    # Context-specific modifiers
    if context in ["command", "leadership"] and char_status.position:
        # Leaders get additional bonus when commanding
        if char_status.position.hierarchy_level >= 5:  # Prince-level
            base_bonus += 2
        elif char_status.position.hierarchy_level >= 3:  # Primogen-level
            base_bonus += 1

    return base_bonus


def set_earned_status(character, value, reason="", changed_by=None):
    """
    Set character's earned Status.

    Args:
        character: Character object
        value (int): New earned Status value (0-5)
        reason (str): Reason for change
        changed_by: Character/account who made the change

    Returns:
        CharacterStatus: Updated status record
    """
    char_status = get_or_create_character_status(character)

    old_value = char_status.earned_status
    char_status.earned_status = max(0, min(5, value))

    # Log history
    change = char_status.earned_status - old_value
    if change != 0:
        char_status.add_status_history(
            change,
            reason or f"Status adjusted to {char_status.earned_status}",
            str(changed_by) if changed_by else "System"
        )

    char_status.save()
    return char_status


def modify_earned_status(character, change, reason="", changed_by=None):
    """
    Modify character's earned Status by a delta.

    Args:
        character: Character object
        change (int): Change amount (+/-)
        reason (str): Reason for change
        changed_by: Character/account who made the change

    Returns:
        CharacterStatus: Updated status record
    """
    char_status = get_or_create_character_status(character)

    new_value = max(0, min(5, char_status.earned_status + change))
    return set_earned_status(character, new_value, reason, changed_by)


def assign_position(character, position_name, assigned_by=None):
    """
    Assign a Camarilla position to a character.

    Args:
        character: Character object
        position_name (str): Name of position
        assigned_by: Character/account assigning position

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        position = CamarillaPosition.objects.get(name__iexact=position_name, is_active=True)
    except CamarillaPosition.DoesNotExist:
        return (False, f"Position '{position_name}' not found or is inactive.")

    char_status = get_or_create_character_status(character)

    # Check requirements
    if position.requires_status > char_status.earned_status:
        return (False, f"Character requires {position.requires_status} earned Status to hold this position.")

    if position.requires_clan:
        char_clan = character.db.vampire.get('clan', '') if hasattr(character.db, 'vampire') else ''
        if char_clan.lower() != position.requires_clan.lower():
            return (False, f"Position requires clan {position.requires_clan}.")

    # If position is unique, remove current holder
    if position.is_unique:
        old_holders = CharacterStatus.objects.filter(position=position)
        for old_holder in old_holders:
            old_holder.position = None
            old_holder.position_status = 0
            old_holder.add_status_history(
                -position.status_granted,
                f"Removed from position: {position.name}",
                str(assigned_by) if assigned_by else "System"
            )
            old_holder.save()

    # Assign position
    char_status.position = position
    char_status.position_status = position.status_granted
    char_status.sect = position.sect
    char_status.add_status_history(
        position.status_granted,
        f"Appointed to position: {position.name}",
        str(assigned_by) if assigned_by else "System"
    )
    char_status.save()

    return (True, f"{character.key} appointed as {position.name}.")


def remove_position(character, removed_by=None):
    """
    Remove character's position.

    Args:
        character: Character object
        removed_by: Character/account removing position

    Returns:
        tuple: (success: bool, message: str)
    """
    char_status = get_character_status(character)

    if not char_status or not char_status.position:
        return (False, f"{character.key} does not hold a position.")

    position_name = char_status.position.name
    status_lost = char_status.position_status

    char_status.position = None
    char_status.position_status = 0
    char_status.add_status_history(
        -status_lost,
        f"Removed from position: {position_name}",
        str(removed_by) if removed_by else "System"
    )
    char_status.save()

    return (True, f"{character.key} removed from position: {position_name}.")


def get_all_positions():
    """
    Get all active Camarilla positions.

    Returns:
        QuerySet: Active positions ordered by hierarchy
    """
    return CamarillaPosition.objects.filter(is_active=True).order_by('-hierarchy_level', 'name')


def get_position_holders(position_name):
    """
    Get all characters holding a specific position.

    Args:
        position_name (str): Position name

    Returns:
        QuerySet: Characters holding this position
    """
    try:
        position = CamarillaPosition.objects.get(name__iexact=position_name, is_active=True)
        return CharacterStatus.objects.filter(position=position)
    except CamarillaPosition.DoesNotExist:
        return CharacterStatus.objects.none()


def create_status_request(character, request_type, reason, **kwargs):
    """
    Create a status change request.

    Args:
        character: Character making request
        request_type (str): Type of request
        reason (str): IC justification
        **kwargs: Additional fields (requested_change, requested_position, ooc_notes)

    Returns:
        StatusRequest: Created request
    """
    request = StatusRequest.objects.create(
        character=character,
        request_type=request_type,
        reason=reason,
        requested_change=kwargs.get('requested_change', 0),
        requested_position=kwargs.get('requested_position', None),
        ooc_notes=kwargs.get('ooc_notes', ''),
        status='pending'
    )

    return request


def get_pending_status_requests():
    """
    Get all pending status requests.

    Returns:
        QuerySet: Pending requests
    """
    return StatusRequest.objects.filter(status='pending').order_by('-created_date')


def get_character_status_requests(character, status=None):
    """
    Get status requests for a character.

    Args:
        character: Character object
        status (str, optional): Filter by status (pending, approved, denied)

    Returns:
        QuerySet: Character's requests
    """
    requests = StatusRequest.objects.filter(character=character)

    if status:
        requests = requests.filter(status=status)

    return requests.order_by('-created_date')


def format_status_display(character):
    """
    Format character's Status for display with colors and symbols.

    Args:
        character: Character object

    Returns:
        str: Formatted status display
    """
    char_status = get_character_status(character)

    if not char_status:
        return f"{SHADOW_GREY}No Status record{RESET}"

    # Colored header
    output = []
    output.append(f"{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}")
    output.append(f"{DBOX_V} {FLEUR_DE_LIS} {BONE_WHITE}Status and Standing{RESET}{' ' * 54}{DARK_RED}{DBOX_V}")
    output.append(f"{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}")
    output.append("")

    # Total Status with color gradient
    total = char_status.total_status

    # Color gradient based on status level
    if total >= 4:
        status_color = GOLD
    elif total >= 2:
        status_color = MIDNIGHT_BLUE
    else:
        status_color = SHADOW_GREY

    # Dot representation with colors
    dots_filled = f"{status_color}{CIRCLE_FILLED * total}{RESET}"
    dots_empty = f"{SHADOW_GREY}{CIRCLE_EMPTY * (5 - total)}{RESET}"

    output.append(f"  {GOLD}Total Status:{RESET} {dots_filled}{dots_empty} {status_color}({total}/5){RESET}")

    # Breakdown
    if char_status.earned_status > 0 or char_status.position_status > 0 or char_status.temporary_status != 0:
        output.append(f"  {SHADOW_GREY}└─ Breakdown:{RESET}")

        if char_status.earned_status > 0:
            output.append(f"     {PALE_IVORY}Earned:{RESET} {GOLD}{char_status.earned_status}{RESET}")

        if char_status.position_status > 0:
            output.append(f"     {PALE_IVORY}Position:{RESET} {MIDNIGHT_BLUE}{char_status.position_status}{RESET}")

        if char_status.temporary_status != 0:
            temp_color = GOLD if char_status.temporary_status > 0 else BLOOD_RED
            output.append(f"     {PALE_IVORY}Temporary:{RESET} {temp_color}{char_status.temporary_status:+d}{RESET}")

    # Position
    if char_status.position:
        output.append("")
        output.append(f"  {GOLD}Position:{RESET} {CROWN} {BONE_WHITE}{char_status.position.name}{RESET}")
        if char_status.position.title:
            output.append(f"  {SHADOW_GREY}└─ Title:{RESET} {PALE_IVORY}{char_status.position.title}{RESET}")
        output.append(f"  {SHADOW_GREY}└─ Status Granted:{RESET} {MIDNIGHT_BLUE}{char_status.position.status_granted}{RESET}")

    # Sect
    output.append("")
    output.append(f"  {GOLD}Sect:{RESET} {FLEUR_DE_LIS} {PALE_IVORY}{char_status.sect}{RESET}")

    # Mechanical bonus
    bonus = char_status.get_status_bonus()
    if bonus > 0:
        output.append("")
        output.append(f"  {GOLD}Social Roll Bonus:{RESET} {MIDNIGHT_BLUE}+{bonus} dice{RESET}")

    # Reputation (if set)
    if char_status.reputation:
        output.append("")
        output.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}")
        output.append(f"{BOX_V} {BONE_WHITE}Reputation{RESET}{' ' * 67}{SHADOW_GREY}{BOX_V}")
        output.append(f"{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")
        output.append(f"{PALE_IVORY}{char_status.reputation}{RESET}")

    return "\n".join(output)


def initialize_default_positions():
    """
    Initialize default Camarilla positions.

    This should be run once during setup to create standard positions.
    """
    default_positions = [
        {
            "name": "Prince",
            "title": "Prince of Athens",
            "status_granted": 3,
            "hierarchy_level": 10,
            "description": "Ruler of the city domain, arbiter of the Traditions",
            "is_unique": True,
            "requires_status": 2,
            "sect": "Camarilla"
        },
        {
            "name": "Primogen",
            "title": "Primogen Council Member",
            "status_granted": 2,
            "hierarchy_level": 8,
            "description": "Clan representative on the Primogen Council",
            "is_unique": False,
            "requires_status": 1,
            "sect": "Camarilla"
        },
        {
            "name": "Sheriff",
            "title": "Sheriff of Athens",
            "status_granted": 2,
            "hierarchy_level": 7,
            "description": "Enforcer of the Prince's will and Traditions",
            "is_unique": True,
            "requires_status": 1,
            "sect": "Camarilla"
        },
        {
            "name": "Scourge",
            "title": "Scourge of Athens",
            "status_granted": 1,
            "hierarchy_level": 6,
            "description": "Hunter of unauthorized vampires and Thin-Bloods",
            "is_unique": True,
            "requires_status": 0,
            "sect": "Camarilla"
        },
        {
            "name": "Keeper of Elysium",
            "title": "Keeper of Elysium",
            "status_granted": 2,
            "hierarchy_level": 7,
            "description": "Guardian of Elysium and enforcer of its neutrality",
            "is_unique": True,
            "requires_status": 1,
            "sect": "Camarilla"
        },
        {
            "name": "Whip",
            "title": "Clan Whip",
            "status_granted": 1,
            "hierarchy_level": 5,
            "description": "Assistant to a Primogen, enforcer of clan discipline",
            "is_unique": False,
            "requires_status": 0,
            "sect": "Camarilla"
        },
        {
            "name": "Harpy",
            "title": "Harpy",
            "status_granted": 1,
            "hierarchy_level": 6,
            "description": "Arbiter of social standing and boons",
            "is_unique": False,
            "requires_status": 1,
            "sect": "Camarilla"
        },
        {
            "name": "Seneschal",
            "title": "Seneschal of Athens",
            "status_granted": 2,
            "hierarchy_level": 9,
            "description": "Second to the Prince, acts in their absence",
            "is_unique": True,
            "requires_status": 2,
            "sect": "Camarilla"
        },
    ]

    created_count = 0
    for pos_data in default_positions:
        position, created = CamarillaPosition.objects.get_or_create(
            name=pos_data["name"],
            defaults=pos_data
        )
        if created:
            created_count += 1

    return created_count


# =============================================================================
# FORMATTING FUNCTIONS (Presentation Layer)
# =============================================================================

def format_character_status(character, char_status):
    """
    Format character status for display.

    Args:
        character: Character object
        char_status: CharacterStatus object

    Returns:
        str: Formatted character status display
    """
    output = []
    output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
    output.append(f"{BOX_V} {GOLD}♛{RESET} {PALE_IVORY}STATUS: {character.key.upper()}{RESET}{' ' * (65 - len(character.key))}{BOX_V}")
    output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

    # Total Status
    total = char_status.total_status
    status_dots = f"{GOLD}{CIRCLE_FILLED * total}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - total)}{RESET}"
    output.append(f"\n{PALE_IVORY}Total Status:{RESET} {status_dots} ({total}/5)")

    # Breakdown
    breakdown = []
    if char_status.earned_status > 0:
        breakdown.append(f"Earned: {char_status.earned_status}")
    if char_status.position_status > 0:
        breakdown.append(f"Position: {char_status.position_status}")
    if char_status.temporary_status != 0:
        breakdown.append(f"Temporary: {char_status.temporary_status:+d}")

    if breakdown:
        output.append(f"{SHADOW_GREY}  ({', '.join(breakdown)}){RESET}")

    # Position
    if char_status.position:
        output.append(f"\n{PALE_IVORY}Position:{RESET} {GOLD}{char_status.position.name}{RESET}")
        if char_status.position.title:
            output.append(f"{SHADOW_GREY}  \"{char_status.position.title}\"{RESET}")
        output.append(f"{SHADOW_GREY}  {char_status.position.description}{RESET}")

    # Sect
    output.append(f"\n{PALE_IVORY}Sect:{RESET} {char_status.sect}")

    # Mechanical Bonus
    bonus = char_status.get_status_bonus()
    if bonus > 0:
        output.append(f"\n{PALE_IVORY}Social Roll Bonus:{RESET} +{bonus} dice")

    # Reputation
    if char_status.reputation:
        output.append(f"\n{PALE_IVORY}Reputation:{RESET}")
        output.append(f"{SHADOW_GREY}{char_status.reputation}{RESET}")

    return "\n".join(output)


def format_status_history(char_status):
    """
    Format status history for display.

    Args:
        char_status: CharacterStatus object

    Returns:
        str: Formatted status history display
    """
    output = []
    output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
    output.append(f"{BOX_V} {PALE_IVORY}STATUS HISTORY{RESET}{' ' * 60}{BOX_V}")
    output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}\n")

    for entry in reversed(char_status.status_history[-10:]):  # Last 10 entries
        date = entry.get('date', 'Unknown')[:10]  # Just the date part
        change = entry.get('change', 0)
        reason = entry.get('reason', 'No reason given')
        changed_by = entry.get('changed_by', 'Unknown')
        new_total = entry.get('new_total', 0)

        change_str = f"{GOLD}+{change}{RESET}" if change > 0 else f"{BLOOD_RED}{change}{RESET}" if change < 0 else f"{SHADOW_GREY}±0{RESET}"

        output.append(f"{SHADOW_GREY}{date}{RESET} - {change_str} → {new_total}")
        output.append(f"  {PALE_IVORY}{reason}{RESET}")
        output.append(f"  {SHADOW_GREY}(by {changed_by}){RESET}")
        output.append("")

    return "\n".join(output)


def format_positions_list(positions):
    """
    Format positions list for display.

    Args:
        positions: QuerySet of CamarillaPosition objects

    Returns:
        str: Formatted positions list display
    """
    output = []
    output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
    output.append(f"{BOX_V} {GOLD}♛{RESET} {PALE_IVORY}CAMARILLA POSITIONS{RESET}{' ' * 53}{BOX_V}")
    output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}\n")

    for position in positions:
        holders = get_position_holders(position.name)
        holder_count = holders.count()

        status_dots = f"{GOLD}{CIRCLE_FILLED * position.status_granted}{RESET}"

        output.append(f"{PALE_IVORY}{position.name}{RESET} {status_dots}")
        output.append(f"  {SHADOW_GREY}{position.description}{RESET}")

        if holder_count > 0:
            holder_names = ", ".join([h.character.key for h in holders])
            output.append(f"  {GOLD}Holder(s):{RESET} {holder_names}")
        elif position.is_unique:
            output.append(f"  {SHADOW_GREY}(Vacant){RESET}")

        output.append("")

    return "\n".join(output)


def format_position_detail(position):
    """
    Format position detail for display.

    Args:
        position: CamarillaPosition object

    Returns:
        str: Formatted position detail display
    """
    holders = get_position_holders(position.name)

    output = []
    output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
    output.append(f"{BOX_V} {GOLD}♛{RESET} {PALE_IVORY}{position.name.upper()}{RESET}{' ' * (68 - len(position.name))}{BOX_V}")
    output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

    # Status granted
    status_dots = f"{GOLD}{CIRCLE_FILLED * position.status_granted}{CIRCLE_EMPTY * (5 - position.status_granted)}{RESET}"
    output.append(f"\n{PALE_IVORY}Status Granted:{RESET} {status_dots} ({position.status_granted})")

    # Hierarchy level
    output.append(f"{PALE_IVORY}Hierarchy Level:{RESET} {position.hierarchy_level}")

    # Description
    output.append(f"\n{PALE_IVORY}Description:{RESET}")
    output.append(f"{SHADOW_GREY}{position.description}{RESET}")

    # Requirements
    if position.requires_status > 0:
        output.append(f"\n{PALE_IVORY}Requirements:{RESET} {position.requires_status} Status")

    # Unique/Multiple
    if position.is_unique:
        output.append(f"\n{PALE_IVORY}Type:{RESET} Unique position (only one holder)")
    else:
        output.append(f"\n{PALE_IVORY}Type:{RESET} Multiple holders allowed")

    # Current holders
    if holders.exists():
        output.append(f"\n{PALE_IVORY}Current Holder(s):{RESET}")
        for holder in holders:
            output.append(f"  {GOLD}{holder.character.key}{RESET}")
    else:
        output.append(f"\n{SHADOW_GREY}(Currently vacant){RESET}")

    return "\n".join(output)
