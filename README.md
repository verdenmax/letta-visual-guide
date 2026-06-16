# Letta 图解教程（Letta Visual Guide）

从零理解 [Letta](https://github.com/letta-ai/letta)（原 MemGPT）的中英双语图解教程。
纯 Python 零依赖生成器，产出自包含静态站点，可 `file://` 直接打开。

## 如何重新生成

```bash
cd src
python build.py          # 生成 index.html + lessons/*.html
python check_links.py    # 校验内部链接无死链
python check_html.py     # 校验结构 / 与 src 无漂移
```

## 目录

- `src/shell.py` — 设计系统（CSS）+ 导航 + 双语切换 + `PAGES`
- `src/registry.py` — 文件名 → 双语内容（单一事实源）
- `src/part1.py …` — 各部分课程内容
- `src/quizzes.py` — 每课自测
- `src/build.py` / `check_links.py` / `check_html.py` — 构建与校验

> 独立第三方学习材料，与 Letta 官方无隶属关系；源码引用锚定 letta `v0.16.8`。
