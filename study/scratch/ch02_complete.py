"""
第2章完整演示脚本：你的第一个量化实验
对应 notebook: 02_你的第一个量化实验.ipynb

包含：
  2.1 股票数据介绍
  2.2 什么是收益率
  2.3 日收益率计算
  2.4 可视化收益率
  2.5 小实验：谁波动更大？

数据源：akshare 新浪财经源（替代原教程的 yfinance）
"""

import os
import warnings
warnings.filterwarnings('ignore')

# 清空代理环境变量
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    os.environ.pop(k, None)
os.environ['NO_PROXY'] = '*'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import akshare as ak

# 获取脚本所在目录，确保图片保存在正确位置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = SCRIPT_DIR  # 图片保存在 scratch 目录

plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

print('=' * 60)
print('第2章：你的第一个量化实验')
print('=' * 60)

# ========================================
# 2.1 股票数据介绍
# ========================================
print('\n【2.1 股票数据介绍】')
print('正在下载苹果 AAPL 数据...')

aapl = ak.stock_us_daily(symbol='AAPL', adjust='qfq')
if len(aapl) == 0:
    print('❌ 下载失败')
    import sys
    sys.exit(0)

aapl['date'] = pd.to_datetime(aapl['date'])
aapl = aapl.set_index('date').sort_index()
aapl = aapl.tail(250)  # 约1年数据
aapl.columns = [c.capitalize() for c in aapl.columns]

print(f'\n数据形状（行=交易日，列=字段）：{aapl.shape}')
print('\n前 5 行：')
print(aapl.head())
print('\n各列含义速查：')
for col in ['Close', 'High', 'Low', 'Open', 'Volume']:
    if col in aapl.columns:
        print(f'  {col}')

# 配图1：收盘价折线 + 成交量柱状图
fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True,
                         gridspec_kw={'height_ratios': [3, 1]})

axes[0].plot(aapl.index, aapl['Close'], color='tab:blue', linewidth=1.2, label='收盘价 Close')
axes[0].set_ylabel('价格 (美元)')
axes[0].set_title('苹果 AAPL：收盘价与成交量（真实行情）', fontsize=14)
axes[0].legend(loc='upper left')
axes[0].grid(True, alpha=0.3)

axes[1].bar(aapl.index, aapl['Volume'], width=0.8, color='gray', alpha=0.5, label='成交量 Volume')
axes[1].set_ylabel('股数')
axes[1].legend(loc='upper left')
axes[1].set_xlabel('日期')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
fig1_path = os.path.join(OUTPUT_DIR, 'ch02_fig1_price_volume.png')
plt.savefig(fig1_path, dpi=100)
print(f'\n✓ 图1已保存：{fig1_path}')
plt.close()

# 配图2：最近8天 OHLC 示意图
sample = aapl.tail(8).copy()
dates = range(len(sample))

fig, ax = plt.subplots(figsize=(12, 5))

for i, (idx, row) in enumerate(sample.iterrows()):
    o, h, l, c = row['Open'], row['High'], row['Low'], row['Close']
    color = 'tab:red' if c < o else 'tab:green'
    ax.vlines(i, l, h, color=color, linewidth=2, alpha=0.85)
    ax.hlines(o, i - 0.15, i + 0.15, color=color, linewidth=2)
    ax.hlines(c, i - 0.15, i + 0.15, color=color, linewidth=3)

ax.set_xticks(dates)
ax.set_xticklabels([d.strftime('%m-%d') for d in sample.index], rotation=45)
ax.set_ylabel('价格 (美元)')
ax.set_title('最近 8 个交易日：竖线 = High↔Low，短横线 = Open / Close（粗线=收盘）', fontsize=13)
ax.grid(True, axis='y', alpha=0.3)

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='tab:green', linewidth=2, label='收涨日 (Close ≥ Open)'),
    Line2D([0], [0], color='tab:red', linewidth=2, label='收跌日 (Close < Open)'),
]
ax.legend(handles=legend_elements, loc='upper left')
plt.tight_layout()
fig2_path = os.path.join(OUTPUT_DIR, 'ch02_fig2_ohlc.png')
plt.savefig(fig2_path, dpi=100)
print(f'✓ 图2已保存：{fig2_path}')
plt.close()

# ========================================
# 2.2 什么是收益率
# ========================================
print('\n【2.2 什么是收益率】')
p_yesterday, p_today = 100, 110
r = (p_today - p_yesterday) / p_yesterday
print(f'昨天: {p_yesterday} 元, 今天: {p_today} 元')
print(f'日收益率 r = {r:.2%}')

# ========================================
# 2.3 日收益率计算
# ========================================
print('\n【2.3 日收益率计算】')
df = aapl[['Close']].copy()
df['日收益率'] = df['Close'].pct_change()

print('最近 10 天的收盘价与日收益率：')
print(df.tail(10))

# 手算验证
row_today = df.iloc[-1]
row_yesterday = df.iloc[-2]
manual_r = (row_today['Close'] - row_yesterday['Close']) / row_yesterday['Close']
print(f"\n验证最后一天：手算 {manual_r:.4%}，pct_change {row_today['日收益率']:.4%}")

# ========================================
# 2.4 可视化收益率
# ========================================
print('\n【2.4 可视化收益率】')
rets = df['日收益率'].dropna()

