# Letta 图解教程 · M3 第三部分（记忆系统，6 课）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 写出第三部分「记忆系统」的 6 课（07 记忆三层总览 · 08 记忆块 · 09 自我编辑记忆 · 10 归档记忆与向量检索 · 11 回忆记忆与对话历史 · 12 上下文压缩与"记忆压力"）。这是**全书重头戏**——要更详细、更图文并茂、绝不出现"大段大段文字"。

**Architecture:** 同前。内容放**新文件 `src/part3.py`**（`registry.py` 加 `import part3`）。新增一课 = 改 `shell.PAGES` + `shell.SUBTITLES` + `registry.CONTENT` + `part3.py` + (可选)`quizzes.QUIZZES`。

**Tech Stack:** Python 3.11+ 标准库；自包含 HTML/CSS。讲解对象 `/home/verden/course/letta`（v0.16.8）。

> **Task 0 已完成**（commit `134bb04` + `fd54800`，本分支 `feat/m3-memory`）：新增 `.note` 轻量 alert 与 `.cute` 萌图组件；`check_html` 加了双语"反长文"软闸门（`<p>` > 200 CJK 或 > 120 词即 WARN）；并已把 M1/M2 既有长段全部拆解、用上新组件。当前全站 `0 error / 0 warning`。

---

## 强化内容准则（M3 在 M1「共享约定」上**加强**；务必逐条遵守）

> M1 共享约定（页面结构、卡片种类、双语等价、源码"文件+符号"且核实、无 `<h1>`、结尾回扣整体）仍然全部生效，见 `2026-06-15-letta-visual-guide-M1-part1-overview.md`。M3 在其上**加四条硬要求**：

1. **反长文（硬性，已上 `check_html` 闸门）**：任何 `<p>` **≤ 200 中文字 / ≤ 120 英文词**，超了直接 WARN。每段只讲一个点，写长了就拆成两段、或改成列表/图/note。**绝不允许连续 3 段以上纯文字**——中间必须插入一个非文字元素。
2. **高频穿插视觉**：平均**每 1–2 段**就要出现一个"非纯文字"块（图 / `.note` / `.cute` / 代码 / `<ul>` 列表 / 折叠）。读者视线每滚动一屏，都应看到图或强调框，而不是一堵文字墙。
3. **新组件 `.note`（轻量 alert，每课 ≥ 3 个）**：把"关键 takeaway / 易错点 / 旁注 / 预告下一课"从正文拎出来强调。
   - markup：`<div class="note tip"><span class="ni">💡</span><span class="nx">……</span></div>`
   - 变体：`note tip`（accent 色，配 💡/🧠/✅）、`note info`（蓝色，配 👉/📌）、`note warn`（琥珀色，配 ⚠️）。
4. **新组件 `.cute`（萌图，每课 ≥ 1 个）**：用 emoji + 标签画一个友好的小示意图来替代一段干解释（记忆系统天然适合：便利贴 📝、抽屉 🗄️、档案柜 📦、大脑 🧠、磁盘 💾…）。
   - markup：`<div class="cute"><div class="row"><span class="emoji">🧠</span><span class="lab">标签</span><span class="arrow">↔</span><span class="emoji">📦</span><span class="lab">标签</span></div><div class="cap">一句话说明</div></div>`
   - 也可只放一行 emoji + 一个 `<div class="bubble">气泡台词</div>` + `cap` 说明，怎么可爱怎么来。
5. **更详细（重头戏）**：每课 CJK **目标 4500+**（仍 ≥3000 硬底）；**图 ≥ 4 张/语言**（合计 ≥ 8，`.cute` 计入）；**折叠 3–4 个**；把机制讲透。但"更详细"靠**更多小块**（多图、多 note、多列表、多折叠）实现，**不是**更长的段落。

> 一句话：M3 要"**像图文并茂的科普长文**"，不是"**论文式大段落**"。

---

## 接线（首次用 part3.py）
`src/part3.py` 顶部写模块 docstring，依次 `LESSON_07 … LESSON_12`。`src/registry.py` 加 `import part3` 并在 `CONTENT` 追加 6 条。`shell.PAGES`/`SUBTITLES` 每课追加一行，`part_zh="第三部分 · 记忆系统"`、`part_en="Part 3 · The memory system"`。

