"""OpenReview CLI entry point.

Usage
-----
    python main.py --input examples/sample.yaml
    python main.py --input examples/sample.json
    python main.py --input examples/sample.yaml --config config.yaml
    python main.py --input examples/sample.yaml --provider mock
    python main.py --input examples/sample.yaml --output-dir my_reports/
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import yaml

from src.core.config import AppConfig, load_config
from src.core.models import Project, ReportData
from src.providers.base_provider import AIProvider
from src.providers.mock_provider import MockProvider
from src.providers.openai_provider import OpenAIProvider
from src.report.generator import ReportGenerator
from src.reviewers.business import BusinessReviewer
from src.reviewers.market import MarketReviewer
from src.reviewers.risk import RiskReviewer
from src.reviewers.technology import TechnologyReviewer
from src.reviewers.ux import UXReviewer


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _load_project(input_path: Path) -> Project:
    """Parse YAML or JSON input file into a Project instance."""
    suffix = input_path.suffix.lower()
    if suffix not in {".yaml", ".yml", ".json"}:
        raise ValueError(
            f"Unsupported file format '{suffix}'. Use .yaml, .yml, or .json."
        )

    text = input_path.read_text(encoding="utf-8")
    raw: dict[str, Any]
    if suffix == ".json":
        raw = json.loads(text)
    else:
        raw = yaml.safe_load(text) or {}

    if not isinstance(raw, dict):
        raise ValueError("Input file must contain a YAML/JSON object (dict) at the top level.")

    required_fields = {"title", "description"}
    missing = required_fields - raw.keys()
    if missing:
        raise ValueError(f"Input file is missing required fields: {missing}")

    target_users = raw.get("target_users", [])
    if isinstance(target_users, str):
        target_users = [target_users]

    return Project(
        title=str(raw["title"]),
        description=str(raw["description"]),
        target_users=[str(u) for u in target_users],
        business_model=str(raw.get("business_model", "")),
        raw_data=raw,
    )


def _build_provider(config: AppConfig) -> AIProvider:
    """Instantiate the appropriate AI provider based on config."""
    if config.provider == "openai":
        if not config.openai_api_key:
            logging.getLogger(__name__).warning(
                "provider=openai but no API key found; falling back to MockProvider."
            )
            return MockProvider()
        return OpenAIProvider(
            api_key=config.openai_api_key,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )
    return MockProvider()


def run_review(input_path: Path, config: AppConfig) -> Path:
    """Execute the full review pipeline and return the path to the report.

    Args:
        input_path: Path to the YAML/JSON project input file.
        config: Application configuration.

    Returns:
        Path to the generated Markdown report.
    """
    logger = logging.getLogger(__name__)

    logger.info("Loading project from: %s", input_path)
    project = _load_project(input_path)
    logger.info("Project loaded: '%s'", project.title)

    provider = _build_provider(config)
    logger.info("Using provider: %s", provider)

    reviewers = [
        TechnologyReviewer(provider=provider, prompts_dir=config.prompts_dir),
        BusinessReviewer(provider=provider, prompts_dir=config.prompts_dir),
        MarketReviewer(provider=provider, prompts_dir=config.prompts_dir),
        UXReviewer(provider=provider, prompts_dir=config.prompts_dir),
        RiskReviewer(provider=provider, prompts_dir=config.prompts_dir),
    ]

    report_data = ReportData(project=project)
    for reviewer in reviewers:
        logger.info("Running %s reviewer…", reviewer.reviewer_name)
        result = reviewer.review(project)
        report_data.results.append(result)
        logger.info(
            "  %s — score: %.1f/10", reviewer.reviewer_name, result.score
        )

    logger.info("Overall score: %.2f/10", report_data.overall_score)

    generator = ReportGenerator(output_dir=config.output_dir)
    report_path = generator.generate(report_data)
    logger.info("Report saved: %s", report_path)
    return report_path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="openreview",
        description=(
            "OpenReview — AI-powered multi-expert project review framework.\n"
            "Evaluate your idea or proposal from Technology, Business, Market, UX, and Risk perspectives."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        type=Path,
        metavar="FILE",
        help="Path to the YAML or JSON project input file.",
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=Path("config.yaml"),
        metavar="FILE",
        help="Path to config.yaml (default: config.yaml in current directory).",
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "mock"],
        default=None,
        help="Override the AI provider (ignores config.yaml value).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Directory to write the output report (overrides config.yaml).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.  Returns an exit code (0 = success, 1 = error)."""
    args = _parse_args(argv)
    _setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    if not args.input.exists():
        logger.error("Input file not found: %s", args.input)
        return 1

    config = load_config(args.config)

    if args.provider is not None:
        config.provider = args.provider  # type: ignore[assignment]
    if args.output_dir is not None:
        config.output_dir = args.output_dir

    try:
        report_path = run_review(input_path=args.input, config=config)
    except (ValueError, FileNotFoundError) as exc:
        logger.error("Failed to run review: %s", exc)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        return 1

    print(f"\nReview complete! Report saved to: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
