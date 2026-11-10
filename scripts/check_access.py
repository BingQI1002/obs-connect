#!/usr/bin/env python3
"""Optional OBS probe with agent/date/tags; removes only its own new test files."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import uuid


def inside(path, root):
    return path == root or root in path.parents


def offset_zone(value):
    if value in ["Z", "+00:00", "-00:00"]:
        return timezone.utc
    match = re.fullmatch(r"([+-])(\d{2}):(\d{2})", value)
    if not match or int(match[2]) > 23 or int(match[3]) > 59:
        raise ValueError("时区偏移应为 Z 或 +08:00 等格式")
    minutes = int(match[2]) * 60 + int(match[3])
    return timezone(timedelta(minutes=minutes if match[1] == "+" else -minutes))


def make_dirs(path, boundary):
    missing, created = [], []
    cursor = path
    while cursor != boundary and not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    for directory in reversed(missing):
        try:
            directory.mkdir()
            created.append(directory)
        except FileExistsError:
            if not directory.is_dir():
                raise
    return created


def check(vault_arg, write_test=False, output_dir=".obs-connect-check", source_agent=None,
          utc_offset="Z", keep_test_files=False):
    vault = Path(os.path.expandvars(vault_arg)).expanduser().resolve(strict=True)
    if not vault.is_dir():
        raise ValueError("库路径不是目录")
    rule = vault / "CLAUDE.md"
    if rule.exists() and not inside(rule.resolve(), vault):
        raise ValueError("CLAUDE.md 指向库外，请先核明目标")
    result = {"vault": str(vault), "rule_exists": rule.is_file(),
              "mode": "write-test" if write_test else "read-only", "files": [],
              "host_loading": "未验", "new_conversation": "未验"}
    if rule.is_file():
        raw = rule.read_bytes()
        raw.decode("utf-8-sig")
        result["rule_sha256"] = hashlib.sha256(raw).hexdigest()
    if not write_test:
        result["write_status"] = "未验（只读检查）"
        return result
    if source_agent not in ["Codex", "Claude Code", "WorkBuddy"]:
        raise ValueError("写入测试必须明确 --source-agent：Codex、Claude Code 或 WorkBuddy，不能猜来源")
    zone = offset_zone(utc_offset)
    if not rule.is_file():
        raise ValueError("先确认库根 CLAUDE.md，再执行写入测试")
    relative = Path(output_dir)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError("测试目录必须是库内相对子目录，不能包含 ..")
    base = (vault / relative).resolve()
    if not inside(base, vault) or base == vault:
        raise ValueError("测试目录不能是库根或通过链接指向库外")
    token = uuid.uuid4().hex
    stamp = datetime.now(zone).isoformat(timespec="seconds")
    agent_name = source_agent.replace(" ", "-")
    basename = stamp[:10] + "_" + agent_name + "_接入测试_" + token[:12]
    target = base / token
    created_dirs = make_dirs(target, vault)
    tags = ["AI接入测试", "Agent/" + agent_name]
    metadata = {"created_at": stamp, "source_agent": source_agent, "tags": tags, "purpose": "接入写入与读回测试"}
    frontmatter = "---\n" + "".join(key + ": " + json.dumps(value, ensure_ascii=False) + "\n" for key, value in metadata.items()) + "---\n\n"
    body = "# OBS 接入测试\n\n生成时间：" + stamp + "\n\n来源 Agent：" + source_agent + "\n\n用途：临时验证本库能写入并读回，属于测试文件。\n\n校验串：`" + token + "`\n"
    markup = ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width, initial-scale=1">'
              '<meta name="date" content="' + html.escape(stamp, quote=True) + '">'
              '<meta name="author" content="' + html.escape(source_agent, quote=True) + '">'
              '<meta name="keywords" content="' + html.escape(",".join(tags), quote=True) + '">'
              '<title>OBS 接入测试</title></head><body><h1>OBS 接入测试</h1>'
              '<p>生成时间：' + html.escape(stamp) + '</p><p>来源 Agent：' + html.escape(source_agent) +
              '</p><p>标签：' + html.escape("、".join(tags)) + '</p><p>用途：临时写入与读回测试</p>'
              '<p>校验串：<code>' + token + '</code></p></body></html>\n')
    for suffix, content in [(".md", frontmatter + body), (".html", markup)]:
        path = target / (basename + suffix)
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        if path.read_text(encoding="utf-8") != content:
            raise OSError("测试读回不一致：" + str(path))
        result["files"].append({"path": str(path), "readback": "通过", "retained": True,
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    if not keep_test_files:
        for item in result["files"]:
            path = Path(item["path"])
            if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]:
                path.unlink()
                item["retained"] = False
            else:
                item["cleanup"] = "文件已变化，保留待核；未删除"
        for directory in reversed(created_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass  # Never remove pre-existing directories or anyone else's files.
    result.update(metadata)
    result["write_status"] = "MD 与 HTML 写入并读回通过；页面显示未验"
    result["cleanup"] = "用户要求保留" if keep_test_files else "仅清理本次新增且内容未变的测试文件；历史检查文件未动"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--write-test", action="store_true")
    parser.add_argument("--source-agent", choices=["Codex", "Claude Code", "WorkBuddy"])
    parser.add_argument("--utc-offset", default="Z", help="按宿主提供的用户时区传入，例如 +08:00；未知时明确使用 UTC")
    parser.add_argument("--output-dir", default=".obs-connect-check")
    parser.add_argument("--keep-test-files", action="store_true", help="仅在用户要求留证时保留新增测试文件")
    args = parser.parse_args()
    try:
        result = check(args.vault, args.write_test, args.output_dir, args.source_agent, args.utc_offset, args.keep_test_files)
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error), "note": "中途失败可能留有本次测试文件；不清理历史文件"}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
