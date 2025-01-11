from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='static')
app.config['SECRET'] = "secret!"
CORS(app)

base_path = '/Little-Brother'
sio = SocketIO(
    app,
    path=base_path + '/socket.io',
    logger=False,
    engineio_logger=False,
    async_mode="eventlet",
    cors_allowed_origins="*"
)

@app.route(base_path + '/')
def index():
    return render_template('display/index.html')

@app.route(base_path + '/remote', methods=['GET', 'POST'])
def remote():
    return render_template('remote/index.html')


@app.route(base_path + '/display', methods=['GET', 'POST'])
def display():
    return render_template('display/index.html')

@app.route(base_path + '/display/<path:path>')
def display_path(path):
    return send_from_directory('templates/display', path)


@app.route(base_path + '/camera', methods=['GET', 'POST'])
def camera_data():
    print(request.data)
    return "200"

@app.route(base_path + '/remote/map', methods=['GET', 'POST'])
def remote_map():
    return render_template('remote/map/index.html')

@app.route(base_path + '/remote/control', methods=['GET', 'POST'])
def remote_control():
    return render_template('remote/control/index.html')

@app.route(base_path + '/remote/commands', methods=['GET', 'POST'])
def remote_commands():
    return render_template('remote/commands/index.html')

@app.route(base_path + '/remote/<path:path>')
def remote_path(path):
    return send_from_directory('templates/remote', path)

@app.route(base_path + '/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