## 已核实源码锚点（v0.16.8，可直接引用，不写行号）
- 记忆模型：`letta/schemas/memory.py::Memory`（`.compile` / `.compile_async`、`ContextWindowOverview`）；`letta/schemas/block.py`（`Block` / `Human` / `Persona` / `CreateBlock` / `BlockUpdate`，注意是 `BlockUpdate`）。
- 三组记忆工具（实现）：`letta/services/tool_executor/core_tool_executor.py::LettaCoreToolExecutor` 的 `core_memory_append` / `core_memory_replace` / `conversation_search` / `archival_memory_insert` / `archival_memory_search`；声明/docstring 在 `letta/functions/function_sets/base.py`。
- 系统提示与元信息：`letta/prompts/prompt_generator.py::PromptGenerator`（`compile_memory_metadata_block`、`get_system_message_from_compiled_memory`）；占位符 `letta/constants.py::IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"`；`letta/services/agent_manager.py::rebuild_system_prompt_async`。核心记忆字符上限 `letta/constants.py::CORE_MEMORY_BLOCK_CHAR_LIMIT = 100000`。
- 服务层：`letta/services/block_manager.py::BlockManager`（+ `block_manager_git.py::GitEnabledBlockManager`、`letta/orm/block_history.py::BlockHistory` 版本/undo）；`letta/services/message_manager.py::MessageManager`；`letta/services/passage_manager.py::PassageManager`；`letta/services/archive_manager.py::ArchiveManager`。
- 归档/向量：`letta/schemas/passage.py::Passage`；`letta/orm/passage.py`（`ArchivalPassage` / `SourcePassage`）；`letta/orm/sqlite_functions.py`（sqlite-vec）；pgvector 见 `letta/orm/custom_columns.py` / `passage.py`。
- 压缩：`letta/services/summarizer/`（`summarizer.py::Summarizer`、`compact.py::compact_messages`、`thresholds.py::get_compaction_trigger_threshold` = `context_window × SUMMARIZATION_TRIGGER_MULTIPLIER`，`0.9` 在 `constants.py`）；触发在 `letta/agents/letta_agent_v3.py::_step` / `compact`；消息信封 `letta/system.py`。

---

## Task 1: 新增第 07 课「记忆三层总览」

**Files:** `src/shell.py`(PAGES+SUBTITLES) · `src/part3.py`(新建 + `LESSON_07`) · `src/registry.py`(import part3 + CONTENT) · (可选)`src/quizzes.py`

**filename:** `07-memory-tiers.html`；标题 zh「记忆三层总览」/ en「The three memory tiers」；副标题 zh「core / recall / archival · 在窗与窗外 · 模型怎么知道自己忘了什么」/ en「core / recall / archival; in vs out of context; how the agent knows what it forgot」。

**学习目标（本部分的"地图"课）：** 一眼讲清 Letta 记忆三层——**core（核心）/ recall（回忆）/ archival（归档）**：各自在不在上下文窗口里、容量多大、怎么读怎么写、对应 MemGPT 论文的哪一层；以及 agent 怎么**知道"窗外还有什么"**（`<memory_metadata>`），从而决定何时去"翻档案"。为 08–12 五课各自的深挖铺路。

**亮点（`card spark`）：** 这其实是把**操作系统的存储层级**搬进了 agent：**core = RAM**（永远在眼前、可被 agent 自己改写）、**recall = 磁盘上的对话日志**（可检索召回）、**archival = 长期向量库**（按相似度捞）。更妙的是 Letta 给模型塞了一张实时"**库存清单**"（`compile_memory_metadata_block` 产出的 `<memory_metadata>`：还有多少条 recall、多少条 archival、有哪些 tag），于是模型**知道自己忘了什么、该去哪一层翻**——"换页"由 agent 自己发起。

