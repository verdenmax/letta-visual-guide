"""Content for Part 1 (macro overview). M0 ships lesson 01 as the baseline."""

LESSON_01 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Letta（前身是 <span class="inline">MemGPT</span>）是一个<strong>有状态 agent 框架</strong>：它给"健忘"的大语言模型配上一套<strong>会自我管理的记忆系统</strong>，让 agent 能跨对话<strong>记住你、积累知识、随时间自我改进</strong>。一句话——把 LLM 从"无状态的一次性问答"升级成"<strong>有记忆、能成长的助手</strong>"。这是本教程的第一课，也是理解后面所有内容的地基。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把大语言模型想象成一位<strong>绝顶聪明却严重健忘</strong>的天才：他每次"醒来"只记得眼前这一小段对话（这就是<strong>上下文窗口</strong>），话音一落就忘得干干净净，连你刚说过的名字都留不住。Letta 做的事，就是给这位天才配三样东西：一本<strong>随身便利贴</strong>（核心记忆，永远摊在桌上看得见）、一间<strong>资料档案室</strong>（归档记忆，需要时去翻），以及——最关键的——教会他<strong>自己动手整理这些笔记</strong>。能"自己整理记忆"，正是 Letta 区别于一切普通聊天机器人的灵魂。
</div>

<h2>它到底解决什么根本问题</h2>
<p>要理解 Letta，先得认清大语言模型的两个"硬伤"。第一，模型本身是<strong>无状态</strong>的：每一次 API 调用都是一张白纸，它只看见你这一次塞进去的文字，上一次聊了什么、它根本不知道——所谓"记住对话"，其实是调用方每次把历史<strong>重新拼进输入</strong>制造出来的错觉。第二，能塞进去的文字是<strong>有限</strong>的：上下文窗口从几千到几十万 token 不等，一旦塞满，更早的内容就会被挤出去、被"遗忘"，而且越长的上下文意味着越高的费用与越慢的响应。</p>
<p>这两条叠加，结论很扎心：<strong>裸用 LLM 做不出能长期陪伴、不断学习的 agent</strong>。你今天告诉它的偏好，明天、甚至几轮对话之后就丢了。Letta（脱胎自 2023 年的 <span class="inline">MemGPT</span> 论文）正是冲着这个根本矛盾而生：既然模型外面缺一层"记忆"，那就把这层记忆<strong>系统化地补上</strong>，并且让 agent 自己来管理它。</p>

<p>举个具体例子：你在第 1 轮告诉它"我对花生过敏"，接着聊了几十轮做菜的话题；等上下文被新内容塞满，最早那句"过敏"早被挤了出去。这时你再问"帮我推荐一道菜"，裸 LLM 完全可能端上一盘花生口味的菜——它不是突然变笨，而是那条关键信息<strong>已经不在它眼前</strong>了。Letta 的解法是：当它判断"过敏"这件事值得记住时，就把它写进核心记忆块，于是不管之后聊多久，这条事实都<strong>常驻在上下文里</strong>、不会被冲掉。这就是"真有记忆"和"假装有记忆"的分水岭。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  Letta 的核心动作，是把 agent 做成<strong>有状态</strong>的：每个 agent 的记忆块、消息历史、可用工具、模型配置，统统打包成数据库里的<strong>一条记录</strong>——它的名字叫 <span class="mono">AgentState</span>。运行时的套路永远是三步：<strong>从库里取出</strong>这条状态 → <strong>跑一步</strong>（读消息、思考、可能调工具、回话）→ <strong>把更新写回</strong>库里。于是 agent"关机重启"也不丢记忆，而且因为状态不黏在某个进程上，服务端可以<strong>水平扩展</strong>。
</div>

<h2>Letta 站在生态的哪个位置</h2>
<p>AI 工具链里名词很多，新手容易混淆。一张表把 Letta 的站位说清楚：训练框架负责"造模型"，推理 API 负责"跑模型"，编排库负责"把多步拼起来"，而 Letta 负责的是<strong>给 agent 一个会自我管理的、持久的记忆与身份</strong>——这是别人都没替你做完的那一环。</p>

<table class="t">
  <tr><th>工具</th><th>定位</th><th>状态</th><th>记忆</th></tr>
  <tr><td class="mono">PyTorch</td><td>训练 + 推理框架</td><td>—</td><td>—</td></tr>
  <tr><td class="mono">OpenAI API</td><td>托管推理（跑模型）</td><td>无状态（每次调用独立）</td><td>无：要你自己把历史拼进 prompt</td></tr>
  <tr><td class="mono">LangChain</td><td>编排 / 胶水</td><td>多为无状态</td><td>可加，但要你自己管</td></tr>
  <tr><td><strong>Letta</strong></td><td><strong>有状态 agent 框架</strong></td><td><strong>有状态：AgentState 存库</strong></td><td><strong>内建三层 + agent 自己编辑</strong></td></tr>
</table>

<p>注意最后一行的两个"<strong>自己</strong>"：状态<strong>自己</strong>存在库里、记忆由 agent <strong>自己</strong>编辑。这正是它和"给 LLM 套个壳、再手动塞历史"做法的本质差别。很多库也号称"支持记忆"，但那通常是你在外面手动维护一段历史、再塞回 prompt，模型和记忆始终是两张皮；Letta 则把"管理记忆"这件事<strong>内化</strong>成 agent 自身的一项能力——它能自己决定该记什么、该忘什么、该去哪儿翻。这是从量变到质变的关键一步。</p>

<h3>无状态 vs 有状态：把时间线摊开看</h3>
<p>用一条时间线对比"裸 LLM"和"Letta agent"在多轮对话里的差别。裸 LLM 这一行，越往后上下文越满，满了就把最早的对话挤掉、彻底遗忘；Letta 这一行，旧消息被收进库里、关键事实被写进核心记忆，所以"现在"这一刻它依然记得开头说过的事。</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">裸 LLM</span><span class="tslot">第 1 轮</span><span class="tslot">第 2 轮</span><span class="tslot span">上下文被塞满…</span><span class="tslot now">第 N 轮：最早的全忘了</span></div>
  <div class="lane"><span class="lane-label">Letta</span><span class="tslot">第 1 轮·写入记忆</span><span class="tslot">第 2 轮·读记忆</span><span class="tslot span">旧消息进库 / 自我压缩</span><span class="tslot now">第 N 轮：仍记得你是谁</span></div>
</div>

<div class="cols">
  <div class="col"><h4>普通 LLM 调用</h4><p>无状态 · 只看本次输入 · 上下文一满就遗忘 · 进程关掉即清零 · "记忆"全靠调用方手动拼历史。</p></div>
  <div class="col"><h4>Letta 有状态 agent</h4><p>状态存库（AgentState）· agent 自我编辑记忆 · 上下文满了自我压缩 · 跨会话长期记住 · 换个进程或机器也能接着跑。</p></div>
</div>

<h2>三层记忆，一眼看全</h2>
<p>Letta 把 <span class="inline">MemGPT</span> 的核心思想落成<strong>三层记忆</strong>。它们的区别只有两个维度：<strong>在不在上下文窗口里</strong>、<strong>怎么被取回来</strong>。这里先建立总览，<strong>第三部分（记忆系统）</strong>会逐层拆开讲实现。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>核心记忆 core memory</h4><p><strong>始终</strong>在上下文里的"便利贴"，典型是 <span class="mono">persona</span>（agent 的人设）和 <span class="mono">human</span>（关于你的事实）两个块；最特别的是 agent 能<strong>自己改写</strong>它们。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>回忆记忆 recall memory</h4><p>完整对话历史<strong>全量</strong>存在数据库里，只有最近的一段留在窗口内，其余可按需<strong>检索召回</strong>——相当于"翻聊天记录"。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>归档记忆 archival memory</h4><p>长期知识库，按<strong>向量相似度</strong>语义检索，容量近乎无限，用来存"读过的资料、沉淀的结论"。</p></div></div>
</div>

<p>为什么非要分三层、而不是一整块大记忆？因为这三层在"<strong>取用速度</strong>"和"<strong>容量</strong>"上正好反着来：核心记忆最快（永远在眼前）但最小，归档记忆最大却要检索才拿得到，回忆记忆居中。把最该随时可见的少量事实放进核心记忆，把海量却不常用的知识丢进归档——这就是一份精打细算的"上下文预算"，好钢用在刀刃上。</p>

<h2>一个 agent 就是一条 AgentState</h2>
<p>新手最常见的误解是"agent 是一个一直在内存里活着的进程"。在 Letta 里不是——<strong>agent 就是数据库里的一条存档</strong>。先从用户视角看：创建一个 agent，本质就是写下它的初始记忆块和能力。下面是来自官方 README 的最小示例（Python SDK）：</p>

<pre class="code"><span class="cm"># 创建一个自带记忆的 agent（Python SDK，源自 letta README）</span>
<span class="kw">from</span> letta_client <span class="kw">import</span> Letta
client = Letta(api_key=os.getenv(<span class="st">"LETTA_API_KEY"</span>))

agent_state = client.agents.<span class="fn">create</span>(
    model=<span class="st">"openai/gpt-5.2"</span>,
    memory_blocks=[
        {<span class="st">"label"</span>: <span class="st">"human"</span>,   <span class="st">"value"</span>: <span class="st">"Name: Timber..."</span>},
        {<span class="st">"label"</span>: <span class="st">"persona"</span>, <span class="st">"value"</span>: <span class="st">"I am a self-improving assistant..."</span>},
    ],
    tools=[<span class="st">"web_search"</span>, <span class="st">"fetch_webpage"</span>],
)
<span class="cm"># 发消息；agent 带着记忆回应</span>
resp = client.agents.messages.<span class="fn">create</span>(
    agent_id=agent_state.id, input=<span class="st">"What do you know about me?"</span>)
</pre>

<p>这两个记忆块各有分工：<span class="mono">persona</span> 描述"agent 自己是谁、该用什么口吻说话"，<span class="mono">human</span> 描述"它正在服务的人是谁"。而当你调用 <span class="mono">messages.create</span> 发一条消息时，服务端会照着这条 <span class="mono">AgentState</span>，把系统提示、核心记忆、最近若干条消息<strong>重新组装成一次模型输入</strong>；模型跑完，再把新产生的消息和记忆改动<strong>写回数据库</strong>——这正是前面那句"取出 → 跑一步 → 写回"落到实处的样子。</p>

<p>关键点：<strong>创建那一刻</strong>，你就把 <span class="mono">persona</span> / <span class="mono">human</span> 两个记忆块交给了 agent；它们会被一直放在上下文里。那么这一条 agent 的"全部存档"长什么样？把 <span class="mono">AgentState</span> 的关键字段画成一张"存档卡"——这就是本课的整体结构图：</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">核心记忆</span><span class="name">memory / blocks</span></div>
    <div class="ld">persona / human 等记忆块，始终在上下文里，agent 可自改。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">在窗消息</span><span class="name">message_ids: list[str]</span></div>
    <div class="ld">当前留在上下文窗口里的消息 id（第 0 条永远是 system 消息）。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">能力</span><span class="name">tools · tool_rules</span></div>
    <div class="ld">这个 agent 能调用哪些工具、以及调用顺序的约束。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">模型</span><span class="name">llm_config · embedding_config</span></div>
    <div class="ld">用哪个模型、上下文多大、用什么嵌入模型做向量检索。</div></div>
</div>

<p>把它对照真实源码（<span class="mono">letta/schemas/agent.py</span> 里的 <span class="mono">AgentState</span>），简化后大致是这样：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/agent.py</span><span class="ln">class AgentState（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentState</span>:
    id: str                  <span class="cm"># "agent-..." 前缀的主键 id</span>
    name: str                <span class="cm"># 人类可读的名字</span>
    system: str              <span class="cm"># 系统提示（核心记忆会被编译进来）</span>
    message_ids: list        <span class="cm"># 当前在上下文窗口里的消息 id</span>
    blocks: list             <span class="cm"># 核心记忆块：persona / human ...</span>
    tools: list              <span class="cm"># 这个 agent 能用的工具</span>
    tool_rules: list         <span class="cm"># 工具调用顺序 / 约束</span>
    llm_config: LLMConfig    <span class="cm"># 模型 / 上下文窗口大小</span>
    embedding_config: ...    <span class="cm"># 归档检索用的嵌入模型</span>
</pre></div>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  这张"存档卡"不是比喻，它就是真实的类：<span class="mono">letta/schemas/agent.py</span> 的 <span class="mono">AgentState</span>。核心记忆由 <span class="mono">letta/schemas/memory.py</span> 的 <span class="mono">Memory</span> 表示，其 <span class="mono">compile()</span> 方法负责把各个记忆块拼成一段文本；而 agent 自己改记忆，靠的是 <span class="mono">core_memory_append</span> / <span class="mono">core_memory_replace</span> 这两个工具（见 <span class="mono">letta/services/tool_executor/core_tool_executor.py</span>）。
</div>

<p>顺带说一个常被忽略的好处：因为整条状态都在数据库里，同一个 Letta 服务可以<strong>同时托管成千上万个 agent</strong>，每个 agent 都是独立的一行存档、互不干扰；要"唤醒"某个 agent，只需按它的 id 把那一行取出来。这让 Letta 能做成一个真正的<strong>多租户服务端</strong>，而不只是跑在你本机内存里的一段脚本。</p>

<h2>灵魂：自我编辑记忆 = 改写自己的系统提示</h2>
<p>到这里可以揭晓本课最精妙、也最反直觉的一点了。你可能以为 agent"记住一件事"是把它写进某个普通数据库字段。但在 Letta 里，<strong>核心记忆是被编译进系统提示（system prompt）的</strong>——也就是说，当 agent 调用 <span class="mono">core_memory_replace</span> 改掉一个记忆块时，它<strong>实质上是在改写自己的第 0 条消息、改写自己的"出厂设定"</strong>。下一轮对话，新的系统提示一上来就生效。</p>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>MemGPT 的"操作系统"类比</strong>，是理解整个 Letta 的钥匙：把 LLM 当作 <strong>CPU</strong>，把上下文窗口当作容量有限的 <strong>内存（RAM）</strong>，把外部记忆当作近乎无限的 <strong>磁盘</strong>。当"内存"放不下时，agent 就像操作系统遇到缺页那样主动<strong>换页</strong>——调用记忆工具，把内容在 RAM 与磁盘之间搬运。<br><br>
  而真正的"啊哈"在于：<strong>自我编辑记忆，本质上是 agent 在改写自己的系统提示</strong>。<span class="mono">Memory.compile()</span> 的产物会被拼进那条<strong>持久化的 system 消息</strong>；一旦记忆块发生变化，<span class="mono">agent_manager.rebuild_system_prompt_async</span> 就会<strong>重写第 0 条消息</strong>。换句话说，agent 不只是"往笔记本上记"，它是在<strong>持续重写定义自己是谁的那段提示词</strong>——这才是"会自我改进的 agent"在机制上的真正含义。
</div>

<p>把这个闭环用伪代码串一遍（思路源自 <span class="mono">core_tool_executor.py</span> 与 <span class="mono">agent_manager.rebuild_system_prompt_async</span>）：</p>

<pre class="code"><span class="cm"># agent 自我编辑记忆的闭环（伪代码）</span>
<span class="kw">def</span> <span class="fn">core_memory_replace</span>(label, old, new):
    block = memory.get_block(label)       <span class="cm"># 找到 persona/human 块</span>
    block.value = block.value.replace(old, new)
    persist(block)                         <span class="cm"># 写回数据库</span>
    <span class="cm"># 关键：记忆变了 -&gt; 重新编译系统提示</span>
    new_system = memory.<span class="fn">compile</span>()      <span class="cm"># 把所有块拼成新 system 文本</span>
    rebuild_system_prompt(agent)           <span class="cm"># 重写第 0 条 system 消息</span>
</pre>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>用户说了一件该记住的事</h4><p>例如"以后叫我 Timber"。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>agent 调用 <span class="mono">core_memory_replace</span></h4><p>把 human 块里的旧值换成新值。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>记忆块写回数据库</h4><p>变化被持久化，不会随对话结束而丢失。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>系统提示<strong>重新编译</strong></h4><p><span class="mono">Memory.compile()</span> 产出新文本，重写第 0 条消息。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>下一轮立即生效</h4><p>新设定从下一次回应起就"长在"agent 身上。</p></div></div>
</div>

<div class="card warn">
  <div class="tag">⚠️ 容易误解</div>
  "有状态"不等于"模型本身有记忆了"。底层 LLM 每一次调用<strong>依然是无状态</strong>的；记忆是 Letta 这个<strong>框架在模型之外</strong>补出来的：它把状态存进库、每步重新组织好上下文再喂给模型。所以严格说，是<strong>框架有记忆</strong>，模型只是被"喂"得更聪明而已。
</div>

<p>那"会成长、能自我改进"具体长什么样？它<strong>不是</strong>去重新训练模型，而是三件每天都在发生的小事：把关于你的新事实写进核心记忆、把读到的资料沉淀进归档、在上下文快满时自动压缩旧消息。日积月累，<strong>同一个模型</strong>因为"带着越来越贴合你的记忆"，用起来就越来越像专属助手——成长发生在<strong>记忆层</strong>，而不在模型权重里。记住这一点，就不会再把 Letta 误当成"又一个套壳聊天机器人"。</p>

<h2>再挖深一点</h2>

