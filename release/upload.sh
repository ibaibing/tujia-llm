# Release helper — mirrors the tujia-asr layout: GitHub Releases + HF + ModelScope.
#   huggingface-cli login
#   modelscope login --token <your-token>
#   PYPI=1 twine upload dist/*      (set PYPI=1 to print the command only)
set -euo pipefail

ORG="${ORG:-TujiaNLP}"
REPO="${REPO:-tujia-llm-8b-v0.2}"
GGUF_REPO="${GGUF_REPO:-tujia-llm-8b-v0.2-gguf}"
WEIGHTS="${WEIGHTS:-$HOME/workspace/github/your-repos/tujia-llm-lab/adapters/tujia-lora-ipa-qwen3-8b-v02/adapters.safetensors}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="$(mktemp -d)"
GGUF_STAGE="$(mktemp -d)"

# --- MLX adapter repository: four files -------------------------------------
cp "$ROOT/release/adapter_config.json" "$STAGE/adapter_config.json"
cp "$WEIGHTS" "$STAGE/adapters.safetensors"
cp "$ROOT/MODEL_CARD.md" "$STAGE/README.md"
cp "$ROOT/NOTICE" "$STAGE/NOTICE"

tar -czf "$STAGE/${REPO}.tar.gz" -C "$STAGE" \
  adapter_config.json adapters.safetensors README.md NOTICE
( cd "$STAGE" && shasum -a 256 "${REPO}.tar.gz" > SHA256SUMS )

# --- GGUF repository (Windows / Linux / Intel Mac) --------------------------
cp "$ROOT/gguf/tujia-llm-8b-v0.2-Q4_K_M.gguf" "$GGUF_STAGE/"
cp "$ROOT/gguf/Modelfile" "$GGUF_STAGE/"
cp "$ROOT/gguf/SHA256SUMS" "$GGUF_STAGE/"
cp "$ROOT/docs/windows-gguf.md" "$GGUF_STAGE/README.md"
cp "$ROOT/NOTICE" "$GGUF_STAGE/NOTICE"

echo "==> MLX staging: $STAGE"
ls -lh "$STAGE"
echo "==> GGUF staging: $GGUF_STAGE"
ls -lh "$GGUF_STAGE"

echo "==> Hugging Face (adapter)"
huggingface-cli repo create "$ORG/$REPO" --type model -y 2>/dev/null || true
huggingface-cli upload "$ORG/$REPO" "$STAGE" . --commit-message "release v0.2"

echo "==> Hugging Face (GGUF)"
huggingface-cli repo create "$ORG/$GGUF_REPO" --type model -y 2>/dev/null || true
huggingface-cli upload "$ORG/$GGUF_REPO" "$GGUF_STAGE" . --commit-message "release v0.2 gguf"

echo "==> ModelScope"
modelscope upload "$ORG/$REPO" "$STAGE" --commit-message "release v0.2" 2>/dev/null || \
  echo "Create the ModelScope repository first: https://modelscope.cn/models/$ORG/$REPO"
modelscope upload "$ORG/$GGUF_REPO" "$GGUF_STAGE" --commit-message "release v0.2 gguf" 2>/dev/null || \
  echo "Create the ModelScope repository first: https://modelscope.cn/models/$ORG/$GGUF_REPO"

echo "==> GitHub Release"
echo "Attach $STAGE/${REPO}.tar.gz and SHA256SUMS to:"
echo "https://github.com/ibaibing/tujia-llm/releases/new"
echo "GGUF (4.7 GB) exceeds the release asset limit; link to Hugging Face instead."

echo "==> PyPI"
echo "python3.11 -m pip install build twine"
echo "python3.11 -m build"
echo "twine upload dist/*"
