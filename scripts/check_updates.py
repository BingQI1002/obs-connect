#!/usr/bin/env python3
"""Check public releases without touching OBS or installing anything.

JSON on stdout, exit 0 for all expected unavailable/offline conditions. The caller
must display an update before acknowledging it. The display/ack pair is best
effort: independent Agents can both display before either acknowledges.
"""

import argparse
import contextlib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time
import urllib.request

API_URL = "https://api.github.com/repos/BingQI1002/obs-connect/releases/latest"
RELEASE_BASE = "https://github.com/BingQI1002/obs-connect/releases/tag/"
INTERVAL = 24 * 60 * 60
TIMEOUT = 4
MAX_RESPONSE = 128 * 1024
VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")


class Unavailable(Exception):
    pass


def version_tuple(value):
    if not isinstance(value, str) or not VERSION_RE.fullmatch(value):
        raise Unavailable("invalid_version")
    return tuple(int(part) for part in value.split("."))


def local_version(skill_root):
    body = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^版本[：:]\s*([0-9]+\.[0-9]+\.[0-9]+)(?=[。\s]|$)", body, re.M)
    if not match:
        raise Unavailable("local_version_unreadable")
    version_tuple(match[1])
    return match[1]


def installation_id(skill_root):
    return hashlib.sha256(os.fsencode(str(skill_root.resolve()))).hexdigest()[:20]


def default_state_file(skill_root):
    if sys.platform == "darwin":
        cache = Path.home() / "Library" / "Caches"
    elif os.name == "nt":
        cache = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    else:
        cache = Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache"))
    return cache / "obs-connect" / installation_id(skill_root) / "updates.json"


def checked_state_path(path, skill_root):
    path = Path(path).expanduser()
    if not path.is_absolute():
        raise Unavailable("state_path_must_be_absolute")
    if path.is_symlink():
        raise Unavailable("state_symlink_rejected")
    path = path.resolve()
    root = skill_root.resolve()
    if path == root or root in path.parents:
        raise Unavailable("state_inside_skill_rejected")
    # A custom path must be outside OBS. Reject identifiable vaults; unmarked
    # vaults cannot be discovered without scanning, so the caller chooses those.
    if any((parent / ".obsidian").is_dir() for parent in path.parents):
        raise Unavailable("state_inside_vault_rejected")
    return path


def private_mkdir(path):
    missing = []
    candidate = path
    while not candidate.exists():
        missing.append(candidate)
        candidate = candidate.parent
    for candidate in reversed(missing):
        try:
            candidate.mkdir(mode=0o700)
        except FileExistsError:
            pass
    if os.name != "nt":
        for candidate in missing:
            candidate.chmod(0o700)


