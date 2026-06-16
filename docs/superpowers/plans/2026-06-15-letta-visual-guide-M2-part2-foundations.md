# Letta 图解教程 · M2 第二部分（前置基础，3 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第二部分「前置基础」的 3 课（04 LLM agent 与 tool calling 基础 · 05 上下文窗口的根本问题 · 06 有状态 vs 无状态），为后面的记忆系统 / agent 循环 / 工具 / provider 打底。

**Architecture:** 同 M1。新增一课 = 改 4 处（`shell.PAGES`、`shell.SUBTITLES`、`registry.CONTENT`、`part2.py` 内容）+（可选）`quizzes.QUIZZES`。**注意：本部分内容放新文件 `src/part2.py`**（M1 的三课在 `part1.py`）；`registry.py` 需 `import part2`。

**共享约定 / 页面结构 / 内容准则 / 每课 DoD：完全沿用 M1 计划的"共享约定"一节**（见 `2026-06-15-letta-visual-guide-M1-part1-overview.md`）。要点复述：
- 每课 zh CJK **>= 3000，目标 4000+**；**>= 3 图/语言（合计 >= 6）**类型多样；**>= 4 卡**含 `analogy`/`key`("本课要点"/"Key points")/`spark`(真正的亮点，不泛泛)；**2-3 代码**（伪代码 + 简化源码，`codefile`/`pre.code`，ASCII，`<`→`&lt;`、`&`→`&amp;`）；**2-3 折叠**（示例→为什么→源码在哪(文件+符号)→替代）；正文无 `<h1>`；结尾回扣整体；中英信息等价；源码引用"文件+符号"不写行号且写作时核实。
- DoD：`cd src && python build.py && python check_links.py && python check_html.py` → `0 error(s)` 且**目标课无 `[WARN]`**；每课一提交，含 `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`。
- 设计系统类名见 M1 计划（cards / cols / vflow / flow / layers / timeline / cellgroup / table.t / codefile+spans cm/kw/fn/st/nb / pre.code / span.inline / span.mono）。

**首次新增 part2.py 的接线：** 在 `src/registry.py` 顶部加 `import part2`，并在 `CONTENT` 里加 part2 的条目；`src/part2.py` 顶部写模块 docstring，依次定义 `LESSON_04/05/06`。

### 本部分已核实源码锚点（v0.16.8）
- 工具/思考：`letta/functions/schema_generator.py::generate_schema`；`letta/llm_api/helpers.py::add_inner_thoughts_to_functions` / `unpack_inner_thoughts_from_kwargs`；`letta/local_llm/constants.py`（`INNER_THOUGHTS_KWARG`、`INNER_THOUGHTS_KWARG_DESCRIPTION(_GO_FIRST)`、`VALID_INNER_THOUGHTS_KWARGS`）；`letta/constants.py::REQUEST_HEARTBEAT_PARAM`、`DEFAULT_MAX_STEPS=50`。
- 上下文窗口：`letta/services/context_window_calculator/context_window_calculator.py`、`token_counter.py`；`letta/schemas/memory.py::ContextWindowOverview`；`letta/services/summarizer/thresholds.py::get_compaction_trigger_threshold`。
- 状态/身份：`letta/schemas/agent.py::AgentState`（`CreateAgent`/`UpdateAgent`）；`letta/schemas/letta_base.py::LettaBase`（`generate_id`、`__id_prefix__`）；`letta/schemas/block.py`（`Block`/`CreateBlock`/`BlockUpdate`）；`letta/orm/custom_columns.py`（pydantic-in-DB）。

---

## Task 1: 新增第 04 课「LLM agent 与 tool calling 基础」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part2.py`(新建 + `LESSON_04`) · `src/registry.py`(import part2 + CONTENT) · (可选)`src/quizzes.py`

**filename:** `04-agent-and-tools.html`；标题 zh「LLM agent 与 tool calling 基础」/ en「LLM agents & tool calling」；副标题 zh「函数调用怎么工作 · ReAct 循环 · 内心独白」/ en「How function calling works; the ReAct loop; inner monologue」。

**学习目标：** 讲清"agent = LLM + 工具 + 循环"；function/tool calling 在**消息层**到底怎么工作（请求里带工具 schema；模型只**产出** tool_call；你的代码执行；把 tool result 回填；模型再继续）；ReAct（想→做→看→再想）；以及 Letta 为什么逼模型"先写内心独白再动手"。为第四、五部分打底。

