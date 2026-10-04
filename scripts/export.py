#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg[binary]>=3.2"]
# ///
"""Write the run file that scripts/cultural.py reads on the LIACC server.

The server has no database, so the models and the questions both travel in one
JSON file.

    uv run scripts/export.py --country Portugal --country Brazil
    uv run scripts/export.py --country PT --country BR --language eng

Every model is asked about every question for every country. Countries travel as
an ISO code and one phrase per prompt language: the code identifies the answer,
the phrase goes in the prompt. The run is recorded in the runs table and its id
travels in the file, so answers always say which execution produced them. Models come from
the llms table, questions from the questions table. The run
file lands in storage/app/private/runs/, which is the folder scripts/liacc_sync.sh
carries to the server and scripts/liacc_fetch.sh brings the answers back into.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "storage/app/private/runs"

# How the models are asked to generate. Kept with the run so that answers made
# under different settings can tell each other apart.
PARAMS = {"max_new_tokens": 8, "do_sample": False}

# What the model reads in place of {country}, per prompt language. Shared with the
# Laravel side, which previews the prompts, so it lives in a file both can read.
# These are whole phrases, not bare names, because Portuguese and French contract
# the preposition with the article: "dos Estados Unidos", not "de os Estados Unidos".
# The por and fra templates therefore say "uma pessoa {country}", with no "de".
COUNTRIES = json.loads((ROOT / "config/countries.json").read_text(encoding="utf-8"))


def env() -> dict:
    """The variables in Laravel's .env."""
    values = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip().removeprefix("export ")
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("\"'")

    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--country", action="append", required=True, choices=COUNTRIES, metavar="CODE",
                        help=f"country to ask about, one of {', '.join(COUNTRIES)}; repeat for several")
    parser.add_argument("--limit", type=int, help="how many questions to export (default: all)")
    parser.add_argument("--model", action="append", help="code of a model from the llms table; repeat for several (default: all)")
    parser.add_argument("--language", action="append", help="language of a prompt to use; repeat for several (default: all)")
    parser.add_argument("--out", type=Path, default=RUNS / "run.json", help="where to write the run file")
    args = parser.parse_args()

    import psycopg

    countries = {code: COUNTRIES[code] for code in args.country}
    config = env()
    with psycopg.connect(
        host=config.get("DB_HOST", "127.0.0.1"),
        port=config.get("DB_PORT", "5432"),
        dbname=config["DB_DATABASE"],
        user=config["DB_USERNAME"],
        password=config.get("DB_PASSWORD") or None,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT code FROM llms" + (" WHERE code = ANY(%s)" if args.model else "") + " ORDER BY parameters",
                (args.model,) if args.model else (),
            )
            models = [code for (code,) in cur.fetchall()]

            cur.execute(
                "SELECT id, statement FROM questions ORDER BY id" + (" LIMIT %s" if args.limit else ""),
                (args.limit,) if args.limit else (),
            )
            questions = [{"id": id, "statement": statement} for id, statement in cur.fetchall()]

            cur.execute(
                "SELECT hash, language, template, affirmative, negative FROM prompts"
                + (" WHERE language = ANY(%s)" if args.language else "")
                + " ORDER BY language",
                (args.language,) if args.language else (),
            )
            prompts = [
                {"hash": hash, "language": language, "template": template, "affirmative": yes, "negative": no}
                for hash, language, template, yes, no in cur.fetchall()
            ]

            # The row is the index, the file is the payload: the server has no
            # database, so everything travels, and the id ties the two together.
            cur.execute(
                "INSERT INTO runs (models, countries, prompts, params, questions, created_at, updated_at)"
                " VALUES (%s, %s, %s, %s, %s, NOW(), NOW()) RETURNING id",
                (
                    json.dumps(models),
                    json.dumps(countries, ensure_ascii=False),
                    json.dumps([prompt["hash"] for prompt in prompts]),
                    json.dumps(PARAMS),
                    len(questions),
                ),
            )
            run_id = cur.fetchone()[0]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    run = {
        "run": run_id,
        "models": models,
        "countries": countries,
        "prompts": prompts,
        "params": PARAMS,
        "questions": questions,
    }
    args.out.write_text(json.dumps(run, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"run {run_id}: {len(models)} models, {len(countries)} countries, {len(prompts)} prompts, {len(questions)} questions in {args.out}")


if __name__ == "__main__":
    main()
