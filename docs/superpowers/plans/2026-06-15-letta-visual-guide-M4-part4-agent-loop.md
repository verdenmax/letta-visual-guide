# Letta 图解教程 · M4 第四部分（Agent 执行循环，4 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第四部分「Agent 执行循环」的 4 课（13 AgentState 与 AgentLoop 工厂 · 14 V3 步进循环 · 15 从 heartbeat 到无 heartbeat · 16 工具规则 Tool Rules）。这一部分是"记忆系统（M3）"之后的**引擎室**——讲清楚 agent 收到消息后，**一步一步**是怎么转起来的：状态从哪来、循环怎么走、什么时候停、工具被什么规则约束。

**Architecture:** 同前。内容放**新文件 `src/part4.py`**（`registry.py` 加 `import part4`）。新增一课 = 改 `shell.PAGES` + `shell.SUBTITLES` + `registry.CONTENT` + `part4.py` + (可选)`quizzes.QUIZZES`。

**Tech Stack:** Python 3.11+ 标准库；自包含 HTML/CSS。讲解对象 `/home/verden/course/letta`（v0.16.8）。

---

## 强化内容准则（沿用 M3；务必逐条遵守）

> M1 共享约定（页面结构、卡片种类、双语等价、源码"文件+符号"且核实、无 `<h1>`、结尾回扣整体）+ M3 四条加强（反长文闸门、高频穿插视觉、`.note` ≥3/课、`.cute` ≥1/课）**全部继续生效**。M4 不降低任何标准。

1. **反长文（硬性，`check_html` 闸门）**：任何 `<p>` **≤ 200 中文字 / ≤ 120 英文词**，超了直接 WARN。每段只讲一个点；写长了拆段、或改成列表/图/note。**绝不允许连续 3 段以上纯文字**——中间必须插入一个非文字元素。
2. **高频穿插视觉**：平均**每 1–2 段**出现一个"非纯文字"块（图 / `.note` / `.cute` / 代码 / `<ul>` / 折叠）。
3. **`.note`（每课 ≥ 3）**：`note tip`（💡/🧠/✅）、`note info`（👉/📌）、`note warn`（⚠️）。把关键 takeaway / 易错点 / 预告拎出来。
4. **`.cute`（每课 ≥ 1）**：emoji + 标签画友好小示意图替代干解释（执行循环天然适合：🔁 循环、🧰 工具箱、🚦 红绿灯=tool rule、💓 心跳、🏭 工厂…）。
5. **更详细**：每课 CJK **目标 4500+**（≥3000 硬底）；**图 ≥ 4 张/语言**（`.cute` 计入，合计 ≥ 8）；**折叠 3–4 个**；机制讲透——但靠**更多小块**（多图/多 note/多列表/多折叠），不是更长的段落。

> 一句话：M4 要"**像图文并茂的科普长文**"，不是"**论文式大段落**"。

---

## 接线（首次用 part4.py）

`src/part4.py` 顶部写模块 docstring，依次 `LESSON_13 … LESSON_16`（各 `{"zh":..,"en":..}`）。`src/registry.py` 加 `import part4` 并在 `CONTENT` 追加 4 条。`shell.PAGES`/`SUBTITLES` 每课追加一行，`part_zh="第四部分 · Agent 执行循环"`、`part_en="Part 4 · The agent execution loop"`。`index.html` 顶部 pill「共 N 课 · N 个部分」会随 `PAGES` 自动更新（16 课 · 4 个部分）；务必跑 `build.py` 后确认。

**导航链**：第 12 课（capstone，`next=../index.html`）→ 改成 `next=13`；第 13 课 `prev=12`；16 课 `next=../index.html`。（build.py 依 `PAGES` 顺序自动生成 prev/next，只要顺序对即可。）

## 验证（每个 task 收尾，DoD）

```
cd src && python build.py && python check_links.py && python check_html.py
```
期望：`0 error / 0 warning`，`all N internal links resolve`，index pill 显示「共 16 课 · 4 个部分」（到 16 课时）。

---

## 已核实源码锚点（v0.16.8，3 个并行 research 子代理核实；引用只写"文件+符号"不写行号）

