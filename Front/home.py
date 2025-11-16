from flask import render_template

def home():
    control_url = "http://127.0.0.1:5000/control"
    return render_template('home.html', control_url=control_url)

def dashboard():
    return render_template('dashboard.html')

def test_readings():
    return render_template('test_readings.html')
