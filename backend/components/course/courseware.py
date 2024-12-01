import os
import json
import time
import sqlite3
import tornado.web
from components.user.base import BaseHandler
from database import DATABASE, get_user_role

class CourseWareHandler(BaseHandler):
    """
    Handles the courseware of a chapter.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Uploads a courseware to the chapter.

        Supported file formats: PDF, MD, TXT, DOCX, PPTX, XLSX, JPG, PNG, MP4, MOV, AVI, MKV.

        Note:
        - The courseware will be stored in the 'files/courseware' directory.
        - The filename will be hashed and stored in the database.
        - Only the owner of the course can upload courseware.
        - The courseware is invisible to students by default.

        Required arguments:
        - chapter_id: The id of the chapter.
        - file: The file to upload.

        Returns:
        - The filename of the uploaded courseware.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        file = self.request.files['file'][0]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                filename = file['filename'] # + time.strftime('%Y%m%d%H%M%S') # Add timestamp for versioning
                file_path = f'files/courseware/{chapter_id}/{filename}'
                if not os.path.exists(f'files/courseware/{chapter_id}'):
                    os.makedirs(f'files/courseware/{chapter_id}')
                with open(file_path, 'wb') as f:
                    f.write(file['body'])
                cursor.execute('''
                    INSERT INTO courseware (chapter_id, filename) VALUES (?, ?)
                ''', (chapter_id, filename))
                conn.commit()
                self.write(filename)
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to upload courseware to this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def get(self):
        """
        Returns the courseware of the chapter.

        Note:
        - If the request is sent by a student, courseware that is not published by the teacher will not be shown.

        Required arguments:
        - chapter_id: The id of the chapter.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    SELECT filename FROM courseware WHERE chapter_id = ?
                ''', (chapter_id,))
                courseware = cursor.fetchall()
                self.write(json.dumps(courseware))
            else:
                cursor.execute('''
                    SELECT published FROM chapters WHERE id = ?
                ''', (chapter_id,))
                published = cursor.fetchone()
                if published and published[0] == 1:
                    cursor.execute('''
                        SELECT filename, is_visible, is_downloadable FROM courseware WHERE chapter_id = ?
                    ''', (chapter_id,))
                    courseware = cursor.fetchall()
                    if get_user_role(username) == 'student':
                        courseware = [file for file in courseware if file[1] == 1]
                    self.write(json.dumps(courseware))
                else:
                    self.set_status(403)
                    self.write("Forbidden: You do not have permission to access the courseware of this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Deletes the courseware of the chapter.

        Note:
        - Only the owner of the course can delete courseware.

        Required arguments:
        - chapter_id: The id of the chapter.
        - filename: The filename of the courseware.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        filename = self.get_argument("filename")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    DELETE FROM courseware WHERE chapter_id = ? AND filename = ?
                ''', (chapter_id, filename))
                file_path = f'files/courseware/{filename}'
                if os.path.exists(file_path):
                    os.remove(file_path)
                conn.commit()
                self.write("Courseware deleted successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to delete courseware from this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def put(self):
        """
        Updates the visibility or downloadability of the courseware of the chapter.

        Note:
        - Only the owner of the course can update the visibility or downloadability of courseware.

        Required arguments:
        - chapter_id: The id of the chapter.
        - filename: The filename of the courseware.
        - is_visible: The visibility status of the courseware.
        - is_downloadable: The downloadability status of the courseware.

        Returns:
        - The updated visibility status of the courseware.
        - The updated downloadability status of the courseware.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        filename = self.get_argument("filename")
        is_visible = self.get_argument("is_visible")
        is_downloadable = self.get_argument("is_downloadable")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    UPDATE courseware SET is_visible = ?, is_downloadable = ? WHERE chapter_id = ? AND filename = ?
                ''', (is_visible, is_downloadable, chapter_id, filename))
                conn.commit()
                self.write({"is_visible": is_visible, "is_downloadable": is_downloadable})
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to update the visibility of courseware in this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()


class CourseWareFileHandlerWithAuth(tornado.web.StaticFileHandler):
    """
    File handler with authentication for courseware.

    IMPORTANT: This is a security risk if not handled properly.

    1. If the user is the owner of the course or admin, they can access the courseware.
    2. If the user is a student, they can access the courseware only if it is visible.

    However, when requesting the file, the path should be '/files/courseware/<chapter_id>/<filename>'.
    """
    def validate_absolute_path(self, root, absolute_path):
        username = self.get_current_user()
        chapter_id = self.request.path.split('/')[-2]
        filename = self.request.path.split('/')[-1]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and (owner[0] == username or get_user_role(username) == 'admin'):
                return absolute_path
            else:
                try:
                    cursor.execute('''
                        SELECT is_visible FROM courseware WHERE chapter_id = ? AND filename = ?
                    ''', (chapter_id, filename))
                    is_visible = cursor.fetchone()
                    if is_visible and is_visible[0] == 1:
                        return absolute_path
                except sqlite3.Error:
                    return absolute_path
                else:
                    raise tornado.web.HTTPError(403)
        except sqlite3.Error as e:
            self.set_status(500)
            print(e)
            self.write(str(e))
        finally:
            conn.close()


class HomeworkProjectHandler(BaseHandler):
    """
    Handles the homework and project submissions of a chapter.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Uploads a homework or project submission to the chapter.

        Supported file formats: PDF, MD, TXT, DOCX, PPTX, XLSX, JPG, PNG, MP4, MOV, AVI, MKV.

        Note:
        - The submission will be stored in the 'files/hwpj' directory.
        - The filename will be hashed and stored in the database.
        - Only students enrolled in the course can upload submissions.
        - The submission is invisible to other students by default.

        Required arguments:
        - chapter_id: The id of the chapter.
        - file: The file to upload.

        Returns:
        - The filename of the uploaded submission.
        """
        username = self.get_current_user()
        course_id = self.get_argument("course_id")
        chapter_id = self.get_argument("chapter_id")
        file = self.request.files['file'][0]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT student FROM course_students WHERE course_id = ? AND student = ?
            ''', (course_id, username))
            student = cursor.fetchone()
            if student:
                filename = file['filename'] # + time.strftime('%Y%m%d%H%M%S') # Add timestamp for versioning
                file_path = f'files/hwpj/{chapter_id}/{filename}'
                if not os.path.exists(f'files/hwpj/{chapter_id}'):
                    os.makedirs(f'files/hwpj/{chapter_id}')
                with open(file_path, 'wb') as f:
                    f.write(file['body'])
                cursor.execute('''
                    INSERT INTO hwpj (chapter_id, filename) VALUES (?, ?)
                ''', (chapter_id, filename))
                conn.commit()
                self.write(filename)
            else:
                self.set_status(403)
                self.write("Forbidden: You are not enrolled in this course.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def get(self):
        """
        Returns the submissions of the chapter.

        Note:
        - If the request is sent by a student, submissions that are not published by the teacher will not be shown.

        Required arguments:
        - chapter_id: The id of the chapter.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    SELECT filename FROM hwpj WHERE chapter_id = ?
                ''', (chapter_id,))
                submissions = cursor.fetchall()
                self.write(json.dumps(submissions))
            else:
                cursor.execute('''
                    SELECT published FROM chapters WHERE id = ?
                ''', (chapter_id,))
                published = cursor.fetchone()
                if published and published[0] == 1:
                    cursor.execute('''
                        SELECT filename, is_visible, is_downloadable FROM hwpj WHERE chapter_id = ?
                    ''', (chapter_id,))
                    submissions = cursor.fetchall()
                    if get_user_role(username) == 'student':
                        submissions = [file for file in submissions if file[1] == 1]
                    self.write(json.dumps(submissions))
                else:
                    self.set_status(403)
                    self.write("Forbidden: You do not have permission to access the submissions of this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def delete(self):
        """
        Deletes the submission of the chapter.

        Note:
        - Only the owner of the course can delete submissions.

        Required arguments:
        - chapter_id: The id of the chapter.
        - filename: The filename of the submission.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        filename = self.get_argument("filename")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    DELETE FROM hwpj WHERE chapter_id = ? AND filename = ?
                ''', (chapter_id, filename))
                file_path = f'files/hwpj/{filename}'
                if os.path.exists(file_path):
                    os.remove(file_path)
                conn.commit()
                self.write("Submission deleted successfully.")
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to delete submissions from this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def put(self):
        """
        Updates the visibility or downloadability of the submission of the chapter.

        Note:
        - Only the owner of the course can update the visibility or downloadability of submissions.

        Required arguments:
        - chapter_id: The id of the chapter.
        - filename: The filename of the submission.
        - is_visible: The visibility status of the submission.
        - is_downloadable: The downloadability status of the submission.

        Returns:
        - The updated visibility status of the submission.
        - The updated downloadability status of the submission.
        """
        username = self.get_current_user()
        chapter_id = self.get_argument("chapter_id")
        filename = self.get_argument("filename")
        is_visible = self.get_argument("is_visible")
        is_downloadable = self.get_argument("is_downloadable")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT owner FROM courses c
                JOIN chapters ch ON c.id = ch.course_id
                WHERE ch.id = ?
            ''', (chapter_id,))
            owner = cursor.fetchone()
            if owner and owner[0] == username:
                cursor.execute('''
                    UPDATE hwpj SET is_visible = ?, is_downloadable = ? WHERE chapter_id = ? AND filename = ?
                ''', (is_visible, is_downloadable, chapter_id, filename))
                conn.commit()
                self.write({"is_visible": is_visible, "is_downloadable": is_downloadable})
            else:
                self.set_status(403)
                self.write("Forbidden: You do not have permission to update the visibility of submissions in this chapter.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()