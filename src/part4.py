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
  <strong>一句话抓住本课：执行循环从"读存档、选引擎"开始。</strong><span class="mono">AgentState</span> 是 agent 的存档——装着 <span class="mono">id / system / agent_type / blocks / message_ids / tools / tool_rules / llm_config</span> 等"重建一个持久化 agent 所需的全部信息"。<span class="mono">AgentLoop.load</span> 是一座工厂——它读存档里的 <span class="mono">agent_type</span> 当钥匙，挑出这次要跑的实现：<span class="mono">letta_v1_agent</span>（及 <span class="mono">sleeptime_agent</span>）走第三代 <span class="mono">LettaAgentV3</span>，其余走第二代 <span class="mono">LettaAgentV2</span>。而 agent 本身经历了三代演进：同步的元老 <span class="mono">Agent</span>、异步的 <span class="mono">LettaAgentV2</span>、砍掉心跳的 <span class="mono">LettaAgentV3</span>。记住这三件事，第四部分就有了骨架——存档、工厂、三代，正好对应"是谁、用哪台、什么脾气"三个问题。
</div>

<h2>AgentState：一个 agent 的"存档"</h2>
<p>先看存档本身。<span class="mono">AgentState</span>（<span class="mono">letta/schemas/agent.py</span>）的文档字符串里有一句点睛之言，道尽了它的本质：<strong>"重建一个持久化 agent 所需的全部信息"</strong>。它不是某个跑在内存里的临时变量，而是一张能序列化、存进数据库、再读出来的<strong>快照</strong>。</p>

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
<p><span class="mono">AgentState</span> 是<strong>内存 / API 表示</strong>，不是数据库里的存储格式。真正落库的是 ORM 行 <span class="mono">letta/orm/agent.py</span>；每次需要时，由 <span class="mono">to_pydantic_async</span> 把那一行连同它的块、工具、消息 id 一起"水合（hydrate）"成一个 <span class="mono">AgentState</span> 对象。</p>

<p>这就是第 6 课那句"服务器不记得任何事"的落地：每个请求都现读存档、跑完再写回。所以同一个 agent 能在任意进程、任意机器上"读档续玩"——它的全部状态都在这张可搬运的存档里，而不在某个常驻内存的对象里。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">"水合 → 跑 → 写回"是每个请求的固定三拍。<strong>写回</strong>把这轮新增的消息、改动过的核心记忆落库，下个请求才能读到最新的存档。</span></div>

<p>"水合"这个词很形象：数据库里存的是<strong>脱水的</strong>原始行（外键、id 列表），读取时再把关联的块、工具、消息<strong>泡发</strong>成一个完整对象。<span class="mono">to_pydantic_async</span> 里的 <span class="mono">async</span> 也有讲究——这些关联要并发地去库里取，异步能省下不少等待。</p>

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
  <strong>三个锚点，一条主线。</strong>存档是 <span class="mono">letta/schemas/agent.py::AgentState</span>（Pydantic，继承链 <span class="mono">OrmMetadataBase → LettaBase → BaseModel</span>，<span class="mono">__id_prefix__ = "agent"</span>），由 ORM 行 <span class="mono">letta/orm/agent.py</span> 经 <span class="mono">to_pydantic_async</span> 水合。工厂是 <span class="mono">letta/agents/agent_loop.py::AgentLoop.load</span>，一个返回 <span class="mono">BaseAgentV2</span> 的 <span class="mono">@staticmethod</span>。钥匙是 <span class="mono">letta/schemas/enums.py::AgentType</span> 这个字符串枚举。三者的关系就一句话：<strong>工厂读存档的 <span class="mono">agent_type</span>，挑一个引擎</strong>。本课只看这条主线，引擎内部怎么转，留给第 14–16 课。
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
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
In Part 3 we took Letta's "memory" apart — three memory tiers, memory blocks, self-editing, compaction. But memory is only the <strong>raw material</strong>: what actually makes an agent <strong>run</strong> is a loop that turns, round after round. Part 4 takes that loop apart, and this lesson is its map.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
Where does the loop start? With two things: a "save file" called <strong>AgentState</strong>, and a "factory" called <strong>AgentLoop.load</strong>. The save file holds everything needed to rebuild an agent; the factory reads the <span class="mono">agent_type</span> on that save and decides which engine runs this time. This lesson doesn't dig into any one engine's internals — that's for the next three lessons; it just sets the starting line straight. Finish it and you hold the map for lessons 14–16.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Think of AgentState as a game save file, and AgentLoop as a factory.</strong> A save file records your level, gear, and current map — load it and you keep playing on any machine. AgentState is the agent's save file: identity, memory, in-window messages, tools, all in there; the server keeps no memory of its own — every request reads this save from the database, runs one round, and writes it back. AgentLoop is like a factory: the same order (save file) comes in, the factory looks at the "product type" column and decides which production line to send it down. <strong>The save decides "who," the factory decides "which engine runs it"</strong> — that's the starting point of the whole execution loop. Read this one save file plus this one factory, and you've read the opening of every story in Part 4.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>One line for this lesson: the execution loop starts by "reading the save, picking the engine."</strong> <span class="mono">AgentState</span> is the agent's save file — holding <span class="mono">id / system / agent_type / blocks / message_ids / tools / tool_rules / llm_config</span> and more, "all the information needed to recreate a persisted agent." <span class="mono">AgentLoop.load</span> is a factory — it reads the <span class="mono">agent_type</span> on the save as a key and picks the implementation to run: <span class="mono">letta_v1_agent</span> (and <span class="mono">sleeptime_agent</span>) goes to third-generation <span class="mono">LettaAgentV3</span>, the rest to second-generation <span class="mono">LettaAgentV2</span>. And the agent itself went through three generations: the synchronous elder <span class="mono">Agent</span>, the async <span class="mono">LettaAgentV2</span>, and the heartbeat-free <span class="mono">LettaAgentV3</span>. Remember these three things and Part 4 has a skeleton — save, factory, three generations, matching "who, which engine, what temperament."
</div>

<h2>AgentState: an agent's "save file"</h2>
<p>Start with the save itself. The docstring of <span class="mono">AgentState</span> (<span class="mono">letta/schemas/agent.py</span>) has one line that captures its essence: <strong>"all the information needed to recreate a persisted agent."</strong> It isn't a temporary variable living in memory — it's a <strong>snapshot</strong> that can be serialized, stored in the database, and read back out.</p>

<p>This connects straight to lesson 6's "stateful vs stateless": the LLM itself is stateless, so Letta <strong>externalizes</strong> the agent's state into this save file. Put differently, "an agent" in Letta equals "one database row + its save-file representation."</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">That <span class="mono">id</span> isn't a random string — it's <strong>type-prefixed</strong>: <span class="mono">agent-xxxx</span> (lessons 2, 6). One glance tells you it's an agent, not a block or message — a naming convention Letta uses everywhere.</span></div>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">Identity</span><span class="name">id / name / agent_type</span></div>
    <div class="ld">A type-prefixed primary key <span class="mono">agent-xxxx</span>, a name, and the all-important <span class="mono">agent_type</span> — the factory's dispatch key.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">In-window</span><span class="name">system / message_ids</span></div>
    <div class="ld">The system prompt plus the "list of in-window message ids" (lesson 11) — these two directly decide the context fed to the model next round.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Memory</span><span class="name">blocks / memory</span></div>
    <div class="ld">Core memory blocks (lesson 8). <span class="mono">blocks</span> is the new field, <span class="mono">memory</span> is its deprecated alias.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">Behavior · Model</span><span class="name">tools / tool_rules / model</span></div>
    <div class="ld">Which tools it can call, tool rules (lesson 16), and the model handle <span class="mono">model</span> (old field <span class="mono">llm_config</span>).</div></div>
</div>

<div class="note info"><span class="ni">📌</span><span class="nx">Read the four groups together: <strong>identity says "who," in-window + memory say "what it knows right now," behavior + model say "what it can do and who does the thinking"</strong> — together that's enough to rebuild a living agent.</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/agent.py</span><span class="ln">AgentState key fields (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentState</span>(OrmMetadataBase):       <span class="cm"># Pydantic, __id_prefix__ = "agent"</span>
    <span class="st">"all the information needed to recreate a persisted agent"</span>  <span class="cm"># docstring</span>
    id: str                              <span class="cm"># "agent-xxxx", type-prefixed key</span>
    name: str
    system: str                          <span class="cm"># system prompt</span>
    agent_type: AgentType                <span class="cm"># factory picks the engine by this (dispatch key)</span>
    message_ids: list[str] | <span class="kw">None</span>        <span class="cm"># ids of in-window messages (lesson 11)</span>
    blocks: list[Block]                  <span class="cm"># core memory blocks (new)</span>
    memory: Memory                       <span class="cm"># DEPRECATED -> use blocks</span>
    tools: list[Tool]
    tool_rules: list[ToolRule] | <span class="kw">None</span>    <span class="cm"># tool rules (lesson 16)</span>
    model: str | <span class="kw">None</span>                    <span class="cm"># model handle (new)</span>
    llm_config: LLMConfig                <span class="cm"># DEPRECATED -> use model</span>
</pre></div>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">Don't get dizzy seeing paired fields: <span class="mono">memory / llm_config / sources</span> are all <strong>deprecated</strong> aliases — new code should use <span class="mono">blocks / model / folders</span>. Both sets coexist only for backward compatibility.</span></div>

<p>Don't let the field count scare you. They roughly fall into the four groups above: <strong>identity, in-window, memory, behavior + model</strong>. Hold onto the thread "together they must rebuild an agent," and you needn't memorize every field — if a group is missing, you can reason it back yourself.</p>

<h2>Where the save comes from: "hydrated" out of one ORM row</h2>
<p><span class="mono">AgentState</span> is the <strong>in-memory / API representation</strong>, not the storage format in the database. What actually lands in the DB is the ORM row <span class="mono">letta/orm/agent.py</span>; whenever needed, <span class="mono">to_pydantic_async</span> "hydrates" that row — together with its blocks, tools, and message ids — into an <span class="mono">AgentState</span> object.</p>

<p>This is lesson 6's "the server remembers nothing" made concrete: every request reads the save fresh, runs, then writes it back. So the same agent can "load and resume" on any process, any machine — all its state lives in this portable save file, not in some long-lived in-memory object.</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">"Hydrate → run → write back" is the fixed three-beat of every request. The <strong>write-back</strong> persists this round's new messages and edited core memory, so the next request reads the latest save.</span></div>

<p>The word "hydrate" is vivid: the database stores a <strong>dehydrated</strong> raw row (foreign keys, id lists), and on read the related blocks, tools, and messages are <strong>rehydrated</strong> into a full object. The <span class="mono">async</span> in <span class="mono">to_pydantic_async</span> matters too — those relations are fetched from the DB concurrently, and async saves a lot of waiting.</p>

<div class="flow">
  <div class="node"><div class="nt">POST message</div><div class="nd">lesson 3</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">read the save</div><div class="nd">AgentState hydrate</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">AgentLoop.load</div><div class="nd">pick engine by type</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">step loop</div><div class="nd">lessons 14–16</div></div>
</div>

<div class="note info"><span class="ni">👉</span><span class="nx">Connect this line to lesson 3: a message comes in, first <strong>hydrate the save</strong>, then the factory <strong>picks the engine</strong>, and only then enter the step loop. This lesson covers those two middle steps — the loop's real "starting line."</span></div>

<h2>What the save holds — and what it doesn't</h2>
<p>The save is big, but it isn't "stuff everything in." It holds <strong>pointers and config</strong>, not bulk text. For instance <span class="mono">message_ids</span> is just a list of <strong>message ids</strong> (lesson 11) — the actual message text lives in recall's database table; archival passages (lesson 10) don't enter the save at all.</p>

<p>This is a key trade-off: the save must be <strong>read and written often</strong>, so it can't be heavy. It keeps only what's "needed in-window, or required to rebuild" — identity, system prompt, core memory blocks, in-window message ids, tool list — and leaves the bulk out-of-window content to each manager to fetch on demand.</p>

<div class="cellgroup">
  <div class="cg-cap"><b>In the save vs in the DB</b>: the save keeps only pointers and config; text stays outside, fetched on demand</div>
  <div class="cells">
    <span class="cell hl">identity / system / blocks</span>
    <span class="sep">·</span>
    <span class="cell hl">message_ids (pointers)</span>
    <span class="sep">·</span>
    <span class="cell q">recall text → MessageManager</span>
    <span class="sep">·</span>
    <span class="cell scale">archival passages → PassageManager</span>
  </div>
</div>

<div class="note tip"><span class="ni">💡</span><span class="nx">Remember it in one line: <strong>the save stores "pointers + config," not "bulk text."</strong> <span class="mono">message_ids</span> points to in-window messages; the text and archive stay in their own DB tables, fetched when needed.</span></div>

<p>The save also hides a few "behavior switches," like <span class="mono">message_buffer_autoclear</span> (default <span class="mono">False</span>): turn it on and the agent <strong>won't remember earlier messages</strong>, living only on core memory plus archival / recall. Such fields don't enter the context directly, yet they really change how the loop runs — the save isn't just "data," it carries "config" too.</p>

<h2>AgentLoop.load: the factory that picks an engine by type</h2>
<p>With the save in hand, the next step is <strong>picking an engine</strong>. <span class="mono">AgentLoop.load</span> (<span class="mono">letta/agents/agent_loop.py</span>) is a <span class="mono">@staticmethod</span> factory: it takes <span class="mono">agent_state</span> and <span class="mono">actor</span>, reads <span class="mono">agent_state.agent_type</span> as the key, and <strong>returns a <span class="mono">BaseAgentV2</span> instance</strong> — the loop to run this time.</p>

<p>The dispatch rule in one line: <span class="mono">letta_v1_agent</span> and <span class="mono">sleeptime_agent</span> go to third-gen <span class="mono">LettaAgentV3</span>, <strong>everything else</strong> goes to second-gen <span class="mono">LettaAgentV2</span>. Only when an agent additionally enables <span class="mono">sleeptime</span> and is wired to a multi-agent group does it switch to <span class="mono">SleeptimeMultiAgentV4 / V3</span>.</p>

