"""
Status System Commands

Commands for viewing and managing Status in Kindred society.
"""

from evennia import Command, default_cmds
from .utils import (
    get_character_status,
    get_or_create_character_status,
    get_total_status,
    get_status_bonus,
    format_status_display,
    get_all_positions,
    get_position_holders,
    create_status_request,
    get_pending_status_requests,
    get_character_status_requests,
    assign_position,
    remove_position,
    set_earned_status,
    modify_earned_status
)
from .models import CamarillaPosition, StatusRequest
from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY,
    GOLD, RESET, BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR,
    CIRCLE_FILLED, CIRCLE_EMPTY
)


class CmdStatus(default_cmds.MuxCommand):
    """
    View Status in Kindred society.

    Usage:
        +status
        +status <character>
        +status/history

    Displays Status rating, position, sect affiliation, and reputation.

    Switches:
        /history - View your status history

    Examples:
        +status
        +status Marcus
        +status/history
    """

    key = "+status"
    aliases = ["status"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Execute status command."""
        caller = self.caller

        # View status history
        if "history" in self.switches:
            self._show_history()
            return

        # Determine target
        if self.args:
            target = caller.search(self.args.strip())
            if not target:
                return
        else:
            target = caller

        # Get status
        char_status = get_character_status(target)

        if not char_status:
            if target == caller:
                caller.msg("|yYou have no Status record. This will be created automatically when needed.|n")
            else:
                caller.msg(f"|y{target.key} has no Status record.|n")
            return

        # Display status
        self._display_status(target, char_status)

    def _display_status(self, character, char_status):
        """Display character status."""
        caller = self.caller

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {GOLD}♛{RESET} {PALE_IVORY}STATUS: {character.key.upper()}{RESET}{' ' * (65 - len(character.key))}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

        # Total Status
        total = char_status.total_status
        status_dots = f"{GOLD}{CIRCLE_FILLED * total}{SHADOW_GREY}{CIRCLE_EMPTY * (5 - total)}{RESET}"
        output.append(f"\n{PALE_IVORY}Total Status:{RESET} {status_dots} ({total}/5)")

        # Breakdown
        breakdown = []
        if char_status.earned_status > 0:
            breakdown.append(f"Earned: {char_status.earned_status}")
        if char_status.position_status > 0:
            breakdown.append(f"Position: {char_status.position_status}")
        if char_status.temporary_status != 0:
            breakdown.append(f"Temporary: {char_status.temporary_status:+d}")

        if breakdown:
            output.append(f"{SHADOW_GREY}  ({', '.join(breakdown)}){RESET}")

        # Position
        if char_status.position:
            output.append(f"\n{PALE_IVORY}Position:{RESET} {GOLD}{char_status.position.name}{RESET}")
            if char_status.position.title:
                output.append(f"{SHADOW_GREY}  \"{char_status.position.title}\"{RESET}")
            output.append(f"{SHADOW_GREY}  {char_status.position.description}{RESET}")

        # Sect
        output.append(f"\n{PALE_IVORY}Sect:{RESET} {char_status.sect}")

        # Mechanical Bonus
        bonus = char_status.get_status_bonus()
        if bonus > 0:
            output.append(f"\n{PALE_IVORY}Social Roll Bonus:{RESET} +{bonus} dice")

        # Reputation
        if char_status.reputation:
            output.append(f"\n{PALE_IVORY}Reputation:{RESET}")
            output.append(f"{SHADOW_GREY}{char_status.reputation}{RESET}")

        caller.msg("\n".join(output))

    def _show_history(self):
        """Show status history."""
        caller = self.caller
        char_status = get_character_status(caller)

        if not char_status or not char_status.status_history:
            caller.msg("|yYou have no status history.|n")
            return

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {PALE_IVORY}STATUS HISTORY{RESET}{' ' * 60}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}\n")

        for entry in reversed(char_status.status_history[-10:]):  # Last 10 entries
            date = entry.get('date', 'Unknown')[:10]  # Just the date part
            change = entry.get('change', 0)
            reason = entry.get('reason', 'No reason given')
            changed_by = entry.get('changed_by', 'Unknown')
            new_total = entry.get('new_total', 0)

            change_str = f"{GOLD}+{change}{RESET}" if change > 0 else f"{BLOOD_RED}{change}{RESET}" if change < 0 else f"{SHADOW_GREY}±0{RESET}"

            output.append(f"{SHADOW_GREY}{date}{RESET} - {change_str} → {new_total}")
            output.append(f"  {PALE_IVORY}{reason}{RESET}")
            output.append(f"  {SHADOW_GREY}(by {changed_by}){RESET}")
            output.append("")

        caller.msg("\n".join(output))


class CmdPositions(default_cmds.MuxCommand):
    """
    View Camarilla positions.

    Usage:
        +positions
        +positions <position name>

    Displays available positions, their Status grants, and current holders.

    Examples:
        +positions
        +positions Prince
        +positions Primogen
    """

    key = "+positions"
    aliases = ["positions"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Execute positions command."""
        caller = self.caller

        # View specific position
        if self.args:
            self._show_position_detail(self.args.strip())
            return

        # List all positions
        self._list_positions()

    def _list_positions(self):
        """List all positions."""
        caller = self.caller
        positions = get_all_positions()

        if not positions:
            caller.msg("|yNo positions are currently defined.|n")
            return

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {GOLD}♛{RESET} {PALE_IVORY}CAMARILLA POSITIONS{RESET}{' ' * 53}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}\n")

        for position in positions:
            holders = get_position_holders(position.name)
            holder_count = holders.count()

            status_dots = f"{GOLD}{CIRCLE_FILLED * position.status_granted}{RESET}"

            output.append(f"{PALE_IVORY}{position.name}{RESET} {status_dots}")
            output.append(f"  {SHADOW_GREY}{position.description}{RESET}")

            if holder_count > 0:
                holder_names = ", ".join([h.character.key for h in holders])
                output.append(f"  {GOLD}Holder(s):{RESET} {holder_names}")
            elif position.is_unique:
                output.append(f"  {SHADOW_GREY}(Vacant){RESET}")

            output.append("")

        output.append(f"{SHADOW_GREY}Use |w+positions <name>|x for details.{RESET}")

        caller.msg("\n".join(output))

    def _show_position_detail(self, position_name):
        """Show detail for a specific position."""
        caller = self.caller

        try:
            position = CamarillaPosition.objects.get(name__iexact=position_name, is_active=True)
        except CamarillaPosition.DoesNotExist:
            caller.msg(f"|rPosition '{position_name}' not found.|n")
            return

        holders = get_position_holders(position.name)

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {GOLD}♛{RESET} {PALE_IVORY}{position.name.upper()}{RESET}{' ' * (68 - len(position.name))}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}")

        # Status granted
        status_dots = f"{GOLD}{CIRCLE_FILLED * position.status_granted}{CIRCLE_EMPTY * (5 - position.status_granted)}{RESET}"
        output.append(f"\n{PALE_IVORY}Status Granted:{RESET} {status_dots} ({position.status_granted})")

        # Hierarchy
        output.append(f"{PALE_IVORY}Hierarchy Level:{RESET} {position.hierarchy_level}")

        # Requirements
        if position.requires_status > 0:
            output.append(f"{PALE_IVORY}Requires:{RESET} {position.requires_status}+ earned Status")

        if position.requires_clan:
            output.append(f"{PALE_IVORY}Requires Clan:{RESET} {position.requires_clan}")

        # Description
        output.append(f"\n{PALE_IVORY}Description:{RESET}")
        output.append(f"{SHADOW_GREY}{position.description}{RESET}")

        # Current holders
        if holders.count() > 0:
            output.append(f"\n{PALE_IVORY}Current Holder(s):{RESET}")
            for holder in holders:
                output.append(f"  {GOLD}●{RESET} {holder.character.key}")
        elif position.is_unique:
            output.append(f"\n{SHADOW_GREY}Position is currently vacant.{RESET}")

        caller.msg("\n".join(output))


