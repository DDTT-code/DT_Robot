import eventlet

eventlet.monkey_patch()

import socketio
import eventlet.wsgi


det_conf_web_name = '/det_conf_web'  # 网页端命名空间
det_conf_web_room = 'det_conf_web'  # 网页端房间

det_conf_data_name = '/det_conf_data'  # 本地数据命名空间
det_conf_data_room = 'det_conf_data'  # 本地数据房间

det_conf_file_name = '/det_conf_web'  # 本地文件命名空间
det_conf_file_room = 'det_conf_web'   # 本地文件房间

sio = socketio.Server(async_mode = 'eventlet', cors_allowed_origins = '*')  # 指明在evenlet模式下
app = socketio.Middleware(sio)


@sio.on('connect', namespace = det_conf_web_name)
def on_connect(sid, environ = None):
    sio.enter_room(sid, det_conf_web_room, namespace = det_conf_web_name)
    print('det_conf-------connect')
    print(sid, environ)


@sio.on('disconnect', namespace = det_conf_web_name)
def on_disconnect(sid):
    sio.leave_room(sid, det_conf_web_room, namespace = det_conf_web_name)
    print('det_conf-------disconnect')
    print(sid)


@sio.on('connect', namespace = det_conf_data_name)
def on_connect(sid, environ = None):
    sio.enter_room(sid, det_conf_data_room, namespace = det_conf_data_name)
    print('det_conf-------connect')
    print(sid, environ)


@sio.on('disconnect', namespace = det_conf_data_name)
def on_disconnect(sid):
    sio.leave_room(sid, det_conf_data_room, namespace = det_conf_data_name)
    print('det_conf-------disconnect')
    print(sid)


@sio.on('connect', namespace = det_conf_file_name)
def on_connect(sid, environ = None):
    sio.enter_room(sid, det_conf_file_room, namespace = det_conf_file_name)
    print('det_conf-------connect')
    print(sid, environ)


@sio.on('disconnect', namespace = det_conf_file_name)
def on_disconnect(sid):
    sio.leave_room(sid, det_conf_file_room, namespace = det_conf_file_name)
    print('det_conf-------disconnect')
    print(sid)


# 接收小车data本身发送的数据
@sio.on('data_camera_info', namespace = det_conf_data_name)
def on_camera(sid, data):
    # 发送数据到网页端
    # print(data)
    sio.emit('data_camera_info', str(data), room = det_conf_web_room, namespace = det_conf_web_name)


# 接收网页发送的数据
@sio.on('data_motor_info', namespace = det_conf_web_name)
def on_motor(sid, data):
    # 发送到小车data
    sio.emit('data_motor_info', data, room = det_conf_data_room, namespace = det_conf_data_name)


# 接收网页发送的数据
@sio.on('data_servo_info', namespace = det_conf_web_name)
def on_servo(sid, data):
    # 发送到小车data
    # print(data)
    sio.emit('data_servo_info', data, room = det_conf_data_room, namespace = det_conf_data_name)


# 接收网页发送的file
@sio.on('data_file_transfer', namespace = det_conf_web_name)
def on_file(sid, data):
    # 发送到小车file
    sio.emit('data_file_transfer', data, room = det_conf_file_room, namespace = det_conf_file_name)

@sio.on('data_ultrasonic_info', namespace = det_conf_web_name)
def on_file(sid, data):
    # 发送到小车file
    sio.emit('data_ultrasonic_info', data, room = det_conf_data_room, namespace = det_conf_data_name)

@sio.on('data_infrared_info', namespace = det_conf_web_name)
def on_file(sid, data):
    # 发送到小车file
    sio.emit('data_infrared_info', data, room = det_conf_data_room, namespace = det_conf_data_name)

eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)