**亮点（`card spark`）：** Letta 把"思维链"**塞进每个工具的一个参数**（`inner_thoughts`/`thinking`，由 `add_inner_thoughts_to_functions` 注入），甚至**强制它第一个生成**（`..._GO_FIRST`）——于是即便底层 provider 没有原生"思考"通道，模型也**被结构性地逼着"先推理后行动"**。推理从"但愿它会想"变成"调用格式里必须先想"。

**必需卡片：** `lead`；`macro`（agent=LLM+工具+循环）；`analogy`（实习生 + 工具箱 + 便签：先写思路再动手）；`detail`（tool schema → tool_call → tool result 消息；`inner_thoughts` kwarg）；`spark`（上面）；`key`；`warn`（模型**不会**自己执行工具，它只产出一个调用请求，真正执行的是你的代码——这关系到安全）。

**必需图（≥3/语言，建议 4）：**
1. **function calling 往返 `flow`**（见草图）。
2. **ReAct 循环 `vflow`**：想(reason/内心独白) → 做(tool call) → 看(observe result) → 再想…直到回话。
3. **一次工具调用的消息序列 `cellgroup`**：user → assistant(含 inner_thoughts + tool_call) → tool(result) → assistant(reply)。
4. **inner_thoughts 注入 `cols`**：普通工具 schema vs 注入了 `inner_thoughts` 参数后的 schema。

**必需代码（2-3，标注 文件+符号）：**
- A) `codefile`：一个工具在模型眼里的 JSON schema（name/description/parameters）。来源 `letta/functions/schema_generator.py::generate_schema`。
- B) `codefile`：`add_inner_thoughts_to_functions` 给每个函数塞一个 `inner_thoughts` 参数（描述见 `local_llm/constants.py`）。来源 `letta/llm_api/helpers.py::add_inner_thoughts_to_functions`。

**必需折叠（2-3）：** 「模型不会自己执行工具」（运行时执行 + 安全）；「为什么把思考塞进参数而非单独字段」（跨 provider 统一、可强制顺序）；「ReAct vs 直接回答」（循环何时有用）。

**自测题种子：** 模型产出的是什么（一个 tool_call 请求，而非执行）；为什么把 `inner_thoughts` 做成参数（强制先想、跨厂商统一）；ReAct 的循环顺序。

**草图（真实类；en 镜像）：**

function calling 往返（`flow`）：
```html
<div class="flow">
  <div class="node"><div class="nt">请求</div><div class="nd">messages + 工具 schema</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">模型产出</div><div class="nd">tool_call(name, args)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">你的代码执行</div><div class="nd">真正跑这个函数</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">回填结果</div><div class="nd">tool result 消息</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">模型继续</div><div class="nd">再想 / 回话</div></div>
</div>
```

inner_thoughts 注入（`codefile`）：
```html
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/helpers.py</span><span class="ln">add_inner_thoughts_to_functions（简化）</span></div>
<pre><span class="cm"># 给每个工具 schema 注入一个"内心独白"参数，并要求最先生成</span>
<span class="kw">def</span> <span class="fn">add_inner_thoughts_to_functions</span>(functions, inner_thoughts_key, inner_thoughts_description):
    <span class="kw">for</span> schema <span class="kw">in</span> functions:
        schema[<span class="st">"parameters"</span>][<span class="st">"properties"</span>][inner_thoughts_key] = {
            <span class="st">"type"</span>: <span class="st">"string"</span>, <span class="st">"description"</span>: inner_thoughts_description,
        }
        schema[<span class="st">"parameters"</span>][<span class="st">"required"</span>].insert(0, inner_thoughts_key)  <span class="cm"># 必填且排第一</span>
    <span class="kw">return</span> functions
</pre></div>
```

**Steps:**
- [ ] **Step 1: 接线**（PAGES/SUBTITLES 追加 04；`registry.py` 加 `import part2` 与 `"04-agent-and-tools.html": part2.LESSON_04`；`part2.py` 建文件 + `LESSON_04` 占位 stub）。PAGES 元组：
  ```python
      ("04-agent-and-tools.html", "LLM agent 与 tool calling 基础", "LLM agents & tool calling",
       "第二部分 · 前置基础", "Part 2 · Foundations"),
  ```
  SUBTITLES：
  ```python
      "04-agent-and-tools.html": ("函数调用怎么工作 · ReAct 循环 · 内心独白",
                                  "How function calling works; ReAct loop; inner monologue"),
  ```
