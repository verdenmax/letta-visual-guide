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
<!--ZHMORE-->
""", "en": r"""<p>stub</p>"""}
