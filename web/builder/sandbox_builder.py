"""
Sandbox builder module - creates Evennia rooms and exits from map_data.

This module handles the actual creation of Evennia game objects from
web builder project data. It runs in the main thread via sandbox_bridge.
"""

import logging
from typing import Dict, Any, List, Optional

from evennia.utils.create import create_object
from evennia.utils.search import search_object

from beckonmu.typeclasses.rooms import Room
from beckonmu.typeclasses.exits import Exit

logger = logging.getLogger(__name__)


def build_sandbox_area(project_id: int, map_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create Evennia rooms and exits from web builder map_data.

    This function runs in Evennia's main thread and creates actual game objects:
    - A sandbox container room as the entry point
    - All rooms from map_data with V5 attributes
    - All exits connecting rooms

    Args:
        project_id: The BuildProject ID for tagging
        map_data: The project's map_data dictionary

    Returns:
        Dict containing:
        - sandbox_room_id: The entry room's database ID
        - room_count: Number of rooms created
        - exit_count: Number of exits created
        - room_map: Dict mapping web room_id to Evennia room object
    """
    rooms_data = map_data.get("rooms", {})
    exits_data = map_data.get("exits", {})

    if not rooms_data:
        raise ValueError("No rooms in project map_data")

    # Track created objects
    created_rooms: Dict[str, Room] = {}  # web room_id -> Evennia room
    room_count = 0
    exit_count = 0
    errors: List[str] = []

    # Create sandbox container room (entry point)
    sandbox_alias = f"_sandbox_{project_id}"
    sandbox_room = create_object(
        typeclass="beckonmu.typeclasses.rooms.Room",
        key=f"Builder Sandbox: Project {project_id}",
        aliases=[sandbox_alias],
        location=None,
    )
    sandbox_room.db.desc = f"Sandbox area for build project {project_id}."
    sandbox_room.tags.add("web_builder")
    sandbox_room.tags.add(f"project_{project_id}")
    sandbox_room.tags.add("sandbox")

    logger.info(f"Created sandbox container: {sandbox_room.id} ({sandbox_alias})")

    # Phase 1: Create all rooms
    for room_id, room_data in rooms_data.items():
        try:
            room_alias = f"_bld_{project_id}_{room_id}"
            room_name = room_data.get("name", "Unnamed Room")

            room = create_object(
                typeclass="beckonmu.typeclasses.rooms.Room",
                key=room_name,
                aliases=[room_alias],
                location=None,
            )

            # Set description
            room.db.desc = room_data.get("description", "")

            # Set V5 attributes
            v5 = room_data.get("v5", {})
            if v5.get("location_type"):
                room.db.location_type = v5["location_type"]
            if v5.get("day_night"):
                room.db.day_night = v5["day_night"]
            if v5.get("danger_level"):
                room.db.danger_level = v5["danger_level"]
            if v5.get("hunting_modifier") is not None:
                room.db.hunting_modifier = v5["hunting_modifier"]
            if v5.get("territory_owner"):
                room.db.territory_owner = v5["territory_owner"]

            # Set haven ratings if this is a haven
            if v5.get("location_type") == "haven":
                haven = v5.get("haven_ratings", {})
                if haven:
                    room.db.haven_security = haven.get("security", 0)
                    room.db.haven_size = haven.get("size", 0)
                    room.db.haven_luxury = haven.get("luxury", 0)
                    room.db.haven_warding = haven.get("warding", 0)
                    room.db.haven_location_hidden = haven.get("location_hidden", False)

            # Store triggers if present
            triggers = room_data.get("triggers", [])
            if triggers:
                room.db.triggers = triggers

            # Add tracking tags
            room.tags.add("web_builder")
            room.tags.add(f"project_{project_id}")
            room.tags.add("sandbox")

            created_rooms[room_id] = room
            room_count += 1

            logger.debug(f"Created room {room_id}: {room_name} (id: {room.id})")

        except Exception as e:
            error_msg = f"Failed to create room {room_id}: {e}"
            logger.exception(error_msg)
            errors.append(error_msg)
            # Continue with other rooms

    # Phase 2: Create exits between rooms
    for exit_id, exit_data in exits_data.items():
        try:
            source_id = exit_data.get("source")
            target_id = exit_data.get("target")

            if not source_id or not target_id:
                logger.warning(f"Exit {exit_id} missing source or target, skipping")
                continue

            # Look up source and target rooms
            source_room = created_rooms.get(source_id)
            target_room = created_rooms.get(target_id)

            if not source_room:
                # Try to find by alias (in case room was created previously)
                source_alias = f"_bld_{project_id}_{source_id}"
                found = search_object(source_alias)
                if found:
                    source_room = found[0]
                else:
                    logger.warning(f"Exit {exit_id}: source room {source_id} not found")
                    continue

            if not target_room:
                target_alias = f"_bld_{project_id}_{target_id}"
                found = search_object(target_alias)
                if found:
                    target_room = found[0]
                else:
                    logger.warning(f"Exit {exit_id}: target room {target_id} not found")
                    continue

            exit_name = exit_data.get("name", "exit")
            aliases = exit_data.get("aliases", [])

            # Create the exit
            exit_obj = create_object(
                typeclass="beckonmu.typeclasses.exits.Exit",
                key=exit_name,
                aliases=aliases,
                location=source_room,
                destination=target_room,
            )

            # Set exit description if provided
            exit_desc = exit_data.get("description", "")
            if exit_desc:
                exit_obj.db.desc = exit_desc

            # Set exit locks if provided
            locks = exit_data.get("locks", "")
            if locks:
                exit_obj.locks.add(locks)

            # Add tracking tags
            exit_obj.tags.add("web_builder")
            exit_obj.tags.add(f"project_{project_id}")
            exit_obj.tags.add("sandbox")

            exit_count += 1

            logger.debug(
                f"Created exit {exit_id}: {exit_name} ({source_id} -> {target_id})"
            )

        except Exception as e:
            error_msg = f"Failed to create exit {exit_id}: {e}"
            logger.exception(error_msg)
            errors.append(error_msg)
            # Continue with other exits

    # Build room_map for return (convert objects to IDs for JSON serialization)
    room_map = {web_id: room.id for web_id, room in created_rooms.items()}

    result = {
        "sandbox_room_id": sandbox_room.id,
        "room_count": room_count,
        "exit_count": exit_count,
        "room_map": room_map,
        "errors": errors if errors else None,
    }

    logger.info(
        f"Sandbox build complete for project {project_id}: "
        f"{room_count} rooms, {exit_count} exits"
    )

    return result
