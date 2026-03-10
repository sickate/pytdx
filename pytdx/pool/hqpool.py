# utf-8
from pytdx.log import DEBUG, log
from functools import partial
import threading
import time


## 调用单个接口，重试次数，超过次数则不再重试
## round-robin 模式下 N 连接 × 3 轮足够覆盖瞬态故障
DEFAULT_API_CALL_MAX_RETRY_TIMES = 6
## 重试间隔的休眠时间
DEFAULT_API_RETRY_INTERVAL = 0.2

class TdxHqApiCallMaxRetryTimesReachedException(Exception):
    pass

class TdxHqPool_API(object):
    """
    N 连接 round-robin 负载均衡连接池

    - apis[0..N-1] 为活跃连接，round-robin 轮流分发请求
    - IP Pool 提供候选 IP 用于故障替换
    - 向后兼容: pool_size=2 时行为与原来 1 主 1 备一致
    """

    def __init__(self, hq_cls, ippool, pool_size=2):
        self.hq_cls = hq_cls
        self.ippool = ippool
        self.pool_size = pool_size

        # N 个活跃连接
        self.apis = [hq_cls(multithread=True, heartbeat=True) for _ in range(pool_size)]
        # round-robin 计数器
        self._rr_index = 0
        self._lock = threading.Lock()

        self.api_call_max_retry_times = DEFAULT_API_CALL_MAX_RETRY_TIMES
        self.api_retry_interval = DEFAULT_API_RETRY_INTERVAL

        # 对hq_cls 里面的get_系列函数进行反射
        log.debug("perform_reflect")
        self.perform_reflect(self.apis[0])

    def perform_reflect(self, api_obj):
        # ref : https://stackoverflow.com/questions/34439/finding-what-methods-an-object-has
        method_names = [attr for attr in dir(api_obj) if callable(getattr(api_obj, attr))]
        for method_name in method_names:
            log.debug("testing attr %s" % method_name)
            if method_name[:3] == 'get' or method_name == "do_heartbeat" or method_name == 'to_df':
                log.debug("set refletion to method: %s", method_name)
                _do_hp_api_call = partial(self.do_hq_api_call, method_name)
                setattr(self, method_name, _do_hp_api_call)

    def _next_api(self):
        """Round-robin 选取下一个连接"""
        with self._lock:
            api = self.apis[self._rr_index % len(self.apis)]
            self._rr_index += 1
        return api

    def do_hq_api_call(self, method_name, *args, **kwargs):
        """带 failover 的 round-robin 调用

        - None 结果: 轮转到下一个连接重试（不替换连接）
        - Exception: 替换失败连接后轮转重试
        - 最多重试 api_call_max_retry_times 次
        """
        for retry in range(self.api_call_max_retry_times):
            api = self._next_api()
            try:
                result = getattr(api, method_name)(*args, **kwargs)
                if result is not None:
                    return result
                log.info("api(%s) call return None on %s (retry %d)" % (method_name, api.ip, retry))
            except Exception as e:
                log.info("api(%s) call failed on %s: %s (retry %d)" % (method_name, api.ip, str(e), retry))
                # 只在异常时替换连接
                self._replace_failed_api(api)

            # 短暂等待后重试
            time.sleep(self.api_retry_interval)

        raise TdxHqApiCallMaxRetryTimesReachedException(
            "(method_name=%s) max retry times(%d) reached" % (method_name, self.api_call_max_retry_times))

    def _replace_failed_api(self, failed_api):
        """替换失败的连接"""
        try:
            idx = self.apis.index(failed_api)
        except ValueError:
            # 已经被替换过了
            return

        failed_ip = failed_api.ip
        failed_api.disconnect()

        # 从 IP 池获取新 IP（排除已在使用的）
        used_ips = {a.ip for a in self.apis}
        new_ips = self.ippool.get_ips()
        for ip_tuple in new_ips:
            if ip_tuple[0] in used_ips:
                continue
            new_api = self.hq_cls(multithread=True, heartbeat=True)
            try:
                new_api.connect(*ip_tuple)
                self.apis[idx] = new_api
                log.info("replaced failed api %s with %s" % (failed_ip, ip_tuple[0]))
                return
            except Exception:
                new_api.disconnect()
        log.warning("no available IP to replace failed api %s" % failed_ip)

    def connect(self, *ip_port_pairs):
        """连接所有活跃连接

        接受 N 个 (ip, port) 元组，N = pool_size
        向后兼容: 也接受 connect(primary, backup) 的旧调用方式
        """
        self.ippool.setup()
        for i, ip_port in enumerate(ip_port_pairs):
            if i >= len(self.apis):
                break
            log.debug("connecting api[%d] to %s" % (i, str(ip_port)))
            self.apis[i].connect(*ip_port)
        return self

    def disconnect(self):
        for i, api in enumerate(self.apis):
            log.debug("disconnecting api[%d]" % i)
            api.disconnect()
        self.ippool.teardown()

    def close(self):
        """
        disconnect的别名，为了支持 with closing(obj): 语法
        :return:
        """
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':

    from pytdx.hq import TdxHq_API
    from pytdx.pool.ippool import AvailableIPPool
    from pytdx.config.hosts import hq_hosts
    import random
    import logging
    import pprint
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    log.addHandler(ch)

    ips = [(v[1], v[2]) for v in hq_hosts]

    # 获取5个随机ip作为ip池
    random.shuffle(ips)
    ips5 = ips[:5]

    ippool = AvailableIPPool(TdxHq_API, ips5)

    primary_ip, hot_backup_ip = ippool.sync_get_top_n(2)

    print("make pool api")
    api = TdxHqPool_API(TdxHq_API, ippool)
    print("make pool api done")
    print("send api call to primary ip %s, %s" % (str(primary_ip), str(hot_backup_ip)))
    with api.connect(primary_ip, hot_backup_ip):
        ret = api.get_xdxr_info(0, '000001')
        print("send api call done")
        pprint.pprint(ret)
