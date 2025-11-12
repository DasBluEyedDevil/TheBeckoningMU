"""
Jobs utility functions for shared functionality across job commands.

Provides service layer functions to keep commands clean and focused.
"""

from .models import Job, Bucket
from evennia.accounts.models import AccountDB
from django.core.exceptions import ObjectDoesNotExist
from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY,
    BONE_WHITE, GOLD, SUCCESS, FAILURE, RESET,
    DBOX_H, DBOX_V, DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR,
    BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR
)


def get_job(caller, job_id, bucket=None):
    """
    Fetches a Job by sequence number with error handling.
    
    Args:
        caller: The calling character
        job_id: Job sequence number (string or int)
        bucket: Optional bucket to search within
    
    Returns:
        Job object or None, messaging the caller on failure.
    """
    try:
        if bucket:
            job = Job.objects.get(sequence_number=int(job_id), bucket=bucket)
        else:
            job = Job.objects.get(sequence_number=int(job_id))
        return job
    except (ValueError, Job.DoesNotExist):
        caller.msg(f"Job #{job_id} not found.")
        return None


def get_bucket(caller, bucket_name):
    """
    Fetches a Bucket by name with error handling.
    
    Args:
        caller: The calling character
        bucket_name: Bucket name string
    
    Returns:
        Bucket object or None, messaging the caller on failure.
    """
    try:
        bucket = Bucket.objects.get(name__iexact=bucket_name)
        return bucket
    except Bucket.DoesNotExist:
        caller.msg(f"Bucket '{bucket_name}' not found.")
        return None


def get_account(caller, account_name):
    """
    Fetches an AccountDB by username with error handling.
    
    Args:
        caller: The calling character
        account_name: Account username string
    
    Returns:
        AccountDB object or None, messaging the caller on failure.
    """
    try:
        account = AccountDB.objects.get(username__iexact=account_name)
        return account
    except AccountDB.DoesNotExist:
        caller.msg(f"Account '{account_name}' not found.")
        return None


def check_job_permission(caller, job):
    """
    Checks if a caller has permission to interact with a specific job.
    
    Args:
        caller: The calling character
        job: Job object
    
    Returns:
        Boolean - True if caller can interact with the job
    """
    # Admins can always interact
    if caller.check_permstring("Builder"):
        return True
    
    # Account created the job
    if caller.account == job.creator:
        return True
    
    # Account is assigned to the job
    if caller.account in job.players.all():
        return True
    
    return False


def format_job_view(job):
    """
    Returns a formatted string for detailed job view with colors and symbols.

    Args:
        job: Job object

    Returns:
        Formatted string for display
    """
    # Status colors and symbols
    if job.completed:
        status_color = SHADOW_GREY
        status_symbol = "✓"
    elif job.status == "OPEN":
        status_color = GOLD
        status_symbol = "⏳"
    elif job.status == "BLOCKED":
        status_color = FAILURE
        status_symbol = "⛔"
    else:
        status_color = "|b"
        status_symbol = "⚙"

    # Header with colored box
    output = []
    output.append(f"{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}")

    # Title line
    title_text = f"Job #{job.sequence_number}: {job.title}"
    padding = 76 - len(title_text)
    output.append(f"{DBOX_V} {GOLD}{title_text}{RESET}{' ' * padding}{DARK_RED}{DBOX_V}")

    output.append(f"{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}")
    output.append("")

    # Details section
    output.append(f"  {GOLD}Bucket:{RESET} {PALE_IVORY}{job.bucket.name}{RESET}")
    output.append(f"  {GOLD}Status:{RESET} {status_color}{status_symbol} {job.status}{RESET}")
    output.append(f"  {GOLD}Created by:{RESET} {PALE_IVORY}{job.creator.username}{RESET}")
    output.append(f"  {GOLD}Created:{RESET} {SHADOW_GREY}{job.created_at.strftime('%B %d, %Y at %I:%M %p')}{RESET}")

    # Assigned players
    players = job.players.all()
    if players:
        player_names = [p.username for p in players]
        output.append(f"  {GOLD}Assigned:{RESET} {PALE_IVORY}{', '.join(player_names)}{RESET}")
    else:
        output.append(f"  {GOLD}Assigned:{RESET} {SHADOW_GREY}None{RESET}")

    # Completion status
    if job.completed:
        output.append(f"  {GOLD}Completed:{RESET} {SUCCESS}✓ Yes{RESET}")
    else:
        output.append(f"  {GOLD}Completed:{RESET} {SHADOW_GREY}○ No{RESET}")

    # Description box
    output.append("")
    output.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}")
    output.append(f"{BOX_V} {BONE_WHITE}Description{RESET}{' ' * 66}{SHADOW_GREY}{BOX_V}")
    output.append(f"{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")
    output.append(f"{PALE_IVORY}{job.description}{RESET}")

    # Comments section
    comments = job.comments.all()
    if comments:
        output.append("")
        output.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}")
        output.append(f"{BOX_V} {BONE_WHITE}Comments{RESET}{' ' * 69}{SHADOW_GREY}{BOX_V}")
        output.append(f"{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")
        output.append("")

        for comment in comments:
            author_name = comment.author.username if comment.author else "System"
            date_str = comment.created_at.strftime("%m/%d/%y %I:%M %p")
            visibility = f"{GOLD}(Public){RESET}" if comment.public else f"{SHADOW_GREY}(Private){RESET}"

            output.append(f"  {GOLD}[{date_str}]{RESET} {PALE_IVORY}{author_name}{RESET} {visibility}:")
            output.append(f"    {SHADOW_GREY}{comment.content}{RESET}")
            output.append("")

    return "\n".join(output)


