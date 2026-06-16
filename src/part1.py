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