- [ ] **Step 2: 写 `LESSON_04`（zh+en）** 到上述结构与深度（**staged**：先接线+stub 跑通 build，再填 zh，再填 en；每次 `python -c "import part2"` 验证）。
- [ ] **Step 3:（可选）加自测题**。
- [ ] **Step 4: 验证 WARN-free**：`cd src && python build.py && python check_links.py && python check_html.py` → 0 errors，无 `04-agent-and-tools.html` 的 WARN。
- [ ] **Step 5: 核对锚点**：`cd /home/verden/course/letta`；`grep -rn "def add_inner_thoughts_to_functions" letta/llm_api/helpers.py`；`grep -rn "def generate_schema" letta/functions/schema_generator.py`；`grep -rn "INNER_THOUGHTS_KWARG" letta/local_llm/constants.py`。
- [ ] **Step 6: 提交** `feat(m2): add lesson 04 (LLM agents & tool calling)`（含 trailer；`git add src/ lessons/ index.html`）。

---

## Task 2: 新增第 05 课「上下文窗口的根本问题」

**Files:** `src/shell.py` · `src/part2.py`(`LESSON_05`) · `src/registry.py` · (可选)`src/quizzes.py`

**filename:** `05-context-window.html`；标题 zh「上下文窗口的根本问题」/ en「The context-window problem」；副标题 zh「token 预算 · prefill/decode · prefix cache · 为什么需要记忆系统」/ en「token budget; prefill/decode; prefix cache; why a memory system」。

**学习目标：** 把上下文窗口理解成**有限的 token 预算**；模型怎么处理它（prefill 整段 prompt、decode 逐 token、KV cache）；为什么**稳定前缀**重要（prefix cache → 省时省钱）；为什么"全塞进去"会失败（成本涨、窗口满）——这正是 MemGPT/Letta 存在的根本理由。Letta 还**主动度量**它（`ContextWindowOverview` / `token_counter`）并据此**压缩**。

**亮点（`card spark`）：** 上下文窗口是 agent 的 RAM，而它**既有限、每个 token 又要花钱**——所以"管理记忆"不是锦上添花，而是**被经济规律逼出来的刚需**。Letta 把它变成可**度量**（`ContextWindowOverview`）、可**触发动作**（逼近阈值就压缩）的东西；第 3 课"稳定前缀 + 变化尾巴"正是 prefill/prefix-cache 经济学的直接产物。

**必需卡片：** `lead`；`macro`（有限 token 预算 = 核心约束）；`analogy`（办公桌台面：放得下的才看得见，满了得收拾）；`detail`（`ContextWindowOverview`/`token_counter` 度量；压缩阈值 `get_compaction_trigger_threshold`）；`spark`（被经济逼出来 + Letta 度量并行动）；`key`；`warn`（上下文越多 ≠ 越好：成本、延迟、"lost in the middle"）。

**必需图（≥3/语言，建议 4）：**
1. **token 预算条 `cellgroup`**（见草图）。
2. **prefill vs decode `flow`**：prefill 一次吃整段 prompt（前缀可缓存）→ decode 一个一个吐 token。
3. **prefix cache `timeline`**：稳定前缀(system) 命中缓存、变化尾巴重算 → 省时省钱。
4. **窗口满了的两条路 `cols`**：直接塞爆（失败）vs 分层记忆+压缩（Letta）。

**必需代码（2-3）：**
- A) `codefile`：`ContextWindowOverview` 的关键字段（整窗 token 账本）。来源 `letta/schemas/memory.py::ContextWindowOverview`。
- B) `codefile`/`pre.code`：压缩触发伪代码（token 估算 vs 阈值 → 压缩）。来源 `letta/services/summarizer/thresholds.py::get_compaction_trigger_threshold` + `letta_agent_v3._step`。

**必需折叠（2-3）：** 「prefill / decode / KV cache 一分钟」；「为什么稳定前缀省钱」（prefix cache）；「长上下文模型不就解决了？」（成本/延迟/lost-in-middle，仍需管理）。

**自测题种子：** 核心约束是什么（有限 token 预算）；为什么稳定前缀（prefix cache 命中）；长上下文为何不能完全替代记忆管理。

