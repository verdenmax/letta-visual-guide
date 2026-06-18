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
<!--ZHMORE-->
""",
    "en": r"""<p>stub</p>""",
}
