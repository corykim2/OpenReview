"""Shared pytest fixtures for OpenReview tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.models import Project, ReportData, ReviewResult
from src.providers.mock_provider import MockProvider


# ---------------------------------------------------------------------------
# Sample project fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_project() -> Project:
    """A minimal valid Project instance for unit tests."""
    return Project(
        title="Test Project",
        description="A test project description for unit testing purposes.",
        target_users=["developers", "testers"],
        business_model="subscription",
        raw_data={
            "title": "Test Project",
            "description": "A test project description for unit testing purposes.",
            "target_users": ["developers", "testers"],
            "business_model": "subscription",
        },
    )


@pytest.fixture
def full_project() -> Project:
    """A richly-populated Project instance."""
    return Project(
        title="AI Resume Builder",
        description=(
            "An AI-powered platform that generates personalised, ATS-optimised "
            "resumes from a structured profile input."
        ),
        target_users=["students", "job seekers"],
        business_model="freemium subscription",
        raw_data={
            "title": "AI Resume Builder",
            "description": "...",
            "target_users": ["students", "job seekers"],
            "business_model": "freemium subscription",
            "tech_stack": ["Python", "React", "OpenAI"],
        },
    )


# ---------------------------------------------------------------------------
# Provider fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_provider() -> MockProvider:
    return MockProvider()


@pytest.fixture
def custom_mock_provider() -> MockProvider:
    """MockProvider with a completely custom response dict."""
    return MockProvider(
        responses={
            "custom": {
                "score": 8.5,
                "summary": "Custom mock summary.",
                "strengths": ["Custom strength"],
                "weaknesses": ["Custom weakness"],
                "recommendations": ["Custom recommendation"],
            }
        }
    )


# ---------------------------------------------------------------------------
# ReviewResult fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_review_result() -> ReviewResult:
    return ReviewResult(
        reviewer_name="Technology",
        score=7.5,
        summary="Solid technical foundation.",
        strengths=["Good architecture", "Modern stack"],
        weaknesses=["Missing CI/CD", "No load tests"],
        recommendations=["Add Docker Compose", "Set up GitHub Actions"],
    )


@pytest.fixture
def all_review_results() -> list[ReviewResult]:
    return [
        ReviewResult(reviewer_name="Technology", score=7.5, summary="Tech review"),
        ReviewResult(reviewer_name="Business", score=6.8, summary="Business review"),
        ReviewResult(reviewer_name="Market", score=7.2, summary="Market review"),
        ReviewResult(reviewer_name="UX", score=6.5, summary="UX review"),
        ReviewResult(reviewer_name="Risk", score=5.9, summary="Risk review"),
    ]


@pytest.fixture
def report_data(full_project: Project, all_review_results: list[ReviewResult]) -> ReportData:
    return ReportData(project=full_project, results=all_review_results)


# ---------------------------------------------------------------------------
# File system fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_prompts_dir(tmp_path: Path) -> Path:
    """Create a temporary prompts directory with all required templates."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    template = (
        "# {name} Reviewer Prompt\n\n"
        "You are a {name} reviewer.\n\n"
        "## Project Information\n\n"
        "{{{{PROJECT_CONTEXT}}}}\n\n"
        "Return JSON with score, summary, strengths, weaknesses, recommendations."
    )

    for name in ("technology", "business", "market", "ux", "risk"):
        (prompts_dir / f"{name}.md").write_text(
            template.format(name=name.capitalize()), encoding="utf-8"
        )

    return prompts_dir


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def valid_json_response() -> str:
    """A well-formed JSON response that all reviewers can parse."""
    return json.dumps(
        {
            "score": 7.0,
            "summary": "This is a test summary.",
            "strengths": ["Strength A", "Strength B"],
            "weaknesses": ["Weakness A"],
            "recommendations": ["Recommendation A", "Recommendation B"],
        }
    )


@pytest.fixture
def invalid_json_response() -> str:
    return "This is not valid JSON at all."
