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
