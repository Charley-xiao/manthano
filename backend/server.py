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
import re
import time 
from database import DATABASE, validate_user, add_user, get_user_role, get_users_by_role, User, add_teacher_request
from database import init_db
import argparse
import toml
import json
import hashlib
import uuid
from recommender import recommend_courses_with_content

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


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        role = self.get_user_role()
        self.write(f"Welcome, {self.current_user.decode('utf-8')}! You're logged in as {role}.")


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
            self.redirect("/")
        else:
            self.write("Login failed. Incorrect username or password.")


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
        role = self.get_argument("role")

        if role == 'admin':
            self.write("Registration failed. Admin registration is not allowed.")
        elif role == 'student':
            if add_user(username, password, email, role):
                self.write(f"User {username} registered successfully as {role}!")
                self.redirect("/login")
            else:
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

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/admin", AdminHandler), 
        (r"/logout", LogoutHandler),
        (r"/inbox", InboxHandler),
        (r"/my/course", MyCourseHandler),
        (r"/add/teacher", AddTeacherHandler),
        (r"/add/course", AddCourseHandler),
        (r"/course/\d+", DetailedCourseHandler),
        (r"/course/notif", CourseNotifHandler),
        (r"/course/like", CourseLikeHandler),
        (r"/course/recommend", CourseRecommendHandler),
        (r"/anticheat", VideoAnticheatHandler)
    ], cookie_secret=SECRET_KEY, login_url="/login")

if __name__ == "__main__":
    app = make_app()
    app.listen(args.port)
    print(f"Server started at http://localhost:{args.port}")
    tornado.ioloop.PeriodicCallback(VideoAnticheatHandler.check_inactivity, 60000).start()
    tornado.ioloop.IOLoop.current().start()

