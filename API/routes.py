import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint
from controllers import get_data
from Front.home import home

api_bp = Blueprint('api', __name__)

api_bp.route('/', methods=['GET'])(home)
api_bp.route('/data', methods=['GET'])(get_data)
