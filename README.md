# OBS 接入与检查

让 Codex、Claude Code、WorkBuddy 把生成的文档、HTML 等成果保存到你自己的 Obsidian 库。

**把链接发给 Agent，由它安装并开始接入；你只需回答必要问题。** 不用提前创建规则文件，也不用自己研究配置目录。

## 怎么开始

把这个链接发给你正在使用的 Agent：

```text
https://github.com/BingQI1002/obs-connect
```

如果 Agent 只介绍了仓库，补一句 **“安装并启动”**。也可以第一次就发送这一行：

```text
安装并启动这个 Skill：https://github.com/BingQI1002/obs-connect
```

Agent 的[安装入口在这里](INSTALL.md)：它应先识别当前软件、安装完整 Skill，然后在**同一个对话**中开始询问，不停在“安装成功，请自己输入命令”。裸链接是否被识别为安装请求，由各 Agent 决定；它不是各软件统一的自动安装按钮。

## 接下来怎么用

Agent 会先查找电脑上 **Obsidian 已登记的库**，再让你做选择题。例如：

> 找到 2 个已登记且可访问的库，你希望成果保存到哪个？
>
> 1. 工作笔记 — …/工作笔记
> 2. 个人资料 — …/个人资料
>
> 回复编号即可，也可以选其他文件夹。

你只需选择，不必先找文件夹路径。它只读取库登记信息和根目录可访问状态，选定前不会读取候选库的规则或笔记。只有一个库也会请你确认；找不到登记信息时，再带你选择文件夹，不会直接判断你没有库。

规则创建、已有规则合并和文件读写检查，都由 Agent 完成。需要你授权目录或点击界面时，它一次只提示当前这一步，完成后继续。

接入完成后，日常照常提需求，例如：

> 帮我整理一份活动方案，再做一个 HTML 展示页。

Agent 应按库内约定保存实际文件并返回路径，**不用每次再调用接入 Skill，也不用重复提醒存到 OBS**。每个软件各接入一次，共用库内一份规则。

## 它会保存到哪里

- 优先沿用你已有的成果目录；没有约定时使用库内的 `AI成果/`。
- 文本成果优先保存 Markdown；需要 Word、PDF、HTML 时保存对应实际文件，HTML 所需资源一起保留。
- 保留已有 `CLAUDE.md` 和目录结构；冲突条款先与你核明，不重建整库。
- 默认保存独立交付成果；普通闲聊不自动建档，工程依赖、构建缓存和完整日志留在工作目录。

## 哪些软件能用

| 软件 | 从链接开始后的处理 |
|---|---|
| Codex 本机版 | Agent 使用可用安装器或文件工具安装，读回 Skill 后立即开始接入。 |
| Claude Code 本机版 | Agent 安装到用户 Skill 目录，再在当前对话执行；原生技能列表是否刷新另行核实。 |
| WorkBuddy 桌面版 | 优先使用实际可用的导入工具；若当前版本只支持界面上传，Agent 先准备 ZIP，再带你完成上传，之后继续接入。 |

需要 Agent 能联网读仓库，并有本机文件操作能力。Skill 不能自行扩大软件权限；没有本机文件通道的云端任务不能直接写你的本地库。WorkBuddy 普通任务若采用项目指令，保存约定只在该私有项目生效。

WorkBuddy 的自定义包导入方式见[官方说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)。本仓库不把“市场搜索安装”当成任意 GitHub 链接安装能力。

## 怎么确认接好了

Agent 会生成 Markdown 和 HTML 测试文件，读回核对，并给你真实路径。然后引导你在新对话中做一次不提醒保存的测试，确认规则会继续生效。**当前能写文件和新对话会自动保存，会分别说明结果。**

HTML 保存成功不等于能在 Obsidian 内直接运行；本 Skill 不安装预览插件。新版本或新电脑上的实际结果，以接入检查为准。

## 备用下载与安装

优先把上面的链接交给 Agent。只有它无法代办安装时，才需要下面的备用方式：

- [下载最新版 Skill ZIP](https://github.com/BingQI1002/obs-connect/releases/latest/download/obs-connect.zip) · [查看版本与校验值](https://github.com/BingQI1002/obs-connect/releases/latest)
- Codex：解压后整个 `obs-connect` 文件夹放到实际支持的用户 Skill 目录，常用为 `~/.agents/skills/`；之后调用 `$obs-connect`。
- Claude Code：文件夹放入 `~/.claude/skills/`；之后调用 `/obs-connect`。
- WorkBuddy：技能 → 添加技能 → 上传技能，选择 ZIP；完成后告诉 Agent“已上传，请继续”。

没有 API Key、联网服务或第三方依赖。Python 只用于可选本地检查，没有 Python 时使用原生文件工具。

当前版本 **0.1.3**。已有包/脚本检查及隔离文件场景验证；发现仅覆盖已检查的登记源，不保证磁盘上的全部库。链接安装和新对话保存尚未完成三个真实客户端的整体验收。[Agent 安装说明](INSTALL.md) · [Skill 正文](SKILL.md) · [宿主规则依据](references/platforms.md)。
