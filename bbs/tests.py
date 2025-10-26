"""
Comprehensive BBS (Bulletin Board System) tests.
"""

import threading
from unittest.mock import Mock, MagicMock, PropertyMock
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from evennia.accounts.models import AccountDB
from evennia.utils.test_resources import BaseEvenniaTest
from .models import Board, Post, Comment
from .utils import get_board, get_post, format_board_list, format_board_view, format_post_read
from .commands import CmdBBS, CmdBBSRead, CmdBBSPost, CmdBBSComment, CmdBBSDelete, CmdBBSAdmin


class BoardModelTests(TestCase):
    """Test Board model functionality."""
    
    def setUp(self):
        """Set up test boards."""
        self.board1 = Board.objects.create(
            name="General",
            description="General discussion board",
            read_perm="",
            write_perm="",
            required_flags=""
        )
        self.board2 = Board.objects.create(
            name="Admin",
            description="Admin-only board",
            read_perm="Admin",
            write_perm="Admin",
            required_flags="admin,staff"
        )
    
    def test_board_creation(self):
        """Test basic board creation."""
        self.assertEqual(self.board1.name, "General")
        self.assertEqual(self.board1.description, "General discussion board")
        self.assertFalse(self.board1.is_ic)
        self.assertFalse(self.board1.allow_anonymous)
    
    def test_get_required_flags_list_empty(self):
        """Test get_required_flags_list with no flags."""
        flags = self.board1.get_required_flags_list()
        self.assertEqual(flags, [])
    
    def test_get_required_flags_list_single(self):
        """Test get_required_flags_list with single flag."""
        board = Board.objects.create(
            name="Vampire",
            description="Vampire board",
            required_flags="vampire"
        )
        flags = board.get_required_flags_list()
        self.assertEqual(flags, ["vampire"])
    
    def test_get_required_flags_list_multiple(self):
        """Test get_required_flags_list with comma-separated flags."""
        flags = self.board2.get_required_flags_list()
        self.assertEqual(flags, ["admin", "staff"])
    
    def test_get_required_flags_list_whitespace(self):
        """Test get_required_flags_list handles whitespace."""
        board = Board.objects.create(
            name="Test",
            description="Test board",
            required_flags="  flag1 , flag2  ,  flag3  "
        )
        flags = board.get_required_flags_list()
        self.assertEqual(flags, ["flag1", "flag2", "flag3"])
    
    def test_board_str(self):
        """Test board string representation."""
        self.assertEqual(str(self.board1), "General")


