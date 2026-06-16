"""Part 3 lesson content (the memory system, the guide's centerpiece).

Bilingual lesson bodies as ``{"zh": html, "en": html}`` dicts, imported by
``registry.py``. Lessons 07-12 cover Letta's layered memory: the three tiers,
memory blocks, self-editing memory, archival + vector search, recall + history,
and context compaction. Markup conventions match part1.py / part2.py.
"""

LESSON_07 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 5 课讲过一道绕不开的墙：上下文窗口是有限的，装不下一个 agent 的全部历史与知识。第 6 课又讲过：agent 的状态被外化成一份可持久化的数据。这一课把两条线接上——看 Letta 具体怎么用一套<strong>分层记忆</strong>，把"装不下"变成"按需取回"。这套机制，正是 Letta 区别于"只会聊天的 LLM"的核心。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
答案是三层：<strong>core（核心）/ recall（回忆）/ archival（归档）</strong>。它们的区别其实只有两点——<strong>在不在上下文窗口里</strong>、以及<strong>怎么读怎么写</strong>。读完这一课，你会拿到第三部分的整张地图，知道 08–12 每课在深挖哪一层。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把记忆系统想象成一间办公室。</strong>core 是你面前的<strong>办公桌台面</strong>——抬眼就见、随手能改，但面积很小，只摆当下要用的几张纸。recall 是<strong>桌边的抽屉</strong>——最近用过的东西都收在里面，关上抽屉它还在，需要时拉开就能翻到。archival 是<strong>地下档案室</strong>——容量近乎无限、存着长期资料，但你得"按主题去检索"才找得到。三层越往外越大、越远，但都能按需取回；而你（agent）始终知道每层大概压着多少东西。记住这间办公室，你就能预判每条信息该落在哪一层。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：Letta 把记忆分成三层（core / recall / archival），区别只有两件事——在不在上下文窗口里、以及怎么读怎么写。</strong>core 始终在窗、agent 可自改；recall 与 archival 在窗外、靠工具检索捞回。窗口装不下整个世界，于是 Letta 用"分层 + 按需换页"绕开了第 5 课那道根本约束。这一课是第三部分的地图，08–12 各自深挖一层。记住这张地图，你就不会再纠结"这条信息到底存哪了"——它一定落在这三层之一，区别只是离窗口的远近。三层之外没有第四种可能，这种"穷尽"恰恰让心智模型变得简单。
</div>

<h2>三层总览：在窗 / 窗外</h2>
<p>先建立总图。三层按"在不在上下文窗口里"分成两组：<strong>core 始终在窗</strong>，<strong>recall 与 archival 在窗外</strong>。在窗的部分模型直接看得见；窗外的部分要靠工具"捞"回来。</p>

<p>这条"在窗 / 窗外"的分界，是本课所有结论的总开关。<strong>在窗</strong>意味着模型直接读得到、但要持续付 token；<strong>窗外</strong>意味着不占 token、却要一次工具调用才能取回。三层的全部差异，都从这一条分界派生出来。</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">在窗 · 可自改</span><span class="name">core memory 核心记忆</span></div>
    <div class="ld">persona / human 等块，永远在上下文里；agent 用 <span class="mono">core_memory_append / replace</span> 自己改。容量小，是稀缺资源。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">窗外 · 可检索</span><span class="name">recall memory 回忆记忆</span></div>
    <div class="ld">全部对话历史的存档，只有最近一段在窗内；用 <span class="mono">conversation_search</span> 按文本 + 语义捞回。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">窗外 · 向量搜</span><span class="name">archival memory 归档记忆</span></div>
    <div class="ld">长期知识库，容量近乎无限；<span class="mono">archival_memory_insert</span> 写、<span class="mono">archival_memory_search</span> 按相似度搜。</div></div>
</div>

<div class="note tip"><span class="ni">💡</span><span class="nx">记住一句话就够了：<strong>在窗的只有 core</strong>；recall 和 archival 都在窗外，靠工具按需取回。</span></div>

<h2>一眼看清：三层对照表</h2>
<p>把三层的关键属性并排放一张表，差异立刻清楚——在不在上下文、容量多大、怎么写、怎么读、对应 MemGPT 论文的哪一层。</p>

<table class="t">
  <tr><th>层</th><th>在上下文?</th><th>容量</th><th>怎么写</th><th>怎么读</th><th>MemGPT 术语</th></tr>
  <tr><td>core 核心</td><td>✅ 始终在窗</td><td>小（每块上限 10 万字符）</td><td class="mono">core_memory_append / replace</td><td>直接读（已在 system 里）</td><td>working context</td></tr>
  <tr><td>recall 回忆</td><td>⛔ 窗外（仅最近在窗）</td><td>全部对话历史</td><td>自动落库（每条消息）</td><td class="mono">conversation_search</td><td>recall storage</td></tr>
  <tr><td>archival 归档</td><td>⛔ 窗外</td><td>近乎无限</td><td class="mono">archival_memory_insert</td><td class="mono">archival_memory_search（向量）</td><td>archival storage</td></tr>
</table>

<div class="cute">
  <div class="row">
    <span class="emoji">🧠</span><span class="lab">core · 眼前</span>
    <span class="arrow">·</span>
    <span class="emoji">🗄️</span><span class="lab">recall · 历史</span>
    <span class="arrow">·</span>
    <span class="emoji">📦</span><span class="lab">archival · 长期</span>
  </div>
  <div class="cap">三层记忆 = 桌面 / 抽屉 / 档案室：越往外越大、越远，但都能按需取回</div>
</div>

<h2>逐层细看：三层各自的脾气</h2>
<p>总图记住了，再花三段把每层的"脾气"说清——它最该装什么、不该装什么。选错层是新手最常见的坑：该进 archival 的长文塞进了 core，或指望 recall 去存"该长期记住"的事实。</p>

<p><strong>core（核心）：精，不在多。</strong>它是唯一始终在窗的层，每个字都在反复占用 token 预算（第 5 课的账还得继续算）。所以 core 只该放"必须时刻在眼前"的事实：用户是谁、当前任务进行到哪、有哪些关键偏好与约束。它还有别层没有的本事——能被 agent <strong>自己改写</strong>（<span class="mono">core_memory_append / replace</span>），这正是第 9 课"自我编辑记忆"的主题。把 core 想成贴在显示器边上的便签：显眼、好改，但贴满了就什么都看不清。</p>

<p><strong>recall（回忆）：自动、全量、可搜。</strong>你不用手动往 recall 写——每条来往消息都会<strong>自动落库</strong>，由 <span class="mono">MessageManager</span> 持有。它存的是<strong>原始对话历史</strong>本身，只有最近一段还留在窗内，其余都在窗外候着。需要时用 <span class="mono">conversation_search</span> 按文本或语义把旧消息捞回——比如"上次聊到的那个报错"，哪怕隔了几百条也能找回来。recall 是"聊过就有"，不需要 agent 操心。</p>

<p><strong>archival（归档）：刻意、长期、按义检索。</strong>和 recall 的"自动"相反，archival 要 agent <strong>主动</strong>写入（<span class="mono">archival_memory_insert</span>），适合存"将来可能要用"的长期事实与知识，由 <span class="mono">PassageManager</span> 持有。它的读取不靠精确关键词，而靠<strong>向量相似度</strong>：你问"API 重构的那个决定"，也能捞回当初用完全不同措辞记下的那条。容量近乎无限，是 agent 的"长期资料库"。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">一个判断口诀：<strong>"现在就要看见的"放 core，"聊过的"自动进 recall，"将来想查的"主动写 archival。</strong></span></div>

<h2>模型怎么知道"窗外还有什么"</h2>
<p>这是本课最容易被忽略、却最关键的一点。窗外的东西模型看不见，那它凭什么知道"还有内容没翻"、又该去哪一层翻？答案是 Letta <strong>每轮都给它一张实时"库存清单"</strong>。这张单不是给人看的调试信息，而是<strong>写进 system、模型每轮真的会读到</strong>的一段文字。</p>

<div class="note info"><span class="ni">📌</span><span class="nx"><strong>模型每轮都先瞄一眼"库存单"。</strong><span class="mono">&lt;memory_metadata&gt;</span> 会告诉它：recall 里还压着 N 条、archival 里存了 M 条、有哪些 tag——于是它<strong>知道自己忘了什么、该去哪层翻</strong>。</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/prompts/prompt_generator.py</span><span class="ln">compile_memory_metadata_block 产出（示例）</span></div>
<pre><span class="cm"># 每轮拼进 system 的"库存清单"：只给计数与标签，不给内容本身</span>
&lt;memory_metadata&gt;
- AGENT_ID: agent-123
- CONVERSATION_ID: default
- System prompt last recompiled: 2024-01-15 09:00 AM PST
- 42 previous messages between you and the user are stored in recall memory
- 156 total memories you created are stored in archival memory (use tools to access them)
- Available archival memory tags: project_x, meeting_notes, research
&lt;/memory_metadata&gt;
</pre></div>

<p>这段文字由 <span class="mono">compile_memory_metadata_block</span>（<span class="mono">letta/prompts/prompt_generator.py</span>）生成，拼进 system 提示。注意它只给"计数和标签"这种<strong>元信息</strong>，不把内容本身塞进窗口——既让模型心里有数，又不浪费宝贵的 token。这一行之差，正是 MemGPT 省 token 的关键设计之一。</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">元信息不是内容本身：库存单只说"recall 里有 42 条"，要看<strong>具体内容</strong>，仍得调用 <span class="mono">conversation_search</span> 把它们捞回窗内。</span></div>

<p>打个比方，这很像操作系统的"缺页中断"：程序访问的页不在内存里，硬件不会假装它不存在，而是发个信号去磁盘把它调进来。库存单就是给模型的那个"信号源"——它一眼看到"窗外还压着 156 条归档"，才会动念去 <span class="mono">archival_memory_search</span> 翻一翻。没有这张单，模型会误以为自己只知道窗里这点东西。</p>

<p>所以库存单的设计哲学很克制：<strong>只给导航、不给货物</strong>。它告诉模型"哪儿有、有多少、什么类别"，但绝不把内容本身搬进窗口。导航信息几乎不花 token，却足以让模型做出"要不要翻、翻哪层"的决定——用最小的代价，换最大的"自我感知"。</p>

<h2>三组记忆工具：改 core、搜 recall、写搜 archival</h2>
<p>三层各配一组工具，名字直接说明用途。改 core 用 <span class="mono">core_memory_append / replace</span>；搜 recall 用 <span class="mono">conversation_search</span>；写 / 搜 archival 用 <span class="mono">archival_memory_insert / search</span>。工具名几乎就是说明书——动词 + 层名，看一眼就知道它动的是哪一层。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/base.py</span><span class="ln">三组记忆工具签名（简化）</span></div>
<pre><span class="cm"># core：agent 自己改"眼前"的核心记忆（实现在 core_tool_executor.py）</span>
<span class="fn">core_memory_append</span>(label, content)                  <span class="cm"># 往某个块追加一行</span>
<span class="fn">core_memory_replace</span>(label, old_content, new_content) <span class="cm"># 精确替换一段</span>

<span class="cm"># recall：搜"窗外"的对话历史（文本 + 语义混合检索）</span>
<span class="fn">conversation_search</span>(query, roles=<span class="kw">None</span>, limit=<span class="kw">None</span>)

<span class="cm"># archival：写 / 搜长期向量库（按相似度）</span>
<span class="fn">archival_memory_insert</span>(content, tags=<span class="kw">None</span>)
<span class="fn">archival_memory_search</span>(query, tags=<span class="kw">None</span>, top_k=<span class="kw">None</span>)
</pre></div>

<div class="cellgroup">
  <div class="cg-cap"><b>OS 存储层级搬进 agent</b>：越往外越大、越慢，但都能按需调度</div>
  <div class="cells">
    <span class="cell hl">RAM · 眼前可改 → core</span>
    <span class="sep">·</span>
    <span class="cell q">磁盘日志 · 可检索 → recall</span>
    <span class="sep">·</span>
    <span class="cell scale">长期向量库 · 相似度捞 → archival</span>
  </div>
</div>

<p>把它和操作系统对照，三层正好是一套<strong>存储层级</strong>：core≈RAM、recall≈磁盘日志、archival≈长期向量库。越往外越大越慢，但都能按需调度。</p>

<p>这套分级不是为了好看，而是<strong>成本与速度的权衡</strong>：越靠近窗口的层，读得越快、但每个 token 都在烧钱；越往外的层，几乎不占 token、但每次取用都要一次检索的延迟。Letta 让 agent 自己在"快而贵"和"慢而省"之间按需调度——这正是记忆管理的全部艺术。</p>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>三层各有归宿。</strong>core memory 是 <span class="mono">Memory</span>（<span class="mono">letta/schemas/memory.py</span>）里一组 <span class="mono">Block</span>，<span class="mono">Memory.compile()</span> 把它们渲染进 system 提示；三组工具的实现在 <span class="mono">LettaCoreToolExecutor</span>（<span class="mono">letta/services/tool_executor/core_tool_executor.py</span>），声明在 <span class="mono">letta/functions/function_sets/base.py</span>。recall 是全部消息历史，由 <span class="mono">MessageManager</span>（<span class="mono">message_manager.py</span>）管；archival 是长期段落，由 <span class="mono">PassageManager</span>（<span class="mono">passage_manager.py</span>）管。那张"库存单"由 <span class="mono">PromptGenerator.compile_memory_metadata_block</span>（<span class="mono">prompt_generator.py</span>）生成。这一课只看"它们各是什么、谁来管"；每个 manager 的细节留给 08–12 逐一展开。你现在只需记住一件事：<strong>每一层都是一个独立的服务对象，各管各的存取</strong>。
</div>

<h2>core 怎么变成 system 里的文字</h2>
<p>core 始终"在窗"，靠的是每轮一步渲染：<span class="mono">Memory.compile()</span> 把各个 <span class="mono">Block</span> 拼成一段带标签的文本，连同那张库存单一起，塞进 system 提示的最前面。</p>

<div class="flow">
  <div class="node"><div class="nt">Block 们</div><div class="nd">persona / human …</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Memory.compile()</div><div class="nd">渲染成带标签文本</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">+ 库存单</div><div class="nd">&lt;memory_metadata&gt;</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">进 system</div><div class="nd">每轮现拼（第 3 课）</div></div>
</div>

<p>这把第 3 课"每步现拼上下文"和本课接上了：core 不是某个常驻变量，而是<strong>每轮由 <span class="mono">Memory.compile()</span> 现渲染</strong>进 system 的一段文字。所以你一旦改了 core，下一轮 system 就跟着变——这正是 agent 能"自我编辑记忆"的底座，第 9 课会专门拆。</p>

<h2>一次完整的"换页"：窗口快满了怎么办</h2>
<p>把这些拼起来看一次真实流程。当窗口快被填满（第 5 课的 token 预算），旧消息必须让位——但"让位"<strong>不等于</strong>"丢弃"。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>窗口快满</h4><p>新消息不断进来，token 预算见底（第 5 课）——旧消息必须让位。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>换出到 recall</h4><p>让位 ≠ 丢弃：旧消息留在 recall storage，仍可被检索。</p><span class="mono">message_manager.py</span></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>看库存单</h4><p><span class="mono">&lt;memory_metadata&gt;</span> 告诉模型 recall / archival 还压着多少、有哪些 tag。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>按需捞回</h4><p>需要旧信息时，用 <span class="mono">conversation_search</span> / <span class="mono">archival_memory_search</span> 把它捞回窗内。</p></div></div>
</div>

<p>整条链路的关键在于：换出去的东西<strong>从未真正消失</strong>，只是从"在窗"挪到了"窗外"。模型靠库存单知道它们还在，再用对应工具按需捞回。这就是 MemGPT 给 LLM 装的"虚拟内存"。</p>

<h2>谁来翻档案：是 agent 自己，不是框架</h2>
<p>还有个容易想当然的点：到底是<strong>谁</strong>决定去翻 recall 或 archival？不是 Letta 框架在背后偷偷检索，而是<strong>模型自己</strong>——它读到库存单、判断"我需要更早的信息"，于是<strong>主动发起一次工具调用</strong>。框架只负责把工具和库存单摆好。</p>

<p>这件事的份量在于：记忆调度成了 agent <strong>可学、可推理</strong>的行为，而不是写死的规则。该不该翻、翻哪一层、用什么查询词，都由模型当场决定。这也是为什么"自我编辑记忆"能成立——读和写，都是 agent 自己的动作。</p>

<p>顺带分清一个常见混淆：这和很多产品里的"自动 RAG"不一样。自动 RAG 是<strong>框架</strong>在每次提问前替你检索、把结果硬塞进提示；而 Letta 是 <strong>agent</strong> 自己判断要不要查、查什么。前者是被动注入，后者是主动调度——区别就在"谁在做决定"。当 agent 能把"查记忆"当成一个普通工具来用，它就能把检索和推理交织起来，而不是只在开头被动吃一口。</p>

<div class="note info"><span class="ni">👉</span><span class="nx">那如果换页也救不了、窗口实在装不下了呢？那就轮到<strong>上下文压缩</strong>登场——把旧消息总结成更短的摘要。这是第 12 课"记忆压力"的主题。</span></div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>这其实是把操作系统的存储层级搬进了 agent。</strong>core 像 <strong>RAM</strong>——永远在眼前、且 agent 能用 <span class="mono">core_memory_append / replace</span> 自己改写；recall 像<strong>磁盘上的对话日志</strong>——写下就不丢、可按文本 + 语义检索；archival 像<strong>长期向量库</strong>——容量近乎无限、按相似度捞。更妙的是：模型不是盲目地在黑暗里翻找。Letta 每轮都给它塞一张实时<strong>"库存清单"</strong>——<span class="mono">compile_memory_metadata_block</span> 产出的 <span class="mono">&lt;memory_metadata&gt;</span>：recall 里还压着 N 条、archival 里存了 M 条、有哪些 tag。于是模型<strong>知道自己忘了什么、该去哪一层翻</strong>——"换页"由 agent 自己发起，而不是框架替它决定。这正是 MemGPT 把虚拟内存的"分页"思想搬给 LLM 的精髓：有限的窗口当 RAM、无限的外存当磁盘，再给一张目录让它自己调度。把这套机制吃透，你会发现 Letta 的"记忆"不是玄学，而是一套你早就熟悉的<strong>分级缓存</strong>：热的放近处、冷的放远处，再加一张目录按需取用。
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>core 是最贵的那层，别什么都往里塞。</strong>核心记忆始终占着上下文窗口——它越大，留给对话和工具结果的 token 就越少（第 5 课的预算账）。每个块还有字符上限：默认 <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT = 100000</span>（<span class="mono">letta/constants.py</span>），这个上限会随记忆一起写进系统提示、提醒模型自觉别写超。正确姿势：core 只放"必须时刻在眼前"的精炼事实（用户是谁、当前任务、关键偏好）；其余统统交给 recall 与 archival，需要时再翻回来。<strong>把 core 当便签，不是当仓库。</strong>一个典型反模式：把整份 FAQ 灌进 persona 块——结果窗口被吃掉一大半、还可能撞上字符上限，而这种海量资料本就是 archival 的活。
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>MemGPT 论文的三层怎么映射？</summary><div class="acc-body">
<p><strong>示例：</strong>你读 MemGPT 论文时会看到 <span class="mono">main context</span> 与 <span class="mono">external context</span> 两个词，还有 FIFO queue、recall storage、archival storage。它们和 Letta 的三层是一一对应的——换句话说，Letta 是这篇论文相当忠实的一个工程实现。</p>
<p><strong>为什么这样设计：</strong>MemGPT 把 LLM 的有限窗口类比成操作系统的 RAM，把外部存储类比成磁盘，用"分页"在两者间搬运。main context（在窗）= system + core memory + 最近消息；external context（窗外）= recall storage + archival storage。</p>
<p><strong>源码在哪：</strong>core 对应 <span class="mono">Memory</span>（<span class="mono">letta/schemas/memory.py</span>）的 <span class="mono">Block</span>；recall 由 <span class="mono">MessageManager</span>（<span class="mono">letta/services/message_manager.py</span>）管；archival 由 <span class="mono">PassageManager</span>（<span class="mono">letta/services/passage_manager.py</span>）管。</p>
<p><strong>还有什么替代：</strong>不分层、只给一个超大窗口——成本与延迟随历史线性上涨，且仍有硬上限；或每次全量检索——慢且贵。分层 + 按需换页是工程上的折中。</p>
</div></details>

<details class="accordion"><summary>为什么要分三层，而不是一个大库？</summary><div class="acc-body">
<p><strong>示例：</strong>假设把所有记忆都塞进 core（在窗）。窗口几下就满了，每轮还要为这些 token 反复付费——哪怕这轮根本用不到它们。反过来，若全靠检索，连"用户叫什么"都要现查，那又慢又不稳。</p>
<p><strong>为什么这样设计：</strong>三层是按"访问频率 vs 成本"分的。core 最贵（占窗口）但最快（直接可见），只放高频必需；recall / archival 便宜（在窗外、不占 token）但要一次工具调用才能取到，放低频海量。各取所长。</p>
<p><strong>源码在哪：</strong>core 的字符上限 <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT</span> 在 <span class="mono">letta/constants.py</span>；recall / archival 的容量由数据库决定，分别走 <span class="mono">message_manager.py</span> / <span class="mono">passage_manager.py</span>。</p>
<p><strong>还有什么替代：</strong>单层全在窗——见上，贵且撞上限；单层全在外——每次都要检索，连"你是谁"都得现搜，慢且不稳。分层让"必须随时在眼前的"留在 core，其余外置。说到底，这和数据库给"热数据"配缓存、给"冷数据"留磁盘是同一个道理。</p>
</div></details>

<details class="accordion"><summary><span class="mono">&lt;memory_metadata&gt;</span> 到底告诉了模型什么？</summary><div class="acc-body">
<p><strong>示例：</strong>一段真实的库存单会写"42 previous messages … stored in recall memory"、"156 total memories … in archival memory"、"Available archival memory tags: project_x, research"。</p>
<p><strong>为什么这样设计：</strong>模型看不见窗外的内容，但需要知道"窗外有多少、有哪些类别"才能决定要不要去翻、用什么 tag 翻。给计数和标签（而非内容）既提供了"导航信息"，又几乎不花 token。</p>
<p><strong>源码在哪：</strong><span class="mono">PromptGenerator.compile_memory_metadata_block</span> 生成这段，再由 <span class="mono">get_system_message_from_compiled_memory</span> 与编译好的记忆一起拼进 system（都在 <span class="mono">letta/prompts/prompt_generator.py</span>）；在窗记忆的占位符常量 <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span> 在 <span class="mono">letta/constants.py</span>。</p>
<p><strong>还有什么替代：</strong>什么都不告诉模型——它就会"以为自己只知道窗里这些"，永远想不到去检索；或把内容也塞进去——直接把窗口撑爆，违背初衷。给"目录"而非"全文"，是这里的关键折中。</p>
</div></details>

<details class="accordion"><summary>core 的字符上限与取舍</summary><div class="acc-body">
<p><strong>示例：</strong>你想把整份产品文档塞进 persona 块好让 agent"随时记得"。一写就可能撞上每块的字符上限，或把窗口占掉一大块。</p>
<p><strong>为什么这样设计：</strong>core 始终在窗，是稀缺资源。默认上限 <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT = 100000</span>（<span class="mono">letta/constants.py</span>）给每个块封顶，逼你只放最关键的事实；海量资料应进 archival，用相似度按需捞。</p>
<p><strong>源码在哪：</strong>常量在 <span class="mono">letta/constants.py::CORE_MEMORY_BLOCK_CHAR_LIMIT</span>；写 core 的 <span class="mono">core_memory_append / replace</span> 在 <span class="mono">LettaCoreToolExecutor</span>（<span class="mono">core_tool_executor.py</span>），其中对 <span class="mono">read_only</span> 块会拒绝写入。</p>
<p><strong>还有什么替代：</strong>调大上限——治标，窗口还是会被占满、token 还是要付；或把长文放 archival、core 只留摘要与指针——这才是设计意图。</p>
</div></details>

<h2>第三部分由此展开：下一站</h2>
<p>这一课是第三部分的地图。把三层的"在窗 / 窗外、怎么读怎么写"记牢，后面五课就是逐层放大。你已经站在了整个记忆系统的入口。</p>
<p>第 8 课拆 core 的最小单位——记忆块 <span class="mono">Block</span>；第 9 课讲 agent 怎么用工具<strong>自我编辑</strong> core；第 10 课深入 archival 与<strong>向量检索</strong>；第 11 课讲 recall 与<strong>对话历史</strong>；第 12 课回到第 5 课那道墙，讲<strong>上下文压缩</strong>与"记忆压力"。带着这张三层地图往下读，每一课都只是其中一格的特写。</p>

<p>再快速回放一遍这张地图：<strong>core 在窗、可自改、最贵最快</strong>；<strong>recall 在窗外、自动全量、可检索</strong>；<strong>archival 在窗外、刻意长期、按相似度</strong>；而 <span class="mono">&lt;memory_metadata&gt;</span> 这张库存单，让模型随时知道窗外还压着什么、该去哪层翻。三层加一张单，就是 Letta 记忆系统的骨架。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>三层只看两件事</strong>：在不在上下文窗口里、怎么读怎么写。core 在窗、可自改；recall / archival 在窗外、靠工具检索。</li>
    <li><strong>core ≈ RAM</strong>：始终在窗、agent 用 <span class="mono">core_memory_append / replace</span> 自己改；有字符上限 <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT</span>，是稀缺资源。</li>
    <li><strong>recall ≈ 磁盘日志</strong>：全部对话历史，最近一段在窗，用 <span class="mono">conversation_search</span> 按文本 + 语义捞回。</li>
    <li><strong>archival ≈ 长期向量库</strong>：容量近乎无限，<span class="mono">archival_memory_insert</span> 写、<span class="mono">archival_memory_search</span> 按相似度搜。</li>
    <li><strong>库存清单</strong>：<span class="mono">compile_memory_metadata_block</span> 产出的 <span class="mono">&lt;memory_metadata&gt;</span> 告诉模型 recall / archival 各有多少、有哪些 tag——它由此知道自己忘了什么、该去哪层翻。</li>
    <li><strong>"换页"由 agent 自己发起</strong>：窗口快满 → 旧消息换出到 recall（不丢）→ 需要时按需捞回，正是 MemGPT 给 LLM 装的"虚拟内存"。</li>
    <li><strong>源码</strong>：<span class="mono">Memory</span>（schemas/memory.py）、三组工具（core_tool_executor.py + function_sets/base.py）、<span class="mono">compile_memory_metadata_block</span>（prompt_generator.py）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Lesson 5 raised a wall you can't go around: the context window is finite and can't hold an agent's entire history and knowledge. Lesson 6 showed that an agent's state is externalized into persistable data. This lesson joins the two threads — how Letta uses one <strong>layered memory</strong> to turn "won't fit" into "retrievable on demand." This mechanism is exactly what sets Letta apart from "an LLM that only chats."</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
The answer is three tiers: <strong>core / recall / archival</strong>. They really differ on only two things — <strong>whether they sit in the context window</strong>, and <strong>how you read and write them</strong>. By the end you'll hold the whole map of Part 3 and know which tier each of Lessons 08–12 drills into.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Picture the memory system as an office.</strong> core is the <strong>desktop in front of you</strong> — glance up and it's there, edit it by hand, but it's small and holds only the few sheets you need right now. recall is the <strong>desk drawer</strong> — recently used things are tucked inside; close the drawer and they're still there, pull it open to find them. archival is the <strong>basement archive</strong> — near-infinite capacity, long-term records, but you must "search by topic" to find anything. The tiers get bigger and farther out, yet all are retrievable on demand; and you (the agent) always know roughly how much each one holds.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>Grab this lesson in one line: Letta splits memory into three tiers (core / recall / archival), differing on just two things — whether they're in the context window, and how you read and write them.</strong> core is always in-window and the agent can edit it; recall and archival sit out of context and are pulled back by tools. The window can't hold the whole world, so Letta sidesteps Lesson 5's hard limit with "tiering + paging on demand." This lesson is the map of Part 3, with 08–12 each drilling one tier. Keep this map and you'll never agonize over "where did that fact go" — it lands in one of these three, differing only by distance from the window. There's no fourth option, and that exhaustiveness keeps the mental model simple.
</div>

<h2>Overview: in-window vs out-of-window</h2>
<p>Build the big picture first. The three tiers split into two groups by "are they in the context window": <strong>core is always in-window</strong>, while <strong>recall and archival sit out of window</strong>. The in-window part the model sees directly; the out-of-window part must be "fished" back with tools.</p>

<p>That "in vs out of window" line is the master switch for every conclusion here. <strong>In-window</strong> means the model reads it directly but keeps paying tokens; <strong>out-of-window</strong> means it costs no tokens but takes a tool call to retrieve. Every difference between the tiers derives from this one boundary.</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">in-window · self-editable</span><span class="name">core memory</span></div>
    <div class="ld">blocks like persona / human, always in context; the agent edits them with <span class="mono">core_memory_append / replace</span>. Small capacity — a scarce resource.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">out-of-window · searchable</span><span class="name">recall memory</span></div>
    <div class="ld">the archive of all conversation history; only the latest slice is in-window. Pull it back with <span class="mono">conversation_search</span> by text + meaning.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">out-of-window · vector search</span><span class="name">archival memory</span></div>
    <div class="ld">a long-term knowledge base, near-infinite capacity; <span class="mono">archival_memory_insert</span> writes, <span class="mono">archival_memory_search</span> retrieves by similarity.</div></div>
</div>

<div class="note tip"><span class="ni">💡</span><span class="nx">One line is enough: <strong>only core is in-window</strong>; recall and archival are both out of window, retrieved by tools on demand.</span></div>

<h2>At a glance: the three-tier table</h2>
<p>Put the key properties side by side and the differences pop — in context or not, how big, how to write, how to read, and which MemGPT-paper tier it maps to.</p>

<table class="t">
  <tr><th>Tier</th><th>In context?</th><th>Capacity</th><th>How to write</th><th>How to read</th><th>MemGPT term</th></tr>
  <tr><td>core</td><td>✅ always in-window</td><td>small (~100k chars per block)</td><td class="mono">core_memory_append / replace</td><td>read directly (already in system)</td><td>working context</td></tr>
  <tr><td>recall</td><td>⛔ out (only latest in-window)</td><td>all conversation history</td><td>auto-logged (every message)</td><td class="mono">conversation_search</td><td>recall storage</td></tr>
  <tr><td>archival</td><td>⛔ out of window</td><td>near-infinite</td><td class="mono">archival_memory_insert</td><td class="mono">archival_memory_search (vector)</td><td>archival storage</td></tr>
</table>

<div class="cute">
  <div class="row">
    <span class="emoji">🧠</span><span class="lab">core · now</span>
    <span class="arrow">·</span>
    <span class="emoji">🗄️</span><span class="lab">recall · history</span>
    <span class="arrow">·</span>
    <span class="emoji">📦</span><span class="lab">archival · long-term</span>
  </div>
  <div class="cap">Three tiers = desk / drawer / archive room: bigger and farther out, but all retrievable on demand</div>
</div>

<h2>The three tiers up close: each one's temperament</h2>
<p>With the big picture set, three short paragraphs nail each tier's "temperament" — what it should and shouldn't hold. Choosing the wrong tier is the classic beginner trap: a long doc that belongs in archival gets stuffed into core, or recall is expected to store a fact that should be remembered long-term.</p>

<p><strong>core: precise, not plentiful.</strong> It's the only tier always in-window, so every character keeps spending your token budget (Lesson 5's bill keeps running). Put only must-be-visible facts here: who the user is, where the current task stands, key preferences and constraints. It also has a power the others lack — the agent can <strong>rewrite it itself</strong> (<span class="mono">core_memory_append / replace</span>), the subject of Lesson 9. Think of core as a sticky note on your monitor: visible and easy to edit, but cover it and you can't read anything.</p>

<p><strong>recall: automatic, complete, searchable.</strong> You never write to recall by hand — every message is <strong>logged automatically</strong>, held by <span class="mono">MessageManager</span>. It stores the <strong>raw conversation history</strong> itself; only the latest slice stays in-window, the rest waits outside. Pull old messages back with <span class="mono">conversation_search</span> by text or meaning — say "that error we discussed last time" — even hundreds of messages back. recall is "say it and it's there," with no effort from the agent.</p>

<p><strong>archival: deliberate, long-term, retrieved by meaning.</strong> Unlike recall's automatic logging, archival requires the agent to <strong>write on purpose</strong> (<span class="mono">archival_memory_insert</span>), held by <span class="mono">PassageManager</span>. It suits long-term facts and knowledge you "might need later." Reads use <strong>vector similarity</strong>, not exact keywords: ask about "that API-redesign decision" and you'll recover the note even if it was worded completely differently. Capacity is effectively unlimited — the agent's long-term library.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">A rule of thumb: <strong>"needs to be visible now" goes in core, "things you talked about" land in recall automatically, "things you'll want to look up later" you write into archival on purpose.</strong></span></div>

<h2>How the agent knows "what's out there"</h2>
<p>Here's the most easily overlooked yet most crucial point. The model can't see out-of-window content, so how does it know "there's more it hasn't paged in" and which tier to look in? Letta <strong>hands it a live "inventory list" every turn</strong>. This list isn't debug info for humans — it's text <strong>written into the system prompt that the model actually reads</strong> each turn.</p>

<div class="note info"><span class="ni">📌</span><span class="nx"><strong>The model peeks at the "inventory" every turn.</strong> <span class="mono">&lt;memory_metadata&gt;</span> tells it: N messages still sit in recall, M memories in archival, and which tags exist — so it <strong>knows what it forgot and which tier to page</strong>.</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/prompts/prompt_generator.py</span><span class="ln">compile_memory_metadata_block output (example)</span></div>
<pre><span class="cm"># The "inventory" stitched into system each turn: counts and tags only, never the content itself</span>
&lt;memory_metadata&gt;
- AGENT_ID: agent-123
- CONVERSATION_ID: default
- System prompt last recompiled: 2024-01-15 09:00 AM PST
- 42 previous messages between you and the user are stored in recall memory
- 156 total memories you created are stored in archival memory (use tools to access them)
- Available archival memory tags: project_x, meeting_notes, research
&lt;/memory_metadata&gt;
</pre></div>

<p>This text is produced by <span class="mono">compile_memory_metadata_block</span> (<span class="mono">letta/prompts/prompt_generator.py</span>) and stitched into the system prompt. Note it gives only <strong>metadata</strong> — counts and tags — never the content itself, so the model is informed without wasting precious tokens. That one-line difference is one of MemGPT's key token-saving moves.</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">Metadata isn't the content: the inventory only says "42 in recall." To see the <strong>actual content</strong> the model still has to call <span class="mono">conversation_search</span> and pull it back into the window.</span></div>

<p>By analogy, this is much like an OS "page fault": the page a program accesses isn't in RAM, so rather than pretend it doesn't exist, the hardware signals to fetch it from disk. The inventory is that "signal source" for the model — seeing "156 archival items still outside," it gets the impulse to call <span class="mono">archival_memory_search</span>. Without the list, the model would assume it knows only what's in the window.</p>

<p>So the inventory's design philosophy is restrained: <strong>give navigation, not cargo</strong>. It tells the model "where, how much, what category," but never hauls the content into the window. Navigation info costs almost no tokens yet is enough for the model to decide "whether to page, and which tier" — the smallest cost for the biggest "self-awareness."</p>

