# Letta 图解教程 · Letta Visual Guide

[![Read online](https://img.shields.io/badge/Read_online-Live_Demo-6d5ce7?logo=githubpages&logoColor=white)](https://verdenmax.github.io/letta-visual-guide/)
[![CI](https://github.com/verdenmax/letta-visual-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/verdenmax/letta-visual-guide/actions/workflows/ci.yml)
[![Deploy](https://github.com/verdenmax/letta-visual-guide/actions/workflows/deploy.yml/badge.svg)](https://github.com/verdenmax/letta-visual-guide/actions/workflows/deploy.yml)
[![Lessons](https://img.shields.io/badge/lessons-31-6d5ce7)](https://verdenmax.github.io/letta-visual-guide/)
[![Parts](https://img.shields.io/badge/parts-8-7048e8)](https://verdenmax.github.io/letta-visual-guide/)
[![Letta](https://img.shields.io/badge/Letta-v0.16.8-0b7285)](https://github.com/letta-ai/letta)
[![Dependencies](https://img.shields.io/badge/dependencies-0-2b8a3e)](#重新生成--build--verify)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

从零理解 [Letta](https://github.com/letta-ai/letta)（原 MemGPT）的**中英双语图解教程**。
纯 Python **零依赖**生成器，产出**自包含**静态站点，可 `file://` 直接打开，也可一键部署到 GitHub Pages。

> A bilingual (中文 / English), source-accurate visual guide to the Letta codebase.
> Pure-stdlib generator, self-contained static output, openable via `file://`.

### 📖 在线阅读 · Read it now → **<https://verdenmax.github.io/letta-visual-guide/>**

- **8 个部分 · 31 课**，层层深入：宏观全景 → 前置基础 → 记忆系统 → agent 执行循环 → 工具系统 → LLM provider → 服务端与持久化 → 进阶专题 + 术语表。
- 每课配**真实源码对应**（锚定 letta `v0.16.8`，引用以「文件 + 符号名」为主，不写死行号）、**图解**、**伪代码 / 简化源码**、**自测题**与**设计亮点**。
- 顶部一键**中英切换**；首页可搜索；附**全书术语表**与跳链索引。

## 课程地图 · Curriculum

| # | 部分 · Part | 课 · Lessons | 看点 · Highlights |
|---|---|---|---|
| 1 | 宏观全景 · The Big Picture | [01–03](https://verdenmax.github.io/letta-visual-guide/lessons/01-what-is-letta.html) | Letta 是什么、项目地图、一条消息的生命周期 · what Letta is, the project map, the life of a message |
| 2 | 前置基础 · Foundations | [04–06](https://verdenmax.github.io/letta-visual-guide/lessons/04-agent-and-tools.html) | agent = LLM + 工具 + 循环、上下文预算、agent 即数据 · agents, the context budget, an agent *is* data |
| 3 | 记忆系统 · Memory system | [07–12](https://verdenmax.github.io/letta-visual-guide/lessons/07-memory-tiers.html) | core / recall / archival 三层记忆、自我编辑、压缩 · the three memory tiers, self-editing, compaction |
| 4 | Agent 执行循环 · Execution loop | [13–16](https://verdenmax.github.io/letta-visual-guide/lessons/13-agent-state-and-loop.html) | AgentState、V3 步进循环、heartbeat、tool rules · AgentState, the V3 step loop, tool rules |
| 5 | 工具系统 · Tool system | [17–20](https://verdenmax.github.io/letta-visual-guide/lessons/17-tool-as-function.html) | 工具即函数、自动 schema、分发 / MCP、沙箱安全 · tools as functions, auto-schemas, dispatch, the sandbox |
| 6 | LLM Provider 抽象 · Providers | [21–23](https://verdenmax.github.io/letta-visual-guide/lessons/21-provider-contract.html) | 统一 provider 契约、怪癖隔离、本地模型 GBNF · the provider contract, quirks, local-model decoding |
| 7 | 服务端与持久化 · Server & persistence | [24–27](https://verdenmax.github.io/letta-visual-guide/lessons/24-three-layer-architecture.html) | 三层架构、Managers、CRUD / 多租户、双库与向量 · the architecture, managers, multi-tenancy, vectors |
| 8 | 进阶专题 · Advanced topics | [28–31](https://verdenmax.github.io/letta-visual-guide/lessons/28-multi-agent-sleeptime.html) | 多智能体 / sleeptime、RAG、jobs/runs/steps、术语表 · multi-agent, RAG, observability, glossary |

## 快速查看 · View

```bash
# 直接打开（无需服务器）
open index.html              # macOS;  Linux: xdg-open index.html

# 或起一个本地静态服务器
python -m http.server -d . 8000   # 然后访问 http://localhost:8000
```

首页右上还有两个**打印版 / PDF** 入口（`print-zh.html` / `print-en.html`）：用浏览器的「打印 → 另存为 PDF」即可导出整本。

## 重新生成 · Build & verify

```bash
cd src
python build.py          # 生成 index.html + lessons/*.html + print-zh.html + print-en.html
python check_links.py    # 校验内部链接无死链
python check_html.py     # 校验结构（标签平衡 / 导航链 / registry↔PAGES 对齐 / 反长文等）
```

期望：`check_html` 报告 `0 error / 0 warning`，`check_links` 全部解析。`src/build.py` 是确定性构建——
改了 `src/` 里的内容后务必重新生成并提交 `index.html` 与 `lessons/`（CI 会校验它们没有过期）。

`print-zh.html` / `print-en.html` 体积较大且可随时重建，已在 `.gitignore` 中忽略；它们由 `build.py`
（或单独运行 `python build_print.py`）生成，并由部署流程在 Pages 上产出。

## 目录结构 · Layout

| 路径 | 作用 |
|---|---|
| `src/shell.py` | 设计系统（CSS）+ 导航 + 双语切换 + `PAGES`（课程清单）+ index 页 |
| `src/registry.py` | 文件名 → 双语内容映射（`import partN`；单一事实源） |
| `src/part1.py … part8.py` | 各部分课程内容（每课一个 `LESSON_NN = {"zh":…, "en":…}`） |
| `src/quizzes.py` | 每课自测题（4 选 1 单选若干 + 1 道开放题，渲染时确定性打乱选项） |
| `src/build.py` | 构建 index + lessons + 打印版 |
| `src/build_print.py` | 单文件打印 / PDF 版（`print-zh.html` / `print-en.html`） |
| `src/check_links.py` | 内部链接校验 |
| `src/check_html.py` | 结构 / 反长文 / 对齐校验（`31-glossary.html` 列入 `SOFT_EXEMPT`） |
| `lessons/NN-*.html` | 生成的课程页（中英同页，CSS 切换） |
| `docs/superpowers/` | 设计规范与各里程碑实施计划 |

## 部署 · Deploy (GitHub Pages)

仓库内含 `.github/workflows/`：

- **`ci.yml`** — 每次 push / PR：构建并校验（链接 + 结构），并确认提交的 HTML 未过期。
- **`deploy.yml`** — push 到 `master`：构建后发布到 GitHub Pages。

**一次性设置**（仓库所有者）：`Settings → Pages → Build and deployment → Source` 选 **GitHub Actions**。
工作流自身无法创建 Pages 站点（`GITHUB_TOKEN` 没有该权限），启用后即会在每次推送时自动部署。

## 致谢与许可 · License

独立的第三方**学习材料**，与 Letta 官方无隶属关系；内容对照 letta 仓库真实源码核实（锚定 `v0.16.8`）。
代码片段为教学用的**简化**摘录。本仓库以 [MIT](LICENSE) 许可发布；Letta 本身为 Apache-2.0。
