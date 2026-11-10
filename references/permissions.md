# 自动写入与必要授权

优先用宿主已有文件/设置/电脑操作工具，获准后自动续做。确实不能自动写入时，提供准确入口和已填好的短指令，清楚交接一次；不修改安全配置来放宽权限。若管理策略禁止目标改动本身，只说明限制，不引导绕过。

## 文件型入口：Codex / Claude Code

原生文件工具即可完成。需要助手时，由 Agent 调用：

```text
python3 scripts/configure_entry.py prepare --host codex --vault <已选库> --work-dir <库外工作目录>
python3 scripts/configure_entry.py apply --plan <返回的plan.json> --plan-sha256 <返回的摘要>
```

Claude Code 改用 `--host claude-code`；实际配置目录不同则传 `--config-root`。准备/备份/摘要/并发检查均在内部完成，保留托管区外原文。更新脚本路径来自运行助手的安装位置，须从正式安装副本执行，不能使用下载暂存目录。

文件写入受限时，申请宿主原生的本次目标写入/执行权限，批准后重跑同一条命令。例如工具支持时用真正的 `sandbox_permissions: require_escalated` 参数，不让用户复制参数到终端。仍无法自动写入时，给出已核实的目标文件完整路径和指令正文，引导用户在编辑器保存，保留其他规则。

## WorkBuddy 的指令字段

已有设置/电脑操作工具时直接读取、合并、保存并读回“给 WorkBuddy 的指令”。macOS 仅有本机命令工具时，可使用已授权的 JXA 后端：

```text
osascript -l JavaScript scripts/workbuddy_ui_macos.js inspect <库外唯一文件.txt>
python3 scripts/configure_entry.py prepare --host workbuddy --vault <已选库> --work-dir <库外工作目录> --before-ui-file <刚读取的文件.txt>
osascript -l JavaScript scripts/workbuddy_ui_macos.js apply <plan.json> <返回的摘要>
```

首次使用系统界面自动化，先取得用户授权。返回 `needs_system_permission` 时只提示必要的辅助功能/自动化授权，范围针对执行宿主，比单个字段宽，开关由用户操作。用户确认后再试一次；仍失败或不想授予自动化权限，就进入下面的人工交接，不换进程反复试，不要求重启所有软件。

读取完整已保存原文，不能以富文本编辑器渲染后的文本代替含注释原文；用户有未保存编辑时暂停。脚本会临时使用并恢复剪贴板，用户并发复制时保留其新内容。缺工具或界面版本不匹配时说清缺口，不改长期记忆、人设、内部数据库或程序包作替代。Windows/Linux 使用宿主实际已有工具，本包没有这些系统的独立界面后端。

返回 `unsupported_rich_text` 时保留原文，直接人工交接；不要循环重试或把编辑框显示变化当成保存成功。

## 一次清楚交接

WorkBuddy 可直接说：“自动写入未成功。请打开「设置 → 个性化 → 给 WorkBuddy 的指令」，把下面这段追加到原有内容末尾并保存，然后告诉我‘好了’。”如果已有本 Skill 的 OBS 区块，则明确只替换该区块。不要让用户修改人设、长期记忆或原有其他指令。

正文使用已替换路径的 [入口模板](../assets/bridge.md)，直接放在回复的一个代码块里，不只给文件链接。`prepare` 返回的 `entry` 就是独立托管区；不要拿 `plan.after` 全文让用户追加，以免重复原有指令。没有 Python 就由 Agent 填好模板；WorkBuddy 用普通文本标题。不在交接正文里留下需用户填写的占位符、需用户运行的命令或需用户转义的路径。

用户回复“好了”后，只做一次可用的读回核对；没有读取能力就注明“用户已确认保存，Agent 未读回”。后续日常成果的实际保存单独核实，不把用户确认等同于实际生效。

官方依据：[Codex 审批](https://learn.chatgpt.com/docs/agent-approvals-security) · [Claude 权限](https://code.claude.com/docs/en/permissions) · [WorkBuddy 权限](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes) · [Apple 界面自动化](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/AutomatetheUserInterface.html)。
