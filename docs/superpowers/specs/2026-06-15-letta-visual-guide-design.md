# Letta 图解教程（letta-visual-guide）· 设计文档（Spec）

> 状态：已与用户确认设计方向，待用户复核本 spec 后进入 writing-plans。
> 日期：2026-06-15
> 仿照项目：`/home/verden/course/llama-cpp-visual-guide`
> 讲解对象仓库：`/home/verden/course/letta`（`letta-ai/letta`，原 MemGPT；锚定版本 `v0.16.8`）

---

## 1. 目标与受众

做一套面向**完全新手**的可视化（HTML 图解）教程，带读者**从零开始、一点点**理解
整个 Letta 项目：既有**宏观全景与整体结构图**，也深入到 **记忆系统 / agent 执行循环 /
工具系统 / LLM provider 抽象 / 服务端与持久化** 的源码细节，并讲清楚
"**每个东西是什么功能、为什么要这么写**"。

- **受众**：
  - 完全没接触过 Letta / MemGPT、想从零入门的新手
  - 想先建立宏观认知、再深入内部源码的学习者
  - 准备阅读 / 调试 / 贡献 Letta 源码，或在其上做二次开发的开发者
- **读者收获**：从"会用有状态 agent"到"懂其记忆与执行原理"的完整路径，
  以及一份可随时查阅的源码导航地图（文件 + 符号）。
- **核心主线**：Letta 的灵魂是 **MemGPT 论文的记忆思想**——
  LLM 无状态、上下文窗口有限，于是把 agent 做成**有状态**、能**自我编辑记忆**、
  能在上下文满时**自我压缩**的系统。全书围绕这条主线展开。

> 注意：本教程是**独立的第三方学习材料**，与 Letta 官方无隶属关系；
> 放在**独立仓库**，**绝不**向 Letta 上游仓库提交任何内容。

---

## 2. 已确认的关键决策

| 决策点 | 结论 |
| --- | --- |
| 深度重心 | **方案 A·全覆盖深挖**：宏观 → 前置基础 → 记忆系统 → agent 循环 → 工具 → LLM provider → 服务端/ORM → 多智能体，源码级，做成大型教程 |
| 项目位置 | 新建独立目录 `/home/verden/course/letta-visual-guide`，单独 git 仓库（与 `/home/verden/course/letta` 平级，互不混入） |
| 语言 | **中英双语**，顶部按钮即时切换（zh ⇄ en），`localStorage` 记住选择 |
| 配套功能 | **全保留**：每课自测 quiz + 下载双语 PDF + GitHub Pages 自动部署 CI |
| 课程组织 | **方案 A·单线递进**：一条从零到深的主线（8 部分 / ~31 课） |
| 内容风格 | **多画图**（结构图/流程图/概念示意，图加深理解）、**多伪代码 + 源码简化片段**、每课**尽量详细** |
| 交付方式 | **分多个 milestone** 逐步交付，不必一次写完 |

---

## 3. 架构（复用模板 + 换皮 + 双语）

完全复用 llama-cpp-visual-guide / langchain-visual-guide 的成熟架构：
**纯 Python 3、零第三方依赖的生成器**，产出**自包含、可 `file://` 直接打开**的 HTML。

### 3.1 仓库结构

```
letta-visual-guide/
├── index.html                  ← 目录页（入口），从这里开始
├── lessons/                    ← 生成的课程页（每课一个 HTML，内嵌中/英两份内容）
│   ├── 01-what-is-letta.html
│   └── …  31-glossary.html
├── src/                        ← 纯 Python 无依赖生成器（可重建全部 HTML / PDF）
│   ├── shell.py                设计系统(CSS) + PAGES + page()/index_page() + 语言切换 JS
│   ├── registry.py             文件名 → {"zh":…, "en":…} 内容映射（单一事实源）
│   ├── part1.py … part8.py     各部分课程内容（每课 LESSON_xx = {"zh":…, "en":…}）
│   ├── quizzes.py              每课自测（双语）
│   ├── build.py                站点构建（→ index.html + lessons/）
│   ├── build_print.py          PDF 构建（→ print-zh.html / print-en.html，折叠全展开）
│   ├── check_html.py           CI：校验生成 HTML 与 src/ 无漂移
│   └── check_links.py          CI：校验内部链接无死链
├── .github/workflows/
│   ├── deploy.yml              CI：构建站点 + 渲染双语 PDF + 部署 Pages
│   └── ci.yml                  CI：防回归（重建校验漂移 + 死链）
├── README.md
└── LICENSE                     （MIT）
```

