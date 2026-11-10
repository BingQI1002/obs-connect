#!/usr/bin/env python3
"""Optional OBS read/write probe; no dependencies, config edits or vault scan."""
import argparse
import hashlib
import html
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def inside(path, root):
    return path == root or root in path.parents


def check(vault_arg, write_test=False, output_dir="AI成果/接入检查"):
    vault = Path(os.path.expandvars(vault_arg)).expanduser().resolve(strict=True)
    if not vault.is_dir():
        raise ValueError("库路径不是目录")
    rule = vault / "CLAUDE.md"
    if rule.exists() and not inside(rule.resolve(), vault):
        raise ValueError("CLAUDE.md 指向库外，请先核明规则目标")
    result = {"vault": str(vault), "obsidian_directory": (vault / ".obsidian").is_dir(),
              "rule_exists": rule.is_file(), "mode": "write-test" if write_test else "read-only",
              "host_loading": "未验", "new_conversation": "未验", "files": []}
    if rule.is_file():
        raw = rule.read_bytes()
        raw.decode("utf-8-sig")
        result["rule_sha256"] = hashlib.sha256(raw).hexdigest()
    if not write_test:
        result["write_status"] = "未验（只读检查）"
        return result
    if not rule.is_file():
        raise ValueError("先建立或确认库根目录 CLAUDE.md，再执行写入测试")
    relative = Path(output_dir)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError("output-dir 必须是库内相对子目录，不能包含 ..")
    target = (vault / relative).resolve()
    if not inside(target, vault) or target == vault:
        raise ValueError("测试目录必须在库内，不能通过符号链接逃逸")
    target.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    stamp = datetime.now(timezone.utc).isoformat()
    basename = "obs-connect-test-" + token
    payloads = {
        ".md": "# OBS 接入测试\n\n时间（UTC）：" + stamp + "\n\n校验串：`" + token + "`\n",
        ".html": '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
                 '<meta name="viewport" content="width=device-width, initial-scale=1">'
                 '<title>OBS 接入测试</title></head><body><h1>OBS 接入测试</h1><p>时间（UTC）：'
                 + html.escape(stamp) + '</p><p>校验串：<code>' + token + '</code></p></body></html>\n'
    }
    for suffix, content in payloads.items():
        path = target / (basename + suffix)
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        readback = path.read_text(encoding="utf-8")
        if readback != content:
            raise OSError("读回不一致：" + str(path))
        result["files"].append({"path": str(path), "readback": "通过",
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    result["write_status"] = "MD 与 HTML 写入并读回通过；页面显示未验"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True, help="用户指定的 Obsidian 库目录")
    parser.add_argument("--write-test", action="store_true", help="明确创建两个独立测试文件")
    parser.add_argument("--output-dir", default="AI成果/接入检查", help="库内相对测试目录")
    args = parser.parse_args()
    try:
        result = check(args.vault, args.write_test, args.output_dir)
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error),
                          "note": "若写入中途失败，已创建的测试文件可能保留；勿删除其他文件"}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
