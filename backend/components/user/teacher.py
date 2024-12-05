import json
import sqlite3
import tornado.web
from components.user.base import BaseHandler
from database import DATABASE, get_user_role

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

class AllTeacherHandler(BaseHandler):
    """
    Return all teachers
    """
    @tornado.web.authenticated
    def get(self):
        """
        Return all teachers
        """
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, username FROM users WHERE role = "teacher"
            ''')
            teachers = cursor.fetchall()
            teachers = [{'id': teacher[0], 'username': teacher[1], 'thumbnail': "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
                          'rating': int(teacher[0])*11%31/10.0+2, 'description': "This is a sample descriptionduction"} for teacher in teachers]
            self.write(json.dumps(teachers))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

class GetTeacherHandler(BaseHandler):
    """
    find a teacher
    """
    @tornado.web.authenticated
    def get(self):
        """
        find a teacher
        """
        id = self.get_argument("id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT username FROM users WHERE id = ?
            ''',(id,))
            teachers = cursor.fetchall()
            teachers = [{'id': id, 'name': teacher[0], 'rating': int(id)*11%31/10.0+2} for teacher in teachers]
            self.write(json.dumps(teachers))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()