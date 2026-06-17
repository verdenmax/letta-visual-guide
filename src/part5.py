"""Part 5 · The tool system — lessons 17-20."""

LESSON_17 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第 4 课说"工具是 agent 伸向世界的手"——它让模型不只是"说话"，还能"做事"。但我们一直没回答一个最朴素的问题：<strong>一个工具到底是什么</strong>？它是个类吗？是个插件吗？是某种注册表里的配置吗？</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">答案出人意料地简单：<strong>一个工具就是一个普通的 Python 函数，加上它的 docstring</strong>。更关键的是——模型从来看不到你的函数体，它看到的是从"函数签名 + docstring"自动生成的一份 JSON schema。你写的 docstring，就是模型眼里这个工具的全部说明书。</p>
<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>把工具想成餐厅点菜。<strong>厨房</strong>（你的函数体、真正干活的代码）顾客永远进不去、也看不见。<strong>顾客</strong>（模型）手里只有一张<strong>菜单</strong>——上面写着菜名、一句描述、有哪些可选项。</p>
<p>模型点菜，靠的全是这张菜单。菜单上写"宫保鸡丁（微辣，可选不要花生）"，它就能点对；要是菜单只写"鸡肉类"、连辣不辣、能不能去花生都不说，顾客只能瞎猜，自然容易点错。这张菜单，就是 <span class="mono">generate_schema</span> 从你的 docstring 拼出来的 JSON schema。</p>
</div>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>工具 = 函数</strong>。Letta 在 <span class="mono">letta/functions/schema_generator.py::generate_schema</span> 里，用 <span class="mono">inspect.signature</span> 读出函数的参数与类型注解，再用 <span class="mono">docstring_parser</span>（按 Google 风格）解析 docstring，把两者拼成一份 OpenAI 兼容的 JSON schema。模型只认这份 schema。</p>
<p>所以这一课其实在讲三件环环相扣的事：① schema 是<strong>怎么生成</strong>的；② docstring 为什么是一份<strong>硬契约</strong>（写不全工具就建不出来）；③ Python 类型<strong>怎么映射</strong>成 JSON schema 类型。把这三点串起来，你就懂了"工具"在 Letta 里的真身。</p>
</div>
<h2>工具就是一个 Python 函数</h2>
<p>先看一个真实的基础工具——<span class="mono">send_message</span>，它来自 <span class="mono">letta/functions/function_sets/base.py</span>。这就是 agent 用来"说话"的工具。注意它没有任何特殊基类、没有装饰器，就是一个再普通不过的方法。它身上唯一"特殊"的东西，是那段写得规规矩矩的 Google 风 docstring。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/base.py</span><span class="ln">一个基础工具的样子</span></div>
<pre><span class="kw">def</span> <span class="fn">send_message</span>(self, message: str) -&gt; Optional[str]:
    <span class="st">&quot;&quot;&quot;</span>
<span class="st">    Sends a message to the human user.</span>
<span class="st">    Args:</span>
<span class="st">        message (str): Message contents. All unicode (including emojis) are supported.</span>
<span class="st">    Returns:</span>
<span class="st">        Optional[str]: None is always returned as this function does not produce a response.</span>
<span class="st">    &quot;&quot;&quot;</span>
</pre></div>
<p>关键点在 <span class="mono">Args:</span> 段：里面对 <span class="mono">message</span> 写的那句"Message contents. All unicode…"，<strong>就是模型将来看到的参数说明</strong>。函数体长什么样、返回什么，模型一概不知；它能依据的只有这段描述。</p>
<h2>从函数到 schema：generate_schema</h2>
<div class="flow">
  <div class="node"><div class="nt">Python 函数</div><div class="nd">签名 + docstring</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">generate_schema</div><div class="nd">inspect.signature + docstring_parser</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">OpenAI JSON schema</div><div class="nd">name / description / parameters</div></div>
</div>
<p>整条流水线的核心就在 <span class="mono">letta/functions/schema_generator.py::generate_schema</span>。它做的事可以拆成几步：用 <span class="mono">inspect.signature</span> 拿到每个参数和它的类型注解；用 <span class="mono">docstring_parser</span> 解析 docstring，从中取出每个参数的描述文字；逐个参数把"类型 + 描述"塞进 schema 的 <span class="mono">properties</span>，并判断它该不该进 <span class="mono">required</span>。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/schema_generator.py</span><span class="ln">generate_schema 核心（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">generate_schema</span>(function, name=<span class="kw">None</span>, ...):
    sig = inspect.<span class="fn">signature</span>(function)
    doc = <span class="fn">parse</span>(function.__doc__)        <span class="cm"># docstring_parser, Google 风</span>
    <span class="kw">for</span> p <span class="kw">in</span> sig.parameters.values():
        <span class="kw">if</span> p.name <span class="kw">in</span> [<span class="st">"self"</span>, <span class="st">"agent_state"</span>]: <span class="kw">continue</span>   <span class="cm"># 保留参数，跳过</span>
        desc = next((d.description <span class="kw">for</span> d <span class="kw">in</span> doc.params <span class="kw">if</span> d.arg_name == p.name), <span class="kw">None</span>)
        <span class="kw">if</span> <span class="kw">not</span> desc:
            <span class="kw">raise</span> <span class="fn">ValueError</span>(<span class="st">f"Parameter '{p.name}' lacks a description in the docstring"</span>)
        props[p.name] = <span class="fn">type_to_json_schema_type</span>(p.annotation)
        <span class="kw">if</span> p.default <span class="kw">is</span> inspect.Parameter.empty <span class="kw">and</span> <span class="kw">not</span> is_optional(p.annotation):
            required.append(p.name)
</pre></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">这段循环藏着两道"质检关卡"：参数<strong>没有描述</strong>就 <span class="mono">raise ValueError</span>；参数<strong>缺类型注解</strong>则在 <span class="mono">type_to_json_schema_type</span> 里抛 <span class="mono">TypeError</span>。换句话说，docstring 写不全，工具根本建不出来。</span></div>
<!--ZHMORE-->
""", "en": r"""<p>stub</p>"""}