### 13 + 14（agent 状态 / 工厂 / V3 步进循环）
- **AgentState**：`letta/schemas/agent.py::AgentState`（Pydantic，`OrmMetadataBase→LettaBase→BaseModel`，`__id_prefix__="agent"`）。"重建一个持久化 agent 所需的全部信息"，是**内存/API 表示**，由 ORM 行 `letta/orm/agent.py` 水合（`from_orm_async`）。关键字段：`id/name/system/agent_type/llm_config`(已弃用→`model`)/`embedding_config`(弃用→`embedding`)/`message_ids`(在窗消息 id)/`memory: Memory`(弃用→`blocks`)/`blocks: List[Block]`/`tools/tool_rules/sources/tags/last_stop_reason/message_buffer_autoclear/pending_approval/timezone…`。`CreateAgent.agent_type` **默认 `letta_v1_agent`**（即默认走 V3）。
- **AgentLoop 工厂**：`letta/agents/agent_loop.py::AgentLoop.load`，`@staticmethod load(agent_state, actor) -> BaseAgentV2`。按 `agent_state.agent_type`（+`enable_sleeptime`/`multi_agent_group`）分派：`letta_v1_agent`/`sleeptime_agent`(非组) → **`LettaAgentV3`**；其余(memgpt_agent/memgpt_v2_agent/react_agent/workflow_agent/voice…) → **`LettaAgentV2`**；带 sleeptime+group → `SleeptimeMultiAgentV4/V3`。
- **AgentType 枚举**：`letta/schemas/enums.py::AgentType(str,Enum)`：`memgpt_agent`/`memgpt_v2_agent`/`letta_v1_agent`（注释："simplification of the memgpt loop, **no heartbeats or forced tool calls**"）/`react_agent`/`workflow_agent`/`split_thread_agent`/`sleeptime_agent`/`voice_convo_agent`/`voice_sleeptime_agent`。**⚠️ 没有 `letta_agent_v3` 这个值**——类叫 V3，枚举值是 `letta_v1_agent`。
- **三代（实际 4 个类）**：抽象接口 `letta/agents/base_agent_v2.py::BaseAgentV2`（`build_request/step/stream`）。① 旧 `letta/agent.py::Agent`（**同步** `def step`，`while True` 靠 heartbeat/function_failed 链式；工厂**不返回**它）；② `letta/agents/letta_agent_v2.py::LettaAgentV2`（**async** 重写，heartbeat 驱动续步）；③ `letta/agents/letta_agent_v3.py::LettaAgentV3(LettaAgentV2)`（**子类化 V2**，去 heartbeat、支持非工具返回/并行工具/审批；docstring："No heartbeats (loops happen on tool calls)"）。另有 `letta/agents/letta_agent.py::LettaAgent` 供 group/voice 用，非工厂路径。
- **step()**：`LettaAgentV3.step(input_messages, max_steps=DEFAULT_MAX_STEPS, …) -> LettaResponse`；**`DEFAULT_MAX_STEPS = 50`**（`letta/constants.py`）。**不流式**——`for i in range(max_steps)` 内 `async for chunk in self._step(...)` 抽干生成器；`if not self.should_continue: break`；`i==max_steps-1` 兜底设 `max_steps`；都没设则默认 `end_turn`。流式是另一个 `stream(...)`。
- **_step()**：`LettaAgentV3._step`，一次迭代＝"一次 LLM 调用 + 工具执行"。顺序：`_get_valid_tools`+`should_force_tool_call` → `_refresh_messages`（**不**重建系统提示，保前缀缓存）→ 审批/取消检查 → `_step_checkpoint_start` → `generate_request_system_prompt`+`build_request_data` → **LLM 调用**（外包一层 `ContextWindowExceededError→compact→retry`）→ 记 `context_token_estimate=usage.total_tokens` → `_handle_ai_response` → `_checkpoint_messages` 持久化（"持久化先于流式，避免不一致"）→ yield。
- **_handle_ai_response()**：`-> (messages_to_persist, continue_stepping, stop_reason)`。统一处理单/并行工具调用：校验每个 call 是否在 `valid_tool_names`（违规→`_build_rule_violation_result`，**不执行**）→ 执行（可并行）→ `register_tool_call` → 逐工具 `_decide_continuation`。无工具但有内容→`_decide_continuation(None,...)` 造 assistant 消息；需审批→造审批消息并停（`requires_approval`）。
- **_decide_continuation()**：`LettaAgentV3._decide_continuation`（**无 `request_heartbeat` 参数**，默认 `continue_stepping=True`）。规则 docstring："①没调工具→结束；②调了工具→继续"。覆盖：`is_terminal_tool`→停(`tool_rule`)；`has_children_tools`/`is_continue_tool`→继续；`tool_rule_violated`→继续；仍有未调的 `required_before_exit`→强制继续；`is_final_step`→停(`max_steps`)；无工具且 `finish_reason=="length"`→`max_tokens_exceeded`，否则 `end_turn`。
- **停止原因**：`letta/schemas/letta_stop_reason.py::StopReasonType(str,Enum)`：`end_turn/error/llm_api_error/invalid_llm_response/invalid_tool_call/max_steps/max_tokens_exceeded/no_tool_call/tool_rule/cancelled/insufficient_credits/requires_approval/context_window_overflow_in_system_prompt`。`LettaStopReason.run_status` 映射到 `completed/failed/cancelled`。

