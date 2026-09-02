#!/bin/bash
# fleet-check wrapper. launchd does not inherit PATH; keep everything absolute.
set -u
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin"
exec /usr/bin/python3 "$HOME/Projects/fleet-check/fleet_check.py" ${1+"$@"}
