# 自动配置与授权续跑

目标是由 Agent 完成写入，用户只作必要的选择、批准和系统授权。不要把“请自行复制粘贴规则”作为正常结束方式。先区分**缺少写入权限**和**缺少操作能力**，批准权限本身不会凭空增加一个不存在的工具。

## 通用步骤

1. 先确定实际宿主、所选库和正确指令入口；规则正文在库内，入口在当前宿主。准备改动预览、库外恢复副本与目标当前版本摘要。
2. 用已有原生写入/设置工具执行。受限时调用宿主真正的操作审批或目录授权功能，展示具体目标和必要理由；不能只在聊天中问“允许吗”后继续用同一个受限工具空转。
3. 获准后自动继续原计划并保存、读回。目标发生并发变化就重读合并。用户拒绝或上级策略明确禁止时停止该写入，保留准备工作并说明实际阻塞，不改权限配置来绕过拒绝。
4. 回执写清“哪个 Agent、哪个指令文件/字段、已写入与读回、新对话是否已验证”，不以测试文件能写就当作全局入口完成。

## Codex：文件计划 + 原生审批

先检查 `CODEX_HOME`、已有 override 与等价入口。新建/修复文件入口时，可用下面的标准库助手，Python 不可用时使用宿主文件工具执行相同方案：

```text
python3 scripts/configure_entry.py prepare --host codex --vault <所选库> --work-dir <库外工作目录>
python3 scripts/configure_entry.py apply --plan <上一步返回的plan.json> --plan-sha256 <上一步返回的摘要>
```

`prepare` 只在工作目录生成具体计划、差异和摘要，不写全局规则；计划目录使用私有权限并放局部 Git 忽略规则，避免把个人指令误提交。`apply` 固定审批时的计划摘要，再合并托管区、留恢复副本、检查并发并读回。不能在批准后改计划换目标或正文，不申请永久的整机写入或泛化 Python 放行规则。已有等价入口就复用，不为执行脚本硬加重复内容。

若出现 `needs_permission` / `PermissionError`，由 Agent 发起当前宿主支持的**工作区外写入/命令审批**，批准后重跑同一条 `apply` 命令。例如本机执行工具若提供 `sandbox_permissions: require_escalated`，应在真实工具参数中申请，而不是让用户把这一段复制进终端。若支持按路径申请写权限，优先只授权目标规则文件所在目录与所选库。

当前会话禁用审批或受管理策略约束时，指出具体原因，带用户切换当前会话至允许申请审批的模式后继续；不自动修改 `config.toml`，不要求关闭沙箱或开启完全访问。明确的保护拒绝不能通过另起进程、模糊命令或其他文件名绕过。

官方依据：[Codex 审批与安全](https://learn.chatgpt.com/docs/agent-approvals-security)、[全局 AGENTS 入口](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。

## Claude Code：同样自动写入，必要时批准

将上面的 `--host` 换为 `claude-code`；先核实际用户配置目录，再准备/应用用户级 `CLAUDE.md`。助手会生成带空格转义的原生 `@` 导入行。使用正常 Edit/Write/Bash 权限确认；如需额外目录，用当前版本支持的目录授权方式，限定到实际所需目录。不要使用跳过权限参数，也不改自动记忆来替代规则。

官方依据：[Claude 权限与工作目录](https://code.claude.com/docs/en/permissions)、[用户规则与导入](https://code.claude.com/docs/en/memory)。

## WorkBuddy：自动操作正确的指令字段

官方公开的桌面入口是“设置 → 个性化”；本库已核对 v5.9.3 的“给 WorkBuddy 的指令”。官方权限文档支持文件/命令的受控审批，但未在已核文档中找到修改此字段的公开 CLI。CodeBuddy Code 的 `config set -g` 不能据此冒充 WorkBuddy 普通任务的桌面字段接口。

优先使用实际提供的设置工具或电脑操作工具，由 Agent 读取当前字段、准备合并、请求所需授权、填写并保存读回。没有对应工具时，先检查是否能经正常授权启用已支持的工具，不直接退回手动粘贴，也不写 `MEMORY.md`、`USER.md`、人设或猜测内部 JSON 键。

### macOS 的系统界面自动化后端

有本机命令能力时，可使用 `scripts/workbuddy_ui_macos.js`，通过 macOS 自带的 JXA / System Events 操作真实界面，不改 WorkBuddy 程序包或内部配置。**先向用户说明并取得当前软件控制界面的授权**；系统可能要求给执行脚本的宿主授予“自动化/辅助功能”，由用户在系统提示中批准，Agent 不自行勾选权限。系统授权针对执行宿主，可能比单个字段的范围更宽；脚本自身只定位 WorkBuddy 指令字段，不能宣称操作系统只授予了该字段权限。

```text
osascript -l JavaScript scripts/workbuddy_ui_macos.js inspect <库外工作目录/当前指令.txt>
python3 scripts/configure_entry.py prepare --host workbuddy --vault <所选库> --work-dir <库外工作目录> --before-ui-file <当前指令.txt>
osascript -l JavaScript scripts/workbuddy_ui_macos.js apply <plan.json> <prepare返回的摘要>
```

以上命令由 Agent 调用，用户不用复制。`inspect` 读取完整预览原文并保存唯一命名的私有副本；不能用编辑器渲染后的可见文本替代含注释的原文。`apply` 固定计划摘要、核当前值一致，再等待真正全选/清空、填写、保存并核目标字段。系统未授权时按原错误申请授权后重试；输出文件已存在应换新文件名，字段变化应重新准备计划，不能把所有失败都当成缺权限。用户同时操作界面或有未保存编辑时暂停自动化。

脚本只定位 WorkBuddy 指令字段，保存前核完整内容；不发消息、不创建聊天、不改人设或长期记忆。UI 入口使用普通文本标题，文件型入口仍保留 Markdown 格式。操作中会临时使用系统剪贴板并在成功/失败路径恢复；若用户同时复制新内容则保留用户的新剪贴板，不将其内容留档。复杂富文本、界面版本或语言存在差异时，严格核保存后的正文；返回未验证时不能声称成功，必要时改用宿主已有的原生电脑操作工具保留格式。

Windows/Linux 若宿主已有可用的电脑操作工具，仍由 Agent 自动填写保存并申请工具所需授权。本包没有已实测的这些系统的独立 UI 后端；若当前宿主确实没有任何可启用的设置/电脑操作能力，说明这个能力缺口并保留进度，不能宣称批准一次就一定能写入，也不把复制粘贴当成已完成。

官方依据：[WorkBuddy 系统设置](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Setting)、[WorkBuddy 权限与系统授权](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Permission-Modes)、[苹果官方界面脚本说明](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/AutomatetheUserInterface.html)。
