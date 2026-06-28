# Lesson Learned — v0.3.15 → v0.3.19 六版迭代复盘

> 日期: 2026-06-28
> 触发事件: 左侧滚动箭头功能，6 个版本才修好
> 影响: 工作流 V1→V2→V3 三次升级

---

## 一、时间线

| 版本 | 现象 | 我的做法 | 实际根因 |
|------|------|---------|---------|
| v0.3.15 | 单击左箭头崩溃 | 改 drawPolygon | `drawPolygon(QPoint)` 匹配错误 PyQt6 重载 |
| v0.3.16 | 按钮可见，单击无效 | 加 QPolygon + try-except | **`ensureVisible` 在 PyQt6 中不存在**，被 try-except 吞掉 |
| v0.3.17 | 按钮完全消失 | 换 QStyle 方案（100+ 行重写） | `QStyleOptionTab` 不是画箭头的正确 option type |
| v0.3.18 | 同 v0.3.16 | 回到 QPainter + 修逻辑 | 仍用不存在的 `ensureVisible`，逻辑改了没改根因 |
| v0.3.19 | 单击崩溃（同 v0.3.15） | 合成事件驱动 | 无限递归——合成事件触发自己的 handler |
| v0.3.20 | **功能正确** | 加防重入守卫 + 功能测试 | 三者结合：QPainter 渲染 + 合成事件滚动 + 防递归 |

**耗时**: 6 个版本 × ~30 行/版 = ~200 行无效代码，用户手动测试 5 次失败。

---

## 二、五问根因

### 第一问：为什么同一错误（滚动无效）发生 6 次？

每次只修**症状**（崩溃→外观→逻辑→外观→递归），从不验证**功能本身**。

### 第二问：为什么不验证功能？

没有 QApplication 功能测试。只跑 `pytest`（57 单元测试全绿），但 pytest 测不了 QTabBar 滚动行为。

### 第三问：为什么没有功能测试？

依赖用户手动 UX 验证。代码改了 → pytest 过了 → "应该可以了" → 用户发现不行。

### 第四问：为什么觉得"应该可以了"？

**先入为主**——读代码 → 形成理论 → 相信理论 → 跳过验证。这是调试方法论 Pitfall 1。

### 第五问：为什么理论优先于观测？

没有 **feedback loop**（`mattpocock-skills-diagnosing-bugs` Phase 1 核心要求）。没有一条命令能自动化验证"滚动是否真的工作了"。

**终极根因: 没有 tight feedback loop。pytest 全绿 ≠ 功能正常，但没有第二层测试验证实际 UI 行为。**

---

## 三、Anti-Bulldozer 模式（`Shen_Huang_debugging_skill_auto_research`）

本次完美展示了该 skill 描述的 **#1 AI 调试失败模式**：

> "Agent forms a theory, writes 150 lines of fix code, it doesn't work,
> so it writes another 150 lines going deeper into the same wrong theory."

我的**推土机轨迹**：
```
理论1: "drawPolygon 问题"  → 修 40 行  → 崩溃
理论2: "加 QPolygon 就行"  → 修 30 行  → 无效
理论3: "QStyle 更原生"     → 修 100 行 → 按钮消失
理论4: "回到 QPainter"     → 修 60 行  → 无效
理论5: "合成事件驱动"       → 修 50 行  → 递归崩溃
理论6: "加防重入守卫"       → 修 20 行  → 终于正确
```

**如果遵循 Anti-Bulldozer 规则（每实验 ≤5 行）**：
- 第 1 个实验应是 `print(hasattr(bar, 'ensureVisible'))` → 立即发现不存在
- 第 2 个实验应是扫描原生按钮位置 → 找到 x=0 和 x=bw-46
- 第 3 个实验应是合成事件滚动测试 → 验证方案可行
- 然后才写正式代码 → 一次通过

---

## 四、Debug Skills 贡献排名

| 排名 | Skill | 贡献率 | 如果一开始就用 |
|------|-------|--------|--------------|
| #1 | `Shen_Huang_debugging_skill_auto_research` | 40% | Anti-Bulldozer 防止 5 次无效迭代 |
| #2 | `mattpocock-skills-diagnosing-bugs` | 35% | Feedback loop 在 v0.3.15 就发现 API 不存在 |
| #3 | `my-systematic-debugging` | 15% | 反转假设 → "什么没坏？原生右侧按钮还能用" |
| #4 | `superpowers-skills-systematic-debugging` | 10% | Iron Law: 不查根因不修 bug |

---

## 五、驱动的工作流变更

| 教训 | 工作流变更 | 版本 |
|------|-----------|------|
| 小 bug 也走 9 步太重 | 引入两轨制（Feature / Bug Fix） | v0.3.14 |
| Hook 机械门禁太僵化 | 删除 Gate 1（计划文件），保留 Gate 2（Version.md） | v0.3.14 |
| 没有反馈循环 | Bug Fix Step 2 三联 skill 调用（**一开始就引入，不等失败**） | v0.3.21 |
| 功能测试缺失 | Step 6 功能测试 + 模拟鼠标点击强制 | v0.3.21 |
| 设计阶段不验证 API | Feature Step 2 增加设计探针（API 存在性 + 集成点） | v0.3.22 |
| 修复后没有审查 | 代码审查清单 6 项（两条轨道都有） | v0.3.20 |
| 直觉修 bug 反复失败 | 三层测试体系（单元 + 功能 + 场景） | v0.3.20 |

---

## 六、新增的防御层（V3.2 工作流）

```
Feature 轨道:  领域建模 → [设计探针] → 计划 → 审查 → TDD → 功能测试(含鼠标) → 审查 → 回归
Bug Fix 轨道:  需求界定 → [三联诊断] → 计划 → 审查 → TDD → 功能测试(含鼠标) → 审查 → 回归
```

**两个关键入口**:
- Feature: 设计阶段就验证 API（不等编码才发现）
- Bug Fix: 一进入诊断就调 3 个 skill（不等失败才补救）

---

## 七、核心教训（一句话）

**"写代码之前，先写一个 5 行脚本证明你的假设是对的——测试不是事后的检查，是事前的验证。"**
