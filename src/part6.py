"""Part 6 · The LLM provider abstraction — lessons 21-23."""

LESSON_21 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">前面五个部分，我们一直把"调用大模型"当成一行就能搞定的事——把消息递过去，等它把回复递回来。可现实远没这么干净：Letta 同时支持<strong>二十多家供应商</strong>，从 OpenAI、Anthropic、Google 到 Groq，再到跑在你自己机器上的本地模型，它们的请求长什么样、响应长什么样、连报错字段都各不相同。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课要回答的就是一个问题：怎么把这一堆五花八门的差异，<strong>整整齐齐藏在同一个统一接口背后</strong>，让第 13 到 16 课那套执行循环，从头到尾既不知道、也根本不需要关心自己究竟在跟哪一家说话。这是整个第六部分的开篇。</p>
<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>想象联合国大会的<strong>同声传译</strong>。台上各国代表各说各的语言——有人讲法语、有人讲阿拉伯语、有人讲中文，谁也不迁就谁。这一个个代表，就是一家家 <span class="mono">provider</span>。</p>
<p>但台下的你，耳机里只听到<strong>一种</strong>工作语言。秘密全在传译间：不管代表说什么，翻译都把它转成同一种语言再送进你耳朵，所以你只要听得懂这一种就够了。</p>
<p>Letta 选定的这门"工作语言"，就是 <strong>OpenAI 的响应形状</strong>。台下的 agent 循环只需听懂这一种，台上换谁发言都无所谓——而那个"传译间"，正是本课要拆开的三方法 client。</p>
</div>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>一个字段驱动一个工厂，一套三方法把差异收敛成一种形状</strong>。</p>
<p>驱动分派的字段是 <span class="mono">llm_config.model_endpoint_type</span>。它被传进 <span class="mono">LLMClient.create</span>，里面一个 <span class="mono">match/case</span> 挑出具体的 client 类；没显式列到的，一律落到默认的 <span class="mono">OpenAIClient</span>。</p>
<p>挑出的 client 继承自 <span class="mono">LLMClientBase</span>，核心是三个方法：<span class="mono">build_request_data</span> / <span class="mono">request_async</span> / <span class="mono">convert_response_to_chat_completion</span>，由 <span class="mono">send_llm_request</span> 串起来。无论底下是哪家，最后吐出来的都是 OpenAI 形状的 <span class="mono">ChatCompletionResponse</span>。</p>
</div>
<p>所以本课其实就讲三件环环相扣的事：<strong>工厂怎么选 client</strong>、<strong>三方法怎么干活</strong>、<strong>为什么大家最后都长成 OpenAI 的样子</strong>。下面逐个拆开。</p>
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
<h2>三方法契约</h2>
<p>选好 client 之后，真正干活的是它从 <span class="mono">LLMClientBase</span> 继承来的三个方法。把它们竖着排开看，就是一条很顺的三步流水线：组请求 → 发请求 → 转形状。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>build_request_data</h4><p>把消息、工具、配置组装成<strong>这一家</strong>认得的请求体。同步方法，返回一个 dict。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>request_async</h4><p>把请求体发出去，拿回这一家的<strong>原始响应</strong>。async 方法，返回一个 dict。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>convert_response_to_chat_completion</h4><p>把原始响应<strong>翻译成 OpenAI 形状</strong>的 ChatCompletionResponse。async 方法。</p></div></div>
</div>
<p>这三步谁来串？是 <span class="mono">send_llm_request</span>——它名字里没带 async，<strong>实际却是个 async 方法</strong>，依次调用三方法，并把任何一步抛出的异常都交给 <span class="mono">handle_llm_error</span> 兜底。</p>
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
<div class="cute"><div class="row"><span class="emoji">🔌🔌🔌</span><span class="lab">各家响应</span><span class="arrow">→</span><span class="emoji">🟢</span><span class="bubble">统一插座</span></div><div class="cap">不同形状的插头 → 转接 → 一个统一插座（OpenAI 形状）：循环只读这一种</div></div>
<h2>LLMConfig：每个 agent 带的"连接配置"</h2>
<p>工厂要拿到 <span class="mono">model_endpoint_type</span>，这个值究竟从哪来？来自每个 agent 随身携带的 <span class="mono">LLMConfig</span>——一张写着"连这家、用这个模型、窗口多大"的连接配置卡。</p>
<div class="cellgroup"><div class="cg-cap"><b>LLMConfig 关键字段</b></div><div class="cells"><span class="cell hl">model_endpoint_type</span><span class="sep">·</span><span class="cell">model</span><span class="sep">·</span><span class="cell">model_endpoint</span><span class="sep">·</span><span class="cell">context_window</span><span class="sep">·</span><span class="cell">put_inner_thoughts_in_kwargs</span><span class="sep">·</span><span class="cell">max_tokens</span><span class="sep">·</span><span class="cell">enable_reasoner</span></div></div>
<div class="note info"><span class="ni">💡</span><span class="nx">这张卡挂在 <span class="mono">AgentState.llm_config</span> 上（回扣第 13 课）。整个 <span class="mono">LLMConfig</span> 类<strong>已被标记弃用</strong>、导向 <span class="mono">ModelSettings</span>，但它仍是工厂与基类正在消费的活抽象；其中 <span class="mono">model_endpoint_type</span> 就是驱动分派的那一项。</span></div>
<p>把这一串顺下来看就通了：<span class="mono">AgentState</span> 带着 <span class="mono">LLMConfig</span>，循环从中取出 <span class="mono">model_endpoint_type</span> 递给工厂，工厂据此造出 client，client 再用其余字段（<span class="mono">model_endpoint</span>、<span class="mono">context_window</span>、<span class="mono">max_tokens</span>…）去拼这一家的请求。一条线就接通了。</p>
<p>也正因如此，"换一家供应商"在 Letta 里往往只是<strong>换一份 <span class="mono">LLMConfig</span></strong>：把 <span class="mono">model_endpoint_type</span> 和 <span class="mono">model_endpoint</span> 一改，工厂自然分派到另一个 client，循环代码一行都不用动。</p>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>这是一节把<strong>"适配器模式"开到极致</strong>的课。第 13 到 16 课那套循环，从头到尾不知道自己在跟谁说话——秘诀只有一句：<strong>选定一种数据形状当"普通话"，让每个 provider 把自己翻译成它</strong>。</p>
<p>于是 Anthropic 的内容块、Google 的 <span class="mono">functionCall</span>、本地模型吐的纯文本，最后都收敛成同一个 <span class="mono">ChatCompletionResponse</span>，循环读它就行。想加第二十家供应商？写一个子类、实现三个方法，循环一行都不用改。</p>
<p>更"投降式"的一手，是那个默认 <span class="mono">case _ → OpenAIClient</span>：既然行业早已把 OpenAI 的形状奉为事实标准，Letta 干脆把"OpenAI 兼容"设成<strong>默认假设</strong>。这也呼应第 14 课循环消费 <span class="mono">usage</span> 与响应、以及第 12、14 课里 <span class="mono">handle_llm_error</span> 把上下文超限映射成 <span class="mono">ContextWindowExceededError</span>。</p>
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
<!--ZHMORE-->
""", "en": r"""<p>stub</p>"""}
