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

### 24（三层架构）
- **请求路径**：REST 路由（薄）→ `SyncServer` + Managers（业务 + session）→ ORM（CRUD + 访问控制）→ DB。**唯一一个全局 `SyncServer`**。
- **关键纠正（outline 略偏）**：路由**不**把 CRUD 都走 `SyncServer` 方法——而是通过 server 对象**直接调 manager**（`server.agent_manager.get_agent_by_id_async(...)`），只有**跨多个 manager 的编排**才调 `SyncServer` 自己的方法（如 `server.create_agent_async`）。`agents.py` 里约 131 次 manager-直调 vs 16 次 SyncServer-方法。
- **全局 server 的诞生**：`letta/server/rest_api/app.py::server`＝**模块级全局**（`server = SyncServer(default_interface_factory=lambda: interface())`），**import 时**就建好（`create_application` 里那行 `SyncServer(...)` 是注释掉的）。`app.py::lifespan` 只做**异步引导** `await server.init_async(init_with_default_org_and_user=...)`（建默认 org/user、upsert 基础工具）。两段式：import 时同步接线 + 启动时异步 init。
- **共享方式**：`letta/server/rest_api/dependencies.py::get_letta_server` **惰性 import** 那个模块全局并返回（不放 `app.state`）；路由用 `Depends(get_letta_server)` 拿到同一个 server。
- **`SyncServer.__init__` 接线**：持有全部 manager 作属性——`organization_manager`/`user_manager`/`tool_manager`/`block_manager`(或 `GitEnabledBlockManager`)/`message_manager`/`passage_manager`/`source_manager`/`agent_manager`(`AgentManager(block_manager=self.block_manager)`，**manager 间组合**)/`provider_manager`/`step_manager`/`job_manager`/`run_manager`/`archive_manager`/… + `self.config`(LettaConfig) + `self._enabled_providers`。**无消息队列**（outline 写错）。
- **薄路由 4 步**：① `actor = await server.user_manager.get_actor_or_default_async(actor_id=headers.actor_id)` ② 轻量参数处理 ③ 调 manager/server 方法 ④ 返回 pydantic schema（FastAPI `response_model`）。actor 解析在**处理函数体内**（不是中间件）；`dependencies.py::get_headers` 只把 `Header(alias="user_id")` 解析/校验成 `HeaderParams.actor_id`（不碰 DB）。
- **端到端轨迹**（`GET /v1/agents/{id}` → `agents.py::retrieve_agent`）：DI 给 server + 解析 user_id → `get_actor_or_default_async`（session#1 查 user）→ `server.agent_manager.get_agent_by_id_async(actor=actor)`（session#2：`select(AgentModel)` + `apply_access_predicate(...ORGANIZATION)` + `where(id==...)`）→ `scalar_one_or_none()`（None→404）→ `to_pydantic_async()` → commit/close → FastAPI 按 `response_model=AgentState` 序列化。**一次请求＝多个独立事务**（无请求级 UoW）。
- **亮点**：`SyncServer` 是**误名**——其实是 async（类 docstring 还写着"single-threaded / blocking"是遗留）；它是**服务定位器/枢纽**不是上帝门面（薄 CRUD 端点绕过它直调 manager，它自己的方法只做跨-manager 编排）；事务边界在 manager 不在请求；多租户就一行 `apply_access_predicate`（且 `del access`，目前只做 org 级）；**FastAPI DI 是分层接缝**。
- **锚点**：`letta/server/rest_api/app.py`（`server`/`create_application`/`lifespan`）、`server/server.py::SyncServer`、`rest_api/dependencies.py::get_letta_server`/`get_headers`、`rest_api/routers/v1/agents.py::retrieve_agent`、`rest_api/middleware/check_password.py::CheckPasswordMiddleware`。

### 25（服务层 Managers）
- **canonical manager 形状**：`async with db_registry.async_session() as session:` → **actor 范围**的 ORM CRUD/查询 → **在 session 内** `to_pydantic()`/`to_pydantic_async()` 转 pydantic → 返回 pydantic（**绝不返回 ORM 行**）。最简范例 `OrganizationManager.get_organization_by_id_async`：`OrganizationModel.read_async(...)` → `org.to_pydantic()`。
- **db_registry 接缝**：`letta/server/db.py::DatabaseRegistry`（整类 docstring＝**"Dummy registry to maintain the existing interface."**），进程级单例 `db_registry`；v0.16.8 **只暴露 `async_session()`**（`@asynccontextmanager`，干净退出 commit、异常/CancelledError rollback、finally `expunge_all()`+`close()`），**没有同步 `session()`**。模块级 `engine = create_async_engine(async_pg_uri, ...)` + `async_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)`。
- **装饰器**（统一横切）：`letta/utils.py::enforce_types`（**同步** wrapper，`get_type_hints` 校验入参，不符 `raise ValueError`；async 方法上它先同步校验再返回协程）；`letta/otel/tracing.py::trace_method`（OTel span，名 `"{ClassName}.{method}"`；`_is_tracing_initialized=False` 时纯透传；跳过 `messages`/`embeddings` 等大参）；常叠 `letta/validators.py::raise_on_invalid_id`（校验前缀 id，`LettaInvalidArgumentError`）。典型栈 `@enforce_types`→`@raise_on_invalid_id`→`@trace_method`→方法。
- **schema↔ORM 边界**：ORM→pydantic 在 **ORM 类**上：`sqlalchemy_base.py::SqlalchemyBase.to_pydantic`＝`self.__pydantic_model__.model_validate(self, from_attributes=True)`；每个 ORM 模型声明 `__pydantic_model__`（如 `orm/agent.py → PydanticAgentState`）；复杂模型重写 `to_pydantic_async`（手搭关系）。pydantic→ORM＝`model_dump(to_orm=True)`（`schemas/letta_base.py::LettaBase.model_dump` 把 `metadata→metadata_`），喂给 ORM 构造器。**没有 `to_record()`/`to_orm()` 方法**（outline 写错）。
- **为何独立成层**：事务归属（唯一开 session 处）、actor/org 范围（唯一 `apply_access_predicate` 处）、跨调用方复用（REST 路由 / agent 循环 / 别的 manager）、装饰器给统一 typing+tracing。
- **亮点**：同一行 `async_session()` 既定事务边界又定租户范围——路由/循环永远看不到 session 或 `WHERE organization_id`，**隔离没法被忘**；`db_registry` 自称"Dummy registry"——上百处 `db_registry.async_session()` 调用点一字不改，底下实现被收成一个模块级 asyncpg 引擎（**接口即契约，引擎可换**）；**转换在 session 内**是性能模式（`get_agent_by_id_async` 甚至"先不解密转 pydantic、释放连接后再跑 PBKDF2"）。
- **纠正**：db.py 在 v0.16.8 是 **Postgres-only**，不在此层分 SQLite/Postgres；方言透明是 ORM 层（column 类型/查询 helper/`__init__.py` 注册 sqlite_functions）的事，不是 db_registry 的特性。
- **锚点**：`letta/services/agent_manager.py`/`organization_manager.py`/`block_manager.py`/`message_manager.py`/`passage_manager.py`、`server/db.py::DatabaseRegistry`、`utils.py::enforce_types`、`otel/tracing.py::trace_method`、`validators.py::raise_on_invalid_id`、`orm/sqlalchemy_base.py::SqlalchemyBase.to_pydantic`、`schemas/letta_base.py::LettaBase.model_dump`。

