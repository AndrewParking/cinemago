from flask import Blueprint

scrapy_layer = Blueprint('scrapy_layer', __name__, url_prefix='/scrapy_layer')

from . import forms, views