### 15（heartbeat → 无 heartbeat）
- **注入点**：`letta/services/helpers/tool_parser_helper.py::runtime_override_tool_json_schema`——给**每个非终止工具**加布尔参数 `request_heartbeat` 并标 **required**（终止工具不加）。
- **常量**（`letta/constants.py`）：`REQUEST_HEARTBEAT_PARAM="request_heartbeat"`；`REQUEST_HEARTBEAT_DESCRIPTION`（"…设 True 才能链式继续，默认 False 立即结束链"）；`REQ_HEARTBEAT_MESSAGE`/`FUNC_FAILED_HEARTBEAT_MESSAGE`（均带前缀 `NON_USER_MSG_PREFIX="[This is an automated system message hidden from the user] "`）。
- **旧 heartbeat 环**：解析在 `letta/agent.py::Agent._handle_ai_response`（`function_args.pop("request_heartbeat")`；tool rule 覆盖：children/continue→True、terminal→False；函数失败→`function_failed=True`）；链式在 `Agent.step`——`heartbeat_request`→注入 `REQ_HEARTBEAT_MESSAGE`、`function_failed`→注入 `FUNC_FAILED_HEARTBEAT_MESSAGE`（均 `role=user`），否则 `break`。`finish_reason=="length"` 旧版**直接 raise**。
- **insert_heartbeat**：`letta/local_llm/function_parser.py::insert_heartbeat`——给已解析的 function call 参数**强制塞** `request_heartbeat=True`；本地 LLM 纠偏路径（`NO_HEARTBEAT_FUNCS=["send_message"]`，issue #601）。
- **V2 vs V3**：`letta_agent_v2.py::_get_valid_tools` 传 `request_heartbeat=True`（**V2 仍用 heartbeat**）；`letta_agent_v3.py::_get_valid_tools` 传 `request_heartbeat=False`（注释 "difference for v3"，**V3 不注入**），且 `_handle_ai_response` 里 `args.pop(REQUEST_HEARTBEAT_PARAM, None)` 防御性丢弃。V3 续步全靠 `_decide_continuation`（"调了工具就继续"）。
- **前后对比锚点修正**：解析在 `Agent._handle_ai_response`（不是 `inner_step`；`inner_step` 调它）+ 链式在 `Agent.step`。

### 16（工具规则 Tool Rules）
- **9 种规则**：`letta/schemas/enums.py::ToolRuleType` ↔ `letta/schemas/tool_rule.py` 子类：`run_first`→`InitToolRule`(可带 `args` 预填)；`exit_loop`→`TerminalToolRule`；`continue_loop`→`ContinueToolRule`；`conditional`→`ConditionalToolRule`(`child_output_mapping`/`default_child`/`require_output_mapping`)；`constrain_child_tools`→`ChildToolRule`(`children`/`child_arg_nodes`)；`max_count_per_step`→`MaxCountPerStepToolRule`(`max_count_limit`)；`parent_last_tool`→`ParentToolRule`(`children`)；`required_before_exit`→`RequiredBeforeExitToolRule`；`requires_approval`→`RequiresApprovalToolRule`。基类 `BaseToolRule.get_valid_tools(history, available, last_resp)`，属性 `requires_force_tool_call`。
- **求解器**：`letta/helpers/tool_rule_solver.py::ToolRulesSolver`。`model_post_init` 按类型**分桶**（init/continue/child_based[含 Child+Conditional+MaxCount]/parent/terminal/required_before_exit/requires_approval）。核心 `get_allowed_tool_names(available_tools, error_on_empty, last_function_response) -> list`：首步且有 init 规则→只返回 init 工具；否则对 `child_based+parent` 规则的 `get_valid_tools` 求**交集**∩available。其它方法：`is_terminal_tool`/`is_continue_tool`/`has_children_tools`/`has_required_tools_been_called`/`get_uncalled_required_tools`/`is_requires_approval_tool`/`should_force_tool_call`/`register_tool_call`/`guess_rule_violation`/`compile_tool_rule_prompts`。
- **违规＝合成错误不执行**：`letta/agents/helpers.py::_build_rule_violation_result` 返回 `ToolExecutionResult(status="error", func_return="[ToolConstraintError] Cannot call <tool>, valid tools include: [...]")`（+`guess_rule_violation` 提示）。
- **接入 V3**：`letta_agent_v3.py::_get_valid_tools`（约束送给 LLM 的工具 schema + 终止工具走 `runtime_override_tool_json_schema`）；`_handle_ai_response`（事后校验 `tool_rule_violated`）；`_decide_continuation`（terminal/children/continue/required 决定续停）。审批：`is_requires_approval_tool`→停 `requires_approval` + 造审批消息。
- **校验**：无环/冲突检测；仅 per-rule pydantic 校验 + `agent_manager_helper.py::check_supports_structured_output` 限"多个 init 规则"。

---

## Task 1: 新增第 13 课「AgentState 与 AgentLoop 工厂」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part4.py`(**新建** + `LESSON_13`) · `src/registry.py`(import part4 + CONTENT) · (可选)`src/quizzes.py`

**filename:** `13-agent-state-and-loop.html`；标题 zh「AgentState 与 AgentLoop 工厂」/ en「AgentState & the AgentLoop factory」；副标题 zh「一个 agent 的'存档' · 工厂按类型选引擎 · 三代 agent」/ en「an agent's 'save file'; the factory picks an engine by type; three generations」。

**学习目标（本部分的"地图"课）：** 讲清**执行循环的起点**：① `AgentState` 是一个 agent 的"存档"——`id/system/agent_type/blocks/message_ids/tools/tool_rules/llm_config…` 一应俱全，"重建 agent 所需的全部信息"都在这；它是**内存/API 表示**，由 ORM 行水合。② `AgentLoop.load` 是个**工厂**：拿 `agent_state.agent_type` 当钥匙，选出该用哪个 agent 实现（`letta_v1_agent`→V3，其余→V2）。③ **三代 agent** 怎么演化：旧同步 `Agent` → async `LettaAgentV2` → `LettaAgentV3`（子类化 V2，去 heartbeat）。为 14（V3 循环细节）、15（heartbeat 对比）、16（tool rules）铺路。

