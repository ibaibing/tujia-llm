# Release helper — mirrors the tujia-asr layout: GitHub Releases + HF + ModelScope.
#   huggingface-cli login
#   modelscope login --token <your-token>
#   PYPI=1 twine upload dist/*      (set PYPI=1 to print the command only)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

ORG="${ORG:-TujiaNLP}"
REPO="${REPO:-tujia-llm-8b-v0.2}"
GGUF_REPO="${GGUF_REPO:-tujia-llm-8b-v0.2-gguf}"
WEIGHTS="${WEIGHTS:-$HOME/workspace/github/your-repos/tujia-llm-lab/adapters/tujia-lora-ipa-qwen3-8b-v02/adapters.safetensors}"
SHARDS_DIR="${SHARDS_DIR:-/tmp/gguf-lfs}"          # llama-gguf-split output
SINGLE_GGUF="${SINGLE_GGUF:-$ROOT/gguf/tujia-llm-8b-v0.2-Q4_K_M.gguf}"

STAGE="$(mktemp -d)"
GGUF_HF="$(mktemp -d)"
GGUF_MS="$(mktemp -d)"

# --- MLX adapter repository: four files -------------------------------------
cp "$ROOT/release/adapter_config.json" "$STAGE/adapter_config.json"
cp "$WEIGHTS" "$STAGE/adapters.safetensors"
cp "$ROOT/MODEL_CARD.md" "$STAGE/README.md"
cp "$ROOT/NOTICE" "$STAGE/NOTICE"

tar -czf "$STAGE/${REPO}.tar.gz" -C "$STAGE" \
  adapter_config.json adapters.safetensors README.md NOTICE
( cd "$STAGE" && shasum -a 256 "${REPO}.tar.gz" > SHA256SUMS )

# --- GGUF: Hugging Face gets llama.cpp shards, ModelScope the single file ----
cp "$SHARDS_DIR"/*.gguf "$GGUF_HF/"
cp "$ROOT/gguf/Modelfile" "$GGUF_HF/"
cp "$ROOT/gguf/SHA256SUMS" "$GGUF_HF/"
cp "$ROOT/docs/windows-gguf.md" "$GGUF_HF/README.md"
cp "$ROOT/NOTICE" "$GGUF_HF/NOTICE"

cp "$SINGLE_GGUF" "$GGUF_MS/"
cp "$ROOT/gguf/Modelfile" "$GGUF_MS/"
cp "$ROOT/gguf/SHA256SUMS" "$GGUF_MS/"
cp "$ROOT/docs/windows-gguf.md" "$GGUF_MS/README.md"
cp "$ROOT/NOTICE" "$GGUF_MS/NOTICE"

echo "==> adapter staging: $STAGE"
ls -lh "$STAGE"
echo "==> GGUF staging (HF, shards): $GGUF_HF"
ls -lh "$GGUF_HF"
echo "==> GGUF staging (ModelScope, single): $GGUF_MS"
ls -lh "$GGUF_MS"

echo "==> Hugging Face (adapter)"
huggingface-cli repo create "$ORG/$REPO" --type model -y 2>/dev/null || true
huggingface-cli upload "$ORG/$REPO" "$STAGE" . --commit-message "release v0.2"

echo "==> Hugging Face (GGUF shards)"
huggingface-cli repo create "$ORG/$GGUF_REPO" --type model -y 2>/dev/null || true
huggingface-cli upload "$ORG/$GGUF_REPO" "$GGUF_HF" . --commit-message "release v0.2 gguf shards"

echo "==> ModelScope"
modelscope upload "$ORG/$REPO" "$STAGE" --commit-message "release v0.2" 2>/dev/null || \
  echo "Create the ModelScope repository first: https://modelscope.cn/models/$ORG/$REPO"
modelscope upload "$ORG/$GGUF_REPO" "$GGUF_MS" --commit-message "release v0.2 gguf" 2>/dev/null || \
  echo "Create the ModelScope repository first: https://modelscope.cn/models/$ORG/$GGUF_REPO"

echo "==> GitHub Release"
echo "Attach $STAGE/${REPO}.tar.gz and SHA256SUMS to:"
echo "https://github.com/ibaibing/tujia-llm/releases/new"

echo "==> PyPI"
echo "python3.11 -m pip install build twine"
echo "python3.11 -m build"
echo "twine upload dist/*"
