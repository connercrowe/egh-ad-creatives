# Step five: retire Roger

Decision: **retire**. `run-step5.sh` executes the whole retire path in order
(backup, token extraction, notify.sh swap, retire) and stops at the first
failure. The demote path below is kept for reference and as the fallback if
inbound Telegram control turns out to matter more than expected.

Roger = the OpenClaw agent on the Mac Mini (gateway `ai.openclaw.gateway`,
Telegram bot @Crowe_ops_bot, plus its two babysitters `com.conner.roger-healthcheck`
and `com.conner.roger-reset`). None of the client reports depend on it; they are
launchd jobs. What Roger uniquely does today: inbound Telegram chat, on-demand
"run X now", the exec reviewer, and one cron (Vanity Resource weekly).

Everything here is run over `ssh macmini`. Scripts are bash 3.2 compatible and
refuse to run out of order.

## 0. Before either path (both required)

**A. Console spend cap.** Anthropic Console, Plans and Billing, Limits. Set a
monthly cap on the org and, if the UI allows, on the key named for Roger in the Console.
This has been an open loop since June and is the only hard backstop OpenClaw
does not provide. Two minutes, no script.

**B. Copy the scripts to the Mac** (PowerShell, from the egh-ad-creatives clone):

```powershell
git -C "C:\Users\Admin\Projects\egh-ad-creatives" pull origin claude/mac-mini-agent-optimization-7tut4s
ssh macmini "mkdir -p ~/step5"
Get-ChildItem "C:\Users\Admin\Projects\egh-ad-creatives\ops\roger-step5\*.sh" | ForEach-Object { scp $_.FullName macmini:"~/step5/" }
ssh macmini "chmod +x ~/step5/*.sh"
```

**C. Backup, then move the Telegram token out of OpenClaw:**

```bash
~/step5/roger-backup.sh
~/step5/telegram-env-extract.sh
```

The second script writes `~/.config/telegram/notify.env` (mode 600) and sends
one test message through the Bot API with OpenClaw not in the loop. If the
test message does not arrive, stop; nothing else has changed yet.

**D. Swap notify.sh so the wrappers use the env file:**

```bash
diff ~/bin/notify.sh ~/step5/notify.sh
```

Read the diff. The new one takes the message as arguments or on stdin, which
covers the two call shapes the wrappers use. If a wrapper passes flags the old
script understood, keep the old script and change only its token line to
`. ~/.config/telegram/notify.env`. Otherwise:

```bash
cp ~/step5/notify.sh ~/bin/notify.sh
TELEGRAM_DRY_RUN=1 ~/bin/notify.sh "dry run"
~/bin/notify.sh "step five: notify.sh swapped"
```

The old copy is in the backup folder as `notify.sh.orig`.

After C and D, alerts from every launchd job are independent of OpenClaw.
That is true whichever path you take next, and it is the point of no regret.

## Path 1: RETIRE (recommended)

```bash
~/step5/roger-retire.sh
```

Boots out the gateway and both babysitters, parks their plists under
`~/Library/LaunchAgents/_disabled-step5/`, leaves the binary and `~/.openclaw`
untouched. Prints the rollback. Then:

- Update `~/Projects/fleet-check/fleet-check.json`: remove
  `com.conner.roger-healthcheck` from `overrides` (harmless if left).
- Delete the Telegram bot's webhook? Not needed; the bot simply stops answering.
- The `Automations` calendar has no Roger events, nothing to remove.

What you lose, and the replacement:

| Lost | Replacement |
|---|---|
| Telegram "run the Greenacre report now" | `ssh macmini '~/bin/greenacre-report.sh'` from any device on the tailnet, or fire a Routine from the routines page |
| Exec reviewer | Nothing to review; no agent runs shell on the box |
| Vanity Resource weekly cron | Accept the loss. VR is not auto-drafting by design, and the VR site moves to Shopify in Sept/Oct, which retires the WordPress publisher anyway |
| Roger-reset and roger-healthcheck | Not needed without the gateway |

## Path 2: DEMOTE

Part 1, model switch (scripted, verified):

```bash
~/step5/roger-demote.sh
~/bin/reset-roger.sh
```

The script finds every `anthropic/claude-sonnet-4-6` in `openclaw.json`,
patches them to `anthropic/claude-sonnet-5` through `openclaw config patch`
(dry run, apply, validate), refreshes `last-good`, restarts the gateway, and
pings the model. If the ping reports an unknown model it tells you how to
restore. Sonnet 5 is listed in OpenClaw's Anthropic provider docs as of the
2026.8.x releases; on 2026.5.28 it is possible the model is not recognised,
in which case the script fails safe and part 2 comes first.

Part 2, version upgrade (manual, watched):

1. Find how it was installed: `brew list openclaw 2>/dev/null` or `npm ls -g openclaw`.
2. Read the release notes between 2026.5.28 and the current extended-stable
   release for `tools.exec` and `approvals` changes. The June crash loop was a
   config-schema conflict; the same class of change is the risk here.
3. Upgrade with the matching tool, then `openclaw config validate` BEFORE
   restarting. If validation fails, fix the config with `openclaw config
   set/unset`, never by hand, and validate again.
4. `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway`, wait 30s,
   `openclaw health --json`, then `openclaw agent --agent main -m "ping"`.
5. `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.last-good` so the
   healthcheck restores the right thing next time.
6. Re-check `openclaw approvals get` still shows the `~/bin/*.sh` allowlist and
   `ask: on-miss`. Re-check `tools.exec.mode` is `auto` so the reviewer runs.

Rollback for part 2: reinstall the pinned old version with the same tool,
`tar -xzf $(cat ~/step5-backups/LATEST)/dot-openclaw.tgz -C ~`, kickstart.

## After either path

- Run `~/bin/run-fleet-check.sh --no-send` and confirm the table reads as expected.
- Delete `~/step5-backups/<timestamp>` only after a week of clean daily fleet-check emails.
