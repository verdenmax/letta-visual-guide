"""Part 8 - Advanced topics (lessons 28-31).

Lesson 28 opens Part 8: multi-agent and sleeptime. In letta v0.16.8 only two
multi-agent mechanisms are actually live:

    send_message_to_agent_* tools (agent A re-enters the server over REST and
        runs agent B's own loop) -> direct agent-to-agent calls
    sleeptime (a foreground agent finishes, then a background sleeptime agent is
        woken every N turns to rewrite memory) -> a shared Block row is the only
        coordination primitive

The classic group managers (round_robin / supervisor / dynamic) survive only as
schema / enum / class skeletons; their executor load_multi_agent is never called.
Each lesson dict mirrors the house style of Parts 1-7 (cards / notes / cute /
codefile / vflow / cols / cellgroup / table.t), with cross-refs back to earlier
lessons. zh is authored first; en starts as a stub for the next agent.
"""

LESSON_28 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第七部分我们把一条请求一路送进数据库——三层楼、统一柜台、焊死的租户门禁，agent 终于在服务端站稳了。第八部分换一个问题：当桌上<strong>不止一个 agent</strong> 时，它们怎么协作？谁来调度？记忆又怎么跨 agent 流动？</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课先把一个反直觉的事实摆上桌：v0.16.8 里<strong>真正活着</strong>的多智能体只有两条——一个 agent 直接调另一个的消息 API（<span class="mono">send_message_to_agent_*</span>），以及后台 sleeptime agent 每隔几回合醒来改记忆。经典的"群管理器"基本是睡着的脚手架。</p>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>v0.16.8 的多智能体不是"一个调度器编排一群 agent"，而是"agent 之间互相调 API ＋ 共享一行记忆"</strong>。</p>
<p>真路径一：<span class="mono">send_message_to_agent_and_wait_for_reply</span> 这类工具，让 agent A 经 REST <strong>重入服务器</strong>、跑 agent B 自己完整的 loop，再把 B 的回复取回来。</p>
<p>真路径二：<strong>sleeptime</strong>——前台 agent 跑完一轮，后台一个 sleeptime agent 被拉起，专职<strong>整理记忆</strong>。</p>
<p>两者唯一的协调基元，朴素到只是<strong>一行共享的 <span class="mono">Block</span></strong>：A 写、B 下次重建 system prompt 时读到。</p>
<p>至于经典群管理器（<span class="mono">round_robin / supervisor / dynamic</span>）？只剩 schema 与类骨架，执行器<strong>从未被调用</strong>。</p>
</div>
<p>先把"两条真路径 ＋ 一行共享记忆"摆成左右两栏，心里有个骨架，后面再逐条拆开。</p>
<div class="cols">
  <div class="col"><h4>🛠️ 路径一 · agent 直接调 agent</h4>
  <p>A 调 <span class="mono">send_message_to_agent_and_wait_for_reply</span> → 沙箱里建 client → <span class="mono">messages.create(B)</span> 经 REST 重入 → 跑 <strong>B 自己的 loop</strong> → 回复回灌给 A。</p>
  <p>不经任何"群管理器"，就是一次<strong>普通的对外 API 调用</strong>，只不过被调方恰好也是个 agent。</p>
  </div>
  <div class="col"><h4>😴 路径二 · sleeptime 后台改记忆</h4>
  <p>前台 agent 跑完 → 回合计数器到点 → <strong>非阻塞</strong>拉起后台 sleeptime agent → 它用记忆工具改写<strong>共享 Block</strong>。</p>
  <p>前台<strong>不等</strong>它；下一回合重建 system prompt 时，自然就读到被整理过的记忆。</p>
  </div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">底注：经典群管理器（<span class="mono">round_robin / supervisor / dynamic</span>）只停在 <strong>schema 级</strong>——枚举、ORM、类骨架都在，但<strong>没接线</strong>，无法经 live API 跑起来。本课只认那两条活路。</span></div>
