# Evaluation — tujia-llm v0.2

Date: 2026-11-11. Frozen sets: `tujia-multimodal-corpus/eval/` (seed 42).

## Evaluation sets

| File | Items | Description |
|---|---|---|
| `llm_gold_lexicon_500.jsonl` | 500 | Multi-source entries, stratified by source |
| `llm_gold_single_250.jsonl` | 250 | Single-sense entries across Longshan, Baojing, Luxi, etc. |
| `llm_gold_sentences_100_ipa.jsonl` | 100 | Sentence pairs (Chinese/Tujia/English); 92 are long narrative sentences |

All gold items are excluded from training by `w_fold` and text hash.

## Main results

| Metric | Base Qwen3-8B | v0.1 (35k, internal) | v0.2 (47k, released) |
|---|---|---|---|
| Lexicon 500, exact | 0%* | 7.2% | 5.8% |
| Lexicon 500, edit similarity | 0.020* | 0.5056 | **0.5112** |
| Lexicon 500, ≥0.8 | — | 16.0% | 14.0% |
| Single-entry 250, exact | — | 2.0% | **2.4%** |
| Single-entry 250, similarity | — | 0.4268 | **0.4486** |
| Sentences 100, whole-sentence decoding | 0.082 | 0.3203 | 0.2999 (320 tokens) |
| Sentences 100, split decoding | — | 0.4233 | **0.4511** |
| Repetition degeneration | — | 39/100 | 25/100 (7/100 with split decoding) |
| Output/reference length ratio | — | 0.91 | 0.94 |

\* Base model evaluated on the first 100 items only.

## Effect of split decoding

The longest completion in the training set is 153 tokens, so the model has never produced
long outputs. Splitting long sentences at punctuation and translating each segment:

| | Whole sentence | Split |
|---|---|---|
| Sentence similarity | 0.3203 | **0.4233** |
| Repetition degeneration | 35/100 | **12/100** |
| Length ratio | 0.74 | **0.92** |

This is why the released inference script supports a split mode.

## Dialect breakdown (single-entry 250)

| Group | Items | v0.1 | v0.2 |
|---|---|---|---|
| Longshan (standard Northern) | 123 | 0.452 | **0.481** |
| Baojing | 60 | 0.393 | 0.428 |
| Luxi (Southern) | 17 | 0.316 | 0.284 |
| Unlabelled | 50 | 0.444 | 0.451 |

The model always emits Longshan forms, so low scores outside that group mostly reflect
variety mismatch rather than incorrect translation.

## Song lyrics (qualitative, not gold)

Reference: 12 lines from 《大家都过好日子》 in `tujia-translation-archive`. Mean similarity 0.583.

| Line | Similarity | Observation |
|---|---|---|
| 土家人们都相好 | 0.83 | Only line directly usable |
| 大家一起过好日子 | 0.74 | Loses `niɛ⁵⁵ ʦʰai³⁵` ("good") |
| 阿妹织土花 / 阿哥把土挖 | 0.74 / 0.67 | Content words correct, verbs guessed |
| 阿哥把犁搬 | 0.61 | `kʰa⁵⁵tʰiɛ⁵⁵ pɤ⁵³` not learned |
| 戴斗笠来蓑衣穿 | 0.29 | Low-frequency nouns drift completely |

Systematic bias: kinship terms always use Chinese loanwords `a²¹ko⁵⁵` / `a⁵³mei³⁵`;
folk-song forms such as `lo⁵⁵pa⁵⁵tiɛ⁵⁵` and `ma²¹ma³⁵tiɛ⁵⁵` are never produced.

## Negative result: dialect-filtered retraining (v0.3)

Retrained from the base model for 25,000 steps after removing Baojing, Xianren, and Luxi
sources (5,902 rows dropped), with all other settings identical. All metrics fell; not released.

| Metric | v0.2 | v0.3 |
|---|---|---|
| Lexicon exact | 5.8% | 1.4% |
| Lexicon similarity | 0.511 | 0.421 |
| Sentence similarity | 0.451 | 0.430 |
| Repetition degeneration | 25/100 | 54/100 |

Only 4.6% of the data was removed but metrics dropped several-fold, indicating the
bottleneck is training-recipe stability and vocabulary coverage, not dialect noise.
The run is retained as a negative result.

## Reproduction

```bash
python3 scripts/eval_lora.py \
  --model Qwen3-8B-bf16 \
  --adapter adapters/tujia-lora-ipa-qwen3-8b-v02 \
  --sent-file llm_gold_sentences_100_ipa.jsonl \
  --split-sent \
  --out logs/eval_release.json
```