### 3.2 双语机制（顶部即时切换）

- 每课页面同时渲染两块内容：`<div class="lang-zh">…</div>` 与 `<div class="lang-en">…</div>`。
- 顶部一个 `中 / EN` 切换按钮：JS 切换 body class，CSS 控制只显示一种语言。
- 选择写入 `localStorage`，**翻到下一课仍保持**同一语言；默认中文（首次访问）。
- 站点/课程的**外壳文案**（导航、进度、按钮、目录副标题）也双语化，跟随切换。

### 3.3 换皮（Letta 主题）

- 主题色：从 llama.cpp 的暖橙改为 **Letta 风格的靛蓝 / 紫罗兰**（呼应"记忆 / 认知"主题），保留深色模式。
- 角标/favicon：llama 标记 → Letta 风格标记（`L` 字标或"记忆块"图形）。
- 站点标题：「Letta 图解教程 · 从零理解有状态记忆 agent」/「Letta Visual Guide」。
- **其余设计系统全部沿用**：卡片（macro/detail/analogy/key/warn/spark）、流程图（flow/vflow）、
  分层架构（layers）、两栏对比（cols）、表格、代码块（带高亮 span）、折叠（accordion）、quiz、
  顶部进度条、上一课/下一课导航、目录搜索。

---

## 4. 课程大纲（8 部分 · 31 课）

> 副标题给方向；每课的真实源码引用以"**文件 + 符号名**"为主（**不写死行号**，避免随上游更新失效）。
> 内容准则见第 6 节：**多图、多伪代码 / 源码简化片段、尽量详细**。下列"源码锚点"是写作时的核实起点。

### 第一部分 · 宏观全景
1. **Letta / MemGPT 是什么** — 解决什么问题（LLM 无状态 + 上下文窗口有限）· "有记忆、能自我改进"的有状态 agent · 与 LangChain / AutoGPT / OpenAI Assistants 的区别 · MemGPT 论文一句话。锚点：`README.md`、`letta/schemas/agent.py::AgentState`。
2. **项目全景地图** — `letta/` 目录导览（agents / schemas / services / orm / server / functions / llm_api / prompts）· 三层架构鸟瞰（REST → services/managers → ORM/DB）· **整体结构图**。锚点：`letta/server/server.py::SyncServer`、`letta/services/*Manager`、`letta/orm/`。
3. **一条消息的生命周期** — `POST /v1/agents/{id}/messages` → 解析 actor → 加载 `AgentState` → 组装上下文 → LLM 调用 → 工具执行 → 记忆更新 → 持久化 → 响应。**全景数据流图**。锚点：`letta/server/rest_api/routers/v1/agents.py::send_message`、`letta/agents/agent_loop.py::AgentLoop.load`、`letta/agents/letta_agent_v3.py::LettaAgentV3.step`。

### 第二部分 · 前置基础（从零打底）
4. **LLM agent 与 tool calling 基础** — decoder-only 极简回顾 · 什么是 tool/function calling · ReAct/循环 · inner monologue（思考再行动）。锚点：`letta/llm_api/helpers.py::add_inner_thoughts_to_functions`、`letta/local_llm/constants.py::INNER_THOUGHTS_KWARG`。
5. **上下文窗口的根本问题** — token 限制 · prefill vs decode · 为什么"无限记忆"难 · prefix cache 为何重要 · 这是 MemGPT 的出发点。**概念示意图**（窗口/token 预算）。锚点：`letta/services/context_window_calculator/`、`letta/schemas/memory.py::ContextWindowOverview`。
6. **有状态 vs 无状态** — 为什么 Letta 把 agent 做成数据库里的 `AgentState`（存档）· stateless runtime + serialized state · 与 OpenAI Assistants 对比 · prefixed id。锚点：`letta/schemas/agent.py::AgentState`、`letta/schemas/letta_base.py::LettaBase`。

