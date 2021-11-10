#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

CLIENT = None
CAMERA = None
MOTOR = None
SERVO = None
ULTRASONIC = None
FTP_SERVER = None
CAMERA_INFO = []
FILE_INFO = []
MOTOR_INFO = []
SERVO_INFO = []
ULTRASONIC_INFO = []
DISTANCE_INFO = []
INFRARED_INFO = []

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

CAMERA_MOD = 0  		# 摄像头模式
LINE_POINT_ONE = 320  	# 摄像头巡线线1 x方向坐标
LINE_POINT_TWO = 320  	# 摄像头巡线线2 x方向坐标