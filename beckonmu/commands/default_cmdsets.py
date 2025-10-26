"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia.commands.default import cmdset_character, cmdset_account, cmdset_session, cmdset_unloggedin


class CharacterCmdSet(cmdset_character.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        import importlib
        BBSCmdSet = getattr(importlib.import_module("bbs.commands"), "BBSCmdSet")
        self.add(BBSCmdSet)

        JobsCmdSet = getattr(importlib.import_module("jobs.cmdset"), "JobsCmdSet")
        self.add(JobsCmdSet)

        # Add staff chargen commands for builders and admins
        from commands.chargen import ChargenCmdSet
        self.add(ChargenCmdSet)

        # Add V5 dice commands
        from commands.v5.dice import CmdRoll, CmdRollStat, CmdRouseCheck
        self.add(CmdRoll)
        self.add(CmdRollStat)
        self.add(CmdRouseCheck)

        # Add V5 sheet commands
        from commands.v5.sheet import CmdSheet, CmdSheetShort
        self.add(CmdSheet)
        self.add(CmdSheetShort)


class AccountCmdSet(cmdset_account.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(cmdset_unloggedin.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(cmdset_session.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
