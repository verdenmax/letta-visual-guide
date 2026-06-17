"""Part 5 · The tool system — lessons 17-20."""

LESSON_17 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第 4 课说"工具是 agent 伸向世界的手"——它让模型不只是"说话"，还能"做事"。但我们一直没回答一个最朴素的问题：<strong>一个工具到底是什么</strong>？它是个类吗？是个插件吗？是某种注册表里的配置吗？</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">答案出人意料地简单：<strong>一个工具就是一个普通的 Python 函数，加上它的 docstring</strong>。更关键的是——模型从来看不到你的函数体，它看到的是从"函数签名 + docstring"自动生成的一份 JSON schema。你写的 docstring，就是模型眼里这个工具的全部说明书。</p>
<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>把工具想成餐厅点菜。<strong>厨房</strong>（你的函数体、真正干活的代码）顾客永远进不去、也看不见。<strong>顾客</strong>（模型）手里只有一张<strong>菜单</strong>——上面写着菜名、一句描述、有哪些可选项。</p>
<p>模型点菜，靠的全是这张菜单。菜单上写"宫保鸡丁（微辣，可选不要花生）"，它就能点对；要是菜单只写"鸡肉类"、连辣不辣、能不能去花生都不说，顾客只能瞎猜，自然容易点错。这张菜单，就是 <span class="mono">generate_schema</span> 从你的 docstring 拼出来的 JSON schema。</p>
</div>
<p>这个类比还能再推一步：菜单不光决定顾客点什么，也决定他<strong>敢不敢点</strong>。描述越具体，模型越有把握调用；描述越含糊，它要么不敢用、要么乱用。后面会看到，Letta 索性用代码强制你把"菜名"写清楚。</p>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>工具 = 函数</strong>。Letta 在 <span class="mono">letta/functions/schema_generator.py::generate_schema</span> 里，用 <span class="mono">inspect.signature</span> 读出函数的参数与类型注解，再用 <span class="mono">docstring_parser</span>（按 Google 风格）解析 docstring，把两者拼成一份 OpenAI 兼容的 JSON schema。模型只认这份 schema。</p>
<p>所以这一课其实在讲三件环环相扣的事：① schema 是<strong>怎么生成</strong>的；② docstring 为什么是一份<strong>硬契约</strong>（写不全工具就建不出来）；③ Python 类型<strong>怎么映射</strong>成 JSON schema 类型。把这三点串起来，你就懂了"工具"在 Letta 里的真身。而这三点共同的地基，正是那句会反复出现的话：<strong>模型只认 schema</strong>。</p>
</div>
<p>开始之前先对齐一个预期：这一课不教你怎么"用"工具，而是带你看清工具的<strong>构造</strong>。搞懂了构造，你之后写自定义工具、排查"模型为什么不调用我的工具"，才真正有抓手。</p>
<p>在动手看代码前，先建立一个核心对照：同一个工具，<strong>你</strong>和<strong>模型</strong>看到的是两样完全不同的东西。你面对的是有逻辑、有实现的函数；模型面对的只是一张抽象的"接口卡片"。</p>
<div class="cols">
  <div class="col"><h4>👩‍💻 你写的（给人看）</h4><p>完整的 Python 函数：参数、类型注解、docstring，以及真正干活的<strong>函数体</strong>。你关心它怎么实现、会不会出错、返回什么。</p></div>
  <div class="col"><h4>🤖 模型看到的（给机器读）</h4><p>一份 JSON schema：只有名字、一句描述、每个参数的类型与说明。<strong>函数体被完全抹掉</strong>，模型既看不到实现，也无从知道你内部怎么处理。</p></div>
</div>
<p>这条"分界线"贯穿全课：左边是实现细节，右边是对外契约。<span class="mono">generate_schema</span> 干的活，就是把左边<strong>提炼</strong>成右边。理解了这一点，后面所有规则——为什么参数必须有描述、为什么类型有限制——都会变得顺理成章。</p>
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
<p>为什么 Letta 不搞一套"工具基类"或装饰器，偏要用裸函数？因为这样<strong>门槛最低</strong>：任何一个普通函数——你写的、第三方库里的、临时拼的——只要 docstring 规范，就能直接变成工具。用<strong>约定</strong>代替了<strong>配置</strong>。</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Google 风 docstring 的三段式很重要：开头一句是<strong>函数总描述</strong>，<span class="mono">Args:</span> 段逐个写<strong>参数描述</strong>，<span class="mono">Returns:</span> 段写返回值。其中只有"总描述"和"每个参数描述"会进 schema；<span class="mono">Returns:</span> 主要是给人看的。</span></div>
<p>所以你写 docstring 时，真正"对模型生效"的就两处：第一句，和 <span class="mono">Args:</span> 里的每一行。把力气花在这两处，远比纠结 <span class="mono">Returns:</span> 的措辞更划算。</p>
<p>还有一点值得知道：Letta 的内置工具按用途分组放在 <span class="mono">letta/functions/function_sets/</span> 下（基础工具、记忆工具等），但<strong>不论哪一组</strong>，最终都走同一个 <span class="mono">generate_schema</span>。也就是说，内置工具和你自定义的工具，在模型眼里没有身份差别——都只是一份 schema。</p>
<div class="note info"><span class="ni">👉</span><span class="nx">生成出的 schema 不会每次现算，而是<strong>持久化</strong>在 Tool 对象上（<span class="mono">json_schema</span> 字段）：注册时算一次、存起来，之后拼进上下文窗口直接复用。这也是为什么 docstring 一旦写定，schema 就跟着固定了。</span></div>
<h2>从函数到 schema：generate_schema</h2>
<div class="flow">
  <div class="node"><div class="nt">Python 函数</div><div class="nd">签名 + docstring</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">generate_schema</div><div class="nd">inspect.signature + docstring_parser</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">OpenAI JSON schema</div><div class="nd">name / description / parameters</div></div>
</div>
<p>整条流水线的核心就在 <span class="mono">letta/functions/schema_generator.py::generate_schema</span>。它做的事可以拆成几步：用 <span class="mono">inspect.signature</span> 拿到每个参数和它的类型注解；用 <span class="mono">docstring_parser</span> 解析 docstring，从中取出每个参数的描述文字；逐个参数把"类型 + 描述"塞进 schema 的 <span class="mono">properties</span>，并判断它该不该进 <span class="mono">required</span>。</p>
<p>这里有个关键洞察：<span class="mono">generate_schema</span> 不需要<strong>运行</strong>你的函数，只靠<strong>静态读取</strong>签名和 docstring 就能产出 schema。<span class="mono">inspect</span> 看的是函数的"外形"，从不碰它的"内脏"。记住这点，第 18 课"不运行代码也能建 schema"就不会让你意外。</p>
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
<div class="note warn"><span class="ni">⚠️</span><span class="nx">这段循环藏着两道"质检关卡"：参数<strong>没有描述</strong>就 <span class="mono">raise ValueError</span>；参数<strong>缺类型注解</strong>则由 <span class="mono">generate_schema</span> 直接抛 <span class="mono">TypeError</span>。换句话说，docstring 写不全，工具根本建不出来。</span></div>
<p>把这段循环"读慢一点"：它<strong>逐个参数</strong>走一遍，每个参数都过同样四步——跳过保留名、取描述、定类型、判必填。任何一步出问题，构建就此中止，错误会一路抛到注册工具的调用方。</p>
<div class="note info"><span class="ni">📌</span><span class="nx">注意 <span class="mono">name=None</span> 这个参数：不显式传名字时，schema 的 <span class="mono">name</span> 默认取 <span class="mono">function.__name__</span>，也就是函数名本身。所以给函数起个好名字，等于给工具起了个好"菜名"，模型一看名字就能猜个八九不离十。</span></div>
<p>顺带说说这份 schema 的"出身"：它遵循 OpenAI 的 function-calling 规范——顶层是 <span class="mono">name</span> 和 <span class="mono">description</span>，参数统一包在 <span class="mono">parameters</span> 里，且 <span class="mono">type</span> 恒为 <span class="mono">object</span>。各家主流模型大多兼容这套格式，于是 Letta 拿它当"通用语"，一份 schema 喂给不同模型都能认。</p>
<p>那这台机器最终"吐"出来的成品长什么样？下面就是 <span class="mono">send_message</span> 经 <span class="mono">generate_schema</span> 处理后得到的 JSON schema。对照前面的函数：函数名变成 <span class="mono">name</span>，docstring 第一句变成 <span class="mono">description</span>，参数 <span class="mono">message</span> 连同它的描述进了 <span class="mono">properties</span>，因为没有默认值又被列进 <span class="mono">required</span>。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">生成结果 · JSON schema</span><span class="ln">模型真正看到的东西</span></div>
<pre>{
  <span class="st">"name"</span>: <span class="st">"send_message"</span>,
  <span class="st">"description"</span>: <span class="st">"Sends a message to the human user."</span>,
  <span class="st">"parameters"</span>: {
    <span class="st">"type"</span>: <span class="st">"object"</span>,
    <span class="st">"properties"</span>: {
      <span class="st">"message"</span>: {
        <span class="st">"type"</span>: <span class="st">"string"</span>,
        <span class="st">"description"</span>: <span class="st">"Message contents. All unicode (including emojis) are supported."</span>
      }
    },
    <span class="st">"required"</span>: [<span class="st">"message"</span>]
  }
}
</pre></div>
<div class="note tip"><span class="ni">👉</span><span class="nx">把这份 JSON 和最前面那段 Python 对照着看：你会发现里面<strong>每一个字</strong>都来自函数签名或 docstring，没有一处是凭空多出来的。这就是"docstring 即说明书"的字面含义。</span></div>
<p>不管工具多复杂，生成出的 schema 永远是同一副"骨架"。把它拆开看，就这么几个固定零件：</p>
<div class="cellgroup"><div class="cg-cap"><b>一份工具 schema 的解剖</b></div>
<div class="cells">
<span class="cell hl">name</span><span class="sep">·</span>
<span class="cell hl">description</span><span class="sep">·</span>
<span class="cell">parameters.type = object</span><span class="sep">·</span>
<span class="cell">properties（逐参数：type + description）</span><span class="sep">·</span>
<span class="cell">required（必填参数名列表）</span>
</div></div>
<p>蓝色高亮的 <span class="mono">name</span> 和 <span class="mono">description</span> 来自函数名与第一句 docstring；<span class="mono">properties</span> 里每个参数对应一组"类型 + 描述"；<span class="mono">required</span> 则是必填判定链的产物。记住这副骨架，你看任何工具的 schema 都不会迷路。</p>
<p>顺便破除一个误解：schema 里<strong>没有</strong>你的函数返回类型，也没有函数体的任何信息。<span class="mono">Returns:</span> 那段、你精心写的实现，模型统统看不到。它能依据的，永远只有这副"名字 + 描述 + 参数"的骨架。</p>
<h2>类型怎么映射</h2>
<p>schema 里每个参数都得有个 <span class="mono">type</span>，这一步由 <span class="mono">type_to_json_schema_type</span> 完成：它把 Python 的类型注解<strong>手写</strong>地翻译成 JSON schema 类型。这张映射表就是工具能接受哪些参数类型的边界——表里没有的，要么被解包、要么直接报错。</p>
<table class="t">
<tr><th>Python 类型</th><th>JSON schema</th><th>备注</th></tr>
<tr><td class="mono">str</td><td class="mono">string</td><td>最常见</td></tr>
<tr><td class="mono">int</td><td class="mono">integer</td><td>整数</td></tr>
<tr><td class="mono">bool</td><td class="mono">boolean</td><td>真/假</td></tr>
<tr><td class="mono">float</td><td class="mono">number</td><td>浮点</td></tr>
<tr><td class="mono">Optional[X]</td><td class="mono">X</td><td>解包成 X，并移出 required</td></tr>
<tr><td class="mono">List[X]</td><td class="mono">array</td><td>带 items 类型</td></tr>
<tr><td class="mono">Literal[...]</td><td class="mono">string + enum</td><td>枚举可选值</td></tr>
<tr><td class="mono">BaseModel</td><td class="mono">object</td><td>调 model_json_schema()</td></tr>
<tr><td class="mono">Dict[k,v]</td><td class="mono">✗</td><td>带参字典 → ValueError</td></tr>
<tr><td class="mono">Union[...]</td><td class="mono">✗</td><td>一般 Union → NotImplementedError</td></tr>
</table>
<p>这张表里最值得记住的是三类"特殊待遇"。<span class="mono">Optional[X]</span> 会被<strong>解包</strong>：schema 里类型就是 <span class="mono">X</span>，但该参数自动变成可选。<span class="mono">List[X]</span> 映射成 <span class="mono">array</span> 并带上 <span class="mono">items</span> 描述元素类型。<span class="mono">Literal</span> 则变成 <span class="mono">enum</span>，把可选值直接写进 schema，等于告诉模型"只能从这几个里挑"。</p>
<div class="note tip"><span class="ni">💡</span><span class="nx">想传一个结构化对象（比如一组配置项）？别用 <span class="mono">Dict</span>，定义一个 Pydantic <span class="mono">BaseModel</span>。<span class="mono">type_to_json_schema_type</span> 会调它的 <span class="mono">model_json_schema()</span>，把字段、类型、必填关系<strong>嵌套</strong>进工具 schema——既结构清晰，又能被模型正确理解。</span></div>
<p>这些映射大多是<strong>递归</strong>的：<span class="mono">List[Optional[int]]</span> 会先解外层 list、再解内层 Optional，最终得到一个"元素可空的整数数组"。正因为是手写分支、逐层处理，Letta 才能精确控制每种类型翻成什么，也才会对处理不了的类型（带参 Dict、任意 Union）明确报错，而不是默默糊弄过去。</p>
<p>注意 <span class="mono">Optional[X]</span> 这一行很特别：它不只是映射类型，还会影响"该参数是否必填"。这就引出了 <span class="mono">required</span> 的判定逻辑——一个参数到底进不进 <span class="mono">required</span>，走的是下面这条小决策链。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>有默认值吗？</h4><p>若该参数在签名里写了默认值（<span class="mono">p.default</span> 不为空）→ <strong>可选</strong>，不进 required。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>是 Optional[X] 吗？</h4><p>没有默认值，但类型是 <span class="mono">Optional[X]</span>（即 <span class="mono">is_optional</span> 为真）→ <strong>可选</strong>，不进 required。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>否则</h4><p>既无默认值、又不是 Optional → <strong>进 required</strong>，模型调用时必须提供。</p></div></div>
</div>
<p>别小看 <span class="mono">required</span> 这份清单——它直接左右模型的行为。被列进 required 的参数，模型调用时<strong>必须</strong>给出；留在外面的，它可以省略。所以"哪些必填"既是正确性约束，也是对模型的提示。</p>
<div class="note tip"><span class="ni">✅</span><span class="nx">一个实用习惯：凡是"缺了就没法干活"的参数，别给默认值、也别标 <span class="mono">Optional</span>，让它进 required；凡是"锦上添花"的参数，给个默认值或用 <span class="mono">Optional</span>，让模型可以不填。这条边界，决定了工具好不好用。</span></div>
<h2>进阶：用 Pydantic 模型当参数</h2>
<p>当一个参数本身是"一组字段"——比如一封邮件草稿有收件人、主题、正文——与其把它摊平成三个零散参数，不如打包成一个 Pydantic 模型，让 schema 自带结构。工具签名里只写一个参数 <span class="mono">draft: EmailDraft</span> 就够了。</p>
<div class="note tip"><span class="ni">💡</span><span class="nx"><span class="mono">generate_schema</span> 遇到 <span class="mono">draft: EmailDraft</span>，会调用 <span class="mono">EmailDraft.model_json_schema()</span>，把 <span class="mono">to / subject / body</span> 连同它们的类型与必填关系，作为一个<strong>嵌套 object</strong> 塞进工具 schema。</span></div>
<p>这样一来，模型看到的是一个结构清晰的对象，而不是三个互不相干的字符串。更妙的是：字段的增删、类型的约束，全集中在模型定义里，工具签名始终保持干净。这正是为什么遇到结构化入参，官方推荐 Pydantic 模型而非 <span class="mono">Dict</span>。</p>
<div class="note info"><span class="ni">📌</span><span class="nx">小结类型这一块：能用基础类型就用基础类型，要"可选"用 <span class="mono">Optional</span>，要"多选一"用 <span class="mono">Literal</span>，要"一组字段"用 Pydantic 模型——避开带参 <span class="mono">Dict[k,v]</span> 和一般 <span class="mono">Union</span>，你就绕开了绝大多数报错。</span></div>
<div class="cute"><div class="row">
  <span class="emoji">📝</span><span class="lab">docstring</span>
  <span class="emoji">🔧</span><span class="lab">函数</span>
  <span class="arrow">→</span>
  <span class="emoji">📜</span><span class="lab">schema</span>
  <span class="arrow">→</span>
  <span class="emoji">🤖</span><span class="bubble">我只看菜单</span>
</div><div class="cap">模型从不读你的函数体，只读 generate_schema 拼出的那份 schema。</div></div>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>这里有个容易被忽略的视角转换：<strong>docstring 不是写给人看的注释，而是写给"模型"的 API 文档</strong>。模型决定要不要调这个工具、怎么填参数，全部依据就是这份 schema——而 schema 的描述文字，逐字来自你的 docstring。</p>
<p>所以一句含糊或缺失的参数描述，会<strong>直接降低</strong>模型用对工具的概率。这是功能问题，不是代码风格问题。Letta 索性把它升级成"编译期错误"：任一参数缺描述，<span class="mono">generate_schema</span> 当场 <span class="mono">raise ValueError</span>，工具压根建不出来，逼你把话说清楚。</p>
<p>一句话记住：<strong>给模型写 docstring，而不是给同事写</strong>。这正好回扣第 4 课——工具是 agent 与世界的接口，而接口的质量，就压在这几行描述上。</p>
</div>
<h2>好 docstring vs 坏 docstring</h2>
<p>抽象的话讲多了，不如看个对比。同一个"发邮件"工具，两种写法，对模型的效果天差地别：</p>
<div class="cols">
  <div class="col"><h4>🙁 含糊的写法</h4><p><span class="mono">to (str): 收件人。</span> 模型只知道要传个字符串，但该填邮箱、姓名、还是用户 ID？它只能猜，猜错就发错人。</p></div>
  <div class="col"><h4>🙂 清楚的写法</h4><p><span class="mono">to (str): 收件人的完整邮箱地址，如 alice@example.com。</span> 模型一眼就懂格式和示例，几乎不会填错。</p></div>
