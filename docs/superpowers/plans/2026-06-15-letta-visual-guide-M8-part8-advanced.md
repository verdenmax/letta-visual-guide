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
- `31-glossary.html` — zh「术语表·概念索引」/ en「Glossary & concept index」；副标题 zh「全书术语一句话查 + 跳链到对应课」/ en「every term in one line + jump links to its lesson」。（**注意：文件名必须是 `31-glossary.html`——`check_html.py` 的 `SOFT_EXEMPT` 已登记该名，豁免图/墙/CJK 软闸；但 en 内容仍需 ≥80 字、`<pre>` 转义、标签平衡，且跳链必须全解析。）

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

### 28（多智能体与 sleeptime）
- **关键纠正（务必照写）**：v0.16.8 里**真正活着的多智能体机制只有两个**：① sleeptime；② `send_message_to_agent_*` 工具。经典"群聊"管理器（`round_robin`/`supervisor`/`dynamic`）只剩 schema/`ManagerType` 枚举与类骨架——其执行器 `letta/groups/helpers.py::load_multi_agent` **从未被调用**，`/v1/groups` 路由整段 `deprecated=True` 且**无发消息端点**，`SupervisorMultiAgent.step` **整段注释掉**。讲课要把这三种讲成"schema 级/历史遗留"，用 tools+sleeptime 演示真正的多智能体。
- **Group 模型**：`letta/schemas/group.py::ManagerType{round_robin,supervisor,dynamic,sleeptime,voice_sleeptime,swarm}`；ORM `letta/orm/group.py::Group`（`manager_type`、`manager_agent_id`、`sleeptime_agent_frequency`、`turns_counter`、`agent_ids`(JSON)、`shared_blocks`(M2M `groups_blocks`)、`agents`(M2M `groups_agents`)）。`GroupManager.create_group_async` 对 sleeptime 设 `turns_counter=-1`（首回合即触发）。
- **多智能体工具**（`letta/functions/function_sets/multi_agent.py`，`ToolType.LETTA_MULTI_AGENT_CORE`，沙箱执行）：`send_message_to_agent_and_wait_for_reply(message, other_agent_id)`（**同步阻塞**，双向取回复）；`send_message_to_agents_matching_tags(message, match_all, match_some)`（**同步广播**，按标签筛 agent 逐个 wait）；`send_message_to_agent_async(message, other_agent_id)`（**异步单向**，prod 禁用，在 `LOCAL_ONLY_MULTI_AGENT_TOOLS`）。机制：工具体建 `letta_client.Letta` → `client.agents.messages.create(agent_id=other_agent_id, messages=[{"role":"system",...}])`，**经 REST 重入服务器、跑被叫 agent B 自己的完整 loop**（`AgentLoop.load(B).step`），不经"群管理器"；发送方身份自动注入 `[Incoming message from agent with ID '...']`。
- **sleeptime 机制**：接线 `letta/agents/agent_loop.py::AgentLoop.load`——`letta_v1_agent`/`sleeptime_agent` + `enable_sleeptime` + 有 group → `letta/groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4(LettaAgentV3)`（**它就是普通 loop 的子类**）。流程：`SleeptimeMultiAgentV4.step` 先 `await super().step(...)` 跑**前台**主 agent、存 `response_messages`，再 `run_sleeptime_agents()`：`group_manager.bump_turns_counter_async`（`(c+1)%frequency`）→ 命中（`%frequency==0`）则对 `group.agent_ids`（**后台 sleeptime agents**）逐个 `_issue_background_task`：建 `Run` + `safe_create_task(_participant_agent_step)`（**非阻塞 asyncio 后台任务**）。`_participant_agent_step` 把 `prior+response_messages` 拼成 transcript、包进 `<system-reminder>你是后台 sleeptime agent，职责是记忆管理…用记忆工具更新相关 block`，再以**完整 `LettaAgentV3`** 跑 `step`。
- **sleeptime 记忆工具（纠正）**：标准 sleeptime 用 `letta/constants.py::BASE_SLEEPTIME_TOOLS = ["memory_replace","memory_insert","memory_rethink","memory_finish_edits"]`，真正实现在 `letta/services/tool_executor/core_tool_executor.py::CoreToolExecutor`（`memory_rethink`→`agent_state.memory.update_block_value` + `agent_manager.update_memory_if_changed_async`；`memory_finish_edits`→返回 `None`）。**outline 里的 `rethink_memory`/`finish_rethinking_memory` 不是 v0.16.8 sleeptime 工具**：`rethink_memory`(`base.py`)是 legacy、`finish_rethinking_memory`(`voice.py`)是 voice_sleeptime 专用。标准 sleeptime 的"rethink"对应 **`memory_rethink`**。
- **共享块（协调基元）**：`letta/orm/blocks_agents.py::BlocksAgents`（复合 PK `(agent_id,block_id,block_label)`）让一个 `Block` 行挂到多个 agent（`Block.agents` ↔ `Agent.core_memory`，`secondary="blocks_agents"`）。`server.py::SyncServer.create_sleeptime_agent_async` 给 sleeptime agent 传 `block_ids=[b.id for b in main_agent.memory.blocks]`——**同一批 Block 行**。sleeptime 改写 → `block_manager.update_block_async`/`update_memory_if_changed_async` 写那一行（`Block` 有乐观锁 `version`）；主 agent 下一回合重建 system prompt 时读到新值——"睡醒带着更好的记忆"。
- **亮点**：sleeptime ＝ **把记忆整理实现成 agent 抽象的递归套用**——后台"记忆整理器"不是特殊子系统，就是**另一个 `LettaAgentV3`** 拿着 transcript + `sleeptime_memory_persona` + 记忆工具；协调基元只是**一个共享可变 `Block` 行**（A 写 B 读，无消息总线）。整个特性 = (同一个 loop) + (共享行) + (回合计数器)。推论：v0.16.8 根本没有专门的"多智能体运行时"，真多智能体行为来自 (a) 一个 agent 把另一个的消息 API 当沙箱工具调、(b) 两个 agent 指向同一个 block。
- **易错点**：`memory_rethink`（非 `rethink_memory`）；sleeptime 是**非阻塞**（更新落在回复之后、下回合才显现），而 `send_message_to_agent_and_wait_for_reply` **阻塞**；sleeptime 的 `manager_agent_id`＝**前台主 agent**、`group.agent_ids`＝后台编辑者（与直觉相反）；"共享块"共享的是**行不是副本**（peer 下次重建 prompt 才见、不自动广播）；round_robin/supervisor/dynamic **不能经 live API 跑**。
- **锚点**：`schemas/group.py::ManagerType`、`orm/group.py::Group`、`orm/blocks_agents.py::BlocksAgents`、`orm/block.py::Block`、`functions/function_sets/multi_agent.py`（三个 `send_message_to_agent_*`）、`agents/agent_loop.py::AgentLoop.load`、`groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4`、`services/group_manager.py::GroupManager`（`create_group_async`/`bump_turns_counter_async`）、`services/tool_executor/core_tool_executor.py::CoreToolExecutor`（`memory_rethink`/`memory_finish_edits`）、`server/server.py::SyncServer.create_sleeptime_agent_async`、`constants.py::BASE_SLEEPTIME_TOOLS`/`MULTI_AGENT_TOOLS`。

