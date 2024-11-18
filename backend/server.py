"""
Basic Requirement (75%):
Support three permissions of system administrator, course teacher and student.
Course creation must be applied for by the course teacher and approved by the system administrator.
The course function needs to include the following specific contents:
The course contains different chapters, and the courseware function can be realized for different chapters. Chapters can be categorized: teaching, homework, and project
Teachers can add some students to the course.
It can be divided into open courses, non-open courses, and semi-open course (open part of the chapter).
Students can join open courses.
Teachers can send email notifications to students who join the course.
Students can give the lesson they have joined a like.

The functions of the chapter include the following specific contents:
Upload courseware module: Teachers can upload courseware for chapters, and the files support at least MD and PDF formats
Update the courseware module: Teachers can choose to keep the original courseware, and each version of the courseware is marked with a version number
Download courseware module: Teachers can set whether the current courseware is downloadable or not.
Video module: Course teachers can upload videos corresponding to chapters, and users can watch them online
Comment module: A comment area is reserved for each courseware for user comments and teacher Q&A
Attachment module: Teachers can upload attachments corresponding to this chapter, such as data, code, etc. Downloadable for students.
Teaching evaluation function: Students can evaluate the course. Feedback scores and reviews.


Advanced Requirement (25%)
Popular courses and popular teachers list.
Add homework module and courseware viewing progress module.
Implement video anti-cheat function,
If you have to see it for a certain amount of time;
Only one video can be played at a time;
When the viewing time reaches a certain time, detect whether the user hangs up;
End-of-course requests cannot be invoked directly;
Single-user login only, etc.
Live broadcast room of the course.
Set specific indicators for teaching evaluation: such as the reasonableness of homework, the teacher's teaching ability, the difficulty of the test, etc.
Pretty UI.
"""

from database import DATABASE, validate_user, add_user, get_user_role, get_users_by_role, User, add_teacher_request
from database import init_db
import argparse
import json
# from recommender import recommend_courses_with_content
from functools import wraps

def verified(cls):
    """Class decorator to mark a class as verified."""
    cls._is_verified = True
    original_methods = {name: method for name, method in cls.__dict__.items() if callable(method)}
    for name, method in original_methods.items():
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not getattr(self, '_is_verified', False):
                print(f'Warning: {self.__class__.__name__} is not verified.')
            return method(self, *args, **kwargs)
        setattr(cls, name, wrapper)
    return cls

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=9265)
args = parser.parse_args()

import tornado
import tornado.ioloop
import tornado.web

init_db()

from components.sendEmail import config
from components.inbox import InboxHandler
from components.user.base import BaseHandler
from components.user.login import LoginHandler, LogoutHandler, RegisterHandler
from components.user.teacher import AddTeacherHandler
from components.user.mycourse import MyCourseHandler, AddCourseRequestHandler, AddTeacherRequestHandler
from components.course.anticheat import VideoAnticheatHandler
from components.course.courseware import CourseWareHandler, CourseWareFileHandlerWithAuth
from components.course.mainCourse import AllCoursesHandler, DetailedCourseHandler, AddCourseHandler, CourseProgressHandler
from components.course.derived import CourseCommentsHandler, CourseNotifHandler, CourseLikeHandler, CourseRecommendHandler, EvaluationHandler
from components.post.post import PostHandler, CommentHandler

class MainHandler(BaseHandler):
    def get(self):
        """
        Returns username and role of the current user in JSON format.
        """
        username = self.get_current_user()
        role = get_user_role(username)
        self.write(json.dumps({"username": username, "role": role}))


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        role = self.get_user_role()
        if role == 'admin':
            self.write("Welcome, Admin! You have access to this page.")
        else:
            self.set_status(403)
            self.write("Forbidden: You do not have permission to access this page.")


SECRET_KEY = config['secret']

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/register", RegisterHandler),
        (r"/admin", AdminHandler),
        (r"/logout", LogoutHandler),
        (r"/inbox", InboxHandler),
        (r"/courses/\d+/comments", CourseCommentsHandler),
        (r"/my/course", MyCourseHandler),
        (r"/add/teacher", AddTeacherHandler),
        (r"/add/course", AddCourseHandler),
        (r"/courses/\d+", DetailedCourseHandler),
        (r"/courses/notif", CourseNotifHandler),
        (r"/courses/like", CourseLikeHandler),
        (r"/courses/recommend", CourseRecommendHandler),
        (r"/anticheat", VideoAnticheatHandler),
        (r"/courseware", CourseWareHandler),
        (r"/files/courseware/(.*)", CourseWareFileHandlerWithAuth, {"path": "files/courseware"}),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        (r"/course/all", AllCoursesHandler),
        (r"/evaluation", EvaluationHandler),
        (r"/course/progress/\d+", CourseProgressHandler),
        (r"/posts", PostHandler),
        (r"/posts/(\d+)/comments", CommentHandler),
        (r"/add-course-requests", AddCourseRequestHandler),
        (r"/add-teacher-requests", AddTeacherRequestHandler),
    ], cookie_secret=SECRET_KEY, login_url="/login")

if __name__ == "__main__":
    app = make_app()
    app.listen(args.port)
    print(f"Server started at http://localhost:{args.port}")
    # tornado.ioloop.PeriodicCallback(VideoAnticheatHandler.check_inactivity, 60000).start()
    tornado.ioloop.IOLoop.current().start()

