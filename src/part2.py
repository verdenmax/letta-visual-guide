"""Content for Part 2 (foundations). Lesson 04: LLM agents & tool calling."""

LESSON_04 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
第一部分我们把 Letta 的骨架看完了：一个 agent 是数据库里的一条 <span class="mono">AgentState</span>（第 1 课），住在 REST → services → ORM 三层架构里（第 2 课），处理一条消息就是让它进入一个<strong>最多 <span class="mono">max_steps</span> 轮的 step 循环</strong>（第 3 课）。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">但那张主轴图里有两个词，我们一直没拆开：<strong>"调 LLM"</strong>和<strong>"执行工具"</strong>。这一课就把这两下放到显微镜下，回答三个最基础、却最容易想当然的问题：模型到底怎么"调用"一个工具？谁真正去执行它？为什么 Letta 要逼着模型"先写一段内心独白、再动手"？把这三点搞透，你就拿到了读懂第四、五部分（agent 循环与工具系统）的钥匙。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把一个 LLM agent 想象成一位<strong>聪明但失忆的实习生</strong>，配了一个<strong>工具箱</strong>和一沓<strong>便签</strong>。你给他派活，但有三条铁律：① 他<strong>不能直接动手</strong>——想用某件工具，只能在便签上写"<strong>请帮我用『查天气』，参数是『北京』</strong>"，然后把便签递给你；真正跑去仓库、把工具用起来的是<strong>你</strong>，不是他。② 你把结果（"北京 26℃"）写回便签塞给他，他才知道发生了什么，接着想下一步。③ 公司还规定：每张工具便签的<strong>最上面一行</strong>，必须先写"<strong>我为什么要用这个工具</strong>"——逼他把思路落在纸上，而不是闷头乱抓。于是一件事常常要<strong>来回递好几张便签</strong>才办完：想一下、递一张、看结果、再想一下……这套"写便签—你执行—回结果"的节奏就是 tool calling；而"最上面先写想法"，就是这一课最妙的那一手。
</div>

<h2>agent = LLM + 工具 + 循环</h2>
<p>先把"agent"这个词去神秘化。一个 LLM agent 不是某种新模型，它就是<strong>三样老东西拼起来</strong>：一个会预测下一个 token 的 <strong>LLM</strong>、一组它能调用的<strong>工具</strong>（函数）、以及一个把"调模型 → 执行工具 → 把结果喂回去"不断重复的<strong>循环</strong>。第 3 课的 step 循环，正是这个"循环"在 Letta 里的实现；本课要补的，是循环里那一下"调模型 + 执行工具"到底怎么运转。</p>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  一句话：<strong>LLM 负责"想和决定"，工具负责"摸到外部世界"，循环负责"把两者串起来直到事情办完"。</strong>模型本身只会做一件事——给定一段文本，预测接下来该写什么。它不能上网、不能读数据库、不能改自己的记忆。所谓"会用工具的 agent"，是在请求里<strong>额外告诉模型"你有这些函数可用"</strong>，模型于是可以在该用的时候<strong>产出一个"调用请求"</strong>；但请求不等于执行——必须有一圈循环，把请求接住、真的去跑、再把结果交回给模型，它才能基于结果继续。<strong>没有这圈循环，LLM 永远停在"我想查一下"，到不了"查到了"。</strong>
</div>

<h2>函数调用，在消息层到底怎么工作</h2>
<p>很多人以为"function calling"是模型偷偷帮你运行了代码。<strong>恰恰相反。</strong>它发生在<strong>消息层</strong>，全程只是"文本进、结构化文本出"。一次完整的往返是这样的：</p>

<div class="flow">
  <div class="node"><div class="nt">请求</div><div class="nd">messages + 工具 schema</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">模型产出</div><div class="nd">tool_call(name, args)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">你的代码执行</div><div class="nd">真正跑这个函数</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">回填结果</div><div class="nd">tool result 消息</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">模型继续</div><div class="nd">再想 / 回话</div></div>
</div>

<p>逐格拆开：<strong>第一格</strong>，你发给模型的请求里，除了对话消息，还附上一份<strong>工具清单</strong>——每个工具是一段 JSON schema，写清"函数叫什么、是干嘛的、要哪些参数"。<strong>第二格</strong>，模型读完后，如果决定用某个工具，它<strong>不会执行</strong>，只会在回复里产出一个结构化的 <span class="mono">tool_call</span>：工具名 + 一串 JSON 参数。<strong>第三格</strong>，你的运行时（Letta）接住这个请求，<strong>在你的机器上真正调用那个函数</strong>。</p>

<p><strong>第四格</strong>，把函数返回值包成一条 <span class="mono">tool</span>（工具结果）消息。<strong>第五格</strong>，连同之前的对话一起再发给模型，它这才"看到"结果，决定继续调下一个工具还是直接回话。</p>

<p>这里有两个容易忽略、却很关键的事实。其一，<strong>模型是无状态的</strong>（这正是第 1 课的根本约束）：第五格"再发给模型"时，并不是接着上次的对话继续，而是把 <strong>system + 历史消息 + 刚才的 tool_call + 工具结果</strong>整段<strong>重新拼好、整包发过去</strong>——模型每一轮都是"读一遍完整剧本，再决定下一句台词"。</p>

<p>其二，请求里的工具结果靠一个 <span class="mono">tool_call_id</span> 和发起它的那次调用<strong>配对</strong>，所以即便一轮里发了好几个工具调用，模型也能把"哪个结果对应哪次调用"对上号。</p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">把这两点和第 3 课连起来：<strong>step 循环每转一圈，都要把上下文从 <span class="mono">AgentState</span> 现拼一份</strong>——这也是为什么"稳定前缀 + 变化尾巴"对省钱那么重要。</span></div>

<p>关键就在第一格那份"工具 schema"。它不是你手写的散文，而是<strong>从一个普通 Python 函数自动生成的 JSON</strong>。Letta 用 <span class="mono">generate_schema</span> 读函数的<strong>签名 + Google 风格 docstring</strong>，吐出下面这种模型能读懂的结构。以"往核心记忆追加内容"的工具 <span class="mono">core_memory_append</span> 为例，模型眼里看到的是：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/functions/schema_generator.py</span><span class="ln">generate_schema 产出（core_memory_append）</span></div>
<pre><span class="cm"># 一个工具在模型眼里就是这样一段 JSON（名字 / 描述 / 参数）</span>
{
  <span class="st">"name"</span>: <span class="st">"core_memory_append"</span>,
  <span class="st">"description"</span>: <span class="st">"Append to the contents of core memory."</span>,
  <span class="st">"parameters"</span>: {
    <span class="st">"type"</span>: <span class="st">"object"</span>,
    <span class="st">"properties"</span>: {
      <span class="st">"label"</span>:   {<span class="st">"type"</span>: <span class="st">"string"</span>, <span class="st">"description"</span>: <span class="st">"Section of the memory to be edited."</span>},
      <span class="st">"content"</span>: {<span class="st">"type"</span>: <span class="st">"string"</span>, <span class="st">"description"</span>: <span class="st">"Content to write to the memory. ..."</span>}
    },
    <span class="st">"required"</span>: [<span class="st">"label"</span>, <span class="st">"content"</span>]
  }
}
</pre></div>

<p>注意一个细节：函数原本的签名是 <span class="mono">core_memory_append(agent_state, label, content)</span>，但 schema 里<strong>看不到 <span class="mono">agent_state</span></strong>。因为它属于 <span class="mono">TOOL_RESERVED_KWARGS</span>（即 <span class="mono">["self", "agent_state"]</span>）——这类"由系统在执行时注入"的参数会被<strong>挡在 schema 之外</strong>，不暴露给模型。模型只需要、也只能填它该填的业务参数；运行时执行时再把 <span class="mono">agent_state</span> 这样的上下文补进去。<strong>"模型看到的参数"和"函数真正接收的参数"并不相同</strong>，这一层裁剪正是框架替你做的。</p>

<div class="card warn">
  <div class="tag">⚠️ 最容易想错的一点</div>
  <strong>模型不会执行任何工具，它只会"请求"执行。</strong>当模型产出 <span class="mono">tool_call(name="web_search", args={...})</span>，这只是一段<strong>结构化文本</strong>，等价于"我想调用这个函数，参数是这些"——此刻什么都还没发生。真正去跑这个函数的，是<strong>你的运行时</strong>（在 Letta 里由运行时的 <span class="mono">_execute_tool</span> → <span class="mono">ToolExecutionManager.execute_tool_async</span> 执行，自定义工具还会进<strong>沙箱</strong>）。这有重大的<strong>安全含义</strong>：模型的输出是<strong>不可信</strong>的，它可能"请求"删库、可能"请求"访问内网。决定<strong>到底执不执行、在什么权限下执行、要不要拦</strong>的，永远是你的代码，不是模型。把模型的 <span class="mono">tool_call</span> 当成"用户提交的表单"来对待——先校验，再执行。
</div>

<h2>ReAct：想一步、做一步、再想一步</h2>
<p>把上面那圈往返重复起来，就得到 agent 最核心的工作模式——<strong>ReAct</strong>（Reasoning + Acting，推理与行动交替）。它不是"一问一答"，而是一个小循环：<strong>想</strong>（推理出下一步该干嘛）→ <strong>做</strong>（产出一个 tool_call）→ <strong>看</strong>（观察工具结果）→ <strong>再想</strong>……直到不需要再用工具，才给出最终回话。</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>想（Reason）</h4><p>模型基于当前上下文推理："要回答这个问题，我得先查一下资料。"这段思路就是<strong>内心独白</strong>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>做（Act）</h4><p>产出一个 <span class="mono">tool_call</span>，例如 <span class="mono">web_search(query="...")</span>。注意：只是<strong>请求</strong>，还没执行。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>看（Observe）</h4><p>运行时执行工具，把返回值作为一条 <span class="mono">tool</span> 结果消息<strong>喂回</strong>上下文。模型这才"看到"答案。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>再想 / 收工</h4><p>带着新结果再推理：够了就<strong>回话结束</strong>；不够就<strong>再产出一个 tool_call</strong>，回到第 2 步。</p></div></div>
</div>

<p>这个循环你<strong>第 3 课已经见过</strong>——只是当时叫它 step 循环。Letta 里"要不要再转一圈"的判断极简：<span class="mono">_decide_continuation</span> 看<strong>这一步有没有调用工具</strong>——调了就继续（结果要喂回去让它接着想），只产出普通消息就停（<span class="mono">end_turn</span>）。所以 <strong>ReAct 的循环，就是第 3 课那个 step 循环的"思想内核"</strong>：每一轮 <span class="mono">_step</span> 是一次"想 + 做"，把工具结果喂回去，触发下一轮"看 + 再想"。</p>

<p>如果把"用一个工具"的完整过程摊成<strong>消息序列</strong>，长这样——注意 assistant 那一条里<strong>同时</strong>带着"内心独白"和"工具调用"，而工具结果是单独的一条 <span class="mono">tool</span> 消息：</p>

<div class="cellgroup">
  <div class="cg-cap">一次工具调用的<b>消息序列</b>（从用户提问到最终回话）：</div>
  <div class="cells">
    <span class="cell">user<br>(你的问题)</span>
    <span class="cell hl">assistant<br>(inner_thoughts<br>+ tool_call)</span>
    <span class="cell q">tool<br>(执行结果)</span>
    <span class="cell">assistant<br>(最终回话)</span>
  </div>
</div>

<p>这条序列里藏着一个 Letta 特有的设计：那条 assistant 消息里的 <strong>inner_thoughts（内心独白）</strong>是从哪来的？为什么模型会"先说想法、再调工具"？答案就是这一课的亮点。</p>

<h2>内心独白：把"思维链"塞进工具的一个参数</h2>
<p>很多新模型有原生的"思考"通道（reasoning / thinking），但<strong>不是所有 provider 都有</strong>，而且各家格式还不一样。Letta 想要一个<strong>跨所有模型都成立</strong>的办法，让 agent 在每次动手前都<strong>先把推理写出来</strong>。它的解法非常巧：<strong>给每个工具的参数表，额外塞进一个名为 <span class="mono">thinking</span> 的字符串参数，并强制它必填、且排在第一个。</strong></p>

<div class="cols">
  <div class="col">
    <h4>普通工具 schema</h4>
    <p>模型只被要求填业务参数：</p>
    <p class="mono" style="font-size:.82rem">required: [label, content]</p>
    <p>模型可以<strong>不写任何推理</strong>，直接产出一个 tool_call——想错了也看不出来。</p>
  </div>
  <div class="col">
    <h4>注入 inner_thoughts 后</h4>
    <p>参数表最前面多了一个 <span class="mono">thinking</span>：</p>
    <p class="mono" style="font-size:.82rem">required: [thinking, label, content]</p>
    <p>模型<strong>必须先填 <span class="mono">thinking</span></strong>（描述里明写"先想后做，永远第一个生成它"），等于被结构性地逼着先推理。</p>
  </div>
</div>

<p>这一步由 <span class="mono">add_inner_thoughts_to_functions</span> 完成。它遍历每个工具 schema，把 <span class="mono">thinking</span> 插到 properties 的最前面、再插到 required 的第 0 位：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/helpers.py</span><span class="ln">add_inner_thoughts_to_functions（简化）</span></div>
<pre><span class="cm"># 给每个工具 schema 注入一个"内心独白"参数，并要求最先生成</span>
<span class="kw">def</span> <span class="fn">add_inner_thoughts_to_functions</span>(functions, inner_thoughts_key, inner_thoughts_description,
                                    inner_thoughts_required=<span class="kw">True</span>, put_inner_thoughts_first=<span class="kw">True</span>):
    <span class="kw">for</span> schema <span class="kw">in</span> functions:
        props = schema[<span class="st">"parameters"</span>][<span class="st">"properties"</span>]
        <span class="cm"># inner_thoughts 作为"第一个"属性插入（key 默认为 "thinking"）</span>
        schema[<span class="st">"parameters"</span>][<span class="st">"properties"</span>] = {
            inner_thoughts_key: {<span class="st">"type"</span>: <span class="st">"string"</span>, <span class="st">"description"</span>: inner_thoughts_description},
            **props,
        }
        schema[<span class="st">"parameters"</span>][<span class="st">"required"</span>].insert(<span class="nb">0</span>, inner_thoughts_key)  <span class="cm"># 必填且排第一</span>
    <span class="kw">return</span> functions
</pre></div>

<p>那段"描述"也大有讲究。<span class="mono">local_llm/constants.py</span> 里有两版：普通版 <span class="mono">INNER_THOUGHTS_KWARG_DESCRIPTION</span> 写 "Deep inner monologue private to you only."；而<strong>强制版</strong> <span class="mono">..._GO_FIRST</span> 额外加一句 "<em>Think before you act, so always generate arg 'thinking' first before any other arg.</em>"——直接用自然语言命令模型"先生成 thinking"。等模型回话后，Letta 再用 <span class="mono">unpack_inner_thoughts_from_kwargs</span> 把这个 <span class="mono">thinking</span> 从工具参数里<strong>抠出来</strong>，单独放进 assistant 消息的正文（就是上面 cellgroup 里那条 inner_thoughts 的来历）。对上层来说，它看起来就像模型"先说了段独白、再调了工具"。</p>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>把"思维链"做成工具的一个参数——这是这一课的"啊哈"。</strong>主流做法是指望模型自带"思考通道"，或在提示里恳求它"请一步步想"；但通道<strong>不是每家都有</strong>，恳求也<strong>可被无视</strong>。Letta 换了个根本不同的支点：既然 agent 每次动手都得调用工具、而工具调用<strong>必须符合 schema</strong>，那就把"先想"写进 schema 本身——加一个 <span class="mono">thinking</span> 参数，设成<strong>必填（required）</strong>、<strong>排第一（put_inner_thoughts_first）</strong>，描述里再明令"永远第一个生成它"。于是"推理"从"<strong>但愿它会想</strong>"变成了"<strong>想法是必填参数——不写它，这次调用就不合法</strong>"（至于"排第一"，则由参数顺序加上描述里那句明令共同保证）。更妙的是，这招<strong>跨 provider 通用</strong>：任何支持 function calling 的模型——哪怕完全没有原生思考能力——都被这套结构<strong>逼着"先推理、后行动"</strong>。一个参数，把一条"软约束"变成了"硬约束"。
</div>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  这一课的每个环节落在哪：<strong>工具 → schema</strong> 在 <span class="mono">letta/functions/schema_generator.py::generate_schema</span>（读签名 + docstring，<span class="mono">TOOL_RESERVED_KWARGS</span> 挡掉 <span class="mono">self / agent_state</span>）；<strong>注入内心独白</strong>在 <span class="mono">letta/llm_api/helpers.py::add_inner_thoughts_to_functions</span>，回收在同文件 <span class="mono">unpack_inner_thoughts_from_kwargs</span>；<strong>键名与描述</strong>在 <span class="mono">letta/local_llm/constants.py</span>（<span class="mono">INNER_THOUGHTS_KWARG="thinking"</span>、<span class="mono">VALID_INNER_THOUGHTS_KWARGS</span>、<span class="mono">..._DESCRIPTION(_GO_FIRST)</span>）；<strong>请求组装时触发注入</strong>见 <span class="mono">letta/llm_api/openai.py</span>（当 <span class="mono">llm_config.put_inner_thoughts_in_kwargs</span> 为真）；<strong>续转判定</strong>在 <span class="mono">letta/agents/letta_agent_v3.py</span>（<span class="mono">_decide_continuation</span>）；<strong>工具执行</strong>在 <span class="mono">letta/agents/letta_agent_v2.py</span>（<span class="mono">_execute_tool</span>，v3 继承）→ <span class="mono">ToolExecutionManager.execute_tool_async</span>。
</div>

<p>把"函数调用往返 + ReAct 续转 + 模型只产出不执行"三件事合到一段伪代码里，整个 agent 的心跳就是这样：</p>

<pre class="code"><span class="cm"># 一个 agent 的最小循环（伪代码，对应第 3 课的 step 循环）</span>
messages = [system, ...history..., user_msg]
tools    = <span class="fn">add_inner_thoughts</span>(<span class="fn">to_schema</span>(my_tools))   <span class="cm"># thinking 被塞成第一个参数</span>
<span class="kw">for</span> step <span class="kw">in</span> <span class="fn">range</span>(max_steps):                    <span class="cm"># 上限默认 50</span>
    reply = llm.<span class="fn">call</span>(messages, tools)            <span class="cm"># 模型只"产出"，绝不执行</span>
    <span class="kw">if</span> reply.tool_calls:                          <span class="cm"># 它请求调用某个工具</span>
        name, args = reply.tool_calls[<span class="nb">0</span>]
        result = runtime.<span class="fn">execute</span>(name, args)      <span class="cm"># 你的代码真正执行（必要时进沙箱）</span>
        messages += [reply, <span class="fn">tool_result</span>(result)]  <span class="cm"># 回填结果 -> 触发"再想一轮"</span>
    <span class="kw">else</span>:
        <span class="kw">break</span>                                     <span class="cm"># 没调工具 -> 收工（end_turn）</span>
</pre>

<h2>再挖深一点</h2>

