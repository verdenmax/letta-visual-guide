"""Part 7 - Server & persistence (lessons 24-27).

Lesson 24 opens Part 7: the three-layer architecture. It traces a single HTTP
request as it falls through three layers down to the database:

    thin REST routers -> SyncServer + Managers -> ORM (CRUD + access control) -> DB

with one process-global SyncServer. Each lesson dict mirrors the house style of
Parts 1-6 (cards / notes / cute / codefile / vflow / layers / cellgroup / table.t),
with bilingual zh/en content.
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
<span class="kw">async def</span> <span class="fn">lifespan</span>(app: FastAPI):
    <span class="cm"># 启动时只做异步引导：建默认 org/user、upsert 基础工具</span>
    <span class="kw">await</span> server.<span class="fn">init_async</span>(init_with_default_org_and_user=<span class="kw">True</span>)
    <span class="kw">yield</span>

<span class="cm"># ---- letta/server/rest_api/dependencies.py ----</span>
<span class="kw">async def</span> <span class="fn">get_letta_server</span>() -&gt; SyncServer:
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
<pre><span class="kw">class</span> <span class="fn">SyncServer</span>(<span class="nb">object</span>):
    <span class="st">&quot;&quot;&quot;Simple single-threaded / blocking server process&quot;&quot;&quot;</span>
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
<span class="kw">async def</span> <span class="fn">retrieve_agent</span>(
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
<p>更妙的是：它不是一座"上帝门面"，而是一个<strong>服务定位器</strong>——薄 CRUD 端点 <span class="mono">server.&lt;manager&gt;.&lt;method&gt;()</span> 一穿到底，<span class="mono">SyncServer</span> 自己的方法只在跨-manager 编排时才出场。</p>
<p>于是"业务枢纽"＝<strong>跨-manager 协调者</strong>，而不是"通往 DB 的唯一一道门"。把"名同步、实异步"配上"枢纽而非门面"，正是读懂这层代码的两把钥匙。</p>
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
<p class="lead" style="font-size:1.06rem;color:var(--muted)">For six parts we've been soaking in the agent's "brain": how memory is layered, how the loop turns, how tools get called, how every provider converges onto one shape. But where does this brain actually run? Who takes an HTTP request in, carries it all the way to the database, and brings the result back?</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">The answer is the <strong>server</strong>. This lesson formally opens Part 7: we follow one request through three floors — the <strong>thin routers</strong> only register and hand off, <strong>SyncServer and its Managers</strong> are the business hub, and the <strong>ORM</strong> guards access control as the work lands in the <strong>DB</strong>. Holding all of this up is the <strong>single global <span class="mono">SyncServer</span></strong> in the process.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Grab this lesson in one line: <strong>an HTTP request must cross three floors before it lands in the database</strong>.</p>
<p>The first floor is the <strong>thin routers</strong>: a REST endpoint writes almost no business logic — it parses identity and parameters, then hands off.</p>
<p>The second floor is <span class="mono">SyncServer</span> and the crowd of <strong>Managers</strong> under it: business orchestration and the database session both land here.</p>
<p>The third floor is the <strong>ORM</strong> (<span class="mono">sqlalchemy_base.py::SqlalchemyBase</span>): it handles CRUD and, along the way, welds access control (multi-tenant isolation) into every SQL statement.</p>
<p>It finally lands in the <strong>DB</strong> (<span class="mono">db.py::db_registry.async_session</span>). And what holds the whole building up is the <strong>single global <span class="mono">SyncServer</span></strong> in the process.</p>
</div>
<p>These three floors aren't an arbitrary taxonomy — they're a request's real path downward. Let's draw that line first; every later section takes apart one stretch of it.</p>
<p>As you read, picture yourself as that request: you're first checked in at the front desk, then handed to a manager, who opens a transaction door to the archive room to fetch your file, and finally passes the result back to you along the same path.</p>
<h2>Three floors: a request's path down</h2>
<p>Standing the building upright is the clearest view: HTTP comes in the front door, falls floor by floor, finally reads and writes in the database, then carries the result back the same way.</p>
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">Floor 1</span><span class="name">Thin routers · REST routers</span></div>
    <div class="ld">Such as <span class="mono">routers/v1/agents.py::retrieve_agent</span>. Almost no business logic: resolve the actor, handle light parameters, then hand off.</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">Floor 2</span><span class="name">SyncServer + Managers</span></div>
    <div class="ld">The business hub and the DB session both live here. Thin endpoints often <strong>bypass</strong> SyncServer and go straight to <span class="mono">server.agent_manager.…</span>; only orchestration across several managers calls SyncServer's own methods.</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">Floor 3</span><span class="name">ORM · SqlalchemyBase</span></div>
    <div class="ld"><span class="mono">sqlalchemy_base.py::SqlalchemyBase</span> provides CRUD and welds access control like <span class="mono">apply_access_predicate</span> into every query.</div></div>
  <div class="layer l-app"><div class="lh"><span class="badge">Landing</span><span class="name">DB · async_session</span></div>
    <div class="ld">The real reads and writes happen in a session opened by <span class="mono">db.py::db_registry.async_session</span> — one request often opens several.</div></div>
</div>
<p>Note the fine print on Floor 2: thin endpoints mostly <strong>call the manager directly</strong> and don't go through SyncServer's methods. This is counterintuitive; later we'll let the numbers speak.</p>
<p>Also remember one boundary: the DB session is opened and closed only on Floor 2 (inside the manager); <strong>Floor-1 routers never touch the database</strong>. This boundary foreshadows the later "multiple transactions" section.</p>
<p>Don't forget the request also <strong>returns the same way</strong>: the row fetched from the DB is lifted floor by floor — turned into an object by the ORM, handed back to the router by the manager, and finally serialized by the router into a JSON response. Calls go down, returns come up; only the round trip counts as finished.</p>
<p>While we're here, get oriented: lower in the diagram means closer to data and more "stateful"; higher means closer to the protocol and more "stateless". The tidiness of the three-layer architecture comes exactly from this up/down division of labor.</p>
<p>In other words, this diagram is both a "call stack" and a "trust boundary": each floor down can do more and carries more responsibility, so access control must sit at the very bottom, not the top.</p>
<div class="card analogy"><div class="tag">🏢 An everyday analogy</div>
<p>Picture the whole server as a <strong>three-story company</strong>, and you (the HTTP request) walk in the front door to get one thing done.</p>
<p>The <strong>first-floor front desk</strong> (thin routers) only does check-in: confirm who you are, collect the forms, then say "this belongs to the second floor" and pass the slip up. The desk never digs through the archives itself.</p>
<p>Only the <strong>second-floor manager</strong> (Manager) has the right to touch data. Crucially — for each file touched, the manager personally opens a door called a "<strong>transaction</strong>" and closes it once done.</p>
<p>The <strong>third-floor archive room</strong> (ORM / DB) keeps all the records, but who may see which one is decided by the gate (access control); even the manager can't overstep.</p>
<p>There's also a boss (<span class="mono">SyncServer</span>) presiding: he doesn't handle every little thing himself, stepping in only when "one task needs several managers to coordinate"; otherwise everyone goes straight to the relevant manager.</p>
<p>One point in this analogy deserves precision: the boss isn't a "must-approve-everything" bottleneck. For everyday small tasks people go straight to the manager; only the big "spans several departments" tasks need the boss to coordinate.</p>
</div>
<h2>One process, one global SyncServer</h2>
<p>The whole building stands only because of that one global <span class="mono">SyncServer</span> in the foundation. Where does it come from? The answer is a bit surprising.</p>
<p>It's a <strong>module-level global</strong> in <span class="mono">app.py::server</span>, built the moment the module is <strong>imported</strong>.</p>
<p>Interestingly, the factory <span class="mono">app.py::create_application</span> does contain a <span class="mono">SyncServer(...)</span> line, but it's <strong>commented out</strong> — the server is not built inside the factory.</p>
<p>So startup is cut into two clean phases: <strong>synchronous wiring at import time</strong> (building the server and all its managers), then <strong>asynchronous initialization at startup</strong>.</p>
<p>The second phase is what <span class="mono">app.py::lifespan</span> does: only async bootstrapping — <span class="mono">await server.init_async(...)</span> creates the default org/user and upserts the base tools into the DB.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/app.py</span><span class="ln">global server + two-phase startup (simplified)</span></div>
<pre><span class="cm"># module-level global: a SyncServer is built when this module is imported</span>
server = <span class="fn">SyncServer</span>(default_interface_factory=<span class="kw">lambda</span>: <span class="fn">interface</span>())

<span class="kw">def</span> <span class="fn">create_application</span>() -&gt; FastAPI:
    app = <span class="fn">FastAPI</span>(..., lifespan=lifespan)
    <span class="cm"># server = SyncServer(...)   # commented out in the source: server isn't built in the factory</span>
    <span class="kw">return</span> app

<span class="nb">@asynccontextmanager</span>
<span class="kw">async def</span> <span class="fn">lifespan</span>(app: FastAPI):
    <span class="cm"># startup only does async bootstrap: create default org/user, upsert base tools</span>
    <span class="kw">await</span> server.<span class="fn">init_async</span>(init_with_default_org_and_user=<span class="kw">True</span>)
    <span class="kw">yield</span>

<span class="cm"># ---- letta/server/rest_api/dependencies.py ----</span>
<span class="kw">async def</span> <span class="fn">get_letta_server</span>() -&gt; SyncServer:
    <span class="kw">from</span> letta.server.rest_api.app <span class="kw">import</span> server   <span class="cm"># lazy-import that module global</span>
    <span class="kw">return</span> server                                  <span class="cm"># not in app.state; every router gets the same one</span>
</pre></div>
<p>How do routers get this same server? Dependency injection. <span class="mono">dependencies.py::get_letta_server</span> lazy-imports that module global and returns it directly, <strong>not</strong> stuffing it into <span class="mono">app.state</span>.</p>
<p>One contrast is easy to confuse here: <span class="mono">create_application</span> builds the FastAPI <strong>application</strong> object, while <span class="mono">server</span> is that global <strong>business</strong> object — one handles routes and middleware, the other handles managers and data; the two are kept well apart.</p>
<p>Each router asks for one via <span class="mono">Depends(get_letta_server)</span>, and they all get <strong>the same instance</strong>. This is how "one process, one global server" is realized in code.</p>
<p>Why insist on building it at import time? Because then any module can <span class="mono">from app import server</span> to get the same instance — no passing it through layer after layer, and no reliance on FastAPI's <span class="mono">app.state</span>.</p>
<p>So what does <span class="mono">init_async</span> add? It does the "bootstrapping that needs <span class="mono">await</span> after the object exists": writing the default org and user, upserting a batch of base tools into the DB — all work that must hit the DB and therefore be async.</p>
<p>Separating the two phases buys something real: construction (synchronous, pure memory) and bootstrapping (asynchronous, hits the DB) each stay in their lane, the startup order is crystal clear, and tests can construct without bootstrapping.</p>
<p>One more detail: <span class="mono">init_async</span> is basically <strong>re-entrant</strong> — it creates the default org/user only if absent, and base tools go through upsert rather than insert, so running it again on restart won't mess up the data.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">Remember this two-phase shape: <strong>synchronous wiring at import + async init at startup</strong>. The former is pure object construction, touching neither network nor DB; the latter (<span class="mono">init_async</span>) does the <span class="mono">await</span>-requiring bootstrap, fitting FastAPI's <span class="mono">lifespan</span> hook exactly.</span></div>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">server/rest_api/app.py::server</span> — module-level global; the <span class="mono">SyncServer(...)</span> line in <span class="mono">create_application</span> is commented out.</p>
<p><span class="mono">app.py::lifespan</span> — only does <span class="mono">await server.init_async(init_with_default_org_and_user=...)</span>.</p>
<p><span class="mono">dependencies.py::get_letta_server</span> — lazy-imports and returns the global; <span class="mono">get_headers</span> parses the <span class="mono">user_id</span> header into <span class="mono">HeaderParams.actor_id</span>.</p>
<p><span class="mono">server.py::SyncServer</span> holds all the managers; <span class="mono">routers/v1/agents.py::retrieve_agent</span> is a typical thin endpoint.</p>
</div>
<p>So which managers actually hang under the server? <span class="mono">server.py::SyncServer.__init__</span> holds them <strong>all as attributes</strong>, wiring them up in one go.</p>
<div class="cellgroup"><div class="cg-cap"><b>Managers held under SyncServer (excerpt)</b></div><div class="cells"><span class="cell hl">agent_manager</span><span class="sep">·</span><span class="cell">message_manager</span><span class="sep">·</span><span class="cell">block_manager</span><span class="sep">·</span><span class="cell">passage_manager</span><span class="sep">·</span><span class="cell">user_manager</span><span class="sep">·</span><span class="cell">tool_manager</span><span class="sep">·</span><span class="cell">provider_manager</span><span class="sep">·</span><span class="cell">source_manager</span><span class="sep">·</span><span class="cell">step_manager</span><span class="sep">·</span><span class="cell">job_manager</span></div></div>
<p>Besides these managers, it also holds <span class="mono">self.config</span> (a <span class="mono">LettaConfig</span>) and <span class="mono">self._enabled_providers</span>. Here's an excerpt of the wiring:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/server.py</span><span class="ln">SyncServer.__init__ manager wiring (excerpt)</span></div>
<pre><span class="kw">class</span> <span class="fn">SyncServer</span>(<span class="nb">object</span>):
    <span class="st">&quot;&quot;&quot;Simple single-threaded / blocking server process&quot;&quot;&quot;</span>
    <span class="kw">def</span> <span class="fn">__init__</span>(self, ...):
        self.config = LettaConfig.<span class="fn">load</span>()
        self.organization_manager = <span class="fn">OrganizationManager</span>()
        self.user_manager = <span class="fn">UserManager</span>()
        self.tool_manager = <span class="fn">ToolManager</span>()
        self.block_manager = <span class="fn">BlockManager</span>()        <span class="cm"># or GitEnabledBlockManager</span>
        self.message_manager = <span class="fn">MessageManager</span>()
        self.passage_manager = <span class="fn">PassageManager</span>()
        self.agent_manager = <span class="fn">AgentManager</span>(block_manager=self.block_manager)  <span class="cm"># manager-to-manager composition</span>
        self.provider_manager = <span class="fn">ProviderManager</span>()
        <span class="cm"># … step / job / run / archive / source, all present</span>
        self._enabled_providers = [...]
</pre></div>
<p>Notice the <span class="mono">agent_manager</span> line: it's <span class="mono">AgentManager(block_manager=self.block_manager)</span> — managers also <strong>compose with each other</strong>, not isolated islands each minding its own business.</p>
<p>This composition isn't decoration: an agent must read and write memory blocks, so <span class="mono">agent_manager</span> keeps a hold of <span class="mono">block_manager</span> and borrows it directly when needed, instead of taking a long detour back through the server.</p>
<p>Hanging all managers on one server has a hidden benefit too: they naturally share the same DB access and configuration, so none of them connects to its own database or runs its own initialization.</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx">There's <strong>no message queue</strong> here: SyncServer holds all managers directly as <strong>plain attributes</strong>; between the layers there's no broker, no queue. A call is just one ordinary Python method call after another, passing through synchronously.</span></div>
<p>With these attributes in place, we can clear up the most common misconception: routers do <strong>not</strong> route all CRUD through SyncServer's methods.</p>
<p>The vast majority of the time, it calls the manager <strong>directly</strong> through the server object; only orchestration that must coordinate several managers calls SyncServer's own methods.</p>
<table class="t">
<tr><th>Call style</th><th>Example</th><th>When to use</th><th>Count in agents.py</th></tr>
<tr><td>Direct manager call</td><td class="mono">server.agent_manager.get_agent_by_id_async(...)</td><td>CRUD on a single manager</td><td>~131 times</td></tr>
<tr><td>SyncServer method</td><td class="mono">server.create_agent_async(...)</td><td>Orchestration across several managers</td><td>~16 times</td></tr>
</table>
<p>What do those 16 "orchestration" calls actually do? Take <span class="mono">server.py::SyncServer.create_agent_async</span>: it resolves the LLM / embedding config, transforms blocks, then delegates the real write to <span class="mono">agent_manager</span> — one action that pulls in several managers.</p>
<p>So <span class="mono">SyncServer</span> is less "the one door to the DB" and more a <strong>service locator</strong> plus <strong>cross-manager coordinator</strong>: for locating, everyone bypasses it and grabs the manager directly; only for coordinating does it step onto the field itself.</p>
<p>This also explains why <span class="mono">SyncServer</span> has few methods yet they're "heavy": each is a cross-manager orchestration facade, and anything a single manager can finish on its own never reaches it.</p>
<h2>Thin routers: four steps, then hand off</h2>
<p>Back to the first floor. Just how "thin" are the thin routers? Thin enough that a GET endpoint is usually four steps, then hands off.</p>
<div class="cellgroup"><div class="cg-cap"><b>The four steps of a thin router</b></div><div class="cells"><span class="cell hl">① Resolve actor</span><span class="sep">·</span><span class="cell">② Light parameter handling</span><span class="sep">·</span><span class="cell">③ Call manager / server</span><span class="sep">·</span><span class="cell">④ Return pydantic schema</span></div></div>
<p>Step ① resolves the actor: <span class="mono">await server.user_manager.get_actor_or_default_async(...)</span>, turning the identity in the request header into an actor object.</p>
<p>Step ② is light parameter handling — paging, filtering, and the like; for many endpoints this step is nearly empty.</p>
<p>Step ③ calls a manager or server method, handing off the real work; step ④ returns a pydantic schema, which FastAPI serializes according to <span class="mono">response_model</span>.</p>
<p>Step ④ is worth a second look: the router <span class="mono">return</span>s a pydantic object directly, <strong>hand-writing no JSON</strong>; serialization is left to FastAPI, done automatically per <span class="mono">response_model=AgentState</span>.</p>
<p>The four-step skeleton isn't unique to <span class="mono">retrieve_agent</span>: list, create, delete endpoints are almost the same skeleton — only steps ② and ③ swap in their own parameters and manager calls.</p>
<p>That's why understanding one endpoint often means understanding a whole group: get retrieve straight, and list / create / update mostly follow the same template.</p>
<p>Lay out <span class="mono">routers/v1/agents.py::retrieve_agent</span> and the four steps are obvious at a glance:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/rest_api/routers/v1/agents.py</span><span class="ln">retrieve_agent: a thin router's four steps (simplified)</span></div>
<pre><span class="nb">@router.get</span>(<span class="st">"/{agent_id}"</span>, response_model=AgentState)   <span class="cm"># ④ FastAPI serializes per response_model</span>
<span class="kw">async def</span> <span class="fn">retrieve_agent</span>(
    agent_id: str,
    server: SyncServer = <span class="fn">Depends</span>(get_letta_server),   <span class="cm"># DI: get that global server</span>
    headers: HeaderParams = <span class="fn">Depends</span>(get_headers),     <span class="cm"># parse user_id header -&gt; actor_id</span>
):
    <span class="cm"># ① resolve actor (session #1: look up user)</span>
    actor = <span class="kw">await</span> server.user_manager.<span class="fn">get_actor_or_default_async</span>(actor_id=headers.actor_id)
    <span class="cm"># ② (this endpoint has almost no params) ③ call the manager directly (session #2: with access control)</span>
    <span class="kw">return</span> <span class="kw">await</span> server.agent_manager.<span class="fn">get_agent_by_id_async</span>(agent_id=agent_id, actor=actor)
    <span class="cm"># ④ the returned pydantic object is serialized by FastAPI per response_model=AgentState</span>
</pre></div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">The actor is resolved <strong>inside the handler body</strong> (step ①), not in some global auth middleware. <span class="mono">dependencies.py::get_headers</span> only parses/validates the <span class="mono">user_id</span> header into <span class="mono">HeaderParams.actor_id</span> (checking the <span class="mono">user-&lt;uuid4&gt;</span> format, <strong>touching no DB</strong>); the actual user lookup happens only when the body <span class="mono">await</span>s <span class="mono">get_actor_or_default_async</span>.</span></div>
<p>Why make routers this thin? Because "thin" and "thick" each have their own job, and seeing them side by side is clearest.</p>
<div class="cols">
  <div class="col"><h4>🪶 Thin router (Floor 1)</h4><p>Only four steps: resolve the actor, handle params, call the manager, return a schema. <strong>No business logic, no DB session.</strong> Switch endpoints and the skeleton is almost copied over.</p></div>
  <div class="col"><h4>🧱 Thick manager (Floor 2)</h4><p>Business logic, transaction boundaries, multi-tenant isolation are all here. <strong>The DB session is opened and closed in the manager</strong>, and access control is welded into every query.</p></div>
</div>
<p>Lock in this dividing line first: <strong>routers never open a DB session</strong>; sessions are all opened and closed in the manager. It's exactly the key to the next section, "why multiple transactions".</p>
<p>One easily overlooked point to add: thin doesn't mean "doing nothing". The router still owns HTTP semantics — status codes, the response model, mapping errors to 4xx; it just pushes the <strong>business</strong> part down to the lower layer.</p>
<div class="cute"><div class="row"><span class="emoji">🚪</span><span class="lab">Doorman · router</span><span class="arrow">→</span><span class="emoji">🧑‍💼</span><span class="lab">Manager · manager</span><span class="arrow">→</span><span class="emoji">🗄️</span><span class="bubble">Archive · ORM/DB</span></div><div class="cap">🏛️ Three floors: the doorman (router) just passes the slip, the manager (manager) opens a "transaction" door to touch data, and who may read the archive (ORM/DB) is decided by the gate (access control)</div></div>
<h2>Follow one GET request all the way down</h2>
<p>Four steps alone isn't satisfying enough. Let's actually take a <span class="mono">GET /v1/agents/{id}</span> request by the hand, from the door all the way to the DB, then back the same way.</p>
<p>A small trick for reading the sequence diagram: treat each "transaction" marker as one complete "open the door — take the item — close the door". You'll count <strong>two</strong> such open/close cycles, and they don't share the same door.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>DI assembly</h4><p><span class="mono">get_letta_server</span> hands over that global server, and <span class="mono">get_headers</span> parses the <span class="mono">user_id</span> header into <span class="mono">actor_id</span> (no DB yet at this point).</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Resolve actor · transaction ①</h4><p><span class="mono">get_actor_or_default_async</span> opens session #1 to look up the user; when <span class="mono">user_id</span> is missing, OSS mode falls back to the default user.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Look up agent · transaction ②</h4><p><span class="mono">get_agent_by_id_async(actor=actor)</span> opens session #2: <span class="mono">select(AgentModel)</span> + <span class="mono">apply_access_predicate(...ORGANIZATION)</span> + <span class="mono">where(id==...)</span>.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Fetch one or 404</h4><p><span class="mono">scalar_one_or_none()</span> gets the row; if None, raise 404. Otherwise <span class="mono">to_pydantic_async()</span> converts it into a schema.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Serialize the response</h4><p>After commit / close, FastAPI serializes the object into JSON per <span class="mono">response_model=AgentState</span> and returns it.</p></div></div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">Notice steps 2 and 3: they are <strong>two independent transactions</strong>, each opening its own session and committing/closing on its own. One request = <strong>multiple independent transactions</strong>, with <strong>no</strong> request-level unit of work (UoW). The reason is that transaction boundaries are drawn inside manager methods — the drawer below has the details.</span></div>
<p>Line this trajectory up with the four steps earlier and you'll find: those thin four steps in the router actually pull in <strong>two trips to the DB, two access-control checks, and one serialization</strong>.</p>
<p>This is the essence of "thin": the complexity didn't vanish, it was just <strong>pushed down to the two lower layers</strong>. The router looks featherlight because the heavy lifting is caught firmly in the manager and the ORM.</p>
<p>The key to access control hides here too: the <span class="mono">apply_access_predicate</span> in step 3 isn't added by the router but <strong>welded in automatically</strong> by the ORM while building the SQL, so organization-level isolation can't be bypassed.</p>
<p>Look at the upward leg again: <span class="mono">to_pydantic_async()</span> <strong>detaches the ORM row from the session</strong> and turns it into a pure pydantic object, so even after the session is closed, the data in the router's hands is still complete and usable.</p>
<p>This step is crucial: it cuts apart the "database row" and the "outward schema", sealing the DB session's lifetime inside the manager so it never leaks to the router layer.</p>
<p>For exactly this reason, the router layer never gets an object that's "still attached to the database" — all it ever sees is a settled schema that's safe to serialize.</p>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p><span class="mono">SyncServer</span> is a beautiful misnomer. The class docstring still reads "Simple single-threaded / blocking server process", yet in v0.16.8 the methods routers call are almost all <span class="mono">async def</span> — the real concurrency model is <strong>cooperative async</strong> on a single event loop.</p>
<p>Better still: it isn't a "god facade" but a <strong>service locator</strong> — thin CRUD endpoints go <span class="mono">server.&lt;manager&gt;.&lt;method&gt;()</span> straight through, and <span class="mono">SyncServer</span>'s own methods appear only for cross-manager orchestration.</p>
<p>So "business hub" = <strong>cross-manager coordinator</strong>, not "the one door to the DB". Pair that reframing with "named Sync, actually async" and you have the two keys to reading this layer.</p>
</div>
<p>Keep this "misnomer" in mind and the names won't lead you astray when you read the server layer later: don't take <span class="mono">Sync</span> at face value, and don't assume server does everything itself. The name is history; the code is reality.</p>
<h2>Digging a little deeper</h2>
<p>The main thread is complete here. The four drawers below collect the details you're likely to ask about — open them as your interest dictates; leaving them closed won't hurt your grasp of the main thread.</p>
<details class="accordion"><summary>Why make routers this thin?</summary><div class="acc-body">
<p>Pulling business logic out of the router buys at least three benefits.</p>
<p><strong>Reuse</strong>: the same <span class="mono">agent_manager.get_agent_by_id_async</span> can be called by REST endpoints, internal code, and background tasks alike, with no need to write one copy each.</p>
<p><strong>Testability</strong>: testing business logic needs no HTTP — just write unit tests against the manager; the router layer is thin enough to barely need testing.</p>
<p><strong>Consistent authorization</strong>: access control is welded into the ORM layer (<span class="mono">apply_access_predicate</span>), so no matter who calls the manager, organization-level isolation still holds — rather than each endpoint writing it again and each missing a spot.</p>
<p>Think of it in reverse: if you stuffed business into the router, the same logic would be copied into REST, background tasks, and tests, sooner or later drifting into three inconsistent versions — thin routers cut off that drift at the source.</p>
</div></details>
<details class="accordion"><summary>Why is SyncServer called "Sync" yet almost all async?</summary><div class="acc-body">
<p>Pure <strong>historical naming</strong>. There really was an early vision of "synchronous, single-threaded, blocking", and the class docstring was written back then.</p>
<p>But the reality in v0.16.8 is: the methods routers call are almost all <span class="mono">async def</span>, with concurrency from cooperative async on a single event loop, not multithreading or blocking.</p>
<p>The name hasn't changed because it's long been a stable symbol at countless call sites; the payoff of renaming is far outweighed by the risk of a repo-wide change. When reading the code, just treat "Sync" as a <strong>historical label</strong>.</p>
</div></details>
<details class="accordion"><summary>Why is one request multiple transactions, not one?</summary><div class="acc-body">
<p>Because <strong>transaction boundaries are drawn inside manager methods</strong>, not at the request level.</p>
<p>Each manager method (such as looking up the user or the agent) opens its own session with <span class="mono">async with db_registry.async_session()</span> and commits/closes once done.</p>
<p>So the single <span class="mono">retrieve_agent</span> request spans <strong>two independent transactions</strong>: look up the user first, then the agent; it does not wrap the whole request in one big transaction as a "request-level UoW".</p>
<p>The cost is that the two reads aren't the same snapshot; the benefit is clear boundaries, self-consistent managers, and easier reuse and testing. Lesson 27 will fully explain where the session comes from.</p>
<p>By the way: precisely because there's no request-level big transaction, a failure in one step won't automatically roll back a write already committed in a prior step — this hands the responsibility for "compensation / idempotency" clearly back to the orchestrator (SyncServer or the caller).</p>
</div></details>
<details class="accordion"><summary>What is that optional server-password middleware?</summary><div class="acc-body">
<p>It's an <strong>orthogonal</strong>, server-wide gate, enabled only in secure mode.</p>
<p><span class="mono">middleware/check_password.py::CheckPasswordMiddleware</span> checks <span class="mono">X-BARE-PASSWORD: password &lt;pw&gt;</span> or <span class="mono">Authorization: Bearer &lt;pw&gt;</span>; health probes pass, otherwise 401.</p>
<p>It's mounted only when <span class="mono">LETTA_SERVER_SECURE=true</span> or <span class="mono">--secure</span>, uses a <strong>single shared secret</strong>, and is entirely unrelated to tenant/actor — don't confuse it with the <span class="mono">user_id</span>/actor multi-tenant identity from earlier.</p>
<p>Tell the two apart in one line: the password middleware governs "<strong>whether the whole server lets you in</strong>", while actor/user_id governs "<strong>whose data you can see once inside</strong>". One is the front-gate access, the other the room number within; neither replaces the other.</p>
</div></details>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<p>Routers do <strong>not</strong> all go through <span class="mono">SyncServer</span> methods — most are direct <span class="mono">server.&lt;manager&gt;.&lt;method&gt;()</span> calls; only cross-manager orchestration goes through SyncServer.</p>
<p><span class="mono">SyncServer</span> is named "sync" but is really "async": the docstring is a legacy remnant, and the real path is almost all <span class="mono">async</span>.</p>
<p>The actor is resolved <strong>inside the handler body</strong> (step ①), not a global auth middleware; the router layer <strong>never</strong> opens a DB session.</p>
<p>When <span class="mono">user_id</span> is missing, OSS mode falls back to the <strong>default user</strong>, rather than erroring out.</p>
<p>That global server is built at <strong>import time</strong> (<span class="mono">app.py::server</span>), <strong>not</strong> in the <span class="mono">create_application</span> factory; there's <strong>no message queue</strong> between the layers.</p>
</div>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li>One request crosses three floors: <strong>thin routers → SyncServer + Managers → ORM → DB</strong>.</li>
<li>A <strong>single global <span class="mono">SyncServer</span></strong> in the process: built at import time, <span class="mono">init_async</span> in <span class="mono">lifespan</span>; routers get the same one via <span class="mono">Depends(get_letta_server)</span>.</li>
<li>The thin router's four steps: resolve actor → handle params → call manager/server → return schema; <strong>the DB session is opened only in the manager</strong>.</li>
<li>Most are <strong>direct manager calls</strong>; only cross-manager orchestration goes through SyncServer methods (about 131 : 16 in agents.py).</li>
<li>One request = <strong>multiple independent transactions</strong>; access control is welded into every query by the ORM's <span class="mono">apply_access_predicate</span>.</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">To wrap up in one line: <strong>routers only receive, managers do the work, the ORM guards the gate, the DB persists — all strung together by one global server</strong>. This three-layer division of labor is the foundation on which every detail of Lessons 25–27 stands.</span></div>
<p>You've actually seen this "thin pattern" before: the message lifecycle of <span class="mono">agents.py::send_message</span> in Lesson 03 follows the very same "routers only receive, managers do the work".</p>
<p>And the agent loop the server brings up (<span class="mono">AgentLoop.load(...)</span> then <span class="mono">.step(...)</span> from Lessons 13 and 14) is also invoked from this layer — the server is precisely its entry point.</p>
<p>The next three lessons take apart the second and third floors one by one: Lesson 25 on how managers actually write business logic, Lesson 26 on the ORM's CRUD and multi-tenant isolation, Lesson 27 on the origins of the DB session and <span class="mono">async_session</span>. Three floors, descending one at a time.</p>
<p>After these three lessons, you'll be able to explain every step of a request, from HTTP all the way to disk, crystal clear.</p>
""",
}