**草图（真实类；en 镜像）：**

token 预算条（`cellgroup`）：
```html
<div class="cellgroup">
  <div class="cg-cap"><b>一个固定大小的 token 预算</b>：system + 在窗消息 + 工具 schema 一起挤这条；满了就得换出</div>
  <div class="cols">
    <div class="col"><h4>system（含核心记忆）</h4><p>稳定前缀，尽量不动</p></div>
    <div class="col"><h4>在窗消息 + 工具 schema</h4><p>会增长的尾巴；逼近上限就触发压缩</p></div>
  </div>
</div>
```

ContextWindowOverview（`codefile`）：
```html
<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/memory.py</span><span class="ln">ContextWindowOverview（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">ContextWindowOverview</span>:
    context_window_size_max: int       <span class="cm"># 这个模型的上限</span>
    context_window_size_current: int   <span class="cm"># 当前已用</span>
    num_tokens_system: int             <span class="cm"># system 占多少</span>
    num_tokens_core_memory: int        <span class="cm"># 核心记忆占多少</span>
    num_tokens_messages: int           <span class="cm"># 在窗消息占多少</span>
    <span class="cm"># ... Letta 把"窗口里都装了啥"算得清清楚楚，才能决定何时压缩</span>
</pre></div>
```

**Steps:**（同 Task 1 的 6 步；PAGES/SUBTITLES/CONTENT 用 05 的值；锚点核对 `grep -rn "class ContextWindowOverview" letta/schemas/memory.py`、`grep -rn "def get_compaction_trigger_threshold" letta/services/summarizer/thresholds.py`；提交 `feat(m2): add lesson 05 (the context-window problem)`）。

---

## Task 3: 新增第 06 课「有状态 vs 无状态」

**Files:** `src/shell.py` · `src/part2.py`(`LESSON_06`) · `src/registry.py` · (可选)`src/quizzes.py`

**filename:** `06-stateful-vs-stateless.html`；标题 zh「有状态 vs 无状态」/ en「Stateful vs stateless」；副标题 zh「AgentState 存档 · prefixed id · schema 与 orm · 对比 OpenAI Assistants」/ en「The AgentState save; prefixed ids; schema vs orm; vs OpenAI Assistants」。

**学习目标：** 比第 1/3 课更深地讲**机制**：Letta 怎么把 agent 序列化成 `AgentState`；**prefixed id** 身份方案（`agent-…`、`block-…`）；**schema（pydantic API）vs orm（SQLAlchemy DB）**两套模型 + create/update/read 三件套；存档怎么**往返**（DB 行 ↔ pydantic ↔ 活的运行时）；并和 **OpenAI Assistants 具体对比**（谁拥有状态、可否导出/版本化、是否模型无关、记忆可否编辑）。

**亮点（`card spark`）：** 因为整个 agent 就是**数据**（带稳定 prefixed id 的序列化 `AgentState`），Letta 拿到了"进程常驻型 agent"拿不到的性质：可以像文件一样**复制 / 共享 / 版本化 / 检视**一个 agent，可以**换掉底层模型**，可以**到处运行**——agent 是**可移植的数据**，不是一个必须一直开着的进程。**身份在 id 里，不在某个活对象里。**

**必需卡片：** `lead`；`macro`（agent = 序列化数据 + 稳定身份）；`analogy`（游戏存档 + 角色卡：换台机器读档还是同一个角色）；`detail`（`AgentState`、`letta_base.py` prefixed id、schema vs orm）；`spark`（agent 即可移植数据）；`key`；`warn`（"有状态数据"≠"无状态运行时"，精确重申第 3 课）。

**必需图（≥3/语言，建议 4）：**
1. **存档 round-trip `flow`**：DB 行(orm) → load → `AgentState`(pydantic) → 跑一步 → save → DB 行。
2. **prefixed id 身份 `table.t`**：`agent-…`/`block-…`/`message-…`/`user-…`/`organization-…` → 前缀即类型/身份。
3. **schema vs orm 两套模型 `cols`**：pydantic（API 契约 / create-update-read）vs SQLAlchemy（DB 行）。
4. **Letta vs OpenAI Assistants `table.t`**：谁存状态、可否导出/版本化、是否模型无关、记忆是否可编辑。

