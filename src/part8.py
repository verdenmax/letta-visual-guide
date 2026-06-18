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
        <span class="kw">if</span> count % self.group.sleeptime_agent_frequency != 0:
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
<p>写库的细节：sleeptime 的改写最终落到 <span class="mono">block_manager.update_block_async</span> / <span class="mono">update_memory_if_changed_async</span>——只改<strong>那一行</strong> Block 的值。前台 agent 的 <span class="mono">core_memory</span> 经 <span class="mono">blocks_agents</span> 指的正是这同一行，于是它"自动"看到更新，无需任何同步代码。</p>
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
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson starts by putting a counterintuitive fact on the table: in v0.16.8 only two multi-agent mechanisms are <strong>actually live</strong> — one agent directly calling another's message API (<span class="mono">send_message_to_agent_*</span>), and a background sleeptime agent that wakes every few turns to rewrite memory. The classic “group managers” are mostly sleeping scaffolding.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>One sentence to grasp this lesson: <strong>v0.16.8's multi-agent isn't “one scheduler orchestrating a flock of agents,” but “agents calling each other's API plus sharing one row of memory.”</strong></p>
<p>Live path one: tools like <span class="mono">send_message_to_agent_and_wait_for_reply</span> let agent A <strong>re-enter the server</strong> over REST, run agent B's own full loop, and fetch B's reply back.</p>
<p>Live path two: <strong>sleeptime</strong> — after the foreground agent finishes a turn, a background sleeptime agent is woken up, dedicated to <strong>tidying memory</strong>.</p>
<p>Their only coordination primitive is humble to the point of being just <strong>one shared <span class="mono">Block</span> row</strong>: A writes, and B reads it the next time it rebuilds its system prompt.</p>
<p>As for the classic group managers (<span class="mono">round_robin / supervisor / dynamic</span>)? Only schema and class skeletons remain; their executor is <strong>never called</strong>.</p>
</div>
<p>Let's lay the “two live paths plus one shared memory row” out as two columns first, to get a skeleton in mind before unpacking each one.</p>
<div class="cols">
  <div class="col"><h4>🛠️ Path one · agent calls agent directly</h4>
  <p>A calls <span class="mono">send_message_to_agent_and_wait_for_reply</span> → builds a client in the sandbox → <span class="mono">messages.create(B)</span> re-enters over REST → runs <strong>B's own loop</strong> → the reply flows back to A.</p>
  <p>No “group manager” is involved — it's an <strong>ordinary outbound API call</strong>, except the callee happens to be an agent too.</p>
  </div>
  <div class="col"><h4>😴 Path two · sleeptime edits memory in the background</h4>
  <p>The foreground agent finishes → the turn counter hits → a background sleeptime agent is <strong>non-blockingly</strong> woken → it rewrites the <strong>shared Block</strong> with memory tools.</p>
  <p>The foreground <strong>doesn't wait</strong> for it; on the next turn, rebuilding the system prompt, it naturally reads the tidied memory.</p>
  </div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">Footnote: the classic group managers (<span class="mono">round_robin / supervisor / dynamic</span>) stop at the <strong>schema level</strong> — enums, ORM, and class skeletons all exist, but they're <strong>not wired up</strong> and can't run over a live API. This lesson recognizes only those two live paths.</span></div>
