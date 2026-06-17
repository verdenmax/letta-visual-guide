"""Part 6 · The LLM provider abstraction — lessons 21-23."""

LESSON_21 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">前面五个部分，我们一直把"调用大模型"当成一行就能搞定的事——把消息递过去，等它把回复递回来。可现实远没这么干净：Letta 同时支持<strong>二十多家供应商</strong>，从 OpenAI、Anthropic、Google 到 Groq，再到跑在你自己机器上的本地模型，它们的请求长什么样、响应长什么样、连报错字段都各不相同。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课要回答的就是一个问题：怎么把这一堆五花八门的差异，<strong>整整齐齐藏在同一个统一接口背后</strong>，让第 13 到 16 课那套执行循环，从头到尾既不知道、也根本不需要关心自己究竟在跟哪一家说话。这是整个第六部分的开篇。</p>
<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>想象联合国大会的<strong>同声传译</strong>。台上各国代表各说各的语言——有人讲法语、有人讲阿拉伯语、有人讲中文，谁也不迁就谁。这一个个代表，就是一家家 <span class="mono">provider</span>。</p>
<p>但台下的你，耳机里只听到<strong>一种</strong>工作语言。秘密全在传译间：不管代表说什么，翻译都把它转成同一种语言再送进你耳朵，所以你只要听得懂这一种就够了。</p>
<p>Letta 选定的这门"工作语言"，就是 <strong>OpenAI 的响应形状</strong>。台下的 agent 循环只需听懂这一种，台上换谁发言都无所谓——而那个"传译间"，正是本课要拆开的三方法 client。</p>
<p>这个类比里藏着一条关键原则：<strong>统一，不是要求各家都改成一样，而是在中间加一层翻译</strong>。代表们照旧说自己的语言，改变的只是"进你耳朵前先过一道同传"。</p>
<p>也正因为翻译这层在中间，台上哪天多来一个说斯瓦希里语的新代表，台下听众什么都不用重学——这正对应本课反复强调的那句"加一家供应商，循环零改动"。</p>
</div>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>一个字段驱动一个工厂，一套三方法把差异收敛成一种形状</strong>。</p>
<p>驱动分派的字段是 <span class="mono">llm_config.model_endpoint_type</span>。它被传进 <span class="mono">LLMClient.create</span>，里面一个 <span class="mono">match/case</span> 挑出具体的 client 类；没显式列到的，一律落到默认的 <span class="mono">OpenAIClient</span>。</p>
<p>挑出的 client 继承自 <span class="mono">LLMClientBase</span>，核心是三个方法：<span class="mono">build_request_data</span> / <span class="mono">request_async</span> / <span class="mono">convert_response_to_chat_completion</span>，由 <span class="mono">send_llm_request</span> 串起来。无论底下是哪家，最后吐出来的都是 OpenAI 形状的 <span class="mono">ChatCompletionResponse</span>。</p>
<p>把这三层连起来记就一句话：<strong>字段 → 工厂 → 三方法 → 统一形状</strong>。本课剩下的篇幅，都是在把这条链条的每一环逐个讲透。</p>
</div>
<p>所以本课其实就讲三件环环相扣的事：<strong>工厂怎么选 client</strong>、<strong>三方法怎么干活</strong>、<strong>为什么大家最后都长成 OpenAI 的样子</strong>。下面逐个拆开。</p>
<h2>先问一句：为什么需要这层抽象</h2>
<p>在动手拆工厂之前，先想清楚"没有它会怎样"。把有它和没它的两个世界并排摆出来，对比最能说明问题。</p>
<div class="cols">
  <div class="col"><h4>😵 如果没有统一抽象</h4><p>执行循环里会塞满 <span class="mono">if provider == ...</span> 的分支：拼请求要分家写、解响应要分家写，连取个 token 用量都得记住每家字段各叫什么名字。每多接一家，循环就被改一回、也跟着脏一分。</p></div>
  <div class="col"><h4>😌 有了统一抽象</h4><p>循环只对着一个接口、一种形状编程。"究竟是哪家"被整个压进工厂和三方法里，循环既不写分支、也不必随供应商的增减而改动，干净又稳定。</p></div>
</div>
<p>这一对照，几乎就是本课的全部价值：把"会随供应商而变的部分"圈进 client，把"对谁都一样的循环"彻底解放出来。带着这个对照往下看，后面每一处设计的用意都会更清楚。</p>
<h2>工厂：按 endpoint 类型选 client</h2>
<p>先看"挑 client"这一步。整个适配的入口是一张总图：agent 循环把请求交出去，工厂按 <span class="mono">model_endpoint_type</span> 选出具体 client，三方法跑完，再把统一形状的响应交回循环。</p>
<div class="flow">
  <div class="node"><div class="nt">agent 循环</div><div class="nd">只认 OpenAI 形状</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLMClient.create</div><div class="nd">按 model_endpoint_type 选 client</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">三方法</div><div class="nd">build / request / convert</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ChatCompletionResponse</div><div class="nd">通用中间格式</div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">一句话：<strong>选一种数据形状当"普通话"，让每个 provider 翻译成它</strong>。循环只学这一种语言，加多少家供应商都不用改。</span></div>
<p>这个工厂本身很薄——它<strong>不是</strong> client，自己不发任何请求，只负责"按类型造出对的 client"。换句话说，它是一道分诊台：不看病、只分科，把你转给对的专科医生。</p>
<p>下面是简化后的分派逻辑：一个 <span class="mono">@staticmethod</span>，对 <span class="mono">provider_type</span> 做 <span class="mono">match</span>，逐个 <span class="mono">case</span> 返回对应 client，最后用 <span class="mono">case _</span> 兜底。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/llm_client.py</span><span class="ln">LLMClient.create 分派（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">LLMClient</span>:
    <span class="nb">@staticmethod</span>
    <span class="kw">def</span> <span class="fn">create</span>(provider_type, put_inner_thoughts_first=<span class="kw">True</span>, actor=<span class="kw">None</span>):
        <span class="kw">match</span> provider_type:                 <span class="cm"># = llm_config.model_endpoint_type</span>
            <span class="kw">case</span> ProviderType.anthropic:     <span class="kw">return</span> <span class="fn">AnthropicClient</span>(...)
            <span class="kw">case</span> ProviderType.google_vertex: <span class="kw">return</span> <span class="fn">GoogleVertexClient</span>(...)
            <span class="kw">case</span> ProviderType.groq:          <span class="kw">return</span> <span class="fn">GroqClient</span>(...)
            <span class="cm"># … 十几个 case …</span>
            <span class="kw">case</span> _:                          <span class="kw">return</span> <span class="fn">OpenAIClient</span>(...)   <span class="cm"># 默认：openai/ollama/vllm/… 都落这</span>
</pre></div>
<div class="note info"><span class="ni">💡</span><span class="nx"><span class="mono">LLMClient</span> 自己不是 client，它只<strong>造</strong> client。分派靠的是 <span class="mono">llm_config.model_endpoint_type</span>——因为 <span class="mono">ProviderType(str, Enum)</span> 本质是字符串，<span class="mono">match/case</span> 才能直接拿它来匹配。</span></div>
<p>把分派关系列成表会更直观。注意最后一行：一大票常见 endpoint 其实都<strong>共用</strong>那个默认 client，并不是每家都要单独写一个类。</p>
<table class="t">
<tr><th>model_endpoint_type</th><th>选中的 client</th></tr>
<tr><td class="mono">anthropic</td><td class="mono">AnthropicClient</td></tr>
<tr><td class="mono">google_vertex</td><td class="mono">GoogleVertexClient</td></tr>
<tr><td class="mono">groq</td><td class="mono">GroqClient</td></tr>
<tr><td class="mono">openrouter</td><td class="mono">OpenAIClient（显式）</td></tr>
<tr><td class="mono">openai / ollama / vllm / …</td><td class="mono">OpenAIClient（默认 case _）</td></tr>
</table>
<p>为什么这么多家都落到默认那一档？因为它们大多<strong>本就兼容 OpenAI 的接口</strong>——本地推理框架（ollama、vllm、lmstudio…）几乎都提供一个"OpenAI 兼容"端点，于是 Letta 只要把请求发到不同的 <span class="mono">model_endpoint</span>，同一个 <span class="mono">OpenAIClient</span> 就能伺候它们一大票。</p>
<p>换个角度看那十几个 <span class="mono">case</span>：它们其实是一份"<strong>例外名单</strong>"——只有行为确实跟 OpenAI 不一样的家才需要单独列出来，剩下的统统按"OpenAI 兼容"默认处理。名单越短，说明这套标准越通用。</p>
<h2>三方法契约</h2>
<p>选好 client 之后，真正干活的是它从 <span class="mono">LLMClientBase</span> 继承来的三个方法。把它们竖着排开看，就是一条很顺的三步流水线：组请求 → 发请求 → 转形状。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>build_request_data</h4><p>把消息、工具、配置组装成<strong>这一家</strong>认得的请求体。同步方法，返回一个 dict。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>request_async</h4><p>把请求体发出去，拿回这一家的<strong>原始响应</strong>。async 方法，返回一个 dict。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>convert_response_to_chat_completion</h4><p>把原始响应<strong>翻译成 OpenAI 形状</strong>的 ChatCompletionResponse。async 方法。</p></div></div>
</div>
<p>这三步谁来串？是 <span class="mono">send_llm_request</span>——它名字里没带 async，<strong>实际却是个 async 方法</strong>，依次调用三方法，并把<strong>网络请求那一步</strong>（<span class="mono">request_async</span>）抛出的异常交给 <span class="mono">handle_llm_error</span> 兜底。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/llm_client_base.py</span><span class="ln">三方法 + send_llm_request 编排（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">LLMClientBase</span>:
    <span class="nb">@abstractmethod</span>
    <span class="kw">def</span> <span class="fn">build_request_data</span>(self, agent_type, messages, llm_config, tools, ...) -&gt; dict: ...
    <span class="nb">@abstractmethod</span>
    <span class="kw">async def</span> <span class="fn">request_async</span>(self, request_data, llm_config) -&gt; dict: ...
    <span class="nb">@abstractmethod</span>
    <span class="kw">async def</span> <span class="fn">convert_response_to_chat_completion</span>(self, response_data, ...) -&gt; ChatCompletionResponse: ...

    <span class="kw">async def</span> <span class="fn">send_llm_request</span>(self, ...):           <span class="cm"># 编排：串起三步</span>
        data = self.<span class="fn">build_request_data</span>(...)
        <span class="kw">try</span>:    resp = <span class="kw">await</span> self.<span class="fn">request_async</span>(data, llm_config)
        <span class="kw">except</span> Exception <span class="kw">as</span> e: <span class="kw">raise</span> self.<span class="fn">handle_llm_error</span>(e, llm_config)
        <span class="kw">return</span> <span class="kw">await</span> self.<span class="fn">convert_response_to_chat_completion</span>(resp, ...)
</pre></div>
<div class="note tip"><span class="ni">💡</span><span class="nx">"三方法"是<strong>教学化简</strong>。<span class="mono">LLMClientBase</span> 实际有 8 个抽象方法，另外 5 个是 <span class="mono">request</span>（同步）/<span class="mono">request_embeddings</span>/<span class="mono">stream_async</span>/<span class="mono">is_reasoning_model</span>/<span class="mono">handle_llm_error</span>。本课只抓"数据形状"这条主线。</span></div>
<p>注意这条流水线的分工：第 1 步知道"这一家要什么格式"，第 3 步知道"这一家会回什么格式"。<strong>所有 provider 差异，都被关进这首尾两步</strong>，中间的发送与编排则是所有家共用的。</p>
<p>这就是抽象基类最值钱的地方：它把"变的部分"和"不变的部分"切开了。变的是请求体怎么拼、响应怎么解；不变的是"先组、再发、后转，出错就映射成统一异常"这条骨架。新接一家，你只需填那两个变的方法。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">留意三方法的同步／异步差别：<span class="mono">build_request_data</span> 是纯组装、不碰网络，所以是<strong>同步</strong>的；真正要等网络的 <span class="mono">request_async</span>，以及随后处理响应的 <span class="mono">convert</span>，都是 <strong>async</strong>。</span></div>
<h2>OpenAI 形状＝通用中间格式</h2>
<p>三方法里最关键的是第三个。不管底层是 Anthropic 的内容块、Google 的 <span class="mono">functionCall</span>、还是本地模型吐出来的一段纯文本，<span class="mono">convert_*</span> 都把它收敛成<strong>同一个</strong>类型——<span class="mono">ChatCompletionResponse</span>。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/openai/chat_completion_response.py</span><span class="ln">通用中间格式（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">ChatCompletionResponse</span>(BaseModel):    <span class="cm"># 不管哪家 provider，都转成这个</span>
    id: str
    choices: List[Choice]                  <span class="cm"># Choice(message, finish_reason, ...)</span>
    created: int
    model: Optional[str]
    usage: UsageStatistics
    object: Literal[<span class="st">"chat.completion"</span>] = <span class="st">"chat.completion"</span>
