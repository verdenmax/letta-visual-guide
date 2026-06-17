# Letta 图解教程 · M6 第六部分（LLM Provider 抽象，3 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第六部分「LLM Provider 抽象」的 3 课（21 统一 provider 三方法契约 · 22 provider 怪癖的隔离 · 23 本地模型与 GBNF 受限解码）。延续前五部分的源码级深挖，讲清 Letta 怎么把**十几家 LLM 供应商**藏在一个统一接口后面、各家怪癖如何被隔离、以及没有原生 function calling 的本地模型怎么被"教会"调工具。

**Architecture:** 同前。内容放**新文件 `src/part6.py`**（`registry.py` 加 `import part6`）。新增一课 = 改 `shell.PAGES` + `shell.SUBTITLES` + `registry.CONTENT` + `part6.py` + (可选)`quizzes.QUIZZES`。

**Tech Stack:** Python 3.11+ 标准库；自包含 HTML/CSS。讲解对象 `/home/verden/course/letta`（v0.16.8）。

---

## 强化内容准则（沿用 M3–M5；务必逐条遵守）

1. **反长文（硬闸门）**：任何 `<p>` **≤ 200 中文字 / ≤ 120 英文词**。每段一个点；绝不连续 3 段以上纯文字。
2. **高频穿插视觉**：平均每 1–2 段一个"非纯文字"块。
3. **`.note`（每课 ≥ 3）** tip/info/warn；**`.cute`（每课 ≥ 1）**（provider 主题适合：🔌 适配器、🏭 工厂、🎭 面具/怪癖、🧩 拼图、📐 GBNF 模子…）。
4. **更详细**：每课 CJK **目标 4500+**（≥3000 硬底）；**图 ≥ 4 张/语言**；**折叠 3–4 个**；2–3 codefiles。靠更多小块实现，不是更长段落。
5. **全 6 卡**：`lead`/`macro`/`analogy`/`detail`/`spark`/`key`/`warn`（`card detail` 别漏）。

> 一句话：M6 要"像图文并茂的科普长文"，不是"论文式大段落"。

---

## 接线（首次用 part6.py）

`src/part6.py` 顶部写模块 docstring，依次 `LESSON_21 … LESSON_23`。`src/registry.py` 加 `import part6` 并在 `CONTENT` 追加 3 条。`shell.PAGES`/`SUBTITLES` 每课追加一行，`part_zh="第六部分 · LLM Provider 抽象"`、`part_en="Part 6 · The LLM provider abstraction"`。index pill 自动更新（到 23 课 · 6 个部分）。导航链：第 20 课 `next` 自动改成 21；23 课 `next=../index.html`。

## 验证（每个 task 收尾，DoD）
```
cd src && python build.py && python check_links.py && python check_html.py
```
期望：`0 error / 0 warning`，链接全解析，index pill「共 23 课 · 6 个部分」（到 23 课时）。

## 执行策略（两阶段 + 增量生成，防 cut-off / 超时）
每课分两次派发：**Phase A**＝scaffold + wiring + 填 zh；**Phase B**＝填 en 镜像 + 加 quiz。**关键：子代理必须"一点一点生成"——用 `<!--ZHMORE-->`/`<!--ENMORE-->` 占位符逐节小步 `edit`、每 ~2 节就 commit，绝不一次性写完整课；且禁止读大文件（part3/4/5、letta 仓库），所需内容全部内联在 prompt 里**（这条是上一里程碑踩坑后定的硬规矩）。各 task 仍跑**完整 spec + 质量双重审查**（claude-opus-4.8）。

---

## 已核实源码锚点（v0.16.8，3 个并行 research 子代理核实；引用只写"文件+符号"不写行号）