**必需卡片：** `lead`；`card macro`（三层是什么、一张总图）；`card analogy`（办公桌台面=core、桌边抽屉=recall、地下档案室=archival）；`card detail`（落到 `Memory`、三组工具、`compile_memory_metadata_block`）；`card spark`（OS 存储层级 + 库存清单）；`card key`；`card warn`（core 有字符上限 `CORE_MEMORY_BLOCK_CHAR_LIMIT`，是稀缺资源——别什么都往 core 塞）。**外加 ≥3 个 `.note`、≥1 个 `.cute`。**

**必需图（≥4/语言）：**
1. **三层总览 `layers`**：l-core=core（在窗·可改）、l-main=recall（窗外·可搜）、l-part=archival（窗外·向量搜），每层标"在窗?/容量/读写方式"。
2. **三层对照 `table.t`**：列＝层 / 在上下文? / 容量 / 怎么写 / 怎么读 / MemGPT 术语。
3. **`.cute` 萌图**：🧠 core ↔ 🗄️ recall ↔ 📦 archival，气泡台词"眼前的/最近的/长期的"。
4. **库存清单 `.note info`**：把 `<memory_metadata>` 的作用画成"模型每轮都先看一眼库存单"。
5.（可选）**何时翻档案 `vflow`**：窗口快满 → 旧消息换出到 recall → 需要时 `conversation_search` / `archival_memory_search` 捞回。

**必需代码（2–3，`codefile`）：**
- A) 三组工具速览：`core_memory_append/replace`（改 core）、`conversation_search`（搜 recall）、`archival_memory_insert/search`（写/搜 archival）。来源 `letta/services/tool_executor/core_tool_executor.py`。
- B) `<memory_metadata>` 长啥样（简化）：来源 `letta/prompts/prompt_generator.py::compile_memory_metadata_block`。

**必需折叠（3–4）：** MemGPT 论文三层映射；为什么要分三层而不是一个大库；`<memory_metadata>` 到底告诉了模型什么；core 的字符上限与取舍。

**自测题种子：** 三层哪层在上下文里（core）；模型怎么知道窗外还有内容（memory_metadata）；archival 靠什么检索（向量相似度）。

**草图（真实类；en 镜像；演示新组件）：**

三层总览（`layers`）：
```html
<div class="layers">
  <div class="layer l-core"><div class="lh"><span class="badge">在窗 · 可自改</span><span class="name">core memory 核心记忆</span></div>
    <div class="ld">persona / human 等块，永远在上下文里；agent 用 <span class="mono">core_memory_append/replace</span> 自己改</div></div>
  <div class="layer l-main"><div class="lh"><span class="badge">窗外 · 可检索</span><span class="name">recall memory 回忆记忆</span></div>
    <div class="ld">全部对话历史的存档，只有最近一段在窗内；用 <span class="mono">conversation_search</span> 捞回</div></div>
  <div class="layer l-part"><div class="lh"><span class="badge">窗外 · 向量搜</span><span class="name">archival memory 归档记忆</span></div>
    <div class="ld">长期知识库，容量近乎无限；按相似度 <span class="mono">archival_memory_search</span></div></div>
</div>
```

萌图（`.cute`）：
```html
<div class="cute">
  <div class="row">
    <span class="emoji">🧠</span><span class="lab">core·眼前</span>
    <span class="arrow">·</span>
    <span class="emoji">🗄️</span><span class="lab">recall·最近</span>
    <span class="arrow">·</span>
    <span class="emoji">📦</span><span class="lab">archival·长期</span>
  </div>
  <div class="cap">三层记忆 = 桌面 / 抽屉 / 档案室：越往外越大、越远，但都能按需取回</div>
</div>
```

库存清单（`.note info`）：
```html
<div class="note info"><span class="ni">📌</span><span class="nx"><strong>模型每轮都先瞄一眼"库存单"。</strong><span class="mono">&lt;memory_metadata&gt;</span> 会告诉它：recall 里还压着 N 条、archival 里存了 M 条、有哪些 tag——于是它<strong>知道自己忘了什么、该去哪层翻</strong>。</span></div>
```

