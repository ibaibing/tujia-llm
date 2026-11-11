"""MLX inference backend."""

import re
from pathlib import Path


class MlxBackend:
    def __init__(self, base: str, adapter: str, max_tokens: int = 96):
        from mlx_lm import generate, load

        self._generate = generate
        self.max_tokens = max_tokens
        self.model, self.tok = load(base, adapter_path=adapter)

    def ask(self, prompt: str, max_tokens: int | None = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        templated = self.tok.apply_chat_template(
            messages, add_generation_prompt=True, enable_thinking=False
        )
        out = self._generate(
            self.model,
            self.tok,
            prompt=templated,
            max_tokens=max_tokens or self.max_tokens,
            verbose=False,
        )
        return re.sub(r"^.*?</think>", "", out, flags=re.S).strip()


def resolve_adapter(spec: str | None, default_repo: str) -> str:
    """Accept a local directory, a local file, or a Hugging Face repo id.

    Cached snapshots are preferred so repeated runs work offline.
    """
    from huggingface_hub import snapshot_download

    if spec:
        p = Path(spec).expanduser()
        if p.exists():
            return str(p)

    repo = spec or default_repo
    kwargs = dict(repo_id=repo, allow_patterns=["*.safetensors", "*.json"])
    try:
        return snapshot_download(local_files_only=True, **kwargs)
    except Exception:
        return snapshot_download(**kwargs)
