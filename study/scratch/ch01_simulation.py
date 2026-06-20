"""第 1 章 模拟代码 —— 调试用可运行版本。

把原 notebook 的代码拆到这个 .py 文件，方便在 IDE 里打断点、
单步看 DataFrame 的变化。运行方式（仓库根目录）：

    python study/scratch/ch01_simulation.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 字体回退列表：macOS 字体在前，SimHei（Windows）留最后，保证跨平台可跑
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
np.random.seed(7)

# ========== 第1步：模拟三段行情 ==========
n1, n2, n3 = 90, 40, 120
ret = np.r_[
    np.random.normal(0.0010, 0.010, n1),
    np.random.normal(-0.012, 0.015, n2),
    np.random.normal(0.0012, 0.012, n3),
]
price = 100 * np.cumprod(1 + ret)

# ========== 第2步：构造 DataFrame + 日收益率 ==========
df = pd.DataFrame({"close": price})
df["ret"] = df["close"].pct_change().fillna(0)

# 调试点：看前几行，确认 ret 第一行是 0
print("=== head ===")
print(df.head())

# ========== 第3步：20日均线规则 ==========
df["ma20"] = df["close"].rolling(20).mean()
df["signal_quant"] = (df["close"] > df["ma20"]).astype(int)

# 调试点：确认 ma20 前 19 行是 NaN
print("\n=== ma20 前 22 行 ===")
print(df[["close", "ma20", "signal_quant"]].head(22))

# ========== 第4步：随机买卖对照 ==========
rng = np.random.default_rng(7)
df["signal_random"] = rng.integers(0, 2, size=len(df))

# ========== 第5步：信号用昨天的，避免偷看未来 ==========
df["ret_quant"] = df["signal_quant"].shift(1).fillna(0) * df["ret"]
df["ret_random"] = df["signal_random"].shift(1).fillna(0) * df["ret"]
df["ret_buyhold"] = df["ret"]

# ========== 第6步：净值曲线 ==========
for col in ["ret_quant", "ret_random", "ret_buyhold"]:
    df[f"nav_{col}"] = (1 + df[col]).cumprod()

# 调试点：最终净值
print("\n=== 最终净值 ===")
print(df[["nav_ret_quant", "nav_ret_random", "nav_ret_buyhold"]].iloc[-1])

# ========== 第7步：画图 ==========
fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

axes[0].plot(df["close"], label="Price", color="black", linewidth=1.4)
axes[0].plot(df["ma20"], label="MA20", color="tab:blue", alpha=0.9)
axes[0].set_title("模拟市场价格与均线")
axes[0].legend()

axes[1].plot(df["nav_ret_buyhold"], label="买入并持有", linewidth=2)
axes[1].plot(df["nav_ret_quant"], label="量化规则策略", linewidth=2)
axes[1].plot(df["nav_ret_random"], label="随机买卖", linewidth=2, alpha=0.85)
axes[1].set_title("三种方法的净值对比")
axes[1].legend()

plt.tight_layout()
plt.show()
