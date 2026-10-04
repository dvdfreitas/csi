#!/bin/bash
# Run the whole run file on the cluster: every model, every country, every question.
#
#   sbatch scripts/run.sbatch
#   sbatch --gres=gpu:H100:2 scripts/run.sbatch    # if the run file holds a 70B+ model
#
# To watch it: keep the id and use tail -F, which waits for the file — the log only
# exists once the job leaves the queue.
#
#   id=$(sbatch --parsable scripts/run.sbatch)
#   squeue -u $USER && tail -F logs/csi-run-$id.out
#
# This cluster's gpu_batch QOS, read from sacctmgr: at most 12h of wall time per
# job, 2 GPUs per job and 2 in use per user at a time, and 10 jobs submitted.
#
# Submit from ~/csi, where scripts/liacc_sync.sh puts everything. Warm the uv cache
# once on the login node first — the compute nodes may have no network:
#
#   uv sync --script scripts/cultural.py

#SBATCH --job-name=csi-run
#SBATCH --account=liacc
#SBATCH --partition=normal
#SBATCH --qos=gpu_batch
# H100 named explicitly, not just "a GPU": the same prompt gives different answers on
# different hardware, so every model in a comparison has to run on the same kind, or
# the difference between models and the difference between GPUs become impossible to
# tell apart.
#SBATCH --gres=gpu:H100:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
# 12h is the QOS ceiling, not a choice: asking for more is refused outright with
# QOSMaxWallDurationPerJobLimit. One job runs every model in the run file in
# sequence, so a run that does not fit has to be split into several run files.
#SBATCH --time=12:00:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.out

set -euo pipefail

cd "$SLURM_SUBMIT_DIR"

# Every path below is relative to the project root, and Slurm starts the job
# wherever it was submitted from — including scripts/, which then looks for
# scripts/scripts/cultural.py and fails with a bare "Failed to spawn".
if [ ! -f scripts/cultural.py ]; then
    echo "Submit from the project root (~/csi), not from $PWD" >&2
    exit 1
fi

# Keep the model weights out of the home quota. sbatch exports the submitting shell's
# environment, so HF_HOME usually arrives already set from ~/.bashrc; this is only the
# fallback when it does not.
export HF_HOME="${HF_HOME:-/data/03/$USER/hf}"

# HF_TOKEN is deliberately NOT set here: it is a credential, it comes from the
# environment, and it must never be committed to this repository.

echo "host: $(hostname) | job: ${SLURM_JOB_ID:-none} | gpus: ${SLURM_GPUS_ON_NODE:-?} | started: $(date -Is)"
echo "HF_HOME=$HF_HOME | token: ${HF_TOKEN:+set}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true

uv run --offline scripts/cultural.py storage/app/private/runs/run.json
