import yfinance as yf
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA  # 使用内置的 SMA 函数

# --- 1. 获取数据 ---
symbol = "NVDA" # 英伟达
data = yf.download(symbol, start="2022-01-01", end="2024-01-01")

# 处理列名的多层索引问题
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# 处理时区问题（防止报错）
if data.index.tz is not None:
    data.index = data.index.tz_localize(None)

# --- 2. 定义策略 ---
class SmaCross(Strategy):
    # 定义两个参数，方便后续优化
    n1 = 10 # 短期均线
    n2 = 20 # 长期均线
    n3 = 200 # 长期趋势均线（过滤条件）

    def init(self):
        # init() 只运行一次，用于计算指标
        # 使用 backtesting 库提供的 SMA 函数
        price = self.data.Close
        self.ma1 = self.I(SMA, price, self.n1)
        self.ma2 = self.I(SMA, price, self.n2)
        self.ma200 = self.I(SMA, price, self.n3)  # 200日均线

    def next(self):
        # next() 会针对每一根K线运行一次，模拟真实交易
        price = self.data.Close[-1]  # 当前价格
        
        # 如果 ma1 上穿 ma2 (金叉) 且价格在 200 日均线之上
        if crossover(self.ma1, self.ma2) and price > self.ma200[-1]:
            self.buy() # 全仓买入

        # 如果 ma1 下穿 ma2 (死叉)
        elif crossover(self.ma2, self.ma1):
            self.position.close() # 清仓卖出

# --- 3. 运行回测 ---
# cash: 初始资金, commission: 手续费 (0.002 = 0.2%)
bt = Backtest(data, SmaCross, cash=10000, commission=.002)

stats = bt.run() # 开始运行
print(stats)     # 打印详细的统计报告

# --- 4. 画图 ---
# 这会在浏览器中打开一个交互式网页
bt.plot()