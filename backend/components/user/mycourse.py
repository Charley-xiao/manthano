import json
import sqlite3
import time
import tornado.web
from components.user.base import BaseHandler
from database import DATABASE, get_user_role
from components.sendEmail import send_email

class MyCourseHandler(BaseHandler):
    """
    Handles the courses of students and teachers.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Returns all the courses of the user.
        """
        username = self.get_current_user()
        role = get_user_role(username)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if role == 'teacher':
                cursor.execute('''
                    SELECT id, title, description FROM courses WHERE owner = ?
                ''', (username,))
                courses = cursor.fetchall()
                courses = [{'id': c[0], 'title': c[1], 'description': c[2]} for c in courses]
                self.write(json.dumps(courses))
            elif role == 'student':
                cursor.execute('''
                    SELECT c.id, c.title, c.description FROM courses c
                    JOIN course_students cs ON c.id = cs.course_id
                    WHERE cs.student = ?
                ''', (username,))
                courses = cursor.fetchall()
                courses = [{'id': c[0], 'title': c[1], 'description': c[2]} for c in courses]
                self.write(json.dumps(courses))
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to access this page.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def post(self):
        """
        If the request is from the owner, adds the list of students to the course.
        If the request is from a student, sends a request to join the course to the teacher.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        students = self.get_argument("students")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            role = get_user_role(username)
            if role == 'teacher':
                cursor.execute('''
                    SELECT owner FROM courses WHERE id = ?
                ''', (course_id,))
                owner = cursor.fetchone()
                if owner and owner[0] == username:
                    for student in students:
                        cursor.execute('''
                            INSERT INTO course_students (course_id, student) VALUES (?, ?)
                        ''', (course_id, student))
                    conn.commit()
                    self.write("Students added to the course successfully.")
                else:
                    self.set_status(403)
                    self.write("Forbidden: You do not have permission to add students to this course.")
            elif role == 'student':
                cursor.execute('''
                    SELECT owner FROM courses WHERE id = ?
                ''', (course_id,))
                owner = cursor.fetchone()
                if owner:
                    cursor.execute('''
                        INSERT INTO join_course_requests (course_id, student) VALUES (?, ?)
                    ''', (course_id, username))
                    conn.commit()
                    send_email(owner[0],
                            'Course Join Request',
                            f'User {username} has requested to join the course with id {course_id}. Please approve or deny the request on the course page.')
                    cursor.execute('''
                        INSERT INTO messages (sender, receiver, subject, body, timestamp, priority, type) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (username, owner[0], 'Course Join Request', f'User {username} has requested to join the course with id {course_id}.', time.strftime('%Y-%m-%d %H:%M:%S'), 1, 'request'))
                    self.write("Request sent to the course teacher.")
                else:
                    self.set_status(404)
                    self.write("Course not found.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to perform this action.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        If the request is from the owner, deletes the list of students from the course.
        If the request is from a student, cancels the request to join the course.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        students = self.get_argument("students")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            role = get_user_role(username)
            if role == 'teacher':
                cursor.execute('''
                    SELECT owner FROM courses WHERE id = ?
                ''', (course_id,))
                owner = cursor.fetchone()
                if owner and owner[0] == username:
                    for student in students:
                        cursor.execute('''
                            DELETE FROM course_students WHERE course_id = ? AND student = ?
                        ''', (course_id, student))
                    conn.commit()
                    self.write("Students removed from the course successfully.")
                else:
                    self.set_status(403)
                    self.write("Forbidden: You do not have permission to remove students from this course.")
            elif role == 'student':
                cursor.execute('''
                    DELETE FROM join_course_requests WHERE course_id = ? AND student = ?
                ''', (course_id, username))
                conn.commit()
                self.write("Request cancelled successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to perform this action.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()