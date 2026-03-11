# coding=utf-8

#
# Just for practising
#


import os
import socket
import sys
import pandas as pd

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pytdx.log import DEBUG, log
from pytdx.parser.ex_setup_commands import ExSetupCmd1
from pytdx.parser.ex_get_markets import GetMarkets
from pytdx.parser.ex_get_instrument_count import GetInstrumentCount
from pytdx.parser.ex_get_instrument_quote import GetInstrumentQuote
from pytdx.parser.ex_get_minute_time_data import GetMinuteTimeData
from pytdx.parser.ex_get_history_minute_time_data import GetHistoryMinuteTimeData
from pytdx.parser.ex_get_transaction_data import GetTransactionData
from pytdx.parser.ex_get_history_transaction_data import GetHistoryTransactionData
from pytdx.parser.ex_get_instrument_bars import GetInstrumentBars
from pytdx.parser.ex_get_instrument_info import GetInstrumentInfo
from pytdx.parser.ex_get_history_instrument_bars_range import GetHistoryInstrumentBarsRange
from pytdx.parser.ex_get_instrument_quote_list import GetInstrumentQuoteList


from pytdx.params import TDXParams

import threading
import datetime
from pytdx.base_socket_client import BaseSocketClient, update_last_ack_time


"""
In [7]: 0x7e
Out[7]: 126

In [5]: len(body)
Out[5]: 8066

In [6]: len(body)/126
Out[6]: 64.01587301587301

In [7]: len(body)%126
Out[7]: 2

In [8]: (len(body)-2)/126
Out[8]: 64.0
"""


class TdxExHq_API(BaseSocketClient):

    def setup(self):
        ExSetupCmd1(self.client).call_api()

    # API LIST

    @update_last_ack_time
    def get_markets(self):
        cmd = GetMarkets(self.client)
        return cmd.call_api()

    @update_last_ack_time
    def get_instrument_count(self):
        cmd = GetInstrumentCount(self.client)
        return cmd.call_api()

    @update_last_ack_time
    def get_instrument_quote(self, market, code):
        cmd = GetInstrumentQuote(self.client)
        cmd.setParams(market, code)
        return cmd.call_api()

    @update_last_ack_time
    def get_instrument_bars(self, category, market, code, start=0, count=700):
        cmd = GetInstrumentBars(self.client)
        cmd.setParams(category, market, code, start=start, count=count)
        return cmd.call_api()

    @update_last_ack_time
    def get_minute_time_data(self, market, code):
        cmd = GetMinuteTimeData(self.client)
        cmd.setParams(market, code)
        return cmd.call_api()

    @update_last_ack_time
    def get_history_minute_time_data(self, market, code, date):
        cmd = GetHistoryMinuteTimeData(self.client)
        cmd.setParams(market, code, date=date)
        return cmd.call_api()

    @update_last_ack_time
    def get_transaction_data(self, market, code, start=0, count=1800):
        cmd = GetTransactionData(self.client)
        cmd.setParams(market, code, start=start, count=count)
        return cmd.call_api()

    @update_last_ack_time
    def get_history_transaction_data(self, market, code, date, start=0, count=1800):
        cmd = GetHistoryTransactionData(self.client)
        cmd.setParams(market, code, date, start=start, count=count)
        return cmd.call_api()

    @update_last_ack_time
    def get_history_instrument_bars_range(self, market, code, start, end):
        cmd = GetHistoryInstrumentBarsRange(self.client)
        cmd.setParams(market, code, start, end)
        return cmd.call_api()

    @update_last_ack_time
    def get_instrument_info(self, start, count=100):
        cmd = GetInstrumentInfo(self.client)
        cmd.setParams(start, count)
        return cmd.call_api()

    @update_last_ack_time
    def get_instrument_quote_list(self, market, category, start=0, count=80):
        cmd = GetInstrumentQuoteList(self.client)
        cmd.setParams(market, category, start, count)
        return cmd.call_api()

    def get_future_contracts(self, market):
        """获取指定期货交易所的全部合约信息

        遍历 get_instrument_info 按 market 过滤

        :param market: 期货市场代码 (如 TDXParams.MARKET_EX_CZCE=28, MARKET_EX_DCE=29 等)
        :return: 该交易所全部合约信息列表
        """
        result = []
        start = 0
        count = 100
        while True:
            data = self.get_instrument_info(start, count)
            if data is None or len(data) == 0:
                break
            for item in data:
                if item.get('market') == market:
                    result.append(item)
            start += count
            if len(data) < count:
                break
        return result

    def get_future_quote_list(self, market, start=0, count=80):
        """获取期货市场行情列表

        封装 get_instrument_quote_list，自动使用期货品类(3)

        :param market: 期货市场代码
        :param start: 起始位置
        :param count: 获取数量
        :return: 行情列表
        """
        return self.get_instrument_quote_list(market, TDXParams.EX_CATEGORY_FUTURES, start, count)

    def get_future_bars(self, market, code, category=TDXParams.KLINE_TYPE_DAILY, start=0, count=700):
        """获取期货K线数据

        封装 get_instrument_bars，market 参数在前更直观

        :param market: 期货市场代码
        :param code: 合约代码
        :param category: K线类型，默认日K
        :param start: 起始位置
        :param count: 获取数量
        :return: K线数据列表
        """
        return self.get_instrument_bars(category, market, code, start, count)

    def get_ex_index_bars(self, market, code, category=TDXParams.KLINE_TYPE_DAILY, start=0, count=700):
        """获取扩展行情指数K线数据（中证指数、国证指数等）

        :param market: 指数市场代码 (如 TDXParams.MARKET_EX_ZZ_INDEX=62, MARKET_EX_GZ_INDEX=102)
        :param code: 指数代码
        :param category: K线类型，默认日K
        :param start: 起始位置
        :param count: 获取数量
        :return: K线数据列表
        """
        return self.get_instrument_bars(category, market, code, start, count)

    def do_heartbeat(self):
        self.get_instrument_count()


