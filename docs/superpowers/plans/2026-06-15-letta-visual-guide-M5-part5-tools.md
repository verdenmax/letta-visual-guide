# Letta 图解教程 · M5 第五部分（工具系统，4 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第五部分「工具系统」的 4 课（17 工具即 Python 函数 + docstring · 18 不执行就生成 schema · 19 工具分发与执行（含 MCP）· 20 自定义工具沙箱与安全修复）。延续 M4「执行循环」的引擎室视角，往下钻一层：agent 调用的「工具」到底**怎么定义、怎么生成 schema、怎么按类型分发执行、怎么在沙箱里安全运行**。

**Architecture:** 同前。内容放**新文件 `src/part5.py`**（`registry.py` 加 `import part5`）。新增一课 = 改 `shell.PAGES` + `shell.SUBTITLES` + `registry.CONTENT` + `part5.py` + (可选)`quizzes.QUIZZES`。

**Tech Stack:** Python 3.11+ 标准库；自包含 HTML/CSS。讲解对象 `/home/verden/course/letta`（v0.16.8）。

---

## 强化内容准则（沿用 M3/M4；务必逐条遵守）

> M1 共享约定（页面结构、卡片种类、双语等价、源码"文件+符号"且核实、无 `<h1>`、结尾回扣整体）+ M3 四条加强（反长文闸门、高频穿插视觉、`.note` ≥3/课、`.cute` ≥1/课）**全部继续生效**。

1. **反长文（硬闸门）**：任何 `<p>` **≤ 200 中文字 / ≤ 120 英文词**，超了 WARN。每段一个点；绝不连续 3 段以上纯文字——中间插非文字元素。
2. **高频穿插视觉**：平均每 1–2 段一个"非纯文字"块（图 / `.note` / `.cute` / 代码 / `<ul>` / 折叠）。
3. **`.note`（每课 ≥ 3）**：tip（💡/🧠/✅）/ info（👉/📌）/ warn（⚠️）。
4. **`.cute`（每课 ≥ 1）**：emoji 萌图替代干解释（工具系统天然适合：🔧 函数、📜 schema、🏭 工厂分发、📦 沙箱、🔌 MCP、🔐 信任边界…）。
5. **更详细**：每课 CJK **目标 4500+**（≥3000 硬底）；**图 ≥ 4 张/语言**（`.cute` 计入）；**折叠 3–4 个**；2–3 codefiles。靠**更多小块**实现，不是更长段落。

> 一句话：M5 要"像图文并茂的科普长文"，不是"论文式大段落"。

---

## 接线（首次用 part5.py）

`src/part5.py` 顶部写模块 docstring，依次 `LESSON_17 … LESSON_20`（各 `{"zh":..,"en":..}`）。`src/registry.py` 加 `import part5` 并在 `CONTENT` 追加 4 条。`shell.PAGES`/`SUBTITLES` 每课追加一行，`part_zh="第五部分 · 工具系统"`、`part_en="Part 5 · The tool system"`。`index.html` pill「共 N 课 · N 个部分」随 `PAGES` 自动更新（到 20 课 · 5 个部分）；跑 `build.py` 后确认。

**导航链**：第 16 课（capstone，`next=../index.html`）→ build 自动改成 `next=17`；17 课 `prev=16`；20 课 `next=../index.html`。

## 验证（每个 task 收尾，DoD）
```
cd src && python build.py && python check_links.py && python check_html.py
```
期望：`0 error / 0 warning`，`all N internal links resolve`，index pill「共 20 课 · 5 个部分」（到 20 课时）。

## 执行策略（两阶段，防 cut-off）
每课分两次派发：**Phase A**＝scaffold + wiring + 填 zh（留 en 为 `<p>stub</p>`，逐步提交）；**Phase B**＝填 en 镜像 + 加 quiz。各 task 仍跑**完整 spec + 质量双重审查**（claude-opus-4.8）。

---

## 已核实源码锚点（v0.16.8，3 个并行 research 子代理核实；引用只写"文件+符号"不写行号）

### 17（工具 = 函数 + docstring → schema）
- **生成器**：`letta/functions/schema_generator.py::generate_schema(function, name=None, description=None, tool_id=None)`——用 `inspect.signature` + `docstring_parser.parse`（Google 风格）+ 手写 `type_to_json_schema_type` 拼出 OpenAI JSON schema。函数级 description 由 docstring 短/长描述拼成（缺则 `"No description available"`）。
- **docstring 是硬契约**：每个参数缺描述 → `raise ValueError("Parameter '…' lacks a description in the docstring")`；缺类型注解 → `raise TypeError("… lacks a type annotation")`。但 `validate_google_style_docstring` 只是**告警**（其 ValueError 被 catch 成 warning）——硬约束在**逐参数**层面。
- **类型映射**：`type_to_json_schema_type`：`{int:integer,str:string,bool:boolean,float:number}`；`Optional[X]` 解包；一般 `Union` → `NotImplementedError`；`List[X]`→array；`Literal`→enum；带参 `Dict[k,v]` → `ValueError`（建议用 Pydantic model）；`BaseModel` → `pydantic_model_to_json_schema`（用 `model.model_json_schema()`，**非** TypeAdapter/create_model）。**required** = 无默认值 **且** 非 Optional。
- **保留参数**：`letta/constants.py::TOOL_RESERVED_KWARGS = ["self", "agent_state"]`，在 schema 里被跳过。`request_heartbeat`（`REQUEST_HEARTBEAT_PARAM`）**不**由 generate_schema 加（运行时另注入，见第 15 课）。
- **示例 docstring**：`letta/functions/function_sets/base.py`（`send_message`/`archival_memory_insert`/`conversation_search`，Google 风 `Args:`/`Returns:`/`Examples:`）。