</div>
<p>注意：两种写法<strong>代码一模一样</strong>，函数体一字没改，差别只在 docstring。这正是为什么说参数描述是"功能"而非"风格"——它实打实地改变了模型用对工具的概率。一句好描述，胜过事后无数次纠错。</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">很多人把 docstring 当成"事后补的文档"，写得敷衍。但在 Letta 里它是<strong>运行时的一部分</strong>：写得好，模型用得准；写得差，再聪明的模型也救不回来。请把它当代码一样认真对待。</span></div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<ul>
<li><strong>函数级描述可以缺，参数描述不能缺。</strong>整个工具没写一句话的总描述？没关系，会回退成 <span class="mono">"No description available"</span>。但<strong>每个参数</strong>必须有描述（否则 <span class="mono">ValueError</span>）和类型注解（否则 <span class="mono">TypeError</span>）。</li>
<li><strong>不是所有类型都支持。</strong>带参数的 <span class="mono">Dict[k,v]</span> 会 <span class="mono">ValueError</span>，一般的 <span class="mono">Union</span> 会 <span class="mono">NotImplementedError</span>。需要结构化入参时，改用 Pydantic <span class="mono">BaseModel</span>。</li>
<li><strong>self / agent_state 是保留参数。</strong>它们属于 <span class="mono">TOOL_RESERVED_KWARGS</span>，会被直接跳过，<strong>不进</strong> schema——模型看不到、也不用填。</li>
<li><strong>request_heartbeat 不在这里加。</strong>它不是由 <span class="mono">generate_schema</span> 注入的，而是运行时另行附加（见第 15 课）。别在 docstring 里手写它。</li>
<li><strong>别在 docstring 里描述 self / agent_state。</strong>它们根本不进 schema，写了也是白写，反而可能干扰解析。只描述模型真正要填的那些参数就好。</li>
</ul>
</div>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<strong>一条主线，几个锚点。</strong>生成器是 <span class="mono">letta/functions/schema_generator.py::generate_schema(function, name=None, …)</span>——内部 <span class="mono">inspect.signature</span> 取签名、<span class="mono">docstring_parser.parse</span> 读 Google 风 docstring、手写的 <span class="mono">type_to_json_schema_type</span> 做类型映射。逐参数的硬校验也在这里：缺描述 <span class="mono">raise ValueError</span>、缺注解 <span class="mono">TypeError</span>；而 <span class="mono">validate_google_style_docstring</span> 只是<strong>告警</strong>（其 <span class="mono">ValueError</span> 被 catch 成 warning）。保留参数清单是 <span class="mono">letta/constants.py::TOOL_RESERVED_KWARGS = ["self", "agent_state"]</span>。示例 docstring 看 <span class="mono">letta/functions/function_sets/base.py</span>（<span class="mono">send_message</span> / <span class="mono">archival_memory_insert</span> 等）。顺着这串符号读，你能把"函数 → schema"完整走通。
</div>
<h2>再挖深一点</h2>
<p>上面是主线。下面四个抽屉，专门给想抠细节的你——每个都按"示例 / 为什么 / 源码"展开。不想深究可以直接跳到本课要点。</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">读这几个抽屉时抓住一条主线：<strong>凡是模型能看到的，都来自 docstring 与签名；凡是模型看不到的（self、函数体、运行时参数），都不归 generate_schema 管。</strong>抓住这条线，零碎的细节就有了归处。</span></div>
<details class="accordion"><summary>① 为什么说 docstring 是"契约"，而不只是注释？</summary><div class="acc-body">
<p><strong>示例：</strong>你把 <span class="mono">message</span> 的描述删掉，函数照样能跑、单元测试照过，但这个工具<strong>注册不进 Letta</strong>。</p>
<p><strong>为什么：</strong>因为模型从头到尾<strong>只见 schema、不见代码</strong>。代码注释写得再好，进不了 schema 就等于不存在；而 schema 的参数描述只能来自 docstring。docstring 因此从"可有可无的注释"升级成"必须履行的契约"。更进一步说：模型对参数的全部理解都来自这句描述，描述一含糊，它的猜测就开始发散，调用成功率随之下滑。</p>
<p><strong>源码：</strong><span class="mono">letta/functions/schema_generator.py::generate_schema</span> 在循环里逐个参数取描述，取不到就 <span class="mono">raise ValueError</span>，把违约挡在构建阶段。</p>
</div></details>
<details class="accordion"><summary>② 类型映射的边界在哪？Dict / Union 为什么不行？</summary><div class="acc-body">
<p><strong>示例：</strong><span class="mono">Optional[str]</span> 会被解包成 <span class="mono">string</span> 并移出 required；但 <span class="mono">Dict[str, int]</span> 直接报错，<span class="mono">Union[int, str]</span> 也报错。</p>
<p><strong>为什么：</strong>JSON schema 需要明确、可校验的结构。带键值类型的 <span class="mono">Dict</span> 和任意 <span class="mono">Union</span> 难以无歧义地表达，于是 Letta 选择"宁可报错也不猜"。要传结构化对象，就定义一个 Pydantic <span class="mono">BaseModel</span>。毕竟一份模糊的 schema 还不如没有——它只会诱导模型一错再错。</p>
<p><strong>源码：</strong><span class="mono">letta/functions/schema_generator.py::type_to_json_schema_type</span> 手写处理各分支；遇到 <span class="mono">BaseModel</span> 时调用其 <span class="mono">model_json_schema()</span> 得到嵌套 object。</p>
</div></details>
<details class="accordion"><summary>③ self / agent_state 和 request_heartbeat 有什么区别？</summary><div class="acc-body">
<p><strong>示例：</strong>一个工具签名写成 <span class="mono">def foo(self, agent_state, x: int)</span>，最终 schema 里只有 <span class="mono">x</span>。运行时模型还可能"看到"一个 <span class="mono">request_heartbeat</span> 参数，但它不在这段代码里。</p>
<p><strong>为什么：</strong><span class="mono">self</span>/<span class="mono">agent_state</span> 是<strong>构建期</strong>的保留参数——它们由运行时框架注入，不该让模型填，所以在生成 schema 时被跳过。而 <span class="mono">request_heartbeat</span> 是<strong>运行期</strong>才附加的控制参数（决定要不要继续循环），由别处注入，不归 <span class="mono">generate_schema</span> 管。一句话：一个是"构建期就该隐藏"，一个是"运行期才需附加"，两者的生命周期完全不同。</p>
<p><strong>源码：</strong>保留名记录在 <span class="mono">TOOL_RESERVED_KWARGS</span>，<span class="mono">generate_schema</span> 遇到就 <span class="mono">continue</span>；<span class="mono">request_heartbeat</span> 的注入见第 15 课的执行循环。</p>
</div></details>
<details class="accordion"><summary>④ Google 风格校验失败，工具一定建不出来吗？</summary><div class="acc-body">
<p><strong>示例：</strong>docstring 格式略不标准（比如 <span class="mono">Args:</span> 缩进不规整），你可能只在日志里看到一条 warning，工具<strong>仍然</strong>建得出来。</p>
<p><strong>为什么：</strong>这里有"软硬两道关"。Google 风格的整体校验是<strong>软</strong>的——它的 <span class="mono">ValueError</span> 被 <span class="mono">try/except</span> 捕获后降级成 <span class="mono">logger.warning</span>，不会中断。真正<strong>硬</strong>挡人的，是循环里逐参数的"有没有描述、有没有类型注解"检查，那两个错误不会被吞。所以记住分量：格式不够标准顶多是"提醒"，参数没描述、没注解才是真正拦你的"硬伤"。</p>
<p><strong>源码：</strong>软校验在 <span class="mono">letta/functions/schema_generator.py::validate_google_style_docstring</span>，其异常被上层 catch 成告警；硬检查仍在 <span class="mono">generate_schema</span> 主循环里。</p>
</div></details>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li><strong>工具 = 函数</strong>：没有特殊基类，普通 Python 函数加规范 docstring 即可。</li>
<li><strong>generate_schema(签名 + docstring) → JSON schema</strong>：用 <span class="mono">inspect.signature</span> + <span class="mono">docstring_parser</span> 自动生成。</li>
<li><strong>模型只看 schema，不看代码</strong>：函数体对模型完全不可见。</li>
<li><strong>每个参数的描述 + 类型注解是硬契约</strong>：缺描述 <span class="mono">ValueError</span>，缺注解 <span class="mono">TypeError</span>。</li>
<li><strong>类型映射是手写的</strong>：str/int/bool/float/Optional/List/Literal/BaseModel 支持，带参 Dict 与一般 Union 报错。</li>
<li><strong>self / agent_state 保留</strong>：属 <span class="mono">TOOL_RESERVED_KWARGS</span>，不进 schema。</li>
<li><strong>schema 会持久化</strong>：存在 Tool 的 <span class="mono">json_schema</span> 字段，注册时算一次、之后复用。</li>
</ul>
</div>
<p>把这一课倒过来想会更清楚：你<strong>不是</strong>在"写一个函数、顺便加注释"，而是在"写一份给模型的接口说明、顺便实现它"。视角一转，docstring 的每个字都有了分量。签名给出接口的形状，docstring 给出接口的语义，两者合起来，才是模型眼里那个完整可用的工具。</p>
<p>最后留个伏笔。这一课从头到尾都假设了一个前提：<strong>我们手里已经有一个函数对象</strong>，可以让 <span class="mono">inspect</span> 去读它的签名。可现实里，用户常常是上传<strong>一段源码字符串</strong>来注册自定义工具。这时服务端面临一个棘手的要求：要在<strong>绝不运行这段代码</strong>的前提下，仍然把 schema 生成出来。它是怎么做到的？这正是<strong>第 18 课</strong>的主题。</p>
""", "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Lesson 4 said "a tool is the agent's hand reaching out into the world" — it lets the model not just <strong>talk</strong> but <strong>act</strong>. Yet we never answered the most basic question: <strong>what exactly is a tool</strong>? Is it a class? A plugin? Some config sitting in a registry?</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">The answer is surprisingly simple: <strong>a tool is just an ordinary Python function, plus its docstring</strong>. And crucially — the model never sees your function body. What it sees is a JSON schema auto-generated from the "signature + docstring". The docstring you write is, in the model's eyes, this tool's entire instruction manual.</p>
<div class="card analogy"><div class="tag">🔌 Real-world analogy</div>
<p>Think of a tool as ordering at a restaurant. The <strong>kitchen</strong> (your function body, the code that does the real work) is somewhere the customer can never enter or even see. The <strong>customer</strong> (the model) holds only one thing — a <strong>menu</strong> — listing dish names, a one-line description, and which options are available.</p>
<p>The model orders entirely off this menu. If the menu says "Kung Pao chicken (mildly spicy, peanuts optional)", it can order correctly; if the menu only says "a chicken dish" — silent on spice or peanuts — the customer can only guess, and naturally gets it wrong. This menu is exactly the JSON schema that <span class="mono">generate_schema</span> stitches together from your docstring.</p>
</div>
<p>The analogy stretches one step further: the menu decides not only <strong>what</strong> the customer orders, but <strong>whether they dare to order at all</strong>. The more specific the description, the more confident the model is to call it; the vaguer it is, the more it either avoids the tool or misuses it. As we'll see, Letta simply forces you — in code — to spell the "dish name" out clearly.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Grab the lesson in one line: <strong>a tool = a function</strong>. In <span class="mono">letta/functions/schema_generator.py::generate_schema</span>, Letta uses <span class="mono">inspect.signature</span> to read the function's parameters and type annotations, then uses <span class="mono">docstring_parser</span> (Google style) to parse the docstring, and stitches the two into an OpenAI-compatible JSON schema. The model knows only this schema.</p>
<p>So this lesson is really about three interlocking things: ① <strong>how</strong> the schema is generated; ② why the docstring is a <strong>hard contract</strong> (write it incompletely and the tool can't be built); ③ <strong>how</strong> Python types map onto JSON schema types. String these together and you understand what a "tool" truly is in Letta. Their shared foundation is the line that keeps coming back: <strong>the model knows only the schema</strong>.</p>
</div>
<p>Before we start, let's align one expectation: this lesson doesn't teach you how to <strong>use</strong> tools, but takes you to see clearly the <strong>construction</strong> of a tool. Once you understand the construction, writing custom tools later — and debugging "why won't the model call my tool" — finally gives you something to grab onto.</p>
<p>Before touching any code, let's set up a core contrast: for the same tool, <strong>you</strong> and the <strong>model</strong> see two completely different things. You face a function with logic and a real implementation; the model faces only an abstract "interface card".</p>
<div class="cols">
  <div class="col"><h4>👩‍💻 What you write (for humans)</h4><p>The full Python function: parameters, type annotations, a docstring, and the <strong>function body</strong> that does the real work. You care how it's implemented, whether it can fail, what it returns.</p></div>
  <div class="col"><h4>🤖 What the model sees (for machines)</h4><p>A JSON schema: just a name, a one-line description, and each parameter's type and explanation. The <strong>function body is wiped out entirely</strong>; the model can neither see the implementation nor know how you handle things inside.</p></div>
</div>
<p>This "dividing line" runs through the whole lesson: implementation details on the left, the outward contract on the right. What <span class="mono">generate_schema</span> does is <strong>distill</strong> the left into the right. Grasp this, and every rule that follows — why parameters must have descriptions, why types are restricted — becomes natural.</p>
<h2>A tool is just a Python function</h2>
<p>Let's look at a real basic tool first — <span class="mono">send_message</span>, from <span class="mono">letta/functions/function_sets/base.py</span>. This is the tool the agent uses to "talk". Notice it has no special base class, no decorator — it's just a perfectly ordinary method. The only "special" thing about it is that neatly written Google-style docstring.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/function_sets/base.py</span><span class="ln">what a basic tool looks like</span></div>
<pre><span class="kw">def</span> <span class="fn">send_message</span>(self, message: str) -&gt; Optional[str]:
    <span class="st">&quot;&quot;&quot;</span>
<span class="st">    Sends a message to the human user.</span>
<span class="st">    Args:</span>
<span class="st">        message (str): Message contents. All unicode (including emojis) are supported.</span>
<span class="st">    Returns:</span>
<span class="st">        Optional[str]: None is always returned as this function does not produce a response.</span>
<span class="st">    &quot;&quot;&quot;</span>
</pre></div>
<p>The key is the <span class="mono">Args:</span> section: the line it writes for <span class="mono">message</span>, "Message contents. All unicode…", <strong>is exactly the parameter explanation the model will later see</strong>. What the function body looks like, what it returns — the model has no idea; all it can lean on is this description.</p>
<p>Why doesn't Letta build a "tool base class" or a decorator, insisting on bare functions instead? Because that keeps the <strong>barrier lowest</strong>: any ordinary function — yours, one from a third-party library, something thrown together on the spot — can become a tool the moment its docstring is well-formed. It replaces <strong>configuration</strong> with <strong>convention</strong>.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">The three-part Google-style docstring matters: the opening line is the <strong>function's overall description</strong>, the <span class="mono">Args:</span> section writes each <strong>parameter description</strong> in turn, and the <span class="mono">Returns:</span> section writes the return value. Of these, only the "overall description" and "each parameter description" enter the schema; <span class="mono">Returns:</span> is mainly for humans.</span></div>
<p>So when you write a docstring, only two places actually "take effect on the model": the first line, and every line under <span class="mono">Args:</span>. Spending your effort there pays off far more than agonizing over the wording of <span class="mono">Returns:</span>.</p>
<p>One more thing worth knowing: Letta's built-in tools are grouped by purpose under <span class="mono">letta/functions/function_sets/</span> (base tools, memory tools, and so on), but <strong>no matter which group</strong>, they all run through the same <span class="mono">generate_schema</span> in the end. In other words, built-in tools and your custom tools carry no identity difference in the model's eyes — both are just a schema.</p>
<div class="note info"><span class="ni">👉</span><span class="nx">The generated schema isn't recomputed each time; it is <strong>persisted</strong> on the Tool object (the <span class="mono">json_schema</span> field): computed once at registration, stored, and afterward spliced straight into the context window for reuse. That's also why, once the docstring is settled, the schema is fixed along with it.</span></div>
<h2>From function to schema: generate_schema</h2>
<div class="flow">
  <div class="node"><div class="nt">Python function</div><div class="nd">signature + docstring</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">generate_schema</div><div class="nd">inspect.signature + docstring_parser</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">OpenAI JSON schema</div><div class="nd">name / description / parameters</div></div>
</div>
<p>The core of the whole pipeline sits in <span class="mono">letta/functions/schema_generator.py::generate_schema</span>. What it does breaks into a few steps: use <span class="mono">inspect.signature</span> to get each parameter and its type annotation; use <span class="mono">docstring_parser</span> to parse the docstring and pull out each parameter's description text; then, parameter by parameter, stuff "type + description" into the schema's <span class="mono">properties</span> and decide whether it belongs in <span class="mono">required</span>.</p>
<p>Here's a key insight: <span class="mono">generate_schema</span> never needs to <strong>run</strong> your function — it produces the schema purely by <strong>statically reading</strong> the signature and docstring. <span class="mono">inspect</span> looks at the function's "outline", never touching its "innards". Remember this, and Lesson 18's "build a schema without running the code" won't catch you off guard.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/schema_generator.py</span><span class="ln">generate_schema core (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">generate_schema</span>(function, name=<span class="kw">None</span>, ...):
    sig = inspect.<span class="fn">signature</span>(function)
    doc = <span class="fn">parse</span>(function.__doc__)        <span class="cm"># docstring_parser, Google style</span>
    <span class="kw">for</span> p <span class="kw">in</span> sig.parameters.values():
        <span class="kw">if</span> p.name <span class="kw">in</span> [<span class="st">"self"</span>, <span class="st">"agent_state"</span>]: <span class="kw">continue</span>   <span class="cm"># reserved params, skip</span>
        desc = next((d.description <span class="kw">for</span> d <span class="kw">in</span> doc.params <span class="kw">if</span> d.arg_name == p.name), <span class="kw">None</span>)
        <span class="kw">if</span> <span class="kw">not</span> desc:
            <span class="kw">raise</span> <span class="fn">ValueError</span>(<span class="st">f"Parameter '{p.name}' lacks a description in the docstring"</span>)
        props[p.name] = <span class="fn">type_to_json_schema_type</span>(p.annotation)
        <span class="kw">if</span> p.default <span class="kw">is</span> inspect.Parameter.empty <span class="kw">and</span> <span class="kw">not</span> is_optional(p.annotation):
            required.append(p.name)
</pre></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">This loop hides two "quality gates": a parameter with <strong>no description</strong> triggers <span class="mono">raise ValueError</span>; a parameter <strong>missing its type annotation</strong> makes <span class="mono">generate_schema</span> raise <span class="mono">TypeError</span> directly. Put another way, an incomplete docstring means the tool simply can't be built.</span></div>
<p>Read this loop "a little slower": it walks <strong>each parameter</strong> in turn, and every parameter passes the same four steps — skip the reserved name, fetch the description, fix the type, decide required. If any step goes wrong, construction halts right there, and the error propagates all the way up to whoever is registering the tool.</p>
<div class="note info"><span class="ni">📌</span><span class="nx">Note the <span class="mono">name=None</span> parameter: when you don't pass a name explicitly, the schema's <span class="mono">name</span> defaults to <span class="mono">function.__name__</span>, the function name itself. So giving a function a good name is like giving the tool a good "dish name" — one glance at the name and the model can guess most of it.</span></div>
<p>A word on this schema's "pedigree": it follows OpenAI's function-calling spec — <span class="mono">name</span> and <span class="mono">description</span> at the top, parameters all wrapped under <span class="mono">parameters</span>, and <span class="mono">type</span> fixed to <span class="mono">object</span>. Most mainstream models accept this format, so Letta treats it as a "lingua franca": one schema feeds different models and they all recognize it.</p>
<p>So what does this machine finally "spit out"? Below is the JSON schema that <span class="mono">send_message</span> yields after <span class="mono">generate_schema</span> processes it. Compare it with the earlier function: the function name becomes <span class="mono">name</span>, the docstring's first line becomes <span class="mono">description</span>, the parameter <span class="mono">message</span> together with its description goes into <span class="mono">properties</span>, and because it has no default value it gets listed under <span class="mono">required</span>.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">result · JSON schema</span><span class="ln">what the model actually sees</span></div>
<pre>{
  <span class="st">"name"</span>: <span class="st">"send_message"</span>,
  <span class="st">"description"</span>: <span class="st">"Sends a message to the human user."</span>,
  <span class="st">"parameters"</span>: {
    <span class="st">"type"</span>: <span class="st">"object"</span>,
    <span class="st">"properties"</span>: {
      <span class="st">"message"</span>: {
        <span class="st">"type"</span>: <span class="st">"string"</span>,
        <span class="st">"description"</span>: <span class="st">"Message contents. All unicode (including emojis) are supported."</span>
      }
    },
    <span class="st">"required"</span>: [<span class="st">"message"</span>]
  }
}
</pre></div>
<div class="note tip"><span class="ni">👉</span><span class="nx">Hold this JSON up against the Python from the very start: you'll find <strong>every single word</strong> in it comes from the function signature or docstring — not one piece is conjured out of thin air. That is the literal meaning of "the docstring is the manual".</span></div>
<p>No matter how complex the tool, the generated schema always wears the same "skeleton". Take it apart and it's just these few fixed parts:</p>
<div class="cellgroup"><div class="cg-cap"><b>Anatomy of a tool schema</b></div>
<div class="cells">
<span class="cell hl">name</span><span class="sep">·</span>
<span class="cell hl">description</span><span class="sep">·</span>
<span class="cell">parameters.type = object</span><span class="sep">·</span>
<span class="cell">properties (per param: type + description)</span><span class="sep">·</span>
<span class="cell">required (list of required param names)</span>
</div></div>
<p>The blue-highlighted <span class="mono">name</span> and <span class="mono">description</span> come from the function name and the first docstring line; each parameter in <span class="mono">properties</span> maps to a "type + description" pair; <span class="mono">required</span> is the product of the must-fill decision chain. Memorize this skeleton and you'll never get lost reading any tool's schema.</p>
<p>While we're here, let's bust a misconception: the schema contains <strong>no</strong> return type of your function, and no information about the function body. That <span class="mono">Returns:</span> section, your carefully written implementation — the model sees none of it. All it can ever lean on is this "name + description + parameters" skeleton.</p>
<h2>How types are mapped</h2>
<p>Every parameter in the schema needs a <span class="mono">type</span>, and that step is handled by <span class="mono">type_to_json_schema_type</span>: it <strong>hand-writes</strong> a translation from Python's type annotations into JSON schema types. This mapping table is the boundary of which parameter types a tool can accept — anything not in the table is either unwrapped or rejected outright.</p>
<table class="t">
<tr><th>Python type</th><th>JSON schema</th><th>Notes</th></tr>
<tr><td class="mono">str</td><td class="mono">string</td><td>most common</td></tr>
<tr><td class="mono">int</td><td class="mono">integer</td><td>integers</td></tr>
<tr><td class="mono">bool</td><td class="mono">boolean</td><td>true / false</td></tr>
<tr><td class="mono">float</td><td class="mono">number</td><td>floating point</td></tr>
<tr><td class="mono">Optional[X]</td><td class="mono">X</td><td>unwrapped to X, removed from required</td></tr>
<tr><td class="mono">List[X]</td><td class="mono">array</td><td>carries an items type</td></tr>
<tr><td class="mono">Literal[...]</td><td class="mono">string + enum</td><td>enumerated allowed values</td></tr>
<tr><td class="mono">BaseModel</td><td class="mono">object</td><td>calls model_json_schema()</td></tr>
<tr><td class="mono">Dict[k,v]</td><td class="mono">✗</td><td>parameterized dict → ValueError</td></tr>
<tr><td class="mono">Union[...]</td><td class="mono">✗</td><td>general Union → NotImplementedError</td></tr>
</table>
<p>The three kinds of "special treatment" are the most worth remembering. <span class="mono">Optional[X]</span> gets <strong>unwrapped</strong>: the type in the schema is just <span class="mono">X</span>, but that parameter automatically turns optional. <span class="mono">List[X]</span> maps to <span class="mono">array</span> and carries an <span class="mono">items</span> describing the element type. <span class="mono">Literal</span> becomes <span class="mono">enum</span>, writing the allowed values straight into the schema — in effect telling the model "you may only pick from these".</p>
<div class="note tip"><span class="ni">💡</span><span class="nx">Want to pass a structured object (say a bundle of config options)? Don't use <span class="mono">Dict</span> — define a Pydantic <span class="mono">BaseModel</span>. <span class="mono">type_to_json_schema_type</span> will call its <span class="mono">model_json_schema()</span>, <strong>nesting</strong> the fields, types, and required relations into the tool schema — clear in structure, and correctly understood by the model.</span></div>
<p>These mappings are mostly <strong>recursive</strong>: <span class="mono">List[Optional[int]]</span> first unwraps the outer list, then the inner Optional, finally yielding an "array of nullable integers". Precisely because the branches are hand-written and handled layer by layer, Letta can control exactly what each type translates into — and can clearly error on types it can't handle (parameterized Dict, arbitrary Union) instead of silently fudging them.</p>
<p>Notice that the <span class="mono">Optional[X]</span> row is special: it doesn't only map the type, it also affects "whether the parameter is required". That brings us to the <span class="mono">required</span> decision logic — whether a parameter enters <span class="mono">required</span> follows the little decision chain below.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Does it have a default?</h4><p>If the parameter has a default in the signature (<span class="mono">p.default</span> is not empty) → <strong>optional</strong>, not added to required.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Is it Optional[X]?</h4><p>No default, but the type is <span class="mono">Optional[X]</span> (i.e. <span class="mono">is_optional</span> is true) → <strong>optional</strong>, not added to required.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Otherwise</h4><p>No default and not Optional → <strong>enters required</strong>; the model must supply it on every call.</p></div></div>
</div>
<p>Don't underestimate this <span class="mono">required</span> list — it directly sways the model's behavior. Parameters listed in <span class="mono">required</span> <strong>must</strong> be supplied by the model when it calls; those left out it may omit. So "which are required" is both a correctness constraint and a hint to the model.</p>
<div class="note tip"><span class="ni">✅</span><span class="nx">A practical habit: for any parameter that "without it the work can't be done", give it no default and don't mark it <span class="mono">Optional</span> — let it enter <span class="mono">required</span>; for any "nice-to-have" parameter, give a default or use <span class="mono">Optional</span> so the model can skip it. This boundary decides how usable the tool is.</span></div>
<h2>Advanced: using a Pydantic model as a parameter</h2>
<p>When a parameter is itself "a set of fields" — say an email draft has a recipient, a subject, and a body — rather than flatten it into three scattered parameters, it's better to pack it into a Pydantic model so the schema carries its own structure. In the tool signature, a single parameter <span class="mono">draft: EmailDraft</span> is enough.</p>
<div class="note tip"><span class="ni">💡</span><span class="nx">When <span class="mono">generate_schema</span> meets <span class="mono">draft: EmailDraft</span>, it calls <span class="mono">EmailDraft.model_json_schema()</span>, placing <span class="mono">to / subject / body</span> along with their types and required relations into the tool schema as one <strong>nested object</strong>.</span></div>
<p>This way, what the model sees is a clearly structured object, not three unrelated strings. Better still: adding or removing fields, and constraining types, all live in the model definition, while the tool signature stays clean. This is exactly why, for structured inputs, the official recommendation is a Pydantic model rather than <span class="mono">Dict</span>.</p>
<div class="note info"><span class="ni">📌</span><span class="nx">Summing up the type section: use basic types when you can, use <span class="mono">Optional</span> for "optional", use <span class="mono">Literal</span> for "one of several", use a Pydantic model for "a set of fields" — steer clear of parameterized <span class="mono">Dict[k,v]</span> and general <span class="mono">Union</span> and you sidestep the vast majority of errors.</span></div>
<div class="cute"><div class="row">
  <span class="emoji">📝</span><span class="lab">docstring</span>
  <span class="emoji">🔧</span><span class="lab">function</span>
  <span class="arrow">→</span>
  <span class="emoji">📜</span><span class="lab">schema</span>
  <span class="arrow">→</span>
  <span class="emoji">🤖</span><span class="bubble">I only read the menu</span>
</div><div class="cap">The model never reads your function body — only the schema that generate_schema stitches together.</div></div>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>Here's an easily overlooked shift in perspective: <strong>a docstring is not a comment for humans, it's API documentation for the "model"</strong>. Whether the model decides to call this tool, and how it fills the parameters, all rests on this schema — and the schema's description text comes word for word from your docstring.</p>
<p>So one vague or missing parameter description <strong>directly lowers</strong> the model's odds of using the tool correctly. This is a functional problem, not a code-style one. Letta simply promotes it to a "compile-time error": if any parameter lacks a description, <span class="mono">generate_schema</span> <span class="mono">raise</span>s <span class="mono">ValueError</span> on the spot, the tool can't be built at all, forcing you to say it clearly.</p>
<p>Remember it in one line: <strong>write the docstring for the model, not for your colleague</strong>. This loops right back to Lesson 4 — a tool is the agent's interface to the world, and the quality of that interface rides on these few lines of description.</p>
</div>
<h2>Good docstring vs bad docstring</h2>
<p>Enough abstract talk — a comparison says it better. The same "send email" tool, written two ways, lands wildly different effects on the model:</p>
<div class="cols">
  <div class="col"><h4>🙁 The vague version</h4><p><span class="mono">to (str): the recipient.</span> The model only knows it must pass a string, but should that be an email, a name, or a user ID? It can only guess, and a wrong guess sends to the wrong person.</p></div>
  <div class="col"><h4>🙂 The clear version</h4><p><span class="mono">to (str): the recipient's full email address, e.g. alice@example.com.</span> The model grasps the format and the example at a glance, and almost never fills it wrong.</p></div>
</div>
<p>Notice: the two versions have <strong>identical code</strong>, not one character of the function body changed; the only difference is the docstring. This is exactly why a parameter description is "function" and not "style" — it concretely changes the model's odds of using the tool correctly. One good description beats countless after-the-fact corrections.</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">Many people treat the docstring as "documentation patched on afterward" and write it carelessly. But in Letta it is <strong>part of the runtime</strong>: write it well and the model uses it accurately; write it poorly and even the smartest model can't be rescued. Please treat it as seriously as code.</span></div>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<ul>
<li><strong>The function-level description may be missing; parameter descriptions may not.</strong> The whole tool has no overall sentence of description? That's fine — it falls back to <span class="mono">"No description available"</span>. But <strong>every parameter</strong> must have a description (otherwise <span class="mono">ValueError</span>) and a type annotation (otherwise <span class="mono">TypeError</span>).</li>
<li><strong>Not every type is supported.</strong> A parameterized <span class="mono">Dict[k,v]</span> gives <span class="mono">ValueError</span>, and a general <span class="mono">Union</span> gives <span class="mono">NotImplementedError</span>. When you need structured input, switch to a Pydantic <span class="mono">BaseModel</span>.</li>
<li><strong>self / agent_state are reserved parameters.</strong> They belong to <span class="mono">TOOL_RESERVED_KWARGS</span>, are skipped outright, and <strong>do not enter</strong> the schema — the model neither sees nor fills them.</li>
<li><strong>request_heartbeat is not added here.</strong> It is not injected by <span class="mono">generate_schema</span>, but attached separately at runtime (see Lesson 15). Don't hand-write it in the docstring.</li>
<li><strong>Don't describe self / agent_state in the docstring.</strong> They never enter the schema, so writing them is wasted effort and may even disturb parsing. Describe only the parameters the model actually fills.</li>
</ul>
</div>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<strong>One through-line, a few anchors.</strong> The generator is <span class="mono">letta/functions/schema_generator.py::generate_schema(function, name=None, …)</span> — inside, <span class="mono">inspect.signature</span> reads the signature, <span class="mono">docstring_parser.parse</span> parses the Google-style docstring, and a hand-written <span class="mono">type_to_json_schema_type</span> does the type mapping. The per-parameter hard checks live here too: missing description → <span class="mono">raise ValueError</span>, missing annotation → <span class="mono">TypeError</span>; while <span class="mono">validate_google_style_docstring</span> only <strong>warns</strong> (its <span class="mono">ValueError</span> is caught and logged). The reserved-param list is <span class="mono">letta/constants.py::TOOL_RESERVED_KWARGS = ["self", "agent_state"]</span>. For example docstrings, see <span class="mono">letta/functions/function_sets/base.py</span> (<span class="mono">send_message</span> / <span class="mono">archival_memory_insert</span>, etc.). Follow this chain of symbols and you can walk "function → schema" end to end.
</div>
<h2>Digging a little deeper</h2>
<p>That was the main line. Below are four drawers, made specially for anyone who likes to pick at the details — each unfolds as "example / why / source". If you'd rather not dig in, skip straight to this lesson's key points.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">As you read these drawers, hold onto one thread: <strong>anything the model can see comes from the docstring and the signature; anything the model can't see (self, the function body, runtime parameters) is not generate_schema's business.</strong> Hold this thread and the scattered details all find their place.</span></div>
<details class="accordion"><summary>① Why is the docstring a "contract", not just a comment?</summary><div class="acc-body">
<p><strong>Example:</strong> you delete <span class="mono">message</span>'s description; the function still runs fine, the unit tests still pass, but this tool <strong>can't be registered into Letta</strong>.</p>
<p><strong>Why:</strong> from start to finish the model <strong>sees only the schema, never the code</strong>. However good your code comments are, if they don't reach the schema they don't exist — and the schema's parameter descriptions can come only from the docstring. That upgrades the docstring from an "optional comment" to "a contract that must be honored". The model's whole understanding of a parameter rides on this one line; once it turns vague, the model's guesses diverge and the call success rate falls with them.</p>
<p><strong>Source:</strong> <span class="mono">letta/functions/schema_generator.py::generate_schema</span> fetches each parameter's description in the loop, and if it can't get one, <span class="mono">raise ValueError</span>, blocking the breach at the construction stage.</p>
</div></details>
<details class="accordion"><summary>② Where are the boundaries of type mapping? Why don't Dict / Union work?</summary><div class="acc-body">
<p><strong>Example:</strong> <span class="mono">Optional[str]</span> gets unwrapped to <span class="mono">string</span> and removed from required; but <span class="mono">Dict[str, int]</span> errors directly, and <span class="mono">Union[int, str]</span> errors too.</p>
<p><strong>Why:</strong> JSON schema needs a clear, validatable structure. A <span class="mono">Dict</span> with key/value types, and an arbitrary <span class="mono">Union</span>, are hard to express unambiguously, so Letta chooses to "error rather than guess". To pass a structured object, define a Pydantic <span class="mono">BaseModel</span>. After all, a fuzzy schema is worse than none — it only lures the model into error after error.</p>
<p><strong>Source:</strong> <span class="mono">letta/functions/schema_generator.py::type_to_json_schema_type</span> handles each branch by hand; on a <span class="mono">BaseModel</span> it calls its <span class="mono">model_json_schema()</span> to get a nested object.</p>
</div></details>
<details class="accordion"><summary>③ What's the difference between self / agent_state and request_heartbeat?</summary><div class="acc-body">
<p><strong>Example:</strong> a tool signed as <span class="mono">def foo(self, agent_state, x: int)</span> ends up with only <span class="mono">x</span> in the schema. At runtime the model may even "see" a <span class="mono">request_heartbeat</span> parameter, but it isn't in this code.</p>
<p><strong>Why:</strong> <span class="mono">self</span>/<span class="mono">agent_state</span> are <strong>build-time</strong> reserved parameters — injected by the runtime framework, not meant for the model to fill, so they're skipped when generating the schema. <span class="mono">request_heartbeat</span>, by contrast, is a <strong>runtime</strong> control parameter attached later (deciding whether to keep looping), injected elsewhere, not <span class="mono">generate_schema</span>'s business. In a word: one is "hidden at build time", the other is "attached at run time" — their lifecycles are entirely different.</p>
<p><strong>Source:</strong> the reserved names live in <span class="mono">TOOL_RESERVED_KWARGS</span>, and <span class="mono">generate_schema</span> hits <span class="mono">continue</span> when it meets them; for <span class="mono">request_heartbeat</span>'s injection see Lesson 15's execution loop.</p>
</div></details>
<details class="accordion"><summary>④ If the Google-style validation fails, can the tool never be built?</summary><div class="acc-body">
<p><strong>Example:</strong> when the docstring format is slightly off-standard (say the <span class="mono">Args:</span> indentation is irregular), you may see only a warning in the log, and the tool <strong>still</strong> builds.</p>
<p><strong>Why:</strong> there are "two gates, one soft, one hard". The overall Google-style validation is <strong>soft</strong> — its <span class="mono">ValueError</span> is caught by a <span class="mono">try/except</span> and downgraded to <span class="mono">logger.warning</span>, never interrupting. What truly <strong>hard</strong>-blocks you is the per-parameter "has a description, has a type annotation" check inside the loop; those two errors aren't swallowed. So remember the weight: a non-standard format is at most a "reminder", while a parameter with no description or no annotation is the real "hard injury" that stops you.</p>
<p><strong>Source:</strong> the soft validation is in <span class="mono">letta/functions/schema_generator.py::validate_google_style_docstring</span>, whose exception is caught upstream as a warning; the hard checks remain in <span class="mono">generate_schema</span>'s main loop.</p>
</div></details>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li><strong>Tool = function</strong>: no special base class; an ordinary Python function plus a well-formed docstring is enough.</li>
<li><strong>generate_schema(signature + docstring) → JSON schema</strong>: auto-generated with <span class="mono">inspect.signature</span> + <span class="mono">docstring_parser</span>.</li>
<li><strong>The model sees only the schema, not the code</strong>: the function body is completely invisible to the model.</li>
<li><strong>Each parameter's description + type annotation is a hard contract</strong>: missing description → <span class="mono">ValueError</span>, missing annotation → <span class="mono">TypeError</span>.</li>
<li><strong>Type mapping is hand-written</strong>: str/int/bool/float/Optional/List/Literal/BaseModel are supported; parameterized Dict and general Union error out.</li>
<li><strong>self / agent_state are reserved</strong>: they belong to <span class="mono">TOOL_RESERVED_KWARGS</span> and don't enter the schema.</li>
<li><strong>The schema is persisted</strong>: stored in the Tool's <span class="mono">json_schema</span> field, computed once at registration and reused thereafter.</li>
</ul>
</div>
<p>Turning this lesson around makes it clearer: you're <strong>not</strong> "writing a function and adding comments along the way", you're "writing an interface spec for the model and implementing it along the way". Flip your perspective and every word of the docstring carries weight. The signature gives the interface's shape, the docstring gives its semantics, and together they form the complete, usable tool in the model's eyes.</p>
<p>One last teaser. From start to finish this lesson assumed one premise: <strong>we already hold a function object</strong> whose signature <span class="mono">inspect</span> can read. But in reality, users often upload <strong>a string of source code</strong> to register a custom tool. The server then faces a thorny requirement: it must still produce the schema while <strong>never running that code</strong>. How does it pull that off? That's exactly the topic of <strong>Lesson 18</strong>.</p>

"""}