LESSON_25 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">上一课我们把整栋服务端大楼竖了起来：薄路由只登记转交，ORM 守着访问控制，DB 在最底下落地。夹在中间的二楼——<span class="mono">SyncServer</span> 名下那一众 <strong>Manager</strong>——只被一句"业务枢纽"轻轻带过。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课就走进二楼，看清每位经理办事时手上那套<strong>一模一样的动作</strong>：开一道 session、按身份取数、<strong>还在 session 里</strong>把行换成 pydantic、再把复印件递出去。认得这副骨架，整层代码就读通了大半。</p>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>每个 manager 方法，都是同一条流水线</strong>。</p>
<p>先过三个装饰器：<span class="mono">@enforce_types</span> 校验类型、<span class="mono">@raise_on_invalid_id</span> 校验 id、<span class="mono">@trace_method</span> 开一个 span。</p>
<p>再 <span class="mono">async with db_registry.async_session()</span> 开一道事务门——这一行同时定了事务边界与 actor 范围。</p>
<p>门里做 actor 范围的 CRUD，访问控制（<span class="mono">apply_access_predicate</span>）由 ORM 焊进每条 SQL。</p>
<p>临走前<strong>仍在 session 内</strong>把 ORM 行 <span class="mono">to_pydantic()</span> 成纯对象，再把它返回。</p>
<p><strong>绝不把 ORM 行漏出门外</strong>——出柜台的，永远只是复印件。</p>
</div>
<p>这条流水线不是某位经理的个性，而是<strong>所有 manager 的公共形状</strong>。下面先把它画成一张解剖图，再逐段拆开。</p>
<p>也提前点破一个反直觉：名字带 <span class="mono">Sync</span> 的 <span class="mono">SyncServer</span>，名下 manager 的方法却几乎全是 <span class="mono">async def</span>——这层真正的底色是 async，第 24 课已埋过这个伏笔。</p>
<p>还要把镜头摆正：上一课站在"整栋楼"的高度看三层分工，这一课只盯<strong>二楼那一间柜台</strong>，看清一个方法从进到出的每一帧。粒度变细，规律反而更清楚。</p>
<p>一个提醒：本课所有代码都标了"简化 / 节选"。真实方法常带分页、过滤、批量等额外参数，但<strong>骨架那五步雷打不动</strong>——我们要的正是骨架，而非逐字复刻。</p>
<p>读这一课时，不妨继续用上一课的"三层楼"做底图：我们这回把镜头怼到二楼柜台前，一帧帧看经理怎么动手。</p>
<h2>一个 manager 方法，长成同一副样子</h2>
<p>先看最小的一个真实例子——查一个 organization。它把"统一形状"压到了最短：开 session、读一行、转 pydantic、返回，四步收工。</p>
<p>把这四步展开成方法解剖图，你能看到装饰器、事务、查询、转换是怎么一节接一节咬合的：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>装饰器三连</h4><p><span class="mono">@enforce_types</span> → <span class="mono">@raise_on_invalid_id</span> → <span class="mono">@trace_method</span>：方法体还没跑，类型、id、span 已经就位。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>开 session · BEGIN</h4><p><span class="mono">async with db_registry.async_session()</span>：事务从这里开始，actor/org 范围也从这里注入。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>拼查询 · 焊隔离</h4><p><span class="mono">select(Model)</span> + <span class="mono">apply_access_predicate(actor)</span> + <span class="mono">where(id==...)</span>，组织级隔离焊进 SQL。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>ORM CRUD</h4><p><span class="mono">read_async</span> / <span class="mono">create_async</span> 等方法落到 DB，拿回一行 ORM 对象。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>转 pydantic · 还在门内</h4><p><strong>仍在 session 内</strong>调 <span class="mono">to_pydantic()</span>，把 ORM 行变成一个纯粹的 pydantic 对象。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>退出 · 收尾三件套</h4><p><span class="mono">async with</span> 块结束：干净退出就 commit，再 <span class="mono">expunge_all</span> + <span class="mono">close</span>。</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>返回 schema</h4><p>交回调用方的是 pydantic，<strong>调用方再也碰不到 session</strong>，也碰不到 ORM 行。</p></div></div>
</div>
<p>七步里，真正"有业务"的其实只有第 3、4 步；其余五步——装饰器、开关 session、转换——<strong>每个 manager 方法都一样</strong>。这正是"统一形状"的含义。</p>
<p>请把第 2 步和第 6 步配成一对：<span class="mono">async with</span> 的进入与退出，就是事务的 BEGIN 与 commit。一个方法体，恰好是一道事务。</p>
<p>也盯住第 5 步那句"仍在 session 内"——它是本课最容易踩错、也最值钱的一条规矩，后面会专门用一个抽屉讲透。</p>
<p>还有一处值得点名：第 3 步的 <span class="mono">apply_access_predicate(actor)</span> 不是你手写的 <span class="mono">where</span>，而是 ORM 拼 SQL 时<strong>自动追加</strong>的一段过滤。你只管说"查 agent"，"只查我组织内的"由它补齐。</p>
<p>正因为这段过滤焊在 ORM、而 session 又只在 manager 里开，<strong>越权查询根本拼不出来</strong>：想绕过它，得先拿到 session，而 session 这层压根不对外。</p>
<p>第 4 步的 <span class="mono">read_async</span> / <span class="mono">create_async</span> 也不是各 manager 自造，而是 ORM 基类 <span class="mono">SqlalchemyBase</span> 提供的统一 CRUD 动词——这是第 26 课的主角，这里先记个名字。</p>
<p>把这七步在脑里跑一遍，你会发现它其实是个<strong>固定模板</strong>：变量只有"哪个 Model、哪个 CRUD 动词、转哪个 pydantic"，模板本身从不变。读 manager，就是在这套模板里找那几个变量。</p>
<p>顺道认一个区别：<span class="mono">get</span> 系列读完即转 pydantic，<span class="mono">create / update</span> 系列则先 <span class="mono">model_dump(to_orm=True)</span> 进门、落库、再 <span class="mono">to_pydantic</span> 出门——读路径短一截，写路径多一次反向换装。</p>
<div class="card analogy"><div class="tag">🏦 生活类比</div>
<p>把每位 manager 想成<strong>银行柜员</strong>，而你（路由）只能站在柜台外，进不了金库。</p>
<p>你报上身份，柜员替你开一笔<strong>"事务"</strong>——拉开柜台那道小门，办完即关。</p>
<p>他只按你的身份取<strong>你那一格</strong>的资料，别人的格子碰都不碰，这就是访问控制。</p>
<p>原始账本（ORM 行）<strong>始终留在柜台内</strong>，柜员递给你的，永远是一份<strong>复印件</strong>（pydantic）。</p>
<p>妙在：复印件离了柜台照样能看，而原件连同那道门，早在你转身时就一并关好了。</p>
</div>
<div class="cute"><div class="row"><span class="emoji">🏦</span><span class="lab">柜员·manager</span><span class="arrow">→</span><span class="emoji">📒</span><span class="lab">账本·ORM</span><span class="arrow">→</span><span class="emoji">🧾</span><span class="bubble">复印件·pydantic</span></div><div class="cap">🏦 柜员开一道"事务"小门，📒 原始账本（ORM 行）留在柜内，🧾 只把复印件（pydantic）递出柜台</div></div>
<p>把这张解剖图对回真实代码，最干净的样板就是 <span class="mono">organization_manager.py::OrganizationManager</span>：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/organization_manager.py</span><span class="ln">最简 manager：读与写都套同一副骨架（简化）</span></div>
<pre><span class="kw">class</span> <span class="fn">OrganizationManager</span>:
    <span class="nb">@enforce_types</span>          <span class="cm"># 同步校验入参类型</span>
    <span class="nb">@trace_method</span>          <span class="cm"># 开一个 "OrganizationManager.get_..." span</span>
    <span class="kw">async def</span> <span class="fn">get_organization_by_id_async</span>(self, org_id: str) -&gt; PydanticOrganization:
        <span class="kw">async with</span> db_registry.<span class="fn">async_session</span>() <span class="kw">as</span> session:   <span class="cm"># 唯一开 session 的地方</span>
            org = <span class="kw">await</span> OrganizationModel.<span class="fn">read_async</span>(db_session=session, identifier=org_id)
            <span class="kw">return</span> org.<span class="fn">to_pydantic</span>()                        <span class="cm"># 仍在 session 内：行 -&gt; pydantic</span>

    <span class="nb">@enforce_types</span>
    <span class="nb">@trace_method</span>
    <span class="kw">async def</span> <span class="fn">_create_organization_async</span>(self, pydantic_org: PydanticOrganization) -&gt; PydanticOrganization:
        <span class="kw">async with</span> db_registry.<span class="fn">async_session</span>() <span class="kw">as</span> session:
            org = <span class="fn">OrganizationModel</span>(**pydantic_org.<span class="fn">model_dump</span>(to_orm=<span class="kw">True</span>))  <span class="cm"># pydantic -&gt; ORM</span>
            <span class="kw">await</span> org.<span class="fn">create_async</span>(session)                  <span class="cm"># 落库</span>
            <span class="kw">return</span> org.<span class="fn">to_pydantic</span>()                        <span class="cm"># 出门即复印件</span>
