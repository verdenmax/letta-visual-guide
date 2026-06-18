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
                "zh": "用“监狱探视窗”这个比喻，把第 20 课的“信任边界”完整讲一遍，并想三件事：(1) 为什么 server→sandbox 能放心用 pickle、而 sandbox→server 必须只用 json.loads？把它和“权限放大的方向”联系起来——什么样的通用规则能让你在任何跨边界场景里一眼判断“这里能不能反序列化”？(2) marker+长度+MD5 帧负责“完整性”、JSON 编码负责“安全性”，这是两件事，PR #3343 只改了后者。如果有人只加强了帧（比如把 MD5 换成 SHA-256），却仍然 pickle.loads payload，安全吗？为什么完整性校验救不了一个“会执行代码的解析器”？(3) 本地沙箱和服务端共享内核，隔离只是“够用级”。把同一个自定义工具从本地切到 E2B/Modal，信任边界这张图会变吗？哪些不变（信任边界原则：去程可信、回程绝不 pickle.loads）、哪些变（隔离强度、延迟，以及回程编码——本地的 marker+MD5 帧 / E2B 的 base64 / Modal 的结构化 dict）？",
                "en": "Use the “prison visitation window” metaphor to tell lesson 20's “trust boundary” as a whole, and think through three things: (1) Why can server→sandbox safely use pickle while sandbox→server must use json.loads only? Tie it to “the direction in which privilege widens” — what general rule lets you judge at a glance, in any cross-boundary scenario, whether “deserialization is safe here”? (2) The marker+length+MD5 frame handles “integrity” while the JSON encoding handles “security” — two different things, and PR #3343 only changed the latter. If someone strengthened only the frame (say, swapping MD5 for SHA-256) but still pickle.loads'd the payload, is that safe? Why can't an integrity check save you from “a parser that executes code”? (3) The local sandbox shares the kernel with the server, so its isolation is only “good enough.” If you move the same custom tool from local to E2B/Modal, does the trust-boundary diagram change? What stays the same (the trust-boundary principle: trusted inbound, never pickle.loads on the way back) and what changes (isolation strength, latency, and the return encoding — local's marker+MD5 frame / E2B's base64 / Modal's structured dict)?",
            },
        ],
    },
    "21-provider-contract.html": {
        "mcq": [
            {
                "q": {
                    "zh": "LLMClient.create 这个工厂，到底是按什么来挑选具体的 client 类的？",
                    "en": "What does the LLMClient.create factory actually use to pick the concrete client class?",
                },
                "opts": [
                    {"zh": "按 llm_config.model_endpoint_type——它是一个 ProviderType 字符串，被传进 create 后用 match/case 匹配；正因为 ProviderType(str, Enum) 本质是字符串，才能直接拿来 match",
                     "en": "By llm_config.model_endpoint_type — a ProviderType string that is passed into create and matched with match/case; because ProviderType(str, Enum) is essentially a string, it can be matched directly"},
                    {"zh": "按整个 LLMConfig 对象做结构匹配，比对里面所有字段后再决定 client",
                     "en": "By structurally matching the whole LLMConfig object, comparing all its fields before deciding the client"},
                    {"zh": "按 model 字段（比如 gpt-4o、claude-3-5-sonnet）的名字前缀来判断",
                     "en": "By the name prefix of the model field (e.g. gpt-4o, claude-3-5-sonnet)"},
                    {"zh": "按 model_endpoint 这个 URL 的域名（比如 api.openai.com）来路由",
                     "en": "By the domain of the model_endpoint URL (e.g. api.openai.com)"},
                ],
                "answer": 0,
                "why": {
                    "zh": "工厂分派只认一个字段：model_endpoint_type。循环把它从 llm_config 里取出来、传进 LLMClient.create，里面对 provider_type 做 match/case 命中具体 client 类。关键细节：ProviderType 是 (str, Enum)，本质就是字符串，所以能直接 match。它分派的不是整个 LLMConfig 对象，也不是 model 名字或 model_endpoint 的 URL——把这些搞混，会以为“换个模型名就换 client”，但实际只有 endpoint 类型才驱动分派。",
                    "en": "The factory dispatches on a single field: model_endpoint_type. The loop pulls it out of llm_config and passes it into LLMClient.create, which runs match/case on provider_type to hit a concrete client class. Key detail: ProviderType is (str, Enum) — essentially a string — so it can be matched directly. It does not dispatch on the whole LLMConfig object, nor on the model name, nor on the model_endpoint URL — confusing these makes you think “change the model name and you change the client”, when in reality only the endpoint type drives the dispatch.",
                },
            },
            {
                "q": {
                    "zh": "openai、ollama、vllm 这些 provider 在 match/case 里大多没有自己的 case 分支。一个 model_endpoint_type 为 ollama 的请求会被分派给哪个 client？",
                    "en": "Providers like openai, ollama and vllm mostly have no case branch of their own in the match/case. Which client does a request with model_endpoint_type = ollama get dispatched to?",
                },
                "opts": [
                    {"zh": "默认的 OpenAIClient——它们统一落到 case _ 兜底分支。这些本地/兼容端点大多提供“OpenAI 兼容”接口，所以同一个 OpenAIClient 只要把请求发到不同的 model_endpoint，就能伺候它们一大票",
                     "en": "The default OpenAIClient — they all fall into the case _ catch-all. These local/compatible endpoints mostly expose an “OpenAI-compatible” interface, so the same OpenAIClient can serve a whole crowd of them just by sending the request to a different model_endpoint"},
                    {"zh": "没有匹配的 client，create 会抛 NotImplementedError，必须先注册一个 OllamaClient",
                     "en": "No matching client; create raises NotImplementedError, and you must first register an OllamaClient"},
                    {"zh": "一个专门的 OllamaClient——每个 provider 名字都对应一个独立的 client 子类",
                     "en": "A dedicated OllamaClient — every provider name maps to its own separate client subclass"},
                    {"zh": "由 LLMConfig.provider_category 二次路由到本地推理专用的 LocalClient",
                     "en": "A secondary route via LLMConfig.provider_category sends it to a local-inference-only LocalClient"},
                ],
                "answer": 0,
                "why": {
                    "zh": "没被显式列出 ≠ 没人管。match/case 的最后一档 case _ 兜底返回 OpenAIClient，于是 openai/ollama/vllm/lmstudio… 全都落到它头上。原因是这些端点大多本就提供“OpenAI 兼容”接口，Letta 只需把请求发到不同的 model_endpoint，同一个 OpenAIClient 就能复用。所以那十几个显式 case 其实是一份“例外名单”——只有行为真跟 OpenAI 不一样的家才单列。它不会抛错，也不是每个名字配一个子类。",
                    "en": "Not listed explicitly ≠ unhandled. The final arm of the match/case, case _, falls back to OpenAIClient, so openai/ollama/vllm/lmstudio… all land on it. The reason is that these endpoints mostly already expose an “OpenAI-compatible” interface, so Letta only has to send the request to a different model_endpoint and the same OpenAIClient is reused. So the dozen-odd explicit cases are really an “exceptions list” — only providers whose behaviour genuinely differs from OpenAI get a separate entry. It does not raise, and it is not one subclass per name.",
                },
            },
            {
                "q": {
                    "zh": "三方法 build_request_data / request_async / convert_response_to_chat_completion 里，哪一个负责把“各家五花八门的原始响应”收敛成统一的 ChatCompletionResponse？",
                    "en": "Among the three methods build_request_data / request_async / convert_response_to_chat_completion, which one collapses “each provider's wildly varied raw response” into the unified ChatCompletionResponse?",
                },
                "opts": [
                    {"zh": "convert_response_to_chat_completion——它是个 async 方法，把这一家的原始响应翻译成 OpenAI 形状的 ChatCompletionResponse；不管底层是 Anthropic 内容块、Google functionCall 还是纯文本，都收敛成同一个类型",
                     "en": "convert_response_to_chat_completion — an async method that translates this provider's raw response into an OpenAI-shaped ChatCompletionResponse; whether the layer below is Anthropic content blocks, Google functionCall or plain text, all collapse into the same type"},
                    {"zh": "build_request_data——它在组请求时就顺手把响应格式也统一好了",
                     "en": "build_request_data — while assembling the request it also unifies the response format in passing"},
                    {"zh": "request_async——它发请求时直接要求各家返回 ChatCompletionResponse 格式",
                     "en": "request_async — when sending the request it directly demands every provider return the ChatCompletionResponse format"},
                    {"zh": "send_llm_request——编排方法自己做格式转换，三方法只管收发",
                     "en": "send_llm_request — the orchestration method does the format conversion itself, while the three methods only send and receive"},
                ],
                "answer": 0,
                "why": {
                    "zh": "收敛形状的是第三个方法 convert_response_to_chat_completion（async）。流水线分工很清楚：build_request_data（同步）知道“这家要什么格式”、request_async（async）只负责发出去并拿回原始 dict、convert 才把原始响应翻成 OpenAI 形状的 ChatCompletionResponse。build 管入口格式、不碰响应；request_async 拿回的是还没统一的原始响应；send_llm_request 只是把三步串起来、并对网络请求那一步兜异常，转换工作委托给 convert。所有 provider 差异都被关进 build 和 convert 这首尾两步。",
                    "en": "The shape-collapsing one is the third method, convert_response_to_chat_completion (async). The pipeline's division of labour is clear: build_request_data (sync) knows “what format this provider wants”, request_async (async) only sends it off and returns the raw dict, and convert is what translates the raw response into an OpenAI-shaped ChatCompletionResponse. build governs the inbound format and never touches the response; request_async returns the still-un-unified raw response; send_llm_request merely strings the three steps together and catches the request step's exceptions, delegating the conversion to convert. All provider differences are locked into the two end steps, build and convert.",
                },
            },
            {
                "q": {
                    "zh": "把一个 agent 的 model_endpoint_type 从 groq 改成 anthropic（或本地 ollama），第 14 课那套执行循环的代码需要跟着改吗？为什么？",
                    "en": "If you change an agent's model_endpoint_type from groq to anthropic (or local ollama), does the execution loop from Lesson 14 need code changes? Why?",
                },
                "opts": [
                    {"zh": "不需要，一行都不用改。循环只递出一个请求、收回一个 ChatCompletionResponse，“这次是哪家”被彻底挡在工厂和三方法里；换 provider 只是换 client 当“主语”，出口形状完全一样，循环全程无感",
                     "en": "No — not a single line. The loop only hands out one request and collects back one ChatCompletionResponse; “which provider this time” is walled off inside the factory and the three methods. Switching providers only changes which client is the “subject”; the exit shape is identical, and the loop feels nothing"},
                    {"zh": "需要，得在循环里加 if model_endpoint_type 为 anthropic 的分支来解析 Anthropic 的内容块",
                     "en": "Yes — you must add an if-model_endpoint_type-is-anthropic branch in the loop to parse Anthropic's content blocks"},
                    {"zh": "需要，因为 Anthropic 的 token 用量字段名和 OpenAI 不同，循环取 usage 的代码要改",
                     "en": "Yes — because Anthropic's token-usage field names differ from OpenAI's, the loop's usage-reading code must change"},
                    {"zh": "不需要改代码，但要手动调用 convert_* 把响应先转一遍，循环才能读",
                     "en": "No code change, but you must manually call convert_* to convert the response first before the loop can read it"},
                ],
                "answer": 0,
                "why": {
                    "zh": "循环看不到底下是哪家——这正是统一契约最直接的红利。从循环视角，它永远只递出一个请求、收回一个 ChatCompletionResponse；换 groq→anthropic→ollama，变的只是三方法里的“主语”（哪个 client），出口形状一字不差，循环代码零改动。Anthropic 的内容块、不同的用量字段，都在该 client 的 build/convert 里被抹平了，不会冒进循环。convert_* 也由 send_llm_request 自动调用、无需手动。一个调试直觉：若循环里出现“if 是不是 anthropic”，多半是抽象漏了。",
                    "en": "The loop cannot see which provider sits below — that is the most direct dividend of a unified contract. From the loop's view it always hands out one request and collects back one ChatCompletionResponse; switching groq→anthropic→ollama only changes the “subject” inside the three methods (which client), while the exit shape is identical and the loop code changes by zero. Anthropic's content blocks and its different usage fields are all smoothed over inside that client's build/convert and never surface in the loop. convert_* is also called automatically by send_llm_request, not by hand. A debugging instinct: if an “if is_anthropic” appears in the loop, the abstraction has probably leaked.",
                },
            },
            {
                "q": {
                    "zh": "本课反复说的“三方法契约”，是 LLMClientBase 的完整抽象方法集合吗？",
                    "en": "Is the “three-method contract” this lesson keeps citing the complete set of abstract methods on LLMClientBase?",
                },
                "opts": [
                    {"zh": "不是。“三方法”是教学化简——LLMClientBase 实际有 8 个 @abstractmethod，另外 5 个是 request（同步）、request_embeddings、stream_async、is_reasoning_model、handle_llm_error；本课只抓 build/request_async/convert 这条“数据形状”主线",
                     "en": "No. “Three methods” is a teaching simplification — LLMClientBase actually has 8 @abstractmethod, the other 5 being request (sync), request_embeddings, stream_async, is_reasoning_model and handle_llm_error; this lesson grabs only the build/request_async/convert “data shape” through-line"},
                    {"zh": "是的，LLMClientBase 恰好只有这 3 个抽象方法，子类实现完就能用",
                     "en": "Yes — LLMClientBase has exactly these 3 abstract methods, and a subclass is usable once it implements them"},
                    {"zh": "不是，实际只有 2 个抽象方法（build 和 convert），request_async 是基类提供的具体实现",
                     "en": "No — there are really only 2 abstract methods (build and convert); request_async is a concrete implementation the base class provides"},
                    {"zh": "不是，共有 12 个抽象方法，多出来的还包括 stream（同步流式）、count_tokens 等",
                     "en": "No — there are 12 abstract methods in total, the extras also including stream (sync streaming), count_tokens and so on"},
                ],
                "answer": 0,
                "why": {
                    "zh": "“三方法”是刻意的教学化简。LLMClientBase 实际声明了 8 个 @abstractmethod：本课主线的 build_request_data / request_async / convert_response_to_chat_completion，加上同步版 request、向量嵌入 request_embeddings、流式 stream_async、推理模型判断 is_reasoning_model、统一错误处理 handle_llm_error。本课只挑那三个，因为它们合起来回答“一次普通对话请求怎么从各家格式收敛成统一形状”。正因为这 8 个都标了 @abstractmethod，子类漏实现任何一个，实例化时就会报错。不是 2 个，也不是 12 个。",
                    "en": "“Three methods” is a deliberate teaching simplification. LLMClientBase actually declares 8 @abstractmethod: this lesson's main-thread build_request_data / request_async / convert_response_to_chat_completion, plus the synchronous request, the vector-embedding request_embeddings, the streaming stream_async, the reasoning-model check is_reasoning_model, and the unified error handling handle_llm_error. The lesson picks only those three because together they answer “how a plain chat request collapses from each provider's format into one unified shape”. Because all 8 are tagged @abstractmethod, a subclass that misses any one errors out at instantiation. It is neither 2 nor 12.",
                },
            },
        ],
        "open": [
            {
                "zh": "用本课的“联合国同声传译”比喻，把第 21 课的“供应商契约”完整讲一遍，并想透三件事：(1) 工厂分派只认 model_endpoint_type 这一个字段（一个 ProviderType 字符串），而不是整个 LLMConfig 对象、也不是 model 名字。为什么“用一个稳定的小字段当路由键”比“比对一大堆字段”更健壮？把它和“加一家供应商、循环零改动”联系起来——什么样的通用设计原则，能让你在任何插件式架构里一眼看出“该拿什么当分派键”？(2) 三方法把 provider 差异全锁进 build（入口格式）和 convert（出口格式）这首尾两步，中间的发送与编排是所有家共用的。如果有人图省事，把“解析 Anthropic 内容块”的逻辑写进了第 14 课的循环里，短期能跑，长期会埋下什么债？为什么说“循环里出现 if 是不是 anthropic”就是抽象漏了的信号？(3) Letta 干脆把 OpenAI 形状设成默认假设（case _ → OpenAIClient），用“也许不完美但人人都懂”换“加 provider 不改循环、加模块不问 provider”。这笔交易的代价是什么（和 OpenAI 形状绑得更紧）？如果哪天出现一个真正更好的新标准，这套抽象帮你把迁移成本压在了哪一层、而不会扩散到记忆/工具/压缩这些模块？",
                "en": "Use this lesson's “UN simultaneous interpretation” metaphor to tell lesson 21's “provider contract” as a whole, and think through three things: (1) The factory dispatches on the single field model_endpoint_type (a ProviderType string), not the whole LLMConfig object and not the model name. Why is “using one stable small field as the routing key” more robust than “comparing a pile of fields”? Tie it to “add a provider, change the loop by zero lines” — what general design principle lets you tell at a glance, in any plug-in architecture, “what to use as the dispatch key”? (2) The three methods lock all provider differences into build (inbound format) and convert (outbound format), while the sending and orchestration in the middle are shared by everyone. If someone took a shortcut and wrote “parse Anthropic content blocks” logic into the Lesson 14 loop, it would run short-term — what debt does it bury long-term? Why is “an if is_anthropic appearing in the loop” a signal that the abstraction has leaked? (3) Letta simply makes the OpenAI shape the default assumption (case _ → OpenAIClient), trading “perhaps imperfect but understood by everyone” for “add a provider without changing the loop, add a module without asking about the provider”. What is the cost of this trade (binding more tightly to the OpenAI shape)? If a genuinely better new standard appeared one day, which single layer does this abstraction confine the migration cost to, so that it does not spread into the memory/tools/compaction modules?",
            },
        ],
    },
    "22-provider-quirks.html": {
        "mcq": [
            {
                "q": {
                    "zh": "当某家 provider 的行为跟 OpenAI 略有不同时，它的 client 子类通常重写哪两个方法？",
                    "en": "When a provider behaves a little differently from OpenAI, which two methods does its client subclass typically override?",
                },
                "opts": [
                    {"zh": "build_request_data + convert_response_to_chat_completion——前者出门时改请求、后者回来时把响应翻成 OpenAI 形状；子类大多是先 super() 拿到标准形状、再就地改几笔 dict",
                     "en": "build_request_data + convert_response_to_chat_completion — the first edits the request on the way out, the second translates the response back into the OpenAI shape; the subclass usually calls super() for the standard shape, then patches a few dict lines in place"},
                    {"zh": "request_async + stream_async——真正负责跟网络通信的那两个方法",
                     "en": "request_async + stream_async — the two methods that actually talk to the network"},
                    {"zh": "__init__ + _prepare_client_kwargs——子类重写构造与连接初始化",
                     "en": "__init__ + _prepare_client_kwargs — the subclass rewrites construction and connection setup"},
                    {"zh": "三方法契约全部，外加工厂 match/case 里那条分支",
                     "en": "All three contract methods, plus the factory's match/case branch"},
                ],
                "answer": 0,
                "why": {
                    "zh": "怪癖只关在首尾两步：build_request_data（改请求）和 convert_response_to_chat_completion（改响应）。XAIClient 删掉两个惩罚字段、GroqClient 把对象形式的 tool_choice 降级成字符串 required，都是 super() 之后改一笔 dict 而已。request_async / stream_async 是各家共用的“发送”管道，不是放差异的地方；_prepare_client_kwargs 已在 OpenAIClient 上把 base_url 设好，这些只改字段的子类根本不碰它；更不必重写整个契约或工厂分支。记住这条纪律：差异进子类的这两个方法，循环之上永远是同一个 ChatCompletionResponse。",
                    "en": "Quirks are caged in just the two end steps: build_request_data (edit request) and convert_response_to_chat_completion (edit response). XAIClient drops two penalty fields, GroqClient down-converts an object-form tool_choice to the string required — each just patches a dict after super(). request_async / stream_async are the shared “send” pipe, not where differences live; _prepare_client_kwargs already sets base_url on OpenAIClient, so these field-tweaking subclasses never touch it; and there is certainly no need to rewrite the whole contract or the factory branch. Remember the discipline: differences go into these two subclass methods, while above the loop it is always the same ChatCompletionResponse.",
                },
            },
            {
                "q": {
                    "zh": "Letta 给一个“只会调函数”的模型模拟内心独白时，这个 thinking 字段被放在每个工具参数的什么位置？是不是可选的？",
                    "en": "When Letta simulates an inner monologue for a model that “only calls functions”, where in each tool's parameters does the thinking field go, and is it optional?",
                },
                "opts": [
                    {"zh": "排在第一个、且是必填——add_inner_thoughts_to_functions 把 thinking 加成第一个 property，再 required.insert(0, key) 把它排到必填项最前；于是模型必须先写完 thinking，才轮到真正的业务参数",
                     "en": "First, and required — add_inner_thoughts_to_functions adds thinking as the first property, then required.insert(0, key) puts it at the front of required; so the model must finish writing thinking before any real business parameter"},
                    {"zh": "排在最后、且可选——追加在真正参数之后，免得打乱它们",
                     "en": "Last, and optional — appended after the real parameters so it doesn't disrupt them"},
                    {"zh": "放在工具调用旁边的一个顶层独立字段里，根本不在 parameters 内",
                     "en": "In a separate top-level field next to the tool call, not inside the parameters at all"},
                    {"zh": "放在 parameters 里哪都行，顺序无所谓，反正模型会整体规划",
                     "en": "Anywhere in the parameters; order doesn't matter because the model plans holistically"},
                ],
                "answer": 0,
                "why": {
                    "zh": "顺序就是一切。LLM 是从左到右按 schema 顺序生成参数的，把 thinking 排在第一个必填字段，等于强迫模型“先写一段推理、再填结构化参数”——先想后调被钉死。helpers.py::add_inner_thoughts_to_functions 两手并用：OrderedDict 让 thinking 当第一个 property，required.insert(0, key) 让它在必填里也排最前。它不是可选的尾巴，也不是 parameters 之外的独立字段。注意 Google 是反例——它把 thinking 追加在最后——但默认/被迫模拟的这条路，永远是排第一。",
                    "en": "Order is everything. An LLM generates parameters left to right in schema order, so making thinking the first required field forces the model to “write a chunk of reasoning, then fill the structured parameters” — think-before-act is nailed down. helpers.py::add_inner_thoughts_to_functions uses both hands: an OrderedDict makes thinking the first property, and required.insert(0, key) puts it first among required too. It is not an optional tail, nor a field outside parameters. Note Google is the counterexample — it appends thinking last — but the default/forced-simulation path always puts it first.",
                },
            },
            {
                "q": {
                    "zh": "哪一个开关决定 Letta 是“注入一段模拟的 thinking”还是“直接用模型的原生推理”？",
                    "en": "Which single switch decides whether Letta injects a simulated thinking parameter or relies on the model's native reasoning?",
                },
                "opts": [
                    {"zh": "LLMConfig.put_inner_thoughts_in_kwargs——普通工具调用模型为 True（注入/模拟），o1/gpt-5/Claude-4 这类原生推理模型为 False（用它们真的 thinking）",
                     "en": "LLMConfig.put_inner_thoughts_in_kwargs — True for plain tool-calling models (inject/simulate), False for native-reasoning models like o1/gpt-5/Claude-4 (use their real thinking)"},
                    {"zh": "is_reasoning_model——循环每一步都重新算一遍的一个布尔值",
                     "en": "is_reasoning_model — a per-request boolean the loop recomputes each step"},
                    {"zh": "INNER_THOUGHTS_KWARG——那个存着字符串 “thinking” 的设置项",
                     "en": "INNER_THOUGHTS_KWARG — the setting that holds the string “thinking”"},
                    {"zh": "LLMClient.create 里的 match/case——它把推理模型路由到另一个 client",
                     "en": "The match/case in LLMClient.create — it routes reasoning models to a different client"},
                ],
                "answer": 0,
                "why": {
                    "zh": "决定权在 put_inner_thoughts_in_kwargs 这一个开关：为 True 就注入一段模拟独白（模型自己不会想），为 False 就退场、直接用模型真正的 reasoning（o1/o3/gpt-5、Claude 3.7/4、ZAI GLM 等）。名字本身就是答案——“把内心独白放进 kwargs（工具参数）里”，为真才需要注入。INNER_THOUGHTS_KWARG 只是那个键名字符串 “thinking”，不是开关；is_reasoning_model 是另一个抽象方法；工厂分派只认 endpoint 类型、不按是否推理路由。同一段注入代码，靠这个布尔值对两类模型给出恰好相反的处理。",
                    "en": "The decision rests on the single switch put_inner_thoughts_in_kwargs: True injects a simulated monologue (the model can't think on its own), False steps aside and uses the model's real reasoning (o1/o3/gpt-5, Claude 3.7/4, ZAI GLM, etc.). The name is the answer — “put inner thoughts in kwargs (the tool parameters)”, true only when injection is needed. INNER_THOUGHTS_KWARG is merely the key-name string “thinking”, not a switch; is_reasoning_model is a different abstract method; and the factory dispatches on endpoint type, not on whether a model reasons. The same injection code, via this one boolean, gives two kinds of model exactly opposite treatment.",
                },
            },
            {
                "q": {
                    "zh": "本课说“内心独白排第一”是默认做法，但有一家偏偏反着来。Google 把 thinking 字段放在哪里？",
                    "en": "The lesson says “inner monologue first” is the default — but one family breaks it. Where does Google place the thinking field?",
                },
                "opts": [
                    {"zh": "排在最后——Google 把 thinking 追加在末尾（INNER_THOUGHTS_KWARG_VERTEX），是“排第一”规则的反例；GoogleVertexClient 还把字段名另起一套（functionCall / .args）、用 “model” 表示助手角色",
                     "en": "Last — Google appends thinking at the end (INNER_THOUGHTS_KWARG_VERTEX), the exception to the “first” rule; GoogleVertexClient also renames fields (functionCall / .args) and uses “model” for the assistant role"},
                    {"zh": "排第一，跟所有人一模一样——Google 遵循同样的约定",
                     "en": "First, exactly like everyone else — Google follows the same convention"},
                    {"zh": "Google 根本不用 thinking 字段，它完全靠原生推理",
                     "en": "Google doesn't use a thinking field at all; it relies purely on native reasoning"},
                    {"zh": "放在中间——第一个必填字段之后、其余参数之前",
                     "en": "In the middle, after the first required field but before the rest"},
                ],
                "answer": 0,
                "why": {
                    "zh": "Google 是被点名的反例：它把 thinking 追加在最后，对应常量 INNER_THOUGHTS_KWARG_VERTEX，而不是像别家那样排第一。这一家处处跟 OpenAI 形状对着干——工具被包成 [{“functionDeclarations”:[...]}]、工具调用叫 functionCall（带 .name / .args）、助手角色名是 “model”——这些差异全被关进 GoogleVertexClient，循环照旧无感。常见误区正是想当然以为“各家都排第一”；真要写一个新 client，第一件事就是去确认它到底把 thinking 放哪儿。它当然也用 thinking、也不会把它塞在中间。",
                    "en": "Google is the named counterexample: it appends thinking last, via the constant INNER_THOUGHTS_KWARG_VERTEX, rather than first like the others. This family works against the OpenAI shape at every turn — tools are wrapped as [{“functionDeclarations”:[...]}], the tool call is called functionCall (with .name / .args), and the assistant role is named “model” — all caged inside GoogleVertexClient so the loop feels nothing. The classic pitfall is assuming “everyone puts it first”; to write a new client for real, the first thing to do is confirm exactly where it puts thinking. It does use thinking, and it doesn't bury it in the middle.",
                },
            },
            {
                "q": {
                    "zh": "一个 OpenAIClient 怎么能在不为每家单写一个 client 的情况下，服务 25 种 ProviderType 里的约 19 种（openai、ollama、vllm、Groq、xAI……）？",
                    "en": "How can a single OpenAIClient serve ~19 of 25 ProviderTypes (openai, ollama, vllm, Groq, xAI, …) without a bespoke client for each?",
                },
                "opts": [
                    {"zh": "_prepare_client_kwargs 只把 base_url 设成 llm_config.model_endpoint——同一套 OpenAI SDK 指向不同 URL 就接上不同的家；这些端点大多提供“OpenAI 兼容”接口，于是默认 case _ 兜底回 OpenAIClient",
                     "en": "_prepare_client_kwargs just sets base_url to llm_config.model_endpoint — the same OpenAI SDK pointed at a different URL connects to a different provider; most expose an “OpenAI-compatible” interface, so the default case _ falls back to OpenAIClient"},
                    {"zh": "它内部维护一张注册表，把每个 provider 名字映射到一套手写的请求/响应翻译器",
                     "en": "It maintains an internal registry mapping every provider name to a hand-written request/response translator"},
                    {"zh": "每家都自带一个 OpenAIClient 子类，根本没有共享的默认实现",
                     "en": "Each provider ships its own OpenAIClient subclass; there is no shared default"},
                    {"zh": "它从 model 名字前缀识别出是哪家，再据此改写 payload",
                     "en": "It detects the provider from the model name prefix and rewrites the payload accordingly"},
                ],
                "answer": 0,
                "why": {
                    "zh": "诀窍小得离谱：_prepare_client_kwargs 只把 base_url 设成 model_endpoint——同一套 OpenAI SDK，换个 URL 就接上一家。因为这些端点大多本就提供“OpenAI 兼容”接口，请求体/响应体的形状跟 OpenAI 对得上，真正不同的只是服务器地址，所以工厂的 case _ 直接兜底回 OpenAIClient。只有 6 种 ProviderType（anthropic / bedrock / chatgpt_oauth / google_ai / google_vertex / minimax）需要非 OpenAI 的 client。那 8 个显式子类是“几乎兼容、但还差一口气”的例外，不是“每个名字配一个子类”；也没有什么手写翻译器注册表，更不靠 model 名字前缀去猜。",
                    "en": "The trick is absurdly small: _prepare_client_kwargs only sets base_url to model_endpoint — the same OpenAI SDK, a new URL, a new provider connected. Because these endpoints mostly already expose an “OpenAI-compatible” interface, their request/response shapes line up with OpenAI and the only real difference is the server address, so the factory's case _ simply falls back to OpenAIClient. Only 6 ProviderTypes (anthropic / bedrock / chatgpt_oauth / google_ai / google_vertex / minimax) need a non-OpenAI client. The 8 explicit subclasses are the “almost compatible but one breath short” exceptions, not “one subclass per name”; there is no hand-written translator registry, and it certainly doesn't guess from the model name prefix.",
                },
            },
        ],
        "open": [
            {
                "zh": "用本课“一张脸、多张面具”的演员比喻，把第 22 课的“供应商怪癖”完整讲一遍，并想透三件事：(1) 各家怪癖都被关进子类的 build_request_data（改请求）与 convert_response_to_chat_completion（改响应）这首尾两步，中间的发送与编排是所有家共用的。为什么把“易变的差异”锁进窄窄两个方法、把“不变的执行循环”彻底解放，能让“加一家 provider、循环零改动”成立？如果有人图省事，把“解析 Anthropic 内容块”写进了第 14 课的循环里，为什么说“循环里冒出 if 是不是 anthropic”就是抽象漏了的信号？(2) 对没有原生推理的模型，Letta 把一个 thinking 字符串硬塞成每个工具的第一个必填参数，逼模型“先想后调”，再在响应里 unpack 回 message.content。为什么“用结构去逼出行为”比“恳求模型请先想一想”更可靠？而 put_inner_thoughts_in_kwargs 又凭什么对原生推理模型（o1/gpt-5/Claude-4）自动关掉这一注入？(3) Google 把 thinking 追加在最后，是“排第一”默认的反例。为什么说“内心独白排第一”是一条默认、而非铁律？据此，动手写一个全新 client 时，你该最先确认哪几件事，才不会想当然踩坑？",
                "en": "Use this lesson's “one face, many masks” actor metaphor to tell lesson 22's “provider quirks” as a whole, and think through three things: (1) Every provider's quirks are caged into the subclass's two end steps, build_request_data (edit request) and convert_response_to_chat_completion (edit response), while the sending and orchestration in the middle are shared by everyone. Why does locking the “volatile differences” into two narrow methods and fully freeing the “invariant execution loop” make “add a provider, change the loop by zero lines” hold? If someone took a shortcut and wrote “parse Anthropic content blocks” into the Lesson 14 loop, why is “an if is_anthropic appearing in the loop” a signal that the abstraction has leaked? (2) For models without native reasoning, Letta jams a thinking string in as each tool's first required parameter, forcing the model to “think before acting”, then unpacks it back into message.content on the response. Why is “using structure to force behavior” more reliable than “begging the model to please think first”? And on what basis does put_inner_thoughts_in_kwargs automatically switch that injection off for native-reasoning models (o1/gpt-5/Claude-4)? (3) Google appends thinking last, the counterexample to the “first” default. Why is “inner monologue first” a default rather than an iron law? Given that, when you sit down to write a brand-new client, what should you confirm first so you don't trip on a wrong assumption?",
            },
        ],
    },
    "23-local-models-gbnf.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 letta v0.16.8 里，本地模型的 GBNF / chat_completion_proxy 这条路，是当前主路径还是历史 legacy 路径？",
                    "en": "In letta v0.16.8, is the local-model GBNF / chat_completion_proxy route the current main path or a historical legacy path?",
                },
                "opts": [
                    {"zh": "legacy 历史路径——现代本地后端走第 21 课的 OpenAIClient（默认 case _）；GBNF 只在旧 Agent 的本地兜底分支才被走到",
                     "en": "A legacy historical path — modern local backends take Lesson 21's OpenAIClient (the default case _); GBNF is only reached on the old Agent's local fallback branch"},
                    {"zh": "当前主路径——所有本地模型都默认经过 get_chat_completion 和 GBNF 受限解码",
                     "en": "The current main path — every local model goes through get_chat_completion and GBNF constrained decoding by default"},
                    {"zh": "两条等价路径，由 LLMConfig 上的一个开关随机择一",
                     "en": "Two equivalent paths, chosen at random by a switch on LLMConfig"},
                    {"zh": "已被完全删除的死代码，v0.16.8 里根本调用不到",
                     "en": "Fully removed dead code that can't be reached at all in v0.16.8"},
                ],
                "answer": 0,
                "why": {
                    "zh": "这是一条 legacy 历史路径。现代本地后端（ollama/vllm/lmstudio）大多提供 OpenAI 兼容端点，于是落到第 21 课工厂的默认 case _ → OpenAIClient，根本不需要专属 client。GBNF 这套只在旧 agent.py::Agent 之后、经 llm_api_tools.py::create 的 else（本地）分支兜底时，才走到 chat_completion_proxy.py::get_chat_completion。它不是默认主路径（多数本地模型并不经过它），不是随机择一的开关，更不是死代码——它仍能跑，只是退居二线。记住：讲它是为了看清 function calling 的本质，不是因为今天默认这么跑。",
                    "en": "This is a legacy historical path. Modern local backends (ollama/vllm/lmstudio) mostly expose OpenAI-compatible endpoints, so they land on Lesson 21's factory default case _ → OpenAIClient and need no dedicated client. The GBNF set is reached only when the old agent.py::Agent, via llm_api_tools.py::create's else (local) branch, falls through to chat_completion_proxy.py::get_chat_completion. It is not the default main path (most local models never go through it), not a randomly chosen switch, and not dead code — it still runs, just demoted. Remember: we study it to see the essence of function calling, not because it's how things run by default today.",
                },
            },
            {
                "q": {
                    "zh": "GBNF 受限解码具体靠什么，把“输出是可解析 JSON”从一个概率变成一个保证？",
                    "en": "By what mechanism does GBNF constrained decoding turn “the output is parseable JSON” from a probability into a guarantee?",
                },
                "opts": [
                    {"zh": "它约束采样器本身——每一步只允许语法此刻合法的 token 进入候选集，模型物理上吐不出非法形状",
                     "en": "It constrains the sampler itself — at each step only grammar-legal tokens enter the candidate set, so the model physically cannot emit an illegal shape"},
                    {"zh": "它在提示里反复叮嘱模型“请务必输出合法 JSON”，靠更强的措辞提高守格式的概率",
                     "en": "It repeatedly reminds the model in the prompt to “please output valid JSON”, raising the odds via stronger wording"},
                    {"zh": "它先让模型自由生成，再用正则把不合法的部分删掉",
                     "en": "It lets the model generate freely, then strips the illegal parts with a regex"},
                    {"zh": "它把温度设为 0，让采样变成确定性的，从而保证 JSON 合法",
                     "en": "It sets temperature to 0 to make sampling deterministic, thereby guaranteeing valid JSON"},
                ],
                "answer": 0,
                "why": {
                    "zh": "关键在“采样级”约束。GBNF（llama.cpp 的 GGML BNF 语法）被喂给采样器，在生成的每一步把下一个 token 的候选集裁剪到“语法此刻允许的”那些——该出 { 的位置只能出 {，该出字段名的位置只能出那几个名字。于是模型无路可走到非法形状，输出必然可解析。这跟“在提示里更用力地叮嘱”（仍是概率）、“事后用正则删”（治标的解析修复，正是 clean_json 那条退化路）、“调低温度”（只改概率分布、不改合法性）都不同。一句话：可解析性不是被劝出来的，是被采样器物理地保证出来的。",
                    "en": "The key is the “sampling-level” constraint. GBNF (llama.cpp's GGML BNF grammar) is fed to the sampler and, at every generation step, trims the next token's candidate set to those “the grammar allows right now” — where a { belongs only a { can appear, where a field name belongs only those few names can. So the model has no path to an illegal shape and the output is necessarily parseable. This differs from “reminding harder in the prompt” (still a probability), “stripping with a regex afterward” (symptom-level parse repair, exactly the degraded clean_json route), and “lowering the temperature” (which changes the probability distribution, not legality). In one line: parseability isn't coaxed out, it's physically guaranteed by the sampler.",
                },
            },
            {
                "q": {
                    "zh": "同一条路生成了 grammar，但只有部分后端真正用它。哪些后端会真正吃 grammar，其余的又靠什么保证 JSON？",
                    "en": "The same path generates a grammar, but only some backends actually use it. Which backends really consume the grammar, and what do the rest rely on to guarantee JSON?",
                },
                "opts": [
                    {"zh": "只有 llamacpp / koboldcpp / webui / webui-legacy 真正吃 grammar；其余（ollama/vllm/lmstudio）丢弃，改靠 clean_json 容错修复",
                     "en": "Only llamacpp / koboldcpp / webui / webui-legacy really consume the grammar; the rest (ollama/vllm/lmstudio) drop it and fall back on clean_json tolerant repair"},
                    {"zh": "所有本地后端都吃 grammar，因为它们底层都是 llama.cpp",
                     "en": "Every local backend consumes the grammar, since they're all llama.cpp underneath"},
                    {"zh": "只有 ollama 和 vllm 吃 grammar，老牌的 llamacpp/koboldcpp 反而不支持",
                     "en": "Only ollama and vllm consume the grammar; the older llamacpp/koboldcpp don't support it"},
                    {"zh": "都不吃 grammar——grammar 只是文档，实际全靠 clean_json 兜底",
                     "en": "None consume the grammar — it's just documentation, and everything actually relies on clean_json"},
                ],
                "answer": 0,
                "why": {
                    "zh": "只有 grammar_supported_backends（koboldcpp/llamacpp/webui/webui-legacy 四个）会把 grammar 真正传给采样器，拿到“采样级硬保证”。其余本地后端（ollama/vllm/lmstudio 等）即便拿到 grammar 也直接丢弃，退化成“解析级”的尽力修复：靠 wrapper 把格式写进提示，再靠 json_parser.py::clean_json 把脏文本掰成合法 JSON（注意 clean_json 是容错修复，不是重采样 / 重试）。所以不是“所有后端都吃”（只有四个），不是 ollama/vllm 那两个（恰恰相反），也不是“全靠 clean_json”（四个语法后端有更硬的保证）。为什么偏偏这四个？因为只有它们的采样接口暴露了能接 grammar 的入口。",
                    "en": "Only grammar_supported_backends (koboldcpp/llamacpp/webui/webui-legacy) actually pass the grammar to the sampler and get the “sampling-level hard guarantee”. Other local backends (ollama/vllm/lmstudio, etc.) drop the grammar even when handed one, degrading to “parse-level” best-effort repair: the wrapper writes the format into the prompt, then json_parser.py::clean_json bends the dirty text into legal JSON (note clean_json is tolerant repair, not resample / retry). So it's not “every backend consumes it” (only four), not ollama/vllm (the opposite), and not “all on clean_json” (the four grammar backends have a harder guarantee). Why these four? Because only their sampling interfaces expose an entry point that accepts a grammar.",
                },
            },
            {
                "q": {
                    "zh": "一个连原生工具 API 都没有、只会续写文本的本地模型，是怎么“知道”自己有哪些函数可调的？",
                    "en": "A local model with no native tool API, one that can only continue text — how does it “know” which functions it can call?",
                },
                "opts": [
                    {"zh": "wrapper 把函数 schema 当文本直接塞进提示，模型在题面里“读到”有哪些工具及参数",
                     "en": "The wrapper stuffs the function schema into the prompt as text, so the model “reads” which tools and parameters exist right in the question"},
                    {"zh": "模型权重里预训练好了这些函数定义，运行时无需传入",
                     "en": "The function definitions are pretrained into the model weights, so nothing needs to be passed at runtime"},
                    {"zh": "GBNF 语法本身就把函数讲给了模型——schema 是从语法反推出来的，不进提示",
                     "en": "The GBNF grammar itself tells the model about the functions — the schema is inferred from the grammar and never enters the prompt"},
                    {"zh": "通过一个独立的 /tools 端点，后端在调用前先把工具列表注册进去",
                     "en": "Through a separate /tools endpoint where the backend registers the tool list before the call"},
                ],
                "answer": 0,
                "why": {
                    "zh": "靠 wrapper 把 schema 写进提示文本。chat_completion_to_prompt（内部用 _compile_function_block）把每个函数的名字、参数、说明，连同 inner_thoughts 的描述，一起当文本拼进提示；裸 completion 端点没有 /chat/completions 那种现成的工具结构，所有“工具长什么样”的信息只能由 proxy 这层自己造进题面。不是预训练进权重的（那样换工具就没法用），不是从 GBNF 反推的（语法管“吐什么形状”，讲解工具的是提示——二者分工：schema 进提示让模型“知道”，语法卡采样让它“只能”填对），也没有什么 /tools 注册端点。记住这台 wrapper 是双向翻译机的“出去”那一头。",
                    "en": "Via the wrapper writing the schema into the prompt text. chat_completion_to_prompt (internally _compile_function_block) assembles each function's name, parameters, and description — together with the inner_thoughts description — into the prompt as text; a bare completion endpoint has none of the ready-made tool structure of /chat/completions, so every bit of “what the tool looks like” must be built into the question by the proxy layer itself. It isn't pretrained into the weights (then you couldn't swap tools), isn't inferred from GBNF (the grammar governs “what shape comes out” while the prompt explains the tools — a division of labor: schema in the prompt lets the model “know”, grammar on the sampler makes it “only” fill in right), and there's no /tools registration endpoint. Remember this wrapper is the “outbound” end of a bidirectional translator.",
                },
            },
            {
                "q": {
                    "zh": "在这条本地路里，第 15 课那个“内心独白”（inner_thoughts）是怎么被表示和处理的？",
                    "en": "On this local path, how is Lesson 15's “inner monologue” (inner_thoughts) represented and handled?",
                },
                "opts": [
                    {"zh": "它是被语法 / 提示强制出现的一个 JSON 字段，解析时再从 params 提升（pop）到 message.content",
                     "en": "It's a JSON field forced to appear by the grammar/prompt, then lifted (popped) from params into message.content on parse"},
                    {"zh": "它是模型自愿在 JSON 之外多写的一段自然语言，proxy 原样保留",
                     "en": "It's a stretch of natural language the model voluntarily adds outside the JSON, kept verbatim by the proxy"},
                    {"zh": "它是后端返回的一个独立 reasoning 字段，本地路直接透传，不做任何搬运",
                     "en": "It's a separate reasoning field returned by the backend, passed straight through on the local path with no relocation"},
                    {"zh": "它只在云端模型上才有，本地这条路完全没有 inner_thoughts 的概念",
                     "en": "It exists only on cloud models; this local path has no concept of inner_thoughts at all"},
                ],
                "answer": 0,
                "why": {
                    "zh": "inner_thoughts 是被强制出来的结构字段，不是模型自愿写的。语法路上，GBNF 逼着每个 params 分支先写一个 inner_thoughts 字符串；非语法路上，wrapper 把它写进提示要求。解析时，output_to_chat_completion_response 把它从参数里 pop 出来、搬进 message.content——正是把第 15 课那条“内心独白”约定，从提示层面升格成语法层面的强制。所以它不是 JSON 之外的自由文本，不是后端原生透传的字段，更不是只有云端才有。一句话：本地这条路里，inner_thoughts 是被语法 / 提示硬性要求、再被解析搬运到 content 的。",
                    "en": "inner_thoughts is a forced structured field, not something the model writes voluntarily. On the grammar route, GBNF forces every params branch to write an inner_thoughts string first; on the non-grammar route, the wrapper writes the requirement into the prompt. On parse, output_to_chat_completion_response pops it out of the parameters and moves it into message.content — exactly promoting Lesson 15's “inner monologue” convention from the prompt level to a grammar-level mandate. So it isn't free text outside the JSON, isn't a field passed through natively by the backend, and certainly isn't cloud-only. In one line: on this local path, inner_thoughts is hard-required by the grammar/prompt and then relocated to content on parse.",
                },
            },
        ],
        "open": [
            {
                "zh": "用本课“镂空钢板”的比喻，把第 23 课“本地模型 + GBNF”这条 legacy 路完整讲一遍，并想透三件事：(1) 给一个只会续写文本、没有原生工具 API 的模型加 function calling，靠的是两招——wrapper 用 chat_completion_to_prompt 把函数 schema 当文本塞进提示（让模型“知道”），GBNF 在采样级约束 token（让它“只能”填对）。为什么说缺了第二招、第一招就只剩一句祈祷？这两招的“软 / 硬”分工，跟第 22 课“把 thinking 排成第一个必填参数、用结构逼出行为”是不是同一种思路？(2) 同一条路生成了 grammar，却只有 llamacpp/koboldcpp/webui/webui-legacy 四个真正吃它，其余（ollama/vllm/lmstudio）丢弃、退化成 clean_json 容错修复。为什么说这是“采样级硬保证”退化成“解析级尽力修复”这两个等级？为什么 clean_json 不能被理解成“重采样重试”？(3) 本地这条路里，inner_thoughts 是被语法 / 提示强制出现、再被 output_to_chat_completion_response 从 params 搬到 message.content 的。它怎么一头扣回第 15 课的“内心独白”，一头又解释了为什么今天它成了 legacy（第 21 课 OpenAI 兼容赢了）？",
                "en": "Use this lesson's “stencil plate” metaphor to tell lesson 23's “local model + GBNF” legacy path as a whole, and think through three things: (1) Adding function calling to a model that only continues text, with no native tool API, rests on two moves — the wrapper uses chat_completion_to_prompt to stuff the function schema into the prompt as text (so the model “knows”), and GBNF constrains tokens at the sampling level (so it “only” fills in right). Why is the first move just a prayer without the second? Is this “soft / hard” division the same idea as Lesson 22's “order thinking as the first required parameter, using structure to force behavior”? (2) The same path generates a grammar, yet only llamacpp/koboldcpp/webui/webui-legacy actually consume it, while the rest (ollama/vllm/lmstudio) drop it and degrade to clean_json tolerant repair. Why is this two tiers — a “sampling-level hard guarantee” degrading to a “parse-level best-effort repair”? And why must clean_json not be read as “resample and retry”? (3) On this local path, inner_thoughts is forced to appear by the grammar/prompt and then moved by output_to_chat_completion_response from params into message.content. How does it clasp back to Lesson 15's “inner monologue” on one end, while on the other explaining why it became legacy today (Lesson 21's OpenAI-compatible won)?",
            },
        ],
    },
    "24-three-layer-architecture.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 letta v0.16.8 里，那个唯一的全局 SyncServer 究竟在哪里被创建？",
                    "en": "In letta v0.16.8, where is that single global SyncServer actually created?",
                },
                "opts": [
                    {"zh": "在 app.py 的模块级——import 这个模块那一刻就同步建好了",
                     "en": "At module level in app.py — built synchronously the moment the module is imported"},
                    {"zh": "在 create_application 工厂里，构建 FastAPI 应用时一并 new 出来",
                     "en": "Inside the create_application factory, newed up together with the FastAPI app"},
                    {"zh": "在 lifespan 里，第一次 await server.init_async(...) 时才创建",
                     "en": "Inside lifespan, created on the first await server.init_async(...)"},
                    {"zh": "在 get_letta_server 里惰性创建，每个请求新建一个",
                     "en": "Lazily created inside get_letta_server, a fresh one per request"},
                ],
                "answer": 0,
                "why": {
                    "zh": "它是 app.py::server 这个模块级全局，在模块被 import 那一刻就同步构造好。create_application 工厂里其实也有一行 SyncServer(...)，但那行是注释掉的——server 不在工厂里建。lifespan 只做异步引导：await server.init_async(...) 建默认 org/user、把基础工具 upsert 进库，那是“对象建好之后”才需要 await 的初始化，不是构造。get_letta_server 只是惰性 import 那个模块全局并返回，每个路由经 Depends(get_letta_server) 拿到的都是同一个实例，并不新建。一句话：import 时同步接线、启动时异步 init。",
                    "en": "It's the module-level global app.py::server, constructed synchronously the moment the module is imported. The create_application factory does contain a SyncServer(...) line, but it's commented out — the server isn't built in the factory. lifespan only does async bootstrapping: await server.init_async(...) creates the default org/user and upserts base tools, an initialization that needs await after the object already exists, not construction. get_letta_server merely lazy-imports that module global and returns it, so every router that asks via Depends(get_letta_server) gets the same instance and none builds a new one. In one line: synchronous wiring at import, async init at startup.",
                },
            },
            {
                "q": {
                    "zh": "一个薄 CRUD 端点，通常靠什么拿到它要的数据？",
                    "en": "How does a thin CRUD endpoint usually reach the data it needs?",
                },
                "opts": [
                    {"zh": "直接调 server.&lt;manager&gt;.&lt;method&gt;()；SyncServer 自己的方法只留给跨-manager 编排",
                     "en": "Directly via server.&lt;manager&gt;.&lt;method&gt;(); SyncServer's own methods are reserved for cross-manager orchestration"},
                    {"zh": "每次读写都得过一道 SyncServer 方法，那是通往 DB 的唯一一道门",
                     "en": "Every read/write must pass through a SyncServer method, the one door to the DB"},
                    {"zh": "路由自己开一个 db_registry.async_session() 跑查询",
                     "en": "The router opens a db_registry.async_session() itself and runs the query"},
                    {"zh": "把请求投进一个内部消息队列，由 manager 工作者异步消费",
                     "en": "It posts the request onto an internal message queue consumed by a manager worker"},
                ],
                "answer": 0,
                "why": {
                    "zh": "绝大多数时候，端点通过 server 对象直接调对应 manager：server.agent_manager.get_agent_by_id_async(...) 这种。在 agents.py 里，这种“直调 manager”约 131 次，而调 SyncServer 自己方法只约 16 次——后者只用于跨多个 manager 的编排（如 create_agent_async 解析 LLM/embedding 配置、变换 block、再委托 agent_manager 写）。所以 SyncServer 是服务定位器加跨-manager 协调者，不是“通往 DB 的唯一一道门”。路由从不自己开 session（session 在 manager 里开关），层与层之间也没有消息队列：所有 manager 都是 SyncServer 的普通属性，调用就是普通的 async 方法调用。",
                    "en": "The vast majority of the time, the endpoint calls the matching manager directly through the server object: things like server.agent_manager.get_agent_by_id_async(...). In agents.py this “direct manager call” appears about 131 times, while calling SyncServer's own methods appears only about 16 — and the latter is reserved for orchestration across several managers (e.g. create_agent_async resolves the LLM/embedding config, transforms blocks, then delegates the write to agent_manager). So SyncServer is a service locator plus cross-manager coordinator, not “the one door to the DB”. The router never opens a session itself (sessions are opened and closed inside the manager), and there's no message queue between layers: every manager is a plain attribute of SyncServer, so a call is just an ordinary async method call.",
                },
            },
            {
                "q": {
                    "zh": "对一条请求来说，actor 的解析究竟发生在哪一步？",
                    "en": "For a request, at which step does actor resolution actually happen?",
                },
                "opts": [
                    {"zh": "在处理函数体内、await get_actor_or_default_async 时；get_headers 只解析/校验 user_id 头",
                     "en": "In the handler body, when it awaits get_actor_or_default_async; get_headers only parses/validates the user_id header"},
                    {"zh": "在一个跑在每个端点之前的全局鉴权中间件里",
                     "en": "In a global auth middleware that runs before every endpoint"},
                    {"zh": "在 get_headers 里——它顺手查库拿到 user 并返回 actor",
                     "en": "Inside get_headers — it conveniently looks up the user in the DB and returns the actor"},
                    {"zh": "在 ORM 里，跑 agent 查询、apply_access_predicate 焊进 SQL 时",
                     "en": "In the ORM, when the agent query runs and apply_access_predicate is welded into the SQL"},
                ],
                "answer": 0,
                "why": {
                    "zh": "actor 在处理函数体内解析（薄路由第 ① 步）：await server.user_manager.get_actor_or_default_async(actor_id=headers.actor_id)，这才开 session #1 真正查 user。dependencies.py::get_headers 只把 user_id 头解析/校验成 HeaderParams.actor_id（校验 user-&lt;uuid4&gt; 格式、不碰 DB），并不查库、也不返回 actor。它不是全局鉴权中间件——靠的是每个 handler 自己的 Depends 加函数体。而 apply_access_predicate 是 session #2 查 agent 时焊进的组织级隔离，管的是“能看谁的数据”，跟“解析出 actor 是谁”是两回事。缺 user_id 时，OSS 模式落到 default user。",
                    "en": "The actor is resolved inside the handler body (the thin router's step ①): await server.user_manager.get_actor_or_default_async(actor_id=headers.actor_id), which is what opens session #1 to actually look up the user. dependencies.py::get_headers only parses/validates the user_id header into HeaderParams.actor_id (checking the user-&lt;uuid4&gt; format, touching no DB); it neither queries the DB nor returns an actor. It is not a global auth middleware — it relies on each handler's own Depends plus the function body. And apply_access_predicate is the organization-level isolation welded into session #2's agent query; it governs “whose data you may see”, a separate concern from “resolving who the actor is”. When user_id is missing, OSS mode falls back to the default user.",
                },
            },
            {
                "q": {
                    "zh": "谁来开 DB session / 事务？一条 GET /v1/agents/{id} 又跨了几个事务？",
                    "en": "Who opens the DB session/transaction, and how many does one GET /v1/agents/{id} span?",
                },
                "opts": [
                    {"zh": "manager 用 db_registry.async_session() 开；路由从不开——一条请求跨多个独立事务",
                     "en": "The manager, via db_registry.async_session(); the router never does — one request spans multiple independent transactions"},
                    {"zh": "路由一开始就开一个 session，把整条请求包进单个事务",
                     "en": "The router opens one session up front, wrapping the whole request in a single transaction"},
                    {"zh": "SyncServer 开一个共享 session，本请求里所有 manager 复用它",
                     "en": "SyncServer opens one shared session that every manager reuses for this request"},
                    {"zh": "一个全局中间件开启并提交一个请求级工作单元（UoW）",
                     "en": "A global middleware opens and commits one request-level unit of work (UoW)"},
                ],
                "answer": 0,
                "why": {
                    "zh": "事务边界被划在 manager 方法里：每个方法各自 async with db_registry.async_session() 开一个 session，办完即 commit/close。于是 retrieve_agent 这一条请求跨了两个独立事务——session #1 查 user，session #2 走 select(AgentModel)+apply_access_predicate+where(id==...)——并没有把整条请求包进一个请求级 UoW。路由层从不开 session（薄：不写业务、不开库），SyncServer 也不替大家开共享 session。代价是两次读不是同一个快照；也因为没有大事务，后一步失败不会自动回滚前一步已提交的写，补偿/幂等的责任落回编排方。session 的来历，第 27 课细讲。",
                    "en": "Transaction boundaries are drawn inside manager methods: each method opens its own session with async with db_registry.async_session() and commits/closes once done. So the single retrieve_agent request spans two independent transactions — session #1 to look up the user, session #2 for select(AgentModel)+apply_access_predicate+where(id==...) — rather than wrapping the whole request in a request-level UoW. The router layer never opens a session (thin: no business, no DB), and SyncServer doesn't open a shared one for everybody either. The cost is that the two reads aren't the same snapshot; and because there's no big transaction, a failure in a later step won't auto-roll-back a write already committed earlier, so compensation/idempotency falls back on the orchestrator. Lesson 27 covers where the session comes from.",
                },
            },
            {
                "q": {
                    "zh": "类名叫 SyncServer、docstring 还写着“单线程 / 阻塞”。可 v0.16.8 的现实是什么？",
                    "en": "The class is named SyncServer and its docstring still says “single-threaded / blocking”. What's the reality in v0.16.8?",
                },
                "opts": [
                    {"zh": "名不副实的历史遗留——路由调到的方法几乎全是 async def",
                     "en": "A legacy misnomer — the methods routers call are almost all async def"},
                    {"zh": "名副其实——它确实单线程、阻塞，请求严格一个接一个处理",
                     "en": "Accurate — it really is single-threaded and blocking, serving requests strictly one at a time"},
                    {"zh": "它为每个请求开一个操作系统线程，这正是“Sync”的本意",
                     "en": "It spawns one OS thread per request, which is exactly what “Sync” means"},
                    {"zh": "它在路由层是同步的，只有进了 ORM 内部才阻塞",
                     "en": "It's synchronous at the router layer and blocks only once inside the ORM"},
                ],
                "answer": 0,
                "why": {
                    "zh": "docstring “Simple single-threaded / blocking server process” 是历史遗留：早期确有“同步、单线程、阻塞”的设想，名字就是那时定的。但 v0.16.8 里路由调到的方法几乎全是 async def，并发靠单事件循环上的协作式 async，不是多线程、不是阻塞、不是一个接一个、也不是“每请求一线程”。名字没改，是因为它早已是无数调用点的稳定符号，改名的收益远抵不过全仓改动的风险——读代码时把 “Sync” 当历史标签即可。提醒：这跟那个可选的服务器口令中间件（CheckPasswordMiddleware，仅 secure 模式）是两码事，后者管“整台服务器让不让进”，与 actor/租户身份正交。",
                    "en": "The docstring “Simple single-threaded / blocking server process” is a legacy remnant: there really was an early vision of “synchronous, single-threaded, blocking”, and the name was fixed back then. But in v0.16.8 the methods routers call are almost all async def, with concurrency from cooperative async on a single event loop — not multithreading, not blocking, not one-at-a-time, and not “one thread per request”. The name hasn't changed because it's long been a stable symbol at countless call sites, and renaming's payoff is far outweighed by the repo-wide risk — when reading the code, just treat “Sync” as a historical label. A reminder: this is unrelated to the optional server-password middleware (CheckPasswordMiddleware, secure mode only), which governs “whether the whole server lets you in” and is orthogonal to actor/tenant identity.",
                },
            },
        ],
        "open": [
            {
                "zh": "用本课“三层楼公司”的比喻，把一条 GET /v1/agents/{id} 从进门到落库再原路返回完整讲一遍，并想透四件事：(1) 那个唯一的全局 SyncServer 为什么在 app.py 模块级、import 时就同步建好（create_application 里那行是注释掉的），而 init_async 却推迟到 lifespan？这“import 同步接线 + 启动异步 init”的两段式，到底买到了什么？(2) 为什么是“薄路由直调 manager”（agents.py 约 131 : 16），而不是把 CRUD 都走 SyncServer？这又如何跟“actor 在函数体内解析、session 只在 manager 里开”扣在一起？(3) 为什么一次请求＝多个独立事务、没有请求级 UoW？这把什么责任交回给了编排方？(4) SyncServer 这个“同步”的误名、再加上那道正交的服务器口令中间件，和每请求的 actor/租户身份，三者各管什么、谁也不替代谁？",
                "en": "Use this lesson's “three-floor company” metaphor to tell a single GET /v1/agents/{id} as a whole — from the front door to the database and back along the same path — and think through four things: (1) Why is that single global SyncServer built synchronously at module level in app.py at import time (the line in create_application is commented out), while init_async is deferred to lifespan? What exactly does this “synchronous wiring at import + async init at startup” two-phase split buy? (2) Why is it “thin routers calling managers directly” (about 131 : 16 in agents.py) rather than routing all CRUD through SyncServer? And how does that clasp together with “the actor is resolved in the handler body, the session is opened only in the manager”? (3) Why is one request = multiple independent transactions with no request-level UoW, and what responsibility does that hand back to the orchestrator? (4) SyncServer's “sync” misnomer, plus that orthogonal server-password middleware, plus the per-request actor/tenant identity — what does each govern, and why does none replace the others?",
            },
        ],
    },
    "25-service-managers.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 letta v0.16.8 里，一个典型 manager 方法（如 OrganizationManager.get_organization_by_id_async）的“标准骨架”是什么？",
                    "en": "In letta v0.16.8, what is the “standard skeleton” of a typical manager method (e.g. OrganizationManager.get_organization_by_id_async)?",
                },
                "opts": [
                    {"zh": "async with db_registry.async_session() 开 session → 按 actor 做范围 CRUD → 仍在 session 内 to_pydantic() → 返回 pydantic",
                     "en": "async with db_registry.async_session() → actor-scoped CRUD → to_pydantic() still inside the session → return pydantic"},
                    {"zh": "直接 select(Model) 查询，把拿到的 ORM 行原样 return，让路由层自己转成 schema",
                     "en": "Run a plain select(Model) and return the ORM row as-is, letting the router layer turn it into a schema"},
                    {"zh": "先 to_pydantic() 复制成纯对象、退出 session 之后，再在门外补做访问控制过滤",
                     "en": "Convert via to_pydantic() first, exit the session, then apply access-control filtering outside the door"},
                    {"zh": "由 SyncServer 开一个共享 session，manager 只拼查询、统一在 server 层提交事务",
                     "en": "SyncServer opens one shared session; the manager only builds the query while the server layer commits the transaction"},
                ],
                "answer": 0,
                "why": {
                    "zh": "标准骨架五步雷打不动：装饰器 → async with db_registry.async_session() 开 session（同时定事务边界与 actor/org 范围）→ 门内做 actor 范围 CRUD（read_async/create_async）→ 仍在 session 内 to_pydantic() 把 ORM 行换成纯 pydantic → 返回。最简样板是 organization_manager.py::OrganizationManager.get_organization_by_id_async。绝不把 ORM 行漏出门外：访问控制（apply_access_predicate）由 ORM 焊进 SQL、不是门外补做；session 也只在 manager 里开，SyncServer 只持有与编排、不开共享 session。",
                    "en": "The five-step skeleton never budges: decorators → async with db_registry.async_session() opens the session (fixing both the transaction boundary and the actor/org scope) → actor-scoped CRUD inside the door (read_async/create_async) → to_pydantic() while still inside the session turns the ORM row into pure pydantic → return. The simplest exemplar is organization_manager.py::OrganizationManager.get_organization_by_id_async. An ORM row never slips out the door: access control (apply_access_predicate) is welded into the SQL by the ORM, not applied outside; and the session is opened only in the manager — SyncServer merely holds and orchestrates, it never opens a shared session.",
                },
            },
            {
                "q": {
                    "zh": "db.py 里的 db_registry 到底是个什么东西？",
                    "en": "What exactly is db_registry in db.py?",
                },
                "opts": [
                    {"zh": "一个进程级单例 DatabaseRegistry，docstring 自称“Dummy registry”，v0.16.8 只暴露 async_session()",
                     "en": "A process-wide singleton DatabaseRegistry, self-described “Dummy registry”, exposing only async_session()"},
                    {"zh": "一个按 DATABASE_URL 在 SQLite 与 Postgres 引擎间动态选择、并抹平方言差异的注册表",
                     "en": "A registry that dynamically picks between SQLite and Postgres engines by DATABASE_URL and smooths over dialect differences"},
                    {"zh": "一个依赖注入容器，启动时把所有 manager 注册进去、供路由按名解析",
                     "en": "A dependency-injection container that registers all managers at startup for routers to resolve by name"},
                    {"zh": "每个请求新建一个的对象，同时提供同步 session() 和异步 async_session() 两种入口",
                     "en": "An object created fresh per request, offering both a sync session() and an async async_session()"},
                ],
                "answer": 0,
                "why": {
                    "zh": "db.py::DatabaseRegistry 是进程级单例 db_registry，类 docstring 只有一句自嘲——“Dummy registry to maintain the existing interface.”：它不再做花哨的注册或选择，只为维持旧接口而留，于是上百处 db_registry.async_session() 调用点一字未改。模块级是一个 create_async_engine(async_pg_uri) + async_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)。v0.16.8 只有 async_session()、没有同步 session()；db.py 是 Postgres-only，不在这层分 SQLite/Postgres——方言透明属于 ORM 层（第 27 课）。它也不是 DI 容器：manager 是 SyncServer.__init__ 里普通 new 出来的。",
                    "en": "db.py::DatabaseRegistry is the process-wide singleton db_registry, and its class docstring is a single self-deprecating line — “Dummy registry to maintain the existing interface.”: it no longer does fancy registration or selection, staying only to keep the old interface, so hundreds of db_registry.async_session() call sites went unchanged. At module level it's one create_async_engine(async_pg_uri) + async_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False). v0.16.8 has only async_session(), no sync session(); db.py is Postgres-only and doesn't split SQLite/Postgres here — dialect transparency lives in the ORM layer (Lesson 27). It's also not a DI container: managers are plainly newed up in SyncServer.__init__.",
                },
            },
            {
                "q": {
                    "zh": "@enforce_types 和 @trace_method 各自做什么、又分别定义在哪？",
                    "en": "What do @enforce_types and @trace_method each do, and where is each defined?",
                },
                "opts": [
                    {"zh": "enforce_types（letta/utils.py）运行时校验入参类型；trace_method（letta/otel/tracing.py）开一个 OTel span",
                     "en": "enforce_types (letta/utils.py) runtime-checks argument types; trace_method (letta/otel/tracing.py) opens an OTel span"},
                    {"zh": "两个都定义在 letta/utils.py：一个校验类型，一个把返回值序列化成 pydantic",
                     "en": "Both live in letta/utils.py: one checks types, the other serializes the return value into pydantic"},
                    {"zh": "enforce_types 把同步方法包成 async；trace_method 负责开 session 并提交事务",
                     "en": "enforce_types wraps sync methods into async; trace_method opens the session and commits the transaction"},
                    {"zh": "enforce_types 校验 id 前缀；trace_method 在 OTel 未初始化时改为抛错",
                     "en": "enforce_types validates the id prefix; trace_method raises when OTel is uninitialized"},
                ],
                "answer": 0,
                "why": {
                    "zh": "enforce_types 定义在 letta/utils.py：它的 wrapper 是同步 def，用 get_type_hints 逐个比对入参、不符就 raise ValueError；对 async 方法它同步校验后把协程原样返回，并不自己 await。trace_method 定义在 letta/otel/tracing.py：开一个名为“{ClassName}.{method}”的 OTel span，记参时跳过 messages/embeddings 等大对象；当 _is_tracing_initialized 为 False 时纯透传（no-op、零开销），绝不抛错。两者并非都在 utils；id 前缀校验是另一个装饰器 raise_on_invalid_id（letta/validators.py）。典型叠放：@enforce_types（最外）→ @raise_on_invalid_id → @trace_method（最内）→ 方法。",
                    "en": "enforce_types is defined in letta/utils.py: its wrapper is a sync def that compares each argument against get_type_hints and raises ValueError on a mismatch; for an async method it validates synchronously then returns the coroutine as-is, never awaiting itself. trace_method is defined in letta/otel/tracing.py: it opens an OTel span named “{ClassName}.{method}” and skips big objects like messages/embeddings when recording; when _is_tracing_initialized is False it's a pure pass-through (no-op, zero overhead) and never raises. They are not both in utils; id-prefix checking is a separate decorator, raise_on_invalid_id (letta/validators.py). Typical stacking: @enforce_types (outermost) → @raise_on_invalid_id → @trace_method (innermost) → method.",
                },
            },
            {
                "q": {
                    "zh": "ORM 行与 pydantic schema 之间，两个方向各靠什么方法转换？",
                    "en": "Between an ORM row and a pydantic schema, what method handles each direction of conversion?",
                },
                "opts": [
                    {"zh": "出门 ORM→pydantic 靠 to_pydantic / to_pydantic_async；进门 pydantic→ORM 靠 model_dump(to_orm=True)",
                     "en": "Outbound ORM→pydantic via to_pydantic / to_pydantic_async; inbound pydantic→ORM via model_dump(to_orm=True)"},
                    {"zh": "两个方向都用 ORM 类上的 to_record()：传 to_orm=True 出 ORM 行、不传则出 pydantic",
                     "en": "Both directions use to_record() on the ORM class: pass to_orm=True for an ORM row, omit it for pydantic"},
                    {"zh": "出门 to_orm()、进门 from_orm()，两者都定义在 SqlalchemyBase 上",
                     "en": "Outbound to_orm(), inbound from_orm(), both defined on SqlalchemyBase"},
                    {"zh": "manager 在方法体里手写字段映射，没有统一的转换入口",
                     "en": "The manager hand-writes the field mapping in the method body; there's no unified conversion entry point"},
                ],
                "answer": 0,
                "why": {
                    "zh": "出门（读）：SqlalchemyBase.to_pydantic ＝ self.__pydantic_model__.model_validate(self, from_attributes=True)，每个 ORM 模型声明自己的 __pydantic_model__（如 orm/agent.py → PydanticAgentState）；带一堆关系的复杂模型（如 agent）重写 to_pydantic_async，因为拼关系可能再发查询、要 await。进门（写）：model_dump(to_orm=True)（schemas/letta_base.py::LettaBase.model_dump）把字段拆成字典，顺手把 metadata 改名成 metadata_，再喂给 ORM 构造器。根本没有 to_record() / to_orm() / from_orm() 这种方法——就 to_pydantic 和 model_dump(to_orm=True) 这两把钥匙。",
                    "en": "Outbound (read): SqlalchemyBase.to_pydantic = self.__pydantic_model__.model_validate(self, from_attributes=True), and each ORM model declares its own __pydantic_model__ (e.g. orm/agent.py → PydanticAgentState); a complex model with many relations (like agent) overrides to_pydantic_async because assembling relations may issue more queries and needs await. Inbound (write): model_dump(to_orm=True) (schemas/letta_base.py::LettaBase.model_dump) breaks the fields into a dict, renames metadata to metadata_ along the way, then feeds the ORM constructor. There is no to_record() / to_orm() / from_orm() at all — just the two keys to_pydantic and model_dump(to_orm=True).",
                },
            },
            {
                "q": {
                    "zh": "为什么 manager 必须在 async with 块内（session 还开着）就 to_pydantic()，而不是返回之后再转？",
                    "en": "Why must the manager call to_pydantic() inside the async with block (while the session is still open), rather than after returning?",
                },
                "opts": [
                    {"zh": "退出块后 session 已 expunge_all + close、ORM 行被解绑，再读字段多半 DetachedInstanceError",
                     "en": "After the block exits, the session has run expunge_all + close and the row is detached, so reading a field usually raises DetachedInstanceError"},
                    {"zh": "因为 to_pydantic() 本身需要一个打开的事务来 commit，否则转换不生效",
                     "en": "Because to_pydantic() itself needs an open transaction to commit, or the conversion won't take effect"},
                    {"zh": "因为 expire_on_commit=False 会让对象在退出后立即过期、字段全部清空",
                     "en": "Because expire_on_commit=False makes the object expire immediately on exit, wiping all its fields"},
                    {"zh": "纯属代码风格约定，返回后在路由层转换功能上完全等价、没有风险",
                     "en": "It's purely a style convention; converting in the router after returning is functionally equivalent and risk-free"},
                ],
                "answer": 0,
                "why": {
                    "zh": "async_session 的 finally 一定跑 expunge_all() + close()：一旦出了 async with 块，ORM 行已被解绑、session 已关，这时再读它的字段多半直接 DetachedInstanceError。expire_on_commit=False 只保证“已加载”的字段在 commit 后不过期（省一次 DB 往返），但碰到尚未加载的关系/惰性属性，脱离 session 的对象没法补查、照样炸——所以它不是“对象立即过期”，方向正好相反。规矩很硬：趁门开着把要用的都读出、定形成 pydantic；复印件一旦成形就和 session 无关。get_agent_by_id_async 甚至故意先转 pydantic、放掉 DB 连接后再跑昂贵的 PBKDF2 解密，把 schema 边界顺手变成连接池优化。",
                    "en": "async_session's finally always runs expunge_all() + close(): once you leave the async with block the ORM row is detached and the session closed, so reading its fields then usually raises DetachedInstanceError outright. expire_on_commit=False only keeps already-loaded fields from expiring after commit (saving a DB round trip), but for an unloaded relationship/lazy attribute an object cut off from its session can't re-query and blows up all the same — so it does not make the object “expire immediately”; it's the opposite. The rule is hard: while the door is open, read out everything you need and set it into pydantic; once formed, the copy is independent of the session. get_agent_by_id_async even deliberately converts to pydantic first and releases the DB connection before running the expensive PBKDF2 decryption, turning the schema boundary into a connection-pool optimization.",
                },
            },
        ],
        "open": [
            {
                "zh": "用本课“银行柜台”的比喻，把一次 server.organization_manager.get_organization_by_id_async(...) 从进门到返回完整讲一遍，并想透四件事：(1) 那一行 async with db_registry.async_session() 为什么能“一行定两件事”——既是事务的 BEGIN/commit 边界，又是 actor/org 范围（apply_access_predicate）的注入点？(2) 为什么 ORM 行绝不出柜台、递出去的永远是 to_pydantic() 的复印件？这跟 finally 里的 expunge_all + close、以及 expire_on_commit=False 各自扣在哪？(3) 三个装饰器（enforce_types / raise_on_invalid_id / trace_method）分别定义在哪、按什么顺序叠、又“免费”换来了什么？(4) 既然 db_registry 自称“Dummy registry”、v0.16.8 还是 Postgres-only，那 SQLite/Postgres 的方言差异到底在哪一层被吃掉、为什么不该记到 db_registry 头上？",
                "en": "Use this lesson's “bank counter” metaphor to tell a single server.organization_manager.get_organization_by_id_async(...) as a whole — from the front door to the return — and think through four things: (1) Why can that one line async with db_registry.async_session() “fix two things at once” — being both the transaction's BEGIN/commit boundary and the injection point for the actor/org scope (apply_access_predicate)? (2) Why does an ORM row never leave the counter, with only the to_pydantic() copy handed out, and how does that clasp onto the finally's expunge_all + close and onto expire_on_commit=False? (3) Where is each of the three decorators (enforce_types / raise_on_invalid_id / trace_method) defined, in what order are they stacked, and what do they buy “for free”? (4) Given that db_registry calls itself a “Dummy registry” and v0.16.8 is Postgres-only, in which layer are the SQLite/Postgres dialect differences actually absorbed, and why shouldn't that be pinned on db_registry?",
            },
        ],
    },
    "26-crud-and-multitenancy.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 letta v0.16.8 里，多租户隔离（“只看你这个 org 的行”）到底是在哪一层、怎么强制的？",
                    "en": "In letta v0.16.8, at which layer — and how — is multi-tenant isolation (“see only your own org's rows”) actually enforced?",
                },
                "opts": [
                    {"zh": "焊在最底层的查询构造器里：SqlalchemyBase.apply_access_predicate 给每次读自动追加 WHERE organization_id == actor.organization_id",
                     "en": "Welded into the lowest-level query builder: SqlalchemyBase.apply_access_predicate auto-appends WHERE organization_id == actor.organization_id to every read"},
                    {"zh": "每个路由 / handler 自己记得在查询里手写一句 WHERE org==... 来过滤别的租户",
                     "en": "Each router / handler remembers to hand-write a WHERE org==... in its own query to filter other tenants"},
                    {"zh": "由 CheckPasswordMiddleware 在请求入口按 org 校验，挡掉别的租户",
                     "en": "CheckPasswordMiddleware checks by org at the request entrance and blocks other tenants"},
                    {"zh": "先把整张表查回来，再在 manager 里用 Python 按 actor.id 筛掉别的租户",
                     "en": "Pull the whole table back, then filter out other tenants by actor.id in Python inside the manager"},
                ],
                "answer": 0,
                "why": {
                    "zh": "隔离焊在最低层：orm/sqlalchemy_base.py::SqlalchemyBase.apply_access_predicate 是行级过滤的唯一注入点——ORGANIZATION 范围（默认）追加 where(organization_id == actor.organization_id)，USER 范围（仅 jobs / runs）追加 where(user_id == actor.id)。约 40 个模型共用这一个 SqlalchemyBase，read_async / list_async / size_async / bulk_hard_delete_async 都自动套上它，没有任何 per-endpoint 的 WHERE 需要各 handler 记得写——这正是“secure by default”的反转。它在 SQL 执行前注到 query 对象上、在 DB 侧完成，不是拉回全表再用 Python 筛。CheckPasswordMiddleware 管的是“能不能进这台服务器”（单一共享密钥），与租户正交，不做按 org 的行级过滤。",
                    "en": "Isolation is welded into the lowest layer: orm/sqlalchemy_base.py::SqlalchemyBase.apply_access_predicate is the single injection point for row-level filtering — the ORGANIZATION scope (default) appends where(organization_id == actor.organization_id), the USER scope (jobs / runs only) appends where(user_id == actor.id). Around 40 models share this one SqlalchemyBase, and read_async / list_async / size_async / bulk_hard_delete_async all auto-apply it, so there's no per-endpoint WHERE for any handler to remember — that's the “secure by default” inversion. It's injected onto the query object before the SQL runs and completed DB-side, not by pulling the whole table back and filtering in Python. CheckPasswordMiddleware governs “can you enter this server” (a single shared secret), is orthogonal to tenancy, and does no per-org row filtering.",
                },
            },
            {
                "q": {
                    "zh": "用你自己 org 的 actor 调 read_async 去读一行属于“别的 org”的数据，会发生什么？",
                    "en": "With an actor carrying your own org, you call read_async for a row that belongs to “another org.” What happens?",
                },
                "opts": [
                    {"zh": "那行被 predicate 的 WHERE 排除→read_async 抛 NoResultFound，list_async 返回 []",
                     "en": "The row is excluded by the predicate's WHERE → read_async raises NoResultFound, and list_async returns []"},
                    {"zh": "门禁识别出越权，直接抛一个 403 / 权限错误（PermissionError）",
                     "en": "The gate detects the violation and raises a 403 / permission error (PermissionError) outright"},
                    {"zh": "照常返回那一行——隔离只在写路生效，读路不拦",
                     "en": "It returns the row as usual — isolation only applies on the write path, reads aren't blocked"},
                    {"zh": "抛 ValueError，因为 actor 的 org 和那行的 org 不匹配",
                     "en": "It raises ValueError because the actor's org doesn't match the row's org"},
                ],
                "answer": 0,
                "why": {
                    "zh": "越权＝查不到，而非报错。apply_access_predicate 在 SQL 执行前就把 where(organization_id == actor.organization_id) 注进 query，别的 org 的行根本不进结果集：read_async 的 scalar_one_or_none() 拿到 None → 抛 NoResultFound；list_async 得 []。这是有意为之——连“那行存在”这件事都不向调用方泄露，所以不是 403、不是 PermissionError。唯一的 ValueError 来自 actor 连 org / id accessor 都没有（配置错），而非跨租户。隔离也不是“只在写路”——读路四个方法（有 actor 时）都套 predicate，写 / 删则骑在读建立的边界上。调试时别被 NoResultFound 骗了：先确认 actor 的 org 对不对。",
                    "en": "A violation = not found, not an error. apply_access_predicate injects where(organization_id == actor.organization_id) onto the query before the SQL runs, so another org's row never enters the result set: read_async's scalar_one_or_none() gets None → raises NoResultFound; list_async gets []. This is by design — it leaks nothing about “that row exists,” so it's not a 403 and not a PermissionError. The only ValueError comes from an actor lacking even the org / id accessor (a misconfig), not from cross-tenant access. Isolation isn't “write-path only” either — the four read methods (when an actor is present) all apply the predicate, while write / delete ride the boundary the read established. When debugging, don't be fooled by NoResultFound: first check that the actor's org is right.",
                },
            },
            {
                "q": {
                    "zh": "约 40 个模型共用的 SqlalchemyBase.delete_async，默认到底“删”了什么？",
                    "en": "What does the shared SqlalchemyBase.delete_async actually “delete” by default?",
                },
                "opts": [
                    {"zh": "软删：只把 is_deleted 翻成 True，行仍留在库里；读路默认（check_is_deleted=False）仍能查到它",
                     "en": "A soft delete: it only flips is_deleted to True; the row stays in the table, and the read path still finds it by default (check_is_deleted=False)"},
                    {"zh": "物理删：session.delete(self) 把整行从库里抹掉，之后再也查不到",
                     "en": "A physical delete: session.delete(self) wipes the whole row from the table, never findable again"},
                    {"zh": "软删，但读路默认会自动过滤掉软删行，所以删完立刻就查不到了",
                     "en": "A soft delete, but the read path auto-filters soft-deleted rows by default, so it's immediately unfindable"},
                    {"zh": "先级联删掉所有外键关联行，再物理删本行",
                     "en": "It cascades through all foreign-key rows first, then physically deletes this row"},
                ],
                "answer": 0,
                "why": {
                    "zh": "delete_async 是软删：内部走 update_async 把 is_deleted 翻成 True（有 actor 则顺手盖审计），行的字节一个没动、外键关联照旧。关键反直觉点：读路过滤是 opt-in——read_async / list_async 的 check_is_deleted 默认 False，不追加 where(is_deleted == False)，所以软删行默认仍被返回；想挡掉得显式传 check_is_deleted=True（如 provider_manager 的读路）。物理删是另外两个方法：hard_delete_async（session.delete(self) + 死锁重试）和 bulk_hard_delete_async（delete(cls).where(id.in_(...)) + apply_access_predicate，唯一在 SQL 层强制租户的删）。delete_async 自己不级联物理删。",
                    "en": "delete_async is a soft delete: internally it goes through update_async to flip is_deleted to True (stamping audit too if there's an actor); not a byte of the row moves and foreign-key relations stay intact. The key counterintuitive point: read-side filtering is opt-in — read_async / list_async default check_is_deleted to False and don't append where(is_deleted == False), so soft-deleted rows are still returned by default; to keep them out you must pass check_is_deleted=True explicitly (as in provider_manager's read path). Physical deletion is the other two methods: hard_delete_async (session.delete(self) + deadlock retry) and bulk_hard_delete_async (delete(cls).where(id.in_(...)) + apply_access_predicate, the only delete that enforces tenancy at the SQL level). delete_async itself does not cascade-physically-delete.",
                },
            },
            {
                "q": {
                    "zh": "每行的审计字段（created_at / updated_at、_created_by_id / _last_updated_by_id）是怎么被填上的？",
                    "en": "How do a row's audit fields (created_at / updated_at, _created_by_id / _last_updated_by_id) get filled in?",
                },
                "opts": [
                    {"zh": "CRUD 方法里显式调 _set_created_and_updated_by_fields(actor_id) 盖“谁”，且只有传了 actor 才盖",
                     "en": "The CRUD methods explicitly call _set_created_and_updated_by_fields(actor_id) to stamp the “who,” only when an actor is passed"},
                    {"zh": "靠 SQLAlchemy 的事件监听（event listener）在 flush 时自动给每行填上",
                     "en": "SQLAlchemy event listeners fill them in automatically on flush"},
                    {"zh": "全部由数据库触发器（trigger）在 INSERT / UPDATE 时生成，应用层不参与",
                     "en": "Database triggers generate them all on INSERT / UPDATE; the app layer isn't involved"},
                    {"zh": "由基类构造函数统一填，不管有没有 actor 都会盖上“谁建 / 谁改”",
                     "en": "The base class constructor fills them uniformly, stamping “who created / changed” whether or not there's an actor"},
                ],
                "answer": 0,
                "why": {
                    "zh": "审计字段不是事件监听、也不是 DB 触发器盖的，而是 CRUD 路径里显式调 orm/base.py::CommonSqlalchemyMetaMixins 的 _set_created_and_updated_by_fields(actor_id)——create_async / update_async 手动点一下。关键前提：只有传了 actor 才盖“谁”；没 actor 的写（系统内部路径）不落 *_by_id，只有时间列照常。时间列确实交给 DB：created_at 用 server_default=func.now()，updated_at 再加 server_onupdate（不依赖应用时钟）。物理列名带下划线 _created_by_id / _last_updated_by_id，对外属性去掉下划线，setter 还断言 id 前缀＝“user”。created_by_id 只在首次写设定、此后不变；last_updated_by_id 每次写刷新。",
                    "en": "Audit fields aren't stamped by event listeners or DB triggers but by an explicit call in the CRUD path to orm/base.py::CommonSqlalchemyMetaMixins's _set_created_and_updated_by_fields(actor_id) — create_async / update_async touch it manually. The key precondition: it stamps the “who” only when an actor is passed; a write without an actor (a system-internal path) records no *_by_id, only the time columns as usual. The time columns are indeed left to the DB: created_at uses server_default=func.now(), and updated_at adds server_onupdate (not relying on the app clock). The physical columns carry an underscore, _created_by_id / _last_updated_by_id; the outward attributes drop it, and the setter asserts the id prefix = “user.” created_by_id is set only on the first write and never changes; last_updated_by_id refreshes on every write.",
                },
            },
            {
                "q": {
                    "zh": "对一个 org 级模型做读取，但没传 actor（actor=None）时，SqlalchemyBase 会怎么做？",
                    "en": "When you read an org-scoped model but pass no actor (actor=None), what does SqlalchemyBase do?",
                },
                "opts": [
                    {"zh": "不硬失败：打一条 SECURITY: ...bypasses organization filtering 警告，然后无范围（不套 predicate）照常跑查询",
                     "en": "It doesn't hard-fail: it logs a SECURITY: ...bypasses organization filtering warning, then runs the query unscoped (no predicate applied)"},
                    {"zh": "直接拒绝：抛异常 / 报错，强制每次读都必须带 actor",
                     "en": "It rejects outright: raises an exception / error, forcing every read to carry an actor"},
                    {"zh": "自动套上 DEFAULT_USER_ID 当 actor，于是查询被限定到默认 org",
                     "en": "It auto-substitutes DEFAULT_USER_ID as the actor, so the query gets scoped to the default org"},
                    {"zh": "静默返回空结果（[] / None），当作“没有任何行可见”",
                     "en": "It silently returns an empty result ([] / None), treating it as “no rows visible”"},
                ],
                "answer": 0,
                "why": {
                    "zh": "actor=None 时 base 不硬失败：read_async 里 predicate 是 gated on if actor:——没 actor 就跳过 apply_access_predicate，并对 org 级模型记一条响亮的 logger.warning(“SECURITY: ... bypasses organization filtering”)，然后无范围照跑（返回的是该 org 之外也不设限的全表行，不是空）。这是有意取舍：Letta 有合法的、系统内部无 user 的查询，于是选了“中央强制 + 响亮日志”而非脆弱的硬失败。别和入口混淆：真正能“强制带身份”的是 user_manager.py::get_actor_or_default_async——当 settings.no_default_actor 且无 id 时抛 NoResultFound，否则才回退 DEFAULT_USER_ID；那是解析 actor 的入口逻辑，不是 SqlalchemyBase 在 actor=None 时自己做的事。",
                    "en": "When actor=None the base does not hard-fail: in read_async the predicate is gated on if actor: — with no actor it skips apply_access_predicate and, for an org-scoped model, logs a loud logger.warning(“SECURITY: ... bypasses organization filtering”), then runs unscoped (returning unrestricted rows across the table, not empty). This is a deliberate trade-off: Letta has legitimate system-internal queries with no user, so it chose “central enforcement + a loud log” over brittle hard failure. Don't conflate this with the entrance: the thing that can actually “force identity” is user_manager.py::get_actor_or_default_async — it raises NoResultFound when settings.no_default_actor and no id, otherwise it falls back to DEFAULT_USER_ID; that's the actor-resolution entry logic, not what SqlalchemyBase itself does when actor=None.",
                },
            },
        ],
        "open": [
            {
                "zh": "用本课“带门禁的共享档案库”的比喻，把一次“按 id 读一行”的查询从进门到落库完整讲一遍，并想透四件事：(1) 为什么说多租户隔离是“焊在最低层的查询构造器里”、而不是每个 handler 各写一句 WHERE？apply_access_predicate 的 ORGANIZATION 与 USER 两个分支分别按什么字段限定、各覆盖哪些对象？(2) 跨租户读为什么是“查不到”（NoResultFound / []）而不是 403？这种“连存在性都隔离”的设计买到了什么、又给调试埋了什么坑？(3) delete_async 的“软删”默认可逆意味着什么——is_deleted 翻 True 之后，为什么读路默认仍能看见它、要怎样才“看起来真的删了”？软删 vs hard_delete_async vs bulk_hard_delete_async 三者在“是否套 predicate”上有何不同？(4) actor 这条身份链（user_id header → get_headers 只校格式不碰 DB → get_actor_or_default_async 解析成带 org 的 PydanticUser → predicate 的 WHERE）里，为什么 base 在 actor=None 时选择“警告 + 无范围照跑”而非硬失败？这跟服务器口令（CheckPasswordMiddleware）那道正交的闸又是什么关系？",
                "en": "Using this lesson's “shared archive with a gate” metaphor, narrate a single “read one row by id” query from the front door to the DB, and think through four things: (1) Why is multi-tenant isolation “welded into the lowest-level query builder” rather than each handler hand-writing a WHERE? In apply_access_predicate, what field does each of the ORGANIZATION and USER branches scope by, and which objects does each cover? (2) Why is a cross-tenant read “not found” (NoResultFound / []) rather than a 403? What does this “isolate even existence” design buy, and what debugging trap does it set? (3) What does delete_async's reversible-by-default “soft delete” mean — after is_deleted flips to True, why does the read path still see it by default, and what makes it “look truly deleted”? How do soft delete vs hard_delete_async vs bulk_hard_delete_async differ on “whether the predicate is applied”? (4) In the actor identity chain (user_id header → get_headers validates format without touching the DB → get_actor_or_default_async resolves it into a PydanticUser with org → the predicate's WHERE), why does the base choose “warn + run unscoped” rather than hard-fail when actor=None? And how does that relate to the orthogonal server-password gate (CheckPasswordMiddleware)?",
            },
        ],
    },
    "27-dual-db-and-vectors.html": {
        "mcq": [
            {
                "q": {
                    "zh": "在 letta v0.16.8 里，“这个进程到底用 SQLite 还是 Postgres”由什么决定？",
                    "en": "In letta v0.16.8, what actually decides whether a process uses SQLite or Postgres?",
                },
                "opts": [
                    {"zh": "派生 @property settings.database_engine：配了 PG URI（letta_pg_uri_no_default 非 None）就是 Postgres，否则 SQLite",
                     "en": "The derived @property settings.database_engine: a configured PG URI (letta_pg_uri_no_default not None) means Postgres, otherwise SQLite"},
                    {"zh": "环境变量 LETTA_DATABASE_ENGINE=sqlite|postgres，手动二选一",
                     "en": "An env var LETTA_DATABASE_ENGINE=sqlite|postgres, a manual either/or"},
                    {"zh": "server/db.py 启动时按可用驱动探测：装了 asyncpg 就走 Postgres，否则 SQLite",
                     "en": "server/db.py probes available drivers at startup: with asyncpg installed it goes Postgres, else SQLite"},
                    {"zh": "看 letta_pg_uri 是否为 None——为 None 就回退 SQLite",
                     "en": "Whether letta_pg_uri is None — if None it falls back to SQLite"},
                ],
                "answer": 0,
                "why": {
                    "zh": "决定权在 settings.py::Settings.database_engine，它是只读 @property，逻辑就一行：POSTGRES if self.letta_pg_uri_no_default else SQLITE。所以“配没配 PG URI”是 dev/prod 的唯一分界；DatabaseChoice(str, Enum) 只有 POSTGRES / SQLITE 两值，是被读出来的结论而非可写字段。没有 LETTA_DATABASE_ENGINE 这种开关——你只要设了任意 LETTA_PG_*（host/db/user/password/port/uri）就会静默翻成 Postgres。陷阱：letta_pg_uri 永远有默认值（postgresql+pg8000://letta:letta@localhost:5432/letta），判定不能看它，真正“URI-或-None”的是 letta_pg_uri_no_default。也不是按驱动探测：server/db.py 模块级只 create_async_engine(async_pg_uri)，不做后端探测。",
                    "en": "The decision lives in settings.py::Settings.database_engine, a read-only @property whose logic is one line: POSTGRES if self.letta_pg_uri_no_default else SQLITE. So “is a PG URI configured” is the only dev/prod divider; DatabaseChoice(str, Enum) has just POSTGRES / SQLITE and is a conclusion read out, not a writable field. There is no LETTA_DATABASE_ENGINE switch — set any LETTA_PG_* (host/db/user/password/port/uri) and it silently flips to Postgres. The trap: letta_pg_uri always has a default (postgresql+pg8000://letta:letta@localhost:5432/letta), so the check can't read it — the real “URI-or-None” is letta_pg_uri_no_default. It isn't driver probing either: server/db.py at module level only does create_async_engine(async_pg_uri) and detects no backend.",
                },
            },
            {
                "q": {
                    "zh": "“一套 ORM 在两套库上跑”，这个双库接缝主要落在代码哪里？",
                    "en": "For “one ORM running on two databases,” where in the code does the dual-DB seam mainly live?",
                },
                "opts": [
                    {"zh": "分布在多处、大多声明式：列类型、查询分支、连接事件、自定义列、alembic——不在某一个 switch 里",
                     "en": "Distributed across several places, mostly declarative: column type, query branch, connect event, custom columns, alembic — not in any single switch"},
                    {"zh": "集中在 server/db.py 一个 if database_engine 大开关里，按后端建不同引擎",
                     "en": "Concentrated in one big if database_engine switch inside server/db.py, building a different engine per backend"},
                    {"zh": "由 SQLAlchemy 的方言层自动处理，应用代码完全不含分库逻辑",
                     "en": "Handled automatically by SQLAlchemy's dialect layer; the application code contains no dual-DB logic at all"},
                    {"zh": "每个 manager 在自己的方法里各写一段 if sqlite/else postgres 来切换",
                     "en": "Each manager writes its own if sqlite/else postgres block inside its methods to switch"},
                ],
                "answer": 0,
                "why": {
                    "zh": "双库不是 server/db.py 里的聪明 switch——v0.16.8 它其实是 Postgres-only async（模块级只 create_async_engine(async_pg_uri)，不按 database_engine 分叉、不加载 sqlite-vec）。真正的接缝分布在约六处、且大多 import 期声明：① settings.database_engine 这个派生 property；② orm/passage.py::BasePassage 类体里、import 期的 if POSTGRES: Vector(MAX_EMBEDDING_DIM) else CommonVector；③ 查询构造器两路 order_by（sqlalchemy_base.py 与 services/helpers/agent_manager_helper.py）；④ orm/sqlite_functions.py::register_functions 用 @event.listens_for(Engine, “connect”) 给任何 SQLite 连接注册 numpy cosine_distance；⑤ orm/custom_columns.py 的 TypeDecorator；⑥ alembic/env.py 选 URI、分两后端建表。唯一还构造 SQLite URI 的地方就是 alembic/env.py。也不是 manager 各写分支：分叉只在用到向量搜索处各写一次。",
                    "en": "The dual DB isn't a clever switch in server/db.py — in v0.16.8 that file is Postgres-only async (module level only create_async_engine(async_pg_uri), no branch on database_engine, no sqlite-vec loaded). The real seam is distributed across ~six places, most declared at import time: (1) the derived settings.database_engine property; (2) orm/passage.py::BasePassage's class-body, import-time if POSTGRES: Vector(MAX_EMBEDDING_DIM) else CommonVector; (3) the two-way order_by in the query builder (sqlalchemy_base.py and services/helpers/agent_manager_helper.py); (4) orm/sqlite_functions.py::register_functions using @event.listens_for(Engine, “connect”) to register a numpy cosine_distance on any SQLite connection; (5) orm/custom_columns.py's TypeDecorators; (6) alembic/env.py picking the URI and building tables for two backends. The only place that still builds a SQLite URI is alembic/env.py. It isn't per-manager branches either — the fork only appears where vector search is used.",
                },
            },
            {
                "q": {
                    "zh": "向量在 Postgres 与 SQLite 两套库里分别怎么存、怎么搜？",
                    "en": "How are vectors stored and searched in Postgres versus SQLite?",
                },
                "opts": [
                    {"zh": "Postgres：pgvector 的 Vector(4096) + 原生算子 &lt;=&gt;；SQLite：CommonVector(BINARY) + numpy cosine_distance UDF",
                     "en": "Postgres: pgvector's Vector(4096) + the native operator &lt;=&gt;; SQLite: CommonVector(BINARY) + a numpy cosine_distance UDF"},
                    {"zh": "两套库都用 pgvector 的 Vector 列与原生 &lt;=&gt;，SQLite 靠 sqlite-vec 扩展提供同款算子",
                     "en": "Both databases use pgvector's Vector column and the native &lt;=&gt;, with SQLite getting the same operator from the sqlite-vec extension"},
                    {"zh": "两套库都把向量存成 JSON 文本，搜索时在 Python 里反序列化后算 cosine",
                     "en": "Both store vectors as JSON text and, at search time, deserialize in Python to compute cosine"},
                    {"zh": "SQLite 用 sqlite-vec 的原生 KNN 索引，Postgres 反而是全表暴力没有索引",
                     "en": "SQLite uses sqlite-vec's native KNN index, while Postgres is the brute-force one with no index"},
                ],
                "answer": 0,
                "why": {
                    "zh": "存：Postgres 是 pgvector 的 Vector(4096) 定长列；SQLite 是 orm/custom_columns.py::CommonVector——impl=BINARY 的 TypeDecorator，用 sqlite_vec.serialize_float32 打包、np.frombuffer 还原。搜：列类型与搜索分支共用一个 if settings.database_engine is POSTGRES（orm/passage.py::BasePassage import 期定列类型；sqlalchemy_base.py / agent_manager_helper.py 运行时分支）。Postgres 走 cls.embedding.cosine_distance(q) → 编译成原生 &lt;=&gt;，可挂 ivfflat / hnsw 做 ANN；SQLite 走 func.cosine_distance(col, q) → 调 orm/sqlite_functions.py::register_functions 注册的 numpy UDF，对全表逐行算再 ORDER BY ASC。关键纠正：SQLite 的相似度不是 sqlite-vec 原生——sqlite_vec.load() 是注释掉的，只借了它的 serialize_float32 打包字节。两边语义一致（按 cosine 升序取最近），只是一个有 ANN、一个全表暴力。",
                    "en": "Storage: Postgres is pgvector's Vector(4096) fixed-length column; SQLite is orm/custom_columns.py::CommonVector — an impl=BINARY TypeDecorator packing with sqlite_vec.serialize_float32 and restoring with np.frombuffer. Search: the column type and the search branch share one if settings.database_engine is POSTGRES (orm/passage.py::BasePassage fixes the column type at import time; sqlalchemy_base.py / agent_manager_helper.py branch at runtime). Postgres uses cls.embedding.cosine_distance(q) → compiles to native &lt;=&gt; and can attach ivfflat / hnsw for ANN; SQLite uses func.cosine_distance(col, q) → the numpy UDF registered by orm/sqlite_functions.py::register_functions, computed row by row over the whole table then ORDER BY ASC. Key correction: SQLite's similarity is not sqlite-vec native — sqlite_vec.load() is commented out; only its serialize_float32 is borrowed to pack bytes. Both are semantically the same (nearest by ascending cosine); one just has ANN, the other brute-forces the whole table.",
                },
            },
            {
                "q": {
                    "zh": "所有 embedding 都被 np.pad 到 MAX_EMBEDDING_DIM=4096（尾部补 0）。为什么这对相似度搜索是“免费”的？",
                    "en": "Every embedding is np.padded to MAX_EMBEDDING_DIM=4096 (zeros at the tail). Why is this “free” for similarity search?",
                },
                "opts": [
                    {"zh": "等量补 0 既不改点积、也不改 L2 范数，于是 cosine 与未填充时数学上完全相等，排序一模一样",
                     "en": "Equal zero-padding changes neither the dot product nor the L2 norm, so cosine is mathematically identical to the unpadded vector and the ranking is unchanged"},
                    {"zh": "因为搜索前会把补的 0 再切掉，只比较原始维度，所以毫无影响",
                     "en": "Because the padding zeros are sliced off again before search, so only the original dims are compared and there's no effect"},
                    {"zh": "因为 cosine 会先做 L2 归一化，归一化能消除任何长度差异，所以补什么都行",
                     "en": "Because cosine first L2-normalizes the vectors, and normalization erases any length difference, so any padding works"},
                    {"zh": "因为补的是很小的随机数，对高维点积的影响可以忽略不计",
                     "en": "Because the padding is tiny random numbers whose effect on a high-dimensional dot product is negligible"},
                ],
                "answer": 0,
                "why": {
                    "zh": "cosine = 点积 /（两向量 L2 范数之积）。尾部补的全是 0：点积里每个新增项是 0 × x = 0，分子不变；L2 里每个新增项是 0² = 0，分母不变。分子分母都不动，cosine 值与排序就和未填充严格相等——这是恒等式，不是近似。所以 constants.py::MAX_EMBEDDING_DIM=4096 把任意维度零填充到定长，一个 Vector(4096)/CommonVector 列即可装下任意模型的输出，且不影响检索排序。注意几个错误项：并没有“搜索前切掉 0”这一步（写路与查询路都补到 4096 再比，是共同前提）；补的是 0 而非随机数；cosine 确实含归一化，但“免费”的根因是补 0 同时不改点积与范数，而非归一化能抹掉任意填充。代价仅是多存一串 0（如 1024 维白存 3072 个 0）。",
                    "en": "Cosine = dot product / (product of the two L2 norms). The tail padding is all zeros: in the dot product each added term is 0 × x = 0, so the numerator is unchanged; in the L2 norm each added term is 0² = 0, so the denominator is unchanged. With neither moving, the cosine value and the ranking are exactly equal to the unpadded case — an identity, not an approximation. So constants.py::MAX_EMBEDDING_DIM=4096 zero-pads any dimension to a fixed length, letting one Vector(4096)/CommonVector column hold any model's output without affecting retrieval order. Watch the wrong options: there is no “slice the zeros off before search” step (both write and query pad to 4096 before comparing — a shared precondition); the padding is zeros, not random numbers; and although cosine does include normalization, the reason it's “free” is that zero-padding leaves both dot product and norm unchanged, not that normalization erases arbitrary padding. The only cost is storing extra zeros (e.g. 3072 wasted zeros for a 1024-dim model).",
                },
            },
            {
                "q": {
                    "zh": "把 EmbeddingConfig / LLMConfig 这类配置整块 model_dump 成一列 JSON（而非拆成多列），买到了什么、代价是什么？",
                    "en": "Storing configs like EmbeddingConfig / LLMConfig as one whole model_dumped JSON column (instead of splitting into many columns) — what does it buy, and what does it cost?",
                },
                "opts": [
                    {"zh": "买到扁平 schema + schema-on-read 演化（加字段免迁移）；代价是子字段不能 WHERE / 建索引，且每次读写都要 (de)序列化",
                     "en": "Buys a flat schema + schema-on-read evolution (adding a field needs no migration); costs the inability to WHERE / index subfields, plus (de)serialization on every read/write"},
                    {"zh": "买到对任意子字段高效 WHERE / 建索引；代价是每加一个字段都要写一次 alembic 迁移",
                     "en": "Buys efficient WHERE / indexing on any subfield; costs an alembic migration for every new field"},
                    {"zh": "买到跨表外键与 JOIN 的能力；代价是失去 pydantic 的类型校验",
                     "en": "Buys cross-table foreign keys and JOINs; costs the loss of pydantic's type validation"},
                    {"zh": "买到更小的存储体积与更快的查询；没有任何实际代价",
                     "en": "Buys smaller storage and faster queries, with no real cost at all"},
                ],
                "answer": 0,
                "why": {
                    "zh": "orm/custom_columns.py 的 TypeDecorator（EmbeddingConfigColumn / LLMConfigColumn / ToolRulesColumn，impl=JSON、cache_ok=True）把整个 pydantic 对象一格存下：process_bind_param 写时 model_dump(mode=“json”) → dict，process_result_value 读时 dict → Model(**data) 还原（真正转换委托 helpers/converters.py）。买到两样：① 扁平 schema + 免迁移——给 LLMConfig 加 pydantic 字段不动表结构，老行靠 deserialize_llm_config 在读时补默认（schema-on-read）；② 保真——嵌套结构不被拍平，读回仍是强类型对象。代价两样：① JSON 子字段不能高效 WHERE / 建索引（没法“按 embedding 模型名筛选”）；② 每次读写都跑一遍 (de)序列化，有 CPU 开销。impl=JSON 在 Postgres 落成 JSONB、SQLite 落成文本，但对上层透明。对配置多变、又很少按子字段查询的 Letta，这笔账划算。",
                    "en": "The TypeDecorators in orm/custom_columns.py (EmbeddingConfigColumn / LLMConfigColumn / ToolRulesColumn, impl=JSON, cache_ok=True) store the whole pydantic object in one cell: process_bind_param writes via model_dump(mode=“json”) → dict, and process_result_value reads dict → Model(**data) to restore it (the real conversion delegated to helpers/converters.py). It buys two things: (1) a flat schema + no migration — adding a pydantic field to LLMConfig leaves the table schema untouched, and old rows get defaults filled on read by deserialize_llm_config (schema-on-read); (2) fidelity — nested structure isn't flattened, and it reads back as a strongly-typed object. It costs two things: (1) JSON subfields can't be efficiently put in a WHERE or indexed (no “filter by embedding model name”); (2) every read/write runs a round of (de)serialization, a CPU cost. impl=JSON lands as JSONB on Postgres and text on SQLite, but that's transparent to the upper layers. For Letta — configs that change a lot and are rarely queried by subfield — it pays off.",
                },
            },
        ],
        "open": [
            {
                "zh": "用本课“一张蓝图、两座工厂”的比喻，把“一条 archival 记忆从写入到按相似度被搜出来”完整讲一遍，并想透四件事：(1) 为什么说“用哪套库”不是 server/db.py 里的一个聪明 switch，而是散在六处、大多 import 期就声明好的接缝？settings.database_engine 这个 @property 凭什么判定 Postgres / SQLite，又为什么不能用 LETTA_DATABASE_ENGINE 手动选？(2) 同一个 Passage 模型，为什么 Postgres 落成 pgvector 的 Vector(4096)、SQLite 落成 CommonVector(BINARY)？那个“列类型在 import 期烤进模型”的 if，为什么意味着一个进程运行时不能切库？(3) 同一句“按相似度排序”，怎么在 Postgres 编译成原生 &lt;=&gt;（可 ANN）、在 SQLite 变成 numpy UDF 全表暴力？为什么 sqlite_vec.load() 注释掉了、却还要 import sqlite_vec？(4) 为什么把任意维度 np.pad 到 4096 对 cosine 排序是“免费”的（请从点积与 L2 范数说清）？再把 pydantic-in-DB 那列 JSON 的“免迁移 + 保真”红利与“子字段不可索引 + 序列化开销”代价摆到一起权衡。最后回到那个诚实星号：v0.16.8 的 server/db.py 只建 Postgres，这跟“双库故事完整活在 ORM 与 alembic”是否矛盾？",
                "en": "Using this lesson's “one blueprint, two factories” metaphor, narrate a single archival memory from being written to being searched out by similarity, and think through four things: (1) Why is “which database” not a clever switch in server/db.py but a seam scattered across six places, most declared at import time? On what basis does the settings.database_engine @property decide Postgres / SQLite, and why can't you pick it by hand with LETTA_DATABASE_ENGINE? (2) For the same Passage model, why does Postgres land as pgvector's Vector(4096) and SQLite as CommonVector(BINARY)? Why does that “bake the column type into the model at import time” if mean a process can't switch databases at runtime? (3) How does the same “order by similarity” compile into the native &lt;=&gt; (ANN-capable) on Postgres and into a numpy UDF brute-force over the whole table on SQLite? And why is sqlite_vec still imported even though sqlite_vec.load() is commented out? (4) Why is np.padding any dimension to 4096 “free” for cosine ranking (explain it from the dot product and the L2 norm)? Then weigh the pydantic-in-DB JSON column's “no-migration + fidelity” payoff against its “non-indexable subfields + serialization overhead” cost. Finally, return to the honest asterisk: v0.16.8's server/db.py only builds Postgres — does that contradict “the dual-DB story lives fully in the ORM and alembic”?",
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