class CmdStatusRequest(default_cmds.MuxCommand):
    """
    Request Status changes or position appointments.

    Usage:
        +statusreq
        +statusreq/status <+/-amount> = <reason>
        +statusreq/position <position name> = <reason>
        +statusreq/view
        +statusreq/cancel <#>

    Switches:
        /status  - Request earned Status change
        /position - Request position appointment
        /view - View your pending requests
        /cancel - Cancel a pending request

    Examples:
        +statusreq/status +1 = Resolved conflict with rival coterie peacefully
        +statusreq/position Primogen = Clan Ventrue has nominated me for Primogen Council
        +statusreq/view
        +statusreq/cancel 5
    """

    key = "+statusreq"
    aliases = ["statusreq", "statusrequest"]
    locks = "cmd:all()"
    help_category = "V5"

    def func(self):
        """Execute status request command."""
        caller = self.caller

        # View requests
        if "view" in self.switches or not self.switches:
            self._view_requests()
            return

        # Cancel request
        if "cancel" in self.switches:
            self._cancel_request()
            return

        # Request status change
        if "status" in self.switches:
            self._request_status_change()
            return

        # Request position
        if "position" in self.switches:
            self._request_position()
            return

        caller.msg("Usage: +statusreq/status or +statusreq/position")

    def _view_requests(self):
        """View character's status requests."""
        caller = self.caller
        requests = get_character_status_requests(caller)

        if not requests:
            caller.msg("|yYou have no status requests.|n")
            return

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {PALE_IVORY}YOUR STATUS REQUESTS{RESET}{' ' * 53}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}\n")

        for req in requests:
            status_color = GOLD if req.status == "pending" else SHADOW_GREY if req.status == "approved" else BLOOD_RED

            output.append(f"#{req.id} - {status_color}{req.status.upper()}{RESET} - {req.get_request_type_display()}")
            output.append(f"  {SHADOW_GREY}Submitted: {req.created_date.strftime('%Y-%m-%d')}{RESET}")
            output.append(f"  {PALE_IVORY}Reason: {req.reason[:60]}{'...' if len(req.reason) > 60 else ''}{RESET}")

            if req.status != "pending":
                output.append(f"  {SHADOW_GREY}Resolved: {req.resolution_reason}{RESET}")

            output.append("")

        caller.msg("\n".join(output))

    def _cancel_request(self):
        """Cancel a pending request."""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +statusreq/cancel <request #>")
            return

        try:
            req_id = int(self.args.strip())
            request = StatusRequest.objects.get(id=req_id, character=caller, status='pending')
            request.delete()
            caller.msg(f"|gRequest #{req_id} canceled.|n")
        except ValueError:
            caller.msg("|rRequest ID must be a number.|n")
        except StatusRequest.DoesNotExist:
            caller.msg("|rRequest not found or already resolved.|n")

    def _request_status_change(self):
        """Request status change."""
        caller = self.caller

        if not self.rhs:
            caller.msg("Usage: +statusreq/status <+/-amount> = <reason>")
            return

        try:
            change = int(self.lhs.strip())
            reason = self.rhs.strip()

            if not reason:
                caller.msg("|rYou must provide a reason for the status change.|n")
                return

            if abs(change) > 2:
                caller.msg("|rStatus changes are typically limited to ±2 at a time.|n")
                return

            # Create request
            request = create_status_request(
                caller,
                "earned_status",
                reason,
                requested_change=change
            )

            caller.msg(
                f"|gStatus change request submitted (#{request.id}).|n\n"
                f"Change: {change:+d}\n"
                f"Reason: {reason}\n\n"
                f"Staff will review your request."
            )

        except ValueError:
            caller.msg("|rInvalid amount. Use format: +statusreq/status +1 = reason|n")

    def _request_position(self):
        """Request position appointment."""
        caller = self.caller

        if not self.rhs:
            caller.msg("Usage: +statusreq/position <position name> = <reason>")
            return

        position_name = self.lhs.strip()
        reason = self.rhs.strip()

        if not reason:
            caller.msg("|rYou must provide IC justification for this appointment.|n")
            return

        # Check if position exists
        try:
            position = CamarillaPosition.objects.get(name__iexact=position_name, is_active=True)
        except CamarillaPosition.DoesNotExist:
            caller.msg(f"|rPosition '{position_name}' not found. Use |w+positions|r to see available positions.|n")
            return

        # Create request
        request = create_status_request(
            caller,
            "position",
            reason,
            requested_position=position
        )

        caller.msg(
            f"|gPosition appointment request submitted (#{request.id}).|n\n"
            f"Position: {position.name}\n"
            f"Reason: {reason}\n\n"
            f"Staff will review your request."
        )


