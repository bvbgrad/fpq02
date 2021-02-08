from flask import render_template, redirect, url_for
from app import db
from app.errors import bp

import logging
import os

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)

# TODO provide message for when a 404 error route is transversed
#   to get to the Welcome page
# TODO create logic to determine when it is better to show the 404 error page
@bp.app_errorhandler(404)
def not_found_error(error):
    logger.info(f"404 error - redirecting to main/index")
    return redirect(url_for('main.index'))
    # return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
