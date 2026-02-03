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

    # ------------------------------------------------------------------
    # Shape validation: rooms
    # ------------------------------------------------------------------
    valid_room_ids = set()
    for room_id, room in rooms.items():
        if not isinstance(room, dict):
            errors.append(f"Room '{room_id}' has invalid data format")
            continue
        if not room.get("name"):
            errors.append(f"Room '{room_id}' is missing a name")
        # Position validation (rooms should have grid coordinates)
        if "x" not in room and "gridX" not in room:
            warnings.append(
                f"Room '{room.get('name', room_id)}' has no grid position"
            )
        valid_room_ids.add(room_id)

    # ------------------------------------------------------------------
    # Shape validation: exits
    # ------------------------------------------------------------------
    valid_exits = {}  # exit_id -> exit_data for exits that pass shape check
    for exit_id, exit_data in exits.items():
        if not isinstance(exit_data, dict):
            errors.append(f"Exit '{exit_id}' has invalid data format")
            continue
        if not exit_data.get("source"):
            errors.append(f"Exit '{exit_id}' is missing source room")
            continue
        if not exit_data.get("target"):
            errors.append(f"Exit '{exit_id}' is missing target room")
            continue
        if not exit_data.get("name"):
            warnings.append(f"Exit '{exit_id}' has no name")
        valid_exits[exit_id] = exit_data

    # ------------------------------------------------------------------
    # Connectivity validation (only exits that passed shape check)
    # ------------------------------------------------------------------
    room_connections = {rid: {"in": [], "out": []} for rid in valid_room_ids}

    for exit_id, exit_data in valid_exits.items():
        source = exit_data.get("source")
        target = exit_data.get("target")

        if source not in rooms:
            errors.append(f"Exit '{exit_id}' has invalid source room '{source}'")
        elif source in valid_room_ids:
            room_connections[source]["out"].append(exit_id)

        if target not in rooms:
            errors.append(f"Exit '{exit_id}' has invalid target room '{target}'")
        elif target in valid_room_ids:
            room_connections[target]["in"].append(exit_id)

    # Warn about isolated rooms
    for room_id, connections in room_connections.items():
        room_name = rooms[room_id].get("name", room_id)
        if not connections["in"] and not connections["out"]:
            warnings.append(f"Room '{room_name}' has no exits (isolated)")
        elif not connections["in"] and len(rooms) > 1:
            warnings.append(f"Room '{room_name}' has no incoming exits (unreachable)")

    # Warn about empty descriptions
    for room_id in valid_room_ids:
        room = rooms[room_id]
        if not room.get("description"):
            warnings.append(f"Room '{room.get('name', room_id)}' has no description")

    # Check for duplicate room names
    names = [
        rooms[rid].get("name", "")
        for rid in valid_room_ids
    ]
    duplicates = set(n for n in names if names.count(n) > 1 and n)
    for name in duplicates:
        warnings.append(f"Multiple rooms named '{name}'")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
