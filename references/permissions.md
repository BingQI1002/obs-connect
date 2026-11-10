# 自动写入与必要授权

优先用宿主已有文件/设置/电脑操作工具。授权由真实工具或系统提示完成，获准后 Agent 自动续做；不要交给用户粘贴指令，也不修改安全配置来放宽权限。

## 文件型入口：Codex / Claude Code

原生文件工具即可完成。需要助手时，由 Agent 调用：

```text
python3 scripts/configure_entry.py prepare --host codex --vault <已选库> --work-dir <库外工作目录>
python3 scripts/configure_entry.py apply --plan <返回的plan.json> --plan-sha256 <返回的摘要>
```

Claude Code 改用 `--host claude-code`；实际配置目录不同则传 `--config-root`。准备/备份/摘要/并发检查均在内部完成，保留托管区外原文。更新脚本路径来自运行助手的安装位置，须从正式安装副本执行，不能使用下载暂存目录。

文件写入受限时，申请宿主原生的本次目标写入/执行权限，批准后重跑同一条命令。例如工具支持时用真正的 `sandbox_permissions: require_escalated` 参数，不让用户复制参数到终端。用户拒绝或策略禁止就暂停该操作，报告具体未完成项。

## WorkBuddy 的指令字段

已有设置/电脑操作工具时直接读取、合并、保存并读回“给 WorkBuddy 的指令”。macOS 仅有本机命令工具时，可使用已授权的 JXA 后端：

```text
osascript -l JavaScript scripts/workbuddy_ui_macos.js inspect <库外唯一文件.txt>
python3 scripts/configure_entry.py prepare --host workbuddy --vault <已选库> --work-dir <库外工作目录> --before-ui-file <刚读取的文件.txt>
osascript -l JavaScript scripts/workbuddy_ui_macos.js apply <plan.json> <返回的摘要>
```

首次使用系统界面自动化，先取得用户对操作 WorkBuddy 界面的授权。若返回 `needs_system_permission`，**当次立即停在这里**，简短提示给实际执行宿主开启所需的辅助功能/自动化权限。授权范围针对宿主进程，比单个指令字段宽；系统开关由用户操作。用户确认后再重试一次，仍失败就报告未接通，不换进程反复试，不笼统要求重启所有软件。

读取完整已保存原文，不能以富文本编辑器渲染后的文本代替含注释原文；用户有未保存编辑时暂停。脚本会临时使用并恢复剪贴板，用户并发复制时保留其新内容。缺工具或界面版本不匹配时说清缺口，不改长期记忆、人设、内部数据库或程序包作替代。Windows/Linux 使用宿主实际已有工具，本包没有这些系统的独立界面后端。

当前后端不支持可靠替换带 YAML 元信息的指令，返回 `unsupported_rich_text` 时原文不改，停止自动编辑；已有能处理此格式的宿主设置工具才继续，不能循环重试或把编辑框显示变化当成保存成功。

官方依据：[Codex 审批](https://learn.chatgpt.com/docs/agent-approvals-security) · [Claude 权限](https://code.claude.com/docs/en/permissions) · [WorkBuddy 权限](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes) · [Apple 界面自动化](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/AutomatetheUserInterface.html)。
