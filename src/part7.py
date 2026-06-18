"""Part 7 - Server & persistence (lessons 24-27).

Lesson 24 opens Part 7: the three-layer architecture. It traces a single HTTP
request as it falls through three layers down to the database:

    thin REST routers -> SyncServer + Managers -> ORM (CRUD + access control) -> DB

with one process-global SyncServer. Each lesson dict mirrors the house style of
Parts 1-6 (cards / notes / cute / codefile / vflow / layers / cellgroup / table.t).
The en value is intentionally left as a stub for the next agent to author.
"""

LESSON_24 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">前六个部分，我们一直泡在 agent 的"大脑"里：记忆怎么分层、循环怎么转、工具怎么调、各家 provider 怎么收敛成一种形状。可这颗大脑究竟跑在哪儿？是谁把一条 HTTP 请求接进来、一路送到数据库、再把结果取回去？</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">答案是<strong>服务端</strong>。这一课正式翻开第七部分：我们追一条请求穿过三层楼——<strong>薄路由</strong>只登记转交，<strong>SyncServer 与各 Manager</strong> 才是业务枢纽，<strong>ORM</strong> 守着访问控制把活儿落到 <strong>DB</strong>。撑起这一切的，是进程里<strong>唯一一个全局 <span class="mono">SyncServer</span></strong>。</p>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>一条 HTTP 请求，要穿过三层才落到数据库</strong>。</p>
<p>第一层是<strong>薄路由</strong>：REST 端点几乎不写业务，解析一下身份与参数就转交出去。</p>
<p>第二层是 <span class="mono">SyncServer</span> 和它名下一众 <strong>Manager</strong>：业务编排与数据库 session 都在这层落地。</p>
<p>第三层是 <strong>ORM</strong>（<span class="mono">sqlalchemy_base.py::SqlalchemyBase</span>）：负责 CRUD，还顺手把访问控制（多租户隔离）焊进每条 SQL。</p>
<p>最终落到 <strong>DB</strong>（<span class="mono">db.py::db_registry.async_session</span>）。而撑起整座楼的，是进程里<strong>唯一一个全局 <span class="mono">SyncServer</span></strong>。</p>
</div>
<p>这三层不是凭空的分类，而是一条请求真实的下行路线。先把这条线画出来，后面每一节都在拆其中一段。</p>
<p>读这一课时，不妨把自己想成那条请求：你会先在前台被登记身份，再被转给某位经理，经理替你开一道事务门去档案室取件，最后把结果顺着原路递回你手上。</p>
<h2>三层楼：一条请求的下行路线</h2>
<p>把这栋楼竖起来看最直观：从大门进来的 HTTP，逐层往下落，最后在数据库里读写，再原路把结果带回去。</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">第一层</span><span class="name">薄路由 · REST routers</span></div>
    <div class="ld">如 <span class="mono">routers/v1/agents.py::retrieve_agent</span>。几乎不写业务：解析 actor、处理轻量参数，然后转交。</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">第二层</span><span class="name">SyncServer + Managers</span></div>
    <div class="ld">业务枢纽与 DB session 都在这层。薄端点常常<strong>绕过</strong> SyncServer，直接 <span class="mono">server.agent_manager.…</span>；只有跨多个 manager 的编排才调 SyncServer 自己的方法。</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">第三层</span><span class="name">ORM · SqlalchemyBase</span></div>
    <div class="ld"><span class="mono">sqlalchemy_base.py::SqlalchemyBase</span> 提供 CRUD，并把 <span class="mono">apply_access_predicate</span> 这类访问控制焊进每条查询。</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">落点</span><span class="name">DB · async_session</span></div>
    <div class="ld">真正的读写发生在 <span class="mono">db.py::db_registry.async_session</span> 开出的会话里——一次请求往往要开好几次。</div></div>
