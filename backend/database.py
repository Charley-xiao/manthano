import sqlite3
import bcrypt
import re

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

    # Add some courses by ms.smith
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)', ('CS201', 'Advanced Data Structures', 'ms.smith', 'Computer Science'))
    cursor.execute('INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)', ('CS101', 'Intro to Computer Science', 'ms.smith', 'Computer Science'))

    # Fetch the course IDs to add chapters and students
    cursor.execute('SELECT id FROM courses WHERE title = "CS101"')
    cs101_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM courses WHERE title = "CS201"')
    cs201_id = cursor.fetchone()[0]

    # Add some chapters for CS101
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Getting Started', 'Welcome to Computer Science', 'teaching', cs101_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Intro to Programming', 'Understanding Python Basics', 'teaching', cs101_id))

    # Add some chapters for CS201
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Data Structures 101', 'Understanding Stacks and Queues', 'teaching', cs201_id))
    cursor.execute('INSERT INTO chapters (title, content, type, course_id) VALUES (?, ?, ?, ?)', ('Tree Structures', 'Binary Trees and Traversals', 'teaching', cs201_id))

    # Add students to courses
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs101_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs101_id, 'john.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs201_id, 'jane.doe'))
    cursor.execute('INSERT INTO course_students (course_id, student) VALUES (?, ?)', (cs201_id, 'alice.wong'))

    # Add some courseware
    cursor.execute('SELECT id FROM chapters WHERE title = "Getting Started"')
    intro_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('welcome_guide.pdf', intro_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('welcome_video.mp4', intro_id))

    cursor.execute('SELECT id FROM chapters WHERE title = "Intro to Programming"')
    programming_id = cursor.fetchone()[0]
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('python_intro.pdf', programming_id))
    cursor.execute('INSERT INTO courseware (filename, chapter_id) VALUES (?, ?)', ('python_basics.mp4', programming_id))

    # Add some detailed posts
    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)', 
                   ('Study Group Forming', cs101_id, 'Jane Doe', 
                    'Hello everyone, I’m forming a study group for CS101. \n\n'
                    'The goal of our group will be to explore key concepts such as programming basics, '
                    'problem-solving strategies, and working through Python exercises together. I believe that learning '
                    'in a group setting can enhance understanding through different perspectives and discussions. \n\n'
                    'We’ll meet weekly on Tuesdays and Thursdays for an hour each. Each session will involve a brief recap '
                    'of the week’s lectures, followed by collaborative problem-solving. Bring your questions, and let’s help each other excel!\n\n'
                    'Please comment below if you are interested, and we can finalize the meeting schedule. Looking forward to learning together!', 
                    15, 'Plain'))

    cursor.execute('INSERT INTO posts (title, course_id, sender_name, content, likes, tag) VALUES (?, ?, ?, ?, ?, ?)', 
                   ('Python Tips & Tricks', cs101_id, 'John Doe', 
                    'Hey everyone, \n\n'
                    'As we dive deeper into Python, I thought it would be helpful to share some tips and tricks that have been a game-changer for me. \n\n'
                    '1. **List Comprehensions**: Simplify your loops and make your code more Pythonic.\n'
                    '2. **Debugging with pdb**: Use the built-in Python debugger to step through your code.\n'
                    '3. **Virtual Environments**: Always set up a virtual environment for your projects to manage dependencies.\n\n'
                    'I’ve also found that breaking down complex problems into smaller functions makes the code more readable and easier to test. '
                    'Let’s use this thread to share more tips and discuss how we can write cleaner and more efficient code. What are your favorite Python hacks?', 
                    25, 'Hot'))

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
                    40, 'Hot'))

    conn.commit()
    conn.close()


def init_db():
    create_user_table()
    create_add_teacher_request_table()
    create_inbox_table()
    create_course_table()
    create_join_course_requests_table()
    create_add_course_requests_table()
    create_posts_table()
    add_fake_data()