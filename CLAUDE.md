# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A lightweight Windows notepad replacement built with **Python 3.9 + PyQt6 + QScintilla**. Features: auto-save (30s debounce), line numbers, bold formatting, Markdown syntax highlighting and live preview, multi-tab, font zoom.

## Commands

```bash
# Setup virtual environment
cd D:\AIAGENT应用\replace_txt\notepad
python -m venv .venv
.venv\Scripts\activate
pip install PyQt6 PyQt6-QScintilla markdown

# Run the app (one-liner, CMD)
.venv\Scripts\activate.bat && python main.py

# Freeze dependencies
pip freeze > requirements.txt
```

---

## 开发工作流

核心原则: **实现 A 功能，绝不破坏 B 功能。** 流程按任务类型分两轨。

### 任务分类

| 类型 | 特征 | 示例 |
|------|------|------|
| **Feature** | 新功能、跨模块改动、架构调整 | 添加高亮语法、重构保存逻辑、新增面板 |
| **Bug Fix** | 修复缺陷、单文件小改、样式修正 | 修复 CRLF 行间距 bug、修正字体颜色 |

判断标准: 改动涉及 >2 个源文件 或 新增行为定义 → Feature；否则 → Bug Fix。

---

### Feature 轨道

| # | 步骤 | 技能 | 产出 |
|---|------|------|------|
| 1 | 需求澄清 | `mattpocock-skills-grilling` | 明确的需求边界和验收标准 |
| 2 | 领域建模 | `mattpocock-skills-domain-modeling` | 领域术语、模块关系、架构决策 |
| 3 | 制定计划 | `superpowers-skills-writing-plans` | `docs/plans/YYYY-MM-DD-<feature>.md` |
| 4 | **人工审查** | — | 用户批准计划 |
| 5 | TDD 实现 | `mattpocock-skills-tdd` + `superpowers-skills-subagent-driven-development` | 测试先行，逐任务实现 |
| 6 | 代码审查 | `mattpocock-skills-review` | 审查通过，无遗留问题 |
| 7 | 回归测试 | `pytest tests/` | 全部绿色，旧功能无退化 |
| 8 | 归档 + 版本 | `openspec-archive-change` + git commit + 更新 Version.md | 版本锚点，知识库更新 |

---

### Bug Fix 轨道

| # | 步骤 | 技能 | 产出 |
|---|------|------|------|
| 1 | 需求界定 | `mattpocock-skills-grilling` | 精确问题现象和边界 |
| 2 | 诊断根因 | `mattpocock-skills-diagnosing-bugs` | 根因确认（非猜测） |
| 3 | 制定计划 | `superpowers-skills-writing-plans` | 修复计划 |
| 4 | **人工审查** | — | 用户批准 |
| 5 | TDD 修复 | `mattpocock-skills-tdd`（先写复现测试 → 修复 → 验证） | 测试 + 修复 |
| 6 | 回归测试 | `pytest tests/` | 全部绿色 |
| 7 | 归档 + 版本 | git commit + 更新 Version.md | 版本锚点 |

**Bug Fix 可跳过步骤**：如果改动 ≤2 行且根因一目了然，可以跳过 Step 2（诊断）和 Step 3（计划），直接从 Step 1 到 Step 4（确认）到 Step 5（修复）。

---

### HOOK 保护

PreToolUse hook 仅在 `git commit` 时检查 **Version.md 是否包含当前 APP_VERSION**，不一致则阻断。Write/Edit 操作不再需要计划文件门禁——行为规范由技能对话驱动，不由机械阻断保证。

---

### 其他规则
- 执行范围内：当前项目目录下的任何增删查改操作，**直接执行，无需询问**
- 执行范围外：任何修改当前项目以外文件的操作，必须先询问用户
- 涉及文件变更时新建版本，不覆盖原文件，更新 `Version.md`
- 每次修改完成后必须执行：`git commit` + 更新 `Version.md`
- `Version.md` 中每个版本号对应一个 `git tag`，版本与 commit 一一对应
- 版本发布时执行：`git tag vX.Y.Z`，并在 `Version.md` 中标注 tag 引用
- 保留所有历史版本文件，不删除，便于回滚
- 提交修改到本地 git
- **每次执行任务完成后，必须在回复末尾告知用户当前版本号**

---

## Architecture

