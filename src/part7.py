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
<p>把这副<strong>公共骨架</strong>展开成方法解剖图（organization 是其中最精简的一个实例），你能看到装饰器、事务、查询、转换是怎么一节接一节咬合的：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>装饰器三连</h4><p><span class="mono">@enforce_types</span> → <span class="mono">@raise_on_invalid_id</span> → <span class="mono">@trace_method</span>：方法体还没跑，类型、id、span 已经就位。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>开 session · BEGIN</h4><p><span class="mono">async with db_registry.async_session()</span>：事务从这里开始，actor/org 范围也从这里注入。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>拼查询 · 焊隔离</h4><p><span class="mono">select(Model)</span> + <span class="mono">apply_access_predicate(actor)</span> + <span class="mono">where(id==...)</span>，组织级隔离焊进 SQL。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>ORM CRUD</h4><p><span class="mono">read_async</span> / <span class="mono">create_async</span> 等方法落到 DB，拿回一行 ORM 对象。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>转 pydantic · 还在门内</h4><p><strong>仍在 session 内</strong>调 <span class="mono">to_pydantic()</span>，把 ORM 行变成一个纯粹的 pydantic 对象。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>退出 · 收尾三件套</h4><p><span class="mono">async with</span> 块结束：干净退出就 commit，再 <span class="mono">expunge_all</span> + <span class="mono">close</span>。</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>返回 schema</h4><p>交回调用方的是 pydantic，<strong>调用方再也碰不到 session</strong>，也碰不到 ORM 行。</p></div></div>
</div>
<p>七步里，真正"有业务"的其实只有第 3、4 步；其余几步——装饰器、开关 session、转换——<strong>每个 manager 方法都一样</strong>。这正是"统一形状"的含义。</p>
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
<div class="note info"><span class="ni">💡</span><span class="nx">organization 是租户树的<strong>根</strong>，所以它的读既没有 <span class="mono">actor</span> 参数、也省掉 id 前缀校验——只挂 <span class="mono">@enforce_types</span> + <span class="mono">@trace_method</span> 两个装饰器。换成 agent、message 这些<strong>租户内</strong>的对象，签名多一个 <span class="mono">actor</span>、装饰器栈也补上 <span class="mono">@raise_on_invalid_id</span>，ORM 据此把 <span class="mono">apply_access_predicate</span> 焊进查询——形状不变，只多了一道身份、一道校验。</span></div>
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
        <span class="kw">with</span> tracer.<span class="fn">start_as_current_span</span>(name) <span class="kw">as</span> span:
            <span class="fn">_record_args</span>(span, args, kwargs)        <span class="cm"># 记参时跳过 messages/embeddings 等大参</span>
            <span class="kw">return</span> <span class="kw">await</span> <span class="fn">func</span>(*args, **kwargs)
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
<p>一行 <span class="mono">async with db_registry.async_session()</span> 同时定死<strong>事务边界</strong>与 <strong>actor/org 范围</strong>。这焊接为什么是结构性的？因为 <span class="mono">AsyncSession</span> 这个类型<strong>从不出现</strong>在任何路由或循环的签名里——拿不到它，就无从绕过隔离、也无从手开事务。隔离不是"记得加"，而是"想碰都碰不到"。</p>
<p>它自嘲为 "Dummy registry"，却恰是设计的胜利：当底层从"每上下文一个引擎"重构成<strong>一个模块级 asyncpg 引擎</strong>，上百处 <span class="mono">async_session()</span> 调用点一行没动。能这样<strong>无痛换心脏</strong>，全靠把"怎么拿连接"藏在这一道接缝后面。</p>
<p>最反直觉的一笔：把"转 pydantic"放进 session 内，不只为躲 <span class="mono">DetachedInstanceError</span>，更是一步<strong>性能棋</strong>——<span class="mono">get_agent_by_id_async</span> 先转换、立刻放掉 DB 连接，再去跑昂贵的 PBKDF2 解密。谁先谁后，决定了连接被占用多久。</p>
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
<p>Unfold this <strong>shared skeleton</strong> into a method-anatomy chart (organization is its leanest instance) and you can see how decorators, transaction, query, and conversion mesh segment by segment:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Three decorators in a row</h4><p><span class="mono">@enforce_types</span> → <span class="mono">@raise_on_invalid_id</span> → <span class="mono">@trace_method</span>: before the body even runs, type, id, and span are already in place.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Open session · BEGIN</h4><p><span class="mono">async with db_registry.async_session()</span>: the transaction starts here, and the actor/org scope is injected here too.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Build query · weld isolation</h4><p><span class="mono">select(Model)</span> + <span class="mono">apply_access_predicate(actor)</span> + <span class="mono">where(id==...)</span>: org-level isolation welded into the SQL.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>ORM CRUD</h4><p>Methods like <span class="mono">read_async</span> / <span class="mono">create_async</span> hit the DB and bring back one ORM object.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>To pydantic · still inside the door</h4><p><strong>Still inside the session</strong>, call <span class="mono">to_pydantic()</span> to turn the ORM row into a pure pydantic object.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Exit · the closing trio</h4><p>The <span class="mono">async with</span> block ends: a clean exit commits, then <span class="mono">expunge_all</span> + <span class="mono">close</span>.</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>Return schema</h4><p>What goes back to the caller is pydantic; the caller <strong>never touches the session</strong>, nor the ORM row.</p></div></div>
</div>
<p>Of the seven steps, only steps 3 and 4 carry real <strong>business</strong>; the other steps — decorators, opening/closing the session, conversion — are <strong>identical in every manager method</strong>. That's exactly what "uniform shape" means.</p>
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
<div class="note info"><span class="ni">💡</span><span class="nx">An organization is the <strong>root</strong> of the tenant tree, so its read takes no <span class="mono">actor</span> parameter and skips the id-prefix check — carrying only <span class="mono">@enforce_types</span> + <span class="mono">@trace_method</span>. Switch to tenant-scoped objects like agent or message and the signature gains an <span class="mono">actor</span> while the stack also picks up <span class="mono">@raise_on_invalid_id</span>, on which the ORM welds <span class="mono">apply_access_predicate</span> into the query — same shape, just one extra identity and one extra check.</span></div>
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
<p>A word on where these managers come from: they aren't injected by a DI container — they're plainly newed up line by line in last lesson's <span class="mono">SyncServer.__init__</span> as <span class="mono">self.x_manager = XManager()</span> — so bare it barely feels like a framework.</p>
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
        <span class="kw">with</span> tracer.<span class="fn">start_as_current_span</span>(name) <span class="kw">as</span> span:
            <span class="fn">_record_args</span>(span, args, kwargs)        <span class="cm"># skips big args like messages/embeddings when recording</span>
            <span class="kw">return</span> <span class="kw">await</span> <span class="fn">func</span>(*args, **kwargs)
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
<p>One line of <span class="mono">async with db_registry.async_session()</span> pins down both the <strong>transaction boundary</strong> and the <strong>actor/org scope</strong> at once. Why is that welding structural? Because the type <span class="mono">AsyncSession</span> <strong>never appears</strong> in any router or loop signature — you can't get a handle on it, so you can't bypass isolation or hand-open a transaction. Isolation isn't "remember to add it"; it's "you can't even reach it."</p>
<p>It calls itself a "Dummy registry", yet that's the design win: when the layer underneath was refactored from "one engine per context" into <strong>a single module-level asyncpg engine</strong>, hundreds of <span class="mono">async_session()</span> call sites didn't move a character. Swapping the heart out <strong>painlessly</strong> works only because "how to get a connection" hides behind this one seam.</p>
<p>The most counter-intuitive stroke: putting "convert to pydantic" inside the session isn't only to dodge <span class="mono">DetachedInstanceError</span> — it's a <strong>performance move</strong>. <span class="mono">get_agent_by_id_async</span> converts first, releases the DB connection immediately, then runs the expensive PBKDF2 decryption. Which comes first decides how long the connection is held.</p>
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
<p>An <span class="mono">*_async</span> name doesn't mean there's no sync validation: <span class="mono">enforce_types</span>'s wrapper is <strong>sync by nature</strong> — validate first, then return the coroutine.</p>
<p><strong>Don't let an ORM row slip out of the session</strong>: despite <span class="mono">expire_on_commit=False</span>, once you leave the <span class="mono">async with</span> and get <span class="mono">expunge_all</span>'d, reading an unloaded field gives a <span class="mono">DetachedInstanceError</span>. Always <span class="mono">to_pydantic()</span> inside the door.</p>
<p><strong>One logical operation per session</strong>: don't cram many steps into one transaction — the transaction boundary is the method boundary.</p>
<p>v0.16.8 has <strong>no</strong> sync <span class="mono">session()</span>, only <span class="mono">async_session()</span>; <span class="mono">db.py</span> is Postgres-only, and dialect transparency isn't in this layer.</p>
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

LESSON_26 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">上一课我们站在二楼柜台前，看清了每个 manager 方法那副"开门取数、门内换装"的统一形状。其中第 3 步那句 <span class="mono">apply_access_predicate</span> 把租户隔离"焊进每条 SQL"，当时只被一笔带过。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课推开三楼档案室的门，看清那道门禁到底怎么运作：约 40 个模型共用一个 <span class="mono">SqlalchemyBase</span>，一套泛型 async CRUD，把"只看你那一格"焊在最低层。<strong>secure by default</strong>——不是"记得加"，而是想漏都难。</p>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>每条查询，默认就只看得到"你这租户、还没删"的行</strong>。</p>
<p>读路（<span class="mono">read / list / size</span>）只要传了 <span class="mono">actor</span>，门禁自动追加一句 <span class="mono">WHERE organization_id == actor.org</span>。</p>
<p>写路（<span class="mono">create / update</span>）顺手盖上审计字段：谁建的、谁最后改的、何时。</p>
<p>"删"默认是<strong>软删</strong>：<span class="mono">delete_async</span> 只把 <span class="mono">is_deleted</span> 翻成 <span class="mono">True</span>，行还躺在库里。</p>
<p>这套东西全长在一个抽象基类 <span class="mono">SqlalchemyBase</span> 上，约 40 个模型继承即得，无需各写一遍。</p>
</div>
<p>这不是某个模型的个性，而是<strong>所有模型的公共底座</strong>。下面先把"secure by default"画成一张总流程，再逐段拆开。</p>
<p>也先点破一处反直觉：<span class="mono">actor</span> 缺席时，这道门禁<strong>不硬失败</strong>，而是打一条响亮的 <span class="mono">SECURITY</span> 警告、无范围地照跑——为什么这么设计，本课后半专门讲。</p>
<p>再把镜头摆正：第 24 课看"整栋三层楼"，第 25 课看"二楼柜台"，这一课只盯<strong>三楼那道门禁</strong>——一条查询从拼装到落库，每一步加了什么过滤。</p>
<p>也提醒一句粒度：本课所有代码都标了"简化 / 节选"。真实方法常带分页、过滤、批量等额外参数，但"焊隔离、盖审计、软删"这三处骨架雷打不动——我们要的正是骨架。</p>
<p>还有个词先说清：本课的"租户"＝organization（org）。一个 org 下可以有多个 user，他们默认共享同一批行；真正按 user 私有的对象极少，下文会一一点名。</p>
<h2>一条查询的安检流水线（secure by default）</h2>
<p>把"默认安全"摊开成一条流水线，你会看到：身份在<strong>最外层</strong>被认出来，隔离在<strong>最里层</strong>被焊进 SQL，中间几棒只负责把 <span class="mono">actor</span> 老实串下去。</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>口令中间件（可选）</h4><p><span class="mono">CheckPasswordMiddleware</span>：整服务器级的一道闸，<span class="mono">--secure</span> 模式才挂；与租户正交。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>get_headers · 认身份</h4><p>从 <span class="mono">user_id</span> header 取值，校验形如 <span class="mono">user-&lt;uuid4&gt;</span>；只校验格式，<strong>不碰 DB</strong>。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>解析 actor</h4><p><span class="mono">get_actor_or_default_async</span>：查到 → <span class="mono">User</span>（带 org）；<span class="mono">no_default_actor</span> 且无 id → 拒。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>manager 串 actor</h4><p>路由把 <span class="mono">actor</span> 一路串进 manager 方法——"串 actor"是阻力最小的写法。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>进泛型 CRUD</h4><p><span class="mono">&lt;crud&gt;_async(actor=...)</span>：落到 <span class="mono">SqlalchemyBase</span> 那套统一动词。</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>焊隔离</h4><p><span class="mono">apply_access_predicate</span> 自动追加 <span class="mono">WHERE org==actor.org</span>；<span class="mono">read_async</span> 再单独按 <span class="mono">check_is_deleted</span> 补 <span class="mono">is_deleted==False</span>。</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>只剩你那一格</h4><p>SQL 落库，回来的只有<strong>这租户、未删</strong>的行；越权的行根本没进结果集。</p></div></div>
</div>
<p>七步里，真正"决定你看到谁"的是第 6 步那句自动追加的 <span class="mono">WHERE</span>；前五步都在做同一件事——把"你是谁"安全地送到门禁面前。</p>
<p>注意第 1 步打了括号：服务器口令是整服务器级的闸，<strong>与租户隔离正交</strong>——口令管"能不能进这台服务器"，<span class="mono">actor</span> 管"进来后看得到哪一格"。这层正交后面单讲。</p>
<p>也盯住第 6 步括号里那半句：<span class="mono">is_deleted==False</span> 只有在 <span class="mono">check_is_deleted</span> 为真时才追加——换句话说，<strong>软删行默认仍会被读回来</strong>。这条最反直觉，软删那节细说。</p>
<div class="card analogy"><div class="tag">🏦 生活类比</div>
<p>把整个数据库想成一座<strong>带门禁的共享档案库</strong>，你（调用方）报上工牌（<span class="mono">actor</span>）才能进。</p>
<p>每次开柜，门禁自动只让你看你们<strong>部门（org）</strong>那一格；别的部门的柜子，你连看都看不到。</p>
<p>"删"不是真烧掉，而是给文件贴一张<strong>"作废"贴纸</strong>（软删）——原件还在架上，需要时还能撕掉贴纸恢复。</p>
<p>每次取放，库管都自动替你盖一个<strong>"谁、何时"</strong>的章（审计），不必你开口。</p>
<p>妙在：这些规矩不写在每张借阅单上，而是焊死在<strong>门禁本身</strong>——换一百个借阅人，规矩一字不改。</p>
</div>
<div class="cute"><div class="row"><span class="emoji">🔐</span><span class="lab">门禁·每查必套</span><span class="arrow">→</span><span class="emoji">🏷️</span><span class="lab">作废贴纸·软删</span><span class="arrow">→</span><span class="emoji">🧾</span><span class="bubble">谁/何时·审计</span></div><div class="cap">🔐 门禁自动盖在每条查询上（只放行你这格），🏷️ "作废"贴纸＝软删（原件留架、可恢复），🧾 每次取放自动盖"谁/何时"的章（审计）</div></div>
<p>这张萌图里的三件事——隔离、软删、审计——其实<strong>全长在同一个抽象类上</strong>。接下来三节，就按这个顺序逐一拆开。</p>
<h2>SqlalchemyBase：一套动词，约 40 个模型共用</h2>
<p>先认清这套 CRUD 的"面"有多大：它不是某个 manager 的私有方法，而是 ORM 抽象基类 <span class="mono">SqlalchemyBase</span>（<span class="mono">__abstract__</span>）上的一组 async 类方法，约 40 个模型继承即得。</p>
<p>这套动词分三类：<strong>读、写、删</strong>。读路才有访问控制，写路负责盖审计，删又分软删与硬删。先用一张表把全貌摆出来：</p>
<table class="t">
<tr><th>方法</th><th>类型</th><th>访问控制？</th><th>软删感知？</th></tr>
<tr><td class="mono">read_async</td><td>读</td><td>有 <span class="mono">actor</span> 才套（org 级）</td><td>仅当 <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">list_async</td><td>读</td><td>有 <span class="mono">actor</span> 才套</td><td>仅当 <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">read_multiple_async</td><td>读</td><td>有 <span class="mono">actor</span> 才套</td><td>仅当 <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">size_async</td><td>读</td><td>有 <span class="mono">actor</span> 才套</td><td>仅当 <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">create_async</td><td>写</td><td>骑在读建立的边界上</td><td>盖审计字段</td></tr>
<tr><td class="mono">update_async</td><td>写</td><td>骑在读建立的边界上</td><td>盖审计字段</td></tr>
<tr><td class="mono">delete_async</td><td>软删</td><td>有 <span class="mono">actor</span> 则盖审计</td><td>翻 <span class="mono">is_deleted=True</span></td></tr>
<tr><td class="mono">hard_delete_async</td><td>物理删</td><td><span class="mono">actor</span> 仅日志</td><td>整行消失</td></tr>
<tr><td class="mono">bulk_hard_delete_async</td><td>批量物理删</td><td><strong>SQL 层套 predicate</strong></td><td>整行消失</td></tr>
</table>
<p>看这张表，记住两条主线。其一：访问控制只在<strong>读路</strong>生效（且"有 <span class="mono">actor</span> 才走"）；写、删并不各自再套一遍 <span class="mono">WHERE</span>，而是骑在读时已建立的边界上。</p>
<p>其二：唯一在"删"这侧也强制租户的，是 <span class="mono">bulk_hard_delete_async</span>——它在 SQL 层把 predicate 套进 <span class="mono">DELETE</span>。这是个重要例外，软删那节再说。</p>
<p>还有个细节值得记：读路四个方法都收同一组参数——<span class="mono">actor</span>、<span class="mono">access=["read"]</span>、<span class="mono">access_type=ORGANIZATION</span>、<span class="mono">check_is_deleted=False</span>。参数一致，行为就一致。</p>
<p>为什么值得做成"泛型"？因为这套动词对每个模型几乎一字不差。若让约 40 个模型各写一遍 read / create，隔离与审计就有约 40 处可能写歪；收进基类，等于把"对的写法"只维护一份。</p>
<p>这也是读这层代码的省力法：认准 <span class="mono">SqlalchemyBase</span> 上的动词，再看具体模型，你只需关心它<strong>覆盖了哪一个</strong>——比如 agent 这种带关系的会重写读路，多数模型则原样继承。</p>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">orm/sqlalchemy_base.py::SqlalchemyBase</span>——抽象基类，<span class="mono">read_async</span> / <span class="mono">list_async</span> / <span class="mono">create_async</span> / <span class="mono">delete_async</span> / <span class="mono">apply_access_predicate</span> 都在这。</p>
<p><span class="mono">SqlalchemyBase.apply_access_predicate</span> + <span class="mono">AccessType(str, Enum){ORGANIZATION, USER}</span>——行级过滤的注入点与两种范围。</p>
<p><span class="mono">orm/base.py::CommonSqlalchemyMetaMixins</span>——审计四件套 + 软删标记 <span class="mono">is_deleted</span>；<span class="mono">orm/mixins.py::OrganizationMixin / UserMixin</span> 提供 <span class="mono">organization_id / user_id</span> 列。</p>
<p><span class="mono">services/user_manager.py::UserManager.get_actor_or_default_async</span>——把 header 里的 id 解析成 <span class="mono">PydanticUser</span>（带 org）。</p>
</div>
<h2>apply_access_predicate：把隔离焊进每次读</h2>
<p>表看完了，现在钻进那句"自动追加的 <span class="mono">WHERE</span>"。它就一个类方法，短得出奇，却是整套多租户隔离的<strong>全部秘密</strong>。</p>
<p>先看它本体。注意第一行 <span class="mono">del access</span>：<span class="mono">read / write / admin</span> 三种 access <strong>目前是 no-op</strong>，纯占位，给将来的行级权限留座。</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/sqlalchemy_base.py</span><span class="ln">apply_access_predicate：隔离的全部秘密（简化）</span></div>
<pre><span class="nb">@classmethod</span>
<span class="kw">def</span> <span class="fn">apply_access_predicate</span>(cls, query, actor, access, access_type=AccessType.ORGANIZATION):
    <span class="kw">del</span> access                      <span class="cm"># read/write/admin 目前是 no-op：将来行级权限的占位</span>
    <span class="kw">if</span> access_type == AccessType.ORGANIZATION:
        <span class="kw">return</span> query.<span class="fn">where</span>(cls.organization_id == actor.organization_id)  <span class="cm"># 同 org 共享</span>
    <span class="kw">elif</span> access_type == AccessType.USER:
        <span class="kw">return</span> query.<span class="fn">where</span>(cls.user_id == actor.id)                  <span class="cm"># 仅 jobs / runs 用</span>
    <span class="kw">raise</span> <span class="fn">ValueError</span>(...)             <span class="cm"># actor 没有 org/id accessor＝配置错</span>
