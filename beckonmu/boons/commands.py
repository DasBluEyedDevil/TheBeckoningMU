"""
Boons System Commands

Commands for managing political favors and debts (Prestation) in Kindred society.
"""

from evennia import Command, default_cmds
from .utils import (
    get_or_create_ledger,
    offer_boon,
    accept_boon,
    decline_boon,
    call_in_boon,
    fulfill_boon,
    cancel_boon,
    dispute_boon,
    acknowledge_boon,
    get_boons_owed_by,
    get_boons_held_by,
    get_boons_between,
    get_pending_boons_for,
    get_net_boon_position,
    check_harpy_permissions,
    update_ledger
)
from .models import Boon
from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY,
    GOLD, RESET, BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR,
    CIRCLE_FILLED, DIAMOND
)


class CmdBoon(Command):
    """
    View boons (favors and debts).

    Usage:
        +boon
        +boon <character>
        +boon/pending

    Displays your boons or boons with a specific character.

    Switches:
        /pending - View boons requiring your action

    Examples:
        +boon
        +boon Marcus
        +boon/pending
    """

    key = "+boon"
    aliases = ["boon", "boons"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        caller = self.caller

        if "pending" in self.switches:
            self._show_pending()
            return

        if self.args:
            self._show_with_character()
            return

        self._show_summary()

    def _show_summary(self):
        """Show boon summary."""
        caller = self.caller
        ledger = get_or_create_ledger(caller)

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {GOLD}{DIAMOND}{RESET} {PALE_IVORY}BOON LEDGER: {caller.key.upper()}{RESET}{' ' * (60 - len(caller.key))}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

        # Debts
        output.append(f"\n{PALE_IVORY}DEBTS (What You Owe):{RESET}")
        if ledger.total_debt_weight > 0:
            if ledger.life_owed > 0:
                output.append(f"  {BLOOD_RED}Life Boons:{RESET} {ledger.life_owed}")
            if ledger.blood_owed > 0:
                output.append(f"  {BLOOD_RED}Blood Boons:{RESET} {ledger.blood_owed}")
            if ledger.major_owed > 0:
                output.append(f"  {DARK_RED}Major Boons:{RESET} {ledger.major_owed}")
            if ledger.minor_owed > 0:
                output.append(f"  {GOLD}Minor Boons:{RESET} {ledger.minor_owed}")
            if ledger.trivial_owed > 0:
                output.append(f"  {SHADOW_GREY}Trivial Boons:{RESET} {ledger.trivial_owed}")
            output.append(f"  {PALE_IVORY}Total Weight:{RESET} {ledger.total_debt_weight}")
        else:
            output.append(f"  {SHADOW_GREY}None{RESET}")

        # Credits
        output.append(f"\n{PALE_IVORY}CREDITS (What Others Owe You):{RESET}")
        if ledger.total_credit_weight > 0:
            if ledger.life_held > 0:
                output.append(f"  {BLOOD_RED}Life Boons:{RESET} {ledger.life_held}")
            if ledger.blood_held > 0:
                output.append(f"  {BLOOD_RED}Blood Boons:{RESET} {ledger.blood_held}")
            if ledger.major_held > 0:
                output.append(f"  {DARK_RED}Major Boons:{RESET} {ledger.major_held}")
            if ledger.minor_held > 0:
                output.append(f"  {GOLD}Minor Boons:{RESET} {ledger.minor_held}")
            if ledger.trivial_held > 0:
                output.append(f"  {SHADOW_GREY}Trivial Boons:{RESET} {ledger.trivial_held}")
            output.append(f"  {PALE_IVORY}Total Weight:{RESET} {ledger.total_credit_weight}")
        else:
            output.append(f"  {SHADOW_GREY}None{RESET}")

        # Net position
        output.append(f"\n{PALE_IVORY}Net Position:{RESET}", end="")
        if ledger.net_weight > 0:
            output.append(f" {GOLD}+{ledger.net_weight}{RESET} (In credit)")
        elif ledger.net_weight < 0:
            output.append(f" {BLOOD_RED}{ledger.net_weight}{RESET} (In debt)")
        else:
            output.append(f" {SHADOW_GREY}Balanced{RESET}")

        output.append(f"\n{SHADOW_GREY}Use |w+boon <character>|x to see boons with specific individuals.{RESET}")

        caller.msg("\n".join(output))

    def _show_with_character(self):
        """Show boons with a specific character."""
        caller = self.caller

        target = caller.search(self.args.strip())
        if not target:
            return

        boons = get_boons_between(caller, target)
        net_position = get_net_boon_position(caller, target)

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {PALE_IVORY}BOONS WITH {target.key.upper()}{RESET}{' ' * (63 - len(target.key))}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

        # Net position
        if net_position['net'] > 0:
            output.append(f"\n{PALE_IVORY}Net Position:{RESET} {GOLD}{target.key} owes you {net_position['net']} weight in boons{RESET}")
        elif net_position['net'] < 0:
            output.append(f"\n{PALE_IVORY}Net Position:{RESET} {BLOOD_RED}You owe {target.key} {abs(net_position['net'])} weight in boons{RESET}")
        else:
            output.append(f"\n{PALE_IVORY}Net Position:{RESET} {SHADOW_GREY}Balanced{RESET}")

        if not boons:
            output.append(f"\n{SHADOW_GREY}No boons between you and {target.key}.{RESET}")
            caller.msg("\n".join(output))
            return

        # List boons
        output.append(f"\n{PALE_IVORY}Boon History:{RESET}")
        for boon in boons[:10]:  # Last 10 boons
            if boon.debtor == caller:
                direction = f"{BLOOD_RED}You owe {target.key}{RESET}"
            else:
                direction = f"{GOLD}{target.key} owes you{RESET}"

            status_color = GOLD if boon.status == 'accepted' else SHADOW_GREY
            output.append(f"\n#{boon.id} - {direction} - {PALE_IVORY}{boon.get_boon_type_display()}{RESET}")
            output.append(f"  Status: {status_color}{boon.status.title()}{RESET}")
            output.append(f"  {SHADOW_GREY}{boon.description[:60]}{'...' if len(boon.description) > 60 else ''}{RESET}")

        caller.msg("\n".join(output))

    def _show_pending(self):
        """Show boons pending action."""
        caller = self.caller
        pending = get_pending_boons_for(caller)

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {PALE_IVORY}PENDING BOONS{RESET}{' ' * 60}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

        has_pending = False

        # To accept
        if pending['to_accept'].exists():
            has_pending = True
            output.append(f"\n{GOLD}To Accept (offered to you):{RESET}")
            for boon in pending['to_accept']:
                output.append(f"  #{boon.id} - {boon.get_boon_type_display()} from {boon.creditor.key}")
                output.append(f"    {SHADOW_GREY}{boon.description[:60]}{RESET}")
                output.append(f"    {SHADOW_GREY}Use: +boonaccept {boon.id} or +boondecline {boon.id}{RESET}")

        # Called in on you
        if pending['called_in_on_you'].exists():
            has_pending = True
            output.append(f"\n{BLOOD_RED}Called In (you must fulfill):{RESET}")
            for boon in pending['called_in_on_you']:
                output.append(f"  #{boon.id} - {boon.get_boon_type_display()} to {boon.creditor.key}")
                output.append(f"    {SHADOW_GREY}Request: {boon.called_in_description[:55]}{RESET}")
                output.append(f"    {SHADOW_GREY}Use: +boonfulfill {boon.id} = <description>{RESET}")

        # Awaiting fulfillment
        if pending['awaiting_fulfillment'].exists():
            has_pending = True
            output.append(f"\n{PALE_IVORY}Awaiting Fulfillment (you called in):{RESET}")
            for boon in pending['awaiting_fulfillment']:
                output.append(f"  #{boon.id} - {boon.get_boon_type_display()} from {boon.debtor.key}")
                output.append(f"    {SHADOW_GREY}Request: {boon.called_in_description[:55]}{RESET}")

        if not has_pending:
            output.append(f"\n{SHADOW_GREY}No boons pending action.{RESET}")

        caller.msg("\n".join(output))


class CmdBoonGive(Command):
    """
    Offer a boon to someone.

    Usage:
        +boongive <character> <type> = <description>

    Types: trivial, minor, major, blood, life

    Creates a boon offer that the other character must accept.

    Examples:
        +boongive Marcus minor = Saved me from a hunter
        +boongive Elena major = She covered up my Masquerade breach
    """

    key = "+boongive"
    aliases = ["boongive"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        caller = self.caller

        if not self.args or not self.rhs:
            caller.msg("Usage: +boongive <character> <type> = <description>")
            caller.msg("Types: trivial, minor, major, blood, life")
            return

        # Parse target and type
        parts = self.lhs.strip().split()
        if len(parts) < 2:
            caller.msg("Usage: +boongive <character> <type> = <description>")
            return

        target_name = " ".join(parts[:-1])
        boon_type = parts[-1].lower()

        target = caller.search(target_name)
        if not target:
            return

        description = self.rhs.strip()

        # Offer boon
        success, boon, message = offer_boon(caller, target, boon_type, description)

        if success:
            caller.msg(f"|g{message}|n")
            caller.msg(f"Boon ID: #{boon.id}")

            # Notify target
            if target.sessions.all():
                target.msg(
                    f"\n{GOLD}[New Boon Offer]{RESET}\n"
                    f"{caller.key} has offered you a {PALE_IVORY}{boon.get_boon_type_display()}{RESET} boon.\n"
                    f"Reason: {description}\n\n"
                    f"Use |w+boonaccept {boon.id}|n to accept or |w+boondecline {boon.id}|n to decline."
                )
        else:
            caller.msg(f"|r{message}|n")


class CmdBoonAccept(Command):
    """
    Accept a boon offer.

    Usage:
        +boonaccept <boon #>

    Accepts a boon that has been offered to you, formalizing the debt.
    """

    key = "+boonaccept"
    aliases = ["boonaccept"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +boonaccept <boon #>")
            return

        try:
            boon_id = int(self.args.strip())
        except ValueError:
            caller.msg("|rBoon ID must be a number.|n")
            return

        success, message = accept_boon(boon_id, caller)

        if success:
            caller.msg(f"|g{message}|n")

            # Notify creditor
            try:
                boon = Boon.objects.get(id=boon_id)
                if boon.creditor.sessions.all():
                    boon.creditor.msg(
                        f"\n{GOLD}[Boon Accepted]{RESET}\n"
                        f"{caller.key} has accepted the {boon.get_boon_type_display()} boon you offered."
                    )
            except Boon.DoesNotExist:
                pass
        else:
            caller.msg(f"|r{message}|n")


class CmdBoonDecline(Command):
    """
    Decline a boon offer.

    Usage:
        +boondecline <boon #>
        +boondecline <boon #> = <reason>

    Declines a boon that has been offered to you.
    """

    key = "+boondecline"
    aliases = ["boondecline"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +boondecline <boon #> = <reason>")
            return

        try:
            boon_id = int(self.lhs.strip())
        except ValueError:
            caller.msg("|rBoon ID must be a number.|n")
            return

        reason = self.rhs.strip() if self.rhs else ""

        success, message = decline_boon(boon_id, reason, caller)

        if success:
            caller.msg(f"|g{message}|n")

            # Notify creditor
            try:
                boon = Boon.objects.get(id=boon_id)
                if boon.creditor.sessions.all():
                    boon.creditor.msg(
                        f"\n{GOLD}[Boon Declined]{RESET}\n"
                        f"{caller.key} has declined the {boon.get_boon_type_display()} boon you offered."
                        + (f"\nReason: {reason}" if reason else "")
                    )
            except Boon.DoesNotExist:
                pass
        else:
            caller.msg(f"|r{message}|n")


class CmdBoonCall(Command):
    """
    Call in a boon owed to you.

    Usage:
        +booncall <boon #> = <description>

    Calls in a boon that is owed to you, specifying what you need.
    """

    key = "+booncall"
    aliases = ["booncall"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        caller = self.caller

        if not self.args or not self.rhs:
            caller.msg("Usage: +booncall <boon #> = <description of what you need>")
            return

        try:
            boon_id = int(self.lhs.strip())
        except ValueError:
            caller.msg("|rBoon ID must be a number.|n")
            return

        description = self.rhs.strip()

        success, message = call_in_boon(boon_id, description, caller)

        if success:
            caller.msg(f"|g{message}|n")

            # Notify debtor
            try:
                boon = Boon.objects.get(id=boon_id)
                if boon.debtor.sessions.all():
                    boon.debtor.msg(
                        f"\n{BLOOD_RED}[Boon Called In]{RESET}\n"
                        f"{caller.key} has called in the {boon.get_boon_type_display()} boon you owe.\n"
                        f"Request: {description}\n\n"
                        f"Use |w+boonfulfill {boon_id} = <description>|n when fulfilled."
                    )
            except Boon.DoesNotExist:
                pass
        else:
            caller.msg(f"|r{message}|n")


class CmdBoonFulfill(Command):
    """
    Mark a boon as fulfilled.

    Usage:
        +boonfulfill <boon #> = <description of how you fulfilled it>

    Marks a boon as fulfilled after you've completed the requested favor.
    """

    key = "+boonfulfill"
    aliases = ["boonfulfill"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        caller = self.caller

        if not self.args or not self.rhs:
            caller.msg("Usage: +boonfulfill <boon #> = <description>")
            return

        try:
            boon_id = int(self.lhs.strip())
        except ValueError:
            caller.msg("|rBoon ID must be a number.|n")
            return

        description = self.rhs.strip()

        success, message = fulfill_boon(boon_id, description, caller)

        if success:
            caller.msg(f"|g{message}|n")

            # Notify other party
            try:
                boon = Boon.objects.get(id=boon_id)
                other_party = boon.creditor if boon.debtor == caller else boon.debtor
                if other_party.sessions.all():
                    other_party.msg(
                        f"\n{GOLD}[Boon Fulfilled]{RESET}\n"
                        f"The {boon.get_boon_type_display()} boon with {caller.key} has been marked as fulfilled.\n"
                        f"Description: {description}"
                    )
            except Boon.DoesNotExist:
                pass
        else:
            caller.msg(f"|r{message}|n")


class CmdBoonAdmin(default_cmds.MuxCommand):
    """
    Admin/Harpy commands for managing boons.

    Usage:
        +boonadmin/acknowledge <boon #>
        +boonadmin/cancel <boon #> = <reason>
        +boonadmin/list
        +boonadmin/refresh <character>

    Switches:
        /acknowledge - Officially acknowledge a boon (Harpy only)
        /cancel - Cancel a boon
        /list - List all public boons
        /refresh - Refresh a character's boon ledger

    Harpies can acknowledge boons to make them official in Kindred society.
    """

    key = "+boonadmin"
    aliases = ["boonadmin"]
    locks = "cmd:perm(Builder) or cmd:pperm(Harpy)"
    help_category = "Admin"

    def func(self):
        caller = self.caller

        if "acknowledge" in self.switches:
            self._acknowledge_boon()
        elif "cancel" in self.switches:
            self._cancel_boon()
        elif "list" in self.switches:
            self._list_boons()
        elif "refresh" in self.switches:
            self._refresh_ledger()
        else:
            caller.msg("Usage: +boonadmin/<switch>. See help for switches.")

    def _acknowledge_boon(self):
        """Acknowledge a boon (Harpy function)."""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +boonadmin/acknowledge <boon #>")
            return

        try:
            boon_id = int(self.args.strip())
        except ValueError:
            caller.msg("|rBoon ID must be a number.|n")
            return

        success, message = acknowledge_boon(boon_id, caller)

        if success:
            caller.msg(f"|g{message}|n")
        else:
            caller.msg(f"|r{message}|n")

    def _cancel_boon(self):
        """Cancel a boon."""
        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: +boonadmin/cancel <boon #> = <reason>")
            return

        try:
            boon_id = int(self.lhs.strip())
        except ValueError:
            caller.msg("|rBoon ID must be a number.|n")
            return

        reason = self.rhs.strip()

        success, message = cancel_boon(boon_id, reason)

        if success:
            caller.msg(f"|g{message}|n")
        else:
            caller.msg(f"|r{message}|n")

    def _list_boons(self):
        """List all public boons."""
        from .utils import get_all_public_boons

        caller = self.caller
        boons = get_all_public_boons()[:20]  # Last 20

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {PALE_IVORY}PUBLIC BOONS{RESET}{' ' * 61}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}\n")

        for boon in boons:
            output.append(f"#{boon.id} - {boon.debtor.key} → {boon.creditor.key} - {boon.get_boon_type_display()}")
            output.append(f"  Status: {boon.status.title()}")
            output.append(f"  {SHADOW_GREY}{boon.description[:60]}{RESET}")
            if boon.acknowledged_by_harpy:
                output.append(f"  {GOLD}✓ Acknowledged by {boon.harpy.key if boon.harpy else 'Harpy'}{RESET}")
            output.append("")

        caller.msg("\n".join(output))

    def _refresh_ledger(self):
        """Refresh a character's boon ledger."""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +boonadmin/refresh <character>")
            return

        target = caller.search(self.args.strip())
        if not target:
            return

        ledger = update_ledger(target)
        caller.msg(f"|gRefreshed boon ledger for {target.key}.|n")
        caller.msg(f"Debts: {ledger.total_debt_weight} | Credits: {ledger.total_credit_weight} | Net: {ledger.net_weight}")
