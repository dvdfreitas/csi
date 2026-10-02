#!/bin/bash
# Traz os resultados do servidor do LIACC para cá. Precisa da VPN da FEUP.
# É o contrário de scripts/liacc_sync.sh.
#
# Tudo o que estiver em ~/csi/storage/app/private/runs/ lá vem para a mesma pasta
# aqui, sobrepondo-se à cópia local — a do servidor é a mais recente.

set -euo pipefail

HOST="liacc"
REMOTE_DIR="csi"
LOCAL="$(cd "$(dirname "$0")/.." && pwd)"
RUNS="storage/app/private/runs"

cd "$LOCAL"
mkdir -p "$RUNS"
ssh "$HOST" "cd '$REMOTE_DIR' && tar czf - '$RUNS'" \
| tar xzvf - -C "$LOCAL"
