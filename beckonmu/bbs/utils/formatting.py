from evennia.utils import evtable
from evennia.utils.utils import crop


def format_board_list(caller, boards):
    """
    Format a list of boards as a pretty table.
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
