import sqlite3
import bcrypt

def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def validate_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_hash = row[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    return False

import tornado.ioloop
import tornado.web
from tornado.web import authenticated

create_user_table()

with open('secret', 'r') as f:
    SECRET_KEY = f.read().strip()

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    @authenticated
    def get(self):
        self.write(f"Welcome, {self.current_user.decode('utf-8')}! You're logged in.")

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
            self.set_secure_cookie("user", username)
            self.redirect("/")
        else:
            self.write("Login failed. Incorrect username or password.")

class RegisterHandler(BaseHandler):
    def get(self):
        self.write('<html><body>'
                   '<form action="/register" method="post">'
                   'Username: <input type="text" name="username"><br>'
                   'Password: <input type="password" name="password"><br>'
                   '<input type="submit" value="Register">'
                   '</form></body></html>')

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        if add_user(username, password):
            self.write(f"User {username} registered successfully!")
            self.redirect("/login")
        else:
            self.write("Registration failed. Username already taken.")

class LogoutHandler(BaseHandler):
    @authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/logout", LogoutHandler),
    ], cookie_secret=SECRET_KEY, login_url="/login")

if __name__ == "__main__":
    app = make_app()
    app.listen(9265)
    tornado.ioloop.IOLoop.current().start()
