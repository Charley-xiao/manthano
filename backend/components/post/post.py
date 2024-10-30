import tornado.web
import sqlite3
from database import DATABASE

class PostHandler(tornado.web.RequestHandler):
    """
    Handler for creating and retrieving posts.

    Each post includes:
    - sender name
    - sender avatar
    - content
    - likes
    - tags
    - comments
    """

    @tornado.web.authenticated
    def get(self):
        """Retrieve all posts along with their comments."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, sender_name, sender_avatar, content, likes, tags FROM posts
            ''')
            posts = cursor.fetchall()

            post_list = []
            for post in posts:
                post_id = post[0]
                # Fetch comments for the post
                cursor.execute('''
                    SELECT commenter_name, commenter_avatar, comment_content FROM comments
                    WHERE post_id = ?
                ''', (post_id,))
                comments = cursor.fetchall()

                post_list.append({
                    'id': post_id,
                    'sender_name': post[1],
                    'sender_avatar': post[2],
                    'content': post[3],
                    'likes': post[4],
                    'tags': post[5],
                    'comments': [{'commenter_name': c[0], 'commenter_avatar': c[1], 'comment_content': c[2]} for c in comments]
                })

            self.write({'posts': post_list})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})
        finally:
            conn.close()

    @tornado.web.authenticated
    def post(self):
        """Create a new post."""
        data = tornado.escape.json_decode(self.request.body)
        sender_name = self.get_current_user()  # Assuming the current user is the sender
        sender_avatar = data.get('sender_avatar')
        content = data.get('content')
        likes = 0
        tags = data.get('tags', '')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO posts (sender_name, sender_avatar, content, likes, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender_name, sender_avatar, content, likes, tags))
            conn.commit()
            self.set_status(201)
            self.write({'message': 'Post created successfully'})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})
        finally:
            conn.close()

class CommentHandler(tornado.web.RequestHandler):
    """
    Handler for adding comments to posts.
    """

    @tornado.web.authenticated
    def post(self, post_id):
        """Add a comment to a specific post."""
        data = tornado.escape.json_decode(self.request.body)
        commenter_name = self.get_current_user()  # Assuming the current user is the commenter
        commenter_avatar = data.get('commenter_avatar')
        comment_content = data.get('comment_content')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO comments (post_id, commenter_name, commenter_avatar, comment_content)
                VALUES (?, ?, ?, ?)
            ''', (post_id, commenter_name, commenter_avatar, comment_content))
            conn.commit()
            self.set_status(201)
            self.write({'message': 'Comment added successfully'})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})
        finally:
            conn.close()