### 第三部分 · 记忆系统（皇冠明珠）
7. **记忆三层总览** — MemGPT 三层（core / recall / archival）· 对应论文 main context / recall storage / archival storage · 映射到代码 · `<memory_metadata>` 让模型知道"忘了什么"。**三层结构图**。锚点：`letta/schemas/memory.py::Memory`、`letta/prompts/prompt_generator.py::PromptGenerator.compile_memory_metadata_block`。
8. **记忆块 Memory Blocks** — `Block`/`Human`/`Persona`（label/value/limit/read_only）· `ChatMemory(persona, human)` · `Memory.compile()` 渲染 · 共享块（多 agent 复用）· 块历史/undo。锚点：`letta/schemas/block.py::Block`、`letta/schemas/memory.py::Memory.compile`、`letta/services/block_manager.py`、`letta/orm/block_history.py`。
9. **自我编辑记忆 = 改写自己的系统提示** — `core_memory_append/replace` 实现 · `{CORE_MEMORY}` 占位符（`IN_CONTEXT_MEMORY_KEYWORD`）· `rebuild_system_prompt_async` 重写 message#0 · prefix-cache 友好。锚点：`letta/services/tool_executor/core_tool_executor.py::LettaCoreToolExecutor`、`letta/services/agent_manager.py::rebuild_system_prompt_async`、`letta/prompts/prompt_generator.py::get_system_message_from_compiled_memory`。
10. **归档记忆与向量检索** — `Passage` + embeddings · `archival_memory_insert/search` · pgvector / sqlite-vec · archive 分组与 tags。**向量检索示意图**。锚点：`letta/schemas/passage.py`、`letta/services/passage_manager.py::insert_passage`、`letta/services/archive_manager.py`、`letta/orm/passage.py`。
11. **回忆记忆与对话历史** — `Message` 全量存储 · `message_ids` 决定哪些在窗口内 · `conversation_search` · 消息是 JSON 信封（`letta/system.py`）。锚点：`letta/services/message_manager.py`、`letta/schemas/message.py::Message`、`letta/system.py::package_user_message`。
12. **上下文压缩与"记忆压力"** — compaction / summarization · 阈值触发（`SUMMARIZATION_TRIGGER_MULTIPLIER`）· sliding window · summary 消息 + compaction 事件 · 系统提示溢出特殊路径。**时间线/压缩示意图**。锚点：`letta/services/summarizer/`（`Summarizer`、`compact_messages`、`thresholds.py::get_compaction_trigger_threshold`）、`letta/agents/letta_agent_v3.py::compact`。

### 第四部分 · Agent 执行循环
13. **AgentState 与 AgentLoop 工厂** — `AgentState` 串起 memory/message_ids/system/tool_rules/llm_config · `AgentLoop.load` 按 agent_type 选实现 · 三代 agent（legacy `Agent` / V2 / V3）。锚点：`letta/agents/agent_loop.py::AgentLoop.load`、`letta/agents/letta_agent_v3.py::LettaAgentV3`、`letta/schemas/enums.py`。
14. **V3 步进循环** — `_step` = 一次 LLM 调用 + 工具执行 + 持久化 · `step()` 的 `max_steps` 循环（`DEFAULT_MAX_STEPS`）· `_handle_ai_response` · `_decide_continuation`（调了工具就继续）。**循环流程图**。锚点：`letta/agents/letta_agent_v3.py::LettaAgentV3._step/_handle_ai_response/_decide_continuation`。
15. **从 heartbeat 到无 heartbeat** — 原始 MemGPT `inner_step` 的 `request_heartbeat` 链式调用 · v3 "无 heartbeat" 简化 · **前后对比图**。锚点：`letta/agent.py::Agent.inner_step`、`letta/local_llm/function_parser.py::insert_heartbeat`、`letta/agents/letta_agent_v3.py::_get_valid_tools`。
16. **工具规则 Tool Rules** — Init/Terminal/Continue/Child/Parent/Conditional/MaxCount/RequiredBeforeExit/RequiresApproval · `ToolRulesSolver` 计算合法下一步 · 违规合成错误而非执行。锚点：`letta/schemas/tool_rule.py`、`letta/helpers/tool_rule_solver.py::ToolRulesSolver`、`letta/schemas/enums.py::ToolRuleType`。

