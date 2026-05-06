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

## MANDATORY WORKFLOW — ENFORCED BY HOOKS

> **PreToolUse hooks will physically BLOCK writes to `notepad/src/**/*.py` and `git commit`
> commands if no plan file exists for today at `docs/plans/YYYY-MM-DD-<feature>.md`.
> This is NOT optional. You MUST complete Steps 1-4 before writing code.**

每次开发任务按以下步骤执行，核心目标：**实现 A 功能，绝不破坏 B 功能**。

### 0. 准备 — 读取上下文
- 任务开始前，AI 必须读取 `openspec/specs/` 中相关的 spec 文件
- 了解已有行为契约，标记"不能破坏"的边界
- [ ] 检查点：spec 已读取

### 1. 需求澄清 → `superpowers-skills-brainstorming`
- 任何修改前，先用 brainstorm 把需求聊透
- 确认：要做什么、不做什么、边界在哪
- [ ] 检查点：需求边界已明确

### 2. 规格先行 → `/opsx:propose`
- 生成 proposal.md + delta spec + design.md + tasks.md
- delta spec 与主 spec 对比，冲突时警告
- [ ] 检查点：proposal 已生成

### 3. 人工审查
- 用户确认 proposal.md 的需求和方向
- **唯一的人工卡点**：方向错了当场纠正，不返工
- [ ] 检查点：用户已批准

### 4. 制定计划 → `superpowers-skills-writing-plans` **[GATE — HOOK ENFORCED]**
- 基于 design 拆解原子 TDD 任务
- 计划保存到 `docs/plans/YYYY-MM-DD-<feature>.md`
- 用户明确同意后方可执行
- [ ] **检查点：计划文件已存在于 docs/plans/ ← 此后才能写代码**

### 5. 执行计划 → `superpowers-skills-subagent-driven-development`
- 每个子代理执行前**必须读取 `openspec/specs/`** 获取上下文
- 逐任务执行，每完成一个 task 即 commit

### 6. 测试验证（两层）
- **TDD（`superpowers-skills-test-driven-development`）**：
  写新代码前先写测试，保证新功能正确
- **全量回归（`pytest tests/`）**：
  所有改动完成后跑全部测试，保证旧功能没坏
- 有任何一个 FAIL → 修好再继续，不到下一步

### 7. 归档记忆 → `/opsx:archive`
- delta spec 合并到 `openspec/specs/`，知识库自更新
- 下一次 AI 任务自动读取，不再遗忘

### 8. 版本锚点 → git
- `git commit` + 更新 `Version.md`
- `git tag vX.Y.Z`：出问题可精确回退

### 9. 调试（按需） → `my-systematic-debugging` + `superpowers-skills-systematic-debugging`
- 遇到 bug 时，同时调用两个 skill 定位根因
- 先查根因，再走 ②→⑧ 修复流程

### QUICK COMPLIANCE CHECK

在写代码之前，自查以下清单（全部 YES 才能动手）：

- [ ] 我读了 `openspec/specs/` 吗？（Step 0）
- [ ] 我和用户做了 brainstorm 吗？（Step 1）
- [ ] 我运行了 `/opsx:propose` 吗？（Step 2）
- [ ] 用户批准了 proposal 吗？（Step 3）
- [ ] **`docs/plans/YYYY-MM-DD-<feature>.md` 存在吗？（Step 4）← HOOK 强制检查**

**如果任何一个答案是 NO，不要写代码。按顺序走完前面的步骤。**

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

## 苏格拉底式五问五答调试法

### 核心原则

**先观测事实，再找根因。** 不要猜原因，要问问题——连续追问五次，每问一层，直到底层机制暴露。

### 五问流程

| 问次 | 问题 | 目的 |
|------|------|------|
| 第一问 | 我实际看到了什么？（精确描述现象） | 建立事实基线 |
| 第二问 | 什么没坏？（界定问题边界） | 缩小排查范围 |
| 第三问 | 两边的差异是什么？（A/B 对比） | 隔离关键变量 |
| 第四问 | 这个差异的底层机制是什么？ | 找到直接原因 |
| 第五问 | 如果根因在此，能解释所有现象吗？ | 验证根因完整性 |

### 示例

```
现象: 字体对话框改了大小，编辑器不变

第一问: 实际看到什么？
答: 滑块拖动后预览变，但编辑器文字大小不变

第二问: 什么没坏？
答: 预览区字体变了，设置值保存了（重启后读到新值）

第三问: 预览 vs 编辑器差异是什么？
答: 预览用的是 QLabel.setFont()，编辑器有 lexer

第四问: lexer 的机制是什么？
答: lexer 每个 style 独立存储 font，优先级高于 editor.setFont()

第五问: 能解释全部现象吗？
答: 能——editor.setFont() 改了但被 lexer 覆盖，预览没 lexer 所以生效
→ 根因: lexer style 字体未同步更新
```

### 适用场景

- 任何 bug 调查开始前，先走完五问再动手
- 五问走不通 → 说明观测不够，回第一问补充事实
- 禁止跳过观测直接猜原因

---

## 重要指令

- 在任何情况下，都不要主动调用或执行 `/opsx:apply` 命令