class PostModelTests(TestCase):
    """Test Post model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test account using Evennia's AccountDB
        self.account1 = AccountDB.objects.create_user(
            username="TestUser1",
            email="test1@example.com",
            password="testpass123"
        )
        self.account2 = AccountDB.objects.create_user(
            username="TestUser2",
            email="test2@example.com",
            password="testpass123"
        )
        self.admin_account = AccountDB.objects.create_superuser(
            username="AdminUser",
            email="admin@example.com",
            password="adminpass123"
        )
        
        self.board = Board.objects.create(
            name="General",
            description="General discussion board"
        )
    
    def test_post_creation(self):
        """Test basic post creation."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Test Post",
            body="This is a test post."
        )
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.author, self.account1)
        self.assertEqual(post.board, self.board)
        self.assertFalse(post.is_anonymous)
    
    def test_sequence_number_auto_increment(self):
        """Test that sequence_number auto-increments per board."""
        post1 = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Post 1",
            body="First post"
        )
        post2 = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Post 2",
            body="Second post"
        )
        post3 = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Post 3",
            body="Third post"
        )
        
        self.assertEqual(post1.sequence_number, 1)
        self.assertEqual(post2.sequence_number, 2)
        self.assertEqual(post3.sequence_number, 3)
    
    def test_sequence_number_per_board(self):
        """Test that sequence_number is per-board."""
        board2 = Board.objects.create(
            name="Admin",
            description="Admin board"
        )
        
        post1_board1 = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Board1 Post1",
            body="First post on board 1"
        )
        post1_board2 = Post.objects.create(
            author=self.account1,
            board=board2,
            title="Board2 Post1",
            body="First post on board 2"
        )
        post2_board1 = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Board1 Post2",
            body="Second post on board 1"
        )
        
        self.assertEqual(post1_board1.sequence_number, 1)
        self.assertEqual(post1_board2.sequence_number, 1)
        self.assertEqual(post2_board1.sequence_number, 2)
    
    def test_get_author_name_normal(self):
        """Test get_author_name for normal (non-anonymous) post."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Normal Post",
            body="Not anonymous",
            is_anonymous=False
        )
        
        self.assertEqual(post.get_author_name(), "TestUser1")
        self.assertEqual(post.get_author_name(viewer=self.account2), "TestUser1")
    
    def test_get_author_name_anonymous_no_viewer(self):
        """Test get_author_name for anonymous post without viewer."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Anonymous Post",
            body="This is anonymous",
            is_anonymous=True
        )
        
        self.assertEqual(post.get_author_name(), "Anonymous")
    
    def test_get_author_name_anonymous_by_author(self):
        """Test get_author_name for anonymous post viewed by author."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Anonymous Post",
            body="This is anonymous",
            is_anonymous=True
        )
        
        self.assertEqual(
            post.get_author_name(viewer=self.account1),
            "TestUser1 (anonymous)"
        )
    
    def test_get_author_name_anonymous_by_admin(self):
        """Test get_author_name for anonymous post viewed by admin."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Anonymous Post",
            body="This is anonymous",
            is_anonymous=True
        )
        
        self.assertEqual(
            post.get_author_name(viewer=self.admin_account),
            "TestUser1 (anonymous)"
        )
    
    def test_get_author_name_anonymous_by_revealed(self):
        """Test get_author_name for anonymous post viewed by revealed_by user."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Anonymous Post",
            body="This is anonymous",
            is_anonymous=True
        )
        post.revealed_by.add(self.account2)
        
        self.assertEqual(
            post.get_author_name(viewer=self.account2),
            "TestUser1 (anonymous)"
        )
    
    def test_get_author_name_anonymous_by_other(self):
        """Test get_author_name for anonymous post viewed by other user."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Anonymous Post",
            body="This is anonymous",
            is_anonymous=True
        )
        
        self.assertEqual(post.get_author_name(viewer=self.account2), "Anonymous")
    
    def test_post_str(self):
        """Test post string representation."""
        post = Post.objects.create(
            author=self.account1,
            board=self.board,
            title="Test Post",
            body="Test body"
        )
        self.assertEqual(str(post), "General/1: Test Post")


