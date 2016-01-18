from schematics.models import Model
from schematics.types import EmailType, StringType, IntType, BooleanType
from schematics.types.compound import ListType
from schematics.exceptions import ValidationError
from .models import Role, User

# TODO: Maybe RegistrationForm should inherit from LoginForm

class LoginForm(Model):
    email = EmailType(required=True, min_length=7, max_length=64)
    password = StringType(required=True, min_length=3, max_length=30)

    def validate_email(self, data, value):
        u = User.query.filter_by(email=value).first()
        if u is None:
            raise ValidationError('Email is wrong.')
        return value

    class Options:
        serialize_when_none = False


class RegistrationForm(Model):
    email = EmailType(required=True, min_length=7, max_length=64)
    password = StringType(required=True, min_length=3, max_length=30)
    first_name = StringType(min_length=3, max_length=64)
    last_name = StringType(min_length=3, max_length=64)
    about = StringType(min_length=1)
    location = StringType(min_length=3, max_length=128)

    def validate_email(self, data, value):
        u = User.query.filter_by(email=value).first()
        if u is not None:
            raise ValidationError('This email is already taken')
        return value

    class Options:
        serialize_when_none = False


class UserUpdateForm(RegistrationForm):
    role_id = IntType()

    def validate_role_id(self, data, value):
        if value is not None:
            role = Role.query.get(value)
            if role is None:
                raise ValidationError('Such a role does not exist.')
        return value


class RoleCreationForm(Model):
    name = StringType(required=True, min_length=3, max_length=64)
    permissions = ListType(IntType, required=True, min_size=1)
    default = BooleanType(default=False)

    def validate_default(self, data, value):
        if value:
            role = Role.query.filter_by(default=True).first()
            if role is not None:
                raise ValidationError('Default role already exists.')
        return value

    def to_native(self, **kwargs):
        data = super(RoleCreationForm, self).to_native(**kwargs)
        if 'permissions' in data:
            perms = data.pop('permissions')
            transformed_perms = 0x0
            for perm in perms:
                transformed_perms = transformed_perms | perm
            data['permissions'] = transformed_perms
        return data

    class Options:
        serialize_when_none = False
