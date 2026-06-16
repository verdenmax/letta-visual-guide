# Letta 图解教程 · M0 脚手架 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 立起 Letta 图解教程的纯 Python 零依赖静态站点生成器，换皮成 Letta 主题、双语可切换，跑通"构建 + 死链校验 + 结构校验"，并产出 1 课基线 + 目录页。

**Architecture:** 完全复用 `/home/verden/course/llama-cpp-visual-guide` 的生成器：`src/shell.py`（设计系统 CSS + 导航 + 双语 JS + `PAGES`）、`registry.py`（文件名→双语内容）、`partN.py`（课程内容）、`quizzes.py`、`build.py`、`check_links.py`、`check_html.py`。M0 以"**复制参考文件 + 定点换皮**"为主，新写的只有 `part1.py` 的基线课与 `registry.py`。验证手段不是单元测试，而是 `build.py`（产出 HTML）+ `check_links.py`（死链）+ `check_html.py`（结构/漂移）三件套全过。

**Tech Stack:** Python 3.11+（仅标准库，零第三方依赖）；输出自包含 HTML/CSS/JS，可 `file://` 直接打开。

> 前置依赖：参考项目 `/home/verden/course/llama-cpp-visual-guide`（与本仓库平级）必须存在，M0 多处从其 `src/` 复制文件。所有命令默认在仓库根 `/home/verden/course/letta-visual-guide` 执行。

---

## File Structure（M0 产出）

```
letta-visual-guide/
├── .gitignore                  ← 忽略 __pycache__
├── README.md                   ← 极简构建说明（M9 再扩写）
├── index.html                  ← 由 build.py 生成（目录页）
├── lessons/
│   └── 01-what-is-letta.html   ← 由 build.py 生成
└── src/
    ├── shell.py                ← 复制参考 + 换皮（主题色/品牌/PAGES/SUBTITLES）
    ├── registry.py             ← 新写：CONTENT = {"01-what-is-letta.html": part1.LESSON_01}
    ├── part1.py                ← 新写：LESSON_01 基线课（双语）
    ├── quizzes.py              ← 新写：render 机制 + QUIZZES = {}（M9 再补题）
    ├── build.py                ← 复制参考（无需改动）
    ├── check_links.py          ← 复制参考 + 改 PDF 文件名
    └── check_html.py           ← 复制参考 + 改 MAX_LESSON / SOFT_EXEMPT
```

每个文件单一职责：`shell.py` 管样式与外壳；`registry.py` 是内容单一事实源；`partN.py` 只放课程正文；`quizzes.py` 只管自测；三个脚本分别管构建、死链、结构。

---

## Task 1: 仓库基础文件（.gitignore）

**Files:**
- Create: `/home/verden/course/letta-visual-guide/.gitignore`

- [ ] **Step 1: 写 .gitignore**

```
__pycache__/
*.pyc
.DS_Store
print-zh.html
print-en.html
*.pdf
```

- [ ] **Step 2: 提交**

```bash
cd /home/verden/course/letta-visual-guide
git add .gitignore
git commit -m "chore: add .gitignore for letta visual guide"
```

---

## Task 2: 移植并换皮 src/shell.py

**Files:**
- Create: `src/shell.py`（从 `../llama-cpp-visual-guide/src/shell.py` 复制后定点修改）

- [ ] **Step 1: 复制参考 shell.py**

```bash
cd /home/verden/course/letta-visual-guide
mkdir -p src
cp ../llama-cpp-visual-guide/src/shell.py src/shell.py
```

- [ ] **Step 2: 机械换色 / 换品牌（sed）**

主题色：暖橙 → Letta 靛蓝紫；favicon 文字 `ll`→`L`，emoji 🦙→🧠；站点名 llama.cpp→Letta。

```bash
cd /home/verden/course/letta-visual-guide/src
# 内部标识符换前缀：lcvg(llama-cpp-visual-guide) -> lvg(letta-visual-guide)
# 即 lvgToggleLang() 与 localStorage 键 'lvg-lang'，避免与参考站点同源串味
sed -i 's/lcvg/lvg/g' shell.py
# 模块 docstring 里的遗留品牌名
sed -i 's/for the llama\.cpp visual guide/for the Letta visual guide/' shell.py
# 主题色（亮色 accent / accent-soft / accent-ink；#c2630e 同时是 theme-color 与 favicon 填充）
sed -i 's/#c2630e/#6d5efc/g; s/#fbeede/#ecebfe/g; s/#8a4708/#4733cf/g' shell.py
# 主题色（暗色 accent / accent-soft / accent-ink）
sed -i 's/#e8923f/#9d8cff/g; s/#3a2410/#211a45/g; s/#f3b673/#c8bcff/g' shell.py
# favicon 文字与角标 emoji
sed -i 's|>ll</text>|>L</text>|; s/🦙/🧠/g' shell.py
# 站点品牌名（标题/导航/og:site_name 等所有出现处）
sed -i 's/llama\.cpp 图解教程/Letta 图解教程/g; s/llama\.cpp Visual Guide/Letta Visual Guide/g' shell.py
```

