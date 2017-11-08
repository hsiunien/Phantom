from flask import render_template
from . import main
@main.app_errorhandler(404)
def handle_page_not_find(e):
    return render_template('404.html'), 404