### 29（数据源与 RAG）
- **核心：RAG 与归档记忆是同一向量底座、不同来源**。`letta/orm/passage.py::BasePassage`（`__abstract__`，回扣第 27 课：`embedding = Vector(MAX_EMBEDDING_DIM)`/Postgres 或 `CommonVector`/SQLite，同一列、同 4096 填充、同 `cosine_distance`）。两个子类：`SourcePassage(BasePassage,FileMixin,SourceMixin)`（表 `source_passages`，`source_id`(必)+`file_id`(选)+`file_name`）vs `ArchivalPassage(BasePassage,ArchiveMixin)`（表 `archival_passages`，`archive_id`，有 `passage_tags` 标签 junction）。FK 来自 `orm/mixins.py::FileMixin/SourceMixin/ArchiveMixin`。
- **两条摄取路径**（都落到 `SourcePassage` 行）：**现代** `letta/services/file_processor/file_processor.py::FileProcessor.process`（`file_manager.create_file`(status=PARSING) → `file_parser.extract_text`(OCR/markdown) → `upsert_file_content`(表 `file_contents` 存全文) → `agent_manager.insert_file_into_context_windows`(开成 FileAgent) → `LlamaIndexChunker.chunk_text`(chunk_size 来自 EmbeddingConfig，回扣第 21 课) → `embedder.generate_embedded_passages`(batch=200) → `passage_manager.create_many_source_passages_async`)；**legacy** `letta/data_sources/connectors.py::load_data`（`DirectoryConnector` + llama_index `TokenTextSplitter`，调**已弃用**的 `create_many_passages_async`）。讲课以 file_processor 为主、提一句 legacy。
- **写入点**：`services/passage_manager.py::PassageManager.create_source_passage_async`/`create_many_source_passages_async`（守卫：必须有 `source_id`、**不能**有 `archive_id`；pad 到 `MAX_EMBEDDING_DIM`(pgvector，TPUF 跳过)；去 null 字节；`SourcePassage.batch_create_async`）。`create_agent_passage_async` 反之（必须 `archive_id`、不能 `source_id`）——两类相互排斥。
- **源的创建/挂载**：`services/source_manager.py::SourceManager.create_source`（org-scoped，`vector_db_provider` TPUF>Pinecone>NATIVE）；`agent_manager.py::AgentManager.attach_source_async` → 只写 `sources_agents` junction 行（**不复制 passage**）。`Source` 是 org 级、可被多 agent 共享（`orm/sources_agents.py::SourcesAgents` 复合 PK M2M）。
- **检索（同一向量搜索、不同工具/表）**：`services/helpers/agent_manager_helper.py::build_source_passage_query`（`select(SourcePassage)` join `SourcesAgents` on `source_id` where `agent_id`；嵌入查询 + pad 4096；Postgres `SourcePassage.embedding.cosine_distance(q).asc()`，SQLite numpy；文本兜底 `func.lower(text).contains`）；`build_agent_passage_query` 同形、join `ArchivesAgents` on `archive_id` + 标签过滤。工具：`semantic_search_files`（源）vs `archival_memory_search`（归档），**两个不同工具、同一套 pgvector cosine**。真正实现在 `tool_executor/files_tool_executor.py::LettaFileToolExecutor.semantic_search_files` 与 `core_tool_executor.py::LettaCoreToolExecutor.archival_memory_search`；`function_sets/base.py`/`files.py` 里的函数声明是 `raise NotImplementedError` 的 schema 占位。
- **文件的两种形态**：(a) 可搜索 RAG chunk = `SourcePassage`；(b) 上下文里的"打开的文件" = `letta/orm/files_agents.py::FileAgent`（junction `files_agents`，`is_open`/`visible_content`/`start_line`/`end_line`），`FileAgent.to_pydantic_block(...) → FileBlock(read_only=True)`——**开文件＝上下文里的只读记忆块**，`open_files`/`grep_files` 操作这层（默认最多 5 个开文件）。文件存储 `orm/file.py::FileMetadata`(表 `files`，`processing_status`/`total_chunks`/`chunks_embedded`) + `FileContent`(表 `file_contents`，全文)。
- **RAG vs 归档（一句话）**：归档＝agent **自己写**的长期记忆（`archival_memory_insert`/`search`，`archive_id`，第 10/11 课）；源＝**你上传**的外部文档（摄取管线建，`semantic_search_files`，`source_id`/`file_id`）；**底座同一**（`BasePassage` 的 `Vector(4096)` + 同 padding + 同 `cosine_distance`，第 27 课）。
- **亮点**：Letta 不另造"RAG 引擎"——它**复用归档记忆的向量机器**，只换表（`source_passages`↔`archival_passages`）、换 FK（`source_id/file_id`↔`archive_id`）、换 junction（`SourcesAgents`↔`ArchivesAgents`）、换工具名（`semantic_search_files`↔`archival_memory_search`）。来源是唯一真差别，检索物理是同一套。次亮点：一个挂载的文件**同时**以两种形态存在——embedded `SourcePassage`(语义召回) + 只读 `FileBlock`(上下文里的原文)。
- **易错点**：源/归档不混（不同表/FK/工具，互不返回；写入点互斥报错）；源是**可共享非 per-agent**；"挂载源"**只写 junction、不复制不重嵌**；嵌入模型/维度必须一致（pad 到 4096 会**静默掩盖维度不匹配**）；pad 仅 pgvector（TPUF/Pinecone 跳过）；`Source` 正被改名 **`Folder`**（`schemas/source.py::Source` docstring "Deprecated: Use Folder"、`PassageBase.source_id` 标 `deprecated`），但 v0.16.8 ORM 表/类仍是 `source_*`，源码照写 `source_`、注一句术语漂移。
- **锚点**：`orm/passage.py::BasePassage`/`SourcePassage`/`ArchivalPassage`、`orm/mixins.py::FileMixin`/`SourceMixin`/`ArchiveMixin`、`services/file_processor/file_processor.py::FileProcessor.process`、`services/file_processor/chunker/llama_index_chunker.py::LlamaIndexChunker`、`services/file_processor/embedder/openai_embedder.py::OpenAIEmbedder.generate_embedded_passages`、`services/passage_manager.py::PassageManager.create_(many_)source_passages_async`、`services/source_manager.py::SourceManager`、`services/agent_manager.py::AgentManager.attach_source_async`、`services/helpers/agent_manager_helper.py::build_source_passage_query`/`build_agent_passage_query`、`orm/files_agents.py::FileAgent`、`orm/file.py::FileMetadata`、`data_sources/connectors.py::load_data`（legacy）、`constants.py::MAX_EMBEDDING_DIM`/`EMBEDDING_BATCH_SIZE`。