<h2>Three tool families: edit core, search recall, write/search archival</h2>
<p>Each tier gets a tool family whose name states its job. Edit core with <span class="mono">core_memory_append / replace</span>; search recall with <span class="mono">conversation_search</span>; write/search archival with <span class="mono">archival_memory_insert / search</span>. The names are practically the manual — verb + tier — so a glance tells you which tier it touches.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/base.py</span><span class="ln">the three memory tool families (simplified)</span></div>
<pre><span class="cm"># core: the agent edits its own "in front of me" memory (implemented in core_tool_executor.py)</span>
<span class="fn">core_memory_append</span>(label, content)                  <span class="cm"># append a line to a block</span>
<span class="fn">core_memory_replace</span>(label, old_content, new_content) <span class="cm"># replace an exact span</span>

<span class="cm"># recall: search the out-of-window conversation history (hybrid text + semantic)</span>
<span class="fn">conversation_search</span>(query, roles=<span class="kw">None</span>, limit=<span class="kw">None</span>)

<span class="cm"># archival: write / search the long-term vector store (by similarity)</span>
<span class="fn">archival_memory_insert</span>(content, tags=<span class="kw">None</span>)
<span class="fn">archival_memory_search</span>(query, tags=<span class="kw">None</span>, top_k=<span class="kw">None</span>)
</pre></div>

<div class="cellgroup">
  <div class="cg-cap"><b>The OS storage hierarchy, moved into the agent</b>: bigger and slower farther out, but all schedulable on demand</div>
  <div class="cells">
    <span class="cell hl">RAM · editable, in front → core</span>
    <span class="sep">·</span>
    <span class="cell q">disk log · searchable → recall</span>
    <span class="sep">·</span>
    <span class="cell scale">long-term vector store · by similarity → archival</span>
  </div>
</div>

<p>Line it up against an operating system and the three tiers are exactly a <strong>storage hierarchy</strong>: core≈RAM, recall≈disk log, archival≈long-term vector store. Bigger and slower farther out, but all schedulable on demand.</p>

<p>This tiering isn't decoration — it's a <strong>cost-vs-speed trade-off</strong>: the closer to the window, the faster the read but the more every token burns; the farther out, the fewer tokens used but the more each retrieval costs in latency. Letta lets the agent schedule between "fast and pricey" and "slow and cheap" on demand — that's the whole art of memory management.</p>

<div class="card detail">
  <div class="tag">🔬 Down to the code</div>
  <strong>Each tier has a home.</strong> core memory is a set of <span class="mono">Block</span>s in <span class="mono">Memory</span> (<span class="mono">letta/schemas/memory.py</span>), rendered into the system prompt by <span class="mono">Memory.compile()</span>; the three tool families are implemented in <span class="mono">LettaCoreToolExecutor</span> (<span class="mono">letta/services/tool_executor/core_tool_executor.py</span>), declared in <span class="mono">letta/functions/function_sets/base.py</span>. recall is the full message history, managed by <span class="mono">MessageManager</span> (<span class="mono">message_manager.py</span>); archival is long-term passages, managed by <span class="mono">PassageManager</span> (<span class="mono">passage_manager.py</span>). That "inventory" is produced by <span class="mono">PromptGenerator.compile_memory_metadata_block</span> (<span class="mono">prompt_generator.py</span>). This lesson only covers "what each is and who manages it"; each manager's details are saved for 08–12. For now, remember one thing: <strong>each tier is a separate service object, each minding its own storage and retrieval</strong>.
</div>

<h2>How core becomes text in the system prompt</h2>
<p>core stays "in-window" through one rendering step each turn: <span class="mono">Memory.compile()</span> stitches the <span class="mono">Block</span>s into a tagged block of text and, together with that inventory, places it at the very front of the system prompt.</p>

<div class="flow">
  <div class="node"><div class="nt">the Blocks</div><div class="nd">persona / human …</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Memory.compile()</div><div class="nd">render to tagged text</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">+ inventory</div><div class="nd">&lt;memory_metadata&gt;</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">into system</div><div class="nd">re-assembled each turn (Lesson 3)</div></div>
</div>

<p>This connects Lesson 3's "re-assemble context every step" to this lesson: core isn't some resident variable but a span of text <strong>freshly rendered into system by <span class="mono">Memory.compile()</span> each turn</strong>. So the moment you edit core, the next turn's system changes too — the very foundation that lets an agent "self-edit memory," which Lesson 9 unpacks.</p>

<h2>One full "page-in": what to do when the window is almost full</h2>
<p>Put it together for one real flow. When the window is nearly full (Lesson 5's token budget), old messages must yield — but "yield" does <strong>not</strong> mean "discard." Letta's move isn't to delete, but to "relocate."</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>window almost full</h4><p>new messages keep arriving, the token budget bottoms out (Lesson 5) — old messages must yield.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>page out to recall</h4><p>yield ≠ discard: old messages stay in recall storage, still searchable.</p><span class="mono">message_manager.py</span></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>check the inventory</h4><p><span class="mono">&lt;memory_metadata&gt;</span> tells the model how much recall / archival still holds and which tags exist.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>page back on demand</h4><p>when old info is needed, use <span class="mono">conversation_search</span> / <span class="mono">archival_memory_search</span> to pull it back in.</p></div></div>
</div>

<p>The crux of the whole chain: what's paged out <strong>never truly disappears</strong> — it just moves from "in-window" to "out-of-window." The model knows it's still there from the inventory, then pulls it back with the matching tool on demand. This is the "virtual memory" MemGPT bolts onto an LLM.</p>

<h2>Who pages it in: the agent itself, not the framework</h2>
<p>One more thing people take for granted: who decides to search recall or archival? Not the Letta framework retrieving behind the scenes, but the <strong>model itself</strong> — it reads the inventory, judges "I need earlier info," and <strong>initiates a tool call</strong>. The framework only lays out the tools and the inventory.</p>

<p>The weight of this: memory scheduling becomes a <strong>learnable, reasoned</strong> behavior of the agent, not a hard-coded rule. Whether to page, which tier, what query — the model decides on the spot. That's why "self-editing memory" works at all — reading and writing are both the agent's own actions.</p>

<p>While we're here, clear up a common confusion: this isn't the "automatic RAG" many products ship. Automatic RAG has the <strong>framework</strong> retrieve before every question and stuff results into the prompt; Letta has the <strong>agent</strong> decide whether and what to query. The former is passive injection, the latter active scheduling — the difference is "who decides." Once the agent treats "search memory" as an ordinary tool, it can interleave retrieval with reasoning instead of taking one passive bite up front.</p>

<div class="note info"><span class="ni">👉</span><span class="nx">And if paging can't save you — the window simply won't fit it all? Then <strong>context compaction</strong> steps in, summarizing old messages into something shorter. That's the topic of Lesson 12, "memory pressure."</span></div>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  <strong>This is really the operating-system storage hierarchy moved into the agent.</strong> core is like <strong>RAM</strong> — always in front, and the agent can rewrite it with <span class="mono">core_memory_append / replace</span>; recall is like a <strong>conversation log on disk</strong> — written once, never lost, searchable by text + meaning; archival is like a <strong>long-term vector store</strong> — near-infinite, fetched by similarity. Better still: the model doesn't grope in the dark. Letta stuffs it a live <strong>"inventory list"</strong> every turn — the <span class="mono">&lt;memory_metadata&gt;</span> from <span class="mono">compile_memory_metadata_block</span>: N items still in recall, M in archival, and which tags. So the model <strong>knows what it forgot and which tier to page</strong> — "paging" is initiated by the agent, not decided for it by the framework. That's the essence of MemGPT porting virtual-memory "paging" to LLMs: the finite window as RAM, the infinite store as disk, plus a directory it schedules itself. Internalize this and Letta's "memory" stops being magic and becomes a <strong>tiered cache</strong> you already know: hot stuff near, cold stuff far, plus a directory to fetch on demand.
</div>

<div class="card warn">
  <div class="tag">⚠️ Common pitfall</div>
  <strong>core is the priciest tier — don't dump everything into it.</strong> Core memory always occupies the context window — the bigger it is, the fewer tokens are left for the conversation and tool results (Lesson 5's budget math). Each block also has a character cap: by default <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT = 100000</span> (<span class="mono">letta/constants.py</span>), and that cap is surfaced to the model in the system prompt so it keeps each block under it. The right posture: keep in core only the distilled facts that "must be visible at all times" (who the user is, the current task, key preferences); hand everything else to recall and archival, paging it back when needed. <strong>Treat core as a sticky note, not a warehouse.</strong> A classic anti-pattern: pouring a whole FAQ into the persona block — it eats the window and may hit the char cap, when that bulk is archival's job.
</div>

<h2>Go a little deeper</h2>

<details class="accordion"><summary>How do the MemGPT paper's three tiers map over?</summary><div class="acc-body">
<p><strong>Example:</strong> reading the MemGPT paper you'll see <span class="mono">main context</span> and <span class="mono">external context</span>, plus FIFO queue, recall storage, archival storage. They map one-to-one onto Letta's three tiers — in other words, Letta is a fairly faithful engineering implementation of that paper.</p>
<p><strong>Why this design:</strong> MemGPT likens the LLM's finite window to an OS's RAM and external storage to disk, paging between them. main context (in-window) = system + core memory + recent messages; external context (out-of-window) = recall storage + archival storage.</p>
<p><strong>Where in the source:</strong> core maps to <span class="mono">Block</span>s of <span class="mono">Memory</span> (<span class="mono">letta/schemas/memory.py</span>); recall is managed by <span class="mono">MessageManager</span> (<span class="mono">letta/services/message_manager.py</span>); archival by <span class="mono">PassageManager</span> (<span class="mono">letta/services/passage_manager.py</span>).</p>
<p><strong>Alternatives:</strong> no tiering, just one huge window — cost and latency rise linearly with history, and a hard cap remains; or full retrieval every time — slow and expensive. Tiering + paging on demand is the engineering compromise.</p>
</div></details>

<details class="accordion"><summary>Why three tiers instead of one big store?</summary><div class="acc-body">
<p><strong>Example:</strong> suppose you stuff all memory into core (in-window). The window fills in a few moves, and every turn you keep paying for those tokens — even when this turn doesn't use them. Conversely, if everything relies on retrieval, even "what's the user's name" must be fetched live — slow and unstable.</p>
<p><strong>Why this design:</strong> the tiers split by "access frequency vs cost." core is priciest (occupies the window) but fastest (directly visible), so keep only high-frequency essentials; recall / archival are cheap (out of window, no tokens) but need a tool call to fetch, so they hold the low-frequency masses. Best of both.</p>
<p><strong>Where in the source:</strong> core's char cap <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT</span> is in <span class="mono">letta/constants.py</span>; recall / archival capacity is database-bound, via <span class="mono">message_manager.py</span> / <span class="mono">passage_manager.py</span>.</p>
<p><strong>Alternatives:</strong> all-in-window — see above, pricey and cap-bound; all-out-of-window — retrieve every time, even "who you are" must be searched live, slow and shaky. Tiering keeps "must always be in front" in core and externalizes the rest. At bottom it's the same idea as a database caching "hot data" and leaving "cold data" on disk.</p>
</div></details>

<details class="accordion"><summary>What exactly does <span class="mono">&lt;memory_metadata&gt;</span> tell the model?</summary><div class="acc-body">
<p><strong>Example:</strong> a real inventory reads "42 previous messages … stored in recall memory," "156 total memories … in archival memory," "Available archival memory tags: project_x, research."</p>
<p><strong>Why this design:</strong> the model can't see out-of-window content but needs to know "how much is out there and what categories" to decide whether to look and which tags to use. Giving counts and tags (not content) provides "navigation info" at almost no token cost.</p>
<p><strong>Where in the source:</strong> <span class="mono">PromptGenerator.compile_memory_metadata_block</span> produces it, and <span class="mono">get_system_message_from_compiled_memory</span> stitches it into system alongside the compiled memory (both in <span class="mono">letta/prompts/prompt_generator.py</span>); the in-context memory placeholder constant <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span> is in <span class="mono">letta/constants.py</span>.</p>
<p><strong>Alternatives:</strong> tell the model nothing — it "thinks it knows only what's in the window" and never thinks to retrieve; or stuff the content in too — blowing up the window, defeating the purpose. Giving a "directory" not the "full text" is the key compromise here.</p>
</div></details>

<details class="accordion"><summary>core's character cap and its trade-offs</summary><div class="acc-body">
<p><strong>Example:</strong> you want to pour a whole product doc into the persona block so the agent "always remembers." Write it and you may hit each block's character cap, or eat a big chunk of the window.</p>
<p><strong>Why this design:</strong> core is always in-window, a scarce resource. The default cap <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT = 100000</span> (<span class="mono">letta/constants.py</span>) caps each block, forcing you to keep only the most critical facts; bulk material belongs in archival, fetched by similarity on demand.</p>
<p><strong>Where in the source:</strong> the constant is <span class="mono">letta/constants.py::CORE_MEMORY_BLOCK_CHAR_LIMIT</span>; the core writers <span class="mono">core_memory_append / replace</span> live in <span class="mono">LettaCoreToolExecutor</span> (<span class="mono">core_tool_executor.py</span>), which rejects writes to a <span class="mono">read_only</span> block.</p>
<p><strong>Alternatives:</strong> raise the cap — a band-aid, the window still fills and tokens still cost; or put long text in archival and keep only a summary and pointer in core — that's the intended design.</p>
</div></details>

<h2>Part 3 begins here: next stop</h2>
<p>This lesson is the map of Part 3. Lock in each tier's "in vs out of window, how to read and write," and the next five lessons just zoom into each. You're now standing at the entrance of the whole memory system.</p>
<p>Lesson 8 dissects core's smallest unit — the memory <span class="mono">Block</span>; Lesson 9 shows how the agent <strong>self-edits</strong> core with tools; Lesson 10 goes deep on archival and <strong>vector search</strong>; Lesson 11 covers recall and <strong>conversation history</strong>; Lesson 12 returns to Lesson 5's wall with <strong>context compaction</strong> and "memory pressure." Read on with this three-tier map and each lesson is just a close-up of one cell.</p>

<p>Quick replay of the map: <strong>core is in-context, self-editable, priciest and fastest</strong>; <strong>recall is out-of-context, automatic and complete, searchable</strong>; <strong>archival is out-of-context, deliberate and long-term, by similarity</strong>; and the <span class="mono">&lt;memory_metadata&gt;</span> inventory keeps the model aware of what's still outside and which tier to page. Three tiers plus one inventory — that's the skeleton of Letta's memory system.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Tiers differ on just two things</strong>: whether they're in the context window, and how you read/write them. core is in-window and self-editable; recall / archival are out-of-window, retrieved by tools.</li>
    <li><strong>core ≈ RAM</strong>: always in-window, the agent edits it with <span class="mono">core_memory_append / replace</span>; has a char cap <span class="mono">CORE_MEMORY_BLOCK_CHAR_LIMIT</span> — a scarce resource.</li>
    <li><strong>recall ≈ disk log</strong>: all conversation history, latest slice in-window, pulled back by <span class="mono">conversation_search</span> via text + meaning.</li>
    <li><strong>archival ≈ long-term vector store</strong>: near-infinite, <span class="mono">archival_memory_insert</span> writes, <span class="mono">archival_memory_search</span> retrieves by similarity.</li>
    <li><strong>The inventory list</strong>: the <span class="mono">&lt;memory_metadata&gt;</span> from <span class="mono">compile_memory_metadata_block</span> tells the model how much recall / archival hold and which tags — so it knows what it forgot and which tier to page.</li>
    <li><strong>"Paging" is agent-initiated</strong>: window almost full → old messages page out to recall (not lost) → paged back on demand — exactly the "virtual memory" MemGPT bolts onto an LLM.</li>
    <li><strong>Source:</strong> <span class="mono">Memory</span> (schemas/memory.py), the three tool families (core_tool_executor.py + function_sets/base.py), <span class="mono">compile_memory_metadata_block</span> (prompt_generator.py).</li>
  </ul>