### 第五部分 · 工具系统
17. **工具即 Python 函数 + docstring** — `generate_schema` 把签名 + Google 风格 docstring 变成 OpenAI JSON schema · 描述是必填的 API 契约 · 保留 kwargs。锚点：`letta/functions/schema_generator.py::generate_schema`、`letta/functions/function_sets/base.py`。
18. **不执行就生成 schema** — `derive_openai_json_schema` + `MockFunction` · AST 静态解析（不 import 不信任代码）· TypeScript 工具。锚点：`letta/functions/functions.py::derive_openai_json_schema`、`letta/functions/ast_parsers.py`、`letta/functions/typescript_parser.py`。
19. **工具分发与执行（含 MCP）** — `ToolType` · `ToolExecutorFactory` 按类型分发 · core/builtin/files/mcp executor · MCP（Model Context Protocol）。锚点：`letta/services/tool_executor/tool_execution_manager.py::ToolExecutorFactory`、`letta/functions/mcp_client/types.py`。
20. **自定义工具沙箱与安全修复** — local venv / E2B / Modal · Jinja 包装脚本 · **server→sandbox（pickle，受信） vs sandbox→server（JSON，不信）** 的安全修复（PR #3343）· marker + 长度 + MD5 校验。**沙箱边界信任图**。锚点：`letta/services/tool_sandbox/`（`base.py::generate_execution_script`、`local_sandbox.py`、`safe_pickle.py`）、`letta/services/helpers/tool_parser_helper.py::parse_stdout_best_effort`、`letta/templates/sandbox_code_file.py.j2`。

### 第六部分 · LLM Provider 抽象
21. **统一 provider 三方法契约** — `LLMConfig` · `LLMClient.create` 工厂 · `build_request_data` / `request_async` / `convert_response_to_chat_completion` · **OpenAI 形状作为通用中间格式**。**provider 适配图**。锚点：`letta/llm_api/llm_client.py::LLMClient.create`、`letta/llm_api/llm_client_base.py::LLMClientBase`、`letta/schemas/llm_config.py::LLMConfig`。
22. **provider 怪癖的隔离** — `OpenAIClient` 继承复用（~12 家）· Anthropic 的 cache-control / reasoning / batch · Google Vertex · inner thoughts 注入为工具参数并保证先行。锚点：`letta/llm_api/openai_client.py`、`letta/llm_api/anthropic_client.py`、`letta/llm_api/helpers.py::unpack_inner_thoughts_from_kwargs`。
23. **本地模型与 GBNF 受限解码** — `chat_completion_proxy.get_chat_completion` 在裸 completion 上模拟 function calling · GBNF 语法约束 JSON · 按模型族的 wrapper。锚点：`letta/local_llm/chat_completion_proxy.py`、`letta/local_llm/grammars/json_func_calls_with_inner_thoughts.gbnf`、`letta/local_llm/llm_chat_completion_wrappers/`。

### 第七部分 · 服务端与持久化
24. **三层架构** — REST 路由（薄）→ `SyncServer`/Manager（业务 + session）→ ORM（CRUD + 访问控制）→ DB · 一个全局 `SyncServer`。**分层调用图 + 一次请求轨迹**。锚点：`letta/server/rest_api/app.py`、`letta/server/server.py::SyncServer`、`letta/server/rest_api/dependencies.py::get_letta_server`。
25. **服务层 Managers** — `AgentManager`/`MessageManager`/`BlockManager`/… · `db_registry.async_session()` 统一事务 · schema↔orm 转换 · `@enforce_types`/`@trace_method`。锚点：`letta/services/agent_manager.py`、`letta/server/db.py::DatabaseRegistry`。
26. **通用 CRUD 与多租户隔离** — `SqlalchemyBase` 泛型 async CRUD · `apply_access_predicate`（org/user 行级隔离）· 软删除 vs 硬删除 · 审计字段 · actor 来自 `user_id` header · server password 鉴权。**"secure by default" 图**。锚点：`letta/orm/sqlalchemy_base.py::SqlalchemyBase`、`letta/orm/base.py::CommonSqlalchemyMetaMixins`、`letta/services/user_manager.py::get_actor_or_default_async`。
27. **双数据库与向量存储** — `settings.database_engine` 选 SQLite(dev)/Postgres+pgvector(prod) · `sqlite-vec` · `custom_columns`（pydantic-in-DB）· alembic 迁移 · `MAX_EMBEDDING_DIM`。锚点：`letta/settings.py::database_engine`、`letta/server/db.py`、`letta/orm/passage.py::BasePassage`、`letta/orm/custom_columns.py`、`letta/orm/sqlite_functions.py`。

