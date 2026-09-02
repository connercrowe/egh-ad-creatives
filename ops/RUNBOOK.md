# Fleet re-tiering: the one-sitting runbook

Everything built in this branch, in the order to execute it. Three machines
are involved and none of them was reachable from the session that built this,
so every step below is yours to run. Each has its own verification line.
Budget: about ninety minutes, most of it waiting on scans and test sends.

Decisions already made: keep the Mac Mini and its launchd fleet; move the
recurring desktop watchers to cloud Routines on Sonnet 5; retire OpenClaw.

## Before anything: two Console settings (5 min)

1. Anthropic Console, Plans and Billing, Limits: set a monthly spend cap.
2. claude.ai/code/routines: note the daily run cap shown on the page.

## A. Windows box (PowerShell 5.1, one line at a time)

**A1. Get the branch.**
```powershell
git -C "C:\Users\Admin\Projects\egh-ad-creatives" fetch origin claude/mac-mini-agent-optimization-7tut4s
git -C "C:\Users\Admin\Projects\egh-ad-creatives" checkout claude/mac-mini-agent-optimization-7tut4s
```

**A2. Step two, prune the desktop tasks.** Open Claude Code on the desktop
and paste the block at the bottom of `ops/desktop-tasks-prune/PRUNE.md`.
Verify: the after-table shows 14 disabled, nothing deleted, the Labor Day
revert and Free Freight verdict untouched.

**A3. Step three, push google-ads-mcp.** Follow `ops/google-ads-mcp-repo/PUSH.md`
sections 1 through 6. Verify: both scans print `clean`, the GitHub listing
shows no `.env`, `audit.log`, `profiles`, or `rsa_drafts.json`, and you have
the real environment-variable names from section 6.

**A4. Ship steps one and five to the Mac.**
```powershell
ssh macmini "mkdir -p ~/Projects/fleet-check ~/bin ~/Library/Logs ~/Library/LaunchAgents ~/step5"
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\fleet_check.py" macmini:~/Projects/fleet-check/
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\fleet-check.json" macmini:~/Projects/fleet-check/
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\test_fleet_check.py" macmini:~/Projects/fleet-check/
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\run-fleet-check.sh" macmini:~/bin/run-fleet-check.sh
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\com.conner.fleet-check.plist" macmini:~/Library/LaunchAgents/
Get-ChildItem "C:\Users\Admin\Projects\egh-ad-creatives\ops\roger-step5\*.sh" | ForEach-Object { scp $_.FullName macmini:"~/step5/" }
ssh macmini "chmod +x ~/bin/run-fleet-check.sh ~/step5/*.sh"
```

## B. Mac Mini (over `ssh macmini`, one line at a time)

**B1. Step one, fleet checker.**
```bash
cd ~/Projects/fleet-check && /usr/bin/python3 -m unittest test_fleet_check.py
~/bin/run-fleet-check.sh --no-send
```
Read the table. Adjust `fleet-check.json` per `ops/mac-fleet-check/DEPLOY.md`
section 2 (parked jobs into `expected_unloaded`, missing logs into
`overrides`). Re-run until it reads right, then:
```bash
~/bin/run-fleet-check.sh
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.conner.fleet-check.plist
```
Verify: the `[fleet-check]` email arrives at hi@.

**B2. Step five, retire Roger.**
```bash
~/step5/run-step5.sh
```
It backs up, moves the Telegram token out of OpenClaw, swaps `notify.sh`,
and boots out the gateway and its two babysitters, stopping at the first
failure. Verify: two Telegram messages arrived during the run (token test,
notify.sh test), `launchctl list | grep -c roger` prints 0, and
`~/bin/run-fleet-check.sh --no-send` no longer lists the three Roger labels.
Rollback is printed at the end of the run and kept in `ops/roger-step5/STEP5.md`.

## C. Routines UI (claude.ai/code/routines)

**C1. Three connector-only routines, no environment work needed.** Create
them from `ops/routines/CREATE.md` (prompt files alongside it). Run each once
with Run now, read the output, then disable the matching desktop task.

**C2. The Google Ads environment.** Create an environment per
`ops/google-ads-mcp-repo/ROUTINE-ENV.md`: repo `connercrowe/google-ads-mcp`,
the credential names from A3, Custom network with the four Google hosts,
the pinned pip line as setup script.

**C3. Seven Google Ads routines, plus two deferred.** Ported prompts are in `ops/routines/ports/`.
Each file's header lists any BLOCKER paths; resolve those first (the EZpanl
claim library and the SugarBabies runbook need a repo home, or the step is
dropped). Create each on the environment from C2, Sonnet 5, Run now once,
then disable the desktop twin. Enable the three write tasks last, after the
read-only ones have produced two clean runs. Deferred until their repo and
secret are attached in the UI: `connercrowe-index-watch` and
`connercrowe-citation-remeasure` (see CREATE.md).

## D. After

- One week of green `[fleet-check]` emails, then delete `~/step5-backups/`.
- After 2026-09-08, disable the Labor Day revert and Free Freight verdict tasks.
- Two files stay as the standing record: `ops/RUNBOOK.md` (this) and the
  assessment page at https://claude.ai/code/artifact/b5654d74-f726-4034-9417-e11bf0cada35.