</div>
""",
}

LESSON_08 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 7 课给了你三层地图：core 在窗、可自改。这一课把放大镜对准 core 的<strong>最小单位——记忆块 Block</strong>。你会发现 core memory 不是一团文字，而是一组<strong>有结构的卡片</strong>。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
一个 Block 只有四个核心字段：<span class="mono">label / value / limit / read_only</span>。就这四个字段，撑起了"可共享、可版本、可自我编辑"三件大事。读完你会明白第 9 课"自我编辑记忆"到底在改什么。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把 core memory 想成 agent 面前的一块白板。</strong>这块白板没被当成一整张随便写的纸，而是贴着几张<strong>分了区的便利贴</strong>：一张写"用户是谁"（<span class="mono">label: human</span>），一张写"我是谁"（<span class="mono">label: persona</span>）。每张便利贴都有抬头（label）、有内容（value）、有大小（limit，快写满了就提醒你别再塞）、还可能盖了"只读"章（read_only，agent 自己不能改）。要改记忆，就是<strong>撕下某一张便利贴重写</strong>——而不是把整块白板擦了重来。便利贴还能从一块白板挪到另一块、被两个人共看，甚至贴歪了能揭下来贴回原处——这正对应着本课后面的"共享"与"版本"。记住这块贴满分区便利贴的白板，本课所有结论都从它展开。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：core memory 是一组 Block，每个 Block 是带 <span class="mono">label / value / limit / read_only</span> 四个字段的卡片；<span class="mono">Memory</span> 是这些卡片的集合，<span class="mono">Memory.compile()</span> 把它们渲染成 system 里的 <span class="mono">&lt;memory_blocks&gt;</span> 文本。</strong>更妙的是，块还是<strong>一等实体</strong>：每张卡有自己的 <span class="mono">block-…</span> id，于是能被多个 agent 共享、能像 git 一样回滚。记住"卡片"这个词——记忆不是一团 blob，而是一叠有标签、有上限、有版本的卡。四个字段、三个性质（可寻址、可共享、可版本），就是本课的全部骨架，后面每一节都是给这副骨架添肉。
</div>

<h2>Block：core memory 的最小单位</h2>
<p>第 7 课说 core 是"一组 Block"。现在把这叠卡片拆开，看清楚一张。一个 Block 就是 LLM 上下文里被<strong>预留出来的一小段</strong>，对应 <span class="mono">letta/schemas/block.py</span> 的 <span class="mono">Block</span> 类。</p>

<p>它的字段少得惊人，真正要记的只有四个：<strong>label</strong>（这张卡叫什么）、<strong>value</strong>（卡上写了什么）、<strong>limit</strong>（最多能写多少字符）、<strong>read_only</strong>（agent 能不能改）。其余都是模板、项目、tag 之类的元数据。</p>

<p>这种"少字段、强语义"的设计是有意为之：字段越少，agent 越不容易在工具调用里填错；语义越清晰，模型越知道每个字段该写什么。Letta 把"好用"摆在了"功能全"前面。</p>

<div class="cellgroup">
  <div class="cg-cap"><b>一个 Block 的解剖</b>：四个字段，各管一件事</div>
  <div class="cells">
    <span class="cell hl">label · 标签</span>
    <span class="sep">·</span>
    <span class="cell">value · 内容</span>
    <span class="sep">·</span>
    <span class="cell q">limit · 字符上限</span>
    <span class="sep">·</span>
    <span class="cell scale">read_only · 只读?</span>
  </div>
</div>

<div class="cute"><div class="row"><span class="emoji">📝</span><span class="bubble">label: human · "名字叫 Timber"</span></div>
<div class="cap">一个 Block 就是一张贴在 agent 眼前的便利贴：有标签、有内容、有字数上限</div></div>

<p>有人会担心"字段这么少，够用吗？"——恰恰是这种克制让 Block 好理解、好操作。复杂度不堆在字段上，而是靠<strong>多张简单卡片的组合</strong>来表达，这和 Unix"小工具拼装"的哲学一脉相承。</p>

<div class="note tip"><span class="ni">💡</span><span class="nx">记住一句话：core memory 的"原子"是 <strong>Block</strong>，不是字符。你对记忆的一切操作——读、写、共享、回滚——都以<strong>一整张卡片</strong>为单位。</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/block.py</span><span class="ln">Block 的核心字段（简化）</span></div>
<pre><span class="cm"># 一个 Block = 上下文里被预留的一段；下面四个字段是重点</span>
<span class="kw">class</span> <span class="fn">Block</span>(BaseBlock):
    value: str                                  <span class="cm"># 卡上的内容（必填）</span>
    limit: int = CORE_MEMORY_BLOCK_CHAR_LIMIT   <span class="cm"># 字符上限，默认 10 万</span>
    label: Optional[str] = <span class="kw">None</span>             <span class="cm"># 标签：human / persona / …</span>
    read_only: bool = <span class="kw">False</span>                 <span class="cm"># 只读则 agent 不能改</span>
    id: str  <span class="cm"># block-… 前缀：可寻址、可被共享、可版本化</span>
</pre></div>

<p>注意最后那个 <span class="mono">id</span>：它带 <span class="mono">block-</span> 前缀（第 6 课讲过 prefixed id）。正因为每张卡片有自己<strong>稳定的 id</strong>，块才能成为"可寻址、可共享"的一等实体——这是本课后半段的伏笔。</p>

<h2>为什么把 core 切成一张张块</h2>
<p>你可能会问：既然 core 最后都渲染成一段文字，为什么不直接存一大段，非要切成块？答案和第 7 课"分层"是同一种思路——<strong>用结构换可控</strong>。</p>

<p>切成块，第一桩好处是<strong>可寻址</strong>。agent 想改"关于用户"的事，只需点名 <span class="mono">label="human"</span> 这一张卡，不会误伤"人设"那张。一大段文字做不到这种精准定位。</p>

<p>第二桩好处是<strong>可分别授权</strong>。系统规则那张卡可以单独设 <span class="mono">read_only</span>，而用户偏好那张照样让 agent 自由改。粒度落在卡片上，权限才能落在卡片上。</p>

<p>第三桩好处是<strong>可分别共享与回滚</strong>。一张"公司政策"卡能单独被整个团队共享、单独留版本历史，而不必牵动其他卡。块越独立，这些能力越自然。</p>

<div class="note tip"><span class="ni">💡</span><span class="nx">一句话：<strong>把记忆切成块，是为了让"寻址、授权、共享、回滚"都能精确到一张卡。</strong>一大段文字什么都混在一起，这些能力就无从谈起。</span></div>

<h2>三个字段，各管一件事</h2>
<p>把四个字段里最关键的三个再说细一点，因为第 9–12 课会反复用到它们。先说结论：<strong>label 是钥匙、value 是内容、limit 是预算。</strong></p>

<p><strong>label：卡片的抬头，也是工具寻址的钥匙。</strong>agent 改记忆时写 <span class="mono">core_memory_replace(label="human", …)</span>，靠的就是 label 找到那张卡。没有正确的 label，agent 根本不知道改哪张。</p>

<p><strong>value：真正进 system 的内容。</strong><span class="mono">Memory.compile()</span> 渲染时会把 value 原样放进 <span class="mono">&lt;value&gt;</span> 标签里——所以"改记忆"的本质，就是改某个 block 的 value。</p>

<p><strong>limit：这张卡的字符预算。</strong>它<strong>不会硬性拦你写超</strong>（很多人会想当然，下面"常见误区"专门讲），而是被写进系统提示，提醒模型"还剩多少额度"。</p>

<p>这三者最容易混的是 label 和 value：label 是<strong>卡的名字</strong>、相对固定，agent 一般不改它；value 是<strong>卡的内容</strong>、经常被改写。一句话——label 决定"这是哪张卡"，value 决定"卡上此刻写着什么"。</p>

<div class="note info"><span class="ni">📌</span><span class="nx">label 是工具的"门牌号"：<span class="mono">core_memory_append / replace</span> 的第一个参数就是 label——它把"改哪张卡"这件事，变成了一次普通的按名查找。</span></div>

<h2>Block 怎么变成 system 里的文字</h2>
<p>core 之所以"始终在窗"，靠的是每轮一次渲染。<span class="mono">Memory</span> 是 Block 的集合（<span class="mono">letta/schemas/memory.py</span> 的 <span class="mono">Memory</span> 类），<span class="mono">Memory.compile()</span> 把每张卡片拼成一段带标签的文本，塞进 system 的最前面。</p>

<div class="flow">
  <div class="node"><div class="nt">Block 们</div><div class="nd">human / persona …</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Memory.compile()</div><div class="nd">逐块渲染</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">&lt;memory_blocks&gt;</div><div class="nd">带标签文本</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">进 system</div><div class="nd">第 0 条消息</div></div>
</div>

<p>这条链路每轮都重走一遍——所以 core 看起来"一直在那儿"，其实是被反复<strong>现渲染</strong>出来的。块没变时渲染结果稳定（对 prefix cache 友好，见第 5 课）；块一变，渲染结果才跟着变，下一轮就生效。</p>

<p>渲染出来长什么样？下面是 <span class="mono">Memory.compile()</span> 产物的简化版——每张卡片变成一段 XML 风格的块，标签、元信息、内容都摆得清清楚楚。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/memory.py</span><span class="ln">Memory.compile() 产物（简化）</span></div>
<pre><span class="cm"># 每张 Block 渲染成一段；chars_current / chars_limit 把"额度"摆给模型看</span>
&lt;memory_blocks&gt;
&lt;human&gt;
&lt;description&gt; 关于用户的事实 &lt;/description&gt;
&lt;metadata&gt;
- chars_current=17
- chars_limit=5000
&lt;/metadata&gt;
&lt;value&gt;
名字叫 Timber，住在多伦多。
&lt;/value&gt;
&lt;/human&gt;
&lt;/memory_blocks&gt;
</pre></div>

<p>看到 <span class="mono">&lt;metadata&gt;</span> 里的 <span class="mono">chars_current / chars_limit</span> 了吗？这就是 limit 的真身：它不在写入时拦你，而是被<strong>渲染进提示</strong>、让模型自己心里有数。只读的块还会多一行 <span class="mono">read_only=true</span>。</p>

<p>多张块会按顺序一张张渲染，彼此之间用空行隔开，最后整体包在一对 <span class="mono">&lt;memory_blocks&gt;</span> 标签里。模型读到的，就是这样一份结构清晰、带元信息的"卡片清单"——而不是一堆混在一起的散文。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">这把第 3 课"每步现拼上下文"接上了：core 不是常驻变量，而是<strong>每轮由 <span class="mono">Memory.compile()</span> 现渲染</strong>进 system 的一段文字。块一变，下一轮 system 就跟着变——这正是第 9 课"自我编辑"的底座。</span></div>

<h2>Human 与 Persona：两个最常用的块</h2>
<p>大多数 agent 一开张就带两张卡：<strong>human</strong>（记关于用户的事）和 <strong>persona</strong>（记 agent 自己的人设）。它们是 Block 的两个子类——<span class="mono">letta/schemas/block.py</span> 里的 <span class="mono">Human</span> / <span class="mono">Persona</span>，只是把 label 预设成了 <span class="mono">"human"</span> / <span class="mono">"persona"</span>。</p>

<p>Letta 还给了一个顺手的构造器 <span class="mono">ChatMemory(persona=…, human=…)</span>，一行就建好这两张卡。它在 <span class="mono">letta/schemas/memory.py</span>，继承自 <span class="mono">BasicBlockMemory</span>。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/memory.py</span><span class="ln">ChatMemory 便捷构造</span></div>
<pre><span class="cm"># 一行建好 persona + human 两张卡（各是一个 Block）</span>
memory = <span class="fn">ChatMemory</span>(
    persona=<span class="st">"我是一个友好的助手，爱用 emoji。"</span>,
    human=<span class="st">"名字叫 Timber，住在多伦多。"</span>,
)
<span class="cm"># 等价于手动建 Block(label="persona") + Block(label="human")</span>
</pre></div>

<p>为什么偏偏是这两张？因为几乎每个对话 agent 都要回答两个问题：<strong>"我在跟谁说话"</strong>（human）和<strong>"我是谁、该用什么口吻"</strong>（persona）。把这两件最高频的事各给一张专卡，是经验沉淀出来的默认配置。</p>

<p>当然，你完全可以再加别的卡。很多生产 agent 会另开一张 <span class="mono">task_state</span> 记当前进度、一张 <span class="mono">scratchpad</span> 当草稿纸——human / persona 只是起点，不是上限。</p>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>每个角色都有归宿。</strong>一个 Block 是 <span class="mono">letta/schemas/block.py</span> 的 <span class="mono">Block</span>（基类 <span class="mono">BaseBlock</span>，子类 <span class="mono">Human</span> / <span class="mono">Persona</span>）。<span class="mono">Memory</span>（<span class="mono">letta/schemas/memory.py</span>）持有一组 Block，<span class="mono">Memory.compile()</span> 把它们渲染成 <span class="mono">&lt;memory_blocks&gt;</span>；写入改的是 <span class="mono">block.value</span>，走 <span class="mono">Memory.update_block_value</span>。增删改查由 <span class="mono">BlockManager</span>（<span class="mono">letta/services/block_manager.py</span>）负责；多 agent 共享靠 <span class="mono">blocks_agents</span> 关联表；版本历史由 <span class="mono">BlockHistory</span>（<span class="mono">letta/orm/block_history.py</span>）记录。三个常用 schema：<span class="mono">CreateBlock</span>（建）、<span class="mono">BlockUpdate</span>（改，注意是 <span class="mono">BlockUpdate</span> 不是 UpdateBlock）、<span class="mono">Block</span>（读）。这一课只看"它们各是什么、谁来管"；增删改查与共享、版本的完整调用，第 9 课与后续会逐一动手。
</div>

<h2>三件套：建 / 改 / 读</h2>
<p>日后用 SDK 或 REST 操作块时，你会反复打交道的就是这三个 schema。把它们并排放一张表，"哪个干哪件事"立刻清楚。</p>

<table class="t">
  <tr><th>动作</th><th>Schema</th><th>关键字段</th><th>说明</th></tr>
  <tr><td>建块</td><td class="mono">CreateBlock</td><td>label, value, limit</td><td>label 必填、value 必填，limit 默认 10 万</td></tr>
  <tr><td>改块</td><td class="mono">BlockUpdate</td><td>value?, limit?</td><td>字段都可选，只传想改的那个</td></tr>
  <tr><td>读块</td><td class="mono">Block</td><td>id, label, value, limit, read_only</td><td>带 <span class="mono">block-</span> 前缀 id，可寻址</td></tr>
</table>

<p>记住一个易错点：改块是 <span class="mono">BlockUpdate</span>，字段<strong>全可选</strong>，只传你要动的那个——其余保持不变。建块是 <span class="mono">CreateBlock</span>，label 与 value 必填。</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">改块时只传想动的字段：<span class="mono">BlockUpdate</span> 里没传的字段保持原值。<strong>别把"没传"误当成"清空"</strong>——真要清空，得显式传一个空字符串。</span></div>

<h2>块是可共享的实体</h2>
<p>现在揭开本课最有意思的性质。因为每张卡片有自己的 <span class="mono">block-</span> id，它就不只属于某一个 agent——<strong>多个 agent 可以挂同一张卡</strong>。</p>

<div class="cols">
  <div class="col">
    <h4>各自独立的块</h4>
    <p>agent A 有自己的 human 卡，agent B 有自己的 human 卡，互不相干。</p>
    <p class="mono" style="font-size:.82rem">A → block-aaa ；B → block-bbb</p>
  </div>
  <div class="col">
    <h4>共享同一张块</h4>
    <p>A 和 B 都挂到 <span class="mono">block-xyz</span>：一方改了，另一方下一轮就看见。</p>
    <p class="mono" style="font-size:.82rem">A → block-xyz ← B</p>
  </div>
</div>

<p>共享在数据库层面靠一张<strong>多对多关联表</strong>实现：<span class="mono">letta/orm/blocks_agents.py</span> 的 <span class="mono">BlocksAgents</span>，把 <span class="mono">block.id</span> 和 <span class="mono">agent.id</span> 连起来。于是"共享记忆"不需要任何额外魔法——它就是<strong>同一张卡挂到了两个 agent 上</strong>。</p>

<p>这里的关键是"引用"而非"复制"：两个 agent 指向的是数据库里<strong>同一行 block</strong>。所以不存在"把内容同步过去"这一步——它们本来就读同一张卡，自然永远一致。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">共享块 = 团队共用的一块白板。一个客服团队多个 agent 共享同一张"公司政策"卡，运营改一次，全员当轮同步——<strong>一处改、处处变</strong>。</span></div>

<p>共享也有要当心的地方：既然是同一张卡，一个 agent 写脏了，所有挂着它的 agent 都会读到脏内容。所以共享块更适合放"<strong>团队级、相对稳定</strong>"的事实，而不是某个 agent 的临时草稿。</p>

<h2>块还是可版本化的</h2>
<p>第二个高级性质：块有 <strong>git 式的历史</strong>。每次改动都能留下一个快照，可以回滚（undo）也可以重做（redo）。改错了不必慌。</p>

<p>快照存在 <span class="mono">letta/orm/block_history.py</span> 的 <span class="mono">BlockHistory</span> 表里，每条带一个<strong>单调递增的 <span class="mono">sequence_number</span></strong>。<span class="mono">BlockManager</span>（<span class="mono">letta/services/block_manager.py</span>）提供 <span class="mono">checkpoint_block_async</span>（存档）、<span class="mono">undo_checkpoint_block</span>（撤销）、<span class="mono">redo_checkpoint_block</span>（重做）。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>改动并存档</h4><p>每次改完 value 就 checkpoint，写一条 BlockHistory（seq=1,2,3…）。</p><span class="mono">checkpoint_block_async</span></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>撤销</h4><p>回到上一个 sequence_number 的快照，value 复原。</p><span class="mono">undo_checkpoint_block</span></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>重做</h4><p>撤销错了？再前进一个快照即可。</p><span class="mono">redo_checkpoint_block</span></div></div>
</div>

<p>为什么记忆需要版本？因为 agent 会<strong>自己改自己的记忆</strong>（第 9 课的主题），改错在所难免。给每次改动留快照，等于给"会自我编辑的记忆"配了一张安全网——错了能退回去，也能审计"这条记忆是哪一步、被谁改的"。</p>

<p>每条 <span class="mono">BlockHistory</span> 还记了"谁改的"（<span class="mono">actor_type / actor_id</span>）：是用户、是 agent、还是系统迁移。于是"这句话怎么进的记忆"也有据可查，调试与合规都用得上。</p>

<div class="note info"><span class="ni">📌</span><span class="nx">还有更强形态：<span class="mono">GitEnabledBlockManager</span>（<span class="mono">letta/services/block_manager_git.py</span>）把块的历史接进<strong>真正的 git 仓库</strong>，能取某次提交时的块内容。普通版本化用 <span class="mono">BlockHistory</span> 就够了。</span></div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>块是一等、可寻址、可共享、可回滚的实体。</strong>每张卡片有自己的 <span class="mono">block-</span> id（第 6 课的 prefixed id），于是两件以前需要"额外架构"的事变得理所当然。其一，两个 agent 挂同一张 block（靠 <span class="mono">blocks_agents</span> 关联表）= <strong>共享记忆</strong>，一处改、处处变；想象一支客服团队共用一张"公司政策"卡，改一次全员同步。其二，每次改动留一份 <span class="mono">BlockHistory</span> 快照（<span class="mono">sequence_number</span> 单调递增），于是记忆能像 git 一样 <strong>undo / redo</strong>，甚至接进真正的 git 仓库（<span class="mono">GitEnabledBlockManager</span>）。换句话说，记忆<strong>不是一团 blob</strong>，而是一组有标签、有上限、有版本、能被多方引用的卡片。把"卡片"这个心智模型立起来，你会发现 Letta 的记忆系统更像一个小型数据库：行有主键、能被引用、还自带审计日志——而不是一段随手 append 的纯文本。把它和第 6 课接上：状态被外化成数据之后，"记忆"这件事就能享受数据库的一切好处——主键、引用、历史。Block 正是这套思路落在 core memory 上的产物。看清这一层，Letta 的"记忆"就不再是黑盒，而是一组你能数得清、叫得出名、还能回放的卡片。
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>两件事最容易想当然，方向还正好相反。</strong>其一，<span class="mono">read_only</span> 的块 agent 真的<strong>改不动</strong>：<span class="mono">core_memory_append / core_memory_replace</span> 在动手前会先看 <span class="mono">block.read_only</span>，是 True 就直接抛错（<span class="mono">READ_ONLY_BLOCK_EDIT_ERROR</span>，见 <span class="mono">letta/services/tool_executor/core_tool_executor.py</span>）。所以"只读卡"是<strong>硬约束</strong>，不是建议。其二，<span class="mono">limit</span> 恰恰相反——它是<strong>软提示</strong>，不是硬墙。写入路径（<span class="mono">Memory.update_block_value</span>）只检查"值是不是字符串"，<strong>并不会因为超过 limit 就拒绝</strong>；limit 只是被渲染进 <span class="mono">&lt;metadata&gt;</span> 的 <span class="mono">chars_limit</span>，提醒模型自觉别写爆。别指望 limit 帮你硬性截断——那不是它的职责，要硬约束长度得在应用层自己做。记住这组对照：<strong>read_only 防的是"agent 乱改"，靠抛错硬挡；limit 管的是"别写太长"，靠提示软劝。</strong>把两者用反，要么挡不住、要么白等一场。
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>共享块怎么实现（<span class="mono">blocks_agents</span> 多对多）？</summary><div class="acc-body">
<p><strong>示例：</strong>一个客服团队有 5 个 agent，都要遵守同一份"退款政策"。与其在 5 张卡上各写一遍，不如建一张 <span class="mono">block-policy</span>，5 个 agent 全挂上去。</p>
<p><strong>怎么实现：</strong>靠 <span class="mono">letta/orm/blocks_agents.py</span> 的 <span class="mono">BlocksAgents</span> 关联表（表名 <span class="mono">blocks_agents</span>），把 <span class="mono">block.id</span> 与 <span class="mono">agent.id</span> 多对多连接。挂载即共享，无需复制内容。</p>
<p><strong>一处改、处处变：</strong>任一 agent（或管理员）改了这张卡的 value，其余 agent 下一轮 <span class="mono">Memory.compile()</span> 就读到新值——因为它们引用的是<strong>同一行</strong>。</p>
<p><strong>注意边界：</strong>共享的是<strong>同一张块</strong>，不是各自一份副本。所以谁都别假设"我改的只影响自己"——共享块上的每次改动，对所有挂着它的 agent 都即时可见。</p>
<p><strong>还有什么替代：</strong>给每个 agent 各复制一份——会漂移、难同步。共享同一张块从根上消除了不一致。</p>
</div></details>

<details class="accordion"><summary>块的版本历史与 undo / redo 怎么做？</summary><div class="acc-body">
<p><strong>示例：</strong>agent 把 human 卡里"住在多伦多"误改成"住在温哥华"。有了历史，一次 undo 就回去了。</p>
<p><strong>怎么实现：</strong>每次 checkpoint 往 <span class="mono">letta/orm/block_history.py</span> 的 <span class="mono">BlockHistory</span> 写一行快照，带单调递增的 <span class="mono">sequence_number</span>。<span class="mono">BlockManager</span> 的 <span class="mono">undo_checkpoint_block</span> / <span class="mono">redo_checkpoint_block</span> 就在序号间前后移动。</p>
<p><strong>更强形态：</strong><span class="mono">GitEnabledBlockManager</span>（<span class="mono">block_manager_git.py</span>）把历史接进真正的 git 仓库，可取某次提交时的块内容。</p>
<p><strong>和第 9 课的关系：</strong>正因为 agent 能自我编辑记忆，版本历史才格外有用——它是"会改自己的系统"的一颗后悔药。</p>
<p><strong>还有什么替代：</strong>不留历史——改错就回不去。审计与回滚，是把记忆当"数据"而非"草稿"的必备能力。</p>
</div></details>

<details class="accordion"><summary><span class="mono">limit</span> 与 <span class="mono">read_only</span> 的取舍</summary><div class="acc-body">
<p><strong>示例：</strong>你想保证某张"系统规则"卡 agent 绝不能自己改，于是设 <span class="mono">read_only=True</span>；又担心 persona 卡被写得太长，于是设一个 <span class="mono">limit</span>。</p>
<p><strong>read_only 是硬的：</strong><span class="mono">core_memory_append / replace</span> 改之前检查 read_only，是 True 就抛 <span class="mono">READ_ONLY_BLOCK_EDIT_ERROR</span>（<span class="mono">core_tool_executor.py</span>）。agent 真的改不动。</p>
<p><strong>limit 是软的：</strong>写入路径不因超限拒绝，只把 <span class="mono">chars_limit</span> 渲染进 metadata 提示模型。要硬性约束长度，得在应用层自己做。</p>
<p><strong>还有什么替代：</strong>把 limit 当硬墙用——会落空。理解"一个硬、一个软"，才不会用错工具。</p>
</div></details>

<details class="accordion"><summary><span class="mono">Human</span> / <span class="mono">Persona</span> 与自定义块</summary><div class="acc-body">
<p><strong>示例：</strong>除了 human / persona，你还能建任意 label 的块，比如 <span class="mono">task_state</span>（当前任务进度）、<span class="mono">preferences</span>（用户偏好）。</p>
<p><strong>怎么实现：</strong><span class="mono">Human</span> / <span class="mono">Persona</span> 只是把 label 预设成 <span class="mono">"human"</span> / <span class="mono">"persona"</span> 的 Block 子类（<span class="mono">block.py</span>）。自定义块就是 <span class="mono">Block(label="task_state", …)</span>，或用 <span class="mono">CreateBlock(label=…)</span> 建。</p>
<p><strong>为什么：</strong>把不同主题分到不同 label 的卡上，比塞进一张大卡更清晰，也便于<strong>分别共享、分别设 read_only</strong>。</p>
<p><strong>还有什么替代：</strong>所有东西塞进一张 persona——可读性差、没法分别授权与共享。分卡是更结构化的做法。</p>
</div></details>

<h2>把零件串起来：改一张卡会发生什么</h2>
<p>用一个最小流程把本课的零件串起来。假设 agent 学到"用户其实住在温哥华"，要更新 human 这张卡。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>按 label 找卡</h4><p>调 <span class="mono">core_memory_replace(label="human", …)</span>，靠 label 定位到那张卡。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>过 read_only 关</h4><p>工具先看这张卡是不是只读；不是，才继续往下。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>改的是 value</h4><p>把旧内容替换成新内容，新值写回 <span class="mono">Memory</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>重渲染进 system</h4><p>下一轮 <span class="mono">Memory.compile()</span> 把新 value 渲染进 <span class="mono">&lt;memory_blocks&gt;</span>。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>留一份快照</h4><p>若开了版本化，这次改动写一条 <span class="mono">BlockHistory</span>，改错可 undo。</p></div></div>
</div>

<p>看，本课每个零件都派上了用场：<strong>label 寻址、read_only 把关、value 承载内容、compile 渲染、history 留底</strong>。第 9 课会把第一步那只"手"——agent 怎么决定调用 <span class="mono">core_memory_replace</span>——讲到底。</p>

<h2>下一站：从"卡片"到"改卡片的手"</h2>
<p>这一课把 core memory 拆到了最小单位——<span class="mono">Block</span>。你现在知道一张卡有哪四个字段、怎么被渲染进 system、怎么被共享和回滚。第 7 课三层地图里 core 那一格，已经被你彻底拆开了。</p>

<p>第 9 课接着问最关键的一步：agent 到底怎么"<strong>自己改</strong>"这些卡片？答案藏在 <span class="mono">core_memory_append / replace</span> 改 <span class="mono">block.value</span>、再触发 system 重建的闭环里。记忆块是<strong>被改的对象</strong>，第 9 课讲的是那只<strong>改它的手</strong>。带着"卡片"这个模型往下读，自我编辑就不再神秘。</p>

<p>快速回放一遍这张"卡片清单"：一个 Block 有 <span class="mono">label / value / limit / read_only</span> 四个字段；<span class="mono">Memory</span> 收着一叠块，<span class="mono">compile()</span> 把它们渲染进 system；块可寻址、可共享（<span class="mono">blocks_agents</span>）、可回滚（<span class="mono">BlockHistory</span>）。四个字段、三个性质，就是 core memory 的全部骨架——把这副骨架记牢，第 9 到 12 课无非是把它逐个性质放大、各拍一张特写。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>Block 是 core 的最小单位</strong>：四个核心字段 <span class="mono">label / value / limit / read_only</span>（<span class="mono">letta/schemas/block.py</span>）。</li>
    <li><strong>Memory 是 Block 的集合</strong>：<span class="mono">Memory.compile()</span> 把每张卡渲染成 system 里的 <span class="mono">&lt;memory_blocks&gt;</span> 文本（<span class="mono">letta/schemas/memory.py</span>）。</li>
    <li><strong>改记忆 = 改 block 的 value</strong>，靠 label 寻址；<span class="mono">Human</span> / <span class="mono">Persona</span> 是预设 label 的子类，<span class="mono">ChatMemory</span> 一行建好两张卡。</li>
    <li><strong>三件套</strong>：<span class="mono">CreateBlock</span> 建、<span class="mono">BlockUpdate</span> 改（不是 UpdateBlock）、<span class="mono">Block</span> 读。</li>
    <li><strong>块可共享</strong>：靠 <span class="mono">blocks_agents</span> 多对多关联表，多个 agent 挂同一张 <span class="mono">block-…</span> = 共享记忆。</li>
    <li><strong>块可版本化</strong>：<span class="mono">BlockHistory</span>（<span class="mono">sequence_number</span>）+ <span class="mono">BlockManager</span> 的 checkpoint / undo / redo；<span class="mono">GitEnabledBlockManager</span> 接真 git。</li>
    <li><strong>两个坑</strong>：read_only 块 agent 改不动（<span class="mono">core_memory_*</span> 抛错，硬约束）；limit 是软提示（写进 metadata，不在写入路径硬拦）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Lesson 7 gave you the three-tier map: core is in-window and self-editable. This lesson zooms in on core's <strong>smallest unit — the memory Block</strong>. You'll find core memory isn't a blob of text, but a set of <strong>structured cards</strong>.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
A Block has just four core fields: <span class="mono">label / value / limit / read_only</span>. Those four fields carry three big ideas — shareable, versioned, self-editable. By the end you'll know exactly what Lesson 9's "self-editing memory" is editing.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Picture core memory as a whiteboard in front of the agent.</strong> It isn't one big sheet scribbled freely; it's covered with <strong>zoned sticky notes</strong>: one says "who the user is" (<span class="mono">label: human</span>), one says "who I am" (<span class="mono">label: persona</span>). Each note has a heading (label), content (value), a size (limit — when it's nearly full it nudges you to stop), and maybe a "read-only" stamp (read_only — the agent can't edit it). Editing memory means <strong>peeling off one note and rewriting it</strong> — not wiping the whole board. Notes can also move between boards, be read by two people, or be peeled off and re-stuck — exactly the "sharing" and "versioning" coming later. Keep this sticky-note whiteboard in mind; every conclusion flows from it.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>Grab this lesson in one line: core memory is a set of Blocks; each Block is a card with four fields — <span class="mono">label / value / limit / read_only</span>; <span class="mono">Memory</span> is the collection of those cards, and <span class="mono">Memory.compile()</span> renders them into the <span class="mono">&lt;memory_blocks&gt;</span> text of the system prompt.</strong> Better still, a block is a <strong>first-class entity</strong>: each card has its own <span class="mono">block-…</span> id, so it can be shared by multiple agents and rolled back like git. Remember the word "card" — memory isn't a blob, it's a stack of labeled, size-limited, versioned cards. Four fields, three properties (addressable, shareable, versioned) are the whole skeleton; every later section just adds flesh.
</div>

<h2>Block: core memory's smallest unit</h2>
<p>Lesson 7 said core is "a set of Blocks." Now let's split the stack and look at one card. A Block is just a <strong>reserved slice</strong> of the LLM's context — the <span class="mono">Block</span> class in <span class="mono">letta/schemas/block.py</span>.</p>

<p>It has surprisingly few fields; only four really matter: <strong>label</strong> (what the card is called), <strong>value</strong> (what's written on it), <strong>limit</strong> (max characters), <strong>read_only</strong> (can the agent edit it). The rest is template / project / tag metadata.</p>

<p>This "few fields, strong semantics" design is deliberate: fewer fields mean the agent is less likely to misfill a tool call; clearer semantics mean the model knows what each field is for. Letta puts <strong>"easy to use" ahead of "feature-complete."</strong></p>

<div class="cellgroup">
  <div class="cg-cap"><b>Anatomy of a Block</b>: four fields, each does one job</div>
  <div class="cells">
    <span class="cell hl">label · the tag</span>
    <span class="sep">·</span>
    <span class="cell">value · the content</span>
    <span class="sep">·</span>
    <span class="cell q">limit · char cap</span>
    <span class="sep">·</span>
    <span class="cell scale">read_only · locked?</span>
  </div>
</div>

<div class="cute"><div class="row"><span class="emoji">📝</span><span class="bubble">label: human · "name is Timber"</span></div>
<div class="cap">A Block is one sticky note in front of the agent: a tag, content, and a character cap</div></div>

<p>Some worry "so few fields — is that enough?" That restraint is exactly what makes a Block easy to grasp and operate. Complexity isn't piled onto fields; it's expressed by <strong>composing many simple cards</strong> — the same philosophy as Unix's "small tools, combined."</p>

<div class="note tip"><span class="ni">💡</span><span class="nx">Remember one line: core memory's "atom" is the <strong>Block</strong>, not the character. Every operation on memory — read, write, share, roll back — works on a <strong>whole card</strong>.</span></div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/block.py</span><span class="ln">Block's core fields (simplified)</span></div>
<pre><span class="cm"># A Block = a reserved slice of context; these four fields are the point</span>
<span class="kw">class</span> <span class="fn">Block</span>(BaseBlock):
    value: str                                  <span class="cm"># content on the card (required)</span>
    limit: int = CORE_MEMORY_BLOCK_CHAR_LIMIT   <span class="cm"># char cap, default 100k</span>
    label: Optional[str] = <span class="kw">None</span>             <span class="cm"># tag: human / persona / …</span>
    read_only: bool = <span class="kw">False</span>                 <span class="cm"># if true, the agent can't edit it</span>
    id: str  <span class="cm"># block-… prefix: addressable, shareable, versionable</span>
</pre></div>

<p>Note that last <span class="mono">id</span>: it carries a <span class="mono">block-</span> prefix (prefixed ids, Lesson 6). Because each card has its own <strong>stable id</strong>, a block becomes an addressable, shareable first-class entity — the setup for the second half of this lesson.</p>

<h2>Why slice core into separate blocks</h2>
<p>You might ask: since core ends up as one block of text anyway, why slice it into blocks instead of one big chunk? The answer echoes Lesson 7's "tiering" — <strong>trade structure for control</strong>.</p>

<p>First payoff: <strong>addressability</strong>. To edit "about the user," the agent just names <span class="mono">label="human"</span> — without touching the persona card. One big chunk can't pinpoint like that.</p>

<p>Second payoff: <strong>per-card permissions</strong>. The system-rules card can be <span class="mono">read_only</span> on its own, while the preferences card stays freely editable by the agent. Granularity on cards means permissions on cards.</p>

<p>Third payoff: <strong>per-card sharing and rollback</strong>. A "company policy" card can be shared with a whole team and keep its own version history, without disturbing other cards. The more independent the block, the more natural these abilities.</p>

<div class="note tip"><span class="ni">💡</span><span class="nx">One line: <strong>slicing memory into blocks lets "addressing, permissions, sharing, rollback" each target a single card.</strong> In one big chunk everything is tangled, and these abilities are impossible.</span></div>

<h2>Three fields, each does one job</h2>
<p>Let's detail the three most important of the four fields, since Lessons 9–12 use them constantly. The punchline: <strong>label is the key, value is the content, limit is the budget.</strong></p>

<p><strong>label: the card's heading, and the key tools address by.</strong> To edit memory the agent writes <span class="mono">core_memory_replace(label="human", …)</span> — label is how it finds the card. Without the right label, it can't tell which card to change.</p>

<p><strong>value: the content that actually enters the system.</strong> When <span class="mono">Memory.compile()</span> renders, it drops value verbatim into the <span class="mono">&lt;value&gt;</span> tag — so "editing memory" is essentially editing some block's value.</p>

<p><strong>limit: the card's character budget.</strong> It <strong>does not hard-stop</strong> you from overflowing (many assume it does — see "Pitfalls"); instead it's written into the system prompt to remind the model how much room is left.</p>

<p>The easiest pair to confuse is label vs value: label is the card's <strong>name</strong>, relatively fixed, rarely changed by the agent; value is the card's <strong>content</strong>, edited often. In short — label decides "which card this is," value decides "what's on it right now."</p>

<div class="note info"><span class="ni">📌</span><span class="nx">label is the tool's "house number": the first argument of <span class="mono">core_memory_append / replace</span> is label — it turns "which card to edit" into an ordinary lookup by name.</span></div>

<h2>How a Block becomes text in the system</h2>
<p>core is "always in-window" thanks to one render per turn. <span class="mono">Memory</span> is the collection of Blocks (the <span class="mono">Memory</span> class in <span class="mono">letta/schemas/memory.py</span>), and <span class="mono">Memory.compile()</span> stitches each card into a labeled block of text at the very front of the system prompt.</p>

<div class="flow">
  <div class="node"><div class="nt">Blocks</div><div class="nd">human / persona …</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Memory.compile()</div><div class="nd">render per block</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">&lt;memory_blocks&gt;</div><div class="nd">labeled text</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">into system</div><div class="nd">message #0</div></div>
</div>

<p>This chain reruns every turn — so core looks "always there," but it's actually <strong>re-rendered</strong> repeatedly. When blocks don't change, the render is stable (prefix-cache friendly, Lesson 5); only when a block changes does the render change, taking effect next turn.</p>

<p>What does it look like? Below is a simplified <span class="mono">Memory.compile()</span> output — each card becomes an XML-style block with label, metadata, and content laid out clearly.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/memory.py</span><span class="ln">Memory.compile() output (simplified)</span></div>
<pre><span class="cm"># each Block renders into one section; chars_current / chars_limit show the model its budget</span>
&lt;memory_blocks&gt;
&lt;human&gt;
&lt;description&gt; facts about the user &lt;/description&gt;
&lt;metadata&gt;
- chars_current=33
- chars_limit=5000
&lt;/metadata&gt;
&lt;value&gt;
Name is Timber, lives in Toronto.
&lt;/value&gt;
&lt;/human&gt;
&lt;/memory_blocks&gt;
</pre></div>

<p>See <span class="mono">chars_current / chars_limit</span> in <span class="mono">&lt;metadata&gt;</span>? That's the true face of limit: it doesn't block you on write, it's <strong>rendered into the prompt</strong> so the model is aware. A read-only block adds a <span class="mono">read_only=true</span> line.</p>

<p>Multiple blocks render one after another, separated by blank lines, all wrapped in a single pair of <span class="mono">&lt;memory_blocks&gt;</span> tags. What the model reads is exactly this clean, metadata-tagged <strong>card list</strong> — not a pile of tangled prose.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">This connects to Lesson 3's "assemble context every step": core isn't a resident variable, it's text <strong>re-rendered into system each turn</strong> by <span class="mono">Memory.compile()</span>. Change a block and the next turn's system follows — the foundation of Lesson 9's "self-editing."</span></div>

<h2>Human and Persona: the two most common blocks</h2>
<p>Most agents start with two cards: <strong>human</strong> (facts about the user) and <strong>persona</strong> (the agent's own persona). They're two Block subclasses — <span class="mono">Human</span> / <span class="mono">Persona</span> in <span class="mono">letta/schemas/block.py</span> — that simply preset label to <span class="mono">"human"</span> / <span class="mono">"persona"</span>.</p>

<p>Letta also gives a handy constructor, <span class="mono">ChatMemory(persona=…, human=…)</span>, building both cards in one line. It lives in <span class="mono">letta/schemas/memory.py</span> and extends <span class="mono">BasicBlockMemory</span>.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/memory.py</span><span class="ln">ChatMemory convenience constructor</span></div>
<pre><span class="cm"># build persona + human in one line (each is a Block)</span>
memory = <span class="fn">ChatMemory</span>(
    persona=<span class="st">"I'm a friendly assistant who loves emoji."</span>,
    human=<span class="st">"Name is Timber, lives in Toronto."</span>,
)
<span class="cm"># equivalent to Block(label="persona") + Block(label="human")</span>
</pre></div>

<p>Why these two? Because nearly every chat agent answers two questions: <strong>"who am I talking to"</strong> (human) and <strong>"who am I, in what tone"</strong> (persona). Giving each high-frequency concern its own card is a battle-tested default.</p>

<p>Of course you can add more cards. Many production agents open a <span class="mono">task_state</span> card for progress and a <span class="mono">scratchpad</span> for drafts — human / persona are a starting point, not a ceiling.</p>

<div class="card detail">
  <div class="tag">🔬 Down to the code</div>
  <strong>Every role has a home.</strong> A Block is the <span class="mono">Block</span> in <span class="mono">letta/schemas/block.py</span> (base <span class="mono">BaseBlock</span>, subclasses <span class="mono">Human</span> / <span class="mono">Persona</span>). <span class="mono">Memory</span> (<span class="mono">letta/schemas/memory.py</span>) holds a set of Blocks, and <span class="mono">Memory.compile()</span> renders them into <span class="mono">&lt;memory_blocks&gt;</span>; a write changes <span class="mono">block.value</span> via <span class="mono">Memory.update_block_value</span>. CRUD goes through <span class="mono">BlockManager</span> (<span class="mono">letta/services/block_manager.py</span>); multi-agent sharing uses the <span class="mono">blocks_agents</span> join table; version history is recorded by <span class="mono">BlockHistory</span> (<span class="mono">letta/orm/block_history.py</span>). Three common schemas: <span class="mono">CreateBlock</span> (create), <span class="mono">BlockUpdate</span> (update — note it's <span class="mono">BlockUpdate</span>, not UpdateBlock), <span class="mono">Block</span> (read). This lesson only covers "what they are and who manages them"; the full CRUD, sharing, and versioning calls are exercised in Lesson 9 onward.
</div>

<h2>The trio: create / update / read</h2>
<p>When you later operate on blocks via SDK or REST, these three schemas are what you keep dealing with. Put them side by side and "which does what" is instantly clear.</p>

<table class="t">
  <tr><th>Action</th><th>Schema</th><th>Key fields</th><th>Notes</th></tr>
  <tr><td>create</td><td class="mono">CreateBlock</td><td>label, value, limit</td><td>label &amp; value required; limit defaults to 100k</td></tr>
  <tr><td>update</td><td class="mono">BlockUpdate</td><td>value?, limit?</td><td>all fields optional; pass only what you change</td></tr>
  <tr><td>read</td><td class="mono">Block</td><td>id, label, value, limit, read_only</td><td><span class="mono">block-</span> prefixed id, addressable</td></tr>
</table>

<p>Remember an easy trap: updating is <span class="mono">BlockUpdate</span>, all fields <strong>optional</strong>, pass only the one you want to change — the rest stay put. Creating is <span class="mono">CreateBlock</span>, with label and value required.</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">When updating, pass only the fields you mean to change: any field omitted from <span class="mono">BlockUpdate</span> keeps its old value. <strong>Don't mistake "omitted" for "cleared"</strong> — to clear, explicitly pass an empty string.</span></div>

<h2>Blocks are shareable entities</h2>
<p>Now the most interesting property. Because each card has its own <span class="mono">block-</span> id, it doesn't belong to just one agent — <strong>multiple agents can attach the same card</strong>.</p>

<div class="cols">
  <div class="col">
    <h4>Separate blocks</h4>
    <p>agent A has its own human card, agent B has its own — unrelated.</p>
    <p class="mono" style="font-size:.82rem">A → block-aaa ; B → block-bbb</p>
  </div>
  <div class="col">
    <h4>Sharing one block</h4>
    <p>A and B both attach <span class="mono">block-xyz</span>: one edits, the other sees it next turn.</p>
    <p class="mono" style="font-size:.82rem">A → block-xyz ← B</p>
  </div>
</div>

<p>Sharing is implemented at the database layer by a <strong>many-to-many join table</strong>: <span class="mono">BlocksAgents</span> in <span class="mono">letta/orm/blocks_agents.py</span>, linking <span class="mono">block.id</span> and <span class="mono">agent.id</span>. So "shared memory" needs no extra magic — it's just <strong>the same card attached to two agents</strong>.</p>

<div class="note tip"><span class="ni">✅</span><span class="nx">A shared block = a whiteboard the team shares. Several agents in a support team share one "company policy" card; ops edits it once and everyone syncs that turn — <strong>change once, change everywhere</strong>.</span></div>

<p>Sharing has a catch too: since it's the same card, if one agent writes garbage, every agent attached to it reads that garbage. So shared blocks suit "<strong>team-level, relatively stable</strong>" facts, not one agent's scratch notes.</p>

<h2>Blocks are versioned too</h2>
<p>A second advanced property: blocks have <strong>git-style history</strong>. Every change can leave a snapshot you can undo and redo. A wrong edit isn't a disaster.</p>

<p>Snapshots live in the <span class="mono">BlockHistory</span> table (<span class="mono">letta/orm/block_history.py</span>), each with a <strong>monotonically increasing <span class="mono">sequence_number</span></strong>. <span class="mono">BlockManager</span> (<span class="mono">letta/services/block_manager.py</span>) offers <span class="mono">checkpoint_block_async</span> (save), <span class="mono">undo_checkpoint_block</span> (undo), <span class="mono">redo_checkpoint_block</span> (redo).</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>edit and checkpoint</h4><p>After each value change, checkpoint writes a BlockHistory row (seq=1,2,3…).</p><span class="mono">checkpoint_block_async</span></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>undo</h4><p>Step back to the previous sequence_number's snapshot; value is restored.</p><span class="mono">undo_checkpoint_block</span></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>redo</h4><p>Undid by mistake? Step forward one snapshot.</p><span class="mono">redo_checkpoint_block</span></div></div>
</div>

<p>Why version a memory? Because the agent <strong>edits its own memory</strong> (Lesson 9's topic), and mistakes happen. Snapshotting each change is a safety net for "memory that edits itself" — you can roll back, and audit "which step changed this, and who."</p>

<p>Each <span class="mono">BlockHistory</span> also records "who changed it" (<span class="mono">actor_type / actor_id</span>): the user, the agent, or a system migration. So "how did this sentence get into memory" is traceable — handy for debugging and compliance.</p>

<div class="note info"><span class="ni">📌</span><span class="nx">There's an even stronger form: <span class="mono">GitEnabledBlockManager</span> (<span class="mono">letta/services/block_manager_git.py</span>) wires block history into a <strong>real git repo</strong>, letting you fetch a block's content at a given commit. For ordinary versioning, <span class="mono">BlockHistory</span> is enough.</span></div>

<div class="card spark">
  <div class="tag">💡 The spark</div>
  <strong>A block is a first-class, addressable, shareable, rollbackable entity.</strong> Each card has its own <span class="mono">block-</span> id (the prefixed id of Lesson 6), which makes two things that used to need "extra architecture" feel obvious. First, two agents attaching the same block (via the <span class="mono">blocks_agents</span> join table) = <strong>shared memory</strong>, change once / change everywhere; picture a support team sharing one "company policy" card, edited once and synced for all. Second, every change leaves a <span class="mono">BlockHistory</span> snapshot (monotonic <span class="mono">sequence_number</span>), so memory can <strong>undo / redo</strong> like git, even wired into a real git repo (<span class="mono">GitEnabledBlockManager</span>). In other words, memory <strong>isn't a blob</strong>, it's a set of labeled, size-limited, versioned cards that multiple parties can reference. Stand the "card" model up and Letta's memory looks more like a small database — rows with primary keys, referencable, with an audit log — than a string you append to. Tie it back to Lesson 6: once state is externalized into data, "memory" enjoys all the perks of a database — keys, references, history. Block is that idea applied to core memory. See this layer clearly and Letta's "memory" stops being a black box and becomes a set of cards you can count, name, and replay.
</div>

<div class="card warn">
  <div class="tag">⚠️ Pitfalls</div>
  <strong>Two things are easy to assume — and they point in opposite directions.</strong> First, a <span class="mono">read_only</span> block really <strong>can't be edited</strong> by the agent: <span class="mono">core_memory_append / core_memory_replace</span> check <span class="mono">block.read_only</span> before acting, and on True they raise (<span class="mono">READ_ONLY_BLOCK_EDIT_ERROR</span>, see <span class="mono">letta/services/tool_executor/core_tool_executor.py</span>). So a "read-only card" is a <strong>hard constraint</strong>, not a suggestion. Second, <span class="mono">limit</span> is the opposite — a <strong>soft hint</strong>, not a hard wall. The write path (<span class="mono">Memory.update_block_value</span>) only checks "is the value a string," and <strong>won't reject for exceeding limit</strong>; limit is merely rendered into <span class="mono">&lt;metadata&gt;</span> as <span class="mono">chars_limit</span> to nudge the model. Don't count on limit to truncate for you — that's not its job; to hard-bound length, do it at the application layer. Remember the contrast: read_only guards against "the agent messing things up," enforced by raising; limit manages "don't write too long," nudged by a hint. Swap the two and you'll either fail to block or wait in vain.
</div>

<h2>Going deeper</h2>

<details class="accordion"><summary>How is block sharing implemented (<span class="mono">blocks_agents</span> many-to-many)?</summary><div class="acc-body">
<p><strong>Example:</strong> a support team has 5 agents, all bound by the same "refund policy." Rather than writing it on 5 cards, create one <span class="mono">block-policy</span> and attach all 5 agents.</p>
<p><strong>How:</strong> via the <span class="mono">BlocksAgents</span> join table in <span class="mono">letta/orm/blocks_agents.py</span> (table <span class="mono">blocks_agents</span>), linking <span class="mono">block.id</span> and <span class="mono">agent.id</span> many-to-many. Attaching is sharing — no content copy.</p>
<p><strong>Change once, change everywhere:</strong> any agent (or an admin) edits this card's value and the others read the new value on their next <span class="mono">Memory.compile()</span> — because they reference the <strong>same row</strong>.</p>
<p><strong>Boundary note:</strong> what's shared is <strong>one card</strong>, not per-agent copies. So nobody should assume "my edit only affects me" — every change on a shared block is instantly visible to all agents attached.</p>
<p><strong>Alternative:</strong> copy a card per agent — drifts, hard to sync. Sharing one block removes inconsistency at the root.</p>
</div></details>

<details class="accordion"><summary>How do block history and undo / redo work?</summary><div class="acc-body">
<p><strong>Example:</strong> the agent mis-edits the human card from "lives in Toronto" to "lives in Vancouver." With history, one undo reverts it.</p>
<p><strong>How:</strong> each checkpoint writes a snapshot row to <span class="mono">BlockHistory</span> (<span class="mono">letta/orm/block_history.py</span>) with a monotonic <span class="mono">sequence_number</span>. <span class="mono">BlockManager</span>'s <span class="mono">undo_checkpoint_block</span> / <span class="mono">redo_checkpoint_block</span> move backward and forward across the numbers.</p>
<p><strong>Tie to Lesson 9:</strong> precisely because the agent self-edits memory, history is so useful — it's the "undo button" for a system that rewrites itself.</p>
<p><strong>Stronger form:</strong> <span class="mono">GitEnabledBlockManager</span> (<span class="mono">block_manager_git.py</span>) wires history into a real git repo, fetching a block's content at a given commit.</p>
<p><strong>Alternative:</strong> keep no history — a wrong edit is unrecoverable. Audit and rollback are essential to treating memory as "data," not a "draft."</p>
</div></details>

<details class="accordion"><summary>The trade-offs of <span class="mono">limit</span> vs <span class="mono">read_only</span></summary><div class="acc-body">
<p><strong>Example:</strong> you want a "system rules" card the agent can never self-edit, so set <span class="mono">read_only=True</span>; and you worry the persona card grows too long, so set a <span class="mono">limit</span>.</p>
<p><strong>read_only is hard:</strong> <span class="mono">core_memory_append / replace</span> check read_only before editing and raise <span class="mono">READ_ONLY_BLOCK_EDIT_ERROR</span> on True (<span class="mono">core_tool_executor.py</span>). The agent truly can't edit it.</p>
<p><strong>limit is soft:</strong> the write path doesn't reject on overflow; it only renders <span class="mono">chars_limit</span> into metadata to nudge the model. To hard-bound length, do it at the application layer.</p>
<p><strong>Alternative:</strong> using limit as a hard wall — it won't hold. Understand "one hard, one soft" and you won't reach for the wrong tool.</p>
</div></details>

<details class="accordion"><summary><span class="mono">Human</span> / <span class="mono">Persona</span> and custom blocks</summary><div class="acc-body">
<p><strong>Example:</strong> beyond human / persona, you can create blocks with any label, e.g. <span class="mono">task_state</span> (current progress) or <span class="mono">preferences</span> (user prefs).</p>
<p><strong>How:</strong> <span class="mono">Human</span> / <span class="mono">Persona</span> are just Block subclasses that preset label to <span class="mono">"human"</span> / <span class="mono">"persona"</span> (<span class="mono">block.py</span>). A custom block is <span class="mono">Block(label="task_state", …)</span>, or created via <span class="mono">CreateBlock(label=…)</span>.</p>
<p><strong>Why:</strong> splitting topics across labeled cards is clearer than one big card, and lets you <strong>share and set read_only per card</strong>.</p>
<p><strong>Alternative:</strong> stuff everything into one persona — poor readability, no per-card authorization or sharing. Splitting into cards is the more structured approach.</p>
</div></details>

<h2>Pulling the parts together: what happens when you edit a card</h2>
<p>Let's wire the lesson's parts into one minimal flow. Say the agent learns "the user actually lives in Vancouver" and needs to update the human card.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>find the card by label</h4><p>Call <span class="mono">core_memory_replace(label="human", …)</span>, locating the card by label.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>pass the read_only gate</h4><p>The tool first checks whether this card is read-only; only if not does it continue.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>edit the value</h4><p>Replace old content with new; the new value is written back to <span class="mono">Memory</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>re-render into system</h4><p>Next turn <span class="mono">Memory.compile()</span> renders the new value into <span class="mono">&lt;memory_blocks&gt;</span>.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>leave a snapshot</h4><p>If versioning is on, the change writes a <span class="mono">BlockHistory</span> row; a wrong edit can be undone.</p></div></div>
</div>

<p>See — every part of this lesson pulls its weight: <strong>label addresses, read_only guards, value carries content, compile renders, history records</strong>. Lesson 9 takes step one — how the agent decides to call <span class="mono">core_memory_replace</span> — all the way down.</p>

<h2>Next stop: from "card" to "the hand that edits it"</h2>
<p>This lesson split core memory down to its smallest unit — the <span class="mono">Block</span>. You now know a card's four fields, how it's rendered into system, and how it's shared and rolled back. The core cell of Lesson 7's three-tier map is now fully unpacked.</p>

<p>Lesson 9 asks the crucial next step: how does the agent <strong>edit these cards itself</strong>? The answer lives in the loop where <span class="mono">core_memory_append / replace</span> change <span class="mono">block.value</span> and trigger a system rebuild. The memory block is the <strong>object being edited</strong>; Lesson 9 is about the <strong>hand that edits it</strong>. Read on with the "card" model and self-editing won't feel mysterious.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Block is core's smallest unit</strong>: four core fields <span class="mono">label / value / limit / read_only</span> (<span class="mono">letta/schemas/block.py</span>).</li>
    <li><strong>Memory is the collection of Blocks</strong>: <span class="mono">Memory.compile()</span> renders each card into the <span class="mono">&lt;memory_blocks&gt;</span> text in system (<span class="mono">letta/schemas/memory.py</span>).</li>
    <li><strong>Editing memory = editing a block's value</strong>, addressed by label; <span class="mono">Human</span> / <span class="mono">Persona</span> are label-preset subclasses, and <span class="mono">ChatMemory</span> builds both cards in one line.</li>
    <li><strong>The trio</strong>: <span class="mono">CreateBlock</span> create, <span class="mono">BlockUpdate</span> update (not UpdateBlock), <span class="mono">Block</span> read.</li>
    <li><strong>Blocks are shareable</strong>: via the <span class="mono">blocks_agents</span> many-to-many table, multiple agents attach the same <span class="mono">block-…</span> = shared memory.</li>
    <li><strong>Blocks are versioned</strong>: <span class="mono">BlockHistory</span> (<span class="mono">sequence_number</span>) + <span class="mono">BlockManager</span>'s checkpoint / undo / redo; <span class="mono">GitEnabledBlockManager</span> wires real git.</li>
    <li><strong>Two pitfalls</strong>: a read_only block can't be edited by the agent (<span class="mono">core_memory_*</span> raise — hard constraint); limit is a soft hint (rendered into metadata, not enforced on the write path).</li>
  </ul>
</div>
""",
}