</div>
<p>注意第二层那行小字：薄端点多数时候<strong>直接调 manager</strong>，并不经过 SyncServer 的方法。这点反直觉，后面会专门拿数据说话。</p>
<p>也请记住一个边界：DB session 只在第二层（manager 里）开关，<strong>第一层路由从不碰数据库</strong>。这条边界是后面"多个事务"那一节的伏笔。</p>
<p>别忘了请求还要<strong>原路返回</strong>：DB 取到的行，逐层往上抬，经 ORM 转成对象、经 manager 交回路由，最后由路由序列化成 JSON 应答。下行调用、上行返回，一来一回才算走完。</p>
<p>顺道认一下方向感：图里越往下，越靠近数据、也越"有状态"；越往上，越靠近协议、越"无状态"。三层架构的整洁，正来自这条上下分工。</p>
<p>换句话说，这张图既是"调用栈"也是"信任边界"：每往下一层，能做的事更多、责任也更重，于是访问控制必须压在最底下，而不是最上面。</p>
<div class="card analogy"><div class="tag">🏢 生活类比</div>
<p>把整套服务端想象成一栋<strong>三层楼的公司</strong>，你（HTTP 请求）走进大门办一件事。</p>
<p><strong>一楼前台</strong>（薄路由）只做登记：核对你是谁、把表格收齐，然后说"这事归二楼"，把条子递上去。前台从不亲自翻档案。</p>
<p><strong>二楼经理</strong>（Manager）才有权动数据。要紧的是——每动一次档案，经理都要亲手开一道叫"<strong>事务</strong>"的门，办完即关。</p>
<p><strong>三楼档案室</strong>（ORM / DB）保管所有资料，但谁能看哪一份，由门禁（访问控制）说了算，经理也不能越权。</p>
<p>还有个老板（<span class="mono">SyncServer</span>）坐镇：他不亲自办每件小事，只在"一件事要好几个经理一起协调"时才出面，平时大家直接找对应的经理。</p>
<p>这个类比有一处要较真：老板并不是"什么都要过问"的瓶颈。日常小事大家直接找经理，只有那种"要跨好几个部门"的大事，才需要老板出面统筹。</p>
</div>
<h2>一个进程，一个全局 SyncServer</h2>
<p>整座楼能立住，全靠地基那一个全局 <span class="mono">SyncServer</span>。它从哪来？答案有点出人意料。</p>
<p>它是 <span class="mono">app.py::server</span> 里的一个<strong>模块级全局变量</strong>，在模块被 <strong>import 那一刻</strong>就造好了。</p>
<p>有意思的是：工厂函数 <span class="mono">app.py::create_application</span> 里其实也有一行 <span class="mono">SyncServer(...)</span>，但那行是<strong>注释掉的</strong>——server 并不在工厂里建。</p>
<p>于是启动被切成清清楚楚的两段：<strong>import 时</strong>同步接线（造好 server 和它名下所有 manager），<strong>启动时</strong>再异步初始化。</p>
<p>第二段就是 <span class="mono">app.py::lifespan</span> 干的事：只做异步引导——<span class="mono">await server.init_async(...)</span> 建默认 org/user、把基础工具 upsert 进库。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/app.py</span><span class="ln">全局 server + 两段式启动（简化）</span></div>
<pre><span class="cm"># 模块级全局：import 这个模块时就建好了一个 SyncServer</span>
server = <span class="fn">SyncServer</span>(default_interface_factory=<span class="kw">lambda</span>: <span class="fn">interface</span>())

<span class="kw">def</span> <span class="fn">create_application</span>() -&gt; FastAPI:
    app = <span class="fn">FastAPI</span>(..., lifespan=lifespan)
    <span class="cm"># server = SyncServer(...)   # 源码里这一行是注释掉的：server 不在工厂里建</span>
    <span class="kw">return</span> app

<span class="nb">@asynccontextmanager</span>
<span class="kw">async</span> <span class="kw">def</span> <span class="fn">lifespan</span>(app: FastAPI):
    <span class="cm"># 启动时只做异步引导：建默认 org/user、upsert 基础工具</span>
    <span class="kw">await</span> server.<span class="fn">init_async</span>(init_with_default_org_and_user=<span class="kw">True</span>)
    <span class="kw">yield</span>

