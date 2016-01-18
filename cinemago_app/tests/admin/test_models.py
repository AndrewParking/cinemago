import unittest
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.admin.models import User, Role
from app.exceptions import BadRequest, NotFound


class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(email='pop@tut.by', password='homm1994')
        db.session.add(self.user)
        db.session.commit()

    def test_password_getter(self):
        with self.assertRaises(AttributeError):
            self.user.password

    def test_password_setter(self):
        self.assertTrue(self.user.password_hash)

    def test_password_verification(self):
        self.assertTrue(self.user.verify_password('homm1994'))
        self.assertFalse(self.user.verify_password('homm1995'))

    def test_auth_token_generation(self):
        wrong_email_data = dict(email='pip@gmai.com', password='homm1994')
        wrong_pass_data = dict(email='pop@tut.by', password='homm1995')
        correct_data = dict(email='pop@tut.by', password='homm1994')
        with self.assertRaises(NotFound):
            User.generate_auth_token(**wrong_email_data)
        with self.assertRaises(BadRequest):
            User.generate_auth_token(**wrong_pass_data)
        self.assertTrue(User.generate_auth_token(**correct_data))

    def test_verify_auth_token(self):
        correct_data = dict(email='pop@tut.by', password='homm1994')
        token = User.generate_auth_token(**correct_data)
        self.assertEqual(self.user, User.verify_auth_token(token))
        with self.assertRaises(BadSignature):
            User.verify_auth_token(token[:-5])

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class RoleModelTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def test_updates_from_form(self):
        test_role = Role(name='TEST_ROLE', permissions=0x111, default=False)
        db.session.add(test_role)
        db.session.commit()
        test_role.update_from_form_data({
            'name': 'NEW_NAME',
            'permissions': 0x222
        })
        self.assertEqual(test_role.name, 'NEW_NAME')
        self.assertEqual(test_role.permissions, 0x222)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
