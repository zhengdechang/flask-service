from flask import Blueprint
from .user import user

blueprint = Blueprint('api', __name__, url_prefix='/api')
blueprint.register_blueprint(user, url_prefix='/user')