### 21（统一 provider 三方法契约）
- **工厂**：`letta/llm_api/llm_client.py::LLMClient.create(provider_type, put_inner_thoughts_first=True, actor=None) -> Optional[LLMClientBase]`——`@staticmethod`，对 `ProviderType` 用 `match/case` 分派（`anthropic→AnthropicClient`、`google_ai→GoogleAIClient`、`google_vertex→GoogleVertexClient`、`bedrock→BedrockClient`、`together/azure/xai/zai/groq/minimax/deepseek/baseten/fireworks/chatgpt_oauth→各自 Client`，`openrouter→OpenAIClient`），**默认 `case _ → OpenAIClient`**（`openai`/`ollama`/`vllm`/`lmstudio` 等都落这）。`LLMClient` 自身不是 client，只造 client；**分派字段是 `llm_config.model_endpoint_type`**（调用方取出来当 `provider_type` 传入；`ProviderType(str,Enum)` 所以字符串能匹配）。
- **抽象基类**：`letta/llm_api/llm_client_base.py::LLMClientBase`（方法标 `@abstractmethod`）。**核心"数据形状"三方法**（本课主线，是 8 个抽象方法的教学化简）：`build_request_data(agent_type, messages, llm_config, tools, …) -> dict`（**同步**，组装该 provider 的请求体）；`async request_async(request_data, llm_config) -> dict`（发请求拿原始响应）；`async convert_response_to_chat_completion(response_data, …) -> ChatCompletionResponse`（把各家响应**转成 OpenAI 形状**）。另有 `request`(同步)/`request_embeddings`/`stream_async`/`is_reasoning_model`/`handle_llm_error` 共 8 个抽象方法。
- **编排**：`LLMClientBase.send_llm_request`（**虽叫这名但是 async**）串起三步：`build_request_data → request_async → convert_response_to_chat_completion`，错误统一走 `handle_llm_error`。另一个 `send_llm_request_async` 接**已建好的 `request_data`**，只跑后两步。
- **OpenAI 形状＝通用中间格式**：`convert_response_to_chat_completion` 一律返回 `letta/schemas/openai/chat_completion_response.py::ChatCompletionResponse`（`id/choices/created/model/usage`，`object="chat.completion"`），不管哪家 provider；agent 循环只认这个形状。流式 `stream_async` 返回 OpenAI SDK 的 `AsyncStream[ChatCompletionChunk]`。
- **LLMConfig**：`letta/schemas/llm_config.py::LLMConfig`（**整类已弃用**，导向 `letta.schemas.model.ModelSettings`，但仍是工厂/基类消费的活抽象）。关键字段：`model`、**`model_endpoint_type`**(Literal，驱动分派)、`model_endpoint`、`context_window`、`put_inner_thoughts_in_kwargs`(默认 False)、`max_tokens`、`temperature`、`enable_reasoner`、`reasoning_effort`、`provider_category`(base/byok)、`handle`。挂在 `letta/schemas/agent.py::AgentState.llm_config`（弃用字段，回扣第 13 课）。
- **错误映射**：`LLMClientBase.handle_llm_error`（`@abstractmethod` 但带可用基类实现）：把 `httpx.RemoteProtocolError`→`LLMConnectionError`，兜底 `LLMError`。`OpenAIClient.handle_llm_error` 把 `context_length_exceeded`→`ContextWindowExceededError`（`letta/errors.py`，回扣第 12/14 课）。

### 22（provider 怪癖的隔离）
- **OpenAIClient 复用**：**8 个显式子类**（`AzureClient`/`BasetenClient`/`DeepseekClient`/`FireworksClient`/`GroqClient`/`TogetherClient`/`XAIClient`/`ZAIClient`，均 `(OpenAIClient)`）+ 直接复用（`openrouter` 显式、`case _` 默认）；约 **19/25** 的 `ProviderType` 最终落到 `OpenAIClient` 或其子类，仅 6 种不用（anthropic/bedrock/chatgpt_oauth/google_ai/google_vertex/minimax）。一个类服务多家的诀窍：`OpenAIClient._prepare_client_kwargs` 只把 `base_url` 设成 `llm_config.model_endpoint`——同一个 OpenAI SDK、不同 URL。**`AnthropicClient` 也是复用基类**（`BedrockClient`/`MiniMaxClient` 继承它）；`GoogleAIClient(GoogleVertexClient)`。
- **内心独白注入为工具参数（核心机制）**：注入 `letta/llm_api/helpers.py::add_inner_thoughts_to_functions`（**注意名字**，不是 `add_inner_thoughts_to_function_call`）——用 `OrderedDict` 把 `thinking` 加成**第一个** property、`required.insert(0, key)` 排**最前**（让模型先想后调）。键名 `letta/settings.py::INNER_THOUGHTS_KWARG = "thinking"`（**在 settings.py 不在 constants.py**），描述在 `letta/local_llm/constants.py`（`INNER_THOUGHTS_KWARG_DESCRIPTION` / `..._GO_FIRST`）。拆回 `helpers.py::unpack_inner_thoughts_from_kwargs`（从 tool_call 参数里 pop 出来塞进 message.content）。开关 `LLMConfig.put_inner_thoughts_in_kwargs`：**原生推理 provider→False**（Anthropic 3.7/4、OpenAI o1/o3/gpt-5、ZAI GLM…）、**普通工具调用→True**（模拟）。**Google 不一样：把 `thinking` 追加在最后**（`INNER_THOUGHTS_KWARG_VERTEX`），不是最前。
- **Anthropic 怪癖**（`anthropic_client.py`）：(a) **cache_control `{"type":"ephemeral"}`**——加在最后一个 tool、system 末块、messages 末消息末块（增量提示缓存）；(b) **extended thinking**——`data["thinking"]={"type":"adaptive"}` 或 `{"type":"enabled","budget_tokens":…}`，开 thinking 时 `temperature=1.0`；beta 头按需拼（`adaptive-thinking`/`interleaved-thinking`/`context-1m`…）；(c) **batch 真有接线**——`send_llm_batch_request_async → client.beta.messages.batches.create(...)`（唯一覆盖基类 `NotImplementedError` 的）；(d) 响应 `text/tool_use/thinking` 内容块 → OpenAI `tool_calls`/`reasoning_content` 形状。
- **Google**（`google_vertex_client.py`/`google_ai_client.py`）：tools 包成 `[{"functionDeclarations":[...]}]`；角色 `"model"→"assistant"`；`functionCall(.name/.args) → tool_calls`；`thinking` 追加在最后。
- **共性模式**：子类**只重写** `build_request_data` + `convert_response_to_chat_completion`（常 `super()` 后改 dict，如 `XAIClient` 去 grok-3-mini 的 penalty、`GroqClient` 强制 tool_choice="required"），怪癖被关在这两处；`send_llm_request_async` 之上的 agent 循环看到的永远是统一的 `ChatCompletionResponse`。