class CmdStatusAdmin(default_cmds.MuxCommand):
    """
    Admin commands for managing Status.

    Usage:
        +statusadmin/pending
        +statusadmin/approve <request #> = <reason>
        +statusadmin/deny <request #> = <reason>
        +statusadmin/set <character> = <amount>
        +statusadmin/modify <character> = <+/-amount>
        +statusadmin/position <character> = <position name>
        +statusadmin/remove <character>

    Switches:
        /pending  - View all pending requests
        /approve  - Approve a status request
        /deny     - Deny a status request
        /set      - Set character's earned status directly
        /modify   - Modify character's earned status by amount
        /position - Assign position to character
        /remove   - Remove character's position

    Examples:
        +statusadmin/pending
        +statusadmin/approve 15 = Verified IC actions warrant this
        +statusadmin/deny 16 = Insufficient IC justification
        +statusadmin/set Marcus = 2
        +statusadmin/modify Marcus = +1
        +statusadmin/position Marcus = Primogen
        +statusadmin/remove Marcus
    """

    key = "+statusadmin"
    aliases = ["statusadmin"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        """Execute status admin command."""
        caller = self.caller

        if "pending" in self.switches:
            self._show_pending_requests()
        elif "approve" in self.switches:
            self._approve_request()
        elif "deny" in self.switches:
            self._deny_request()
        elif "set" in self.switches:
            self._set_status()
        elif "modify" in self.switches:
            self._modify_status()
        elif "position" in self.switches:
            self._assign_position()
        elif "remove" in self.switches:
            self._remove_position()
        else:
            caller.msg("Usage: +statusadmin/<switch>. See help for switches.")

    def _show_pending_requests(self):
        """Show pending status requests."""
        caller = self.caller
        requests = get_pending_status_requests()

        if not requests:
            caller.msg("|yNo pending status requests.|n")
            return

        output = []
        output.append(f"\n{DARK_RED}{BOX_TL}{BOX_H * 76}{BOX_TR}{RESET}")
        output.append(f"{BOX_V} {PALE_IVORY}PENDING STATUS REQUESTS{RESET}{' ' * 50}{BOX_V}")
        output.append(f"{DARK_RED}{BOX_BL}{BOX_H * 76}{BOX_BR}{RESET}\n")

        for req in requests:
            output.append(f"#{req.id} - {GOLD}{req.character.key}{RESET} - {req.get_request_type_display()}")
            output.append(f"  {SHADOW_GREY}Submitted: {req.created_date.strftime('%Y-%m-%d %H:%M')}{RESET}")
            output.append(f"  {PALE_IVORY}Reason: {req.reason}{RESET}")

            if req.request_type == "earned_status":
                output.append(f"  {GOLD}Requested Change: {req.requested_change:+d}{RESET}")
            elif req.request_type == "position":
                output.append(f"  {GOLD}Requested Position: {req.requested_position.name}{RESET}")

            if req.ooc_notes:
                output.append(f"  {SHADOW_GREY}OOC Notes: {req.ooc_notes}{RESET}")

            output.append("")

        output.append(f"{SHADOW_GREY}Use |w+statusadmin/approve <#>|x or |w+statusadmin/deny <#>|x{RESET}")

        caller.msg("\n".join(output))

    def _approve_request(self):
        """Approve a status request."""
        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: +statusadmin/approve <request #> = <reason>")
            return

        try:
            req_id = int(self.lhs.strip())
            reason = self.rhs.strip()

            request = StatusRequest.objects.get(id=req_id, status='pending')
            request.approve(caller, reason)

            caller.msg(f"|gRequest #{req_id} approved.|n")

            # Notify player
            if request.character.sessions.all():
                request.character.msg(
                    f"\n{GOLD}[Status Update]{RESET}\n"
                    f"Your status request (#{req_id}) has been |gAPPROVED|n.\n"
                    f"Reason: {reason}"
                )

        except ValueError:
            caller.msg("|rRequest ID must be a number.|n")
        except StatusRequest.DoesNotExist:
            caller.msg("|rRequest not found or already resolved.|n")

    def _deny_request(self):
        """Deny a status request."""
        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: +statusadmin/deny <request #> = <reason>")
            return

        try:
            req_id = int(self.lhs.strip())
            reason = self.rhs.strip()

            request = StatusRequest.objects.get(id=req_id, status='pending')
            request.deny(caller, reason)

            caller.msg(f"|rRequest #{req_id} denied.|n")

            # Notify player
            if request.character.sessions.all():
                request.character.msg(
                    f"\n{GOLD}[Status Update]{RESET}\n"
                    f"Your status request (#{req_id}) has been |rDENIED|n.\n"
                    f"Reason: {reason}"
                )

        except ValueError:
            caller.msg("|rRequest ID must be a number.|n")
        except StatusRequest.DoesNotExist:
            caller.msg("|rRequest not found or already resolved.|n")

    def _set_status(self):
        """Set character's earned status."""
        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: +statusadmin/set <character> = <amount>")
            return

        target = caller.search(self.lhs.strip())
        if not target:
            return

        try:
            amount = int(self.rhs.strip())
            set_earned_status(target, amount, "Set by admin", caller)
            caller.msg(f"|g{target.key}'s earned status set to {amount}.|n")

            if target.sessions.all():
                target.msg(f"|yYour earned Status has been set to {amount} by staff.|n")

        except ValueError:
            caller.msg("|rAmount must be a number (0-5).|n")

    def _modify_status(self):
        """Modify character's earned status."""
        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: +statusadmin/modify <character> = <+/-amount>")
            return

        target = caller.search(self.lhs.strip())
        if not target:
            return

        try:
            change = int(self.rhs.strip())
            modify_earned_status(target, change, "Modified by admin", caller)

            caller.msg(f"|g{target.key}'s earned status modified by {change:+d}.|n")

            if target.sessions.all():
                target.msg(f"|yYour earned Status has been modified by {change:+d} by staff.|n")

        except ValueError:
            caller.msg("|rAmount must be a number.|n")

    def _assign_position(self):
        """Assign position to character."""
        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: +statusadmin/position <character> = <position name>")
            return

        target = caller.search(self.lhs.strip())
        if not target:
            return

        position_name = self.rhs.strip()
        success, message = assign_position(target, position_name, caller)

        if success:
            caller.msg(f"|g{message}|n")
            if target.sessions.all():
                target.msg(f"|yYou have been appointed as {position_name} by staff!|n")
        else:
            caller.msg(f"|r{message}|n")

    def _remove_position(self):
        """Remove character's position."""
        caller = self.caller

        if not self.args:
            caller.msg("Usage: +statusadmin/remove <character>")
            return

        target = caller.search(self.args.strip())
        if not target:
            return

        success, message = remove_position(target, caller)

        if success:
            caller.msg(f"|g{message}|n")
            if target.sessions.all():
                target.msg(f"|yYou have been removed from your position by staff.|n")
        else:
            caller.msg(f"|r{message}|n")
