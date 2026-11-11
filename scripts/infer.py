# -*- coding: utf-8 -*-
"""Inference example for tujia-llm (MLX / Apple Silicon).

Usage:
  python scripts/infer.py --prompt "「酒」用土家语怎么说？"
  python scripts/infer.py --adapter TujiaNLP/tujia-llm-8b-v0.2 --prompt "把这句话翻译成土家语：大家都过好日子。"
  python scripts/infer.py --file prompts.txt
"""
import argparse
import re
from pathlib import Path


def resolve_adapter(spec: str) -> str:
    """Use a local directory as-is; otherwise treat it as a Hugging Face repo id."""
    p = Path(spec).expanduser()
    if p.exists():
        return str(p)
    from huggingface_hub import snapshot_download

    return snapshot_download(repo_id=spec, allow_patterns=["*.safetensors", "*.json"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="mlx-community/Qwen3-8B-bf16")
    ap.add_argument("--adapter", default="TujiaNLP/tujia-llm-8b-v0.2",
                    help="local directory or Hugging Face repo id")
    ap.add_argument("--prompt", default="")
    ap.add_argument("--file", default="", help="one prompt per line")
    ap.add_argument("--max-tokens", type=int, default=96)
    ap.add_argument("--split", action="store_true",
                    help="split long sentences at punctuation, translate segments, then join")
    a = ap.parse_args()

    from mlx_lm import generate, load

    model, tok = load(a.base, adapter_path=resolve_adapter(a.adapter))

    def ask(q, n=None):
        msgs = [{"role": "user", "content": q}]
        prompt = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                        enable_thinking=False)
        out = generate(model, tok, prompt=prompt,
                       max_tokens=n or a.max_tokens, verbose=False)
        return re.sub(r"^.*?</think>", "", out, flags=re.S).strip()

    def translate(zh):
        if not a.split or len(zh) <= 18:
            return ask(f"把这句话翻译成土家语：{zh}")
        parts = [x for x in re.split(r"(?<=[，。！？；])", zh) if x.strip()]
        return " ".join(ask(f"把这句话翻译成土家语：{p}") for p in parts)

    if a.file:
        for line in open(a.file, encoding="utf-8"):
            line = line.strip()
            if line:
                print(f"{line}\t{translate(line)}")
    elif a.prompt:
        print(translate(a.prompt))
    else:
        ap.error("either --prompt or --file is required")


if __name__ == "__main__":
    main()
