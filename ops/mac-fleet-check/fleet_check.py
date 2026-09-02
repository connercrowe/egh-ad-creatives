#!/usr/bin/env python3
"""fleet-check: is every launchd job on the Mac loaded, recent, and exiting clean?

One daily email. The email's absence is itself the signal that the checker did
not run. Runs on /usr/bin/python3 (macOS system Python 3.9) so it survives a
broken venv. No model, no network beyond the mailer and an optional
healthchecks ping.

Exit codes: 0 = checker ran and the email was sent (issues or not),
            2 = the checker itself failed (could not list jobs, could not mail).
"""
from __future__ import annotations

import argparse
import json
import plistlib
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PREFIXES = ("com.conner.", "com.connercrowe.", "ai.openclaw.")
SELF_LABEL = "com.conner.fleet-check"
STALE_FACTOR = 1.5
GRACE_HOURS = 2.0
HOURS_DAY = 24.0
HOURS_WEEK = 168.0
HOURS_MONTH = 31 * 24.0

DEFAULT_CONFIG = {
    "email_to": "hi@connercrowe.com",
    "mailer": ["/usr/bin/python3", str(Path.home() / "Projects" / "ops-mailer" / "send_email.py")],
    "healthchecks_url": "",
    "expected_unloaded": [],
    "ignore_labels": [],
    "overrides": {},
}


# ---------------------------------------------------------------- config

def load_config(path):
    cfg = dict(DEFAULT_CONFIG)
    p = Path(path)
    if p.exists():
        with p.open() as fh:
            cfg.update(json.load(fh))
    return cfg


# ---------------------------------------------------------------- launchctl

def parse_launchctl(text):
    """Parse `launchctl list` output -> {label: (pid or None, last_exit_status)}."""
    jobs = {}
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3 or parts[0] == "PID":
            continue
        pid_s, status_s, label = parts[0].strip(), parts[1].strip(), parts[2].strip()
        pid = None if pid_s in ("-", "") else int(pid_s)
        try:
            status = int(status_s)
        except ValueError:
            status = 0
        jobs[label] = (pid, status)
    return jobs