<span class="cm"># ---- letta/server/rest_api/dependencies.py ----</span>
<span class="kw">def</span> <span class="fn">get_letta_server</span>() -&gt; SyncServer:
    <span class="kw">from</span> letta.server.rest_api.app <span class="kw">import</span> server   <span class="cm"># 惰性 import 那个模块全局</span>
    <span class="kw">return</span> server                                  <span class="cm"># 不放 app.state；每个路由拿到同一个</span>
</pre></div>
<p>路由怎么拿到这同一个 server？靠依赖注入。<span class="mono">dependencies.py::get_letta_server</span> 惰性 import 那个模块全局并直接返回，<strong>不</strong>塞进 <span class="mono">app.state</span>。</p>
<p>这里有个对照容易混：<span class="mono">create_application</span> 造的是 FastAPI <strong>应用</strong>对象，而 <span class="mono">server</span> 是那个全局<strong>业务</strong>对象——一个管路由与中间件，一个管 manager 与数据，两者分得很开。</p>
<p>每个路由用 <span class="mono">Depends(get_letta_server)</span> 要一份，拿到的<strong>都是同一个实例</strong>。这就是"一个进程，一个全局 server"在代码里的落地方式。</p>
<p>为什么非要在 import 时就建好？因为这样任何模块都能 <span class="mono">from app import server</span> 拿到同一个实例，无需层层传参，也不必依赖 FastAPI 的 <span class="mono">app.state</span>。</p>
<p>那 <span class="mono">init_async</span> 又补了什么？它做的是"建好对象之后才需要 <span class="mono">await</span> 的引导"：写入默认 org 与 user、把一批基础工具 upsert 进库——都是要落 DB、必须异步的活儿。</p>
<p>把两段分开的好处很实在：构造（同步、纯内存）与引导（异步、要落库）各归各位，启动顺序清清楚楚，也方便测试时只构造、不引导。</p>
<p>还有个细节：<span class="mono">init_async</span> 基本是<strong>可重入</strong>的——默认 org/user 不存在才建，基础工具走 upsert 而非 insert，于是重启再跑一遍也不会把数据搞乱。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">记住这条两段式：<strong>import 同步接线 + 启动异步 init</strong>。前者纯属对象构造、不碰网络与库；后者（<span class="mono">init_async</span>）才做需要 <span class="mono">await</span> 的引导，正好契合 FastAPI 的 <span class="mono">lifespan</span> 钩子。</span></div>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">server/rest_api/app.py::server</span>——模块级全局；<span class="mono">create_application</span> 里那行 <span class="mono">SyncServer(...)</span> 是注释掉的。</p>
<p><span class="mono">app.py::lifespan</span>——只做 <span class="mono">await server.init_async(init_with_default_org_and_user=...)</span>。</p>
<p><span class="mono">dependencies.py::get_letta_server</span>——惰性 import 返回全局；<span class="mono">get_headers</span> 把 <span class="mono">user_id</span> 头解析成 <span class="mono">HeaderParams.actor_id</span>。</p>
<p><span class="mono">server.py::SyncServer</span> 持有全部 manager；<span class="mono">routers/v1/agents.py::retrieve_agent</span> 是一条典型薄端点。</p>
</div>
<p>那 server 名下到底挂了哪些 manager？<span class="mono">server.py::SyncServer.__init__</span> 把它们<strong>全都作为属性持有</strong>，一次性接好线。</p>
<div class="cellgroup"><div class="cg-cap"><b>SyncServer 名下持有的 Manager（节选）</b></div><div class="cells"><span class="cell hl">agent_manager</span><span class="sep">·</span><span class="cell">message_manager</span><span class="sep">·</span><span class="cell">block_manager</span><span class="sep">·</span><span class="cell">passage_manager</span><span class="sep">·</span><span class="cell">user_manager</span><span class="sep">·</span><span class="cell">tool_manager</span><span class="sep">·</span><span class="cell">provider_manager</span><span class="sep">·</span><span class="cell">source_manager</span><span class="sep">·</span><span class="cell">step_manager</span><span class="sep">·</span><span class="cell">job_manager</span></div></div>
<p>除了这些 manager，它还顺手持有 <span class="mono">self.config</span>（一个 <span class="mono">LettaConfig</span>）和 <span class="mono">self._enabled_providers</span>。把接线节选出来看：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/server.py</span><span class="ln">SyncServer.__init__ 的 manager 接线（节选）</span></div>
<pre><span class="kw">class</span> <span class="fn">SyncServer</span>(Server):
    <span class="st">&quot;&quot;&quot;Simple single-threaded / blocking server process.&quot;&quot;&quot;</span>   <span class="cm"># 名不副实：见下文“亮点”</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, ...):
        self.config = LettaConfig.<span class="fn">load</span>()
        self.organization_manager = <span class="fn">OrganizationManager</span>()
        self.user_manager = <span class="fn">UserManager</span>()
        self.tool_manager = <span class="fn">ToolManager</span>()
        self.block_manager = <span class="fn">BlockManager</span>()        <span class="cm"># 或 GitEnabledBlockManager</span>
        self.message_manager = <span class="fn">MessageManager</span>()
        self.passage_manager = <span class="fn">PassageManager</span>()
        self.agent_manager = <span class="fn">AgentManager</span>(block_manager=self.block_manager)  <span class="cm"># manager 间组合</span>
        self.provider_manager = <span class="fn">ProviderManager</span>()
        <span class="cm"># … step / job / run / archive / source 等一应俱全</span>
        self._enabled_providers = [...]
