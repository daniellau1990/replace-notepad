# Guardrail 方案：CLAUDE.md 工作流强制执行

> 2026-05-03 | 轻量级方案：用 Claude Code Hooks 强制检查计划文件存在性

## 问题

CLAUDE.md 定义了 9 步开发工作流，但 LLM 频繁跳过 Step 1-4，直接写代码+commit。
2026-05-03：3 个 commit、8 个文件、285 行代码，没有任何计划文件。

**根因**：工作流是"道德约束"（文字提醒），不是"物理约束"（强制执行）。

## 方案：三层防御

### Tier 1: CLAUDE.md 重构（预防层）

将工作流从第 141 行移到文件顶部（项目概述之后），添加：
- `MANDATORY — ENFORCED BY HOOKS` 警告框
- `[GATE-N]` 检查点标记
- `QUICK COMPLIANCE CHECK` 自查清单

### Tier 2: PreToolUse Hook — Write/Edit 守卫（拦截层）

```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "python .claude/hooks/workflow_check.py",
    "timeout": 10
  }]
}
```

- 在写入 `notepad/src/**/*.py` 前检查 `docs/plans/` 是否有当日计划文件
- 无计划 → **BLOCK（exit 2）**
- 白名单始终放行：`docs/**`、`Version.md`、`CLAUDE.md`、`*.bat`、`.claude/**`

### Tier 3: PreToolUse Hook — git commit 守卫（最终防线）

```json
{
  "matcher": "Bash(git commit*)",
  "hooks": [{
    "type": "command",
    "command": "python .claude/hooks/workflow_check.py",
    "timeout": 10
  }]
}
```

- 检查暂存文件，非平凡变更 + 无计划 → BLOCK

## 执行顺序（防自锁）

1. 创建 `.claude/hooks/workflow_check.py`
2. 修改 CLAUDE.md
3. 添加 hooks 到 `settings.local.json`
4. 添加权限白名单

## 覆盖范围

| Harness 组件 | 覆盖 |
|-------------|:---:|
| Guardrails & Safety (#9) | ✅ |
| Verification Loops (#10) | ⚠️ 仅检查文件存在 |
| Context Management (#4) | ⚠️ 仅重构 CLAUDE.md |

**覆盖 Harness 12 组件中的 ~1.5/12**

## 优点

- 极简（~120 行 Python + 3 个 hook 配置）
- 快速部署（15 分钟）
- 不会过度阻塞（白名单放行 trivial 文件）
- 符合 Anthropic "薄 harness" 理念

## 不足

- 只检查"计划文件是否存在"，不验证"计划是否被正确执行"
- 不验证测试是否通过
- 不追踪工作流状态（当前处于哪一步）
- Block 后不引导恢复路径
- CLAUDE.md 重构是"提示词工程"不是"上下文工程"