</pre></div>
<p>有了这个统一出口，第 14 课那套循环才能放心地<strong>只读固定字段</strong>：从 <span class="mono">choices</span> 取消息和工具调用、从 <span class="mono">usage</span> 取 token 用量，完全不必先问一句"这次是哪家回的"。</p>
<p>顺带一提流式：<span class="mono">stream_async</span> 返回的是 OpenAI SDK 的 <span class="mono">AsyncStream[ChatCompletionChunk]</span>——连"边生成边返回"的分块格式，也统一收敛到 OpenAI 这一套上。</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">可以把 <span class="mono">convert_*</span> 想成翻译官的最后一道工序：前面收到的无论是嵌套 JSON、还是夹着标记的纯文本，到这一步都被誊写进同一张标准表格，下游谁来取，看到的都是同一种排版。</span></div>
<div class="cute"><div class="row"><span class="emoji">🔌🔌🔌</span><span class="lab">各家响应</span><span class="arrow">→</span><span class="emoji">🟢</span><span class="bubble">统一插座</span></div><div class="cap">不同形状的插头 → 转接 → 一个统一插座（OpenAI 形状）：循环只读这一种</div></div>
<h2>统一形状里到底装了什么</h2>
<p>既然全系统都靠 <span class="mono">ChatCompletionResponse</span> 沟通，那就值得花一分钟看清它最关键的几格——因为循环正是靠读这几格来推进的。</p>
<div class="cellgroup"><div class="cg-cap"><b>循环最常读的几格</b></div><div class="cells"><span class="cell hl">choices[].message</span><span class="sep">·</span><span class="cell">choices[].finish_reason</span><span class="sep">·</span><span class="cell">usage.total_tokens</span><span class="sep">·</span><span class="cell">model</span><span class="sep">·</span><span class="cell">id</span></div></div>
<p>其中 <span class="mono">message</span> 装着助手回复与工具调用，第 14 课的循环正是据此决定"要不要再跑下一步"；<span class="mono">usage</span> 则喂给上下文压力的统计，呼应第 12 课的压缩判断。各家原始响应再怪，只要把这几格如实填对，上面的循环就能照常运转。</p>
<p>反过来说，这也是给每个新 client 立的<strong>验收标准</strong>：你的 <span class="mono">convert_*</span> 只要能把这几格填对、填全，就算接通了；填不齐，循环立刻会在取字段时露馅。</p>
<h2>LLMConfig：每个 agent 带的"连接配置"</h2>
<p>工厂要拿到 <span class="mono">model_endpoint_type</span>，这个值究竟从哪来？来自每个 agent 随身携带的 <span class="mono">LLMConfig</span>——一张写着"连这家、用这个模型、窗口多大"的连接配置卡。</p>
<div class="cellgroup"><div class="cg-cap"><b>LLMConfig 关键字段</b></div><div class="cells"><span class="cell hl">model_endpoint_type</span><span class="sep">·</span><span class="cell">model</span><span class="sep">·</span><span class="cell">model_endpoint</span><span class="sep">·</span><span class="cell">context_window</span><span class="sep">·</span><span class="cell">put_inner_thoughts_in_kwargs</span><span class="sep">·</span><span class="cell">max_tokens</span><span class="sep">·</span><span class="cell">enable_reasoner</span></div></div>
<div class="note info"><span class="ni">💡</span><span class="nx">这张卡挂在 <span class="mono">AgentState.llm_config</span> 上（回扣第 13 课）。整个 <span class="mono">LLMConfig</span> 类<strong>已被标记弃用</strong>、导向 <span class="mono">ModelSettings</span>，但它仍是工厂与基类正在消费的活抽象；其中 <span class="mono">model_endpoint_type</span> 就是驱动分派的那一项。</span></div>
<p>把这一串顺下来看就通了：<span class="mono">AgentState</span> 带着 <span class="mono">LLMConfig</span>，循环从中取出 <span class="mono">model_endpoint_type</span> 递给工厂，工厂据此造出 client，client 再用其余字段（<span class="mono">model_endpoint</span>、<span class="mono">context_window</span>、<span class="mono">max_tokens</span>…）去拼这一家的请求。一条线就接通了。</p>
<p>也正因如此，"换一家供应商"在 Letta 里往往只是<strong>换一份 <span class="mono">LLMConfig</span></strong>：把 <span class="mono">model_endpoint_type</span> 和 <span class="mono">model_endpoint</span> 一改，工厂自然分派到另一个 client，循环代码一行都不用动。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">这张卡里还有几个"行为开关"，本部分后两课会用到：<span class="mono">put_inner_thoughts_in_kwargs</span> 决定要不要把内心独白塞成工具参数（第 22 课）、<span class="mono">enable_reasoner</span> 与 <span class="mono">reasoning_effort</span> 控制推理强度、<span class="mono">provider_category</span> 区分平台自带额度还是 BYOK（自带密钥）。</span></div>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>这是一节把<strong>"适配器模式"开到极致</strong>的课。第 13 到 16 课那套循环，从头到尾不知道自己在跟谁说话——秘诀只有一句：<strong>选定一种数据形状当"普通话"，让每个 provider 把自己翻译成它</strong>。</p>
<p>于是 Anthropic 的内容块、Google 的 <span class="mono">functionCall</span>、本地模型吐的纯文本，最后都收敛成同一个 <span class="mono">ChatCompletionResponse</span>，循环读它就行。想加第二十家供应商？写一个子类、实现三个方法，循环一行都不用改。</p>
<p>更"投降式"的一手，是那个默认 <span class="mono">case _ → OpenAIClient</span>：既然行业早已把 OpenAI 的形状奉为事实标准，Letta 干脆把"OpenAI 兼容"设成<strong>默认假设</strong>。这也呼应第 14 课循环消费 <span class="mono">usage</span> 与响应、以及第 12、14 课里 <span class="mono">handle_llm_error</span> 把上下文超限映射成 <span class="mono">ContextWindowExceededError</span>。</p>
<p>这套思路最妙的地方在于它的"传染性"：一旦把 OpenAI 形状定为内部货币，记忆、工具、压缩、持久化这些模块就全都只跟这一种形状打交道，谁也不需要知道下面接的是哪家——抽象的红利就这样一层层往外摊开。</p>
<p>也难怪官方愿意为它牺牲一点"纯净"：用一个也许不完美、但人人都懂的形状，去换来"加供应商不改循环、加模块不问供应商"，这在工程上几乎是稳赚不赔的买卖。</p>
</div>
<h2>回顾：把工厂和三方法连起来跑一遍</h2>
<p>抽象讲完，走一遍具体的会更踏实。假设某个 agent 的 <span class="mono">LLMConfig</span> 里 <span class="mono">model_endpoint_type</span> 是 <span class="mono">groq</span>，循环要发一次请求，幕后会发生这样三件事。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>选 client</h4><p>循环取出 <span class="mono">groq</span> 传给 <span class="mono">LLMClient.create</span>，<span class="mono">match</span> 命中 <span class="mono">GroqClient</span>。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>组 + 发</h4><p><span class="mono">build_request_data</span> 拼出 Groq 要的请求体，<span class="mono">request_async</span> 发出去并拿回原始响应。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>转形状</h4><p><span class="mono">convert_*</span> 把 Groq 的响应翻成 <span class="mono">ChatCompletionResponse</span>，交回循环。</p></div></div>
</div>
<p>从循环的视角看，这一整趟它只递出去一个请求、又收回来一个 <span class="mono">ChatCompletionResponse</span>。"这次走的是 Groq"这件事，被彻底挡在了工厂和三方法里头，循环全程无感。</p>
<p>把 <span class="mono">groq</span> 换成 <span class="mono">anthropic</span>、<span class="mono">google_vertex</span>、或干脆是本地的 <span class="mono">ollama</span>，上面三步的"主语"会换成不同 client，但<strong>形状完全一样</strong>，循环代码同样一字不改——这正是统一契约最直接的红利。</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">记住这条因果：<strong>形状统一在前，循环简单在后</strong>。正因为三方法保证了出口形状一致，第 14 课那段循环才敢写得那么干净——它从不为"这次是哪家"留任何分支。</span></div>
<p>你甚至可以拿这点当调试直觉：要是循环里冒出了类似 <span class="mono">if 是不是 anthropic</span> 的判断，那多半是抽象漏了——这种逻辑的正确归宿，是某个 client 的 <span class="mono">build</span> 或 <span class="mono">convert</span> 里，而不该爬进循环。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">下面两张卡片，把本课牵涉到的真实代码位置、以及几个最容易踩的坑收拢在一起，方便你回头自查或翻源码。</span></div>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">llm_api/llm_client.py::LLMClient.create</span>——<span class="mono">match/case</span> 分派，默认 <span class="mono">OpenAIClient</span>。</p>
<p><span class="mono">llm_api/llm_client_base.py::LLMClientBase</span>——三方法 + <span class="mono">send_llm_request</span> 编排。</p>
<p><span class="mono">schemas/openai/chat_completion_response.py::ChatCompletionResponse</span>——通用中间格式。</p>
<p><span class="mono">schemas/llm_config.py::LLMConfig</span>——已弃用但仍是活路径；错误映射见 <span class="mono">OpenAIClient.handle_llm_error → ContextWindowExceededError</span>（定义在 <span class="mono">letta/errors.py</span>）。</p>
</div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>工厂分派靠的是 <span class="mono">model_endpoint_type</span>（一个 <span class="mono">ProviderType</span> 字符串），<strong>不是</strong> <span class="mono">LLMConfig</span> 对象本身。</p>
<p>没被显式列出的 provider（<span class="mono">openai</span>/<span class="mono">ollama</span>/<span class="mono">vllm</span>…）<strong>不是没人管</strong>，而是统一落到默认的 <span class="mono">case _ → OpenAIClient</span>。</p>
<p><span class="mono">convert_response_to_chat_completion</span> 是 <strong>async</strong>，别当成同步函数调用；"三方法"也只是 8 个抽象方法的教学化简。</p>
<p><span class="mono">LLMConfig</span> 整类虽已弃用，但它<strong>仍在被消费</strong>——别因为标了"deprecated"就以为是死代码、可以直接绕开。</p>
</div>
<h2>再挖深一点</h2>
<p>主线到这里就完整了。下面四个抽屉，专门收那些你大概率会追问的细节——按兴趣展开即可，不展开也不影响对主线的理解。</p>
<details class="accordion"><summary>为什么偏偏选 OpenAI 的形状当"普通话"？</summary><div class="acc-body">
<p>因为它早就是这一行的<strong>事实标准</strong>。大量第三方工具、客户端 SDK、可观测与评测平台，都默认按 <span class="mono">ChatCompletion</span> 那套字段去读写消息、工具调用和用量。选它当中间格式，等于让 Letta 一出生就接上了这一整套现成生态。</p>
<p>反过来想，如果自己另造一套"中立格式"，那么每接入一家供应商、每对接一个外部工具，都得在两套格式之间再翻译一道，维护成本只会越滚越大。与其如此，不如直接站在已经被广泛接受的标准上——这是最省力、也最不容易出错的一手。</p>
<p>它的代价，是把 Letta 和 OpenAI 的这套形状绑得比较紧；但考虑到它的普及程度，这笔交易显然非常划算。</p>
<p>也别把它误读成"OpenAI 形状是最完美的格式"。它未必最优雅，但胜在<strong>足够通用、足够流行</strong>——在工程里，"大家都认得"往往比"设计最漂亮"更值钱。</p>
</div></details>
<details class="accordion"><summary>"三方法"其实是几个方法？</summary><div class="acc-body">
<p>严格说是 <strong>8 个</strong> <span class="mono">@abstractmethod</span>。除了本课主线的 build、request_async、convert 这三个，还有同步版的 <span class="mono">request</span>、做向量嵌入的 <span class="mono">request_embeddings</span>、做流式输出的 <span class="mono">stream_async</span>、判断是否推理模型的 <span class="mono">is_reasoning_model</span>，以及统一错误处理的 <span class="mono">handle_llm_error</span>。</p>
<p>本课之所以只挑那三个讲，是因为它们合起来回答了一个最核心的问题：<strong>一次普通的对话请求，是怎么从"各家格式"一路收敛成"统一形状"的</strong>。其余几个分别照顾同步、嵌入、流式与异常这些旁支场景，机制大同小异，留到真正用得上时再看也不迟。</p>
<p>还有个细节值得一提：正因为这 8 个方法都标了 <span class="mono">@abstractmethod</span>，任何一个具体 client 只要漏实现其中之一，类一被实例化就会报错。等于用类型系统逼着每家把契约老老实实填满。</p>
</div></details>
<details class="accordion"><summary>send_llm_request 和 send_llm_request_async 有什么区别？</summary><div class="acc-body">
<p><span class="mono">send_llm_request</span> 跑的是<strong>完整三步</strong>：先 <span class="mono">build_request_data</span> 把请求体拼出来，再 <span class="mono">request_async</span> 发出去，最后 <span class="mono">convert</span> 成统一形状。你只要把消息和配置交给它，它从头管到尾。</p>
<p>而 <span class="mono">send_llm_request_async</span> 接的是一个<strong>已经建好的</strong> <span class="mono">request_data</span>，于是它跳过第一步，只跑"发请求 + 转形状"这后两步。适合请求体已经在别处组装妥当、想直接拿来复用的场景，省去重复拼装的开销。</p>
<p>什么时候会用到后一个？比如批处理或失败重试时，请求体早就构造好了、只想换个时机再发一遍，这时跳过重复的 build，既省事，也避免了重新拼装可能带来的参数漂移。</p>
</div></details>
<details class="accordion"><summary>各家五花八门的错误，怎么收敛成统一异常？</summary><div class="acc-body">
<p>靠的就是那第 8 个抽象方法 <span class="mono">handle_llm_error</span>。基类提供了一份可用的默认实现：把 <span class="mono">httpx</span> 抛出的连接类错误映射成 <span class="mono">LLMConnectionError</span>，其余未知错误兜底成 <span class="mono">LLMError</span>，让上层至少拿到一个统一的异常类型。</p>
<p><span class="mono">OpenAIClient</span> 在此基础上再具体一层：把"上下文超长"这类 <span class="mono">context_length_exceeded</span> 映射成 <span class="mono">ContextWindowExceededError</span>（定义在 <span class="mono">letta/errors.py</span>），正好接回第 12、14 课讲过的上下文压力与压缩。于是循环只需要 catch 这些统一异常，完全不必去认识每一家各自的错误码和报文格式。</p>
<p>这层映射真正的意义，是让上层只面对一张<strong>稳定的异常词表</strong>：循环看到 <span class="mono">ContextWindowExceededError</span> 就去触发压缩，而压根不用关心它最初是 OpenAI、Anthropic 还是别家抛出来的。</p>
</div></details>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li>工厂 <span class="mono">LLMClient.create</span> 按 <span class="mono">model_endpoint_type</span> 选 client，没显式列到的默认落 <span class="mono">OpenAIClient</span>。</li>
<li>核心三方法 build / request_async / convert，由 <span class="mono">send_llm_request</span> 串联，且它本身是个 async 方法。</li>
<li>输出统一为 OpenAI 形状的 <span class="mono">ChatCompletionResponse</span>，是贯穿全系统的通用中间格式。</li>
<li>agent 循环看不到底下究竟是哪家 provider，自始至终只认这一种形状。</li>
<li><span class="mono">LLMConfig</span> 携带连接配置（含驱动分派的 <span class="mono">model_endpoint_type</span>）；整类已弃用但仍是活路径。</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">一句话收束本课：<strong>endpoint 类型选 client，三方法把差异收敛成 OpenAI 形状，循环只认这一种</strong>。这三句，正是后面两课所有"怪癖隔离"赖以成立的地基。</span></div>
<p>契约这张纸立好了，可各家供应商的"怪脾气"并没就此消失——Anthropic 的提示缓存、Google 的请求格式、给没有原生推理能力的模型<strong>硬注入一段内心独白</strong>……这些差异究竟被藏在哪、又是怎么做到不污染上面那套循环的？下一课，第 22 课就来讲"provider 怪癖的隔离"。</p>
""", "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">For the last five parts we have treated "call the LLM" as a one-liner — hand the messages over, wait for the reply to come back. Reality is far messier: Letta supports <strong>more than twenty providers</strong> at once — from OpenAI, Anthropic and Google to Groq, all the way down to local models running on your own machine — and what their requests look like, what their responses look like, even the names of their error fields, all differ.</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson answers a single question: how do you tuck that pile of wildly different behaviour <strong>neatly behind one unified interface</strong>, so the execution loop from Lessons 13–16 never knows — and never needs to care — which provider it is actually talking to. This is the opening of Part 6.</p>
<div class="card analogy"><div class="tag">🔌 Real-world analogy</div>
<p>Picture the simultaneous interpretation at a UN General Assembly. On the floor, each nation's delegate speaks their own language — one in French, one in Arabic, one in Chinese — and nobody accommodates anyone else. Each of those delegates is one <span class="mono">provider</span>.</p>
<p>But you, down in the audience, hear only <strong>one</strong> working language in your headset. The secret lives in the interpretation booth: whatever a delegate says, the interpreter turns it into the same language before it reaches your ears, so understanding that one language is all you need.</p>
<p>The "working language" Letta settles on is the <strong>OpenAI response shape</strong>. The agent loop in the audience only has to understand this one, and it makes no difference who takes the floor — and that "interpretation booth" is exactly the three-method client we will take apart in this lesson.</p>
<p>Hidden in this analogy is a key principle: <strong>unification is not about forcing everyone to become the same — it is about adding one layer of translation in the middle</strong>. The delegates go on speaking their own languages; all that changes is that "it passes through interpretation before it reaches your ears".</p>
<p>And precisely because that translation layer sits in the middle, the day a new delegate who speaks Swahili shows up, the audience has nothing to relearn — which is exactly the refrain this lesson keeps repeating: "add a provider, change the loop by zero lines".</p>
</div>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Grab this lesson in one sentence: <strong>one field drives one factory, and one set of three methods collapses the differences into one shape</strong>.</p>
<p>The field that drives the dispatch is <span class="mono">llm_config.model_endpoint_type</span>. It is passed into <span class="mono">LLMClient.create</span>, where a <span class="mono">match/case</span> picks out the concrete client class; anything not listed explicitly falls through to the default <span class="mono">OpenAIClient</span>.</p>
<p>The chosen client inherits from <span class="mono">LLMClientBase</span>, whose core is three methods — <span class="mono">build_request_data</span> / <span class="mono">request_async</span> / <span class="mono">convert_response_to_chat_completion</span> — strung together by <span class="mono">send_llm_request</span>. No matter which provider sits underneath, what comes out is always an OpenAI-shaped <span class="mono">ChatCompletionResponse</span>.</p>
<p>Remember the three layers as one line: <strong>field → factory → three methods → unified shape</strong>. The rest of this lesson is just spelling out each link of that chain, one at a time.</p>
</div>
<p>So this lesson really covers three interlocking things: <strong>how the factory picks a client</strong>, <strong>how the three methods do their work</strong>, and <strong>why everyone ends up looking like OpenAI</strong>. Let's take them apart one by one.</p>
<h2>First, a question: why do we need this abstraction</h2>
<p>Before we take the factory apart, let's get clear on "what happens without it". Putting the two worlds — with it and without it — side by side is what makes the case clearest.</p>
<div class="cols">
  <div class="col"><h4>😵 Without a unified abstraction</h4><p>The execution loop fills up with <span class="mono">if provider == ...</span> branches: building requests is written per provider, parsing responses is written per provider, and even reading the token usage means remembering what each provider's fields are called. Every provider you add rewrites the loop once more, and dirties it a little further.</p></div>
  <div class="col"><h4>😌 With a unified abstraction</h4><p>The loop programs against one interface and one shape. "Which provider exactly" is pressed entirely down into the factory and the three methods, so the loop writes no branches and never has to change as providers come and go — clean and stable.</p></div>
</div>
<p>That contrast is almost the whole value of this lesson: fence "the part that varies by provider" inside the client, and set "the loop that is the same for everyone" completely free. Keep this contrast in mind as you read on, and the intent behind every later design choice becomes clearer.</p>
<h2>The factory: pick a client by endpoint type</h2>
<p>Start with the "pick a client" step. The entry point of the whole adaptation is one overview diagram: the agent loop hands a request off, the factory selects a concrete client by <span class="mono">model_endpoint_type</span>, the three methods run, and a unified-shape response is handed back to the loop.</p>
<div class="flow">
  <div class="node"><div class="nt">agent loop</div><div class="nd">only knows the OpenAI shape</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLMClient.create</div><div class="nd">pick client by model_endpoint_type</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">three methods</div><div class="nd">build / request / convert</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">ChatCompletionResponse</div><div class="nd">universal intermediate format</div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">In one line: <strong>pick one data shape as the "lingua franca" and make every provider translate into it</strong>. The loop learns only this one language, and no number of added providers forces a change.</span></div>
<p>The factory itself is thin — it is <strong>not</strong> a client, it sends no request of its own, it only "manufactures the right client by type". Put differently, it is a triage desk: it does not treat you, it only sorts you, and hands you off to the right specialist.</p>
<p>Here is the simplified dispatch logic: a <span class="mono">@staticmethod</span> that runs <span class="mono">match</span> on <span class="mono">provider_type</span>, returns the matching client case by case, and finally falls back with <span class="mono">case _</span>.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/llm_client.py</span><span class="ln">LLMClient.create dispatch (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">LLMClient</span>:
    <span class="nb">@staticmethod</span>
    <span class="kw">def</span> <span class="fn">create</span>(provider_type, put_inner_thoughts_first=<span class="kw">True</span>, actor=<span class="kw">None</span>):
        <span class="kw">match</span> provider_type:                 <span class="cm"># = llm_config.model_endpoint_type</span>
            <span class="kw">case</span> ProviderType.anthropic:     <span class="kw">return</span> <span class="fn">AnthropicClient</span>(...)
            <span class="kw">case</span> ProviderType.google_vertex: <span class="kw">return</span> <span class="fn">GoogleVertexClient</span>(...)
            <span class="kw">case</span> ProviderType.groq:          <span class="kw">return</span> <span class="fn">GroqClient</span>(...)
            <span class="cm"># … a dozen-odd cases …</span>
            <span class="kw">case</span> _:                          <span class="kw">return</span> <span class="fn">OpenAIClient</span>(...)   <span class="cm"># default: openai/ollama/vllm/… all land here</span>
</pre></div>
<div class="note info"><span class="ni">💡</span><span class="nx"><span class="mono">LLMClient</span> is not itself a client; it only <strong>manufactures</strong> clients. The dispatch relies on <span class="mono">llm_config.model_endpoint_type</span> — and because <span class="mono">ProviderType(str, Enum)</span> is essentially a string, <span class="mono">match/case</span> can match on it directly.</span></div>
<p>Laying the dispatch out as a table is more intuitive. Note the last row: a whole crowd of common endpoints actually <strong>share</strong> that default client — not every provider needs its own class.</p>
<table class="t">
<tr><th>model_endpoint_type</th><th>client selected</th></tr>
<tr><td class="mono">anthropic</td><td class="mono">AnthropicClient</td></tr>
<tr><td class="mono">google_vertex</td><td class="mono">GoogleVertexClient</td></tr>
<tr><td class="mono">groq</td><td class="mono">GroqClient</td></tr>
<tr><td class="mono">openrouter</td><td class="mono">OpenAIClient (explicit)</td></tr>
<tr><td class="mono">openai / ollama / vllm / …</td><td class="mono">OpenAIClient (default case _)</td></tr>
</table>
<p>Why do so many providers land in that default bucket? Because most of them are already compatible with OpenAI's interface — local inference frameworks (ollama, vllm, lmstudio…) almost all expose an "OpenAI-compatible" endpoint, so Letta only has to send the request to a different <span class="mono">model_endpoint</span>, and the same <span class="mono">OpenAIClient</span> can serve a whole crowd of them.</p>
<p>Look at that dozen-odd <span class="mono">case</span>s from another angle: they are really an "exceptions list" — only providers whose behaviour genuinely differs from OpenAI need a separate entry, and the rest are all handled as "OpenAI-compatible" by default. The shorter the list, the more universal the standard.</p>
<h2>The three-method contract</h2>
<p>Once a client is chosen, the real work is done by the three methods it inherits from <span class="mono">LLMClientBase</span>. Lined up vertically, they form a smooth three-step pipeline: assemble the request → send the request → convert the shape.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>build_request_data</h4><p>Assemble the messages, tools and config into the request body <strong>this provider</strong> understands. A synchronous method that returns a dict.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>request_async</h4><p>Send the request body off and get back <strong>this provider's</strong> raw response. An async method that returns a dict.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>convert_response_to_chat_completion</h4><p>Translate the raw response <strong>into the OpenAI shape</strong> — a ChatCompletionResponse. An async method.</p></div></div>
</div>
<p>Who strings the three steps together? <span class="mono">send_llm_request</span> — its name carries no <span class="mono">async</span>, yet it is <strong>actually an async method</strong>. It calls the three methods in order and hands any exception from the <strong>request step</strong> (<span class="mono">request_async</span>) to <span class="mono">handle_llm_error</span> as the catch-all.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/llm_client_base.py</span><span class="ln">the three methods + send_llm_request orchestration (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">LLMClientBase</span>:
    <span class="nb">@abstractmethod</span>
    <span class="kw">def</span> <span class="fn">build_request_data</span>(self, agent_type, messages, llm_config, tools, ...) -&gt; dict: ...
    <span class="nb">@abstractmethod</span>
    <span class="kw">async def</span> <span class="fn">request_async</span>(self, request_data, llm_config) -&gt; dict: ...
    <span class="nb">@abstractmethod</span>
    <span class="kw">async def</span> <span class="fn">convert_response_to_chat_completion</span>(self, response_data, ...) -&gt; ChatCompletionResponse: ...

    <span class="kw">async def</span> <span class="fn">send_llm_request</span>(self, ...):           <span class="cm"># orchestration: string the three steps</span>
        data = self.<span class="fn">build_request_data</span>(...)
        <span class="kw">try</span>:    resp = <span class="kw">await</span> self.<span class="fn">request_async</span>(data, llm_config)
        <span class="kw">except</span> Exception <span class="kw">as</span> e: <span class="kw">raise</span> self.<span class="fn">handle_llm_error</span>(e, llm_config)
        <span class="kw">return</span> <span class="kw">await</span> self.<span class="fn">convert_response_to_chat_completion</span>(resp, ...)
</pre></div>
<div class="note tip"><span class="ni">💡</span><span class="nx">"Three methods" is a <strong>teaching simplification</strong>. <span class="mono">LLMClientBase</span> actually has 8 abstract methods; the other 5 are <span class="mono">request</span> (sync) / <span class="mono">request_embeddings</span> / <span class="mono">stream_async</span> / <span class="mono">is_reasoning_model</span> / <span class="mono">handle_llm_error</span>. This lesson grabs only the "data shape" through-line.</span></div>
<p>Notice the division of labour in this pipeline: step 1 knows "what format this provider wants", step 3 knows "what format this provider replies in". <strong>All provider differences are locked into these two end steps</strong>, while the sending and orchestration in the middle are shared by every provider.</p>
<p>This is where the abstract base class earns its keep: it cuts "the part that varies" apart from "the part that stays fixed". What varies is how the request body is assembled and how the response is parsed; what stays fixed is the skeleton "assemble first, then send, then convert, and map errors into one unified exception". To onboard a new provider, you only fill in those two varying methods.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">Watch the sync/async split across the three methods: <span class="mono">build_request_data</span> is pure assembly and touches no network, so it is <strong>synchronous</strong>; the network-waiting <span class="mono">request_async</span>, and the <span class="mono">convert</span> that then processes the response, are both <strong>async</strong>.</span></div>
<h2>The OpenAI shape = the universal intermediate format</h2>
<p>The most critical of the three methods is the third. Whether the layer below is Anthropic's content blocks, Google's <span class="mono">functionCall</span>, or a stretch of plain text spat out by a local model, <span class="mono">convert_*</span> collapses it into one and the same type — <span class="mono">ChatCompletionResponse</span>.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/schemas/openai/chat_completion_response.py</span><span class="ln">the universal intermediate format (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">ChatCompletionResponse</span>(BaseModel):    <span class="cm"># whichever provider, it all converts to this</span>
    id: str
    choices: List[Choice]                  <span class="cm"># Choice(message, finish_reason, ...)</span>
    created: int
    model: Optional[str]
    usage: UsageStatistics
    object: Literal[<span class="st">"chat.completion"</span>] = <span class="st">"chat.completion"</span>
</pre></div>
<p>With this unified exit, the loop from Lesson 14 can safely <strong>read only fixed fields</strong>: take the message and tool calls from <span class="mono">choices</span>, take the token usage from <span class="mono">usage</span>, never first asking "which provider replied this time".</p>
<p>A note on streaming: <span class="mono">stream_async</span> returns the OpenAI SDK's <span class="mono">AsyncStream[ChatCompletionChunk]</span> — even the "generate-as-you-go" chunk format is collapsed onto OpenAI's set as well.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Think of <span class="mono">convert_*</span> as the interpreter's final step: whatever arrived earlier — nested JSON, or plain text laced with markers — is at this step transcribed into the same standard form, and whoever fetches it downstream sees the very same layout.</span></div>
<div class="cute"><div class="row"><span class="emoji">🔌🔌🔌</span><span class="lab">each provider's response</span><span class="arrow">→</span><span class="emoji">🟢</span><span class="bubble">one unified socket</span></div><div class="cap">differently shaped plugs → adapter → one unified socket (the OpenAI shape): the loop reads only this one</div></div>
<h2>What exactly sits inside the unified shape</h2>
<p>Since the whole system communicates through <span class="mono">ChatCompletionResponse</span>, it is worth a minute to see clearly its most critical cells — because the loop advances precisely by reading these few cells.</p>
<div class="cellgroup"><div class="cg-cap"><b>the cells the loop reads most</b></div><div class="cells"><span class="cell hl">choices[].message</span><span class="sep">·</span><span class="cell">choices[].finish_reason</span><span class="sep">·</span><span class="cell">usage.total_tokens</span><span class="sep">·</span><span class="cell">model</span><span class="sep">·</span><span class="cell">id</span></div></div>
<p>Of these, <span class="mono">message</span> holds the assistant reply and the tool calls, and the loop in Lesson 14 decides "whether to run another step" exactly from it; <span class="mono">usage</span> in turn feeds the context-pressure statistics, echoing the compaction decision from Lesson 12. However strange a provider's raw response, as long as these cells are filled in faithfully, the loop above runs as usual.</p>
<p>Conversely, this is also the acceptance test set for every new client: as long as your <span class="mono">convert_*</span> fills these cells correctly and completely, you are wired in; fill them incompletely, and the loop gives itself away the instant it reaches for a field.</p>
<h2>LLMConfig: the "connection profile" each agent carries</h2>
<p>The factory needs <span class="mono">model_endpoint_type</span> — but where does that value come from? From the <span class="mono">LLMConfig</span> every agent carries with it — a connection-profile card that says "connect to this provider, use this model, with this window size".</p>
<div class="cellgroup"><div class="cg-cap"><b>LLMConfig key fields</b></div><div class="cells"><span class="cell hl">model_endpoint_type</span><span class="sep">·</span><span class="cell">model</span><span class="sep">·</span><span class="cell">model_endpoint</span><span class="sep">·</span><span class="cell">context_window</span><span class="sep">·</span><span class="cell">put_inner_thoughts_in_kwargs</span><span class="sep">·</span><span class="cell">max_tokens</span><span class="sep">·</span><span class="cell">enable_reasoner</span></div></div>
<div class="note info"><span class="ni">💡</span><span class="nx">This card hangs on <span class="mono">AgentState.llm_config</span> (calling back to Lesson 13). The whole <span class="mono">LLMConfig</span> class is <strong>marked deprecated</strong> and points toward <span class="mono">ModelSettings</span>, yet it is still the live abstraction the factory and the base class consume; within it, <span class="mono">model_endpoint_type</span> is the very item that drives the dispatch.</span></div>
<p>Trace the chain and it all connects: <span class="mono">AgentState</span> carries the <span class="mono">LLMConfig</span>, the loop pulls <span class="mono">model_endpoint_type</span> out of it and hands it to the factory, the factory builds the client from that, and the client then uses the remaining fields (<span class="mono">model_endpoint</span>, <span class="mono">context_window</span>, <span class="mono">max_tokens</span>…) to assemble this provider's request. One line is now wired end to end.</p>
<p>And precisely for that reason, "switching providers" in Letta is often just <strong>swapping one <span class="mono">LLMConfig</span></strong>: change <span class="mono">model_endpoint_type</span> and <span class="mono">model_endpoint</span>, and the factory naturally dispatches to a different client, with not a single line of loop code touched.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">This card also carries a few "behaviour switches" the next two lessons of this part will use: <span class="mono">put_inner_thoughts_in_kwargs</span> decides whether to stuff the inner monologue into a tool argument (Lesson 22), <span class="mono">enable_reasoner</span> and <span class="mono">reasoning_effort</span> control reasoning strength, and <span class="mono">provider_category</span> distinguishes platform-included quota from BYOK (bring-your-own-key).</span></div>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>This is a lesson that pushes the <strong>adapter pattern to its limit</strong>. The loop from Lessons 13–16 never, from start to finish, knows who it is talking to — and the secret is one sentence: <strong>settle on one data shape as the "lingua franca" and make every provider translate itself into it</strong>.</p>
<p>So Anthropic's content blocks, Google's <span class="mono">functionCall</span>, and the plain text a local model spits out all collapse into the same <span class="mono">ChatCompletionResponse</span>, and the loop just reads it. Want to add a twentieth provider? Write a subclass, implement three methods, and change not one line of the loop.</p>
<p>An even more "surrender-style" move is that default <span class="mono">case _ → OpenAIClient</span>: since the industry long ago enshrined OpenAI's shape as the de facto standard, Letta simply makes "OpenAI-compatible" the <strong>default assumption</strong>. This also echoes Lesson 14's loop consuming <span class="mono">usage</span> and the response, and the way <span class="mono">handle_llm_error</span> in Lessons 12 and 14 maps a context overflow into <span class="mono">ContextWindowExceededError</span>.</p>
<p>The cleverest thing about this approach is its "contagiousness": once the OpenAI shape is set as the internal currency, modules like memory, tools, compaction and persistence all deal with this one shape only, and none of them needs to know which provider sits below — the abstraction's dividend spreads outward, layer by layer.</p>
<p>No wonder the maintainers are willing to sacrifice a little "purity" for it: trading a shape that is perhaps imperfect but understood by everyone for "add a provider without changing the loop, add a module without asking about the provider" is, in engineering terms, an almost sure-win bargain.</p>
</div>
<h2>Recap: run the factory and the three methods together once</h2>
<p>With the abstraction explained, walking through a concrete pass makes it feel more solid. Suppose some agent's <span class="mono">LLMConfig</span> has <span class="mono">model_endpoint_type</span> = <span class="mono">groq</span>, and the loop is about to send one request — three things happen behind the scenes.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>pick the client</h4><p>The loop pulls out <span class="mono">groq</span> and passes it to <span class="mono">LLMClient.create</span>; the <span class="mono">match</span> hits <span class="mono">GroqClient</span>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>build + send</h4><p><span class="mono">build_request_data</span> assembles the request body Groq wants, and <span class="mono">request_async</span> sends it off and gets back the raw response.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>convert the shape</h4><p><span class="mono">convert_*</span> translates Groq's response into a <span class="mono">ChatCompletionResponse</span> and hands it back to the loop.</p></div></div>
</div>
<p>From the loop's point of view, the whole trip only hands out one request and collects back one <span class="mono">ChatCompletionResponse</span>. The fact that "this run went through Groq" is completely walled off inside the factory and the three methods, and the loop feels nothing throughout.</p>
<p>Swap <span class="mono">groq</span> for <span class="mono">anthropic</span>, <span class="mono">google_vertex</span>, or simply a local <span class="mono">ollama</span>, and the "subject" of the three steps above becomes a different client, but <strong>the shape is exactly the same</strong> and the loop code likewise does not change by a single character — this is the most direct dividend of a unified contract.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Remember this cause and effect: <strong>the shape is unified first, the loop is simple second</strong>. Precisely because the three methods guarantee a consistent exit shape, the loop in Lesson 14 dares to be written so cleanly — it never reserves any branch for "which provider this time".</span></div>
<p>You can even use this as a debugging instinct: if a check like <span class="mono">if is_anthropic</span> shows up inside the loop, the abstraction has most likely leaked — the right home for that logic is some client's <span class="mono">build</span> or <span class="mono">convert</span>, not crawling up into the loop.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">The next two cards gather up the real code locations this lesson touches, along with a few of the easiest pitfalls to step on — handy for self-checking later or digging into the source.</span></div>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">llm_api/llm_client.py::LLMClient.create</span> — <span class="mono">match/case</span> dispatch, default <span class="mono">OpenAIClient</span>.</p>
<p><span class="mono">llm_api/llm_client_base.py::LLMClientBase</span> — the three methods + <span class="mono">send_llm_request</span> orchestration.</p>
<p><span class="mono">schemas/openai/chat_completion_response.py::ChatCompletionResponse</span> — the universal intermediate format.</p>
<p><span class="mono">schemas/llm_config.py::LLMConfig</span> — deprecated but still a live path; for error mapping see <span class="mono">OpenAIClient.handle_llm_error → ContextWindowExceededError</span> (defined in <span class="mono">letta/errors.py</span>).</p>
</div>
<div class="card warn"><div class="tag">⚠️ Common misconceptions</div>
<p>The factory dispatches on <span class="mono">model_endpoint_type</span> (a <span class="mono">ProviderType</span> string), <strong>not</strong> on the <span class="mono">LLMConfig</span> object itself.</p>
<p>Providers not listed explicitly (<span class="mono">openai</span>/<span class="mono">ollama</span>/<span class="mono">vllm</span>…) are <strong>not unhandled</strong>; they all land in the default <span class="mono">case _ → OpenAIClient</span>.</p>
<p><span class="mono">convert_response_to_chat_completion</span> is <strong>async</strong>; don't call it as a synchronous function. And "three methods" is only a teaching simplification of 8 abstract methods.</p>
<p>Although the entire <span class="mono">LLMConfig</span> class is deprecated, it is <strong>still being consumed</strong> — don't assume that because it is tagged "deprecated" it is dead code you can route around.</p>
</div>
<h2>Dig a little deeper</h2>
<p>The main thread is complete at this point. The four drawers below collect the details you are likely to ask about — expand them as your interest dictates; leaving them closed costs you nothing on the main thread.</p>
<details class="accordion"><summary>Why pick OpenAI's shape, of all shapes, as the "lingua franca"?</summary><div class="acc-body">
<p>Because it has long been the de facto standard of this field. A vast number of third-party tools, client SDKs, and observability and evaluation platforms read and write messages, tool calls and usage by the <span class="mono">ChatCompletion</span> set of fields by default. Choosing it as the intermediate format means Letta plugs into this whole ready-made ecosystem the moment it is born.</p>
<p>Think of it in reverse: if you built your own "neutral format", then every provider you onboard and every external tool you integrate would have to translate once more between the two formats, and the maintenance cost would only snowball. Rather than that, stand directly on a widely accepted standard — it is the least-effort and least-error-prone move.</p>
<p>The cost is that it binds Letta fairly tightly to OpenAI's shape; but given how widespread that shape is, the trade is clearly very worthwhile.</p>
<p>Don't misread this as "the OpenAI shape is the most perfect format". It is not necessarily the most elegant, but it wins on being universal enough and popular enough — in engineering, "everyone recognizes it" is often worth more than "the prettiest design".</p>
</div></details>
<details class="accordion"><summary>How many methods is "three methods" really?</summary><div class="acc-body">
<p>Strictly, it is <strong>8</strong> <span class="mono">@abstractmethod</span>s. Besides this lesson's main-thread three — build, request_async, convert — there are also the synchronous <span class="mono">request</span>, the vector-embedding <span class="mono">request_embeddings</span>, the streaming <span class="mono">stream_async</span>, the reasoning-model check <span class="mono">is_reasoning_model</span>, and the unified error handling <span class="mono">handle_llm_error</span>.</p>
<p>This lesson picks only those three because together they answer the most central question: how does a plain chat request collapse all the way from "each provider's format" into "one unified shape". The rest cover side scenarios — sync, embeddings, streaming and exceptions — and their mechanisms are broadly alike, so there is no rush to look at them until you actually need them.</p>
<p>One more detail worth mentioning: precisely because all 8 methods are tagged <span class="mono">@abstractmethod</span>, if a concrete client misses implementing even one of them, the class errors out the moment it is instantiated. It amounts to using the type system to force every provider to fill the contract honestly and completely.</p>
</div></details>
<details class="accordion"><summary>What's the difference between send_llm_request and send_llm_request_async?</summary><div class="acc-body">
<p><span class="mono">send_llm_request</span> runs the <strong>full three steps</strong>: first <span class="mono">build_request_data</span> assembles the request body, then <span class="mono">request_async</span> sends it off, and finally <span class="mono">convert</span> turns it into the unified shape. Hand it the messages and config, and it manages everything from start to finish.</p>
<p><span class="mono">send_llm_request_async</span>, by contrast, takes a <strong>pre-built</strong> <span class="mono">request_data</span>, so it skips the first step and runs only the latter two — "send the request + convert the shape". It suits scenarios where the request body was already assembled elsewhere and you want to reuse it directly, sparing the cost of reassembly.</p>
<p>When would you use the latter? In batch processing or retries after failure, say, where the request body was constructed long ago and you only want to send it again at a different moment — skipping the repeated build is both less work and avoids the parameter drift a re-assembly might introduce.</p>
</div></details>
<details class="accordion"><summary>How do providers' wildly varied errors collapse into one unified exception?</summary><div class="acc-body">
<p>It relies on that eighth abstract method, <span class="mono">handle_llm_error</span>. The base class provides a usable default implementation: it maps connection-type errors thrown by <span class="mono">httpx</span> into <span class="mono">LLMConnectionError</span>, and catches the remaining unknown errors as <span class="mono">LLMError</span>, so the upper layer at least receives one unified exception type.</p>
<p><span class="mono">OpenAIClient</span> adds one more concrete layer on top: it maps a "context too long" <span class="mono">context_length_exceeded</span> into <span class="mono">ContextWindowExceededError</span> (defined in <span class="mono">letta/errors.py</span>), tying right back to the context pressure and compaction from Lessons 12 and 14. So the loop only needs to catch these unified exceptions, and never has to recognize each provider's own error codes and message formats.</p>
<p>The real point of this mapping layer is that the upper layer faces only a <strong>stable vocabulary of exceptions</strong>: when the loop sees <span class="mono">ContextWindowExceededError</span> it triggers compaction, without caring in the slightest whether it was originally thrown by OpenAI, Anthropic or someone else.</p>
</div></details>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li>The factory <span class="mono">LLMClient.create</span> picks a client by <span class="mono">model_endpoint_type</span>; anything not listed explicitly defaults to <span class="mono">OpenAIClient</span>.</li>
<li>The core three methods — build / request_async / convert — are strung together by <span class="mono">send_llm_request</span>, which is itself an async method.</li>
<li>The output is uniformly an OpenAI-shaped <span class="mono">ChatCompletionResponse</span>, the universal intermediate format running through the whole system.</li>
<li>The agent loop cannot see which provider sits underneath; from start to finish it only knows this one shape.</li>
<li><span class="mono">LLMConfig</span> carries the connection config (including the dispatch-driving <span class="mono">model_endpoint_type</span>); the whole class is deprecated but still a live path.</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">Close the lesson in one line: <strong>the endpoint type picks the client, the three methods collapse the differences into the OpenAI shape, and the loop knows only this one</strong>. These three clauses are the very foundation on which all the "quirk isolation" in the next two lessons rests.</span></div>
<p>The contract is now on paper, but the providers' "quirks" have not vanished with it — Anthropic's prompt caching, Google's request format, force-injecting an inner monologue into a model with no native reasoning… where exactly are these differences hidden, and how do they avoid polluting the loop above? The next lesson, Lesson 22, takes up "isolating provider quirks".</p>
"""}