LESSON_18 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第 17 课有一个悄悄藏起来的前提：我们<strong>已经握着一个 Python 函数对象</strong>，可以直接 <span class="mono">inspect.signature</span> 读它的签名。可现实里，用户注册自定义工具时，递给服务器的往往不是函数对象，而是<strong>一段源码字符串</strong>。</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">于是冒出一个棘手的要求：要在<strong>绝不运行这段代码</strong>的前提下，照样产出它的 JSON schema。既要"读懂"这段陌生代码的形状，又一行都不能跑——这才是本课真正的难点。第 17 课解决的是"已有函数对象"的简单情形，本课要啃的，是"只有一段源码字符串"的硬核情形。</p>

<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>想象你在仓库验收一批陌生的电子产品。最稳妥的办法不是<strong>拆封、通电、试用</strong>——万一里头是"诈弹"呢？而是<strong>不拆封就验货</strong>：只读包装外印的"成分表 / 规格参数"，照着这些信息建档入库。</p>
<p>给 schema 派生器读源码，就是这种"读规格不通电"：只看函数的<strong>签名与 docstring</strong>（外印的规格），绝不 <span class="mono">import</span> 运行它（通电试用）。这段代码是用户上传的，谁也不知道它通电后会做什么。</p>
<p>更妙的是，这张"规格表"还自带防伪：包装上印的信息若对不上（源码语法错、参数缺注解），验货当场就能打回，根本不必通电就知道这批货不合格。读源码派生 schema 也一样——很多问题在"读"的阶段就被拦下了，压根轮不到"跑"。</p>
</div>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>Letta 的答案是 <span class="mono">letta/functions/functions.py::derive_openai_json_schema(source_code, name=None)</span>。它的套路只有三步：先用<strong>纯 AST 解析</strong>把源码读成语法树，再据此造一个 <span class="mono">MockFunction</span>（只带 <span class="mono">__name__ / __doc__ / __signature__</span> 三件套），最后把这个"假函数"喂给<strong>第 17 课里那个一模一样的</strong> <span class="mono">generate_schema</span>。</p>
<p>全程<strong>绝不 <span class="mono">exec</span>、绝不 <span class="mono">import</span></strong> 用户代码。要看懂这套魔术，得回答三个问题：</p>
<ul>
<li>为什么<strong>不能</strong>直接 <span class="mono">import</span> 这段源码？</li>
<li><span class="mono">MockFunction</span> 凭什么能<strong>骗过 <span class="mono">inspect</span></strong>？</li>
<li>AST 究竟<strong>静态读</strong>到了哪些东西？</li>
</ul>
<p>留意这三步全程<strong>只读不写、只解析不执行</strong>。下面几节就顺着这三个问题往下挖：先看 import 为何危险，再看 <span class="mono">MockFunction</span> 如何伪装，最后看 AST 到底读了哪些字段。</p>
</div>

<p>为什么"绝不运行"是条不容商量的红线？因为 Letta 是<strong>多租户</strong>服务：同一个进程里可能同时跑着许多用户的工具。只要有一段上传代码在 import 时越界，受害的就不只是它自己的会话，而是整台服务器和上面所有人的数据。把执行权牢牢攥在自己手里，是这类平台的生存底线。</p>

<h2>为什么不能直接 import</h2>
<p>最直觉的做法是 <span class="mono">import</span> 用户模块、再 <span class="mono">inspect</span> 里面的函数。可这条路有致命问题：<span class="mono">import</span> 会执行模块的<strong>顶层代码</strong>。用户源码里只要在函数定义之外写一行 <span class="mono">os.system(...)</span>，导入的那一刻就在你的服务器上跑起来了——这是教科书级的<strong>远程代码执行（RCE）</strong>。</p>
<div class="cols">
<div class="col"><h4>❌ import + inspect</h4><p>把源码当模块加载，会<strong>执行顶层代码</strong>。等于让陌生人在你服务器上跑任意命令，安全边界直接失守。</p></div>
<div class="col"><h4>✅ ast.parse</h4><p>把源码解析成<strong>语法树</strong>，<strong>纯静态、只读不跑</strong>。语法树就是结构化的"代码长相"，读它不会触发任何副作用。</p></div>
</div>
<p>把"顶层代码"说穿了：它指的是函数定义<strong>之外</strong>、模块一被加载就会执行的语句——<span class="mono">import</span> 第三方库、读环境变量、发一个网络请求，全都在加载那一刻发生。攻击者只要把恶意逻辑放在顶层（甚至藏进一个装饰器或默认参数表达式里），你的 <span class="mono">import</span> 就替他按下了执行键。</p>
<p>而 <span class="mono">ast.parse</span> 走的是另一条世界线：它把源码当成<strong>文本</strong>来分析，产出一棵描述"代码长什么样"的语法树。树上记着"这里定义了一个函数、它叫什么、有哪些参数、注解是什么"，但<strong>没有任何一步会执行</strong>这些语句。读一棵树，再危险的代码也只是数据。</p>
<table class="t">
<tr><th>维度</th><th>import + inspect</th><th>ast.parse（Letta 选这条）</th></tr>
<tr><td class="mono">是否执行代码</td><td>会，顶层语句立即运行</td><td>否，只构建语法树</td></tr>
<tr><td class="mono">安全风险</td><td>任意代码执行（RCE）</td><td>无副作用，纯只读</td></tr>
<tr><td class="mono">能拿到什么</td><td>真函数对象与真实签名</td><td>节点信息：函数名、参数、注解、docstring</td></tr>
<tr><td class="mono">坏代码的下场</td><td>已经跑了，覆水难收</td><td>顶多语法错，抛 LettaToolCreateError</td></tr>
</table>
<p>有人会反问：那我先把代码丢进一个受限沙箱、再 import 不就行了？可以，但成本与风险都高得多——你得维护沙箱、限制系统调用、还得承担逃逸风险。而"只为拿一张 schema"这件小事，根本不值得动用那么重的武器。能用"读"解决的，就别用"跑"。</p>
<div class="cute"><div class="row"><span class="emoji">📄</span><span class="lab">用户源码</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="lab">AST 只读不跑</span><span class="arrow">→</span><span class="emoji">📜</span><span class="bubble">我读你，但绝不跑你</span></div><div class="cap">派生器只"阅读"代码的形状，把它翻译成一张 schema，自始至终不让这段代码运行一行。</div></div>

<h2>派生流程：纯 AST + 复用 generate_schema</h2>
<div class="flow">
<div class="node"><div class="nt">source_code</div><div class="nd">用户上传的源码字符串</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">ast.parse（不跑）</div><div class="nd">解析成语法树，纯静态</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">_parse_function_from_source</div><div class="nd">从树里抽出签名与 docstring</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">MockFunction</div><div class="nd">只带三件套的假函数</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">generate_schema</div><div class="nd">第 17 课的同一个生成器</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">JSON schema</div><div class="nd">模型能看懂的工具契约</div></div>
</div>
<p>这条流水线最妙的地方，是末端那个 <span class="mono">generate_schema</span> 跟第 17 课<strong>一字不差</strong>。原生工具走的是"函数对象 → generate_schema"，上传工具走的是"源码 → MockFunction → generate_schema"——两条路在最后一步<strong>汇合到同一个生成器</strong>，schema 的口径因此完全一致。</p>
<p>别把"复用"看成偷懒，它其实是<strong>刻意的单一事实源</strong>：schema 的生成规则全代码库只有一处实现。无论工具是平台内置的、还是用户现写现传的，只要走到 <span class="mono">generate_schema</span>，类型映射、docstring 解析、保留参数过滤就完全一致，绝不会冒出"内置工具和上传工具 schema 口径不一样"的诡异 bug。</p>
<p>把上面流程里的第三步 <span class="mono">_parse_function_from_source</span> 单独放大，它内部其实是四个干净利落的小动作：</p>
<div class="vflow">
<div class="step"><div class="num">1</div><div class="sc"><h4>ast.parse(src)</h4><p>把源码字符串解析成语法树；语法不合法当场抛 <span class="mono">LettaToolCreateError</span>。</p></div></div>
<div class="step"><div class="num">2</div><div class="sc"><h4>选出函数节点</h4><p>遍历 <span class="mono">ast.walk(tree)</span>，取<strong>最后一个</strong> <span class="mono">FunctionDef</span> 当作工具本体。</p></div></div>
<div class="step"><div class="num">3</div><div class="sc"><h4>重建 Signature</h4><p>逐个参数读注解、用 <span class="mono">ast.literal_eval</span> 取字面量默认值，拼出 <span class="mono">inspect.Signature</span>。</p></div></div>
<div class="step"><div class="num">4</div><div class="sc"><h4>装进 MockFunction</h4><p>把函数名、docstring 与重建好的签名塞进假函数，交还给上层。</p></div></div>
</div>
<p>第一步的 <span class="mono">ast.parse</span> 还顺手当了"守门员"：源码若有语法错误，解析阶段就抛 <span class="mono">LettaToolCreateError</span>，把坏代码挡在创建环节之外。注意它<strong>只检查语法、不检查语义</strong>——能解析成树就放行；至于工具跑起来对不对，那是后面执行阶段才操心的事。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/functions.py</span><span class="ln">派生入口（简化）</span></div>
<pre><span class="kw">def</span> <span class="fn">derive_openai_json_schema</span>(source_code: str, name=<span class="kw">None</span>):
    mock = <span class="fn">_parse_function_from_source</span>(source_code, name)  <span class="cm"># 纯 AST，绝不 exec</span>
    <span class="kw">return</span> <span class="fn">generate_schema</span>(mock, name=name)            <span class="cm"># 复用第 17 课的生成器</span>
</pre></div>
<p>请记住这条主线：派生器<strong>没有重写</strong>任何 schema 生成逻辑。它干的活，是把一段源码"翻译"成一个 <span class="mono">generate_schema</span> 能接受的输入；真正生成 schema 的，仍是第 17 课那台机器。少一处实现，就少一处会与另一处跑偏的风险。</p>
<h2>MockFunction：骗过 inspect 的"假函数"</h2>
<p>问题来了：<span class="mono">generate_schema</span> 期待的是一个<strong>真函数对象</strong>，它要对其调用 <span class="mono">inspect.signature</span>、读 <span class="mono">__doc__</span>。可我们手里只有从 AST 抽出来的零件，并没有真函数。Letta 的办法是临时<strong>捏一个"假函数"</strong>——<span class="mono">MockFunction</span>，只把 <span class="mono">inspect</span> 关心的几个属性凑齐，剩下的一概不管。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/functions.py</span><span class="ln">MockFunction</span></div>
<pre><span class="kw">class</span> <span class="fn">MockFunction</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self, name, docstring, signature):
        self.__name__ = name
        self.__doc__ = docstring
        self.__signature__ = signature        <span class="cm"># 设了它，inspect.signature 就照常工作</span>
    <span class="kw">def</span> <span class="fn">__call__</span>(self, *a, **k):
        <span class="kw">raise</span> <span class="fn">NotImplementedError</span>(<span class="st">"mock function cannot be called"</span>)
</pre></div>
<div class="cellgroup"><div class="cg-cap"><b>MockFunction 只凑齐三个属性</b></div><div class="cells"><span class="cell hl">__name__ 名字</span><span class="sep">·</span><span class="cell hl">__doc__ docstring</span><span class="sep">·</span><span class="cell hl">__signature__ 参数</span></div></div>
<div class="note tip"><span class="ni">💡</span><span class="nx">关键在于：一旦显式设好 <span class="mono">__signature__</span>，<span class="mono">inspect.signature(mock)</span> 与 <span class="mono">parse(mock.__doc__)</span> 就能在一段<strong>从未运行过</strong>的代码上照常工作——<span class="mono">inspect</span> 只认这些属性，根本不在乎对象是真函数还是假货。这正是上传工具能<strong>原样复用</strong> <span class="mono">generate_schema</span> 的底层原因。</span></div>
<p>还有个细节别放过：<span class="mono">__call__</span> 被<strong>故意</strong>写成抛 <span class="mono">NotImplementedError</span>。<span class="mono">MockFunction</span> 的唯一使命是"供 <span class="mono">inspect</span> 读取属性"，它不该、也不能被真正调用。万一某段代码手滑把它当工具执行，会立刻炸出清晰的错误，而不是悄悄返回 <span class="mono">None</span> 把 bug 藏起来——这是典型的<strong>防御性设计</strong>。</p>
<p>这背后是 Python 的<strong>鸭子类型</strong>哲学："像鸭子一样走路、像鸭子一样叫，就当它是鸭子。" <span class="mono">inspect</span> 不查血统、只看属性：你拿得出 <span class="mono">__signature__</span>，它就把你当一个有签名的对象对待。<span class="mono">MockFunction</span> 正是吃准了这一点，用最小的"伪装"骗过了一整套本为真函数设计的工具链。</p>
<h2>AST 静态读了什么</h2>
<p>真正干活的是 <span class="mono">_parse_function_from_source</span>。它先把源码 <span class="mono">ast.parse</span> 成语法树，从中挑出函数节点，再<strong>逐项重建</strong>一个 <span class="mono">inspect.Signature</span>：参数名取自节点、类型来自注解、默认值用 <span class="mono">ast.literal_eval</span> 安全求值（只认字面量，不执行表达式）。整张签名是"拼"出来的，没有任何一处需要运行原代码。</p>
<p>举个具体例子：用户上传一个签名为 <span class="mono">def lookup(city: str = "NYC")</span> 的工具。解析器读树之后得到——函数名 <span class="mono">lookup</span>、参数 <span class="mono">city</span> 类型为 <span class="mono">str</span>、默认值 <span class="mono">"NYC"</span>，再加上 docstring 里那句描述。这些全部来自"读结构"，函数体里真正干活的那行逻辑<strong>一次都没跑过</strong>。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/functions.py</span><span class="ln">_parse_function_from_source（要点）</span></div>
<pre><span class="kw">def</span> <span class="fn">_parse_function_from_source</span>(src, name):
    tree = ast.<span class="fn">parse</span>(src)               <span class="cm"># 语法错 -> LettaToolCreateError</span>
    func = [n <span class="kw">for</span> n <span class="kw">in</span> ast.<span class="fn">walk</span>(tree) <span class="kw">if</span> isinstance(n, ast.FunctionDef)][-<span class="nb">1</span>]  <span class="cm"># 取最后一个函数</span>
    <span class="cm"># 重建 inspect.Signature：参数名、注解、用 ast.literal_eval 取默认值</span>
    <span class="cm"># 源码里定义的 BaseModel 用 type(name, (BaseModel,), {...}) 原地重建成桩，不 import</span>
    <span class="kw">return</span> <span class="fn">MockFunction</span>(func.name, ast.<span class="fn">get_docstring</span>(func), sig)
</pre></div>
<p>顺带一提，docstring 是直接从解析出的函数节点上读出来的（它的第一条语句若是字符串，就是 docstring）——纯 AST、不靠正则。Letta 的 AST 辅助 <span class="mono">ast_parsers.py::get_function_name_and_docstring</span> 干脆直接用标准库的 <span class="mono">ast.get_docstring</span> 来做这件事，多行、缩进、转义都替你处理好。</p>
<div class="note info"><span class="ni">📌</span><span class="nx">一段源码里若有<strong>多个函数</strong>，取<strong>最后一个</strong> <span class="mono">FunctionDef</span>（约定：工具就是文件里最后定义的那个）。相关 AST 辅助住在 <span class="mono">letta/functions/ast_parsers.py</span>，其中 <span class="mono">resolve_type</span> 用<strong>白名单</strong>解析类型、默认 <span class="mono">allow_unsafe_eval=False</span>——不过它是在<strong>之后执行工具、强转模型传来的参数</strong>时才用上，同样守着"不借解析跑代码"的底线。</span></div>
<p>这里还藏着两个值得记住的"安全阀"。第一个针对默认值：解析器不用 <span class="mono">eval</span>，而用 <span class="mono">ast.literal_eval</span>——后者只接受数字、字符串、列表、字典这类<strong>字面量</strong>，碰到函数调用或任意表达式就直接拒绝，从根上堵死"连求个默认值都能偷跑代码"的缝隙。</p>
<p>第二个针对类型注解：派生时，注解里不认识的名字<strong>不会</strong>被 import 或求值，而是当作普通字符串放过（源码里定义的 BaseModel 则原地造桩）——靠的是 functions.py 内的静态解析，不真去解类型。两道阀门合起来，确保"解析"绝不退化成"执行"。</p>

<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>一句话概括这门手艺：<strong>"从一段你拒绝运行的代码里，生成它的 schema。"</strong> 读函数签名最朴素的办法是 <span class="mono">import + inspect</span>，可 <span class="mono">import</span> 用户代码＝在你的服务端执行任意代码。Letta 的巧招是：先 <span class="mono">ast.parse</span> 成语法树（只读不跑），再造一个只带 <span class="mono">__name__/__doc__/__signature__</span> 的 <span class="mono">MockFunction</span>，喂给<strong>完全相同</strong>的 <span class="mono">generate_schema</span>。</p>
<p>结果是：模型拿到一张真 schema，服务器却<strong>一行用户代码都没跑</strong>。连源码里定义的 Pydantic 类型，也用 <span class="mono">type(name,(BaseModel,),{})</span> 原地重建成桩，而非 import。它把"安全"巧妙地变成了一道"解析"题——这正是第 20 课沙箱哲学的前奏：<strong>"工具的代码，自始至终不可信。"</strong></p>
<p>这种"把危险操作转化成安全操作"的思路，在工程上极有价值：它不是给危险行为层层加锁，而是<strong>从设计上让危险根本无从发生</strong>。记住这个套路，你会在很多优秀系统里反复见到它的身影。</p>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">记忆钩子：这一课的所有巧思，都能压缩成一句话——<strong>"读它，但绝不跑它。"</strong> 读，靠 AST；接回旧流程，靠 <span class="mono">MockFunction</span>；安全，靠从不 import。</span></div>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p>这套机制散落在几处，但脉络清晰：</p>
<ul>
<li><strong>派生器三件套</strong>（均在 <span class="mono">letta/functions/functions.py</span>）：<span class="mono">derive_openai_json_schema</span>、<span class="mono">MockFunction</span>、<span class="mono">_parse_function_from_source</span>。</li>
<li><strong>AST 辅助</strong>：<span class="mono">letta/functions/ast_parsers.py</span>，含 <span class="mono">get_function_name_and_docstring</span> 与白名单类型解析 <span class="mono">resolve_type</span>。</li>
<li><strong>TypeScript 派生</strong>：<span class="mono">letta/functions/typescript_parser.py::derive_typescript_json_schema</span>。</li>
<li><strong>接线在创建时</strong>：<span class="mono">letta/services/tool_manager.py</span>（custom 且无 schema → 调用派生）→ <span class="mono">letta/services/tool_schema_generator.py::generate_schema_for_tool_creation</span>（按 <span class="mono">source_type</span> 分派 Python / TypeScript）。</li>
</ul>
<p>一句话串起来：<strong>创建时</strong>由 <span class="mono">tool_manager</span> 触发，<strong>派生</strong>落在 <span class="mono">functions.py</span> 三件套，<strong>类型解析</strong>靠 <span class="mono">ast_parsers.py</span>，<strong>语言分派</strong>看 <span class="mono">source_type</span>。顺着这条线读源码，基本不会迷路。</p>
</div>

<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<ul>
<li><span class="mono">MockFunction</span> 住在 <strong>functions.py</strong>，<strong>不在</strong> <span class="mono">ast_parsers.py</span>——别找错文件。</li>
<li>多函数源码取<strong>最后一个</strong> <span class="mono">FunctionDef</span>，<strong>不是第一个</strong>。</li>
<li>TypeScript 工具创建<strong>必须显式传 <span class="mono">json_schema</span></strong>，否则 <span class="mono">ToolCreate</span> 直接报错。</li>
<li>schema 派生<strong>只在创建时</strong>做，<strong>已不在</strong> pydantic 校验器里：<span class="mono">Tool.refresh_source_code_and_json_schema</span> 对 custom 缺 schema 只<strong>告警</strong>、不再现算。</li>
<li><span class="mono">ast.literal_eval</span> 只认<strong>字面量</strong>；别误以为它能求值任意默认值表达式，那正是它"安全"的原因。</li>
</ul>
</div>
<h2>TypeScript 工具</h2>
<p>工具不只能用 Python 写。<span class="mono">letta/functions/typescript_parser.py::derive_typescript_json_schema</span> 负责 TS：它<strong>不走 AST</strong>，而是用<strong>正则</strong>扫描 <span class="mono">export function</span> 的签名，再从 <span class="mono">JSDoc</span> 注释里取参数描述；参数名后带 <span class="mono">?</span> 视为可选。</p>
<p>类型映射更粗放：<span class="mono">union</span> 一律映射成 <span class="mono">string</span>，<span class="mono">any</span> 也落到 <span class="mono">string</span>。源类型由 <span class="mono">letta/schemas/enums.py::ToolSourceType</span> 枚举给出，有 <span class="mono">python / typescript / json</span> 三种。</p>
<div class="note info"><span class="ni">👉</span><span class="nx">但有个硬约束：TS 工具在 API 创建时<strong>必须</strong>自带 <span class="mono">json_schema</span>（<span class="mono">ToolCreate.validate_typescript_requires_schema</span>，缺了就 <span class="mono">ValueError</span>）。所以"自动派生 schema"这条路<strong>主要服务 Python 工具</strong>；TS 的 schema 通常由调用方显式给出。</span></div>
<p>顺手厘清 <span class="mono">source_type</span> 的角色：它就是一张"语言标签"，告诉派生器这段源码该用哪把解析器——Python 走 AST、TypeScript 走正则，而 JSON 则表示"schema 我已经给你了，不用派生"。</p>
<div class="cellgroup"><div class="cg-cap"><b>ToolSourceType 的三种取值</b></div><div class="cells"><span class="cell hl">python · 走 AST 派生</span><span class="sep">·</span><span class="cell">typescript · 走正则，需显式 schema</span><span class="sep">·</span><span class="cell">json · 直接提供 schema</span></div></div>
<p>那为什么 TS 偏偏要"必须显式给 schema"？因为正则能稳妥覆盖的 TypeScript 语法面，远不如 Python 的 AST 完整、严谨。与其在复杂类型上猜错，不如让调用方把权威 schema 直接交出来。于是"自动派生"这条便利通道，主力服务的始终是 Python。</p>
<p>顺带交代 <span class="mono">JSDoc</span> 的角色：TS 解析器从 <span class="mono">/** ... */</span> 注释里取每个参数的描述，就像 Python 从 docstring 取描述一样——给模型看的"说明"，两种语言殊途同归，都放在注释里。区别只在抽取方式：一个用正则扫文本，一个用 AST 读结构。</p>

