"""
Server startup/shutdown hooks for The Beckoning MU

This module is called at server startup and shutdown.
"""

def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    # Patch the cmdhandler to use our custom error messages
    _patch_command_error_messages()


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def _patch_command_error_messages():
    """
    Monkey-patch Evennia's cmdhandler to provide styled error messages.
    """
    from evennia.commands import cmdhandler
    from evennia.utils.utils import string_suggestions

    # Store original function
    original_cmdhandler = cmdhandler.cmdhandler

    def custom_cmdhandler(caller, raw_string, *args, **kwargs):
        """
        Wrapper that intercepts command-not-found errors.
        """
        # Get the cmdset
        cmdset = caller.cmdset.current

        # Try original handler first
        result = original_cmdhandler(caller, raw_string, *args, **kwargs)

        # If command wasn't found, Evennia already sent the error message
        # We need to intercept BEFORE that happens
        return result

    # Actually, let's patch the specific error message function instead
    # The error message comes from cmdhandler._MSG_NO_COMMAND_MATCH

    def styled_no_command_message(caller, cmdname, cmdset):
        """
        Custom styled "command not found" message.
        """
        # Get unique command keys only (no duplicate aliases)
        all_cmds = set()
        for cmd in cmdset:
            all_cmds.add(cmd.key.lower())

        # Find suggestions
        suggestions = string_suggestions(cmdname, all_cmds, cutoff=0.7, maxnum=3)

        if suggestions:
            if len(suggestions) == 1:
                msg = f"|rCommand '|n{cmdname}|r' is not available.|n Maybe you meant |w\"{suggestions[0]}\"|n?"
            else:
                suggestions_str = '|n, |w'.join(f'"{sug}"' for sug in suggestions)
                msg = f"|rCommand '|n{cmdname}|r' is not available.|n Maybe you meant {suggestions_str}?"
        else:
            msg = f"|rCommand '|n{cmdname}|r' is not available.|n Type |whelp|n for available commands."

        caller.msg(msg)

    # Patch it
    if hasattr(cmdhandler, '_MSG_NO_COMMAND_MATCH'):
        cmdhandler._MSG_NO_COMMAND_MATCH = styled_no_command_message
