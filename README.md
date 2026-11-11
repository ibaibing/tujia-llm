# tujia-llm

LoRA weights and evaluation for Tujia language generation. First public release: **v0.2** (research preview). v0.1 was internal only.

> **Status: research preview.** Suitable for draft lookup and short-sentence translation, not for
> authoritative output. Exact word-lookup accuracy is 5.8%; sentence similarity is 0.45.
> See [evaluation](docs/eval-v0.2.md) for details.

## Model

| Item | Value |
|---|---|
| Base model | `Qwen/Qwen3-8B` (base, not instruct); MLX conversion `mlx-community/Qwen3-8B-bf16` |
| Method | LoRA, rank 16, 16 layers, scale 32, dropout 0.05 |
| Weight size | 74 MB (`adapters.safetensors`) |
| Training steps | 35,000 + 12,000 continued |
| Target variety | Northern Tujia, Longshan standard |
| License | Research use only; see [NOTICE](NOTICE) |

## Download

| Channel | Location |
|---|---|
| ModelScope (MLX) | [TujiaNLP/tujia-llm-8b-v0.2](https://modelscope.cn/models/TujiaNLP/tujia-llm-8b-v0.2) |
| ModelScope (GGUF) | [TujiaNLP/tujia-llm-8b-v0.2-gguf](https://modelscope.cn/models/TujiaNLP/tujia-llm-8b-v0.2-gguf) |
| Hugging Face | [MLX adapter](https://huggingface.co/TujiaNLP/tujia-llm-8b-v0.2) · [GGUF shards](https://huggingface.co/TujiaNLP/tujia-llm-8b-v0.2-gguf) |
| GitHub Releases | `github.com/ibaibing/tujia-llm/releases` → `tujia-llm-8b-v0.2.tar.gz` |
| PyPI | `pip install tujia-llm` (Apple Silicon) |

## Install

**Requirements:** macOS 13+, Apple Silicon, Python 3.10+.

| Memory | Flag | Download | Notes |
|---|---|---|---|
| 32 GB+ | default (`bf16`) | ~15 GB | Reference quality |
| 16 GB | `--precision 4bit` | ~4.5 GB | Runs, but output degrades visibly (repetition, tone errors) |

```bash
pip install tujia-llm                          # after the PyPI release
pip install dist/tujia_llm-0.2.0-py3-none-any.whl   # offline / local wheel
```

The wheel contains code only. Weights (74 MB) and the base model are downloaded on first run.

## CLI

```bash
tujia-llm info                                  # backend, precision, memory
tujia-llm lookup 酒
tujia-llm translate "大家都过好日子。"
tujia-llm translate "大家都过好日子，土家人们都相好。" --split
tujia-llm translate "zɤ³⁵" --to zh
tujia-llm translate "zɤ³⁵" --to en
```

Options: `--adapter` (local directory or HF repo id), `--precision auto|bf16|4bit`,
`--max-tokens`, `--json`.

```bash
tujia-llm lookup 酒 --adapter /path/to/adapter-dir --json
```

For development, `python scripts/infer.py` offers the same prompts without installation.

## Windows / CPU (GGUF)

The MLX build is Apple Silicon only. For Windows, Linux, and Intel Macs use the GGUF build
with llama.cpp or Ollama — see [docs/windows-gguf.md](docs/windows-gguf.md).

| File | Size | Memory |
|---|---|---|
| `gguf/tujia-llm-8b-v0.2-Q4_K_M.gguf` | 4.7 GB | 16 GB+ |
| `gguf/tujia-llm-8b-v0.2-f16.gguf` | 15 GB | 20 GB+ |

```powershell
ollama create tujia -f gguf/Modelfile
ollama run tujia "「酒」用土家语怎么说？"
```

## Capabilities and limits

**Works**

- Chinese word → Tujia form + IPA (reliable for high-frequency words)
- Chinese short sentence → Tujia sentence (stable up to roughly 8 syllables)
- Tujia sentence → English

**Does not work**

- Authoritative translation, publication-grade text, legal or medical use
- Folk songs, ritual language, and other low-resource registers
- Southern Tujia (Luxi) and non-Longshan varieties such as Baojing
- Out-of-vocabulary words: there is no refusal mechanism, so the model will invent forms

## Evaluation summary

| Metric | Base | v0.2 |
|---|---|---|
| Lexicon 500, first-candidate exact | 0% | 5.8% |
| Lexicon 500, edit similarity | 0.020* | 0.511 |
| Single-entry 250, similarity | 0.024* | 0.449 |
| Sentences 100, similarity (split decoding) | 0.082 | 0.451 |
| Song lyrics, 12 lines, similarity | — | 0.583 |

\* Base model evaluated on the first 100 items only, so not directly comparable to the full sets.

Full tables, dialect breakdowns, and failure modes: [docs/eval-v0.2.md](docs/eval-v0.2.md).

## Prompt format

The model was trained on four fixed templates. Keep them unchanged at inference time:

```
「{Chinese word}」用土家语怎么说？
把这句话翻译成土家语：{Chinese sentence}
把这句话翻译成汉语：{Tujia sentence}
把这句话翻译成英语：{Tujia sentence}
```

Output uses mixed Ye pinyin / IPA notation with superscript tone digits, e.g. `zɤ³⁵`.

## Layout

```
scripts/infer.py        inference example
docs/eval-v0.2.md       evaluation report
release/                release config and upload script
MODEL_CARD.md           model card
NOTICE                  usage boundaries
```

## Citation

```bibtex
@misc{tujia-llm-v0.1,
  title  = {tujia-llm: LoRA adapter for Tujia language generation (v0.2)},
  author = {ibaibing},
  year   = {2026},
  note   = {Research preview}
}
```
