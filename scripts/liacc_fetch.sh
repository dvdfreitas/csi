#!/bin/bash
# Bring the answers back from the LIACC server. Requires the FEUP VPN to be up.
# Counterpart of scripts/liacc_sync.sh.
#
# The answers in ~/csi/storage/app/private/runs/answers/<run>/ there come back to
# the same folders here, one file per model plus its .status.json, overwriting the
# local copy — the server's is the one a job has just produced.
#
# Files still being written (.jsonl.part) travel too, so a run can be looked at
# while it goes. What says a model is finished is finished_at in its .status.json, not the name.

set -euo pipefail

HOST="liacc"
REMOTE_DIR="csi"
LOCAL="$(cd "$(dirname "$0")/.." && pwd)"
RUNS="storage/app/private/runs/answers"

cd "$LOCAL"
mkdir -p "$RUNS"
# The glob is left unexpanded here on purpose: the remote shell expands it.
ssh "$HOST" "cd '$REMOTE_DIR' && ls $RUNS/*/*.jsonl* >/dev/null 2>&1 \
  || { echo 'No answers on the server yet - has a job started?' >&2; exit 1; }; \
  tar czf - $RUNS/*/*.jsonl* \$(ls $RUNS/*/*.status.json 2>/dev/null)" \
| tar xzvf - --warning=no-timestamp -C "$LOCAL"