**亮点（`card spark`）：** 把第 6 课"有状态 vs 无状态"落到一个具体对象——**`AgentState` 就是那张"存档/save file"**：服务器自己不记忆，每次请求把整张存档从库里水合出来、跑完再存回去，于是同一个 agent 能在任意进程/机器上"读档续玩"。而 `AgentLoop.load` 是"**读档时选引擎**"：同一张存档，`agent_type` 决定用哪套循环（V3 简化环 / V2 heartbeat 环 / sleeptime 多 agent）。**最妙的反直觉点**：类名叫 `LettaAgentV3`，但触发它的枚举值却是 `letta_v1_agent`——因为"V3 代码"实现的正是"Letta v1 设计"（去掉 MemGPT 的 heartbeat 与强制工具调用）。命名是历史，行为看代码。

**必需卡片：** `lead`；`card macro`（AgentState=存档、AgentLoop=工厂选引擎、三代演化，一张总图）；`card analogy`（游戏存档 + 工厂按订单选生产线）；`card detail`（落到 `schemas/agent.py::AgentState`、`agent_loop.py::AgentLoop.load`、`enums.py::AgentType`）；`card spark`（存档/读档选引擎 + V3↔letta_v1 命名反直觉）；`card key`；`card warn`（**别被命名骗**：没有 `letta_agent_v3` 枚举值；类名≠枚举名；且 `memory/llm_config` 是弃用字段，新代码看 `blocks/model`）。**外加 ≥3 个 `.note`、≥1 个 `.cute`。**

**必需图（≥4/语言）：**
1. **AgentState 字段总览 `layers` 或 `flow`**：把存档拆成几组——身份(`id/name/agent_type`)、记忆(`blocks/memory`)、在窗(`message_ids/system`)、行为(`tools/tool_rules`)、模型(`llm_config/model`)；标注哪些喂给循环。
2. **工厂分派 `flow`/`vflow`（决策图）**：`agent_state.agent_type` → 判断 → `letta_v1_agent/sleeptime_agent`?→`LettaAgentV3`；else→`LettaAgentV2`（+sleeptime&group→`SleeptimeMultiAgentV4/V3`）。
3. **三代对照 `table.t`**：列＝代/类/同步异步/续步机制/工厂是否返回。行＝旧 `Agent`(sync,heartbeat,否) / `LettaAgentV2`(async,heartbeat,是) / `LettaAgentV3`(async,无heartbeat·调工具就继续,是)。
4. **`.cute` 萌图**：🏭 工厂 + 一张贴着 `agent_type` 标签的存档 📁 → 传送带选出 🤖V3 / 🤖V2 引擎，气泡"按类型选引擎"。
5. **AgentType → 类 映射 `table.t` 或 `cellgroup`**：9 个枚举值各落到 V3 还是 V2。

**必需代码（2–3，`codefile`）：**
- A) `AgentState` 关键字段（简化，源 `letta/schemas/agent.py::AgentState`）：标出弃用↔新字段（`memory→blocks`、`llm_config→model`）。
- B) `AgentLoop.load` 分派（简化，源 `letta/agents/agent_loop.py::AgentLoop.load`）：`if agent_type in [letta_v1_agent, sleeptime_agent]: return LettaAgentV3(...) else: return LettaAgentV2(...)`。
- C)（可选）`AgentType` 枚举节选（源 `letta/schemas/enums.py`），高亮 `letta_v1_agent` 那条注释"no heartbeats or forced tool calls"。

**必需折叠（3–4）：**
- 为什么用工厂模式（同一存档、`agent_type` 选实现；新增 agent 种类只改工厂）。
- "V3 类 / letta_v1 枚举"命名为什么错位（代码代际 vs 设计版本；历史包袱）。
- `AgentState` 的弃用字段（`memory`/`llm_config`/`sources` → `blocks`/`model`/`folders`）：为什么还在、该信哪个。
- 其实有"第 4 个类"`LettaAgent`（group/voice 用，非工厂路径）；以及 `BaseAgentV2` 抽象接口。

**自测题种子：** 工厂按什么选实现（`agent_type`）；哪个枚举值触发 V3（`letta_v1_agent`，不是 `letta_agent_v3`）；AgentState 里"在窗消息"是哪个字段（`message_ids`）；存档/无状态如何呼应第 6 课。

**草图（真实类；en 镜像；务必穿插 `.note`/`.cute`，段落 ≤200 CJK）：**

工厂分派（`flow`）：
```
<div class="flow">
  <div class="node"><div class="nt">输入</div><div class="nd">AgentState（agent_type=?）</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">AgentLoop.load</div><div class="nd">读 agent_type 选引擎</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">letta_v1_agent / sleeptime</div><div class="nd">LettaAgentV3（无 heartbeat）</div></div>
</div>
```
`.cute`（工厂选引擎）：
```
<div class="cute"><div class="row"><span class="emoji">📁</span><span class="lab">存档·agent_type</span><span class="arrow">→</span><span class="emoji">🏭</span><span class="arrow">→</span><span class="emoji">🤖</span><span class="bubble">V3 引擎</span></div>
<div class="cap">同一张存档，工厂按 agent_type 选出该用哪套循环</div></div>
```
`.note warn`（命名反直觉）：
```
<div class="note warn"><span class="ni">⚠️</span><span class="nx">没有 <span class="mono">letta_agent_v3</span> 这个枚举值！触发 <span class="mono">LettaAgentV3</span> 的是 <span class="mono">agent_type="letta_v1_agent"</span>——"V3 代码"实现的是"Letta v1 设计"。<strong>命名看历史，行为看代码。</strong></span></div>
```
三代对照（`table.t`）：列 代 / 类 / 同步? / 续步机制 / 工厂返回。

