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
<p>开讲前先校准期待：若你冲着"像编排框架那样的多智能体调度"而来，v0.16.8 会让你略感意外——它给的不是一个编排层，而是<strong>两条更底层的原语</strong>。理解了这两条，你反而能在其上自己搭出编排。</p>
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
<p>为什么留着这些睡着的枚举？因为它们是<strong>设计意图的化石</strong>：曾设想过 round_robin/supervisor 式编排，schema 也铺好了，但重心转向了"单 agent ＋ sleeptime 记忆"，执行层便一直没接。读它们能看懂方向，但别当能用的功能。</p>
<p>那"agent 直接调 agent"（路径一）呢？它<strong>根本不在这张表里</strong>——它不是某种 group manager，而是一组<strong>工具</strong>，下一节专讲。</p>
<p>所以脑子里要分两层：<strong>group / ManagerType</strong> 是"一群 agent 的配置对象"，目前只有 sleeptime 那类真在用；而 <strong>send_message 工具</strong>是"agent 手里的一把锤子"，谁都能拿起来敲另一个 agent，跟 group 毫无关系。</p>
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
<p>B 跑完后，A 怎么"听见"回复？工具把 <span class="mono">response.messages</span> 里 B 的 assistant 消息抽出来，作为这次工具调用的<strong>返回值</strong>交回 A 的 loop——于是在 A 看来，"问另一个 agent"和"调一个普通工具拿到字符串"没有区别。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/multi_agent.py</span><span class="ln">send_message_to_agent_and_wait_for_reply：经 REST 重入、跑 B 的 loop（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">send_message_to_agent_and_wait_for_reply</span>(message: str, other_agent_id: str) -&gt; str:
    <span class="cm"># 工具在沙箱里执行：建一个面向本服务器的客户端</span>
    client = <span class="fn">_get_sandbox_client</span>()
    <span class="cm"># 经 REST 把消息投给 B —— 跑的是 B 自己完整的 loop，不经群管理器</span>
    response = client.agents.messages.<span class="fn">create</span>(
        agent_id=other_agent_id,
        messages=[{<span class="st">&quot;role&quot;</span>: <span class="st">&quot;system&quot;</span>, <span class="st">&quot;content&quot;</span>: message}],  <span class="cm"># 自动带 [Incoming message from agent ...] 前缀</span>
    )
    <span class="cm"># 同步阻塞：把 B 的 assistant 回复抽出来，回灌给调用方 A</span>
    <span class="kw">return</span> <span class="fn">extract_assistant_reply</span>(response.messages)
</pre></div>
<p>为什么要绕一圈 REST，而不在进程内直接调 B？因为工具在<strong>沙箱</strong>里跑（回扣第 20 课），它能拿到的只是一个普通客户端句柄；于是 A 调 B，和一个外部脚本调 B <strong>走同一条公开 API</strong>，隔离与鉴权一视同仁。</p>
<p>这也解释了为什么 B 跑的是"自己<strong>完整的</strong> loop"：服务器收到 <span class="mono">messages.create(B)</span> 就照常 <span class="mono">AgentLoop.load(B).step</span>，B 该调工具调工具、该写记忆写记忆，A 只在最后拿回它的 assistant 回复。</p>
<details class="accordion"><summary><span class="mono">send_message_to_agent_*</span> 的三个变体差在哪？</summary><div class="acc-body">
<p><strong>① <span class="mono">..._and_wait_for_reply(message, other_agent_id)</span></strong>：<strong>同步阻塞</strong>、双向——发给一个 agent，<strong>等</strong>它把回复写回来再继续。最常用。</p>
<p><strong>② <span class="mono">..._to_agents_matching_tags(message, match_all, match_some)</span></strong>：<strong>同步广播</strong>——按标签筛出一批 agent，<strong>逐个</strong>发送并等待。一对多。</p>
<p><strong>③ <span class="mono">..._to_agent_async(message, other_agent_id)</span></strong>：<strong>异步单向</strong>——发了就走、不等回复；注意它在<strong>生产环境被禁用</strong>。</p>
<p>三者共用同一机制（建 client → <span class="mono">messages.create</span> → 跑对方 loop），区别只在<strong>等不等回复</strong>、<strong>一个还是一批</strong>。</p>
</div></details>
<p>标签广播（<span class="mono">..._matching_tags</span>）值得单独说一句：它按 <span class="mono">match_all</span> / <span class="mono">match_some</span> 在库里筛出一批 agent，再<strong>逐个 wait</strong>。所以它本质是"循环版的 wait_for_reply"，不是真正并行群发——一对多，但仍同步串行。</p>
<p>还有个工程提醒：<span class="mono">..._and_wait_for_reply</span> 会让 A 这一步<strong>真的卡住</strong>，直到 B 整轮跑完。若 B 又调 C、C 再调 D，阻塞会一层层叠加——设计 agent 协作时，别让同步等待链拉太长。</p>
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
        <span class="kw">if</span> count % self.group.sleeptime_agent_frequency != <span class="nb">0</span>:
            <span class="kw">return</span>                                   <span class="cm"># 没到点，跳过</span>
        <span class="kw">for</span> agent_id <span class="kw">in</span> self.group.agent_ids:     <span class="cm"># 后台编辑者们</span>
            <span class="kw">await</span> self.<span class="fn">_issue_background_task</span>(agent_id, response_messages)  <span class="cm"># 非阻塞 safe_create_task</span>
</pre></div>
<p>逐句读：<span class="mono">bump_turns_counter_async</span> 把计数器推进 <span class="mono">(c+1) % frequency</span>；只有<strong>整除（<span class="mono">% frequency == 0</span>）</strong>才命中。</p>
<p>命中后，对 <span class="mono">group.agent_ids</span> 里的<strong>每个后台 sleeptime agent</strong> 做 <span class="mono">_issue_background_task</span>：建一个 <span class="mono">Run</span>，再 <span class="mono">safe_create_task(_participant_agent_step)</span>——一个<strong>非阻塞的 asyncio 后台任务</strong>。前台<strong>不等</strong>它。</p>
<p>那后台任务做什么？<span class="mono">_participant_agent_step</span> 把 <span class="mono">prior + response_messages</span> 拼成 transcript，包进一段 <span class="mono">&lt;system-reminder&gt;</span>——"你是后台 sleeptime agent，职责是记忆管理，用记忆工具更新相关 block"，再以<strong>完整的 <span class="mono">LettaAgentV3</span></strong> 跑 <span class="mono">step</span>。</p>
<p>注意它喂给后台的是 <span class="mono">prior + response_messages</span>——也就是<strong>前台刚发生的这轮对话</strong>。后台 agent 不是凭空整理，而是基于"刚说了什么"来决定哪些该写进长期记忆块。它读的是对话，改的是记忆。</p>
<p>这里有个细节别漏：<span class="mono">_issue_background_task</span> 会先建一个 <span class="mono">Run</span> 记录，再 <span class="mono">safe_create_task</span>。<span class="mono">Run</span> 让这次后台整理<strong>可观测、可追踪</strong>——不是"开个任务就忘"，而是和前台一样留下一条可查的执行记录。</p>
<p>那段 <span class="mono">&lt;system-reminder&gt;</span> 也是关键：它把 sleeptime agent 的<strong>身份与职责</strong>临时注入——"你是后台记忆管理者，请用记忆工具更新相关 block"。同一个 loop，靠这段提示语 ＋ <span class="mono">sleeptime_memory_persona</span>，就被"切换"成记忆整理器。</p>
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
<p>"sleeptime"这名字也有讲究：它对应人睡觉时大脑的"记忆巩固"——把白天的短期经历整理进长期记忆。Letta 把这隐喻落成工程：前台对话像"清醒"，后台整理像"睡眠"，两者错峰进行、互不抢占。</p>
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
<p>复合主键是 <span class="mono">(agent_id, block_id, block_label)</span> 三元组：关联按"哪个 agent、哪行 block、挂成什么 label"登记。于是同一行 Block 能稳定地以某个 label 出现在多个 agent 的 core memory 里，既共享值、又各自知道该把它编进 prompt 的哪一段。</p>
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
<p>写库的细节：sleeptime 的改写最终落到 <span class="mono">block_manager</span> 的 <span class="mono">update_block_async</span>（及 <span class="mono">agent_manager</span> 的 <span class="mono">update_memory_if_changed_async</span>）——只改<strong>那一行</strong> Block 的值。前台 agent 的 <span class="mono">core_memory</span> 经 <span class="mono">blocks_agents</span> 指的正是这同一行，于是它"自动"看到更新，无需任何同步代码。</p>
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
    <span class="kw">return</span> new_memory                        <span class="cm"># 返回新内容；真正收尾的是 memory_finish_edits（它才返回 None）</span>
</pre></div>
<p>三步：拒只读块 → <span class="mono">update_block_value(label, new_memory)</span> 整块替换 → <span class="mono">update_memory_if_changed_async</span> 把新值写进那一行共享 Block。<span class="mono">memory_finish_edits</span> 则只 <span class="mono">return None</span> 收尾。</p>
<p>顺带分清 <span class="mono">voice_sleeptime</span>：它是语音场景的变体，走另一套工具（含 <span class="mono">finish_rethinking_memory</span>），和标准 sleeptime 的 <span class="mono">memory_finish_edits</span> 不是一回事。本课只讲标准 sleeptime，遇到 voice 那条线记得它<strong>另有一套</strong>。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">易错纠正：标准 sleeptime 的"重想记忆"是 <span class="mono">memory_rethink</span>，<strong>不是</strong> <span class="mono">rethink_memory</span>（legacy）或 <span class="mono">finish_rethinking_memory</span>（voice 专用）。看 v0.16.8 时认准 <span class="mono">BASE_SLEEPTIME_TOOLS</span> 那四个。</span></div>
<details class="accordion"><summary>sleeptime 改了记忆，前台<strong>什么时候</strong>才看得见？</summary><div class="acc-body">
<p>不是即时的。sleeptime 调 <span class="mono">memory_rethink</span> → <span class="mono">update_memory_if_changed_async</span> 把新值写进那一行 <span class="mono">Block</span>，仅此而已——它没去"通知"前台。</p>
<p>前台是在<strong>下一回合重建 system prompt</strong> 时，把这行 Block 重新编译进 core memory，才读到新值（回扣第 08、09 课：core memory 每回合从 block 现编）。</p>
<p><span class="mono">Block</span> 带乐观锁 <span class="mono">version</span>：并发写按版本号检测冲突，避免后台与前台互相覆盖。</p>
<p>所以"共享"共享的是<strong>那一行的当前值</strong>，可见性边界是"下次重建 prompt"，不是"立刻推送"。</p>
</div></details>
<p>这种"共享一行"的协调，好处是<strong>零额外机制</strong>：不需要消息总线、不需要锁服务，复用的就是你早学过的 Block ＋ 乐观锁。代价则是<strong>弱实时</strong>：peer 的更新要等"下次重建 prompt"才生效，不适合需要毫秒级同步的场景。</p>
<h2>一处最反直觉的接线：谁才是"管理者"？</h2>
<p>sleeptime 的 group 里有两个字段最容易认反。<span class="mono">manager_agent_id</span> 听着像"协调者"，其实是<strong>前台主 agent</strong>；<span class="mono">group.agent_ids</span> 听着像"普通成员"，其实是<strong>后台编辑者</strong>（那些 sleeptime agents）。</p>
<p>换句话说：跑用户对话的"主角"被记成 <span class="mono">manager</span>，真正干"整理记忆"脏活的后台 agent 反而躺在 <span class="mono">agent_ids</span> 里。命名与直觉正好相反，读 <span class="mono">orm/group.py::Group</span> 时务必盯紧。</p>
<p><span class="mono">Group</span> 这行还带着 <span class="mono">manager_type / manager_agent_id / sleeptime_agent_frequency / turns_counter / agent_ids</span>，并经 M2M 表 <span class="mono">groups_agents</span> 连到 <span class="mono">agents</span>——一张表把"谁是主角、谁是夜班、多久叫一次"全记下了。</p>
<p>为什么这么记？因为 sleeptime 的"主语"始终是<strong>前台那次对话</strong>：是它跑完触发了计数器、是它的 <span class="mono">step</span> 顺手叫起后台。后台编辑者只是被它"使唤"的工具人，所以把前台记成 <span class="mono">manager</span>、把后台塞进 <span class="mono">agent_ids</span>，从实现视角反而自洽。</p>
<div class="cute"><div class="row"><span class="emoji">😴</span><span class="lab">趁前台空档</span><span class="arrow">→</span><span class="emoji">🧠</span><span class="lab">记忆块被悄悄擦改</span><span class="arrow">→</span><span class="emoji">✨</span><span class="bubble">睡醒记忆更好</span></div><div class="cap">😴 前台主 agent 两次对话之间的空档，sleeptime agent 把 🧠 共享记忆块擦掉、重写成更整洁的版本，✨ 主 agent 下回合醒来，记忆已被整理好——它甚至不知道刚才有人来过</div></div>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>sleeptime ＝ 把"记忆整理"<strong>实现成 agent 抽象的递归套用</strong>。后台那个"记忆整理器"不是特殊子系统——它就是<strong>另一个 <span class="mono">LettaAgentV3</span></strong>（<span class="mono">SleeptimeMultiAgentV4</span> 干脆继承普通 loop）。同一套"读上下文→调工具→改状态"的机器，对内换个 persona、对外换个触发时机，就成了记忆的"夜班整理员"。</p>
<p>这层递归套用还白送一个红利：整理器既然就是个普通 agent，它跑的每一步同样落 <span class="mono">Step</span> 行、同样能被观测与计费（第 30 课）——"后台记忆整理"不是黑箱，而是又一段可追踪的 agent 执行。</p>
<p>最反直觉的推论：v0.16.8 <strong>根本没有专门的"多智能体运行时"</strong>——<span class="mono">round_robin / supervisor</span> 那套是睡着的脚手架，真多智能体行为全从"一个 agent 调另一个的 API"和"两个 agent 指向同一个 block"里<strong>涌现</strong>。</p>
</div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>标准 sleeptime 的记忆工具是 <span class="mono">memory_rethink</span>，<strong>不是</strong> <span class="mono">rethink_memory</span>（legacy）或 <span class="mono">finish_rethinking_memory</span>（voice 专用）。</p>
<p>阻塞语义相反：<span class="mono">..._and_wait_for_reply</span> <strong>同步阻塞</strong>，sleeptime 后台任务<strong>非阻塞</strong>。别拿一个的直觉套另一个。</p>
<p>字段易认反：sleeptime 的 <span class="mono">manager_agent_id</span> ＝<strong>前台主 agent</strong>，<span class="mono">group.agent_ids</span> ＝<strong>后台编辑者</strong>。</p>
<p>"共享块"共享的是<strong>同一行 Block</strong>，不是各持一份副本——改一处，另一个 agent 下次重建 prompt 就见到。</p>
<p><span class="mono">round_robin / supervisor / dynamic</span> 在 v0.16.8 <strong>不能经 live API 跑</strong>，别照着 schema 以为它们能用。</p>
</div>
<h2>回扣与小结：多智能体是"涌现"出来的</h2>
<p>把这一课收个尾。v0.16.8 的多智能体没有一个气派的"调度中枢"，它是从几个你<strong>早就学过</strong>的零件里拼出来的。</p>
<p>回扣第 13、14 课：sleeptime agent 跑的<strong>就是那个 <span class="mono">LettaAgentV3</span> step loop</strong>——<span class="mono">SleeptimeMultiAgentV4</span> 直接继承它。被叫的 agent B 也一样，跑的是 B 自己的完整 loop。每个"成员"都只是一个普通 agent。</p>
<p>回扣第 08、09 课：sleeptime 改的是 <strong>block ＋ 自编辑记忆</strong> 那一套——<span class="mono">memory_rethink</span> 复用的正是你学过的 core memory 工具，只不过这次写的是<strong>共享</strong>的那一行。</p>
<p>回扣第 25 课：触发节奏靠 <span class="mono">group_manager</span> 的 <span class="mono">bump_turns_counter_async</span> 维护 <span class="mono">turns_counter</span>，正是第七部分那套 service manager 的又一次出场。</p>
<p>于是"多智能体"在 Letta 这里，不是一个新运行时，而是<strong>旧零件的新组合</strong>：同一个 loop、同一套记忆工具、同一个 service manager，外加一行共享 Block 和一个计数器。</p>
<p>这也是 Letta 一以贯之的"少即是多"：与其造一个庞大的多智能体引擎，不如把 agent、block、manager 这几个已被打磨过的抽象<strong>复用到极致</strong>。新行为从旧抽象的组合里涌现，维护面反而最小。</p>
<p>再回扣第 24 课的"三层楼"：A 调 B 这一跳，正是从工具沙箱<strong>重新走了一遍</strong>那条 REST → SyncServer → loop 的下楼梯。多智能体没有绕开架构，而是<strong>把同一条请求路径又跑了一次</strong>，只是这次发起者是另一个 agent。</p>
<p>一句话串起来：路径一让 agent 之间<strong>能说话</strong>（同步调 API），sleeptime 让 agent 之间<strong>能交接记忆</strong>（异步改共享块），而真正把它们粘住的，始终是那一行 <span class="mono">Block</span>。</p>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li>v0.16.8 真正活着的多智能体<strong>只有两条</strong>：<span class="mono">send_message_to_agent_*</span> 工具（A 经 REST 重入、跑 B 自己的 loop）与 <strong>sleeptime</strong>（后台 agent 每 N 回合改记忆）。</li>
<li>经典群管理器 <span class="mono">round_robin / supervisor / dynamic</span> 只剩 schema/枚举/类骨架：<span class="mono">load_multi_agent</span> 从未被调、<span class="mono">/v1/groups</span> deprecated 无发消息端点、<span class="mono">SupervisorMultiAgent.step</span> 注释掉。</li>
<li>sleeptime ＝ <span class="mono">SleeptimeMultiAgentV4(LettaAgentV3)</span>：<span class="mono">step</span> 先 <span class="mono">super().step()</span> 跑前台，再 <span class="mono">run_sleeptime_agents</span>——<span class="mono">% frequency == 0</span> 命中则 <span class="mono">safe_create_task</span> <strong>非阻塞</strong>拉起后台。</li>
<li>协调基元是<strong>一行共享 <span class="mono">Block</span></strong>（<span class="mono">blocks_agents.py::BlocksAgents</span> 复合主键）：sleeptime 用 <span class="mono">memory_rethink</span> 写、前台下回合重建 prompt 才读到；<span class="mono">Block.version</span> 乐观锁。</li>
<li>易认反：sleeptime <span class="mono">manager_agent_id</span> ＝前台主 agent，<span class="mono">group.agent_ids</span> ＝后台编辑者；<span class="mono">turns_counter=-1</span> ＋ 默认频率 5 → 首回合即触发。</li>
</ul>
</div>
<p>把这条肌肉记忆带走：在 Letta 里看到"多 agent"，别先找调度器——先问<strong>"它们调的是谁的 API"</strong>和<strong>"它们指向同一行 Block 吗"</strong>。答得上这两问，多智能体的行为就不再神秘。</p>
<p>第八部分就此开张。下一课我们继续往"进阶专题"里走，把这套"旧零件、新组合"的思路用到更多地方。</p>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Part 7 walked a single request all the way down into the database — three floors, a unified counter, a welded-shut tenant gate; the agent finally stands firm on the server side. Part 8 asks a different question: when there is <strong>more than one agent</strong> at the table, how do they cooperate? Who schedules them? And how does memory flow across agents?</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson starts by putting a counterintuitive fact on the table: in v0.16.8 only two multi-agent mechanisms are <strong>actually live</strong> — one agent directly calling another's message API (<span class="mono">send_message_to_agent_*</span>), and a background sleeptime agent that wakes every few turns to rewrite memory. The classic "group managers" are mostly sleeping scaffolding.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>One sentence to grasp this lesson: <strong>v0.16.8's multi-agent isn't "one scheduler orchestrating a flock of agents," but "agents calling each other's API plus sharing one row of memory."</strong></p>
<p>Live path one: tools like <span class="mono">send_message_to_agent_and_wait_for_reply</span> let agent A <strong>re-enter the server</strong> over REST, run agent B's own full loop, and fetch B's reply back.</p>
<p>Live path two: <strong>sleeptime</strong> — after the foreground agent finishes a turn, a background sleeptime agent is woken up, dedicated to <strong>tidying memory</strong>.</p>
<p>Their only coordination primitive is humble to the point of being just <strong>one shared <span class="mono">Block</span> row</strong>: A writes, and B reads it the next time it rebuilds its system prompt.</p>
<p>As for the classic group managers (<span class="mono">round_robin / supervisor / dynamic</span>)? Only schema and class skeletons remain; their executor is <strong>never called</strong>.</p>
</div>
<p>Let's lay the "two live paths plus one shared memory row" out as two columns first, to get a skeleton in mind before unpacking each one.</p>
<div class="cols">
  <div class="col"><h4>🛠️ Path one · agent calls agent directly</h4>
  <p>A calls <span class="mono">send_message_to_agent_and_wait_for_reply</span> → builds a client in the sandbox → <span class="mono">messages.create(B)</span> re-enters over REST → runs <strong>B's own loop</strong> → the reply flows back to A.</p>
  <p>No "group manager" is involved — it's an <strong>ordinary outbound API call</strong>, except the callee happens to be an agent too.</p>
  </div>
  <div class="col"><h4>😴 Path two · sleeptime edits memory in the background</h4>
  <p>The foreground agent finishes → the turn counter hits → a background sleeptime agent is <strong>non-blockingly</strong> woken → it rewrites the <strong>shared Block</strong> with memory tools.</p>
  <p>The foreground <strong>doesn't wait</strong> for it; on the next turn, rebuilding the system prompt, it naturally reads the tidied memory.</p>
  </div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">Footnote: the classic group managers (<span class="mono">round_robin / supervisor / dynamic</span>) stop at the <strong>schema level</strong> — enums, ORM, and class skeletons all exist, but they're <strong>not wired up</strong> and can't run over a live API. This lesson recognizes only those two live paths.</span></div>
