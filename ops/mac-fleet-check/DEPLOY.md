# fleet-check: deploy to the Mac Mini

Step one of the fleet re-tiering. A daily email that answers one question:
is every launchd job on the Mac loaded, recent, and exiting clean?

It reads `~/Library/LaunchAgents/*.plist` (labels starting `com.conner.`,
`com.connercrowe.`, `ai.openclaw.`), compares against `launchctl list`,
derives each job's expected cadence from its own `StartCalendarInterval` or
`StartInterval`, and checks the age of the log file named in the plist. It
never touches a job. It sends through the existing `ops-mailer` path
(`ops@connercrowe.com` to `hi@`), no new secrets.

Why it exists: the EZpanl report sat unloaded for nine days and nothing said so.
A job that does not exist cannot tell you it did not run. This checker lives
outside every job, so a missing job is a visible line, not silence.

Statuses: `OK`, `NOT_LOADED` (plist present, not bootstrapped), `STALE`
(log older than 1.5x the largest schedule gap plus 2h), `FAILED` (last exit
nonzero), `NO_LOG`, `NOT_RUNNING` (KeepAlive service with no PID),
`UNLOADED_BY_DESIGN` (listed in config, reported but not counted).

The email sends every day, issues or not. **No email by 10:45 means the
checker itself did not run.** That is the dead-man signal.

## Files

| File | Goes to |
|---|---|
| `fleet_check.py`, `fleet-check.json`, `test_fleet_check.py` | `~/Projects/fleet-check/` |
| `run-fleet-check.sh` | `~/bin/run-fleet-check.sh` (already inside Roger's `~/bin/*.sh` allowlist) |
| `com.conner.fleet-check.plist` | `~/Library/LaunchAgents/` |

Runs on `/usr/bin/python3` (system 3.9). Stdlib only. No venv.

## 1. Copy from Windows (PowerShell 5.1)

Fetch the branch into wherever `egh-ad-creatives` is cloned, then scp the folder.
Replace the clone path if yours differs.

```powershell
git -C "C:\Users\Admin\Projects\egh-ad-creatives" fetch origin claude/mac-mini-agent-optimization-7tut4s
git -C "C:\Users\Admin\Projects\egh-ad-creatives" checkout claude/mac-mini-agent-optimization-7tut4s
ssh macmini "mkdir -p ~/Projects/fleet-check ~/bin ~/Library/Logs"
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\fleet_check.py" macmini:~/Projects/fleet-check/
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\fleet-check.json" macmini:~/Projects/fleet-check/
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\test_fleet_check.py" macmini:~/Projects/fleet-check/
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\run-fleet-check.sh" macmini:~/bin/run-fleet-check.sh
scp "C:\Users\Admin\Projects\egh-ad-creatives\ops\mac-fleet-check\com.conner.fleet-check.plist" macmini:~/Library/LaunchAgents/
```

If `ssh macmini` fails with a BOM error from `~/.ssh/config`, add
`-F /dev/null -i "$env:USERPROFILE\.ssh\id_macmini"` and use
`frontdesk@100.64.180.32` in place of `macmini`.

## 2. On the Mac (over `ssh macmini`)

Run each line on its own.

```bash
chmod +x ~/bin/run-fleet-check.sh
cd ~/Projects/fleet-check && /usr/bin/python3 -m unittest test_fleet_check.py
```

Expect `OK` with 23 tests. Then the dry run, which is also the discovery pass:

```bash
~/bin/run-fleet-check.sh --no-send
```

Read the table. Every job on the box appears with its derived cadence
(`EVERY`) and log age. Three things to fix in `fleet-check.json` before
loading the schedule:

- A job that shows `NOT_LOADED` and is intentionally parked (EZpanl report
  until its three credentials exist, the two Brand It Meta jobs, the killed
  negatives autopilot, greenacre-sweep) goes in `expected_unloaded`. The
  labels prefilled there are from the vault and need confirming against
  what the table actually shows.
- A job that shows `NO_LOG` has no `StandardOutPath` in its plist. Either
  add `"overrides": {"<label>": {"log": "/path/to/its.log"}}` or, for jobs
  that legitimately write nothing on a healthy run, `{"skip_log": true}`.
- A job whose `EVERY` is wrong (an unusual schedule the derivation
  misreads) gets `{"max_age_hours": N}` in `overrides`.

Re-run `--no-send` until the table reads the way you expect. Then one real send:

```bash
~/bin/run-fleet-check.sh
```

Confirm the email lands at hi@ with subject `[fleet-check] ...`. Then load:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.conner.fleet-check.plist
launchctl list | grep fleet-check
```

Schedule: daily 10:30 Pacific, after the Monday 09:30 SugarBabies recap so
every morning job has fired before it looks.

## 3. Optional

- **Dead-man on the checker itself.** Create a healthchecks.io check with a
  1-day period and 2h grace, paste its ping URL into `healthchecks_url` in
  the config. The checker pings on success and `/fail` when it cannot mail.
  Without it, the absence of the daily email is the signal.
- **Calendar mirror.** Add a Free event "Fleet check" daily 10:30 to the
  Automations calendar if you want the full mirror.

## Disable

```bash
launchctl bootout gui/$(id -u)/com.conner.fleet-check
```

## Not in scope, on purpose

No writes, no restarts, no `launchctl kickstart`. The checker reports.
Roger's healthcheck already self-heals the gateway; this one covers
everything the gateway is not.
