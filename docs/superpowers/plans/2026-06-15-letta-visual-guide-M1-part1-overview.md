# Letta 图解教程 · M1 第一部分（宏观全景，3 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第一部分「宏观全景」的 3 课（01 Letta/MemGPT 是什么 · 02 项目全景地图 · 03 一条消息的生命周期），确立"多图 + 伪代码/简化源码 + 详尽 + 有亮点"的内容基线，并把 01 从 M0 基线扩写到完整深度。

**Architecture:** 沿用 M0 生成器。每课是 `src/part1.py` 里的 `LESSON_xx = {"zh": html, "en": html}`，经 `build.py` 套进 `shell.py` 外壳。新增一课 = 改 4 处（`shell.PAGES`、`shell.SUBTITLES`、`registry.CONTENT`、`part1.py` 内容）+（可选）`quizzes.QUIZZES`。验证 = `build.py + check_links.py + check_html.py` 全过，且**目标课不再出现 WARN**（即满足 `MIN_DIAGRAMS=6`、`MIN_CJK=3000`）。

**Tech Stack:** Python 3.11+ 标准库；自包含 HTML/CSS（设计系统类：`card macro/detail/analogy/key/warn/spark`、`flow/vflow/layers/cols/timeline/cellgroup`、`table.t`、`accordion`）。

> 讲解对象：`/home/verden/course/letta`（`v0.16.8`）。所有源码引用以"**文件 + 符号名**"为准，**不写行号**，并在写作时对照真实代码核实。

---

## 共享约定（每课都遵守）

### A. 如何"扩写"已存在的第 01 课
只改 `src/part1.py` 的 `LESSON_01`（`PAGES`/`SUBTITLES`/`CONTENT` 已含 01）。

### B. 如何"新增"一课（02、03）
按顺序改 4 处，保持一一对应：
1. `src/shell.py` 的 `PAGES`：在 01 之后追加元组 `(filename, title_zh, title_en, part_zh, part_en)`，`part_*` 同为 `"第一部分 · 宏观全景"` / `"Part 1 · The Big Picture"`。
2. `src/shell.py` 的 `SUBTITLES`：追加 `filename: (subtitle_zh, subtitle_en)`。
3. `src/part1.py`：新增 `LESSON_02` / `LESSON_03 = {"zh": ..., "en": ...}`。
4. `src/registry.py`：在 `CONTENT` 追加 `filename: part1.LESSON_0X`。
5.（可选，本里程碑鼓励）`src/quizzes.py` 的 `QUIZZES`：追加该课 2-3 题（双语）。

### C. 每课页面结构（硬性，缺一即不达标）
正文**不要**再写 `<h1>`（外壳的 hero 已有）；用 `<h2>/<h3>/<h4>`。每课至少包含：
- **导语** `<p class="lead" ...>` 一段点题。
- **教学卡片** 至少 4 种：`card macro`（🌍 宏观）、`card analogy`（🔌 类比）、`card key`（✅ 本课要点，含"本课要点"/"Key points" 字样）、`card spark`（💡 设计亮点）；按需加 `card detail`（🔬 源码对应）、`card warn`（⚠️）。
- **图（硬性 ≥ 3 张/语言，合计 ≥ 6）**：从 `layers/vflow/flow/cols/timeline/cellgroup` 选，类型要多样（不要 3 张都是 cols）。宏观/结构课必须有一张"**整体结构图**"。
- **代码 2-3 段**：`<pre><code>`，先**伪代码**讲思路，再给**从源码简化的真实片段**（标注来源"文件 + 符号"）。代码内部用 ASCII（`->`、`...`，不用 `→`/`—`）。`<` 写成 `&lt;`，`&` 写成 `&amp;`。
- **折叠深挖 2-3 个**：`<details class="accordion"><summary>…</summary><div class="acc-body">…</div></details>`，结构「示例 → 为什么这样设计 → 源码在哪（文件+符号）→ 还有什么替代」。
- **末尾自测**（推荐）：在 `quizzes.QUIZZES` 加 2-3 题，build 会自动渲染到课末。
- **底部导航**：由外壳自动生成（无需手写）。

