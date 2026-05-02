# AI 辅助开发工作流 v2.0 — 不返工方案

> 综合 OpenSpec + Superpowers + 用户验证，2026-05-02 定稿
> 目标：实现 A 功能，绝不破坏 B 功能

## 8 步闭环

```
① brainstorm      →  需求澄清，落代码前先吵明白
② /opsx:propose   →  生成 proposal + delta spec + design
③ 人工审查         →  确认方向和规格，方向错了当场纠正
④ writing-plans   →  基于 design 拆解原子 TDD 任务
⑤ /opsx:apply     →  子代理执行，每个子代理读取 specs/ 获取上下文
⑥ pytest tests/   →  全量回归，所有测试必须通过（不是只跑新测试）
⑦ /opsx:archive   →  delta spec 合并到主 spec，知识库更新
⑧ git tag vX.Y.Z  →  回退锚点
```

## 为什么不返工

| 步骤 | 防护 | 原理 |
|------|------|------|
| ① brainstorm | 需求偏差 | 在聊代码前把需求吵透，AI 不瞎猜 |
| ② /opsx:propose | 规格遗漏 | 生成 delta spec，冲突时可见 |
| ③ 人工审查 | 方向错误 | 唯一的人工卡点，错了当场纠正 |
| ⑤ 子代理读 specs | 无知破坏 | 每个子代理带着"已有行为契约"写代码 |
| ⑥ 全量回归 | 隐性破坏 | 旧测试 FAIL = 当场发现，当场修 |
| ⑦ /opsx:archive | 记忆丢失 | spec 自更新，下次 AI 有"记忆" |
| ⑧ git tag | 无法回退 | 出问题精确回退到上一个干净版本 |

## 工具分工

| 工具 | 职责 | 阶段 |
|------|------|------|
| **Superpowers** | 管设计和执行 | ① brainstorm, ④ writing-plans, ⑤ 子代理 |
| **OpenSpec** | 管规格和记忆 | ② propose, ⑦ archive |
| **pytest** | 管质量验证 | ⑥ 全量回归 |
| **git** | 管版本锚点 | ⑧ tag |

## 与 CLAUDE.md 现有工作流的关系

```
现有：  writing-plans → subagent-dev → test → commit + tag
新版：  brainstorm → propose → 审查 → writing-plans → apply → 全量测试 → archive → tag
```

新版多了 4 步：① brainstorm（需求澄清）、② propose（规格先行）、③ 审查（人工卡点）、⑦ archive（记忆沉淀）。其余步骤保留。

## 已就位的 baseline spec

```
openspec/specs/
├── autosave/spec.md          # 自动保存行为
├── file-naming/spec.md       # 文件名过滤规则
├── tab-management/spec.md    # 标签页行为
├── status-bar/spec.md        # 状态栏显示
└── markdown-editor/spec.md   # 编辑器功能
```

## 参考来源

- `C:\Users\surface\Documents\Notes\code工作流.md` — OpenSpec + Superpowers 工作流经验
- 本项目实际开发经历 v0.1.0 ~ v0.3.6
- `.md 递增 bug` 调试过程 — 全量回归测试的必要性验证