<div class="note info"><span class="ni">📌</span><span class="nx">That <span class="mono">sleeptime</span> + multi-agent-group branch is <strong>advanced play</strong> (background memory housekeeping) that most agents never touch. Grab the trunk first: <span class="mono">letta_v1 / sleeptime → V3</span>, everything else → V2.</span></div>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Grab the key</h4><p>Read <span class="mono">agent_state.agent_type</span> — the whole dispatch looks at this one field.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Is it letta_v1 / sleeptime?</h4><p>Yes → return <span class="mono">LettaAgentV3</span> (the new simplified loop, no heartbeats).</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Otherwise</h4><p>memgpt / memgpt_v2 / react / workflow / voice… → return <span class="mono">LettaAgentV2</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>sleeptime + group on?</h4><p>Switch to <span class="mono">SleeptimeMultiAgentV4</span> (v1/sleeptime types) or <span class="mono">V3</span> (others).</p></div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/agent_loop.py</span><span class="ln">AgentLoop.load dispatch (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentLoop</span>:
    <span class="kw">@staticmethod</span>
    <span class="kw">def</span> <span class="fn">load</span>(agent_state, actor) -> BaseAgentV2:
        t = agent_state.agent_type        <span class="cm"># the only dispatch key</span>
        <span class="kw">if</span> t <span class="kw">in</span> [AgentType.letta_v1_agent, AgentType.sleeptime_agent]:
            <span class="kw">return</span> <span class="fn">LettaAgentV3</span>(agent_state, actor)   <span class="cm"># new simplified loop</span>
        <span class="kw">else</span>:                              <span class="cm"># memgpt / react / workflow / voice ...</span>
            <span class="kw">return</span> <span class="fn">LettaAgentV2</span>(agent_state, actor)   <span class="cm"># older loop with heartbeats</span>
        <span class="cm"># note: with sleeptime + group -> SleeptimeMultiAgentV4 / V3</span>
</pre></div>

<div class="note tip"><span class="ni">💡</span><span class="nx">The factory's payoff: callers <strong>only ever write</strong> <span class="mono">AgentLoop.load(agent_state, actor)</span>, never caring whether it's V2 or V3 behind it. Add a new agent kind later and you touch only this one factory, nowhere else.</span></div>

<p>A word on the factory's second argument <span class="mono">actor</span> — it's the <strong>user who made this request</strong>, carried along for permission and ownership checks. The factory not only "picks the class" but also assembles <span class="mono">agent_state</span> and <span class="mono">actor</span> into the engine, so the returned object is ready to <span class="mono">step</span>.</p>

<p>One thing easily missed: <span class="mono">load</span> <strong>runs fresh every request</strong>. Last round finishes, the engine object is thrown away; next round <span class="mono">load</span>s a new one. This matches the "save file" idea exactly — the engine keeps no state, all state lives in <span class="mono">agent_state</span>, assembled and run anew each round.</p>

<div class="card detail">
  <div class="tag">🔬 Down to the code</div>
  <strong>Three anchors, one through-line.</strong> The save is <span class="mono">letta/schemas/agent.py::AgentState</span> (Pydantic, inheritance chain <span class="mono">OrmMetadataBase → LettaBase → BaseModel</span>, <span class="mono">__id_prefix__ = "agent"</span>), hydrated from the ORM row <span class="mono">letta/orm/agent.py</span> via <span class="mono">to_pydantic_async</span>. The factory is <span class="mono">letta/agents/agent_loop.py::AgentLoop.load</span>, a <span class="mono">@staticmethod</span> returning <span class="mono">BaseAgentV2</span>. The key is the string enum <span class="mono">letta/schemas/enums.py::AgentType</span>. Their relationship in one line: <strong>the factory reads the save's <span class="mono">agent_type</span> and picks an engine</strong>. This lesson follows only that through-line; how an engine turns inside is left to lessons 14–16.
</div>

<h2>Three generations of agent: from synchronous elder to heartbeat-free</h2>
<p>The factory can "pick" because there really are several generations behind it. They share one abstract interface, <span class="mono">BaseAgentV2</span> (<span class="mono">letta/agents/base_agent_v2.py</span>, which mandates three abstract methods <span class="mono">build_request / step / stream</span>), but their temperaments differ.</p>

<p><strong>The elder <span class="mono">Agent</span></strong> (<span class="mono">letta/agent.py</span>) is <strong>synchronous</strong>: <span class="mono">def step(...) -> LettaUsageStatistics</span>, with an inner <span class="mono">while True</span> loop that relies on "heartbeat requests" and function failures to decide whether to continue. It's MemGPT's original form, and it's <strong>not on the factory's return path</strong>.</p>

<div class="note info"><span class="ni">👉</span><span class="nx">"Not on the factory path" doesn't mean useless: some older code that constructs <span class="mono">Agent</span> directly still exists. But <strong>this lesson's main line</strong> — the one a new agent runs by default — only looks at V2 / V3.</span></div>

<table class="t">
  <tr><th>Generation</th><th>Class</th><th>Sync/Async</th><th>How it decides to "step again"</th><th>Returned by factory?</th></tr>
  <tr><td>Elder</td><td class="mono">Agent</td><td>sync</td><td>heartbeat requests + function failures, <span class="mono">while True</span></td><td>❌ not via factory</td></tr>
  <tr><td>2nd gen</td><td class="mono">LettaAgentV2</td><td>async</td><td>heartbeat-driven (<span class="mono">request_heartbeat</span>)</td><td>✅ most types</td></tr>
  <tr><td>3rd gen</td><td class="mono">LettaAgentV3</td><td>async</td><td>no heartbeat · continues if there's a tool call</td><td>✅ letta_v1 / sleeptime</td></tr>
</table>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">Even the return type changed: the elder <span class="mono">Agent.step</span> returns <span class="mono">LettaUsageStatistics</span> (usage stats), while V2's <span class="mono">step</span> returns <span class="mono">LettaResponse</span> (a full response). Different generation, even "one round" hands you something different.</span></div>

<p><strong>2nd-gen <span class="mono">LettaAgentV2</span></strong> is an async rewrite: <span class="mono">async def step(...) -> LettaResponse</span>, where whether to continue is decided by <strong>heartbeats</strong> (<span class="mono">_decide_continuation</span> reads <span class="mono">request_heartbeat</span>). <strong>3rd-gen <span class="mono">LettaAgentV3</span> directly subclasses V2</strong>, and its docstring says it's "stripped down further": <strong>no heartbeats, the loop becomes "continue as long as there's a tool call."</strong></p>

<p>Why upgrade from the synchronous elder to async V2? Because the server must carry <strong>many agents at once and stream tokens</strong>. A synchronous <span class="mono">while True</span> ties up a thread; async can yield while waiting on the model or tools, improving both throughput and latency. V3 then, on V2's async foundation, also drops the old "heartbeat" layer.</p>

<div class="note info"><span class="ni">👉</span><span class="nx">The three generations are a line of <strong>inheritance + simplification</strong>: the elder <span class="mono">Agent</span> (sync) → <span class="mono">LettaAgentV2</span> (async, heartbeat) → <span class="mono">LettaAgentV3</span> (subclasses V2, drops heartbeats). Lesson 14 dissects V3's loop; lesson 15 focuses on the "heartbeat" contrast.</span></div>

<h2>The interface the generations share: BaseAgentV2</h2>
<p>The factory dares to "return anything" thanks to a <strong>uniform contract</strong>. <span class="mono">BaseAgentV2</span> is an abstract base class (<span class="mono">ABC</span>) that mandates every generation of engine implement three methods: <span class="mono">build_request</span> (assemble the request), <span class="mono">step</span> (run one round), and <span class="mono">stream</span> (stream one round).</p>

<p>With this contract, callers know only the interface, not the concrete class — exactly the premise that lets the factory work. Both V2 and V3 dutifully subclass <span class="mono">BaseAgentV2</span>; because V3 inherits from V2, it reuses many methods directly and only <strong>overrides</strong> the parts it simplifies (like the continuation decision <span class="mono">_decide_continuation</span>).</p>

<div class="note info"><span class="ni">📌</span><span class="nx">An abstract base class = a "slot spec." The factory can plug in any board (V2 / V3), because their <strong>pins (method signatures) are identical</strong>. That's "programming to an interface" made concrete in Letta.</span></div>

<p>One common question, answered: since V3 is the "stripped-down" simplification, why still <strong>inherit</strong> V2 instead of starting fresh? Because the vast majority of logic (assembling requests, calling the model, storing messages) is the same, and inheritance <strong>maximizes reuse</strong>, overriding only a few spots. That also explains the slightly counter-intuitive relationship in the code: the "newer" V3 is a subclass of the "older" V2.</p>

<h2>Nine agent_types, and which line each one takes</h2>
<p>Spread the key out. <span class="mono">AgentType</span> (<span class="mono">letta/schemas/enums.py</span>) is a string enum with nine values. The table below maps each value to the engine the factory returns "without a sleeptime group" — you'll find the vast majority land on V2, with only two going to V3.</p>

<p><span class="mono">agent_type</span> is <strong>fixed when the agent is created</strong>: the default of <span class="mono">CreateAgent.agent_type</span> is exactly <span class="mono">AgentType.letta_v1_agent</span> (<span class="mono">letta/schemas/agent.py</span>). So if you don't specify a type and just spin up an agent, it's <span class="mono">letta_v1_agent</span>, running V3 — the new design became the new default.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/enums.py</span><span class="ln">AgentType enum (excerpt)</span></div>
<pre><span class="kw">class</span> <span class="fn">AgentType</span>(str, Enum):
    memgpt_agent     = <span class="st">"memgpt_agent"</span>      <span class="cm"># the original memgpt toolset</span>
    memgpt_v2_agent  = <span class="st">"memgpt_v2_agent"</span>   <span class="cm"># refreshed</span>
    letta_v1_agent   = <span class="st">"letta_v1_agent"</span>    <span class="cm"># simplified memgpt loop: no heartbeats, no forced tool calls</span>
    react_agent      = <span class="st">"react_agent"</span>       <span class="cm"># no memory tools</span>
    workflow_agent   = <span class="st">"workflow_agent"</span>    <span class="cm"># auto-clearing message buffer</span>
    <span class="cm"># ... split_thread / sleeptime / voice_convo / voice_sleeptime</span>
    <span class="cm"># note: there is NO letta_agent_v3 value!</span>
</pre></div>

<table class="t">
  <tr><th>agent_type</th><th>Returned (no group)</th><th>Note</th></tr>
  <tr><td class="mono">letta_v1_agent</td><td>LettaAgentV3</td><td>main path; default for new agents</td></tr>
  <tr><td class="mono">sleeptime_agent</td><td>LettaAgentV3</td><td>falls back to V3 when not grouped</td></tr>
  <tr><td class="mono">memgpt_agent</td><td>LettaAgentV2</td><td>OG memgpt tools</td></tr>
  <tr><td class="mono">memgpt_v2_agent</td><td>LettaAgentV2</td><td>refreshed</td></tr>
  <tr><td class="mono">react_agent</td><td>LettaAgentV2</td><td>no memory tools</td></tr>
  <tr><td class="mono">workflow_agent</td><td>LettaAgentV2</td><td>auto-clears buffer</td></tr>
  <tr><td class="mono">split_thread_agent</td><td>LettaAgentV2</td><td>—</td></tr>
  <tr><td class="mono">voice_convo_agent</td><td>LettaAgentV2</td><td>—</td></tr>
  <tr><td class="mono">voice_sleeptime_agent</td><td>LettaAgentV2</td><td>—</td></tr>
</table>

<div class="note tip"><span class="ni">🧠</span><span class="nx">One shortcut is enough: <strong>only <span class="mono">letta_v1_agent</span> (and the ungrouped <span class="mono">sleeptime_agent</span>) go to V3, everything else is V2.</strong> And new agents default to <span class="mono">letta_v1_agent</span> — so spin one up casually and it runs V3.</span></div>

<div class="cute">
  <div class="row">
    <span class="emoji">📁</span><span class="lab">save · agent_type</span>
    <span class="arrow">→</span>
    <span class="emoji">🏭</span><span class="lab">AgentLoop.load</span>
    <span class="arrow">→</span>
    <span class="emoji">🤖</span><span class="bubble">letta_v1 → V3 engine</span>
    <span class="emoji">🤖</span><span class="bubble">others → V2 engine</span>
  </div>
  <div class="cap">the same save enters the factory; it reads the agent_type column and picks the production line — pick the engine by type</div>
</div>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  <strong>Those six words, "read the save, pick the engine," ground lesson 6's "stateful vs stateless" in one concrete object.</strong> The server keeps no memory of its own: every request hydrates the whole save from the database, runs one round, and writes it back — so the same agent can "load and resume" on any process, any machine. And <span class="mono">AgentLoop.load</span> is "picking the engine while you load the save": same save file, <span class="mono">agent_type</span> decides which loop runs this time (V3 simplified / V2 heartbeat / sleeptime multi-agent). The delight is the counter-intuitive kicker: the class is literally named <span class="mono">LettaAgentV3</span>, yet the enum value that triggers it is <span class="mono">letta_v1_agent</span> — because the "V3 code" implements the "Letta v1 design" (dropping MemGPT's heartbeats and forced tool calls). <strong>The name records history; behavior lives in the code.</strong> See this layer and naming will never mislead you — and you'll smile at Letta's style of "sealing history into names, writing truth into code."
</div>

<div class="card warn">
  <div class="tag">⚠️ Common pitfalls</div>
  <strong>Don't be fooled by names.</strong> First, there is <strong>no</strong> <span class="mono">letta_agent_v3</span> or <span class="mono">letta_v3_agent</span> enum value — the thing that triggers <span class="mono">LettaAgentV3</span> is <span class="mono">letta_v1_agent</span>; class name ≠ enum name, so never guess the enum from the class name. Second, in <span class="mono">AgentState</span> the fields <span class="mono">memory / llm_config / sources</span> are all <strong>deprecated</strong>; new code should use <span class="mono">blocks / model / folders</span> — both sets coexist only for historical compatibility, so trust the new names when reading code. Keep these two straight and you'll spare yourself half the "why doesn't this match" confusion. A closing mnemonic: <strong>class name carries V3, enum name carries v1; new code knows blocks / model, old fields are just aliases.</strong>
</div>

<h2>Digging a little deeper</h2>

<details class="accordion"><summary>Why use a "factory" instead of just newing an agent?</summary><div class="acc-body">
<p><strong>Example:</strong> the caller (say, the service handling a POST) just wants to say "run this agent"; it shouldn't care how many generations of implementation you have inside. <span class="mono">AgentLoop.load(agent_state, actor)</span> is one line, and the return value is uniformly <span class="mono">BaseAgentV2</span>.</p>
<p><strong>Why it's designed this way:</strong> it <strong>funnels</strong> the "which generation to pick" branching into one place. The same save comes in, <span class="mono">agent_type</span> decides the line; add a new agent kind later and you touch only this one factory method, not a single line of caller code. This is the open–closed principle — open to extension, closed to modification — in the flesh.</p>
<p><strong>Where in the source:</strong> <span class="mono">letta/agents/agent_loop.py::AgentLoop.load</span>, a <span class="mono">@staticmethod</span> whose return annotation is exactly <span class="mono">BaseAgentV2</span>.</p>
<p><strong>What's the alternative:</strong> write <span class="mono">if agent_type == …</span> at every call site — branches scatter everywhere and adding a type means editing ten places. The factory is the textbook solution.</p>
</div></details>

<details class="accordion"><summary>Why don't the "V3 class" and "letta_v1 enum" match?</summary><div class="acc-body">
<p><strong>Example:</strong> you want an agent to run <span class="mono">LettaAgentV3</span>, so you hunt the enum for <span class="mono">letta_v3_agent</span> — and can't find it. The value that triggers V3 is actually called <span class="mono">letta_v1_agent</span>.</p>
<p><strong>Why it's designed this way:</strong> the two version numbers mean different things. <span class="mono">V3</span> is the generation of <strong>code implementation</strong> (the third rewrite of the loop); <span class="mono">v1</span> is the <strong>design version</strong> — "Letta v1," a design that advocates dropping MemGPT's heartbeats and forced tool calls. The V3 code implements exactly the v1 design.</p>
<p><strong>Where in the source:</strong> the enum comment says it plainly — <span class="mono">letta_v1_agent</span> = "simplification of the memgpt loop, no heartbeats or forced tool calls" (<span class="mono">letta/schemas/enums.py</span>).</p>
<p><strong>What's the alternative:</strong> renaming the enum to <span class="mono">letta_agent_v3</span> would be clearer, but that's a rename that breaks all stored data (every agent row stored this string). So the historical baggage stays.</p>
</div></details>

<details class="accordion"><summary>Those "deprecated fields" in AgentState — which do I trust?</summary><div class="acc-body">
<p><strong>Example:</strong> you print an <span class="mono">AgentState</span> and see both <span class="mono">memory</span> and <span class="mono">blocks</span>, both <span class="mono">llm_config</span> and <span class="mono">model</span> — which to read?</p>
<p><strong>Why it's designed this way:</strong> these fields are doing a <strong>gradual migration</strong>. The old fields (<span class="mono">memory / llm_config / embedding_config / sources</span>) are marked <span class="mono">deprecated=True</span> but kept for now, so old clients don't crash the moment they upgrade; the new fields (<span class="mono">blocks / model / embedding / folders</span>) are the future direction.</p>
<p><strong>Where in the source:</strong> all in <span class="mono">letta/schemas/agent.py::AgentState</span>, where each deprecated field's <span class="mono">Field(description=...)</span> literally says "Use `X` field instead."</p>
<p><strong>What's the alternative:</strong> deleting the old fields outright — which would cut off all old clients at once. Keeping them + marking deprecated is the steadiest transition during the compatibility window. When reading code: <strong>trust the new fields, treat the old ones as aliases.</strong></p>
</div></details>

<details class="accordion"><summary>There's actually a "fourth class," LettaAgent — which generation is it?</summary><div class="acc-body">
<p><strong>Example:</strong> under <span class="mono">letta/agents/</span> you'll also see a <span class="mono">LettaAgent</span> (note: no V2/V3 suffix), and it's easy to assume it's the one the factory returns.</p>
<p><strong>Why it's designed this way:</strong> <span class="mono">LettaAgent</span> (<span class="mono">letta/agents/letta_agent.py</span>, which inherits the earlier <span class="mono">BaseAgent</span>) serves group / voice scenarios and is <strong>not on <span class="mono">AgentLoop.load</span>'s return path</strong>. This lesson's main line only follows the factory: both V2 and V3 inherit <span class="mono">BaseAgentV2</span>. In other words, the word "generation" is a bit messy in Letta — don't count how many Agent classes there are, just remember "the factory hands you back V2 or V3" and that's enough to get through Part 4.</p>
<p><strong>Where in the source:</strong> the abstract interface <span class="mono">base_agent_v2.py::BaseAgentV2</span> (abstract methods <span class="mono">build_request / step / stream</span>); the side-path <span class="mono">letta_agent.py::LettaAgent</span>.</p>
<p><strong>What's the alternative:</strong> cramming every path into one factory — which would drag group/voice's special assembly in too. Letta chose to let the factory handle only the "single-agent main loop," with the rest going their own way.</p>
</div></details>

<h2>Part 4 opens from here: next stop</h2>
<p>This lesson is Part 4's map: <strong>the save (AgentState) says "who," the factory (AgentLoop.load) picks an engine by agent_type, and the three generations each have their temperament.</strong> The loop's "starting point" is now firmly in place. Weld these three nouns into your head and even the most complex loop details ahead can be hung back onto them.</p>

<p>The next three lessons each zoom in one notch: lesson 14 dissects exactly how <span class="mono">LettaAgentV3</span>'s loop steps through; lesson 15 contrasts the "heartbeat" — how V2's <span class="mono">request_heartbeat</span> differs from V3's "continue on a tool call"; lesson 16 covers <strong>tool rules</strong> (<span class="mono">tool_rules</span>), that field in the save we kept not detailing.</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">Take away one line: <strong>the same save, different engines by <span class="mono">agent_type</span></strong>. The save is "who," the factory is "which engine," the three generations are "the engine's temperament." The next three lessons all unfold on this map.</span></div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>AgentState = the save file</strong>: holds <span class="mono">id / system / agent_type / blocks / message_ids / tools / tool_rules / model</span> and more — "all the information needed to recreate a persisted agent"; it's the in-memory / API representation, hydrated from an ORM row.</li>
    <li><strong>AgentLoop.load = the factory</strong>: reads <span class="mono">agent_state.agent_type</span> as the key and returns a <span class="mono">BaseAgentV2</span> instance — <span class="mono">letta_v1_agent / sleeptime_agent</span> → V3, everything else → V2.</li>
    <li><strong>Three generations</strong>: synchronous elder <span class="mono">Agent</span> → async <span class="mono">LettaAgentV2</span> (heartbeat) → <span class="mono">LettaAgentV3</span> (subclasses V2, drops heartbeats, continues on tool calls).</li>
    <li><strong>Naming trap</strong>: there is no <span class="mono">letta_agent_v3</span> enum value; what triggers V3 is <span class="mono">letta_v1_agent</span> (the V3 code implements the v1 design). Class name ≠ enum name.</li>
    <li><strong>Deprecated fields</strong>: <span class="mono">memory / llm_config / sources</span> are deprecated; new code uses <span class="mono">blocks / model / folders</span>.</li>
    <li><strong>Echoes lesson 6</strong>: the server is stateless; every request hydrates the save, runs, writes back — so the same agent can "load and resume" on any machine.</li>
    <li><strong>Source</strong>: <span class="mono">schemas/agent.py::AgentState</span>, <span class="mono">agents/agent_loop.py::AgentLoop.load</span>, <span class="mono">schemas/enums.py::AgentType</span>.</li>
  </ul>
