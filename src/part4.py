"""Part 4 · The agent execution loop — lessons 13-16.

Bilingual lesson bodies as ``{"zh": html, "en": html}`` dicts, imported by
``registry.py``. Lesson 13 is the part's "map": it explains the starting point
of the loop — ``AgentState`` (an agent's save file) and the ``AgentLoop`` factory
that picks an engine by ``agent_type``. Markup conventions match part1/2/3.py.
"""

LESSON_13 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第三部分我们把 Letta 的"记忆"拆透了——三层记忆、记忆块、自我编辑、压缩。但记忆只是<strong>原料</strong>：真正让 agent "跑起来"的，是一圈一圈的<strong>执行循环</strong>。第四部分就来拆这个循环，而这一课是它的地图。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
循环从哪儿开始？答案是两样东西：一份叫 <strong>AgentState</strong> 的"存档"，和一个叫 <strong>AgentLoop.load</strong> 的"工厂"。存档装着重建 agent 所需的一切；工厂读存档上的 <span class="mono">agent_type</span>，决定这次该用哪个引擎来跑。这一课不深挖任何一个引擎的内部——那留给后三课；它只负责把"起点"摆正。读完，你就拿到了 14–16 课的地图。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把 AgentState 想成一张游戏存档，把 AgentLoop 想成一座工厂。</strong>游戏存档（save file）记下你的等级、装备、所在地图——读档就能在任何一台机器上接着玩。AgentState 就是 agent 的存档：身份、记忆、在窗消息、工具，全在里面；服务器自己不留记忆，每次请求都从数据库读出这张存档、跑一轮、再写回。而 AgentLoop 像一座工厂：同一张订单（存档）递进来，工厂看订单上"产品类型"那一栏，决定送它上哪条生产线。<strong>存档决定"是谁"，工厂决定"用哪台引擎跑"</strong>——这就是整个执行循环的起点。读懂这一张存档加这一座工厂，你就读懂了第四部分所有故事的开头。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：执行循环从"读存档、选引擎"开始。</strong><span class="mono">AgentState</span> 是 agent 的存档——装着 <span class="mono">id / system / agent_type / blocks / message_ids / tools / tool_rules / llm_config</span> 等"重建一个持久化 agent 所需的全部信息"。<span class="mono">AgentLoop.load</span> 是一座工厂——它读存档里的 <span class="mono">agent_type</span> 当钥匙，挑出这次要跑的实现：<span class="mono">letta_v1_agent</span> 走第三代 <span class="mono">LettaAgentV3</span>，其余走第二代 <span class="mono">LettaAgentV2</span>。而 agent 本身经历了三代演进：同步的元老 <span class="mono">Agent</span>、异步的 <span class="mono">LettaAgentV2</span>、砍掉心跳的 <span class="mono">LettaAgentV3</span>。记住这三件事，第四部分就有了骨架——存档、工厂、三代，正好对应"是谁、用哪台、什么脾气"三个问题。
</div>

<h2>AgentState：一个 agent 的"存档"</h2>
<p>先看存档本身。<span class="mono">AgentState</span>（<span class="mono">letta/schemas/agent.py</span>）的文档字符串只有一句话，却说尽了它的本质：<strong>"重建一个持久化 agent 所需的全部信息"</strong>。它不是某个跑在内存里的临时变量，而是一张能序列化、存进数据库、再读出来的<strong>快照</strong>。</p>

<p>这正好接上第 6 课"有状态 vs 无状态"：LLM 本身无状态，Letta 把 agent 的状态<strong>外化</strong>成这张存档。换句话说，"一个 agent"在 Letta 里就等于"一行数据库记录 + 它的存档表示"。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">那个 <span class="mono">id</span> 不是随机串，而是<strong>带类型前缀</strong>的：<span class="mono">agent-xxxx</span>（第 2、6 课）。一眼就能从 id 认出它是 agent，还是 block、message——这是 Letta 贯穿全局的命名约定。</span></div>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">身份</span><span class="name">id / name / agent_type</span></div>
    <div class="ld">带类型前缀的主键 <span class="mono">agent-xxxx</span>、名字，以及最关键的 <span class="mono">agent_type</span>——它就是工厂的分派键。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">在窗</span><span class="name">system / message_ids</span></div>
    <div class="ld">系统提示，加上"在窗消息的 id 列表"（第 11 课）——这两样直接决定下一轮喂给模型的上下文。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">记忆</span><span class="name">blocks / memory</span></div>
    <div class="ld">核心记忆块（第 8 课）。<span class="mono">blocks</span> 是新字段，<span class="mono">memory</span> 是它的废弃别名。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">行为 · 模型</span><span class="name">tools / tool_rules / model</span></div>
    <div class="ld">能调哪些工具、工具规则（第 16 课），以及模型句柄 <span class="mono">model</span>（旧字段 <span class="mono">llm_config</span>）。</div></div>