**必需代码（2-3）：**
- A) `codefile`：prefixed id 生成。来源 `letta/schemas/letta_base.py::generate_id` / `__id_prefix__`。
- B) `codefile`：某资源的 create/update/read 三件套（如 `CreateBlock`/`BlockUpdate`/`Block`，或 `CreateAgent`/`AgentState`）。来源 `letta/schemas/block.py` / `letta/schemas/agent.py`。

**必需折叠（2-3）：** 「schema 与 orm 为什么分两套」（API 稳定性 vs DB 形态；`custom_columns` 把 pydantic 存进 DB）；「prefixed id 有什么好处」（类型安全、好调试、不撞车）；「和 OpenAI Assistants 到底差在哪」（归属、可移植、模型无关、记忆可编辑）。

**自测题种子：** 一个 agent 物理上是什么（库里一条序列化 `AgentState`）；id 前缀编码了什么（类型/身份）；schema 与 orm 各自的角色。

**草图（真实类；en 镜像）：**

prefixed id 身份（`table.t`）：
```html
<table class="t">
  <tr><th>实体</th><th>id 形如</th><th>前缀即身份</th></tr>
  <tr><td>Agent</td><td class="mono">agent-1a2b...</td><td>一眼看出这是个 agent</td></tr>
  <tr><td>Block（记忆块）</td><td class="mono">block-9f8e...</td><td>可被多个 agent 共享引用</td></tr>
  <tr><td>Message</td><td class="mono">message-7c6d...</td><td>recall 里按 id 取</td></tr>
  <tr><td>User / Org</td><td class="mono">user-... / organization-...</td><td>多租户作用域</td></tr>
</table>
```

存档 round-trip（`flow`）：
```html
<div class="flow">
  <div class="node"><div class="nt">DB 行</div><div class="nd">orm 模型</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">load</div><div class="nd">to_pydantic_async</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">AgentState</div><div class="nd">活的运行时读它跑一步</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">save</div><div class="nd">写回 DB 行</div></div>
</div>
```

**Steps:**（同 Task 1 的 6 步；PAGES/SUBTITLES/CONTENT 用 06 的值；锚点核对 `grep -rn "def generate_id" letta/schemas/letta_base.py`、`grep -rn "class AgentState" letta/schemas/agent.py`、`grep -rn "class CreateBlock\|class BlockUpdate" letta/schemas/block.py`；提交 `feat(m2): add lesson 06 (stateful vs stateless)`）。

---

## Task 4: M2 收尾 — 全量校验 + 导航链 + roadmap

- [ ] **Step 1: 全量校验**：`cd src && python build.py && python check_links.py && python check_html.py && echo ALL_OK` → `ALL_OK`，`0 error(s)`，**04/05/06 均无 WARN**；`index.html` 显示"共 6 课 · 2 个部分"。
- [ ] **Step 2: 导航链自检**：03 的"下一课"指向 04；04→05；05→06（`grep -c` 各为 1）。
- [ ] **Step 3: 浏览器人工自检（手动）**：六课可点进、图/代码/折叠正常、中英切换跨课保持、深色模式正常、第二部分在目录页单列一组。
- [ ] **Step 4: roadmap 标记 M2 完成并提交**。

---

## Self-Review（对照 spec 第 4 节第二部分 + 内容准则）

- **覆盖**：spec 第二部分 3 课（04 基础 / 05 上下文 / 06 状态）各有 Task。✔
- **去重**：06 与第 1/3 课有概念交集，但本课聚焦**序列化 / 身份 / schema-orm / 与 Assistants 对比**的更深机制，并显式"在 M1 基础上加深"，避免重复。✔
- **页面结构 / 内容准则 / DoD**：沿用 M1 共享约定（CJK≥3000、≥3 图/语言、spark 亮点、双语等价、源码文件+符号且核实、WARN-free 客观闸门）。✔
- **锚点**：每课 Step 5 grep 核对；全局锚点已对照 v0.16.8 核实。✔
- **占位符扫描**：无 TODO/TBD；每课给了真实-类名草图（flow/codefile/cellgroup/table.t）+ 接线值；prose 由实现者按 brief 写。
- **命名一致**：`04-agent-and-tools.html` / `05-context-window.html` / `06-stateful-vs-stateless.html`；内容在新文件 `src/part2.py`，`registry.py` 需 `import part2`。
