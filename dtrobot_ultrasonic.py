#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

import time
import threading
from builtins import int, chr, object

import dtrobot_gpio as gpio
import dtrobot_config as dtrobot

from dtrobot_motor import Motor
motor = Motor()

from dtrobot_servo import Servo
servo = Servo()


class Ultrasonic():
    def __init__(self):
        self.MAZE_ABLE = 0
        self.MAZE_CNT = 0
        self.MAZE_TURN_TIME = 0
        self.dis = 0
        self.s_L = 0
        self.s_R = 0

    def get_distance(self):
        """
        获取超声波距离函数,有返回值distance，单位cm
        """
        time_count = 0
        time.sleep(0.01)
        gpio.digital_write(gpio.TRIG, True)  # 拉高超声波Trig引脚
        time.sleep(0.000015)  # 发送10um以上高电平方波
        gpio.digital_write(gpio.TRIG, False)  # 拉低
        while not gpio.digital_read(gpio.ECHO):  # 等待Echo引脚由低电平变成高电平
            pass
        t1 = time.time()  # 记录Echo引脚高电平开始时间点
        while gpio.digital_read(gpio.ECHO):  # 等待Echo引脚由低电平变成低电平
            if time_count < 2000:  # 超时检测，防止死循环
                time_count = time_count + 1
                time.sleep(0.000001)
                pass
            else:
                print("NO ECHO receive! Please check connection")
                break
        t2 = time.time()  # 记录Echo引脚高电平结束时间点
        distance = (t2 - t1) * 340 / 2 * 100  # Echo引脚高电平持续时间就是超声波由发射到返回的时间，即用时间x声波速度/2等于单程即超声波距物体距离值
        # t2-t1时间单位s,声波速度340m/s,x100将距离值单位m转换成cm
        # print("distance is %d" % distance)  # 打印距离值
        if distance < 500:  # 正常检测距离值
            # print("distance is %d"%distance)
            Distance = round(distance, 2)
            return Distance
        else:
            # print("distance is 0")  # 如果距离值大于5m,超出检测范围
            Distance = 0
            return 0

    def avoidbyragar(self):
        """
        超声波避障函数
        """
        dtrobot.LEFT_SPEED = 30
        dtrobot.RIGHT_SPEED = 30
        dis = self.get_distance()
        if 25 < dis < 300 or dis == 0:  # 距离大于25cm小于300cm超声波的测距范围,等于0的时候是远距离超过超声波测距范围
            dtrobot.AVOID_CHANGER = 1
        else:
            if dtrobot.AVOID_CHANGER == 1:
                motor.stop()
                dtrobot.AVOID_CHANGER = 0

    def send_distance(self):
        """
        发送超声波数据至上位机
        """
        dtrobot.DISTANCE = int(self.get_distance())
        if 1 < dtrobot.DISTANCE < 255:
            print(dtrobot.DISTANCE)
            dtrobot.DISTANCE_INFO = bytes([0x03, 0x04, dtrobot.DISTANCE]) 	# 将超声波距离值上传到上位机
        else:
            dtrobot.DISTANCE_INFO = []

    def maze(self):
        """
        超声波走迷宫函数
        """
        dtrobot.LEFT_SPEED = 35
        dtrobot.RIGHT_SPEED = 35
        # print("超声波走迷宫函数")
        self.dis = self.get_distance()		# 获取距离值
        if self.MAZE_ABLE == 0 and ((self.dis > 30) or self.dis == 0):  # 前方没有障碍物时候并且不是死胡同
            while ((self.dis > 30) or self.dis == 0) and dtrobot.ULTRASONIC_MODE == 3:
                self.dis = self.get_distance()
                motor.forward()
            if dtrobot.ULTRASONIC_MODE == 3:		# 在退出模式时不运行这个，避免退出模式后仍然不停车
                self.MAZE_CNT = self.MAZE_CNT+1
                print(self.MAZE_CNT)
                motor.stop()
                time.sleep(0.05)
                motor.back()		# 后退一点点
                time.sleep(0.15)
                motor.stop()
                time.sleep(0.05)
                if self.MAZE_CNT > 3:		# 多次检测前方是否为障碍物，避免误检测
                    self.MAZE_CNT = 0
                    self.MAZE_ABLE = 1		# 如果前面是胡同

        else:
            motor.stop()
            self.s_L = 0
            self.s_R = 0
            time.sleep(0.1)
            servo.set(7, 5)		# 先把超声波转动的舵机转到右边
            if dtrobot.ULTRASONIC_MODE == 3:
                time.sleep(0.25)
            self.s_R = self.get_distance()
            if dtrobot.ULTRASONIC_MODE == 3:
                time.sleep(0.2)

            servo.set(7, 175)		# 再把舵机转动到左边
            if dtrobot.ULTRASONIC_MODE == 3:
                time.sleep(0.3)
            self.s_L = self.get_distance()
            if dtrobot.ULTRASONIC_MODE == 3:
                time.sleep(0.2)
            servo.set(7, 80)		# 再把舵机转动到中间
            time.sleep(0.1)

            if (self.s_R == 0) or (self.s_R > self.s_L and self.s_R > 20): # 如果右边宽阔，并且障碍物距离大于20，并且右侧大于左侧
                self.MAZE_ABLE = 0
                dtrobot.LEFT_SPEED = 99		# 转向速度，如果在不同得地面需要实际手动调节其速度满足转向力度，这里是地毯上的速度需要高点
                dtrobot.RIGHT_SPEED = 99
                motor.right()
                if dtrobot.ULTRASONIC_MODE == 3:
                    time.sleep(dtrobot.MAZE_TURN_TIME/1000)			# 转向的时间，根据上面转向的速度调节，实测转到90度左右即可
                dtrobot.LEFT_SPEED = 45
                dtrobot.RIGHT_SPEED = 45

            elif (self.s_L == 0) or (self.s_R < self.s_L and self.s_L > 20): 		# 如果左边宽阔，并且障碍物距离大于20，并且左侧大于右侧
                self.MAZE_ABLE = 0
                dtrobot.LEFT_SPEED = 99  	# 转向速度，如果在不同得地面需要实际手动调节其速度满足转向力度，这里是地毯上的速度需要高点
                dtrobot.RIGHT_SPEED = 99
                motor.left()
                if dtrobot.ULTRASONIC_MODE == 3:
                    time.sleep(dtrobot.MAZE_TURN_TIME/1000)		# 转向的时间，根据上面转向的速度调节，实测转到90度左右即可
                dtrobot.LEFT_SPEED = 45
                dtrobot.RIGHT_SPEED = 45

            else: 	# 前方不能走，左右都不能走，即进入了死胡同，只能原路返回
                self.MAZE_ABLE = 1 		# 把标志置1，避免又重复进入死胡同，只能一点点后退再左右检测是否有其他通道，当左右通道任意一方畅通时标志位置0，才可往前进
                motor.back()
                if dtrobot.ULTRASONIC_MODE == 3:
                    time.sleep(0.3)

        motor.stop()
        time.sleep(0.1)
    
    def ultrasonic_mode_info(self):
        while True:
            if len(dtrobot.ULTRASONIC_INFO):
                if(dtrobot.ULTRASONIC_INFO[0] == 0x03):
                    if dtrobot.ULTRASONIC_INFO[1] == 0x00:
                        dtrobot.ULTRASONIC_MODE = 0
                    elif dtrobot.ULTRASONIC_INFO[1] == 0x01:
                        dtrobot.ULTRASONIC_MODE = 1
                    elif dtrobot.ULTRASONIC_INFO[1] == 0x02:
                        dtrobot.ULTRASONIC_MODE = 2
                    elif dtrobot.ULTRASONIC_INFO[1] == 0x03:
                        dtrobot.ULTRASONIC_MODE = 3
                    else:
                        dtrobot.ULTRASONIC_MODE = 0
                dtrobot.ULTRASONIC_INFO = []

    def dtrobot_ultrasonic(self):
        threads = []
        t_mode_info = threading.Thread(target = self.ultrasonic_mode_info, args = ())
        threads.append(t_mode_info)
        for t in threads:
            t.setDaemon(True)
            t.start()
            time.sleep(0.05)

        while True:
            if dtrobot.ULTRASONIC_MODE == 1:
                self.send_distance()
            elif dtrobot.ULTRASONIC_MODE == 2:
                self.avoidbyragar()
            elif dtrobot.ULTRASONIC_MODE == 3:
                self.maze()