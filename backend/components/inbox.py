import json
import sqlite3
import time
import tornado.web
from components.user.base import BaseHandler
from database import DATABASE

class InboxHandler(BaseHandler):
    """
    Handles the inbox of students, teachers, and admins.
    """
    @tornado.web.authenticated
    def get(self):
        """
        With no parameters, returns all the messages of the inbox of the user. Sorted based on factors `priority` and `timestamp`.

        With the parameter `id`, returns the message with the given id.

        With the parameter `type`, returns all the messages of the inbox of the user with the given type.

        With the parameter `sender`, returns all the messages of the inbox of the user with the given sender.

        With the parameter `priority`, returns all the messages of the inbox of the user with the given priority.

        With the parameter `read`, returns all the messages of the inbox of the user with the given read status.

        With the parameter `limit`, returns the first `limit` messages of the inbox of the user.

        With the parameter `offset`, returns the messages of the inbox of the user starting from the `offset` index.
        """
        username = self.get_current_user()
        message_id = self.get_argument("id", None)
        message_type = self.get_argument("type", None)
        sender = self.get_argument("sender", None)
        priority = self.get_argument("priority", None)
        read = self.get_argument("read", None)
        limit = self.get_argument("limit", None)
        offset = self.get_argument("offset", None)

        try:
            limit = int(limit) if limit else None
            offset = int(offset) if offset else None
        except ValueError:
            self.set_status(400)
            self.write("Invalid limit or offset value.")
            return

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            if message_id:
                cursor.execute('''
                    SELECT sender, receiver, subject, body, timestamp, read, type, priority
                    FROM messages
                    WHERE id = ? AND receiver = ?
                ''', (message_id, username))
                result = cursor.fetchone()
                if result:
                    self.write(json.dumps(result))
                else:
                    self.set_status(404)
                    self.write("Message not found.")
            else:
                query = '''
                    SELECT sender, receiver, subject, body, timestamp, read, type, priority
                    FROM messages
                    WHERE receiver = ?
                '''
                params = [username]

                if message_type:
                    query += ' AND type = ?'
                    params.append(message_type)
                if sender:
                    query += ' AND sender = ?'
                    params.append(sender)
                if priority:
                    try:
                        priority = int(priority)
                        query += ' AND priority = ?'
                        params.append(priority)
                    except ValueError:
                        self.set_status(400)
                        self.write("Invalid priority value.")
                        return
                if read:
                    try:
                        read = int(read)
                        query += ' AND read = ?'
                        params.append(read)
                    except ValueError:
                        self.set_status(400)
                        self.write("Invalid read value.")
                        return

                query += ' ORDER BY priority DESC, timestamp DESC'

                if limit:
                    query += ' LIMIT ?'
                    params.append(limit)
                if offset:
                    query += ' OFFSET ?'
                    params.append(offset)

                cursor.execute(query, params)
                result = cursor.fetchall()
                self.write(json.dumps(result))

        except sqlite3.Error as e:
            self.set_status(500)
            self.write(f"Database error: {str(e)}")
        finally:
            conn.close()

    @tornado.web.authenticated
    def post(self):
        """
        Sends a message to the user's inbox.

        Required arguments:
        - receiver: The username of the receiver.
        - subject: The subject of the message.
        - body: The body of the message.

        Optional arguments:
        - priority: The priority of the message. Default is 0.
        - type: The type of the message. Default is 'message'.

        Auto-generated arguments:
        - sender: The username of the sender.
        - timestamp: The current timestamp.
        - read: The read status of the message. Default is 0.
        """
        sender = self.get_current_user()
        receiver = self.get_argument("receiver")
        subject = self.get_argument("subject")
        body = self.get_argument("body")
        priority = self.get_argument("priority", 0)
        message_type = self.get_argument("type", 'message')
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO messages (sender, receiver, subject, body, timestamp, priority, type) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (sender, receiver, subject, body, timestamp, priority, message_type))
            conn.commit()
            self.write("Message sent successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()

    @tornado.web.authenticated
    def put(self):
        """
        Updates the read status of a message in the user's inbox.
        """
        message_id = self.get_argument("id")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE messages SET read = 1 WHERE id = ?
            ''', (message_id,))
            conn.commit()
            self.write("Message read status updated successfully.")
        except sqlite3.Error as e:
            self.set_status(500)
            self.write(str(e))
        finally:
            conn.close()