### 23（本地模型与 GBNF 受限解码 · **legacy 路径**）
- **⚠️ 框架定位（最重要）**：`local_llm` / `chat_completion_proxy` / GBNF 这条路在 v0.16.8 **是 legacy/次要路径**。现代本地后端（ollama/vllm/lmstudio）走 **OpenAI 兼容**的 `LLMClient.create → OpenAIClient`（默认 case，无专属 client）。GBNF 路只经由**旧** `letta/agent.py::Agent` 在 `LLMClient.create` 之后的**兜底**：`letta/llm_api/llm_api_tools.py::create` 的 `else:`(local) 分支调 `get_chat_completion`。讲本课要**明说这是 MemGPT 时代的经典老把戏 / 历史路径**。
- **编排器**：`letta/local_llm/chat_completion_proxy.py::get_chat_completion(model, messages, functions=None, …, wrapper=None, endpoint=None, endpoint_type=None, function_correction=True, …) -> ChatCompletionResponse`。流程：选 wrapper（默认 `ChatMLInnerMonologueWrapper`）→（wrapper 名含 `"grammar"` 才）**动态生成 GBNF**（`generate_grammar_and_documentation` + `grammars/gbnf_grammar_generator.py`，**不读静态 .gbnf 文件**）→ `wrapper.chat_completion_to_prompt(...)` 把函数 schema **塞进 prompt 文本** → 按 `endpoint_type` 调**裸 completion** 后端（llamacpp `/completion`、koboldcpp `/api/v1/generate`…），grammar 仅传给 4 个后端 → `wrapper.output_to_chat_completion_response(result)` 把文本 **解析回** `{function, params}` → `function_correction` 走 `patch_function`（本地心跳纠偏，回扣第 15 课）→ 包成 `ChatCompletionResponse`。
- **GBNF**：`letta/local_llm/grammars/json_func_calls_with_inner_thoughts.gbnf` 是**参考样例**（硬编码 8 个 MemGPT 基础工具）；运行时**动态生成**。每个分支强制 JSON `{"function": <名>, "params": {"inner_thoughts": <string>, …}}`，记忆类工具还要 `request_heartbeat` bool。GBNF（llama.cpp 的 GGML BNF）喂给采样器：每步只允许语法合法的 token → **输出必然是可解析的 JSON**，根治"忘了调函数/JSON 坏掉"。仅 `grammar_supported_backends = ["koboldcpp","llamacpp","webui","webui-legacy"]` 生效；其余（ollama/vllm/lmstudio）**丢掉 grammar**，靠 prompt 格式 + `json_parser.py::clean_json` 容错修复（非重采样重试）。另有通用 `grammars/json.gbnf`。
- **wrappers**：`letta/local_llm/llm_chat_completion_wrappers/`：基类 `wrapper_base.py::LLMChatCompletionWrapper`(ABC，`chat_completion_to_prompt` + `output_to_chat_completion_response`)；`chatml.py::ChatMLInnerMonologueWrapper`(默认 `DEFAULT_WRAPPER`)、`ChatMLOuterInnerMonologueWrapper`(noforce)、`llama3.py`、legacy `airoboros/dolphin/zephyr`、`configurable_wrapper.py`、`simple_summary_wrapper.py`。选择 `utils.py::get_available_wrappers()`（名含 `"grammar"`→建语法、`"noforce"`→inner_thoughts 放顶层）。"裸 completion 上模拟 function calling"：wrapper 把函数 schema 写进 prompt（`_compile_function_block`，含 `inner_thoughts` 描述），输出经 `clean_json` 解析回 `{function, args}`。
- **inner_thoughts/heartbeat**：`inner_thoughts` 是 grammar/prompt 强制的 JSON 字段，解析时从 params 提到 message.content。`letta/local_llm/function_parser.py::insert_heartbeat`（回扣第 15 课）+ `heartbeat_correction`/`patch_function`（issue #601；`tool_call` 分支有 `tools_calls` typo 小 bug）。