</pre></div>
<p>读和写，两副身子骨一模一样：开 session → 动 ORM → <span class="mono">to_pydantic()</span> → 返回。差别只在中间——一个 <span class="mono">read_async</span>，一个 <span class="mono">create_async</span>。</p>
<p>留意写那一支的入口：<span class="mono">model_dump(to_orm=True)</span> 把 pydantic 拆成构造 ORM 用的字段字典，再喂给 <span class="mono">OrganizationModel(...)</span>。这趟是<strong>反方向</strong>换装，后面单开一节细说。</p>
<p>还有一点呼应上一课：这些 manager 全挂在那个全局 <span class="mono">SyncServer</span> 名下（第 24 课），可真正开 session、动数据的，从来是 manager 自己，而非 server。server 只负责<strong>持有</strong>与<strong>编排</strong>。</p>
<p>也顺带回答一个常见疑问：为什么不直接把 ORM 行返回路由、省掉一次转换？因为那样 DB 会话的生命周期会<strong>泄到路由层</strong>，序列化时一不留神就触发惰性加载——既危险又难测。</p>
<p>反过来也成立：正因为返回的是 pydantic，给 manager 写单测时<strong>根本不用起 HTTP</strong>——直接调方法、断言返回的 schema 即可，这正是上一课"薄路由几乎不用测"的另一面。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">organization 是租户树的<strong>根</strong>，所以它的读没有 <span class="mono">actor</span> 参数。换成 agent、message 这些<strong>租户内</strong>的对象，方法签名就会多一个 <span class="mono">actor</span>，ORM 据此把 <span class="mono">apply_access_predicate</span> 焊进查询——形状不变，只多了一道身份。</span></div>
<h2>db_registry：唯一能开 session 的接缝</h2>
<p>统一形状里最关键的一行，是 <span class="mono">async with db_registry.async_session()</span>。它凭什么"一行定两件事"——既划事务边界，又注入租户范围？答案藏在 <span class="mono">db.py</span> 里。</p>
<p>先记住一个反差极大的事实：<span class="mono">db_registry</span> 听着像个复杂的"注册表"，可它的类 docstring 只有一句自嘲——<strong>"Dummy registry to maintain the existing interface."</strong>（为维持旧接口而留的傀儡注册表）。</p>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">db.py::DatabaseRegistry</span>——进程级单例 <span class="mono">db_registry</span>；v0.16.8 只暴露 <span class="mono">async_session()</span>，没有同步 <span class="mono">session()</span>。</p>
<p><span class="mono">db.py</span> 模块级：<span class="mono">engine = create_async_engine(...)</span> + <span class="mono">async_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)</span>。</p>
<p><span class="mono">utils.py::enforce_types</span>、<span class="mono">otel/tracing.py::trace_method</span>、<span class="mono">sqlalchemy_base.py::SqlalchemyBase.to_pydantic</span>——这层的三件横切工具。</p>
</div>
<p>把 <span class="mono">async_session</span> 摊开看，它就是一个 <span class="mono">@asynccontextmanager</span>：干净退出提交、出错回滚、最后一定清场。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/db.py</span><span class="ln">DatabaseRegistry.async_session：事务边界都在这（节选）</span></div>
<pre><span class="cm"># 模块级：一个进程一个引擎 + 一个 session 工厂</span>
engine = <span class="fn">create_async_engine</span>(async_pg_uri, ...)
async_session_factory = <span class="fn">async_sessionmaker</span>(engine, expire_on_commit=<span class="kw">False</span>, autoflush=<span class="kw">False</span>)

