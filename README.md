# pytdx — Python 通达信数据接口

纯 Python 实现的通达信行情数据接口，支持标准行情（沪深A股）和扩展行情（期货/港股/外盘/指数）。

## 安装

```bash
pip install pytdx
```

## 快速开始

```python
from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams

api = TdxHq_API()
with api.connect('180.153.18.170', 7709):
    # 实时行情
    quotes = api.get_security_quotes([(0, '000001'), (1, '600300')])
    print(api.to_df(quotes))

    # 日K线
    bars = api.get_security_bars(TDXParams.KLINE_TYPE_RI_K, 0, '000001', 0, 100)
    print(api.to_df(bars))
```

```python
from pytdx.exhq import TdxExHq_API
from pytdx.params import TDXParams

api = TdxExHq_API()
with api.connect('112.74.214.43', 7727):
    # 期货行情
    data = api.get_future_quote_list(TDXParams.MARKET_EX_DCE)
    print(api.to_df(data))
```

## 特性

- 纯 Python，无需 `.dll/.so`
- 支持 Python 3.5+，全平台 (Windows / macOS / Linux)
- 线程安全接口（`multithread=True`）
- 心跳包保持长连接（`heartbeat=True`）
- 自动重连策略（`auto_retry=True`）
- 连接池与 failover 支持（`pytdx.pool`）

---

## API 参考

### 常量 `pytdx.params.TDXParams`

#### 标准行情市场

| 常量 | 值 | 说明 |
|------|----|------|
| `MARKET_SZ` | 0 | 深圳 |
| `MARKET_SH` | 1 | 上海 |
| `MARKET_BJ` | 2 | 北京（北交所），`get_security_list` 不可用，行情/K线正常 |

#### 扩展行情 — 期货市场

| 常量 | 值 | 说明 |
|------|----|------|
| `MARKET_EX_CZCE` | 28 | 郑商所 |
| `MARKET_EX_DCE` | 29 | 大商所 |
| `MARKET_EX_SHFE` | 30 | 上期所 |
| `MARKET_EX_CFFEX` | 47 | 中金所 |

#### 扩展行情 — 指数市场

| 常量 | 值 | 说明 |
|------|----|------|
| `MARKET_EX_HK_INDEX` | 27 | 香港指数 |
| `MARKET_EX_GLOBAL_INDEX` | 37 | 全球指数 |
| `MARKET_EX_ZZ_INDEX` | 62 | 中证指数 |
| `MARKET_EX_GZ_INDEX` | 102 | 国证指数 |

#### 扩展行情品类

| 常量 | 值 | 说明 |
|------|----|------|
| `EX_CATEGORY_HK` | 2 | 港股 |
| `EX_CATEGORY_FUTURES` | 3 | 期货 |
| `EX_CATEGORY_INDEX` | 5 | 指数 |

#### K线类型

| 常量 | 值 | 说明 |
|------|----|------|
| `KLINE_TYPE_5MIN` | 0 | 5分钟 |
| `KLINE_TYPE_15MIN` | 1 | 15分钟 |
| `KLINE_TYPE_30MIN` | 2 | 30分钟 |
| `KLINE_TYPE_1HOUR` | 3 | 1小时 |
| `KLINE_TYPE_DAILY` | 4 | 日K |
| `KLINE_TYPE_WEEKLY` | 5 | 周K |
| `KLINE_TYPE_MONTHLY` | 6 | 月K |
| `KLINE_TYPE_EXHQ_1MIN` | 7 | 1分钟(扩展行情) |
| `KLINE_TYPE_1MIN` | 8 | 1分钟 |
| `KLINE_TYPE_RI_K` | 9 | 日K(备选) |
| `KLINE_TYPE_3MONTH` | 10 | 季K |
| `KLINE_TYPE_YEARLY` | 11 | 年K |

#### 板块文件

| 常量 | 值 | 说明 |
|------|----|------|
| `BLOCK_DEFAULT` | `block.dat` | 默认板块 |
| `BLOCK_GN` | `block_gn.dat` | 概念板块 |
| `BLOCK_FG` | `block_fg.dat` | 风格板块 |
| `BLOCK_SZ` | `block_zs.dat` | 指数板块 |

