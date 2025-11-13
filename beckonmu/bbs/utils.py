"""
BBS utility functions for permissions and formatting.
"""

from evennia.utils.utils import crop
from .models import Board, Post


def get_board(caller, board_id, check_perm=True):
    """
    Get a board by name or ID.
    
    Args:
        caller: Character or Account object
        board_id: Board name (str) or ID (int)
        check_perm: If True, check read permissions
    
    Returns:
        Board object or None
    """
    try:
        # Try to get by name first, then by ID
        if isinstance(board_id, str):
            board = Board.objects.get(name__iexact=board_id)
        else:
            board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return None
    
    if not check_perm:
        return board
    
    # Check read permissions
    if board.read_perm:
        account = caller.account if hasattr(caller, 'account') else caller
        if not account.check_permstring(board.read_perm):
            return None
    
    # Check required flags
    required_flags = board.get_required_flags_list()
    if required_flags:
        # Get character flags
        character = caller if hasattr(caller, 'db') else None
        if character:
            char_flags = character.db.flags or {}
            # Check if character has all required flags
            for flag in required_flags:
                if not char_flags.get(flag):
                    return None
        else:
            # No character, can't check flags
            return None
    
    return board


def get_post(caller, board, post_id, check_perm=True):
    """
    Get a post by sequence number.
    
    Args:
        caller: Character or Account object
        board: Board object
        post_id: Post sequence number (int) or str that can be converted to int
        check_perm: If True, check read permissions
    
    Returns:
        Post object or None
    """
    try:
        post_num = int(post_id)
        post = Post.objects.get(board=board, sequence_number=post_num)
    except (ValueError, Post.DoesNotExist):
        return None
    
    if not check_perm:
        return post
    
    # Check read permissions
    perm_to_check = post.read_perm or board.read_perm
    if perm_to_check:
        account = caller.account if hasattr(caller, 'account') else caller
        if not account.check_permstring(perm_to_check):
            return None
    
    return post


def format_board_list(caller, boards):
    """
    Formats a list of Board objects into a table view with elegant styling.

    Args:
        caller: The calling character
        boards: List of Board objects

    Returns:
        Formatted string for display
    """
    if not boards:
        return "No boards available."

    # Build elegant table with colors and proper formatting
    table = "|c" + "=" * 78 + "|n\n"
    table += "|c{:<30} {:<15} {:<22} {:<13}|n\n".format(
        "  Board Name", "Group", "Last Post", "# of Messages"
    )
    table += "|c" + "=" * 78 + "|n\n"

    # Add each board with proper formatting
    for board in boards:
        # Count posts that the caller can read
        readable_posts = [p for p in board.posts.all()
                         if p.read_perm == 'all' or caller.check_permstring(p.read_perm)]
        post_count = len(readable_posts)

        # Get last post info
        last_post = board.posts.order_by('-created_at').first() if readable_posts else None
        if last_post:
            last_post_info = f"{last_post.author.username[:15]} - {last_post.created_at.strftime('%m/%d/%y')}"
        else:
            last_post_info = "No posts"

        # Determine group/category display
        group_display = "IC" if getattr(board, 'is_ic', True) else "OOC"

        table += "|w{:<30}|n {:<15} {:<22} {:<13}\n".format(
            f"  {board.name[:28]}",
            group_display,
            last_post_info[:22],
            str(post_count)
        )

    table += "|c" + "=" * 78 + "|n\n"
    return table


def format_board_view(caller, board):
    """
    Formats the list of posts for a given board.

    Args:
        caller: The calling character
        board: Board object

    Returns:
        Formatted string for display
    """
    # Get posts the caller can read
    readable_posts = []
    for post in board.posts.all():
        if post.read_perm == 'all' or caller.check_permstring(post.read_perm):
            readable_posts.append(post)

    if not readable_posts:
        return f"Board '{board.name}' has no posts or you don't have permission to read them."

    # Build header
    output = f"|wBoard: {board.name}|n\n"
    output += "|w{:<5} {:<30} {:<15} {:<10}|n\n".format("#", "Title", "Author", "Date")
    output += "-" * 60 + "\n"

    # Add each post
    for post in readable_posts:
        author_name = post.author.username if post.author else "Unknown"
        date_str = post.created_at.strftime("%m/%d/%y")

        output += "{:<5} {:<30} {:<15} {:<10}\n".format(
            post.sequence_number,
            post.title[:29],
            author_name[:14],
            date_str
        )

    return output


def format_post_read(post, viewer=None):
    """
    Formats a single post and its comments for reading.

    Args:
        post: Post object
        viewer: AccountDB object of the viewer (optional, for compatibility)

    Returns:
        Formatted string for display
    """
    author_name = post.author.username if post.author else "Unknown"
    date_str = post.created_at.strftime("%B %d, %Y at %I:%M %p")

    # Post header
    output = f"|wPost #{post.sequence_number}: {post.title}|n\n"
    output += f"|wBy: {author_name} on {date_str}|n\n"
    output += "-" * 60 + "\n"

    # Post body
    output += f"{post.body}\n"

    # Comments
    comments = post.comments.all()
    if comments:
        output += "\n|wComments:|n\n"
        output += "-" * 60 + "\n"

        for comment in comments:
            comment_author = comment.author.username if comment.author else "Unknown"
            comment_date = comment.created_at.strftime("%m/%d/%y %I:%M %p")

            output += f"|w{comment_author}|n ({comment_date}):\n"
            output += f"{comment.body}\n\n"

    return output