LESSON_09 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 7 课给了你三层地图，其中点了一句：core memory 是<strong>唯一能被 agent 自己改写</strong>的那一层。第 8 课又拆开了 core 的最小单位——带 <span class="mono">label / value / limit / read_only</span> 四个字段的<strong>记忆块 Block</strong>。这一课把那句"自我编辑记忆"讲到机制底。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
答案会让你有点意外：agent "记住一件事"，本质是<strong>改写自己的系统提示</strong>。改一个块 → 持久化 → 重新编译 → <strong>原地重写第 0 条 system 消息</strong>。读完你会明白，core memory 根本不是"存在别处的记忆"，它<strong>就是 system 提示的一部分</strong>。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把 core memory 想成一张贴在 agent 额头上的"人设卡"。</strong>这张卡写着"你是谁、用户是谁、现在在做什么"，而且 agent <strong>每开口前都会先读一遍</strong>。神奇的地方在于：agent 能拿起笔<strong>改这张卡</strong>——划掉旧的一行、补上新的一句。卡一改，从下一句话起，它读到的"自己"就变了，于是它的言行也跟着变。它不是"在某个数据库里记了一笔"，而是<strong>把自己的"出厂设定"重写了一遍</strong>。这就是本课要拆穿的核心魔术：记忆不在别处，记忆就贴在脸上、每轮都读。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：agent 调 <span class="mono">core_memory_append / replace</span> 改某个块的 <span class="mono">value</span> → 持久化 → 触发 <span class="mono">rebuild_system_prompt_async</span> <strong>原地重写第 0 条 system 消息</strong>。</strong>而 system 提示里有个写死的占位符 <span class="mono">{CORE_MEMORY}</span>，编译好的块就<strong>填进这个洞</strong>。所以"改记忆"和"改系统提示"在 Letta 里是<strong>同一件事</strong>。本课就沿着这条闭环走一遍：从一次工具调用，到第 0 条被换掉，再到为什么"正常步骤故意不重建"。
</div>

<h2>先记住一句话：core memory 就是 system 的一部分</h2>
<p>很多人以为 core memory 像 recall / archival 那样"存在某个表里、要时才取"。<strong>不是。</strong>core 始终在窗，是因为 <span class="mono">Memory.compile()</span> 把它编译进了<strong>持久化的第 0 条 system</strong>（第 7、8 课讲过）——那条 system 每轮都在窗内，只有它改了才重新编译。它<strong>本身就是 system 文本</strong>。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>关键一句：</strong>core memory 不是"存在别处的记忆"，它<strong>就是 system 提示的一部分</strong>。agent 改记忆 = 改自己每轮都会读到的"出厂设定"。</span></div>

<p>对比一下就清楚：recall 和 archival 是"窗外的库"，要靠工具调用才取得回；而 core <strong>不需要"取"</strong>——它就<strong>长在持久化的 system 里</strong>，模型每轮睁眼就看见、无需取回。正因为它"长在 system 上"，改它才等于改 system。</p>


<p>抓住这一点，本课后面全是推论：既然 core 就是 system 文本，那"改记忆"就必然意味着"改 system 文本"；而 system 文本是<strong>持久化的第 0 条消息</strong>，于是改记忆最终会<strong>落到那一条消息上</strong>。下面把这条因果链一步步走清。</p>

<h2>自编辑闭环：从"想记住"到"下一轮就生效"</h2>
<p>先看全景。一次自我编辑要走六步——从用户说了点该记的事，到 agent 的"自我"在下一轮真正变样。把这六步记住，后面每一节都是给其中一步做特写。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>出现该记的事</h4><p>用户说"以后叫我老王"，或任务状态变了——agent 判断这值得写进 core。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>调用记忆工具</h4><p>agent 发起一次工具调用 <span class="mono">core_memory_replace(label, 旧, 新)</span>（或 append）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>改 block.value</h4><p>执行器先在内存里把块的 <span class="mono">value</span> 改掉（<span class="mono">update_block_value</span>）。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>持久化到库</h4><p><span class="mono">update_memory_if_changed_async</span> 把变更写进数据库（块表，last-write-wins）。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>重写第 0 条</h4><p><span class="mono">rebuild_system_prompt_async</span> 重新编译记忆，<strong>原地</strong>改掉第 0 条 system 消息。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>下一轮即生效</h4><p>下一轮一开头，模型读到的 system 已是新内容——agent "就是"新设定了。</p></div></div>
</div>

<p>注意第 6 步的"时差"：改动不是当场插进对话，而是<strong>沉淀进第 0 条</strong>，等下一轮拼上下文时一并被读到。所以自我编辑是"写给未来的自己"——这一轮动笔，下一轮起效。</p>

<p>举个具体的：human 块原本写着"用户在调研选型"。用户说"我们定了，下单 Letta"。agent 调 <span class="mono">core_memory_replace('human', '在调研选型', '已选定 Letta')</span>——块值被改、落库、第 0 条重编译。下一轮模型一读 system 就知道"项目已定"，不会再傻问"选得怎么样了"。</p>

<p>这条闭环里，第 4、5 步并不总会"真干活"：只有当编译出的记忆和当前 system <strong>确有差异</strong>时，才会落库并重写第 0 条。"改了等于没改"的调用会被悄悄短路——下一节看 <span class="mono">rebuild_system_prompt_async</span> 时会更清楚。</p>



<h2>core_memory_append / replace 改的是什么</h2>
<p>先看最贴近"动手"的一层：两个工具到底做了什么。它们的实现都在 <span class="mono">LettaCoreToolExecutor</span>（<span class="mono">letta/services/tool_executor/core_tool_executor.py</span>），短得超乎想象。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">core_memory_replace（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">core_memory_replace</span>(self, agent_state, actor, label, old_content, new_content):
    block = agent_state.memory.get_block(label)
    <span class="kw">if</span> block.read_only:                       <span class="cm"># 只读块：agent 不能改（第 8 课的硬约束）</span>
        <span class="kw">raise</span> ValueError(READ_ONLY_BLOCK_EDIT_ERROR)
    current = <span class="kw">str</span>(block.value)
    <span class="kw">if</span> old_content <span class="kw">not in</span> current:            <span class="cm"># old 必须精确出现，否则报错</span>
        <span class="kw">raise</span> ValueError(<span class="st">"Old content not found"</span>)
    new_value = current.replace(old_content, new_content)
    agent_state.memory.<span class="fn">update_block_value</span>(label=label, value=new_value)   <span class="cm"># ① 改内存里的块</span>
    <span class="kw">await</span> self.agent_manager.<span class="fn">update_memory_if_changed_async</span>(            <span class="cm"># ② 持久化 + 触发重建</span>
        agent_id=agent_state.id, new_memory=agent_state.memory, actor=actor)
    <span class="kw">return</span> new_value
</pre></div>

<p>三件事，按顺序：<strong>① 把关</strong>——只读块直接抛 <span class="mono">READ_ONLY_BLOCK_EDIT_ERROR</span>（第 8 课说的硬约束就在这一行）；<strong>② 改值</strong>——在内存对象里替换 <span class="mono">block.value</span>；<strong>③ 交棒</strong>——把"持久化 + 重建 system"这件大事交给 <span class="mono">update_memory_if_changed_async</span>。</p>

<div class="cols">
  <div class="col"><h4><span class="mono">core_memory_append</span></h4><p>往块尾<strong>追加一行</strong>：<span class="mono">current + "\n" + content</span>。适合"又多知道了一件事"，不动原有内容。</p></div>
  <div class="col"><h4><span class="mono">core_memory_replace</span></h4><p><strong>精确替换</strong>一段：<span class="mono">old</span> 必须存在且匹配。适合"事实变了，把旧的纠正成新的"。</p></div>
</div>

<div class="note info"><span class="ni">📌</span><span class="nx">两个工具<strong>第一步都查 <span class="mono">read_only</span></strong>：只读块（如团队共享的"政策"卡）会直接抛错，agent 改不动——这正是第 8 课"读写权限"在自编辑路径上的落地。</span></div>

<p>有意思的是实现<strong>短得离谱</strong>：真正的重活——持久化、判断要不要重建、原地换消息——全被推给了 <span class="mono">update_memory_if_changed_async</span>。工具本身只管"把块改对"，把"让改动生效"留给下游。这种<strong>关注点分离</strong>让两个工具既好读、又难写错。</p>

<p>还有个细节：工具<strong>返回改完后的新值</strong>（<span class="mono">return new_value</span>）。这个返回会作为工具结果回到对话里，等于让 agent <strong>当场确认</strong>"我刚把卡改成了这样"——它对自己的修改有即时反馈，而不是改完两眼一抹黑。</p>



<div class="cute">
  <div class="row">
    <span class="emoji">🤖</span><span class="arrow">✏️</span><span class="emoji">📋</span>
    <span class="bubble">"把'叫小李'改成'叫老王'"</span>
  </div>
  <div class="cap">自我编辑记忆 = agent 拿起笔，改写自己每轮都会读到的那张 system "人设卡"</div>
</div>

<h2>{CORE_MEMORY}：模板上预留的一个洞</h2>
<p>第 ② 步把球传给了"持久化 + 重建"。但在看重建之前，得先搞懂一件事：编译好的块<strong>到底拼到 system 的哪里</strong>？答案是一个写死的占位符 <span class="mono">{CORE_MEMORY}</span>。</p>

<div class="flow">
  <div class="node"><div class="nt">system 模板</div><div class="nd">含 <span class="mono">{CORE_MEMORY}</span> 洞</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Memory.compile()</div><div class="nd">块渲染成 &lt;memory_blocks&gt;</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">.replace 填洞</div><div class="nd">洞 → 真实记忆 + 库存单</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">完整 system#0</div><div class="nd">模型真正读到的</div></div>
</div>

<p>这个洞由 <span class="mono">get_system_message_from_compiled_memory</span>（<span class="mono">letta/prompts/prompt_generator.py</span>）来填。它把编译好的块、再加上第 7 课那张 <span class="mono">&lt;memory_metadata&gt;</span> 库存单，一起替换进占位符。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/prompts/prompt_generator.py</span><span class="ln">get_system_message_from_compiled_memory（简化）</span></div>
<pre><span class="cm"># 1) 编译好的块 + 库存单 拼成一大段在窗记忆</span>
full_memory_string = memory_with_sources + <span class="st">"\n\n"</span> + memory_metadata_string

<span class="cm"># 2) 占位符就是字符串 "{CORE_MEMORY}"（名字来自常量 IN_CONTEXT_MEMORY_KEYWORD）</span>
memory_variable_string = <span class="st">"{"</span> + IN_CONTEXT_MEMORY_KEYWORD + <span class="st">"}"</span>

<span class="cm"># 3) 把模板里的洞，替换成真实记忆 —— 这一步就是"记忆进 system"</span>
formatted_prompt = system_prompt.replace(memory_variable_string, full_memory_string)
<span class="kw">return</span> formatted_prompt
</pre></div>

<div class="note info"><span class="ni">📌</span><span class="nx"><span class="mono">{CORE_MEMORY}</span> 这个名字写死在常量 <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span>（<span class="mono">letta/constants.py</span>）。它是系统提示模板里唯一"受保护"的变量——你的自定义提示词只要留着这个洞，记忆就能被注进去。</span></div>

<p>万一你的自定义系统提示<strong>忘了写</strong>这个洞呢？别担心，注入函数有个兜底：发现模板里没有 <span class="mono">{CORE_MEMORY}</span>，就<strong>自动把它补到末尾</strong>（<span class="mono">append_icm_if_missing</span>），保证记忆无论如何都进得了 system。</p>


<p>所以"core 在窗"不是什么后台魔法，就是一次朴素的字符串替换：模板里挖个 <span class="mono">{CORE_MEMORY}</span>，每次重建时把当前的块填进去。理解了这个洞，你就理解了"记忆怎么变成模型读到的文字"。</p>

<p>填进洞里的也不只是块本身。<span class="mono">full_memory_string</span> = 编译后的 <span class="mono">&lt;memory_blocks&gt;</span> + 第 7 课那张 <span class="mono">&lt;memory_metadata&gt;</span> 库存单。前者是"眼前卡片的内容"，后者是"窗外还压着多少条"。两段拼在一起，模型既看见当下、又对窗外心里有数。</p>


<h2>原地重写第 0 条：rebuild_system_prompt_async</h2>
<p>现在看闭环里份量最重的一步。把"洞被填好的新 system 文本"真正<strong>写回那条消息</strong>的，是 <span class="mono">rebuild_system_prompt_async</span>（<span class="mono">letta/services/agent_manager.py</span>）。它的关键有两点：<strong>没变就不写</strong>、<strong>变了就原地换</strong>。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/agent_manager.py</span><span class="ln">rebuild_system_prompt_async（伪代码）</span></div>
<pre><span class="kw">async def</span> <span class="fn">rebuild_system_prompt_async</span>(agent_id, actor, force=<span class="kw">False</span>):
    curr = message_manager.get(message_ids[<span class="nb">0</span>])        <span class="cm"># 第 0 条 = system 消息</span>
    memory_str = agent_state.memory.<span class="fn">compile</span>(...)        <span class="cm"># 重新编译当前核心记忆</span>

    <span class="kw">if</span> memory_str <span class="kw">in</span> curr.content <span class="kw">and not</span> force:    <span class="cm"># 记忆没变 → 直接返回，不重建</span>
        <span class="kw">return</span>                                       <span class="cm">#   （这是 prefix cache 的护城河）</span>

    new_system = PromptGenerator.<span class="fn">get_system_message_from_compiled_memory</span>(
        system_prompt=agent_state.system, memory_with_sources=memory_str, ...)

    temp = Message(role=<span class="st">"system"</span>, content=new_system)
    temp.id = curr.id                            <span class="cm"># ★ 关键：沿用同一个 id</span>
    <span class="kw">await</span> message_manager.<span class="fn">update_message_by_id_async</span>(curr.id, ...)   <span class="cm"># 原地重写第 0 条</span>
</pre></div>

<p>两个设计决定值得停下来看。第一，<strong>没变就不写</strong>：先比对"新编译的记忆"是否已在当前 system 里，若在且非强制，直接返回——这一步省下大量无谓重建。第二，<strong>原地换</strong>：新消息<strong>沿用旧消息的 id</strong>（<span class="mono">temp.id = curr.id</span>），所以第 0 条还是那一条，只是内容被换了。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">重写时 <span class="mono">temp.id = curr.id</span>：第 0 条的<strong>身份没变</strong>，变的只是它的<strong>内容</strong>——同一个 id、原地更新，<strong>不是</strong>新插一条 system 消息。这让"历史只有一条 system"这件事始终成立。</span></div>

<p>"没变就不写"这条短路也别小看：它先比对"新编译的记忆是否已在当前 system 里"，是就直接返回。于是即便 agent 调了工具、内容其实没变（把"老王"又改成"老王"），也不会平白重写第 0 条、不会无谓打碎缓存。<strong>正确</strong>与<strong>省钱</strong>在这里恰好一致。</p>


<p>把这一步和第 6 课接上：agent 的状态是外化、持久的，而 system 提示就是 <span class="mono">message_ids[0]</span> 这一条持久消息。所以"改记忆"最终落在一条<strong>数据库里的消息</strong>上——既不丢、又能被下一次加载读回。</p>

<p>形象点说：第 0 条像一块门牌号固定的展示板。改记忆不是<strong>换一块新板</strong>（新 id），而是<strong>擦掉旧字、写上新字</strong>（同 id）。门牌没变，下一次加载走到老地方，读到的却是新内容。这也是为什么 agent 的"历史"里始终只有一条 system 消息。</p>

<p>落库这一步走的是<strong>"有变才写"</strong>：<span class="mono">update_memory_if_changed_async</span> 先比对编译结果，只有真变了才把块写进数据库（<span class="mono">update_block_async</span>，后写覆盖先写）。多个 agent 抢改同一张共享卡时，这就是一条朴素的 last-write-wins 规则。</p>



<h2>为什么"正常步骤故意不重建"——为了 prefix cache</h2>
<p>这里有个容易被忽略、却很关键的取舍。既然记忆这么重要，为什么不<strong>每一步</strong>都重建一遍 system、保证它绝对最新？因为那会<strong>砸掉 prefix cache</strong>（第 5 课）。</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">正常步骤</span><span class="tslot">第 1 轮·system#0 稳定</span><span class="tslot">第 2 轮·前缀不变 → 命中缓存</span><span class="tslot span">不动第 0 条…</span><span class="tslot now">第 N 轮·仍命中</span></div>
  <div class="lane"><span class="lane-label">记忆变 / 压缩后</span><span class="tslot">改了 core 块</span><span class="tslot">重建第 0 条</span><span class="tslot span">前缀变了 · 这次缓存失效</span><span class="tslot now">换来正确状态</span></div>
</div>

<p>道理在第 5 课算过：稳定的<strong>前缀</strong>能命中 KV cache，省下大量重复 prefill。system 提示正好是最前面那段最稳定的前缀。每步都重写它，等于每步都让缓存失效——又慢又贵。</p>

<p>算笔账更直观：假设 system 提示有几千 token，每轮重写就意味着这几千 token 的 prefill <strong>无法复用</strong>、得从头重算。十轮下来就是几万 token 的白烧。把"不动第 0 条"设成默认，正是把第 5 课的省钱手艺用到了底。</p>


<div class="note info"><span class="ni">👉</span><span class="nx">看源码里的原话：<span class="mono">letta_agent_v3.py</span> 的 <span class="mono">_step</span> 在每步开头只刷新消息、<strong>跳过 system 重建</strong>，注释写着"preserve prefix caching"；只有<strong>记忆变化</strong>（<span class="mono">core_memory_*</span> 触发 <span class="mono">update_memory_if_changed_async</span>）或<strong>压缩之后</strong>才会重建第 0 条——其中只有压缩那次带 <span class="mono">force=True</span>。</span></div>

<p>于是策略很清楚：<strong>能不动第 0 条就不动</strong>。普通对话轮次保持前缀稳定、吃满缓存；只有当核心记忆真的被改了、或发生上下文压缩（第 12 课）时，才不得不重建一次——用一次缓存失效，换一份正确的"自我"。</p>

<p>那"压缩之后为什么要强制重建"？因为压缩会重写消息序列、可能动到靠前的内容，前缀本就破了；既然缓存这一次反正要失效，就顺手用 <span class="mono">force=True</span> 把第 0 条也刷成最新的记忆与时间戳。第 12 课会把这条压缩路径讲透。</p>


<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>这是 agent 在运行时给自己"重新编程"。</strong>别的系统把记忆存到一张<strong>外挂的表</strong>里，用时再查；Letta 反其道而行——把记忆直接<strong>编进系统提示</strong>。<span class="mono">Memory.compile()</span> 的产物，经 <span class="mono">{CORE_MEMORY}</span> 占位符拼进那条<strong>持久化的 system 消息</strong>；块一变，<span class="mono">rebuild_system_prompt_async</span> 就<strong>原地</strong>重写第 0 条（<span class="mono">temp.id = curr.id</span>，同一个 id）。于是 agent "记住一件事"不再是"在数据库里记一笔"，而是<strong>改写自己的出厂设定</strong>——它读到的"我是谁"变了，言行随之而变。这正是 MemGPT 区别于"LLM + 外挂记忆"的根本一手：记忆不是 agent 之外的附件，而是<strong>它自我定义的源代码</strong>，而且这份源代码<strong>由 agent 自己维护</strong>。把这层看透，你会发现"自我编辑记忆"既不玄、也不重——它就是"改一段字符串、换一条消息"，但因为那段字符串<strong>定义了 agent 是谁</strong>，这件小事就成了整个 MemGPT 的灵魂。
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>别以为"每一步都会重建 system 来同步最新记忆"。</strong>恰恰相反：正常步骤<strong>故意跳过</strong> system 重建，为的是<strong>保住 prefix cache</strong>（<span class="mono">_step</span> 注释明写 "preserve prefix caching"）。第 0 条只在<strong>两种时刻</strong>被重写：① 核心记忆<strong>真的变了</strong>（<span class="mono">core_memory_*</span> 触发）；② 发生<strong>上下文压缩</strong>之后（<span class="mono">rebuild_system_prompt_async(force=True)</span>）。这还带来一个推论：<span class="mono">&lt;memory_metadata&gt;</span> 里 recall / archival 的<strong>计数可能略微滞后</strong>——因为只有 core 变化才触发重建，光是来了几条新消息并不会立刻刷新那串数字。知道这点，你就不会被"为什么计数没马上更新"绊住。
</div>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>整条闭环的源码坐标。</strong>两个写工具 <span class="mono">core_memory_append / replace</span> 在 <span class="mono">LettaCoreToolExecutor</span>（<span class="mono">core_tool_executor.py</span>），都先验 <span class="mono">read_only</span>、再 <span class="mono">update_block_value</span>、最后 <span class="mono">update_memory_if_changed_async</span> 持久化；后者在 <span class="mono">letta/services/agent_manager.py</span>，比对记忆若有变就 <span class="mono">update_block_async</span> 落库（last-write-wins）并调 <span class="mono">rebuild_system_prompt_async</span>。重建逻辑同在 <span class="mono">agent_manager.py</span>：取 <span class="mono">message_ids[0]</span>、<span class="mono">memory.compile()</span>、未变则跳过，变了就用 <span class="mono">get_system_message_from_compiled_memory</span>（<span class="mono">prompt_generator.py</span>）拼出新 system，并令 <span class="mono">temp.id = curr.id</span> 原地 <span class="mono">update_message_by_id_async</span>。占位符常量 <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span> 在 <span class="mono">letta/constants.py</span>；"正常步骤不重建"的注释在 <span class="mono">letta/agents/letta_agent_v3.py</span> 的 <span class="mono">_step</span>。
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>为什么把记忆编进 prompt，而不是另存一张表？</summary><div class="acc-body">
<p><strong>示例：</strong>你也可以把"用户叫老王"存进一张 user_facts 表，每次提问前查出来塞进提示。很多 RAG 产品就是这么做的。</p>
<p><strong>为什么这样设计：</strong>Letta 让记忆<strong>本身就是 system 提示</strong>，于是模型每轮"无条件"读到它，不依赖任何检索步骤是否被触发；而且 agent 能用同一套工具<strong>读写自己</strong>，把"我是谁"变成可推理、可编辑的对象，而不是外部注入的只读上下文。</p>
<p><strong>源码在哪：</strong>编译在 <span class="mono">Memory.compile</span>（<span class="mono">letta/schemas/memory.py</span>），注入在 <span class="mono">get_system_message_from_compiled_memory</span>（<span class="mono">prompt_generator.py</span>）。</p>
<p><strong>还有什么替代：</strong>外挂表 + 每轮检索——好处是 core 不占稳定前缀，坏处是多一道"会不会查、查得准不准"的不确定性，且记忆变成 agent 改不动的只读外设。</p>
</div></details>

<details class="accordion"><summary>prefix cache 与第 0 条：到底何时才重建？</summary><div class="acc-body">
<p><strong>示例：</strong>连续聊十轮普通对话，第 0 条<strong>一次都不会重写</strong>；直到某轮 agent 调了 <span class="mono">core_memory_replace</span>，或窗口满了触发压缩，第 0 条才被重建一次。</p>
<p><strong>为什么这样设计：</strong>system 提示是最靠前、最稳定的前缀，命中 KV cache 能省大量 prefill（第 5 课）。每步重建会持续打碎缓存，得不偿失，所以默认"按需重建"。</p>
<p><strong>源码在哪：</strong><span class="mono">letta/agents/letta_agent_v3.py</span> 的 <span class="mono">_step</span> 在步开头 <span class="mono">_refresh_messages</span> 但跳过 system 重建（注释 "preserve prefix caching"）；压缩后才 <span class="mono">rebuild_system_prompt_async(force=True)</span>。</p>
<p><strong>还有什么替代：</strong>每步强制重建——绝对最新，但缓存常年失效、又慢又贵；完全不重建——便宜，但 agent 改了记忆却读不到，自我编辑形同虚设。Letta 取"变了才重建"的折中。</p>
</div></details>

<details class="accordion"><summary>append 还是 replace？两个写工具怎么选</summary><div class="acc-body">
<p><strong>示例：</strong>用户说"我还养了只猫"——用 <span class="mono">append</span> 往 human 块尾加一行；用户说"我搬到上海了，不在北京了"——用 <span class="mono">replace</span> 把"北京"那段精确换成"上海"。</p>
<p><strong>为什么这样设计：</strong><span class="mono">append</span> 只做 <span class="mono">current + "\n" + content</span>，安全、不碰旧内容，适合"新增事实"；<span class="mono">replace</span> 要求 <span class="mono">old_content</span> 在块里<strong>精确出现</strong>，适合"纠正/更新"，匹配不到会直接报错，避免误改。</p>
<p><strong>源码在哪：</strong>两者都在 <span class="mono">core_tool_executor.py</span>；<span class="mono">replace</span> 用 <span class="mono">current.replace(old, new)</span>，若 <span class="mono">old_content not in current</span> 就抛错。</p>
<p><strong>还有什么替代：</strong>只给一个"整块覆写"的工具——简单但危险，agent 容易把整张卡写崩；拆成 append / replace 让"加"和"改"各有其稳妥语义。</p>
</div></details>

<details class="accordion"><summary>多个 agent 共享同一个块，一处改会怎样？</summary><div class="acc-body">
<p><strong>示例：</strong>第 8 课讲过，两个 agent 可以挂同一张 <span class="mono">block-…</span>。若 agent A 用 <span class="mono">core_memory_replace</span> 改了它，agent B 下一轮重编译 system 时就读到了新值。</p>
<p><strong>为什么这样设计：</strong>块是可寻址的一等实体，共享靠 <span class="mono">blocks_agents</span> 多对多表把同一行连给多个 agent。自编辑写的是<strong>那一行</strong>，所以"一处改、处处变"，天然实现共享记忆。</p>
<p><strong>源码在哪：</strong>落库走 <span class="mono">block_manager.update_block_async</span>（<span class="mono">update_memory_if_changed_async</span> 里调用），共享关系在 <span class="mono">letta/orm/blocks_agents.py</span>；B 端的"读到新值"发生在它自己的 <span class="mono">rebuild_system_prompt_async</span>。</p>
<p><strong>还有什么替代：</strong>每个 agent 各存副本——要写同步逻辑、易不一致；共享同一行 + 各自按需重建，是更省心的做法（但也要小心只读块与并发覆写）。</p>
</div></details>

<h2>下一站：把这套"动手"铺到其余三层</h2>
<p>这一课是第三部分的灵魂：你看清了 core 怎么被 agent <strong>自己改写</strong>，以及"改记忆 = 改 system"这条闭环。接下来三课，把"动手"的视角铺到其余两层与收尾。</p>

<p>为什么说它是"灵魂"？因为"自我编辑记忆"正是 MemGPT 那篇论文最反直觉、也最关键的一手：让 LLM <strong>用工具管理自己的上下文</strong>。一旦"读、写、改自己的 system"这件事成立，agent 就从"被动应答的模型"变成了"会经营自己记忆的主体"——其余各层、各种工具，都是围着这个核心转。</p>


<p><strong>第 10 课</strong>讲 archival 的"写与搜"——<span class="mono">archival_memory_insert / search</span> 怎么把长期知识嵌入成向量、再按相似度捞回；<strong>第 11 课</strong>讲 recall 与对话历史——消息怎么作为带类型的 JSON 事件被持久与检索；<strong>第 12 课</strong>回到第 5 课那道墙，讲<strong>上下文压缩</strong>，也正是本课说的"压缩后会强制重建第 0 条"的那条路径。</p>

<p>临走再把闭环默背一遍：<strong>改块 → 落库 → 编译填洞 → 原地换第 0 条 → 下一轮生效</strong>；而且<strong>能不重建就不重建</strong>，只为护住 prefix cache。这五步加一条"按需重建"的纪律，把这条链记牢，你就握住了 Letta 记忆系统跳动的心脏，也就读懂了 MemGPT 最想说的那句话。</p>


<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>core memory 就是 system 提示的一部分</strong>：所以"自我编辑记忆"本质是<strong>改写系统提示</strong>，不是往别处的表里记一笔。</li>
    <li><strong>两个写工具</strong>：<span class="mono">core_memory_append</span>（尾部追加）/ <span class="mono">core_memory_replace</span>（精确替换），都先验 <span class="mono">read_only</span>、再改 <span class="mono">block.value</span>、再持久化（<span class="mono">core_tool_executor.py</span>）。</li>
    <li><strong>{CORE_MEMORY} 占位符</strong>：编译好的块经 <span class="mono">get_system_message_from_compiled_memory</span> 的 <span class="mono">.replace</span> 填进这个洞；常量 <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span>（<span class="mono">constants.py</span>）。</li>
    <li><strong>原地重写第 0 条</strong>：<span class="mono">rebuild_system_prompt_async</span> 取 <span class="mono">message_ids[0]</span>，记忆变了才重建，并令 <span class="mono">temp.id = curr.id</span> 同 id 原地更新。</li>
    <li><strong>正常步骤不重建</strong>：为保 prefix cache，<span class="mono">_step</span> 故意跳过 system 重建；只在<strong>记忆变化</strong>或<strong>压缩</strong>后重建（<span class="mono">letta_agent_v3.py</span>）。</li>
    <li><strong>一句话</strong>：agent 在运行时给自己"重新编程"——改一段定义"我是谁"的字符串、换掉那一条 system 消息，这就是 MemGPT 的灵魂。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Lesson 7 gave you the three-tier map and dropped one line: core memory is the <strong>only</strong> tier the agent can rewrite itself. Lesson 8 cracked open core's smallest unit — the <strong>memory Block</strong>, with its four fields <span class="mono">label / value / limit / read_only</span>. This lesson takes that line about self-editing all the way down to the mechanism.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
The answer is a little surprising: when an agent "remembers" something, it is <strong>rewriting its own system prompt</strong>. Edit a block → persist → recompile → <strong>rewrite message #0 in place</strong>. By the end you'll see core memory isn't "memory stored elsewhere" — it <strong>is part of the system prompt itself</strong>.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Picture core memory as a character sheet taped to the agent's forehead.</strong> It says who you are, who the user is, what you're doing now — and the agent <strong>reads it before every single utterance</strong>. The magic: the agent can pick up a pen and <strong>edit that sheet</strong> — cross out an old line, write in a new one. Change the sheet, and from its next sentence on, the "self" it reads is different, so its words and actions follow. It isn't "noting something in some database" — it is <strong>rewriting its own factory settings</strong>. That's the trick this lesson exposes: memory isn't elsewhere; it's on its face, read every turn.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>Grab this lesson in one line: the agent calls <span class="mono">core_memory_append / replace</span> to change a block's <span class="mono">value</span> → persist → trigger <span class="mono">rebuild_system_prompt_async</span>, which <strong>rewrites message #0 (the system message) in place</strong>.</strong> And the system prompt has a hardcoded placeholder <span class="mono">{CORE_MEMORY}</span> where the compiled blocks get <strong>spliced in</strong>. So "editing memory" and "editing the system prompt" are the <strong>same act</strong> in Letta. We'll walk the whole loop: from one tool call, to message #0 being swapped, to why "normal steps deliberately don't rebuild."
</div>

<h2>First, one line: core memory IS part of system</h2>
<p>Many assume core memory is like recall / archival — stored in some table, fetched on demand. <strong>It isn't.</strong> core stays in-window because <span class="mono">Memory.compile()</span> has compiled it into the <strong>persisted message #0</strong> (Lessons 7 &amp; 8) — and that #0 is in-window every turn, recompiled only when it changes. It <strong>is the system text itself</strong>.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>Key line:</strong> core memory isn't "memory stored elsewhere" — it <strong>is part of the system prompt</strong>. An agent editing memory = editing the "factory settings" it reads every turn.</span></div>

<p>Contrast makes it clear: recall and archival are "out-of-window stores" you must fetch with a tool; core needs <strong>no fetch</strong> — it <strong>lives in the persisted system message</strong>, visible the moment the model opens its eyes each turn. Because it "lives on" system, editing it equals editing system.</p>

<p>Hold that, and the rest is corollaries: since core is system text, editing memory must mean editing system text; and system text is the <strong>persisted message #0</strong>, so an edit ultimately <strong>lands on that one message</strong>. Let's walk the causal chain step by step.</p>

<h2>The self-editing loop: from "want to remember" to "live next turn"</h2>
<p>Big picture first. One self-edit takes six steps — from the user saying something worth keeping, to the agent's "self" actually changing next turn. Memorize these six; every later section just zooms into one.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Something worth keeping</h4><p>User says "call me Boss from now on," or a task's status changes — the agent decides it belongs in core.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Call a memory tool</h4><p>The agent issues a tool call <span class="mono">core_memory_replace(label, old, new)</span> (or append).</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Change block.value</h4><p>The executor first edits the block's <span class="mono">value</span> in memory (<span class="mono">update_block_value</span>).</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Persist to the store</h4><p><span class="mono">update_memory_if_changed_async</span> writes the change to the database (block table, last-write-wins).</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Rewrite message #0</h4><p><span class="mono">rebuild_system_prompt_async</span> recompiles memory and edits message #0, the system message, <strong>in place</strong>.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Live next turn</h4><p>At the start of the next turn, the model reads the new system — the agent now "is" the new setting.</p></div></div>
</div>

<p>Note the "lag" in step 6: the change isn't injected into the conversation on the spot — it <strong>settles into message #0</strong> and gets read when the next turn assembles context. Self-editing is "writing to your future self" — pen down this turn, effect next turn.</p>

<p>Concretely: the human block said "user is evaluating options." The user says "we decided — buying Letta." The agent calls <span class="mono">core_memory_replace('human', 'evaluating options', 'chose Letta')</span> — value changed, persisted, #0 recompiled. Next turn the model reads system, knows "project decided," and won't dumbly ask "how's the evaluation going?"</p>

<p>In this loop, steps 4 and 5 don't always "do real work": only when the compiled memory <strong>actually differs</strong> from the current system do they persist and rewrite #0. A "changed but unchanged" call gets quietly short-circuited — clearer when we look at <span class="mono">rebuild_system_prompt_async</span> next.</p>