<details class="accordion"><summary>为什么不干脆把所有历史都塞进上下文？</summary><div class="acc-body">
<p><strong>示例：</strong>有人会想，既然现在有几十万 token 的长上下文，为什么不把全部聊天记录一股脑塞进去？</p>
<p><strong>为什么这样设计：</strong>因为上下文不是免费的。token 越多，<strong>每次调用越贵、延迟越高</strong>；而且把无关内容堆在一起还会<strong>稀释注意力</strong>，让模型抓不住重点。更现实的是：上下文总有上限，对话只要够长，<strong>迟早会溢出</strong>。所以正确做法是只在窗口里放"该放的"，其余进库、要用再取。</p>
<p><strong>源码在哪：</strong>窗口与上下文大小由 <span class="mono">AgentState.llm_config</span> 决定；把记忆拼进上下文由 <span class="mono">letta/schemas/memory.py::Memory.compile</span> 和 <span class="mono">letta/prompts/prompt_generator.py::PromptGenerator</span> 负责。</p>
<p><strong>还有什么替代：</strong>纯长上下文（贵且有上限）、纯向量 RAG（无分层、agent 不能自管）——Letta 选了"分层 + agent 自管"，这块到<strong>第 3 课 一条消息的生命周期</strong>和第三部分会展开。</p>
</div></details>

<details class="accordion"><summary>Letta 和 OpenAI Assistants / LangChain memory 有什么不同？</summary><div class="acc-body">
<p><strong>示例：</strong>它们听起来都"给 LLM 加了记忆"，到底差在哪？</p>
<p><strong>为什么这样设计：</strong>差别有三点。其一，Letta 让 <strong>agent 自己编辑</strong>分层记忆（core/recall/archival），而不是只在外面被动检索；其二，<strong>状态完全在数据库里</strong>，一条 <span class="mono">AgentState</span> 就能完整重建一个 agent；其三，<strong>模型无关</strong>——换底层模型不影响记忆机制。</p>
<p><strong>源码在哪：</strong>状态的定义在 <span class="mono">schemas/agent.py::AgentState</span>，自管记忆的工具在 <span class="mono">core_tool_executor.py</span>，整体编排在 <span class="mono">letta/server/server.py::SyncServer</span> 与 <span class="mono">agent_manager.py</span>。</p>
<p><strong>还有什么替代：</strong>OpenAI Assistants 把状态托管在它自己服务里、记忆策略不透明；LangChain 提供 memory 组件但要你自己拼装与持久化。Letta 的取舍是"开箱即用的有状态 + 全透明、可自托管"。</p>
</div></details>

<details class="accordion"><summary>用一句话说清 MemGPT 的核心思想</summary><div class="acc-body">
<p><strong>示例：</strong>如果只能记住一句话，记这句：<strong>LLM ≈ CPU，上下文 ≈ RAM，外部存储 ≈ 磁盘，记忆工具 ≈ 系统调用 / 换页。</strong></p>
<p><strong>为什么这样设计：</strong>操作系统几十年前就解决过"内存装不下"的问题——用分层存储 + 换页。MemGPT 把同一套思路搬到 agent 上：让 agent 像 OS 调度内存一样，自己决定什么留在上下文、什么换到外部。</p>
<p><strong>源码在哪：</strong>"换页"对应的就是 <span class="mono">core_tool_executor.py</span> 里那组记忆工具，以及检索召回相关的 <span class="mono">block_manager.py</span> / <span class="mono">passage_manager.py</span>。</p>
<p><strong>还有什么替代：</strong>不分层、把所有东西塞进一个超长 prompt——能跑，但贵、慢、且终会溢出。OS 类比的价值，就是告诉你"分层 + 自主调度"才是可持续的解法。</p>
</div></details>

<h2>这一课在整张大图的哪里</h2>
<p>你现在站在全书的<strong>起点</strong>：已经知道 Letta 为何存在（LLM 无状态 + 上下文有限）、它的核心抽象是什么（一条可自我编辑的 <span class="mono">AgentState</span>）、以及它最精妙的设计（自编辑记忆 = 改写系统提示）。接下来这一部分（宏观全景）还有两课：<strong>下一课（第 2 课）项目全景地图</strong>会带你看 <span class="mono">letta/</span> 的目录结构与"REST 路由 → services → ORM/数据库"三层架构；<strong>第 3 课 一条消息的生命周期</strong>会跟着一条用户消息走完从进入到回复的全过程。再往后的<strong>第三部分（记忆系统）</strong>，会把今天一笔带过的三层记忆逐层拆开。带着"agent 就是一条 AgentState"这把钥匙，后面的内容都会顺很多。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>LLM <strong>无状态</strong> + 上下文<strong>有限</strong>，是 Letta 存在的根本理由。</li>
    <li>Letta（前身 MemGPT）把 agent 做成<strong>有状态</strong>，状态就是数据库里的一条 <span class="mono">AgentState</span>。</li>
    <li>记忆分<strong>三层</strong>：core（眼前便利贴）/ recall（历史可检索）/ archival（向量档案）。</li>
    <li>灵魂特性：agent 能<strong>自我编辑记忆</strong>，而自编辑记忆在机制上 = <strong>改写自己的系统提示</strong>（<span class="mono">Memory.compile</span> 的产物被重新拼进第 0 条 system 消息）。</li>
    <li>OS 类比：LLM≈CPU、上下文≈RAM、外部记忆≈磁盘、记忆工具≈换页。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Letta (formerly <span class="inline">MemGPT</span>) is a <strong>stateful agent framework</strong>: it gives the "forgetful" LLM a <strong>self-managing memory system</strong>, so an agent can <strong>remember you, accumulate knowledge, and self-improve over time</strong> across conversations. In one line: it upgrades an LLM from a <strong>stateless one-off Q&amp;A</strong> into a <strong>remembering, growing assistant</strong>. This is lesson one — the bedrock for everything that follows.
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture an LLM as a <strong>brilliant but deeply amnesiac</strong> genius: each time it "wakes" it only recalls the little stretch of conversation in front of it (the <strong>context window</strong>), then forgets everything — even the name you just told it. Letta hands this genius three things: a <strong>pocket sticky-note pad</strong> (core memory, always on the desk), a <strong>filing room</strong> (archival memory, fetched on demand), and — crucially — teaches it to <strong>tidy those notes itself</strong>. Being able to "curate its own memory" is exactly what sets Letta apart from any ordinary chatbot.
</div>

<h2>What fundamental problem it solves</h2>
<p>To understand Letta, first face two "hard limits" of LLMs. First, the model itself is <strong>stateless</strong>: every API call is a blank slate that sees only the text you pass this time; it has no idea what was said last time — "remembering a conversation" is really an illusion the caller creates by <strong>re-stuffing the history</strong> into the input each turn. Second, how much text fits is <strong>finite</strong>: context windows range from a few thousand to a few hundred thousand tokens, and once full, older content is pushed out and "forgotten" — and longer context means higher cost and slower responses.</p>
<p>Stack those two and the conclusion stings: <strong>you cannot build a long-term, continually-learning agent on a raw LLM</strong>. The preference you state today is gone a few turns later. Letta (born from the 2023 <span class="inline">MemGPT</span> paper) exists for exactly this contradiction: since a "memory" layer is missing outside the model, add it <strong>systematically</strong> — and let the agent manage it itself.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  Letta's core move is to make agents <strong>stateful</strong>: each agent's memory blocks, message history, tools and model config are packed into <strong>one database row</strong> called <span class="mono">AgentState</span>. The runtime loop is always three steps: <strong>load</strong> the state → <strong>run a step</strong> (read messages, think, maybe call tools, reply) → <strong>save</strong> it back. So the agent survives "power-cycling" without losing memory, and since state is not glued to any one process, the server can <strong>scale horizontally</strong>.
</div>

<h2>Where Letta sits in the ecosystem</h2>
<p>The AI stack is full of overlapping terms that are easy to confuse. One table pins down Letta's spot: training frameworks "make models", inference APIs "run models", orchestration libraries "wire steps together", and Letta provides <strong>a self-managing, persistent memory and identity for an agent</strong> — the part nobody else finished for you.</p>

<table class="t">
  <tr><th>Tool</th><th>Role</th><th>State</th><th>Memory</th></tr>
  <tr><td class="mono">PyTorch</td><td>Training + inference framework</td><td>—</td><td>—</td></tr>
  <tr><td class="mono">OpenAI API</td><td>Hosted inference (run a model)</td><td>Stateless (each call independent)</td><td>None: you stuff history into the prompt</td></tr>
  <tr><td class="mono">LangChain</td><td>Orchestration / glue</td><td>Mostly stateless</td><td>Addable, but you manage it</td></tr>
  <tr><td><strong>Letta</strong></td><td><strong>Stateful agent framework</strong></td><td><strong>Stateful: AgentState in DB</strong></td><td><strong>Built-in 3 tiers + agent self-edits</strong></td></tr>
</table>

<p>Note the two "selves" in the last row: state lives in the DB by <strong>itself</strong>, and memory is edited by the agent <strong>itself</strong>. That is the essential difference from "wrap an LLM and manually re-stuff history".</p>

<h3>Stateless vs stateful: unroll the timeline</h3>
<p>Compare "raw LLM" and "Letta agent" across a multi-turn chat. On the raw-LLM lane, context fills up and the earliest turns get evicted and truly forgotten; on the Letta lane, old messages are tucked into the DB and key facts are written into core memory, so "now" it still remembers what was said at the start.</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">Raw LLM</span><span class="tslot">Turn 1</span><span class="tslot">Turn 2</span><span class="tslot span">context fills up…</span><span class="tslot now">Turn N: earliest is gone</span></div>
  <div class="lane"><span class="lane-label">Letta</span><span class="tslot">Turn 1 · write memory</span><span class="tslot">Turn 2 · read memory</span><span class="tslot span">old msgs to DB / self-compact</span><span class="tslot now">Turn N: still knows you</span></div>
</div>

<div class="cols">
  <div class="col"><h4>Plain LLM call</h4><p>Stateless · sees only this input · forgets when context fills · gone when the process closes · "memory" is purely the caller re-stuffing history.</p></div>
  <div class="col"><h4>Letta stateful agent</h4><p>State in DB (AgentState) · agent self-edits memory · self-compacts when full · remembers across sessions · resumes on another process or machine.</p></div>
</div>

<h2>The three memory tiers at a glance</h2>
<p>Letta turns <span class="inline">MemGPT</span>'s core idea into <strong>three memory tiers</strong>. They differ on only two axes: <strong>whether they sit in the context window</strong>, and <strong>how they are fetched back</strong>. Here is the overview; <strong>Part 3 (the memory system)</strong> drills into each implementation.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>core memory</h4><p>The "sticky notes" <strong>always</strong> in context, typically the <span class="mono">persona</span> (the agent's character) and <span class="mono">human</span> (facts about you) blocks; what's special is the agent can <strong>rewrite them itself</strong>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>recall memory</h4><p>The <strong>full</strong> conversation history lives in the DB; only the recent slice stays in-window, the rest is <strong>searchable</strong> on demand — like scrolling back through chat logs.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>archival memory</h4><p>A long-term knowledge store searched by <strong>vector similarity</strong>, near-unlimited in size, for "documents read and conclusions distilled".</p></div></div>
</div>

<h2>An agent is just one AgentState row</h2>
<p>The most common beginner misconception is "an agent is a process living in memory forever". In Letta it is not — <strong>an agent is one saved row in the database</strong>. Start from the user's view: creating an agent is essentially writing down its initial memory blocks and abilities. Here is the minimal example from the official README (Python SDK):</p>

<pre class="code"><span class="cm"># Create an agent that ships with memory (Python SDK, from letta README)</span>
<span class="kw">from</span> letta_client <span class="kw">import</span> Letta
client = Letta(api_key=os.getenv(<span class="st">"LETTA_API_KEY"</span>))

agent_state = client.agents.<span class="fn">create</span>(
    model=<span class="st">"openai/gpt-5.2"</span>,
    memory_blocks=[
        {<span class="st">"label"</span>: <span class="st">"human"</span>,   <span class="st">"value"</span>: <span class="st">"Name: Timber..."</span>},
        {<span class="st">"label"</span>: <span class="st">"persona"</span>, <span class="st">"value"</span>: <span class="st">"I am a self-improving assistant..."</span>},
    ],
    tools=[<span class="st">"web_search"</span>, <span class="st">"fetch_webpage"</span>],
)
<span class="cm"># Send a message; the agent replies with memory in hand</span>
resp = client.agents.messages.<span class="fn">create</span>(
    agent_id=agent_state.id, input=<span class="st">"What do you know about me?"</span>)
</pre>

