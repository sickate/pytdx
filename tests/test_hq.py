#coding: utf-8

from collections import OrderedDict

import pandas as pd
import pytest
from pytdx.errors import TdxConnectionError, TdxFunctionCallError
from pytdx.hq import TdxHq_API, TDXParams
import socket


class Log(object):
    def info(self, *args):
        pass


log = Log()


# 测试任意组合的选项
@pytest.mark.parametrize("multithread", [False])
@pytest.mark.parametrize("heartbeat", [False, True])
@pytest.mark.parametrize("auto_retry", [False, True])
@pytest.mark.parametrize("raise_exception", [False])
def test_all_functions(multithread, heartbeat, auto_retry, raise_exception, hq_server):

    ip, port = hq_server
    api = TdxHq_API(multithread=multithread, heartbeat=heartbeat,
                    auto_retry=auto_retry, raise_exception=raise_exception)
    with api.connect(ip=ip, port=port, time_out=60):
        log.info("获取股票行情")
        stocks = api.get_security_quotes([(0, "000001"), (1, "600300")])
        assert stocks is not None
        assert type(stocks) is list

        # 方法2
        stocks = api.get_security_quotes(0, "000001")
        assert stocks is not None
        assert type(stocks) is list

        # 方法3
        stocks = api.get_security_quotes((0, "000001"))
        assert stocks is not None
        assert type(stocks) is list

        log.info("获取k线")
        data = api.get_security_bars(9, 0, '000001', 4, 3)
        assert data is not None
        assert type(data) is list
        assert len(data) == 3

        log.info("获取 深市 股票数量")
        assert api.get_security_count(0) > 0

        log.info("获取股票列表")
        stocks = api.get_security_list(0, 0)  # 深圳market=0，上海start=0在部分服务器返回None
        assert stocks is not None
        assert type(stocks) is list
        assert len(stocks) > 0

        log.info("获取指数k线")
        data = api.get_index_bars(9, 1, '000001', 1, 2)
        assert data is not None
        assert type(data) is list
        assert len(data) == 2

        log.info("查询分时行情")
        data = api.get_minute_time_data(TDXParams.MARKET_SH, '600300')
        assert data is not None

        log.info("查询历史分时行情")
        data = api.get_history_minute_time_data(
            TDXParams.MARKET_SH, '600300', 20161209)
        assert data is not None
        assert type(data) is list
        assert len(data) > 0

        log.info("查询分时成交")
        data = api.get_transaction_data(TDXParams.MARKET_SZ, '000001', 0, 30)
        assert data is not None
        assert type(data) is list

        log.info("查询历史分时成交")
        data = api.get_history_transaction_data(
            TDXParams.MARKET_SZ, '000001', 0, 10, 20170209)

        assert data is not None
        assert type(data) is list
        assert len(data) == 10

        log.info("查询公司信息目录")
        data = api.get_company_info_category(TDXParams.MARKET_SZ, '000001')
        assert data is not None
        assert type(data) is list
        assert len(data) > 0

        start = data[0]['start']
        length = data[0]['length']
        log.info("读取公司信息-最新提示")
        data = api.get_company_info_content(
            0, '000001', '000001.txt', start, length)
        assert data is not None
        assert len(data) > 0

        log.info("读取除权除息信息")
        data = api.get_xdxr_info(1, '600300')
        assert data is not None
        assert type(data) is list
        assert len(data) > 0

        log.info("读取财务信息")
        data = api.get_finance_info(0, '000001')
        assert data is not None
        assert type(data) is OrderedDict
        assert len(data) > 0

        log.info("日线级别k线获取函数")
        data = api.get_k_data('000001', '2017-07-01', '2017-07-10')
        assert type(data) is pd.DataFrame
        assert len(data) == 6

        log.info("获取板块信息")
        data = api.get_and_parse_block_info(TDXParams.BLOCK_FG)
        assert data is not None
        assert type(data) is list
        assert len(data) > 0


def test_block_and_index_functions(hq_api):
    api = hq_api

    log.info("获取概念板块列表")
    data = api.get_concept_sector_list()
    assert data is not None
    assert type(data) is list
    assert len(data) > 0
    assert 'blockname' in data[0]
    assert 'stock_count' in data[0]
    assert 'code_list' in data[0]

    log.info("获取指定概念板块成分股")
    sector_name = data[0]['blockname']
    stocks = api.get_concept_sector_stocks(sector_name)
    assert type(stocks) is list
    assert len(stocks) > 0

    log.info("获取不存在的概念板块")
    stocks = api.get_concept_sector_stocks("不存在的板块名称_xyz")
    assert stocks == []

    log.info("获取通用板块列表")
    data = api.get_block_sector_list(TDXParams.BLOCK_FG)
    assert data is not None
    assert type(data) is list
    assert len(data) > 0

    log.info("获取指数列表")
    data = api.get_index_list()
    assert data is not None
    assert type(data) is list
    assert len(data) > 0

    log.info("按市场过滤指数列表")
    sh_indexes = api.get_index_list(market=TDXParams.MARKET_SH)
    assert type(sh_indexes) is list

    log.info("批量获取指数行情")
    data = api.get_index_quotes([(1, "000001"), (0, "399001")])
    assert data is not None
    assert type(data) is list
    assert len(data) == 2

    log.info("get_and_parse_block_info with result_type")
    from pytdx.reader.block_reader import BlockReader_TYPE_GROUP
    data = api.get_and_parse_block_info(TDXParams.BLOCK_GN, result_type=BlockReader_TYPE_GROUP)
    assert data is not None
    assert type(data) is list
    assert len(data) > 0
    assert 'stock_count' in data[0]


def test_raise_excepiton():
    api = TdxHq_API(raise_exception=True)
    with pytest.raises((socket.timeout, TdxConnectionError)):
        with api.connect('114.114.114.114'):
            pass