### 30（jobs / runs / steps 与可观测性）
- **关键纠正（务必照写）**：嵌套是 **`Run ⊃ Step ⊃ StepMetrics`（外加 `Run`–`RunMetrics` 一对一）；`Job` 不是 Run 的父级，是平级的另一张表**。outline 的 "Job ⊃ Run ⊃ Steps" 错。
- **三实体（三张表/三个 manager）**：**Job**（`orm/job.py::Job` 表 `jobs`，`UserMixin`；**后台/批任务**，典型是加载+解析+嵌入文件；`schemas/enums.py::JobType{JOB,RUN,BATCH}`、`JobStatus{created,running,completed,failed,pending,cancelled,expired}`；`services/job_manager.py::JobManager`）。**Run**（`orm/run.py::Run` 表 `runs`，**一次 agent 调用**；`agent_id`(必)，`OrganizationMixin`；`Run.steps`(1:N, cascade)、`Run.messages`(1:N)；`schemas/enums.py::RunStatus{created,running,completed,failed,cancelled}`；`services/run_manager.py::RunManager.create_run` 同时写 `RunMetrics`(run_start_ns,num_steps=0)）。**Step**（`orm/step.py::Step` 表 `steps`，**一次 loop 迭代＝一次 LLM 调用 + 工具执行**；`run_id` FK；字段含 `model/provider_*`、per-step `prompt/completion/total_tokens`、`stop_reason`、**`trace_id`**(OTel)、`feedback`、`status`；`StepStatus{PENDING,SUCCESS,FAILED,CANCELLED}`；1:1 `Step.metrics`→`orm/step_metrics.py::StepMetrics`(llm_request_ns/tool_execution_ns/step_ns)；`Step.messages` 1:N；`services/step_manager.py::StepManager` + 单例 `NoopStepManager`）。
- **ID 串联**：`POST .../messages` → `RunManager.create_run`(`run-…`) → `agent_loop.step(run_id)` → `for i in range(max_steps): _step(run_id)` → 每个 `_step` `generate_step_id()`(`step-…`) → 写 `steps` 行 → 每条新 `Message` 盖 `run_id`+`step_id`（`letta_agent_v3.py::LettaAgentV3._checkpoint_messages`）。**一个 Run → ≤max_steps 个 Step → 每 Step 多条 Message**。
- **Step 在 loop 里怎么记**（回扣 13/14）：`LettaAgentV3._step` 内——① `_step_checkpoint_start`(`letta_agent_v2.py`)：建 `StepMetrics`、开 OTel span `tracer.start_span("agent_step")`、`StepManager.log_step_async(usage=0,0,0, status=PENDING, run_id, step_id, model, provider...)` **在 LLM 调用前就写 steps 行（零 token）**；② LLM + `_handle_ai_response`(工具)；③ `_step_checkpoint_finish`：算 `step_ns`、结束 span、`record_step_metrics_async`、`update_step_success_async(真实 per-step usage, stop_reason)` 翻成 SUCCESS；④ `_checkpoint_messages` 盖 run/step 持久化；⑤ `finally` 用 `StepProgression` 状态机（`START…FINISHED`）兜底：崩了就 `update_step_error_async`。**token**：`Step.total_tokens`＝单次 LLM；run 总量＝跨 Step 累加（`LettaAgentV2._update_global_usage_stats`，回扣第 14 课 `usage.total_tokens`）。
- **可观测性三套粒度**（别混）：① **steps 行**（产品+计费分析，per-step model/provider/tokens/stop/feedback）；② **OTel** `letta/otel/`（`tracing.py::trace_method`(第 25 课)开 `"{Class}.{method}"` span、`get_trace_id()` 写进 `Step.trace_id`；`metrics.py`/`metric_registry.py::MetricRegistry` 单例的 `ttft_ms_histogram`/`step_execution_time_ms_histogram`/`message_cost`/`sse_*` 等；`app.py` 启动时 gated on `otel_exporter_otlp_endpoint and not disable_tracing`，pytest 下 no-op）；③ **provider traces** `services/telemetry_manager.py::TelemetryManager`（按 `step_id` 存**原始 LLM 请求/响应**到 postgres/clickhouse/socket；默认 `NoopTelemetryManager`→None；经 `GET /v1/runs/{run_id}` trace 端点取）。`Step.trace_id = get_trace_id()` 把"产品行↔分布式 trace↔原始 payload"缝在一起。
- **流式 SSE（纠正）**：v3 实际走 `letta/services/streaming_service.py::StreamingService.create_agent_stream`（建 Run、存 Redis、`AgentLoop.load(...).stream(...)` 已产出 `data: {json}\n\n`；`_create_error_aware_stream` 兜 `[DONE]`/error；外面再包 cancellation/keepalive(`LettaPing`)/`_create_sse_lifecycle_stream`，最后 `streaming_response.py::StreamingResponseWithStatusCode(media_type="text/event-stream")`）。**outline 点名的 `server/rest_api/interface.py::StreamingServerInterface` 是 legacy**（deque 缓冲、`process_chunk`/`get_generator`/`step_complete` 给出"step=LLM 响应+工具执行"的权威定义），背后是旧 `agent.py`/OpenAI-proxy 路，不是 v3。SSE 线格式 `utils.py::sse_formatter`→`data: {json}\n\n`，终止 `data: [DONE]`，错误 `event: error`。流式事件类型：`ReasoningMessage`/`AssistantMessage`/`ToolCallMessage`/`ToolReturnMessage`/`LettaPing`/`LettaUsageStatistics`/`LettaStopReason`…
- **用户侧异步三态**：`messages`(streaming=false)→建 Run→跑 loop→`LettaResponse`，`finally` 里 `update_run_by_id_async` 置 completed/failed；`messages`(streaming=true)→SSE；`messages/async`→`send_message_async` **立即返回 background Run**、shielded 后台任务，**轮询 `GET /v1/runs/{run_id}`**（+ `/steps`/`/messages`/`/usage`/`/metrics`/trace；取消 `messages/cancel` 或 `RunManager.cancel_run`）。background 流式需 Redis，可经 `POST /v1/runs/{run_id}/stream` 重连（3h 过期）。
- **亮点**：第 14 课那个 `for` 循环，每个 `_step` 同时写出**三份关联视图**——steps DB 行（计费/产品）、OTel span（延迟/分布式追踪）、可选 provider trace（原始 payload），靠 `Step.trace_id` 缝合，一行就能跳到 trace、再跳到原始 LLM 调用。更妙：steps 行**在 LLM 调用前就以 PENDING/零 token 落库**、之后才翻 SUCCESS 填真实用量（`StepProgression` 状态机 + `finally` 兜底），所以崩溃/取消也留下可归因的持久记录。而同一个 loop 被**三种包装**（同步 `LettaResponse`、SSE 流、Redis 可恢复后台 Run），**只有外壳不同**——把进程内 `for` 循环变成可追踪/可取消/可恢复的异步资源。
- **易错点**：Job≠Run（异步 agent 消息建的是 background **Run** 不是 Job；jobs＝文件加载+批处理；历史上 run 曾是 `job_type=RUN` 的 job 行，那是 legacy 别讲）；嵌套是 `Run⊃Step` 不是 `Job⊃Run⊃Step`；Step 粒度＝一次 LLM+工具（不是 per-message/per-run）；持久化看 manager（sleeptime 子 agent / 旧 `LettaAgent` 默认 `NoopStepManager` 不写行；Run 要 `track_agent_run=True` 默认开；provider trace 默认 Noop；OTel 要配 endpoint）；per-step token vs 累计 token 别混。
- **锚点**：`orm/job.py::Job`、`orm/run.py::Run`、`orm/step.py::Step`、`orm/step_metrics.py::StepMetrics`、`schemas/enums.py::{JobType,JobStatus,RunStatus,StepStatus}`、`schemas/step.py::StepProgression`、`services/job_manager.py::JobManager`、`services/run_manager.py::RunManager`(`create_run`/`update_run_by_id_async`/`cancel_run`)、`services/step_manager.py::StepManager`(`log_step_async`/`update_step_success_async`/`record_step_metrics_async`)+`NoopStepManager`、`agents/letta_agent_v3.py::LettaAgentV3._step`/`_checkpoint_messages`、`agents/letta_agent_v2.py::LettaAgentV2._step_checkpoint_start`/`_step_checkpoint_finish`/`_update_global_usage_stats`、`otel/tracing.py`(`trace_method`/`get_trace_id`/`setup_tracing`)、`otel/metric_registry.py::MetricRegistry`、`services/telemetry_manager.py::TelemetryManager`、`services/streaming_service.py::StreamingService`、`server/rest_api/streaming_response.py::StreamingResponseWithStatusCode`、`server/rest_api/interface.py::StreamingServerInterface`(legacy)、`server/rest_api/routers/v1/agents.py::send_message`/`send_message_async`、`server/rest_api/routers/v1/runs.py`。

