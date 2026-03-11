#coding: utf-8

import pytest
from pytdx.errors import TdxFunctionCallError, TdxConnectionError
from collections import OrderedDict
import pandas as pd
import socket
from pytdx.exhq import TdxExHq_API, TDXParams
from pytdx.params import TDXParams as Params


class Log(object):
    def info(self, *args):
        pass


log = Log()


def test_all_functions(exhq_api):
    api = exhq_api

    symbol_params = [
        [47, "IF1709"],
        [8, "10000889"],
        [31, "00020"],
        [47, "IFL0"],
        [31, "00700"]
    ]

    log.info("获取市场代码")
    data = api.get_markets()
    assert data is not None
    assert type(data) is list
    assert len(data) > 0

    log.info("查询市场中商品数量")
    data = api.get_instrument_count()
    assert data is not None
    assert data > 0

    log.info("查询五档行情")
    for params in symbol_params:
        data = api.get_instrument_quote(*params)

        assert data is not None
        assert type(data) is list
        assert len(data) > 0

    # log.info("查询分时行情")
    for params in symbol_params:
        data = api.get_minute_time_data(*params)
        assert data is not None
        assert type(data) is list
        assert len(data) >= 0

    log.info("查询历史分时行情")
    for params in symbol_params:
        data = api.get_history_minute_time_data(
            params[0], params[1], 20170811)
        assert data is not None
        assert type(data) is list
        assert len(data) >= 0

    log.info("查询分时成交")
    for params in symbol_params:
        data = api.get_transaction_data(*params)
        assert data is not None
        assert type(data) is list
        assert len(data) >= 0

    log.info("查询历史分时成交")
    for params in symbol_params:
        data = api.get_history_transaction_data(
            params[0], params[1], 20170811)
        assert data is not None
        assert type(data) is list
        assert len(data) >= 0

    log.info("查询k线")
    for params in symbol_params:
        data = api.get_instrument_bars(
            TDXParams.KLINE_TYPE_DAILY, params[0], params[1])
        assert data is not None
        assert type(data) is list
        assert len(data) >= 0

    log.info("查询代码列表")
    data = api.get_instrument_info(10000, 98)
    assert data is not None
    assert type(data) is list
    assert len(data) > 0


def test_future_and_index_functions(exhq_api):
    api = exhq_api

    log.info("验证常量定义")
    assert Params.MARKET_EX_CZCE == 28
    assert Params.MARKET_EX_DCE == 29
    assert Params.MARKET_EX_SHFE == 30
    assert Params.MARKET_EX_CFFEX == 47
    assert Params.MARKET_EX_ZZ_INDEX == 62
    assert Params.MARKET_EX_GZ_INDEX == 102
    assert Params.EX_CATEGORY_FUTURES == 3
    assert Params.EX_CATEGORY_INDEX == 5

    log.info("获取期货行情列表")
    data = api.get_future_quote_list(Params.MARKET_EX_DCE)
    if data is None:
        pytest.skip("服务器不支持 get_instrument_quote_list 接口")
    assert type(data) is list
    assert len(data) > 0

    log.info("获取期货K线")
    data = api.get_future_bars(Params.MARKET_EX_CFFEX, "IF1709")
    assert data is not None
    assert type(data) is list

    log.info("获取扩展指数K线")
    data = api.get_ex_index_bars(Params.MARKET_EX_ZZ_INDEX, "000905")
    assert data is not None
    assert type(data) is list

    log.info("获取期货合约列表")
    data = api.get_future_contracts(Params.MARKET_EX_CFFEX)
    assert data is not None
    assert type(data) is list


def test_get_history_instrument_bars_range(exhq_api):
    api = exhq_api

    log.info("查询代码列表")
    data = api.get_history_instrument_bars_range(
        74, "BABA", 20170613, 20170620)
    assert data is not None
    assert type(data) is list
    assert len(data) > 0
