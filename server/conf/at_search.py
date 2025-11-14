"""
Custom search result handler for TheBeckoningMU.

This overrides Evennia's default at_search_result to provide:
1. Colored/styled error messages
2. Cleaner display of multimatch results
"""

from collections import defaultdict
from django.utils.translation import gettext as _


# Template for multimatch display
_MULTIMATCH_TEMPLATE = " |w{number}|n-|c{name}|n{aliases}{info}\n"


def at_search_result(matches, caller, query="", quiet=False, **kwargs):
    """
    Custom search result handler with styled error messages.

    This is called for both object searches AND command not-found errors.

    Args:
        matches (list): List of matched objects/commands (0, 1, or more)
        caller (Object): The searching object
        query (str): The search query
        quiet (bool): If True, suppress error messages

    Keyword Args:
        nofound_string (str): Custom not-found message
        multimatch_string (str): Custom multimatch message

    Returns:
        Object/Command or None: Single match or None
    """

    error = ""
    if not matches:
        # No results - styled error
        error = kwargs.get("nofound_string") or (
            "|rError:|n Could not find |y'{query}'|n."
        ).format(query=query)
        matches = None

    elif len(matches) > 1:
        # Multiple matches
        multimatch_string = kwargs.get("multimatch_string")
        if multimatch_string:
            error = "%s\n" % multimatch_string
        else:
            error = (
                "|yMultiple matches|n for |y'{query}'|n (please be more specific):\n"
            ).format(query=query)

        # Group results by display name
        grouped_matches = defaultdict(list)
        for item in matches:
            group_key = (
                item.get_display_name(caller)
                if hasattr(item, "get_display_name")
                else query
            )
            grouped_matches[group_key].append(item)

        for key, match_list in grouped_matches.items():
            for num, result in enumerate(match_list):
                # Get aliases (could be AliasHandler or list)
                if hasattr(result.aliases, "all"):
                    # Typeclass entity with AliasHandler
                    aliases = result.aliases.all(return_objs=True)
                    aliases = [
                        alias.db_key
                        for alias in aliases
                        if alias.db_category != "plural_key"
                    ]
                else:
                    # Command with list of aliases
                    aliases = result.aliases

                error += _MULTIMATCH_TEMPLATE.format(
                    number=num + 1,
                    name=key,
                    aliases=" [{alias}]".format(
                        alias="|w;|n".join(aliases)
                    ) if aliases else "",
                    info=result.get_extra_info(caller),
                )
        matches = None

    else:
        # Exactly one match
        matches = matches[0]

    if error and not quiet:
        caller.msg(error.strip())

    return matches