### 18（不执行就生成 schema · AST · TypeScript）
- **派生器**：`letta/functions/functions.py::derive_openai_json_schema(source_code, name=None)`——**纯 AST**：`_parse_function_from_source` → `MockFunction` → 复用 `generate_schema`。**绝不 `exec`/`import` 用户代码**。错误包成 `LettaToolCreateError`。
- **MockFunction 在 `functions.py`**（不是 ast_parsers.py！）：设 `__name__/__doc__/__signature__`，使 `inspect.signature`/`parse(__doc__)` 在未运行的代码上照常工作；`__call__` 抛 NotImplementedError。`_parse_function_from_source`：`ast.parse`（SyntaxError→LettaToolCreateError），取**最后**一个 `FunctionDef`，要求 docstring，用 `ast.literal_eval` 重建默认值，未知 BaseModel 用 `type(name,(BaseModel,),{...})` 桩。
- **AST 工具**：`letta/functions/ast_parsers.py`：`get_function_name_and_docstring`（取最后 FunctionDef，docstring 可选）、`resolve_type`（白名单 `_ALLOWED_TYPE_NAMES`，`allow_unsafe_eval=False` 默认，未白名单→`ValueError`）、`coerce_dict_args_by_annotations`（调用时强转）。
- **TypeScript**：`letta/functions/typescript_parser.py::derive_typescript_json_schema`——**正则**解析 `export function`，JSDoc 取描述，`?` 标可选；`union`→string、`any`→string。`ToolSourceType`（`enums.py`）= `python/typescript/json`。**TS 工具创建必须显式传 json_schema**（`ToolCreate.validate_typescript_requires_schema` 否则 ValueError）。
- **接线**：schema 在**创建时**自动派生（仅 Python）：`letta/services/tool_manager.py`（custom 且无 json_schema → 调）→ `letta/services/tool_schema_generator.py::generate_schema_for_tool_creation`（按 source_type 分派 derive_openai/derive_typescript/args_schema 路径）。**已不在** pydantic 校验器里（`schemas/tool.py::Tool.refresh_source_code_and_json_schema` 仅对内置类型按模块重建、对 custom 缺 schema 仅告警）。

### 19（分发与执行 · 含 MCP）
- **ToolType 枚举**（`letta/schemas/enums.py`，11 个）：`CUSTOM`(custom，默认) · `LETTA_CORE` · `LETTA_MEMORY_CORE` · `LETTA_MULTI_AGENT_CORE` · `LETTA_SLEEPTIME_CORE` · `LETTA_VOICE_SLEEPTIME_CORE` · `LETTA_BUILTIN` · `LETTA_FILES_CORE` · `EXTERNAL_LANGCHAIN`(弃用) · `EXTERNAL_COMPOSIO`(弃用) · `EXTERNAL_MCP`。
- **工厂**：`letta/services/tool_executor/tool_execution_manager.py::ToolExecutorFactory`——`_executor_map: ClassVar[Dict[ToolType, Type[ToolExecutor]]]`，`get_executor(tool_type, …)` 返回实例；**默认兜底 `SandboxToolExecutor`**（`CUSTOM`/`LETTA_VOICE_SLEEPTIME_CORE`/两个 external 弃用项都走兜底）。
- **真正入口**是同文件 `ToolExecutionManager.execute_tool_async(function_name, function_args, tool, step_id=None)`：建 executor → `AsyncTimer` 计时 → `executor.execute(...)` → 超 `tool.return_char_limit` 截断 → 异常包成 `ToolExecutionResult(status="error", …)`。
- **执行器**（基类 `tool_executor_base.py::ToolExecutor`，`async def execute(...) -> ToolExecutionResult`）：`core_tool_executor.py::LettaCoreToolExecutor`（core+**memory**+sleeptime，直跑，`function_map` 含 `core_memory_append/replace` 等）；`builtin_tool_executor.py::LettaBuiltinToolExecutor`（`run_code`/`web_search`/`fetch_webpage`/`run_code_with_tools`）；`files_tool_executor.py::LettaFileToolExecutor`；`mcp_tool_executor.py::ExternalMCPToolExecutor`（连外部 MCP server）；`sandbox_tool_executor.py::SandboxToolExecutor`（**自定义工具/多 agent/兜底** → 交沙箱，接第 20 课）。
- **ToolExecutionResult**（`schemas/tool_execution_result.py`）：`status:Literal["success","error"]`、`func_return`、`stdout/stderr:list[str]`、`sandbox_config_fingerprint`、`success_flag` 属性。**与第 16 课 `_build_rule_violation_result` 返回同型**（已确认）。
- **tool_type 赋值**：schema 默认 `CUSTOM`；注册时按名字归类（`tool_manager.py::upsert_base_tools`：`name in BASE_TOOLS→LETTA_CORE`、`BASE_MEMORY_TOOLS→LETTA_MEMORY_CORE`、`BUILTIN_TOOLS→LETTA_BUILTIN`、`FILES_TOOLS→LETTA_FILES_CORE`…）；MCP 显式设（`create_mcp_tool_async` → `tool_type=EXTERNAL_MCP`）。
- **MCP**：`letta/functions/mcp_client/types.py`：`MCPServerType`=`sse/stdio/streamable_http`；配置类 `StdioServerConfig`(command/args/env)、`SSEServerConfig`/`StreamableHTTPServerConfig`(server_url/auth…)；`MCPTool(Tool)` + `MCPToolHealth`。`ToolCreate.from_mcp` → `tags=["mcp:<server>"]`。**执行**：`ExternalMCPToolExecutor` → `MCPManager().execute_mcp_server_tool(...)`（**不走沙箱**，每次开新连接 `connect_to_server→execute_tool→cleanup`）。传输客户端在 `letta/services/mcp/`（**不是** `functions/mcp_client/`），工厂 `mcp_manager.py::MCPManager.get_mcp_client`。
- **内置工具**：`constants.py::BUILTIN_TOOLS=["run_code","run_code_with_tools","web_search","fetch_webpage"]`。

