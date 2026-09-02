#!/bin/bash
# Telegram notify, independent of OpenClaw. Drop-in for ~/bin/notify.sh.
#
#   notify.sh "message text"          send the arguments as the message
#   some-command | notify.sh          send stdin as the message (no args)
#   TELEGRAM_DRY_RUN=1 notify.sh ...  print instead of send
#
# Token and chat id come from ~/.config/telegram/notify.env (written by
# telegram-env-extract.sh). Falls back to the old openclaw.json lookup only
# if that file is missing, so the swap cannot break alerts mid-transition.
set -u

ENV_FILE="${TELEGRAM_ENV:-$HOME/.config/telegram/notify.env}"
if [ -r "$ENV_FILE" ]; then
  . "$ENV_FILE"
fi
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] && [ -r "$HOME/.openclaw/openclaw.json" ]; then
  TELEGRAM_BOT_TOKEN="$(/usr/bin/python3 -c 'import re,sys;t=open(sys.argv[1],encoding="utf-8",errors="ignore").read();m=re.search(r"\b(\d{8,12}:[A-Za-z0-9_\-]{35})\b",t);print(m.group(1) if m else "")' "$HOME/.openclaw/openclaw.json")"
fi
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-8644778909}"

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "notify.sh: no Telegram token (expected $ENV_FILE)" >&2
  exit 2
fi

if [ "$#" -gt 0 ]; then
  MSG="$*"
elif [ ! -t 0 ]; then
  MSG="$(cat)"
else
  echo "usage: notify.sh \"message\"  or  cmd | notify.sh" >&2
  exit 2
fi
# Telegram caps a message at 4096 chars; keep the tail, which is where the verdict is.
if [ "${#MSG}" -gt 4000 ]; then
  MSG="...${MSG: -3990}"
fi

if [ "${TELEGRAM_DRY_RUN:-0}" = "1" ]; then
  printf 'notify.sh (dry run) -> chat %s:\n%s\n' "$TELEGRAM_CHAT_ID" "$MSG"
  exit 0
fi

RESP="$(/usr/bin/curl -sS -m 20 -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${MSG}")"
case "$RESP" in
  *'"ok":true'*) exit 0 ;;
  *) echo "notify.sh: send failed: $RESP" >&2; exit 1 ;;
esac