### D. 内容准则（硬性）
- **CJK ≥ 3000，目标 4000+**（`check_html` 统计 zh 正文中 `[\u4e00-\u9fff]`；不含英文/代码/路径）。宁多勿少，但**不灌水**：每段要有信息增量。
- **有亮点**：每课必须有一个 `card spark` 讲该课最精妙、最反直觉的设计思想（"aha"），并落到"为什么这么写"。**禁止泛泛而谈**。
- **关注整体项目**：每课结尾把本课放回 Letta 整体（这块在大图的哪里、下一课接什么）。
- **双语信息等价**：zh/en 要点不缺；不要求逐字对译。
- **源码准确**：引用的文件/符号在 `letta` 仓库真实存在；写作时用 grep/view 核实；优先引用本计划"源码锚点"里已核实的符号。

### E. 每课验收（DoD）
1. `cd src && python build.py && python check_links.py && python check_html.py` → `0 error(s)`，且输出里**没有**针对该课文件名的 `[WARN]`（特别是 "only N visual blocks"、"only N CJK chars"）。
2. 该课 zh、en 两块都存在且非空；HTML 标签平衡（`check_html` 会校验）。
3. 提交（每课一提交），消息含 `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`。

### F. 全局源码锚点（已对照 v0.16.8 核实，可直接引用）
- 入口/路由：`letta/main.py`（`app`，`letta` 命令）、`letta/server/rest_api/app.py`（`create_application`、全局 `server`）、`letta/server/rest_api/routers/v1/agents.py` 的 `send_message`、`create_agent`。
- 服务/编排：`letta/server/server.py::SyncServer`（持有各 `*Manager`）、`letta/services/agent_manager.py::AgentManager`、`message_manager.py::MessageManager`、`block_manager.py::BlockManager`、`passage_manager.py::PassageManager`、`letta/services/user_manager.py::get_actor_or_default_async`。
- Agent 运行：`letta/agents/agent_loop.py::AgentLoop.load`、`letta/agents/letta_agent_v3.py::LettaAgentV3`（`.step`、内部 `_step`、`_decide_continuation`）。
- 记忆与提示：`letta/schemas/agent.py::AgentState`、`letta/schemas/memory.py::Memory`（`.compile`）、`letta/schemas/block.py::Block`、`letta/prompts/prompt_generator.py::PromptGenerator`、`letta/services/agent_manager.py::rebuild_system_prompt_async`。
- 持久化：`letta/orm/sqlalchemy_base.py::SqlalchemyBase`（`apply_access_predicate`）、`letta/server/db.py`（`db_registry.async_session`）、`letta/settings.py::database_engine`。

---

## Task 1: 扩写第 01 课「Letta / MemGPT 是什么」到完整深度

**Files:**
- Modify: `src/part1.py`（替换 `LESSON_01` 的 `zh`/`en` 全文）
- (可选) Modify: `src/quizzes.py`（为 `01-what-is-letta.html` 增 2-3 题）

**学习目标：** 一个完全的新手读完能讲清：Letta 是什么、解决什么根本问题（LLM 无状态 + 上下文有限）、MemGPT 的核心思想（把 agent 做成有状态、能自我管理记忆）、与"裸 LLM 调用 / LangChain / OpenAI Assistants"的区别、三层记忆是什么、"agent 就是数据库里的一条 AgentState"。

**本课最大亮点（必须落到 `card spark`）：** MemGPT 的"**操作系统**"类比——把上下文窗口当 **RAM**、外部记忆当**磁盘**，agent 自己发起"**换页**"（调用记忆工具）；并由此点出"**自我编辑记忆 = 改写自己的系统提示**"（`Memory.compile()` 的产物被拼进持久化的 system message，`rebuild_system_prompt_async` 在记忆变化时重写第 0 条消息）。

**必需卡片：** `lead` 导语；`card macro`（有状态 agent / AgentState 是存档）；`card analogy`（健忘天才 + 随身笔记本 + 档案室，扩写 M0 版）；`card detail`（🔬 落到 `schemas/agent.py::AgentState`、`schemas/memory.py::Memory`、自我编辑工具 `core_memory_append/replace`）；`card spark`（上面的 OS 类比 + 自编辑系统提示）；`card key`（本课要点）；可选 `card warn`（"有状态"不是说模型有记忆——模型每次调用仍无状态，记忆是框架在模型外补的）。