### 第八部分 · 进阶专题 + 速查
28. **多智能体与 sleeptime** — `groups` · `send_message_to_agent_*` · `sleeptime_multi_agent` 在后台编辑记忆（`rethink_memory`）· 共享块。锚点：`letta/groups/`、`letta/functions/function_sets/multi_agent.py`、`letta/services/group_manager.py`。
29. **数据源与 RAG** — `data_sources` / files · source passages vs archival passages · ingestion + embeddings · 与归档记忆的区别。锚点：`letta/data_sources/`、`letta/services/source_manager.py`、`letta/services/file_manager.py`、`letta/orm/passage.py::SourcePassage`。
30. **jobs / runs / steps 与可观测性** — 异步执行追踪 · otel / telemetry · 流式 SSE 接口。锚点：`letta/services/job_manager.py`、`letta/services/run_manager.py`、`letta/services/step_manager.py`、`letta/otel/`、`letta/server/rest_api/interface.py`。
31. **术语表 · 概念索引** — 全书术语一句话查（core/recall/archival memory、block、AgentState、tool rule、heartbeat、compaction、actor、passage、MCP…）+ 点链接跳到对应课。

---

## 5. 每课页面结构（页面解剖）

沿用模板的教学元素，每课大致包含（按需取用，不强制全有）：

- **顶部**：进度条 + 部分标签 + `NN / 31` + 语言切换按钮。
- **Hero**：部分名 + 课程标题。
- **导语**：一段话点题。
- **教学卡片**：
  - 🌍 **宏观理解**（macro）— 大局观、为什么这样设计。
  - 🔬 **细节 / 源码对应**（detail）— 指向真实文件 + 符号（如 `letta/agents/letta_agent_v3.py` 的 `_step`）。
  - 🔌 **生活类比**（analogy）— 用日常事物帮助理解抽象概念（如"记忆块=便利贴"、"压缩=做会议纪要"）。
  - ✅ **关键要点**（key）— 每课小结。
  - 💡 **设计亮点**（spark）— 该课最精妙的设计思想。
  - ⚠️ **坑 / 注意**（warn，按需）。
- **图（硬性要求，重点）**：**每课 3-5 张图**，类型尽量多样：
  - **结构 / 分层图**（`layers`）、**流程图**（`flow` 横向 / `vflow` 纵向步骤）、**对比图**（`cols` 并排）、
  - **概念示意图**（用 **HTML+CSS** 画的原理草图，如三层记忆、上下文压缩时间线、沙箱信任边界、
    provider 适配、三层请求轨迹；用设计系统 CSS 变量配色，**深色模式自适应**，自包含、不依赖外部图片/SVG）。
  - 宏观/结构课必须有"**整体结构图**"；原理课必须有至少 1 张**概念示意图**。
- **代码（重点）**：每课 **2-3 段**伪代码 / 从源码简化的真实片段（带高亮），讲清"为什么这么写"。
- **折叠深挖**（accordion）：**每课 2-3 个**可展开的深入卡片，新手可跳过；
  推荐结构「**示例 → 为什么这样设计 → 源码在哪（文件+符号）→ 还有什么替代**」。
- **末尾自测**（quiz）：2-4 题双语，点开看解析。
- **底部导航**：上一课 / 下一课。

---

## 6. 内容准则

1. **多图（硬性）**：**每课 3-5 张图**，类型多样化（分层 / 流程 / 对比 / 概念示意），而非只画一张分层图。
   宏观/结构课必须有"整体结构图"，原理课必须有至少 1 张"概念示意图"。概念图优先用 **HTML+CSS**（设计系统
   CSS 变量配色、深色模式自适应、自包含），不用硬编码颜色的 SVG。
2. **多代码**：每课 **2-3 段**——以**伪代码**讲清思路，再给**从源码简化的真实片段**对照（标注来源文件 + 符号）。
3. **尽量详细（硬性）**：每课**纯中文正文目标 ~4000+ 汉字（CJK，按 `\u4e00-\u9fff` 计；不含英文/代码/路径）**，
   并配 **2-3 个折叠深挖**，把"是什么 / 为什么这么写 / 源码在哪 / 还有什么替代方案"讲透；宁多勿少。
