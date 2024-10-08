"""
Basic Requirement (75%):
Support three permissions of system administrator, course teacher and student.
Course creation must be applied for by the course teacher and approved by the system administrator.
The course function needs to include the following specific contents:
The course contains different chapters, and the courseware function can be realized for different chapters. Chapters can be categorized: teaching, homework, and project
Teachers can add some students to the course.
It can be divided into open courses, non-open courses, and semi-open course (open part of the chapter).
Students can join open courses.
Teachers can send email notifications to students who join the course.
Students can give the lesson they have joined a like.

The functions of the chapter include the following specific contents:
Upload courseware module: Teachers can upload courseware for chapters, and the files support at least MD and PDF formats
Update the courseware module: Teachers can choose to keep the original courseware, and each version of the courseware is marked with a version number
Download courseware module: Teachers can set whether the current courseware is downloadable or not.
Video module: Course teachers can upload videos corresponding to chapters, and users can watch them online 
Comment module: A comment area is reserved for each courseware for user comments and teacher Q&A
Attachment module: Teachers can upload attachments corresponding to this chapter, such as data, code, etc. Downloadable for students.
Teaching evaluation function: Students can evaluate the course. Feedback scores and reviews.


Advanced Requirement (25%)
Popular courses and popular teachers list.
Add homework module and courseware viewing progress module.
Implement video anti-cheat function,
If you have to see it for a certain amount of time;
Only one video can be played at a time;
When the viewing time reaches a certain time, detect whether the user hangs up;
End-of-course requests cannot be invoked directly;
Single-user login only, etc.
Live broadcast room of the course.
Set specific indicators for teaching evaluation: such as the reasonableness of homework, the teacher's teaching ability, the difficulty of the test, etc.
Pretty UI.
"""

import sqlite3
import bcrypt
import os 
import re
import time 
from database import DATABASE, validate_user, add_user, get_user_role, get_users_by_role, User, add_teacher_request
from database import init_db
import argparse
import toml
import json
import hashlib
import uuid
# from recommender import recommend_courses_with_content
import warnings
from functools import wraps

def verified(cls):
    """Class decorator to mark a class as verified."""
    cls._is_verified = True
    original_methods = {name: method for name, method in cls.__dict__.items() if callable(method)}
    for name, method in original_methods.items():
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not getattr(self, '_is_verified', False):
                warnings.warn(f"Warning: {self.__class__.__name__} is not verified!")
            return method(self, *args, **kwargs)
        setattr(cls, name, wrapper)
    return cls

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=9265)
args = parser.parse_args()

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

with open('config.toml') as f:
    config = toml.load(f)

SECRET_KEY = config['secret']

def send_email(receiver, subject, body):
    sender = config['email']['sender']
    password = config['email']['password']
    host = config['email']['host']
    port = config['email']['port']

    message = MIMEMultipart('alternative')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(sender, password)
        print(f'Sending email to {receiver}...')
        server.sendmail(sender, receiver, message.as_string())

import tornado
import tornado.ioloop
import tornado.web

init_db()
active_sessions = {}

class BaseHandler(tornado.web.RequestHandler):
    def get_login_url(self) -> str:
        return "/login"
    
    def get_current_user(self):
        session_id = self.get_secure_cookie("session_id")
        username = self.get_secure_cookie("user")

        if not session_id or not username:
            return None

        if active_sessions.get(username.decode('utf-8')) == session_id.decode('utf-8'):
            return username.decode('utf-8')
        return None

    def get_user_role(self):
        username = self.get_current_user()
        if username:
            role = get_user_role(username)
            return role
        return None
    
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.set_header("Access-Control-Allow-Credentials", "true")


class MainHandler(BaseHandler):
    def get(self):
        """
        Returns username and role of the current user in JSON format.
        """
        username = self.get_current_user()
        role = get_user_role(username)
        self.write(json.dumps({"username": username, "role": role}))


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        role = self.get_user_role()
        if role == 'admin':
            self.write("Welcome, Admin! You have access to this page.")
        else:
            self.set_status(403)
            self.write("Forbidden: You do not have permission to access this page.")


class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html><body>'
                   '<form action="/login" method="post">'
                   'Username: <input type="text" name="username"><br>'
                   'Password: <input type="password" name="password"><br>'
                   '<input type="submit" value="Login">'
                   '</form></body></html>')

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        if validate_user(username, password):
            session_id = hashlib.sha256(uuid.uuid4().hex.encode('utf-8')).hexdigest()
            active_sessions[username] = session_id
            self.set_secure_cookie("user", username)
            self.set_secure_cookie("session_id", session_id)
            self.write(json.dumps({
                'success': True
            }))
        else:
            self.write(json.dumps({
                'success': False,
                'message': 'Incorrect password'
            }))


