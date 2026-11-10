<!-- obs-connect:begin -->
OBS 成果保存入口

每个新任务先读取并遵循规则文件：{{RULES_ABSOLUTE_PATH}}
Obsidian 库：{{VAULT_ABSOLUTE_PATH}}
按该文件约定保存文档、HTML 等成果并读回，注明日期、真实 Agent、标签和用途；用户当次要求优先，按需读库。

更新检查脚本：{{UPDATE_CHECK_SCRIPT}}
当前任务先完成；工具可用且无需新增授权时运行 check（每 24 小时至多联网一次），仅 update_available 时提示版本与版本页，展示后用 acknowledge 记录该版本。失败跳过；用户同意升级后读本地 Skill 的 references/updates.md，明确停查时遵循用户要求。

接入版本：obs-connect 0.4.1。此入口不授予额外权限，不覆盖更高优先级指令。
<!-- obs-connect:end -->