---

### 通用方法（HQ / ExHQ 共有）

| 方法 | 说明 |
|------|------|
| `connect(ip, port, time_out=5)` | 连接服务器，支持 `with` 上下文管理 |
| `disconnect()` | 断开连接 |
| `to_df(data)` | 将返回数据转为 pandas DataFrame |
| `get_traffic_stats()` | 获取网络流量统计 |

---

### 标准行情 `pytdx.hq.TdxHq_API`

用于获取沪深A股数据，默认端口 7709。

```python
api = TdxHq_API(multithread=False, heartbeat=False, auto_retry=False, raise_exception=False)
```

#### 实时行情

| 方法 | 说明 |
|------|------|
| `get_security_quotes([(market, code), ...])` | 获取实时行情，支持批量。也支持 `get_security_quotes(market, code)` 和 `get_security_quotes((market, code))` |
| `get_security_count(market)` | 获取市场证券总数 |
| `get_security_list(market, start)` | 获取证券列表（分页，每次约1000条） |

#### K线数据

| 方法 | 说明 |
|------|------|
| `get_security_bars(category, market, code, start, count)` | 获取证券K线，count 最大 800 |
| `get_index_bars(category, market, code, start, count)` | 获取指数K线 |
| `get_k_data(code, start_date, end_date)` | 便捷方法，按日期范围获取日K，返回 DataFrame |

#### 分时 / 分笔

| 方法 | 说明 |
|------|------|
| `get_minute_time_data(market, code)` | 获取当日分时数据 |
| `get_history_minute_time_data(market, code, date)` | 获取历史分时数据，date 格式 `20161209` |
| `get_transaction_data(market, code, start, count)` | 获取当日分笔成交，count 最大 2000 |
| `get_history_transaction_data(market, code, start, count, date)` | 获取历史分笔成交 |

#### 基本面

| 方法 | 说明 |
|------|------|
| `get_company_info_category(market, code)` | 获取公司信息目录 |
| `get_company_info_content(market, code, filename, start, length)` | 获取公司信息内容 |
| `get_xdxr_info(market, code)` | 获取除权除息信息 |
| `get_finance_info(market, code)` | 获取财务信息 |

#### 板块数据

| 方法 | 说明 |
|------|------|
| `get_and_parse_block_info(blockfile, result_type=None)` | 获取并解析板块文件。`result_type` 可选 `BlockReader_TYPE_FLAT`(默认) 或 `BlockReader_TYPE_GROUP` |
| `get_block_sector_list(blockfile)` | 获取板块列表（按板块分组），返回含 blockname / stock_count / code_list 的列表 |
| `get_concept_sector_list()` | 获取概念板块列表（解析 `block_gn.dat`） |
| `get_concept_sector_stocks(sector_name)` | 获取指定概念板块的成分股代码列表 |
| `get_index_list(market=None)` | 获取指数列表（从 `block_zs.dat`），可按市场过滤 |
| `get_index_quotes(index_list)` | 批量获取指数实时行情，参数格式 `[(market, code), ...]` |

#### 文件下载

| 方法 | 说明 |
|------|------|
| `get_report_file(filename, offset)` | 获取报告文件内容 |
| `get_report_file_by_size(filename, filesize, reporthook)` | 按大小下载文件，支持进度回调 |

---

### 扩展行情 `pytdx.exhq.TdxExHq_API`

用于获取期货、港股、外盘、扩展指数等数据，默认端口 7727。

```python
api = TdxExHq_API(multithread=False, heartbeat=False, auto_retry=False, raise_exception=False)
```

#### 市场与合约

| 方法 | 说明 |
|------|------|
| `get_markets()` | 获取所有可用市场列表 |
| `get_instrument_count()` | 获取合约/品种总数 |
| `get_instrument_info(start, count=100)` | 获取合约信息（分页） |
| `get_instrument_quote(market, code)` | 获取单个合约实时五档行情 |
| `get_instrument_quote_list(market, category, start, count)` | 获取指定市场和品类的行情列表 |

