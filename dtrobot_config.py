#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

import numpy as np

CLIENT = None
CAMERA = None
CAMERA_MODE = 0
MOTOR = None
SERVO = None
ULTRASONIC = None
INFRARED = None
FUNCTION = None
FTP_SERVER = None
CAMERA_INFO = []
CAMERA_MODE_INFO = []
FILE_INFO = []
MOTOR_INFO = []
SERVO_INFO = []
ULTRASONIC_INFO = []
ULTRASONIC_MODE = 0
DISTANCE_INFO = []
INFRARED_INFO = []
INFRARED_MODE = 0

LEFT_SPEED = 80
RIGHT_SPEED = 80
LASRT_LEFT_SPEED = 100
LASRT_RIGHT_SPEED = 100

SERVO_CAMERA_X = 7
SERVO_CAMERA_Y = 8
SERVO_CAMERA_ANGLE_X = 80
SERVO_CAMERA_ANGLE_Y = 20
SERVO_ANGLE = 90
SERVO_ANGLE_LAST = 90
ANGLE_MAX = 160  			# 舵机角度上限值，防止舵机卡死，可设置小于180的数值
ANGLE_MIN = 15  
ANGLE = [90, 90, 90, 90, 90, 90, 90, 5]

DISTANCE = 0  			# 超声波测距值
AVOID_CHANGER = 1  		# 超声波避障启动标志
AVOIDDROP_CHANGER = 1 	# 红外防跌落启动标志

MAZE_TURN_TIME = 400    # 迷宫状态转向角度设置

LINE_POINT_ONE = 320  	# 摄像头巡线线1 x方向坐标
LINE_POINT_TWO = 320  	# 摄像头巡线线2 x方向坐标

PATH_DECT_FLAG = 0

# 颜色检测跟随的颜色区间
# 颜色区间低阀值
COLOR_LOWER = [
	# 红色
	np.array([0, 43, 46]),
	# 绿色
	np.array([35, 43, 46]),
	# 蓝色
	np.array([100, 43, 46]),
	# 紫色
	np.array([125, 43, 46]),
	# 橙色
	np.array([11, 43, 46])
]
# 颜色区间高阀值
COLOR_UPPER = [
	# 红色
	np.array([10, 255, 255]),
	# 绿色
	np.array([77, 255, 255]),
	# 蓝色
	np.array([124, 255, 255]),
	# 紫色
	np.array([155, 255, 255]),
	# 橙色
	np.array([25, 255, 255])
]
COLOR_FOLLOW_SET = {'red': 0, 'green': 1, 'blue': 2, 'violet': 3, 'orange': 4}		# 颜色跟随功能颜色区间下标设置
COLOR_INDEX = 0			# 颜色区间阈值下标，在socket通信中改变

BARCODE_DATE = None		# 二维码识别数据
BARCODE_TYPE = None		# 二维码识别数据类型