LESSON_22 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">上一课我们把"统一契约"立在了纸面上：一个工厂按类型选 client，三方法把差异收敛成 OpenAI 形状。可纸面平整，不等于底下风平浪静——<strong>各家 LLM 的脾气其实大不相同</strong>：Anthropic 要你贴 <span class="mono">cache_control</span> 缓存标记、Google 连字段名都另起一套、有的模型干脆没有原生推理能力。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课要回答的就是：这些五花八门的怪癖，到底<strong>怎么被一个个关进各自的 client 子类里</strong>——关到第 13 到 16 课那套执行循环之上、对它们一无所知、也根本无需知道。这是统一契约真正开始"兑现红利"的一课。</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">说"兑现红利"不夸张：上一课花力气立的那套统一形状，到这一课才真正显出价值——正因为有它兜底，各家的怪癖才有地方可藏，而不必摊到循环里碍眼。</span></div>
<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>想象一个演员，<strong>一张脸</strong>，按不同场次戴上不同面具登台。那张脸，就是上一课的 <span class="mono">OpenAIClient</span>；而一个个面具，就是各家 provider 的子类。</p>
<p>妙处在于：<strong>换面具不用换脸</strong>。大多数子类要做的，只是把面具上某一处改一改——通常就是换个 <span class="mono">base_url</span>，顶多再顺手抹掉或补上一两个字段。</p>
<p>于是同一张脸，戴上 Groq 的面具就去演 Groq，戴上 xAI 的面具就去演 xAI。台下的循环始终只看到"那个演员"，至于这场他戴的是哪张面具，循环全程不关心。</p>
<p>这条类比藏着本课的主张：<strong>怪癖不该摊在循环里到处都是，而该被收进各自的面具</strong>——也就是子类那两个被重写的方法里。</p>
<p>这副面具的比喻还能再推一步：面具越薄越好——子类写得越少，意味着复用得越彻底、要单独维护的"特例"也越少。Letta 大多数子类都只有寥寥几行，正是这个道理。</p>
</div>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>怪癖只藏在两个方法里，循环之上永远是同一种形状</strong>。</p>
<p>先看复用有多狠：<span class="mono">OpenAIClient</span> 一个类，被 <strong>8 个显式子类</strong>外加默认 <span class="mono">case _</span> 共同复用，诀窍只是换一个 <span class="mono">base_url</span>——同一套 OpenAI SDK，指向不同 URL 就接上不同的家。</p>
<p>再看怪癖关在哪：子类<strong>只重写两个方法</strong>——<span class="mono">build_request_data</span>（出门前改请求）与 <span class="mono">convert_response_to_chat_completion</span>（回来后改响应），常常是先 <span class="mono">super()</span> 拿到 OpenAI 形状、再就地改几笔。</p>
<p>本课最妙的一手怪招，是把<strong>内心独白硬塞成工具的第一个参数</strong> <span class="mono">thinking</span>，响应时再 <span class="mono">unpack</span> 抽回消息正文；外加 Anthropic 独有的 cache / thinking / batch 三件套。这几样，就是下面要逐个拆开的对象。</p>
<p>把这四件事记成一条链：<strong>复用省掉重复、两方法关住差异、内心独白补出思考、开关切换模拟与原生</strong>。下面三个小节顺着这条链走，最后再单看 Anthropic 这个怪癖最密集的家族。</p>
<p>这条链也是一道"<strong>抽象的防线</strong>"：每往里走一层，外面的代码就少操一份心。循环不必懂 provider，记忆 / 工具 / 压缩等模块更不必——它们只跟统一形状打交道。</p>
</div>
<h2>OpenAIClient：一个类服务多家</h2>
<p>先看最省事的那条路——大量 provider 根本不需要新写 client，它们直接复用 <span class="mono">OpenAIClient</span>。把整条继承谱系画出来，三大家族一目了然。</p>
<p>看图先约定一个方法：把每个 client 想成"基类定骨架、子类补细节"。骨架（三方法的契约）只在三个家族基类里各写一遍，子类拿来就用，顶多覆盖其中一两个方法。</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">抽象基类</span><span class="name">LLMClientBase</span></div>
    <div class="ld">定义三方法契约（上一课）。下面三大家族都从它派生，各自实现一套"出门改请求、回来改响应"。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">OpenAI 家族</span><span class="name">OpenAIClient ← 8 个子类</span></div>
    <div class="ld">Azure / Baseten / Deepseek / Fireworks / Groq / Together / XAI / ZAI 都继承它；<span class="mono">openrouter</span> 与默认 <span class="mono">case _</span> 干脆直接复用它本身。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Anthropic 家族</span><span class="name">AnthropicClient ← Bedrock / MiniMax</span></div>
    <div class="ld">它自己<strong>也是</strong>一个复用基类：<span class="mono">BedrockClient</span> 与 <span class="mono">MiniMaxClient</span> 继承它，再各改各的怪癖。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">Google 家族</span><span class="name">GoogleVertexClient ← GoogleAIClient</span></div>
    <div class="ld"><span class="mono">GoogleAIClient</span> 继承 <span class="mono">GoogleVertexClient</span>；字段名、角色名、内心独白的位置，都另起一套。</div></div>
