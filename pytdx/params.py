# coding=utf-8


class TDXParams:

    #市场

    MARKET_SZ = 0  # 深圳
    MARKET_SH = 1  # 上海
    MARKET_BJ = 2  # 北京（北交所）

    #K线种类
    # K 线种类
    # 0 -   5 分钟K 线
    # 1 -   15 分钟K 线
    # 2 -   30 分钟K 线
    # 3 -   1 小时K 线
    # 4 -   日K 线
    # 5 -   周K 线
    # 6 -   月K 线
    # 7 -   1 分钟
    # 8 -   1 分钟K 线
    # 9 -   日K 线
    # 10 -  季K 线
    # 11 -  年K 线

    KLINE_TYPE_5MIN = 0
    KLINE_TYPE_15MIN = 1
    KLINE_TYPE_30MIN = 2
    KLINE_TYPE_1HOUR = 3
    KLINE_TYPE_DAILY = 4
    KLINE_TYPE_WEEKLY = 5
    KLINE_TYPE_MONTHLY = 6
    KLINE_TYPE_EXHQ_1MIN = 7
    KLINE_TYPE_1MIN = 8
    KLINE_TYPE_RI_K = 9
    KLINE_TYPE_3MONTH = 10
    KLINE_TYPE_YEARLY = 11


    # ref : https://github.com/rainx/pytdx/issues/7
    # 分笔行情最多2000条
    MAX_TRANSACTION_COUNT = 2000
    # k先数据最多800条
    MAX_KLINE_COUNT = 800


    # 期货市场代码 (扩展行情)
    MARKET_EX_CZCE = 28     # 郑商所 (郑州商品)
    MARKET_EX_DCE = 29      # 大商所 (大连商品)
    MARKET_EX_SHFE = 30     # 上期所 (上海期货)
    MARKET_EX_CFFEX = 47    # 中金所 (股指期货)

    # 扩展行情指数市场
    MARKET_EX_HK_INDEX = 27    # 香港指数
    MARKET_EX_GLOBAL_INDEX = 37  # 全球指数
    MARKET_EX_ZZ_INDEX = 62    # 中证指数
    MARKET_EX_GZ_INDEX = 102   # 国证指数

    # 扩展行情品类 (用于 get_instrument_quote_list)
    EX_CATEGORY_HK = 2        # 港股
    EX_CATEGORY_FUTURES = 3    # 期货
    EX_CATEGORY_INDEX = 5      # 指数

    # 板块相关参数
    BLOCK_SZ = "block_zs.dat"
    BLOCK_FG = "block_fg.dat"
    BLOCK_GN = "block_gn.dat"
    BLOCK_DEFAULT = "block.dat"