class PostRaceConditionTests(TransactionTestCase):
    """Test Post race condition protection using TransactionTestCase."""
    
    def setUp(self):
        """Set up test data."""
        self.account = AccountDB.objects.create_user(
            username="TestUser",
            email="test@example.com",
            password="testpass123"
        )
        self.board = Board.objects.create(
            name="General",
            description="Test board"
        )
    
    def create_post(self, post_num):
        """Helper to create a post (for threading)."""
        Post.objects.create(
            author=self.account,
            board=self.board,
            title=f"Post {post_num}",
            body=f"Body {post_num}"
        )
    
    def test_concurrent_post_creation(self):
        """Test that concurrent posts get unique sequence numbers."""
        threads = []
        num_threads = 10
        
        # Create 10 posts concurrently
        for i in range(num_threads):
            thread = threading.Thread(target=self.create_post, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all posts were created with unique sequence numbers
        posts = Post.objects.filter(board=self.board).order_by('sequence_number')
        self.assertEqual(posts.count(), num_threads)
        
        # Check sequence numbers are 1-10 with no duplicates
        sequence_numbers = [post.sequence_number for post in posts]
        self.assertEqual(sequence_numbers, list(range(1, num_threads + 1)))


class CommentModelTests(TestCase):
    """Test Comment model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.account = AccountDB.objects.create_user(
            username="TestUser",
            email="test@example.com",
            password="testpass123"
        )
        self.board = Board.objects.create(
            name="General",
            description="Test board"
        )
        self.post = Post.objects.create(
            author=self.account,
            board=self.board,
            title="Test Post",
            body="Test body"
        )
    
    def test_comment_creation(self):
        """Test basic comment creation."""
        comment = Comment.objects.create(
            author=self.account,
            post=self.post,
            body="This is a comment."
        )
        
        self.assertEqual(comment.author, self.account)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.body, "This is a comment.")
    
    def test_comment_relationship(self):
        """Test comment-post relationship."""
        comment1 = Comment.objects.create(
            author=self.account,
            post=self.post,
            body="Comment 1"
        )
        comment2 = Comment.objects.create(
            author=self.account,
            post=self.post,
            body="Comment 2"
        )
        
        comments = self.post.comments.all()
        self.assertEqual(comments.count(), 2)
        self.assertIn(comment1, comments)
        self.assertIn(comment2, comments)
    
    def test_comment_str(self):
        """Test comment string representation."""
        comment = Comment.objects.create(
            author=self.account,
            post=self.post,
            body="Test comment"
        )
        self.assertEqual(str(comment), "Comment by TestUser on General/1: Test Post")


class UtilityFunctionTests(TestCase):
    """Test BBS utility functions."""
    
    def setUp(self):
        """Set up test data."""
        # Create accounts
        self.account1 = AccountDB.objects.create_user(
            username="TestUser",
            email="test@example.com",
            password="testpass123"
        )
        self.admin_account = AccountDB.objects.create_superuser(
            username="AdminUser",
            email="admin@example.com",
            password="adminpass123"
        )
        
        # Create boards
        self.public_board = Board.objects.create(
            name="General",
            description="Public board",
            read_perm="",
            write_perm=""
        )
        self.admin_board = Board.objects.create(
            name="Admin",
            description="Admin-only board",
            read_perm="Admin",
            write_perm="Admin"
        )
        self.flag_board = Board.objects.create(
            name="Vampire",
            description="Vampire-only board",
            required_flags="vampire"
        )
        
        # Create posts
        self.post1 = Post.objects.create(
            author=self.account1,
            board=self.public_board,
            title="Public Post",
            body="Public content"
        )
        self.admin_post = Post.objects.create(
            author=self.admin_account,
            board=self.admin_board,
            title="Admin Post",
            body="Admin content"
        )
    
    def _create_mock_caller(self, account, flags=None):
        """Create a mock caller (character) with account and flags."""
        caller = Mock()
        caller.account = account
        caller.db = Mock()
        caller.db.flags = flags or {}
        return caller
    
    def test_get_board_by_name(self):
        """Test get_board by name."""
        caller = self._create_mock_caller(self.account1)
        board = get_board(caller, "General")
        self.assertEqual(board, self.public_board)
    
    def test_get_board_by_name_case_insensitive(self):
        """Test get_board by name is case-insensitive."""
        caller = self._create_mock_caller(self.account1)
        board = get_board(caller, "GENERAL")
        self.assertEqual(board, self.public_board)
    
    def test_get_board_by_id(self):
        """Test get_board by ID."""
        caller = self._create_mock_caller(self.account1)
        board = get_board(caller, self.public_board.id)
        self.assertEqual(board, self.public_board)
    
    def test_get_board_not_found(self):
        """Test get_board returns None for non-existent board."""
        caller = self._create_mock_caller(self.account1)
        board = get_board(caller, "NonExistent")
        self.assertIsNone(board)
    
    def test_get_board_permission_check(self):
        """Test get_board filters by read permission."""
        caller = self._create_mock_caller(self.account1)
        
        # Regular user can't access admin board
        board = get_board(caller, "Admin")
        self.assertIsNone(board)
        
        # Admin can access admin board
        admin_caller = self._create_mock_caller(self.admin_account)
        board = get_board(admin_caller, "Admin")
        self.assertEqual(board, self.admin_board)
    
    def test_get_board_skip_permission_check(self):
        """Test get_board with check_perm=False."""
        caller = self._create_mock_caller(self.account1)
        
        # Regular user can access admin board if check_perm=False
        board = get_board(caller, "Admin", check_perm=False)
        self.assertEqual(board, self.admin_board)
    
    def test_get_board_flag_filtering(self):
        """Test get_board filters by required flags."""
        # User without vampire flag
        caller = self._create_mock_caller(self.account1, flags={})
        board = get_board(caller, "Vampire")
        self.assertIsNone(board)
        
        # User with vampire flag
        caller_with_flag = self._create_mock_caller(
            self.account1,
            flags={"vampire": True}
        )
        board = get_board(caller_with_flag, "Vampire")
        self.assertEqual(board, self.flag_board)
    
    def test_get_post_by_sequence_number(self):
        """Test get_post by sequence number."""
        caller = self._create_mock_caller(self.account1)
        post = get_post(caller, self.public_board, 1)
        self.assertEqual(post, self.post1)
    
    def test_get_post_by_string_number(self):
        """Test get_post accepts string number."""
        caller = self._create_mock_caller(self.account1)
        post = get_post(caller, self.public_board, "1")
        self.assertEqual(post, self.post1)
    
    def test_get_post_not_found(self):
        """Test get_post returns None for non-existent post."""
        caller = self._create_mock_caller(self.account1)
        post = get_post(caller, self.public_board, 999)
        self.assertIsNone(post)
    
    def test_get_post_invalid_number(self):
        """Test get_post returns None for invalid number."""
        caller = self._create_mock_caller(self.account1)
        post = get_post(caller, self.public_board, "invalid")
        self.assertIsNone(post)
    
    def test_get_post_permission_check(self):
        """Test get_post filters by permission."""
        caller = self._create_mock_caller(self.account1)
        
        # Regular user can't access admin post
        post = get_post(caller, self.admin_board, 1)
        self.assertIsNone(post)
        
        # Admin can access admin post
        admin_caller = self._create_mock_caller(self.admin_account)
        post = get_post(admin_caller, self.admin_board, 1)
        self.assertEqual(post, self.admin_post)
    
    def test_format_board_list_empty(self):
        """Test format_board_list with no boards."""
        caller = self._create_mock_caller(self.account1)
        output = format_board_list(caller, [])
        self.assertEqual(output, "No boards available.")
    
    def test_format_board_list_filtered(self):
        """Test format_board_list filters by permissions."""
        caller = self._create_mock_caller(self.account1)
        boards = Board.objects.all()
        output = format_board_list(caller, boards)
        
        # Should contain public boards but not admin board
        self.assertIn("General", output)
        self.assertNotIn("Admin", output)
    
    def test_format_board_view_empty(self):
        """Test format_board_view with no posts."""
        caller = self._create_mock_caller(self.account1)
        empty_board = Board.objects.create(
            name="Empty",
            description="Empty board"
        )
        output = format_board_view(caller, empty_board)
        
        self.assertIn("Empty", output)
        self.assertIn("No posts yet", output)
    
    def test_format_board_view_with_posts(self):
        """Test format_board_view with posts."""
        caller = self._create_mock_caller(self.account1)
        output = format_board_view(caller, self.public_board)
        
        self.assertIn("General", output)
        self.assertIn("Public Post", output)
        self.assertIn("TestUser", output)
    
    def test_format_post_read_without_comments(self):
        """Test format_post_read without comments."""
        output = format_post_read(self.post1, viewer=self.account1)
        
        self.assertIn("General", output)
        self.assertIn("Public Post", output)
        self.assertIn("Public content", output)
        self.assertIn("TestUser", output)
    
    def test_format_post_read_with_comments(self):
        """Test format_post_read with comments."""
        Comment.objects.create(
            author=self.account1,
            post=self.post1,
            body="First comment"
        )
        Comment.objects.create(
            author=self.admin_account,
            post=self.post1,
            body="Second comment"
        )
        
        output = format_post_read(self.post1, viewer=self.account1)
        
        self.assertIn("Comments:", output)
        self.assertIn("First comment", output)
        self.assertIn("Second comment", output)
        self.assertIn("AdminUser", output)


class CommandTestBase(BaseEvenniaTest):
    """Base class for command tests using Evennia test helpers."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create test boards
        self.public_board = Board.objects.create(
            name="General",
            description="Public board"
        )
        self.admin_board = Board.objects.create(
            name="Admin",
            description="Admin-only board",
            read_perm="Admin",
            write_perm="Admin"
        )
        
        # Create test posts
        self.post1 = Post.objects.create(
            author=self.account,
            board=self.public_board,
            title="Test Post",
            body="Test content"
        )


class CmdBBSTests(CommandTestBase):
    """Test CmdBBS command."""
    
    def test_list_boards(self):
        """Test +bbs lists available boards."""
        self.call(CmdBBS(), "", "General")
    
    def test_view_board(self):
        """Test +bbs <board> views board posts."""
        self.call(CmdBBS(), "General", "Test Post")
    
    def test_view_nonexistent_board(self):
        """Test +bbs with non-existent board."""
        self.call(CmdBBS(), "NonExistent", "not found")


class CmdBBSReadTests(CommandTestBase):
    """Test CmdBBSRead command."""
    
    def test_read_post(self):
        """Test +bbread reads a post."""
        self.call(CmdBBSRead(), "General/1", "Test content")
    
    def test_read_post_no_args(self):
        """Test +bbread with no arguments."""
        self.call(CmdBBSRead(), "", "Usage:")
    
    def test_read_post_invalid_format(self):
        """Test +bbread with invalid format."""
        self.call(CmdBBSRead(), "General", "Usage:")
    
    def test_read_nonexistent_post(self):
        """Test +bbread with non-existent post."""
        self.call(CmdBBSRead(), "General/999", "not found")


class CmdBBSPostTests(CommandTestBase):
    """Test CmdBBSPost command."""
    
    def test_create_post(self):
        """Test +bbpost creates a post."""
        self.call(
            CmdBBSPost(),
            "General=New Post/This is new content",
            "Posted to 'General'"
        )
        
        # Verify post was created
        post = Post.objects.get(board=self.public_board, sequence_number=2)
        self.assertEqual(post.title, "New Post")
        self.assertEqual(post.body, "This is new content")
    
    def test_create_post_no_args(self):
        """Test +bbpost with no arguments."""
        self.call(CmdBBSPost(), "", "Usage:")
    
    def test_create_post_invalid_format(self):
        """Test +bbpost with invalid format."""
        self.call(CmdBBSPost(), "General=NoSlash", "Usage:")
    
    def test_create_post_nonexistent_board(self):
        """Test +bbpost with non-existent board."""
        self.call(
            CmdBBSPost(),
            "NonExistent=Title/Body",
            "not found"
        )


class CmdBBSCommentTests(CommandTestBase):
    """Test CmdBBSComment command."""
    
    def test_add_comment(self):
        """Test +bbcomment adds a comment."""
        self.call(
            CmdBBSComment(),
            "General/1=Great post!",
            "Added comment"
        )
        
        # Verify comment was created
        comment = Comment.objects.get(post=self.post1)
        self.assertEqual(comment.body, "Great post!")
    
    def test_add_comment_no_args(self):
        """Test +bbcomment with no arguments."""
        self.call(CmdBBSComment(), "", "Usage:")
    
    def test_add_comment_invalid_format(self):
        """Test +bbcomment with invalid format."""
        self.call(CmdBBSComment(), "General", "Usage:")


class CmdBBSAdminTests(CommandTestBase):
    """Test CmdBBSAdmin command."""
    
    def test_create_board(self):
        """Test +bbadmin/create creates a board."""
        # Make character1 an admin
        self.char1.permissions.add("Admin")
        
        self.call(
            CmdBBSAdmin(),
            "/create NewBoard=A new board",
            "Created board 'NewBoard'"
        )
        
        # Verify board was created
        board = Board.objects.get(name="NewBoard")
        self.assertEqual(board.description, "A new board")
    
    def test_edit_board(self):
        """Test +bbadmin/edit edits a board."""
        # Make character1 an admin
        self.char1.permissions.add("Admin")
        
        self.call(
            CmdBBSAdmin(),
            "/edit General/description=Updated description",
            "Updated description"
        )
        
        # Verify board was updated
        self.public_board.refresh_from_db()
        self.assertEqual(self.public_board.description, "Updated description")
    
    def test_delete_board(self):
        """Test +bbadmin/delete deletes a board."""
        # Make character1 an admin
        self.char1.permissions.add("Admin")
        
        # Create a test board to delete
        test_board = Board.objects.create(
            name="ToDelete",
            description="Will be deleted"
        )
        
        self.call(
            CmdBBSAdmin(),
            "/delete ToDelete",
            "Deleted board 'ToDelete'"
        )
        
        # Verify board was deleted
        self.assertFalse(Board.objects.filter(name="ToDelete").exists())