**Steps:**
- [ ] **Step 1: 接线**（PAGES/SUBTITLES 追加 07；`registry.py` 加 `import part3` 与 `"07-memory-tiers.html": part3.LESSON_07`；`part3.py` 建文件 + `LESSON_07` 占位 stub，build 跑通）。PAGES 元组：
  ```python
      ("07-memory-tiers.html", "记忆三层总览", "The three memory tiers",
       "第三部分 · 记忆系统", "Part 3 · The memory system"),
  ```
  SUBTITLES：
  ```python
      "07-memory-tiers.html": ("core / recall / archival · 在窗与窗外 · 模型怎么知道自己忘了什么",
                               "core / recall / archival; in vs out of context; how the agent knows what it forgot"),
  ```
- [ ] **Step 2: 写 `LESSON_07`（zh+en）** 到强化准则的结构与深度（**staged**：先接线+stub，再填 zh，再填 en；每次 `python -c "import part3"`）。务必满足：CJK≥4500 目标、≥4 图/语言、≥3 个 `.note`、≥1 个 `.cute`、3–4 折叠、无 `<p>` 超长。
- [ ] **Step 3:（可选）加自测题**。
- [ ] **Step 4: 验证 WARN-free**：`cd src && python build.py && python check_links.py && python check_html.py` → `0 error(s)`，且**无** `07-memory-tiers.html` 的任何 `[WARN]`（含 wall-of-text）。
- [ ] **Step 5: 核对锚点**：`cd /home/verden/course/letta`；`grep -rn "def core_memory_append" letta/services/tool_executor/core_tool_executor.py`；`grep -rn "def compile_memory_metadata_block" letta/prompts/prompt_generator.py`；`grep -rn 'IN_CONTEXT_MEMORY_KEYWORD' letta/constants.py`。
- [ ] **Step 6: 提交** `feat(m3): add lesson 07 (three memory tiers)`（含 trailer；`git add src/ lessons/ index.html`）。

---

---

## Task 2: 新增第 08 课「记忆块 Memory Blocks」

**Files:** `src/shell.py` · `src/part3.py`(`LESSON_08`) · `src/registry.py` · (可选)`src/quizzes.py`
**filename:** `08-memory-blocks.html`；zh「记忆块 Memory Blocks」/ en「Memory blocks」；副标题 zh「label/value/limit · Memory.compile · 共享块 · 版本历史」/ en「label/value/limit; Memory.compile; shared blocks; versioning」。

**学习目标：** 深入 core memory 的**最小单位——Block**：字段 `label / value / limit / read_only`，`Human` / `Persona` 两个常用子类，`Memory` 是 Block 的集合，`Memory.compile()` 怎么把这些块渲染成 system 里的 `<memory_blocks>` 文本；以及块的两个高级性质——**可共享**与**可版本化**。

**亮点（`card spark`）：** 块是**一等、可寻址、可共享**的实体（`block-…` id）——两个 agent 可以挂同一个 block，于是"共享记忆"自然成立；块还有 **git 式历史**（`BlockHistory` / `GitEnabledBlockManager`，可 undo/redo）。记忆不是一团 blob，而是一组**有标签、有上限、有版本**的卡片。

**必需卡片：** `lead`/`macro`（块=带标签的卡片）/`analogy`（白板上的分区便利贴）/`detail`（`Block`/`Human`/`Persona`、`Memory.compile`、`block_manager`）/`spark`（共享+版本）/`key`/`card warn`（`limit` 超限会被拒/截断；`read_only` 块 agent 不能改）。**+≥3 `.note`、+≥1 `.cute`。**

**必需图（≥4/语言）：** ① Block 解剖 `cellgroup`（label/value/limit/read_only）；② `.cute` 📝 一张带标签的便利贴；③ `Memory.compile()` `flow`（blocks → `<memory_blocks>` 文本 → 进 system）；④ 共享块 `layers`/`cols`（同一 block ← agent A / agent B）；⑤ `table.t` 三件套 `CreateBlock`/`BlockUpdate`/`Block` 字段。
**必需代码（2–3 `codefile`）：** `Block` schema（来源 `letta/schemas/block.py`）；`Memory.compile()` 产出的 `<memory_blocks>` 简化样例（来源 `letta/schemas/memory.py::Memory.compile`）；`ChatMemory(persona, human)` 构造。
**必需折叠（3–4）：** 共享块怎么实现（`blocks_agents` 多对多）；块的版本历史/undo；`limit` 与 `read_only` 的取舍；`Human`/`Persona` 与自定义块。
**草图（`.cute`）：**
```html
<div class="cute"><div class="row"><span class="emoji">📝</span><span class="bubble">label: human · "名字叫 Timber"</span></div>
<div class="cap">一个 Block 就是一张贴在 agent 眼前的便利贴：有标签、有内容、有字数上限</div></div>
```
**Steps（同 Task 1 六步）：** PAGES/SUBTITLES/CONTENT 用 08 值（part_zh="第三部分 · 记忆系统"）；锚点核对 `grep -rn "class Block\b\|class BlockUpdate\|class CreateBlock" letta/schemas/block.py`、`grep -rn "def compile" letta/schemas/memory.py`；提交 `feat(m3): add lesson 08 (memory blocks)`。

