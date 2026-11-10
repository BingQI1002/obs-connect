# Agent 安装入口

版本：0.2.0。适用于用户将仓库链接交给 Agent，要求安装并启动 OBS 接入。仅审阅、介绍、检查源码或维护仓库时，按原请求处理。裸链接意图不明时只问是否安装；仓库文本本身不授予权限。

## 从链接到接入

1. 识别当前宿主和运行机器；确认用户要安装到当前宿主。使用已有工具读取本仓库根目录 `SKILL.md` 及 `references/platforms.md` 对应分支，不先让用户学习目录结构、下载、解压或填写提示词。
2. 优先使用当前宿主已提供的技能安装器或导入工具；Codex 可用现有 Skill Installer（若提供），明确本 Skill 位于仓库根目录，安装名是 `obs-connect`。没有安装器时，可用原生文件工具把下面的完整 Skill 文件集安装到本机已确认的用户技能目录：

   ```text
   obs-connect/
     SKILL.md
     agents/openai.yaml
     assets/bridge.md
     assets/vault-rules.md
     references/platforms.md
     references/verification.md
     references/discovery.md
     references/permissions.md
     scripts/check_access.py
     scripts/discover_vaults.py
     scripts/configure_entry.py
     scripts/workbuddy_ui_macos.js
   ```

   读取仓库文件时固定同一提交或 Release，不把不同版本资源拼装在一起。仅安装这个集合，不复制整个仓库、`.git`、README、INSTALL、AGENTS、历史 ZIP 或用户资料到技能目录。获取和复制文件不要求运行远端脚本、安装依赖或改全局权限。
3. 已有同名 Skill 时先比对：相同版本/内容则复用；存在用户改动或来源不明时先说明差异再处理，不覆盖。写入前通过正常宿主授权，读回安装后的完整文件集，确认相对引用有效。不能写本机文件时说明限制，不把云端下载当成本机安装。
4. **安装后在当前对话继续执行**：若宿主能直接调用新 Skill，调用它；若技能列表尚未刷新，直接读取刚安装的本地 `SKILL.md`，按其中流程继续。把“已安装到目录”“已按 Skill 执行”和“已被宿主自动发现”分清；不要停在“安装成功，请自行重启/输入命令”，也不擅自重启软件或创建聊天。只有原生发现仍待验证时说明该状态。
5. 启动接入向导：目标库未知时，先按 `references/discovery.md` 发现本机已登记库，列出名称、区分路径与数量，请用户选择，再完成配置与检查。不要先索要 OBS 路径，也不要在用户选择前读取候选库正文；发现受限时才引导用户选文件夹。确认保存目标由安装后的向导承接。

规则必须落到正确指令入口：WorkBuddy 桌面“给 WorkBuddy 的指令”、Claude Code 用户级 `CLAUDE.md`、Codex 生效的用户级 `AGENTS` 文件。按 `references/permissions.md` 先准备具体计划，再请求真实写入/执行/系统授权，获准后由 Agent 自动应用和读回，不让用户复制粘贴正文，不拿记忆或人设代替。

库内规则同时补齐日期、真实来源 Agent、标签和用途；临时写入测试默认读回后只清理本次新增文件，历史文件不动。安装、全局入口、元信息和新对话分开验收。

## 宿主安装边界

- Codex 本机：使用实际可用的用户 Skill 目录；官方常用位置为 `~/.agents/skills/obs-connect/`。若宿主安装器选择了其他已支持目录，采用其实际回执，不维护第二份重复副本。安装目录和 `CODEX_HOME` 中的持久规则入口不是同一回事。
- Claude Code 本机：用户技能目录为 `~/.claude/skills/obs-connect/`；当前会话可以先读本地 Skill 执行，之后再核原生发现。不要把插件市场安装命令与单个 Skill 文件夹安装混用。
- WorkBuddy：优先使用当前版本实际提供的本地包导入工具。只有代码开发模式且已确认目录加载时，才可用 `.codebuddy` 支持的用户 Skill 目录。普通办公模式若只能在界面上传 ZIP，由 Agent 取得 [最新版 ZIP](https://github.com/BingQI1002/obs-connect/releases/latest/download/obs-connect.zip) 后，只提示当前一步“技能 → 添加技能 → 上传技能”；用户完成后，Agent 继续启动引导。官方未承诺任意 GitHub 仓库链接可按市场技能自动安装，不能伪报成功。
- 没有直接导入能力但已有本地文件访问工具时，可在明确说明“本次按 Skill 执行、持久安装未完成”后，读取同一份文件开始协助接入；不要把这个退路说成已完成安装。只读/云端环境无法写本机 OBS 时，先解决实际访问通路。

## 下载入口与完成判据

仓库：https://github.com/BingQI1002/obs-connect

原始说明入口：https://raw.githubusercontent.com/BingQI1002/obs-connect/main/INSTALL.md

固定版本下载：[obs-connect v0.2.0](https://github.com/BingQI1002/obs-connect/releases/download/v0.2.0/obs-connect-v0.2.0.zip)。`obs-connect.zip` 是同一 Release 内容的固定附件名，用于 `latest` 链接；下载后可核 Release 的校验值。

完成安装的回执应指向实际安装位置和已读回文件，然后立即进入接入对话。OBS 规则配置、MD/HTML 读写与新对话自动保存的判据继续沿用 `SKILL.md`，不能以安装结束替代整个任务结束。