<h2>What core_memory_append / replace actually change</h2>
<p>Start at the layer closest to "hands on": what the two tools do. Both live in <span class="mono">LettaCoreToolExecutor</span> (<span class="mono">letta/services/tool_executor/core_tool_executor.py</span>), and they're shorter than you'd guess.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">core_memory_replace (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">core_memory_replace</span>(self, agent_state, actor, label, old_content, new_content):
    block = agent_state.memory.get_block(label)
    <span class="kw">if</span> block.read_only:                       <span class="cm"># read-only block: the agent can't edit it (Lesson 8's hard rule)</span>
        <span class="kw">raise</span> ValueError(READ_ONLY_BLOCK_EDIT_ERROR)
    current = <span class="kw">str</span>(block.value)
    <span class="kw">if</span> old_content <span class="kw">not in</span> current:            <span class="cm"># old must appear verbatim, else error</span>
        <span class="kw">raise</span> ValueError(<span class="st">"Old content not found"</span>)
    new_value = current.replace(old_content, new_content)
    agent_state.memory.<span class="fn">update_block_value</span>(label=label, value=new_value)   <span class="cm"># (1) edit the in-memory block</span>
    <span class="kw">await</span> self.agent_manager.<span class="fn">update_memory_if_changed_async</span>(            <span class="cm"># (2) persist + trigger rebuild</span>
        agent_id=agent_state.id, new_memory=agent_state.memory, actor=actor)
    <span class="kw">return</span> new_value
</pre></div>