#### K线数据

| 方法 | 说明 |
|------|------|
| `get_instrument_bars(category, market, code, start, count)` | 获取合约K线数据 |
| `get_history_instrument_bars_range(market, code, start_date, end_date)` | 按日期范围获取K线 |

#### 分时 / 分笔

| 方法 | 说明 |
|------|------|
| `get_minute_time_data(market, code)` | 获取当日分时数据 |
| `get_history_minute_time_data(market, code, date)` | 获取历史分时数据 |
| `get_transaction_data(market, code, start, count)` | 获取当日分笔成交 |
| `get_history_transaction_data(market, code, date, start, count)` | 获取历史分笔成交 |

#### 期货便捷方法

| 方法 | 说明 |
|------|------|
| `get_future_contracts(market)` | 获取指定交易所全部合约信息（遍历 `get_instrument_info` 按 market 过滤） |
| `get_future_quote_list(market, start, count)` | 获取期货行情列表（自动使用品类 3） |
| `get_future_bars(market, code, category, start, count)` | 获取期货K线（market 参数在前） |
| `get_ex_index_bars(market, code, category, start, count)` | 获取扩展指数K线（中证/国证等） |

---

### 数据文件读取 `pytdx.reader`

用于直接读取通达信客户端本地数据文件，无需连接服务器。

| 类 | 说明 |
|----|------|
| `TdxDailyBarReader` | 读取日线文件（`.day`），支持按 code+exchange 或文件路径 |
| `TdxMinBarReader` | 读取分钟线文件（`.lc1` / `.lc5`） |
| `TdxLCMinBarReader` | 读取 LC 格式分钟线文件 |
| `TdxExHqDailyBarReader` | 读取扩展行情日线文件 |
| `BlockReader` | 读取板块文件（`block*.dat`） |
| `CustomerBlockReader` | 读取自定义板块文件夹 |
| `GbbqReader` | 读取股本变迁文件 |
| `HistoryFinancialReader` | 读取历史财务数据文件（`.zip` / `.dat`） |

所有 Reader 均提供 `get_df(fname)` 方法返回 DataFrame。

---

### 历史财务数据爬取 `pytdx.crawler`

| 类/方法 | 说明 |
|---------|------|
| `HistoryFinancialListCrawler().fetch_and_parse()` | 获取财务数据文件列表 |

---

## 命令行工具

| 命令 | 说明 |
|------|------|
| `hqget` | 交互式行情数据获取，支持选择服务器和功能 |
| `hqreader` | 本地数据文件读取 |
| `hqbenchmark` | 服务器性能测试 |
| `hqsample` | 随机抽样行情测试（见下文） |

### hqsample 用法

```bash
hqsample                                  # 默认：深市随机5只，日K+5分钟+1分钟
hqsample -m 1 -n 3                        # 上海市场随机3只
hqsample -s 180.153.18.170:7709           # 指定服务器
hqsample --kline 4,0,8 --kline-count 10   # 指定K线类型和条数
hqsample --all-kline                       # 全部12种K线
hqsample --quote-only                      # 只看实时行情
hqsample --kline-only                      # 只看K线
```

---

## 服务器列表与延迟测试

> 测试时间：2026-03-11，测试方法：连接后依次调用 quotes / security_list / bars / index_bars / block_info 接口验证。

### HQ 标准行情服务器 (端口 7709)

103 个服务器去重后，38 个可连接。所有可连接服务器的功能表现一致：`quotes`/`bars`/`index_bars`/`block_info` 正常，`security_list` 全部 OK。

> 注意：`get_security_list(1, 0)`（上海市场 start=0）在部分服务器返回 None，属于服务器端数据空洞，改用 `get_security_list(0, 0)` 或 `get_security_list(1, 1000)` 即可正常获取。

按延迟排序：

