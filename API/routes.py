from flask import Blueprint
from API.controllers import get_data, control_command, esp_status, ingest_status, esp_latest
from Front.home import home

api_bp = Blueprint('api', __name__)

api_bp.route('/', methods=['GET'])(home)
api_bp.route('/data', methods=['GET'])(get_data)
api_bp.route('/control', methods=['POST'])(control_command)
api_bp.route('/esp/status', methods=['GET'])(esp_status)
api_bp.route('/esp/ingest', methods=['POST'])(ingest_status)
api_bp.route('/esp/latest', methods=['GET'])(esp_latest)
