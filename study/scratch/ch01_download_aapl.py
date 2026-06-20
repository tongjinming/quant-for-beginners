"""第 1 章「下载真实股票数据 AAPL」—— 字体修复版。

原 notebook (cell 34) 用 `plt.rcParams['font.sans-serif'] = ['SimHei']`，
macOS 上报 findfont 警告并显示成方框。这里改用跨平台字体回退列表。

注意两点与 notebook 版本的差异（脚本环境必须改）：
  1. `display(aapl.tail(5))` 是 IPython/Notebook 专用，脚本里换成 `print(...)`
  2. 需要联网下载 yfinance 数据；如网络受限会抛异常

运行（仓库根目录）：
    python study/scratch/ch01_download_aapl.py
"""

import warnings
warnings.filterwarnings('ignore')   # 隐藏不影响学习的警告信息

import time
import matplotlib.pyplot as plt     # 画图
import yfinance as yf               # 从雅虎财经免费下载行情

# 关键修复：字体回退列表，macOS 字体在前，SimHei（Windows）留最后
plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 下载苹果 AAPL 最近 6 个月的日线（需要联网）
# 两个反限流措施：
#   1. download 前先 sleep 3 秒，降低突发请求速率
#   2. threads=False 关闭多线程并发，改单线程顺序请求（雅虎对并发请求限流更严）
print('正在下载 AAPL 数据（已加 3 秒延迟 + 关闭多线程以规避限流）...')
time.sleep(3)
aapl = yf.download('AAPL', period='6mo', progress=False, multi_level_index=False, threads=False)

# 雅虎限流时会返回空 DataFrame，给清晰提示而不是崩溃
if len(aapl) == 0:
    print('❌ 下载失败：未拿到任何数据。常见原因是雅虎财经限流')
    print('   (YFRateLimitError: Too Many Requests)。')
    print('   解决：等 5-15 分钟后重试，或切换网络（如手机热点）。')
    import sys
    sys.exit(0)

print('🎉 恭喜！你已经拿到真实股票数据')
print(f'   共 {len(aapl)} 个交易日')                              # 行数 = 交易日个数
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
