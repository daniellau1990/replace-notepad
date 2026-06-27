# 2026-06-27 Bug Fix 计划

## #1 修复 CRLF 行间空行

| 文件 | 行号 | 修改 |
|------|------|------|
| `file_handler.py` | 34 | `open(path, "w", encoding="utf-8")` → `open(path, "w", encoding="utf-8", newline='')` |
| `autosave.py` | 79 | 同上 |
| `app.py` | 425, 445 | 同上 (2处) |

## #3 启动零标签

| 文件 | 行号 | 修改 |
|------|------|------|
| `app.py` | 187 | 删除 `self._new_tab()` |

## #4/5 路径文字可自由选中 + 右键全选并复制

| 文件 | 修改 |
|------|------|
| `app.py` ClickablePathWidget | 删除 `self._path.installEventFilter(self)` (line 37) 和 `eventFilter()` (line 41-47) |
| `app.py` `_on_context_menu` | 增加 `全选并复制` 菜单项 |

## #7 双击路径弹窗

| 文件 | 修改 |
|------|------|
| `app.py` ClickablePathWidget | 安装 `eventFilter` 只监听 `MouseButtonDblClick` → `_change_default_dir()` |

---

## #6 左侧滚动箭头 (Feature)

| 文件 | 修改 |
|------|------|
| `tab_manager.py` | 子类化 QTabBar，重写 `tabSizeHint` 或使用 `setUsesScrollButtons(true)` + 左侧按钮布局 |

注: #6 为 Feature 轨道，先完成 Bug Fix 后再单独处理。

---

## 执行顺序

1. #1 CRLF fix (4 file changes)
2. #3 Remove default tab
3. #4/5 Path text interaction
4. #7 Path double-click
5. 回归测试 `pytest tests/`
6. git commit + Version.md