</div>

<div class="note info"><span class="ni">📌</span><span class="nx">把这四组连起来读：<strong>身份说"是谁"，在窗 + 记忆说"它现在知道什么"，行为 + 模型说"它能做什么、用谁来想"</strong>——合起来就够重建一个活的 agent。</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/agent.py</span><span class="ln">AgentState 关键字段（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentState</span>(OrmMetadataBase):       <span class="cm"># Pydantic，__id_prefix__ = "agent"</span>
    <span class="st">"重建一个持久化 agent 所需的全部信息"</span>  <span class="cm"># 类文档串</span>
    id: str                              <span class="cm"># "agent-xxxx"，带类型前缀的主键</span>
    name: str
    system: str                          <span class="cm"># 系统提示</span>
    agent_type: AgentType                <span class="cm"># 工厂据此选引擎（分派键）</span>
    message_ids: list[str] | <span class="kw">None</span>        <span class="cm"># 在窗消息的 id（第 11 课）</span>
    blocks: list[Block]                  <span class="cm"># 核心记忆块（新）</span>
    memory: Memory                       <span class="cm"># DEPRECATED -> 用 blocks</span>
    tools: list[Tool]
    tool_rules: list[ToolRule] | <span class="kw">None</span>    <span class="cm"># 工具规则（第 16 课）</span>
    model: str | <span class="kw">None</span>                    <span class="cm"># 模型句柄（新）</span>
    llm_config: LLMConfig                <span class="cm"># DEPRECATED -> 用 model</span>
</pre></div>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">看见成对的字段别犯晕：<span class="mono">memory / llm_config / sources</span> 都是<strong>废弃</strong>别名，新代码请认 <span class="mono">blocks / model / folders</span>。两套并存只是为了向后兼容。</span></div>

<p>别被字段数量吓到。它们大致就分成开头那四组：<strong>身份、在窗、记忆、行为 + 模型</strong>。抓住"合起来要能重建一个 agent"这条线，你就不必死记每个字段——缺了哪一类，自己也能反推出来。</p>

<h2>存档从哪儿来：从一行 ORM 记录"水合"出来</h2>
<p><span class="mono">AgentState</span> 是<strong>内存 / API 表示</strong>，不是数据库里的存储格式。真正落库的是 ORM 行 <span class="mono">letta/orm/agent.py</span>；每次需要时，由 <span class="mono">from_orm_async</span> 把那一行连同它的块、工具、消息 id 一起"水合（hydrate）"成一个 <span class="mono">AgentState</span> 对象。</p>

<p>这就是第 6 课那句"服务器不记得任何事"的落地：每个请求都现读存档、跑完再写回。所以同一个 agent 能在任意进程、任意机器上"读档续玩"——它的全部状态都在这张可搬运的存档里，而不在某个常驻内存的对象里。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">"水合 → 跑 → 写回"是每个请求的固定三拍。<strong>写回</strong>把这轮新增的消息、改动过的核心记忆落库，下个请求才能读到最新的存档。</span></div>

<p>"水合"这个词很形象：数据库里存的是<strong>脱水的</strong>原始行（外键、id 列表），读取时再把关联的块、工具、消息<strong>泡发</strong>成一个完整对象。<span class="mono">from_orm_async</span> 里的 <span class="mono">async</span> 也有讲究——这些关联要并发地去库里取，异步能省下不少等待。</p>

<div class="flow">
  <div class="node"><div class="nt">POST 消息</div><div class="nd">第 3 课</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">读出存档</div><div class="nd">AgentState 水合</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">AgentLoop.load</div><div class="nd">按类型选引擎</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">step 循环</div><div class="nd">14–16 课</div></div>
</div>

<div class="note info"><span class="ni">👉</span><span class="nx">把这条线和第 3 课接上：一条消息进来，先<strong>水合存档</strong>，再由工厂<strong>选引擎</strong>，最后才进 step 循环。本课讲的就是中间这两步——循环真正的"起跑线"。</span></div>