</div>
<p>看这棵树就懂了：真正"从零写"的只有三个家族基类，其余全是站在它们肩膀上的薄薄一层子类。OpenAI 家族尤其夸张——一个基类背后挂着 8 个子类，还兜着所有没列名的 provider。</p>
<div class="cellgroup"><div class="cg-cap"><b>OpenAIClient 的 8 个显式子类</b></div><div class="cells"><span class="cell hl">AzureClient</span><span class="sep">·</span><span class="cell">BasetenClient</span><span class="sep">·</span><span class="cell">DeepseekClient</span><span class="sep">·</span><span class="cell">FireworksClient</span><span class="sep">·</span><span class="cell">GroqClient</span><span class="sep">·</span><span class="cell">TogetherClient</span><span class="sep">·</span><span class="cell">XAIClient</span><span class="sep">·</span><span class="cell">ZAIClient</span></div></div>
<div class="note info"><span class="ni">💡</span><span class="nx">一个类服务多家的诀窍：<span class="mono">OpenAIClient._prepare_client_kwargs</span> 只把 <span class="mono">base_url</span> 设成 <span class="mono">llm_config.model_endpoint</span>——同一套 OpenAI SDK，换个 URL 就接上一家。约 <strong>19/25</strong> 的 <span class="mono">ProviderType</span> 最终落到 <span class="mono">OpenAIClient</span> 或其子类，仅 6 种不用（anthropic / bedrock / chatgpt_oauth / google_ai / google_vertex / minimax）。</span></div>
<p>为什么"只换一个 <span class="mono">base_url</span>"就够用？因为这些 provider 大多直接对外提供 <strong>OpenAI 兼容</strong>的接口：请求体、响应体的形状本就和 OpenAI 对得上，真正不同的只是服务器地址。Letta 抓住这一点，把它们统统划进默认那一档，连子类都省了。</p>
<p>需要单独写子类的，往往是那些"OpenAI 兼容、但还差一口气"的家——某个模型不认某个参数、或多要一个字段。这时子类才登场，<span class="mono">super()</span> 之后补这一口气就好，不必从头另起炉灶。</p>
<h2>子类只改两个方法</h2>
<p>那 8 个子类里头到底写了什么？答案出奇地短：<strong>大多只动两个方法</strong>。下面这个 <span class="mono">XAIClient</span> 就是典型——先调 <span class="mono">super()</span> 拿到标准 OpenAI 请求，再只针对自家某个模型删掉两个惩罚字段。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/xai_client.py</span><span class="ln">一个子类只在 super() 之后改字段（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">XAIClient</span>(OpenAIClient):
    <span class="kw">def</span> <span class="fn">build_request_data</span>(self, ...):
        data = <span class="kw">super</span>().<span class="fn">build_request_data</span>(...)     <span class="cm"># 先拿 OpenAI 形状的请求</span>
        <span class="kw">if</span> <span class="st">"grok-3-mini-"</span> <span class="kw">in</span> model:           <span class="cm"># 只关这家的怪癖</span>
            data.<span class="fn">pop</span>(<span class="st">"presence_penalty"</span>, <span class="kw">None</span>)
            data.<span class="fn">pop</span>(<span class="st">"frequency_penalty"</span>, <span class="kw">None</span>)
        <span class="kw">return</span> data
</pre></div>
<p>换个子类，套路一模一样，只是改的字段不同：<span class="mono">GroqClient</span> 会把对象形式的 <span class="mono">tool_choice</span>（强制指定某个工具时才会出现）降级成字符串 <span class="mono">"required"</span>，因为 Groq 只认字符串形式。改哪一笔因家而异，但"先 super、再就地改"这条骨架始终不变。</p>
<div class="note tip"><span class="ni">💡</span><span class="nx">共性模式记一句：<strong>怪癖只关在 <span class="mono">build_request_data</span> 与 <span class="mono">convert_response_to_chat_completion</span> 这两处</strong>。<span class="mono">send_llm_request_async</span> 之上的那段循环，无论底下是 xAI 还是 Groq，看到的永远是同一个统一的 <span class="mono">ChatCompletionResponse</span>。</span></div>
<p>反过来想更清楚：要是这些惩罚字段、<span class="mono">tool_choice</span> 之类的特例漏进了循环，循环里就会冒出一片 <span class="mono">if 是不是 xAI</span>、<span class="mono">if 是不是 Groq</span> 的分支——正是上一课反复警告的"抽象漏了"。把它们牢牢关进子类，循环才配得上"干净"二字。</p>
<p>还要留意：怪癖既可能在<strong>出门时</strong>改（<span class="mono">build_request_data</span> 动请求），也可能在<strong>回来时</strong>改（<span class="mono">convert_response_to_chat_completion</span> 动响应）。前者管"我们怎么问"，后者管"它的回答被翻译成什么"，两头各守一道关口。</p>
<h2>核心怪招：把内心独白塞成工具参数</h2>
<p>现在拆本课最精彩的一招。很多模型只会"调函数"，并不会先吐一段思考。Letta 偏要它们<strong>先想后调</strong>——办法是把一个叫 <span class="mono">thinking</span> 的字符串，硬塞成每个工具的<strong>第一个参数</strong>。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>注入</h4><p><span class="mono">add_inner_thoughts_to_functions</span> 把 <span class="mono">thinking</span> 加成每个工具的第一个 property，并排进 <span class="mono">required</span> 的最前面。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>生成</h4><p>模型按 schema 顺序填参数，于是<strong>先写 thinking</strong>、再写真正的业务参数——思考被"逼"在了动作之前。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>拆回</h4><p>响应里 <span class="mono">unpack_inner_thoughts_from_kwargs</span> 把 <span class="mono">thinking</span> 从工具参数里 pop 出来，塞进 <span class="mono">message.content</span>。</p></div></div>
</div>
<p>于是一个"只会调函数"的模型，被硬生生挤出了一条思维链：思考成了参数的一部分，模型不得不先写出来。等响应回来，这段思考又被抽回助手消息正文——对下游而言，就跟模型"本来就会想"一模一样。</p>
<p>这里有个容易忽略的妙处：<strong>这段思考对模型自己也有用</strong>。被逼着先写一遍推理，等于给后面的参数选择做了铺垫——很多时候，模型正是借这一步把"该调哪个工具、传什么参数"想清楚的。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/helpers.py</span><span class="ln">把内心独白排成第一个参数（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">add_inner_thoughts_to_functions</span>(functions, inner_thoughts_key, ..., put_inner_thoughts_first=<span class="kw">True</span>):
    <span class="kw">for</span> f <span class="kw">in</span> functions:
        new_props = OrderedDict()
        <span class="kw">if</span> put_inner_thoughts_first:
            new_props[inner_thoughts_key] = {<span class="st">"type"</span>: <span class="st">"string"</span>, ...}   <span class="cm"># thinking 放第一个</span>
            new_props.<span class="fn">update</span>(f[<span class="st">"parameters"</span>][<span class="st">"properties"</span>])
            f[<span class="st">"parameters"</span>][<span class="st">"required"</span>].<span class="fn">insert</span>(<span class="nb">0</span>, inner_thoughts_key)   <span class="cm"># required 也排最前</span>
</pre></div>
<p>举个具体例子：注入之后，<span class="mono">send_message</span> 这个工具的参数顺序会变成 <span class="mono">thinking</span> 在前、<span class="mono">message</span> 在后。模型想调用它，就<strong>必须先生成一段 thinking 文本</strong>，再生成真正要发出的消息——这一步怎么都跳不过去。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">键名 <span class="mono">INNER_THOUGHTS_KWARG = "thinking"</span> 定义在 <span class="mono">letta/settings.py</span>（<strong>不在</strong> <span class="mono">constants.py</span>，那里放的是描述文字）。反向拆解走 <span class="mono">helpers.py::unpack_inner_thoughts_from_kwargs</span>：从 tool_call 的参数里 <span class="mono">pop</span> 出 <span class="mono">thinking</span>，再塞回 <span class="mono">message.content</span>。</span></div>
<p>这一招的精髓，是<strong>用结构去逼出行为</strong>：不是恳求模型"请先想一想"，而是把"想"做成它绕不开的第一个必填字段。结构一立，思考就成了刚需，而不再依赖模型的自觉。</p>
<p>还有个收尾动作别忘了：拆回 thinking 之后，工具调用的参数里就<strong>不该再留</strong>这个字段，否则真正执行工具时会凭空多出一个它不认识的参数。<span class="mono">unpack</span> 既是"取出思考"，也是"清理现场"。</p>
<div class="cute"><div class="row"><span class="emoji">🎭🎭🎭</span><span class="lab">三张面具</span><span class="arrow">→</span><span class="emoji">🙂</span><span class="bubble">同一张脸</span></div><div class="cap">同一个 OpenAIClient，只换 base_url / 几个字段，就服务一堆供应商</div></div>
<p>这张萌图想说的就一句：复用不是偷懒，而是把"相同的部分"真正只写一遍。图里画的是 OpenAI 那张脸；整座动物园里这样的脸也只有三张（三个家族基类），面具却能挂一大把——多接一家，多戴一张面具即可。</p>
<h2>开关：模拟推理 vs 原生推理</h2>
<p>注入这招并不是对所有模型都开。有的模型本来就会推理，再塞一个假的 <span class="mono">thinking</span> 反而画蛇添足。于是 <span class="mono">LLMConfig.put_inner_thoughts_in_kwargs</span> 这个开关会<strong>自动翻转</strong>。</p>
<div class="cellgroup"><div class="cg-cap"><b>put_inner_thoughts_in_kwargs 怎么翻转</b></div><div class="cells"><span class="cell hl">原生推理 (o1/gpt-5/Claude-4) → False</span><span class="sep">·</span><span class="cell">普通工具调用 → True（模拟一个）</span></div></div>
<p>翻转规则其实就一句话：<strong>模型自带推理就关、只会调函数就开</strong>。两边并排看更清楚。</p>
<div class="cols">
  <div class="col"><h4>🧠 原生推理 → 关</h4><p>o1 / o3 / gpt-5、Claude 3.7/4、ZAI GLM 这类自带推理的模型，<span class="mono">=False</span>：直接用它们真正的 thinking，不必再注入假参数。</p></div>
  <div class="col"><h4>🎭 普通工具调用 → 开</h4><p>只会调函数、不会先思考的模型，<span class="mono">=True</span>：注入一个 <span class="mono">thinking</span> 参数，给它模拟出一段思维链。</p></div>
</div>
<div class="note tip"><span class="ni">💡</span><span class="nx">为什么非要排<strong>第一个</strong>？因为参数是按顺序生成的——把 <span class="mono">thinking</span> 放最前，等于强迫模型"<strong>先写一段推理，再填结构化参数</strong>"。顺序一换，先想后调这件事就落了空。</span></div>
<p>这种"自动翻转"，是抽象优雅的又一处体现：同一段注入代码，既照顾了只会调函数的小模型，也不去打扰自带推理的大模型，区别仅在一个布尔值。你几乎不用操心它，Letta 会按模型替你拨好。</p>
<h2>Anthropic 三大怪癖</h2>
<p>Anthropic 是少数没法靠 <span class="mono">OpenAIClient</span> 糊弄过去的家族，它有三样很扎眼的怪癖，全被关在 <span class="mono">AnthropicClient</span> 里。先用一张表把它们摆开。</p>
<table class="t">
<tr><th>怪癖</th><th>做法</th><th>作用 / 注意</th></tr>
<tr><td class="mono">cache_control</td><td>给最后一个 tool、system 末块、messages 末消息末块各盖一个 <span class="mono">{"type":"ephemeral"}</span></td><td>增量提示缓存：重复前缀命中就省钱省延迟</td></tr>
<tr><td class="mono">extended thinking</td><td><span class="mono">data["thinking"]={"type":"enabled","budget_tokens":…}</span> 或 adaptive</td><td>开 thinking 时必须 <span class="mono">temperature=1.0</span></td></tr>
<tr><td class="mono">batch</td><td><span class="mono">send_llm_batch_request_async → client.beta.messages.batches.create</span></td><td>唯一覆盖基类批量方法的 client，其余仍抛 NotImplementedError</td></tr>
<tr><td>内容块<br><small>（响应翻译）</small></td><td>响应里的 <span class="mono">text / tool_use / thinking</span> 三类块</td><td>转成 OpenAI 的 <span class="mono">tool_calls</span> / <span class="mono">reasoning_content</span> 形状</td></tr>
</table>
<p>三样里 <span class="mono">batch</span> 尤其特别：基类把批量方法留成一个 <span class="mono">NotImplementedError</span>，只有 <span class="mono">AnthropicClient</span> 真接了线。而 <span class="mono">cache_control</span> 是 Anthropic 计费模型独有的优化——把稳定不变的前缀标成可缓存，下次命中就不再重复计费。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/anthropic_client.py</span><span class="ln">cache_control 与 extended thinking（简化）</span></div>
<pre><span class="cm"># 提示缓存：给最后一个 tool 盖个 ephemeral 戳，命中就省钱省延迟</span>
data[<span class="st">"tools"</span>][-<span class="nb">1</span>][<span class="st">"cache_control"</span>] = {<span class="st">"type"</span>: <span class="st">"ephemeral"</span>}
<span class="cm"># 扩展思考：开 thinking 时温度必须为 1</span>
data[<span class="st">"thinking"</span>] = {<span class="st">"type"</span>: <span class="st">"enabled"</span>, <span class="st">"budget_tokens"</span>: budget}
data[<span class="st">"temperature"</span>] = <span class="nb">1.0</span>
</pre></div>
<p>响应方向也得翻译回去：Anthropic 把内容拆成 <span class="mono">text</span> / <span class="mono">tool_use</span> / <span class="mono">thinking</span> 三类块，<span class="mono">convert</span> 再把它们拼回 OpenAI 的 <span class="mono">tool_calls</span> 与 <span class="mono">reasoning_content</span>。出门改一次、回来改一次，恰好对称。</p>
<p>这也是为什么 Anthropic 值得单开一节：别家大多只改请求里的零星字段，它却在请求与响应<strong>两端</strong>都动了真格——缓存标记、思考预算、批量接口、内容块翻译，样样都要 client 亲自接管。</p>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>上一课那纸契约，<strong>红利正是在这一课兑现</strong>的。每家 provider 的"怪脾气"都被隔离进两个方法——<span class="mono">build</span> 改请求、<span class="mono">convert</span> 改响应，循环之上一无所知。</p>
<p>最妙的怪癖是"把内心独白塞成工具参数"：对没有原生推理的模型，Letta 强制每次工具调用都把一个 <span class="mono">thinking</span> 字符串排成<strong>第一个参数</strong>，于是模型"先想后调"，再在响应里把它抽回助手消息——硬是从一个"只会调函数"的模型里挤出了思维链。</p>
<p>而 <span class="mono">put_inner_thoughts_in_kwargs</span> 会<strong>自动翻转</strong>：原生推理模型（o1/gpt-5/Claude-4）→ 关，用它们真的 thinking；普通工具调用模型 → 开，模拟一个。同一个抽象，对两类模型给出恰好相反的处理。</p>
<p>同一招 MemGPT 内心独白，就这样在一整座 provider 动物园里活了下来。而第 23 课的本地路径，还会用<strong>语法约束</strong>把它再实现一遍——那是后话。</p>
<p>往大里看，这是"适配器模式"最划算的一种用法：把易变的部分（各家怪癖）锁进子类窄窄的两个方法，把不变的部分（执行循环）彻底解放。改动的半径，被牢牢摁在 client 内部，外面的世界毫不知情。</p>
<p>说到底，这一课讲的不是某一家的奇技淫巧，而是<strong>"差异该放在哪"这件事的纪律</strong>：放进子类，系统就稳；漏进循环，系统就乱。每一处怪癖，都是对这条纪律的一次小小检验。</p>
</div>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">llm_api/openai_client.py::OpenAIClient</span>——<span class="mono">_prepare_client_kwargs</span> 把 <span class="mono">base_url</span> 设成 endpoint；外加 8 个子类（Azure/Baseten/Deepseek/Fireworks/Groq/Together/XAI/ZAI）。</p>
<p><span class="mono">llm_api/anthropic_client.py::AnthropicClient</span>——cache_control / extended thinking / batch；它自身又是 <span class="mono">BedrockClient</span> / <span class="mono">MiniMaxClient</span> 的基类。</p>
<p><span class="mono">llm_api/helpers.py::add_inner_thoughts_to_functions</span> 与 <span class="mono">unpack_inner_thoughts_from_kwargs</span>——注入与拆回内心独白。</p>
<p><span class="mono">settings.py::INNER_THOUGHTS_KWARG</span> 是键名 <span class="mono">"thinking"</span>；<span class="mono">llm_api/google_vertex_client.py</span> 则把 thinking 追加在<strong>最后</strong>。</p>
</div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>注入函数叫 <span class="mono">add_inner_thoughts_to_functions</span>（复数 functions），<strong>不是</strong> <span class="mono">add_inner_thoughts_to_function_call</span>。</p>
<p>键名 <span class="mono">INNER_THOUGHTS_KWARG="thinking"</span> 在 <span class="mono">settings.py</span>，<strong>不在</strong> <span class="mono">constants.py</span>（那儿只放描述文字）。</p>
<p><strong>Google 是反例</strong>：它把 <span class="mono">thinking</span> 追加在<strong>最后</strong>，不是最前——别想当然以为各家都排第一。</p>
<p><span class="mono">AnthropicClient</span> 自己<strong>也是</strong>复用基类（Bedrock/MiniMax 继承它）；而 <span class="mono">OpenAIClient</span> 的显式子类是 <strong>8 个</strong>，不是 12。</p>
</div>
<h2>再挖深一点</h2>
<p>主线到这里就完整了。下面四个抽屉，专门收那些你大概率会追问的细节——按兴趣展开即可，不展开也不影响对主线的理解。</p>
<details class="accordion"><summary>内心独白为什么要排第一？又怎么 unpack 回 content？</summary><div class="acc-body">
<p>排第一是为了"先想后调"。LLM 生成参数是<strong>从左到右、按顺序</strong>来的；把 <span class="mono">thinking</span> 放在第一个，模型就必须先吐一段推理，才轮到填真正的业务参数。等于用参数顺序，把"思考在动作之前"这件事钉死。</p>
<p>注入由 <span class="mono">add_inner_thoughts_to_functions</span> 完成：它用 <span class="mono">OrderedDict</span> 把 <span class="mono">thinking</span> 塞成第一个 property，又 <span class="mono">required.insert(0, key)</span> 让它在必填项里也排最前。两手一起，模型躲不掉。</p>
<p>拆回则走 <span class="mono">unpack_inner_thoughts_from_kwargs</span>：响应回来后，把 <span class="mono">thinking</span> 从工具调用参数里 <span class="mono">pop</span> 出来，写进 <span class="mono">message.content</span>。于是下游看到的，是一个普通的"先有思考、再有工具调用"的助手消息。</p>
<p>这也回答了一个常见疑问：为什么不让模型在普通文本里思考就好？因为工具调用模型的输出<strong>已经被约束成 JSON 参数</strong>，自由发挥的文本无处安放；把思考做成一个参数字段，是在这种约束下挤出思维链的唯一干净办法。</p>
</div></details>
<details class="accordion"><summary>put_inner_thoughts_in_kwargs：到底谁关谁开？</summary><div class="acc-body">
<p>这个开关回答一个问题：<strong>这模型需不需要我替它造一段思考？</strong>需要就开（<span class="mono">=True</span>，模拟），不需要就关（<span class="mono">=False</span>，用原生）。</p>
<p>自带推理的会被关掉：Anthropic 3.7/4、OpenAI 的 o1/o3/gpt-5、ZAI 的 GLM 等。它们本就会产出真正的 reasoning，再注入一个假 <span class="mono">thinking</span> 纯属添乱。</p>
<p>普通工具调用模型则打开，由 Letta 注入一段模拟的内心独白。一个开关，把"两类截然不同的模型"收进了同一套代码路径。</p>
<p>顺带一提：这个开关通常由模型句柄或默认配置替你决定，不用手工去拨。Letta 心里清楚哪些 provider 自带推理、哪些不会，于是预先把 <span class="mono">put_inner_thoughts_in_kwargs</span> 设成合适的值。</p>
<p>记住这个对应就不会乱：<strong>开 = 模拟</strong>（注入假 thinking），<strong>关 = 原生</strong>（用真 reasoning）。名字里的 "in_kwargs" 说的正是"把内心独白放进工具参数里"——为真才需要注入。</p>
</div></details>
<details class="accordion"><summary>Anthropic 的三处 cache_control + thinking + batch</summary><div class="acc-body">
<p><span class="mono">cache_control</span> 一共贴三处：最后一个 tool、system 的末块、messages 里末条消息的末块。被标 <span class="mono">{"type":"ephemeral"}</span> 的前缀可被缓存，重复请求命中就省钱省延迟。</p>
<p>extended thinking 打开时，<span class="mono">data["thinking"]</span> 被设成 enabled（带 <span class="mono">budget_tokens</span>）或 adaptive，且<strong>温度被强制为 1</strong>；需要时还会按需拼 beta 头。</p>
<p>batch 是唯一真接线的：基类的批量方法留成 <span class="mono">NotImplementedError</span>，只有 <span class="mono">AnthropicClient</span> 用 <span class="mono">client.beta.messages.batches.create</span> 实现了它。响应侧再把 text/tool_use/thinking 三类块翻成 OpenAI 形状。</p>
<p>这三处位置也不是随便挑的：它们都落在请求里<strong>最稳定、最值得缓存</strong>的前缀上——工具定义、系统提示、历史消息。越靠前越不变的内容，缓存命中带来的省钱省延迟就越可观。</p>
<p>顺便说一句 beta 头：开启 adaptive thinking、interleaved thinking 或 1M 上下文这些较新能力时，<span class="mono">AnthropicClient</span> 会按需把对应的 beta 标识拼进请求头——这也是它远比"换个 base_url"复杂的原因之一。</p>
</div></details>
<details class="accordion"><summary>Google 的反例：处处跟 OpenAI 形状对着干</summary><div class="acc-body">
<p>最该记的一点：Google 把内心独白 <span class="mono">thinking</span> <strong>追加在最后</strong>（<span class="mono">INNER_THOUGHTS_KWARG_VERTEX</span>），而不是像别家那样排第一。</p>
<p>字段名也另起一套：工具被包成 <span class="mono">[{"functionDeclarations":[...]}]</span>，模型的工具调用叫 <span class="mono">functionCall</span>（带 <span class="mono">.name</span> / <span class="mono">.args</span>），转换时映射成 OpenAI 的 <span class="mono">tool_calls</span>。</p>
<p>连角色名都不同：Google 用 <span class="mono">"model"</span> 表示助手，<span class="mono">convert</span> 时要把它改写成 <span class="mono">"assistant"</span>。这些差异全被关在 <span class="mono">GoogleVertexClient</span> 里，循环照旧无感。</p>
<p>把 Google 拎出来当反例，是想提醒一件事：<strong>"内心独白排第一"并非铁律</strong>，而是 Letta 面向大多数 provider 的默认做法。真要写一个新 client，第一件事就是去确认它究竟把 thinking 放在哪儿。</p>
</div></details>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li>子类一般只重写 <span class="mono">build_request_data</span> + <span class="mono">convert_response_to_chat_completion</span> 两个方法，常 <span class="mono">super()</span> 后改 dict。</li>
<li><span class="mono">OpenAIClient</span> 一个类服务多家：8 个显式子类 + 默认 case，靠换 <span class="mono">base_url</span>。</li>
<li>内心独白被注入成工具的<strong>第一个参数</strong> <span class="mono">thinking</span>，响应时 <span class="mono">unpack</span> 回 <span class="mono">message.content</span>。</li>
<li><span class="mono">put_inner_thoughts_in_kwargs</span> 决定<strong>模拟还是用原生推理</strong>：自带推理→关，普通工具调用→开。</li>
<li>Anthropic 三大怪癖：<span class="mono">cache_control</span> 提示缓存、extended thinking、batch。</li>
<li>Google 是反例：把 <span class="mono">thinking</span> 追加在<strong>最后</strong>，不是最前。</li>
</ul>
</div>
<p><strong>小结一下：</strong>云端 provider 的怪癖，就这样被一一关进子类的那两个方法里。可要是来一个<strong>连原生 function calling 都没有</strong>的本地模型呢？它又怎么被"教会"调工具？下一课，第 23 课，讲本地模型与 <span class="mono">GBNF</span> 受限解码——看 Letta 怎么用语法把"可解析"从概率变成保证。</p>
<p>带着这一课的两条直觉往下走会更顺：<strong>差异关进子类、思考可以被构造</strong>。下一课你会看到，当模型连"调工具"都不会时，Letta 是怎么用一套语法把它从头教起的。</p>