<details class="accordion"><summary>模型为什么不自己执行工具？</summary><div class="acc-body">
<p><strong>示例：</strong>模型产出 <span class="mono">run_code("rm -rf /")</span>。如果"产出"就等于"执行"，那就完了。事实是：这只是一段它<strong>请求</strong>执行的文本，跑不跑由你的运行时说了算。</p>
<p><strong>为什么这样设计：</strong>因为模型输出<strong>天然不可信</strong>——它可能被提示注入、可能幻觉出危险调用。把"决定权"留在框架手里，才能在执行前做权限校验、参数清洗、放进沙箱、甚至直接拒绝。这就是"模型提议、运行时裁决"的安全边界。</p>
<p><strong>源码在哪：</strong>执行入口 <span class="mono">letta/agents/letta_agent_v2.py::LettaAgentV2._execute_tool</span>（<span class="mono">LettaAgentV3</span> 继承并调用）→ <span class="mono">letta/services/tool_executor/tool_execution_manager.py::ToolExecutionManager.execute_tool_async</span>；自定义工具走 <span class="mono">letta/services/tool_executor/sandbox_tool_executor.py</span> 的沙箱。</p>
<p><strong>还有什么替代：</strong>有些玩具框架让模型直接 <span class="mono">eval()</span> 自己的输出——开发快，但等于把 root 权限交给一段概率文本，生产环境绝不可取。</p>
</div></details>

<details class="accordion"><summary>为什么把"思考"塞进参数，而不是单独开一个字段？</summary><div class="acc-body">
<p><strong>示例：</strong>同一个 agent，今天接 OpenAI、明天换 Anthropic、后天用本地 LM Studio。如果"思考"依赖各家私有的 reasoning 字段，就得为每家写一套适配，还可能有的家根本没有这个通道。</p>
<p><strong>为什么这样设计：</strong>所有支持 function calling 的 provider 都认 schema 里的 <span class="mono">required</span> 和参数顺序。把 <span class="mono">thinking</span> 做成"必填且第一"的普通参数，就用<strong>最大公约数</strong>的能力，换来了<strong>跨厂商一致</strong>的"先想后做"，还能<strong>强制顺序</strong>（GO_FIRST 描述明令第一个生成）。回话后再 <span class="mono">unpack</span> 出来当独白，对上层透明。</p>
<p><strong>源码在哪：</strong>注入 <span class="mono">letta/llm_api/helpers.py::add_inner_thoughts_to_functions</span>（<span class="mono">put_inner_thoughts_first=True</span>、<span class="mono">inner_thoughts_required=True</span>）；回收 <span class="mono">unpack_inner_thoughts_from_kwargs</span>；描述 <span class="mono">letta/local_llm/constants.py::INNER_THOUGHTS_KWARG_DESCRIPTION_GO_FIRST</span>。</p>
<p><strong>还有什么替代：</strong>① 指望原生思考通道——不通用；② 在 system 提示里恳求"请一步步想"——软约束，模型可无视；③ 单开一个非工具字段——又回到"各家格式不同"的老问题。塞进参数是覆盖面最广的一招。</p>
</div></details>

<details class="accordion"><summary>ReAct 循环 vs 直接回答：什么时候才需要绕这一圈？</summary><div class="acc-body">
<p><strong>示例：</strong>问"1+1 等于几"，模型一轮直接回答，根本不调工具——ReAct 退化成普通一问一答。问"我上周说的项目截止日是哪天、顺便查下那天天气"，就得先 recall 记忆、再 web_search，两三轮工具才答得了。</p>
<p><strong>为什么这样设计：</strong>循环的价值在于"<strong>模型发起调用时还没看到结果</strong>"。只有把结果喂回去再调一次，它才能基于真实信息继续。需要"看一眼外部世界再决定"的任务，就得绕这一圈；纯靠已有知识能答的，第一轮就 <span class="mono">end_turn</span> 了。</p>
<p><strong>源码在哪：</strong>续转判定 <span class="mono">letta/agents/letta_agent_v3.py::LettaAgentV3._decide_continuation</span>（"调了工具就继续、否则停"）；循环上限 <span class="mono">letta/constants.py::DEFAULT_MAX_STEPS</span>（默认 50）。</p>
<p><strong>还有什么替代：</strong>不带循环的"单次函数调用"——适合一锤子买卖的小任务，但没法多步推理；纯 chain（写死步骤）——可控但不灵活，没法让模型自己决定下一步。ReAct 在"灵活"和"可控"之间取了平衡。</p>
</div></details>

<h2>这一课在整张大图的哪里</h2>
<p>回到第一部分的主轴：第 3 课里那个 step 循环，被我们这一课<strong>拆成了内核</strong>——它跳动的每一下，就是一次"<strong>函数调用往返</strong>"（请求带 schema → 模型产出 tool_call → 运行时执行 → 结果回填 → 再想），而"调了工具就继续、没调就停"这条续转规则，正是 <strong>ReAct"想-做-看-再想"</strong>的直接体现。你现在应该能把第 3 课的 <span class="mono">_step</span> 和本课的 ReAct 循环<strong>对上号</strong>了：它们是同一个东西的两种讲法。</p>

<p>而 Letta 把"先想后做"<strong>焊进了工具的 schema</strong>，这又把第 1 课"自我编辑记忆"的故事补完了一环：agent 改记忆用的就是 <span class="mono">core_memory_append</span> 这样的工具，调用它之前会被 <span class="mono">thinking</span> 参数逼着先写一句"我为什么要改这块记忆"。<strong>记忆、工具、推理，在 Letta 里是同一套机制串起来的。</strong></p>

<p>往后看：<strong>第四部分（agent 循环）</strong>会把本课的循环放大——续转规则、并行工具、<span class="mono">max_steps</span>、流式怎么逐字吐出；<strong>第五部分（工具系统）</strong>会把"工具"这一格放大——schema 怎么从函数生成、<span class="mono">tool_rules</span> 怎么约束调用顺序、沙箱怎么隔离执行、MCP 怎么接外部工具。本课给你的，是读懂那两部分所需的<strong>最小心智模型</strong>：<strong>agent = 会产出调用请求的 LLM + 真正执行的运行时 + 把两者串起来的循环，外加一个被塞进参数、逼它先想的内心独白。</strong></p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>agent = LLM + 工具 + 循环</strong>：模型负责想和决定，工具负责碰外部世界，循环把两者串到事情办完。</li>
    <li><strong>function calling 在消息层</strong>：请求带工具 schema → 模型只<strong>产出</strong> <span class="mono">tool_call</span>（名字 + JSON 参数）→ <strong>你的运行时执行</strong> → tool 结果回填 → 模型继续。</li>
    <li><strong>模型不执行工具</strong>，只发出"调用请求"；真正执行的是 <span class="mono">_execute_tool</span> / <span class="mono">ToolExecutionManager</span>（必要时进沙箱）——这是安全边界。</li>
    <li><strong>工具 schema 由函数自动生成</strong>（<span class="mono">generate_schema</span>，读签名 + docstring），<span class="mono">self / agent_state</span> 等保留参数不暴露给模型。</li>
    <li><strong>ReAct = 想 → 做 → 看 → 再想</strong>，就是第 3 课 step 循环的内核；续转规则极简：调了工具就继续、否则停。</li>
    <li><strong>内心独白塞进参数（亮点）</strong>：<span class="mono">add_inner_thoughts_to_functions</span> 给每个工具加一个必填且排第一的 <span class="mono">thinking</span> 参数，跨 provider 把"先推理后行动"从软约束变成硬约束。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Part 1 gave us Letta's skeleton: an agent is one <span class="mono">AgentState</span> row in a database (Lesson 1), it lives in a three-layer house — REST → services → ORM (Lesson 2), and handling a message means dropping it into a <strong>step loop of up to <span class="mono">max_steps</span> rounds</strong> (Lesson 3).</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">But two words in that spine were never opened up: <strong>"call the LLM"</strong> and <strong>"execute a tool."</strong> This lesson puts both under a microscope and answers the three most basic — yet most easily mis-assumed — questions: how does a model actually "call" a tool? Who really executes it? And why does Letta force the model to "write a line of inner monologue before it acts"? Nail these three and you hold the key to Parts 4 and 5 (the agent loop &amp; the tool system).
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture an LLM agent as a <strong>brilliant but amnesiac intern</strong> equipped with a <strong>toolbox</strong> and a stack of <strong>sticky notes</strong>. You give it work, but with three iron rules: ① It <strong>cannot act directly</strong> — to use a tool, it can only write on a note "<strong>please use 'check weather' with the argument 'Beijing'</strong>" and hand it to <strong>you</strong>; the one who actually walks to the warehouse and runs the tool is <strong>you</strong>, not the intern. ② Only when you write the result back ("Beijing 26℃") and hand the note back does it learn what happened and think about the next step. ③ The company also mandates: the <strong>very first line</strong> of every tool note must say "<strong>why I'm using this tool</strong>" — forcing the thinking onto paper instead of grabbing blindly. So one task often takes <strong>several notes back and forth</strong>: think, hand over a note, see the result, think again… That "write-a-note → you-execute → return-result" rhythm <strong>is</strong> tool calling; and "write the thought on the top line first" is the cleverest move in this lesson.
</div>

<h2>agent = LLM + tools + a loop</h2>
<p>Let's de-mystify the word "agent." An LLM agent is not some new model — it's <strong>three old things bolted together</strong>: an <strong>LLM</strong> that predicts the next token, a set of <strong>tools</strong> (functions) it can call, and a <strong>loop</strong> that keeps repeating "call the model → execute a tool → feed the result back." Lesson 3's step loop is exactly that "loop" inside Letta; what this lesson adds is how the "call the model + execute a tool" beat actually works.</p>

<div class="card macro">
  <div class="tag">🌍 The big picture</div>
  In one line: <strong>the LLM does the "thinking and deciding," tools "touch the outside world," and the loop "strings them together until the job is done."</strong> The model itself does exactly one thing — given some text, predict what to write next. It can't browse the web, read a database, or edit its own memory. A "tool-using agent" simply <strong>tells the model "you have these functions available"</strong> in the request, so the model can <strong>emit a "call request"</strong> when appropriate; but a request is not an execution — there must be a loop to catch the request, actually run it, and hand the result back, before the model can continue from the result. <strong>Without that loop, the LLM is forever stuck at "I'd like to look this up" and never reaches "I looked it up."</strong>
</div>

<h2>How function calling actually works, at the message layer</h2>
<p>Many people think "function calling" means the model secretly ran code for you. <strong>It's the opposite.</strong> It happens at the <strong>message layer</strong> — the whole thing is just "text in, structured text out." One full round-trip looks like this:</p>

<div class="flow">
  <div class="node"><div class="nt">Request</div><div class="nd">messages + tool schemas</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">Model emits</div><div class="nd">tool_call(name, args)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Your code runs it</div><div class="nd">actually call the function</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Feed result back</div><div class="nd">tool result message</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Model continues</div><div class="nd">think / reply</div></div>
</div>

<p>Cell by cell: <strong>cell 1</strong>, the request you send the model carries — besides the conversation messages — a <strong>tool list</strong>, where each tool is a JSON schema stating "what the function is called, what it does, which arguments it takes." <strong>Cell 2</strong>, having read them, if the model decides to use a tool it <strong>does not execute</strong> it; it only emits a structured <span class="mono">tool_call</span>: a tool name + a JSON blob of arguments. <strong>Cell 3</strong>, your runtime (Letta) catches that request and <strong>actually calls the function on your machine</strong>.</p>

<p><strong>Cell 4</strong>, the return value is wrapped into a <span class="mono">tool</span> (tool-result) message. <strong>Cell 5</strong>, it's sent back to the model together with the prior conversation, and only now does the model "see" the result and decide whether to call another tool or just reply.</p>

<p>Two easily-missed but crucial facts hide here. First, <strong>the model is stateless</strong> (exactly Lesson 1's core constraint): "sending it back" in cell 5 doesn't resume a session — it <strong>re-assembles and re-sends the entire packet</strong> of <strong>system + history + that tool_call + the tool result</strong>. The model re-reads the whole script every round before deciding its next line.</p>

<p>Second, the tool result is <strong>paired</strong> with the call that produced it via a <span class="mono">tool_call_id</span>, so even if a round emits several tool calls, the model can match "which result belongs to which call." </p>

<div class="note tip"><span class="ni">🧠</span><span class="nx">Tie both back to Lesson 3: <strong>every turn of the step loop re-assembles the context fresh from <span class="mono">AgentState</span></strong> — which is why "stable prefix + changing tail" matters so much for cost.</span></div>

<p>The crux is that "tool schema" in cell 1. It isn't prose you hand-write — it's <strong>JSON auto-generated from an ordinary Python function</strong>. Letta uses <span class="mono">generate_schema</span> to read a function's <strong>signature + Google-style docstring</strong> and emit a structure the model can read. Take <span class="mono">core_memory_append</span>, the tool that appends to core memory; here's what the model sees:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/functions/schema_generator.py</span><span class="ln">generate_schema output (core_memory_append)</span></div>
<pre><span class="cm"># To the model, a tool is just this JSON (name / description / parameters)</span>
{
  <span class="st">"name"</span>: <span class="st">"core_memory_append"</span>,
  <span class="st">"description"</span>: <span class="st">"Append to the contents of core memory."</span>,
  <span class="st">"parameters"</span>: {
    <span class="st">"type"</span>: <span class="st">"object"</span>,
    <span class="st">"properties"</span>: {
      <span class="st">"label"</span>:   {<span class="st">"type"</span>: <span class="st">"string"</span>, <span class="st">"description"</span>: <span class="st">"Section of the memory to be edited."</span>},
      <span class="st">"content"</span>: {<span class="st">"type"</span>: <span class="st">"string"</span>, <span class="st">"description"</span>: <span class="st">"Content to write to the memory. ..."</span>}
    },
    <span class="st">"required"</span>: [<span class="st">"label"</span>, <span class="st">"content"</span>]
  }
}
</pre></div>

<p>Note a detail: the function's real signature is <span class="mono">core_memory_append(agent_state, label, content)</span>, yet the schema has <strong>no <span class="mono">agent_state</span></strong>. That's because it belongs to <span class="mono">TOOL_RESERVED_KWARGS</span> (namely <span class="mono">["self", "agent_state"]</span>) — these "injected-by-the-system-at-execution" parameters are <strong>kept out of the schema</strong> and never exposed to the model. The model only needs to (and only can) fill the business arguments; the runtime adds context like <span class="mono">agent_state</span> back in when it executes. <strong>"What the model sees" and "what the function actually receives" are not the same</strong> — that trimming layer is the framework doing work for you.</p>

<div class="card warn">
  <div class="tag">⚠️ The thing people get wrong</div>
  <strong>The model executes nothing — it only "requests" execution.</strong> When the model emits <span class="mono">tool_call(name="web_search", args={...})</span>, that's just <strong>structured text</strong>, equivalent to "I'd like to call this function with these arguments" — nothing has happened yet. The one that actually runs the function is <strong>your runtime</strong> (in Letta, the runtime's <span class="mono">_execute_tool</span> → <span class="mono">ToolExecutionManager.execute_tool_async</span>; custom tools even go through a <strong>sandbox</strong>). This has serious <strong>security implications</strong>: the model's output is <strong>untrusted</strong> — it could "request" to drop a database or reach an internal network. What decides <strong>whether to run it, under what privileges, and whether to block it</strong> is always your code, not the model. Treat a model's <span class="mono">tool_call</span> like "a form submitted by a user" — validate first, then execute.
</div>

<h2>ReAct: think a step, act a step, think again</h2>
<p>Repeat that round-trip and you get the agent's core working pattern — <strong>ReAct</strong> (Reasoning + Acting, interleaved). It isn't "one question, one answer"; it's a small loop: <strong>think</strong> (reason out the next move) → <strong>act</strong> (emit a tool_call) → <strong>observe</strong> (look at the tool result) → <strong>think again</strong>… until no tool is needed, then give the final reply.</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Think (Reason)</h4><p>The model reasons from the current context: "to answer this, I should look something up first." That reasoning is the <strong>inner monologue</strong>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Act</h4><p>It emits a <span class="mono">tool_call</span>, e.g. <span class="mono">web_search(query="...")</span>. Note: only a <strong>request</strong>, not yet executed.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Observe</h4><p>The runtime executes the tool and <strong>feeds</strong> the return value back as a <span class="mono">tool</span> result message. Only now does the model "see" the answer.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Think again / finish</h4><p>Reason with the new result: enough → <strong>reply and stop</strong>; not enough → <strong>emit another tool_call</strong> and go back to step 2.</p></div></div>
</div>

<p>You've <strong>already met this loop in Lesson 3</strong> — we just called it the step loop. Letta's "go around again?" decision is dead simple: <span class="mono">_decide_continuation</span> checks <strong>whether this step called a tool</strong> — called one, continue (the result must be fed back so it can keep thinking); only a plain message, stop (<span class="mono">end_turn</span>). So <strong>the ReAct loop IS the "intellectual core" of Lesson 3's step loop</strong>: each <span class="mono">_step</span> round is one "think + act," feeding the tool result back to trigger the next round's "observe + think again."</p>

<p>If you lay out "using one tool" as a <strong>message sequence</strong>, it looks like this — note that the assistant message carries <strong>both</strong> the "inner monologue" and the "tool call," while the tool result is a separate <span class="mono">tool</span> message:</p>

<div class="cellgroup">
  <div class="cg-cap">The <b>message sequence</b> of one tool call (from your question to the final reply):</div>
  <div class="cells">
    <span class="cell">user<br>(your question)</span>
    <span class="cell hl">assistant<br>(inner_thoughts<br>+ tool_call)</span>
    <span class="cell q">tool<br>(execution result)</span>
    <span class="cell">assistant<br>(final reply)</span>
  </div>
</div>

<p>This sequence hides a Letta-specific design: where do the <strong>inner_thoughts</strong> in that assistant message come from? Why does the model "state its thinking before calling a tool"? That's the spark of this lesson.</p>

<h2>Inner monologue: stuffing the "chain of thought" into a tool argument</h2>
<p>Many new models have a native "thinking" channel (reasoning / thinking), but <strong>not every provider does</strong>, and the formats differ. Letta wanted a way that <strong>holds across all models</strong> to make the agent <strong>write its reasoning before every action</strong>. Its solution is clever: <strong>add to every tool's parameter list one extra string argument named <span class="mono">thinking</span>, force it to be required, and put it first.</strong></p>

<div class="cols">
  <div class="col">
    <h4>Ordinary tool schema</h4>
    <p>The model is only asked to fill business args:</p>
    <p class="mono" style="font-size:.82rem">required: [label, content]</p>
    <p>The model can <strong>write no reasoning at all</strong> and emit a tool_call directly — if it reasoned wrong, you can't tell.</p>
  </div>
  <div class="col">
    <h4>After injecting inner_thoughts</h4>
    <p>A <span class="mono">thinking</span> is prepended to the param list:</p>
    <p class="mono" style="font-size:.82rem">required: [thinking, label, content]</p>
    <p>The model <strong>must fill <span class="mono">thinking</span> first</strong> (the description literally says "think before you act, always generate it first") — structurally forced to reason first.</p>
  </div>
</div>

<p>This step is done by <span class="mono">add_inner_thoughts_to_functions</span>. It walks each tool schema, inserts <span class="mono">thinking</span> at the front of properties, then inserts it at index 0 of required:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/helpers.py</span><span class="ln">add_inner_thoughts_to_functions (simplified)</span></div>
<pre><span class="cm"># Inject an "inner monologue" arg into every tool schema, required to come first</span>
<span class="kw">def</span> <span class="fn">add_inner_thoughts_to_functions</span>(functions, inner_thoughts_key, inner_thoughts_description,
                                    inner_thoughts_required=<span class="kw">True</span>, put_inner_thoughts_first=<span class="kw">True</span>):
    <span class="kw">for</span> schema <span class="kw">in</span> functions:
        props = schema[<span class="st">"parameters"</span>][<span class="st">"properties"</span>]
        <span class="cm"># insert inner_thoughts as the "first" property (key defaults to "thinking")</span>
        schema[<span class="st">"parameters"</span>][<span class="st">"properties"</span>] = {
            inner_thoughts_key: {<span class="st">"type"</span>: <span class="st">"string"</span>, <span class="st">"description"</span>: inner_thoughts_description},
            **props,
        }
        schema[<span class="st">"parameters"</span>][<span class="st">"required"</span>].insert(<span class="nb">0</span>, inner_thoughts_key)  <span class="cm"># required and first</span>
    <span class="kw">return</span> functions
</pre></div>

<p>That "description" matters too. <span class="mono">local_llm/constants.py</span> holds two versions: the plain <span class="mono">INNER_THOUGHTS_KWARG_DESCRIPTION</span> ("Deep inner monologue private to you only."), and the <strong>forcing</strong> <span class="mono">..._GO_FIRST</span> which adds "<em>Think before you act, so always generate arg 'thinking' first before any other arg.</em>" — a natural-language command to "generate thinking first." After the model replies, Letta uses <span class="mono">unpack_inner_thoughts_from_kwargs</span> to <strong>pop</strong> that <span class="mono">thinking</span> out of the tool arguments and place it into the assistant message's content (that's the origin of the inner_thoughts in the cellgroup above). To everything upstream, it looks like the model "spoke a monologue, then called a tool."</p>

