#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

from builtins import float, object
import time

import os
import dtrobot_gpio as gpio
import dtrobot_config as dtrobot

from dtrobot_configparser import HandleConfig
path_data = os.path.dirname(os.path.realpath(__file__)) + '/data.ini'
cfgparser = HandleConfig(path_data)

class Motor():
	def __init__(self):
		pass

	def set_speed(self, num, speed):
		"""
		设置电机速度，num表示左侧还是右侧，等于1表示左侧，等于右侧，speed表示设定的速度值（0-100）
		"""
		# print(speed)
		if num == 1:  # 调节左侧
			gpio.ena_pwm(speed)
		elif num == 2:  # 调节右侧
			gpio.enb_pwm(speed)

	def motor_init(self):
		"""
		获取机器人存储的速度
		"""
		print("获取机器人存储的速度")
		speed = cfgparser.get_data('motor', 'speed')
		dtrobot.LEFT_SPEED = speed[0]
		dtrobot.RIGHT_SPEED = speed[1]
		print(speed[0])
		print(speed[1])

	def save_speed(self):
		speed = [0, 0]
		speed[0] = dtrobot.LEFT_SPEED
		speed[1] = dtrobot.RIGHT_SPEED
		cfgparser.save_data('motor', 'speed', speed)

	def m1m2_forward(self):
		# 设置电机组M1、M2正转
		gpio.digital_write(gpio.IN1, True)
		gpio.digital_write(gpio.IN2, False)

	def m1m2_reverse(self):
		# 设置电机组M1、M2反转
		gpio.digital_write(gpio.IN1, False)
		gpio.digital_write(gpio.IN2, True)

	def m1m2_stop(self):
		# 设置电机组M1、M2停止
		gpio.digital_write(gpio.IN1, False)
		gpio.digital_write(gpio.IN2, False)

	def m3m4_forward(self):
		# 设置电机组M3、M4正转
		gpio.digital_write(gpio.IN3, True)
		gpio.digital_write(gpio.IN4, False)

	def m3m4_reverse(self):
		# 设置电机组M3、M4反转
		gpio.digital_write(gpio.IN3, False)
		gpio.digital_write(gpio.IN4, True)

	def m3m4_stop(self):
		# 设置电机组M3、M4停止
		gpio.digital_write(gpio.IN3, False)
		gpio.digital_write(gpio.IN4, False)

	def forward(self):
		"""
		设置机器人运动方向为前进
		"""
		self.set_speed(1, dtrobot.LEFT_SPEED)
		self.set_speed(2, dtrobot.RIGHT_SPEED)
		self.m1m2_forward()
		self.m3m4_forward()

	def back(self):
		"""
		#设置机器人运动方向为后退
		"""
		self.set_speed(1, dtrobot.LEFT_SPEED)
		self.set_speed(2, dtrobot.RIGHT_SPEED)
		self.m1m2_reverse()
		self.m3m4_reverse()

	def left(self):
		"""
		#设置机器人运动方向为左转
		"""
		self.set_speed(1, dtrobot.LEFT_SPEED)
		self.set_speed(2, dtrobot.RIGHT_SPEED)
		self.m1m2_reverse()
		self.m3m4_forward()

	def right(self):
		"""
		#设置机器人运动方向为右转
		"""
		self.set_speed(1, dtrobot.LEFT_SPEED)
		self.set_speed(2, dtrobot.RIGHT_SPEED)
		self.m1m2_forward()
		self.m3m4_reverse()

	def stop(self):
		"""
		#设置机器人运动方向为停止
		"""
		self.set_speed(1, 0)
		self.set_speed(2, 0)
		self.m1m2_stop()
		self.m3m4_stop()
	
	def run_motor(self):
		while True:
			if len(dtrobot.MOTOR_INFO):
				if dtrobot.MOTOR_INFO[0] == 0x00:
					if dtrobot.MOTOR_INFO[1] == 0x01:
						self.forward()
					elif dtrobot.MOTOR_INFO[1] == 0x02:
						self.back()
					elif dtrobot.MOTOR_INFO[1] == 0x03:
						self.left()
					elif dtrobot.MOTOR_INFO[1] == 0x04:
						self.right()
					elif dtrobot.MOTOR_INFO[1] == 0x00:
						self.stop()
					else:
						self.stop()
				
				dtrobot.MOTOR_INFO = []

	def dtrobot_motor(self):
		self.run_motor()