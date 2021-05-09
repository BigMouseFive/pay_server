#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis
import os


def getEnv(key, default_value):
    value = os.getenv(key)
    if value is None:
        value = default_value
    else:
        if type(default_value) == bool:
            if value == "true" or value == "True":
                value = True
            else:
                value = False
        else:
            value = type(default_value)(value)
    print("Param " + key + "=" + str(value))
    return value


# Redis 配置参数
HOST = getEnv("ARRIVEAI_REDIS_HOST", "127.0.0.1")
PORT = getEnv("ARRIVEAI_REDIS_PORT", 6379)

CHANNEL_NAME_CMD = "op_global_planner_in"
# 数据/命令格式
MESSAGE_DATA = {  # 注意,使用该dict前,请完成深度拷贝: message_data = copy.deepcopy(MESSAGE_DATA)
    "time": None,
    "cmd": None,  # 命令: 采用反射机制调用函数。为了方便, 此时函数名可与cmd值一致
    "async": True,  # 是否开启异步模式处理当前任务
    "data": {},  # 通过多层字典统区别不同类型的数据状态. 如: {"plan":{}, "cmd_vel":{}, "status":{}, "battery":{} }
}


def connect(host=HOST, port=PORT):
    return redis.Redis(host=host, port=port)
