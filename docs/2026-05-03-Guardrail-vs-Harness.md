# Guardrail vs Harness 方案对比

> 2026-05-03 | 两种工作流强制执行方案的设计哲学、覆盖范围和实施路径对比

---

## 一句话区分

| 方案 | 本质 | 类比 |
|------|------|------|
| **Guardrail** | 门禁 — "没过这门不许进" | 工地围栏：拦住危险区域 |
| **Harness** | 脚手架 — "给你搭好架子再干活" | 建筑脚手架：提供完整的施工环境 |

---

## 设计哲学

| 维度 | Guardrail | Harness |
|------|-----------|---------|
| **核心理念** | 拦截违规行为 | 引导正确行为 |
| **关注点** | "什么不能做" | "应该怎么做" |
| **触发时机** | 违规发生时（事后拦截） | 工作开始前 + 进行中 + 结束后 |
| **失败模式** | Block 后 LLM 不知所措 | Block 后引导 LLM 回到正确路径 |
| **覆盖范围** | 1.5/12 组件 | 6/12 组件 |
| **实施时间** | ~1 小时 | ~6 小时（4 个 Phase） |

---

## 功能逐项对比

| 功能 | Guardrail | Harness |
|------|:---:|:---:|
| 计划文件存在性检查 | ✅ | ✅ |
| 源码写入前拦截（PreToolUse Write/Edit） | ✅ | ✅ |
| git commit 拦截 | ✅ | ✅ |
| CLAUDE.md 重构（工作流前置） | ✅ | ✅ |
| 白名单路径放行 | ✅ | ✅ |
| **测试执行验证（Stop hook）** | ❌ | ✅ |
| **Python 语法自动检查（PostToolUse）** | ❌ | ✅ |
| **恢复引导（block 时提示下一步）** | ❌ | ✅ |
| **动态上下文注入（SessionStart）** | ❌ | ✅ |
| **工作流状态追踪（JSON 文件）** | ❌ | ✅ |
| **高危命令拦截** | ❌ | ✅ |
| **上下文分层策略** | ❌ | ✅ |
| **验证循环（三层验证）** | ❌ | ✅ |

---

## Hooks 配置对比

### Guardrail（3 个 hooks）

```
PreToolUse (Write|Edit)        → 检查计划文件
PreToolUse (Bash git commit*)  → 检查计划文件 + 暂存文件
```

### Harness（7 个 hooks）

```
SessionStart                   → 动态上下文注入 + 工作流状态读取
PreToolUse (Write|Edit)        → 检查计划文件 + 工作流阶段校验
PreToolUse (Bash git commit*)  → 检查计划文件 + 测试是否通过
PreToolUse (Bash)              → 高危命令拦截
PostToolUse (Edit)             → Python 语法自动检查
Stop                           → 强制测试执行验证
PostToolUseFailure             → 工具失败恢复引导
```

---

## 恢复引导对比

### Guardrail block 输出
```
WORKFLOW CHECK: Action BLOCKED
No plan file found in: docs/plans/
```
→ **只告诉 LLM 被阻断了，不告诉它怎么办**

### Harness block 输出
```
WORKFLOW CHECK: Action BLOCKED
No plan file found. To proceed:
  1. Skill("superpowers-skills-brainstorming") — clarify requirements
  2. Skill("openspec-propose") — generate proposal + specs
  3. Ask user for approval
  4. Skill("superpowers-skills-writing-plans") — write plan
After all steps complete, retry your action.
```
→ **明确告知恢复路径，引导 LLM 回正轨**

---

## 上下文管理对比

| 维度 | Guardrail | Harness |
|------|-----------|---------|
| CLAUDE.md | 静态文本前移 | 工作流开头+结尾双位置，防止"Lost in the Middle" |
| SessionStart | 无 | 动态检查：无计划则注入完整工作流，有计划则注入执行模式 |
| 状态追踪 | 无 | `.claude/workflow_state.json` — 9 步中当前处于哪一步 |
| 记忆系统 | 不涉及 | 新增 `workflow_state.md` memory，跨会话持久化 |