**必需图（≥ 3/语言，建议 4-5，类型要多样）：**
1. **生态定位图**（`cols` 或 `flow`）：训练框架(PyTorch) · 推理 API(OpenAI) · 编排(LangChain) · **Letta=有状态记忆 agent**，标出 Letta 站位。
2. **无状态 vs 有状态 时间线**（`timeline` 或 `cols`）：裸 LLM 调用 = 上下文满即遗忘；Letta = 跨调用持久化 `AgentState`。
3. **三层记忆总览**（`vflow` 或 `layers`）：core / recall / archival 各一行（为第三部分埋钩子）。
4. **"agent = AgentState 存档"概念图**（`layers` 或 `cellgroup`）：把 `AgentState` 的字段（memory blocks、message_ids、system、tools、llm_config）画成一张"存档卡"。
5.（可选）**自我编辑记忆闭环**（`vflow`）：用户消息 -> agent 调 `core_memory_replace` -> 块更新 -> 系统提示重编译 -> 下一轮即生效。

**必需代码（2-3 段，标注来源文件+符号）：**
- A) **用户视角 hello-world**（真实，来自 `README.md` 的 Python SDK）：`client.agents.create(model=..., memory_blocks=[{label:"human"...},{label:"persona"...}], tools=["web_search",...])` 然后 `client.agents.messages.create(agent_id, input=...)`。点出"创建 agent 时就给了 persona/human 记忆块"。
- B) **`AgentState` 简化结构**（伪代码，源自 `letta/schemas/agent.py::AgentState`）：列出 `id / name / memory(Memory) / message_ids / system / tools / llm_config / embedding_config` 等关键字段，说明"这一条就是 agent 的全部存档"。
- C)（可选）**自我编辑思路**（伪代码，源自 `services/tool_executor/core_tool_executor.py` + `agent_manager.rebuild_system_prompt_async`）：`core_memory_replace(label, old, new)` 改 block.value -> 持久化 -> 重建 system prompt。

**必需折叠（2-3）：**
- 「为什么不把所有历史都塞进上下文？」：上下文经济学（token 成本、延迟、prefix cache、长上下文≠免费），为第 5 课埋钩子。
- 「Letta vs OpenAI Assistants / LangChain memory」：都"加了记忆"，差别在 Letta 让 **agent 自己编辑**分层记忆、状态完全在库、模型无关。
- 「MemGPT 一句话」：LLM≈CPU、上下文≈RAM、外部存储≈磁盘；记忆工具≈系统调用/换页。

**自测题种子（写入 `quizzes.QUIZZES["01-what-is-letta.html"]`，2-3 题双语）：**
- Letta 存在的根本理由？→ LLM 无状态 + 上下文窗口有限。
- Letta 里"agent 的状态"具体是什么？→ 数据库里的一条 `AgentState`。
- "自我编辑记忆"在机制上意味着什么？→ agent 通过记忆工具**改写自己的系统提示**（`Memory.compile` 重新拼进 system message）。

**草图（已用真实 CSS 类，可直接用 / 微调；en 版镜像同结构）：**

生态定位图（`table.t`）：
```html
<table class="t">
  <tr><th>工具</th><th>定位</th><th>状态</th><th>记忆</th></tr>
  <tr><td class="mono">PyTorch</td><td>训练 + 推理框架</td><td>—</td><td>—</td></tr>
  <tr><td class="mono">OpenAI API</td><td>托管推理</td><td>无状态（每次调用独立）</td><td>无：要自己把历史拼进 prompt</td></tr>
  <tr><td class="mono">LangChain</td><td>编排 / 胶水</td><td>多为无状态</td><td>可加，但要你自己管</td></tr>
  <tr><td><strong>Letta</strong></td><td><strong>有状态 agent 框架</strong></td><td><strong>有状态：AgentState 存库</strong></td><td><strong>内建三层 + agent 自己编辑</strong></td></tr>
</table>
```

"agent = AgentState 存档"概念图（`layers`）：
```html
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">核心记忆</span><span class="name">memory: Memory</span></div>
    <div class="ld">persona / human 等记忆块，始终在上下文里，agent 可自改</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">在窗消息</span><span class="name">message_ids: list[str]</span></div>
    <div class="ld">当前留在上下文窗口里的消息 id（第 0 条是 system 消息）</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">能力</span><span class="name">tools · tool_rules</span></div>
    <div class="ld">这个 agent 能调用哪些工具、调用顺序约束</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">模型</span><span class="name">llm_config · embedding_config</span></div>
    <div class="ld">用哪个模型、上下文多大、用什么嵌入模型</div></div>
</div>
```