<h2>再挖深一点</h2>
<p>把几个最容易卡住的"为什么"摊开来讲，每条都给示例、原因和源码出处。</p>
<details class="accordion"><summary>① 为什么用 AST，而不直接 import？</summary><div class="acc-body">
<p><strong>示例：</strong>用户源码在函数定义之外、顶层写了一行 <span class="mono">os.system("rm -rf /")</span>，只要你 <span class="mono">import</span> 它，这行就在你的服务器上跑了。注意：函数<strong>根本没被调用</strong>，仅仅"导入"就足以触发，这正是顶层代码可怕的地方。</p>
<p><strong>为什么：</strong><span class="mono">import</span> 会执行模块的<strong>顶层代码</strong>，等于把服务器交给陌生人，是标准的 RCE。<span class="mono">ast.parse</span> 则只把源码读成<strong>语法树</strong>——纯静态、零副作用，看一千遍也不会触发任何执行。安全的本质，是"只读不跑"。</p>
<p><strong>源码：</strong><span class="mono">letta/functions/functions.py::_parse_function_from_source</span> 全程基于 <span class="mono">ast</span>，没有一处 <span class="mono">exec/import</span>。</p>
<p><strong>延伸：</strong>正因如此，Letta 把"不可信代码"当成贯穿整个工具系统的第一性原则——从派生 schema 到第 20 课的沙箱执行，都是这条原则的不同侧面。</p>
</div></details>
<details class="accordion"><summary>② MockFunction 凭什么骗过 inspect？</summary><div class="acc-body">
<p><strong>示例：</strong><span class="mono">inspect.signature(mock)</span> 照样返回完整签名，哪怕 <span class="mono">mock</span> 从未被当作真函数定义过、调用它还会直接抛 <span class="mono">NotImplementedError</span>。</p>
<p><strong>为什么：</strong><span class="mono">inspect</span> 读签名时只看对象的 <span class="mono">__signature__</span> 属性，读文档只看 <span class="mono">__doc__</span>——它<strong>根本不验证</strong>对象是不是"真函数"。只要这几个属性齐了，它就照常工作。这正是上传工具能原样复用 <span class="mono">generate_schema</span> 的关键。</p>
<p><strong>源码：</strong><span class="mono">letta/functions/functions.py::MockFunction</span> 在 <span class="mono">__init__</span> 里手动设好这三个属性。</p>
<p><strong>延伸：</strong>这也解释了为什么不必"真造一个函数"：<span class="mono">generate_schema</span> 要的从来不是可执行性，而是<strong>可描述性</strong>——签名与文档齐了，描述就齐了。</p>
</div></details>
<details class="accordion"><summary>③ 为什么取最后一个函数？未知类型怎么办？</summary><div class="acc-body">
<p><strong>示例：</strong>源码里先写了几个辅助函数、最后才是工具本体，于是解析器取<strong>最后一个</strong> <span class="mono">FunctionDef</span>。</p>
<p><strong>为什么：</strong>约定"工具是文件末尾那个函数"。若源码里<strong>定义</strong>了 Pydantic 模型，就用 <span class="mono">type(name, (BaseModel,), {...})</span> <strong>原地重建</strong>成一个桩类，绝不去 <span class="mono">import</span> 真实定义——既能让签名成形，又守住"不跑用户代码"的底线。</p>
<p><strong>源码：</strong><span class="mono">_parse_function_from_source</span>（取最后一个 <span class="mono">FunctionDef</span>、<span class="mono">ast.literal_eval</span> 取默认值）；白名单解析 <span class="mono">ast_parsers.py::resolve_type</span> 用于之后的参数强转。</p>
<p><strong>延伸：</strong>造桩靠 <span class="mono">type(name,(BaseModel,),{})</span> 这一行——它在运行时凭空合成一个类，仅供签名"有个名字可填"，绝不去触碰用户真正想引用的那个定义。</p>
</div></details>
<details class="accordion"><summary>④ 派生到底在何时、何地触发？</summary><div class="acc-body">
<p><strong>示例：</strong>你创建一个 custom Python 工具却没给 <span class="mono">json_schema</span>，服务器就在<strong>创建流程</strong>里替你把 schema 派生出来。反过来，若你已经给了 schema，这一步就被跳过——派生只是"缺啥补啥"的兜底。</p>
<p><strong>为什么：</strong>接线落在 <span class="mono">tool_manager</span>（判断 custom 且缺 schema）→ <span class="mono">generate_schema_for_tool_creation</span>（按 <span class="mono">source_type</span> 分派 Python / TS）。它<strong>已不在</strong> pydantic 校验器里，所以一次创建只算一次；而 TS 因为必须显式给 schema，通常不会落到自动派生这一支。</p>
<p><strong>源码：</strong><span class="mono">letta/services/tool_manager.py</span>、<span class="mono">letta/services/tool_schema_generator.py::generate_schema_for_tool_creation</span>。</p>
<p><strong>延伸：</strong>把派生放在创建时、而非每次校验时，既省去重复计算，也让 schema 成为一份"创建那一刻定下、之后稳定不变"的契约。</p>
</div></details>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li><strong>注册自定义工具时，schema 靠纯 AST 派生</strong>：从源码字符串生成 schema，<strong>绝不运行</strong>这段代码。</li>
<li><strong><span class="mono">derive_openai_json_schema</span> = <span class="mono">_parse_function_from_source</span> + 复用 <span class="mono">generate_schema</span></strong>：和第 17 课汇合到同一个生成器。</li>
<li><strong><span class="mono">MockFunction</span> 提供 <span class="mono">__name__ / __doc__ / __signature__</span></strong>：用三件套骗过 <span class="mono">inspect</span>，调用即抛错。</li>
<li><strong>取最后一个 <span class="mono">FunctionDef</span>、未知类型造桩</strong>：未定义的 BaseModel 用 <span class="mono">type(name,(BaseModel,),{})</span> 顶上，不 import。</li>
<li><strong>TS 工具必须显式给 <span class="mono">json_schema</span></strong>：自动派生主要服务 Python。</li>
<li><strong>派生只在创建时做</strong>：接线在 <span class="mono">tool_manager</span> → <span class="mono">tool_schema_generator</span>，已不在 pydantic 校验器里。</li>
</ul>
<p>把这几条连起来看：<strong>不运行</strong>是原则，<strong>AST 解析</strong>是手段，<strong>MockFunction</strong>是适配器，<strong>复用 generate_schema</strong>是收益。四者环环相扣，缺一不可——这正是一个"安全又省事"的设计该有的样子。</p>
</div>

<p>回头看这一课，它其实只讲了一件事：<strong>把"安全"重新表述成"解析"</strong>。一旦你拒绝运行用户代码，"读懂它"就从一个运行时问题变成了一个纯文本分析问题——而文本分析，正是 AST 的拿手好戏。<span class="mono">MockFunction</span> 则像一座桥，让分析出来的零件无缝接回第 17 课那套成熟的生成器。</p>

<p>至此，工具有了 schema、能被模型"看见"并发起调用。可当 agent <strong>真要执行</strong>一个工具时，它怎么知道"该用哪种方式跑它"——是直接在进程内调用、丢进沙箱隔离执行、还是连去一台外部服务器？这就是<strong>第 19 课"工具分发与执行"</strong>要回答的问题。换句话说，schema 解决的是"模型怎么理解工具"，而执行要解决的是"系统怎么安全地把工具跑起来"——这个故事，才刚刚讲到一半。</p>

""", "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Lesson 17 quietly leaned on one assumption: we <strong>already held a Python function object</strong> and could call <span class="mono">inspect.signature</span> on it directly. But in reality, when a user registers a custom tool, what reaches the server is usually not a function object but <strong>a string of source code</strong>.</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">That raises a thorny demand: produce its JSON schema <strong>without ever running the code</strong>. You must "understand" the shape of this unfamiliar code yet execute not a single line — that is the real difficulty here. Lesson 17 solved the easy case of "we already have a function object"; this lesson tackles the hardcore case of "all we have is a source string."</p>

<div class="card analogy"><div class="tag">🔌 Analogy</div>
<p>Picture yourself receiving a batch of unfamiliar electronics at a warehouse. The safest move is not to <strong>unbox, power on, and try them out</strong> — what if one is a "booby trap"? Instead you <strong>inspect without unsealing</strong>: read only the "ingredients / spec sheet" printed on the box, and file each item by that information.</p>
<p>Handing source code to the schema deriver is exactly this "read the spec, never power it on": look only at the function's <strong>signature and docstring</strong> (the printed spec), never <span class="mono">import</span> and run it (powering on). This code was uploaded by a user, and nobody knows what it will do once powered up.</p>
<p>Better still, this "spec sheet" is self-checking: if the printed information doesn't add up (a syntax error in the source, a parameter missing its annotation), you can reject the shipment on the spot — no need to power anything on to know the batch is defective. Deriving a schema from source is the same: many problems are caught at the "reading" stage and never reach the "running" stage at all.</p>
</div>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Letta's answer is <span class="mono">letta/functions/functions.py::derive_openai_json_schema(source_code, name=None)</span>. Its recipe is just three steps: first use <strong>pure AST parsing</strong> to read the source into a syntax tree, then build a <span class="mono">MockFunction</span> from it (carrying only the trio <span class="mono">__name__ / __doc__ / __signature__</span>), and finally feed that "fake function" into the <strong>exact same</strong> <span class="mono">generate_schema</span> from Lesson 17.</p>
<p>At no point does it <strong>ever <span class="mono">exec</span> or <span class="mono">import</span></strong> the user's code. To see through this magic, answer three questions:</p>
<ul>
<li>Why can we <strong>not</strong> just <span class="mono">import</span> this source directly?</li>
<li>How does <span class="mono">MockFunction</span> manage to <strong>fool <span class="mono">inspect</span></strong>?</li>
<li>What exactly does the AST <strong>read statically</strong>?</li>
</ul>
<p>Notice that all three steps <strong>only read, never write; only parse, never execute</strong>. The next sections dig down along these three questions: first why import is dangerous, then how <span class="mono">MockFunction</span> disguises itself, and finally which fields the AST actually reads.</p>
</div>

<p>Why is "never run it" a non-negotiable red line? Because Letta is a <strong>multi-tenant</strong> service: one process may run many users' tools at once. If a single piece of uploaded code oversteps at import time, the victim is not just its own session but the whole server and everyone's data on it. Keeping execution firmly in your own hands is the survival baseline for such a platform.</p>
<h2>Why you can't just import</h2>
<p>The most intuitive approach is to <span class="mono">import</span> the user's module and then <span class="mono">inspect</span> the function inside. But this path has a fatal flaw: <span class="mono">import</span> executes the module's <strong>top-level code</strong>. If the user's source has a single line like <span class="mono">os.system(...)</span> outside any function definition, it runs on your server the instant you import it — a textbook case of <strong>remote code execution (RCE)</strong>.</p>
<div class="cols">
<div class="col"><h4>❌ import + inspect</h4><p>Loading the source as a module <strong>executes top-level code</strong>. That's like letting a stranger run arbitrary commands on your server — the security boundary falls immediately.</p></div>
<div class="col"><h4>✅ ast.parse</h4><p>Parsing the source into a <strong>syntax tree</strong> is <strong>purely static, read-only, never run</strong>. A syntax tree is just the structured "shape" of the code; reading it triggers no side effects.</p></div>
</div>
<p>To spell out "top-level code": it means statements <strong>outside</strong> any function definition that run the instant the module is loaded — importing a third-party library, reading an environment variable, firing a network request, all happen at load time. An attacker only has to put malicious logic at the top level (or even hide it inside a decorator or a default-argument expression), and your <span class="mono">import</span> presses the execute button for them.</p>
<p>By contrast, <span class="mono">ast.parse</span> follows a different timeline: it analyzes the source as <strong>text</strong> and produces a syntax tree describing "what the code looks like." The tree records "a function is defined here, this is its name, these are its parameters, here are the annotations," but <strong>no step executes</strong> any of those statements. Read as a tree, even the most dangerous code is just data.</p>
<table class="t">
<tr><th>Dimension</th><th>import + inspect</th><th>ast.parse (Letta's choice)</th></tr>
<tr><td class="mono">Runs the code?</td><td>Yes — top-level statements run at once</td><td>No — only builds a syntax tree</td></tr>
<tr><td class="mono">Security risk</td><td>Arbitrary code execution (RCE)</td><td>No side effects, pure read-only</td></tr>
<tr><td class="mono">What you can get</td><td>A real function object and real signature</td><td>Node info: function name, parameters, annotations, docstring</td></tr>
<tr><td class="mono">Fate of bad code</td><td>Already ran — no undo</td><td>At worst a syntax error, raises LettaToolCreateError</td></tr>
</table>
<p>Someone might push back: can't I drop the code into a restricted sandbox first and then import it? You can, but the cost and risk are far higher — you must maintain the sandbox, restrict system calls, and still bear the escape risk. For the small matter of "just getting a schema," it isn't worth wielding such a heavy weapon. If "reading" can solve it, don't "run" it.</p>
<div class="cute"><div class="row"><span class="emoji">📄</span><span class="lab">user source</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="lab">AST reads, never runs</span><span class="arrow">→</span><span class="emoji">📜</span><span class="bubble">I read you, but never run you</span></div><div class="cap">The deriver only "reads" the shape of the code and translates it into a schema, never letting a single line of that code run.</div></div>
<h2>The pipeline: pure AST + reusing generate_schema</h2>
<div class="flow">
<div class="node"><div class="nt">source_code</div><div class="nd">the source string a user uploaded</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">ast.parse (no run)</div><div class="nd">parsed into a syntax tree, purely static</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">_parse_function_from_source</div><div class="nd">pulls signature and docstring from the tree</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">MockFunction</div><div class="nd">a fake function carrying only the trio</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">generate_schema</div><div class="nd">the very same generator from Lesson 17</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">JSON schema</div><div class="nd">the tool contract the model can read</div></div>
</div>
<p>The cleverest part of this pipeline is that the <span class="mono">generate_schema</span> at the end is <strong>word-for-word identical</strong> to Lesson 17's. Native tools take "function object → generate_schema"; uploaded tools take "source → MockFunction → generate_schema" — the two paths <strong>converge on the same generator</strong> at the final step, so the schemas come out perfectly consistent.</p>
<p>Don't read "reuse" as laziness — it is a deliberate <strong>single source of truth</strong>: the rules for generating a schema have exactly one implementation across the whole codebase. Whether a tool is platform-built-in or written and uploaded on the spot, once it reaches <span class="mono">generate_schema</span> the type mapping, docstring parsing, and reserved-parameter filtering are identical, so the weird bug of "built-in and uploaded tools have different schema conventions" can never appear.</p>
<p>Zoom in on the third step above, <span class="mono">_parse_function_from_source</span>, and inside it are four clean little moves:</p>
<div class="vflow">
<div class="step"><div class="num">1</div><div class="sc"><h4>ast.parse(src)</h4><p>Parse the source string into a syntax tree; invalid syntax raises <span class="mono">LettaToolCreateError</span> on the spot.</p></div></div>
<div class="step"><div class="num">2</div><div class="sc"><h4>Pick the function node</h4><p>Walk <span class="mono">ast.walk(tree)</span> and take the <strong>last</strong> <span class="mono">FunctionDef</span> as the tool body.</p></div></div>
<div class="step"><div class="num">3</div><div class="sc"><h4>Rebuild the Signature</h4><p>Read each parameter's annotation, take literal defaults via <span class="mono">ast.literal_eval</span>, and assemble an <span class="mono">inspect.Signature</span>.</p></div></div>
<div class="step"><div class="num">4</div><div class="sc"><h4>Wrap in MockFunction</h4><p>Stuff the function name, docstring, and rebuilt signature into the fake function and hand it back up.</p></div></div>
</div>
<p>Step one's <span class="mono">ast.parse</span> doubles as a "gatekeeper": if the source has a syntax error, the parsing stage raises <span class="mono">LettaToolCreateError</span> and keeps bad code out of creation entirely. Note it checks <strong>syntax only, not semantics</strong> — parse into a tree and it passes; whether the tool runs correctly is a worry for the later execution stage.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/functions.py</span><span class="ln">derivation entry (simplified)</span></div>
<pre><span class="kw">def</span> <span class="fn">derive_openai_json_schema</span>(source_code: str, name=<span class="kw">None</span>):
    mock = <span class="fn">_parse_function_from_source</span>(source_code, name)  <span class="cm"># pure AST, never exec</span>
    <span class="kw">return</span> <span class="fn">generate_schema</span>(mock, name=name)            <span class="cm"># reuse Lesson 17's generator</span>
</pre></div>
<p>Keep this main thread in mind: the deriver <strong>rewrites none</strong> of the schema-generation logic. Its job is to "translate" a piece of source into an input that <span class="mono">generate_schema</span> will accept; the thing that actually generates the schema is still Lesson 17's machine. One fewer implementation means one fewer place that can drift out of sync with another.</p>
<h2>MockFunction: the "fake function" that fools inspect</h2>
<p>Here's the snag: <span class="mono">generate_schema</span> expects a <strong>real function object</strong> — it wants to call <span class="mono">inspect.signature</span> on it and read <span class="mono">__doc__</span>. But all we hold are parts pulled from the AST, not a real function. Letta's move is to whip up a "fake function" on the fly — <span class="mono">MockFunction</span> — gathering just the few attributes <span class="mono">inspect</span> cares about and ignoring everything else.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/functions.py</span><span class="ln">MockFunction</span></div>
<pre><span class="kw">class</span> <span class="fn">MockFunction</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self, name, docstring, signature):
        self.__name__ = name
        self.__doc__ = docstring
        self.__signature__ = signature        <span class="cm"># set this, and inspect.signature just works</span>
    <span class="kw">def</span> <span class="fn">__call__</span>(self, *a, **k):
        <span class="kw">raise</span> <span class="fn">NotImplementedError</span>(<span class="st">"mock function cannot be called"</span>)
</pre></div>
<div class="cellgroup"><div class="cg-cap"><b>MockFunction gathers just three attributes</b></div><div class="cells"><span class="cell hl">__name__ name</span><span class="sep">·</span><span class="cell hl">__doc__ docstring</span><span class="sep">·</span><span class="cell hl">__signature__ params</span></div></div>
<div class="note tip"><span class="ni">💡</span><span class="nx">The key point: once <span class="mono">__signature__</span> is set explicitly, <span class="mono">inspect.signature(mock)</span> and <span class="mono">parse(mock.__doc__)</span> work fine on code that has <strong>never run</strong> — <span class="mono">inspect</span> only looks at these attributes and doesn't care whether the object is a real function or a fake. This is exactly why uploaded tools can <strong>reuse</strong> <span class="mono">generate_schema</span> unchanged.</span></div>
<p>Don't miss another detail: <span class="mono">__call__</span> is <strong>deliberately</strong> written to raise <span class="mono">NotImplementedError</span>. <span class="mono">MockFunction</span>'s only mission is "let <span class="mono">inspect</span> read attributes"; it shouldn't and can't be truly called. Should some code slip and execute it as a tool, it blows up with a clear error at once, rather than quietly returning <span class="mono">None</span> and hiding the bug — a textbook piece of <strong>defensive design</strong>.</p>
<p>Behind this is Python's <strong>duck typing</strong> philosophy: "if it walks like a duck and quacks like a duck, treat it as a duck." <span class="mono">inspect</span> checks no pedigree, only attributes: produce a <span class="mono">__signature__</span> and it treats you as an object that has a signature. <span class="mono">MockFunction</span> banks on exactly this, using the smallest possible "disguise" to fool an entire toolchain built for real functions.</p>
<h2>What the AST reads statically</h2>
<p>The real workhorse is <span class="mono">_parse_function_from_source</span>. It first <span class="mono">ast.parse</span>s the source into a syntax tree, picks out the function node, then <strong>rebuilds</strong> an <span class="mono">inspect.Signature</span> item by item: parameter names come from the node, types from the annotations, and defaults from <span class="mono">ast.literal_eval</span>'s safe evaluation (literals only, no expressions executed). The whole signature is "assembled," with nothing anywhere needing the original code to run.</p>
<p>A concrete example: a user uploads a tool whose signature is <span class="mono">def lookup(city: str = "NYC")</span>. After reading the tree, the parser obtains — function name <span class="mono">lookup</span>, parameter <span class="mono">city</span> of type <span class="mono">str</span>, default <span class="mono">"NYC"</span>, plus the description line from the docstring. All of it comes from "reading structure"; the line in the body that does the real work never ran once.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/functions/functions.py</span><span class="ln">_parse_function_from_source (key points)</span></div>
<pre><span class="kw">def</span> <span class="fn">_parse_function_from_source</span>(src, name):
    tree = ast.<span class="fn">parse</span>(src)               <span class="cm"># syntax error -> LettaToolCreateError</span>
    func = [n <span class="kw">for</span> n <span class="kw">in</span> ast.<span class="fn">walk</span>(tree) <span class="kw">if</span> isinstance(n, ast.FunctionDef)][-<span class="nb">1</span>]  <span class="cm"># take the last function</span>
    <span class="cm"># rebuild inspect.Signature: param names, annotations, defaults via ast.literal_eval</span>
    <span class="cm"># rebuild source-defined BaseModels in place via type(name, (BaseModel,), {...}), no import</span>
    <span class="kw">return</span> <span class="fn">MockFunction</span>(func.name, ast.<span class="fn">get_docstring</span>(func), sig)
</pre></div>
<p>By the way, the docstring is read straight off the parsed function node (its first statement, if a string literal, is the docstring) — pure AST, no regex. Letta's AST helper <span class="mono">ast_parsers.py::get_function_name_and_docstring</span> uses the stdlib <span class="mono">ast.get_docstring</span> for exactly this, handling multi-line text, indentation, and escaping for you.</p>
<div class="note info"><span class="ni">📌</span><span class="nx">If a piece of source has <strong>multiple functions</strong>, it takes the <strong>last</strong> <span class="mono">FunctionDef</span> (convention: the tool is the last function defined in the file). The related AST helpers live in <span class="mono">letta/functions/ast_parsers.py</span>, where <span class="mono">resolve_type</span> resolves types via a <strong>whitelist</strong> with <span class="mono">allow_unsafe_eval=False</span> by default — though it kicks in <strong>later, when the tool runs and the model's incoming args are coerced</strong>, holding the same "no code-execution-via-parsing" line.</span></div>
<p>Two more "safety valves" hide here, worth remembering. The first targets defaults: the parser doesn't use <span class="mono">eval</span> but <span class="mono">ast.literal_eval</span> — which accepts only literals like numbers, strings, lists, and dicts, and outright rejects a function call or arbitrary expression, sealing off the gap of "sneaking code in even while evaluating a default."</p>
<p>The second targets type annotations: during derivation an unrecognized name is <strong>not</strong> imported or evaluated — it's left as a plain string (and a Pydantic model defined in the source is stubbed in place), via the static parsing in functions.py rather than truly resolving the type. Together the two valves ensure "parsing" never degrades into "executing."</p>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>One line sums up the craft: <strong>"generate the schema of code you refuse to run."</strong> The plainest way to read a function's signature is <span class="mono">import + inspect</span>, but importing user code = executing arbitrary code on your server. Letta's trick: first <span class="mono">ast.parse</span> into a syntax tree (read-only, no run), then build a <span class="mono">MockFunction</span> carrying only <span class="mono">__name__/__doc__/__signature__</span>, and feed it to the <strong>exact same</strong> <span class="mono">generate_schema</span>.</p>
<p>The result: the model gets a real schema, yet the server <strong>ran not one line</strong> of user code. Even a Pydantic type defined in the source is rebuilt in place via <span class="mono">type(name,(BaseModel,),{})</span> as a stub rather than imported. It cleverly turns "security" into a "parsing" problem — a prelude to Lesson 20's sandbox philosophy: <strong>"a tool's code is untrusted from start to finish."</strong></p>
<p>This idea of "turning a dangerous operation into a safe one" is hugely valuable in engineering: instead of piling locks on dangerous behavior, it makes the danger <strong>impossible to occur by design</strong>. Remember this pattern and you'll see it again and again in many fine systems.</p>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Memory hook: every bit of cleverness in this lesson compresses to one line — <strong>"read it, but never run it."</strong> Reading relies on the AST; reconnecting to the old pipeline relies on <span class="mono">MockFunction</span>; safety relies on never importing.</span></div>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p>This machinery is scattered across a few spots, but the thread is clear:</p>
<ul>
<li><strong>The deriver trio</strong> (all in <span class="mono">letta/functions/functions.py</span>): <span class="mono">derive_openai_json_schema</span>, <span class="mono">MockFunction</span>, <span class="mono">_parse_function_from_source</span>.</li>
<li><strong>AST helpers</strong>: <span class="mono">letta/functions/ast_parsers.py</span>, with <span class="mono">get_function_name_and_docstring</span> and the whitelist type resolver <span class="mono">resolve_type</span>.</li>
<li><strong>TypeScript derivation</strong>: <span class="mono">letta/functions/typescript_parser.py::derive_typescript_json_schema</span>.</li>
<li><strong>Wired at creation time</strong>: <span class="mono">letta/services/tool_manager.py</span> (custom and no schema → call the deriver) → <span class="mono">letta/services/tool_schema_generator.py::generate_schema_for_tool_creation</span> (dispatch Python / TypeScript by <span class="mono">source_type</span>).</li>
</ul>
<p>Stringing it together: <strong>at creation</strong> <span class="mono">tool_manager</span> triggers it, <strong>derivation</strong> lands in the <span class="mono">functions.py</span> trio, <strong>type resolution</strong> relies on <span class="mono">ast_parsers.py</span>, and <strong>language dispatch</strong> looks at <span class="mono">source_type</span>. Follow this line through the source and you'll rarely get lost.</p>
</div>
<div class="card warn"><div class="tag">⚠️ Common misconceptions</div>
<ul>
<li><span class="mono">MockFunction</span> lives in <strong>functions.py</strong>, <strong>not</strong> in <span class="mono">ast_parsers.py</span> — don't look in the wrong file.</li>
<li>Multi-function source takes the <strong>last</strong> <span class="mono">FunctionDef</span>, <strong>not the first</strong>.</li>
<li>Creating a TypeScript tool <strong>must pass an explicit <span class="mono">json_schema</span></strong>, or <span class="mono">ToolCreate</span> errors out.</li>
<li>Schema derivation happens <strong>only at creation</strong>, <strong>no longer</strong> in a pydantic validator: <span class="mono">Tool.refresh_source_code_and_json_schema</span> only <strong>warns</strong> on a custom tool missing its schema, never recomputes it.</li>
<li><span class="mono">ast.literal_eval</span> accepts <strong>literals only</strong>; don't assume it can evaluate arbitrary default expressions — that is precisely why it is "safe."</li>
</ul>
</div>
<h2>TypeScript tools</h2>
<p>Tools needn't be written in Python alone. <span class="mono">letta/functions/typescript_parser.py::derive_typescript_json_schema</span> handles TS: it <strong>skips the AST</strong> and instead uses <strong>regex</strong> to scan the signature of <span class="mono">export function</span>, then pulls parameter descriptions from <span class="mono">JSDoc</span> comments; a parameter name followed by <span class="mono">?</span> is treated as optional.</p>
<p>Its type mapping is coarser: <span class="mono">union</span> always maps to <span class="mono">string</span>, and <span class="mono">any</span> also lands on <span class="mono">string</span>. The source type comes from the <span class="mono">letta/schemas/enums.py::ToolSourceType</span> enum, with three values: <span class="mono">python / typescript / json</span>.</p>
<div class="note info"><span class="ni">👉</span><span class="nx">But there's a hard constraint: a TS tool <strong>must</strong> bring its own <span class="mono">json_schema</span> at API creation (<span class="mono">ToolCreate.validate_typescript_requires_schema</span>; missing it raises <span class="mono">ValueError</span>). So the "auto-derive schema" path <strong>mainly serves Python tools</strong>; a TS schema is usually supplied explicitly by the caller.</span></div>
<p>Let's clarify <span class="mono">source_type</span>'s role: it is just a "language label" telling the deriver which parser to use for this source — Python takes the AST, TypeScript takes regex, and JSON means "I've already given you the schema, no derivation needed."</p>
<div class="cellgroup"><div class="cg-cap"><b>The three values of ToolSourceType</b></div><div class="cells"><span class="cell hl">python · AST derivation</span><span class="sep">·</span><span class="cell">typescript · regex, needs explicit schema</span><span class="sep">·</span><span class="cell">json · schema provided directly</span></div></div>
<p>So why must TS "supply a schema explicitly"? Because the slice of TypeScript syntax regex can cover reliably is far less complete and rigorous than Python's AST. Rather than guess wrong on complex types, let the caller hand over the authoritative schema directly. So the convenient "auto-derive" channel is, first and foremost, in service of Python.</p>
<p>While we're at it, JSDoc's role: the TS parser pulls each parameter's description from <span class="mono">/** ... */</span> comments, just as Python takes descriptions from the docstring — the "manual" shown to the model lives in comments in both languages, arriving at the same place by different roads. The only difference is extraction: one scans text with regex, the other reads structure with the AST.</p>
<h2>Digging a little deeper</h2>
<p>Let's lay out the "why"s most likely to trip you up, each with an example, the reason, and the source location.</p>
<details class="accordion"><summary>① Why use the AST instead of importing directly?</summary><div class="acc-body">
<p><strong>Example:</strong> the user's source has a line <span class="mono">os.system("rm -rf /")</span> at the top level, outside any function definition; just <span class="mono">import</span> it and that line runs on your server. Note: the function is <strong>never called</strong> — merely "importing" is enough to trigger it, which is exactly what makes top-level code so frightening.</p>
<p><strong>Why:</strong> <span class="mono">import</span> executes a module's <strong>top-level code</strong>, which is like handing your server to a stranger — a standard RCE. <span class="mono">ast.parse</span>, by contrast, only reads the source into a <strong>syntax tree</strong> — purely static, zero side effects; read it a thousand times and nothing executes. The essence of safety is "read, never run."</p>
<p><strong>Source:</strong> <span class="mono">letta/functions/functions.py::_parse_function_from_source</span> is built entirely on <span class="mono">ast</span>, with not a single <span class="mono">exec/import</span>.</p>
<p><strong>Going further:</strong> for this very reason, Letta treats "untrusted code" as a first principle running through the whole tool system — from deriving a schema to Lesson 20's sandboxed execution, all are different facets of this one principle.</p>
</div></details>
<details class="accordion"><summary>② How does MockFunction fool inspect?</summary><div class="acc-body">
<p><strong>Example:</strong> <span class="mono">inspect.signature(mock)</span> still returns a full signature, even though <span class="mono">mock</span> was never defined as a real function and calling it raises <span class="mono">NotImplementedError</span> outright.</p>
<p><strong>Why:</strong> when reading a signature <span class="mono">inspect</span> looks only at the object's <span class="mono">__signature__</span> attribute, and for docs only at <span class="mono">__doc__</span> — it <strong>doesn't verify</strong> whether the object is a "real function." With those few attributes in place, it works as usual. This is the key to uploaded tools reusing <span class="mono">generate_schema</span> unchanged.</p>
<p><strong>Source:</strong> <span class="mono">letta/functions/functions.py::MockFunction</span> sets these three attributes by hand in <span class="mono">__init__</span>.</p>
<p><strong>Going further:</strong> this also explains why you needn't "really build a function": <span class="mono">generate_schema</span> never wanted executability, only <strong>describability</strong> — with signature and docs in place, the description is complete.</p>
</div></details>
<details class="accordion"><summary>③ Why take the last function? What about unknown types?</summary><div class="acc-body">
<p><strong>Example:</strong> the source has a few helper functions first and the tool body last, so the parser takes the <strong>last</strong> <span class="mono">FunctionDef</span>.</p>
<p><strong>Why:</strong> the convention is "the tool is the function at the end of the file." If the source <strong>defines</strong> a Pydantic model, a <strong>stub class</strong> is rebuilt in place with <span class="mono">type(name, (BaseModel,), {...})</span> rather than importing the real definition — letting the signature take shape while holding the "don't run user code" line.</p>
<p><strong>Source:</strong> <span class="mono">_parse_function_from_source</span> (last <span class="mono">FunctionDef</span>, defaults via <span class="mono">ast.literal_eval</span>); the whitelist resolver <span class="mono">ast_parsers.py::resolve_type</span> is used later for arg coercion.</p>
<p><strong>Going further:</strong> the stubbing rests on the one line <span class="mono">type(name,(BaseModel,),{})</span> — it synthesizes a class out of thin air at runtime, just so the signature "has a name to fill in," never touching the definition the user actually meant to reference.</p>
</div></details>
<details class="accordion"><summary>④ When and where is derivation actually triggered?</summary><div class="acc-body">
<p><strong>Example:</strong> you create a custom Python tool but give no <span class="mono">json_schema</span>, and the server derives the schema for you during the <strong>creation flow</strong>. Conversely, if you've already given a schema, this step is skipped — derivation is just a "fill in what's missing" fallback.</p>
<p><strong>Why:</strong> the wiring lands in <span class="mono">tool_manager</span> (which judges "custom and missing schema") → <span class="mono">generate_schema_for_tool_creation</span> (dispatching Python / TS by <span class="mono">source_type</span>). It is <strong>no longer</strong> in a pydantic validator, so one creation counts as one derivation; and since TS must supply a schema explicitly, it usually doesn't fall into the auto-derive branch.</p>
<p><strong>Source:</strong> <span class="mono">letta/services/tool_manager.py</span> and <span class="mono">letta/services/tool_schema_generator.py::generate_schema_for_tool_creation</span>.</p>
<p><strong>Going further:</strong> placing derivation at creation rather than at every validation both spares repeated computation and makes the schema a contract "settled at the moment of creation and stable thereafter."</p>
</div></details>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li><strong>When registering a custom tool, the schema is derived by pure AST</strong>: a schema is built from the source string, <strong>never running</strong> that code.</li>
<li><strong><span class="mono">derive_openai_json_schema</span> = <span class="mono">_parse_function_from_source</span> + reusing <span class="mono">generate_schema</span></strong>: it converges on the same generator as Lesson 17.</li>
<li><strong><span class="mono">MockFunction</span> provides <span class="mono">__name__ / __doc__ / __signature__</span></strong>: it fools <span class="mono">inspect</span> with the trio, and raises if called.</li>
<li><strong>Take the last <span class="mono">FunctionDef</span>, stub unknown types</strong>: an undefined BaseModel is filled by <span class="mono">type(name,(BaseModel,),{})</span>, no import.</li>
<li><strong>A TS tool must supply <span class="mono">json_schema</span> explicitly</strong>: auto-derivation mainly serves Python.</li>
<li><strong>Derivation happens only at creation</strong>: wired in <span class="mono">tool_manager</span> → <span class="mono">tool_schema_generator</span>, no longer in a pydantic validator.</li>
</ul>
<p>Read these together: <strong>not running</strong> is the principle, <strong>AST parsing</strong> is the means, <strong>MockFunction</strong> is the adapter, and <strong>reusing generate_schema</strong> is the payoff. The four interlock, none dispensable — exactly what a "safe yet effortless" design should look like.</p>
</div>

<p>Looking back, this lesson really told just one story: <strong>restating "security" as "parsing."</strong> Once you refuse to run user code, "understanding it" turns from a runtime problem into a pure text-analysis problem — and text analysis is exactly the AST's forte. <span class="mono">MockFunction</span> then acts as a bridge, seamlessly reconnecting the analyzed parts to Lesson 17's mature generator.</p>

<p>By now a tool has a schema, can be "seen" by the model, and can be invoked. But when an agent <strong>actually executes</strong> a tool, how does it know "which way to run it" — call it directly in-process, drop it into a sandbox for isolated execution, or reach out to an external server? That is the question <strong>Lesson 19, "tool dispatch and execution,"</strong> will answer. In other words, the schema solves "how the model understands a tool," while execution must solve "how the system runs a tool safely" — and that story is only half told.</p>

"""}


