# server.py
from flask import Flask
from flask_cors import CORS
from control_runner import start_control, stop_control, is_running

app = Flask(__name__)
CORS(app)

@app.route('/start', methods=['POST'])
def start():
    start_control()
    return {'status': 'started'}

@app.route('/stop', methods=['POST'])
def stop():
    stop_control()
    return {'status': 'stopped'}

@app.route('/status')
def status():
    return {'running': is_running()}

if __name__ == '__main__':
    app.run(port=5000)