# 图3：日收益率曲线 + 直方图
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].plot(rets.index, rets.values, color='steelblue', linewidth=0.9, alpha=0.85)
axes[0].axhline(0, color='black', linewidth=0.8, linestyle='--')
axes[0].set_title('苹果 AAPL：日收益率曲线', fontsize=13)
axes[0].set_xlabel('日期')
axes[0].set_ylabel('日收益率')
axes[0].grid(True, alpha=0.3)

axes[1].hist(rets.values, bins=40, color='steelblue', edgecolor='white', alpha=0.85)
axes[1].axvline(0, color='black', linewidth=0.8, linestyle='--')
axes[1].axvline(rets.mean(), color='orange', linewidth=2, label=f'平均值 {rets.mean():.2%}')
axes[1].set_title('日收益率分布（Histogram）', fontsize=13)
axes[1].set_xlabel('日收益率')
axes[1].set_ylabel('天数')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
fig3_path = os.path.join(OUTPUT_DIR, 'ch02_fig3_returns.png')
plt.savefig(fig3_path, dpi=100)
print(f'✓ 图3已保存：{fig3_path}')
plt.close()

print(f'\n样本天数: {len(rets)}')
print(f'平均日收益率: {rets.mean():.3%}（正=整体偏多涨）')
print(f'日收益率标准差: {rets.std():.3%}（越大=波动越剧烈）')

# 图4：累计收益率曲线
cum_return = (1 + rets).cumprod() - 1

plt.figure(figsize=(12, 4))
plt.plot(cum_return.index, cum_return.values * 100, color='tab:purple', linewidth=1.5)
plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
plt.title('苹果 AAPL：累计收益率曲线（%）', fontsize=14)
plt.xlabel('日期')
plt.ylabel('累计收益率 (%)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
fig4_path = os.path.join(OUTPUT_DIR, 'ch02_fig4_cumulative.png')
plt.savefig(fig4_path, dpi=100)
print(f'✓ 图4已保存：{fig4_path}')
plt.close()

print(f'这段区间累计涨跌: {cum_return.iloc[-1]:.2%}')

# ========================================
# 2.5 小实验：谁波动更大？
# ========================================
print('\n【2.5 小实验：谁波动更大？】')
print('正在下载三只股票数据...')

tickers = {
    'AAPL': '苹果',
    'TSLA': '特斯拉',
    'NVDA': '英伟达',
}

all_rets = {}

for symbol, name in tickers.items():
    data = ak.stock_us_daily(symbol=symbol, adjust='qfq')
    if len(data) == 0:
        print(f'  ✗ {name} 下载失败')
        continue
    data['date'] = pd.to_datetime(data['date'])
    data = data.set_index('date').sort_index()
    data = data.tail(250)
    data.columns = [c.capitalize() for c in data.columns]

    all_rets[name] = data['Close'].pct_change().dropna()
    print(f'{name} ({symbol}): {len(all_rets[name])} 个交易日')

vol = pd.Series({name: s.std() for name, s in all_rets.items()}).sort_values(ascending=False)
print('\n=== 日收益率波动（标准差，越大越猛）===')
for name, v in vol.items():
    print(f'  {name}: {v:.3%}')

# 图5：三只股票收益率对比
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colors = ['tab:blue', 'tab:orange', 'tab:green']

for (name, series), c in zip(all_rets.items(), colors):
    axes[0].plot(series.index, series.values, label=name, alpha=0.75, linewidth=0.8)
axes[0].axhline(0, color='black', linestyle='--', linewidth=0.6)
axes[0].set_title('日收益率对比', fontsize=13)
axes[0].set_xlabel('日期')
axes[0].set_ylabel('日收益率')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].bar(vol.index, vol.values * 100, color=colors[:len(vol)], edgecolor='white')
axes[1].set_title('波动大小对比（标准差 %）', fontsize=13)
axes[1].set_ylabel('标准差 (%)')
axes[1].grid(True, axis='y', alpha=0.3)
for i, v in enumerate(vol.values):
    axes[1].text(i, v * 100 + 0.02, f'{v:.2%}', ha='center', fontsize=11)

plt.tight_layout()
fig5_path = os.path.join(OUTPUT_DIR, 'ch02_fig5_comparison.png')
plt.savefig(fig5_path, dpi=100)
print(f'\n✓ 图5已保存：{fig5_path}')
plt.close()

print(f'\n在本实验设定下（1年日线），波动最大的是：{vol.index[0]}')

# 图6：三只股票 Histogram 对比
fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)

for ax, (name, series), c in zip(axes, all_rets.items(), colors):
    ax.hist(series.values, bins=35, color=c, alpha=0.75, edgecolor='white')
    ax.axvline(0, color='black', linestyle='--', linewidth=0.6)
    ax.set_title(f'{name}\nσ = {series.std():.2%}')
    ax.set_xlabel('日收益率')

axes[0].set_ylabel('天数')
fig.suptitle('三只股票：日收益率 Histogram 对比', fontsize=14, y=1.02)
plt.tight_layout()
fig6_path = os.path.join(OUTPUT_DIR, 'ch02_fig6_histograms.png')
plt.savefig(fig6_path, dpi=100)
print(f'✓ 图6已保存：{fig6_path}')
plt.close()

print('\n' + '=' * 60)
print('✓ 第2章学习完成！')
print('=' * 60)
print('\n💡 挑战任务：')
print('  1. 修改 tickers 字典，换成你喜欢的股票重做实验')
print('  2. 尝试修改时间范围（如改成2年数据）')
print('  3. 思考：Histogram 尾巴很长说明什么？')