LESSON_19 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第 14 课讲 agent 的执行循环时，"执行工具"只用一行带过；第 17、18 课又让工具长出了 schema、能被模型"看见"并调用。可是当模型真吐出一个工具调用、系统<strong>要去跑它</strong>的那一步，我们一直没拆开看。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课就把"执行"摊开：当 agent 真要跑一个工具时，它怎么知道<strong>该用哪种方式</strong>跑——进程内直接调？丢进沙箱隔离执行？还是开一条网络连接到外部服务器？答案藏在一个叫 <span class="mono">ToolType</span> 的标签和一个工厂里。</p>
<div class="note info"><span class="ni">❓</span><span class="nx">带着一个具体问题读下去：当模型说"调用 <span class="mono">run_code</span>"时，到底是<strong>谁、在哪里、用什么方式</strong>真正把这段代码跑起来的？答案不是某一个函数，而是"类型标签 + 工厂 + 执行器"这一整套机制——这一课就是把它拆给你看。</span></div>

<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>把"执行工具"想成医院的<strong>分诊台</strong>。同样是来"看病"，前台并不自己治，而是按你的<strong>科室标签</strong>把你送到不同地方。</p>
<p>内科的小毛病，直接进诊室当场看（对应 <span class="mono">core</span>，进程内直跑）；要动刀的，送进<strong>手术室</strong>隔离操作（对应 <span class="mono">sandbox</span>，在沙箱里跑陌生代码）；本院看不了的疑难，<strong>转外院会诊</strong>（对应 <span class="mono">MCP</span>，连外部服务器）。</p>
<p>关键在于：分诊台自己<strong>不看病</strong>，它只做一件事——<strong>按类型把你送到对的地方</strong>。Letta 里这个分诊台，就是下面要讲的"工厂"。</p>
</div>

<p>这个类比里其实藏着这一课的全部要点：<strong>同样一句"执行工具"，落地时有好几种完全不同的跑法</strong>；决定走哪条路的，是工具身上的类型标签和那个"分诊"的工厂。把这两样搞懂，"执行"这一步就透明了。</p>

<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>每个 <span class="mono">Tool</span> 都带一个 <span class="mono">ToolType</span>（共 11 种），相当于贴在工具上的"科室标签"。</p>
<p><span class="mono">tool_execution_manager.py::ToolExecutorFactory</span> 是那个分诊台：它按 <span class="mono">ToolType</span> 把工具映射到对应的<strong>执行器</strong>。但真正被 agent 循环调用的入口，是同一个文件里的 <span class="mono">ToolExecutionManager::execute_tool_async</span>。</p>
<p>执行器们各管一摊：<span class="mono">core</span> 进程内直跑、<span class="mono">builtin</span> 跑内置工具、<span class="mono">files</span> 管文件、<span class="mono">mcp</span> 连外部服务器、<span class="mono">sandbox</span> 跑自定义代码。</p>
<p>所以这一课只讲三件事：<strong>ToolType 是什么</strong>、<strong>工厂怎么按它选执行器</strong>、<strong>每个执行器到底干啥</strong>。</p>
</div>

<div class="note tip"><span class="ni">🗺️</span><span class="nx">读这一课可以盯住一条主线：<strong>标签（ToolType）→ 工厂（选执行器）→ 入口（ToolExecutionManager）→ 五个执行器（各种运行时）→ 统一结果（ToolExecutionResult）</strong>。下面就顺着这条线一节一节走。</span></div>

<h2>ToolType：工具的"种类标签"</h2>
<p>先认标签。<span class="mono">schemas/enums.py::ToolType</span> 一共 11 种，可以归成三类——<strong>内置</strong>（Letta 自带，进程内或受控执行）、<strong>自定义</strong>（你写的，默认进沙箱）、<strong>外部</strong>（连第三方）。</p>
<div class="cellgroup"><div class="cg-cap"><b>内置 · Letta 自带（7 种）</b></div><div class="cells"><span class="cell hl">letta_core</span><span class="sep">·</span><span class="cell">letta_memory_core</span><span class="sep">·</span><span class="cell">letta_multi_agent_core</span><span class="sep">·</span><span class="cell">letta_sleeptime_core</span><span class="sep">·</span><span class="cell">letta_voice_sleeptime_core</span><span class="sep">·</span><span class="cell">letta_builtin</span><span class="sep">·</span><span class="cell">letta_files_core</span></div></div>
<div class="cellgroup"><div class="cg-cap"><b>自定义 · 默认值（1 种）</b></div><div class="cells"><span class="cell hl">custom</span></div></div>
<div class="cellgroup"><div class="cg-cap"><b>外部 · 第三方（3 种）</b></div><div class="cells"><span class="cell">external_langchain（弃用）</span><span class="sep">·</span><span class="cell">external_composio（弃用）</span><span class="sep">·</span><span class="cell hl">external_mcp</span></div></div>
<div class="note info"><span class="ni">🏷️</span><span class="nx"><span class="mono">custom</span> 是<strong>默认值</strong>：注册一个工具如果没被归到别的类，它就是 <span class="mono">custom</span>——而 <span class="mono">custom</span> 会兜底走沙箱。两个 <span class="mono">external_langchain / external_composio</span> 已弃用，真正活跃的外部类型只有 <span class="mono">external_mcp</span>。</span></div>
<p>为什么要分这么多种？因为 Letta 的工具来源天差地别：有的是框架自带的核心能力（发消息、改记忆），有的是平台内置的实用工具（跑代码、搜网页），有的是你临时写的业务函数，还有的根本不在本地、得连出去。给每个工具贴上类型标签，后面的工厂才能照标签把它们派到正确的运行时。</p>
<p>内置那 7 种又按用途细分：<span class="mono">letta_core</span> 管对话与控制流，<span class="mono">letta_memory_core</span> 改写记忆，<span class="mono">letta_sleeptime_core</span> 与 <span class="mono">letta_voice_sleeptime_core</span> 服务"睡眠时间"里的后台整理，<span class="mono">letta_multi_agent_core</span> 负责多 agent 协作，<span class="mono">letta_builtin</span> 跑代码、搜网，<span class="mono">letta_files_core</span> 管文件。</p>

<h2>工厂：按类型选执行器</h2>
<p>标签有了，谁来读标签、派活？是 <span class="mono">ToolExecutorFactory</span>。它内部存了一张 <span class="mono">_executor_map</span>，把 <span class="mono">ToolType</span> 映射到执行器类；<span class="mono">get_executor</span> 查表、实例化、返回一个执行器。</p>
<div class="flow">
<div class="node"><div class="nt">tool.tool_type</div><div class="nd">工具上的标签</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">get_executor</div><div class="nd">查 _executor_map</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">具体执行器</div><div class="nd">LettaCore / Sandbox …</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">execute(...)</div><div class="nd">真正跑工具</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">ToolExecutionResult</div><div class="nd">统一结果</div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">循环只说"调这个工具"，<strong>怎么跑</strong>由 <span class="mono">ToolType</span> + 工厂决定：进程内直跑 / 沙箱 / 连 MCP server——同一个 <span class="mono">execute</span> 接口，藏起三种运行时。</span></div>
<p>还要记住流程的<strong>终点</strong>：不管走哪条路，所有执行器都返回同一种 <span class="mono">ToolExecutionResult</span>。差异被藏在中间，出口却是统一的——这正是"多态"的形状。</p>
<p>实现上，<span class="mono">_executor_map</span> 是一个 <span class="mono">ClassVar</span>——类级别的字典，所有实例共享。查表就是普通的 <span class="mono">dict.get(key, default)</span>：命中就拿映射好的执行器类，落空就拿第二个参数 <span class="mono">SandboxToolExecutor</span>。短短一行，既是"分发表"，又是"安全网"。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/tool_execution_manager.py</span><span class="ln">工厂（简化）</span></div><pre><span class="kw">class</span> <span class="fn">ToolExecutorFactory</span>:
    _executor_map = {
        ToolType.LETTA_CORE: LettaCoreToolExecutor,
        ToolType.LETTA_MEMORY_CORE: LettaCoreToolExecutor,
        ToolType.LETTA_SLEEPTIME_CORE: LettaCoreToolExecutor,
        ToolType.LETTA_MULTI_AGENT_CORE: SandboxToolExecutor,
        ToolType.LETTA_BUILTIN: LettaBuiltinToolExecutor,
        ToolType.LETTA_FILES_CORE: LettaFileToolExecutor,
        ToolType.EXTERNAL_MCP: ExternalMCPToolExecutor,
    }
    <span class="kw">def</span> <span class="fn">get_executor</span>(cls, tool_type, ...):
        cls_ = cls._executor_map.<span class="fn">get</span>(tool_type, SandboxToolExecutor)   <span class="cm"># 未映射 -> 兜底沙箱</span>
        <span class="kw">return</span> cls_(...)
</pre></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">看 <span class="mono">get_executor</span> 那行的 <span class="mono">.get(tool_type, SandboxToolExecutor)</span>：<strong>没在表里的类型，一律兜底走沙箱</strong>。<span class="mono">custom</span>、<span class="mono">letta_voice_sleeptime_core</span>、两个弃用的 external 这 4 种落这里（<span class="mono">letta_multi_agent_core</span> 则是<strong>显式</strong>映射到沙箱，不算兜底）。所以"自定义工具＝在沙箱里跑"是<strong>默认</strong>，不是特例。</span></div>
<p>这其实是经典的<strong>工厂模式</strong>：把"<em>到底用哪一种实现</em>"收拢到一处，调用方只管开口要"一个执行器"，不必知道背后是哪个类、怎么构造。日后想加一种工具类型，往 <span class="mono">_executor_map</span> 里登记一行即可，循环和入口的代码一个字都不用改。</p>

<h2>真正的入口：ToolExecutionManager</h2>
<p>工厂只负责"选人"。真正被 agent 循环调用的，是 <span class="mono">ToolExecutionManager::execute_tool_async</span>：它用工厂拿到执行器，<strong>计时</strong>、<strong>截断超长返回</strong>、把异常<strong>包成结果对象</strong>，再交回循环。</p>
<p>为什么把这些杂活都塞进入口？因为工具是 agent 里最"不可控"的一环——可能读数据库、跑代码、连网络，耗时和失败方式千差万别。把计时、截断、异常包装统一收在入口这一层，循环就不必为每种工具单独操心；每步耗时的可观测性、不被撑爆不抛异常的稳定性，也都集中、可控。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/tool_execution_manager.py</span><span class="ln">入口（简化）</span></div><pre><span class="kw">async def</span> <span class="fn">execute_tool_async</span>(self, function_name, function_args, tool, ...):
    executor = ToolExecutorFactory.<span class="fn">get_executor</span>(tool.tool_type, ...)
    result = <span class="kw">await</span> executor.<span class="fn">execute</span>(function_name, function_args, tool, actor, ...)
    <span class="kw">if</span> len(return_str) > tool.return_char_limit:   <span class="cm"># 超长截断</span>
        ...
    <span class="kw">return</span> result   <span class="cm"># ToolExecutionResult(status, func_return, stdout, stderr, ...)</span>
</pre></div>
<div class="note tip"><span class="ni">🧭</span><span class="nx">分清两层：工厂只回答"<strong>用哪个执行器</strong>"，<span class="mono">ToolExecutionManager</span> 才是循环真正调的<strong>入口</strong>——它负责计时、超 <span class="mono">return_char_limit</span> 截断、把异常统一包成 <span class="mono">ToolExecutionResult(status="error")</span>。</span></div>
<p>那个统一的返回值 <span class="mono">ToolExecutionResult</span> 长什么样？它带 <span class="mono">status</span>（成功或失败）、<span class="mono">func_return</span>（工具的返回值）、<span class="mono">stdout / stderr</span>（运行时打印的内容），还有 <span class="mono">sandbox_config_fingerprint</span> 等字段。无论 core 直跑还是沙箱里跑，循环拿到的都是这同一个壳——这也是入口愿意花力气把一切都归一成它的原因。</p>

<h2>五个执行器，各管一摊</h2>
<p>工厂表里点名的、加上兜底的，一共五个执行器。下面这张表把"标签 → 执行器 → 类别 → 典型工具"对上号。</p>
<table class="t">
<tr><th>ToolType</th><th>执行器</th><th>类别</th><th>典型工具</th></tr>
<tr><td class="mono">letta_core</td><td class="mono">LettaCoreToolExecutor</td><td>进程内</td><td class="mono">send_message · conversation_search</td></tr>
<tr><td class="mono">letta_memory_core</td><td class="mono">LettaCoreToolExecutor</td><td>进程内 · 记忆</td><td class="mono">core_memory_append · core_memory_replace</td></tr>
<tr><td class="mono">letta_builtin</td><td class="mono">LettaBuiltinToolExecutor</td><td>受控内置</td><td class="mono">run_code · web_search · fetch_webpage</td></tr>
<tr><td class="mono">letta_files_core</td><td class="mono">LettaFileToolExecutor</td><td>文件</td><td class="mono">open_files · grep_files</td></tr>
<tr><td class="mono">external_mcp</td><td class="mono">ExternalMCPToolExecutor</td><td>外部服务器</td><td class="mono">MCP 工具</td></tr>
<tr><td class="mono">custom（兜底）</td><td class="mono">SandboxToolExecutor</td><td>沙箱</td><td class="mono">你写的自定义工具</td></tr>
</table>
<p>把这五个执行器各自的活儿摊开说：</p>
<ul>
<li><span class="mono">LettaCoreToolExecutor</span>：core、<strong>记忆</strong>、sleeptime 三摊工具全揽下，统统<strong>进程内直跑</strong>。改核心记忆的 <span class="mono">core_memory_append / core_memory_replace</span> 就在这里执行，不绕沙箱、延迟最低。</li>
<li><span class="mono">LettaBuiltinToolExecutor</span>：跑平台内置工具——<span class="mono">run_code</span> 执行代码、<span class="mono">web_search</span> 搜网、<span class="mono">fetch_webpage</span> 抓网页，是一组"受控"的实用能力。</li>
<li><span class="mono">LettaFileToolExecutor</span>：专管文件类工具，比如 <span class="mono">open_files</span>、<span class="mono">grep_files</span>，服务于把文件读进上下文、在文件里检索。</li>
<li><span class="mono">ExternalMCPToolExecutor</span>：唯一"往外连"的执行器，把调用转发给外部 MCP 服务器，本地一行业务代码都不跑。</li>
<li><span class="mono">SandboxToolExecutor</span>：自定义工具和所有未映射类型的<strong>兜底</strong>，把陌生代码丢进隔离沙箱里执行——它怎么跑、为什么敢跑，是第 20 课的主题。</li>
</ul>
<p>举三个例子把分发走一遍。模型要 <span class="mono">core_memory_append</span>（类型 <span class="mono">letta_memory_core</span>），工厂交给 <span class="mono">LettaCoreToolExecutor</span>，在进程内当场改记忆；要 <span class="mono">run_code</span>（<span class="mono">letta_builtin</span>），交给 <span class="mono">LettaBuiltinToolExecutor</span> 受控执行；要你自己写的 <span class="mono">calculate_invoice</span>（没归类、落在 <span class="mono">custom</span>），工厂在表里找不到、兜底交给 <span class="mono">SandboxToolExecutor</span> 丢进沙箱。同一行调用，三种完全不同的命运。</p>
<p>它们都继承基类 <span class="mono">tool_executor_base.py::ToolExecutor</span>，统一签名 <span class="mono">async def execute(...) -&gt; ToolExecutionResult</span>。注意记忆工具 <span class="mono">core_memory_append</span> 也归 <span class="mono">LettaCoreToolExecutor</span>，在<strong>进程内直跑</strong>，并不进沙箱。</p>
<div class="note info"><span class="ni">🧩</span><span class="nx">统一接口的妙处：循环只认 <span class="mono">execute(...) -&gt; ToolExecutionResult</span> 这一个签名。无论底层是改记忆、跑代码、还是连外部服务器，对循环来说都"长得一样"——于是它能对任何工具一视同仁地调用、计时、记录、再把结果接回对话。</span></div>
<p>进程内直跑和丢进沙箱，本质是一道"信任与速度"的取舍。可信的核心工具（改记忆、发消息）直接在进程里跑，最快也最省事；来路不明的自定义代码则必须先隔离，宁可慢一点、麻烦一点，也不能让它碰到服务端的内存和权限。把这道取舍交给"类型"来表达，正是这套设计最聪明的地方。</p>

<div class="cute">
<div class="row"><span class="emoji">🏭</span><span class="lab">按 ToolType 分拣</span><span class="arrow">→</span><span class="emoji">🧠</span><span class="bubble">core · 进程内</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">同一座工厂</span><span class="arrow">→</span><span class="emoji">🔧</span><span class="bubble">builtin · 内置</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">不同传送带</span><span class="arrow">→</span><span class="emoji">📁</span><span class="bubble">files · 文件</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">各走各的</span><span class="arrow">→</span><span class="emoji">🔌</span><span class="bubble">mcp · 外部</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">兜底那条</span><span class="arrow">→</span><span class="emoji">📦</span><span class="bubble">sandbox · 沙箱</span></div>
<div class="cap">工厂按 ToolType 把每个工具送上对的传送带：进程内、内置、文件、外部、沙箱</div>
</div>

<p>所以"分发"这件事可以一句话收口：<strong>工具带着类型标签进来，工厂照标签发往对应执行器，执行器各跑各的运行时，最后都吐出同一种结果</strong>。下面单看最特别的一条传送带——通往外部世界的 MCP。</p>

<h2>MCP：连接外部工具服务器</h2>
<p>前面四类都在 Letta 自己家里跑。<strong>MCP</strong>（Model Context Protocol）不一样：工具其实活在<strong>外部服务器</strong>上，Letta 只是个客户端，把调用<strong>转发</strong>过去、再把结果取回来。</p>
<p>这类工具的 <span class="mono">tool_type</span> 是 <span class="mono">external_mcp</span>，还会被打上 <span class="mono">mcp:&lt;server&gt;</span> 标签（由 <span class="mono">ToolCreate.from_mcp</span> 设置）。执行时由 <span class="mono">ExternalMCPToolExecutor</span> 从标签里取出目标服务器名，交给 <span class="mono">MCPManager</span> 去连、去跑、再断开。</p>
<div class="note tip"><span class="ni">🌐</span><span class="nx">MCP 是个<strong>开放协议</strong>：任何人都能写一个 MCP server，暴露一批工具（查库、发邮件、调内部 API…）。Letta 这边只要登记服务器、导入工具，agent 就能调用，而工具的实现细节对 Letta 完全透明。</span></div>
<div class="vflow">
<div class="step"><div class="num">1</div><div class="sc"><h4>MCP 工具</h4><p>带 <span class="mono">mcp:&lt;server&gt;</span> 标签，类型 <span class="mono">external_mcp</span></p></div></div>
<div class="step"><div class="num">2</div><div class="sc"><h4>ExternalMCPToolExecutor</h4><p>从标签解析出目标服务器名</p></div></div>
<div class="step"><div class="num">3</div><div class="sc"><h4>MCPManager.execute_mcp_server_tool</h4><p>统一入口，掌管整条连接生命周期</p></div></div>
<div class="step"><div class="num">4</div><div class="sc"><h4>connect → execute → cleanup</h4><p>每次开新连接、跑完即断，不复用</p></div></div>
</div>
<p>把这条竖流连起来读：工具带着 <span class="mono">mcp:&lt;server&gt;</span> 标签进来，执行器从标签解析出服务器名，<span class="mono">MCPManager</span> 负责连上去、把调用发过去、收回结果、再断开。整个过程里 Letta 不执行任何工具逻辑，只做"中转"。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/mcp_tool_executor.py</span><span class="ln">MCP 执行（简化）</span></div><pre><span class="kw">async def</span> <span class="fn">execute</span>(self, function_name, function_args, tool, ...):
    server = <span class="fn">_tag_to_server</span>(tool.tags)        <span class="cm"># 从 "mcp:&lt;server&gt;" 标签取服务器名</span>
    resp, ok = <span class="kw">await</span> MCPManager().<span class="fn">execute_mcp_server_tool</span>(
        server, tool_name=function_name, tool_args=function_args, ...)   <span class="cm"># 连外部 server</span>
    <span class="kw">return</span> ToolExecutionResult(status=<span class="st">"success"</span> <span class="kw">if</span> ok <span class="kw">else</span> <span class="st">"error"</span>, func_return=resp)
</pre></div>
<div class="cellgroup"><div class="cg-cap"><b>三种 MCP 传输 · MCPServerType</b></div><div class="cells"><span class="cell hl">stdio</span><span class="sep">·</span><span class="cell">sse</span><span class="sep">·</span><span class="cell">streamable_http</span></div></div>
<p>换个角度看，MCP 把"工具"和"运行工具的进程"彻底解耦：实现、依赖、密钥都留在工具自己的服务器里，Letta 只通过协议发起调用。第三方因此能把一整套能力打包成一个 MCP server，挂到任意 agent 上即插即用。</p>
<p>代价是每次调用都得<strong>现连现断</strong>——<span class="mono">connect → execute → cleanup</span> 一条龙。好处是无状态、干净、互不影响；坏处是连接开销，所以 MCP 更适合"偶尔用一下的外部能力"，而非高频热路径。</p>
<div class="note info"><span class="ni">🔌</span><span class="nx">两个反直觉点：MCP 执行<strong>不走沙箱</strong>（它连的是外部 server，不是在本地跑代码）；而且每次调用都<strong>开一条新连接</strong>（<span class="mono">connect → execute → cleanup</span>）。真正的传输客户端在 <span class="mono">letta/services/mcp/</span>，<strong>不是</strong> <span class="mono">functions/mcp_client/</span>——后者只放配置类型与异常。</span></div>
<p>一句话记住 MCP：<strong>工具在别人家，Letta 上门调用</strong>。它扩展了 agent 的能力边界，又把"运行第三方代码"的风险留在第三方那边——这和本地沙箱是两条不同的安全思路。</p>
<p>换个比方：前面四类执行器像是"在自己家的不同房间干活"，MCP 则像"打电话叫外卖"——活儿在别人那儿干，你只负责下单和收货。这也解释了 MCP 为什么不走沙箱：沙箱是用来隔离"在你家里跑的陌生代码"的，而 MCP 的代码压根不在你家跑。</p>

