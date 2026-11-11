"""Command-line interface."""

import argparse
import json
import os
import re
import sys

from . import __version__
from .config import (
    DEFAULT_REPO,
    TPL_LOOKUP,
    TPL_TJ2EN,
    TPL_TJ2ZH,
    TPL_ZH2TJ,
    require_mlx,
    settings,
)


def _common() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--adapter", default=argparse.SUPPRESS,
                   help="local adapter directory/file, or a Hugging Face repo id")
    p.add_argument("--precision", choices=["auto", "bf16", "4bit"], default=argparse.SUPPRESS,
                   help="auto picks bf16 on machines with 32 GB or more")
    p.add_argument("--max-tokens", type=int, default=argparse.SUPPRESS)
    p.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                   help="machine-readable output")
    return p


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tujia-llm",
        description="Tujia language generation (research preview).",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    common = _common()
    sub = p.add_subparsers(dest="cmd", required=True)

    lk = sub.add_parser("lookup", parents=[common], help="Chinese word to Tujia form")
    lk.add_argument("word")

    tr = sub.add_parser("translate", parents=[common], help="translate a sentence")
    tr.add_argument("text")
    tr.add_argument("--to", choices=["tj", "zh", "en"], default="tj",
                    help="target language: tj (Tujia), zh (Chinese), en (English)")
    tr.add_argument("--split", action="store_true",
                    help="split long Chinese sentences at punctuation before translating")

    sub.add_parser("info", parents=[common], help="show backend and model settings")
    return p


def _split_zh(text: str) -> list[str]:
    return [x for x in re.split(r"(?<=[，。！？；])", text) if x.strip()]


def run(args) -> dict:
    precision = getattr(args, "precision", "auto")
    max_tokens = getattr(args, "max_tokens", 96)
    adapter = getattr(args, "adapter", "") or os.environ.get("TUJIA_LLM_ADAPTER", "")

    cfg = settings(precision, DEFAULT_REPO)

    if args.cmd == "info":
        return {
            "version": __version__,
            "base": cfg.base,
            "precision": cfg.precision,
            "ram_gb": cfg.ram_gb,
            "adapter": adapter or cfg.repo,
            "platform": f"{sys.platform}/{os.uname().machine}",
        }

    require_mlx()
    from .backend_mlx import MlxBackend, resolve_adapter

    backend = MlxBackend(cfg.base, resolve_adapter(adapter or None, cfg.repo),
                         max_tokens=max_tokens)

    if args.cmd == "lookup":
        prompt = TPL_LOOKUP.format(zh=args.word)
        return {"input": args.word, "output": backend.ask(prompt)}

    tpl = {"tj": TPL_ZH2TJ, "zh": TPL_TJ2ZH, "en": TPL_TJ2EN}[args.to]
    if args.to == "tj" and args.split and len(args.text) > 18:
        parts = [backend.ask(tpl.format(text=s), 64) for s in _split_zh(args.text)]
        return {"input": args.text, "output": " ".join(parts), "split": len(parts)}

    return {"input": args.text, "output": backend.ask(tpl.format(text=args.text))}


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    result = run(args)
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(result.get("output", result))
