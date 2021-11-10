#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

import cv2
import base64
import threading
import time
from PIL import Image
from io import BytesIO
import dtrobot_config as dtrobot
from dtrobot_servo import Servo

servo = Servo()

class Camera():
    def __init__(self):
        self.cap_open = 0
        self.ret = 0
        self.cap = None
        self.frame = None
    
    def frame2base64(self, frame):
        img = Image.fromarray(frame)
        output_buffer = BytesIO()
        img.save(output_buffer, format = 'JPEG')
        byte_data = output_buffer.getvalue()
        base64_data = base64.b64encode(byte_data)
        return base64_data
    
    def face_detection(self):
        while True:
            if self.ret == 1:
                face_cascade = cv2.CascadeClassifier('/home/pi/dt_robot/python_src/face.xml')
                gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray)
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        # 参数分别是“目标帧”，“矩形”，“矩形大小”，“线条颜色”，“宽度”
                        cv2.rectangle(self.frame, (x, y), (x + h, y + w), (0, 255, 0), 2)
                dtrobot.CAMERA_INFO = self.frame2base64(self.frame)

    def run_camera(self):
        servo.set(dtrobot.SERVO_CAMERA_X, dtrobot.SERVO_CAMERA_ANGLE_X)
        servo.set(dtrobot.SERVO_CAMERA_Y, dtrobot.SERVO_CAMERA_ANGLE_Y)
        threads = []
        t_face_detection = threading.Thread(target = self.face_detection, args = ())
        threads.append(t_face_detection)
        for t in threads:
            t.setDaemon(True)
            t.start()
            time.sleep(0.05)

        while True:
            if self.cap_open == 0:
                try:
                    self.cap = cv2.VideoCapture(0)
                    self.cap.set(3, 320)
                    self.cap.set(4, 320)
                    self.cap_open = 1
                except Exception as e:
                    self.cap_open = 0
            else:
                try:
                    self.ret, self.frame = self.cap.read()
                except Exception as e:
                    self.cap_open = 0
                    self.cap.release()

    def dtrobot_camera(self):
        self.run_camera()