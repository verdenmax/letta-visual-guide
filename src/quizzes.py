"""Per-lesson bilingual self-test (自测题). M0 ships the machinery; QUIZZES is empty.

Schema per lesson::

    "NN-file.html": {
        "mcq": [{"q": {"zh","en"}, "opts": [{"zh","en"}, ...], "answer": 0,
                 "why": {"zh","en"}}],
        "open": [{"zh","en"}],
    }

``render(fname, lang)`` returns the self-test HTML ('' when the lesson has no quiz).
Options are deterministically shuffled per question (same permutation for zh/en).
"""
import hashlib

_HEAD = {"zh": "🧪 自测 · 想一想为什么这么设计", "en": "🧪 Self-test - think about the design"}
_SEE = {"zh": "看答案与解析", "en": "Show answer & explanation"}
_CLICK = {"zh": "点击展开", "en": "click to expand"}
_ANS = {"zh": "答案：", "en": "Answer: "}
_SEP = {"zh": "。", "en": ". "}
_OPEN = {
    "zh": "💭 发散思考（没有标准答案，动手或动脑想想）",
    "en": "💭 Open questions (no single right answer - just think or try)",
}


def _shuffle(opts, answer, seed):
    """Deterministically permute opts (stable across builds); return
    (new_opts, new_answer_index) so the correct option lands in a varied slot."""
    order = sorted(
        range(len(opts)),
        key=lambda i: hashlib.md5(f"{seed}:{i}".encode("utf-8")).hexdigest(),
    )
    return [opts[i] for i in order], order.index(answer)


