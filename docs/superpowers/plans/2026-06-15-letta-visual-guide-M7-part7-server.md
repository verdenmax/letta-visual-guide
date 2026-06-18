# Letta 图解教程 · M7 第七部分（服务端与持久化，4 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第七部分「服务端与持久化」的 4 课（24 三层架构 · 25 服务层 Managers · 26 通用 CRUD 与多租户隔离 · 27 双数据库与向量存储）。延续前六部分的源码级深挖，讲清一条请求从 REST 路由怎么穿过 `SyncServer`/Manager/ORM 落到数据库，业务层如何统一事务与类型/追踪，行级多租户隔离怎么"默认安全"，以及同一套 ORM 如何在 SQLite(dev) 与 Postgres+pgvector(prod) 两套引擎上透明跑、向量怎么存与搜。

**Architecture:** 同前。内容放**新文件 `src/part7.py`**（`registry.py` 加 `import part7`）。新增一课 = 改 `shell.PAGES` + `shell.SUBTITLES` + `registry.CONTENT` + `part7.py` + (可选)`quizzes.QUIZZES`。

**Tech Stack:** Python 3.11+ 标准库；自包含 HTML/CSS。讲解对象 `/home/verden/course/letta`（v0.16.8）。

---

## 强化内容准则（沿用 M3–M6；务必逐条遵守）

1. **反长文（硬闸门）**：任何 `<p>` **≤ 200 中文字 / ≤ 120 英文词**。每段一个点；绝不连续 3 段以上纯文字。
2. **高频穿插视觉**：平均每 1–2 段一个"非纯文字"块。
3. **`.note`（每课 ≥ 3）** tip/info/warn；**`.cute`（每课 ≥ 1）**（服务端主题适合：🏛️ 三层楼、🚪 门房/路由、🗄️ 档案柜/ORM、🔐 门禁/隔离、🔀 双引擎切换、🧬 pydantic 进 DB、📐 向量空间…）。
4. **更详细**：每课 CJK **目标 4500+**（≥3000 硬底）；**图 ≥ 4 张/语言**；**折叠 3–4 个**；2–3 codefiles。靠更多小块实现，不是更长段落。
5. **全 6 卡**：`lead`/`macro`/`analogy`/`detail`/`spark`/`key`/`warn`（`card detail` 别漏）。

> 一句话：M7 要"像图文并茂的科普长文"，不是"论文式大段落"。

---

## 接线（首次用 part7.py）

`src/part7.py` 顶部写模块 docstring，依次 `LESSON_24 … LESSON_27`。`src/registry.py` 加 `import part7` 并在 `CONTENT` 追加 4 条。`shell.PAGES`/`SUBTITLES` 每课追加一行，`part_zh="第七部分 · 服务端与持久化"`、`part_en="Part 7 · Server & persistence"`。index pill 自动更新（到 27 课 · 7 个部分）。导航链：第 23 课 `next` 自动改成 24；27 课 `next=../index.html`。

文件名与标题（en 镜像）：
- `24-three-layer-architecture.html` — zh「三层架构」/ en「The three-layer architecture」；副标题 zh「薄路由 → SyncServer/Manager → ORM → DB · 一个全局 server」/ en「thin routers → SyncServer/Managers → ORM → DB; one global server」。
- `25-service-managers.html` — zh「服务层 Managers」/ en「The service-layer Managers」；副标题 zh「db_registry.async_session 统一事务 · schema↔ORM · enforce_types/trace_method」/ en「db_registry.async_session transactions; schema↔ORM; enforce_types/trace_method」。
- `26-crud-and-multitenancy.html` — zh「通用 CRUD 与多租户隔离」/ en「Generic CRUD & multi-tenant isolation」；副标题 zh「SqlalchemyBase 泛型 CRUD · apply_access_predicate 行级隔离 · 软删除 · 审计字段」/ en「SqlalchemyBase generic CRUD; row-level access predicate; soft delete; audit fields」。
- `27-dual-db-and-vectors.html` — zh「双数据库与向量存储」/ en「Dual database & vector storage」；副标题 zh「database_engine 选 SQLite/Postgres · pgvector / sqlite-vec · pydantic-in-DB · alembic」/ en「database_engine: SQLite/Postgres; pgvector / sqlite-vec; pydantic-in-DB; alembic」。

## 验证（每个 task 收尾，DoD）
```
cd src && python build.py && python check_links.py && python check_html.py
```
期望：`0 error / 0 warning`，链接全解析，index pill「共 27 课 · 7 个部分」（到 27 课时）。Phase A（en 仍是 stub）阶段，check_html 会**只报一条**预期错误「en content missing or too short」，属正常；zh 必须 0 墙/0 图警告。

## 执行策略（两阶段 + 增量生成，防 cut-off / 超时）
每课分两次派发：**Phase A**＝scaffold + wiring + 填 zh；**Phase B**＝填 en 镜像 + 加 quiz。**关键：子代理必须"一点一点生成"——用 `<!--ZHMORE-->`/`<!--ENMORE-->` 占位符逐节小步 `edit`、每 ~2 节就 commit，绝不一次性写完整课；且禁止读大文件（part3/4/5/6、letta 仓库），所需内容全部内联在 prompt 里**（这条是 M5/M6 踩坑后定的硬规矩）。各 task 仍跑**完整 spec + 质量双重审查**（claude-opus-4.8）。

---

## 已核实源码锚点（v0.16.8，4 个并行 research 子代理核实；引用只写"文件+符号"不写行号）

<!--ANCHORS-->

---

<!--TASKS-->

---

## Self-Review（写完即查）
<!--SELFREVIEW-->
