import json
import sqlite3
import time
import tornado.web
from components.user.base import BaseHandler
from database import DATABASE, get_user_role
from components.sendEmail import send_email
import bcrypt

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

class AddCourseRequestHandler(BaseHandler):
    """
    Handles the requests to add a course.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Returns all the requests to add a course.
        """
        username = self.get_current_user()
        role = get_user_role(username)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if role == 'admin':
                cursor.execute('''
                    SELECT id, title, description, owner, category FROM add_course_requests
                ''')
                requests = cursor.fetchall()
                requests = [{'id': r[0], 'title': r[1], 'description': r[2], 'owner': r[3], 'category': r[4]} for r in requests]
                self.write(json.dumps(requests))
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
        Approves or denies the request to add a course.
        """
        username = self.get_current_user()
        print(f'Request: {self.request.body}')
        request_id = self.get_argument("request_id")
        action = self.get_argument("action")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if get_user_role(username) == 'admin':
                cursor.execute('''
                    SELECT owner, title, description, category FROM add_course_requests WHERE id = ?
                ''', (request_id,))
                request = cursor.fetchone()
                if request:
                    if action == 'approve':
                        cursor.execute('''
                            INSERT INTO courses (owner, title, description, category) VALUES (?, ?, ?, ?)
                        ''', (request[0], request[1], request[2], request[3]))
                        cursor.execute('''
                            DELETE FROM add_course_requests WHERE id = ?
                        ''', (request_id,))
                        conn.commit()
                        self.write("Course added successfully.")
                    elif action == 'deny':
                        cursor.execute('''
                            DELETE FROM course_requests WHERE id = ?
                        ''', (request_id,))
                        conn.commit()
                        self.write("Course request denied.")
                    else:
                        self.set_status(400)
                        self.write("Bad request: Invalid action.")
                else:
                    self.set_status(404)
                    self.write("Course request not found.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to perform this action.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

class AddTeacherRequestHandler(BaseHandler):
    """
    Handles the requests to add a teacher.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Returns all the requests to add a teacher.
        """
        username = self.get_current_user()
        role = get_user_role(username)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if role == 'admin':
                cursor.execute('''
                    SELECT id, username, email FROM add_teacher_requests
                ''')
                requests = cursor.fetchall()
                requests = [{'id': r[0], 'username': r[1], 'email': r[2]} for r in requests]
                self.write(json.dumps(requests))
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
        Approves or denies the request to add a teacher.
        """
        username = self.get_current_user()
        request_id = self.get_argument("request_id")
        action = self.get_argument("action")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if get_user_role(username) == 'admin':
                cursor.execute('''
                    SELECT username, email, password_hash FROM add_teacher_requests WHERE id = ?
                ''', (request_id,))
                request = cursor.fetchone()
                if request:
                    if action == 'approve':
                        cursor.execute('''
                            INSERT INTO users (username, email, role, password_hash) VALUES (?, ?, ?, ?)
                        ''', (request[0], request[1], 'teacher', request[2]))
                        cursor.execute('''
                            DELETE FROM add_teacher_requests WHERE id = ?
                        ''', (request_id,))
                        conn.commit()
                        self.write("Teacher added successfully.")
                    elif action == 'deny':
                        cursor.execute('''
                            DELETE FROM add_teacher_requests WHERE id = ?
                        ''', (request_id,))
                        conn.commit()
                        self.write("Teacher request denied.")
                    else:
                        self.set_status(400)
                        self.write("Bad request: Invalid action.")
                else:
                    self.set_status(404)
                    self.write("Teacher request not found.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to perform this action.")

        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()