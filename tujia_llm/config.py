"""Configuration and local environment helpers."""

import os
import subprocess
import sys
from dataclasses import dataclass

DEFAULT_REPO = "TujiaNLP/tujia-llm-8b-v0.2"
BASE_BF16 = "mlx-community/Qwen3-8B-bf16"
BASE_4BIT = "mlx-community/Qwen3-8B-4bit"

# Prompt templates must match training exactly.
TPL_LOOKUP = "「{zh}」用土家语怎么说？"
TPL_ZH2TJ = "把这句话翻译成土家语：{text}"
TPL_TJ2ZH = "把这句话翻译成汉语：{text}"
TPL_TJ2EN = "把这句话翻译成英语：{text}"


@dataclass
class Settings:
    repo: str
    base: str
    precision: str
    ram_gb: float


def total_ram_gb() -> float:
    """Best-effort physical memory size in GiB."""
    if sys.platform == "darwin":
        try:
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            return int(out.strip()) / 2**30
        except Exception:
            pass
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        size = os.sysconf("SC_PAGE_SIZE")
        return pages * size / 2**30
    except Exception:
        return 0.0


def pick_precision(requested: str) -> str:
    if requested in ("bf16", "4bit"):
        return requested
    # 8B bf16 needs roughly 16 GB for weights plus KV cache.
    return "bf16" if total_ram_gb() >= 32 else "4bit"


def base_model(precision: str) -> str:
    return BASE_BF16 if precision == "bf16" else BASE_4BIT


def settings(precision: str = "auto", repo: str = DEFAULT_REPO) -> Settings:
    p = pick_precision(precision)
    return Settings(repo=repo, base=base_model(p), precision=p, ram_gb=round(total_ram_gb(), 1))


def require_mlx() -> None:
    if sys.platform != "darwin" or os.uname().machine != "arm64":
        raise SystemExit(
            "This build requires Apple Silicon (macOS arm64) because the adapter is in MLX "
            "format. On other platforms, use the GGUF build with llama.cpp or Ollama "
            "(see the README)."
        )