<div class="card spark"><div class="tag">💡 设计亮点</div>
<p><strong>"一次调用，背后是好几种运行时。"</strong> 从第 14 课循环的视角看，"调一个工具"永远是统一的一行代码。</p>
<p>可底下却天差地别：进程内改核心记忆（<span class="mono">LettaCore</span>）、shell 出去在沙箱 venv 里跑陌生代码（<span class="mono">Sandbox</span>）、开一条网络连接到 MCP 服务器（<span class="mono">ExternalMCP</span>）。<span class="mono">ToolType</span> + 工厂，就是把这些差异藏起来的<strong>多态</strong>。</p>
<p>还有个反直觉真相：11 种 <span class="mono">ToolType</span> 其实只对应 <strong>5 个执行器类</strong>——<span class="mono">_executor_map</span> 显式登记了 <strong>7 条</strong>（多种类型共用 <span class="mono">LettaCore</span>），剩下 4 种（<span class="mono">custom</span>、voice-sleeptime、两个弃用 external）才<strong>兜底走 <span class="mono">SandboxToolExecutor</span></strong>。"自定义＝沙箱"是默认，不是特例。</p>
<p>而所有执行器，最后都返回同一个 <span class="mono">ToolExecutionResult</span>——正是第 16 课工具规则违规时用的那个类型。出口统一，差异内敛。</p>
<p>放进整条工具链看更清楚：第 17、18 课让工具"有了 schema、能被看见"，这一课让工具"被正确地跑起来"。模型那端永远是统一的函数调用，系统这端却悄悄做了一次<strong>按类型的运行时选择</strong>——这正是好抽象的样子：上层简单，下层灵活。</p>
<p>换句话说，<span class="mono">ToolType</span> 把"我是什么工具"写进数据，工厂把"什么工具用什么方式跑"写进逻辑——这是一种<strong>数据驱动的分发</strong>。想改变某类工具的跑法，不必动循环，只要改它的类型、或改 <span class="mono">_executor_map</span> 里的一行映射。</p>
</div>

<div class="card detail"><div class="tag">🔬 落到代码</div>
<p>想自己翻源码的话，这一课牵涉的文件不多，按"分发链路"排一排：</p>
<p>工厂与入口都在 <span class="mono">letta/services/tool_executor/tool_execution_manager.py</span>：<span class="mono">ToolExecutorFactory</span> 选执行器，<span class="mono">ToolExecutionManager</span> 是真入口。</p>
<p>执行器基类 <span class="mono">tool_executor_base.py::ToolExecutor</span>；五个实现：<span class="mono">core_tool_executor.py::LettaCoreToolExecutor</span>、<span class="mono">builtin_tool_executor.py::LettaBuiltinToolExecutor</span>、<span class="mono">files_tool_executor.py::LettaFileToolExecutor</span>、<span class="mono">mcp_tool_executor.py::ExternalMCPToolExecutor</span>、<span class="mono">sandbox_tool_executor.py::SandboxToolExecutor</span>。</p>
<p>类型定义在 <span class="mono">schemas/enums.py::ToolType</span>；MCP 配置在 <span class="mono">functions/mcp_client/types.py</span>，客户端与管理器在 <span class="mono">services/mcp/</span> 加 <span class="mono">services/mcp_manager.py::MCPManager</span>；<span class="mono">ToolExecutionResult</span> 在 <span class="mono">schemas/tool_execution_result.py</span>。</p>
</div>

<p>这一课其实在反复讲同一个道理：好的系统会把"变化"关进一个小盒子。工具千变万化，但变化都被收进了"类型标签"和"工厂映射"这两处；除此之外，循环、入口、结果对象统统保持不变。于是新增一种工具、换一种运行时，影响面都很小——这就是把复杂度按位置切开的价值。</p>

<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>这一课最容易踩的几个坑：</p>
<ul>
<li><strong>以为每种类型都有专属执行器</strong>——11 种类型只对应 5 个执行器类；<span class="mono">_executor_map</span> 显式登记 7 条，其余 4 种兜底沙箱。</li>
<li><strong>以为工厂就是入口</strong>——真正入口是 <span class="mono">ToolExecutionManager</span>，工厂只负责"选"。</li>
<li><strong>以为 MCP 客户端在 <span class="mono">functions/mcp_client/</span></strong>——那里只有配置类型，客户端在 <span class="mono">services/mcp/</span>。</li>
<li><strong>以为只有自定义工具走沙箱</strong>——<span class="mono">letta_voice_sleeptime_core</span> 和多 agent 工具也走沙箱。</li>
<li><strong>彩蛋</strong>：<span class="mono">ExternalComposioToolExecutor</span> 其实没被接线（<span class="mono">external_composio</span> 弃用、兜底沙箱），是一段死代码。</li>
</ul>
</div>

<p>还有一个常被忽略的好处：因为所有执行器都吐出同一种结果，错误处理也被统一了。工具抛异常也好、返回超长也好、规则违规也好，循环看到的永远是一个带状态的结果对象，而不是五花八门的异常。"出错"于是变成"正常流程的一个分支"，循环因此能稳稳地继续走下去。</p>

<h2>再挖深一点</h2>
<p>下面四个抽屉，留给想钻到底的人：标签从哪来、为什么默认沙箱是安全的、MCP 怎么集成、内置工具有哪些（外加一段"考古"）。</p>
<p>这些都是"知道了更踏实，第一次读却可以跳过"的细节。只想记主线，记住"类型 → 工厂 → 执行器 → 统一结果"就够；想抠实现，就逐个展开下面的抽屉。</p>
<details class="accordion"><summary>① 一个工具的 tool_type 是怎么定的？</summary><div class="acc-body">
<p>schema 层默认就是 <span class="mono">CUSTOM</span>。注册<strong>基础工具</strong>时按名字归类：<span class="mono">tool_manager.py::upsert_base_tools</span> 里，<span class="mono">name in BASE_TOOLS → LETTA_CORE</span>、<span class="mono">BASE_MEMORY_TOOLS → LETTA_MEMORY_CORE</span>、<span class="mono">BUILTIN_TOOLS → LETTA_BUILTIN</span>、<span class="mono">FILES_TOOLS → LETTA_FILES_CORE</span> 等。</p>
<p>MCP 工具则<strong>显式设</strong>：<span class="mono">create_mcp_tool_async</span> 直接给 <span class="mono">tool_type=EXTERNAL_MCP</span>。其余你自己写的，就留在默认 <span class="mono">CUSTOM</span>。</p>
<div class="note tip"><span class="ni">🔖</span><span class="nx">一个工具<strong>叫什么名字</strong>，往往就决定了它<strong>怎么被执行</strong>：注册阶段定下的 <span class="mono">tool_type</span> 会一路跟着它，直到执行时被工厂读到。</span></div>
</div></details>
<details class="accordion"><summary>② 为什么"自定义默认沙箱"是合理的安全默认？</summary><div class="acc-body">
<p>因为自定义工具是<strong>不可信代码</strong>——它可能来自任何人。把"没归类的一律丢沙箱"设成默认，意味着<strong>除非明确认定安全（进了 _executor_map），否则就隔离</strong>。这是"默认安全"（secure by default）的典型做法。</p>
<p>反过来想：要是默认进程内直跑，任何一个忘了归类的工具都会拿到服务端的执行权限。兜底沙箱，正好把这个风险堵死。</p>
<div class="note info"><span class="ni">🛡️</span><span class="nx">这也呼应第 18 课的态度：对待工具代码，<strong>默认不信任</strong>。第 18 课是"不运行就派生 schema"，这一课是"不确定就丢沙箱"——同一种安全直觉的两面。</span></div>
</div></details>
<details class="accordion"><summary>③ MCP 到底怎么集成？</summary><div class="acc-body">
<p>三种传输：<span class="mono">stdio</span>（本地子进程）、<span class="mono">sse</span>、<span class="mono">streamable_http</span>（远程 HTTP），定义在 <span class="mono">functions/mcp_client/types.py::MCPServerType</span>，配套 <span class="mono">StdioServerConfig</span> 等配置类。</p>
<p>执行特点：<strong>不走沙箱</strong>、每次<strong>开新连接</strong>（<span class="mono">connect → execute → cleanup</span>）。客户端实现在 <span class="mono">services/mcp/</span>，由工厂 <span class="mono">MCPManager::get_mcp_client</span> 按传输类型挑客户端。</p>
<div class="note warn"><span class="ni">📁</span><span class="nx">容易记混：<span class="mono">functions/mcp_client/types.py</span> 里只有<strong>配置与类型</strong>，真正建连接、发请求的<strong>客户端实现</strong>在 <span class="mono">services/mcp/</span>。别被目录名 <span class="mono">mcp_client</span> 骗了。</span></div>
</div></details>
<details class="accordion"><summary>④ 内置工具有哪些？外加一段"考古"</summary><div class="acc-body">
<p>内置工具在 <span class="mono">constants.py::BUILTIN_TOOLS</span>：<span class="mono">run_code</span>、<span class="mono">run_code_with_tools</span>、<span class="mono">web_search</span>、<span class="mono">fetch_webpage</span>，都由 <span class="mono">LettaBuiltinToolExecutor</span> 跑。</p>
<p>考古发现：<span class="mono">ExternalComposioToolExecutor</span> 这个类<strong>存在</strong>，却<strong>没出现在 _executor_map 里</strong>。<span class="mono">external_composio</span> 已弃用、会兜底走沙箱——所以那个执行器是一段<strong>永远不会被选中</strong>的死代码。</p>
<div class="note info"><span class="ni">🔍</span><span class="nx">考古的启示：<strong>一个类存在，不代表它被用上</strong>。判断代码活没活，要看它有没有被真正<strong>接线</strong>——这里就是看它在不在 <span class="mono">_executor_map</span> 里。</span></div>
</div></details>

<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li><span class="mono">ToolType</span> 共 11 种，像标签一样贴在每个 <span class="mono">Tool</span> 上。</li>
<li><span class="mono">ToolExecutorFactory</span> 按类型选执行器；<strong>未映射的一律兜底 <span class="mono">SandboxToolExecutor</span></strong>。</li>
<li><span class="mono">ToolExecutionManager::execute_tool_async</span> 才是真入口（计时、截断、包结果）。</li>
<li>运行时各异：<span class="mono">core</span> 进程内、<span class="mono">custom</span> 沙箱、<span class="mono">mcp</span> 连外部服务器。</li>
<li>所有执行器统一返回 <span class="mono">ToolExecutionResult</span>。</li>
</ul>
</div>

<div class="cellgroup"><div class="cg-cap"><b>第五部分串起来 · 工具的一生</b></div><div class="cells"><span class="cell">17 定义：函数+docstring→schema</span><span class="sep">·</span><span class="cell">18 派生：不跑就生成</span><span class="sep">·</span><span class="cell hl">19 分发：按类型执行</span><span class="sep">·</span><span class="cell">20 隔离：沙箱+信任边界</span></div></div>

<p>回头看第五部分这条线：<strong>定义 → 派生 → 分发 → 隔离执行</strong>。第 17 课把函数变成 schema，第 18 课不运行就把 schema 派生出来，第 19 课按类型把工具分发给执行器，第 20 课讲最危险的那一类——自定义代码——到底怎么被隔离着跑。</p>

