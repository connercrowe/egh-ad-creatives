#!/usr/bin/env python3
"""Port a Claude Code desktop scheduled task (SKILL.md) into a cloud Routine prompt.

    python port_task.py <task-dir-or-SKILL.md> [more ...] --out ops/routines/ports

Mechanical, reviewable transformations only:
  - strips the YAML frontmatter, keeps name/description as a header
  - prepends the cloud preamble (unattended, fresh clone, fail fast if the package is missing)
  - rewrites `cd "C:/Users/Admin/Projects/google-ads-mcp" && ` to nothing and other
    references to that path to "the repository root (your working directory)"
  - lists every other Windows path as a BLOCKER in the header so nothing is silently lost
  - drops the trailing "Keep the intel log rotated" section (local script)
  - appends the output rule: logs cannot be written from the cloud, format the entry instead
Everything else in the prompt is preserved verbatim.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MCP_ROOT = "C:/Users/Admin/Projects/google-ads-mcp"
WIN_PATH = re.compile(r"C:[/\\][A-Za-z0-9_./\\ -]+")
ROTATE_HEADING = re.compile(r"^## Keep the intel log rotated\s*$", re.M)

PREAMBLE = (
    "You are running unattended as a cloud Routine: a fresh clone of the google-ads-mcp "
    "repository is your working directory, PYTHONPATH=src and the Google Ads credentials are "
    "set as environment variables, and there is no browser and no access to Conner's desktop "
    "files. If `python -c \"import google_ads_mcp\"` fails or the credentials are missing, say so "
    "in one line as your entire report and stop. GOOGLE_ADS_ALLOW_WRITES is not set in the "
    "environment; a task that is permitted one write sets it inline on that command only, "
    "exactly as written below.\n\n"
)

FOOTER = (
    "\n\n## Output rule for the cloud\n"
    "You cannot append to any account-management log or local report file from here. Put the "
    "dated log entry, in the log's established format, at the end of your final message so it "
    "can be pasted in by hand. The final message is the deliverable.\n"
)


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, text[m.end():]


def port(text):
    meta, body = split_frontmatter(text)
    body = ROTATE_HEADING.split(body)[0].rstrip()

    body = re.sub(r'cd\s+"?' + re.escape(MCP_ROOT) + r'"?\s*(&&|;|\bthen\b)\s*', "", body)
    body = re.sub(r'cd\s+"?' + re.escape(MCP_ROOT) + r'"?', "stay in the repository root", body)
    body = body.replace(MCP_ROOT + "/.env", "the environment variables (no .env file exists in the cloud)")
    body = body.replace(MCP_ROOT + "/src", "src")
    body = body.replace(MCP_ROOT, "the repository root (your working directory)")

    blockers = sorted(set(p.replace("\\", "/").rstrip() for p in WIN_PATH.findall(body)))
    header = ["# Routine port: %s" % meta.get("name", "unknown")]
    if meta.get("description"):
        header.append("Source description: " + meta["description"])
    header.append("Ported mechanically by port_task.py; review before creating the routine.")
    if blockers:
        header.append("")
        header.append("BLOCKERS (paths that do not exist in the cloud; give each a repo home or drop the step):")
        for b in blockers:
            header.append("  - " + b)
    header.append("")
    header.append("---")
    header.append("")
    return "\n".join(header) + PREAMBLE + body.lstrip() + FOOTER, blockers


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for s in args.sources:
        p = Path(s)
        if p.is_dir():
            p = p / "SKILL.md"
        text = p.read_text(encoding="utf-8")
        ported, blockers = port(text)
        name = p.parent.name if p.name == "SKILL.md" else p.stem
        dest = out / (name + ".md")
        dest.write_text(ported, encoding="utf-8")
        print("%-40s -> %s  (%d blocker path%s)" % (name, dest, len(blockers), "" if len(blockers) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