</pre></div>
<p>留意 <span class="mono">agent_manager</span> 那行：它是 <span class="mono">AgentManager(block_manager=self.block_manager)</span>——manager 之间还会<strong>互相组合</strong>，不是各管各的孤岛。</p>
<p>这种组合不是花架子：agent 要读写记忆 block，于是 <span class="mono">agent_manager</span> 手里就攥着 <span class="mono">block_manager</span>，需要时直接借用，而不必绕一大圈再回到 server。</p>
<p>把全部 manager 都挂在一个 server 上，还有个隐性好处：它们天然共享同一套 DB 接入与配置，谁也不会各自连各自的库、各跑各的初始化。</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">这里<strong>没有消息队列</strong>：SyncServer 把所有 manager 都当成<strong>普通属性</strong>直接持有，层与层之间没有 broker、没有队列。调用就是一次次普通的 Python 方法调用，同步地穿过去。</span></div>
<p>有了这些属性，就能讲清一个最常见的误解了：路由<strong>不是</strong>把 CRUD 都走 SyncServer 的方法。</p>
<p>绝大多数时候，它通过 server 对象<strong>直接调 manager</strong>；只有需要协调好几个 manager 的编排，才会去调 SyncServer 自己的方法。</p>
<table class="t">
<tr><th>调用方式</th><th>例子</th><th>何时用</th><th>在 agents.py 的量级</th></tr>
<tr><td>直调 manager</td><td class="mono">server.agent_manager.get_agent_by_id_async(...)</td><td>单个 manager 的 CRUD</td><td>约 131 次</td></tr>
<tr><td>SyncServer 方法</td><td class="mono">server.create_agent_async(...)</td><td>跨多个 manager 的编排</td><td>约 16 次</td></tr>
</table>
<p>那 16 次"编排"具体在干嘛？以 <span class="mono">server.py::SyncServer.create_agent_async</span> 为例：它要解析 LLM / embedding 配置、变换 block，再把真正的写委托给 <span class="mono">agent_manager</span>——一个动作牵动好几个 manager。</p>
<p>所以 <span class="mono">SyncServer</span> 与其说是"通往 DB 的唯一一道门"，不如说是个<strong>服务定位器</strong>加<strong>跨-manager 协调者</strong>：定位时大家绕过它直取 manager，只有协调时它才亲自下场。</p>
<p>这也解释了为什么 SyncServer 的方法不多却很"重"：它们个个都是跨 manager 的编排门面，单 manager 能独立办完的事，根本轮不到它插手。</p>
<h2>薄路由：四步就交班</h2>
<p>回到第一层。薄路由到底"薄"到什么程度？薄到一个 GET 端点通常就四步，办完即交班。</p>
<div class="cellgroup"><div class="cg-cap"><b>薄路由的四步</b></div><div class="cells"><span class="cell hl">① 解析 actor</span><span class="sep">·</span><span class="cell">② 轻量参数处理</span><span class="sep">·</span><span class="cell">③ 调 manager / server</span><span class="sep">·</span><span class="cell">④ 返回 pydantic schema</span></div></div>
<p>第 ① 步解析 actor：<span class="mono">await server.user_manager.get_actor_or_default_async(...)</span>，把请求头里的身份换成一个 actor 对象。</p>
<p>第 ② 步是轻量参数处理——分页、过滤之类；很多端点这一步几乎为空。</p>
<p>第 ③ 步调 manager 或 server 方法，把真正的活儿交出去；第 ④ 步返回一个 pydantic schema，由 FastAPI 按 <span class="mono">response_model</span> 序列化。</p>
<p>这第 ④ 步值得多看一眼：路由直接 <span class="mono">return</span> 一个 pydantic 对象，<strong>不手写 JSON</strong>；序列化交给 FastAPI 照 <span class="mono">response_model=AgentState</span> 自动完成。</p>
<p>四步骨架并非 <span class="mono">retrieve_agent</span> 独有：列表、创建、删除这些端点，几乎都是同一副骨架——只在第 ②、③ 步换成各自的参数与 manager 调用。</p>
<p>这也是为什么读懂一个端点，往往就读懂了一整组：把 retrieve 看通，list / create / update 基本是照葫芦画瓢。</p>
<p>把 <span class="mono">routers/v1/agents.py::retrieve_agent</span> 摊开看，这四步一目了然：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/routers/v1/agents.py</span><span class="ln">retrieve_agent：薄路由四步（简化）</span></div>
<pre><span class="nb">@router.get</span>(<span class="st">"/{agent_id}"</span>, response_model=AgentState)   <span class="cm"># ④ FastAPI 按 response_model 序列化</span>
<span class="kw">async</span> <span class="kw">def</span> <span class="fn">retrieve_agent</span>(
    agent_id: str,
    server: SyncServer = <span class="fn">Depends</span>(get_letta_server),   <span class="cm"># DI：拿到那个全局 server</span>
    headers: HeaderParams = <span class="fn">Depends</span>(get_headers),     <span class="cm"># 解析 user_id 头 -&gt; actor_id</span>
):
    <span class="cm"># ① 解析 actor（session #1：查 user）</span>
    actor = <span class="kw">await</span> server.user_manager.<span class="fn">get_actor_or_default_async</span>(actor_id=headers.actor_id)
    <span class="cm"># ②（这个端点几乎没有参数要处理）③ 直接调 manager（session #2：带访问控制）</span>
    <span class="kw">return</span> <span class="kw">await</span> server.agent_manager.<span class="fn">get_agent_by_id_async</span>(agent_id=agent_id, actor=actor)
    <span class="cm"># ④ 返回的 pydantic 对象由 FastAPI 按 response_model=AgentState 序列化</span>