### 26（通用 CRUD 与多租户隔离）
- **CRUD 面**（`letta/orm/sqlalchemy_base.py::SqlalchemyBase`，`__abstract__`，给所有模型）：`read_async`/`list_async`/`read_multiple_async`/`size_async`（读，**有 actor 才**走访问控制）、`create_async`/`update_async`（写，盖审计字段）、`delete_async`（**软删**＝`is_deleted=True`，行留库）、`hard_delete_async`（物理删）、`bulk_hard_delete_async`（**在 SQL 层套 predicate**）、`apply_access_predicate`。读/写四参：`actor`、`access=["read"]`、`access_type=AccessType.ORGANIZATION`、`check_is_deleted=False`。
- **`apply_access_predicate(query, actor, access, access_type=ORGANIZATION)`**：开头 `del access`（read/write/admin **目前是 no-op**，是将来行级权限的占位）；`AccessType.ORGANIZATION`→`query.where(cls.organization_id == actor.organization_id)`；`AccessType.USER`→`where(cls.user_id == actor.id)`（**仅 jobs/runs 用**）。`AccessType(str,Enum){ORGANIZATION,USER}`。`organization_id`/`user_id` 来自 `orm/mixins.py::OrganizationMixin`/`UserMixin`。
- **"访问违规不报错"**：跨租户的行被 WHERE 直接排除→`read_async` 抛 `NoResultFound`、`list_async` 返回 `[]`。唯一的 `ValueError` 是 actor 没有 org/id accessor（配置错）。
- **软删 vs 硬删**：`delete_async`（有 actor 则盖审计、`is_deleted=True`、内部 `update_async`）；`hard_delete_async`（`session.delete(self)`+死锁重试，actor 仅日志）；`bulk_hard_delete_async`（`delete(cls).where(id.in_(...))` + `apply_access_predicate`，唯一在 SQL 层强租户的删）。**读侧过滤软删是 opt-in**：`check_is_deleted` 默认 `False`→**软删行默认仍被返回**；实战 `provider_manager.py` 删时软删、读/列时 `check_is_deleted=True`。
- **审计字段**（`letta/orm/base.py::CommonSqlalchemyMetaMixins`）：`created_at`（`server_default=func.now()`）、`updated_at`（`server_default`+`server_onupdate`）、`is_deleted`（默认 FALSE）、`created_by_id`(物理列 **`_created_by_id`**)/`last_updated_by_id`(物理 **`_last_updated_by_id`**)。盖法**不是事件监听**，是 CRUD 里显式调 `_set_created_and_updated_by_fields(actor_id)`（`created_by_id` 只首次设、`last_updated_by_id` 每次写）——**只有传 actor 才盖**。属性 setter 断言 id 前缀＝`"user"`。
- **actor/鉴权链（secure by default）**：`dependencies.py::get_headers`（`Header(None, alias="user_id")`，校验 `user-<uuid4>` 格式，不碰 DB）→ 处理函数体 `server.user_manager.get_actor_or_default_async(actor_id=...)`：`settings.no_default_actor` 且无 id → `raise NoResultFound`；否则回退 `DEFAULT_USER_ID`（缺则建默认 user）。返回 `PydanticUser`（带 `organization_id`，默认 `DEFAULT_ORG_ID`）。**服务器口令**（正交、整服务器级）：`middleware/check_password.py::CheckPasswordMiddleware`（`X-BARE-PASSWORD: password <pw>` 或 `Authorization: Bearer <pw>`，放行健康探针，否则 401），**仅 secure 模式**（`LETTA_SERVER_SECURE=true`/`--secure`）挂载；单一共享密钥，**与租户无关**。
- **关键安全细节**：actor=None 时 base **不硬失败**——记 `SECURITY: ...without actor... bypasses organization filtering` 警告并**无范围地**跑（因为有合法的系统内部无 user 查询）。即"**传了 actor 才安全**＋中央强制＋响亮告警"，不是无条件保证。默认 org 级（同 org 所有用户共享行：Block/Passage/Agent/Tool…），仅 jobs/runs 用户私有。
- **亮点**：隔离在**查询构造器**不在 handler——~40 个模型共一个 `SqlalchemyBase`，"按调用者 org 限定每次读"只实现一次、自动套在 `read_async`/`list_async`/`size_async`/`bulk_hard_delete_async`；新功能作者写**零**租户 SQL，只要把 actor 串下去（路由→manager 的路径让这成为阻力最小路径）。配上**软删可恢复**＋**审计四件套可追溯**——多租户+可恢复+可审计全是**一个抽象类**的属性。
- **锚点**：`letta/orm/sqlalchemy_base.py::SqlalchemyBase`（`read_async`/`list_async`/`delete_async`/`bulk_hard_delete_async`/`apply_access_predicate`/`AccessType`）、`orm/base.py::CommonSqlalchemyMetaMixins`、`orm/mixins.py::OrganizationMixin`/`UserMixin`、`services/user_manager.py::UserManager.get_actor_or_default_async`、`rest_api/dependencies.py::get_headers`、`rest_api/middleware/check_password.py::CheckPasswordMiddleware`。

