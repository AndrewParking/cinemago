import unittest
from schematics.exceptions import ValidationError
from app import create_app, db
from app.admin.models import Permissions, Role
from app.admin.forms import RoleCreationForm


class RoleCreationTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        db.session.commit()

    def test_validates_default(self):
        form = RoleCreationForm(dict(
            name='TEST_ROLE',
            permissions=[
                Permissions.GET_ROLES.value,
                Permissions.CREATE_NEW_ROLE.value
            ],
            default=True
        ))
        with self.assertRaises(ValidationError):
            form.validate()

    def test_converts_permissions(self):
        form = RoleCreationForm(dict(
            name='TEST_ROLE',
            permissions=[
                Permissions.GET_ROLES.value,
                Permissions.CREATE_NEW_ROLE.value
            ],
            default=False
        ))
        form.validate()
        self.assertEqual(form.to_native()['permissions'], (
            Permissions.GET_ROLES.value | Permissions.CREATE_NEW_ROLE.value
        ))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