### 20（沙箱 · 安全修复）
- **沙箱类型**：`letta/schemas/enums.py::SandboxType`=`E2B/MODAL/LOCAL`；配置 `schemas/sandbox_config.py`（`LocalSandboxConfig`:sandbox_dir/use_venv/venv_name/pip_requirements 等）。**选择**（`sandbox_tool_executor.py`）：tool.metadata `sandbox=="modal"` 且启用 → Modal；否则 `settings.py::ToolSettings.sandbox_type`（有 `e2b_api_key`→E2B，否则 LOCAL）。
- **生成脚本**：`letta/services/tool_sandbox/base.py::AsyncToolSandboxBase.generate_execution_script` / `_render_sandbox_code`——① 服务端 **`pickle.dumps(agent_state)`**；② 参数按 `repr()` 内联字面量（`convert_param_to_str_value`）；③ 用户 `source_code` **逐字内联**；④ 调用工具；⑤ 结果 + `agent_state.model_dump(mode='json')` 打包成 **JSON** 写 stdout（带帧）。脚本内再用 `coerce_dict_args_by_annotations(...)` 按注解强转。
- **信任边界**（本课核心，画图用）：
  - **server→sandbox = pickle（受信）**：`agent_state` 由服务端用自己的对象 `pickle.dumps`、沙箱内 `pickle.loads`；权限向**下**流入低信任沙箱，不是"反序列化不可信输入"。（Modal v2 用 `tool_sandbox/safe_pickle.py::safe_pickle_dumps`，加 10MB/深度 50 的**防崩溃/DoS**护栏，非防恶意。）
  - **sandbox→server = JSON（不可信）**：沙箱跑了任意用户代码，其 stdout **绝不 `pickle.loads`**，只 `json.loads`。帧：`MARKER(16, uuid5 字节) ‖ LENGTH(4, '>I') ‖ MD5(32, hex) ‖ JSON_PAYLOAD`。
  - **校验**：`local_sandbox.py::parse_out_function_results_markers` 找 marker、按 length 切片、比 MD5，不符 → `raise Exception("Function ran, but output is corrupted.")`；再由 `tool_parser_helper.py::parse_stdout_best_effort` `json.loads` + `AgentState.model_validate`（pydantic 重水合，非 pickle）。防的是用户工具往 stdout 打**假结果/假 marker**污染结果通道。
- **PR #3343**（commit `1131535`，"use JSON instead of pickle for sandbox->server tool result transport"）：把 sandbox→server 的 payload 从 **pickle 改成 JSON**（消除"对不可信沙箱输出 `pickle.loads`"的 RCE）。**marker+length+MD5 帧本就存在**（不是 #3343 引入）；server→sandbox 仍 pickle agent_state（有意的受信方向）。
- **本地沙箱**：`local_sandbox.py::AsyncToolSandboxLocal`：venv 按需建/复用（`venv.create(with_pip=True)` + `pip install -r`），脚本写临时 `.py`，`asyncio.create_subprocess_exec` 跑，超时 `tool_settings.tool_sandbox_timeout`(默认 180s)。
- **⚠️ 锚点修正**：spec 里的 `letta/templates/sandbox_code_file.py.j2` **在 v0.16.8 未被引用**（`grep sandbox_code_file` 无 .py 命中）；真实脚本由 `base.py::_render_sandbox_code` 拼。**讲解请引 Python 构造器，可把 `.j2` 作为"对照参考"提一句**。`generate_execution_script` 的 docstring（"base64-encode/pickle the result"）也已**过时**（实为 JSON）；变量名 `..._pkl` 是遗留命名、装的是 JSON 字节。

---

## Task 1: 新增第 17 课「工具即 Python 函数 + docstring」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part5.py`(**新建** + `LESSON_17`) · `src/registry.py`(import part5 + CONTENT) · (可选)`src/quizzes.py`

**filename:** `17-tool-as-function.html`；标题 zh「工具即 Python 函数 + docstring」/ en「A tool is a Python function + docstring」；副标题 zh「generate_schema · docstring 是 API 契约 · 类型映射」/ en「generate_schema; the docstring is the API contract; type mapping」。

