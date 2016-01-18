import requests
from flask import current_app, request
from flask.ext.restful import Resource
from app.decorators import auth_required, permission_required
from app.exceptions import ScrapyServerError
from app.admin.models import Permissions
from .forms import JobForm


class JobsEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_JOBS)
    def get(self):
        project = request.args.get('project')
        if project is None:
            project = current_app.config['SCRAPY_PROJECT_NAME']
        url = current_app.config['SCRAPY_SERVER_URL'] + 'listjobs.json'
        params = {'project': project}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ScrapyServerError
        return response.json(), 200

    @auth_required
    @permission_required(Permissions.CREATE_JOB)
    def post(self):
        data = request.get_json()
        form = JobForm(data)
        form.validate()
        url = current_app.config['SCRAPY_SERVER_URL'] + 'schedule.json'
        response = requests.post(url, data=form.to_native())
        if response.status_code != 200:
            raise ScrapyServerError
        return response.json(), 200

    @auth_required
    @permission_required(Permissions.CANCEL_JOB)
    def delete(self):
        form = JobForm(request.args)
        form.validate()
        url = current_app.config['SCRAPY_SERVER_URL'] + 'cancel.json'
        response = requests.post(url, data=form.to_native())
        if response.status_code != 200:
            raise ScrapyServerError
        return response.json(), 204


class SpidersEndpoint(Resource):

    @auth_required
    @permission_required(Permissions.GET_SPIDERS)
    def get(self):
        project = request.args.get('project')
        if project is None:
            project = current_app.config['SCRAPY_PROJECT_NAME']
        url = current_app.config['SCRAPY_SERVER_URL'] + 'listspiders.json'
        response = requests.get(url, params={'project': project})
        if response.status_code != 200:
            raise ScrapyServerError
        return response.json(), 200