---

## Task 1: 新增第 21 课「统一 provider 三方法契约」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part6.py`(**新建** + `LESSON_21`) · `src/registry.py`(import part6 + CONTENT) · (可选)`src/quizzes.py`

**filename:** `21-provider-contract.html`；标题 zh「统一 provider 三方法契约」/ en「The unified provider contract」；副标题 zh「LLMClient.create 工厂 · 三方法 · OpenAI 形状作通用中间格式」/ en「the LLMClient.create factory; the 3 methods; the OpenAI shape as the universal format」。

**学习目标（Part-6 开篇）:** 讲清 Letta 怎么把**二十多家 LLM 供应商**藏在一个统一接口后面。① `llm_config.model_endpoint_type` 驱动 `LLMClient.create`（`match/case` → 具体 client 类，**默认 `OpenAIClient`**）。② `LLMClientBase` 的核心"数据形状"三方法：`build_request_data`（→ 该家请求 dict）、`request_async`（→ 原始响应 dict）、`convert_response_to_chat_completion`（→ **OpenAI 形状** `ChatCompletionResponse`）；`send_llm_request` 把三步串起来。③ **OpenAI ChatCompletion 形状是通用中间格式**——agent 循环（第 13–16 课）只认它，不管底下是哪家。为 22（怪癖隔离）、23（本地+GBNF）铺路。

**亮点（`card spark`）:** 这是**"适配器模式"开到极致**的一课。第 13–16 课那套执行循环，**从头到尾不知道自己在跟哪个 LLM 说话**——秘密只有一句：**选定一种数据形状（OpenAI 的 ChatCompletion）当"普通话"，让每个 provider client 把自己翻译成它**。于是 Anthropic 的内容块、Google 的 `functionCall`、本地模型吐的纯文本，最后都收敛成同一个 `ChatCompletionResponse`，循环读它就行。想加第 20 家供应商？写一个子类、实现三个方法，循环一行都不用改。更"投降式"的设计是那个**默认 `case _ → OpenAIClient`**：行业已经把 OpenAI 的形状当成事实标准，Letta 干脆把"OpenAI 兼容"设成**默认假设**。这也呼应第 14 课（循环消费 `usage.total_tokens` 与响应）、第 12/14 课（`handle_llm_error` 把上下文超限映射成 `ContextWindowExceededError`）。

**必需卡片:** `lead`；`card macro`（工厂 + 三方法 + OpenAI 形状，一张总图）；`card analogy`（联合国同传：各国代表（provider）说各自语言，统一翻译成一种工作语言（OpenAI 形状），台下（agent 循环）只听这一种）；`card detail`（落到 `llm_client.py::LLMClient.create`、`llm_client_base.py::LLMClientBase`、`schemas/openai/chat_completion_response.py::ChatCompletionResponse`、`schemas/llm_config.py::LLMConfig`）；`card spark`（适配器开到极致 + OpenAI 形状当普通话 + 默认 OpenAI 兼容）；`card key`；`card warn`（易错点：工厂分派的是 `model_endpoint_type`/`ProviderType`、**不是** `LLMConfig` 对象；默认 `case _ → OpenAIClient`；`convert_response_to_chat_completion` 是 **async**；"三方法"是 8 个抽象方法的化简；`LLMConfig` 整类已弃用但仍是活路径）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **provider 适配总图 `flow`**：agent 循环 → `LLMClient.create(model_endpoint_type)` → 具体 client → 三方法 → `ChatCompletionResponse` → 回循环。
2. **三方法契约 `vflow`**：`build_request_data`(组该家请求) → `request_async`(发请求拿原始响应) → `convert_response_to_chat_completion`(转 OpenAI 形状)；旁注 `send_llm_request` 串联 + `handle_llm_error` 兜错。
3. **endpoint_type → client `table.t`**（节选）：`anthropic→AnthropicClient`、`google_vertex→GoogleVertexClient`、`groq→GroqClient`、`openrouter→OpenAIClient`、`openai/ollama/vllm/…→OpenAIClient(默认)`。
4. **`.cute` 萌图**：🔌🔌🔌 一堆不同插头 → 🔄 转接 → 🟢 一个统一插座（OpenAI 形状），气泡"翻译成普通话"。
5. **LLMConfig 关键字段 `cellgroup`**：`model · model_endpoint_type · model_endpoint · context_window · put_inner_thoughts_in_kwargs · max_tokens · enable_reasoner`。

