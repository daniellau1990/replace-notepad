# 拖放打开文件 — 实施计划

## 影响文件

- `notepad/src/app.py` MainWindow — 新增 dragEnterEvent / dropEvent

## 实施步骤

### 1. MainWindow.dragEnterEvent

```
event.mimeData().hasUrls() → 遍历 URL：
  - 是本地文件 + 非图片 → event.acceptProposedAction() → return
  - 是本地文件 + 图片   → pass（留给 Editor 处理）
其他 → super().dragEnterEvent(event)
```

### 2. MainWindow.dropEvent

```
event.mimeData().hasUrls() → 遍历 URL：
  - 图片文件 → continue（Editor.dropEvent 会处理，先执行 super）
  - 非图片本地文件 → 收集路径
其他 → super().dropEvent(event)

对收集到的路径：
  - 已打开（_file_paths 中） → 切到对应标签
  - 新文件 → _new_tab(content, path)
  - 解码失败 → 静默跳过

最后：根据是否已有标签决定是否激活第一个新文件
```

### 3. 编辑器图片拖放不受影响

Editor.dragEnterEvent/dropEvent 保持原样——MainWindow 的 dropEvent 必须调用 super().dropEvent(event) 让事件继续传播到 Editor。

### 关键逻辑

```python
def dragEnterEvent(self, event):
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if not Editor._is_image_file(path):
                    event.acceptProposedAction()
                    return
    super().dragEnterEvent(event)

def dropEvent(self, event):
    paths = []
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if Editor._is_image_file(path):
                    continue  # let Editor handle
                paths.append(path)
    
    # Super first → let Editor handle images
    super().dropEvent(event)
    
    if not paths:
        return
    
    opened = 0
    for path in paths:
        # Check duplicate
        existing = None
        for eid, editor, p, _ in self._tab_manager.all_editors():
            if p == path:
                existing = eid
                break
        if existing is not None:
            # Switch to existing tab
            self._tab_manager.setCurrentWidget(editor)
            continue
        
        try:
            content = self._file_handler.read_file(path)
            editor = self._new_tab(content, path)
            self._file_handler.add_recent(path)
            opened += 1
        except Exception:
            pass  # silent skip for binary/unreadable
    
    # If no tabs existed before, activate first new tab
    # (handled naturally: _new_tab calls setCurrentWidget)
```

## 验收

见 PRD `2026-06-28-拖放打开文件.md` 验收标准。