<!-- 后续 Task 2/3/4（lessons 14/15/16）将逐个补入。 -->

---

## Task 2: 新增第 14 课「V3 步进循环」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part4.py`(`LESSON_14`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `14-v3-step-loop.html`；标题 zh「V3 步进循环」/ en「The V3 step loop」；副标题 zh「一次 step = 一次 LLM 调用 + 工具执行 · 调了工具就继续 · 最多 50 步」/ en「one step = one LLM call + tool exec; loop while tools are called; up to 50 steps」。

**学习目标：** 把 13 课"工厂选出的 V3 引擎"拆开看它**怎么转**：① `step()` 是一个 `for i in range(max_steps)` 的循环，`DEFAULT_MAX_STEPS = 50`；每轮跑一次 `_step` 抽干其生成器，最后返回一个 `LettaResponse`。② `_step` 一次迭代＝**一次 LLM 调用 + 工具执行 + 持久化**（取有效工具→刷消息→LLM→`_handle_ai_response`→落库→yield）。③ 续/停由 `_decide_continuation` 拍板，规则极简——**"没调工具就结束、调了工具就继续"**，外加 terminal/required/max_steps/审批 几个覆盖。④ 收尾枚举 `StopReasonType`。

**亮点（`card spark`）：** "Agent"听着玄，落到代码就是**一个带预算的 for 循环**：`调 LLM → 执行工具 → 问一句"还继续吗" → 重复，最多 50 次`。而那句"还继续吗"的判据简单到反直觉——**不看模型有没有说"我想继续"，只看它这轮有没有调用工具**（调了＝还有活干，继续；没调＝该把话交还用户，结束）。这正是 `letta_v1_agent` 注释说的"no heartbeats"。再加一个工程小细节却是"可恢复性"的关键：**先持久化、再流式输出**——哪怕流到一半进程崩了，AgentState 里也已记下这步，下次读档能接上（呼应 13 课"存档"）。

**必需卡片：** `lead`；`card macro`（step 循环 + _step 内部 + 续停判据，总图）；`card analogy`（流水线工人：拿活→干活→看看还有没有下一件→最多干 50 件下班）；`card detail`（`letta_agent_v3.py::step/_step/_handle_ai_response/_decide_continuation`、`constants.py::DEFAULT_MAX_STEPS`、`letta_stop_reason.py::StopReasonType`）；`card spark`（带预算的 for 循环 + "调了工具就继续" + 先存后流）；`card key`；`card warn`（`step()` **不流式**——它抽干 `_step` 生成器返回单个 `LettaResponse`；流式是另一个 `stream()`；别把两者混了）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）：**
1. **step 主循环 `vflow`/环形 `flow`**：进入 → `_step`（一次 LLM+工具）→ `should_continue?` →（是）回到顶；（否）break；`i==49` 兜底 `max_steps`。
2. **`_step` 内部流水 `vflow`**：取有效工具+是否强制 → 刷消息(不重建系统提示) → LLM 调用(套 compact 重试) → `_handle_ai_response`(执行工具/校验) → 持久化 → yield。
3. **`_decide_continuation` 决策树 `flow`**：调工具? →否→（有未调 required?→继续 / 否→`end_turn`）；→是→ terminal?→停`tool_rule` / 否→继续；`is_final_step`→停`max_steps`。
4. **`.cute` 萌图**：🔁 仓鼠轮 + 里程表"step 3/50"，气泡"调了工具？再转一圈！"。
5. **停止原因 `table.t`**：`end_turn/tool_rule/max_steps/max_tokens_exceeded/requires_approval/cancelled/…` 各自"何时触发" + `run_status`(completed/failed/cancelled)。

**必需代码（2–3，`codefile`）：**
- A) `step()` 主循环（简化，源 `letta_agent_v3.py::step`）：`for i in range(max_steps): async for chunk in self._step(...): ...; if not self.should_continue: break`，`i==max_steps-1`→`max_steps`，默认 `end_turn`。
- B) `_decide_continuation`（简化，源同文件）：`if tool_call_name is None: return False,…,end_turn`；`else: register; if is_terminal_tool: stop tool_rule; ... if is_final_step: stop max_steps`。
- C)（可选）`_step` 骨架：valid_tools → LLM invoke（外层 `except ContextWindowExceededError: compact; retry`）→ `_handle_ai_response` → `_checkpoint_messages`（"持久化先于流式"）。

**必需折叠（3–4）：**
- 为什么"先持久化再流式"（崩溃可恢复、状态不脏；引用 `_checkpoint_messages` 注释）。
- `max_steps=50` 是什么保险（防失控自循环；到顶 → `max_steps` 停因，`run_status=completed`）。
- `_step` 里的 `ContextWindowExceededError → compact → retry`（把第 12 课压缩接到循环里：撞窗就地压完重试）。
- 并行工具调用：执行完**强制 `continue`** 让模型把多个结果汇总（除非命中 terminal/max_steps）。