### 27（双数据库与向量存储 · Part-7 终章）
- **唯一开关**：`letta/settings.py::Settings.database_engine`（**`@property` 不是字段**）→ `DatabaseChoice.POSTGRES if self.letta_pg_uri_no_default else DatabaseChoice.SQLITE`。`DatabaseChoice(str,Enum){POSTGRES,SQLITE}`。**真正的 dev/prod 切换**＝有没有配 PG URI（`letta_pg_uri` 总有默认 `postgresql+pg8000://letta:letta@localhost:5432/letta`；`letta_pg_uri_no_default` 才是 URI-或-None）。**没有 `LETTA_DATABASE_ENGINE=sqlite`**——设任一 `pg_*` 就静默翻成 Postgres。
- **关键纠正（outline 错）**：v0.16.8 `letta/server/db.py` **是 Postgres-only async**（在 `0.16.8` tag SHA `980e3ec` 核实）——**不**按 `database_engine` 建 SQLite 引擎、**不**在此加载 sqlite-vec。唯一构造 SQLite URI 的地方是 `alembic/env.py`。
- **"双库"接缝是分布式/声明式的**（没有单一 switch）：① `settings.database_engine`（property）② `orm/passage.py::BasePassage`：**import 时**类体 `if POSTGRES: embedding = mapped_column(Vector(MAX_EMBEDDING_DIM)) else: Column(CommonVector)`（pgvector 定长 4096 vs BINARY blob）③ `orm/sqlalchemy_base.py` + `services/helpers/agent_manager_helper.py` 的向量搜索**运行时**两分支 ④ `orm/sqlite_functions.py::register_functions`（`@event.listens_for(Engine,"connect")`，给**任何** SQLite 连接注册 **numpy** `cosine_distance` UDF；**`sqlite_vec.load()` 是注释掉的**）⑤ `orm/custom_columns.py` ⑥ `alembic/env.py`（POSTGRES→pg8000 同步 URI；else→`sqlite:///…sqlite.db`）。
- **向量两套存/搜**：Postgres＝pgvector `Vector(4096)` + `cls.embedding.cosine_distance(...)`→SQL `<=>`（可用 ivfflat/hnsw 索引）；SQLite＝`CommonVector` BINARY + `func.cosine_distance(...)` 走**Python numpy UDF**、`ORDER BY` 全表暴力（无 ANN）。`letta/constants.py::MAX_EMBEDDING_DIM = 4096`（"别改否则要重置库"）；写路径/查询向量都 `np.pad` 到 4096。**零填充让 cosine 完全不变**（点积+0、L2 范数+0）——这就是一个定长 `Vector(4096)` 列能装任意模型输出的原因。SQLite UDF `validate_and_transform_embedding` 也要求维度==4096，否则返回 0.0。
- **pydantic-in-DB（custom_columns）**：`orm/custom_columns.py` 每个类继承 `TypeDecorator`（`cache_ok=True`）委托 `helpers/converters.py`。`EmbeddingConfigColumn`/`LLMConfigColumn`/`ToolRulesColumn`（`impl=JSON`：`process_bind_param`=pydantic→`model_dump(mode="json")`、`process_result_value`=dict→pydantic；`deserialize_llm_config` 还做 schema-on-read 兜底默认）；`CommonVector`（`impl=BINARY`：`serialize_vector`=`sqlite_vec.serialize_float32`、`deserialize_vector`=`np.frombuffer`）。**配置存一列 JSON**→关系 schema 保持扁平、加 pydantic 字段**免迁移**（反序列化填默认）；代价：子字段不可 `WHERE`/索引、每次读写有 (de)序列化开销。
- **alembic 两后端**：Postgres＝从 `9a505cc7eca9` 起的增量链（早期 Postgres-gated：`if not settings.letta_pg_uri_no_default: return`）；SQLite＝单个 baseline 快照 `2c059cad97cc`（反向 guard `if settings.letta_pg_uri_no_default: return`，用纯 `sa.JSON()` 一次建全 schema）；baseline 之后的迁移两边都跑、内联处理方言差（`CURRENT_TIMESTAMP` vs `now()`）。
- **纠正**：v0.16.8 **没有 `AgentPassage` ORM 类**（只 `SourcePassage`/`source_passages` 和 `ArchivalPassage`/`archival_passages`）；SQLite 相似度是 **numpy UDF 不是 sqlite-vec 原生**（`sqlite_vec.load()` 注释掉，仅用其 `serialize_float32`）。
- **亮点**："同一套代码两套库"**不是 db.py 的聪明 switch——根本没有单一 switch**：派生 property + 类体 import 期 `if`（把 embedding 列类型烤进模型，**进程被特化到一种后端、运行时不能切**）+ 查询构造器两行 `order_by` 分支 + 全局 connect 事件注入 numpy UDF + alembic env 选 URI。pydantic-in-DB 是另一半（配置当 JSON blob，schema-on-read 演化，**保真胜过范式化**）。`MAX_EMBEDDING_DIM=4096` 是安静的拱顶石（零填充使 cosine 排序与未填充**数学等价**）。**诚实的星号**（很好的教学点）：v0.16.8 引擎层已悄悄收敛到 Postgres——双引擎故事在 ORM/alembic 完全活着，但 `server/db.py` 只建 Postgres。
- **锚点**：`letta/settings.py::Settings.database_engine`/`DatabaseChoice`/`letta_pg_uri`/`letta_pg_uri_no_default`、`server/db.py`、`database_utils.py::get_database_uri_for_context`、`orm/passage.py::BasePassage`/`SourcePassage`/`ArchivalPassage`、`orm/custom_columns.py`（`EmbeddingConfigColumn`/`LLMConfigColumn`/`ToolRulesColumn`/`CommonVector`）、`helpers/converters.py`、`orm/sqlite_functions.py`（`register_functions`/`cosine_distance`/`adapt_array`）、`constants.py::MAX_EMBEDDING_DIM`、`alembic/env.py`。