---

## 风险对比

| 风险 | Guardrail | Harness |
|------|-----------|---------|
| **过度阻塞** | 低（只检查文件存在） | 中（多层检查，需调优） |
| **阻塞后卡死** | **高**（无恢复引导） | 低（block 时引导下一步） |
| **维护成本** | 低（1 个脚本） | 中（3 个脚本 + 状态文件） |
| **假阳性** | 中（有今日计划但非本功能） | 低（检查更全面） |
| **性能开销** | 低（每次 Write/Edit ~200ms） | 中（每次 Edit + PostToolUse） |
| **LLM 绕过** | 中（可能用 Bash 绕过 Write） | 低（多层防御） |

---

## 文章对标：覆盖 Harness 12 组件

| # | 组件 | Guardrail | Harness |
|---|------|:---:|:---:|
| 1 | 编排循环 | N/A（Claude Code 自带） | N/A |
| 2 | 工具 | N/A | N/A |
| 3 | 记忆 | ❌ | ✅ |
| 4 | 上下文管理 | ⚠️ 半覆盖 | ✅ |
| 5 | 提示词构建 | ❌ | ✅ |
| 6 | 输出解析 | N/A | N/A |
| 7 | 状态管理 | ❌ | ✅ |
| 8 | 错误处理 | ❌ | ✅ |
| 9 | 防护栏和安全 | ✅ | ✅ |
| 10 | 验证循环 | ❌ | ✅ |
| 11 | 子智能体编排 | N/A | N/A |
| 12 | 框架实现 | N/A | N/A |
| **覆盖率** | | **1.5/12** | **6/12** |

---

## 七个设计决策对比

| # | 决策 | Guardrail | Harness | 文章建议 |
|---|------|:---:|:---:|---------|
| 1 | 单智能体 vs 多智能体 | 单 | 单 | ✅ 先最大化单个 agent |
| 2 | ReAct vs 计划-执行 | 未考虑 | 计划-执行 | ✅ 快 3.6 倍 |
| 3 | 上下文管理策略 | 未考虑 | 即时检索+结构化笔记 | ✅ 5 种方法选 2 |
| 4 | 验证循环设计 | 未考虑 | 计算验证为主 | ✅ 确定性真相 |
| 5 | 权限和安全 | 限制性 | 限制性 | ✅ 适合本项目 |
| 6 | 工具范围策略 | 未考虑 | 默认工具集 | ⚠️ 未做精简 |
| 7 | Harness 厚度 | 极薄 | 薄 | ✅ 遵循 Anthropic 哲学 |

---

## 适用场景

| 场景 | 推荐方案 |
|------|---------|
| 快速试验、个人项目 | **Guardrail** — 够用，不拖慢节奏 |
| 团队协作、多人开发 | **Harness** — 多层防护 + 恢复引导 |
| 需求不稳定的早期项目 | **Guardrail** — 轻量，随时改 |
| 需合规/审计的生产项目 | **Harness** — 状态追踪 + 完整记录 |
| 当前项目（replace_txt） | **Guardrail → Harness** 渐进式 |

---

## 推荐路径

```
Phase 1 (本周): Guardrail
  → 1 小时上线，先堵住"跳步写代码"的漏洞

Phase 2 (下周): +验证循环
  → 加 Stop hook + PostToolUse 语法检查

Phase 3 (本月): +上下文工程
  → 加 SessionStart 动态注入 + 状态追踪

Phase 4 (按需): 持续简化
  → 模型升级后删除不必要的 hook
```

**核心原则**（来自文章）："Harness 不是目的，是手段。当新模型内化了当前需要强制执行的规则时，应主动删除对应的 harness 复杂度。"

---

## 文件清单

| 文件 | 方案 |
|------|------|
| `docs/2026-05-03-Guardrail.md` | Guardrail 详细设计 |
| `docs/2026-05-03-Harness.md` | Harness 详细设计 |
| `docs/2026-05-03-Guardrail-vs-Harness.md` | 本文（对比） |
