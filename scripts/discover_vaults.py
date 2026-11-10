#!/usr/bin/env python3
"""List registered Obsidian vault metadata; never read vault files or write."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys


def registry_paths(platform=None, home=None, env=None):
    platform = sys.platform if platform is None else platform
    home = Path.home() if home is None else Path(home)
    env = os.environ if env is None else env
    if platform == "darwin":
        return [home / "Library/Application Support/obsidian/obsidian.json"]
    if platform == "win32":
        base = Path(env["APPDATA"]) if env.get("APPDATA") else home / "AppData/Roaming"
        return [base / "obsidian/obsidian.json"]
    if platform.startswith("linux"):
        base = Path(env["XDG_CONFIG_HOME"]) if env.get("XDG_CONFIG_HOME") else home / ".config"
        return [base / "obsidian/obsidian.json"]
    return []


def directory_status(path):
    try:
        return "available" if stat.S_ISDIR(path.stat().st_mode) else "not_directory"
    except PermissionError:
        return "permission_denied"
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unavailable"


def discover(registries):
    vaults, sources, skipped = {}, [], 0
    for supplied in registries:
        source = Path(supplied).expanduser()
        record = {"path": str(source)}
        sources.append(record)
        try:
            # Only this registration file is opened; do not dump its other fields.
            with source.open("rb") as stream:
                raw = stream.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError("registry_too_large")
            data = json.loads(raw.decode("utf-8-sig"))
            registered = data.get("vaults") if isinstance(data, dict) else None
            if not isinstance(registered, dict):
                raise ValueError("unsupported_registry_format")
        except FileNotFoundError:
            record["status"] = "not_found"
            continue
        except PermissionError:
            record["status"] = "permission_denied"
            continue
        except (OSError, ValueError) as error:
            record["status"] = "unreadable_or_unsupported"
            record["error_type"] = type(error).__name__
            continue
        record["status"] = "read"
        for entry in registered.values():
            raw_path = entry.get("path") if isinstance(entry, dict) else None
            if not isinstance(raw_path, str) or not raw_path or "\x00" in raw_path:
                skipped += 1
                continue
            path = Path(raw_path)
            if not path.is_absolute():
                skipped += 1
                continue
            try:
                # Normalize aliases by directory metadata only, without listing files.
                normalized = path.resolve()
            except (OSError, RuntimeError):
                normalized = path
            key = os.path.normcase(str(normalized))
            if key in vaults:
                if str(source) not in vaults[key]["sources"]:
                    vaults[key]["sources"].append(str(source))
                continue
            vaults[key] = {"name": normalized.name or normalized.anchor,
                           "path": str(normalized), "status": directory_status(normalized),
                           "sources": [str(source)]}
    candidates = sorted(vaults.values(), key=lambda item: (item["name"].casefold(), item["path"]))
    for index, item in enumerate(candidates, 1):
        item["number"] = index
    return {"mode": "read-only-registry-metadata", "sources": sources,
            "registered_count": len(candidates),
            "available_count": sum(item["status"] == "available" for item in candidates),
            "skipped_entries": skipped, "vaults": candidates,
            "coverage": "Only registered entries in checked configuration files; not all vaults on disk.",
            "selection": "Await user choice; no vault selected or configured."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", action="append", help="Explicit registration file; repeatable. Overrides default lookup.")
    args = parser.parse_args()
    result = discover(args.registry if args.registry is not None else registry_paths())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
