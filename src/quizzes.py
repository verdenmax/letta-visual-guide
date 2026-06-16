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
