from flask import render_template, request, jsonify

from . import main


@main.app_errorhandler(404)
def handle_page_not_find(e):
    if request_wants_json():
        return jsonify({"status": 404, "error": {"errCode": 404, "errMsg": 'not found'}})
    else:
        return render_template('404.html'), 404


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
           request.accept_mimetypes[best] > \
           request.accept_mimetypes['text/html']
