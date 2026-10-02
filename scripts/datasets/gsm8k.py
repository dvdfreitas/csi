"""O GSM8K traz a resposta final depois de '####', precedida do raciocínio."""

import re

from datasets import load_dataset

DATASET = "openai/gsm8k"
DEFAULTS = {"type": "numeric", "language": "en"}

FINAL_ANSWER = re.compile(r"####\s*(.+?)\s*$", re.MULTILINE)


def rows():
    for subdataset in ("main", "socratic"):
        for split in ("train", "test"):
            for row in load_dataset(DATASET, subdataset, split=split):
                final = FINAL_ANSWER.search(row["answer"])

                yield {
                    "subdataset": subdataset,
                    "split": split,
                    "statement": row["question"],
                    "answer": final.group(1).replace(",", ""),
                    "reasoning": FINAL_ANSWER.sub("", row["answer"]).strip(),
                }