<h2>存档装了什么，又没装什么</h2>
<p>存档大，但不是"什么都往里塞"。它装的是<strong>指针和配置</strong>，不是海量正文。比如 <span class="mono">message_ids</span> 只是一串<strong>消息 id</strong>（第 11 课），真正的消息正文躺在 recall 的数据库表里；归档段落（第 10 课）更是压根不进存档。</p>

<p>这是个关键取舍：存档要<strong>能被频繁读写</strong>，就不能太重。所以它只留"在窗需要、或重建必需"的东西——身份、系统提示、核心记忆块、在窗消息的 id、工具清单——把窗外的海量内容交给各自的 manager 按需去捞。</p>

<div class="cellgroup">
  <div class="cg-cap"><b>存档里 vs 数据库里</b>：存档只放指针与配置，正文留在外面按需取</div>
  <div class="cells">
    <span class="cell hl">身份 / system / blocks</span>
    <span class="sep">·</span>
    <span class="cell hl">message_ids（指针）</span>
    <span class="sep">·</span>
    <span class="cell q">recall 正文 → MessageManager</span>
    <span class="sep">·</span>
    <span class="cell scale">archival 段落 → PassageManager</span>
  </div>
</div>

<div class="note tip"><span class="ni">💡</span><span class="nx">一句话记住：<strong>存档存"指针 + 配置"，不存"海量正文"。</strong><span class="mono">message_ids</span> 指向在窗消息，正文与归档都留在各自的数据库表里，要用再捞。</span></div>

<p>存档里还藏着些"行为开关"，比如 <span class="mono">message_buffer_autoclear</span>（默认 <span class="mono">False</span>）：一旦打开，agent 就<strong>不记前面的消息</strong>，只靠核心记忆与归档 / 回忆活着。这类字段不直接进上下文，却实打实地改变循环怎么跑——存档不只是"数据"，也带着"配置"。</p>

<h2>AgentLoop.load：按类型选引擎的工厂</h2>
<p>有了存档，下一步就是<strong>挑引擎</strong>。<span class="mono">AgentLoop.load</span>（<span class="mono">letta/agents/agent_loop.py</span>）是个 <span class="mono">@staticmethod</span> 工厂：它收下 <span class="mono">agent_state</span> 与 <span class="mono">actor</span>，读 <span class="mono">agent_state.agent_type</span> 当钥匙，<strong>返回一个 <span class="mono">BaseAgentV2</span> 实例</strong>——也就是这次要跑的循环。</p>

<p>分派规则一句话：<span class="mono">letta_v1_agent</span> 和 <span class="mono">sleeptime_agent</span> 走第三代 <span class="mono">LettaAgentV3</span>，<strong>其余一律</strong>走第二代 <span class="mono">LettaAgentV2</span>。只有当 agent 额外开了 <span class="mono">sleeptime</span> 且配了多 agent 组时，才换成 <span class="mono">SleeptimeMultiAgentV4 / V3</span>。</p>

<div class="note info"><span class="ni">📌</span><span class="nx"><span class="mono">sleeptime</span> + 多 agent 组那条分支属于<strong>进阶玩法</strong>（后台记忆整理），大多数 agent 用不到。先抓主干：<span class="mono">letta_v1 / sleeptime → V3</span>，其余 → V2。</span></div>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>拿到钥匙</h4><p>读 <span class="mono">agent_state.agent_type</span>——整个分派只看这一个字段。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>是 letta_v1 / sleeptime？</h4><p>是 → 返回 <span class="mono">LettaAgentV3</span>（新的简化循环，无心跳）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>否则</h4><p>memgpt / memgpt_v2 / react / workflow / voice… → 返回 <span class="mono">LettaAgentV2</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>开了 sleeptime + 组？</h4><p>换成 <span class="mono">SleeptimeMultiAgentV4</span>（v1/sleeptime 类型）或 <span class="mono">V3</span>（其他）。</p></div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/agent_loop.py</span><span class="ln">AgentLoop.load 分派（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentLoop</span>:
    <span class="kw">@staticmethod</span>
    <span class="kw">def</span> <span class="fn">load</span>(agent_state, actor) -> BaseAgentV2:
        t = agent_state.agent_type        <span class="cm"># 唯一的分派键</span>
        <span class="kw">if</span> t <span class="kw">in</span> [AgentType.letta_v1_agent, AgentType.sleeptime_agent]:
            <span class="kw">return</span> <span class="fn">LettaAgentV3</span>(agent_state, actor)   <span class="cm"># 新的简化循环</span>
        <span class="kw">else</span>:                              <span class="cm"># memgpt / react / workflow / voice ...</span>
            <span class="kw">return</span> <span class="fn">LettaAgentV2</span>(agent_state, actor)   <span class="cm"># 带心跳的老循环</span>
        <span class="cm"># 注：开了 sleeptime + group 时 -> SleeptimeMultiAgentV4 / V3</span>