<p>串起来看：模型选工具（第 17、18 课给了 schema）→ 循环调用（第 14 课）→ 工厂按 <span class="mono">ToolType</span> 分发 → 执行器各跑各的。而自定义工具默认被交给 <span class="mono">SandboxToolExecutor</span>，也就是丢进<strong>沙箱</strong>。可沙箱到底<strong>怎么跑、凭什么敢跑陌生人的代码</strong>？这就是第 20 课，也是第五部分的收尾。</p>
<div class="note tip"><span class="ni">🧷</span><span class="nx">小结一句：这一课把"执行工具"从一行黑箱，拆成了"类型 → 工厂 → 入口 → 执行器 → 结果"五个清清楚楚的环节。下一课，我们钻进其中最危险的那个环节——沙箱。</span></div>
""", "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">When Lesson 14 walked through the agent's execution loop, "running a tool" got barely a single line; Lessons 17 and 18 then grew tools a schema so the model could "see" and call them. But the moment the model actually emits a tool call and the system <strong>has to run it</strong> — that one step we never pried open.</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson lays "execution" out flat: when an agent really has to run a tool, how does it know <strong>which way</strong> to run it — call it in-process? throw it into an isolated sandbox? or open a network connection to an external server? The answer hides inside a label called <span class="mono">ToolType</span> and a factory.</p>
<div class="note info"><span class="ni">❓</span><span class="nx">Read on with one concrete question in mind: when the model says "call <span class="mono">run_code</span>", who exactly, <strong>where</strong>, and <strong>by what means</strong> actually runs that code? The answer is not some single function but a whole mechanism — "type label + factory + executor" — and this lesson takes it apart for you.</span></div>

<div class="card analogy"><div class="tag">🔌 Analogy</div>
<p>Think of "running a tool" as a hospital's <strong>triage desk</strong>. Everyone shows up to "see a doctor," yet the front desk treats no one itself — it routes you by your <strong>department label</strong> to different places.</p>
<p>A minor internal complaint goes straight into a consulting room and is seen on the spot (this is <span class="mono">core</span>, run in-process); anything that needs cutting is sent to an isolated <strong>operating room</strong> (this is <span class="mono">sandbox</span>, running unfamiliar code under isolation); a hard case this hospital can't handle is <strong>referred out for a second opinion</strong> (this is <span class="mono">MCP</span>, connecting to an external server).</p>
<p>The point is this: the triage desk <strong>treats no one</strong>; it does exactly one thing — <strong>route you by type to the right place</strong>. In Letta, that triage desk is the "factory" we are about to meet.</p>
</div>
<p>This analogy quietly holds the whole lesson: one phrase, "run a tool," lands as several completely different ways of running; what decides the route is the tool's <strong>type label</strong> and that "triaging" factory. Grasp those two and the "execution" step turns transparent.</p>

<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Every <span class="mono">Tool</span> carries a <span class="mono">ToolType</span> (11 in all), the equivalent of a "department label" stuck on the tool.</p>
<p><span class="mono">tool_execution_manager.py::ToolExecutorFactory</span> is that triage desk: it maps a tool to the matching <strong>executor</strong> by its <span class="mono">ToolType</span>. But the entry the agent loop actually calls is <span class="mono">ToolExecutionManager::execute_tool_async</span>, in the very same file.</p>
<p>The executors each mind their own patch: <span class="mono">core</span> runs in-process, <span class="mono">builtin</span> runs the built-in tools, <span class="mono">files</span> handles files, <span class="mono">mcp</span> connects to external servers, <span class="mono">sandbox</span> runs custom code.</p>
<p>So this lesson covers just three things: <strong>what ToolType is</strong>, <strong>how the factory picks an executor by it</strong>, and <strong>what each executor actually does</strong>.</p>
</div>

<div class="note tip"><span class="ni">🗺️</span><span class="nx">You can keep one through-line in view across this lesson: <strong>label (ToolType) → factory (pick the executor) → entry (ToolExecutionManager) → five executors (various runtimes) → one unified result (ToolExecutionResult)</strong>. The sections below follow that line one stop at a time.</span></div>
<h2>ToolType: a tool's "category label"</h2>
<p>Meet the labels first. <span class="mono">schemas/enums.py::ToolType</span> has 11 values in all, which fall into three groups — <strong>built-in</strong> (shipped by Letta, run in-process or under control), <strong>custom</strong> (the ones you write, sandboxed by default), and <strong>external</strong> (connecting to third parties).</p>
<div class="cellgroup"><div class="cg-cap"><b>Built-in · shipped by Letta (7)</b></div><div class="cells"><span class="cell hl">letta_core</span><span class="sep">·</span><span class="cell">letta_memory_core</span><span class="sep">·</span><span class="cell">letta_multi_agent_core</span><span class="sep">·</span><span class="cell">letta_sleeptime_core</span><span class="sep">·</span><span class="cell">letta_voice_sleeptime_core</span><span class="sep">·</span><span class="cell">letta_builtin</span><span class="sep">·</span><span class="cell">letta_files_core</span></div></div>
<div class="cellgroup"><div class="cg-cap"><b>Custom · the default (1)</b></div><div class="cells"><span class="cell hl">custom</span></div></div>
<div class="cellgroup"><div class="cg-cap"><b>External · third-party (3)</b></div><div class="cells"><span class="cell">external_langchain (deprecated)</span><span class="sep">·</span><span class="cell">external_composio (deprecated)</span><span class="sep">·</span><span class="cell hl">external_mcp</span></div></div>
<div class="note info"><span class="ni">🏷️</span><span class="nx"><span class="mono">custom</span> is the <strong>default</strong>: register a tool and, unless it gets sorted into another class, it stays <span class="mono">custom</span> — and <span class="mono">custom</span> falls through to the sandbox. The two <span class="mono">external_langchain / external_composio</span> are deprecated; the only genuinely live external type is <span class="mono">external_mcp</span>.</span></div>
<p>Why split into so many kinds? Because Letta's tools come from wildly different places: some are core framework abilities (send a message, edit memory), some are built-in platform utilities (run code, search the web), some are business functions you wrote on the spot, and some don't live locally at all and must be reached over the wire. Labelling each tool with a type is what lets the factory later dispatch it to the right runtime.</p>
<p>Those 7 built-in kinds break down further by purpose: <span class="mono">letta_core</span> handles conversation and control flow, <span class="mono">letta_memory_core</span> rewrites memory, <span class="mono">letta_sleeptime_core</span> and <span class="mono">letta_voice_sleeptime_core</span> serve the background tidying that happens during "sleep time," <span class="mono">letta_multi_agent_core</span> drives multi-agent collaboration, <span class="mono">letta_builtin</span> runs code and searches the web, and <span class="mono">letta_files_core</span> handles files.</p>
<h2>The factory: picking an executor by type</h2>
<p>The labels exist — but who reads them and hands out the work? <span class="mono">ToolExecutorFactory</span>. Inside it holds an <span class="mono">_executor_map</span> that maps each <span class="mono">ToolType</span> to an executor class; <span class="mono">get_executor</span> looks up the table, instantiates, and returns an executor.</p>
<div class="flow">
<div class="node"><div class="nt">tool.tool_type</div><div class="nd">the label on the tool</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">get_executor</div><div class="nd">look up _executor_map</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">the concrete executor</div><div class="nd">LettaCore / Sandbox …</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">execute(...)</div><div class="nd">actually run the tool</div></div>
<div class="arrow">→</div>
<div class="node"><div class="nt">ToolExecutionResult</div><div class="nd">one unified result</div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">The loop only says "call this tool"; <strong>how</strong> it runs is decided by <span class="mono">ToolType</span> + the factory: in-process / sandbox / connect to an MCP server — one and the same <span class="mono">execute</span> interface, hiding three runtimes.</span></div>
<p>Keep the <strong>end</strong> of the flow in mind too: whichever route it takes, every executor returns the same <span class="mono">ToolExecutionResult</span>. The differences are hidden in the middle while the exit stays uniform — that is exactly the shape of <strong>polymorphism</strong>.</p>
<p>In implementation, <span class="mono">_executor_map</span> is a <span class="mono">ClassVar</span> — a class-level dict shared by every instance. Looking it up is a plain <span class="mono">dict.get(key, default)</span>: a hit returns the mapped executor class, a miss returns the second argument, <span class="mono">SandboxToolExecutor</span>. One short line that is both a "dispatch table" and a "safety net."</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/tool_execution_manager.py</span><span class="ln">the factory (simplified)</span></div><pre><span class="kw">class</span> <span class="fn">ToolExecutorFactory</span>:
    _executor_map = {
        ToolType.LETTA_CORE: LettaCoreToolExecutor,
        ToolType.LETTA_MEMORY_CORE: LettaCoreToolExecutor,
        ToolType.LETTA_SLEEPTIME_CORE: LettaCoreToolExecutor,
        ToolType.LETTA_MULTI_AGENT_CORE: SandboxToolExecutor,
        ToolType.LETTA_BUILTIN: LettaBuiltinToolExecutor,
        ToolType.LETTA_FILES_CORE: LettaFileToolExecutor,
        ToolType.EXTERNAL_MCP: ExternalMCPToolExecutor,
    }
    <span class="kw">def</span> <span class="fn">get_executor</span>(cls, tool_type, ...):
        cls_ = cls._executor_map.<span class="fn">get</span>(tool_type, SandboxToolExecutor)   <span class="cm"># unmapped -> fall back to sandbox</span>
        <span class="kw">return</span> cls_(...)
</pre></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">Look at that <span class="mono">.get(tool_type, SandboxToolExecutor)</span> line inside <span class="mono">get_executor</span>: <strong>any type not in the table falls through to the sandbox</strong>. <span class="mono">custom</span>, <span class="mono">letta_voice_sleeptime_core</span>, and both deprecated externals (<span class="mono">external_langchain / external_composio</span>) land here that way — and <span class="mono">letta_multi_agent_core</span> runs in the sandbox too, just via an explicit entry. So "a custom tool = runs in the sandbox" is the <strong>default</strong>, not a special case.</span></div>
<p>This is the classic <strong>factory pattern</strong>: it gathers "<em>which implementation to actually use</em>" into one place, so the caller just asks for "an executor" without needing to know which class sits behind it or how it is built. Want to add a tool type later? Register one line in <span class="mono">_executor_map</span> — and not a single word of the loop or the entry has to change.</p>
<h2>The real entry: ToolExecutionManager</h2>
<p>The factory only "picks the person." The thing the agent loop actually calls is <span class="mono">ToolExecutionManager::execute_tool_async</span>: it uses the factory to get an executor, then <strong>times</strong> the call, <strong>truncates</strong> an over-long return, <strong>wraps</strong> exceptions into a result object, and hands it all back to the loop.</p>
<p>Why cram all this drudgery into the entry? Because a tool is the most "uncontrollable" link in an agent — it might read a database, run code, or hit the network, with wildly varying latency and failure modes. Collecting timing, truncation, and exception-wrapping into this one entry layer means the loop needn't fuss over each tool separately; the observability of per-step latency and the stability of "never blow up, never throw" stay centralized and under control.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/tool_execution_manager.py</span><span class="ln">the entry (simplified)</span></div><pre><span class="kw">async def</span> <span class="fn">execute_tool_async</span>(self, function_name, function_args, tool, ...):
    executor = ToolExecutorFactory.<span class="fn">get_executor</span>(tool.tool_type, ...)
    result = <span class="kw">await</span> executor.<span class="fn">execute</span>(function_name, function_args, tool, actor, ...)
    <span class="kw">if</span> len(return_str) > tool.return_char_limit:   <span class="cm"># truncate if too long</span>
        ...
    <span class="kw">return</span> result   <span class="cm"># ToolExecutionResult(status, func_return, stdout, stderr, ...)</span>
</pre></div>
<div class="note tip"><span class="ni">🧭</span><span class="nx">Tell the two layers apart: the factory only answers "<strong>which executor</strong>," while <span class="mono">ToolExecutionManager</span> is the <strong>entry</strong> the loop truly calls — it does the timing, the truncation past <span class="mono">return_char_limit</span>, and the uniform wrapping of exceptions into <span class="mono">ToolExecutionResult(status="error")</span>.</span></div>
<p>So what does that unified return value <span class="mono">ToolExecutionResult</span> look like? It carries <span class="mono">status</span> (success or failure), <span class="mono">func_return</span> (the tool's return value), <span class="mono">stdout / stderr</span> (whatever ran printed), plus fields like <span class="mono">sandbox_config_fingerprint</span>. Whether core ran it in-process or a sandbox ran it, the loop receives this same shell — which is exactly why the entry bothers to normalize everything into it.</p>
<h2>Five executors, each minding its patch</h2>
<p>Counting the ones named in the factory table plus the fallback, there are five executors in all. The table below lines up "label → executor → category → typical tools."</p>
<table class="t">
<tr><th>ToolType</th><th>Executor</th><th>Category</th><th>Typical tools</th></tr>
<tr><td class="mono">letta_core</td><td class="mono">LettaCoreToolExecutor</td><td>in-process</td><td class="mono">send_message · conversation_search</td></tr>
<tr><td class="mono">letta_memory_core</td><td class="mono">LettaCoreToolExecutor</td><td>in-process · memory</td><td class="mono">core_memory_append · core_memory_replace</td></tr>
<tr><td class="mono">letta_builtin</td><td class="mono">LettaBuiltinToolExecutor</td><td>controlled built-in</td><td class="mono">run_code · web_search · fetch_webpage</td></tr>
<tr><td class="mono">letta_files_core</td><td class="mono">LettaFileToolExecutor</td><td>files</td><td class="mono">open_files · grep_files</td></tr>
<tr><td class="mono">external_mcp</td><td class="mono">ExternalMCPToolExecutor</td><td>external server</td><td class="mono">MCP tools</td></tr>
<tr><td class="mono">custom (fallback)</td><td class="mono">SandboxToolExecutor</td><td>sandbox</td><td class="mono">your custom tools</td></tr>
</table>
<p>Let's spell out what each of these five executors does:</p>
<ul>
<li><span class="mono">LettaCoreToolExecutor</span>: it takes on all three patches — core, <strong>memory</strong>, and sleeptime — and runs every one of them <strong>in-process</strong>. The core-memory edits <span class="mono">core_memory_append / core_memory_replace</span> execute right here, no sandbox detour, lowest latency.</li>
<li><span class="mono">LettaBuiltinToolExecutor</span>: runs the platform's built-in tools — <span class="mono">run_code</span> executes code, <span class="mono">web_search</span> searches the web, <span class="mono">fetch_webpage</span> grabs a page — a set of "controlled" utilities.</li>
<li><span class="mono">LettaFileToolExecutor</span>: dedicated to file tools such as <span class="mono">open_files</span> and <span class="mono">grep_files</span>, serving "read a file into context" and "search within files."</li>
<li><span class="mono">ExternalMCPToolExecutor</span>: the only "reach-outward" executor; it forwards the call to an external MCP server and runs not one line of business code locally.</li>
<li><span class="mono">SandboxToolExecutor</span>: the <strong>fallback</strong> for custom tools and every unmapped type, throwing unfamiliar code into an isolated sandbox to run — how it runs and why it dares to is the subject of Lesson 20.</li>
</ul>
<p>Walk the dispatch with three examples. The model wants <span class="mono">core_memory_append</span> (type <span class="mono">letta_memory_core</span>): the factory hands it to <span class="mono">LettaCoreToolExecutor</span>, editing memory on the spot in-process. It wants <span class="mono">run_code</span> (<span class="mono">letta_builtin</span>): handed to <span class="mono">LettaBuiltinToolExecutor</span> for controlled execution. It wants your own <span class="mono">calculate_invoice</span> (unsorted, landing in <span class="mono">custom</span>): the factory can't find it in the table and falls back to <span class="mono">SandboxToolExecutor</span>, into the sandbox. One identical call, three completely different fates.</p>
<p>They all inherit the base class <span class="mono">tool_executor_base.py::ToolExecutor</span>, with the uniform signature <span class="mono">async def execute(...) -&gt; ToolExecutionResult</span>. Note that the memory tool <span class="mono">core_memory_append</span> also belongs to <span class="mono">LettaCoreToolExecutor</span> and runs <strong>in-process</strong>, never in a sandbox.</p>
<div class="note info"><span class="ni">🧩</span><span class="nx">The beauty of a uniform interface: the loop recognizes only one signature, <span class="mono">execute(...) -&gt; ToolExecutionResult</span>. Whether underneath it edits memory, runs code, or connects to an external server, it all "looks the same" to the loop — so it can call, time, record, and feed the result back into the conversation for any tool, all alike.</span></div>
<p>In-process versus into-the-sandbox is, at heart, a "trust versus speed" trade-off. Trusted core tools (edit memory, send a message) run straight in the process — fastest and simplest; custom code of unknown origin must be isolated first, accepting slower and clunkier over letting it touch the server's memory and permissions. Letting the "type" express that trade-off is the cleverest part of this design.</p>

<div class="cute">
<div class="row"><span class="emoji">🏭</span><span class="lab">sort by ToolType</span><span class="arrow">→</span><span class="emoji">🧠</span><span class="bubble">core · in-process</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">the same factory</span><span class="arrow">→</span><span class="emoji">🔧</span><span class="bubble">builtin · built-in</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">different belts</span><span class="arrow">→</span><span class="emoji">📁</span><span class="bubble">files · files</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">each its own way</span><span class="arrow">→</span><span class="emoji">🔌</span><span class="bubble">mcp · external</span></div>
<div class="row"><span class="emoji">🏭</span><span class="lab">the fallback lane</span><span class="arrow">→</span><span class="emoji">📦</span><span class="bubble">sandbox · sandbox</span></div>
<div class="cap">The factory puts each tool on the right belt by ToolType: in-process, built-in, files, external, sandbox.</div>
</div>

<p>So "dispatch" can be closed in one sentence: <strong>a tool arrives wearing its type label, the factory sends it to the matching executor by that label, each executor runs its own runtime, and they all emit the same kind of result</strong>. Next we look at the most special belt of all — the one to the outside world, MCP.</p>
<h2>MCP: connecting to an external tool server</h2>
<p>The previous four categories all run inside Letta's own house. <strong>MCP</strong> (Model Context Protocol) is different: the tool actually lives on an <strong>external server</strong>, and Letta is merely a client that <strong>forwards</strong> the call and fetches the result back.</p>
<p>Such a tool's <span class="mono">tool_type</span> is <span class="mono">external_mcp</span>, and it is also tagged <span class="mono">mcp:&lt;server&gt;</span> (set by <span class="mono">ToolCreate.from_mcp</span>). At execution time <span class="mono">ExternalMCPToolExecutor</span> pulls the target server name out of the tag and hands it to <span class="mono">MCPManager</span> to connect, run, and then disconnect.</p>
<div class="note tip"><span class="ni">🌐</span><span class="nx">MCP is an <strong>open protocol</strong>: anyone can write an MCP server exposing a batch of tools (query a database, send email, call an internal API…). On Letta's side you only register the server and import the tools, and the agent can call them — while the tool's implementation details stay entirely opaque to Letta.</span></div>
<div class="vflow">
<div class="step"><div class="num">1</div><div class="sc"><h4>MCP tool</h4><p>tagged <span class="mono">mcp:&lt;server&gt;</span>, type <span class="mono">external_mcp</span></p></div></div>
<div class="step"><div class="num">2</div><div class="sc"><h4>ExternalMCPToolExecutor</h4><p>parses the target server name from the tag</p></div></div>
<div class="step"><div class="num">3</div><div class="sc"><h4>MCPManager.execute_mcp_server_tool</h4><p>the single entry, owning the whole connection lifecycle</p></div></div>
<div class="step"><div class="num">4</div><div class="sc"><h4>connect → execute → cleanup</h4><p>a fresh connection each time, dropped when done, never reused</p></div></div>
</div>
<p>Read that vertical flow as one chain: the tool comes in wearing its <span class="mono">mcp:&lt;server&gt;</span> tag, the executor parses the server name out of the tag, and <span class="mono">MCPManager</span> connects, sends the call across, takes the result back, and disconnects. Throughout, Letta executes no tool logic of its own — it only "relays."</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_executor/mcp_tool_executor.py</span><span class="ln">MCP execution (simplified)</span></div><pre><span class="kw">async def</span> <span class="fn">execute</span>(self, function_name, function_args, tool, ...):
    server = <span class="fn">_tag_to_server</span>(tool.tags)        <span class="cm"># pull the server name from the "mcp:&lt;server&gt;" tag</span>
    resp, ok = <span class="kw">await</span> MCPManager().<span class="fn">execute_mcp_server_tool</span>(
        server, tool_name=function_name, tool_args=function_args, ...)   <span class="cm"># connect to the external server</span>
    <span class="kw">return</span> ToolExecutionResult(status=<span class="st">"success"</span> <span class="kw">if</span> ok <span class="kw">else</span> <span class="st">"error"</span>, func_return=resp)
</pre></div>
<div class="cellgroup"><div class="cg-cap"><b>Three MCP transports · MCPServerType</b></div><div class="cells"><span class="cell hl">stdio</span><span class="sep">·</span><span class="cell">sse</span><span class="sep">·</span><span class="cell">streamable_http</span></div></div>
<p>Seen another way, MCP fully decouples "the tool" from "the process that runs the tool": implementation, dependencies, and secrets all stay on the tool's own server, and Letta only initiates the call through the protocol. A third party can therefore package a whole set of abilities into one MCP server and plug it into any agent.</p>
<p>The cost is that every call must <strong>connect and disconnect on the spot</strong> — <span class="mono">connect → execute → cleanup</span> end to end. The upside is stateless, clean, and mutually non-interfering; the downside is connection overhead, so MCP suits "external abilities used now and then" rather than a high-frequency hot path.</p>
<div class="note info"><span class="ni">🔌</span><span class="nx">Two counterintuitive points: MCP execution <strong>does not go through the sandbox</strong> (it connects to an external server, it isn't running code locally); and every call <strong>opens a fresh connection</strong> (<span class="mono">connect → execute → cleanup</span>). The real transport clients live in <span class="mono">letta/services/mcp/</span>, <strong>not</strong> <span class="mono">functions/mcp_client/</span> — the latter only holds config types and exceptions.</span></div>
<p>Remember MCP in a sentence: <strong>the tool is at someone else's place; Letta calls on it</strong>. It extends the agent's reach while leaving the risk of "running third-party code" on the third party's side — a different security philosophy from the local sandbox.</p>
<p>Put another way: the previous four executors are like "working in different rooms of your own house," whereas MCP is like "phoning for takeout" — the work happens at someone else's place, and you only place the order and receive the delivery. This also explains why MCP skips the sandbox: the sandbox exists to isolate "unfamiliar code running in your house," but MCP's code never runs in your house at all.</p>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p><strong>"One call, several runtimes behind it."</strong> From the vantage of Lesson 14's loop, "call a tool" is forever one uniform line of code.</p>
<p>Yet underneath they differ wildly: edit core memory in-process (<span class="mono">LettaCore</span>), shell out to run unfamiliar code in a sandbox venv (<span class="mono">Sandbox</span>), open a network connection to an MCP server (<span class="mono">ExternalMCP</span>). <span class="mono">ToolType</span> + the factory is the <strong>polymorphism</strong> that hides those differences.</p>
<p>And another counterintuitive truth: there are only <strong>5 executor classes</strong> for <strong>11 ToolTypes</strong>. <span class="mono">_executor_map</span> wires 7 types explicitly (several share <span class="mono">LettaCore</span>), and the remaining 4 — <span class="mono">custom</span>, voice-sleeptime, and the two deprecated externals — <strong>fall back to <span class="mono">SandboxToolExecutor</span></strong>. So "custom = sandbox" is the default, not a special case.</p>
<p>Every executor, finally, returns the same <span class="mono">ToolExecutionResult</span> — the very type used for a tool-rule violation back in Lesson 16. Uniform exit, differences kept inward.</p>
<p>It is clearer set against the whole tool chain: Lessons 17 and 18 gave a tool "a schema, the ability to be seen," and this lesson gets a tool "correctly run." The model's end is always a uniform function call, yet the system's end quietly makes one <strong>runtime choice by type</strong> — that is exactly what a good abstraction looks like: simple on top, flexible underneath.</p>
<p>Put differently, <span class="mono">ToolType</span> writes "what tool I am" into data, and the factory writes "which tool runs which way" into logic — a kind of <strong>data-driven dispatch</strong>. To change how some class of tool runs, you needn't touch the loop; you only change its type, or one line of mapping in <span class="mono">_executor_map</span>.</p>
</div>

<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p>If you want to read the source yourself, this lesson touches few files; line them up along the "dispatch chain":</p>
<p>The factory and the entry both live in <span class="mono">letta/services/tool_executor/tool_execution_manager.py</span>: <span class="mono">ToolExecutorFactory</span> picks the executor, <span class="mono">ToolExecutionManager</span> is the real entry.</p>
<p>The executor base class is <span class="mono">tool_executor_base.py::ToolExecutor</span>; the five implementations: <span class="mono">core_tool_executor.py::LettaCoreToolExecutor</span>, <span class="mono">builtin_tool_executor.py::LettaBuiltinToolExecutor</span>, <span class="mono">files_tool_executor.py::LettaFileToolExecutor</span>, <span class="mono">mcp_tool_executor.py::ExternalMCPToolExecutor</span>, <span class="mono">sandbox_tool_executor.py::SandboxToolExecutor</span>.</p>
<p>The type is defined in <span class="mono">schemas/enums.py::ToolType</span>; MCP config in <span class="mono">functions/mcp_client/types.py</span>, with clients and manager in <span class="mono">services/mcp/</span> plus <span class="mono">services/mcp_manager.py::MCPManager</span>; <span class="mono">ToolExecutionResult</span> in <span class="mono">schemas/tool_execution_result.py</span>.</p>
</div>
<p>This lesson really keeps making the same point: a good system locks "change" inside a small box. Tools vary endlessly, but the variation is gathered into just two places — the "type label" and the "factory mapping"; beyond those, the loop, the entry, and the result object all stay unchanged. So adding a tool kind or swapping a runtime has a tiny blast radius — that is the value of cutting complexity by location.</p>

<div class="card warn"><div class="tag">⚠️ Common misconceptions</div>
<p>The traps easiest to fall into here:</p>
<ul>
<li><strong>Thinking every type has its own dedicated executor</strong> — there are only 5 executor classes for 11 types; <span class="mono">_executor_map</span> wires 7 explicitly and the rest fall back to the sandbox.</li>
<li><strong>Thinking the factory is the entry</strong> — the real entry is <span class="mono">ToolExecutionManager</span>; the factory only "picks."</li>
<li><strong>Thinking the MCP client is in <span class="mono">functions/mcp_client/</span></strong> — that holds only config types; the clients are in <span class="mono">services/mcp/</span>.</li>
<li><strong>Thinking only custom tools go to the sandbox</strong> — <span class="mono">letta_voice_sleeptime_core</span> and the multi-agent tools go there too.</li>
<li><strong>Easter egg</strong>: <span class="mono">ExternalComposioToolExecutor</span> is in fact never wired up (<span class="mono">external_composio</span> is deprecated and falls back to the sandbox) — it is dead code.</li>
</ul>
</div>

<p>One more often-overlooked benefit: because every executor emits the same kind of result, error handling gets unified too. Whether a tool throws, returns something over-long, or violates a rule, what the loop sees is always one status-bearing result object, not a motley of exceptions. "Going wrong" thus becomes "a branch of the normal flow," and the loop can keep marching steadily on.</p>
<h2>Digging a little deeper</h2>
<p>The four drawers below are for those who want to dig to the bottom: where the label comes from, why the default sandbox is safe, how MCP integrates, and which built-in tools exist (plus a bit of "archaeology").</p>
<p>These are details that "make you steadier once known but can be skipped on a first read." If you only want the through-line, remembering "type → factory → executor → unified result" is enough; to pry into the implementation, open the drawers below one by one.</p>
<details class="accordion"><summary>① How is a tool's tool_type decided?</summary><div class="acc-body">
<p>At the schema layer the default is just <span class="mono">CUSTOM</span>. When <strong>base tools</strong> are registered they're sorted by name: in <span class="mono">tool_manager.py::upsert_base_tools</span>, <span class="mono">name in BASE_TOOLS → LETTA_CORE</span>, <span class="mono">BASE_MEMORY_TOOLS → LETTA_MEMORY_CORE</span>, <span class="mono">BUILTIN_TOOLS → LETTA_BUILTIN</span>, <span class="mono">FILES_TOOLS → LETTA_FILES_CORE</span>, and so on.</p>
<p>MCP tools are set <strong>explicitly</strong>: <span class="mono">create_mcp_tool_async</span> assigns <span class="mono">tool_type=EXTERNAL_MCP</span> directly. Everything else you write yourself stays at the default <span class="mono">CUSTOM</span>.</p>
<div class="note tip"><span class="ni">🔖</span><span class="nx">What a tool is <strong>named</strong> often decides <strong>how it gets executed</strong>: the <span class="mono">tool_type</span> fixed at registration follows it all the way until the factory reads it at execution time.</span></div>
</div></details>
<details class="accordion"><summary>② Why is "custom defaults to sandbox" a sound security default?</summary><div class="acc-body">
<p>Because custom tools are <strong>untrusted code</strong> — they could come from anyone. Making "anything unsorted goes to the sandbox" the default means <strong>isolate unless explicitly judged safe (it made it into _executor_map)</strong>. This is the textbook "secure by default" approach.</p>
<p>Flip it around: if the default were in-process, any tool someone forgot to sort would get server-side execution rights. The fallback sandbox seals exactly that risk.</p>
<div class="note info"><span class="ni">🛡️</span><span class="nx">This echoes Lesson 18's stance: treat tool code as <strong>untrusted by default</strong>. Lesson 18 was "derive a schema without running it," and this lesson is "throw it to the sandbox when unsure" — two faces of the same security instinct.</span></div>
</div></details>
<details class="accordion"><summary>③ How does MCP actually integrate?</summary><div class="acc-body">
<p>Three transports: <span class="mono">stdio</span> (a local subprocess), <span class="mono">sse</span>, and <span class="mono">streamable_http</span> (remote HTTP), defined in <span class="mono">functions/mcp_client/types.py::MCPServerType</span>, with config classes like <span class="mono">StdioServerConfig</span>.</p>
<p>Execution traits: <strong>no sandbox</strong>, a <strong>fresh connection every time</strong> (<span class="mono">connect → execute → cleanup</span>). The client implementations live in <span class="mono">services/mcp/</span>, where the factory <span class="mono">MCPManager::get_mcp_client</span> picks the client by transport type.</p>
<div class="note warn"><span class="ni">📁</span><span class="nx">Easy to muddle: <span class="mono">functions/mcp_client/types.py</span> holds only <strong>config and types</strong>; the real <strong>client implementations</strong> that build connections and send requests are in <span class="mono">services/mcp/</span>. Don't be fooled by the directory name <span class="mono">mcp_client</span>.</span></div>
</div></details>
<details class="accordion"><summary>④ Which built-in tools exist? Plus a bit of "archaeology"</summary><div class="acc-body">
<p>The built-in tools are in <span class="mono">constants.py::BUILTIN_TOOLS</span>: <span class="mono">run_code</span>, <span class="mono">run_code_with_tools</span>, <span class="mono">web_search</span>, <span class="mono">fetch_webpage</span> — all run by <span class="mono">LettaBuiltinToolExecutor</span>.</p>
<p>An archaeological find: the class <span class="mono">ExternalComposioToolExecutor</span> <strong>exists</strong> yet <strong>never appears in _executor_map</strong>. <span class="mono">external_composio</span> is deprecated and falls back to the sandbox — so that executor is dead code that <strong>can never be selected</strong>.</p>
<div class="note info"><span class="ni">🔍</span><span class="nx">The lesson of the dig: <strong>a class existing doesn't mean it's used</strong>. To judge whether code is alive, see whether it is actually <strong>wired up</strong> — here, whether it appears in <span class="mono">_executor_map</span>.</span></div>
</div></details>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li><span class="mono">ToolType</span> has 11 values, stuck like a label on every <span class="mono">Tool</span>.</li>
<li><span class="mono">ToolExecutorFactory</span> picks an executor by type; <strong>anything unmapped falls back to <span class="mono">SandboxToolExecutor</span></strong>.</li>
<li><span class="mono">ToolExecutionManager::execute_tool_async</span> is the real entry (timing, truncation, result-wrapping).</li>
<li>Runtimes differ: <span class="mono">core</span> in-process, <span class="mono">custom</span> sandbox, <span class="mono">mcp</span> connects to an external server.</li>
<li>Every executor returns the same <span class="mono">ToolExecutionResult</span>.</li>
</ul>
</div>

<div class="cellgroup"><div class="cg-cap"><b>Part 5 strung together · the life of a tool</b></div><div class="cells"><span class="cell">17 define: function+docstring→schema</span><span class="sep">·</span><span class="cell">18 derive: generate without running</span><span class="sep">·</span><span class="cell hl">19 dispatch: execute by type</span><span class="sep">·</span><span class="cell">20 isolate: sandbox+trust boundary</span></div></div>

<p>Look back at Part 5's line: define → derive → dispatch → isolated execution. Lesson 17 turns a function into a schema, Lesson 18 derives the schema without running it, Lesson 19 dispatches a tool to an executor by type, and Lesson 20 covers the most dangerous kind — custom code — and how it actually runs under isolation.</p>

<p>Strung together: the model picks a tool (Lessons 17 and 18 gave it a schema) → the loop calls it (Lesson 14) → the factory dispatches by <span class="mono">ToolType</span> → each executor runs its own way. And a custom tool is handed by default to <span class="mono">SandboxToolExecutor</span>, that is, thrown into the sandbox. But how exactly does the sandbox run, and on what grounds does it dare run a stranger's code? That is Lesson 20, the close of Part 5.</p>
<div class="note tip"><span class="ni">🧷</span><span class="nx">In one line: this lesson took "running a tool" from a single black-box line and broke it into five crisp links — "type → factory → entry → executor → result." Next lesson we burrow into the most dangerous link of all — the sandbox.</span></div>
"""}