""", "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Last lesson we drew the "unified contract" on paper: one factory picks a client by type, and three methods collapse every difference into the OpenAI shape. But a smooth page doesn't mean calm waters underneath — <strong>each LLM has a very different temperament</strong>: Anthropic wants you to stamp on <span class="mono">cache_control</span> cache markers, Google reinvents even the field names, and some models simply have no native reasoning at all.</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">What this lesson answers is exactly this: how these motley quirks get locked away, one by one, into their own client subclasses — locked above the execution loop from Lessons 13–16, which knows nothing about them and never needs to. This is the lesson where the unified contract truly starts to <strong>pay its dividend</strong>.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">"Pay its dividend" is no exaggeration: the unified shape we worked so hard to erect last lesson only proves its worth here — precisely because it has our back, each provider's quirks have somewhere to hide, instead of being smeared across the loop where they'd be an eyesore.</span></div>
<div class="card analogy"><div class="tag">🔌 Real-life analogy</div>
<p>Picture an actor, <strong>one face</strong>, stepping on stage in a different mask for each show. That face is last lesson's <span class="mono">OpenAIClient</span>; the masks, one per provider, are the subclasses.</p>
<p>The beauty is: <strong>swapping the mask doesn't swap the face</strong>. Most subclasses only tweak one spot on the mask — usually just a new <span class="mono">base_url</span>, at most dropping or adding a field or two along the way.</p>
<p>So the same face, wearing Groq's mask, plays Groq; wearing xAI's mask, plays xAI. The loop in the audience only ever sees "that actor" — which mask he wears tonight, the loop never cares.</p>
<p>This analogy hides the lesson's thesis: <strong>quirks shouldn't be scattered all over the loop, but tucked into their own masks</strong> — that is, into the subclass's two overridden methods.</p>
<p>The mask metaphor goes one step further: the thinner the mask the better — the less a subclass writes, the more thoroughly it reuses, and the fewer "special cases" need separate upkeep. Most of Letta's subclasses are just a few lines, for exactly this reason.</p>
</div>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Grab the lesson in one line: <strong>quirks hide in only two methods, and above the loop it's always the same shape</strong>.</p>
<p>First see how ruthless the reuse is: a single <span class="mono">OpenAIClient</span> class is shared by <strong>8 explicit subclasses</strong> plus the default <span class="mono">case _</span>, and the trick is just swapping one <span class="mono">base_url</span> — the same OpenAI SDK, pointed at a different URL, connects to a different provider.</p>
<p>Then see where the quirks are caged: a subclass <strong>overrides only two methods</strong> — <span class="mono">build_request_data</span> (edit the request on the way out) and <span class="mono">convert_response_to_chat_completion</span> (edit the response on the way back), often calling <span class="mono">super()</span> for the OpenAI shape, then patching a few lines in place.</p>
<p>The lesson's slickest stunt is jamming the inner monologue in as a tool's <strong>first parameter</strong> <span class="mono">thinking</span>, then <span class="mono">unpack</span>-ing it back into the message body on the response; plus Anthropic's exclusive cache / thinking / batch trio. These are what we'll pry open one by one below.</p>
<p>Remember the four as a chain: <strong>reuse kills duplication, two methods cage the differences, the inner monologue supplies the thinking, and a switch toggles simulated vs native</strong>. The next three sections walk this chain, and we close on Anthropic, the family densest with quirks.</p>
<p>This chain is also a "<strong>line of abstraction defense</strong>": every layer inward, the outer code worries about one less thing. The loop needn't understand providers, and the memory / tools / compaction modules even less — they all deal only with the unified shape.</p>
</div>
<h2>OpenAIClient: One Class Serves Many</h2>
<p>Start with the laziest route — a great many providers need no new client at all; they reuse <span class="mono">OpenAIClient</span> directly. Draw out the whole inheritance tree and the three families jump into view.</p>
<p>Before the diagram, agree on one mental model: think of each client as "the base class sets the skeleton, the subclass fills the details". The skeleton (the three-method contract) is written once in each of the three family bases; subclasses take it as-is, overriding one or two methods at most.</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">Abstract base</span><span class="name">LLMClientBase</span></div>
    <div class="ld">Defines the three-method contract (last lesson). All three families below derive from it, each implementing its own "edit request on the way out, edit response on the way back".</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">OpenAI family</span><span class="name">OpenAIClient ← 8 subclasses</span></div>
    <div class="ld">Azure / Baseten / Deepseek / Fireworks / Groq / Together / XAI / ZAI all inherit it; <span class="mono">openrouter</span> and the default <span class="mono">case _</span> simply reuse it as-is.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Anthropic family</span><span class="name">AnthropicClient ← Bedrock / MiniMax</span></div>
    <div class="ld">It is <strong>also</strong> a reuse base: <span class="mono">BedrockClient</span> and <span class="mono">MiniMaxClient</span> inherit it, then each patch their own quirks.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">Google family</span><span class="name">GoogleVertexClient ← GoogleAIClient</span></div>
    <div class="ld"><span class="mono">GoogleAIClient</span> inherits <span class="mono">GoogleVertexClient</span>; field names, role names, and where the inner monologue goes are all a different set.</div></div>
</div>
<p>The tree makes it obvious: only the three family bases are truly "written from scratch"; everything else is a thin subclass standing on their shoulders. The OpenAI family is especially extreme — one base with 8 subclasses behind it, also catching every unnamed provider.</p>
<div class="cellgroup"><div class="cg-cap"><b>OpenAIClient's 8 explicit subclasses</b></div><div class="cells"><span class="cell hl">AzureClient</span><span class="sep">·</span><span class="cell">BasetenClient</span><span class="sep">·</span><span class="cell">DeepseekClient</span><span class="sep">·</span><span class="cell">FireworksClient</span><span class="sep">·</span><span class="cell">GroqClient</span><span class="sep">·</span><span class="cell">TogetherClient</span><span class="sep">·</span><span class="cell">XAIClient</span><span class="sep">·</span><span class="cell">ZAIClient</span></div></div>
<div class="note info"><span class="ni">💡</span><span class="nx">The trick to one class serving many: <span class="mono">OpenAIClient._prepare_client_kwargs</span> only sets <span class="mono">base_url</span> to <span class="mono">llm_config.model_endpoint</span> — the same OpenAI SDK, a new URL, a new provider connected. Roughly <strong>19/25</strong> of <span class="mono">ProviderType</span> end up at <span class="mono">OpenAIClient</span> or a subclass; only 6 don't (anthropic / bedrock / chatgpt_oauth / google_ai / google_vertex / minimax).</span></div>
<p>Why is "just swap one <span class="mono">base_url</span>" enough? Because most of these providers expose an <strong>OpenAI-compatible</strong> interface directly: the request and response shapes already line up with OpenAI, and the only real difference is the server address. Letta seizes on this and sweeps them all into the default arm, sparing even a subclass.</p>
<p>The ones that need their own subclass are usually those "OpenAI-compatible but not quite there" — some model rejects some parameter, or demands one extra field. Only then does a subclass step in: after <span class="mono">super()</span>, supply the missing piece, no need to start over from scratch.</p>
<h2>Subclasses Change Only Two Methods</h2>
<p>So what's actually inside those 8 subclasses? The answer is surprisingly short: <strong>most touch only two methods</strong>. The <span class="mono">XAIClient</span> below is typical — call <span class="mono">super()</span> for the standard OpenAI request, then, only for one of its own models, delete two penalty fields.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/xai_client.py</span><span class="ln">a subclass changes fields only after super() (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">XAIClient</span>(OpenAIClient):
    <span class="kw">def</span> <span class="fn">build_request_data</span>(self, ...):
        data = <span class="kw">super</span>().<span class="fn">build_request_data</span>(...)     <span class="cm"># grab the OpenAI-shaped request first</span>
        <span class="kw">if</span> <span class="st">"grok-3-mini-"</span> <span class="kw">in</span> model:           <span class="cm"># only this provider's quirk</span>
            data.<span class="fn">pop</span>(<span class="st">"presence_penalty"</span>, <span class="kw">None</span>)
            data.<span class="fn">pop</span>(<span class="st">"frequency_penalty"</span>, <span class="kw">None</span>)
        <span class="kw">return</span> data
</pre></div>
<p>Switch subclasses and the pattern is identical, only the edited field differs: <span class="mono">GroqClient</span> down-converts an object-form <span class="mono">tool_choice</span> (which only appears when a specific tool is force-called) into the string <span class="mono">"required"</span>, since Groq accepts only string values. Which line gets edited varies by provider, but the "super first, then patch in place" skeleton never changes.</p>
<div class="note tip"><span class="ni">💡</span><span class="nx">The shared pattern in one line: <strong>quirks are caged in only two places, <span class="mono">build_request_data</span> and <span class="mono">convert_response_to_chat_completion</span></strong>. The loop above <span class="mono">send_llm_request_async</span>, whether xAI or Groq sits below, always sees the same unified <span class="mono">ChatCompletionResponse</span>.</span></div>
<p>The reverse is clearer still: if those penalty fields, the <span class="mono">tool_choice</span> special-case and the like leaked into the loop, the loop would sprout a thicket of <span class="mono">if is_xAI</span>, <span class="mono">if is_Groq</span> branches — exactly the "leaked abstraction" last lesson kept warning about. Cage them firmly in the subclass, and only then does the loop deserve the word "clean".</p>
<p>Note too: a quirk can be edited <strong>on the way out</strong> (<span class="mono">build_request_data</span> touches the request) or <strong>on the way back</strong> (<span class="mono">convert_response_to_chat_completion</span> touches the response). The former governs "how we ask", the latter "what its answer gets translated into" — each end guards its own gate.</p>
<h2>The Core Trick: Stuff the Inner Monologue into a Tool Parameter</h2>
<p>Now pry open the lesson's finest move. Many models only "call functions"; they won't spit out a thought first. Letta insists they <strong>think before they act</strong> — by jamming a string named <span class="mono">thinking</span> in as each tool's <strong>first parameter</strong>.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Inject</h4><p><span class="mono">add_inner_thoughts_to_functions</span> adds <span class="mono">thinking</span> as each tool's first property, and slots it to the very front of <span class="mono">required</span>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Generate</h4><p>The model fills parameters in schema order, so it <strong>writes thinking first</strong>, then the real business parameters — thought is "forced" ahead of action.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Unpack</h4><p>In the response, <span class="mono">unpack_inner_thoughts_from_kwargs</span> pops <span class="mono">thinking</span> out of the tool parameters and tucks it into <span class="mono">message.content</span>.</p></div></div>
</div>
<p>So a model that "only calls functions" gets a chain of thought squeezed out of it by force: thinking becomes part of the parameters, and the model has no choice but to write it first. When the response comes back, that thought is drawn back into the assistant message body — to everything downstream, it's exactly as if the model "could think all along".</p>
<p>Here's an easily missed bonus: <strong>this thought is useful to the model itself</strong>. Being forced to write the reasoning out first paves the way for the parameter choices that follow — often it's precisely this step the model uses to think clearly about "which tool to call, with what arguments".</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/helpers.py</span><span class="ln">put the inner monologue as the first parameter (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">add_inner_thoughts_to_functions</span>(functions, inner_thoughts_key, ..., put_inner_thoughts_first=<span class="kw">True</span>):
    <span class="kw">for</span> f <span class="kw">in</span> functions:
        new_props = OrderedDict()
        <span class="kw">if</span> put_inner_thoughts_first:
            new_props[inner_thoughts_key] = {<span class="st">"type"</span>: <span class="st">"string"</span>, ...}   <span class="cm"># thinking goes first</span>
            new_props.<span class="fn">update</span>(f[<span class="st">"parameters"</span>][<span class="st">"properties"</span>])
            f[<span class="st">"parameters"</span>][<span class="st">"required"</span>].<span class="fn">insert</span>(<span class="nb">0</span>, inner_thoughts_key)   <span class="cm"># required first too</span>
</pre></div>
<p>A concrete example: after injection, the <span class="mono">send_message</span> tool's parameter order becomes <span class="mono">thinking</span> first, <span class="mono">message</span> second. To call it, the model <strong>must generate a chunk of thinking text first</strong>, then the message it actually sends — this step simply can't be skipped.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">The key name <span class="mono">INNER_THOUGHTS_KWARG = "thinking"</span> is defined in <span class="mono">letta/settings.py</span> (<strong>not</strong> <span class="mono">constants.py</span>, which holds the description text). The reverse unpacking goes through <span class="mono">helpers.py::unpack_inner_thoughts_from_kwargs</span>: <span class="mono">pop</span> <span class="mono">thinking</span> out of the tool_call's arguments, then tuck it back into <span class="mono">message.content</span>.</span></div>
<p>The essence of this move is <strong>using structure to force behavior</strong>: not begging the model "please think first", but making "thinking" the first required field it can't get around. Once the structure stands, thought becomes a hard requirement, no longer reliant on the model's self-discipline.</p>
<p>Don't forget the closing act: once <span class="mono">thinking</span> is unpacked, that field <strong>shouldn't remain</strong> in the tool-call arguments, or executing the tool for real would carry one stray parameter it doesn't recognize. <span class="mono">unpack</span> is both "extract the thought" and "clean up the scene".</p>
<div class="cute"><div class="row"><span class="emoji">🎭🎭🎭</span><span class="lab">Three masks</span><span class="arrow">→</span><span class="emoji">🙂</span><span class="bubble">One face</span></div><div class="cap">One OpenAIClient, just swapping base_url / a few fields, serves a whole crowd of providers</div></div>
<p>This little cartoon says just one thing: reuse isn't laziness, it's writing the "identical part" truly only once. The cartoon draws the OpenAI face; across the whole zoo there are only three such faces (the three family bases), but masks hang by the bunch — to add one more provider, just wear one more mask.</p>
<h2>The Switch: Simulated vs Native Reasoning</h2>
<p>The injection trick isn't turned on for every model. Some models reason natively already, and stuffing in a fake <span class="mono">thinking</span> only gilds the lily. So the <span class="mono">LLMConfig.put_inner_thoughts_in_kwargs</span> switch <strong>flips automatically</strong>.</p>
<div class="cellgroup"><div class="cg-cap"><b>How put_inner_thoughts_in_kwargs flips</b></div><div class="cells"><span class="cell hl">Native reasoning (o1/gpt-5/Claude-4) → False</span><span class="sep">·</span><span class="cell">Plain tool calling → True (simulate one)</span></div></div>
<p>The flip rule is really one line: <strong>if the model reasons natively, off; if it only calls functions, on</strong>. Side by side it's clearer.</p>
<div class="cols">
  <div class="col"><h4>🧠 Native reasoning → off</h4><p>Models that reason natively — o1 / o3 / gpt-5, Claude 3.7/4, ZAI GLM — get <span class="mono">=False</span>: use their real thinking directly, no fake parameter to inject.</p></div>
  <div class="col"><h4>🎭 Plain tool calling → on</h4><p>Models that only call functions and won't think first get <span class="mono">=True</span>: inject a <span class="mono">thinking</span> parameter to simulate a chain of thought for them.</p></div>
</div>
<div class="note tip"><span class="ni">💡</span><span class="nx">Why insist on <strong>first</strong>? Because parameters are generated in order — putting <span class="mono">thinking</span> at the very front forces the model to "<strong>write a chunk of reasoning, then fill the structured parameters</strong>". Reorder it and "think before acting" comes to nothing.</span></div>
<p>This "auto-flip" is another show of the abstraction's elegance: the same injection code both serves the small models that only call functions and leaves the big models with native reasoning alone — the difference is a single boolean. You hardly have to think about it; Letta sets it for you per model.</p>
<h2>Anthropic's Three Big Quirks</h2>
<p>Anthropic is one of the few families that can't be papered over with <span class="mono">OpenAIClient</span>; it has three glaring quirks, all caged inside <span class="mono">AnthropicClient</span>. Lay them out in a table first.</p>
<table class="t">
<tr><th>Quirk</th><th>How</th><th>Effect / note</th></tr>
<tr><td class="mono">cache_control</td><td>stamp a <span class="mono">{"type":"ephemeral"}</span> on the last tool, the system's last block, and the last block of the last message</td><td>incremental prompt caching: a repeated prefix that hits saves money and latency</td></tr>
<tr><td class="mono">extended thinking</td><td><span class="mono">data["thinking"]={"type":"enabled","budget_tokens":…}</span> or adaptive</td><td>when thinking is on, <span class="mono">temperature=1.0</span> is required</td></tr>
<tr><td class="mono">batch</td><td><span class="mono">send_llm_batch_request_async → client.beta.messages.batches.create</span></td><td>the only client that overrides the base batch method; the rest still raise NotImplementedError</td></tr>
<tr><td>content blocks<br><small>(response translation)</small></td><td>the <span class="mono">text / tool_use / thinking</span> block types in the response</td><td>converted to OpenAI's <span class="mono">tool_calls</span> / <span class="mono">reasoning_content</span> shape</td></tr>
</table>
<p>Of the three, <span class="mono">batch</span> is especially singular: the base class leaves the batch method as a <span class="mono">NotImplementedError</span>, and only <span class="mono">AnthropicClient</span> actually wires it up. And <span class="mono">cache_control</span> is an optimization unique to Anthropic's billing model — mark the stable, unchanging prefix as cacheable, and the next hit isn't billed again.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/llm_api/anthropic_client.py</span><span class="ln">cache_control and extended thinking (simplified)</span></div>
<pre><span class="cm"># Prompt caching: stamp an ephemeral mark on the last tool; a hit saves money and latency</span>
data[<span class="st">"tools"</span>][-<span class="nb">1</span>][<span class="st">"cache_control"</span>] = {<span class="st">"type"</span>: <span class="st">"ephemeral"</span>}
<span class="cm"># Extended thinking: temperature must be 1 when thinking is on</span>
data[<span class="st">"thinking"</span>] = {<span class="st">"type"</span>: <span class="st">"enabled"</span>, <span class="st">"budget_tokens"</span>: budget}
data[<span class="st">"temperature"</span>] = <span class="nb">1.0</span>
</pre></div>
<p>The response direction must translate back too: Anthropic splits content into <span class="mono">text / tool_use / thinking</span> block types, and <span class="mono">convert</span> stitches them back into OpenAI's <span class="mono">tool_calls</span> and <span class="mono">reasoning_content</span>. Edit once on the way out, once on the way back — perfectly symmetric.</p>
<p>This is why Anthropic deserves its own section: most others only edit a stray field or two in the request, while it does real work on <strong>both ends</strong>, request and response — cache markers, thinking budget, batch interface, content-block translation, every one taken over by the client itself.</p>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>Last lesson's paper contract <strong>pays its dividend right here</strong>. Every provider's "odd temperament" is isolated into two methods — <span class="mono">build</span> edits the request, <span class="mono">convert</span> edits the response — and above the loop, nothing knows.</p>
<p>The slickest quirk is "stuff the inner monologue into a tool parameter": for models without native reasoning, Letta forces every tool call to slot a <span class="mono">thinking</span> string as the <strong>first parameter</strong>, so the model "thinks before it acts", then draws it back into the assistant message on the response — squeezing a chain of thought out of a model that "only calls functions".</p>
<p>And <span class="mono">put_inner_thoughts_in_kwargs</span> <strong>flips automatically</strong>: native-reasoning models (o1/gpt-5/Claude-4) → off, use their real thinking; plain tool-calling models → on, simulate one. The same abstraction gives two kinds of model exactly opposite treatment.</p>
<p>The same MemGPT inner-monologue move thus survives across a whole zoo of providers. And Lesson 23's local path will implement it once more with <strong>grammar constraints</strong> — but that's for later.</p>
<p>Zoom out and this is the adapter pattern's most cost-effective use: lock the volatile part (each provider's quirks) into the subclass's two narrow methods, and fully free the invariant part (the execution loop). The radius of change is pinned firmly inside the client, and the outside world has no idea.</p>
<p>In the end, this lesson isn't about any one provider's tricks, but the <strong>discipline of "where differences belong"</strong>: put them in the subclass and the system stays stable; leak them into the loop and the system turns to chaos. Every quirk is a small test of this discipline.</p>
</div>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">llm_api/openai_client.py::OpenAIClient</span> — <span class="mono">_prepare_client_kwargs</span> sets <span class="mono">base_url</span> to the endpoint; plus 8 subclasses (Azure/Baseten/Deepseek/Fireworks/Groq/Together/XAI/ZAI).</p>
<p><span class="mono">llm_api/anthropic_client.py::AnthropicClient</span> — cache_control / extended thinking / batch; it is itself the base of <span class="mono">BedrockClient</span> / <span class="mono">MiniMaxClient</span>.</p>
<p><span class="mono">llm_api/helpers.py::add_inner_thoughts_to_functions</span> and <span class="mono">unpack_inner_thoughts_from_kwargs</span> — inject and unpack the inner monologue.</p>
<p><span class="mono">settings.py::INNER_THOUGHTS_KWARG</span> is the key name <span class="mono">"thinking"</span>; <span class="mono">llm_api/google_vertex_client.py</span> appends thinking <strong>last</strong>.</p>
</div>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<p>The injection function is <span class="mono">add_inner_thoughts_to_functions</span> (plural functions), <strong>not</strong> <span class="mono">add_inner_thoughts_to_function_call</span>.</p>
<p>The key name <span class="mono">INNER_THOUGHTS_KWARG="thinking"</span> is in <span class="mono">settings.py</span>, <strong>not</strong> <span class="mono">constants.py</span> (which holds only description text).</p>
<p><strong>Google is the counterexample</strong>: it appends <span class="mono">thinking</span> <strong>last</strong>, not first — don't assume every provider puts it first.</p>
<p><span class="mono">AnthropicClient</span> is <strong>also</strong> a reuse base (Bedrock/MiniMax inherit it); and <span class="mono">OpenAIClient</span>'s explicit subclasses number <strong>8</strong>, not 12.</p>
</div>
<h2>Dig a Little Deeper</h2>
<p>The main thread is complete here. The four drawers below hold the details you'll most likely ask about — open them by interest; leaving them shut doesn't hurt your grasp of the main thread.</p>
<details class="accordion"><summary>Why must the inner monologue come first? And how is it unpacked back into content?</summary><div class="acc-body">
<p>First is for "think before acting". An LLM generates parameters left to right, in order; put <span class="mono">thinking</span> first and the model must spit out a chunk of reasoning before it gets to fill the real business parameters. It nails "thought before action" using parameter order.</p>
<p>Injection is done by <span class="mono">add_inner_thoughts_to_functions</span>: it uses an <span class="mono">OrderedDict</span> to slot <span class="mono">thinking</span> in as the first property, and <span class="mono">required.insert(0, key)</span> to put it first among the required fields too. With both hands, the model can't dodge.</p>
<p>Unpacking goes through <span class="mono">unpack_inner_thoughts_from_kwargs</span>: once the response is back, <span class="mono">pop</span> <span class="mono">thinking</span> out of the tool-call arguments and write it into <span class="mono">message.content</span>. So what downstream sees is an ordinary "thought first, then tool call" assistant message.</p>
<p>This also answers a common question: why not just let the model think in plain text? Because a tool-calling model's output is <strong>already constrained to JSON parameters</strong>, with nowhere to put free-form text; making thought a parameter field is the only clean way to squeeze a chain of thought out under that constraint.</p>
</div></details>
<details class="accordion"><summary>put_inner_thoughts_in_kwargs: who exactly is off, who's on?</summary><div class="acc-body">
<p>This switch answers one question: <strong>does this model need me to manufacture a thought for it?</strong> If yes, on (<span class="mono">=True</span>, simulate); if no, off (<span class="mono">=False</span>, use native).</p>
<p>Those that reason natively get switched off: Anthropic 3.7/4, OpenAI's o1/o3/gpt-5, ZAI's GLM, and so on. They already produce real reasoning, so injecting a fake <span class="mono">thinking</span> is pure noise.</p>
<p>Plain tool-calling models get switched on, and Letta injects a simulated inner monologue. One switch folds "two utterly different kinds of model" into the same code path.</p>
<p>By the way: this switch is usually decided for you by the model handle or default config, no manual flipping needed. Letta knows which providers reason natively and which don't, so it presets <span class="mono">put_inner_thoughts_in_kwargs</span> to the right value.</p>
<p>Remember this mapping and you won't get muddled: <strong>on = simulate</strong> (inject fake thinking), <strong>off = native</strong> (use real reasoning). The "in_kwargs" in the name says exactly "put the inner monologue into the tool parameters" — true only when injection is needed.</p>
</div></details>
<details class="accordion"><summary>Anthropic's three cache_control spots + thinking + batch</summary><div class="acc-body">
<p><span class="mono">cache_control</span> is stamped in three spots total: the last tool, the system's last block, and the last block of the last message in messages. A prefix marked <span class="mono">{"type":"ephemeral"}</span> can be cached, so a repeated-request hit saves money and latency.</p>
<p>When extended thinking is on, <span class="mono">data["thinking"]</span> is set to enabled (with <span class="mono">budget_tokens</span>) or adaptive, and <strong>temperature is forced to 1</strong>; when needed, a beta header is assembled on demand.</p>
<p>batch is the only one truly wired up: the base class's batch method stays a <span class="mono">NotImplementedError</span>, and only <span class="mono">AnthropicClient</span> implements it with <span class="mono">client.beta.messages.batches.create</span>. The response side then translates the text/tool_use/thinking block types into the OpenAI shape.</p>
<p>These three spots aren't picked at random: they all land on the request's <strong>most stable, most cache-worthy</strong> prefix — tool definitions, the system prompt, history messages. The further forward and more unchanging the content, the more sizable the money and latency saved on a cache hit.</p>
<p>A word on the beta header: when enabling newer capabilities like adaptive thinking, interleaved thinking, or 1M context, <span class="mono">AnthropicClient</span> assembles the matching beta identifier into the request header on demand — one of the reasons it's far more complex than "swap a base_url".</p>
</div></details>
<details class="accordion"><summary>Google, the counterexample: working against the OpenAI shape at every turn</summary><div class="acc-body">
<p>The one thing most worth remembering: Google <strong>appends</strong> the inner monologue <span class="mono">thinking</span> <strong>last</strong> (<span class="mono">INNER_THOUGHTS_KWARG_VERTEX</span>), not first like the others.</p>
<p>The field names are a different set too: tools are wrapped as <span class="mono">[{"functionDeclarations":[...]}]</span>, the model's tool call is called <span class="mono">functionCall</span> (with <span class="mono">.name</span> / <span class="mono">.args</span>), mapped to OpenAI's <span class="mono">tool_calls</span> on conversion.</p>
<p>Even the role names differ: Google uses <span class="mono">"model"</span> for the assistant, and <span class="mono">convert</span> must rewrite it to <span class="mono">"assistant"</span>. All these differences are caged in <span class="mono">GoogleVertexClient</span>, and the loop feels nothing as usual.</p>
<p>Holding Google up as a counterexample is meant to remind you of one thing: <strong>"inner monologue first" is no iron law</strong>, but Letta's default for most providers. To write a new client for real, the first thing to do is confirm exactly where it puts thinking.</p>
</div></details>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li>A subclass usually overrides only two methods, <span class="mono">build_request_data</span> + <span class="mono">convert_response_to_chat_completion</span>, often patching the dict after <span class="mono">super()</span>.</li>
<li><span class="mono">OpenAIClient</span> serves many as one class: 8 explicit subclasses + the default case, by swapping <span class="mono">base_url</span>.</li>
<li>The inner monologue is injected as a tool's <strong>first parameter</strong> <span class="mono">thinking</span>, and <span class="mono">unpack</span>-ed back into <span class="mono">message.content</span> on the response.</li>
<li><span class="mono">put_inner_thoughts_in_kwargs</span> decides <strong>simulated vs native reasoning</strong>: native → off, plain tool calling → on.</li>
<li>Anthropic's three big quirks: <span class="mono">cache_control</span> prompt caching, extended thinking, batch.</li>
<li>Google is the counterexample: it appends <span class="mono">thinking</span> <strong>last</strong>, not first.</li>
</ul>
</div>
<p><strong>To sum up:</strong> a cloud provider's quirks get caged, one by one, into those two methods of a subclass. But what about a local model that lacks even native function calling? How does it get "taught" to call tools? The next lesson, Lesson 23, covers local models and <span class="mono">GBNF</span> constrained decoding — see how Letta uses grammar to turn "parseable" from a probability into a guarantee.</p>
<p>Carrying this lesson's two intuitions forward makes the next one smoother: <strong>differences cage into subclasses, and thinking can be constructed</strong>. Next lesson you'll see, when a model can't even "call a tool", how Letta teaches it from scratch with a grammar.</p>

"""}