class RegisterHandler(BaseHandler):
    def get(self):
        self.write('<html><body>'
                   '<form action="/register" method="post">'
                   'Username: <input type="text" name="username"><br>'
                   'Password: <input type="password" name="password"><br>'
                   'Role: <select name="role">'
                   '<option value="student">Student</option>'
                     '<option value="teacher">Teacher</option>'
                        '<option value="admin">Admin</option>'
                     '</select><br>'
                     'Email: <input type="email" name="email"><br>'
                        '<input type="submit" value="Register">'
                        '</form></body></html>')

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        email = self.get_argument("email")
        role = self.get_argument("role", 'student')

        if role == 'admin':
            self.write("Registration failed. Admin registration is not allowed.")
        elif role == 'student':
            if add_user(username, password, email, role):
                self.write(f"User {username} registered successfully as {role}!")
            else:
                self.set_status(400)
                self.write("Registration failed. Possibly due to duplicate username/email or invalid email format.")
        elif role == 'teacher':
            if add_teacher_request(username, password, email):
                admins = get_users_by_role('admin')
                for admin in admins:
                    send_email(admin.email, 
                            'Course Teacher Registration Request', 
                            f'User {username} has requested to register as a course teacher. Please approve or deny the request on the admin panel.')
                self.write(f"Request sent to admin for approval.")
            else:
                self.set_status(400)
                self.write("Request failed. Possibly due to duplicate username/email or invalid email format.")


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")


