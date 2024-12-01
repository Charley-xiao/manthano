import json
import sqlite3
import time
import tornado.web
from components.user.base import BaseHandler
from database import DATABASE

class CourseNotifHandler(BaseHandler):
    """
    Handles the notifications of a course.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Sends a notification to the course.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        subject = self.get_argument("subject")
        body = self.get_argument("body")
        priority = self.get_argument("priority", 0)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses WHERE id = ?
            ''', (course_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    SELECT student FROM course_students WHERE course_id = ?
                ''', (course_id,))
                students = cursor.fetchall()
                for student in students:
                    cursor.execute('''
                        INSERT INTO messages (sender, receiver, subject, body, timestamp, read, type, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (username, student[0], subject, body, time.strftime('%Y-%m-%d %H:%M:%S'), 0, 'course', priority))
                conn.commit()
                self.write("Notification sent to the course successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to send notifications to this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


class CourseLikeHandler(BaseHandler):
    """
    Handles the likes of a course.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Likes a course.

        Note:
        - A user can only like a course if they are a student in the course.
        - If the user has already liked the course, the request will be interpreted as an unlike request.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT student FROM course_students WHERE course_id = ?
            ''', (course_id,))
            students = cursor.fetchall()
            if (username,) in students:
                cursor.execute('''
                    SELECT student FROM course_likes WHERE course_id = ? AND student = ?
                ''', (course_id, username))
                like = cursor.fetchone()
                if like:
                    cursor.execute('''
                        DELETE FROM course_likes WHERE course_id = ? AND student = ?
                    ''', (course_id, username))
                    conn.commit()
                    self.write("Course unliked successfully.")
                else:
                    cursor.execute('''
                        INSERT INTO course_likes (course_id, student) VALUES (?, ?)
                    ''', (course_id, username))
                    conn.commit()
                    self.write("Course liked successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to like this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


class CourseRecommendHandler(BaseHandler):
    """
    Handles the recommendations of a course.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Returns the recommended courses for the user.
        """
        username = self.get_current_user()
        recommended_courses = recommend_courses_with_content(username)
        self.write(json.dumps(recommended_courses))

class CourseCommentsHandler(BaseHandler):
    """
    Handles the in-course comments.

    Note: This is different from the evaluation comments.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Adds a comment to a course.

        Required arguments:
        - course_id: The id of the course.
        - comment: The comment text.
        """
        print(f'Request: {self.request.body}')
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        comment = self.get_argument("content")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO course_comments (course_id, student, comment) VALUES (?, ?, ?)
            ''', (course_id, username, comment))
            conn.commit()
            self.write("Comment added successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def get(self):
        """
        Gets the comments of a course.
        """
        course_id = self.get_argument("course_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT student, comment, date_submitted FROM course_comments WHERE course_id = ?
            ''', (course_id,))
            comments = cursor.fetchall()
            comments = [{'user': comment[0], 'content': comment[1], 'timestamp': comment[2]} for comment in comments]
            self.write(json.dumps(comments))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Deletes a comment from a course.

        Note:
        - Only the owner of the comment can delete it.

        Required arguments:
        - comment_id: The id of the comment.
        """
        username = self.get_current_user()
        comment_id = self.get_argument("comment_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT student FROM course_comments WHERE id = ?
            ''', (comment_id,))
            student = cursor.fetchone()
            if student and student[0] == username:
                cursor.execute('''
                    DELETE FROM course_comments WHERE id = ?
                ''', (comment_id,))
                conn.commit()
                self.write("Comment deleted successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to delete this comment.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

class CourseRatingHandler(BaseHandler):
    """
    Handles the rating.

    Note: This is the evaluation/rating.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Adds a rating to a course.

        Required arguments:
        - course_id: The id of the course.
        - sender_name
        - star
        - difficulty
        - workload
        - grading
        - gain
        - comment: The comment text.
        """
        print(f'Request: {self.request.body}')
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        star = self.get_argument("star")
        difficulty = self.get_argument("difficulty")
        workload = self.get_argument("workload")
        grading = self.get_argument("grading")
        gain = self.get_argument("gain")
        comment = self.get_argument("comment")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO rating (course_id, sender_name, star, difficulty, workload, grading, gain, comment, likes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)''',
                (course_id, username, star, difficulty, workload, grading, gain, comment))
            conn.commit()
            self.write("Comment added successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def get(self):
        """
        Gets the rating of a course.
        """
        course_id = self.get_argument("course_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT sender_name, star, difficulty, workload, grading, gain, comment, date_submitted FROM course_comments WHERE course_id = ?
            ''', (course_id,))
            rating = cursor.fetchall()
            rates = [{'sender_name': rate[0], 'star': rate[1], 'difficulty': rate[2], 'workload': rate[3], 'grading': rate[4], 'gain': rate[5],
                      'comment': rate[6], 'timestamp': rate[7]} for rate in rating]
            self.write(json.dumps(rates))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Deletes a feedback from the rating of a course.

        Note:
        - Only the owner of the feedback can delete it.

        Required arguments:
        - feedback_id: The id of the feedback.
        """
        username = self.get_current_user()
        feedback_id = self.get_argument("feedback_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT sender_name FROM rating WHERE id = ?
            ''', (feedback_id,))
            student = cursor.fetchone()
            if student and student[0] == username:
                cursor.execute('''
                    DELETE FROM rating WHERE id = ?
                ''', (feedback_id,))
                conn.commit()
                self.write("Feedback deleted successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to delete this feedback.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()