<span class="kw">class</span> <span class="fn">DatabaseRegistry</span>:
    <span class="st">&quot;&quot;&quot;Dummy registry to maintain the existing interface.&quot;&quot;&quot;</span>

    <span class="nb">@asynccontextmanager</span>
    <span class="kw">async def</span> <span class="fn">async_session</span>(self):
        session = <span class="fn">async_session_factory</span>()
        <span class="kw">try</span>:
            <span class="kw">yield</span> session
            <span class="kw">await</span> session.<span class="fn">commit</span>()        <span class="cm"># 干净退出 -&gt; 提交</span>
        <span class="kw">except</span> BaseException:               <span class="cm"># 含 CancelledError</span>
            <span class="kw">await</span> session.<span class="fn">rollback</span>()      <span class="cm"># 出错 -&gt; 回滚</span>
            <span class="kw">raise</span>
        <span class="kw">finally</span>:
            session.<span class="fn">expunge_all</span>()         <span class="cm"># 解绑所有对象，防止行泄漏出 session</span>
            <span class="kw">await</span> session.<span class="fn">close</span>()

db_registry = <span class="fn">DatabaseRegistry</span>()           <span class="cm"># 进程级单例</span>
</pre></div>
<p>三个收尾动作各有分工：<span class="mono">commit/rollback</span> 管数据正确，<span class="mono">expunge_all</span> 管对象安全，<span class="mono">close</span> 管连接归还。每开一次 session，这套收尾都<strong>原子地</strong>跑一遍。</p>
<p>把它和上一课的时序对上：那条 GET 请求里数到的"两次开关门"，每次的 BEGIN/commit 其实都发生在这个 <span class="mono">async_session</span> 里——manager 方法只是借它开一道门。</p>
<p>顺带说一句这些 manager 怎么来的：它们不是 DI 容器注入的，而是上一课 <span class="mono">SyncServer.__init__</span> 里一行行 <span class="mono">self.x_manager = XManager()</span> 普通地 new 出来——朴素到几乎没有框架感。</p>
<p>这也呼应上一课的结论：一次请求＝<strong>多个独立事务</strong>，而非一个请求级大事务。原因正在这里——事务边界被 <span class="mono">async with</span> 划在了每个 manager 方法内部。</p>
<p>注意是 <span class="mono">except BaseException</span> 而非 <span class="mono">except Exception</span>：连 <span class="mono">CancelledError</span>（请求被取消）也要回滚——async 世界里被取消是常态，绝不能把半截事务留在库里。</p>
<p>还有 <span class="mono">expire_on_commit=False</span> 这个不起眼的参数：它让对象在 commit 后<strong>不</strong>被标记过期，于是 <span class="mono">to_pydantic()</span> 读字段时不必再跑一次 DB 往返。这是后面"为什么在 session 内转"的另一半钥匙。</p>
<p>那么，谁会来调这些 manager？答案是<strong>四类调用方，殊途同归</strong>，最后都收束到 <span class="mono">db_registry.async_session()</span> 这一道接缝上。</p>
<div class="cellgroup"><div class="cg-cap"><b>谁在调 managers（四类调用方）</b></div><div class="cells"><span class="cell hl">REST 路由</span><span class="sep">·</span><span class="cell">agent 循环</span><span class="sep">·</span><span class="cell">别的 manager</span><span class="sep">·</span><span class="cell">序列化 / 批任务</span></div></div>
<p>四路调用看似各走各的，进了二楼却都被拢成同一条窄路：</p>
<div class="flow">
  <div class="node hl"><div class="nt">任意调用方</div><div class="nd">路由 / 循环 / 别的 manager</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">manager 方法</div><div class="nd">server.&lt;manager&gt;.&lt;method&gt;</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">async_session()</div><div class="nd">唯一接缝 · 一道事务</div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">"唯一接缝"是这层最大的杠杆：路由和 agent 循环<strong>永远看不到</strong> session，也写不出 <span class="mono">WHERE organization_id</span>。隔离与事务被<strong>结构性地</strong>焊死在"唯一能开 session 的地方"，想忘都忘不掉。</span></div>
<details class="accordion"><summary>manager 这层，到底为什么要单独存在？</summary><div class="acc-body">
<p>把"开 session + 范围 CRUD + 转 pydantic"收进一层，至少买到四样东西。</p>
<p><strong>事务归属</strong>：全进程<strong>只有</strong> manager 能开 session，事务边界因此有唯一、明确的归属，不散落在路由或循环里。</p>
<p><strong>租户范围</strong>：<span class="mono">apply_access_predicate</span> 只在这层注入一次，组织级隔离绕不过去，也不必每个端点各写一遍。</p>
<p><strong>跨调用方复用</strong>：同一个方法，REST 路由能调、agent 循环能调、别的 manager 也能调；<span class="mono">AgentManager.__init__</span> 甚至直接组合 <span class="mono">BlockManager / ToolManager / MessageManager / PassageManager</span>。</p>
<p><strong>横切免费</strong>：装饰器一叠，typing、tracing、id 校验对每个方法一视同仁，不必手写。</p>
</div></details>
<h2>schema ↔ ORM：进出柜台都要换装</h2>
<p>"统一形状"里其实有两处换装：出门时 ORM 行 → pydantic，进门时 pydantic → ORM 行。两个方向用的是<strong>两个不同的入口</strong>，别记混。</p>
<p>先看出门（读）那一程。转换方法挂在 <strong>ORM 类</strong>上，而不是写在 manager 里：</p>
<div class="cols">
  <div class="col"><h4>📤 出门 · ORM → pydantic</h4><p><span class="mono">SqlalchemyBase.to_pydantic</span> ＝ <span class="mono">self.__pydantic_model__.model_validate(self, from_attributes=True)</span>。每个 ORM 模型声明自己的 <span class="mono">__pydantic_model__</span>（如 <span class="mono">orm/agent.py → PydanticAgentState</span>）。</p></div>
  <div class="col"><h4>📥 进门 · pydantic → ORM</h4><p><span class="mono">model_dump(to_orm=True)</span>（<span class="mono">schemas/letta_base.py::LettaBase.model_dump</span>）把字段拆成字典，顺手把 <span class="mono">metadata</span> 改名成 <span class="mono">metadata_</span>，再喂给 ORM 构造器。</p></div>