---

## Task 3: 新增第 09 课「自我编辑记忆 = 改写系统提示」

**Files:** `src/shell.py` · `src/part3.py`(`LESSON_09`) · `src/registry.py` · (可选)`src/quizzes.py`
**filename:** `09-self-editing-memory.html`；zh「自我编辑记忆 = 改写系统提示」/ en「Self-editing memory = rewriting the system prompt」；副标题 zh「core_memory_append/replace · {CORE_MEMORY} 占位符 · 重建第 0 条 · prefix cache」/ en「core_memory_append/replace; the {CORE_MEMORY} slot; rebuilding message #0; prefix cache」。

**学习目标（全书灵魂课）：** 把第 1 课点过的那句"自我编辑记忆 = 改写系统提示"**讲到机制底**：`core_memory_append/replace` 怎么改 `block.value` → 持久化 → 触发 `rebuild_system_prompt_async` **原地重写第 0 条 system 消息**；`{CORE_MEMORY}` 占位符（`IN_CONTEXT_MEMORY_KEYWORD = "CORE_MEMORY"`）怎么被编译后的块替换；以及为什么"正常步骤不重建、只在记忆变化/压缩时重建"（prefix cache）。

**亮点（`card spark`）：** agent "记住一件事"= **改写自己的出厂设定**。`Memory.compile()` 的产物被拼进**持久化的 system 消息**，块一变，`rebuild_system_prompt_async` 就**原地**重写第 0 条（同一个 id）。agent 在运行时**给自己重新编程**——这是 MemGPT 区别于"外挂记忆"的根本一手。

**必需卡片：** `lead`/`macro`（自编辑闭环）/`analogy`（改写自己的人设卡）/`detail`（`core_memory_*`、`{CORE_MEMORY}`、`rebuild_system_prompt_async`、prefix cache）/`spark`/`key`/`card warn`（正常步骤**故意不**重建 system 以保 prefix cache；只在记忆变化或压缩后重建）。**+≥3 `.note`、+≥1 `.cute`。**

**必需图（≥4/语言）：** ① 自编辑闭环 `vflow`（用户消息 → agent 调 `core_memory_replace` → block.value 改 → 持久化 → 重编译 system#0 → 下一轮即生效）；② `.cute` 🤖✏️📋（机器人在改自己的卡）；③ `{CORE_MEMORY}` 替换示意 `flow`（模板 + 编译后的块 → 完整 system）；④ prefix-cache `timeline`（稳定前缀命中缓存）。
**必需代码（2–3 `codefile`）：** `core_memory_replace` 实现简化（来源 `core_tool_executor.py`）；`get_system_message_from_compiled_memory` 的 `{CORE_MEMORY}` 替换（来源 `prompt_generator.py`）；`rebuild_system_prompt_async` 伪代码（来源 `agent_manager.py`）。
**必需折叠（3–4）：** 为什么改 prompt 而不是另存一张表；prefix cache 与第 0 条何时重建；`append` vs `replace`；多 agent 共享块时一处改、处处变。
**草图（`.note tip`）：**
```html
<div class="note tip"><span class="ni">🧠</span><span class="nx"><strong>关键一句：</strong>core memory 不是"存在别处的记忆"，它<strong>就是 system 提示的一部分</strong>。agent 改记忆 = 改自己每轮都会读到的"出厂设定"。</span></div>
```
**Steps（同 Task 1 六步）：** 09 值；锚点 `grep -rn "def core_memory_replace" letta/services/tool_executor/core_tool_executor.py`、`grep -rn "def rebuild_system_prompt_async" letta/services/agent_manager.py`、`grep -rn "def get_system_message_from_compiled_memory" letta/prompts/prompt_generator.py`；提交 `feat(m3): add lesson 09 (self-editing memory)`。