</pre></div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">actor 的解析在<strong>处理函数体内</strong>（第 ① 步），不是某个全局鉴权中间件。<span class="mono">dependencies.py::get_headers</span> 只把 <span class="mono">user_id</span> 头解析/校验成 <span class="mono">HeaderParams.actor_id</span>（校验 <span class="mono">user-&lt;uuid4&gt;</span> 格式、<strong>不碰 DB</strong>）；真正查 user，是函数体里 <span class="mono">await get_actor_or_default_async</span> 时才发生。</span></div>
<p>为什么要把路由做得这么薄？因为"薄"和"厚"各司其职，把它俩并排看最清楚。</p>
<div class="cols">
  <div class="col"><h4>🪶 薄路由（第一层）</h4><p>只做四步：解析 actor、处理参数、调 manager、返回 schema。<strong>不写业务、不开 DB session</strong>。换个端点，骨架几乎照抄。</p></div>
  <div class="col"><h4>🧱 厚 manager（第二层）</h4><p>业务逻辑、事务边界、多租户隔离全在这里。<strong>DB session 在 manager 里开关</strong>，访问控制焊进每条查询。</p></div>
</div>
<p>这条分界请先记牢：<strong>路由从不开 DB session</strong>，session 全在 manager 里开关。它正是下一节"为什么是多个事务"的关键。</p>
<p>还要补一句容易忽略的：薄，不等于"什么都不做"。路由仍负责 HTTP 语义——状态码、响应模型、错误到 4xx 的映射；它只是把<strong>业务</strong>那部分推给了下层。</p>
<div class="cute"><div class="row"><span class="emoji">🚪</span><span class="lab">门房·路由</span><span class="arrow">→</span><span class="emoji">🧑‍💼</span><span class="lab">经理·manager</span><span class="arrow">→</span><span class="emoji">🗄️</span><span class="bubble">档案室·ORM/DB</span></div><div class="cap">🏛️ 三层楼：门房（路由）只递条子，经理（manager）开“事务”门动数据，档案室（ORM/DB）给谁看由门禁（访问控制）说了算</div></div>
<h2>跟着一条 GET 请求走到底</h2>
<p>光看四步还不够过瘾。让我们真的牵着一条 <span class="mono">GET /v1/agents/{id}</span> 请求，从进门一路走到 DB，再原路走回来。</p>
<p>读时序图有个小技巧：把每个"事务"标记当成一次完整的"开门—取物—关门"。你会数到<strong>两次</strong>这样的开关，而它们之间并不共享同一道门。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>DI 装配</h4><p><span class="mono">get_letta_server</span> 递上那个全局 server，<span class="mono">get_headers</span> 把 <span class="mono">user_id</span> 头解析成 <span class="mono">actor_id</span>（此刻还不碰 DB）。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>解析 actor · 事务①</h4><p><span class="mono">get_actor_or_default_async</span> 开 session #1 查 user；缺 <span class="mono">user_id</span> 时在 OSS 模式落到 default user。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>查 agent · 事务②</h4><p><span class="mono">get_agent_by_id_async(actor=actor)</span> 开 session #2：<span class="mono">select(AgentModel)</span> + <span class="mono">apply_access_predicate(...ORGANIZATION)</span> + <span class="mono">where(id==...)</span>。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>取一条或 404</h4><p><span class="mono">scalar_one_or_none()</span> 拿到行；为 None 就抛 404。否则 <span class="mono">to_pydantic_async()</span> 转成 schema。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>序列化回包</h4><p>commit / close 之后，FastAPI 按 <span class="mono">response_model=AgentState</span> 把对象序列化成 JSON 返回。</p></div></div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">留意第 2、3 步：它们是<strong>两个独立事务</strong>，各开各的 session、各自 commit/close。一次请求＝<strong>多个独立事务</strong>，<strong>没有</strong>请求级的统一工作单元（UoW）。原因是事务边界被划在 manager 方法里——下面抽屉细讲。</span></div>
<p>把这条轨迹和前面的四步对上号，你会发现：路由那薄薄四步，背后其实牵动了<strong>两次入库、两道访问控制、一次序列化</strong>。</p>
<p>这正是"薄"的精髓：复杂度并没有消失，只是被<strong>压到了下面两层</strong>。路由看起来轻飘飘，是因为重活都在 manager 与 ORM 里被稳稳接住了。</p>
<p>这里也藏着访问控制的关键：第 3 步那个 <span class="mono">apply_access_predicate</span> 不是路由加的，而是 ORM 在拼 SQL 时<strong>自动焊进</strong>的，组织级隔离因此绕不过去。</p>
<p>再看上行那一程：<span class="mono">to_pydantic_async()</span> 把 ORM 行<strong>脱离 session</strong> 转成纯粹的 pydantic 对象，于是即便 session 已关闭，路由手里的数据依然完整可用。</p>
<p>这一步很关键：它把"数据库行"与"对外 schema"切开，DB 会话的生命周期就此封死在 manager 内部，不会泄漏到路由层。</p>
<p>也正因如此，路由层永远拿不到一个"还连着数据库"的对象——它能看到的，只有已经定形、可以安全序列化的 schema。</p>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p><span class="mono">SyncServer</span> 是个美丽的误名。类的 docstring 至今还写着 "Simple single-threaded / blocking server process"，可 v0.16.8 里路由调到的几乎全是 <span class="mono">async def</span>——真正的并发模型，是单事件循环上的<strong>协作式 async</strong>。</p>
<p>更妙的是：它不是一座"上帝门面"，而是一个<strong>服务定位器</strong>。薄 CRUD 端点直接绕过它，<span class="mono">server.&lt;manager&gt;.&lt;method&gt;()</span> 一穿到底。</p>
<p>SyncServer 自己的方法，只在"一个动作要协调好几个 manager"时才出场——比如 <span class="mono">create_agent_async</span> 解析 LLM/embedding 配置、变换 block、再把写委托给 <span class="mono">agent_manager</span>。</p>
<p>于是"业务枢纽"＝<strong>跨-manager 协调者</strong>，而不是"通往 DB 的唯一一道门"。这个重新理解，正是读懂这层代码的钥匙。</p>
<p>再点一下分层的接缝：FastAPI 的 <span class="mono">Depends</span> 就是那道缝——两个依赖把一个普通函数变成分层 handler，actor 在 header 依赖跑完后于<strong>函数体内</strong>解析，而非靠全局鉴权中间件。</p>
</div>
<p>把这个"误名"记在心里，你以后读 server 层就不会被名字带偏：看见 <span class="mono">Sync</span> 别当真，看见 server 别以为它什么都自己干。名字是历史，代码才是现实。</p>
<h2>再挖深一点</h2>
<p>主线到这儿就完整了。下面四个抽屉，专收你大概率会追问的细节——按兴趣展开即可，不展开也不影响对主线的理解。</p>
<details class="accordion"><summary>为什么路由要做得这么薄？</summary><div class="acc-body">
<p>把业务逻辑从路由里抽走，至少买到三样好处。</p>
<p><strong>复用</strong>：同一个 <span class="mono">agent_manager.get_agent_by_id_async</span>，REST 端点能调，内部代码、后台任务也能调，不必各写一份。</p>
<p><strong>可测</strong>：测业务不必起 HTTP——直接对 manager 写单测即可，路由那层薄到几乎不用测。</p>
<p><strong>一致鉴权</strong>：访问控制焊在 ORM 层（<span class="mono">apply_access_predicate</span>），无论谁来调 manager，组织级隔离都照样生效，而不是每个端点各写一遍、各漏一处。</p>
<p>反过来想：要是把业务塞进路由，同一段逻辑就会在 REST、后台任务、测试里各抄一份，迟早抄出三种不一致的版本——薄路由正是从源头掐断了这种漂移。</p>
</div></details>
<details class="accordion"><summary>SyncServer 为何叫 "Sync" 却几乎全是 async？</summary><div class="acc-body">
<p>纯属<strong>历史命名</strong>。早期确实有"同步、单线程、阻塞"的设想，类的 docstring 就是那时写下的。</p>
<p>但 v0.16.8 的现实是：路由调到的方法几乎全是 <span class="mono">async def</span>，并发靠单事件循环上的协作式 async，而不是多线程或阻塞。</p>
<p>名字没改，是因为它早已是无数调用点的稳定符号；改名的收益，远抵不过全仓改动的风险。读代码时，把 "Sync" 当成一个<strong>历史标签</strong>看待就好。</p>
</div></details>
<details class="accordion"><summary>一次请求为什么是多个事务，而不是一个？</summary><div class="acc-body">
<p>因为<strong>事务边界被划在 manager 方法里</strong>，而不是请求级别。</p>
<p>每个 manager 方法（如查 user、查 agent）各自用 <span class="mono">async with db_registry.async_session()</span> 开一个 session，办完即 commit/close。</p>
<p>于是 <span class="mono">retrieve_agent</span> 这一条请求，跨了<strong>两个独立事务</strong>：先查 user，再查 agent；并没有把整条请求包进一个大事务的"请求级 UoW"。</p>
<p>代价是两次读之间不是同一个快照；好处是边界清晰、各 manager 自洽，也更容易复用与测试。第 27 课会把 session 的来历讲透。</p>
<p>顺带一提：正因为没有请求级大事务，某一步失败也不会自动回滚前一步已提交的写——这把"补偿 / 幂等"的责任，明确交回到了编排方（SyncServer 或调用者）手里。</p>
</div></details>
<details class="accordion"><summary>那个可选的服务器口令中间件是什么？</summary><div class="acc-body">
<p>这是一道<strong>正交</strong>的、整服务器级的关卡，只在 secure 模式启用。</p>
<p><span class="mono">middleware/check_password.py::CheckPasswordMiddleware</span> 检查 <span class="mono">X-BARE-PASSWORD: password &lt;pw&gt;</span> 或 <span class="mono">Authorization: Bearer &lt;pw&gt;</span>；健康探针放行，否则 401。</p>
<p>它只在 <span class="mono">LETTA_SERVER_SECURE=true</span> 或 <span class="mono">--secure</span> 时才挂载，用的是<strong>单一共享密钥</strong>，与租户/actor 完全无关——别把它和前面那套 <span class="mono">user_id</span>/actor 的多租户身份混为一谈。</p>
<p>一句话分清两者：口令中间件管的是"<strong>整台服务器让不让进</strong>"，actor/user_id 管的是"<strong>进来之后能看谁的数据</strong>"。一个是大门门禁，一个是楼内门牌，互不替代。</p>
</div></details>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>路由<strong>不是</strong>都经 <span class="mono">SyncServer</span> 方法——多数是 <span class="mono">server.&lt;manager&gt;.&lt;method&gt;()</span> 直调，只有跨-manager 编排才走 SyncServer。</p>
<p><span class="mono">SyncServer</span> 名"同步"实"异步"：docstring 是历史遗留，真实路径几乎全 <span class="mono">async</span>。</p>
<p>actor 在<strong>处理函数体内</strong>解析（第 ① 步），不是全局鉴权中间件；路由层<strong>从不</strong>开 DB session。</p>
<p>缺 <span class="mono">user_id</span> 时，OSS 模式默认落到 <strong>default user</strong>，不会直接报错。</p>
<p>那个全局 server 在 <strong>import 时</strong>就建好（<span class="mono">app.py::server</span>），<strong>不</strong>在 <span class="mono">create_application</span> 工厂里；层与层之间<strong>无消息队列</strong>。</p>
</div>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li>一条请求穿三层：<strong>薄路由 → SyncServer + Managers → ORM → DB</strong>。</li>
<li>进程里<strong>唯一一个全局 <span class="mono">SyncServer</span></strong>：import 时建、<span class="mono">lifespan</span> 里 <span class="mono">init_async</span>；路由经 <span class="mono">Depends(get_letta_server)</span> 拿到同一个它。</li>
<li>薄路由四步：解析 actor → 处理参数 → 调 manager/server → 返回 schema；<strong>DB session 只在 manager 里开</strong>。</li>
<li>多数是 <strong>manager 直调</strong>，只有跨-manager 编排才走 SyncServer 方法（agents.py 约 131 : 16）。</li>
<li>一次请求＝<strong>多个独立事务</strong>；访问控制由 ORM 的 <span class="mono">apply_access_predicate</span> 焊进每条查询。</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">一句话收束：<strong>路由只接、manager 才办、ORM 守门、DB 落地，全靠一个全局 server 串起来</strong>。这三层分工，正是后面 25–27 课所有细节赖以站立的地基。</span></div>
<p>这条"薄模式"你其实早就见过：第 03 课 <span class="mono">agents.py::send_message</span> 的消息生命周期，走的正是同一套"路由只接、manager 才办"。</p>
<p>而被 server 拉起来的 agent 循环（第 13、14 课的 <span class="mono">AgentLoop.load(...)</span> 再 <span class="mono">.step(...)</span>），也是从这一层被调起来的——服务端正是它的入口。</p>
<p>接下来三课会把第二、三层逐一拆开：第 25 课讲 manager 到底怎么写业务，第 26 课讲 ORM 的 CRUD 与多租户隔离，第 27 课讲 DB session 与 <span class="mono">async_session</span> 的来历。三层楼，一层层往下走。</p>
<p>走完这三课，你就能把一条请求从 HTTP 一路到磁盘的每一步，都说得清清楚楚。</p>
""",
    "en": r"""
<!--ENMORE-->
""",
}
