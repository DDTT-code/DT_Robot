#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

import os
import re
import signal
import shutil

class Reset():
    def __init__(self):
        self.program_name = "dtrobot_main.py"
        self.src_path = "/home/pi/dt_robot/back_up"
        self.dest_path = "/home/pi/dt_robot/python_src"
    
    def reset(self):
        order_str = "ps -aux | grep %s" % self.program_name

        strs_obj = os.popen(order_str)
        t_strs = strs_obj.read()

        pid_lists = re.findall("(\d+).+python dtrobot_main.py", t_strs, re.I)

        for i in pid_lists:
            print(int(i))
            os.kill(int(i), signal.SIGKILL)

        src_files = os.listdir(self.src_path)
        dest_files = os.listdir(self.dest_path)
        for i in src_files:
            for j in dest_files:
                if i == j:
                    os.remove(self.dest_path + '/' + j)
            shutil.move(self.src_path +'/' + i, self.dest_path + '/' + i)

        os.system('python dtrobot_main.py')