---

## Task 4: 新增第 10 课「归档记忆与向量检索」

**Files:** `src/shell.py` · `src/part3.py`(`LESSON_10`) · `src/registry.py` · (可选)`src/quizzes.py`
**filename:** `10-archival-memory.html`；zh「归档记忆与向量检索」/ en「Archival memory & vector search」；副标题 zh「Passage · 嵌入 · insert/search · pgvector / sqlite-vec · tags」/ en「Passage; embeddings; insert/search; pgvector / sqlite-vec; tags」。

**学习目标：** archival = **长期向量库**：`Passage`（文本 + 向量），`archival_memory_insert`（嵌入并存），`archival_memory_search`（按相似度搜），**pgvector（生产）vs sqlite-vec（开发）**双方言，archive 与 `tags`（`PassageTag`），嵌入模型来自 `embedding_config`。

**亮点（`card spark`）：** archival 就是**内建进 agent 的 RAG**——agent 自己写长期笔记（insert）、再**按意思**取回（search）；而且和第 7 课同款"**双数据库**"魔法（pgvector/sqlite-vec）让它从笔记本到生产**同一套代码**。tags 让 agent 给自己的知识**分类过滤**。

**必需卡片：** `lead`/`macro`（向量库 + 两个工具）/`analogy`（会自己记笔记、按意思查的资料库）/`detail`（`Passage`、`PassageManager`、`ArchivalPassage`、嵌入）/`spark`/`key`/`card warn`（search 是**相似**不是精确；每次 insert/search 都要一次嵌入调用，有成本）。**+≥3 `.note`、+≥1 `.cute`。**

**必需图（≥4/语言）：** ① insert `flow`（文本 → 嵌入 → `Passage(vector)` → 存）；② search `flow`（query → 嵌入 → 最近邻 passages）；③ `.cute` 📦🔍（按意思翻档案）；④ `table.t`（archival / recall / core：容量·检索方式·谁来写）；⑤ 双方言 `cols`（SQLite+sqlite-vec / Postgres+pgvector）。
**必需代码（2–3 `codefile`）：** `Passage` schema（来源 `letta/schemas/passage.py`）；`archival_memory_insert/search` 简化（来源 `core_tool_executor.py`）；嵌入 → 向量列（来源 `letta/orm/passage.py` / `custom_columns.py`）。
**必需折叠（3–4）：** 向量检索一分钟（余弦相似度）；pgvector vs sqlite-vec；archive 与 tags；archival passage vs source passage。
**草图（`.cute`）：**
```html
<div class="cute"><div class="row"><span class="emoji">📦</span><span class="arrow">→</span><span class="emoji">🔢</span><span class="lab">嵌入向量</span><span class="arrow">→</span><span class="emoji">🔍</span><span class="bubble">"按意思找最像的"</span></div>
<div class="cap">归档记忆 = 会按语义检索的长期笔记本，容量近乎无限</div></div>
```
**Steps（同 Task 1 六步）：** 10 值；锚点 `grep -rn "class Passage" letta/schemas/passage.py`、`grep -rn "def archival_memory_insert\|def archival_memory_search" letta/services/tool_executor/core_tool_executor.py`、`ls letta/orm/sqlite_functions.py`；提交 `feat(m3): add lesson 10 (archival memory & vector search)`。

---

## Task 5: 新增第 11 课「回忆记忆与对话历史」

**Files:** `src/shell.py` · `src/part3.py`(`LESSON_11`) · `src/registry.py` · (可选)`src/quizzes.py`
**filename:** `11-recall-memory.html`；zh「回忆记忆与对话历史」/ en「Recall memory & conversation history」；副标题 zh「Message · message_ids 在窗 · conversation_search · JSON 信封」/ en「Message; in-window message_ids; conversation_search; JSON envelopes」。