<div class="card spark">
  <div class="tag">💡 Design spark</div>
  <strong>Making the "chain of thought" a tool argument — that's this lesson's "aha."</strong> The mainstream approach hopes the model has a "thinking channel," or begs it in the prompt to "please think step by step"; but channels <strong>aren't universal</strong> and pleas <strong>can be ignored</strong>. Letta picks a fundamentally different fulcrum: since the agent must call a tool to act, and a tool call <strong>must conform to the schema</strong>, write "think first" into the schema itself — add a <span class="mono">thinking</span> argument, mark it <strong>required</strong>, put it <strong>first (put_inner_thoughts_first)</strong>, and have the description order "always generate it first." So "reasoning" goes from "<strong>hopefully it thinks</strong>" to "<strong>the thought is a required argument — omit it and the call is invalid</strong>" (its first position is enforced by property order plus the explicit "generate it first" instruction). Even better, this trick is <strong>provider-agnostic</strong>: any model that supports function calling — even one with zero native thinking ability — is <strong>forced by this structure to "reason before acting."</strong> One argument turns a "soft constraint" into a "hard constraint."
</div>

<div class="card detail">
  <div class="tag">🔬 Source map</div>
  Where each piece lives: <strong>function → schema</strong> in <span class="mono">letta/functions/schema_generator.py::generate_schema</span> (reads signature + docstring; <span class="mono">TOOL_RESERVED_KWARGS</span> filters out <span class="mono">self / agent_state</span>); <strong>injecting the monologue</strong> in <span class="mono">letta/llm_api/helpers.py::add_inner_thoughts_to_functions</span>, recovered in the same file's <span class="mono">unpack_inner_thoughts_from_kwargs</span>; <strong>the key &amp; descriptions</strong> in <span class="mono">letta/local_llm/constants.py</span> (<span class="mono">INNER_THOUGHTS_KWARG="thinking"</span>, <span class="mono">VALID_INNER_THOUGHTS_KWARGS</span>, <span class="mono">..._DESCRIPTION(_GO_FIRST)</span>); <strong>injection is triggered during request assembly</strong> in <span class="mono">letta/llm_api/openai.py</span> (when <span class="mono">llm_config.put_inner_thoughts_in_kwargs</span> is true); <strong>continuation</strong> in <span class="mono">letta/agents/letta_agent_v3.py</span> (<span class="mono">_decide_continuation</span>); <strong>tool execution</strong> in <span class="mono">letta/agents/letta_agent_v2.py</span> (<span class="mono">_execute_tool</span>, inherited by v3) → <span class="mono">ToolExecutionManager.execute_tool_async</span>.
</div>

<p>Fuse "function-call round-trip + ReAct continuation + the model only emits, never executes" into one pseudo-code block, and the agent's heartbeat is just this:</p>

<pre class="code"><span class="cm"># An agent's minimal loop (pseudo-code, maps to Lesson 3's step loop)</span>
messages = [system, ...history..., user_msg]
tools    = <span class="fn">add_inner_thoughts</span>(<span class="fn">to_schema</span>(my_tools))   <span class="cm"># thinking forced as the first arg</span>
<span class="kw">for</span> step <span class="kw">in</span> <span class="fn">range</span>(max_steps):                    <span class="cm"># default cap 50</span>
    reply = llm.<span class="fn">call</span>(messages, tools)            <span class="cm"># the model only "emits," never executes</span>
    <span class="kw">if</span> reply.tool_calls:                          <span class="cm"># it requests a tool</span>
        name, args = reply.tool_calls[<span class="nb">0</span>]
        result = runtime.<span class="fn">execute</span>(name, args)      <span class="cm"># your code actually runs it (sandboxed if needed)</span>
        messages += [reply, <span class="fn">tool_result</span>(result)]  <span class="cm"># feed result back -> trigger "think again"</span>
    <span class="kw">else</span>:
        <span class="kw">break</span>                                     <span class="cm"># no tool -> finish (end_turn)</span>
</pre>

<h2>Dig a little deeper</h2>

<details class="accordion"><summary>Why doesn't the model execute tools itself?</summary><div class="acc-body">
<p><strong>Example:</strong> the model emits <span class="mono">run_code("rm -rf /")</span>. If "emit" equaled "execute," you'd be done for. In fact it's just text it <strong>requests</strong> to run; whether it runs is your runtime's call.</p>
<p><strong>Why designed this way:</strong> because model output is <strong>inherently untrusted</strong> — it can be prompt-injected or hallucinate a dangerous call. Keeping the "decision" in the framework's hands lets you validate permissions, sanitize args, sandbox it, or outright refuse before execution. That's the "model proposes, runtime adjudicates" security boundary.</p>
<p><strong>Where in source:</strong> the execution entry <span class="mono">letta/agents/letta_agent_v2.py::LettaAgentV2._execute_tool</span> (inherited and called by <span class="mono">LettaAgentV3</span>) → <span class="mono">letta/services/tool_executor/tool_execution_manager.py::ToolExecutionManager.execute_tool_async</span>; custom tools go through the sandbox in <span class="mono">letta/services/tool_executor/sandbox_tool_executor.py</span>.</p>
<p><strong>Alternatives:</strong> some toy frameworks let the model <span class="mono">eval()</span> its own output — fast to build, but it hands root to a probabilistic string; never acceptable in production.</p>
</div></details>

<details class="accordion"><summary>Why stuff "thinking" into an argument instead of a separate field?</summary><div class="acc-body">
<p><strong>Example:</strong> the same agent runs on OpenAI today, Anthropic tomorrow, local LM Studio the day after. If "thinking" relied on each vendor's private reasoning field, you'd write an adapter per vendor — and some vendors have no such channel at all.</p>
<p><strong>Why designed this way:</strong> every function-calling provider honors a schema's <span class="mono">required</span> list and parameter order. Making <span class="mono">thinking</span> an ordinary "required and first" parameter uses the <strong>greatest common denominator</strong> capability to buy <strong>cross-vendor consistency</strong> for "think before act," and even <strong>forces order</strong> (the GO_FIRST description orders it first). After the reply it's <span class="mono">unpack</span>ed back out as the monologue — transparent to everything above.</p>
<p><strong>Where in source:</strong> injection <span class="mono">letta/llm_api/helpers.py::add_inner_thoughts_to_functions</span> (<span class="mono">put_inner_thoughts_first=True</span>, <span class="mono">inner_thoughts_required=True</span>); recovery <span class="mono">unpack_inner_thoughts_from_kwargs</span>; description <span class="mono">letta/local_llm/constants.py::INNER_THOUGHTS_KWARG_DESCRIPTION_GO_FIRST</span>.</p>
<p><strong>Alternatives:</strong> ① rely on a native thinking channel — not universal; ② beg "please think step by step" in the system prompt — soft, ignorable; ③ open a separate non-tool field — back to the "every vendor differs" problem. Stuffing it into an argument has the widest coverage.</p>
</div></details>

<details class="accordion"><summary>ReAct loop vs a direct answer: when do you even need the round-trip?</summary><div class="acc-body">
<p><strong>Example:</strong> ask "what's 1+1" and the model answers in one round, no tool at all — ReAct degenerates into plain Q&amp;A. Ask "what was the project deadline I mentioned last week, and by the way what's the weather that day" and it must recall memory, then web_search — two or three tool rounds to answer.</p>
<p><strong>Why designed this way:</strong> the loop's value is that "<strong>when the model issues a call it hasn't seen the result yet</strong>." Only by feeding the result back and calling again can it continue on real information. Tasks that need to "peek at the outside world before deciding" require the round-trip; those answerable from existing knowledge hit <span class="mono">end_turn</span> on round one.</p>
<p><strong>Where in source:</strong> the continuation decision <span class="mono">letta/agents/letta_agent_v3.py::LettaAgentV3._decide_continuation</span> ("called a tool → continue, else stop"); the loop cap <span class="mono">letta/constants.py::DEFAULT_MAX_STEPS</span> (default 50).</p>
<p><strong>Alternatives:</strong> a loop-less "single function call" — fine for one-shot tasks, but no multi-step reasoning; a pure chain (hard-coded steps) — controllable but inflexible, the model can't decide its own next move. ReAct balances flexibility and control.</p>
</div></details>

<h2>Where this lesson sits on the big map</h2>
<p>Back to Part 1's spine: this lesson <strong>cracked open the core</strong> of Lesson 3's step loop — every beat it makes is one "<strong>function-call round-trip</strong>" (request carries schemas → model emits tool_call → runtime executes → result fed back → think again), and the continuation rule "called a tool → continue, else stop" is the direct expression of <strong>ReAct's "think-act-observe-think."</strong> You should now be able to <strong>match</strong> Lesson 3's <span class="mono">_step</span> with this lesson's ReAct loop: they're two tellings of the same thing.</p>

<p>And by <strong>welding "think before act" into the tool schema</strong>, Letta closes a loop on Lesson 1's "self-editing memory" story: the agent edits memory using tools like <span class="mono">core_memory_append</span>, and before calling one it's forced by the <span class="mono">thinking</span> argument to first write "why I'm editing this memory block." <strong>Memory, tools, and reasoning are strung together by one and the same mechanism in Letta.</strong></p>

<p>Looking ahead: <strong>Part 4 (the agent loop)</strong> magnifies this lesson's loop — continuation rules, parallel tools, <span class="mono">max_steps</span>, how streaming emits token by token; <strong>Part 5 (the tool system)</strong> magnifies the "tool" cell — how schemas are generated from functions, how <span class="mono">tool_rules</span> constrain call order, how the sandbox isolates execution, how MCP plugs in external tools. What this lesson gives you is the <strong>minimal mental model</strong> needed to read those parts: <strong>agent = an LLM that emits call requests + a runtime that actually executes + a loop stringing them together, plus an inner monologue stuffed into an argument that forces it to think first.</strong></p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>agent = LLM + tools + a loop</strong>: the model thinks and decides, tools touch the outside world, the loop strings them until the job is done.</li>
    <li><strong>function calling lives at the message layer</strong>: request carries tool schemas → the model only <strong>emits</strong> a <span class="mono">tool_call</span> (name + JSON args) → <strong>your runtime executes</strong> → tool result fed back → the model continues.</li>
    <li><strong>The model does not execute tools</strong>, it only issues a "call request"; the actual executor is <span class="mono">_execute_tool</span> / <span class="mono">ToolExecutionManager</span> (sandboxed if needed) — that's the security boundary.</li>
    <li><strong>Tool schemas are auto-generated from functions</strong> (<span class="mono">generate_schema</span>, reading signature + docstring); reserved params like <span class="mono">self / agent_state</span> aren't exposed to the model.</li>
    <li><strong>ReAct = think → act → observe → think again</strong>, the core of Lesson 3's step loop; the continuation rule is dead simple: called a tool → continue, else stop.</li>
    <li><strong>Inner monologue stuffed into an argument (the spark)</strong>: <span class="mono">add_inner_thoughts_to_functions</span> adds a required, first-position <span class="mono">thinking</span> argument to every tool, turning "reason before act" from a soft into a hard constraint across providers.</li>
  </ul>
