#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

from builtins import float, object, bytes

import time
import dtrobot_config as dtrobot

from dtrobot_motor import Motor
motor = Motor()

class Function():
	def __init__(self):
		pass

	def linepatrol_control(self):
		"""
		摄像头巡线小车运动
		:return:
		"""
		while dtrobot.CAMERA_MODE == 4:
			dx = dtrobot.LINE_POINT_TWO - dtrobot.LINE_POINT_ONE			# 上与下取样点中心坐标差值
			mid = int(dtrobot.LINE_POINT_ONE + dtrobot.LINE_POINT_TWO) / 2	# 上与下取样点中心坐标均值

			print("dx==%d" % dx)			# 打印上与下取样点中心坐标差值
			print("mid==%s" % mid)			# 打印上与下取样点中心坐标均值

			if 0 < mid < 260:				# 如果巡线中心点偏左，说明车子右偏离轨道,就需要左转来校正。
				print("turn left")
				motor.left()
			elif mid > 420:					# 如果巡线中心点偏右，说明车子左偏离轨道，就需要右转来校正。
				print("turn right")
				motor.right()
			else:							# 如果巡线中心点居中情况
				if dx > 45:
					print("turn left")		# 线有右倾斜的趋势
					motor.left()
				elif dx < -45:
					print("turn right")		# 线有左倾斜的趋势
					motor.right()
				else:
					print("motor stright")		# 线在中心位置，并且线处于竖直状态
					motor.forward()
			time.sleep(0.007)
			motor.stop()
			time.sleep(0.007)

	def qrcode_control(self):
		"""
		二维码检测识别控制小车运动
		:return:
		"""
		dtrobot.LASRT_LEFT_SPEED = dtrobot.LEFT_SPEED  # 将当前速度保存
		dtrobot.LASRT_RIGHT_SPEED = dtrobot.RIGHT_SPEED
		dtrobot.LEFT_SPEED = 30		# 设置合适的速度
		dtrobot.RIGHT_SPEED = 30
		code_status = 0
		while dtrobot.CAMERA_MOD == 2:
			time.sleep(0.05)
			if dtrobot.BARCODE_DATE == 'start':		# 检测到起始信号，start的二维码
				time.sleep(1.5)
				code_status = 1						# code_status
			elif dtrobot.BARCODE_DATE == 'stop':	# 检测到结束信号，stop的二维码
				time.sleep(1.5)
				code_status = 0						# code_status

			if code_status:
				if dtrobot.BARCODE_DATE == 'forward':	# 检测到forward的二维码，小车前进
					motor.forward()
					time.sleep(2.5)
					motor.stop()
					time.sleep(0.5)
				elif dtrobot.BARCODE_DATE == 'back':	# 检测到back的二维码，小车后退
					motor.back()
					time.sleep(2.5)
					motor.stop()
					time.sleep(0.5)
				elif dtrobot.BARCODE_DATE == 'left':	# 检测到left的二维码，小车左转
					motor.left()
					time.sleep(1.5)
					motor.stop()
					time.sleep(0.5)
				elif dtrobot.BARCODE_DATE == 'right':	# 检测到right的二维码，小车右转
					motor.right()
					time.sleep(1.5)
					motor.stop()
					time.sleep(0.5)
				else:
					pass
			else:
				motor.stop()
				time.sleep(0.05)
		motor.stop()