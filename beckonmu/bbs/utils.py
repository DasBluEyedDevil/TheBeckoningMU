"""
BBS utility functions for permissions and formatting.
"""

from evennia.utils import evtable, ansi
from evennia.utils.utils import crop
from .models import Board, Post
from world.ansi_theme import (
    BLOOD_RED, DARK_RED, PALE_IVORY, SHADOW_GREY,
    BONE_WHITE, MIDNIGHT_BLUE, GOLD, RESET,
    DBOX_H, DBOX_V, DBOX_TL, DBOX_TR, DBOX_BL, DBOX_BR,
    BOX_H, BOX_V, BOX_TL, BOX_TR, BOX_BL, BOX_BR,
    FLEUR_DE_LIS, CIRCLE_FILLED
)


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
    Format a list of boards as a pretty table with colors and symbols.

    Args:
        caller: Character or Account object
        boards: QuerySet or list of Board objects

    Returns:
        str: Formatted table
    """
    # Filter boards by required flags
    filtered_boards = []
    character = caller if hasattr(caller, 'db') else None
    char_flags = character.db.flags if character else {}

    for board in boards:
        required_flags = board.get_required_flags_list()
        if required_flags:
            # Check if character has all required flags
            if not character:
                continue
            if not all(char_flags.get(flag) for flag in required_flags):
                continue

        # Check read permissions
        if board.read_perm:
            account = caller.account if hasattr(caller, 'account') else caller
            if not account.check_permstring(board.read_perm):
                continue

        filtered_boards.append(board)

    # Colored header
    output = []
    output.append(f"{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}")
    output.append(f"{DBOX_V} {GOLD}Bulletin Boards{RESET}{' ' * 62}{DARK_RED}{DBOX_V}")
    output.append(f"{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}")
    output.append("")

    if not filtered_boards:
        output.append(f"{SHADOW_GREY}  No boards available.{RESET}")
        return "\n".join(output)

    # Table header
    output.append(f"{BONE_WHITE}  {'Board':<20} {'Description':<40} {'Posts':<10}{RESET}")
    output.append(f"{SHADOW_GREY}  {BOX_H * 76}{RESET}")

    for board in filtered_boards:
        post_count = board.posts.count()
        description = crop(board.description, width=39)

        # Determine board symbol based on category or permissions
        if board.read_perm and "Admin" in board.read_perm:
            symbol = f"{FLEUR_DE_LIS}"  # Staff/admin boards
        elif hasattr(board, 'category') and board.category == 'ic':
            symbol = f"{CIRCLE_FILLED}"  # IC boards
        else:
            symbol = "○"  # OOC/general boards

        # Color board name based on activity
        name_color = MIDNIGHT_BLUE

        output.append(f"  {symbol} {name_color}{board.name:<18}{RESET} "
                     f"{PALE_IVORY}{description:<40}{RESET} "
                     f"{GOLD}{post_count:<10}{RESET}")

    return "\n".join(output)


def format_board_view(caller, board):
    """
    Format a board view showing all posts with colors and structure.

    Args:
        caller: Character or Account object
        board: Board object

    Returns:
        str: Formatted board view
    """
    # Get all posts (we'll filter by permissions if needed)
    posts = board.posts.all()

    # Colored header
    output = []
    output.append(f"{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}")

    # Board name line
    board_line = f"Board: {board.name}"
    padding = 76 - len(board_line)
    output.append(f"{DBOX_V} {GOLD}{board_line}{RESET}{' ' * padding}{DARK_RED}{DBOX_V}")

    output.append(f"{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}")
    output.append(f"  {SHADOW_GREY}{board.description}{RESET}")
    output.append("")

    if not posts:
        output.append(f"{SHADOW_GREY}  No posts yet.{RESET}")
        return "\n".join(output)

    # Table header
    output.append(f"{BONE_WHITE}  {'#':<5} {'Author':<20} {'Title':<35} {'Date':<10}{RESET}")
    output.append(f"{SHADOW_GREY}  {BOX_H * 76}{RESET}")

    account = caller.account if hasattr(caller, 'account') else caller

    for post in posts:
        # Check read permissions
        perm_to_check = post.read_perm or board.read_perm
        if perm_to_check and not account.check_permstring(perm_to_check):
            continue

        author_name = post.get_author_name(viewer=account)
        # Color anonymous posts differently
        if "Anonymous" in author_name:
            author_color = SHADOW_GREY
        else:
            author_color = PALE_IVORY

        title = crop(post.title, width=34)
        date_str = post.created_at.strftime("%m/%d/%y")

        output.append(f"  {GOLD}{post.sequence_number:<5}{RESET} "
                     f"{author_color}{author_name:<20}{RESET} "
                     f"{PALE_IVORY}{title:<35}{RESET} "
                     f"{SHADOW_GREY}{date_str:<10}{RESET}")

    return "\n".join(output)


def format_post_read(post, viewer=None):
    """
    Format a full post with comments using colors and structure.

    Args:
        post: Post object
        viewer: AccountDB object of the viewer (optional)

    Returns:
        str: Formatted post
    """
    author_name = post.get_author_name(viewer=viewer)
    date_str = post.created_at.strftime("%Y-%m-%d %H:%M:%S")

    # Colored header
    output = []
    output.append(f"{DARK_RED}{DBOX_TL}{DBOX_H * 78}{DBOX_TR}")

    # Title line
    title_text = f"Post #{post.sequence_number}: {post.title}"
    padding = 76 - len(title_text)
    output.append(f"{DBOX_V} {GOLD}{title_text}{RESET}{' ' * padding}{DARK_RED}{DBOX_V}")

    output.append(f"{DBOX_BL}{DBOX_H * 78}{DBOX_BR}{RESET}")
    output.append("")

    # Metadata
    output.append(f"  {GOLD}Board:{RESET} {MIDNIGHT_BLUE}{post.board.name}{RESET}")
    output.append(f"  {GOLD}Author:{RESET} {PALE_IVORY}{author_name}{RESET}")
    output.append(f"  {GOLD}Date:{RESET} {SHADOW_GREY}{date_str}{RESET}")

    # Content box
    output.append("")
    output.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}")
    output.append(f"{BOX_V} {BONE_WHITE}Message{RESET}{' ' * 70}{SHADOW_GREY}{BOX_V}")
    output.append(f"{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")
    output.append(f"{PALE_IVORY}{post.body}{RESET}")

    # Comments section
    comments = post.comments.all()
    if comments:
        output.append("")
        output.append(f"{SHADOW_GREY}{BOX_TL}{BOX_H * 78}{BOX_TR}")
        output.append(f"{BOX_V} {BONE_WHITE}Comments ({len(comments)}){RESET}{' ' * (70 - len(str(len(comments))) - 11)}{SHADOW_GREY}{BOX_V}")
        output.append(f"{BOX_BL}{BOX_H * 78}{BOX_BR}{RESET}")
        output.append("")

        for i, comment in enumerate(comments, 1):
            comment_date = comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
            output.append(f"  {GOLD}[{i}] {PALE_IVORY}{comment.author.username}{RESET} - {SHADOW_GREY}{comment_date}{RESET}")
            output.append(f"    {PALE_IVORY}{comment.body}{RESET}")
            output.append("")

    return "\n".join(output)