**自测题种子：** 一次 `_step` 做哪三件事（LLM 调用+工具执行+持久化）；续步判据是什么（调了工具就继续）；`DEFAULT_MAX_STEPS`＝?（50）；到顶停因（`max_steps`）；`step()` 流式吗（否，返回 `LettaResponse`）。

**草图（真实类；en 镜像）：**

step 主循环（环形 `flow`）：
```
<div class="flow">
  <div class="node"><div class="nt">_step</div><div class="nd">一次 LLM 调用 + 工具执行</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">should_continue?</div><div class="nd">_decide_continuation</div></div>
  <div class="arrow">↻ 是</div>
  <div class="node"><div class="nt">否 → break</div><div class="nd">设 stop_reason，返回 LettaResponse</div></div>
</div>
```
`.note tip`（续步判据）：
```
<div class="note tip"><span class="ni">🧠</span><span class="nx">续停只问一句：<strong>这轮调工具了吗？</strong>调了→还有活→继续；没调→把话交还用户→<span class="mono">end_turn</span>。不看模型"想不想继续"——这就是 V3 的"无 heartbeat"。</span></div>
```

---

## Task 3: 新增第 15 课「从 heartbeat 到无 heartbeat」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part4.py`(`LESSON_15`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `15-heartbeat-to-no-heartbeat.html`；标题 zh「从 heartbeat 到无 heartbeat」/ en「From heartbeat to no-heartbeat」；副标题 zh「MemGPT 的 request_heartbeat 链式 · V3 为什么把它拿掉 · 前后对比」/ en「MemGPT's request_heartbeat chaining; why V3 drops it; before/after」。

**学习目标：** 讲清一个**设计演化**：① 原始 MemGPT/旧 `Agent`/V2 给**每个非终止工具**塞了一个 required 布尔参 `request_heartbeat`——模型必须在工具调用里设 `=true` 才能"继续下一步"；框架还会在**函数出错**时自动补一次 heartbeat 让模型补救。② 这套靠"模型自报继续"的链式，到 V3 被**整个拿掉**：`request_heartbeat=False` 不再注入，循环改成"调了工具就继续"（14 课的规则）。③ 顺带讲 `insert_heartbeat`（本地 LLM 忘设时的纠偏）。给出**清晰前后对比**。

**亮点（`card spark`）：** 这是一堂"**少即是多**"的设计课。旧机制把"要不要继续"的决定权交给**模型**（设 `request_heartbeat=true`）——灵活，但脆：模型一忘设，agent 就在用户说完话后"卡死"不动（于是才有 `insert_heartbeat` 这种打补丁的纠偏，还专门为本地模型修过 issue #601）。V3 的洞见是：**这个决定根本不该问模型**——"调了工具" 本身就是"还有后续"的可靠信号，框架据此决定即可。于是一个 required 参数、一串 heartbeat 提示消息、一类"模型忘设"的 bug，**一起消失**。把控制流从"模型自觉"收回到"框架确定"，是 agent 工程走向可靠的典型一步。

**必需卡片：** `lead`；`card macro`（旧 heartbeat 链 vs V3 无 heartbeat，一张对比总图）；`card analogy`（旧＝对讲机"完毕，请继续"必须每次手动喊，忘喊就冷场；新＝只要你还在递工具单，流水线默认继续）；`card detail`（`tool_parser_helper.py::runtime_override_tool_json_schema`、`agent.py::Agent._handle_ai_response/step`、`local_llm/function_parser.py::insert_heartbeat`、`letta_agent_v3.py::_get_valid_tools`、`constants.py` 几个常量）；`card spark`（少即是多：删一个参数=删一类 bug）；`card key`；`card warn`（**别记错**：解析在 `Agent._handle_ai_response`（不是 `inner_step`）；`request_heartbeat` 是 **required** 且**只加非终止工具**；V2 仍用 heartbeat，只有 V3 拿掉；旧版 `finish_reason=="length"` 直接 raise、不是 heartbeat）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）：**
1. **前后对比 `cols`/`table.t`**：左＝旧（schema 含 required `request_heartbeat`；模型设 true→注入 `REQ_HEARTBEAT_MESSAGE`(role=user)→继续；出错→`FUNC_FAILED_HEARTBEAT_MESSAGE`）；右＝V3（不注入；`_decide_continuation`：调了工具就继续）。
2. **旧 heartbeat 链 `vflow`**：LLM 调工具(`request_heartbeat=true`) → `_handle_ai_response` 读旗标 → `step` 注入 heartbeat 用户消息 → 再来一步；`false`→break。
3. **`.cute` 萌图**：💓 对讲机喊"完毕,请继续"（旧）↔ 🔁 默认继续（新），气泡"忘喊就冷场 / 不用喊"。
4. **注入点示意 `flow`**：工具 schema → `runtime_override_tool_json_schema(request_heartbeat=True/False)` → (旧)加 `request_heartbeat:bool[required]` /(V3)不加。
5.（可选）`insert_heartbeat` 纠偏 `.note info`：本地模型忘设、上一条是 user、这条是非 `send_message` 工具 → 自动补 heartbeat。

