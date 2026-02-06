"""
Whitelisted trigger actions for the trigger system.

This module defines safe actions that can be executed by room triggers.
All actions are pure functions that accept only primitive types and
perform no unsafe operations (no file I/O, no network calls, no eval/exec).
"""

import logging

logger = logging.getLogger(__name__)


def send_message(obj, message):
    """
    Send a message to a specific object (typically a character).

    Args:
        obj: The target object to receive the message (must have msg() method)
        message (str): The message text to send

    Returns:
        None
    """
    if obj and hasattr(obj, "msg") and callable(obj.msg):
        try:
            obj.msg(message)
        except Exception as e:
            logger.error(f"Error sending message to {obj}: {e}")


def emit_message(location, message, exclude=None):
    """
    Emit a message to all objects in a location.

    Args:
        location: The room/location to emit the message in (must have msg_contents() method)
        message (str): The message text to emit
        exclude (list, optional): List of objects to exclude from receiving the message

    Returns:
        None
    """
    if exclude is None:
        exclude = []

    if (
        location
        and hasattr(location, "msg_contents")
        and callable(location.msg_contents)
    ):
        try:
            location.msg_contents(message, exclude=exclude)
        except Exception as e:
            logger.error(f"Error emitting message in {location}: {e}")


def set_attribute(obj, attr_name, value):
    """
    Set a database attribute on an object.

    Args:
        obj: The target object (must have db attribute)
        attr_name (str): The name of the attribute to set
        value: The value to set (must be JSON-serializable primitive)

    Returns:
        None
    """
    if obj and hasattr(obj, "db"):
        try:
            setattr(obj.db, attr_name, value)
        except Exception as e:
            logger.error(f"Error setting attribute {attr_name} on {obj}: {e}")


def list_actions():
    """
    Return a list of available action names for UI display.

    Returns:
        list: List of action name strings
    """
    return list(ACTION_REGISTRY.keys())


# Registry mapping action names to their handler functions
ACTION_REGISTRY = {
    "send_message": send_message,
    "emit_message": emit_message,
    "set_attribute": set_attribute,
}
