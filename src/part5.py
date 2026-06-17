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
<div class="step"><div class="num">2</div><div class="sc"><h4>选出函数节点</h4><p>遍历 <span class="mono">tree.body</span>，取<strong>最后一个</strong> <span class="mono">FunctionDef</span> 当作工具本体。</p></div></div>
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
    func = [n <span class="kw">for</span> n <span class="kw">in</span> tree.body <span class="kw">if</span> isinstance(n, ast.FunctionDef)][-<span class="nb">1</span>]  <span class="cm"># 取最后一个函数</span>
    <span class="cm"># 重建 inspect.Signature：参数名、注解、用 ast.literal_eval 取默认值</span>
    <span class="cm"># 未定义的 BaseModel 用 type(name, (BaseModel,), {...}) 造桩，不 import</span>
    <span class="kw">return</span> <span class="fn">MockFunction</span>(func.name, ast.<span class="fn">get_docstring</span>(func), sig)
</pre></div>
<p>顺带一提，docstring 不是手撕字符串得来的，而是用 <span class="mono">ast.get_docstring(func)</span> 规规矩矩地取——它能正确处理多行、缩进、转义等细节，比自己写正则稳妥得多。又是一处"让标准库替你把脏活干净利落地干掉"的体现。</p>
<div class="note info"><span class="ni">📌</span><span class="nx">一段源码里若有<strong>多个函数</strong>，取<strong>最后一个</strong> <span class="mono">FunctionDef</span>（约定：工具就是文件里最后定义的那个）。配套的 AST 辅助住在 <span class="mono">letta/functions/ast_parsers.py</span>，其中 <span class="mono">resolve_type</span> 用<strong>白名单</strong>解析类型，默认 <span class="mono">allow_unsafe_eval=False</span>，从源头杜绝"借解析之名跑代码"。</span></div>
<p>这里还藏着两个值得记住的"安全阀"。第一个针对默认值：解析器不用 <span class="mono">eval</span>，而用 <span class="mono">ast.literal_eval</span>——后者只接受数字、字符串、列表、字典这类<strong>字面量</strong>，碰到函数调用或任意表达式就直接拒绝，从根上堵死"连求个默认值都能偷跑代码"的缝隙。</p>
<p>第二个针对类型注解：注解里的名字交给 <span class="mono">ast_parsers.py::resolve_type</span> 按<strong>白名单</strong>翻译成 JSON schema 类型。认识的类型照常映射，不认识的名字<strong>不会</strong>被 import 求值，而是走"造桩或报错"。两道阀门合起来，确保"解析"绝不退化成"执行"。</p>

<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>一句话概括这门手艺：<strong>"从一段你拒绝运行的代码里，生成它的 schema。"</strong> 读函数签名最朴素的办法是 <span class="mono">import + inspect</span>，可 <span class="mono">import</span> 用户代码＝在你的服务端执行任意代码。Letta 的巧招是：先 <span class="mono">ast.parse</span> 成语法树（只读不跑），再造一个只带 <span class="mono">__name__/__doc__/__signature__</span> 的 <span class="mono">MockFunction</span>，喂给<strong>完全相同</strong>的 <span class="mono">generate_schema</span>。</p>
<p>结果是：模型拿到一张真 schema，服务器却<strong>一行用户代码都没跑</strong>。连源码里引用的未定义 Pydantic 类型，也用 <span class="mono">type(name,(BaseModel,),{})</span> 造桩，而非 import。它把"安全"巧妙地变成了一道"解析"题——这正是第 20 课沙箱哲学的前奏：<strong>"工具的代码，自始至终不可信。"</strong></p>
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
<p><strong>为什么：</strong>约定"工具是文件末尾那个函数"。若签名里引用了某个<strong>未定义</strong>的 Pydantic 模型，就用 <span class="mono">type(name, (BaseModel,), {...})</span> 当场造一个<strong>桩类</strong>顶上，绝不去 <span class="mono">import</span> 真实定义——既能让签名成形，又守住"不跑用户代码"的底线。</p>
<p><strong>源码：</strong><span class="mono">_parse_function_from_source</span> 配合 <span class="mono">letta/functions/ast_parsers.py::resolve_type</span>（白名单解析）。</p>
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
<div class="step"><div class="num">2</div><div class="sc"><h4>Pick the function node</h4><p>Walk <span class="mono">tree.body</span> and take the <strong>last</strong> <span class="mono">FunctionDef</span> as the tool body.</p></div></div>
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
<!--ENMORE-->
"""}