class InboxHandler(BaseHandler):
    """
    Handles the inbox of students, teachers, and admins.
    """
    @tornado.web.authenticated
    def get(self):
        """
        With no parameters, returns all the messages of the inbox of the user. Sorted based on factors `priority` and `timestamp`.

        With the parameter `id`, returns the message with the given id.

        With the parameter `type`, returns all the messages of the inbox of the user with the given type.

        With the parameter `sender`, returns all the messages of the inbox of the user with the given sender.

        With the parameter `priority`, returns all the messages of the inbox of the user with the given priority.

        With the parameter `read`, returns all the messages of the inbox of the user with the given read status.

        With the parameter `limit`, returns the first `limit` messages of the inbox of the user.

        With the parameter `offset`, returns the messages of the inbox of the user starting from the `offset` index.
        """
        username = self.get_current_user()
        message_id = self.get_argument("id", None)
        message_type = self.get_argument("type", None)
        sender = self.get_argument("sender", None)
        priority = self.get_argument("priority", None)
        read = self.get_argument("read", None)
        limit = self.get_argument("limit", None)
        offset = self.get_argument("offset", None)

        try:
            limit = int(limit) if limit else None
            offset = int(offset) if offset else None
        except ValueError:
            self.set_status(400)
            self.write("Invalid limit or offset value.")
            return

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if message_id:
                cursor.execute('''
                    SELECT sender, receiver, subject, body, timestamp, read, type, priority 
                    FROM messages 
                    WHERE id = ? AND receiver = ?
                ''', (message_id, username))
                result = cursor.fetchone()
                if result:
                    self.write(json.dumps(result))
                else:
                    self.set_status(404)
                    self.write("Message not found.")
            else:
                query = '''
                    SELECT sender, receiver, subject, body, timestamp, read, type, priority 
                    FROM messages 
                    WHERE receiver = ?
                '''
                params = [username]

                if message_type:
                    query += ' AND type = ?'
                    params.append(message_type)
                if sender:
                    query += ' AND sender = ?'
                    params.append(sender)
                if priority:
                    try:
                        priority = int(priority)
                        query += ' AND priority = ?'
                        params.append(priority)
                    except ValueError:
                        self.set_status(400)
                        self.write("Invalid priority value.")
                        return
                if read:
                    try:
                        read = int(read)
                        query += ' AND read = ?'
                        params.append(read)
                    except ValueError:
                        self.set_status(400)
                        self.write("Invalid read value.")
                        return

                query += ' ORDER BY priority DESC, timestamp DESC'

                if limit:
                    query += ' LIMIT ?'
                    params.append(limit)
                if offset:
                    query += ' OFFSET ?'
                    params.append(offset)

                cursor.execute(query, params)
                result = cursor.fetchall()
                self.write(json.dumps(result))

        except sqlite3.Error as e:
            self.set_status(500)
            self.write(f"Database error: {str(e)}")
        finally:
            conn.close()

    @tornado.web.authenticated
    def post(self):
        """
        Sends a message to the user's inbox.

        Required arguments:
        - receiver: The username of the receiver.
        - subject: The subject of the message.
        - body: The body of the message.
        
        Optional arguments:
        - priority: The priority of the message. Default is 0.
        - type: The type of the message. Default is 'message'.

        Auto-generated arguments:
        - sender: The username of the sender.
        - timestamp: The current timestamp.
        - read: The read status of the message. Default is 0.
        """
        sender = self.get_current_user()
        receiver = self.get_argument("receiver")
        subject = self.get_argument("subject")
        body = self.get_argument("body")
        priority = self.get_argument("priority", 0)
        message_type = self.get_argument("type", 'message')
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO messages (sender, receiver, subject, body, timestamp, priority, type) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sender, receiver, subject, body, timestamp, priority, message_type))
            conn.commit()
            self.write("Message sent successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def put(self):
        """
        Updates the read status of a message in the user's inbox.
        """
        message_id = self.get_argument("id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE messages SET read = 1 WHERE id = ?
            ''', (message_id,))
            conn.commit()
            self.write("Message read status updated successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


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


class AddTeacherHandler(BaseHandler):
    """
    Handles the requests to add a teacher.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Returns all the requests to add a teacher.
        """
        username = self.get_current_user()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if get_user_role(username) == 'admin':
                cursor.execute('''
                    SELECT username, email FROM add_teacher_requests
                ''')
                requests = cursor.fetchall()
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
        Approves or denies a request to add a teacher.
        """
        username = self.get_current_user()
        teacher = self.get_argument("teacher")
        action = self.get_argument("action")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if get_user_role(username) == 'admin':
                if action == 'approve':
                    cursor.execute('''
                        SELECT username, password_hash, email FROM add_teacher_requests WHERE username = ?
                    ''', (teacher,))
                    request = cursor.fetchone()
                    if request:
                        cursor.execute('''
                            INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)
                        ''', (request[0], request[1], request[2], 'teacher'))
                        cursor.execute('''
                            DELETE FROM add_teacher_requests WHERE username = ?
                        ''', (teacher,))
                        conn.commit()
                        self.write("Request approved successfully.")
                    else:
                        self.set_status(404)
                        self.write("Request not found.")
                elif action == 'deny':
                    cursor.execute('''
                        DELETE FROM add_teacher_requests WHERE username = ?
                    ''', (teacher,))
                    conn.commit()
                    self.write("Request denied successfully.")
                else:
                    self.set_status(400)
                    self.write("Invalid action.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to perform this action.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


class AddCourseHandler(BaseHandler):
    """
    Handles the requests to add a course.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Returns all the requests to add a course.
        """
        username = self.get_current_user()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if get_user_role(username) == 'admin':
                cursor.execute('''
                    SELECT title, description, owner FROM add_course_requests
                ''')
                requests = cursor.fetchall()
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
        If the request is from the owner, submits a request to add a course.
        If the request is from an admin, approves or denies a request to add a course based on the title and owner.
        """
        username = self.get_current_user()
        title = self.get_argument("title")
        description = self.get_argument("description")
        owner = self.get_argument("owner")
        action = self.get_argument("action", None)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if action:
                if get_user_role(username) == 'admin':
                    if action == 'approve':
                        cursor.execute('''
                            INSERT INTO courses (title, description, owner) VALUES (?, ?, ?)
                        ''', (title, description, owner))
                        cursor.execute('''
                            DELETE FROM add_course_requests WHERE title = ? AND owner = ?
                        ''', (title, owner))
                        conn.commit()
                        self.write("Request approved successfully.")
                    elif action == 'deny':
                        cursor.execute('''
                            DELETE FROM add_course_requests WHERE title = ? AND owner = ?
                        ''', (title, owner))
                        conn.commit()
                        self.write("Request denied successfully.")
                    else:
                        self.set_status(400)
                        self.write("Invalid action.")
                else:
                    self.set_status(403)
                    self.write("Forbidden: You do not have permission to perform this action.")
            else:
                if get_user_role(username) == 'teacher':
                    cursor.execute('''
                        INSERT INTO add_course_requests (title, description, owner) VALUES (?, ?, ?)
                    ''', (title, description, username))
                    conn.commit()
                    self.write("Request sent successfully.")
                else:
                    self.set_status(403)
                    self.write("Forbidden: You do not have permission to add a course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


class DetailedCourseHandler(BaseHandler):
    """
    Handles the detailed information of a specific course, including:
    - id: The id of the course.
    - title: The title of the course.
    - description: The description of the course.
    - owner: The owner of the course.
    - type: The type of the course (open, ongoing, closed).
    - students: The list of students in the course, if the user is the owner or an admin.
    - chapters: The list of chapters in the course, with the following information:
        - id: The id of the chapter.
        - title: The title of the chapter.
        - content: The content of the chapter, typically a video link.
        - type: The type of the chapter (teaching, homework, project).
        - courseware: The courseware of the chapter, if the user is the owner or an admin.
        Note: 
        1. The courseware is a list of files uploaded by the teacher, typically for homework or project chapters.
        2. If the request is sent by a student, chapters that are not published by the teacher will not be shown.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Returns the detailed information of a specific course.
        """
        username = self.get_current_user()
        course_id = re.search(r'/(\d+)', self.request.path).group(1)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT title, description, owner, type FROM courses WHERE id = ?
            ''', (course_id,))
            course = cursor.fetchone()
            if course:
                cursor.execute('''
                    SELECT student FROM course_students WHERE course_id = ?
                ''', (course_id,))
                students = cursor.fetchall()
                course = list(course)
                course.append(students)

                cursor.execute('''
                    SELECT id, title, content, type, published FROM chapters WHERE course_id = ?
                ''', (course_id,))
                chapters = cursor.fetchall()
                if get_user_role(username) == 'student':
                    chapters = [chapter for chapter in chapters if chapter[4] == 1]

                for chapter in chapters:
                    cursor.execute('''
                        SELECT filename FROM courseware WHERE chapter_id = ?
                    ''', (chapter[0],))
                    courseware = cursor.fetchall()
                    chapter = list(chapter)
                    chapter.append(courseware)

                course.append(chapters)
                self.write(json.dumps(course))
            else:
                self.set_status(404)
                self.write("Course not found.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def post(self):
        """
        Adds a chapter to the course.
        """
        username = self.get_current_user()
        course_id = re.search(r'/(\d+)', self.request.path).group(1)
        title = self.get_argument("title")
        content = self.get_argument("content")
        chapter_type = self.get_argument("type")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses WHERE id = ?
            ''', (course_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)
                ''', (title, content, chapter_type, course_id))
                conn.commit()
                self.write("Chapter added successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to add chapters to this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Deletes a chapter from the course.
        """
        username = self.get_current_user()
        course_id = re.search(r'/(\d+)', self.request.path).group(1)
        chapter_id = self.get_argument("chapter_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses WHERE id = ?
            ''', (course_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    DELETE FROM chapters WHERE id = ?
                ''', (chapter_id,))
                conn.commit()
                self.write("Chapter deleted successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to delete chapters from this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def put(self):
        """
        Updates the published status of a chapter in the course.
        """
        username = self.get_current_user()
        course_id = re.search(r'/(\d+)', self.request.path).group(1)
        chapter_id = self.get_argument("chapter_id")
        published = self.get_argument("published")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses WHERE id = ?
            ''', (course_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    UPDATE chapters SET published = ? WHERE id = ?
                ''', (published, chapter_id))
                conn.commit()
                self.write("Chapter published status updated successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to update the published status of chapters in this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


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


class VideoAnticheatHandler(tornado.web.RequestHandler):
    """
    Handles video anti-cheat functionalities.
    """
    users_watch_time = {}

    @tornado.web.authenticated
    def post(self):
        username = self.get_current_user()
        data = tornado.escape.json_decode(self.request.body)
        watch_time = data.get('watch_time')

        if username in self.users_watch_time and self.users_watch_time[username]['active']:
            self.write({"violation": True})
            return

        self.users_watch_time[username] = {
            'watch_time': watch_time,
            'last_active': time.time(),
            'active': True
        }

        # Check if the user is "cheating" by being inactive or playing more than one video
        if watch_time >= 300:  # After 5 minutes of watching
            last_active = self.users_watch_time[username]['last_active']
            if time.time() - last_active > 60:  # Assume user inactive if no activity for 60 seconds
                self.write({"violation": True})
            else:
                self.write({"violation": False})
        else:
            self.write({"violation": False})

    @staticmethod
    def check_inactivity():
        """
        Periodic check for user inactivity. This can be run as a background task.
        """
        current_time = time.time()
        for user_id, data in VideoAnticheatHandler.users_watch_time.items():
            if data['active'] and current_time - data['last_active'] > 60:
                data['active'] = False


class CourseWareHandler(BaseHandler):
    """
    Handles the courseware of a chapter.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Uploads a courseware to the chapter.

        Supported file formats: PDF, MD, TXT, DOCX, PPTX, XLSX, JPG, PNG, MP4, MOV, AVI, MKV.

        Note:
        - The courseware will be stored in the 'files/courseware' directory.
        - The filename will be hashed and stored in the database.
        - Only the owner of the course can upload courseware.
        - The courseware is invisible to students by default.

        Required arguments:
        - chapter_id: The id of the chapter.
        - file: The file to upload.

        Returns:
        - The filename of the uploaded courseware.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        file = self.request.files['file'][0]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                filename = file['filename'] + time.strftime('%Y%m%d%H%M%S') # Add timestamp for versioning
                file_path = f'files/courseware/{filename}'
                with open(file_path, 'wb') as f:
                    f.write(file['body'])
                cursor.execute('''
                    INSERT INTO courseware (chapter_id, filename) VALUES (?, ?)
                ''', (chapter_id, filename))
                conn.commit()
                self.write(filename)
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to upload courseware to this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def get(self):
        """
        Returns the courseware of the chapter.

        Note:
        - If the request is sent by a student, courseware that is not published by the teacher will not be shown.

        Required arguments:
        - chapter_id: The id of the chapter.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    SELECT filename FROM courseware WHERE chapter_id = ?
                ''', (chapter_id,))
                courseware = cursor.fetchall()
                self.write(json.dumps(courseware))
            else:
                cursor.execute('''
                    SELECT published FROM chapters WHERE id = ?
                ''', (chapter_id,))
                published = cursor.fetchone()
                if published and published[0] == 1:
                    cursor.execute('''
                        SELECT filename, is_visible, is_downloadable FROM courseware WHERE chapter_id = ?
                    ''', (chapter_id,))
                    courseware = cursor.fetchall()
                    if get_user_role(username) == 'student':
                        courseware = [file for file in courseware if file[1] == 1]
                    self.write(json.dumps(courseware))
                else:
                    self.set_status(403)
                    self.write("Forbidden: You do not have permission to access the courseware of this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Deletes the courseware of the chapter.

        Note:
        - Only the owner of the course can delete courseware.

        Required arguments:
        - chapter_id: The id of the chapter.
        - filename: The filename of the courseware.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        filename = self.get_argument("filename")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    DELETE FROM courseware WHERE chapter_id = ? AND filename = ?
                ''', (chapter_id, filename))
                file_path = f'files/courseware/{filename}'
                if os.path.exists(file_path):
                    os.remove(file_path)
                conn.commit()
                self.write("Courseware deleted successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to delete courseware from this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def put(self):
        """
        Updates the visibility or downloadability of the courseware of the chapter.

        Note:
        - Only the owner of the course can update the visibility or downloadability of courseware.

        Required arguments:
        - chapter_id: The id of the chapter.
        - filename: The filename of the courseware.
        - is_visible: The visibility status of the courseware.
        - is_downloadable: The downloadability status of the courseware.

        Returns:
        - The updated visibility status of the courseware.
        - The updated downloadability status of the courseware.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        filename = self.get_argument("filename")
        is_visible = self.get_argument("is_visible")
        is_downloadable = self.get_argument("is_downloadable")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    UPDATE courseware SET is_visible = ?, is_downloadable = ? WHERE chapter_id = ? AND filename = ?
                ''', (is_visible, is_downloadable, chapter_id, filename))
                conn.commit()
                self.write({"is_visible": is_visible, "is_downloadable": is_downloadable})
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to update the visibility of courseware in this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


class CourseWareFileHandlerWithAuth(tornado.web.StaticFileHandler):
    """
    File handler with authentication for courseware.

    IMPORTANT: This is a security risk if not handled properly.

    1. If the user is the owner of the course or admin, they can access the courseware.
    2. If the user is a student, they can access the courseware only if it is visible.

    A typical path for courseware files is '/files/courseware/<filename>'.

    However, when requesting the file, the path should be '/files/courseware/<chapter_id>/<filename>'.
    """
    @tornado.web.authenticated
    def validate_absolute_path(self, root, absolute_path):
        username = self.get_current_user()
        chapter_id = self.request.path.split('/')[-2]
        filename = self.request.path.split('/')[-1]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and (owner[0] == username or get_user_role(username) == 'admin'):
                return absolute_path
            else:
                cursor.execute('''
                    SELECT is_visible FROM courseware WHERE chapter_id = ? AND filename = ?
                ''', (chapter_id, filename))
                is_visible = cursor.fetchone()
                if is_visible and is_visible[0] == 1:
                    return absolute_path
                else:
                    raise tornado.web.HTTPError(403)
        except sqlite3.Error:
            raise tornado.web.HTTPError(500)
        finally:
            conn.close()


class AllCoursesHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        """
        Returns all the courses.
        """
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, title, description FROM courses
            ''')
            courses = cursor.fetchall()
            self.write(json.dumps(courses))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


