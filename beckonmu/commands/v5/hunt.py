"""
V5 Hunting Commands

Commands for hunting and feeding mechanics with AI Storyteller integration.
"""

from evennia import Command
from .utils.hunting_utils import (
    hunt_prey,
    get_predator_hunting_bonus,
    generate_hunting_opportunity,
    HUNTING_DIFFICULTIES
)
from .utils.blood_utils import get_hunger
from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY,
    GOLD, RESET, BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR,
    CIRCLE_FILLED
)


class CmdHunt(Command):
    """
    Hunt for prey to feed upon.

    Usage:
        +hunt [<location>]
        +hunt/quick [<location>]
        +hunt/ai [<location>]

    Locations:
        club       - Nightclubs, bars, scenes (Difficulty 3)
        street     - Streets, alleys (Difficulty 4)
        residential - Residential areas (Difficulty 5)
        hospital   - Hospitals, medical facilities (Difficulty 6)
        secured    - Gated communities (Difficulty 7)
        rural      - Rural/wilderness areas (Difficulty 4)

    Switches:
        /quick - Quick automated hunt (single roll)
        /ai    - AI Storyteller guided hunt (interactive)

    Examples:
        +hunt club
        +hunt/quick street
        +hunt/ai residential
    """

    key = "+hunt"
    aliases = ["hunt"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Execute hunt command."""
        caller = self.caller

        # Check if character has vampire data
        if not hasattr(caller.db, 'vampire') or not caller.db.vampire:
            caller.msg("|rYou are not a vampire!|n")
            return

        # Parse location
        location = self.args.strip().lower() if self.args else "street"
        if location not in HUNTING_DIFFICULTIES:
            valid_locations = ", ".join(HUNTING_DIFFICULTIES.keys())
            caller.msg(f"|rInvalid location. Valid locations: {valid_locations}|n")
            return

        # Check Hunger level (no need to hunt if not hungry)
        hunger = get_hunger(caller)
        if hunger == 0:
            caller.msg("|gYou are fully sated. You do not need to hunt right now.|n")
            return

        # Get Predator Type bonuses
        predator_info = get_predator_hunting_bonus(caller)

        # Check if using /ai switch for AI Storyteller
        if "ai" in self.switches:
            self._ai_storyteller_hunt(location, predator_info)
            return

        # Quick hunt (default)
        self._quick_hunt(location, predator_info)

    def _quick_hunt(self, location, predator_info):
        """Quick automated hunting (single roll)."""
        caller = self.caller

        # Determine skill to use (based on Predator Type or default to Streetwise)
        vamp = caller.db.vampire if hasattr(caller.db, 'vampire') else {}
        predator_type = vamp.get('predator_type', None)

        # Map predator types to skills
        predator_skills = {
            "Alleycat": "stealth",
            "Sandman": "stealth",
            "Scene Queen": "streetwise",
            "Siren": "persuasion",
            "Consensualist": "persuasion",
            "Bagger": "streetwise",
            "Farmer": "animal_ken"
        }

        skill_name = predator_skills.get(predator_type, "streetwise")

        # Perform hunt
        result = hunt_prey(
            caller,
            location=location,
            skill_name=skill_name,
            predator_type_bonus=predator_info.get("bonus_dice", 0),
            kill=False  # Default: don't kill
        )

        # Display results
        self._display_hunt_result(result, location)

    def _ai_storyteller_hunt(self, location, predator_info):
        """AI Storyteller guided hunt (interactive)."""
        from .utils.ai_storyteller import get_storyteller

        caller = self.caller
        storyteller = get_storyteller()

        # Start AI storyteller session
        scene = storyteller.start_hunt(caller, location)

        # Display opening scene
        self._display_ai_scene(scene)

        caller.msg(
            f"\n{GOLD}[AI Storyteller Mode Active]{RESET}\n"
            f"Describe your actions using |y+huntaction <your action>|n\n"
            f"Or type |y+huntcancel|n to abandon this hunt."
        )

    def _display_ai_scene(self, scene):
        """Display AI Storyteller scene."""
        caller = self.caller

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {BLOOD_RED}{CIRCLE_FILLED}{RESET} {PALE_IVORY}THE HUNT{RESET}{' ' * 65}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")
        output.append("")
        output.append(scene["narrative"])
        output.append("")
        if scene.get("prompt"):
            output.append(f"{GOLD}>{RESET} {scene['prompt']}")

        caller.msg("\n".join(output))

    def _display_hunting_scene(self, opportunity):
        """Display the hunting opportunity scene."""
        caller = self.caller

        output = []
        output.append(f"{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {BLOOD_RED}{CIRCLE_FILLED}{RESET} {PALE_IVORY}HUNTING SCENE{RESET}{' ' * 60}{BOX_V}")
        output.append(f"{BOX_V} {GOLD}Location:{RESET} {opportunity['location'].title()}{' ' * (67 - len(opportunity['location']))}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")
        output.append("")
        output.append(f"{PALE_IVORY}You spot a potential vessel:{RESET}")
        output.append(f"  {opportunity['prey_description']}")
        output.append(f"  {opportunity['hook']}")
        output.append("")
        output.append(f"{PALE_IVORY}Resonance:{RESET} {GOLD}{opportunity['resonance']['type']}{RESET} ({opportunity['resonance']['intensity_name']})")
        output.append(f"{PALE_IVORY}Difficulty:{RESET} {opportunity['difficulty']}")
        output.append("")
        output.append(f"{SHADOW_GREY}Potential Risks:{RESET}")
        for risk in opportunity['risks']:
            output.append(f"  {SHADOW_GREY}- {risk['desc']} ({risk['severity']}){RESET}")

        caller.msg("\n".join(output))

    def _display_hunt_result(self, result, location):
        """Display hunting results."""
        caller = self.caller

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")

        if result["hunting_success"]:
            output.append(f"{BOX_V} {BLOOD_RED}{CIRCLE_FILLED}{RESET} {PALE_IVORY}SUCCESSFUL HUNT{RESET}{' ' * 58}{BOX_V}")
        else:
            output.append(f"{BOX_V} {SHADOW_GREY}{CIRCLE_FILLED}{RESET} {PALE_IVORY}HUNT FAILED{RESET}{' ' * 62}{BOX_V}")

        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")
        output.append("")
        output.append(result["message"])

        caller.msg("\n".join(output))


class CmdFeed(Command):
    """
    Feed from a vessel.

    Usage:
        +feed <target>
        +feed/kill <target>

    This command is used when you have a specific vessel in mind (NPC or PC).
    For hunting to find prey, use +hunt instead.

    Switches:
        /kill - Drain the vessel completely (grants more blood, may affect Humanity)

    Examples:
        +feed John
        +feed/kill the homeless man
    """

    key = "+feed"
    aliases = ["feed"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Execute feed command."""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +feed <target>")
            return

        # Check if character has vampire data
        if not hasattr(caller.db, 'vampire') or not caller.db.vampire:
            caller.msg("|rYou are not a vampire!|n")
            return

        # This is a placeholder for feeding from specific targets
        # In a full implementation, this would handle:
        # 1. Finding the target in the room
        # 2. Checking if feeding is appropriate (consent, NPC vs PC)
        # 3. Rolling for feeding success
        # 4. Applying results

        caller.msg(
            f"|yFeeding from specific targets requires AI Storyteller or staff approval.|n\n"
            f"For automated hunting, use |w+hunt|n instead."
        )


class CmdHuntingInfo(Command):
    """
    Display information about hunting and feeding.

    Usage:
        +huntinfo
        +huntinfo <location>

    Shows hunting difficulties, your Predator Type bonuses, and current Hunger.
    """

    key = "+huntinfo"
    aliases = ["huntinfo"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Execute huntinfo command."""
        caller = self.caller

        # Check if character has vampire data
        if not hasattr(caller.db, 'vampire') or not caller.db.vampire:
            caller.msg("|rYou are not a vampire!|n")
            return

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {BLOOD_RED}{CIRCLE_FILLED}{RESET} {PALE_IVORY}HUNTING INFORMATION{RESET}{' ' * 54}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

        # Current Hunger
        hunger = get_hunger(caller)
        output.append(f"\n{PALE_IVORY}Current Hunger:{RESET} {BLOOD_RED}{'●' * hunger}{SHADOW_GREY}{'○' * (5 - hunger)}{RESET} ({hunger}/5)")

        # Predator Type Info
        vamp = caller.db.vampire if hasattr(caller.db, 'vampire') else {}
        predator_type = vamp.get('predator_type', 'Unknown')
        predator_info = get_predator_hunting_bonus(caller)

        output.append(f"\n{PALE_IVORY}Predator Type:{RESET} {GOLD}{predator_type}{RESET}")
        output.append(f"{PALE_IVORY}Hunting Bonus:{RESET} +{predator_info.get('bonus_dice', 0)} dice")
        output.append(f"{PALE_IVORY}Preferred Locations:{RESET} {', '.join(predator_info.get('preferred_locations', ['none']))}")

        if predator_info.get('special_ability'):
            output.append(f"{PALE_IVORY}Special:{RESET} {predator_info['special_ability']}")

        # Hunting Difficulties
        output.append(f"\n{PALE_IVORY}Hunting Difficulties by Location:{RESET}")
        for location, diff in sorted(HUNTING_DIFFICULTIES.items()):
            if location != "default":
                output.append(f"  {GOLD}{location.title():<15}{RESET} Difficulty {diff}")

        output.append(f"\n{SHADOW_GREY}Use |w+hunt <location>|x to hunt for prey.{RESET}")

        caller.msg("\n".join(output))


class CmdHuntAction(Command):
    """
    Perform an action during an AI Storyteller hunt.

    Usage:
        +huntaction <your action>

    Examples:
        +huntaction I approach them casually, striking up a conversation
        +huntaction I stalk them from the shadows, waiting for the right moment
        +huntaction I use Dominate to mesmerize them
    """

    key = "+huntaction"
    aliases = ["huntaction"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Execute hunt action."""
        from .utils.ai_storyteller import get_storyteller

        caller = self.caller

        if not self.args:
            caller.msg("Usage: +huntaction <your action>")
            return

        storyteller = get_storyteller()
        session = storyteller.get_active_session(caller)

        if not session:
            caller.msg("|rYou don't have an active hunt. Use |w+hunt/ai <location>|r to start.|n")
            return

        # Process player's action
        response = storyteller.process_player_input(caller, self.args.strip())

        if response.get("error"):
            caller.msg(f"|r{response['error']}|n")
            return

        # Display storyteller response
        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {BLOOD_RED}{CIRCLE_FILLED}{RESET} {PALE_IVORY}THE HUNT{RESET}{' ' * 65}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")
        output.append("")
        output.append(response["narrative"])
        output.append("")

        if response.get("prompt"):
            output.append(f"{GOLD}>{RESET} {response['prompt']}")

        if response.get("requires_roll"):
            output.append(f"\n{SHADOW_GREY}(You would roll {response['roll_type']} here - dice integration pending){RESET}")

        if response.get("session_complete"):
            output.append(f"\n{GOLD}[Hunt Complete]{RESET}")

        caller.msg("\n".join(output))


class CmdHuntCancel(Command):
    """
    Cancel an active AI Storyteller hunt.

    Usage:
        +huntcancel

    Abandons your current hunt and removes you from the AI Storyteller session.
    """

    key = "+huntcancel"
    aliases = ["huntcancel"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Cancel active hunt."""
        from .utils.ai_storyteller import get_storyteller

        caller = self.caller
        storyteller = get_storyteller()

        if storyteller.cancel_hunt(caller):
            caller.msg(f"{GOLD}You abandon the hunt and fade back into the shadows.{RESET}")
        else:
            caller.msg("|rYou don't have an active hunt to cancel.|n")