<p>Before we dive in, let's calibrate expectations: if you came for “multi-agent scheduling like an orchestration framework,” v0.16.8 may surprise you — it gives not an orchestration layer but <strong>two lower-level primitives</strong>. Understand these two, and you can build orchestration on top of them yourself.</p>
<h2>First, count them: how many multi-agent mechanisms are actually live in v0.16.8</h2>
<p>Many people start by hunting for a “group-chat scheduler” — assuming some object queues turns and lets A, B, and C speak in rotation. In v0.16.8 that object is <strong>mostly asleep</strong>.</p>
<p>The group manager's executor entry, <span class="mono">groups/helpers.py::load_multi_agent</span>, is <strong>never called</strong> anywhere on the live path; the <span class="mono">/v1/groups</span> routes are entirely <span class="mono">deprecated=True</span> with <strong>no send-message endpoint</strong>; even <span class="mono">SupervisorMultiAgent.step</span> is <strong>commented out entirely</strong>.</p>
<p>So let's lay out the six <span class="mono">ManagerType</span> enum values — their “intended behavior” beside their “real v0.16.8 status” — side by side. Only one row is green.</p>
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
<p>Why keep these sleeping enums? Because they're <strong>fossils of design intent</strong>: round_robin/supervisor-style orchestration was once envisioned and the schema was even laid down, but the focus shifted to “single agent plus sleeptime memory,” so the execution layer was never wired. Read them to see the direction, but don't treat them as usable features.</p>
<p>And “agent directly calls agent” (path one)? It's <strong>not in this table at all</strong> — it's not a group manager but a set of <strong>tools</strong>, covered in the next section.</p>
<p>So keep two layers in mind: <strong>group / ManagerType</strong> is “a config object for a flock of agents,” of which only the sleeptime kind is truly in use; while the <strong>send_message tools</strong> are “a hammer in an agent's hand” — anyone can pick one up to knock on another agent, with no relation to group at all.</p>
<div class="card analogy"><div class="tag">📝 Real-world analogy</div>
<p>Picture the team as a <strong>small shop</strong>, with a <strong>shared message board</strong> (the shared <span class="mono">Block</span>) hanging behind the counter.</p>
<p>The day-shift clerk (the foreground agent) serves customers all day, jotting a few scrawled notes on the board as they go.</p>
<p>Before closing, the night-shift tidier (the sleeptime agent) is woken to <strong>tidy the day's notes into the same board</strong> — erasing duplicates, filling in the key points.</p>
<p>When the day shift returns the next morning, it sees the <strong>tidied version</strong> and has no idea anyone came by overnight.</p>
<p>Clerks can also <strong>pass notes directly</strong> (<span class="mono">send_message_to_agent</span>): write a question to the next counter and wait for them to write back — that's path one.</p>
</div>
<details class="accordion"><summary>Why are the classic group managers “sleeping scaffolding”?</summary><div class="acc-body">
<p>Three hard pieces of evidence. First: the executor <span class="mono">groups/helpers.py::load_multi_agent</span> is <strong>never called</strong> on the live path — it can build the matching multi-agent object by <span class="mono">manager_type</span>, but nobody news it up.</p>
<p>Second: the <span class="mono">/v1/groups</span> routes are all marked <span class="mono">deprecated=True</span>, and there's simply <strong>no “send a message to a group” endpoint</strong> — you can CRUD a group row but can't make it run.</p>
<p>Third: the body of <span class="mono">SupervisorMultiAgent.step</span> is <strong>commented out entirely</strong>; calling it does nothing.</p>
<p>Conclusion: in v0.16.8, <span class="mono">round_robin / supervisor / dynamic</span> are merely <strong>schema plus enum plus class skeleton</strong> — seats saved for the future, not features usable today.</p>
</div></details>
<h2>Live path one: send_message_to_agent_* (agent calls agent directly)</h2>
<p>Path one isn't “scheduling” but a <strong>tool call</strong>. These tools are registered in <span class="mono">functions/function_sets/multi_agent.py</span>, typed <span class="mono">ToolType.LETTA_MULTI_AGENT_CORE</span>, and <strong>execute in the sandbox</strong> like any other tool.</p>
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
<p>Note the sender's identity is <strong>auto-injected</strong>: the message B receives is prefixed with <span class="mono">[Incoming message from agent with ID '...']</span>, so B knows “this came from another agent.”</p>
<p>Once B finishes, how does A “hear” the reply? The tool pulls B's assistant message out of <span class="mono">response.messages</span> and hands it back as this tool call's <strong>return value</strong> to A's loop — so from A's view, “asking another agent” is no different from “calling an ordinary tool and getting a string.”</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/multi_agent.py</span><span class="ln">send_message_to_agent_and_wait_for_reply: re-enter over REST, run B's loop (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">send_message_to_agent_and_wait_for_reply</span>(self, message: str, other_agent_id: str) -&gt; str:
    <span class="cm"># tool runs in the sandbox: build a client pointed at this server</span>
    client = <span class="fn">Letta</span>(base_url=self.base_url, token=self.token)
    <span class="cm"># post the message to B over REST -- runs B's own full loop, no group manager</span>
    response = client.agents.messages.<span class="fn">create</span>(
        agent_id=other_agent_id,
        messages=[{<span class="st">&quot;role&quot;</span>: <span class="st">&quot;system&quot;</span>, <span class="st">&quot;content&quot;</span>: message}],  <span class="cm"># auto-prefixed [Incoming message from agent ...]</span>
    )
    <span class="cm"># synchronous, blocking: pull out B's assistant reply, hand it back to caller A</span>
    <span class="kw">return</span> <span class="fn">extract_assistant_reply</span>(response.messages)