**学习目标：** recall = **全部对话历史**：`Message`（一条就是一行），`message_ids` 决定哪些在窗内，`conversation_search` 搜回旧消息；消息不是裸文本而是**带类型的 JSON 事件信封**（`letta/system.py` 的 `package_user_message` / `package_function_response` / `get_heartbeat`）；分清"在窗"与"已存档"。

**亮点（`card spark`）：** 对话**从不丢失**——每条消息都是可持久、可检索的 `Message` 行，只有 `message_ids` 留在窗内；而且消息是**带类型的 JSON 事件**（user_message / function_response / heartbeat），所以 agent 是在**结构化事件**上推理，`conversation_search` 也能精确捞回旧事件。

**必需卡片：** `lead`/`macro`（recall=全量日志、窗口=最近一段）/`analogy`（完整聊天记录 vs 屏幕上能看到的最近几条）/`detail`（`Message`、`message_ids`、`conversation_search`、`system.py` 信封）/`spark`/`key`/`card warn`（"在窗" ≠ 全部历史；更早的是**可搜不可见**）。**+≥3 `.note`、+≥1 `.cute`。**

**必需图（≥4/语言）：** ① 窗内 vs 全量 `cellgroup`/`layers`（`message_ids` ⊂ 全部 Message）；② `.cute` 🗄️🔍（翻聊天记录）；③ 一条 Message 的 JSON 信封 `codefile`/示意；④ `conversation_search` `flow`。
**必需代码（2–3 `codefile`）：** `Message` 关键字段 / `message_ids`（来源 `letta/schemas/message.py` / `schemas/agent.py`）；`package_user_message` 信封（来源 `letta/system.py`）；`conversation_search` 简化（来源 `core_tool_executor.py`）。
**必需折叠（3–4）：** 为什么用 JSON 信封而非裸文本；窗内消息怎么管理；recall vs archival（都能搜，差别在哪）；summary 消息也算 recall 的一部分。
**草图（`.note info`）：**
```html
<div class="note info"><span class="ni">👉</span><span class="nx">把 recall 想成<strong>完整录像</strong>，把"在窗消息"想成<strong>正在播放的最近几分钟</strong>——录像一直都在，只是没都摆在眼前。</span></div>
```
**Steps（同 Task 1 六步）：** 11 值；锚点 `grep -rn "class Message" letta/schemas/message.py`、`grep -rn "def conversation_search" letta/services/tool_executor/core_tool_executor.py`、`grep -rn "def package_user_message" letta/system.py`；提交 `feat(m3): add lesson 11 (recall memory)`。

---

## Task 6: 新增第 12 课「上下文压缩与"记忆压力"」

**Files:** `src/shell.py` · `src/part3.py`(`LESSON_12`) · `src/registry.py` · (可选)`src/quizzes.py`
**filename:** `12-context-compaction.html`；zh「上下文压缩与记忆压力」/ en「Context compaction & memory pressure」；副标题 zh「90% 阈值 · compact_messages · 滑窗摘要 · summary 消息 · 系统提示溢出」/ en「the 90% threshold; compact_messages; sliding-window summary; the summary message; system-prompt overflow」。

**学习目标（本部分收尾，呼应第 5 课）：** 窗口快满时怎么办——**压缩/摘要**把较旧的消息**换出并总结**：`get_compaction_trigger_threshold`（×0.9）、`compact_messages`、`Summarizer`（滑动窗口）、`role=summary` 的**摘要消息**、可见的 **compaction 事件**、以及"**核心记忆压不动**"的特殊溢出路径。

**亮点（`card spark`）：** "记忆压力"被当作**操作系统问题**处理：到 90% 就把较旧对话**递归摘要**成一段 summary，并把"我做了摘要"作为**可见事件**抛给客户端；但**核心记忆不能被压缩**（它就是 system 的一部分），所以有一条专门的**溢出处理**路径。这正是 MemGPT 论文里"队列管理器"的落地。

**必需卡片：** `lead`/`macro`（压力 → 压缩）/`analogy`（桌子满了先做一份会议纪要再收走旧纸）/`detail`（`thresholds`、`compact_messages`、`Summarizer`、`_step` 触发）/`spark`/`key`/`card warn`（摘要是**有损**的；核心记忆块若自己撑爆预算，要走溢出特判）。**+≥3 `.note`、+≥1 `.cute`。**