</pre></div>
<p>两个分支，对应两种范围。<span class="mono">ORGANIZATION</span> 是默认：按 <span class="mono">actor.organization_id</span> 限定，同 org 的所有用户<strong>共享</strong>同一批行（Block、Passage、Agent、Tool… 都走这条）。</p>
<p><span class="mono">USER</span> 范围<strong>只有 jobs / runs</strong> 两类用：按 <span class="mono">actor.id</span> 限定，做成用户私有。<span class="mono">organization_id</span> 与 <span class="mono">user_id</span> 这两列，分别由 <span class="mono">OrganizationMixin</span>、<span class="mono">UserMixin</span> 混进模型。</p>
<p>唯一会抛 <span class="mono">ValueError</span> 的，是 actor 连 org/id 这种 accessor 都没有——那是<strong>配置错</strong>，而非越权。越权长什么样？下面 <span class="mono">read_async</span> 里见分晓。</p>
<p>也别小看这短短两行的覆盖面：Block、Passage、Agent、Tool 等都带 <span class="mono">OrganizationMixin</span>，它们的每次读都从这<strong>同一个分支</strong>穿过。你第 08、10、11 课读过的记忆隔离，底层就是这里这一句 <span class="mono">where</span>。</p>
<p>再点一个易混：predicate 按 <span class="mono">actor.organization_id</span> 过滤，而<strong>不是</strong>按 <span class="mono">actor.id</span>——所以同一个 org 下换个 user，看到的行完全一样。真正按用户私有的，只有 jobs / runs 两类。</p>
<p>光有 predicate 还不够，得看它在 <span class="mono">read_async</span> 里被"谁、何时"调。把读路骨架展开，统共四步：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/sqlalchemy_base.py</span><span class="ln">read_async：拼查询 → 焊隔离 → 可选过滤软删 → 取一行（简化）</span></div>
<pre><span class="nb">@classmethod</span>
<span class="kw">async def</span> <span class="fn">read_async</span>(cls, db_session, identifier=<span class="kw">None</span>, actor=<span class="kw">None</span>,
                     access=[<span class="st">&quot;read&quot;</span>], access_type=AccessType.ORGANIZATION,
                     check_is_deleted=<span class="kw">False</span>, **kwargs):
    query = <span class="fn">select</span>(cls).<span class="fn">where</span>(cls.id == identifier)
    <span class="kw">if</span> actor:                                <span class="cm"># 有身份 -&gt; 焊 org/user 隔离</span>
        query = cls.<span class="fn">apply_access_predicate</span>(query, actor, access, access_type)
    <span class="kw">elif</span> <span class="fn">is_org_scoped</span>(cls):                 <span class="cm"># 无 actor 但本是 org 级：不拦，只响亮警告</span>
        logger.<span class="fn">warning</span>(<span class="st">&quot;SECURITY: ... without actor ... bypasses organization filtering&quot;</span>)
    <span class="kw">if</span> check_is_deleted:                      <span class="cm"># opt-in：默认不过滤软删</span>
        query = query.<span class="fn">where</span>(cls.is_deleted == <span class="kw">False</span>)
    row = (<span class="kw">await</span> db_session.<span class="fn">execute</span>(query)).<span class="fn">scalar_one_or_none</span>()
    <span class="kw">if</span> row <span class="kw">is</span> <span class="kw">None</span>:
        <span class="kw">raise</span> <span class="fn">NoResultFound</span>(...)            <span class="cm"># 越权的行＝查不到，而非报错</span>
    <span class="kw">return</span> row
</pre></div>
<p>四步看透：先 <span class="mono">select(cls).where(id)</span>，再据 <span class="mono">actor</span> 焊隔离（或在缺 actor 时记 <span class="mono">SECURITY</span> 警告），可选地过滤软删，最后 <span class="mono">scalar_one_or_none</span> 取一行。</p>
<p><span class="mono">read_multiple_async</span> 共用同一套预处理（<span class="mono">_read_multiple_preprocess</span>）：照样拼 query、套 predicate、按需过滤软删，只是把 <span class="mono">where(id==)</span> 换成 <span class="mono">where(id.in_(...))</span>。换汤不换药。</p>
<p>现在回答"越权长什么样"：跨租户的那行，被第 2 步的 <span class="mono">WHERE</span> 直接排除在结果集之外。于是 <span class="mono">read_async</span> 拿到 <span class="mono">None</span> → 抛 <span class="mono">NoResultFound</span>；<span class="mono">list_async</span> 则返回 <span class="mono">[]</span>。</p>
<div class="flow">
  <div class="node hl"><div class="nt">越权的行</div><div class="nd">别的 org 的数据</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">被 WHERE 排除</div><div class="nd">predicate 自动追加</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">scalar_one_or_none()</div><div class="nd">＝ None</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">NoResultFound / []</div><div class="nd">查不到，非 403</div></div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">越权不报 403、而是"查不到"，这是<strong>有意为之</strong>：它不向调用方泄露"那行存在、但你无权"的信息——连<strong>存在性</strong>本身都被隔离了。这也意味着调试时别被 <span class="mono">NoResultFound</span> 骗了，先确认 <span class="mono">actor</span> 的 org 对不对。</span></div>
<details class="accordion"><summary><span class="mono">apply_access_predicate</span> 到底注了什么？那三个 access 又去哪了？</summary><div class="acc-body">
<p>注的就是<strong>一句行级 <span class="mono">WHERE</span></strong>，仅此而已：<span class="mono">ORGANIZATION</span> → <span class="mono">where(organization_id == actor.organization_id)</span>，<span class="mono">USER</span> → <span class="mono">where(user_id == actor.id)</span>。</p>
<p>它"注"在 query 对象上，发生在 SQL <strong>真正执行之前</strong>，所以隔离在 DB 侧完成——不是把全表拉回来再在 Python 里筛。</p>
<p>违规＝查不到，而非报错：被排除的行根本不进结果集，<span class="mono">read</span> 得 <span class="mono">None</span>→<span class="mono">NoResultFound</span>，<span class="mono">list</span> 得 <span class="mono">[]</span>。唯一的 <span class="mono">ValueError</span> 来自 actor 配置错（没有 org/id accessor）。</p>
<p>那三个 <span class="mono">access</span>（read/write/admin）呢？开头 <span class="mono">del access</span> 把它丢了——<strong>目前纯 no-op</strong>，是给将来行级权限预留的形参，现在传什么都不影响结果。</p>
</div></details>
<h2>软删 vs 硬删：删除是可逆的</h2>
<p>第三件长在这个基类上的事：<strong>可恢复性</strong>。"删"在这里不是一个动作，而是三个，差别很大。先把三种删并排看清：</p>
<div class="cols">
  <div class="col"><h4>🏷️ delete_async · 软删</h4><p>只把 <span class="mono">is_deleted</span> 翻成 <span class="mono">True</span>（内部走 <span class="mono">update_async</span>，有 actor 则顺手盖审计）。行留库、可恢复；读路<strong>默认仍能看见</strong>它。</p></div>
  <div class="col"><h4>🔥 hard_delete_async · 物理删</h4><p><span class="mono">session.delete(self)</span>，整行从库里消失，带死锁重试；<span class="mono">actor</span> 在这里<strong>只用于日志</strong>，不参与隔离。</p></div>
  <div class="col"><h4>🧹 bulk_hard_delete_async · 批量物理删</h4><p><span class="mono">delete(cls).where(id.in_(...))</span> <span class="mono">+ apply_access_predicate</span>——<strong>唯一</strong>在 SQL 层强制租户的删。</p></div>
</div>
<p>三者里只有 <span class="mono">bulk_hard_delete_async</span> 在删除时也套了 predicate；其余两种删，安全边界都<strong>"骑"在它们之前那次读上</strong>：你得先 <span class="mono">read_async</span> 拿到这行（已被隔离），才删得了它。</p>
<p>默认走软删。实战里 <span class="mono">services/provider_manager.py</span> 删 provider 时调软删，读 / 列时再带 <span class="mono">check_is_deleted=True</span> 把软删行挡掉——删与读两侧，过滤是<strong>分开 opt-in</strong> 的。</p>
<p>这就解释了那条最反直觉的默认：读路 <span class="mono">check_is_deleted</span> 默认 <span class="mono">False</span>，<strong>软删行默认仍被返回</strong>。想让它"看起来真的删了"，读时得显式传 <span class="mono">check_is_deleted=True</span>。</p>
<p>软删买到的，是一份"后悔药"：误删能恢复、历史能回溯、级联清理能慢慢来。代价则是读路要<strong>时时记得过滤</strong>，否则"已删"的行会悄悄混进结果——这正是上面那条坑的来源。</p>
<p>还有个工程上的好处：软删让"删除"变成一次普通的 <span class="mono">update</span>，省去了级联外键的即时清理；真要回收空间，再用 <span class="mono">hard_delete</span> 系列择机物理删。读写路径因此都更简单。</p>
<details class="accordion"><summary>软删为什么"还在库里"？什么时候才过滤掉？</summary><div class="acc-body">
<p>软删只翻一个布尔位 <span class="mono">is_deleted=True</span>，行的字节一个没动，外键、关联照旧——所以<strong>历史、审计、恢复</strong>都还在手上。</p>
<p>过滤是<strong>读侧的 opt-in</strong>：<span class="mono">read / list</span> 默认 <span class="mono">check_is_deleted=False</span>，不追加 <span class="mono">is_deleted==False</span>，于是软删行照样查得到。</p>
<p>想挡掉软删行，调用方得显式传 <span class="mono">check_is_deleted=True</span>（如 <span class="mono">provider_manager</span> 的读路）。一处删、一处读，各自决定要不要看见"已作废"。</p>
<p>为什么不默认过滤？因为不少内部场景（审计、回溯、级联清理）正需要看到软删行；把过滤交给调用方，比一刀切更灵活。</p>
</div></details>
<h2>审计字段：每行天生能回答"谁、何时"</h2>
<p>同一个基类还顺手给每行几个"出生证明"字段（外加我们已熟的 <span class="mono">is_deleted</span>），让任何一行都能回答<strong>"谁建的、谁最后动的、何时"</strong>。</p>
<div class="cellgroup"><div class="cg-cap"><b>审计四件套 + <span class="mono">is_deleted</span>（<span class="mono">base.py::CommonSqlalchemyMetaMixins</span>）</b></div><div class="cells"><span class="cell hl">created_at</span><span class="sep">·</span><span class="cell">updated_at</span><span class="sep">·</span><span class="cell">_created_by_id</span><span class="sep">·</span><span class="cell">_last_updated_by_id</span><span class="sep">·</span><span class="cell">is_deleted</span></div></div>
<p><span class="mono">created_at</span> / <span class="mono">updated_at</span> 由 <strong>DB 侧默认值</strong>盖：<span class="mono">created_at</span> 用 <span class="mono">server_default=func.now()</span>，<span class="mono">updated_at</span> 再加 <span class="mono">server_onupdate</span>，每次写自动刷新。</p>
<p>两个 <span class="mono">*_by_id</span> 才是"谁"：注意<strong>物理列名带下划线</strong>——<span class="mono">_created_by_id</span>、<span class="mono">_last_updated_by_id</span>；对外属性去掉下划线，setter 还断言 id 前缀＝<span class="mono">"user"</span>。</p>
<p><span class="mono">created_by_id</span> 只在<strong>首次写</strong>时设、此后不变；<span class="mono">last_updated_by_id</span> 每次写都更新。于是一行的"出身"与"最近经手人"分得清清楚楚。</p>
<p>把审计和隔离摆在一起看更有意思：隔离决定"谁<strong>能看到</strong>这行"，审计记录"谁<strong>动过</strong>这行"。同一个 actor，一边当过滤条件、一边当签名落款——身份在这层被用到了两次。</p>
<p>时间字段交给 DB 默认值还有一层好处：<span class="mono">created_at</span> / <span class="mono">updated_at</span> 由 <span class="mono">server_default</span> / <span class="mono">server_onupdate</span> 在库侧生成，不依赖应用时钟，多实例并发写也不会各记各的。</p>
<details class="accordion"><summary>审计字段是怎么盖上去的？为什么列名带下划线？</summary><div class="acc-body">
<p>不是 SQLAlchemy 的事件监听，而是 CRUD 里<strong>显式调</strong> <span class="mono">_set_created_and_updated_by_fields(actor_id)</span> 盖的——create / update 路径上手动点一下。</p>
<p>关键前提：<strong>只有传了 actor 才盖</strong>。没 actor 的写（少见的系统内部路径）就不落"谁"，只有 DB 侧的时间默认值照常生效。</p>
<p>物理列叫 <span class="mono">_created_by_id</span> / <span class="mono">_last_updated_by_id</span>（带下划线），是为了和对外属性解耦：属性 setter 会断言传入 id 以 <span class="mono">"user"</span> 开头，挡住乱填。</p>
<p><span class="mono">created_by_id</span> 首次设定后不再变，<span class="mono">last_updated_by_id</span> 每次写刷新——一个记"谁生的"，一个记"谁最后碰的"。</p>
</div></details>
<h2>actor 从哪来：secure by default 的入口</h2>
<p>隔离的全部前提，是那个 <span class="mono">actor</span>。它从哪来？答案朴素得意外：一个 <strong>HTTP header</strong>。</p>
<p><span class="mono">rest_api/dependencies.py::get_headers</span> 用 <span class="mono">Header(None, alias="user_id")</span> 取 <span class="mono">user_id</span> 头，校验它形如 <span class="mono">user-&lt;uuid4&gt;</span>——<strong>只校格式，不碰 DB</strong>。</p>
<p>真正把这个 id 换成 <span class="mono">User</span> 的，是 <span class="mono">get_actor_or_default_async</span>：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/user_manager.py</span><span class="ln">get_actor_or_default_async：把 header 里的 id 解析成 actor（简化）</span></div>
<pre><span class="kw">async def</span> <span class="fn">get_actor_or_default_async</span>(self, actor_id=<span class="kw">None</span>):
    <span class="kw">if</span> settings.no_default_actor <span class="kw">and</span> actor_id <span class="kw">is</span> <span class="kw">None</span>:
        <span class="kw">raise</span> <span class="fn">NoResultFound</span>(...)               <span class="cm"># 安全模式：必须显式带身份</span>
    actor_id = actor_id <span class="kw">or</span> DEFAULT_USER_ID     <span class="cm"># 否则回退到默认 user</span>
    <span class="kw">try</span>:
        <span class="kw">return</span> <span class="kw">await</span> self.<span class="fn">get_actor_by_id_async</span>(actor_id)   <span class="cm"># PydanticUser（带 org）</span>
    <span class="kw">except</span> NoResultFound:
        <span class="kw">return</span> <span class="kw">await</span> self.<span class="fn">create_default_actor_async</span>()    <span class="cm"># 首次启动：懒建默认 user/org</span>
