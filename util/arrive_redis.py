#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import pickle
import json
import threading
import time
from arrive_redis_config import *


class RedisHelper(object):
    '''
    Redis通信基类-接口规范
    '''

    def __init__(self, sub_obj=None, auto_init=False, sub_thread_init=False, sub_channel=CHANNEL_NAME_CMD,
                 encode_type="pickle"):
        # redis初始化
        self._redis = None  # connect()
        self.sub_obj = self if sub_obj is None else sub_obj
        self.encode_type = encode_type
        # ****************************************
        if auto_init:  # 自动初始化
            self.set_redis_obj()
            if sub_thread_init:  # 自动订阅
                self.sub_msg(sub_channel)
        # ****************************************
        print("RedisHelper init sucessed.")

    def set_redis_obj(self):
        if self._redis:
            return
        try:
            self.pool = redis.ConnectionPool(host=HOST, port=PORT)
            self._redis = redis.Redis(connection_pool=self.pool)
            self.pubsub = self._redis.pubsub()
        except Exception as e:
            print('Redis connection failed, error message%s' % e)

    def sub_msg(self, channel=CHANNEL_NAME_CMD):
        self.pubsub.subscribe(**{channel: self.sub_cb})
        self.pubsub.run_in_thread(sleep_time=0.001, daemon=True)

    def sub_cb(self, message):
        try:
            if message:
                try:
                    data = json.loads(message['data'])
                except:
                    data = pickle.loads(message['data'])
                # 反射机制
                fun = getattr(self.sub_obj, data["fun"], None)
                if fun:
                    if not "async" not in data or data["async"]:
                        # 线程并发、异步函数
                        t = threading.Thread(target=fun, args=[data["data"]])
                        t.setDaemon(True)
                        t.start()
                    else:
                        fun(data)
                else:
                    pass
                    # print("sub_cb(): {}".format(fun))
        except Exception:
            print("[redis] sub_cb: {}".format(Exception) )

    def pub_msg(self, fun=None, data=None, channel=CHANNEL_NAME_CMD, async_arg=True, encode_type="pickle"):
        '''
        发命令 - 采用反射机制,通过cmd调用对应方法
        '''
        if data is None:
            data = {}
        message_data = copy.deepcopy(MESSAGE_DATA)
        message_data["time"] = time.time()
        message_data["fun"] = fun
        message_data["async"] = async_arg
        message_data["data"] = data
        if encode_type == "json":
            message = json.dumps(message_data)
        else:
            message = pickle.dumps(message_data)

        self._redis.publish(channel, message)
        return message_data

    def str_get(self, k, encode_type="pickle"):
        '''
        根据key，获取string类型数据
        '''
        res = self._redis.get(k)
        if res:
            try:
                return json.loads(res.decode())
            except:
                return pickle.loads(res.decode())
        else:
            return None

    def str_set(self, k, v, t_time=None, encode_type="pickle"):
        '''
        存string类型数据
        '''
        type_ = self._redis.type(k)
        if not (type_ == "string" or type_ == "none"):
            return
        data = json.dumps(v) if encode_type == "json" else pickle.dumps(v)
        self._redis.set(k, data, t_time)

    def delete(self, k):
        '''
        根据key，删除string类型数据
        '''
        tag = self._redis.exists(k)
        if tag:
            self._redis.delete(k)
        else:
            print('dThis key does not exist.')

    def list_lpush(self, name, v, encode_type="pickle"):
        '''
            在name列表的头部插入值value
        '''
        type_ = self._redis.type(name)
        if not (type_ == "list" or type_ == "none"):
            return
        data = json.dumps(v) if encode_type == "json" else pickle.dumps(v)
        self._redis.lpush(name, data)

    def list_rpop(self, name, encode_type="pickle"):
        '''
            移除name列表最后一个元素并返回
        '''
        type_ = self._redis.type(name)
        if not (type_ == "list" or type_ == "none"):
            return
        res = self._redis.rpop(name)
        if res:
            try:
                return json.loads(res.decode())
            except:
                return pickle.loads(res.decode())
        else:
            return None

    def hash_hget(self, name, key, encode_type="pickle"):
        '''
        由name及key，获取string类型数据
        '''
        res = self._redis.hget(name, key)
        if res:
            try:
                return json.loads(res.decode())
            except:
                return pickle.loads(res.decode())
        else:
            return None

    def hash_hset(self, name, k, v, encode_type="pickle"):
        '''
        由name及key，设置hash类型数据
        '''
        type_ = self._redis.type(name)
        if not (type_ == "hash" or type_ == "none"):
            return
        data = json.dumps(v) if encode_type == "json" else pickle.dumps(v)
        self._redis.hset(name, k, data)

    def hash_getall(self, name, encode_type="pickle"):
        '''
        由name，获取hash类型数据
        '''
        res = self._redis.hgetall(name)
        new_dict = {}
        if res:
            for k, v in res.items():
                k = k.decode()
                try:
                    v = json.loads(v.decode())
                except:
                    v = pickle.loads(v)
                new_dict[k] = v
        return new_dict

    def hash_del(self, name, k):
        '''
        由name及key，删除hash类型数据
        '''
        res = self._redis.hdel(name, k)
        if res:
            return True
        else:
            print('This key does not exist.')
            return False

    def set_hset(self, name, v, encode_type="pickle"):
        '''
        存set类型数据
        '''
        type_ = self._redis.type(name)
        if not (type_ == "set" or type_ == "none"):
            return
        data = json.dumps(v) if encode_type == "json" else pickle.dumps(v)
        self._redis.sadd(name, data)

    def set_getall(self, name, encode_type="pickle"):
        '''
        获取set类型数据
        '''
        res = self._redis.smembers(name)
        new_set = []
        if res:
            for v in res:
                try:
                    v = json.loads(v.decode())
                except:
                    v = pickle.loads(v.decode())
                new_set.append(v)
        return new_set

    def set_del(self, name, v):
        '''
        删除set类型数据
        '''
        res = self._redis.srem(name, v)
        if res:
            return True
        else:
            print('This key does not exist.')
            return False

    def set_del_by_find(self, keys):
        '''
        按（关键字）模糊查询
        '''
        if not keys:
            return
        pre_keys = self._redis.keys(str(keys) + "*")
        mid_keys = self._redis.keys("*" + str(keys) + "*")
        suf_keys = self._redis.keys("*" + str(keys))
        list_keys = list(set(pre_keys + mid_keys + suf_keys))
        for key in list_keys:
            self._redis.delete(key)

    def clean_up_redis(self):
        self._redis.flushdb()  # 清空redis
        # self.pubsub.unsubscribe()
        print('Clear redis successfully.')
        return 0

    @property
    def clean_redis(self):
        self._redis.flushdb()  # 清空redis
        # self.pubsub.unsubscribe()
        print('Clear redis successfully.')
        return 0
