import json
import unittest
from flask import url_for
from app import create_app, db
from app.admin.models import Role


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class BaseViewTestCase(BaseTestCase):

    def setUp(self):
        super(BaseViewTestCase, self).setUp()
        self.client = self.app.test_client()


class BaseAuthedViewTestCase(BaseViewTestCase):

    def setUp(self):
        super(BaseAuthedViewTestCase, self).setUp()
        Role.insert_roles()

    def get_authed_headers(self, token_user_data):
        data = json.dumps(dict(
            email=token_user_data['email'],
            password=token_user_data['password']
        ))
        response = self.client.post(
            url_for('admin.login'),
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        token = json.loads(response.get_data(as_text=True))['auth_token']
        return {
            'Content-Type': 'application/json',
            'Auth-Cinemago-Token': token
        }
