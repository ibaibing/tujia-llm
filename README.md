# tujia-llm

Public release hub for large language models of **Northern Tujia (Longshan Miaoertan standard pronunciation)**.

This repository ships only what can be used directly: LoRA adapters, merged 4-bit
quantized models, inference scripts, prompt templates, and the evaluation protocol.
Training corpora, training code, and experiment logs live in the private
`tujia-llm-lab` repository.

## Positioning

The goal is not "a model that speaks Tujia", but a **usable Tujia assistant**:

- Lexicon lookup: Chinese → Tujia, Tujia → Chinese gloss
- Phonetic annotation: IPA plus Ye DeShu–Peng Xiumo pinyin (1984 scheme)
- Short-sentence translation: greetings and textbook-level example sentences
- Cultural Q&A: answers about Tujia history, customs, and literature **in Chinese**

Explicit non-goals: free-form long Tujia prose, lecturing on history in Tujia, singing synthesis.

## Models

| Version | Base | Training data | Status |
| --- | --- | --- | --- |
| v0.1 | Qwen3-8B-Instruct-2507 | Corpus v0.1 (full OCR + normalized lexicon + sentence pairs) | Planned |
| v0.1-edge | Qwen3-4B-Instruct-2507 | Same (on-device slice) | Planned |
| v0.2 | Same base | Corpus v0.2 (post human review) | Planned |

All versions pin the same base release so that v0.1 and v0.2 metrics stay comparable.

## Quick start

```bash
pip install -r requirements.txt

# LoRA adapter (bring your own base weights)
python infer.py --base Qwen/Qwen3-8B-Instruct-2507 \
                --adapter ./adapters/v0.1 \
                --prompt "Chinese: sun"

# On-device 4-bit (llama.cpp)
./llama-cli -m tujia-llm-v0.1-edge-Q4_K_M.gguf -p "Tujia: muxddi"
```

## Evaluation

Three independent held-out sets, none used in training:

| Set | Size | Purpose |
| --- | --- | --- |
| `llm_gold_lexicon_500` | 500 entries | Lexicon lookup and glossing |
| `llm_gold_single_250` | 250 items | Single-item tasks |
| `llm_gold_sentences_100` | 100 sentences | Tujia–Chinese translation |

Metric definitions, prompt templates, and scoring scripts are in `docs/protocol.md`.

## License

- Code: MIT (third-party components keep their own licenses)
- Model weights: research use only
- No rights to training corpora, recordings, or speaker voices are granted
