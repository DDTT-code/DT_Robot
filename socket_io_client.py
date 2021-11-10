import socketio
import time
import dtrobot_config as dtrobot

class Client():
    def __init__(self):
        self.info = None

    def create_client(self):
        sio = socketio.Client()

        @sio.on('connect', namespace = '/det_conf_data')
        def on_connect():
            print('dtrobot client connection')
            # sio.emit('data', {'msg': 'lj'})
    
        @sio.on('disconnect', namespace = '/det_conf_data')
        def on_disconnect():
            print('disconnected')
            sio.disconnect()

        @sio.on('connect_error', namespace = '/det_conf_data')
        def on_connect_error():
            print("connect_error")
            sio.disconnect()
        
        @sio.on('data_motor_info', namespace = '/det_conf_data')
        def on_motor(data):
            if len(dtrobot.MOTOR_INFO) == 0:
                dtrobot.MOTOR_INFO = data

        @sio.on('data_servo_info', namespace = '/det_conf_data')
        def on_servo(data):
            if len(dtrobot.SERVO_INFO) == 0:
                dtrobot.SERVO_INFO = data
        
        @sio.on('data_ultrasonic_info', namespace = '/det_conf_data')
        def on_ultrasonic(data):
            if len(dtrobot.ULTRASONIC_INFO) == 0:
                dtrobot.ULTRASONIC_INFO = data
        
        @sio.on('data_infrared_info', namespace = '/det_conf_data')
        def on_infrared(data):
            if len(dtrobot.INFRARED_INFO) == 0:
                dtrobot.INFRARED_INFO = data

        @sio.on('data_infrared_info', namespace = '/det_conf_data')
        def on_camera_mode(sid, data):
            if len(dtrobot.CAMERA_MODE_INFO) == 0:
                dtrobot.CAMERA_MODE_INFO = data

        sio.connect('http://127.0.0.1:8080', namespaces = ['/det_conf_data'])
        while True:
            if len(dtrobot.CAMERA_INFO):
                self.info = dtrobot.CAMERA_INFO
                dtrobot.CAMERA_INFO = []
                sio.emit('data_camera_info', self.info, namespace = '/det_conf_data')
            elif len(dtrobot.DISTANCE_INFO):
                self.info = dtrobot.DISTANCE_INFO
                dtrobot.DISTANCE_INFO = []
                sio.emit('data_distance_info', self.info, namespace = '/det_conf_data')
            
            self.info = []
            time.sleep(0.5)