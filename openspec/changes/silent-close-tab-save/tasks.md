## 1. Core Implementation

- [ ] 1.1 Add `_save_with_fallback(content, target_path)` method — try save to target, fallback to Documents\Notes with auto-increment naming, return (actual_path, warning_message_or_None)
- [ ] 1.2 Replace `_confirm_save_and_close()` with `_auto_save_and_close(editor)` — check dirty, call `_save_with_fallback`, mark clean, return True/False
- [ ] 1.3 Update `_close_tab()` to call `_auto_save_and_close()` instead of `_confirm_save_and_close()`
- [ ] 1.4 Update `closeEvent()` to call `_auto_save_and_close()` instead of `_confirm_save_and_close()`

## 2. Testing

- [ ] 2.1 Manual test: close dirty tab with known path — verify silent save, no dialog
- [ ] 2.2 Manual test: close dirty unnamed tab — verify auto-save to Documents\Notes
- [ ] 2.3 Manual test: close clean tab — verify no save, no dialog
- [ ] 2.4 Manual test: close window with multiple dirty tabs — verify all saved silently
- [ ] 2.5 Manual test: save failure fallback — verify auto-increment naming in Documents\Notes
- [ ] 2.6 Run `pytest tests/` for regression
