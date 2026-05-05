# Phase 4: Path Click + Default Editor — Implementation Plan

**Goal:** 状态栏左键点击改路径 + 设为默认编辑器 + #15 跳过(无限制)

---

### Task 1: Left-click path widget to change dir

**File:** `notepad/src/app.py` — ClickablePathWidget class (line 18-72)

Add mousePressEvent that triggers _change_default_dir on left click.

### Task 2: Set as default Windows editor

**File:** `notepad/src/app.py` — MainWindow file_menu section

Add "设为默认编辑器" menu item → write HKCU\Software\Classes registry for .md/.txt association.

### Task 3: Regression + version → v0.3.13