</div>
""",
}


LESSON_14 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课我们站在工厂门口：一份叫 <strong>AgentState</strong> 的"存档"递进来，<span class="mono">AgentLoop.load</span> 看 <span class="mono">agent_type</span> 这一栏，挑出这次该跑的引擎——默认那条线挑中的，是第三代 <strong>LettaAgentV3</strong>。可工厂只负责"挑"，没说引擎"怎么转"。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
这一课，我们掀开 V3 引擎的盖子。里面没有魔法，只有一个朴素的 <strong>for 循环</strong>：调一次模型 → 执行工具 → 问一句"还要继续吗" → 再来一遍，最多 50 次。而那句"还要继续吗"的判据，简单到反直觉——它不看模型"想不想继续"，只看模型这一轮<strong>有没有调工具</strong>。读完这一课，你就拿到了 agent "跑起来"的全部真相。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把 V3 的循环想成一名流水线工人。</strong>工人面前有条传送带：每来一个零件（一次 step），他做一件事——看图纸、动手装、装完抬头看"后面还有没有活"。有活就接着装下一个，没活就把工位交还给你（用户）。但工人有条铁规矩：一天最多干 <strong>50 件</strong>，到点必须打卡下班，免得无限加班。最妙的是他判断"还有没有活"的方式特别朴素：不是问自己"我还想不想干"，而是看"我这一轮有没有<strong>伸手去拿工具</strong>"——伸手拿了工具，说明话没说完、活没干完，那就再转一圈；这一轮光说话没动工具，那就是收尾了，把话筒交还给你。整条流水线就这么转：<strong>拿活 → 干活 → 看看还有没有下一件 → 最多 50 件就下班。</strong>
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：<span class="mono">step()</span> 是个带预算的 for 循环，每一圈抽干一个 <span class="mono">_step</span>。</strong><span class="mono">step()</span>（<span class="mono">letta_agent_v3.py::step</span>）的骨架就是 <span class="mono">for i in range(max_steps)</span>，<span class="mono">max_steps</span> 默认 <span class="mono">DEFAULT_MAX_STEPS = 50</span>；每一圈把一个 <span class="mono">_step</span> 异步生成器抽干（<span class="mono">async for chunk</span>），循环结束统一返回<strong>一个</strong> <span class="mono">LettaResponse</span>。而一次 <span class="mono">_step</span> 干三件事：<strong>调一次 LLM、执行工具、把结果落库</strong>（拿有效工具 → 刷新消息 → 调模型 → <span class="mono">_handle_ai_response</span> → 持久化 → yield）。续步与否由 <span class="mono">_decide_continuation</span> 拍板，规则朴素到一句话——"没调工具就结束，调了工具就继续"，外加几条硬覆盖（终止工具 / 退出前必调 / 到 50 步 / 要审批）。记住这三件事——<strong>for 循环、一次 _step、续步规则</strong>——V3 的循环就拆完了。
</div>

<h2>step()：一个带预算的 for 循环</h2>
<p>先看最外层。很多人以为"agent 循环"是什么精巧的状态机，可 <span class="mono">step()</span>（<span class="mono">letta_agent_v3.py::step</span>）的骨架朴素得让人意外：就是一句 <span class="mono">for i in range(max_steps)</span>。每一圈调一个 <span class="mono">_step</span>、抽干它吐出的消息攒进一个列表；循环跑完，把列表打包成一个 <span class="mono">LettaResponse</span> 返回。</p>

<div class="note tip"><span class="ni">💡</span><span class="nx"><span class="mono">max_steps</span> 的默认值写在 <span class="mono">constants.py::DEFAULT_MAX_STEPS = 50</span>。这个"预算"就是循环的<strong>安全绳</strong>——后面有专门一节讲它防的到底是什么。</span></div>

<p>每一圈里真正干活的是 <span class="mono">self._step(...)</span>，它是个<strong>异步生成器</strong>。<span class="mono">step()</span> 用 <span class="mono">async for chunk in response</span> 把它一块块抽干，每块（一条 <span class="mono">LettaMessage</span>）都 append 进结果列表。抽干之后，看一眼 <span class="mono">self.should_continue</span> 这个开关：为真就转下一圈，为假就 <span class="mono">break</span>。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>进入第 i 圈</h4><p>还在预算内（<span class="mono">i &lt; 50</span>）就开跑；用尽就退出。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>跑一个 _step</h4><p>一次 LLM 调用 + 工具执行；<span class="mono">async for</span> 把它吐的消息抽干、攒进列表。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>should_continue？</h4><p>这一轮调工具了吗？这个开关由 <span class="mono">_decide_continuation</span> 写好。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>是 / 否</h4><p>是 → 回到顶上转下一圈；否 → <span class="mono">break</span> 跳出循环。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>i == 49 兜底</h4><p>跑满最后一圈还没人设停因，就盖上 <span class="mono">max_steps</span>。</p></div></div>
</div>

<div class="note info"><span class="ni">📌</span><span class="nx">那个开关 <span class="mono">should_continue</span> 不是 <span class="mono">step()</span> 自己算的——它由 <span class="mono">_step</span> 内部写好（更准确说，是 <span class="mono">_handle_ai_response</span> 一并算出 <span class="mono">(新消息, should_continue, stop_reason)</span> 三元组）。<span class="mono">step()</span> 只管<strong>读</strong>这个开关。</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">step 主循环（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">step</span>(self, input_messages, max_steps=DEFAULT_MAX_STEPS, ...) -> LettaResponse:
    msgs = []
    <span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span>(max_steps):          <span class="cm"># 预算：最多 50 圈</span>
        response = self.<span class="fn">_step</span>(...)        <span class="cm"># 一次 LLM + 工具，异步生成器</span>
        <span class="kw">async for</span> chunk <span class="kw">in</span> response:    <span class="cm"># 把这一圈吐的消息抽干</span>
            msgs.<span class="fn">append</span>(chunk)
        <span class="kw">if not</span> self.should_continue:      <span class="cm"># _step 写好的开关</span>
            <span class="kw">break</span>                         <span class="cm"># 没调工具 -> 收尾</span>
        <span class="kw">if</span> i == max_steps - 1 <span class="kw">and</span> self.stop_reason <span class="kw">is None</span>:
            self.stop_reason = <span class="fn">LettaStopReason</span>(StopReasonType.max_steps)
    <span class="cm"># 循环外：没人设停因就默认 end_turn，最后打包成一个响应</span>
    <span class="kw">return</span> <span class="fn">LettaResponse</span>(messages=msgs, stop_reason=self.stop_reason <span class="kw">or</span> end_turn)
</pre></div>

<p>循环跑完还有两处收尾值得记。其一，若跑到最后一圈（<span class="mono">i == max_steps - 1</span>）都没人设过停因，<span class="mono">step()</span> 会主动盖一个 <span class="mono">StopReasonType.max_steps</span>——这就是"预算用尽"的标记。其二，整个循环结束后若仍没有任何停因，默认就是 <span class="mono">StopReasonType.end_turn</span>（正常收尾）。</p>

<h2>一次 _step：LLM 调用 + 工具执行 + 落库</h2>
<p>拆完外层，钻进每一圈的 <span class="mono">_step</span>（<span class="mono">letta_agent_v3.py::_step</span>）。源码里它的定位写得很清楚——"一次 LLM 调用与工具执行"，是所有公开方法（<span class="mono">step</span> / <span class="mono">stream</span>）共同 funnel 进来的那个异步生成器。一次 <span class="mono">_step</span>，干的就是三件事：<strong>调一次模型、执行工具、把结果落库</strong>。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>拿有效工具 + 要不要强制</h4><p><span class="mono">_get_valid_tools()</span>，再问 <span class="mono">tool_rules_solver.should_force_tool_call()</span>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>刷新消息</h4><p><span class="mono">_refresh_messages</span> 擦掉旧的内心独白；<strong>不重建系统提示</strong>（保住 prefix cache）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>调 LLM</h4><p><span class="mono">llm_adapter.invoke_llm(...)</span>，外面裹一层"撑爆就压缩重试"。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>_handle_ai_response</h4><p>校验并执行工具，算出 <span class="mono">(新消息, should_continue, stop_reason)</span>。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>落库</h4><p><span class="mono">_checkpoint_messages</span> 把这一步的消息写进库——<strong>先落库，再流式</strong>。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>yield</h4><p>把消息一块块吐给外层 <span class="mono">step()</span> 去 append。</p></div></div>
</div>

<div class="note info"><span class="ni">👉</span><span class="nx">第 2 步那句"不重建系统提示"是个性能细节：系统提示是消息列表最前面、最稳定的一段，保持它不变，模型服务端的 <strong>prefix cache</strong>（第 5、9 课）才能命中。系统提示只在<strong>压缩或重置后</strong>才重建。</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">_step 骨架（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">_step</span>(self, messages, ...):        <span class="cm"># 异步生成器：一次 LLM + 工具</span>
    valid_tools = <span class="kw">await</span> self.<span class="fn">_get_valid_tools</span>()
    force = self.tool_rules_solver.<span class="fn">should_force_tool_call</span>()
    messages = <span class="kw">await</span> self.<span class="fn">_refresh_messages</span>(messages)  <span class="cm"># 擦内心独白，不重建系统提示</span>
    <span class="kw">for</span> _ <span class="kw">in</span> <span class="fn">range</span>(max_retries + <span class="nb">1</span>):       <span class="cm"># 撑爆就压缩重试（有上限）</span>
        <span class="kw">try</span>:
            <span class="kw">async for</span> chunk <span class="kw">in</span> llm_adapter.<span class="fn">invoke_llm</span>(messages, valid_tools):
                <span class="kw">yield</span> chunk
            <span class="kw">break</span>
        <span class="kw">except</span> ContextWindowExceededError:   <span class="cm"># 接上第 12 课的压缩</span>
            messages = <span class="kw">await</span> self.<span class="fn">compact</span>(...)
            <span class="kw">await</span> self.<span class="fn">rebuild_system_prompt_async</span>()
    new_messages, self.should_continue, self.stop_reason = \
        <span class="kw">await</span> self.<span class="fn">_handle_ai_response</span>(tool_calls, valid_tools, ...)
    <span class="kw">await</span> self.<span class="fn">_checkpoint_messages</span>(...)        <span class="cm"># 持久化要在流式之前</span>
    <span class="kw">for</span> m <span class="kw">in</span> new_messages:
        <span class="kw">yield</span> m
</pre></div>

<div class="note tip"><span class="ni">🧠</span><span class="nx">把第 5 步那句源码注释记牢——"<strong>持久化要发生在流式之前</strong>，以最小化 agent 进入不一致状态的概率"。一会儿有专门的折叠讲它为什么这么重要。</span></div>

<div class="cute">
  <div class="row">
    <span class="emoji">🐹</span><span class="lab">step 3/50</span>
    <span class="arrow">→</span>
    <span class="emoji">🔁</span><span class="lab">这轮调工具了？</span>
    <span class="arrow">→</span>
    <span class="emoji">🛞</span><span class="bubble">调了 → 再转一圈！</span>
    <span class="emoji">🛑</span><span class="bubble">没调 → 刹车，停。</span>
  </div>
  <div class="cap">仓鼠轮上的里程表数到 3/50：只要这一轮伸手调了工具，就再蹬一圈；空手而归就刹车下班</div>
</div>

<h2>继续还是停：_decide_continuation 拍板</h2>
<p>现在轮到全课的题眼：循环凭什么决定"再走一步"还是"收工"？答案在 <span class="mono">_decide_continuation</span>（<span class="mono">letta_agent_v3.py::_decide_continuation</span>）。它的文档字符串把规则写成两条，朴素到反直觉：<strong>1. 没调工具？循环结束。2. 调了工具？循环继续。</strong></p>

<div class="note tip"><span class="ni">💡</span><span class="nx">反直觉在哪？它压根<strong>不看</strong>模型有没有说"我想继续"。它只认一个客观事实——这一轮模型<strong>有没有发起工具调用</strong>。调了，说明还有后续要做（执行完工具得让模型看看结果）；没调，说明模型在直接回话了，那就把话筒交还用户。</span></div>

<p>为什么"调了工具就得继续"？因为工具调用是个<strong>两段式</strong>动作：模型先说"我要调 <span class="mono">search</span>"，系统执行 <span class="mono">search</span> 拿到结果，还得把结果<strong>喂回</strong>模型让它接着说。所以只要这一轮有工具调用，循环就必须再转一圈消化结果——这也正是 <span class="mono">letta_v1_agent</span> 注释里 "no heartbeats" 的真意：不靠模型自己举手要心跳，只靠"有没有调工具"这个客观信号驱动。</p>

<div class="flow">
  <div class="node hl"><div class="nt">这轮调工具了吗？</div><div class="nd">_decide_continuation 的唯一题眼</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">否 · 没调工具</div><div class="nd">还有"退出前必调"的工具没调？有 → 继续；没有 → 停 end_turn</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">是 · 调了工具</div><div class="nd">是"终止工具"？是 → 停 tool_rule；否 → 继续</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">硬覆盖</div><div class="nd">已是第 50 步？→ 停 max_steps</div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">_decide_continuation（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">_decide_continuation</span>(self, agent_state, tool_call_name,
                         tool_rule_violated, tool_rules_solver, is_final_step, finish_reason=None):
    <span class="cm"># 规则：没调工具 -> 结束；调了工具 -> 继续（再加几条硬覆盖）</span>
    <span class="kw">if</span> tool_call_name <span class="kw">is None</span>:                  <span class="cm"># 这一轮没调工具</span>
        uncalled = tool_rules_solver.<span class="fn">get_uncalled_required_tools</span>(...)
        <span class="kw">if</span> uncalled <span class="kw">and not</span> is_final_step:
            <span class="kw">return</span> <span class="nb">True</span>, nudge, <span class="nb">None</span>           <span class="cm"># 还有"退出前必调" -> 继续并提示补调</span>
        <span class="kw">if</span> finish_reason == <span class="st">"length"</span>:
            <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(max_tokens_exceeded)
        <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(end_turn)      <span class="cm"># 正常收尾</span>
    <span class="kw">else</span>:                                       <span class="cm"># 这一轮调了工具</span>
        <span class="kw">if</span> tool_rule_violated:
            <span class="kw">return</span> <span class="nb">True</span>, nudge, <span class="nb">None</span>           <span class="cm"># 违规也继续（带纠正提示）</span>
        tool_rules_solver.<span class="fn">register_tool_call</span>(tool_call_name)
        <span class="kw">if</span> tool_rules_solver.<span class="fn">is_terminal_tool</span>(tool_call_name):
            <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(tool_rule)   <span class="cm"># 终止工具 -> 停</span>
        <span class="kw">if</span> is_final_step:
            <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(max_steps)   <span class="cm"># 到 50 步 -> 停</span>
        <span class="kw">return</span> <span class="nb">True</span>, nudge, <span class="nb">None</span>               <span class="cm"># 否则继续</span>
</pre></div>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">这里藏着几条<strong>硬覆盖</strong>，别忽略：即便规则说"没调工具就结束"，只要还有 <span class="mono">required_before_exit</span>（退出前必须至少调一次）的工具没调，循环就被强行续上、并提示模型去补调；反过来，即便调了工具，撞上"终止工具"或"第 50 步"也会被强行停下。<strong>规则是骨架，覆盖是补丁。</strong></span></div>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>四个锚点，一条主线。</strong>外层循环是 <span class="mono">letta_agent_v3.py::step</span>（<span class="mono">for i in range(max_steps)</span>，返回 <span class="mono">LettaResponse</span>）；每圈的 <span class="mono">letta_agent_v3.py::_step</span> 是"一次 LLM + 工具 + 落库"的异步生成器；工具的校验与执行、那个续步三元组在 <span class="mono">letta_agent_v3.py::_handle_ai_response</span>；续步判据在 <span class="mono">letta_agent_v3.py::_decide_continuation</span>。再加两个常量级锚点：预算 <span class="mono">constants.py::DEFAULT_MAX_STEPS = 50</span>，停因 <span class="mono">letta/schemas/letta_stop_reason.py::StopReasonType</span>。一句话串起来：<strong>step 转圈、_step 干活、_handle_ai_response 算账、_decide_continuation 拍板，撞上预算就盖 max_steps。</strong>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>"Agent"听着玄，落到代码里就是一个带预算的 for 循环：调模型 → 跑工具 → 问"还继续吗" → 重复，最多 50 次。</strong>而那句"还继续吗"的判据反直觉地简单——它不看模型"说没说想继续"，只看模型这一轮"<strong>有没有调工具</strong>"：调了，说明活没干完，继续；没调，说明该把话筒还给用户，结束。这正是 <span class="mono">letta_v1_agent</span> 注释里 "no heartbeats"（无心跳）的精髓：上一代要靠模型自己在参数里举手要"心跳"才续步（第 15 课细讲），V3 把这层全省了，只认一个客观信号。还有一处工程细节是"可恢复性"的关键：<strong>先落库，再流式</strong>（<span class="mono">_checkpoint_messages</span> 的注释明说"持久化要在流式之前"）。哪怕进程在<strong>把这一步结果流式吐回去时</strong>崩了，这一步的消息（连同已执行的工具副作用）也早已落库——下次读档就能接着跑，不会把同一步的工具再跑一遍（正好呼应第 13 课那张"存档"）。<strong>朴素的循环、客观的判据、先存后吐的纪律——三样加起来，就是 V3 "稳"的全部秘密。</strong>
</div>

<h2>停下来的理由：StopReasonType</h2>
<p>循环每次停下，都会盖一个"停因"章——<span class="mono">StopReasonType</span>（<span class="mono">letta/schemas/letta_stop_reason.py</span>，一个字符串枚举）。它不只是给人看的标签：<span class="mono">LettaStopReason.run_status</span> 会把停因映射成这次运行的<strong>最终状态</strong>（<span class="mono">completed / failed / cancelled</span>），决定调用方看到的是"成功收尾"还是"出错了"。</p>

<p>最常见的两个停因，正好对应循环的两种正常退出：<span class="mono">end_turn</span>（模型这轮没调工具、正常把话筒交还用户）和 <span class="mono">max_steps</span>（跑满 50 步的预算上限）。注意——<span class="mono">max_steps</span> 映射的是 <strong>completed</strong>，不是 failed：撞上限是"按规矩到点下班"，不算崩溃。</p>

<table class="t">
  <tr><th>停因 StopReasonType</th><th>什么时候触发</th><th>run_status</th></tr>
  <tr><td class="mono">end_turn</td><td>这轮没调工具，正常收尾</td><td>completed</td></tr>
  <tr><td class="mono">tool_rule</td><td>调到了"终止工具"（第 16 课）</td><td>completed</td></tr>
  <tr><td class="mono">max_steps</td><td>跑满 50 步预算上限</td><td>completed</td></tr>
  <tr><td class="mono">requires_approval</td><td>工具需人工审批，暂停等批准</td><td>completed</td></tr>
  <tr><td class="mono">max_tokens_exceeded</td><td>模型这轮因长度被截断（<span class="mono">finish_reason=length</span>）</td><td>failed</td></tr>
  <tr><td class="mono">cancelled</td><td>运行被外部取消</td><td>cancelled</td></tr>
  <tr><td class="mono">error / llm_api_error / …</td><td>模型出错、工具非法、响应无效等</td><td>failed</td></tr>
</table>

<div class="note info"><span class="ni">📌</span><span class="nx">把停因按 <span class="mono">run_status</span> 分三堆记最省力：<strong>completed</strong> 那堆都是"正常下班"——<span class="mono">end_turn / max_steps / tool_rule / requires_approval</span>；<strong>failed</strong> 那堆是"出岔子"——<span class="mono">error / invalid_tool_call / max_tokens_exceeded …</span>；<strong>cancelled</strong> 单独一个。撞上限算 completed 这点最反直觉，记住它。</span></div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>别把 <span class="mono">step()</span> 当成流式接口。</strong><span class="mono">step()</span>（<span class="mono">letta_agent_v3.py::step</span>）不是边跑边吐字给前端的——它在内部把每个 <span class="mono">_step</span> 生成器抽干、攒进一个列表，循环结束后<strong>统一返回一个 <span class="mono">LettaResponse</span></strong>（完整响应）。真正"流式吐字"的是另一个方法 <span class="mono">stream(...)</span>，两者别混为一谈。常见的错觉是：看到 <span class="mono">_step</span> 里有 <span class="mono">async for ... yield</span> 就以为整个 <span class="mono">step()</span> 在流式——其实那个 <span class="mono">yield</span> 只是 <span class="mono">_step</span> 把消息交给 <span class="mono">step()</span> 的<strong>内部管道</strong>，<span class="mono">step()</span> 拿到后是 append 进列表、不是转发给客户端。一句话收尾：<strong><span class="mono">_step</span> 的 yield 是"内部传话"，<span class="mono">stream()</span> 才是"对外直播"，<span class="mono">step()</span> 是"录好再交片"。</strong>
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>为什么要"先落库、再流式"？</summary><div class="acc-body">
<p><strong>示例：</strong>用户问了个问题，模型调了工具、正吐着回复，进程突然崩了。如果是"先吐字、后落库"，这半截工作就全丢了，重来一遍还可能扣两次费、发两次邮件。</p>
<p><strong>为什么这样设计：</strong>V3 在 <span class="mono">_step</span> 里把顺序定死成"先 <span class="mono">_checkpoint_messages</span> 落库，再 <span class="mono">yield</span> 流式"。源码注释原话——"持久化要发生在流式之前，以最小化 agent 进入不一致状态的概率"。这样哪怕流到一半崩了，这一步的消息已经在 <span class="mono">AgentState</span> 里，下次读档能接着跑，状态不会被弄脏。</p>
<p><strong>源码在哪：</strong><span class="mono">letta_agent_v3.py::_step</span> 末尾的 <span class="mono">_checkpoint_messages</span> 调用；存档本身见第 13 课的 <span class="mono">AgentState</span>。</p>
<p><strong>还有什么替代：</strong>先流后存——延迟更低，但崩溃就丢状态、还可能重复副作用。Letta 选了"稳"压"快"。</p>
</div></details>

<details class="accordion"><summary><span class="mono">max_steps = 50</span> 到底防的是什么？</summary><div class="acc-body">
<p><strong>示例：</strong>模型陷入"调工具 → 看结果 → 再调同一个工具 → ……"的自我循环，停不下来。没有上限的话，它能一直烧 token、一直占着这个请求。</p>
<p><strong>为什么这样设计：</strong><span class="mono">DEFAULT_MAX_STEPS = 50</span>（<span class="mono">constants.py</span>）就是给循环装的"保险丝"。跑满 50 圈还没自然收尾，<span class="mono">step()</span> 主动盖上 <span class="mono">StopReasonType.max_steps</span> 退出。关键是——这个停因映射的 <span class="mono">run_status</span> 是 <strong>completed</strong>，不是 failed：到点下班是预期内的保护，不当成错误。</p>
<p><strong>源码在哪：</strong><span class="mono">letta_agent_v3.py::step</span> 里 <span class="mono">i == max_steps - 1</span> 的兜底；映射见 <span class="mono">letta_stop_reason.py::LettaStopReason.run_status</span>。</p>
<p><strong>还有什么替代：</strong>不设上限——一个跑飞的 agent 就能拖垮服务、烧光预算。50 是"够用又不至于失控"的工程折中。</p>
</div></details>

<details class="accordion"><summary><span class="mono">_step</span> 里那层 "撑爆 → 压缩 → 重试" 是干嘛的？</summary><div class="acc-body">
<p><strong>示例：</strong>消息越堆越多，这一轮喂给模型时撑爆了上下文窗口，LLM 直接报 <span class="mono">ContextWindowExceededError</span>。</p>
<p><strong>为什么这样设计：</strong><span class="mono">_step</span> 把 <span class="mono">invoke_llm</span> 裹在一个重试循环里：一旦抓到 <span class="mono">ContextWindowExceededError</span>，就调 <span class="mono">self.compact(...)</span> 把历史压一压（正是第 12 课的压缩）、重建系统提示，然后重试这次调用。于是"窗口压力"被悄悄消化在循环内部，外层 <span class="mono">step()</span> 基本无感。</p>
<p><strong>源码在哪：</strong><span class="mono">letta_agent_v3.py::_step</span> 的 <span class="mono">except ContextWindowExceededError</span> 分支；压缩逻辑见 <span class="mono">services/summarizer/compact.py::compact_messages</span>（第 12 课）。</p>
<p><strong>还有什么替代：</strong>直接报错给用户——体验差。把压缩接进循环、让 agent 自己"喘口气再继续"，是更顺滑的解法。</p>
</div></details>

<details class="accordion"><summary>模型一轮调了好几个工具（并行），循环怎么算？</summary><div class="acc-body">
<p><strong>示例：</strong>模型一次性发起 3 个工具调用（并行）。每个工具各自算一遍"要不要继续"，会不会有的说停、有的说继续，打架？</p>
<p><strong>为什么这样设计：</strong><span class="mono">_handle_ai_response</span> 统一处理单个与并行工具调用：逐个校验、执行、再各自跑 <span class="mono">_decide_continuation</span>。但只要这批里没有谁触发"终止工具（<span class="mono">tool_rule</span>）"或"第 50 步（<span class="mono">max_steps</span>）"这类硬停，它就强制 <span class="mono">aggregate_continue = True</span>——也就是说，并行调用<strong>默认续一圈</strong>，好让模型回头把多个工具的结果汇总成一段话。</p>
<p><strong>源码在哪：</strong><span class="mono">letta_agent_v3.py::_handle_ai_response</span> 聚合续步那段（<span class="mono">has_terminal</span> / <span class="mono">is_max_steps</span> 的判断）。</p>
<p><strong>还有什么替代：</strong>任一工具说停就停——可模型还没机会把并行结果讲给用户。默认续步更合直觉。</p>
</div></details>

<h2>下一站</h2>
<p>这一课我们把 V3 引擎拆到了底：<span class="mono">step()</span> 是带预算的 for 循环，一次 <span class="mono">_step</span> 做三件事（调模型、跑工具、落库），续步与否由 <span class="mono">_decide_continuation</span> 用"调没调工具"一锤定音，停下来时盖一个 <span class="mono">StopReasonType</span>。三件事焊进脑子，agent "跑起来"就不再神秘。</p>

<p>但有个对照一直没展开：上一代 V2 不是靠"调没调工具"续步的，而是靠模型在参数里举手要"心跳"（<span class="mono">request_heartbeat</span>）。下一课（第 15 课）就专讲这个对照——为什么 MemGPT 当初要心跳、V3 又为什么敢把它砍掉。再往后第 16 课，拆 <span class="mono">_decide_continuation</span> 反复点到、却一直没细说的那套 <span class="mono">tool_rules</span>（终止 / 必调 / 审批）。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">一句话带走：<strong><span class="mono">step()</span> 是带预算的 for 循环，一次 <span class="mono">_step</span> = 调模型 + 跑工具 + 落库，续步只看"这轮调没调工具"。</strong>把这三句记牢，第四部分剩下的循环细节都能挂回到它们身上。</span></div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>step() = 带预算的 for 循环</strong>：<span class="mono">for i in range(max_steps)</span>，<span class="mono">DEFAULT_MAX_STEPS = 50</span>；每圈抽干一个 <span class="mono">_step</span>，循环结束返回<strong>一个</strong> <span class="mono">LettaResponse</span>。</li>
    <li><strong>一次 _step = 三件事</strong>：一次 LLM 调用 + 工具执行 + 落库（拿有效工具 → 刷新消息 → 调模型 → <span class="mono">_handle_ai_response</span> → <span class="mono">_checkpoint_messages</span> → yield）。</li>
    <li><strong>续步规则</strong>（<span class="mono">_decide_continuation</span>）：没调工具 → 结束（<span class="mono">end_turn</span>）；调了工具 → 继续。硬覆盖：终止工具 → <span class="mono">tool_rule</span> 停、退出前必调 → 续、第 50 步 → <span class="mono">max_steps</span> 停、要审批 → <span class="mono">requires_approval</span>。</li>
    <li><strong>先落库再流式</strong>：<span class="mono">_checkpoint_messages</span> 注释"持久化要在流式之前"，保证半路崩了也能读档续跑（呼应第 13 课）。</li>
    <li><strong>撑爆就压缩重试</strong>：<span class="mono">_step</span> 里 LLM 调用裹着 <span class="mono">except ContextWindowExceededError → compact → 重试</span>（接上第 12 课）。</li>
    <li><strong>step() 不流式</strong>：返回 <span class="mono">LettaResponse</span>；流式是另一个 <span class="mono">stream()</span>。</li>
    <li><strong>源码</strong>：<span class="mono">letta_agent_v3.py::step / _step / _handle_ai_response / _decide_continuation</span>、<span class="mono">constants.py::DEFAULT_MAX_STEPS</span>、<span class="mono">letta_stop_reason.py::StopReasonType</span>。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Last lesson we stood at the factory door: a "save file" called <strong>AgentState</strong> is handed in, <span class="mono">AgentLoop.load</span> reads the <span class="mono">agent_type</span> column, and picks the engine that should run this time — on the default line, the pick is the third-generation <strong>LettaAgentV3</strong>. But the factory only "picks"; it never says how the engine actually <strong>turns</strong>.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
This lesson lifts the lid on the V3 engine. There's no magic inside, just a plain <strong>for loop</strong>: call the model once → execute tools → ask "keep going?" → run it again, up to 50 times. And the criterion behind that "keep going?" is counterintuitively simple — it doesn't read whether the model "feels like continuing," only whether the model <strong>called a tool</strong> this round. Finish this lesson and you hold the whole truth of how an agent "runs."</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Picture V3's loop as a worker on an assembly line.</strong> A conveyor belt runs in front of the worker: each part that arrives (one step) gets one thing done — read the blueprint, fit it on, then look up to check "is there more work behind it." More work → fit the next one; none → hand the station back to you (the user). But the worker has one iron rule: <strong>at most 50 a day</strong>, and at the limit they must clock out, so there's no endless overtime. The neatest bit is how they judge "is there more": not by asking "do I still feel like it," but by checking "did I just <strong>reach for a tool</strong> this round" — reached for one, and the sentence isn't finished, the job isn't done, so take another lap; this round only talked and touched no tool, so it's wrapping up, hand the mic back to you. The whole line turns like this: <strong>grab work → do work → check if there's a next piece → at most 50, then off shift.</strong>
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>One line for this lesson: <span class="mono">step()</span> is a budgeted for loop, and each lap drains one <span class="mono">_step</span>.</strong> The skeleton of <span class="mono">step()</span> (<span class="mono">letta_agent_v3.py::step</span>) is just <span class="mono">for i in range(max_steps)</span>, where <span class="mono">max_steps</span> defaults to <span class="mono">DEFAULT_MAX_STEPS = 50</span>; each lap drains one <span class="mono">_step</span> async generator (<span class="mono">async for chunk</span>), and when the loop ends it returns <strong>one</strong> <span class="mono">LettaResponse</span>. A single <span class="mono">_step</span> does three things: <strong>one LLM call, tool execution, and persisting the result</strong> (get valid tools → refresh messages → call the model → <span class="mono">_handle_ai_response</span> → persist → yield). Whether to step again is settled by <span class="mono">_decide_continuation</span>, whose rule fits in one sentence — "no tool call → end, tool call → continue" — plus a few hard overrides (terminal tool / required-before-exit / hitting 50 steps / needs approval). Remember these three things — <strong>the for loop, one _step, the continuation rule</strong> — and V3's loop is fully taken apart.
</div>

<h2>step(): a budgeted for loop</h2>
<p>Start with the outermost layer. Many people imagine the "agent loop" is some intricate state machine, but the skeleton of <span class="mono">step()</span> (<span class="mono">letta_agent_v3.py::step</span>) is surprisingly plain: just one <span class="mono">for i in range(max_steps)</span>. Each lap calls a <span class="mono">_step</span> and drains the messages it yields into a list; when the loop finishes, it packs that list into one <span class="mono">LettaResponse</span> and returns it.</p>

<div class="note tip"><span class="ni">💡</span><span class="nx">The default for <span class="mono">max_steps</span> lives in <span class="mono">constants.py::DEFAULT_MAX_STEPS = 50</span>. This "budget" is the loop's <strong>safety rope</strong> — a later section is devoted to what exactly it guards against.</span></div>

<p>The real work each lap is <span class="mono">self._step(...)</span>, an <strong>async generator</strong>. <span class="mono">step()</span> uses <span class="mono">async for chunk in response</span> to drain it piece by piece, appending each chunk (a <span class="mono">LettaMessage</span>) to the result list. Once it's drained, it glances at the <span class="mono">self.should_continue</span> switch: true → on to the next lap, false → <span class="mono">break</span>.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Enter lap i</h4><p>Still within budget (<span class="mono">i &lt; 50</span>)? run; exhausted, exit.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Run one _step</h4><p>One LLM call + tool execution; <span class="mono">async for</span> drains its messages into the list.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>should_continue?</h4><p>Did this round call a tool? This switch is written by <span class="mono">_decide_continuation</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Yes / No</h4><p>Yes → back to the top for another lap; No → <span class="mono">break</span> out of the loop.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>i == 49 fallback</h4><p>Ran the last lap with no stop reason set → stamp <span class="mono">max_steps</span>.</p></div></div>
</div>

<div class="note info"><span class="ni">📌</span><span class="nx">That <span class="mono">should_continue</span> switch isn't computed by <span class="mono">step()</span> itself — it's written inside <span class="mono">_step</span> (more precisely, <span class="mono">_handle_ai_response</span> computes the triple <span class="mono">(new messages, should_continue, stop_reason)</span> all at once). <span class="mono">step()</span> only <strong>reads</strong> the switch.</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">step main loop (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">step</span>(self, input_messages, max_steps=DEFAULT_MAX_STEPS, ...) -> LettaResponse:
    msgs = []
    <span class="kw">for</span> i <span class="kw">in</span> <span class="fn">range</span>(max_steps):          <span class="cm"># budget: at most 50 laps</span>
        response = self.<span class="fn">_step</span>(...)        <span class="cm"># one LLM + tool, async generator</span>
        <span class="kw">async for</span> chunk <span class="kw">in</span> response:    <span class="cm"># drain the messages this lap yields</span>
            msgs.<span class="fn">append</span>(chunk)
        <span class="kw">if not</span> self.should_continue:      <span class="cm"># the switch _step wrote</span>
            <span class="kw">break</span>                         <span class="cm"># no tool call -> wrap up</span>
        <span class="kw">if</span> i == max_steps - 1 <span class="kw">and</span> self.stop_reason <span class="kw">is None</span>:
            self.stop_reason = <span class="fn">LettaStopReason</span>(StopReasonType.max_steps)
    <span class="cm"># after the loop: no stop reason set -> default end_turn, then pack into one response</span>
    <span class="kw">return</span> <span class="fn">LettaResponse</span>(messages=msgs, stop_reason=self.stop_reason <span class="kw">or</span> end_turn)
</pre></div>

<p>Two bits of cleanup after the loop are worth remembering. First, if it reaches the last lap (<span class="mono">i == max_steps - 1</span>) with no stop reason ever set, <span class="mono">step()</span> actively stamps a <span class="mono">StopReasonType.max_steps</span> — the "budget exhausted" marker. Second, after the whole loop, if there's still no stop reason at all, it defaults to <span class="mono">StopReasonType.end_turn</span> (a normal finish).</p>

<h2>One _step: LLM call + tool execution + persist</h2>
<p>With the outer layer unpacked, let's drill into each lap's <span class="mono">_step</span> (<span class="mono">letta_agent_v3.py::_step</span>). The source spells out its role plainly — "one LLM call and tool execution" — the async generator that all the public methods (<span class="mono">step</span> / <span class="mono">stream</span>) funnel into. A single <span class="mono">_step</span> does exactly three things: <strong>call the model once, execute tools, and persist the result.</strong></p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Valid tools + force?</h4><p><span class="mono">_get_valid_tools()</span>, then ask <span class="mono">tool_rules_solver.should_force_tool_call()</span>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Refresh messages</h4><p><span class="mono">_refresh_messages</span> wipes the stale inner monologue; <strong>doesn't rebuild the system prompt</strong> (keeps the prefix cache).</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Call the LLM</h4><p><span class="mono">llm_adapter.invoke_llm(...)</span>, wrapped in an "overflow → compact → retry" layer.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>_handle_ai_response</h4><p>Validate and execute tools, compute <span class="mono">(new messages, should_continue, stop_reason)</span>.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Persist</h4><p><span class="mono">_checkpoint_messages</span> writes this step's messages to the DB — <strong>persist first, then stream</strong>.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>yield</h4><p>Hand the messages chunk by chunk to the outer <span class="mono">step()</span> to append.</p></div></div>
</div>

<div class="note info"><span class="ni">👉</span><span class="nx">Step 2's "don't rebuild the system prompt" is a performance detail: the system prompt is the frontmost, most stable segment of the message list, and keeping it unchanged lets the model server's <strong>prefix cache</strong> (lessons 5, 9) hit. The system prompt is only rebuilt <strong>after compaction or a reset</strong>.</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">_step skeleton (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">_step</span>(self, messages, ...):        <span class="cm"># async generator: one LLM + tool</span>
    valid_tools = <span class="kw">await</span> self.<span class="fn">_get_valid_tools</span>()
    force = self.tool_rules_solver.<span class="fn">should_force_tool_call</span>()
    messages = <span class="kw">await</span> self.<span class="fn">_refresh_messages</span>(messages)  <span class="cm"># wipe monologue, don't rebuild system prompt</span>
    <span class="kw">for</span> _ <span class="kw">in</span> <span class="fn">range</span>(max_retries + <span class="nb">1</span>):       <span class="cm"># overflow -> compact -> retry (bounded)</span>
        <span class="kw">try</span>:
            <span class="kw">async for</span> chunk <span class="kw">in</span> llm_adapter.<span class="fn">invoke_llm</span>(messages, valid_tools):
                <span class="kw">yield</span> chunk
            <span class="kw">break</span>
        <span class="kw">except</span> ContextWindowExceededError:   <span class="cm"># the compaction from lesson 12</span>
            messages = <span class="kw">await</span> self.<span class="fn">compact</span>(...)
            <span class="kw">await</span> self.<span class="fn">rebuild_system_prompt_async</span>()
    new_messages, self.should_continue, self.stop_reason = \
        <span class="kw">await</span> self.<span class="fn">_handle_ai_response</span>(tool_calls, valid_tools, ...)
    <span class="kw">await</span> self.<span class="fn">_checkpoint_messages</span>(...)        <span class="cm"># persistence before streaming</span>
    <span class="kw">for</span> m <span class="kw">in</span> new_messages:
        <span class="kw">yield</span> m
</pre></div>

<div class="note tip"><span class="ni">🧠</span><span class="nx">Burn step 5's source comment in — "<strong>persistence needs to happen before streaming</strong>, to minimize chances of the agent getting into an inconsistent state." A dedicated accordion below explains why it matters so much.</span></div>

<div class="cute">
  <div class="row">
    <span class="emoji">🐹</span><span class="lab">step 3/50</span>
    <span class="arrow">→</span>
    <span class="emoji">🔁</span><span class="lab">Call a tool this round?</span>
    <span class="arrow">→</span>
    <span class="emoji">🛞</span><span class="bubble">Did → one more lap!</span>
    <span class="emoji">🛑</span><span class="bubble">Didn't → brake, stop.</span>
  </div>
  <div class="cap">The odometer on the hamster wheel reads 3/50: as long as this lap reached for a tool, pedal one more; come back empty-handed and the brakes go on</div>
</div>

<h2>Continue or stop: _decide_continuation makes the call</h2>
<p>Now for the lesson's crux: on what basis does the loop decide to "take one more step" or "wrap up"? The answer is in <span class="mono">_decide_continuation</span> (<span class="mono">letta_agent_v3.py::_decide_continuation</span>). Its docstring writes the rule as two lines, plain to the point of being counterintuitive: <strong>1. Did not call a tool? Loop ends. 2. Called a tool? Loop continues.</strong></p>

<div class="note tip"><span class="ni">💡</span><span class="nx">Where's the counterintuition? It doesn't <strong>look</strong> at whether the model said "I want to continue." It recognizes one objective fact — whether the model <strong>issued a tool call</strong> this round. Called one → there's follow-up to do (after executing the tool, the model must see the result); didn't → the model is replying directly, so hand the mic back to the user.</span></div>

<p>Why must "called a tool" mean "continue"? Because a tool call is a <strong>two-stage</strong> action: the model first says "I'll call <span class="mono">search</span>," the system executes <span class="mono">search</span> and gets a result, and that result must then be <strong>fed back</strong> to the model so it can carry on. So whenever a round has a tool call, the loop must take one more lap to digest the result — which is the real meaning of "no heartbeats" in <span class="mono">letta_v1_agent</span>'s comment: it doesn't rely on the model raising its own hand for a heartbeat, only on the objective signal of "did it call a tool."</p>

<div class="flow">
  <div class="node hl"><div class="nt">Did this round call a tool?</div><div class="nd">_decide_continuation's only crux</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">No · no tool call</div><div class="nd">A "required-before-exit" tool still uncalled? yes → continue; no → stop end_turn</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Yes · called a tool</div><div class="nd">A "terminal tool"? yes → stop tool_rule; no → continue</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Hard overrides</div><div class="nd">Already step 50? → stop max_steps</div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">_decide_continuation (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">_decide_continuation</span>(self, agent_state, tool_call_name,
                         tool_rule_violated, tool_rules_solver, is_final_step, finish_reason=None):
    <span class="cm"># rule: no tool -> end; tool -> continue (plus a few hard overrides)</span>
    <span class="kw">if</span> tool_call_name <span class="kw">is None</span>:                  <span class="cm"># no tool call this round</span>
        uncalled = tool_rules_solver.<span class="fn">get_uncalled_required_tools</span>(...)
        <span class="kw">if</span> uncalled <span class="kw">and not</span> is_final_step:
            <span class="kw">return</span> <span class="nb">True</span>, nudge, <span class="nb">None</span>           <span class="cm"># required-before-exit remains -> continue + nudge</span>
        <span class="kw">if</span> finish_reason == <span class="st">"length"</span>:
            <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(max_tokens_exceeded)
        <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(end_turn)      <span class="cm"># normal finish</span>
    <span class="kw">else</span>:                                       <span class="cm"># a tool was called this round</span>
        <span class="kw">if</span> tool_rule_violated:
            <span class="kw">return</span> <span class="nb">True</span>, nudge, <span class="nb">None</span>           <span class="cm"># violation continues too (with a correction nudge)</span>
        tool_rules_solver.<span class="fn">register_tool_call</span>(tool_call_name)
        <span class="kw">if</span> tool_rules_solver.<span class="fn">is_terminal_tool</span>(tool_call_name):
            <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(tool_rule)   <span class="cm"># terminal tool -> stop</span>
        <span class="kw">if</span> is_final_step:
            <span class="kw">return</span> <span class="nb">False</span>, <span class="nb">None</span>, <span class="fn">stop</span>(max_steps)   <span class="cm"># reached step 50 -> stop</span>
        <span class="kw">return</span> <span class="nb">True</span>, nudge, <span class="nb">None</span>               <span class="cm"># otherwise continue</span>
</pre></div>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">A few <strong>hard overrides</strong> hide here, don't miss them: even though the rule says "no tool → end," as long as a <span class="mono">required_before_exit</span> (must be called at least once before exit) tool is still uncalled, the loop is forced to continue and nudges the model to call it; conversely, even if a tool was called, hitting a "terminal tool" or "step 50" forces a stop. <strong>The rule is the skeleton, the overrides are the patches.</strong></span></div>

<div class="card detail">
  <div class="tag">🔬 Down to the code</div>
  <strong>Four anchors, one through-line.</strong> The outer loop is <span class="mono">letta_agent_v3.py::step</span> (<span class="mono">for i in range(max_steps)</span>, returns a <span class="mono">LettaResponse</span>); each lap's <span class="mono">letta_agent_v3.py::_step</span> is the "one LLM + tool + persist" async generator; tool validation and execution, plus that continuation triple, live in <span class="mono">letta_agent_v3.py::_handle_ai_response</span>; the continuation criterion is in <span class="mono">letta_agent_v3.py::_decide_continuation</span>. Add two constant-level anchors: the budget <span class="mono">constants.py::DEFAULT_MAX_STEPS = 50</span>, and the stop reason <span class="mono">letta/schemas/letta_stop_reason.py::StopReasonType</span>. Strung into one line: <strong><span class="mono">step</span> turns the laps, <span class="mono">_step</span> does the work, <span class="mono">_handle_ai_response</span> settles the accounts, <span class="mono">_decide_continuation</span> makes the call, and hitting the budget stamps <span class="mono">max_steps</span>.</strong>
</div>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  <strong>"Agent" sounds mystical, but in code it's a budgeted for loop: call the model → run a tool → ask "keep going?" → repeat, up to 50 times.</strong> And that "keep going?" criterion is counterintuitively simple — it doesn't look at whether the model "said it wants to continue," only at whether the model "<strong>called a tool</strong>" this round: called one → the work isn't done, continue; didn't → time to hand the mic back to the user, end. This is the essence of "no heartbeats" in <span class="mono">letta_v1_agent</span>'s comment: the previous generation needed the model to raise its hand for a "heartbeat" in the parameters to step again (lesson 15 goes deep), while V3 drops that whole layer and trusts a single objective signal. One more engineering detail is the key to "recoverability": <strong>persist first, then stream</strong> (<span class="mono">_checkpoint_messages</span>'s comment plainly says "persistence needs to happen before streaming"). Even if the process crashes <strong>while streaming this step's results back</strong>, this step's messages (and any tool side effects already executed) are already persisted — the next load resumes without re-running the same step's tools (echoing lesson 13's "save file"). <strong>A plain loop, an objective criterion, and the persist-before-stream discipline — those three together are the whole secret of V3's steadiness.</strong>
</div>

<h2>Reasons to stop: StopReasonType</h2>
<p>Every time the loop stops, it stamps a "stop reason" — <span class="mono">StopReasonType</span> (<span class="mono">letta/schemas/letta_stop_reason.py</span>, a string enum). It's more than a human-facing label: <span class="mono">LettaStopReason.run_status</span> maps the stop reason to this run's <strong>final status</strong> (<span class="mono">completed / failed / cancelled</span>), deciding whether the caller sees "finished cleanly" or "something errored."</p>

<p>The two most common stop reasons match the loop's two normal exits: <span class="mono">end_turn</span> (the model called no tool this round and hands the mic back) and <span class="mono">max_steps</span> (the 50-step budget cap was reached). Note — <span class="mono">max_steps</span> maps to <strong>completed</strong>, not failed: hitting the cap is "clocking out on schedule," not a crash.</p>

<table class="t">
  <tr><th>StopReasonType</th><th>When it fires</th><th>run_status</th></tr>
  <tr><td class="mono">end_turn</td><td>no tool this round, normal finish</td><td>completed</td></tr>
  <tr><td class="mono">tool_rule</td><td>a "terminal tool" was called (lesson 16)</td><td>completed</td></tr>
  <tr><td class="mono">max_steps</td><td>ran the 50-step budget cap</td><td>completed</td></tr>
  <tr><td class="mono">requires_approval</td><td>a tool needs human approval, paused for it</td><td>completed</td></tr>
  <tr><td class="mono">max_tokens_exceeded</td><td>model truncated by length this round (<span class="mono">finish_reason=length</span>)</td><td>failed</td></tr>
  <tr><td class="mono">cancelled</td><td>the run was cancelled from outside</td><td>cancelled</td></tr>
  <tr><td class="mono">error / llm_api_error / …</td><td>model error, illegal tool, invalid response, etc.</td><td>failed</td></tr>
</table>

<div class="note info"><span class="ni">📌</span><span class="nx">The easiest way to hold the stop reasons is in three piles by <span class="mono">run_status</span>: the <strong>completed</strong> pile is all "normal clock-out" — <span class="mono">end_turn / max_steps / tool_rule / requires_approval</span>; the <strong>failed</strong> pile is "something went wrong" — <span class="mono">error / invalid_tool_call / max_tokens_exceeded …</span>; <strong>cancelled</strong> stands alone. The cap counting as completed is the most counterintuitive — remember it.</span></div>

<div class="card warn">
  <div class="tag">⚠️ Common pitfalls</div>
  <strong>Don't treat <span class="mono">step()</span> as a streaming interface.</strong> <span class="mono">step()</span> (<span class="mono">letta_agent_v3.py::step</span>) does not spit tokens to the frontend as it runs — internally it drains each <span class="mono">_step</span> generator, gathers the messages into a list, and after the loop returns <strong>one <span class="mono">LettaResponse</span></strong> (the full response). The thing that actually "streams tokens" is a separate method, <span class="mono">stream(...)</span>; don't conflate the two. The common illusion: seeing <span class="mono">async for ... yield</span> inside <span class="mono">_step</span> makes you think the whole <span class="mono">step()</span> streams — but that <span class="mono">yield</span> is only <span class="mono">_step</span>'s <strong>internal pipe</strong> handing messages to <span class="mono">step()</span>, which then appends them to a list rather than forwarding them to the client. One line to close: <strong><span class="mono">_step</span>'s yield is "internal relay," <span class="mono">stream()</span> is "broadcasting live to the outside," and <span class="mono">step()</span> is "record it, then deliver the finished cut."</strong>
</div>

<h2>Digging a little deeper</h2>

<details class="accordion"><summary>Why "persist first, then stream"?</summary><div class="acc-body">
<p><strong>Example:</strong> a user asks a question, the model calls a tool and is mid-stream on its reply, and the process suddenly crashes. With "stream first, persist later," this half-finished work is all lost, and redoing it might double-charge or send two emails.</p>
<p><strong>Why it's designed this way:</strong> V3 nails the order inside <span class="mono">_step</span> to "first <span class="mono">_checkpoint_messages</span> to persist, then <span class="mono">yield</span> to stream." The source comment puts it verbatim — "persistence needs to happen before streaming, to minimize chances of the agent getting into an inconsistent state." So even if streaming dies halfway, this step's messages are already in <span class="mono">AgentState</span>, the next load resumes, and the state never gets dirtied.</p>
<p><strong>Where in the source:</strong> the <span class="mono">_checkpoint_messages</span> call near the end of <span class="mono">letta_agent_v3.py::_step</span>; the save itself is lesson 13's <span class="mono">AgentState</span>.</p>
<p><strong>What's the alternative:</strong> stream-then-persist — lower latency, but a crash loses the state and may duplicate side effects. Letta picked "steady" over "fast."</p>
</div></details>

<details class="accordion"><summary>What does <span class="mono">max_steps = 50</span> actually guard against?</summary><div class="acc-body">
<p><strong>Example:</strong> the model falls into a "call a tool → see the result → call the same tool again → …" self-loop and can't stop. With no cap, it would burn tokens forever and hold the request hostage forever.</p>
<p><strong>Why it's designed this way:</strong> <span class="mono">DEFAULT_MAX_STEPS = 50</span> (<span class="mono">constants.py</span>) is the fuse fitted on the loop. Run a full 50 laps without a natural finish and <span class="mono">step()</span> actively stamps <span class="mono">StopReasonType.max_steps</span> and exits. The key part — this stop reason maps to a <span class="mono">run_status</span> of <strong>completed</strong>, not failed: clocking out on schedule is expected protection, not an error.</p>
<p><strong>Where in the source:</strong> the <span class="mono">i == max_steps - 1</span> fallback in <span class="mono">letta_agent_v3.py::step</span>; the mapping is in <span class="mono">letta_stop_reason.py::LettaStopReason.run_status</span>.</p>
<p><strong>What's the alternative:</strong> set no cap — one runaway agent could drag down the service and burn the whole budget. 50 is the "enough, but not out of control" engineering compromise.</p>
</div></details>

<details class="accordion"><summary>What's that "overflow → compact → retry" layer inside <span class="mono">_step</span> for?</summary><div class="acc-body">
<p><strong>Example:</strong> messages keep piling up, and this round's feed to the model overflows the context window, so the LLM raises <span class="mono">ContextWindowExceededError</span> outright.</p>
<p><strong>Why it's designed this way:</strong> <span class="mono">_step</span> wraps <span class="mono">invoke_llm</span> in a retry loop: the moment it catches <span class="mono">ContextWindowExceededError</span>, it calls <span class="mono">self.compact(...)</span> to squeeze the history down (exactly lesson 12's compaction), rebuilds the system prompt, and retries the call. So "window pressure" gets quietly digested inside the loop, and the outer <span class="mono">step()</span> barely notices.</p>
<p><strong>Where in the source:</strong> the <span class="mono">except ContextWindowExceededError</span> branch of <span class="mono">letta_agent_v3.py::_step</span>; the compaction logic is in <span class="mono">services/summarizer/compact.py::compact_messages</span> (lesson 12).</p>
<p><strong>What's the alternative:</strong> error straight out to the user — a poor experience. Wiring compaction into the loop, letting the agent "catch its breath and continue," is the smoother fix.</p>
</div></details>

<details class="accordion"><summary>The model calls several tools in one round (in parallel) — how does the loop count that?</summary><div class="acc-body">
<p><strong>Example:</strong> the model issues 3 tool calls at once (in parallel). Each tool runs its own "continue or not" check — could some say stop while others say continue, and clash?</p>
<p><strong>Why it's designed this way:</strong> <span class="mono">_handle_ai_response</span> handles single and parallel tool calls uniformly: validate each, execute, then run <span class="mono">_decide_continuation</span> for each. But as long as nobody in the batch trips a hard stop like a "terminal tool (<span class="mono">tool_rule</span>)" or "step 50 (<span class="mono">max_steps</span>)," it forces <span class="mono">aggregate_continue = True</span> — that is, parallel calls <strong>continue one more lap by default</strong>, so the model can come back and summarize the several tools' results into one passage.</p>
<p><strong>Where in the source:</strong> the aggregate-continuation part of <span class="mono">letta_agent_v3.py::_handle_ai_response</span> (the <span class="mono">has_terminal</span> / <span class="mono">is_max_steps</span> checks).</p>
<p><strong>What's the alternative:</strong> stop the moment any tool says stop — but then the model never gets to tell the user the parallel results. Continuing by default is the more intuitive choice.</p>
</div></details>

<h2>Next stop</h2>
<p>This lesson took the V3 engine apart to the bottom: <span class="mono">step()</span> is a budgeted for loop, one <span class="mono">_step</span> does three things (call the model, run tools, persist), continuation is settled by <span class="mono">_decide_continuation</span> with "did it call a tool" in a single stroke, and on stopping it stamps a <span class="mono">StopReasonType</span>. Weld those three things into your head and an agent "running" stops being mysterious.</p>

<p>But one comparison stayed unopened: the previous generation, V2, didn't continue based on "did it call a tool," but on the model raising its hand for a "heartbeat" in the parameters (<span class="mono">request_heartbeat</span>). The next lesson (15) is all about this contrast — why MemGPT needed heartbeats back then, and why V3 dares to cut them. Further on, lesson 16 unpacks the <span class="mono">tool_rules</span> (terminal / required / approval) that <span class="mono">_decide_continuation</span> kept pointing at but never detailed.</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">Take one line away: <strong><span class="mono">step()</span> is a budgeted for loop, one <span class="mono">_step</span> = call the model + run the tool + persist, and continuation only looks at "did this round call a tool."</strong> Hold these three sentences and the rest of Part 4's loop details all hang back onto them.</span></div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>step() = a budgeted for loop</strong>: <span class="mono">for i in range(max_steps)</span>, <span class="mono">DEFAULT_MAX_STEPS = 50</span>; each lap drains one <span class="mono">_step</span>, and the loop ends by returning <strong>one</strong> <span class="mono">LettaResponse</span>.</li>
    <li><strong>one _step = three things</strong>: one LLM call + tool execution + persist (get valid tools → refresh messages → call the model → <span class="mono">_handle_ai_response</span> → <span class="mono">_checkpoint_messages</span> → yield).</li>
    <li><strong>the continuation rule</strong> (<span class="mono">_decide_continuation</span>): no tool call → end (<span class="mono">end_turn</span>); tool call → continue. Hard overrides: terminal tool → stop <span class="mono">tool_rule</span>, required-before-exit → continue, step 50 → stop <span class="mono">max_steps</span>, needs approval → <span class="mono">requires_approval</span>.</li>
    <li><strong>persist before stream</strong>: <span class="mono">_checkpoint_messages</span>'s comment "persistence needs to happen before streaming" guarantees a mid-way crash can still resume from the save (echoing lesson 13).</li>
    <li><strong>overflow → compact → retry</strong>: the LLM call in <span class="mono">_step</span> is wrapped in <span class="mono">except ContextWindowExceededError → compact → retry</span> (continuing lesson 12).</li>
    <li><strong>step() doesn't stream</strong>: it returns a <span class="mono">LettaResponse</span>; streaming is a separate <span class="mono">stream()</span>.</li>
    <li><strong>source</strong>: <span class="mono">letta_agent_v3.py::step / _step / _handle_ai_response / _decide_continuation</span>, <span class="mono">constants.py::DEFAULT_MAX_STEPS</span>, <span class="mono">letta_stop_reason.py::StopReasonType</span>.</li>
  </ul>
</div>
""",
}

