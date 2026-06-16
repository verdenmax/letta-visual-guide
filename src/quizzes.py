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