- [ ] **Step 3: 验证机械替换无残留**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
grep -nF '🦙' shell.py; grep -nF 'llama.cpp 图解教程' shell.py; grep -nF '#c2630e' shell.py; grep -nF 'lcvg' shell.py; grep -niF 'llama' shell.py
```
Expected: 五条命令均**无输出**（grep 退出码 1）。若某条仍有输出，用 `perl -CSD -i -pe 's/.../.../g' shell.py` 重做该替换。

- [ ] **Step 4: 替换 PAGES（M0 只含第 1 课）**

把 `shell.py` 里整段 `PAGES = [ ... ]`（从 `PAGES = [` 到对应的 `]`）替换为：

```python
PAGES = [
    ("01-what-is-letta.html", "Letta / MemGPT 是什么", "What is Letta / MemGPT",
     "第一部分 · 宏观全景", "Part 1 · The Big Picture"),
]
```

- [ ] **Step 5: 替换 SUBTITLES（M0 只留第 1 课）**

把 `shell.py` 里整段 `SUBTITLES = { ... }` 替换为：

```python
# Per-lesson TOC subtitle: filename -> (zh, en). Missing entries render blank.
SUBTITLES = {
    "01-what-is-letta.html": ("LLM 无状态 + 上下文有限 · 有状态记忆 agent",
                              "Stateless LLM + finite context; stateful memory agents"),
}
```

- [ ] **Step 6: 改写目录页 hero 文案（index_page 内，llama 专属散文）**

在 `index_page()` 中做三处替换（sed 已把"站点名"换好，这里改剩余的 llama 专属句子）：

(a) `desc`：把
```python
    desc = ("从零理解整个 llama.cpp 项目的中英双语图解教程：宏观结构、用法、ggml 引擎、"
            "llama 推理内部、底层内核，每课配真实源码对应、折叠深挖与设计亮点。")
```
改成
```python
    desc = ("从零理解整个 Letta（原 MemGPT）项目的中英双语图解教程：宏观结构、记忆系统、"
            "agent 执行循环、工具与 LLM provider、服务端与持久化，每课配真实源码对应、折叠深挖与设计亮点。")
```

(b) `<h1>`：把
```python
    <h1><span class="lang-zh">用图解理解整个 llama.cpp 项目</span><span class="lang-en">Understand the whole llama.cpp project, visually</span></h1>
```
改成
```python
    <h1><span class="lang-zh">用图解理解整个 Letta 项目</span><span class="lang-en">Understand the whole Letta project, visually</span></h1>
```

(c) `lead` 段与底部说明：把
```python
    <p class="lead"><span class="lang-zh">这套教程带你<strong>层层深入</strong>：先建立<strong>宏观全景</strong>，再学会<strong>使用</strong>，
    然后深入 <strong>ggml 引擎</strong>与 <strong>llama 推理内部</strong>，最后直抵<strong>底层内核</strong>。每课配真实源码对应、图解与设计亮点。</span>
    <span class="lang-en">A layered tour: build the <strong>big picture</strong> first, learn to <strong>use</strong> it,
    then dive into the <strong>ggml engine</strong> and <strong>llama inference internals</strong>, down to the <strong>low-level kernels</strong>. Every lesson maps to real source, with diagrams and design insights.</span></p>
```
改成
```python
    <p class="lead"><span class="lang-zh">这套教程带你<strong>层层深入</strong>：先建立<strong>宏观全景</strong>，再打牢<strong>前置基础</strong>，
    然后深入 Letta 的灵魂——<strong>三层记忆系统</strong>与 <strong>agent 执行循环</strong>，再到<strong>工具、LLM provider、服务端与持久化</strong>。每课配真实源码对应、图解与设计亮点。</span>
    <span class="lang-en">A layered tour: build the <strong>big picture</strong> first, lay the <strong>foundations</strong>,
    then dive into Letta's soul - the <strong>three-tier memory system</strong> and the <strong>agent loop</strong> - on to <strong>tools, LLM providers, server &amp; persistence</strong>. Every lesson maps to real source, with diagrams and design insights.</span></p>