---

## Task 1: 新增第 24 课「三层架构」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part7.py`(**新建** + `LESSON_24`) · `src/registry.py`(import part7 + CONTENT) · (可选)`src/quizzes.py`

**filename:** `24-three-layer-architecture.html`；标题/副标题见「接线」。

**学习目标（Part-7 开篇）:** 讲清一条 HTTP 请求怎么穿过三层落到 DB。① **薄路由**：`Depends(get_letta_server)` 注入唯一全局 server、`Depends(get_headers)` 解析 `user_id`，处理函数体内 4 步（actor → 调 manager → 返回 schema）。② **`SyncServer` 是枢纽**：import 时建好的模块级全局，持有全部 `*_manager`；薄 CRUD **直调 manager**，只有跨-manager 编排才走 server 方法。③ **事务在 manager、不在请求**：一次请求＝多个独立 session；路由从不开 DB session。为 25（manager）、26（CRUD/隔离）、27（DB）铺路；回扣第 03 课（消息生命周期）、13/14（被 server 拉起的 agent 循环）。

**亮点（`card spark`）:** `SyncServer` 是个**美丽的误名**——类 docstring 还写"single-threaded / blocking"，但 v0.16.8 里路由调到的几乎全是 `async def`，真正的并发模型是单事件循环上的协作式 async。更妙的是它**不是上帝门面而是服务定位器**：薄端点根本绕过它、`server.<manager>.<method>()` 直穿，`SyncServer` 自己的方法只在"一个动作要协调好几个 manager"时才出场（`create_agent_async` 解析 LLM/embedding 配置、变换 block、把写委托给 `agent_manager`）。于是"业务枢纽"＝**跨-manager 协调者**，不是"通往 DB 的唯一一道门"。再点一层：**FastAPI 的 `Depends` 就是分层接缝**——两个依赖把一个普通函数变成分层 handler，actor 在 header 依赖跑完后于函数体内解析，而非全局鉴权中间件。

**必需卡片:** `lead`×2；`card macro`（三层 + 全局 server + 一次轨迹，一张总图）；`card analogy`（**三层楼的公司**：前台/路由只登记转交，中层/经理才有权动档案、且自己开关"事务"这道门，档案室/ORM 给谁看由门禁定）；`card detail`（落到 `app.py::server`/`create_application`/`lifespan`、`server.py::SyncServer`、`dependencies.py::get_letta_server`/`get_headers`、`routers/v1/agents.py::retrieve_agent`）；`card spark`（误名 async + 服务定位器非门面 + DI 即接缝）；`card key`；`card warn`（易错点：路由**不是**都经 `SyncServer` 方法，多数直调 manager；`SyncServer` 名同步实异步；actor 解析在函数体不是中间件；路由**从不**开 DB session；缺 `user_id` 在 OSS 模式默认落到 default user；server 在 **import** 时建、不在 factory；**无消息队列**）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **分层调用图 `layers`/`flow`**：HTTP → 薄路由（`retrieve_agent`）→ `SyncServer`+Managers（`server.agent_manager...`）→ ORM（`select`+`apply_access_predicate`）→ DB（`async_session`）。
2. **一次请求时序 `vflow`**：`get_letta_server`/`get_headers` → `get_actor_or_default_async`(session#1) → `get_agent_by_id_async`(session#2) → `to_pydantic_async` → `response_model` 序列化；旁注**两个独立事务**。
3. **`SyncServer` 持有的 managers `cellgroup`**：`agent_manager · message_manager · block_manager · passage_manager · user_manager · tool_manager · provider_manager · …`。
4. **`.cute` 萌图**：🏛️ 三层楼，🚪 门房（路由）只递条子，🧑‍💼 经理（manager）开"事务"门，🗄️ 档案室（ORM/DB）。
5. **薄 vs 厚 `.note`**：薄路由 4 步 vs manager 里的业务/事务/隔离。

**必需代码（2–3，`codefile`）:**
- A) app 工厂 + 全局 server + DI（简化，源 `app.py`/`dependencies.py`）：模块级 `server = SyncServer(...)`、`lifespan` 里 `await server.init_async(...)`、`get_letta_server` 惰性 import 返回全局。
- B) 薄路由 4 步（源 `agents.py::retrieve_agent`）：`Depends(get_letta_server)`+`Depends(get_headers)` → `get_actor_or_default_async` → `server.agent_manager.get_agent_by_id_async(actor=...)`。
- C)（可选）`SyncServer.__init__` manager 接线节选（源 `server.py`）。