# quiz seeds (en-phase agent to expand into quizzes.py):
#  - what request_heartbeat is & which tools get it (non-terminal, required boolean)
#  - how the old loop continues (model sets true -> framework injects a heartbeat user-msg)
#  - how V3 decides (a tool was called -> continue; ignores/strips heartbeat)
#  - what bug class deleting it kills (model-forgot-to-set-it silence)
LESSON_15 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课拆 V3 循环时，我们撞见一句反直觉的判据：续不续步，<strong>不看模型想不想继续，只看这一轮有没有调工具</strong>。当时埋了个悬念——<span class="mono">letta_v1_agent</span> 注释里那句 "no heartbeats"（无心跳）到底拿掉了什么？这一课就来还这笔账。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
这是一堂<strong>设计演化课</strong>。老的 MemGPT、元老 <span class="mono">Agent</span>、第二代 <span class="mono">LettaAgentV2</span> 都靠一个叫 <span class="mono">request_heartbeat</span> 的开关续步：模型得在工具调用里<strong>自己举手</strong>说"我还要继续"。第三代 V3 把这个开关整个删掉了。一删一留之间，藏着一条朴素的工程智慧——<strong>别把"要不要继续"这种关键决定，押在模型的自觉上。</strong></p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把两代机制想成两种对讲机。</strong>老机制是<strong>半双工对讲机</strong>：你每说完一句，必须主动加一句"完毕，请继续（over）"，对面才知道该接话；万一你忘了说这句"完毕"，线路就<strong>静默</strong>了——对面干等，你也以为在等对方，整条对话就卡死在那。新机制换了规矩：<strong>只要你还在往外递"工具单子"，线路就默认接着转</strong>，不必每次都喊"请继续"；什么时候你不再递单子、直接开口说话了，才算把话筒交还回去。老机制把"继续"的责任压在<strong>说话人记不记得喊口令</strong>上，新机制把它焊死在<strong>"有没有递单子"这个客观动作</strong>上——后者不会忘，也就不会卡死。说到底，靠谱的流水线不靠工人时时记得喊"完毕"，而靠传送带本身的机械确定性。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：老设计让<em>模型</em>决定"继续不继续"，V3 把这个决定收回给<em>框架</em>。</strong>老机制（<span class="mono">letta/agent.py</span> 的元老 <span class="mono">Agent</span>，以及 <span class="mono">LettaAgentV2</span>）给每个<strong>非终止工具</strong>都塞一个必填布尔参数 <span class="mono">request_heartbeat</span>；模型若想接着干，就得把它设成 <span class="mono">true</span>，框架随后注入一条"心跳"用户消息把控制权还给模型、续上一圈（<span class="mono">agent.py::_handle_ai_response</span> 读这个标志，<span class="mono">agent.py::step</span> 注入并续步）。工具<strong>报错</strong>时，框架还会自动补一条心跳，好让模型看见错误去补救。V3（<span class="mono">letta_agent_v3.py</span>）的洞见是：这个决定<strong>不该问模型</strong>——"这一轮调了工具"本身就是"还有后续"的可靠信号，于是 <span class="mono">_get_valid_tools</span> 传 <span class="mono">request_heartbeat=False</span>（注释 "NOTE: difference for v3"），续步判据回到上一课的 <span class="mono">_decide_continuation</span>。一个必填参数、一类心跳消息、一整类"模型忘了设"的 bug，就此一起消失。代价几乎为零——因为"调了工具"本就等价于"还要继续"，老机制那层让模型再确认一次的设计，从一开始就是冗余的。
</div>

