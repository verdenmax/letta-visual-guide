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
<div class="note warn"><span class="ni">⚠️</span><span class="nx">这段循环藏着两道"质检关卡"：参数<strong>没有描述</strong>就 <span class="mono">raise ValueError</span>；参数<strong>缺类型注解</strong>则在 <span class="mono">type_to_json_schema_type</span> 里抛 <span class="mono">TypeError</span>。换句话说，docstring 写不全，工具根本建不出来。</span></div>
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
<tr><td class="mono">Literal[...]</td><td class="mono">enum</td><td>枚举可选值</td></tr>
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
<div class="note info"><span class="ni">📌</span><span class="nx">小结类型这一块：能用基础类型就用基础类型，要"可选"用 <span class="mono">Optional</span>，要"多选一"用 <span class="mono">Literal</span>，要"一组字段"用 Pydantic 模型——避开裸 <span class="mono">Dict</span> 和 <span class="mono">Union</span>，你就绕开了绝大多数报错。</span></div>
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
<!--ENMORE-->
"""}