def format_job_list(jobs, title="Jobs"):
    """
    Returns a formatted string for a list of jobs with colors and symbols.

    Args:
        jobs: QuerySet or list of Job objects
        title: Title for the list

    Returns:
        Formatted string for display
    """
    # Colored header
    output = []
    output.append(f"{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}")
    output.append(f"{DBOX_V} {GOLD}{title}{RESET}{' ' * (76 - len(title))}{DARK_RED}{DBOX_V}")
    output.append(f"{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}")
    output.append("")

    if not jobs:
        # Handle specific messaging for different contexts
        if title == "All Open Jobs":
            output.append(f"{SHADOW_GREY}  There are no jobs.{RESET}")
        elif title == "My Jobs":
            output.append(f"{SHADOW_GREY}  You have no jobs submitted.{RESET}")
        else:
            output.append(f"{SHADOW_GREY}  No {title.lower()} found.{RESET}")
        return "\n".join(output)

    # Table header
    output.append(f"{BONE_WHITE}  {'ID':<5} {'Title':<25} {'Bucket':<15} {'Status':<12} {'Assigned':<15}{RESET}")
    output.append(f"{SHADOW_GREY}  {BOX_H * 76}{RESET}")

    # Jobs
    for job in jobs:
        # Get assigned players
        players = job.players.all()
        if players:
            assigned = players.first().username[:14]
            if len(players) > 1:
                assigned += " (+)"
        else:
            assigned = f"{SHADOW_GREY}None{RESET}"

        # Status formatting with colors and symbols
        if job.completed:
            status_display = f"{SHADOW_GREY}✓ CLOSED{RESET}"
        elif job.status == "OPEN":
            status_display = f"{GOLD}⏳ OPEN{RESET}"
        elif job.status == "BLOCKED":
            status_display = f"{FAILURE}⛔ BLOCKED{RESET}"
        else:
            status_display = f"{PALE_IVORY}⚙ {job.status}{RESET}"

        # Job row
        output.append(f"  {GOLD}{job.sequence_number:<5}{RESET} "
                     f"{PALE_IVORY}{job.title[:24]:<25}{RESET} "
                     f"{SHADOW_GREY}{job.bucket.name[:14]:<15}{RESET} "
                     f"{status_display:<22} "  # Extra padding for ANSI codes
                     f"{PALE_IVORY if isinstance(assigned, str) and 'None' not in assigned else ''}{assigned}{RESET}")

    return "\n".join(output)


def format_bucket_list(buckets):
    """
    Returns a formatted string for a list of buckets with colors.

    Args:
        buckets: QuerySet or list of Bucket objects

    Returns:
        Formatted string for display
    """
    # Colored header
    output = []
    output.append(f"{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}")
    output.append(f"{DBOX_V} {GOLD}Job Buckets{RESET}{' ' * 65}{DARK_RED}{DBOX_V}")
    output.append(f"{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}")
    output.append("")

    if not buckets:
        output.append(f"{SHADOW_GREY}  No buckets found.{RESET}")
        return "\n".join(output)

    # Table header
    output.append(f"{BONE_WHITE}  {'Name':<20} {'Jobs':<10} {'Description':<40}{RESET}")
    output.append(f"{SHADOW_GREY}  {BOX_H * 76}{RESET}")

    # Buckets
    for bucket in buckets:
        job_count = bucket.jobs.count()
        description = bucket.description[:39] if bucket.description else f"{SHADOW_GREY}No description{RESET}"

        output.append(f"  {PALE_IVORY}{bucket.name[:19]:<20}{RESET} "
                     f"{GOLD}{job_count:<10}{RESET} "
                     f"{SHADOW_GREY}{description if 'No description' not in description else description}{RESET}")

    return "\n".join(output)


def can_view_job(caller, job):
    """
    Checks if a caller can view a specific job.
    
    Args:
        caller: The calling character
        job: Job object
    
    Returns:
        Boolean - True if caller can view the job
    """
    # Anyone can view public jobs or jobs they're involved with
    return True  # For now, all jobs are viewable. Can be restricted later.


def can_modify_job(caller, job):
    """
    Checks if a caller can modify a specific job.
    
    Args:
        caller: The calling character
        job: Job object
    
    Returns:
        Boolean - True if caller can modify the job
    """
    # Only admins, job creator, or assigned players can modify
    return check_job_permission(caller, job)


def can_complete_job(caller, job):
    """
    Checks if a caller can complete a specific job.
    
    Args:
        caller: The calling character
        job: Job object
    
    Returns:
        Boolean - True if caller can complete the job
    """
    # Admins can always complete
    if caller.check_permstring("Builder"):
        return True
    
    # Assigned players can complete
    if caller.account in job.players.all():
        return True
    
    # Job creator can complete their own job
    if caller.account == job.creator:
        return True
    
    return False