<h2>先数清楚：v0.16.8 里"活着"的多智能体有几条</h2>
<p>很多人一上来就找"群聊调度器"——以为有个对象负责排队、让 A、B、C 轮流说话。v0.16.8 里这个对象<strong>基本是睡着的</strong>。</p>
<p>群管理器的执行入口 <span class="mono">groups/helpers.py::load_multi_agent</span> 在整个 live 路径里<strong>从未被调用</strong>；<span class="mono">/v1/groups</span> 路由整段 <span class="mono">deprecated=True</span> 且<strong>没有发消息端点</strong>；连 <span class="mono">SupervisorMultiAgent.step</span> 都<strong>整段被注释掉</strong>。</p>
<p>所以先把六种 <span class="mono">ManagerType</span> 枚举的"设想行为"和"v0.16.8 真实状态"并排列清楚——只有一行是绿的。</p>
<table class="t">
<tr><th>ManagerType 枚举</th><th>设想的路由行为</th><th>v0.16.8 真实状态</th></tr>
<tr><td class="mono">round_robin</td><td>成员轮流发言</td><td>休眠：枚举/ORM 在，执行器未接线</td></tr>
<tr><td class="mono">supervisor</td><td>主管把消息分派给下属</td><td>骨架：<span class="mono">SupervisorMultiAgent.step</span> 整段注释掉</td></tr>
<tr><td class="mono">dynamic</td><td>由 LLM 动态挑下一个发言者</td><td>休眠：未接线</td></tr>
<tr><td class="mono">sleeptime</td><td>前台跑完，后台 agent 改记忆</td><td><strong>ACTIVE ✅</strong>：本课主角</td></tr>
<tr><td class="mono">voice_sleeptime</td><td>语音场景的 sleeptime 变体</td><td>voice 专用（另走一套工具）</td></tr>
<tr><td class="mono">swarm</td><td>OpenAI swarm 式交接</td><td>未实现</td></tr>
</table>
<p>记住这张表的主线：<strong>真正能经 live API 跑起来的群行为，只有 <span class="mono">sleeptime</span> 那一行</strong>。其余几行是历史遗留或半成品，看代码时别被它们的存在骗了。</p>
<p>那"agent 直接调 agent"（路径一）呢？它<strong>根本不在这张表里</strong>——它不是某种 group manager，而是一组<strong>工具</strong>，下一节专讲。</p>
<div class="card analogy"><div class="tag">📝 生活类比</div>
<p>把团队想成一家<strong>小店</strong>，柜台后挂着一块<strong>共享留言板</strong>（共享 <span class="mono">Block</span>）。</p>
<p>白班店员（前台 agent）一整天接客，随手在留言板上记几笔潦草的便条。</p>
<p>下班前，夜班整理员（sleeptime agent）被叫醒，把这天的便条<strong>整理进同一块留言板</strong>——擦掉重复、补上要点。</p>
<p>第二天白班一上班，看到的就是<strong>整理好的版本</strong>，根本不知道夜里有人来过。</p>
<p>店员之间也能<strong>直接递条子</strong>（<span class="mono">send_message_to_agent</span>）：把问题写给隔壁柜台，等对方写回来——这就是路径一。</p>
</div>
<details class="accordion"><summary>经典群管理器为什么是"睡着的脚手架"？</summary><div class="acc-body">
<p>三处硬证据。其一：执行器 <span class="mono">groups/helpers.py::load_multi_agent</span> 在 live 路径里<strong>从未被调用</strong>——它能按 <span class="mono">manager_type</span> 造出对应的多智能体对象，但没人去 new 它。</p>
<p>其二：<span class="mono">/v1/groups</span> 整段路由标着 <span class="mono">deprecated=True</span>，而且<strong>压根没有"给 group 发消息"的端点</strong>——你能 CRUD 一个 group 行，却无法让它跑起来。</p>
<p>其三：<span class="mono">SupervisorMultiAgent.step</span> 的方法体<strong>整段被注释掉</strong>，调它等于什么都不做。</p>
<p>结论：<span class="mono">round_robin / supervisor / dynamic</span> 在 v0.16.8 只是 <strong>schema ＋ 枚举 ＋ 类骨架</strong>，是给未来留的座位，不是今天能用的功能。</p>
</div></details>
<h2>第一条活路：send_message_to_agent_*（agent 直接调 agent）</h2>
<p>路径一不是"调度"，而是<strong>工具调用</strong>。它们登记在 <span class="mono">functions/function_sets/multi_agent.py</span>，归类 <span class="mono">ToolType.LETTA_MULTI_AGENT_CORE</span>，和别的工具一样<strong>在沙箱里执行</strong>。</p>
<p>核心机制只有一句：工具体内<strong>建一个 <span class="mono">letta_client.Letta</span> 客户端</strong>，调 <span class="mono">client.agents.messages.create(agent_id=other_agent_id, ...)</span>——经 REST <strong>重入服务器</strong>，跑被叫 agent B 自己<strong>完整的 loop</strong>（<span class="mono">AgentLoop.load(B).step</span>），全程<strong>不经群管理器</strong>。</p>
<p>把这条调用链画出来：</p>
<div class="flow">
  <div class="node hl"><div class="nt">Agent A</div><div class="nd">调 wait_for_reply 工具</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">工具沙箱</div><div class="nd">建 letta_client.Letta</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">REST 重入</div><div class="nd">messages.create(B)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Agent B 的 loop</div><div class="nd">AgentLoop.load(B).step</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">回复回灌 A</div><div class="nd">取 B 的 assistant 消息</div></div>