<h2>旧设计：每个非终止工具都挂一个 request_heartbeat</h2>
<p>先认清这个开关。老机制在把工具的 JSON schema 交给模型之前，会<strong>动态地</strong>给每个工具多塞一个参数 <span class="mono">request_heartbeat</span>（布尔值），并把它列进 <span class="mono">required</span>。注入逻辑在 <span class="mono">tool_parser_helper.py::runtime_override_tool_json_schema</span>，文档字符串写得很直白——"工具会被加上一个额外的 <span class="mono">request_heartbeat</span> 参数（终止工具除外）"。</p>

<div class="note tip"><span class="ni">💡</span><span class="nx">这个参数的描述（<span class="mono">constants.py::REQUEST_HEARTBEAT_DESCRIPTION</span>）就是写给模型看的说明书：<strong>"若你想发后续消息或再调一个工具（把多个工具串起来），你必须把这个值设为 <span class="mono">True</span>；若设为 <span class="mono">False</span>（默认），执行链会在这次调用后立即结束。"</strong>——"继续"与否，明明白白交到了模型手里。</span></div>

<p>注意两个"只"字：<strong>只加给非终止工具</strong>（<span class="mono">send_message</span> 这类终止工具被排除在外，它本就该结束这一轮），而且加进去就是<strong>必填的</strong>。于是模型每调一个普通工具，都被迫表态一次"我还继不继续"。</p>

<div class="flow">
  <div class="node"><div class="nt">工具原始 schema</div><div class="nd">只有工具自身的参数</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">runtime_override_tool_json_schema</div><div class="nd">改写工具 schema 的那道关</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">旧 · 加 request_heartbeat</div><div class="nd">bool，且进 required（终止工具除外）</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">V3 · 什么都不加</div><div class="nd">传 request_heartbeat=False</div></div>
</div>

<p>为什么 MemGPT 当初要这么设计？因为模型一次只产出"一段话"，而一个任务常要连着调好几个工具——先查核心记忆、再搜归档、最后才回话。模型需要一个口子告诉框架"我这段还没完，别急着把话筒还给用户"，<span class="mono">request_heartbeat=true</span> 就是这个口子。它和第 4 课的 ReAct、内心独白一脉相承：让模型<strong>显式</strong>说出"我还要再想一步、再做一步"。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/helpers/tool_parser_helper.py</span><span class="ln">注入 request_heartbeat（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">runtime_override_tool_json_schema</span>(tool_list, response_format,
                                      request_heartbeat=<span class="nb">True</span>, terminal_tools=<span class="kw">None</span>):
    <span class="cm"># 文档：工具会被加上一个 request_heartbeat 参数（终止工具除外）</span>
    terminal_tools = terminal_tools <span class="kw">or</span> <span class="fn">set</span>()
    <span class="kw">for</span> tool_json <span class="kw">in</span> tool_list:
        <span class="kw">if</span> request_heartbeat:
            <span class="kw">if</span> tool_json[<span class="st">"name"</span>] <span class="kw">not in</span> terminal_tools:   <span class="cm"># 只加给非终止工具</span>
                tool_json[<span class="st">"parameters"</span>][<span class="st">"properties"</span>][REQUEST_HEARTBEAT_PARAM] = {
                    <span class="st">"type"</span>: <span class="st">"boolean"</span>,
                    <span class="st">"description"</span>: REQUEST_HEARTBEAT_DESCRIPTION,
                }
                <span class="kw">if</span> REQUEST_HEARTBEAT_PARAM <span class="kw">not in</span> tool_json[<span class="st">"parameters"</span>][<span class="st">"required"</span>]:
                    tool_json[<span class="st">"parameters"</span>][<span class="st">"required"</span>].<span class="fn">append</span>(REQUEST_HEARTBEAT_PARAM)  <span class="cm"># 必填</span>
    <span class="kw">return</span> tool_list