</div>
""",
}

LESSON_05 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前四课我们一直在用一个词——"上下文窗口"——却从没真正拆开它：第 1 课说"上下文有限"是 Letta 存在的根本理由，第 3 课说要"稳定前缀 + 变化尾巴"，第 4 课说每一步都要"把整段剧本重新拼好再发给模型"。这三句话背后，是同一条被反复绕开的硬约束：<strong>上下文窗口是一笔固定大小、还按 token 计费的预算</strong>。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课就把这笔账摊开算清楚——模型怎么读这段 prompt（prefill 与 decode）、为什么稳定前缀能省真金白银（prefix cache）、为什么"把历史全塞进去"必然失败，以及 Letta 如何把这笔账<strong>量出来</strong>（<span class="mono">ContextWindowOverview</span>）并据此<strong>动手</strong>（逼近阈值就压缩）。读完你会明白：记忆系统不是锦上添花，而是被这条约束<strong>逼出来</strong>的刚需。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把上下文窗口想象成一张<strong>固定大小的办公桌台面</strong>。所有要"现在就看着办"的材料——系统说明书（system）、便利贴上的核心备忘（核心记忆）、刚来回的几封信（在窗消息）、还有一张"我能用哪些工具"的清单（工具 schema）——都得<strong>摊在这张桌面上</strong>；模型只能看见桌面上的东西，桌子外的一概看不到。桌面有两个残酷的事实：① <strong>它就这么大</strong>，新材料铺上来，旧的就得收走，否则放不下；② <strong>每一格都在计费</strong>——桌上铺得越满，每"看一眼"（每次调用）越贵、越慢。于是你被迫做一件事：<strong>把不常用的材料归档进抽屉，只在桌面留最相关的</strong>，要用时再取回来。这套"放不下就归档、要用再取回"的收拾动作，就是记忆管理；而 Letta 的高明之处在于，它会<strong>随时量一量桌面还剩多少、谁占了多少</strong>，快满了就自动收拾——这正是这一课的主线。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  一句话抓住本课：<strong>上下文窗口 = 模型一次能"看见"的、固定大小的 token 预算</strong>，它既<strong>有限</strong>、每个 token 又<strong>要花钱</strong>。这条预算里同时挤着 system、核心记忆、在窗消息、工具 schema 四样东西——这正是 Letta（乃至整个 MemGPT 思路）存在的<strong>根本约束</strong>：因为窗口装不下"全部历史"，才必须有<strong>分层记忆</strong>与<strong>"满了就压缩"</strong>。记住这条核心约束，后面记忆系统的一切设计都是它的回声。
</div>

<h2>有限的 token 预算：这才是核心约束</h2>
<p>先把"上下文窗口"翻译成一句大白话：<strong>模型一次调用最多能"看见"的 token 数，是一个写死的上限</strong>（比如 8k、128k、200k、甚至 1M）。token 是模型眼里的最小单位——一个汉字大约 1～2 个 token，一个常见英文单词约 1 个多。这个上限不是建议，是<strong>物理边界</strong>：超了，要么直接报错（<span class="mono">ContextWindowExceededError</span>），要么把最前面的内容悄悄截掉。更要命的是，这条预算<strong>不是只装对话历史</strong>——它得同时容纳四样东西，它们一起挤同一条预算：</p>

<div class="cellgroup">
  <div class="cg-cap"><b>一条固定大小的 token 预算</b>：下面这些加起来不能超过上限；逼近上限，就得把旧内容"换出"</div>
  <div class="cells">
    <span class="cell scale">system 提示</span>
    <span class="cell hl">核心记忆<br>persona / human</span>
    <span class="cell q">工具 schema</span>
    <span class="cell">在窗消息<br>（会增长）</span>
    <span class="cell dim">…放不下的</span>
  </div>
  <div class="cells">
    <span class="lab">← 稳定前缀（每轮尽量不动）</span>
    <span class="sep">|</span>
    <span class="lab">变化尾巴（不断增长）→</span>
  </div>
</div>

<p>把这四块一加你就明白了：<strong>真正留给"对话历史"的空间，是上限减去 system、核心记忆、工具清单之后的剩余</strong>。其中 system 与核心记忆是<strong>稳定前缀</strong>（每轮几乎不变，第 3 课讲过），工具 schema 也基本固定；只有"在窗消息"这条<strong>尾巴</strong>会随着对话不断变长。尾巴越长，离上限越近；一旦逼近，就必须把旧消息"换出"——要么截断、要么归档、要么压缩成摘要。<strong>这就是记忆管理的全部动机：预算有限，而尾巴只会增长。</strong></p>

<h2>模型怎么读这段 prompt：prefill 与 decode</h2>
<p>要理解"为什么稳定前缀能省钱"，得先看模型生成一次回复的两个阶段。它们的成本结构完全不同：</p>

<div class="flow">
  <div class="node"><div class="nt">① prefill 预填充</div><div class="nd">一次性"读完"整段 prompt<br>system+历史+工具，可并行</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">建立 KV cache</div><div class="nd">把读过的每个 token<br>算成键值对缓存起来</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">② decode 解码</div><div class="nd">一个一个往外吐 token<br>每吐一个都要回看缓存</div></div>
</div>

<p><strong>prefill</strong> 是"读题"：模型把你给的整段 prompt 一口吃下，<strong>所有输入 token 可以并行处理</strong>，算得快；这一步会顺手把每个 token 的中间结果（注意力的 key/value）存成 <strong>KV cache</strong>。<strong>decode</strong> 是"答题"：模型<strong>一次只生成一个 token</strong>，每生成一个都要回看前面所有 token 的 KV cache 再决定下一个——这一步天生串行，<strong>输出越长越慢</strong>。</p>

<p>两个关键结论：其一，<strong>输入越长，prefill 越贵</strong>（要读的 token 多）；其二，既然 prefill 会把前缀的 KV 都算出来缓存，那么<strong>如果这次请求的前缀和上次逐 token 一模一样，这部分缓存就能直接复用、不必重算</strong>——这就引出了 prefix cache。</p>

<h2>稳定前缀为什么省钱：prefix cache</h2>
<p>现代推理服务（以及一些本地引擎）都会做一件事：<strong>缓存"前缀"的计算结果</strong>。如果两次请求开头的一长串 token 完全相同，第二次就能<strong>跳过这段的 prefill</strong>，直接拿上次缓存好的 KV——又快又便宜（很多厂商对命中缓存的输入 token 直接打折计费）。关键词是<strong>"前缀必须逐 token 完全一致"</strong>：只要前面有一个 token 变了，从那之后的缓存全部作废、得重算。</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">第 1 轮</span>
    <span class="tslot span">system + 核心记忆（稳定前缀，全量 prefill）</span>
    <span class="tslot now">新消息</span>
  </div>
  <div class="lane"><span class="lane-label">第 2 轮</span>
    <span class="tslot span">同样的前缀 → 命中缓存，跳过重算</span>
    <span class="tslot">旧消息</span>
    <span class="tslot now">新消息</span>
  </div>
  <div class="lane"><span class="lane-label">省下的</span>
    <span class="tslot">前缀那段的 prefill 时间 &amp; 费用</span>
  </div>
</div>

<p>现在第 3 课那条设计原则就有了经济学解释：<strong>为什么要把 system + 核心记忆放在最前面、且每轮尽量不改？</strong>因为它们是<strong>最长、最稳定的那段前缀</strong>——保持它逐 token 不变，就能让每一轮都吃到 prefix cache，把这段昂贵的 prefill 省掉。反过来，如果你每轮都去改系统提示的开头（哪怕只改一个字），就等于<strong>亲手把缓存作废</strong>，每轮都全量重算。</p>

<div class="note tip"><span class="ni">📌</span><span class="nx"><strong>"稳定前缀 + 变化尾巴"不是审美，是 prefill / prefix-cache 经济学逼出来的结构。</strong>这也是为什么 Letta 在第 3 课里宁可"只往尾巴追加消息、记忆变了才重建系统提示"，也不肯每轮乱动前缀。</span></div>
<h2>Letta 把这笔账量出来，也据此动手</h2>
<p>到这里，约束和经济学都讲清楚了。Letta 的高明之处，是<strong>不把上下文窗口当黑盒</strong>：它能把"窗口里到底装了啥"<strong>逐块拆开计数</strong>，再据此在<strong>逼近上限时压缩</strong>。先看"计数"——它有一个专门的数据结构 <span class="mono">ContextWindowOverview</span>，是整个上下文窗口的一本<strong>token 账本</strong>（主要在检视 / 接口侧按需算出）：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/memory.py</span><span class="ln">class ContextWindowOverview（节选真实字段）</span></div>
<pre><span class="kw">class</span> <span class="fn">ContextWindowOverview</span>(BaseModel):
    context_window_size_max: int             <span class="cm"># 这个模型的上限（预算总额）</span>
    context_window_size_current: int         <span class="cm"># 当前已用了多少 token</span>
    num_tokens_system: int                   <span class="cm"># system 提示占多少</span>
    num_tokens_core_memory: int              <span class="cm"># 核心记忆（persona/human 块）占多少</span>
    num_tokens_functions_definitions: int    <span class="cm"># 工具 schema 占多少</span>
    num_tokens_messages: int                 <span class="cm"># 在窗消息占多少</span>
    num_tokens_summary_memory: int           <span class="cm"># 摘要记忆占多少</span>
    num_tokens_external_memory_summary: int  <span class="cm"># 外部记忆(归档/recall)元信息占多少</span>
    num_messages: int                        <span class="cm"># 在窗消息条数</span>
    num_archival_memory: int                 <span class="cm"># 归档记忆条数（在桌外）</span>
    num_recall_memory: int                   <span class="cm"># recall 记忆条数（在桌外）</span>
    <span class="cm"># ... 还带每段原文(system_prompt/core_memory/...)，便于审计</span>
</pre></div>

<p>看清这张账本，你就抓住了 Letta 的关键一手：它<strong>不把上下文当黑盒</strong>，而是把"上限多少、现在用了多少、每一块（system / 核心记忆 / 工具 / 消息 / 摘要）各占多少"全部<strong>拆开计数</strong>。这本账由 <span class="mono">ContextWindowCalculator.calculate_context_window</span> 现场算出来，背后用一组 <span class="mono">TokenCounter</span>（按 provider 分 <span class="mono">AnthropicTokenCounter</span> / <span class="mono">ApproxTokenCounter</span>）分别数 system、消息、工具的 token。<strong>能量化，才能决策。</strong></p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  这一课的每个环节落在哪：<strong>token 账本</strong>是 <span class="mono">letta/schemas/memory.py::ContextWindowOverview</span>；<strong>现场计算</strong>在 <span class="mono">letta/services/context_window_calculator/context_window_calculator.py::ContextWindowCalculator</span>（<span class="mono">calculate_context_window</span>），由 <span class="mono">letta/services/agent_manager.py::AgentManager.get_context_window</span> 调用；<strong>数 token</strong>用 <span class="mono">letta/services/context_window_calculator/token_counter.py::TokenCounter</span>（<span class="mono">count_text_tokens</span> / <span class="mono">count_message_tokens</span> / <span class="mono">count_tool_tokens</span>，实现类 <span class="mono">AnthropicTokenCounter</span> / <span class="mono">ApproxTokenCounter</span>）；<strong>压缩阈值</strong>在 <span class="mono">letta/services/summarizer/thresholds.py::get_compaction_trigger_threshold</span>（= <span class="mono">context_window × SUMMARIZATION_TRIGGER_MULTIPLIER</span>，后者在 <span class="mono">letta/constants.py</span> 为 0.9）；<strong>压缩动作</strong>在 <span class="mono">letta/agents/letta_agent_v3.py::LettaAgentV3</span>（<span class="mono">compact</span>，由 <span class="mono">_step</span> 在逼近阈值/超窗时触发）。
</div>

<p>至于"何时动手"，运行时为了快，并不每步都重算整本账，而是<strong>顺手记下每次模型调用返回的 token 用量</strong>，拿这个<strong>估算值</strong>和一个阈值比一比。这个阈值不等窗口真满才算，而是留了余量——默认在<strong>上限的 90%</strong> 就触发，避免真的撞上"prompt 太长"的报错：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/summarizer/thresholds.py</span><span class="ln">get_compaction_trigger_threshold（简化）</span></div>
<pre><span class="cm"># 压缩触发阈值 = 上下文窗口 × 0.9（留 10% 余量，避免撞上报错）</span>
SUMMARIZATION_TRIGGER_MULTIPLIER = <span class="nb">0.9</span>   <span class="cm"># letta/constants.py</span>

<span class="kw">def</span> <span class="fn">get_compaction_trigger_threshold</span>(llm_config, *, force_proactive=<span class="kw">False</span>):
    <span class="cm"># 不区分模型，一律取 上限 × 0.9（force_proactive 目前不改变结果）</span>
    <span class="kw">return</span> <span class="fn">int</span>(llm_config.context_window * SUMMARIZATION_TRIGGER_MULTIPLIER)
</pre></div>

<p>把"量"和"动"串进第 3、4 课那个 step 循环，就是下面这段伪代码——每走一步，先估算用量、再和阈值比，逼近了就压缩，然后才继续：</p>

<pre class="code"><span class="cm"># agent 每一步：估算上下文用量 -&gt; 比阈值 -&gt; 逼近就压缩（伪代码）</span>
threshold = <span class="fn">get_compaction_trigger_threshold</span>(llm_config)   <span class="cm"># = context_window * 0.9</span>
<span class="kw">for</span> step <span class="kw">in</span> <span class="fn">range</span>(max_steps):
    used = <span class="fn">estimate_tokens</span>(system, core_memory, tools, messages)
    <span class="kw">if</span> used &gt;= threshold:                       <span class="cm"># 桌面快满了</span>
        messages = <span class="fn">compact</span>(messages)            <span class="cm"># 把旧消息压成摘要，换出尾巴</span>
        <span class="fn">rebuild_system_prompt</span>()                 <span class="cm"># 压缩后重建系统提示（前缀只在这一刻变）</span>
    reply = llm.<span class="fn">call</span>(system, messages, tools)    <span class="cm"># prefill 整段 -&gt; decode 逐 token</span>
    <span class="kw">if</span> <span class="kw">not</span> reply.tool_calls:
        <span class="kw">break</span>
</pre>

<p>这条"度量 → 判定 → 压缩 → 重建前缀"的闭环，可以画成四步：</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>度量</h4><p>用 <span class="mono">TokenCounter</span> 数清 system / 核心记忆 / 工具 / 消息各占多少 token</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>判定</h4><p>当前用量是否 ≥ 阈值（<span class="mono">context_window × 0.9</span>）</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>压缩</h4><p><span class="mono">compact</span>：把较旧的在窗消息总结成摘要，腾出尾巴空间</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>重建前缀</h4><p>压缩后 <span class="mono">rebuild_system_prompt_async</span> 重写第 0 条消息，下一轮继续吃缓存</p></div></div>
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>上下文窗口就是 agent 的 RAM——而它"既有限、每个 token 又要花钱"，这一条经济事实，逼出了整个记忆系统。</strong>很多框架把"加记忆"当成可选功能；Letta 的视角根本不同：既然桌面就这么大、还按格子收费，那"管理记忆"就<strong>不是锦上添花，而是被经济规律逼出来的刚需</strong>。更妙的是，Letta 没有停在"知道有这约束"，而是把它做成了两件<strong>可操作</strong>的事：一是<strong>可度量</strong>——<span class="mono">ContextWindowOverview</span> 把窗口拆成一本逐项 token 账本，"用了多少、谁占的"一清二楚；二是<strong>可触发动作</strong>——一旦逼近 <span class="mono">context_window × 0.9</span> 的阈值，就自动 <span class="mono">compact</span> 把旧消息压成摘要。把这条线和第 3 课接上你会恍然大悟：<strong>"稳定前缀 + 变化尾巴"不是某人拍脑袋的风格，而是 prefill / prefix-cache 经济学的直接产物</strong>——前缀稳定才能命中缓存、省下最贵的那段 prefill。一句话：<strong>Letta 把"上下文很贵"这条物理约束，翻译成了"量得出、压得动"的工程闭环。</strong>
</div>

<h2>窗口满了，你只有两条路</h2>
<p>当尾巴增长到逼近上限，区别一个玩具 demo 和一个能长期运行的 agent 的，就是这一步怎么处理：</p>

<div class="cols">
  <div class="col">
    <h4>路 A：硬塞（玩具做法）</h4>
    <p>把所有历史一股脑塞进 prompt，指望"窗口够大就行"。结果：要么<strong>撞上上限报错</strong>（<span class="mono">ContextWindowExceededError</span>），要么把最早的消息<strong>悄悄截掉</strong>——agent 突然"失忆"，且你无法控制丢了什么。成本和延迟还随历史<strong>线性上涨</strong>。</p>
  </div>
  <div class="col">
    <h4>路 B：分层 + 压缩（Letta）</h4>
    <p>只把<strong>最相关</strong>的留在窗口（核心记忆 + 近期消息），其余<strong>归档到窗外</strong>（archival / recall，第三部分细讲），需要时再取回；逼近阈值就把旧消息<strong>压成摘要</strong>。窗口始终可控，历史不丢、可检索。</p>
  </div>
</div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>"上下文越大越好"是个危险的直觉。</strong>就算模型号称 1M token，把东西全塞进去也有三个代价：① <strong>更贵</strong>——按 token 计费，塞得越多每轮越烧钱；② <strong>更慢</strong>——prefill 要读的 token 越多、延迟越高；③ <strong>反而更笨</strong>——研究反复发现"<span class="mono">lost in the middle</span>"：放在超长上下文<strong>中间</strong>的信息最容易被模型忽略，关键内容淹没在噪声里，答得还不如精简上下文准。所以"长上下文模型"只是<strong>放宽</strong>了约束，<strong>并没有取消它</strong>——你仍然需要"放什么、不放什么"的记忆管理。
</div>

<table class="t">
  <tr><th>做法</th><th>成本 / 延迟</th><th>记得住多久</th><th>失忆风险</th></tr>
  <tr><td>裸塞历史进 prompt</td><td>随历史线性上涨</td><td>到窗口满为止</td><td>高：满了就截断 / 报错</td></tr>
  <tr><td>只靠超长上下文模型</td><td>更高（读得越多越贵）</td><td>更久，但仍有上限</td><td>中：lost-in-the-middle</td></tr>
  <tr><td><strong>Letta：分层 + 压缩</strong></td><td><strong>可控（前缀吃缓存）</strong></td><td><strong>理论无限（归档可检索）</strong></td><td><strong>低：旧消息压成摘要，不丢</strong></td></tr>
</table>

<h2>再挖深一点</h2>

<details class="accordion"><summary>prefill / decode / KV cache，一分钟搞懂</summary><div class="acc-body">
<p><strong>示例：</strong>你发一段 2000 token 的 prompt，模型回 200 token。prefill 阶段一次性"读"这 2000 个输入 token（可并行，快）；decode 阶段把那 200 个输出 token <strong>一个一个</strong>生成（串行，慢）。</p>
<p><strong>为什么这样设计：</strong>Transformer 算注意力时，每个新 token 都要和前面所有 token 比一遍。把前面 token 的 key/value 算一次就<strong>缓存（KV cache）</strong>起来，之后每生成一个新 token 只需算它自己、再去查缓存，避免重复计算。代价是缓存要占显存，所以上下文越长越吃显存——这也是窗口有上限的原因之一。</p>
<p><strong>源码在哪：</strong>Letta 不自己跑推理（那是 provider / 推理引擎的事），但它<strong>估算</strong>这些 token 账：<span class="mono">letta/services/context_window_calculator/token_counter.py::TokenCounter</span> 负责数 token，<span class="mono">ContextWindowCalculator.calculate_context_window</span> 汇总成账本。</p>
<p><strong>还有什么替代：</strong>不缓存就每生成一个新 token 都从头重算整段注意力——慢到不可用；这正是 KV cache 成为现代推理标配的原因。</p>
</div></details>

<details class="accordion"><summary>为什么"稳定前缀"能省钱（prefix cache）</summary><div class="acc-body">
<p><strong>示例：</strong>两轮请求都以同样的 system + 核心记忆开头，只是结尾多了一条新消息。第二轮里，那段相同的开头能直接命中上一轮缓存的 KV，<strong>跳过 prefill</strong>。</p>
<p><strong>为什么这样设计：</strong>prefill 是按输入 token 收费 / 耗时的，而前缀往往又长又稳定（system + persona / human）。只要逐 token 一致就能复用缓存，于是"别乱动前缀"直接转化成省钱省延迟。Letta 因此选择：正常步骤里<strong>不</strong>刷新系统提示，只往尾巴追加消息；只有记忆变化或压缩后才重建前缀。</p>
<p><strong>源码在哪：</strong>第 3 课的 <span class="mono">letta/services/agent_manager.py::rebuild_system_prompt_async</span>——它只在必要时（记忆变更 / 压缩后）重写第 0 条 system 消息；<span class="mono">letta/agents/letta_agent_v3.py</span> 的步骤注释明确写着"跳过 system 刷新以保留 prefix 缓存"。</p>
<p><strong>还有什么替代：</strong>每轮都重建系统提示——简单，但<strong>每轮都作废缓存</strong>、全量重算，长对话下成本高得多。</p>
</div></details>

<details class="accordion"><summary>"换个长上下文模型不就行了？"</summary><div class="acc-body">
<p><strong>示例：</strong>把模型从 8k 换成 1M 上下文，似乎就能把所有历史塞进去。但跑久了你会发现：账单飙升、响应变慢，而且模型经常"看不见"埋在中间的关键信息。</p>
<p><strong>为什么这样设计：</strong>长上下文<strong>抬高了上限</strong>，但三条代价没消失——成本随 token 线性涨、prefill 延迟随长度涨、"lost in the middle"让中段信息被忽略。约束被<strong>放宽</strong>而非<strong>取消</strong>，所以"放什么进窗口"的决策依然要做。Letta 的分层记忆 + 压缩，就是这个决策的系统化答案。</p>
<p><strong>源码在哪：</strong>阈值仍按窗口比例算（<span class="mono">get_compaction_trigger_threshold</span> = <span class="mono">context_window × 0.9</span>）——窗口再大，逼近 90% 照样压缩；账本 <span class="mono">ContextWindowOverview</span> 对大窗口同样适用。</p>
<p><strong>还有什么替代：</strong>无限堆上下文——被成本和 lost-in-the-middle 反噬；纯向量检索（RAG）外挂——能扩容，但缺少"agent 自己编辑 / 分层"的主动记忆管理，正是第三部分要补的。</p>
</div></details>

<h2>这一课在整张大图的哪里</h2>
<p>把前五课串起来：第 1 课说 Letta 的根本理由是"LLM 无状态 + 上下文有限"，第 3 课给了"稳定前缀 + 变化尾巴"的结构，第 4 课展示了每一步都要把整段上下文重拼再发。<strong>这一课补上了那块缺失的"为什么"</strong>：因为上下文是一笔<strong>有限且按 token 计费的预算</strong>，prefill / prefix-cache 的经济学让"稳定前缀"成为省钱的硬道理，而"尾巴只会增长"让"换出旧内容"成为迟早要做的事。Letta 没有回避，而是把它量化成 <span class="mono">ContextWindowOverview</span>、把动作触发在 <span class="mono">context_window × 0.9</span>。</p>

<div class="note info"><span class="ni">👉</span><span class="nx">顺着这条逻辑，下一站就水到渠成：<strong>既然预算有限、尾巴必须换出，那"换出去的东西放哪、怎么取回、agent 怎么自己管"——这就是"记忆系统"要回答的问题，也正是第三部分的主题。</strong></span></div>

<p>核心记忆（始终在窗的 persona / human）、recall（可检索的历史消息）、archival（可检索的长期事实）这三层，本质上就是"桌面 + 抽屉 + 档案室"的工程实现——是对本课这条约束的<strong>正面回答</strong>。读完第三部分，你会看到 <span class="mono">compact</span> 压出来的摘要、归档进去的消息、agent 用记忆工具自我编辑的闭环，如何共同把"有限窗口"变成"看起来无限的记忆"。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>核心约束 = 有限的 token 预算</strong>：一次调用能看见的 token 有写死的上限，且 system + 核心记忆 + 工具 schema + 在窗消息<strong>共享</strong>这条预算。</li>
    <li><strong>prefill vs decode</strong>：prefill 并行读入整段 prompt（越长越贵），decode 串行逐 token 生成（越长越慢）；prefill 会建立 KV cache。</li>
    <li><strong>稳定前缀省钱（prefix cache）</strong>：前缀逐 token 一致就能命中缓存、跳过 prefill——这正是第 3 课"稳定前缀 + 变化尾巴"的经济学原因。</li>
    <li><strong>Letta 量化它</strong>：<span class="mono">ContextWindowOverview</span> 把窗口拆成逐项 token 账本（<span class="mono">ContextWindowCalculator</span> + <span class="mono">TokenCounter</span> 现场计算）。</li>
    <li><strong>Letta 据此行动</strong>：逼近 <span class="mono">context_window × 0.9</span>（<span class="mono">get_compaction_trigger_threshold</span>）就 <span class="mono">compact</span> 压缩旧消息。</li>
    <li><strong>更多上下文 ≠ 更好</strong>：成本、延迟、lost-in-the-middle 三重代价；长上下文放宽约束但不取消它——记忆管理仍是刚需，正是第三部分的主题。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
We've leaned on one phrase for four lessons — "the context window" — without ever cracking it open: Lesson 1 said "context is finite" is the root reason Letta exists, Lesson 3 said keep a "stable prefix + a changing tail," Lesson 4 said every step has to "re-assemble the whole script and send it to the model." Behind all three sits the same hard constraint we kept dodging: <strong>the context window is a fixed-size budget that is also billed per token</strong>.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson lays that bill out in full — how the model reads the prompt (prefill and decode), why a stable prefix saves real money (prefix cache), why "just stuff all the history in" is doomed, and how Letta <strong>measures</strong> the bill (<span class="mono">ContextWindowOverview</span>) and <strong>acts</strong> on it (compact as it nears a threshold). By the end you'll see: a memory system isn't a nice-to-have, it's a necessity <strong>forced</strong> by this constraint.
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture the context window as a <strong>fixed-size desktop</strong>. Everything you need to "act on right now" — the manual (system), the sticky-note core memos (core memory), the few letters just exchanged (in-context messages), and a checklist of "which tools I can use" (tool schemas) — all has to be <strong>spread out on this desktop</strong>; the model can only see what's on the desk, nothing off it. The desk has two brutal facts: ① <strong>it's only this big</strong> — lay down something new and something old must go, or it won't fit; ② <strong>every square is billed</strong> — the fuller the desk, the more expensive and slower each "glance" (each call). So you're forced into one habit: <strong>file the rarely-used material into a drawer, keep only the most relevant on the desk</strong>, fetch it back when needed. That "file it when it won't fit, fetch it when you need it" tidying <strong>is</strong> memory management; and Letta's cleverness is that it <strong>constantly measures how much desk is left and who's using it</strong>, tidying up automatically as it fills — the throughline of this lesson.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  Grab this lesson in one line: <strong>the context window = a fixed-size token budget the model can "see" in a single call</strong> — it is both <strong>finite</strong> and <strong>costly per token</strong>. That budget is shared at once by four things: the system prompt, core memory, in-context messages, and tool schemas. This is the <strong>root constraint</strong> that Letta — and the whole MemGPT idea — exists to answer: because the window cannot hold "all of history," you must have <strong>tiered memory</strong> and <strong>"compact when it fills."</strong> Hold onto this constraint; every later memory-system design is an echo of it.
</div>

<h2>A finite token budget: this is the core constraint</h2>
<p>First, plain English for "context window": <strong>the maximum number of tokens a model can "see" in one call is a hard-coded ceiling</strong> (say 8k, 128k, 200k, even 1M). A token is the model's smallest unit — a Chinese character is roughly 1-2 tokens, a common English word about one. This ceiling isn't a suggestion, it's a <strong>physical boundary</strong>: exceed it and you either get an error (<span class="mono">ContextWindowExceededError</span>) or the earliest content gets silently truncated. Worse, this budget <strong>doesn't only hold conversation history</strong> — it must simultaneously fit four things, all squeezed into the same budget:</p>

<div class="cellgroup">
  <div class="cg-cap"><b>One fixed-size token budget</b>: the items below must sum to under the ceiling; as you near it, old content must be "swapped out"</div>
  <div class="cells">
    <span class="cell scale">system prompt</span>
    <span class="cell hl">core memory<br>persona / human</span>
    <span class="cell q">tool schemas</span>
    <span class="cell">in-context msgs<br>(grows)</span>
    <span class="cell dim">…what won't fit</span>
  </div>
  <div class="cells">
    <span class="lab">← stable prefix (kept put each turn)</span>
    <span class="sep">|</span>
    <span class="lab">changing tail (keeps growing) →</span>
  </div>
</div>

<p>Add those four up and it clicks: <strong>the room actually left for "conversation history" is the ceiling minus system, core memory, and the tool list</strong>. Of these, system and core memory are the <strong>stable prefix</strong> (barely changing each turn, as Lesson 3 explained), and tool schemas are mostly fixed too; only the "in-context messages" <strong>tail</strong> keeps growing as the dialogue goes on. The longer the tail, the closer to the ceiling; once you near it, old messages must be "swapped out" — truncated, archived, or compressed into a summary. <strong>That's the entire motive for memory management: the budget is finite, and the tail only grows.</strong></p>

<h2>How the model reads the prompt: prefill and decode</h2>
<p>To understand "why a stable prefix saves money," first look at the two phases of generating one reply. Their cost structures are completely different:</p>

<div class="flow">
  <div class="node"><div class="nt">① prefill</div><div class="nd">"reads" the whole prompt at once<br>system+history+tools, in parallel</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">build KV cache</div><div class="nd">every token read becomes<br>a cached key/value pair</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">② decode</div><div class="nd">emits tokens one by one<br>each one re-reads the cache</div></div>
</div>

<p><strong>prefill</strong> is "reading the question": the model swallows your whole prompt in one bite, <strong>all input tokens processed in parallel</strong>, so it's fast; along the way it stores each token's intermediate results (the attention key/value) as a <strong>KV cache</strong>. <strong>decode</strong> is "answering": the model <strong>generates one token at a time</strong>, each time re-reading the KV cache of all prior tokens before deciding the next — inherently serial, so <strong>the longer the output, the slower</strong>.</p>

<p>Two key takeaways: first, <strong>longer input means costlier prefill</strong> (more tokens to read); second, since prefill computes and caches the prefix's KV, then <strong>if this request's prefix is token-for-token identical to last time, that cache can be reused, no recompute</strong> — which brings us to prefix cache.</p>

<h2>Why a stable prefix saves money: prefix cache</h2>
<p>Modern inference services (and some local engines) all do one thing: <strong>cache the computed result of the "prefix."</strong> If the long opening run of tokens is identical across two requests, the second can <strong>skip that prefill</strong> and grab last time's cached KV directly — faster and cheaper (many providers bill cache-hit input tokens at a discount). The keyword is <strong>"the prefix must be token-for-token identical"</strong>: change a single earlier token and every cache entry after it is invalidated and must be recomputed.</p>

<div class="timeline">
  <div class="lane"><span class="lane-label">turn 1</span>
    <span class="tslot span">system + core memory (stable prefix, full prefill)</span>
    <span class="tslot now">new msg</span>
  </div>
  <div class="lane"><span class="lane-label">turn 2</span>
    <span class="tslot span">same prefix → cache hit, skip recompute</span>
    <span class="tslot">old msgs</span>
    <span class="tslot now">new msg</span>
  </div>
  <div class="lane"><span class="lane-label">saved</span>
    <span class="tslot">the prefix's prefill time &amp; cost</span>
  </div>
</div>

<p>Now Lesson 3's design principle has an economic explanation: <strong>why put system + core memory at the very front and barely touch it each turn?</strong> Because they're the <strong>longest, most stable prefix</strong> — keep it token-for-token unchanged and every turn hits the prefix cache, sparing that expensive prefill. Conversely, edit the opening of the system prompt each turn (even by one character) and you've <strong>invalidated the cache by hand</strong>, forcing a full recompute every turn.</p>

<div class="note tip"><span class="ni">📌</span><span class="nx"><strong>"Stable prefix + changing tail" is not aesthetics, it's a structure forced by prefill / prefix-cache economics.</strong> That's also why, back in Lesson 3, Letta would rather "only append messages to the tail and rebuild the system prompt only when memory changes" than fiddle with the prefix every turn.</span></div>
<h2>Letta measures the bill, and acts on it</h2>
<p>By here, both the constraint and the economics are clear. Letta's cleverness is that it <strong>doesn't treat the context window as a black box</strong>: it can count, <strong>block by block</strong>, exactly "what's in the window," and compress as it <strong>approaches the ceiling</strong>. Take "counting" first — it has a dedicated data structure, <span class="mono">ContextWindowOverview</span>, a <strong>token ledger</strong> for the whole window (computed on demand, mainly on the inspection / API side):</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/memory.py</span><span class="ln">class ContextWindowOverview (real fields, excerpt)</span></div>
<pre><span class="kw">class</span> <span class="fn">ContextWindowOverview</span>(BaseModel):
    context_window_size_max: int             <span class="cm"># this model's ceiling (total budget)</span>
    context_window_size_current: int         <span class="cm"># how many tokens used right now</span>
    num_tokens_system: int                   <span class="cm"># tokens in the system prompt</span>
    num_tokens_core_memory: int              <span class="cm"># tokens in core memory (persona/human)</span>
    num_tokens_functions_definitions: int    <span class="cm"># tokens in the tool schemas</span>
    num_tokens_messages: int                 <span class="cm"># tokens in in-context messages</span>
    num_tokens_summary_memory: int           <span class="cm"># tokens in the summary memory</span>
    num_tokens_external_memory_summary: int  <span class="cm"># tokens for external (archival/recall) metadata</span>
    num_messages: int                        <span class="cm"># count of in-context messages</span>
    num_archival_memory: int                 <span class="cm"># count of archival items (off-desk)</span>
    num_recall_memory: int                   <span class="cm"># count of recall items (off-desk)</span>
    <span class="cm"># ... also carries each section's text (system_prompt/core_memory/...) for auditing</span>
</pre></div>

<p>See this ledger and you've grasped Letta's key move: it <strong>doesn't treat context as a black box</strong> — it <strong>counts every piece separately</strong>: what's the ceiling, how much is used now, and how much each block (system / core memory / tools / messages / summary) takes. The ledger is computed on the spot by <span class="mono">ContextWindowCalculator.calculate_context_window</span>, backed by a set of <span class="mono">TokenCounter</span>s (per provider: <span class="mono">AnthropicTokenCounter</span> / <span class="mono">ApproxTokenCounter</span>) that count system, message, and tool tokens. <strong>You can only decide what you can quantify.</strong></p>

<div class="card detail">
  <div class="tag">🔬 Source map</div>
  Where each beat of this lesson lives: the <strong>token ledger</strong> is <span class="mono">letta/schemas/memory.py::ContextWindowOverview</span>; the <strong>on-the-spot calculation</strong> is in <span class="mono">letta/services/context_window_calculator/context_window_calculator.py::ContextWindowCalculator</span> (<span class="mono">calculate_context_window</span>), called by <span class="mono">letta/services/agent_manager.py::AgentManager.get_context_window</span>; <strong>counting tokens</strong> uses <span class="mono">letta/services/context_window_calculator/token_counter.py::TokenCounter</span> (<span class="mono">count_text_tokens</span> / <span class="mono">count_message_tokens</span> / <span class="mono">count_tool_tokens</span>, implemented by <span class="mono">AnthropicTokenCounter</span> / <span class="mono">ApproxTokenCounter</span>); the <strong>compaction threshold</strong> is in <span class="mono">letta/services/summarizer/thresholds.py::get_compaction_trigger_threshold</span> (= <span class="mono">context_window × SUMMARIZATION_TRIGGER_MULTIPLIER</span>, the latter 0.9 in <span class="mono">letta/constants.py</span>); the <strong>compaction action</strong> is in <span class="mono">letta/agents/letta_agent_v3.py::LettaAgentV3</span> (<span class="mono">compact</span>, triggered by <span class="mono">_step</span> near the threshold / on overflow).
</div>

<p>As for "when to act," the runtime — for speed — doesn't recompute the whole ledger every step; it just <strong>notes the token usage each model call reports back</strong> and compares that <strong>estimate</strong> to a threshold. That threshold doesn't wait until the window is full — it leaves headroom, firing by default at <strong>90% of the ceiling</strong> to avoid actually hitting the "prompt too long" error:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/services/summarizer/thresholds.py</span><span class="ln">get_compaction_trigger_threshold (simplified)</span></div>
<pre><span class="cm"># compaction trigger threshold = context window * 0.9 (10% headroom to avoid errors)</span>
SUMMARIZATION_TRIGGER_MULTIPLIER = <span class="nb">0.9</span>   <span class="cm"># letta/constants.py</span>

<span class="kw">def</span> <span class="fn">get_compaction_trigger_threshold</span>(llm_config, *, force_proactive=<span class="kw">False</span>):
    <span class="cm"># Same for every model: context_window * 0.9 (force_proactive currently unused)</span>
    <span class="kw">return</span> <span class="fn">int</span>(llm_config.context_window * SUMMARIZATION_TRIGGER_MULTIPLIER)
</pre></div>

<p>String "measure" and "act" into that step loop from Lessons 3 and 4, and you get the pseudocode below — each step, estimate usage, compare to the threshold, compress if near, then continue:</p>

<pre class="code"><span class="cm"># each agent step: estimate context usage -&gt; compare threshold -&gt; compress if near (pseudocode)</span>
threshold = <span class="fn">get_compaction_trigger_threshold</span>(llm_config)   <span class="cm"># = context_window * 0.9</span>
<span class="kw">for</span> step <span class="kw">in</span> <span class="fn">range</span>(max_steps):
    used = <span class="fn">estimate_tokens</span>(system, core_memory, tools, messages)
    <span class="kw">if</span> used &gt;= threshold:                       <span class="cm"># desk is nearly full</span>
        messages = <span class="fn">compact</span>(messages)            <span class="cm"># summarize old msgs, swap out the tail</span>
        <span class="fn">rebuild_system_prompt</span>()                 <span class="cm"># rebuild prompt post-compaction (prefix changes only now)</span>
    reply = llm.<span class="fn">call</span>(system, messages, tools)    <span class="cm"># prefill whole -&gt; decode token by token</span>
    <span class="kw">if</span> <span class="kw">not</span> reply.tool_calls:
        <span class="kw">break</span>
</pre>

<p>This "measure → decide → compact → rebuild prefix" loop draws as four steps:</p>

<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Measure</h4><p>use <span class="mono">TokenCounter</span> to count tokens for system / core memory / tools / messages</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Decide</h4><p>is current usage ≥ the threshold (<span class="mono">context_window × 0.9</span>)?</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Compact</h4><p><span class="mono">compact</span>: summarize older in-context messages, freeing tail space</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Rebuild prefix</h4><p>post-compaction, <span class="mono">rebuild_system_prompt_async</span> rewrites message 0 so the next turn keeps hitting the cache</p></div></div>
</div>

<div class="card spark">
  <div class="tag">💡 The spark</div>
  <strong>The context window is the agent's RAM — and it's both finite AND costly per token. That one economic fact forces the entire memory system into existence.</strong> Many frameworks treat "add memory" as an optional feature; Letta's view is fundamentally different: since the desk is only this big and billed by the square, "managing memory" is <strong>not a nice-to-have but a necessity forced by economics</strong>. Better still, Letta doesn't stop at "knowing the constraint exists" — it turns it into two <strong>actionable</strong> things: one, it's <strong>measurable</strong> — <span class="mono">ContextWindowOverview</span> breaks the window into an itemized token ledger, so "how much is used, by whom" is crystal clear; two, it's <strong>action-triggering</strong> — once usage nears the <span class="mono">context_window × 0.9</span> threshold, it auto-<span class="mono">compact</span>s old messages into a summary. Wire this to Lesson 3 and it dawns on you: <strong>"stable prefix + changing tail" wasn't someone's stylistic whim, it's a direct product of prefill / prefix-cache economics</strong> — only a stable prefix hits the cache and spares the priciest prefill. In one line: <strong>Letta translates the physical constraint "context is expensive" into an engineering loop that's "measurable and compressible."</strong>
</div>

<h2>When the window is full, you have exactly two roads</h2>
<p>When the tail grows to near the ceiling, what separates a toy demo from a long-running agent is how this step is handled:</p>

<div class="cols">
  <div class="col">
    <h4>Road A: cram it in (the toy way)</h4>
    <p>Stuff all history into the prompt and hope "a big enough window will do." Result: either you <strong>hit the ceiling error</strong> (<span class="mono">ContextWindowExceededError</span>) or the earliest messages get <strong>silently truncated</strong> — the agent suddenly "forgets," and you can't control what was lost. Cost and latency also rise <strong>linearly</strong> with history.</p>
  </div>
  <div class="col">
    <h4>Road B: tiered + compress (Letta)</h4>
    <p>Keep only the <strong>most relevant</strong> in the window (core memory + recent messages), <strong>archive the rest off-window</strong> (archival / recall, detailed in Part 3), fetch back on demand; near the threshold, <strong>compress old messages into a summary</strong>. The window stays bounded, history is kept and searchable.</p>
  </div>
</div>

<div class="card warn">
  <div class="tag">⚠️ Common misconception</div>
  <strong>"Bigger context is always better" is a dangerous intuition.</strong> Even if a model boasts 1M tokens, cramming everything in has three costs: ① <strong>pricier</strong> — billed per token, the more you stuff, the more each turn burns; ② <strong>slower</strong> — the more tokens prefill must read, the higher the latency; ③ <strong>actually dumber</strong> — research keeps finding "<span class="mono">lost in the middle</span>": information placed in the <strong>middle</strong> of a very long context is the most likely to be ignored, key content drowning in noise, often less accurate than a trimmed context. So a "long-context model" only <strong>loosens</strong> the constraint, it doesn't <strong>remove</strong> it — you still need the memory management of "what to put in, what to leave out."
</div>

<table class="t">
  <tr><th>approach</th><th>cost / latency</th><th>how long it remembers</th><th>amnesia risk</th></tr>
  <tr><td>raw-stuff history into prompt</td><td>rises linearly with history</td><td>until the window fills</td><td>high: truncates / errors when full</td></tr>
  <tr><td>rely on a long-context model only</td><td>higher (more to read)</td><td>longer, but still capped</td><td>medium: lost-in-the-middle</td></tr>
  <tr><td><strong>Letta: tiered + compress</strong></td><td><strong>bounded (prefix hits cache)</strong></td><td><strong>effectively unlimited (archive is searchable)</strong></td><td><strong>low: old msgs summarized, not lost</strong></td></tr>
</table>

<h2>Digging a little deeper</h2>

<details class="accordion"><summary>prefill / decode / KV cache, in one minute</summary><div class="acc-body">
<p><strong>Example:</strong> you send a 2000-token prompt and the model replies with 200 tokens. The prefill phase "reads" those 2000 input tokens at once (parallel, fast); the decode phase generates those 200 output tokens <strong>one at a time</strong> (serial, slow).</p>
<p><strong>Why designed this way:</strong> when a Transformer computes attention, each new token must compare against all prior tokens. Compute each prior token's key/value once and <strong>cache it (the KV cache)</strong>, then each new token only computes itself and looks up the cache, avoiding repeated work. The price is that the cache eats GPU memory, so longer context costs more memory — one reason the window has a ceiling at all.</p>
<p><strong>Where in the source:</strong> Letta doesn't run inference itself (that's the provider / inference engine), but it <strong>estimates</strong> these token bills: <span class="mono">letta/services/context_window_calculator/token_counter.py::TokenCounter</span> counts tokens, and <span class="mono">ContextWindowCalculator.calculate_context_window</span> aggregates the ledger.</p>
<p><strong>Alternatives:</strong> without caching, every new token recomputes the whole attention from scratch — unusably slow; that's exactly why the KV cache is standard in modern inference.</p>
</div></details>

<details class="accordion"><summary>Why a "stable prefix" saves money (prefix cache)</summary><div class="acc-body">
<p><strong>Example:</strong> two requests both open with the same system + core memory, differing only by one new message at the end. In the second, that identical opening can hit the previous turn's cached KV and <strong>skip prefill</strong>.</p>
<p><strong>Why designed this way:</strong> prefill is billed / timed by input tokens, and the prefix tends to be long and stable (system + persona / human). As long as it's token-for-token identical, the cache is reusable, so "don't fiddle with the prefix" converts directly into saved money and latency. Letta therefore chooses: during normal steps it does <strong>not</strong> refresh the system prompt, only appends messages to the tail; it rebuilds the prefix only after memory changes or compaction.</p>
<p><strong>Where in the source:</strong> Lesson 3's <span class="mono">letta/services/agent_manager.py::rebuild_system_prompt_async</span> rewrites message 0 only when needed (memory change / post-compaction); <span class="mono">letta/agents/letta_agent_v3.py</span>'s step comments explicitly say "skip system refresh to preserve prefix caching."</p>
<p><strong>Alternatives:</strong> rebuild the system prompt every turn — simple, but <strong>invalidates the cache every turn</strong> and recomputes in full, far costlier over long dialogues.</p>
</div></details>

<details class="accordion"><summary>"Can't I just switch to a long-context model?"</summary><div class="acc-body">
<p><strong>Example:</strong> swap the model from 8k to 1M context and it seems you could stuff all history in. But run it long enough and you'll find: the bill spikes, responses slow down, and the model often "can't see" key info buried in the middle.</p>
<p><strong>Why designed this way:</strong> long context <strong>raises the ceiling</strong>, but the three costs don't vanish — cost rises linearly with tokens, prefill latency rises with length, and "lost in the middle" ignores mid-context info. The constraint is <strong>loosened</strong>, not <strong>removed</strong>, so the "what goes into the window" decision still has to be made. Letta's tiered memory + compaction is the systematic answer to that decision.</p>
<p><strong>Where in the source:</strong> the threshold is still computed as a fraction of the window (<span class="mono">get_compaction_trigger_threshold</span> = <span class="mono">context_window × 0.9</span>) — no matter how big the window, nearing 90% still triggers compaction; the ledger <span class="mono">ContextWindowOverview</span> applies to big windows just the same.</p>
<p><strong>Alternatives:</strong> pile on infinite context — bitten by cost and lost-in-the-middle; bolt on pure vector retrieval (RAG) — it scales storage but lacks the "agent self-edits / tiers" active memory management that Part 3 fills in.</p>
</div></details>

<h2>Where this lesson sits on the big map</h2>
<p>Stringing the five lessons together: Lesson 1 said Letta's root reason is "stateless LLM + finite context," Lesson 3 gave the "stable prefix + changing tail" structure, Lesson 4 showed that every step re-assembles and re-sends the whole context. <strong>This lesson supplies the missing "why"</strong>: because context is a <strong>finite, per-token-billed budget</strong>, prefill / prefix-cache economics make a "stable prefix" a hard money-saving rule, and "the tail only grows" makes "swapping out old content" something you'll do sooner or later. Letta doesn't dodge it — it quantifies it as <span class="mono">ContextWindowOverview</span> and triggers action at <span class="mono">context_window × 0.9</span>.</p>

<div class="note info"><span class="ni">👉</span><span class="nx">Follow that logic and the next stop comes naturally: <strong>since the budget is finite and the tail must be swapped out, "where does the swapped-out stuff go, how is it fetched back, how does the agent manage it itself" — that's the question the "memory system" answers, and it's exactly Part 3's subject.</strong></span></div>

<p>The three tiers — core memory (the always-in-window persona / human), recall (searchable past messages), archival (searchable long-term facts) — are essentially the engineering of "desk + drawer + archive room," a <strong>direct answer</strong> to this lesson's constraint. After Part 3, you'll see how the summaries squeezed out by <span class="mono">compact</span>, the messages pushed into archive, and the agent's self-editing loop via memory tools together turn a "finite window" into "seemingly unlimited memory."</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>Core constraint = a finite token budget</strong>: the tokens visible in one call have a hard-coded ceiling, and system + core memory + tool schemas + in-context messages all <strong>share</strong> that budget.</li>
    <li><strong>prefill vs decode</strong>: prefill reads the whole prompt in parallel (longer = pricier), decode generates token by token serially (longer = slower); prefill builds the KV cache.</li>
    <li><strong>Stable prefix saves money (prefix cache)</strong>: a token-for-token identical prefix hits the cache and skips prefill — exactly the economic reason behind Lesson 3's "stable prefix + changing tail."</li>
    <li><strong>Letta quantifies it</strong>: <span class="mono">ContextWindowOverview</span> breaks the window into an itemized token ledger (computed live by <span class="mono">ContextWindowCalculator</span> + <span class="mono">TokenCounter</span>).</li>
    <li><strong>Letta acts on it</strong>: nearing <span class="mono">context_window × 0.9</span> (<span class="mono">get_compaction_trigger_threshold</span>) it <span class="mono">compact</span>s old messages.</li>
    <li><strong>More context ≠ better</strong>: a triple cost of price, latency, and lost-in-the-middle; long context loosens but doesn't remove the constraint — memory management is still a necessity, the subject of Part 3.</li>
  </ul>
</div>
""",
}

