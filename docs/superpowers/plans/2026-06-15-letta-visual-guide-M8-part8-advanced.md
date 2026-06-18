# Letta 图解教程 · M8 第八部分（进阶专题 + 术语表，4 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第八部分「进阶专题 + 术语表」的 4 课（28 多智能体与 sleeptime · 29 数据源与 RAG · 30 jobs/runs/steps 与可观测性 · 31 术语表·概念索引）。前三课延续源码级深挖；第 31 课是**全书术语速查 + 跳链索引**（结构与前面不同）。这是全书正文的收尾部分。

**Architecture:** 同前。内容放**新文件 `src/part8.py`**（`registry.py` 加 `import part8`）。新增一课 = 改 `shell.PAGES` + `shell.SUBTITLES` + `registry.CONTENT` + `part8.py` + (可选)`quizzes.QUIZZES`。

**Tech Stack:** Python 3.11+ 标准库；自包含 HTML/CSS。讲解对象 `/home/verden/course/letta`（v0.16.8）。

---

## 强化内容准则（沿用 M3–M7；务必逐条遵守）

1. **反长文（硬闸门）**：任何 `<p>` **≤ 200 中文字 / ≤ 120 英文词**。每段一个点；绝不连续 3 段以上纯文字。
2. **高频穿插视觉**：平均每 1–2 段一个"非纯文字"块。
3. **`.note`（每课 ≥ 3）** tip/info/warn；**`.cute`（每课 ≥ 1）**（进阶主题适合：🤝 多智能体、😴 sleeptime、📚 数据源/RAG、🧾 jobs/runs/steps、🔭 可观测性、📖 术语表…）。
4. **更详细**：每课 CJK **目标 4500+**（≥3000 硬底）；**图 ≥ 4 张/语言**；**折叠 3–4 个**；2–3 codefiles。靠更多小块实现，不是更长段落。**（第 31 课术语表除外——见下方 Task 4 的特例结构。）**
5. **全 6 卡**：`lead`/`macro`/`analogy`/`detail`/`spark`/`key`/`warn`（`card detail` 别漏）。**（第 31 课除外。）**
6. **卡序**：沿用 Part 7 的 **macro-first** 节奏（28–30）。

> 一句话：M8 前三课要"像图文并茂的科普长文"；第 31 课要"像一本好查的速查手册"。

---

## 接线（首次用 part8.py）

`src/part8.py` 顶部写模块 docstring，依次 `LESSON_28 … LESSON_31`。`src/registry.py` 加 `import part8` 并在 `CONTENT` 追加 4 条。`shell.PAGES`/`SUBTITLES` 每课追加一行，`part_zh="第八部分 · 进阶专题"`、`part_en="Part 8 · Advanced topics"`。index pill 自动更新（到 31 课 · 8 个部分）。导航链：第 27 课 `next` 自动改成 28；31 课 `next=../index.html`。

文件名与标题（en 镜像）：
- `28-multi-agent-sleeptime.html` — zh「多智能体与 sleeptime」/ en「Multi-agent & sleeptime」；副标题 zh「groups · send_message_to_agent_* · sleeptime 后台改记忆 · 共享块」/ en「groups; send_message_to_agent_*; sleeptime background memory edits; shared blocks」。
- `29-data-sources-rag.html` — zh「数据源与 RAG」/ en「Data sources & RAG」；副标题 zh「files → source passages · 摄取+嵌入 · 与归档记忆的区别」/ en「files → source passages; ingestion + embeddings; vs archival memory」。
- `30-jobs-runs-steps.html` — zh「jobs / runs / steps 与可观测性」/ en「Jobs, runs, steps & observability」；副标题 zh「异步执行追踪 · otel/telemetry · 流式 SSE」/ en「async execution tracking; otel/telemetry; streaming SSE」。
- `31-glossary-index.html` — zh「术语表·概念索引」/ en「Glossary & concept index」；副标题 zh「全书术语一句话查 + 跳链到对应课」/ en「every term in one line + jump links to its lesson」。

## 验证（每个 task 收尾，DoD）
```
cd src && python build.py && python check_links.py && python check_html.py
```
期望：`0 error / 0 warning`，链接全解析，index pill「共 31 课 · 8 个部分」（到 31 课时）。Phase A（en 仍是 stub）阶段，check_html 会**只报一条**预期错误「en content missing or too short」，属正常；zh 必须 0 墙/0 图警告。
**第 31 课特例**：术语表结构特殊（无 6 卡/无 ≥4 图的硬性），但仍须 0 error / 0 warning、双语等价、跳链全部解析（`check_links` 是关键闸门）。

## 执行策略（两阶段 + 增量生成，防 cut-off / 超时）
每课分两次派发：**Phase A**＝scaffold + wiring + 填 zh；**Phase B**＝填 en 镜像 + 加 quiz（第 31 课术语表是否配 quiz 视内容而定）。**关键：子代理必须"一点一点生成"——用 `<!--ZHMORE-->`/`<!--ENMORE-->` 占位符逐节小步 `edit`、每 ~2 节就 commit，绝不一次性写完整课；且禁止读大文件（part3-7、letta 仓库），所需内容全部内联在 prompt 里**。各 task 仍跑**完整 spec + 质量双重审查**（claude-opus-4.8）。

---

## 已核实源码锚点（v0.16.8，3 个并行 research 子代理核实；引用只写"文件+符号"不写行号）

<!--ANCHORS-->

---

<!--TASKS-->

---

## Self-Review（写完即查）
<!--SELFREVIEW-->
