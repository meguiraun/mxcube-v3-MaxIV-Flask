from flask import Flask
from flask.ext.socketio import SocketIO
socketio = SocketIO()
from threading import Thread

@socketio.on('connect', namespace='/test')
def connect():
    print 'someone connected'
    socketio.emit('test', {'data': 'Welcome'}, namespace='/test')

def create_app(debug=True):
	"""Create an application."""
	app = Flask(__name__, static_url_path='')
	app.debug = debug
	#app.config['SECRET_KEY'] = 'mXcUbE'
	#app.config['SERVER_NAME'] = '127.0.0.1'

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	socketio.init_app(app)#, host='srvv-bli9113-datacollection', port=8081)
	return app