```
并把紧随其后的底部说明
```python
    <p style="margin:.8rem 0 0;color:var(--faint);font-size:.8rem">{bi("📌 对照 llama.cpp 仓库真实源码核实 · 源码引用以“文件 + 符号名”为主（行号随上游更新而变）", "📌 Verified against the real llama.cpp source; references cite file + symbol (line numbers drift upstream)")}</p>
```
改成
```python
    <p style="margin:.8rem 0 0;color:var(--faint);font-size:.8rem">{bi("📌 对照 Letta 仓库真实源码核实（锚定 v0.16.8）· 源码引用以“文件 + 符号名”为主（行号随上游更新而变）", "📌 Verified against the real Letta source (anchored at v0.16.8); references cite file + symbol (line numbers drift upstream)")}</p>
```

- [ ] **Step 7: 改写 page() 的 desc（lesson 级 meta 描述里的 llama 专属串）**

`page()` 中的 `title_tag` 经 sed 已正确（结尾变成 `- Letta 图解教程`）。把 `desc` 一行
```python
    desc = f"{part_zh}｜{title_zh} - llama.cpp 图解教程（中英双语，配真实源码对应、折叠深挖与设计亮点）"
```
（sed 后此处的 `llama.cpp 图解教程` 已变为 `Letta 图解教程`，无需再改；仅确认即可。）

- [ ] **Step 8: 验证 shell.py 可导入且 PAGES 正确**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python -c "import shell; print(len(shell.PAGES), shell.PAGES[0][0]); shell.index_page()[:1]"
```
Expected: 打印 `1 01-what-is-letta.html`，无异常（说明 CSS f-string、PAGES、index_page 均正常）。

- [ ] **Step 9: 提交**

```bash
cd /home/verden/course/letta-visual-guide
git add src/shell.py
git commit -m "feat(m0): port and re-skin shell.py for Letta theme"
```

---

## Task 3: 新写 src/part1.py（LESSON_01 基线课）

**Files:**
- Create: `src/part1.py`

> 这是一课**基线**（够真、能过结构校验、展示设计系统），M1 会把它扩写到 ~4000 CJK 与 3-5 图。正文不要再出现 `<h1>`（外壳已给），用 `<h2>/<h3>`。

- [ ] **Step 1: 写 part1.py**