<p>Before we dive in, let's calibrate expectations: if you came for "multi-agent scheduling like an orchestration framework," v0.16.8 may surprise you — it gives not an orchestration layer but <strong>two lower-level primitives</strong>. Understand these two, and you can build orchestration on top of them yourself.</p>
<h2>First, count them: how many multi-agent mechanisms are actually live in v0.16.8</h2>
<p>Many people start by hunting for a "group-chat scheduler" — assuming some object queues turns and lets A, B, and C speak in rotation. In v0.16.8 that object is <strong>mostly asleep</strong>.</p>
<p>The group manager's executor entry, <span class="mono">groups/helpers.py::load_multi_agent</span>, is <strong>never called</strong> anywhere on the live path; the <span class="mono">/v1/groups</span> routes are entirely <span class="mono">deprecated=True</span> with <strong>no send-message endpoint</strong>; even <span class="mono">SupervisorMultiAgent.step</span> is <strong>commented out entirely</strong>.</p>
<p>So let's lay out the six <span class="mono">ManagerType</span> enum values — their "intended behavior" beside their "real v0.16.8 status" — side by side. Only one row is green.</p>
<table class="t">
<tr><th>ManagerType enum</th><th>Intended routing behavior</th><th>Real status in v0.16.8</th></tr>
<tr><td class="mono">round_robin</td><td>Members speak in rotation</td><td>Dormant: enum/ORM exist, executor unwired</td></tr>
<tr><td class="mono">supervisor</td><td>A supervisor dispatches messages to subordinates</td><td>Skeleton: <span class="mono">SupervisorMultiAgent.step</span> commented out</td></tr>
<tr><td class="mono">dynamic</td><td>An LLM dynamically picks the next speaker</td><td>Dormant: unwired</td></tr>
<tr><td class="mono">sleeptime</td><td>Foreground finishes, a background agent edits memory</td><td><strong>ACTIVE ✅</strong>: this lesson's star</td></tr>
<tr><td class="mono">voice_sleeptime</td><td>A sleeptime variant for voice scenarios</td><td>Voice-only (a separate tool set)</td></tr>
<tr><td class="mono">swarm</td><td>OpenAI-swarm-style handoff</td><td>Not implemented</td></tr>
</table>
<p>Remember this table's through-line: <strong>the only group behavior that actually runs over a live API is the <span class="mono">sleeptime</span> row</strong>. The rest are historical leftovers or half-finished; don't let their mere presence fool you when reading the code.</p>
<p>Why keep these sleeping enums? Because they're <strong>fossils of design intent</strong>: round_robin/supervisor-style orchestration was once envisioned and the schema was even laid down, but the focus shifted to "single agent plus sleeptime memory," so the execution layer was never wired. Read them to see the direction, but don't treat them as usable features.</p>
<p>And "agent directly calls agent" (path one)? It's <strong>not in this table at all</strong> — it's not a group manager but a set of <strong>tools</strong>, covered in the next section.</p>
<p>So keep two layers in mind: <strong>group / ManagerType</strong> is "a config object for a flock of agents," of which only the sleeptime kind is truly in use; while the <strong>send_message tools</strong> are "a hammer in an agent's hand" — anyone can pick one up to knock on another agent, with no relation to group at all.</p>
<div class="card analogy"><div class="tag">📝 Real-world analogy</div>
<p>Picture the team as a <strong>small shop</strong>, with a <strong>shared message board</strong> (the shared <span class="mono">Block</span>) hanging behind the counter.</p>
<p>The day-shift clerk (the foreground agent) serves customers all day, jotting a few scrawled notes on the board as they go.</p>
<p>Before closing, the night-shift tidier (the sleeptime agent) is woken to <strong>tidy the day's notes into the same board</strong> — erasing duplicates, filling in the key points.</p>
<p>When the day shift returns the next morning, it sees the <strong>tidied version</strong> and has no idea anyone came by overnight.</p>
<p>Clerks can also <strong>pass notes directly</strong> (<span class="mono">send_message_to_agent</span>): write a question to the next counter and wait for them to write back — that's path one.</p>
</div>
<details class="accordion"><summary>Why are the classic group managers "sleeping scaffolding"?</summary><div class="acc-body">
<p>Three hard pieces of evidence. First: the executor <span class="mono">groups/helpers.py::load_multi_agent</span> is <strong>never called</strong> on the live path — it can build the matching multi-agent object by <span class="mono">manager_type</span>, but nobody news it up.</p>
<p>Second: the <span class="mono">/v1/groups</span> routes are all marked <span class="mono">deprecated=True</span>, and there's simply <strong>no "send a message to a group" endpoint</strong> — you can CRUD a group row but can't make it run.</p>
<p>Third: the body of <span class="mono">SupervisorMultiAgent.step</span> is <strong>commented out entirely</strong>; calling it does nothing.</p>
<p>Conclusion: in v0.16.8, <span class="mono">round_robin / supervisor / dynamic</span> are merely <strong>schema plus enum plus class skeleton</strong> — seats saved for the future, not features usable today.</p>
</div></details>
<h2>Live path one: send_message_to_agent_* (agent calls agent directly)</h2>
<p>Path one isn't "scheduling" but a <strong>tool call</strong>. These tools are registered in <span class="mono">functions/function_sets/multi_agent.py</span>, typed <span class="mono">ToolType.LETTA_MULTI_AGENT_CORE</span>, and <strong>execute in the sandbox</strong> like any other tool.</p>
<p>The core mechanism is one sentence: inside the tool body it <strong>builds a <span class="mono">letta_client.Letta</span> client</strong> and calls <span class="mono">client.agents.messages.create(agent_id=other_agent_id, ...)</span> — <strong>re-entering the server</strong> over REST to run callee agent B's own <strong>full loop</strong> (<span class="mono">AgentLoop.load(B).step</span>), <strong>never through a group manager</strong>.</p>
<p>Let's draw this call chain:</p>
<div class="flow">
  <div class="node hl"><div class="nt">Agent A</div><div class="nd">calls the wait_for_reply tool</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Tool sandbox</div><div class="nd">builds letta_client.Letta</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">REST re-entry</div><div class="nd">messages.create(B)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Agent B's loop</div><div class="nd">AgentLoop.load(B).step</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Reply flows back to A</div><div class="nd">takes B's assistant message</div></div>
</div>
<p>Note the sender's identity is <strong>auto-injected</strong>: the message B receives is prefixed with <span class="mono">[Incoming message from agent with ID '...']</span>, so B knows "this came from another agent."</p>
<p>Once B finishes, how does A "hear" the reply? The tool pulls B's assistant message out of <span class="mono">response.messages</span> and hands it back as this tool call's <strong>return value</strong> to A's loop — so from A's view, "asking another agent" is no different from "calling an ordinary tool and getting a string."</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/multi_agent.py</span><span class="ln">send_message_to_agent_and_wait_for_reply: re-enter over REST, run B's loop (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">send_message_to_agent_and_wait_for_reply</span>(message: str, other_agent_id: str) -&gt; str:
    <span class="cm"># tool runs in the sandbox: build a client pointed at this server</span>
    client = <span class="fn">_get_sandbox_client</span>()
    <span class="cm"># post the message to B over REST -- runs B's own full loop, no group manager</span>
    response = client.agents.messages.<span class="fn">create</span>(
        agent_id=other_agent_id,
        messages=[{<span class="st">&quot;role&quot;</span>: <span class="st">&quot;system&quot;</span>, <span class="st">&quot;content&quot;</span>: message}],  <span class="cm"># auto-prefixed [Incoming message from agent ...]</span>
    )
    <span class="cm"># synchronous, blocking: pull out B's assistant reply, hand it back to caller A</span>
    <span class="kw">return</span> <span class="fn">extract_assistant_reply</span>(response.messages)
