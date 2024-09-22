import tornado.gen
from tornado.testing import AsyncTestCase, gen_test
from tornado.httpclient import AsyncHTTPClient
from server import make_app

class TestServer(AsyncTestCase):
    def setUp(self):
        super(TestServer, self).setUp()
        self.http_client = AsyncHTTPClient(self.io_loop)
        self.app = make_app()

    @gen_test
    def test_homepage(self):
        response = yield self.http_client.fetch(
            self.get_url('/'),
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        self.assertIn('Hello, world!', response.body.decode())

    @gen_test
    def test_login(self):
        response = yield self.http_client.fetch(
            self.get_url('/login'),
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        self.assertIn('Login', response.body.decode())

    @gen_test
    def test_login_post(self):
        response = yield self.http_client.fetch(
            self.get_url('/login'),
            method='POST',
            body='username=admin&password=admin',
            raise_error=False
        )
        self.assertEqual(response.code, 200)
        self.assertIn('Login failed', response.body.decode())