```python
"""Content for Part 1 (macro overview). M0 ships lesson 01 as the baseline."""

LESSON_01 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Letta（原 <span class="inline">MemGPT</span>）是一个<strong>有状态 agent 框架</strong>：它给"健忘"的大语言模型配上一套<strong>会自我管理的记忆系统</strong>，
让 agent 能跨对话<strong>记住你、积累知识、随时间自我改进</strong>。一句话——把 LLM 从"无状态的一次性问答"变成"<strong>有记忆、能成长的助手</strong>"。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把 LLM 想成一个<strong>聪明但严重健忘</strong>的天才：每次"醒来"只记得眼前这一小段对话（上下文窗口），说完就忘。Letta 给他配了一个<strong>随身笔记本</strong>（核心记忆，时刻在眼前）
  和一个<strong>资料档案室</strong>（归档记忆，需要时去检索），还教会他<strong>自己整理笔记</strong>——这正是 Letta 的灵魂。
</div>

<h2>它到底解决什么问题</h2>
<p>大语言模型本身是<strong>无状态</strong>的：每次调用，它只看到这一次传进去的文字；上下文窗口（几千到几十万 token）一满，更早的内容就被挤掉、"忘"得一干二净。
要做一个能长期陪伴、不断学习的 agent，就必须在模型之外补上"<strong>记忆</strong>"这一环。Letta（脱胎自 <span class="inline">MemGPT</span> 论文）正是为此而生。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  Letta 把 agent 做成<strong>有状态</strong>的：每个 agent 的记忆块、消息历史、工具、模型配置都以一条 <span class="mono">AgentState</span> 存进数据库。
  运行时把它<strong>取出来跑一步、再存回去</strong>，于是 agent"关机重启"也不丢记忆——这也让服务端可以水平扩展。
</div>

<div class="cols">
  <div class="col"><h4>普通 LLM 调用</h4><p>无状态 · 只看本次输入 · 上下文一满就忘 · 关掉即清零</p></div>
  <div class="col"><h4>Letta 有状态 agent</h4><p>状态存库（AgentState）· 自我编辑记忆 · 上下文满了自我压缩 · 跨会话长期记住</p></div>
</div>

<h2>三层记忆，一眼看全</h2>
<p>Letta 借鉴 <span class="inline">MemGPT</span> 的核心思想，把记忆分成三层（后面第三部分会逐层深挖）：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>核心记忆 core memory</h4><p>始终在上下文里的"便利贴"（如 <span class="mono">persona</span> / <span class="mono">human</span> 块），agent 能<strong>自己改写</strong>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>回忆记忆 recall memory</h4><p>完整对话历史存在库里，只有最近的留在窗口内，其余可<strong>检索召回</strong>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>归档记忆 archival memory</h4><p>长期知识库，按<strong>向量相似度</strong>检索，容量近乎无限。</p></div></div>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>LLM <strong>无状态</strong> + 上下文<strong>有限</strong>，是 Letta 存在的根本理由。</li>
    <li>Letta（原 MemGPT）把 agent 做成<strong>有状态</strong>，状态即数据库里的 <span class="mono">AgentState</span>。</li>
    <li>记忆分<strong>三层</strong>：core（眼前）/ recall（历史）/ archival（档案）。</li>
    <li>灵魂特性：agent 能<strong>自我编辑记忆</strong>、上下文满了能<strong>自我压缩</strong>。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Letta (formerly <span class="inline">MemGPT</span>) is a <strong>stateful agent framework</strong>: it gives the "forgetful" LLM a <strong>self-managing memory system</strong>,
so an agent can <strong>remember you, accumulate knowledge, and self-improve over time</strong> across conversations. In one line: it turns an LLM from a <strong>stateless one-off Q&amp;A</strong> into a <strong>remembering, growing assistant</strong>.
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Think of an LLM as a <strong>brilliant but deeply amnesiac</strong> genius: each time it "wakes" it only recalls the little stretch of conversation in front of it (the context window), then forgets. Letta hands it a <strong>pocket notebook</strong>
  (core memory, always in view) and a <strong>filing room</strong> (archival memory, fetched on demand), and teaches it to <strong>tidy its own notes</strong> - which is Letta's soul.
</div>

<h2>What problem it actually solves</h2>
<p>An LLM is itself <strong>stateless</strong>: each call sees only the text you pass in this time, and once the context window (a few thousand to a few hundred thousand tokens) fills up, older content is pushed out and "forgotten". To build an agent that companions you long-term and keeps learning, you must add the missing <strong>memory</strong> layer around the model. Letta (born from the <span class="inline">MemGPT</span> paper) exists for exactly this.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  Letta makes agents <strong>stateful</strong>: each agent's memory blocks, message history, tools and model config are persisted as one <span class="mono">AgentState</span> row. The runtime <strong>loads it, runs a step, saves it back</strong>, so an agent survives "power-cycling" without losing memory - and the server can scale horizontally.
</div>

<div class="cols">
  <div class="col"><h4>Plain LLM call</h4><p>Stateless · sees only this input · forgets when context fills · gone when closed</p></div>
  <div class="col"><h4>Letta stateful agent</h4><p>State in DB (AgentState) · self-edits memory · self-compacts when full · remembers across sessions</p></div>
</div>

<h2>The three memory tiers at a glance</h2>
<p>Letta borrows <span class="inline">MemGPT</span>'s core idea and splits memory into three tiers (Part 3 drills into each):</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>core memory</h4><p>The "sticky notes" always in context (e.g. <span class="mono">persona</span> / <span class="mono">human</span> blocks); the agent can <strong>rewrite them itself</strong>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>recall memory</h4><p>The full conversation history lives in the DB; only the recent part stays in-window, the rest is <strong>searchable</strong>.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>archival memory</h4><p>A long-term knowledge store, retrieved by <strong>vector similarity</strong>, near-unlimited in size.</p></div></div>
</div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>A <strong>stateless</strong> LLM + <strong>finite</strong> context is the whole reason Letta exists.</li>
    <li>Letta (formerly MemGPT) makes agents <strong>stateful</strong>; the state is an <span class="mono">AgentState</span> row in the DB.</li>
    <li>Memory has <strong>three tiers</strong>: core (in view) / recall (history) / archival (filing room).</li>
    <li>Soul features: the agent <strong>self-edits memory</strong> and <strong>self-compacts</strong> when context fills.</li>
  </ul>
</div>
""",
}
```

