#!/bin/bash
# Move the Telegram bot token out of ~/.openclaw/openclaw.json into its own
# env file so notify.sh (and every wrapper that calls it) keeps working with
# or without OpenClaw. Read-only against openclaw.json. Idempotent.
#
# Usage: telegram-env-extract.sh [--chat-id 8644778909]
# Result: ~/.config/telegram/notify.env (chmod 600) with TELEGRAM_BOT_TOKEN
# and TELEGRAM_CHAT_ID, then one test message so the path is proven.
set -u
set -o pipefail

CHAT_ID="8644778909"
if [ "${1:-}" = "--chat-id" ] && [ -n "${2:-}" ]; then CHAT_ID="$2"; fi

SRC="${OPENCLAW_JSON:-$HOME/.openclaw/openclaw.json}"
DST_DIR="$HOME/.config/telegram"
DST="$DST_DIR/notify.env"

if [ -f "$DST" ] && grep -q '^TELEGRAM_BOT_TOKEN=' "$DST"; then
  echo "already present: $DST"
else
  if [ ! -r "$SRC" ]; then
    echo "cannot read $SRC" >&2
    exit 2
  fi
  # Bot tokens have a fixed shape: <8-10 digits>:<35 chars>. Match on shape,
  # not on a config key, so this survives whatever nesting OpenClaw uses.
  TOKEN="$(/usr/bin/python3 - "$SRC" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
m = re.search(r"\b(\d{8,10}:[A-Za-z0-9_\-]{35})\b", text)
print(m.group(1) if m else "")
PY
)"
  if [ -z "$TOKEN" ]; then
    echo "no Telegram bot token found in $SRC" >&2
    exit 2
  fi
  mkdir -p "$DST_DIR"
  chmod 700 "$DST_DIR"
  umask 077
  printf 'TELEGRAM_BOT_TOKEN=%s\nTELEGRAM_CHAT_ID=%s\n' "$TOKEN" "$CHAT_ID" > "$DST"
  chmod 600 "$DST"
  echo "wrote $DST"
fi

# Prove the path without OpenClaw in the loop.
. "$DST"
if [ "${TELEGRAM_DRY_RUN:-0}" = "1" ]; then
  echo "dry run: would send test message to chat $TELEGRAM_CHAT_ID"
  exit 0
fi
RESP="$(/usr/bin/curl -sS -m 20 -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=step five: Telegram alerts now run from ~/.config/telegram/notify.env, independent of OpenClaw.")"
case "$RESP" in
  *'"ok":true'*) echo "test message delivered" ;;
  *) echo "test message FAILED: $RESP" >&2; exit 1 ;;
esac