@contextlib.contextmanager
def state_lock(state_file):
    private_mkdir(state_file.parent)
    if Path(str(state_file) + ".lock").is_symlink():
        raise Unavailable("state_symlink_rejected")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(state_file) + ".lock", flags, 0o600)
    locked = False
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise Unavailable("invalid_lock_file")
        if os.name == "nt":
            import msvcrt
            if os.fstat(fd).st_size == 0:
                os.write(fd, b"0")
            os.lseek(fd, 0, os.SEEK_SET)
            try:
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            except OSError:
                raise Unavailable("state_busy")
        else:
            import fcntl
            os.fchmod(fd, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Unavailable("state_busy")
        locked = True
        yield
    finally:
        if locked:
            if os.name == "nt":
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def validate_release(payload):
    if not isinstance(payload, dict) or payload.get("draft") is not False or payload.get("prerelease") is not False:
        raise Unavailable("invalid_release")
    tag = payload.get("tag_name")
    if not isinstance(tag, str):
        raise Unavailable("invalid_release")
    version = tag[1:] if tag.startswith("v") else tag
    version_tuple(version)
    url = RELEASE_BASE + tag
    if payload.get("html_url") != url:
        raise Unavailable("invalid_release_url")
    return {"version": version, "release_url": url}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_latest():
    request = urllib.request.Request(API_URL, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "obs-connect-update-checker",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(request, timeout=TIMEOUT) as response:
        data = response.read(MAX_RESPONSE + 1)
    if len(data) > MAX_RESPONSE:
        raise Unavailable("response_too_large")
    return json.loads(data)


def read_state(path, identity):
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    except FileNotFoundError:
        return {"schema": 1, "installation_id": identity}
    with os.fdopen(fd, "r", encoding="utf-8") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > 16384:
            raise Unavailable("invalid_state")
        if os.name != "nt" and info.st_mode & 0o077:
            raise Unavailable("state_not_private")
        data = json.load(handle)
    if not isinstance(data, dict) or type(data.get("schema")) is not int or data.get("schema") != 1:
        raise Unavailable("invalid_state")
    if data.get("installation_id") != identity:
        raise Unavailable("state_installation_mismatch")
    if "last_attempt_at" in data:
        timestamp = data["last_attempt_at"]
        if (isinstance(timestamp, bool) or not isinstance(timestamp, (int, float))
                or not 0 <= timestamp < 1e12 or not math.isfinite(timestamp)):
            raise Unavailable("invalid_state")
        if data.get("last_result") not in ("success", "failure"):
            raise Unavailable("invalid_state")
        if data["last_result"] == "success":
            release = data.get("release")
            if not isinstance(release, dict):
                raise Unavailable("invalid_state")
            version_tuple(release.get("version"))
            version = release["version"]
            if release.get("release_url") not in (RELEASE_BASE + version, RELEASE_BASE + "v" + version):
                raise Unavailable("invalid_state")
    elif any(key in data for key in ("last_result", "release", "acknowledged_version")):
        raise Unavailable("invalid_state")
    if "acknowledged_version" in data:
        version_tuple(data["acknowledged_version"])
    return data


def write_state(path, data):
    fd, temporary = tempfile.mkstemp(prefix=".updates-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            if os.name != "nt":
                os.fchmod(handle.fileno(), 0o600)
            json.dump(data, handle, ensure_ascii=True, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def result_from_state(state, current, source):
    if state.get("last_result") != "success":
        return {"status": "unavailable", "reason": "previous_check_failed", "source": source, "current_version": current}
    release = state["release"]
    latest = release["version"]
    comparison = (version_tuple(latest) > version_tuple(current)) - (version_tuple(latest) < version_tuple(current))
    if comparison > 0:
        acknowledged = state.get("acknowledged_version")
        status = "already_notified" if acknowledged and version_tuple(acknowledged) >= version_tuple(latest) else "update_available"
    else:
        status = "up_to_date" if comparison == 0 else "local_ahead"
    return {"status": status, "current_version": current, "latest_version": latest,
            "release_url": release["release_url"], "source": source}


def run(command="check", *, skill_root=None, state_file=None, force=False, version=None, now=None, fetch=None):
    """Dependency injection is for isolated tests; CLI has no remote URL switch."""
    try:
        skill_root = Path(skill_root) if skill_root else Path(__file__).resolve().parent.parent
        current = local_version(skill_root)
        path = checked_state_path(state_file or default_state_file(skill_root), skill_root)
        identity = installation_id(skill_root)
        with state_lock(path):
            state = read_state(path, identity)
            if command == "acknowledge":
                version_tuple(version)
                release = state.get("release")
                if (state.get("last_result") != "success" or not release or release["version"] != version
                        or version_tuple(version) <= version_tuple(current)):
                    return {"status": "acknowledgement_rejected", "reason": "version_not_checked_newer"}
                state["acknowledged_version"] = version
                write_state(path, state)
                return {"status": "acknowledged", "version": version}
            timestamp = time.time() if now is None else now
            if not force and "last_attempt_at" in state and timestamp - state["last_attempt_at"] < INTERVAL:
                return result_from_state(state, current, "cache")
            # Persist attempt before requesting: a killed/failed request also
            # respects the throttle. Never preserve stale success as latest.
            state["last_attempt_at"] = timestamp
            state["last_result"] = "failure"
            state.pop("release", None)
            write_state(path, state)
            try:
                release = validate_release((fetch or fetch_latest)())
            except Exception:
                return {"status": "unavailable", "reason": "release_check_failed", "current_version": current, "source": "network"}
            state["release"] = release
            state["last_result"] = "success"
            write_state(path, state)
            return result_from_state(state, current, "network")
    except Unavailable as exc:
        return {"status": "unavailable", "reason": str(exc)}
    except (OSError, ValueError, UnicodeError):
        return {"status": "unavailable", "reason": "local_state_or_version_unavailable"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("--force", action="store_true", help="Bypass the 24h request throttle; does not reset acknowledgement")
    check.add_argument("--state-file", type=Path, help="Absolute path outside OBS and the installed Skill")
    ack = commands.add_parser("acknowledge")
    ack.add_argument("--version", required=True)
    ack.add_argument("--state-file", type=Path, help="The same external state file used for check")
    args = parser.parse_args(argv)
    result = run(args.command, state_file=args.state_file, force=getattr(args, "force", False), version=getattr(args, "version", None))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
