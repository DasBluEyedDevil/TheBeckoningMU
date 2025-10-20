# -*- coding: utf-8 -*-
"""
Connection screen module for TheBeckoningMU.

This module defines the text players see when connecting to the MUD before
they are logged in. It uses the V:tM Gothic theme established in
beckonmu/world/ansi_theme.py.

See: THEMING_GUIDE.md for complete aesthetics specification

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.
"""

from django.conf import settings
from evennia import utils

# Connection screen shown before login
CONNECTION_SCREEN = """
|[R
      ██╗   ██╗ █████╗ ███╗   ███╗██████╗ ██╗██████╗ ███████╗
      ██║   ██║██╔══██╗████╗ ████║██╔══██╗██║██╔══██╗██╔════╝
      ██║   ██║███████║██╔████╔██║██████╔╝██║██████╔╝█████╗
      ╚██╗ ██╔╝██╔══██║██║╚██╔╝██║██╔═══╝ ██║██╔══██╗██╔══╝
       ╚████╔╝ ██║  ██║██║ ╚═╝ ██║██║     ██║██║  ██║███████╗
        ╚═══╝  ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
|n
|[r            ╔════════════════════════════════════════╗
|[r            ║  |WT H E   B E C K O N I N G           |[r║
|[r            ║  |wThe Masquerade - 5th Edition       |[r║
|[r            ╚════════════════════════════════════════╝|n

|x┌──────────────────────────────────────────────────────────────┐
|x│  |W"The night has a thousand eyes, and the blood has a     |x│
|x│  |W thousand secrets. Welcome, Kindred, to your Danse      |x│
|x│  |W Macabre."|n                                             |x│
|x└──────────────────────────────────────────────────────────────┘|n

         |wConnect with:|n  connect <username> <password>
         |wCreate char:|n  create <username> <password>

|[R═══════════════════════════════════════════════════════════════════|n
"""

# Post-logout screen (shown after disconnect)
POST_DISCONNECT_SCREEN = """
|x
╔═══════════════════════════════════════════════════════════════╗
║  |wYou fade into the shadows, leaving only whispers...       |x║
╚═══════════════════════════════════════════════════════════════╝|n

|wThank you for playing TheBeckoningMU. Until the next night...|n
"""