</div>
<p>两个方向都<strong>没有</strong> <span class="mono">to_record()</span> / <span class="mono">to_orm()</span> 这种方法——出门靠 <span class="mono">to_pydantic</span>，进门靠 <span class="mono">model_dump(to_orm=True)</span>，就这两把钥匙。</p>
<p>为什么 <span class="mono">metadata</span> 要改名？因为 SQLAlchemy 把 <span class="mono">metadata</span> 占作保留属性，ORM 列只能叫 <span class="mono">metadata_</span>；而对外 schema 仍想叫 <span class="mono">metadata</span>，于是换装时顺手对调。</p>
<p>简单模型一句 <span class="mono">to_pydantic()</span> 就够；可像 agent 这种<strong>带一堆关系</strong>的，得手工把 block、tool、source 等关系拼齐，于是它重写了 <span class="mono">to_pydantic_async</span>：</p>
<table class="t">
<tr><th>方法</th><th>挂在哪</th><th>做什么</th><th>用于</th></tr>
<tr><td class="mono">to_pydantic()</td><td>SqlalchemyBase</td><td class="mono">model_validate(from_attributes=True)</td><td>简单模型（如 organization）</td></tr>
<tr><td class="mono">to_pydantic_async()</td><td>复杂 ORM 类重写</td><td>手搭关系，可能再发查询</td><td class="mono">orm/agent.py::Agent</td></tr>
<tr><td class="mono">model_dump(to_orm=True)</td><td>LettaBase（pydantic 侧）</td><td>拆字段 + metadata→metadata_</td><td>构造 ORM 行（写路径）</td></tr>
</table>
<p>为什么 agent 要用 async 版？因为拼关系可能<strong>再发查询</strong>，而查询要 await。简单模型字段都在手上，同步 <span class="mono">to_pydantic()</span> 足矣。一句话：<strong>关系越多，转换越可能 async</strong>。</p>
<p>多说一句方向感：出门（读）几乎每个方法都要走，所以 <span class="mono">to_pydantic</span> 是高频路径；进门（写）只在 create / update 时出现，<span class="mono">model_dump(to_orm=True)</span> 因此稀疏得多。</p>
<p>把"换装"想成海关：进出柜台都要换证件，ORM 行是"内部工牌"、pydantic 是"对外护照"。两边各管一段，谁也别拿错证件出门。</p>
<p>还要留意 <span class="mono">actor</span> 是<strong>显式传参</strong>、而非从某个全局上下文里摸出来的：每个需要隔离的方法签名里都明明白白写着 <span class="mono">actor</span>，谁的身份、取谁的数据，一眼可查、也好测。</p>
<details class="accordion"><summary>为什么转换必须在 session 内完成？</summary><div class="acc-body">
<p>因为一旦出了 <span class="mono">async with</span> 块，session 已 <span class="mono">close</span>、ORM 行也被 <span class="mono">expunge_all</span> 解了绑——这时再读它的字段，多半直接 <span class="mono">DetachedInstanceError</span>。</p>
<p>有人会问：不是有 <span class="mono">expire_on_commit=False</span> 吗，对象不该过期啊？没错，已加载的字段确实还在；可一旦碰到<strong>尚未加载</strong>的关系或惰性属性，脱离 session 的对象就没法补查，照样炸。</p>
<p>所以规矩很硬：<strong>趁门还开着，把要用的都读出来、定形成 pydantic</strong>。复印件一旦成形，就和柜台、和那道门彻底无关了。</p>
<p>这也解释了 <span class="mono">get_agent_by_id_async</span> 一个"反直觉"的细节：它故意<strong>先不解密就转 pydantic、放掉 DB 连接之后</strong>，再去跑昂贵的 PBKDF2 解密——schema 边界顺手成了连接池优化。</p>
</div></details>
<h2>三个装饰器：typing、tracing、id 校验"免费"</h2>
<p>回到方法顶上那三行 <span class="mono">@</span>。它们不写在方法体里，却让每个 manager 方法都"免费"得到类型校验、链路追踪、id 校验。先看它们怎么定义、怎么叠：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/utils.py · letta/otel/tracing.py</span><span class="ln">两个装饰器 + 一个真实方法栈（简化）</span></div>
<pre><span class="cm"># letta/utils.py</span>
<span class="kw">def</span> <span class="fn">enforce_types</span>(func):
    <span class="nb">@wraps</span>(func)
    <span class="kw">def</span> <span class="fn">wrapper</span>(*args, **kwargs):            <span class="cm"># 注意：同步 def，不是 async</span>
        hints = <span class="fn">get_type_hints</span>(func)
        <span class="kw">if</span> <span class="fn">_mismatch</span>(args, kwargs, hints):     <span class="cm"># 逐个比对入参与注解</span>
            <span class="kw">raise</span> <span class="fn">ValueError</span>(...)            <span class="cm"># 校验在调用前、同步发生</span>
        <span class="kw">return</span> <span class="fn">func</span>(*args, **kwargs)          <span class="cm"># async 方法：这里得到协程，原样返回</span>
    <span class="kw">return</span> wrapper

<span class="cm"># letta/otel/tracing.py</span>
<span class="kw">def</span> <span class="fn">trace_method</span>(func):
    <span class="nb">@wraps</span>(func)
    <span class="kw">async def</span> <span class="fn">async_wrapper</span>(*args, **kwargs):
        <span class="kw">if</span> <span class="kw">not</span> _is_tracing_initialized:        <span class="cm"># 未初始化 -&gt; 纯透传（no-op）</span>
            <span class="kw">return</span> <span class="kw">await</span> <span class="fn">func</span>(*args, **kwargs)
        name = f<span class="st">&quot;{type(args[0]).__name__}.{func.__name__}&quot;</span>  <span class="cm"># "AgentManager.get_..."</span>
        <span class="kw">with</span> tracer.<span class="fn">start_as_current_span</span>(name):
            <span class="kw">return</span> <span class="kw">await</span> <span class="fn">func</span>(*args, **kwargs)   <span class="cm"># 记参时跳过 messages/embeddings 等大参</span>
    <span class="kw">return</span> async_wrapper

<span class="cm"># letta/services/agent_manager.py —— 典型装饰器栈</span>
<span class="nb">@enforce_types</span>           <span class="cm"># 最外：typing</span>
<span class="nb">@raise_on_invalid_id</span>(param_name=<span class="st">&quot;agent_id&quot;</span>, expected_prefix=...)  <span class="cm"># 中：校验前缀 id（validators.py）</span>
<span class="nb">@trace_method</span>            <span class="cm"># 最内：tracing</span>
<span class="kw">async def</span> <span class="fn">get_agent_by_id_async</span>(self, agent_id: str, actor: User) -&gt; PydanticAgentState:
    ...