**学习目标（Part-5 开篇）:** 讲清"一个工具到底是什么"：一个 Letta 工具就是一个**普通 Python 函数**；`generate_schema` 把它的**签名 + Google 风 docstring** 变成模型看见的 **OpenAI JSON schema**。模型**永远看不到你的代码**，只看到这份 schema——所以 **docstring 是 API 契约**，不是注释。Letta 把这条强制成硬约束：参数没写描述 → 创建工具时直接 `ValueError`；没写类型注解 → `TypeError`。再讲类型映射与保留参数（`self`/`agent_state` 被隐藏）。为 18（不执行就生成 schema）、19（分发执行）铺路。

**亮点（`card spark`）:** **docstring 不是给人看的注释，而是你写给"模型"的 API 文档。** 模型从不读你的函数体，它做工具调用的全部依据，就是 `generate_schema` 从你的**签名 + docstring** 拼出来的那份 schema。所以一句含糊或缺失的参数描述，<strong>直接降低模型用对这个工具的概率</strong>——这不是风格问题，是<strong>功能</strong>问题。Letta 干脆把它变成<strong>编译期错误</strong>：任一参数缺描述，<span class="mono">generate_schema</span> 直接 <span class="mono">raise ValueError</span>，工具压根建不出来。一句话——<strong>给模型写 docstring，而不是给同事写</strong>。这也呼应第 4 课："工具是 agent 与世界的接口"，而 schema 正是这个接口的"类型签名"。

**必需卡片:** `lead`；`card macro`（函数 → generate_schema → JSON schema，一张总图）；`card analogy`（docstring = 餐厅菜单：厨房（你的代码）顾客看不见，点菜只认菜单上的名称+描述+选项）；`card detail`（落到 `schema_generator.py::generate_schema`、`type_to_json_schema_type`、`function_sets/base.py`、`TOOL_RESERVED_KWARGS`）；`card spark`（docstring 是写给模型的 API + 缺描述=编译期错误）；`card key`；`card warn`（易错点：函数级描述可缺省，但**每个参数**必须有描述(ValueError)+类型注解(TypeError)；带参 `Dict[k,v]`/一般 `Union` 不支持；`self`/`agent_state` 不进 schema；`request_heartbeat` 不由 generate_schema 加）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **生成流程 `flow`**：Python 函数（签名+docstring）→ `generate_schema`（inspect.signature + docstring_parser）→ OpenAI JSON schema（name/description/parameters）。
2. **类型映射 `table.t`**：列＝Python 类型 / JSON schema / 备注。行＝`str→string`、`int→integer`、`bool→boolean`、`float→number`、`Optional[X]→X(去 required)`、`List[X]→array`、`Literal→enum`、`BaseModel→object(model_json_schema)`、`Dict[k,v]→✗ ValueError`、`Union→✗ NotImplementedError`。
3. **`.cute` 萌图**：📝 docstring + 🔧 函数 → 📜 schema → 🤖 模型照单点菜，气泡"我只看菜单"。
4. **required 判定 `vflow`/`flow`**：有默认值? 或 Optional? → 否且否 → 进 `required`；否则可选。
5.（可选）**保留参数 `.note info`**：`self`/`agent_state` 被 `TOOL_RESERVED_KWARGS` 跳过，不出现在模型看到的 schema 里（它们由运行时注入）。

**必需代码（2–3，`codefile`）:**
- A) 一个真实基础工具的 Google docstring（源 `function_sets/base.py`，如 `archival_memory_insert` 或 `send_message`）——标出 `Args:` 里每个参数的描述。
- B) `generate_schema` 核心（简化，源 `schema_generator.py`）：`sig=inspect.signature(f)`；`doc=parse(f.__doc__)`；逐参数取 `doc.params` 描述，缺则 `raise ValueError`；`type_to_json_schema_type(annotation)`；据"无默认且非 Optional"决定 required。
- C) 生成出的 JSON schema 长啥样（`{"name","description","parameters":{"type":"object","properties":{…},"required":[…]}}`）。

**必需折叠（3–4）:** 为什么 docstring 是契约（模型只见 schema、不见代码）；类型映射的边界（Optional 解包、Dict/Union 为何不支持、Pydantic model 怎么处理）；保留参数 `self`/`agent_state` 与（对比）运行时注入的 `request_heartbeat`；Google 风校验只是"告警"、真正拦人的是逐参数的描述/注解检查。

**自测题种子:** 模型做工具调用看的是什么（schema，不是代码）；参数缺 docstring 描述会怎样（创建时 ValueError）；`self`/`agent_state` 会出现在 schema 里吗（不会，保留参数）；`Dict[str,int]` 能直接当参数类型吗（不能，建议 Pydantic model）。

**草图（真实类；en 镜像；段落 ≤200 CJK；穿插 `.note`/`.cute`）:**

生成流程（`flow`）：
```
<div class="flow">
  <div class="node"><div class="nt">Python 函数</div><div class="nd">签名 + Google docstring</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">generate_schema</div><div class="nd">inspect.signature + docstring_parser</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">OpenAI JSON schema</div><div class="nd">模型看到的"菜单"</div></div>
</div>
```
`.note warn`（硬契约）：
```
<div class="note warn"><span class="ni">⚠️</span><span class="nx">每个参数<strong>必须</strong>在 docstring 里有描述，否则 <span class="mono">generate_schema</span> 直接 <span class="mono">raise ValueError</span>；缺类型注解则 <span class="mono">TypeError</span>。<strong>docstring 不全，工具建不出来。</strong></span></div>
```

