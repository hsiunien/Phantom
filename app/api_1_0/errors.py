from flask.json import jsonify

from app.exceptions import ValidationError
from . import api


def forbidden(message):
    response = jsonify({"status": 401, "error": message})
    return response, 401


def bad_request(param):
    response = jsonify({"status": 412, "error": param})
    return response, 412


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
