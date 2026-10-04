#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["datasets>=5.0.1", "psycopg[binary]>=3.2"]
# ///
"""Import question datasets from the Hugging Face into the questions table.

    uv run scripts/import.py gsm8k

Each dataset is a file in scripts/datasets/ defining DATASET (its Hugging Face
name), DEFAULTS (values shared by every row) and rows(), which yields one dict
per question. The dataset and hash columns are filled in here.

Do not add an __init__.py to that folder: it would become a regular package and
take the place of the Hugging Face datasets library in every import.
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
    """The variables in Laravel's .env."""
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip().removeprefix("export ")
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("\"'")

    return values


def record(dataset: str, defaults: dict, row: dict) -> dict:
    """One importer row with the dataset and the hash filled in."""
    record = {**OPTIONAL, **defaults, **row, "dataset": dataset}
    normalized = " ".join(record["statement"].split()).lower()
    record["hash"] = hashlib.sha256(f"{normalized}\n{record['language']}".encode()).hexdigest()

    return record


def main() -> None:
    available = sorted(path.stem for path in DATASETS.glob("*.py"))

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dataset", choices=available, help="dataset to import")
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

    print(f"{module.DATASET}: {len(rows)} rows", file=sys.stderr)


if __name__ == "__main__":
    main()