if __name__ == '__main__':
    import pprint

    api = TdxExHq_API()
    with api.connect('121.14.110.210', 7727):
        # log.info("获取市场代码")
        # pprint.pprint(api.to_df(api.get_markets()))
        # log.info("查询市场中商品数量")
        # pprint.pprint(api.get_instrument_count())
        # log.info("查询五档行情")
        #pprint.pprint(api.to_df(api.get_instrument_quote(47, "IF1709")))
        #pprint.pprint(api.get_instrument_quote(8, "10000889"))
        #pprint.pprint(api.get_instrument_quote(31, "00020"))
        # log.info("查询分时行情")
        #api.get_minute_time_data(47, "IFL0")
        #pprint.pprint(api.to_df(api.get_minute_time_data(47, "IFL0")))
        #pprint.pprint(api.to_df(api.get_minute_time_data(8, "10000889")).tail())
        #pprint.pprint(api.get_minute_time_data(31, "00020"))
        log.info("查询历史分时行情")
        pprint.pprint(api.to_df(api.get_history_minute_time_data(31, "00020", 20170811)).tail())
        log.info("查询分时成交")
        pprint.pprint(api.to_df(api.get_transaction_data(31, "00020")).tail())

        log.info("查询历史分时成交")
        pprint.pprint(api.to_df(api.get_history_transaction_data(31, "00020", 20170811)).tail())
        #data = api.get_history_minute_time_data(47, 'IFL0', 20170811)
        # pprint.pprint(data)

        # log.info("查询k线")
        #pprint.pprint(api.to_df(api.get_instrument_bars(TDXParams.KLINE_TYPE_DAILY, 8, "10000843")))
        #pprint.pprint(api.to_df(api.get_instrument_bars(TDXParams.KLINE_TYPE_DAILY, 31, "00700")))
        # log.info("查询代码列表")
        #pprint.pprint(api.to_df(api.get_instrument_info(10000, 98)))