</pre></div>
<p>叠放顺序很有讲究：<span class="mono">@enforce_types</span> 在最外、<span class="mono">@trace_method</span> 在最内。于是入参先被校验类型与 id，<strong>通过之后</strong>才进 span、才真正执行——脏数据根本到不了 tracing。</p>
<p>还有个隐性收益：校验、追踪、id 检查都收进装饰器后，方法体里<strong>看不到一行样板</strong>，读起来就是纯业务——开 session、查、转、返回。共性下沉，主线才清爽。</p>
<p>顺序也别记反：<span class="mono">@enforce_types</span> 最外、<span class="mono">@trace_method</span> 最内，意味着 span 只包住"已通过校验"的执行——trace 里看到的，都是干净入参跑出来的真实耗时。</p>
<p>这套装饰器也解释了为何 manager 方法读起来都"短得可疑"：真正的横切早被抽走，留在方法体里的，几乎只剩那一句 <span class="mono">async with</span> 和一两行查询。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">把这三行想成"<strong>免费横切</strong>"：每个 manager 方法都自动获得<strong>类型校验 + 链路追踪 + id 校验</strong>，作者一行都不用为它们写。这正是"统一形状"能统一的底气——共性收进装饰器，方法体只剩业务。</span></div>
<details class="accordion"><summary><span class="mono">enforce_types</span> 是同步的，怎么对 async 方法也成立？</summary><div class="acc-body">
<p>关键在于：<span class="mono">enforce_types</span> 的 <span class="mono">wrapper</span> 是个普通 <span class="mono">def</span>，<strong>不是</strong> <span class="mono">async def</span>。</p>
<p>它先<strong>同步</strong>跑完类型校验；通过后调 <span class="mono">func(*args, **kwargs)</span>。若 <span class="mono">func</span> 是 async，这一步并不执行方法体，而是返回一个<strong>协程对象</strong>。</p>
<p>wrapper 把这个协程<strong>原样 return</strong> 出去，由调用方 <span class="mono">await</span>。于是校验同步、执行异步，两不耽误。</p>
<p>反过来想：要是 wrapper 自己 <span class="mono">await</span> 了，它就得是 async，那同步方法就没法共用同一个装饰器了。同步 wrapper 是<strong>故意</strong>的最大公约数。</p>
</div></details>
<details class="accordion"><summary><span class="mono">trace_method</span> 何时是 no-op？span 又怎么命名？</summary><div class="acc-body">
<p><strong>何时 no-op</strong>：当 <span class="mono">_is_tracing_initialized</span> 为 <span class="mono">False</span>（没配 OTel 后端），<span class="mono">trace_method</span> 直接 <span class="mono">await func(...)</span>，一个 span 都不开——纯透传、零开销。</p>
<p><strong>怎么命名</strong>：开 span 时名字是 <span class="mono">"{ClassName}.{method}"</span>，如 <span class="mono">"AgentManager.get_agent_by_id_async"</span>，于是一条 trace 上能一眼认出是哪个 manager 的哪个方法。</p>
<p><strong>省什么</strong>：记录入参时会<strong>跳过</strong> <span class="mono">messages</span>、<span class="mono">embeddings</span> 这类大对象，免得把整车消息或向量塞进 span、拖垮追踪。</p>
</div></details>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>一行 <span class="mono">async with db_registry.async_session()</span> 同时定了两件事——<strong>事务从哪开始/提交</strong>，以及 <strong>actor/org 范围从哪注入</strong>（<span class="mono">apply_access_predicate</span>）。路由和 agent 循环永远看不到 session、也看不到 <span class="mono">WHERE organization_id</span>，于是隔离结构上<strong>没法被忘</strong>：它和"唯一能开 session 的地方"焊在一起。</p>
<p>再看 <span class="mono">db_registry</span> 自嘲的 docstring "Dummy registry to maintain the existing interface"——上百处 <span class="mono">async_session()</span> 调用点<strong>一字未改</strong>，底下实现却被收成一个模块级 asyncpg 引擎：<strong>接口是契约、引擎可替换</strong>。</p>
<p>第三层妙处是"转换在 session 内"竟是个<strong>性能模式</strong>：<span class="mono">get_agent_by_id_async</span> 故意"先不解密就转 pydantic、放掉 DB 连接后再跑昂贵的 PBKDF2"——schema 边界顺手成了连接池优化。</p>
</div>
<h2>为什么独立成一层（记忆层也同形）</h2>
<p>把前面几节合起来，"为什么 manager 要单独成层"就有了完整答案：<strong>事务、租户、复用、横切</strong>四件事，全靠这一层一次性焊死。</p>
<p>更有说服力的是：你早在第 08、10、11 课见过的记忆 managers，走的正是同一副骨架——<span class="mono">block / message / passage</span> 三位，方法形状和 organization 别无二致。</p>
<div class="cellgroup"><div class="cg-cap"><b>同一副骨架的 managers（节选，回扣 08 / 10 / 11 课）</b></div><div class="cells"><span class="cell hl">BlockManager</span><span class="sep">·</span><span class="cell">MessageManager</span><span class="sep">·</span><span class="cell">PassageManager</span><span class="sep">·</span><span class="cell">AgentManager</span><span class="sep">·</span><span class="cell">OrganizationManager</span></div></div>
<p>认得了一个 <span class="mono">OrganizationManager.get_..._async</span>，你其实就认得了它们全部：开 session、按 actor 取数、session 内转 pydantic、返回。换的只是模型名与那一两行业务。</p>
<p>这也是读这套代码的省力法：<strong>先吃透一个 manager，再横扫一片</strong>。block 怎么读写、message 怎么追加、passage 怎么检索，骨架都一样，差异只在各自的查询与关系。</p>
<p>这种"同形"不是巧合，而是把 <span class="mono">SqlalchemyBase</span> 当公共基类、把 <span class="mono">async_session</span> 当唯一接缝换来的<strong>必然结果</strong>：底座一样，长出来的 manager 自然一个样。</p>
<p>再往上看一眼分工：路由（第一层）只接、manager（第二层）才办、ORM（第三层）守门。这一课把第二层那间柜台拆到了零件级，下一课该轮到第三层的门禁了。</p>
<p>临走再钉一遍那条铁律：<strong>ORM 行不出柜台</strong>。无论方法多复杂、关系多缠绕，递出门的永远是 pydantic——这一条，就是整层 manager 最该带走的肌肉记忆。</p>
<p>把这条肌肉记忆和"唯一接缝、免费横切、门内换装"拼在一起，二楼这间柜台就算彻底看透了。下一课，我们推开档案室的门。</p>
<p>最后澄清一个容易想多的点：<span class="mono">db_registry</span> 既然这么"傀儡"，那 SQLite / Postgres 的差异是不是也在它这层抹平的？不是。</p>
<details class="accordion"><summary><span class="mono">db_registry</span> 的"Dummy registry"，以及 Postgres-only 的现状</summary><div class="acc-body">
<p>"Dummy registry" 的意思是：它<strong>不</strong>再做花哨的注册或选择，只为<strong>维持旧接口</strong>而留——上百处 <span class="mono">db_registry.async_session()</span> 调用点因此一字未改，底下实现却能被收成一个模块级 asyncpg 引擎。</p>
<p>v0.16.8 的 <span class="mono">db.py</span> 是 <strong>Postgres-only</strong> 的：模块级就一个 <span class="mono">create_async_engine(async_pg_uri)</span>，<strong>不</strong>在这层分 SQLite / Postgres。</p>
<p>那"方言透明"在哪？在 <strong>ORM 层</strong>：column 类型、查询 helper、<span class="mono">orm/__init__.py</span> 里注册的 <span class="mono">sqlite_functions</span> 等，才是吃方言差异的地方——这是第 27 课的主题，别记到 <span class="mono">db_registry</span> 头上。</p>
</div></details>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>名字带 <span class="mono">*_async</span> 不代表没有同步校验：<span class="mono">enforce_types</span> 的 wrapper 本就是<strong>同步</strong>的，先校验、再返回协程。</p>
<p><strong>别把 ORM 行漏出 session</strong>：尽管 <span class="mono">expire_on_commit=False</span>，可一旦出了 <span class="mono">async with</span>、被 <span class="mono">expunge_all</span>，读未加载字段就 <span class="mono">DetachedInstanceError</span>。务必在门内 <span class="mono">to_pydantic()</span>。</p>
<p>一个逻辑操作配<strong>一道</strong> session：跨多步别硬塞进一个事务，事务边界就是方法边界。</p>
<p>v0.16.8 <strong>没有</strong>同步 <span class="mono">session()</span>，只有 <span class="mono">async_session()</span>；<span class="mono">db.py</span> 是 Postgres-only，方言透明不在这层。</p>
<p>没有 <span class="mono">to_record()</span> / <span class="mono">to_orm()</span>：出门 <span class="mono">to_pydantic</span>、进门 <span class="mono">model_dump(to_orm=True)</span>，认准这两把。</p>
</div>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li>每个 manager 方法都是<strong>同一条流水线</strong>：装饰器 → <span class="mono">async with db_registry.async_session()</span> → actor 范围 CRUD → <strong>session 内</strong> <span class="mono">to_pydantic()</span> → 返回 pydantic。</li>
<li><strong>绝不返回 ORM 行</strong>：门内转好复印件，门外只见 schema；<span class="mono">expire_on_commit=False</span> + <span class="mono">expunge_all</span>，漏出去就 <span class="mono">DetachedInstanceError</span>。</li>
<li><span class="mono">db_registry.async_session()</span> 是<strong>唯一接缝</strong>：一行定事务边界 + actor/org 范围；docstring 自称 "Dummy registry"，v0.16.8 只有 async 版。</li>
<li>三装饰器<strong>免费横切</strong>：<span class="mono">enforce_types</span>(typing) / <span class="mono">raise_on_invalid_id</span>(id) / <span class="mono">trace_method</span>(tracing，未初始化即 no-op)。</li>
<li>换装两把：出门 <span class="mono">SqlalchemyBase.to_pydantic</span>，进门 <span class="mono">model_dump(to_orm=True)</span>（<span class="mono">metadata→metadata_</span>）；没有 <span class="mono">to_record / to_orm</span>。</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">一句话收束：<strong>manager 这层＝"唯一能开事务的柜台"</strong>——它开 session、按身份取数、在门内把行复印成 pydantic 递出去，事务、租户、横切全焊在这一处。</span></div>
<p>这副"统一形状"你其实早就见过：第 08、10、11 课的记忆 managers，走的就是同一套开门取数、门内转换。</p>
<p>接下来两课会钻进这条流水线的后半段：第 26 课拆 ORM 的 CRUD 与 <span class="mono">apply_access_predicate</span> 多租户隔离，第 27 课讲 DB 引擎、session 来历与方言透明。柜台之下，还有两层楼要看。</p>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Last lesson we stood the whole server building upright: thin routers only register and hand off, the ORM guards access control, and the DB lands at the very bottom. The second floor wedged in between — the crowd of <strong>Managers</strong> under <span class="mono">SyncServer</span> — got brushed past with a single phrase, "the business hub."</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson walks onto that second floor and watches the <strong>identical set of moves</strong> every manager makes: open a session, fetch data by identity, turn the row into pydantic <strong>while still inside the session</strong>, then hand the copy back out. Recognize this skeleton and you've read most of the layer already.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Grab this lesson in one line: <strong>every manager method is the same assembly line</strong>.</p>
<p>First it passes three decorators: <span class="mono">@enforce_types</span> checks types, <span class="mono">@raise_on_invalid_id</span> checks the id, <span class="mono">@trace_method</span> opens a span.</p>
<p>Then <span class="mono">async with db_registry.async_session()</span> opens a transaction door — that one line fixes both the transaction boundary and the actor scope.</p>
<p>Inside the door it does actor-scoped CRUD; access control (<span class="mono">apply_access_predicate</span>) is welded by the ORM into every SQL statement.</p>
<p>Just before leaving, <strong>still inside the session</strong>, it turns the ORM row into a plain object via <span class="mono">to_pydantic()</span>, then returns it.</p>
<p>It <strong>never lets an ORM row slip out the door</strong> — what leaves the counter is always just a copy.</p>
</div>
<p>This assembly line isn't one manager's personality — it's the <strong>shared shape of every manager</strong>. Below we first draw it as an anatomy chart, then take it apart stretch by stretch.</p>
<p>One counterintuitive point up front: despite the <span class="mono">Sync</span> in <span class="mono">SyncServer</span>, the manager methods under it are almost all <span class="mono">async def</span> — this layer's true color is async, a thread Lesson 24 already planted.</p>
<p>Let's also fix the camera: last lesson stood at building height to see the three-floor division of labor; this one stares only at <strong>that one counter on the second floor</strong>, catching every frame of a method from entry to exit. Finer grain, clearer pattern.</p>
<p>A reminder: every code block here is marked "simplified / excerpt." Real methods often carry pagination, filtering, batching and other extra parameters, but those <strong>five skeleton steps never budge</strong> — the skeleton is what we're after, not a word-for-word copy.</p>
<p>As you read, keep last lesson's <strong>three floors</strong> as the base map: this time we push the camera right up to the second-floor counter and watch, frame by frame, how the manager works.</p>
<h2>Every manager method grows the same shape</h2>
<p>Start with the smallest real example — fetching one organization. It compresses the <strong>uniform shape</strong> to its shortest: open a session, read one row, convert to pydantic, return — four steps and done.</p>
<p>Unfold those four steps into a method-anatomy chart and you can see how decorators, transaction, query, and conversion mesh segment by segment:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Three decorators in a row</h4><p><span class="mono">@enforce_types</span> → <span class="mono">@raise_on_invalid_id</span> → <span class="mono">@trace_method</span>: before the body even runs, type, id, and span are already in place.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Open session · BEGIN</h4><p><span class="mono">async with db_registry.async_session()</span>: the transaction starts here, and the actor/org scope is injected here too.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Build query · weld isolation</h4><p><span class="mono">select(Model)</span> + <span class="mono">apply_access_predicate(actor)</span> + <span class="mono">where(id==...)</span>: org-level isolation welded into the SQL.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>ORM CRUD</h4><p>Methods like <span class="mono">read_async</span> / <span class="mono">create_async</span> hit the DB and bring back one ORM object.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>To pydantic · still inside the door</h4><p><strong>Still inside the session</strong>, call <span class="mono">to_pydantic()</span> to turn the ORM row into a pure pydantic object.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Exit · the closing trio</h4><p>The <span class="mono">async with</span> block ends: a clean exit commits, then <span class="mono">expunge_all</span> + <span class="mono">close</span>.</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>Return schema</h4><p>What goes back to the caller is pydantic; the caller <strong>never touches the session</strong>, nor the ORM row.</p></div></div>
</div>
<p>Of the seven steps, only steps 3 and 4 carry real <strong>business</strong>; the other five — decorators, opening/closing the session, conversion — are <strong>identical in every manager method</strong>. That's exactly what "uniform shape" means.</p>
<p>Pair step 2 with step 6: entering and exiting the <span class="mono">async with</span> is the transaction's BEGIN and commit. One method body is exactly one transaction.</p>
<p>Watch step 5's phrase "still inside the session" too — it's the easiest rule to get wrong and the most valuable one in this lesson; a drawer later spells it out in full.</p>
<p>One more worth naming: step 3's <span class="mono">apply_access_predicate(actor)</span> isn't a <span class="mono">where</span> you hand-write — it's a filter the ORM <strong>appends automatically</strong> as it builds the SQL. You just say "query agents"; "only the ones in my org" is filled in for you.</p>
<p>Because that filter is welded into the ORM and the session is only opened inside the manager, <strong>an over-reaching query simply can't be assembled</strong>: to bypass it you'd need the session first, and that layer is never exposed.</p>
<p>Step 4's <span class="mono">read_async</span> / <span class="mono">create_async</span> aren't each manager's own invention either — they're the uniform CRUD verbs provided by the ORM base class <span class="mono">SqlalchemyBase</span>, the star of Lesson 26; just note the name for now.</p>
<p>Run the seven steps in your head and you'll find it's really a <strong>fixed template</strong>: the only variables are "which Model, which CRUD verb, which pydantic to convert to"; the template itself never changes. Reading a manager is just finding those few variables inside this template.</p>
<p>Note one distinction in passing: the <span class="mono">get</span> family reads then converts to pydantic; the <span class="mono">create / update</span> family first does <span class="mono">model_dump(to_orm=True)</span> on the way in, persists, then <span class="mono">to_pydantic</span> on the way out — the read path is a notch shorter, the write path has one extra reverse change of outfit.</p>
<div class="card analogy"><div class="tag">🏦 An everyday analogy</div>
<p>Picture each manager as a <strong>bank teller</strong>, and you (the router) can only stand outside the counter, never entering the vault.</p>
<p>You give your identity; the teller opens a <strong>"transaction"</strong> for you — slides open that little counter door, and closes it once done.</p>
<p>They fetch only <strong>your slot's</strong> records, by your identity, never touching anyone else's slot — that is access control.</p>
<p>The original ledger (the ORM row) <strong>always stays behind the counter</strong>; what the teller hands you is always a <strong>copy</strong> (pydantic).</p>
<p>The beauty: the copy is still readable away from the counter, while the original — along with that door — was already shut the moment you turned around.</p>
</div>
<div class="cute"><div class="row"><span class="emoji">🏦</span><span class="lab">Teller · manager</span><span class="arrow">→</span><span class="emoji">📒</span><span class="lab">Ledger · ORM</span><span class="arrow">→</span><span class="emoji">🧾</span><span class="bubble">Copy · pydantic</span></div><div class="cap">🏦 The teller opens a little "transaction" door, 📒 the original ledger (ORM row) stays behind the counter, 🧾 and only the copy (pydantic) is handed out</div></div>
<p>Map this anatomy chart back to real code and the cleanest template is <span class="mono">organization_manager.py::OrganizationManager</span>:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/organization_manager.py</span><span class="ln">Simplest manager: read and write share one skeleton (simplified)</span></div>
<pre><span class="kw">class</span> <span class="fn">OrganizationManager</span>:
    <span class="nb">@enforce_types</span>          <span class="cm"># sync-validate argument types</span>
    <span class="nb">@trace_method</span>          <span class="cm"># opens an "OrganizationManager.get_..." span</span>
    <span class="kw">async def</span> <span class="fn">get_organization_by_id_async</span>(self, org_id: str) -&gt; PydanticOrganization:
        <span class="kw">async with</span> db_registry.<span class="fn">async_session</span>() <span class="kw">as</span> session:   <span class="cm"># the only place a session opens</span>
            org = <span class="kw">await</span> OrganizationModel.<span class="fn">read_async</span>(db_session=session, identifier=org_id)
            <span class="kw">return</span> org.<span class="fn">to_pydantic</span>()                        <span class="cm"># still inside the session: row -&gt; pydantic</span>

    <span class="nb">@enforce_types</span>
    <span class="nb">@trace_method</span>
    <span class="kw">async def</span> <span class="fn">_create_organization_async</span>(self, pydantic_org: PydanticOrganization) -&gt; PydanticOrganization:
        <span class="kw">async with</span> db_registry.<span class="fn">async_session</span>() <span class="kw">as</span> session:
            org = <span class="fn">OrganizationModel</span>(**pydantic_org.<span class="fn">model_dump</span>(to_orm=<span class="kw">True</span>))  <span class="cm"># pydantic -&gt; ORM</span>
            <span class="kw">await</span> org.<span class="fn">create_async</span>(session)                  <span class="cm"># persist</span>
            <span class="kw">return</span> org.<span class="fn">to_pydantic</span>()                        <span class="cm"># a copy on the way out</span>