<!-- 后续 Task 2/3/4（lessons 18/19/20）+ Task 5（集成）将逐个补入。 -->

---

## Task 2: 新增第 18 课「不执行就生成 schema」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part5.py`(`LESSON_18`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `18-schema-without-executing.html`；标题 zh「不执行就生成 schema」/ en「Deriving the schema without executing」；副标题 zh「derive_openai_json_schema · AST 静态解析 · TypeScript」/ en「derive_openai_json_schema; static AST parsing; TypeScript」。

**学习目标:** 第 17 课假设"已经有一个 Python 函数对象"。但用户**上传一段源码**注册自定义工具时，服务端必须在**绝不运行这段代码**的前提下产出 schema。`derive_openai_json_schema` 的做法：**纯 AST 解析** → 造一个 `MockFunction`（只带 `__name__/__doc__/__signature__`）→ **复用第 17 课的 `generate_schema``。同时讲：AST 工具的白名单类型解析、TypeScript 工具（正则、必须显式传 schema）、以及这套在**创建工具时**怎么接线。

**亮点（`card spark`）:** **"从一段你拒绝运行的代码里，生成它的 schema。"** 想读一个函数的签名，最朴素的办法是 `import` 它再 `inspect`——可 `import` 用户提交的代码＝在你服务器上**任意代码执行**。Letta 的巧招：把源码 `ast.parse` 成语法树（**只读不跑**），据此造一个 `MockFunction`——它只伪装出 `__name__/__doc__/__signature__` 三样，`__call__` 直接抛错——再把它喂给**完全相同的** `generate_schema`。模型拿到一份真 schema，你的服务器却一行用户代码都没执行。连代码里引用的未定义 Pydantic 类型，也是用 `type(name,(BaseModel,),{})` **造个桩**，而不是去 import。**把"安全"变成了一道"解析"题**——这正是第 20 课沙箱哲学的前奏："工具的代码，自始至终不可信"。

**必需卡片:** `lead`；`card macro`（源码 → AST → MockFunction → generate_schema → schema，一张总图）；`card analogy`（不拆封就验货：靠包装上印的"成分表/规格"(AST 读签名)建档，而不是拆开试用(import 运行)）；`card detail`（`functions.py::derive_openai_json_schema`/`MockFunction`/`_parse_function_from_source`、`ast_parsers.py`、`typescript_parser.py`、接线 `tool_manager.py`→`tool_schema_generator.py`）；`card spark`（不运行就生成 schema = 安全即解析）；`card key`；`card warn`（易错点：`MockFunction` 在 **functions.py** 不在 ast_parsers.py；取**最后**一个 FunctionDef；TypeScript 工具创建**必须显式传 json_schema**；派生**只在创建时**做、且**已不在** pydantic 校验器里）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **派生流程 `flow`/`vflow`**：`source_code` → `ast.parse`（不跑）→ `_parse_function_from_source` → `MockFunction(__name__/__doc__/__signature__)` → `generate_schema` → JSON schema。
2. **import vs AST `cols`**：左＝`import + inspect`（会执行模块顶层代码 = RCE 风险）；右＝`ast.parse`（纯静态、不执行、安全）。
3. **`.cute` 萌图**：📄 用户代码 → 🔍 AST"只读不跑" → 📜 schema，气泡"我读你，但不跑你"。
4. **MockFunction 解剖 `table.t`/`cellgroup`**：`__name__`（名字）/`__doc__`（docstring）/`__signature__`（参数）——只够 `inspect.signature` 与 `parse(__doc__)` 用，`__call__` 抛 NotImplementedError。
5.（可选）**TypeScript 路径 `.note info`**：正则解析 `export function` + JSDoc；`source_type=typescript`；创建必须带 json_schema。

**必需代码（2–3，`codefile`）:**
- A) `derive_openai_json_schema`（简化，源 `functions.py`）：`mock = _parse_function_from_source(src, name)`；`return generate_schema(mock, name=name)`——一行点题"复用第 17 课"。
- B) `MockFunction` 类（源 `functions.py`）：`__init__` 设三属性；`__call__` `raise NotImplementedError("mock function cannot be called")`。
- C) `_parse_function_from_source` 要点（源 `functions.py`）：`ast.parse`；取 `functions[-1]`（最后一个 FunctionDef）；要求 docstring；用 `ast.literal_eval` 取默认值；未定义 BaseModel 用 `type(name,(BaseModel,),{})` 桩。

**必需折叠（3–4）:** 为什么用 AST 不用 import（import = 执行顶层 = RCE）；`MockFunction` 为什么能骗过 `inspect`（设了 `__signature__`）；为什么取**最后**一个函数 + 怎么给未知类型造桩；TypeScript 工具（正则、`source_type`、必须显式 schema）；接线在**创建时**（`tool_manager`→`tool_schema_generator`），不在 pydantic 校验器。

**自测题种子:** 注册自定义工具时 schema 怎么来的（AST 静态派生，不执行代码）；`MockFunction` 提供哪三样（`__name__/__doc__/__signature__`）；多函数源码取哪个（最后一个 FunctionDef）；TypeScript 工具能自动生成 schema 吗（不能，创建必须传 json_schema）。

**草图（真实类；en 镜像）:**

import vs AST（`cols`）：左红右绿，各一段说明 + `.note`。
`.note warn`（位置易错）：
```
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><span class="mono">MockFunction</span> 住在 <span class="mono">letta/functions/functions.py</span>，<strong>不在</strong> <span class="mono">ast_parsers.py</span>；派生只在<strong>创建工具时</strong>跑，<strong>不在</strong> pydantic 校验器里。</span></div>
```

---

## Task 3: 新增第 19 课「工具分发与执行（含 MCP）」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part5.py`(`LESSON_19`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `19-tool-dispatch-and-mcp.html`；标题 zh「工具分发与执行（含 MCP）」/ en「Tool dispatch & execution (incl. MCP)」；副标题 zh「ToolType · 工厂分发 · core/builtin/files/mcp/sandbox · MCP」/ en「ToolType; factory dispatch; core/builtin/files/mcp/sandbox; MCP」。

**学习目标:** 第 14 课里"执行工具"是一行带过的；这一课拆开它。每个 `Tool` 有个 `ToolType`（11 种）；`ToolExecutorFactory` 按类型映射到对应**执行器**；真正入口是 `ToolExecutionManager.execute_tool_async`。执行器各管一摊：`LettaCore`（core+记忆，进程内直跑）、`Builtin`（run_code/web_search）、`Files`、`ExternalMCP`（连外部 MCP server）、`Sandbox`（自定义/兜底 → 交第 20 课的沙箱）。再讲 MCP 集成（传输、每次开新连接）。

**亮点（`card spark`）:** **"一个方法调用，背后是好几种运行时。"** 从第 14 课循环的视角看，"调一个工具"是统一的一行；但底下，"运行这个工具"可以是**天差地别**的三件事：在进程内改核心记忆（`LettaCore`）、shell 出去在沙箱 venv 里跑（`Sandbox`）、或开一条网络连接到 MCP 服务器（`ExternalMCP`）。`ToolType` + 工厂就是藏起这种差异的**多态**。一个反直觉的真相：工厂的 `_executor_map` 只显式列了 5 个，**其余全部（自定义、多 agent、voice、两个弃用 external）兜底走 `SandboxToolExecutor`**——所以"自定义工具＝在沙箱里跑"是**默认**，不是特例。而所有执行器都返回同一种 `ToolExecutionResult`（正是第 16 课工具规则违规用的那个类型）。

**必需卡片:** `lead`；`card macro`（ToolType → 工厂 → 执行器 → execute → ToolExecutionResult，一张总图）；`card analogy`（前台分诊：同样是"看病"，按科室(ToolType)分到内科直接看(core)/外科手术室(sandbox)/转外院会诊(MCP)）；`card detail`（`tool_execution_manager.py::ToolExecutorFactory`/`ToolExecutionManager`、五个执行器、`schemas/enums.py::ToolType`、`mcp_client/types.py`）；`card spark`（一次调用多种运行时 + 自定义默认走沙箱 + 统一 ToolExecutionResult）；`card key`；`card warn`（易错点：工厂 `_executor_map` 只列 5 个、其余**兜底沙箱**；真正入口是 `ToolExecutionManager` 不是工厂本身；MCP 客户端在 `services/mcp/` **不在** `functions/mcp_client/`；`LETTA_VOICE_SLEEPTIME_CORE`/多 agent 也走沙箱）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **分发总图 `flow`**：`tool.tool_type` → `ToolExecutorFactory.get_executor` → 具体执行器 → `execute(...)` → `ToolExecutionResult`。
2. **ToolType → 执行器 `table.t`**（用研究表）：列＝ToolType / 执行器 / 类别 / 示例工具。突出"未映射→Sandbox 兜底"。
3. **MCP 执行 `vflow`**：MCP 工具（tag `mcp:<server>`）→ `ExternalMCPToolExecutor` → `MCPManager.execute_mcp_server_tool` → `connect_to_server → execute_tool → cleanup`（每次开新连接、**不走沙箱**）。
4. **`.cute` 萌图**：🏭 分拣工厂把工具按标签分到 🧠core / 🔧builtin / 📁files / 🔌mcp / 📦sandbox 几条传送带。
5. **MCP 传输 `cellgroup`**：`stdio` / `sse` / `streamable_http` 三种传输（`MCPServerType`）。

**必需代码（2–3，`codefile`）:**
- A) 工厂（简化，源 `tool_execution_manager.py`）：`_executor_map = {LETTA_CORE:LettaCore…, EXTERNAL_MCP:ExternalMCP…}`；`get_executor`：`cls._executor_map.get(tool_type, SandboxToolExecutor)`（点出兜底）。
- B) 入口（简化，源同文件）：`ToolExecutionManager.execute_tool_async`：建 executor → 计时 → `await executor.execute(...)` → 超 `return_char_limit` 截断 → 异常包 `ToolExecutionResult(status="error")`。
- C) MCP 执行（源 `mcp_tool_executor.py`）：取 `mcp:<server>` tag → `MCPManager().execute_mcp_server_tool(server, function_name, args, …)`。

