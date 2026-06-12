"""Markdown report generator for OpenReview."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from src.core.models import ReportData, ReviewResult


logger = logging.getLogger(__name__)

_SCORE_EMOJI = {
    (0.0, 4.0): "🔴",
    (4.0, 6.0): "🟡",
    (6.0, 8.0): "🟢",
    (8.0, 10.01): "⭐",
}

_REPORT_FILENAME = "output.md"


def _score_emoji(score: float) -> str:
    for (lo, hi), emoji in _SCORE_EMOJI.items():
        if lo <= score < hi:
            return emoji
    return "⭐"


def _score_bar(score: float, width: int = 20) -> str:
    """Return a simple ASCII progress bar for the given score."""
    filled = round((score / 10.0) * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {score:.1f}/10"


class ReportGenerator:
    """Generates a Markdown report from aggregated review results.

    Args:
        output_dir: Directory where the report file will be written.
    """

    def __init__(self, output_dir: Path = Path("reports")) -> None:
        self._output_dir = Path(output_dir)

    def generate(self, report_data: ReportData, filename: str = _REPORT_FILENAME) -> Path:
        """Build and save the Markdown report.

        Args:
            report_data: Aggregated project and review data.
            filename: Name of the output file inside ``output_dir``.

        Returns:
            The :class:`~pathlib.Path` of the written report file.
        """
        self._output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._output_dir / filename
        content = self._render(report_data)
        output_path.write_text(content, encoding="utf-8")
        logger.info("Report saved to %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _render(self, data: ReportData) -> str:
        sections: list[str] = [
            self._render_header(data),
            self._render_overall_score(data),
            self._render_score_table(data),
        ]
        for result in data.results:
            sections.append(self._render_reviewer_section(result))
        sections.append(self._render_recommendations(data))
        sections.append(self._render_footer())
        return "\n\n---\n\n".join(sections)

    @staticmethod
    def _render_header(data: ReportData) -> str:
        now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return (
            f"# OpenReview Report\n\n"
            f"**Project:** {data.project.title}  \n"
            f"**Generated:** {now}  \n"
            f"**Reviewers:** {len(data.results)}"
        )

    @staticmethod
    def _render_overall_score(data: ReportData) -> str:
        score = data.overall_score
        emoji = _score_emoji(score)
        bar = _score_bar(score)
        return (
            f"## Overall Score {emoji}\n\n"
            f"```\n{bar}\n```\n\n"
            f"> **{score:.1f} / 10** — averaged across {len(data.results)} reviewers."
        )

    @staticmethod
    def _render_score_table(data: ReportData) -> str:
        rows = ["## Score Summary\n", "| Reviewer | Score | Rating |", "|----------|-------|--------|"]
        for result in data.results:
            emoji = _score_emoji(result.score)
            rows.append(f"| {result.reviewer_name} | {result.score:.1f} | {emoji} |")
        rows.append(f"| **Overall** | **{data.overall_score:.1f}** | {_score_emoji(data.overall_score)} |")
        return "\n".join(rows)

    @staticmethod
    def _render_reviewer_section(result: ReviewResult) -> str:
        emoji = _score_emoji(result.score)
        bar = _score_bar(result.score)
        lines = [
            f"## {result.reviewer_name} Review {emoji}\n",
            f"```\n{bar}\n```\n",
            f"### Summary\n\n{result.summary}\n",
        ]
        if result.strengths:
            lines.append("### Strengths\n")
            for item in result.strengths:
                lines.append(f"- ✅ {item}")
            lines.append("")
        if result.weaknesses:
            lines.append("### Weaknesses\n")
            for item in result.weaknesses:
                lines.append(f"- ⚠️ {item}")
            lines.append("")
        if result.recommendations:
            lines.append("### Recommendations\n")
            for i, item in enumerate(result.recommendations, start=1):
                lines.append(f"{i}. {item}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _render_recommendations(data: ReportData) -> str:
        all_recs = data.all_recommendations
        if not all_recs:
            return "## Key Recommendations\n\n_No recommendations were generated._"
        lines = ["## Key Recommendations\n"]
        for i, rec in enumerate(all_recs, start=1):
            lines.append(f"{i}. {rec}")
        return "\n".join(lines)

    @staticmethod
    def _render_footer() -> str:
        return (
            "_Generated by [OpenReview](https://github.com/corykim2/OpenReview) — "
            "An open-source AI framework for structured project reviews._"
        )
