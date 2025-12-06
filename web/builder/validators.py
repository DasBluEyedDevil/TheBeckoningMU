"""
Validation utilities for the Web Builder.
"""


def validate_project(map_data):
    """
    Validate a project's map data before building.

    Returns:
        tuple: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    rooms = map_data.get("rooms", {})
    exits = map_data.get("exits", {})

    if not rooms:
        errors.append("Project has no rooms.")
        return False, errors, warnings

    # Check for isolated rooms (no exits)
    room_connections = {rid: {"in": [], "out": []} for rid in rooms}

    for exit_id, exit_data in exits.items():
        source = exit_data.get("source")
        target = exit_data.get("target")

        if source not in rooms:
            errors.append(f"Exit '{exit_id}' has invalid source room '{source}'")
        else:
            room_connections[source]["out"].append(exit_id)

        if target not in rooms:
            errors.append(f"Exit '{exit_id}' has invalid target room '{target}'")
        else:
            room_connections[target]["in"].append(exit_id)

    # Warn about isolated rooms
    for room_id, connections in room_connections.items():
        room_name = rooms[room_id].get("name", room_id)
        if not connections["in"] and not connections["out"]:
            warnings.append(f"Room '{room_name}' has no exits (isolated)")
        elif not connections["in"] and len(rooms) > 1:
            warnings.append(f"Room '{room_name}' has no incoming exits (unreachable)")

    # Warn about empty descriptions
    for room_id, room in rooms.items():
        if not room.get("description"):
            warnings.append(f"Room '{room.get('name', room_id)}' has no description")

    # Check for duplicate room names
    names = [r.get("name", "") for r in rooms.values()]
    duplicates = set(n for n in names if names.count(n) > 1 and n)
    for name in duplicates:
        warnings.append(f"Multiple rooms named '{name}'")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
