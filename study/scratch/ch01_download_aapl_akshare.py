"""第 1 章「下载真实股票数据 AAPL」—— akshare 版（国内数据源，无雅虎限流）。

对应 notebook cell 34，原版用 yfinance，在国内常被雅虎限流。
本脚本改用 akshare 的新浪财经源 (`stock_us_daily`)，国内访问稳定。

与 notebook 版本的差异：
  1. 字体回退列表适配 macOS（原 notebook 用 SimHei 在 Mac 上报错）
  2. 数据源换成 akshare（东方财富源对部分网络不友好，改用新浪源更稳）
  3. `display(aapl.tail(5))` 是 Notebook 专用，脚本里换成 print
  4. 关闭系统代理直连国内站点（如果你的代理软件把国内流量也走了代理，
     会导致东方财富/新浪连接失败；脚本内主动清空代理环境变量）

运行（仓库根目录）：
    python study/scratch/ch01_download_aapl_akshare.py
"""

import os
import warnings
warnings.filterwarnings('ignore')   # 隐藏不影响学习的警告信息

# 清空代理环境变量，确保直连国内数据源（新浪财经）
# 你机器装了 Clash/Surge 等代理，默认会把国内流量也走代理，导致连不上东方财富/新浪
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(k, None)
os.environ['NO_PROXY'] = '*'

import pandas as pd
import matplotlib.pyplot as plt     # 画图
import akshare as ak                # 国内财经数据源

# 关键修复：字体回退列表，macOS 字体在前，SimHei（Windows）留最后
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 通过 akshare 新浪源下载 AAPL 全部历史日线（前复权）
# 新浪源返回全部历史数据，列名小写英文：date/open/high/low/close/volume
print('正在通过 akshare（新浪财经源）下载 AAPL 数据...')
aapl = ak.stock_us_daily(symbol='AAPL', adjust='qfq')

# 雅虎限流/网络异常时会返回空 DataFrame，给清晰提示而不是崩溃
if len(aapl) == 0:
    print('❌ 下载失败：未拿到任何数据。')
    print('   排查：1) 网络是否通  2) 代理是否拦截了国内站点  3) 稍后重试')
    import sys
    sys.exit(0)

# 整理：把 date 列设为 DatetimeIndex，只取最近 6 个月（与原 notebook 对齐）
aapl['date'] = pd.to_datetime(aapl['date'])
aapl = aapl.set_index('date').sort_index()
# 取最近约 6 个月（约 130 个交易日）
aapl = aapl.tail(130)
# 列名首字母大写，保持与原 notebook 一致（Open/High/Low/Close/Volume）
aapl.columns = [c.capitalize() for c in aapl.columns]

print('🎉 恭喜！你已经拿到真实股票数据')
print(f'   共 {len(aapl)} 个交易日')
print(f'   最新收盘价: ${aapl["Close"].iloc[-1]:.2f}')            # iloc[-1] = 最后一行
print(aapl.tail(5))   # 脚本环境用 print 替代 notebook 的 display()

# ========== 上图收盘价、下图成交量 ==========
fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True,       # 2行子图，横轴对齐
                         gridspec_kw={'height_ratios': [3, 1]})    # 上图占 3 份高度
axes[0].plot(aapl.index, aapl['Close'], color='tab:blue', linewidth=1.5)  # 折线：收盘价
axes[0].set_title('真实数据 · 苹果 AAPL 收盘价', fontsize=14)
axes[0].set_ylabel('美元')
axes[0].grid(True, alpha=0.3)

axes[1].bar(aapl.index, aapl['Volume'], width=0.8, color='gray', alpha=0.5)  # 柱状：成交量
axes[1].set_ylabel('成交量')
axes[1].set_xlabel('日期')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
