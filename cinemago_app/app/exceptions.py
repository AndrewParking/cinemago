from flask import jsonify

# exception classes

class BadRequest(ValueError):
    pass


class Unauthorized(ValueError):
    pass


class Forbidden(ValueError):
    pass


class NotFound(ValueError):
    pass


class ScrapyServerError(ValueError):
    pass


# exception handlers

def validation_error_handler(e):
    response = jsonify({'error': 'Bad Request', 'messages': e.messages})
    response.status_code = 400
    return response


def bad_signature_handler(e):
    response = jsonify({
        'error': 'Bad Signature',
        'message': 'Singature is wrong. Please, provide the right one.',
    })
    response.status_code = 400
    return response


def signature_expired_handler(e):
    response = jsonify({
        'error': 'Signature Expired',
        'message': 'Signature is outdated. Please get new one.',
    })
    response.status_code = 400
    return response


def bad_request_handler(e):
    response = jsonify({'error': 'Bad Request', 'messages': str(e)})
    response.status_code = 400
    return response


def unauthorized_handler(e):
    response = jsonify({'error': 'Unauthorized', 'message': str(e)})
    response.status_code = 401
    return response


def forbidden_handler(e):
    response = jsonify({'error': 'Forbidden', 'message': str(e)})
    response.status_code = 403
    return response


def not_found_handler(e):
    response = jsonify({'error': 'Not Found', 'message': str(e)})
    response.status_code = 404
    return response


def scrapy_server_error_handler(e):
    response = jsonify({
        'error': 'Scrapy Server Error',
        'message': 'Some error occured on scrapy server side'})
    response.status_code = 500
    return response
