#!/usr/bin/env python3
"""Secret scan for google-ads-mcp before its first push to a code host.

Two modes:
  python scan_secrets.py --tree "C:/Users/Admin/Projects/google-ads-mcp"
      scans the working tree (skipping .git, .venv, __pycache__ and anything
      matched by gitignore.google-ads-mcp next to this script)
  git log --all -p | python scan_secrets.py --stdin
      scans full history so a key committed in June and deleted since is caught

Exit 0 = clean. Exit 1 = findings (printed, values redacted). Exit 2 = usage.
Stdlib only, runs on Windows system Python.
"""
from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path

PATTERNS = [
    ("anthropic api key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("google oauth client secret", re.compile(r"GOCSPX-[A-Za-z0-9_\-]{20,}")),
    ("google oauth refresh token", re.compile(r"\b1//0[A-Za-z0-9_\-]{30,}")),
    ("google access token", re.compile(r"\bya29\.[A-Za-z0-9_\-\.]{30,}")),
    ("google api key", re.compile(r"\bAIza[A-Za-z0-9_\-]{30,}")),
    ("google oauth client id", re.compile(r"\b\d{10,}-[a-z0-9]{20,}\.apps\.googleusercontent\.com")),
    ("developer token assignment", re.compile(r"(?i)developer[_\-]?token\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{18,}")),
    ("client secret assignment", re.compile(r"(?i)client[_\-]?secret\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{12,}")),
    ("refresh token assignment", re.compile(r"(?i)refresh[_\-]?token\s*[=:]\s*['\"]?[A-Za-z0-9_\-/]{20,}")),
    ("app password assignment", re.compile(r"(?i)(app[_\-]?password|smtp[_\-]?pass|email[_\-]?pass)\s*[=:]\s*['\"]?[A-Za-z0-9 ]{12,}")),
    ("telegram bot token", re.compile(r"\b\d{8,12}:[A-Za-z0-9_\-]{35}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

# Lines that look like assignments to a placeholder are fine.
PLACEHOLDER = re.compile(r"(?i)(your[_\-]|<[^>]+>|xxxx|example|placeholder|redacted|changeme)")

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache"}
TEXT_MAX_BYTES = 5_000_000


def load_ignore_globs():
    here = Path(__file__).resolve().parent / "gitignore.google-ads-mcp"
    if not here.exists():
        return []
    globs = []
    for line in here.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        globs.append(line.rstrip("/"))
    return globs


def ignored(rel, globs):
    parts = rel.split("/")
    for g in globs:
        if any(fnmatch.fnmatch(p, g) for p in parts) or fnmatch.fnmatch(rel, g):
            return True
    return False


def redact(s):
    return s[:6] + "..." + s[-3:] if len(s) > 12 else "***"


def scan_text(text, where, findings):
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, rx in PATTERNS:
            m = rx.search(line)
            if m and not PLACEHOLDER.search(m.group(0)):
                findings.append((where, lineno, name, redact(m.group(0))))
                break


def scan_tree(root, globs):
    findings = []
    root = Path(root)
    tracked_secret_files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if ignored(rel, globs):
            # `.env` is expected and stays local. Backup copies of it are not; flag them so they get
            # moved out of the folder, not merely ignored.
            if ".bak" in p.name or (p.name.startswith(".env") and p.name != ".env"):
                tracked_secret_files.append(rel)
            continue
        if p.stat().st_size > TEXT_MAX_BYTES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        scan_text(text, rel, findings)
    return findings, tracked_secret_files


def scan_stdin():
    findings = []
    where = "history"
    buf = sys.stdin.read()
    for lineno, line in enumerate(buf.splitlines(), 1):
        if line.startswith("commit "):
            where = line.split()[1][:12]
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        for name, rx in PATTERNS:
            m = rx.search(line)
            if m and not PLACEHOLDER.search(m.group(0)):
                findings.append((where, lineno, name, redact(m.group(0))))
                break
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description="secret scan before first push")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tree", help="scan this working tree")
    g.add_argument("--stdin", action="store_true", help="scan `git log --all -p` from stdin")
    args = ap.parse_args(argv)

    if args.stdin:
        findings = scan_stdin()
        label = "history"
        extra = []
    else:
        findings, extra = scan_tree(args.tree, load_ignore_globs())
        label = "tree"

    if extra:
        print("Secret-shaped files present (ignored by gitignore, but delete or move them out of the repo):")
        for f in extra:
            print("  " + f)
        print()

    if not findings:
        if extra:
            print("%s scan: no secret values found, but the file(s) above must be moved out before pushing" % label)
            return 1
        print("%s scan: clean" % label)
        return 0

    print("%s scan: %d finding(s)" % (label, len(findings)))
    for where, lineno, name, val in findings:
        print("  %s:%d  %s  %s" % (where, lineno, name, val))
    print()
    print("STOP. Do not push. Tree hits: remove the value and move it to .env. "
          "History hits: push a clean snapshot (see PUSH.md, section 4b), keep history local.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