class EvaluationHandler(BaseHandler):
    """
    Handles the evaluation of a course.

    Students can evaluate a course by giving a rating and feedback comments.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Evaluates a course.

        Required arguments:
        - course_id: The id of the course.
        - rating: The rating of the course.
        - feedback: The feedback comments for the course.

        CREATE TABLE IF NOT EXISTS evaluations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        course_id TEXT NOT NULL,
                        student TEXT NOT NULL,
                        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                        feedback TEXT,
                        date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        rating = self.get_argument("rating")
        feedback = self.get_argument("feedback")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO evaluations (course_id, student, rating, feedback) VALUES (?, ?, ?, ?, ?)
            ''', (course_id, username, rating, feedback))
            conn.commit()
            self.write("Course evaluated successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def get(self):
        """
        Gets the evaluation of a course.

        Required arguments:
        - course_id: The id of the course.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT rating, feedback, date_submitted, student FROM evaluations WHERE course_id = ?
            ''', (course_id,))
            evaluations = cursor.fetchall()
            self.write(json.dumps(evaluations))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Deletes a comment from the evaluation of a course.

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
                SELECT student FROM evaluations WHERE id = ?
            ''', (comment_id,))
            student = cursor.fetchone()
            if student and student[0] == username:
                cursor.execute('''
                    DELETE FROM evaluations WHERE id = ?
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
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        comment = self.get_argument("comment")

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

        Required arguments:
        - course_id: The id of the course.
        """
        course_id = self.get_argument("course_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT student, comment, date_submitted FROM course_comments WHERE course_id = ?
            ''', (course_id,))
            comments = cursor.fetchall()
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


