"""Tests for AI provider implementations."""

from __future__ import annotations

import json

import pytest

from src.providers.base_provider import AIProvider, ProviderError
from src.providers.mock_provider import MockProvider, _DEFAULT_RESPONSE, _MOCK_RESPONSES
from src.providers.openai_provider import OpenAIProvider


# ---------------------------------------------------------------------------
# AIProvider interface contract
# ---------------------------------------------------------------------------


class TestAIProviderInterface:
    def test_mock_is_ai_provider(self, mock_provider: MockProvider) -> None:
        assert isinstance(mock_provider, AIProvider)

    def test_cannot_instantiate_abstract_provider(self) -> None:
        with pytest.raises(TypeError):
            AIProvider()  # type: ignore[abstract]

    def test_provider_error_is_runtime_error(self) -> None:
        err = ProviderError("something went wrong")
        assert isinstance(err, RuntimeError)


# ---------------------------------------------------------------------------
# MockProvider
# ---------------------------------------------------------------------------


class TestMockProvider:
    def test_returns_string(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("Some prompt about technology review")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_valid_json(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("technology reviewer assessment")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_matches_technology_keyword(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("You are a technology reviewer.")
        parsed = json.loads(result)
        assert parsed["score"] == _MOCK_RESPONSES["technology"]["score"]

    def test_matches_business_keyword(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("Evaluate the business model.")
        parsed = json.loads(result)
        assert parsed["score"] == _MOCK_RESPONSES["business"]["score"]

    def test_matches_market_keyword(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("Analyse the market opportunity.")
        parsed = json.loads(result)
        assert parsed["score"] == _MOCK_RESPONSES["market"]["score"]

    def test_matches_ux_keyword(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("Evaluate the ux of this product.")
        parsed = json.loads(result)
        assert parsed["score"] == _MOCK_RESPONSES["ux"]["score"]

    def test_matches_risk_keyword(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("Identify all risk factors.")
        parsed = json.loads(result)
        assert parsed["score"] == _MOCK_RESPONSES["risk"]["score"]

    def test_returns_default_for_unknown_keyword(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("Completely unrelated prompt with no keywords.")
        parsed = json.loads(result)
        assert parsed["score"] == _DEFAULT_RESPONSE["score"]

    def test_response_has_required_fields(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("technology review")
        parsed = json.loads(result)
        for field in ("score", "summary", "strengths", "weaknesses", "recommendations"):
            assert field in parsed, f"Missing field: {field}"

    def test_score_is_within_range(self, mock_provider: MockProvider) -> None:
        for keyword in _MOCK_RESPONSES:
            result = mock_provider.complete(f"This is a {keyword} prompt.")
            parsed = json.loads(result)
            assert 0.0 <= parsed["score"] <= 10.0

    def test_custom_response_overrides_default(self) -> None:
        custom = MockProvider(responses={"technology": {"score": 9.9, "summary": "Overridden"}})
        result = custom.complete("technology assessment")
        parsed = json.loads(result)
        assert parsed["score"] == 9.9
        assert parsed["summary"] == "Overridden"

    def test_repr(self, mock_provider: MockProvider) -> None:
        assert repr(mock_provider) == "MockProvider()"

    def test_case_insensitive_matching(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("TECHNOLOGY REVIEW IN CAPS")
        parsed = json.loads(result)
        assert parsed["score"] == _MOCK_RESPONSES["technology"]["score"]

    def test_strengths_is_list(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("technology")
        parsed = json.loads(result)
        assert isinstance(parsed["strengths"], list)

    def test_weaknesses_is_list(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("technology")
        parsed = json.loads(result)
        assert isinstance(parsed["weaknesses"], list)

    def test_recommendations_is_list(self, mock_provider: MockProvider) -> None:
        result = mock_provider.complete("technology")
        parsed = json.loads(result)
        assert isinstance(parsed["recommendations"], list)


# ---------------------------------------------------------------------------
# OpenAIProvider
# ---------------------------------------------------------------------------


class TestOpenAIProvider:
    def test_raises_value_error_without_api_key(self) -> None:
        with pytest.raises(ValueError, match="API key"):
            OpenAIProvider(api_key="")

    def test_raises_value_error_with_none_api_key(self) -> None:
        with pytest.raises((ValueError, TypeError)):
            OpenAIProvider(api_key=None)  # type: ignore[arg-type]

    def test_repr(self) -> None:
        try:
            provider = OpenAIProvider(api_key="sk-fake-key-for-repr-test")
            assert "OpenAIProvider" in repr(provider)
            assert "gpt-4.1" in repr(provider)
        except ImportError:
            pytest.skip("openai package not installed")

    def test_complete_raises_provider_error_on_api_failure(self) -> None:
        try:
            from unittest.mock import MagicMock, patch

            provider = OpenAIProvider(api_key="sk-fake-key")
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API failure")
            provider._client = mock_client

            with pytest.raises(ProviderError, match="API call failed"):
                provider.complete("test prompt")
        except ImportError:
            pytest.skip("openai package not installed")