---

## Task 1: 新增第 28 课「多智能体与 sleeptime」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part8.py`(**新建** + `LESSON_28`) · `src/registry.py`(import part8 + CONTENT) · (可选)`src/quizzes.py`

**filename:** `28-multi-agent-sleeptime.html`；标题/副标题见「接线」。

**学习目标（Part-8 开篇）:** 讲清 Letta 在 v0.16.8 里**真正活着**的多智能体怎么玩。① 两条真路径：`send_message_to_agent_*` 工具（一个 agent 把另一个的消息 API 当沙箱工具调，经 REST 重入跑 B 自己的 loop）+ sleeptime（前台 agent 跑完，后台 sleeptime agent 每 N 回合被 `safe_create_task` 拉起去改记忆）。② 共享 `Block` 行（`blocks_agents` M2M）是唯一的协调基元：A 写 B 读、无消息总线。③ 经典群管理器（round_robin/supervisor/dynamic）只是 schema 级/历史遗留，不能经 live API 跑。回扣第 08/09（block + 自编辑记忆）、13/14（每个成员跑同一个 loop）、25（group_manager）。

**亮点（`card spark`）:** sleeptime ＝ **把"记忆整理"实现成 agent 抽象的递归套用**。后台那个"记忆整理器"不是什么特殊子系统——它就是**另一个 `LettaAgentV3`**（`SleeptimeMultiAgentV4` 干脆 *继承* 普通 loop），被丢进一段 transcript、戴上 `sleeptime_memory_persona`、给一套记忆工具，然后告诉它"你的活儿是整理记忆"。而两个 agent 之间的协调基元，朴素到只是**一个共享可变的 `Block` 行**：A 写、B 在下次重建 system prompt 时读到。于是整个特性 = (同一个 loop) + (一行共享记忆) + (一个回合计数器)。最反直觉的推论：v0.16.8 **根本没有专门的"多智能体运行时"**——round_robin/supervisor 那套是睡着的脚手架，真正的多智能体行为，全从"一个 agent 调另一个的 API"和"两个 agent 指向同一个 block"里**涌现**出来。