LESSON_06 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前面几课我们一直在用两个词——"有状态"和"无状态"——却从没把它们拆到机制层面。第 1 课说"LLM 是无状态的，所以 Letta 替它把状态存进数据库"；第 3 课说"每处理一条消息，都要从存档里把上下文现拼一份再发给模型"。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课就把那句"存档"本身翻开看个究竟——它<strong>比第 1、3 课更深一层</strong>，专攻五件具体的事：Letta 到底怎么把一个 agent <strong>序列化</strong>成一条 <span class="mono">AgentState</span>；身份为什么放在一个<strong>带前缀的 id</strong>（<span class="mono">agent-…</span>、<span class="mono">block-…</span>）里、而不是某个活对象里；为什么同一份数据要分 <strong>schema（pydantic API 契约）</strong>和 <strong>orm（SQLAlchemy 数据库行）</strong>两套模型；存档怎么在"数据库行 ↔ pydantic ↔ 活的运行时"之间<strong>往返</strong>；以及把这套设计和 <strong>OpenAI Assistants</strong> 正面对比，差距到底落在哪。读完你会真正握住那句口号——<strong>agent 是数据，不是进程</strong>。
</p>

<div class="card analogy">
  <div class="tag">🔌 生活类比</div>
  把一个 Letta agent 想象成一张<strong>游戏存档</strong>，外加一张<strong>角色卡</strong>。角色卡上写满了"这个角色是谁"：记忆（persona / human）、走到剧情哪一步（在窗消息）、学会了哪些技能（工具）、配的是哪套引擎（模型）。这里有三条关键事实：① <strong>角色不是"那台一直开着的主机"</strong>——主机关了角色不会消失，因为它整个被写进了存档文件；② <strong>换台机器读同一份档，还是同一个角色</strong>——身份写在<strong>存档编号</strong>里，而不在某个正在运行的进程里；③ <strong>存档是普通数据</strong>——你能复制它、给它打版本号、塞回云端、甚至把底层引擎换成另一款（换显卡照样读档）。Letta 干的就是这件事：它不让 agent 当一个"必须常驻的进程"，而是把它做成一份<strong>随时能存、能读、能搬、能改的存档</strong>。这一课，我们就拆开这张角色卡，看清楚里面到底存了什么、身份编号怎么来、读档时又怎么把角色"现搭"回来。