# Filename -> quiz dict. Empty in M0; lessons render without a self-test block.
QUIZZES = {
    "01-what-is-letta.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Letta 存在的根本理由是什么？",
                    "en": "What is the fundamental reason Letta exists?",
                },
                "opts": [
                    {"zh": "LLM 本身无状态，且上下文窗口有限",
                     "en": "LLMs are stateless and the context window is finite"},
                    {"zh": "LLM 太慢，需要缓存来加速",
                     "en": "LLMs are too slow and need a cache to speed up"},
                    {"zh": "LLM 不会调用任何工具",
                     "en": "LLMs cannot call any tools"},
                    {"zh": "LLM 只能理解英文",
                     "en": "LLMs only understand English"},
                ],
                "answer": 0,
                "why": {
                    "zh": "模型每次调用都是一张白纸（无状态），且能塞进的 token 有限，所以必须在模型之外补一层会自我管理的记忆——这正是 Letta 的使命。",
                    "en": "Each call is a blank slate (stateless) and only a finite number of tokens fit, so a self-managing memory layer must be added around the model - exactly Letta's mission.",
                },
            },
            {
                "q": {
                    "zh": "在 Letta 里，“一个 agent 的状态”具体是什么？",
                    "en": "In Letta, what exactly is 'an agent's state'?",
                },
                "opts": [
                    {"zh": "数据库里的一条 AgentState 记录",
                     "en": "One AgentState row in the database"},
                    {"zh": "一个一直驻留在内存里的进程",
                     "en": "A process that stays resident in memory forever"},
                    {"zh": "磁盘上的一个 JSON 配置文件",
                     "en": "A JSON config file on disk"},
                    {"zh": "模型权重里的一部分参数",
                     "en": "Part of the model weights"},
                ],
                "answer": 0,
                "why": {
                    "zh": "agent 的记忆块、消息、工具、模型配置都打包成一条 AgentState（letta/schemas/agent.py）。运行时取出→跑一步→写回，因此可水平扩展、关机也不丢记忆。",
                    "en": "Memory blocks, messages, tools and model config are packed into one AgentState (letta/schemas/agent.py). The runtime loads it, runs a step, saves it back - hence horizontal scaling and durable memory.",
                },
            },
            {
                "q": {
                    "zh": "“自我编辑记忆”在机制上意味着什么？",
                    "en": "Mechanically, what does 'self-editing memory' mean?",
                },
                "opts": [
                    {"zh": "agent 改写自己的系统提示（核心记忆被重新编译进第 0 条 system 消息）",
                     "en": "The agent rewrites its own system prompt (core memory is recompiled into message #0)"},
                    {"zh": "重新训练（微调）底层模型",
                     "en": "Re-training (fine-tuning) the underlying model"},
                    {"zh": "把整段对话写进一个日志文件",
                     "en": "Writing the whole conversation to a log file"},
                    {"zh": "直接清空上下文窗口",
                     "en": "Simply clearing the context window"},
                ],
                "answer": 0,
                "why": {
                    "zh": "core_memory_replace 改了记忆块后，Memory.compile() 会把它重新拼进系统提示，rebuild_system_prompt_async 重写第 0 条消息——等于 agent 在改写“自己是谁”。",
                    "en": "After core_memory_replace edits a block, Memory.compile() splices it back into the system prompt and rebuild_system_prompt_async rewrites message #0 - the agent literally rewrites 'who it is'.",
                },
            },
        ],
        "open": [
            {
                "zh": "用 MemGPT 的操作系统类比想一想：如果上下文是 RAM、外部记忆是磁盘，那么“换页”在 Letta 里对应哪些具体动作？什么时候该把内容从 RAM 换出到磁盘？",
                "en": "Using MemGPT's OS analogy: if context is RAM and external memory is disk, which concrete actions are the 'paging' in Letta, and when should content be paged out from RAM to disk?",
            },
        ],
    },
    "02-project-map.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Letta 后端的三层架构，从上到下（离请求最近到最底层）的顺序是？",
                    "en": "In Letta's 3-layer backend, what is the order from top (closest to the request) to bottom?",
                },
                "opts": [
                    {"zh": "REST 路由 -> services/managers -> ORM/数据库",
                     "en": "REST routes -> services/managers -> ORM/database"},
                    {"zh": "ORM/数据库 -> services -> REST 路由",
                     "en": "ORM/database -> services -> REST routes"},
                    {"zh": "services -> REST 路由 -> ORM/数据库",
                     "en": "services -> REST routes -> ORM/database"},
                    {"zh": "REST 路由 -> ORM/数据库 -> services",
                     "en": "REST routes -> ORM/database -> services"},
                ],
                "answer": 0,
                "why": {
                    "zh": "路由（server/rest_api/routers/v1/*）很薄，只解析 actor、收发 HTTP；它把活交给 services 的各 *Manager；manager 再经 ORM（SqlalchemyBase）落到数据库。",
                    "en": "Routes (server/rest_api/routers/v1/*) are thin: resolve the actor, send/receive HTTP. They hand work to the services' *Managers, which reach the database via the ORM (SqlalchemyBase).",
                },
            },
            {
                "q": {
                    "zh": "业务逻辑（开 DB 会话、查改数据、schema&lt;-&gt;orm 转换）主要落在哪一层？",
                    "en": "Which layer holds the business logic (open a DB session, query/modify, schema&lt;-&gt;orm conversion)?",
                },
                "opts": [
                    {"zh": "services 层的各 *Manager（如 AgentManager）",
                     "en": "The *Managers in the services layer (e.g. AgentManager)"},
                    {"zh": "REST 路由层",
                     "en": "The REST routes layer"},
                    {"zh": "数据库本身（SQLite / Postgres）",
                     "en": "The database itself (SQLite / Postgres)"},
                    {"zh": "前端调用方",
                     "en": "The front-end caller"},
                ],
                "answer": 0,
                "why": {
                    "zh": "路由薄、ORM 通用，真正的业务规则都压在 services 层的 *Manager 里——所以 REST、CLI、测试可以复用同一套方法。",
                    "en": "Routes are thin and the ORM is generic; the real business rules sit in the services layer's *Managers - so REST, CLI, and tests reuse the same methods.",
                },
            },
            {
                "q": {
                    "zh": "SqlalchemyBase.apply_access_predicate 的作用是什么？",
                    "en": "What does SqlalchemyBase.apply_access_predicate do?",
                },
                "opts": [
                    {"zh": "给任意查询自动加一道 WHERE，按组织（actor.organization_id）做行级隔离，只看本组织数据",
                     "en": "Auto-adds a WHERE to any query for row-level isolation by organization (actor.organization_id), so it only sees that org's rows"},
                    {"zh": "把 pydantic 模型转换成 ORM 模型",
                     "en": "Converts a pydantic model into an ORM model"},
                    {"zh": "在记忆变化时重新编译系统提示",
                     "en": "Recompiles the system prompt when memory changes"},
                    {"zh": "决定用 SQLite 还是 Postgres",
                     "en": "Decides whether to use SQLite or Postgres"},
                ],
                "answer": 0,
                "why": {
                    "zh": "它是多租户隔离的入口：默认按 actor 的 organization_id 加过滤，让每张表的查询都'只看自己组织'，而且是 secure by default——想绕都得特意绕。",
                    "en": "It's the entry point of multi-tenant isolation: by default it filters on the actor's organization_id so every table's query only sees its own org - secure by default, hard to bypass by accident.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设给 Letta 加一张新表（比如“笔记 notes”）。让它继承 SqlalchemyBase 后，它大致自动获得了哪些能力？为什么把这些做进一个基类、而不是每张表各写一遍，对多租户安全特别重要？",
                "en": "Suppose you add a new table to Letta (say 'notes'). Once it inherits SqlalchemyBase, what does it roughly get for free? Why does putting these into one base class - instead of re-writing them per table - matter so much for multi-tenant safety?",
            },
        ],
    },
    "03-message-lifecycle.html": {
        "mcq": [
            {
                "q": {
                    "zh": "路由 send_message 收到一条消息后，第一步做的是什么？",
                    "en": "When the send_message route receives a message, what's the first thing it does?",
                },
                "opts": [
                    {"zh": "解析 actor —— 确认是谁、属于哪个组织在操作",
                     "en": "Resolve the actor - figure out who, and which organization, is acting"},
                    {"zh": "立刻调用 LLM 生成回复",
                     "en": "Immediately call the LLM to generate a reply"},
                    {"zh": "把整段对话历史压缩成一条 summary",
                     "en": "Compress the entire history into one summary"},
                    {"zh": "训练（微调）底层模型",
                     "en": "Train (fine-tune) the underlying model"},
                ],
                "answer": 0,
                "why": {
                    "zh": "send_message 很薄：先 get_actor_or_default_async 解析 actor（决定多租户隔离），再按 id 载入 AgentState，然后交给 AgentLoop.load → step。调模型发生在更下层的 _step 里。",
                    "en": "send_message is thin: first get_actor_or_default_async resolves the actor (which drives multi-tenant isolation), then it loads the AgentState by id and hands off to AgentLoop.load → step. The model call happens lower down, inside _step.",
                },
            },
            {
                "q": {
                    "zh": "step 循环靠什么决定“要不要再来一轮”？",
                    "en": "What does the step loop use to decide 'run another round or not'?",
                },
                "opts": [
                    {"zh": "看这一步有没有调用工具：调了就继续，只产出普通消息就停",
                     "en": "Whether this step called a tool: called one -> continue; only a plain message -> stop"},
                    {"zh": "看用户有没有再发一条新消息",
                     "en": "Whether the user sent another message"},
                    {"zh": "看回复的字数有没有超过阈值",
                     "en": "Whether the reply length exceeded a threshold"},
                    {"zh": "随机决定，掷一次硬币",
                     "en": "Randomly, by a coin flip"},
                ],
                "answer": 0,
                "why": {
                    "zh": "_decide_continuation 的核心规则就一句：调了工具就继续、没调就停（源码注释：Did not call a tool? Loop ends. Called a tool? Loop continues.）。这比 MemGPT 靠模型输出 heartbeat 简单得多，且受 max_steps 上限保护。",
                    "en": "_decide_continuation's core rule is one line: called a tool -> continue, didn't -> stop (source comment: Did not call a tool? Loop ends. Called a tool? Loop continues.). Much simpler than MemGPT's heartbeat, and bounded by max_steps.",
                },
            },
            {
                "q": {
                    "zh": "两次 _step 之间，agent 的状态存在哪里？",
                    "en": "Between two _step rounds, where does the agent's state live?",
                },
                "opts": [
                    {"zh": "数据库里的 AgentState（运行时无状态：每次重建、用完即弃）",
                     "en": "The AgentState in the database (the runtime is stateless: rebuilt each time, discarded after use)"},
                    {"zh": "一直驻留在某台机器内存里的对象",
                     "en": "An object kept resident in one machine's memory"},
                    {"zh": "模型权重里",
                     "en": "Inside the model weights"},
                    {"zh": "前端浏览器的 localStorage 里",
                     "en": "In the browser's localStorage"},
                ],
                "answer": 0,
                "why": {
                    "zh": "运行时 agent 由 AgentLoop.load 从 AgentState 现造、跑完即弃；新消息与记忆改动都写回库。正因状态在数据不在进程，一条消息的多轮才能跨机器接力，服务端也才能水平扩展。",
                    "en": "The runtime agent is built fresh from AgentState by AgentLoop.load and discarded after the run; new messages and memory edits are written back. Because state lives in the data, not the process, a message's many rounds can hop across machines and the server can scale horizontally.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设一条消息触发了 3 轮 _step（改记忆 → 查资料 → 回话）。请按七步主轴把这 3 轮“摊开”：哪些步骤只发生一次、哪些重复了 3 次？如果第 2 轮所在的机器突然宕机，为什么换一台机器仍能接着把第 3 轮跑完？",
                "en": "Suppose one message triggers 3 _step rounds (edit memory → look up → reply). Lay these 3 rounds onto the seven-stop spine: which steps happen once, which repeat 3 times? If the machine running round 2 suddenly crashes, why can a different machine still finish round 3?",
            },
        ],
    },
    "04-agent-and-tools.html": {
        "mcq": [
            {
                "q": {
                    "zh": "当模型决定使用一个工具时，它实际上“产出”的是什么？",
                    "en": "When a model decides to use a tool, what does it actually 'emit'?",
                },
                "opts": [
                    {"zh": "一个结构化的 tool_call 请求（工具名 + JSON 参数），并不执行任何代码",
                     "en": "A structured tool_call request (tool name + JSON args) - it runs no code itself"},
                    {"zh": "它直接在自己的进程里运行那个函数并拿到返回值",
                     "en": "It runs the function in its own process and gets the return value"},
                    {"zh": "它把那个函数的源代码改写一遍",
                     "en": "It rewrites the function's source code"},
                    {"zh": "它当场训练出一个新工具",
                     "en": "It trains a brand-new tool on the spot"},
                ],
                "answer": 0,
                "why": {
                    "zh": "function calling 发生在消息层：模型只产出一个 tool_call（名字 + JSON 参数）。真正执行的是运行时（letta_agent_v3.py::_execute_tool → ToolExecutionManager.execute_tool_async，必要时进沙箱）——这也是安全边界：模型输出不可信，执行与否由你的代码裁决。",
                    "en": "Function calling happens at the message layer: the model only emits a tool_call (name + JSON args). The runtime actually executes it (letta_agent_v3.py::_execute_tool → ToolExecutionManager.execute_tool_async, sandboxed if needed) - the security boundary: model output is untrusted, your code decides whether to run it.",
                },
            },
            {
                "q": {
                    "zh": "Letta 为什么把“内心独白”做成每个工具 schema 里的一个参数（thinking）？",
                    "en": "Why does Letta make the 'inner monologue' an argument (thinking) inside every tool schema?",
                },
                "opts": [
                    {"zh": "用 schema 的最大公约数，跨所有支持 function calling 的 provider 统一强制“先推理后行动”，还能用 required + 排第一强制顺序",
                     "en": "Using the schema's greatest common denominator to force 'reason before act' uniformly across all function-calling providers, and enforce order via required + first position"},
                    {"zh": "为了让工具执行得更快",
                     "en": "To make tool execution run faster"},
                    {"zh": "因为模型权重里没有空间存放思考",
                     "en": "Because the model weights have no room to store thinking"},
                    {"zh": "为了减少 token 计费",
                     "en": "To reduce token billing"},
                ],
                "answer": 0,
                "why": {
                    "zh": "不是所有 provider 都有原生思考通道，格式还各不相同。add_inner_thoughts_to_functions 把 thinking 设成必填（required）且排第一（put_inner_thoughts_first），描述（..._GO_FIRST）再明令第一个生成——把“但愿它会想”的软约束变成“调用格式必须先写想法”的硬约束，且跨厂商通用。",
                    "en": "Not every provider has a native thinking channel, and formats differ. add_inner_thoughts_to_functions makes thinking required and first (put_inner_thoughts_first), and the description (..._GO_FIRST) orders it generated first - turning a soft 'hopefully it thinks' into a hard 'the call format must contain the thought first,' uniformly across vendors.",
                },
            },
            {
                "q": {
                    "zh": "ReAct 循环的正确顺序是哪一个？",
                    "en": "Which is the correct order of the ReAct loop?",
                },
                "opts": [
                    {"zh": "想（推理）→ 做（产出 tool_call）→ 看（观察工具结果）→ 再想……直到不再调工具",
                     "en": "Think (reason) → Act (emit tool_call) → Observe (see the tool result) → think again... until no tool is called"},
                    {"zh": "做 → 想 → 看 → 训练",
                     "en": "Act → Think → Observe → Train"},
                    {"zh": "看 → 回话 → 想 → 做",
                     "en": "Observe → Reply → Think → Act"},
                    {"zh": "一次性想完所有步骤，再一起执行",
                     "en": "Think through all steps at once, then execute them together"},
                ],
                "answer": 0,
                "why": {
                    "zh": "ReAct = Reasoning + Acting 交替：想→做→看→再想。模型发起调用时还没看到结果，必须把结果喂回去再调一次。Letta 用 _decide_continuation“调了工具就继续、否则停”驱动它——这正是第 3 课 step 循环的内核。",
                    "en": "ReAct = interleaved Reasoning + Acting: think→act→observe→think again. The model hasn't seen the result when it issues a call, so the result must be fed back and it's called again. Letta drives this with _decide_continuation ('called a tool → continue, else stop') - the very core of Lesson 3's step loop.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你要给 agent 加一个“删除文件”的工具。结合本课“模型只产出请求、运行时才执行”和“tool_call 不可信”，你会在执行前加哪些检查（权限、参数校验、沙箱、白名单）？为什么把这些放在运行时，而不是指望模型自律？",
                "en": "Suppose you add a 'delete file' tool to an agent. Given this lesson's 'the model only emits a request, the runtime executes' and 'tool_call is untrusted,' what checks would you add before execution (permissions, arg validation, sandbox, allow-list)? Why put these in the runtime instead of trusting the model to police itself?",
            },
        ],
    },
    "05-context-window.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Letta（以及 MemGPT）要解决的“上下文窗口”核心约束，最准确的描述是？",
                    "en": "What most accurately describes the core 'context window' constraint Letta (and MemGPT) address?",
                },
                "opts": [
                    {"zh": "它是一笔固定大小、且按 token 计费的预算，system + 核心记忆 + 工具 schema + 在窗消息共享它",
                     "en": "It's a fixed-size, per-token-billed budget shared by system + core memory + tool schemas + in-context messages"},
                    {"zh": "它只是对话历史的存储上限，与 system 和工具无关",
                     "en": "It's only a cap on conversation history, unrelated to system or tools"},
                    {"zh": "它是模型权重的大小限制",
                     "en": "It's a limit on the size of the model weights"},
                    {"zh": "它是磁盘上能存多少条消息的限制",
                     "en": "It's a limit on how many messages can be stored on disk"},
                ],
                "answer": 0,
                "why": {
                    "zh": "上下文窗口是一次调用能“看见”的 token 上限，而且 system、核心记忆、工具 schema 和在窗消息一起挤这条预算——真正留给历史的只是剩余。预算有限、尾巴只会增长，这正是记忆管理被逼出来的根本原因。",
                    "en": "The window is the token ceiling a single call can 'see,' and system, core memory, tool schemas, and in-context messages all squeeze into it — only the remainder is left for history. Finite budget plus an ever-growing tail is exactly why memory management is forced into existence.",
                },
            },
            {
                "q": {
                    "zh": "为什么 Letta 坚持“稳定前缀 + 变化尾巴”，正常步骤里不刷新系统提示？",
                    "en": "Why does Letta insist on 'stable prefix + changing tail,' not refreshing the system prompt during normal steps?",
                },
                "opts": [
                    {"zh": "前缀逐 token 不变才能命中 prefix cache、跳过昂贵的 prefill，省时省钱",
                     "en": "A token-for-token stable prefix hits the prefix cache and skips the costly prefill, saving time and money"},
                    {"zh": "因为系统提示不允许被修改",
                     "en": "Because the system prompt is not allowed to be modified"},
                    {"zh": "因为模型读不懂太长的系统提示",
                     "en": "Because the model can't understand a long system prompt"},
                    {"zh": "为了让 decode 阶段并行化",
                     "en": "To parallelize the decode phase"},
                ],
                "answer": 0,
                "why": {
                    "zh": "prefill 按输入 token 计费/耗时，且会把前缀的 KV 缓存起来。只要前缀逐 token 一致，第二次就能复用缓存、跳过这段 prefill；改动前缀（哪怕一个字）会让缓存作废、全量重算。所以 rebuild_system_prompt_async 只在记忆变化或压缩后才重写第 0 条消息。",
                    "en": "prefill is billed/timed by input tokens and caches the prefix's KV. As long as the prefix is token-for-token identical, the next request reuses the cache and skips that prefill; changing the prefix (even one character) invalidates it and forces a full recompute. That's why rebuild_system_prompt_async rewrites message 0 only on memory change or after compaction.",
                },
            },
            {
                "q": {
                    "zh": "“换个 1M 上下文的模型就不用管理记忆了”——这个说法的问题在哪？",
                    "en": "'Just switch to a 1M-context model and you won't need memory management' — what's wrong with this?",
                },
                "opts": [
                    {"zh": "长上下文只是放宽约束而非取消它：成本随 token 涨、prefill 延迟涨、还有 lost-in-the-middle",
                     "en": "Long context only loosens, not removes, the constraint: cost rises with tokens, prefill latency rises, plus lost-in-the-middle"},
                    {"zh": "1M 上下文的模型根本不存在",
                     "en": "1M-context models don't exist at all"},
                    {"zh": "长上下文模型不能调用工具",
                     "en": "Long-context models cannot call tools"},
                    {"zh": "长上下文会让模型忘记系统提示",
                     "en": "Long context makes the model forget the system prompt"},
                ],
                "answer": 0,
                "why": {
                    "zh": "更大的窗口抬高了上限，但三条代价仍在：按 token 计费导致成本线性上涨、prefill 读得越多越慢、研究反复发现放在超长上下文中间的信息容易被忽略（lost in the middle）。所以“放什么进窗口”的决策依然要做——Letta 用 ContextWindowOverview 量化、用 context_window×0.9 触发压缩来系统化地回答它。",
                    "en": "A bigger window raises the ceiling, but three costs remain: per-token billing makes cost rise linearly, more tokens make prefill slower, and research repeatedly finds mid-context info gets ignored (lost in the middle). So the 'what goes into the window' decision still must be made — Letta answers it systematically by quantifying with ContextWindowOverview and triggering compaction at context_window×0.9.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你的 agent 逼近了 context_window×0.9 的阈值。结合本课的 token 账本（ContextWindowOverview）和压缩闭环，你会优先换出/压缩哪一部分（旧消息？工具 schema？核心记忆？），又会尽量保住哪一部分前缀来吃 prefix cache？为什么？",
                "en": "Suppose your agent nears the context_window×0.9 threshold. Given this lesson's token ledger (ContextWindowOverview) and the compaction loop, which part would you swap out/compress first (old messages? tool schemas? core memory?), and which prefix would you preserve to keep hitting the prefix cache? Why?",
            },
        ],
    },
    "06-stateful-vs-stateless.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 Letta 里，一个 agent 物理上到底是什么？",
                    "en": "In Letta, what is an agent physically?",
                },
                "opts": [
                    {"zh": "数据库里一条可序列化的 AgentState 记录（记忆 / message_ids / system / tools / 配置）",
                     "en": "One serializable AgentState record in the database (memory / message_ids / system / tools / configs)"},
                    {"zh": "一个必须一直开着的常驻进程，在内存里记着对话",
                     "en": "A resident process that must stay running, holding the conversation in memory"},
                    {"zh": "一份微调过的模型权重",
                     "en": "A set of fine-tuned model weights"},
                    {"zh": "一条长期保持的网络连接（session）",
                     "en": "A long-lived network connection (session)"},
                ],
                "answer": 0,
                "why": {
                    "zh": "创建 agent 就是往库里写一行；读出来是一个 AgentState，装着重建它所需的全部状态。没有活对象、没有常驻进程——状态被完整外化成数据，运行时每个请求由 AgentLoop.load 现搭、跑完即弃。",
                    "en": "Creating an agent writes a row; read it back and you get an AgentState holding all state needed to rebuild it. There's no live object or resident process — state is fully externalized as data, and the runtime is rebuilt per request by AgentLoop.load and discarded.",
                },
            },
            {
                "q": {
                    "zh": "像 agent-1a2b… / block-9f8e… 这样的“带前缀 id”，前缀编码了什么、又为什么有用？",
                    "en": "In a prefixed id like agent-1a2b… / block-9f8e…, what does the prefix encode and why is it useful?",
                },
                "opts": [
                    {"zh": "前缀即实体类型：自证类型、好调试，配上 uuid4 不撞车且与机器无关（可移植）",
                     "en": "The prefix is the entity type: self-describing, easy to debug, plus a uuid4 means no collisions and machine-independence (portable)"},
                    {"zh": "前缀是创建时间戳，用来排序",
                     "en": "The prefix is the creation timestamp, used for sorting"},
                    {"zh": "前缀是分片所在的服务器编号",
                     "en": "The prefix is the shard's server number"},
                    {"zh": "前缀是自增主键，越小越早创建",
                     "en": "The prefix is an auto-increment key; smaller means created earlier"},
                ],
                "answer": 0,
                "why": {
                    "zh": "generate_id = f\"{__id_prefix__}-{uuid4()}\"，前缀由各 schema 的 __id_prefix__ 指定（如 AgentState→agent）。前缀让你一眼看出实体类型、便于排错；uuid4 几乎不撞车，且 id 不依赖自增主键或机器，导出别处仍有效，这是“agent 可搬运”的前提。",
                    "en": "generate_id = f\"{__id_prefix__}-{uuid4()}\", with the prefix set by each schema's __id_prefix__ (e.g. AgentState→agent). The prefix makes the entity type obvious and aids debugging; uuid4 avoids collisions, and the id depends on no auto-increment key or machine, so it stays valid when exported — the premise of portable agents.",
                },
            },
            {
                "q": {
                    "zh": "为什么同一个 Block / Agent 既有 letta/schemas/ 里的 pydantic 类，又有 letta/orm/ 里的 SQLAlchemy 类？",
                    "en": "Why does the same Block / Agent have both a pydantic class in letta/schemas/ and a SQLAlchemy class in letta/orm/?",
                },
                "opts": [
                    {"zh": "schema 是稳定的对外 API 契约，orm 是可为性能演进的存储；解耦后 DB 重构不惊动 API，manager 负责转换",
                     "en": "The schema is the stable external API contract, the orm is evolvable storage; decoupling lets DB refactors not disturb the API, with the manager converting between them"},
                    {"zh": "纯粹是历史遗留的重复代码，应该删掉一套",
                     "en": "It's just leftover duplicate code that should be deleted"},
                    {"zh": "一套给 Python 用、一套给 JavaScript 用",
                     "en": "One is for Python, the other for JavaScript"},
                    {"zh": "pydantic 用于训练，SQLAlchemy 用于推理",
                     "en": "pydantic is for training, SQLAlchemy is for inference"},
                ],
                "answer": 0,
                "why": {
                    "zh": "pydantic schema 定义对外承诺的形状（要稳定），SQLAlchemy orm 定义数据怎么落表（可为性能调整）。两者解耦：DB 怎么改都不漏到 API，API 加校验也不动表结构；manager 层用 to_pydantic_async 之类做转换，有的 pydantic 配置还以 JSON 整块存进一列（custom_columns.py）。",
                    "en": "The pydantic schema defines the externally promised shape (must stay stable); the SQLAlchemy orm defines how data lands in tables (tunable for performance). Decoupled, DB changes don't leak into the API and API validation doesn't touch tables; the manager converts (e.g. to_pydantic_async), and some pydantic configs are stored whole as JSON columns (custom_columns.py).",
                },
            },
        ],
        "open": [
            {
                "zh": "本课说“状态在数据里，算力在运行时里”。如果让你把一个调好的 Letta agent 复制一份、换掉底层模型再版本化入库，你会具体改 AgentState 的哪个字段、保留哪些字段不动？再想想：为什么同样的事在“把 agent 当常驻进程”的方案里很难做到？",
                "en": "This lesson says \"state lives in the data, compute in the runtime.\" To clone a tuned Letta agent, swap its underlying model, and version it into a repo, which AgentState field would you edit and which would you keep untouched? Then consider: why is the same thing hard when an agent is treated as a resident process?",
            },
        ],
    },
    "07-memory-tiers.html": {
        "mcq": [
            {
                "q": {
                    "zh": "core / recall / archival 三层里，哪一层始终在上下文窗口里？",
                    "en": "Of the three tiers core / recall / archival, which one is always in the context window?",
                },
                "opts": [
                    {"zh": "core memory（核心记忆）——始终在窗，且 agent 还能用工具自己改写",
                     "en": "core memory — always in-window, and the agent can even rewrite it with tools"},
                    {"zh": "recall memory——它存全部对话历史，所以一直在窗",
                     "en": "recall memory — it stores all conversation history, so it's always in-window"},
                    {"zh": "archival memory——长期向量库，所以一直在窗",
                     "en": "archival memory — it's the long-term vector store, so it's always in-window"},
                    {"zh": "三层都不在上下文里，每次都得现检索",
                     "en": "None of the three are in context; everything is retrieved fresh each time"},
                ],
                "answer": 0,
                "why": {
                    "zh": "只有 core 始终在上下文窗口里（对应 MemGPT 的 working context）；recall 与 archival 都在窗外，靠工具按需取回——recall 只有最近一段在窗，archival 全在窗外。",
                    "en": "Only core is always in the context window (MemGPT's working context); recall and archival sit out of window and are pulled back by tools — recall keeps only its latest slice in-window, and archival is entirely out of window.",
                },
            },
            {
                "q": {
                    "zh": "模型怎么知道“窗外还压着它看不见的内容”、又该去哪一层翻？",
                    "en": "How does the model know \"there's out-of-window content it can't see\" and which tier to page?",
                },
                "opts": [
                    {"zh": "系统每轮把一段 &lt;memory_metadata&gt; 库存清单拼进 system，告诉它 recall/archival 各有多少、有哪些 tag",
                     "en": "Each turn the system stitches a &lt;memory_metadata&gt; inventory into the prompt, telling it how much recall/archival hold and which tags exist"},
                    {"zh": "框架在每次回答前自动检索并把结果塞进提示，模型无需自己知道",
                     "en": "The framework auto-retrieves before every answer and stuffs results in, so the model needn't know itself"},
                    {"zh": "模型靠微调记住了所有历史，不需要任何提示",
                     "en": "The model memorized all history via fine-tuning and needs no hint"},
                    {"zh": "模型随机猜测，再看工具报错来判断",
                     "en": "The model guesses at random and infers from tool errors"},
                ],
                "answer": 0,
                "why": {
                    "zh": "compile_memory_metadata_block 产出的 &lt;memory_metadata&gt; 给的是计数与标签（不是内容本身），写进 system 让模型每轮都读到——于是它知道自己忘了什么、该去哪层翻。注意是 agent 自己发起检索，这和“框架自动 RAG”相反。",
                    "en": "The &lt;memory_metadata&gt; from compile_memory_metadata_block provides counts and tags (not the content itself), written into system so the model reads it every turn — so it knows what it forgot and which tier to page. Crucially the agent initiates the search itself, the opposite of \"framework auto-RAG.\"",
                },
            },
            {
                "q": {
                    "zh": "archival memory 靠什么把相关内容找回来？",
                    "en": "How does archival memory find relevant content?",
                },
                "opts": [
                    {"zh": "向量相似度（语义检索），用 archival_memory_search，措辞不同也能命中",
                     "en": "Vector similarity (semantic search) via archival_memory_search, hitting even when worded differently"},
                    {"zh": "精确关键词匹配，必须和原文一字不差",
                     "en": "Exact keyword matching, requiring a word-for-word match with the original"},
                    {"zh": "按写入时间顺序遍历，从最新到最旧",
                     "en": "Walking write-time order, newest to oldest"},
                    {"zh": "直接把全部内容塞进上下文窗口，不需要检索",
                     "en": "Dumping all content into the context window, no retrieval needed"},
                ],
                "answer": 0,
                "why": {
                    "zh": "archival 是长期向量库，archival_memory_search 按语义相似度检索——你问“API 重构的那个决定”，也能捞回当初用别的措辞记下的那条；这正是它和“精确关键词”的区别。",
                    "en": "archival is a long-term vector store, and archival_memory_search retrieves by semantic similarity — ask about \"that API-redesign decision\" and you recover the note even if it was worded differently; that's the difference from exact keyword matching.",
                },
            },
        ],
        "open": [
            {
                "zh": "随手挑三条信息：用户的名字、三个月前的一次闲聊、整份产品 FAQ 文档。分别该放进 core / recall / archival 哪一层？说出你的理由；再想想：如果故意放错层（比如把 FAQ 灌进 core），会触发本课提到的哪些代价（token 预算、字符上限、检索延迟）？",
                "en": "Pick three pieces of info: the user's name, a casual chat from three months ago, and a whole product FAQ doc. Which tier — core / recall / archival — should each go in, and why? Then consider: if you deliberately put one in the wrong tier (e.g., pour the FAQ into core), which costs from this lesson does it trigger (token budget, char cap, retrieval latency)?",
            },
        ],
    },
    "08-memory-blocks.html": {
        "mcq": [
            {
                "q": {
                    "zh": "core memory 的“最小单位”是什么？一个它有哪几个核心字段？",
                    "en": "What is core memory's smallest unit, and which core fields does one have?",
                },
                "opts": [
                    {"zh": "Block（记忆块）——核心字段是 label / value / limit / read_only",
                     "en": "A Block — its core fields are label / value / limit / read_only"},
                    {"zh": "字符——core memory 就是一长串字符，没有更小的结构",
                     "en": "The character — core memory is just one long string with no finer structure"},
                    {"zh": "Message（消息）——每条消息就是一个核心记忆单位",
                     "en": "A Message — each message is one unit of core memory"},
                    {"zh": "Passage（段落）——带向量的长期段落就是 core 的单位",
                     "en": "A Passage — the embedded long-term passage is core's unit"},
                ],
                "answer": 0,
                "why": {
                    "zh": "core memory 的原子是 Block（letta/schemas/block.py），核心字段四个：label（标签/寻址钥匙）、value（内容）、limit（字符上限）、read_only（能否被 agent 改）。Memory 是 Block 的集合，Memory.compile() 把它们渲染成 system 里的 &lt;memory_blocks&gt; 文本。Message / Passage 分别属于 recall / archival，不是 core 的单位。",
                    "en": "core memory's atom is the Block (letta/schemas/block.py), with four core fields: label (tag/addressing key), value (content), limit (char cap), read_only (whether the agent can edit it). Memory is the collection of Blocks, and Memory.compile() renders them into the &lt;memory_blocks&gt; text in system. Message / Passage belong to recall / archival, not core.",
                },
            },
            {
                "q": {
                    "zh": "agent A 和 agent B 都挂上了同一个 block-xyz。A 改了这张卡，会发生什么？",
                    "en": "Agents A and B both attach the same block-xyz. A edits the card — what happens?",
                },
                "opts": [
                    {"zh": "B 下一轮 Memory.compile() 就读到新值——因为两者引用的是同一行 block（blocks_agents 多对多）",
                     "en": "B reads the new value on its next Memory.compile() — both reference the same block row (blocks_agents many-to-many)"},
                    {"zh": "什么都不会变，B 有自己独立的副本，需要手动同步",
                     "en": "Nothing changes; B has its own copy and must sync manually"},
                    {"zh": "A 的改动会被拒绝，因为共享块自动变成 read_only",
                     "en": "A's edit is rejected because a shared block automatically becomes read_only"},
                    {"zh": "系统会复制一份给 B，从此两者各走各的",
                     "en": "The system copies one for B, and the two diverge from then on"},
                ],
                "answer": 0,
                "why": {
                    "zh": "块是可寻址、可共享的一等实体：共享靠 letta/orm/blocks_agents.py 的 BlocksAgents 关联表把 block.id 与 agent.id 多对多连接。两个 agent 引用的是“同一行”，所以一处改、处处变，无需任何同步步骤——这正是“共享记忆”的实现。",
                    "en": "A block is an addressable, shareable first-class entity: sharing uses the BlocksAgents join table (letta/orm/blocks_agents.py) linking block.id and agent.id many-to-many. The two agents reference the \"same row,\" so a change in one place shows everywhere with no sync step — that's how \"shared memory\" works.",
                },
            },
            {
                "q": {
                    "zh": "关于 read_only 与 limit，下面哪句是对的？",
                    "en": "Regarding read_only and limit, which statement is correct?",
                },
                "opts": [
                    {"zh": "read_only 是硬约束（core_memory_* 会抛错），limit 是软提示（只渲染进 metadata，写入路径不拦超限）",
                     "en": "read_only is a hard constraint (core_memory_* raise), while limit is a soft hint (only rendered into metadata; the write path doesn't block overflow)"},
                    {"zh": "两个都是硬约束：超 limit 会被直接拒绝，改 read_only 也会被拒绝",
                     "en": "Both are hard: exceeding limit is rejected, and editing a read_only block is rejected"},
                    {"zh": "两个都是软提示：只是写进提示给模型看，都不会真的拦",
                     "en": "Both are soft hints: just written into the prompt; neither truly blocks"},
                    {"zh": "read_only 是软提示，limit 才是硬性截断的那个",
                     "en": "read_only is the soft hint; limit is the one that hard-truncates"},
                ],
                "answer": 0,
                "why": {
                    "zh": "方向正好相反：core_memory_append / replace 改之前检查 block.read_only，是 True 就抛 READ_ONLY_BLOCK_EDIT_ERROR（core_tool_executor.py）——硬约束。而 limit 不在写入路径拦你：update_block_value 只校验“值是字符串”，limit 仅被渲染成 &lt;metadata&gt; 里的 chars_limit 提醒模型——软提示。要硬性限长得在应用层自己做。",
                    "en": "They point opposite ways: core_memory_append / replace check block.read_only before editing and raise READ_ONLY_BLOCK_EDIT_ERROR on True (core_tool_executor.py) — a hard constraint. But limit doesn't block the write path: update_block_value only checks \"value is a string,\" and limit is merely rendered as chars_limit in &lt;metadata&gt; to nudge the model — a soft hint. To hard-bound length, do it at the application layer.",
                },
            },
        ],
        "open": [
            {
                "zh": "假设你在搭一个客服 agent 团队：有一份全员必须遵守、谁都不能私自改的“退款政策”，还有每个 agent 各自记录的“当前对话进度”。你会怎么用 Block 的 label / read_only、共享（blocks_agents）和版本（BlockHistory）来设计这两类记忆？分别说说为什么。",
                "en": "Say you're building a team of support agents: there's a \"refund policy\" everyone must follow and nobody may privately edit, plus each agent's own \"current conversation progress.\" How would you use a Block's label / read_only, sharing (blocks_agents), and versioning (BlockHistory) to design these two kinds of memory? Explain your reasoning for each.",
            },
        ],
    },
    "09-self-editing-memory.html": {
        "mcq": [
            {
                "q": {
                    "zh": "“自我编辑记忆”本质上改写的是什么？",
                    "en": "What does \"self-editing memory\" fundamentally rewrite?",
                },
                "opts": [
                    {"zh": "持久化的第 0 条 system 消息——因为 core memory 就是 system 提示的一部分",
                     "en": "The persisted message #0 (the system message) — because core memory is part of the system prompt"},
                    {"zh": "一张独立的 user_facts 表，agent 用时再去查",
                     "en": "A separate user_facts table the agent queries on demand"},
                    {"zh": "一个常驻在进程内存里的全局变量",
                     "en": "A global variable kept resident in process memory"},
                    {"zh": "archival 向量库里的一条 passage",
                     "en": "One passage inside the archival vector store"},
                ],
                "answer": 0,
                "why": {
                    "zh": "core memory 不是“存在别处的记忆”——它每轮都被 Memory.compile() 拼进 system 提示，而 system 提示就是持久化的第 0 条消息（message_ids[0]）。所以 core_memory_append/replace 改块、触发 rebuild_system_prompt_async 后，最终落点是“原地重写第 0 条”。user_facts 表是外挂 RAG 的做法；archival passage 属于另一层。",
                    "en": "core memory isn't \"memory stored elsewhere\" — every turn Memory.compile() splices it into the system prompt, and the system prompt is the persisted message #0 (message_ids[0]). So core_memory_append/replace edit a block, trigger rebuild_system_prompt_async, and ultimately land on \"rewrite message #0 in place.\" A user_facts table is the bolted-on-RAG approach; an archival passage belongs to another tier.",
                },
            },
            {
                "q": {
                    "zh": "agent 改了一个块后，rebuild_system_prompt_async 怎么更新第 0 条 system 消息？",
                    "en": "After the agent edits a block, how does rebuild_system_prompt_async update message #0?",
                },
                "opts": [
                    {"zh": "用同一个 id 原地重写第 0 条（temp.id = curr.id），且只在记忆真的变了时才重建",
                     "en": "Rewrites #0 in place with the same id (temp.id = curr.id), and only rebuilds when memory actually changed"},
                    {"zh": "往历史末尾追加一条新的 system 消息（新 id）",
                     "en": "Appends a new system message (new id) to the end of history"},
                    {"zh": "立刻在当前这一轮把改动作为一条消息插进对话",
                     "en": "Immediately inserts the change as a message into the current turn"},
                    {"zh": "每一步都无条件重建，确保 system 永远最新",
                     "en": "Unconditionally rebuilds every step to keep system always fresh"},
                ],
                "answer": 0,
                "why": {
                    "zh": "rebuild_system_prompt_async 取 message_ids[0]，重新 compile 记忆；若新记忆已在当前 system 里且非强制，就直接返回（不重建）。要重建时，新消息沿用旧 id（temp.id = curr.id），再 update_message_by_id_async 原地更新——所以历史里始终只有一条 system。改动不是当场插进对话，而是沉淀进第 0 条、下一轮才被读到；也不是每步都重建（那会砸掉 prefix cache）。",
                    "en": "rebuild_system_prompt_async takes message_ids[0] and recompiles memory; if the new memory is already in the current system and not forced, it returns early (no rebuild). When it does rebuild, the new message reuses the old id (temp.id = curr.id) and update_message_by_id_async updates it in place — so history always holds exactly one system message. The change isn't inserted into the current turn; it settles into #0 and is read next turn; nor is it rebuilt every step (that would smash the prefix cache).",
                },
            },
            {
                "q": {
                    "zh": "为什么“正常对话步骤”故意不重建 system 提示？",
                    "en": "Why do \"normal conversation steps\" deliberately skip rebuilding the system prompt?",
                },
                "opts": [
                    {"zh": "为保住 prefix cache——稳定前缀命中 KV cache，只在记忆变化或压缩后才重建",
                     "en": "To preserve the prefix cache — a stable prefix hits the KV cache; rebuild only on a memory change or after compaction"},
                    {"zh": "因为重建会把对话历史一起清空",
                     "en": "Because rebuilding also wipes the conversation history"},
                    {"zh": "因为 core memory 是只读的，根本改不了",
                     "en": "Because core memory is read-only and can't be changed at all"},
                    {"zh": "因为模型其实不读 system 提示",
                     "en": "Because the model doesn't actually read the system prompt"},
                ],
                "answer": 0,
                "why": {
                    "zh": "system 提示是最靠前、最稳定的前缀，命中 KV cache 能省大量重复 prefill（第 5 课）。letta_agent_v3.py 的 _step 在步开头只刷新消息、跳过 system 重建，注释明写 “preserve prefix caching”；只有记忆真的变了（core_memory_*）或发生压缩后才重建 system（其中只有压缩那次带 force=True）。重建不会清空历史；core 默认可写；模型每轮都会读 system。",
                    "en": "The system prompt is the leading, stablest prefix; hitting the KV cache saves heavy repeated prefill (Lesson 5). _step in letta_agent_v3.py only refreshes messages at step start and skips the system rebuild, with the comment \"preserve prefix caching\"; it rebuilds the system message only on a real memory change (core_memory_*) or after compaction (only the compaction path passing force=True). Rebuilding doesn't wipe history; core is writable by default; the model reads system every turn.",
                },
            },
        ],
        "open": [
            {
                "zh": "你的 agent 反复忘记“用户已经付过款了”，每隔几轮就又问一次。结合本课的自编辑闭环：它应该在什么时机、用 append 还是 replace 改哪个块？为什么这条改动要落到第 0 条 system 消息上、而不是只回一句话？再想想：如果这是一张多 agent 共享的块，会有什么副作用？",
                "en": "Your agent keeps forgetting that \"the user already paid,\" re-asking every few turns. Using this lesson's self-editing loop: at what moment, with append or replace, and on which block should it write? Why must this edit land on message #0 rather than just a reply? And: if this were a block shared across multiple agents, what side effects might arise?",
            },
        ],
    },
    "10-archival-memory.html": {
        "mcq": [
            {
                "q": {
                    "zh": "archival_memory_search 是怎么把一条 passage “找回来”的？",
                    "en": "How does archival_memory_search actually \"find\" a passage?",
                },
                "opts": [
                    {"zh": "把查询也嵌成向量，按余弦距离取最近邻（cosine_distance 升序）——按“意思”找，不是字面匹配",
                     "en": "It embeds the query too, then takes nearest neighbors by cosine distance (cosine_distance ascending) — retrieval by meaning, not literal match"},
                    {"zh": "执行 SQL WHERE text = '…' 做精确字符串匹配",
                     "en": "Runs SQL WHERE text = '…' for an exact string match"},
                    {"zh": "按 created_at 倒序，永远只返回最近写入的几条",
                     "en": "Orders by created_at descending and always returns just the most recent rows"},
                    {"zh": "按关键词出现次数（BM25）排序，命中得越多越靠前",
                     "en": "Ranks by keyword frequency (BM25) — more keyword hits float to the top"},
                ],
                "answer": 0,
                "why": {
                    "zh": "search 工具先用同一个 embedding 模型把查询变成向量，再让数据库按向量距离排序取最近邻。SQLite 路径靠 sqlite_functions.py 注册的 cosine_distance（=1−相似度），Postgres 路径用 pgvector，两边都是 order_by(cosine_distance(...).asc())。所以它按语义相近度召回——“付款”能命中“已结清账单”，哪怕一个字都不重合；精确 WHERE、按时间、按关键词计数都不是它的检索方式。",
                    "en": "The search tool first turns the query into a vector with the same embedding model, then asks the database to sort by vector distance and take the nearest neighbors. The SQLite path uses cosine_distance (=1−similarity) registered in sqlite_functions.py; the Postgres path uses pgvector; both do order_by(cosine_distance(...).asc()). So it recalls by semantic closeness — \"payment\" can hit \"invoice already settled\" with zero shared words. Exact WHERE, recency, and keyword counting are not how it retrieves.",
                },
            },
            {
                "q": {
                    "zh": "“同一份代码，pgvector 跑生产、sqlite-vec 跑本机”这套双方言，魔法到底在哪一层？",
                    "en": "The \"same code, pgvector in prod / sqlite-vec on a laptop\" dual-dialect trick — at which layer does the magic live?",
                },
                "opts": [
                    {"zh": "向量列和距离算子由 settings.database_engine 在 ORM 层二选一；insert/search 两个工具和上层逻辑一字不改",
                     "en": "The vector column and distance operator are chosen by settings.database_engine in the ORM layer; the insert/search tools and upper logic don't change at all"},
                    {"zh": "每次换数据库都得把 archival 的两个工具重写一遍",
                     "en": "You must rewrite both archival tools every time you switch databases"},
                    {"zh": "archival 只能跑在 Postgres 上，本机其实是关掉的",
                     "en": "archival only runs on Postgres; on a laptop it's actually disabled"},
                    {"zh": "SQLite 把向量当 JSON 文本存，根本算不了相似度",
                     "en": "SQLite stores vectors as JSON text and can't compute similarity at all"},
                ],
                "answer": 0,
                "why": {
                    "zh": "在 orm/passage.py 里，BasePassage 用 settings.database_engine 决定 embedding 列：Postgres 用 Vector(MAX_EMBEDDING_DIM)，否则用 CommonVector；sqlalchemy_base.py 的排序也同样按引擎分支，但两边都是 cosine_distance(...).asc()。差异被关在 ORM/列类型这一层，archival_memory_insert/search 与调用它们的 agent 完全无感——所以 laptop→prod 不用改业务代码。换库不必重写工具；本机用 sqlite-vec 一样能算相似度。",
                    "en": "In orm/passage.py, BasePassage picks the embedding column by settings.database_engine: Vector(MAX_EMBEDDING_DIM) on Postgres, else CommonVector; sqlalchemy_base.py branches the ordering the same way, but both sides do cosine_distance(...).asc(). The difference is sealed inside the ORM/column-type layer, so archival_memory_insert/search and the agent calling them notice nothing — which is why laptop→prod needs no business-code changes. Switching DBs doesn't require rewriting the tools, and sqlite-vec computes similarity just fine.",
                },
            },
            {
                "q": {
                    "zh": "关于 archival 的“代价”和“语义”，下面哪句是对的？",
                    "en": "About archival's \"cost\" and \"semantics,\" which statement is true?",
                },
                "opts": [
                    {"zh": "search 是相似度召回（不保证精确命中），而且每次 insert / search 都要花一次 embedding 调用",
                     "en": "search is similarity recall (no guaranteed exact hit), and every insert / search costs one embedding call"},
                    {"zh": "search 保证一定返回你心里想要的那一条",
                     "en": "search is guaranteed to return exactly the row you had in mind"},
                    {"zh": "insert 不花钱，因为向量都是预先算好的",
                     "en": "insert is free because the vectors are all precomputed"},
                    {"zh": "archival 常驻上下文，所以每一轮都按 token 计费",
                     "en": "archival sits in the context window, so it's billed by token every turn"},
                ],
                "answer": 0,
                "why": {
                    "zh": "archival 是“按意思找”，结果是最相近的若干条，可能漏掉措辞差很远、或被更相似的噪音盖过的目标——所以不保证精确命中。写入要把文本嵌成向量、检索要把查询嵌成向量，两边都各是一次 embedding 调用，有真实开销。它也不像 core memory 常驻 system 提示，而是放在库里、用到才召回，所以不是每轮吃 token——这正是它便宜地“无限扩容”的原因。",
                    "en": "archival retrieves by meaning, returning the closest few — it can miss a target phrased very differently or drowned out by more-similar noise, so no exact-hit guarantee. Writing embeds the text into a vector; searching embeds the query — each is one embedding call with real cost. Unlike core memory, it doesn't live in the system prompt; it sits in the store and is recalled only when needed, so it isn't billed by token every turn — which is exactly why it scales \"infinitely\" cheaply.",
                },
            },
        ],
        "open": [
            {
                "zh": "你的客服 agent 要记住成百上千条历史工单。结合本课：哪些内容该用 archival_memory_insert 写进向量库（而不是塞进 core memory 块）？为什么 search 有时“明明存过却搜不出来”，你会怎么补救（想想 tags 和措辞）？再算一笔账：把每条用户消息都 insert 一次，代价和噪音会怎样？",
                "en": "Your support agent must remember hundreds of past tickets. Using this lesson: which content should go into the vector store via archival_memory_insert (rather than into a core-memory block)? Why does search sometimes \"miss a passage you definitely stored,\" and how would you fix it (think tags and phrasing)? Then do the math: if you insert every single user message, what happens to cost and noise?",
            },
        ],
    },
    "11-recall-memory.html": {
        "mcq": [
            {
                "q": {
                    "zh": "recall 和 archival 都在窗外、都能搜，它们最根本的区别是什么？",
                    "en": "recall and archival are both out-of-window and both searchable — what is their most fundamental difference?",
                },
                "opts": [
                    {"zh": "区别在“存什么 / 谁来写”：recall 是系统自动记的全量对话，archival 是 agent 主动挑着写的精选笔记",
                     "en": "It's “what's stored / who writes”: recall is the system's auto-logged full conversation, archival is the agent's actively-curated notes"},
                    {"zh": "recall 按字面关键词搜、archival 按语义搜——一个纯文本、一个纯向量",
                     "en": "recall searches by literal keyword and archival by semantics — one pure text, one pure vector"},
                    {"zh": "recall 在上下文窗口里、archival 在窗外",
                     "en": "recall is inside the context window, archival is outside it"},
                    {"zh": "recall 容量有限、会装满，archival 容量无限",
                     "en": "recall has limited capacity and fills up, archival is unlimited"},
                ],
                "answer": 0,
                "why": {
                    "zh": "两层都在窗外、都能搜，所以“在不在窗”不是区别。检索方式也都带语义：recall 的 conversation_search 是 hybrid（字面+语义），archival 是纯语义——所以“字面 vs 语义”是常见的记反。真正分野在“存什么 / 谁来写”：recall 由系统自动记下每一条原始消息（你不调任何工具），archival 由 agent 判断“值得长期留”才主动 insert 一条提炼后的笔记。一个被动全收，一个主动精选。",
                    "en": "Both are out-of-window and both searchable, so “in or out of context” isn't the difference. Both retrieve with semantics too: recall's conversation_search is hybrid (text+meaning), archival is pure semantic — so “literal vs semantic” is the common mix-up. The real split is “what's stored / who writes”: recall auto-logs every raw message (you call no tool), while archival is written only when the agent judges something worth keeping long-term and actively inserts a distilled note. One passively records all, one actively curates.",
                },
            },
            {
                "q": {
                    "zh": "用户三周前说“财年从 7 月开始”，今天 agent 用 conversation_search 查“季度起点”——一个原词都没对上，为什么还能把那条消息找回来？",
                    "en": "Three weeks ago the user said “fiscal year starts in July”; today the agent runs conversation_search for “quarter start” — not one original word matches, so why does the old message still come back?",
                },
                "opts": [
                    {"zh": "conversation_search 是 hybrid 检索（字面 + 语义），语义那一路能匹配意思相近、措辞不同的旧消息",
                     "en": "conversation_search is hybrid (text + semantic); the semantic path matches old messages that mean the same thing but are worded differently"},
                    {"zh": "它做的是精确字符串匹配，“季度”和“财年”被当作同义词写死在代码里",
                     "en": "It does exact string matching, with “quarter” and “fiscal year” hard-coded as synonyms"},
                    {"zh": "因为那条消息一直在上下文窗口里，根本不用搜",
                     "en": "Because that message has stayed in the context window all along, so no search is needed"},
                    {"zh": "因为 archival 早就自动存了一份，search 其实是从 archival 捞的",
                     "en": "Because archival auto-stored a copy long ago, and search actually pulls it from archival"},
                ],
                "answer": 0,
                "why": {
                    "zh": "conversation_search 的工具说明原话是“hybrid search (text + semantic similarity)”：它同时算字面和语义，所以措辞全变、意思相近的旧消息也能命中——这正是纯关键词匹配做不到的。那条消息其实早已滑出窗口（不在 message_ids 里），所以不是“一直在窗”；它也从没被 insert 进 archival（那是 recall 的活）。它依旧是库里的一行 Message，被 hybrid 按语义捞了回来。",
                    "en": "conversation_search's tool description literally says “hybrid search (text + semantic similarity)”: it computes text and meaning together, so a reworded-but-related old message still hits — exactly what pure keyword matching can't do. That message had already slid out of the window (not in message_ids), so it wasn't “still in-window”; nor was it ever inserted into archival (that's recall's job). It's still a Message row in the store, pulled back by hybrid on meaning.",
                },
            },
            {
                "q": {
                    "zh": "关于 message_ids 和“在窗 vs 全部历史”，下面哪句是对的？",
                    "en": "About message_ids and “in-window vs all history,” which statement is correct?",
                },
                "opts": [
                    {"zh": "message_ids 是一串指针，只圈出最近一段在窗消息；[0] 永远是系统消息，被移出 ≠ 被删除，旧消息可搜不可见",
                     "en": "message_ids is a list of pointers marking only the recent in-window slice; [0] is always the system message; dropped ≠ deleted, and old messages are searchable-not-visible"},
                    {"zh": "message_ids 直接存消息正文，trim 掉就等于把那几条 Message 从库里删了",
                     "en": "message_ids stores message bodies directly, so trimming deletes those Message rows from the store"},
                    {"zh": "message_ids 里第 0 条是最新的用户消息",
                     "en": "Index 0 of message_ids is the most recent user message"},
                    {"zh": "只要不在 message_ids 里，消息就永久丢失、再也找不回",
                     "en": "Any message not in message_ids is permanently lost and unrecoverable"},
                ],
                "answer": 0,
                "why": {
                    "zh": "message_ids（AgentState）是一串 id 指针，不是消息本身；第 0 条恒为系统消息（第 9 课“重建第 0 条”靠的就是它）。窗口瘦身用 trim_older_in_context_messages，只是从指针里去掉较旧的几条，真正的 Message 行由 MessageManager 一直留在库里——被移出窗口 ≠ 被删除。所以旧消息“可搜不可见”：看不见，但 conversation_search 一下就回来。",
                    "en": "message_ids (AgentState) is a list of id pointers, not the messages themselves; index 0 is always the system message (the basis for Lesson 9's “rebuild message #0”). Slimming uses trim_older_in_context_messages, which only drops older entries from the pointer list; the real Message rows stay in the store via MessageManager — dropped from the window ≠ deleted. So old messages are “searchable but not visible”: out of sight, but conversation_search brings them right back.",
                },
            },
        ],
        "open": [
            {
                "zh": "你在做一个长期陪伴 agent。结合本课想三件事：(1) 用户两个月前随口说的一句话今天突然有用——你指望 recall 还是 archival 把它找回来，为什么？(2) 如果消息只是裸文本、而不是带 type/time 的 JSON 事件，agent 在“分清谁说的、什么时候说的”上会丢掉什么？(3) 让 agent 频繁 conversation_search 翻历史，代价在哪（想想搜回来的消息要占回 token、hybrid 检索本身也有成本）？",
                "en": "You're building a long-term companion agent. Using this lesson, think through three things: (1) a line the user mentioned offhand two months ago suddenly matters today — do you count on recall or archival to retrieve it, and why? (2) If messages were raw text instead of JSON events with type/time, what would the agent lose in “telling who said it and when”? (3) If the agent runs conversation_search constantly to flip through history, where's the cost (think: fetched messages cost context tokens again, and hybrid search itself isn't free)?",
            },
        ],
    },
    "12-context-compaction.html": {
        "mcq": [
            {
                "q": {
                    "zh": "Letta 的压缩触发阈值是 context_window × 0.9，而不是等到 100% 才压。为什么要留这 10% 余量？",
                    "en": "Letta's compaction trigger threshold is context_window × 0.9, not waiting until 100%. Why keep that 10% margin?",
                },
                "opts": [
                    {"zh": "提前在 90% 主动压缩，留出余量，避免真撞上“prompt 太长”的报错；这也呼应第 5 课“度量 → 动手”的闭环",
                     "en": "Compact proactively at 90% to keep a buffer and avoid actually hitting a “prompt too long” error; this echoes Lesson 5's “measure → act” loop"},
                    {"zh": "因为模型只能数到窗口的 90%，剩下 10% 物理上无法使用",
                     "en": "Because the model can only count to 90% of the window; the last 10% is physically unusable"},
                    {"zh": "0.9 是随模型变化的，每个模型都有自己的阈值倍数",
                     "en": "0.9 varies per model; each model has its own threshold multiplier"},
                    {"zh": "留 10% 是为了给核心记忆压缩腾地方",
                     "en": "The 10% is reserved to make room for compacting core memory"},
                ],
                "answer": 0,
                "why": {
                    "zh": "get_compaction_trigger_threshold = int(context_window × SUMMARIZATION_TRIGGER_MULTIPLIER)，后者在 constants.py 固定为 0.9（不区分模型，force_proactive 目前也不改变结果）。在 90% 就触发，是为了在真正撞满、报“prompt 太长”之前主动腾空间。这正是第 5 课那条“度量 → 判定 → 压缩”闭环里“动手”的一步。核心记忆从不被压缩，所以最后一项是错的。",
                    "en": "get_compaction_trigger_threshold = int(context_window × SUMMARIZATION_TRIGGER_MULTIPLIER), the latter fixed at 0.9 in constants.py (model-agnostic; force_proactive doesn't change the result today). Triggering at 90% frees space before truly hitting the wall and raising “prompt too long.” That's the “act” step of Lesson 5's “measure → decide → compact” loop. Core memory is never compacted, so the last option is wrong.",
                },
            },
            {
                "q": {
                    "zh": "你把几万字塞进 persona/human 块，系统提示本身就快顶满窗口。这时 agent 不断压缩对话却仍然报错——发生了什么？",
                    "en": "You stuff tens of thousands of chars into persona/human blocks, so the system prompt alone nearly fills the window. The agent keeps compacting conversation yet still errors out — what happened?",
                },
                "opts": [
                    {"zh": "走了“系统提示溢出”特判：压缩只驱逐对话、绝不动 core；当第 0 条系统消息自己就 ≥ 窗口，抛 SystemPromptTokenExceededError",
                     "en": "It took the “system-prompt overflow” special case: compaction only evicts conversation and never touches core; when message[0] alone is ≥ the window, it raises SystemPromptTokenExceededError"},
                    {"zh": "压缩会把核心记忆也一起摘要掉，多压几次就好了",
                     "en": "Compaction summarizes core memory too; just compact a few more times and it's fine"},
                    {"zh": "agent 自动把超出的核心记忆挪进 archival，不会报错",
                     "en": "The agent auto-moves the overflowing core memory into archival, so it won't error"},
                    {"zh": "这是 recall 满了，清空对话历史即可",
                     "en": "This is recall being full; just clear the conversation history"},
                ],
                "answer": 0,
                "why": {
                    "zh": "summarizer 只总结对话消息，绝不碰核心记忆与系统提示（core 是 agent 的身份、必须始终在窗且逐字稳定）。compact_messages 压完会复核：若 compacted_messages[0]（系统消息）单独就 ≥ 窗口，说明元凶不是对话太长，而是 core/系统提示太大——于是 _check_for_system_prompt_overflow 抛 SystemPromptTokenExceededError，停止原因 context_window_overflow_in_system_prompt。正确做法是精简核心记忆（第 8 课的 limit）或换更大窗口，而不是再压对话。",
                    "en": "The summarizer only summarizes conversation messages and never touches core memory or the system prompt (core is the agent's identity — it must stay in-window and byte-stable). After compacting, compact_messages rechecks: if compacted_messages[0] (the system message) alone is ≥ the window, the culprit isn't a too-long conversation but a too-big core/system prompt — so _check_for_system_prompt_overflow raises SystemPromptTokenExceededError with stop reason context_window_overflow_in_system_prompt. The fix is to trim core memory (Lesson 8's limit) or use a bigger window, not to compact more conversation.",
                },
            },
            {
                "q": {
                    "zh": "压缩把前一小时的对话总结成了一段摘要。那些原始消息的命运是？",
                    "en": "Compaction summarized the past hour of conversation into one summary. What happens to those original messages?",
                },
                "opts": [
                    {"zh": "摘要是有损的，但原话没被删：原始 Message 仍留在 recall 里，可用 conversation_search 按 hybrid 捞回",
                     "en": "The summary is lossy, but the originals aren't deleted: the original Message rows stay in recall and can be fetched back by conversation_search (hybrid)"},
                    {"zh": "原始消息被永久删除，只剩摘要，细节再也找不回",
                     "en": "The original messages are permanently deleted; only the summary remains and details are gone forever"},
                    {"zh": "原始消息被原样保留在上下文窗口里，只是折叠起来",
                     "en": "The originals stay verbatim in the context window, just collapsed"},
                    {"zh": "原始消息被搬进核心记忆长期保存",
                     "en": "The originals are moved into core memory for long-term keeping"},
                ],
                "answer": 0,
                "why": {
                    "zh": "压缩是用“细节精度”换“窗口空间”的有损总结，不是无损归档：具体措辞、语气、边角细节从在窗视野里消失了。但它们没被删——原始 Message 行依旧躺在 recall 里（第 11 课），conversation_search 能按 hybrid 把它们捞回来。所以别把“摘要里没有”当成“模型还记得清”：摘要里没有，就意味着模型当下看不到、得主动去搜。原话退出的是窗口，不是数据库。",
                    "en": "Compaction is a lossy summary trading “detail precision” for “window space,” not a lossless archive: exact wording, tone, and edge details vanish from the in-window view. But they aren't deleted — the original Message rows still sit in recall (Lesson 11), and conversation_search can fetch them back by hybrid. So don't treat “not in the summary” as “the model still remembers it”: not in the summary means the model can't see it now and must actively search. The originals leave the window, not the database.",
                },
            },
        ],
        "open": [
            {
                "zh": "你在做一个要连聊几小时的客服 agent。结合本课想三件事：(1) 为什么“到 90% 就压缩”比“等撞满再处理”更稳？把它和第 5 课的“度量 → 动手”闭环接起来说。(2) 压缩是可见事件（compaction / SummaryMessage）——对用户体验和调试，这种“透明”比悄悄截断历史好在哪？(3) 既然摘要有损、原话又还在 recall，你会怎么设计“什么时候直接读摘要、什么时候该 conversation_search 翻原话”，才不至于既丢细节又浪费 token？",
                "en": "You're building a support agent that chats for hours. Using this lesson, think through three things: (1) why is “compact at 90%” steadier than “wait until the wall, then deal with it”? Connect it to Lesson 5's “measure → act” loop. (2) Compaction is a visible event (compaction / SummaryMessage) — for UX and debugging, how is this “transparency” better than silently truncating history? (3) Since the summary is lossy but the originals remain in recall, how would you design “when to just read the summary vs when to conversation_search the originals,” so you neither lose detail nor waste tokens?",
            },
        ],
    },
    "13-agent-state-and-loop.html": {
        "mcq": [
            {
                "q": {
                    "zh": "AgentLoop.load 是个工厂：同一张存档进来，它靠什么决定这次返回哪个 agent 引擎（V2 还是 V3）？",
                    "en": "AgentLoop.load is a factory: the same save comes in — what does it use to decide which agent engine (V2 or V3) to return this time?",
                },
                "opts": [
                    {"zh": "读存档里的 agent_state.agent_type 这一个字段当钥匙——整个分派只看它",
                     "en": "It reads the single field agent_state.agent_type as the key — the whole dispatch looks only at that"},
                    {"zh": "看当前上下文用了多少 token，超过阈值就改用 V3",
                     "en": "It looks at how many tokens the current context uses; above a threshold it switches to V3"},
                    {"zh": "随机挑一个，反正两代接口一样",
                     "en": "It picks one at random, since both generations share the same interface"},
                    {"zh": "看 actor（发起请求的用户）的权限等级来决定",
                     "en": "It decides based on the permission level of the actor (the requesting user)"},
                ],
                "answer": 0,
                "why": {
                    "zh": "AgentLoop.load(agent_state, actor) 只把 agent_state.agent_type 当分派键：letta_v1_agent / sleeptime_agent → LettaAgentV3，其余 → LettaAgentV2（额外开了 sleeptime + 组才走 SleeptimeMultiAgent）。token 用量是第 12 课压缩要管的事，与选引擎无关；actor 只用于权限与归属校验，不参与选类；两代虽都继承 BaseAgentV2、接口一致，但绝不是随机挑。",
                    "en": "AgentLoop.load(agent_state, actor) uses only agent_state.agent_type as the dispatch key: letta_v1_agent / sleeptime_agent → LettaAgentV3, everything else → LettaAgentV2 (sleeptime + group additionally goes to SleeptimeMultiAgent). Token usage is Lesson 12's compaction concern, unrelated to engine choice; actor is only for permission/ownership checks, not class selection; both generations subclass BaseAgentV2 and share an interface, but selection is never random.",
                },
            },
            {
                "q": {
                    "zh": "你想让一个新 agent 跑第三代实现 LettaAgentV3。该把 agent_type 设成哪个枚举值？",
                    "en": "You want a new agent to run the third-generation implementation LettaAgentV3. Which enum value should you set agent_type to?",
                },
                "opts": [
                    {"zh": "letta_v1_agent —— 它就是触发 V3 的值（也是新建 agent 的默认值）；注意“类叫 V3、枚举叫 v1”的错位",
                     "en": "letta_v1_agent — it's the value that triggers V3 (and the default for new agents); note the “class is V3, enum is v1” mismatch"},
                    {"zh": "letta_agent_v3 —— 跟类名对齐的那个",
                     "en": "letta_agent_v3 — the one aligned with the class name"},
                    {"zh": "letta_v3_agent",
                     "en": "letta_v3_agent"},
                    {"zh": "memgpt_v2_agent —— 数字最大的那个",
                     "en": "memgpt_v2_agent — the one with the biggest number"},
                ],
                "answer": 0,
                "why": {
                    "zh": "AgentType 里根本没有 letta_agent_v3 或 letta_v3_agent 这种值——照着类名去猜枚举必然落空。触发 LettaAgentV3 的是 letta_v1_agent（也是 CreateAgent.agent_type 的默认值）：“V3”说的是代码第三次重写循环，“v1”说的是 Letta v1 的设计（砍掉心跳与强制工具调用），V3 的代码实现的正是 v1 的设计。memgpt_v2_agent 走的是 V2。",
                    "en": "AgentType has no letta_agent_v3 or letta_v3_agent value at all — guessing the enum from the class name always fails. What triggers LettaAgentV3 is letta_v1_agent (also the default of CreateAgent.agent_type): “V3” means the third code rewrite of the loop, “v1” means the Letta v1 design (dropping heartbeats and forced tool calls), and the V3 code implements exactly that v1 design. memgpt_v2_agent runs V2.",
                },
            },
            {
                "q": {
                    "zh": "AgentState 里，哪个字段决定了“下一轮喂给模型的在窗对话消息有哪些”？",
                    "en": "In AgentState, which field determines “which in-window conversation messages are fed to the model next round”?",
                },
                "opts": [
                    {"zh": "message_ids —— 一串在窗消息的 id（指针）；正文留在 recall 表里，要用再捞",
                     "en": "message_ids — a list of in-window message ids (pointers); the text stays in the recall table, fetched when needed"},
                    {"zh": "blocks —— 核心记忆块里装着完整对话历史",
                     "en": "blocks — the core memory blocks hold the full conversation history"},
                    {"zh": "system —— 系统提示里内联了所有历史消息",
                     "en": "system — the system prompt inlines all historical messages"},
                    {"zh": "memory —— 它是专门存对话正文的字段",
                     "en": "memory — it's the field dedicated to storing conversation text"},
                ],
                "answer": 0,
                "why": {
                    "zh": "message_ids 是“在窗消息的 id 列表”（第 11 课），存的是指针而非正文——这正体现存档“只放指针 + 配置、不放海量正文”的取舍，真正的消息正文在 recall 数据库表里。blocks 是核心记忆块（人设 / 用户 / 自定义，第 8 课），不是对话历史；system 是系统提示；memory 只是 blocks 的废弃别名。",
                    "en": "message_ids is the “list of in-window message ids” (Lesson 11), storing pointers not text — embodying the save's trade-off of “pointers + config, not bulk text,” with the actual message text in the recall DB table. blocks are core memory blocks (persona / human / custom, Lesson 8), not conversation history; system is the system prompt; memory is merely the deprecated alias of blocks.",
                },
            },
            {
                "q": {
                    "zh": "把 AgentState 叫做“存档”，是怎么呼应第 6 课“有状态 vs 无状态”的？",
                    "en": "Calling AgentState a “save file” — how does that echo Lesson 6's “stateful vs stateless”?",
                },
                "opts": [
                    {"zh": "服务器自己不留记忆：每个请求都把整张存档从数据库水合出来、跑一轮、再写回——所以同一 agent 能在任意进程 / 机器上“读档续玩”",
                     "en": "The server keeps no memory of its own: every request hydrates the whole save from the DB, runs a round, and writes it back — so the same agent can “load and resume” on any process / machine"},
                    {"zh": "服务器把每个 agent 的状态常驻在内存对象里，所以一换机器就会丢",
                     "en": "The server keeps each agent's state in a long-lived in-memory object, so switching machines loses it"},
                    {"zh": "LLM 自己有状态、会记住上一轮，所以根本不需要存档",
                     "en": "The LLM is itself stateful and remembers the last round, so no save is needed at all"},
                    {"zh": "存档只是个缓存，真相一直在模型权重里",
                     "en": "The save is just a cache; the truth always lives in the model weights"},
                ],
                "answer": 0,
                "why": {
                    "zh": "第 6 课的要点：LLM 无状态，Letta 把 agent 的状态外化成一张可序列化、可落库的存档。每个请求的固定三拍是“水合 → 跑 → 写回”：现从 ORM 行读出 AgentState，跑完把新消息 / 改动写回库。引擎对象每轮现装现扔、自己不留状态，状态全在存档里——所以同一 agent 能在任意进程 / 机器续跑。常驻内存、“LLM 自己记得”、“真相在权重里”都与这套无状态架构相悖。",
                    "en": "Lesson 6's point: the LLM is stateless, so Letta externalizes the agent's state into a serializable, persistable save file. Every request's fixed three-beat is “hydrate → run → write back”: read AgentState fresh from the ORM row, then persist new messages / edits back. The engine object is assembled and discarded each round and keeps no state — all state lives in the save — so the same agent resumes on any process / machine. Long-lived memory, “the LLM remembers,” and “truth in the weights” all contradict this stateless architecture.",
                },
            },
        ],
        "open": [
            {
                "zh": "用“游戏存档 + 工厂选引擎”这两个比喻，把第 13 课串成一个完整故事，并想三件事：(1) 为什么要让一个工厂（AgentLoop.load）按 agent_type 选实现，而不是在每个调用点写 if/else？把它和“将来新增一种 agent”连起来说。(2) 类名是 LettaAgentV3、枚举名却是 letta_v1_agent——这种“名字记录历史、行为写在代码里”的错位，会给读代码的人埋下哪些坑？你会怎么避免被带偏？(3) 既然引擎每个请求现装现扔、状态全在存档里，这对“同一 agent 能在任意机器续跑”意味着什么？再把它接回第 6 课的无状态设计。",
                "en": "Using the two metaphors “game save file + factory picks the engine,” weave Lesson 13 into one coherent story, and think through three things: (1) why have a factory (AgentLoop.load) pick the implementation by agent_type instead of writing if/else at every call site? Connect it to “adding a new agent kind later.” (2) The class is named LettaAgentV3 yet the enum is letta_v1_agent — what traps does this “name records history, behavior lives in code” mismatch set for readers, and how would you avoid being misled? (3) Since the engine is assembled and discarded each request with all state in the save, what does that mean for “the same agent resuming on any machine”? Tie it back to Lesson 6's stateless design.",
            },
        ],
    },
    "14-v3-step-loop.html": {
        "mcq": [
            {
                "q": {
                    "zh": "V3 循环里，一次 _step（letta_agent_v3.py::_step）到底做哪三件事？",
                    "en": "In the V3 loop, what three things does a single _step (letta_agent_v3.py::_step) actually do?",
                },
                "opts": [
                    {"zh": "调一次 LLM、执行工具、把结果落库（拿有效工具 → 刷新消息 → 调模型 → _handle_ai_response → _checkpoint_messages → yield）",
                     "en": "One LLM call, tool execution, and persisting the result (get valid tools → refresh messages → call the model → _handle_ai_response → _checkpoint_messages → yield)"},
                    {"zh": "只调一次 LLM，工具执行和落库都甩给外层 step() 去做",
                     "en": "Only one LLM call; it hands tool execution and persistence off to the outer step()"},
                    {"zh": "把整个 50 步循环一次跑完，再一次性返回所有消息",
                     "en": "Run the whole 50-step loop in one go, then return all messages at once"},
                    {"zh": "重建系统提示、压缩历史、再把整张存档写回数据库",
                     "en": "Rebuild the system prompt, compact history, then write the whole save back to the DB"},
                ],
                "answer": 0,
                "why": {
                    "zh": "_step 的源码定位就是“一次 LLM 调用与工具执行”，它是个异步生成器：拿有效工具并问要不要强制 → _refresh_messages（不重建系统提示，保住 prefix cache）→ invoke_llm（外裹“撑爆就压缩重试”）→ _handle_ai_response 校验并执行工具、算出续步三元组 → _checkpoint_messages 落库（“持久化要在流式之前”）→ yield。工具执行与落库都在 _step 内部，不是甩给 step()；跑满 50 步是外层 step() 的 for 循环干的，不是一次 _step；重建系统提示只在压缩 / 重置后才发生，不是每个 _step 的常规动作。",
                    "en": "The source pins _step as “one LLM call and tool execution” — an async generator: get valid tools and check whether to force a call → _refresh_messages (no system-prompt rebuild, preserving the prefix cache) → invoke_llm (wrapped in “overflow → compact → retry”) → _handle_ai_response validates and executes tools and computes the continuation triple → _checkpoint_messages persists (“persistence needs to happen before streaming”) → yield. Tool execution and persistence both live inside _step, not handed to step(); running all 50 steps is the outer step()'s for loop, not one _step; rebuilding the system prompt only happens after compaction / reset, not on every _step.",
                },
            },
            {
                "q": {
                    "zh": "_decide_continuation 怎么判断“还要不要再走一步”？它最核心的判据是什么？",
                    "en": "How does _decide_continuation decide “take one more step or not”? What is its core criterion?",
                },
                "opts": [
                    {"zh": "只看模型这一轮有没有调工具：调了 → 继续；没调 → 结束（end_turn）。再叠加几条硬覆盖",
                     "en": "It only looks at whether the model called a tool this round: called → continue; didn't → end (end_turn). Plus a few hard overrides"},
                    {"zh": "看模型有没有在参数里举手要“心跳”（request_heartbeat）",
                     "en": "It checks whether the model raised its hand for a “heartbeat” in the parameters (request_heartbeat)"},
                    {"zh": "看模型生成的文本里有没有出现“继续”这个词",
                     "en": "It scans the model's generated text for the word “continue”"},
                    {"zh": "看这一轮用了多少 token，超过一半预算就停",
                     "en": "It watches how many tokens this round used and stops past half the budget"},
                ],
                "answer": 0,
                "why": {
                    "zh": "_decide_continuation 的文档字符串把规则写成两条：没调工具 → 循环结束；调了工具 → 循环继续。它不看模型“想不想继续”，只认“有没有发起工具调用”这个客观信号——因为工具调用是两段式的，执行完得把结果喂回模型，所以必须再转一圈。硬覆盖：没调但还有 required_before_exit 没调 → 继续；终止工具 → 停 tool_rule；第 50 步 → 停 max_steps。靠 request_heartbeat 续步是上一代 V2 的做法，正是 V3 砍掉的“心跳”（第 15 课）；扫文本关键词、看 token 用量都不是它的判据。",
                    "en": "_decide_continuation's docstring states the rule in two lines: no tool call → loop ends; tool call → loop continues. It doesn't read whether the model “wants to continue,” only the objective signal “did it issue a tool call” — because a tool call is two-stage, the result must be fed back to the model, so one more lap is required. Hard overrides: no call but a required_before_exit tool remains → continue; terminal tool → stop tool_rule; step 50 → stop max_steps. Continuing via request_heartbeat is the previous-gen V2 approach — exactly the “heartbeat” V3 dropped (lesson 15); scanning text for a keyword or watching token usage are not its criteria.",
                },
            },
            {
                "q": {
                    "zh": "step() 的预算上限 max_steps 默认是多少？这个默认值写在哪里？",
                    "en": "What is the default budget cap max_steps for step(), and where is that default defined?",
                },
                "opts": [
                    {"zh": "50 —— 写在 constants.py::DEFAULT_MAX_STEPS",
                     "en": "50 — defined in constants.py::DEFAULT_MAX_STEPS"},
                    {"zh": "10 —— 硬编码在 letta_agent_v3.py 的 step 函数体里",
                     "en": "10 — hard-coded in the body of step in letta_agent_v3.py"},
                    {"zh": "100 —— 由 llm_config 的上下文窗口大小推算出来",
                     "en": "100 — derived from llm_config's context-window size"},
                    {"zh": "没有默认值，每次调用 step() 都必须显式传入",
                     "en": "There is no default; every step() call must pass it explicitly"},
                ],
                "answer": 0,
                "why": {
                    "zh": "DEFAULT_MAX_STEPS = 50 定义在 constants.py，step(input_messages, max_steps=DEFAULT_MAX_STEPS) 用它当默认值。这个“预算”是循环的安全绳：跑满 50 圈还没自然收尾，step() 就主动盖 StopReasonType.max_steps 退出。它是个常量、不随上下文窗口大小变化；也不必显式传入——不传就是 50。",
                    "en": "DEFAULT_MAX_STEPS = 50 is defined in constants.py, and step(input_messages, max_steps=DEFAULT_MAX_STEPS) uses it as the default. This “budget” is the loop's safety rope: run a full 50 laps without a natural finish and step() actively stamps StopReasonType.max_steps and exits. It's a constant, not derived from the context-window size; nor must it be passed explicitly — omit it and you get 50.",
                },
            },
            {
                "q": {
                    "zh": "循环跑满 50 步上限而退出时，会盖上哪个停因？它映射的 run_status 是什么？",
                    "en": "When the loop exits because it hit the 50-step cap, which stop reason is stamped, and what run_status does it map to?",
                },
                "opts": [
                    {"zh": "max_steps，且映射成 completed（到点下班是预期内的保护，不算失败）",
                     "en": "max_steps, and it maps to completed (clocking out on schedule is expected protection, not a failure)"},
                    {"zh": "max_steps，但映射成 failed（撞上限算出错）",
                     "en": "max_steps, but it maps to failed (hitting the cap counts as an error)"},
                    {"zh": "end_turn，映射成 completed",
                     "en": "end_turn, mapping to completed"},
                    {"zh": "max_tokens_exceeded，映射成 failed",
                     "en": "max_tokens_exceeded, mapping to failed"},
                ],
                "answer": 0,
                "why": {
                    "zh": "step() 里到了 i == max_steps - 1 还没人设停因，就主动盖 StopReasonType.max_steps。反直觉的关键：LettaStopReason.run_status 把 max_steps 归到 completed（和 end_turn / tool_rule / requires_approval 同堆），不是 failed——撞上限是“按规矩到点下班”的保护，不当成崩溃。end_turn 是“没调工具的正常收尾”，不是撞上限；max_tokens_exceeded 是模型这轮因 finish_reason=length 被截断才映射 failed，与 50 步上限无关。",
                    "en": "In step(), when i == max_steps - 1 and no stop reason is set yet, it actively stamps StopReasonType.max_steps. The counterintuitive key: LettaStopReason.run_status puts max_steps in the completed pile (alongside end_turn / tool_rule / requires_approval), not failed — hitting the cap is “clocking out on schedule” protection, not a crash. end_turn is the “no-tool-call normal finish,” not the cap; max_tokens_exceeded maps to failed only for a length-truncated round (finish_reason=length), unrelated to the 50-step cap.",
                },
            },
            {
                "q": {
                    "zh": "step() 是边跑边把 token 流式吐给前端的吗？它最终返回什么？",
                    "en": "Does step() stream tokens to the frontend as it runs, and what does it ultimately return?",
                },
                "opts": [
                    {"zh": "不流式：它把每个 _step 抽干、攒进列表，循环结束统一返回一个 LettaResponse；真正流式的是另一个 stream()",
                     "en": "It doesn't stream: it drains each _step into a list and returns one LettaResponse when the loop ends; the real streaming is a separate stream()"},
                    {"zh": "流式：_step 里有 async for ... yield，所以整个 step() 就是在对外直播",
                     "en": "It streams: _step has async for ... yield, so the whole step() is broadcasting live"},
                    {"zh": "流式：step() 每跑完一步就把该步消息直接转发给客户端",
                     "en": "It streams: step() forwards each step's messages straight to the client as it finishes"},
                    {"zh": "既不流式也不返回消息，只返回一个 LettaUsageStatistics 用量统计",
                     "en": "It neither streams nor returns messages; it only returns a LettaUsageStatistics usage object"},
                ],
                "answer": 0,
                "why": {
                    "zh": "step() 不是流式接口：它在内部把每个 _step 生成器抽干、append 进一个列表，循环结束后统一返回一个完整的 LettaResponse。_step 里的 async for ... yield 只是“内部传话”——把消息交给 step() 去 append，不是转发给客户端。真正“对外直播”的是另一个方法 stream(...)，别和 step() 混为一谈。返回 LettaUsageStatistics 的是同步老祖 Agent.step（第 13 课），V2 / V3 的 step 返回的是 LettaResponse。",
                    "en": "step() is not a streaming interface: internally it drains each _step generator, appends to a list, and after the loop returns one complete LettaResponse. The async for ... yield inside _step is just an “internal relay” — handing messages to step() to append, not forwarding to the client. The real “live broadcast” is a separate method, stream(...); don't conflate it with step(). Returning LettaUsageStatistics is the synchronous elder Agent.step (lesson 13); V2 / V3's step returns a LettaResponse.",
                },
            },
        ],
        "open": [
            {
                "zh": "用“带预算的流水线工人”这个比喻，把第 14 课的 V3 循环串成一个完整故事，并想三件事：(1) 续步判据为什么敢只看“这轮有没有调工具”，而不像上一代那样让模型在参数里举手要心跳（request_heartbeat）？“客观信号驱动”相比“模型自报”各有什么利弊？(2) 为什么 _step 要把顺序定死成“先 _checkpoint_messages 落库、再 yield 流式”？设想进程在把这一步结果流式吐回去时崩了，这个顺序到底救回了什么？(3) max_steps = 50 这根安全绳防的到底是什么？为什么撞上它映射的是 completed 而不是 failed？",
                "en": "Using the metaphor of a “budgeted assembly-line worker,” weave lesson 14's V3 loop into one coherent story, and think through three things: (1) why dare to base continuation on just “did this round call a tool,” instead of having the model raise its hand for a heartbeat (request_heartbeat) like the previous generation? What are the trade-offs of an “objective-signal-driven” loop versus the model “self-reporting”? (2) Why does _step nail the order to “first _checkpoint_messages to persist, then yield to stream”? Imagine the process crashing while streaming this step's results back — what exactly does this order save? (3) What does the max_steps = 50 safety rope actually guard against, and why does hitting it map to completed rather than failed?",
            },
        ],
    },
    "15-heartbeat-to-no-heartbeat.html": {
        "mcq": [
            {
                "q": {
                    "zh": "老机制（元老 Agent / V2）里的 request_heartbeat 到底是个什么参数？它被加到哪些工具上？",
                    "en": "In the old mechanism (the elder Agent / V2), what kind of parameter is request_heartbeat, and which tools does it get added to?",
                },
                "opts": [
                    {"zh": "一个必填的布尔参数，由 runtime_override_tool_json_schema 动态加到每个非终止工具上；模型想续步就得设 true",
                     "en": "A required boolean param that runtime_override_tool_json_schema dynamically adds to every non-terminal tool; the model must set it true to step again"},
                    {"zh": "一个可选的字符串参数，只加到 send_message 这类终止工具上",
                     "en": "An optional string param added only to terminal tools like send_message"},
                    {"zh": "一个整数参数，表示模型还想再走多少步",
                     "en": "An integer param saying how many more steps the model wants to take"},
                    {"zh": "一个由框架自动填好的只读字段，模型无法设置",
                     "en": "A read-only field auto-filled by the framework that the model cannot set"},
                ],
                "answer": 0,
                "why": {
                    "zh": "request_heartbeat 是老机制在 tool_parser_helper.py::runtime_override_tool_json_schema 里动态注入的布尔参数：只加给非终止工具（send_message 这类终止工具被排除），而且进 required（必填）。于是模型每调一个普通工具都得表态——设 true 才续步，false（默认）就收尾。它不是可选的、不是字符串、不是步数计数器，也不是只读字段；恰恰相反，它把“要不要继续”的决定权显式交到了模型手里。",
                    "en": "request_heartbeat is a boolean the old mechanism injects dynamically in tool_parser_helper.py::runtime_override_tool_json_schema: it's added only to non-terminal tools (terminal tools like send_message are excluded) and put into required. So on every ordinary tool call the model must declare — set true to continue, false (the default) to wrap up. It is not optional, not a string, not a step counter, and not read-only; on the contrary, it hands the “continue or not” decision explicitly to the model.",
                },
            },
            {
                "q": {
                    "zh": "老机制里，模型把 request_heartbeat 设成 true 之后，框架靠什么把这一圈续下去？工具报错时又会怎样？",
                    "en": "In the old mechanism, once the model sets request_heartbeat to true, how does the framework keep the lap going? And what happens when a tool fails?",
                },
                "opts": [
                    {"zh": "框架注入一条 role=user 的“心跳”消息（REQ_HEARTBEAT_MESSAGE，对用户隐藏）把控制权还给模型并 continue；工具报错时即便没要心跳，也会自动注入 FUNC_FAILED_HEARTBEAT_MESSAGE 续一圈",
                     "en": "The framework injects a role=user “heartbeat” message (REQ_HEARTBEAT_MESSAGE, hidden from the user) to hand control back and continue; on tool failure it auto-injects FUNC_FAILED_HEARTBEAT_MESSAGE for one more lap even without a requested heartbeat"},
                    {"zh": "框架直接把工具结果当成 assistant 消息追加，不需要任何额外消息",
                     "en": "The framework just appends the tool result as an assistant message, needing no extra message"},
                    {"zh": "框架重启整个 step() 循环，从第 0 步重新跑",
                     "en": "The framework restarts the whole step() loop, rerunning from step 0"},
                    {"zh": "框架把 request_heartbeat 透传给工具函数，由工具自己决定要不要续",
                     "en": "The framework passes request_heartbeat through to the tool function and lets the tool decide whether to continue"},
                ],
                "answer": 0,
                "why": {
                    "zh": "解析在 agent.py::_handle_ai_response（pop 出标志、把字符串 \"true\" 归一成布尔），链式在 agent.py::step：function_failed 为真 → 注入 FUNC_FAILED_HEARTBEAT_MESSAGE 并 continue；否则 heartbeat_request 为真 → 注入 REQ_HEARTBEAT_MESSAGE 并 continue；都不满足 → break。这两条消息都带 NON_USER_MSG_PREFIX 前缀、角色是 user 但对用户隐藏。“报错”那条排在心跳判断之前，所以哪怕模型没要心跳，失败也会自动续一圈让它补救。框架并不会把心跳标志透传给工具（恰恰要先 pop 掉），也不会从头重启循环。",
                    "en": "Parsing is in agent.py::_handle_ai_response (pop the flag, normalize the string \"true\" to a bool); chaining is in agent.py::step: if function_failed → inject FUNC_FAILED_HEARTBEAT_MESSAGE and continue; elif heartbeat_request → inject REQ_HEARTBEAT_MESSAGE and continue; else break. Both messages carry the NON_USER_MSG_PREFIX prefix and have role=user but are hidden from the user. The “failure” branch sits before the heartbeat check, so even without a requested heartbeat a failure auto-continues one lap for recovery. The framework does not pass the heartbeat flag through to the tool (it pops it out first), nor does it restart the loop from scratch.",
                },
            },
            {
                "q": {
                    "zh": "V3（letta_v1_agent）不再用心跳，那它靠什么决定要不要再走一步？又怎么处理模型硬塞进来的 request_heartbeat？",
                    "en": "V3 (letta_v1_agent) no longer uses heartbeats — so how does it decide whether to take another step, and how does it handle a request_heartbeat the model jams in?",
                },
                "opts": [
                    {"zh": "靠 _decide_continuation：“这一轮调了工具就继续，没调就停”；_get_valid_tools 传 request_heartbeat=False 压根不加这个参数，_handle_ai_response 还会 args.pop(REQUEST_HEARTBEAT_PARAM, None) 把残留默默丢掉",
                     "en": "Via _decide_continuation: “called a tool this round → continue, didn't → stop”; _get_valid_tools passes request_heartbeat=False so the param isn't added at all, and _handle_ai_response does args.pop(REQUEST_HEARTBEAT_PARAM, None) to quietly drop any leftover"},
                    {"zh": "还是看 request_heartbeat，只是把默认值从 false 改成了 true",
                     "en": "It still reads request_heartbeat, just flips the default from false to true"},
                    {"zh": "看模型生成文本里有没有出现“继续”二字",
                     "en": "It scans the model's generated text for the word “continue”"},
                    {"zh": "每一步都无脑续，直到撞上 token 上限才停",
                     "en": "It blindly continues every step until it hits the token cap"},
                ],
                "answer": 0,
                "why": {
                    "zh": "V3 的 _get_valid_tools 调 runtime_override_tool_json_schema 时传 request_heartbeat=False（注释 \"NOTE: difference for v3\"），工具 schema 里根本没有这个参数。续步判据回到第 14 课的 _decide_continuation：调了工具 → 继续（工具调用是两段式的，结果得喂回模型），没调 → 停。就算某个旧 prompt 硬塞一个心跳参数，_handle_ai_response 也用 args.pop(REQUEST_HEARTBEAT_PARAM, None) 丢掉它，绝不让残留干扰判据。它既不靠默认 true、也不扫文本关键词，更不是无脑续到 token 上限。",
                    "en": "V3's _get_valid_tools passes request_heartbeat=False to runtime_override_tool_json_schema (comment \"NOTE: difference for v3\"), so the tool schema has no such param. Continuation falls back to lesson 14's _decide_continuation: called a tool → continue (a tool call is two-stage, the result must be fed back to the model); didn't → stop. Even if some old prompt jams in a heartbeat param, _handle_ai_response drops it with args.pop(REQUEST_HEARTBEAT_PARAM, None), never letting a leftover disturb the criterion. It neither relies on a true default, nor scans text for a keyword, nor blindly continues to the token cap.",
                },
            },
            {
                "q": {
                    "zh": "V3 删掉 request_heartbeat，最大的收益是消灭了哪一整类 bug？老机制原本又是用什么给这类 bug 打补丁的？",
                    "en": "Deleting request_heartbeat, what whole bug-class does V3 eliminate as its biggest win? And what did the old mechanism use to patch that bug-class?",
                },
                "opts": [
                    {"zh": "消灭“模型忘了设 request_heartbeat=true → agent 在调完工具后直接静默冻住”这一类 bug；老机制靠 local_llm 里的 insert_heartbeat 给本地模型兜底（issue #601）",
                     "en": "Eliminates the “model forgot to set request_heartbeat=true → the agent freezes silent after calling a tool” bug-class; the old mechanism backed local models up with insert_heartbeat in local_llm (issue #601)"},
                    {"zh": "消灭“工具执行超时”这类 bug；老机制靠加大超时时间兜底",
                     "en": "Eliminates the “tool execution timeout” bug-class; the old mechanism patched it by raising the timeout"},
                    {"zh": "消灭“上下文窗口溢出”这类 bug；老机制靠压缩历史兜底",
                     "en": "Eliminates the “context-window overflow” bug-class; the old mechanism patched it by compacting history"},
                    {"zh": "消灭“并行工具调用结果冲突”这类 bug；老机制靠串行化工具兜底",
                     "en": "Eliminates the “parallel tool-call result conflict” bug-class; the old mechanism patched it by serializing tools"},
                ],
                "answer": 0,
                "why": {
                    "zh": "把“要不要继续”押在模型自觉上很脆弱：模型一旦忘了设 request_heartbeat=true，工具跑完没人续步，agent 就在用户说完话后静默冻住。这正是 insert_heartbeat（local_llm/function_parser.py）存在的理由——本地模型常忘设（issue #601），于是“上一条是真用户消息”且“这是非 send_message 工具调用”时，强行补 request_heartbeat=True。V3 把判据换成“调了工具就继续”，这一整类“模型忘了设”的 bug 随之消失，补丁也不必存在。上下文溢出、工具超时、并行冲突是另外的问题，与删心跳无关。",
                    "en": "Pinning “continue or not” on the model's conscientiousness is fragile: the moment the model forgets to set request_heartbeat=true, the tool finishes, nobody steps again, and the agent freezes silent right after the user speaks. That is exactly why insert_heartbeat (local_llm/function_parser.py) exists — local models often forget (issue #601), so when “the previous message is a real user message” and “this is a non-send_message tool call,” it forces in request_heartbeat=True. V3 swaps the criterion to “called a tool → continue,” so the whole “model forgot to set it” bug-class vanishes and the patch needn't exist. Context overflow, tool timeouts, and parallel conflicts are separate issues, unrelated to deleting heartbeats.",
                },
            },
            {
                "q": {
                    "zh": "关于“哪几代靠心跳续步”，下面哪个说法是对的？",
                    "en": "About “which generations continue via heartbeats,” which statement is correct?",
                },
                "opts": [
                    {"zh": "元老 Agent 和第二代 V2 都还在用心跳（V2 的 _get_valid_tools 传 True，_decide_continuation 里 continue_stepping = request_heartbeat），只有第三代 V3 把它彻底删掉",
                     "en": "Both the elder Agent and the second-gen V2 still use heartbeats (V2's _get_valid_tools passes True, and continue_stepping = request_heartbeat in _decide_continuation); only the third-gen V3 removes it entirely"},
                    {"zh": "心跳是被全盘否定的旧设计，V2 和 V3 都已经不用了",
                     "en": "Heartbeats are a wholly rejected old design that both V2 and V3 have dropped"},
                    {"zh": "只有元老 Agent 用心跳，V2 和 V3 都改用了 _decide_continuation",
                     "en": "Only the elder Agent uses heartbeats; both V2 and V3 switched to _decide_continuation"},
                    {"zh": "三代都在用心跳，V3 只是把常量名换了一个",
                     "en": "All three generations use heartbeats; V3 merely renamed a constant"},
                ],
                "answer": 0,
                "why": {
                    "zh": "别把“心跳”当成被否定的旧设计——同代的 V2 依然在用。letta_agent_v2.py::_get_valid_tools 传 request_heartbeat=True，其 _decide_continuation 里 continue_stepping = request_heartbeat，续步判据仍由模型的心跳标志驱动。只有 V3（letta_v1_agent，注释 \"no heartbeats or forced tool calls\"）才把心跳整套拿掉——它重写 _decide_continuation，去掉该参数、默认继续。所以不是“V2/V3 都不用”，不是“只有 Agent 用”，更不是“三代都用、只换名字”。一参之差（_get_valid_tools 传 True 还是 False）正是 V2 与 V3 的分水岭。",
                    "en": "Don't treat “heartbeats” as a rejected old design — the same-era V2 still uses them. letta_agent_v2.py::_get_valid_tools passes request_heartbeat=True, and continue_stepping = request_heartbeat in its _decide_continuation, so continuation is still driven by the model's heartbeat flag. Only V3 (letta_v1_agent, comment \"no heartbeats or forced tool calls\") removes the whole heartbeat machinery — it overrides _decide_continuation to drop that param and default to continue. So it's not “neither V2 nor V3,” not “only Agent,” and not “all three with just a rename.” One param's difference (_get_valid_tools passing True vs False) is the watershed between V2 and V3.",
                },
            },
        ],
        "open": [
            {
                "zh": "用“对讲机”这个比喻，把第 15 课从“心跳续步”到“调了工具就继续”的演化串成一个完整故事，并想三件事：(1) 老机制为什么要让模型在参数里举手要心跳（request_heartbeat=true）？把“要不要继续”交给模型，灵活在哪、脆弱在哪？(2) insert_heartbeat 这块给本地模型打的补丁（issue #601），和 V3“从根上不依赖模型自觉”的思路，本质区别在哪？为什么说“补丁盖症状、V3 治根因”？(3) V3 既然觉得心跳多余，为什么同代的 V2 还留着它？从“兼容旧设计”和“演化节奏”的角度想想，删一个看似冗余的参数为什么也得分代、分步来做。",
                "en": "Using the “walkie-talkie” metaphor, weave lesson 15's evolution from “heartbeat-driven continuation” to “called a tool → continue” into one coherent story, and think through three things: (1) why did the old mechanism make the model raise its hand for a heartbeat (request_heartbeat=true) in the parameters? Handing “continue or not” to the model — where's the flexibility, where's the fragility? (2) What's the essential difference between the insert_heartbeat patch for local models (issue #601) and V3's “stop depending on the model's conscientiousness at the root”? Why say “a patch covers the symptom, V3 cures the root cause”? (3) If V3 deems heartbeats redundant, why does the same-era V2 still keep them? Thinking in terms of “compatibility with the old design” and “the pace of evolution,” why must even deleting a seemingly redundant parameter be done generation by generation, step by step?",
            },
        ],
    },
    "16-tool-rules.html": {
        "mcq": [
            {
                "q": {
                    "zh": "agent 循环刚开始、还没调过任何工具时，是哪种工具规则能“强制”第一步只能调某个（些）特定工具？ToolRulesSolver 又是怎么处理它的？",
                    "en": "At the very start of the agent loop, before any tool has been called, which tool rule can “force” the first step to call only a specific tool (or tools)? And how does ToolRulesSolver handle it?",
                },
                "opts": [
                    {"zh": "run_first（子类 InitToolRule）；get_allowed_tool_names 一看 tool_call_history 为空且配了 init 规则，就直接返回 [r.tool_name for r in init_tool_rules]，别的规则一概不算",
                     "en": "run_first (subclass InitToolRule); when get_allowed_tool_names sees an empty tool_call_history with init rules configured, it returns [r.tool_name for r in init_tool_rules] directly, ignoring every other rule"},
                    {"zh": "exit_loop（TerminalToolRule）；它把第一步钉死在终止工具上",
                     "en": "exit_loop (TerminalToolRule); it pins the first step onto the terminal tool"},
                    {"zh": "constrain_child_tools（ChildToolRule）；首步只能调它列出的 children",
                     "en": "constrain_child_tools (ChildToolRule); the first step may only call its listed children"},
                    {"zh": "required_before_exit（RequiredBeforeExitToolRule）；它要求第一步必须是结算类工具",
                     "en": "required_before_exit (RequiredBeforeExitToolRule); it requires the first step to be a settlement-type tool"},
                ],
                "answer": 0,
                "why": {
                    "zh": "run_first 对应子类 InitToolRule，是唯一“强制首步”的规则。get_allowed_tool_names 的第一条岔路就是：if not self.tool_call_history and self.init_tool_rules → return [r.tool_name for r in self.init_tool_rules]，首步直接锁定 init 工具、其他规则一律不参与。exit_loop 管的是“调到就停”（终点，不是起点），constrain_child_tools 约束的是“调完某父工具后的下一步”（要先有父调用），required_before_exit 只要求“退出前至少调一次”、并不限定它是第一步。别被子类名误导：枚举值是 run_first 而非 Init。",
                    "en": "run_first maps to the subclass InitToolRule, the only “force the first step” rule. get_allowed_tool_names's first fork is exactly: if not self.tool_call_history and self.init_tool_rules → return [r.tool_name for r in self.init_tool_rules], locking the first step onto the init tools and excluding every other rule. exit_loop governs “called → stop” (the end, not the start), constrain_child_tools constrains “the next step after a given parent tool” (a parent call must come first), and required_before_exit only demands “at least one call before exit,” not that it be the first step. Don't be misled by the subclass name: the enum value is run_first, not Init.",
                },
            },
            {
                "q": {
                    "zh": "模型无视裁剪后的 schema，硬挑了一个不在合法集里的工具。框架会怎么处理这次调用？",
                    "en": "The model ignores the trimmed schema and picks a tool that isn't in the legal set. How does the framework handle that call?",
                },
                "opts": [
                    {"zh": "不执行该工具：_handle_ai_response 算出 tool_rule_violated = name not in valid_tool_names，转而调 _build_rule_violation_result 合成一条 status=\"error\" 的 [ToolConstraintError] 当作“工具返回”喂回模型，让它自纠",
                     "en": "It doesn't execute the tool: _handle_ai_response computes tool_rule_violated = name not in valid_tool_names, then calls _build_rule_violation_result to synthesize a status=\"error\" [ToolConstraintError] as the “tool return” fed back to the model for self-correction"},
                    {"zh": "照样执行该工具，只是在结果后面附一句警告，提醒模型下次别这么调",
                     "en": "It runs the tool anyway, just appending a warning after the result to remind the model not to do it next time"},
                    {"zh": "直接抛出异常、终止整个 step，让用户看到报错",
                     "en": "It raises an exception outright, terminating the whole step so the user sees the error"},
                    {"zh": "静默丢弃这次调用，既不执行也不回任何消息，直接进入下一步",
                     "en": "It silently drops the call, neither executing nor returning any message, and moves straight to the next step"},
                ],
                "answer": 0,
                "why": {
                    "zh": "违规工具绝不执行。判定在 letta_agent_v3.py::_handle_ai_response：tool_rule_violated = name not in valid_tool_names；为真则跳过执行，改由 agents/helpers.py::_build_rule_violation_result 合成一条 ToolExecutionResult(status=\"error\", func_return=\"[ToolConstraintError] Cannot call X, valid tools include: [...]\")，当作那个工具的“返回值”喂回模型。它既不是“先执行再警告”，也不是直接 raise 崩掉 step（那样用户只会看到莫名其妙的报错），更不是静默丢弃——而是把违规变成一次“教学”，循环继续、给模型重挑的机会。错误字符串在 agent 层拼，solver 只通过 guess_rule_violation 供一句 hint。",
                    "en": "A violating tool is never executed. The decision is in letta_agent_v3.py::_handle_ai_response: tool_rule_violated = name not in valid_tool_names; if true it skips execution and instead has agents/helpers.py::_build_rule_violation_result synthesize a ToolExecutionResult(status=\"error\", func_return=\"[ToolConstraintError] Cannot call X, valid tools include: [...]\") fed back as that tool's “return value.” It's neither “run then warn,” nor a bare raise that crashes the step (which would only show the user a baffling error), nor a silent drop — it turns the violation into a “lesson,” continuing the loop and giving the model a chance to re-pick. The error string is assembled in the agent layer; the solver only supplies a one-line hint via guess_rule_violation.",
                },
            },
            {
                "q": {
                    "zh": "ToolRulesSolver.get_allowed_tool_names 在算“这一步合法工具集”时，到底对哪些规则求交集来缩小工具集？",
                    "en": "When ToolRulesSolver.get_allowed_tool_names computes “this step's legal tool set,” which rules does it actually intersect to shrink the tool set?",
                },
                "opts": [
                    {"zh": "只对 child 类（Child/Conditional/MaxCount）+ parent 规则求交，再 & 可用工具；terminal / continue / required_before_exit / requires_approval 根本不进交集",
                     "en": "Only the child family (Child/Conditional/MaxCount) + parent rules are intersected, then & available tools; terminal / continue / required_before_exit / requires_approval never enter the intersection"},
                    {"zh": "对全部 9 种规则一视同仁地求交集",
                     "en": "All 9 rule types are intersected, treated alike"},
                    {"zh": "只对 terminal + required_before_exit 求交，因为它们决定循环能否结束",
                     "en": "Only terminal + required_before_exit are intersected, since they decide whether the loop can end"},
                    {"zh": "对 init + requires_approval 求交，其余规则在别处处理",
                     "en": "init + requires_approval are intersected, with the rest handled elsewhere"},
                ],
                "answer": 0,
                "why": {
                    "zh": "缩小工具集只看 child + parent 两类。源码里 relevant = self.child_based_tool_rules + self.parent_tool_rules（child_based 桶含 Child/Conditional/MaxCount），对每条调 get_valid_tools 求交，再 & available。terminal / continue / required_before_exit / requires_approval 这几桶不参与交集——solver 文档字符串明说它们“在 agent 循环里生效，不用来限制工具”，它们的作用体现在 _decide_continuation 的续步/停止判断里。init 规则则走另一条岔路（首步强制），不在这步的交集里。所以“全部 9 种求交”或“terminal 参与缩集”都是典型记反。",
                    "en": "Shrinking the tool set looks only at the child + parent families. In source, relevant = self.child_based_tool_rules + self.parent_tool_rules (the child_based bucket holds Child/Conditional/MaxCount); each rule's get_valid_tools is intersected, then & available. The terminal / continue / required_before_exit / requires_approval buckets don't join the intersection — the solver's docstring states they “apply in the agent loop, not to restrict tools,” and their effect shows up in _decide_continuation's continue/stop decision. The init rules take the other fork (first-step forcing), not this step's intersection. So “intersect all 9” or “terminal shrinks the set” are classic reversals.",
                },
            },
            {
                "q": {
                    "zh": "某工具配了 requires_approval。模型这一步要调它时，agent 循环会停下，停止原因（StopReasonType）记成什么？随后又发生什么？",
                    "en": "A tool is configured with requires_approval. When the model goes to call it this step, the agent loop stops — what stop reason (StopReasonType) is recorded, and what happens next?",
                },
                "opts": [
                    {"zh": "停止原因记 requires_approval：循环不执行该工具，持久化一条 create_approval_request_message_from_llm_response(...) 造的“审批请求”消息；人批准后下一次以 is_approval_response 进来，绕过违规检查放行",
                     "en": "The stop reason is requires_approval: the loop doesn't execute the tool, persists an “approval request” message from create_approval_request_message_from_llm_response(...); after a human approves, the next entry comes in as an is_approval_response that bypasses the violation check and proceeds"},
                    {"zh": "停止原因记 tool_rule，和终止工具一样，因为两者都让循环停下",
                     "en": "The stop reason is tool_rule, same as a terminal tool, since both stop the loop"},
                    {"zh": "停止原因记 max_steps：审批被当作“步数耗尽”处理",
                     "en": "The stop reason is max_steps: approval is treated as “steps exhausted”"},
                    {"zh": "不记停止原因，循环照常执行工具，只是事后发一封审批邮件",
                     "en": "No stop reason is recorded; the loop runs the tool as usual and just sends an approval email afterward"},
                ],
                "answer": 0,
                "why": {
                    "zh": "命中 is_requires_approval_tool 时，循环停在 StopReasonType.requires_approval（不是 tool_rule，也不是 max_steps）。它不执行该工具，而是持久化一条由 create_approval_request_message_from_llm_response(...) 生成的“审批请求”消息，把控制权交给人。等批准后，下一次请求以 is_approval_response 进入，它绕过违规检查直接放行执行——这正对上第 14 课列的停止原因表，也接上第 15 课“工具规则可覆盖默认行为”。注意区分：终止工具 exit_loop 停在 tool_rule，requires_approval 停在 requires_approval，两者停止原因不同。",
                    "en": "When is_requires_approval_tool hits, the loop stops at StopReasonType.requires_approval (not tool_rule, not max_steps). It doesn't execute the tool but persists an “approval request” message generated by create_approval_request_message_from_llm_response(...), handing control to a human. After approval, the next request enters as an is_approval_response that bypasses the violation check and proceeds — matching lesson 14's stop-reason table and connecting to lesson 15's “tool rules can override default behavior.” Note the distinction: a terminal tool (exit_loop) stops at tool_rule, while requires_approval stops at requires_approval — different stop reasons.",
                },
            },
            {
                "q": {
                    "zh": "关于 9 种 ToolRuleType 的“枚举值”和“子类名”，下面哪个说法是对的？",
                    "en": "About the 9 ToolRuleType “enum values” and “subclass names,” which statement is correct?",
                },
                "opts": [
                    {"zh": "枚举值是历史命名 run_first / exit_loop / constrain_child_tools 等，而子类才叫 InitToolRule / TerminalToolRule / ChildToolRule——别照子类名去猜枚举值",
                     "en": "The enum values are legacy-named run_first / exit_loop / constrain_child_tools etc., while the subclasses are InitToolRule / TerminalToolRule / ChildToolRule — don't guess the enum value from the subclass name"},
                    {"zh": "枚举值就是 Init / Terminal / Child，和子类名前缀完全一致",
                     "en": "The enum values are Init / Terminal / Child, exactly matching the subclass name prefixes"},
                    {"zh": "枚举值和子类名是同一个字符串，框架不区分二者",
                     "en": "The enum value and the subclass name are the same string; the framework doesn't distinguish them"},
                    {"zh": "根本没有枚举，规则全靠子类的 isinstance 判断，没有 type 字段",
                     "en": "There's no enum at all; rules rely solely on isinstance of the subclass, with no type field"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这是最容易踩的命名坑。枚举 schemas/enums.py::ToolRuleType 用的是历史名：run_first / exit_loop / continue_loop / conditional / constrain_child_tools / max_count_per_step / parent_last_tool / required_before_exit / requires_approval。而子类（schemas/tool_rule.py）叫 InitToolRule / TerminalToolRule / ChildToolRule…，每个子类 pin 死一个 Literal type 字符串（如 InitToolRule.type == \"run_first\"）。所以枚举值不是 Init/Terminal/Child；type 字符串与子类名也不是同一个串；更不是“没有 type”——恰恰相反，正是这个 type 字段构成了 pydantic 的判别联合，让一串带 type 的 JSON 能各归各的子类。",
                    "en": "This is the easiest naming trap. The enum schemas/enums.py::ToolRuleType uses legacy names: run_first / exit_loop / continue_loop / conditional / constrain_child_tools / max_count_per_step / parent_last_tool / required_before_exit / requires_approval. The subclasses (schemas/tool_rule.py) are InitToolRule / TerminalToolRule / ChildToolRule…, each pinning a Literal type string (e.g. InitToolRule.type == \"run_first\"). So the enum values are not Init/Terminal/Child; the type string and the subclass name aren't the same string; and it's not “no type” — on the contrary, that very type field forms pydantic's discriminated union, letting a string of JSON with a type field resolve to the right subclass.",
                },
            },
        ],
        "open": [
            {
                "zh": "用“城市交通规则”这个比喻，把第 16 课的工具规则系统讲成一个完整故事，并想三件事：(1) 为什么要把“agent 该怎么用工具”从“模型的自觉”搬成“路口的硬件”（声明式、可强制）？事前裁 schema 和事后合成错误这“两道防线”各自防住了什么？只留一道行不行？(2) get_allowed_tool_names 为什么“只对 child + parent 求交”来缩工具集，而把 terminal / continue / required / approval 留给 _decide_continuation？“缩工具集”和“决定循环怎么走”为什么要拆成两件事？(3) Letta 故意不做“环/冲突检测”，只逐条 pydantic 校验。把这把“双刃剑”交给配置者，好处和风险各在哪？如果你要给一个真实 agent 配规则，你会怎么自查规则之间不打架？",
                "en": "Using the “city traffic rules” metaphor, tell lesson 16's tool-rule system as one coherent story, and think through three things: (1) why move “how an agent should use tools” from “the model's conscientiousness” into “hardware at the junction” (declarative, enforceable)? What does each of the “two lines of defense” — trimming the schema beforehand and synthesizing an error afterward — guard against? Would keeping only one line do? (2) Why does get_allowed_tool_names “intersect only child + parent” to shrink the tool set, leaving terminal / continue / required / approval to _decide_continuation? Why split “shrink the tool set” and “decide how the loop proceeds” into two separate things? (3) Letta deliberately does no “cycle/conflict detection,” only per-rule pydantic validation. Handing this “double-edged sword” to the configurer — where are the benefits and the risks? If you were configuring rules for a real agent, how would you self-check that the rules don't clash?",
            },
        ],
    },
    "17-tool-as-function.html": {
        "mcq": [
            {
                "q": {
                    "zh": "模型在决定要不要调某个工具、以及怎么填参数时，它真正读到的是什么？",
                    "en": "When the model decides whether to call a tool and how to fill its arguments, what does it actually read?",
                },
                "opts": [
                    {"zh": "只有 generate_schema 从签名 + docstring 拼出的那份 JSON schema——name、description，以及每个参数的类型/描述。函数体从不展示给模型",
                     "en": "Only the JSON schema that generate_schema built from the signature + docstring — name, description, and each parameter's type/description. The function body is never shown to the model"},
                    {"zh": "函数的完整 Python 源码（含函数体），好让它推敲各种边界情况",
                     "en": "The full Python source of the function, body included, so it can reason about edge cases"},
                    {"zh": "主要是 docstring 的 Returns: 段，它告诉模型这次调用会返回什么",
                     "en": "Mainly the docstring's Returns: section, which tells it what the call will hand back"},
                    {"zh": "函数在几组样例输入上实际执行的一段运行轨迹",
                     "en": "A live trace of the function executing on a few sample inputs"},
                ],
                "answer": 0,
                "why": {
                    "zh": "模型只读 schema。generate_schema（letta/functions/schema_generator.py）用 inspect.signature 取参数与注解、用 docstring_parser（Google 风）取描述文字，产出 name / description / parameters；函数体被抹掉，所以“完整源码”和“运行轨迹”它都看不到——这正是“你写代码、模型读 schema”的全部要义。而 Returns: 是给人看的：只有 docstring 第一句（成为 description）和 Args: 里逐参数那几行会进 schema，Returns: 不进。",
                    "en": "The model reads only the schema. generate_schema (letta/functions/schema_generator.py) uses inspect.signature for params + annotations and docstring_parser (Google style) for the description text, emitting name / description / parameters; the body is wiped, so neither the full source nor a live trace is ever available — that is the whole point of “you write code, the model reads a schema.” And Returns: is for humans: only the first docstring line (which becomes the description) and the Args: per-parameter lines enter the schema, not Returns:.",
                },
            },
            {
                "q": {
                    "zh": "你写了个工具，签名里有参数 x: int，但 docstring 的 Args: 段从没描述 x。创建这个工具时会发生什么？",
                    "en": "You write a tool whose signature has a parameter x: int, but your docstring's Args: section never describes x. What happens when the tool is created?",
                },
                "opts": [
                    {"zh": "generate_schema 在构建 schema 时 raise ValueError——不给 x 补上描述，工具就建不出来",
                     "en": "generate_schema raises ValueError while building the schema — the tool can't be created until you add a description for x"},
                    {"zh": "工具照常创建；x 只是拿到一个空描述，模型靠猜来填它",
                     "en": "The tool is created fine; x just gets an empty description and the model fills it by guessing"},
                    {"zh": "工具能创建，但 x 被悄悄从 schema 里丢掉，模型根本看不到它",
                     "en": "The tool is created, but x is silently dropped from the schema so the model never sees it"},
                    {"zh": "它只记一条警告，并给 x 套上 “No description available” 顶替",
                     "en": "It only logs a warning and substitutes “No description available” for x"},
                ],
                "answer": 0,
                "why": {
                    "zh": "在 generate_schema 的逐参数循环里，缺描述是硬中止：它在 doc.params 里找该参数、取到 None，于是 raise ValueError（Parameter 'x' lacks a description...）。创建当场失败，错误一路抛给注册工具的调用方。它不会降级成警告、不会塞个空/默认描述、也不会悄悄丢弃——这些做法都会瓦解“docstring 是模型唯一的说明书”。一个易混点：“No description available” 这个回退只用于函数级总描述，从不用于某个参数。",
                    "en": "In generate_schema's per-parameter loop a missing description is a hard stop: it scans doc.params for that arg, gets None, and raises ValueError (Parameter 'x' lacks a description...). Creation aborts and the error propagates to whoever is registering the tool. It is not downgraded to a warning, not given an empty/default description, and not silently dropped — any of those would defeat “the docstring is the model's only manual.” One subtlety: the “No description available” fallback applies only to the function-level description, never to a parameter.",
                },
            },
            {
                "q": {
                    "zh": "一个工具定义为 def foo(self, agent_state, x: int)。生成的 JSON schema 里会出现哪些参数？",
                    "en": "A tool is defined as def foo(self, agent_state, x: int). Which parameters appear in the generated JSON schema?",
                },
                "opts": [
                    {"zh": "只有 x。self 和 agent_state 属于 TOOL_RESERVED_KWARGS，generate_schema 直接跳过；它们从不进 schema，模型既看不到也不用填",
                     "en": "Only x. self and agent_state are in TOOL_RESERVED_KWARGS, so generate_schema skips them; they never enter the schema and the model neither sees nor fills them"},
                    {"zh": "三个都在——self、agent_state、x——因为 schema 完全照搬签名",
                     "en": "All three — self, agent_state, and x — since the schema mirrors the signature exactly"},
                    {"zh": "x 和 agent_state，但不含 self",
                     "en": "x and agent_state, but not self"},
                    {"zh": "只有 x，外加一个 request_heartbeat 参数——由 generate_schema 作为保留控制字段注入",
                     "en": "Only x, plus a request_heartbeat parameter that generate_schema injects as a reserved control field"},
                ],
                "answer": 0,
                "why": {
                    "zh": "generate_schema 会跳过保留参数：循环开头，若 p.name 在 TOOL_RESERVED_KWARGS（[self, agent_state]）里就 continue，两者都不进 schema——schema 并非逐字照搬签名。而 request_heartbeat 不是由 generate_schema 加的，它在运行期另行附加（第 15 课），所以任何“让 generate_schema 注入它”的选项都是错的。最终只剩 x，也就是模型真正要填的那一个参数。",
                    "en": "generate_schema skips reserved kwargs: at the top of the loop, if p.name is in TOOL_RESERVED_KWARGS ([self, agent_state]) it continues, so neither enters the schema — the signature is not mirrored verbatim. And request_heartbeat is NOT added by generate_schema; it is attached separately at runtime (Lesson 15), so any option that has generate_schema inject it is wrong. Net result: only x, the single parameter the model must actually supply.",
                },
            },
            {
                "q": {
                    "zh": "你能把工具参数标注成 Dict[str, int] 并让它进入 schema 吗？",
                    "en": "Can you annotate a tool parameter as Dict[str, int] and have it become part of the schema?",
                },
                "opts": [
                    {"zh": "不行——type_to_json_schema_type 对带参的 Dict[k,v] 会 raise ValueError。要传结构化入参，请改用 Pydantic BaseModel，它会经 model_json_schema() 展开",
                     "en": "No — type_to_json_schema_type raises ValueError on a parameterized Dict[k,v]. For structured input, define a Pydantic BaseModel instead; it is expanded via model_json_schema()"},
                    {"zh": "可以——它能干净地映射成“字符串键、整数值”的 JSON object",
                     "en": "Yes — it maps cleanly to a JSON object with string keys and integer values"},
                    {"zh": "可以，但前提是你还得给它一个默认值 {}",
                     "en": "Yes, but only if you also give it a default value of {}"},
                    {"zh": "不行——它会 raise TypeError，和“缺类型注解”报的是同一个错",
                     "en": "No — it raises TypeError, the very same error you get from a missing type annotation"},
                ],
                "answer": 0,
                "why": {
                    "zh": "带参的 Dict[str, int] 会被拒：type_to_json_schema_type 手写映射各类型，对带键值的 Dict 抛 ValueError（对一般 Union 抛 NotImplementedError）。JSON schema 无法无歧义地表达任意键值字典，所以 Letta 宁可报错也不猜。正解是 Pydantic BaseModel，其 model_json_schema() 会把字段/类型/必填嵌进工具 schema。注意错误类型：这是 ValueError，不是“缺注解”时的 TypeError——两道关、两种异常。",
                    "en": "A parameterized Dict[str, int] is rejected: type_to_json_schema_type hand-maps types and raises ValueError for a keyed Dict (and NotImplementedError for a general Union). JSON schema can't express an arbitrary key/value dict unambiguously, so Letta errors rather than guesses. The fix is a Pydantic BaseModel, whose model_json_schema() nests fields/types/required into the tool schema. Mind the error kind: it is ValueError, not the TypeError raised for a missing annotation — different gates, different exceptions.",
                },
            },
            {
                "q": {
                    "zh": "你 docstring 的 Args: 段格式略不规范，validate_google_style_docstring 不太满意。工具还建得出来吗？",
                    "en": "Your docstring's Args: block is formatted a little off-standard, so validate_google_style_docstring isn't satisfied. Does the tool still build?",
                },
                "opts": [
                    {"zh": "通常能——validate_google_style_docstring 只是建议性的：它的 ValueError 被捕获后降级成 logger.warning。真正的关卡是逐参数检查“有没有描述、有没有类型注解”",
                     "en": "Usually yes — validate_google_style_docstring is advisory: its ValueError is caught and downgraded to a logger.warning. The real gate is the per-parameter check for a description and a type annotation"},
                    {"zh": "不能——任何 Google 风校验失败都会以 ValueError 中止 schema 生成",
                     "en": "No — any Google-style validation failure aborts schema generation with a ValueError"},
                    {"zh": "不能——它会 raise TypeError，不修好格式工具就被拒",
                     "en": "No — it raises TypeError and the tool is rejected until the formatting is fixed"},
                    {"zh": "能，而且那些不规范的参数会在建 schema 前被自动修正成 Google 风格",
                     "en": "Yes, and the malformed parameters are auto-corrected to Google style before the schema is built"},
                ],
                "answer": 0,
                "why": {
                    "zh": "两道关，一软一硬。validate_google_style_docstring 是软的：它的 ValueError 被 try/except 包住、记成一条警告，所以单是格式不规范并不会拦住构建。硬关在 generate_schema 的循环里——参数缺描述抛 ValueError、缺类型注解抛 TypeError，这两个不会被吞。没有任何东西会自动修正你的 docstring。所以格式只是“提醒”，逐参数缺描述或缺注解才是真正拦住创建的“硬伤”。",
                    "en": "Two gates, soft and hard. validate_google_style_docstring is soft: its ValueError is wrapped in try/except and logged as a warning, so off-standard formatting alone won't stop the build. The hard gate lives inside generate_schema's loop — a parameter with no description raises ValueError, a missing type annotation raises TypeError; those are not swallowed. Nothing auto-corrects your docstring. So formatting is a reminder; a missing per-parameter description or annotation is what actually blocks creation.",
                },
            },
        ],
        "open": [
            {
                "zh": "用“餐厅菜单”这个比喻，把第 17 课的故事完整讲一遍，并想三件事：(1) 为什么 Letta 把工具表示成“裸函数 + docstring”，而不是搞一个特殊基类或装饰器？“模型只读 schema、从不读函数体”换来了什么——又给 docstring 压上了什么新责任？(2) generate_schema 把“某个参数缺描述”做成创建期的硬 ValueError，却对“不规范的 Google 风 docstring”只给一条警告放行。为什么把“硬/软”这条线正好画在这里？(3) 类型表支持 str/int/bool/float/Optional/List/Literal/BaseModel，却拒绝带参 Dict 和一般 Union。如果一定要再支持一种“结构化”入参类型，你会扩这张表，还是把人引向 Pydantic 模型——你会怎么权衡？",
                "en": "Use the “restaurant menu” metaphor to tell lesson 17's story as a whole, and think through three things: (1) Why does Letta represent a tool as a bare function + docstring instead of a special base class or decorator? What does “the model reads only the schema, never the body” buy you — and what new responsibility does it place on the docstring? (2) generate_schema turns a missing per-parameter description into a hard ValueError at creation time, yet lets an off-standard Google-style docstring through with only a warning. Why draw the “hard vs soft” line exactly there? (3) The type map supports str/int/bool/float/Optional/List/Literal/BaseModel but rejects parameterized Dict and general Union. If you had to support one more “structured” input type, would you extend the map or push people toward Pydantic models — and what would you trade off?",
            },
        ],
    },
    "18-schema-without-executing.html": {
        "mcq": [
            {
                "q": {
                    "zh": "用户注册自定义 Python 工具时，递给服务器的是一段源码字符串（不是函数对象）。Letta 如何为它产出 JSON schema？",
                    "en": "A user registers a custom Python tool by sending a source-code string (not a function object). How does Letta produce its JSON schema?",
                },
                "opts": [
                    {"zh": "derive_openai_json_schema 用 ast.parse 纯静态解析源码、重建签名、包成 MockFunction，再复用 generate_schema——这段代码从不被 exec 或 import",
                     "en": "derive_openai_json_schema parses the source with ast.parse (pure AST), rebuilds a signature, wraps it in a MockFunction, and reuses generate_schema — the code is never exec'd or imported"},
                    {"zh": "它把源码当模块 import 进来，再对得到的函数对象调 inspect.signature",
                     "en": "It imports the source as a module, then calls inspect.signature on the resulting function object"},
                    {"zh": "它拿几组样例输入把函数跑一遍，记录观察到的参数/返回类型",
                     "en": "It runs the function once on a few sample inputs and records the argument/return types it observes"},
                    {"zh": "它让模型读源码、生成一份 schema，再把模型的输出缓存下来",
                     "en": "It asks the model to read the source and emit a schema, then caches the model's output"},
                ],
                "answer": 0,
                "why": {
                    "zh": "第 18 课的核心就是“不运行代码也能派生 schema”。derive_openai_json_schema（letta/functions/functions.py）调用 _parse_function_from_source：用 ast.parse 纯静态解析、挑出函数节点、重建 inspect.Signature，返回一个 MockFunction；再把这个 mock 喂给第 17 课同一个 generate_schema。import + inspect 会执行顶层代码（在多租户服务器上即 RCE），既不是“跑函数”也不是“问模型”。是“读”，不是“跑”。",
                    "en": "The whole point of lesson 18 is deriving a schema without running the code. derive_openai_json_schema (letta/functions/functions.py) calls _parse_function_from_source, which uses ast.parse — purely static — picks the function node, rebuilds an inspect.Signature, and returns a MockFunction; that mock is then fed to the same generate_schema from lesson 17. import + inspect would execute top-level code (an RCE on a multi-tenant server), and neither running the function nor asking the model is involved. Reading, not running.",
                },
            },
            {
                "q": {
                    "zh": "generate_schema 期待一个可内省的真函数对象，可我们手里只有从 AST 拆出来的零件。MockFunction 凭什么能顶替上场？",
                    "en": "generate_schema expects a real function object to introspect, but we only hold fragments pulled from the AST. What makes a MockFunction good enough to stand in?",
                },
                "opts": [
                    {"zh": "它设好 __name__、__doc__、__signature__——而 inspect.signature() 与 docstring 解析读的正是这几个属性，于是对从未运行的代码也能内省",
                     "en": "It sets __name__, __doc__, and __signature__ — exactly what inspect.signature() and docstring parsing read — so introspection works on code that never ran"},
                    {"zh": "它把源码编译成真正可调用的对象，让 inspect 能在沙箱里安全地执行它",
                     "en": "It compiles the source into a real callable so inspect can execute it safely in a sandbox"},
                    {"zh": "它继承用户的类、重写 __call__ 让其直接返回 schema",
                     "en": "It subclasses the user's class and overrides __call__ to return the schema directly"},
                    {"zh": "它保存原始源码字符串，generate_schema 每要一个字段就把字符串重新解析一遍",
                     "en": "It stores the raw source string, and generate_schema re-parses that string each time it needs a field"},
                ],
                "answer": 0,
                "why": {
                    "zh": "inspect 不查血统、只读属性。MockFunction.__init__（letta/functions/functions.py）设好 __name__、__doc__、__signature__；一旦显式设了 __signature__，inspect.signature(mock) 就返回它、docstring 解析读 __doc__，于是同一个 generate_schema 能在从未运行的代码上工作（鸭子类型）。注意 MockFunction.__call__ 故意抛 NotImplementedError——它本就不该被执行。既不编译、不沙箱跑，也不会“每个字段重解析一次”。",
                    "en": "inspect checks no pedigree — it reads attributes. MockFunction.__init__ (letta/functions/functions.py) sets __name__, __doc__, and __signature__; once __signature__ is set explicitly, inspect.signature(mock) returns it and docstring parsing reads __doc__, so the same generate_schema works on never-run code (duck typing). Notably MockFunction.__call__ raises NotImplementedError — it is never meant to execute. Nothing is compiled, sandbox-run, or re-parsed per field.",
                },
            },
            {
                "q": {
                    "zh": "用户上传的源码里定义了三个函数：先是两个辅助函数，最后才是真正的工具。哪个会成为工具？这个判断需要“运行”什么吗？",
                    "en": "A user's uploaded source defines three functions: two helpers first, then the actual tool. Which one becomes the tool, and is anything run to decide?",
                },
                "opts": [
                    {"zh": "解析树里最后一个 FunctionDef，纯靠遍历 AST 节点列表选出——不执行任何东西",
                     "en": "The last FunctionDef in the parsed tree, chosen purely by walking the AST node list — nothing is executed"},
                    {"zh": "第一个 FunctionDef，因为解析器惯例取最先定义的那个",
                     "en": "The first FunctionDef, since parsers conventionally take the earliest definition"},
                    {"zh": "哪个函数有 docstring 就取哪个；若有多个有 docstring，源码因有歧义被拒",
                     "en": "Whichever function has a docstring; if several do, the source is rejected as ambiguous"},
                    {"zh": "名字与 tool name 参数相符的那个，通过 import 模块来确定",
                     "en": "The one whose name matches the tool name argument, resolved by importing the module"},
                ],
                "answer": 0,
                "why": {
                    "zh": "_parse_function_from_source 用 ast.walk 收集 ast.FunctionDef 节点，取最后一个（[-1]）——约定是“工具就是文件里最后定义的那个函数”。这是对 AST 节点的静态读取，不跑任何代码。它明确不是第一个、也不是“有 docstring 的那个”（被选中的函数要求有 docstring，但选择靠位置），更不会为匹配名字去 import。",
                    "en": "_parse_function_from_source collects ast.FunctionDef nodes via ast.walk and takes the last one ([-1]) — the convention is “the tool is the last function defined in the file.” This is a static read of the AST nodes; nothing runs. It is explicitly NOT the first function, and not “the one with a docstring” (a docstring is required on the chosen function, but selection is by position), and nothing is imported to match names.",
                },
            },
            {
                "q": {
                    "zh": "你创建一个 source_type 为 typescript 的工具，却没传 json_schema，指望 Letta 像对 Python 那样替你自动派生。结果如何？",
                    "en": "You create a tool whose source_type is typescript but pass no json_schema, expecting Letta to auto-derive it the way it does for Python. What happens?",
                },
                "opts": [
                    {"zh": "创建失败：ToolCreate.validate_typescript_requires_schema 抛 ValueError——TypeScript 工具必须显式提供 json_schema",
                     "en": "Creation fails: ToolCreate.validate_typescript_requires_schema raises ValueError — a TypeScript tool must supply an explicit json_schema"},
                    {"zh": "和 Python 一样照常工作：derive_typescript_json_schema 通过 AST 从源码生成完整 schema",
                     "en": "It works just like Python: derive_typescript_json_schema produces a complete schema from the source via the AST"},
                    {"zh": "它静默地用一份空的 parameters schema 建出工具，模型靠猜来填参数",
                     "en": "It silently creates the tool with an empty parameters schema, and the model fills arguments by guessing"},
                    {"zh": "它先把 TypeScript 转译成 Python，再走普通的 AST 派生",
                     "en": "It transpiles the TypeScript to Python first, then runs the normal AST derivation"},
                ],
                "answer": 0,
                "why": {
                    "zh": "TS 工具是“自动派生”的例外。ToolCreate.validate_typescript_requires_schema 会拒绝没有 json_schema 的 typescript 源码（ValueError），所以便利的自动派生主要服务 Python。derive_typescript_json_schema 确实存在，但它基于正则、较粗放（union/any → string），并非 AST，也没有 TS→Python 转译这一步。schema 不会被静默置空；缺显式 json_schema 时创建直接失败。",
                    "en": "TS tools are the exception to auto-derivation. ToolCreate.validate_typescript_requires_schema rejects a typescript source with no json_schema (ValueError), so the convenient auto-derive path mainly serves Python. derive_typescript_json_schema does exist, but it is regex-based and coarse (union/any → string), not AST, and there is no TS→Python transpile step. The schema is not silently emptied; creation simply fails until you pass an explicit json_schema.",
                },
            },
            {
                "q": {
                    "zh": "你想读 MockFunction 的定义，它在哪个文件里？",
                    "en": "You want to read MockFunction's definition. Which file holds it?",
                },
                "opts": [
                    {"zh": "letta/functions/functions.py——和 derive_openai_json_schema、_parse_function_from_source 在一起",
                     "en": "letta/functions/functions.py — alongside derive_openai_json_schema and _parse_function_from_source"},
                    {"zh": "letta/functions/ast_parsers.py——因为它属于 AST 解析辅助",
                     "en": "letta/functions/ast_parsers.py — since it is part of the AST-parsing helpers"},
                    {"zh": "letta/functions/typescript_parser.py——它被 Python 和 TypeScript 派生共用",
                     "en": "letta/functions/typescript_parser.py — it is shared by both Python and TypeScript derivation"},
                    {"zh": "letta/services/tool_schema_generator.py——挨着创建期接线",
                     "en": "letta/services/tool_schema_generator.py — next to the creation-time wiring"},
                ],
                "answer": 0,
                "why": {
                    "zh": "MockFunction 住在 letta/functions/functions.py，和派生三件套 derive_openai_json_schema、_parse_function_from_source 在一起。ast_parsers.py 是常见的坑——它放的是 get_function_name_and_docstring、resolve_type（白名单，allow_unsafe_eval=False）等 AST 辅助，但没有 MockFunction。typescript_parser.py 负责基于正则的 TS 派生；tool_schema_generator.py 放的是 generate_schema_for_tool_creation（创建期分派）——都不是 MockFunction。",
                    "en": "MockFunction lives in letta/functions/functions.py, together with the deriver trio derive_openai_json_schema and _parse_function_from_source. ast_parsers.py is a common trap — it holds AST helpers like get_function_name_and_docstring and resolve_type (whitelist, allow_unsafe_eval=False), but NOT MockFunction. typescript_parser.py handles regex-based TS derivation; tool_schema_generator.py holds generate_schema_for_tool_creation (the creation-time dispatch), not MockFunction.",
                },
            },
        ],
        "open": [
            {
                "zh": "用“不拆封验货”这个比喻，把第 18 课的故事完整讲一遍，并想三件事：(1) 为什么 Letta 宁可“读源码”也绝不“import 跑一下”？若把 import 换成“先丢进沙箱再 import”，省下的麻烦和新增的风险各是什么？(2) MockFunction 只凑齐 __name__/__doc__/__signature__ 三个属性，却故意让 __call__ 抛 NotImplementedError。为什么“能被内省”和“不能被调用”要同时成立——这对一个“假函数”意味着怎样的设计取舍？(3) Python 工具能在创建时自动派生 schema，TypeScript 工具却必须显式带上 json_schema。若让你把“自动派生”也扩到 TypeScript，你会选 AST 式解析器还是继续用正则——如何权衡“覆盖更多语法”与“猜错复杂类型”的风险？",
                "en": "Use the “inspect without unsealing” metaphor to tell lesson 18's story as a whole, and think through three things: (1) Why does Letta insist on “reading the source” and never “just import to run it”? If you swapped import for “sandbox it first, then import,” what trouble would you save and what new risk would you add? (2) MockFunction gathers only the three attributes __name__/__doc__/__signature__, yet deliberately makes __call__ raise NotImplementedError. Why should “introspectable” and “not callable” hold at the same time — and what design trade-off does that imply for a “fake function”? (3) Python tools can auto-derive a schema at creation, but TypeScript tools must bring an explicit json_schema. If you had to extend “auto-derivation” to TypeScript too, would you pick an AST-style parser or stay with regex — how would you weigh “covering more syntax” against the risk of “guessing complex types wrong”?",
            },
        ],
    },
    "19-tool-dispatch-and-mcp.html": {
        "mcq": [
            {
                "q": {
                    "zh": "模型吐出一个工具调用后，agent 循环真正调用的“执行入口”是谁？ToolExecutorFactory 在其中扮演什么角色？",
                    "en": "After the model emits a tool call, which “execution entry” does the agent loop actually call? And what role does ToolExecutorFactory play?",
                },
                "opts": [
                    {"zh": "真入口是 ToolExecutionManager.execute_tool_async：它用工厂拿到执行器，再负责计时、超长截断、把异常包成 ToolExecutionResult。工厂只“按 ToolType 选执行器”，本身不运行工具",
                     "en": "The real entry is ToolExecutionManager.execute_tool_async: it uses the factory to obtain an executor, then handles timing, over-length truncation, and wrapping exceptions into a ToolExecutionResult. The factory only “picks an executor by ToolType” and does not run the tool itself"},
                    {"zh": "工厂 ToolExecutorFactory.get_executor 既选执行器又直接运行工具，循环调它就够了",
                     "en": "The factory ToolExecutorFactory.get_executor both picks the executor and runs the tool directly, so the loop just calls it"},
                    {"zh": "循环直接调用具体执行器的 execute()，中间没有任何管理器层",
                     "en": "The loop calls a concrete executor's execute() directly, with no intermediate manager layer"},
                    {"zh": "模型自己通过网络把工具调用发给执行器，服务端只负责转发结果",
                     "en": "The model itself sends the tool call to the executor over the network, and the server only relays the result"},
                ],
                "answer": 0,
                "why": {
                    "zh": "第 19 课的关键分层：ToolExecutorFactory（tool_execution_manager.py）只做“选人”——按 tool.tool_type 查 _executor_map、返回一个执行器实例；真正被循环调用的入口是同一文件的 ToolExecutionManager.execute_tool_async，它先用工厂取执行器，再统一计时、按 return_char_limit 截断、把异常包成 ToolExecutionResult。所以“工厂＝入口”是常见误区：工厂不运行工具，管理器才是入口。",
                    "en": "Lesson 19's key layering: ToolExecutorFactory (tool_execution_manager.py) only “picks the person” — it looks up _executor_map by tool.tool_type and returns an executor instance; the entry the loop actually calls is ToolExecutionManager.execute_tool_async in the same file, which first gets the executor from the factory, then uniformly times the call, truncates by return_char_limit, and wraps exceptions into a ToolExecutionResult. So “factory = entry” is a common trap: the factory doesn't run the tool; the manager is the entry.",
                },
            },
            {
                "q": {
                    "zh": "你注册了一个自己写的 Python 工具 calculate_invoice，没有把它归到任何内置类别。它默认会被哪个执行器执行？为什么？",
                    "en": "You register a Python tool you wrote yourself, calculate_invoice, without sorting it into any built-in category. Which executor runs it by default, and why?",
                },
                "opts": [
                    {"zh": "SandboxToolExecutor。它的类型默认是 custom，而 custom 不在工厂 _executor_map 里——get_executor 的 .get(tool_type, SandboxToolExecutor) 会兜底返回沙箱执行器",
                     "en": "SandboxToolExecutor. Its type defaults to custom, and custom is not in the factory's _executor_map — get_executor's .get(tool_type, SandboxToolExecutor) falls back to the sandbox executor"},
                    {"zh": "LettaCoreToolExecutor，因为所有没有特别归类的工具都按“核心工具”在进程内直跑",
                     "en": "LettaCoreToolExecutor, since any tool not specially categorized runs in-process as a “core tool”"},
                    {"zh": "LettaBuiltinToolExecutor，自定义函数被当作内置工具处理",
                     "en": "LettaBuiltinToolExecutor, treating a custom function as a built-in tool"},
                    {"zh": "创建会失败，因为工厂里没有 custom 对应的执行器，无法分发",
                     "en": "Creation fails, because the factory has no executor mapped for custom, so it can't be dispatched"},
                ],
                "answer": 0,
                "why": {
                    "zh": "schema 层默认 tool_type=CUSTOM（custom 不会被 upsert_base_tools_async 按名字归类）。工厂 ToolExecutorFactory._executor_map 显式登记 7 条、落到 5 个执行器类（LETTA_CORE/LETTA_MEMORY_CORE/LETTA_SLEEPTIME_CORE→LettaCore、LETTA_MULTI_AGENT_CORE→Sandbox、LETTA_BUILTIN→LettaBuiltin、LETTA_FILES_CORE→LettaFile、EXTERNAL_MCP→ExternalMCP），custom 不在其中；get_executor 用 _executor_map.get(tool_type, SandboxToolExecutor) 兜底，所以自定义工具默认进沙箱。它不会失败——兜底正是为这种情况设计的。",
                    "en": "At the schema layer tool_type defaults to CUSTOM (custom is not name-sorted by upsert_base_tools_async). The factory ToolExecutorFactory._executor_map wires 7 entries explicitly onto 5 executor classes (LETTA_CORE/LETTA_MEMORY_CORE/LETTA_SLEEPTIME_CORE→LettaCore, LETTA_MULTI_AGENT_CORE→Sandbox, LETTA_BUILTIN→LettaBuiltin, LETTA_FILES_CORE→LettaFile, EXTERNAL_MCP→ExternalMCP), and custom is not among them; get_executor falls back via _executor_map.get(tool_type, SandboxToolExecutor), so a custom tool goes to the sandbox by default. It does not fail — the fallback exists precisely for this case.",
                },
            },
            {
                "q": {
                    "zh": "一个 external_mcp 类型的工具被调用时，它的代码是在 Letta 的本地沙箱里跑的吗？执行路径大致是怎样的？",
                    "en": "When a tool of type external_mcp is called, does its code run inside Letta's local sandbox? Roughly what is the execution path?",
                },
                "opts": [
                    {"zh": "不在沙箱。ExternalMCPToolExecutor 从 mcp:&lt;server&gt; 标签解析出服务器名，交给 MCPManager().execute_mcp_server_tool 连接外部 MCP server（connect → execute → cleanup），Letta 本地不跑任何工具代码",
                     "en": "Not in the sandbox. ExternalMCPToolExecutor parses the server name from the mcp:&lt;server&gt; tag and hands it to MCPManager().execute_mcp_server_tool, which connects to the external MCP server (connect → execute → cleanup); Letta runs no tool code locally"},
                    {"zh": "在沙箱里跑。所有“外部代码”都被当作不可信代码，统一丢进 SandboxToolExecutor 隔离执行",
                     "en": "It runs in the sandbox. All “external code” is treated as untrusted and uniformly thrown into SandboxToolExecutor for isolated execution"},
                    {"zh": "在 Letta 进程内直跑，和 core_memory_append 一样，以求最低延迟",
                     "en": "It runs in-process inside Letta, just like core_memory_append, for the lowest latency"},
                    {"zh": "Letta 把工具源码下载到本地，import 后在受限解释器里执行",
                     "en": "Letta downloads the tool's source locally and executes it in a restricted interpreter after importing it"},
                ],
                "answer": 0,
                "why": {
                    "zh": "MCP 有两个反直觉点：①不走沙箱——ExternalMCPToolExecutor（mcp_tool_executor.py）连接的是外部 MCP server，本地不跑工具代码；②每次开新连接——MCPManager.execute_mcp_server_tool 走 connect → execute → cleanup，不复用连接。真正的传输客户端在 services/mcp/（stdio/sse/streamable_http），functions/mcp_client/ 只放配置类型。沙箱是用来隔离“在你机器上跑的陌生代码”的，而 MCP 的代码根本不在你机器上跑。",
                    "en": "MCP has two counterintuitive points: (1) no sandbox — ExternalMCPToolExecutor (mcp_tool_executor.py) connects to an external MCP server and runs no tool code locally; (2) a fresh connection each time — MCPManager.execute_mcp_server_tool goes connect → execute → cleanup with no connection reuse. The real transport clients live in services/mcp/ (stdio/sse/streamable_http); functions/mcp_client/ holds only config types. The sandbox exists to isolate “unfamiliar code running on your machine,” but MCP's code never runs on your machine at all.",
                },
            },
            {
                "q": {
                    "zh": "agent 调用 core_memory_append 改写核心记忆时，是哪个执行器在执行它？在哪种运行时里跑？",
                    "en": "When an agent calls core_memory_append to rewrite core memory, which executor runs it, and in what runtime?",
                },
                "opts": [
                    {"zh": "LettaCoreToolExecutor，在 Letta 进程内直跑。core_memory_append 的类型是 letta_memory_core，工厂把 LETTA_MEMORY_CORE 也映射到 LettaCoreToolExecutor——记忆工具不进沙箱",
                     "en": "LettaCoreToolExecutor, in-process inside Letta. core_memory_append has type letta_memory_core, and the factory maps LETTA_MEMORY_CORE to LettaCoreToolExecutor too — memory tools do not go to the sandbox"},
                    {"zh": "SandboxToolExecutor，因为任何“写状态”的工具都必须先隔离，避免污染服务端内存",
                     "en": "SandboxToolExecutor, because any “state-writing” tool must be isolated first to avoid polluting server memory"},
                    {"zh": "有一个专门的 LettaMemoryToolExecutor 处理所有记忆工具",
                     "en": "A dedicated LettaMemoryToolExecutor handles all memory tools"},
                    {"zh": "LettaBuiltinToolExecutor，记忆改写被当作内置实用工具处理",
                     "en": "LettaBuiltinToolExecutor, treating memory edits as a built-in utility"},
                ],
                "answer": 0,
                "why": {
                    "zh": "工厂 _executor_map 把 LETTA_CORE 和 LETTA_MEMORY_CORE（还有 LETTA_SLEEPTIME_CORE）都映射到同一个 LettaCoreToolExecutor（core_tool_executor.py），它把 core、记忆、sleeptime 三摊工具全在进程内直跑——所以 core_memory_append 在进程内执行、延迟最低，不绕沙箱。没有单独的“Memory”执行器；记忆工具也不会因为“写状态”被丢进沙箱。",
                    "en": "The factory's _executor_map maps LETTA_CORE and LETTA_MEMORY_CORE (and LETTA_SLEEPTIME_CORE) all to the same LettaCoreToolExecutor (core_tool_executor.py), which runs core, memory, and sleeptime tools all in-process — so core_memory_append executes in-process at the lowest latency, with no sandbox detour. There is no separate “Memory” executor, and memory tools are not sandboxed for “writing state.”",
                },
            },
            {
                "q": {
                    "zh": "ToolType 共有 11 种，但工厂只有 5 个执行器类；_executor_map 只显式接线了其中一部分类型。像 custom、letta_voice_sleeptime_core、以及弃用的 external_langchain/external_composio 这些没进表的类型，会怎样被执行？",
                    "en": "ToolType has 11 values, but there are only 5 executor classes; _executor_map wires only some of those types explicitly. Types not in the table — like custom, letta_voice_sleeptime_core, and the deprecated external_langchain/external_composio — how do they get executed?",
                },
                "opts": [
                    {"zh": "全部兜底走 SandboxToolExecutor——get_executor 用 _executor_map.get(tool_type, SandboxToolExecutor)，凡是没在表里的类型一律落到沙箱。这是“默认安全”：除非明确认定安全，否则隔离",
                     "en": "They all fall back to SandboxToolExecutor — get_executor uses _executor_map.get(tool_type, SandboxToolExecutor), so any type not in the table lands in the sandbox. This is “secure by default”: isolate unless explicitly judged safe"},
                    {"zh": "工厂会抛 KeyError，这些类型的工具无法被执行",
                     "en": "The factory raises KeyError, and tools of those types cannot be executed"},
                    {"zh": "每种类型都有一个同名执行器，只是没写进 _executor_map，运行时按命名约定动态加载",
                     "en": "Each type has a same-named executor that's simply omitted from _executor_map and loaded dynamically by naming convention at runtime"},
                    {"zh": "它们回退到 LettaCoreToolExecutor，在进程内直跑",
                     "en": "They fall back to LettaCoreToolExecutor and run in-process"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这正是本课最大的“陷阱”：_executor_map 显式接线了 7 个条目（LETTA_CORE、LETTA_MEMORY_CORE、LETTA_SLEEPTIME_CORE → LettaCore；LETTA_MULTI_AGENT_CORE → Sandbox；LETTA_BUILTIN、LETTA_FILES_CORE、EXTERNAL_MCP），映射到 5 个执行器类。其余 4 种没进表的类型（custom、letta_voice_sleeptime_core、external_langchain、external_composio）靠 get_executor 的 .get(tool_type, SandboxToolExecutor) 兜底走沙箱。注意 letta_multi_agent_core 也在沙箱跑，但它是被显式映射的，不是兜底。彩蛋：ExternalComposioToolExecutor 这个类存在却没被接线（external_composio 弃用、兜底沙箱），是永远不会被选中的死代码。既不会 KeyError，也没有“按命名动态加载”。",
                    "en": "This is the lesson's biggest trap: _executor_map wires 7 entries explicitly (LETTA_CORE, LETTA_MEMORY_CORE, LETTA_SLEEPTIME_CORE → LettaCore; LETTA_MULTI_AGENT_CORE → Sandbox; LETTA_BUILTIN, LETTA_FILES_CORE, EXTERNAL_MCP) onto just 5 executor classes. The other 4 unlisted types (custom, letta_voice_sleeptime_core, external_langchain, external_composio) fall through to the sandbox via get_executor's .get(tool_type, SandboxToolExecutor). Note letta_multi_agent_core also runs in the sandbox, but by an explicit mapping, not the fallback. Easter egg: the class ExternalComposioToolExecutor exists but is never wired up (external_composio is deprecated and falls back to the sandbox) — dead code that can never be selected. There is no KeyError and no “dynamic load by name.”",
                },
            },
        ],
        "open": [
            {
                "zh": "用“医院分诊台”这个比喻，把第 19 课的执行链路完整讲一遍，并想三件事：(1) ToolType + 工厂这套“按类型分发”的设计，和“在循环里写一长串 if/elif 判断该怎么跑”相比，好在哪？日后新增一种工具类型、或想把某类工具从沙箱挪到进程内，各要改哪里？(2) 自定义工具“默认兜底沙箱”是“默认安全”，可它也意味着一个忘了归类的内置工具会悄悄变慢（多绕一层沙箱）。这个“安全 vs 性能”的默认你怎么权衡？要不要在“落到兜底”时打一条告警日志？(3) MCP 不走沙箱、每次现连现断，把“运行第三方代码”的风险留在外部 server。对比“本地沙箱跑自定义代码”，这两种扩展能力的方式在信任边界、延迟、故障模式上各有什么不同？什么场景该选哪种？",
                "en": "Use the “hospital triage desk” metaphor to tell lesson 19's execution chain as a whole, and think through three things: (1) Compared with “writing a long if/elif in the loop to decide how to run,” what's better about the ToolType + factory “dispatch by type” design? To add a new tool type later, or to move some class of tool from the sandbox to in-process, what would you change in each case? (2) “Custom defaults to the sandbox” is secure by default, but it also means a built-in tool someone forgot to categorize silently gets slower (one extra sandbox hop). How would you weigh this “safety vs performance” default — would you log a warning whenever execution “hits the fallback”? (3) MCP skips the sandbox and connects/disconnects per call, leaving the risk of “running third-party code” on the external server. Compared with “running custom code in a local sandbox,” how do these two ways of extending capability differ in trust boundary, latency, and failure modes — and when would you pick each?",
            },
        ],
    },
    "20-tool-sandbox-security.html": {
        "mcq": [
            {
                "q": {
                    "zh": "服务端把 agent_state 送进沙箱时用的是哪种序列化？为什么这个方向用 pickle 是安全的？",
                    "en": "When the server sends agent_state into the sandbox, which serialization does it use, and why is pickle safe in this direction?",
                },
                "opts": [
                    {"zh": "用 pickle：被反序列化的 agent_state 是服务端自己造的可信对象，沙箱只负责 pickle.loads。数据从高信任流向低信任沙箱、权限在收窄，不存在“反序列化不可信输入”的问题",
                     "en": "pickle: the agent_state being deserialized is a trusted object the server built itself, and the sandbox only pickle.loads it. Data flows from high trust down into the low-trust sandbox, so privilege narrows and there is no “deserializing untrusted input” problem"},
                    {"zh": "用 JSON：所有跨沙箱边界的数据都必须是 JSON，pickle 在任何方向都被禁止",
                     "en": "JSON: all data crossing the sandbox boundary must be JSON, and pickle is forbidden in every direction"},
                    {"zh": "用 pickle，但只是因为快——agent_state 太大，JSON 编不动，和信任方向无关",
                     "en": "pickle, but only because it is fast — agent_state is too big for JSON, and it has nothing to do with trust direction"},
                    {"zh": "调用参数和 agent_state 都用 pickle 一起打包送进去，沙箱再统一 loads",
                     "en": "both the call arguments and agent_state are pickled together and sent in, and the sandbox loads them all at once"},
                ],
                "answer": 0,
                "why": {
                    "zh": "server→sandbox 走 pickle 是有意的受信方向：agent_state 由服务端 pickle.dumps，沙箱里 pickle.loads 还原。因为被反序列化的字节来源可信（服务端自己造的），且权限往低信任侧流，pickle.loads 不会变成攻击面。注意区分：整段脚本里只有 agent_state 用 pickle；调用参数是按 repr() 内联的字面量，不是 pickle。说“任何方向都禁 pickle”是错的——被禁的是回程（sandbox→server）。",
                    "en": "server→sandbox uses pickle as a deliberate trusted direction: agent_state is pickle.dumps'd by the server and pickle.loads'd back inside the sandbox. Because the deserialized bytes come from a trusted source (the server built them) and privilege flows toward the low-trust side, pickle.loads never becomes an attack surface. Note the distinction: in the whole script only agent_state uses pickle; call arguments are inlined literals via repr(), not pickle. “Forbid pickle in every direction” is wrong — what is forbidden is the return leg (sandbox→server).",
                },
            },
            {
                "q": {
                    "zh": "为什么沙箱回传给服务端的结果必须用 JSON 读，而绝不能 pickle.loads？",
                    "en": "Why must the result the sandbox sends back to the server be read as JSON, and never pickle.loads'd?",
                },
                "opts": [
                    {"zh": "因为沙箱刚执行过不可信的用户代码，它的 stdout 是不可信输出。pickle.loads 会在反序列化时执行任意代码——对沙箱输出 pickle.loads 等于一个服务端 RCE；json.loads 最坏只是拿到假数据",
                     "en": "Because the sandbox just ran untrusted user code, so its stdout is untrusted output. pickle.loads executes arbitrary code during deserialization — pickle.loads on the sandbox output is a server-side RCE; json.loads at worst yields fake data"},
                    {"zh": "因为 JSON 比 pickle 快，回程数据量大，必须用最快的格式",
                     "en": "Because JSON is faster than pickle, and the return data is large, so the fastest format is required"},
                    {"zh": "因为沙箱里没装 pickle 模块，只能用 JSON 编码结果",
                     "en": "Because the sandbox has no pickle module installed, so it can only encode results as JSON"},
                    {"zh": "因为 agent_state 已经在去程用过 pickle 了，回程不能重复用同一种格式",
                     "en": "Because agent_state already used pickle on the way in, and the return trip cannot reuse the same format"},
                ],
                "answer": 0,
                "why": {
                    "zh": "回程是不可信方向：沙箱刚跑完陌生人的工具代码，它写到 stdout 的每个字节都可疑。pickle.loads 在反序列化时执行任意代码，一个恶意工具只要返回带 __reduce__ 的对象，服务端 pickle.loads 的瞬间就被 RCE。改用 json.loads，这类对象根本无法表达，最坏只是解析到假数据。这和“快不快”“装没装模块”都无关——纯粹是信任边界问题。这也正是 PR #3343 修复的点。",
                    "en": "The return leg is the untrusted direction: the sandbox just ran a stranger's tool code, so every byte it writes to stdout is suspect. pickle.loads executes arbitrary code during deserialization — a malicious tool need only return an object carrying a __reduce__, and the instant the server pickle.loads it, it is RCE'd. With json.loads such objects cannot even be expressed, so the worst case is parsing fake data. This has nothing to do with speed or installed modules — it is purely a trust-boundary issue, and exactly what PR #3343 fixed.",
                },
            },
            {
                "q": {
                    "zh": "回程帧里的 marker + 长度 + MD5 解决的是哪一类问题？",
                    "en": "What class of problem does the return frame's marker + length + MD5 solve?",
                },
                "opts": [
                    {"zh": "结果通道被污染：用户工具能往 stdout 打任何东西（调试 print、异常栈、甚至伪造的假结果）。marker 在噪声里定位真 payload、长度精确切片、MD5 抓篡改/截断，三层叠起来保证读到的就是工具真正返回的那份",
                     "en": "The result channel being polluted: a user tool can print anything to stdout (debug prints, stack traces, even a forged fake result). The marker locates the real payload amid the noise, the length slices it precisely, and MD5 catches tampering/truncation — three layers ensuring what is read is exactly what the tool actually returned"},
                    {"zh": "把 pickle 升级成加密格式，防止 agent_state 在去程被沙箱偷看",
                     "en": "Upgrading pickle to an encrypted format to stop the sandbox from peeking at agent_state on the way in"},
                    {"zh": "压缩 stdout，避免大结果占用太多带宽",
                     "en": "Compressing stdout to keep large results from using too much bandwidth"},
                    {"zh": "替代 JSON 解析，让服务端可以直接 pickle.loads 沙箱输出",
                     "en": "Replacing JSON parsing so the server can pickle.loads the sandbox output directly"},
                ],
                "answer": 0,
                "why": {
                    "zh": "stdout 是条嘈杂的河：调试输出、异常栈、甚至用户故意打的假结果/假 marker 都混在里面。三层各司其职——marker（uuid5 的 16 字节）在噪声里定位真 payload 起点；length（4 字节 big-endian '&gt;I'）精确切出 payload；MD5（32 hex）抓篡改与截断，不符就 raise Exception(\"Function ran, but output is corrupted.\")。它防的是完整性/伪造，和加密、压缩无关；更不是为了让服务端去 pickle.loads——恰恰相反，校验通过后只 json.loads。",
                    "en": "stdout is a noisy river: debug output, stack traces, even a fake result/fake marker a user deliberately prints are all mixed in. The three layers each do a job — marker (uuid5's 16 bytes) locates the real payload's start amid the noise; length (4 bytes big-endian '&gt;I') slices the payload precisely; MD5 (32 hex) catches tampering and truncation, raising Exception(\"Function ran, but output is corrupted.\") on mismatch. It defends integrity/forgery, unrelated to encryption or compression; and it is certainly not there to let the server pickle.loads — on the contrary, once verified, only json.loads runs.",
                },
            },
            {
                "q": {
                    "zh": "PR #3343（commit 1131535）到底改了什么？哪些是它没动的？",
                    "en": "What exactly did PR #3343 (commit 1131535) change, and what did it leave untouched?",
                },
                "opts": [
                    {"zh": "它只把 sandbox→server 的 payload 编码从 pickle 换成 JSON，于是服务端读回从 pickle.loads 变成 json.loads，消除 RCE 面。marker+长度+MD5 帧早就存在、不是它加的；server→sandbox 仍 pickle agent_state，是有意保留的受信方向",
                     "en": "It only switched the sandbox→server payload encoding from pickle to JSON, so the server's read-back changed from pickle.loads to json.loads, eliminating the RCE surface. The marker+length+MD5 frame already existed and was not added by it; server→sandbox still pickles agent_state, the intentionally kept trusted direction"},
                    {"zh": "它新增了 marker+长度+MD5 帧，在此之前回程根本没有任何完整性校验",
                     "en": "It added the marker+length+MD5 frame; before it, the return leg had no integrity check at all"},
                    {"zh": "它把去程的 agent_state 也从 pickle 改成 JSON，彻底禁用了 pickle",
                     "en": "It also switched the inbound agent_state from pickle to JSON, banning pickle entirely"},
                    {"zh": "它把本地沙箱换成 E2B，用云端隔离替代了进程隔离",
                     "en": "It replaced the local sandbox with E2B, swapping cloud isolation for process isolation"},
                ],
                "answer": 0,
                "why": {
                    "zh": "#3343 的范围很窄但很关键：只改回程 payload 的编码（pickle→JSON），落点在 tool_parser_helper.py——服务端从 pickle.loads(沙箱字节) 变成 json.loads(payload)，结构性消除了服务端 RCE。它没动的：①marker+长度+MD5 帧本就存在（负责完整性，不是 #3343 引入）；②server→sandbox 仍 pickle agent_state（受信方向，有意保留，不是漏改）。说它“加了帧”“禁用了所有 pickle”“换成 E2B”都把范围搞错了。一句话：帧管完整性、编码格式管安全性，#3343 动的是后者。",
                    "en": "#3343's scope is narrow but pivotal: it changes only the return payload's encoding (pickle→JSON), landing in tool_parser_helper.py — the server goes from pickle.loads(sandbox bytes) to json.loads(payload), structurally eliminating the server RCE. What it left alone: (1) the marker+length+MD5 frame already existed (it handles integrity and was not introduced by #3343); (2) server→sandbox still pickles agent_state (the trusted direction, kept on purpose, not an oversight). Saying it “added the frame,” “banned all pickle,” or “switched to E2B” all misstate the scope. In one line: the frame governs integrity, the encoding governs security, and #3343 moved the latter.",
                },
            },
            {
                "q": {
                    "zh": "在 v0.16.8 里，沙箱实际执行的那段脚本是由 letta/templates/sandbox_code_file.py.j2 模板渲染出来的吗？",
                    "en": "In v0.16.8, is the script the sandbox actually runs rendered from the letta/templates/sandbox_code_file.py.j2 template?",
                },
                "opts": [
                    {"zh": "不是。那个 .j2 模板在 v0.16.8 没有被任何 .py 引用，只能当对照参考；真实脚本是 tool_sandbox/base.py 里 generate_execution_script / _render_sandbox_code 用字符串拼出来的",
                     "en": "No. That .j2 template is not referenced by any .py in v0.16.8 and only serves as a side reference; the real script is string-assembled by generate_execution_script / _render_sandbox_code in tool_sandbox/base.py"},
                    {"zh": "是的，Jinja2 在运行时渲染该模板，把 agent_state 和用户源码填进去生成脚本",
                     "en": "Yes, Jinja2 renders that template at runtime, filling in agent_state and the user source to produce the script"},
                    {"zh": "是的，但只有 Modal 沙箱用模板，本地和 E2B 用别的方式",
                     "en": "Yes, but only the Modal sandbox uses the template; local and E2B use other means"},
                    {"zh": "没有脚本——沙箱直接 import 用户的工具模块并调用，不需要拼脚本",
                     "en": "There is no script — the sandbox directly imports the user's tool module and calls it, with no assembling needed"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这是常见误区。letta/templates/sandbox_code_file.py.j2 在 v0.16.8 是死文件——没有任何 .py 引用它，只能当人类对照参考。真实脚本由 tool_sandbox/base.py::AsyncToolSandboxBase.generate_execution_script 调 _render_sandbox_code 用字符串拼出：pickle.loads 还原 agent_state、按 repr() 内联参数、逐字内联用户 source_code、调用并把结果+agent_state 打成 JSON、加 marker+长度+MD5 写 stdout。也别被 docstring（写着“base64-encode/pickle the result”）和带 _pkl 的变量名骗了——都是遗留，实际装 JSON。沙箱也不会 import 用户模块（那模块只存在数据库里），所以必须内联自包含。",
                    "en": "A common trap. letta/templates/sandbox_code_file.py.j2 is dead in v0.16.8 — no .py references it, so it is only a human side reference. The real script is string-assembled by tool_sandbox/base.py::AsyncToolSandboxBase.generate_execution_script via _render_sandbox_code: pickle.loads to restore agent_state, inline arguments via repr(), inline the user's source_code verbatim, call it, pack result+agent_state into JSON, and write marker+length+MD5 to stdout. Do not be fooled by the docstring (which says “base64-encode/pickle the result”) or the _pkl variable name — both are legacy; what is actually carried is JSON. The sandbox also cannot import the user module (it lives only in the database), so the script must be inlined and self-contained.",
                },
            },
        ],
        "open": [
            {
                "zh": "用“监狱探视窗”这个比喻，把第 20 课的“信任边界”完整讲一遍，并想三件事：(1) 为什么 server→sandbox 能放心用 pickle、而 sandbox→server 必须只用 json.loads？把它和“权限放大的方向”联系起来——什么样的通用规则能让你在任何跨边界场景里一眼判断“这里能不能反序列化”？(2) marker+长度+MD5 帧负责“完整性”、JSON 编码负责“安全性”，这是两件事，PR #3343 只改了后者。如果有人只加强了帧（比如把 MD5 换成 SHA-256），却仍然 pickle.loads payload，安全吗？为什么完整性校验救不了一个“会执行代码的解析器”？(3) 本地沙箱和服务端共享内核，隔离只是“够用级”。把同一个自定义工具从本地切到 E2B/Modal，信任边界这张图会变吗？哪些不变（去程 pickle、回程 JSON、帧校验）、哪些变（隔离强度、延迟、回程多包的 base64 或结构化 dict）？",
                "en": "Use the “prison visitation window” metaphor to tell lesson 20's “trust boundary” as a whole, and think through three things: (1) Why can server→sandbox safely use pickle while sandbox→server must use json.loads only? Tie it to “the direction in which privilege widens” — what general rule lets you judge at a glance, in any cross-boundary scenario, whether “deserialization is safe here”? (2) The marker+length+MD5 frame handles “integrity” while the JSON encoding handles “security” — two different things, and PR #3343 only changed the latter. If someone strengthened only the frame (say, swapping MD5 for SHA-256) but still pickle.loads'd the payload, is that safe? Why can't an integrity check save you from “a parser that executes code”? (3) The local sandbox shares the kernel with the server, so its isolation is only “good enough.” If you move the same custom tool from local to E2B/Modal, does the trust-boundary diagram change? What stays the same (inbound pickle, return JSON, the frame check) and what changes (isolation strength, latency, the return's extra base64 or structured dict)?",
            },
        ],
    },
}


def render(fname, lang):
    """Return the self-test HTML block for ``fname`` in ``lang`` ('' if none)."""
    data = QUIZZES.get(fname)
    if not data or not (data.get("mcq") or data.get("open")):
        return ""
    out = ['<div class="selftest">', f'<h2>{_HEAD[lang]}</h2>']
    for i, item in enumerate(data.get("mcq", []), 1):
        shuffled, ans = _shuffle(item["opts"], item["answer"], f"{fname}:{i}")
        opts = "\n".join(f"    <li>{o[lang]}</li>" for o in shuffled)
        letter = chr(65 + ans)
        out.append(
            f'<div class="quiz">\n'
            f'  <div class="qn">{i}. {item["q"][lang]}</div>\n'
            f'  <ol class="opts">\n{opts}\n  </ol>\n'
            f'  <details class="accordion">\n'
            f'    <summary>{_SEE[lang]} <span class="hint">{_CLICK[lang]}</span></summary>\n'
            f'    <div class="acc-body"><div class="qa"><div class="a">'
            f'<strong>{_ANS[lang]}{letter}</strong>{_SEP[lang]}{item["why"][lang]}'
            f"</div></div></div>\n"
            f"  </details>\n"
            f"</div>"
        )
    opens = data.get("open", [])
    if opens:
        lis = "\n".join(f"    <li>{o[lang]}</li>" for o in opens)
        out.append(
            '<div class="card spark">\n'
            f'  <div class="tag">{_OPEN[lang]}</div>\n'
            f"  <ul>\n{lis}\n  </ul>\n"
            "</div>"
        )
    out.append("</div>")
    return "\n".join(out)


def _validate():
    """Fail fast on authoring mistakes in QUIZZES (clear message names the lesson)."""
    for fname, data in QUIZZES.items():
        for qi, item in enumerate(data.get("mcq", []), 1):
            opts = item["opts"]
            if not (0 <= item["answer"] < len(opts)):
                raise ValueError(
                    f"quizzes[{fname!r}] Q{qi}: answer {item['answer']} out of range 0..{len(opts) - 1}"
                )
            for o in opts:
                if not ({"zh", "en"} <= o.keys()):
                    raise ValueError(f"quizzes[{fname!r}] Q{qi}: an option is missing zh/en")
            if not ({"zh", "en"} <= item["q"].keys() and {"zh", "en"} <= item["why"].keys()):
                raise ValueError(f"quizzes[{fname!r}] Q{qi}: q/why missing zh/en")
        for oi, o in enumerate(data.get("open", []), 1):
            if not ({"zh", "en"} <= o.keys()):
                raise ValueError(f"quizzes[{fname!r}] open{oi}: missing zh/en")


_validate()