4. **源码引用**：以"**文件 + 符号名**"为主，**不写死行号**（行号会随上游更新失效）。
5. **准确性**：所有源码引用对照 Letta 仓库**真实代码核实**（锚定 `v0.16.8`）；
   注意 Letta 有**三代 agent**，正文以**当前默认的 V3**（`letta_v1_agent` → `LettaAgentV3`）为主线，legacy/V2 作对比。
6. **ASCII 优先**：正文/代码避免 em-dash `—`、unicode 箭头 `→` 等（用 `-`、`->`、`...`）——
   *仅指课程"代码片段"内部*；中文叙述与既有模板中的排版符号不受此限。
7. **自包含**：页面无外部 JS/CSS 依赖，相对链接，支持 `file://` 与任意静态服务器。
8. **双语对齐**：中/英两份内容**信息等价**（不要求逐字对译，但要点不能缺）。

---

## 7. 配套功能

- **quizzes.py**：每课 2-4 题自测，双语，折叠看解析。
- **build_print.py**：把全 31 课合成单页、折叠全展开、自动分页，分别产出
  `print-zh.html` 与 `print-en.html`，供无头 Chrome 打成
  `letta-visual-guide-zh.pdf` / `-en.pdf`。
- **CI**：
  - `deploy.yml`：push 即重建站点 + 渲染双语 PDF（安装 CJK/emoji 字体）+ 部署 GitHub Pages；
    打 `v*` 标签时发布 Release 附带双语 PDF。
  - `ci.yml`：每次 push/PR 重跑 `build.py` 校验提交 HTML 与 `src/` 无漂移；跑 `check_links.py` 防死链。
- **首次启用 Pages**：仓库 Settings → Pages → Source 选 GitHub Actions（一次性，需仓库 owner 操作）。

---

## 8. 里程碑（分步交付）

按"先骨架、再内容分批"的节奏，每个 milestone 都能独立构建、可在浏览器查看：

- **M0 · 脚手架**：`src/shell.py`（设计系统 + 双语切换 + 导航）、`registry.py`、`build.py`、
  1-2 课样板内容 + index 页跑通；确定 Letta 主题色与品牌、双语切换交互。
- **M1 · 第一部分（宏观全景，3 课）**：含整体结构图与全景数据流，确立"图 + 伪代码 + 详尽"的内容基线。
- **M2 · 第二部分（前置基础，3 课）**。
- **M3 · 第三部分（记忆系统，6 课）** — **全书核心**，重点打磨。
- **M4 · 第四部分（agent 执行循环，4 课）**。
- **M5 · 第五部分（工具系统，4 课）**。
- **M6 · 第六部分（LLM provider 抽象，3 课）**。
- **M7 · 第七部分（服务端与持久化，4 课）**。
- **M8 · 第八部分（进阶专题 3 课 + 术语表 1 课）**。
- **M9 · 配套收尾**：quizzes 补全、`build_print.py` 双语 PDF、CI（deploy.yml / ci.yml）、README、LICENSE。

> 每个 milestone 内部再按课拆分；写实施计划时**分步逐段**，不一次写完。

---

## 9. 非目标 / YAGNI

- 不做账号、评论、后端服务、搜索引擎索引等动态功能（站点是纯静态）。
- 不逐行翻译/搬运 Letta 全部源码；只挑**讲清原理所需**的简化片段。
- 不追求覆盖每一个 provider 的每个细节；provider 部分以 OpenAI/Anthropic 为主线，其它做概览。
- 不深入前端/CLI 客户端（真正的 SDK 是外部 `letta-client` 包）；聚焦 server 端与 agent 内核。
- 不向 Letta 上游提交任何内容。

---

## 10. 成功标准

- 一个完全没接触过 Letta 的人，能顺着 1 → 31 课**一点点读懂**整个项目的结构与原理，
  尤其是**记忆三层 + 自我编辑记忆 + 上下文压缩**这条主线。
- 每课都能回答："这个组件**是什么功能**、**为什么这么写**、对应**哪些源码文件/符号**"。
- 站点可 `file://` 直接打开，也可部署到 GitHub Pages；可下载中/英 PDF。
- 中英双语切换顺滑、跨课保持；CI 防漂移与死链。
