# OBS 接入与检查

让 Codex、Claude Code、WorkBuddy 把文档、HTML 等成果保存到你自己的 Obsidian 库。

## 发给 Agent 就能开始

```text
安装并启动这个 Skill：https://github.com/BingQI1002/obs-connect
```

Agent 按 [安装入口](INSTALL.md) 安装后，在同一对话继续接入。仅发送裸链接时，部分 Agent 会先询问用途。

## 只需三步

1. **选库**：已有绑定就沿用；首次使用时，Agent 查找已登记的 Obsidian 库，列出名称和路径供你选择。
2. **必要时授权**：Agent 自动准备并写入当前软件的全局指令入口，缺权限时只提示当前必要授权；批准后继续，不用粘贴规则。
3. **保存读回**：Agent 确认入口已保存，并告诉你连接到哪个库。之后照常提需求，无需每次调用 Skill 或提醒存到 OBS。

默认不生成接入测试文件、不要求另开对话验收。备份和比对由 Agent 内部完成；你要求实际测试时再进行。遇到系统拒绝就停在那一步，不反复尝试、展开长排查。

## 各软件写到哪里

| 软件 | 全局入口 |
|---|---|
| Codex 本机 | 实际 Codex 配置目录中生效的 `AGENTS.md` 或已有非空 `AGENTS.override.md` |
| Claude Code | 实际用户配置目录中的 `CLAUDE.md`，含 OBS 规则原生导入 |
| WorkBuddy 桌面 | 设置 → 个性化 → **给 WorkBuddy 的指令** |

WorkBuddy 不使用长期记忆或人设代替。桌面写入使用已有设置/电脑操作工具，macOS 附系统界面后端，首次可能需要你批准自动化/辅助功能。其他系统依赖宿主工具；无本机通道的云端任务不能直接写本地库。[宿主与授权细节](references/permissions.md)。

当前 macOS 后端遇到带 YAML 元信息的指令会保留原文并停下，需要能处理该编辑器的宿主设置工具；不会把这种情况报为已接通。

## 成果怎么保存

- 沿用库内既有规则和成果目录，没有约定时用 `AI成果/`；缺保存约定才补充，不重建整库。
- 新文件名包含日期、主题和真实 Agent，例如 `2026-11-10_活动方案_WorkBuddy.md`。
- MD 属性和 HTML 可见信息记录日期、来源 Agent、标签与用途；复用旧稿保留原创建信息，另记修改者。
- 普通闲聊不自动建档，工程依赖和日志留在工作目录。HTML 保存成功不代表 Obsidian 已能直接运行它。

## 更新

0.3.0 起支持使用时检查更新，0.4.0 起先完成当前任务，工具就绪且无需新增授权时再尝试；默认每 24 小时至多联网一次，同版本提醒后不反复提示，失败直接跳过。用户同意后由 Agent 升级，保留原库和自定义规则。无需再次调用 Skill，软件关闭时没有后台通知。

旧用户把链接交给 Agent，说“升级 OBS 接入，保留原库和自定义规则”即可。只升级包而未补全局入口，不算提醒已接通；也可说“停止检查更新”。[更新方法](references/updates.md)。

## 下载与边界

[下载最新版 ZIP](https://github.com/BingQI1002/obs-connect/releases/latest/download/obs-connect.zip) · [版本与实测范围](https://github.com/BingQI1002/obs-connect/releases/latest)

优先让 Agent 代办。宿主只有手动导入界面时，由 Agent 先取得 ZIP，再引导当前一步，完成后继续。WorkBuddy 的技能导入见 [官方说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)。

当前版本 **0.4.0**。需要宿主能读仓库并操作本机；不需要 API Key。Python 仅为可选助手，保存入口可用原生文件工具配置。各客户端的新对话是否实际遵循，要有对应实测证据，不能用文件读回代替。
