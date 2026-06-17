# Letta 图解教程 · 实施路线图（Roadmap）

> 配套 spec：`docs/superpowers/specs/2026-06-15-letta-visual-guide-design.md`
> 计划**按里程碑分步编写**：先出 M0 脚手架计划并执行，再逐个里程碑写计划，不一次写完全部。

## 里程碑总览

| 里程碑 | 内容 | 课数 | 计划文档 |
| --- | --- | --- | --- |
| **M0** | 脚手架：生成器（shell/registry/build）+ 主题换皮 + 双语切换 + 校验脚本 + 1 课基线 + index | 1（基线） | `2026-06-15-letta-visual-guide-M0-scaffold.md` ✅ 已完成并合并 |
| **M1** | 第一部分 · 宏观全景 | 3 | `2026-06-15-letta-visual-guide-M1-part1-overview.md` ✅ 已完成并合并 |
| **M2** | 第二部分 · 前置基础 | 3 | `2026-06-15-letta-visual-guide-M2-part2-foundations.md` ✅ 已完成并合并 |
| **M3** | 第三部分 · 记忆系统（**全书核心**） | 6 | `2026-06-15-letta-visual-guide-M3-part3-memory.md` ✅ 已完成并合并 |
| **M4** | 第四部分 · Agent 执行循环 | 4 | `2026-06-15-letta-visual-guide-M4-part4-agent-loop.md` ✅ 已完成并合并 |
| **M5** | 第五部分 · 工具系统 | 4 | `2026-06-15-letta-visual-guide-M5-part5-tools.md` ✅ 已完成并合并 |
| **M6** | 第六部分 · LLM Provider 抽象 | 3 | 待写 |
| **M7** | 第七部分 · 服务端与持久化 | 4 | 待写 |
| **M8** | 第八部分 · 进阶专题 + 术语表 | 4 | 待写 |
| **M9** | 配套收尾：quizzes 全量 + 双语 PDF + CI + README + LICENSE | — | 待写 |

合计：8 部分 / 31 课。

## 不变量（每个里程碑都要守住）

1. 每次改完跑：`cd src && python build.py && python check_links.py && python check_html.py`，三者都通过（check_html 允许 WARN）。
2. `shell.PAGES` 与 `registry.CONTENT` 始终一一对应（build.py 会校验；不对应直接 `sys.exit`）。
3. 源码引用以「文件 + 符号名」为准，不写死行号；对照 `letta` 仓库 `v0.16.8` 真实代码核实。
4. 自包含、相对链接、`file://` 可开；中英信息等价。
5. 每个里程碑独立可构建、可在浏览器查看，并独立提交。

## 执行方式

每个里程碑的计划写完后，按 `superpowers:subagent-driven-development`（每个 task 派发子代理 + spec/质量双重审查）执行；
内容类 task 用「先写课、再跑 check_html」的回路代替传统单测。
