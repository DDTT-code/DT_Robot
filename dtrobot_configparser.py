#!/usr/bin/env python
# coding=utf-8

__author__ = ''
__email__ = ''
__description__ = ''

from configparser import ConfigParser

class HandleConfig:
    """
    配置文件读写数据的封装
    """
    def __init__(self, filename):
        """
        :param filename: 配置文件名
        """
        self.filename = filename
        self.config = ConfigParser()        # 读取配置文件1.创建配置解析器
        self.config.read(self.filename, encoding="utf-8")   # 读取配置文件2.指定读取的配置文件

    def save_data(self, group, key, data):

        if not self.config.has_section(group):  # 判断section是否存在
            self.config.add_section(group)      # 不存在则添加
        self.config.set(group, key, str(data))  # 修改section
        with open(self.filename, "w") as file:  # 保存到哪个文件filename=需要指定文件名
            self.config.write(file)

    def get_data(self, group, key):
        data = self.get_value(group, key)  # 读取什么内容
        data = str(data)[1:-1].split(',')
        data = list(map(int, data))
        return data

    # get_value获取所有的字符串，section区域名, option选项名
    def get_value(self, section, option):
        return self.config.get(section, option)