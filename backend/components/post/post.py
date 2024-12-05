import tornado.web
import sqlite3
from database import DATABASE, add_post, get_post_comments, add_post_comment, get_post_by_tag

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

    CREATE TABLE IF NOT EXISTS post_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            floor INTEGER NOT NULL,
            commenter_name TEXT NOT NULL,
            comment_content TEXT NOT NULL,
            date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(commenter_name) REFERENCES users(username)
        )
    """

    def get(self, post_id):
        """Retrieve all comments for a specific post."""

        try:
            comments = get_post_comments(post_id)
            self.write({'comments': comments})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})

    # @tornado.web.authenticated
    def post(self, post_id):
        """Add a comment to a specific post."""

        data = tornado.escape.json_decode(self.request.body)
        floor = data.get('floor')
        commenter_name = data.get('commenter_name')
        comment_content = data.get('comment_content')
        if data.get('likes') is not None:
            likes = data.get('likes')
        else:
            likes = 0

        if add_post_comment(post_id, floor, commenter_name, comment_content, likes):
            self.set_status(201)
            self.write({'message': 'Comment added successfully'})
        else:
            self.set_status(500)
            self.write({'error': 'Database error'})

    def put(self, post_id):
        """Update a comment."""

        data = tornado.escape.json_decode(self.request.body)
        floor = data.get('floor')
        likes = data.get('likes')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE post_comments
                SET likes = ?
                WHERE post_id = ? AND floor = ?
            ''', (floor, likes, post_id, floor))
            conn.commit()
            self.write({'message': 'Comment updated successfully'})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})


class PostTagHandler(tornado.web.RequestHandler):
    """
    Handler for retrieving posts by tag.
    """

    def get(self, tag):
        """Retrieve all posts with a specific tag."""
        try:
            posts = get_post_by_tag(tag)
            print(posts)
            self.write({'posts': posts})
        except sqlite3.Error:
            self.set_status(500)
            self.write({'error': 'Database error'})