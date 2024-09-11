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
            email TEXT NOT NULL
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