**必需折叠（3–4）:** `tool_type` 怎么定（注册时按名字归类 + MCP 显式 + 默认 CUSTOM）；默认兜底 → `SandboxToolExecutor`（自定义默认沙箱）；MCP 集成（传输 stdio/sse/streamable_http、每次开新连接、不走沙箱、客户端在 `services/mcp/`）；内置工具（`run_code`/`web_search`…）+ Composio 执行器其实是**未接线的死代码**（`EXTERNAL_COMPOSIO` 弃用、兜底走沙箱）。

**自测题种子:** 谁是真正的执行入口（`ToolExecutionManager.execute_tool_async`，工厂只负责选执行器）；自定义工具默认用哪个执行器（`SandboxToolExecutor`，兜底）；MCP 工具执行走沙箱吗（不走，连外部 server）；记忆工具 `core_memory_append` 谁来跑（`LettaCoreToolExecutor`，进程内）。

**草图（真实类；en 镜像）:**

分发总图（`flow`）+ ToolType→执行器 `table.t`（研究表）。
`.note tip`（多态一句）：
```
<div class="note tip"><span class="ni">🧠</span><span class="nx">循环只说"调这个工具"，<strong>怎么跑</strong>由 <span class="mono">ToolType</span> + 工厂决定：进程内直跑 / 沙箱 / 连 MCP server——同一个 <span class="mono">execute</span> 接口，藏起三种运行时。</span></div>
```

