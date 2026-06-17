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


LESSON_22 = {"zh": r"""<p>stub</p>""", "en": r"""<p>stub</p>"""}
