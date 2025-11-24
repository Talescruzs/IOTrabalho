from flask import Blueprint
from API.controllers import (
    get_data, control_command, esp_status, ingest_status, 
    esp_latest, get_chart_data, get_sensor_history, get_detailed_readings, get_esp_data
)
from Front.home import home, dashboard

api_bp = Blueprint('api', __name__)

api_bp.route('/', methods=['GET'])(home)
api_bp.route('/dashboard', methods=['GET'])(dashboard)
api_bp.route('/data', methods=['GET'])(get_data)
api_bp.route('/control', methods=['POST'])(control_command)
api_bp.route('/esp/status', methods=['GET'])(esp_status)
api_bp.route('/esp/ingest', methods=['POST'])(ingest_status)
api_bp.route('/esp/latest', methods=['GET'])(esp_latest)
api_bp.route('/api/chart-data', methods=['GET'])(get_chart_data)
api_bp.route('/api/sensor-history', methods=['GET'])(get_sensor_history)
api_bp.route('/api/detailed-readings', methods=['GET'])(get_detailed_readings)
api_bp.route('/api/esp-data', methods=['GET'])(get_esp_data)