</pre></div>

<h2>旧机制怎么续步：一条"心跳"消息链</h2>
<p>参数有了，循环怎么用它续步？分三拍：模型在工具调用里带上 <span class="mono">request_heartbeat=true</span> → 框架执行完工具后，<strong>注入一条"心跳"用户消息</strong>把控制权交还模型 → 下一圈模型看着这条消息接着说。若带的是 <span class="mono">false</span>（或没带），就 <span class="mono">break</span>，把话筒还给真正的用户。</p>

<div class="note info"><span class="ni">📌</span><span class="nx">这条"心跳"消息角色是 <span class="mono">role=user</span>，但它不是真用户发的——内容前缀是 <span class="mono">NON_USER_MSG_PREFIX</span>（"[This is an automated system message hidden from the user] "），对用户<strong>隐藏</strong>。常量见 <span class="mono">constants.py::REQ_HEARTBEAT_MESSAGE</span>。</span></div>

<p>这里的关键和上一课同源：工具调用天生是<strong>两段式</strong>的——模型先说"我要调 <span class="mono">search</span>"，框架执行、拿到结果，还得把结果<strong>喂回</strong>模型让它接着说。所以"调了工具"本就意味着"还有下半场"。可老机制没有直接用上这个事实，而是<strong>多绕了一道</strong>：让模型在参数里再确认一次"我要继续"。V3 看穿了这道确认是多余的，才把它省掉。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>模型调工具</h4><p>带上 <span class="mono">request_heartbeat=true</span>，表示"我还要继续"。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>_handle_ai_response 读标志</h4><p><span class="mono">function_args.pop("request_heartbeat")</span>；字符串 "true" 归一成布尔。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>执行工具</h4><p>跑完拿结果；若<strong>报错</strong>，记下 <span class="mono">function_failed=True</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>step 注入心跳</h4><p><span class="mono">true</span> → 注入 <span class="mono">REQ_HEARTBEAT_MESSAGE</span>（role=user），<span class="mono">continue</span>。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>false → break</h4><p>没要心跳，跳出循环，收尾交还用户。</p></div></div>
</div>

<p>解析这一步发生在 <span class="mono">agent.py::Agent._handle_ai_response</span>：它把 <span class="mono">request_heartbeat</span> 从工具参数里 <span class="mono">pop</span> 出来，顺手处理"被序列化成字符串 'true'"的边角情况。工具规则还能<strong>覆盖</strong>这个标志——<span class="mono">has_children_tools</span> 强制 <span class="mono">True</span>、<span class="mono">is_terminal_tool</span> 强制 <span class="mono">False</span>、<span class="mono">is_continue_tool</span> 强制 <span class="mono">True</span>（这套规则留到第 16 课细讲）。</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">别记错落点：解析心跳标志的是 <span class="mono">Agent._handle_ai_response</span>，<strong>不是</strong> <span class="mono">inner_step</span>；真正"注入心跳消息、决定 continue/break"的是 <span class="mono">Agent.step</span>（它的文档字符串原话就是"在循环里处理基于心跳请求与函数失败的链式续步"）。</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agent.py</span><span class="ln">老链式续步（_handle_ai_response + step，简化）</span></div>
<pre><span class="cm"># _handle_ai_response：从工具参数里取出心跳标志</span>
heartbeat_request = function_args.<span class="fn">pop</span>(<span class="st">"request_heartbeat"</span>, <span class="kw">None</span>)
<span class="kw">if</span> <span class="fn">isinstance</span>(heartbeat_request, <span class="nb">str</span>) <span class="kw">and</span> heartbeat_request.<span class="fn">lower</span>() == <span class="st">"true"</span>:
    heartbeat_request = <span class="nb">True</span>             <span class="cm"># "true" 字符串归一成布尔</span>

<span class="cm"># step：根据标志决定续步还是收尾</span>
<span class="kw">if</span> function_failed:                       <span class="cm"># 工具报错 -> 自动续，让模型看错误</span>
    inject(<span class="fn">get_heartbeat</span>(FUNC_FAILED_HEARTBEAT_MESSAGE)); <span class="kw">continue</span>
<span class="kw">elif</span> heartbeat_request:                   <span class="cm"># 模型要心跳 -> 续</span>
    inject(<span class="fn">get_heartbeat</span>(REQ_HEARTBEAT_MESSAGE)); <span class="kw">continue</span>
<span class="kw">else</span>:
    <span class="kw">break</span>                                <span class="cm"># 没要心跳 -> 收尾，交还用户</span>
</pre></div>

<p>第 4 拍那条"工具报错就自动续"值得单独点出：哪怕模型<strong>没</strong>要心跳，只要工具执行<strong>失败</strong>，老机制也会强行注入一条 <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span>，把控制权还给模型——好让它看见错误、有机会补救，而不是带着一个失败的工具调用就草草收场。</p>

<div class="cellgroup">
  <div class="cg-cap">老机制的两条"控制权交还"消息，都带 <b>NON_USER_MSG_PREFIX</b> 前缀、对用户隐藏</div>
  <div class="cells">
    <span class="lab">续步</span>
    <span class="cell hl">REQ_HEARTBEAT_MESSAGE</span>
    <span class="sep">·</span>
    <span class="cell">模型设 true，归还控制权</span>
  </div>
  <div class="cells">
    <span class="lab">报错</span>
    <span class="cell hl">FUNC_FAILED_HEARTBEAT_MESSAGE</span>
    <span class="sep">·</span>
    <span class="cell">函数失败，归还控制权</span>
  </div>
  <div class="cells">
    <span class="lab">前缀</span>
    <span class="cell q">[This is an automated system message hidden from the user]</span>
  </div>
</div>

<div class="cols">
  <div class="col">
    <h4>🕰️ 老机制（Agent / V2）</h4>
    <p>schema 里有<strong>必填</strong>的 <span class="mono">request_heartbeat</span>。</p>
    <p>模型设 <span class="mono">true</span> → 注入 <span class="mono">REQ_HEARTBEAT_MESSAGE</span>（role=user）→ 续。</p>
    <p>工具报错 → 注入 <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span> → 续。</p>
    <p class="mono" style="font-size:.82rem">继续 = 模型自己举手</p>
  </div>
  <div class="col">
    <h4>🆕 V3（letta_v1_agent）</h4>
    <p>schema 里<strong>根本不加</strong> <span class="mono">request_heartbeat</span>。</p>
    <p><span class="mono">_decide_continuation</span>：这轮调了工具 → 续；没调 → 停。</p>
    <p>就算模型硬塞一个心跳参数，也被 <span class="mono">args.pop(...)</span> 默默丢掉。</p>
    <p class="mono" style="font-size:.82rem">继续 = 框架看"调没调工具"</p>
  </div>
</div>

<div class="cute">
  <div class="row">
    <span class="emoji">💓</span><span class="lab">老 · 对讲机</span>
    <span class="arrow">→</span>
    <span class="emoji">🤐</span><span class="bubble">忘喊"完毕，请继续" → 线路静默</span>
    <span class="emoji">🔁</span><span class="bubble">只要还递工具单 → 线路照转</span>
    <span class="lab">新 · 默认继续</span>
  </div>
  <div class="cap">老机制靠模型每次喊 "over, please continue"，忘了就卡死；新机制把"继续"焊在"调没调工具"上，不用喊也不会忘</div>
</div>

<h2>模型忘了设怎么办：insert_heartbeat 这块补丁</h2>
<p>把"继续"的决定交给模型，灵活，却<strong>脆弱</strong>：模型只要忘了把 <span class="mono">request_heartbeat</span> 设成 <span class="mono">true</span>，agent 就会在用户刚说完话、它调了个工具之后<strong>直接冻住</strong>——工具执行完没人续步，对话凭空卡死。这正是 <span class="mono">insert_heartbeat</span> 存在的理由。</p>

<p>这块补丁在 <span class="mono">local_llm/function_parser.py</span>，是给<strong>本地 LLM</strong> 兜底的。<span class="mono">heartbeat_correction</span> 会看两件事：上一条消息是不是<strong>真用户消息</strong>、这条新消息是不是一个<strong>非 <span class="mono">send_message</span></strong> 的工具调用（<span class="mono">NO_HEARTBEAT_FUNCS = ["send_message"]</span>）。两条都满足，就调 <span class="mono">insert_heartbeat</span> 把这次调用的参数里<strong>强行设上</strong> <span class="mono">request_heartbeat=True</span>。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>上一条是真用户消息？</h4><p>解析 <span class="mono">content.type == "user_message"</span>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>新消息是非 send_message 工具调用？</h4><p><span class="mono">send_message</span> 本就该收尾，跳过。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>两条都满足 → 补心跳</h4><p><span class="mono">insert_heartbeat</span> 强设 <span class="mono">request_heartbeat=True</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>否则原样放行</h4><p>不该补的不动，避免误伤。</p></div></div>
</div>

<p>换句话说，<span class="mono">insert_heartbeat</span> 是在替模型"补一句它忘了说的 over"。它只在最容易卡死的那个节点出手——用户刚开口、模型却调了个非收尾工具——既救了场，又不会在本该收尾时画蛇添足。但这终究是<strong>打补丁</strong>：补丁能盖住症状，盖不住"把控制权押在模型自觉上"这个根因。</p>

<div class="note info"><span class="ni">👉</span><span class="nx">这块补丁专为本地模型而生，缘起 <span class="mono">issue #601</span>（本地模型常忘设心跳 → agent 静默）。它甚至带着一个已知的笔误（<span class="mono">tool_call</span> 分支里把 <span class="mono">tool_calls</span> 写成了 <span class="mono">tools_calls</span>）——一个为"模型不靠谱"打的补丁，自己也不那么稳。这恰好反衬出 V3 的思路：与其层层打补丁，不如<strong>从根上不依赖模型的自觉</strong>。</span></div>

<h2>V3 的洞见：把这个决定从模型手里收回</h2>
<p>V3 的做法干脆利落：<span class="mono">_get_valid_tools</span> 调 <span class="mono">runtime_override_tool_json_schema</span> 时直接传 <span class="mono">request_heartbeat=False</span>，源码注释挑明——"NOTE: difference for v3（don't add request heartbeat）"。于是工具 schema 里<strong>压根没有</strong>这个参数，模型也就无从设它。</p>

<p>那循环靠什么续步？靠上一课的 <span class="mono">_decide_continuation</span>：<strong>这一轮调了工具就继续，没调就停</strong>。"调了工具"这个客观动作，取代了"模型举手要心跳"这个主观表态——前者不会忘，于是"模型忘了设"这类 bug 整类消失。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">V3 还留了一手防御：就算模型（或某个旧 prompt）<strong>硬塞</strong>进来一个 <span class="mono">request_heartbeat</span>，<span class="mono">letta_agent_v3.py::_handle_ai_response</span> 也会用 <span class="mono">args.pop(REQUEST_HEARTBEAT_PARAM, None)</span> 把它<strong>默默丢掉</strong>，绝不让一个残留参数干扰续步判据。</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">V3 不注入心跳（_get_valid_tools / _handle_ai_response，简化）</span></div>
<pre><span class="cm"># _get_valid_tools：传 False，不给工具加 request_heartbeat</span>
allowed_tools = <span class="fn">runtime_override_tool_json_schema</span>(
    tool_list=allowed_tools,
    response_format=self.agent_state.response_format,
    request_heartbeat=<span class="nb">False</span>,   <span class="cm"># NOTE: difference for v3（不加心跳）</span>
    terminal_tools=terminal_tool_names,
)

<span class="cm"># _handle_ai_response：防御性地丢掉任何残留的心跳参数</span>
args = <span class="fn">_safe_load_tool_call_str</span>(tc.function.arguments)
args.<span class="fn">pop</span>(REQUEST_HEARTBEAT_PARAM, <span class="kw">None</span>)   <span class="cm"># 续步只看"调没调工具"</span>
</pre></div>

<p>可别以为"心跳"是被全盘否定的设计——同代的<strong>第二代 V2 依然在用</strong>。<span class="mono">letta_agent_v2.py::_get_valid_tools</span> 传的是 <span class="mono">request_heartbeat=True</span>，它的 <span class="mono">_decide_continuation</span> 里 <span class="mono">continue_stepping = request_heartbeat</span>，续步判据仍由模型的心跳标志驱动。只有 V3（<span class="mono">letta_v1_agent</span>，注释 "no heartbeats or forced tool calls"）才把它彻底拿掉。</p>

<table class="t">
  <tr><th>实现</th><th>给工具加 request_heartbeat？</th><th>靠什么续步</th></tr>
  <tr><td class="mono">Agent（元老 / 同步）</td><td>加（必填，非终止工具）</td><td>模型设 true → 注入心跳</td></tr>
  <tr><td class="mono">LettaAgentV2</td><td>加（<span class="mono">request_heartbeat=True</span>）</td><td><span class="mono">continue_stepping = request_heartbeat</span></td></tr>
  <tr><td class="mono">LettaAgentV3</td><td><strong>不加</strong>（<span class="mono">=False</span>）</td><td><span class="mono">_decide_continuation</span>：调了工具就继续</td></tr>
</table>

<div class="note info"><span class="ni">📌</span><span class="nx">还有个反方向的坑别踩：老机制里 <span class="mono">finish_reason == "length"</span>（模型因长度被截断）是直接 <span class="mono">raise RuntimeError</span> 的——它是个<strong>不可重试的错误</strong>，<strong>不是</strong>什么"心跳"。别把"截断"和"续步"搞混。</span></div>

<p>退一步看，这次改动的内核是一句朴素的工程原则：<strong>能用客观信号判定的事，就别去问模型的主观意愿。</strong>"模型想不想继续"是主观的、会忘、会漂移；"这一轮有没有调工具"是客观的、可复现、不看模型脸色。把判据从前者换成后者，循环的行为立刻从"赌模型尽责"变成"按规矩办事"——这正是 agent 从"能跑"走向"可靠"的关键一步。</p>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>这是一堂"少即是多"的设计课：删掉一个参数，等于删掉一整类 bug。</strong>老机制把"我还要不要继续"这个决定交给<strong>模型</strong>——灵活，但脆弱：模型一旦忘了把 <span class="mono">request_heartbeat</span> 设成 <span class="mono">true</span>，agent 就在用户说完话后<strong>冻住</strong>。这正是 <span class="mono">insert_heartbeat</span> 这块补丁存在的原因（还专门为本地模型修过，见 <span class="mono">issue #601</span>）。V3 的洞见是：这个决定<strong>压根不该问模型</strong>——"这一轮调了工具"本身就是"还有后续要做"的可靠信号，那就让<strong>框架</strong>来拍板。于是一个必填参数、一类心跳提示消息、外加"模型忘了设"这一整类 bug，<strong>一起消失</strong>。把控制流从"靠模型自觉"拉回到"靠框架确定"，正是迈向可靠 agent 工程的一步经典操作——<strong>能不交给模型决定的，就别交给它。</strong>同样的哲学，你会在第 16 课的 <span class="mono">tool_rules</span> 里再遇到：把约束写进框架去强制执行，而不是寄望模型自觉遵守。
</div>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>五个锚点，一条演化线。</strong>注入参数在 <span class="mono">services/helpers/tool_parser_helper.py::runtime_override_tool_json_schema</span>（给非终止工具加必填 <span class="mono">request_heartbeat</span>）；老的解析与链式在 <span class="mono">agent.py::Agent._handle_ai_response</span>（<span class="mono">pop</span> 出标志）与 <span class="mono">agent.py::Agent.step</span>（注入心跳、<span class="mono">continue</span>/<span class="mono">break</span>）；本地模型兜底在 <span class="mono">local_llm/function_parser.py::insert_heartbeat</span>；V3 的"不注入"在 <span class="mono">letta_agent_v3.py::_get_valid_tools</span>（<span class="mono">request_heartbeat=False</span>）；常量在 <span class="mono">constants.py</span>（<span class="mono">REQUEST_HEARTBEAT_PARAM / REQUEST_HEARTBEAT_DESCRIPTION / NON_USER_MSG_PREFIX / REQ_HEARTBEAT_MESSAGE / FUNC_FAILED_HEARTBEAT_MESSAGE</span>）。一句话串起来：<strong>schema 里塞参数、_handle_ai_response 读它、step 据它续步、insert_heartbeat 给本地模型兜底，到了 V3 这一串全删，只剩"调了工具就继续"。</strong>想顺藤摸瓜时，从 <span class="mono">constants.py</span> 里那几个心跳常量入手最快——谁还引用它们，谁就还在用心跳。
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>四个别记错的点。</strong>其一，解析心跳标志的是 <span class="mono">Agent._handle_ai_response</span>，<strong>不是</strong> <span class="mono">inner_step</span>——注入与续步则在 <span class="mono">Agent.step</span>。其二，<span class="mono">request_heartbeat</span> 是<strong>必填</strong>的，而且<strong>只</strong>加给<strong>非终止工具</strong>（<span class="mono">send_message</span> 这类终止工具不加）。其三，别以为"心跳"是被否定的旧设计——<strong>V2 仍在用</strong>心跳续步，<strong>只有 V3</strong> 把它拿掉。其四，老机制里 <span class="mono">finish_reason == "length"</span> 是 <span class="mono">raise RuntimeError</span>（不可重试的错误），<strong>不是</strong>心跳，别混为一谈。
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary><span class="mono">request_heartbeat</span> 加在哪、为什么必填、为什么不加给终止工具？</summary><div class="acc-body">
<p><strong>加在哪：</strong>在 <span class="mono">runtime_override_tool_json_schema</span> 这道"改写工具 schema"的关口，遍历每个工具，往它的 <span class="mono">parameters.properties</span> 里塞一个 <span class="mono">request_heartbeat: {type: boolean}</span>，并 <span class="mono">append</span> 进 <span class="mono">parameters.required</span>。</p>
<p><strong>为什么必填：</strong>若它是可选的，模型很可能干脆不提它，"继续"就成了薛定谔状态。设成必填，逼模型每次调工具都<strong>明确表态</strong>——这是老设计把决定权交给模型的代价。</p>
<p><strong>为什么不加给终止工具：</strong>终止工具（如 <span class="mono">send_message</span>）的语义本就是"这一轮到此为止"，再问它"要不要继续"自相矛盾。所以 <span class="mono">terminal_tools</span> 集合里的工具被显式跳过。</p>
<p><strong>一个副作用：</strong>因为它进了 <span class="mono">required</span>，模型每次调普通工具都得带上这个参数——这也是为什么 <span class="mono">_handle_ai_response</span> 第一件事就是把它 <span class="mono">pop</span> 出来，免得它混进真正传给工具函数的实参里。</p>
<p><strong>源码在哪：</strong><span class="mono">services/helpers/tool_parser_helper.py::runtime_override_tool_json_schema</span>。</p>
</div></details>

<details class="accordion"><summary>工具<strong>报错</strong>时那条"自动心跳"是干嘛的？</summary><div class="acc-body">
<p><strong>示例：</strong>模型调了个查数据库的工具，工具抛了异常。如果就这么收场，模型根本不知道发生了什么，用户只会收到一句莫名其妙的沉默。</p>
<p><strong>为什么这样设计：</strong>老机制在 <span class="mono">step</span> 里把"函数失败"排在心跳判断<strong>之前</strong>：只要 <span class="mono">function_failed</span> 为真，就算模型没要心跳，也强行注入一条 <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span> 续上一圈，让模型<strong>看见错误、有机会补救</strong>（换个参数重试，或向用户解释）。</p>
<p><strong>一个连锁反应：</strong>正因为"报错也续步"，模型才能在下一圈换个参数重试同一个工具——这也是为什么第 14 课那道 <span class="mono">max_steps=50</span> 保险丝必须存在：万一模型反复失败、反复重试，总得有个上限兜住，免得无限烧 token。</p>
<p><strong>源码在哪：</strong><span class="mono">agent.py::step</span> 的 <span class="mono">if function_failed: ... continue</span> 分支；常量 <span class="mono">constants.py::FUNC_FAILED_HEARTBEAT_MESSAGE</span>。</p>
<p><strong>还有什么替代：</strong>报错即停——但模型没机会自愈，体验更差。老机制选了"出错也续一圈让模型救场"。</p>
</div></details>