---

## Task 4: 新增第 20 课「自定义工具沙箱与安全修复」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part5.py`(`LESSON_20`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `20-tool-sandbox-security.html`；标题 zh「自定义工具沙箱与安全修复」/ en「The tool sandbox & a security fix」；副标题 zh「local/E2B/Modal · 信任边界 · pickle vs JSON · marker+长度+MD5」/ en「local/E2B/Modal; the trust boundary; pickle vs JSON; marker+length+MD5」。

**学习目标（Part-5 收尾）:** 第 19 课说"自定义工具默认交沙箱"，这一课讲沙箱**怎么跑、为什么安全**。自定义工具是**不可信代码**，跑在沙箱里（本地 venv / E2B / Modal）。核心是一张**信任边界图**：`server→sandbox` 用 **pickle**（受信，传 `agent_state`），`sandbox→server` 用 **JSON**（不可信，**绝不 `pickle.loads`），并用 `marker+长度+MD5` 帧校验。PR #3343 正是把结果通道从 pickle 改成 JSON 的安全修复。把这张信任边界画清楚。

**亮点（`card spark`）:** **"你信任哪个方向，决定你用哪种序列化。"** `pickle.loads` 能在反序列化时执行任意代码——于是规则朴素到极致：**你可以 `pickle.loads` 你自己造的数据**（server→sandbox：服务端 pickle 自己的 `agent_state`、沙箱里 loads——权限是往**下**流进低信任的沙箱，没风险），但**绝不能 `pickle.loads` 跨过不可信边界回来的数据**（sandbox→server：沙箱刚跑完任意用户代码，它的输出只能当 **JSON** 读）。PR #3343 修的正是这个：旧代码对沙箱 stdout 直接 `pickle.loads`——一个**服务端 RCE**；修复把它换成 `json.loads`。而 `marker+长度+MD5` 帧是**完整性**层：用户工具能往 stdout 打任何东西（包括一个**假结果**），marker 圈出真 payload、MD5 抓篡改。**安全被化简成一个词：信任＝方向。** 这把整条工具链收口：第 18 课"不跑代码就读它" → 第 19 课"自定义→沙箱" → 第 20 课"连沙箱的输出也不可信"。

**必需卡片:** `lead`；`card macro`（沙箱三选一 + 双向信任边界 + 帧校验，一张总图）；`card analogy`（监狱探视窗：递进去的东西可以是原物(pickle 受信)，递出来的必须隔着玻璃验真、过安检(JSON+MD5)，绝不直接接管对方递出的"包裹"）；`card detail`（`tool_sandbox/base.py::generate_execution_script`/`_render_sandbox_code`、`local_sandbox.py`、`tool_parser_helper.py::parse_stdout_best_effort`、`SandboxType`、PR #3343 commit `1131535`）；`card spark`（信任＝方向：pickle 向下 OK / JSON 向上必须）；`card key`；`card warn`（易错点：`.j2` 模板 v0.16.8 **未被引用**、真实脚本由 `_render_sandbox_code` 拼；参数是**内联字面量**不是 pickle，只有 `agent_state` 走 pickle；marker+长度+MD5 帧**早于** #3343 就存在、#3343 只改了 payload 编码；`generate_execution_script` 的 docstring 已过时）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **信任边界总图 `cols`/`flow`**（本课核心）：左 server ——`pickle(agent_state)` 受信⬇️—— 右 sandbox；右 sandbox ——`JSON + marker+长度+MD5` 不可信⬆️—— 左 server。两方向标"信/不信"。
2. **stdout 帧布局 `table.t`/`cellgroup`**：`MARKER(16 字节, uuid5)` ‖ `LENGTH(4, '>I')` ‖ `MD5(32, hex)` ‖ `JSON_PAYLOAD(LENGTH)`，每段标作用。
3. **沙箱选择 `vflow`/`flow`**：tool.metadata `sandbox==modal`?→Modal；否则有 `e2b_api_key`?→E2B；否则→Local(venv)。
4. **`.cute` 萌图**：🔐 两个箭头：⬇️ pickle「自己人，放行」、⬆️ JSON「外人，过安检 MD5」。
5. **生成脚本 `vflow`**：`pickle.loads(agent_state)` → 内联参数 → 内联用户源码 → `_function_result = tool(...)` → JSON 打包 + 帧 → 写 stdout。

