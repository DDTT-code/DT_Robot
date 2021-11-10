#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

import cv2
import base64
import time
import math
import threading
from PIL import Image
from io import BytesIO
import pyzbar.pyzbar as pyzbar
import dtrobot_config as dtrobot
from dtrobot_servo import Servo
from dtrobot_motor import Motor

servo = Servo()
motor = Motor()

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
    
    def linepatrol_processing(self):
        while True:
            if self.cap_open == 0:  # 摄像头没有打开
                try:
                    self.cap = cv2.VideoCapture(0)
                    self.cap_open = 1  # 标志置1
                    self.cap.set(3, 320)  # 设置图像的宽为320像素
                    self.cap.set(4, 320)  # 设置图像的高为320像素
                except Exception as e:
                    print('opencv camera open error:', e)
                    break
            else:
                try:
                    ret, frame = self.cap.read()  # 获取摄像头帧数据
                    if ret:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将RGB转换成GRAY颜色空间
                        if dtrobot.PATH_DECT_FLAG == 0:
                            ret, thresh1 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)  # 巡黑色线
                        else:
                            ret, thresh1 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)  # 巡白色线
                        for j in range(0, 640, 5):  # X轴方向横向采样，采样点间隔5个像素
                            if thresh1[350, j] == 0:  # 取图像y轴中间偏上值350，对采样点进行二值化判断
                                self.px_sum = self.px_sum + j  # 将符合线颜色的采样点x坐标累计相加
                                self.fre_count = self.fre_count + 1  # 将采样数量累计
                        dtrobot.LINE_POINT_ONE = self.px_sum / self.fre_count  # 用x坐标累计值/采样数量=符合线颜色坐标点平均值，相当于线x坐标实际位置点
                        self.px_sum = 0  # 清除累计值
                        self.fre_count = 1  # 清除采样数量最低为1
                        for j in range(0, 640, 5):  # X轴方向横向采样，采样点间隔5个像素
                            if thresh1[200, j] == 0:  # 取图像y轴中间偏下值200，对采样点进行二值化判断
                                self.px_sum = self.px_sum + j  # 将符合线颜色的采样点x坐标累计相加
                                self.fre_count = self.fre_count + 1  # 将采样数量累计
                        dtrobot.LINE_POINT_TWO = self.px_sum / self.fre_count  # 用x坐标累计值/采样数量=符合线颜色坐标点平均值，相当于线x坐标实际位置点
                        self.px_sum = 0  # 清除累计值
                        self.fre_count = 1  # 清除采样数量最低为1
                        print("point1 = %d ,point2 = %d"%(motor.LINE_POINT_ONE, motor.LINE_POINT_TWO))
                except Exception as e:  # 捕获并打印出错信息
                    motor.stop()  # 退出,停止小车
                    self.cap_open = 0  # 关闭标志
                    self.cap.release()  # 释放摄像头
                    print('linepatrol_processing error:', e)

            if self.cap_open == 1 and dtrobot.CAMERA_MODE != 4:  # 如果退出巡线模式
                motor.stop()  # 退出巡线,停止小车
                self.cap_open = 0  # 关闭标志
                self.cap.release()  # 释放摄像头
                break  # 退出循环

    def color_follow(self):
        while True:
            if self.cap_open == 0:  # 摄像头没有打开
                try:
                    self.cap = cv2.VideoCapture(0)
                    self.cap_open = 1  # 标志置1
                    self.cap.set(3, 320)  # 设置图像的宽为320像素
                    self.cap.set(4, 320)  # 设置图像的高为320像素
                except Exception as e:
                    print('opencv camera open error:', e)
                    break
            else:
                try:
                    ret, frame = self.cap.read()  # 获取摄像头视频流
                    if ret == 1:  # 判断摄像头是否工作
                        frame = cv2.GaussianBlur(frame, (5, 5), 0)  # 高斯滤波GaussianBlur() 让图片模糊
                        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # 将图片的色域转换为HSV的样式 以便检测
                        mask = cv2.inRange(hsv, dtrobot.COLOR_LOWER[dtrobot.COLOR_INDEX],
                                           dtrobot.COLOR_UPPER[dtrobot.COLOR_INDEX])  # 设置阈值，去除背景 保留所设置的颜色

                        mask = cv2.erode(mask, None, iterations=2)  # 显示腐蚀后的图像
                        mask = cv2.GaussianBlur(mask, (3, 3), 0)  # 高斯模糊
                        res = cv2.bitwise_and(frame, frame, mask=mask)  # 图像合并

                        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # 边缘检测

                        if len(cnts) > 0:  # 通过边缘检测来确定所识别物体的位置信息得到相对坐标
                            cnt = max(cnts, key=cv2.contourArea)
                            (x, y), radius = cv2.minEnclosingCircle(cnt)
                            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 255), 2)  # 画出一个圆
                            # print(int(x), int(y))

                            self.X_pid.update(x)  # 将X轴数据放入pid中计算输出值
                            self.Y_pid.update(y)  # 将Y轴数据放入pid中计算输出值
                            # print("X_pid.output==%d"%X_pid.output)		#打印X输出
                            # print("Y_pid.output==%d"%Y_pid.output)		#打印Y输出
                            self.angle_X = math.ceil(
                                self.angle_X + 1 * self.X_pid.output)  # 更新X轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度
                            self.angle_Y = math.ceil(
                                self.angle_Y + 0.8 * self.Y_pid.output)  # 更新Y轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度
                            # print("angle_X-----%d" % self.angle_X)	#打印X轴舵机角度
                            # print("angle_Y-----%d" % self.angle_Y)	#打印Y轴舵机角度
                            if self.angle_X > 180:  # 限制X轴最大角度
                                self.angle_X = 180
                            if self.angle_X < 0:  # 限制X轴最小角度
                                self.angle_X = 0
                            if self.angle_Y > 180:  # 限制Y轴最大角度
                                self.angle_Y = 180
                            if self.angle_Y < 0:  # 限制Y轴最小角度
                                self.angle_Y = 0
                            servo.set(self.servo_X, self.angle_X)  # 设置X轴舵机
                            servo.set(self.servo_Y, self.angle_Y)  # 设置Y轴舵机
                except Exception as e:  # 捕获并打印出错信息
                    motor.stop()  # 退出,停止小车
                    self.cap_open = 0  # 关闭标志
                    self.cap.release()  # 释放摄像头
                    print('color_follow error:', e)

            if self.cap_open == 1 and dtrobot.CAMERA_MODE != 3:  # 如果退出摄像头颜色检测跟随模式
                motor.stop()  # 退出,停止小车
                self.cap_open = 0  # 关闭标志
                self.cap.release()  # 释放摄像头
                break  # 退出循环
    
    def decodeDisplay(self, image):
        """
        二维码识别
        :param image:摄像头数据帧
        :return:image 识别后的图像数据帧
        """
        barcodes = pyzbar.decode(image)
        if barcodes == []:
            dtrobot.BARCODE_DATE = None
            dtrobot.BARCODE_TYPE = None
        else:
            for barcode in barcodes:
                # 提取条形码的边界框的位置
                # 画出图像中条形码的边界框
                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # 条形码数据为字节对象，所以如果我们想在输出图像上
                # 画出来，就需要先将它转换成字符串
                dtrobot.BARCODE_DATE = barcode.data.decode("utf-8")
                dtrobot.BARCODE_TYPE = barcode.type

                # 绘出图像上条形码的数据和条形码类型
                text = "{} ({})".format(dtrobot.BARCODE_DATE, dtrobot.BARCODE_TYPE)
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            .5, (0, 0, 125), 2)

                # 向终端打印条形码数据和条形码类型
                print("[INFO] Found {} barcode: {}".format(dtrobot.BARCODE_TYPE, dtrobot.BARCODE_DATE))
        return image
    
    def qrcode_detection(self):
        while True:
            if self.cap_open == 0:  # 摄像头没有打开
                try:
                    self.cap = cv2.VideoCapture(0)
                    self.cap_open = 1  # 标志置1
                    self.cap.set(3, 320)  # 设置图像的宽为320像素
                    self.cap.set(4, 320)  # 设置图像的高为320像素
                except Exception as e:
                            print('opencv camera open error:', e)
                            break
            else:
                try:
                    ret, frame = self.cap.read()  # 获取摄像头视频流
                    if ret == 1:  # 判断摄像头是否工作
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转为灰度图像
                        img = self.decodeDisplay(gray)  # 识别二维码
                    dtrobot.CAMERA_INFO = self.frame2base64(img)
                except Exception as e:  # 捕获并打印出错信息
                    motor.stop()  # 退出,停止小车
                    self.cap_open = 0  # 关闭标志
                    self.cap.release()  # 释放摄像头
                    print('qrcode_detection error:', e)

            if self.cap_open == 1 and dtrobot.CAMERA_MODE != 2:  # 如果退出摄像头二维码检测模式
                motor.stop()  # 退出,停止小车
                self.cap_open = 0  # 关闭标志
                self.cap.release()  # 释放摄像头
                break  # 退出循环
    
    def face_detection(self):
        time.sleep(3)
        while True:
            if self.cap_open == 0:  # 摄像头没有打开
                try:
                    self.cap = cv2.VideoCapture(0)
                    self.cap_open = 1  # 标志置1
                    self.cap.set(3, 320)  # 设置图像的宽为320像素
                    self.cap.set(4, 320)  # 设置图像的高为320像素
                    face_cascade = cv2.CascadeClassifier('/home/pi/dt_robot/Code/face.xml')  # 人脸识别OpenCV级联检测器，也可以换成其他特征识别器，比如鼻子的
                except Exception as e:
                    print('opencv camera open error:', e)
                    break
            else:
                try:
                    ret, frame = self.cap.read()  # 获取摄像头视频流
                    if ret == 1:  # 判断摄像头是否工作
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 要先将每一帧先转换成灰度图，在灰度图中进行查找
                        faces = face_cascade.detectMultiScale(gray)  # 查找人脸
                        if len(faces) > 0:  # 当视频中有人脸轮廓时
                            print('face found!')
                            for (x, y, w, h) in faces:
                                # 参数分别是“目标帧”，“矩形”，“矩形大小”，“线条颜色”，“宽度”
                                cv2.rectangle(frame, (x, y), (x + h, y + w), (0, 255, 0), 2)
                                result = (x, y, w, h)
                                x_middle = result[0] + w / 2  # x轴中心
                                y_middle = result[1] + h / 2  # y轴中心

                                self.X_pid.update(x_middle)  # 将X轴数据放入pid中计算输出值
                                self.Y_pid.update(y_middle)  # 将Y轴数据放入pid中计算输出值
                                print("X_pid.output==%d"%self.X_pid.output)     #打印X输出
                                print("Y_pid.output==%d"%self.Y_pid.output)     #打印Y输出
                                self.angle_X = math.ceil(self.angle_X + 1 * self.X_pid.output)  # 更新X轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度
                                self.angle_Y = math.ceil(self.angle_Y + 0.8 * self.Y_pid.output)  # 更新Y轴的舵机角度，用上一次的舵机角度加上一定比例的增量值取整更新舵机角度
                                print("angle_X-----%d" % self.angle_X)  #打印X轴舵机角度
                                print("angle_Y-----%d" % self.angle_Y)  #打印Y轴舵机角度
                                if self.angle_X > 180:  # 限制X轴最大角度
                                    self.angle_X = 180
                                if self.angle_X < 0:  # 限制X轴最小角度
                                    self.angle_X = 0
                                if self.angle_Y > 180:  # 限制Y轴最大角度
                                    self.angle_Y = 180
                                if self.angle_Y < 0:  # 限制Y轴最小角度
                                    self.angle_Y = 0
                                servo.set(self.servo_X, self.angle_X)  # 设置X轴舵机
                                servo.set(self.servo_Y, self.angle_Y)  # 设置Y轴舵机
                    dtrobot.CAMERA_INFO = self.frame2base64(frame)
                except Exception as e:  # 捕获并打印出错信息
                    motor.stop()  # 退出,停止小车
                    self.cap_open = 0  # 关闭标志
                    self.cap.release()  # 释放摄像头
                    print('face_detection error:', e)

            if self.cap_open == 1 and dtrobot.CAMERA_MODE != 1:  # 如果退出人脸识别模式
                motor.stop()  # 退出,停止小车
                self.cap_open = 0  # 关闭标志
                self.cap.release()  # 释放摄像头
                time.sleep(2)
                break  # 退出循环

    def run_camera(self):
        while True:
            if self.cap_open == 0:
                try:
                    self.cap = cv2.VideoCapture(0)
                    self.cap.set(3, 320)
                    self.cap.set(4, 320)
                    self.cap_open = 1
                except Exception as e:
                    self.cap_open = 0
                    break
            else:
                try:
                    ret, frame = self.cap.read()
                    if ret == 1:
                        dtrobot.CAMERA_INFO = self.frame2base64(frame)
                except Exception as e:
                    self.cap_open = 0
                    self.cap.release()
            
            if self.cap_open == 1 and dtrobot.CAMERA_MODE != 0:
                self.cap_open = 0
                self.cap.release()
                break

    def camera_mode_info(self):
        while True:
            if len(dtrobot.CAMERA_MODE_INFO):
                if(dtrobot.CAMERA_MODE_INFO[0] == 0x05):
                    if dtrobot.CAMERA_MODE_INFO[1] == 0x00:
                        dtrobot.CAMERA_MODE = 0
                    elif dtrobot.CAMERA_MODE_INFO[1] == 0x01:
                        dtrobot.CAMERA_MODE = 1
                    elif dtrobot.CAMERA_MODE_INFO[1] == 0x02:
                        dtrobot.CAMERA_MODE = 2
                    elif dtrobot.CAMERA_MODE_INFO[1] == 0x03:
                        dtrobot.CAMERA_MODE = 3
                    elif dtrobot.CAMERA_MODE_INFO[1] == 0x04:
                        dtrobot.CAMERA_MODE = 4
                    else:
                        dtrobot.CAMERA_MODE = 0
                dtrobot.CAMERA_MODE_INFO = []
    
    def dtrobot_camera(self):
        servo.set(dtrobot.SERVO_CAMERA_X, dtrobot.SERVO_CAMERA_ANGLE_X)
        servo.set(dtrobot.SERVO_CAMERA_Y, dtrobot.SERVO_CAMERA_ANGLE_Y)
        threads = []
        t_mode_info = threading.Thread(target = self.camera_mode_info, args = ())
        threads.append(t_mode_info)
        for t in threads:
            t.setDaemon(True)
            t.start()
            time.sleep(0.05)

        while True:
            if dtrobot.CAMERA_MODE == 0:
                self.run_camera()
            elif dtrobot.CAMERA_MODE == 1:
                self.face_detection()
            elif dtrobot.CAMERA_MODE == 2:
                self.qrcode_detection()
            elif dtrobot.CAMERA_MODE == 3:
                self.color_follow()
            elif dtrobot.CAMERA_MODE == 4:
                self.linepatrol_processing()
            else:
                pass