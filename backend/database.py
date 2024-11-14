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
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
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
            category TEXT,
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

    # courseware
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courseware (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            chapter_id INTEGER NOT NULL,
            FOREIGN KEY(chapter_id) REFERENCES chapters(id)
        )
    ''')

    # course comments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            student TEXT NOT NULL,
            comment TEXT NOT NULL,
            date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            title TEXT NOT NULL,
            owner TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            FOREIGN KEY(owner) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def add_fake_data():
    # Add some users
    add_user('admin', 'adminpass', 'admin@example.com', 'admin')
    add_user('teacher1', 'teacherpass', 'teacher1@example.com', 'teacher')
    add_user('teacher2', 'teacherpass', 'teacher2@example.com', 'teacher')
    add_user('student1', 'studentpass', 'student1@example.com', 'student')
    add_user('student2', 'studentpass', 'student2@example.com', 'student')
    add_user('student3', 'studentpass', 'student3@example.com', 'student')

    # Add a teacher request
    add_teacher_request('teacher3', 'teacherpass', 'teacher3@example.com')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Add some courses by teacher1
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)', ('CS102', 'Data Structures', 'teacher1', 'Computer Science'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)', ('CS101', 'Introduction to Computer Science', 'teacher1', 'Computer Science'))

    # Fetch the course IDs to add chapters and students
    cursor.execute('SELECT id FROM courses WHERE title = "CS101"')
    cs101_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM courses WHERE title = "CS102"')
    cs102_id = cursor.fetchone()[0]

    # Add some chapters for CS101
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Introduction', 'Basics of Computer Science', 'teaching', cs101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Programming', 'Introduction to Python', 'teaching', cs101_id))

    # Add some chapters for CS102
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Data Structures Overview', 'Arrays, Lists, Trees', 'teaching', cs102_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Linked Lists', 'Singly and Doubly Linked Lists', 'teaching', cs102_id))

    # Add students to courses
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs101_id, 'student1'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs101_id, 'student2'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs102_id, 'student1'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs102_id, 'student3'))

    # Add some courseware
    cursor.execute('SELECT id FROM chapters WHERE title = "Introduction"')
    introduction_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('intro.pdf', introduction_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('intro.mp4', introduction_id))

    cursor.execute('SELECT id FROM chapters WHERE title = "Programming"')
    programming_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('python.pdf', programming_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('python.mp4', programming_id))

    conn.commit()
    conn.close()


def init_db():
    create_user_table()
    create_add_teacher_request_table()
    create_inbox_table()
    create_course_table()
    create_join_course_requests_table()
    create_add_course_requests_table()
    add_fake_data()