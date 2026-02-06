"""
Trigger execution engine for the trigger system.

This module provides the core trigger execution functionality:
- Trigger validation
- Trigger execution
- Error handling and logging
"""

import logging
from typing import Dict, Any, Tuple, List, Optional

from .trigger_actions import ACTION_REGISTRY
from .v5_conditions import check_condition

logger = logging.getLogger(__name__)


class TriggerError(Exception):
    """Exception raised for trigger execution errors."""

    pass


VALID_TRIGGER_TYPES = {"entry", "exit", "timed", "interaction"}


def validate_trigger(trigger_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate trigger data structure.

    Args:
        trigger_data: Dictionary containing trigger configuration

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
        If valid, error_message is None
    """
    # Check required fields
    if not isinstance(trigger_data, dict):
        return False, "Trigger data must be a dictionary"

    required_fields = {"type", "action", "parameters"}
    missing_fields = required_fields - set(trigger_data.keys())
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    # Validate trigger type
    trigger_type = trigger_data.get("type")
    if trigger_type not in VALID_TRIGGER_TYPES:
        return (
            False,
            f"Invalid trigger type '{trigger_type}'. Must be one of: {', '.join(VALID_TRIGGER_TYPES)}",
        )

    # Validate action exists in registry
    action_name = trigger_data.get("action")
    if action_name not in ACTION_REGISTRY:
        return (
            False,
            f"Unknown action '{action_name}'. Available actions: {', '.join(ACTION_REGISTRY.keys())}",
        )

    # Validate parameters is a dict
    parameters = trigger_data.get("parameters")
    if not isinstance(parameters, dict):
        return (
            False,
            f"Parameters must be a dictionary, got {type(parameters).__name__}",
        )

    # Check enabled field if present
    enabled = trigger_data.get("enabled", True)
    if not isinstance(enabled, bool):
        return False, "Enabled field must be a boolean"

    # Validate conditions if present
    conditions = trigger_data.get("conditions", [])
    if conditions:
        if not isinstance(conditions, list):
            return False, "conditions must be a list"

        from .v5_conditions import list_condition_types

        valid_conditions = list_condition_types()

        for condition in conditions:
            if not isinstance(condition, dict):
                return False, "each condition must be a dictionary"
            if "type" not in condition:
                return False, "condition missing 'type' field"
            if condition["type"] not in valid_conditions:
                return False, f"invalid condition type: {condition['type']}"

    # Validate timed trigger has interval
    if trigger_data.get("type") == "timed":
        interval = trigger_data.get("interval")
        if not interval or not isinstance(interval, int) or interval < 10:
            return False, "timed triggers must have interval >= 10 seconds"

    return True, None


def execute_trigger(trigger_data: Dict[str, Any], room, character, **context) -> bool:
    """
    Execute a single trigger.

    Args:
        trigger_data: Dictionary containing trigger configuration
        room: The room where the trigger is firing
        character: The character who triggered it
        **context: Additional context (e.g., target_location for exit triggers)

    Returns:
        bool: True if trigger executed successfully, False otherwise
    """
    # Validate trigger data
    is_valid, error_message = validate_trigger(trigger_data)
    if not is_valid:
        logger.warning(f"Skipping invalid trigger: {error_message}")
        return False

    # Check if trigger is enabled
    if not trigger_data.get("enabled", True):
        logger.debug(f"Skipping disabled trigger: {trigger_data.get('id', 'unknown')}")
        return False

    action_name = trigger_data["action"]
    parameters = trigger_data["parameters"]

    # Get the action function from registry
    action_func = ACTION_REGISTRY.get(action_name)
    if not action_func:
        logger.error(f"Action '{action_name}' not found in registry")
        return False

    # Prepare parameters based on action type
    try:
        if action_name == "send_message":
            # Send message to the character
            message = parameters.get("message", "")
            if message:
                action_func(character, message)
                logger.debug(f"Executed send_message trigger for {character}")

        elif action_name == "emit_message":
            # Emit message to room
            message = parameters.get("message", "")
            if message:
                action_func(room, message, exclude=[character])
                logger.debug(f"Executed emit_message trigger in {room}")

        elif action_name == "set_attribute":
            # Set attribute on room or character
            target = parameters.get("target", "room")  # "room" or "character"
            attr_name = parameters.get("attr_name", "")
            value = parameters.get("value")

            if attr_name:
                if target == "character" and character:
                    action_func(character, attr_name, value)
                else:
                    action_func(room, attr_name, value)
                logger.debug(
                    f"Executed set_attribute trigger: {target}.{attr_name} = {value}"
                )

        else:
            # Unknown action - should not reach here due to validation
            logger.warning(f"Unhandled action type: {action_name}")
            return False

        return True

    except Exception as e:
        logger.exception(
            f"Error executing trigger {trigger_data.get('id', 'unknown')}: {e}"
        )
        return False


def execute_triggers(
    room, trigger_type: str, character, trigger_id: Optional[str] = None, **context
) -> Tuple[int, int]:
    """
    Execute all triggers of a specific type for a room.

    Args:
        room: The room where triggers should fire
        trigger_type: Type of trigger to execute ("entry", "exit", "timed", "interaction")
        character: The character who triggered the event
        trigger_id: Optional specific trigger ID to execute (for timed triggers)
        **context: Additional context (e.g., target_location for exit triggers)

    Returns:
        Tuple of (executed_count: int, failed_count: int)
    """
    # Get triggers from room.db.triggers (default to empty list)
    triggers = getattr(room.db, "triggers", None)
    if not triggers:
        return 0, 0

    if not isinstance(triggers, list):
        logger.warning(f"Room {room} has invalid triggers data (not a list)")
        return 0, 0

    executed_count = 0
    failed_count = 0

    for trigger_data in triggers:
        # Filter by trigger type
        if trigger_data.get("type") != trigger_type:
            continue

        # Filter by trigger_id if specified (for timed triggers)
        if trigger_id and trigger_data.get("id") != trigger_id:
            continue

        # Check conditions
        conditions = trigger_data.get("conditions", [])
        conditions_met = True
        for condition in conditions:
            if not check_condition(
                condition.get("type"),
                condition.get("parameters", {}),
                character=character,
                room=room,
            ):
                conditions_met = False
                break

        if not conditions_met:
            continue

        # Execute the trigger
        success = execute_trigger(trigger_data, room, character, **context)
        if success:
            executed_count += 1
        else:
            failed_count += 1

    if executed_count > 0 or failed_count > 0:
        logger.info(
            f"Executed {executed_count} {trigger_type} triggers in {room} ({failed_count} failed)"
        )

    return executed_count, failed_count
