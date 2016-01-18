import json
from flask import request
from flask.ext.restful import Resource
from .. import db
from ..exceptions import NotFound
from ..decorators import auth_required, permission_required
from app.admin.models import Permissions
from .models import Genre, Film
from .forms import GenreForm, FilmForm


class GenresListEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_GENRES)
    def get(self):
        result = [genre.to_native() for genre in Genre.query.all()]
        return result, 200

    @auth_required
    @permission_required(Permissions.CREATE_GENRE)
    def post(self):
        data = request.get_json()
        form = GenreForm(data)
        form.validate()
        genre = Genre(**form.to_native())
        db.session.add(genre)
        db.session.commit()
        return genre.to_native(), 201


class GenresDetailEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_GENRES)
    def get(self, pk):
        genre = Genre.query.get(pk)
        if genre is None:
            raise NotFound('There is no such genre.')
        result = genre.to_native()
        return result, 200

    @auth_required
    @permission_required(Permissions.UPDATE_GENRE)
    def put(self, pk):
        genre = Genre.query.get(pk)
        if genre is None:
            raise NotFound('There is no such a genre.')
        data = request.get_json()
        form = GenreForm(data)
        form.validate()
        genre.update_from_form_data(form.to_native())
        db.session.add(genre)
        db.session.commit()
        db.session.refresh(genre)
        return genre.to_native(), 200

    @auth_required
    @permission_required(Permissions.DELETE_GENRE)
    def delete(self, pk):
        genre = Genre.query.get(pk)
        if genre is None:
            raise NotFound('There is no such a genre.')
        db.session.delete(genre)
        db.session.commit()
        return {}, 204


class FilmsListEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_FILMS)
    def get(self):
        result = [film.to_native() for film in Film.query.all()]
        return result, 200

    @auth_required
    @permission_required(Permissions.CREATE_FILM)
    def post(self):
        genres = None
        data = request.get_json()
        form = FilmForm(data)
        form.validate()
        data = form.to_native()
        if data.get('genres'):
            genres = data.pop('genres')
        film = Film(**data)
        if genres:
            for genre in genres:
                film.genres.append(genre)
        db.session.add(film)
        db.session.commit()
        return film.to_native(), 201


class FilmsDetailEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_FILMS)
    def get(self, pk):
        film = Film.query.get(pk)
        if film is None:
            raise NotFound('No such a film.')
        return film.to_native(), 200

    @auth_required
    @permission_required(Permissions.UPDATE_FILM)
    def put(self, pk):
        film = Film.query.get(pk)
        if film is None:
            raise NotFound('No such a film.')
        data = request.get_json()
        form = FilmForm(data)
        form.validate(partial=True)
        data = form.to_native()
        if data.get('genres'):
            genres = data.pop('genres')
            film.genres = []
            for genre in genres:
                film.genres.append(genre)
        film.update_from_form_data(data)
        db.session.add(film)
        db.session.commit()
        db.session.refresh(film)
        return film.to_native(), 200


    @auth_required
    @permission_required(Permissions.DELETE_FILM)
    def delete(self, pk):
        film = Film.query.get(pk)
        if film is None:
            raise NotFound('No such a film.')
        db.session.delete(film)
        db.session.commit()
        return {}, 204