</pre></div>
<p>Read and write have the <strong>identical frame</strong>: open session → touch ORM → <span class="mono">to_pydantic()</span> → return. The only difference is in the middle — one <span class="mono">read_async</span>, one <span class="mono">create_async</span>.</p>
<p>Note the entry on the write branch: <span class="mono">model_dump(to_orm=True)</span> breaks the pydantic into a dict of fields for constructing the ORM, then feeds it to <span class="mono">OrganizationModel(...)</span>. This is the <strong>reverse</strong> change of outfit; a later section covers it in detail.</p>
<p>One more echo of last lesson: these managers all hang under that global <span class="mono">SyncServer</span> (Lesson 24), yet what actually opens the session and touches data is always the manager itself, not the server. The server only <strong>holds</strong> and <strong>orchestrates</strong>.</p>
<p>It also answers a common question: why not just return the ORM row to the router and skip a conversion? Because then the DB session's lifecycle <strong>leaks into the router layer</strong>, and serialization can trip lazy loading without warning — both dangerous and hard to test.</p>
<p>The reverse holds too: because what's returned is pydantic, unit-testing a manager needs <strong>no HTTP at all</strong> — just call the method and assert on the returned schema, the flip side of last lesson's "thin routers barely need testing."</p>
<div class="note info"><span class="ni">💡</span><span class="nx">An organization is the <strong>root</strong> of the tenant tree, so its read takes no <span class="mono">actor</span> parameter. Switch to tenant-scoped objects like agent or message and the signature gains an <span class="mono">actor</span>, on which the ORM welds <span class="mono">apply_access_predicate</span> into the query — same shape, just one extra identity.</span></div>
<h2>db_registry: the only seam that can open a session</h2>
<p>The most pivotal line in the uniform shape is <span class="mono">async with db_registry.async_session()</span>. How does it <strong>fix two things in one line</strong> — drawing the transaction boundary and injecting the tenant scope? The answer hides in <span class="mono">db.py</span>.</p>
<p>First, a fact with stark contrast: <span class="mono">db_registry</span> sounds like a complex "registry," yet its class docstring is one self-deprecating line — <strong>"Dummy registry to maintain the existing interface."</strong></p>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">db.py::DatabaseRegistry</span> — the process-wide singleton <span class="mono">db_registry</span>; v0.16.8 exposes only <span class="mono">async_session()</span>, no sync <span class="mono">session()</span>.</p>
<p><span class="mono">db.py</span> module level: <span class="mono">engine = create_async_engine(...)</span> + <span class="mono">async_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)</span>.</p>
<p><span class="mono">utils.py::enforce_types</span>, <span class="mono">otel/tracing.py::trace_method</span>, <span class="mono">sqlalchemy_base.py::SqlalchemyBase.to_pydantic</span> — this layer's three cross-cutting tools.</p>
</div>
<p>Spread <span class="mono">async_session</span> open and it's just an <span class="mono">@asynccontextmanager</span>: commit on a clean exit, roll back on error, and always clear the field at the end.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/db.py</span><span class="ln">DatabaseRegistry.async_session: the transaction boundary lives here (excerpt)</span></div>
<pre><span class="cm"># module level: one engine + one session factory per process</span>
engine = <span class="fn">create_async_engine</span>(async_pg_uri, ...)
async_session_factory = <span class="fn">async_sessionmaker</span>(engine, expire_on_commit=<span class="kw">False</span>, autoflush=<span class="kw">False</span>)

<span class="kw">class</span> <span class="fn">DatabaseRegistry</span>:
    <span class="st">&quot;&quot;&quot;Dummy registry to maintain the existing interface.&quot;&quot;&quot;</span>

    <span class="nb">@asynccontextmanager</span>
    <span class="kw">async def</span> <span class="fn">async_session</span>(self):
        session = <span class="fn">async_session_factory</span>()
        <span class="kw">try</span>:
            <span class="kw">yield</span> session
            <span class="kw">await</span> session.<span class="fn">commit</span>()        <span class="cm"># clean exit -&gt; commit</span>
        <span class="kw">except</span> BaseException:               <span class="cm"># includes CancelledError</span>
            <span class="kw">await</span> session.<span class="fn">rollback</span>()      <span class="cm"># error -&gt; roll back</span>
            <span class="kw">raise</span>
        <span class="kw">finally</span>:
            session.<span class="fn">expunge_all</span>()         <span class="cm"># detach all objects, so no row leaks out of the session</span>
            <span class="kw">await</span> session.<span class="fn">close</span>()

db_registry = <span class="fn">DatabaseRegistry</span>()           <span class="cm"># process-wide singleton</span>
</pre></div>
<p>The three closing actions each have a job: <span class="mono">commit/rollback</span> keeps the data correct, <span class="mono">expunge_all</span> keeps the objects safe, <span class="mono">close</span> returns the connection. Every time a session opens, this closing set runs <strong>atomically</strong> once.</p>
<p>Line it up with last lesson's sequence: the "two door open/closes" counted in that GET request — each BEGIN/commit actually happens inside this <span class="mono">async_session</span>; the manager method merely borrows it to open a door.</p>
<p>A word on where these managers come from: they aren't injected by a DI container — they're plainly newed up line by line in last lesson's <span class="mono">SyncServer.__init__</span> as <span class="mono">self.x_manager = XManager()</span> — so plain there's hardly a framework feel.</p>
<p>This echoes last lesson's conclusion too: one request = <strong>several independent transactions</strong>, not one request-wide mega-transaction. Here's why — the transaction boundary is drawn by <span class="mono">async with</span> inside each manager method.</p>
<p>Note it's <span class="mono">except BaseException</span>, not <span class="mono">except Exception</span>: even <span class="mono">CancelledError</span> (a cancelled request) must roll back — cancellation is routine in the async world, and a half-finished transaction must never be left in the database.</p>
<p>And the inconspicuous <span class="mono">expire_on_commit=False</span>: it keeps objects from being marked stale after commit, so <span class="mono">to_pydantic()</span> reading fields needn't make another DB round trip. That's the other half of the key to "why convert inside the session" later.</p>
<p>So who calls these managers? The answer: <strong>four kinds of callers, all converging</strong>, finally narrowing to that one seam, <span class="mono">db_registry.async_session()</span>.</p>
<div class="cellgroup"><div class="cg-cap"><b>Who calls the managers (four kinds of callers)</b></div><div class="cells"><span class="cell hl">REST routers</span><span class="sep">·</span><span class="cell">agent loop</span><span class="sep">·</span><span class="cell">other managers</span><span class="sep">·</span><span class="cell">serialization / batch jobs</span></div></div>
<p>The four call paths look like they each go their own way, but on the second floor they're gathered onto the same narrow road:</p>
<div class="flow">
  <div class="node hl"><div class="nt">Any caller</div><div class="nd">router / loop / another manager</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">manager method</div><div class="nd">server.&lt;manager&gt;.&lt;method&gt;</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">async_session()</div><div class="nd">the only seam · one transaction</div></div>
</div>
<div class="note tip"><span class="ni">🧠</span><span class="nx">The "only seam" is this layer's biggest lever: routers and the agent loop <strong>never see</strong> a session, and can't write a <span class="mono">WHERE organization_id</span>. Isolation and transactions are <strong>structurally</strong> welded to "the only place a session can open" — impossible to forget.</span></div>
<details class="accordion"><summary>Why does the manager layer need to exist at all?</summary><div class="acc-body">
<p>Folding "open session + scoped CRUD + convert to pydantic" into one layer buys at least four things.</p>
<p><strong>Transaction ownership</strong>: in the whole process only a manager can open a session, so the transaction boundary has a single, clear owner, not scattered across routers or loops.</p>
<p><strong>Tenant scope</strong>: <span class="mono">apply_access_predicate</span> is injected just once in this layer, so org-level isolation can't be bypassed and needn't be re-written at every endpoint.</p>
<p><strong>Reuse across callers</strong>: the same method can be called by a REST router, the agent loop, or another manager; <span class="mono">AgentManager.__init__</span> even composes <span class="mono">BlockManager / ToolManager / MessageManager / PassageManager</span> directly.</p>
<p><strong>Cross-cutting for free</strong>: stack the decorators and typing, tracing, and id checking apply to every method alike, no hand-writing needed.</p>
</div></details>
<h2>schema ↔ ORM: a change of outfit in both directions</h2>
<p>The uniform shape actually has two changes of outfit: on the way out, ORM row → pydantic; on the way in, pydantic → ORM row. The two directions use <strong>two different entry points</strong> — don't mix them up.</p>
<p>Take the outbound (read) leg first. The conversion method hangs on the <strong>ORM class</strong>, not written inside the manager:</p>
<div class="cols">
  <div class="col"><h4>📤 Outbound · ORM → pydantic</h4><p><span class="mono">SqlalchemyBase.to_pydantic</span> = <span class="mono">self.__pydantic_model__.model_validate(self, from_attributes=True)</span>. Each ORM model declares its own <span class="mono">__pydantic_model__</span> (e.g. <span class="mono">orm/agent.py → PydanticAgentState</span>).</p></div>
  <div class="col"><h4>📥 Inbound · pydantic → ORM</h4><p><span class="mono">model_dump(to_orm=True)</span> (<span class="mono">schemas/letta_base.py::LettaBase.model_dump</span>) breaks the fields into a dict, renames <span class="mono">metadata</span> to <span class="mono">metadata_</span> along the way, then feeds the ORM constructor.</p></div>
</div>
<p>Neither direction has a <span class="mono">to_record()</span> / <span class="mono">to_orm()</span> method — outbound relies on <span class="mono">to_pydantic</span>, inbound on <span class="mono">model_dump(to_orm=True)</span>; just these two keys.</p>
<p>Why rename <span class="mono">metadata</span>? Because SQLAlchemy reserves <span class="mono">metadata</span> as a reserved attribute, so the ORM column can only be <span class="mono">metadata_</span>; the outward schema still wants <span class="mono">metadata</span>, so the change of outfit swaps them in passing.</p>
<p>For simple models one <span class="mono">to_pydantic()</span> is enough; but something like agent, which carries <strong>a pile of relationships</strong>, must hand-assemble the block, tool, source relations, so it overrides <span class="mono">to_pydantic_async</span>:</p>
<table class="t">
<tr><th>Method</th><th>Hangs on</th><th>What it does</th><th>Used for</th></tr>
<tr><td class="mono">to_pydantic()</td><td>SqlalchemyBase</td><td class="mono">model_validate(from_attributes=True)</td><td>simple models (e.g. organization)</td></tr>
<tr><td class="mono">to_pydantic_async()</td><td>overridden by complex ORM classes</td><td>assembles relations by hand, may issue more queries</td><td class="mono">orm/agent.py::Agent</td></tr>
<tr><td class="mono">model_dump(to_orm=True)</td><td>LettaBase (pydantic side)</td><td>split fields + metadata→metadata_</td><td>construct ORM rows (write path)</td></tr>
</table>
<p>Why does agent use the async version? Because assembling relations may issue more queries, and queries need <span class="mono">await</span>. A simple model has all its fields in hand, so a sync <span class="mono">to_pydantic()</span> suffices. In one line: <strong>the more relations, the more likely the conversion is async</strong>.</p>
<p>A word on direction: the outbound (read) leg runs in nearly every method, so <span class="mono">to_pydantic</span> is a high-frequency path; the inbound (write) leg shows up only on create / update, so <span class="mono">model_dump(to_orm=True)</span> is far sparser.</p>
<p>Think of the "change of outfit" as customs: crossing the counter in either direction means swapping papers — the ORM row is an "internal badge," pydantic an "outward passport." Each governs its own stretch; don't leave with the wrong papers.</p>
<p>Note too that <span class="mono">actor</span> is <strong>passed explicitly</strong>, not fished out of some global context: every method that needs isolation spells <span class="mono">actor</span> right in its signature — whose identity, whose data, plain to see and easy to test.</p>
<details class="accordion"><summary>Why must the conversion finish inside the session?</summary><div class="acc-body">
<p>Because once you leave the <span class="mono">async with</span> block, the session is already <span class="mono">close</span>d and the ORM row detached by <span class="mono">expunge_all</span> — read its fields now and you'll likely hit a <span class="mono">DetachedInstanceError</span> outright.</p>
<p>Someone will ask: isn't there <span class="mono">expire_on_commit=False</span>, so the object shouldn't expire? True, already-loaded fields are still there; but the moment you touch an <strong>unloaded</strong> relationship or lazy attribute, an object cut off from its session can't re-query, and it blows up all the same.</p>
<p>So the rule is hard: <strong>while the door is still open, read out everything you need and set it into pydantic</strong>. Once the copy is formed, it's wholly independent of the counter and that door.</p>
<p>This also explains a "counterintuitive" detail in <span class="mono">get_agent_by_id_async</span>: it deliberately converts to pydantic <strong>before decrypting and after releasing the DB connection</strong>, then runs the expensive PBKDF2 decryption — the schema boundary doubles as a connection-pool optimization.</p>
</div></details>
<h2>Three decorators: typing, tracing, id checking "for free"</h2>
<p>Back to those three <span class="mono">@</span> lines atop the method. They live outside the body yet hand every manager method type checking, tracing, and id checking "for free." First, how they're defined and stacked:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/utils.py · letta/otel/tracing.py</span><span class="ln">Two decorators + one real method stack (simplified)</span></div>
<pre><span class="cm"># letta/utils.py</span>
<span class="kw">def</span> <span class="fn">enforce_types</span>(func):
    <span class="nb">@wraps</span>(func)
    <span class="kw">def</span> <span class="fn">wrapper</span>(*args, **kwargs):            <span class="cm"># note: sync def, not async</span>
        hints = <span class="fn">get_type_hints</span>(func)
        <span class="kw">if</span> <span class="fn">_mismatch</span>(args, kwargs, hints):     <span class="cm"># compare each arg against its annotation</span>
            <span class="kw">raise</span> <span class="fn">ValueError</span>(...)            <span class="cm"># validation happens before the call, synchronously</span>
        <span class="kw">return</span> <span class="fn">func</span>(*args, **kwargs)          <span class="cm"># async method: this yields a coroutine, returned as-is</span>
    <span class="kw">return</span> wrapper

