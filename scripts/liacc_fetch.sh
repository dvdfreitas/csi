#!/bin/bash
# Traz os resultados do servidor do LIACC para cá. Precisa da VPN da FEUP.
# É o contrário de scripts/liacc_sync.sh.
#
# As respostas em ~/csi/storage/app/private/runs/ lá vêm para a mesma pasta aqui,
# sobrepondo-se à cópia local — a do servidor é a que um job acabou de produzir.

set -euo pipefail

HOST="liacc"
REMOTE_DIR="csi"
LOCAL="$(cd "$(dirname "$0")/.." && pwd)"
RUNS="storage/app/private/runs"

cd "$LOCAL"
mkdir -p "$RUNS"
# O glob fica sem expandir aqui de propósito: é a shell remota que o expande.
ssh "$HOST" "cd '$REMOTE_DIR' && ls $RUNS/*-answers.jsonl >/dev/null 2>&1 \
  || { echo 'Ainda não há respostas no servidor — algum job terminou?' >&2; exit 1; }; \
  tar czf - $RUNS/*-answers.jsonl" \
| tar xzvf - --warning=no-timestamp -C "$LOCAL"
