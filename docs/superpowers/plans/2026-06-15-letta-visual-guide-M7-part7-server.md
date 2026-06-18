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

<!--TASKS-->

---

## Self-Review（写完即查）
<!--SELFREVIEW-->
