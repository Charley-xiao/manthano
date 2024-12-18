import json
import sqlite3
import re
import tornado.web
from components.user.base import BaseHandler
from database import DATABASE, get_user_role

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
                SELECT id, title, description, owner FROM courses
            ''')
            courses = cursor.fetchall()
            update_courses = []

            cursor.execute('''
                SELECT course_id
                FROM rating
            ''')
            course_ids = cursor.fetchall()

            for course in courses:
                star = 2+course[0]*23%31*1.0/10.0
                for course_id in course_ids:
                    if course_id == course[0]:
                        cursor.execute('''
                            SELECT AVG(star) AS average_star
                            FROM rating
                            WHERE course_id = ?
                        ''', (course_id))

                        star = cursor.fetchall()[0]
                        print(star)

                update_courses.append({'id': course[0], 'title': course[1], 'instructor': course[3], 'description': course[2], 'rating': star})

            self.write(json.dumps(update_courses))
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
                    SELECT title, description, owner, category FROM add_course_requests
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
        category = self.get_argument("category")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if action:
                if get_user_role(username) == 'admin':
                    if action == 'approve':
                        cursor.execute('''
                            INSERT INTO courses (title, description, owner, category) VALUES (?, ?, ?, ?)
                        ''', (title, description, owner, category))
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
                        INSERT INTO add_course_requests (title, description, owner, category) VALUES (?, ?, ?, ?)
                    ''', (title, description, username, category))
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
                students = [student[0] for student in students]
                course = list(course)
                course.append(students)

                cursor.execute('''
                    SELECT id, title, content, type, published FROM chapters WHERE course_id = ?
                ''', (course_id,))
                chapters = cursor.fetchall()
                if get_user_role(username) == 'student':
                    chapters = [chapter for chapter in chapters if chapter[4] == 1]

                new_chapters = []
                for chapter in chapters:
                    cursor.execute('''
                        SELECT filename FROM courseware WHERE chapter_id = ?
                    ''', (chapter[0],))
                    courseware = cursor.fetchall()
                    courseware = [{'name': c[0], 'link': f'/files/courseware/{c[0]}'} for c in courseware]
                    chapter = list(chapter)
                    print(chapter)
                    chapter.append(courseware)
                    print(chapter)
                    chapter = {'id': chapter[0], 'title': chapter[1], 'content': chapter[2], 'type': chapter[3], 'published': chapter[4], 'courseware': courseware}
                    new_chapters.append(chapter)

                course.append(new_chapters)
                course = {'id': course_id, 'title': course[0], 'description': course[1], 'owner': course[2], 'type': course[3], 'students': course[4], 'chapters': new_chapters}
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
                SELECT chapter_id FROM course_progress WHERE username = ? AND chapter_id IN (SELECT id FROM chapters WHERE course_id = ?)
            ''', (username, course_id))
            chapters = cursor.fetchall()
            chapters = {'chapters': chapters}
            print(chapters)
            self.write(json.dumps(chapters))
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def post(self):
        """
        Updates the progress of a course for the current user.
        Essentially, this handler is used to mark a chapter as completed by the student.

        Required arguments:
        - chapter_id: The id of the chapter.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO course_progress (username, chapter_id) VALUES (?, ?)
            ''', (username, chapter_id))
            conn.commit()
            self.write("Chapter marked as completed successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()
        

class AddCourseStudentHandler(BaseHandler):
    """
    POST /courses/<course_id>/students
    """
    @tornado.web.authenticated
    def post(self):
        """
        Adds a student to the course.
        """
        username = self.get_current_user()
        course_id = re.search(r'/(\d+)', self.request.path).group(1)
        student = self.get_argument("student")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses WHERE id = ?
            ''', (course_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    INSERT INTO course_students (course_id, student) VALUES (?, ?)
                ''', (course_id, student))
                conn.commit()
                self.write("Student added to the course successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to add students to this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Removes a student from the course.
        """
        username = self.get_current_user()
        course_id = re.search(r'/(\d+)', self.request.path).group(1)
        student = self.get_argument("student")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses WHERE id = ?
            ''', (course_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    DELETE FROM course_students WHERE course_id = ? AND student = ?
                ''', (course_id, student))
                conn.commit()
                self.write("Student removed from the course successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to remove students from this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()