</div>

<div class="card macro">
  <div class="tag">🌍 宏观理解</div>
  一句话抓住本课：<strong>在 Letta 里，一个 agent 不是"正在运行的进程"，而是数据库里一条带稳定身份、可序列化的记录（<span class="mono">AgentState</span>）。</strong>所谓"有状态"，指的是<strong>这份数据被持久化、有归属、可往返</strong>；而"无状态"指的是<strong>跑它的那段运行时是临时的、用完即弃</strong>——每来一个请求，Letta 都按这份数据<strong>现搭</strong>一个运行时、跑完就丢。把两者分清楚，本课所有结论都顺理成章：状态在数据里（持久、可移植），算力在运行时里（短命、可重建）。这正是 Letta 能"像文件一样对待 agent"的根基。
</div>

<h2>比第 1、3 课更深：这次翻开"存档"本身</h2>
<p>第 1 课给了结论——"agent 是库里一条记录"；第 3 课给了节奏——"每步现拼上下文再发给无状态的模型"。但两课都把"存档"当成黑盒一笔带过。这一课<strong>明确在它们的基础上加深</strong>，只钻一个问题：<strong>这份存档具体长什么样、怎么生成身份、怎么读回来变成能跑的东西</strong>。</p>

<p>我们会依次回答五个递进的问题：①一个 agent <strong>物理上</strong>是什么？②它的<strong>身份</strong>凭什么稳定？③它怎么在数据库与运行时之间<strong>往返</strong>？④同一份数据为什么要存<strong>两套模型</strong>？⑤这套"agent 即数据"的设计，比 <strong>OpenAI Assistants</strong> 那种"托管在云端"的做法强在哪？把这五问串起来，你就拿到了读懂第三部分（记忆系统）的钥匙。</p>

<div class="cute"><div class="row"><span class="emoji">💾</span><span class="lab">AgentState（数据）</span><span class="arrow">→</span><span class="emoji">⚙️</span><span class="lab">运行时（现搭即弃）</span></div><div class="cap">agent 是数据，不是进程：数据持久、可复制、可迁移；运行时每次现搭、用完即弃</div></div>

<h2>一个 agent 物理上是什么：库里一条 AgentState</h2>
<p>去神秘化第一步：当你"创建一个 agent"，Letta 并不会启动一个常驻服务，而是<strong>往数据库里写一行</strong>。这一行被读出来时，就是一个 <span class="mono">AgentState</span>（定义在 <span class="mono">letta/schemas/agent.py</span>）——它装着重建这个 agent 所需的<strong>全部状态</strong>：核心记忆、在窗消息的 id 列表、system 提示、工具与工具规则、以及模型与嵌入配置。换句话说，<strong>agent 的"全部"就摊在这几个字段里</strong>：</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">记忆</span><span class="name">memory（blocks）</span></div>
    <div class="ld">persona / human 等核心记忆块，序列化时一并存下，读档即恢复——agent 自己也能改它。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">历史指针</span><span class="name">message_ids · system</span></div>
    <div class="ld">在窗消息的 id 列表（第 0 条永远是 system 消息）+ system 提示模板，运行时按它现拼上下文。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">能力 / 规则</span><span class="name">tools · tool_rules</span></div>
    <div class="ld">这个 agent 能调用哪些工具、以及调用顺序的约束（tool_rules）。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">模型配置</span><span class="name">llm_config · embedding_config</span></div>
    <div class="ld">用哪个模型、上下文多大、用哪个嵌入模型做向量检索——换模型，只是改这里一行。</div></div>
</div>

<p>盯着这张图想一件事：<strong>这里没有任何"活的对象"</strong>。没有打开的网络连接、没有常驻线程、没有内存里的会话。全是<strong>能写进数据库、能读回来的纯数据</strong>。这正是"有状态"的确切含义——状态被完整地<strong>外化</strong>成了一份记录。第 3 课说"每步要把上下文重拼"，原因到这里就闭环了：因为模型无状态、运行时也无状态，<strong>唯一长期可靠的真相只有这份 <span class="mono">AgentState</span></strong>，每次都得拿它当唯一信源重新组装。</p>

<h2>身份在 id 里：prefixed id 方案</h2>
<p>既然 agent 是数据，那"这是哪一个 agent"就不能靠"哪个进程在跑"来回答，只能靠一个<strong>稳定的标识符</strong>。Letta 的所有核心实体都用同一种身份方案——<strong>带类型前缀的 id</strong>：前缀就是这个实体的类型，后面跟一个 <span class="mono">uuid4</span>。于是光看 id 的开头，你就知道它是什么：</p>

<table class="t">
  <tr><th>实体</th><th>id 形如</th><th>__id_prefix__</th><th>前缀编码了什么</th></tr>
  <tr><td>Agent</td><td class="mono">agent-1a2b…</td><td class="mono">agent</td><td>一眼是个 agent；按此 id 取出整份存档</td></tr>
  <tr><td>Block（记忆块）</td><td class="mono">block-9f8e…</td><td class="mono">block</td><td>可被多个 agent 共享引用的记忆单元</td></tr>
  <tr><td>Message</td><td class="mono">message-7c6d…</td><td class="mono">message</td><td>recall / 历史里按 id 精确定位一条消息</td></tr>
  <tr><td>Tool</td><td class="mono">tool-3e4f…</td><td class="mono">tool</td><td>一个可被多个 agent 装配的工具</td></tr>
  <tr><td>User / Org</td><td class="mono">user-… / org-…</td><td class="mono">user / org</td><td>多租户作用域：谁拥有、谁可见</td></tr>
</table>

<p>这套 id 怎么来的？答案简单得令人安心：每个 schema 声明一个 <span class="mono">__id_prefix__</span>，<span class="mono">generate_id</span> 就把"前缀 + 一个 uuid4"拼起来。比如 <span class="mono">AgentState</span> 的前缀解析为 <span class="mono">agent</span>，于是它的 id 永远长成 <span class="mono">agent-&lt;uuid&gt;</span>：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/letta_base.py</span><span class="ln">LettaBase.generate_id / __id_prefix__（简化）</span></div>
<pre><span class="cm"># 每个 schema 声明自己的前缀；id = 前缀 + 一个 uuid4</span>
<span class="kw">class</span> <span class="fn">LettaBase</span>(BaseModel):
    __id_prefix__: str                      <span class="cm"># 子类各自指定，如 "agent" / "block"</span>

    <span class="nb">@classmethod</span>
    <span class="kw">def</span> <span class="fn">generate_id</span>(cls, prefix=<span class="kw">None</span>):
        prefix = prefix <span class="kw">or</span> cls.__id_prefix__
        <span class="kw">return</span> <span class="st">f"{prefix}-{uuid.uuid4()}"</span>   <span class="cm"># 例: agent-1a2b… / block-9f8e…</span>
</pre></div>

<p>别小看这一点点字符串约定，它带来三个实打实的好处。<strong>其一，类型自证</strong>：拿到 <span class="mono">block-9f8e…</span> 你立刻知道这是个记忆块，不会误当成 agent——前缀就是廉价的类型标签。<strong>其二，好调试</strong>：日志里满屏 id，前缀让你一眼分辨实体种类，定位问题快得多。<strong>其三，不撞车且可移植</strong>：uuid4 几乎不可能重复，且 id 不依赖任何自增主键或机器，<strong>导出到别处仍然有效</strong>——这正是"agent 可搬运"的前提。身份在 id 里，不在某个活对象里。</p>

<h2>存档怎么往返：DB 行 ↔ pydantic ↔ 活的运行时</h2>
<p>有了"数据"和"身份"，还差最后一环：这份存档怎么变成"能跑一步"的东西，跑完又怎么写回去。这是一条<strong>往返路径</strong>——数据库行被读成 pydantic 的 <span class="mono">AgentState</span>，运行时拿它现搭一个 agent 跑一步，产生的新状态再写回数据库行：</p>

<div class="flow">
  <div class="node"><div class="nt">DB 行</div><div class="nd">orm 模型（一行）</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">load</div><div class="nd">to_pydantic_async</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">AgentState</div><div class="nd">pydantic · 可移植数据</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">现搭运行时</div><div class="nd">AgentLoop.load 跑一步</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">save</div><div class="nd">写回 DB 行</div></div>
</div>

<p>最值得玩味的是"现搭运行时"那一格。运行时<strong>不是常驻进程</strong>——每来一个请求，<span class="mono">AgentLoop.load</span> 就读这份 <span class="mono">AgentState</span>，按里面的 <span class="mono">agent_type</span>、模型、工具、记忆，<strong>当场构造</strong>一个运行时对象（如 <span class="mono">LettaAgentV3</span>），跑完这一步就丢掉。换句话说，<strong>运行时是数据的一个"短命投影"</strong>，真相永远在那行数据里：</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/agent_loop.py</span><span class="ln">AgentLoop.load（简化）</span></div>
<pre><span class="cm"># 运行时不是常驻进程：每次都用 AgentState 这份数据"现搭"一个出来</span>
<span class="kw">class</span> <span class="fn">AgentLoop</span>:
    <span class="nb">@staticmethod</span>
    <span class="kw">def</span> <span class="fn">load</span>(agent_state: AgentState, actor):
        <span class="cm"># 按存档里的 agent_type 选一个运行时实现，把状态喂进去</span>
        <span class="kw">if</span> agent_state.agent_type <span class="kw">in</span> (letta_v1_agent, sleeptime_agent):
            <span class="kw">return</span> <span class="fn">LettaAgentV3</span>(agent_state=agent_state, actor=actor)
        <span class="kw">return</span> <span class="fn">LettaAgentV2</span>(agent_state=agent_state, actor=actor)
</pre></div>

<div class="card warn">
  <div class="tag">⚠️ 常见误区</div>
  <strong>"有状态的数据"不等于"有状态的运行时"——别把这两件事混成一件。</strong>说 Letta agent"有状态"，指的是它的状态被<strong>持久化成一份数据</strong>（<span class="mono">AgentState</span>）；这恰恰是<strong>为了配合一个无状态的运行时</strong>而存在的（精确重申第 3 课）。模型本身无状态——它不记得上一轮；运行时也无状态——它每个请求现搭现拆、不常驻内存。<strong>真正"记得住"的，只有那份被存下来的数据。</strong>所以正确的心智模型是：<em>状态在数据里（持久、有归属、可移植），算力在运行时里（短命、可重建）</em>。如果你以为"有状态"意味着"有个一直开着的 agent 进程在内存里记着东西"，就会彻底误解 Letta：它偏偏不这么干，正是因为不这么干，才换来了可复制、可版本化、可搬运的好处。
</div>

<h2>一份数据，两套模型：schema（pydantic）vs orm（SQLAlchemy）</h2>
<p>这里有个初学者常被绊住的点：同一个"Block"或"Agent"，代码里居然有<strong>两套</strong>类定义。一套在 <span class="mono">letta/schemas/</span>（pydantic），一套在 <span class="mono">letta/orm/</span>（SQLAlchemy）。这不是冗余，而是<strong>故意的分层</strong>——它们各管一件事：</p>

<div class="cols">
  <div class="col">
    <h4>schema：pydantic（API 契约）</h4>
    <p>住在 <span class="mono">letta/schemas/</span>。它定义<strong>对外承诺的形状</strong>：请求/响应长什么样、字段类型、校验规则。它是<strong>稳定的 API 契约</strong>，前端、SDK、文档都依赖它，不能随数据库实现乱动。</p>
  </div>
  <div class="col">
    <h4>orm：SQLAlchemy（数据库行）</h4>
    <p>住在 <span class="mono">letta/orm/</span>。它定义<strong>数据怎么落到表里</strong>：列、索引、外键、关系。它服务于存储与查询，可以为了性能调整，而<strong>不惊动对外契约</strong>。</p>
  </div>
</div>

<p>两套之间靠 <strong>manager 层转换</strong>：从数据库读出 orm 行，调 <span class="mono">to_pydantic_async</span> 之类的方法变成 pydantic schema 发给客户端；写入时反向。有意思的是，有些 pydantic 配置（如 <span class="mono">llm_config</span>）本身就是结构化对象，Letta 干脆把它们<strong>以 JSON 形式整块存进一列</strong>——这套"pydantic 存进 DB"的胶水在 <span class="mono">letta/orm/custom_columns.py</span> 里。于是同一份配置，<strong>对外是带类型的 pydantic、对内是一段 JSON 列</strong>，两边都舒服。</p>

