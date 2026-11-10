# OBS 接入与检查 · 0.1.1

下载 [Skill ZIP](dist/obs-connect-v0.1.1.zip)，安装后直接启动 Skill 即可。Agent 会主动询问必要信息，带着完成接入，让文档、HTML 等交付文件默认存到使用者自己的 Obsidian 库。此说明只用于需要时查安装方式，不用先读完才开始。

## 怎么开始

安装后直接选择或调用“OBS 接入与检查”，不用附加提示词。也可以说：

> 帮我接入 OBS。

Agent 会询问要接入哪个库；不知道路径时，它会帮助你找。然后由它创建或合并 `CLAUDE.md`、设置入口并检查读写。需要本人授权或点击界面时，它一次提示当前这一步，完成后继续，不让你照整份教程操作。已有规则会保留；真正冲突的条款由本人决定。每个软件各接入一次，共用库内一份保存约定，日常不用重复启动接入 Skill。

## 三种软件怎样安装

| 软件 | 安装方式 | 安装后调用 |
|---|---|---|
| Codex 本机版 | 解压后，将整个 `obs-connect` 文件夹放入 `~/.agents/skills/`，或使用当前客户端实际支持的本地安装入口；也可把解压目录交给 Codex，让它安装到个人 Skill 目录，保留已有同名版本。 | `$obs-connect` |
| Claude Code 本机版 | 解压后，将整个文件夹放入 `~/.claude/skills/`；也可让 Claude Code 从解压目录安装，保留已有同名版本。 | `/obs-connect` |
| WorkBuddy 桌面版 | 在技能页选择“添加技能 → 上传技能”，上传原 ZIP；私人上传包使用此入口，不能按市场技能搜索安装。 | 选择该 Skill，或说“请使用 OBS 接入与检查” |

`~` 指自己的用户主目录，Windows 通常是 `C:\Users\自己的用户名`。不同机器使用各自真实的库路径。不要把整个 ZIP 文件作为一个文件塞进技能目录；目录结构应是 `<技能目录>/obs-connect/SKILL.md`。

本包只有接入说明、规则模板和一个可选本地检查脚本；没有联网服务或第三方依赖。不需要 API Key，不要求安装 Obsidian 插件。Python 仅用于可选检查，无 Python 时 Agent 可用文件工具完成。

## 接入后会发生什么

- 库根目录的 `CLAUDE.md` 保存具体成果约定；每个 Agent 自己的持久入口指向它。
- 优先沿用原成果目录；没有约定才用 `AI成果/`。普通聊天不自动存档，不重建整库，不把工程依赖和日志塞入库。
- 接入时生成两份独立的 Markdown、HTML 测试文件并读回。它们标明接入测试，可自行保留或删除。
- Agent 会告诉你改了哪些文件、库外恢复副本的位置、已验证什么及尚缺什么。文件访问权限由各软件授权机制决定，Skill 本身不会扩大权限。

WorkBuddy 普通办公任务若只能使用项目“指令”，规则仅在该私有项目生效；不能据此称全局生效。不要把私人库路径和规则粘进团队共享项目。云端/远程任务如果没有本机文件通道，不能靠这个包直接写本机 OBS。

## Agent 会引导最后的新对话检查

接入和读写检查完成后，Agent 会请你新开普通对话，给出下面这句话直接发送；如果使用 WorkBuddy 项目入口，它会说明要在同一私有项目中新开任务。这一步不再调用本 Skill：

> 请制作一份三条建议的番茄钟使用说明，分别交付 Markdown 文档和一个不依赖外网的 HTML 页面。

看它是否自行把两份真实文件保存到约定目录并返回路径。当前能写文件和新对话会自动保存，是两个不同检查。首次通过也不代表所有软件、项目和未来版本都已稳定。

后续可直接说“只读检查我的 OBS 接入”“修复我的 OBS 接入”或“我把库搬到了……，请迁移接入”。已有规则没冲突时可重复运行，不应重复堆入口。HTML 已保存不等于能在 Obsidian 内直接运行；本包不安装 HTML 预览插件。

## 当前验证范围

此版按三家官方入口制作适配，做包结构检查、可选脚本执行和隔离文件场景验证；没有在收件人的真实软件、系统或库里运行，也尚未完成三个真实客户端的新对话验收。以对方实际接入回执为准。

官方依据：[Codex 技能](https://learn.chatgpt.com/docs/build-skills)、[Codex 持久规则](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Claude Code 技能](https://code.claude.com/docs/en/skills)、[Claude Code 规则](https://code.claude.com/docs/en/memory)、[WorkBuddy 技能上传](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[WorkBuddy 项目指令](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)。文档核对日期：2026-11-10。
