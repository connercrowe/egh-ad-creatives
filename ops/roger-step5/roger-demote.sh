#!/bin/bash
# DEMOTE path, part 1 of 2: switch every Anthropic model reference in
# openclaw.json from claude-sonnet-4-6 to claude-sonnet-5, validate, refresh
# last-good, restart the gateway, and prove the model answers a ping.
# The OpenClaw version upgrade is part 2 and stays manual (see STEP5.md).
#
# Refuses to run without a backup. Every change goes through the official
# CLI (config patch --dry-run, then apply, then validate), never a hand edit,
# per the 2026-06-22 lesson.
set -u
set -o pipefail

if [ ! -f "$HOME/step5-backups/LATEST" ]; then
  echo "refusing: no backup found. Run roger-backup.sh first." >&2
  exit 2
fi
CFG="$HOME/.openclaw/openclaw.json"
[ -r "$CFG" ] || { echo "cannot read $CFG" >&2; exit 2; }

FROM="${FROM_MODEL:-anthropic/claude-sonnet-4-6}"
TO="${TO_MODEL:-anthropic/claude-sonnet-5}"

# Build a patch that sets every path currently holding FROM to TO.
PATCH="$(/usr/bin/python3 - "$CFG" "$FROM" "$TO" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1], encoding="utf-8"))
frm, to = sys.argv[2], sys.argv[3]
hits = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + [k])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + [i])
    elif node == frm:
        hits.append(path)
walk(cfg, [])
if not hits:
    print("")
    sys.exit(0)
patch = {}
for p in hits:
    cur = patch
    for k in p[:-1]:
        cur = cur.setdefault(k, {})
    cur[p[-1]] = to
print(json.dumps(patch, indent=2))
for p in hits:
    print("path: " + ".".join(str(x) for x in p), file=sys.stderr)
PY
)"
if [ -z "$PATCH" ]; then
  echo "no occurrences of $FROM in $CFG; nothing to change"
  exit 0
fi

TMP="${TMPDIR:-/tmp}/roger-demote-$$.json"
printf '%s\n' "$PATCH" > "$TMP"
echo "patch to apply:"; cat "$TMP"

echo "--- dry run"
openclaw config patch --file "$TMP" --dry-run || { echo "dry run failed; aborting" >&2; exit 1; }
echo "--- apply"
openclaw config patch --file "$TMP" || { echo "apply failed; restore from backup" >&2; exit 1; }
echo "--- validate"
openclaw config validate || { echo "config invalid after patch; restoring last-good" >&2; cp "$CFG.last-good" "$CFG"; exit 1; }
cp "$CFG" "$CFG.last-good"
echo "last-good refreshed"

LAUNCHCTL="${LAUNCHCTL:-/bin/launchctl}"
echo "--- restart gateway"
"$LAUNCHCTL" kickstart -k "gui/$(id -u)/ai.openclaw.gateway"
sleep "${SETTLE_SECONDS:-20}"
echo "--- health"
openclaw health --json 2>/dev/null | head -c 400; echo
echo "--- model ping (this is the check that caught the June Haiku failure)"
PING_OUT="$(openclaw agent --agent main -m "ping" --timeout 60 2>&1)"
printf '%s\n' "$PING_OUT" | tail -5
if printf '%s' "$PING_OUT" | grep -qi "unknown model\|model_not_found\|not_found"; then
  echo "MODEL FAILED on $TO. Restore the pre-change state:" >&2
  echo "  tar -xzf \"\$(cat ~/step5-backups/LATEST)/dot-openclaw.tgz\" -C ~" >&2
  echo "  $LAUNCHCTL kickstart -k gui/$(id -u)/ai.openclaw.gateway" >&2
  exit 1
fi
echo "model switch complete: $TO. Because the CLI drove the main session, run ~/bin/reset-roger.sh now so Telegram replies route again."
