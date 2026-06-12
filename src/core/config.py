"""Configuration loader for OpenReview."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml


ProviderType = Literal["openai", "mock"]


@dataclass
class AppConfig:
    """Application-level configuration.

    Attributes:
        provider: Which AI provider to use ("openai" or "mock").
        model: The LLM model identifier to request.
        output_dir: Directory where generated reports are saved.
        prompts_dir: Directory containing prompt template files.
        openai_api_key: Optional API key; falls back to OPENAI_API_KEY env var.
        temperature: Sampling temperature for the LLM.
        max_tokens: Maximum tokens in each LLM response.
    """

    provider: ProviderType = "mock"
    model: str = "gpt-4.1"
    output_dir: Path = field(default_factory=lambda: Path("reports"))
    prompts_dir: Path = field(default_factory=lambda: Path("prompts"))
    openai_api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir)
        self.prompts_dir = Path(self.prompts_dir)
        if not self.openai_api_key:
            self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")


def load_config(config_path: Path | str = "config.yaml") -> AppConfig:
    """Load configuration from a YAML file.

    Missing keys fall back to ``AppConfig`` defaults.  If the file is absent
    the defaults are returned without raising an error.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Populated ``AppConfig`` instance.
    """
    path = Path(config_path)
    if not path.exists():
        return AppConfig()

    with path.open(encoding="utf-8") as fh:
        raw: dict = yaml.safe_load(fh) or {}

    provider_raw = raw.get("provider", "mock")
    provider: ProviderType = (
        "openai" if str(provider_raw).lower() == "openai" else "mock"
    )

    output_dir_raw = raw.get("output", "reports")
    # Support both "output" and "output_dir" keys
    if isinstance(output_dir_raw, str):
        output_dir = Path(output_dir_raw)
    else:
        output_dir = Path("reports")

    prompts_dir_raw = raw.get("prompts_dir", "prompts")

    return AppConfig(
        provider=provider,
        model=raw.get("model", "gpt-4.1"),
        output_dir=output_dir,
        prompts_dir=Path(prompts_dir_raw),
        openai_api_key=raw.get("openai_api_key", ""),
        temperature=float(raw.get("temperature", 0.7)),
        max_tokens=int(raw.get("max_tokens", 1024)),
    )
