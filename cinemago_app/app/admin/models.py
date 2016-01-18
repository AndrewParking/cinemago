from enum import Enum
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, jsonify
from .. import db
from ..exceptions import BadRequest, NotFound, Forbidden

# TODO: test User model methods
# TODO: User.to_native() needs current_user parameter, try to fix it


class Permissions(Enum):
    GET_OWN_ACCOUNT_INFO = 0x1
    GET_EVERY_ACCOUNT_INFO = 0x2
    UPDATE_OWN_ACCOUNT = 0x4
    UPDATE_EVERY_ACCOUNT = 0x8
    DELETE_OWN_ACCOUNT = 0x10
    DELETE_EVERY_ACCOUNT = 0x20
    GET_USER_ROLES = 0x40
    CHANGE_USER_ROLE = 0x80
    GET_ROLES = 0x100
    CREATE_NEW_ROLE = 0x200
    UPDATE_ROLE = 0x400
    DELETE_ROLE = 0x800
    GET_PERMISSIONS = 0x1000
    GET_JOBS = 0x2000
    CREATE_JOB = 0x4000
    CANCEL_JOB = 0x8000
    GET_SPIDERS = 0x10000
    GET_GENRES = 0x20000
    CREATE_GENRE = 0x40000
    UPDATE_GENRE = 0x80000
    DELETE_GENRE = 0x100000
    GET_FILMS = 0x200000
    CREATE_FILM = 0x400000
    UPDATE_FILM = 0x800000
    DELETE_FILM = 0x1000000

    @classmethod
    def find_by_value(cls, value):
        return [perm.name for perm in Permissions
                if (perm.value & value) == perm.value]

    @classmethod
    def to_native(cls):
        return {p.name: p.value for p in cls}


class RolePermissions(Enum):
    NO_PERMS_USER = 0x0
    BASE_USER = (
        Permissions.GET_OWN_ACCOUNT_INFO.value |
        Permissions.UPDATE_OWN_ACCOUNT.value |
        Permissions.DELETE_OWN_ACCOUNT.value
    )
    ADMIN = 0xffffffff


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True)
    permissions = db.Column(db.BigInteger, unique=True)
    default = db.Column(db.Boolean, default=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role: {name}>'.format(name=self.name)

    def update_from_form_data(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
        db.session.add(self)
        db.session.commit()

    def to_native(self):
        return dict(
            id=self.id,
            name=self.name,
            permissions=Permissions.find_by_value(self.permissions),
            default=self.default,
            users=[user.to_native() for user in self.users],
        )

    @classmethod
    def insert_roles(cls):
        for r in RolePermissions:
            role = cls.query.filter_by(name=r.name).first()
            if role is None:
                new_role = cls(
                    name=r.name,
                    permissions=r.value,
                    default=(r.name == 'BASE_USER')
                )
                db.session.add(new_role)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    about = db.Column(db.Text)
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_action = db.Column(db.DateTime, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            base_role = Role.query.filter_by(name='BASE_USER').first()
            self.role = base_role

    def __repr__(self):
        return '<User: {email}>'.format(email=self.email)

    def to_native(self, current_user=None):
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'about': self.about,
            'location': self.location,
        }
        if current_user and current_user.check_permission(Permissions.GET_USER_ROLES):
            data['role'] = self.role.name if self.role else None
        return data

    def update_from_form_data(self, data, current_user):
        role_id = None
        if 'role_id' in data:
            role_id = data.pop('role_id')
        for attr, value in data.items():
            setattr(self, attr, value)
        if role_id:
            if current_user.check_permission(Permissions.CHANGE_USER_ROLE):
                role = Role.query.get(role_id)
                self.role = role
                db.session.add(self)
                db.session.commit()
            else:
                raise Forbidden('Permission denied')

    @property
    def password(self):
        raise AttributeError('Password cannot be fetched from db.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def generate_auth_token(cls, email, password):
        user = cls.query.filter_by(email=email).first()
        if user is None:
            raise NotFound('No user with such email')
        if not user.verify_password(password):
            raise BadRequest('Password is invalid')
        s = Serializer(current_app.config['SECRET_KEY'],
            expires_in=current_app.config['AUTH_TOKEN_EXPIRATION_TIME'])
        return s.dumps({'id': user.id}).decode('utf-8')

    @classmethod
    def verify_auth_token(cls, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        user_id = s.loads(token)['id']
        user = cls.query.get(user_id)
        return user

    def check_permission(self, *permissions):
        if len(permissions) == 1:
            perms = permissions[0].value
        else:
            perms = 0x0
            for p in permissions:
                perms = perms | p.value
        if (self.role.permissions & perms) != perms:
            return False
        return True
