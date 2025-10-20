from flask import Blueprint
from API.controllers import get_data
from Front.home import home

api_bp = Blueprint('api', __name__)

api_bp.route('/', methods=['GET'])(home)
api_bp.route('/data', methods=['GET'])(get_data)