**必需折叠（3–4）:** 为什么路由要薄（复用/测试/一致鉴权）；`SyncServer` 为何叫 Sync 却是 async（遗留命名）；一次请求为什么是多个事务（事务边界在 manager）；可选的服务器口令中间件（secure 模式，正交于租户）。

**自测题种子:** 全局 server 在何时创建（import 时，`app.py::server`）；薄 CRUD 端点直调什么（`server.<manager>`，非全 SyncServer 方法）；actor 在哪解析（处理函数体 `get_actor_or_default_async`）；DB session 由谁开（manager，不是路由）。

---

## Task 2: 新增第 25 课「服务层 Managers」

**Files:** `src/shell.py` · `src/part7.py`(`LESSON_25`) · `src/registry.py` · (可选)`src/quizzes.py`

**filename:** `25-service-managers.html`。

**学习目标:** 讲清 manager 这层的**统一形状**：`async with db_registry.async_session()` → actor 范围 CRUD → **session 内** `to_pydantic()` → 返回 pydantic。① `db_registry`＝自称"Dummy registry"的单例接缝，唯一开/提交/回滚事务处。② 三装饰器（`enforce_types` 同步校验类型 / `trace_method` OTel span / `raise_on_invalid_id`）给每个方法免费的 typing+tracing+id 校验。③ schema↔ORM：`to_pydantic`/`to_pydantic_async`（ORM→pydantic）、`model_dump(to_orm=True)`（pydantic→ORM）；**manager 绝不返回 ORM 行**。回扣第 24 课（server 接线 managers）、08/10/11（记忆 managers 同形）、铺垫 26/27。

**亮点（`card spark`）:** 一行 `async with db_registry.async_session()` 同时定了**两件事**——事务从哪开始/提交，以及 actor/org 范围从哪注入（`apply_access_predicate`）。路由和 agent 循环永远看不到 session、也看不到 `WHERE organization_id`，所以隔离**结构上没法被忘**：它和"唯一能开 session 的地方"焊在一起。再看 `db_registry` 自嘲的 docstring "Dummy registry to maintain the existing interface"——上百处 `db_registry.async_session()` 调用点一字未改，底下实现被收成一个模块级 asyncpg 引擎：**接口是契约、引擎可替换**。第三层妙处是**"转换在 session 内"是性能模式**：`get_agent_by_id_async` 故意"先不解密就转 pydantic、放掉 DB 连接后再跑昂贵的 PBKDF2"——schema 边界顺手成了连接池优化。

**必需卡片:** `lead`×2；`card macro`（manager 方法解剖：装饰器 → 开 session → 范围 CRUD → 转 pydantic → 返回，一张总图）；`card analogy`（**银行柜员**：你（路由）不能进金库，柜员（manager）开一笔"事务"、按你的身份只取你那一格、把原件复印成回执（pydantic）给你，绝不把原始账本递出柜台）；`card detail`（`db.py::DatabaseRegistry.async_session`、`utils.py::enforce_types`、`otel/tracing.py::trace_method`、`sqlalchemy_base.py::SqlalchemyBase.to_pydantic`）；`card spark`（一行定事务+租户 + Dummy registry 接缝 + session 内转换是性能模式）；`card key`；`card warn`（易错点：名 `*_async` 同步装饰器也存在；**别把 ORM 行漏出 session**（`expire_on_commit=False`+`expunge_all`→`DetachedInstanceError`）；一逻辑操作一 session；v0.16.8 **无同步 `session()`**；db.py 是 Postgres-only，方言透明不在这层；没有 `to_record()/to_orm()`）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **manager 方法解剖 `vflow`**：`@enforce_types`→`@raise_on_invalid_id`→`@trace_method` → `async with async_session()` BEGIN → `select`+`apply_access_predicate` → `read/create_async` → `to_pydantic()` → exit commit/expunge/close → 返回 schema。
2. **谁在调 managers `cellgroup`/`flow`**：REST 路由 / agent 循环 / 别的 manager / 序列化&批任务 → `SyncServer` 持有的单例 → `db_registry.async_session()` 单接缝。
3. **schema↔ORM 双向 `cols`**：左 `to_pydantic`/`to_pydantic_async`（`__pydantic_model__.model_validate`）；右 `model_dump(to_orm=True)`（`metadata→metadata_`）。
4. **`.cute` 萌图**：🏦 柜员开"事务"小门，📒 原始账本（ORM）留柜内，🧾 复印件（pydantic）递出去。
5. **装饰器栈 `.note info`**：typing / tracing / id 校验"免费"。

**必需代码（2–3，`codefile`）:**
- A) canonical manager 方法（源 `organization_manager.py`）：`@enforce_types @trace_method async def get..._async` → `async with db_registry.async_session()` → `Model.read_async(...)` → `to_pydantic()`；附一个 `_create_..._async`：`Model(**p.model_dump(to_orm=True))` → `create_async`。
- B) `DatabaseRegistry.async_session` 节选（源 `db.py`）：`@asynccontextmanager` yield session、clean→commit、except→rollback、finally expunge/close。
- C) 装饰器定义+用法（源 `utils.py::enforce_types` + `otel/tracing.py::trace_method` + 一个真实方法栈）。

**必需折叠（3–4）:** manager 这层为何存在（事务归属/租户/复用/横切）；`enforce_types` 怎么对 async 也成立（同步校验后返回协程）；`trace_method` 何时是 no-op（tracing 未初始化）+ span 命名；为什么必须在 session 内转 pydantic（`DetachedInstanceError`）；`db_registry` 的"Dummy registry"与 Postgres-only 现状（方言透明在 ORM 层，接第 27 课）。

**自测题种子:** 事务边界在哪开（manager 的 `db_registry.async_session()`）；manager 返回什么（pydantic，不是 ORM 行）；`enforce_types`/`trace_method` 各在哪定义（`utils.py`/`otel/tracing.py`）；pydantic→ORM 怎么走（`model_dump(to_orm=True)`，没有 `to_orm()` 方法）。

