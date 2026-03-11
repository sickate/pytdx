# coding=utf-8
"""
测试公共 fixtures —— 自动轮询 IP 池找到可用服务器

不仅检查连接是否成功，还验证数据接口是否正常返回数据，
确保找到的服务器真正可用。
"""

import socket
import pytest
from pytdx.hq import TdxHq_API
from pytdx.exhq import TdxExHq_API
from pytdx.config.hosts import hq_hosts


# 扩展行情服务器列表
exhq_hosts = [
    ('扩展市场上海双线', '106.14.95.149', 7727),
    ('扩展市场深圳双线1', '112.74.214.43', 7727),
    ('扩展市场深圳主站', '119.147.86.171', 7727),
    ('扩展市场武汉主站1', '119.97.185.5', 7727),
    ('扩展市场深圳双线2', '120.24.0.77', 7727),
    ('扩展市场北京主站', '47.92.127.181', 7727),
    ('扩展市场武汉主站3', '59.175.238.38', 7727),
    ('扩展市场上海主站1', '61.152.107.141', 7727),
    ('扩展市场上海主站2', '61.152.107.171', 7727),
    ('扩展市场深圳双线3', '47.107.75.159', 7727),
]


def _find_hq_server(timeout=8):
    """轮询标准行情服务器，连接后验证数据接口可用"""
    for name, ip, port in hq_hosts:
        api = TdxHq_API()
        try:
            r = api.connect(ip, port, time_out=timeout)
            if r:
                # 验证关键接口: get_security_quotes 和 get_security_list
                quotes = api.get_security_quotes([(0, "000001")])
                slist = api.get_security_list(0, 0)  # 用深圳market=0验证，上海start=0可能为空
                api.disconnect()
                if quotes and slist:
                    return ip, port, name
        except Exception:
            try:
                api.disconnect()
            except Exception:
                pass
    return None, None, None


def _find_exhq_server(timeout=8):
    """轮询扩展行情服务器，连接后验证数据接口可用"""
    for name, ip, port in exhq_hosts:
        api = TdxExHq_API()
        try:
            r = api.connect(ip, port, time_out=timeout)
            if r:
                # 验证多个关键接口都能返回数据
                markets = api.get_markets()
                count = api.get_instrument_count()
                info = api.get_instrument_info(0, 10)
                api.disconnect()
                if markets and count and count > 0 and info:
                    return ip, port, name
        except Exception:
            try:
                api.disconnect()
            except Exception:
                pass
    return None, None, None


# 模块级缓存，避免每个测试都轮询
_hq_server_cache = None
_exhq_server_cache = None


@pytest.fixture(scope="session")
def hq_server():
    """Session 级 fixture：返回可用的标准行情服务器 (ip, port)，找不到则 skip"""
    global _hq_server_cache
    if _hq_server_cache is None:
        ip, port, name = _find_hq_server()
        if ip is None:
            pytest.skip("无法连接任何标准行情服务器（或所有服务器数据接口不可用）")
        print(f"\n使用标准行情服务器: {name} ({ip}:{port})")
        _hq_server_cache = (ip, port)
    return _hq_server_cache


@pytest.fixture(scope="session")
def exhq_server():
    """Session 级 fixture：返回可用的扩展行情服务器 (ip, port)，找不到则 skip"""
    global _exhq_server_cache
    if _exhq_server_cache is None:
        ip, port, name = _find_exhq_server()
        if ip is None:
            pytest.skip("无法连接任何扩展行情服务器（或所有服务器数据接口不可用）")
        print(f"\n使用扩展行情服务器: {name} ({ip}:{port})")
        _exhq_server_cache = (ip, port)
    return _exhq_server_cache


@pytest.fixture
def hq_api(hq_server):
    """返回已连接的 TdxHq_API 实例，测试结束后自动断开"""
    ip, port = hq_server
    api = TdxHq_API()
    r = api.connect(ip, port, time_out=30)
    if not r:
        pytest.skip(f"连接 {ip}:{port} 失败")
    yield api
    api.disconnect()


@pytest.fixture
def exhq_api(exhq_server):
    """返回已连接的 TdxExHq_API 实例，测试结束后自动断开"""
    ip, port = exhq_server
    api = TdxExHq_API(auto_retry=True)
    r = api.connect(ip, port, time_out=30)
    if not r:
        pytest.skip(f"连接 {ip}:{port} 失败")
    yield api
    api.disconnect()