LESSON_23 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第六部分走到收尾。前两课我们先立好了统一契约（第 21 课），又把各家云厂商的怪癖一个个关进子类（第 22 课）。可还剩一种最硬的情况没碰：一个连<strong>原生 function calling 都没有</strong>的本地模型，它只会"续写文本"，你要怎么让它去调一个工具？</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课就来还原 MemGPT 时代那个经典戏法：先把工具的 schema 当成文本塞进提示，再用一套 <span class="mono">GBNF</span> 语法去<strong>约束解码器本身</strong>，让模型采样时压根吐不出非法 token、只能吐出合法 JSON。先打个预防针——这是一条 legacy 老路径。</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><strong>这是 legacy 路径</strong>：现代本地后端（ollama/vllm/lmstudio）走第 21 课的 OpenAI 兼容 <span class="mono">OpenAIClient</span>；GBNF 受限解码只在旧 <span class="mono">Agent</span> 兜底路径、且仅 <span class="mono">llamacpp/koboldcpp/webui</span> 生效。讲的是"它怎么 work、为什么经典"，不是"现在默认这么跑"。</span></div>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>给只会续写的模型，用语法逼出可解析的 JSON</strong>。</p>
<p>先把话说在前头——这是一条<strong>历史 / 次要路径</strong>。现代本地后端（ollama / vllm / lmstudio）早就提供"OpenAI 兼容"端点，走的是第 21 课那个默认 <span class="mono">case _ → OpenAIClient</span>，根本没有专属 client。</p>
<p>GBNF 这条路只在<strong>兜底</strong>时才被走到：旧的 <span class="mono">agent.py::Agent</span> 在 <span class="mono">LLMClient.create</span> 之后，经 <span class="mono">llm_api_tools.py::create</span> 的 <span class="mono">else</span>（本地）分支，调到 <span class="mono">chat_completion_proxy.py::get_chat_completion</span>。</p>
<p>它的流程是一条链：选 wrapper →（名字带 <span class="mono">grammar</span> 才）动态生成 GBNF → wrapper 把函数 schema 塞进<strong>提示文本</strong> → 调"裸 completion"后端 → 把文本<strong>解析回</strong> <span class="mono">{function, params}</span> → 心跳补正。</p>
<p>记住一句话：<strong>schema 进提示，语法管采样，文本再解析回结构</strong>。这三步就是本课要逐环拆开的全部，也是这条老路的全部秘密。</p>
</div>
<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>把"给只会续写的模型加上 function calling"想象成这样：你面前是一个<strong>只会接话的小孩</strong>，你递一句，他就顺着往下写一句，他压根不懂什么叫"调用工具"。</p>
<p>第一招很直白：把工具长什么样、有哪些参数，<strong>写成说明书直接抄进题面</strong>，再叮嘱一句"请照这个格式输出 JSON"。这就是 wrapper 把 schema 塞进提示。</p>
<p>可光靠叮嘱不保险——他可能写跑题、JSON 还少个括号。于是有了第二招，也是真正的妙手：给他一张<strong>镂空钢板</strong>盖在纸上，笔只能落进挖空的格子里，<strong>物理上写不出</strong>格子外的字。</p>
<p>这张钢板，就是 <span class="mono">GBNF</span> 语法。它不"劝"模型守格式，而是直接卡住采样：每一步只允许语法合法的 token，于是落笔必然成形。</p>
<p>记住这两招的分工：第一招让模型"知道"该填什么，第二招让它"只能"填对——一软一硬。缺了第二招，第一招就只剩一句温柔的祈祷。</p>
</div>
<p>所以本课其实就讲三件环环相扣的事：<strong>schema 怎么进提示</strong>、<strong>GBNF 怎么卡住采样</strong>、<strong>文本又怎么被解析回结构</strong>。下面逐个拆开，但先回答一个最该问的问题。</p>
<p>多说一句来历：早期 MemGPT 面对的正是一批没有工具 API 的开源模型，这套"提示 + 语法"的打法就是那时逼出来的。今天读它，更像在读一段"function calling 还没标准化"的历史切片。</p>
<h2>为什么光把 schema 写进提示还不够</h2>
<p>把"只靠提示叮嘱"和"提示再加语法卡死"两个世界并排摆出来，最能看清 GBNF 的价值到底在哪。</p>
<div class="cols">
  <div class="col"><h4>😬 只靠提示叮嘱</h4><p>模型"大概率"会照格式来，但仍可能漏字段、JSON 被截断、甚至忘了调函数。解析端只能事后修补，修不动就直接失败。"对不对"是<strong>一个概率</strong>。</p></div>
  <div class="col"><h4>😌 提示 + GBNF 语法</h4><p>采样阶段就被卡死：每一步只能选语法合法的 token，输出<strong>必然</strong>是可解析的 JSON。"可解析"不再靠运气，而是<strong>被保证</strong>。</p></div>
</div>
<p>这一对照几乎就是本课的核心：<strong>把"但愿格式没错"换成"采样器只能选对的 token"</strong>。带着这个对照往下看，后面每一步的用意都会更清楚。</p>
<p>举个具体的：你叮嘱模型输出 JSON，它却回一句"好的，我这就帮你发消息"——一句大白话，连个花括号都没有，解析端只能干瞪眼。</p>
<p>就算它真输出了 JSON，也可能漏掉最后一个 <span class="mono">}</span>，或把 <span class="mono">inner_thoughts</span> 错拼成 <span class="mono">inner_thought</span>。差一个字符，<span class="mono">json.loads</span> 就当场翻脸。</p>
<h2>走一遍 get_chat_completion 的流程</h2>
<p>别被"legacy"三个字吓退——正因为它把每一步都摊开来做、毫不藏着掖着，反而成了看清"function calling 到底是什么"的最佳标本。</p>
<p>这条 legacy 路的总指挥是 <span class="mono">chat_completion_proxy.py::get_chat_completion</span>。把它干的事竖排开看，是一条很顺的七步流水线：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>选 wrapper</h4><p>默认是 <span class="mono">ChatMLInnerMonologueWrapper</span>；也可以按名字从 <span class="mono">get_available_wrappers()</span> 里取一个。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>生成 GBNF</h4><p><strong>仅当</strong> wrapper 名字含 <span class="mono">grammar</span> 时，<span class="mono">generate_grammar_and_documentation</span> 动态拼出语法——不是去读静态 <span class="mono">.gbnf</span> 文件。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>schema 进提示</h4><p><span class="mono">chat_completion_to_prompt</span> 把函数 schema 写进<strong>提示文本</strong>，让裸模型"看见"有哪些工具。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>调裸 completion</h4><p>按 <span class="mono">endpoint_type</span> 打到 <span class="mono">/completion</span> 这类裸补全端点；grammar 只会传给 4 个后端。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>解析回结构</h4><p><span class="mono">output_to_chat_completion_response</span> 把吐回的文本<strong>读回</strong> <span class="mono">{function, params}</span>。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>心跳补正</h4><p><span class="mono">function_correction</span> 经 <span class="mono">patch_function</span> 补上 <span class="mono">request_heartbeat</span>（回扣第 15 课）。</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>统一形状</h4><p>最后包成第 21 课那个 <span class="mono">ChatCompletionResponse</span> 交回，下游照旧只读这一种形状。</p></div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">留意第 2 步那个 <strong>仅当</strong>：GBNF 不是默认就生成的，要 wrapper 名字里带 <span class="mono">grammar</span>。换句话说，"受限解码"是要你<strong>显式点名</strong>才开的特性，不是这条路的默认配置。</span></div>
<p>下面把这条流水线落成代码骨架。注意它和上一课三方法的味道一致：<strong>组 → 发 → 转</strong>，只是这里多了"生成语法"和"心跳补正"两道本地特有的工序。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/local_llm/chat_completion_proxy.py</span><span class="ln">get_chat_completion 主流程（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">get_chat_completion</span>(model, messages, functions=<span class="kw">None</span>,
                        wrapper=<span class="kw">None</span>, endpoint=<span class="kw">None</span>, endpoint_type=<span class="kw">None</span>,
                        function_correction=<span class="kw">True</span>, ...) -&gt; ChatCompletionResponse:
    <span class="cm"># 1) 选 wrapper（默认 ChatMLInnerMonologueWrapper）</span>
    llm_wrapper = DEFAULT_WRAPPER() <span class="kw">if</span> wrapper <span class="kw">is</span> <span class="kw">None</span> <span class="kw">else</span> get_available_wrappers()[wrapper]

    <span class="cm"># 2) 仅当 wrapper 名字含 "grammar" 才动态生成 GBNF（不读静态 .gbnf）</span>
    grammar = <span class="kw">None</span>
    <span class="kw">if</span> <span class="st">"grammar"</span> <span class="kw">in</span> (wrapper <span class="kw">or</span> <span class="st">""</span>):
        grammar = <span class="fn">generate_grammar_and_documentation</span>(functions)

    <span class="cm"># 3) wrapper 把函数 schema 塞进提示文本</span>
    prompt = llm_wrapper.<span class="fn">chat_completion_to_prompt</span>(messages, functions)

    <span class="cm"># 4) 按 endpoint_type 调裸 completion 后端（grammar 只有 4 个后端会真正用）</span>
    result = <span class="fn">get_completion</span>(endpoint, endpoint_type, prompt, grammar=grammar)

    <span class="cm"># 5) 把文本解析回 {function, params}</span>
    chat_completion = llm_wrapper.<span class="fn">output_to_chat_completion_response</span>(result)

    <span class="cm"># 6) 本地心跳补正（回扣第 15 课）</span>
    <span class="kw">if</span> function_correction:
        chat_completion = <span class="fn">patch_function</span>(chat_completion)

    <span class="kw">return</span> chat_completion   <span class="cm"># 7) 已是 ChatCompletionResponse 统一形状</span>
