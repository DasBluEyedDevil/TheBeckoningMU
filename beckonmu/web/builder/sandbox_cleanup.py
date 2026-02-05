"""
Sandbox cleanup utilities for deleting all rooms/exits created for a project.
Can be called from web API or in-game commands.
"""

from evennia.utils import search
from evennia.utils.utils import run_in_main_thread
import threading


def _do_cleanup_in_main_thread(project_id):
    """
    Actually perform cleanup in Evennia's main thread.
    Returns (success, result_dict).
    """
    try:
        from beckonmu.web.builder.models import BuildProject

        # Find all objects tagged with this project
        project_tag = f"project_{project_id}"

        # Search for rooms
        rooms = search.search_object(
            "", typeclass="beckonmu.typeclasses.rooms.Room", tags=[project_tag]
        )

        # Search for exits
        exits = search.search_object(
            "", typeclass="beckonmu.typeclasses.exits.Exit", tags=[project_tag]
        )

        # Search for objects
        objects = search.search_object("", tags=[project_tag])
        # Filter out rooms and exits (we already counted them)
        objects = [o for o in objects if o not in rooms and o not in exits]

        deleted_counts = {"rooms": 0, "exits": 0, "objects": 0, "errors": []}

        # Delete exits first (they reference rooms)
        for exit_obj in list(exits):
            try:
                exit_obj.delete()
                deleted_counts["exits"] += 1
            except Exception as e:
                deleted_counts["errors"].append(f"Exit {exit_obj.id}: {e}")

        # Delete objects
        for obj in list(objects):
            try:
                obj.delete()
                deleted_counts["objects"] += 1
            except Exception as e:
                deleted_counts["errors"].append(f"Object {obj.id}: {e}")

        # Delete rooms last
        for room in list(rooms):
            try:
                room.delete()
                deleted_counts["rooms"] += 1
            except Exception as e:
                deleted_counts["errors"].append(f"Room {room.id}: {e}")

        return True, deleted_counts

    except Exception as e:
        return False, {"error": str(e)}


def cleanup_sandbox_for_project(project_id):
    """
    Clean up all sandbox objects for a project.

    Args:
        project_id: BuildProject ID

    Returns:
        (success: bool, result: dict)
        result contains: deleted_rooms, deleted_exits, deleted_objects, errors
    """
    from beckonmu.web.builder.models import BuildProject

    try:
        project = BuildProject.objects.get(id=project_id)
    except BuildProject.DoesNotExist:
        return False, {"error": "Project not found"}

    if not project.sandbox_room_id:
        return False, {"error": "Project has no active sandbox"}

    # Run in main thread
    result = None
    error = None
    event = threading.Event()

    def wrapper():
        nonlocal result, error
        try:
            success, result = _do_cleanup_in_main_thread(project_id)
            if not success:
                error = result.get("error")
        except Exception as e:
            error = str(e)
        finally:
            event.set()

    run_in_main_thread(wrapper)
    event.wait(timeout=30)

    if error:
        return False, {"error": error}

    # Update project status
    project.sandbox_room_id = None
    project.save(update_fields=["sandbox_room_id"])

    # Reset status from 'built' to 'approved' if needed
    if project.status == "built":
        # We can't use can_transition_to because built -> approved is valid
        # but mark_built() only goes forward. Direct update:
        project.status = "approved"
        project.save(update_fields=["status"])

    return True, {
        "deleted_rooms": result.get("rooms", 0),
        "deleted_exits": result.get("exits", 0),
        "deleted_objects": result.get("objects", 0),
        "errors": result.get("errors", []),
    }