def run_launchctl():
    out = subprocess.run(["/bin/launchctl", "list"], capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise RuntimeError("launchctl list failed: %s" % out.stderr.strip())
    return parse_launchctl(out.stdout)


# ---------------------------------------------------------------- schedule

def _max_circular_gap(slots, period):
    if not slots:
        return period
    s = sorted(set(slots))
    if len(s) == 1:
        return period
    gaps = [s[i + 1] - s[i] for i in range(len(s) - 1)]
    gaps.append(period - s[-1] + s[0])
    return max(gaps)


def expected_interval_hours(pl):
    """Largest gap between consecutive firings, in hours. None = not scheduled."""
    if "StartInterval" in pl:
        return float(pl["StartInterval"]) / 3600.0
    sci = pl.get("StartCalendarInterval")
    if sci is None:
        return None
    entries = sci if isinstance(sci, list) else [sci]
    if any("Day" in e or "Month" in e for e in entries):
        return HOURS_MONTH
    if any("Weekday" in e for e in entries):
        if not all("Weekday" in e for e in entries):
            return HOURS_DAY
        slots = []
        for e in entries:
            wd = int(e["Weekday"]) % 7
            slots.append(wd * 24 + float(e.get("Hour", 0)) + float(e.get("Minute", 0)) / 60.0)
        return _max_circular_gap(slots, HOURS_WEEK)
    if any("Hour" in e for e in entries):
        slots = [float(e.get("Hour", 0)) + float(e.get("Minute", 0)) / 60.0 for e in entries]
        return _max_circular_gap(slots, HOURS_DAY)
    if any("Minute" in e for e in entries):
        return 1.0
    return HOURS_DAY


def job_kind(pl):
    if pl.get("KeepAlive"):
        return "service"
    if expected_interval_hours(pl) is not None:
        return "scheduled"
    return "on-demand"


# ---------------------------------------------------------------- inventory

def read_plists(agents_dir):
    found = []
    for p in sorted(Path(agents_dir).glob("*.plist")):
        try:
            with p.open("rb") as fh:
                pl = plistlib.load(fh)
        except Exception as exc:  # noqa: BLE001
            found.append({"label": p.stem, "path": str(p), "error": "unreadable plist: %s" % exc})
            continue
        label = pl.get("Label", p.stem)
        if not label.startswith(PREFIXES):
            continue
        found.append({"label": label, "path": str(p), "plist": pl})
    return found


def log_path_for(entry, cfg):
    ov = cfg.get("overrides", {}).get(entry["label"], {})
    if ov.get("log"):
        return Path(ov["log"]).expanduser()
    pl = entry.get("plist", {})
    for key in ("StandardOutPath", "StandardErrorPath"):
        if pl.get(key):
            return Path(pl[key]).expanduser()
    return None


def hours_since(path, now):
    try:
        return (now - path.stat().st_mtime) / 3600.0
    except OSError:
        return None


# ---------------------------------------------------------------- assess

def assess(entries, loaded, cfg, now):
    """Return list of row dicts with a status per job."""
    rows = []
    unloaded_ok = set(cfg.get("expected_unloaded", []))
    ignore = set(cfg.get("ignore_labels", []))
    for e in entries:
        label = e["label"]
        if label in ignore or label == SELF_LABEL:
            continue
        row = {"label": label, "kind": "?", "status": "OK", "detail": "", "interval_h": None, "age_h": None, "exit": None}
        if "error" in e:
            row.update(status="BROKEN_PLIST", detail=e["error"])
            rows.append(row)
            continue
        pl = e["plist"]
        kind = job_kind(pl)
        row["kind"] = kind
        interval = expected_interval_hours(pl)
        row["interval_h"] = interval
        ov = cfg.get("overrides", {}).get(label, {})
        if ov.get("max_age_hours"):
            interval = float(ov["max_age_hours"]) / STALE_FACTOR
            row["interval_h"] = interval

        is_loaded = label in loaded
        if not is_loaded:
            if label in unloaded_ok:
                row.update(status="UNLOADED_BY_DESIGN", detail="plist present, intentionally not loaded")
            else:
                row.update(status="NOT_LOADED", detail="plist present in LaunchAgents but launchctl does not list it")
            rows.append(row)
            continue

        pid, status = loaded[label]
        row["exit"] = status
        if kind == "service":
            if pid is None:
                row.update(status="NOT_RUNNING", detail="KeepAlive service has no PID (last exit %d)" % status)
            elif status != 0:
                row.update(status="RESTARTING", detail="running, but last exit was %d" % status)
            rows.append(row)
            continue

        if status != 0:
            row.update(status="FAILED", detail="last run exited %d" % status)

        if not ov.get("skip_log"):
            lp = log_path_for(e, cfg)
            if lp is None:
                if row["status"] == "OK":
                    row.update(status="NO_LOG", detail="no StandardOutPath in plist; add overrides.%s.log" % label)
            else:
                age = hours_since(lp, now)
                row["age_h"] = age
                if age is None:
                    if row["status"] == "OK":
                        row.update(status="NO_LOG", detail="log never written: %s" % lp)
                elif interval is not None and age > interval * STALE_FACTOR + GRACE_HOURS:
                    stale = "log %s old, expected every %s" % (fmt_h(age), fmt_h(interval))
                    if row["status"] == "OK":
                        row.update(status="STALE", detail=stale)
                    else:
                        row["detail"] += "; " + stale
        rows.append(row)
    return rows


ISSUE_STATUSES = ("NOT_LOADED", "FAILED", "STALE", "NO_LOG", "NOT_RUNNING", "RESTARTING", "BROKEN_PLIST")


def summarize(rows):
    issues = [r for r in rows if r["status"] in ISSUE_STATUSES]
    return issues


def fmt_h(h):
    if h is None:
        return "-"
    if h < 48:
        return "%.0fh" % h
    return "%.1fd" % (h / 24.0)


def render(rows, hostname, when):
    issues = summarize(rows)
    lines = []
    lines.append("fleet-check on %s at %s" % (hostname, when.strftime("%Y-%m-%d %H:%M %Z")))
    lines.append("%d jobs scanned, %d issue(s)" % (len(rows), len(issues)))
    lines.append("")
    if issues:
        lines.append("ISSUES")
        for r in issues:
            lines.append("  %-18s %-45s %s" % (r["status"], r["label"], r["detail"]))
        lines.append("")
    lines.append("%-18s %-45s %-10s %-8s %-8s %s" % ("STATUS", "LABEL", "KIND", "EVERY", "LOG AGE", "EXIT"))
    for r in rows:
        lines.append("%-18s %-45s %-10s %-8s %-8s %s" % (
            r["status"], r["label"], r["kind"], fmt_h(r["interval_h"]), fmt_h(r["age_h"]),
            "-" if r["exit"] is None else r["exit"]))
    lines.append("")
    lines.append("STALE = log older than 1.5x the largest gap in the schedule plus 2h. "
                 "NOT_LOADED = the EZpanl failure class: built, never bootstrapped. "
                 "Silence from this email means the checker itself did not run.")
    return "\n".join(lines)


def subject(rows):
    issues = summarize(rows)
    if not issues:
        return "[fleet-check] OK, %d jobs" % len(rows)
    head = ", ".join("%s %s" % (r["status"], r["label"].split(".")[-1]) for r in issues[:3])
    more = "" if len(issues) <= 3 else " +%d" % (len(issues) - 3)
    return "[fleet-check] %d ISSUE%s: %s%s" % (len(issues), "" if len(issues) == 1 else "S", head, more)


# ---------------------------------------------------------------- delivery

def send_mail(cfg, subj, body):
    cmd = list(cfg["mailer"]) + ["--to", cfg["email_to"], "--subject", subj, "--body", body]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError("mailer exited %d: %s" % (out.returncode, (out.stderr or out.stdout).strip()[-500:]))


def ping(url):
    if not url:
        return
    try:
        urllib.request.urlopen(url, timeout=10).read()
    except Exception as exc:  # noqa: BLE001
        print("healthchecks ping failed: %s" % exc, file=sys.stderr)


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=str(Path.home() / "Projects" / "fleet-check" / "fleet-check.json"))
    ap.add_argument("--agents-dir", default=str(Path.home() / "Library" / "LaunchAgents"))
    ap.add_argument("--no-send", action="store_true", help="print the report instead of emailing it")
    ap.add_argument("--launchctl-file", help="testing: read `launchctl list` output from a file")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    now = time.time()
    when = datetime.now(timezone.utc).astimezone()
    try:
        if args.launchctl_file:
            with open(args.launchctl_file) as fh:
                loaded = parse_launchctl(fh.read())
        else:
            loaded = run_launchctl()
        entries = read_plists(args.agents_dir)
    except Exception as exc:  # noqa: BLE001
        print("fleet-check FAILED before assessment: %s" % exc, file=sys.stderr)
        ping(cfg["healthchecks_url"] + "/fail" if cfg["healthchecks_url"] else "")
        return 2

    import socket
    rows = assess(entries, loaded, cfg, now)
    body = render(rows, socket.gethostname(), when)
    subj = subject(rows)

    if args.no_send:
        print(subj)
        print(body)
        return 0
    try:
        send_mail(cfg, subj, body)
    except Exception as exc:  # noqa: BLE001
        print(body)
        print("fleet-check could not send email: %s" % exc, file=sys.stderr)
        ping(cfg["healthchecks_url"] + "/fail" if cfg["healthchecks_url"] else "")
        return 2
    ping(cfg["healthchecks_url"])
    print(subj)
    return 0


if __name__ == "__main__":
    sys.exit(main())