</pre></div>
<p>七步里，真正"本地特有"的只有第 2、5、6 三步：生成语法、把文本读回结构、补心跳。其余几步，本质上就是上一课"组请求 → 发请求 → 转形状"那条老骨架。</p>
<p>再多看一眼第 4 步打的端点：是"裸 completion"，比如 llamacpp 的 <span class="mono">/completion</span>、koboldcpp 的 <span class="mono">/api/v1/generate</span>。它们只会"接着这段文字往下写"。</p>
<p>这些端点没有 <span class="mono">/chat/completions</span> 那种现成的消息与工具结构。正因为后端这么"原始"，前面那套"schema 进提示、语法卡采样、文本再解析回来"才有存在的必要——所有结构，都得靠 proxy 这层自己造。</p>
<h2>GBNF：把 JSON 形状刻进语法</h2>
<p>那么"卡住采样"具体怎么卡？答案是 <span class="mono">GBNF</span>——llama.cpp 用的一种 GGML BNF 语法。它被喂给采样器，<strong>每一步只允许语法合法的 token</strong>，于是输出必然是可解析的 JSON。</p>
<p>它强制出来的骨架长这样：最外层是一个 <span class="mono">function</span> 名，配一个 <span class="mono">params</span> 对象；而 <span class="mono">params</span> 里<strong>每个分支都被逼着</strong>先写一个 <span class="mono">inner_thoughts</span> 字符串。</p>
<div class="cellgroup"><div class="cg-cap"><b>一条 GBNF 强制出来的 JSON 骨架</b></div><div class="cells"><span class="cell hl">{</span><span class="sep">·</span><span class="cell">"function": &lt;name&gt;</span><span class="sep">·</span><span class="cell">"params":</span><span class="sep">·</span><span class="cell hl">inner_thoughts: string</span><span class="sep">·</span><span class="cell">request_heartbeat: bool</span><span class="sep">·</span><span class="cell">}</span></div></div>
<p>先花十秒认一下 BNF 记号：<span class="mono">::=</span> 读作"被定义为"，竖线 <span class="mono">|</span> 是"或者"，引号里的是必须原样出现的字面量。规则层层引用，最后拼成一棵语法树。</p>
<p>把它写成语法规则会更清楚。下面是参考样例里的几条关键产生式——但记住开头那句注释：这只是<strong>样板</strong>，运行时是动态生成的。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/local_llm/grammars/json_func_calls_with_inner_thoughts.gbnf</span><span class="ln">关键产生式（节选）</span></div>
<pre><span class="cm"># 参考样例：运行时其实是“动态生成”的，这份样板硬编码了 8 个 MemGPT 基础工具</span>
root               ::= Function
Function           ::= SendMessage | ConversationSearch | ArchivalInsert | ...
SendMessage        ::= "{" "\"function\":" "\"send_message\"" "," "\"params\":" SendMessageParams "}"
SendMessageParams  ::= "{" InnerThoughtsParam "," "\"message\":" string "}"
InnerThoughtsParam ::= "\"inner_thoughts\":" string     <span class="cm"># 每个分支都被强制带上</span>
<span class="cm"># 记忆类工具的 params 还会再强制一个布尔：</span>
HeartbeatParam     ::= "\"request_heartbeat\":" ( "true" | "false" )
</pre></div>
<p>读懂这几行，就读懂了整个戏法：<span class="mono">root</span> 只能展开成某个 <span class="mono">Function</span>，每个 <span class="mono">Function</span> 又只能展开成一个带 <span class="mono">inner_thoughts</span> 的 <span class="mono">params</span> 对象。模型沿着这棵树往下采样，<strong>无路可走到非法形状</strong>。</p>
<p>那 8 个分支也不是随手列的，正是 MemGPT 的基础工具集（发消息、读写归档与核心记忆等）。样例把它们写死只为演示；真跑起来，<span class="mono">Function</span> 的可选项是<strong>照当前 agent 的工具集动态生成</strong>的。</p>
<p>所以模型其实没有"选择困难"：在每个位置，语法都替它把候选集砍到最小，它只是在合法选项里挑概率最高的那个。形状由语法定，内容由模型填，分工清清楚楚。</p>
<div class="cute"><div class="row"><span class="emoji">🔡🔣🔤</span><span class="lab">乱挤的 token</span><span class="arrow">→</span><span class="emoji">📐</span><span class="bubble">只放合法 JSON 出去</span></div><div class="cap">GBNF 像一张镂空模板：一堆乱七八糟的 token 想挤进来，只有 { } 形状的合法 JSON token 能通过</div></div>
<div class="note info"><span class="ni">💡</span><span class="nx">那个 <span class="mono">inner_thoughts</span> 字段不是摆设：它被语法逼着出现在每个分支里，解析时再从 <span class="mono">params</span> 提到 <span class="mono">message.content</span>，正是第 15 课"内心独白"的本地版来源。</span></div>
<p>这一点很关键：本地这条路里，<span class="mono">inner_thoughts</span> 不是模型"自愿"写的，而是被语法<strong>硬性要求</strong>的。等于把第 15 课那条"内心独白"约定，从提示层面的请求，升格成了语法层面的强制。</p>
<h2>并不是所有后端都吃这套语法</h2>
<p>这里有个最容易被忽略的限制：GBNF 受限解码<strong>只有四个后端</strong>真正生效。其余本地后端拿到 grammar 也会把它<strong>丢掉</strong>，改靠别的办法保证 JSON。</p>
<table class="t">
<tr><th>后端</th><th>grammar</th><th>靠什么保证 JSON</th></tr>
<tr><td class="mono">llamacpp / koboldcpp / webui / webui-legacy</td><td>传入 grammar</td><td>受限解码：输出<strong>必然</strong>可解析</td></tr>
<tr><td class="mono">ollama / vllm / lmstudio …</td><td>丢弃 grammar</td><td>靠提示格式 + <span class="mono">clean_json</span> 容错修复</td></tr>
</table>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">别把 <span class="mono">clean_json</span> 当成"重采样 / 重试"。它是 <span class="mono">json_parser.py::clean_json</span> 的<strong>容错修复</strong>：尽力把模型吐的脏文本掰成合法 JSON，实在掰不动就报错——而不是再喊模型重生成一遍。</span></div>
<p>说白了，"丢弃 grammar"的后端就少了那道采样保险，只能赌模型自觉、再靠 <span class="mono">clean_json</span> 兜底。多数现代本地模型对话能力够强，赌得起；但这跟四个语法后端的"硬保证"，终究是两个等级。</p>
<p>所以同一条 legacy 路，对四个语法后端是"<strong>采样级</strong>的硬保证"，对其余后端则退化成"<strong>解析级</strong>的尽力修复"。前者治本，后者治标。</p>
<p>为什么偏偏是这四个？因为只有它们的采样接口暴露了一个能接 grammar 的入口（llama.cpp 系一脉相承）。ollama、vllm 这些虽然底子相近，对外却只给"OpenAI 兼容"那套，并不收 GBNF。</p>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>这其实是 MemGPT 最初的魔法，也是对"function calling"一次漂亮的重新理解。</p>
<p>在 OpenAI 的工具 API 还没一统江湖之前，你要怎么让一个只会"续写文本"的模型去调用函数？</p>
<p>第一步好想：把函数 schema 当文本塞进提示，请它输出 JSON。难的是第二步——用 <strong>GBNF 语法去约束解码器本身</strong>，让模型在采样时<strong>压根吐不出</strong>任何非法 token，只能吐出一个合法的 <span class="mono">{"function":…, "params":{"inner_thoughts":…}}</span>。</p>
<p>受限解码把"<strong>但愿</strong>格式对了"换成"采样器<strong>只能</strong>挑语法合法的 token"——可解析性，从概率升级成了保证。</p>
<p>这也正是它后来变成 legacy 的原因：等到每家 provider 都会说 OpenAI 的工具 API（第 21 课那个通用形状），兼容后端就不再需要这套语法戏法了。</p>
<p>但它仍是 Letta 拿到可靠结构化输出的<strong>观念源头</strong>。一头呼应第 21 课（OpenAI 形状赢了），一头呼应第 15 课（inner_thoughts 与心跳）。</p>
</div>
<h2>wrapper：在裸 completion 上"演"出 function calling</h2>
<p>语法管住了"吐什么形状"，那"把工具讲给模型听"和"把文本读回结构"这两头，归谁管？归 wrapper。它的抽象基类是 <span class="mono">wrapper_base.py::LLMChatCompletionWrapper</span>，只有两个方法。</p>
<p>一头 <span class="mono">chat_completion_to_prompt</span> 把函数 schema（连同 <span class="mono">inner_thoughts</span> 的说明）<strong>写进提示</strong>；另一头 <span class="mono">output_to_chat_completion_response</span> 把模型吐回的文本<strong>解析回</strong> <span class="mono">{function, args}</span>。</p>
<p>这两个方法都挂在抽象基类上、标了 <span class="mono">@abstractmethod</span>。换句话说，任何一个新 wrapper 想接进来，都被逼着把"怎么写出去"和"怎么读回来"两头都填齐，少一个都实例化不了。</p>
<p>选哪个 wrapper，由 <span class="mono">utils.py::get_available_wrappers()</span> 决定：名字含 <span class="mono">grammar</span> 就顺手建语法，含 <span class="mono">noforce</span> 就把 <span class="mono">inner_thoughts</span> 放到顶层。默认那个是 <span class="mono">ChatMLInnerMonologueWrapper</span>。</p>
<p>为什么还要分模型家族？因为不同基座的"对话模板"不一样：ChatML 用 <span class="mono">&lt;|im_start|&gt;</span> 这类标记分隔角色，Llama3 又另起一套。wrapper 得套对模板，模型才认得出哪段是系统、哪段是用户。</p>
<p>下面看"解析回结构"这一头的骨架——它就是上面 <span class="mono">clean_json</span> 容错修复真正被调用的地方。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/local_llm/llm_chat_completion_wrappers/chatml.py</span><span class="ln">output_to_chat_completion_response（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">output_to_chat_completion_response</span>(self, raw_llm_output) -&gt; ChatCompletionResponse:
    <span class="cm"># 1) 先把脏文本掰成 JSON（容错修复，不是重采样）</span>
    data = <span class="fn">clean_json</span>(raw_llm_output)

    <span class="cm"># 2) 取出 function 名与 params</span>
    function_name = data[<span class="st">"function"</span>]
    function_params = data[<span class="st">"params"</span>]

    <span class="cm"># 3) 把 inner_thoughts 从 params 提升到 message.content（回扣第 15 课）</span>
    inner_thoughts = function_params.pop(<span class="st">"inner_thoughts"</span>, <span class="kw">None</span>)

    message = {
        <span class="st">"role"</span>: <span class="st">"assistant"</span>,
        <span class="st">"content"</span>: inner_thoughts,
        <span class="st">"function_call"</span>: {<span class="st">"name"</span>: function_name,
                          <span class="st">"arguments"</span>: json.<span class="fn">dumps</span>(function_params)},
    }
    <span class="kw">return</span> <span class="fn">ChatCompletionResponse</span>(choices=[Choice(message=message)])
</pre></div>
<p>看清这三步，就看清了 wrapper 的本质：它是一台<strong>双向翻译机</strong>——出去时把工具写成人话塞进提示，回来时把人话读回成 <span class="mono">function_call</span>。模型自始至终只在"续写文本"。</p>
<p>这台翻译机最妙的地方，是它把"会不会 function calling"这个能力，从模型身上<strong>挪到了外面</strong>。模型还是那个只会续写的模型，本事是 proxy 这层替它"接"上去的。</p>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">local_llm/chat_completion_proxy.py::get_chat_completion</span>——legacy 总指挥，串起七步。</p>
<p><span class="mono">local_llm/grammars/gbnf_grammar_generator.py::generate_grammar_and_documentation</span>——运行时动态生成 GBNF。</p>
<p><span class="mono">llm_chat_completion_wrappers/wrapper_base.py::LLMChatCompletionWrapper</span>——抽象基类，两个方法。</p>
<p><span class="mono">llm_chat_completion_wrappers/chatml.py::ChatMLInnerMonologueWrapper</span>——默认 wrapper（<span class="mono">DEFAULT_WRAPPER</span>）。</p>
<p><span class="mono">local_llm/function_parser.py::insert_heartbeat</span> 与 <span class="mono">patch_function</span>——本地心跳补正（回扣第 15 课）。</p>
</div>
<h2>今天它还在哪条路上</h2>
<p>把"现代"和"legacy"两条路并排画出来，就不会再把它们搞混。现代本地后端根本不碰下面这条链：</p>
<div class="flow">
  <div class="node"><div class="nt">agent.py::Agent</div><div class="nd">旧执行体</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">llm_api_tools.py::create</div><div class="nd">老 create 函数</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">else 本地分支</div><div class="nd">非云厂商兜底</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">get_chat_completion</div><div class="nd">GBNF 老路</div></div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">对照记牢：现代本地（ollama/vllm/lmstudio）走 <span class="mono">LLMClient.create → OpenAIClient</span>（第 21 课默认 <span class="mono">case _</span>，无专属 client）；GBNF 这条路只在旧 <span class="mono">agent.py::Agent</span> 经 <span class="mono">llm_api_tools.py::create</span> 的 <span class="mono">else</span> 本地分支兜底时才被走到。</span></div>
