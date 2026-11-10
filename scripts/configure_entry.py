#!/usr/bin/env python3
"""Prepare and apply a reviewed host-entry edit. Never grants permissions itself."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import uuid

BEGIN = "<!-- obs-connect:begin -->"
END = "<!-- obs-connect:end -->"
SKILL = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_current(path):
    if path.is_symlink():
        raise ValueError("规则入口是符号链接；先核明真实目标，不自动替换链接")
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def merge_block(original, block):
    if original.count(BEGIN) != original.count(END) or original.count(BEGIN) > 1:
        raise ValueError("托管区边界缺失或重复；先核明，不能自动覆盖")
    if BEGIN in original:
        start, finish = original.index(BEGIN), original.index(END) + len(END)
        if finish < start:
            raise ValueError("托管区边界顺序错误")
        return original[:start] + block + original[finish:]
    return original + ("" if not original or original.endswith("\n\n") else "\n" if original.endswith("\n") else "\n\n") + block + "\n"


def render_bridge(vault, host):
    rules = vault / "CLAUDE.md"
    update_script = SKILL / "scripts/check_updates.py"
    if not update_script.is_file():
        raise ValueError("已安装 Skill 缺少更新脚本；先安装完整文件集")
    for value in [str(vault), str(rules), str(update_script)]:
        if any(char in value for char in ["\n", "\r", "\x00"]):
            raise ValueError("库路径含不支持的控制字符")
    block = (SKILL / "assets/bridge.md").read_text(encoding="utf-8").strip()
    block = block.replace("{{RULES_ABSOLUTE_PATH}}", str(rules)).replace("{{VAULT_ABSOLUTE_PATH}}", str(vault))
    block = block.replace("{{UPDATE_CHECK_SCRIPT}}", str(update_script))
    if host == "claude-code":
        native_import = "@" + rules.as_posix().replace(" ", "\\ ")
        block = block.replace("OBS 成果保存入口", "OBS 成果保存入口\n\n" + native_import, 1)
    return block


def private_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        os.chmod(path, 0o600)
        stream.write(data)


def prepare(host, vault_arg, work_dir, config_root=None, before_ui_file=None):
    vault = Path(vault_arg).expanduser().resolve(strict=True)
    if not vault.is_dir() or not (vault / "CLAUDE.md").is_file():
        raise ValueError("先确认所选库及库根 CLAUDE.md")
    work = Path(work_dir).expanduser().resolve()
    if work == vault or vault in work.parents:
        raise ValueError("改动预览、计划和恢复副本必须保存在库外工作目录")
    block = render_bridge(vault, host)
    if host == "workbuddy":
        if not before_ui_file:
            raise ValueError("WorkBuddy 请先通过设置工具或已授权界面自动化读取指令字段；不要猜内部配置文件")
        before = Path(before_ui_file).read_text(encoding="utf-8")
        target = "WorkBuddy/设置/个性化/给 WorkBuddy 的指令"
        kind = "ui-field"
        raw = before.encode("utf-8")
    else:
        default = os.environ.get("CODEX_HOME", str(Path.home() / ".codex")) if host == "codex" else os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude"))
        base = Path(config_root or default).expanduser().resolve()
        if host == "codex":
            override = base / "AGENTS.override.md"
            override_data = read_current(override)
            target_path = override if override_data and override_data.strip() else base / "AGENTS.md"
        else:
            target_path = base / "CLAUDE.md"
        target = str(target_path)
        raw = read_current(target_path)
        before = raw.decode("utf-8") if raw is not None else ""
        kind = "file"
    # Preserve text outside the managed block, including BOM and existing CRLFs.
    if "\r\n" in before:
        block = block.replace("\n", "\r\n")
    after = merge_block(before, block)
    job = work / ("obs-connect-" + uuid.uuid4().hex[:12])
    job.mkdir(mode=0o700, parents=True, exist_ok=False)
    private_write(job / ".gitignore", b"*\n")
    plan = {"schema": 1, "host": host, "kind": kind, "target": target,
            "vault": str(vault), "before_exists": raw is not None,
            "before_sha256": digest(raw) if raw is not None else None,
            "before": before, "after": after, "after_sha256": digest(after.encode("utf-8")),
            "status": "unchanged" if before == after else "prepared", "approval": "由宿主申请本次具体目标的写入/界面权限；本计划不授予权限"}
    plan_bytes = json.dumps(plan, ensure_ascii=False, indent=2).encode("utf-8")
    private_write(job / "plan.json", plan_bytes)
    preview = "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=target, tofile=target))
    private_write(job / "preview.diff", preview.encode("utf-8"))
    return {"status": plan["status"], "host": host, "kind": kind, "target": target,
            "plan": str(job / "plan.json"), "plan_sha256": digest(plan_bytes), "preview": str(job / "preview.diff"),
            "entry": block,
            "next": "申请该字段的自动化权限后自动应用" if kind == "ui-field" else "由 Agent 执行 apply；受限时申请宿主原生审批，再重跑同一计划"}


def apply_file(plan_path, plan_sha256):
    plan_path = Path(plan_path).resolve(strict=True)
    plan_bytes = plan_path.read_bytes()
    if digest(plan_bytes) != plan_sha256:
        raise ValueError("计划与审批预览时的摘要不一致；停止写入")
    plan = json.loads(plan_bytes.decode("utf-8"))
    if plan.get("schema") != 1 or plan.get("kind") != "file" or plan.get("host") not in ["codex", "claude-code"]:
        raise ValueError("本命令只应用 Codex/Claude Code 文件计划；WorkBuddy 使用正确字段的 UI/设置工具")
    target = Path(plan["target"])
    if not target.is_absolute() or target.name not in ["AGENTS.md", "AGENTS.override.md", "CLAUDE.md"]:
        raise ValueError("计划目标不是支持的绝对规则文件")
    content = plan["after"].encode("utf-8")
    if digest(content) != plan["after_sha256"]:
        raise ValueError("计划正文已变化，请重新准备预览")
    current = read_current(target)
    if current is not None and digest(current) == plan["after_sha256"]:
        return {"status": "already_applied", "target": str(target), "readback": True}
    if (current is not None) != plan["before_exists"] or (digest(current) if current is not None else None) != plan["before_sha256"]:
        raise ValueError("目标已被其他人修改；停止写入，重读并重新准备计划")
    backup = None
    if current is not None:
        backup = plan_path.parent / "before.bin"
        if backup.exists():
            if backup.read_bytes() != current:
                raise ValueError("恢复副本不匹配；停止写入")
        else:
            private_write(backup, current)
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(target.stat().st_mode) if current is not None else 0o644
    temporary = None
    try:
        descriptor, name = tempfile.mkstemp(prefix=".obs-connect-", dir=str(target.parent))
        temporary = Path(name)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        # Recheck after preparing the replacement, before making it visible.
        if read_current(target) != current:
            raise ValueError("写入前目标又发生变化；请重新准备计划")
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    if target.read_bytes() != content:
        raise OSError("规则读回不一致；保留恢复副本并停止后续步骤")
    result = {"status": "applied", "host": plan["host"], "target": str(target),
              "backup": str(backup) if backup else None, "readback": True, "new_conversation": "未验"}
    (plan_path.parent / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--host", choices=["codex", "claude-code", "workbuddy"], required=True)
    p.add_argument("--vault", required=True)
    p.add_argument("--work-dir", required=True)
    p.add_argument("--config-root")
    p.add_argument("--before-ui-file")
    a = commands.add_parser("apply")
    a.add_argument("--plan", required=True)
    a.add_argument("--plan-sha256", required=True)
    args = parser.parse_args()
    try:
        result = apply_file(args.plan, args.plan_sha256) if args.command == "apply" else prepare(args.host, args.vault, args.work_dir, args.config_root, args.before_ui_file)
    except PermissionError as error:
        print(json.dumps({"status": "needs_permission", "target": str(error.filename or ""),
                          "next": "申请本次原生权限并续做；仍无法自动写入时，给出准确目标和已填好的 entry 正文交接用户保存；不绕过管理策略"}, ensure_ascii=False))
        return 3
    except (OSError, ValueError, KeyError) as error:
        print(json.dumps({"status": "error", "message": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