</pre></div>
<p>三步：<span class="mono">no_default_actor</span> 守卫挡住"裸奔"请求；否则把空 id 回退成 <span class="mono">DEFAULT_USER_ID</span>；最后查这个 user，查不到就懒建一个默认 user（带 <span class="mono">DEFAULT_ORG_ID</span>）。</p>
<p>返回的是 <span class="mono">PydanticUser</span>，身上带着 <span class="mono">organization_id</span>——正是 <span class="mono">apply_access_predicate</span> 用来限定 org 的那个字段。身份链到这里闭合：<strong>header → actor → org → 每条查询的 WHERE</strong>。</p>
<p>注意 <span class="mono">get_headers</span> "不碰 DB" 是有意为之：它只做廉价的格式校验，把"这个 user 到底存不存在"留给真正用到它的那次查询。<strong>鉴权与取数解耦</strong>，入口因此极轻。</p>
<p>这也划出了 secure by default 的边界：身份校验只保证"格式对"，真正的隔离发生在底层那句 <span class="mono">where</span>。两道关卡，一轻一重，缺一不可。</p>
<p>留意这个回退：不开 <span class="mono">no_default_actor</span> 时，缺 <span class="mono">user_id</span> 的请求会落到<strong>共享的 default 租户</strong>。开发顺手，但生产要当心——别让多个真实租户共用了默认 org。</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">secure by default 的 "default" 其实有两层意思：<strong>默认隔离</strong>（每查必套 predicate），和<strong>缺身份时的默认 actor</strong>。前者永远在；后者可被 <span class="mono">no_default_actor</span> 关掉，以强制每个请求都显式带身份。</span></div>
<details class="accordion"><summary>服务器口令 vs 租户隔离——这俩是一回事吗？</summary><div class="acc-body">
<p>不是，<strong>完全正交</strong>。服务器口令由 <span class="mono">middleware/check_password.py::CheckPasswordMiddleware</span> 处理，仅在 <span class="mono">LETTA_SERVER_SECURE=true</span>（或 <span class="mono">--secure</span>）时才挂载。</p>
<p>它认的是<strong>单一共享密钥</strong>：<span class="mono">X-BARE-PASSWORD: password &lt;pw&gt;</span> 或 <span class="mono">Authorization: Bearer &lt;pw&gt;</span>，对就放行、错就 <span class="mono">401</span>，健康探针豁免。</p>
<p>关键：这道闸<strong>与租户无关</strong>——它只管"能不能进这台服务器"；进来之后你是哪个 org、看得到哪一格，全由 <span class="mono">actor</span> 决定。</p>
<p>所以两层叠着用：口令是<strong>大门门禁</strong>（整服务器级），actor 隔离是<strong>柜内分格</strong>（租户级）。一个把外人挡在楼外，一个把同楼的部门彼此隔开。</p>
</div></details>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>多租户隔离的反转：它不在 handler 里"记得加 <span class="mono">WHERE</span>"，而是<strong>焊在最低层的查询构造器里</strong>。约 40 个模型共用一个 <span class="mono">SqlalchemyBase</span>，"按调用者 org 限定每次读"只写一次，自动套在 <span class="mono">read_async</span> / <span class="mono">list_async</span> / <span class="mono">size_async</span> / <span class="mono">bulk_hard_delete_async</span> 上。</p>
<p>于是新功能作者写<strong>零租户 SQL</strong>——只要把 <span class="mono">actor</span> 串下去（"路由 → manager"让串 actor 成了阻力最小的写法），跨租户泄漏在结构上就很难发生：没有任何一处 per-endpoint 的 <span class="mono">WHERE</span> 可被遗忘。</p>
<p>更耐人寻味的取舍：actor 缺失时 base <strong>不硬失败</strong>，而是打一条 <span class="mono">SECURITY: ...bypasses organization filtering</span> 警告照跑——因为 Letta 有合法的、系统内部无 user 的查询。于是它选了<strong>中央强制 + 响亮日志</strong>，而非脆弱的硬失败。</p>
<p>再叠两层同长在这个 base 上的可恢复性：软删让删除可逆（<span class="mono">delete_async</span> 只翻 <span class="mono">is_deleted</span>），审计四件套让每行天生能回答"谁、何时"。于是<strong>多租户 + 可恢复 + 可审计，全是一个抽象类的属性</strong>。</p>
</div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p>predicate 虽在 base，却 <strong>gated on <span class="mono">if actor:</span></strong>：<span class="mono">actor=None</span> 时只记 <span class="mono">SECURITY</span> 警告、<strong>不拦</strong>，无范围照跑。别以为"焊在底层"就一定拦得住。</p>
<p><strong>软删行默认仍被返回</strong>：<span class="mono">check_is_deleted</span> 默认 <span class="mono">False</span>，是 opt-in。以为 <span class="mono">delete_async</span> 后就查不到，是最常见的坑。</p>
<p>默认是 <strong>org 级</strong>（同 org 的用户共享行）；只有 <span class="mono">jobs / runs</span> 才用 <strong>user 级</strong>私有。别把 Block/Agent 当成用户私有的。</p>
<p><span class="mono">access</span>（read/write/admin）<strong>目前是 no-op</strong>（开头 <span class="mono">del access</span>）：传它不改变任何结果，只是给将来留座。</p>
<p>不开 <span class="mono">no_default_actor</span> 时，缺 <span class="mono">user_id</span> 的请求会落到<strong>共享 default 租户</strong>——开发方便，生产务必显式带身份或开守卫。</p>
</div>
<h2>回扣与铺垫：一个基类的复利</h2>
<p>把这一课收个尾。多租户、可恢复、可审计这三样，之所以能"免费"地遍布全库，是因为它们都长在同一个 <span class="mono">SqlalchemyBase</span> 上——<strong>继承一次，复利三份</strong>。</p>
<p>回扣第 25 课：manager 那套统一流水线里，第 3、4 步调的正是这套泛型 CRUD。manager 负责开 session、串 actor，CRUD 负责焊隔离、盖审计——两层各司其职。</p>
<p>回扣第 24 课：<span class="mono">actor</span> 的源头在路由入口那个 <span class="mono">user_id</span> header。三层楼从上到下，身份一路下沉，到这层才被翻译成一句 <span class="mono">WHERE</span>。</p>
<p>回扣第 08 / 10 / 11 课：你早见过的 Block、Passage、记忆三件套，全带 <span class="mono">OrganizationMixin</span>、全走这条 <span class="mono">apply_access_predicate</span>——同一道门禁，这次隔离的是记忆。</p>
<p>铺垫第 27 课：这些被隔离、被审计的行，最终落在哪个库、靠哪个引擎、怎么抹平方言差异？下一课推开最底层那扇门。</p>
<p>一句话串起第七部分的后三课：第 25 课"谁开事务"、第 26 课"每行怎么被隔离与记账"、第 27 课"这些行落在哪"。三课合起来，才凑成完整的服务端持久化。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">一个抽象基类同时给出隔离、软删、审计——这正是"继承一次、复利三份"。读这套代码时，先认 <span class="mono">SqlalchemyBase</span>，再看各模型，剩下的就只是"多了哪列、改了哪个动词"。</span></div>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li><strong>secure by default</strong>：读路只要传了 <span class="mono">actor</span>，<span class="mono">apply_access_predicate</span> 自动追加 <span class="mono">WHERE org==actor.org</span>（USER 范围仅 jobs/runs）；越权＝查不到（<span class="mono">NoResultFound</span> / <span class="mono">[]</span>），非报错。</li>
<li>一个抽象基类 <span class="mono">SqlalchemyBase</span> 给约 40 个模型一套泛型 async CRUD：<strong>读控访问、写盖审计、删分软硬</strong>；隔离只写一次，焊在最低层。</li>
<li>软删默认<strong>可逆</strong>：<span class="mono">delete_async</span> 只翻 <span class="mono">is_deleted</span>；读侧过滤是 opt-in（<span class="mono">check_is_deleted</span> 默认 <span class="mono">False</span>），所以软删行默认仍被返回。</li>
<li>两个 <span class="mono">_*_by_id</span> 由 CRUD 在 <span class="mono">_set_created_and_updated_by_fields</span> 里显式盖、<strong>且只有传 actor 才盖</strong>；<span class="mono">created_at</span> / <span class="mono">updated_at</span> 走 DB 的 <span class="mono">server_default</span> / <span class="mono">onupdate</span>（不需 actor）；<span class="mono">is_deleted</span> 由 <span class="mono">delete_async</span> 翻。</li>
<li>关键 gate：predicate <strong>gated on <span class="mono">if actor:</span></strong>，<span class="mono">actor=None</span> 只警告不拦；<span class="mono">access</span> 目前 no-op；服务器口令与租户隔离<strong>正交</strong>。</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">一句话收束：<span class="mono">SqlalchemyBase</span> ＝<strong>"secure by default 的底座"</strong>——每条查询自动按 org/user 限定、删除默认可逆、每行自带"谁/何时"。多租户、可恢复、可审计，全是一个抽象类的属性。</span></div>
<p>把这条肌肉记忆带走：看到一个新模型，先问它<strong>继承了谁</strong>——只要根上是 <span class="mono">SqlalchemyBase</span>，隔离、软删、审计就都默认到位，你要找的只是它"多了哪一列"。</p>
<p>三楼这道门禁看透了。下一课，我们走到楼底的引擎房，看这些行究竟落在哪个库、靠什么把 SQLite 与 Postgres 的差异抹平。</p>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Last lesson we stood at the second-floor counter and saw the uniform shape of every manager method — open the door, fetch data, change clothes inside. Step 3's one line, <span class="mono">apply_access_predicate</span>, welds tenant isolation "into every SQL," and back then it got only a passing mention.</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson pushes open the third-floor archive room and watches how that gate actually works: around 40 models share one <span class="mono">SqlalchemyBase</span>, one set of generic async CRUD, welding "you only ever see your own cell" into the lowest layer. <strong>Secure by default</strong> — not "remember to add it," but hard to leak even if you tried.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>The whole lesson in one sentence: <strong>every query, by default, sees only the rows that are "your tenant, not yet deleted."</strong></p>
<p>On the read path (<span class="mono">read / list / size</span>), as long as you pass an <span class="mono">actor</span>, the gate auto-appends a <span class="mono">WHERE organization_id == actor.org</span>.</p>
<p>On the write path (<span class="mono">create / update</span>), it stamps the audit fields along the way: who created it, who last changed it, and when.</p>
<p>"Delete" defaults to a <strong>soft delete</strong>: <span class="mono">delete_async</span> only flips <span class="mono">is_deleted</span> to <span class="mono">True</span>; the row still lies in the table.</p>
<p>All of this lives on one abstract base class, <span class="mono">SqlalchemyBase</span>; around 40 models inherit it for free, with no need to rewrite each one.</p>
</div>
<p>This isn't one model's quirk — it's the <strong>shared foundation of all models</strong>. Below, we first draw "secure by default" as one overall flow, then take it apart section by section.</p>
<p>Let's flag one counterintuitive point up front: when <span class="mono">actor</span> is absent, this gate <strong>does not hard-fail</strong> — it logs a loud <span class="mono">SECURITY</span> warning and runs on, unscoped. Why it's designed that way is the subject of this lesson's second half.</p>
<p>Re-aim the camera: Lesson 24 looked at "the whole three-floor building," Lesson 25 at "the second-floor counter," and this lesson watches only <strong>the third-floor gate</strong> — what filter each step adds to a query, from assembly to landing in the DB.</p>
<p>A word on granularity: every code block here is marked "simplified / excerpt." Real methods often carry pagination, filtering, batching and other extra parameters, but the three skeletal moves — <strong>weld isolation, stamp audit, soft delete</strong> — never budge, and the skeleton is exactly what we're after.</p>
<p>One more term to pin down: "tenant" in this lesson = organization (org). One org can hold multiple users, who by default <strong>share the same rows</strong>; objects that are truly per-user private are very few, and we'll name them one by one below.</p>
<h2>A query's security pipeline (secure by default)</h2>
<p>Lay "secure by default" out as a pipeline and you'll see: identity is recognized at the <strong>outermost</strong> layer, isolation is welded into the SQL at the <strong>innermost</strong> layer, and the relay legs in between only honestly thread the <span class="mono">actor</span> through.</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>Password middleware (optional)</h4><p><span class="mono">CheckPasswordMiddleware</span>: a whole-server-level gate, mounted only in <span class="mono">--secure</span> mode; orthogonal to tenancy.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>get_headers · identify</h4><p>Reads the <span class="mono">user_id</span> header, validates it looks like <span class="mono">user-&lt;uuid4&gt;</span>; format only, <strong>never touches the DB</strong>.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Resolve actor</h4><p><span class="mono">get_actor_or_default_async</span>: found → <span class="mono">User</span> (with org); <span class="mono">no_default_actor</span> and no id → rejected.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>manager threads actor</h4><p>The router threads <span class="mono">actor</span> all the way into the manager method — "threading actor" is the path of least resistance.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>Into generic CRUD</h4><p><span class="mono">&lt;crud&gt;_async(actor=...)</span>: lands on <span class="mono">SqlalchemyBase</span>'s uniform verbs.</p></div></div>
  <div class="step"><div class="num">6</div><div class="sc"><h4>Weld isolation</h4><p><span class="mono">apply_access_predicate</span> auto-appends <span class="mono">WHERE org==actor.org</span>; <span class="mono">read_async</span> separately adds <span class="mono">is_deleted==False</span> only when <span class="mono">check_is_deleted</span>.</p></div></div>
  <div class="step"><div class="num">7</div><div class="sc"><h4>Only your own cell remains</h4><p>SQL lands; what comes back is only <strong>this tenant's, undeleted</strong> rows; cross-tenant rows never enter the result set.</p></div></div>
</div>
<p>Of the seven steps, the one that truly <strong>decides who you see</strong> is step 6's auto-appended <span class="mono">WHERE</span>; the first five all do the same thing — safely deliver "who you are" to the gate.</p>
<p>Notice step 1 is parenthesized: the server password is a whole-server-level gate, <strong>orthogonal to tenant isolation</strong> — the password governs "can you enter this server," the <span class="mono">actor</span> governs "once in, which cell you see." That orthogonality gets its own treatment later.</p>
<p>Watch the half-clause in step 6's parentheses too: <span class="mono">is_deleted==False</span> is appended only when <span class="mono">check_is_deleted</span> is true — in other words, <strong>soft-deleted rows are still read back by default</strong>. This is the most counterintuitive bit; the soft-delete section spells it out.</p>
<div class="card analogy"><div class="tag">🏦 An everyday analogy</div>
<p>Picture the whole database as a <strong>shared archive with a gate</strong>; you (the caller) get in only by presenting your badge (<span class="mono">actor</span>).</p>
<p>Every time you open a cabinet, the gate automatically lets you see only your <strong>department's (org)</strong> cell; other departments' cabinets you can't even see.</p>
<p>"Delete" doesn't really incinerate; it slaps a <strong>"void" sticker</strong> on the file (soft delete) — the original stays on the shelf, and you can peel the sticker off to restore it when needed.</p>
<p>On every fetch or return, the archivist automatically stamps a <strong>"who, when"</strong> mark for you (audit), without you asking.</p>
<p>The beauty: these rules aren't written on each borrowing slip but welded into <strong>the gate itself</strong> — swap in a hundred borrowers and the rules don't change a word.</p>
</div>
<div class="cute"><div class="row"><span class="emoji">🔐</span><span class="lab">Gate · every query</span><span class="arrow">→</span><span class="emoji">🏷️</span><span class="lab">Void sticker · soft delete</span><span class="arrow">→</span><span class="emoji">🧾</span><span class="bubble">Who/when · audit</span></div><div class="cap">🔐 The gate auto-stamps every query (only your cell passes), 🏷️ a "void" sticker = soft delete (original stays on the shelf, recoverable), 🧾 every fetch/return auto-stamps a "who/when" mark (audit)</div></div>
<p>The three things in this little picture — isolation, soft delete, audit — actually all live on <strong>the same abstract class</strong>. The next three sections take them apart, in exactly this order.</p>
<h2>SqlalchemyBase: one set of verbs, shared by ~40 models</h2>
<p>First grasp how wide this CRUD's <strong>surface</strong> is: it isn't some manager's private method but a set of async classmethods on the ORM abstract base class <span class="mono">SqlalchemyBase</span> (<span class="mono">__abstract__</span>), which around 40 models inherit for free.</p>
<p>These verbs come in three kinds: <strong>read, write, delete</strong>. Only the read path has access control, the write path stamps audit, and delete splits into soft and hard. Let's lay the whole picture out in a table first:</p>
<table class="t">
<tr><th>Method</th><th>Kind</th><th>Access control?</th><th>Soft-delete aware?</th></tr>
<tr><td class="mono">read_async</td><td>Read</td><td>Only with <span class="mono">actor</span> (org-level)</td><td>Only when <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">list_async</td><td>Read</td><td>Only with <span class="mono">actor</span></td><td>Only when <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">read_multiple_async</td><td>Read</td><td>Only with <span class="mono">actor</span></td><td>Only when <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">size_async</td><td>Read</td><td>Only with <span class="mono">actor</span></td><td>Only when <span class="mono">check_is_deleted</span></td></tr>
<tr><td class="mono">create_async</td><td>Write</td><td>Rides the boundary the read established</td><td>Stamps audit fields</td></tr>
<tr><td class="mono">update_async</td><td>Write</td><td>Rides the boundary the read established</td><td>Stamps audit fields</td></tr>
<tr><td class="mono">delete_async</td><td>Soft delete</td><td>Stamps audit if <span class="mono">actor</span></td><td>Flips <span class="mono">is_deleted=True</span></td></tr>
<tr><td class="mono">hard_delete_async</td><td>Physical delete</td><td><span class="mono">actor</span> for logging only</td><td>Whole row vanishes</td></tr>
<tr><td class="mono">bulk_hard_delete_async</td><td>Bulk physical delete</td><td><strong>predicate applied in SQL</strong></td><td>Whole row vanishes</td></tr>
</table>
<p>Reading the table, hold two through-lines. First: access control takes effect only on the <strong>read path</strong> (and only "if there's an <span class="mono">actor</span>"); write and delete don't each re-apply a <span class="mono">WHERE</span> — they ride the boundary the read already established.</p>
<p>Second: the only one that enforces tenancy on the <strong>delete</strong> side too is <span class="mono">bulk_hard_delete_async</span> — it weaves the predicate into the <span class="mono">DELETE</span> at the SQL level. That's an important exception; more in the soft-delete section.</p>
<p>One detail worth remembering: the four read-path methods all take the same parameter set — <span class="mono">actor</span>, <span class="mono">access=["read"]</span>, <span class="mono">access_type=ORGANIZATION</span>, <span class="mono">check_is_deleted=False</span>. Same parameters, same behavior.</p>
<p>Why make it <strong>generic</strong>? Because these verbs are nearly identical for every model. Had each of ~40 models written its own read / create, isolation and audit would have ~40 places to get wrong; folding them into the base means the <strong>correct way</strong> is maintained in just one place.</p>
<p>This is also the easy way to read this layer: learn the verbs on <span class="mono">SqlalchemyBase</span>, then for a concrete model you only care <strong>which one it overrides</strong> — a relation-heavy one like agent rewrites the read path, while most models inherit it as-is.</p>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">orm/sqlalchemy_base.py::SqlalchemyBase</span> — the abstract base class; <span class="mono">read_async</span> / <span class="mono">list_async</span> / <span class="mono">create_async</span> / <span class="mono">delete_async</span> / <span class="mono">apply_access_predicate</span> all live here.</p>
<p><span class="mono">SqlalchemyBase.apply_access_predicate</span> + <span class="mono">AccessType(str, Enum){ORGANIZATION, USER}</span> — the injection point for row-level filtering and its two scopes.</p>
<p><span class="mono">orm/base.py::CommonSqlalchemyMetaMixins</span> — the four audit fields + the <span class="mono">is_deleted</span> soft-delete flag; <span class="mono">orm/mixins.py::OrganizationMixin / UserMixin</span> provide the <span class="mono">organization_id / user_id</span> columns.</p>
<p><span class="mono">services/user_manager.py::UserManager.get_actor_or_default_async</span> — resolves the id in the header into a <span class="mono">PydanticUser</span> (with org).</p>
</div>
<h2>apply_access_predicate: welding isolation into every read</h2>
<p>Table done; now drill into that "auto-appended <span class="mono">WHERE</span>." It's one classmethod, astonishingly short, yet the <strong>entire secret</strong> of the whole multi-tenant isolation.</p>
<p>Look at the body first. Note the first line, <span class="mono">del access</span>: the three accesses <span class="mono">read / write / admin</span> are <strong>currently a no-op</strong>, pure placeholders reserving a seat for future row-level permissions.</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/sqlalchemy_base.py</span><span class="ln">apply_access_predicate: the entire secret of isolation (simplified)</span></div>
<pre><span class="nb">@classmethod</span>
<span class="kw">def</span> <span class="fn">apply_access_predicate</span>(cls, query, actor, access, access_type=AccessType.ORGANIZATION):
    <span class="kw">del</span> access                      <span class="cm"># read/write/admin are a no-op for now: placeholder for future row-level perms</span>
    <span class="kw">if</span> access_type == AccessType.ORGANIZATION:
        <span class="kw">return</span> query.<span class="fn">where</span>(cls.organization_id == actor.organization_id)  <span class="cm"># same org shares</span>
    <span class="kw">elif</span> access_type == AccessType.USER:
        <span class="kw">return</span> query.<span class="fn">where</span>(cls.user_id == actor.id)                  <span class="cm"># only jobs / runs</span>
    <span class="kw">raise</span> <span class="fn">ValueError</span>(...)             <span class="cm"># actor lacks org/id accessor = misconfig</span>
</pre></div>
<p>Two branches, two scopes. <span class="mono">ORGANIZATION</span> is the default: scoped by <span class="mono">actor.organization_id</span>, so all users in the same org <strong>share</strong> the same rows (Block, Passage, Agent, Tool… all take this branch).</p>
<p>The <span class="mono">USER</span> scope is used by only two kinds, <strong>jobs / runs</strong>: scoped by <span class="mono">actor.id</span>, making them per-user private. The two columns <span class="mono">organization_id</span> and <span class="mono">user_id</span> are mixed into models by <span class="mono">OrganizationMixin</span> and <span class="mono">UserMixin</span> respectively.</p>
<p>The only thing that raises <span class="mono">ValueError</span> is an <span class="mono">actor</span> that lacks even the org/id accessor — that's a <strong>misconfiguration</strong>, not a violation. What does a cross-tenant access look like? <span class="mono">read_async</span> below has the answer.</p>
<p>Don't underestimate the reach of these two short lines: Block, Passage, Agent, Tool and more all carry <span class="mono">OrganizationMixin</span>, and every read of theirs passes through this <strong>same branch</strong>. The memory isolation you read about in Lessons 08, 10 and 11 is, underneath, this one <span class="mono">where</span> right here.</p>
<p>One more easy mix-up: the predicate filters by <span class="mono">actor.organization_id</span>, <strong>not</strong> by <span class="mono">actor.id</span> — so switching users within the same org sees exactly the same rows. The only things truly per-user private are jobs / runs.</p>
<p>The predicate alone isn't enough; we need to see who calls it, and when, inside <span class="mono">read_async</span>. Unfold the read-path skeleton and it's four steps total:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/sqlalchemy_base.py</span><span class="ln">read_async: build query → weld isolation → optionally filter soft-deleted → fetch one row (simplified)</span></div>
<pre><span class="nb">@classmethod</span>
<span class="kw">async def</span> <span class="fn">read_async</span>(cls, db_session, identifier=<span class="kw">None</span>, actor=<span class="kw">None</span>,
                     access=[<span class="st">&quot;read&quot;</span>], access_type=AccessType.ORGANIZATION,
                     check_is_deleted=<span class="kw">False</span>, **kwargs):
    query = <span class="fn">select</span>(cls).<span class="fn">where</span>(cls.id == identifier)
    <span class="kw">if</span> actor:                                <span class="cm"># have identity -&gt; weld org/user isolation</span>
        query = cls.<span class="fn">apply_access_predicate</span>(query, actor, access, access_type)
    <span class="kw">elif</span> <span class="fn">is_org_scoped</span>(cls):                 <span class="cm"># no actor but org-scoped: don't block, just warn loudly</span>
        logger.<span class="fn">warning</span>(<span class="st">&quot;SECURITY: ... without actor ... bypasses organization filtering&quot;</span>)
    <span class="kw">if</span> check_is_deleted:                      <span class="cm"># opt-in: soft-delete not filtered by default</span>
        query = query.<span class="fn">where</span>(cls.is_deleted == <span class="kw">False</span>)
    row = (<span class="kw">await</span> db_session.<span class="fn">execute</span>(query)).<span class="fn">scalar_one_or_none</span>()
    <span class="kw">if</span> row <span class="kw">is</span> <span class="kw">None</span>:
        <span class="kw">raise</span> <span class="fn">NoResultFound</span>(...)            <span class="cm"># cross-tenant row = not found, not an error</span>
    <span class="kw">return</span> row