代码 A — 用户视角 hello-world（`pre.code`，真实，源自 `README.md`）：
```html
<pre class="code"><span class="cm"># 创建一个自带记忆的 agent（Python SDK）</span>
agent = client.agents.<span class="fn">create</span>(
    model=<span class="st">"openai/gpt-5"</span>,
    memory_blocks=[
        {<span class="st">"label"</span>: <span class="st">"human"</span>,   <span class="st">"value"</span>: <span class="st">"叫 Timber，在做 Letta"</span>},
        {<span class="st">"label"</span>: <span class="st">"persona"</span>, <span class="st">"value"</span>: <span class="st">"我是会自我改进的助手"</span>},
    ],
    tools=[<span class="st">"web_search"</span>],
)
<span class="cm"># 发消息；agent 带着记忆回应</span>
resp = client.agents.messages.<span class="fn">create</span>(agent.id, input=<span class="st">"你知道我什么？"</span>)
</pre>
```

代码 B — `AgentState` 简化结构（`codefile`，标注来源；伪代码，源自 `letta/schemas/agent.py::AgentState`）：
```html
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/agent.py</span><span class="ln">class AgentState（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentState</span>:
    id: str                  <span class="cm"># "agent-..." 前缀 id</span>
    memory: Memory           <span class="cm"># 核心记忆：persona / human 块</span>
    message_ids: list        <span class="cm"># 当前在上下文窗口里的消息</span>
    system: str              <span class="cm"># 系统提示（核心记忆会被编译进来）</span>
    tools: list              <span class="cm"># 可用工具</span>
    llm_config: LLMConfig    <span class="cm"># 模型 / 上下文窗口大小</span>
</pre></div>
```

> 提示：这 4 张草图给了"整体结构图 + 代码"的骨架；实现者需另补 ≥1 张图（如"无状态 vs 有状态时间线"用 `timeline`，或"三层记忆总览"用 `vflow`），把 zh 正文充实到 CJK ≥ 3000（目标 4000+），并写英文镜像版。

**Steps:**

- [ ] **Step 1: 重写 `LESSON_01`（zh + en）到上述结构与深度**
  - 在 `src/part1.py` 用满足 C/D 准则的完整双语 HTML 替换现有 `LESSON_01`。CJK ≥ 3000（目标 4000+），≥ 4 图、3 卡（含 spark/key/analogy）、2-3 代码段、2-3 折叠。
  - 保持 M0 已验证的设计系统类名（`card analogy/macro/key/spark`、`cols/col`、`vflow/step/num/sc`、`layers`、`timeline`、`cellgroup`、`inline`、`mono`）。

- [ ] **Step 2:（可选）加自测题**
  - 在 `src/quizzes.py` 的 `QUIZZES` 加 `"01-what-is-letta.html": {"mcq":[...2-3...], "open":[...1...]}`，双语，`answer` 为 0 基下标。

- [ ] **Step 3: 构建并验证该课 WARN-free**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python build.py && python check_links.py && python check_html.py
```
Expected: `0 error(s)`；输出中**没有**任何 `01-what-is-letta.html` 的 `[WARN]`（既不报 "only N visual blocks" 也不报 "only N CJK chars"）。若仍报 CJK 不足或图不足，继续补内容/补图，不要降低标准。

- [ ] **Step 4: 核对源码准确性（自检）**

Run（抽查引用到的符号确实存在）：
```bash
cd /home/verden/course/letta
grep -rn "class AgentState" letta/schemas/agent.py
grep -rn "def compile" letta/schemas/memory.py
grep -rn "def rebuild_system_prompt_async" letta/services/agent_manager.py
```
Expected: 三个符号都能命中（说明 `card detail`/代码段里引用的"文件+符号"真实存在）。

- [ ] **Step 5: 提交**

```bash
cd /home/verden/course/letta-visual-guide
git add src/part1.py src/quizzes.py
git commit -m "feat(m1): expand lesson 01 (what is Letta/MemGPT) to full depth

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

---

## Task 2: 新增第 02 课「项目全景地图」

**Files:**
- Modify: `src/shell.py`（`PAGES` 追加 02；`SUBTITLES` 追加 02）
- Modify: `src/part1.py`（新增 `LESSON_02`）
- Modify: `src/registry.py`（`CONTENT` 追加 02）
- (可选) Modify: `src/quizzes.py`

**filename:** `02-project-map.html`；标题 zh「项目全景地图」/ en「The project map」；副标题 zh「目录导览 · 三层架构（REST -> services -> ORM/DB）」/ en「Directory tour; the 3-layer architecture」。

**学习目标：** 在脑子里建立 `letta/` 代码地图与**三层架构**（REST 路由 -> services/managers -> ORM/DB），知道"记忆 / agent 循环 / 工具 / provider / 存储"各落在哪个目录，并理解 `AgentState` 是穿过三层的核心对象。**这是全书的"整体结构图"课。**

