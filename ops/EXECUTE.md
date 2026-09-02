# Executor brief for a Claude Code session on the Windows desktop

Paste the block at the bottom into Claude Code on the Windows box. That
session has what the cloud session that built this kit does not: the local
files, `ssh macmini` over Tailscale, the scheduled-tasks MCP, `gh`, and the
Chrome tools for the Routines UI. It executes `ops/RUNBOOK.md` end to end and
leaves a written record on the branch so the result can be verified remotely.

Ground rules the executor must keep, in priority order:

1. Every step's verification line in RUNBOOK.md is a gate. A failed
   verification stops the run at that step; do not improvise around it.
2. Nothing is deleted. Tasks are disabled, plists are parked, files are moved
   to backup folders. If a step would delete, stop and record why.
3. No live ad-account writes and no client-facing sends, ever. The kit has
   none; if a command appears to require one, stop.
4. Secrets stay where they are. Never paste a credential value into the log,
   a commit, or a prompt.
5. Record as you go: append to `ops/EXECUTION-LOG.md` after every step
   (timestamp, step id, what ran, what the verification printed, PASS or
   STOP), commit and push to the branch after sections A, B, and C. The
   remote session reads that file to confirm the outcome.

---

Execute the fleet re-tiering runbook end to end.

Repository: C:\Users\Admin\Projects\egh-ad-creatives (if it is cloned elsewhere, find it first). Fetch and check out branch claude/mac-mini-agent-optimization-7tut4s, then read ops/RUNBOOK.md and ops/EXECUTE.md in full before running anything.

Run RUNBOOK sections in order: the two Console settings (use the Chrome tools; if the Console or the routines page needs a login, stop and say so), then A1 through A4 on this machine, then B1 and B2 over `ssh macmini`, then C1 through C3 in the Routines UI with the Chrome tools. Each section's own document (DEPLOY.md, PRUNE.md, PUSH.md, STEP5.md, CREATE.md) is authoritative for its details.

Rules: every verification line is a gate, stop on the first failure; disable, park, or move, never delete; no live ad-account writes and no client-facing sends; never print or commit a credential value. For A2, use the scheduled-tasks MCP exactly as the paste block in PRUNE.md says. For A3, both scans must print clean before `gh repo create` runs. For B2, run ~/step5/run-step5.sh and confirm two Telegram messages arrived and `launchctl list | grep -c roger` prints 0. For C, create the three connector-only routines first, Run now each, and only then build the Google Ads environment and its seven routines; enable the three write tasks last.

After each step append a dated entry to ops/EXECUTION-LOG.md with the step id, what ran, what the verification printed, and PASS or STOP. Commit with `-c user.name="Conner Crowe" -c user.email="hi@connercrowe.com"` and push to the same branch after sections A, B, and C, and immediately on any STOP. Finish with a summary of what is live, what stopped, and why.