| 名称 | IP | 端口 | 延迟 |
|------|----|------|------|
| 上海电信主站Z1 | 180.153.18.170 | 7709 | 110ms |
| 上海电信主站Z80 | 180.153.18.172 | 80 | 129ms |
| 杭州电信主站J4 | 115.238.90.165 | 7709 | 152ms |
| 杭州联通主站J2 | 60.12.136.250 | 7709 | 155ms |
| 华林 | 218.106.92.183 | 7709 | 166ms |
| 杭州电信主站J1 | 60.191.117.167 | 7709 | 169ms |
| 华林 | 220.178.55.71 | 7709 | 171ms |
| 华林 | 220.178.55.86 | 7709 | 171ms |
| 海通 | 182.118.47.151 | 7709 | 177ms |
| 杭州电信主站J3 | 218.75.126.9 | 7709 | 201ms |
| 国泰君安 | 117.34.114.14 | 7709 | 213ms |
| 国泰君安 | 117.34.114.17 | 7709 | 213ms |
| 国泰君安 | 117.34.114.15 | 7709 | 217ms |
| 北京联通主站Z80 | 202.108.253.139 | 80 | 219ms |
| 国泰君安 | 117.34.114.18 | 7709 | 221ms |
| 国泰君安 | 117.34.114.16 | 7709 | 224ms |
| 海通 | 58.63.254.191 | 7709 | 226ms |
| 国泰君安 | 117.34.114.27 | 7709 | 239ms |
| 杭州电信主站J2 | 115.238.56.198 | 7709 | 240ms |
| 广发 | 183.60.224.177 | 7709 | 240ms |
| 上证云北京联通一 | 123.125.108.14 | 7709 | 242ms |
| 国信 | 58.63.254.247 | 7709 | 244ms |
| 华林 | 218.106.92.182 | 7709 | 247ms |
| 国泰君安 | 117.34.114.13 | 7709 | 249ms |
| 海通 | 182.131.3.245 | 7709 | 249ms |
| 国泰君安 | 117.34.114.20 | 7709 | 258ms |
| 海通 | 58.63.254.217 | 7709 | 259ms |
| 海通 | 175.6.5.153 | 7709 | 260ms |
| 海通 | 123.125.108.90 | 7709 | 271ms |
| 上证云成都电信一 | 218.6.170.47 | 7709 | 279ms |
| 华林 | 202.96.138.90 | 7709 | 279ms |
| 广发 | 119.29.19.242 | 7709 | 289ms |
| 国信 | 182.131.3.252 | 7709 | 295ms |
| 国泰君安 | 117.34.114.30 | 7709 | 301ms |
| 广发 | 183.60.224.178 | 7709 | 336ms |
| 安信 | 59.36.5.11 | 7709 | 341ms |
| 海通 | 202.100.166.27 | 7709 | 357ms |
| 国泰君安 | 117.34.114.31 | 7709 | 396ms |

### ExHQ 扩展行情服务器 (端口 7727)

10 个服务器中仅 1 个可连接，但数据接口均返回 None。

| 名称 | IP | 端口 | 延迟 | 状态 |
|------|----|------|------|------|
| 扩展市场深圳双线1 | 112.74.214.43 | 7727 | 109ms | 连接OK，数据接口无响应 |
| 扩展市场上海双线 | 106.14.95.149 | 7727 | — | 连接失败 |
| 扩展市场深圳主站 | 119.147.86.171 | 7727 | — | 连接失败 |
| 扩展市场武汉主站1 | 119.97.185.5 | 7727 | — | 连接失败 |
| 扩展市场深圳双线2 | 120.24.0.77 | 7727 | — | 连接失败 |
| 扩展市场北京主站 | 47.92.127.181 | 7727 | — | 连接失败 |
| 扩展市场武汉主站3 | 59.175.238.38 | 7727 | — | 连接失败 |
| 扩展市场上海主站1 | 61.152.107.141 | 7727 | — | 连接失败 |
| 扩展市场上海主站2 | 61.152.107.171 | 7727 | — | 连接失败 |
| 扩展市场深圳双线3 | 47.107.75.159 | 7727 | — | 连接失败 |

> 服务器可用性随时间和网络环境变化，建议使用 `pytdx.util.best_ip` 自动选择最优服务器。

---

## 声明

此代码用于个人对网络协议的研究和学习，不对外提供服务。连接的是既有行情软件兼容服务器，使用者自行承担风险。