**必需图（≥4/语言）：** ① 压缩 `timeline`（tokens → 0.9 阈值 → compact → summary）；② `.cute` 📚→📝（把一摞旧消息压成一张纪要）；③ 滑窗摘要 `vflow`；④ 能压/不能压 `cols`（recall 可压 / core 不可压 → 溢出特判）。
**必需代码（2–3 `codefile`）：** `get_compaction_trigger_threshold`（来源 `summarizer/thresholds.py`，可与第 5 课呼应但聚焦"动手"）；`compact_messages` 伪代码（来源 `summarizer/compact.py`）；`role=summary` 的 summary 消息（来源 `letta/system.py` / `summarizer`）。
**必需折叠（3–4）：** 递归摘要怎么做；为什么核心记忆压不动（溢出特判）；可见的 compaction 事件；和第 5 课"度量"如何接上"动手"。
**草图（`.cute`）：**
```html
<div class="cute"><div class="row"><span class="emoji">📚</span><span class="arrow">→</span><span class="emoji">🗜️</span><span class="arrow">→</span><span class="emoji">📝</span><span class="bubble">一段摘要</span></div>
<div class="cap">窗口快满（~90%）：把较旧的一摞消息压成一张"会议纪要"，腾出空间继续聊</div></div>
```
**Steps（同 Task 1 六步）：** 12 值；锚点 `grep -rn "def get_compaction_trigger_threshold" letta/services/summarizer/thresholds.py`、`grep -rn "def compact_messages" letta/services/summarizer/compact.py`、`grep -rn "class Summarizer" letta/services/summarizer/summarizer.py`；提交 `feat(m3): add lesson 12 (context compaction)`。

---

## Task 7: M3 收尾 — 全量校验 + 导航链 + roadmap + 合并

- [ ] **Step 1: 全量校验**：`cd src && python build.py && python check_links.py && python check_html.py && echo ALL_OK` → `ALL_OK`，`0 error(s)`，**07–12 均无任何 WARN**（含 wall-of-text）；`index.html` 显示"共 12 课 · 3 个部分"。
- [ ] **Step 2: 导航链自检**：06→07、07→08、…、11→12（`grep -c` 各为 1）。
- [ ] **Step 3: 每课组件量自检**：07–12 每课 `.note` ≥3、`.cute` ≥1、图 ≥8（双语合计）、无 `<p>` 超长。
- [ ] **Step 4: 浏览器人工自检（手动）**：12 课可点进、记忆三层/自编辑/向量/压缩的图与萌图与 note 显示正常、深色模式正常、中英切换跨课保持。
- [ ] **Step 5: roadmap 标记 M3 完成并提交**。
- [ ] **Step 6: 合并**：`git checkout master && git merge --no-ff feat/m3-memory`（验证 merged 结果校验绿）→ `git branch -d feat/m3-memory` → `git push origin master`。

---

## Self-Review（对照 spec 第 4 节第三部分 + 强化准则）
- **覆盖**：spec 第三部分 6 课（07 总览 / 08 块 / 09 自编辑 / 10 归档 / 11 回忆 / 12 压缩）各有 Task。✔
- **强化准则**：每课 brief 都要求 ≥3 `.note`、≥1 `.cute`、≥4 图/语言、CJK 目标 4500+、反长文（已上 check_html 双语闸门），且"更详细=更多小块"。✔
- **去重/承接**：12 与第 5 课呼应（度量 → 动手），09 把第 1 课的"自编辑"讲到底，互不重复、层层加深。✔
- **源码准确**：每课 Step 5 grep 核对；全局锚点已对照 v0.16.8 核实。✔
- **占位符扫描**：无 TODO/TBD；每课给了真实-类名草图 + `.note`/`.cute` 演示 + 接线值。
- **命名一致**：`07-memory-tiers` / `08-memory-blocks` / `09-self-editing-memory` / `10-archival-memory` / `11-recall-memory` / `12-context-compaction`；内容在新文件 `src/part3.py`，`registry.py` 需 `import part3`。