</pre></div>
<p>Why loop through REST rather than call B in-process? Because the tool runs in the <strong>sandbox</strong> (callback to Lesson 20), where all it can get is an ordinary client handle; so A calling B goes through <strong>the same public API</strong> as an external script calling B — isolation and auth treated identically.</p>
<p>This also explains why B runs its "own <strong>full</strong> loop": when the server receives <span class="mono">messages.create(B)</span> it does the usual <span class="mono">AgentLoop.load(B).step</span> — B calls tools as needed, writes memory as needed — and A only gets its assistant reply back at the end.</p>
<details class="accordion"><summary>How do the three <span class="mono">send_message_to_agent_*</span> variants differ?</summary><div class="acc-body">
<p><strong>① <span class="mono">..._and_wait_for_reply(message, other_agent_id)</span></strong>: <strong>synchronous, blocking</strong>, two-way — send to one agent and <strong>wait</strong> for its reply before continuing. The most common.</p>
<p><strong>② <span class="mono">..._to_agents_matching_tags(message, match_all, match_some)</span></strong>: <strong>synchronous broadcast</strong> — filter a batch of agents by tags, then send to and wait for each <strong>one by one</strong>. One-to-many.</p>
<p><strong>③ <span class="mono">..._to_agent_async(message, other_agent_id)</span></strong>: <strong>asynchronous, one-way</strong> — fire and forget, no reply awaited; note it's <strong>disabled in production</strong>.</p>
<p>All three share one mechanism (build client → <span class="mono">messages.create</span> → run the other's loop); they differ only in <strong>whether they wait</strong> and <strong>one versus a batch</strong>.</p>
</div></details>
<p>The tag broadcast (<span class="mono">..._matching_tags</span>) deserves a note: it filters a batch of agents from the DB by <span class="mono">match_all / match_some</span>, then <strong>waits on each in turn</strong>. So it's essentially a "looped wait_for_reply," not true parallel fan-out — one-to-many, but still synchronous and serial.</p>
<p>An engineering caution: <span class="mono">..._and_wait_for_reply</span> truly <strong>blocks</strong> A's step until B's whole turn finishes. If B then calls C and C calls D, the blocking <strong>stacks layer by layer</strong> — when designing agent collaboration, don't let the synchronous wait chain grow too long.</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">Don't confuse this path with sleeptime: <span class="mono">..._and_wait_for_reply</span> is <strong>synchronous and blocking</strong> — A stalls waiting for B to finish. Sleeptime below is exactly the opposite: a <strong>non-blocking</strong> background task. The two "multi-agent" modes have completely opposite blocking semantics.</span></div>
<h2>Live path two: sleeptime (a background agent quietly edits memory)</h2>
<p>Sleeptime is the only <strong>truly live</strong> "group" behavior in v0.16.8. The wiring point is <span class="mono">agents/agent_loop.py::AgentLoop.load</span>: when an agent is <span class="mono">letta_v1_agent / sleeptime_agent</span>, has <span class="mono">enable_sleeptime</span> on, and is attached to a group, it's handed to <span class="mono">SleeptimeMultiAgentV4</span>.</p>
<p>The key point up front: <span class="mono">groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4</span> <strong>directly subclasses <span class="mono">LettaAgentV3</span></strong> — it's <strong>a subclass of that ordinary loop from Lessons 13 and 14</strong>, not some special subsystem.</p>
<p>Its <span class="mono">step</span> does two things: first <span class="mono">await super().step(...)</span> to run the <strong>foreground primary agent</strong> through a normal turn and save <span class="mono">response_messages</span>; then call <span class="mono">run_sleeptime_agents()</span> to decide whether to wake the background.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/groups/sleeptime_multi_agent_v4.py</span><span class="ln">SleeptimeMultiAgentV4: foreground runs first, then non-blockingly wakes the background (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">SleeptimeMultiAgentV4</span>(LettaAgentV3):       <span class="cm"># note: it's just a subclass of the ordinary loop</span>
    <span class="kw">async def</span> <span class="fn">step</span>(self, input_messages, ...):
        <span class="cm"># 1) foreground primary agent runs a normal turn; save the messages it produced</span>
        response_messages = <span class="kw">await</span> <span class="fn">super</span>().<span class="fn">step</span>(input_messages, ...)
        <span class="cm"># 2) decide whether to wake the background sleeptime agents</span>
        <span class="kw">await</span> self.<span class="fn">run_sleeptime_agents</span>(response_messages)
        <span class="kw">return</span> response_messages

    <span class="kw">async def</span> <span class="fn">run_sleeptime_agents</span>(self, response_messages):
        count = <span class="kw">await</span> group_manager.<span class="fn">bump_turns_counter_async</span>(self.group.id)  <span class="cm"># (c+1) % frequency</span>
        <span class="kw">if</span> count % self.group.sleeptime_agent_frequency != <span class="nb">0</span>:
            <span class="kw">return</span>                                   <span class="cm"># not yet, skip</span>
        <span class="kw">for</span> agent_id <span class="kw">in</span> self.group.agent_ids:     <span class="cm"># the background editors</span>
            <span class="kw">await</span> self.<span class="fn">_issue_background_task</span>(agent_id, response_messages)  <span class="cm"># non-blocking safe_create_task</span>
</pre></div>
<p>Line by line: <span class="mono">bump_turns_counter_async</span> advances the counter as <span class="mono">(c+1) % frequency</span>; only an exact division (<span class="mono">% frequency == 0</span>) is a hit.</p>
<p>On a hit, for <strong>each background sleeptime agent</strong> in <span class="mono">group.agent_ids</span> it runs <span class="mono">_issue_background_task</span>: create a <span class="mono">Run</span>, then <span class="mono">safe_create_task(_participant_agent_step)</span> — a <strong>non-blocking asyncio background task</strong>. The foreground <strong>doesn't wait</strong>.</p>
<p>What does that background task do? <span class="mono">_participant_agent_step</span> stitches <span class="mono">prior + response_messages</span> into a transcript, wraps it in a <span class="mono">&lt;system-reminder&gt;</span> — "you are a background sleeptime agent, your job is memory management, update the relevant blocks with the memory tools" — then runs <span class="mono">step</span> as a <strong>full <span class="mono">LettaAgentV3</span></strong>.</p>
<p>Note what it feeds the background is <span class="mono">prior + response_messages</span> — namely the foreground's just-happened turn. The background agent doesn't tidy out of thin air but decides what to write into long-term memory blocks based on "what was just said." It reads the conversation and edits the memory.</p>
<p>Don't miss this detail: <span class="mono">_issue_background_task</span> first creates a <span class="mono">Run</span> record, then <span class="mono">safe_create_task</span>. The <span class="mono">Run</span> makes this background tidying <strong>observable and traceable</strong> — not "fire a task and forget" but, like the foreground, leaving a queryable execution record.</p>
<p>That <span class="mono">&lt;system-reminder&gt;</span> matters too: it temporarily injects the sleeptime agent's <strong>identity and duty</strong> — "you are a background memory manager, update the relevant blocks with the memory tools." The same loop, via this prompt plus <span class="mono">sleeptime_memory_persona</span>, is "switched" into a memory tidier.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>User → foreground step</h4><p>A user message arrives; <span class="mono">SleeptimeMultiAgentV4.step</span> first does <span class="mono">await super().step()</span> to run the foreground primary agent.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>bump_turns_counter</h4><p>The counter advances by <span class="mono">(c+1) % frequency</span>; ask: is <span class="mono">% frequency == 0</span>?</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Hit → non-blocking wake</h4><p>On a hit, <span class="mono">safe_create_task(_participant_agent_step)</span> for each background agent; the foreground doesn't wait and returns right away.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>sleeptime step → memory_rethink</h4><p>The background agent runs <span class="mono">step</span> as a full <span class="mono">LettaAgentV3</span>, rewriting memory with <span class="mono">memory_rethink</span>.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Write shared Block (version++)</h4><p>The new content lands in that one <span class="mono">Block</span> row; the optimistic-lock <span class="mono">version</span> increments.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Foreground reads it next turn</h4><p>On its next turn, rebuilding the system prompt, the foreground naturally reads the tidied new value.</p></div></div>
</div>
<details class="accordion"><summary>How often does sleeptime trigger? And why "on the very first turn"?</summary><div class="acc-body">
<p>Frequency is set by <span class="mono">group.sleeptime_agent_frequency</span>, default <strong>5</strong> (see <span class="mono">server.py::create_sleeptime_agent_async</span>).</p>
<p>The hit condition is <span class="mono">% frequency == 0</span> after <span class="mono">bump_turns_counter</span> advances.</p>
<p>The trick is the initial value: <span class="mono">GroupManager.create_group_async</span> sets <span class="mono">turns_counter</span> to <strong><span class="mono">-1</span></strong> for sleeptime. On the first turn <span class="mono">(-1+1)=0</span>, and <span class="mono">0 % 5 == 0</span> → <strong>a hit on the very first turn</strong>.</p>
<p>So a newly created sleeptime agent needn't idle for 5 turns; the background starts tidying memory right after the first conversation turn.</p>
</div></details>
<p>The name "sleeptime" is deliberate: it echoes the brain's "memory consolidation" during sleep — tidying the day's short-term experiences into long-term memory. Letta turns this metaphor into engineering: foreground conversation is like "being awake," background tidying like "sleep," the two staggered so neither preempts the other.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Remember this causal chain: <strong>sleeptime = the same <span class="mono">LettaAgentV3</span> loop plus one shared memory row plus one turn counter</strong>. There's no "special memory-tidying subsystem" — just an ordinary agent dropped into a transcript, given memory tools, and told "your job is to tidy memory."</span></div>
<div class="card detail"><div class="tag">🔬 Down in the code</div>
<p><span class="mono">functions/function_sets/multi_agent.py</span> — the three <span class="mono">send_message_to_agent_*</span> tools, <span class="mono">LETTA_MULTI_AGENT_CORE</span>, sandbox-executed.</p>
<p><span class="mono">groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4</span> — subclasses <span class="mono">LettaAgentV3</span>; <span class="mono">step</span> does <span class="mono">super().step()</span> then <span class="mono">run_sleeptime_agents</span>.</p>
<p><span class="mono">orm/blocks_agents.py::BlocksAgents</span> — composite PK <span class="mono">(agent_id, block_id, block_label)</span>, attaching one <span class="mono">Block</span> row to many agents.</p>
<p><span class="mono">services/tool_executor/core_tool_executor.py::CoreToolExecutor.memory_rethink</span> — where sleeptime's memory edit lands.</p>
</div>
<h2>The only coordination primitive: one shared Block row</h2>
<p>How do two agents "confer"? The answer is surprisingly plain: they <strong>point at the same <span class="mono">Block</span> row</strong>. No message queue, no shared in-memory object — just the same record in the database.</p>
<p>What attaches one Block row to many agents is the association table <span class="mono">orm/blocks_agents.py::BlocksAgents</span>: composite PK <span class="mono">(agent_id, block_id, block_label)</span>. <span class="mono">Block.agents</span> ↔ <span class="mono">Agent.core_memory</span> are linked many-to-many via <span class="mono">secondary="blocks_agents"</span>.</p>
<p>The composite PK is the triple <span class="mono">(agent_id, block_id, block_label)</span>: the link is recorded by "which agent, which block row, attached as what label." So one Block row can stably appear under some label in many agents' core memory — sharing the value while each knows which prompt section to compile it into.</p>
<p>Who wires them together? When <span class="mono">server.py::SyncServer.create_sleeptime_agent_async</span> builds the sleeptime agent, it passes <span class="mono">block_ids=[b.id for b in main_agent.memory.blocks]</span> — <strong>the same Block rows</strong>, not copies.</p>
<div class="cellgroup"><div class="cg-cap"><b>One Block row on many agents: <span class="mono">blocks_agents.py::BlocksAgents</span> composite PK</b></div><div class="cells"><span class="cell hl">agent_id</span><span class="sep">·</span><span class="cell hl">block_id</span><span class="sep">·</span><span class="cell hl">block_label</span><span class="sep">→</span><span class="cell">Block.version (optimistic lock)</span></div></div>
<p>Let's draw "two agents sharing one row" — note the middle <span class="mono">Block</span> row has only one <span class="mono">block_id</span>:</p>
<div class="flow">
  <div class="node"><div class="nt">Foreground primary agent</div><div class="nd">core_memory</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">blocks_agents</div><div class="nd">(agent_id, block_id, label)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">The same Block row</div><div class="nd">unique block_id · version</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">blocks_agents</div><div class="nd">(agent_id, block_id, label)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Background sleeptime agent</div><div class="nd">core_memory</div></div>
</div>
<p>How to read it: the two ends are the two agents' core memory, each linked through <span class="mono">blocks_agents</span> to the same Block row in the middle. Sleeptime writes on the right, the foreground reads on the left — what's shared is that middle row.</p>
<p>The write detail: sleeptime's edit ultimately lands in <span class="mono">block_manager.update_block_async</span> (and <span class="mono">agent_manager.update_memory_if_changed_async</span>) — changing only that one Block row's value. The foreground agent's <span class="mono">core_memory</span> points, via <span class="mono">blocks_agents</span>, at this very row, so it sees the update "automatically," with no sync code at all.</p>
<p>Which tools does sleeptime use to edit this row? Standard sleeptime is equipped with <span class="mono">constants.py::BASE_SLEEPTIME_TOOLS</span> = <span class="mono">memory_replace / memory_insert / memory_rethink / memory_finish_edits</span>, all implemented in <span class="mono">CoreToolExecutor</span>. Look at <span class="mono">memory_rethink</span>:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">memory_rethink: rewrite that one shared Block row (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">memory_rethink</span>(self, agent_state, label: str, new_memory: str):
    block = agent_state.memory.<span class="fn">get_block</span>(label)
    <span class="kw">if</span> block.read_only:                       <span class="cm"># read-only block: refuse the edit</span>
        <span class="kw">raise</span> <span class="fn">ValueError</span>(<span class="st">&quot;cannot rethink a read-only block&quot;</span>)
    <span class="cm"># replace the whole content for this label</span>
    agent_state.memory.<span class="fn">update_block_value</span>(label=label, value=new_memory)
    <span class="cm"># write only when content changed: lands in that one shared Block (version++)</span>
    <span class="kw">await</span> agent_manager.<span class="fn">update_memory_if_changed_async</span>(agent_state)
    <span class="kw">return</span> new_memory                        <span class="cm"># returns the new content; memory_finish_edits is the one that returns None</span>
</pre></div>
<p>Three steps: refuse read-only blocks → <span class="mono">update_block_value(label, new_memory)</span> replaces the whole block → <span class="mono">update_memory_if_changed_async</span> writes the new value into that one shared Block. <span class="mono">memory_finish_edits</span> just does <span class="mono">return None</span> to wrap up.</p>
<p>While we're here, distinguish <span class="mono">voice_sleeptime</span>: it's a voice-scenario variant using a different tool set (including <span class="mono">finish_rethinking_memory</span>), not the same as standard sleeptime's <span class="mono">memory_finish_edits</span>. This lesson covers only standard sleeptime; when you hit the voice line, remember it has <strong>its own set</strong>.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">Common-mistake correction: standard sleeptime's "rethink memory" is <span class="mono">memory_rethink</span>, <strong>not</strong> <span class="mono">rethink_memory</span> (legacy) or <span class="mono">finish_rethinking_memory</span> (voice-only). When reading v0.16.8, lock onto those four in <span class="mono">BASE_SLEEPTIME_TOOLS</span>.</span></div>
<details class="accordion"><summary>Once sleeptime edits memory, <strong>when</strong> does the foreground see it?</summary><div class="acc-body">
<p>Not instantly. Sleeptime calls <span class="mono">memory_rethink</span> → <span class="mono">update_memory_if_changed_async</span> to write the new value into that one <span class="mono">Block</span> row, and that's all — it doesn't "notify" the foreground.</p>
<p>The foreground only reads the new value when, on its <strong>next turn rebuilding the system prompt</strong>, it recompiles this Block row into core memory (callback to Lessons 8 and 9: core memory is compiled fresh from blocks each turn).</p>
<p><span class="mono">Block</span> carries an optimistic-lock <span class="mono">version</span>: concurrent writes detect conflicts by version number, preventing the background and foreground from overwriting each other.</p>
<p>So what's "shared" is that row's current value, and the visibility boundary is "the next prompt rebuild," not "an immediate push."</p>
</div></details>
<p>This "share one row" coordination has the benefit of <strong>zero extra machinery</strong>: no message bus, no lock service — just reusing the Block plus optimistic lock you already learned. The cost is <strong>weak real-time</strong>: a peer's update takes effect only at "the next prompt rebuild," unfit for scenarios needing millisecond-level sync.</p>
<h2>A most counterintuitive wiring: who is the "manager"?</h2>
<p>Two fields in a sleeptime group are the easiest to read backwards. <span class="mono">manager_agent_id</span> sounds like "the coordinator" but is actually the <strong>foreground primary agent</strong>; <span class="mono">group.agent_ids</span> sounds like "ordinary members" but is actually the <strong>background editors</strong> (those sleeptime agents).</p>
<p>In other words: the "protagonist" running the user conversation is recorded as <span class="mono">manager</span>, while the background agents doing the dirty "tidy memory" work lie in <span class="mono">agent_ids</span>. The naming runs opposite to intuition; watch it closely when reading <span class="mono">orm/group.py::Group</span>.</p>
<p>The <span class="mono">Group</span> row also carries <span class="mono">manager_type / manager_agent_id / sleeptime_agent_frequency / turns_counter / agent_ids</span>, and links to <span class="mono">agents</span> via the M2M table <span class="mono">groups_agents</span> — one table recording "who's the protagonist, who's the night shift, and how often to wake them."</p>
<p>Why record it this way? Because sleeptime's "subject" is always the foreground conversation: it's the one that, on finishing, trips the counter, and whose <span class="mono">step</span> wakes the background in passing. The background editors are just its "errand-runners," so recording the foreground as <span class="mono">manager</span> and stuffing the background into <span class="mono">agent_ids</span> is, from the implementation's view, self-consistent.</p>
<div class="cute"><div class="row"><span class="emoji">😴</span><span class="lab">In the foreground's downtime</span><span class="arrow">→</span><span class="emoji">🧠</span><span class="lab">Memory block quietly rewritten</span><span class="arrow">→</span><span class="emoji">✨</span><span class="bubble">Better memory on waking</span></div><div class="cap">😴 In the gap between the foreground agent's turns, the sleeptime agent erases the 🧠 shared memory block and rewrites it into a tidier version; ✨ the primary agent wakes next turn to find the memory already tidied — never knowing anyone came by</div></div>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>Sleeptime = implementing "memory tidying" as a <strong>recursive reuse of the agent abstraction</strong>. That background "memory tidier" isn't a special subsystem — it's <strong>just another <span class="mono">LettaAgentV3</span></strong> (<span class="mono">SleeptimeMultiAgentV4</span> simply subclasses the ordinary loop). The same "read context -> call tools -> change state" machine, given a different persona inside and a different trigger outside, becomes memory's "night-shift tidier."</p>
<p>This recursion throws in a bonus: since the tidier is just an ordinary agent, each step it runs also writes a <span class="mono">Step</span> row and is equally observable and billable (lesson 30) — "background memory tidying" is not a black box but one more traceable agent execution.</p>
<p>The most counterintuitive corollary: v0.16.8 has <strong>no dedicated "multi-agent runtime" at all</strong> — the <span class="mono">round_robin / supervisor</span> set is sleeping scaffolding, and real multi-agent behavior all <strong>emerges</strong> from "one agent calling another's API" and "two agents pointing at the same block."</p>
</div>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<p>Standard sleeptime's memory tool is <span class="mono">memory_rethink</span>, <strong>not</strong> <span class="mono">rethink_memory</span> (legacy) or <span class="mono">finish_rethinking_memory</span> (voice-only).</p>
<p>Opposite blocking semantics: <span class="mono">..._and_wait_for_reply</span> is <strong>synchronous and blocking</strong>; the sleeptime background task is <strong>non-blocking</strong>. Don't apply one's intuition to the other.</p>
<p>Fields read backwards easily: sleeptime's <span class="mono">manager_agent_id</span> = the <strong>foreground primary agent</strong>, and <span class="mono">group.agent_ids</span> = the <strong>background editors</strong>.</p>
<p>A "shared block" shares the <strong>same Block row</strong>, not a copy each — edit one place and the other agent sees it on its next prompt rebuild.</p>
<p><span class="mono">round_robin / supervisor / dynamic</span> cannot run over a live API in v0.16.8; don't read the schema and assume they're usable.</p>
</div>
<h2>Callbacks and recap: multi-agent is something that "emerges"</h2>
<p>Let's wrap up this lesson. v0.16.8's multi-agent has no grand "scheduling hub"; it's assembled from a few parts you <strong>already learned</strong> long ago.</p>
<p>Callback to Lessons 13 and 14: the sleeptime agent runs that very <span class="mono">LettaAgentV3</span> step loop — <span class="mono">SleeptimeMultiAgentV4</span> subclasses it directly. The callee agent B is the same, running B's own full loop. Every "member" is just an ordinary agent.</p>
<p>Callback to Lessons 8 and 9: what sleeptime edits is the block plus self-editing memory set — <span class="mono">memory_rethink</span> reuses exactly the core-memory tools you learned, only this time writing the shared row.</p>
<p>Callback to Lesson 25: the trigger cadence relies on <span class="mono">group_manager</span>'s <span class="mono">bump_turns_counter_async</span> maintaining <span class="mono">turns_counter</span> — another appearance of that service-manager set from Part 7.</p>
<p>So "multi-agent" in Letta is not a new runtime but a <strong>new combination of old parts</strong>: the same loop, the same memory tools, the same service manager, plus one shared Block row and a counter.</p>
<p>This is Letta's consistent "less is more": rather than building a giant multi-agent engine, it reuses the already-polished abstractions of agent, block, and manager to the hilt. New behavior emerges from combining old abstractions, and the maintenance surface stays minimal.</p>
<p>Another callback to Lesson 24's "three floors": the A-calls-B hop walks that REST → SyncServer → loop staircase back down, this time from the tool sandbox. Multi-agent doesn't bypass the architecture but <strong>runs the same request path again</strong>, only with another agent as the initiator.</p>
<p>To string it together: path one lets agents <strong>talk</strong> (a synchronous API call), sleeptime lets agents <strong>hand off memory</strong> (an asynchronous edit of the shared block), and what truly glues them is always that one <span class="mono">Block</span> row.</p>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li>Only <strong>two</strong> multi-agent mechanisms are truly live in v0.16.8: the <span class="mono">send_message_to_agent_*</span> tools (A re-enters over REST to run B's own loop) and <strong>sleeptime</strong> (a background agent edits memory every N turns).</li>
<li>The classic group managers <span class="mono">round_robin / supervisor / dynamic</span> are only schema/enum/class skeleton: <span class="mono">load_multi_agent</span> is never called, <span class="mono">/v1/groups</span> is deprecated with no send endpoint, and <span class="mono">SupervisorMultiAgent.step</span> is commented out.</li>
<li>Sleeptime = <span class="mono">SleeptimeMultiAgentV4(LettaAgentV3)</span>: <span class="mono">step</span> first does <span class="mono">super().step()</span> for the foreground, then <span class="mono">run_sleeptime_agents</span> — on a <span class="mono">% frequency == 0</span> hit, <span class="mono">safe_create_task</span> non-blockingly wakes the background.</li>
<li>The coordination primitive is <strong>one shared <span class="mono">Block</span></strong> (<span class="mono">blocks_agents.py::BlocksAgents</span> composite PK): sleeptime writes with <span class="mono">memory_rethink</span>, the foreground reads only on its next prompt rebuild; <span class="mono">Block.version</span> is an optimistic lock.</li>
<li>Read-backwards alert: sleeptime's <span class="mono">manager_agent_id</span> = the foreground primary agent, <span class="mono">group.agent_ids</span> = the background editors; <span class="mono">turns_counter=-1</span> plus default frequency 5 → it fires on the very first turn.</li>
</ul>
</div>
<p>Take this muscle memory with you: when you see "multi-agent" in Letta, don't hunt for a scheduler first — ask "whose API are they calling" and "do they point at the same Block row." Answer those two and multi-agent behavior is no longer mysterious.</p>
<p>Part 8 is now open. In the next lesson we continue into the "advanced topics," applying this "old parts, new combinations" mindset to more places.</p>
""",
}

LESSON_29 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第 27 课我们拆开了向量存储那根 <span class="mono">Vector(4096)</span> 列——agent 自己写的记忆怎么落库、又怎么按 <span class="mono">cosine_distance</span> 召回。这一课接着问一个很自然的问题：你<strong>从外部上传的文档</strong>，是怎么钻进同一套向量机器里、变得可被语义搜索的？答案两个字：RAG。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">先把一个反直觉的事实摆上台面：Letta <strong>没有另造一台"RAG 引擎"</strong>。它把第 27 课那套归档记忆的向量机器<strong>原样复用</strong>了一遍，只换了张表、换个外键、换个工具名。"RAG"和"长期记忆"，在物理层根本是同一回事。</p>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>RAG 与归档记忆"同底座、不同来源"</strong>——同一根向量列、同一套召回，唯一的真差别是"谁写进去的"。</p>
<p>底座：<span class="mono">SourcePassage</span>（你上传的文档）和 <span class="mono">ArchivalPassage</span>（agent 自己写的记忆）是<strong>同一个 <span class="mono">BasePassage</span></strong> 的两个兄弟子类，骑同一根 <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> 列。</p>
<p>摄取：一份文件经<strong>解析 → 切块 → 嵌入</strong>的管线，被打散成一排 <span class="mono">SourcePassage</span> 行，从此可被语义搜索。</p>
<p>检索：源用 <span class="mono">semantic_search_files</span>、归档用 <span class="mono">archival_memory_search</span>——<strong>两个不同工具，同一套 pgvector cosine</strong>。</p>
</div>
<p>为什么值得专门讲这件事？因为很多人以为 RAG 是"另一个系统"，于是去找配置、找引擎、找索引服务。看懂"它就是归档记忆换了来源"，你会省下大量找错地方的时间。</p>
<p>还有个实际好处：理解了同底座，你就知道<strong>调优 RAG 和调优记忆是同一件事</strong>——换嵌入模型、调 chunk 尺寸、改距离度量，对源和归档<strong>同时生效</strong>，因为它们共用那根列。</p>
<p>把这条主线记牢：本课从头到尾都在反复印证"<strong>底座一样，来源不同</strong>"这八个字。下面先认底座，再走摄取，最后看检索。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">底注：两类 passage <strong>共用</strong>第 27 课那根 <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> 列、同一套 4096 padding、同一个 <span class="mono">cosine_distance</span> 排序。差别<strong>不在</strong>向量机器，只在<strong>来源</strong>与<strong>外键</strong>。</span></div>
<h2>同一个 BasePassage，两个兄弟子类</h2>
<p>先认底座。<span class="mono">orm/passage.py::BasePassage</span> 是个 <span class="mono">__abstract__</span> 抽象基类——它<strong>自己不建表</strong>，只规定"一条 passage 长什么样"：主键、文本、元数据，以及最关键的那根<strong>嵌入向量列</strong>。</p>
<p>那根列正是第 27 课的主角：Postgres 上是 <span class="mono">embedding = Vector(MAX_EMBEDDING_DIM)</span>（pgvector），SQLite 上是 <span class="mono">CommonVector</span>。<strong>同列、同 4096 填充、同 <span class="mono">cosine_distance</span></strong>——两个子类<strong>原样继承</strong>，一行没改。</p>
<p>两个子类只在<strong>"挂到谁身上"</strong>这件事上分道扬镳：</p>
<p><strong>① <span class="mono">SourcePassage(BasePassage, FileMixin, SourceMixin)</span></strong>：表 <span class="mono">source_passages</span>，带 <span class="mono">source_id</span>(必填) ＋ <span class="mono">file_id</span>(可选) ＋ <span class="mono">file_name</span>。它属于"某个源里的某个文件"。</p>
<p><strong>② <span class="mono">ArchivalPassage(BasePassage, ArchiveMixin)</span></strong>：表 <span class="mono">archival_passages</span>，带 <span class="mono">archive_id</span>，还多挂一张 <span class="mono">passage_tags</span> 标签 junction。它属于"某个 archive"。</p>
<p>那些外键从哪来？全在 <span class="mono">orm/mixins.py</span> 的三个 mixin 里：<span class="mono">FileMixin</span>(给 file_id/file_name)、<span class="mono">SourceMixin</span>(给 source_id)、<span class="mono">ArchiveMixin</span>(给 archive_id)。子类只是<strong>拼装 mixin</strong>，就拿到各自的归属外键。</p>
<p>为什么底座要做成 <span class="mono">__abstract__</span>？因为那根 4096 维向量列、<span class="mono">cosine_distance</span> 算法、padding 约定<strong>只想写一遍</strong>。两个子类继承同一份定义，就<strong>天然不可能</strong>出现"源和归档用了不同向量空间"这种灾难。</p>
<p>为什么 <span class="mono">SourcePassage</span> 要 <span class="mono">source_id</span> ＋ <span class="mono">file_id</span> 两个外键？因为一个源能装<strong>多个文件</strong>：<span class="mono">source_id</span> 标"属于哪个源"，<span class="mono">file_id</span> 标"来自源里哪个文件"，<span class="mono">file_name</span> 方便回显出处。</p>
<p>而 <span class="mono">ArchivalPassage</span> 多挂的那张 <span class="mono">passage_tags</span> junction，是归档<strong>独有</strong>的：它让 agent 给记忆片段打标签，检索时按标签过滤（回扣第 11 课）。源 passage <strong>没有</strong>这层标签。</p>
<p>记住这个分层：<strong>mixin 决定"归属"，base 决定"能力"</strong>。能力（向量、检索）共享，归属（源 / archive、文件）分家——这正是"同底座、不同来源"在 ORM 层的精确投影。</p>
<p>反过来想更清楚：要新增第三类 passage（比如某种"工具产出的缓存"），你只需写个新 mixin ＋ 新表，继承 <span class="mono">BasePassage</span> 就<strong>白拿</strong>整套向量检索。底座的复用性，就体现在这种"加一类几乎零成本"上。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/passage.py</span><span class="ln">一个抽象基类，两个兄弟子类（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">BasePassage</span>(Base):
    __abstract__ = <span class="kw">True</span>                       <span class="cm"># 不建表，只定义"一条 passage 长什么样"</span>
    text: Mapped[str]
    <span class="cm"># 第 27 课那根列：Postgres 用 pgvector，SQLite 用 CommonVector</span>
    <span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
        embedding = <span class="fn">mapped_column</span>(<span class="fn">Vector</span>(MAX_EMBEDDING_DIM))   <span class="cm"># 固定 4096 维</span>
    <span class="kw">else</span>:
        embedding = <span class="fn">mapped_column</span>(CommonVector)

<span class="kw">class</span> <span class="fn">SourcePassage</span>(BasePassage, FileMixin, SourceMixin):   <span class="cm"># 你上传的文档</span>
    __tablename__ = <span class="st">&quot;source_passages&quot;</span>      <span class="cm"># source_id(必) + file_id(选) + file_name</span>

<span class="kw">class</span> <span class="fn">ArchivalPassage</span>(BasePassage, ArchiveMixin):            <span class="cm"># agent 自己写的记忆</span>
    __tablename__ = <span class="st">&quot;archival_passages&quot;</span>    <span class="cm"># archive_id；另挂 passage_tags 标签</span>
</pre></div>
<p>把"两个子类、同一底座"摆成左右两栏看，差别一目了然——除了来源与外键，其余全共用：</p>
<div class="cols">
  <div class="col"><h4>🧠 ArchivalPassage · agent 写的</h4>
  <p>表 <span class="mono">archival_passages</span> · 外键 <span class="mono">archive_id</span> · 工具 <span class="mono">archival_memory_search</span> · join <span class="mono">ArchivesAgents</span> · 带 <span class="mono">passage_tags</span>。</p>
  <p>来源：agent 调 <span class="mono">archival_memory_insert</span> 自己写下（第 10、11 课）。</p>
  </div>
  <div class="col"><h4>📄 SourcePassage · 你上传的</h4>
  <p>表 <span class="mono">source_passages</span> · 外键 <span class="mono">source_id</span>＋<span class="mono">file_id</span> · 工具 <span class="mono">semantic_search_files</span> · join <span class="mono">SourcesAgents</span>。</p>
  <p>来源：上传文件，经摄取管线解析+嵌入而成（下一节）。</p>
  </div>
</div>
<div class="cellgroup"><div class="cg-cap"><b>两子类共用：<span class="mono">BasePassage</span> 的同一根向量列（第 27 课）</b></div><div class="cells"><span class="cell">archival_passages</span><span class="sep">·</span><span class="cell">source_passages</span><span class="sep">→</span><span class="cell hl">BasePassage.embedding = Vector(MAX_EMBEDDING_DIM)</span><span class="sep">·</span><span class="cell hl">cosine_distance</span></div></div>
<details class="accordion"><summary>source 与 archival 真就"井水不犯河水"？</summary><div class="acc-body">
<p><strong>写入互斥（库层守卫）</strong>：<span class="mono">PassageManager.create_source_passage_async</span> 要求<strong>必须有</strong> <span class="mono">source_id</span>、<strong>不能有</strong> <span class="mono">archive_id</span>；<span class="mono">create_agent_passage_async</span> 反之。给错一个就直接报错。</p>
<p><strong>检索互不返回</strong>：源走 <span class="mono">build_source_passage_query</span>（扫 <span class="mono">source_passages</span>），归档走 <span class="mono">build_agent_passage_query</span>（扫 <span class="mono">archival_passages</span>）。两条查询<strong>各扫各的表</strong>，永不把对方的行混进结果。</p>
<p>所以"同底座"指的是<strong>物理列与算法</strong>一样，不是"数据混在一起"。两类 passage 在表、外键、工具、查询四个层面都<strong>分开</strong>。</p>
</div></details>
<div class="card analogy"><div class="tag">📝 生活类比</div>
<p>把向量库想成一座<strong>图书馆</strong>，馆里有<strong>两种藏书</strong>。</p>
<p>一种是<strong>你捐进来的书</strong>（<span class="mono">SourcePassage</span> ／ RAG）：从外面带进来的文档，馆员拆页、编号、上架。</p>
<p>另一种是<strong>馆员自己手写的读书笔记</strong>（<span class="mono">ArchivalPassage</span> ／ 归档）：agent 工作中随手记下的心得。</p>
<p>两种书都进<strong>同一套"按语义检索"的索引</strong>（那根向量列）——查的时候都按"意思相近"排序。</p>
<p>只是它们分放<strong>两个书架</strong>（两张表），借阅要填<strong>不同的检索单</strong>（两个工具）：找捐书用 <span class="mono">semantic_search_files</span>，翻笔记用 <span class="mono">archival_memory_search</span>。</p>
</div>
<h2>摄取管线：一份文件怎么变成一排可搜索的 passage</h2>
<p>认完底座，看"文件怎么进来"。现代摄取的主入口是 <span class="mono">services/file_processor/file_processor.py::FileProcessor.process</span>，它把一份原始文件一步步加工成一排 <span class="mono">SourcePassage</span>。</p>
<p>整条管线可拆成八步，从上传一路走到落库。先看全景，再逐段解释：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Upload → 进入某个 source</h4><p>文件被上传，归到一个已建好的 <span class="mono">Source</span>（org 级，下一节细说）。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>create_file（PARSING）</h4><p><span class="mono">FileManager.create_file</span> 登记一行 <span class="mono">FileMetadata</span>，状态置 <span class="mono">PARSING</span>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>extract_text（OCR）</h4><p><span class="mono">FileParser.extract_text</span> 抽全文：PDF/图片走 OCR，文档转 markdown。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>upsert_file_content（全文）</h4><p>全文落进 <span class="mono">file_contents</span> 表——原文留底，独立于切块。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>insert_file_into_context_windows</h4><p>把文件"打开"成 <span class="mono">FileAgent</span>（上下文里的只读原文，末节专讲）。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>chunk_text（按 EmbeddingConfig）</h4><p><span class="mono">LlamaIndexChunker.chunk_text</span> 切块，<span class="mono">chunk_size</span> 来自 <span class="mono">EmbeddingConfig</span>（第 21 课）。</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>generate_embedded_passages（batch 200）</h4><p><span class="mono">Embedder</span> 每 200 条一批算嵌入向量。</p></div></div>
  <div class="step"><div class="num">8</div><div class="sc"><h4>create_many_source_passages_async</h4><p>批量写进 <span class="mono">source_passages</span>，每条 pad 到 4096 → 一排 <span class="mono">SourcePassage</span> 行。</p></div></div>
</div>
<p>把这八步落成代码，省去错误处理与状态机，骨架就这么直：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/file_processor/file_processor.py</span><span class="ln">FileProcessor.process：存原文 → 切块 → 嵌入 → 落库（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">process</span>(self, source_id, content, ...):
    <span class="cm"># 1) 登记文件行，状态置 PARSING</span>
    file = <span class="kw">await</span> self.file_manager.<span class="fn">create_file</span>(..., status=FileProcessingStatus.PARSING)
    <span class="cm"># 2) 抽全文（OCR / markdown），存进 file_contents 表</span>
    text = <span class="kw">await</span> self.file_parser.<span class="fn">extract_text</span>(content)
    <span class="kw">await</span> self.file_manager.<span class="fn">upsert_file_content</span>(file.id, text)
    <span class="cm"># 3) 把文件"打开"进上下文（FileAgent，见末节）</span>
    <span class="kw">await</span> self.agent_manager.<span class="fn">insert_file_into_context_windows</span>(source_id, file, ...)
    <span class="cm"># 4) 切块 → 嵌入（chunk_size 来自 EmbeddingConfig）</span>
    chunks = self.chunker.<span class="fn">chunk_text</span>(text)
    passages = <span class="kw">await</span> self.embedder.<span class="fn">generate_embedded_passages</span>(chunks, batch_size=<span class="nb">200</span>)
    <span class="cm"># 5) 批量写入 source_passages（每条 pad 到 4096）</span>
    <span class="kw">await</span> self.passage_manager.<span class="fn">create_many_source_passages_async</span>(passages, source_id=source_id)
</pre></div>
<p>逐段读这条管线。<strong>前三步是"存原文"</strong>：<span class="mono">create_file</span> 把文件登记成一行 <span class="mono">FileMetadata</span>（状态 <span class="mono">PARSING</span>）；<span class="mono">extract_text</span> 经 OCR/markdown 抽出纯文本；<span class="mono">upsert_file_content</span> 把全文存进 <span class="mono">file_contents</span> 表。</p>
<p><strong>第四步是岔路</strong>：<span class="mono">insert_file_into_context_windows</span> 把文件"打开"进 agent 上下文（建 <span class="mono">FileAgent</span>）——这条支线留到最后一节专讲。</p>
<p>这条岔路本身就很妙：<strong>摄取一次，双重产出</strong>——同一趟管线既把文件切块嵌入（建 RAG），又顺手把它"打开"进上下文（建 FileAgent）。上传一个文件，两种形态<strong>一并就位</strong>。</p>
<p><strong>后三步才是"建 RAG"</strong>：<span class="mono">chunk_text</span> 按 <span class="mono">EmbeddingConfig</span> 切块，<span class="mono">generate_embedded_passages</span> 每 200 条一批算嵌入，<span class="mono">create_many_source_passages_async</span> 落进 <span class="mono">source_passages</span>。</p>
<p>那行 <span class="mono">status=PARSING</span> 不是摆设。<span class="mono">FileMetadata</span> 带 <span class="mono">processing_status</span> 状态字段，配 <span class="mono">total_chunks</span> / <span class="mono">chunks_embedded</span> 两个计数——状态从 <span class="mono">PARSING</span> 起步，两个计数记录嵌入进度，全嵌完才算就绪。前端"处理中…"进度条就读它。</p>
<p>为什么把全文单独存进 <span class="mono">file_contents</span>，而不只留 chunk？因为两种形态各有所需：<strong>chunk 供语义召回</strong>（模糊找相关段），<strong>全文供逐字打开</strong>（<span class="mono">open_files</span> 要原原本本的文本）。拆开存，两条路互不干扰。</p>
<p>嵌入为什么按 <strong>200 条一批</strong>？因为嵌入要调外部模型 API，逐条发太慢太贵；攒成批一次发，吞吐高、往返少。这是工程上常见的"批处理摊薄开销"。</p>
<p>顺带说一句容错：全文存在 <span class="mono">file_contents</span> 是<strong>独立于</strong> chunk 的一份底稿。将来想换嵌入模型、重切重嵌，原文还在，不必让用户重传——<span class="mono">total_chunks</span> 归零、重跑后半段即可。</p>
<details class="accordion"><summary>摄取有两条路：现代 file_processor 与 legacy connectors</summary><div class="acc-body">
<p><strong>现代（主线）</strong>：<span class="mono">services/file_processor/file_processor.py::FileProcessor.process</span>——带 OCR/markdown 解析、<span class="mono">LlamaIndexChunker</span> 切块、<span class="mono">generate_embedded_passages</span> 批量嵌入，末了 <span class="mono">create_many_source_passages_async</span>。本课讲的就是它。</p>
<p><strong>legacy（旧路）</strong>：<span class="mono">data_sources/connectors.py::load_data</span>——用 <span class="mono">DirectoryConnector</span> ＋ llama_index 的 <span class="mono">TokenTextSplitter</span>，调的是<strong>已弃用</strong>的 <span class="mono">create_many_passages_async</span>。</p>
<p>看 v0.16.8 认准 <span class="mono">file_processor</span> 这条；遇到 <span class="mono">connectors.load_data</span> 知道它是旧路即可，别照它写新代码。</p>
</div></details>
<div class="note tip"><span class="ni">🧩</span><span class="nx">切块的 <span class="mono">chunk_size</span> 不是拍脑袋定的，它来自 agent 的 <span class="mono">EmbeddingConfig</span>（第 21 课）——<strong>嵌入模型窗口多大，块就切多大</strong>。摄取与召回必须用<strong>同一套嵌入配置</strong>，否则两边向量根本不在一个空间里。</span></div>
<div class="cute"><div class="row"><span class="emoji">📄</span><span class="lab">一份文档</span><span class="arrow">→</span><span class="emoji">📚</span><span class="lab">切成小卡片</span><span class="arrow">→</span><span class="emoji">🔢</span><span class="bubble">每张盖个向量戳</span></div><div class="cap">📄 一份上传的文档被拆成 📚 一摞小卡片（chunk），每张盖上一枚 🔢 向量戳（embedding），再统一排进那座 4096 维货架——从此"按意思"就能一把抓出最相近的几张</div></div>
<h2>检索：同一套向量搜索，换个工具与表</h2>
<p>passage 建好了，怎么查？关键还是那句"同底座、不同来源"——<strong>检索用的也是同一套向量搜索</strong>，只是查询 builder 与工具名各换一个。</p>
<p>源的检索 builder 是 <span class="mono">services/helpers/agent_manager_helper.py::build_source_passage_query</span>，它和归档那条 <span class="mono">build_agent_passage_query</span> <strong>形状几乎一样</strong>，差别只在 join 哪张 junction、扫哪张表。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/helpers/agent_manager_helper.py</span><span class="ln">build_source_passage_query：嵌入查询 → join → cosine 排序（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">build_source_passage_query</span>(agent_id, query_text, embed_config, ...):
    <span class="cm"># 1) 查询文本嵌成向量，pad 到 4096（与落库同一套配置）</span>
    q = <span class="fn">embed_query</span>(query_text, embed_config)
    q = np.<span class="fn">pad</span>(q, (<span class="nb">0</span>, MAX_EMBEDDING_DIM - <span class="fn">len</span>(q)))
    <span class="cm"># 2) 只取"这个 agent 挂载的源"里的 passage：join SourcesAgents</span>
    query = (
        <span class="fn">select</span>(SourcePassage)
        .<span class="fn">join</span>(SourcesAgents, SourcesAgents.source_id == SourcePassage.source_id)
        .<span class="fn">where</span>(SourcesAgents.agent_id == agent_id)
    )
    <span class="cm"># 3) 按 cosine 距离升序（Postgres pgvector；SQLite 走 numpy）</span>
    <span class="kw">return</span> query.<span class="fn">order_by</span>(SourcePassage.embedding.<span class="fn">cosine_distance</span>(q).<span class="fn">asc</span>())
</pre></div>
<p>三步看懂这条查询。<strong>① 嵌入 + pad</strong>：把查询文本用<strong>同一套 <span class="mono">EmbeddingConfig</span></strong> 嵌成向量，再 <span class="mono">np.pad</span> 到 4096，好和库里 padding 过的向量对齐。</p>
<p><strong>② join 限定范围</strong>：<span class="mono">select(SourcePassage)</span> join <span class="mono">SourcesAgents</span> on <span class="mono">source_id</span>、where <span class="mono">agent_id</span>——只搜"<strong>这个 agent 挂载的源</strong>"里的 passage，不越界。</p>
<p><strong>③ 排序</strong>：Postgres 用 <span class="mono">embedding.cosine_distance(q).asc()</span>（pgvector），SQLite 落回 numpy 算距离；文本兜底则用 <span class="mono">func.lower(text).contains</span>。</p>
<p>这里方向别记反：<span class="mono">cosine_distance</span> 是<strong>距离</strong>，<strong>越小越近</strong>，所以用 <span class="mono">.asc()</span> 升序取前几条——和"相似度越大越好"正好反着来（回扣第 27 课）。</p>
<p>对照归档那条 <span class="mono">build_agent_passage_query</span>：同样的嵌入 + pad + cosine，只是 join 的是 <span class="mono">ArchivesAgents</span>(on <span class="mono">archive_id</span>)，还能按标签过滤。<strong>同一套机器，换个接头。</strong></p>
<p>那条 <span class="mono">func.lower(text).contains</span> 文本兜底，是给"没嵌入 / 纯关键词"场景留的后路：拿不到向量时，至少能按子串、大小写不敏感地命中，不至于两手空空。</p>
<p>还有一处分支：<span class="mono">np.pad</span> 到 4096 <strong>只在 pgvector 路径</strong>做；若走外部向量库 Turbopuffer（TPUF），padding 被<strong>跳过</strong>——维度交给它自己管。pad 是 pgvector"定长列"的迁就，不是通用步骤。</p>
<p>别小看那个 <span class="mono">join SourcesAgents</span>：它就是<strong>多租户的护栏</strong>（回扣第 26 课）。没有它，向量搜索会扫到别的 agent、别的组织的源；有了它，每个 agent 只能搜<strong>自己挂载</strong>的那几个源。</p>
<div class="note info"><span class="ni">🔧</span><span class="nx">小心"函数声明"与"真实现"分家：<span class="mono">function_sets/files.py</span>、<span class="mono">function_sets/base.py</span> 里的 <span class="mono">semantic_search_files</span> / <span class="mono">archival_memory_search</span> 只是 <span class="mono">raise NotImplementedError</span> 的 <strong>schema 占位</strong>；真正干活的在 <span class="mono">tool_executor/files_tool_executor.py</span> 与 <span class="mono">core_tool_executor.py</span>。</span></div>
<p>把源检索这条链画直，五个节点一目了然：</p>
<div class="flow">
  <div class="node hl"><div class="nt">查询文本</div><div class="nd">找关于 X 的段落</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">嵌入 + pad</div><div class="nd">embed(q) → np.pad 4096</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">select(SourcePassage)</div><div class="nd">join SourcesAgents · source_id</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">cosine_distance.asc()</div><div class="nd">按相近度排序</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">top-k 段落</div><div class="nd">回灌给工具调用方</div></div>
</div>
<p>最后用一张表把"源 vs 归档"在六个维度上并排清楚，便于随时回查：</p>
<table class="t">
<tr><th>维度</th><th>SourcePassage（源 / RAG）</th><th>ArchivalPassage（归档）</th></tr>
<tr><td>表</td><td class="mono">source_passages</td><td class="mono">archival_passages</td></tr>
<tr><td>来源外键</td><td class="mono">source_id（必）+ file_id（选）</td><td class="mono">archive_id</td></tr>
<tr><td>谁写进去</td><td>你上传文档，摄取管线建</td><td>agent 调 archival_memory_insert</td></tr>
<tr><td>查询 builder</td><td class="mono">build_source_passage_query</td><td class="mono">build_agent_passage_query</td></tr>
<tr><td>检索工具</td><td class="mono">semantic_search_files</td><td class="mono">archival_memory_search</td></tr>
<tr><td>标签</td><td>无</td><td class="mono">passage_tags junction</td></tr>
</table>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">orm/passage.py::SourcePassage / ArchivalPassage</span>——同一个 <span class="mono">BasePassage</span> 的两个子类，分表 <span class="mono">source_passages / archival_passages</span>。</p>
<p><span class="mono">services/file_processor/file_processor.py::FileProcessor.process</span>——现代摄取管线：解析 → 切块 → 嵌入 → <span class="mono">create_many_source_passages_async</span>。</p>
<p><span class="mono">services/helpers/agent_manager_helper.py::build_source_passage_query</span>——源向量搜索：嵌入查询 ＋ pad ＋ join <span class="mono">SourcesAgents</span> ＋ <span class="mono">cosine_distance</span>。</p>
<p><span class="mono">orm/files_agents.py::FileAgent</span>——文件的另一形态：上下文里的只读 <span class="mono">FileBlock</span>（下一节）。</p>
</div>
<h2>文件的两种形态：可搜索的 passage vs 上下文里"打开的文件"</h2>
<p>回到摄取管线第五步那条岔路。一份挂载的文件，在 Letta 里会<strong>同时活成两种形态</strong>——这是本课第二个值得记住的点。</p>
<p><strong>形态 A：可搜索的 RAG chunk</strong>，就是前面讲的 <span class="mono">SourcePassage</span>——切块、嵌入、按 cosine 召回。</p>
<p><strong>形态 B：上下文里"打开的文件"</strong>，是另一套机制：<span class="mono">orm/files_agents.py::FileAgent</span>。它是 <span class="mono">files_agents</span> junction 上的一行，带 <span class="mono">is_open</span> / <span class="mono">visible_content</span>。</p>
<div class="cellgroup"><div class="cg-cap"><b>一个文件，两种形态：元数据 <span class="mono">FileMetadata</span>(表 files) ＋ 全文 <span class="mono">FileContent</span>(表 file_contents)</b></div><div class="cells"><span class="cell hl">SourcePassage</span><span class="lab">embedded · 语义搜</span><span class="sep">‖</span><span class="cell q">FileAgent / FileBlock</span><span class="lab">visible_content · 上下文只读原文</span></div></div>
<p>关键一句：<span class="mono">FileAgent.to_pydantic_block(...)</span> 会把它<strong>渲染成一个 <span class="mono">FileBlock(read_only=True)</span></strong>——"打开一个文件" ＝ 在上下文里塞进一块<strong>只读的记忆 block</strong>，内容是原文（或片段）。</p>
<p>操作这层的是 <span class="mono">open_files</span> / <span class="mono">grep_files</span> 工具：把文件开进上下文、在已开文件里按行抓取。注意有个上限——<strong>默认最多 5 个</strong>同时打开的文件。</p>
<p><span class="mono">grep_files</span> 和 <span class="mono">semantic_search_files</span> 是<strong>两种找法</strong>：前者在<strong>已打开的文件</strong>里按关键词逐行精确抓，后者在<strong>全部 chunk</strong> 里按语义模糊召回。要"原文逐字"用 grep，要"意思相近"用 semantic。</p>
<p>为什么 <span class="mono">FileBlock</span> 是 <span class="mono">read_only=True</span>？因为它是<strong>外部文档的镜像</strong>，不该被 agent 改写——你不希望 LLM"顺手"把你上传的合同改了。只读，正是把"源文档"和"agent 自己的记忆块"分开的护栏。</p>
<p>那"最多开 5 个"的上限又为何？因为打开的文件是<strong>实打实塞进上下文</strong>的只读块，要占 token。限量是替你守住上下文预算，免得一口气开十几个文件把窗口撑爆。</p>
<p>所以同一份文件，<span class="mono">SourcePassage</span> 与 <span class="mono">FileBlock</span> 是<strong>互补</strong>而非重复：先用 <span class="mono">semantic_search_files</span> 模糊定位到相关文件，再 <span class="mono">open_files</span> 把它逐字调进上下文细读。一个负责"找到"，一个负责"看清"。</p>
<p>把"一个文件 → 两种形态"画直，左边落库、右边进上下文：</p>
<div class="flow">
  <div class="node hl"><div class="nt">一个挂载文件</div><div class="nd">FileMetadata + FileContent</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">形态 A · 切块嵌入</div><div class="nd">SourcePassage（语义可搜）</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node q"><div class="nt">形态 B · open_files</div><div class="nd">FileAgent → FileBlock</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">上下文只读原文</div><div class="nd">visible_content（read_only=True）</div></div>
</div>
<details class="accordion"><summary>"打开的文件"为什么是另一套机制，而不是 passage？</summary><div class="acc-body">
<p><span class="mono">FileAgent</span>（<span class="mono">orm/files_agents.py</span>）是 <span class="mono">files_agents</span> junction 的一行，记"哪个 agent 开着哪个文件"，带 <span class="mono">is_open</span> / <span class="mono">visible_content</span>。它<strong>不进向量库</strong>，靠 <span class="mono">to_pydantic_block</span> 渲染成上下文里的 <span class="mono">FileBlock(read_only=True)</span>。</p>
<p>所以"打开文件" ＝ 把原文（片段）作为<strong>只读记忆块</strong>塞进上下文窗口，让 LLM 直接逐字读到——这是<strong>精确</strong>的；而 <span class="mono">SourcePassage</span> 是<strong>模糊、语义</strong>的近邻召回。两者解决不同问题。</p>
<p>元数据存 <span class="mono">orm/file.py::FileMetadata</span>（表 <span class="mono">files</span>，带 <span class="mono">processing_status</span> / <span class="mono">total_chunks</span> / <span class="mono">chunks_embedded</span>），全文存 <span class="mono">FileContent</span>（表 <span class="mono">file_contents</span>）。<span class="mono">open_files</span> 读全文，<span class="mono">semantic_search_files</span> 搜 chunk。</p>
</div></details>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">别把两种形态搞混：<strong>"上下文里打开的文件"（<span class="mono">FileBlock</span>，只读原文）</strong>不是<strong>"可语义搜索的 passage"（<span class="mono">SourcePassage</span>）</strong>。前者逐字、占上下文、默认最多 5 个；后者按意思召回、不占上下文。同一份文件，两条路。</span></div>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>Letta <strong>不另造"RAG 引擎"</strong>——它直接复用归档记忆那套向量机器，只把表、外键、junction、工具名各换一个。</p>
<p><span class="mono">SourcePassage</span>（你喂给 agent 的文档）和 <span class="mono">ArchivalPassage</span>（agent 自己写的记忆）是同一个 <span class="mono">BasePassage</span> 的两个兄弟，骑同一根 <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> 列、同一套 4096 padding、同一个 <span class="mono">cosine_distance</span>（第 27 课）。</p>
<p>于是"RAG"和"长期记忆"在物理层根本是<strong>一回事</strong>——唯一的真差别是来源：一个你给的，一个它写的。</p>
<p>次亮点：一份挂载的文件会<strong>同时</strong>活成两种形态——可语义搜索的 <span class="mono">SourcePassage</span> chunk，与上下文窗口里那块只读的 <span class="mono">FileBlock</span>(原文)。一份文件，两种"被记住"的方式。</p>
</div>
<h2>源是 org 级资产：挂载 ≠ 复制</h2>
<p>还有一处容易踩错：<strong>源不是某个 agent 私有的</strong>。<span class="mono">services/source_manager.py::SourceManager.create_source</span> 建出的 <span class="mono">Source</span> 是 <strong>org 级</strong>，可被同组织的<strong>多个 agent 共享</strong>。</p>
<p>怎么共享？<span class="mono">orm/sources_agents.py::SourcesAgents</span> 是一张<strong>复合主键的 M2M 表</strong>——一个源能连多个 agent，一个 agent 也能挂多个源。</p>
<p>复合主键 <span class="mono">(agent_id, source_id)</span> 保证同一对"agent — 源"<strong>只连一次</strong>，不会重复挂载；这和第 28 课 <span class="mono">blocks_agents</span> 那张共享块表是<strong>同一种套路</strong>——用 junction 表表达"谁能用什么"。</p>
<p>最关键的一点：<span class="mono">agent_manager.py::AgentManager.attach_source_async</span> "挂载一个源"时，<strong>只写一行 <span class="mono">sources_agents</span> junction</strong>——<strong>不复制 passage、不重新嵌入</strong>。passage 还是那一批，挂载只是"连一条线"。</p>
<p>这点呼应第 26 课的多租户：源在 org 这层登记一次，多个 agent 经 junction 复用同一批向量。检索时 <span class="mono">build_source_passage_query</span> 正是 join 这张 <span class="mono">SourcesAgents</span>，才知道"这个 agent 能搜哪些源"。</p>
<p>把账算清：一个 50 页的手册，挂给 10 个 agent，<strong>只嵌入一次</strong>、只存一份 passage；10 个 agent 经 10 行 <span class="mono">sources_agents</span> 共用它。若挂载真去"复制+重嵌"，那就是 10 倍的存储与嵌入开销——Letta 用一张 junction 表把这笔账省了。</p>
<p>这也是为什么源叫"org 级资产"：它和 agent 是<strong>多对多</strong>的松耦合，建一次、共享给多人；删 agent 不连累源，删源也只清掉 junction 连线——和第 26 课"组织拥有资源、成员按需挂载"的思路一脉相承。</p>
<p>一句话给源定性：它是<strong>组织的共享知识库</strong>，不是 agent 的私人笔记。私人笔记是归档（<span class="mono">archival_passages</span>），共享知识库是源（<span class="mono">source_passages</span>）——又一次落回"同底座、不同来源"。</p>
<details class="accordion"><summary>读源码时的术语漂移：<span class="mono">Source</span> 正改名 <span class="mono">Folder</span></summary><div class="acc-body">
<p>v0.16.8 里你会同时看到 <span class="mono">Source</span> 和 <span class="mono">Folder</span> 两个词。<span class="mono">schemas/source.py::Source</span> 的 docstring 已标 <strong>"Deprecated: Use Folder"</strong>，<span class="mono">PassageBase.source_id</span> 也打了 <span class="mono">deprecated</span> 标记。</p>
<p>但 <strong>ORM 表与类仍是 <span class="mono">source_*</span></strong>：表名 <span class="mono">source_passages</span> / <span class="mono">sources_agents</span>、外键 <span class="mono">source_id</span>、类 <span class="mono">SourcePassage</span> / <span class="mono">SourceManager</span> 一律没改。</p>
<p>结论：读到 <span class="mono">Folder</span> 知道它就是 <span class="mono">Source</span> 的新名；写 v0.16.8 代码仍照 <span class="mono">source_</span> 来。本课通篇用 <span class="mono">Source</span>，与源码一致。</p>
</div></details>
<h2>回扣与小结：RAG 就是"换了来源的归档记忆"</h2>
<p>收个尾。本课没引入任何新的向量技术，它通篇都在复用你<strong>早就学过</strong>的零件。</p>
<p>回扣第 27 课：两类 passage 骑的<strong>就是那根 <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> 列</strong>——同一套 4096 padding、同一个 <span class="mono">cosine_distance</span>。RAG 没有"自己的"向量存储。</p>
<p>回扣第 10、11 课：归档记忆那套 <span class="mono">archival_memory_insert</span> / <span class="mono">search</span> 是<strong>另一个来源</strong>的同款机器；本课的源只是把"谁来写"从 agent 换成了你。</p>
<p>回扣第 21 课：切块尺寸、查询嵌入都听 <span class="mono">EmbeddingConfig</span> 的——摄取和召回<strong>同一套配置</strong>，向量才在同一个空间里可比。</p>
<p>一句话串起来：<strong>RAG ＝ 归档记忆的向量机器 ＋ 外部来源的 passage ＋ 一张 <span class="mono">sources_agents</span> 共享表</strong>。底座没变，变的只是"东西从哪来"。</p>
<p>再补一刀对称之美：归档是 agent <strong>写给未来的自己</strong>，源是你<strong>写给 agent</strong> 的资料——方向相反，却共用同一套"嵌入 → 存 → cosine 召回"的肌肉。读 Letta 久了，你会反复遇到这种"一套机制、多处复用"。</p>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>源与归档<strong>不混</strong>：不同表 / 外键 / 工具，检索互不返回，写入点<strong>互斥</strong>（给错 source_id/archive_id 直接报错）。</p>
<p>源是 <strong>org 级、可共享</strong>，不是 per-agent；"挂载源"只写 <span class="mono">sources_agents</span> junction，<strong>不复制、不重嵌</strong> passage。</p>
<p>嵌入模型与维度<strong>必须一致</strong>：摄取和召回用同一套 <span class="mono">EmbeddingConfig</span>；pad 到 4096 会<strong>静默掩盖</strong>维度不匹配，埋下"搜不准"的坑。</p>
<p><span class="mono">pad</span> 到 <span class="mono">MAX_EMBEDDING_DIM</span> 仅 <strong>pgvector 路径</strong>做（TPUF 跳过）。</p>
<p><span class="mono">Source</span> 正改名 <span class="mono">Folder</span>，但 v0.16.8 的 ORM 表 / 类仍是 <span class="mono">source_*</span>；"上下文里开的文件"（<span class="mono">FileBlock</span>，只读）<strong>≠</strong>"可搜索的 passage"（<span class="mono">SourcePassage</span>）。</p>
</div>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li>RAG 与归档记忆<strong>同底座、不同来源</strong>：<span class="mono">SourcePassage</span>（你上传的文档）与 <span class="mono">ArchivalPassage</span>（agent 自己写的记忆）是同一 <span class="mono">BasePassage</span> 子类，共用第 27 课那根 <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> 列 ＋ 4096 padding ＋ <span class="mono">cosine_distance</span>。</li>
<li>摄取管线 <span class="mono">FileProcessor.process</span>：<span class="mono">create_file</span>(PARSING) → <span class="mono">extract_text</span>(OCR) → <span class="mono">upsert_file_content</span>(全文) → <span class="mono">insert_file_into_context_windows</span> → <span class="mono">chunk_text</span>(按 EmbeddingConfig) → <span class="mono">generate_embedded_passages</span>(batch 200) → <span class="mono">create_many_source_passages_async</span>(pad 4096)。</li>
<li>检索是<strong>同一套向量搜索、换表换工具</strong>：<span class="mono">build_source_passage_query</span> join <span class="mono">SourcesAgents</span>、工具 <span class="mono">semantic_search_files</span>；归档则 join <span class="mono">ArchivesAgents</span>、工具 <span class="mono">archival_memory_search</span>。</li>
<li>一份文件有<strong>两种形态</strong>：可语义搜的 <span class="mono">SourcePassage</span> chunk，与上下文里只读的 <span class="mono">FileAgent</span> / <span class="mono">FileBlock</span>(原文，默认最多开 5 个)。</li>
<li>源是 <strong>org 级可共享</strong>资产，<span class="mono">attach_source_async</span> 只写 junction 不复制；<span class="mono">Source</span> 正改名 <span class="mono">Folder</span>，但 v0.16.8 ORM 仍 <span class="mono">source_*</span>。</li>
</ul>
</div>
<p>把这条肌肉记忆带走：看到"RAG / 数据源"，先别找新引擎——先问<strong>"它和归档记忆是不是同一根向量列"</strong>。答案是肯定的，于是一切都顺理成章。</p>
<p>第八部分的进阶专题继续往下走。下一课我们换个视角，看 Letta 怎么把这些执行步骤变得<strong>可观测、可追踪</strong>。</p>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Lesson 27 cracked open the <span class="mono">Vector(4096)</span> column behind vector storage — how the memory an agent writes for itself lands in the database, and how it is recalled by <span class="mono">cosine_distance</span>. This lesson asks the natural next question: the documents <strong>you upload from outside</strong>, how do they burrow into that same vector machinery and become semantically searchable? The answer is three letters: RAG.</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Let's put a counterintuitive fact on the table first: Letta <strong>did not build a separate "RAG engine."</strong> It reuses Lesson 27's archival-memory vector machinery <strong>verbatim</strong>, swapping only the table, the foreign key, and the tool name. "RAG" and "long-term memory" are, at the physical layer, the very same thing.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>One sentence to grasp this lesson: <strong>RAG and archival memory are "same foundation, different source"</strong> — the same vector column, the same recall; the only real difference is "who wrote it in."</p>
<p>The foundation: <span class="mono">SourcePassage</span> (the documents you upload) and <span class="mono">ArchivalPassage</span> (the memory the agent writes for itself) are <strong>two sibling subclasses of the same <span class="mono">BasePassage</span></strong>, riding the same <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> column.</p>
<p>Ingestion: a file goes through a <strong>parse → chunk → embed</strong> pipeline and is scattered into a row of <span class="mono">SourcePassage</span> records, searchable from then on.</p>
<p>Retrieval: sources use <span class="mono">semantic_search_files</span>, archival uses <span class="mono">archival_memory_search</span> — <strong>two different tools, the same pgvector cosine</strong>.</p>
</div>
<p>Why single this out for a whole lesson? Because many people assume RAG is "another system" and go hunting for a config, an engine, an index service. Once you see that "it is just archival memory with a different source," you save a lot of time looking in the wrong place.</p>
<p>There's a practical payoff too: once you grasp the shared foundation, you know <strong>tuning RAG and tuning memory are one and the same job</strong> — swap the embedding model, adjust the chunk size, change the distance metric, and it takes effect for <strong>both</strong> source and archival at once, because they share that one column.</p>
<p>Hold onto this through-line: from start to finish, this lesson keeps re-proving four words — "<strong>same foundation, different source</strong>." First we meet the foundation, then walk the ingestion, and finally look at retrieval.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">Footnote: the two kinds of passage <strong>share</strong> Lesson 27's <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> column, the same 4096 padding, and the same <span class="mono">cosine_distance</span> ordering. The difference is <strong>not</strong> in the vector machinery, only in the <strong>source</strong> and the <strong>foreign key</strong>.</span></div>
<h2>One BasePassage, two sibling subclasses</h2>
<p>Meet the foundation first. <span class="mono">orm/passage.py::BasePassage</span> is an <span class="mono">__abstract__</span> base class — it <strong>builds no table of its own</strong>, it only dictates "what a passage looks like": primary key, text, metadata, and most crucially that one <strong>embedding vector column</strong>.</p>
<p>That column is precisely Lesson 27's protagonist: on Postgres it is <span class="mono">embedding = Vector(MAX_EMBEDDING_DIM)</span> (pgvector), on SQLite it is <span class="mono">CommonVector</span>. <strong>Same column, same 4096 padding, same <span class="mono">cosine_distance</span></strong> — the two subclasses <strong>inherit it verbatim</strong>, not a line changed.</p>
<p>The two subclasses part ways on one thing only — <strong>"whom they attach to"</strong>:</p>
<p><strong>① <span class="mono">SourcePassage(BasePassage, FileMixin, SourceMixin)</span></strong>: table <span class="mono">source_passages</span>, carrying <span class="mono">source_id</span> (required) + <span class="mono">file_id</span> (optional) + <span class="mono">file_name</span>. It belongs to "a particular file inside a particular source."</p>
<p><strong>② <span class="mono">ArchivalPassage(BasePassage, ArchiveMixin)</span></strong>: table <span class="mono">archival_passages</span>, carrying <span class="mono">archive_id</span>, plus one extra <span class="mono">passage_tags</span> tag junction. It belongs to "a particular archive."</p>
<p>Where do those foreign keys come from? All from three mixins in <span class="mono">orm/mixins.py</span>: <span class="mono">FileMixin</span> (gives file_id/file_name), <span class="mono">SourceMixin</span> (gives source_id), <span class="mono">ArchiveMixin</span> (gives archive_id). A subclass merely <strong>assembles mixins</strong> to obtain its own ownership foreign keys.</p>
<p>Why make the foundation <span class="mono">__abstract__</span>? Because that 4096-dim vector column, the <span class="mono">cosine_distance</span> algorithm, and the padding convention are <strong>meant to be written once</strong>. With both subclasses inheriting one definition, the disaster of "source and archival living in different vector spaces" becomes <strong>structurally impossible</strong>.</p>
<p>Why does <span class="mono">SourcePassage</span> need both <span class="mono">source_id</span> and <span class="mono">file_id</span>? Because one source can hold <strong>many files</strong>: <span class="mono">source_id</span> marks "which source it belongs to," <span class="mono">file_id</span> marks "which file inside the source it came from," and <span class="mono">file_name</span> makes the provenance easy to echo back.</p>
<p>The extra <span class="mono">passage_tags</span> junction on <span class="mono">ArchivalPassage</span> is <strong>archival-only</strong>: it lets the agent tag memory fragments and filter by tag at retrieval time (a callback to Lesson 11). Source passages have <strong>no</strong> such tag layer.</p>
<p>Remember this split: <strong>the mixin decides "ownership," the base decides "capability."</strong> Capability (vector, retrieval) is shared, ownership (source / archive, file) is separated — exactly the ORM-layer projection of "same foundation, different source."</p>
<p>Flip it around for clarity: to add a third kind of passage (say some "tool-produced cache"), you only write a new mixin + new table; inheriting <span class="mono">BasePassage</span> hands you the whole vector-retrieval stack <strong>for free</strong>. The foundation's reusability shows up exactly in this "adding a kind costs almost nothing."</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/passage.py</span><span class="ln">one abstract base, two sibling subclasses (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">BasePassage</span>(Base):
    __abstract__ = <span class="kw">True</span>                       <span class="cm"># no table; only defines "what a passage looks like"</span>
    text: Mapped[str]
    <span class="cm"># Lesson 27's column: Postgres uses pgvector, SQLite uses CommonVector</span>
    <span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
        embedding = <span class="fn">mapped_column</span>(<span class="fn">Vector</span>(MAX_EMBEDDING_DIM))   <span class="cm"># fixed 4096 dims</span>
    <span class="kw">else</span>:
        embedding = <span class="fn">mapped_column</span>(CommonVector)

<span class="kw">class</span> <span class="fn">SourcePassage</span>(BasePassage, FileMixin, SourceMixin):   <span class="cm"># documents you upload</span>
    __tablename__ = <span class="st">&quot;source_passages&quot;</span>      <span class="cm"># source_id(req) + file_id(opt) + file_name</span>

<span class="kw">class</span> <span class="fn">ArchivalPassage</span>(BasePassage, ArchiveMixin):            <span class="cm"># memory the agent writes itself</span>
    __tablename__ = <span class="st">&quot;archival_passages&quot;</span>    <span class="cm"># archive_id; plus passage_tags tags</span>
</pre></div>
<p>Lay "two subclasses, one foundation" out as two side-by-side columns and the difference is obvious — apart from source and foreign key, everything else is shared:</p>
<div class="cols">
  <div class="col"><h4>🧠 ArchivalPassage · agent-written</h4>
  <p>Table <span class="mono">archival_passages</span> · FK <span class="mono">archive_id</span> · tool <span class="mono">archival_memory_search</span> · join <span class="mono">ArchivesAgents</span> · carries <span class="mono">passage_tags</span>.</p>
  <p>Source: the agent writes it via <span class="mono">archival_memory_insert</span> (Lessons 10, 11).</p>
  </div>
  <div class="col"><h4>📄 SourcePassage · you-uploaded</h4>
  <p>Table <span class="mono">source_passages</span> · FK <span class="mono">source_id</span>+<span class="mono">file_id</span> · tool <span class="mono">semantic_search_files</span> · join <span class="mono">SourcesAgents</span>.</p>
  <p>Source: an uploaded file, built by the ingestion pipeline's parse+embed (next section).</p>
  </div>
</div>
<div class="cellgroup"><div class="cg-cap"><b>Both subclasses share: <span class="mono">BasePassage</span>'s one vector column (Lesson 27)</b></div><div class="cells"><span class="cell">archival_passages</span><span class="sep">·</span><span class="cell">source_passages</span><span class="sep">→</span><span class="cell hl">BasePassage.embedding = Vector(MAX_EMBEDDING_DIM)</span><span class="sep">·</span><span class="cell hl">cosine_distance</span></div></div>
<details class="accordion"><summary>Are source and archival really "kept entirely apart"?</summary><div class="acc-body">
<p><strong>Mutually exclusive writes (DB-layer guard)</strong>: <span class="mono">PassageManager.create_source_passage_async</span> <strong>requires</strong> <span class="mono">source_id</span> and <strong>forbids</strong> <span class="mono">archive_id</span>; <span class="mono">create_agent_passage_async</span> is the reverse. Pass the wrong one and it errors out immediately.</p>
<p><strong>Retrieval never crosses over</strong>: sources go through <span class="mono">build_source_passage_query</span> (scanning <span class="mono">source_passages</span>), archival through <span class="mono">build_agent_passage_query</span> (scanning <span class="mono">archival_passages</span>). Each query <strong>scans its own table</strong> and never mixes the other's rows into the result.</p>
<p>So "same foundation" means the <strong>physical column and algorithm</strong> are identical, not that "the data is commingled." The two kinds of passage are <strong>separate</strong> at all four levels: table, foreign key, tool, and query.</p>
</div></details>
<div class="card analogy"><div class="tag">📝 Real-world analogy</div>
<p>Picture the vector store as a <strong>library</strong> holding <strong>two kinds of books</strong>.</p>
<p>One kind is <strong>books you donate</strong> (<span class="mono">SourcePassage</span> / RAG): documents brought in from outside, which the librarian tears into pages, numbers, and shelves.</p>
<p>The other is <strong>the librarian's own handwritten reading notes</strong> (<span class="mono">ArchivalPassage</span> / archival): jottings the agent makes as it works.</p>
<p>Both kinds go into <strong>the same "search by meaning" index</strong> (that one vector column) — at query time both are ranked by "closeness of meaning."</p>
<p>They just sit on <strong>two different shelves</strong> (two tables), and borrowing means filling out <strong>different request slips</strong> (two tools): use <span class="mono">semantic_search_files</span> for donated books, <span class="mono">archival_memory_search</span> to flip through the notes.</p>
</div>
<h2>The ingestion pipeline: how a file becomes a row of searchable passages</h2>
<p>With the foundation met, let's see "how a file gets in." The modern ingestion entry point is <span class="mono">services/file_processor/file_processor.py::FileProcessor.process</span>, which works a raw file step by step into a row of <span class="mono">SourcePassage</span> records.</p>
<p>The whole pipeline breaks into eight steps, from upload all the way to landing in the database. Look at the panorama first, then we'll explain segment by segment:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Upload → into some source</h4><p>The file is uploaded and assigned to an already-created <span class="mono">Source</span> (org-scoped; detailed next section).</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>create_file (PARSING)</h4><p><span class="mono">FileManager.create_file</span> registers one <span class="mono">FileMetadata</span> row, status set to <span class="mono">PARSING</span>.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>extract_text (OCR)</h4><p><span class="mono">FileParser.extract_text</span> pulls the full text: PDFs/images go through OCR, documents convert to markdown.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>upsert_file_content (full text)</h4><p>The full text lands in the <span class="mono">file_contents</span> table — the original kept on file, independent of chunking.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>insert_file_into_context_windows</h4><p>It "opens" the file into a <span class="mono">FileAgent</span> (read-only original in context; covered in the final section).</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>chunk_text (by EmbeddingConfig)</h4><p><span class="mono">LlamaIndexChunker.chunk_text</span> chunks the text; <span class="mono">chunk_size</span> comes from <span class="mono">EmbeddingConfig</span> (Lesson 21).</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>generate_embedded_passages (batch 200)</h4><p>The <span class="mono">Embedder</span> computes embedding vectors in batches of 200.</p></div></div>
  <div class="step"><div class="num">8</div><div class="sc"><h4>create_many_source_passages_async</h4><p>Bulk-writes into <span class="mono">source_passages</span>, each padded to 4096 → a row of <span class="mono">SourcePassage</span> records.</p></div></div>
</div>
<p>Put those eight steps into code, drop the error handling and the state machine, and the skeleton is this straight:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/file_processor/file_processor.py</span><span class="ln">FileProcessor.process: store text → chunk → embed → land (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">process</span>(self, source_id, content, ...):
    <span class="cm"># 1) register the file row, status set to PARSING</span>
    file = <span class="kw">await</span> self.file_manager.<span class="fn">create_file</span>(..., status=FileProcessingStatus.PARSING)
    <span class="cm"># 2) pull full text (OCR / markdown), store into file_contents</span>
    text = <span class="kw">await</span> self.file_parser.<span class="fn">extract_text</span>(content)
    <span class="kw">await</span> self.file_manager.<span class="fn">upsert_file_content</span>(file.id, text)
    <span class="cm"># 3) "open" the file into context (FileAgent, see final section)</span>
    <span class="kw">await</span> self.agent_manager.<span class="fn">insert_file_into_context_windows</span>(source_id, file, ...)
    <span class="cm"># 4) chunk -&gt; embed (chunk_size comes from EmbeddingConfig)</span>
    chunks = self.chunker.<span class="fn">chunk_text</span>(text)
    passages = <span class="kw">await</span> self.embedder.<span class="fn">generate_embedded_passages</span>(chunks, batch_size=<span class="nb">200</span>)
    <span class="cm"># 5) bulk-write into source_passages (each padded to 4096)</span>
    <span class="kw">await</span> self.passage_manager.<span class="fn">create_many_source_passages_async</span>(passages, source_id=source_id)
</pre></div>
<p>Read the pipeline segment by segment. <strong>The first three steps "store the original"</strong>: <span class="mono">create_file</span> registers the file as one <span class="mono">FileMetadata</span> row (status <span class="mono">PARSING</span>); <span class="mono">extract_text</span> pulls plain text via OCR/markdown; <span class="mono">upsert_file_content</span> stores the full text into the <span class="mono">file_contents</span> table.</p>
<p><strong>The fourth step is a fork</strong>: <span class="mono">insert_file_into_context_windows</span> "opens" the file into the agent's context (creating a <span class="mono">FileAgent</span>) — that branch is saved for the final section.</p>
<p>The fork itself is rather elegant: <strong>ingest once, produce twice</strong> — the same pass both chunks-and-embeds the file (building RAG) and "opens" it into context (building a <span class="mono">FileAgent</span>). Upload one file and both forms are ready at once.</p>
<p><strong>The last three steps are where RAG is built</strong>: <span class="mono">chunk_text</span> chunks by <span class="mono">EmbeddingConfig</span>, <span class="mono">generate_embedded_passages</span> embeds 200 at a time, and <span class="mono">create_many_source_passages_async</span> lands them into <span class="mono">source_passages</span>.</p>
<p>That <span class="mono">status=PARSING</span> line is no decoration. <span class="mono">FileMetadata</span> carries a <span class="mono">processing_status</span> field plus two counters, <span class="mono">total_chunks</span> / <span class="mono">chunks_embedded</span> — status starts at <span class="mono">PARSING</span>, the counters track embedding progress, and only when every chunk is embedded is it ready. The frontend's "processing…" progress bar reads exactly this.</p>
<p>Why store the full text separately in <span class="mono">file_contents</span> rather than keep only chunks? Because the two forms have different needs: <strong>chunks serve semantic recall</strong> (fuzzy-find relevant passages), <strong>full text serves verbatim opening</strong> (<span class="mono">open_files</span> wants the text exactly as is). Stored apart, the two paths don't interfere.</p>
<p>Why embed in <strong>batches of 200</strong>? Because embedding calls an external model API; sending one at a time is too slow and too costly. Batch them and send once: higher throughput, fewer round trips. This is the familiar engineering move of "batching to amortize overhead."</p>
<p>A word on resilience: the full text in <span class="mono">file_contents</span> is a master copy <strong>independent</strong> of the chunks. Want to swap the embedding model later and re-chunk/re-embed? The original is still there, no need to make the user re-upload — zero out <span class="mono">total_chunks</span> and re-run the back half.</p>
<details class="accordion"><summary>Ingestion has two paths: the modern file_processor and the legacy connectors</summary><div class="acc-body">
<p><strong>Modern (the mainline)</strong>: <span class="mono">services/file_processor/file_processor.py::FileProcessor.process</span> — with OCR/markdown parsing, <span class="mono">LlamaIndexChunker</span> chunking, <span class="mono">generate_embedded_passages</span> batch embedding, and finally <span class="mono">create_many_source_passages_async</span>. This is what the lesson covers.</p>
<p><strong>Legacy (the old path)</strong>: <span class="mono">data_sources/connectors.py::load_data</span> — using <span class="mono">DirectoryConnector</span> plus llama_index's <span class="mono">TokenTextSplitter</span>, calling the <strong>deprecated</strong> <span class="mono">create_many_passages_async</span>.</p>
<p>For v0.16.8, lock onto the <span class="mono">file_processor</span> path; if you run into <span class="mono">connectors.load_data</span>, just recognize it as the old path and don't model new code on it.</p>
</div></details>
<div class="note tip"><span class="ni">🧩</span><span class="nx">The <span class="mono">chunk_size</span> isn't picked arbitrarily; it comes from the agent's <span class="mono">EmbeddingConfig</span> (Lesson 21) — <strong>chunks are cut as large as the embedding model's window</strong>. Ingestion and recall must use the <strong>same embedding config</strong>, or the vectors on the two sides simply aren't in the same space.</span></div>
<div class="cute"><div class="row"><span class="emoji">📄</span><span class="lab">one document</span><span class="arrow">→</span><span class="emoji">📚</span><span class="lab">cut into cards</span><span class="arrow">→</span><span class="emoji">🔢</span><span class="bubble">stamp each with a vector</span></div><div class="cap">📄 one uploaded document is split into 📚 a stack of little cards (chunks), each stamped with a 🔢 vector (embedding), then lined up on that 4096-dim shelf — and from then on you can grab the closest few "by meaning" in one go</div></div>
<h2>Retrieval: the same vector search, just a different tool and table</h2>
<p>Passages are built — how do you query them? The key is still "same foundation, different source": <strong>retrieval also uses the same vector search</strong>, only the query builder and the tool name each get swapped.</p>
<p>The source retrieval builder is <span class="mono">services/helpers/agent_manager_helper.py::build_source_passage_query</span>, and it is <strong>nearly identical in shape</strong> to archival's <span class="mono">build_agent_passage_query</span> — the only difference is which junction it joins and which table it scans.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/helpers/agent_manager_helper.py</span><span class="ln">build_source_passage_query: embed query → join → cosine sort (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">build_source_passage_query</span>(agent_id, query_text, embed_config, ...):
    <span class="cm"># 1) embed the query text, pad to 4096 (same config as on write)</span>
    q = <span class="fn">embed_query</span>(query_text, embed_config)
    q = np.<span class="fn">pad</span>(q, (<span class="nb">0</span>, MAX_EMBEDDING_DIM - <span class="fn">len</span>(q)))
    <span class="cm"># 2) take only passages from "sources this agent attached": join SourcesAgents</span>
    query = (
        <span class="fn">select</span>(SourcePassage)
        .<span class="fn">join</span>(SourcesAgents, SourcesAgents.source_id == SourcePassage.source_id)
        .<span class="fn">where</span>(SourcesAgents.agent_id == agent_id)
    )
    <span class="cm"># 3) ascending by cosine distance (Postgres pgvector; SQLite uses numpy)</span>
    <span class="kw">return</span> query.<span class="fn">order_by</span>(SourcePassage.embedding.<span class="fn">cosine_distance</span>(q).<span class="fn">asc</span>())
</pre></div>
<p>Three steps to understand this query. <strong>① Embed + pad</strong>: embed the query text with the <strong>same <span class="mono">EmbeddingConfig</span></strong>, then <span class="mono">np.pad</span> to 4096 so it aligns with the padded vectors in the store.</p>
<p><strong>② Join scopes the range</strong>: <span class="mono">select(SourcePassage)</span> join <span class="mono">SourcesAgents</span> on <span class="mono">source_id</span>, where <span class="mono">agent_id</span> — searching only passages in "the sources this agent has attached," never out of bounds.</p>
<p><strong>③ Sort</strong>: Postgres uses <span class="mono">embedding.cosine_distance(q).asc()</span> (pgvector), SQLite falls back to numpy for the distance; the text fallback uses <span class="mono">func.lower(text).contains</span>.</p>
<p>Don't get the direction backwards: <span class="mono">cosine_distance</span> is a <strong>distance</strong>, <strong>smaller is closer</strong>, so use <span class="mono">.asc()</span> to take the top few — the exact opposite of "bigger similarity is better" (a callback to Lesson 27).</p>
<p>Compare archival's <span class="mono">build_agent_passage_query</span>: the same embed + pad + cosine, only it joins <span class="mono">ArchivesAgents</span> (on <span class="mono">archive_id</span>) and can also filter by tag. <strong>Same machine, different connector.</strong></p>
<p>That <span class="mono">func.lower(text).contains</span> text fallback is a back road for the "no embedding / pure keyword" case: when no vector is available, you can at least match by substring, case-insensitively, instead of coming up empty-handed.</p>
<p>One more branch: the <span class="mono">np.pad</span> to 4096 happens <strong>only on the pgvector path</strong>; if you go through the external vector store Turbopuffer (TPUF), padding is <strong>skipped</strong> — it manages dimensions itself. Padding is a concession to pgvector's "fixed-length column," not a universal step.</p>
<p>Don't underestimate that <span class="mono">join SourcesAgents</span>: it is the <strong>multi-tenant guardrail</strong> (a callback to Lesson 26). Without it, the vector search would reach other agents' and other orgs' sources; with it, each agent can only search the handful of sources <strong>it has attached</strong>.</p>
<div class="note info"><span class="ni">🔧</span><span class="nx">Watch out for the split between "function declaration" and "real implementation": the <span class="mono">semantic_search_files</span> / <span class="mono">archival_memory_search</span> in <span class="mono">function_sets/files.py</span> and <span class="mono">function_sets/base.py</span> are just <span class="mono">raise NotImplementedError</span> <strong>schema stubs</strong>; the real work lives in <span class="mono">tool_executor/files_tool_executor.py</span> and <span class="mono">core_tool_executor.py</span>.</span></div>
<p>Straighten the source-retrieval chain into a line and the five nodes are clear at a glance:</p>
<div class="flow">
  <div class="node hl"><div class="nt">query text</div><div class="nd">find passages about X</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">embed + pad</div><div class="nd">embed(q) → np.pad 4096</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">select(SourcePassage)</div><div class="nd">join SourcesAgents · source_id</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">cosine_distance.asc()</div><div class="nd">ranked by closeness</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">top-k passages</div><div class="nd">fed back to the tool caller</div></div>
</div>
<p>Finally, a table lays "source vs archival" side by side across six dimensions, handy to look back at any time:</p>
<table class="t">
<tr><th>Dimension</th><th>SourcePassage (source / RAG)</th><th>ArchivalPassage (archival)</th></tr>
<tr><td>Table</td><td class="mono">source_passages</td><td class="mono">archival_passages</td></tr>
<tr><td>Source FK</td><td class="mono">source_id (req) + file_id (opt)</td><td class="mono">archive_id</td></tr>
<tr><td>Who writes it</td><td>you upload docs; built by ingestion</td><td>the agent calls archival_memory_insert</td></tr>
<tr><td>Query builder</td><td class="mono">build_source_passage_query</td><td class="mono">build_agent_passage_query</td></tr>
<tr><td>Retrieval tool</td><td class="mono">semantic_search_files</td><td class="mono">archival_memory_search</td></tr>
<tr><td>Tags</td><td>none</td><td class="mono">passage_tags junction</td></tr>
</table>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">orm/passage.py::SourcePassage / ArchivalPassage</span> — two subclasses of the same <span class="mono">BasePassage</span>, split across tables <span class="mono">source_passages / archival_passages</span>.</p>
<p><span class="mono">services/file_processor/file_processor.py::FileProcessor.process</span> — the modern ingestion pipeline: parse → chunk → embed → <span class="mono">create_many_source_passages_async</span>.</p>
<p><span class="mono">services/helpers/agent_manager_helper.py::build_source_passage_query</span> — source vector search: embed query + pad + join <span class="mono">SourcesAgents</span> + <span class="mono">cosine_distance</span>.</p>
<p><span class="mono">orm/files_agents.py::FileAgent</span> — the file's other form: a read-only <span class="mono">FileBlock</span> in context (next section).</p>
</div>
<h2>A file's two forms: a searchable passage vs an "opened file" in context</h2>
<p>Back to that fork at step five of the ingestion pipeline. An attached file lives in Letta as <strong>two forms at once</strong> — this is the lesson's second point worth remembering.</p>
<p><strong>Form A: the searchable RAG chunk</strong>, the <span class="mono">SourcePassage</span> we just covered — chunked, embedded, recalled by cosine.</p>
<p><strong>Form B: the "opened file" in context</strong>, a different mechanism: <span class="mono">orm/files_agents.py::FileAgent</span>. It is one row on the <span class="mono">files_agents</span> junction, carrying <span class="mono">is_open</span> / <span class="mono">visible_content</span>.</p>
<div class="cellgroup"><div class="cg-cap"><b>One file, two forms: metadata <span class="mono">FileMetadata</span> (table files) + full text <span class="mono">FileContent</span> (table file_contents)</b></div><div class="cells"><span class="cell hl">SourcePassage</span><span class="lab">embedded · semantic search</span><span class="sep">‖</span><span class="cell q">FileAgent / FileBlock</span><span class="lab">visible_content · read-only original in context</span></div></div>
<p>The key line: <span class="mono">FileAgent.to_pydantic_block(...)</span> renders it into a <strong><span class="mono">FileBlock(read_only=True)</span></strong> — "opening a file" = stuffing a <strong>read-only memory block</strong> into context, whose content is the original text (or a fragment).</p>
<p>The tools that operate this layer are <span class="mono">open_files</span> / <span class="mono">grep_files</span>: open a file into context, and grab lines within already-open files. Note the cap — <strong>at most 5 files open</strong> at once by default.</p>
<p><span class="mono">grep_files</span> and <span class="mono">semantic_search_files</span> are <strong>two ways of finding</strong>: the former grabs lines exactly by keyword <strong>within already-open files</strong>, the latter fuzzily recalls across <strong>all chunks</strong> by meaning. Want "verbatim text," use grep; want "close in meaning," use semantic.</p>
<p>Why is <span class="mono">FileBlock</span> <span class="mono">read_only=True</span>? Because it is a <strong>mirror of an external document</strong> and shouldn't be rewritten by the agent — you don't want the LLM "casually" editing the contract you uploaded. Read-only is exactly the guardrail separating "source document" from "the agent's own memory block."</p>
<p>And why the "at most 5 open" cap? Because an opened file is a read-only block <strong>actually stuffed into context</strong>, costing tokens. The limit guards your context budget for you, so you don't blow the window by opening a dozen files at once.</p>
<p>So for the same file, <span class="mono">SourcePassage</span> and <span class="mono">FileBlock</span> are <strong>complementary, not redundant</strong>: first use <span class="mono">semantic_search_files</span> to fuzzily locate the relevant file, then <span class="mono">open_files</span> to pull it verbatim into context for a close read. One handles "finding," the other "seeing clearly."</p>
<p>Straighten "one file → two forms": database on the left, context on the right:</p>
<div class="flow">
  <div class="node hl"><div class="nt">an attached file</div><div class="nd">FileMetadata + FileContent</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Form A · chunk+embed</div><div class="nd">SourcePassage (semantically searchable)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node q"><div class="nt">Form B · open_files</div><div class="nd">FileAgent → FileBlock</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">read-only original in context</div><div class="nd">visible_content (read_only=True)</div></div>
</div>
<details class="accordion"><summary>Why is an "opened file" a different mechanism, not a passage?</summary><div class="acc-body">
<p><span class="mono">FileAgent</span> (<span class="mono">orm/files_agents.py</span>) is one row on the <span class="mono">files_agents</span> junction, recording "which agent has which file open," with <span class="mono">is_open</span> / <span class="mono">visible_content</span>. It <strong>does not enter the vector store</strong>; it renders via <span class="mono">to_pydantic_block</span> into a <span class="mono">FileBlock(read_only=True)</span> in context.</p>
<p>So "opening a file" = stuffing the original text (a fragment) into the context window as a read-only memory block, so the LLM reads it verbatim — this is <strong>exact</strong>; whereas <span class="mono">SourcePassage</span> is <strong>fuzzy, semantic</strong> nearest-neighbor recall. The two solve different problems.</p>
<p>Metadata lives in <span class="mono">orm/file.py::FileMetadata</span> (table <span class="mono">files</span>, with <span class="mono">processing_status</span> / <span class="mono">total_chunks</span> / <span class="mono">chunks_embedded</span>), full text in <span class="mono">FileContent</span> (table <span class="mono">file_contents</span>). <span class="mono">open_files</span> reads the full text, <span class="mono">semantic_search_files</span> searches chunks.</p>
</div></details>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">Don't conflate the two forms: <strong>"a file opened in context" (<span class="mono">FileBlock</span>, read-only original)</strong> is not <strong>"a semantically searchable passage" (<span class="mono">SourcePassage</span>)</strong>. The former is verbatim, occupies context, and is capped at 5 by default; the latter is recalled by meaning and costs no context. One file, two paths.</span></div>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>Letta <strong>builds no separate "RAG engine"</strong> — it directly reuses archival memory's vector machinery, swapping only the table, the foreign key, the junction, and the tool name.</p>
<p><span class="mono">SourcePassage</span> (the documents you feed the agent) and <span class="mono">ArchivalPassage</span> (the memory the agent writes itself) are two siblings of the same <span class="mono">BasePassage</span>, riding the same <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> column, the same 4096 padding, the same <span class="mono">cosine_distance</span> (Lesson 27).</p>
<p>So "RAG" and "long-term memory" are, at the physical layer, the very same thing — the only real difference is the source: one you give, one it writes.</p>
<p>A secondary highlight: an attached file lives as <strong>two forms at once</strong> — the semantically searchable <span class="mono">SourcePassage</span> chunk, and that read-only <span class="mono">FileBlock</span> (the original) in the context window. One file, two ways of "being remembered."</p>
</div>
<h2>A source is an org-scoped asset: attaching ≠ copying</h2>
<p>Another easy misstep: a source is <strong>not private to any one agent</strong>. The <span class="mono">Source</span> built by <span class="mono">services/source_manager.py::SourceManager.create_source</span> is <strong>org-scoped</strong> and can be <strong>shared across multiple agents</strong> in the same org.</p>
<p>How is it shared? <span class="mono">orm/sources_agents.py::SourcesAgents</span> is a <strong>composite-PK M2M table</strong> — one source can link to many agents, and one agent can attach many sources.</p>
<p>The composite PK <span class="mono">(agent_id, source_id)</span> guarantees the same "agent — source" pair <strong>links only once</strong>, never double-attached; this is the <strong>same pattern</strong> as Lesson 28's shared-block table <span class="mono">blocks_agents</span> — using a junction table to express "who can use what."</p>
<p>The crucial point: when <span class="mono">agent_manager.py::AgentManager.attach_source_async</span> "attaches a source," it <strong>writes only one <span class="mono">sources_agents</span> junction row</strong> — <strong>no passage copy, no re-embedding</strong>. The passages are still the same batch; attaching just "draws a line."</p>
<p>This echoes Lesson 26's multi-tenancy: a source is registered once at the org level, and multiple agents reuse the same batch of vectors through the junction. At retrieval, <span class="mono">build_source_passage_query</span> joins exactly this <span class="mono">SourcesAgents</span> to know "which sources this agent may search."</p>
<p>Do the math: a 50-page manual attached to 10 agents is <strong>embedded once, stored once</strong> as one set of passages; 10 agents share it via 10 <span class="mono">sources_agents</span> rows. If attaching truly did "copy + re-embed," that would be 10× the storage and embedding cost — Letta saves that bill with a single junction table.</p>
<p>This is also why a source is an "org-scoped asset": it is loosely coupled to agents in a many-to-many way, built once and shared with many; deleting an agent doesn't drag the source down, and deleting a source only clears the junction lines — of a piece with Lesson 26's "the org owns resources, members attach as needed."</p>
<p>To characterize a source in one line: it is the <strong>org's shared knowledge base</strong>, not an agent's private notebook. The private notebook is archival (<span class="mono">archival_passages</span>), the shared knowledge base is the source (<span class="mono">source_passages</span>) — landing once more on "same foundation, different source."</p>
<details class="accordion"><summary>Terminology drift when reading the source: Source is being renamed Folder</summary><div class="acc-body">
<p>In v0.16.8 you'll see both words, <span class="mono">Source</span> and <span class="mono">Folder</span>. The docstring of <span class="mono">schemas/source.py::Source</span> already reads <strong>"Deprecated: Use Folder"</strong>, and <span class="mono">PassageBase.source_id</span> is also marked <span class="mono">deprecated</span>.</p>
<p>But the <strong>ORM tables and classes are still <span class="mono">source_*</span></strong>: table names <span class="mono">source_passages</span> / <span class="mono">sources_agents</span>, the foreign key <span class="mono">source_id</span>, and the classes <span class="mono">SourcePassage</span> / <span class="mono">SourceManager</span> are all unchanged.</p>
<p>Conclusion: when you read <span class="mono">Folder</span>, know it's the new name for <span class="mono">Source</span>; for v0.16.8 code still go by <span class="mono">source_</span>. This lesson uses <span class="mono">Source</span> throughout, consistent with the source code.</p>
</div></details>
<h2>Callbacks and recap: RAG is just "archival memory with a different source"</h2>
<p>Let's wrap up. This lesson introduced no new vector technology; throughout, it reused parts <strong>you already learned</strong>.</p>
<p>Callback to Lesson 27: the two kinds of passage ride <strong>that very <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> column</strong> — the same 4096 padding, the same <span class="mono">cosine_distance</span>. RAG has no vector storage "of its own."</p>
<p>Callback to Lessons 10, 11: archival memory's <span class="mono">archival_memory_insert</span> / search is the same machine fed by <strong>another source</strong>; this lesson's source merely swaps "who writes" from the agent to you.</p>
<p>Callback to Lesson 21: chunk size and query embedding both obey <span class="mono">EmbeddingConfig</span> — ingestion and recall share one config, and only then are vectors comparable in the same space.</p>
<p>One line to tie it together: <strong>RAG = archival memory's vector machine + passages from an external source + one <span class="mono">sources_agents</span> sharing table</strong>. The foundation didn't change; all that changed is "where the stuff comes from."</p>
<p>One more note on symmetry: archival is the agent <strong>writing to its future self</strong>, a source is you <strong>writing material for the agent</strong> — opposite directions, yet sharing the same "embed → store → cosine recall" muscle. Read Letta long enough and you'll keep meeting this "one mechanism, reused in many places."</p>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<p>Source and archival don't mix: different tables / foreign keys / tools, retrieval never crosses over, and the write points are <strong>mutually exclusive</strong> (pass the wrong source_id/archive_id and it errors out).</p>
<p>A source is <strong>org-scoped and shareable</strong>, not per-agent; "attaching a source" only writes a <span class="mono">sources_agents</span> junction row and does <strong>not copy or re-embed</strong> passages.</p>
<p>The embedding model and dimension <strong>must match</strong>: ingestion and recall use the same <span class="mono">EmbeddingConfig</span>; padding to 4096 will <strong>silently mask</strong> a dimension mismatch, burying a "bad search results" trap.</p>
<p>Padding to <span class="mono">MAX_EMBEDDING_DIM</span> happens only on the pgvector path (TPUF skips it).</p>
<p><span class="mono">Source</span> is being renamed <span class="mono">Folder</span>, but v0.16.8's ORM tables / classes are still <span class="mono">source_*</span>; "a file opened in context" (<span class="mono">FileBlock</span>, read-only) <strong>≠</strong> "a searchable passage" (<span class="mono">SourcePassage</span>).</p>
</div>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li>RAG and archival memory are <strong>same foundation, different source</strong>: <span class="mono">SourcePassage</span> (the documents you upload) and <span class="mono">ArchivalPassage</span> (the memory the agent writes itself) are subclasses of the same <span class="mono">BasePassage</span>, sharing Lesson 27's <span class="mono">Vector(MAX_EMBEDDING_DIM)</span> column + 4096 padding + <span class="mono">cosine_distance</span>.</li>
<li>Ingestion pipeline <span class="mono">FileProcessor.process</span>: <span class="mono">create_file</span>(PARSING) → <span class="mono">extract_text</span>(OCR) → <span class="mono">upsert_file_content</span>(full text) → <span class="mono">insert_file_into_context_windows</span> → <span class="mono">chunk_text</span>(by EmbeddingConfig) → <span class="mono">generate_embedded_passages</span>(batch 200) → <span class="mono">create_many_source_passages_async</span>(pad 4096).</li>
<li>Retrieval is <strong>the same vector search with a different table and tool</strong>: <span class="mono">build_source_passage_query</span> joins <span class="mono">SourcesAgents</span>, tool <span class="mono">semantic_search_files</span>; archival joins <span class="mono">ArchivesAgents</span>, tool <span class="mono">archival_memory_search</span>.</li>
<li>A file has <strong>two forms</strong>: the semantically searchable <span class="mono">SourcePassage</span> chunk, and the read-only <span class="mono">FileAgent</span> / <span class="mono">FileBlock</span> (the original) in context (at most 5 open by default).</li>
<li>A source is an <strong>org-scoped, shareable</strong> asset; <span class="mono">attach_source_async</span> only writes the junction, no copy; <span class="mono">Source</span> is being renamed <span class="mono">Folder</span>, but v0.16.8's ORM is still <span class="mono">source_*</span>.</li>
</ul>
</div>
<p>Take this muscle memory with you: when you see "RAG / data sources," don't go hunting for a new engine first — first ask "is it the same vector column as archival memory?" The answer is yes, and everything falls into place.</p>
<p>Part 8's advanced topics roll on. Next lesson we switch perspective and see how Letta makes these execution steps <strong>observable and traceable</strong>.</p>
""",
}