**必需卡片:** `lead`×2；`card macro`（两条真路径 + 共享块协调 + 群管理器是 schema 级，一张总图）；`card analogy`（**便利贴留言板**：白班店员(前台 agent)下班前，夜班整理员(sleeptime agent)把这天的便utes整理进同一块留言板(共享 block)，第二天白班一上班就看到整理好的版本；店员之间也能直接递条子(`send_message_to_agent`)）；`card detail`（落到 `functions/function_sets/multi_agent.py`、`groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4`、`orm/blocks_agents.py::BlocksAgents`、`core_tool_executor.py::CoreToolExecutor.memory_rethink`）；`card spark`（见上）；`card key`；`card warn`（易错点：是 `memory_rethink` **不是** `rethink_memory`；sleeptime **非阻塞**（落在回复之后、下回合才显现）vs `send_message_to_agent_and_wait_for_reply` **阻塞**；sleeptime 的 `manager_agent_id`＝**前台主 agent**、`group.agent_ids`＝后台编辑者；"共享块"共享的是**行不是副本**；round_robin/supervisor/dynamic **不能经 live API 跑**）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **多智能体两路 `cols`/`flow`**：左 tool 路（Agent A —`send_message_to_agent_and_wait_for_reply`→ Sandbox → `client.agents.messages.create(B)` → B 的 loop → 回复回灌）；右 sleeptime 路（前台 step → 计数器 → 后台 agent 改共享块）；底注"群管理器 schema 级、未接线"。
2. **sleeptime 时序 `vflow`**：User→前台 `super().step()`→`bump_turns_counter`（`%frequency==0`？）→命中则 `safe_create_task(_participant_agent_step)`(非阻塞) → sleeptime `step` → `memory_rethink` → 写共享 Block(version++) → 下回合前台重建 prompt 读到新值。
3. **共享块 `cellgroup`/`flow`**：一个 `Block` 行 ↔ `blocks_agents` ↔ 多个 agent（前台 + sleeptime 共享同一 `block_id`）。
4. **`.cute` 萌图**：😴 sleeptime agent 在主 agent"睡觉"时，悄悄把 🧠 记忆块擦改成更整洁的版本，气泡"睡醒记忆更好"。
5. **`ManagerType` `table.t`**：六种枚举 · 一行路由行为 · v0.16.8 状态（sleeptime=ACTIVE、其余 dormant/stub/未实现）。

**必需代码（2–3，`codefile`）:**
- A) `send_message_to_agent_and_wait_for_reply`（简化，源 `multi_agent.py`）：建 `letta_client.Letta` → `client.agents.messages.create(agent_id=other_agent_id, messages=[{"role":"system",...}])` → 取 assistant 回复。
- B) `SleeptimeMultiAgentV4`（简化，源 `sleeptime_multi_agent_v4.py`）：`step` 先 `super().step()` 再 `run_sleeptime_agents()`（`bump_turns_counter` → `%frequency` → 对 `group.agent_ids` `safe_create_task(_participant_agent_step)`）。
- C) `memory_rethink`（简化，源 `core_tool_executor.py`）：拒只读块 → `agent_state.memory.update_block_value(label, new_memory)` → `update_memory_if_changed_async` 写共享行。

**必需折叠（3–4）:** 经典群管理器为何是"睡着的脚手架"（`load_multi_agent` 从不被调、`/v1/groups` deprecated、`SupervisorMultiAgent.step` 注释掉）；sleeptime 触发节奏（`turns_counter=-1` 初值 + `%frequency` → 首回合也触发）；共享块的可见性（写一行、peer 下次重建 prompt 才见、乐观锁 `version`）；`send_message_to_agent_*` 三个变体（同步等待 / 标签广播 / 异步单向 prod 禁用）。

**自测题种子:** v0.16.8 真正能跑的多智能体是哪两条（tools + sleeptime）；sleeptime 的记忆工具叫什么（`memory_rethink` 等，非 `rethink_memory`）；sleeptime 的 `manager_agent_id` 是谁（前台主 agent）；两个 agent 怎么共享状态（同一个 `Block` 行经 `blocks_agents`）；`send_message_to_agent_and_wait_for_reply` 阻塞吗（阻塞）。

---

## Task 2: 新增第 29 课「数据源与 RAG」

**Files:** `src/shell.py` · `src/part8.py`(`LESSON_29`) · `src/registry.py` · (可选)`src/quizzes.py`

**filename:** `29-data-sources-rag.html`。