---

## Task 3: 新增第 26 课「通用 CRUD 与多租户隔离」

**Files:** `src/shell.py` · `src/part7.py`(`LESSON_26`) · `src/registry.py` · (可选)`src/quizzes.py`

**filename:** `26-crud-and-multitenancy.html`。

**学习目标:** 讲清"secure by default"。① `SqlalchemyBase` 给每个模型一套泛型 async CRUD（`read/list/size/create/update/delete/hard_delete/bulk_hard_delete`），读路径自动套 `apply_access_predicate`。② `apply_access_predicate` 把 `WHERE organization_id == actor.organization_id`（或 user 级）注进语句；跨租户=查不到（`NoResultFound`/`[]`），不是报错。③ 软删（`is_deleted=True`，**默认仍返回**，过滤 opt-in）vs 硬删；审计四件套在 CRUD 里显式盖。④ actor 从 `user_id` header 解析、串进每次 CRUD；服务器口令正交。回扣第 24（actor 入口）、25（manager 调 CRUD）、08/10/11（Block/Passage 同被隔离）。

**亮点（`card spark`）:** 多租户隔离的**反转**：它不在 handler 里"记得加 WHERE"，而是焊在**最低层的查询构造器**里——~40 个模型共用一个 `SqlalchemyBase`，"按调用者 org 限定每次读"只写一次、自动套在 `read_async`/`list_async`/`size_async`/`bulk_hard_delete_async`。新功能作者写**零**租户 SQL，只要把 actor 串下去（而"路由→manager"的路径让串 actor 成为阻力最小的写法），跨租户泄漏在结构上就很难发生——**没有一处 per-endpoint 的 WHERE 可被遗忘**。更耐人寻味的设计选择：actor 缺失时 base **不硬失败**，而是打一条 `SECURITY: ...bypasses organization filtering` 警告照跑——因为 Letta 有合法的系统内部无 user 查询，于是它选了**中央强制 + 响亮异常日志**而非**脆弱的硬失败**。再叠两层同样长在这个 base 上的可恢复性：**软删让删除可逆**（`delete_async` 只翻 `is_deleted`），**审计四件套**（`created_at`/`updated_at`/`_created_by_id`/`_last_updated_by_id`，在 CRUD 里盖）让每行天生能回答"谁、何时"。于是多租户+可恢复+可审计，全是**一个抽象类**的属性。

**必需卡片:** `lead`×2；`card macro`（secure by default：请求 → actor → 每条查询自动按 org/user 限定 → 软删感知，一张总图）；`card analogy`（**带门禁的共享档案库**：每次开柜，门禁自动只让你看你们部门（org）那一格；"删"只是贴张"作废"贴纸（软删）、原件还在；每次取放都自动盖"谁/何时"的章（审计））；`card detail`（`sqlalchemy_base.py::SqlalchemyBase`/`apply_access_predicate`/`AccessType`、`base.py::CommonSqlalchemyMetaMixins`、`user_manager.py::get_actor_or_default_async`）；`card spark`（隔离在查询构造器 + 警告而非硬失败 + 软删&审计=天生可恢复可追溯）；`card key`；`card warn`（易错点：predicate 在 base 但**gated on `if actor:`**，actor=None 只警告不拦；软删行**默认仍被返回**（`check_is_deleted` opt-in）；默认 org 级（同 org 共享），仅 jobs/runs user 级；`access`(read/write/admin) **目前 no-op**（`del access`）；缺 `user_id` 在非 `no_default_actor` 下落到共享 default 租户）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **secure by default 流 `vflow`**：（可选口令中间件）→ `get_headers`(校验 `user-<uuid4>`) → `get_actor_or_default_async`(→User 带 org，或 no_default_actor→拒) → manager 串 actor → `<crud>_async(actor=...)` → `apply_access_predicate` → `WHERE org==actor.org`(+`is_deleted==False` 仅当 `check_is_deleted`) → 只这租户、未删的行。
2. **CRUD 面 `table.t`**：方法 · 类型 · 访问控制? · 软删感知? （读+`bulk_hard_delete` 受控；`create/update/delete/hard_delete` 骑在 read 时已建立的边界上）。
3. **软删 vs 硬删 `cols`**：`delete_async`(翻 `is_deleted`、行留库、读默认仍见) vs `hard_delete_async`(物理删) vs `bulk_hard_delete_async`(SQL 层套 predicate)。
4. **`.cute` 萌图**：🔐 门禁自动盖在每次查询上，🏷️ "作废"贴纸（软删），🧾 "谁/何时"印章（审计）。
5. **审计四件套 `cellgroup`**：`created_at · updated_at · _created_by_id · _last_updated_by_id`（+ `is_deleted`）。

**必需代码（2–3，`codefile`）:**
- A) `read_async`（+`_read_multiple_preprocess` 要点，源 `sqlalchemy_base.py`）：`select(cls).where(id==...)` → `if actor: apply_access_predicate` / `elif org-scoped: warn` → `if check_is_deleted: where(is_deleted==False)` → `scalar_one_or_none()` None→`NoResultFound`。
- B) `apply_access_predicate`（源同上）：`del access` → ORGANIZATION→`where(organization_id==actor.organization_id)` / USER→`where(user_id==actor.id)`。
- C) `get_actor_or_default_async`（源 `user_manager.py`）：`no_default_actor` 守卫 → `actor_id or DEFAULT_USER_ID` → 查不到则建默认。

**必需折叠（3–4）:** `apply_access_predicate` 到底注了什么（org/user 行级 WHERE，违规=查不到非报错）；软删为什么"还在库里"+ 何时过滤（`check_is_deleted`）；审计字段怎么盖（CRUD 里显式 `_set_created_and_updated_by_fields`，非事件监听；物理列带下划线）；服务器口令 vs 租户隔离（正交两层）；`access`(read/write/admin) 为何现在是 no-op（占位将来行级权限）。