<p>The key point: <strong>at creation time</strong> you already hand the agent its <span class="mono">persona</span> / <span class="mono">human</span> blocks; they stay in context from then on. What does this agent's "entire save file" look like? Draw the key fields of <span class="mono">AgentState</span> as a "save card" — this is the lesson's overall structure diagram:</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">core memory</span><span class="name">memory / blocks</span></div>
    <div class="ld">persona / human and other blocks, always in context, agent-editable.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">in-window msgs</span><span class="name">message_ids: list[str]</span></div>
    <div class="ld">ids of messages currently kept in the context window (message #0 is always the system message).</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">abilities</span><span class="name">tools · tool_rules</span></div>
    <div class="ld">which tools this agent may call, and constraints on call order.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">model</span><span class="name">llm_config · embedding_config</span></div>
    <div class="ld">which model, how big the context, which embedding model for vector search.</div></div>
</div>

<p>Mapped onto the real source (<span class="mono">AgentState</span> in <span class="mono">letta/schemas/agent.py</span>), a simplified shape is:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/agent.py</span><span class="ln">class AgentState (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentState</span>:
    id: str                  <span class="cm"># primary key with an "agent-..." prefix</span>
    name: str                <span class="cm"># human-readable name</span>
    system: str              <span class="cm"># system prompt (core memory compiles into this)</span>
    message_ids: list        <span class="cm"># ids of messages in the context window</span>
    blocks: list             <span class="cm"># core memory blocks: persona / human ...</span>
    tools: list              <span class="cm"># tools this agent can use</span>
    tool_rules: list         <span class="cm"># tool call ordering / constraints</span>
    llm_config: LLMConfig    <span class="cm"># model / context window size</span>
    embedding_config: ...    <span class="cm"># embedding model for archival search</span>
</pre></div>

<div class="card detail">
  <div class="tag">🔬 Source mapping</div>
  This "save card" is not a metaphor — it is a real class: <span class="mono">AgentState</span> in <span class="mono">letta/schemas/agent.py</span>. Core memory is represented by <span class="mono">Memory</span> in <span class="mono">letta/schemas/memory.py</span>, whose <span class="mono">compile()</span> method stitches the blocks into one text; and the agent edits its own memory through the <span class="mono">core_memory_append</span> / <span class="mono">core_memory_replace</span> tools (see <span class="mono">letta/services/tool_executor/core_tool_executor.py</span>).
</div>

<h2>The soul: self-editing memory = rewriting your own system prompt</h2>
<p>Here is the lesson's most elegant, most counter-intuitive point. You might assume "the agent remembers a fact" by writing it into some ordinary DB field. But in Letta, <strong>core memory is compiled into the system prompt</strong> — meaning when the agent calls <span class="mono">core_memory_replace</span> to change a memory block, it is <strong>literally rewriting its own message #0, its own "factory settings"</strong>. On the next turn, the new system prompt takes effect from the very first token.</p>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  <strong>MemGPT's "operating system" analogy</strong> is the key to the whole of Letta: treat the LLM as the <strong>CPU</strong>, the context window as limited <strong>RAM</strong>, and external memory as near-infinite <strong>disk</strong>. When "RAM" overflows, the agent does what an OS does on a page fault — it <strong>pages</strong>, actively calling memory tools to move content between RAM and disk.<br><br>
  The real "aha": <strong>self-editing memory is the agent rewriting its own system prompt</strong>. The output of <span class="mono">Memory.compile()</span> is spliced into that <strong>persisted system message</strong>; the moment a block changes, <span class="mono">agent_manager.rebuild_system_prompt_async</span> <strong>rewrites message #0</strong>. In other words the agent is not merely "jotting in a notebook" — it is <strong>continually rewriting the very prompt that defines who it is</strong>. That is what a "self-improving agent" really means mechanically.
</div>

<p>Trace the loop in pseudocode (idea from <span class="mono">core_tool_executor.py</span> and <span class="mono">agent_manager.rebuild_system_prompt_async</span>):</p>

<pre class="code"><span class="cm"># the agent's self-editing memory loop (pseudocode)</span>
<span class="kw">def</span> <span class="fn">core_memory_replace</span>(label, old, new):
    block = memory.get_block(label)       <span class="cm"># find persona/human block</span>
    block.value = block.value.replace(old, new)
    persist(block)                         <span class="cm"># write back to the DB</span>
    <span class="cm"># key: memory changed -&gt; recompile the system prompt</span>
    new_system = memory.<span class="fn">compile</span>()      <span class="cm"># stitch all blocks into new system text</span>
    rebuild_system_prompt(agent)           <span class="cm"># rewrite message #0 (system)</span>
</pre>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>User says something worth remembering</h4><p>e.g. "call me Timber from now on".</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Agent calls <span class="mono">core_memory_replace</span></h4><p>swaps the old value in the human block for the new one.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Block written back to DB</h4><p>the change is persisted and survives the conversation ending.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>System prompt <strong>recompiled</strong></h4><p><span class="mono">Memory.compile()</span> yields new text, rewriting message #0.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Effective next turn</h4><p>the new setting "lives on" the agent from its next reply.</p></div></div>
</div>

<div class="card warn">
  <div class="tag">⚠️ Easy to misread</div>
  "Stateful" does not mean "the model itself now has memory". The underlying LLM is <strong>still stateless on every call</strong>; memory is what Letta the <strong>framework adds around the model</strong>: it persists state in the DB and re-assembles the context each step before feeding the model. Strictly, the <strong>framework</strong> has memory; the model is just "fed" more cleverly.
</div>

<h2>Dig a little deeper</h2>

<details class="accordion"><summary>Why not just stuff the entire history into context?</summary><div class="acc-body">
<p><strong>Example:</strong> with hundred-thousand-token context windows, why not dump the whole chat log in?</p>
<p><strong>Why it is designed this way:</strong> context is not free. More tokens means <strong>each call is pricier and slower</strong>; piling in irrelevant content also <strong>dilutes attention</strong> so the model misses the point. And realistically the window has a ceiling: a long-enough chat <strong>eventually overflows</strong>. The right move is to keep only "what belongs" in-window and stash the rest, fetching on demand.</p>
<p><strong>Where in source:</strong> window and context size come from <span class="mono">AgentState.llm_config</span>; compiling memory into context is handled by <span class="mono">letta/schemas/memory.py::Memory.compile</span> and <span class="mono">letta/prompts/prompt_generator.py::PromptGenerator</span>.</p>
<p><strong>Alternatives:</strong> pure long context (costly and capped) or pure vector RAG (no tiers, agent cannot self-manage). Letta picks "tiers + agent self-management", expanded in <strong>lesson 3 (the life of a message)</strong> and Part 3.</p>
</div></details>

<details class="accordion"><summary>How is Letta different from OpenAI Assistants / LangChain memory?</summary><div class="acc-body">
<p><strong>Example:</strong> they all sound like they "added memory to an LLM" — so what is the difference?</p>
<p><strong>Why it is designed this way:</strong> three differences. One, Letta lets the <strong>agent itself edit</strong> tiered memory (core/recall/archival) rather than only retrieving passively from outside; two, <strong>state lives entirely in the DB</strong>, so one <span class="mono">AgentState</span> fully reconstructs an agent; three, it is <strong>model-agnostic</strong> — swapping the base model does not change the memory mechanism.</p>
<p><strong>Where in source:</strong> the state is defined in <span class="mono">schemas/agent.py::AgentState</span>, the self-management tools in <span class="mono">core_tool_executor.py</span>, orchestration in <span class="mono">letta/server/server.py::SyncServer</span> and <span class="mono">agent_manager.py</span>.</p>
<p><strong>Alternatives:</strong> OpenAI Assistants hosts state in its own service with an opaque memory policy; LangChain offers memory components but you wire and persist them yourself. Letta's trade-off is "stateful out of the box, fully transparent and self-hostable".</p>
</div></details>

<details class="accordion"><summary>MemGPT's core idea in one sentence</summary><div class="acc-body">
<p><strong>Example:</strong> if you can keep only one sentence, keep this: <strong>LLM ≈ CPU, context ≈ RAM, external store ≈ disk, memory tools ≈ system calls / paging.</strong></p>
<p><strong>Why it is designed this way:</strong> operating systems solved "memory too small" decades ago with tiered storage and paging. MemGPT carries the same idea to agents: let the agent, like an OS scheduling memory, decide what stays in context and what is paged out.</p>
<p><strong>Where in source:</strong> "paging" corresponds to the memory tools in <span class="mono">core_tool_executor.py</span>, plus retrieval-related <span class="mono">block_manager.py</span> / <span class="mono">passage_manager.py</span>.</p>
<p><strong>Alternatives:</strong> no tiers, everything in one giant prompt — it runs, but it is costly, slow, and eventually overflows. The OS analogy's value is telling you "tiers + autonomous scheduling" is the sustainable answer.</p>
</div></details>

<h2>Where this lesson sits in the big picture</h2>
<p>You are now at the <strong>start</strong> of the whole guide: you know why Letta exists (stateless LLM + finite context), its core abstraction (one self-editable <span class="mono">AgentState</span>), and its most elegant design (self-editing memory = rewriting the system prompt). This part (the big picture) has two more lessons: <strong>the next one (lesson 2), the project map</strong>, tours the <span class="mono">letta/</span> directory and the "REST routes → services → ORM/DB" three layers; <strong>lesson 3, the life of a message</strong>, follows one user message from arrival to reply. Later, <strong>Part 3 (the memory system)</strong> unpacks the three tiers we only sketched today. Carry the key "an agent is one AgentState" and the rest will go down much easier.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>A <strong>stateless</strong> LLM plus <strong>finite</strong> context is the whole reason Letta exists.</li>
    <li>Letta (formerly MemGPT) makes agents <strong>stateful</strong>; the state is one <span class="mono">AgentState</span> row in the DB.</li>
    <li>Memory has <strong>three tiers</strong>: core (sticky notes in view) / recall (searchable history) / archival (vector archive).</li>
    <li>Soul feature: the agent <strong>self-edits memory</strong>, and mechanically that equals <strong>rewriting its own system prompt</strong> (<span class="mono">Memory.compile</span>'s output is re-stitched into message #0).</li>
    <li>OS analogy: LLM≈CPU, context≈RAM, external memory≈disk, memory tools≈paging.</li>
  </ul>
</div>
""",
}

LESSON_02 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
还记得上一课的结论吗——<strong>一个 agent 就是数据库里的一条 <span class="mono">AgentState</span></strong>。这一课要回答的是：这条状态住在一座什么样的"房子"里？我们会摊开 <span class="mono">letta/</span> 的目录地图，并把整个后端看成清清楚楚的<strong>三层</strong>：REST 路由 → 服务层（managers）→ ORM / 数据库。这是全书的"<strong>整体结构图</strong>"——记住它，后面每一课讲的细节，你都能在这张图上找到自己的位置。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把 Letta 的后端想象成一家<strong>运转良好的餐厅</strong>。<strong>前台服务员</strong>（REST 路由）只负责接待：听你点单、把菜端上桌，自己从不下厨；<strong>后厨大师傅</strong>（services 里的各种 <span class="mono">*Manager</span>）才是真正干活的人——所有业务逻辑、火候与配方都压在这里；而<strong>中央仓库</strong>（ORM / 数据库）统一管理食材进出，谁能取哪批货、怎么记账，都按一套铁打的规矩来。前台越薄、后厨越厚、仓库越通用，这家店就越好扩张、越不容易出乱子。Letta 的代码恰恰就是这么分工的。
</div>

<h2>三层架构：把后端拆成清清楚楚的三层</h2>
<p>很多人第一次打开 <span class="mono">letta/</span> 会被几十个目录吓到。其实只要抓住一条主线，复杂度立刻坍缩成<strong>三层</strong>：从上到下，每一层只跟相邻的层说话、各司其职。这就是本课的整体结构图——先把它刻在脑子里：</p>

<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">REST 路由</span><span class="name">server/rest_api/routers/v1/*</span></div>
    <div class="ld">很薄：解析 actor、收发 HTTP，把活立刻交给 services。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">服务层</span><span class="name">services/*Manager</span></div>
    <div class="ld">业务逻辑都在这里：开 DB 会话、调 ORM、做 schema &lt;-&gt; orm 转换。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">ORM 模型</span><span class="name">orm/* · SqlalchemyBase</span></div>
    <div class="ld">通用 CRUD + <span class="mono">apply_access_predicate</span> 多租户行级隔离。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">数据库</span><span class="name">SQLite（开发）/ Postgres+pgvector（生产）</span></div>
    <div class="ld"><span class="mono">settings.database_engine</span> 选型；同一套代码，两种库。</div></div>
</div>

<p><strong>从上往下读</strong>：最上面的 <span class="mono">REST 路由</span>层薄得几乎没有逻辑，它只做"翻译"——把一个 HTTP 请求解析成"谁（actor）要对哪个 agent 做什么"，然后立刻把活交给下一层。中间的<strong>服务层</strong>才是真正的主角：所有业务规则、数据库会话、模型与数据库之间的来回转换，统统压在这一层。再往下，<span class="mono">orm/</span> 把每张表抽象成 Python 对象，并由一个共同的基类 <span class="mono">SqlalchemyBase</span> 提供"<strong>通用的增删改查</strong>"。最底层才是真正的数据库——开发时是一个文件式的 SQLite，上了生产换成 Postgres（配 <span class="mono">pgvector</span> 做向量检索），而上面三层的代码<strong>几乎一行都不用改</strong>。</p>

<p><strong>为什么非要这么严格地分层？</strong>因为"每层只跟相邻层说话"换来了三种自由：其一，<strong>底层可替换</strong>——把 SQLite 换成 Postgres，只要 ORM 那层适配好，上面的服务与路由毫不知情；其二，<strong>中层可单测</strong>——直接调 <span class="mono">*Manager</span> 的方法就能测业务，不必费劲假装发一个 HTTP 请求；其三，<strong>上层可多样</strong>——同一套业务既能被 REST 调，也能被 CLI、后台任务调。分层不是为了好看，而是让每一块都能<strong>独立演进、独立替换、独立测试</strong>。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  整张后端的"中枢"只有一个，叫 <span class="mono">SyncServer</span>（在 <span class="mono">letta/server/server.py</span>）。它像餐厅的<strong>总调度</strong>：一上电就把所有 <span class="mono">*Manager</span> 都创建好、挂在自己身上——<span class="mono">agent_manager</span>、<span class="mono">message_manager</span>、<span class="mono">block_manager</span>、<span class="mono">passage_manager</span>、<span class="mono">user_manager</span>…… 几十个"经理"各管一摊。<span class="mono">app.py</span> 里只有<strong>一个</strong>全局 <span class="mono">SyncServer</span> 实例，REST 路由想干活，就向它要对应的经理。把"谁持有谁"理顺，整个项目的脉络就清楚了。
</div>

<h2>跟着一次请求穿过三层</h2>
<p>光看分层还不够，得看它<strong>动起来</strong>。拿你最熟悉的动作——给 agent 发一条消息——走一遍，看请求怎么自上而下穿过三层、再把结果带回来：</p>

<div class="flow">
  <div class="node hl"><div class="nt">REST 路由</div><div class="nd">send_message</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">SyncServer / Manager</div><div class="nd">业务 + DB 会话</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">ORM CRUD</div><div class="nd">apply_access_predicate</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">数据库</div><div class="nd">SQLite / Postgres</div></div>
</div>

<p>这条链路最值得玩味的是它的<strong>第一站</strong>。你可能以为"发消息"这种核心动作，路由里一定写满了逻辑；恰恰相反，真实的 <span class="mono">send_message</span> 短得惊人。把它简化出来看：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/routers/v1/agents.py</span><span class="ln">send_message（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">send_message</span>(agent_id, request, server, headers):
    actor = <span class="kw">await</span> server.user_manager.<span class="fn">get_actor_or_default_async</span>(headers.actor_id)
    agent = <span class="kw">await</span> server.agent_manager.<span class="fn">get_agent_by_id_async</span>(agent_id, actor)
    loop  = AgentLoop.<span class="fn">load</span>(agent_state=agent, actor=actor)
    <span class="kw">return await</span> loop.<span class="fn">step</span>(request.messages)   <span class="cm"># 路由只做这些；业务都在下层</span>
</pre></div>

<p>看见了吗？路由只做三件事：<strong>解析出 actor</strong>（哪个用户/组织在操作）、<strong>按 id 把 agent 取出来</strong>、<strong>交给 agent 循环跑一步</strong>。它不开数据库会话、不拼上下文、不调模型——这些全在下层。这就是"薄路由"的含义：<strong>路由是入口，不是车间</strong>。</p>

<p>这里还藏着一个贯穿全局的细节：第一行解析出来的 <span class="mono">actor</span>。它代表"<strong>此刻是哪个用户、属于哪个组织在操作</strong>"，并会被一路往下传——传到 manager、再传到 ORM 的 <span class="mono">apply_access_predicate</span>，最终变成数据库查询里那道"只看自己组织"的过滤。换句话说，<strong>多租户隔离从路由的第一行就开始了</strong>，之后每一层都在接力，而不是等到最后才补一刀。记住 <span class="mono">actor</span> 这个词，它会在后面的课里反复出现。</p>

<h3><span class="mono">letta/</span> 目录全景</h3>
<p>建立了三层骨架，再把血肉填上——下面这张表是 <span class="mono">letta/</span> 里最该先认识的几个目录。读代码时先问"我关心的是哪一层、哪一块"，再按图索骥，比一头扎进去高效得多：</p>

<table class="t">
  <tr><th>目录</th><th>作用</th></tr>
  <tr><td class="mono">agents/</td><td>agent 运行时与执行循环（<span class="mono">letta_agent_v3.py</span>、<span class="mono">agent_loop.py</span>）</td></tr>
  <tr><td class="mono">schemas/</td><td>Pydantic 数据契约：<span class="mono">AgentState</span> · <span class="mono">Memory</span> · <span class="mono">Block</span> · <span class="mono">Message</span> · <span class="mono">LLMConfig</span></td></tr>
  <tr><td class="mono">services/</td><td>业务逻辑层：各 <span class="mono">*Manager</span>（agent / message / block / passage …）</td></tr>
  <tr><td class="mono">orm/</td><td>SQLAlchemy 持久化模型 + <span class="mono">SqlalchemyBase</span> 通用 CRUD</td></tr>
  <tr><td class="mono">server/</td><td>FastAPI REST 服务、<span class="mono">SyncServer</span>、路由 <span class="mono">rest_api/routers/v1/*</span></td></tr>
  <tr><td class="mono">functions/</td><td>工具：从函数 + docstring 生成 schema、内置工具集</td></tr>
  <tr><td class="mono">llm_api/</td><td>多家 LLM provider 的统一客户端抽象</td></tr>
  <tr><td class="mono">prompts/</td><td>系统提示文本 + <span class="mono">PromptGenerator</span>（把记忆编译进 system message）</td></tr>
</table>

<p>这八个目录里，<span class="mono">schemas/</span> 和 <span class="mono">orm/</span> 最容易被搞混——一个是"对外的数据契约"，一个是"对内的存储模型"，我们待会儿在折叠里专门拆。先记住一条对应关系：<strong>路由在 <span class="mono">server/</span>、业务在 <span class="mono">services/</span>、存储在 <span class="mono">orm/</span></strong>，而穿过这三层、始终被传来传去的核心对象，就是上一课那条 <span class="mono">AgentState</span>。</p>

<p>顺带认一下另外三个"能力面"的目录：<span class="mono">functions/</span> 负责把一个普通 Python 函数 + 它的 docstring 自动变成模型看得懂的工具 schema；<span class="mono">llm_api/</span> 把 OpenAI、Anthropic、Google 等各家厂商的差异抹平成统一的客户端接口，于是"换模型"基本不动业务；<span class="mono">prompts/</span> 则由 <span class="mono">PromptGenerator</span> 把记忆与人设编译进系统提示。它们不在"三层主干"上，却是让 agent 真正<strong>能调工具、能跨厂商、会说话</strong>的三块拼图。</p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  落到真实符号：三层分别对应 <span class="mono">letta/server/rest_api/routers/v1/*</span>（路由）、<span class="mono">letta/services/*_manager.py</span>（服务）、<span class="mono">letta/orm/*</span>（ORM）。中枢是 <span class="mono">letta/server/server.py::SyncServer</span>；最常打交道的经理是 <span class="mono">services/agent_manager.py::AgentManager</span>；所有 ORM 模型的共同基类是 <span class="mono">letta/orm/sqlalchemy_base.py::SqlalchemyBase</span>；数据库会话由 <span class="mono">letta/server/db.py</span> 的 <span class="mono">db_registry.async_session()</span> 提供；用哪种数据库由 <span class="mono">letta/settings.py::database_engine</span> 决定（设了 Postgres 连接串就用 Postgres，否则回落到 SQLite）。
</div>

<h2>厚服务：业务逻辑都压在 managers</h2>
<p>既然路由那么薄，活儿到底谁干？答案是<strong>服务层</strong>。每个 <span class="mono">*Manager</span> 都是一组方法的集合，套路高度统一：<strong>开一个数据库会话 → 用 ORM 查/改 → 把结果转回 pydantic 模型返回</strong>。拿路由里调用过的 <span class="mono">get_agent_by_id_async</span> 当样板（已简化）：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/agent_manager.py</span><span class="ln">AgentManager.get_agent_by_id_async（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentManager</span>:
    <span class="kw">async def</span> <span class="fn">get_agent_by_id_async</span>(self, agent_id, actor):
        <span class="kw">async with</span> db_registry.<span class="fn">async_session</span>() <span class="kw">as</span> session:
            query = <span class="fn">select</span>(AgentModel)
            query = AgentModel.<span class="fn">apply_access_predicate</span>(query, actor, [<span class="st">"read"</span>])
            query = query.<span class="fn">where</span>(AgentModel.id == agent_id)
            row   = (<span class="kw">await</span> session.<span class="fn">execute</span>(query)).<span class="fn">scalar_one_or_none</span>()
            <span class="kw">return await</span> row.<span class="fn">to_pydantic_async</span>()   <span class="cm"># ORM 行 -&gt; pydantic schema</span>
</pre></div>

<p>三步骨架一目了然：<span class="mono">async with db_registry.async_session()</span> 借来一个异步会话，<span class="mono">apply_access_predicate</span> 给查询自动加上"只看自己组织"的过滤，最后 <span class="mono">to_pydantic_async()</span> 把数据库行<strong>翻译成对外的 pydantic 模型</strong>。注意那行 <span class="mono">apply_access_predicate</span>——它不是这个方法特有的，而是<strong>几乎每个 manager 查询都会用</strong>的同一道护栏。</p>

<p>正因为每个 manager 方法都长这一个样子——开会话、加隔离、查改、再转 pydantic——你读懂一个，就读懂了一整类。想找"创建 agent"的逻辑？去 <span class="mono">agent_manager.py</span> 找 <span class="mono">create</span> 系列方法；想"取回某段对话"？去 <span class="mono">message_manager.py</span>。<strong>目录 + 命名 + 统一套路</strong>三者一合，就是一张比任何文档都可靠的代码地图。</p>

<p>为什么能这么统一？秘密在最底层。</p>

<h2>通用 ORM：一处实现，处处受益</h2>
<p>Letta 的 ORM 有个让人会心一笑的设计：所有数据库模型都继承同一个基类 <span class="mono">SqlalchemyBase</span>，于是<strong>增删改查、分页、软删除、多租户隔离</strong>这些活儿，只在这一个地方写一遍，每张表就都自动拥有了。其中最关键的是多租户隔离那一道——看它有多简单：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/orm/sqlalchemy_base.py</span><span class="ln">apply_access_predicate（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">SqlalchemyBase</span>(Base):          <span class="cm"># 每个 ORM 模型都继承它</span>
    <span class="nb">@classmethod</span>
    <span class="kw">def</span> <span class="fn">apply_access_predicate</span>(cls, query, actor, access):
        <span class="cm"># 给任意查询自动加一道 WHERE：只看本组织的数据</span>
        <span class="kw">return</span> query.<span class="fn">where</span>(cls.organization_id == actor.organization_id)
</pre></div>

<p>就这么一行 <span class="mono">WHERE organization_id = 当前用户的组织</span>，却是 Letta 能安全托管成千上万租户的地基：任何查询只要走 <span class="mono">apply_access_predicate</span>，就<strong>不可能</strong>看到别人组织的数据——而且这是<strong>默认行为</strong>，写新功能的人想绕都得特意绕。再加上软删除（删除只是把 <span class="mono">is_deleted</span> 置真）和统一分页，<strong>安全与一致性被"焊死"在了最底层</strong>，而不是指望每个写业务的人都记得加。</p>

<h3>schemas 与 orm：同一个对象的两副面孔</h3>
<p>上面反复出现两个词——<span class="mono">schemas</span> 和 <span class="mono">orm</span>。它们描述的常常是"同一个东西"（比如一个 Agent），却活在两个不同的世界：</p>

<div class="cols">
  <div class="col"><h4>Pydantic 数据契约 · schemas/</h4><p>面向<strong>外部</strong>：API 的请求/响应长什么样、字段如何校验、如何序列化成 JSON。<span class="mono">AgentState</span>、<span class="mono">Memory</span>、<span class="mono">Block</span>、<span class="mono">Message</span> 都住在这里，通常一套"三件"：<span class="mono">Create</span> / <span class="mono">Update</span> / 读取模型。</p></div>
  <div class="col"><h4>SQLAlchemy ORM 模型 · orm/</h4><p>面向<strong>内部</strong>：数据怎么落到数据库的表与列、关系如何连。<span class="mono">orm/agent.py::Agent</span> 等都继承 <span class="mono">SqlalchemyBase</span>。manager 取出 ORM 行后，用 <span class="mono">to_pydantic</span> 翻成 schema 再返回给上层。</p></div>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>薄路由、厚服务、通用 ORM</strong>——这三句话是看懂整个 Letta 后端的钥匙；而真正的"啊哈"，在于它们各自<strong>换来一个大好处</strong>：<br><br>
  ① <strong>通用 ORM = 安全与一致性默认免费。</strong><span class="mono">SqlalchemyBase</span> 一处实现泛型 CRUD，<span class="mono">apply_access_predicate</span> 给每张表自动加上多租户行级隔离——分页、软删除、隔离都是"<strong>secure by default</strong>"，新建一张表就白捡这些能力。<br>
  ② <strong>厚服务 + 薄路由 = 一套业务、多种入口。</strong>逻辑全在 <span class="mono">*Manager</span>，于是 REST 接口、CLI、后台任务、测试可以<strong>复用同一套</strong>方法，路由只是众多入口里的一个。<br>
  ③ <strong>无状态运行时 = 水平扩展。</strong>整个服务端是<strong>一个</strong> <span class="mono">SyncServer</span> 持有全部经理；而 agent 本身"不黏进程"——它只是把序列化的 <span class="mono">AgentState</span> 取出来、跑一步、再写回。任何一台机器都能接手任何一个 agent，于是加机器就能扛更多负载。<br><br>
  一句话：<strong>把"难做对的事"（隔离、扩展、复用）下沉到框架底层做一次，让上层无论怎么写都不容易出错。</strong>
</div>

<h2>无状态运行时：同一个 agent，哪台机器都能接手</h2>
<p>前面反复说 agent"不黏进程"，这里把它说透。一个正在"思考"的 agent，本质上<strong>没有任何东西常驻在某台机器的内存里</strong>——它要用的一切，都来自数据库里那条 <span class="mono">AgentState</span>。所以处理一条消息的真实节奏，永远是干净利落的三拍：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>取出 load</h4><p>按 <span class="mono">agent_id</span> 从库里读出 <span class="mono">AgentState</span>：记忆块、在窗消息、可用工具、模型配置一并取齐。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>跑一步 step</h4><p><span class="mono">AgentLoop.load</span> 据此造出运行时 agent；<span class="mono">step</span> 里读消息、组装上下文、调模型、按需执行工具。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>写回 persist</h4><p>新产生的消息、记忆改动、状态更新统统落库；这一拍一结束，内存里那个运行时 agent 就可以<strong>彻底丢弃</strong>。</p></div></div>
</div>

<p>这三拍带来一个极其实用的性质：<strong>处理同一个 agent 的两条消息，完全可以落在两台不同的机器上</strong>——因为"上一步"的所有结果都已经在数据库里，"下一步"无非是再 <span class="mono">load</span> 一次。于是 Letta 服务端可以像普通的无状态 Web 服务那样<strong>水平扩展</strong>：流量大了就加机器，请求随便路由到哪一台都行，背后共享同一个数据库。这正是把"状态"从"进程"里彻底剥离、塞进 <span class="mono">AgentState</span> 的回报。</p>

<p>回看上一课那句"<strong>取出 → 跑一步 → 写回</strong>"，现在你知道它分别落在哪一层了：<strong>取出</strong>与<strong>写回</strong>是 <span class="mono">services/</span> 里各 <span class="mono">*Manager</span> 的活，<strong>跑一步</strong>是 <span class="mono">agents/</span> 的活，而把它们串起来、对外发令的，是 <span class="mono">server/</span> 路由那薄薄的一层。三层架构与"有状态 agent"，在这里严丝合缝地合上了。</p>

<div class="card warn">
  <div class="tag">⚠️ 容易误解</div>
  "无状态运行时"不是说 Letta <strong>整个系统</strong>无状态——状态稳稳地存在数据库里。无状态的只是<strong>处理请求的那段运行时</strong>：它不在内存里攒东西，每次都从 <span class="mono">AgentState</span> 重建、用完即弃。把"<strong>有状态的数据</strong>"和"<strong>无状态的运行时</strong>"分开来看，才不会把这句话理解反。
</div>

<h3>按学习路线读代码</h3>
<p>最后给你一张"读码路线图"。不必从头到尾啃完整个仓库——按你当下的目标，挑对应的一层切进去就好：</p>

<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">想跑起来</span><span class="name">server/ · cli/</span></div>
    <div class="ld">先看 <span class="mono">server/rest_api/app.py</span> 的 <span class="mono">create_application</span> 与全局 <span class="mono">SyncServer</span>；命令行入口在 <span class="mono">cli/cli.py</span>。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">懂记忆</span><span class="name">schemas/memory.py · services/*</span></div>
    <div class="ld"><span class="mono">Memory</span> / <span class="mono">Block</span> 的数据契约，加上 <span class="mono">block_manager</span> / <span class="mono">passage_manager</span> 怎么存取。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">懂循环</span><span class="name">agents/letta_agent_v3.py</span></div>
    <div class="ld"><span class="mono">LettaAgentV3.step</span>：读消息 → 组装上下文 → 调模型 → 执行工具 → 写回。</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">懂存储</span><span class="name">orm/ · server/db.py</span></div>
    <div class="ld"><span class="mono">SqlalchemyBase</span> 通用 CRUD、<span class="mono">db_registry.async_session</span> 开会话。</div></div>
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>为什么路由要写得这么"薄"？</summary><div class="acc-body">
<p><strong>示例：</strong>真实的 <span class="mono">send_message</span> 几乎把活全转给了下层，路由里看不到什么 if/else 业务判断。</p>
<p><strong>为什么这样设计：</strong>因为业务一旦写进路由，就只能从 HTTP 入口用；放进 manager，则 CLI、后台任务、测试都能直接调<strong>同一个方法</strong>。薄路由还让"换协议"（比如把普通响应换成 SSE 流式）只动入口、不动业务——稳定的核心被入口层的变化保护着。</p>
<p><strong>源码在哪：</strong>路由 <span class="mono">letta/server/rest_api/routers/v1/agents.py::send_message</span>；业务在 <span class="mono">services/agent_manager.py</span> 等 <span class="mono">*Manager</span>。</p>
<p><strong>还有什么替代：</strong>"胖控制器"把业务直接写在路由里——上手快，但 CLI 与 REST 会各写一份、难测、容易漂移。Letta 选了薄路由，换取复用与可测。</p>
</div></details>

<details class="accordion"><summary>有了 schemas，为什么还要单独一套 orm？</summary><div class="acc-body">
<p><strong>示例：</strong>一个 Agent 既有 <span class="mono">schemas/agent.py::AgentState</span>（API 模型），又有 <span class="mono">orm/agent.py::Agent</span>（数据库模型），看起来"重复"。</p>
<p><strong>为什么这样设计：</strong>两者关心的事根本不同。pydantic schema 关心"<strong>对外契约</strong>"——字段校验、序列化、<span class="mono">Create</span>/<span class="mono">Update</span>/读取三件套；ORM 关心"<strong>对内存储</strong>"——表、列、外键、索引。分开之后，API 可以演进而不被数据库结构绑死，数据库也能重构而不惊动 API。manager 站在中间做转换。</p>
<p><strong>源码在哪：</strong><span class="mono">schemas/</span> 下的 pydantic 模型；<span class="mono">orm/</span> 下继承 <span class="mono">SqlalchemyBase</span> 的模型；转换方法如 <span class="mono">orm/agent.py::Agent.to_pydantic_async</span>。</p>
<p><strong>还有什么替代：</strong>只用一套模型（ORM 直接当 API 返回）——少写代码，但数据库结构会泄露到 API、校验与序列化也难做干净。两套模型是成熟后端的常见取舍。</p>
</div></details>

<details class="accordion"><summary><span class="mono">SyncServer</span> 到底是什么？</summary><div class="acc-body">
<p><strong>示例：</strong><span class="mono">app.py</span> 启动时只 new 了一个 <span class="mono">server = SyncServer(...)</span>，整个进程共用它。</p>
<p><strong>为什么这样设计：</strong>把所有 <span class="mono">*Manager</span> 的创建与持有集中到一个对象，依赖关系一目了然（例如 <span class="mono">agent_manager</span> 需要 <span class="mono">block_manager</span>，就在构造时注入）。路由通过依赖注入拿到这个全局 <span class="mono">server</span>，再用 <span class="mono">server.xxx_manager</span> 取经理——干净、可追踪。</p>
<p><strong>源码在哪：</strong><span class="mono">letta/server/server.py::SyncServer</span>（构造里逐个创建各 manager）；全局实例在 <span class="mono">letta/server/rest_api/app.py</span>（<span class="mono">server = SyncServer(...)</span>）。</p>
<p><strong>还有什么替代：</strong>每个请求各自 new 一堆 manager——重复又浪费；或把单例散落在全局各处——难追踪。集中到一个中枢，是"组合优于散落"的体现。</p>
</div></details>

<h2>这一课在整张大图的哪里</h2>
<p>你现在手里有了全书的<strong>整体结构图</strong>：<span class="mono">letta/</span> 的目录地图、REST → services → ORM/DB 三层、以及把它们串起来的中枢 <span class="mono">SyncServer</span>。把它和上一课接上——那条会自我编辑的 <span class="mono">AgentState</span>，正是被这三层<strong>取出、加工、写回</strong>的核心对象。<strong>下一课（第 3 课）一条消息的生命周期</strong>会把本课的 <span class="mono">send_message</span> 这一站放大成慢镜头：从路由进来、经 <span class="mono">AgentLoop.load</span> 载入 agent、再到 <span class="mono">step</span> 里"读消息 → 组装上下文 → 调模型 → 执行工具 → 写回"，一帧一帧看完。再往后第二、三部分讲工具与记忆时，你都能立刻定位到"它落在这张三层图的哪一层"。</p>

<p>把这张三层图当成你随身的导航：读到任何一个新模块，先问它属于<strong>路由、服务还是存储</strong>，再看它跟 <span class="mono">AgentState</span> 怎么打交道——只要这两个问题答得上来，再大的代码库也不会让你失去方向。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Letta 后端是清清楚楚的<strong>三层</strong>：REST 路由（薄）→ <span class="mono">services/*Manager</span>（厚）→ <span class="mono">orm/SqlalchemyBase</span> + 数据库。</li>
    <li>业务逻辑都在 <strong>services 层</strong>的 <span class="mono">*Manager</span>；路由只解析 actor、收发 HTTP。</li>
    <li>中枢是<strong>一个</strong> <span class="mono">SyncServer</span>，持有全部 <span class="mono">*Manager</span>；<span class="mono">app.py</span> 里只有一个全局实例。</li>
    <li>通用 ORM：<span class="mono">SqlalchemyBase</span> 一处实现 CRUD，<span class="mono">apply_access_predicate</span> 让每张表<strong>默认</strong>获得多租户行级隔离（secure by default），并自带软删除与分页。</li>
    <li><span class="mono">schemas</span>（对外 pydantic 契约）与 <span class="mono">orm</span>（对内存储模型）是<strong>两套模型</strong>，manager 负责转换。</li>
    <li><span class="mono">AgentState</span> 是穿过三层的核心对象；agent 是<strong>无状态运行时</strong>，因此可以水平扩展。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Remember last lesson's punchline — <strong>an agent is just one <span class="mono">AgentState</span> row in a database</strong>. This lesson answers: what kind of "house" does that row live in? We'll unroll the <span class="mono">letta/</span> directory map and view the whole backend as three crisp layers: REST routes → service layer (managers) → ORM / database. This is the guide's "<strong>overall structure diagram</strong>" — memorize it, and every detail in later lessons will have a place to sit.
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture Letta's backend as a <strong>well-run restaurant</strong>. The <strong>front-of-house waiter</strong> (REST routes) only greets you: takes the order, brings the dishes out, never cooks. The <strong>head chef</strong> (the various <span class="mono">*Manager</span>s in services) is who actually works — all business logic, timing and recipes sit here. And the <strong>central warehouse</strong> (ORM / database) governs every ingredient in and out: who may take which stock, and how it's accounted for, all follow one ironclad set of rules. The thinner the front, the thicker the kitchen, the more generic the warehouse — the easier the place scales and the less it breaks. Letta's code is split exactly this way.
</div>

<h2>The 3-layer architecture: a backend in three crisp layers</h2>
<p>Open <span class="mono">letta/</span> for the first time and a few dozen directories may scare you. But grab one through-line and the complexity collapses into <strong>three layers</strong>: top to bottom, each talks only to its neighbor, each with one job. This is the lesson's overall structure diagram — carve it into your mind first:</p>

<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">REST routes</span><span class="name">server/rest_api/routers/v1/*</span></div>
    <div class="ld">Very thin: parse the actor, send/receive HTTP, hand the work straight to services.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Service layer</span><span class="name">services/*Manager</span></div>
    <div class="ld">All business logic lives here: open a DB session, call the ORM, convert schema &lt;-&gt; orm.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">ORM models</span><span class="name">orm/* · SqlalchemyBase</span></div>
    <div class="ld">Generic CRUD + <span class="mono">apply_access_predicate</span> row-level multi-tenant isolation.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">Database</span><span class="name">SQLite (dev) / Postgres+pgvector (prod)</span></div>
    <div class="ld"><span class="mono">settings.database_engine</span> picks; one codebase, two databases.</div></div>
</div>

<p><strong>Read it top-down</strong>: the top <span class="mono">REST routes</span> layer is so thin it's almost logic-free — it just "translates" an HTTP request into "who (the actor) wants to do what to which agent", then immediately hands off downward. The middle <strong>service layer</strong> is the real protagonist: all business rules, database sessions, and the back-and-forth between models and tables sit here. Below that, <span class="mono">orm/</span> abstracts every table into a Python object, with a shared base class <span class="mono">SqlalchemyBase</span> providing <strong>generic create/read/update/delete</strong>. Only the bottom is the real database — a file-based SQLite in dev, swapped for Postgres (with <span class="mono">pgvector</span> for vector search) in prod — and the three layers above need <strong>almost no changes</strong>.</p>

<p><strong>Why insist on such strict layering?</strong> Because "each layer talks only to its neighbor" buys three freedoms: one, <strong>the bottom is swappable</strong> — swap SQLite for Postgres and, as long as the ORM layer adapts, the services and routes above are none the wiser; two, <strong>the middle is unit-testable</strong> — call a <span class="mono">*Manager</span> method directly to test business logic, no need to fake an HTTP request; three, <strong>the top is pluralizable</strong> — the same business is callable from REST, the CLI, or background jobs. Layering isn't for looks; it lets every piece <strong>evolve, swap, and test independently</strong>.</p>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  The whole backend has exactly one "hub", called <span class="mono">SyncServer</span> (in <span class="mono">letta/server/server.py</span>). It's the restaurant's <strong>head dispatcher</strong>: at startup it creates all the <span class="mono">*Manager</span>s and hangs them on itself — <span class="mono">agent_manager</span>, <span class="mono">message_manager</span>, <span class="mono">block_manager</span>, <span class="mono">passage_manager</span>, <span class="mono">user_manager</span>… dozens of "managers", each owning one slice. <span class="mono">app.py</span> holds <strong>one</strong> global <span class="mono">SyncServer</span> instance; whenever a route needs work done, it asks the hub for the right manager. Get "who holds whom" straight and the whole project's wiring becomes clear.
</div>

<h2>Follow one request through all three layers</h2>
<p>Looking at the layers isn't enough — watch them <strong>move</strong>. Take the action you know best — sending a message to an agent — and trace how the request crosses the three layers downward, then carries the result back:</p>

<div class="flow">
  <div class="node hl"><div class="nt">REST route</div><div class="nd">send_message</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">SyncServer / Manager</div><div class="nd">business + DB session</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">ORM CRUD</div><div class="nd">apply_access_predicate</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Database</div><div class="nd">SQLite / Postgres</div></div>
</div>

<p>The most telling part of this chain is its <strong>first stop</strong>. You'd assume a core action like "send a message" has a route stuffed with logic; on the contrary, the real <span class="mono">send_message</span> is startlingly short. Here it is, simplified:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/routers/v1/agents.py</span><span class="ln">send_message (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">send_message</span>(agent_id, request, server, headers):
    actor = <span class="kw">await</span> server.user_manager.<span class="fn">get_actor_or_default_async</span>(headers.actor_id)
    agent = <span class="kw">await</span> server.agent_manager.<span class="fn">get_agent_by_id_async</span>(agent_id, actor)
    loop  = AgentLoop.<span class="fn">load</span>(agent_state=agent, actor=actor)
    <span class="kw">return await</span> loop.<span class="fn">step</span>(request.messages)   <span class="cm"># the route does only this; business lives below</span>
</pre></div>

<p>See it? The route does three things: <strong>resolve the actor</strong> (which user/org is acting), <strong>load the agent by id</strong>, and <strong>hand it to the agent loop for one step</strong>. It opens no DB session, assembles no context, calls no model — all of that is downstairs. That's what "thin route" means: <strong>a route is an entrance, not a workshop</strong>.</p>

<p>There's also a detail here that runs through everything: the <span class="mono">actor</span> resolved on the first line. It represents "<strong>which user, in which organization, is acting right now</strong>", and it's passed all the way down — to the manager, then to the ORM's <span class="mono">apply_access_predicate</span>, finally becoming that "only my own org" filter in the database query. In other words, <strong>multi-tenant isolation begins on the route's very first line</strong>, and every layer after relays it — rather than bolting it on at the end. Remember the word <span class="mono">actor</span>; it recurs in later lessons.</p>

<h3>The <span class="mono">letta/</span> directory map</h3>
<p>With the three-layer skeleton in place, add the flesh — the table below lists the <span class="mono">letta/</span> directories worth meeting first. When reading code, ask "which layer, which piece do I care about" and navigate by the map, far more efficient than diving in headfirst:</p>

<table class="t">
  <tr><th>Directory</th><th>Role</th></tr>
  <tr><td class="mono">agents/</td><td>Agent runtime and execution loop (<span class="mono">letta_agent_v3.py</span>, <span class="mono">agent_loop.py</span>)</td></tr>
  <tr><td class="mono">schemas/</td><td>Pydantic data contracts: <span class="mono">AgentState</span> · <span class="mono">Memory</span> · <span class="mono">Block</span> · <span class="mono">Message</span> · <span class="mono">LLMConfig</span></td></tr>
  <tr><td class="mono">services/</td><td>Business-logic layer: the <span class="mono">*Manager</span>s (agent / message / block / passage …)</td></tr>
  <tr><td class="mono">orm/</td><td>SQLAlchemy persistence models + <span class="mono">SqlalchemyBase</span> generic CRUD</td></tr>
  <tr><td class="mono">server/</td><td>FastAPI REST service, <span class="mono">SyncServer</span>, routes <span class="mono">rest_api/routers/v1/*</span></td></tr>
  <tr><td class="mono">functions/</td><td>Tools: generate a schema from a function + docstring; built-in tool set</td></tr>
  <tr><td class="mono">llm_api/</td><td>A unified client abstraction over many LLM providers</td></tr>
  <tr><td class="mono">prompts/</td><td>System-prompt text + <span class="mono">PromptGenerator</span> (compiles memory into the system message)</td></tr>
</table>

<p>Of these eight, <span class="mono">schemas/</span> and <span class="mono">orm/</span> are the easiest to confuse — one is the "outward data contract", the other the "inward storage model"; we'll pull them apart in an accordion shortly. For now hold one mapping: <strong>routes in <span class="mono">server/</span>, business in <span class="mono">services/</span>, storage in <span class="mono">orm/</span></strong> — and the core object passed across all three layers is last lesson's <span class="mono">AgentState</span>.</p>

<p>While we're here, meet three more "capability-side" directories: <span class="mono">functions/</span> turns a plain Python function plus its docstring into a tool schema the model understands; <span class="mono">llm_api/</span> smooths over the differences among OpenAI, Anthropic, Google and others into one client interface, so "swapping models" barely touches business code; and <span class="mono">prompts/</span> uses <span class="mono">PromptGenerator</span> to compile memory and persona into the system prompt. They aren't on the "three-layer trunk", yet they're the three puzzle pieces that let an agent actually <strong>call tools, cross providers, and speak</strong>.</p>

<div class="card detail">
  <div class="tag">🔬 Source mapping</div>
  Pinned to real symbols: the three layers map to <span class="mono">letta/server/rest_api/routers/v1/*</span> (routes), <span class="mono">letta/services/*_manager.py</span> (services), and <span class="mono">letta/orm/*</span> (ORM). The hub is <span class="mono">letta/server/server.py::SyncServer</span>; the manager you'll meet most is <span class="mono">services/agent_manager.py::AgentManager</span>; the shared base of every ORM model is <span class="mono">letta/orm/sqlalchemy_base.py::SqlalchemyBase</span>; DB sessions come from <span class="mono">letta/server/db.py</span>'s <span class="mono">db_registry.async_session()</span>; and which database is used is decided by <span class="mono">letta/settings.py::database_engine</span> (set a Postgres URI and it uses Postgres, otherwise it falls back to SQLite).
</div>

<h2>Thick services: business logic sits in the managers</h2>
<p>If the route is that thin, who does the work? The <strong>service layer</strong>. Each <span class="mono">*Manager</span> is a set of methods following a highly uniform pattern: <strong>open a DB session → query/modify via the ORM → convert the result back to a pydantic model and return it</strong>. Take the <span class="mono">get_agent_by_id_async</span> the route called, as a template (simplified):</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/agent_manager.py</span><span class="ln">AgentManager.get_agent_by_id_async (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentManager</span>:
    <span class="kw">async def</span> <span class="fn">get_agent_by_id_async</span>(self, agent_id, actor):
        <span class="kw">async with</span> db_registry.<span class="fn">async_session</span>() <span class="kw">as</span> session:
            query = <span class="fn">select</span>(AgentModel)
            query = AgentModel.<span class="fn">apply_access_predicate</span>(query, actor, [<span class="st">"read"</span>])
            query = query.<span class="fn">where</span>(AgentModel.id == agent_id)
            row   = (<span class="kw">await</span> session.<span class="fn">execute</span>(query)).<span class="fn">scalar_one_or_none</span>()
            <span class="kw">return await</span> row.<span class="fn">to_pydantic_async</span>()   <span class="cm"># ORM row -&gt; pydantic schema</span>
</pre></div>

<p>The three-step skeleton is plain: <span class="mono">async with db_registry.async_session()</span> borrows an async session, <span class="mono">apply_access_predicate</span> auto-adds the "only my own org" filter, and finally <span class="mono">to_pydantic_async()</span> <strong>translates the database row into the outward pydantic model</strong>. Note that <span class="mono">apply_access_predicate</span> line — it isn't special to this method; it's the same guardrail used by <strong>nearly every manager query</strong>.</p>

<p>Precisely because every manager method looks like this one — open a session, add isolation, query/modify, then convert to pydantic — read one and you've read a whole class of them. Looking for the "create agent" logic? Go to <span class="mono">agent_manager.py</span> and find the <span class="mono">create</span> family; want to "fetch a chunk of conversation"? Go to <span class="mono">message_manager.py</span>. <strong>Directory + naming + a uniform pattern</strong> together form a code map more reliable than any document.</p>

<p>Why can it be this uniform? The secret is at the very bottom.</p>

<h2>Generic ORM: write it once, benefit everywhere</h2>
<p>Letta's ORM has a design that makes you smile: every database model inherits the same base, <span class="mono">SqlalchemyBase</span>, so the chores of <strong>CRUD, pagination, soft delete, and multi-tenant isolation</strong> are written once, in this one place, and every table gets them automatically. The most important is the isolation guardrail — see how simple it is:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/orm/sqlalchemy_base.py</span><span class="ln">apply_access_predicate (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">SqlalchemyBase</span>(Base):          <span class="cm"># every ORM model inherits this</span>
    <span class="nb">@classmethod</span>
    <span class="kw">def</span> <span class="fn">apply_access_predicate</span>(cls, query, actor, access):
        <span class="cm"># auto-adds a WHERE to any query: only this org's rows</span>
        <span class="kw">return</span> query.<span class="fn">where</span>(cls.organization_id == actor.organization_id)
</pre></div>

<p>Just that one line — <span class="mono">WHERE organization_id = the current user's org</span> — yet it's the bedrock that lets Letta safely host thousands of tenants: any query that goes through <span class="mono">apply_access_predicate</span> <strong>cannot</strong> see another org's data — and that's the <strong>default behavior</strong>; a developer would have to go out of their way to bypass it. Add soft delete (deletion just sets <span class="mono">is_deleted</span> true) and uniform pagination, and <strong>safety and consistency are welded into the lowest layer</strong> — instead of hoping every business author remembers to add them.</p>

<h3>schemas vs orm: two faces of the same object</h3>
<p>Two words keep recurring above — <span class="mono">schemas</span> and <span class="mono">orm</span>. They often describe "the same thing" (say, an Agent), yet live in two different worlds:</p>

<div class="cols">
  <div class="col"><h4>Pydantic data contracts · schemas/</h4><p>Facing <strong>outward</strong>: what the API request/response looks like, how fields validate, how they serialize to JSON. <span class="mono">AgentState</span>, <span class="mono">Memory</span>, <span class="mono">Block</span>, <span class="mono">Message</span> live here — usually a "set of three": <span class="mono">Create</span> / <span class="mono">Update</span> / read models.</p></div>
  <div class="col"><h4>SQLAlchemy ORM models · orm/</h4><p>Facing <strong>inward</strong>: how data lands in tables and columns, how relations connect. <span class="mono">orm/agent.py::Agent</span> and friends inherit <span class="mono">SqlalchemyBase</span>. After a manager loads an ORM row, it uses <span class="mono">to_pydantic</span> to turn it into a schema before returning it upward.</p></div>
</div>

<div class="card spark">
  <div class="tag">💡 Spark</div>
  <strong>Thin routes, thick services, generic ORM</strong> — these three phrases are the key to the whole Letta backend; the real "aha" is how each <strong>buys a big payoff</strong>:<br><br>
  ① <strong>Generic ORM = safety and consistency for free, by default.</strong> <span class="mono">SqlalchemyBase</span> implements generic CRUD in one place, and <span class="mono">apply_access_predicate</span> auto-adds row-level multi-tenant isolation to every table — pagination, soft delete, isolation are all "<strong>secure by default</strong>", picked up free by any new table.<br>
  ② <strong>Thick services + thin routes = one business, many entrances.</strong> Logic lives entirely in the <span class="mono">*Manager</span>s, so REST endpoints, the CLI, background jobs, and tests can <strong>reuse the same</strong> methods; a route is just one entrance among many.<br>
  ③ <strong>Stateless runtime = horizontal scale.</strong> The whole server is <strong>one</strong> <span class="mono">SyncServer</span> holding all managers; and the agent itself "doesn't stick to a process" — it just loads the serialized <span class="mono">AgentState</span>, runs a step, and saves it back. Any machine can take over any agent, so adding machines adds capacity.<br><br>
  In one line: <strong>push "the things hard to get right" (isolation, scale, reuse) down into the framework's floor and do them once, so the upper layers are hard to get wrong no matter how they're written.</strong>
</div>

<h2>Stateless runtime: any machine can take over the same agent</h2>
<p>We keep saying the agent "doesn't stick to a process" — here's the full story. An agent that's "thinking" has, in essence, <strong>nothing resident in any one machine's memory</strong> — everything it needs comes from that <span class="mono">AgentState</span> row in the database. So the real rhythm of handling a message is always a clean three-beat:</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>load</h4><p>Read the <span class="mono">AgentState</span> from the DB by <span class="mono">agent_id</span>: memory blocks, in-window messages, available tools, and model config all together.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>step</h4><p><span class="mono">AgentLoop.load</span> builds the runtime agent from it; <span class="mono">step</span> reads messages, assembles context, calls the model, and runs tools as needed.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>persist</h4><p>New messages, memory edits, and state updates all land in the DB; the moment this beat ends, the in-memory runtime agent can be <strong>thrown away</strong>.</p></div></div>
</div>

<p>Those three beats grant an intensely practical property: <strong>two messages for the same agent can land on two different machines</strong> — because all of the previous step's results are already in the database, and the next step is just another <span class="mono">load</span>. So the Letta server can <strong>scale horizontally</strong> like an ordinary stateless web service: more traffic, more machines, route a request to any of them, all sharing one database behind. That's the payoff of prying "state" out of "process" and stuffing it into <span class="mono">AgentState</span>.</p>

<p>Look back at last lesson's "<strong>load → run a step → save</strong>", and now you know which layer each lands in: <strong>load</strong> and <strong>save</strong> are the job of the <span class="mono">*Manager</span>s in <span class="mono">services/</span>, <strong>run a step</strong> is the job of <span class="mono">agents/</span>, and stringing them together and issuing orders outward is that thin <span class="mono">server/</span> route layer. The three-layer architecture and the "stateful agent" snap together right here.</p>

<div class="card warn">
  <div class="tag">⚠️ Easy to misread</div>
  "Stateless runtime" does not mean the <strong>whole Letta system</strong> is stateless — state sits firmly in the database. What's stateless is only <strong>the runtime that handles a request</strong>: it hoards nothing in memory, rebuilding from <span class="mono">AgentState</span> each time and discarding after. Keep "<strong>stateful data</strong>" and "<strong>stateless runtime</strong>" separate and you won't read the phrase backwards.
</div>

<h3>Read the code along a learning route</h3>
<p>Finally, a "reading route" map. You needn't chew through the whole repo end to end — pick the layer that matches your current goal and cut in there:</p>

<div class="layers">
  <div class="layer l-app"><div class="lh"><span class="badge">Want it running</span><span class="name">server/ · cli/</span></div>
    <div class="ld">Start with <span class="mono">server/rest_api/app.py</span>'s <span class="mono">create_application</span> and the global <span class="mono">SyncServer</span>; the command-line entry is <span class="mono">cli/cli.py</span>.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Understand memory</span><span class="name">schemas/memory.py · services/*</span></div>
    <div class="ld">The <span class="mono">Memory</span> / <span class="mono">Block</span> data contracts, plus how <span class="mono">block_manager</span> / <span class="mono">passage_manager</span> store and fetch.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Understand the loop</span><span class="name">agents/letta_agent_v3.py</span></div>
    <div class="ld"><span class="mono">LettaAgentV3.step</span>: read messages → assemble context → call model → run tools → write back.</div></div>
  <div class="layer l-core"><div class="lh"><span class="badge">Understand storage</span><span class="name">orm/ · server/db.py</span></div>
    <div class="ld"><span class="mono">SqlalchemyBase</span> generic CRUD, and <span class="mono">db_registry.async_session</span> to open a session.</div></div>
</div>

<h2>Dig a little deeper</h2>

<details class="accordion"><summary>Why are routes written so "thin"?</summary><div class="acc-body">
<p><strong>Example:</strong> the real <span class="mono">send_message</span> hands almost everything downstream; you barely see any if/else business logic in the route.</p>
<p><strong>Why this design:</strong> once business is written into a route, it's only usable from the HTTP entrance; put it in a manager and the CLI, background jobs, and tests can all call <strong>the same method</strong>. A thin route also lets "swapping protocols" (say, from a plain response to SSE streaming) touch only the entrance, not the business — the stable core is shielded from entry-layer churn.</p>
<p><strong>Where in source:</strong> route <span class="mono">letta/server/rest_api/routers/v1/agents.py::send_message</span>; business in <span class="mono">services/agent_manager.py</span> and other <span class="mono">*Manager</span>s.</p>
<p><strong>Alternatives:</strong> a "fat controller" writing business straight into the route — fast to start, but the CLI and REST end up with two copies, hard to test and prone to drift. Letta chose thin routes to buy reuse and testability.</p>
</div></details>

<details class="accordion"><summary>Given schemas, why a separate orm too?</summary><div class="acc-body">
<p><strong>Example:</strong> an Agent has both <span class="mono">schemas/agent.py::AgentState</span> (the API model) and <span class="mono">orm/agent.py::Agent</span> (the database model) — looks "redundant".</p>
<p><strong>Why this design:</strong> they care about fundamentally different things. A pydantic schema cares about the "<strong>outward contract</strong>" — field validation, serialization, the <span class="mono">Create</span>/<span class="mono">Update</span>/read trio; the ORM cares about "<strong>inward storage</strong>" — tables, columns, foreign keys, indexes. Separating them lets the API evolve without being chained to the schema, and the database refactor without disturbing the API. The manager converts in between.</p>
<p><strong>Where in source:</strong> pydantic models under <span class="mono">schemas/</span>; models inheriting <span class="mono">SqlalchemyBase</span> under <span class="mono">orm/</span>; conversion methods such as <span class="mono">orm/agent.py::Agent.to_pydantic_async</span>.</p>
<p><strong>Alternatives:</strong> one model only (return the ORM straight as the API) — less code, but the database schema leaks into the API and validation/serialization gets messy. Two models is a common mature-backend trade-off.</p>
</div></details>

<details class="accordion"><summary>What exactly is <span class="mono">SyncServer</span>?</summary><div class="acc-body">
<p><strong>Example:</strong> at startup <span class="mono">app.py</span> news up a single <span class="mono">server = SyncServer(...)</span>, shared by the whole process.</p>
<p><strong>Why this design:</strong> centralizing the creation and ownership of all <span class="mono">*Manager</span>s into one object makes dependencies obvious (e.g. <span class="mono">agent_manager</span> needs <span class="mono">block_manager</span>, injected at construction). Routes get this global <span class="mono">server</span> via dependency injection, then reach a manager via <span class="mono">server.xxx_manager</span> — clean and traceable.</p>
<p><strong>Where in source:</strong> <span class="mono">letta/server/server.py::SyncServer</span> (creates each manager in its constructor); the global instance in <span class="mono">letta/server/rest_api/app.py</span> (<span class="mono">server = SyncServer(...)</span>).</p>
<p><strong>Alternatives:</strong> new up a pile of managers per request — repetitive and wasteful; or scatter singletons across globals — hard to trace. Centralizing into one hub embodies "composition over scattering".</p>
</div></details>

<h2>Where this lesson sits in the big map</h2>
<p>You now hold the guide's <strong>overall structure diagram</strong>: the <span class="mono">letta/</span> directory map, the REST → services → ORM/DB three layers, and the <span class="mono">SyncServer</span> hub stringing them together. Connect it to last lesson — that self-editing <span class="mono">AgentState</span> is exactly the core object these three layers <strong>load, process, and save</strong>. <strong>Next lesson (lesson 3), the lifecycle of a message</strong>, zooms this lesson's <span class="mono">send_message</span> stop into slow motion: in through the route, <span class="mono">AgentLoop.load</span> to load the agent, then inside <span class="mono">step</span> — "read messages → assemble context → call model → run tools → write back" — frame by frame. And later, when Parts 2 and 3 cover tools and memory, you'll instantly locate "which of these three layers it lands in".</p>

<p>Treat this three-layer diagram as your pocket compass: hitting any new module, first ask whether it's <strong>route, service, or storage</strong>, then see how it deals with <span class="mono">AgentState</span> — answer those two and no codebase, however large, will leave you lost.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>Letta's backend is three crisp layers: REST routes (thin) → <span class="mono">services/*Manager</span> (thick) → <span class="mono">orm/SqlalchemyBase</span> + database.</li>
    <li>Business logic lives in the <strong>service layer</strong>'s <span class="mono">*Manager</span>s; routes only resolve the actor and send/receive HTTP.</li>
    <li>The hub is <strong>one</strong> <span class="mono">SyncServer</span> holding all <span class="mono">*Manager</span>s; <span class="mono">app.py</span> has a single global instance.</li>
    <li>Generic ORM: <span class="mono">SqlalchemyBase</span> implements CRUD in one place, and <span class="mono">apply_access_predicate</span> gives every table row-level multi-tenant isolation <strong>by default</strong> (secure by default), with soft delete and pagination built in.</li>
    <li><span class="mono">schemas</span> (outward pydantic contracts) and <span class="mono">orm</span> (inward storage models) are <strong>two models</strong>; the manager converts between them.</li>
    <li><span class="mono">AgentState</span> is the core object crossing all three layers; the agent is a <strong>stateless runtime</strong>, hence it scales horizontally.</li>
  </ul>
</div>
""",
}

LESSON_03 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前两课我们建立了两张地图：<strong>一个 agent 就是数据库里的一条 <span class="mono">AgentState</span></strong>（第 1 课），它住在 <strong>REST → services → ORM/DB 三层</strong>的房子里（第 2 课）。这一课把这两张静态图<strong>动起来</strong>：跟着<strong>一条用户消息</strong>从进门到回信走完全程，看清它依次经过哪些函数、在哪一步组装上下文、在哪一步调模型、又在哪一步落库。这是全书的"<strong>全景数据流</strong>"课——后面第三到第七部分会分别把这条主轴上的某一站放大成特写，而你需要先有这条主轴。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把处理一条消息想象成一张<strong>客服工单</strong>的流转。客户来信（你的消息）先到<strong>前台收单</strong>（路由 <span class="mono">send_message</span>）：核对"你是哪位、找哪个客服"（解析 <span class="mono">actor</span>），再按编号把工单派给对应客服（按 <span class="mono">agent_id</span> 载入 <span class="mono">AgentState</span>）。客服开始<strong>处理</strong>：先翻一翻这位客户的档案与最近往来（组装上下文），再动脑子回复；要是发现"得查个资料、改个备注"，就<strong>起身去仓库跑一趟</strong>（调用工具、改写记忆），回来接着想。一封信可能要<strong>来回跑好几趟仓库</strong>才处理得完。最后把回信寄出（返回响应），并把这次往来<strong>归档</strong>（持久化消息）。前台只管收发、客服只管思考、仓库只管存取——分工清楚，工单才不会乱。
</div>

<h2>端到端：一条消息要走的七步</h2>
<p>先给你一张<strong>全景主轴</strong>。从 HTTP 请求落地，到一个 <span class="mono">LettaResponse</span> 返回，中间大致就是这七步。把它当作本课的"地铁线路图"——后面每一节都是在放大其中的某一站：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>收到请求</h4><p><span class="mono">POST /v1/agents/{id}/messages</span> 命中路由 <span class="mono">send_message</span>，拿到你这次发来的消息。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>解析 actor</h4><p><span class="mono">get_actor_or_default_async</span> 按请求头里的身份定位"<strong>谁、属于哪个组织</strong>"，这决定了后面只能看到自己组织的数据。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>载入存档</h4><p><span class="mono">get_agent_by_id_async</span> 按 <span class="mono">agent_id</span> 取出 <span class="mono">AgentState</span>：记忆块、在窗消息、工具、模型配置一并到位。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>进入循环</h4><p><span class="mono">AgentLoop.load(agent_state, actor)</span> 据此造出运行时 agent（默认是 <span class="mono">LettaAgentV3</span>），再调它的 <span class="mono">step</span>。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>组装 + 调模型</h4><p>把<strong>系统提示</strong>（已把核心记忆编译进去）、在窗消息、工具 schema <strong>组装</strong>成一次请求发给 LLM；组装每轮都做，系统提示本身只在记忆变化时才重编译。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>执行工具 / 改记忆</h4><p>解析模型返回的 <span class="mono">tool_call</span> 并执行；工具可能改写记忆块、查档案，结果作为新消息喂回下一轮。</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>持久化 + 判定</h4><p>新消息落库、更新 <span class="mono">message_ids</span>；<span class="mono">_decide_continuation</span> 判断"再来一轮"还是"收工"，收工就返回 <span class="mono">LettaResponse</span>。</p></div></div>
</div>

<p>这七步里，<strong>第 1–4 步只发生一次</strong>（收单、定身份、取存档、进循环），而 <strong>第 5–7 步是一个会重复的循环体</strong>——这正是本课最容易被误解的地方，我们后面用一整节来讲。先记住主轴的形状：<strong>一次进门，多次内循环，一次出门</strong>。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  整条链路可以浓缩成一句话：<strong>路由把活交给循环，循环在 <span class="mono">max_steps</span> 内反复"调模型 + 执行工具 + 落库"，直到模型不再调工具为止。</strong>路由层（第 2 课的"薄路由"）几乎不含逻辑，它的全部职责就是把请求翻译成"谁、对哪个 agent、说了什么"，然后交给 <span class="mono">AgentLoop</span>。真正的"思考-行动"发生在 <span class="mono">LettaAgentV3.step</span> 里，而每一次"思考-行动"的最小单元是 <span class="mono">_step</span>。读懂"循环 + 单步"这一对关系，你就读懂了 Letta 运行时的心脏。
</div>

<h2>请求怎么穿过这几层</h2>
<p>把第 2 课的三层图叠到这条主轴上，看请求如何自上而下穿层、又把结果带回来。注意：真正"重"的活在 <span class="mono">step</span> / <span class="mono">_step</span>，而不在路由：</p>

<div class="flow">
  <div class="node hl"><div class="nt">路由</div><div class="nd">send_message</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">工厂</div><div class="nd">AgentLoop.load</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">循环</div><div class="nd">step()</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">单步</div><div class="nd">_step()</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">持久化</div><div class="nd">message_manager</div></div>
</div>

<p>第一站 <span class="mono">send_message</span> 短得惊人——它只解析 actor、按 id 取出 agent、把活交给循环。把它简化出来看：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/routers/v1/agents.py</span><span class="ln">send_message（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">send_message</span>(agent_id, request, server, headers):
    actor = <span class="kw">await</span> server.user_manager.<span class="fn">get_actor_or_default_async</span>(headers.actor_id)
    agent = <span class="kw">await</span> server.agent_manager.<span class="fn">get_agent_by_id_async</span>(agent_id, actor)
    loop  = AgentLoop.<span class="fn">load</span>(agent_state=agent, actor=actor)   <span class="cm"># 据 AgentState 造运行时 agent</span>
    <span class="kw">return await</span> loop.<span class="fn">step</span>(request.messages, max_steps=request.max_steps)
</pre></div>

<p>四行就是路由的全部：<strong>定身份 → 取存档 → 造运行时 → 跑循环</strong>。这里藏着一个关键细节——<span class="mono">AgentLoop.load</span> 是个<strong>工厂</strong>：它看 <span class="mono">AgentState</span> 的类型，决定造出哪一种运行时（普通对话是 <span class="mono">LettaAgentV3</span>，开了 sleeptime 的是多 agent 变体）。也就是说，<strong>"用哪套循环"是数据（<span class="mono">AgentState</span>）决定的，不是路由写死的</strong>。</p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  七步各自落在哪：① 路由 <span class="mono">letta/server/rest_api/routers/v1/agents.py::send_message</span>；② <span class="mono">services/user_manager.py::get_actor_or_default_async</span>；③ <span class="mono">services/agent_manager.py::get_agent_by_id_async</span>；④ <span class="mono">agents/agent_loop.py::AgentLoop.load</span> → <span class="mono">agents/letta_agent_v3.py::LettaAgentV3.step</span>；⑤⑥ <span class="mono">LettaAgentV3._step</span>（内部经 <span class="mono">PromptGenerator</span> 把 <span class="mono">Memory.compile()</span> 拼进 system，再调 LLM、执行工具）；⑦ 持久化由 <span class="mono">services/message_manager.py</span> 落库，<span class="mono">_decide_continuation</span> 判定收尾，最终返回 <span class="mono">schemas/letta_response.py::LettaResponse</span>。
</div>

<h2>进了 step：是一个循环，不是一次调用</h2>
<p>很多人对 agent 的想象是"发一条、答一条"——一次消息对应一次模型调用。Letta 不是这样。<span class="mono">step</span> 内部是一个<strong>最多 <span class="mono">max_steps</span> 轮的循环</strong>，每一轮叫一次 <span class="mono">_step</span>：</p>

<div class="flow">
  <div class="node"><div class="nt">_step</div><div class="nd">组装上下文</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">调 LLM</div><div class="nd">一次模型调用</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">执行工具</div><div class="nd">改记忆 / 查档</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">持久化</div><div class="nd">写消息</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">判定</div><div class="nd">_decide_continuation</div></div>
</div>

<p>一次 <span class="mono">_step</span> = <strong>一次 LLM 调用 + 工具执行 + 持久化</strong>。跑完一轮，<span class="mono">_decide_continuation</span> 决定要不要再来一轮。整段循环简化出来是这样：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">step / _step（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">step</span>(self, input_messages, max_steps=<span class="nb">50</span>):
    msgs = in_context_messages + input_messages
    <span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span>(max_steps):              <span class="cm"># 一条消息可能要走好几轮</span>
        <span class="kw">await</span> self.<span class="fn">_step</span>(msgs)              <span class="cm"># 一次 LLM 调用 + 工具执行 + 持久化</span>
        <span class="cm"># _step 内部用 _decide_continuation 设置 self.should_continue：</span>
        <span class="cm">#   这一步调了工具 -&gt; True（继续）；只产出普通消息 -&gt; False（停）</span>
        <span class="kw">if not</span> self.should_continue:
            <span class="kw">break</span>
    <span class="kw">return</span> <span class="fn">LettaResponse</span>(messages=..., stop_reason=..., usage=...)
</pre></div>

<p>看 <span class="mono">for i in range(max_steps)</span> 这一行——它就是"<strong>一条消息≠一次模型调用</strong>"的根源。只要模型在这一轮里<strong>调了工具</strong>（比如 <span class="mono">core_memory_append</span> 改记忆、或 <span class="mono">web_search</span> 查资料），循环就会把工具结果喂回去、<strong>再调一次模型</strong>；直到某一轮模型<strong>只回了一句普通话、没有再调工具</strong>，循环才停。<span class="mono">max_steps</span>（默认 50）是一道安全闸，防止无限打转。</p>

<p>循环停下来时，会带上一个 <span class="mono">stop_reason</span> 说明"为什么停"：模型正常说完话、没再调工具，是 <span class="mono">end_turn</span>；撞到步数上限，是 <span class="mono">max_steps</span>；被工具规则判定调用了某个"终止工具"，是 <span class="mono">tool_rule</span>。另外，每一轮 <span class="mono">_step</span> 在调模型前其实还悄悄做了两件小事：先<strong>刷新一遍消息</strong>（把上一轮的内部思考擦掉，既省 token，又尽量保住 prefix cache），再算出<strong>这一轮有哪些可用工具、要不要强制调用工具</strong>。这些细节你现在不必记牢，但知道"单步里不只有一次裸调用"，会让后面的课好懂很多。</p>

<div class="card warn">
  <div class="tag">⚠️ 容易误解</div>
  <strong>一条消息 ≠ 一次模型调用。</strong>一次 <span class="mono">send_message</span> 背后，可能藏着 <strong>2 次、5 次、甚至几十次</strong> LLM 调用——每一次工具调用都会触发"再想一轮"。所以：响应可能比你以为的慢（多轮往返），也更贵（多次计费）；调试时该看的是"<strong>这一轮里模型调了什么工具</strong>"，而不是"这条消息为什么只回了一次"。循环的上限是 <span class="mono">max_steps</span>，到顶就会以 <span class="mono">max_steps</span> 这个 stop reason 收尾。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  这一课的"啊哈"有两层，都藏在那个简单到反直觉的循环里：<br><br>
  ① <strong>继续规则简单到家了。</strong>"要不要再想一轮"这种听起来很玄的判断，<span class="mono">_decide_continuation</span> 的核心其实就一句话——<strong>"这一步调了工具就继续，只产出普通消息就停"</strong>。源码注释写得明明白白：<em>Did not call a tool? Loop ends. Called a tool? Loop continues.</em> 相比原始 MemGPT 要靠模型自己输出一个 <span class="mono">heartbeat</span> 标志来"请求续命"，v3 直接用"<strong>这一步有没有工具调用</strong>"这个客观信号来驱动循环——少了一个模型要学会、且可能学错的约定，鲁棒性大增。<br>
  ② <strong>运行时是无状态的。</strong>每次请求都从 <span class="mono">AgentState</span> <strong>重新造一个</strong>运行时 agent（<span class="mono">AgentLoop.load</span>），跑完即弃；两步之间，agent 的一切都在库里，内存里不留东西。于是"一条消息触发多轮"也好、"换台机器接着跑"也好，都成立——因为<strong>状态在数据，不在进程</strong>。<br><br>
  一句话：<strong>用"是否调用工具"这个最朴素的信号，驱动一个无状态的循环</strong>——既好懂、又好扩展、还难写错。
</div>

<p>把这两点合起来看一个场景：你发一条消息，agent 在第 1 轮调了工具、第 2 轮才回话——这两轮<strong>完全可以落在两台不同的机器上</strong>。第 1 轮结束时，新消息与记忆改动都已写回数据库；第 2 轮无非是另一台机器再 <span class="mono">load</span> 一次 <span class="mono">AgentState</span>、接着跑 <span class="mono">_step</span>。正因为"继续与否"只看<strong>这一步有没有调用工具</strong>这个客观事实（结果也随即落库），而"状态"又全在数据库里，整套循环才能既<strong>横跨多轮</strong>、又<strong>横跨多机</strong>。这是第 2 课"无状态运行时可水平扩展"在数据流层面的兑现。</p>

<h2>上下文是怎么拼出来的</h2>
<p>第 5 步"组装上下文"值得单独拆开。每一轮 <span class="mono">_step</span> 调模型前，都要现拼出一份完整的输入。它由<strong>三种来源</strong>合成：</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">system 消息</span><span class="name">Memory.compile() + memory_metadata</span></div>
    <div class="ld">把<strong>核心记忆块</strong>（persona / human 等）编译成文本，拼进第 0 条 system 消息；再附上一段元信息（recall 里有多少条、archival 多大）。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">在窗消息</span><span class="name">in-context messages</span></div>
    <div class="ld">当前留在上下文窗口里的最近对话（来自 recall 记忆）：上一轮的工具结果、你这次的新消息，都在这里。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">工具 schema</span><span class="name">tools / tool_rules</span></div>
    <div class="ld">这个 agent 能调的工具签名（名字、参数），让模型知道"我能干什么"，外加调用顺序的约束。</div></div>
</div>

<p>这里要分清两个词：<strong>recall（召回记忆）</strong>是这个 agent 全部历史消息的存档，可能成千上万条；<strong>在窗消息</strong>只是其中"<strong>当前还留在上下文窗口里</strong>"的最近一小段。模型每一轮看到的，永远只是后者——更早的对话并没有消失，只是被换出了窗口，需要时再靠工具去 recall 里捞回来。这正是"上下文有限"这个根本约束在数据流里的样子：<strong>窗口是会满的，所以必须有进、有出</strong>。</p>

<p>这三块<strong>拼成一次 LLM 请求</strong>，大致是下面这个形状——第 0 条永远是编译好的 system，后面跟着在窗消息，工具 schema 作为单独的字段一并发出：</p>

<div class="cellgroup">
  <div class="cg-cap">一次 LLM 请求的<b>消息序列</b>（外加工具 schema）：</div>
  <div class="cells">
    <span class="cell hl">system<br>(记忆编译)</span>
    <span class="cell">user</span>
    <span class="cell">assistant<br>(tool_call)</span>
    <span class="cell">tool<br>(结果)</span>
    <span class="cell">user<br>(本次)</span>
    <span class="cell q">+ tools schema</span>
  </div>
</div>

<p>关键在<strong>第 0 条 system</strong>。它不是写死的——而是每次由 <span class="mono">Memory.compile()</span> 把当前记忆块<strong>重新渲染</strong>出来，经 <span class="mono">PromptGenerator</span> 拼进系统提示。这正是第 1 课"自我编辑记忆 = 改写自己的系统提示"在数据流上的落点：agent 用工具改了记忆块，下一轮 <span class="mono">_step</span> 一组装，新的记忆就自动出现在 system 里了。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/prompts/prompt_generator.py</span><span class="ln">compile_system_message_async（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">compile_system_message_async</span>(system_prompt, in_context_memory, ...):
    <span class="cm"># 把核心记忆块渲染成文本（persona / human 等）</span>
    memory_text = in_context_memory.<span class="fn">compile</span>(tool_usage_rules=..., sources=...)
    <span class="cm"># 再把这段记忆 + 元信息塞进 system 提示模板</span>
    <span class="kw">return</span> PromptGenerator.<span class="fn">get_system_message_from_compiled_memory</span>(
        system_prompt=system_prompt, memory_with_sources=memory_text, ...)
</pre></div>

<p>这里还有个性能上的讲究：第 0 条 system 一旦编译好，<strong>只要核心记忆没变就尽量不去动它</strong>。因为大多数 provider 会对"<strong>提示前缀</strong>"做缓存（prefix cache）——system 放在最前面且保持稳定，后续每一轮就能少算一大截，又快又省。只有当记忆真被改写、或发生了压缩，才用 <span class="mono">rebuild_system_prompt_async</span> 把第 0 条重编译一次。<strong>"稳定的前缀 + 变化的尾巴"</strong>，是这套上下文设计里很关键的一条性能直觉。</p>

<h3>上下文快满了怎么办：压缩</h3>
<p>对话越来越长，在窗消息迟早会把上下文窗口顶满。Letta 的应对是<strong>压缩（compaction）</strong>：当 token 数逼近阈值，就把一段较旧的对话<strong>总结</strong>成一条 summary 消息，替换掉原始的一长串，腾出空间继续。整个过程沿着对话时间线发生：</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">早期</span><span class="tslot span">很久以前的大段对话</span></div>
  <div class="lane"><span class="lane-label">逼近阈值</span><span class="tslot">msg</span><span class="tslot">msg</span><span class="tslot">msg</span><span class="tslot now">tokens 接近上限</span></div>
  <div class="lane"><span class="lane-label">压缩后</span><span class="tslot now">summary（总结）</span><span class="tslot">最近 msg</span><span class="tslot">本次新消息</span></div>
</div>

<p>压缩之后，因为消息序列变了，系统提示也要重新编译一遍（<span class="mono">rebuild_system_prompt_async</span>），保证下一轮上下文一致。这块的细节（什么时候触发、怎么总结、summary 长什么样）留到<strong>第 12 课</strong>专门讲，这里你只需要知道：<strong>主轴的第 5 步里，藏着一个"窗口快满就自动腾地方"的机制</strong>。</p>

<h2>再挖深一点</h2>

<details class="accordion"><summary>为什么一条消息会触发好几次模型调用？</summary><div class="acc-body">
<p><strong>示例：</strong>你说"帮我把刚才提到的生日记下来，再查下今天天气"。agent 可能：第 1 轮调 <span class="mono">core_memory_append</span> 记生日 → 第 2 轮调 <span class="mono">web_search</span> 查天气 → 第 3 轮才回你一句汇总。三轮，三次 LLM 调用。</p>
<p><strong>为什么这样设计：</strong>因为"调工具"和"回话"必须分开。模型发起工具调用的那一刻，它还<strong>没看到工具结果</strong>；只有把结果喂回去、<strong>再调一次</strong>，它才能基于结果继续。于是"想一步、做一步、再想一步"天然就是个循环。<span class="mono">_decide_continuation</span> 用"这一步有没有工具调用"来决定要不要继续——有就继续、没有就停。</p>
<p><strong>源码在哪：</strong>循环在 <span class="mono">letta/agents/letta_agent_v3.py::LettaAgentV3.step</span>，单步在 <span class="mono">_step</span>，判定在 <span class="mono">_decide_continuation</span>。</p>
<p><strong>还有什么替代：</strong>原始 MemGPT 靠模型输出一个 <span class="mono">heartbeat</span> 布尔来"请求继续"——多一个模型要学会的约定，也更容易学错。v3 改用"有没有工具调用"这个客观信号，简单且稳。</p>
</div></details>

<details class="accordion"><summary>上下文窗口满了会怎样？</summary><div class="acc-body">
<p><strong>示例：</strong>一个聊了几百轮的 agent，在窗消息早超过模型能吃下的 token 了，却还能继续对话。</p>
<p><strong>为什么这样设计：</strong>因为有压缩。token 逼近阈值时，把旧对话总结成一条 summary 顶上去，既保住"大意"，又把"逐字长文"换出窗口——正是第 1 课那个"上下文=RAM、外部记忆=磁盘、自己换页"的类比在循环里的体现。压缩后系统提示会用 <span class="mono">rebuild_system_prompt_async</span> 重编译一次。</p>
<p><strong>源码在哪：</strong>触发阈值与压缩逻辑在 <span class="mono">letta/agents/letta_agent_v3.py</span> 的单步流程里（配合 summarizer）；系统提示重建在 <span class="mono">services/agent_manager.py::rebuild_system_prompt_async</span>。完整机制见<strong>第 12 课</strong>。</p>
<p><strong>还有什么替代：</strong>简单粗暴地"丢掉最早的消息"——省事，但会真的失忆；或无限堆上下文——又慢又贵还可能超限。总结式压缩是质量与成本的折中。</p>
</div></details>

<details class="accordion"><summary>流式（stream）和阻塞（step）有什么区别？</summary><div class="acc-body">
<p><strong>示例：</strong>同一条消息，网页里你能看到字一个个蹦出来（流式）；而脚本里 <span class="mono">client.agents.messages.create(...)</span> 往往是等全部算完、一次性拿到结果（阻塞）。</p>
<p><strong>为什么这样设计：</strong>两种入口服务两种需求。阻塞模式（<span class="mono">step</span>）逻辑最简单、最好测，一次返回完整的 <span class="mono">LettaResponse</span>；流式模式（<span class="mono">stream</span> + SSE）边算边推，体验更跟手。但它们<strong>共用同一套循环</strong>——内部都走 <span class="mono">_step</span>，只是"怎么把中间结果交出去"不同。</p>
<p><strong>源码在哪：</strong>阻塞 <span class="mono">LettaAgentV3.step</span>；流式 <span class="mono">LettaAgentV3.stream</span>；路由 <span class="mono">send_message</span> 按请求的 <span class="mono">streaming</span> 字段二选一（流式走 SSE）。</p>
<p><strong>还有什么替代：</strong>只做阻塞——实现简单但长回答体验差；只做流式——所有调用方都得处理事件流，脚本场景反而麻烦。两者都留、共用内核，是常见做法。</p>
</div></details>

<h2>这一课在整张大图的哪里</h2>
<p>现在你手里有了全书的<strong>第三张、也是最关键的一张图</strong>：一条消息的端到端数据流。把三张图叠起来——一个 agent 是一条 <span class="mono">AgentState</span>（第 1 课），它住在三层架构里（第 2 课），而处理一条消息，就是让这条 <span class="mono">AgentState</span> 被<strong>取出 → 组装上下文 → 循环"调模型 + 执行工具" → 写回</strong>（本课）。第一部分"宏观全景"到此收尾：你已经能在脑子里完整地"放"一遍一条消息的旅程了。</p>

<p>接下来的每个部分，都是<strong>把这条主轴上的某一站按下慢放</strong>：讲<strong>记忆</strong>的部分会放大第 5 步——核心记忆怎么编译进 system、recall / archival 怎么分层、压缩怎么发生；讲<strong>工具</strong>的部分会放大第 6 步——函数怎么变成 schema、<span class="mono">tool_call</span> 怎么解析与执行、<span class="mono">tool_rules</span> 怎么约束顺序；讲 <strong>provider</strong> 的部分会放大"调 LLM"那一下——各家模型的差异怎么被 <span class="mono">llm_api</span> 抹平；讲<strong>持久化</strong>的部分会放大第 7 步——消息与状态怎么落库。每读到一个新细节，都回到这张主轴上问一句："<strong>它发生在七步里的哪一步？</strong>"——只要答得上来，再深的细节都不会让你迷路。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>一条消息的主轴：<span class="mono">POST</span> → <span class="mono">send_message</span> → 解析 <span class="mono">actor</span> → 载入 <span class="mono">AgentState</span> → <span class="mono">AgentLoop.load</span> → <span class="mono">step</span> 循环 → 工具/记忆 → 持久化 → <span class="mono">LettaResponse</span>。</li>
    <li>路由很薄：只做"定身份 → 取存档 → 造运行时 → 跑循环"，业务都在 <span class="mono">step</span> / <span class="mono">_step</span>。</li>
    <li><strong>一条消息 ≠ 一次模型调用</strong>：<span class="mono">step</span> 是个最多 <span class="mono">max_steps</span>（默认 50）轮的循环，一次 <span class="mono">_step</span> = 一次 LLM 调用 + 工具执行 + 持久化。</li>
    <li>循环的继续规则极简：<span class="mono">_decide_continuation</span> —— <strong>调了工具就继续，只产出普通消息就停</strong>（比 MemGPT 的 heartbeat 大幅简化）。</li>
    <li>上下文每轮现拼：<span class="mono">Memory.compile()</span> 把核心记忆编译进第 0 条 system（经 <span class="mono">PromptGenerator</span>），再加在窗消息、加工具 schema。</li>
    <li>运行时<strong>无状态</strong>：每次从 <span class="mono">AgentState</span> 重建、用完即弃；两步之间的状态都在库里。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
The last two lessons drew two maps: <strong>an agent is just one <span class="mono">AgentState</span> row in a database</strong> (Lesson 1), and it lives in a house with <strong>three layers — REST → services → ORM/DB</strong> (Lesson 2). This lesson sets those static maps <strong>in motion</strong>: we follow <strong>one user message</strong> from the front door to the reply, seeing exactly which functions it passes through, where the context is assembled, where the model is called, and where things are written to the database. This is the guide's "<strong>panoramic data-flow</strong>" lesson — Parts 3 through 7 each zoom one stop on this spine into close-up, so you need the spine first.
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture handling one message as a <strong>support ticket</strong> moving through an office. The customer's letter (your message) first hits the <strong>front desk</strong> (the route <span class="mono">send_message</span>): it verifies "who are you, which agent are you talking to" (resolve the <span class="mono">actor</span>), then routes the ticket to the right agent by number (load <span class="mono">AgentState</span> by <span class="mono">agent_id</span>). The agent starts <strong>working</strong>: first it flips through this customer's file and recent exchanges (assemble context), then thinks up a reply; if it realizes "I need to look something up, or update a note," it <strong>walks to the warehouse</strong> (call a tool, edit memory) and comes back to keep thinking. One letter may require <strong>several trips to the warehouse</strong> before it's done. Finally the reply is mailed out (return a response) and the exchange is <strong>filed away</strong> (persist messages). Front desk only sends/receives, the agent only thinks, the warehouse only stores — clear roles keep the ticket from descending into chaos.
</div>

<h2>End to end: the seven stops a message makes</h2>
<p>Here's the <strong>panoramic spine</strong> first. From an HTTP request landing to a <span class="mono">LettaResponse</span> coming back, it's roughly these seven stops. Treat it as the lesson's "subway map" — every later section magnifies one of these stops:</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Receive the request</h4><p><span class="mono">POST /v1/agents/{id}/messages</span> hits the route <span class="mono">send_message</span>, which takes the message you just sent.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Resolve the actor</h4><p><span class="mono">get_actor_or_default_async</span> locates "<strong>who, and which organization</strong>" from the request headers — this decides that later it can only see its own org's data.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Load the save file</h4><p><span class="mono">get_agent_by_id_async</span> fetches the <span class="mono">AgentState</span> by <span class="mono">agent_id</span>: memory blocks, in-context messages, tools, and model config all arrive together.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Enter the loop</h4><p><span class="mono">AgentLoop.load(agent_state, actor)</span> builds a runtime agent from it (by default <span class="mono">LettaAgentV3</span>), then calls its <span class="mono">step</span>.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Assemble + call the model</h4><p><strong>Assemble</strong> the request - the system message (with core memory already compiled in), in-context messages and tool schemas - and send it to the LLM; the assembly runs every <span class="mono">_step</span>, while the system message itself is only recompiled when memory changes.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Run tools / edit memory</h4><p>Parse the model's <span class="mono">tool_call</span> and execute it; a tool may rewrite a memory block or look something up, and its result is fed back as a new message for the next round.</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>Persist + decide</h4><p>New messages are written and <span class="mono">message_ids</span> updated; <span class="mono">_decide_continuation</span> judges "another round" vs "wrap up," and on wrap-up returns a <span class="mono">LettaResponse</span>.</p></div></div>
</div>

<p>Of these seven, <strong>steps 1–4 happen once</strong> (intake, identify, load, enter), while <strong>steps 5–7 are a loop body that repeats</strong> — which is exactly the most misunderstood part of this lesson, covered in its own section below. For now, remember the shape of the spine: <strong>one entry, many inner loops, one exit</strong>.</p>

<div class="card macro">
  <div class="tag">🌍 The big picture</div>
  The whole chain boils down to one sentence: <strong>the route hands work to the loop, and the loop repeats "call model + run tools + persist" within <span class="mono">max_steps</span>, until the model stops calling tools.</strong> The route layer (Lesson 2's "thin route") holds almost no logic; its entire job is to translate the request into "who, to which agent, said what," then hand off to <span class="mono">AgentLoop</span>. The real "think-act" happens inside <span class="mono">LettaAgentV3.step</span>, and the smallest unit of each "think-act" is <span class="mono">_step</span>. Understand the pair "loop + single step" and you've understood the heart of Letta's runtime.
</div>

<h2>How the request crosses the layers</h2>
<p>Overlay Lesson 2's three-layer map onto this spine and watch the request cross down and bring a result back up. Notice: the truly "heavy" work is in <span class="mono">step</span> / <span class="mono">_step</span>, not in the route:</p>

<div class="flow">
  <div class="node hl"><div class="nt">Route</div><div class="nd">send_message</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Factory</div><div class="nd">AgentLoop.load</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Loop</div><div class="nd">step()</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Single step</div><div class="nd">_step()</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Persist</div><div class="nd">message_manager</div></div>
</div>

<p>The first stop, <span class="mono">send_message</span>, is shockingly short — it only resolves the actor, fetches the agent by id, and hands work to the loop. Simplified:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/routers/v1/agents.py</span><span class="ln">send_message (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">send_message</span>(agent_id, request, server, headers):
    actor = <span class="kw">await</span> server.user_manager.<span class="fn">get_actor_or_default_async</span>(headers.actor_id)
    agent = <span class="kw">await</span> server.agent_manager.<span class="fn">get_agent_by_id_async</span>(agent_id, actor)
    loop  = AgentLoop.<span class="fn">load</span>(agent_state=agent, actor=actor)   <span class="cm"># build runtime agent from AgentState</span>
    <span class="kw">return await</span> loop.<span class="fn">step</span>(request.messages, max_steps=request.max_steps)
</pre></div>

<p>Four lines are the whole route: <strong>identify → load save → build runtime → run loop</strong>. There's a key detail here — <span class="mono">AgentLoop.load</span> is a <strong>factory</strong>: it looks at the type of <span class="mono">AgentState</span> and decides which runtime to build (a normal conversation is <span class="mono">LettaAgentV3</span>; a sleeptime-enabled one is a multi-agent variant). In other words, <strong>"which loop to use" is decided by the data (<span class="mono">AgentState</span>), not hard-coded in the route</strong>.</p>

<div class="card detail">
  <div class="tag">🔬 Source mapping</div>
  Where each of the seven stops lives: ① route <span class="mono">letta/server/rest_api/routers/v1/agents.py::send_message</span>; ② <span class="mono">services/user_manager.py::get_actor_or_default_async</span>; ③ <span class="mono">services/agent_manager.py::get_agent_by_id_async</span>; ④ <span class="mono">agents/agent_loop.py::AgentLoop.load</span> → <span class="mono">agents/letta_agent_v3.py::LettaAgentV3.step</span>; ⑤⑥ <span class="mono">LettaAgentV3._step</span> (internally splices <span class="mono">Memory.compile()</span> into the system via <span class="mono">PromptGenerator</span>, then calls the LLM and runs tools); ⑦ persistence via <span class="mono">services/message_manager.py</span>, <span class="mono">_decide_continuation</span> wraps up, and finally a <span class="mono">schemas/letta_response.py::LettaResponse</span> is returned.
</div>

<h2>Inside step: it's a loop, not a single call</h2>
<p>Many people imagine an agent as "send one, get one" — one message equals one model call. Letta isn't like that. Inside <span class="mono">step</span> is a <strong>loop of up to <span class="mono">max_steps</span> rounds</strong>, and each round is one <span class="mono">_step</span>:</p>

<div class="flow">
  <div class="node"><div class="nt">_step</div><div class="nd">assemble context</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">call LLM</div><div class="nd">one model call</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">run tools</div><div class="nd">edit memory / look up</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">persist</div><div class="nd">write messages</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">decide</div><div class="nd">_decide_continuation</div></div>
</div>

<p>One <span class="mono">_step</span> = <strong>one LLM call + tool execution + persistence</strong>. After a round, <span class="mono">_decide_continuation</span> decides whether to run another. The whole loop, simplified:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">step / _step (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">step</span>(self, input_messages, max_steps=<span class="nb">50</span>):
    msgs = in_context_messages + input_messages
    <span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span>(max_steps):              <span class="cm"># one message may need several rounds</span>
        <span class="kw">await</span> self.<span class="fn">_step</span>(msgs)              <span class="cm"># one LLM call + tool execution + persistence</span>
        <span class="cm"># _step sets self.should_continue via _decide_continuation:</span>
        <span class="cm">#   this step called a tool -&gt; True (continue); only a plain message -&gt; False (stop)</span>
        <span class="kw">if not</span> self.should_continue:
            <span class="kw">break</span>
    <span class="kw">return</span> <span class="fn">LettaResponse</span>(messages=..., stop_reason=..., usage=...)
</pre></div>

<p>Look at the line <span class="mono">for i in range(max_steps)</span> — that's the root of "<strong>one message ≠ one model call</strong>." As long as the model <strong>called a tool</strong> this round (e.g. <span class="mono">core_memory_append</span> to edit memory, or <span class="mono">web_search</span> to look something up), the loop feeds the tool result back and <strong>calls the model again</strong>; only when some round produces <strong>just a plain message with no tool call</strong> does the loop stop. <span class="mono">max_steps</span> (default 50) is a safety stop against spinning forever.</p>

<p>When the loop stops it carries a <span class="mono">stop_reason</span> explaining "why it stopped": the model said its piece with no further tool call, <span class="mono">end_turn</span>; it hit the step ceiling, <span class="mono">max_steps</span>; a tool rule flagged that it called a "terminal tool," <span class="mono">tool_rule</span>. Also, before calling the model each <span class="mono">_step</span> quietly does two small things: it <strong>refreshes the messages</strong> (scrubbing the previous round's inner thoughts to save tokens and preserve the prefix cache), and it computes <strong>which tools are available this round and whether a tool call must be forced</strong>. You needn't memorize these now, but knowing "a single step is more than one naked call" makes later lessons much easier.</p>

<div class="card warn">
  <div class="tag">⚠️ Common misconception</div>
  <strong>One message ≠ one model call.</strong> Behind a single <span class="mono">send_message</span> there may be <strong>2, 5, or even dozens</strong> of LLM calls — every tool call triggers "think one more round." So: a response may be slower than you expect (multiple round-trips) and more expensive (billed multiple times); when debugging, look at "<strong>what tool did the model call this round</strong>," not "why did this message only reply once." The loop's ceiling is <span class="mono">max_steps</span>, and hitting it wraps up with a <span class="mono">max_steps</span> stop reason.
</div>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  This lesson's "aha" has two layers, both hidden in that counter-intuitively simple loop:<br><br>
  ① <strong>The continuation rule is dead simple.</strong> "Should I think another round?" sounds mysterious, but the core of <span class="mono">_decide_continuation</span> is one sentence — <strong>"called a tool this step → keep going; produced only a plain message → stop."</strong> The source comment says it plainly: <em>Did not call a tool? Loop ends. Called a tool? Loop continues.</em> Compared with original MemGPT, which relied on the model emitting a <span class="mono">heartbeat</span> flag to "request another life," v3 drives the loop directly off the <strong>objective signal of whether a tool was called</strong> — one fewer convention the model must learn (and could get wrong), which greatly improves robustness.<br>
  ② <strong>The runtime is stateless.</strong> Each request <strong>rebuilds</strong> a runtime agent from <span class="mono">AgentState</span> (<span class="mono">AgentLoop.load</span>) and discards it when done; between steps, everything about the agent lives in the database, nothing in memory. So both "one message triggers many rounds" and "another machine picks up the work" hold — because <strong>state is in the data, not the process</strong>.<br><br>
  In one line: <strong>drive a stateless loop off the most primitive signal possible — whether a tool was called</strong> — simple to grasp, easy to scale, and hard to get wrong.
</div>

<p>Put the two together in one scenario: you send a message, the agent calls a tool in round 1 and only replies in round 2 — those two rounds <strong>can land on two different machines</strong>. When round 1 ends, the new messages and memory edits are already written to the database; round 2 is just another machine doing <span class="mono">load</span> on the <span class="mono">AgentState</span> again and continuing with <span class="mono">_step</span>. Precisely because "continue or not" depends only on an objective fact - did this step call a tool (which is then persisted) - and "state" lives entirely in the database, the loop can span <strong>both many rounds</strong> and <strong>many machines</strong>. This is Lesson 2's "stateless runtime scales horizontally," cashed out at the data-flow level.</p>

<h2>How the context gets assembled</h2>
<p>Step 5, "assemble context," deserves its own dissection. Before each <span class="mono">_step</span> calls the model, it freshly assembles a complete input, synthesized from <strong>three sources</strong>:</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">system message</span><span class="name">Memory.compile() + memory_metadata</span></div>
    <div class="ld">Compile the <strong>core memory blocks</strong> (persona / human, etc.) into text and splice it into message #0, the system message; then append a metadata note (how many in recall, how big archival is).</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">in-context messages</span><span class="name">in-context messages</span></div>
    <div class="ld">The recent conversation currently kept in the context window (from recall memory): last round's tool result and your new message are both here.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">tool schemas</span><span class="name">tools / tool_rules</span></div>
    <div class="ld">The tool signatures (names, parameters) this agent can call, so the model knows "what I can do," plus ordering constraints.</div></div>
</div>

<p>Distinguish two words here: <strong>recall (recall memory)</strong> is the archive of this agent's entire message history, possibly thousands of rows; <strong>in-context messages</strong> are only the recent slice that's "<strong>still in the context window right now</strong>." What the model sees each round is always the latter — earlier conversation hasn't vanished, it's just been paged out of the window, to be fished back from recall by a tool when needed. This is exactly what "finite context" looks like in the data flow: <strong>the window fills up, so there must be an in and an out</strong>.</p>

<p>These three blocks <strong>assemble into one LLM request</strong>, roughly this shape — message #0 is always the compiled system, followed by in-context messages, with tool schemas sent along as a separate field:</p>

<div class="cellgroup">
  <div class="cg-cap">The <b>message sequence</b> of one LLM request (plus tool schemas):</div>
  <div class="cells">
    <span class="cell hl">system<br>(memory)</span>
    <span class="cell">user</span>
    <span class="cell">assistant<br>(tool_call)</span>
    <span class="cell">tool<br>(result)</span>
    <span class="cell">user<br>(this)</span>
    <span class="cell q">+ tools schema</span>
  </div>
</div>

<p>The key is <strong>message #0, the system</strong>. It isn't hard-coded — each time, <span class="mono">Memory.compile()</span> <strong>re-renders</strong> the current memory blocks, and <span class="mono">PromptGenerator</span> splices them into the system prompt. This is exactly where Lesson 1's "self-editing memory = rewriting your own system prompt" lands in the data flow: the agent edits a memory block with a tool, and the moment the next <span class="mono">_step</span> assembles context, the new memory automatically shows up in the system.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/prompts/prompt_generator.py</span><span class="ln">compile_system_message_async (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">compile_system_message_async</span>(system_prompt, in_context_memory, ...):
    <span class="cm"># render core memory blocks into text (persona / human, etc.)</span>
    memory_text = in_context_memory.<span class="fn">compile</span>(tool_usage_rules=..., sources=...)
    <span class="cm"># then splice that memory + metadata into the system prompt template</span>
    <span class="kw">return</span> PromptGenerator.<span class="fn">get_system_message_from_compiled_memory</span>(
        system_prompt=system_prompt, memory_with_sources=memory_text, ...)
</pre></div>

<p>There's a performance angle too: once message #0, the system, is compiled, <strong>it's kept untouched as long as core memory doesn't change</strong>. Because most providers cache the "<strong>prompt prefix</strong>" (prefix cache) — putting the system first and keeping it stable lets every later round skip a big chunk of compute, faster and cheaper. Only when memory is actually rewritten, or a compaction happens, is message #0 recompiled via <span class="mono">rebuild_system_prompt_async</span>. <strong>"Stable prefix + changing tail"</strong> is a key performance intuition behind this context design.</p>

<h3>What if the context is nearly full: compaction</h3>
<p>As a conversation grows, in-context messages will eventually overflow the context window. Letta's answer is <strong>compaction</strong>: when token count nears a threshold, an older stretch of conversation is <strong>summarized</strong> into a single summary message that replaces the long original, freeing room to continue. The whole thing happens along the conversation timeline:</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">early</span><span class="tslot span">a long stretch from way back</span></div>
  <div class="lane"><span class="lane-label">near limit</span><span class="tslot">msg</span><span class="tslot">msg</span><span class="tslot">msg</span><span class="tslot now">tokens near ceiling</span></div>
  <div class="lane"><span class="lane-label">after compaction</span><span class="tslot now">summary</span><span class="tslot">recent msg</span><span class="tslot">this new msg</span></div>
</div>

<p>After compaction, because the message sequence changed, the system prompt is recompiled (<span class="mono">rebuild_system_prompt_async</span>) to keep the next round's context consistent. The details (when it triggers, how it summarizes, what the summary looks like) are saved for <strong>Lesson 12</strong>; here you only need to know: <strong>hidden inside step 5 of the spine is a "free up room when the window is nearly full" mechanism</strong>.</p>

<h2>Digging a little deeper</h2>

<details class="accordion"><summary>Why does one message trigger several model calls?</summary><div class="acc-body">
<p><strong>Example:</strong> you say "save the birthday I just mentioned, then check today's weather." The agent might: round 1 call <span class="mono">core_memory_append</span> to save the birthday → round 2 call <span class="mono">web_search</span> for the weather → round 3 finally reply with a summary. Three rounds, three LLM calls.</p>
<p><strong>Why it's designed this way:</strong> because "call a tool" and "reply" must be separate. The moment the model issues a tool call, it <strong>hasn't seen the tool result yet</strong>; only by feeding the result back and <strong>calling again</strong> can it continue based on the result. So "think a step, act a step, think again" is naturally a loop. <span class="mono">_decide_continuation</span> uses "did this step call a tool" to decide whether to continue — yes keeps going, no stops.</p>
<p><strong>Where in the source:</strong> the loop is in <span class="mono">letta/agents/letta_agent_v3.py::LettaAgentV3.step</span>, the single step in <span class="mono">_step</span>, the decision in <span class="mono">_decide_continuation</span>.</p>
<p><strong>Alternatives:</strong> original MemGPT relied on the model emitting a <span class="mono">heartbeat</span> boolean to "request continuation" — one more convention to learn and to get wrong. v3 switched to the objective signal of "was a tool called," simpler and steadier.</p>
</div></details>

<details class="accordion"><summary>What happens when the context window fills up?</summary><div class="acc-body">
<p><strong>Example:</strong> an agent that's chatted hundreds of rounds has in-context messages well past what the model can swallow, yet it keeps conversing.</p>
<p><strong>Why it's designed this way:</strong> because of compaction. As tokens near the threshold, old conversation is summarized into one summary placed on top — keeping the "gist" while paging the "verbatim long text" out of the window. This is exactly Lesson 1's "context = RAM, external memory = disk, page yourself" analogy showing up inside the loop. After compaction the system prompt is recompiled once via <span class="mono">rebuild_system_prompt_async</span>.</p>
<p><strong>Where in the source:</strong> the trigger threshold and compaction logic live in the single-step flow of <span class="mono">letta/agents/letta_agent_v3.py</span> (with a summarizer); system-prompt rebuild is in <span class="mono">services/agent_manager.py::rebuild_system_prompt_async</span>. Full mechanism in <strong>Lesson 12</strong>.</p>
<p><strong>Alternatives:</strong> bluntly "drop the oldest messages" — easy, but it genuinely forgets; or pile up context forever — slow, expensive, and may exceed limits. Summary-based compaction is the quality/cost compromise.</p>
</div></details>

<details class="accordion"><summary>What's the difference between streaming (stream) and blocking (step)?</summary><div class="acc-body">
<p><strong>Example:</strong> for the same message, in a web UI you see characters pop out one by one (streaming); in a script, <span class="mono">client.agents.messages.create(...)</span> usually waits for everything to finish and returns the result at once (blocking).</p>
<p><strong>Why it's designed this way:</strong> two entrances serve two needs. Blocking mode (<span class="mono">step</span>) has the simplest, most testable logic and returns a complete <span class="mono">LettaResponse</span> at once; streaming mode (<span class="mono">stream</span> + SSE) pushes as it computes for a more responsive feel. But they <strong>share the same loop</strong> — both go through <span class="mono">_step</span> internally; only "how intermediate results are handed out" differs.</p>
<p><strong>Where in the source:</strong> blocking <span class="mono">LettaAgentV3.step</span>; streaming <span class="mono">LettaAgentV3.stream</span>; the route <span class="mono">send_message</span> picks one based on the request's <span class="mono">streaming</span> field (streaming goes SSE).</p>
<p><strong>Alternatives:</strong> blocking only — simple to build but poor for long answers; streaming only — every caller must handle an event stream, which is awkward for scripts. Keeping both and sharing the core is the common practice.</p>
</div></details>

<h2>Where this lesson sits in the big map</h2>
<p>You now hold the guide's <strong>third — and most important — map</strong>: the end-to-end data flow of one message. Stack the three maps: an agent is one <span class="mono">AgentState</span> (Lesson 1), it lives in a three-layer architecture (Lesson 2), and handling one message means having that <span class="mono">AgentState</span> get <strong>loaded → context assembled → looped over "call model + run tools" → written back</strong> (this lesson). Part 1, "The Big Picture," ends here: you can now "play" a message's whole journey in your head.</p>

<p>Each part that follows <strong>presses one stop on this spine into slow motion</strong>: the <strong>memory</strong> part magnifies step 5 — how core memory compiles into the system, how recall / archival are layered, how compaction happens; the <strong>tools</strong> part magnifies step 6 — how functions become schemas, how a <span class="mono">tool_call</span> is parsed and executed, how <span class="mono">tool_rules</span> constrain ordering; the <strong>provider</strong> part magnifies the "call LLM" moment — how each vendor's differences are flattened by <span class="mono">llm_api</span>; the <strong>persistence</strong> part magnifies step 7 — how messages and state hit the database. Every time you read a new detail, return to this spine and ask: "<strong>which of the seven stops does it happen at?</strong>" — as long as you can answer, no depth of detail will lose you.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li>A message's spine: <span class="mono">POST</span> → <span class="mono">send_message</span> → resolve <span class="mono">actor</span> → load <span class="mono">AgentState</span> → <span class="mono">AgentLoop.load</span> → <span class="mono">step</span> loop → tools/memory → persist → <span class="mono">LettaResponse</span>.</li>
    <li>The route is thin: only "identify → load save → build runtime → run loop"; the business is all in <span class="mono">step</span> / <span class="mono">_step</span>.</li>
    <li><strong>One message ≠ one model call</strong>: <span class="mono">step</span> is a loop of up to <span class="mono">max_steps</span> (default 50) rounds; one <span class="mono">_step</span> = one LLM call + tool execution + persistence.</li>
    <li>The loop's continuation rule is minimal: <span class="mono">_decide_continuation</span> — <strong>called a tool → continue; only a plain message → stop</strong> (a big simplification from MemGPT's heartbeat).</li>
    <li>Context is freshly assembled each round: <span class="mono">Memory.compile()</span> compiles core memory into message #0, the system (via <span class="mono">PromptGenerator</span>), plus in-context messages and tool schemas.</li>
    <li>The runtime is <strong>stateless</strong>: rebuilt from <span class="mono">AgentState</span> each time and discarded after use; state between steps lives in the database.</li>
  </ul>
</div>
""",
}