**学习目标:** 讲清 RAG 与归档记忆**同底座、不同来源**。① `SourcePassage`（你上传的文档）vs `ArchivalPassage`（agent 自己写的记忆）都是 `BasePassage` 子类，共用第 27 课那根 `Vector(4096)` 列、同 padding、同 `cosine_distance`。② 摄取管线 file→OCR→chunk→embed→`SourcePassage`（现代 `FileProcessor.process`；legacy `connectors.load_data` 提一句）。③ 检索：`semantic_search_files`（源）vs `archival_memory_search`（归档）是**两个工具、同一套向量搜索**。④ 挂载源只写 junction、不复制；一个文件同时以 `SourcePassage`(语义) + `FileBlock`(上下文原文) 存在。回扣第 10/11（归档/召回）、27（向量存储+padding）、21（EmbeddingConfig）。

**亮点（`card spark`）:** Letta **不另造"RAG 引擎"**——它直接复用归档记忆那套向量机器，只是把表、外键、junction、工具名各换一个。`SourcePassage`（你喂给 agent 的文档）和 `ArchivalPassage`（agent 自己写下的记忆）是同一个 `BasePassage` 的两个兄弟子类，骑着**同一根** `Vector(MAX_EMBEDDING_DIM)` 列、同一套 4096 padding、同一个 `cosine_distance` 排序（第 27 课）。"RAG"和"长期记忆"在物理层根本是一回事——**唯一的真差别是来源**（一个你给的、一个它写的）。次亮点：一个挂载的文件会**同时**活成两种形态——可语义搜索的 `SourcePassage` chunk，以及上下文窗口里那块只读的 `FileBlock`(原文)；同一次 `process()` 喂出来，却服务两种召回（grep/读 vs 语义）。

**必需卡片:** `lead`×2；`card macro`（摄取管线 + 两类 passage 同底座 + 两工具同搜索，一张总图）；`card analogy`（**同一个图书馆，两种藏书**：你捐的书(source/RAG) 和 馆员手写的读书笔记(archival)，都进同一套**按语义检索的索引**(向量列)，只是分两个书架(表)、用不同的检索单(工具)）；`card detail`（`orm/passage.py::SourcePassage`/`ArchivalPassage`、`services/file_processor/file_processor.py::FileProcessor.process`、`services/helpers/agent_manager_helper.py::build_source_passage_query`、`orm/files_agents.py::FileAgent`）；`card spark`（见上）；`card key`；`card warn`（易错点：源/归档不混（不同表/FK/工具、互不返回、写入互斥报错）；源**可共享非 per-agent**；"挂载源"**只写 junction、不复制不重嵌**；嵌入模型/维度必须一致（pad 到 4096 静默掩盖维度不匹配）；pad 仅 pgvector；`Source` 正改名 `Folder` 但 v0.16.8 仍 `source_*`；"开文件 FileBlock" ≠ "可搜索 passage"）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **摄取管线 `vflow`**：Upload → `FileManager.create_file`(PARSING) → `FileParser.extract_text`(OCR) → `upsert_file_content`(全文) → `insert_file_into_context_windows`(FileAgent) → `LlamaIndexChunker.chunk_text`(chunk_size=EmbeddingConfig) → `Embedder.generate_embedded_passages`(batch 200) → `create_many_source_passages_async`(pad 4096) → `SourcePassage` 行。
2. **两类 passage 一底座 `cols`**：左 ArchivalPassage（`archival_passages` · `archive_id` · `archival_memory_search` · join `ArchivesAgents`）/右 SourcePassage（`source_passages` · `source_id`+`file_id` · `semantic_search_files` · join `SourcesAgents`）；中间汇到 `BasePassage` 的 `Vector(MAX_EMBEDDING_DIM)` + `cosine_distance`（第 27 课）。
3. **文件两形态 `cellgroup`/`flow`**：一个文件 → `SourcePassage`(embedded, 语义搜) + `FileAgent`/`FileBlock`(visible_content, 上下文只读原文)。
4. **`.cute` 萌图**：📄 一份文档切成 📚 小卡片(chunk)、每张盖上 🔢 向量戳，排进 4096 维货架。
5. **source vs archival `table.t`**：表 · 来源 FK · 谁写 · 查询 builder · 工具 · 标签。

**必需代码（2–3，`codefile`）:**
- A) 摄取（简化，源 `file_processor.py::FileProcessor.process`）：create_file → extract_text → chunk → `generate_embedded_passages` → `create_many_source_passages_async`。
- B) 两类 passage（简化，源 `orm/passage.py`）：`BasePassage`(import 期 `Vector(MAX_EMBEDDING_DIM)`/`CommonVector`) → `SourcePassage(FileMixin,SourceMixin)` / `ArchivalPassage(ArchiveMixin)`。
- C) 源向量搜索（简化，源 `agent_manager_helper.py::build_source_passage_query`）：嵌入查询 + `np.pad` 4096 → `select(SourcePassage)` join `SourcesAgents` → `embedding.cosine_distance(q).asc()`。

**必需折叠（3–4）:** 两条摄取路径（现代 `file_processor` OCR vs legacy `connectors.load_data` 已弃用）；source vs archival 的强约束（写入点互斥、检索互不返回）；FileAgent/FileBlock 这层"上下文里的开文件"是另一套机制；嵌入配置必须一致 + pad 掩盖维度不匹配的坑；`Source`→`Folder` 术语漂移。

**自测题种子:** SourcePassage 和 ArchivalPassage 的共同底座是什么（`BasePassage` 的 `Vector(4096)` + `cosine_distance`，第 27 课）；它们差在哪（来源/表/FK/工具）；`archival_memory_search` 会返回上传文档的 chunk 吗（不会，那是 `semantic_search_files`）；"挂载一个源"做了什么（写 `sources_agents` junction，不复制 passage）；一个文件在 agent 里有哪两种形态（SourcePassage + FileBlock）。

---

## Task 3: 新增第 30 课「jobs / runs / steps 与可观测性」