**本课最大亮点（`card spark`）：** "**薄路由、厚服务、通用 ORM**"——`SqlalchemyBase` 一处实现泛型 CRUD + `apply_access_predicate`，让每张表**自动**获得分页 / 软删除 / 多租户行级隔离（secure by default）；整个服务端是**一个** `SyncServer` 持有全部 `*Manager`；agent 是"无状态运行时 + 序列化 `AgentState`"，因此能水平扩展。

**必需卡片：** `lead`；`card macro`（三层架构 + SyncServer 中枢）；`card analogy`（餐厅：前台=路由、后厨=managers、仓库=ORM/DB）；`card detail`（落到真实目录与 `SyncServer` / `*Manager` / `SqlalchemyBase`）；`card spark`（上面的亮点）；`card key`。

**必需图（≥3/语言，建议 4-5；本课必须含"整体结构图"）：**
1. **目录全景 `table.t`**（见草图）。
2. **三层架构 `layers`**（见草图）。
3. **一次请求穿过三层 `flow`**（见草图）。
4. **按学习路线读代码 `layers`**（仿参考 lesson 02 的"想会用/懂…"路线图：想跑起来 -> server/cli；懂记忆 -> schemas/memory + services；懂循环 -> agents/letta_agent_v3；懂存储 -> orm）。

**必需代码（2-3，`codefile` 优先，标注 文件+符号）：**
- A) 薄路由：`send_message` 简化（解析 actor -> 载入 agent -> `AgentLoop.load` -> `.step`）。来源 `letta/server/rest_api/routers/v1/agents.py::send_message`。
- B) 厚服务：一个 manager 方法骨架（`async with db_registry.async_session()` -> ORM 调用 -> 返回 pydantic）。来源 `letta/services/agent_manager.py`。
- C)（可选）通用 CRUD：`apply_access_predicate` 一行点出多租户隔离。来源 `letta/orm/sqlalchemy_base.py`。

**必需折叠（2-3）：** 「为什么路由这么薄」（业务在 managers，CLI 与 REST 复用、可测）；「schema vs orm 两套模型」（pydantic API 模型 vs SQLAlchemy DB 模型，create/update/read 三件套）；「SyncServer 是什么」（一个中枢持有所有 manager，`app.py` 里一个全局实例）。

**自测题种子：** 三层顺序？业务逻辑落在哪层（managers/services）？`apply_access_predicate` 干什么（org/user 行级隔离）。

**草图（已用真实类；en 镜像）：**

目录全景（`table.t`）：
```html
<table class="t">
  <tr><th>目录</th><th>作用</th></tr>
  <tr><td class="mono">agents/</td><td>agent 运行时与执行循环（<span class="mono">letta_agent_v3.py</span>、<span class="mono">agent_loop.py</span>）</td></tr>
  <tr><td class="mono">schemas/</td><td>Pydantic 数据契约：<span class="mono">AgentState</span> · <span class="mono">Memory</span> · <span class="mono">Block</span> · <span class="mono">Message</span> · <span class="mono">LLMConfig</span></td></tr>
  <tr><td class="mono">services/</td><td>业务逻辑层：各 <span class="mono">*Manager</span>（agent / message / block / passage …）</td></tr>
  <tr><td class="mono">orm/</td><td>SQLAlchemy 持久化模型 + <span class="mono">SqlalchemyBase</span> 通用 CRUD</td></tr>
  <tr><td class="mono">server/</td><td>FastAPI REST 服务、<span class="mono">SyncServer</span>、路由 <span class="mono">rest_api/routers/v1/*</span></td></tr>
  <tr><td class="mono">functions/</td><td>工具：从函数 + docstring 生成 schema、内置工具集</td></tr>
  <tr><td class="mono">llm_api/</td><td>多家 LLM provider 的统一客户端抽象</td></tr>
  <tr><td class="mono">prompts/</td><td>系统提示文本 + <span class="mono">PromptGenerator</span>（把记忆编译进 system message）</td></tr>
</table>
```

三层架构（`layers`）：
```html
<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">REST 路由</span><span class="name">server/rest_api/routers/v1/*</span></div>
    <div class="ld">很薄：解析 actor、收发 HTTP，把活交给 services</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">服务层</span><span class="name">services/*Manager</span></div>
    <div class="ld">业务逻辑都在这里：开 DB 会话、调 ORM、schema&lt;-&gt;orm 转换</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">ORM 模型</span><span class="name">orm/* · SqlalchemyBase</span></div>
    <div class="ld">通用 CRUD + <span class="mono">apply_access_predicate</span> 多租户隔离</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">数据库</span><span class="name">SQLite（开发）/ Postgres+pgvector（生产）</span></div>
    <div class="ld"><span class="mono">settings.database_engine</span> 选型；同一套代码两种库</div></div>
</div>
```