<span class="cm"># letta/otel/tracing.py</span>
<span class="kw">def</span> <span class="fn">trace_method</span>(func):
    <span class="nb">@wraps</span>(func)
    <span class="kw">async def</span> <span class="fn">async_wrapper</span>(*args, **kwargs):
        <span class="kw">if</span> <span class="kw">not</span> _is_tracing_initialized:        <span class="cm"># not initialized -&gt; pure pass-through (no-op)</span>
            <span class="kw">return</span> <span class="kw">await</span> <span class="fn">func</span>(*args, **kwargs)
        name = f<span class="st">&quot;{type(args[0]).__name__}.{func.__name__}&quot;</span>  <span class="cm"># "AgentManager.get_..."</span>
        <span class="kw">with</span> tracer.<span class="fn">start_as_current_span</span>(name):
            <span class="kw">return</span> <span class="kw">await</span> <span class="fn">func</span>(*args, **kwargs)   <span class="cm"># skips big args like messages/embeddings when recording</span>
    <span class="kw">return</span> async_wrapper

<span class="cm"># letta/services/agent_manager.py — a typical decorator stack</span>
<span class="nb">@enforce_types</span>           <span class="cm"># outermost: typing</span>
<span class="nb">@raise_on_invalid_id</span>(param_name=<span class="st">&quot;agent_id&quot;</span>, expected_prefix=...)  <span class="cm"># middle: validate prefixed id (validators.py)</span>
<span class="nb">@trace_method</span>            <span class="cm"># innermost: tracing</span>
<span class="kw">async def</span> <span class="fn">get_agent_by_id_async</span>(self, agent_id: str, actor: User) -&gt; PydanticAgentState:
    ...
</pre></div>
<p>The stacking order is deliberate: <span class="mono">@enforce_types</span> outermost, <span class="mono">@trace_method</span> innermost. So arguments are checked for type and id first, and only <strong>after passing</strong> do they enter the span and actually run — dirty data never reaches tracing.</p>
<p>There's a hidden gain too: with validation, tracing, and id checking folded into decorators, the body shows <strong>not a line of boilerplate</strong> and reads as pure business — open session, query, convert, return. Push the commonality down and the main line stays clean.</p>
<p>Don't flip the order in memory: <span class="mono">@enforce_types</span> outermost, <span class="mono">@trace_method</span> innermost means the span wraps only the <strong>already-validated</strong> execution — what you see in a trace is the real timing of a run on clean arguments.</p>
<p>These decorators also explain why manager methods read "suspiciously short": the real cross-cutting was extracted long ago, and what's left in the body is little more than that one <span class="mono">async with</span> and a query line or two.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">Think of these three lines as <strong>free cross-cutting</strong>: every manager method automatically gets type checking + tracing + id checking, and the author writes not a single line for them. That's the backbone of why the "uniform shape" can be uniform — commonality folds into decorators, the body keeps only business.</span></div>
<details class="accordion"><summary><span class="mono">enforce_types</span> is sync — how does it hold for async methods?</summary><div class="acc-body">
<p>The key: <span class="mono">enforce_types</span>'s <span class="mono">wrapper</span> is an ordinary <span class="mono">def</span>, <strong>not</strong> an <span class="mono">async def</span>.</p>
<p>It first runs type checking <strong>synchronously</strong>; on passing it calls <span class="mono">func(*args, **kwargs)</span>. If <span class="mono">func</span> is async, this step doesn't run the body — it returns a <strong>coroutine object</strong>.</p>
<p>The wrapper <strong>returns that coroutine as-is</strong>, for the caller to <span class="mono">await</span>. So validation is sync and execution is async — neither holds up the other.</p>
<p>Flip it around: if the wrapper <span class="mono">await</span>ed itself, it would have to be async, and then sync methods couldn't share the same decorator. A sync wrapper is the <strong>deliberate</strong> greatest common divisor.</p>
</div></details>
<details class="accordion"><summary>When is <span class="mono">trace_method</span> a no-op? And how is the span named?</summary><div class="acc-body">
<p><strong>When no-op</strong>: when <span class="mono">_is_tracing_initialized</span> is <span class="mono">False</span> (no OTel backend configured), <span class="mono">trace_method</span> just <span class="mono">await func(...)</span> and opens not a single span — pure pass-through, zero overhead.</p>
<p><strong>How named</strong>: a span is named <span class="mono">"{ClassName}.{method}"</span>, like <span class="mono">"AgentManager.get_agent_by_id_async"</span>, so on a trace you can spot at a glance which method of which manager it is.</p>
<p><strong>What it spares</strong>: when recording arguments it <strong>skips</strong> big objects like <span class="mono">messages</span> and <span class="mono">embeddings</span>, lest a whole truckload of messages or vectors be stuffed into the span and drag tracing down.</p>
</div></details>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>One line of <span class="mono">async with db_registry.async_session()</span> fixes two things at once — where the transaction starts/commits, and where the actor/org scope is injected (<span class="mono">apply_access_predicate</span>). Routers and the agent loop never see a session, nor a <span class="mono">WHERE organization_id</span>, so isolation is <strong>structurally impossible to forget</strong>: it's welded to "the only place a session can open."</p>
<p>Look again at <span class="mono">db_registry</span>'s self-deprecating docstring "Dummy registry to maintain the existing interface" — hundreds of <span class="mono">async_session()</span> call sites went unchanged by a single character, while the implementation underneath was folded into a module-level asyncpg engine: <strong>the interface is the contract, the engine is swappable</strong>.</p>
<p>A third bit of cleverness: "convert inside the session" turns out to be a <strong>performance pattern</strong> — <span class="mono">get_agent_by_id_async</span> deliberately "converts to pydantic before decrypting, then runs the expensive PBKDF2 after releasing the DB connection" — the schema boundary doubles as a connection-pool optimization.</p>
</div>
<h2>Why it stands as its own layer (memory managers share the shape)</h2>
<p>Put the previous sections together and "why managers form their own layer" has a complete answer: <strong>transaction, tenant, reuse, cross-cutting</strong> — all four are welded down once by this single layer.</p>
<p>More convincing still: the memory managers you met back in Lessons 08, 10, and 11 walk the very same skeleton — <span class="mono">block / message / passage</span>, their method shape no different from organization's.</p>
<div class="cellgroup"><div class="cg-cap"><b>Managers sharing one skeleton (excerpt, callback to Lessons 08 / 10 / 11)</b></div><div class="cells"><span class="cell hl">BlockManager</span><span class="sep">·</span><span class="cell">MessageManager</span><span class="sep">·</span><span class="cell">PassageManager</span><span class="sep">·</span><span class="cell">AgentManager</span><span class="sep">·</span><span class="cell">OrganizationManager</span></div></div>
<p>Recognize one <span class="mono">OrganizationManager.get_..._async</span> and you've really recognized them all: open session, fetch by actor, convert to pydantic inside the session, return. All that changes is the model name and that line or two of business.</p>
<p>This is also the labor-saving way to read this code: <strong>master one manager, then sweep across</strong>. How block reads and writes, how message appends, how passage retrieves — the skeleton is the same; the differences are only in each one's queries and relations.</p>
<p>This "same shape" is no coincidence but the <strong>inevitable result</strong> of taking <span class="mono">SqlalchemyBase</span> as the common base class and <span class="mono">async_session</span> as the only seam: same foundation, so the managers that grow from it naturally look alike.</p>
<p>One more glance at the division of labor: the router (floor 1) only takes it in, the manager (floor 2) does the work, the ORM (floor 3) guards the gate. This lesson took apart floor 2's counter down to the parts; next lesson it's floor 3's gate's turn.</p>
<p>On the way out, nail the iron rule once more: <strong>an ORM row never leaves the counter</strong>. However complex the method, however tangled the relations, what's handed out is always pydantic — that one rule is the muscle memory to carry away from this whole manager layer.</p>
<p>Put that muscle memory together with "the only seam, free cross-cutting, change of outfit inside the door" and the second-floor counter is fully seen through. Next lesson, we push open the archive-room door.</p>
<p>Finally, clear up a point easy to over-think: since <span class="mono">db_registry</span> is so "dummy," is the SQLite / Postgres difference also smoothed over in this layer? No.</p>
<details class="accordion"><summary><span class="mono">db_registry</span>'s "Dummy registry," and the Postgres-only reality</summary><div class="acc-body">
<p><strong>"Dummy registry"</strong> means it no longer does any fancy registration or selection — it stays only to <strong>maintain the existing interface</strong>, so hundreds of <span class="mono">db_registry.async_session()</span> call sites went unchanged by a single character, while the implementation underneath could be folded into a module-level asyncpg engine.</p>
<p>v0.16.8's <span class="mono">db.py</span> is <strong>Postgres-only</strong>: at module level there's just one <span class="mono">create_async_engine(async_pg_uri)</span>, with no SQLite / Postgres split in this layer.</p>
<p>So where's the "dialect transparency"? In the <strong>ORM layer</strong>: column types, query helpers, the <span class="mono">sqlite_functions</span> registered in <span class="mono">orm/__init__.py</span> — those are where dialect differences are absorbed; that's Lesson 27's topic, don't pin it on <span class="mono">db_registry</span>.</p>
</div></details>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<p>An <span class="mono">*_async</span> name doesn't mean there's no sync validation: <span class="mono">enforce_types</span>'s wrapper is sync by nature — validate first, then return the coroutine.</p>
<p><strong>Don't let an ORM row slip out of the session</strong>: despite <span class="mono">expire_on_commit=False</span>, once you leave the <span class="mono">async with</span> and get <span class="mono">expunge_all</span>'d, reading an unloaded field gives a <span class="mono">DetachedInstanceError</span>. Always <span class="mono">to_pydantic()</span> inside the door.</p>
<p>One logical operation per session: don't cram many steps into one transaction — the transaction boundary is the method boundary.</p>
<p>v0.16.8 has no sync <span class="mono">session()</span>, only <span class="mono">async_session()</span>; <span class="mono">db.py</span> is Postgres-only, and dialect transparency isn't in this layer.</p>
<p>There's no <span class="mono">to_record()</span> / <span class="mono">to_orm()</span>: outbound <span class="mono">to_pydantic</span>, inbound <span class="mono">model_dump(to_orm=True)</span> — fix on these two.</p>
</div>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li>Every manager method is the <strong>same assembly line</strong>: decorators → <span class="mono">async with db_registry.async_session()</span> → actor-scoped CRUD → <span class="mono">to_pydantic()</span> <strong>inside the session</strong> → return pydantic.</li>
<li><strong>Never return an ORM row</strong>: form the copy inside the door, only schema outside; with <span class="mono">expire_on_commit=False</span> + <span class="mono">expunge_all</span>, a leak means <span class="mono">DetachedInstanceError</span>.</li>
<li><span class="mono">db_registry.async_session()</span> is the <strong>only seam</strong>: one line fixes the transaction boundary + actor/org scope; the docstring calls itself "Dummy registry," and v0.16.8 has only the async version.</li>
<li>Three decorators, <strong>free cross-cutting</strong>: <span class="mono">enforce_types</span> (typing) / <span class="mono">raise_on_invalid_id</span> (id) / <span class="mono">trace_method</span> (tracing, a no-op when uninitialized).</li>
<li>Two keys for the change of outfit: outbound <span class="mono">SqlalchemyBase.to_pydantic</span>, inbound <span class="mono">model_dump(to_orm=True)</span> (<span class="mono">metadata→metadata_</span>); there's no <span class="mono">to_record / to_orm</span>.</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">To wrap in one line: the manager layer = <strong>"the only counter that can open a transaction"</strong> — it opens a session, fetches by identity, copies the row into pydantic inside the door and hands it out; transaction, tenant, and cross-cutting are all welded right here.</span></div>
<p>You've actually seen this "uniform shape" long ago: the memory managers in Lessons 08, 10, and 11 walk the same open-the-door-and-fetch, convert-inside-the-door routine.</p>
<p>The next two lessons drill into the back half of this assembly line: Lesson 26 takes apart the ORM's CRUD and <span class="mono">apply_access_predicate</span> multi-tenant isolation, Lesson 27 covers the DB engine, where the session comes from, and dialect transparency. Below the counter, two more floors remain to see.</p>
""",
}