<details class="accordion"><summary><span class="mono">insert_heartbeat</span> 和 issue #601 到底在补什么？</summary><div class="acc-body">
<p><strong>示例：</strong>一个<strong>本地小模型</strong>跑 agent，用户问完问题，它调了个工具却忘了设 <span class="mono">request_heartbeat=true</span>。工具跑完没人续步，agent 当场静默——用户以为它死机了。</p>
<p><strong>为什么这样设计：</strong>本地模型不如大厂模型"听话"，常漏设这个参数。<span class="mono">heartbeat_correction</span> 于是兜底：<strong>上一条是真用户消息</strong> 且 <strong>新消息是非 <span class="mono">send_message</span> 的工具调用</strong>时，就 <span class="mono">insert_heartbeat</span> 强行补上 <span class="mono">request_heartbeat=True</span>。这正是 <span class="mono">issue #601</span> 的修复。</p>
<p><strong>源码在哪：</strong><span class="mono">local_llm/function_parser.py::insert_heartbeat / heartbeat_correction</span>；<span class="mono">NO_HEARTBEAT_FUNCS = ["send_message"]</span>。</p>
<p><strong>还有什么替代：</strong>就是 V3 的路子——不依赖模型设标志，从根上让"调了工具"驱动续步，这块补丁也就不必存在了。</p>
</div></details>

<details class="accordion"><summary>V3 凭什么敢删掉心跳，V2 又为什么还留着？</summary><div class="acc-body">
<p><strong>V3 凭什么敢删：</strong>因为它换了续步信号。老机制问"模型想不想继续"（主观、会忘），V3 改问"这一轮调没调工具"（客观、不会忘）——而"调了工具"本身就蕴含"还得把结果喂回模型"，天然等价于"要继续"。信号更可靠，心跳参数就成了多余。</p>
<p><strong>V2 为什么还留：</strong>V2 是从老 MemGPT 循环平滑演进来的异步版，续步判据仍是 <span class="mono">continue_stepping = request_heartbeat</span>，<strong>为兼容旧设计</strong>而保留心跳。删除是 V3 才迈出的一步。</p>
<p><strong>怎么记：</strong>看 <span class="mono">_get_valid_tools</span> 传的那个布尔——V2 传 <span class="mono">True</span>（加心跳），V3 传 <span class="mono">False</span>（不加）。一参之差，正是两代的分水岭。</p>
<p><strong>一句话总结这条演化：</strong>从"模型举手要心跳"（元老 <span class="mono">Agent</span>）→ 异步化但仍保留心跳（<span class="mono">V2</span>）→ 彻底改用"调了工具就继续"（<span class="mono">V3</span>）。每一代都在把"继续"的决定权，从模型一点点挪回框架。</p>
<p><strong>源码在哪：</strong><span class="mono">letta_agent_v2.py::_get_valid_tools</span> vs <span class="mono">letta_agent_v3.py::_get_valid_tools</span>；续步见 <span class="mono">letta_agent_v3.py::_decide_continuation</span>（第 14 课）。</p>
</div></details>

<h2>下一站</h2>
<p>这一课我们追了一条设计演化线：老的 MemGPT / 元老 <span class="mono">Agent</span> / V2 给每个非终止工具塞一个必填的 <span class="mono">request_heartbeat</span>，让模型自己举手续步；本地模型忘了设，就靠 <span class="mono">insert_heartbeat</span> 兜底。到了 V3，这一整套被"调了工具就继续"取代——参数、心跳消息，连同"模型忘了设"的 bug，一并删干净。</p>

<p>这正好接回第 14 课那句 <span class="mono">_decide_continuation</span> 的判据，也呼应它注释里的 "no heartbeats"。而老机制里反复出现的"工具规则可以覆盖心跳标志"（<span class="mono">has_children_tools</span> / <span class="mono">is_terminal_tool</span> / <span class="mono">is_continue_tool</span>），正是下一课第 16 课的主角——<span class="mono">tool_rules</span>（终止 / 必调 / 审批）究竟怎么左右这个循环。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">一句话带走：<strong>老机制让模型设 <span class="mono">request_heartbeat=true</span> 来续步，V3 改成"调了工具就继续"，把这个决定从模型手里收回给框架——删一个参数，灭一类 bug。</strong></span></div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>request_heartbeat 是什么</strong>：老机制给每个<strong>非终止工具</strong>加的一个<strong>必填</strong>布尔参数；模型设 <span class="mono">true</span> 才续步。注入在 <span class="mono">tool_parser_helper.py::runtime_override_tool_json_schema</span>。</li>
    <li><strong>老机制怎么续步</strong>：模型设 <span class="mono">true</span> → 框架注入一条 <span class="mono">REQ_HEARTBEAT_MESSAGE</span>（<span class="mono">role=user</span>，对用户隐藏）→ 续；工具报错 → 注入 <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span> → 续；否则 <span class="mono">break</span>。解析在 <span class="mono">agent.py::_handle_ai_response</span>，链式在 <span class="mono">agent.py::step</span>。</li>
    <li><strong>insert_heartbeat</strong>：本地模型常忘设标志（<span class="mono">issue #601</span>）→ 上一条是用户消息且这是非 <span class="mono">send_message</span> 工具调用时，强行补 <span class="mono">request_heartbeat=True</span>（<span class="mono">local_llm/function_parser.py</span>）。</li>
    <li><strong>V3 拿掉它</strong>：<span class="mono">_get_valid_tools</span> 传 <span class="mono">request_heartbeat=False</span>（"NOTE: difference for v3"），续步改由 <span class="mono">_decide_continuation</span>"调了工具就继续"决定；还会 <span class="mono">args.pop(REQUEST_HEARTBEAT_PARAM)</span> 防御性丢弃残留。</li>
    <li><strong>别记错</strong>：<strong>V2 仍用心跳</strong>（传 <span class="mono">True</span>），只有 V3 删；解析在 <span class="mono">_handle_ai_response</span> 不是 <span class="mono">inner_step</span>；老机制 <span class="mono">finish_reason=="length"</span> 是 <span class="mono">raise</span>，不是心跳。</li>
    <li><strong>设计亮点</strong>：把"要不要继续"从"模型自觉"收回到"框架确定"——删一个参数，灭一类 bug。</li>
    <li><strong>源码</strong>：<span class="mono">tool_parser_helper.py::runtime_override_tool_json_schema</span>、<span class="mono">agent.py::_handle_ai_response / step</span>、<span class="mono">local_llm/function_parser.py::insert_heartbeat</span>、<span class="mono">letta_agent_v3.py::_get_valid_tools</span>、<span class="mono">constants.py</span> 心跳常量。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Last lesson, while taking the V3 loop apart, we hit a counterintuitive criterion: whether to step again <strong>doesn't read whether the model wants to continue, only whether this round called a tool</strong>. That left a loose thread — what exactly did the "no heartbeats" in <span class="mono">letta_v1_agent</span>'s comment take away? This lesson settles that account.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
This is a <strong>design-evolution lesson</strong>. Old MemGPT, the elder <span class="mono">Agent</span>, and the second-generation <span class="mono">LettaAgentV2</span> all step again via one switch called <span class="mono">request_heartbeat</span>: the model must <strong>raise its own hand</strong> inside a tool call to say "I want to keep going." The third generation, V3, deletes that switch entirely. Between cutting it and keeping it sits a plain piece of engineering wisdom — <strong>don't pin a decision as critical as "continue or not" on the model's conscientiousness.</strong></p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Picture the two generations as two kinds of walkie-talkie.</strong> The old one is a <strong>half-duplex walkie-talkie</strong>: every time you finish a sentence you must actively add "over, please continue," or the other side won't know it's their turn; forget that "over" and the line goes <strong>silent</strong> — they wait for you, you think you're waiting for them, and the whole conversation jams right there. The new one changes the rule: <strong>as long as you keep handing out "tool tickets," the line keeps turning by default</strong>, no need to shout "please continue" each time; only when you stop handing out tickets and speak directly do you hand the mic back. The old design rests "continue" on <strong>whether the speaker remembers the code word</strong>; the new one welds it to <strong>the objective act of "did you hand out a ticket"</strong> — the latter can't be forgotten, so it can't jam. In the end, a reliable line doesn't lean on the worker remembering to call "over" every time, but on the mechanical certainty of the belt itself.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>One line for this lesson: the old design lets the <em>model</em> decide "continue or not," and V3 takes that decision back for the <em>framework</em>.</strong> The old mechanism (the elder <span class="mono">Agent</span> in <span class="mono">letta/agent.py</span>, plus <span class="mono">LettaAgentV2</span>) stuffs every <strong>non-terminal tool</strong> with a required boolean param <span class="mono">request_heartbeat</span>; to keep working, the model must set it <span class="mono">true</span>, and the framework then injects a "heartbeat" user message to hand control back and take one more lap (<span class="mono">agent.py::_handle_ai_response</span> reads the flag, <span class="mono">agent.py::step</span> injects and continues). When a tool <strong>fails</strong>, the framework auto-adds a heartbeat too, so the model can see the error and recover. V3's (<span class="mono">letta_agent_v3.py</span>) insight: this decision <strong>shouldn't be asked of the model</strong> — "a tool was called this round" is itself a reliable signal of "there's follow-up," so <span class="mono">_get_valid_tools</span> passes <span class="mono">request_heartbeat=False</span> (comment "NOTE: difference for v3"), and continuation falls back to last lesson's <span class="mono">_decide_continuation</span>. One required param, one class of heartbeat message, and a whole bug-class of "the model forgot to set it" all vanish together. The cost is nearly zero — because "called a tool" already means "keep going," and that extra layer of making the model confirm once more was redundant from the start.
</div>

<h2>The old design: every non-terminal tool carries a request_heartbeat</h2>
<p>First, get to know this switch. Before handing a tool's JSON schema to the model, the old mechanism <strong>dynamically</strong> stuffs one extra param into every tool — <span class="mono">request_heartbeat</span> (a boolean) — and lists it in <span class="mono">required</span>. The injection logic lives in <span class="mono">tool_parser_helper.py::runtime_override_tool_json_schema</span>, whose docstring says it plainly — "tools get an extra <span class="mono">request_heartbeat</span> parameter (except terminal tools)."</p>

<div class="note tip"><span class="ni">💡</span><span class="nx">This parameter's description (<span class="mono">constants.py::REQUEST_HEARTBEAT_DESCRIPTION</span>) is the instruction sheet written for the model: <strong>"if you want to send a follow-up message or call another tool (chaining multiple tools together), you MUST set this to <span class="mono">True</span>; set it <span class="mono">False</span> (the default) and the execution chain ends immediately after this call."</strong> — whether to "continue" is placed squarely in the model's hands.</span></div>

<p>Note two "only"s: it's <strong>added only to non-terminal tools</strong> (terminal tools like <span class="mono">send_message</span> are excluded — they're meant to end the round), and once added it's <strong>required</strong>. So every time the model calls an ordinary tool, it's forced to declare once more "do I continue or not."</p>

<div class="flow">
  <div class="node"><div class="nt">Raw tool schema</div><div class="nd">only the tool's own parameters</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">runtime_override_tool_json_schema</div><div class="nd">the gate that rewrites the tool schema</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Old · add request_heartbeat</div><div class="nd">bool, and into required (except terminal tools)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">V3 · add nothing</div><div class="nd">passes request_heartbeat=False</div></div>
</div>

<p>Why did MemGPT design it this way? Because the model produces just "one passage" at a time, while a task often needs several tool calls in a row — check core memory, search archival, then finally reply. The model needs an outlet to tell the framework "this passage isn't done, don't rush the mic back to the user," and <span class="mono">request_heartbeat=true</span> is that outlet. It's of a piece with lesson 4's ReAct and inner monologue: let the model <strong>explicitly</strong> say "I want to think one more step, do one more step."</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/helpers/tool_parser_helper.py</span><span class="ln">inject request_heartbeat (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">runtime_override_tool_json_schema</span>(tool_list, response_format,
                                      request_heartbeat=<span class="nb">True</span>, terminal_tools=<span class="kw">None</span>):
    <span class="cm"># docstring: tools get an extra request_heartbeat param (except terminal tools)</span>
    terminal_tools = terminal_tools <span class="kw">or</span> <span class="fn">set</span>()
    <span class="kw">for</span> tool_json <span class="kw">in</span> tool_list:
        <span class="kw">if</span> request_heartbeat:
            <span class="kw">if</span> tool_json[<span class="st">"name"</span>] <span class="kw">not in</span> terminal_tools:   <span class="cm"># only add to non-terminal tools</span>
                tool_json[<span class="st">"parameters"</span>][<span class="st">"properties"</span>][REQUEST_HEARTBEAT_PARAM] = {
                    <span class="st">"type"</span>: <span class="st">"boolean"</span>,
                    <span class="st">"description"</span>: REQUEST_HEARTBEAT_DESCRIPTION,
                }
                <span class="kw">if</span> REQUEST_HEARTBEAT_PARAM <span class="kw">not in</span> tool_json[<span class="st">"parameters"</span>][<span class="st">"required"</span>]:
                    tool_json[<span class="st">"parameters"</span>][<span class="st">"required"</span>].<span class="fn">append</span>(REQUEST_HEARTBEAT_PARAM)  <span class="cm"># required</span>
    <span class="kw">return</span> tool_list
</pre></div>

<h2>How the old mechanism steps again: a "heartbeat" message chain</h2>
<p>With the param in place, how does the loop use it to step again? In three beats: the model includes <span class="mono">request_heartbeat=true</span> in a tool call → after running the tool, the framework <strong>injects a "heartbeat" user message</strong> to hand control back to the model → next lap the model reads that message and carries on. If it's <span class="mono">false</span> (or absent), the loop <span class="mono">break</span>s and hands the mic back to the real user.</p>

<div class="note info"><span class="ni">📌</span><span class="nx">This "heartbeat" message has <span class="mono">role=user</span>, but no real user sent it — its content is prefixed with <span class="mono">NON_USER_MSG_PREFIX</span> ("[This is an automated system message hidden from the user] ") and is <strong>hidden</strong> from the user. See the constant <span class="mono">constants.py::REQ_HEARTBEAT_MESSAGE</span>.</span></div>

<p>The crux here shares a root with last lesson: a tool call is inherently <strong>two-stage</strong> — the model first says "I'll call <span class="mono">search</span>," the framework runs it, gets a result, and must <strong>feed that result back</strong> for the model to carry on. So "called a tool" already means "there's a second half." Yet the old mechanism didn't use that fact directly; it <strong>took an extra detour</strong>: making the model confirm once more, in the parameters, "I want to continue." V3 saw through that confirmation as redundant and dropped it.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Model calls a tool</h4><p>Includes <span class="mono">request_heartbeat=true</span>, signaling "I want to continue."</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>_handle_ai_response reads the flag</h4><p><span class="mono">function_args.pop("request_heartbeat")</span>; the string "true" is normalized to a bool.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Execute the tool</h4><p>Run it and get the result; if it <strong>fails</strong>, record <span class="mono">function_failed=True</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>step injects a heartbeat</h4><p><span class="mono">true</span> → inject <span class="mono">REQ_HEARTBEAT_MESSAGE</span> (role=user), <span class="mono">continue</span>.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>false → break</h4><p>No heartbeat requested, break out of the loop, wrap up and hand back to the user.</p></div></div>
</div>

<p>This parsing step happens in <span class="mono">agent.py::Agent._handle_ai_response</span>: it <span class="mono">pop</span>s <span class="mono">request_heartbeat</span> out of the tool args and, along the way, handles the corner case of "serialized into the string 'true'." Tool rules can also <strong>override</strong> this flag — <span class="mono">has_children_tools</span> forces <span class="mono">True</span>, <span class="mono">is_terminal_tool</span> forces <span class="mono">False</span>, <span class="mono">is_continue_tool</span> forces <span class="mono">True</span> (that rule set is for lesson 16 to detail).</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">Don't misplace it: the one parsing the heartbeat flag is <span class="mono">Agent._handle_ai_response</span>, <strong>not</strong> <span class="mono">inner_step</span>; the one actually "injecting the heartbeat message and deciding continue/break" is <span class="mono">Agent.step</span> (its docstring says verbatim it "handles heartbeat-request and function-failure based chaining within the loop").</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agent.py</span><span class="ln">old chained continuation (_handle_ai_response + step, simplified)</span></div>
<pre><span class="cm"># _handle_ai_response: pull the heartbeat flag out of the tool args</span>
heartbeat_request = function_args.<span class="fn">pop</span>(<span class="st">"request_heartbeat"</span>, <span class="kw">None</span>)
<span class="kw">if</span> <span class="fn">isinstance</span>(heartbeat_request, <span class="nb">str</span>) <span class="kw">and</span> heartbeat_request.<span class="fn">lower</span>() == <span class="st">"true"</span>:
    heartbeat_request = <span class="nb">True</span>             <span class="cm"># normalize the string "true" to a bool</span>

<span class="cm"># step: use the flag to decide continue or wrap up</span>
<span class="kw">if</span> function_failed:                       <span class="cm"># tool failed -> auto-continue so the model sees the error</span>
    inject(<span class="fn">get_heartbeat</span>(FUNC_FAILED_HEARTBEAT_MESSAGE)); <span class="kw">continue</span>
<span class="kw">elif</span> heartbeat_request:                   <span class="cm"># model asked for a heartbeat -> continue</span>
    inject(<span class="fn">get_heartbeat</span>(REQ_HEARTBEAT_MESSAGE)); <span class="kw">continue</span>
<span class="kw">else</span>:
    <span class="kw">break</span>                                <span class="cm"># no heartbeat -> wrap up, hand back to the user</span>
</pre></div>

<p>Beat 4's "tool failed → auto-continue" deserves its own mention: even if the model <strong>didn't</strong> ask for a heartbeat, as long as a tool execution <strong>fails</strong>, the old mechanism force-injects a <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span> to hand control back to the model — so it can see the error and get a chance to recover, rather than wrapping up hastily with a failed tool call in hand.</p>

<div class="cellgroup">
  <div class="cg-cap">The old mechanism's two "hand control back" messages both carry the <b>NON_USER_MSG_PREFIX</b> prefix and are hidden from the user</div>
  <div class="cells">
    <span class="lab">continue</span>
    <span class="cell hl">REQ_HEARTBEAT_MESSAGE</span>
    <span class="sep">·</span>
    <span class="cell">model set true, return control</span>
  </div>
  <div class="cells">
    <span class="lab">failure</span>
    <span class="cell hl">FUNC_FAILED_HEARTBEAT_MESSAGE</span>
    <span class="sep">·</span>
    <span class="cell">function failed, return control</span>
  </div>
  <div class="cells">
    <span class="lab">prefix</span>
    <span class="cell q">[This is an automated system message hidden from the user]</span>
  </div>
</div>

<div class="cols">
  <div class="col">
    <h4>🕰️ Old mechanism (Agent / V2)</h4>
    <p>The schema has a <strong>required</strong> <span class="mono">request_heartbeat</span>.</p>
    <p>Model sets <span class="mono">true</span> → inject <span class="mono">REQ_HEARTBEAT_MESSAGE</span> (role=user) → continue.</p>
    <p>Tool fails → inject <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span> → continue.</p>
    <p class="mono" style="font-size:.82rem">continue = the model raised its own hand</p>
  </div>
  <div class="col">
    <h4>🆕 V3 (letta_v1_agent)</h4>
    <p>The schema <strong>adds no</strong> <span class="mono">request_heartbeat</span> at all.</p>
    <p><span class="mono">_decide_continuation</span>: called a tool this round → continue; didn't → stop.</p>
    <p>Even if the model jams in a heartbeat param, <span class="mono">args.pop(...)</span> quietly drops it.</p>
    <p class="mono" style="font-size:.82rem">continue = the framework checks "was a tool called"</p>
  </div>
</div>

