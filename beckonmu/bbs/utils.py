"""
BBS utility functions for permissions and formatting.
"""

from evennia.utils import evtable, ansi
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
    Format a list of boards as a pretty table.
    
    Args:
        caller: Character or Account object
        boards: QuerySet or list of Board objects
    
    Returns:
        str: Formatted table
    """
    # Filter boards using get_board() to ensure consistent permission checking
    filtered_boards = []
    
    for board in boards:
        # Use get_board() with the board's ID to perform permission checks
        # This ensures we use the same logic as other parts of the system
        if get_board(caller, board.id, check_perm=True):
            filtered_boards.append(board)
    
    
    if not filtered_boards:
        return "No boards available."
    
    # Create table
    table = evtable.EvTable(
        "|wBoard|n",
        "|wDescription|n",
        "|wPosts|n",
        border="cells",
        width=78
    )
    
    for board in filtered_boards:
        post_count = board.posts.count()
        description = crop(board.description, width=40)
        table.add_row(
            f"|c{board.name}|n",
            description,
            str(post_count)
        )
    
    return f"|wAvailable Bulletin Boards|n\n{table}"


def format_board_view(caller, board):
    """
    Format a board view showing all posts.
    
    Args:
        caller: Character or Account object
        board: Board object
    
    Returns:
        str: Formatted board view
    """
    # Get all posts (we'll filter by permissions if needed)
    posts = board.posts.all()
    
    if not posts:
        header = f"|w{'=' * 78}|n\n"
        header += f"|wBoard:|n |c{board.name}|n\n"
        header += f"|wDescription:|n {board.description}\n"
        header += f"|w{'=' * 78}|n\n"
        return header + "No posts yet."
    
    # Create table
    table = evtable.EvTable(
        "|w#|n",
        "|wAuthor|n",
        "|wTitle|n",
        "|wDate|n",
        border="cells",
        width=78
    )
    
    account = caller.account if hasattr(caller, 'account') else caller
    
    for post in posts:
        # Check read permissions
        perm_to_check = post.read_perm or board.read_perm
        if perm_to_check and not account.check_permstring(perm_to_check):
            continue
        
        author_name = post.get_author_name(viewer=account)
        title = crop(post.title, width=35)
        date_str = post.created_at.strftime("%m/%d/%y")
        
        table.add_row(
            str(post.sequence_number),
            author_name,
            title,
            date_str
        )
    
    header = f"|w{'=' * 78}|n\n"
    header += f"|wBoard:|n |c{board.name}|n\n"
    header += f"|wDescription:|n {board.description}\n"
    header += f"|w{'=' * 78}|n\n"
    
    return header + str(table)


def format_post_read(post, viewer=None):
    """
    Format a full post with comments.
    
    Args:
        post: Post object
        viewer: AccountDB object of the viewer (optional)
    
    Returns:
        str: Formatted post
    """
    author_name = post.get_author_name(viewer=viewer)
    date_str = post.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    output = []
    output.append(f"|w{'=' * 78}|n")
    output.append(f"|wBoard:|n |c{post.board.name}|n  |wPost:|n |y#{post.sequence_number}|n")
    output.append(f"|wTitle:|n {post.title}")
    output.append(f"|wAuthor:|n {author_name}  |wDate:|n {date_str}")
    output.append(f"|w{'-' * 78}|n")
    output.append(post.body)
    output.append(f"|w{'=' * 78}|n")
    
    # Add comments
    comments = post.comments.all()
    if comments:
        output.append(f"\n|wComments:|n")
        for i, comment in enumerate(comments, 1):
            comment_date = comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
            output.append(f"\n|w[{i}] {comment.author.username}|n - {comment_date}")
            output.append(f"{comment.body}")
    
    return "\n".join(output)
