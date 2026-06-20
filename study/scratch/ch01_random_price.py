"""第 1 章「3行代码生成随机股价走势」—— 字体修复版。

原 notebook (cell 20) 用 `plt.rcParams['font.sans-serif'] = ['SimHei']`，
macOS 上没有 SimHei 字体会报 findfont 警告并显示成方框。
这里改用跨平台字体回退列表，Mac / Windows 都能正常显示中文。

运行（仓库根目录）：
    python study/scratch/ch01_random_price.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 关键修复：字体回退列表，macOS 字体在前，SimHei（Windows）留最后
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)          # 固定随机数，结果可复现
days = 120                  # 一共模拟 120 个交易日
daily_returns = np.random.normal(loc=0.0008, scale=0.02, size=days)  # 每天随机收益率
price = 100 * np.cumprod(1 + daily_returns)     # 从100元出发连乘成价格序列

df = pd.DataFrame({
    '收盘价': price,
    '5日均线': pd.Series(price).rolling(5).mean(),
    '20日均线': pd.Series(price).rolling(20).mean()
})

plt.figure(figsize=(12, 5))
plt.plot(df['收盘价'], label='收盘价', alpha=0.6, linewidth=1)
plt.plot(df['5日均线'], label='5日均线 (MA5)', linewidth=1.5)
plt.plot(df['20日均线'], label='20日均线 (MA20)', linewidth=1.5)
plt.fill_between(range(days), df['5日均线'], df['20日均线'], alpha=0.1, color='orange')
plt.title('Python 模拟股价走势 + 移动平均线', fontsize=14)
plt.xlabel('交易日')
plt.ylabel('价格')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print(f"起始价格: ¥{price[0]:.2f}")
print(f"最终价格: ¥{price[-1]:.2f}")
print(f"区间收益率: {(price[-1]/price[0] - 1)*100:.2f}%")
print(f"最大回撤价格: ¥{price.min():.2f}")
print(f"最高价格: ¥{price.max():.2f}")
