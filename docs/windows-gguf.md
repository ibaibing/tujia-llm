---
license: other
license_name: research-preview
license_link: https://github.com/ibaibing/tujia-llm/blob/main/NOTICE
base_model: Qwen/Qwen3-8B
library_name: llama.cpp
pipeline_tag: text-generation
language:
  - zh
  - en
tags:
  - tujia
  - low-resource
  - gguf
---

# Windows / CPU usage (GGUF)

The MLX build only runs on Apple Silicon. This GGUF build runs on Windows, Linux, and
Intel Macs through llama.cpp or Ollama.

**Weights:** this repository hosts the five llama.cpp shards (~1 GB each). ModelScope also
carries the single 4.7 GB file:
[ModelScope · TujiaNLP/tujia-llm-8b-v0.2-gguf](https://modelscope.cn/models/TujiaNLP/tujia-llm-8b-v0.2-gguf).

## Files

| File | Size | Notes |
|---|---|---|
| `tujia-llm-8b-v0.2-Q4_K_M-00001-of-00005.gguf` … `-00005-of-00005.gguf` | 5 × ~1 GB | llama.cpp split shards; keep all five in one directory |
| `tujia-llm-8b-v0.2-Q4_K_M.gguf` | 4.7 GB | Single file (ModelScope only) |
| `tujia-llm-8b-v0.2-f16.gguf` | 15 GB | Reference precision, needs ~20 GB RAM |

For llama.cpp, point `-m` at the **first** shard; the remaining four are opened automatically:

```powershell
llama-completion.exe -m tujia-llm-8b-v0.2-Q4_K_M-00001-of-00005.gguf -p "<prompt>" -n 64 -no-cnv
```

Ollama does not always follow split shards. Either download the single 4.7 GB file from
ModelScope, or merge locally:

```powershell
llama-gguf-split --merge tujia-llm-8b-v0.2-Q4_K_M-00001-of-00005.gguf tujia-llm-8b-v0.2-Q4_K_M.gguf
```

Requires 16 GB RAM or more for Q4 (32 GB is comfortable).

## Option A: Ollama

```powershell
# 1. Install Ollama for Windows: https://ollama.com/download
# 2. Put Modelfile and the .gguf file in the same directory
ollama create tujia -f Modelfile
ollama run tujia "「酒」用土家语怎么说？"
```

## Option B: llama.cpp

```powershell
# Download a Windows build from https://github.com/ggml-org/llama.cpp/releases
llama-completion.exe -m tujia-llm-8b-v0.2-Q4_K_M.gguf -p "<prompt>" -n 64 --temp 0 -no-cnv
```

## Prompt format

The model was trained on four fixed templates:

```
「{Chinese word}」用土家语怎么说？
把这句话翻译成土家语：{Chinese sentence}
把这句话翻译成汉语：{Tujia sentence}
把这句话翻译成英语：{Tujia sentence}
```

It was also trained with an **empty, already-closed think block**. If you supply the prompt
manually instead of using the bundled `Modelfile`, render it exactly like this (`␊` marks a
newline):

```
<|im_start|>user␊
「酒」用土家语怎么说？<|im_end|>␊
<|im_start|>assistant␊
<think>␊
␊
</think>␊
␊
```

Without the closed think block, Ollama displays a thinking section and output quality drops.

## Verified behaviour

| Test | Result |
|---|---|
| `「酒」用土家语怎么说？` | `zɤ³⁵；zɤ³⁵` (identical to the bf16 MLX build) |
| `把这句话翻译成土家语：大家都过好日子。` | `xu³⁵ ni⁵⁵ niɛ⁵⁵ kʰa⁵⁵ ɕi⁵⁵ tsʰa³⁵` |
| `「谢谢」用土家语怎么说？` | `aŋ²¹tsai⁵⁵；aŋ²¹tsai³⁵` |
| Speed, Apple M2 Ultra, Metal | 12.8 tok/s (prompt 159 tok/s) |
| Speed, Apple M2 Ultra, CPU only (`-ngl 0`) | 27.4 tok/s (prompt 57.6 tok/s) |
| Windows 11, 32 GB RAM, no GPU, Ollama | **Passed** (2026-11-11, CPU-only) |

Windows CPU speed is typically 4–8 tok/s for an 8B Q4 model; a recent GPU or Ollama with
CUDA/Vulkan is faster.

## Quality

Q4_K_M keeps the same output as bf16 in the samples above, but quantization can increase
repetition on long sentences. Treat it as a preview build: the research-preview caveats in
the model card apply.