<h2>再挖深一点</h2>
<p>主线到这里就完整了。下面四个抽屉，专收你大概率会追问的细节——按兴趣展开即可，不展开也不影响对主线的理解。</p>
<details class="accordion"><summary>GBNF 到底做了什么？</summary><div class="acc-body">
<p>GBNF 是 llama.cpp 的一种 GGML BNF 语法。它不参与"理解"，只在<strong>采样那一步</strong>做一件事：把下一个 token 的候选集，裁剪到"语法此刻允许的"那些。</p>
<p>于是模型每走一步都被语法牵着：该出 <span class="mono">{</span> 的位置只能出 <span class="mono">{</span>，该出字段名的位置只能出那几个名字。走到最后，整串输出<strong>必然</strong>是一棵合法的 JSON 树。</p>
<p>这就是它最值钱的地方：把"可解析"从一个<strong>概率</strong>，变成了一个<strong>保证</strong>——顺带治好"忘了调函数 / JSON 断在半截"这两类老毛病。</p>
</div></details>
<details class="accordion"><summary>为什么说它是 legacy？</summary><div class="acc-body">
<p>因为 OpenAI 兼容赢了。等到几乎每家 provider 都提供"OpenAI 形状"的工具 API，第 21 课那个默认 <span class="mono">case _ → OpenAIClient</span> 就能接住一大票本地后端，根本用不上语法戏法。</p>
<p>代码里也有痕迹：<span class="mono">LLMClient.create</span> 里<strong>没有</strong>本地专属 client；<span class="mono">ProviderType</span> 枚举里也<strong>不再</strong>有 <span class="mono">llamacpp / koboldcpp / webui</span> 这些项，它们退到了 <span class="mono">local_llm</span> 这条老路里。</p>
<p>所以本课讲的是"它当年怎么 work、为什么经典"，而不是"今天默认就这么跑"。</p>
</div></details>
<details class="accordion"><summary>不支持语法的后端怎么办？</summary><div class="acc-body">
<p>只有 <span class="mono">koboldcpp / llamacpp / webui / webui-legacy</span> 这四个会真正吃 grammar。其余后端（ollama / vllm / lmstudio…）拿到 grammar 也直接丢掉。</p>
<p>它们改靠两条腿走路：一是 wrapper 把格式要求写进提示，二是 <span class="mono">json_parser.py::clean_json</span> 在解析时<strong>容错修复</strong>那串文本。</p>
<p>强调一遍：<span class="mono">clean_json</span> 是"尽力把脏 JSON 掰正"，<strong>不是</strong>"再喊模型生成一遍"。它治标不治本，但多数时候够用。</p>
</div></details>
<details class="accordion"><summary>wrapper 怎么"在裸 completion 上演 function calling"？</summary><div class="acc-body">
<p>出去这一头：wrapper 用 <span class="mono">_compile_function_block</span> 把函数 schema（含 <span class="mono">inner_thoughts</span> 的描述）写进提示，并按模型家族（ChatML、Llama3…）套上对应模板，必要时还给 <span class="mono">first_message</span> 一点引导。</p>
<p>回来这一头：把文本经 <span class="mono">clean_json</span> 读回 <span class="mono">{function, args}</span>，再把 <span class="mono">inner_thoughts</span> 从 params 提到 <span class="mono">content</span>。</p>
<p>心跳也在这条路里补：<span class="mono">function_parser.py::insert_heartbeat</span> 给记忆类工具补上 <span class="mono">request_heartbeat</span>，正接回第 15 课那套"要不要再走一步"的判断。</p>
</div></details>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>别以为 GBNF 是现在本地模型的<strong>默认</strong>路径。它是 legacy；现代本地后端走第 21 课的 <span class="mono">OpenAIClient</span>。</p>
<p>别以为运行时 GBNF 读的是某个静态 <span class="mono">.gbnf</span> 文件。它是<strong>动态生成</strong>的；<span class="mono">json_func_calls_with_inner_thoughts.gbnf</span> 只是参考样例。</p>
<p>别以为所有本地后端都吃 grammar。只有 <span class="mono">llamacpp/koboldcpp/webui/webui-legacy</span> 四个生效，其余直接丢弃。</p>
<p>别把 <span class="mono">clean_json</span> 当成"重采样重试"——它只是解析时的容错修复，掰不动就报错。</p>
</div>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li><span class="mono">chat_completion_proxy.py::get_chat_completion</span> 是 legacy 总指挥：选 wrapper → 生成 GBNF → schema 进提示 → 调裸 completion → 解析回结构 → 心跳补正。</li>
<li>GBNF 在<strong>采样级</strong>约束 token，让输出必然是可解析 JSON，并强制每个分支都带 <span class="mono">inner_thoughts</span>。</li>
<li>语法只在 <span class="mono">llamacpp/koboldcpp/webui/webui-legacy</span> 生效；其余后端丢弃语法，靠 <span class="mono">clean_json</span> 容错修复。</li>
<li>wrapper 是双向翻译机：<span class="mono">chat_completion_to_prompt</span> 把 schema 写出去，<span class="mono">output_to_chat_completion_response</span> 把文本读回来。</li>
<li>这是 MemGPT 时代的经典老路；现代本地后端走第 21 课的 OpenAI 兼容 <span class="mono">OpenAIClient</span>。</li>
</ul>
</div>
<h2>第六部分收官</h2>
<p>三课走完，整个第六部分其实是一条很顺的线。把它收成一张图：</p>
<div class="cellgroup"><div class="cg-cap"><b>第六部分收官：三课一条线</b></div><div class="cells"><span class="cell">21 立统一契约</span><span class="sep">·</span><span class="cell">22 隔离怪癖</span><span class="sep">·</span><span class="cell hl">23 本地 + GBNF</span></div></div>
<p>一句话把三课缝起来：<strong>先立契约 → 再把怪癖关进笼子 → 最后连没有工具 API 的模型也想办法接上</strong>。</p>
<p>它一头扣回第 21 课——之所以处处以 OpenAI 形状为目标，正因为它已是全行业的通用格式；一头扣回第 15 课——本地路上那个被语法逼出来的 <span class="mono">inner_thoughts</span> 与心跳，就是"内心独白 + 要不要再走一步"的同一套机制。</p>
<p>退一步看，整部分讲的其实是同一件事的三个层次：<strong>定义一种通用语言、把方言关进翻译层、再给不会说话的模型也配一个翻译</strong>。抽象的红利，就这样一层层往外摊开。</p>
<p>把这条线记牢，往后每见一家新接入的 provider，你都会自然去问同样三个问题：它的请求长什么样、响应怎么收成 OpenAI 形状、有没有原生工具能力。这正是第六部分留给你的肌肉记忆。</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">一句话收束整个第六部分：<strong>无论底下接的是云端大厂还是一个连工具 API 都没有的本地小模型，到了 agent 循环眼里，都只是同一种 OpenAI 形状的响应</strong>。这就是"provider 抽象"全部的野心。</span></div>
<p>这份野心也有它的边界：它只管"把各家模型收成一种形状"。至于这些形状收回来之后怎么落库、怎么被一个长期运行的服务调度起来，就是下一部分要接手的活了。</p>
<p>provider 这一层讲透了，模型这头就算交代清楚。可一个 agent 要真正跑起来，它的状态、记忆、消息得<strong>存下来</strong>，还要包成一个能对外服务的进程。下一部分，第七部分就转入 server 与持久化——看 Letta 怎么把这一切落到数据库与服务端，让一个 agent 真正"活"过一次次重启。</p>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Part 6 reaches its close. The first two lessons stood up the unified contract (Lesson 21), then caged each cloud provider's quirks into a subclass one by one (Lesson 22). But one hardest case stays untouched: a local model with <strong>no native function calling at all</strong>, one that can only "continue text" — how do you get it to call a tool?</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson reconstructs that classic MemGPT-era trick: first stuff the tool schema into the prompt as text, then use a <span class="mono">GBNF</span> grammar to <strong>constrain the decoder itself</strong>, so that while sampling the model literally cannot emit an illegal token — only legal JSON. One inoculation up front: this is a legacy path.</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><strong>This is a legacy path</strong>: modern local backends (ollama/vllm/lmstudio) go through Lesson 21's OpenAI-compatible <span class="mono">OpenAIClient</span>; GBNF constrained decoding only fires on the old <span class="mono">Agent</span> fallback path, and only for <span class="mono">llamacpp/koboldcpp/webui</span>. We cover "how it works, why it's classic", not "how things run by default today".</span></div>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Grab the lesson in one line: <strong>for a model that can only continue text, use grammar to force out parseable JSON</strong>.</p>
<p>Say it plainly up front — this is a <strong>historical / secondary path</strong>. Modern local backends (ollama / vllm / lmstudio) have long offered "OpenAI-compatible" endpoints, taking Lesson 21's default <span class="mono">case _ → OpenAIClient</span>, with no dedicated client at all.</p>
<p>The GBNF route is reached only as a <strong>fallback</strong>: the old <span class="mono">agent.py::Agent</span>, after <span class="mono">LLMClient.create</span>, goes through <span class="mono">llm_api_tools.py::create</span>'s <span class="mono">else</span> (local) branch to call <span class="mono">chat_completion_proxy.py::get_chat_completion</span>.</p>
<p>Its flow is a chain: pick a wrapper → (only if the name contains <span class="mono">grammar</span>) dynamically generate GBNF → the wrapper stuffs the function schema into <strong>prompt text</strong> → call the "bare completion" backend → parse the text <strong>back</strong> into <span class="mono">{function, params}</span> → heartbeat correction.</p>
<p>Remember one line: <strong>schema into the prompt, grammar governs sampling, text parsed back into structure</strong>. These three steps are everything this lesson pries apart, ring by ring — and the whole secret of this old path.</p>
</div>
<div class="card analogy"><div class="tag">🔌 Real-life analogy</div>
<p>Picture "adding function calling to a model that can only continue text" like this: in front of you sits a <strong>child who only finishes sentences</strong> — you hand over a line, he writes the next one along, with no idea what "calling a tool" even means.</p>
<p>The first move is blunt: write down what the tool looks like and which parameters it takes as a <strong>manual copied straight into the question</strong>, then add "please output JSON in this format". That is the wrapper stuffing the schema into the prompt.</p>
<p>But a reminder alone isn't safe — he might wander off-topic, or leave the JSON one bracket short. Hence the second move, the real masterstroke: lay a <strong>stencil plate</strong> over the paper, so the pen can only land in the cut-out slots and <strong>physically cannot</strong> write outside them.</p>
<p>That plate is the <span class="mono">GBNF</span> grammar. It doesn't "persuade" the model to keep the format — it clamps the sampling directly: each step only allows grammar-legal tokens, so every stroke necessarily takes shape.</p>
<p>Remember the division of labor: the first move lets the model <strong>"know"</strong> what to fill in, the second lets it <strong>"only"</strong> fill it in right — one soft, one hard. Without the second, the first is just a gentle prayer.</p>
</div>
<p>So this lesson really tells three interlocking things: <strong>how schema enters the prompt</strong>, <strong>how GBNF clamps sampling</strong>, and <strong>how text gets parsed back into structure</strong>. We pry them apart below — but first answer the one question most worth asking.</p>
<p>One more word on origins: early MemGPT faced exactly a batch of open-source models with no tool API, and this "prompt + grammar" play was forced out back then. Reading it today feels more like reading a historical slice from when "function calling wasn't standardized yet".</p>
<h2>Why Putting Schema in the Prompt Isn't Enough</h2>
<p>Set "rely on the prompt's reminder alone" and "prompt plus a grammar clamp" side by side, and you see exactly where GBNF's value lies.</p>
<div class="cols">
  <div class="col"><h4>😬 Prompt reminder only</h4><p>The model will "most likely" follow the format, but it can still drop fields, truncate the JSON, even forget to call a function. The parser can only patch afterward, and fails outright when it can't. "Correct" is <strong>a probability</strong>.</p></div>
  <div class="col"><h4>😌 Prompt + GBNF grammar</h4><p>Clamped at the sampling stage: each step can only choose a grammar-legal token, so the output is <strong>necessarily</strong> parseable JSON. "Parseable" no longer rides on luck — it is <strong>guaranteed</strong>.</p></div>
</div>
<p>This contrast is nearly the lesson's core: swap "hopefully the format is right" for <strong>"the sampler can only pick the right tokens"</strong>. Carry it downward and the purpose of every later step gets clearer.</p>
<p>Concretely: you tell the model to output JSON, and it replies "Sure, I'll send that message for you now" — plain prose, not a single brace, and the parser can only stare.</p>
<p>Even if it does output JSON, it might drop the final <span class="mono">}</span>, or misspell <span class="mono">inner_thoughts</span> as <span class="mono">inner_thought</span>. One character off, and <span class="mono">json.loads</span> blows up on the spot.</p>
<h2>Walking Through the get_chat_completion Flow</h2>
<p>Don't let the word "legacy" scare you off — precisely because it lays every step out in the open, hiding nothing, it becomes the best specimen for seeing "what function calling really is".</p>
<p>This legacy path's conductor is <span class="mono">chat_completion_proxy.py::get_chat_completion</span>. Lay out what it does vertically and it's a smooth seven-step pipeline:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Pick the wrapper</h4><p>Default is <span class="mono">ChatMLInnerMonologueWrapper</span>; you can also fetch one by name from <span class="mono">get_available_wrappers()</span>.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Generate GBNF</h4><p><strong>Only when</strong> the wrapper name contains <span class="mono">grammar</span>, <span class="mono">generate_grammar_and_documentation</span> dynamically assembles the grammar — not by reading a static <span class="mono">.gbnf</span> file.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Schema into prompt</h4><p><span class="mono">chat_completion_to_prompt</span> writes the function schema into <strong>prompt text</strong>, so the bare model "sees" which tools exist.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Call bare completion</h4><p>By <span class="mono">endpoint_type</span>, hit a bare completion endpoint like <span class="mono">/completion</span>; the grammar is passed to only 4 backends.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Parse back to structure</h4><p><span class="mono">output_to_chat_completion_response</span> reads the returned text <strong>back</strong> into <span class="mono">{function, params}</span>.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Heartbeat correction</h4><p><span class="mono">function_correction</span>, via <span class="mono">patch_function</span>, supplies <span class="mono">request_heartbeat</span> (callback to Lesson 15).</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>Unify the shape</h4><p>Finally wrap into Lesson 21's <span class="mono">ChatCompletionResponse</span> and hand back; downstream still reads only this one shape.</p></div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Note the <strong>only when</strong> in step 2: GBNF isn't generated by default — it needs <span class="mono">grammar</span> in the wrapper name. In other words, "constrained decoding" is a feature you must <strong>explicitly name</strong> to turn on, not this path's default setting.</span></div>
<p>Below, drop this pipeline into a code skeleton. Note it has the same flavor as last lesson's three methods: <strong>assemble → send → convert</strong>, just with two locally specific steps added — "generate grammar" and "heartbeat correction".</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/local_llm/chat_completion_proxy.py</span><span class="ln">get_chat_completion main flow (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">get_chat_completion</span>(model, messages, functions=<span class="kw">None</span>,
                        wrapper=<span class="kw">None</span>, endpoint=<span class="kw">None</span>, endpoint_type=<span class="kw">None</span>,
                        function_correction=<span class="kw">True</span>, ...) -&gt; ChatCompletionResponse:
    <span class="cm"># 1) pick the wrapper (default ChatMLInnerMonologueWrapper)</span>
    llm_wrapper = DEFAULT_WRAPPER() <span class="kw">if</span> wrapper <span class="kw">is</span> <span class="kw">None</span> <span class="kw">else</span> get_available_wrappers()[wrapper]

    <span class="cm"># 2) only when the wrapper name contains "grammar" do we generate GBNF (no static .gbnf)</span>
    grammar = <span class="kw">None</span>
    <span class="kw">if</span> <span class="st">"grammar"</span> <span class="kw">in</span> (wrapper <span class="kw">or</span> <span class="st">""</span>):
        grammar = <span class="fn">generate_grammar_and_documentation</span>(functions)

    <span class="cm"># 3) the wrapper stuffs the function schema into prompt text</span>
    prompt = llm_wrapper.<span class="fn">chat_completion_to_prompt</span>(messages, functions)

    <span class="cm"># 4) call the bare completion backend by endpoint_type (only 4 backends really use grammar)</span>
    result = <span class="fn">get_completion</span>(endpoint, endpoint_type, prompt, grammar=grammar)

    <span class="cm"># 5) parse the text back into {function, params}</span>
    chat_completion = llm_wrapper.<span class="fn">output_to_chat_completion_response</span>(result)

    <span class="cm"># 6) local heartbeat correction (callback to Lesson 15)</span>
    <span class="kw">if</span> function_correction:
        chat_completion = <span class="fn">patch_function</span>(chat_completion)

    <span class="kw">return</span> chat_completion   <span class="cm"># 7) already the unified ChatCompletionResponse shape</span>
</pre></div>
<p>Of the seven steps, only steps 2, 5, and 6 are truly "locally specific": generate grammar, read text back into structure, supply the heartbeat. The rest are essentially last lesson's old skeleton — <strong>assemble request → send request → convert shape</strong>.</p>
<p>Glance once more at the endpoint step 4 hits: a "bare completion", like llamacpp's <span class="mono">/completion</span> or koboldcpp's <span class="mono">/api/v1/generate</span>. They only "keep writing on from this text".</p>
<p>These endpoints have none of the ready-made message-and-tool structure of <span class="mono">/chat/completions</span>. Precisely because the backend is this "primitive", the earlier "schema into prompt, grammar clamps sampling, text parsed back" has any reason to exist — every bit of structure must be built by the proxy layer itself.</p>
<h2>GBNF: Carving the JSON Shape into Grammar</h2>
<p>So how does "clamping the sampling" actually clamp? The answer is GBNF — a GGML BNF grammar used by llama.cpp. Fed to the sampler, <strong>each step only allows grammar-legal tokens</strong>, so the output is necessarily parseable JSON.</p>
<p>The skeleton it forces out looks like this: the outermost layer is a <span class="mono">function</span> name paired with a <span class="mono">params</span> object; and inside <span class="mono">params</span>, <strong>every branch is forced</strong> to write an <span class="mono">inner_thoughts</span> string first.</p>
<div class="cellgroup"><div class="cg-cap"><b>A JSON skeleton forced out by one GBNF</b></div><div class="cells"><span class="cell hl">{</span><span class="sep">·</span><span class="cell">"function": &lt;name&gt;</span><span class="sep">·</span><span class="cell">"params":</span><span class="sep">·</span><span class="cell hl">inner_thoughts: string</span><span class="sep">·</span><span class="cell">request_heartbeat: bool</span><span class="sep">·</span><span class="cell">}</span></div></div>
<p>Spend ten seconds on the BNF notation: <span class="mono">::=</span> reads as "is defined as", the bar <span class="mono">|</span> is "or", and the literals in quotes must appear verbatim. Rules reference rules, layer by layer, finally assembling into a grammar tree.</p>
<p>Writing it as grammar rules is clearer. Below are a few key productions from the reference sample — but remember that opening comment: this is only <strong>boilerplate</strong>; at runtime it is dynamically generated.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/local_llm/grammars/json_func_calls_with_inner_thoughts.gbnf</span><span class="ln">key productions (excerpt)</span></div>
<pre><span class="cm"># reference sample: at runtime it is actually “dynamically generated”; this boilerplate hardcodes 8 MemGPT base tools</span>
root               ::= Function
Function           ::= SendMessage | ConversationSearch | ArchivalInsert | ...
SendMessage        ::= "{" "\"function\":" "\"send_message\"" "," "\"params\":" SendMessageParams "}"
SendMessageParams  ::= "{" InnerThoughtsParam "," "\"message\":" string "}"
InnerThoughtsParam ::= "\"inner_thoughts\":" string     <span class="cm"># every branch is forced to carry it</span>
<span class="cm"># memory-class tools' params force one more boolean:</span>
HeartbeatParam     ::= "\"request_heartbeat\":" ( "true" | "false" )
</pre></div>
<p>Read these few lines and you've read the whole trick: <span class="mono">root</span> can only expand into some <span class="mono">Function</span>, and each <span class="mono">Function</span> can only expand into a <span class="mono">params</span> object carrying <span class="mono">inner_thoughts</span>. The model samples down this tree with <strong>no path to an illegal shape</strong>.</p>
<p>Those 8 branches aren't listed at random either — they're MemGPT's base tool set (send message, read/write archival and core memory, etc.). The sample hardcodes them only to demonstrate; in a real run, <span class="mono">Function</span>'s options are <strong>dynamically generated from the current agent's tool set</strong>.</p>
<p>So the model has no "decision paralysis": at each position the grammar cuts its candidate set to the minimum, and it merely picks the highest-probability one among the legal options. Shape is set by grammar, content is filled by the model — the division is crystal clear.</p>
<div class="cute"><div class="row"><span class="emoji">🔡🔣🔤</span><span class="lab">jumbled tokens</span><span class="arrow">→</span><span class="emoji">📐</span><span class="bubble">only legal JSON gets out</span></div><div class="cap">GBNF is like a stencil: a crowd of messy tokens want in, but only the legal { } -shaped JSON tokens can pass</div></div>
<div class="note info"><span class="ni">💡</span><span class="nx">That <span class="mono">inner_thoughts</span> field is no decoration: the grammar forces it into every branch, and on parse it's lifted from <span class="mono">params</span> into <span class="mono">message.content</span> — exactly the local version of Lesson 15's "inner monologue".</span></div>
<p>This point is key: on the local path, <span class="mono">inner_thoughts</span> isn't written "voluntarily" by the model — it's <strong>hard-required</strong> by the grammar. That promotes Lesson 15's "inner monologue" convention from a prompt-level request to a grammar-level mandate.</p>
<h2>Not Every Backend Accepts This Grammar</h2>
<p>Here's the most easily overlooked limit: GBNF constrained decoding really fires on only <strong>four backends</strong>. The rest take the grammar and <strong>drop</strong> it, falling back on another way to guarantee JSON.</p>
<table class="t">
<tr><th>Backend</th><th>grammar</th><th>How JSON is guaranteed</th></tr>
<tr><td class="mono">llamacpp / koboldcpp / webui / webui-legacy</td><td>grammar passed in</td><td>constrained decoding: output <strong>necessarily</strong> parseable</td></tr>
<tr><td class="mono">ollama / vllm / lmstudio …</td><td>grammar dropped</td><td>prompt format + <span class="mono">clean_json</span> tolerant repair</td></tr>
</table>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">Don't treat <span class="mono">clean_json</span> as "resampling / retry". It's the tolerant repair of <span class="mono">json_parser.py::clean_json</span>: it tries hard to bend the model's dirty text into legal JSON, and errors out when it truly can't — rather than asking the model to regenerate.</span></div>
<p>Plainly: a backend that "drops the grammar" loses that sampling insurance, and can only bet on the model behaving, with <span class="mono">clean_json</span> as a net. Most modern local models are conversational enough to bet on; but versus the four grammar backends' "hard guarantee", these are ultimately two tiers.</p>
<p>So the same legacy path is a <strong>"sampling-level hard guarantee"</strong> for the four grammar backends, but degrades to a <strong>"parse-level best-effort repair"</strong> for the rest. The former cures the root, the latter treats the symptom.</p>
<p>Why exactly these four? Because only their sampling interfaces expose an entry point that accepts a grammar (all descending from llama.cpp). ollama, vllm and the like share similar internals, but externally offer only the "OpenAI-compatible" set and don't accept GBNF.</p>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>This is really MemGPT's original magic, and a beautiful reinterpretation of "function calling".</p>
<p>Before OpenAI's tool API unified the field, how could you get a model that only "continues text" to call a function?</p>
<p>The first step is easy to imagine: stuff the function schema into the prompt as text and ask for JSON. The hard part is the second — use a <strong>GBNF grammar to constrain the decoder itself</strong>, so that while sampling the model literally <strong>cannot</strong> emit any illegal token, only a legal <span class="mono">{"function":…, "params":{"inner_thoughts":…}}</span>.</p>
<p>Constrained decoding swaps "hopefully the format came out right" for "the sampler can only pick grammar-legal tokens" — parseability, upgraded from a probability to a guarantee.</p>
<p>This is also exactly why it later became legacy: once every provider could speak OpenAI's tool API (Lesson 21's universal shape), compatible backends no longer needed this grammar trick.</p>
<p>But it remains the <strong>conceptual origin</strong> of Letta's reliable structured output. One end echoes Lesson 21 (the OpenAI shape won), the other echoes Lesson 15 (<span class="mono">inner_thoughts</span> and the heartbeat).</p>
</div>
<h2>wrapper: "Acting Out" Function Calling on Bare Completion</h2>
<p>Grammar governs "what shape comes out", so who handles the two ends — "telling the model about the tools" and "reading text back into structure"? The wrapper. Its abstract base class is <span class="mono">wrapper_base.py::LLMChatCompletionWrapper</span>, with just two methods.</p>
<p>On one end <span class="mono">chat_completion_to_prompt</span> writes the function schema (along with the <span class="mono">inner_thoughts</span> description) into the prompt; on the other, <span class="mono">output_to_chat_completion_response</span> parses the model's returned text back into <span class="mono">{function, args}</span>.</p>
<p>Both methods hang on the abstract base, marked <span class="mono">@abstractmethod</span>. In other words, any new wrapper that wants in is forced to fill both ends — "how to write out" and "how to read back" — and can't be instantiated if either is missing.</p>
<p>Which wrapper to pick is decided by <span class="mono">utils.py::get_available_wrappers()</span>: a name with <span class="mono">grammar</span> builds a grammar along the way, one with <span class="mono">noforce</span> puts <span class="mono">inner_thoughts</span> at the top level. The default is <span class="mono">ChatMLInnerMonologueWrapper</span>.</p>
<p>Why split by model family? Because different bases have different "chat templates": ChatML uses markers like <span class="mono">&lt;|im_start|&gt;</span> to separate roles, while Llama3 has its own set. The wrapper must apply the right template for the model to recognize which span is system and which is user.</p>
<p>Below, look at the skeleton of the "parse back to structure" end — it's where the <span class="mono">clean_json</span> tolerant repair above is actually called.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/local_llm/llm_chat_completion_wrappers/chatml.py</span><span class="ln">output_to_chat_completion_response (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">output_to_chat_completion_response</span>(self, raw_llm_output) -&gt; ChatCompletionResponse:
    <span class="cm"># 1) first bend the dirty text into JSON (tolerant repair, not resampling)</span>
    data = <span class="fn">clean_json</span>(raw_llm_output)

    <span class="cm"># 2) pull out the function name and params</span>
    function_name = data[<span class="st">"function"</span>]
    function_params = data[<span class="st">"params"</span>]

    <span class="cm"># 3) lift inner_thoughts from params into message.content (callback to Lesson 15)</span>
    inner_thoughts = function_params.pop(<span class="st">"inner_thoughts"</span>, <span class="kw">None</span>)

    message = {
        <span class="st">"role"</span>: <span class="st">"assistant"</span>,
        <span class="st">"content"</span>: inner_thoughts,
        <span class="st">"function_call"</span>: {<span class="st">"name"</span>: function_name,
                          <span class="st">"arguments"</span>: json.<span class="fn">dumps</span>(function_params)},
    }
    <span class="kw">return</span> <span class="fn">ChatCompletionResponse</span>(choices=[Choice(message=message)])
</pre></div>
<p>See these three steps and you see the wrapper's essence: a <strong>bidirectional translator</strong> — on the way out it writes tools as plain words into the prompt, on the way back it reads plain words into a <span class="mono">function_call</span>. The model, start to finish, only "continues text".</p>
<p>The translator's slickest part is moving the "can it do function calling" capability <strong>off the model and outside</strong>. The model is still the same continue-only model; the skill is "wired on" for it by the proxy layer.</p>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">local_llm/chat_completion_proxy.py::get_chat_completion</span> — the legacy conductor, stringing the seven steps.</p>
<p><span class="mono">local_llm/grammars/gbnf_grammar_generator.py::generate_grammar_and_documentation</span> — dynamically generates GBNF at runtime.</p>
<p><span class="mono">llm_chat_completion_wrappers/wrapper_base.py::LLMChatCompletionWrapper</span> — the abstract base, two methods.</p>
<p><span class="mono">llm_chat_completion_wrappers/chatml.py::ChatMLInnerMonologueWrapper</span> — the default wrapper (<span class="mono">DEFAULT_WRAPPER</span>).</p>
<p><span class="mono">local_llm/function_parser.py::insert_heartbeat</span> and <span class="mono">patch_function</span> — local heartbeat correction (callback to Lesson 15).</p>
</div>
<!--ENMORE-->
""",
}
