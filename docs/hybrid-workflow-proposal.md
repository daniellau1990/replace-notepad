# 混合工作流方案：防止"实现A功能，破坏B功能"

> 草案 — 待讨论确认后正式纳入 CLAUDE.md

## 流程图

```
┌─────────────────────────────────────────────────────────┐
│                    每次变更前                           │
│                                                         │
│  1. AI 读取 openspec/specs/ 相关 spec                   │
│     ├─ 了解已有行为契约                                  │
│     └─ 标记"不能破坏"的边界                              │
│                                                         │
│                    每次变更中                           │
│                                                         │
│  2. /opsx:propose "功能描述"                            │
│     ├─ 生成 delta spec（本次要改什么）                   │
│     ├─ 生成 tasks（执行步骤）                            │
│     └─ delta spec 与主 spec 对比，冲突时警告             │
│                                                         │
│  3. /opsx:apply → 执行 tasks                            │
│     └─ TDD：先写测试，再写实现                            │
│                                                         │
│  4. 运行 全部 测试（不只是新测试）                         │
│     └─ 回归检测：旧功能坏了 = 测试 FAIL                  │
│                                                         │
│                    每次变更后                           │
│                                                         │
│  5. /opsx:archive                                      │
│     └─ delta spec → 合并到主 spec（活文档更新）           │
│                                                         │
│  6. git tag vX.Y.Z                                     │
│     └─ 万一出问题，可精确回退到此版本                     │
└─────────────────────────────────────────────────────────┘
```

## 三层防护

| 层级 | 机制 | 作用 | 时机 |
|------|------|------|------|
| **事前** | AI 读 `openspec/specs/` | 知道不能破坏什么 | 编码前 |
| **事中** | 全量回归测试 | 当场发现破坏 | `pytest tests/` |
| **事后** | `git tag` | 出问题就回退 | 发布后 |

## 和当前工作流的关系

```
现在是：writing-plans → subagent-dev → test → commit + tag
改为：  /opsx:propose → /opsx:apply → pytest tests/ → /opsx:archive → git tag
                                                   ↑
                                          关键：跑全量，不是只跑新测试
```

## 关键新增：回归测试

现有 57 个测试就是最好的"B 功能保护网"。每次改完，`pytest tests/` 跑全部，有一个 FAIL 就说明破坏了旧功能——根本到不了 archive/commit 那步。

## baseline spec 已就位

```
openspec/specs/
├── autosave/spec.md          # 自动保存行为定义
├── file-naming/spec.md       # 文件名过滤规则
├── tab-management/spec.md    # 标签页行为
├── status-bar/spec.md        # 状态栏显示规范
└── markdown-editor/spec.md   # 编辑器功能
```

## 待讨论

- [ ] 是否用 `/opsx:propose` 替代 `writing-plans`？
- [ ] 回归测试是否加入 pre-commit hook？
- [ ] CLAUDE.md 中是否需要精简现有工作流，避免两套并存？
