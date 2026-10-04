#!/bin/bash
# Push this project's scripts and run file to the LIACC server.
# Requires the FEUP VPN to be up (the host is on a private 10.x address).
# The way back is scripts/liacc_fetch.sh.
#
# Uses tar over ssh rather than rsync, because the server has no rsync.
# Everything goes through a single ssh connection, so it asks for the password
# once.
#
# The tree on the server mirrors this one, so the same command runs on both
# sides. What lands in ~/csi there:
#   scripts/                            (without __pycache__)
#   storage/app/private/runs/run.json
#
# Local answers are not pushed: the server is what produces them, one file per
# model in runs/answers/. Neither is run.log, which is the log of a run started
# from the app on this machine; on the server the log goes to logs/.

set -euo pipefail

HOST="liacc"
REMOTE_DIR="csi"
LOCAL="$(cd "$(dirname "$0")/.." && pwd)"

cd "$LOCAL"
# --warning=no-timestamp on the remote tar: the server's clock runs a few
# seconds behind this one, so freshly written files look like they come from
# the future.
tar czf - --exclude=__pycache__ --exclude=answers --exclude=run.log \
  scripts \
  storage/app/private/runs \
| ssh "$HOST" "mkdir -p '$REMOTE_DIR/logs' && tar xzvf - --warning=no-timestamp -C '$REMOTE_DIR'"
