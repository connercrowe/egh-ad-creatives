#!/bin/bash
# One-shot step five, RETIRE path, in the only safe order:
#   backup -> move Telegram token out of OpenClaw -> swap notify.sh -> retire.
# Stops at the first failure. Every piece is individually re-runnable.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"

step() { printf '\n===== %s\n' "$*"; }

step "1/4 backup"
"$HERE/roger-backup.sh" || { echo "backup failed; nothing changed" >&2; exit 1; }

step "2/4 telegram token -> ~/.config/telegram/notify.env (sends one test message)"
"$HERE/telegram-env-extract.sh" || { echo "token extraction or test send failed; nothing else changed" >&2; exit 1; }

step "3/4 notify.sh swap"
if [ -f "$HOME/bin/notify.sh" ]; then
  if diff -q "$HOME/bin/notify.sh" "$HERE/notify.sh" >/dev/null 2>&1; then
    echo "notify.sh already current"
  else
    echo "old notify.sh (kept in the backup folder as notify.sh.orig):"
    sed -n '1,40p' "$HOME/bin/notify.sh"
    cp "$HERE/notify.sh" "$HOME/bin/notify.sh"
    chmod +x "$HOME/bin/notify.sh"
    echo "installed new notify.sh"
  fi
else
  mkdir -p "$HOME/bin"
  cp "$HERE/notify.sh" "$HOME/bin/notify.sh"
  chmod +x "$HOME/bin/notify.sh"
  echo "installed notify.sh (none existed)"
fi
"$HOME/bin/notify.sh" "step five: notify.sh now runs independent of OpenClaw" || { echo "new notify.sh could not send; restoring the old one" >&2; cp "$(cat "$HOME/step5-backups/LATEST")/notify.sh.orig" "$HOME/bin/notify.sh" 2>/dev/null; exit 1; }

step "4/4 retire OpenClaw gateway + babysitters"
"$HERE/roger-retire.sh" || exit 1

step "done"
echo "Next: ~/bin/run-fleet-check.sh --no-send  (the three Roger labels should no longer appear)"
