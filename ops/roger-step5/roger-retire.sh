#!/bin/bash
# RETIRE path: stop the OpenClaw gateway and its two babysitter jobs, park
# their plists, leave the binary and ~/.openclaw in place. Reversible with
# the rollback printed at the end. Refuses to run until the Telegram env file
# exists, because every wrapper's notify.sh would otherwise lose its token.
set -u
set -o pipefail
LAUNCHCTL="${LAUNCHCTL:-/bin/launchctl}"

ENV_FILE="$HOME/.config/telegram/notify.env"
if [ ! -r "$ENV_FILE" ] || ! grep -q '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE"; then
  echo "refusing: $ENV_FILE missing. Run telegram-env-extract.sh first." >&2
  exit 2
fi
if [ ! -f "$HOME/step5-backups/LATEST" ]; then
  echo "refusing: no backup found. Run roger-backup.sh first." >&2
  exit 2
fi

UID_NUM="$(id -u)"
PARK="$HOME/Library/LaunchAgents/_disabled-step5"
mkdir -p "$PARK"

for L in com.conner.roger-healthcheck com.conner.roger-reset ai.openclaw.gateway; do
  P="$HOME/Library/LaunchAgents/$L.plist"
  if "$LAUNCHCTL" list | grep -q "$L"; then
    "$LAUNCHCTL" bootout "gui/$UID_NUM/$L" 2>/dev/null && echo "booted out $L" || echo "bootout of $L returned nonzero (may already be down)"
  else
    echo "$L not loaded"
  fi
  if [ -f "$P" ]; then
    mv "$P" "$PARK/" && echo "parked $L.plist -> $PARK/"
  fi
done

sleep 3
if pgrep -f "[o]penclaw" 2>/dev/null | grep -qv "roger-retire"; then
  echo "WARNING: an openclaw process is still running:"; pgrep -fl "[o]penclaw" | grep -v "roger-retire"
else
  echo "no openclaw process running"
fi

cat <<EOF

Retired. Left in place on purpose: the openclaw binary, ~/.openclaw (config,
cron store, sessions), and the exec-approvals file. Nothing deleted.

What stops with this:
  - Telegram chat with @Crowe_ops_bot (inbound). Outbound alerts continue via notify.sh.
  - OpenClaw cron "Vanity Resource - Weekly" (Fri 05:00).
  - On-demand "run X now" over Telegram. Use: ssh macmini '~/bin/<wrapper>.sh'

Rollback (all three, in this order):
  mv "$PARK"/ai.openclaw.gateway.plist "$HOME/Library/LaunchAgents/"
  mv "$PARK"/com.conner.roger-healthcheck.plist "$HOME/Library/LaunchAgents/"
  mv "$PARK"/com.conner.roger-reset.plist "$HOME/Library/LaunchAgents/"
  launchctl bootstrap gui/$UID_NUM "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
  launchctl bootstrap gui/$UID_NUM "$HOME/Library/LaunchAgents/com.conner.roger-healthcheck.plist"
  launchctl bootstrap gui/$UID_NUM "$HOME/Library/LaunchAgents/com.conner.roger-reset.plist"
EOF
