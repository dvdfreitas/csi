#!/bin/bash
# Copia os scripts deste projeto para o servidor do LIACC.
# Precisa da VPN da FEUP: o host está num endereço 10.x privado.
# O caminho de volta é scripts/liacc_fetch.sh.
#
# Usa tar sobre ssh em vez de rsync, porque o servidor não tem rsync. Tudo passa
# numa única ligação, logo a password é pedida uma vez.
#
# A estrutura no servidor é igual à de cá, para o mesmo comando correr nos dois
# lados. O que fica em ~/csi lá:
#   scripts/                            (sem __pycache__)
#   storage/app/private/runs/run.json

set -euo pipefail

HOST="liacc"
REMOTE_DIR="csi"
LOCAL="$(cd "$(dirname "$0")/.." && pwd)"

cd "$LOCAL"
tar czf - --exclude=__pycache__ scripts storage/app/private/runs \
| ssh "$HOST" "mkdir -p '$REMOTE_DIR/logs' && tar xzvf - -C '$REMOTE_DIR'"