</pre></div>

<div class="note tip"><span class="ni">💡</span><span class="nx">工厂的好处：调用方<strong>永远只写</strong> <span class="mono">AgentLoop.load(agent_state, actor)</span>，不必关心背后是 V2 还是 V3。将来新增一种 agent，只动这一个工厂，别处不必改。</span></div>

<p>顺带说工厂的第二个入参 <span class="mono">actor</span>——它是<strong>发起这次请求的用户</strong>，会一路带着做权限与归属校验。工厂不光"挑类"，还把 <span class="mono">agent_state</span> 与 <span class="mono">actor</span> 一起装配进引擎，返回的对象拿来就能 <span class="mono">step</span>。</p>

<p>还有一点容易忽略：<span class="mono">load</span> 是<strong>每个请求都重来一遍</strong>的。上一轮跑完，引擎对象就扔了；下一轮再 <span class="mono">load</span> 一个新的。这跟"存档"的思路完全一致——引擎不留状态，状态全在 <span class="mono">agent_state</span> 里，每轮现装现跑。</p>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>三个锚点，一条主线。</strong>存档是 <span class="mono">letta/schemas/agent.py::AgentState</span>（Pydantic，继承链 <span class="mono">OrmMetadataBase → LettaBase → BaseModel</span>，<span class="mono">__id_prefix__ = "agent"</span>），由 ORM 行 <span class="mono">letta/orm/agent.py</span> 经 <span class="mono">from_orm_async</span> 水合。工厂是 <span class="mono">letta/agents/agent_loop.py::AgentLoop.load</span>，一个返回 <span class="mono">BaseAgentV2</span> 的 <span class="mono">@staticmethod</span>。钥匙是 <span class="mono">letta/schemas/enums.py::AgentType</span> 这个字符串枚举。三者的关系就一句话：<strong>工厂读存档的 <span class="mono">agent_type</span>，挑一个引擎</strong>。本课只看这条主线，引擎内部怎么转，留给第 14–16 课。
</div>

<h2>三代 agent：从同步元老到砍掉心跳</h2>
<p>工厂能"挑"，是因为背后真有好几代实现。它们共享一个抽象接口 <span class="mono">BaseAgentV2</span>（<span class="mono">letta/agents/base_agent_v2.py</span>，规定了 <span class="mono">build_request / step / stream</span> 三个抽象方法），但脾气各不相同。</p>

<p><strong>元老 <span class="mono">Agent</span></strong>（<span class="mono">letta/agent.py</span>）是<strong>同步</strong>的：<span class="mono">def step(...) -> LettaUsageStatistics</span>，内部一个 <span class="mono">while True</span> 循环，靠"心跳请求"和函数失败来决定要不要继续。它是 MemGPT 的原始形态，<strong>不在工厂的返回路径上</strong>。</p>

<div class="note info"><span class="ni">👉</span><span class="nx">"不在工厂路径上"不等于没用：一些直接构造 <span class="mono">Agent</span> 的旧代码仍在。但<strong>本课主线</strong>——你新建 agent 默认会走的那条——只看 V2 / V3。</span></div>

<table class="t">
  <tr><th>代际</th><th>类</th><th>同步/异步</th><th>怎么决定"再走一步"</th><th>工厂会返回它吗</th></tr>
  <tr><td>元老</td><td class="mono">Agent</td><td>同步 sync</td><td>心跳请求 + 函数失败，<span class="mono">while True</span></td><td>❌ 不经工厂</td></tr>
  <tr><td>第二代</td><td class="mono">LettaAgentV2</td><td>异步 async</td><td>心跳驱动（<span class="mono">request_heartbeat</span>）</td><td>✅ 大多数类型</td></tr>
  <tr><td>第三代</td><td class="mono">LettaAgentV3</td><td>异步 async</td><td>无心跳 · 有工具调用就继续</td><td>✅ letta_v1 / sleeptime</td></tr>
