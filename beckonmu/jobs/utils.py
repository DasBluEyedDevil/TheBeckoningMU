"""
Jobs utility functions for shared functionality across job commands.

Provides service layer functions to keep commands clean and focused.
"""

from .models import Job, Bucket
from evennia.accounts.models import AccountDB
from django.core.exceptions import ObjectDoesNotExist


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
    Returns a formatted string for detailed job view.
    
    Args:
        job: Job object
    
    Returns:
        Formatted string for display
    """
    # Header
    status_color = "|g" if job.status == "OPEN" else "|r" if job.completed else "|y"
    output = f"|wJob #{job.sequence_number}: {job.title}|n\n"
    output += f"|wBucket:|n {job.bucket.name}\n"
    output += f"|wStatus:|n {status_color}{job.status}|n\n"
    output += f"|wCreated by:|n {job.creator.username}\n"
    output += f"|wCreated:|n {job.created_at.strftime('%B %d, %Y at %I:%M %p')}\n"
    
    # Assigned players
    players = job.players.all()
    if players:
        player_names = [p.username for p in players]
        output += f"|wAssigned to:|n {', '.join(player_names)}\n"
    else:
        output += f"|wAssigned to:|n None\n"
    
    # Completion status
    if job.completed:
        output += f"|wCompleted:|n Yes\n"
    else:
        output += f"|wCompleted:|n No\n"
    
    output += "\n|wDescription:|n\n"
    output += f"{job.description}\n"
    
    # Comments
    comments = job.comments.all()
    if comments:
        output += "\n|wComments:|n\n"
        output += "-" * 60 + "\n"
        
        for comment in comments:
            author_name = comment.author.username if comment.author else "System"
            date_str = comment.created_at.strftime("%m/%d/%y %I:%M %p")
            visibility = " (Public)" if comment.public else " (Private)"
            
            output += f"|w{author_name}|n{visibility} ({date_str}):\n"
            output += f"{comment.content}\n\n"
    
    return output


def format_job_list(jobs, title="Jobs"):
    """
    Returns a formatted string for a list of jobs.
    
    Args:
        jobs: QuerySet or list of Job objects
        title: Title for the list
    
    Returns:
        Formatted string for display
    """
    if not jobs:
        # Handle specific messaging for different contexts
        if title == "All Open Jobs":
            return "There are no jobs."
        elif title == "My Jobs":
            return "You have no jobs submitted."
        else:
            return f"No {title.lower()} found."
    
    # Header
    output = f"|w{title}:|n\n"
    output += "|w{:<5} {:<25} {:<15} {:<10} {:<15}|n\n".format(
        "ID", "Title", "Bucket", "Status", "Assigned"
    )
    output += "-" * 70 + "\n"
    
    # Jobs
    for job in jobs:
        # Get assigned players
        players = job.players.all()
        if players:
            assigned = players.first().username[:14]
            if len(players) > 1:
                assigned += " (+)"
        else:
            assigned = "None"
        
        # Status formatting
        status = job.status
        if job.completed:
            status = "CLOSED"
        
        output += "{:<5} {:<25} {:<15} {:<10} {:<15}\n".format(
            job.sequence_number,
            job.title[:24],
            job.bucket.name[:14],
            status[:9],
            assigned
        )
    
    return output


def format_bucket_list(buckets):
    """
    Returns a formatted string for a list of buckets.
    
    Args:
        buckets: QuerySet or list of Bucket objects
    
    Returns:
        Formatted string for display
    """
    if not buckets:
        return "No buckets found."
    
    # Header
    output = "|wJob Buckets:|n\n"
    output += "|w{:<20} {:<10} {:<40}|n\n".format("Name", "Jobs", "Description")
    output += "-" * 70 + "\n"
    
    # Buckets
    for bucket in buckets:
        job_count = bucket.jobs.count()
        description = bucket.description[:39] if bucket.description else "No description"
        
        output += "{:<20} {:<10} {:<40}\n".format(
            bucket.name[:19],
            job_count,
            description
        )
    
    return output


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