</div>
<p>注意发送方身份是<strong>自动注入</strong>的：B 收到的消息会被打上 <span class="mono">[Incoming message from agent with ID '...']</span> 前缀，所以 B 知道"这条是另一个 agent 发来的"。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/multi_agent.py</span><span class="ln">send_message_to_agent_and_wait_for_reply：经 REST 重入、跑 B 的 loop（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">send_message_to_agent_and_wait_for_reply</span>(self, message: str, other_agent_id: str) -&gt; str:
    <span class="cm"># 工具在沙箱里执行：建一个面向本服务器的客户端</span>
    client = <span class="fn">Letta</span>(base_url=self.base_url, token=self.token)
    <span class="cm"># 经 REST 把消息投给 B —— 跑的是 B 自己完整的 loop，不经群管理器</span>
    response = client.agents.messages.<span class="fn">create</span>(
        agent_id=other_agent_id,
        messages=[{<span class="st">&quot;role&quot;</span>: <span class="st">&quot;system&quot;</span>, <span class="st">&quot;content&quot;</span>: message}],  <span class="cm"># 自动带 [Incoming message from agent ...] 前缀</span>
    )
    <span class="cm"># 同步阻塞：把 B 的 assistant 回复抽出来，回灌给调用方 A</span>
    <span class="kw">return</span> <span class="fn">extract_assistant_reply</span>(response.messages)
