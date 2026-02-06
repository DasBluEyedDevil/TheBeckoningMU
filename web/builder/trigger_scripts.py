"""
Trigger script management for timed room triggers.

Handles creation, deletion, and lifecycle of Evennia Scripts
attached to rooms for timed trigger execution.
"""

import logging
from typing import List, Dict, Any, Optional

from evennia.utils.create import create_script
from evennia.utils.search import search_script

logger = logging.getLogger(__name__)


def create_timed_trigger(room, trigger_data: Dict[str, Any]) -> Optional[Any]:
    """
    Create a timed trigger script attached to a room.

    Args:
        room: The Evennia room object to attach trigger to
        trigger_data: Trigger configuration dict with:
            - id: unique trigger identifier
            - interval: seconds between firings (default 300)
            - action: action name (from ACTION_REGISTRY)
            - parameters: dict of action parameters
            - enabled: bool (default True)

    Returns:
        The created Script object, or None if creation failed
    """
    trigger_id = trigger_data.get("id")
    if not trigger_id:
        logger.error("Cannot create timed trigger without id")
        return None

    # Check if script already exists for this trigger
    existing = search_script(f"trigger_{trigger_id}")
    if existing:
        logger.warning(f"Timed trigger {trigger_id} already exists, skipping")
        return existing[0]

    interval = trigger_data.get("interval", 300)
    if interval < 10:
        logger.warning(
            f"Trigger {trigger_id} interval {interval}s too short, using 10s minimum"
        )
        interval = 10

    try:
        script = create_script(
            typeclass="typeclasses.scripts.RoomTriggerScript",
            key=f"trigger_{trigger_id}",
            obj=room,
            interval=interval,
            persistent=True,
            repeats=0,  # Infinite
            start_delay=False,
        )

        # Store trigger configuration
        script.db.trigger_id = trigger_id
        script.db.trigger_action = trigger_data.get("action")
        script.db.trigger_parameters = trigger_data.get("parameters", {})

        logger.info(
            f"Created timed trigger {trigger_id} on room {room.id} (interval: {interval}s)"
        )
        return script

    except Exception as e:
        logger.exception(f"Failed to create timed trigger {trigger_id}: {e}")
        return None


def delete_timed_trigger(trigger_id: str) -> bool:
    """
    Delete a specific timed trigger script by trigger ID.

    Args:
        trigger_id: The unique trigger identifier

    Returns:
        True if deleted or didn't exist, False on error
    """
    try:
        scripts = search_script(f"trigger_{trigger_id}")
        for script in scripts:
            script.stop()
            script.delete()
            logger.info(f"Deleted timed trigger {trigger_id}")
        return True
    except Exception as e:
        logger.exception(f"Failed to delete timed trigger {trigger_id}: {e}")
        return False


def delete_timed_triggers_for_room(room) -> int:
    """
    Delete all timed trigger scripts attached to a room.

    Args:
        room: The Evennia room object

    Returns:
        Number of scripts deleted
    """
    count = 0
    try:
        # Find scripts where obj is this room
        from evennia.scripts.models import ScriptDB

        scripts = ScriptDB.objects.filter(obj=room)

        for script in scripts:
            # Only delete our trigger scripts
            if (
                hasattr(script, "db")
                and hasattr(script.db, "trigger_id")
                and script.db.trigger_id
            ):
                script.stop()
                script.delete()
                count += 1

        if count > 0:
            logger.info(f"Deleted {count} timed triggers for room {room.id}")
        return count

    except Exception as e:
        logger.exception(f"Failed to delete timed triggers for room {room.id}: {e}")
        return count


def sync_timed_triggers_for_room(room) -> Dict[str, Any]:
    """
    Synchronize timed triggers for a room based on room.db.triggers.

    Creates scripts for new timed triggers, deletes scripts for
    removed triggers, updates changed triggers.

    Args:
        room: The Evennia room object

    Returns:
        Dict with created, deleted, updated counts
    """
    results = {"created": 0, "deleted": 0, "updated": 0, "errors": []}

    try:
        triggers = room.db.triggers or []
        timed_trigger_ids = set()

        # Process current timed triggers
        for trigger in triggers:
            if trigger.get("type") != "timed":
                continue
            if not trigger.get("enabled", True):
                continue

            trigger_id = trigger.get("id")
            if not trigger_id:
                continue

            timed_trigger_ids.add(trigger_id)

            # Check if script exists
            existing = search_script(f"trigger_{trigger_id}")
            if not existing:
                # Create new script
                if create_timed_trigger(room, trigger):
                    results["created"] += 1
                else:
                    results["errors"].append(f"Failed to create {trigger_id}")

        # Find and delete orphaned scripts
        from evennia.scripts.models import ScriptDB

        existing_scripts = ScriptDB.objects.filter(obj=room)

        for script in existing_scripts:
            if (
                hasattr(script, "db")
                and hasattr(script.db, "trigger_id")
                and script.db.trigger_id
                and script.db.trigger_id not in timed_trigger_ids
            ):
                script.stop()
                script.delete()
                results["deleted"] += 1

        return results

    except Exception as e:
        logger.exception(f"Failed to sync timed triggers for room {room.id}: {e}")
        results["errors"].append(str(e))
        return results
