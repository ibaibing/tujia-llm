---
license: other
license_name: research-preview
license_link: https://github.com/ibaibing/tujia-llm/blob/main/NOTICE
base_model: Qwen/Qwen3-8B
library_name: mlx
pipeline_tag: text-generation
language:
  - zh
  - en
tags:
  - tujia
  - low-resource
  - lora
  - mlx
---

# Model Card — tujia-llm v0.2

## Overview

`tujia-llm-8b-v0.2` is the first public release of a Tujia language generation model,
released as a LoRA adapter. The release is a **research preview**: it establishes
availability, not translation quality. The base model is **`Qwen/Qwen3-8B` (base version)**; training
and inference use its MLX conversion, `mlx-community/Qwen3-8B-bf16`. The base is not an
instruct model, so all instruction-following behaviour comes from this adapter's SFT.

The model covers Chinese↔Tujia (Northern dialect, Longshan standard) word lookup and
short-sentence translation, plus Tujia→English.

**This is a research preview intended to establish availability, not translation quality.**

## Training

| Item | Value |
|---|---|
| Base | Qwen/Qwen3-8B (base, bf16; MLX: mlx-community/Qwen3-8B-bf16) |
| Fine-tuning | LoRA, rank 16, 16 layers, scale 32, dropout 0.05 |
| Steps | 35,000 (v0.1) + 12,000 (continued) |
| Batch size / sequence length | 4 / 512 (continued stage) |
| Learning rate | 2e-5, then 1e-5 |
| Final validation loss | 0.918 |
| Training samples | 236,316 instruction samples |

Data composition (all internal; not distributed with the weights):

| Type | Rows |
|---|---|
| Dictionary and entry tasks | ~128,000 |
| Dictionary examples and collocations | ~25,000 |
| Chinese–Tujia parallel pairs | ~64,000 (both directions) |
| Sentence-segmentation samples | 3,769 |
| Collocation-weighted samples | 10,221 |

Training text carries **Ye pinyin (ASCII)**; IPA is emitted as an output field so the
tokenizer does not split phonetic symbols.

## Evaluation

Gold sets are frozen (`eval/manifest.json`, seed 42) and excluded from training by
text hash.

| Metric | Base | v0.2 |
|---|---|---|
| Lexicon 500, first-candidate exact | 0% | 5.8% |
| Lexicon 500, edit similarity | 0.020* | 0.511 |
| Lexicon 500, similarity ≥0.8 | — | 14.0% |
| Single-entry 250, exact | 0% | 2.4% |
| Single-entry 250, similarity | 0.024* | 0.449 |
| Sentences 100, similarity (split decoding) | 0.082 | 0.451 |
| Sentences 100, repetition degeneration | — | 7/100 |
| Song lyrics, 12 lines, similarity | — | 0.583 |

\* Base model evaluated on the first 100 items only.

Dialect breakdown on the single-entry set: Longshan (123 items) 0.481, Baojing (60) 0.428,
Luxi (17) 0.284. The model always emits Longshan forms, so non-Longshan items measure
variety mismatch rather than translation error.

## Intended use

**Suitable for**

- Assisted annotation and candidate generation in linguistic research
- Translation drafts in prototypes
- Cross-checking during lexicography (human confirmation required)

**Not suitable for**

- Publication, educational materials, or official documents without review
- Medical, legal, or public-safety contexts
- Folk songs, ritual language, poetry, and other low-resource registers
- Southern Tujia (Luxi) or non-standard varieties such as Baojing

## Known limitations

1. **Exact lookup is only 5.8%.** The model often emits multiple candidates
   (e.g. `zɤ⁵³；zɤ⁵⁵`) and tone values (53/55) vary. Counting any candidate as a hit
   raises accuracy to about 16%.
2. **Sentence similarity is 0.45.** Long sentences lose their second half;
   35% of samples showed repetition degeneration before split decoding, 7% after.
3. **Uneven vocabulary coverage.** High-frequency and monosyllabic words are reliable;
   low-frequency concrete nouns (斗笠 "bamboo hat", 蓑衣 "straw rain cape") are invented.
4. **No refusal mechanism.** Out-of-vocabulary words produce syllables that are not in any lexicon.
5. **Loanword bias.** Kinship terms default to Chinese loanwords (`a²¹ko⁵⁵` for 阿哥)
   rather than folk-song forms (`lo⁵⁵pa⁵⁵tiɛ⁵⁵` for 倮巴爹).
6. **Single variety.** Only Longshan standard is covered; no dialect selection or detection.

## Data and licensing

- All training corpora are `license=internal-only` and are **not distributed** here.
- Weights are research-use only under [NOTICE](../NOTICE); the base model retains its
  original license (Apache-2.0) and attribution requirements.
- Speaker consent (`voice_consent`) has not been confirmed per source. Any commercial
  use or redistribution requires a full rights review.
- This repository contains no dictionary data; retrieval must be supplied by the user.

## Ethics and community

Tujia is an endangered language. Model output may contain incorrect phonetic
transcriptions. If used in teaching or community material, outputs should be reviewed by
native speakers or linguists. Consultation with Tujia communities is recommended before
publishing derivatives.

## Version history

Release numbers match internal training versions.

| Version | Steps | Notes |
|---|---|---|
| v0.1 | 35,000 | Internal only |
| v0.2 | 35,000 + 12,000 continued | First public release |
| v0.3 | 25,000, dialect-filtered | Negative result; all metrics below v0.2, not released |
