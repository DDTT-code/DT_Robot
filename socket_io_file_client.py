import socketio
import time
import dtrobot_config as dtrobot

class Client():
    def __init__(self):
        self.info = None

    def create_client(self):
        sio = socketio.Client()

        @sio.on('connect', namespace='/det_conf_web')
        def on_connect():
            print('file client connection')
            # sio.emit('data', {'msg': 'lj'})
    
        @sio.on('disconnect', namespace='/det_conf_web')
        def on_disconnect():
            print('disconnected')
            sio.disconnect(namespaces=['/det_conf_web'])

        @sio.on('connect_error', namespace='/det_conf_web')
        def on_connect_error():
            print("connect_error")
            sio.disconnect(namespaces=['/det_conf_web'])
        
        @sio.on('data_file_transfer', namespace='/det_conf_web')
        def on_file(data):
            print(data)
            if len(dtrobot.FILE_INFO) == 0:
                dtrobot.FILE_INFO = data

        sio.connect('http://127.0.0.1:8080', namespaces=['/det_conf_web'])