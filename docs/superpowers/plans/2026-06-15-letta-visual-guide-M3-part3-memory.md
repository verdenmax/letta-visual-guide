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

> Task 2–6（08 记忆块 / 09 自我编辑记忆 / 10 归档与向量 / 11 回忆与对话历史 / 12 上下文压缩）与 Task 7（收尾+合并）将在计划第二段补充（按用户偏好分步写）。