</pre></div>
<details class="accordion"><summary><span class="mono">send_message_to_agent_*</span> 的三个变体差在哪？</summary><div class="acc-body">
<p><strong>① <span class="mono">..._and_wait_for_reply(message, other_agent_id)</span></strong>：<strong>同步阻塞</strong>、双向——发给一个 agent，<strong>等</strong>它把回复写回来再继续。最常用。</p>
<p><strong>② <span class="mono">..._to_agents_matching_tags(message, match_all, match_some)</span></strong>：<strong>同步广播</strong>——按标签筛出一批 agent，<strong>逐个</strong>发送并等待。一对多。</p>
<p><strong>③ <span class="mono">..._to_agent_async(message, other_agent_id)</span></strong>：<strong>异步单向</strong>——发了就走、不等回复；注意它在<strong>生产环境被禁用</strong>。</p>
<p>三者共用同一机制（建 client → <span class="mono">messages.create</span> → 跑对方 loop），区别只在<strong>等不等回复</strong>、<strong>一个还是一批</strong>。</p>
</div></details>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">别把这条路径和 sleeptime 搞混：<span class="mono">..._and_wait_for_reply</span> 是<strong>同步阻塞</strong>——A 会卡住等 B 跑完。后面 sleeptime 恰恰相反，是<strong>非阻塞</strong>后台任务。两种"多 agent"在阻塞语义上完全相反。</span></div>
<h2>第二条活路：sleeptime（后台 agent 悄悄改记忆）</h2>
<p>sleeptime 才是 v0.16.8 唯一<strong>真正活着</strong>的"群"行为。接线点在 <span class="mono">agents/agent_loop.py::AgentLoop.load</span>：当 agent 是 <span class="mono">letta_v1_agent / sleeptime_agent</span>、开了 <span class="mono">enable_sleeptime</span>、且挂在一个 group 上，就交给 <span class="mono">SleeptimeMultiAgentV4</span>。</p>
<p>最关键的一点先说破：<span class="mono">groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4</span> <strong>直接继承 <span class="mono">LettaAgentV3</span></strong>——它<strong>就是第 13、14 课那个普通 loop 的子类</strong>，不是什么特殊子系统。</p>
<p>它的 <span class="mono">step</span> 干两件事：先 <span class="mono">await super().step(...)</span> 把<strong>前台主 agent</strong> 正常跑一轮、存下 <span class="mono">response_messages</span>；再调 <span class="mono">run_sleeptime_agents()</span> 看看要不要叫醒后台。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/groups/sleeptime_multi_agent_v4.py</span><span class="ln">SleeptimeMultiAgentV4：前台先跑，再非阻塞拉起后台（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">SleeptimeMultiAgentV4</span>(LettaAgentV3):       <span class="cm"># 注意：它就是普通 loop 的子类</span>
    <span class="kw">async def</span> <span class="fn">step</span>(self, input_messages, ...):
        <span class="cm"># 1) 前台主 agent 照常跑一轮，存下这轮产出的消息</span>
        response_messages = <span class="kw">await</span> <span class="fn">super</span>().<span class="fn">step</span>(input_messages, ...)
        <span class="cm"># 2) 看看要不要叫醒后台 sleeptime agents</span>
        <span class="kw">await</span> self.<span class="fn">run_sleeptime_agents</span>(response_messages)
        <span class="kw">return</span> response_messages

    <span class="kw">async def</span> <span class="fn">run_sleeptime_agents</span>(self, response_messages):
        count = <span class="kw">await</span> group_manager.<span class="fn">bump_turns_counter_async</span>(self.group.id)  <span class="cm"># (c+1) % frequency</span>
        <span class="kw">if</span> count % self.group.sleeptime_agent_frequency != 0:
            <span class="kw">return</span>                                   <span class="cm"># 没到点，跳过</span>
        <span class="kw">for</span> agent_id <span class="kw">in</span> self.group.agent_ids:     <span class="cm"># 后台编辑者们</span>
            <span class="kw">await</span> self.<span class="fn">_issue_background_task</span>(agent_id, response_messages)  <span class="cm"># 非阻塞 safe_create_task</span>
