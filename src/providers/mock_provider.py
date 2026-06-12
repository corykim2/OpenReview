"""Mock AI provider for testing and offline use."""

from __future__ import annotations

import json
import logging
import re


from src.providers.base_provider import AIProvider


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default mock responses keyed by reviewer keyword found in the prompt.
# Each value is a dict that will be serialised to JSON and returned.
# ---------------------------------------------------------------------------
_MOCK_RESPONSES: dict[str, dict] = {
    "technology": {
        "score": 7.5,
        "summary": (
            "The project demonstrates a solid technical foundation with modern "
            "AI-driven capabilities.  The proposed architecture is feasible, "
            "though the team should address scalability concerns early."
        ),
        "strengths": [
            "Leverages well-established AI/ML frameworks",
            "Clear separation between frontend and backend concerns",
            "Stateless API design enables horizontal scaling",
        ],
        "weaknesses": [
            "No mention of model versioning or A/B testing strategy",
            "Data pipeline design is underspecified",
            "Latency requirements for real-time inference are not addressed",
        ],
        "recommendations": [
            "Define an MLOps workflow for model training and deployment",
            "Implement a caching layer (e.g. Redis) to reduce repeated inference costs",
            "Conduct load testing before launch with realistic traffic profiles",
        ],
    },
    "business": {
        "score": 6.8,
        "summary": (
            "The business model has clear revenue potential but faces stiff "
            "competition.  A freemium tier could accelerate user acquisition, "
            "while enterprise contracts would stabilise recurring revenue."
        ),
        "strengths": [
            "Recurring subscription model provides predictable MRR",
            "Low marginal cost per additional user once infrastructure is in place",
            "Clear value proposition for the target segment",
        ],
        "weaknesses": [
            "Customer acquisition cost (CAC) assumptions are not quantified",
            "Churn risk is high in a competitive SaaS market",
            "No secondary revenue stream identified",
        ],
        "recommendations": [
            "Model out unit economics: CAC, LTV, payback period",
            "Introduce a freemium tier to reduce top-of-funnel friction",
            "Explore B2B partnerships as a low-cost distribution channel",
        ],
    },
    "market": {
        "score": 7.2,
        "summary": (
            "The target market is large and growing, with clear demand signals. "
            "However, existing incumbents hold strong network effects, so a "
            "differentiated go-to-market strategy is essential."
        ),
        "strengths": [
            "TAM is in the multi-billion dollar range with strong CAGR",
            "Growing awareness of the problem space among target users",
            "Regulatory tailwinds in the sector",
        ],
        "weaknesses": [
            "Two well-funded direct competitors already have market share",
            "Network effects favour incumbents",
            "International expansion challenges not addressed",
        ],
        "recommendations": [
            "Focus on a defensible niche (e.g. one geography or industry vertical) first",
            "Conduct 20+ customer discovery interviews before finalising positioning",
            "Map the competitive landscape using a 2x2 differentiation matrix",
        ],
    },
    "ux": {
        "score": 6.5,
        "summary": (
            "The user experience concept shows promise but lacks detail on "
            "onboarding flows and accessibility.  Investing in user research "
            "early will prevent costly redesigns later."
        ),
        "strengths": [
            "Intuitive core workflow described",
            "Mobile-first consideration noted",
            "Personalisation features increase perceived value",
        ],
        "weaknesses": [
            "Onboarding journey is not defined",
            "Accessibility (WCAG) compliance not mentioned",
            "No error recovery or empty-state handling described",
        ],
        "recommendations": [
            "Conduct usability testing with 5 representative users before engineering",
            "Define an onboarding checklist to drive activation",
            "Ensure WCAG 2.1 AA compliance from the start",
        ],
    },
    "risk": {
        "score": 5.9,
        "summary": (
            "Several material risks require mitigation plans before the project "
            "can move to production.  Regulatory and data-privacy risks are the "
            "most pressing and should be addressed in the next planning cycle."
        ),
        "strengths": [
            "Team appears aware of key technical risks",
            "Modular architecture reduces single points of failure",
        ],
        "weaknesses": [
            "GDPR / data privacy compliance strategy is absent",
            "Key-person dependency on founding team",
            "No disaster-recovery or business-continuity plan",
        ],
        "recommendations": [
            "Engage a privacy lawyer to draft a compliant data-processing agreement",
            "Document a runbook for top-5 failure scenarios",
            "Establish a security incident response process before launch",
        ],
    },
}

_DEFAULT_RESPONSE: dict = {
    "score": 6.0,
    "summary": "This is a mock review response generated for testing purposes.",
    "strengths": ["Clear problem statement", "Defined target audience"],
    "weaknesses": ["Limited detail provided", "Execution risks not addressed"],
    "recommendations": [
        "Provide more implementation detail",
        "Define success metrics",
    ],
}


class MockProvider(AIProvider):
    """AI provider that returns deterministic mock responses.

    Useful for development, testing, and demos when no OpenAI API key
    is available.  The response is selected by searching for reviewer
    keywords in the prompt text.

    Args:
        responses: Optional override mapping of keyword → response dict.
            Merged on top of the built-in defaults.
    """

    def __init__(self, responses: dict[str, dict] | None = None) -> None:
        self._responses: dict[str, dict] = dict(_MOCK_RESPONSES)
        if responses:
            self._responses.update(responses)

    def complete(self, prompt: str) -> str:
        """Return a mock JSON response based on keywords found in *prompt*.

        Matching is intentionally anchored to the prompt *header* (first 5
        lines) so that project-context text like "business_model: …" does not
        cause false positives for later reviewers.

        Args:
            prompt: The full prompt string (used only for keyword detection).

        Returns:
            A JSON-encoded string matching the expected reviewer response schema.
        """
        # Primary: look for "# <keyword> Reviewer Prompt" in the first line
        first_line = prompt.splitlines()[0].lower() if prompt.strip() else ""
        for keyword, response in self._responses.items():
            pattern = rf"#\s*{re.escape(keyword)}\s+reviewer"
            if re.search(pattern, first_line):
                logger.debug("MockProvider title-matched keyword '%s'", keyword)
                return json.dumps(response, ensure_ascii=False, indent=2)

        # Fallback: whole-text search (for custom prompts without standard headers)
        prompt_lower = prompt.lower()
        for keyword, response in self._responses.items():
            if re.search(rf"\b{re.escape(keyword)}\b", prompt_lower):
                logger.debug("MockProvider full-text matched keyword '%s'", keyword)
                return json.dumps(response, ensure_ascii=False, indent=2)

        logger.debug("MockProvider: no keyword matched; returning default response")
        return json.dumps(_DEFAULT_RESPONSE, ensure_ascii=False, indent=2)

    def __repr__(self) -> str:
        return "MockProvider()"
