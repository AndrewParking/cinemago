from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin')

# TODO: import all concerns admin
from . import models, views, forms