</pre></div>
<p>Four steps, clear through: first <span class="mono">select(cls).where(id)</span>, then weld isolation per <span class="mono">actor</span> (or log a <span class="mono">SECURITY</span> warning when actor is missing), optionally filter soft-deletes, and finally <span class="mono">scalar_one_or_none</span> fetches one row.</p>
<p><span class="mono">read_multiple_async</span> shares the same preprocessing (<span class="mono">_read_multiple_preprocess</span>): same query build, same predicate, same optional soft-delete filter — it just swaps <span class="mono">where(id==)</span> for <span class="mono">where(id.in_(...))</span>. Different broth, same medicine.</p>
<p>Now to answer "what a cross-tenant access looks like": that cross-tenant row is excluded from the result set outright by step 2's <span class="mono">WHERE</span>. So <span class="mono">read_async</span> gets <span class="mono">None</span> → raises <span class="mono">NoResultFound</span>; <span class="mono">list_async</span> returns <span class="mono">[]</span>.</p>
<div class="flow">
  <div class="node hl"><div class="nt">Cross-tenant row</div><div class="nd">another org's data</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">Excluded by WHERE</div><div class="nd">predicate auto-appended</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">scalar_one_or_none()</div><div class="nd">= None</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">NoResultFound / []</div><div class="nd">not found, not 403</div></div>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">A violation returns "not found" rather than 403, <strong>by design</strong>: it leaks nothing to the caller about "that row exists, but you lack permission" — even <strong>existence</strong> itself is isolated. It also means: when debugging, don't be fooled by <span class="mono">NoResultFound</span>; first check that the <span class="mono">actor</span>'s org is right.</span></div>