**必需代码（2–3，`codefile`）:**
- A) `LLMClient.create` 分派（简化，源 `llm_api/llm_client.py`）：`match provider_type: case anthropic: AnthropicClient(...); … case _: OpenAIClient(...)`。
- B) `LLMClientBase` 三方法 + 编排（简化，源 `llm_api/llm_client_base.py`）：三个 `@abstractmethod` 签名 + `send_llm_request`：`data=build_request_data(...); resp=await request_async(data); return await convert_response_to_chat_completion(resp)`（`except → handle_llm_error`）。
- C) 通用中间格式 `ChatCompletionResponse`（简化，源 `schemas/openai/chat_completion_response.py`）：`id/choices[Choice(message, finish_reason)]/usage/object="chat.completion"`。

**必需折叠（3–4）:** 为什么选 OpenAI 形状当"普通话"（行业事实标准、生态工具都按它来）；"三方法"其实是 8 个抽象方法（`request`/`request_embeddings`/`stream_async`/`is_reasoning_model`/`handle_llm_error`）；`send_llm_request` vs `send_llm_request_async`（一个跑全 3 步、一个接已建好的 request 只跑后 2 步）；`handle_llm_error` 把各家错误映射成统一异常（`ContextWindowExceededError` 回扣第 12/14 课）；`LLMConfig` 已弃用 → `ModelSettings`（为何仍讲它）。

**自测题种子:** 工厂按什么字段选 client（`model_endpoint_type`）；没列出的 provider（如 openai/ollama）用哪个 client（默认 `OpenAIClient`）；三方法里哪个产出"通用格式"（`convert_response_to_chat_completion → ChatCompletionResponse`）；agent 循环看得到 provider 差异吗（看不到，只看 OpenAI 形状）。

**草图（真实类；en 镜像；段落 ≤200 CJK；穿插 `.note`/`.cute`）:**

provider 适配总图（`flow`）：
```
<div class="flow">
  <div class="node"><div class="nt">agent 循环</div><div class="nd">只认 OpenAI 形状</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLMClient.create</div><div class="nd">按 model_endpoint_type 选 client</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">三方法</div><div class="nd">build / request / convert</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ChatCompletionResponse</div><div class="nd">通用中间格式</div></div>
</div>
```
`.note tip`（一句话）：
```
<div class="note tip"><span class="ni">🧠</span><span class="nx">一句话：<strong>选一种数据形状当"普通话"，让每个 provider 翻译成它</strong>。循环只学这一种语言，加多少家供应商都不用改。</span></div>
```

<!-- 后续 Task 2/3（lessons 22/23）+ Task 4（集成）将逐个补入。 -->

---

## Task 2: 新增第 22 课「provider 怪癖的隔离」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part6.py`(`LESSON_22`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `22-provider-quirks.html`；标题 zh「provider 怪癖的隔离」/ en「Isolating provider quirks」；副标题 zh「OpenAIClient 复用 · Anthropic cache/thinking/batch · 内心独白注入为参数」/ en「OpenAIClient reuse; Anthropic cache/thinking/batch; inner thoughts as a tool arg」。

**学习目标:** 第 21 课立了"统一契约"，这一课看**各家怪癖怎么被关进子类**。① `OpenAIClient` 被 8 个子类 + 默认 case 复用（诀窍：只换 `base_url`）；子类**只重写** `build_request_data` + `convert_response_to_chat_completion`（常 `super()` 后改 dict）。② 核心机制：**内心独白被注入成工具的第一个参数 `thinking`**（`add_inner_thoughts_to_functions`，强制排最前），响应时再 `unpack` 回 message.content。③ Anthropic 三大怪癖：`cache_control` 提示缓存、extended thinking、batch。④ Google 反例：`thinking` 追加在**最后**。

**亮点（`card spark`）:** 第 21 课那纸契约，**红利在这一课兑现**——每家 provider 的"怪脾气"都被**隔离在两个方法里**，循环之上一无所知。最妙的一个怪癖是"**把内心独白塞成工具参数**"：对没有原生推理的模型，Letta 强制每次工具调用都把一个 `thinking` 字符串排成**第一个参数**（于是模型"先想后调"），再在响应里把它**抽回**助手消息——硬是从一个"只会调函数"的模型里挤出了思维链。而 `put_inner_thoughts_in_kwargs` 会**自动翻转**：原生推理模型（o1/gpt-5/Claude-4）→ 关（用它们真的 thinking）；普通工具调用模型 → 开（模拟一个）。同一招 MemGPT 内心独白，在一动物园的 provider 之间活了下来——第 23 课的本地路径还会用语法再实现它一遍。