<div class="cute">
  <div class="row">
    <span class="emoji">💓</span><span class="lab">Old · walkie-talkie</span>
    <span class="arrow">→</span>
    <span class="emoji">🤐</span><span class="bubble">Forgot "over, please continue" → line goes silent</span>
    <span class="emoji">🔁</span><span class="bubble">Still handing out tool tickets → line keeps turning</span>
    <span class="lab">New · continue by default</span>
  </div>
  <div class="cap">The old way leans on the model shouting "over, please continue" each time and jams when it forgets; the new way welds "continue" to "was a tool called," so nothing to shout and nothing to forget</div>
</div>

<h2>What if the model forgets: the insert_heartbeat patch</h2>
<p>Handing the "continue" decision to the model is flexible, but <strong>fragile</strong>: the moment the model forgets to set <span class="mono">request_heartbeat</span> to <span class="mono">true</span>, the agent <strong>freezes</strong> right after the user has spoken and it called a tool — the tool finishes, nobody steps again, and the conversation jams out of nowhere. This is exactly why <span class="mono">insert_heartbeat</span> exists.</p>

<p>This patch sits in <span class="mono">local_llm/function_parser.py</span> as a safety net for <strong>local LLMs</strong>. <span class="mono">heartbeat_correction</span> checks two things: whether the previous message is a <strong>real user message</strong>, and whether this new message is a <strong>non-<span class="mono">send_message</span></strong> tool call (<span class="mono">NO_HEARTBEAT_FUNCS = ["send_message"]</span>). If both hold, it calls <span class="mono">insert_heartbeat</span> to <strong>force-set</strong> <span class="mono">request_heartbeat=True</span> into this call's arguments.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Previous is a real user message?</h4><p>Parse <span class="mono">content.type == "user_message"</span>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>New message is a non-send_message tool call?</h4><p><span class="mono">send_message</span> is meant to wrap up, so skip it.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Both hold → add a heartbeat</h4><p><span class="mono">insert_heartbeat</span> force-sets <span class="mono">request_heartbeat=True</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Otherwise pass through</h4><p>Leave alone what shouldn't be patched, avoiding collateral damage.</p></div></div>
</div>

<p>In other words, <span class="mono">insert_heartbeat</span> adds, on the model's behalf, "the 'over' it forgot to say." It only steps in at the node most prone to jamming — the user just spoke, yet the model called a non-terminal tool — rescuing the situation without gilding the lily when it should wrap up. But this is, after all, a <strong>patch</strong>: it covers the symptom, not the root cause of "pinning control on the model's conscientiousness."</p>

<div class="note info"><span class="ni">👉</span><span class="nx">This patch was born for local models, originating from <span class="mono">issue #601</span> (local models often forget to set the heartbeat → the agent goes silent). It even carries a known typo (the <span class="mono">tool_call</span> branch writes <span class="mono">tools_calls</span> instead of <span class="mono">tool_calls</span>) — a patch for "the model is unreliable" that isn't all that steady itself. Which neatly throws V3's approach into relief: rather than patch layer upon layer, stop depending on the model's conscientiousness at the root.</span></div>

<h2>V3's insight: take the decision back from the model</h2>
<p>V3's move is clean and decisive: when <span class="mono">_get_valid_tools</span> calls <span class="mono">runtime_override_tool_json_schema</span>, it passes <span class="mono">request_heartbeat=False</span> outright, and the source comment spells it out — "NOTE: difference for v3 (don't add request heartbeat)." So the tool schema has no such param at all, and the model has no way to set it.</p>

<p>Then what does the loop step on? On last lesson's <span class="mono">_decide_continuation</span>: <strong>called a tool this round → continue, didn't → stop</strong>. The objective act of "called a tool" replaces the subjective declaration of "the model raised its hand for a heartbeat" — the former can't be forgotten, so the whole bug-class of "the model forgot to set it" vanishes.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">V3 keeps one defensive move too: even if the model (or some old prompt) <strong>jams in</strong> a <span class="mono">request_heartbeat</span>, <span class="mono">letta_agent_v3.py::_handle_ai_response</span> uses <span class="mono">args.pop(REQUEST_HEARTBEAT_PARAM, None)</span> to <strong>quietly drop it</strong>, never letting a leftover param disturb the continuation criterion.</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/letta_agent_v3.py</span><span class="ln">V3 injects no heartbeat (_get_valid_tools / _handle_ai_response, simplified)</span></div>
<pre><span class="cm"># _get_valid_tools: pass False, don't add request_heartbeat to tools</span>
allowed_tools = <span class="fn">runtime_override_tool_json_schema</span>(
    tool_list=allowed_tools,
    response_format=self.agent_state.response_format,
    request_heartbeat=<span class="nb">False</span>,   <span class="cm"># NOTE: difference for v3 (no heartbeat added)</span>
    terminal_tools=terminal_tool_names,
)

<span class="cm"># _handle_ai_response: defensively drop any leftover heartbeat param</span>
args = <span class="fn">_safe_load_tool_call_str</span>(tc.function.arguments)
args.<span class="fn">pop</span>(REQUEST_HEARTBEAT_PARAM, <span class="kw">None</span>)   <span class="cm"># continuation only looks at "was a tool called"</span>
</pre></div>

<p>Don't assume "heartbeats" are a wholly rejected design — the same-era second generation, <strong>V2, still uses them</strong>. <span class="mono">letta_agent_v2.py::_get_valid_tools</span> passes <span class="mono">request_heartbeat=True</span>, and in its <span class="mono">_decide_continuation</span>, <span class="mono">continue_stepping = request_heartbeat</span> — continuation is still driven by the model's heartbeat flag. Only V3 (<span class="mono">letta_v1_agent</span>, comment "no heartbeats or forced tool calls") removes it entirely.</p>

<table class="t">
  <tr><th>Implementation</th><th>Add request_heartbeat to tools?</th><th>What it steps on</th></tr>
  <tr><td class="mono">Agent (elder / synchronous)</td><td>add (required, non-terminal tools)</td><td>model sets true → inject heartbeat</td></tr>
  <tr><td class="mono">LettaAgentV2</td><td>add (<span class="mono">request_heartbeat=True</span>)</td><td><span class="mono">continue_stepping = request_heartbeat</span></td></tr>
  <tr><td class="mono">LettaAgentV3</td><td><strong>don't add</strong> (<span class="mono">=False</span>)</td><td><span class="mono">_decide_continuation</span>: called a tool → continue</td></tr>
</table>

<div class="note info"><span class="ni">📌</span><span class="nx">One more trap in the other direction: in the old mechanism, <span class="mono">finish_reason == "length"</span> (the model truncated by length) directly <span class="mono">raise</span>s a <span class="mono">RuntimeError</span> — it's a <strong>non-retryable error</strong>, <strong>not</strong> any kind of "heartbeat." Don't confuse "truncation" with "stepping again."</span></div>

<p>Step back, and the core of this change is one plain engineering principle: <strong>what an objective signal can settle, don't ask the model's subjective will.</strong> "Does the model want to continue" is subjective, forgettable, drift-prone; "did this round call a tool" is objective, reproducible, indifferent to the model's mood. Swap the criterion from the former to the latter and the loop's behavior shifts at once from "betting on the model being dutiful" to "going by the rules" — exactly the key step in an agent moving from "runs" to "reliable."</p>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  <strong>This is a "less is more" design lesson: delete one parameter, and you delete a whole bug-class.</strong> The old mechanism hands the "do I keep going" decision to the <strong>model</strong> — flexible, but fragile: once the model forgets to set <span class="mono">request_heartbeat</span> to <span class="mono">true</span>, the agent <strong>freezes</strong> right after the user speaks. This is exactly why the <span class="mono">insert_heartbeat</span> patch exists (and it was fixed specifically for local models, see <span class="mono">issue #601</span>). V3's insight: this decision <strong>shouldn't be asked of the model at all</strong> — "a tool was called this round" is itself a reliable signal of "there's follow-up to do," so let the <strong>framework</strong> make the call. So one required parameter, one class of heartbeat prompt message, plus the whole bug-class of "the model forgot to set it" all <strong>vanish together</strong>. Pulling control flow from "lean on the model's conscientiousness" back to "lean on the framework's certainty" is a classic move toward reliable agent engineering — <strong>whatever needn't be left to the model to decide, don't.</strong> You'll meet the same philosophy again in lesson 16's <span class="mono">tool_rules</span>: write constraints into the framework to enforce them, rather than hoping the model abides by them on its own.
</div>

<div class="card detail">
  <div class="tag">🔬 Down to the code</div>
  <strong>Five anchors, one evolution line.</strong> The param injection is in <span class="mono">services/helpers/tool_parser_helper.py::runtime_override_tool_json_schema</span> (adds a required <span class="mono">request_heartbeat</span> to non-terminal tools); the old parsing and chaining are in <span class="mono">agent.py::Agent._handle_ai_response</span> (<span class="mono">pop</span>s the flag) and <span class="mono">agent.py::Agent.step</span> (inject heartbeat, <span class="mono">continue</span>/<span class="mono">break</span>); the local-model safety net is <span class="mono">local_llm/function_parser.py::insert_heartbeat</span>; V3's "don't inject" is in <span class="mono">letta_agent_v3.py::_get_valid_tools</span> (<span class="mono">request_heartbeat=False</span>); the constants are in <span class="mono">constants.py</span> (<span class="mono">REQUEST_HEARTBEAT_PARAM / REQUEST_HEARTBEAT_DESCRIPTION / NON_USER_MSG_PREFIX / REQ_HEARTBEAT_MESSAGE / FUNC_FAILED_HEARTBEAT_MESSAGE</span>). Strung into one line: <strong>the schema stuffs in the param, _handle_ai_response reads it, step continues on it, insert_heartbeat backs up local models, and by V3 the whole chain is deleted, leaving only "called a tool → continue."</strong> When tracing the thread, start from those heartbeat constants in <span class="mono">constants.py</span> — whoever still references them is still using heartbeats.
</div>

<div class="card warn">
  <div class="tag">⚠️ Common pitfalls</div>
  <strong>Four points not to misremember.</strong> One: the one parsing the heartbeat flag is <span class="mono">Agent._handle_ai_response</span>, <strong>not</strong> <span class="mono">inner_step</span> — injection and continuation are in <span class="mono">Agent.step</span>. Two: <span class="mono">request_heartbeat</span> is <strong>required</strong>, and added <strong>only</strong> to <strong>non-terminal tools</strong> (terminal tools like <span class="mono">send_message</span> don't get it). Three: don't think "heartbeats" are a rejected old design — <strong>V2 still uses</strong> heartbeats to continue, <strong>only V3</strong> drops them. Four: in the old mechanism, <span class="mono">finish_reason == "length"</span> is a <span class="mono">raise RuntimeError</span> (a non-retryable error), <strong>not</strong> a heartbeat — don't lump them together.
</div>

<h2>Digging a little deeper</h2>

<details class="accordion"><summary>Where is <span class="mono">request_heartbeat</span> added, why is it required, and why not on terminal tools?</summary><div class="acc-body">
<p><strong>Where it's added:</strong> at <span class="mono">runtime_override_tool_json_schema</span>, the "rewrite the tool schema" gate, it walks every tool and stuffs a <span class="mono">request_heartbeat: {type: boolean}</span> into its <span class="mono">parameters.properties</span>, and <span class="mono">append</span>s it into <span class="mono">parameters.required</span>.</p>
<p><strong>Why required:</strong> if it were optional, the model would likely just omit it, and "continue" would become a Schrödinger state. Making it required forces the model to <strong>declare explicitly</strong> on every tool call — the price of the old design handing the decision to the model.</p>
<p><strong>Why not on terminal tools:</strong> a terminal tool (like <span class="mono">send_message</span>) means "this round ends here" by definition, so asking it "continue or not" is self-contradictory. Tools in the <span class="mono">terminal_tools</span> set are therefore explicitly skipped.</p>
<p><strong>A side effect:</strong> because it's in <span class="mono">required</span>, the model must include this param on every ordinary tool call — which is why <span class="mono">_handle_ai_response</span>'s first move is to <span class="mono">pop</span> it out, lest it slip into the real arguments passed to the tool function.</p>
<p><strong>Where in the source:</strong> <span class="mono">services/helpers/tool_parser_helper.py::runtime_override_tool_json_schema</span>.</p>
</div></details>

<details class="accordion"><summary>What is that "auto-heartbeat" on tool <strong>failure</strong> for?</summary><div class="acc-body">
<p><strong>Example:</strong> the model called a database tool and the tool threw an exception. Wrap up right there and the model has no idea what happened, while the user gets nothing but a baffling silence.</p>
<p><strong>Why it's designed this way:</strong> the old mechanism puts "function failed" <strong>before</strong> the heartbeat check in <span class="mono">step</span>: as long as <span class="mono">function_failed</span> is true, even without a requested heartbeat, it force-injects a <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span> and takes one more lap, letting the model <strong>see the error and get a chance to recover</strong> (retry with different args, or explain to the user).</p>
<p><strong>A knock-on effect:</strong> precisely because "failure also continues," the model can retry the same tool with different args next lap — which is also why lesson 14's <span class="mono">max_steps=50</span> fuse must exist: should the model fail and retry over and over, there has to be a ceiling to catch it before it burns tokens endlessly.</p>
<p><strong>Where in the source:</strong> the <span class="mono">if function_failed: ... continue</span> branch in <span class="mono">agent.py::step</span>; the constant <span class="mono">constants.py::FUNC_FAILED_HEARTBEAT_MESSAGE</span>.</p>
<p><strong>What's the alternative:</strong> stop on error — but then the model gets no chance to self-heal, a worse experience. The old mechanism chose "continue one lap on error to let the model rescue it."</p>
</div></details>

<details class="accordion"><summary>What exactly do <span class="mono">insert_heartbeat</span> and <span class="mono">issue #601</span> patch?</summary><div class="acc-body">
<p><strong>Example:</strong> a <strong>small local model</strong> runs an agent; the user asks a question, it calls a tool but forgets to set <span class="mono">request_heartbeat=true</span>. The tool finishes, nobody steps again, and the agent goes silent on the spot — the user thinks it crashed.</p>
<p><strong>Why it's designed this way:</strong> local models aren't as "obedient" as big-vendor models and often miss this param. So <span class="mono">heartbeat_correction</span> backs them up: when the <strong>previous message is a real user message</strong> and the <strong>new message is a non-<span class="mono">send_message</span> tool call</strong>, it calls <span class="mono">insert_heartbeat</span> to force in <span class="mono">request_heartbeat=True</span>. This is exactly the <span class="mono">issue #601</span> fix.</p>
<p><strong>Where in the source:</strong> <span class="mono">local_llm/function_parser.py::insert_heartbeat / heartbeat_correction</span>; <span class="mono">NO_HEARTBEAT_FUNCS = ["send_message"]</span>.</p>
<p><strong>What's the alternative:</strong> V3's path — don't depend on the model setting a flag; let "called a tool" drive continuation at the root, and this patch needn't exist at all.</p>
</div></details>

<details class="accordion"><summary>What lets V3 dare to delete heartbeats, and why does V2 keep them?</summary><div class="acc-body">
<p><strong>What lets V3 dare to delete:</strong> it changed the continuation signal. The old mechanism asks "does the model want to continue" (subjective, forgettable); V3 asks "did this round call a tool" (objective, unforgettable) — and "called a tool" already entails "the result must be fed back to the model," naturally equivalent to "continue." A more reliable signal makes the heartbeat param redundant.</p>
<p><strong>Why V2 keeps them:</strong> V2 is the async version that evolved smoothly from the old MemGPT loop, and its continuation criterion is still <span class="mono">continue_stepping = request_heartbeat</span>, keeping heartbeats <strong>for compatibility with the old design</strong>. Deleting them is a step only V3 took.</p>
<p><strong>How to remember:</strong> look at the boolean <span class="mono">_get_valid_tools</span> passes — V2 passes <span class="mono">True</span> (add heartbeats), V3 passes <span class="mono">False</span> (don't). One param's difference is the watershed between the two generations.</p>
<p><strong>One line for this evolution:</strong> from "the model raises its hand for a heartbeat" (the elder <span class="mono">Agent</span>) → made async but still keeping heartbeats (<span class="mono">V2</span>) → switched wholesale to "called a tool → continue" (<span class="mono">V3</span>). Each generation nudges the "continue" decision a little further back from the model to the framework.</p>
<p><strong>Where in the source:</strong> <span class="mono">letta_agent_v2.py::_get_valid_tools</span> vs <span class="mono">letta_agent_v3.py::_get_valid_tools</span>; for continuation see <span class="mono">letta_agent_v3.py::_decide_continuation</span> (lesson 14).</p>
</div></details>

<h2>Next stop</h2>
<p>This lesson chased one design-evolution line: old MemGPT / the elder <span class="mono">Agent</span> / V2 stuff every non-terminal tool with a required <span class="mono">request_heartbeat</span>, letting the model raise its own hand to step again; when a local model forgets, <span class="mono">insert_heartbeat</span> backs it up. By V3, the whole set is replaced by "called a tool → continue" — the param, the heartbeat messages, and the "model forgot to set it" bug, all swept away together.</p>

<p>This loops right back to lesson 14's <span class="mono">_decide_continuation</span> criterion, and echoes the "no heartbeats" in its comment. And the recurring "tool rules can override the heartbeat flag" in the old mechanism (<span class="mono">has_children_tools / is_terminal_tool / is_continue_tool</span>) is exactly the star of the next lesson, lesson 16 — how <span class="mono">tool_rules</span> (terminal / required / approval) actually steer this loop.</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">Take one line away: <strong>the old mechanism makes the model set <span class="mono">request_heartbeat=true</span> to step again; V3 switches to "called a tool → continue," taking that decision back from the model to the framework — delete one param, kill one bug-class.</strong></span></div>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>What request_heartbeat is</strong>: a <strong>required</strong> boolean param the old mechanism adds to every <strong>non-terminal tool</strong>; the model must set it <span class="mono">true</span> to step again. Injected in <span class="mono">tool_parser_helper.py::runtime_override_tool_json_schema</span>.</li>
    <li><strong>How the old mechanism continues</strong>: model sets <span class="mono">true</span> → the framework injects a <span class="mono">REQ_HEARTBEAT_MESSAGE</span> (<span class="mono">role=user</span>, hidden from the user) → continue; tool fails → inject <span class="mono">FUNC_FAILED_HEARTBEAT_MESSAGE</span> → continue; otherwise <span class="mono">break</span>. Parsing is in <span class="mono">agent.py::_handle_ai_response</span>, chaining in <span class="mono">agent.py::step</span>.</li>
    <li><strong>insert_heartbeat</strong>: local models often forget the flag (<span class="mono">issue #601</span>) → when the previous message is a user message and this is a non-<span class="mono">send_message</span> tool call, force in <span class="mono">request_heartbeat=True</span> (<span class="mono">local_llm/function_parser.py</span>).</li>
    <li><strong>V3 removes it</strong>: <span class="mono">_get_valid_tools</span> passes <span class="mono">request_heartbeat=False</span> ("NOTE: difference for v3"), and continuation is decided by <span class="mono">_decide_continuation</span>'s "called a tool → continue"; it also <span class="mono">args.pop(REQUEST_HEARTBEAT_PARAM)</span> to defensively drop any leftover.</li>
    <li><strong>Don't misremember</strong>: <strong>V2 still uses heartbeats</strong> (passes <span class="mono">True</span>), only V3 deletes them; parsing is in <span class="mono">_handle_ai_response</span>, not <span class="mono">inner_step</span>; the old mechanism's <span class="mono">finish_reason=="length"</span> is a <span class="mono">raise</span>, not a heartbeat.</li>
    <li><strong>Design spark</strong>: pull "continue or not" from "the model's conscientiousness" back to "the framework's certainty" — delete one param, kill one bug-class.</li>
    <li><strong>Source</strong>: <span class="mono">tool_parser_helper.py::runtime_override_tool_json_schema</span>, <span class="mono">agent.py::_handle_ai_response / step</span>, <span class="mono">local_llm/function_parser.py::insert_heartbeat</span>, <span class="mono">letta_agent_v3.py::_get_valid_tools</span>, <span class="mono">constants.py</span> heartbeat constants.</li>
  </ul>
</div>
""",
}
