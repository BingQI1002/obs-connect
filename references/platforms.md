# 宿主入口

只读当前宿主这一行；Skill 目录负责安装，全局入口负责以后任务读取 OBS 规则。

| 宿主 | 实际全局入口 | 安装位置 |
|---|---|---|
| Codex 本机 | 实际 `CODEX_HOME`（默认 `~/.codex`）中的非空 `AGENTS.override.md` 优先，否则 `AGENTS.md`；不新建 override 遮蔽原规则 | 优先宿主安装器，常用 `~/.agents/skills/obs-connect/`，已有受支持位置直接复用 |
| Claude Code | 实际 `CLAUDE_CONFIG_DIR`（默认 `~/.claude`）中的 `CLAUDE.md`；托管区内独立加入原生 `@绝对路径` 导入，路径空格前加反斜杠，不加引号或代码块 | 实际用户配置目录下 `skills/obs-connect/` |
| WorkBuddy 桌面 | 设置 → 个性化 → **给 WorkBuddy 的指令** | 优先实际原生导入工具；已有被宿主识别的安装直接复用，否则导入完整 ZIP |

- 不用自动记忆、人设或项目规则冒充全局入口。WorkBuddy 的 `AGENTS.md` / `.codebuddy` 兼容说明属于代码开发配置，普通办公不能据此宣称全局生效。
- 文件型入口用正常文件工具，必要时用 `configure_entry.py`；WorkBuddy 用现有设置/电脑操作工具，macOS 可用随包界面后端，详见 [授权方法](permissions.md)。不要猜内部 JSON/数据库字段。
- 修复误写位置：先存正确入口并读回，再仅移除原位置属于本 Skill 的同目标区块；保留其他内容。
- 工具只能访问云端时，先说明本机通路未接通。规则文件可读不等于当前任务可写；权限按实际操作申请。

官方依据：[Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md) · [Claude Code](https://code.claude.com/docs/en/memory) · [WorkBuddy 设置](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Setting) · [代码开发配置范围](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)。
