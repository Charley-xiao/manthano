import sqlite3
import bcrypt
import re
import os

DATABASE = 'db.db'

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

class Post:
    def __init__(self, id, title, course_id, sender_name, content, likes, tag):
        self.id = id
        self.title = title
        self.course_id = course_id
        self.sender_name = sender_name
        self.content = content
        self.likes = likes
        self.tag = tag

    def __str__(self):
        return f"Post(id={self.id}, title='{self.title}', course_id={self.course_id}, sender_name='{self.sender_name}', content='{self.content}', likes={self.likes}, tag='{self.tag}')"

class Rating:
    def __init__(self, star, difficulty, workload, grading, gain, comment):
        self.star = star
        self.difficulty = difficulty
        self.workload = workload
        self.grading = grading
        self.gain = gain
        self.comment = comment

    def __str__(self):
        return f"Rating(star={self.star}, difficulty={self.difficulty}, workload={self.workload}, grading={self.grading}, gain={self.gain}, comment='{self.comment}')"


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

def get_users_by_role_with_id(role):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'SELECT id, username, email, role FROM users WHERE role="{role}"')
    rows = cursor.fetchall()
    conn.close()

    return [{"id": row[0], "username": row[1]} for row in rows]

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
            published INTEGER NOT NULL DEFAULT 1,
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

    # course progress
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_progress (
            chapter_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            PRIMARY KEY (chapter_id, username),
            FOREIGN KEY(chapter_id) REFERENCES chapters(id),
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')

    # INSERT INTO hwpj (chapter_id, filename) VALUES (?, ?)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hwpj (
            chapter_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            FOREIGN KEY(chapter_id) REFERENCES chapters(id)
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

def create_posts_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            content TEXT NOT NULL,
            likes INTEGER NOT NULL,
            tag TEXT NOT NULL,
            date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_posts(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM posts where id = {id}')
    rows = cursor.fetchall()
    conn.close()

    return [Post(*row) for row in rows]

def add_post(course_id, title, sender_name, content, likes, tag):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # try:
    #     cursor.execute('INSERT INTO posts (course_id, title, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)', (course_id, title, sender_name, content, likes, tag))
    #     conn.commit()
    # except sqlite3.IntegrityError:
    #     return False
    # finally:
    #     conn.close()
    cursor.execute('INSERT INTO posts (course_id, title, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)', (course_id, title, sender_name, content, likes, tag))
    conn.commit()
    return True

def create_rating_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rating (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            sender_name TEXT NOT NULL,
            star INTEGER NOT NULL CHECK (star >= 1 AND star <= 5),
            difficulty TEXT NOT NULL,
            workload TEXT NOT NULL,
            grading TEXT NOT NULL,
            gain TEXT NOT NULL,
            comment TEXT NOT NULL,
            likes INTEGER NOT NULL,
            date_submitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(course_id) REFERENCES courses(id),
            FOREIGN KEY(sender_name) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def add_rating(star, difficulty, workload, grading, gain, comment, course_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO rating (star, difficulty, workload, grading, gain, comment, likes, course_id) VALUES (?, ?, ?, ?, ?, ?, 0, ?)',
                   (star, difficulty, workload, grading, gain, comment, course_id))
    conn.commit()
    conn.close()

def get_rating(course_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rating WHERE course_id=?', (course_id,))
    rows = cursor.fetchall()
    conn.close()

    return [Rating(*row[1:]) for row in rows]

def add_fake_data():
    # Add some users with varied passwords and realistic emails
    add_user('admin', 'StrongAdminPass2024!', 'admin@schoolplatform.edu', 'admin')
    add_user('mr.johnson', 'TeacherP@ss123', 'johnson.math@schoolplatform.edu', 'teacher')
    add_user('ms.smith', 'Smith2024Teach!', 'smith.cs@schoolplatform.edu', 'teacher')
    add_user('jane.doe', 'JDoe@Stud2024', 'jane.doe@schoolplatform.edu', 'student')
    add_user('john.doe', 'JDoe123#Pass', 'john.doe@schoolplatform.edu', 'student')
    add_user('alice.wong', 'AliceW2024!', 'alice.wong@schoolplatform.edu', 'student')

    # Add a teacher request
    add_teacher_request('mr.brown', 'NewTeach123!', 'brown.history@schoolplatform.edu')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Add some courses by ms.smith and mr.johnson
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('CS201', 'Advanced Data Structures', 'ms.smith', 'Computer Science'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('CS101', 'Intro to Computer Science', 'ms.smith', 'Computer Science'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('MA101', 'Algebra Basics', 'ms.smith', 'Mathematics'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('PH101', 'Introduction to Philosophy', 'mr.johnson', 'Philosophy'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('PH201', 'Ethics and Morality', 'mr.johnson', 'Philosophy'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('MA201', 'Calculus I', 'ms.smith', 'Mathematics'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('MA202', 'Calculus II', 'ms.smith', 'Mathematics'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('PH301', 'Philosophy of Mind', 'mr.johnson', 'Philosophy'))
    # Add more detailed courses
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('BIO101', 'Introduction to Biology', 'mr.johnson', 'Biology'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('BIO201', 'Genetics and Evolution', 'mr.johnson', 'Biology'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('CHEM101', 'General Chemistry', 'ms.smith', 'Chemistry'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('CHEM201', 'Organic Chemistry', 'ms.smith', 'Chemistry'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('PHY101', 'Physics I: Mechanics', 'mr.johnson', 'Physics'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('PHY201', 'Physics II: Electromagnetism', 'mr.johnson', 'Physics'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('ENG101', 'English Literature', 'ms.smith', 'Literature'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('ENG201', 'Creative Writing', 'ms.smith', 'Literature'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('HIS101', 'World History', 'mr.johnson', 'History'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('HIS201', 'Modern History', 'mr.johnson', 'History'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('ART101', 'Introduction to Art', 'ms.smith', 'Art'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('ART201', 'Art History', 'ms.smith', 'Art'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('MUS101', 'Music Theory', 'mr.johnson', 'Music'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('MUS201', 'History of Music', 'mr.johnson', 'Music'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('PSY101', 'Introduction to Psychology', 'ms.smith', 'Psychology'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('PSY201', 'Cognitive Psychology', 'ms.smith', 'Psychology'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('SOC101', 'Introduction to Sociology', 'mr.johnson', 'Sociology'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)',
                   ('SOC201', 'Social Psychology', 'mr.johnson', 'Sociology'))

    # Fetch the course IDs to add chapters and students
    cursor.execute('SELECT id FROM courses WHERE title = "CS101"')
    cs101_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM courses WHERE title = "CS201"')
    cs201_id = cursor.fetchone()[0]

    # Add some chapters for CS101
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Getting Started', 'https://www.youtube.com/embed/6ARjrl74nc4', 'teaching', cs101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Intro to Programming', 'https://player.bilibili.com/player.html?isOutside=true&aid=113525263434587&bvid=BV1HuBvYMEdF&cid=26898860143&p=1', 'teaching', cs101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Python Basics', 'https://www.youtube.com/embed/8DvywoWv6fI', 'homework', cs101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Python Functions', 'https://www.youtube.com/embed/9Os0o3wzS_I', 'homework', cs101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Python Project 1', 'https://www.youtube.com/embed/8DvywoWv6fI', 'project', cs101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Python Project 2', 'https://www.youtube.com/embed/9Os0o3wzS_I', 'project', cs101_id))
    # Add some chapters for CS201
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Data Structures 101', 'https://www.youtube.com/embed/AWclMLWpTEs', 'teaching', cs201_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Tree Structures', 'https://www.youtube.com/embed/2f3gB3zSL08', 'teaching', cs201_id))

    # Fetch the course IDs to add chapters for more courses
    cursor.execute('SELECT id FROM courses WHERE title = "MA101"')
    ma101_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM courses WHERE title = "PH101"')
    ph101_id = cursor.fetchone()[0]

    # Add some chapters for MA101
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Algebra Basics', 'https://www.youtube.com/embed/1', 'teaching', ma101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Linear Equations', 'https://www.youtube.com/embed/2', 'homework', ma101_id))

    # Add some chapters for PH101
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Introduction to Philosophy', 'https://www.youtube.com/embed/3', 'teaching', ph101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Ethics and Morality', 'https://www.youtube.com/embed/4', 'project', ph101_id))

    # Fetch the course IDs to add chapters for more courses
    cursor.execute('SELECT id FROM courses WHERE title = "BIO101"')
    bio101_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM courses WHERE title = "CHEM101"')
    chem101_id = cursor.fetchone()[0]

    # Add some chapters for BIO101
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Introduction to Biology', 'https://www.youtube.com/embed/5', 'teaching', bio101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Genetics Basics', 'https://www.youtube.com/embed/6', 'homework', bio101_id))

    # Add some chapters for CHEM101
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('General Chemistry', 'https://www.youtube.com/embed/7', 'teaching', chem101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Organic Chemistry Basics', 'https://www.youtube.com/embed/8', 'project', chem101_id))

    # Fetch the course IDs to add chapters for additional courses (e.g., MA201)
    cursor.execute('SELECT id FROM courses WHERE title = "MA201"')
    ma201_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM courses WHERE title = "PH201"')
    ph201_id = cursor.fetchone()[0]

    # Add chapters for MA201
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Limits and Continuity', 'https://www.youtube.com/embed/9', 'teaching', ma201_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Derivatives', 'https://www.youtube.com/embed/10', 'homework', ma201_id))

    # Add chapters for PH201
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Moral Philosophy', 'https://www.youtube.com/embed/11', 'teaching', ph201_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)',
                   ('Applied Ethics', 'https://www.youtube.com/embed/12', 'project', ph201_id))

    # Add students to courses
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs101_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs101_id, 'john.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs201_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs201_id, 'alice.wong'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (ma101_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (ma101_id, 'john.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (ph101_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (ph101_id, 'alice.wong'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (bio101_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (bio101_id, 'john.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (chem101_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (chem101_id, 'alice.wong'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (ma201_id, 'john.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (ma201_id, 'alice.wong'))

    # Add courseware for additional chapters

    # Fetch the chapter IDs for CS101 chapters
    cursor.execute('SELECT id FROM chapters WHERE title = "Python Basics"')
    python_basics_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM chapters WHERE title = "Python Functions"')
    python_functions_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM chapters WHERE title = "Python Project 1"')
    python_project1_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM chapters WHERE title = "Python Project 2"')
    python_project2_id = cursor.fetchone()[0]

    # Add courseware for Python Basics
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('python_basics_notes.pdf', python_basics_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('python_basics_slides.pptx', python_basics_id))

    # Add courseware for Python Functions
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('python_functions_notes.pdf', python_functions_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('python_functions_examples.zip', python_functions_id))

    # Add courseware for Python Project 1
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('project1_description.pdf', python_project1_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('project1_sample_code.py', python_project1_id))

    # Add courseware for Python Project 2
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('project2_description.pdf', python_project2_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('project2_sample_code.py', python_project2_id))

    # Fetch the chapter IDs for CS201 chapters
    cursor.execute('SELECT id FROM chapters WHERE title = "Data Structures 101"')
    data_structures_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM chapters WHERE title = "Tree Structures"')
    tree_structures_id = cursor.fetchone()[0]

    # Add courseware for Data Structures 101
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('data_structures_notes.pdf', data_structures_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('data_structures_slides.pptx', data_structures_id))

    # Add courseware for Tree Structures
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('tree_structures_notes.pdf', tree_structures_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('tree_structures_examples.zip', tree_structures_id))

    # Fetch the chapter IDs for MA101 chapters
    cursor.execute('SELECT id FROM chapters WHERE title = "Algebra Basics"')
    algebra_basics_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM chapters WHERE title = "Linear Equations"')
    linear_equations_id = cursor.fetchone()[0]

    # Add courseware for Algebra Basics
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('algebra_basics_notes.pdf', algebra_basics_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('algebra_basics_practice_questions.pdf', algebra_basics_id))

    # Add courseware for Linear Equations
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('linear_equations_notes.pdf', linear_equations_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('linear_equations_homework.pdf', linear_equations_id))

    # Fetch the chapter IDs for PH101 chapters
    cursor.execute('SELECT id FROM chapters WHERE title = "Introduction to Philosophy"')
    intro_philosophy_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM chapters WHERE title = "Ethics and Morality"')
    ethics_morality_id = cursor.fetchone()[0]

    # Add courseware for Introduction to Philosophy
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('intro_philosophy_readings.pdf', intro_philosophy_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('intro_philosophy_slides.pptx', intro_philosophy_id))

    # Add courseware for Ethics and Morality
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('ethics_morality_case_studies.pdf', ethics_morality_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)',
                   ('ethics_morality_assignment.docx', ethics_morality_id))

    # Add some detailed posts

    # Posts for CS101
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Study Group Forming', cs101_id, 'Jane Doe',
                    'Hello everyone, I’m forming a study group for CS101. \n\n'
                    'The goal of our group will be to explore key concepts such as programming basics, '
                    'problem-solving strategies, and working through Python exercises together. I believe that learning '
                    'in a group setting can enhance understanding through different perspectives and discussions. \n\n'
                    'We’ll meet weekly on Tuesdays and Thursdays for an hour each. Each session will involve a brief recap '
                    'of the week’s lectures, followed by collaborative problem-solving. Bring your questions, and let’s help each other excel!\n\n'
                    'Please comment below if you are interested, and we can finalize the meeting schedule. Looking forward to learning together!',
                    15, 'Tech'))

    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Python Tips & Tricks', cs101_id, 'John Doe',
                    'Hey everyone, \n\n'
                    'As we dive deeper into Python, I thought it would be helpful to share some tips and tricks that have been a game-changer for me. \n\n'
                    '1. **List Comprehensions**: Simplify your loops and make your code more Pythonic.\n'
                    '2. **Debugging with pdb**: Use the built-in Python debugger to step through your code.\n'
                    '3. **Virtual Environments**: Always set up a virtual environment for your projects to manage dependencies.\n\n'
                    'I’ve also found that breaking down complex problems into smaller functions makes the code more readable and easier to test. '
                    'Let’s use this thread to share more tips and discuss how we can write cleaner and more efficient code. What are your favorite Python hacks?',
                    25, 'Academic'))

    # Posts for CS201
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Mastering Binary Trees', cs201_id, 'Alice Wong',
                    'Hi all, \n\n'
                    'In this post, I’d like to dive into binary trees, a foundational concept in data structures that will benefit us greatly '
                    'in our CS201 journey and beyond. \n\n'
                    '### Why Binary Trees?\n'
                    'Binary trees are essential for understanding algorithms like search (binary search trees), sorting, and hierarchical data representation. '
                    'They are also the basis for more complex structures like heaps and balanced trees (e.g., AVL and Red-Black Trees).\n\n'
                    '### Key Operations\n'
                    '- **Traversal**: Understanding in-order, pre-order, and post-order traversals is crucial.\n'
                    '- **Balancing**: Learn how self-balancing trees optimize operations.\n\n'
                    '### Practical Applications\n'
                    'Binary trees are used in scenarios such as database indexing, network routing, and even some AI algorithms. I’ve also found them '
                    'in file compression algorithms like Huffman encoding. \n\n'
                    'Let’s discuss how we can make these concepts intuitive. Share your thoughts or questions below!',
                    40, 'Health'))

    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Help with Linked Lists', cs201_id, 'John Doe',
                    'Hello CS201 classmates, \n\n'
                    'I\'m having trouble understanding how linked lists work, particularly when it comes to inserting and deleting nodes. '
                    'Does anyone have a good resource or can explain it in a way that\'s easy to grasp? Maybe we can form a study group to tackle this topic.',
                    12, 'Career'))

    # Posts for MA101
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Quadratic Equations Help', ma101_id, 'John Doe',
                    'Hi everyone, \n\n'
                    'I\'m struggling a bit with solving quadratic equations, especially when it comes to completing the square and using the quadratic formula. '
                    'Does anyone have any tips or resources that could help clarify these methods? I think understanding this is crucial for our upcoming exam. '
                    'Any assistance would be greatly appreciated!',
                    10, 'Tech'))

    # Posts for PH101
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Philosophy Discussion Group', ph101_id, 'Alice Wong',
                    'Hello PH101 classmates, \n\n'
                    'I\'m organizing a casual discussion group where we can delve deeper into the philosophical concepts covered in our lectures. '
                    'Our first topic will be "The Nature of Reality" as discussed by Plato and Aristotle. It would be great to hear diverse perspectives '
                    'and interpretations. Let me know if you\'re interested, and we can decide on a time that works for everyone.',
                    20, 'Lifestyle'))

    # Posts for BIO101
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Interesting Biology Article', bio101_id, 'Jane Doe',
                    'Hey everyone, \n\n'
                    'I came across an intriguing article on CRISPR gene editing and its potential to cure genetic diseases. '
                    'Here\'s the link: [CRISPR Breakthrough](https://example.com/crispr-article). '
                    'I thought it relates well to our recent lectures on genetics. Let\'s discuss the ethical implications and future possibilities in class!',
                    30, 'Health'))

    # Posts for CHEM101
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Lab Safety Reminder', chem101_id, 'Ms. Smith',
                    'Dear students, \n\n'
                    'As we approach our first laboratory session, I want to remind everyone about the importance of lab safety. '
                    'Please review the safety guidelines provided in the course materials, and make sure to wear appropriate protective gear. '
                    'If you have any questions or concerns, feel free to reach out to me before the lab session.',
                    50, 'Academic'))

    # Posts for MA201
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Understanding Limits', ma201_id, 'Alice Wong',
                    'Hi everyone, \n\n'
                    'Limits can be a bit tricky to understand, especially when dealing with approaching infinity or undefined points. '
                    'I found a helpful video that explains the concept clearly: [Understanding Limits](https://example.com/limits-video). '
                    'Hope this helps others too!',
                    22, 'Health'))

    # Posts for PH201
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)',
                   ('Ethical Dilemmas Discussion', ph201_id, 'Mr. Johnson',
                    'Dear students, \n\n'
                    'For our next class, please prepare to discuss various ethical dilemmas. Think about scenarios where moral principles may conflict, '
                    'and consider the reasoning behind different ethical decisions. I encourage you to bring real-world examples to enrich our discussion.',
                    35, 'Academic'))

    conn.commit()
    conn.close()


def init_db():
    os.remove(DATABASE)
    create_user_table()
    create_add_teacher_request_table()
    create_inbox_table()
    create_course_table()
    create_join_course_requests_table()
    create_add_course_requests_table()
    create_posts_table()
    create_rating_table()
    add_fake_data()