一次请求穿三层（`flow`）：
```html
<div class="flow">
  <div class="node hl"><div class="nt">REST 路由</div><div class="nd">send_message</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">SyncServer / Manager</div><div class="nd">业务 + DB 会话</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">ORM CRUD</div><div class="nd">apply_access_predicate</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">数据库</div><div class="nd">SQLite / Postgres</div></div>
</div>
```

薄路由代码（`codefile`）：
```html
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/routers/v1/agents.py</span><span class="ln">send_message（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">send_message</span>(agent_id, request, server, headers):
    actor = <span class="kw">await</span> server.user_manager.<span class="fn">get_actor_or_default_async</span>(headers.actor_id)
    agent = <span class="kw">await</span> server.agent_manager.<span class="fn">get_agent_by_id_async</span>(agent_id, actor)
    loop  = AgentLoop.<span class="fn">load</span>(agent_state=agent, actor=actor)
    <span class="kw">return await</span> loop.<span class="fn">step</span>(request.messages)   <span class="cm"># 路由只做这些；业务在下层</span>
</pre></div>
```

**Steps:**

- [ ] **Step 1: 接线**：在 `src/shell.py` 的 `PAGES` 追加
  ```python
      ("02-project-map.html", "项目全景地图", "The project map",
       "第一部分 · 宏观全景", "Part 1 · The Big Picture"),
  ```
  在 `SUBTITLES` 追加
  ```python
      "02-project-map.html": ("目录导览 · 三层架构（REST -> services -> ORM/DB）",
                              "Directory tour; 3-layer architecture (REST -> services -> ORM/DB)"),
  ```
  在 `src/registry.py` 的 `CONTENT` 追加 `"02-project-map.html": part1.LESSON_02,`。
- [ ] **Step 2: 写 `LESSON_02`（zh+en）** 到上述结构与深度（CJK ≥ 3000 目标 4000+，≥4 图含整体结构图，3+ 卡含 spark/key/analogy，2-3 代码段，2-3 折叠）。
- [ ] **Step 3:（可选）加自测题**。
- [ ] **Step 4: 构建并验证 02 课 WARN-free**
  ```bash
  cd /home/verden/course/letta-visual-guide/src && python build.py && python check_links.py && python check_html.py
  ```
  Expected: `0 error(s)`，且无 `02-project-map.html` 的 `[WARN]`。
- [ ] **Step 5: 核对源码锚点**
  ```bash
  cd /home/verden/course/letta
  grep -rn "class SyncServer" letta/server/server.py
  grep -rn "def apply_access_predicate" letta/orm/sqlalchemy_base.py
  grep -rn "async def send_message" letta/server/rest_api/routers/v1/agents.py
  ```
  Expected: 三者都命中。