</pre></div>
<p>逐句读：<span class="mono">bump_turns_counter_async</span> 把计数器推进 <span class="mono">(c+1) % frequency</span>；只有<strong>整除（<span class="mono">% frequency == 0</span>）</strong>才命中。</p>
<p>命中后，对 <span class="mono">group.agent_ids</span> 里的<strong>每个后台 sleeptime agent</strong> 做 <span class="mono">_issue_background_task</span>：建一个 <span class="mono">Run</span>，再 <span class="mono">safe_create_task(_participant_agent_step)</span>——一个<strong>非阻塞的 asyncio 后台任务</strong>。前台<strong>不等</strong>它。</p>
<p>那后台任务做什么？<span class="mono">_participant_agent_step</span> 把 <span class="mono">prior + response_messages</span> 拼成 transcript，包进一段 <span class="mono">&lt;system-reminder&gt;</span>——"你是后台 sleeptime agent，职责是记忆管理，用记忆工具更新相关 block"，再以<strong>完整的 <span class="mono">LettaAgentV3</span></strong> 跑 <span class="mono">step</span>。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>User → 前台 step</h4><p>用户消息进来，<span class="mono">SleeptimeMultiAgentV4.step</span> 先 <span class="mono">await super().step()</span> 跑前台主 agent。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>bump_turns_counter</h4><p>计数器推进 <span class="mono">(c+1) % frequency</span>；问一句：<span class="mono">% frequency == 0</span> 吗？</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>命中 → 非阻塞拉起</h4><p>到点则对每个后台 agent <span class="mono">safe_create_task(_participant_agent_step)</span>；前台<strong>不等</strong>，直接返回。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>sleeptime step → memory_rethink</h4><p>后台 agent 以完整 <span class="mono">LettaAgentV3</span> 跑 <span class="mono">step</span>，用 <span class="mono">memory_rethink</span> 改写记忆。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>写共享 Block（version++）</h4><p>新内容落到那一行 <span class="mono">Block</span>，乐观锁 <span class="mono">version</span> 自增。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>下回合前台读到</h4><p>前台下一回合重建 system prompt 时，自然读到被整理过的新值。</p></div></div>
</div>
<details class="accordion"><summary>sleeptime 多久触发一次？为什么"第一回合就触发"？</summary><div class="acc-body">
<p>频率由 <span class="mono">group.sleeptime_agent_frequency</span> 决定，默认 <strong>5</strong>（见 <span class="mono">server.py::create_sleeptime_agent_async</span>）。</p>
<p>命中条件是 <span class="mono">bump_turns_counter</span> 推进后 <span class="mono">% frequency == 0</span>。</p>
<p>玄机在初值：<span class="mono">GroupManager.create_group_async</span> 给 sleeptime 把 <span class="mono">turns_counter</span> 设成 <strong><span class="mono">-1</span></strong>。第一回合 <span class="mono">(-1+1)=0</span>，<span class="mono">0 % 5 == 0</span> → <strong>首回合就命中</strong>。</p>
<p>于是新建的 sleeptime agent 不必干等 5 回合，第一轮对话后台就开始整理记忆了。</p>
</div></details>
<div class="note tip"><span class="ni">🧠</span><span class="nx">记住这条因果链：<strong>sleeptime ＝ 同一个 <span class="mono">LettaAgentV3</span> loop ＋ 一行共享记忆 ＋ 一个回合计数器</strong>。没有"特殊的记忆整理子系统"——只是把普通 agent 丢进一段 transcript、给它记忆工具、告诉它"你的活儿是整理记忆"。</span></div>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">functions/function_sets/multi_agent.py</span>——三个 <span class="mono">send_message_to_agent_*</span> 工具，<span class="mono">LETTA_MULTI_AGENT_CORE</span>，沙箱执行。</p>
<p><span class="mono">groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4</span>——继承 <span class="mono">LettaAgentV3</span>；<span class="mono">step</span> 先 <span class="mono">super().step()</span> 再 <span class="mono">run_sleeptime_agents</span>。</p>
<p><span class="mono">orm/blocks_agents.py::BlocksAgents</span>——复合主键 <span class="mono">(agent_id, block_id, block_label)</span>，让一行 Block 挂到多个 agent。</p>
<p><span class="mono">services/tool_executor/core_tool_executor.py::CoreToolExecutor.memory_rethink</span>——sleeptime 改记忆的落点。</p>
</div>
<h2>唯一的协调基元：共享的一行 Block</h2>
<p>两个 agent 怎么"商量"？答案朴素到让人意外：它们<strong>指向同一行 <span class="mono">Block</span></strong>。没有消息队列、没有共享内存对象，就是数据库里<strong>同一条记录</strong>。</p>
<p>让一行 Block 挂到多个 agent 的，是关联表 <span class="mono">orm/blocks_agents.py::BlocksAgents</span>：复合主键 <span class="mono">(agent_id, block_id, block_label)</span>。<span class="mono">Block.agents</span> ↔ <span class="mono">Agent.core_memory</span> 经 <span class="mono">secondary="blocks_agents"</span> 多对多相连。</p>
<p>谁把它们接到一起？<span class="mono">server.py::SyncServer.create_sleeptime_agent_async</span> 建 sleeptime agent 时，传 <span class="mono">block_ids=[b.id for b in main_agent.memory.blocks]</span>——<strong>同一批 Block 行</strong>，不是副本。</p>
<div class="cellgroup"><div class="cg-cap"><b>一行 Block 挂多个 agent：<span class="mono">blocks_agents.py::BlocksAgents</span> 复合主键</b></div><div class="cells"><span class="cell hl">agent_id</span><span class="sep">·</span><span class="cell hl">block_id</span><span class="sep">·</span><span class="cell hl">block_label</span><span class="sep">→</span><span class="cell">Block.version（乐观锁）</span></div></div>
<p>把"两个 agent 共享同一行"画出来——注意中间那行 <span class="mono">Block</span> 只有一个 <span class="mono">block_id</span>：</p>
<div class="flow">
  <div class="node"><div class="nt">前台主 agent</div><div class="nd">core_memory</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">blocks_agents</div><div class="nd">(agent_id, block_id, label)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">同一行 Block</div><div class="nd">block_id 唯一 · version</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">blocks_agents</div><div class="nd">(agent_id, block_id, label)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">后台 sleeptime agent</div><div class="nd">core_memory</div></div>
