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
<div class="card analogy"><div class="tag">🏢 生活类比</div>
<p>把整套服务端想象成一栋<strong>三层楼的公司</strong>，你（HTTP 请求）走进大门办一件事。</p>
<p><strong>一楼前台</strong>（薄路由）只做登记：核对你是谁、把表格收齐，然后说"这事归二楼"，把条子递上去。前台从不亲自翻档案。</p>
<p><strong>二楼经理</strong>（Manager）才有权动数据。要紧的是——每动一次档案，经理都要亲手开一道叫"<strong>事务</strong>"的门，办完即关。</p>
<p><strong>三楼档案室</strong>（ORM / DB）保管所有资料，但谁能看哪一份，由门禁（访问控制）说了算，经理也不能越权。</p>
<p>还有个老板（<span class="mono">SyncServer</span>）坐镇：他不亲自办每件小事，只在"一件事要好几个经理一起协调"时才出面，平时大家直接找对应的经理。</p>
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
<p>每个路由用 <span class="mono">Depends(get_letta_server)</span> 要一份，拿到的<strong>都是同一个实例</strong>。这就是"一个进程，一个全局 server"在代码里的落地方式。</p>
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
<!--ZHMORE-->
""",
    "en": r"""<p>stub</p>""",
}
