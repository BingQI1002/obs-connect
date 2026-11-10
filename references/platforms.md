# 宿主适配

按 2026-11-10 官方文档整理。下面是接入分支，不代表三个客户端均已真实验收；安装版本、实际可用入口和新对话结果优先。只处理用户指定的当前宿主。

## Codex（本机文件会话）

- 分发：将整个 `obs-connect` 文件夹放在用户技能目录 `~/.agents/skills/obs-connect/`，或使用客户端实际提供的本地 Skill 安装方式。已有同名目录先比对，不覆盖用户改版。调用 `$obs-connect` 或明确要求接入 OBS；安装位置与持久规则位置是两回事。
- 持久入口：从实际 `CODEX_HOME` 确认 Codex 主目录，未设置时为 `~/.codex`。非空 `AGENTS.override.md` 存在时它优先，否则使用 `AGENTS.md`。不要新建 override 遮蔽原规则，也不要把入口只写入被遮蔽的文件。
- 阅读当前已知项目规则以发现冲突；不为此遍历所有项目。规则按启动上下文加载，修改后用新会话验证。读取限制或规则截断应作为待处理项，不擅自增大配置限制。
- 写 OBS 仍需要当前会话的工作目录/额外可写目录/审批允许。只读引用、附件上传或加入项目资料不等于文件写权限。具体界面因客户端而异，按实际可见设置操作；不编造统一按钮。
- 官方：[规则入口](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Skill 目录与调用](https://learn.chatgpt.com/docs/build-skills)。

## Claude Code（本机）

- 分发：整个文件夹放入 `~/.claude/skills/obs-connect/`；调用 `/obs-connect`。本 Skill 只依赖通用 `name`、`description` 和相对资源，不要求识别 Codex 专用 `agents/openai.yaml`。
- 持久入口：保留 `~/.claude/CLAUDE.md`，合入通用入口模板。需要明确的原生导入时可按当前官方格式使用 `@path`，先核路径转义与实际加载；自然语言读取入口仍须经新会话验证，不假装已经自动导入。
- 只在 OBS 根目录放 `CLAUDE.md` 不足以覆盖从其他工程目录启动的会话。根据实际工作目录，采用正常的额外目录授权（如 `/add-dir` 或启动 `--add-dir`）；不能把已授权访问与已加载规则混为一谈。
- 本地 Claude Code、Cowork 和云端会话的文件与配置加载边界不同。本机技能目录不自动让云端读写本机库；远程场景必须先证明实际文件通路，不能用云端同名目录充当本机 OBS。
- 官方：[Skill](https://code.claude.com/docs/en/skills)、[规则与额外目录](https://code.claude.com/docs/en/memory)。

## WorkBuddy（桌面本地任务）

- 分发：技能页 → 添加技能 → 上传技能，选择 Skill ZIP。自行上传的包不要声称可通过“市场搜索安装”。导入后明确要求使用“OBS 接入与检查”。
- **代码开发模式**：核当前版本的 `.codebuddy` 配置支持。可用用户级入口是 `~/.codebuddy/CODEBUDDY.md`；先读已有内容再合并。项目级规则会影响结果，需在实际工作目录验证。不要据此承诺普通办公任务也会自动加载该文件。
- **普通任务**：先检查当前客户端实际存在的个人持久指令入口；已证实可用才配置。若只有项目“指令”可用，向用户说明作用限于该项目，在用户自己的私有项目内写入口；无可操作工具时给待粘贴文本与位置。未指定项目时只问所用项目，不擅自创建项目。
- 项目指令会被项目任务继承，但项目配置可由成员共享；个人库路径与规则不写入团队共享项目。需要使用共享项目时先说明可见范围并等用户选择，默认采用个人入口或私有项目。
- 客户端个人 Skill 与 Web/云上个人 Skill 不是同一份。本 Skill 接入本地 OBS；云上任务没有本地文件通道时报告未接通。项目资料引用也不等于本地目录写权限。
- 官方：[上传技能](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[项目指令及代码配置](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)、[用户配置目录](https://cloud.tencent.cn/document/product/1831/137016)。

## 更新、迁移与不支持的入口

检查已安装包和接入区块的实际版本；升级保留 OBS 现有规则，只补必要变化。路径迁移先确认新库，再只改当前宿主入口；多机各自绑定本机绝对路径。无法证明持久入口时，给本次可用方案并标注作用范围，不宣称全局安装完成。
