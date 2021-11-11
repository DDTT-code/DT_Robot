#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

from builtins import hex, eval, int, object
from dtrobot_i2c import I2C
import os

i2c = I2C()
import dtrobot_config as dtrobot

from dtrobot_configparser import HandleConfig
path_data = os.path.dirname(os.path.realpath(__file__)) + '/data.ini'
cfgparser = HandleConfig(path_data)

class Servo():
    """
    舵机控制类
    """
    def __init__(self):
        pass

    def angle_limit(self, angle):
        """
        对舵机角度限幅，防止舵机堵转烧毁
        """
        if angle > dtrobot.ANGLE_MAX:
            angle = dtrobot.ANGLE_MAX
        elif angle < dtrobot.ANGLE_MIN:
            angle = dtrobot.ANGLE_MIN
        return angle

    def set(self, servonum, servoangle):
        """
        设置舵机角度
        :param servonum:舵机号
        :param servoangle:舵机角度
        :return:
        """
        angle = self.angle_limit(servoangle)
        buf = [0xff, 0x01, servonum, angle, 0xff]
        try:
            i2c.writedata(i2c.mcu_address, buf)
        except Exception as e:
            print('servo write error:', e)

    def store(self):
        """
        存储舵机角度
        :return:
        """
        cfgparser.save_data("servo", "angle", dtrobot.ANGLE)

    def restore(self):
        """
        恢复舵机角度
        :return:
        """
        dtrobot.ANGLE = cfgparser.get_data("servo", "angle")
        for i in range(0, 8):
            dtrobot.SERVO_NUM = i + 1
            dtrobot.SERVO_ANGLE = dtrobot.ANGLE[i]
            self.set(i + 1, dtrobot.ANGLE[i])

    def run_servo(self):
        while True:
            if len(dtrobot.SERVO_INFO):
                if dtrobot.SERVO_INFO[0] == 0x01:
                    if dtrobot.SERVO_INFO[1] == 0x01:
                        dtrobot.SERVO_CAMERA_ANGLE_Y = dtrobot.SERVO_CAMERA_ANGLE_Y + 20
                        self.set(dtrobot.SERVO_CAMERA_Y, dtrobot.SERVO_CAMERA_ANGLE_Y)
                    elif dtrobot.SERVO_INFO[1] == 0x02:
                        dtrobot.SERVO_CAMERA_ANGLE_Y = dtrobot.SERVO_CAMERA_ANGLE_Y - 20
                        self.set(dtrobot.SERVO_CAMERA_Y, dtrobot.SERVO_CAMERA_ANGLE_Y)
                    elif dtrobot.SERVO_INFO[1] == 0x03:
                        dtrobot.SERVO_CAMERA_ANGLE_X = dtrobot.SERVO_CAMERA_ANGLE_X + 20
                        self.set(dtrobot.SERVO_CAMERA_X, dtrobot.SERVO_CAMERA_ANGLE_X)
                    else:
                        dtrobot.SERVO_CAMERA_ANGLE_X = dtrobot.SERVO_CAMERA_ANGLE_X - 20
                        self.set(dtrobot.SERVO_CAMERA_X, dtrobot.SERVO_CAMERA_ANGLE_X)
                
                dtrobot.SERVO_INFO = []

    def dtrobot_servo(self):
        self.run_servo()