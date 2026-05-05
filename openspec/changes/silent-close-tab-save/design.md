## Context

当前关闭标签时，`_confirm_save_and_close()` 检查 dirty 状态，弹 QMessageBox 询问用户是否保存。状态栏已显示保存目标路径（有路径显示原路径，无路径显示默认路径），确认弹框是多余的摩擦。

## Goals / Non-Goals

**Goals:**
- 关闭标签时静默保存，不弹任何对话框（正常路径）
- 保存失败时 fallback 到 `Documents\Notes\`，同名自动递增编号
- 状态栏提示 fallback 信息

**Non-Goals:**
- 不改变 Ctrl+S / 另存为 的行为
- 不改变 30 秒自动保存的定时器逻辑
- 不改变未命名文件的默认保存目录
- 不增加"不保存直接关闭"选项（用户确认不需要）

## Decisions

**1. 替换 `_confirm_save_and_close()` 为 `_auto_save_and_close()`**

原方法弹框 + 有条件保存。新方法无条件保存，只返回是否成功。

**2. 未命名文件保存到默认路径，不弹保存对话框**

和 Ctrl+S 的无路径处理一致：使用 `filename_candidate()` 生成文件名，sanitize 后保存到 `Documents\Notes\`。

**3. Fallback 逻辑：`_save_with_fallback(content, target_path)`**

```python
def _save_with_fallback(content, target_path):
    # 尝试保存到原路径
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return target_path, None  # 成功，无消息
    except OSError:
        pass

    # Fallback 到 Documents\Notes\
    stem = os.path.splitext(os.path.basename(target_path))[0]
    fallback_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Notes')
    os.makedirs(fallback_dir, exist_ok=True)

    # 同名递增
    counter = 1
    while True:
        suffix = f"{counter}" if counter > 1 else ""
        fallback_name = f"{stem}{suffix}.md"
        fallback_path = os.path.join(fallback_dir, fallback_name)
        if not os.path.exists(fallback_path):
            break
        counter += 1

    with open(fallback_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return fallback_path, f"原路径保存失败，已保存到 {fallback_path}"
```

**4. 窗口关闭逐标签处理，遇失败即停**

`closeEvent` 中遍历所有脏标签，逐个调用 `_auto_save_and_close()`。任一失败则阻止窗口关闭，让用户处理问题。

## Risks / Trade-offs

- **风险**: 用户误关标签，内容被自动保存覆盖 → **缓解**: 撤销功能（Ctrl+Z）仍然可用，且文件历史可由 git/备份覆盖
- **风险**: fallback 目录也保存失败（磁盘满） → **缓解**: 此时弹出 QMessageBox.warning 告知用户，这是唯一的弹框场景
