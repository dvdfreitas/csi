#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["torch>=2.4", "transformers>=4.45", "accelerate>=1.0"]
# ///
"""Ask every model in a run file whether a question is hard for each country.

Meant to run on the LIACC server, where there is no database: the models, the
prompts, the countries and the questions all come in the run file, written
either by the Run page or by scripts/export.py.

    uv run scripts/cultural.py run.json

One answers file per model, in answers/<run>/ next to the run file, plus a
.status.json beside it. The run is in the path so two runs never write over each
other. The status is written when the model starts, so a file being written
already says which run and which model it is, and rewritten at the end with the
count and finished_at. A model already finished for this same run is skipped, so
re-running resumes where a dead job stopped; a marker from another run is
ignored, because a different run asks different questions.

How the models generate comes from the run file too, so answers produced under
different settings are never confused with each other.

There is no prompt in this file on purpose. Each prompt travels with the words
it asks for ("YES"/"NO", "SIM"/"NÃO", "1"/"2"), so a new prompt or a new
language never means touching the runner.
"""

import argparse
import gc
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

# One progress line every this many answers. Printing each answer meant 36k
# flushed writes for a full run, on a filesystem shared with the whole cluster.
PROGRESS = 100


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def verdict(prompt: dict, answer: str) -> str | None:
    """YES or NO, whatever words this prompt asked for; None if the model used neither."""
    found = re.search(
        rf"\b({re.escape(prompt['affirmative'])}|{re.escape(prompt['negative'])})\b",
        answer,
        re.IGNORECASE,
    )
    if found is None:
        return None

    return "YES" if found.group(1).upper() == prompt["affirmative"].upper() else "NO"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path, help="run file from the Export page or scripts/export.py")
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    run = json.loads(args.run.read_text(encoding="utf-8"))
    answers = args.run.parent / "answers" / str(run["run"])
    answers.mkdir(parents=True, exist_ok=True)

    total = len(run["prompts"]) * len(run["questions"]) * len(run["countries"])

    for name in run["models"]:
        out = answers / f"{name.split('/')[-1]}.jsonl"
        # finished_at in the status is the marker, not the .jsonl: a file whose
        # status has no finished_at was never completed.
        status_path = out.with_suffix(".status.json")
        status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
        if status.get("finished_at") and status.get("run") == run["run"]:
            print(f"== {name} (done already)", flush=True)
            continue

        print(f"== {name} ({total} answers)", flush=True)
        started = time.monotonic()
        tokenizer = AutoTokenizer.from_pretrained(name)
        model = AutoModelForCausalLM.from_pretrained(name, dtype="auto", device_map="auto")

        # Written aside and renamed at the end: a job killed half way leaves a
        # .part file, which does not look finished to the next run.
        part = out.with_suffix(".jsonl.part")
        written = 0

        # Written before the first answer: a file halfway through already says
        # what it is, without anyone having to parse it.
        status = {"run": run["run"], "model": name, "started_at": now()}
        status_path.write_text(json.dumps(status, ensure_ascii=False) + "\n", encoding="utf-8")
        with part.open("w", encoding="utf-8") as fh:

            for prompt in run["prompts"]:
                for question in run["questions"]:
                    for code, phrases in run["countries"].items():
                        text = prompt["template"].format(
                            country=phrases[prompt["language"]],
                            statement=question["statement"],
                        )
                        inputs = tokenizer.apply_chat_template(
                            [{"role": "user", "content": text}],
                            add_generation_prompt=True,
                            return_tensors="pt",
                            return_dict=True,
                        ).to(model.device)

                        with torch.inference_mode():
                            generated = model.generate(**inputs, **run["params"])

                        answer = tokenizer.decode(
                            generated[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True
                        ).strip()

                        fh.write(json.dumps({
                            "run": run["run"],
                            "id": question["id"],
                            "country": code,
                            "model": name,
                            "prompt": prompt["hash"],
                            "language": prompt["language"],
                            "verdict": verdict(prompt, answer),
                            "answer": answer,
                        }, ensure_ascii=False) + "\n")

                        written += 1

                        if written % PROGRESS == 0 or written == total:
                            done_per_second = written / max(0.001, time.monotonic() - started)
                            left = (total - written) / done_per_second
                            print(
                                f"   {written}/{total} {written / total:.0%}"
                                f"  {done_per_second:.1f}/s  {left / 60:.0f}m left",
                                flush=True,
                            )

        part.rename(out)

        # Completed after the answers: finished_at is what says the file is whole.
        # It stays out of the .jsonl to keep every line in there an answer.
        status_path.write_text(json.dumps({
            **status,
            "answers": written,
            "finished_at": now(),
        }, ensure_ascii=False) + "\n", encoding="utf-8")

        print(f"   wrote {out} in {time.monotonic() - started:.0f}s", flush=True)

        # Free the GPU before the next model is loaded.
        del model, tokenizer
        gc.collect()
        torch.cuda.empty_cache()

    print(f"answers in {answers}")


if __name__ == "__main__":
    main()