```
notepad/
├── main.py              # Entry point, creates QApplication
├── src/
│   ├── app.py           # QMainWindow — menu bar, toolbar, status bar, assembles all modules
│   ├── editor.py        # QsciScintilla subclass — line numbers, MD lexer, bold, zoom
│   ├── tab_manager.py   # QTabWidget — manages open tabs, Ctrl+T / Ctrl+W
│   ├── md_preview.py    # QSplitter — live Markdown preview via QTextBrowser
│   ├── autosave.py      # QTimer — 30s debounce, saves directly to file (no .tmp)
│   ├── file_handler.py  # File I/O, UTF-8/GBK detection, recent files
│   ├── find_replace.py  # Find/replace bar
│   └── settings.py      # QSettings persistence — font, theme, auto-save interval
└── resources/           # Icons (optional)
```

## Key Design Decisions

- **Auto-save (Obsidian-style)**: Save directly to the original file after 30s of inactivity. No temp files, no backup directory. Unnamed new files auto-save to `%USERPROFILE%\Documents\Notes\` with filename derived from first line of text.
- **QScintilla**: line numbers, Markdown lexer, bracket matching, auto-indent, undo/redo enabled. Code folding, autocomplete, breakpoint margin disabled.
- **Markdown preview**: `QSplitter` side-by-side. Python `markdown` library → HTML → `QTextBrowser`. 300ms debounce. `Ctrl+P` toggle. Hidden for `.txt` files.
- **Bold**: `Ctrl+B` wraps selected text with `**` delimiters (or removes them if present).
- **Font zoom**: `Ctrl+Scroll` → `zoomIn()`/`zoomOut()`.
- **Default directory**: `Documents\Notes\`, auto-created on first launch.

---

## Behavioral Guidelines

Reduce common LLM coding mistakes. Bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- Remove only imports/variables/functions that YOUR changes made unused.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

---

## 调试方法论

核心原则: **先观测再推断** — 不要先入为主，直接写测试验证。

1. 先观测再推断 — 事实第一，理论第二
2. 反转假设 — 问什么存活了，而不是什么坏了
3. 隔离理解 — 最小测试揭示最大真相
4. 对比学习 — A/B 测试是调试的最佳伙伴
5. 相信测试，不信文档 — 验证一切
6. 找反例 — 找"不正常"的行为，往往藏着答案
7. 记录根因 — 这样不会重蹈覆辙

### 七步框架

| 步骤 | 核心问题 |
| --- | --- |
| Step 1: 精确界定问题 | 期望行为 vs 实际行为是什么？ |
| Step 2: 反转假设 | 什么没坏？什么存活了？为什么？ |
| Step 3: 隔离测试 | 最小化复现，排除干扰 |
| Step 4: 对比实验：A vs B | 差异即原因 |
| Step 5: 验证文档 | 文档描述契约，不等于实现行为 |
| Step 6: UX 验证 | 用户实际看到什么？ |
| Step 7: 记录根因 | 记录机制，不只是记录修复 |

### 常见陷阱

| 陷阱 | 表现 | 正确做法 |
| --- | --- | --- |
| 过早锁定假设 | 前5分钟形成假设，花好几天证明它对 | 把假设明确写下来，主动找反对证据 |
| 忽视部分成功 | 修复症状，忽略已经工作的部分 | 研究"为什么这部分有效" |
| 架构隧道视野 | 架构正确但问题依旧，不停重构 | 停止编码，写隔离测试 |
| 只测正常路径 | 验证修复有效，不验证是否破坏其他 | 验证修复 + 回归测试 |

---

## 日志记录规则

### 软件运行日志

- 每次启动 app 时，自动将运行日志追加写入 `logs/runtime.log`
- 日志格式：`[YYYY-MM-DD HH:MM:SS] [LEVEL] message`
- LEVEL: INFO / WARNING / ERROR
- 不覆盖历史日志，本地持续叠加
- 日志内容包括：启动/退出时间、打开/保存文件路径、异常堆栈

### 测试日志

- 每次执行 `pytest` 后，将测试结果追加写入 `logs/test.log`
- 日志格式：`[YYYY-MM-DD HH:MM:SS] total=N passed=N failed=N errors=N`
- 保留每次测试运行的完整记录，便于追溯回归

### 日志目录

- `logs/` 目录自动创建（`os.makedirs(exist_ok=True)`）
- 日志文件大小超过 10MB 时自动轮转（添加 `.1` 后缀）

---

## 测试原则

### 技术验证 ≠ 用户体验验证

**代码通过不等于用户满意。** 单元测试和集成测试验证的是代码行为契约，用户验证的是真实交互体验。两者不可互相替代。

### 关键反例

| 技术验证（Pass） | 用户体验（Fail） |
|------|------|
| `assert widget.isVisible() == True` | 用户实际看不到——被其他窗口遮挡或在屏幕外 |
| `assert os.path.exists(path)` | 用户在资源管理器里找不到——路径太深或文件夹隐藏 |
| `assert color.blue() > 150` | 链接蓝色泄漏到整段文字——样式 bug 单元测试发现不了 |
| `assert tab.count() == 5` | 用户只能看到 3 个——TabBar 宽度不够，其余被挤出视线 |

### 测试规则

- **模拟真实操作**：测试时使用鼠标点击、键盘输入、拖拽等用户实际操作方式，不直接调内部方法
- **还原实际环境**：使用相同分辨率（本项目 1920×1080）、相同 DPI、相同字体环境
- **端到端验证**：每次改完代码后启动 app，亲自操作一遍完整流程
- **边界情境**：多标签、长文件名、大文件、特殊字符、网络路径等实际使用场景

### 测试清单

- [ ] 用鼠标（不是代码）操作完整个用户流程
- [ ] 用键盘快捷键验证（Ctrl+S, Ctrl+B, Ctrl+W 等）
- [ ] 在默认 1920×1080 分辨率下确认 UI 布局正常
- [ ] 检查状态栏提示信息是否准确、及时

---

## 苏格拉底式五问五答调试法

### 核心原则

**先观测日志事实，再找根因。**

调试三步顺序（必须遵守）：
1. **先看日志** — 读取 `logs/runtime.log` 和 `logs/test.log`，从日志中提取异常时间点、错误堆栈、失败用例
2. **再看现场** — 观察 UI 行为、文件状态、系统资源的实际表现
3. **最后五问** — 基于日志事实和观测事实，连续追问五次，每问一层，直到底层机制暴露

禁止跳过日志直接猜原因。日志是最客观的事实来源。

### 调试入口清单

在开始任何 bug 调查前，必须按顺序检查：

| 顺序 | 检查项 | 命令/路径 |
|------|--------|-----------|
| 1 | 运行日志 | `cat logs/runtime.log` |
| 2 | 测试日志 | `cat logs/test.log` |
| 3 | git log | `git log --oneline -10` |
| 4 | 当前版本 | `git tag -l "v*" --sort=-v:refname \| head -1` |

### 五问流程

| 问次 | 问题 | 目的 |
|------|------|------|
| 第一问 | 日志里实际记录了什么？（精确描述日志事实） | 建立事实基线 |
| 第二问 | 什么没坏？（界定问题边界） | 缩小排查范围 |
| 第三问 | 两边的差异是什么？（A/B 对比） | 隔离关键变量 |
| 第四问 | 这个差异的底层机制是什么？ | 找到直接原因 |
| 第五问 | 如果根因在此，能解释所有现象吗？ | 验证根因完整性 |

### 示例

```
现象: 字体对话框改了大小，编辑器不变

