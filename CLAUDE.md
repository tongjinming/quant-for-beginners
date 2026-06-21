# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在本仓库工作时提供指引。

## 项目概览

`Quant-for-Beginners` 是一份面向零基础读者的中文量化金融教程，以 Jupyter Notebook 形式交付。每章可在约 30 分钟内跑通：真实数据 → 收益率分析 → 双均线策略 → 回测评估。数据来自 `yfinance`（免费日线行情）。第一期（4 章）已上线；Phase 2–4 为规划中内容（见 `docs/ROADMAP.md`）。

## 环境与常用命令

Python 3.10+。安装依赖：

```bash
pip install -r requirements.txt
```

启动教程：

```bash
jupyter lab
```

注意：在不少 macOS 环境下 `pip` 不在 PATH 中，请使用 `pip3` 或 `python3 -m pip`。

Notebook 维护脚本（位于 `scripts/`，在仓库根目录运行）：

```bash
python scripts/prepare_github_notebooks.py     # 整理封面/HTML 便于 GitHub 渲染；保留 outputs
python scripts/clear_notebook_outputs.py        # 仅打印帮助；不加 --confirm 不会执行
python scripts/clear_notebook_outputs.py --confirm   # 清除 outputs/execution_count（不可逆；请先提交 git）
python scripts/apply_notebook_comments.py       # 为指定代码单元重写带中文注释的源码
python scripts/generate_showcase_images.py      # 重新生成 README 使用的 assets/images/chXX_*.png
```

关键约定：`prepare_github_notebooks.py` 故意保留 cell 输出，让学习者在 GitHub 上直接看到结果；只有 `clear_notebook_outputs.py --confirm` 会清除输出，并且刻意加了开关以防误删。

## 仓库结构

- `notebooks/phase1_intro/` —— 课程正文。第 `01`–`04` 章顺序递进（入门 → 收益率 → 均线策略 → 回测）。Markdown 单元使用封面图 `yibo-quant.jpg`（不要用带空格的 `yibo quant.jpg`）。
- `src/` —— 计划放置可复用 Python 模块（`data/`、`strategies/`、`backtest/`）。目前为空/脚手架，教程逻辑仍内联在 Notebook 中。重构 Notebook 代码时，优先抽到 `src/` 而非复制粘贴。
- `scripts/` —— Notebook 与配图维护工具（见上文）。这些脚本直接把 notebook 当作 JSON 解析，而非通过 `nbformat`。
- `docs/` —— `ROADMAP.md`（阶段规划 + 每章发布检查清单）、`CHAPTER_TEMPLATE.md` 与 `NOTEBOOK_TEMPLATE.md`（每章必须遵循的结构模板）。
- `assets/images/` —— README/传播用配图（由 `generate_showcase_images.py` 生成）；`assets/interactive/` —— README 中链接的独立 HTML 演示。
- `data/raw/` 与 `data/processed/` —— 除 `.gitkeep` 外均被 gitignore；下载的行情数据落在这里。

## 编写约定

新章节必须遵循 `docs/CHAPTER_TEMPLATE.md`（章节顺序：目标 → 背景 → 数学直觉 → Python 实现 → 可视化 → 小练习 → 总结 → 下章预告）与 `docs/NOTEBOOK_TEMPLATE.md`（cell 顺序）。模板中的风格规则：

- 先直觉与例子，公式靠后且可选。
- 一个代码单元只做一件事；每一步都要说明"为什么这么做"。
- 读者必须在 30 分钟内跑通本章。
- 计算策略收益时使用 `signal.shift(1)`，避免偷看未来数据（此模式出现在第 1 章，是本项目信号回测的统一约定）。

每章发布检查清单（来自 `ROADMAP.md`）：开头含 等级/难度/时间/前置 信息，正文像人在说话，结尾有 🎯 挑战任务 + 本章总结，配一张 `assets/images/chXX_*.png` 成果图，且 `pip install -r requirements.txt` 后无报错运行通过。

## 内容范围

本仓库是教学用教程代码，不是生产级交易软件。策略代码（均线交叉、简单回测）应视为教学示例。README 中的免责声明同样适用：此处内容不构成任何投资建议。
