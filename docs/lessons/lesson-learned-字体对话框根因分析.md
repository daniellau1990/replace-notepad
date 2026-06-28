# Lesson Learned — 字体对话框改了大小，编辑器不变

> 来源: CLAUDE.md 苏格拉底式五问五答示例（已从主文件移除）
> 调试方法: my-systematic-debugging + 5-why

## 现象

格式 → 字体 → 拖动滑块改大小。预览区生效。编辑器不生效。

## 调试过程

### Step 1: 看日志

```
[2026-05-06 10:23:01] [INFO] App started v0.3.10
[2026-05-06 10:23:15] [INFO] Font size changed: 11 → 14
```

pytest: 57 passed — 不是崩溃级 bug，是行为逻辑问题。

### Step 2: 看现场

- 预览区 QLabel: 字体变为 14pt ✓
- 编辑器: 字体仍为 11pt ✗
- 重新打开格式菜单: 显示 14pt（设置存了）

### Step 3: 五问

**第一问**: 日志和现场显示了什么？
→ 日志记录字体变更成功，预览生效但编辑器未生效。

**第二问**: 什么没坏？
→ 预览区、设置持久化、滑块 UI 都正常。

**第三问**: 预览 vs 编辑器差异是什么？
→ 预览用 QLabel.setFont()，编辑器有 QsciLexerMarkdown。

**第四问**: lexer 的机制是什么？
→ lexer 每个 style 独立存储 font，优先级高于 editor.setFont()。

**第五问**: 能解释全部现象吗？
→ 能——editor.setFont() 被 lexer 覆盖，预览无 lexer 所以生效。

## 根因

`MarkdownLexer` 在每个 style 里硬编码了字体大小（QFont("Consolas", size)），lexer 的字体优先级高于 editor.setFont()，editor 字体改完立刻被 lexer 覆盖回去。

## 修复

给 MarkdownLexer 添加 `update_font_size(new_size)` 方法，重建所有 style 的字体。