</table>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">连返回类型都变了：元老 <span class="mono">Agent.step</span> 返回 <span class="mono">LettaUsageStatistics</span>（用量统计），而 V2 的 <span class="mono">step</span> 返回 <span class="mono">LettaResponse</span>（完整响应）。代际不同，连"走一轮"给你什么都不一样。</span></div>

<p><strong>第二代 <span class="mono">LettaAgentV2</span></strong> 是异步重写：<span class="mono">async def step(...) -> LettaResponse</span>，是否续步由<strong>心跳</strong>决定（<span class="mono">_decide_continuation</span> 读 <span class="mono">request_heartbeat</span>）。<strong>第三代 <span class="mono">LettaAgentV3</span> 直接继承 V2</strong>，文档说它"砍到更精简"：<strong>不要心跳，循环改成"只要有工具调用就继续"</strong>。</p>

<p>为什么要从同步元老升级到异步的 V2？因为服务端要同时扛<strong>很多 agent、还要流式吐字</strong>。同步的 <span class="mono">while True</span> 会把线程占死；异步能在等模型、等工具时让出，吞吐与延迟都更好。V3 又在 V2 的异步底座上，把"心跳"这层老机制也省了。</p>

<div class="note info"><span class="ni">👉</span><span class="nx">三代是一条<strong>继承 + 简化</strong>的线：元老 <span class="mono">Agent</span>（同步）→ <span class="mono">LettaAgentV2</span>（异步、心跳）→ <span class="mono">LettaAgentV3</span>（继承 V2、砍掉心跳）。第 14 课拆 V3 的循环，第 15 课专讲"心跳"这个对照。</span></div>

<h2>三代共享的接口：BaseAgentV2</h2>
<p>工厂敢"返回什么都行"，靠的是一份<strong>统一契约</strong>。<span class="mono">BaseAgentV2</span> 是个抽象基类（<span class="mono">ABC</span>），规定任何一代引擎都必须实现三个方法：<span class="mono">build_request</span>（拼请求）、<span class="mono">step</span>（走一轮）、<span class="mono">stream</span>（流式走一轮）。</p>

<p>有了这份契约，调用方只认接口、不认具体类——这正是工厂能成立的前提。V2 和 V3 都老实继承 <span class="mono">BaseAgentV2</span>；V3 因为继承自 V2，很多方法直接复用，只<strong>覆写</strong>要简化的那部分（比如续步判断 <span class="mono">_decide_continuation</span>）。</p>

<div class="note info"><span class="ni">📌</span><span class="nx">抽象基类 = "插槽规格"。工厂往插槽里插哪块板子（V2 / V3）都行，因为它们的<strong>引脚（方法签名）一样</strong>。这就是"面向接口编程"在 Letta 里的一处具体落地。</span></div>

<p>顺便回答一个常见疑问：既然 V3 是"砍掉东西"的简化版，为什么还要<strong>继承</strong> V2、而不是另起炉灶？因为两者绝大部分逻辑（拼请求、调模型、存消息）是一样的，继承能<strong>最大化复用</strong>，只在少数几处覆写差异。这也解释了代码里那条略反直觉的关系：更"新"的 V3，是更"老"的 V2 的子类。</p>

<h2>九种 agent_type，到底各走哪条线</h2>
<p>把钥匙摊开看。<span class="mono">AgentType</span>（<span class="mono">letta/schemas/enums.py</span>）是个字符串枚举，共九个值。下表把每个值映到工厂在"无 sleeptime 组"时返回的引擎——你会发现绝大多数都落在 V2，只有两个走 V3。</p>

