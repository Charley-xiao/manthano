import tornado.web
import sqlite3
from database import DATABASE, add_post

class PostHandler(tornado.web.RequestHandler):
    """
    Handler for creating and retrieving posts.

    Each post includes:
    - sender name
    - sender avatar
    - content
    - likes
    - date_submitted
    - tag
    - comments
    """

    # @tornado.web.authenticated
    def get(self):
        """Retrieve all posts along with their comments."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, course_id, title, sender_name, content, likes, tag, date_submitted FROM posts
            ''')
            posts = cursor.fetchall()

            post_list = []
            for post in posts:
                post_list.append({
                    'id': post[0],
                    'course_id': post[1],
                    'title': post[2],
                    'sender_name': post[3],
                    'content': post[4],
                    'likes': post[5],
                    'tag': post[6],
                    'date_submitted': post[7]
                })
            # for post in posts:
            #     post_id = post[0]
            #     # Fetch comments for the post
            #     cursor.execute('''
            #         SELECT commenter_name, comment_content FROM comments
            #         WHERE post_id = ?
            #     ''', (post_id,))
            #     comments = cursor.fetchall()

            #     post_list.append({
            #         'id': post_id,
            #         'sender_name': post[1],
            #         'content': post[2],
            #         'likes': post[3],
            #         'tag': post[4],
            #         'comments': [{'commenter_name': c[0], 'comment_content': c[1]} for c in comments]
            #     })

            self.write({'posts': post_list})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})
        finally:
            conn.close()

    # @tornado.web.authenticated
    def post(self):
        """Create a new post."""
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        sender_name = data.get('sender_name')  # Assuming the current user is the sender
        title = data.get('title')
        course_id = data.get('course_id')
        content = data.get('content')
        likes = 0
        tag = data.get('tag', '')

        if add_post(course_id, title, sender_name, content, likes, tag):
            self.set_status(201)
            self.write({'message': 'Post created successfully'})
        else:
            self.set_status(500)
            self.write({'error': 'Database error'})

class CommentHandler(tornado.web.RequestHandler):
    """
    Handler for adding comments to posts.
    """

    @tornado.web.authenticated
    def post(self, post_id):
        """Add a comment to a specific post."""
        data = tornado.escape.json_decode(self.request.body)
        commenter_name = self.get_current_user()  # Assuming the current user is the commenter
        comment_content = data.get('comment_content')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO comments (post_id, commenter_name, comment_content)
                VALUES (?, ?, ?, ?)
            ''', (post_id, commenter_name, comment_content))
            conn.commit()
            self.set_status(201)
            self.write({'message': 'Comment added successfully'})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})
        finally:
            conn.close()