<p>Three things, in order: <strong>(1) gatekeep</strong> — a read_only block raises <span class="mono">READ_ONLY_BLOCK_EDIT_ERROR</span> (Lesson 8's hard constraint is this very line); <strong>(2) change the value</strong> — replace <span class="mono">block.value</span> in the in-memory object; <strong>(3) hand off</strong> — delegate the big job of "persist + rebuild system" to <span class="mono">update_memory_if_changed_async</span>.</p>

<div class="cols">
  <div class="col"><h4><span class="mono">core_memory_append</span></h4><p><strong>Appends a line</strong> at the block's end: <span class="mono">current + "\n" + content</span>. Good for "learned one more thing"; leaves existing content alone.</p></div>
  <div class="col"><h4><span class="mono">core_memory_replace</span></h4><p><strong>Exact replace</strong> of a span: <span class="mono">old</span> must exist and match. Good for "a fact changed; correct old into new."</p></div>
</div>

<p>What's striking is how tiny the implementation is: the real heavy lifting — persisting, deciding whether to rebuild, swapping the message in place — is all pushed to <span class="mono">update_memory_if_changed_async</span>. The tools only "get the block right" and leave "make it take effect" downstream. This <strong>separation of concerns</strong> makes both tools easy to read and hard to misuse.</p>

<p>One more detail: the tools <strong>return the new value</strong> (<span class="mono">return new_value</span>). That return goes back into the conversation as the tool result, letting the agent <strong>confirm on the spot</strong> "I just changed the card to this" — it has immediate feedback on its own edit, not a blind write.</p>

<div class="note info"><span class="ni">📌</span><span class="nx">Both tools <strong>check <span class="mono">read_only</span> first</strong>: a read-only block (like a team-shared "policy" card) raises immediately and the agent can't change it — Lesson 8's read/write permission, realized on the self-edit path.</span></div>

<div class="cute">
  <div class="row">
    <span class="emoji">🤖</span><span class="arrow">✏️</span><span class="emoji">📋</span>
    <span class="bubble">"change 'call me Lee' to 'call me Boss'"</span>
  </div>
  <div class="cap">Self-editing memory = the agent picks up a pen and rewrites the very system "character sheet" it reads each turn</div>
</div>

<h2>{CORE_MEMORY}: a hole reserved in the template</h2>
<p>Step (2) passed the ball to "persist + rebuild." But before the rebuild, settle one thing: <strong>where exactly</strong> do the compiled blocks get spliced into system? Into a hardcoded placeholder, <span class="mono">{CORE_MEMORY}</span>.</p>

<div class="flow">
  <div class="node"><div class="nt">system template</div><div class="nd">has the <span class="mono">{CORE_MEMORY}</span> hole</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Memory.compile()</div><div class="nd">blocks → &lt;memory_blocks&gt;</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">.replace fills it</div><div class="nd">hole → real memory + inventory</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">full system#0</div><div class="nd">what the model truly reads</div></div>
</div>

<p>That hole is filled by <span class="mono">get_system_message_from_compiled_memory</span> (<span class="mono">letta/prompts/prompt_generator.py</span>). It replaces the placeholder with the compiled blocks plus Lesson 7's <span class="mono">&lt;memory_metadata&gt;</span> inventory.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/prompts/prompt_generator.py</span><span class="ln">get_system_message_from_compiled_memory (simplified)</span></div>
<pre><span class="cm"># 1) compiled blocks + inventory joined into one big in-context-memory string</span>
full_memory_string = memory_with_sources + <span class="st">"\n\n"</span> + memory_metadata_string

<span class="cm"># 2) the placeholder is the string "{CORE_MEMORY}" (name from constant IN_CONTEXT_MEMORY_KEYWORD)</span>
memory_variable_string = <span class="st">"{"</span> + IN_CONTEXT_MEMORY_KEYWORD + <span class="st">"}"</span>

<span class="cm"># 3) replace the hole in the template with real memory -- this is "memory enters system"</span>
formatted_prompt = system_prompt.replace(memory_variable_string, full_memory_string)
<span class="kw">return</span> formatted_prompt
</pre></div>

<div class="note info"><span class="ni">📌</span><span class="nx">The name <span class="mono">{CORE_MEMORY}</span> is hardcoded in the constant <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span> (<span class="mono">letta/constants.py</span>). It's the only "protected" variable in the system-prompt template — as long as your custom prompt keeps this hole, memory gets injected.</span></div>

<p>What if your custom system prompt <strong>forgets the hole</strong>? No worry — the injector has a fallback: if <span class="mono">{CORE_MEMORY}</span> is missing from the template, it <strong>appends it to the end automatically</strong> (<span class="mono">append_icm_if_missing</span>), so memory makes it into system no matter what.</p>

<p>So "core in-window" is no background magic — it's a plain string replace: carve a <span class="mono">{CORE_MEMORY}</span> into the template, fill it with the current blocks on each rebuild. Understand the hole and you understand "how memory becomes the text the model reads."</p>

<p>What fills the hole isn't only the blocks. <span class="mono">full_memory_string</span> = the compiled <span class="mono">&lt;memory_blocks&gt;</span> + Lesson 7's <span class="mono">&lt;memory_metadata&gt;</span> inventory. The former is "what's on the cards in front of you"; the latter is "how much is still out of window." Joined, the model sees the present and stays aware of what's outside.</p>

<h2>Rewriting message #0 in place: rebuild_system_prompt_async</h2>
<p>Now the heaviest step in the loop. What actually writes the "hole-filled new system text" back to the message is <span class="mono">rebuild_system_prompt_async</span> (<span class="mono">letta/services/agent_manager.py</span>). Two key moves: <strong>don't write if unchanged</strong>, <strong>swap in place if changed</strong>.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/agent_manager.py</span><span class="ln">rebuild_system_prompt_async (pseudocode)</span></div>
<pre><span class="kw">async def</span> <span class="fn">rebuild_system_prompt_async</span>(agent_id, actor, force=<span class="kw">False</span>):
    curr = message_manager.get(message_ids[<span class="nb">0</span>])        <span class="cm"># message #0 = the system message</span>
    memory_str = agent_state.memory.<span class="fn">compile</span>(...)        <span class="cm"># recompile current core memory</span>

    <span class="kw">if</span> memory_str <span class="kw">in</span> curr.content <span class="kw">and not</span> force:    <span class="cm"># memory unchanged -> return, no rebuild</span>
        <span class="kw">return</span>                                       <span class="cm">#   (this is the prefix-cache moat)</span>

    new_system = PromptGenerator.<span class="fn">get_system_message_from_compiled_memory</span>(
        system_prompt=agent_state.system, memory_with_sources=memory_str, ...)

    temp = Message(role=<span class="st">"system"</span>, content=new_system)
    temp.id = curr.id                            <span class="cm"># * key: keep the SAME id</span>
    <span class="kw">await</span> message_manager.<span class="fn">update_message_by_id_async</span>(curr.id, ...)   <span class="cm"># rewrite #0 in place</span>
</pre></div>

<p>Two design decisions worth a pause. First, <strong>don't write if unchanged</strong>: compare whether the "newly compiled memory" is already in the current system; if so and not forced, return — saving lots of pointless rebuilds. Second, <strong>swap in place</strong>: the new message <strong>reuses the old message's id</strong> (<span class="mono">temp.id = curr.id</span>), so message #0 is still that one message, only its content changed.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">On rewrite, <span class="mono">temp.id = curr.id</span>: message #0's <strong>identity is unchanged</strong>; only its <strong>content</strong> changes — same id, in-place update, <strong>not</strong> a newly inserted system message. This keeps "history holds exactly one system message" always true.</span></div>

<p>Don't underestimate the "don't write if unchanged" short-circuit: it first checks whether the newly compiled memory is already in the current system, and returns if so. So even if the agent called a tool but the content didn't actually change (re-replacing "Boss" with "Boss"), it won't needlessly rewrite #0 or pointlessly bust the cache. Here, <strong>correct</strong> and <strong>cheap</strong> happen to align.</p>

<p>Tie this to Lesson 6: the agent's state is externalized and persistent, and the system prompt is that one persistent message, <span class="mono">message_ids[0]</span>. So "editing memory" ultimately lands on a <strong>message in the database</strong> — neither lost, nor unreadable on the next load.</p>

<p>Vividly: message #0 is a display board with a fixed address number. Editing memory isn't <strong>swapping in a new board</strong> (new id) — it's <strong>erasing old text and writing new</strong> (same id). The address didn't change; the next load walks to the same spot and reads new content. That's why an agent's "history" always holds exactly one system message.</p>

<p>Persistence follows <strong>"write only if changed"</strong>: <span class="mono">update_memory_if_changed_async</span> compares the compiled result first, and only writes blocks to the database (<span class="mono">update_block_async</span>, later write wins) when something truly changed. When multiple agents race to edit the same shared card, that's a plain last-write-wins rule.</p>

<h2>Why "normal steps deliberately don't rebuild" — for prefix cache</h2>
<p>Here's an easily-missed but crucial trade-off. If memory matters this much, why not rebuild system <strong>every step</strong> to guarantee it's absolutely fresh? Because that would <strong>smash the prefix cache</strong> (Lesson 5).</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">normal steps</span><span class="tslot">turn 1 · system#0 stable</span><span class="tslot">turn 2 · prefix unchanged → cache hit</span><span class="tslot span">leave #0 alone…</span><span class="tslot now">turn N · still hits</span></div>
  <div class="lane"><span class="lane-label">memory change / post-compaction</span><span class="tslot">edited a core block</span><span class="tslot">rebuild #0</span><span class="tslot span">prefix changed · miss this once</span><span class="tslot now">buys a correct state</span></div>
</div>

<p>The math is from Lesson 5: a stable <strong>prefix</strong> hits the KV cache, saving lots of repeated prefill. The system prompt is exactly that stablest leading prefix. Rewriting it every step invalidates the cache every step — slow and expensive.</p>

<p>Concretely: say the system prompt is a few thousand tokens; rewriting it every turn means those tokens of prefill <strong>can't be reused</strong> and must be recomputed. Ten turns is tens of thousands of tokens burned. Making "don't touch #0" the default is Lesson 5's cost-saving craft taken to its conclusion.</p>

<div class="note info"><span class="ni">👉</span><span class="nx">Straight from the source: <span class="mono">_step</span> in <span class="mono">letta_agent_v3.py</span> only refreshes messages at the start of each step and <strong>skips the system rebuild</strong>, with the comment "preserve prefix caching"; only on a <strong>memory change</strong> (<span class="mono">core_memory_*</span> triggers <span class="mono">update_memory_if_changed_async</span>) or <strong>after compaction</strong> does it rebuild message #0 — and only the compaction path passes <span class="mono">force=True</span>.</span></div>

<p>So the strategy is clear: <strong>don't touch #0 if you can avoid it</strong>. Normal turns keep the prefix stable and feast on the cache; only when core memory truly changed, or compaction (Lesson 12) happens, is a rebuild forced — trading one cache miss for a correct "self."</p>

<p>Why force a rebuild after compaction? Because compaction rewrites the message sequence and may touch leading content — the prefix is already broken; since the cache will miss this once anyway, it also uses <span class="mono">force=True</span> to refresh #0 to the latest memory and timestamp. Lesson 12 walks this compaction path in full.</p>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>This is the agent "reprogramming" itself at runtime.</strong> Other systems stash memory in an <strong>external table</strong> and query it when needed; Letta goes the other way — it <strong>compiles memory directly into the system prompt</strong>. The output of <span class="mono">Memory.compile()</span> is spliced, via the <span class="mono">{CORE_MEMORY}</span> placeholder, into that <strong>persisted system message</strong>; when a block changes, <span class="mono">rebuild_system_prompt_async</span> rewrites message #0 <strong>in place</strong> (<span class="mono">temp.id = curr.id</span>, same id). So an agent "remembering" isn't "noting a row in a database" — it's <strong>rewriting its own factory settings</strong>: the "who I am" it reads changes, and its behavior follows. This is exactly what separates MemGPT from "an LLM + bolted-on memory": memory isn't an attachment outside the agent, it's the <strong>source code of the agent's self-definition</strong> — and that source code is <strong>maintained by the agent itself</strong>. See through this layer and "self-editing memory" feels neither mystical nor heavy — it's "change a string, swap a message," but because that string <strong>defines who the agent is</strong>, this small act becomes the soul of all MemGPT.
</div>

<div class="card warn">
  <div class="tag">⚠️ Common misconception</div>
  <strong>Don't assume "every step rebuilds system to sync the latest memory."</strong> Quite the opposite: normal steps <strong>deliberately skip</strong> the system rebuild to <strong>preserve the prefix cache</strong> (the <span class="mono">_step</span> comment literally says "preserve prefix caching"). Message #0 is rewritten only at <strong>two moments</strong>: (1) core memory <strong>actually changed</strong> (triggered by <span class="mono">core_memory_*</span>); (2) <strong>after compaction</strong> (<span class="mono">rebuild_system_prompt_async(force=True)</span>). A corollary: the recall / archival <strong>counts in <span class="mono">&lt;memory_metadata&gt;</span> may lag slightly</strong> — since only a core change triggers a rebuild, merely receiving a few new messages won't refresh those numbers immediately. Know this and you won't be tripped up by "why didn't the count update right away."
</div>

<div class="card detail">
  <div class="tag">🔬 In the code</div>
  <strong>Source coordinates for the whole loop.</strong> The two write tools <span class="mono">core_memory_append / replace</span> are in <span class="mono">LettaCoreToolExecutor</span> (<span class="mono">core_tool_executor.py</span>): each checks <span class="mono">read_only</span>, then <span class="mono">update_block_value</span>, then persists via <span class="mono">update_memory_if_changed_async</span>; the latter (in <span class="mono">letta/services/agent_manager.py</span>) compares memory and, if changed, writes blocks with <span class="mono">update_block_async</span> (last-write-wins) and calls <span class="mono">rebuild_system_prompt_async</span>. The rebuild (also in <span class="mono">agent_manager.py</span>) takes <span class="mono">message_ids[0]</span>, runs <span class="mono">memory.compile()</span>, returns early if unchanged, else builds the new system via <span class="mono">get_system_message_from_compiled_memory</span> (<span class="mono">prompt_generator.py</span>) and sets <span class="mono">temp.id = curr.id</span> for an in-place <span class="mono">update_message_by_id_async</span>. The placeholder constant <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span> is in <span class="mono">letta/constants.py</span>; the "normal steps don't rebuild" comment is in <span class="mono">_step</span> (<span class="mono">letta/agents/letta_agent_v3.py</span>).
</div>

<h2>Going deeper</h2>

<details class="accordion"><summary>Why compile memory into the prompt instead of a side table?</summary><div class="acc-body">
<p><strong>Example:</strong> you could store "user is Boss" in a user_facts table and inject it into the prompt before each question. Many RAG products do exactly that.</p>
<p><strong>Why it's designed this way:</strong> Letta makes memory <strong>the system prompt itself</strong>, so the model "unconditionally" reads it every turn, independent of whether some retrieval step fired; and the agent uses the <strong>same tools to read and write itself</strong>, turning "who I am" into a reasoned, editable object rather than read-only injected context.</p>
<p><strong>Where in code:</strong> compilation in <span class="mono">Memory.compile</span> (<span class="mono">letta/schemas/memory.py</span>); injection in <span class="mono">get_system_message_from_compiled_memory</span> (<span class="mono">prompt_generator.py</span>).</p>
<p><strong>Alternatives:</strong> side table + per-turn retrieval — keeps core out of the stable prefix, but adds the uncertainty of "did it fetch, did it fetch right," and memory becomes a read-only peripheral the agent can't edit.</p>
</div></details>

<details class="accordion"><summary>Prefix cache and message #0: when exactly is it rebuilt?</summary><div class="acc-body">
<p><strong>Example:</strong> chat ten normal turns and message #0 is <strong>never rewritten</strong>; not until some turn the agent calls <span class="mono">core_memory_replace</span>, or the window fills and triggers compaction, is #0 rebuilt once.</p>
<p><strong>Why it's designed this way:</strong> the system prompt is the leading, stablest prefix; hitting the KV cache saves heavy prefill (Lesson 5). Rebuilding every step keeps shattering the cache — not worth it, so the default is "rebuild on demand."</p>
<p><strong>Where in code:</strong> <span class="mono">_step</span> in <span class="mono">letta/agents/letta_agent_v3.py</span> calls <span class="mono">_refresh_messages</span> at step start but skips the system rebuild (comment "preserve prefix caching"); only after compaction does it <span class="mono">rebuild_system_prompt_async(force=True)</span>.</p>
<p><strong>Alternatives:</strong> force a rebuild every step — absolutely fresh, but the cache misses constantly, slow and costly; never rebuild — cheap, but the agent edits memory and can't read it, so self-editing is moot. Letta takes the "rebuild when changed" middle.</p>
</div></details>

<details class="accordion"><summary>append or replace? choosing between the two write tools</summary><div class="acc-body">
<p><strong>Example:</strong> the user says "I also have a cat" — use <span class="mono">append</span> to add a line to the human block; "I moved to Shanghai, not Beijing anymore" — use <span class="mono">replace</span> to swap the "Beijing" span exactly for "Shanghai."</p>
<p><strong>Why it's designed this way:</strong> <span class="mono">append</span> just does <span class="mono">current + "\n" + content</span> — safe, doesn't touch old content, good for "new facts"; <span class="mono">replace</span> requires <span class="mono">old_content</span> to appear <strong>verbatim</strong>, good for "correct/update," and errors out if it can't match — avoiding accidental edits.</p>
<p><strong>Where in code:</strong> both in <span class="mono">core_tool_executor.py</span>; <span class="mono">replace</span> uses <span class="mono">current.replace(old, new)</span> and raises if <span class="mono">old_content not in current</span>.</p>
<p><strong>Alternatives:</strong> a single "overwrite the whole block" tool — simple but risky, the agent easily wrecks the card; splitting into append / replace gives "add" and "edit" each a safe, distinct semantic.</p>
</div></details>

<details class="accordion"><summary>Multiple agents sharing one block — what happens on an edit?</summary><div class="acc-body">
<p><strong>Example:</strong> Lesson 8 showed two agents can attach the same <span class="mono">block-…</span>. If agent A edits it via <span class="mono">core_memory_replace</span>, agent B reads the new value when it recompiles system next turn.</p>
<p><strong>Why it's designed this way:</strong> a block is an addressable first-class entity; sharing uses the <span class="mono">blocks_agents</span> many-to-many table to link the same row to multiple agents. Self-editing writes <strong>that row</strong>, so "change once, change everywhere" — shared memory falls out naturally.</p>
<p><strong>Where in code:</strong> persistence goes through <span class="mono">block_manager.update_block_async</span> (called inside <span class="mono">update_memory_if_changed_async</span>); the sharing relation is in <span class="mono">letta/orm/blocks_agents.py</span>; B "reading the new value" happens in its own <span class="mono">rebuild_system_prompt_async</span>.</p>
<p><strong>Alternatives:</strong> each agent keeps a copy — needs sync logic, easy to drift; sharing one row + each rebuilding on demand is simpler (but mind read-only blocks and concurrent overwrites).</p>
</div></details>

<h2>Next stop: spread "hands-on" across the other tiers</h2>
<p>This lesson is Part 3's soul: you've seen how core gets <strong>rewritten by the agent itself</strong>, and the loop where "editing memory = editing system." The next three lessons spread the hands-on view across the other two tiers and the wrap-up.</p>

<p>Why call it the "soul"? Because "self-editing memory" is the MemGPT paper's most counterintuitive — and most crucial — move: letting an LLM <strong>manage its own context with tools</strong>. Once "read, write, edit your own system" holds, the agent turns from "a passive responder" into "a subject that curates its own memory" — every other tier and tool orbits this core.</p>

<p><strong>Lesson 10</strong> covers archival's "write & search" — how <span class="mono">archival_memory_insert / search</span> embed long-term knowledge into vectors and pull it back by similarity; <strong>Lesson 11</strong> covers recall and conversation history — how messages are persisted and searched as typed JSON events; <strong>Lesson 12</strong> returns to Lesson 5's wall with <strong>context compaction</strong> — exactly the "force-rebuild #0 after compaction" path this lesson mentioned.</p>

<p>One last recitation of the loop: <strong>edit block → persist → compile & fill the hole → swap #0 in place → live next turn</strong>; and <strong>don't rebuild unless you must</strong>, purely to protect the prefix cache. These five steps plus a "rebuild on demand" discipline — keep this chain and you hold the beating heart of Letta's memory system, and you've understood the one thing MemGPT most wants to say.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>core memory IS part of the system prompt</strong>: so "self-editing memory" is fundamentally <strong>rewriting the system prompt</strong>, not noting a row in some other table.</li>
    <li><strong>Two write tools</strong>: <span class="mono">core_memory_append</span> (append a line) / <span class="mono">core_memory_replace</span> (exact replace), both check <span class="mono">read_only</span> first, then edit <span class="mono">block.value</span>, then persist (<span class="mono">core_tool_executor.py</span>).</li>
    <li><strong>The {CORE_MEMORY} placeholder</strong>: compiled blocks fill this hole via the <span class="mono">.replace</span> in <span class="mono">get_system_message_from_compiled_memory</span>; the constant is <span class="mono">IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"</span> (<span class="mono">constants.py</span>).</li>
    <li><strong>Rewrite message #0 in place</strong>: <span class="mono">rebuild_system_prompt_async</span> takes <span class="mono">message_ids[0]</span>, rebuilds only if memory changed, and sets <span class="mono">temp.id = curr.id</span> for a same-id in-place update.</li>
    <li><strong>Normal steps don't rebuild</strong>: to preserve the prefix cache, <span class="mono">_step</span> deliberately skips the system rebuild; it rebuilds only on a <strong>memory change</strong> or <strong>after compaction</strong> (<span class="mono">letta_agent_v3.py</span>).</li>
    <li><strong>In one line</strong>: the agent "reprograms" itself at runtime — change a string that defines "who I am," swap that one system message, and that is the soul of MemGPT.</li>
  </ul>
</div>
""",
}


LESSON_10 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 7 课那张三层地图里，archival（归档）是压在最底下、<strong>容量近乎无限</strong>的那一层：它在上下文窗口<strong>之外</strong>，平时不占一个 token，要用时才按需捞回。这一课把这层"长期记忆"讲到能动手。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
关键词只有四个：<strong>Passage</strong>（一条归档记忆 = 文本 + 向量）、<strong>insert</strong>（嵌入并存）、<strong>search</strong>（按相似度捞），以及让它从笔记本跑到生产<strong>同一套代码</strong>的 pgvector / sqlite-vec 双方言。读完你会明白：archival 就是<strong>内建进 agent 的 RAG</strong>。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把 archival 想成 agent 自己的一间地下档案室——但这间档案室会"按意思"找东西。</strong>普通仓库你得记得"那份合同放在 3 排 B 架第 2 格"，靠精确编号去取；archival 不一样：你只要描述"<strong>关于去年那笔续约的讨论</strong>"，它就能把意思最接近的几份档案<strong>捞出来</strong>，哪怕你一个原词都没说对。秘密在于：存进去的时候，每段文字都被翻译成一串<strong>坐标（向量）</strong>，意思相近的坐标也彼此靠近；查的时候把问题也翻成坐标，找<strong>最近的邻居</strong>即可。于是 agent 拥有了一座<strong>会自己记笔记、又能按语义翻找</strong>的长期资料库，而且它<strong>容量近乎无限</strong>，绝不会"装满了就忘"。这也是它和"贴在额头上、每轮都读"的 core 最大的不同：core 是<strong>随身的便签</strong>，archival 是<strong>身后那座取之不尽的档案室</strong>——平时不打扰你，喊一声才把最相关的几份递到眼前。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：archival = 一座 <span class="mono">Passage</span> 向量库 + 两个工具。</strong><span class="mono">archival_memory_insert(content, tags)</span> 把一段文本<strong>嵌入成向量</strong>、连同标签存成一条 <span class="mono">Passage</span>；<span class="mono">archival_memory_search(query, tags)</span> 把查询也嵌入，再<strong>按余弦相似度</strong>取回最像的几条。两个工具都在 <span class="mono">LettaCoreToolExecutor</span>，声明在 <span class="mono">function_sets/base.py</span>。底层那一列向量，在 Postgres 上是 pgvector、在 SQLite 上是 sqlite-vec——<strong>同一套查询、两种后端</strong>。本课就沿"写一条、搜一条、换个数据库照样跑"走一遍。 看懂这一条，你会发现 archival 没什么神秘：它不过是"把文本算成向量存下来、再按距离取回"，难的不是机制，而是<strong>想清楚什么该长期记、什么时候该去翻</strong>。
</div>

<h2>先把 archival 摆回三层地图里</h2>
<p>第 7 课讲过三层的分工：<strong>core</strong> 在窗、最稀缺、agent 自己改；<strong>recall</strong> 是<strong>全量对话历史</strong>，按关键词/时间召回；<strong>archival</strong> 则是窗外的<strong>长期向量库</strong>，按<strong>语义</strong>检索。这一课只聚焦最后一层。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>一句话定位：</strong>archival 就是<strong>内建进 agent 的 RAG</strong>——agent 自己写长期笔记（insert）、再按意思取回（search），不依赖外部检索管线，发起权全在 agent 手里。</span></div>

<p>三层最值得记住的差别是<strong>"怎么检索"</strong>：core 不用检索（一直在眼前），recall 用 <strong>hybrid（字面+语义）</strong>翻完整聊天记录，archival 按<strong>意思</strong>翻向量库。下面这张表把它们并排放一起，一眼对清楚。</p>

<table class="t">
  <thead><tr><th>记忆层</th><th>在上下文?</th><th>容量</th><th>谁来写</th><th>怎么检索</th></tr></thead>
  <tbody>
    <tr><td>core 核心</td><td>✅ 永远在窗</td><td class="mono">极小（字符上限）</td><td>agent 自改</td><td>不用检索</td></tr>
    <tr><td>recall 回忆</td><td>❌ 仅最近一段在窗</td><td class="mono">全量对话史</td><td>系统自动记</td><td>hybrid（字面+语义）</td></tr>
    <tr><td>archival 归档</td><td>❌ 全在窗外</td><td class="mono">近乎无限</td><td>agent 主动 insert</td><td>按<strong>语义</strong>（向量）</td></tr>
  </tbody>
</table>

<p>注意 archival 这一行的两个"主动"：容量近乎无限，但它<strong>不会自动记</strong>——得 agent 判断"这条值得长期留着"，主动调 insert；要用时也得<strong>主动</strong> search。它是 agent 自己经营的一座库，不是后台默默记的流水账。</p>

<p>为什么 archival 偏偏要"按语义"检索？因为长期库里的东西<strong>时过境迁</strong>：三个月前 agent 记下"客户偏好深色界面"，今天用户问"界面风格我之前怎么说的来着"——用词对不上，但<strong>意思是一回事</strong>。靠字面早就搜不到了，靠语义却能稳稳捞回。这正是 archival 把"按意思找"设成<strong>默认检索方式</strong>的原因。archival 与 recall 的根本分工其实在"<strong>存什么</strong>"：recall 是系统自动记下的全量对话历史，archival 是 agent 精选的长期知识库。</p>

<div class="cute"><div class="row"><span class="emoji">📦</span><span class="arrow">→</span><span class="emoji">🔢</span><span class="lab">嵌入向量</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="bubble">"按意思找最像的"</span></div>
<div class="cap">归档记忆 = 会按语义检索的长期笔记本，容量近乎无限</div></div>

<h2>一条归档记忆长什么样：Passage</h2>
<p>archival 里的最小单位叫 <span class="mono">Passage</span>（<span class="mono">letta/schemas/passage.py</span>）。剥掉元数据，它的核心就两样东西：<strong>一段文本</strong>，和这段文本的<strong>一串向量</strong>；再加上"用哪个嵌入模型算的"和几个标签。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/passage.py</span><span class="ln">Passage（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">Passage</span>(PassageBase):
    <span class="cm"># 存在 archival memory 里的一条记忆</span>
    text: str                                <span class="cm"># (1) 原始文本</span>
    embedding: Optional[List[float]]         <span class="cm"># (2) 向量：这段文本的"坐标"</span>
    embedding_config: Optional[EmbeddingConfig]   <span class="cm"># (3) 用哪个嵌入模型算的</span>
    archive_id: Optional[str]                <span class="cm"># 属于哪个 archive（agent 的默认档案库）</span>
    tags: Optional[List[str]]                <span class="cm"># (4) 标签：给知识分类、好过滤</span>
</pre></div>

<p>四个字段串起整课：<strong>(1) text</strong> 是你存的原话；<strong>(2) embedding</strong> 是它的语义坐标，search 全靠它；<strong>(3) embedding_config</strong> 记下"用哪个模型嵌入的"，保证存和查用<strong>同一把尺子</strong>；<strong>(4) tags</strong> 让 agent 给自己的知识贴分类标签。</p>

<div class="note info"><span class="ni">📌</span><span class="nx">向量从哪来？由 <span class="mono">embedding_config</span>（<span class="mono">letta/schemas/embedding_config.py</span>）指定的嵌入模型算出。在 pgvector（Postgres）上，归档向量还会被<strong>补齐到固定维度</strong> <span class="mono">MAX_EMBEDDING_DIM = 4096</span>（<span class="mono">letta/constants.py</span>），这样不同模型产出的向量能存进同一列。</span></div>

<p>这里藏着一条铁律：<strong>insert 和 search 必须用同一个嵌入模型</strong>。向量空间是嵌入模型"私人定义"的坐标系，换了模型，同一句话的坐标就全变了——存进去的旧向量和新查询根本不在一个空间里，没法比距离。<span class="mono">embedding_config</span> 把这把"尺子"钉死在每条 <span class="mono">Passage</span> 上，正是为了让存与查<strong>始终量纲一致</strong>。</p>

<p>还要破一个误会：容量"近乎无限"<strong>不等于"免费随便塞"</strong>。每存一条都要算一次向量、占一行存储；库越大，search 时要比的邻居也越多。所以 archival 的正确姿势是存<strong>提炼过的事实与摘要</strong>，而不是把原始对话一股脑灌进去——这一点下面的"常见误区"卡会再敲一遍。</p>

<h2>两个工具：insert 写、search 读</h2>
<p>先看"写"。agent 调 <span class="mono">archival_memory_insert(content, tags)</span> 时，发生的事可以画成一条直线：<strong>文本 → 嵌入 → Passage(向量) → 落库</strong>。</p>

<div class="flow">
  <div class="node"><div class="nt">一段文本</div><div class="nd">agent 想长期记住的话</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">嵌入模型</div><div class="nd">embedding_config 指定</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Passage</div><div class="nd">text + 向量 + tags</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">写入向量库</div><div class="nd">archival_passages 表</div></div>
</div>

<p>再看"读"。<span class="mono">archival_memory_search(query, tags)</span> 走的是<strong>镜像</strong>的一条线：query 先被嵌入成同样的向量，再去库里找<strong>最近的邻居</strong>，按相似度排好端回来。</p>

<div class="flow">
  <div class="node"><div class="nt">查询语句</div><div class="nd">"关于续约的讨论"</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">嵌入模型</div><div class="nd">同一把尺子</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">最近邻搜索</div><div class="nd">cosine_distance 升序</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Top-K 条 Passage</div><div class="nd">按相似度排好</div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">archival_memory_insert / search（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">archival_memory_insert</span>(self, agent_state, actor, content, tags=<span class="kw">None</span>):
    <span class="kw">await</span> self.passage_manager.<span class="fn">insert_passage</span>(             <span class="cm"># 嵌入文本 + 存成 Passage</span>
        agent_state=agent_state, text=content, actor=actor, tags=tags)
    <span class="kw">await</span> self.agent_manager.<span class="fn">rebuild_system_prompt_async</span>(       <span class="cm"># 刷新 &lt;memory_metadata&gt; 计数</span>
        agent_id=agent_state.id, actor=actor, force=<span class="kw">True</span>)

<span class="kw">async def</span> <span class="fn">archival_memory_search</span>(self, agent_state, actor, query,
                                 tags=<span class="kw">None</span>, tag_match_mode=<span class="st">"any"</span>, top_k=<span class="kw">None</span>):
    <span class="kw">return await</span> self.agent_manager.<span class="fn">search_agent_archival_memory_async</span>(  <span class="cm"># 嵌入 query → 最近邻</span>
        agent_id=agent_state.id, actor=actor, query=query,
        tags=tags, tag_match_mode=tag_match_mode, top_k=top_k)
</pre></div>

<p>insert 短得意外：它几乎只是<strong>转交</strong>——把活儿交给 <span class="mono">PassageManager.insert_passage</span>，自己最后补一刀 <span class="mono">rebuild_system_prompt_async(force=True)</span>。那一刀是为了刷新第 7 课讲的<strong>库存清单</strong>：插了新档案，<span class="mono">&lt;memory_metadata&gt;</span> 里"archival 共几条"得跟着变，agent 才知道窗外又多了一条。</p>

<p>那条 Passage 具体存到哪？存进 agent 的<strong>默认 archive</strong>（档案库）。<span class="mono">insert_passage</span> 内部先调 <span class="mono">ArchiveManager.get_or_create_default_archive_for_agent_async</span>——没有就建一个、有就拿来用，再把新 Passage 挂到这座库上。一个 agent 默认对应一座 archive，它所有的归档记忆都装在里面，<span class="mono">archive_id</span> 就是它们的"户口"。</p>

<p>search 也只是<strong>转交</strong>给 <span class="mono">search_agent_archival_memory_async</span>。关键在它内部那句 <span class="mono">order_by(cosine_distance(...).asc())</span>：距离越小 = 意思越近，所以<strong>升序取前 K 条</strong>就是"最像的几条"。<span class="mono">top_k</span> 控制取几条（工具 docstring 标注默认 10，未传时实际回退到 <span class="mono">RETRIEVAL_QUERY_DEFAULT_PAGE_SIZE</span>=5）。</p>

<p>串个具体场景：用户两周前随口提过"我对花生过敏"，agent 当时 <span class="mono">archival_memory_insert("用户对花生过敏", tags=["健康"])</span> 记了一笔。今天用户问"这家餐厅你觉得我能吃吗"，agent 调 <span class="mono">archival_memory_search("用户的饮食禁忌")</span>——查询里一个"花生"都没提，但语义最近的那条 Passage 还是被捞了回来，agent 于是想起了过敏这件事。这就是"按意思找"在真实对话里的威力：<strong>记得的是意思，而不是字眼</strong>。</p>

<p>那 agent 怎么知道"现在该去搜一下"？还是靠第 7 课那张<strong>库存清单</strong>：<span class="mono">&lt;memory_metadata&gt;</span> 每轮都告诉它"archival 里还压着 N 条"。看到窗外有货、又觉得当前问题可能和过去有关，它就主动发起一次 search——连"<strong>什么时候该翻档案</strong>"这个时机判断，也是 agent 自己做的。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx"><strong>每次 insert 都要一次嵌入调用</strong>：把文本送进嵌入模型算向量，是有成本的（钱 + 延迟）。所以 archival 适合存"<strong>自洽、值得长期留</strong>"的事实或摘要，而不是把每句闲聊都塞进去。</span></div>

<div class="note info"><span class="ni">👉</span><span class="nx"><strong>tags 是过滤器：</strong>search 可带 <span class="mono">tags</span> 和 <span class="mono">tag_match_mode</span>（<span class="mono">any</span>/<span class="mono">all</span>）——先按标签缩小范围、再按语义排序。于是 agent 能"只在<strong>会议纪要</strong>里找关于路线图的讨论"，把语义搜索和分类过滤叠起来用。</span></div>

<h2>同一套代码，两种数据库：pgvector / sqlite-vec</h2>
<p>第 7 课点过一句"双数据库魔法"：开发用 SQLite、生产用 Postgres，<strong>同一套代码</strong>。archival 的向量检索把这句话演到了极致——靠的是一个按数据库类型<strong>二选一</strong>的向量列。</p>

<div class="cols">
  <div class="col"><h4>🧪 开发：SQLite + sqlite-vec</h4><p>向量列用自定义类型 <span class="mono">CommonVector</span>，把 float 数组序列化成二进制存进 SQLite；相似度用注册进去的 <span class="mono">cosine_distance</span> 函数算。<strong>零外部依赖，笔记本即开即用。</strong></p></div>
  <div class="col"><h4>🚀 生产：Postgres + pgvector</h4><p>向量列用 <span class="mono">pgvector</span> 的 <span class="mono">Vector(4096)</span> 类型，相似度走原生 <span class="mono">cosine_distance</span> 算子，可建索引、扛大规模。<strong>同样的接口，换更强的后端。</strong></p></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/orm/passage.py · sqlalchemy_base.py</span><span class="ln">向量列 + 最近邻（二选一）</span></div>
<pre><span class="cm"># letta/orm/passage.py —— 向量列按数据库类型二选一</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    <span class="kw">from</span> pgvector.sqlalchemy <span class="kw">import</span> Vector
    embedding = mapped_column(Vector(MAX_EMBEDDING_DIM))   <span class="cm"># 生产：pgvector</span>
<span class="kw">else</span>:
    embedding = Column(CommonVector)                       <span class="cm"># 开发：sqlite-vec</span>

<span class="cm"># letta/orm/sqlalchemy_base.py —— 排序也二选一，但落到同一句语义</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    query = query.order_by(cls.embedding.<span class="fn">cosine_distance</span>(q).asc())
<span class="kw">else</span>:
    query = query.order_by(<span class="fn">func.cosine_distance</span>(cls.embedding, q).asc())
</pre></div>

<p>妙就妙在<strong>上层完全无感</strong>：两个分支最后都落到 <span class="mono">order_by(cosine_distance(...).asc())</span>——同一句"按余弦距离升序取最近邻"。换数据库只换<strong>列类型和距离算子的实现</strong>，<span class="mono">insert</span> / <span class="mono">search</span> 两个工具、agent 的用法，一个字都不用改。</p>

<p>把这层看穿，你对第 6 课"有状态"那句话会有更深体会：agent 的长期知识<strong>外化在数据库里</strong>，换不换数据库、用哪种向量后端，都不影响它"是谁、记得什么"。引擎只是<strong>存取记忆的介质</strong>，记忆本身是一串与介质无关的 Passage——这正是"状态外化"在向量层的兑现。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>这就是"笔记本 → 生产不改代码"的底气：</strong>引擎由 <span class="mono">settings.database_engine</span>（有没有配 <span class="mono">letta_pg_uri</span>）自动选；选 SQLite 还是 Postgres，决定了向量列用 <span class="mono">CommonVector</span> 还是 <span class="mono">pgvector.Vector</span>——但你的检索逻辑浑然不觉。</span></div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>archival 就是把 RAG <em>内建进了 agent 自己</em>。</strong>别的产品把"长期知识库 + 向量检索"做成 agent <strong>外面</strong>的一套管线，由工程师决定何时检索、检索什么；Letta 把这套能力<strong>变成 agent 自己的两个工具</strong>：它自己判断"这条值得长期记"，调 <span class="mono">archival_memory_insert</span> 写下笔记；自己判断"我需要回忆点什么"，调 <span class="mono">archival_memory_search</span> <strong>按意思</strong>取回——检索的发起权在 agent 手里，而不是外部代码。更妙的是<strong>同一手"双方言"魔法</strong>：向量列在开发期是 sqlite-vec、生产期是 pgvector，可 <span class="mono">insert</span> / <span class="mono">search</span> 两个工具与上层逻辑<strong>一字不改</strong>，于是从笔记本到生产<strong>无缝放大</strong>。再加上 <span class="mono">tags</span>——agent 能给自己的知识<strong>分类、过滤</strong>，"只在会议纪要里搜路线图"。把这三点合起来：一个能<strong>自己写笔记、自己按语义翻找、还能自己分门别类</strong>的长期大脑，正是 MemGPT 让 agent "管理自己记忆"的最后一块拼图。 一句话收束：core 让 agent <em>改写自己是谁</em>，archival 让 agent <em>积累并随时调取自己知道的一切</em>——两者合起来，才是一个真正"会成长"的 agent。
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>别把 archival_memory_search 当成数据库的精确查询。</strong>它是<strong>相似度</strong>搜索，不是 <span class="mono">WHERE text = '…'</span>：返回的是"意思最接近"的几条，<strong>可能漏掉</strong>用词不同但相关的、也<strong>可能带回</strong>意思沾边却不完全对的——结果<strong>按相似度排序，没有"完全命中"这一说</strong>。所以它擅长"<strong>我大概记得聊过类似的事</strong>"，不擅长"精确匹配某个 ID / 字段"（那是 recall 的字面检索该干的）。还有一笔<strong>成本</strong>要记牢：<strong>每次 insert 和每次 search 都要一次嵌入调用</strong>——把文本或查询送进嵌入模型算向量，既花钱又有延迟。所以别把每句闲聊都 insert，也别拿 search 当 if 判断来频繁轮询；存"自洽、值得长期留"的事实，查"真的需要回忆"的时候。 再纠一个常见想象：search 返回的"相关度"不是布尔的"有/无"，而是连续的"远/近"，所以即便库里没有真正切题的东西，它<strong>照样会端回几条最不离谱的</strong>——别把"有返回"误当成"一定找到了"。
</div>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>整条链路的源码坐标。</strong>数据模型 <span class="mono">Passage</span>（text + embedding + embedding_config + tags）在 <span class="mono">letta/schemas/passage.py</span>；落库的 ORM 是 <span class="mono">ArchivalPassage</span>（<span class="mono">letta/orm/passage.py</span>，对应 <span class="mono">archival_passages</span> 表，区别于来自文件的 <span class="mono">SourcePassage</span>）。两个工具 <span class="mono">archival_memory_insert / search</span> 在 <span class="mono">LettaCoreToolExecutor</span>（<span class="mono">core_tool_executor.py</span>），docstring 声明在 <span class="mono">functions/function_sets/base.py</span>。写路径 <span class="mono">PassageManager.insert_passage</span>（<span class="mono">passage_manager.py</span>）先经 <span class="mono">ArchiveManager</span> 取默认 archive、再用 <span class="mono">embedding_config</span> 的模型算向量；搜路径 <span class="mono">search_agent_archival_memory_async</span>（<span class="mono">agent_manager.py</span>）按 <span class="mono">cosine_distance(...).asc()</span> 取最近邻。向量列二选一在 <span class="mono">letta/orm/passage.py</span> / <span class="mono">custom_columns.py</span>（<span class="mono">CommonVector</span>）与 <span class="mono">sqlite_functions.py</span>；维度上限 <span class="mono">MAX_EMBEDDING_DIM = 4096</span>（<span class="mono">constants.py</span>）；引擎选择 <span class="mono">settings.database_engine</span>。tags 的高效查询靠 <span class="mono">PassageTag</span> 联结表（<span class="mono">letta/orm/passage_tag.py</span>）。 想顺藤摸瓜，从这两个工具的 docstring 入手最快——它们把"<strong>按语义、不是按关键词</strong>""加 tag 便于日后查找"写得明明白白，那正是 agent 在 prompt 里读到的使用说明。
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>向量检索一分钟：什么叫"按意思找"</summary><div class="acc-body">
<p><strong>示例：</strong>"狗"和"小狗"用词不同，但向量离得很近；"狗"和"股票"离得很远。把每段文字映射成高维空间里的一个点，<strong>意思近 = 点近</strong>。</p>
<p><strong>为什么这样设计：</strong>嵌入模型学过海量语料，能把语义压进坐标。检索时把 query 也映射成一个点，找<strong>距离最近</strong>的几个点，就是"意思最接近"的几条——这正是"按意思找"而非"按字面找"。</p>
<p><strong>源码在哪：</strong>距离用余弦，<span class="mono">cosine_distance = 1 - cos(θ)</span>（<span class="mono">letta/orm/sqlite_functions.py</span> 的 <span class="mono">cosine_distance</span>）；排序在 <span class="mono">sqlalchemy_base.py</span>，<span class="mono">order_by(...asc())</span> 取距离最小者。</p>
<p><strong>还有什么替代：</strong>关键词检索（BM25 之类）按字面匹配，快但对同义/改写无能为力；向量检索抓语义，但有嵌入成本、且是"相似"非"精确"。两者各有所长，常被组合成 hybrid 检索。</p>
<p><strong>再补一句直觉：</strong>"维度"听着玄，其实就是用几百上千个数字从不同角度给一段话打分——有的维度大致对应"和钱有关吗"、有的对应"语气正式吗"。两段话这些分都接近，它们在空间里就挨得近。你不必懂每个维度是什么，只要记住<strong>"近 = 像"</strong>就够用了。</p>
</div></details>

<details class="accordion"><summary>pgvector 还是 sqlite-vec？什么时候用哪个</summary><div class="acc-body">
<p><strong>示例：</strong>本地跑 demo、写测试，不想装 Postgres——默认就是 SQLite + sqlite-vec，开箱即用；上线要扛量、要索引——配上 <span class="mono">letta_pg_uri</span> 切到 Postgres + pgvector。</p>
<p><strong>为什么这样设计：</strong>开发期要<strong>零摩擦</strong>，生产期要<strong>能扩展</strong>。把"向量列类型"和"距离算子"做成按引擎二选一，就能在不改上层代码的前提下兼顾两头。</p>
<p><strong>源码在哪：</strong>引擎判定 <span class="mono">settings.database_engine</span>（配了 <span class="mono">letta_pg_uri</span> 即 Postgres，否则 SQLite）；列定义在 <span class="mono">letta/orm/passage.py</span> 的 <span class="mono">BasePassage</span>，SQLite 用 <span class="mono">CommonVector</span>、Postgres 用 <span class="mono">pgvector.Vector</span>。</p>
<p><strong>还有什么替代：</strong>专用向量库（如 Turbopuffer）——Letta 也支持，archive 可配 <span class="mono">vector_db_provider</span> 走外部向量服务；好处是更强的检索/规模，代价是多一个外部依赖。</p>
<p><strong>一个数字感受规模：</strong>sqlite-vec 在本地几万条以内顺滑得很；但当归档涨到几十万、上百万条，pgvector 的近邻索引（如 HNSW / IVFFlat）就成了刚需——这也是"生产切 Postgres"的现实理由，不只是为了多用户并发，更是为了让"找最近邻"这件事在大库上依然够快。</p>
</div></details>

<details class="accordion"><summary>archive 与 tags：agent 怎么给知识分类</summary><div class="acc-body">
<p><strong>示例：</strong>insert 时打上 <span class="mono">tags=["会议","路线图"]</span>；search 时用 <span class="mono">tags=["会议"], tag_match_mode="all"</span> 就只在会议类档案里按语义找。</p>
<p><strong>为什么这样设计：</strong>纯语义搜索有时太"散"。tags 给 agent 一把<strong>结构化的过滤刀</strong>：先按标签圈定范围、再按向量排序，召回更准。每个 agent 默认有一个 <strong>archive</strong>（档案库）装它所有的 Passage。</p>
<p><strong>源码在哪：</strong>默认 archive 由 <span class="mono">ArchiveManager.get_or_create_default_archive_for_agent_async</span>（<span class="mono">archive_manager.py</span>）取得；tags 既存在 <span class="mono">Passage.tags</span> 的 JSON 列里，又写进 <span class="mono">PassageTag</span> 联结表（<span class="mono">letta/orm/passage_tag.py</span>）做高效过滤/计数。</p>
<p><strong>还有什么替代：</strong>不打 tags 也能用，全靠语义；但当知识变多、类别清晰时，tags 能显著提升"找得准"。这是"语义 + 结构"的叠加。</p>
<p><strong>多一层实现细节：</strong>tags 是<strong>双存</strong>的——既塞在 <span class="mono">Passage.tags</span> 的 JSON 列里（取 Passage 时顺手就有），又拆进 <span class="mono">PassageTag</span> 联结表（一行一个 tag）。前者方便随数据带出，后者让"按某 tag 过滤/计数有多少条"这类查询走索引、跑得快。同一份信息、两种摆法，各为一种访问模式服务。</p>
</div></details>

<details class="accordion"><summary>archival passage vs source passage：两种 Passage</summary><div class="acc-body">
<p><strong>示例：</strong>agent 自己 <span class="mono">insert</span> 写下的笔记 → <span class="mono">ArchivalPassage</span>；你上传一份 PDF / 文档被切片灌进来的 → <span class="mono">SourcePassage</span>。</p>
<p><strong>为什么这样设计：</strong>两者都是"文本 + 向量"的可检索片段，共享 <span class="mono">BasePassage</span> 的字段与向量列；但来源与归属不同——一个挂在 agent 的 <strong>archive</strong> 上、由 agent 自写，一个挂在<strong>外部文件 / 数据源</strong>上。分成两张表各自建索引更清晰。</p>
<p><strong>源码在哪：</strong><span class="mono">letta/orm/passage.py</span>：<span class="mono">ArchivalPassage</span>（<span class="mono">archival_passages</span>，带 <span class="mono">ArchiveMixin</span>）与 <span class="mono">SourcePassage</span>（<span class="mono">source_passages</span>，带 <span class="mono">FileMixin</span>/<span class="mono">SourceMixin</span>）都继承 <span class="mono">BasePassage</span>。</p>
<p><strong>还有什么替代：</strong>合成一张表加个"来源"字段也行，但分表能让"agent 自写的记忆"和"灌进来的资料"各自演化、各建各的索引。本课聚焦前者。</p>
</div></details>

<h2>下一站：从"长期向量库"回到"对话历史"</h2>
<p>这一课你拿下了三层里最"远"的一层：archival 是 agent 自己经营的<strong>长期向量库</strong>，靠 <span class="mono">insert</span> 写、<span class="mono">search</span> 按语义读，底层是一列"二选一"的向量。它把 RAG 收进了 agent 自己手里。</p>

<div class="note info"><span class="ni">👉</span><span class="nx"><strong>预告第 11 课：</strong>archival 是 agent <strong>精选</strong>的长期库（按意思翻），而 recall 是系统<strong>自动记</strong>的完整对话历史（hybrid 检索）。下一课讲 recall——每条消息怎么作为带类型的 JSON 事件被持久，又怎么用 <span class="mono">conversation_search</span> 捞回。</span></div>

<p>再往后，<strong>第 12 课</strong>回到第 5 课那道"上下文窗口"的墙：当窗口快满，较旧的消息怎么被<strong>压缩成摘要</strong>换出去——也就是第 9 课结尾说的"压缩后会强制重建第 0 条"的那条路径。三层记忆 + 一套压缩，第三部分就闭环了。</p>

<p>临走把这条链默背一遍：<strong>文本 → 嵌入 → Passage(向量) → 落库</strong>是写，<strong>query → 嵌入 → 最近邻 → Top-K</strong>是读，中间靠 <span class="mono">cosine_distance</span> 量"像不像"，底下靠"二选一的向量列"在笔记本与生产之间无缝切换。把这四步记牢，再记住"<strong>相似不是精确、每次都要嵌入</strong>"这句告诫，archival 这层你就真正握在手里了。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>archival = 内建进 agent 的 RAG</strong>：窗外的长期向量库，容量近乎无限，按<strong>语义</strong>检索；agent 自己 <span class="mono">insert</span> 写、自己 <span class="mono">search</span> 读。</li>
    <li><strong>Passage</strong>：一条归档记忆 = <span class="mono">text</span> + <span class="mono">embedding</span>（向量）+ <span class="mono">embedding_config</span> + <span class="mono">tags</span>（<span class="mono">letta/schemas/passage.py</span>）。</li>
    <li><strong>两个工具</strong>：<span class="mono">archival_memory_insert</span> 转交 <span class="mono">PassageManager.insert_passage</span>（嵌入 + 存）；<span class="mono">archival_memory_search</span> 按 <span class="mono">cosine_distance(...).asc()</span> 取最近邻（<span class="mono">core_tool_executor.py</span>）。</li>
    <li><strong>双方言向量列</strong>：开发 SQLite + <span class="mono">CommonVector</span>/sqlite-vec、生产 Postgres + <span class="mono">pgvector.Vector(4096)</span>，由 <span class="mono">settings.database_engine</span> 自动选——<strong>上层一字不改</strong>。</li>
    <li><strong>search 是"相似"非"精确"</strong>，且<strong>每次 insert/search 都要一次嵌入调用</strong>（有成本）——存自洽事实、按需检索。</li>
    <li><strong>tags</strong>：给知识分类，search 时先按标签过滤、再按语义排序（<span class="mono">PassageTag</span> 联结表）。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
In Lesson 7's three-tier map, archival sits at the very bottom — the tier with <strong>near-infinite capacity</strong>: it lives <strong>outside</strong> the context window, costs zero tokens at rest, and is fetched on demand only when needed. This lesson takes that "long-term memory" tier all the way to hands-on.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
Just four keywords: <strong>Passage</strong> (one archival memory = text + vector), <strong>insert</strong> (embed and store), <strong>search</strong> (retrieve by similarity), and the pgvector / sqlite-vec dual dialect that runs laptop-to-prod on <strong>the same code</strong>. By the end you'll see: archival is <strong>RAG built right into the agent</strong>.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Picture archival as the agent's own basement archive room — but one that finds things "by meaning."</strong> An ordinary warehouse makes you remember "that contract is in row 3, shelf B, slot 2," retrieved by exact index; archival is different: you just describe "<strong>the discussion about last year's renewal</strong>," and it <strong>pulls out</strong> the closest-in-meaning files, even if you got not a single original word right. The secret: on the way in, each piece of text is translated into a string of <strong>coordinates (a vector)</strong>, and similar meanings land near each other; on the way out, the question is translated into coordinates too, and you just find the <strong>nearest neighbors</strong>. So the agent gets a long-term library that <strong>takes its own notes and searches them semantically</strong>, with <strong>near-infinite capacity</strong> — it never "fills up and forgets." That's also its biggest difference from core, "taped to its forehead, read every turn": core is a <strong>sticky note it carries</strong>, archival is the <strong>inexhaustible archive room behind it</strong> — quiet until you call, then it hands you the few most relevant files.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>Grab this lesson in one line: archival = a <span class="mono">Passage</span> vector store + two tools.</strong> <span class="mono">archival_memory_insert(content, tags)</span> <strong>embeds</strong> a piece of text into a vector and stores it, with tags, as a <span class="mono">Passage</span>; <span class="mono">archival_memory_search(query, tags)</span> embeds the query too, then returns the closest few <strong>by cosine similarity</strong>. Both tools live in <span class="mono">LettaCoreToolExecutor</span>, declared in <span class="mono">function_sets/base.py</span>. That one vector column underneath is pgvector on Postgres and sqlite-vec on SQLite — <strong>same query, two backends</strong>. We'll walk "write one, search one, swap the database and it still runs." See this, and archival loses its mystery: it's just "compute a vector from text, store it, fetch by distance"; the hard part isn't the mechanism, it's <strong>deciding what's worth keeping long-term and when to go look</strong>.
</div>

<h2>First, put archival back on the three-tier map</h2>
<p>Lesson 7 covered the division of labor: <strong>core</strong> is in-window, scarcest, edited by the agent itself; <strong>recall</strong> is the <strong>full conversation history</strong>, recalled by keyword/time; <strong>archival</strong> is the out-of-window <strong>long-term vector store</strong>, searched by <strong>meaning</strong>. This lesson focuses only on the last.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>One-line placement:</strong> archival is <strong>RAG built into the agent</strong> — the agent writes its own long-term notes (insert) and retrieves them by meaning (search), with no external retrieval pipeline; the agent itself holds the trigger.</span></div>

<p>The difference worth memorizing across the three is <strong>"how you retrieve"</strong>: core needs no retrieval (always in view), recall searches the full chat log with <strong>hybrid (text + meaning)</strong>, archival flips through a vector store <strong>by meaning</strong>. The table below puts them side by side.</p>

<table class="t">
  <thead><tr><th>Memory tier</th><th>In context?</th><th>Capacity</th><th>Who writes</th><th>How retrieved</th></tr></thead>
  <tbody>
    <tr><td>core</td><td>✅ always in-window</td><td class="mono">tiny (char limit)</td><td>agent self-edits</td><td>no retrieval</td></tr>
    <tr><td>recall</td><td>❌ only recent slice in-window</td><td class="mono">full history</td><td>system auto-logs</td><td>hybrid (text + meaning)</td></tr>
    <tr><td>archival</td><td>❌ all out-of-window</td><td class="mono">near-infinite</td><td>agent actively inserts</td><td>by <strong>meaning</strong> (vectors)</td></tr>
  </tbody>
</table>

<p>Note the two "actives" in the archival row: capacity is near-infinite, but it <strong>doesn't auto-record</strong> — the agent must judge "this is worth keeping long-term" and actively call insert; and it must <strong>actively</strong> search to use it. It's a library the agent runs itself, not a ledger quietly kept in the background.</p>

<p>Why must archival retrieve "by meaning"? Because long-term contents <strong>drift over time</strong>: three months ago the agent noted "customer prefers a dark UI"; today the user asks "what did I say about the interface style?" — the words don't match, but <strong>the meaning is the same</strong>. Literal search lost it long ago; semantic search pulls it back reliably. That's why archival makes "search by meaning" its <strong>default</strong>. The real split from recall is <strong>what each stores</strong>: recall is the system's full auto-logged conversation history, archival is the agent's curated long-term store.</p>

<div class="cute"><div class="row"><span class="emoji">📦</span><span class="arrow">→</span><span class="emoji">🔢</span><span class="lab">embed vector</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="bubble">"find the closest by meaning"</span></div>
<div class="cap">Archival memory = a long-term notebook searched semantically, with near-infinite capacity</div></div>

<h2>What one archival memory looks like: Passage</h2>
<p>The smallest unit in archival is the <span class="mono">Passage</span> (<span class="mono">letta/schemas/passage.py</span>). Strip the metadata and its core is two things: <strong>a piece of text</strong> and that text's <strong>vector</strong>; plus "which embedding model computed it" and a few tags.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/passage.py</span><span class="ln">Passage (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">Passage</span>(PassageBase):
    <span class="cm"># one memory stored in archival memory</span>
    text: str                                <span class="cm"># (1) the raw text</span>
    embedding: Optional[List[float]]         <span class="cm"># (2) vector: this text's "coordinates"</span>
    embedding_config: Optional[EmbeddingConfig]   <span class="cm"># (3) which embedding model computed it</span>
    archive_id: Optional[str]                <span class="cm"># which archive (the agent's default store)</span>
    tags: Optional[List[str]]                <span class="cm"># (4) tags: categorize knowledge, easy to filter</span>
</pre></div>

<p>Four fields tie the lesson together: <strong>(1) text</strong> is what you stored; <strong>(2) embedding</strong> is its semantic coordinates, on which search wholly relies; <strong>(3) embedding_config</strong> records "which model embedded it," so storing and searching use <strong>the same ruler</strong>; <strong>(4) tags</strong> let the agent categorize its own knowledge.</p>

<div class="note info"><span class="ni">📌</span><span class="nx">Where do vectors come from? Computed by the embedding model named in <span class="mono">embedding_config</span> (<span class="mono">letta/schemas/embedding_config.py</span>). On pgvector (Postgres), archival vectors are also <strong>padded to a fixed dimension</strong>, <span class="mono">MAX_EMBEDDING_DIM = 4096</span> (<span class="mono">letta/constants.py</span>), so vectors from different models fit one column.</span></div>

<p>There's an iron rule hiding here: <strong>insert and search must use the same embedding model</strong>. A vector space is a coordinate system "privately defined" by the embedding model; change the model and the same sentence's coordinates change entirely — old stored vectors and the new query aren't even in the same space, so distances are meaningless. <span class="mono">embedding_config</span> pins that "ruler" onto every <span class="mono">Passage</span> precisely to keep storing and searching <strong>dimensionally consistent</strong>.</p>

<p>And break one illusion: "near-infinite" capacity <strong>doesn't mean "free, stuff anything in."</strong> Every insert computes a vector and takes a row; the bigger the store, the more neighbors search must compare. So the right posture is to store <strong>distilled facts and summaries</strong>, not dump raw conversation wholesale — the "common pitfall" card below hammers this again.</p>

<h2>Two tools: insert writes, search reads</h2>
<p>Writing first. When the agent calls <span class="mono">archival_memory_insert(content, tags)</span>, what happens is a straight line: <strong>text → embed → Passage(vector) → store</strong>.</p>

<div class="flow">
  <div class="node"><div class="nt">a piece of text</div><div class="nd">what the agent wants to keep</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">embedding model</div><div class="nd">named by embedding_config</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Passage</div><div class="nd">text + vector + tags</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">write to store</div><div class="nd">archival_passages table</div></div>
</div>

<p>Reading next. <span class="mono">archival_memory_search(query, tags)</span> runs the <strong>mirror</strong> line: the query is embedded into the same kind of vector, then it finds the <strong>nearest neighbors</strong> in the store, sorted by similarity and handed back.</p>

<div class="flow">
  <div class="node"><div class="nt">query</div><div class="nd">"the discussion about renewal"</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">embedding model</div><div class="nd">the same ruler</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">nearest-neighbor search</div><div class="nd">cosine_distance ascending</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Top-K Passages</div><div class="nd">sorted by similarity</div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">archival_memory_insert / search (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">archival_memory_insert</span>(self, agent_state, actor, content, tags=<span class="kw">None</span>):
    <span class="kw">await</span> self.passage_manager.<span class="fn">insert_passage</span>(             <span class="cm"># embed text + store as a Passage</span>
        agent_state=agent_state, text=content, actor=actor, tags=tags)
    <span class="kw">await</span> self.agent_manager.<span class="fn">rebuild_system_prompt_async</span>(       <span class="cm"># refresh &lt;memory_metadata&gt; count</span>
        agent_id=agent_state.id, actor=actor, force=<span class="kw">True</span>)

<span class="kw">async def</span> <span class="fn">archival_memory_search</span>(self, agent_state, actor, query,
                                 tags=<span class="kw">None</span>, tag_match_mode=<span class="st">"any"</span>, top_k=<span class="kw">None</span>):
    <span class="kw">return await</span> self.agent_manager.<span class="fn">search_agent_archival_memory_async</span>(  <span class="cm"># embed query -&gt; nearest</span>
        agent_id=agent_state.id, actor=actor, query=query,
        tags=tags, tag_match_mode=tag_match_mode, top_k=top_k)
</pre></div>

<p>insert is surprisingly tiny: it's almost pure <strong>delegation</strong> — it hands the work to <span class="mono">PassageManager.insert_passage</span> and adds one final stroke, <span class="mono">rebuild_system_prompt_async(force=True)</span>. That stroke refreshes the <strong>inventory list</strong> from Lesson 7: after inserting, the "archival count" in <span class="mono">&lt;memory_metadata&gt;</span> must change, so the agent knows one more thing now sits outside the window.</p>

<p>Where exactly does that Passage go? Into the agent's <strong>default archive</strong>. Inside, <span class="mono">insert_passage</span> first calls <span class="mono">ArchiveManager.get_or_create_default_archive_for_agent_async</span> — create one if absent, reuse if present — then attaches the new Passage to it. One agent maps to one archive by default; all its archival memories live there, and <span class="mono">archive_id</span> is their "address."</p>

<p>search is also pure <strong>delegation</strong>, to <span class="mono">search_agent_archival_memory_async</span>. The key is that inner <span class="mono">order_by(cosine_distance(...).asc())</span>: smaller distance = closer meaning, so <strong>taking the top K in ascending order</strong> is "the closest few." <span class="mono">top_k</span> controls how many; default 10.</p>

<p>A concrete scene: two weeks ago the user mentioned in passing "I'm allergic to peanuts," and the agent noted <span class="mono">archival_memory_insert("user is allergic to peanuts", tags=["health"])</span>. Today the user asks "do you think I can eat at this restaurant?" The agent calls <span class="mono">archival_memory_search("the user's dietary restrictions")</span> — the query never says "peanut," yet the semantically nearest Passage still comes back, and the agent remembers the allergy. That's the power of "search by meaning" in a real conversation: <strong>it remembers meaning, not wording</strong>.</p>

<p>So how does the agent know "now's the time to search"? Again via Lesson 7's <strong>inventory list</strong>: <span class="mono">&lt;memory_metadata&gt;</span> tells it every turn "there are still N out in archival." Seeing goods outside the window and sensing the current question may relate to the past, it actively fires a search — even the <strong>timing decision</strong> of "when to flip through the archive" is the agent's own.</p>

<div class="note tip"><span class="ni">✅</span><span class="nx"><strong>Every insert costs one embedding call</strong>: sending text to the embedding model to compute a vector has a cost (money + latency). So archival suits <strong>self-contained, worth-keeping</strong> facts or summaries — not stuffing in every bit of small talk.</span></div>

<div class="note info"><span class="ni">👉</span><span class="nx"><strong>tags are a filter:</strong> search can take <span class="mono">tags</span> and <span class="mono">tag_match_mode</span> (<span class="mono">any</span>/<span class="mono">all</span>) — narrow by tag first, then rank by meaning. So the agent can "find only the roadmap discussion <strong>within meeting notes</strong>," stacking semantic search and categorical filtering.</span></div>

<h2>Same code, two databases: pgvector / sqlite-vec</h2>
<p>Lesson 7 hinted at "the dual-database magic": SQLite in dev, Postgres in prod, <strong>the same code</strong>. Archival's vector search takes that to the extreme — via a vector column chosen <strong>two-ways</strong> by database type.</p>

<div class="cols">
  <div class="col"><h4>🧪 Dev: SQLite + sqlite-vec</h4><p>The vector column uses the custom type <span class="mono">CommonVector</span>, serializing the float array to binary in SQLite; similarity is computed by the registered <span class="mono">cosine_distance</span> function. <strong>Zero external deps, instant on a laptop.</strong></p></div>
  <div class="col"><h4>🚀 Prod: Postgres + pgvector</h4><p>The vector column uses pgvector's <span class="mono">Vector(4096)</span> type, similarity goes through the native <span class="mono">cosine_distance</span> operator, indexable and built to scale. <strong>Same interface, stronger backend.</strong></p></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/orm/passage.py · sqlalchemy_base.py</span><span class="ln">vector column + nearest neighbor (two-way)</span></div>
<pre><span class="cm"># letta/orm/passage.py —— the vector column is chosen two-ways by db type</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    <span class="kw">from</span> pgvector.sqlalchemy <span class="kw">import</span> Vector
    embedding = mapped_column(Vector(MAX_EMBEDDING_DIM))   <span class="cm"># prod: pgvector</span>
<span class="kw">else</span>:
    embedding = Column(CommonVector)                       <span class="cm"># dev: sqlite-vec</span>

<span class="cm"># letta/orm/sqlalchemy_base.py —— ordering is two-way too, but the same semantics</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    query = query.order_by(cls.embedding.<span class="fn">cosine_distance</span>(q).asc())
<span class="kw">else</span>:
    query = query.order_by(<span class="fn">func.cosine_distance</span>(cls.embedding, q).asc())
</pre></div>

<p>The beauty is the upper layer is <strong>completely oblivious</strong>: both branches end at <span class="mono">order_by(cosine_distance(...).asc())</span> — the same "ascending by cosine distance, take nearest neighbors." Swapping databases only swaps <strong>the column type and the distance operator's implementation</strong>; the two tools <span class="mono">insert</span> / <span class="mono">search</span> and the agent's usage don't change one character.</p>

<p>See through this and Lesson 6's "stateful" line lands deeper: the agent's long-term knowledge is <strong>externalized in the database</strong>, and whether you swap databases or which vector backend you use doesn't change "who it is or what it remembers." The engine is merely <strong>the medium for storing/fetching memory</strong>; memory itself is a list of Passages independent of the medium — that's "externalized state," cashed out at the vector layer.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>This is the backbone of "laptop → prod, no code changes":</strong> the engine is auto-chosen by <span class="mono">settings.database_engine</span> (whether <span class="mono">letta_pg_uri</span> is set); SQLite vs Postgres decides whether the vector column is <span class="mono">CommonVector</span> or <span class="mono">pgvector.Vector</span> — but your retrieval logic never notices.</span></div>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  <strong>archival is RAG <em>built into the agent itself</em>.</strong> Other products make "long-term knowledge base + vector retrieval" a pipeline <strong>outside</strong> the agent, where engineers decide when to retrieve and what; Letta turns that capability into <strong>two of the agent's own tools</strong>: it decides "this is worth keeping" and calls <span class="mono">archival_memory_insert</span> to write the note; it decides "I need to recall something" and calls <span class="mono">archival_memory_search</span> to fetch it <strong>by meaning</strong> — the trigger for retrieval is in the agent's hands, not external code. Even better is <strong>the same "dual-dialect" magic</strong>: the vector column is sqlite-vec in dev and pgvector in prod, yet the two tools <span class="mono">insert</span> / <span class="mono">search</span> and the upper logic <strong>don't change a character</strong>, so it <strong>scales laptop-to-prod seamlessly</strong>. Add <span class="mono">tags</span> — the agent can <strong>categorize and filter</strong> its own knowledge, "search the roadmap only within meeting notes." Put the three together: a long-term brain that <strong>writes its own notes, searches them by meaning, and files them by category</strong> is the final puzzle piece of MemGPT letting an agent "manage its own memory." In one line: core lets the agent <em>rewrite who it is</em>, archival lets the agent <em>accumulate and recall everything it knows</em> — together, that's an agent that truly "grows."
</div>

<div class="card warn">
  <div class="tag">⚠️ Common pitfall</div>
  <strong>Don't treat archival_memory_search as a database's exact query.</strong> It's a <strong>similarity</strong> search, not <span class="mono">WHERE text = '…'</span>: it returns the "closest in meaning" few, which <strong>may miss</strong> relevant items worded differently and <strong>may bring back</strong> things tangentially related but not quite right — results are <strong>ranked by similarity, with no notion of "exact hit."</strong> So it's great at "<strong>I vaguely recall we talked about something like this</strong>," not at "match a specific ID/field exactly" (that's recall's literal search). And one <strong>cost</strong> to remember: <strong>every insert and every search costs an embedding call</strong> — sending text or a query to the embedding model to compute a vector, which costs money and latency. So don't insert every bit of small talk, and don't poll with search as if it were an if-check; store self-contained, worth-keeping facts, and search when you truly need to recall. One more image to correct: search's "relevance" isn't a boolean "have/haven't" but a continuous "far/near," so even when nothing truly on-topic exists, it <strong>still returns the few least-wrong ones</strong> — don't mistake "got a result" for "definitely found it."
</div>

<div class="card detail">
  <div class="tag">🔬 Down to the code</div>
  <strong>Source coordinates for the whole chain.</strong> The data model <span class="mono">Passage</span> (text + embedding + embedding_config + tags) is in <span class="mono">letta/schemas/passage.py</span>; the persisted ORM is <span class="mono">ArchivalPassage</span> (<span class="mono">letta/orm/passage.py</span>, the <span class="mono">archival_passages</span> table, distinct from file-derived <span class="mono">SourcePassage</span>). The two tools <span class="mono">archival_memory_insert / search</span> live in <span class="mono">LettaCoreToolExecutor</span> (<span class="mono">core_tool_executor.py</span>), with docstrings declared in <span class="mono">functions/function_sets/base.py</span>. The write path <span class="mono">PassageManager.insert_passage</span> (<span class="mono">passage_manager.py</span>) first gets the default archive via <span class="mono">ArchiveManager</span>, then computes the vector with <span class="mono">embedding_config</span>'s model; the search path <span class="mono">search_agent_archival_memory_async</span> (<span class="mono">agent_manager.py</span>) takes nearest neighbors by <span class="mono">cosine_distance(...).asc()</span>. The two-way vector column is in <span class="mono">letta/orm/passage.py</span> / <span class="mono">custom_columns.py</span> (<span class="mono">CommonVector</span>) and <span class="mono">sqlite_functions.py</span>; the dimension cap <span class="mono">MAX_EMBEDDING_DIM = 4096</span> is in <span class="mono">constants.py</span>; engine choice is <span class="mono">settings.database_engine</span>. Efficient tag queries use the <span class="mono">PassageTag</span> junction table (<span class="mono">letta/orm/passage_tag.py</span>). To pull the thread, start from the two tools' docstrings — they spell out "by meaning, not by keyword" and "add tags for later lookup," exactly the usage manual the agent reads in its prompt.
</div>

<h2>Dig a little deeper</h2>

<details class="accordion"><summary>Vector retrieval in a minute: what "search by meaning" means</summary><div class="acc-body">
<p><strong>Example:</strong> "dog" and "puppy" are worded differently but their vectors sit close; "dog" and "stock" sit far apart. Map each piece of text to a point in high-dimensional space, and <strong>close in meaning = close as points</strong>.</p>
<p><strong>Why it's designed this way:</strong> embedding models have learned from massive corpora and can compress meaning into coordinates. At search time the query is mapped to a point too, and finding the <strong>nearest</strong> points gives "the closest in meaning" — that's "search by meaning," not "by text."</p>
<p><strong>Where in the source:</strong> distance is cosine, <span class="mono">cosine_distance = 1 - cos(θ)</span> (<span class="mono">cosine_distance</span> in <span class="mono">letta/orm/sqlite_functions.py</span>); sorting is in <span class="mono">sqlalchemy_base.py</span>, <span class="mono">order_by(...asc())</span> taking the smallest distance.</p>
<p><strong>Alternatives:</strong> keyword search (BM25-style) matches literally, fast but helpless against synonyms/paraphrase; vector search captures meaning but has embedding cost and is "similar," not "exact." Each has strengths; they're often combined into hybrid retrieval.</p>
<p><strong>One more intuition:</strong> "dimensions" sound mystical but are just a few hundred to a few thousand numbers scoring a piece of text from different angles — one roughly "is it about money?", another "is the tone formal?". When two texts score alike on these, they sit near each other in space. You needn't know what each dimension is; just remember <strong>"near = alike."</strong></p>
</div></details>

<details class="accordion"><summary>pgvector or sqlite-vec? When to use which</summary><div class="acc-body">
<p><strong>Example:</strong> running a local demo or writing tests, not wanting to install Postgres — the default is SQLite + sqlite-vec, out of the box; going live with scale and indexes — set <span class="mono">letta_pg_uri</span> to switch to Postgres + pgvector.</p>
<p><strong>Why it's designed this way:</strong> dev wants <strong>zero friction</strong>; prod wants <strong>scalability</strong>. Making "vector column type" and "distance operator" two-way by engine satisfies both without touching upper code.</p>
<p><strong>Where in the source:</strong> engine decided by <span class="mono">settings.database_engine</span> (Postgres if <span class="mono">letta_pg_uri</span> is set, else SQLite); the column is defined in <span class="mono">BasePassage</span> in <span class="mono">letta/orm/passage.py</span>, SQLite using <span class="mono">CommonVector</span> and Postgres using <span class="mono">pgvector.Vector</span>.</p>
<p><strong>Alternatives:</strong> a dedicated vector store (e.g. Turbopuffer) — Letta supports it too; an archive can set <span class="mono">vector_db_provider</span> to use an external vector service; stronger retrieval/scale at the cost of one more external dependency.</p>
<p><strong>A number for scale:</strong> sqlite-vec is smooth locally up to tens of thousands of rows; but as archival grows to hundreds of thousands or millions, pgvector's nearest-neighbor indexes (like HNSW / IVFFlat) become essential — the real reason to "switch to Postgres in prod," not just multi-user concurrency, but keeping "find the nearest neighbor" fast on a big store.</p>
</div></details>

<details class="accordion"><summary>archive and tags: how the agent categorizes knowledge</summary><div class="acc-body">
<p><strong>Example:</strong> insert with <span class="mono">tags=["meetings","roadmap"]</span>; search with <span class="mono">tags=["meetings"], tag_match_mode="all"</span> to find by meaning only within meeting files.</p>
<p><strong>Why it's designed this way:</strong> pure semantic search is sometimes too "diffuse." tags give the agent a <strong>structured filter</strong>: scope by tag first, then rank by vector, for sharper recall. Each agent has one <strong>archive</strong> (store) by default holding all its Passages.</p>
<p><strong>Where in the source:</strong> the default archive comes from <span class="mono">ArchiveManager.get_or_create_default_archive_for_agent_async</span> (<span class="mono">archive_manager.py</span>); tags are stored both in <span class="mono">Passage.tags</span>'s JSON column and written to the <span class="mono">PassageTag</span> junction table (<span class="mono">letta/orm/passage_tag.py</span>) for efficient filter/count.</p>
<p><strong>Alternatives:</strong> it works without tags, all by semantics; but as knowledge grows and categories clarify, tags markedly improve "finding precisely." This is "semantics + structure" stacked.</p>
<p><strong>One more implementation detail:</strong> tags are <strong>dual-stored</strong> — both in <span class="mono">Passage.tags</span>'s JSON column (handy when fetching a Passage) and split into the <span class="mono">PassageTag</span> junction table (one row per tag). The former rides along with the data; the latter lets "filter/count by a tag" use an index and run fast. One piece of info, two layouts, each serving an access pattern.</p>
</div></details>

<details class="accordion"><summary>archival passage vs source passage: two kinds of Passage</summary><div class="acc-body">
<p><strong>Example:</strong> a note the agent <span class="mono">insert</span>s itself → <span class="mono">ArchivalPassage</span>; a PDF/document you upload that's chunked in → <span class="mono">SourcePassage</span>.</p>
<p><strong>Why it's designed this way:</strong> both are searchable "text + vector" fragments sharing <span class="mono">BasePassage</span>'s fields and vector column; but origin and ownership differ — one hangs on the agent's <strong>archive</strong>, written by the agent, the other on an <strong>external file/source</strong>. Two tables, each indexed, is cleaner.</p>
<p><strong>Where in the source:</strong> <span class="mono">letta/orm/passage.py</span>: <span class="mono">ArchivalPassage</span> (<span class="mono">archival_passages</span>, with <span class="mono">ArchiveMixin</span>) and <span class="mono">SourcePassage</span> (<span class="mono">source_passages</span>, with <span class="mono">FileMixin</span>/<span class="mono">SourceMixin</span>) both inherit <span class="mono">BasePassage</span>.</p>
<p><strong>Alternatives:</strong> one table with a "source" field works too, but separate tables let "memories the agent wrote" and "material poured in" evolve and index independently. This lesson focuses on the former.</p>
</div></details>

<h2>Next stop: from "long-term vector store" back to "conversation history"</h2>
<p>This lesson nailed the "farthest" of the three tiers: archival is a <strong>long-term vector store</strong> the agent runs itself, written by <span class="mono">insert</span> and read by <span class="mono">search</span> by meaning, with a "two-way" vector column underneath. It pulls RAG into the agent's own hands.</p>

<div class="note info"><span class="ni">👉</span><span class="nx"><strong>Preview of Lesson 11:</strong> archival is the agent's <strong>curated</strong> long-term store (searched by meaning), while recall is the system's <strong>auto-logged</strong> full conversation history (hybrid retrieval). Next lesson covers recall — how each message is persisted as a typed JSON event, and how <span class="mono">conversation_search</span> fetches it back.</span></div>

<p>Further on, <strong>Lesson 12</strong> returns to Lesson 5's "context window" wall: when the window nears full, how older messages get <strong>compacted into a summary</strong> and swapped out — the very path Lesson 9 ended on, "after compaction it force-rebuilds message #0." Three tiers of memory + one compaction, and Part 3 closes the loop.</p>

<p>On the way out, recite the chain once: <strong>text → embed → Passage(vector) → store</strong> is the write, <strong>query → embed → nearest neighbors → Top-K</strong> is the read, with <span class="mono">cosine_distance</span> measuring "how alike" in between, and a "two-way vector column" switching seamlessly between laptop and prod underneath. Memorize those four steps, plus the warning "<strong>similar isn't exact, and every call embeds</strong>," and this tier is truly in your hands.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>archival = RAG built into the agent</strong>: an out-of-window long-term vector store, near-infinite capacity, searched <strong>by meaning</strong>; the agent <span class="mono">insert</span>s and <span class="mono">search</span>es itself.</li>
    <li><strong>Passage</strong>: one archival memory = <span class="mono">text</span> + <span class="mono">embedding</span> (vector) + <span class="mono">embedding_config</span> + <span class="mono">tags</span> (<span class="mono">letta/schemas/passage.py</span>).</li>
    <li><strong>Two tools</strong>: <span class="mono">archival_memory_insert</span> delegates to <span class="mono">PassageManager.insert_passage</span> (embed + store); <span class="mono">archival_memory_search</span> takes nearest neighbors by <span class="mono">cosine_distance(...).asc()</span> (<span class="mono">core_tool_executor.py</span>).</li>
    <li><strong>Dual-dialect vector column</strong>: dev SQLite + <span class="mono">CommonVector</span>/sqlite-vec, prod Postgres + <span class="mono">pgvector.Vector(4096)</span>, auto-chosen by <span class="mono">settings.database_engine</span> — <strong>upper layer unchanged</strong>.</li>
    <li><strong>search is "similar," not "exact,"</strong> and <strong>every insert/search costs an embedding call</strong> (a cost) — store self-contained facts, search on demand.</li>
    <li><strong>tags</strong>: categorize knowledge; search filters by tag first, then ranks by meaning (the <span class="mono">PassageTag</span> junction table).</li>
  </ul>
</div>
""",
}