- [ ] **Step 2: 验证可导入且双语非空**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python -c "import part1; print(len(part1.LESSON_01['zh']), len(part1.LESSON_01['en']))"
```
Expected: 打印两个较大的数（均 > 80），无异常。

---

## Task 4: 新写 src/registry.py

**Files:**
- Create: `src/registry.py`

- [ ] **Step 1: 写 registry.py**

```python
"""Single source of truth: ordered map of output filename -> bilingual content.

Each value is a dict ``{"zh": html, "en": html}``. build.py / check_html.py import
this so the lesson set stays in sync with shell.PAGES.
"""
import part1

# Filename -> {"zh": ..., "en": ...}. Keep keys in sync with shell.PAGES.
CONTENT = {
    "01-what-is-letta.html": part1.LESSON_01,
}
```

- [ ] **Step 2: 验证与 PAGES 对齐**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python -c "import shell, registry; ps={p[0] for p in shell.PAGES}; cs=set(registry.CONTENT); print('ok' if ps==cs else ('MISMATCH', ps^cs))"
```
Expected: 打印 `ok`。

---

## Task 5: 新写 src/quizzes.py（机制 + 空题库）

**Files:**
- Create: `src/quizzes.py`

> M0 不出题，仅提供 `render()` 机制；`render` 在某课无题时返回空串，构建照常。M9 再补全题库。

- [ ] **Step 1: 写 quizzes.py**

```python
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
QUIZZES = {}


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
```

- [ ] **Step 2: 验证可导入且空题课返回空串**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python -c "import quizzes; print(repr(quizzes.render('01-what-is-letta.html','zh')))"
```
Expected: 打印 `''`（空串）。

---

## Task 6: 移植 src/build.py 并首次构建

**Files:**
- Create: `src/build.py`（从参考复制，无需改动）

- [ ] **Step 1: 复制 build.py（并修正遗留品牌名 docstring）**

```bash
cd /home/verden/course/letta-visual-guide
cp ../llama-cpp-visual-guide/src/build.py src/build.py
sed -i 's/Build the llama\.cpp visual guide/Build the Letta visual guide/' src/build.py
```

- [ ] **Step 2: 构建站点**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python build.py
```
Expected: 打印 `Wrote 2 files under ...`，列出 `lessons/01-what-is-letta.html` 与 `index.html`。

- [ ] **Step 3: 验证产物存在且含双语 + 主题色**

Run:
```bash
cd /home/verden/course/letta-visual-guide
ls lessons/01-what-is-letta.html index.html
grep -c 'class="lang-zh"' lessons/01-what-is-letta.html
grep -c '#6d5efc' index.html
grep -c 'Letta 图解教程' index.html
```
Expected: 两文件存在；三个 `grep -c` 均 > 0（双语块在、Letta 靛蓝主题色在、品牌名已换）。

- [ ] **Step 4: 提交生成器与产物**

```bash
cd /home/verden/course/letta-visual-guide
git add src/build.py src/part1.py src/registry.py src/quizzes.py index.html lessons/
git commit -m "feat(m0): add build pipeline + baseline lesson 01 + index"
```

---

## Task 7: 移植 src/check_links.py（死链校验）

**Files:**
- Create: `src/check_links.py`（复制 + 改 PDF 文件名）

- [ ] **Step 1: 复制并改 PDF 名**

```bash
cd /home/verden/course/letta-visual-guide
cp ../llama-cpp-visual-guide/src/check_links.py src/check_links.py
sed -i 's/llama-cpp-visual-guide/letta-visual-guide/g' src/check_links.py
```

- [ ] **Step 2: 运行死链校验**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python check_links.py
```
Expected: 打印 `all N internal links resolve`，退出码 0。

- [ ] **Step 3: 提交**

```bash
cd /home/verden/course/letta-visual-guide
git add src/check_links.py
git commit -m "feat(m0): add internal-link checker"
```

---

## Task 8: 移植 src/check_html.py（结构 / 漂移校验）

**Files:**
- Create: `src/check_html.py`（复制 + 改 `MAX_LESSON` / `SOFT_EXEMPT`）

- [ ] **Step 1: 复制并改课程总数与豁免名**

```bash
cd /home/verden/course/letta-visual-guide
cp ../llama-cpp-visual-guide/src/check_html.py src/check_html.py
sed -i 's/^MAX_LESSON = 40.*/MAX_LESSON = 31  # planned final lesson count; cross-refs may point forward/' src/check_html.py
sed -i 's/SOFT_EXEMPT = {"40-glossary.html"}/SOFT_EXEMPT = {"31-glossary.html"}/' src/check_html.py
```

- [ ] **Step 2: 验证改动生效**

Run:
```bash
cd /home/verden/course/letta-visual-guide
grep -n 'MAX_LESSON = 31' src/check_html.py; grep -n '31-glossary.html' src/check_html.py
```
Expected: 两条都各有一行输出。

- [ ] **Step 3: 运行结构校验**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python check_html.py
```
Expected: 末行 `structural check passed`，`0 error(s)`。可能出现若干 `[WARN]`（如 CJK/图数量不足、无 analogy/key —— 基线课允许，M1 会补足），WARN 不致失败。