**Files:** `src/shell.py` · `src/part8.py`(`LESSON_30`) · `src/registry.py` · (可选)`src/quizzes.py`

**filename:** `30-jobs-runs-steps.html`。

**学习目标:** 讲清一次 agent 执行怎么被**记录、追踪、流式吐出**。① 三实体三张表：**Run**（一次 agent 调用）⊃ **Step**（一次 LLM 调用+工具执行＝第 14 课 loop 的一迭代）⊃ `StepMetrics`；**Job** 是平级的后台/批任务（文件加载），**不是 Run 的父级**。② Step 在 loop 里**先以 PENDING/零 token 落库、后翻 SUCCESS 填真实用量**（`StepProgression` 兜底）。③ 可观测三套粒度：steps 行（计费）+ OTel span（延迟）+ provider trace（原始 payload），靠 `Step.trace_id` 缝合。④ 流式 SSE（v3 走 `StreamingService`，`StreamingServerInterface` 是 legacy）+ 异步 Run 轮询。回扣第 13/14（产出 step 的 loop）、24（建 Run 的路由）、25（`trace_method`）、03（每条 Message 盖 run/step）。

**亮点（`card spark`）:** 第 14 课那个朴素的 `for` 循环，每跑一个 `_step` 就同时甩出**三份互相关联的视图**：一条 `steps` DB 行（带 model/provider/per-step token/stop_reason——产品和**计费**分析）、一个 OTel `agent_step` span（延迟/分布式追踪）、以及可选的一条 provider trace（原始 LLM payload）。它们被 `Step.trace_id = get_trace_id()` 缝在一起——从一行产品记录能直接跳到分布式 trace，再跳到那次原始 LLM 调用。更妙的是 step 行**在 LLM 调用之前**就以 `PENDING`/零 token 落库、事后才翻 `SUCCESS` 填真实用量（靠 `StepProgression` 状态机 + `finally` 兜底），所以**连崩溃/取消的迭代都留下可归因的持久记录**。而同一个 loop 被**三种外壳**一包——同步 `LettaResponse`、SSE 流、Redis 可恢复的后台 Run——**只有壳不同**，一个进程内 `for` 循环就变成了可追踪、可取消、可恢复的异步资源。

**必需卡片:** `lead`×2；`card macro`（Run⊃Step⊃StepMetrics + Job 平级 + 三套可观测 + SSE，一张总图）；`card analogy`（**一次快递的轨迹**：一单(Run)拆成若干次扫描(Step)，每次扫描留时间戳+重量(StepMetrics/token)；后台仓储任务(Job)是另一条线；你能实时看轨迹推送(SSE)或事后查单号(轮询 Run)）；`card detail`（`orm/run.py::Run`/`orm/step.py::Step`/`orm/job.py::Job`、`agents/letta_agent_v2.py::LettaAgentV2._step_checkpoint_start/_finish`、`otel/tracing.py::get_trace_id`、`services/streaming_service.py::StreamingService`）；`card spark`（见上）；`card key`；`card warn`（易错点：**Job≠Run**（异步 agent 消息建的是 background Run 不是 Job）；嵌套是 `Run⊃Step` 不是 `Job⊃Run⊃Step`；Step 粒度＝一次 LLM+工具；持久化看 manager（sleeptime/旧 agent 用 `NoopStepManager` 不写行）；流式 v3 走 `StreamingService`、`StreamingServerInterface` 是 legacy；per-step token vs 累计 token 别混）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **嵌套 `cellgroup`/`flow`**：`Run`(runs, RunStatus)⊃`Step`(steps, StepStatus, trace_id)⊃`StepMetrics`；`Run`–`RunMetrics` 1:1；`Step`⊃`Message`；`Job`(jobs, JobStatus)**画在旁边、非父级**。
2. **step 在 loop 里落库 `vflow`**：`_step` → `_step_checkpoint_start`(开 span + `log_step_async` PENDING/0 token) → LLM+工具 → `_step_checkpoint_finish`(`update_step_success_async` 真实用量 SUCCESS + metrics) → `finally` `StepProgression` 兜底。
3. **三套可观测 `cols`**：steps 行(计费) / OTel span(延迟) / provider trace(原始 payload)，`Step.trace_id` 缝合。
4. **`.cute` 萌图**：🧾 每个 step 同时盖三个章——💰 计费、⏱️ 延迟、🔬 原始 payload，一根线串起来。
5. **异步三态 `table.t`**：sync(`messages`)→`LettaResponse` / stream(`messages` SSE)→`data:…\n\n` / async(`messages/async`)→轮询 `GET /runs/{id}`。

**必需代码（2–3，`codefile`）:**
- A) step 落库（简化，源 `letta_agent_v2.py` checkpoint）：`log_step_async(usage=0,0,0, status=PENDING, run_id, step_id, ...)` → … → `update_step_success_async(真实 usage, stop_reason)`。
- B) 路由建 Run + 生命周期（简化，源 `routers/v1/agents.py::send_message`）：`RunManager.create_run(...)` → `AgentLoop.load(...).step(run_id=run.id)` → `finally: update_run_by_id_async(status=...)`。
- C) SSE 流（简化，源 `streaming_service.py` + `utils.py::sse_formatter`）：`async for chunk in agent_loop.stream(...): yield chunk`；兜 `data: [DONE]`。

**必需折叠（3–4）:** Job vs Run vs Step 各是什么 + 正确嵌套（`Run⊃Step`，Job 平级）；step 的 `StepProgression` 兜底为什么能让崩溃也留记录；三套可观测（steps 行 / OTel `letta/otel/` / provider trace `telemetry_manager`）各管什么 + 默认开关；流式 v3（`StreamingService`）vs legacy（`StreamingServerInterface`）+ 异步 Run 轮询/Redis 恢复。