**必需卡片:** `lead`；`card macro`（OpenAIClient 复用 + 子类只改两方法 + 内心独白注入，一张总图）；`card analogy`（同一张脸戴不同面具：`OpenAIClient` 是脸，各 provider 子类是面具，只改 base_url / 个别字段）；`card detail`（落到 `openai_client.py::OpenAIClient`、`anthropic_client.py::AnthropicClient`、`helpers.py::add_inner_thoughts_to_functions`/`unpack_inner_thoughts_from_kwargs`、`settings.py::INNER_THOUGHTS_KWARG`）；`card spark`（契约红利 + 内心独白塞成第一个参数 + 开关自动翻转）；`card key`；`card warn`（易错点：注入函数叫 `add_inner_thoughts_to_functions`**不是** `_to_function_call`；`INNER_THOUGHTS_KWARG="thinking"` 在 **settings.py** 不在 constants.py；**Google 把 thinking 追加在最后**不是最前；`AnthropicClient` 也是复用基类（Bedrock/MiniMax 继承）；显式子类是 **8 个**不是 12）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **继承树 `flow`/`layers`**：`LLMClientBase` →（`OpenAIClient` ← Azure/Baseten/Deepseek/Fireworks/Groq/Together/XAI/ZAI）/（`AnthropicClient` ← Bedrock/MiniMax）/（`GoogleVertexClient` ← GoogleAI）。
2. **内心独白 注入/拆回 `vflow`**：注入 `thinking` 排最前 → 模型先写 thinking 再写参数 → 响应里 `unpack` 把 thinking 抽进 message.content。
3. **Anthropic 怪癖 `table.t`**：行＝cache_control（末 tool / system 末块 / messages 末块）/ extended thinking（adaptive 或 budget，temp=1）/ batch（`messages.batches.create`）/ 内容块→OpenAI 形状。
4. **`.cute` 萌图**：🎭🎭🎭 三张不同面具 + 同一张脸 🙂（`OpenAIClient`），气泡"只换 base_url / 几个字段"。
5. **开关自动翻转 `cellgroup`**：原生推理(o1/gpt-5/Claude-4) → `put_inner_thoughts_in_kwargs=False`；普通工具调用 → `True`（模拟）。

**必需代码（2–3，`codefile`）:**
- A) 一个子类只改两方法（简化，源 `xai_client.py` 或 `groq_client.py`）：`data = super().build_request_data(...)`；然后改/删个别字段（如 grok-3-mini 去 penalty / Groq 强制 `tool_choice="required"`）。
- B) `add_inner_thoughts_to_functions`（简化，源 `helpers.py`）：`OrderedDict`，`thinking` 放第一个 property，`required.insert(0, key)`。
- C) Anthropic `cache_control` 或 thinking（简化，源 `anthropic_client.py`）：`data["tools"][-1]["cache_control"]={"type":"ephemeral"}` / `data["thinking"]={"type":"enabled","budget_tokens":…}`。

**必需折叠（3–4）:** 内心独白为什么要排第一（先想后调）+ 怎么 unpack 回 content；`put_inner_thoughts_in_kwargs` 原生 vs 模拟（谁关谁开）；Anthropic 三处 cache_control + extended thinking + batch（唯一覆盖基类批量方法的）；Google 的反例（thinking 追加在最后、`functionCall→tool_calls`、`"model"→"assistant"`）；`OpenAIClient` 一类服务多家（只换 `base_url`，`AnthropicClient` 同样是复用基类）。

**自测题种子:** 子类一般重写哪两个方法（`build_request_data` + `convert_response_to_chat_completion`）；内心独白被放成工具的第几个参数（第一个，强制最前）；哪个开关决定"模拟还是用原生推理"（`put_inner_thoughts_in_kwargs`）；Google 的内心独白放最前还是最后（最后，反例）；`OpenAIClient` 服务多家靠改什么（`base_url`）。

**草图（真实类；en 镜像）:** 继承树 `flow` + 内心独白 `vflow` + Anthropic `table.t`。
`.note warn`（易错点）：
```
<div class="note warn"><span class="ni">⚠️</span><span class="nx">注入函数是 <span class="mono">add_inner_thoughts_to_functions</span>（复数 functions）；键名 <span class="mono">INNER_THOUGHTS_KWARG="thinking"</span> 在 <span class="mono">letta/settings.py</span>。<strong>Google 是反例</strong>：把 <span class="mono">thinking</span> 追加在<strong>最后</strong>，不是最前。</span></div>
```

---

## Task 3: 新增第 23 课「本地模型与 GBNF 受限解码」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part6.py`(`LESSON_23`) · `src/registry.py`(CONTENT) · (可选)`src/quizzes.py`

**filename:** `23-local-models-gbnf.html`；标题 zh「本地模型与 GBNF 受限解码」/ en「Local models & GBNF constrained decoding」；副标题 zh「chat_completion_proxy · GBNF 约束 JSON · wrapper · 经典老路径」/ en「chat_completion_proxy; GBNF-constrained JSON; wrappers; the classic legacy path」。

