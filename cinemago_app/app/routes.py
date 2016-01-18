from . import api
from .admin import admin, views as admin_views
from .scrapy_layer import views as scrapy_layer_views
from .seanses import views as seanses_views


admin.add_url_rule('/login', 'login', admin_views.login, methods=['POST'])
admin.add_url_rule('/register', 'register', admin_views.register, methods=['POST'])
api.add_resource(admin_views.UsersListEndpoint, '/users', endpoint='admin.users_list')
api.add_resource(admin_views.UsersDetailEndpoint, '/users/<int:pk>', endpoint='admin.users_detail')
api.add_resource(admin_views.RolesListEndpoint, '/roles', endpoint='admin.roles_list')
api.add_resource(admin_views.RolesDetailEndpoint, '/roles/<int:pk>', endpoint='admin.roles_detail')
api.add_resource(admin_views.PermissionsEndpoint, '/permissions', endpoint='admin.permissions')
api.add_resource(scrapy_layer_views.JobsEndpoint, '/jobs', endpoint='scrapy_layer.jobs')
api.add_resource(scrapy_layer_views.SpidersEndpoint, '/spiders', endpoint='scrapy_layer.spiders')
api.add_resource(seanses_views.GenresListEndpoint, '/genres', endpoint='seanses.genres_list')
api.add_resource(seanses_views.GenresDetailEndpoint, '/genres/<int:pk>', endpoint='seanses.genres_detail')
api.add_resource(seanses_views.FilmsListEndpoint, '/films', endpoint='seanses.films_list')
api.add_resource(seanses_views.FilmsDetailEndpoint, '/films/<int:pk>', endpoint='seanses.films_detail')