**自测题种子:** 跨租户读会怎样（被 WHERE 排除→`NoResultFound`/`[]`，不报错）；软删后默认还查得到吗（会，除非 `check_is_deleted=True`）；隔离写在哪层（`SqlalchemyBase` 查询构造器，非各 handler）；actor 缺失时 base 怎么做（警告并无范围跑，不硬失败）；哪类资源是 user 私有（jobs/runs）。

---

## Task 4: 新增第 27 课「双数据库与向量存储」

**Files:** `src/shell.py` · `src/part7.py`(`LESSON_27`) · `src/registry.py` · (可选)`src/quizzes.py`

**filename:** `27-dual-db-and-vectors.html`。

**学习目标（Part-7 收尾）:** 讲清"同一套 ORM 怎么在两套库上跑、向量怎么存与搜"。① 唯一开关 `settings.database_engine`（`@property`：配了 PG URI→Postgres，否则 SQLite）。② **没有单一 switch**：选择**分布式**地散在 `passage.py`（import 期定 `Vector(4096)` vs `CommonVector`）、向量搜索两分支、`sqlite_functions.py`（numpy UDF）、`custom_columns.py`、`alembic/env.py`。③ 向量两套：pgvector `<=>`(可索引) vs SQLite numpy UDF 暴力 `ORDER BY`；`MAX_EMBEDDING_DIM=4096` + 零填充使 cosine 不变。④ pydantic-in-DB：配置当 JSON 列、schema-on-read、免迁移。**诚实星号**：v0.16.8 `server/db.py` 只建 Postgres 引擎。回扣第 25/26（session/CRUD 骑在其上）、10/11（archival/recall=带 embedding 的 Passage）、21（LLMConfig/EmbeddingConfig 经 custom column 存）。

**亮点（`card spark`）:** "同一套代码两套库"最反直觉的一点：**根本没有一个 `db.py` 里的聪明 switch**。接缝是**分布式且大多声明式**的——一个派生 `database_engine` property、一句**类体 `if` 把 embedding 列类型在 import 期烤进模型**（所以一个进程被**特化**到一种后端、运行时不能切库）、共享查询构造器里两行 `order_by` 分支、一个全局 `@event.listens_for(Engine,"connect")` 往任何 SQLite 连接注入 numpy `cosine_distance`、外加 alembic `env.py` 选 URI。pydantic-in-DB 是另一半魔术：`EmbeddingConfig`/`LLMConfig`/多态 `ToolRule[]` 都存成单列 JSON，于是关系 schema 两库一致、靠**反序列化器 schema-on-read** 演化而非迁移——**保真胜过范式化**。而安静的拱顶石是 `MAX_EMBEDDING_DIM=4096`：把每个 embedding 零填充到定长，一个 `Vector(4096)` 列就能装任意模型的输出，且因为等量零填充不改点积与 L2 范数，**cosine 排序与未填充数学等价**——这就是填充"免费"、常量被冻结（"否则要重置库"）的原因。最后一个诚实又好教的节拍：v0.16.8 引擎层其实已悄悄收敛到 Postgres——双引擎在 ORM/alembic 完全活着，但 `server/db.py` 只建 Postgres。

**必需卡片:** `lead`×2；`card macro`（一套 ORM 两套引擎 + 向量两存两搜 + pydantic-in-DB，一张总图，并点明 db.py 现状）；`card analogy`（**一张设计图、两座工厂**：同一份蓝图（ORM 模型），按一个开关（`database_engine`）在装配线上换零件——向量列、距离算子、迁移路径都换；蓝图不变）；`card detail`（`settings.py::database_engine`/`DatabaseChoice`、`orm/passage.py::BasePassage`、`orm/custom_columns.py`、`orm/sqlite_functions.py::register_functions`、`constants.py::MAX_EMBEDDING_DIM`、`alembic/env.py`）；`card spark`（没有单一 switch/import 期特化 + pydantic-in-DB 保真 + 4096 零填充不变 + db.py 收敛 Postgres 的诚实星号）；`card key`；`card warn`（易错点：`db.py` **不**分 SQLite/Postgres（Postgres-only）；`database_engine` 是 `@property` 由"有没有 PG URI"决定、**无 `LETTA_DATABASE_ENGINE`**；SQLite 是 **numpy UDF 不是 sqlite-vec 原生**（`sqlite_vec.load()` 注释掉）；**无 `AgentPassage`**（只 `SourcePassage`/`ArchivalPassage`）；列类型 import 期定死、运行时不能切库；填充让向量**可存**不等于跨模型**可比**）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **一套 ORM 两套引擎 `cols`/`flow`**：顶＝`orm/*` 一份模型；判定＝`settings.database_engine`；左 SQLite-dev（aiosqlite · `CommonVector` BINARY · `func.cosine_distance` numpy UDF · baseline `2c059cad97cc`）/右 Postgres-prod（asyncpg · `Vector(4096)` · `<=>` 可 ivfflat/hnsw · 增量链）；底栏列"什么被换"（驱动/列类型/距离算子/序列化/迁移/要填充?）；callout：v0.16.8 `server/db.py` 只建 Postgres。
2. **pydantic-in-DB 往返 `vflow`**：`EmbeddingConfig`(pydantic) →`process_bind_param`(`model_dump(json)`)→ JSON 列 → `process_result_value`(`Model(**data)`)→ pydantic；旁注 `deserialize_llm_config` 兜底默认＝schema-on-read 免迁移。
3. **向量两套搜 `table.t`**：Postgres `cls.embedding.cosine_distance()`→`<=>`、可 ANN 索引；SQLite `func.cosine_distance` numpy、全表暴力。
4. **`.cute` 萌图**：📐 4096 维定长格子，1024/1536 维向量后面补 0 进格，气泡"补 0 不改 cosine"。
5. **`MAX_EMBEDDING_DIM` 零填充不变 `cellgroup`/`.note info`**：点积 +0、L2 +0 → cosine 不变。