**学习目标（Part-6 收尾）:** 讲清没有原生 function calling 的本地模型怎么被"教会"调工具——**MemGPT 时代的经典老把戏**。① **必须明说这是 legacy 路径**：现代本地后端（ollama/vllm/lmstudio）走第 21 课的 OpenAI 兼容 `OpenAIClient`；GBNF 路只经旧 `Agent` 兜底。② `chat_completion_proxy.get_chat_completion` 流程：选 wrapper →（名含 grammar 才）**动态生成 GBNF** → wrapper 把函数 schema **塞进 prompt 文本** → 调裸 completion 后端（grammar 仅 llamacpp/koboldcpp/webui）→ 文本**解析回** `{function, params}` → 心跳纠偏。③ **GBNF** 约束采样器：每步只允许语法合法 token → 输出**必然是可解析 JSON**。

**亮点（`card spark`）:** 这是 MemGPT 最初的魔法，也是对"function calling"一次漂亮的重新理解。在 OpenAI 的工具 API 还没一统江湖之前，**怎么让一个只会"文本续写"的模型去调函数？**两步：其一，把函数 schema **当文本塞进 prompt**，要求模型输出 JSON；其二——更狠——用 **GBNF 语法约束解码器本身**，让模型在采样时**根本吐不出**任何非法 token，只能产出合法的 `{"function":…, "params":{"inner_thoughts":…,…}}`。受限解码把"**但愿**模型格式对"变成了"采样器**只能**挑语法合法的 token"——可解析性从概率变成了保证。这也正是它沦为 legacy 的原因：当每家 provider 都说起 OpenAI 的工具 API（第 21 课那个通用形状），兼容后端就不再需要这套语法戏法了。但它是 Letta"如何拿到可靠结构化输出"思路的**概念根**。呼应第 21 课（OpenAI 形状赢了）与第 15 课（inner_thoughts / 心跳）。

**必需卡片:** `lead`；`card macro`（proxy 流程 + GBNF 约束 + wrapper，一张总图，并点明 legacy）；`card analogy`（GBNF 像浇筑混凝土的**模子**：不管模型想吐什么，只有 JSON 形状的"浆"能从模子的缝里流出来）；`card detail`（落到 `local_llm/chat_completion_proxy.py::get_chat_completion`、`grammars/json_func_calls_with_inner_thoughts.gbnf`、`llm_chat_completion_wrappers/wrapper_base.py`、`function_parser.py::insert_heartbeat`）；`card spark`（裸 completion 上模拟 function calling + 受限解码把概率变保证 + 为何 legacy）；`card key`；`card warn`（易错点：**这是 legacy 路径**，现代本地用 `OpenAIClient`；GBNF 运行时**动态生成**，不读静态 .gbnf；grammar **只在 llamacpp/koboldcpp/webui** 生效，其余丢掉靠 `clean_json` 修复；默认 wrapper 是 `chatml` 不是 airoboros）。**外加 ≥3 `.note`、≥1 `.cute`。**

**必需图（≥4/语言）:**
1. **proxy 流程 `vflow`**：选 wrapper →（含 grammar）动态生成 GBNF → wrapper 把 schema 塞进 prompt → 调裸 completion(+grammar) → `output_to_chat_completion_response` 解析 → `patch_function` 心跳纠偏 → `ChatCompletionResponse`。
2. **GBNF 结构 `codefile`/`cellgroup`**：`root ::= Function`；`Function ::= SendMessage | …`；`…Params ::= "{" "inner_thoughts": string, … "}"`——强制 `{function, params{inner_thoughts,…}}`。
3. **grammar 支持 vs 不支持 `table.t`**：`llamacpp/koboldcpp/webui` → 传 grammar、受限解码；`ollama/vllm/lmstudio` → 丢 grammar → `json_parser.clean_json` 容错修复。
4. **`.cute` 萌图**：📐 GBNF 模子，左边一堆乱 token 想挤进来，只有 `{ }` JSON 形状的能通过，气泡"只放合法 JSON 出去"。
5. **legacy vs 现代 `.note info`**：现代本地（ollama/vllm/lmstudio）→ `LLMClient.create → OpenAIClient`；GBNF 路 → 旧 `Agent` 兜底。

