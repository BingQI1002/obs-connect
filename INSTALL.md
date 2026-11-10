# Agent 安装入口

版本：0.4.0。用户要求安装并启动时，安装后立即在当前对话执行 [Skill 最短流程](SKILL.md)。明确要求升级时沿用原库及入口，不重新选库；仅介绍或审阅仓库时不安装。裸链接意图不明时先核用途。

## 安装

使用宿主已有安装器或原生导入工具；已有被宿主识别的安装直接复用。取同一正式 Release/提交的完整文件集，不把整个仓库复制进技能目录：

```text
obs-connect/
  SKILL.md
  agents/openai.yaml
  assets/bridge.md
  assets/vault-rules.md
  references/platforms.md
  references/discovery.md
  references/permissions.md
  references/verification.md
  references/updates.md
  scripts/configure_entry.py
  scripts/workbuddy_ui_macos.js
  scripts/discover_vaults.py
  scripts/check_access.py
  scripts/check_updates.py
```

- Codex：优先当前安装器，常用 `~/.agents/skills/obs-connect/`；现有受支持目录不迁来迁去。
- Claude Code：实际用户配置目录（默认 `~/.claude`）下 `skills/obs-connect/`。
- WorkBuddy：优先原生导入；已有识别目录就复用。只能界面上传时由 Agent 取得 ZIP，再引导“技能 → 添加技能 → 上传技能”，用户完成后继续。不要把复制到猜测目录说成已被软件识别。

同名 Skill 有用户修改时保留并合并，只有真正冲突才请用户取舍。正常授权后安装并读回完整文件集。技能列表尚未刷新时直接读本地 `SKILL.md` 继续，不要求用户重新调用，不擅自重启或新建聊天。

## 接入与升级

安装后只做“确认目标库 → 必要时授权 → 自动写入并读回”。正确入口见 [宿主适配](references/platforms.md)；缺权限才读 [授权方法](references/permissions.md)。默认不运行写入测试、不要求新对话验收、不排查更新网络。备份与比对在内部完成，回复连接到的库及入口结果即可。

更新脚本使用正式安装位置，不能指向下载暂存目录；更新失败不影响保存接入。升级按 [更新方法](references/updates.md) 沿用原库、保留自定义规则，只补必要入口差异。

[固定版 ZIP](https://github.com/BingQI1002/obs-connect/releases/download/v0.4.0/obs-connect-v0.4.0.zip) · [最新版 ZIP](https://github.com/BingQI1002/obs-connect/releases/latest/download/obs-connect.zip)。两个附件内容相同，校验值随 Release 提供。