- [ ] **Step 4: 提交**

```bash
cd /home/verden/course/letta-visual-guide
git add src/check_html.py
git commit -m "feat(m0): add structural/anti-drift checker (31 lessons)"
```

---

## Task 9: README + 全流程冒烟 + 浏览器自检

**Files:**
- Create: `README.md`

- [ ] **Step 1: 写极简 README（M9 再扩写）**

```markdown
# Letta 图解教程（Letta Visual Guide）

从零理解 [Letta](https://github.com/letta-ai/letta)（原 MemGPT）的中英双语图解教程。
纯 Python 零依赖生成器，产出自包含静态站点，可 `file://` 直接打开。

## 如何重新生成

```bash
cd src
python build.py          # 生成 index.html + lessons/*.html
python check_links.py    # 校验内部链接无死链
python check_html.py     # 校验结构 / 与 src 无漂移
```

## 目录

- `src/shell.py` — 设计系统（CSS）+ 导航 + 双语切换 + `PAGES`
- `src/registry.py` — 文件名 → 双语内容（单一事实源）
- `src/part1.py …` — 各部分课程内容
- `src/quizzes.py` — 每课自测
- `src/build.py` / `check_links.py` / `check_html.py` — 构建与校验

> 独立第三方学习材料，与 Letta 官方无隶属关系；源码引用锚定 letta `v0.16.8`。
```

- [ ] **Step 2: 全流程冒烟（三件套连跑）**

Run:
```bash
cd /home/verden/course/letta-visual-guide/src
python build.py && python check_links.py && python check_html.py && echo ALL_OK
```
Expected: 末尾打印 `ALL_OK`（三步均成功）。

- [ ] **Step 3: 浏览器人工自检（手动）**

打开 `index.html`（`file://`），确认：
- 目录页显示"用图解理解整个 Letta 项目"，主题为靛蓝紫、品牌为"Letta 图解教程"。
- 点右上角 `EN` 能切到英文；刷新/进入课程后语言保持（localStorage `lvg-lang`）。
- 顶部搜索框能按关键词过滤课程。
- 点开第 1 课，卡片（类比/宏观/要点）、对比两栏、三层记忆 vflow 正常显示；上/下导航可用。

- [ ] **Step 4: 提交 README**

```bash
cd /home/verden/course/letta-visual-guide
git add README.md
git commit -m "docs(m0): add minimal README with build instructions"
```

---

## Self-Review（对照 spec 第 3/8 节）

- **3.1 仓库结构**：M0 产出 `src/{shell,registry,part1,quizzes,build,check_links,check_html}.py` + `index.html` + `lessons/01` + `README` + `.gitignore` ✔（`build_print.py`、`.github/workflows/*` 属 M9）。
- **3.2 双语机制**：`lvg-lang` localStorage + `lvgToggleLang()` 切换 ✔（Task 2 sed 由 `lcvg`→`lvg` 整体替换）。
- **3.3 换皮**：主题色靛蓝紫、favicon `L`/🧠、品牌名、hero 文案 ✔（Task 2）。
- **第 8 节 M0 验收**：脚手架 + 1-2 课样板 + index 跑通、确定主题与双语交互 ✔（Task 6/9）。
- **不变量**：`build + check_links + check_html` 三件套全过（Task 9 Step 2）；`PAGES`↔`CONTENT` 对齐（Task 4 Step 2）。

**占位符扫描**：无 TODO/TBD；每个改动都给了完整内容或精确 sed/edit。
**类型/命名一致**：`render(fname, lang)`、`CONTENT`、`PAGES`、`SUBTITLES`、`LESSON_01` 在各文件间一致。
**遗留到后续里程碑**：题库内容（M9）、`build_print.py` 与 CI（M9）、第 1 课扩写到 ~4000 CJK 与 3-5 图（M1）。