<details class="accordion"><summary>What exactly does <span class="mono">apply_access_predicate</span> inject? And where did those three accesses go?</summary><div class="acc-body">
<p>It injects exactly one row-level <span class="mono">WHERE</span>, nothing more: <span class="mono">ORGANIZATION</span> → <span class="mono">where(organization_id == actor.organization_id)</span>, <span class="mono">USER</span> → <span class="mono">where(user_id == actor.id)</span>.</p>
<p>It "injects" onto the query object, <strong>before</strong> the SQL actually executes, so isolation happens on the DB side — not by pulling the whole table back and filtering in Python.</p>
<p>A violation = not found, not an error: the excluded row never enters the result set, <span class="mono">read</span> gets <span class="mono">None</span>→<span class="mono">NoResultFound</span>, <span class="mono">list</span> gets <span class="mono">[]</span>. The only <span class="mono">ValueError</span> comes from a misconfigured actor (no org/id accessor).</p>
<p>And those three accesses (read/write/admin)? The opening <span class="mono">del access</span> throws them away — <strong>a pure no-op for now</strong>, a parameter reserved for future row-level permissions; passing anything changes nothing today.</p>
</div></details>
<h2>Soft delete vs hard delete: deletion is reversible</h2>
<p>The third thing that lives on this base class: <strong>recoverability</strong>. "Delete" here isn't one action but three, and they differ a lot. Let's line up the three deletes side by side first:</p>
<div class="cols">
  <div class="col"><h4>🏷️ delete_async · soft delete</h4><p>Only flips <span class="mono">is_deleted</span> to <span class="mono">True</span> (internally via <span class="mono">update_async</span>, stamping audit too if there's an actor). The row stays, recoverable; the read path <strong>still sees it by default</strong>.</p></div>
  <div class="col"><h4>🔥 hard_delete_async · physical delete</h4><p><span class="mono">session.delete(self)</span>, the whole row vanishes from the table, with deadlock retry; <span class="mono">actor</span> here is <strong>used only for logging</strong>, not for isolation.</p></div>
  <div class="col"><h4>🧹 bulk_hard_delete_async · bulk physical delete</h4><p><span class="mono">delete(cls).where(id.in_(...))</span> <span class="mono">+ apply_access_predicate</span> — the <strong>only</strong> delete that enforces tenancy at the SQL level.</p></div>
</div>
<p>Of the three, only <span class="mono">bulk_hard_delete_async</span> also applies the predicate at delete time; for the other two, the security boundary <strong>"rides"</strong> the read that came before them: you must first <span class="mono">read_async</span> the row (already isolated) before you can delete it.</p>
<p>Soft delete is the default. In practice, <span class="mono">services/provider_manager.py</span> calls soft delete when removing a provider, then passes <span class="mono">check_is_deleted=True</span> on read / list to keep soft-deleted rows out — on both the delete and read sides, filtering is <strong>separately opt-in</strong>.</p>
<p>This explains that most counterintuitive default: on the read path <span class="mono">check_is_deleted</span> defaults to <span class="mono">False</span>, so <strong>soft-deleted rows are still returned by default</strong>. To make it "look truly deleted," you must pass <span class="mono">check_is_deleted=True</span> explicitly on read.</p>
<p>What soft delete buys is a "do-over pill": an accidental delete can be restored, history can be traced back, and cascade cleanup can take its time. The cost is that the read path must <strong>always remember to filter</strong>, or "deleted" rows quietly slip into results — exactly the source of the pitfall above.</p>
<p>One more engineering upside: soft delete turns "delete" into an ordinary <span class="mono">update</span>, sparing the immediate cleanup of cascading foreign keys; when you truly need to reclaim space, the <span class="mono">hard_delete</span> family does a physical delete at a chosen moment. Both read and write paths end up simpler.</p>
<details class="accordion"><summary>Why is a soft-deleted row "still in the table"? And when does it get filtered out?</summary><div class="acc-body">
<p>Soft delete flips a single boolean bit, <span class="mono">is_deleted=True</span>; not a byte of the row moves, foreign keys and relations stay intact — so <strong>history, audit and restore</strong> are all still in hand.</p>
<p>Filtering is the <strong>read side's opt-in</strong>: <span class="mono">read / list</span> default to <span class="mono">check_is_deleted=False</span> and don't append <span class="mono">is_deleted==False</span>, so soft-deleted rows are still found.</p>
<p>To keep soft-deleted rows out, the caller must pass <span class="mono">check_is_deleted=True</span> explicitly (as in <span class="mono">provider_manager</span>'s read path). One place deletes, another reads, each deciding on its own whether to see the "voided" ones.</p>
<p>Why not filter by default? Because plenty of internal scenarios (audit, trace-back, cascade cleanup) need exactly to see soft-deleted rows; leaving the filter to the caller is more flexible than a one-size-fits-all rule.</p>
</div></details>
<h2>Audit fields: every row is born able to answer "who, when"</h2>
<p>The same base class also hands every row a few "birth certificate" fields (plus the <span class="mono">is_deleted</span> we already know), so any row can answer <strong>"who created it, who last touched it, and when."</strong></p>
<div class="cellgroup"><div class="cg-cap"><b>The four audit fields + <span class="mono">is_deleted</span> (<span class="mono">base.py::CommonSqlalchemyMetaMixins</span>)</b></div><div class="cells"><span class="cell hl">created_at</span><span class="sep">·</span><span class="cell">updated_at</span><span class="sep">·</span><span class="cell">_created_by_id</span><span class="sep">·</span><span class="cell">_last_updated_by_id</span><span class="sep">·</span><span class="cell">is_deleted</span></div></div>
<p><span class="mono">created_at</span> / <span class="mono">updated_at</span> are stamped by <strong>DB-side defaults</strong>: <span class="mono">created_at</span> uses <span class="mono">server_default=func.now()</span>, and <span class="mono">updated_at</span> adds <span class="mono">server_onupdate</span>, refreshing automatically on every write.</p>
<p>The two <span class="mono">*_by_id</span> columns are the "who": note the <strong>physical column names carry an underscore</strong> — <span class="mono">_created_by_id</span>, <span class="mono">_last_updated_by_id</span>; the outward attributes drop the underscore, and the setter even asserts the id prefix = <span class="mono">"user"</span>.</p>
<p><span class="mono">created_by_id</span> is set only on the <strong>first write</strong> and never changes after; <span class="mono">last_updated_by_id</span> updates on every write. So a row's "origin" and "most recent handler" are kept cleanly apart.</p>
<p>It's more interesting to view audit and isolation together: isolation decides "<strong>who can see</strong> this row," audit records "<strong>who touched</strong> this row." The same <span class="mono">actor</span> serves once as a filter condition and once as a signature — identity is used twice at this layer.</p>
<p>Leaving time fields to DB defaults has another upside: <span class="mono">created_at</span> / <span class="mono">updated_at</span> are generated DB-side by <span class="mono">server_default</span> / <span class="mono">server_onupdate</span>, not relying on the app clock, so concurrent writes from multiple instances won't each record their own.</p>
<details class="accordion"><summary>How do the audit fields get stamped? And why do the column names carry an underscore?</summary><div class="acc-body">
<p>Not via SQLAlchemy event listeners but by an <strong>explicit call</strong> in the CRUD, <span class="mono">_set_created_and_updated_by_fields(actor_id)</span> — a manual touch on the create / update path.</p>
<p>Key precondition: <strong>it stamps only when an actor is passed</strong>. A write without an actor (a rare system-internal path) records no "who," and only the DB-side time defaults still take effect as usual.</p>
<p>The physical columns are named <span class="mono">_created_by_id</span> / <span class="mono">_last_updated_by_id</span> (with the underscore) to decouple from the outward attributes: the attribute setter asserts the incoming id starts with <span class="mono">"user"</span>, blocking garbage.</p>
<p><span class="mono">created_by_id</span> never changes once first set, <span class="mono">last_updated_by_id</span> refreshes on every write — one records "who birthed it," the other "who last touched it."</p>
</div></details>
<h2>Where actor comes from: the entrance to secure by default</h2>
<p>The whole premise of isolation is that <span class="mono">actor</span>. Where does it come from? The answer is surprisingly plain: an <strong>HTTP header</strong>.</p>
<p><span class="mono">rest_api/dependencies.py::get_headers</span> uses <span class="mono">Header(None, alias="user_id")</span> to read the <span class="mono">user_id</span> header and validate it looks like <span class="mono">user-&lt;uuid4&gt;</span> — <strong>format only, never touches the DB</strong>.</p>
<p>What actually turns that id into a <span class="mono">User</span> is <span class="mono">get_actor_or_default_async</span>:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/services/user_manager.py</span><span class="ln">get_actor_or_default_async: resolve the id in the header into an actor (simplified)</span></div>
<pre><span class="kw">async def</span> <span class="fn">get_actor_or_default_async</span>(self, actor_id=<span class="kw">None</span>):
    <span class="kw">if</span> settings.no_default_actor <span class="kw">and</span> actor_id <span class="kw">is</span> <span class="kw">None</span>:
        <span class="kw">raise</span> <span class="fn">NoResultFound</span>(...)               <span class="cm"># secure mode: must carry identity explicitly</span>
    actor_id = actor_id <span class="kw">or</span> DEFAULT_USER_ID     <span class="cm"># otherwise fall back to the default user</span>
    <span class="kw">try</span>:
        <span class="kw">return</span> <span class="kw">await</span> self.<span class="fn">get_actor_by_id_async</span>(actor_id)   <span class="cm"># PydanticUser (with org)</span>
    <span class="kw">except</span> NoResultFound:
        <span class="kw">return</span> <span class="kw">await</span> self.<span class="fn">create_default_actor_async</span>()    <span class="cm"># first boot: lazily create the default user/org</span>
</pre></div>
<p>Three steps: the <span class="mono">no_default_actor</span> guard blocks "naked" requests; otherwise an empty id falls back to <span class="mono">DEFAULT_USER_ID</span>; finally it looks up that user, and on a miss lazily creates a default user (with <span class="mono">DEFAULT_ORG_ID</span>).</p>
<p>It returns a <span class="mono">PydanticUser</span> carrying <span class="mono">organization_id</span> — precisely the field <span class="mono">apply_access_predicate</span> uses to scope by org. The identity chain closes here: <strong>header → actor → org → every query's WHERE</strong>.</p>
<p>Note that <span class="mono">get_headers</span> "never touching the DB" is deliberate: it does only a cheap format check and leaves "does this user actually exist" to the query that truly uses it. <strong>Auth and data-fetch are decoupled</strong>, keeping the entrance extremely light.</p>
<p>This also draws the boundary of secure by default: identity validation only guarantees "the format is right," while the real isolation happens in that low-level <span class="mono">where</span>. Two checkpoints, one light and one heavy, neither dispensable.</p>
<p>Watch this fallback: with <span class="mono">no_default_actor</span> off, a request missing <span class="mono">user_id</span> lands in the <strong>shared default tenant</strong>. Handy in development, but be careful in production — don't let multiple real tenants share the default org.</p>
<div class="note tip"><span class="ni">🧠</span><span class="nx">The "default" in secure by default actually carries two meanings: <strong>default isolation</strong> (the predicate on every query) and the <strong>default actor</strong> when identity is missing. The former is always on; the latter can be switched off with <span class="mono">no_default_actor</span> to force every request to carry identity explicitly.</span></div>
<details class="accordion"><summary>Server password vs tenant isolation — are these the same thing?</summary><div class="acc-body">
<p>No, <strong>completely orthogonal</strong>. The server password is handled by <span class="mono">middleware/check_password.py::CheckPasswordMiddleware</span>, mounted only when <span class="mono">LETTA_SERVER_SECURE=true</span> (or <span class="mono">--secure</span>).</p>
<p>It recognizes a <strong>single shared secret</strong>: <span class="mono">X-BARE-PASSWORD: password &lt;pw&gt;</span> or <span class="mono">Authorization: Bearer &lt;pw&gt;</span> — right passes, wrong gets <span class="mono">401</span>, with health probes exempt.</p>
<p>Key: this gate is <strong>tenant-agnostic</strong> — it governs only "can you enter this server"; once in, which org you are and which cell you see is entirely decided by <span class="mono">actor</span>.</p>
<p>So the two layers stack: the password is the <strong>front-door gate</strong> (whole-server-level), actor isolation is the <strong>cell partition inside the cabinet</strong> (tenant-level). One keeps outsiders out of the building, the other keeps departments in the same building apart.</p>
</div></details>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>The inversion of multi-tenant isolation: it doesn't "remember to add a <span class="mono">WHERE</span>" in each handler but is <strong>welded into the lowest-level query builder</strong>. Around 40 models share one <span class="mono">SqlalchemyBase</span>, so "scope every read by the caller's org" is written once and auto-applied to <span class="mono">read_async</span> / <span class="mono">list_async</span> / <span class="mono">size_async</span> / <span class="mono">bulk_hard_delete_async</span>.</p>
<p>So a new-feature author writes <strong>zero tenant SQL</strong> — just thread <span class="mono">actor</span> through ("router → manager" makes threading actor the path of least resistance), and cross-tenant leakage becomes structurally hard: there's no per-endpoint <span class="mono">WHERE</span> anywhere to forget.</p>
<p>A more intriguing trade-off: when actor is missing the base <strong>does not hard-fail</strong> but logs a <span class="mono">SECURITY: ...bypasses organization filtering</span> warning and runs on — because Letta has legitimate, system-internal queries with no user. So it chose <strong>central enforcement + a loud log</strong> over brittle hard failure.</p>
<p>Stack on two more layers of recoverability that live on this same base: soft delete makes deletion reversible (<span class="mono">delete_async</span> only flips <span class="mono">is_deleted</span>), and the four audit fields let every row natively answer "who, when." So <strong>multi-tenant + recoverable + auditable</strong> are all properties of one abstract class.</p>
</div>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<p>Though the predicate lives in the base, it's <strong>gated on <span class="mono">if actor:</span></strong>: when <span class="mono">actor=None</span> it only logs a <span class="mono">SECURITY</span> warning and <strong>doesn't block</strong>, running on unscoped. Don't assume "welded into the bottom layer" always blocks.</p>
<p><strong>Soft-deleted rows are still returned by default</strong>: <span class="mono">check_is_deleted</span> defaults to <span class="mono">False</span>, it's opt-in. Assuming <span class="mono">delete_async</span> makes a row unfindable is the most common trap.</p>
<p>The default is <strong>org-level</strong> (users in the same org share rows); only <span class="mono">jobs / runs</span> use <strong>user-level</strong> privacy. Don't treat Block/Agent as per-user private.</p>
<p><span class="mono">access</span> (read/write/admin) is <strong>a no-op for now</strong> (the opening <span class="mono">del access</span>): passing it changes nothing, it just reserves a seat for the future.</p>
<p>With <span class="mono">no_default_actor</span> off, a request missing <span class="mono">user_id</span> lands in the <strong>shared default tenant</strong> — convenient in development, but in production always carry identity explicitly or enable the guard.</p>
</div>
<h2>Looking back, looking ahead: the compound interest of one base class</h2>
<p>Let's wrap this lesson. Multi-tenancy, recoverability and auditability spread "for free" across the whole codebase because they all live on the same <span class="mono">SqlalchemyBase</span> — <strong>inherit once, compound three ways</strong>.</p>
<p>Callback to Lesson 25: in the manager's uniform pipeline, steps 3 and 4 call exactly this generic CRUD. The manager opens the session and threads <span class="mono">actor</span>, the CRUD welds isolation and stamps audit — two layers, each to its own job.</p>
<p>Callback to Lesson 24: <span class="mono">actor</span>'s source is the <span class="mono">user_id</span> header at the router entrance. Down the three floors, identity sinks all the way and only at this layer gets translated into one <span class="mono">WHERE</span>.</p>
<p>Callback to Lessons 08 / 10 / 11: the Block, Passage and the memory trio you saw long ago all carry <span class="mono">OrganizationMixin</span> and all go through this <span class="mono">apply_access_predicate</span> — the same gate, this time isolating memory.</p>
<p>Setup for Lesson 27: these isolated, audited rows ultimately land in which database, on which engine, smoothing over which dialect differences? The next lesson pushes open that bottom-most door.</p>
<p>One sentence threads Part 7's last three lessons: Lesson 25 "who opens the transaction," Lesson 26 "how each row is isolated and accounted for," Lesson 27 "where these rows land." The three together make up complete server-side persistence.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">One abstract base class delivers isolation, soft delete and audit at once — that's exactly "inherit once, compound three ways." When reading this code, first learn <span class="mono">SqlalchemyBase</span>, then each model, and the rest is just "which column was added, which verb was overridden."</span></div>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li><strong>secure by default</strong>: on the read path, as long as you pass <span class="mono">actor</span>, <span class="mono">apply_access_predicate</span> auto-appends <span class="mono">WHERE org==actor.org</span> (the USER scope is jobs/runs only); a violation = not found (<span class="mono">NoResultFound</span> / <span class="mono">[]</span>), not an error.</li>
<li>One abstract base class <span class="mono">SqlalchemyBase</span> gives ~40 models one set of generic async CRUD: <strong>reads control access, writes stamp audit, deletes split soft/hard</strong>; isolation is written once, welded into the lowest layer.</li>
<li>Soft delete is <strong>reversible by default</strong>: <span class="mono">delete_async</span> only flips <span class="mono">is_deleted</span>; read-side filtering is opt-in (<span class="mono">check_is_deleted</span> defaults to <span class="mono">False</span>), so soft-deleted rows are still returned by default.</li>
<li>The two <span class="mono">_*_by_id</span> fields are stamped by the CRUD's <span class="mono">_set_created_and_updated_by_fields</span>, <strong>only when an actor is passed</strong>; <span class="mono">created_at</span> / <span class="mono">updated_at</span> come from DB-side <span class="mono">server_default</span> / <span class="mono">server_onupdate</span> (no actor needed); <span class="mono">is_deleted</span> is flipped by <span class="mono">delete_async</span>.</li>
<li>Key gate: the predicate is <strong>gated on <span class="mono">if actor:</span></strong>, <span class="mono">actor=None</span> only warns, doesn't block; <span class="mono">access</span> is a no-op for now; the server password is orthogonal to tenant isolation.</li>
</ul>
</div>
<div class="note info"><span class="ni">💡</span><span class="nx">In one line: <span class="mono">SqlalchemyBase</span> = "the foundation of secure by default" — every query auto-scoped by org/user, deletion reversible by default, every row carrying its own "who/when." Multi-tenant, recoverable, auditable — all properties of one abstract class.</span></div>
<p>Take this muscle memory with you: when you see a new model, first ask who it inherits — as long as <span class="mono">SqlalchemyBase</span> is at the root, isolation, soft delete and audit are all in place by default, and all you're looking for is "which column it added."</p>
<p>The third-floor gate is now seen through. Next lesson we walk down to the engine room at the bottom and watch which database these rows actually land in, and what smooths over the differences between SQLite and Postgres.</p>
""",
}

LESSON_27 = {
    "zh": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">上一课在三楼档案室，我们看清了 <span class="mono">SqlalchemyBase</span> 怎么把隔离、软删、审计焊进每条 SQL。可那句 SQL 最终落进哪个库、靠哪个引擎执行，当时只用一句"走到楼底的引擎房"带过。</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">这一课就推开引擎房那扇门：同一套 ORM 模型，怎么在 SQLite 与 Postgres 两套库上都能跑？向量又怎么在两套库里存、怎么搜？答案不在某个聪明的 <span class="mono">db.py</span> 里，而是<strong>散在六处、且大多声明式</strong>的接缝。</p>
<div class="card macro"><div class="tag">🌍 宏观理解</div>
<p>一句话抓住本课：<strong>一套 ORM 模型，按一个开关在两套库上跑；向量两存两搜；配置当 JSON blob 整块塞进列</strong>。</p>
<p>开关＝ <span class="mono">settings.database_engine</span>：配了 Postgres URI 就走 Postgres，否则走 SQLite。</p>
<p>向量两套：Postgres 用 pgvector 的 <span class="mono">Vector(4096)</span> + 原生算子 <span class="mono">&lt;=&gt;</span>；SQLite 用 BINARY blob + numpy 写的 <span class="mono">cosine_distance</span> 全表暴力。</p>
<p>pydantic-in-DB：<span class="mono">EmbeddingConfig</span> / <span class="mono">LLMConfig</span> 这类配置不拆成列，整个 <span class="mono">model_dump</span> 成 JSON 存一格。</p>
<p>一处诚实的现状：v0.16.8 的 <span class="mono">server/db.py</span> 其实只建 Postgres——双库故事完整活在 ORM 与 alembic 层。</p>
</div>
<p>这不是一句"if 后端 == sqlite"的大开关。真正的接缝<strong>分布在六处</strong>，大多在 import 期就声明好，而不是运行时临场判断。</p>
<p>先把镜头拉远：第 24 课看三层架构，第 25 课看 manager 开事务，第 26 课看每行怎么被隔离。这一课走到最底，看这些行<strong>落在哪个库、向量怎么被搜出来</strong>。</p>
<p>也先打个预防针：本课有几处专治"想当然"。比如 <span class="mono">db.py</span> 并不分库、<span class="mono">database_engine</span> 不是个能手设的字段、SQLite 的相似度也不是 sqlite-vec 原生——下文逐一点破。</p>
<h2>一套 ORM，两套引擎：换的是零件，不是蓝图</h2>
<p>先看全景。<span class="mono">letta/orm/</span> 下那约 40 个模型只写<strong>一份</strong>；到底落进哪套库，由一个开关 <span class="mono">settings.database_engine</span> 决定。两条线并排看最清楚：</p>
<div class="cols">
  <div class="col"><h4>🪶 SQLite · 开发默认</h4>
  <p>驱动：<span class="mono">aiosqlite</span>（async）。</p>
  <p>向量列：<span class="mono">CommonVector</span>，一个 BINARY blob。</p>
  <p>距离：<span class="mono">func.cosine_distance</span>，走 numpy UDF。</p>
  <p>搜索：<span class="mono">ORDER BY</span> 全表暴力，没有 ANN。</p>
  <p>迁移：单个 baseline 快照 <span class="mono">2c059cad97cc</span>。</p>
  </div>
  <div class="col"><h4>🐘 Postgres · 生产</h4>
  <p>驱动：<span class="mono">asyncpg</span>（async）。</p>
  <p>向量列：pgvector 的 <span class="mono">Vector(4096)</span>。</p>
  <p>距离：<span class="mono">cosine_distance()</span> → SQL <span class="mono">&lt;=&gt;</span>。</p>
  <p>搜索：可挂 <span class="mono">ivfflat</span> / <span class="mono">hnsw</span> 索引。</p>
  <p>迁移：从 <span class="mono">9a505cc7eca9</span> 起的增量链。</p>
  </div>
</div>
<p>看出门道了吗？两列的<strong>形状一模一样</strong>，被换掉的只是零件：驱动、向量列类型、距离算子、序列化方式、迁移路径，以及"要不要把向量填充到定长"。</p>
<p>同样别忽略"没被换"的那一长串：表名、列名、关系、约束、<span class="mono">SqlalchemyBase</span> 的隔离与审计、manager 的事务边界——全来自<strong>同一份模型</strong>，两库一字不差。换库只动了贴近存储的薄薄一层。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">一个诚实的星号：上表把"双库"画得很对称，但 v0.16.8 的 <span class="mono">server/db.py</span> 模块级<strong>只建 Postgres async 引擎</strong>。双库的完整故事活在 ORM 列类型与 alembic 迁移里，运行期引擎层已悄悄收敛到 Postgres——为什么这样，本课末尾的"诚实星号"专门讲。</span></div>
<div class="card analogy"><div class="tag">🏭 生活类比</div>
<p>把这套设计想成<strong>一张蓝图、两座工厂</strong>。蓝图＝ORM 模型，画的是"有哪些表、哪些列、怎么关联"，<strong>一份不变</strong>。</p>
<p>两座工厂＝SQLite 厂与 Postgres 厂。同一张蓝图发下去，按墙上那个开关（<span class="mono">database_engine</span>）在装配线上换不同零件。</p>
<p>换的零件很具体：向量列用哪种料（pgvector 定长格 vs BINARY 袋子）、距离用哪台机器（原生 <span class="mono">&lt;=&gt;</span> vs numpy 手算）、迁移走哪条流水线。</p>
<p>妙在工人（写新功能的人）只认蓝图——他不必知道今天在哪座厂开工，照着模型写就行，两套库都装得出来。</p>
</div>
<p>这个"蓝图不变、零件可换"的设计，正是接下来每节要逐一拆开的：先看那个开关，再看换列类型、换距离算子、换迁移路径。</p>
<h2>唯一的开关：database_engine 其实是个 property</h2>
<p>"两套库"听起来该有个枚举让你挑。可打开 <span class="mono">settings.py</span> 你会愣一下：<span class="mono">database_engine</span> <strong>根本不是字段</strong>，而是个只读 <span class="mono">@property</span>。</p>
<p>它的逻辑短到一行：<span class="mono">POSTGRES if self.letta_pg_uri_no_default else SQLITE</span>。换句话说，<strong>配没配 Postgres URI</strong>，就是 dev/prod 的全部分界。</p>
<div class="flow">
  <div class="node hl"><div class="nt">settings.database_engine</div><div class="nd">@property，不是字段</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">看 letta_pg_uri_no_default</div><div class="nd">URI 或 None</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">非 None → POSTGRES</div><div class="nd">否则 → SQLITE</div></div>
</div>
<p>注意这里有个陷阱：<span class="mono">letta_pg_uri</span> <strong>永远</strong>有默认值，所以判定不能看它；真正"URI-或-None"的是 <span class="mono">letta_pg_uri_no_default</span>。</p>
<p><span class="mono">DatabaseChoice</span> 是个 <span class="mono">(str, Enum)</span>，只有 <span class="mono">POSTGRES</span> / <span class="mono">SQLITE</span> 两值。它是被<strong>读出来的结论</strong>，不是被你写进去的选择。</p>
<p>那个默认 URI 还透露了驱动：<span class="mono">postgresql+pg8000://…</span>——同步路径用 pg8000，异步引擎再换成 asyncpg。组成它的是一组 <span class="mono">LETTA_PG_HOST / DB / USER / PASSWORD / PORT</span>，或直接给整条 <span class="mono">LETTA_PG_URI</span>。</p>
<p>引擎本身在哪建？这正是第一处反直觉：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/db.py · letta/orm/sqlite_functions.py</span><span class="ln">引擎只建 Postgres；给任何 SQLite 连接挂 numpy UDF（节选）</span></div>
<pre><span class="cm"># server/db.py：模块级只有一条 async 引擎——Postgres-only</span>
engine = <span class="fn">create_async_engine</span>(async_pg_uri, ...)   <span class="cm"># 不按 database_engine 分叉、不在此加载 sqlite-vec</span>

<span class="cm"># orm/sqlite_functions.py：任何 SQLite 连接一建立，就挂上 numpy 写的距离函数</span>
<span class="nb">@event.listens_for(Engine, &quot;connect&quot;)</span>
<span class="kw">def</span> <span class="fn">register_functions</span>(dbapi_conn, _):
    <span class="kw">if</span> <span class="fn">isinstance</span>(dbapi_conn, sqlite3.Connection):
        dbapi_conn.<span class="fn">create_function</span>(<span class="st">&quot;cosine_distance&quot;</span>, 2, cosine_distance)  <span class="cm"># 纯 numpy 实现</span>
        <span class="cm"># sqlite_vec.load(dbapi_conn)  ← 注释掉了：不用 sqlite-vec 原生相似度</span>
</pre></div>
<p>两段对照着看：左边 <span class="mono">db.py</span> 的引擎是 Postgres-only；右边那个全局 <span class="mono">@event.listens_for</span> 才是 SQLite 的接缝——它给<strong>任何</strong> SQLite 连接注册一个 numpy 写的 <span class="mono">cosine_distance</span>。</p>
<p>留意最后那行注释：<span class="mono">sqlite_vec.load()</span> 是<strong>被注释掉</strong>的。SQLite 的相似度靠纯 numpy UDF，而不是 sqlite-vec 原生算子——这个纠正后面还会强调。</p>
<p>这个 <span class="mono">@event.listens_for(Engine, "connect")</span> 是<strong>全局</strong>的：不管哪条 SQLite 连接——开发库、测试库、临时内存库——一建立就挂上这个 UDF。所以"SQLite 能算 cosine"是连接级的既成事实，无需每处显式启用。</p>
<div class="card detail"><div class="tag">🔬 落到代码</div>
<p><span class="mono">settings.py::Settings.database_engine</span>——<span class="mono">@property</span>：<span class="mono">POSTGRES if self.letta_pg_uri_no_default else SQLITE</span>；<span class="mono">DatabaseChoice(str, Enum){POSTGRES, SQLITE}</span>。</p>
<p><span class="mono">orm/passage.py::BasePassage</span>——import 期按 <span class="mono">database_engine</span> 定 embedding 列类型。</p>
<p><span class="mono">orm/custom_columns.py</span>——pydantic-in-DB 的一批 <span class="mono">TypeDecorator</span>；<span class="mono">orm/sqlite_functions.py::register_functions</span>——SQLite 的 numpy <span class="mono">cosine_distance</span>。</p>
<p><span class="mono">constants.py::MAX_EMBEDDING_DIM = 4096</span>——定长填充的那把尺；<span class="mono">alembic/env.py</span>——选 URI、分两后端建表。</p>
</div>
<details class="accordion"><summary><span class="mono">database_engine</span> 到底怎么定？能用环境变量手动选 SQLite 吗？</summary><div class="acc-body">
<p>不能直接选。<span class="mono">database_engine</span> 是个<strong>派生 <span class="mono">@property</span></strong>，不是可写字段：它只看 <span class="mono">letta_pg_uri_no_default</span> 是不是 None。</p>
<p><span class="mono">letta_pg_uri</span> 永远有默认值（<span class="mono">postgresql+pg8000://letta:letta@localhost:5432/letta</span>）；真正"URI-或-None"的是 <span class="mono">letta_pg_uri_no_default</span>。配了它＝Postgres，没配＝SQLite。</p>
<p><strong>没有 <span class="mono">LETTA_DATABASE_ENGINE=sqlite</span> 这种开关</strong>。你只要设了任意 <span class="mono">LETTA_PG_*</span>（host / db / user / password / port / uri），就会<strong>静默</strong>翻成 Postgres。</p>
<p>所以"dev 用 SQLite、prod 用 Postgres"不是手动切换，而是<strong>有没有给它 PG 连接信息</strong>这一件事的副作用。</p>
</div></details>
<div class="note tip"><span class="ni">🧠</span><span class="nx">想强制 SQLite？别找开关，<strong>清掉所有 <span class="mono">LETTA_PG_*</span> 环境变量</strong>即可——只要 <span class="mono">letta_pg_uri_no_default</span> 为 None，<span class="mono">database_engine</span> 自然回到 SQLITE。反过来，生产里"怎么没走 Postgres"，先查是不是漏配了 PG URI。</span></div>
<h2>向量怎么存：把任意维度塞进定长 4096 的一列</h2>
<p>记忆里的 archival / recall（第 10、11 课）本质是带 embedding 的 <span class="mono">Passage</span>。可不同模型输出的维度天差地别：有的 1024，有的 1536，有的 3072。一列怎么装得下？</p>
<p>Letta 的答案简单粗暴：<span class="mono">constants.py::MAX_EMBEDDING_DIM = 4096</span>——所有 embedding 在写入和查询时都 <span class="mono">np.pad</span> 到 4096 维，<strong>尾部补 0</strong>。于是一个 <span class="mono">Vector(4096)</span> 列就能装下任意模型的输出。</p>
<p>填充发生在<strong>写入前</strong>：embedding 一生成就被 <span class="mono">np.pad</span> 到 4096，再交给 ORM 落库；查询向量在比对前也走同一步。两端对齐，定长列才装得下、比得了。</p>
<div class="cute"><div class="row"><span class="emoji">📐</span><span class="lab">定长 4096 格</span><span class="arrow">→</span><span class="emoji">🧮</span><span class="lab">某模型 1536 维</span><span class="arrow">→</span><span class="emoji">0️⃣</span><span class="bubble">尾部补 0 填满</span></div><div class="cap">📐 一列就是 4096 维的固定格子；🧮 某模型只输出 1536 维；0️⃣ 尾部补 0 填满格子——补的全是 0，<strong>cosine 排序一点不变</strong>，所以一列能装下任意模型的输出</div></div>
<p>等等，补一堆 0 进去，不会把相似度算歪吗？这正是设计的精妙处：<strong>补 0 对 cosine 完全无影响</strong>。</p>
<div class="cellgroup"><div class="cg-cap"><b>补 0 为什么"免费"：cosine = 点积 /（L2 × L2），两端都不动</b></div><div class="cells"><span class="cell hl">点积 +0×x=0</span><span class="sep">→</span><span class="cell">分子不变</span><span class="sep">·</span><span class="cell">L2 +0²=0</span><span class="sep">→</span><span class="cell">分母不变</span><span class="sep">⇒</span><span class="cell hl">cosine 不变</span></div></div>
<p>道理很直白。cosine ＝点积 ÷（两个向量的 L2 范数之积）。补的是 0：点积里 <span class="mono">0 × 任何 = 0</span>，分子不变；L2 里 <span class="mono">0² = 0</span>，分母也不变。<strong>分子分母都不动，排序自然一模一样</strong>。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">所以"定长一列装任意模型"不是近似、不是妥协，而是<strong>数学上严格等价于不填充</strong>，代价只是多存一串 0、占点空间。SQLite 的 numpy UDF <span class="mono">cosine_distance</span> 会先用 <span class="mono">validate_and_transform_embedding</span> 校验维度＝＝4096，对不上（捕获 <span class="mono">ValueError</span> 后）返回 <span class="mono">0.0</span>——填充是写路和查询路<strong>共同的前提</strong>。</span></div>
<p>那"存哪种列"呢？这是六处接缝里的第二处，发生在 <span class="mono">BasePassage</span> 的<strong>类体里、import 期</strong>：Postgres 用 pgvector 的 <span class="mono">Vector(4096)</span>，SQLite 用 <span class="mono">CommonVector</span>（一个 BINARY blob）。具体代码下一节连搜索一起看。</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><span class="mono">MAX_EMBEDDING_DIM</span> 的注释明确写着"别改，否则得重置数据库"：它定死了列宽，一旦改动，就和库里已存的定长向量对不上了。这把尺是<strong>全局约定</strong>，不是某张表的局部选择。</span></div>
<p>定长也不是全无代价：1024 维的模型，每行白存 3072 个 0，磁盘和内存都摊上这份浪费。但换来的是<strong>一列通吃所有模型</strong>、不必为每种维度各建表——对一个要兼容多家 embedding 的系统，这笔账划算。</p>
<h2>向量怎么搜：原生 &lt;=&gt; vs numpy 暴力</h2>
<p>存定了，怎么搜？这是六处接缝里的第三处，也是运行时唯一真正"分两路"的地方：同一句"按相似度排序"，在两套库上编译成完全不同的执行。</p>
<p>先把列类型和搜索分支放进同一张代码里看——它们其实共用一个 <span class="mono">if database_engine is POSTGRES</span>：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/passage.py · letta/orm/sqlalchemy_base.py</span><span class="ln">import 期定列类型；运行时按引擎分两路搜（节选）</span></div>
<pre><span class="cm"># orm/passage.py::BasePassage —— 类体里、import 期就把列类型烤进模型</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    embedding = <span class="fn">mapped_column</span>(<span class="fn">Vector</span>(MAX_EMBEDDING_DIM))   <span class="cm"># pgvector 定长 4096</span>
<span class="kw">else</span>:
    embedding = <span class="fn">Column</span>(CommonVector)                      <span class="cm"># SQLite：BINARY blob</span>

<span class="cm"># orm/sqlalchemy_base.py 查询构造器：运行时按同一个开关，分两路排序</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    query = query.<span class="fn">order_by</span>(cls.embedding.<span class="fn">cosine_distance</span>(q_emb).<span class="fn">asc</span>())          <span class="cm"># 编译成 SQL &lt;=&gt;</span>
<span class="kw">else</span>:
    query = query.<span class="fn">order_by</span>(<span class="fn">func.cosine_distance</span>(cls.embedding, q_emb).<span class="fn">asc</span>())   <span class="cm"># 走 numpy UDF</span>
</pre></div>
<p>看清两处分叉：上半段是 <strong>import 期</strong>的——类体里那个 <span class="mono">if</span> 在模块被导入时就执行一次，把列类型<strong>烤死</strong>在模型上。所以一个进程被特化到一种后端，运行时<strong>不能切库</strong>。</p>
<p>下半段是<strong>运行时</strong>的：Postgres 把 <span class="mono">cosine_distance()</span> 翻成原生算子 <span class="mono">&lt;=&gt;</span>，SQLite 则调那个我们在 <span class="mono">register_functions</span> 里见过的 numpy UDF。把全貌摆成一张表：</p>
<table class="t">
<tr><th>维度</th><th>Postgres（pgvector）</th><th>SQLite</th></tr>
<tr><td>向量列</td><td class="mono">Vector(4096)</td><td class="mono">CommonVector（BINARY）</td></tr>
<tr><td>距离调用</td><td class="mono">embedding.cosine_distance(q)</td><td class="mono">func.cosine_distance(col, q)</td></tr>
<tr><td>实际算子</td><td>SQL 原生 <span class="mono">&lt;=&gt;</span></td><td>Python numpy UDF</td></tr>
<tr><td>排序</td><td class="mono">ORDER BY dist ASC</td><td class="mono">ORDER BY dist ASC</td></tr>
<tr><td>索引 / ANN</td><td>可挂 <span class="mono">ivfflat</span> / <span class="mono">hnsw</span></td><td>无，全表暴力</td></tr>
<tr><td>适用规模</td><td>大库也扛得住</td><td>小库 / 开发够用</td></tr>
</table>
<p>两边<strong>语义相同</strong>——都按 cosine 升序取最近的若干条；差别只在执行：Postgres 可借索引做近似最近邻（ANN），SQLite 对全表逐行算、再排序。</p>
<p>有人担心"全表暴力"太慢。在开发与小数据量下其实不慢：几千上万条逐行算 cosine，numpy 是向量化的，眨眼就回。真正需要 ANN 的是生产级海量记忆，那时你本就该上 Postgres。</p>
<p>这两路分支也不只活在 <span class="mono">sqlalchemy_base.py</span> 的通用查询里：<span class="mono">services/helpers/agent_manager_helper.py</span> 拼 archival 检索时带的是同一个 <span class="mono">if POSTGRES</span>——同一道分叉，在用到向量搜索的地方各写一次。</p>
<p>这也呼应第 10、11 课：你读过的 archival / recall 检索，底层那句"找最像的记忆"，到这层就分成了这两条路。</p>
<details class="accordion"><summary>向量在两套库里到底怎么存、怎么搜？性能差在哪？</summary><div class="acc-body">
<p><strong>存</strong>：Postgres 是 pgvector 的 <span class="mono">Vector(4096)</span> 定长列；SQLite 是 <span class="mono">CommonVector</span>——一个 BINARY blob，用 <span class="mono">sqlite_vec.serialize_float32</span> 打包、<span class="mono">np.frombuffer</span> 还原。</p>
<p><strong>搜</strong>：Postgres 把 <span class="mono">cosine_distance()</span> 编译成原生算子 <span class="mono">&lt;=&gt;</span>，可借 <span class="mono">ivfflat</span> / <span class="mono">hnsw</span> 索引做 ANN；SQLite 调 numpy UDF，对<strong>全表</strong>逐行算距离再排序。</p>
<p>所以差距在<strong>规模</strong>：小库、开发环境，SQLite 全表暴力毫无压力；行数一大，就得靠 Postgres 的向量索引。两边语义一致，只是一个有 ANN、一个没有。</p>
<p>别忘了：两边都先把查询向量 <span class="mono">np.pad</span> 到 4096 再比——填充是存和搜<strong>共同的前提</strong>，它让"任意模型的向量"落进同一个定长空间。</p>
</div></details>
<h2>pydantic-in-DB：把配置整块塞进一列 JSON</h2>
<p>魔术的另一半和向量无关，却同样优雅：<span class="mono">EmbeddingConfig</span>、<span class="mono">LLMConfig</span>、<span class="mono">ToolRules</span> 这些配置，<strong>不拆成列</strong>，而是整块当 JSON blob 存一格。</p>
<p>第 21 课你见过 <span class="mono">LLMConfig</span> / <span class="mono">EmbeddingConfig</span> 在内存里是 pydantic 模型。它们怎么落库？靠 <span class="mono">custom_columns.py</span> 里一批 <span class="mono">TypeDecorator</span>——SQLAlchemy 的"列类型适配器"。</p>
<p>它在 ORM 与 DB 之间架了一座双向桥，往返各走一道转换：</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>EmbeddingConfig（pydantic）</h4><p>内存里是个带类型、带默认值的 pydantic 模型。</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>写 · process_bind_param</h4><p><span class="mono">model_dump(mode="json")</span> → 一个普通 dict。</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>落库 · 一列 JSON</h4><p>整块配置塞进 <span class="mono">impl=JSON</span> 那一格，关系 schema 保持扁平。</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>读 · process_result_value</h4><p>dict → <span class="mono">Model(**data)</span>，还原成 pydantic。</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>schema-on-read 兜底</h4><p><span class="mono">deserialize_llm_config</span> 给缺失字段填默认——加字段<strong>免迁移</strong>。</p></div></div>
</div>
<p>这批 <span class="mono">TypeDecorator</span> 都继承同一套骨架（<span class="mono">cache_ok=True</span>，委托 <span class="mono">helpers/converters.py</span> 做真正的转换）。挑两个最有代表性的看代码：</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/custom_columns.py</span><span class="ln">两类 TypeDecorator：配置存 JSON、向量存 BINARY（节选）</span></div>
<pre><span class="kw">class</span> <span class="fn">EmbeddingConfigColumn</span>(TypeDecorator):
    impl = JSON                          <span class="cm"># 底层就是一列 JSON</span>
    cache_ok = <span class="kw">True</span>
    <span class="kw">def</span> <span class="fn">process_bind_param</span>(self, value, _):      <span class="cm"># 写：pydantic -&gt; dict</span>
        <span class="kw">return</span> value.<span class="fn">model_dump</span>(mode=<span class="st">&quot;json&quot;</span>) <span class="kw">if</span> value <span class="kw">else</span> value
    <span class="kw">def</span> <span class="fn">process_result_value</span>(self, value, _):    <span class="cm"># 读：dict -&gt; pydantic</span>
        <span class="kw">return</span> <span class="fn">EmbeddingConfig</span>(**value) <span class="kw">if</span> value <span class="kw">else</span> value

<span class="kw">class</span> <span class="fn">CommonVector</span>(TypeDecorator):
    impl = BINARY                        <span class="cm"># 向量打包成二进制</span>
    cache_ok = <span class="kw">True</span>
    <span class="kw">def</span> <span class="fn">process_bind_param</span>(self, value, _):
        <span class="kw">return</span> <span class="fn">serialize_vector</span>(value)           <span class="cm"># sqlite_vec.serialize_float32</span>
    <span class="kw">def</span> <span class="fn">process_result_value</span>(self, value, _):
        <span class="kw">return</span> <span class="fn">deserialize_vector</span>(value)         <span class="cm"># np.frombuffer</span>
</pre></div>
<p>两个类一个模子：<span class="mono">bind</span> 管"进库怎么打包"，<span class="mono">result</span> 管"出库怎么还原"。<span class="mono">EmbeddingConfigColumn</span> 走 JSON，<span class="mono">CommonVector</span> 走 BINARY——后者正是上文 SQLite 那列向量的真身。</p>
<p>而 <span class="mono">impl=JSON</span> 在两套库上也各有落地：Postgres 用原生 <span class="mono">JSONB</span>，SQLite 把 JSON 存成文本。但这对上层完全透明——你拿到的永远是还原好的 pydantic 对象。</p>
<p>有意思的是 <span class="mono">CommonVector</span> 只<strong>借用</strong>了 <span class="mono">sqlite_vec.serialize_float32</span> 来打包字节，并没有用它的原生相似度。还记得吗？<span class="mono">sqlite_vec.load()</span> 是注释掉的。</p>
<p>顺带认全这家族：<span class="mono">impl=JSON</span> 那一脉有 <span class="mono">EmbeddingConfigColumn</span>、<span class="mono">LLMConfigColumn</span>、<span class="mono">ToolRulesColumn</span> 三个，套路一致；<span class="mono">CommonVector</span> 是 <span class="mono">impl=BINARY</span> 的独苗。</p>
<p>其中 <span class="mono">deserialize_llm_config</span> 多做一步：读出来若缺新字段，就<strong>就地补默认</strong>再构造 pydantic。这正是 schema-on-read——老数据不必迁移，读时顺手"升级"。</p>
<details class="accordion"><summary>把配置塞进一列 JSON，是聪明还是偷懒？取舍在哪？</summary><div class="acc-body">
<p>买到两样东西。其一<strong>免迁移</strong>：给 <span class="mono">LLMConfig</span> 加个 pydantic 字段，不用动表结构——老行反序列化时 <span class="mono">deserialize_llm_config</span> 自动补默认（schema-on-read）。</p>
<p>其二<strong>保真</strong>：整个 pydantic 对象原样进、原样出，嵌套结构不被拍平成一堆列，读回来还是那个强类型对象。</p>
<p>代价也实在：JSON 里的子字段<strong>不能 <span class="mono">WHERE</span>、不能建索引</strong>——你没法高效地"按 embedding 模型名筛选"。而且每次读写都要跑一遍 (de)序列化，有 CPU 开销。</p>
<p>一句话取舍：<strong>用"不可查询子字段 + 序列化开销"，换"扁平 schema + 加字段免迁移 + 配置保真"</strong>。对 Letta 这种配置多变、又很少按子字段查询的场景，划算。</p>
</div></details>
<h2>alembic：两套迁移，怎么不打架</h2>
<p>列类型、向量、配置都说清了，最后一处接缝是<strong>建表与迁移</strong>。两套库的 schema 怎么各自立起来、又不互相踩？答案在 <span class="mono">alembic/env.py</span>。</p>
<p><span class="mono">env.py</span> 先按 <span class="mono">database_engine</span> 选 URI：Postgres 用 pg8000 同步 URI，SQLite 用 <span class="mono">sqlite:///…sqlite.db</span>。建表策略则一边一个套路。</p>
<p><strong>Postgres</strong> 走一条<strong>增量链</strong>：从 <span class="mono">9a505cc7eca9</span> 起一版版往上叠。早期迁移还带门禁——<span class="mono">if not settings.letta_pg_uri_no_default: return</span>，没配 PG 就跳过。</p>
<p><strong>SQLite</strong> 则是<strong>单个 baseline 快照</strong> <span class="mono">2c059cad97cc</span>：一个反向门禁 <span class="mono">if settings.letta_pg_uri_no_default: return</span>，用纯 <span class="mono">sa.JSON()</span> 一次性把整套 schema 建出来。</p>
<p>baseline 之后的迁移<strong>两边都跑</strong>，方言差异在脚本里<strong>内联处理</strong>——比如时间默认值，Postgres 用 <span class="mono">now()</span>，SQLite 用 <span class="mono">CURRENT_TIMESTAMP</span>。</p>
<p>这套设计的红利是 dev 体验：开发者装好后不配任何 PG，直接拿 SQLite 起一个本地库；要上生产，配上 PG URI，同一套迁移自动走 Postgres 的增量链。<strong>一份代码，两种部署</strong>。</p>
<details class="accordion"><summary>一套 alembic 怎么同时伺候两套库？baseline 和增量链什么关系？</summary><div class="acc-body">
<p>靠两道<strong>方向相反的门禁</strong>。Postgres 早期迁移：<span class="mono">if not letta_pg_uri_no_default: return</span>——没配 PG 就整段跳过；SQLite baseline：<span class="mono">if letta_pg_uri_no_default: return</span>——配了 PG 反而跳过。</p>
<p>于是同一次 <span class="mono">upgrade</span>，Postgres 那侧顺着 <span class="mono">9a505cc7eca9</span> 的增量链一版版建；SQLite 那侧只认 baseline <span class="mono">2c059cad97cc</span>，用纯 <span class="mono">sa.JSON()</span> 一把建全。</p>
<p>baseline <strong>之后</strong>新增的迁移没有门禁，<strong>两库都执行</strong>；遇到方言差异（<span class="mono">now()</span> vs <span class="mono">CURRENT_TIMESTAMP</span>、类型名等）就在脚本里按 dialect 内联分叉。</p>
<p>所以 SQLite 不必重放 Postgres 那条长长的历史——它直接从一张"今日全貌"的快照起步，再跟上后续增量。两条起跑线，同一条终点。</p>
</div></details>
<h2>诚实的星号：为什么 v0.16.8 的 db.py 只建 Postgres</h2>
<p>本课开头就埋了伏笔：双库画得这么对称，可 <span class="mono">server/db.py</span> 模块级<strong>只</strong> <span class="mono">create_async_engine(async_pg_uri)</span>，根本不按 <span class="mono">database_engine</span> 建 SQLite 引擎。这不矛盾吗？</p>
<p>不矛盾，而是<strong>分层收敛</strong>。双库的故事完整活在<strong>两层</strong>：ORM 的列类型（<span class="mono">Vector</span> vs <span class="mono">CommonVector</span>）、alembic 的两后端建表。这两层至今仍是货真价实的双轨。</p>
<p>真正悄悄收敛到 Postgres 的，只是<strong>运行期那条 async 引擎</strong>。换句话说，"声明层"还双着，"连接层"先一步统一了。唯一还构造 SQLite URI 的地方，是 <span class="mono">alembic/env.py</span>。</p>
<p>对你读码的实际影响：想确认"当前进程在用哪套库"，别去翻 <span class="mono">db.py</span>（那里永远 Postgres），而要看 <span class="mono">settings.database_engine</span> 的取值——它才是 ORM 列类型与迁移路径的真正依据。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">这其实是个很好的教学点：<strong>读架构别只盯一个文件</strong>。只看 <span class="mono">db.py</span>，你会以为 Letta 只支持 Postgres；只看 ORM 与 alembic，你又会以为运行期能随意切 SQLite。真相是分层的——不同层处在收敛的不同阶段。</span></div>
<div class="card spark"><div class="tag">💡 设计亮点</div>
<p>"同一套代码两套库"最反直觉的一点：<strong>根本没有一个 <span class="mono">db.py</span> 里的聪明 switch</strong>。接缝是<strong>分布式且大多声明式</strong>的。</p>
<p>数一数就五六处：一个派生的 <span class="mono">database_engine</span> property；一句<strong>类体 <span class="mono">if</span> 把 embedding 列类型在 import 期烤进模型</strong>（所以一个进程被特化到一种后端、运行时不能切库）；查询构造器里两行 <span class="mono">order_by</span> 分支；一个全局 <span class="mono">@event.listens_for</span> 往任何 SQLite 连接注入 numpy <span class="mono">cosine_distance</span>；外加 <span class="mono">alembic/env.py</span> 选 URI。</p>
<p>pydantic-in-DB 是另一半魔术：配置当 JSON blob、schema-on-read 演化，<strong>保真胜过范式化</strong>。</p>
<p>而安静的拱顶石是 <span class="mono">MAX_EMBEDDING_DIM=4096</span>：把每个 embedding 零填充到定长，一个 <span class="mono">Vector(4096)</span> 列就能装任意模型的输出；又因等量补 0 不改点积与 L2 范数，<strong>cosine 排序与未填充数学等价</strong>。</p>
</div>
<div class="card warn"><div class="tag">⚠️ 常见误区</div>
<p><span class="mono">server/db.py</span> <strong>不</strong>按后端分叉：v0.16.8 它是 <strong>Postgres-only async</strong>，别在这找 SQLite 引擎或 sqlite-vec 加载。</p>
<p><span class="mono">database_engine</span> 是 <span class="mono">@property</span>，由"<strong>有没有配 PG URI</strong>"决定，<strong>没有 <span class="mono">LETTA_DATABASE_ENGINE</span></strong> 这种环境变量。</p>
<p>SQLite 的相似度是 <strong>numpy UDF，不是 sqlite-vec 原生</strong>——<span class="mono">sqlite_vec.load()</span> 是注释掉的，只借了它的 <span class="mono">serialize_float32</span>。</p>
<p>没有 <span class="mono">AgentPassage</span> 这个 ORM 类：只有 <span class="mono">SourcePassage</span> 与 <span class="mono">ArchivalPassage</span>，都继承 <span class="mono">BasePassage</span>。</p>
<p>列类型在 <strong>import 期定死</strong>，一个进程运行时<strong>不能切库</strong>；还有——填充让不同模型的向量<strong>可存进同一列</strong>，但不等于它们跨模型<strong>可比</strong>。</p>
</div>
<h2>回扣与铺垫：一套 ORM 两套库，装下整座记忆</h2>
<p>把第七部分收个尾。这四课其实是<strong>从骨架到向量</strong>的一条线：</p>
<div class="cellgroup"><div class="cg-cap"><b>第七部分四课连起来：从骨架到向量</b></div><div class="cells"><span class="cell">24 三层架构</span><span class="sep">→</span><span class="cell">25 服务层 Managers</span><span class="sep">→</span><span class="cell">26 CRUD / 隔离</span><span class="sep">→</span><span class="cell hl">27 双库 / 向量</span></div></div>
<p>一句话串起来：<strong>分层立骨架（24）→ manager 管事务与转换（25）→ 一个 base 默认安全（26）→ 一套 ORM 两套库装下记忆的向量（27）</strong>。</p>
<p>回指第 03 课：你追过的消息生命周期，最终"持久化的那一端"就落在这层引擎与列上。</p>
<p>回指第 10、11 课：archival / recall 的那些向量，存的就是这里的 <span class="mono">Passage</span>——<span class="mono">SourcePassage</span> 与 <span class="mono">ArchivalPassage</span>，搜索就是本课的两条路。</p>
<p>也回指第 21 课：<span class="mono">LLMConfig</span> / <span class="mono">EmbeddingConfig</span> 经 <span class="mono">custom_columns</span> 的 JSON 列落库——你配的模型参数，就这么躺在一格 JSON 里。</p>
<div class="note info"><span class="ni">💡</span><span class="nx">一句话收束：<strong>一套 ORM、一个 property 开关、两套库</strong>——pgvector 的原生 <span class="mono">&lt;=&gt;</span> 与 SQLite 的 numpy UDF 各搜各的，定长 4096 让任意模型的向量同住一列，pydantic-in-DB 让配置免迁移地演化。记忆的向量，就这样被两套库稳稳装下。</span></div>
<div class="card key"><div class="tag">✅ 本课要点</div>
<ul>
<li><strong>一个开关</strong>：<span class="mono">settings.database_engine</span> 是<strong>派生 @property</strong>——配了 PG URI（<span class="mono">letta_pg_uri_no_default</span> 非 None）走 Postgres，否则 SQLite；<strong>没有 <span class="mono">LETTA_DATABASE_ENGINE</span></strong>。</li>
<li><strong>接缝分布在六处、大多声明式</strong>：property、<span class="mono">BasePassage</span> import 期列类型 <span class="mono">if</span>、查询两路 <span class="mono">order_by</span>、<span class="mono">register_functions</span> 的 numpy UDF、<span class="mono">custom_columns</span>、<span class="mono">alembic/env.py</span>。</li>
<li><strong>向量两存两搜</strong>：Postgres ＝ <span class="mono">Vector(4096)</span> + 原生 <span class="mono">&lt;=&gt;</span>（可 ANN 索引）；SQLite ＝ <span class="mono">CommonVector</span> BINARY + numpy UDF 全表暴力。所有向量 <span class="mono">np.pad</span> 到 <span class="mono">MAX_EMBEDDING_DIM=4096</span>，<strong>补 0 不改 cosine</strong>。</li>
<li><strong>pydantic-in-DB</strong>：<span class="mono">TypeDecorator</span> 把 <span class="mono">EmbeddingConfig</span> / <span class="mono">LLMConfig</span> 整块 <span class="mono">model_dump</span> 成 JSON 存一列；schema-on-read 加字段免迁移，代价是子字段不可索引 + 序列化开销。</li>
<li><strong>诚实星号</strong>：v0.16.8 <span class="mono">server/db.py</span> 只建 Postgres async 引擎；双库故事完整活在 ORM 列类型与 alembic 两后端里。</li>
</ul>
</div>
<p>第七部分到此完整：从三层架构，到 manager、到 secure-by-default 的 base、再到双库与向量。服务端怎么把"一个 agent 的记忆"安全地存下、又精准地取回，你已看穿整条链路。</p>
<p>接下来是<strong>第八部分</strong>：进阶专题与术语表。我们会挑几个横切全局的主题深挖，再用一份术语表把这一路的关键词收拢成可随时回查的索引。</p>
""",
    "en": r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted)">Last lesson, in the third-floor archive, we saw how <span class="mono">SqlalchemyBase</span> welds isolation, soft delete and audit into every SQL statement. But which database that SQL finally lands in, and which engine runs it, we waved past with a single phrase — "down to the engine room at the bottom."</p>
<p class="lead" style="font-size:1.06rem;color:var(--muted)">This lesson pushes that engine-room door open: how does one set of ORM models run on both SQLite and Postgres? And how are vectors stored and searched in each? The answer isn't some clever <span class="mono">db.py</span> — it's a seam <strong>scattered across six places, most of it declarative</strong>.</p>
<div class="card macro"><div class="tag">🌍 The big picture</div>
<p>Catch this lesson in one line: <strong>one set of ORM models runs on two databases by one switch; vectors are stored two ways and searched two ways; configs get stuffed whole into a column as a JSON blob</strong>.</p>
<p>The switch = <span class="mono">settings.database_engine</span>: configure a Postgres URI and you're on Postgres, otherwise SQLite.</p>
<p>Two vector paths: Postgres uses pgvector's <span class="mono">Vector(4096)</span> + the native operator <span class="mono">&lt;=&gt;</span>; SQLite uses a BINARY blob + a numpy <span class="mono">cosine_distance</span> brute-forced over the whole table.</p>
<p>pydantic-in-DB: configs like <span class="mono">EmbeddingConfig</span> / <span class="mono">LLMConfig</span> aren't split into columns — the whole thing is <span class="mono">model_dump</span>ed to JSON and stored in one cell.</p>
<p>One honest caveat: v0.16.8's <span class="mono">server/db.py</span> actually only builds Postgres — the dual-DB story lives fully in the ORM and alembic layers.</p>
</div>
<p>This is not one big "if backend == sqlite" switch. The real seam is <strong>distributed across six places</strong>, most of it declared at import time rather than decided on the fly at runtime.</p>
<p>Pull the camera back first: Lesson 24 looked at the three-layer architecture, Lesson 25 at managers opening transactions, Lesson 26 at how each row is isolated. This lesson goes to the very bottom — which database these rows <strong>land in, and how vectors get searched out</strong>.</p>
<p>A quick inoculation too: this lesson cures a few "taking it for granted" assumptions. For instance, <span class="mono">db.py</span> doesn't branch by backend, <span class="mono">database_engine</span> isn't a field you can set by hand, and SQLite's similarity isn't sqlite-vec native — we puncture each below.</p>
<h2>One ORM, two engines: swap the parts, not the blueprint</h2>
<p>Start with the panorama. The ~40 models under <span class="mono">letta/orm/</span> are written <strong>once</strong>; which database they land in is decided by one switch, <span class="mono">settings.database_engine</span>. Two tracks side by side make it clearest:</p>
<div class="cols">
  <div class="col"><h4>🪶 SQLite · dev default</h4>
  <p>Driver: <span class="mono">aiosqlite</span> (async).</p>
  <p>Vector column: <span class="mono">CommonVector</span>, a BINARY blob.</p>
  <p>Distance: <span class="mono">func.cosine_distance</span>, via a numpy UDF.</p>
  <p>Search: <span class="mono">ORDER BY</span> brute-force over the whole table, no ANN.</p>
  <p>Migration: a single baseline snapshot <span class="mono">2c059cad97cc</span>.</p>
  </div>
  <div class="col"><h4>🐘 Postgres · production</h4>
  <p>Driver: <span class="mono">asyncpg</span> (async).</p>
  <p>Vector column: pgvector's <span class="mono">Vector(4096)</span>.</p>
  <p>Distance: <span class="mono">cosine_distance()</span> → SQL <span class="mono">&lt;=&gt;</span>.</p>
  <p>Search: can attach an <span class="mono">ivfflat</span> / <span class="mono">hnsw</span> index.</p>
  <p>Migration: an incremental chain from <span class="mono">9a505cc7eca9</span>.</p>
  </div>
</div>
<p>See the trick? The two tracks are <strong>identically shaped</strong>; only the parts get swapped: driver, vector column type, distance operator, serialization, migration path, and "whether to pad vectors to a fixed length."</p>
<p>Don't overlook the long list that <strong>isn't</strong> swapped either: table names, column names, relationships, constraints, <span class="mono">SqlalchemyBase</span>'s isolation and audit, the managers' transaction boundaries — all from <strong>one set of models</strong>, identical on both databases. Switching DBs only moves a thin layer next to storage.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">An honest asterisk: the table above paints the "dual DB" very symmetrically, but v0.16.8's <span class="mono">server/db.py</span> only builds a <strong>Postgres async engine</strong> at module level. The full dual-DB story lives in the ORM column types and the alembic migrations; the runtime engine layer has quietly converged on Postgres — the "honest asterisk" at the end of this lesson explains why.</span></div>
<div class="card analogy"><div class="tag">🏭 An everyday analogy</div>
<p>Picture this design as <strong>one blueprint, two factories</strong>. The blueprint = the ORM models, drawing "which tables, which columns, how they relate" — <strong>one copy, unchanging</strong>.</p>
<p>The two factories = the SQLite plant and the Postgres plant. The same blueprint goes to both; following the switch on the wall (<span class="mono">database_engine</span>), the assembly line swaps in different parts.</p>
<p>The swapped parts are concrete: which material the vector column uses (pgvector's fixed-length slot vs a BINARY bag), which machine computes distance (the native <span class="mono">&lt;=&gt;</span> vs numpy by hand), which line the migration runs down.</p>
<p>The beauty: the workers (people writing new features) only read the blueprint — they needn't know which plant runs today; coding against the models is enough, and both databases can build it.</p>
</div>
<p>This "blueprint fixed, parts swappable" design is exactly what the following sections take apart one by one: first the switch, then swapping the column type, the distance operator, the migration path.</p>
<h2>The only switch: database_engine is really a property</h2>
<p>"Two databases" sounds like it should come with an enum to pick from. But open <span class="mono">settings.py</span> and you'll do a double take: <span class="mono">database_engine</span> <strong>isn't a field at all</strong> — it's a read-only <span class="mono">@property</span>.</p>
<p>Its logic fits on one line: <span class="mono">POSTGRES if self.letta_pg_uri_no_default else SQLITE</span>. In other words, <strong>whether a Postgres URI is configured</strong> is the entire dev/prod dividing line.</p>
<div class="flow">
  <div class="node hl"><div class="nt">settings.database_engine</div><div class="nd">a @property, not a field</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">check letta_pg_uri_no_default</div><div class="nd">a URI or None</div></div>
  <div class="arrow">-&gt;</div>
  <div class="node"><div class="nt">not None → POSTGRES</div><div class="nd">else → SQLITE</div></div>
</div>
<p>Note the trap here: <span class="mono">letta_pg_uri</span> <strong>always</strong> has a default, so the decision can't read it; the real "URI-or-None" is <span class="mono">letta_pg_uri_no_default</span>.</p>
<p><span class="mono">DatabaseChoice</span> is a <span class="mono">(str, Enum)</span> with only two values, <span class="mono">POSTGRES</span> / <span class="mono">SQLITE</span>. It's a conclusion <strong>read out</strong>, not a choice you write in.</p>
<p>That default URI also reveals the driver: <span class="mono">postgresql+pg8000://…</span> — the sync path uses pg8000, while the async engine switches to asyncpg. It's assembled from a set of <span class="mono">LETTA_PG_HOST / DB / USER / PASSWORD / PORT</span>, or you give the whole <span class="mono">LETTA_PG_URI</span> directly.</p>
<p>Where is the engine itself built? This is the first counterintuitive spot:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/server/db.py · letta/orm/sqlite_functions.py</span><span class="ln">engine only builds Postgres; attach a numpy UDF to any SQLite connection (excerpt)</span></div>
<pre><span class="cm"># server/db.py: at module level there's only one async engine — Postgres-only</span>
engine = <span class="fn">create_async_engine</span>(async_pg_uri, ...)   <span class="cm"># no branch on database_engine, no sqlite-vec loaded here</span>

<span class="cm"># orm/sqlite_functions.py: the moment any SQLite connection is made, attach the numpy distance function</span>
<span class="nb">@event.listens_for(Engine, &quot;connect&quot;)</span>
<span class="kw">def</span> <span class="fn">register_functions</span>(dbapi_conn, _):
    <span class="kw">if</span> <span class="fn">isinstance</span>(dbapi_conn, sqlite3.Connection):
        dbapi_conn.<span class="fn">create_function</span>(<span class="st">&quot;cosine_distance&quot;</span>, 2, cosine_distance)  <span class="cm"># pure numpy impl</span>
        <span class="cm"># sqlite_vec.load(dbapi_conn)  ← commented out: no sqlite-vec native similarity</span>
</pre></div>
<p>Read the two snippets together: on the left, <span class="mono">db.py</span>'s engine is Postgres-only; on the right, that global <span class="mono">@event.listens_for</span> is the actual SQLite seam — it registers a numpy <span class="mono">cosine_distance</span> for <strong>any</strong> SQLite connection.</p>
<p>Note the last comment line: <span class="mono">sqlite_vec.load()</span> is <strong>commented out</strong>. SQLite's similarity rides on a pure numpy UDF, not a sqlite-vec native operator — a correction we'll stress again later.</p>
<p>This <span class="mono">@event.listens_for(Engine, "connect")</span> is <strong>global</strong>: whichever SQLite connection it is — dev DB, test DB, a throwaway in-memory one — the UDF attaches the moment it's made. So "SQLite can compute cosine" is a connection-level fait accompli, with no per-site opt-in needed.</p>
<div class="card detail"><div class="tag">🔬 Down to the code</div>
<p><span class="mono">settings.py::Settings.database_engine</span> — a <span class="mono">@property</span>: <span class="mono">POSTGRES if self.letta_pg_uri_no_default else SQLITE</span>; <span class="mono">DatabaseChoice(str, Enum){POSTGRES, SQLITE}</span>.</p>
<p><span class="mono">orm/passage.py::BasePassage</span> — at import time, the embedding column type is fixed by <span class="mono">database_engine</span>.</p>
<p><span class="mono">orm/custom_columns.py</span> — a batch of pydantic-in-DB <span class="mono">TypeDecorator</span>s; <span class="mono">orm/sqlite_functions.py::register_functions</span> — SQLite's numpy <span class="mono">cosine_distance</span>.</p>
<p><span class="mono">constants.py::MAX_EMBEDDING_DIM = 4096</span> — the ruler for fixed-length padding; <span class="mono">alembic/env.py</span> — picks the URI and builds tables for two backends.</p>
</div>
<details class="accordion"><summary>How exactly is <span class="mono">database_engine</span> decided? Can you pick SQLite by hand with an env var?</summary><div class="acc-body">
<p>You can't pick it directly. <span class="mono">database_engine</span> is a <strong>derived <span class="mono">@property</span></strong>, not a writable field: it only looks at whether <span class="mono">letta_pg_uri_no_default</span> is None.</p>
<p><span class="mono">letta_pg_uri</span> always has a default (<span class="mono">postgresql+pg8000://letta:letta@localhost:5432/letta</span>); the real "URI-or-None" is <span class="mono">letta_pg_uri_no_default</span>. Set it = Postgres, leave it = SQLite.</p>
<p>There's <strong>no <span class="mono">LETTA_DATABASE_ENGINE=sqlite</span></strong> switch. Set any <span class="mono">LETTA_PG_*</span> (host / db / user / password / port / uri) and it <strong>silently</strong> flips to Postgres.</p>
<p>So "SQLite in dev, Postgres in prod" isn't a manual toggle — it's a side effect of the single fact of <strong>whether you handed it PG connection info</strong>.</p>
</div></details>
<div class="note tip"><span class="ni">🧠</span><span class="nx">Want to force SQLite? Don't hunt for a switch — <strong>clear every <span class="mono">LETTA_PG_*</span> env var</strong>. As long as <span class="mono">letta_pg_uri_no_default</span> is None, <span class="mono">database_engine</span> falls back to SQLITE on its own. Conversely, if production "somehow isn't on Postgres," first check whether the PG URI was left unconfigured.</span></div>
<h2>How vectors are stored: cramming any dimension into one fixed-length 4096 column</h2>
<p>The archival / recall memory you met (Lessons 10, 11) is essentially a <span class="mono">Passage</span> carrying an embedding. But different models output wildly different dimensions: some 1024, some 1536, some 3072. How can one column hold them all?</p>
<p>Letta's answer is blunt: <span class="mono">constants.py::MAX_EMBEDDING_DIM = 4096</span> — every embedding is <span class="mono">np.pad</span>ded to 4096 dims on write and on query, <strong>zero-padded at the tail</strong>. So one <span class="mono">Vector(4096)</span> column holds any model's output.</p>
<p>Padding happens <strong>before the write</strong>: an embedding is <span class="mono">np.pad</span>ded to 4096 the moment it's generated, then handed to the ORM to persist; the query vector takes the same step before comparison. Both ends aligned, the fixed-length column can hold and compare them.</p>
<div class="cute"><div class="row"><span class="emoji">📐</span><span class="lab">fixed 4096-slot</span><span class="arrow">→</span><span class="emoji">🧮</span><span class="lab">a model's 1536 dims</span><span class="arrow">→</span><span class="emoji">0️⃣</span><span class="bubble">zero-pad the tail</span></div><div class="cap">📐 one column is a fixed 4096-dim slot; 🧮 a model outputs only 1536 dims; 0️⃣ zero-pad the tail to fill the slot — the padding is all zeros, so <strong>cosine ranking doesn't change at all</strong>, which is why one column holds any model's output</div></div>
<p>Wait — stuffing in a pile of zeros, won't it skew the similarity? That's exactly the clever part: <strong>zero-padding has no effect on cosine at all</strong>.</p>
<div class="cellgroup"><div class="cg-cap"><b>Why zero-padding is "free": cosine = dot / (L2 × L2), neither end moves</b></div><div class="cells"><span class="cell hl">dot +0×x=0</span><span class="sep">→</span><span class="cell">numerator unchanged</span><span class="sep">·</span><span class="cell">L2 +0²=0</span><span class="sep">→</span><span class="cell">denominator unchanged</span><span class="sep">⇒</span><span class="cell hl">cosine unchanged</span></div></div>
<p>The reasoning is plain. Cosine = dot product ÷ (the product of the two vectors' L2 norms). What's added is zeros: in the dot product <span class="mono">0 × anything = 0</span>, so the numerator is unchanged; in the L2 norm <span class="mono">0² = 0</span>, so the denominator is unchanged too. <strong>Neither numerator nor denominator moves, so the ranking is naturally identical</strong>.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">So "one fixed column fits any model" is not an approximation or a compromise — it's <strong>mathematically exactly equivalent to no padding</strong>, costing only an extra run of zeros and a little space. SQLite's numpy UDF <span class="mono">cosine_distance</span> first checks the dimension == 4096 via <span class="mono">validate_and_transform_embedding</span>, and (after catching the <span class="mono">ValueError</span>) returns <span class="mono">0.0</span> on a mismatch — padding is a <strong>shared precondition</strong> of both the write and query paths.</span></div>
<p>And "which column type"? This is the second of the six seams, happening in <span class="mono">BasePassage</span>'s <strong>class body, at import time</strong>: Postgres uses pgvector's <span class="mono">Vector(4096)</span>, SQLite uses <span class="mono">CommonVector</span> (a BINARY blob). The next section shows the code together with search.</p>
<div class="note warn"><span class="ni">⚠️</span><span class="nx"><span class="mono">MAX_EMBEDDING_DIM</span>'s comment spells it out — "don't change it, or you'll have to reset the database": it pins the column width, and once changed it no longer matches the fixed-length vectors already stored. This ruler is a <strong>global convention</strong>, not some table's local choice.</span></div>
<p>Fixed length isn't free of cost either: for a 1024-dim model, every row wastes 3072 stored zeros, a waste borne by both disk and memory. But what you get is <strong>one column for every model</strong>, with no per-dimension table — for a system that must support many embedding vendors, the math pays off.</p>
<h2>How vectors are searched: native &lt;=&gt; vs numpy brute force</h2>
<p>Storage settled, how do we search? This is the third of the six seams, and the only place that genuinely <strong>forks two ways at runtime</strong>: the same "order by similarity" compiles into completely different execution on the two databases.</p>
<p>Let's put the column type and the search branch in one code view — they actually share a single <span class="mono">if database_engine is POSTGRES</span>:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/passage.py · letta/orm/sqlalchemy_base.py</span><span class="ln">column type fixed at import time; search forks by engine at runtime (excerpt)</span></div>
<pre><span class="cm"># orm/passage.py::BasePassage — in the class body, import time bakes the column type into the model</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    embedding = <span class="fn">mapped_column</span>(<span class="fn">Vector</span>(MAX_EMBEDDING_DIM))   <span class="cm"># pgvector fixed-length 4096</span>
<span class="kw">else</span>:
    embedding = <span class="fn">Column</span>(CommonVector)                      <span class="cm"># SQLite: BINARY blob</span>

<span class="cm"># orm/sqlalchemy_base.py query builder: at runtime, the same switch forks the sort two ways</span>
<span class="kw">if</span> settings.database_engine <span class="kw">is</span> DatabaseChoice.POSTGRES:
    query = query.<span class="fn">order_by</span>(cls.embedding.<span class="fn">cosine_distance</span>(q_emb).<span class="fn">asc</span>())          <span class="cm"># compiles to SQL &lt;=&gt;</span>
<span class="kw">else</span>:
    query = query.<span class="fn">order_by</span>(<span class="fn">func.cosine_distance</span>(cls.embedding, q_emb).<span class="fn">asc</span>())   <span class="cm"># via numpy UDF</span>
</pre></div>
<p>See the two forks clearly: the top half is <strong>import-time</strong> — that <span class="mono">if</span> in the class body runs once when the module is imported, baking the column type onto the model. So a process is specialized to one backend and <strong>can't switch databases at runtime</strong>.</p>
<p>The bottom half is <strong>runtime</strong>: Postgres turns <span class="mono">cosine_distance()</span> into the native operator <span class="mono">&lt;=&gt;</span>, while SQLite calls that numpy UDF we saw in <span class="mono">register_functions</span>. Laying the whole picture out as a table:</p>
<table class="t">
<tr><th>Aspect</th><th>Postgres (pgvector)</th><th>SQLite</th></tr>
<tr><td>Vector column</td><td class="mono">Vector(4096)</td><td class="mono">CommonVector (BINARY)</td></tr>
<tr><td>Distance call</td><td class="mono">embedding.cosine_distance(q)</td><td class="mono">func.cosine_distance(col, q)</td></tr>
<tr><td>Actual operator</td><td>native SQL <span class="mono">&lt;=&gt;</span></td><td>Python numpy UDF</td></tr>
<tr><td>Sort</td><td class="mono">ORDER BY dist ASC</td><td class="mono">ORDER BY dist ASC</td></tr>
<tr><td>Index / ANN</td><td>can attach <span class="mono">ivfflat</span> / <span class="mono">hnsw</span></td><td>none, brute-force whole table</td></tr>
<tr><td>Scale fit</td><td>holds up even for large stores</td><td>small stores / dev is enough</td></tr>
</table>
<p>Both sides are <strong>semantically the same</strong> — both take the nearest few in ascending cosine order; the difference is only execution: Postgres can use an index for approximate nearest neighbor (ANN), SQLite computes row by row over the whole table and then sorts.</p>
<p>Some worry "brute-force over the whole table" is too slow. In dev and at small scale it actually isn't: computing cosine row by row over a few thousand to tens of thousands, numpy is vectorized and returns in a blink. ANN is only truly needed for production-scale massive memory — by then you should be on Postgres anyway.</p>
<p>These two branches don't only live in <span class="mono">sqlalchemy_base.py</span>'s generic query: <span class="mono">services/helpers/agent_manager_helper.py</span> carries the same <span class="mono">if POSTGRES</span> when assembling archival retrieval — the same fork, written once at each place that uses vector search.</p>
<p>This echoes Lessons 10, 11: the archival / recall retrieval you read about — its underlying "find the most similar memory" — splits into these two paths at this layer.</p>
<details class="accordion"><summary>How exactly are vectors stored and searched in each database? Where's the performance difference?</summary><div class="acc-body">
<p><strong>Storage</strong>: Postgres is pgvector's <span class="mono">Vector(4096)</span> fixed-length column; SQLite is <span class="mono">CommonVector</span> — a BINARY blob, packed with <span class="mono">sqlite_vec.serialize_float32</span> and restored with <span class="mono">np.frombuffer</span>.</p>
<p><strong>Search</strong>: Postgres compiles <span class="mono">cosine_distance()</span> into the native operator <span class="mono">&lt;=&gt;</span> and can do ANN via an <span class="mono">ivfflat</span> / <span class="mono">hnsw</span> index; SQLite calls a numpy UDF, computing distance row by row over the whole table and then sorting.</p>
<p>So the gap is about <strong>scale</strong>: at small size and in dev, SQLite's brute-force is no strain; once the row count grows, you need Postgres's vector index. Both sides are semantically the same — one just has ANN and the other doesn't.</p>
<p>Don't forget: both sides first <span class="mono">np.pad</span> the query vector to 4096 before comparing — padding is a shared precondition of storage and search, dropping "any model's vector" into one fixed-length space.</p>
</div></details>
<h2>pydantic-in-DB: stuffing a whole config into one JSON column</h2>
<p>The other half of the magic has nothing to do with vectors yet is just as elegant: configs like <span class="mono">EmbeddingConfig</span>, <span class="mono">LLMConfig</span>, <span class="mono">ToolRules</span> aren't split into columns — the whole thing is stored in one cell as a JSON blob.</p>
<p>In Lesson 21 you saw <span class="mono">LLMConfig</span> / <span class="mono">EmbeddingConfig</span> as pydantic models in memory. How do they persist? Through a batch of <span class="mono">TypeDecorator</span>s in <span class="mono">custom_columns.py</span> — SQLAlchemy's "column-type adapters."</p>
<p>It builds a two-way bridge between the ORM and the DB, with one conversion in each direction:</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>EmbeddingConfig (pydantic)</h4><p>In memory it's a pydantic model with types and defaults.</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>Write · process_bind_param</h4><p><span class="mono">model_dump(mode="json")</span> → a plain dict.</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>Persist · one JSON column</h4><p>the whole config goes into the <span class="mono">impl=JSON</span> cell; the relational schema stays flat.</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>Read · process_result_value</h4><p>dict → <span class="mono">Model(**data)</span>, restored to pydantic.</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>schema-on-read fallback</h4><p><span class="mono">deserialize_llm_config</span> fills defaults for missing fields — adding a field needs no migration.</p></div></div>
</div>
<p>These <span class="mono">TypeDecorator</span>s all inherit one skeleton (<span class="mono">cache_ok=True</span>, delegating the real conversion to <span class="mono">helpers/converters.py</span>). Let's read the two most representative ones:</p>
<div class="codefile"><div class="cf-head"><span class="dot"></span><span class="path">letta/orm/custom_columns.py</span><span class="ln">two kinds of TypeDecorator: config to JSON, vector to BINARY (excerpt)</span></div>
<pre><span class="kw">class</span> <span class="fn">EmbeddingConfigColumn</span>(TypeDecorator):
    impl = JSON                          <span class="cm"># underneath it's just a JSON column</span>
    cache_ok = <span class="kw">True</span>
    <span class="kw">def</span> <span class="fn">process_bind_param</span>(self, value, _):      <span class="cm"># write: pydantic -&gt; dict</span>
        <span class="kw">return</span> value.<span class="fn">model_dump</span>(mode=<span class="st">&quot;json&quot;</span>) <span class="kw">if</span> value <span class="kw">else</span> value
    <span class="kw">def</span> <span class="fn">process_result_value</span>(self, value, _):    <span class="cm"># read: dict -&gt; pydantic</span>
        <span class="kw">return</span> <span class="fn">EmbeddingConfig</span>(**value) <span class="kw">if</span> value <span class="kw">else</span> value

<span class="kw">class</span> <span class="fn">CommonVector</span>(TypeDecorator):
    impl = BINARY                        <span class="cm"># vector packed to binary</span>
    cache_ok = <span class="kw">True</span>
    <span class="kw">def</span> <span class="fn">process_bind_param</span>(self, value, _):
        <span class="kw">return</span> <span class="fn">serialize_vector</span>(value)           <span class="cm"># sqlite_vec.serialize_float32</span>
    <span class="kw">def</span> <span class="fn">process_result_value</span>(self, value, _):
        <span class="kw">return</span> <span class="fn">deserialize_vector</span>(value)         <span class="cm"># np.frombuffer</span>
</pre></div>
<p>Two classes from one mold: <span class="mono">bind</span> governs "how to pack on the way in," <span class="mono">result</span> governs "how to restore on the way out." <span class="mono">EmbeddingConfigColumn</span> goes JSON, <span class="mono">CommonVector</span> goes BINARY — the latter is exactly the true form of that SQLite vector column above.</p>
<p>And <span class="mono">impl=JSON</span> lands differently on each database too: Postgres uses native <span class="mono">JSONB</span>, SQLite stores JSON as text. But that's fully transparent to the upper layers — what you get is always a restored pydantic object.</p>
<p>Interestingly, <span class="mono">CommonVector</span> only <strong>borrows</strong> <span class="mono">sqlite_vec.serialize_float32</span> to pack bytes — it doesn't use its native similarity. Remember? <span class="mono">sqlite_vec.load()</span> is commented out.</p>
<p>While we're at it, meet the whole family: the <span class="mono">impl=JSON</span> line has three — <span class="mono">EmbeddingConfigColumn</span>, <span class="mono">LLMConfigColumn</span>, <span class="mono">ToolRulesColumn</span> — same pattern throughout; <span class="mono">CommonVector</span> is the lone <span class="mono">impl=BINARY</span> member.</p>
<p>Among them <span class="mono">deserialize_llm_config</span> does one extra step: if a new field is missing on read, it fills the default in place before constructing the pydantic object. That's exactly schema-on-read — old data needs no migration, "upgraded" on the fly as it's read.</p>
<details class="accordion"><summary>Stuffing a config into one JSON column — clever or lazy? Where's the trade-off?</summary><div class="acc-body">
<p>You buy two things. One, <strong>no migration</strong>: add a pydantic field to <span class="mono">LLMConfig</span> and you needn't touch the table schema — old rows get the default filled automatically by <span class="mono">deserialize_llm_config</span> on deserialization (schema-on-read).</p>
<p>Two, <strong>fidelity</strong>: the whole pydantic object goes in and comes out as-is; nested structure isn't flattened into a pile of columns, and it reads back as that same strongly-typed object.</p>
<p>The cost is real too: subfields inside the JSON <strong>can't be in a <span class="mono">WHERE</span> or indexed</strong> — you can't efficiently "filter by embedding model name." And every read/write runs a round of (de)serialization, a CPU cost.</p>
<p>The trade-off in one line: trade "non-queryable subfields + serialization overhead" for "flat schema + add-field-without-migration + config fidelity." For Letta's case — configs that change a lot and are rarely queried by subfield — it pays off.</p>
</div></details>
<h2>alembic: two migration sets that don't clash</h2>
<p>Column types, vectors and configs are all clear now; the last seam is <strong>table creation and migration</strong>. How do the two databases' schemas each stand up without stepping on each other? The answer is in <span class="mono">alembic/env.py</span>.</p>
<p><span class="mono">env.py</span> first picks the URI by <span class="mono">database_engine</span>: Postgres uses a pg8000 sync URI, SQLite uses <span class="mono">sqlite:///…sqlite.db</span>. The table-building strategy then differs on each side.</p>
<p><strong>Postgres</strong> follows an <strong>incremental chain</strong>: stacking version on version from <span class="mono">9a505cc7eca9</span>. Early migrations even carry a gate — <span class="mono">if not settings.letta_pg_uri_no_default: return</span> — skipping when no PG is configured.</p>
<p><strong>SQLite</strong> is a <strong>single baseline snapshot</strong> <span class="mono">2c059cad97cc</span>: a reverse gate <span class="mono">if settings.letta_pg_uri_no_default: return</span>, building the entire schema in one shot with plain <span class="mono">sa.JSON()</span>.</p>
<p>Migrations after the baseline <strong>run on both sides</strong>, with dialect differences handled <strong>inline</strong> in the scripts — for example a time default: Postgres uses <span class="mono">now()</span>, SQLite uses <span class="mono">CURRENT_TIMESTAMP</span>.</p>
<p>The payoff of this design is dev experience: after install a developer configures no PG and spins up a local DB on SQLite directly; to go to production, configure a PG URI and the same migrations automatically run Postgres's incremental chain. <strong>One codebase, two deployments</strong>.</p>
<details class="accordion"><summary>How does one alembic serve both databases at once? What's the relationship between the baseline and the incremental chain?</summary><div class="acc-body">
<p>Through two <strong>oppositely-directed gates</strong>. The early Postgres migrations: <span class="mono">if not letta_pg_uri_no_default: return</span> — skip the whole block when no PG is configured; the SQLite baseline: <span class="mono">if letta_pg_uri_no_default: return</span> — skip precisely when PG is configured.</p>
<p>So in one <span class="mono">upgrade</span>, the Postgres side builds version by version along the <span class="mono">9a505cc7eca9</span> incremental chain; the SQLite side recognizes only the baseline <span class="mono">2c059cad97cc</span>, building everything at once with plain <span class="mono">sa.JSON()</span>.</p>
<p>Migrations added <strong>after</strong> the baseline have no gate and <strong>run on both</strong>; where dialects differ (<span class="mono">now()</span> vs <span class="mono">CURRENT_TIMESTAMP</span>, type names, etc.) the script forks inline by dialect.</p>
<p>So SQLite needn't replay Postgres's long history — it starts straight from a "today's full picture" snapshot and then keeps up with later increments. Two starting lines, one finish line.</p>
</div></details>
<h2>The honest asterisk: why v0.16.8's db.py only builds Postgres</h2>
<p>We planted this at the start: the dual DB is painted so symmetrically, yet <span class="mono">server/db.py</span> at module level <strong>only</strong> does <span class="mono">create_async_engine(async_pg_uri)</span>, never building a SQLite engine by <span class="mono">database_engine</span>. Isn't that a contradiction?</p>
<p>No contradiction — it's <strong>layered convergence</strong>. The dual-DB story lives fully in <strong>two layers</strong>: the ORM column types (<span class="mono">Vector</span> vs <span class="mono">CommonVector</span>) and alembic's two-backend table building. Those two layers are still genuinely dual-track today.</p>
<p>What has quietly converged on Postgres is only the <strong>runtime async engine</strong>. In other words, the "declaration layer" is still dual, while the "connection layer" unified one step ahead. The only place that still builds a SQLite URI is <span class="mono">alembic/env.py</span>.</p>
<p>The practical impact on your code reading: to confirm "which database the current process uses," don't flip through <span class="mono">db.py</span> (always Postgres there) — look at the value of <span class="mono">settings.database_engine</span>, which is the real basis for the ORM column type and migration path.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">This is actually a fine teaching point: <strong>don't read architecture by staring at one file</strong>. Look only at <span class="mono">db.py</span> and you'd think Letta only supports Postgres; look only at the ORM and alembic and you'd think you can freely switch to SQLite at runtime. The truth is layered — different layers sit at different stages of convergence.</span></div>
<div class="card spark"><div class="tag">💡 Design highlight</div>
<p>The most counterintuitive thing about "one codebase, two databases": there's <strong>no clever switch inside <span class="mono">db.py</span> at all</strong>. The seam is <strong>distributed and mostly declarative</strong>.</p>
<p>Count them and it's five or six places: a derived <span class="mono">database_engine</span> property; a <strong>class-body <span class="mono">if</span> that bakes the embedding column type into the model at import time</strong> (so a process is specialized to one backend and can't switch at runtime); two <span class="mono">order_by</span> branch lines in the query builder; a global <span class="mono">@event.listens_for</span> injecting a numpy <span class="mono">cosine_distance</span> into any SQLite connection; plus <span class="mono">alembic/env.py</span> picking the URI.</p>
<p>pydantic-in-DB is the other half of the magic: config as a JSON blob, schema-on-read evolution — <strong>fidelity over normalization</strong>.</p>
<p>And the quiet keystone is <span class="mono">MAX_EMBEDDING_DIM=4096</span>: zero-pad every embedding to a fixed length and one <span class="mono">Vector(4096)</span> column holds any model's output; and because equal zero-padding doesn't change the dot product or the L2 norm, <strong>cosine ranking is mathematically equivalent to the unpadded vector</strong>.</p>
</div>
<div class="card warn"><div class="tag">⚠️ Common pitfalls</div>
<p><span class="mono">server/db.py</span> does <strong>not</strong> branch by backend: in v0.16.8 it's <strong>Postgres-only async</strong> — don't look here for a SQLite engine or sqlite-vec loading.</p>
<p><span class="mono">database_engine</span> is a <span class="mono">@property</span>, decided by "<strong>whether a PG URI is configured</strong>" — there's <strong>no <span class="mono">LETTA_DATABASE_ENGINE</span></strong> env var.</p>
<p>SQLite's similarity is a <strong>numpy UDF, not sqlite-vec native</strong> — <span class="mono">sqlite_vec.load()</span> is commented out; only its <span class="mono">serialize_float32</span> is borrowed.</p>
<p>There's no <span class="mono">AgentPassage</span> ORM class: only <span class="mono">SourcePassage</span> and <span class="mono">ArchivalPassage</span>, both inheriting <span class="mono">BasePassage</span>.</p>
<p>The column type is fixed <strong>at import time</strong>, so a process <strong>can't switch databases at runtime</strong>; and — padding lets different models' vectors <strong>be stored in one column</strong>, but that doesn't make them <strong>comparable across models</strong>.</p>
</div>
<h2>Looking back, looking ahead: one ORM, two databases, holding the whole memory</h2>
<p>Let's wrap up Part 7. These four lessons are really one line <strong>from skeleton to vector</strong>:</p>
<div class="cellgroup"><div class="cg-cap"><b>Part 7's four lessons strung together: from skeleton to vector</b></div><div class="cells"><span class="cell">24 three layers</span><span class="sep">→</span><span class="cell">25 service-layer Managers</span><span class="sep">→</span><span class="cell">26 CRUD / isolation</span><span class="sep">→</span><span class="cell hl">27 dual DB / vectors</span></div></div>
<p>Strung into one line: <strong>layers raise the skeleton (24) → managers handle transactions and conversion (25) → one base is secure by default (26) → one ORM on two databases holds memory's vectors (27)</strong>.</p>
<p>Pointing back to Lesson 03: the message lifecycle you traced — its "persistence end" finally lands on this layer of engine and columns.</p>
<p>Pointing back to Lessons 10, 11: those archival / recall vectors are stored as this layer's <span class="mono">Passage</span> — <span class="mono">SourcePassage</span> and <span class="mono">ArchivalPassage</span> — and the search is this lesson's two paths.</p>
<p>And pointing back to Lesson 21: <span class="mono">LLMConfig</span> / <span class="mono">EmbeddingConfig</span> persist through <span class="mono">custom_columns</span>' JSON column — the model parameters you set lie right there in one JSON cell.</p>
<div class="note info"><span class="ni">💡</span><span class="nx">To close in one line: <strong>one ORM, one property switch, two databases</strong> — pgvector's native <span class="mono">&lt;=&gt;</span> and SQLite's numpy UDF each search their own way, a fixed-length 4096 lets any model's vector share one column, and pydantic-in-DB lets configs evolve without migration. Memory's vectors are held steadily by both databases, just like this.</span></div>
<div class="card key"><div class="tag">✅ Key points</div>
<ul>
<li><strong>One switch</strong>: <span class="mono">settings.database_engine</span> is a <strong>derived @property</strong> — a configured PG URI (<span class="mono">letta_pg_uri_no_default</span> not None) goes Postgres, else SQLite; <strong>no <span class="mono">LETTA_DATABASE_ENGINE</span></strong>.</li>
<li><strong>The seam is distributed across six places, mostly declarative</strong>: the property, <span class="mono">BasePassage</span>'s import-time column-type <span class="mono">if</span>, the two-way query <span class="mono">order_by</span>, <span class="mono">register_functions</span>' numpy UDF, <span class="mono">custom_columns</span>, <span class="mono">alembic/env.py</span>.</li>
<li><strong>Vectors stored two ways, searched two ways</strong>: Postgres = <span class="mono">Vector(4096)</span> + native <span class="mono">&lt;=&gt;</span> (ANN-index capable); SQLite = <span class="mono">CommonVector</span> BINARY + a numpy UDF brute-forcing the whole table. All vectors <span class="mono">np.pad</span> to <span class="mono">MAX_EMBEDDING_DIM=4096</span>; <strong>zero-padding doesn't change cosine</strong>.</li>
<li><strong>pydantic-in-DB</strong>: a <span class="mono">TypeDecorator</span> <span class="mono">model_dump</span>s the whole <span class="mono">EmbeddingConfig</span> / <span class="mono">LLMConfig</span> to JSON in one column; schema-on-read makes adding a field migration-free, at the cost of non-indexable subfields + serialization overhead.</li>
<li><strong>Honest asterisk</strong>: v0.16.8's <span class="mono">server/db.py</span> only builds a Postgres async engine; the dual-DB story lives fully in the ORM column types and alembic's two backends.</li>
</ul>
</div>
<p>Part 7 is now complete: from the three-layer architecture, to managers, to the secure-by-default base, to dual DB and vectors. How the server safely stores and precisely retrieves "an agent's memory" — you've now seen through the whole chain.</p>
<p>Next is <strong>Part 8</strong>: advanced topics and a glossary. We'll dig into a few cross-cutting themes, then pull this whole journey's keywords into a glossary you can look up any time.</p>
""",
}