<p><span class="mono">agent_type</span> 是<strong>创建 agent 时就定死</strong>的：<span class="mono">CreateAgent.agent_type</span> 的默认值正是 <span class="mono">AgentType.letta_v1_agent</span>（<span class="mono">letta/schemas/agent.py</span>）。所以你不指定类型、随手建一个 agent，它就是 <span class="mono">letta_v1_agent</span>，跑的就是 V3——新设计成了新默认。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/enums.py</span><span class="ln">AgentType 枚举（节选）</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentType</span>(str, Enum):
    memgpt_agent     = <span class="st">"memgpt_agent"</span>      <span class="cm"># 最初的 memgpt 工具集</span>
    memgpt_v2_agent  = <span class="st">"memgpt_v2_agent"</span>   <span class="cm"># 翻新版</span>
    letta_v1_agent   = <span class="st">"letta_v1_agent"</span>    <span class="cm"># 简化 memgpt 循环：无心跳、不强制工具调用</span>
    react_agent      = <span class="st">"react_agent"</span>       <span class="cm"># 无记忆工具</span>
    workflow_agent   = <span class="st">"workflow_agent"</span>    <span class="cm"># 自动清空消息缓冲</span>
    <span class="cm"># …… split_thread / sleeptime / voice_convo / voice_sleeptime</span>
    <span class="cm"># 注意：根本没有 letta_agent_v3 这个值！</span>
</pre></div>

<table class="t">
  <tr><th>agent_type</th><th>无组时返回</th><th>备注</th></tr>
  <tr><td class="mono">letta_v1_agent</td><td>LettaAgentV3</td><td>主路径；新建 agent 的默认值</td></tr>
  <tr><td class="mono">sleeptime_agent</td><td>LettaAgentV3</td><td>无组时回退到 V3</td></tr>
  <tr><td class="mono">memgpt_agent</td><td>LettaAgentV2</td><td>OG memgpt 工具</td></tr>
  <tr><td class="mono">memgpt_v2_agent</td><td>LettaAgentV2</td><td>翻新版</td></tr>
  <tr><td class="mono">react_agent</td><td>LettaAgentV2</td><td>无记忆工具</td></tr>
  <tr><td class="mono">workflow_agent</td><td>LettaAgentV2</td><td>自动清缓冲</td></tr>
  <tr><td class="mono">split_thread_agent</td><td>LettaAgentV2</td><td>—</td></tr>
  <tr><td class="mono">voice_convo_agent</td><td>LettaAgentV2</td><td>—</td></tr>
  <tr><td class="mono">voice_sleeptime_agent</td><td>LettaAgentV2</td><td>—</td></tr>
</table>

<div class="note tip"><span class="ni">🧠</span><span class="nx">记一条捷径就够：<strong>只有 <span class="mono">letta_v1_agent</span>（和无组的 <span class="mono">sleeptime_agent</span>）走 V3，其余全是 V2。</strong>而新建 agent 默认就是 <span class="mono">letta_v1_agent</span>——所以你随手 create 一个，跑的就是 V3。</span></div>

<div class="cute">
  <div class="row">
    <span class="emoji">📁</span><span class="lab">存档 · agent_type</span>
    <span class="arrow">→</span>
    <span class="emoji">🏭</span><span class="lab">AgentLoop.load</span>
    <span class="arrow">→</span>
    <span class="emoji">🤖</span><span class="bubble">letta_v1 → V3 引擎</span>
    <span class="emoji">🤖</span><span class="bubble">其余 → V2 引擎</span>
  </div>
  <div class="cap">同一张存档进厂，工厂看 agent_type 这一栏，挑出该上哪条生产线——按类型选引擎</div>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>"读存档、选引擎"这六个字，就把第 6 课的"有状态 vs 无状态"落到了一个具体对象上。</strong>服务器自己不留记忆：每次请求都把整张存档从数据库水合出来、跑一轮、再写回——所以同一个 agent 能在任意进程、任意机器上"读档续玩"。而 <span class="mono">AgentLoop.load</span> 就是"读档时顺手挑引擎"：同一张存档，<span class="mono">agent_type</span> 决定这次用哪套循环（V3 精简 / V2 心跳 / sleeptime 多 agent）。最妙的是那个反直觉的彩蛋：类明明叫 <span class="mono">LettaAgentV3</span>，触发它的枚举值却是 <span class="mono">letta_v1_agent</span>——因为"V3 的代码"实现的是"Letta v1 的设计"（砍掉了 MemGPT 的心跳与强制工具调用）。<strong>名字记录的是历史，行为写在代码里。</strong>看懂这一层，你就不会再被命名带偏——也会对 Letta"把历史封存进名字、把真相写进代码"的风格会心一笑。
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>别被名字骗了。</strong>第一，<strong>没有</strong> <span class="mono">letta_agent_v3</span> 或 <span class="mono">letta_v3_agent</span> 这个枚举值——触发 <span class="mono">LettaAgentV3</span> 的是 <span class="mono">letta_v1_agent</span>，类名 ≠ 枚举名，千万别照着类名去猜枚举。第二，<span class="mono">AgentState</span> 里 <span class="mono">memory / llm_config / sources</span> 都是<strong>废弃字段</strong>，新代码要用 <span class="mono">blocks / model / folders</span>；两套并存只是兼容历史，读代码时认准新名。把这两点记牢，能省掉一大半"为什么对不上"的困惑。一句口诀收尾：<strong>类名带 V3、枚举名带 v1；新代码认 blocks / model，老字段只当别名读。</strong>
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>为什么要用一个"工厂"，而不是直接 new 一个 agent？</summary><div class="acc-body">
<p><strong>示例：</strong>调用方（比如处理 POST 的服务）只想说"把这个 agent 跑起来"，它不该关心你内部分了几代实现。<span class="mono">AgentLoop.load(agent_state, actor)</span> 一行就够，返回值统一是 <span class="mono">BaseAgentV2</span>。</p>
<p><strong>为什么这样设计：</strong>把"选哪代实现"的分支<strong>收口到一个地方</strong>。同一张存档进来，<span class="mono">agent_type</span> 决定走哪条线；将来新增一种 agent，只动这一个工厂方法，别处的调用代码一行都不用改。这正是"开闭原则"——对扩展开放、对修改关闭——的活例子。</p>
<p><strong>源码在哪：</strong><span class="mono">letta/agents/agent_loop.py::AgentLoop.load</span>，一个 <span class="mono">@staticmethod</span>，返回类型标注就是 <span class="mono">BaseAgentV2</span>。</p>
<p><strong>还有什么替代：</strong>在每个调用点写 <span class="mono">if agent_type == …</span>——分支会散落各处、加一种类型就要改十处。工厂是教科书式的解法。</p>
</div></details>

