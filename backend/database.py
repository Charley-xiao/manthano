import sqlite3
import bcrypt
import re

DATABASE = 'db'

def validate_email_format(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

class User:
    def __init__(self, username, email, role):
        self.username = username
        self.email = email
        self.role = role

    def __str__(self):
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}')"

    def __repr__(self):
        return str(self)
    
class Chapter:
    def __init__(self, id, title, content, type):
        self.id = id
        self.title = title
        self.content = content
        self.type = type

    def __str__(self):
        return f"Chapter(id={self.id}, title='{self.title}', content='{self.content}')"

    def __repr__(self):
        return str(self)
    
class Course:
    def __init__(self, id, title, description, chapters, owner):
        self.id = id
        self.title = title
        self.description = description
        self.chapters = chapters
        self.owner = owner
        self.students = []

    def __str__(self):
        return f"Course(id={self.id}, title='{self.title}', description='{self.description}', chapters={self.chapters}, owner='{self.owner}', students={self.students})"
    
    def __repr__(self):
        return str(self)

def create_user_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'student'
        )
    ''')
    conn.commit()
    conn.close()

def validate_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_hash = row[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    return False

def add_user(username, password, email, role='student'):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if not validate_email_format(email):
        return False

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)', (username, password_hash, email, role))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def get_user_role(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE username=?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return None

def get_users_by_role(role):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'SELECT username, email, role FROM users WHERE role="{role}"')
    rows = cursor.fetchall()
    conn.close()

    return [User(*row) for row in rows]

def create_add_teacher_request_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS add_teacher_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            UNIQUE(username, email),
            FOREIGN KEY(username) REFERENCES users(username),
            FOREIGN KEY(email) REFERENCES users(email)
        )
    ''')
    conn.commit()
    conn.close()

def add_teacher_request(username, password, email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if not validate_email_format(email):
        return False

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute('INSERT INTO add_teacher_requests (username, password_hash, email) VALUES (?, ?, ?)', (username, password_hash, email))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def create_inbox_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inbox (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            read INTEGER NOT NULL DEFAULT 0,
            type TEXT NOT NULL DEFAULT 'message', -- message, request
            priority INTEGER NOT NULL DEFAULT 0, -- 0: normal, 1: high
            FOREIGN KEY(sender) REFERENCES users(username),
            FOREIGN KEY(receiver) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def create_course_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            owner TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'open', -- open, ongoing, closed
            FOREIGN KEY(owner) REFERENCES users(username)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_likes (
            course_id INTEGER NOT NULL,
            student TEXT NOT NULL,
            FOREIGN KEY(course_id) REFERENCES courses(id),
            FOREIGN KEY(student) REFERENCES users(username)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'teaching', -- teaching, homework, project
            course_id INTEGER NOT NULL,
            published INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_students (
            course_id INTEGER NOT NULL,
            student TEXT NOT NULL,
            FOREIGN KEY(course_id) REFERENCES courses(id),
            FOREIGN KEY(student) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def create_join_course_requests_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS join_course_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY(student) REFERENCES users(username),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_add_course_requests_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS add_course_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY(owner) REFERENCES users(username),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')
    conn.commit()
    conn.close()

def init_db():
    create_user_table()
    create_add_teacher_request_table()
    create_inbox_table()
    create_course_table()
    create_join_course_requests_table()
    create_add_course_requests_table()