</div>
<p>读法：两端是两个 agent 的 core memory，中间经 <span class="mono">blocks_agents</span> 各自连到<strong>同一行 Block</strong>。sleeptime 在右边写，前台在左边读——共享的就是中间那一行。</p>
<p>sleeptime 用什么工具改这行？标准 sleeptime 配 <span class="mono">constants.py::BASE_SLEEPTIME_TOOLS</span> ＝ <span class="mono">memory_replace / memory_insert / memory_rethink / memory_finish_edits</span>，实现都在 <span class="mono">CoreToolExecutor</span>。看其中的 <span class="mono">memory_rethink</span>：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">memory_rethink：改写共享 Block 那一行（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">memory_rethink</span>(self, agent_state, label: str, new_memory: str):
    block = agent_state.memory.<span class="fn">get_block</span>(label)
    <span class="kw">if</span> block.read_only:                       <span class="cm"># 只读块：拒绝改写</span>
        <span class="kw">raise</span> <span class="fn">ValueError</span>(<span class="st">&quot;cannot rethink a read-only block&quot;</span>)
    <span class="cm"># 整块替换 label 对应的内容</span>
    agent_state.memory.<span class="fn">update_block_value</span>(label=label, value=new_memory)
    <span class="cm"># 内容变了才写库：落到那一行共享 Block（version 自增）</span>
    <span class="kw">await</span> agent_manager.<span class="fn">update_memory_if_changed_async</span>(agent_state)
    <span class="kw">return</span> <span class="kw">None</span>                              <span class="cm"># memory_finish_edits 同样返回 None，收尾</span>