<details class="accordion"><summary>"V3 的类 / letta_v1 的枚举"为什么对不上？</summary><div class="acc-body">
<p><strong>示例：</strong>你想让一个 agent 跑 <span class="mono">LettaAgentV3</span>，于是去枚举里找 <span class="mono">letta_v3_agent</span>——找不到。能触发 V3 的值其实叫 <span class="mono">letta_v1_agent</span>。</p>
<p><strong>为什么这样设计：</strong>两个版本号说的不是一回事。<span class="mono">V3</span> 是<strong>代码实现</strong>的代际（第三次重写循环）；<span class="mono">v1</span> 是<strong>设计版本</strong>——"Letta v1"这套设计主张砍掉 MemGPT 的心跳与强制工具调用。V3 的代码，实现的正是 v1 的设计。</p>
<p><strong>源码在哪：</strong>枚举注释写得很直白——<span class="mono">letta_v1_agent</span> = "simplification of the memgpt loop, no heartbeats or forced tool calls"（<span class="mono">letta/schemas/enums.py</span>）。</p>
<p><strong>还有什么替代：</strong>把枚举改名 <span class="mono">letta_agent_v3</span> 当然更直观，但那是个会破坏所有存量数据的改名（每行 agent 都存了这个字符串）。于是历史包袱就这么留下了。</p>
</div></details>

<details class="accordion"><summary>AgentState 里那些"废弃字段"，到底信哪个？</summary><div class="acc-body">
<p><strong>示例：</strong>你打印一个 <span class="mono">AgentState</span>，看到既有 <span class="mono">memory</span> 又有 <span class="mono">blocks</span>，既有 <span class="mono">llm_config</span> 又有 <span class="mono">model</span>——该读哪个？</p>
<p><strong>为什么这样设计：</strong>这些字段在做<strong>渐进式迁移</strong>。老字段（<span class="mono">memory / llm_config / embedding_config / sources</span>）被标了 <span class="mono">deprecated=True</span> 但暂时保留，免得旧客户端一升级就崩；新字段（<span class="mono">blocks / model / embedding / folders</span>）是未来方向。</p>
<p><strong>源码在哪：</strong>都在 <span class="mono">letta/schemas/agent.py::AgentState</span>，每个废弃字段的 <span class="mono">Field(description=...)</span> 里直接写着"Use `X` field instead"。</p>
<p><strong>还有什么替代：</strong>直接删老字段——会一刀切断所有老客户端。保留 + 标记废弃，是兼容期里最稳的过渡。读代码时：<strong>认新字段，把老字段当别名。</strong></p>
</div></details>