**必需代码（2–3，`codefile`）:**
- A) 生成的沙箱脚本骨架（简化，源 `base.py::_render_sandbox_code`）：`agent_state = pickle.loads(<bytes>)`；`x = <内联字面量>`；`<用户源码逐字>`；`_function_result = tool(x, agent_state=agent_state)`；`payload = json.dumps({...}).encode()`；`sys.stdout.buffer.write(MARKER + struct.pack('>I',len) + md5 + payload)`。
- B) 回读校验（简化，源 `local_sandbox.py::parse_out_function_results_markers` + `tool_parser_helper.py::parse_stdout_best_effort`）：找 marker → 切 length → 比 MD5（不符 `raise "output is corrupted"`）→ `json.loads` → `AgentState.model_validate`。
- C) PR #3343 前后对比：`- result = pickle.loads(text)`（旧·RCE）→ `+ result = json.loads(payload)`（新·安全）。

**必需折叠（3–4）:** 信任边界为什么这样切（pickle 能 RCE；向下传自己的数据 OK、向上收不可信数据只能 JSON）；marker+长度+MD5 防的是什么（用户工具往 stdout 打假结果/噪声）；PR #3343 到底改了什么（payload pickle→JSON；帧本就有）；本地 venv 细节（建/复用 venv、子进程、超时 180s）+ E2B/Modal 差异；（修正）`.j2` 模板未被引用、真实在 `_render_sandbox_code`。

**Capstone 收尾:** 作为第五部分终章，用 `cellgroup` 回扣全 Part：**17 函数+docstring→schema · 18 不跑就派生 · 19 按类型分发执行 · 20 沙箱隔离 + 信任边界**——一句话串成"**定义 → 派生 → 分发 → 隔离执行**"。并回指第 18 课（同样"不信任工具代码"）、第 19 课（自定义→沙箱的那次 handoff）。

**自测题种子:** server→sandbox 用什么序列化、为什么可以（pickle；自己造的数据、权限向下）；sandbox→server 为什么必须 JSON（沙箱跑了不可信代码，pickle.loads 会 RCE）；marker+长度+MD5 防什么（stdout 假结果/污染）；PR #3343 改了哪段（结果通道 pickle→JSON）；`.j2` 模板在 v0.16.8 用了吗（没有，真实在 `_render_sandbox_code`）。

**草图（真实类；en 镜像）:**

信任边界（`cols`）：左 server / 右 sandbox，中间两个反向箭头标 pickle(信)/JSON(不信)。
`.note warn`（核心安全点）：
```
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><strong>绝不 <span class="mono">pickle.loads</span> 沙箱回传的数据</strong>——它刚跑完任意用户代码。回程只 <span class="mono">json.loads</span>，再 <span class="mono">AgentState.model_validate</span>。这正是 PR #3343 的修复。</span></div>
```

---

## Task 5: 集成与合并（M5 收尾）

**Files:** `docs/superpowers/plans/2026-06-15-letta-visual-guide-roadmap.md` · （验证）全站

- [ ] 全量构建：`cd src && python build.py && python check_links.py && python check_html.py`，期望 `0 error / 0 warning`、链接全解析、index pill「共 20 课 · 5 个部分」。
- [ ] 导航链抽查：`16→17→18→19→20`，每课 `prev/next` 各 1，20 课 `next=../index.html`。
- [ ] roadmap 把 **M5** 标 `✅ 已完成并合并`（计划文档名填入）。
- [ ] 合并：`git checkout master && git merge --no-ff feat/m5-tools`；合并后再跑三件套确认绿。
- [ ] `git branch -d feat/m5-tools`；`git push origin master`。
- [ ] 报告 M5 完成，询问用户是否继续 M6（LLM Provider 抽象，21–23）。

---

## Self-Review（写完即查）

1. **Spec coverage**：spec 第五部分 17–20 ↔ Task 1–4 一一对应（函数→schema ✓、不执行就派生 ✓、分发+MCP ✓、沙箱+安全 ✓）。✅
2. **Placeholder scan**：无 TBD/TODO；每个 task 给 filename/学习目标/亮点/卡片/图/代码/折叠/自测题/草图（含真实 HTML 片段与已核实锚点）。✅
3. **Type/name consistency**：全程用 `generate_schema`/`derive_openai_json_schema`/`MockFunction`/`ToolType`/`ToolExecutorFactory`/`ToolExecutionManager`/`SandboxToolExecutor`/`generate_execution_script`/`parse_stdout_best_effort`/`SandboxType`/PR #3343，与"已核实锚点"一致。✅
4. **跨课一致**：18 复用 17 的 `generate_schema`；19 的 `ToolExecutionResult` 接第 16 课、Sandbox handoff 接 20；20 的"工具代码不可信"回扣 18；整 Part 收口"定义→派生→分发→隔离"。✅
