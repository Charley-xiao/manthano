import hashlib
import uuid
import json
import tornado.web
from components.user.base import BaseHandler
from database import validate_user, add_user, add_teacher_request, get_users_by_role
from components.sendEmail import send_email

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