<p>顺带厘清一个最容易记错的命名：每种资源其实有<strong>三个动词</strong>对应三个不同形状的对象——"建"用什么、"改"用什么、"读"到什么，别混为一谈：</p>

<div class="cellgroup">
  <div class="cg-cap"><b>每种资源的"三个动词"</b>：建、改、读是三个不同形状的对象（注意是 <span class="mono">BlockUpdate</span> 不是 UpdateBlock）</div>
  <div class="cells">
    <span class="cell hl">建 · Create*<br>CreateBlock / CreateAgent</span>
    <span class="cell">改 · *Update<br>BlockUpdate / UpdateAgent</span>
    <span class="cell scale">读 · 完整对象<br>Block / AgentState</span>
  </div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/block.py</span><span class="ln">create / update / read 三件套（简化）</span></div>
<pre><span class="cm"># 建：客户端要新建一个记忆块时给的字段（没有 id，服务端生成）</span>
<span class="kw">class</span> <span class="fn">CreateBlock</span>(BaseBlock):
    label: str                       <span class="cm"># 如 "human" / "persona"</span>
    value: str                       <span class="cm"># 记忆内容</span>

<span class="cm"># 改：只带要修改的字段，其余可省（名字是 BlockUpdate，不是 UpdateBlock）</span>
<span class="kw">class</span> <span class="fn">BlockUpdate</span>(BaseBlock):
    value: Optional[str] = <span class="kw">None</span>
    limit: Optional[int] = <span class="kw">None</span>

<span class="cm"># 读：服务端发回的完整对象，带稳定的 prefixed id 与时间戳</span>
<span class="kw">class</span> <span class="fn">Block</span>(BaseBlock):
    id: str = <span class="fn">Field</span>(..., description=<span class="st">"block-…"</span>)
    value: str
    <span class="cm"># 还有 label / limit 等；时间戳、organization_id 等元数据在 orm 行上</span>
</pre></div>

<p>同样的三件套也适用于 agent：<strong>建</strong>用 <span class="mono">CreateAgent</span>、<strong>改</strong>用 <span class="mono">UpdateAgent</span>、<strong>读</strong>到的是那份完整的 <span class="mono">AgentState</span>（都在 <span class="mono">letta/schemas/agent.py</span>）。记住这个模式，你读 Letta 的任何资源接口都会轻松很多：<em>请求体是 Create/Update，响应体是那个完整 schema</em>。</p>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <strong>因为整个 agent 就是数据（一份带稳定 prefixed id 的序列化 <span class="mono">AgentState</span>），Letta 拿到了"进程常驻型 agent"永远拿不到的一组性质。</strong>你可以像对待一个文件那样对待一个 agent：<strong>复制</strong>它（拷一份数据就是一个孪生 agent）、<strong>共享</strong>它（把 block 的 id 给另一个 agent 就共用同一块记忆）、<strong>版本化</strong>它（对状态做 diff、回滚、入库）、<strong>检视</strong>它（直接读字段，而不是猜一个黑盒进程在想什么）。你还能<strong>换掉底层模型</strong>——改一行 <span class="mono">llm_config</span>，同一个 agent 就从一款模型平滑迁到另一款，记忆与身份分毫不动；你更能<strong>到处运行</strong>它——读档即恢复，换台机器还是同一个 agent。这一切的根都在一句话上：<strong>身份在 id 里，不在某个活对象里。</strong>把 agent 从"必须一直开着的进程"降格为"随时能存读搬改的数据"，看似只是工程选择，实则解锁了 OpenAI Assistants 那种托管方案给不了的全部自由。
</div>

<h2>和 OpenAI Assistants 正面对比</h2>
<p>把上面这些性质放到一张对比表里，和"把 agent 托管在云端"的 OpenAI Assistants 摆在一起，差距就一目了然。核心分歧只有一句：<strong>状态归谁、能否当数据自由处置</strong>。</p>

<table class="t">
  <tr><th>维度</th><th>Letta（agent 即有状态数据）</th><th>OpenAI Assistants（托管在云端）</th></tr>
  <tr><td>状态归谁</td><td>你库里一条 <span class="mono">AgentState</span>，你拥有、你能读</td><td>在服务端，你只拿到一个 id 引用</td></tr>
  <tr><td>能否导出 / 版本化</td><td>能：它就是数据，可复制 / diff / 入库 / 回滚</td><td>难：拿不到底层状态整份导出</td></tr>
  <tr><td>是否模型无关</td><td>是：改 <span class="mono">llm_config</span> 即换模型，身份不变</td><td>基本绑定其自家模型</td></tr>
  <tr><td>记忆可否编辑</td><td>能：核心记忆是可改的 <span class="mono">block</span>，agent 自己也能改</td><td>受限：记忆机制不透明、难自由编辑</td></tr>
  <tr><td>能否到处运行</td><td>能：读档即恢复，换机器仍是同一个 agent</td><td>必须经其托管 API</td></tr>
</table>

<p>不是说托管方案一无是处——它省心、免运维。但只要你的诉求里出现"我要拥有、要导出、要换模型、要编辑记忆、要在自己的环境里跑"，<strong>"agent 是数据"这条路线就有结构性优势</strong>：数据可以被你完全掌控，进程不行。这也呼应了第 1 课那句"Letta 让 agent 像数据库记录一样持久而可移植"——到这一课，你终于看清了它<strong>具体凭什么</strong>做到。</p>

<h2>再挖深一点</h2>

<details class="accordion"><summary>schema 与 orm 为什么要分两套？</summary><div class="acc-body">
<p><strong>示例：</strong>你想给 Block 表加一个索引、或把某列拆成两列以提速。如果对外接口和数据库表是同一套类，这种内部优化就会<strong>改变 API 形状</strong>，所有客户端都得跟着改。</p>
<p><strong>为什么这样设计：</strong>pydantic schema 是<strong>对外契约</strong>（要稳定），SQLAlchemy orm 是<strong>存储细节</strong>（要能为性能演进）。两者解耦，DB 怎么调都不惊动 API；API 想加校验也不必动表结构。manager 层负责在两者间转换（如 <span class="mono">to_pydantic_async</span>）。</p>
<p><strong>源码在哪：</strong>schema 在 <span class="mono">letta/schemas/</span>（如 <span class="mono">block.py</span> / <span class="mono">agent.py</span>），orm 在 <span class="mono">letta/orm/</span>；把 pydantic 配置整块以 JSON 存进一列的胶水在 <span class="mono">letta/orm/custom_columns.py</span>。</p>
<p><strong>还有什么替代：</strong>只用一套（ORM 直接当 API 模型）——小项目省事，但 API 与表强耦合，任何 DB 重构都漏到接口上；大型、长期演进的系统几乎都会像 Letta 这样分层。</p>
</div></details>

<details class="accordion"><summary>prefixed id 到底有什么好处？</summary><div class="acc-body">
<p><strong>示例：</strong>日志里出现 <span class="mono">block-9f8e…</span> 和 <span class="mono">agent-1a2b…</span>。不用查表，你一眼就知道前者是记忆块、后者是 agent，排错速度立刻不同。</p>
<p><strong>为什么这样设计：</strong>前缀=类型，等于把"这是什么"<strong>编码进 id 本身</strong>：① 类型自证、防止把一种 id 误用成另一种；② 调试可读；③ uuid4 部分保证不撞车，且 id 不依赖自增主键或机器，<strong>导出别处仍有效</strong>，是"可移植"的前提。</p>
<p><strong>源码在哪：</strong><span class="mono">letta/schemas/letta_base.py::LettaBase.generate_id</span>（= <span class="mono">f"{prefix}-{uuid4()}"</span>），前缀由各 schema 的 <span class="mono">__id_prefix__</span> 指定（如 <span class="mono">AgentState</span> 解析为 <span class="mono">agent</span>）。</p>
<p><strong>还有什么替代：</strong>纯自增整数主键——紧凑但<strong>泄露规模、跨库会撞、看不出类型</strong>；裸 uuid（无前缀）——不撞车但丢了类型可读性。带前缀的 uuid 同时拿到"不撞 + 自证类型"。</p>
</div></details>

<details class="accordion"><summary>和 OpenAI Assistants 到底差在哪？</summary><div class="acc-body">
<p><strong>示例：</strong>你想把一个调好的 agent <strong>复制三份</strong>、各换一个模型做 A/B，再把表现最好的那份<strong>存进 git 版本库</strong>。在 Letta 里，这就是"复制数据 + 改 <span class="mono">llm_config</span> + 入库"；在纯托管方案里，你拿不到底层状态，做不了这套。</p>
<p><strong>为什么这样设计：</strong>归属与形态不同——Letta 把状态放在<strong>你的数据库</strong>里、做成<strong>可读可改的数据</strong>，于是导出、版本化、换模型、编辑记忆、异地运行都成立；托管方案把状态留在服务端，你只持有一个引用。</p>
<p><strong>源码在哪：</strong>状态实体 <span class="mono">letta/schemas/agent.py::AgentState</span>；模型配置 <span class="mono">llm_config</span> 即其一个字段，换模型就是改它；可编辑记忆是 <span class="mono">letta/schemas/block.py::Block</span>（配 <span class="mono">BlockUpdate</span>）。</p>
<p><strong>还有什么替代：</strong>托管 Assistants——省运维、但牺牲掌控与可移植；自建但仍把 agent 当常驻进程——一旦进程没了状态也没了，且难复制/版本化。Letta 选"agent 即数据"，正是为换取这些自由。</p>
</div></details>

<h2>第二部分到此结束：下一站是记忆系统</h2>
<p>第二部分（前置基础）三课走到这里收尾。回头看这条线：第 4 课讲清了"agent = LLM + 工具 + 循环"以及 tool calling 在消息层怎么工作；第 5 课讲清了"上下文是一笔有限且按 token 计费的预算"，记忆管理是被经济规律逼出来的刚需；这一课则把"状态"本身翻开——<strong>agent 是一条可序列化、有稳定 prefixed 身份、靠 schema/orm 两套模型落库、在数据与短命运行时之间往返的数据</strong>。三课合起来，你已经握牢了三把钥匙：<strong>工具（agent 怎么动手）、上下文（为什么必须管理记忆）、状态（agent 物理上是什么）</strong>。</p>
<p>这三把钥匙，恰好同时指向同一扇门——<strong>记忆系统</strong>，也就是第三部分的主题。第 5 课留下的问题是"换出去的东西放哪、怎么取回、agent 怎么自己管"；这一课则告诉你"那些被管理的记忆，本身就是带 id 的、可编辑的数据（<span class="mono">block</span> 等）"。把两者接上，第三部分就要正式展开 Letta 的分层记忆：始终在窗的<strong>核心记忆</strong>、可检索的<strong>recall</strong>历史、可检索的<strong>archival</strong>长期事实，以及 agent 用记忆工具<strong>自我编辑</strong>的闭环。带着"agent 是数据"这个心智模型往下读，你会发现记忆系统的每一处设计，都是本课这条原则的自然延伸。</p>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>agent 物理上是数据</strong>：一个 agent = 数据库里一条可序列化的 <span class="mono">AgentState</span>（记忆 / message_ids / system / tools / tool_rules / llm_config / embedding_config），没有"活对象"。</li>
    <li><strong>身份在 prefixed id 里</strong>：<span class="mono">generate_id</span> = <span class="mono">f"{__id_prefix__}-{uuid4()}"</span>，前缀即类型（<span class="mono">agent-…</span> / <span class="mono">block-…</span>），带来类型自证、好调试、不撞车且可移植。</li>
    <li><strong>schema vs orm 两套模型</strong>：pydantic（<span class="mono">letta/schemas/</span>）是稳定 API 契约，SQLAlchemy（<span class="mono">letta/orm/</span>）是可演进的存储；manager 转换，配置以 JSON 存列（<span class="mono">custom_columns.py</span>）。</li>
    <li><strong>create/update/read 三件套</strong>：建用 <span class="mono">CreateBlock</span>/<span class="mono">CreateAgent</span>，改用 <span class="mono">BlockUpdate</span>/<span class="mono">UpdateAgent</span>，读到 <span class="mono">Block</span>/<span class="mono">AgentState</span>（注意是 BlockUpdate，不是 UpdateBlock）。</li>
    <li><strong>往返而非常驻</strong>：DB 行 → <span class="mono">AgentState</span> → <span class="mono">AgentLoop.load</span> 现搭运行时跑一步 → 写回；运行时是数据的短命投影。</li>
    <li><strong>"有状态数据" ≠ "有状态运行时"</strong>：状态在数据里（持久、有归属、可移植），算力在运行时里（短命、可重建）——精确重申第 3 课。</li>
    <li><strong>对比 OpenAI Assistants</strong>：因为 agent 是数据，才能复制 / 共享 / 版本化 / 检视 / 换模型 / 异地运行——身份在 id 里，不在活对象里。</li>
  </ul>
</div>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
We've leaned on two words for several lessons — "stateful" and "stateless" — without ever cracking them open at the mechanism level. Lesson 1 said "the LLM is stateless, so Letta saves its state in the database"; Lesson 3 said "to handle each message, re-assemble the context from the save and send it to the model."</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson opens that "save" itself and looks inside — going <strong>one layer deeper than Lessons 1 and 3</strong>, focused on five concrete things: how Letta <strong>serializes</strong> an agent into one <span class="mono">AgentState</span>; why identity lives in a <strong>prefixed id</strong> (<span class="mono">agent-…</span>, <span class="mono">block-…</span>) rather than in some live object; why one piece of data is modeled <strong>twice</strong> — as a <strong>schema (pydantic API contract)</strong> and an <strong>orm (SQLAlchemy DB row)</strong>; how the save <strong>round-trips</strong> between "DB row ↔ pydantic ↔ live runtime"; and how this design compares head-to-head with <strong>OpenAI Assistants</strong>. By the end you'll truly grasp the slogan — <strong>an agent is data, not a process</strong>.
</p>

<div class="card analogy">
  <div class="tag">🔌 Analogy</div>
  Picture a Letta agent as a <strong>game save file</strong> plus a <strong>character sheet</strong>. The sheet spells out "who this character is": memory (persona / human), how far the story has progressed (in-context messages), which skills were learned (tools), and which engine it's tuned for (the model). Three facts matter: ① <strong>the character is not "the console that happens to be on"</strong> — turn the console off and the character survives, because it's been written entirely into the save file; ② <strong>load the same save on another machine and it's the same character</strong> — identity lives in the <strong>save's id</strong>, not in some running process; ③ <strong>a save is ordinary data</strong> — you can copy it, version it, push it to the cloud, even swap the underlying engine (load the save on a new GPU just fine). That's exactly what Letta does: it refuses to make an agent a "must-stay-running process" and instead makes it a <strong>save you can store, load, move, and edit at will</strong>. This lesson opens that character sheet — what's stored inside, where the id comes from, and how loading "rebuilds" the character on the fly.
</div>

<div class="card macro">
  <div class="tag">🌍 Big picture</div>
  Grab this lesson in one line: <strong>in Letta an agent is not a "running process" but a database record with a stable identity and a serializable shape (<span class="mono">AgentState</span>).</strong> "Stateful" means <strong>this data is persisted, owned, and round-trippable</strong>; "stateless" means <strong>the runtime that executes it is temporary, used and discarded</strong> — for every request Letta <strong>rebuilds</strong> a runtime from that data and throws it away when the step is done. Keep the two apart and every conclusion here follows: state lives in the data (durable, portable), compute lives in the runtime (short-lived, rebuildable). That's the foundation that lets Letta "treat an agent like a file."
</div>

<h2>Deeper than Lessons 1 and 3: opening the "save" itself</h2>
<p>Lesson 1 gave the conclusion — "an agent is a record in the DB"; Lesson 3 gave the rhythm — "re-assemble context each step and send it to a stateless model." But both treated the "save" as a black box. This lesson <strong>explicitly builds on them</strong> and drills one question: <strong>what does that save actually look like, how is its identity generated, and how is it loaded back into something runnable</strong>.</p>

<p>We'll answer five escalating questions: ① what is an agent <strong>physically</strong>? ② what makes its <strong>identity</strong> stable? ③ how does it <strong>round-trip</strong> between database and runtime? ④ why store the same data as <strong>two models</strong>? ⑤ how does this "agent-as-data" design beat the "hosted in the cloud" approach of <strong>OpenAI Assistants</strong>? String these together and you hold the key to Part 3 (the memory system).</p>

<div class="cute"><div class="row"><span class="emoji">💾</span><span class="lab">AgentState (data)</span><span class="arrow">→</span><span class="emoji">⚙️</span><span class="lab">runtime (rebuilt, discarded)</span></div><div class="cap">an agent is data, not a process: the data persists, copies, and travels; the runtime is rebuilt per request and thrown away</div></div>

<h2>What an agent physically is: one AgentState in the DB</h2>
<p>Demystification step one: when you "create an agent," Letta does not spin up a resident service — it <strong>writes a row to the database</strong>. Read that row back and you get an <span class="mono">AgentState</span> (defined in <span class="mono">letta/schemas/agent.py</span>) — it holds <strong>all the state</strong> needed to rebuild this agent: core memory, the list of in-context message ids, the system prompt, tools and tool rules, and the model and embedding configs. In other words, the agent's "everything" is laid out across these few fields:</p>

<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">memory</span><span class="name">memory (blocks)</span></div>
    <div class="ld">core blocks like persona / human, serialized along with the rest, restored on load — the agent itself can edit them.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">history pointer</span><span class="name">message_ids · system</span></div>
    <div class="ld">the list of in-context message ids (index 0 is always the system message) plus the system prompt; the runtime re-assembles context from it.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">abilities / rules</span><span class="name">tools · tool_rules</span></div>
    <div class="ld">which tools this agent may call, and the ordering constraints on those calls (tool_rules).</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">model config</span><span class="name">llm_config · embedding_config</span></div>
    <div class="ld">which model, how big the window, which embedding model for vector search — swapping models is just editing one line here.</div></div>
</div>

<p>Stare at this and notice one thing: <strong>there is no "live object" here</strong>. No open network connection, no resident thread, no in-memory session. It's all <strong>pure data that can be written to and read from the database</strong>. That's the precise meaning of "stateful" — the state is fully <strong>externalized</strong> into a record. Lesson 3's "re-assemble context every step" closes the loop here: because the model is stateless and the runtime is stateless too, <strong>the only durable source of truth is this <span class="mono">AgentState</span></strong>, and every step must rebuild from it as the single source.</p>

<h2>Identity lives in the id: the prefixed-id scheme</h2>
<p>If an agent is data, then "which agent is this" can't be answered by "which process is running" — only by a <strong>stable identifier</strong>. Every core entity in Letta uses the same identity scheme: a <strong>type-prefixed id</strong> — the prefix is the entity's type, followed by a <span class="mono">uuid4</span>. So just by the start of an id you know what it is:</p>