<details class="accordion"><summary>其实还有"第四个类" LettaAgent，它算第几代？</summary><div class="acc-body">
<p><strong>示例：</strong>你在 <span class="mono">letta/agents/</span> 下还会看到一个 <span class="mono">LettaAgent</span>（注意没有 V2/V3 后缀），容易以为它就是工厂返回的那个。</p>
<p><strong>为什么这样设计：</strong><span class="mono">LettaAgent</span>（<span class="mono">letta/agents/letta_agent.py</span>，继承的是更早的 <span class="mono">BaseAgent</span>）服务于 group / voice 等场景，<strong>不在 <span class="mono">AgentLoop.load</span> 的返回路径上</strong>。本课的主线只看工厂这条路：V2 / V3 都继承 <span class="mono">BaseAgentV2</span>。换句话说，"代"这个词在 Letta 里有点乱——别去数有几个 Agent 类，只记住"工厂会还给你 V2 或 V3"就够走完第四部分。</p>
<p><strong>源码在哪：</strong>抽象接口 <span class="mono">base_agent_v2.py::BaseAgentV2</span>（抽象方法 <span class="mono">build_request / step / stream</span>）；旁路的 <span class="mono">letta_agent.py::LettaAgent</span>。</p>
<p><strong>还有什么替代：</strong>把所有路径都塞进一个工厂——会把 group/voice 的特殊装配也搅进来。Letta 选择让工厂只管"单 agent 主循环"这一条线，其余另走它路。</p>
</div></details>

<h2>第四部分由此展开：下一站</h2>
<p>这一课是第四部分的地图：<strong>存档（AgentState）说"是谁"，工厂（AgentLoop.load）按 agent_type 选引擎，三代实现各有脾气。</strong>循环的"起点"就此立住。把这三个名词焊进脑子，后面再复杂的循环细节，都能挂回到它们身上。</p>

<p>接下来三课各放大一格：第 14 课拆 <span class="mono">LettaAgentV3</span> 的循环到底怎么一步步走；第 15 课对照"心跳"——看 V2 的 <span class="mono">request_heartbeat</span> 和 V3"靠工具调用续步"差在哪；第 16 课讲<strong>工具规则</strong>（<span class="mono">tool_rules</span>），也就是存档里那个一直没细说的字段。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">一句话带走：<strong>同一张存档，按 <span class="mono">agent_type</span> 选不同引擎</strong>。存档是"是谁"，工厂是"用哪台引擎"，三代是"引擎的脾气"。后面三课，都在这张地图上展开。</span></div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>AgentState = 存档</strong>：装着 <span class="mono">id / system / agent_type / blocks / message_ids / tools / tool_rules / model</span> 等"重建一个持久化 agent 所需的全部信息"；它是内存 / API 表示，由 ORM 行水合而来。</li>
    <li><strong>AgentLoop.load = 工厂</strong>：读 <span class="mono">agent_state.agent_type</span> 当钥匙，返回一个 <span class="mono">BaseAgentV2</span> 实例——<span class="mono">letta_v1_agent / sleeptime_agent</span> → V3，其余 → V2。</li>
    <li><strong>三代演进</strong>：同步元老 <span class="mono">Agent</span> → 异步 <span class="mono">LettaAgentV2</span>（心跳）→ <span class="mono">LettaAgentV3</span>（继承 V2、砍掉心跳，靠工具调用续步）。</li>
    <li><strong>命名陷阱</strong>：没有 <span class="mono">letta_agent_v3</span> 枚举值；触发 V3 的是 <span class="mono">letta_v1_agent</span>（V3 代码实现 v1 设计）。类名 ≠ 枚举名。</li>
    <li><strong>废弃字段</strong>：<span class="mono">memory / llm_config / sources</span> 已废弃，新代码用 <span class="mono">blocks / model / folders</span>。</li>
    <li><strong>呼应第 6 课</strong>：服务器无状态，每次请求水合存档、跑、写回，所以同一 agent 能在任意机器"读档续玩"。</li>
    <li><strong>源码</strong>：<span class="mono">schemas/agent.py::AgentState</span>、<span class="mono">agents/agent_loop.py::AgentLoop.load</span>、<span class="mono">schemas/enums.py::AgentType</span>。</li>
  </ul>
</div>
""",
    "en": r"""<p>stub</p>""",
}
