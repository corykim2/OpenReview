"""Tests for reviewer agent implementations."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.core.base_reviewer import BaseReviewer
from src.core.models import Project, ReviewResult
from src.providers.mock_provider import MockProvider
from src.reviewers.business import BusinessReviewer
from src.reviewers.market import MarketReviewer
from src.reviewers.risk import RiskReviewer
from src.reviewers.technology import TechnologyReviewer
from src.reviewers.ux import UXReviewer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_reviewer(cls, provider, prompts_dir):
    return cls(provider=provider, prompts_dir=prompts_dir)


ALL_REVIEWER_CLASSES = [
    TechnologyReviewer,
    BusinessReviewer,
    MarketReviewer,
    UXReviewer,
    RiskReviewer,
]


# ---------------------------------------------------------------------------
# BaseReviewer contract
# ---------------------------------------------------------------------------


class TestBaseReviewerContract:
    def test_cannot_instantiate_without_reviewer_name(
        self, mock_provider: MockProvider, tmp_prompts_dir: Path
    ) -> None:
        class BadReviewer(BaseReviewer):
            reviewer_name = ""
            prompt_file = "technology.md"

            def get_focus_areas(self) -> list[str]:
                return []

        with pytest.raises(NotImplementedError):
            BadReviewer(provider=mock_provider, prompts_dir=tmp_prompts_dir)

    def test_cannot_instantiate_without_prompt_file(
        self, mock_provider: MockProvider, tmp_prompts_dir: Path
    ) -> None:
        class BadReviewer(BaseReviewer):
            reviewer_name = "Test"
            prompt_file = ""

            def get_focus_areas(self) -> list[str]:
                return []

        with pytest.raises(NotImplementedError):
            BadReviewer(provider=mock_provider, prompts_dir=tmp_prompts_dir)

    def test_raises_file_not_found_for_missing_template(
        self, mock_provider: MockProvider, tmp_path: Path
    ) -> None:
        class GoodReviewer(BaseReviewer):
            reviewer_name = "Test"
            prompt_file = "nonexistent.md"

            def get_focus_areas(self) -> list[str]:
                return []

        with pytest.raises(FileNotFoundError):
            GoodReviewer(provider=mock_provider, prompts_dir=tmp_path)

    def test_extract_json_from_plain_json(self) -> None:
        data = json.dumps({"score": 7, "summary": "test"})
        result = BaseReviewer._extract_json(data)
        assert result is not None
        assert result["score"] == 7

    def test_extract_json_from_fenced_block(self) -> None:
        data = "```json\n{\"score\": 8, \"summary\": \"hello\"}\n```"
        result = BaseReviewer._extract_json(data)
        assert result is not None
        assert result["score"] == 8

    def test_extract_json_returns_none_for_no_json(self) -> None:
        result = BaseReviewer._extract_json("plain text with no json")
        assert result is None

    def test_safe_score_clamps_above_10(self) -> None:
        assert BaseReviewer._safe_score(15.0) == 10.0

    def test_safe_score_clamps_below_0(self) -> None:
        assert BaseReviewer._safe_score(-5.0) == 0.0

    def test_safe_score_handles_string(self) -> None:
        assert BaseReviewer._safe_score("7.5") == 7.5

    def test_safe_score_handles_none(self) -> None:
        assert BaseReviewer._safe_score(None) == 5.0

    def test_safe_score_handles_non_numeric_string(self) -> None:
        assert BaseReviewer._safe_score("not_a_number") == 5.0


# ---------------------------------------------------------------------------
# Individual reviewer instantiation
# ---------------------------------------------------------------------------


class TestReviewerInstantiation:
    @pytest.mark.parametrize("ReviewerClass", ALL_REVIEWER_CLASSES)
    def test_instantiates_successfully(
        self,
        ReviewerClass,
        mock_provider: MockProvider,
        tmp_prompts_dir: Path,
    ) -> None:
        reviewer = make_reviewer(ReviewerClass, mock_provider, tmp_prompts_dir)
        assert reviewer.reviewer_name != ""

    @pytest.mark.parametrize("ReviewerClass", ALL_REVIEWER_CLASSES)
    def test_get_focus_areas_returns_list(
        self,
        ReviewerClass,
        mock_provider: MockProvider,
        tmp_prompts_dir: Path,
    ) -> None:
        reviewer = make_reviewer(ReviewerClass, mock_provider, tmp_prompts_dir)
        areas = reviewer.get_focus_areas()
        assert isinstance(areas, list)
        assert len(areas) > 0


# ---------------------------------------------------------------------------
# review() method
# ---------------------------------------------------------------------------


class TestReviewMethod:
    @pytest.mark.parametrize("ReviewerClass", ALL_REVIEWER_CLASSES)
    def test_review_returns_review_result(
        self,
        ReviewerClass,
        mock_provider: MockProvider,
        tmp_prompts_dir: Path,
        sample_project: Project,
    ) -> None:
        reviewer = make_reviewer(ReviewerClass, mock_provider, tmp_prompts_dir)
        result = reviewer.review(sample_project)
        assert isinstance(result, ReviewResult)

    @pytest.mark.parametrize("ReviewerClass", ALL_REVIEWER_CLASSES)
    def test_review_result_has_correct_reviewer_name(
        self,
        ReviewerClass,
        mock_provider: MockProvider,
        tmp_prompts_dir: Path,
        sample_project: Project,
    ) -> None:
        reviewer = make_reviewer(ReviewerClass, mock_provider, tmp_prompts_dir)
        result = reviewer.review(sample_project)
        assert result.reviewer_name == reviewer.reviewer_name

    @pytest.mark.parametrize("ReviewerClass", ALL_REVIEWER_CLASSES)
    def test_review_score_in_valid_range(
        self,
        ReviewerClass,
        mock_provider: MockProvider,
        tmp_prompts_dir: Path,
        sample_project: Project,
    ) -> None:
        reviewer = make_reviewer(ReviewerClass, mock_provider, tmp_prompts_dir)
        result = reviewer.review(sample_project)
        assert 0.0 <= result.score <= 10.0

    def test_review_parses_valid_json_response(
        self,
        tmp_prompts_dir: Path,
        sample_project: Project,
        valid_json_response: str,
    ) -> None:
        provider = MagicMock()
        provider.complete.return_value = valid_json_response
        reviewer = TechnologyReviewer(provider=provider, prompts_dir=tmp_prompts_dir)
        result = reviewer.review(sample_project)
        assert result.score == 7.0
        assert result.summary == "This is a test summary."
        assert result.strengths == ["Strength A", "Strength B"]
        assert result.weaknesses == ["Weakness A"]
        assert result.recommendations == ["Recommendation A", "Recommendation B"]

    def test_review_falls_back_on_invalid_json(
        self,
        tmp_prompts_dir: Path,
        sample_project: Project,
        invalid_json_response: str,
    ) -> None:
        provider = MagicMock()
        provider.complete.return_value = invalid_json_response
        reviewer = TechnologyReviewer(provider=provider, prompts_dir=tmp_prompts_dir)
        result = reviewer.review(sample_project)
        assert result.score == 5.0
        assert isinstance(result.summary, str)

    def test_project_context_injected_into_prompt(
        self,
        tmp_prompts_dir: Path,
        sample_project: Project,
    ) -> None:
        provider = MagicMock()
        provider.complete.return_value = json.dumps(
            {"score": 5.0, "summary": "ok", "strengths": [], "weaknesses": [], "recommendations": []}
        )
        reviewer = TechnologyReviewer(provider=provider, prompts_dir=tmp_prompts_dir)
        reviewer.review(sample_project)

        call_args = provider.complete.call_args[0][0]
        assert sample_project.title in call_args
        assert sample_project.description in call_args


# ---------------------------------------------------------------------------
# ReviewResult validation
# ---------------------------------------------------------------------------


class TestReviewResultValidation:
    def test_score_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            ReviewResult(reviewer_name="Test", score=11.0, summary="bad score")

    def test_score_negative_raises(self) -> None:
        with pytest.raises(ValueError):
            ReviewResult(reviewer_name="Test", score=-1.0, summary="bad score")

    def test_valid_boundary_scores(self) -> None:
        r1 = ReviewResult(reviewer_name="Test", score=0.0, summary="min")
        r2 = ReviewResult(reviewer_name="Test", score=10.0, summary="max")
        assert r1.score == 0.0
        assert r2.score == 10.0
