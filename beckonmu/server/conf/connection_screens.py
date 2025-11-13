# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function 'connection_screen()', taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings

from evennia import utils
from world.ansi_theme import (
    BLOOD_RED, DARK_RED, BONE_WHITE, SHADOW_GREY, PALE_IVORY, GOLD, RESET,
    DBOX_H, DBOX_V, DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR, FLEUR_DE_LIS
)

CONNECTION_SCREEN = f"""{DARK_RED}
{DBOX_TL}{DBOX_H * 78}{DBOX_TR}
{DBOX_V}{' ' * 78}{DBOX_V}
{DBOX_V}                        {BONE_WHITE}THE BECKONING MUD{DARK_RED}                                 {DBOX_V}
{DBOX_V}{' ' * 78}{DBOX_V}
{DBOX_V}             {SHADOW_GREY}[Vampire: The Masquerade 5th Edition]{DARK_RED}                      {DBOX_V}
{DBOX_V}{' ' * 78}{DBOX_V}
{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}

           {BLOOD_RED}
                   .d:....:h.
                .:!!!!!!!!!!!!:.
           .::!!!!!!!!!!!!!!!!!!!!::.
    ..::!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!::..
{RESET}
  {SHADOW_GREY}The night calls. The Beast stirs. The Camarilla gathers.{RESET}

{SHADOW_GREY}{DBOX_H * 80}{RESET}

  {GOLD}→{RESET} To connect: {BONE_WHITE}connect <username> <password>{RESET}
  {GOLD}→{RESET} To create:  {BONE_WHITE}create <username> <password>{RESET}
  {GOLD}→{RESET} For help:   {BONE_WHITE}help{RESET}

  {SHADOW_GREY}If you have spaces in your username, enclose it in quotes.{RESET}

{SHADOW_GREY}{DBOX_H * 80}{RESET}

  {BLOOD_RED}{FLEUR_DE_LIS}{RESET} {PALE_IVORY}Original Work by lcanady (github/lcanady){RESET}
  {SHADOW_GREY}Modifications by Devil and erratic{RESET}
  {SHADOW_GREY}Powered By Evennia v{utils.get_evennia_version("short")}{RESET}

{DARK_RED}{DBOX_BL}{DBOX_H * 80}{DBOX_BR}{RESET}
"""

