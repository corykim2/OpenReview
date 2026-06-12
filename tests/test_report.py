"""Tests for the report generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.models import Project, ReportData, ReviewResult
from src.report.generator import ReportGenerator, _score_bar, _score_emoji


# ---------------------------------------------------------------------------
# Score helper functions
# ---------------------------------------------------------------------------


class TestScoreHelpers:
    def test_score_emoji_red_for_low_score(self) -> None:
        assert _score_emoji(2.0) == "🔴"

    def test_score_emoji_yellow_for_mid_score(self) -> None:
        assert _score_emoji(5.0) == "🟡"

    def test_score_emoji_green_for_good_score(self) -> None:
        assert _score_emoji(7.0) == "🟢"

    def test_score_emoji_star_for_excellent_score(self) -> None:
        assert _score_emoji(9.0) == "⭐"

    def test_score_bar_contains_score(self) -> None:
        bar = _score_bar(7.5)
        assert "7.5/10" in bar

    def test_score_bar_width(self) -> None:
        bar = _score_bar(5.0, width=10)
        # 5/10 * 10 = 5 filled, 5 empty
        assert "█████░░░░░" in bar

    def test_score_bar_full(self) -> None:
        bar = _score_bar(10.0, width=10)
        assert "░" not in bar

    def test_score_bar_empty(self) -> None:
        bar = _score_bar(0.0, width=10)
        assert "█" not in bar


# ---------------------------------------------------------------------------
# ReportData model
# ---------------------------------------------------------------------------


class TestReportData:
    def test_overall_score_average(self, all_review_results: list[ReviewResult], full_project: Project) -> None:
        data = ReportData(project=full_project, results=all_review_results)
        expected = round((7.5 + 6.8 + 7.2 + 6.5 + 5.9) / 5, 2)
        assert data.overall_score == expected

    def test_overall_score_zero_for_no_results(self, full_project: Project) -> None:
        data = ReportData(project=full_project, results=[])
        assert data.overall_score == 0.0

    def test_all_recommendations_deduplicated(self, full_project: Project) -> None:
        shared_rec = "Shared recommendation"
        results = [
            ReviewResult(
                reviewer_name="A",
                score=7.0,
                summary="s",
                recommendations=[shared_rec, "Only in A"],
            ),
            ReviewResult(
                reviewer_name="B",
                score=7.0,
                summary="s",
                recommendations=[shared_rec, "Only in B"],
            ),
        ]
        data = ReportData(project=full_project, results=results)
        recs = data.all_recommendations
        assert recs.count(shared_rec) == 1
        assert "Only in A" in recs
        assert "Only in B" in recs

    def test_all_recommendations_preserves_order(self, full_project: Project) -> None:
        r1 = ReviewResult(
            reviewer_name="A", score=7.0, summary="s", recommendations=["First", "Second"]
        )
        r2 = ReviewResult(
            reviewer_name="B", score=7.0, summary="s", recommendations=["Third"]
        )
        data = ReportData(project=full_project, results=[r1, r2])
        recs = data.all_recommendations
        assert recs == ["First", "Second", "Third"]


# ---------------------------------------------------------------------------
# ReportGenerator
# ---------------------------------------------------------------------------


class TestReportGenerator:
    def test_generate_creates_file(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        assert path.exists()

    def test_generate_returns_correct_path(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data, filename="my_report.md")
        assert path.name == "my_report.md"
        assert path.parent == tmp_output_dir

    def test_report_contains_project_title(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        content = path.read_text(encoding="utf-8")
        assert report_data.project.title in content

    def test_report_contains_overall_score(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        content = path.read_text(encoding="utf-8")
        assert "Overall Score" in content

    def test_report_contains_all_reviewer_names(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        content = path.read_text(encoding="utf-8")
        for result in report_data.results:
            assert result.reviewer_name in content

    def test_report_contains_score_table(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        content = path.read_text(encoding="utf-8")
        assert "Score Summary" in content
        assert "Reviewer" in content

    def test_report_contains_recommendations(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        content = path.read_text(encoding="utf-8")
        assert "Key Recommendations" in content

    def test_report_contains_strengths_section(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        # Inject a result with strengths so the section appears
        result_with_strengths = ReviewResult(
            reviewer_name="Technology",
            score=7.5,
            summary="Good",
            strengths=["Strength one"],
            weaknesses=[],
            recommendations=[],
        )
        data = ReportData(project=report_data.project, results=[result_with_strengths])
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(data)
        content = path.read_text(encoding="utf-8")
        assert "Strengths" in content
        assert "Strength one" in content

    def test_report_creates_output_dir_if_missing(
        self, report_data: ReportData, tmp_path: Path
    ) -> None:
        nonexistent_dir = tmp_path / "new" / "nested" / "dir"
        gen = ReportGenerator(output_dir=nonexistent_dir)
        path = gen.generate(report_data)
        assert path.exists()

    def test_report_is_valid_markdown_with_headers(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        content = path.read_text(encoding="utf-8")
        assert content.startswith("# OpenReview Report")

    def test_report_contains_generated_timestamp(
        self, report_data: ReportData, tmp_output_dir: Path
    ) -> None:
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(report_data)
        content = path.read_text(encoding="utf-8")
        assert "Generated:" in content

    def test_report_with_no_results(
        self, full_project: Project, tmp_output_dir: Path
    ) -> None:
        data = ReportData(project=full_project, results=[])
        gen = ReportGenerator(output_dir=tmp_output_dir)
        path = gen.generate(data)
        content = path.read_text(encoding="utf-8")
        assert "0.0" in content or "No recommendations" in content
