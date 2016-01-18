import json
import unittest
from flask import url_for
from app import create_app, db
from app.admin.models import User, Role, Permissions
from tests.base_test_classes import BaseViewTestCase, BaseAuthedViewTestCase


class RegistrationTest(BaseViewTestCase):

    def setUp(self):
        super(RegistrationTest, self).setUp()
        self.headers = {
            'Content-Type': 'application/json'
        }

    def test_register_user(self):
        data = dict(email='pop@tut.by', password='homm1994', first_name='homie')
        response = self.client.post(
            url_for('admin.register'),
            data=json.dumps(data),
            headers=self.headers,
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(body['email'], 'pop@tut.by')
        self.assertEqual(body['first_name'], 'homie')
        self.assertTrue(body.get('auth_token'))

    def test_400_on_bad_data(self):
        data = dict(email='ppp')
        response = self.client.post(
            url_for('admin.register'),
            data=json.dumps(data),
            headers=self.headers,
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(body.get('messages'))

    def test_400_on_taken_email(self):
        data = dict(email='pop@tut.by', password='homm1994')
        u = User(**data)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(
            url_for('admin.register'),
            data=json.dumps(data),
            headers=self.headers,
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertTrue(body.get('messages'))



class LoginTest(BaseViewTestCase):

    def setUp(self):
        super(LoginTest, self).setUp()
        self.headers = {
            'Content-Type': 'application/json',
        }
        u = User(email='pop@tut.by', password='homm1994')
        db.session.add(u)
        db.session.commit()

    def test_returns_token(self):
        data = dict(email='pop@tut.by', password='homm1994')
        response = self.client.post(
            url_for('admin.login'),
            data=json.dumps(data),
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.get_data(as_text=True))
        self.assertTrue(body.get('auth_token'))

    def test_400_on_bad_data(self):
        data = dict(email='p', password='homm')
        response = self.client.post(
            url_for('admin.login'),
            data=json.dumps(data),
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.get_data(as_text=True))
        self.assertTrue(body.get('messages'))


class UserEndpointTest(BaseAuthedViewTestCase):

    def fetch_with_auth_token(self, token_user_data, data_user_id):
        headers = self.get_authed_headers(token_user_data)
        response = self.client.get(
            url_for('admin.users_detail', pk=data_user_id),
            headers=headers
        )
        return response

    def fetch_list_with_auth_token(self, token_user_data):
        headers = self.get_authed_headers(token_user_data)
        response = self.client.get(
            url_for('admin.users_list'),
            headers=headers
        )
        return response

    def put_with_auth_token(self, token_user_data, data_user_id, data):
        headers = self.get_authed_headers(token_user_data)
        response = self.client.put(
            url_for('admin.users_detail', pk=data_user_id),
            data=json.dumps(data),
            headers=headers,
        )
        return response

    def delete_with_auth_token(self, token_user_data, data_user_id):
        headers = self.get_authed_headers(token_user_data)
        response = self.client.delete(
            url_for('admin.users_detail', pk=data_user_id),
            headers=headers,
        )
        return response

    def test_403_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user)
        db.session.commit()
        response = self.fetch_with_auth_token(
            token_user_data=dict(email='apatr@to.by', password='hhhooo'),
            data_user_id=no_perms_user.id
        )
        self.assertEqual(response.status_code, 403)

    def test_returns_own_data(self):
        base_user = User(email='pop@tut.by', password='homm1994')
        db.session.add(base_user)
        db.session.commit()
        response = self.fetch_with_auth_token(
            token_user_data=dict(email='pop@tut.by', password='homm1994'),
            data_user_id=base_user.id
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['email'], 'pop@tut.by')

    def test_returns_foreign_data_to_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        base_user = User(email='pop@tut.by', password='homm1994')
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(base_user, admin_user)
        db.session.commit()
        response = self.fetch_with_auth_token(
            token_user_data=dict(email='admin@ru.dot', password='sayhi'),
            data_user_id=base_user.id
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['email'], 'pop@tut.by')

    def test_returns_all_to_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        response = self.fetch_list_with_auth_token(
            token_user_data=dict(email='admin@ru.dot', password='sayhi')
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body), 1)

    def test_403_on_all_to_base(self):
        base_user = User(email='pop@tut.by', password='homm1994')
        db.session.add(base_user)
        db.session.commit()
        response = self.fetch_list_with_auth_token(
            token_user_data=dict(email='pop@tut.by', password='homm1994')
        )
        self.assertEqual(response.status_code, 403)

    def test_403_on_put_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user)
        db.session.commit()
        response = self.put_with_auth_token(
            token_user_data=dict(email='apatr@to.by', password='hhhooo'),
            data_user_id=no_perms_user.id,
            data=dict(first_name='test', last_name='testing')
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(no_perms_user.first_name)
        self.assertFalse(no_perms_user.last_name)

    def test_updates_own_data(self):
        base_user = User(email='pop@tut.by', password='homm1994')
        db.session.add(base_user)
        db.session.commit()
        response = self.put_with_auth_token(
            token_user_data=dict(email='pop@tut.by', password='homm1994'),
            data_user_id=base_user.id,
            data=dict(first_name='test', last_name='testing')
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(base_user.first_name, 'test')
        self.assertEqual(base_user.last_name, 'testing')

    def test_admin_updates_foreign_account(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        base_user = User(email='pop@tut.by', password='homm1994')
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add_all([admin_role, base_user, admin_user])
        db.session.commit()
        response = self.put_with_auth_token(
            token_user_data=dict(
                email='admin@ru.dot',
                password='sayhi'
            ),
            data_user_id=base_user.id,
            data=dict(
                first_name='test',
                last_name='testing',
                role_id=admin_role.id
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(base_user.first_name, 'test')
        self.assertEqual(base_user.last_name, 'testing')
        self.assertEqual(base_user.role, admin_role)

    def test_403_on_delete_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user)
        db.session.commit()
        response = self.delete_with_auth_token(
            token_user_data=dict(email='apatr@to.by', password='hhhooo'),
            data_user_id=no_perms_user.id
        )
        self.assertEqual(response.status_code, 403)

    def test_delets_own_account(self):
        base_user = User(email='pop@tut.by', password='homm1994')
        db.session.add(base_user)
        db.session.commit()
        response = self.delete_with_auth_token(
            token_user_data=dict(email='pop@tut.by', password='homm1994'),
            data_user_id=base_user.id
        )
        self.assertEqual(response.status_code, 204)
        u = User.query.filter_by(email='pop@tut.by').first()
        self.assertFalse(u)

    def test_admin_deletes_every_user(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        base_user = User(email='pop@tut.by', password='homm1994')
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add_all([admin_role, base_user, admin_user])
        db.session.commit()
        response = self.delete_with_auth_token(
            token_user_data=dict(email='admin@ru.dot', password='sayhi'),
            data_user_id=base_user.id
        )
        self.assertEqual(response.status_code, 204)
        u = User.query.filter_by(email='pop@tut.by').first()
        self.assertFalse(u)



class RolesEndpointTest(BaseAuthedViewTestCase):

    def test_403_on_detail_get_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user, no_perms_role)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.get(
            url_for('admin.roles_detail', pk=no_perms_role.id),
            headers=headers
        )
        self.assertEqual(response.status_code, 403)

    def test_data_on_detail_get_to_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.get(
            url_for('admin.roles_detail', pk=admin_role.id),
            headers=headers
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)

    def test_403_on_list_get_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user, no_perms_role)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.get(
            url_for('admin.roles_list'),
            headers=headers
        )
        self.assertEqual(response.status_code, 403)

    def test_data_on_list_get_to_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.get(
            url_for('admin.roles_list'),
            headers=headers
        )
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)

    def test_403_on_post_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user, no_perms_role)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.post(
            url_for('admin.roles_list'),
            data=dict(
                name='TEST_ROLE',
                permissions=[
                    Permissions.GET_ROLES.value,
                    Permissions.UPDATE_OWN_ACCOUNT.value,
                    Permissions.CREATE_NEW_ROLE.value,
                ],
                default=False
            ),
            headers=headers
        )
        self.assertEqual(response.status_code, 403)
        new_role = Role.query.filter_by(name='TEST_ROLE').first()
        self.assertTrue(new_role is None)

    def test_creates_role_on_admin_post(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.post(
            url_for('admin.roles_list'),
            data=json.dumps(dict(
                name='TEST_ROLE',
                permissions=[
                    Permissions.GET_ROLES.value,
                    Permissions.UPDATE_OWN_ACCOUNT.value,
                    Permissions.CREATE_NEW_ROLE.value,
                ],
                default=False
            )),
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        new_role = Role.query.filter_by(name='TEST_ROLE').first()
        self.assertTrue(new_role is not None)
        self.assertEqual(new_role.name, 'TEST_ROLE')

    def test_403_on_put_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user, no_perms_role)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.put(
            url_for('admin.roles_detail', pk=no_perms_role.id),
            data=json.dumps(dict(name='TEST_ROLE')),
            headers=headers
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(no_perms_role.name, 'NO_PERMS_USER')

    def test_updates_data_on_admin_put(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.put(
            url_for('admin.roles_detail', pk=admin_role.id),
            data=json.dumps(dict(name='TEST_ROLE')),
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(admin_role.name, 'TEST_ROLE')

    def test_403_on_delete_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user, no_perms_role)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.delete(
            url_for('admin.roles_detail', pk=no_perms_role.id),
            headers=headers
        )
        self.assertEqual(response.status_code, 403)
        role = Role.query.filter_by(name='NO_PERMS_USER').first()
        self.assertTrue(role is not None)

    def test_deletes_role_on_admin_delete(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.delete(
            url_for('admin.roles_detail', pk=admin_role.id),
            headers=headers
        )
        self.assertEqual(response.status_code, 204)
        role = Role.query.filter_by(name='ADMIN_ROLE').first()
        self.assertTrue(role is None)


class PermissionsEndpointTest(BaseAuthedViewTestCase):

    def test_403_on_get_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user, no_perms_role)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.get(
            url_for('admin.permissions'),
            headers=headers
        )
        self.assertEqual(response.status_code, 403)

    def test_returns_perms_to_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.get(
            url_for('admin.permissions'),
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