- [ ] **Step 6: 提交**
  ```bash
  cd /home/verden/course/letta-visual-guide && git add src/ && git commit -m "feat(m1): add lesson 02 (project map / 3-layer architecture)

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 3: 新增第 03 课「一条消息的生命周期」

**Files:**
- Modify: `src/shell.py`（`PAGES` 追加 03；`SUBTITLES` 追加 03）
- Modify: `src/part1.py`（新增 `LESSON_03`）
- Modify: `src/registry.py`（`CONTENT` 追加 03）
- (可选) Modify: `src/quizzes.py`

**filename:** `03-message-lifecycle.html`；标题 zh「一条消息的生命周期」/ en「Lifecycle of one message」；副标题 zh「POST -> actor -> AgentState -> step 循环 -> 工具/记忆 -> 持久化 -> 响应」/ en「POST -> actor -> AgentState -> step loop -> tools/memory -> persist -> response」。

**学习目标：** 把一条用户消息**端到端**走一遍，串起后面第三~七部分：`POST /v1/agents/{id}/messages` -> `send_message` -> 解析 actor -> 载入 `AgentState` -> `AgentLoop.load` -> `LettaAgentV3.step` -> （循环）`_step`：组装上下文（把核心记忆编译进 system）-> LLM 调用 -> 解析并执行工具（可能改记忆）-> 持久化消息 -> `_decide_continuation` 判断继续/结束 -> 必要时压缩 -> 返回 `LettaResponse`。**这是全书的"全景数据流"课。**

**本课最大亮点（`card spark`）：** 循环的继续规则简单到反直觉——"**调了工具就继续，产出普通消息且没调工具就停**"（`_decide_continuation`），相比原始 MemGPT 的 heartbeat 是一次大幅简化；且 agent **每次请求都从 `AgentState` 重建**（无状态运行时），所以一条"消息"可能触发**多次** LLM 步（受 `max_steps` 上限约束）。

**必需卡片：** `lead`；`card macro`（端到端数据流）；`card analogy`（客服工单：收单 -> 查档 -> 处理（可能去仓库取资料）-> 回信 -> 归档）；`card detail`（每个阶段对应的真实符号）；`card spark`（继续规则 + 无状态运行时）；`card key`；`card warn`（一条消息≠一次模型调用：多步工具循环）。

**必需图（≥3/语言，建议 5）：**
1. **端到端 `vflow`**（主轴 ~7 步，见草图）。
2. **请求穿层 `flow`**（route -> AgentLoop.load -> step -> _step -> 持久化）。
3. **step 循环示意 `flow`**：一次 `_step` = 一次 LLM 调用 + 工具执行 + 持久化；`step()` 在 `max_steps` 内循环；`_decide_continuation` 决定继不继续。
4. **上下文怎么拼出来 `layers`/`cellgroup`**：system（编译进来的核心记忆 + memory_metadata）+ 在窗消息（recall 最近）+ 工具 schema -> 一次 LLM 请求。
5.（可选）**压缩触发 `timeline`**：tokens 逼近阈值 -> compact -> summary 消息（为第 12 课埋钩子）。

**必需代码（2-3，`codefile` 优先）：**
- A) 入口：`send_message` 简化（同 Task 2 草图，可复用并强调"路由把活交给 step"）。来源 `routers/v1/agents.py::send_message` + `agents/agent_loop.py::AgentLoop.load`。
- B) 循环：`LettaAgentV3.step` 伪代码（`for i in range(max_steps): _step(); 若不再调工具则 break`）。来源 `letta/agents/letta_agent_v3.py::step / _step / _decide_continuation`。
- C)（可选）上下文组装：`Memory.compile()` 经 `PromptGenerator` 拼进 system。来源 `letta/prompts/prompt_generator.py` + `letta/schemas/memory.py::compile`。

**必需折叠（2-3）：** 「一条消息为什么会触发好几次模型调用」（多步工具循环；heartbeat 历史 -> v3 规则）；「上下文满了怎么办」（compaction 预告 -> 第 12 课）；「流式 vs 阻塞」（`step` vs `stream` / SSE）。

**自测题种子：** `send_message` 第一步做什么（解析 actor）；循环靠什么决定继续（是否调用了工具）；两步之间 agent 的状态存在哪（库里的 `AgentState`）。

**草图（已用真实类；en 镜像）：**

端到端主轴（`vflow`）：
```html
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>收到请求</h4><p><span class="mono">POST /v1/agents/{id}/messages</span> -&gt; <span class="mono">send_message</span></p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>解析 actor</h4><p><span class="mono">get_actor_or_default_async</span>：从 user_id 头定位租户</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>载入存档</h4><p><span class="mono">get_agent_by_id_async</span> 取出 <span class="mono">AgentState</span></p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>进入循环</h4><p><span class="mono">AgentLoop.load(agent).step(messages)</span></p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>组装 + 调模型</h4><p>把核心记忆编译进 system，连同在窗消息 + 工具 schema 发给 LLM</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>执行工具 / 改记忆</h4><p>解析 tool_call 并执行；可能改写记忆块</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>持久化 + 判定</h4><p>写消息、更 <span class="mono">message_ids</span>；<span class="mono">_decide_continuation</span> 决定再来一轮还是返回 <span class="mono">LettaResponse</span></p></div></div>
</div>
```

step 循环伪代码（`codefile`）：
```html
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">step / _step（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">step</span>(self, input_messages):
    msgs = self.<span class="fn">load_in_context_messages</span>() + input_messages
    <span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span>(self.max_steps):       <span class="cm"># 一条消息可能要走好几轮</span>
        ai = <span class="kw">await</span> self.<span class="fn">_step</span>(msgs)        <span class="cm"># 一次 LLM 调用 + 工具执行 + 持久化</span>
        <span class="kw">if not</span> self.<span class="fn">_decide_continuation</span>(ai):  <span class="cm"># 调了工具就继续，否则停</span>
            <span class="kw">break</span>
    <span class="kw">return</span> <span class="fn">LettaResponse</span>(messages=..., stop_reason=..., usage=...)