LESSON_11 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第 7 课那张三层地图里，recall（回忆）是中间那一层：它在上下文窗口<strong>之外</strong>，却收着<strong>每一句说过的话</strong>。第 10 课的 archival 是 agent <strong>精选</strong>的长期笔记，这一课的 recall 则是系统<strong>自动记下</strong>的完整对话历史——一句都不漏。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
关键词只有三个：<strong>Message</strong>（一条消息 = 一行可持久、可检索的记录）、<strong>message_ids</strong>（决定哪几条"在窗内"）、<strong>conversation_search</strong>（把窗外的旧消息按 hybrid 检索捞回）。读完你会明白：对话<strong>从不丢失</strong>，只是没都摆在眼前。</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  <strong>把 recall 想成一卷从不停录的完整录像，把"在窗消息"想成屏幕上正在回放的最近几分钟。</strong>摄像机从第一句话起就一直在录，每个画面都存进了硬盘——这就是 recall：<strong>全部对话历史</strong>，系统自动记、一帧不丢。但你的屏幕装不下整卷录像，只能显示<strong>最近一小段</strong>，这一小段就是"在窗"的消息。更早的画面没有消失，它们好端端躺在硬盘里；你想看，只要<strong>去检索那一段</strong>，就能把它调回屏幕。所以"看不见"绝不等于"没了"——录像一直都在，区别只是<strong>当前在播哪一段</strong>。记住这卷录像，你就能分清两件最常被搞混的事：<strong>哪些在眼前</strong>，和<strong>一共录了多少</strong>。前者由屏幕（窗口）决定，后者由硬盘（recall 全量）决定，两者从来不是一回事。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  <strong>一句话抓住本课：recall = 一份系统自动记的 <span class="mono">Message</span> 全量日志，agent 只在 <span class="mono">message_ids</span> 指着的"最近一段"上推理，需要更早的就用 <span class="mono">conversation_search</span> 捞。</strong>每说一句话，Letta 都把它存成一行 <span class="mono">Message</span>（带 role、时间、内容），永久落库；<span class="mono">AgentState.message_ids</span> 是一串指针，圈出当前在窗的那几条，第 0 条永远是系统消息。窗口装不下整部历史，于是较旧的消息被移出 <span class="mono">message_ids</span>，但<strong>仍留在库里可搜</strong>。要回忆，agent 调 <span class="mono">conversation_search</span>，按 hybrid（字面 + 语义）把旧消息捞回。看懂这条主线，recall 就不神秘：它不过是"全都记下来、只让最近一段在窗、其余按需搜回"。这也是它和 archival 最大的不同——archival 由 agent 挑着记，recall 替你无差别地全记下。
</div>

<h2>先把 recall 摆回三层地图</h2>
<p>第 7 课分过三层的工：<strong>core</strong> 在窗、最稀缺、agent 自改；<strong>archival</strong>（第 10 课）是 agent 精选的长期向量库；<strong>recall</strong> 则是系统<strong>自动记</strong>的完整对话历史。这一课只聚焦 recall 这一层。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>一句话定位：</strong>recall 是<strong>系统替你记的流水账</strong>——你不用调任何工具，每条消息都被自动存成 <span class="mono">Message</span>；要用时再 <span class="mono">conversation_search</span> 捞回。<strong>写是自动的，读才靠工具。</strong></span></div>

<p>recall 和 archival 最容易被搞混。它们<strong>都在窗外、都能搜</strong>，但区别不在"怎么搜"，而在<strong>存什么、谁来写</strong>：recall 是系统自动记的<strong>全量对话</strong>，archival 是 agent 主动写的<strong>精选笔记</strong>。下面这张表并排对清楚。</p>

<table class="t">
  <thead><tr><th>对照项</th><th>recall 回忆</th><th>archival 归档</th></tr></thead>
  <tbody>
    <tr><td>存什么</td><td>全部对话消息（原样）</td><td>agent 提炼的事实 / 摘要</td></tr>
    <tr><td>谁来写</td><td><strong>系统自动</strong>记每一条</td><td><strong>agent 主动</strong> insert</td></tr>
    <tr><td>在上下文?</td><td>仅 <span class="mono">message_ids</span> 指的最近一段</td><td>全在窗外</td></tr>
    <tr><td>怎么检索</td><td><span class="mono">conversation_search</span> · <strong>hybrid（字面+语义）</strong></td><td><span class="mono">archival_memory_search</span> · 按语义</td></tr>
    <tr><td>容量</td><td>全量历史</td><td>近乎无限</td></tr>
  </tbody>
</table>

<p>记住这条铁律：<strong>区别在"存什么 / 谁写"，不在"字面 vs 语义"</strong>。两层其实都带语义检索——recall 的 <span class="mono">conversation_search</span> 是 hybrid（字面 + 语义），archival 是纯语义。真正分野是：recall 替你<strong>无差别记下一切</strong>，archival 由 agent <strong>挑着记</strong>。</p>

<p>为什么这两层要分开？因为它们答的是两个不同的问题。recall 答<strong>"我们到底说过什么"</strong>——要的是原话、要完整、要可追溯；archival 答<strong>"关于这件事我总结过什么"</strong>——要的是提炼后的结论。把"原始流水"和"提炼笔记"拆成两层，找原话不会被结论淹没，找结论也不必在海量原话里大海捞针。</p>

<div class="cute"><div class="row"><span class="emoji">🎞️</span><span class="bubble">完整录像 = 全量 Message</span><span class="arrow">→</span><span class="emoji">🪟</span><span class="lab">在窗最近一段</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="bubble">搜回更早的</span></div>
<div class="cap">回忆记忆 = 一直在录的对话录像；屏幕只放最近一段，旧片段搜一下就回来</div></div>

<p>这张对照表里最该背下的一行是<strong>"谁来写"</strong>：recall 是<strong>系统</strong>在你背后自动记的，agent 连手都不用抬；archival 是 agent <strong>自己</strong>动手挑着写的。一个被动全收，一个主动精选——记住这一条，胜过记十个细节。</p>

<h2>一条消息 = 一行 Message</h2>
<p>recall 的最小单位是 <span class="mono">Message</span>（<span class="mono">letta/schemas/message.py</span>）。你、agent、工具说的每一句，都是一行 <span class="mono">Message</span>：它有角色、有内容、有时间戳，存进库就<strong>永久在那</strong>。</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/message.py · schemas/agent.py</span><span class="ln">Message 关键字段 + message_ids（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">Message</span>(BaseMessage):
    id: str                          <span class="cm"># 一条消息的唯一 id</span>
    role: MessageRole                <span class="cm"># system / user / assistant / tool / summary</span>
    content: Optional[List[...]]     <span class="cm"># 这条消息的正文</span>
    tool_calls: Optional[List[...]]  <span class="cm"># assistant 发起的工具调用</span>
    tool_call_id: Optional[str]      <span class="cm"># role=tool 时，对应哪一次调用</span>
    created_at: datetime             <span class="cm"># 时间戳：什么时候说的</span>
    agent_id: Optional[str]          <span class="cm"># 属于哪个 agent</span>

<span class="cm"># letta/schemas/agent.py —— 哪些 Message 当前在窗</span>
<span class="kw">class</span> <span class="fn">AgentState</span>(...):
    message_ids: Optional[List[str]]  <span class="cm"># 在窗消息的 id；[0] 永远是系统消息</span>
</pre></div>

<p>几件事串起整课：<strong>role</strong> 标明谁说的（注意还有 <span class="mono">summary</span> 这个角色，第 12 课会用到）；<strong>content</strong> 是正文；<strong>tool_calls / tool_call_id</strong> 让"调用工具"和"工具返回"也都成为<strong>结构化的消息</strong>，而不是夹在文本里；<strong>created_at</strong> 让"按时间检索"成为可能。</p>

<p>换句话说，recall 里的 role 是一份"<strong>角色表</strong>"：<span class="mono">user</span>（人）、<span class="mono">assistant</span>（agent 本体）、<span class="mono">tool</span>（工具返回）、<span class="mono">system</span>（系统提示）、<span class="mono">summary</span>（压缩摘要）。同一段历史里，谁说的、是话还是工具结果，靠 role 一眼分清——这是"结构化事件"能成立的地基。</p>

<div class="note info"><span class="ni">📌</span><span class="nx"><strong>Message 是持久的，不是临时的。</strong>它由 <span class="mono">MessageManager</span>（<span class="mono">letta/services/message_manager.py</span>）负责落库与取回。一旦写下，就算被移出窗口，行还在表里——这正是"对话从不丢失"的物理保证。</span></div>

<p>谁来写这些 Message？<strong>不是 agent，是系统</strong>。每走一步（第 3 课的 step 循环），新产生的消息都由 <span class="mono">MessageManager</span> 自动落库、并追加进 <span class="mono">message_ids</span>。agent <strong>无需调用任何"保存"工具</strong>——这正是 recall 与 archival 的根本区别：archival 要 agent 主动 <span class="mono">insert</span>，recall 是后台默默全记。</p>

<h2>message_ids：在窗的那一小段</h2>
<p>全量 Message 躺在库里，但模型每轮只读得到 <span class="mono">message_ids</span> 圈出的那几条。<span class="mono">message_ids</span> 是一串<strong>指针</strong>（id 列表），不是消息本身——它指向"现在该把哪几行摆进上下文"。</p>

<div class="cellgroup">
  <div class="cg-cap"><b>message_ids ⊂ 全部 Message</b>：在窗的只是全量日志的一个尾巴</div>
  <div class="cells">
    <span class="cell hl">[0] 系统消息 · 永远在窗</span>
    <span class="sep">·</span>
    <span class="cell q">更早的消息 · 在库里、不在 message_ids</span>
    <span class="sep">·</span>
    <span class="cell">最近一段 · message_ids 指着、在窗可见</span>
  </div>
</div>

<p>窗口快满时，较旧的消息会被<strong>移出</strong> <span class="mono">message_ids</span>——但只是从"在窗指针"里去掉，<span class="mono">Message</span> 行<strong>原封不动留在库里</strong>。增删都只动这串指针，不搬真正的消息行：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>窗口快满</h4><p>在窗 token 逼近预算（第 5 课），旧消息必须让位。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>trim 掉较旧的</h4><p>从 <span class="mono">message_ids</span> 去掉前面几条，<strong>保留第 0 条系统消息</strong>。</p><span class="mono">trim_older_in_context_messages</span></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>原话仍留库</h4><p>被移出 ≠ 被删除，<span class="mono">Message</span> 行还在表里。</p><span class="mono">message_manager.py</span></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>需要时搜回</h4><p>用 <span class="mono">conversation_search</span> 把旧消息按 hybrid 捞回窗内。</p></div></div>
</div>

<p>新消息进来则相反：<span class="mono">append_to_in_context_messages</span> 把它追加到 <span class="mono">message_ids</span> 末尾。整体替换用 <span class="mono">set_in_context_messages</span>。三个动作都只改指针，<strong>极轻</strong>——这也是把"在窗消息"做成 id 列表而非整列对象的好处。</p>

<p>一个好记的画面：<span class="mono">message_ids</span> 像录像机的<strong>播放头</strong>——它在整卷录像（全量 Message）上滑动，决定"此刻屏幕上放哪一段"。播放头往后移，前面的画面退出屏幕，但<strong>胶片一格没少</strong>，随时能倒回去看。</p>

<h2>消息不是裸文本：带类型的 JSON 事件</h2>
<p>这里有个容易被忽略的关键：进入上下文的消息<strong>不是裸文本</strong>。每条在被模型读到之前，都被 <span class="mono">letta/system.py</span> 包成一个<strong>带类型的 JSON 事件</strong>，标明"这是什么、什么时候发生的"。</p>

<p>这些信封长得很像：都是一个小 JSON 对象，至少有 <span class="mono">type</span>（或 <span class="mono">status</span>）和 <span class="mono">time</span> 两个字段，再加一个装正文的 <span class="mono">message</span>。统一的形状让"打包 / 拆包 / 按类型分流"都有章可循。</p>

<div class="cols">
  <div class="col"><h4>❌ 如果是裸文本</h4><p>"你好" / "天气晴" / "OK"——模型得自己猜：谁说的？是用户、工具返回、还是系统提醒？信息全糊在一起。</p></div>
  <div class="col"><h4>✅ Letta 的 JSON 信封</h4><p>每条带 <span class="mono">type</span> 和 <span class="mono">time</span>：<span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span>——一眼分清来路与时间。</p></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/system.py</span><span class="ln">每条消息都包成带类型的 JSON 事件（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">package_user_message</span>(user_message, timezone, ...):
    <span class="kw">return</span> json_dumps({
        <span class="st">"type"</span>: <span class="st">"user_message"</span>,   <span class="cm"># 事件类型</span>
        <span class="st">"message"</span>: user_message,     <span class="cm"># 用户说的话</span>
        <span class="st">"time"</span>: formatted_time,       <span class="cm"># 本地时间</span>
    })

<span class="kw">def</span> <span class="fn">package_function_response</span>(was_success, response_string, timezone):
    <span class="kw">return</span> json_dumps({
        <span class="st">"status"</span>: <span class="st">"OK"</span> <span class="kw">if</span> was_success <span class="kw">else</span> <span class="st">"Failed"</span>,
        <span class="st">"message"</span>: response_string,   <span class="cm"># 工具执行的返回</span>
        <span class="st">"time"</span>: formatted_time,
    })

<span class="kw">def</span> <span class="fn">get_heartbeat</span>(timezone, reason=<span class="st">"Automated timer"</span>, ...):
    <span class="kw">return</span> json_dumps({<span class="st">"type"</span>: <span class="st">"heartbeat"</span>, <span class="st">"reason"</span>: reason, <span class="st">"time"</span>: ...})
</pre></div>

<p>三类最常见的事件：<strong>user_message</strong>（用户说的话）、<strong>function_response</strong>（工具执行的返回，带 <span class="mono">status</span>）、<strong>heartbeat</strong>（系统定时唤醒 agent 的"心跳"）。它们都带 <span class="mono">time</span>，于是"按时间检索"和"知道多久以前"都成了可能。</p>

<p>三类里 <span class="mono">heartbeat</span> 最特别：它不是谁说的话，而是系统<strong>定时唤醒</strong> agent 的一次"心跳"，让它在没有用户输入时也有机会主动接着做事。心跳同样是一条带 <span class="mono">type</span> 的 JSON 事件，照样进 recall、照样可搜——连"系统什么时候戳了它一下"都留了痕。</p>

<div class="note info"><span class="ni">👉</span><span class="nx">取回时还有一步<strong>拆包</strong>：<span class="mono">unpack_message</span>（<span class="mono">letta/system.py</span>）把信封拆开、取出内层文本——但它<strong>只对 <span class="mono">user_message</span></strong> 这么做，其余类型原样保留，好让结构信息不丢。</span></div>

<h2>conversation_search：把旧消息按 hybrid 捞回</h2>
<p>窗外的旧消息怎么找回来？靠 <span class="mono">conversation_search</span>（<span class="mono">core_tool_executor.py</span>）。agent 给一个查询，它就去<strong>整部对话史</strong>里捞最相关的几条，端回窗内。</p>

<div class="note tip"><span class="ni">✅</span><span class="nx"><strong>conversation_search 是 hybrid 检索。</strong>它的工具说明（<span class="mono">letta/functions/function_sets/base.py</span>）原话就是 "hybrid search (text + semantic similarity)"——<strong>字面 + 语义一起上</strong>，所以换了措辞也能命中，<strong>不是</strong>纯关键词匹配。</span></div>

<div class="flow">
  <div class="node"><div class="nt">query</div><div class="nd">"上次聊的续约"</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">hybrid 检索</div><div class="nd">字面 + 语义</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">滤掉 tool 消息</div><div class="nd">避免递归嵌套</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Top-K 旧消息</div><div class="nd">带时间戳 + "Xd ago"</div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">conversation_search（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">conversation_search</span>(self, agent_state, actor, query=<span class="kw">None</span>,
                              roles=<span class="kw">None</span>, limit=<span class="kw">None</span>,
                              start_date=<span class="kw">None</span>, end_date=<span class="kw">None</span>):
    <span class="cm"># 委托给 message_manager，默认 search_mode="hybrid"（字面 + 语义）</span>
    message_results = <span class="kw">await</span> self.message_manager.<span class="fn">search_messages_async</span>(
        agent_id=agent_state.id, actor=actor,
        query_text=query, roles=..., limit=search_limit,
        start_date=..., end_date=...)
    <span class="cm"># 滤掉 tool 消息 + "调用 conversation_search 本身"的那条，避免递归</span>
    <span class="cm"># 给每条标上时间戳与 "Xd ago"，再返回</span>
    <span class="kw">return</span> formatted_results
</pre></div>

<p>两个细节值得记。其一：它默认走 <strong>hybrid</strong>——委托 <span class="mono">search_messages_async(search_mode="hybrid")</span>，字面与语义一起算，所以换了措辞也搜得到。其二：它会<strong>滤掉 tool 消息</strong>、以及"调用 conversation_search 本身"的那条 assistant 消息，避免把搜索结果层层嵌套、越转义越乱。</p>

<p>还能按<strong>角色和时间</strong>过滤：<span class="mono">roles=["user"]</span> 只搜用户说的，<span class="mono">start_date</span> / <span class="mono">end_date</span> 圈定时间窗。返回的每条都带<strong>时间戳和 "Xd ago"</strong>，让 agent 知道这话是"多久以前"说的。</p>

<p>取几条由 <span class="mono">limit</span> 决定；不传时回退到系统默认页大小 <span class="mono">RETRIEVAL_QUERY_DEFAULT_PAGE_SIZE</span>。和 archival 一样，<strong>搜回来的每条都要占回上下文 token</strong>——所以它是"按需捞回一小撮"，不是"把历史整卷摊开"。</p>

<h2>一个真实场景：三周后还能想起那句话</h2>
<p>把机制串成一个故事。三周前，用户随口说过一句"我们公司财年从 7 月开始"。当时这只是一条普通的 <span class="mono">user_message</span>，被存成一行 <span class="mono">Message</span>，随对话推进慢慢滑出了窗口。</p>

<p>今天用户说："帮我把季度复盘排进日历。"agent 要排日历，得先知道财年起点——可那句话早不在窗内了。于是它调 <span class="mono">conversation_search</span>，查询写"公司财年 / 季度起点"。</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">注意查询里<strong>一个原词都没对上</strong>："财年从 7 月开始" 对 查询"季度起点"。纯关键词会扑空——但 <span class="mono">conversation_search</span> 是 <strong>hybrid</strong>，语义那一路把它稳稳捞了回来。</span></div>

<p>那条三周前的 <span class="mono">Message</span> 被端回窗内，还带着 "21d ago" 的时间标注。agent 读到"财年 7 月起"，于是把季度复盘排进了正确的月份。<strong>对话从没丢，它只是一直等着被搜回来。</strong></p>

<p>有人会问：这种"想起旧事"，为什么不交给 archival？因为那句话 agent <strong>当时并没判断它值得长期记</strong>，自然没 insert 进 archival。但 recall <strong>无差别地全记了</strong>——正是这种"先全记下、用时再搜"的兜底，让 agent 不会因为"当时没多想"而彻底丢掉信息。</p>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>对话从不丢失——而且它不是一堆裸文本，是一串带类型的 JSON 事件。</strong>两件事叠在一起，才是 recall 的真正威力。第一：每条消息都是一行可持久、可检索的 <span class="mono">Message</span>，写下就永远在库里；窗口里只留 <span class="mono">message_ids</span> 指着的最近一段，其余<strong>看不见但搜得到</strong>。第二：消息进入上下文前，都被 <span class="mono">letta/system.py</span> 包成<strong>带类型的事件</strong>——<span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span> 各有 <span class="mono">type</span> 和 <span class="mono">time</span>。于是 agent 不是在读一段流水文字，而是在<strong>一连串结构化事件</strong>上推理：它分得清"这是用户说的""这是工具返回的""这是定时心跳"。把这两点合起来：一部<strong>永不丢失、可按 hybrid 搜回、且每条都自带语义类型</strong>的对话史——agent 既不会"忘了说过什么"，也不会"分不清谁说的"。这正是 MemGPT 把"对话历史"也当成一等记忆来管的关键：历史不是日志垃圾堆，而是<strong>可推理、可检索的结构化记忆</strong>——也正因如此，agent 才能在三周后、十几轮对话之后，依然精准引用你随口说过的一句话。
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>"在窗" ≠ "全部历史"——别把眼前这几条当成对话的全部。</strong>模型每轮直接读到的，只有 <span class="mono">message_ids</span> 圈出的最近一段；更早的消息<strong>可搜，但不可见</strong>。这带来两个要命的误判。其一：以为"模型没提到 = 它忘了"。不一定——它可能只是没去搜；那条消息还在库里躺着，<span class="mono">conversation_search</span> 一下就回来了。其二：以为"反正都记着，可以无脑翻历史"。也不对——搜回来的消息要<strong>占回上下文 token</strong>，而且 hybrid 搜是有成本的检索，不是免费的全文摊开。正确姿势是：把"在窗的最近一段"当工作台面，把"窗外全量历史"当随时可查的档案——<strong>需要时才搜，搜了才可见</strong>。还有一个细节别忘：被移出窗口<strong>不等于</strong>被删除，<span class="mono">Message</span> 行一直都在，所以"看不见"从来不是"没了"，只是"暂时没摆上台面"。
</div>

<div class="card detail">
  <div class="tag">🔬 落到代码</div>
  <strong>整条链路的源码坐标。</strong>数据模型 <span class="mono">Message</span>（role / content / tool_calls / created_at）在 <span class="mono">letta/schemas/message.py</span>；落库与取回由 <span class="mono">MessageManager</span>（<span class="mono">letta/services/message_manager.py</span>）负责。在窗指针 <span class="mono">message_ids</span> 在 <span class="mono">letta/schemas/agent.py::AgentState</span>，<span class="mono">[0]</span> 永远是系统消息；增删在 <span class="mono">agent_manager.py</span> 的 <span class="mono">append_to_in_context_messages</span> / <span class="mono">trim_older_in_context_messages</span> / <span class="mono">set_in_context_messages</span>。JSON 信封在 <span class="mono">letta/system.py</span>：<span class="mono">package_user_message</span> / <span class="mono">package_function_response</span> / <span class="mono">get_heartbeat</span> / <span class="mono">package_summarize_message</span>，取回时 <span class="mono">unpack_message</span> 拆出内层文本。检索工具 <span class="mono">conversation_search</span> 在 <span class="mono">core_tool_executor.py</span>，委托 <span class="mono">MessageManager.search_messages_async</span>（默认 <span class="mono">search_mode="hybrid"</span>），docstring 声明在 <span class="mono">functions/function_sets/base.py</span>，原话 "hybrid search (text + semantic similarity)"。顺着这几个符号读，你能把"一句话怎么从输入变成可搜的历史"完整走通。
</div>

<h2>再挖深一点</h2>

<details class="accordion"><summary>为什么用 JSON 信封，而不是直接塞裸文本</summary><div class="acc-body">
<p><strong>示例：</strong>用户说"你好"，进上下文的不是 <span class="mono">你好</span> 三个字，而是 <span class="mono">{"type":"user_message","message":"你好","time":"..."}</span>。</p>
<p><strong>为什么这样设计：</strong>裸文本会把"谁说的、什么时候、是不是工具结果"全糊在一起，模型只能猜。包成带 <span class="mono">type</span> 的事件后，它一眼分清 <span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span>，推理更稳。</p>
<p><strong>源码在哪：</strong><span class="mono">letta/system.py</span> 的 <span class="mono">package_*</span> 系列负责"打包"，<span class="mono">unpack_message</span> 负责取回时"拆包"（只对 <span class="mono">user_message</span> 拆出内层文本）。</p>
<p><strong>还有什么替代：</strong>也可用特殊前缀（如 <span class="mono">User:</span> / <span class="mono">Tool:</span>），但 JSON 更结构化、好扩展——加 <span class="mono">location</span>、<span class="mono">name</span> 等字段不破坏旧格式。</p>
</div></details>

