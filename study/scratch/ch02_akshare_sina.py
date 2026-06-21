"""
第2章数据源修改：使用 akshare 替代 yfinance
参考 ch01 的成功经验，使用新浪财经源（stock_us_daily）而非东方财富源
"""

import os
import warnings
warnings.filterwarnings('ignore')

# 清空代理环境变量，确保直连国内数据源
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(k, None)
os.environ['NO_PROXY'] = '*'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import akshare as ak

# macOS 字体配置
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

print('环境就绪 ✓\n')

# ========== 下载苹果 AAPL 最近约 1 年的日线数据 ==========
print('正在下载苹果 AAPL 数据（新浪财经源）...')
aapl = ak.stock_us_daily(symbol='AAPL', adjust='qfq')

if len(aapl) == 0:
    print('❌ 下载失败，请检查网络')
    import sys
    sys.exit(0)

# 转换日期格式并设为索引
aapl['date'] = pd.to_datetime(aapl['date'])
aapl = aapl.set_index('date').sort_index()

# 取最近1年数据（约250个交易日）
aapl = aapl.tail(250)

# 列名首字母大写（与原教程保持一致）
aapl.columns = [c.capitalize() for c in aapl.columns]

print(f'数据形状（行=交易日，列=字段）：{aapl.shape}')
print('\n前 5 行：')
print(aapl.head())

print('\n各列含义速查：')
for col in ['Close', 'High', 'Low', 'Open', 'Volume']:
    if col in aapl.columns:
        print(f'  {col}')

# ========== 计算日收益率 ==========
df = aapl[['Close']].copy()
df['日收益率'] = df['Close'].pct_change()

print('\n最近 10 天的收盘价与日收益率：')
print(df.tail(10))

# 验证最后一天
row_today = df.iloc[-1]
row_yesterday = df.iloc[-2]
manual_r = (row_today['Close'] - row_yesterday['Close']) / row_yesterday['Close']
print(f"\n验证最后一天：手算 {manual_r:.4%}，pct_change {row_today['日收益率']:.4%}")

# ========== 小实验：三只股票波动对比 ==========
print('\n正在下载三只股票数据进行波动对比...')
tickers = {
    'AAPL': '苹果',
    'TSLA': '特斯拉',
    'NVDA': '英伟达',
}

all_rets = {}

for symbol, name in tickers.items():
    print(f'  下载 {name} ({symbol})...')
    data = ak.stock_us_daily(symbol=symbol, adjust='qfq')

    if len(data) == 0:
        print(f'    ✗ {name} 下载失败')
        continue

    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date').sort_index()
    data = data.tail(250)  # 最近1年
    data.columns = [c.capitalize() for c in data.columns]

    all_rets[name] = data['Close'].pct_change().dropna()
    print(f'    {name} ({symbol}): {len(all_rets[name])} 个交易日')

if len(all_rets) > 0:
    vol = pd.Series({name: s.std() for name, s in all_rets.items()}).sort_values(ascending=False)
    print('\n=== 日收益率波动（标准差，越大越猛）===')
    for name, v in vol.items():
        print(f'  {name}: {v:.3%}')

    print(f'\n在本实验设定下（1年日线），波动最大的是：{vol.index[0]}')
else:
    print('\n所有股票下载失败，请检查网络连接')

print('\n✓ 数据下载和分析完成！')
