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