</pre></div>
<p>Why loop through REST rather than call B in-process? Because the tool runs in the <strong>sandbox</strong> (callback to Lesson 20), where all it can get is an ordinary client handle; so A calling B goes through <strong>the same public API</strong> as an external script calling B — isolation and auth treated identically.</p>
<p>This also explains why B runs its “own <strong>full</strong> loop”: when the server receives <span class="mono">messages.create(B)</span> it does the usual <span class="mono">AgentLoop.load(B).step</span> — B calls tools as needed, writes memory as needed — and A only gets its assistant reply back at the end.</p>
<details class="accordion"><summary>How do the three <span class="mono">send_message_to_agent_*</span> variants differ?</summary><div class="acc-body">
<p><strong>① <span class="mono">..._and_wait_for_reply(message, other_agent_id)</span></strong>: <strong>synchronous, blocking</strong>, two-way — send to one agent and <strong>wait</strong> for its reply before continuing. The most common.</p>
<p><strong>② <span class="mono">..._to_agents_matching_tags(message, match_all, match_some)</span></strong>: <strong>synchronous broadcast</strong> — filter a batch of agents by tags, then send to and wait for each <strong>one by one</strong>. One-to-many.</p>
<p><strong>③ <span class="mono">..._to_agent_async(message, other_agent_id)</span></strong>: <strong>asynchronous, one-way</strong> — fire and forget, no reply awaited; note it's <strong>disabled in production</strong>.</p>
<p>All three share one mechanism (build client → <span class="mono">messages.create</span> → run the other's loop); they differ only in <strong>whether they wait</strong> and <strong>one versus a batch</strong>.</p>
</div></details>
<p>The tag broadcast (<span class="mono">..._matching_tags</span>) deserves a note: it filters a batch of agents from the DB by <span class="mono">match_all / match_some</span>, then <strong>waits on each in turn</strong>. So it's essentially a “looped wait_for_reply,” not true parallel fan-out — one-to-many, but still synchronous and serial.</p>
<p>An engineering caution: <span class="mono">..._and_wait_for_reply</span> truly <strong>blocks</strong> A's step until B's whole turn finishes. If B then calls C and C calls D, the blocking <strong>stacks layer by layer</strong> — when designing agent collaboration, don't let the synchronous wait chain grow too long.</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">Don't confuse this path with sleeptime: <span class="mono">..._and_wait_for_reply</span> is <strong>synchronous and blocking</strong> — A stalls waiting for B to finish. Sleeptime below is exactly the opposite: a <strong>non-blocking</strong> background task. The two “multi-agent” modes have completely opposite blocking semantics.</span></div>
<h2>Live path two: sleeptime (a background agent quietly edits memory)</h2>
<p>Sleeptime is the only <strong>truly live</strong> “group” behavior in v0.16.8. The wiring point is <span class="mono">agents/agent_loop.py::AgentLoop.load</span>: when an agent is <span class="mono">letta_v1_agent / sleeptime_agent</span>, has <span class="mono">enable_sleeptime</span> on, and is attached to a group, it's handed to <span class="mono">SleeptimeMultiAgentV4</span>.</p>
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
        <span class="kw">if</span> count % self.group.sleeptime_agent_frequency != 0:
            <span class="kw">return</span>                                   <span class="cm"># not yet, skip</span>
        <span class="kw">for</span> agent_id <span class="kw">in</span> self.group.agent_ids:     <span class="cm"># the background editors</span>
            <span class="kw">await</span> self.<span class="fn">_issue_background_task</span>(agent_id, response_messages)  <span class="cm"># non-blocking safe_create_task</span>
</pre></div>
<p>Line by line: <span class="mono">bump_turns_counter_async</span> advances the counter as <span class="mono">(c+1) % frequency</span>; only an exact division (<span class="mono">% frequency == 0</span>) is a hit.</p>
<p>On a hit, for <strong>each background sleeptime agent</strong> in <span class="mono">group.agent_ids</span> it runs <span class="mono">_issue_background_task</span>: create a <span class="mono">Run</span>, then <span class="mono">safe_create_task(_participant_agent_step)</span> — a <strong>non-blocking asyncio background task</strong>. The foreground <strong>doesn't wait</strong>.</p>
<p>What does that background task do? <span class="mono">_participant_agent_step</span> stitches <span class="mono">prior + response_messages</span> into a transcript, wraps it in a <span class="mono">&lt;system-reminder&gt;</span> — “you are a background sleeptime agent, your job is memory management, update the relevant blocks with the memory tools” — then runs <span class="mono">step</span> as a <strong>full <span class="mono">LettaAgentV3</span></strong>.</p>
<p>Note what it feeds the background is <span class="mono">prior + response_messages</span> — namely the foreground's just-happened turn. The background agent doesn't tidy out of thin air but decides what to write into long-term memory blocks based on “what was just said.” It reads the conversation and edits the memory.</p>
<p>Don't miss this detail: <span class="mono">_issue_background_task</span> first creates a <span class="mono">Run</span> record, then <span class="mono">safe_create_task</span>. The <span class="mono">Run</span> makes this background tidying <strong>observable and traceable</strong> — not “fire a task and forget” but, like the foreground, leaving a queryable execution record.</p>
<p>That <span class="mono">&lt;system-reminder&gt;</span> matters too: it temporarily injects the sleeptime agent's <strong>identity and duty</strong> — “you are a background memory manager, update the relevant blocks with the memory tools.” The same loop, via this prompt plus <span class="mono">sleeptime_memory_persona</span>, is “switched” into a memory tidier.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>User → foreground step</h4><p>A user message arrives; <span class="mono">SleeptimeMultiAgentV4.step</span> first does <span class="mono">await super().step()</span> to run the foreground primary agent.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>bump_turns_counter</h4><p>The counter advances by <span class="mono">(c+1) % frequency</span>; ask: is <span class="mono">% frequency == 0</span>?</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Hit → non-blocking wake</h4><p>On a hit, <span class="mono">safe_create_task(_participant_agent_step)</span> for each background agent; the foreground doesn't wait and returns right away.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>sleeptime step → memory_rethink</h4><p>The background agent runs <span class="mono">step</span> as a full <span class="mono">LettaAgentV3</span>, rewriting memory with <span class="mono">memory_rethink</span>.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Write shared Block (version++)</h4><p>The new content lands in that one <span class="mono">Block</span> row; the optimistic-lock <span class="mono">version</span> increments.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Foreground reads it next turn</h4><p>On its next turn, rebuilding the system prompt, the foreground naturally reads the tidied new value.</p></div></div>
</div>
<details class="accordion"><summary>How often does sleeptime trigger? And why “on the very first turn”?</summary><div class="acc-body">
<p>Frequency is set by <span class="mono">group.sleeptime_agent_frequency</span>, default <strong>5</strong> (see <span class="mono">server.py::create_sleeptime_agent_async</span>).</p>
<p>The hit condition is <span class="mono">% frequency == 0</span> after <span class="mono">bump_turns_counter</span> advances.</p>
<p>The trick is the initial value: <span class="mono">GroupManager.create_group_async</span> sets <span class="mono">turns_counter</span> to <strong><span class="mono">-1</span></strong> for sleeptime. On the first turn <span class="mono">(-1+1)=0</span>, and <span class="mono">0 % 5 == 0</span> → <strong>a hit on the very first turn</strong>.</p>
<p>So a newly created sleeptime agent needn't idle for 5 turns; the background starts tidying memory right after the first conversation turn.</p>
</div></details>
<p>The name “sleeptime” is deliberate: it echoes the brain's “memory consolidation” during sleep — tidying the day's short-term experiences into long-term memory. Letta turns this metaphor into engineering: foreground conversation is like “being awake,” background tidying like “sleep,” the two staggered so neither preempts the other.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Remember this causal chain: <strong>sleeptime = the same <span class="mono">LettaAgentV3</span> loop plus one shared memory row plus one turn counter</strong>. There's no “special memory-tidying subsystem” — just an ordinary agent dropped into a transcript, given memory tools, and told “your job is to tidy memory.”</span></div>
<div class="card detail"><div class="tag">🔬 Down in the code</div>
<p><span class="mono">functions/function_sets/multi_agent.py</span> — the three <span class="mono">send_message_to_agent_*</span> tools, <span class="mono">LETTA_MULTI_AGENT_CORE</span>, sandbox-executed.</p>
<p><span class="mono">groups/sleeptime_multi_agent_v4.py::SleeptimeMultiAgentV4</span> — subclasses <span class="mono">LettaAgentV3</span>; <span class="mono">step</span> does <span class="mono">super().step()</span> then <span class="mono">run_sleeptime_agents</span>.</p>
<p><span class="mono">orm/blocks_agents.py::BlocksAgents</span> — composite PK <span class="mono">(agent_id, block_id, block_label)</span>, attaching one <span class="mono">Block</span> row to many agents.</p>
<p><span class="mono">services/tool_executor/core_tool_executor.py::CoreToolExecutor.memory_rethink</span> — where sleeptime's memory edit lands.</p>
</div>
<h2>The only coordination primitive: one shared Block row</h2>
<p>How do two agents “confer”? The answer is surprisingly plain: they <strong>point at the same <span class="mono">Block</span> row</strong>. No message queue, no shared in-memory object — just the same record in the database.</p>
<p>What attaches one Block row to many agents is the association table <span class="mono">orm/blocks_agents.py::BlocksAgents</span>: composite PK <span class="mono">(agent_id, block_id, block_label)</span>. <span class="mono">Block.agents</span> ↔ <span class="mono">Agent.core_memory</span> are linked many-to-many via <span class="mono">secondary="blocks_agents"</span>.</p>
<p>The composite PK is the triple <span class="mono">(agent_id, block_id, block_label)</span>: the link is recorded by “which agent, which block row, attached as what label.” So one Block row can stably appear under some label in many agents' core memory — sharing the value while each knows which prompt section to compile it into.</p>
<p>Who wires them together? When <span class="mono">server.py::SyncServer.create_sleeptime_agent_async</span> builds the sleeptime agent, it passes <span class="mono">block_ids=[b.id for b in main_agent.memory.blocks]</span> — <strong>the same Block rows</strong>, not copies.</p>
<div class="cellgroup"><div class="cg-cap"><b>One Block row on many agents: <span class="mono">blocks_agents.py::BlocksAgents</span> composite PK</b></div><div class="cells"><span class="cell hl">agent_id</span><span class="sep">·</span><span class="cell hl">block_id</span><span class="sep">·</span><span class="cell hl">block_label</span><span class="sep">→</span><span class="cell">Block.version (optimistic lock)</span></div></div>
<p>Let's draw “two agents sharing one row” — note the middle <span class="mono">Block</span> row has only one <span class="mono">block_id</span>:</p>
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
<p>The write detail: sleeptime's edit ultimately lands in <span class="mono">block_manager.update_block_async</span> / <span class="mono">update_memory_if_changed_async</span> — changing only that one Block row's value. The foreground agent's <span class="mono">core_memory</span> points, via <span class="mono">blocks_agents</span>, at this very row, so it sees the update “automatically,” with no sync code at all.</p>
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
    <span class="kw">return</span> <span class="kw">None</span>                              <span class="cm"># memory_finish_edits likewise returns None to wrap up</span>
</pre></div>
<p>Three steps: refuse read-only blocks → <span class="mono">update_block_value(label, new_memory)</span> replaces the whole block → <span class="mono">update_memory_if_changed_async</span> writes the new value into that one shared Block. <span class="mono">memory_finish_edits</span> just does <span class="mono">return None</span> to wrap up.</p>
<p>While we're here, distinguish <span class="mono">voice_sleeptime</span>: it's a voice-scenario variant using a different tool set (including <span class="mono">finish_rethinking_memory</span>), not the same as standard sleeptime's <span class="mono">memory_finish_edits</span>. This lesson covers only standard sleeptime; when you hit the voice line, remember it has <strong>its own set</strong>.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">Common-mistake correction: standard sleeptime's “rethink memory” is <span class="mono">memory_rethink</span>, <strong>not</strong> <span class="mono">rethink_memory</span> (legacy) or <span class="mono">finish_rethinking_memory</span> (voice-only). When reading v0.16.8, lock onto those four in <span class="mono">BASE_SLEEPTIME_TOOLS</span>.</span></div>
<details class="accordion"><summary>Once sleeptime edits memory, <strong>when</strong> does the foreground see it?</summary><div class="acc-body">
<p>Not instantly. Sleeptime calls <span class="mono">memory_rethink</span> → <span class="mono">update_memory_if_changed_async</span> to write the new value into that one <span class="mono">Block</span> row, and that's all — it doesn't “notify” the foreground.</p>
<p>The foreground only reads the new value when, on its <strong>next turn rebuilding the system prompt</strong>, it recompiles this Block row into core memory (callback to Lessons 8 and 9: core memory is compiled fresh from blocks each turn).</p>
<p><span class="mono">Block</span> carries an optimistic-lock <span class="mono">version</span>: concurrent writes detect conflicts by version number, preventing the background and foreground from overwriting each other.</p>
<p>So what's “shared” is that row's current value, and the visibility boundary is “the next prompt rebuild,” not “an immediate push.”</p>
</div></details>
<p>This “share one row” coordination has the benefit of <strong>zero extra machinery</strong>: no message bus, no lock service — just reusing the Block plus optimistic lock you already learned. The cost is <strong>weak real-time</strong>: a peer's update takes effect only at “the next prompt rebuild,” unfit for scenarios needing millisecond-level sync.</p>
<!--ENMORE-->
""",
}