</pre></div>
```

**Steps:**

- [ ] **Step 1: 接线** `PAGES` / `SUBTITLES` / `CONTENT` 追加 03（`"03-message-lifecycle.html"`，标题/副标题如上）。
- [ ] **Step 2: 写 `LESSON_03`（zh+en）** 到上述结构与深度。
- [ ] **Step 3:（可选）加自测题**。
- [ ] **Step 4: 构建并验证 03 课 WARN-free**
  ```bash
  cd /home/verden/course/letta-visual-guide/src && python build.py && python check_links.py && python check_html.py
  ```
  Expected: `0 error(s)`，且无 `03-message-lifecycle.html` 的 `[WARN]`。
- [ ] **Step 5: 核对源码锚点**
  ```bash
  cd /home/verden/course/letta
  grep -rn "async def step" letta/agents/letta_agent_v3.py
  grep -rn "def _decide_continuation" letta/agents/letta_agent_v3.py
  grep -rn "def load" letta/agents/agent_loop.py
  ```
  Expected: 三者都命中。
- [ ] **Step 6: 提交**
  ```bash
  cd /home/verden/course/letta-visual-guide && git add src/ && git commit -m "feat(m1): add lesson 03 (lifecycle of one message)

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Task 4: M1 收尾 — 全量校验 + 导航链 + 目录页

**Files:** 无新增（验证 + 必要的小修）

- [ ] **Step 1: 全量构建与校验**
  ```bash
  cd /home/verden/course/letta-visual-guide/src && python build.py && python check_links.py && python check_html.py && echo ALL_OK
  ```
  Expected: 末尾 `ALL_OK`；`0 error(s)`；**三课（01/02/03）均无 `[WARN]`**（图数与 CJK 都达标）。`index.html` 目录页应显示"共 3 课 · 1 个部分"，并列出三课标题与副标题。
- [ ] **Step 2: 导航链与跨课引用自检**
  ```bash
  cd /home/verden/course/letta-visual-guide
  grep -c 'href="02-project-map.html"' lessons/01-what-is-letta.html      # 01 的"下一课"指向 02
  grep -c 'href="03-message-lifecycle.html"' lessons/02-project-map.html  # 02 的"下一课"指向 03
  grep -c 'href="01-what-is-letta.html"' lessons/02-project-map.html      # 02 的"上一课"指向 01
  ```
  Expected: 三个计数都为 1（外壳自动生成的上一课/下一课链成链）。
- [ ] **Step 3: 浏览器人工自检（手动）** 打开 `index.html`：三课可点进；每课图/代码/卡片/折叠正常；中英切换跨课保持；深色模式正常。
- [ ] **Step 4: 更新 roadmap 标记 M1 完成并提交**
  ```bash
  cd /home/verden/course/letta-visual-guide
  # 把 roadmap 的 M1 行标注 “✅ 已完成”
  git add docs/ && git commit -m "docs: mark M1 complete in roadmap

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
  ```

---

## Self-Review（对照 spec 第 4/5/6 节与本计划）

- **覆盖**：spec 第一部分 3 课（宏观全景）全部有 Task（1 扩写 01 / 2 新增 02 / 3 新增 03 / 4 收尾）。✔
- **页面结构（spec 5）**：每个 brief 都要求 lead + ≥4 卡（含 spark/key/analogy）+ ≥3 图/语言 + 2-3 代码 + 2-3 折叠 + 自测 + 自动导航。✔
- **内容准则（spec 6）**：CJK ≥3000 目标 4000+、必有 spark 亮点、关注整体、双语等价、源码"文件+符号"且写作时核实——均写进"共享约定 D/E"与每课 DoD。✔
- **源码准确**：每课有 Step 5 grep 核对锚点；全局锚点已对照 v0.16.8 核实。✔
- **占位符扫描**：无 TODO/TBD；图与代码给了可直接用的真实-类名草图；其余 prose 由实现者按 brief 写。
- **命名一致**：文件名 `01-what-is-letta.html` / `02-project-map.html` / `03-message-lifecycle.html` 在 PAGES/SUBTITLES/CONTENT/导航/校验中一致。
- **DoD 客观**：用 `check_html` 的 WARN-free 作为"图够多 + 字够多"的客观闸门，而非主观判断。
