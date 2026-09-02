#!/bin/bash
# Snapshot everything the retire or demote path touches. Run first, either path.
# Creates ~/step5-backups/<timestamp>/ with the OpenClaw state dir, the three
# Roger plists, notify.sh, and the launchctl listing. Nothing is modified.
set -u
set -o pipefail

TS="$(date +%Y%m%d-%H%M%S)"
DEST="$HOME/step5-backups/$TS"
mkdir -p "$DEST"
chmod 700 "$HOME/step5-backups" "$DEST"

if [ -d "$HOME/.openclaw" ]; then
  /usr/bin/tar -czf "$DEST/dot-openclaw.tgz" -C "$HOME" .openclaw
  echo "saved ~/.openclaw -> $DEST/dot-openclaw.tgz"
fi
for L in ai.openclaw.gateway com.conner.roger-healthcheck com.conner.roger-reset; do
  P="$HOME/Library/LaunchAgents/$L.plist"
  [ -f "$P" ] && cp "$P" "$DEST/" && echo "saved $L.plist"
done
[ -f "$HOME/bin/notify.sh" ] && cp "$HOME/bin/notify.sh" "$DEST/notify.sh.orig" && echo "saved notify.sh"
"${LAUNCHCTL:-/bin/launchctl}" list > "$DEST/launchctl-list.txt" 2>&1
command -v openclaw >/dev/null 2>&1 && openclaw --version > "$DEST/openclaw-version.txt" 2>&1
echo "backup complete: $DEST"
echo "$DEST" > "$HOME/step5-backups/LATEST"
