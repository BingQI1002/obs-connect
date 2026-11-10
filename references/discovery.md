# 首次选库

仅目标未知时使用；已有绑定或用户已指定就沿用。

运行 `python3 scripts/discover_vaults.py`，或用现有文件工具读取下列 Obsidian 登记文件中的 `vaults` 路径：

| 系统 | 常用位置 |
|---|---|
| macOS | `~/Library/Application Support/obsidian/obsidian.json` |
| Windows | `%APPDATA%/obsidian/obsidian.json` |
| Linux | `$XDG_CONFIG_HOME/obsidian/obsidian.json`，未设置则 `~/.config/obsidian/obsidian.json` |

只检查登记名称、路径及根目录可访问性，不读取候选库正文；按真实路径去重，不扫描磁盘，不修改登记表。结果仅代表已核登记源，不保证发现所有库。

列出数量、名称与区分路径让用户选择，只有一个也确认，例如“找到 2 个已登记库：1. 工作笔记（路径）；2. 个人资料（路径）。保存到哪个？”也允许选择其他文件夹。

查不到登记信息时带用户选择文件夹，不说用户没有库。用户选定前不读规则或笔记、不创建文件；确定目标后才继续接入。

登记结构为兼容性读取，可能随版本变化。[Obsidian 全局目录说明](https://obsidian.md/help/data-storage)。