Step 1: 看日志
$ cat logs/runtime.log
[2026-05-06 10:23:01] [INFO] App started v0.3.10
[2026-05-06 10:23:15] [INFO] Font size changed: 11 → 14
$ cat logs/test.log
[2026-05-06 09:15:00] total=57 passed=57 failed=0  ← 全部通过！说明不是崩溃级bug

Step 2: 看现场
- 预览区 QLabel: 字体变为 14pt ✓
- 编辑器: 字体仍为 11pt ✗
- 重新打开格式菜单: 显示 14pt（设置存了）

Step 3: 五问
第一问: 日志和现场显示了什么？
答: 日志记录字体变更成功，实际预览生效但编辑器未生效

第二问: 什么没坏？
答: 预览区、设置持久化、滑块 UI 都正常

第三问: 预览 vs 编辑器差异是什么？
答: 预览用 QLabel.setFont()，编辑器有 QsciLexerMarkdown

第四问: lexer 的机制是什么？
答: lexer 每个 style 独立存储 font，优先级高于 editor.setFont()

第五问: 能解释全部现象吗？
答: 能——editor.setFont() 被 lexer 覆盖，预览无 lexer 所以生效
→ 根因: lexer style 字体未同步更新
```

### 适用场景

- 任何 bug 调查开始前，**必须先查 `logs/runtime.log` 和 `logs/test.log`**
- 基于日志事实开始五问，而非基于猜测
- 五问走不通 → 说明日志不够或观测不够，回第一步补充事实
- 禁止跳过日志直接猜原因

---

## 重要指令

- 在任何情况下，都不要主动调用或执行 `/opsx:apply` 命令