<details class="accordion"><summary>窗内消息怎么管理：append、trim、set</summary><div class="acc-body">
<p><strong>示例：</strong>新消息进来 → 追加到 <span class="mono">message_ids</span> 末尾；窗口要瘦身 → 砍掉较旧的几条，但保留第 0 条系统消息。</p>
<p><strong>为什么这样设计：</strong>把"在窗有哪些"做成一串可改的 id 指针，增删极轻——不用搬动真正的 <span class="mono">Message</span> 行，只动指针。</p>
<p><strong>源码在哪：</strong><span class="mono">agent_manager.py</span> 的 <span class="mono">append_to_in_context_messages</span>（追加）、<span class="mono">trim_older_in_context_messages(num)</span>（保留 <span class="mono">[0]</span>、丢前面较旧的）、<span class="mono">set_in_context_messages</span>（整体替换）。</p>
<p><strong>还有什么替代：</strong>直接存整列消息对象也行，但存 id 指针更省、且让"同一条消息被多处引用"成为可能。第 0 条恒为系统消息，是第 9 课"重建第 0 条"的前提。</p>
</div></details>

<details class="accordion"><summary>recall vs archival：都能搜，差别到底在哪</summary><div class="acc-body">
<p><strong>示例：</strong>"用户三周前抱怨过发货慢"是说过的原话，属 recall，用 <span class="mono">conversation_search</span> 搜；"用户对花生过敏"被 agent 提炼成长期事实写进 archival，用 <span class="mono">archival_memory_search</span> 搜。</p>
<p><strong>为什么这样设计：</strong>一个是<strong>系统自动记的原始流水</strong>，一个是<strong>agent 主动挑的提炼笔记</strong>。分开后，"找原话"和"找结论"各走各的层，互不污染。</p>
<p><strong>源码在哪：</strong>recall 搜 <span class="mono">conversation_search</span> → <span class="mono">search_messages_async</span>（<span class="mono">message_manager.py</span>）；archival 搜 <span class="mono">archival_memory_search</span> → <span class="mono">cosine_distance</span> 最近邻（第 10 课）。</p>
<p><strong>别记反了：</strong>区别<strong>不是</strong>"recall 按字面、archival 按语义"。两者都带语义：recall 是 hybrid（字面+语义），archival 是纯语义。真正分野是<strong>存什么 / 谁来写</strong>。</p>
</div></details>

<details class="accordion"><summary>summary 消息：被压缩的历史也还在 recall 里</summary><div class="acc-body">
<p><strong>示例：</strong>窗口压力大时，较旧的一批消息被<strong>压成一段摘要</strong>塞回上下文，原话则退到窗外——但它们仍是库里的 <span class="mono">Message</span>，仍可搜。</p>
<p><strong>为什么这样设计：</strong>压缩是为了省 token，不是为了删历史。摘要让"要点"留在眼前，原始消息留在 recall 备查，两不耽误。</p>
<p><strong>源码在哪：</strong>摘要由 <span class="mono">letta/system.py::package_summarize_message</span> 打包成 <span class="mono">system_alert</span> 事件；<span class="mono">Message</span> 的 role 取值里本就有 <span class="mono">summary</span> 一项。</p>
<p><strong>预告第 12 课：</strong>"什么时候压、压哪些、摘要怎么生成"是下一课的主题（<span class="mono">letta/services/summarizer/</span>）。这里只需记住：<strong>压缩 ≠ 丢失</strong>，被换出的原话依旧躺在 recall 里。</p>
</div></details>

<h2>下一站：从"记得住"到"装得下"</h2>
<p>这一课你拿下了三层里最"全"的一层：recall 是系统自动记的<strong>完整对话史</strong>，每条都是可持久、可检索的 <span class="mono">Message</span>；<span class="mono">message_ids</span> 圈出在窗的一段，其余用 <span class="mono">conversation_search</span> 按 hybrid 捞回。</p>

<div class="note info"><span class="ni">👉</span><span class="nx"><strong>预告第 12 课：</strong>recall 保证"不丢"，但窗口仍然有限。当在窗消息逼近 token 预算，Letta 会把较旧的一批<strong>压缩成摘要</strong>换出去——也就是第 9 课结尾说的"压缩后强制重建第 0 条"。下一课讲<strong>上下文压缩与"记忆压力"</strong>。</span></div>

<p>把第三部分串起来：core 让 agent <strong>改写自己是谁</strong>（07–09），archival 让它<strong>积累长期知识</strong>（10），recall 让它<strong>记得说过的每句话</strong>（11），而压缩（12）让这一切在有限窗口里<strong>转得动</strong>。四块拼齐，记忆系统就闭环了。</p>

<p>回头看第 3 课那条"消息的生命周期"：一条消息从 POST 进来，被 agent 处理、持久化、再响应——它<strong>落库的那一刻</strong>就成了 recall 的一员。所以 recall 不是某个独立模块，而是<strong>每条消息生命周期的自然归宿</strong>：说过的就记下了，记下的就能搜回。</p>

<p>临走默背一条链：<strong>说一句话 → 包成 JSON 事件 → 存为 Message 行 → message_ids 圈出在窗的一段 → 旧的换出但留库 → 要回忆就 conversation_search（hybrid）捞回</strong>。把这条链记牢，再记住"<strong>看不见 ≠ 没了</strong>"这一句，recall 这层你就真正握住了。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>recall = 系统自动记的全量对话史</strong>：每条消息都是可持久、可检索的 <span class="mono">Message</span>（<span class="mono">letta/schemas/message.py</span>），由 <span class="mono">MessageManager</span> 落库；写是自动的。</li>
    <li><strong>message_ids = 在窗指针</strong>（<span class="mono">AgentState</span>）：只圈出最近一段，<span class="mono">[0]</span> 永远是系统消息；增删走 <span class="mono">append</span> / <span class="mono">trim_older</span> / <span class="mono">set_in_context</span>。</li>
    <li><strong>消息是带类型的 JSON 事件</strong>：<span class="mono">letta/system.py</span> 把每条包成 <span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span>（带 <span class="mono">type</span> + <span class="mono">time</span>），agent 在结构化事件上推理。</li>
    <li><strong>conversation_search 是 hybrid（字面 + 语义）</strong>：在 <span class="mono">core_tool_executor.py</span>，委托 <span class="mono">search_messages_async</span>；docstring 原话 "hybrid search (text + semantic similarity)"。</li>
    <li><strong>"在窗" ≠ "全部历史"</strong>：旧消息<strong>可搜不可见</strong>，被换出 ≠ 被删除；搜回来要占回 token。</li>
    <li><strong>recall vs archival 的真分野</strong>：在"<strong>存什么 / 谁来写</strong>"（recall 系统记全量、archival agent 挑着记），不在"字面 vs 语义"。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
In Lesson 7's three-tier map, recall sits in the middle: it lives <strong>outside</strong> the context window, yet it keeps <strong>every single thing ever said</strong>. Lesson 10's archival is the agent's <strong>curated</strong> long-term notes; this lesson's recall is the system's <strong>auto-logged</strong> full conversation history — not one line dropped.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">
Just three keywords: <strong>Message</strong> (one message = one durable, searchable row), <strong>message_ids</strong> (which few are "in-window"), and <strong>conversation_search</strong> (pulls old out-of-window messages back by hybrid search). By the end you'll see: the conversation is <strong>never lost</strong> — it just isn't all laid out in front of you.</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  <strong>Picture recall as a never-stopping full recording, and "in-window messages" as the last few minutes currently replaying on screen.</strong> The camera has been rolling since the first word, every frame saved to disk — that's recall: <strong>the entire conversation history</strong>, auto-logged by the system, not a frame missing. But your screen can't hold the whole reel; it shows only <strong>the most recent slice</strong>, and that slice is the "in-window" messages. The earlier frames didn't vanish — they sit safely on disk; to see them you just <strong>search that segment</strong> and it's back on screen. So "not visible" is never "gone" — the recording is always there; the only question is <strong>which segment is playing now</strong>. Remember this reel and you'll separate the two things people most often confuse: <strong>what's in front of you</strong>, and <strong>how much was recorded in total</strong>. The former is set by the screen (the window), the latter by the disk (recall's full log) — never the same thing.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  <strong>Grab this lesson in one line: recall = a system-auto-logged full <span class="mono">Message</span> log; the agent reasons only over the "recent slice" that <span class="mono">message_ids</span> points to, and uses <span class="mono">conversation_search</span> to fetch anything older.</strong> Every utterance, Letta stores as one <span class="mono">Message</span> row (with role, time, content), persisted forever; <span class="mono">AgentState.message_ids</span> is a list of pointers marking what's currently in-window, and index 0 is always the system message. The window can't hold the whole history, so older messages drop out of <span class="mono">message_ids</span> but <strong>stay in the store, searchable</strong>. To recall, the agent calls <span class="mono">conversation_search</span>, fetching old messages by hybrid (text + meaning). See this main line and recall loses its mystery: it's just "log everything, keep only the recent slice in-window, fetch the rest on demand." That's also its biggest difference from archival — archival is curated by the agent; recall logs everything for you, indiscriminately.
</div>

<h2>First, put recall back on the three-tier map</h2>
<p>Lesson 7 split the labor: <strong>core</strong> is in-window, scarcest, self-edited; <strong>archival</strong> (Lesson 10) is the agent's curated long-term vector store; <strong>recall</strong> is the system's <strong>auto-logged</strong> full conversation history. This lesson focuses on recall alone.</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>One-line placement:</strong> recall is <strong>the ledger the system keeps for you</strong> — you call no tool; every message is auto-stored as a <span class="mono">Message</span>; you reach for <span class="mono">conversation_search</span> only to read it back. <strong>Writing is automatic; only reading needs a tool.</strong></span></div>

<p>recall and archival are the easiest pair to confuse. They're <strong>both out-of-window and both searchable</strong>, but the difference isn't "how you search" — it's <strong>what's stored and who writes it</strong>: recall is the system's auto-logged <strong>full conversation</strong>, archival is the agent's actively-written <strong>curated notes</strong>. The table lines them up.</p>

<table class="t">
  <thead><tr><th>Aspect</th><th>recall</th><th>archival</th></tr></thead>
  <tbody>
    <tr><td>Stores what</td><td>all conversation messages (verbatim)</td><td>agent-distilled facts / summaries</td></tr>
    <tr><td>Who writes</td><td><strong>system, automatically</strong>, every message</td><td><strong>agent, actively</strong> inserts</td></tr>
    <tr><td>In context?</td><td>only the recent slice <span class="mono">message_ids</span> points to</td><td>all out-of-window</td></tr>
    <tr><td>How retrieved</td><td><span class="mono">conversation_search</span> · <strong>hybrid (text+meaning)</strong></td><td><span class="mono">archival_memory_search</span> · by meaning</td></tr>
    <tr><td>Capacity</td><td>full history</td><td>near-infinite</td></tr>
  </tbody>
</table>

<p>Memorize this rule: <strong>the difference is "what's stored / who writes," not "literal vs semantic."</strong> Both tiers carry semantic retrieval — recall's <span class="mono">conversation_search</span> is hybrid (text + meaning), archival is pure semantic. The real split: recall logs <strong>everything indiscriminately</strong>, archival is <strong>curated by the agent</strong>.</p>

<p>Why split these two tiers? Because they answer different questions. recall answers <strong>"what did we actually say"</strong> — it wants verbatim, complete, traceable; archival answers <strong>"what have I concluded about this"</strong> — it wants the distilled takeaway. Keep "raw log" and "curated notes" apart, and finding the original words isn't drowned by conclusions, nor is finding a conclusion a needle-in-a-haystack over raw chatter.</p>

<div class="cute"><div class="row"><span class="emoji">🎞️</span><span class="bubble">full recording = all Messages</span><span class="arrow">→</span><span class="emoji">🪟</span><span class="lab">recent slice in-window</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="bubble">search older back</span></div>
<div class="cap">Recall memory = an always-on recording of the conversation; the screen shows only the recent slice, older clips come back with a search</div></div>

<p>The row to memorize in that table is <strong>"who writes"</strong>: recall is logged by the <strong>system</strong> behind your back, the agent never lifts a finger; archival is written by the agent <strong>itself</strong>, deliberately. One passively records all, one actively curates — that one row beats ten details.</p>

<h2>One message = one Message row</h2>
<p>recall's smallest unit is the <span class="mono">Message</span> (<span class="mono">letta/schemas/message.py</span>). Every line you, the agent, or a tool says is one <span class="mono">Message</span> row: it has a role, content, and a timestamp, and once stored it's <strong>there forever</strong>.</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/message.py · schemas/agent.py</span><span class="ln">Message key fields + message_ids (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">Message</span>(BaseMessage):
    id: str                          <span class="cm"># unique id of one message</span>
    role: MessageRole                <span class="cm"># system / user / assistant / tool / summary</span>
    content: Optional[List[...]]     <span class="cm"># the body of this message</span>
    tool_calls: Optional[List[...]]  <span class="cm"># tool calls the assistant made</span>
    tool_call_id: Optional[str]      <span class="cm"># for role=tool, which call it answers</span>
    created_at: datetime             <span class="cm"># timestamp: when it was said</span>
    agent_id: Optional[str]          <span class="cm"># which agent it belongs to</span>

<span class="cm"># letta/schemas/agent.py — which Messages are currently in-window</span>
<span class="kw">class</span> <span class="fn">AgentState</span>(...):
    message_ids: Optional[List[str]]  <span class="cm"># ids of in-window messages; [0] is always the system message</span>
</pre></div>

<p>A few things tie the lesson together: <strong>role</strong> marks who spoke (note the <span class="mono">summary</span> role too, used in Lesson 12); <strong>content</strong> is the body; <strong>tool_calls / tool_call_id</strong> make "calling a tool" and "the tool's return" <strong>structured messages</strong> rather than text buried inline; <strong>created_at</strong> makes time-based retrieval possible.</p>

<p>Put differently, role in recall is a <strong>cast list</strong>: <span class="mono">user</span> (the human), <span class="mono">assistant</span> (the agent itself), <span class="mono">tool</span> (a tool return), <span class="mono">system</span> (the system prompt), <span class="mono">summary</span> (a compaction summary). Across one history, who spoke and whether it's speech or a tool result is clear from role — the bedrock that makes "structured events" possible.</p>

<div class="note info"><span class="ni">📌</span><span class="nx"><strong>A Message is durable, not transient.</strong> <span class="mono">MessageManager</span> (<span class="mono">letta/services/message_manager.py</span>) persists and retrieves it. Once written, even after it drops out of the window, the row stays in the table — the physical guarantee behind "the conversation is never lost."</span></div>

<p>Who writes these Messages? <strong>Not the agent — the system.</strong> Each step (Lesson 3's step loop), newly produced messages are auto-persisted by <span class="mono">MessageManager</span> and appended to <span class="mono">message_ids</span>. The agent <strong>calls no "save" tool</strong> — exactly the core difference from archival: archival needs the agent to actively <span class="mono">insert</span>, recall quietly logs all in the background.</p>

<h2>message_ids: the small in-window slice</h2>
<p>The full set of Messages sits in the store, but each turn the model only reads the few that <span class="mono">message_ids</span> marks. <span class="mono">message_ids</span> is a list of <strong>pointers</strong> (ids), not the messages themselves — it points at "which rows go into context right now."</p>

<div class="cellgroup">
  <div class="cg-cap"><b>message_ids ⊂ all Messages</b>: what's in-window is just the tail of the full log</div>
  <div class="cells">
    <span class="cell hl">[0] system message · always in-window</span>
    <span class="sep">·</span>
    <span class="cell q">older messages · in the store, not in message_ids</span>
    <span class="sep">·</span>
    <span class="cell">recent slice · pointed at by message_ids, visible in-window</span>
  </div>
</div>

<p>When the window fills, older messages are <strong>dropped</strong> from <span class="mono">message_ids</span> — but only removed from the "in-window pointers"; the <span class="mono">Message</span> rows <strong>stay untouched in the store</strong>. Adds and drops only touch this pointer list, never the real rows:</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Window nearly full</h4><p>In-window tokens approach the budget (Lesson 5); old messages must yield.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Trim the older</h4><p>Drop the front entries from <span class="mono">message_ids</span>, <strong>keeping system message #0</strong>.</p><span class="mono">trim_older_in_context_messages</span></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Originals stay stored</h4><p>Dropped ≠ deleted; the <span class="mono">Message</span> rows are still in the table.</p><span class="mono">message_manager.py</span></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Search back when needed</h4><p>Use <span class="mono">conversation_search</span> to fetch old messages back by hybrid.</p></div></div>
</div>

<p>New messages go the other way: <span class="mono">append_to_in_context_messages</span> tacks them onto the end of <span class="mono">message_ids</span>. A wholesale swap uses <span class="mono">set_in_context_messages</span>. All three only edit pointers, <strong>very cheaply</strong> — the payoff of making "in-window" an id list rather than a column of objects.</p>

<p>A handy image: <span class="mono">message_ids</span> is like a tape player's <strong>playhead</strong> — it slides over the whole reel (all Messages), deciding "which segment is on screen now." Move the playhead forward and earlier frames leave the screen, but <strong>not a frame of film is lost</strong>; you can always rewind.</p>

<h2>Messages aren't raw text: typed JSON events</h2>
<p>Here's an easily-missed key point: messages entering the context are <strong>not raw text</strong>. Before the model reads each one, <span class="mono">letta/system.py</span> wraps it into a <strong>typed JSON event</strong> stating "what this is and when it happened."</p>

<p>These envelopes look alike: each is a small JSON object with at least <span class="mono">type</span> (or <span class="mono">status</span>) and <span class="mono">time</span>, plus a <span class="mono">message</span> holding the body. The uniform shape gives "pack / unpack / route by type" a predictable structure.</p>

<div class="cols">
  <div class="col"><h4>❌ If it were raw text</h4><p>"hi" / "sunny" / "OK" — the model must guess: who said it? a user, a tool return, a system alert? It's all mushed together.</p></div>
  <div class="col"><h4>✅ Letta's JSON envelope</h4><p>Each carries <span class="mono">type</span> and <span class="mono">time</span>: <span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span> — origin and timing clear at a glance.</p></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/system.py</span><span class="ln">every message is packed into a typed JSON event (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">package_user_message</span>(user_message, timezone, ...):
    <span class="kw">return</span> json_dumps({
        <span class="st">"type"</span>: <span class="st">"user_message"</span>,   <span class="cm"># event type</span>
        <span class="st">"message"</span>: user_message,     <span class="cm"># what the user said</span>
        <span class="st">"time"</span>: formatted_time,       <span class="cm"># local time</span>
    })

<span class="kw">def</span> <span class="fn">package_function_response</span>(was_success, response_string, timezone):
    <span class="kw">return</span> json_dumps({
        <span class="st">"status"</span>: <span class="st">"OK"</span> <span class="kw">if</span> was_success <span class="kw">else</span> <span class="st">"Failed"</span>,
        <span class="st">"message"</span>: response_string,   <span class="cm"># the tool's return</span>
        <span class="st">"time"</span>: formatted_time,
    })

<span class="kw">def</span> <span class="fn">get_heartbeat</span>(timezone, reason=<span class="st">"Automated timer"</span>, ...):
    <span class="kw">return</span> json_dumps({<span class="st">"type"</span>: <span class="st">"heartbeat"</span>, <span class="st">"reason"</span>: reason, <span class="st">"time"</span>: ...})
</pre></div>

<p>The three most common events: <strong>user_message</strong> (what the user said), <strong>function_response</strong> (a tool's return, with <span class="mono">status</span>), <strong>heartbeat</strong> (a system timer waking the agent). All carry <span class="mono">time</span>, so "retrieve by time" and "know how long ago" both become possible.</p>

<p>Of the three, <span class="mono">heartbeat</span> is the odd one: it isn't anyone's speech but a system <strong>timed wake-up</strong>, giving the agent a chance to act even with no user input. A heartbeat is still a typed JSON event — it enters recall and is searchable too, leaving a trace of "when the system nudged it."</p>

<div class="note info"><span class="ni">👉</span><span class="nx">Reading back adds an <strong>unpack</strong> step: <span class="mono">unpack_message</span> (<span class="mono">letta/system.py</span>) opens the envelope and pulls the inner text — but <strong>only for <span class="mono">user_message</span></strong>; other types are kept as-is so structure isn't lost.</span></div>

<h2>conversation_search: fetch old messages back by hybrid</h2>
<p>How do out-of-window messages come back? Via <span class="mono">conversation_search</span> (<span class="mono">core_tool_executor.py</span>). The agent gives a query, and it fishes the most relevant few from the <strong>entire conversation history</strong> back into the window.</p>

<div class="note tip"><span class="ni">✅</span><span class="nx"><strong>conversation_search is hybrid retrieval.</strong> Its tool description (<span class="mono">letta/functions/function_sets/base.py</span>) literally says "hybrid search (text + semantic similarity)" — <strong>text + meaning together</strong>, so it hits even when wording changes. It's <strong>not</strong> pure keyword matching.</span></div>

<div class="flow">
  <div class="node"><div class="nt">query</div><div class="nd">"the renewal we discussed"</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">hybrid search</div><div class="nd">text + meaning</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">filter tool msgs</div><div class="nd">avoid recursive nesting</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Top-K old msgs</div><div class="nd">with timestamp + "Xd ago"</div></div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/core_tool_executor.py</span><span class="ln">conversation_search (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">conversation_search</span>(self, agent_state, actor, query=<span class="kw">None</span>,
                              roles=<span class="kw">None</span>, limit=<span class="kw">None</span>,
                              start_date=<span class="kw">None</span>, end_date=<span class="kw">None</span>):
    <span class="cm"># delegates to message_manager, default search_mode="hybrid" (text + meaning)</span>
    message_results = <span class="kw">await</span> self.message_manager.<span class="fn">search_messages_async</span>(
        agent_id=agent_state.id, actor=actor,
        query_text=query, roles=..., limit=search_limit,
        start_date=..., end_date=...)
    <span class="cm"># filter out tool msgs + the "called conversation_search" message, to avoid recursion</span>
    <span class="cm"># tag each with a timestamp and "Xd ago", then return</span>
    <span class="kw">return</span> formatted_results
</pre></div>

<p>Two details worth remembering. One: it defaults to <strong>hybrid</strong> — delegating to <span class="mono">search_messages_async(search_mode="hybrid")</span>, computing text and meaning together, so rephrasing still hits. Two: it <strong>filters out tool messages</strong>, plus the assistant message that "called conversation_search itself," to avoid nesting search results layer upon layer with runaway escaping.</p>

<p>You can also filter by <strong>role and time</strong>: <span class="mono">roles=["user"]</span> searches only user lines, <span class="mono">start_date</span> / <span class="mono">end_date</span> bound a time window. Each result carries a <strong>timestamp and "Xd ago,"</strong> so the agent knows how long ago it was said.</p>

<p>How many come back is set by <span class="mono">limit</span>; unset, it falls back to the system default page size <span class="mono">RETRIEVAL_QUERY_DEFAULT_PAGE_SIZE</span>. Like archival, <strong>each fetched message costs context tokens again</strong> — so it's "fetch a small handful on demand," not "unroll the whole reel."</p>

<h2>A real scenario: still recalling that one line three weeks later</h2>
<p>Let's string the mechanism into a story. Three weeks ago the user mentioned offhand, "our fiscal year starts in July." At the time it was just an ordinary <span class="mono">user_message</span>, stored as one <span class="mono">Message</span>, slowly sliding out of the window as the conversation moved on.</p>

<p>Today the user says, "put the quarterly review on my calendar." To schedule it the agent needs the fiscal-year start — but that line is long gone from the window. So it calls <span class="mono">conversation_search</span> with the query "company fiscal year / quarter start."</p>

<div class="note warn"><span class="ni">⚠️</span><span class="nx">Note <strong>not a single original word matches</strong>: "fiscal year starts in July" vs the query "quarter start." Pure keywords would whiff — but <span class="mono">conversation_search</span> is <strong>hybrid</strong>, and the semantic path pulls it back reliably.</span></div>

<p>That three-week-old <span class="mono">Message</span> comes back into the window, tagged "21d ago." The agent reads "fiscal year starts July" and schedules the quarterly review in the right month. <strong>The conversation was never lost — it just waited to be searched back.</strong></p>

<p>One might ask: why not hand this "remembering" to archival? Because the agent <strong>never judged that line worth keeping long-term</strong>, so it never inserted it into archival. But recall <strong>logged it indiscriminately</strong> — and that "log it all first, search later" safety net is exactly what keeps the agent from losing information just because it "didn't think much of it at the time."</p>

<div class="card spark">
  <div class="tag">💡 Design highlight</div>
  <strong>The conversation is never lost — and it isn't a pile of raw text, it's a stream of typed JSON events.</strong> Two things stacked together are recall's real power. First: every message is one durable, searchable <span class="mono">Message</span>; once written it lives in the store forever, while only the recent slice <span class="mono">message_ids</span> points to stays in the window — the rest is <strong>invisible but searchable</strong>. Second: before entering context, each message is wrapped by <span class="mono">letta/system.py</span> into a <strong>typed event</strong> — <span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span>, each with <span class="mono">type</span> and <span class="mono">time</span>. So the agent isn't reading a flat stream of prose, it reasons over <strong>a sequence of structured events</strong>: it can tell "this is the user," "this is a tool return," "this is a timed heartbeat." Put them together: a conversation history that is <strong>never lost, hybrid-searchable, and self-typed per message</strong> — the agent neither "forgets what was said" nor "confuses who said it." That's the key to MemGPT treating "conversation history" as first-class memory: history isn't a junk log, it's <strong>reasoning-ready, searchable structured memory</strong> — which is exactly why the agent can, three weeks and a dozen turns later, precisely cite a line you mentioned offhand.
</div>

<div class="card warn">
  <div class="tag">⚠️ Common pitfall</div>
  <strong>"In-window" ≠ "all history" — don't mistake the few in front of you for the whole conversation.</strong> What the model reads directly each turn is only the recent slice <span class="mono">message_ids</span> marks; earlier messages are <strong>searchable but not visible</strong>. This breeds two deadly misjudgments. One: thinking "the model didn't mention it = it forgot." Not necessarily — it may simply not have searched; that message still sits in the store, and <span class="mono">conversation_search</span> brings it right back. Two: thinking "since it's all kept, I can flip through history freely." Also wrong — fetched messages <strong>cost context tokens again</strong>, and hybrid search is a retrieval with real cost, not a free full-text dump. The right stance: treat "the recent in-window slice" as the workbench, and "the full out-of-window history" as an archive you can query anytime — <strong>search only when needed, visible only once searched</strong>. And don't forget: being dropped from the window <strong>does not</strong> mean deleted; the <span class="mono">Message</span> rows are always there, so "not visible" is never "gone," just "not on the table right now."
</div>

<div class="card detail">
  <div class="tag">🔬 Down to the code</div>
  <strong>Source coordinates for the whole chain.</strong> The data model <span class="mono">Message</span> (role / content / tool_calls / created_at) is in <span class="mono">letta/schemas/message.py</span>; persistence and retrieval go through <span class="mono">MessageManager</span> (<span class="mono">letta/services/message_manager.py</span>). The in-window pointer <span class="mono">message_ids</span> is on <span class="mono">letta/schemas/agent.py::AgentState</span>, with <span class="mono">[0]</span> always the system message; adds/drops live in <span class="mono">agent_manager.py</span>'s <span class="mono">append_to_in_context_messages</span> / <span class="mono">trim_older_in_context_messages</span> / <span class="mono">set_in_context_messages</span>. The JSON envelopes are in <span class="mono">letta/system.py</span>: <span class="mono">package_user_message</span> / <span class="mono">package_function_response</span> / <span class="mono">get_heartbeat</span> / <span class="mono">package_summarize_message</span>, with <span class="mono">unpack_message</span> pulling the inner text on read-back. The retrieval tool <span class="mono">conversation_search</span> is in <span class="mono">core_tool_executor.py</span>, delegating to <span class="mono">MessageManager.search_messages_async</span> (default <span class="mono">search_mode="hybrid"</span>); its docstring is declared in <span class="mono">functions/function_sets/base.py</span>, literally "hybrid search (text + semantic similarity)." Follow these symbols and you can trace "how one utterance becomes searchable history" end to end.
</div>

<h2>Dig a little deeper</h2>

<details class="accordion"><summary>Why JSON envelopes instead of raw text</summary><div class="acc-body">
<p><strong>Example:</strong> the user says "hi"; what enters context isn't the two letters <span class="mono">hi</span> but <span class="mono">{"type":"user_message","message":"hi","time":"..."}</span>.</p>
<p><strong>Why designed this way:</strong> raw text mushes "who said it, when, is it a tool result" together, leaving the model to guess. Wrapped as a <span class="mono">type</span>-tagged event, it tells <span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span> apart at a glance, reasoning more steadily.</p>
<p><strong>Where in the source:</strong> the <span class="mono">package_*</span> family in <span class="mono">letta/system.py</span> does the "packing," <span class="mono">unpack_message</span> does the "unpacking" on read-back (pulling inner text only for <span class="mono">user_message</span>).</p>
<p><strong>Alternatives:</strong> special prefixes (like <span class="mono">User:</span> / <span class="mono">Tool:</span>) work too, but JSON is more structured and extensible — adding <span class="mono">location</span>, <span class="mono">name</span>, etc. doesn't break the old format.</p>
</div></details>

<details class="accordion"><summary>Managing in-window messages: append, trim, set</summary><div class="acc-body">
<p><strong>Example:</strong> a new message arrives → appended to the end of <span class="mono">message_ids</span>; the window needs slimming → drop the older few, but keep system message #0.</p>
<p><strong>Why designed this way:</strong> making "what's in-window" a mutable list of id pointers keeps adds/drops featherlight — no moving the real <span class="mono">Message</span> rows, just the pointers.</p>
<p><strong>Where in the source:</strong> <span class="mono">agent_manager.py</span>'s <span class="mono">append_to_in_context_messages</span> (append), <span class="mono">trim_older_in_context_messages(num)</span> (keep <span class="mono">[0]</span>, drop older fronts), <span class="mono">set_in_context_messages</span> (wholesale swap).</p>
<p><strong>Alternatives:</strong> storing the full column of message objects works, but id pointers are leaner and let "one message be referenced from several places." Index 0 always being the system message is the premise for Lesson 9's "rebuild message #0."</p>
</div></details>

<details class="accordion"><summary>recall vs archival: both searchable — where's the difference</summary><div class="acc-body">
<p><strong>Example:</strong> "the user complained about slow shipping three weeks ago" is a verbatim line, so it's recall, searched by <span class="mono">conversation_search</span>; "the user is allergic to peanuts," distilled by the agent into a long-term fact in archival, is searched by <span class="mono">archival_memory_search</span>.</p>
<p><strong>Why designed this way:</strong> one is the <strong>system's auto-logged raw stream</strong>, the other the <strong>agent's actively curated distilled notes</strong>. Kept apart, "find the original words" and "find the conclusion" each travel their own tier, uncontaminated.</p>
<p><strong>Where in the source:</strong> recall searches <span class="mono">conversation_search</span> → <span class="mono">search_messages_async</span> (<span class="mono">message_manager.py</span>); archival searches <span class="mono">archival_memory_search</span> → <span class="mono">cosine_distance</span> nearest neighbors (Lesson 10).</p>
<p><strong>Don't flip it:</strong> the difference is <strong>not</strong> "recall by literal, archival by semantic." Both carry semantics: recall is hybrid (text+meaning), archival is pure semantic. The real split is <strong>what's stored / who writes</strong>.</p>
</div></details>

<details class="accordion"><summary>summary messages: compacted history still lives in recall</summary><div class="acc-body">
<p><strong>Example:</strong> under window pressure, an older batch of messages is <strong>squeezed into one summary</strong> placed back in context, while the originals retreat out-of-window — but they're still <span class="mono">Message</span> rows in the store, still searchable.</p>
<p><strong>Why designed this way:</strong> compaction is to save tokens, not to delete history. The summary keeps the "gist" in front of you, the original messages stay in recall for reference — no conflict.</p>
<p><strong>Where in the source:</strong> the summary is packed by <span class="mono">letta/system.py::package_summarize_message</span> into a <span class="mono">system_alert</span> event; <span class="mono">summary</span> is already one of <span class="mono">Message</span>'s role values.</p>
<p><strong>Lesson 12 preview:</strong> "when to compact, what to compact, how the summary is generated" is next lesson's topic (<span class="mono">letta/services/summarizer/</span>). Here just remember: <strong>compaction ≠ loss</strong>; the swapped-out originals still sit in recall.</p>
</div></details>

<h2>Next stop: from "able to remember" to "able to fit"</h2>
<p>This lesson nailed the most "complete" of the three tiers: recall is the system's auto-logged <strong>full conversation history</strong>, each entry a durable, searchable <span class="mono">Message</span>; <span class="mono">message_ids</span> marks the in-window slice, the rest fetched by <span class="mono">conversation_search</span> via hybrid.</p>

<div class="note info"><span class="ni">👉</span><span class="nx"><strong>Lesson 12 preview:</strong> recall guarantees "nothing lost," but the window is still finite. When in-window messages approach the token budget, Letta <strong>compacts the older batch into a summary</strong> and swaps it out — Lesson 9's closing "rebuild message #0 after compaction." Next: <strong>context compaction and "memory pressure."</strong></span></div>

<p>Tie Part 3 together: core lets the agent <strong>rewrite who it is</strong> (07–09), archival lets it <strong>accumulate long-term knowledge</strong> (10), recall lets it <strong>remember every line said</strong> (11), and compaction (12) keeps it all <strong>turning</strong> inside a finite window. Four pieces in place, the memory system closes the loop.</p>

<p>Look back at Lesson 3's "lifecycle of one message": a message comes in via POST, is processed, persisted, and answered — the moment it <strong>hits the store</strong> it joins recall. So recall isn't a separate module but the <strong>natural destination of every message's lifecycle</strong>: said is logged, logged is searchable.</p>

<p>One chain to memorize on your way out: <strong>say a line → pack into a JSON event → store as a Message row → message_ids marks the in-window slice → old ones swap out but stay stored → to recall, conversation_search (hybrid) fetches it back</strong>. Hold this chain, plus "invisible ≠ gone," and recall is truly in your hands.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>recall = the system's auto-logged full conversation history</strong>: every message is a durable, searchable <span class="mono">Message</span> (<span class="mono">letta/schemas/message.py</span>), persisted by <span class="mono">MessageManager</span>; writing is automatic.</li>
    <li><strong>message_ids = in-window pointers</strong> (<span class="mono">AgentState</span>): marks only the recent slice, <span class="mono">[0]</span> is always the system message; adds/drops via <span class="mono">append</span> / <span class="mono">trim_older</span> / <span class="mono">set_in_context</span>.</li>
    <li><strong>messages are typed JSON events</strong>: <span class="mono">letta/system.py</span> packs each into <span class="mono">user_message</span> / <span class="mono">function_response</span> / <span class="mono">heartbeat</span> (with <span class="mono">type</span> + <span class="mono">time</span>); the agent reasons over structured events.</li>
    <li><strong>conversation_search is hybrid (text + meaning)</strong>: in <span class="mono">core_tool_executor.py</span>, delegating to <span class="mono">search_messages_async</span>; docstring literally "hybrid search (text + semantic similarity)."</li>
    <li><strong>"in-window" ≠ "all history"</strong>: old messages are <strong>searchable but not visible</strong>, dropped ≠ deleted; fetching them back costs tokens.</li>
    <li><strong>recall vs archival's true split</strong>: it's "<strong>what's stored / who writes</strong>" (recall logs all automatically, archival is agent-curated), not "literal vs semantic."</li>
  </ul>
</div>
""",
}
