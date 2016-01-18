import logging
from flask import request, jsonify, g
from flask.ext.restful import Resource
from .. import db
from ..decorators import auth_required, permission_required
from ..exceptions import BadRequest, Forbidden, NotFound
from .forms import LoginForm, RegistrationForm, UserUpdateForm, RoleCreationForm
from .models import Role, Permissions, User


def login():
    data = request.get_json()
    form = LoginForm(data)
    form.validate()
    token = User.generate_auth_token(**form.to_native())
    user = User.query.filter_by(email=form.email).first()
    data = user.to_native()
    data['auth_token'] = token
    return jsonify(data), 200


def register():
    data = request.get_json()
    form = RegistrationForm(data)
    form.validate()
    new_user = User(**form.to_native())
    db.session.add(new_user)
    db.session.commit()
    data = new_user.to_native()
    token = User.generate_auth_token(email=form.email, password=form.password)
    data['auth_token'] = token
    return jsonify(data), 201


class UsersListEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_OWN_ACCOUNT_INFO)
    def get(self):
        u = g.current_user
        if not u.check_permission(Permissions.GET_EVERY_ACCOUNT_INFO):
            # if the user wants to get all users' data we should check
            # whether he has according permission
            raise Forbidden('You are not allowed to fetch all users\' data')
        users = User.query.all()
        return [user.to_native(u) for user in users]


class UsersDetailEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_OWN_ACCOUNT_INFO)
    def get(self, pk):
        u = g.current_user
        if pk != u.id and not u.check_permission(Permissions.GET_EVERY_ACCOUNT_INFO):
            # if user tries to fetch someone's account we should check
            # whether he has according permission
            raise Forbidden('You are not allowed to fetch all users\' data.')
        # here the user is fetching its own account data
        user = User.query.get(pk)
        if user is None:
            raise NotFound('No such user')
        return user.to_native(u)

    @auth_required
    @permission_required(Permissions.UPDATE_OWN_ACCOUNT)
    def put(self, pk):
        current_user = g.current_user
        if pk != current_user.id and not \
                current_user.check_permission(Permissions.UPDATE_EVERY_ACCOUNT):
            raise Forbidden('You are not allowed to update this user.')
        data = request.get_json()
        form = UserUpdateForm(data)
        form.validate(partial=True)
        if pk == current_user.id:
            user_to_update = current_user
        else:
            user_to_update = User.query.get(pk)
        user_to_update.update_from_form_data(form.to_native(), current_user)
        db.session.add(user_to_update)
        db.session.commit()
        return user_to_update.to_native(current_user)

    @auth_required
    @permission_required(Permissions.DELETE_OWN_ACCOUNT)
    def delete(self, pk):
        current_user = g.current_user
        if pk != current_user.id and not \
                current_user.check_permission(Permissions.DELETE_EVERY_ACCOUNT):
            raise Forbidden('You are not allowed to delete this user.')
        user = User.query.get(pk)
        if user is None:
            raise NotFound('There is no such a user.')
        db.session.delete(user)
        db.session.commit()
        return {}, 204


class RolesListEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_ROLES)
    def get(self):
        roles = Role.query.all()
        return [role.to_native() for role in roles], 200

    @auth_required
    @permission_required(Permissions.CREATE_NEW_ROLE)
    def post(self):
        data = request.get_json()
        form = RoleCreationForm(data)
        form.validate()
        data = form.to_native()
        role = Role(**data)
        db.session.add(role)
        db.session.commit()
        return role.to_native(), 201


class RolesDetailEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_ROLES)
    def get(self, pk):
        role = Role.query.get(pk)
        if role is None:
            raise NotFound('There is no such role')
        return role.to_native(), 200

    @auth_required
    @permission_required(Permissions.UPDATE_ROLE)
    def put(self, pk):
        role = Role.query.get(pk)
        if role is None:
            raise NotFound('There is no such role')
        data = request.get_json()
        form = RoleCreationForm(data)
        form.validate(partial=True)
        role.update_from_form_data(form.to_native())
        return role.to_native(), 200

    @auth_required
    @permission_required(Permissions.DELETE_ROLE)
    def delete(self, pk):
        role = Role.query.get(pk)
        if role is None:
            raise NotFound('There is no such role')
        db.session.delete(role)
        db.session.commit()
        return {}, 204


class PermissionsEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_PERMISSIONS)
    def get(self):
        return Permissions.to_native(), 200