</pre></div>
<p>三步：拒只读块 → <span class="mono">update_block_value(label, new_memory)</span> 整块替换 → <span class="mono">update_memory_if_changed_async</span> 把新值写进那一行共享 Block。<span class="mono">memory_finish_edits</span> 则只 <span class="mono">return None</span> 收尾。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">易错纠正：标准 sleeptime 的"重想记忆"是 <span class="mono">memory_rethink</span>，<strong>不是</strong> <span class="mono">rethink_memory</span>（legacy）或 <span class="mono">finish_rethinking_memory</span>（voice 专用）。看 v0.16.8 时认准 <span class="mono">BASE_SLEEPTIME_TOOLS</span> 那四个。</span></div>
<details class="accordion"><summary>sleeptime 改了记忆，前台<strong>什么时候</strong>才看得见？</summary><div class="acc-body">
<p>不是即时的。sleeptime 调 <span class="mono">memory_rethink</span> → <span class="mono">update_memory_if_changed_async</span> 把新值写进那一行 <span class="mono">Block</span>，仅此而已——它没去"通知"前台。</p>
<p>前台是在<strong>下一回合重建 system prompt</strong> 时，把这行 Block 重新编译进 core memory，才读到新值（回扣第 08、09 课：core memory 每回合从 block 现编）。</p>
<p><span class="mono">Block</span> 带乐观锁 <span class="mono">version</span>：并发写按版本号检测冲突，避免后台与前台互相覆盖。</p>
<p>所以"共享"共享的是<strong>那一行的当前值</strong>，可见性边界是"下次重建 prompt"，不是"立刻推送"。</p>
</div></details>
<h2>一处最反直觉的接线：谁才是"管理者"？</h2>
<p>sleeptime 的 group 里有两个字段最容易认反。<span class="mono">manager_agent_id</span> 听着像"协调者"，其实是<strong>前台主 agent</strong>；<span class="mono">group.agent_ids</span> 听着像"普通成员"，其实是<strong>后台编辑者</strong>（那些 sleeptime agents）。</p>
<p>换句话说：跑用户对话的"主角"被记成 <span class="mono">manager</span>，真正干"整理记忆"脏活的后台 agent 反而躺在 <span class="mono">agent_ids</span> 里。命名与直觉正好相反，读 <span class="mono">orm/group.py::Group</span> 时务必盯紧。</p>
<p><span class="mono">Group</span> 这行还带着 <span class="mono">manager_type / manager_agent_id / sleeptime_agent_frequency / turns_counter / agent_ids</span>，并经 M2M 表 <span class="mono">groups_agents</span> 连到 <span class="mono">agents</span>——一张表把"谁是主角、谁是夜班、多久叫一次"全记下了。</p>
<div class="cute"><div class="row"><span class="emoji">😴</span><span class="lab">主 agent 在睡</span><span class="arrow">→</span><span class="emoji">🧠</span><span class="lab">记忆块被悄悄擦改</span><span class="arrow">→</span><span class="emoji">✨</span><span class="bubble">睡醒记忆更好</span></div><div class="cap">😴 前台主 agent "睡着"的间隙，sleeptime agent 把 🧠 共享记忆块擦掉、重写成更整洁的版本，✨ 主 agent 下回合醒来，记忆已被整理好——它甚至不知道夜里有人来过</div></div>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>sleeptime ＝ 把"记忆整理"<strong>实现成 agent 抽象的递归套用</strong>。后台那个"记忆整理器"不是特殊子系统——它就是<strong>另一个 <span class="mono">LettaAgentV3</span></strong>（<span class="mono">SleeptimeMultiAgentV4</span> 干脆继承普通 loop）。</p>
<p>它被丢进一段 transcript、戴上 <span class="mono">sleeptime_memory_persona</span>、给一套记忆工具，然后被告知"你的活儿是整理记忆"——仅此而已。</p>
<p>两个 agent 之间的协调基元，朴素到只是一个<strong>共享可变的 <span class="mono">Block</span> 行</strong>：A 写、B 下次重建 system prompt 时读到。</p>
<p>于是整个特性 ＝（同一个 loop）＋（一行共享记忆）＋（一个回合计数器）。三块积木，没有第四块。</p>
<p>最反直觉的推论：v0.16.8 <strong>根本没有专门的"多智能体运行时"</strong>——<span class="mono">round_robin / supervisor</span> 那套是睡着的脚手架，真多智能体行为全从"一个 agent 调另一个的 API"和"两个 agent 指向同一个 block"里<strong>涌现</strong>。</p>
</div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>标准 sleeptime 的记忆工具是 <span class="mono">memory_rethink</span>，<strong>不是</strong> <span class="mono">rethink_memory</span>（legacy）或 <span class="mono">finish_rethinking_memory</span>（voice 专用）。</p>
<p>阻塞语义相反：<span class="mono">..._and_wait_for_reply</span> <strong>同步阻塞</strong>，sleeptime 后台任务<strong>非阻塞</strong>。别拿一个的直觉套另一个。</p>
<p>字段易认反：sleeptime 的 <span class="mono">manager_agent_id</span> ＝<strong>前台主 agent</strong>，<span class="mono">group.agent_ids</span> ＝<strong>后台编辑者</strong>。</p>
<p>"共享块"共享的是<strong>同一行 Block</strong>，不是各持一份副本——改一处，另一个 agent 下次重建 prompt 就见到。</p>
<p><span class="mono">round_robin / supervisor / dynamic</span> 在 v0.16.8 <strong>不能经 live API 跑</strong>，别照着 schema 以为它们能用。</p>
</div>
<!--ZHMORE-->
""",
    "en": r"""<p>stub</p>""",
}
