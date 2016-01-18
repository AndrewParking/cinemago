from flask import Blueprint

seanses = Blueprint('seanses', __name__, url_prefix='/seanses')

from . import models, views