**必需代码（2–3，`codefile`）：**
- A) 注入 `request_heartbeat`（简化，源 `tool_parser_helper.py::runtime_override_tool_json_schema`）：非终止工具才加，且进 `required`；`REQUEST_HEARTBEAT_DESCRIPTION`。
- B) 旧链式（简化，源 `agent.py::_handle_ai_response`+`step`）：`hb = args.pop("request_heartbeat"); ... if function_failed: inject FUNC_FAILED_…; elif hb: inject REQ_HEARTBEAT_…; else: break`。
- C) V3 不注入（源 `letta_agent_v3.py::_get_valid_tools`）：`runtime_override_tool_json_schema(..., request_heartbeat=False)  # NOTE: difference for v3`；+ `args.pop(REQUEST_HEARTBEAT_PARAM, None)` 防御丢弃。

**必需折叠（3–4）：**
- `request_heartbeat` 到底加在哪、为什么 required、为什么终止工具不加。
- 函数出错的"自动 heartbeat"：旧版靠它让模型看到错误并补救（`FUNC_FAILED_HEARTBEAT_MESSAGE`）。
- `insert_heartbeat` 与 issue #601：本地模型忘设导致冷场的历史补丁。
- V3 为什么能安全删掉：续步信号改用"调了工具"（更可靠）；V2 为何仍保留（兼容旧设计）。

**自测题种子：** `request_heartbeat` 是谁、加在哪类工具（非终止、required）；旧版怎么靠它继续（模型设 true→注入 heartbeat 用户消息）；V3 怎么决定继续（调了工具就继续，不看 heartbeat）；删掉它顺带消灭了哪类 bug（模型忘设导致冷场）。

**草图（真实类；en 镜像）：**

前后对比（`cols`）：左旧右新，各配一段 `codefile`。
`.note warn`（易错点）：
```
<div class="note warn"><span class="ni">⚠️</span><span class="nx">解析 heartbeat 的是 <span class="mono">Agent._handle_ai_response</span>（<span class="mono">inner_step</span> 只是调用它）；<span class="mono">request_heartbeat</span> 是 <strong>required</strong> 且<strong>只加非终止工具</strong>；<strong>V2 仍用 heartbeat，只有 V3 拿掉</strong>。</span></div>
```

---

## Task 4: 新增第 16 课「工具规则 Tool Rules」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part4.py`(`LESSON_16`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `16-tool-rules.html`；标题 zh「工具规则 Tool Rules」/ en「Tool rules」；副标题 zh「9 种规则 · ToolRulesSolver 算合法下一步 · 违规＝合成错误不执行」/ en「9 rule types; the solver computes the legal next set; a violation becomes a synthetic error, not an execution」。

**学习目标（本部分收尾）：** 讲清 Letta 的**声明式工具约束**：① 9 种 `ToolRuleType`（`run_first/exit_loop/continue_loop/conditional/constrain_child_tools/max_count_per_step/parent_last_tool/required_before_exit/requires_approval`）各管什么。② `ToolRulesSolver` 怎么把一堆规则**分桶**，并在每一步算出"**合法的下一步工具集**"（首步强制 init；其余对 child/parent 规则求交集）。③ 关键设计：模型若选了**非法工具**，框架**不执行**，而是合成一条 `[ToolConstraintError]` 错误喂回去让它改。④ 接回 14 课：terminal/required/approval 怎么影响续停。

**亮点（`card spark`）：** Tool rules 把"agent 能怎么用工具"从**模型的自觉**变成**可声明、可执行的状态机**。最漂亮的两个设计：其一，**约束是"算"出来的**——`ToolRulesSolver` 每步对所有相关规则的"合法集"求**交集**，得到"此刻只准调这些"，再把 schema 缩到这个集合喂给 LLM（从源头减少模型乱选）；其二，**违规不是崩溃、而是教学**——模型万一仍选了非法工具，框架不执行它，而是返回一条 `[ToolConstraintError] Cannot call X, valid tools include: [...]` 当作"工具返回"喂回去，模型读到后自己改正。约束既前置（缩 schema）又兜底（合成错误），把"放飞的 LLM"收成"按图施工的执行器"——这也是 14 课那个极简循环敢"调了工具就继续"的底气：有 tool rules 兜着。

**必需卡片：** `lead`；`card macro`（9 种规则 + solver 算合法集 + 违规合成错误，总图）；`card analogy`（红绿灯/路牌：init=必须先走这条、terminal=到此下车、child=只能拐进这几条岔路、required_before_exit=离场前必须打卡）；`card detail`（`schemas/tool_rule.py` 九子类、`helpers/tool_rule_solver.py::ToolRulesSolver`、`agents/helpers.py::_build_rule_violation_result`、接入 `letta_agent_v3.py`）；`card spark`（约束＝交集运算 + 违规＝合成错误教学）；`card key`；`card warn`（常见误区：违规工具**不会被执行**；`get_allowed_tool_names` 只对 **child/parent** 规则求交集，terminal/continue/required/approval 不缩集、在循环里另行处理；枚举值是 `run_first/exit_loop…` 不是 `Init/Terminal…`）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）：**
1. **9 种规则 `table.t`**：列＝枚举值 / 子类 / 关键字段 / 一句话含义。（直接用研究表）
2. **solver 算合法集 `vflow`**：分桶 → 首步?有 init?→只返 init 工具；否则对 child+parent 规则 `get_valid_tools` 求交集 ∩ available → 合法集 → 缩 schema 喂 LLM。
3. **违规处理 `flow`**：LLM 选工具 → 在合法集? →是→执行+`register_tool_call`；→否→`_build_rule_violation_result` 合成 `[ToolConstraintError]`（不执行）→喂回模型。
4. **`.cute` 萌图**：🚦 红绿灯 + 工具箱 🧰，气泡"现在只准调这几个"。
5. **规则↔续停 `cellgroup`/`table.t`**：terminal→停`tool_rule`；continue/child→继续；required_before_exit→未打卡强制继续；requires_approval→停`requires_approval`+审批消息（接 14 课）。

