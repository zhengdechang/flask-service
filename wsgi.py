import os
from eventlet import wsgi
import eventlet
from flask import Flask, g, request, current_app
from flask_cors import CORS


from apis import blueprint as api
from config import ProductionConfig
from database import db, setup_db
from log import logging
from auth.auth_service import AuthService
from utils.utils import make_response
import load_env

def validate_token(request, current_app):
    try:
        if not request.endpoint.endswith('login'):
            access_token = request.cookies.get('access_token')
            resp = None
            if access_token is not None:
                is_valid, _ = current_app.config[
                    'AUTH_SERVICE'].verify_token_expiration(access_token)
                if not is_valid:
                    resp = make_response(401,
                                         data=None,
                                         message=f'login has expired.')

            else:
                resp = make_response(401,
                                     data=None,
                                     message=f'login has expired.')
            if resp is not None:
                resp[0].set_cookie('access_token',
                                   "",
                                   max_age=-1,
                                   path='/',
                                   secure=False,
                                   httponly=True)
                resp[0].set_cookie('refresh_token',
                                   "",
                                   max_age=-1,
                                   path='/',
                                   secure=False,
                                   httponly=True)
                resp[0].set_cookie('logged_in',
                                   '',
                                   max_age=-1,
                                   path='/',
                                   secure=False,
                                   httponly=False)
                return resp
    except Exception as e:
        return make_response(401, data=None, message=f'{str(e)}')


def before_request():
    response = validate_token(request, current_app)
    if response is not None:
        return response
    g.db = db.session()


def after_request(response):
    db_session = g.pop('db', None)

    if db_session is not None:
        db_session.close()

    return response


def create_app():
    backend_app = Flask(__name__)
    CORS(backend_app, resources={r"/*": {"origins": "*"}})
    backend_app.config.from_object(ProductionConfig)
    backend_app.config['AUTH_SERVICE'] = AuthService(
        backend_app.config['AUTH_CONFIG'], )

    setup_db(backend_app)
    backend_app.register_blueprint(api)
    backend_app.before_request(before_request)
    backend_app.after_request(after_request)

    return backend_app


if __name__ == '__main__':
    SERVER_IP = os.environ.get('SERVER_IP', '0.0.0.0')
    SERVER_PORT = int(os.environ.get('SERVER_PORT', 8000))

    app = create_app()
    logging.info('SRT App is running...')
    wsgi.server(eventlet.listen((SERVER_IP, SERVER_PORT)), app)
