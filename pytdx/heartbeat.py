# coding=utf-8

from threading import Thread
from pytdx.log import DEBUG, log
import time

# 参考 :https://stackoverflow.com/questions/6524459/stopping-a-thread-after-a-certain-amount-of-time


DEFAULT_HEARTBEAT_INTERVAL = 10.0 # 10秒一个heartbeat

class HqHeartBeatThread(Thread):

    def __init__(self, api, stop_event, heartbeat_interval=DEFAULT_HEARTBEAT_INTERVAL):
        self.api = api
        self.stop_event = stop_event
        self.heartbeat_interval = heartbeat_interval
        super(HqHeartBeatThread, self).__init__(daemon=True)

    def run(self):
        while not self.stop_event.is_set():
            self.stop_event.wait(self.heartbeat_interval)
            if self.stop_event.is_set():
                break
            if self.api.client and (time.time() - self.api.last_ack_time > self.heartbeat_interval):
                try:
                    # 发送一个获取股票数量的包作为心跳包
                    self.api.do_heartbeat()
                except Exception as e:
                    log.debug(str(e))