**必需代码（2–3，`codefile`）:**
- A) 引擎 + SQLite UDF 注册（源 `db.py` + `sqlite_functions.py::register_functions`）：`engine=create_async_engine(async_pg_uri,...)`（Postgres-only）+ `@event.listens_for(Engine,"connect")` 给 SQLite 连接注册 numpy `cosine_distance`（注明 `sqlite_vec.load()` 注释掉）。
- B) pydantic-in-DB `TypeDecorator`（源 `custom_columns.py`）：`EmbeddingConfigColumn`(impl=JSON, bind/result) + `CommonVector`(impl=BINARY, `serialize_float32`/`frombuffer`)。
- C) `BasePassage` embedding 列 + 两路搜索（源 `passage.py` + `sqlalchemy_base.py`）：import 期 `if POSTGRES: Vector(4096) else: CommonVector`；查询 `if POSTGRES: order_by(cosine_distance().asc())` else numpy UDF。

**必需折叠（3–4）:** `database_engine` 到底怎么定（property，看有没有 PG URI；无 `LETTA_DATABASE_ENGINE`）；向量在两库怎么存/搜（pgvector `<=>`+索引 vs numpy UDF 暴力）+ 为什么零填充"免费"；pydantic-in-DB 的取舍（免迁移/保真 vs 不可索引子字段+序列化开销）；alembic 两后端（Postgres 增量链 + SQLite 单 baseline + 内联方言差）；**诚实星号**：为何 v0.16.8 `server/db.py` 只建 Postgres（引擎层收敛、双库故事在 ORM/alembic）。

**Capstone 收尾:** 第七部分终章，用 `cellgroup` 回扣全 Part：**24 三层架构 · 25 服务层 Managers · 26 CRUD/隔离 · 27 双库/向量**，一句话串成"**分层立骨架 → manager 管事务与转换 → 一个 base 默认安全 → 一套 ORM 两套库装下记忆的向量**"。回指第 03（消息生命周期的持久化一端）、10/11（archival/recall 的向量就存在这）。最后过渡到第八部分（进阶专题 + 术语表）。

**自测题种子:** `database_engine` 由什么决定（有没有配 PG URI 的 `@property`，非 `LETTA_DATABASE_ENGINE`）；`server/db.py` 在 v0.16.8 建哪种引擎（Postgres-only）；SQLite 的相似度靠什么（注册的 numpy `cosine_distance` UDF，非 sqlite-vec 原生）；`MAX_EMBEDDING_DIM` + 零填充为什么不改排序（点积/范数 +0，cosine 不变）；配置为什么能存一列还免迁移（pydantic-in-DB + schema-on-read 反序列化）。

---

## Task 5: 集成与合并（M7 收尾）

**Files:** `docs/superpowers/plans/2026-06-15-letta-visual-guide-roadmap.md` · （验证）全站

- [ ] 全量构建：`cd src && python build.py && python check_links.py && python check_html.py`，期望 `0 error / 0 warning`、链接全解析、index pill「共 27 课 · 7 个部分」。
- [ ] 导航链抽查：`23→24→25→26→27`，每课 `prev/next` 各 1，27 课 `next=../index.html`。
- [ ] roadmap 把 **M7** 标 `✅ 已完成并合并`（计划文档名填入）。
- [ ] 合并：`git checkout master && git merge --no-ff feat/m7-server`；合并后再跑三件套确认绿。
- [ ] `git branch -d feat/m7-server`；`git push origin master`。
- [ ] 报告 M7 完成，**自动继续 M8**（进阶专题 + 术语表，28–31）——用户已要求一路做完全部 M。

---

## Self-Review（写完即查）
## Self-Review（写完即查）
1. **Spec coverage**：spec 第七部分 24–27 ↔ Task 1–4 一一对应（三层架构 ✓、服务层 Managers ✓、CRUD/多租户 ✓、双库/向量 ✓）。✅
2. **Placeholder scan**：无 TBD/TODO；每个 task 给 filename/学习目标/亮点/卡片/图/代码/折叠/自测题。✅
3. **Type/name consistency**：全程用 `SyncServer`/`get_letta_server`/`get_headers`/`get_actor_or_default_async`/`db_registry.async_session`/`DatabaseRegistry`/`enforce_types`/`trace_method`/`SqlalchemyBase`/`apply_access_predicate`/`AccessType`/`CommonSqlalchemyMetaMixins`/`to_pydantic`/`model_dump(to_orm=True)`/`database_engine`/`DatabaseChoice`/`BasePassage`/`CommonVector`/`EmbeddingConfigColumn`/`MAX_EMBEDDING_DIM`/`sqlite_functions`，与"已核实锚点"一致。✅
4. **outline 纠正已固化**：路由直调 manager（非全经 SyncServer）；`SyncServer` 无消息队列、import 期创建、async 实质；db.py **Postgres-only**（方言透明在 ORM 层 + alembic）；无 `to_record()/to_orm()` 方法；软删默认仍返回（`check_is_deleted` opt-in）；`access` 现为 no-op；`database_engine` 是 `@property`；无 `AgentPassage`；SQLite 用 numpy UDF 非 sqlite-vec 原生。✅
5. **跨课一致**：24 立三层骨架 → 25 manager 兑现事务/转换 → 26 一个 base 默认安全 → 27 一套 ORM 两套库装向量；27 的 Passage 向量回扣 10/11，custom column 回扣 21；整 Part 收口"分层→事务→默认安全→双库向量"，过渡到第八部分。✅