LESSON_20 = {"zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">第 19 课结尾留了个悬念：一个自定义工具——用户自己写的 Python 源码——默认会被交给 <span class="mono">SandboxToolExecutor</span>，也就是"扔进沙箱"。可沙箱凭什么敢跑一段陌生人的代码？跑完之后，又该怎么把结果安全地收回服务端？</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">这是第五部分的收尾，也是整套工具系统"安全观"的落点。我们要把一张<strong>信任边界图</strong>画清楚：哪段路可以"放心传"、哪段路"必须验真"，以及一次真实的安全修复（PR #3343）如何把这条边界焊死。</p>

<div class="card analogy"><div class="tag">🔌 生活类比</div>
<p>把沙箱想成监狱的探视窗。你（服务端）要递东西<strong>进去</strong>——那是你自己的物品，可以直接递原物。因为风险方向是"往里走"：东西进了高墙，再危险也跑不到你这边。</p>
<p>可对方（沙箱里跑的陌生代码）从里面递<strong>出来</strong>的任何包裹，你绝不能伸手直接接管。必须隔着玻璃、过安检、核对封条——因为你根本不知道里面是糖果还是刀片。</p>
<p>这一课全部的安全感，就压在这条朴素规矩上：<strong>往里递可以是原物，往外收必须过安检</strong>。剩下的工程，只是把"原物"翻译成 <span class="mono">pickle</span>、把"安检"翻译成 <span class="mono">JSON</span> 加一层校验而已。</p>
<p>这条规矩看着简单，却常被违反：很多"沙箱"只盯着把代码关进去，却忘了"收结果"这一步同样跨越边界。真正的安全，恰恰藏在你<strong>怎么把东西拿出来</strong>。</p>
</div>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>记住一句话就够了：<strong>自定义工具是不可信代码</strong>。它不在主进程里跑，而是被丢进一个沙箱——本地 venv、E2B 或 Modal，由 <span class="mono">SandboxType</span> 三选一。</p>
<p>沙箱内外只有两条数据通道，方向相反、信任也相反。<strong>server→sandbox</strong> 走 <span class="mono">pickle</span>（受信：服务端把自己造的 <span class="mono">agent_state</span> 序列化进去）；<strong>sandbox→server</strong> 走 <span class="mono">JSON</span>（不可信：<strong>绝不 <span class="mono">pickle.loads</span></strong>），并加 <span class="mono">marker+长度+MD5</span> 帧来校验完整性。</p>
<p>这张<strong>信任边界图</strong>就是本课的全部。而 PR #3343 正是一次把回程通道从 pickle 改成 JSON 的真实安全修复——它把这条边界从"差不多安全"变成"焊死"。</p>
<p>再强调一遍方向感：数据从服务端流向沙箱时，权限是在<strong>收窄</strong>（进了低信任区），所以 pickle 安全；数据从沙箱流回服务端时，权限在<strong>放大</strong>（回到高信任区），所以必须只用 JSON。把"权限放大的方向"当成红线，整张图就记住了。</p>
</div>
<h2>沙箱三选一：代码到底在哪跑</h2>
<p>一个自定义工具被执行前，Letta 先决定"在哪跑"。这不是随机的，而是一条短路式的判定链：先看工具自己的偏好，再看全局配置，最后兜底到本地。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>看 tool.metadata</h4><p>若工具显式标了 <span class="mono">sandbox=="modal"</span> 且 Modal 已启用 → 用 <strong>Modal</strong>（云端容器，强隔离）。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>看全局配置</h4><p>否则查 <span class="mono">ToolSettings.sandbox_type</span>：若配了 <span class="mono">e2b_api_key</span> → 用 <strong>E2B</strong>（云端微沙箱）。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>兜底本地</h4><p>都没有 → <strong>Local</strong>：在本机建一个隔离 venv，用子进程跑。开发期最常见。</p></div></div>
</div>
<p>三种沙箱不是冗余，而是<strong>隔离强度与部署成本的权衡</strong>。本地 venv 零依赖、最快，但和服务端共享内核，隔离最弱；E2B、Modal 把代码送进云端独立容器，隔离强，但要联网和配额。所以同一段工具，开发期可能跑在本地，生产期被切到 Modal——这正是"在哪跑"必须可配置的原因。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">类型定义在 <span class="mono">schemas/enums.py::SandboxType</span>（<span class="mono">E2B / MODAL / LOCAL</span>）；选择逻辑落在 <span class="mono">sandbox_tool_executor.py</span>，全局开关是 <span class="mono">settings.py::ToolSettings.sandbox_type</span>。关键点是：无论选哪个，下面这套"生成脚本 + 信任边界 + 帧校验"的玩法<strong>三种沙箱完全一致</strong>，差别只在外层容器。</span></div>
<p>顺便提一句配置：<span class="mono">LocalSandboxConfig</span> 还能调 <span class="mono">sandbox_dir</span>、<span class="mono">use_venv</span>、<span class="mono">venv_name</span>、<span class="mono">pip_requirements</span> 等，决定本地沙箱具体怎么落地。但这些都是"怎么跑"的旋钮，不改"信谁"的边界。</p>
<h2>生成的沙箱脚本：把工具包起来跑</h2>
<p>沙箱不会"直接调用"用户函数。服务端会<strong>现拼一段 Python 脚本</strong>，把所有需要的东西内联进去，再让沙箱整段执行。这段脚本由 <span class="mono">tool_sandbox/base.py::_render_sandbox_code</span> 拼出来。</p>
<p>这种"现拼脚本"的做法有个好处：服务端对沙箱里要发生的一切<strong>完全掌控</strong>——传什么、调用什么、怎么打包结果，全写死在脚本里，沙箱只是个老老实实的执行器。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>解出 agent_state</h4><p><span class="mono">pickle.loads(...)</span> 还原服务端传进来的 <span class="mono">agent_state</span>（受信方向）。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>内联参数</h4><p>每个调用参数按 <span class="mono">repr()</span> 写成字面量，<strong>不是 pickle</strong>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>内联用户源码</h4><p>把工具的 <span class="mono">source_code</span> 逐字粘进来，定义出函数本体。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>调用 + 打包</h4><p><span class="mono">_function_result = tool(...)</span>，再把结果 + <span class="mono">agent_state</span> 打成 JSON。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>加帧写 stdout</h4><p>前面缀上 <span class="mono">marker+长度+MD5</span>，写进标准输出，等服务端来读。</p></div></div>
</div>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_sandbox/base.py</span><span class="ln">_render_sandbox_code（简化骨架）</span></div>
<pre><span class="cm"># 服务端把 agent_state pickle 进脚本，沙箱里 loads（受信方向）</span>
agent_state = pickle.<span class="fn">loads</span>(<span class="nb">b"..."</span>)
x = <span class="st">"&lt;内联字面量&gt;"</span>            <span class="cm"># 参数按 repr() 内联，不是 pickle</span>
<span class="cm"># &lt;用户工具源码逐字内联&gt;</span>
_function_result = <span class="fn">my_tool</span>(x, agent_state=agent_state)
payload = _letta_json.<span class="fn">dumps</span>({<span class="st">"results"</span>: _function_result,
    <span class="st">"agent_state"</span>: agent_state.<span class="fn">model_dump</span>(mode=<span class="st">"json"</span>)}).<span class="fn">encode</span>()  <span class="cm"># JSON，不是 pickle</span>
sys.stdout.buffer.<span class="fn">write</span>(MARKER + struct.<span class="fn">pack</span>(<span class="st">"&gt;I"</span>, len(payload)) + md5_hex + payload)
</pre></div>
<div class="note info"><span class="ni">💡</span><span class="nx">为什么把<strong>源码逐字内联</strong>、而不是 import 用户模块？因为沙箱里根本没有那个模块——工具源码只存在数据库里。内联后脚本自包含，沙箱只要一个干净解释器就能跑。脚本里还会用 <span class="mono">coerce_dict_args_by_annotations(...)</span> 按注解把参数强转成正确类型，避免字符串和数字错配。</span></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><span class="mono">agent_state</span> 走 <span class="mono">pickle.dumps</span>（服务端造、沙箱 <span class="mono">loads</span>）；但<strong>调用参数是内联字面量（<span class="mono">repr()</span>），不是 pickle</strong>。整段脚本里，只有 <span class="mono">agent_state</span> 这一项用到了 pickle——这个区分后面会反复用到。</span></div>

<h2>信任边界：方向决定序列化</h2>
<p>现在把两条通道并排放。<strong>同一份脚本，两个方向用了两种序列化</strong>——这不是随意，而是信任在说话。</p>
<div class="cols">
  <div class="col"><h4>⬇️ server → sandbox</h4><p>用 <span class="mono">pickle</span> 传 <span class="mono">agent_state</span>。<strong>受信</strong>：是服务端 pickle 自己造的对象，沙箱只负责 loads。权限往低信任侧流，没有"反序列化不可信输入"的问题。</p></div>
  <div class="col"><h4>⬆️ sandbox → server</h4><p>只用 <span class="mono">JSON</span> + <span class="mono">marker+长度+MD5</span>。<strong>不可信</strong>：沙箱刚跑完任意用户代码，它的 stdout 绝不能 <span class="mono">pickle.loads</span>，只能当数据读。</p></div>
</div>
<p>为什么向下可以 pickle？因为被反序列化的对象是<strong>服务端自己造的</strong>，沙箱拿到的是数据、不是攻击面；就算沙箱想搞鬼，它也改不了"已经 pickle 进去的字节"。</p>
<p>为什么向上必须 JSON？因为 <span class="mono">pickle.loads</span> 会在反序列化时<strong>执行任意代码</strong>。沙箱里跑的是陌生人的工具，它的输出天然可疑——用 <span class="mono">json.loads</span> 读，最坏也只是拿到一坨假数据，而不是被 RCE。</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">一个反直觉点：受信方向用 pickle 不是"将就"，而是<strong>主动选择</strong>——它能一次性还原 <span class="mono">agent_state</span> 这种复杂对象，省去手写序列化。pickle 本身不是坏人，把它用在不可信方向才是。</span></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">举个具体攻击：恶意工具在 <span class="mono">return</span> 时不返回普通 dict，而是返回一个带 <span class="mono">__reduce__</span> 的对象。若服务端用 <span class="mono">pickle.loads</span> 读它，反序列化的瞬间就执行攻击者指定的命令——服务端沦陷。改成 <span class="mono">json.loads</span> 后，这种对象根本无法表达，攻击面被结构性消除。</span></div>
<div class="cute"><div class="row"><span class="emoji">🔐</span><span class="lab">⬇️ pickle</span><span class="arrow">→</span><span class="emoji">📦</span><span class="bubble">自己人，放行</span></div>
<div class="row"><span class="emoji">🔐</span><span class="lab">⬆️ JSON</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="bubble">外人，过安检 MD5</span></div>
<div class="cap">信任＝方向：能 pickle.loads 你自己造的数据；绝不 pickle.loads 跨过不可信边界回来的数据。</div></div>

<h2>回程帧：marker + 长度 + MD5</h2>
<p>沙箱的 stdout 是一条嘈杂的河：用户代码可能 print 调试信息、可能抛异常栈、甚至可能故意打一个<strong>假结果</strong>。所以真正的结果不是"整段 stdout"，而是被一段帧<strong>圈起来</strong>的那一小块。</p>
<table class="t">
  <tr><th>字段</th><th>大小</th><th>作用</th></tr>
  <tr><td class="mono">MARKER</td><td class="mono">16 字节</td><td>uuid5 生成的定位锚，在噪声里标出"真结果从这里开始"</td></tr>
  <tr><td class="mono">LENGTH</td><td class="mono">4 字节 '&gt;I'</td><td>big-endian 无符号整数，告诉你 payload 有多长，好精确切片</td></tr>
  <tr><td class="mono">MD5</td><td class="mono">32 字节 hex</td><td>payload 的校验和，抓篡改与截断</td></tr>
  <tr><td class="mono">JSON_PAYLOAD</td><td class="mono">LENGTH 字节</td><td>真正的结果：工具返回值 + agent_state 的 JSON</td></tr>
</table>
<div class="cellgroup"><div class="cg-cap"><b>stdout 帧布局</b></div><div class="cells"><span class="cell hl">MARKER(16)</span><span class="sep">·</span><span class="cell">LENGTH(4)</span><span class="sep">·</span><span class="cell">MD5(32)</span><span class="sep">·</span><span class="cell">JSON_PAYLOAD</span></div></div>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_sandbox/local_sandbox.py</span><span class="ln">parse_out_function_results_markers（简化）</span></div>
<pre>pos = data.<span class="fn">find</span>(MARKER)                       <span class="cm"># 在嘈杂 stdout 里定位真结果</span>
length = struct.<span class="fn">unpack</span>(<span class="st">"&gt;I"</span>, data[p:p+<span class="nb">4</span>])[<span class="nb">0</span>]
payload = data[start : start+length]
<span class="kw">if</span> hashlib.<span class="fn">md5</span>(payload).<span class="fn">hexdigest</span>() != checksum:
    <span class="kw">raise</span> <span class="fn">Exception</span>(<span class="st">"Function ran, but output is corrupted."</span>)
result = json.<span class="fn">loads</span>(payload)                     <span class="cm"># JSON，绝不 pickle.loads</span>
agent_state = AgentState.<span class="fn">model_validate</span>(result[<span class="st">"agent_state"</span>])  <span class="cm"># pydantic 重水合</span>
</pre></div>
<p>你可能会问：为什么用 stdout 这种"脏"通道，而不开一条干净的返回管道？因为沙箱的边界本质是一个<strong>进程</strong>，进程之间最通用、最不挑运行时的桥就是标准输出。代价是 stdout 里混着一切，于是必须靠帧把"真结果"从噪声里捞出来。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">这套帧防的是什么？用户工具能往 stdout 打<strong>任何东西</strong>，包括一个伪造的结果或假 marker。marker 圈出真 payload，长度做精确切片，MD5 抓篡改/截断——三层叠起来，服务端才敢说"我读到的就是工具真正返回的那一份"。</span></div>
<p>顺序也有讲究：<strong>先比 MD5、再 <span class="mono">json.loads</span></strong>。若先解析、出错了再说，攻击者就有机会用畸形 JSON 去触发解析器的边角行为；先校验完整性，等于把"可疑输入"挡在解析之前。</p>
<h2>PR #3343：把 pickle 换成 JSON</h2>
<p>帧校验一直都在，但有一处老漏洞：早期回程 payload 是 <strong>pickle</strong> 编码的，服务端读回来时会 <span class="mono">pickle.loads</span>。这等于对"刚跑完任意用户代码的沙箱输出"做反序列化——一个干净利落的<strong>服务端 RCE</strong>。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/helpers/tool_parser_helper.py</span><span class="ln">PR #3343 · commit 1131535</span></div>
<pre><span class="cm"># 旧（有漏洞）：服务端对沙箱 stdout 直接 pickle.loads -> 服务端 RCE</span>
<span class="cm">- result = pickle.loads(text)</span>
<span class="cm"># 新（已修复）：只 json.loads，绝不执行代码</span>
<span class="cm">+ result = json.loads(payload)</span>
</pre></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">注意分寸：<span class="mono">marker+长度+MD5</span> 帧<strong>早于 #3343 就存在</strong>。#3343 只把 sandbox→server 的 <strong>payload 编码</strong>从 pickle 换成 JSON；server→sandbox 仍然 pickle <span class="mono">agent_state</span>——那是有意保留的受信方向，不是漏改。</span></div>
<p>这条修复的价值不在代码量，而在<strong>思路</strong>：序列化格式的选择本身就是一道安全闸。把 pickle 留给"我造的、往低信任侧流"的数据，把 JSON 留给"别人造的、往高信任侧回"的数据——这条规矩一旦内化，类似的 RCE 在设计阶段就被挡住，而不必等事后修补。</p>

<h2>把回程在脑子里走一遍</h2>
<p>抽象讲完，拿个具体例子收一收。假设用户写了个 <span class="mono">get_weather(city)</span> 工具，模型在某一步决定调用它、参数是 <span class="mono">city="上海"</span>。从这一刻起，发生的事是这样的。</p>
<p>服务端先把当前 <span class="mono">agent_state</span> 用 <span class="mono">pickle.dumps</span> 成一段字节，连同 <span class="mono">city</span> 的字面量、用户那段 <span class="mono">get_weather</span> 源码，一起拼进一份临时脚本。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">这一步就能看清区分：<span class="mono">agent_state</span> 是 pickle 字节，而 <span class="mono">city</span> 只是脚本里一个内联的字符串字面量 <span class="mono">"上海"</span>。同一份脚本，两种"塞数据进去"的方式，对应两种信任。</span></div>
<p>脚本被丢进沙箱执行：沙箱里 <span class="mono">pickle.loads</span> 还原 <span class="mono">agent_state</span>、跑 <span class="mono">get_weather("上海")</span>、拿到返回值，再把"返回值 + 更新后的 agent_state"打成 JSON，前面缀上 marker、长度、MD5，整包写进 stdout。</p>
<div class="note tip"><span class="ni">🧷</span><span class="nx">这里是全课的转折点：从下一步起，所有数据都<strong>跨过了不可信边界</strong>。沙箱刚执行完一段我们无法预先信任的代码，它写出来的每个字节，都得当"外人递出的包裹"来对待。</span></div>
<p>服务端读回 stdout：先用 marker 定位、按长度切片、比对 MD5——任何一步不符，就判定结果损坏、直接抛错。校验通过后，<strong>只</strong>对 payload 做 <span class="mono">json.loads</span>。</p>
<p>最后用 <span class="mono">AgentState.model_validate</span> 把状态重新水合成对象。全程没有任何一行对沙箱输出做 <span class="mono">pickle.loads</span>——这就是整条旅程的安全保证：往里是 pickle、往外是 JSON，边界两侧泾渭分明。</p>
<div class="note tip"><span class="ni">🧷</span><span class="nx">把这趟旅程压缩成一句话：<strong>数据下行用 pickle、上行用 JSON，中间隔着一道 marker+长度+MD5 的安检门</strong>。记住这句，等于记住了整课。</span></div>

<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>一句话收束：<strong>你信任哪个方向，决定你用哪种序列化。</strong></p>
<p><span class="mono">pickle.loads</span> 能在反序列化时执行任意代码，于是规则被砍到极简：<strong>可以 pickle.loads 你自己造的数据</strong>（server→sandbox，权限往下流进低信任沙箱，没风险）；<strong>绝不 pickle.loads 跨过不可信边界回来的数据</strong>（sandbox→server，刚跑完任意用户代码，只能当 JSON 读）。</p>
<p>PR #3343 修的正是这个：旧代码 <span class="mono">pickle.loads</span> 沙箱 stdout——服务端 RCE；改成 <span class="mono">json.loads</span> 就堵死了。而 <span class="mono">marker+长度+MD5</span> 是另一层——完整性层：用户工具能打假结果，marker 圈真 payload、MD5 抓篡改。</p>
<p>安全被化简成一个词：<strong>信任＝方向</strong>。这也收口了整条工具链：第 18 课"不跑代码就读它" → 第 19 课"自定义→沙箱" → 第 20 课"连沙箱的输出也不可信"。</p>
<p>顺着这条线还能预判别处：只要看到"反序列化不可信来源"，就该立刻警觉；只要确认"数据是自己造、往低信任侧送"，就可以放心用高表达力的格式。这套直觉，远不止用在沙箱上，它几乎是所有跨边界通信的底色。</p>
</div>

<div class="card detail"><div class="tag">🔬 落到代码</div>
<p>生成脚本：<span class="mono">tool_sandbox/base.py::AsyncToolSandboxBase.generate_execution_script</span> 与 <span class="mono">_render_sandbox_code</span>。本地执行：<span class="mono">local_sandbox.py::AsyncToolSandboxLocal</span>（建/复用 venv、子进程、超时）。</p>
<p>回读校验：<span class="mono">local_sandbox.py::parse_out_function_results_markers</span> 找 marker、切长度、比 MD5；再交 <span class="mono">helpers/tool_parser_helper.py::parse_stdout_best_effort</span> 做 <span class="mono">json.loads</span> + <span class="mono">AgentState.model_validate</span>。</p>
<p>类型与安全：沙箱类型在 <span class="mono">schemas/enums.py::SandboxType</span>；本次安全修复是 PR #3343（commit <span class="mono">1131535</span>）。</p>
<p>顺带一提，<span class="mono">local_sandbox.py</span> 里还藏着 venv 复用、依赖安装、超时控制等工程细节；它们不影响信任边界这条主线，却决定了本地沙箱跑得快不快、稳不稳。</p>
</div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p><strong>误区一：以为脚本由 <span class="mono">.j2</span> 模板渲染。</strong> <span class="mono">letta/templates/sandbox_code_file.py.j2</span> 在 v0.16.8 <strong>未被任何 .py 引用</strong>，只能当对照参考；真实脚本由 <span class="mono">_render_sandbox_code</span> 拼字符串。</p>
<p><strong>误区二：以为参数也走 pickle。</strong> 参数是<strong>内联字面量</strong>（<span class="mono">repr()</span>），整段脚本里只有 <span class="mono">agent_state</span> 一项走 pickle。</p>
<p><strong>误区三：以为帧是 #3343 加的。</strong> <span class="mono">marker+长度+MD5</span> 帧<strong>早就存在</strong>，#3343 只改了 payload 编码（pickle→JSON）。</p>
<p><strong>误区四：信 docstring 和变量名。</strong> <span class="mono">generate_execution_script</span> 的 docstring 写着"base64-encode/pickle the result"、变量名带 <span class="mono">_pkl</span>——都是<strong>遗留</strong>，实际装的是 JSON。</p>
</div>
<h2>再挖深一点</h2>
<p>下面四个抽屉，分别回答"为什么这样切边界""帧到底防谁""#3343 改了哪一段""本地 venv 怎么跑"。想细抠的同学可以逐个展开。</p>
<details class="accordion"><summary>① 信任边界为什么这样切？</summary><div class="acc-body">
<p>核心只有一条：<span class="mono">pickle.loads</span> 会在反序列化时执行任意代码。所以"能不能 pickle.loads"等价于"我信不信这段字节的来源"。</p>
<p>server→sandbox 的 <span class="mono">agent_state</span> 是服务端自己 <span class="mono">pickle.dumps</span> 的，来源可信，沙箱只 loads——风险往低信任侧流，没问题。sandbox→server 的输出来自陌生代码，来源不可信，所以只能 <span class="mono">json.loads</span>。</p>
<p>再换个角度：信任不是"信不信这段数据长得对"，而是"信不信造它的人"。pickle 危险，恰恰因为它把"数据"和"可执行代码"混在一起——来源可信时这种混合很方便（能直接还原复杂对象），来源不可信时它就成了炸弹。</p>
</div></details>
<details class="accordion"><summary>② marker+长度+MD5 防的是什么？</summary><div class="acc-body">
<p>防的是"结果通道被污染"。沙箱的 stdout 谁都能写：调试 print、异常栈、甚至一个伪造的 marker 加假结果。</p>
<p>于是三层各司其职：<span class="mono">marker</span> 在噪声里定位真 payload 的起点；<span class="mono">length</span> 精确切出 payload，避免被尾部噪声带偏；<span class="mono">MD5</span> 比对校验和，一旦被截断或篡改就 <span class="mono">raise Exception("Function ran, but output is corrupted.")</span>。</p>
<p>还有个细节：<span class="mono">marker</span> 是 uuid5 生成的 16 字节，几乎不可能被用户输出意外撞上，也很难被恶意"猜中"，于是"定位"这一步本身就带了一点防伪意味。</p>
<p>有人会问：MD5 不是不安全吗？这里它只用来抓<strong>意外损坏</strong>，并不抗密码学攻击——真正挡恶意的是"只 json.loads、绝不 pickle.loads"那条规矩，MD5 只是完整性的廉价快照。</p>
</div></details>
<details class="accordion"><summary>③ PR #3343 到底改了什么？</summary><div class="acc-body">
<p>只改了一件事：把 sandbox→server 的 <strong>payload 编码</strong>从 pickle 换成 JSON，于是服务端读回来时从 <span class="mono">pickle.loads</span> 变成 <span class="mono">json.loads</span>，RCE 面被消除。</p>
<p>没改的：marker+长度+MD5 帧（本就存在）、server→sandbox 仍 pickle <span class="mono">agent_state</span>（有意的受信方向）。另外 <span class="mono">safe_pickle.py::safe_pickle_dumps</span> 只服务于 modal_sandbox_v2，加的是 10MB/深度 50 的防崩溃护栏，并非防恶意。</p>
<p>一句话区分两件事：帧负责<strong>完整性</strong>（结果没被改坏），编码格式负责<strong>安全性</strong>（读它不会执行代码）。#3343 动的是后者，前者从一开始就在。</p>
<p>想直观点：修复前服务端这端是 <span class="mono">pickle.loads(沙箱字节)</span>，修复后是 <span class="mono">json.loads(沙箱字节)</span>。同样在读不可信输入，前者能被反序列化触发 RCE，后者最多解析失败——差别就这么大。</p>
</div></details>
<details class="accordion"><summary>④ 本地 venv 怎么跑？E2B/Modal 有何不同？</summary><div class="acc-body">
<p>本地 <span class="mono">AsyncToolSandboxLocal</span>：按需 <span class="mono">venv.create(with_pip=True)</span> 建或复用虚拟环境、<span class="mono">pip install -r</span> 装依赖，脚本写临时 <span class="mono">.py</span>，用 <span class="mono">asyncio.create_subprocess_exec</span> 起子进程跑，超时是 <span class="mono">tool_sandbox_timeout</span>（默认 180s）。</p>
<p>差异只在外层：E2B 回程会多包一层 base64；Modal 返回的是结构化 dict。但"生成脚本 + 信任边界 + 帧校验"这套主干，在三种沙箱里是一致的。</p>
<p>也正因为本地沙箱与服务端共享内核，它的隔离是"够用级"而非"强保证"：能挡住误伤和大多数意外，但要跑完全不可信的代码，应切到 E2B 或 Modal 的容器级隔离。</p>
<p>超时到了会怎样？子进程被杀、本次调用按失败处理，不会把服务端拖死。临时脚本文件用完即清，venv 则可复用，省去每次重新建环境的开销。</p>
</div></details>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li>自定义工具是不可信代码，跑在沙箱里（<span class="mono">local / E2B / Modal</span>，由 <span class="mono">SandboxType</span> 三选一）。</li>
<li><strong>server→sandbox = pickle</strong>（受信，传 <span class="mono">agent_state</span>）；<strong>sandbox→server = JSON</strong>（不可信）+ <span class="mono">marker+长度+MD5</span> 帧。</li>
<li><strong>绝不 <span class="mono">pickle.loads</span> 沙箱输出</strong>——这正是 PR #3343（commit <span class="mono">1131535</span>）的修复。</li>
<li><span class="mono">.j2</span> 模板在 v0.16.8 未被引用，真实脚本在 <span class="mono">_render_sandbox_code</span>；docstring 与 <span class="mono">_pkl</span> 命名是遗留。</li>
<li>一个词记住全部：<strong>信任＝方向</strong>。</li>
</ul>
</div>

<h2>第五部分收尾：定义 → 派生 → 分发 → 隔离执行</h2>
<p>第五部分到这里走完。把四课串成一条线，工具系统的全貌就清楚了：从"一个普通 Python 函数"到"安全地跑完一段陌生代码"，每一步都在回答一个具体问题。</p>
<div class="cellgroup"><div class="cg-cap"><b>Part 5 · 一条线</b></div><div class="cells"><span class="cell">17 函数+docstring→schema</span><span class="sep">·</span><span class="cell">18 不跑就派生</span><span class="sep">·</span><span class="cell">19 按类型分发执行</span><span class="sep">·</span><span class="cell hl">20 沙箱隔离+信任边界</span></div></div>
<p>一句话串起来：<strong>定义 → 派生 → 分发 → 隔离执行</strong>。第 17 课把函数变成 schema，第 18 课不执行就派生出 schema，第 19 课按 <span class="mono">ToolType</span> 分发给执行器，第 20 课处理最危险的一类——自定义代码——并画清它运行时的信任边界。</p>
<div class="note tip"><span class="ni">🧷</span><span class="nx">它还回指前两课：第 20 课"连沙箱输出也不可信"，与第 18 课"不执行就读它"是同一种警惕；而第 19 课结尾那次"自定义→沙箱"的 handoff，正是在这一课被兑现。</span></div>
<p>拉远看，这也是整份《Letta 可视化指南》在工具这块的全部野心：不堆砌 API，而是把"一个普通函数怎么变成模型能安全调用的能力"这条链，从头到尾讲透——定义它、派生它的接口、按类型分发它、再隔离地执行它。</p>
<div class="note tip"><span class="ni">🧷</span><span class="nx">如果你只带走一张图，就带"信任＝方向"这张：它不仅解释了沙箱，也是一切"跨信任边界传数据"问题的通用解法——无论对面是沙箱、第三方服务，还是另一个不受控的进程。</span></div>
<p>下一站是<strong>第六部分 · LLM Provider 抽象</strong>：工具讲完了，我们回到更上游的问题——Letta 怎么用一套统一接口，把 OpenAI、Anthropic 等不同厂商的模型，接进同一个 agent 循环。</p>
""", "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Lesson 19 ended on a cliffhanger: a custom tool — Python source the user wrote themselves — is by default handed to <span class="mono">SandboxToolExecutor</span>, i.e. "thrown into a sandbox." But what gives the sandbox the nerve to run a stranger's code? And once it finishes, how do you safely collect the result back into the server?</p>

<p class="lead" style="font-size:1.06rem;color:var(--muted)">This is Part 5's finale, and the landing point for the whole tool system's "security mindset." We will draw one <strong>trust-boundary diagram</strong> clearly: which leg of the trip you can "pass along freely," which leg "must be verified," and how one real security fix (PR #3343) welds that boundary shut.</p>

<div class="card analogy"><div class="tag">🔌 Real-world analogy</div>
<p>Think of the sandbox as a prison visitation window. You (the server) want to pass something <strong>in</strong> — it is your own belongings, so you can hand over the original object. Because the risk only flows inward: once something is behind the high wall, however dangerous, it can never reach your side.</p>
<p>But any parcel the other party (the stranger's code running inside) hands <strong>out</strong>, you must never reach in and take directly. It has to go through the glass, through the scanner, with its seal checked — because you have no idea whether it holds candy or a razor blade.</p>
<p>All of this lesson's sense of safety rests on one plain rule: <strong>passing in may be the original; collecting out must pass the scanner</strong>. The rest of the engineering merely translates "the original" into <span class="mono">pickle</span> and "the scanner" into <span class="mono">JSON</span> plus a layer of verification.</p>
<p>The rule looks simple yet is often broken: many "sandboxes" fixate on locking code <em>in</em>, yet forget that "collecting the result" crosses the boundary just the same. Real safety hides precisely in <strong>how you take things back out</strong>.</p>
</div>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>One sentence is enough: <strong>a custom tool is untrusted code</strong>. It does not run in the main process; it is dropped into a sandbox — a local venv, E2B, or Modal, one of three picked by <span class="mono">SandboxType</span>.</p>
<p>Across the wall there are only two data channels, opposite in direction and opposite in trust. <strong>server→sandbox</strong> uses <span class="mono">pickle</span> (trusted: the server serializes the <span class="mono">agent_state</span> it built itself); <strong>sandbox→server</strong> uses <span class="mono">JSON</span> (untrusted: <strong>never <span class="mono">pickle.loads</span></strong>), with a <span class="mono">marker+length+MD5</span> frame to verify integrity.</p>
<p>This <strong>trust-boundary diagram</strong> is the whole lesson. And PR #3343 is exactly the real security fix that switched the return channel from pickle to JSON — taking this boundary from "roughly safe" to "welded shut."</p>
<p>Stressing the sense of direction once more: when data flows from server to sandbox, privilege <strong>narrows</strong> (entering a low-trust zone), so pickle is safe; when data flows from sandbox back to server, privilege <strong>widens</strong> (returning to a high-trust zone), so it must be JSON only. Treat "the direction in which privilege widens" as the red line, and you have memorized the whole diagram.</p>
</div>
<h2>Three sandboxes, one pick: where does the code actually run?</h2>
<p>Before a custom tool runs, Letta first decides "where to run it." This is not random but a short-circuit decision chain: check the tool's own preference first, then the global config, and finally fall back to local.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Check tool.metadata</h4><p>If the tool explicitly marks <span class="mono">sandbox=="modal"</span> and Modal is enabled → use <strong>Modal</strong> (cloud container, strong isolation).</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Check the global config</h4><p>Otherwise consult <span class="mono">ToolSettings.sandbox_type</span>: if an <span class="mono">e2b_api_key</span> is set → use <strong>E2B</strong> (cloud micro-sandbox).</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Fall back to local</h4><p>Neither → <strong>Local</strong>: build an isolated venv on the host and run it in a subprocess. The most common case during development.</p></div></div>
</div>
<p>The three sandboxes are not redundant; they are a <strong>trade-off between isolation strength and deployment cost</strong>. A local venv has zero dependencies and is fastest, but shares the kernel with the server and isolates the least; E2B and Modal ship code into a dedicated cloud container — strong isolation, yet they need network access and quota. So the same tool may run locally in development and be switched to Modal in production — exactly why "where to run" must be configurable.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">The type is defined in <span class="mono">schemas/enums.py::SandboxType</span> (<span class="mono">E2B / MODAL / LOCAL</span>); the selection logic lives in <span class="mono">sandbox_tool_executor.py</span>, and the global switch is <span class="mono">settings.py::ToolSettings.sandbox_type</span>. The key point: whichever you pick, the "generate script + trust boundary + frame check" machinery below is <strong>identical across all three sandboxes</strong> — the only difference is the outer container.</span></div>
<p>A configuration aside: <span class="mono">LocalSandboxConfig</span> can also tune <span class="mono">sandbox_dir</span>, <span class="mono">use_venv</span>, <span class="mono">venv_name</span>, <span class="mono">pip_requirements</span> and more, deciding how the local sandbox is actually laid down. But these are all "how to run" knobs; they do not change the "whom to trust" boundary.</p>
<h2>The generated sandbox script: wrap the tool and run it</h2>
<p>The sandbox does not "directly call" the user's function. The server assembles a Python script on the fly, inlines everything it needs, and then lets the sandbox execute the whole thing. That script is assembled by <span class="mono">tool_sandbox/base.py::_render_sandbox_code</span>.</p>
<p>This "assemble-the-script" approach has an upside: the server has <strong>full control</strong> over everything that happens inside the sandbox — what gets passed in, what gets called, how the result is packed are all hard-coded into the script, and the sandbox is merely an obedient executor.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Unpickle agent_state</h4><p><span class="mono">pickle.loads(...)</span> restores the <span class="mono">agent_state</span> the server passed in (the trusted direction).</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Inline the arguments</h4><p>Each call argument is written as a literal via <span class="mono">repr()</span>, <strong>not</strong> pickle.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Inline the user source</h4><p>The tool's <span class="mono">source_code</span> is pasted in verbatim, defining the function body.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Call + pack</h4><p><span class="mono">_function_result = tool(...)</span>, then pack the result + <span class="mono">agent_state</span> into JSON.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Frame + write stdout</h4><p>Prefix it with <span class="mono">marker+length+MD5</span>, write to standard output, and wait for the server to read it.</p></div></div>
</div>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/tool_sandbox/base.py</span><span class="ln">_render_sandbox_code (simplified skeleton)</span></div>
<pre><span class="cm"># server pickles agent_state into the script; the sandbox loads it (trusted direction)</span>
agent_state = pickle.<span class="fn">loads</span>(<span class="nb">b"..."</span>)
x = <span class="st">"&lt;inlined literal&gt;"</span>            <span class="cm"># args inlined via repr(), not pickle</span>
<span class="cm"># &lt;user tool source inlined verbatim&gt;</span>
_function_result = <span class="fn">my_tool</span>(x, agent_state=agent_state)
payload = _letta_json.<span class="fn">dumps</span>({<span class="st">"results"</span>: _function_result,
    <span class="st">"agent_state"</span>: agent_state.<span class="fn">model_dump</span>(mode=<span class="st">"json"</span>)}).<span class="fn">encode</span>()  <span class="cm"># JSON, not pickle</span>
sys.stdout.buffer.<span class="fn">write</span>(MARKER + struct.<span class="fn">pack</span>(<span class="st">"&gt;I"</span>, len(payload)) + md5_hex + payload)
</pre></div>
<div class="note info"><span class="ni">💡</span><span class="nx">Why inline the source <strong>verbatim</strong> instead of importing the user's module? Because that module simply does not exist inside the sandbox — the tool source lives only in the database. Inlined, the script is self-contained, and the sandbox needs only a clean interpreter to run it. The script also calls <span class="mono">coerce_dict_args_by_annotations(...)</span> to coerce each argument to the right type per its annotation, avoiding string/number mismatches.</span></div>
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><span class="mono">agent_state</span> goes through <span class="mono">pickle.dumps</span> (server-built, sandbox <span class="mono">loads</span>); but <strong>the call arguments are inlined literals (<span class="mono">repr()</span>), not pickle</strong>. In the entire script, <span class="mono">agent_state</span> is the only thing that uses pickle — a distinction we will lean on repeatedly later.</span></div>
<!--ENMORE-->
"""}
