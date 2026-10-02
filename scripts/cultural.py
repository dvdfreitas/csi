#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["torch>=2.4", "transformers>=4.45", "accelerate>=1.0"]
# ///
"""Ask every model in a run file whether a question is hard for each country.

Meant to run on the LIACC server, where there is no database: the models, the
countries and the questions all come in the run file written by
scripts/export.py, and the answers go out as JSONL.

    uv run scripts/cultural.py run.json
"""

import argparse
import gc
import json
import re
from pathlib import Path

PROMPT = """Does this question contain any information that a person from {country} would have difficulty understanding?

Question:
{statement}

Answer with one word only: YES or NO."""

# The first YES or NO the model utters; models that ignore the format give None.
VERDICT = re.compile(r"\b(YES|NO)\b", re.IGNORECASE)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path, help="run file from scripts/export.py")
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    run = json.loads(args.run.read_text(encoding="utf-8"))
    questions = run["questions"]
    out = args.run.with_name(f"{args.run.stem}-answers.jsonl")

    with out.open("w", encoding="utf-8") as fh:
        for name in run["models"]:
            print(f"== {name}", flush=True)
            tokenizer = AutoTokenizer.from_pretrained(name)
            model = AutoModelForCausalLM.from_pretrained(name, dtype="auto", device_map="auto")

            for question in questions:
                for code, country in run["countries"].items():
                    prompt = PROMPT.format(country=country, statement=question["statement"])
                    inputs = tokenizer.apply_chat_template(
                        [{"role": "user", "content": prompt}],
                        add_generation_prompt=True,
                        return_tensors="pt",
                        return_dict=True,
                    ).to(model.device)

                    with torch.inference_mode():
                        generated = model.generate(**inputs, max_new_tokens=8, do_sample=False)

                    answer = tokenizer.decode(generated[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True).strip()
                    verdict = VERDICT.search(answer)

                    fh.write(json.dumps({
                        "id": question["id"],
                        "country": code,
                        "model": name,
                        "verdict": verdict.group(1).upper() if verdict else None,
                        "answer": answer,
                    }, ensure_ascii=False) + "\n")

                    print(f"#{question['id']} {code} {verdict.group(1).upper() if verdict else '?'}", flush=True)

            # Free the GPU before the next model is loaded.
            del model, tokenizer
            gc.collect()
            torch.cuda.empty_cache()

    print(f"answers in {out}")


if __name__ == "__main__":
    main()
