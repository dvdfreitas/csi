#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["datasets>=5.0.1", "psycopg[binary]>=3.2"]
# ///
"""Importa datasets de perguntas do Hugging Face para a tabela questions.

    uv run scripts/import.py gsm8k

Cada dataset é um ficheiro em scripts/datasets/ que define DATASET (o nome no
Hugging Face), DEFAULTS (valores comuns a todas as linhas) e rows(), que gera um
dict por pergunta. As colunas dataset e hash são preenchidas aqui.

Não acrescentes um __init__.py a essa pasta: passaria a pacote regular e tomaria
o lugar da biblioteca datasets do Hugging Face nos imports.
"""

import argparse
import hashlib
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = Path(__file__).resolve().parent / "datasets"

OPTIONAL = {"subdataset": "default", "reasoning": None}

UPSERT = """
    INSERT INTO questions
        (dataset, subdataset, split, hash, type, language, statement, answer, reasoning, created_at, updated_at)
    VALUES
        (%(dataset)s, %(subdataset)s, %(split)s, %(hash)s, %(type)s, %(language)s,
         %(statement)s, %(answer)s, %(reasoning)s, NOW(), NOW())
    ON CONFLICT (dataset, subdataset, split, hash) DO UPDATE SET
        type = EXCLUDED.type,
        language = EXCLUDED.language,
        statement = EXCLUDED.statement,
        answer = EXCLUDED.answer,
        reasoning = EXCLUDED.reasoning,
        updated_at = NOW()
"""


def env() -> dict:
    """As variáveis do .env do Laravel."""
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip().removeprefix("export ")
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("\"'")

    return values


def record(dataset: str, defaults: dict, row: dict) -> dict:
    """Uma linha do importer com o dataset e o hash preenchidos."""
    record = {**OPTIONAL, **defaults, **row, "dataset": dataset}
    normalized = " ".join(record["statement"].split()).lower()
    record["hash"] = hashlib.sha256(f"{normalized}\n{record['language']}".encode()).hexdigest()

    return record


def main() -> None:
    available = sorted(path.stem for path in DATASETS.glob("*.py"))

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dataset", choices=available, help="dataset a importar")
    args = parser.parse_args()

    sys.path.insert(0, str(DATASETS))
    module = importlib.import_module(args.dataset)

    rows = [record(module.DATASET, module.DEFAULTS, row) for row in module.rows()]

    import psycopg

    config = env()
    with psycopg.connect(
        host=config.get("DB_HOST", "127.0.0.1"),
        port=config.get("DB_PORT", "5432"),
        dbname=config["DB_DATABASE"],
        user=config["DB_USERNAME"],
        password=config.get("DB_PASSWORD") or None,
    ) as conn:
        conn.cursor().executemany(UPSERT, rows)

    print(f"{module.DATASET}: {len(rows)} linhas", file=sys.stderr)


if __name__ == "__main__":
    main()
