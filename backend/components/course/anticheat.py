import time
import tornado.web

class VideoAnticheatHandler(tornado.web.RequestHandler):
    """
    Handles video anti-cheat functionalities.
    """
    users_watch_time = {}

    @tornado.web.authenticated
    def post(self):
        username = self.get_current_user()
        data = tornado.escape.json_decode(self.request.body)
        watch_time = data.get('watch_time')

        if username in self.users_watch_time and self.users_watch_time[username]['active']:
            self.write({"violation": True})
            return

        self.users_watch_time[username] = {
            'watch_time': watch_time,
            'last_active': time.time(),
            'active': True
        }

        # Check if the user is "cheating" by being inactive or playing more than one video
        if watch_time >= 300:  # After 5 minutes of watching
            last_active = self.users_watch_time[username]['last_active']
            if time.time() - last_active > 60:  # Assume user inactive if no activity for 60 seconds
                self.write({"violation": True})
            else:
                self.write({"violation": False})
        else:
            self.write({"violation": False})

    @staticmethod
    def check_inactivity():
        """
        Periodic check for user inactivity. This can be run as a background task.
        """
        current_time = time.time()
        for user_id, data in VideoAnticheatHandler.users_watch_time.items():
            if data['active'] and current_time - data['last_active'] > 60:
                data['active'] = False