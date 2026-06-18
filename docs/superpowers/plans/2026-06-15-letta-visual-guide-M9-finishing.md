# Letta 图解教程 · M9 配套收尾（quizzes / 双语 PDF / CI / README / LICENSE）

> 全书正文（8 部分 / 31 课）在 M8 已完成。M9 是**配套收尾**，交付让这套教程"可发布、可分发、可维护"的基础设施。非课程内容，故不走两阶段 zh/en 协议。

## 交付清单

1. **Quizzes 全量** — 30 课（01–30）均已配自测题（5 选 1 + 1 开放题）；术语表（31）按设计无 quiz。
   - **题面长度均衡**：全量量化后，对正确项 ≥ 2.5× 最长干扰项的 **36 道**（lessons 01/04/05/06/07/12/13/14/15/16/17/19/20/21/22）逐一收敛，引用/枚举移入 `why`，正确项仍唯一正确、`answer:0` 不变。其余轻度长度差作为可接受体例（确定性洗牌已消除位置线索）。

2. **双语 PDF** — `src/build_print.py` 生成单文件、自包含、打印优化的 `print-zh.html` / `print-en.html`（拼全 31 课，`@media print` 分课分页、卡片/表格 `break-inside:avoid`、强制浅色）。浏览器"打印 → 另存为 PDF"即得双语两本。`build.py` 顺带生成；首页提供入口；术语表跨课链接在单文件版改写为 `#LNN` 文内锚点。零依赖（无 headless 浏览器 / PDF 库）。

3. **CI** — `.github/workflows/`：
   - `ci.yml`：push / PR 时 `build.py` → `git diff --exit-code`（提交的 HTML 未过期）→ `check_links.py` → `check_html.py`。
   - `deploy.yml`：push 到 master 后构建并发布到 GitHub Pages（标准 configure/upload/deploy）。

4. **README** — 覆盖：是什么、如何查看（`file://` / 本地服务器）、如何重新生成与校验、如何导出 PDF、如何部署、目录结构、致谢与许可。

5. **LICENSE** — MIT（`Copyright (c) 2026 verdenmax`）。独立学习材料，与 Letta 官方无隶属；片段为教学化简；Letta 本身 Apache-2.0。

## 需要仓库所有者手动做的一步

GitHub Pages 一次性启用：`Settings → Pages → Build and deployment → Source` 选 **GitHub Actions**。
工作流自身无法创建 Pages 站点（`GITHUB_TOKEN` 无该权限）；启用后每次推送自动部署。

## 验证（DoD，已满足）

```
cd src && python build.py && python check_links.py && python check_html.py
```
`0 error / 0 warning`，链接全解析，index pill「共 31 课 · 8 个部分」；`build_print.py` 产出两本打印版；
两个 workflow YAML 合法；LICENSE / README 就位。M9 净增代码经 code-review（charset、文内锚点、check_links 容错三处已修）。
