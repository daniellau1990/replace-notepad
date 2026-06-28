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
| 2 | 领域建模 + **设计探针** | `mattpocock-skills-domain-modeling` + 探针验证（见下） | 领域术语 + API 存在性 + 集成点验证 |
| 3 | 制定计划 | `superpowers-skills-writing-plans` | `docs/plans/YYYY-MM-DD-<feature>.md` |
| 4 | **人工审查** | — | 用户批准计划 |
| 5 | TDD 实现 | `mattpocock-skills-tdd` + `superpowers-skills-test-driven-development` + `superpowers-skills-subagent-driven-development` | 测试先行，逐任务实现 |
| 6 | 功能测试 | QApplication 功能测试 + **模拟鼠标点击测试**（UI 改动强制） | 功能/事件链验证通过 |
| 7 | 代码审查 | `mattpocock-skills-review`（见代码审查清单） | 审查通过 |
| 8 | 回归测试 | `pytest tests/` | 全部绿色，旧功能无退化 |
| 9 | 归档 + 版本 | `openspec-archive-change` + git commit + 更新 Version.md | 版本锚点，知识库更新 |

---

### 🔴 Feature Step 2 — 设计探针（领域建模后的代码验证）

领域建模完成后、制定计划前，对设计中涉及的 API、集成点、边界条件
写 5-10 行探针脚本。**不等实现阶段才发现 API 不存在。**

| 探针类型 | 验证问题 | v0.3.15–v0.3.19 教训 |
|---------|---------|---------------------|
| API 存在性 | 要调的方法真的存在？ | `hasattr(QTabBar, 'ensureVisible')` → False → 发现时已写 200 行 |
| 集成点兼容 | 两个模块的接口真的匹配？ | 参数类型、返回值格式是否一致 |
| 边界条件 | 空值/溢出/极端输入？ | tab 数 = 0 或 100 时行为正确？ |
| 失败预演 | "如果方案失败，最先在哪崩？" | 主动验证那个点，不等崩溃才排查 |

探针脚本格式：
```python
# 5 行探针：验证关键 API 在运行时真实存在
from PyQt6.QtWidgets import QTabBar
bar = QTabBar()
for i in range(20): bar.addTab(f'T{i}')
bar.resize(200, 40)
assert hasattr(bar, 'ensureVisible'), "API 不存在，需替换方案"
```

**硬规则**：
- 设计涉及不熟悉的 API → **必须写探针**
- 两个模块首次对接 → **必须写集成探针**
- 探针通过 → 进入 Step 3 制定计划
- 探针失败 → 修正设计，**不带着错误假设进入编码**

---

### Bug Fix 轨道

| # | 步骤 | 技能 | 产出 |
|---|------|------|------|
| 1 | 需求界定 | `mattpocock-skills-grilling` | 精确问题现象和边界 |
| 2 | **诊断根因** | 🔴 三 skill 联合调用（见下） | 根因确认 + DEBUG.md |
| 3 | 制定计划 | `superpowers-skills-writing-plans` | 修复计划 |
| 4 | **人工审查** | — | 用户批准 |
| 5 | TDD 修复 | `mattpocock-skills-tdd` + `superpowers-skills-test-driven-development` | 先写复现测试 → 失败 → 修复 → 通过 |
| 6 | 功能测试 | QApplication 功能测试 + **模拟鼠标点击测试**（UI 改动强制） | 功能验证 + 事件链验证 |
| 7 | 代码审查 | `mattpocock-skills-review`（见代码审查清单） | 审查通过 |
| 8 | 回归测试 | `pytest tests/` | 全部绿色 |
| 9 | 归档 + 版本 | git commit + 更新 Version.md | 版本锚点 |

**🔴 Bug Fix Step 2 — 诊断根因（三 skill 联合调用，不可跳过）**

进入 Step 2 **立即按顺序调用**以下三个 skills，不等失败：

| 顺序 | Skill | 核心作用 |
|------|-------|---------|
| 1 | `Shen_Huang_debugging_skill_auto_research` | Anti-Bulldozer：Observe→Hypothesize→Experiment→Conclude，写入 DEBUG.md，每实验 ≤5 行 |
| 2 | `mattpocock-skills-diagnosing-bugs` | Phase 1：建 feedback loop——一个能复现 bug 的自动化命令 |
| 3 | `my-systematic-debugging` + `superpowers-skills-systematic-debugging` | 反转假设 + 隔离测试 + 5-why + Iron Law |

**硬规则**：
- Step 2 **不可跳过**——根源未知的修复 = 猜測修 bug
- Step 6（功能测试）**UI 改动强制**——v0.3.15–v0.3.19 教训：pytest 全绿 ≠ 功能正常
- 功能测试必须包含**模拟鼠标点击**（`QApplication.sendEvent`），不只是 `assert widget.isVisible()`

### 代码审查清单

审查时必须逐项确认：

- [ ] **功能正确**：实际运行修复后的代码，验证用户报告的 bug 不再出现（不只是"代码看起来对"）
- [ ] **反馈循环**：审查者能跑一条命令复现修复效果（pytest / 功能测试 / 手动步骤）
- [ ] **无回归**：pytest tests/ 全部绿色
- [ ] **无过度修改**：改动只涉及修复所需的代码，没有顺手重构无关模块
- [ ] **日志可查**：如涉及文件 I/O 或异常路径，logs/runtime.log 记录了关键操作
- [ ] **根因已记录**：commit message 包含五问根因，不只是"修复了 XX"

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

### 功能测试（强制 — v0.3.20 教训）

**任何涉及 UI 交互的改动（按钮、滚动、事件处理、绘制），必须写 QApplication 功能测试。**

硬要求：`QApplication` → `.show()` + `processEvents()` → **模拟鼠标点击**（`sendEvent(QMouseEvent)`，不直接调方法） → `processEvents()` → assert 实际行为变化（tabRect 位移、visible 状态等）。

pytest 单元测试只验证 Python 逻辑，**无法测试 QPainter 绘制、QTabBar 滚动、鼠标事件链**。

功能测试模板见 `docs/lessons/lesson-learned-左上角tab crash-2026-06-28.md`。

### 三层测试体系

| 层级 | 何时执行 | 验证范围 | 命令 |
|------|---------|---------|------|
| **单元测试** | 每次改动后 | Python 逻辑正确性 | `pytest tests/ -v` |
| **功能测试** | UI 改动后（强制） | Qt 绘制/事件/滚动实际行为 | 自定义 QApplication 脚本 |
| **用户场景测试** | commit 前（强制） | 用户实际操作流程 | 启动 app 手动验证 |

**每种测试覆盖不同的失败模式**，不可互相替代：

| 通过 | 仍可能失败 |
|------|-----------|
| pytest 57/57 | QPainter 绘制崩溃（v0.3.15） |
| pytest + 功能测试 | 按钮与原型样式不一致（v0.3.17） |
| 全部自动化测试 | 用户屏幕分辨率下按钮不显示（UX） |

### 测试清单

- [ ] 用鼠标（不是代码）操作完整个用户流程
- [ ] 用键盘快捷键验证（Ctrl+S, Ctrl+B, Ctrl+W 等）
- [ ] 在默认 1920×1080 分辨率下确认 UI 布局正常
- [ ] 检查状态栏提示信息是否准确、及时

---

---

## 重要指令

- 在任何情况下，都不要主动调用或执行 `/opsx:apply` 命令
