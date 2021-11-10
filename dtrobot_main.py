#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

import time
import threading
from dtrobot_camera import Camera
from dtrobot_motor import Motor
from dtrobot_servo import Servo
from dtrobot_ultrasonic import Ultrasonic
from dtrobot_infrared import Infrared
from dtrobot_function import Function
import dtrobot_config as dtrobot

from socket_io_client import Client

if __name__ == '__main__':
    dtrobot.CLIENT = Client()
    dtrobot.CAMERA = Camera()
    dtrobot.MOTOR = Motor()
    dtrobot.SERVO = Servo()
    dtrobot.ULTRASONIC = Ultrasonic()
    dtrobot.INFRARED = Infrared()
    dtrobot.FUNCTION = Function()
    threads = []
    t_server = threading.Thread(target = dtrobot.CLIENT.create_client, args = ())
    threads.append(t_server)
    t_camera = threading.Thread(target = dtrobot.CAMERA.dtrobot_camera, args = ())
    threads.append(t_camera)
    t_motor = threading.Thread(target = dtrobot.MOTOR.dtrobot_motor, args = ())
    threads.append(t_motor)
    t_servo = threading.Thread(target = dtrobot.SERVO.dtrobot_servo, args = ())
    threads.append(t_servo)
    t_ultrasonic = threading.Thread(target = dtrobot.ULTRASONIC.dtrobot_ultrasonic, args = ())
    threads.append(t_ultrasonic)
    t_infrared = threading.Thread(target = dtrobot.INFRARED.dtrobot_infrared, args = ())
    threads.append(t_infrared)

    for t in threads:
        t.setDaemon(True)
        t.start()
        time.sleep(0.05)
    
    while True:
        if dtrobot.CAMERA_MODE == 2:
            dtrobot.FUNCTION.qrcode_control()
        elif dtrobot.CAMERA_MODE == 4:
            dtrobot.FUNCTION.linepatrol_control()