class CourseProgressHandler(BaseHandler):
    """
    Handles the progress of a course for a student.
    """
    @tornado.web.authenticated
    def get(self):
        """
        Gets the progress of a course for the current user.

        Required arguments:
        - course_id: The id of the course.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT progress FROM course_progress WHERE course_id = ? AND student = ?
            ''', (course_id, username))
            progress = cursor.fetchone()
            if progress:
                self.write(json.dumps({"progress": progress[0]}))
            else:
                self.write(json.dumps({"progress": 0}))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def post(self):
        """
        Updates the progress of a course for the current user.

        Required arguments:
        - course_id: The id of the course.
        - progress: The progress of the course.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        progress = self.get_argument("progress")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO course_progress (course_id, student, progress) VALUES (?, ?, ?)
                ON CONFLICT(course_id, student) DO UPDATE SET progress = excluded.progress
            ''', (course_id, username, progress))
            conn.commit()
            self.write("Progress updated successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/admin", AdminHandler), 
        (r"/logout", LogoutHandler),
        (r"/inbox", InboxHandler),
        (r"/courses/\d+/comments", CourseCommentsHandler),
        (r"/my/course", MyCourseHandler),
        (r"/add/teacher", AddTeacherHandler),
        (r"/add/course", AddCourseHandler),
        (r"/course/\d+", DetailedCourseHandler),
        (r"/course/notif", CourseNotifHandler),
        (r"/course/like", CourseLikeHandler),
        (r"/course/recommend", CourseRecommendHandler),
        (r"/anticheat", VideoAnticheatHandler),
        (r"/courseware", CourseWareHandler),
        (r"/files/courseware/(.*)", CourseWareFileHandlerWithAuth, {"path": "files/courseware"}),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        (r"/course/all", AllCoursesHandler),
        (r"/evaluation", EvaluationHandler),
        (r"/course/progress/\d+", CourseProgressHandler),
    ], cookie_secret=SECRET_KEY, login_url="/login")

if __name__ == "__main__":
    app = make_app()
    app.listen(args.port)
    print(f"Server started at http://localhost:{args.port}")
    tornado.ioloop.PeriodicCallback(VideoAnticheatHandler.check_inactivity, 60000).start()
    tornado.ioloop.IOLoop.current().start()