**自测题种子:** Run/Step/Job 的正确嵌套（Run⊃Step；Job 平级，非父级）；一个 Step 是什么粒度（一次 LLM 调用+工具执行）；异步 agent 消息建的是 Run 还是 Job（background Run）；`Step.trace_id` 把哪几样缝在一起（steps 行↔OTel trace↔provider payload）；v3 的流式走哪个（`StreamingService`，非 `StreamingServerInterface`）。

---

## Task 4: 新增第 31 课「术语表·概念索引」（**特例结构**）

**Files:** `src/shell.py` · `src/part8.py`(`LESSON_31`) · `src/registry.py`

**filename:** `31-glossary.html`（**必须用这个名**——已在 `check_html.py::SOFT_EXEMPT`，豁免 图/墙/CJK 软闸；但 en ≥80 字、`<pre>` 转义、标签平衡、**跳链全解析** 仍是硬闸）。

**学习目标:** 给全书做一本**好查的速查手册**：每个核心术语**一句话定义** + **跳链到首讲它的课**。不是又一篇深挖长文，而是索引。

**结构（与前面不同，无 6 卡/无 ≥4 图硬性）:**
- 开头 `lead` ×1–2：说明这是速查索引、怎么用（点术语跳到对应课）。
- 用**分组**组织（每组一个 `<h2>` + 一张 `table.t` 或定义列表）：
  - **记忆系统**：core/recall/archival memory、`Block`、`Passage`、`SourcePassage`/`ArchivalPassage`、compaction → 课 07–12、27、29。
  - **Agent 执行**：`AgentState`、agent loop（V3）、`_step`、heartbeat、tool rule、`ToolRule` → 课 13–16。
  - **工具系统**：tool=function、schema 派生、dispatch、MCP、sandbox → 课 17–20。
  - **LLM Provider**：`LLMClient`、三方法契约、`ChatCompletionResponse`、inner_thoughts、GBNF → 课 21–23。
  - **服务端/持久化**：`SyncServer`、Manager、`db_registry`、`SqlalchemyBase`、`apply_access_predicate`、actor、多租户、`database_engine`、pgvector → 课 24–27。
  - **进阶**：group、sleeptime、shared block、source/RAG、`FileAgent`、Run/Step/Job、observability、SSE → 课 28–30。
- 每行：**术语（zh + en/原词）· 一句话定义 · `<a href="NN-....html">第 NN 课</a>` 跳链**。
- 跳链用**相对文件名**（同目录 `lessons/`，如 `href="08-memory-blocks.html"`）。**务必逐一核对文件名真实存在**（用 `glob`/`ls lessons/`），否则 `check_links` 报错。
- 末尾一句过渡：正文到此为止，配套（quizzes/PDF/CI）在收尾里。可加 1 个 `.cute`（📖 一本翻开的速查手册）点缀，但非硬性。

**双语:** zh、en 两份**信息等价**（术语原词如 `Block`/`AgentState` 两边都保留英文符号，定义分别中/英）。

**自测题:** 术语表一般**不配 quiz**（它是索引）。Phase B 只做 en 镜像 + 跳链复核，不加 `QUIZZES` 条目。

---

## Task 5: 集成与合并（M8 收尾）

**Files:** `docs/superpowers/plans/2026-06-15-letta-visual-guide-roadmap.md` · （验证）全站

- [ ] 全量构建：`cd src && python build.py && python check_links.py && python check_html.py`，期望 `0 error / 0 warning`、链接全解析、index pill「共 31 课 · 8 个部分」。
- [ ] 导航链抽查：`27→28→29→30→31`，每课 `prev/next` 各 1，31 课 `next=../index.html`。术语表跳链全部解析。
- [ ] roadmap 把 **M8** 标 `✅ 已完成并合并`（计划文档名填入）。
- [ ] 合并：`git checkout master && git merge --no-ff feat/m8-advanced`；合并后再跑三件套确认绿。
- [ ] `git branch -d feat/m8-advanced`；`git push origin master`。
- [ ] 报告 M8 完成，**自动继续 M9**（配套收尾：quizzes 补全 / 双语 PDF / CI / README / LICENSE）——用户已要求一路做完全部 M。

---

## Self-Review（写完即查）
## Self-Review（写完即查）
1. **Spec coverage**：spec 第八部分 28–31 ↔ Task 1–4 一一对应（多智能体+sleeptime ✓、数据源+RAG ✓、jobs/runs/steps+可观测 ✓、术语表 ✓）。✅
2. **Placeholder scan**：无 TBD/TODO；前三课给 filename/学习目标/亮点/卡片/图/代码/折叠/自测题；第 31 课给特例结构 + 分组 + 跳链规则。✅
3. **Type/name consistency**：全程用 `send_message_to_agent_*`/`SleeptimeMultiAgentV4`/`memory_rethink`/`blocks_agents`/`SourcePassage`/`ArchivalPassage`/`BasePassage`/`FileProcessor`/`build_source_passage_query`/`FileAgent`/`Run`/`Step`/`Job`/`StepMetrics`/`StepProgression`/`StreamingService`/`trace_id`/`get_trace_id`，与"已核实锚点"一致。✅
4. **outline 纠正已固化**：经典群管理器(round_robin/supervisor/dynamic)是 schema 级/未接线；sleeptime 工具是 `memory_rethink` 非 `rethink_memory`；sleeptime `manager_agent`=前台；RAG 与归档同 `BasePassage` 底座；嵌套是 `Run⊃Step`、`Job` 平级；流式 v3 走 `StreamingService` 非 `StreamingServerInterface`；术语表文件名 `31-glossary.html`(SOFT_EXEMPT)。✅
5. **跨课一致**：28 复用 08/09 的 block + 13/14 的 loop；29 复用 27 的向量底座 + 10/11 的归档；30 把 13/14 的 loop 变成可观测的 Run/Step；31 把全书术语串成索引、跳链回各课。整 Part 收口"正文完结 → 进阶专题 → 速查手册"，过渡到 M9 配套收尾。✅
