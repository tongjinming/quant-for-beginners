#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第三章：移动平均线策略 —— 调试脚本
修复字体问题 + 可单步运行
"""

# ========== 环境准备 ==========
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# macOS 中文字体修复
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'STHeiti', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

TICKER = 'AAPL'
PERIOD = '2y'

print('环境就绪 ✓')

# ========== 3.1 模拟三种市场状态 ==========
np.random.seed(7)
n_up, n_down, n_noise = 60, 50, 70

ret_up = np.random.normal(0.004, 0.008, n_up)
ret_down = np.random.normal(-0.005, 0.010, n_down)
ret_noise = np.random.normal(0.0, 0.015, n_noise)

price = 100 * np.cumprod(1 + np.r_[ret_up, ret_down, ret_noise])
x = np.arange(len(price))

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(x, price, color='black', linewidth=1.2, label='价格')
ax.axvspan(0, n_up, alpha=0.15, color='green', label='上涨趋势')
ax.axvspan(n_up, n_up + n_down, alpha=0.15, color='red', label='下跌趋势')
ax.axvspan(n_up + n_down, len(price), alpha=0.15, color='gray', label='噪声/横盘')
ax.set_title('三种市场状态（模拟）：趋势 vs 噪声', fontsize=14)
ax.set_xlabel('交易日（示意）')
ax.set_ylabel('价格')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print('绿色区：整体向上 | 红色区：整体向下 | 灰色区：方向不明显、抖动大')

# ========== 3.2 对比原始价格和均线 ==========
demo = pd.DataFrame({'Close': price})
demo['MA20'] = demo['Close'].rolling(20).mean()

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(demo['Close'], label='原始收盘价（很乱）', color='lightgray', linewidth=1.5)
ax.plot(demo['MA20'], label='20日移动平均线（更平滑）', color='tab:blue', linewidth=2)
ax.set_title('为什么需要平均？—— 磨平噪声，看清趋势', fontsize=14)
ax.set_xlabel('交易日（示意）')
ax.set_ylabel('价格')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ========== 3.3 下载真实股票并计算 MA5、MA20 ==========
print(f'\n正在下载 {TICKER} 数据...')
raw = yf.download(TICKER, period=PERIOD, progress=False, multi_level_index=False)
df = raw[['Close']].dropna().copy()
df.columns = ['Close']

df['MA5'] = df['Close'].rolling(5).mean()
df['MA20'] = df['Close'].rolling(20).mean()

print(f'{TICKER} 共 {len(df)} 个交易日')
print(df.tail(8))

# ========== 画收盘价 + 两条均线 ==========
plt.figure(figsize=(13, 5))
plt.plot(df.index, df['Close'], label='收盘价', color='gray', alpha=0.5, linewidth=1)
plt.plot(df.index, df['MA5'], label='MA5（5日均线）', color='tab:orange', linewidth=1.5)
plt.plot(df.index, df['MA20'], label='MA20（20日均线）', color='tab:blue', linewidth=2)
plt.title(f'{TICKER}：价格与移动平均线', fontsize=14)
plt.xlabel('日期')
plt.ylabel('价格')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ========== 3.4 检测金叉、死叉 ==========
df['spread'] = df['MA5'] - df['MA20']
df['cross'] = np.sign(df['spread']).diff()

golden = df[df['cross'] > 0].dropna(subset=['MA5', 'MA20'])
death = df[df['cross'] < 0].dropna(subset=['MA5', 'MA20'])

print(f'\n样本期内 金叉 {len(golden)} 次，死叉 {len(death)} 次')
print('\n最近 3 次金叉日期：')
print(golden.tail(3).index.strftime('%Y-%m-%d').tolist())
print('\n最近 3 次死叉日期：')
print(death.tail(3).index.strftime('%Y-%m-%d').tolist())

# ========== 金叉死叉标注图 ==========
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df['Close'], color='gray', alpha=0.4, linewidth=1, label='收盘价')
ax.plot(df.index, df['MA5'], color='tab:orange', linewidth=1.5, label='MA5')
ax.plot(df.index, df['MA20'], color='tab:blue', linewidth=2, label='MA20')
ax.fill_between(df.index, df['MA5'], df['MA20'],
                where=(df['MA5'] >= df['MA20']),
                interpolate=True, alpha=0.12, color='green', label='MA5 > MA20')
ax.scatter(golden.index, golden['MA5'], marker='^', s=80, color='green',
           edgecolors='black', linewidths=0.5, zorder=5, label='金叉（买入参考）')
ax.scatter(death.index, death['MA5'], marker='v', s=80, color='red',
           edgecolors='black', linewidths=0.5, zorder=5, label='死叉（卖出参考）')
ax.set_title(f'{TICKER}：MA5 vs MA20 —— 金叉 ▲ 与 死叉 ▼', fontsize=14)
ax.set_xlabel('日期')
ax.set_ylabel('价格')
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ========== 3.5 策略：MA5>MA20 则持仓 ==========
df['signal'] = (df['MA5'] > df['MA20']).astype(int)
df['trade'] = 0
df.loc[df['cross'] > 0, 'trade'] = 1
df.loc[df['cross'] < 0, 'trade'] = -1

hold_days = df['signal'].sum()
print(f'\n规则：MA5 > MA20 则持仓 (signal=1)')
print(f'样本期内约 {hold_days} 个交易日处于持仓状态（共 {len(df)} 天）')
print(f'共产生 { (df["trade"] != 0).sum() } 次调仓信号（买+卖）')

print('\n最近几次交易信号：')
print(df[df['trade'] != 0][['Close', 'MA5', 'MA20', 'signal', 'trade']].tail(6))

# ========== 3.6 策略信号大图 ==========
buys = df[df['trade'] == 1]
sells = df[df['trade'] == -1]

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True,
                         gridspec_kw={'height_ratios': [3, 1]})
ax_price, ax_pos = axes

ax_price.plot(df.index, df['Close'], color='gray', alpha=0.45, linewidth=1, label='收盘价')
ax_price.plot(df.index, df['MA5'], color='tab:orange', linewidth=1.5, label='MA5')
ax_price.plot(df.index, df['MA20'], color='tab:blue', linewidth=2, label='MA20')
ax_price.scatter(buys.index, buys['Close'], marker='^', s=120, color='limegreen',
                 edgecolors='darkgreen', linewidths=1, zorder=6, label='买入 ▲')
ax_price.scatter(sells.index, sells['Close'], marker='v', s=120, color='salmon',
                 edgecolors='darkred', linewidths=1, zorder=6, label='卖出 ▼')
ax_price.set_title(f'{TICKER} 双均线策略：均线 + 买卖点', fontsize=14)
ax_price.set_ylabel('价格')
ax_price.legend(loc='upper left')
ax_price.grid(True, alpha=0.3)

ax_pos.fill_between(df.index, 0, df['signal'], step='post', alpha=0.35, color='steelblue')
ax_pos.set_ylim(-0.1, 1.2)
ax_pos.set_yticks([0, 1])
ax_pos.set_yticklabels(['空仓 (0)', '持仓 (1)'])
ax_pos.set_xlabel('日期')
ax_pos.set_ylabel('信号')
ax_pos.set_title('策略持仓状态：MA5 > MA20 时持有', fontsize=12)
ax_pos.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print('\n✓ 第三章调试脚本运行完成')
