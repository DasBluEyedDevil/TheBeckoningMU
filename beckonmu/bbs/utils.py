"""
BBS utility functions for permissions and formatting.
"""

from evennia.utils import evtable
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
    if not boards:
        return "|wNo boards available.|n"

    table = evtable.EvTable(
        "|wBoard|n",
        "|wDescription|n",
        "|wPosts|n",
        border="header",
        width=78,
    )
    table.reformat_column(0, width=20)
    table.reformat_column(1, width=45)
    table.reformat_column(2, width=10, align="r")

    for board in boards:
        post_count = board.posts.count()
        description = crop(board.description, width=44)
        table.add_row(
            f"|C{board.name}|n",
            f"|w{description}|n",
            f"|y{post_count}|n",
        )

    return str(table)


def format_board_view(caller, board):
    """
    Format a board view showing all posts.

    Args:
        caller: Character or Account object
        board: Board object

    Returns:
        str: Formatted board view
    """
    posts = board.posts.all()
    if not posts:
        return f"|wBoard:|n {board.name}\n|wNo posts yet.|n"

    table = evtable.EvTable(
        "|w#|n",
        "|wAuthor|n",
        "|wTitle|n",
        "|wDate|n",
        border="header",
        width=78,
    )
    table.reformat_column(0, width=5, align="r")
    table.reformat_column(1, width=20)
    table.reformat_column(2, width=40)
    table.reformat_column(3, width=10, align="r")

    for post in posts:
        author_name = post.get_author_name(viewer=caller.account)
        title = crop(post.title, width=39)
        date_str = post.created_at.strftime("%m/%d/%y")
        table.add_row(
            f"|w{post.sequence_number}|n",
            f"|C{author_name}|n",
            f"|w{title}|n",
            f"|x{date_str}|n",
        )

    return f"|wBoard:|n {board.name}\n{table}"


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
    output.append(f"|wPost #{post.sequence_number}: {post.title}|n")
    output.append(f"|wBoard:|n {post.board.name}")
    output.append(f"|wAuthor:|n {author_name}")
    output.append(f"|wDate:|n {date_str}")
    output.append("-" * 78)
    output.append(post.body)
    output.append("-" * 78)

    comments = post.comments.all()
    if comments:
        output.append("|wComments:|n")
        for i, comment in enumerate(comments, 1):
            comment_date = comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
            output.append(
                f"|w[{i}] {comment.author.username}|n - |x{comment_date}|n"
            )
            output.append(f"  {comment.body}")

    return "\n".join(output)
