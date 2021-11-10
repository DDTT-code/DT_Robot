#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

import threading
import time
import dtrobot_gpio as gpio
import dtrobot_config as dtrobot

from dtrobot_motor import Motor

motor = Motor()

class Infrared():
    def __init__(self):
        pass

    def trackline(self):
        """
        红外巡线
        """
        dtrobot.LEFT_SPEED = 30
        dtrobot.RIGHT_SPEED = 30
        # print('ir_trackline run...')
        # 两边都没有检测到黑线
        if (gpio.digital_read(gpio.IR_L) == 0) and (gpio.digital_read(gpio.IR_R) == 0):  # 黑线为高，地面为低
            motor.forward()
            # 右边红外传感器检测到黑线
        elif (gpio.digital_read(gpio.IR_L) == 0) and (gpio.digital_read(gpio.IR_R) == 1):
            motor.right()
            # 左边传感器检测到黑线
        elif (gpio.digital_read(gpio.IR_L) == 1) and (gpio.digital_read(gpio.IR_R) == 0):
            motor.left()
            # 两边同时检测到黑线
        elif (gpio.digital_read(gpio.IR_L) == 1) and (gpio.digital_read(gpio.IR_R) == 1):
            motor.stop()

    def iravoid(self):
        """
        红外避障
        """
        if gpio.digital_read(gpio.IR_M) == 0:		# 如果中间传感器校测到物体
            motor.stop()

    def irfollow(self):
        """
        红外跟随
        """
        dtrobot.LEFT_SPEED = 30
        dtrobot.RIGHT_SPEED = 30
        if  (gpio.digital_read(gpio.IRF_L) == 0 and gpio.digital_read(gpio.IRF_R) == 0 and gpio.digital_read(gpio.IR_M) == 1):
            motor.stop()				# 停止：左右检测到障碍物或全都检测不到障碍物
        else:
            if gpio.digital_read(gpio.IRF_L) == 1 and gpio.digital_read(gpio.IRF_R) == 0:
                dtrobot.LEFT_SPEED = 50
                dtrobot.RIGHT_SPEED = 50
                motor.right()			# 左边传感器未检测到障碍物+右边传感器检测到障碍物
            elif gpio.digital_read(gpio.IRF_L) == 0 and gpio.digital_read(gpio.IRF_R) == 1:
                dtrobot.LEFT_SPEED = 50
                dtrobot.RIGHT_SPEED = 50
                motor.left()			# 左边传感器检测到障碍物+右边传感器未检测到障碍物
            elif (gpio.digital_read(gpio.IRF_L) == 1 and gpio.digital_read(gpio.IRF_R) == 1) or (gpio.digital_read(gpio.IRF_L) == 1 and gpio.digital_read(gpio.IRF_R) == 1):
                dtrobot.LEFT_SPEED = 50
                dtrobot.RIGHT_SPEED = 50
                motor.forward()		# 前进：只有中间传感器检测到障碍物

    def avoiddrop(self):
        """
        红外防跌落
        """
        dtrobot.LEFT_SPEED = 25
        dtrobot.RIGHT_SPEED = 25
        if (gpio.digital_read(gpio.IR_L) == 0) and (gpio.digital_read(gpio.IR_R) == 0):  # 俩个红外传感器都探测到地面的时候
            dtrobot.AVOIDDROP_CHANGER = 1		# 标志位置1，串口解析中方向判断此标志
        else:
            if dtrobot.AVOIDDROP_CHANGER == 1: 	# 只有当上一次得到状态是正常状态时才会运行停止，避免重复执行停止无法再进行遥控
                motor.stop()
                dtrobot.AVOIDDROP_CHANGER = 0
    
    def infrared_mode_info(self):
        while True:
            if len(dtrobot.INFRARED_INFO):
                if dtrobot.INFRARED_INFO[0] == 0x04:
                    if dtrobot.INFRARED_INFO[1] == 0x00:
                        dtrobot.INFRARED_MODE = 0
                    elif dtrobot.INFRARED_INFO[1] == 0x01:
                        dtrobot.INFRARED_MODE = 1
                    elif dtrobot.INFRARED_INFO[1] == 0x02:
                        dtrobot.INFRARED_MODE = 2
                    elif dtrobot.INFRARED_INFO[1] == 0x03:
                        dtrobot.INFRARED_MODE = 3
                    elif dtrobot.INFRARED_INFO[1] == 0x04:
                        dtrobot.INFRARED_MODE = 4
                    else:
                        dtrobot.INFRARED_MODE = 0

                dtrobot.INFRARED_INFO = []

    def dtrobot_infrared(self):
        threads = []
        t_mode_info = threading.Thread(target = self.infrared_mode_info, args = ())
        threads.append(t_mode_info)
        for t in threads:
            t.setDaemon(True)
            t.start()
            time.sleep(0.05)

        while True:
            if dtrobot.INFRARED_MODE == 1:
                self.trackline()
            elif dtrobot.INFRARED_MODE == 2:
                self.iravoid()
            elif dtrobot.INFRARED_MODE == 3:
                self.irfollow()
            elif dtrobot.INFRARED_MODE == 4:
                self.avoiddrop()