**必需代码（2–3，`codefile`）:**
- A) `get_chat_completion` 流程骨架（简化，源 `chat_completion_proxy.py`）：选 wrapper → (含 grammar) 生成 → `prompt=wrapper.chat_completion_to_prompt(...)` → 按 endpoint_type 调后端(传 grammar) → `wrapper.output_to_chat_completion_response(result)`。
- B) GBNF 关键规则（源 `json_func_calls_with_inner_thoughts.gbnf`）：`root`/`Function`/`SendMessageParams`/`InnerThoughtsParam`（注意是参考样例、运行时动态生成）。
- C) wrapper 解析（简化，源 `chatml.py::output_to_chat_completion_response`）：`clean_json(raw)` → 取 `function`/`params` → 把 `inner_thoughts` 提进 content。

**必需折叠（3–4）:** GBNF 到底做什么（GGML BNF 在采样器层约束 token，可解析性从概率→保证）；为什么它是 legacy（OpenAI 兼容一统、`LLMClient.create` 无本地专属 client、`ProviderType` 已无 llamacpp/koboldcpp/webui）；grammar 只在 4 个后端 + 不支持时的 `clean_json` 修复链（非重采样）；wrappers 怎么"在裸 completion 上模拟 function calling"（schema 塞进 prompt、按模型族格式化、`first_message` 引导）；inner_thoughts / 心跳在本地路径（`function_parser.py::insert_heartbeat`，回扣第 15 课）。

**Capstone 收尾:** 第六部分终章，用 `cellgroup` 回扣全 Part：**21 统一契约 · 22 隔离怪癖 · 23 本地+GBNF**，一句话串成"**立契约 → 关怪癖 → 连没有工具 API 的模型也接得进来**"。回指第 21 课（OpenAI 形状当通用格式）、第 15 课（inner_thoughts/心跳）。最后过渡到第七部分（服务端与持久化）。

**自测题种子:** 这条 GBNF 路在 v0.16.8 是主力还是 legacy（legacy，现代用 OpenAIClient）；GBNF 怎么保证输出可解析（约束采样器、只允许语法合法 token）；grammar 在哪些后端生效（llamacpp/koboldcpp/webui）；没原生工具 API 的模型怎么"知道"有哪些函数（schema 被塞进 prompt 文本）；inner_thoughts 在本地怎么表示（grammar/prompt 强制的 JSON 字段）。

**草图（真实类；en 镜像）:** proxy `vflow` + GBNF `codefile` + grammar 支持 `table.t`。
`.note warn`（定位）：
```
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><strong>这是 legacy 路径</strong>：现代本地后端（ollama/vllm/lmstudio）走第 21 课的 OpenAI 兼容 <span class="mono">OpenAIClient</span>；GBNF 受限解码只在旧 <span class="mono">Agent</span> 兜底路径、且仅 <span class="mono">llamacpp/koboldcpp/webui</span> 生效。讲的是"它怎么work、为什么经典"，不是"现在默认这么跑"。</span></div>
```

---

## Task 4: 集成与合并（M6 收尾）

**Files:** `docs/superpowers/plans/2026-06-15-letta-visual-guide-roadmap.md` · （验证）全站

- [ ] 全量构建：`cd src && python build.py && python check_links.py && python check_html.py`，期望 `0 error / 0 warning`、链接全解析、index pill「共 23 课 · 6 个部分」。
- [ ] 导航链抽查：`20→21→22→23`，每课 `prev/next` 各 1，23 课 `next=../index.html`。
- [ ] roadmap 把 **M6** 标 `✅ 已完成并合并`（计划文档名填入）。
- [ ] 合并：`git checkout master && git merge --no-ff feat/m6-providers`；合并后再跑三件套确认绿。
- [ ] `git branch -d feat/m6-providers`；`git push origin master`。
- [ ] 报告 M6 完成，**自动继续 M7**（服务端与持久化，24–27）——用户已要求一路做完全部 M。

---

## Self-Review（写完即查）
1. **Spec coverage**：spec 第六部分 21–23 ↔ Task 1–3 一一对应（统一契约 ✓、怪癖隔离 ✓、本地+GBNF ✓）。✅
2. **Placeholder scan**：无 TBD/TODO；每个 task 给 filename/学习目标/亮点/卡片/图/代码/折叠/自测题/草图（含真实 HTML 片段与已核实锚点）。✅
3. **Type/name consistency**：全程用 `LLMClient.create`/`LLMClientBase`/`build_request_data`/`request_async`/`convert_response_to_chat_completion`/`send_llm_request`/`ChatCompletionResponse`/`OpenAIClient`/`AnthropicClient`/`add_inner_thoughts_to_functions`/`INNER_THOUGHTS_KWARG`/`get_chat_completion`/`json_func_calls_with_inner_thoughts.gbnf`，与"已核实锚点"一致。✅
4. **跨课一致**：22 兑现 21 的契约红利；23 的 inner_thoughts/心跳接第 15 课、OpenAI 形状赢了接第 21 课；21 的 handle_llm_error 接第 12/14 课；整 Part 收口"立契约→关怪癖→接入无工具 API 的模型"。✅