**必需代码（2–3，`codefile`）：**
- A) 几种规则定义速览（简化，源 `schemas/tool_rule.py`）：`InitToolRule(run_first)`、`TerminalToolRule(exit_loop)`、`ChildToolRule(constrain_child_tools, children)`、`MaxCountPerStepToolRule(max_count_limit)`。
- B) `get_allowed_tool_names` 核心（简化，源 `tool_rule_solver.py`）：首步 init；否则 `set.intersection(*[r.get_valid_tools(...) for r in child_based+parent]) & available`。
- C) 违规合成错误（源 `agents/helpers.py::_build_rule_violation_result`）：`ToolExecutionResult(status="error", func_return="[ToolConstraintError] Cannot call …, valid tools include: …")`。

**必需折叠（3–4）：**
- 9 种规则逐个一句话 + 一个迷你例子（如 `run_first` 强制先 search、`max_count_per_step` 防刷同一工具）。
- 合法集为什么用"交集"（多条规则同时生效，取共同允许）；为什么 terminal/required 不参与缩集。
- 违规为什么"合成错误"而非抛异常（让模型自纠、循环不中断；接 14 课"调了工具就继续"——违规也算调了工具，继续让它改）。
- `requires_approval` 审批流：停 `requires_approval`、造审批消息、`is_approval_response` 恢复（接 14 课停因）。

**自测题种子：** 哪种规则强制第一步（`run_first`/Init）；违规工具会被执行吗（不会，合成 `[ToolConstraintError]`）；solver 算合法集对哪类规则求交集（child/parent）；`requires_approval` 触发什么停因（`requires_approval`）；枚举值长啥样（`run_first` 等，不是 `Init`）。

**草图（真实类；en 镜像）：**

违规处理（`flow`）：
```
<div class="flow">
  <div class="node"><div class="nt">LLM 选了工具 X</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">X ∈ 合法集?</div><div class="nd">get_allowed_tool_names</div></div>
  <div class="arrow">否 →</div>
  <div class="node"><div class="nt">不执行</div><div class="nd">合成 [ToolConstraintError] 喂回模型</div></div>
</div>
```
`.note tip`（亮点一句）：
```
<div class="note tip"><span class="ni">💡</span><span class="nx">约束<strong>双保险</strong>：前置——把 schema 缩到合法集，从源头少让模型乱选；兜底——真选错了也不执行，合成 <span class="mono">[ToolConstraintError]</span> 让它自己改。</span></div>
```
9 种规则 `table.t`：列 枚举值 / 子类 / 字段 / 含义（用研究表）。

---

## Task 5: 集成与合并（M4 收尾）

**Files:** `docs/superpowers/plans/2026-06-15-letta-visual-guide-roadmap.md` · （验证）全站

- [ ] 全量构建：`cd src && python build.py && python check_links.py && python check_html.py`，期望 `0 error / 0 warning`、`all N internal links resolve`、index pill「共 16 课 · 4 个部分」。
- [ ] 导航链抽查：`12→13→14→15→16`，每课 `prev/next` 各 1，16 课 `next=../index.html`。
- [ ] roadmap 把 **M4** 标 `✅ 已完成并合并`（计划文档名填入）。
- [ ] 合并：`git checkout master && git merge --no-ff feat/m4-agent-loop`；合并后再跑一次三件套确认绿。
- [ ] `git branch -d feat/m4-agent-loop`；`git push origin master`。
- [ ] 报告 M4 完成，询问用户是否继续 M5（工具系统，17–20）。

---

## Self-Review（写完即查）

1. **Spec coverage**：spec 第四部分 13–16 四课 ↔ Task 1–4 一一对应（AgentState/AgentLoop ✓、V3 步进 ✓、heartbeat 对比 ✓、tool rules ✓）。✅
2. **Placeholder scan**：无 TBD/TODO；每个 task 给了 filename/学习目标/亮点/卡片/图/代码/折叠/自测题/草图（含真实 HTML 片段与已核实锚点）。✅
3. **Type/name consistency**：全程用 `AgentState`/`AgentLoop.load`/`AgentType.letta_v1_agent`/`LettaAgentV2`/`LettaAgentV3`/`DEFAULT_MAX_STEPS`/`_step`/`_handle_ai_response`/`_decide_continuation`/`StopReasonType`/`ToolRulesSolver`/`runtime_override_tool_json_schema`/`_build_rule_violation_result`，与"已核实锚点"一致。✅
4. **跨课一致**：15 课"无 heartbeat"与 14 课"调了工具就继续"同源；16 课 terminal/approval 续停与 14 课 `StopReasonType` 衔接；13 课"存档"回扣第 6 课无状态。✅
