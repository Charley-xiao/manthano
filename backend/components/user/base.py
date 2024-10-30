import tornado.web
from database import get_user_role

active_sessions = {}

class BaseHandler(tornado.web.RequestHandler):
    def get_login_url(self) -> str:
        return "/login"

    def get_current_user(self):
        session_id = self.get_secure_cookie("session_id")
        username = self.get_secure_cookie("user")

        if not session_id or not username:
            return None

        if active_sessions.get(username.decode('utf-8')) == session_id.decode('utf-8'):
            return username.decode('utf-8')
        return None

    def get_user_role(self):
        username = self.get_current_user()
        if username:
            role = get_user_role(username)
            return role
        return None

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.set_header("Access-Control-Allow-Credentials", "true")