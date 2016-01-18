import json
import unittest
from flask import url_for
from app import create_app, db
from app.admin.models import Role, User
from app.seanses.models import Genre, Film
from tests.base_test_classes import BaseAuthedViewTestCase


class GenresEndpointTestCase(BaseAuthedViewTestCase):

    def test_401_to_anon(self):
        response = self.client.get(url_for('seanses.genres_list'))
        self.assertEqual(response.status_code, 401)

    def test_403_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.get(url_for('seanses.genres_list'), headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_returns_data_to_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        test_genre = Genre(name='test_genre')
        db.session.add_all([admin_user, test_genre])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.get(url_for('seanses.genres_list'), headers=headers)
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(body[0]['name'], 'test_genre')

    def test_401_to_anon_on_post(self):
        response = self.client.post(
            url_for('seanses.genres_list'),
            data=json.dumps(dict(name='test_genre')),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 401)

    def test_403_if_no_perms_on_post(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.post(
            url_for('seanses.genres_list'),
            data=json.dumps(dict(name='test_genre')),
            headers=headers
        )
        genre = Genre.query.filter_by(name='test_genre').first()
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(genre)

    def test_creats_genre_on_post_if_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.post(
            url_for('seanses.genres_list'),
            data=json.dumps(dict(name='test_genre')),
            headers=headers
        )
        genre = Genre.query.filter_by(name='test_genre').first()
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(genre)
        self.assertEqual(genre.name, 'test_genre')

    def test_401_to_anon_on_put(self):
        test_genre = Genre(name='test_genre')
        db.session.add(test_genre)
        db.session.commit()
        response = self.client.put(
            url_for('seanses.genres_detail', pk=test_genre.id),
            data=json.dumps(dict(name='new_name'))
        )
        self.assertEqual(response.status_code, 401)

    def test_403_if_no_perms_on_put(self):
        test_genre = Genre(name='test_genre')
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add_all([test_genre, no_perms_role, no_perms_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.put(
            url_for('seanses.genres_detail', pk=test_genre.id),
            data=json.dumps(dict(name='new_name')),
            headers=headers
        )
        genre = Genre.query.get(test_genre.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(genre.name, 'test_genre')

    def test_updates_genre_if_admin_on_put(self):
        test_genre = Genre(name='test_genre')
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add_all([test_genre, admin_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.put(
            url_for('seanses.genres_detail', pk=test_genre.id),
            data=json.dumps(dict(name='new_name')),
            headers=headers
        )
        genre = Genre.query.get(test_genre.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(genre.name, 'new_name')

    def test_401_to_anon_on_delete(self):
        test_genre = Genre(name='test_genre')
        db.session.add(test_genre)
        db.session.commit()
        response = self.client.delete(
            url_for('seanses.genres_detail', pk=test_genre.id)
        )
        genre = Genre.query.filter_by(name=test_genre.name).first()
        self.assertEqual(response.status_code, 401)
        self.assertIsNotNone(genre)

    def test_403_if_no_perms_on_delete(self):
        test_genre = Genre(name='test_genre')
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add_all([test_genre, no_perms_role, no_perms_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.delete(
            url_for('seanses.genres_detail', pk=test_genre.id),
            headers=headers
        )
        genre = Genre.query.filter_by(name=test_genre.name).first()
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(genre)

    def test_deletes_genre_on_delete_if_admin(self):
        test_genre = Genre(name='test_genre')
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add_all([test_genre, admin_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.delete(
            url_for('seanses.genres_detail', pk=test_genre.id),
            headers=headers
        )
        genre = Genre.query.filter_by(name=test_genre.name).first()
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(genre)


class FilmsEndpointTestCase(BaseAuthedViewTestCase):

    def test_401_to_anon(self):
        response = self.client.get(url_for('seanses.films_list'))
        self.assertEqual(response.status_code, 401)

    def test_403_if_no_perms(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.get(url_for('seanses.films_list'), headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_returns_data_to_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        test_film = Film(name='test_film')
        db.session.add_all([admin_user, test_film])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.get(url_for('seanses.films_list'), headers=headers)
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.get_data(as_text=True))
        self.assertEqual(body[0]['name'], 'test_film')

    def test_401_to_anon_on_post(self):
        response = self.client.post(
            url_for('seanses.films_list'),
            data=json.dumps(dict(name='test_film')),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 401)

    def test_403_if_no_perms_on_post(self):
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add(no_perms_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.post(
            url_for('seanses.films_list'),
            data=json.dumps(dict(name='test_film')),
            headers=headers
        )
        film = Film.query.filter_by(name='test_film').first()
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(film)

    def test_creats_film_on_post_if_admin(self):
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add(admin_user)
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.post(
            url_for('seanses.films_list'),
            data=json.dumps(dict(name='test_film')),
            headers=headers
        )
        film = Film.query.filter_by(name='test_film').first()
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(film)
        self.assertEqual(film.name, 'test_film')

    def test_401_to_anon_on_put(self):
        test_film = Film(name='test_film')
        db.session.add(test_film)
        db.session.commit()
        response = self.client.put(
            url_for('seanses.films_detail', pk=test_film.id),
            data=json.dumps(dict(name='new_name'))
        )
        self.assertEqual(response.status_code, 401)

    def test_403_if_no_perms_on_put(self):
        test_film = Film(name='test_film')
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add_all([test_film, no_perms_role, no_perms_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.put(
            url_for('seanses.films_detail', pk=test_film.id),
            data=json.dumps(dict(name='new_name')),
            headers=headers
        )
        film = Film.query.get(test_film.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(film.name, 'test_film')

    def test_updates_film_if_admin_on_put(self):
        test_film = Film(name='test_film')
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add_all([test_film, admin_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.put(
            url_for('seanses.films_detail', pk=test_film.id),
            data=json.dumps(dict(name='new_name')),
            headers=headers
        )
        film = Film.query.get(test_film.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(film.name, 'new_name')

    def test_401_to_anon_on_delete(self):
        test_film = Film(name='test_film')
        db.session.add(test_film)
        db.session.commit()
        response = self.client.delete(
            url_for('seanses.films_detail', pk=test_film.id)
        )
        film = Film.query.filter_by(name=test_film.name).first()
        self.assertEqual(response.status_code, 401)
        self.assertIsNotNone(film)

    def test_403_if_no_perms_on_delete(self):
        test_film = Film(name='test_film')
        no_perms_role = Role.query.filter_by(name='NO_PERMS_USER').first()
        no_perms_user = User(email='apatr@to.by', password='hhhooo', role=no_perms_role)
        db.session.add_all([test_film, no_perms_role, no_perms_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='apatr@to.by', password='hhhooo'))
        response = self.client.delete(
            url_for('seanses.films_detail', pk=test_film.id),
            headers=headers
        )
        film = Film.query.filter_by(name=test_film.name).first()
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(film)

    def test_deletes_film_on_delete_if_admin(self):
        test_film = Film(name='test_film')
        admin_role = Role.query.filter_by(name='ADMIN').first()
        admin_user = User(email='admin@ru.dot', password='sayhi', role=admin_role)
        db.session.add_all([test_film, admin_user])
        db.session.commit()
        headers = self.get_authed_headers(dict(email='admin@ru.dot', password='sayhi'))
        response = self.client.delete(
            url_for('seanses.films_detail', pk=test_film.id),
            headers=headers
        )
        film = Film.query.filter_by(name=test_film.name).first()
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(film)