<table class="t">
  <tr><th>Entity</th><th>id looks like</th><th>__id_prefix__</th><th>what the prefix encodes</th></tr>
  <tr><td>Agent</td><td class="mono">agent-1a2b…</td><td class="mono">agent</td><td>obviously an agent; fetch the whole save by this id</td></tr>
  <tr><td>Block (memory block)</td><td class="mono">block-9f8e…</td><td class="mono">block</td><td>a memory unit shareable across many agents</td></tr>
  <tr><td>Message</td><td class="mono">message-7c6d…</td><td class="mono">message</td><td>pinpoint one message by id in recall / history</td></tr>
  <tr><td>Tool</td><td class="mono">tool-3e4f…</td><td class="mono">tool</td><td>a tool that many agents can be equipped with</td></tr>
  <tr><td>User / Org</td><td class="mono">user-… / org-…</td><td class="mono">user / org</td><td>multi-tenant scope: who owns it, who can see it</td></tr>
</table>

<p>Where do these ids come from? Reassuringly simple: each schema declares an <span class="mono">__id_prefix__</span>, and <span class="mono">generate_id</span> stitches together "prefix + a uuid4." For example <span class="mono">AgentState</span>'s prefix resolves to <span class="mono">agent</span>, so its id always looks like <span class="mono">agent-&lt;uuid&gt;</span>:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/letta_base.py</span><span class="ln">LettaBase.generate_id / __id_prefix__ (simplified)</span></div>
<pre><span class="cm"># each schema declares its prefix; id = prefix + a uuid4</span>
<span class="kw">class</span> <span class="fn">LettaBase</span>(BaseModel):
    __id_prefix__: str                      <span class="cm"># set by each subclass, e.g. "agent" / "block"</span>

    <span class="nb">@classmethod</span>
    <span class="kw">def</span> <span class="fn">generate_id</span>(cls, prefix=<span class="kw">None</span>):
        prefix = prefix <span class="kw">or</span> cls.__id_prefix__
        <span class="kw">return</span> <span class="st">f"{prefix}-{uuid.uuid4()}"</span>   <span class="cm"># e.g. agent-1a2b… / block-9f8e…</span>
</pre></div>

<p>Don't underestimate this tiny string convention — it buys three real benefits. <strong>One, self-describing types</strong>: see <span class="mono">block-9f8e…</span> and you instantly know it's a memory block, never mistaking it for an agent — the prefix is a cheap type tag. <strong>Two, easy debugging</strong>: logs full of ids become readable at a glance, so you locate problems faster. <strong>Three, no collisions and portable</strong>: uuid4 is practically never duplicated, and the id depends on no auto-increment key or machine, so <strong>it stays valid when exported elsewhere</strong> — the very premise of "agents are movable." Identity lives in the id, not in a live object.</p>

<h2>How the save round-trips: DB row ↔ pydantic ↔ live runtime</h2>
<p>With "data" and "identity" in hand, one link remains: how this save becomes something that "runs a step," and how the result gets written back. It's a <strong>round-trip</strong> — the DB row is read into a pydantic <span class="mono">AgentState</span>, the runtime rebuilds an agent from it and runs a step, and the new state is written back to the DB row:</p>

<div class="flow">
  <div class="node"><div class="nt">DB row</div><div class="nd">orm model (one row)</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node hl"><div class="nt">load</div><div class="nd">to_pydantic_async</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">AgentState</div><div class="nd">pydantic · portable data</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">rebuild runtime</div><div class="nd">AgentLoop.load runs a step</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">save</div><div class="nd">write back to DB row</div></div>
</div>

<p>The most telling box is "rebuild runtime." The runtime is <strong>not a resident process</strong> — for each request, <span class="mono">AgentLoop.load</span> reads this <span class="mono">AgentState</span> and, based on its <span class="mono">agent_type</span>, model, tools, and memory, <strong>constructs a runtime object on the spot</strong> (e.g. <span class="mono">LettaAgentV3</span>), runs the step, and discards it. In other words, <strong>the runtime is a short-lived projection of the data</strong>; the truth always lives in that row:</p>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/agents/agent_loop.py</span><span class="ln">AgentLoop.load (simplified)</span></div>
<pre><span class="cm"># the runtime is not resident: each call rebuilds one from the AgentState data</span>
<span class="kw">class</span> <span class="fn">AgentLoop</span>:
    <span class="nb">@staticmethod</span>
    <span class="kw">def</span> <span class="fn">load</span>(agent_state: AgentState, actor):
        <span class="cm"># pick a runtime implementation from the saved agent_type, feed state in</span>
        <span class="kw">if</span> agent_state.agent_type <span class="kw">in</span> (letta_v1_agent, sleeptime_agent):
            <span class="kw">return</span> <span class="fn">LettaAgentV3</span>(agent_state=agent_state, actor=actor)
        <span class="kw">return</span> <span class="fn">LettaAgentV2</span>(agent_state=agent_state, actor=actor)
</pre></div>

<div class="card warn">
  <div class="tag">⚠️ Common pitfall</div>
  <strong>"Stateful data" is not "a stateful runtime" — don't conflate the two.</strong> Calling a Letta agent "stateful" means its state is <strong>persisted as data</strong> (<span class="mono">AgentState</span>); that exists <strong>precisely to serve a stateless runtime</strong> (a precise recap of Lesson 3). The model itself is stateless — it doesn't remember the previous turn; the runtime is stateless too — it's rebuilt and torn down per request, never resident in memory. <strong>The only thing that actually "remembers" is the saved data.</strong> So the correct mental model is: <em>state lives in the data (durable, owned, portable), compute lives in the runtime (short-lived, rebuildable)</em>. If you imagine "stateful" means "a permanently running agent process holding things in memory," you'll badly misread Letta: it deliberately does not do that — and precisely because it doesn't, it earns the payoffs of being copyable, versionable, and movable.
</div>

<h2>One piece of data, two models: schema (pydantic) vs orm (SQLAlchemy)</h2>
<p>Here's a spot beginners trip on: the same "Block" or "Agent" has <strong>two</strong> class definitions in the code. One in <span class="mono">letta/schemas/</span> (pydantic), one in <span class="mono">letta/orm/</span> (SQLAlchemy). This isn't redundancy — it's <strong>deliberate layering</strong>, each owning one job:</p>

<div class="cols">
  <div class="col">
    <h4>schema: pydantic (API contract)</h4>
    <p>Lives in <span class="mono">letta/schemas/</span>. It defines <strong>the shape promised to the outside</strong>: what requests/responses look like, field types, validation rules. It's a <strong>stable API contract</strong> that frontends, SDKs, and docs depend on — it must not wobble with DB internals.</p>
  </div>
  <div class="col">
    <h4>orm: SQLAlchemy (DB row)</h4>
    <p>Lives in <span class="mono">letta/orm/</span>. It defines <strong>how data lands in tables</strong>: columns, indexes, foreign keys, relations. It serves storage and queries and can be tuned for performance <strong>without disturbing the external contract</strong>.</p>
  </div>
</div>

<p>The two are bridged by <strong>conversion in the manager layer</strong>: read an orm row from the DB, call something like <span class="mono">to_pydantic_async</span> to turn it into a pydantic schema for the client; reverse on write. Tellingly, some pydantic configs (like <span class="mono">llm_config</span>) are themselves structured objects, so Letta just <strong>stores them whole as JSON in a column</strong> — the "pydantic-in-DB" glue lives in <span class="mono">letta/orm/custom_columns.py</span>. So the same config is <strong>a typed pydantic object outside and a JSON column inside</strong> — both sides happy.</p>

<p>While we're here, clear up the most commonly misremembered naming: each resource actually has <strong>three verbs</strong> mapping to three differently-shaped objects — what you use to "create," to "update," and what you "read" — don't conflate them:</p>

<div class="cellgroup">
  <div class="cg-cap"><b>Each resource's "three verbs"</b>: create, update, read are three differently-shaped objects (note it's <span class="mono">BlockUpdate</span>, not UpdateBlock)</div>
  <div class="cells">
    <span class="cell hl">create · Create*<br>CreateBlock / CreateAgent</span>
    <span class="cell">update · *Update<br>BlockUpdate / UpdateAgent</span>
    <span class="cell scale">read · full object<br>Block / AgentState</span>
  </div>
</div>

<div class="codefile">
  <div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/block.py</span><span class="ln">create / update / read trio (simplified)</span></div>
<pre><span class="cm"># create: fields the client gives to make a new memory block (no id, server generates it)</span>
<span class="kw">class</span> <span class="fn">CreateBlock</span>(BaseBlock):
    label: str                       <span class="cm"># e.g. "human" / "persona"</span>
    value: str                       <span class="cm"># the memory content</span>

<span class="cm"># update: only the fields to change, rest optional (it's BlockUpdate, not UpdateBlock)</span>
<span class="kw">class</span> <span class="fn">BlockUpdate</span>(BaseBlock):
    value: Optional[str] = <span class="kw">None</span>
    limit: Optional[int] = <span class="kw">None</span>

<span class="cm"># read: the full object the server returns, with a stable prefixed id and timestamps</span>
<span class="kw">class</span> <span class="fn">Block</span>(BaseBlock):
    id: str = <span class="fn">Field</span>(..., description=<span class="st">"block-…"</span>)
    value: str
    <span class="cm"># plus label / limit, etc.; timestamps and organization_id live on the orm row</span>
</pre></div>

<p>The same trio applies to agents: <strong>create</strong> with <span class="mono">CreateAgent</span>, <strong>update</strong> with <span class="mono">UpdateAgent</span>, and you <strong>read</strong> the full <span class="mono">AgentState</span> (all in <span class="mono">letta/schemas/agent.py</span>). Remember this pattern and every Letta resource API gets easier: <em>request bodies are Create/Update, response bodies are the full schema</em>.</p>

<div class="card spark">
  <div class="tag">💡 Design insight</div>
  <strong>Because the whole agent is just data (a serialized <span class="mono">AgentState</span> with a stable prefixed id), Letta gains a set of properties a "resident-process agent" can never have.</strong> You can treat an agent like a file: <strong>copy</strong> it (clone the data and you have a twin agent), <strong>share</strong> it (hand a block's id to another agent and they share the same memory), <strong>version</strong> it (diff, roll back, commit the state), <strong>inspect</strong> it (read the fields directly instead of guessing what a black-box process is "thinking"). You can also <strong>swap the underlying model</strong> — change one line of <span class="mono">llm_config</span> and the same agent migrates smoothly from one model to another, identity and memory untouched; and you can <strong>run it anywhere</strong> — load the save and it's restored, same agent on a different machine. The root of all this is one sentence: <strong>identity lives in the id, not in a live object.</strong> Demoting an agent from "a process that must stay running" to "data you can store, load, move, and edit at will" looks like a mere engineering choice, but it unlocks every freedom a hosted scheme like OpenAI Assistants cannot give.
</div>

<h2>Head-to-head with OpenAI Assistants</h2>
<p>Put these properties in a comparison table next to OpenAI Assistants — which "hosts the agent in the cloud" — and the gap is obvious. The core split is one sentence: <strong>who owns the state, and can it be handled freely as data</strong>.</p>

<table class="t">
  <tr><th>Dimension</th><th>Letta (agent as stateful data)</th><th>OpenAI Assistants (hosted in cloud)</th></tr>
  <tr><td>Who owns state</td><td>one <span class="mono">AgentState</span> in your DB — you own it, you can read it</td><td>on the server; you only hold an id reference</td></tr>
  <tr><td>Export / version?</td><td>Yes: it's data — copy / diff / commit / roll back</td><td>Hard: no full export of the underlying state</td></tr>
  <tr><td>Model-agnostic?</td><td>Yes: edit <span class="mono">llm_config</span> to swap models, identity intact</td><td>Largely bound to its own models</td></tr>
  <tr><td>Editable memory?</td><td>Yes: core memory is an editable <span class="mono">block</span>; the agent can edit it too</td><td>Limited: opaque memory, hard to edit freely</td></tr>
  <tr><td>Run anywhere?</td><td>Yes: load the save and it's restored — same agent on another machine</td><td>Must go through its hosted API</td></tr>
</table>

<p>None of this says hosting is worthless — it's low-maintenance and ops-free. But the moment your needs include "I want to own it, export it, swap models, edit memory, run it in my own environment," the <strong>"agent-as-data" route has a structural edge</strong>: data can be fully under your control, a process cannot. This echoes Lesson 1's line that "Letta makes an agent as durable and portable as a database record" — and by this lesson you finally see <strong>exactly how</strong> it pulls that off.</p>

<h2>A little deeper</h2>

<details class="accordion"><summary>Why split schema and orm into two models?</summary><div class="acc-body">
<p><strong>Example:</strong> you want to add an index to the Block table, or split a column in two for speed. If the external API and the DB table are the same class, that internal optimization <strong>changes the API shape</strong>, and every client must follow.</p>
<p><strong>Why it's designed this way:</strong> the pydantic schema is the <strong>external contract</strong> (must stay stable), the SQLAlchemy orm is a <strong>storage detail</strong> (must be free to evolve for performance). Decoupling them means the DB can be tuned without disturbing the API, and the API can add validation without touching table structure. The manager layer converts between them (e.g. <span class="mono">to_pydantic_async</span>).</p>
<p><strong>Where in the source:</strong> schemas in <span class="mono">letta/schemas/</span> (e.g. <span class="mono">block.py</span> / <span class="mono">agent.py</span>), orm in <span class="mono">letta/orm/</span>; the glue that stores a pydantic config whole as JSON in a column is <span class="mono">letta/orm/custom_columns.py</span>.</p>
<p><strong>Alternatives:</strong> use one model (the ORM directly as the API model) — easy for small projects, but API and tables become tightly coupled, so any DB refactor leaks into the interface; large, long-evolving systems almost always layer like Letta does.</p>
</div></details>

<details class="accordion"><summary>What's so good about prefixed ids?</summary><div class="acc-body">
<p><strong>Example:</strong> a log shows <span class="mono">block-9f8e…</span> and <span class="mono">agent-1a2b…</span>. Without a lookup you instantly know the first is a memory block and the second an agent — debugging speed changes immediately.</p>
<p><strong>Why it's designed this way:</strong> prefix = type, i.e. "what this is" is <strong>encoded into the id itself</strong>: ① self-describing types, preventing one kind of id from being misused as another; ② readable debugging; ③ the uuid4 part avoids collisions, and the id depends on no auto-increment key or machine, so <strong>it stays valid when exported elsewhere</strong> — the premise of portability.</p>
<p><strong>Where in the source:</strong> <span class="mono">letta/schemas/letta_base.py::LettaBase.generate_id</span> (= <span class="mono">f"{prefix}-{uuid4()}"</span>), with the prefix set by each schema's <span class="mono">__id_prefix__</span> (e.g. <span class="mono">AgentState</span> resolves to <span class="mono">agent</span>).</p>
<p><strong>Alternatives:</strong> plain auto-increment integer keys — compact but <strong>leak scale, collide across DBs, hide the type</strong>; bare uuids (no prefix) — collision-free but lose type readability. A prefixed uuid gets both "no collisions" and "self-describing type."</p>
</div></details>

<details class="accordion"><summary>Where exactly does it differ from OpenAI Assistants?</summary><div class="acc-body">
<p><strong>Example:</strong> you want to <strong>clone a tuned agent three times</strong>, swap a different model into each for A/B, then <strong>commit the best one to a git repo</strong>. In Letta that's "copy the data + edit <span class="mono">llm_config</span> + commit"; in a pure hosted scheme you can't get the underlying state, so you can't do it.</p>
<p><strong>Why it's designed this way:</strong> ownership and form differ — Letta keeps state in <strong>your database</strong> as <strong>readable, editable data</strong>, so export, versioning, model swaps, memory edits, and remote runs all become possible; a hosted scheme keeps state on the server and you hold only a reference.</p>
<p><strong>Where in the source:</strong> the state entity is <span class="mono">letta/schemas/agent.py::AgentState</span>; the model config <span class="mono">llm_config</span> is one of its fields, so swapping models is just editing it; editable memory is <span class="mono">letta/schemas/block.py::Block</span> (with <span class="mono">BlockUpdate</span>).</p>
<p><strong>Alternatives:</strong> hosted Assistants — ops-free, but sacrifices control and portability; self-hosted but still treating the agent as a resident process — lose the process and you lose the state, and copy/version is hard. Letta chooses "agent as data" precisely to win back these freedoms.</p>
</div></details>

<h2>Part 2 ends here: next stop, the memory system</h2>
<p>Part 2 (Foundations), three lessons, wraps up here. Looking back over the arc: Lesson 4 made clear that "agent = LLM + tools + loop" and how tool calling works at the message layer; Lesson 5 made clear that "context is a finite, per-token-billed budget," so memory management is a necessity forced by economics; and this lesson opened "state" itself — <strong>an agent is data that is serializable, has a stable prefixed identity, persists via two models (schema/orm), and round-trips between data and a short-lived runtime</strong>. Together, the three lessons hand you three keys: <strong>tools (how an agent acts), context (why memory must be managed), and state (what an agent physically is)</strong>.</p>
<p>These three keys all point to the same door — <strong>the memory system</strong>, the subject of Part 3. Lesson 5 left the question "where does swapped-out content go, how is it fetched back, how does the agent manage it itself"; this lesson tells you "those managed memories are themselves id-bearing, editable data (<span class="mono">block</span> and friends)." Join them and Part 3 will formally unfold Letta's tiered memory: always-in-window <strong>core memory</strong>, searchable <strong>recall</strong> history, searchable <strong>archival</strong> long-term facts, and the loop where an agent <strong>self-edits</strong> via memory tools. Read on with "an agent is data" as your mental model, and you'll find every design choice in the memory system is a natural extension of this lesson's principle.</p>

<div class="card key">
  <div class="tag">✅ Key points</div>
  <ul>
    <li><strong>An agent is physically data</strong>: one agent = one serializable <span class="mono">AgentState</span> in the DB (memory / message_ids / system / tools / tool_rules / llm_config / embedding_config), no "live object."</li>
    <li><strong>Identity lives in the prefixed id</strong>: <span class="mono">generate_id</span> = <span class="mono">f"{__id_prefix__}-{uuid4()}"</span>, prefix = type (<span class="mono">agent-…</span> / <span class="mono">block-…</span>), giving self-describing types, easy debugging, no collisions, portability.</li>
    <li><strong>schema vs orm, two models</strong>: pydantic (<span class="mono">letta/schemas/</span>) is the stable API contract, SQLAlchemy (<span class="mono">letta/orm/</span>) is evolvable storage; the manager converts, configs stored as JSON columns (<span class="mono">custom_columns.py</span>).</li>
    <li><strong>create/update/read trio</strong>: create with <span class="mono">CreateBlock</span>/<span class="mono">CreateAgent</span>, update with <span class="mono">BlockUpdate</span>/<span class="mono">UpdateAgent</span>, read <span class="mono">Block</span>/<span class="mono">AgentState</span> (note it's BlockUpdate, not UpdateBlock).</li>
    <li><strong>Round-trip, not resident</strong>: DB row → <span class="mono">AgentState</span> → <span class="mono">AgentLoop.load</span> rebuilds a runtime, runs a step → write back; the runtime is a short-lived projection of the data.</li>
    <li><strong>"Stateful data" ≠ "stateful runtime"</strong>: state lives in the data (durable, owned, portable), compute lives in the runtime (short-lived, rebuildable) — a precise recap of Lesson 3.</li>
    <li><strong>vs OpenAI Assistants</strong>: because the agent is data, you can copy / share / version / inspect / swap models / run anywhere — identity lives in the id, not a live object.</li>
  </ul>
</div>
""",
}
