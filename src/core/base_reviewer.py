"""Abstract base class for all reviewer agents."""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path

from src.core.models import Project, ReviewResult
from src.providers.base_provider import AIProvider


logger = logging.getLogger(__name__)

_FALLBACK_SCORE = 5.0
_SCORE_RANGE = (0.0, 10.0)


class BaseReviewer(ABC):
    """Abstract reviewer that loads a prompt template and calls an AI provider.

    Concrete subclasses must define :attr:`reviewer_name` and
    :attr:`prompt_file` class attributes.

    Args:
        provider: The AI provider instance to use for completions.
        prompts_dir: Directory where ``*.md`` prompt templates live.
    """

    reviewer_name: str = ""
    prompt_file: str = ""

    def __init__(self, provider: AIProvider, prompts_dir: Path = Path("prompts")) -> None:
        if not self.reviewer_name:
            raise NotImplementedError("Subclasses must define reviewer_name")
        if not self.prompt_file:
            raise NotImplementedError("Subclasses must define prompt_file")

        self._provider = provider
        self._prompts_dir = Path(prompts_dir)
        self._prompt_template: str = self._load_prompt_template()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def review(self, project: Project) -> ReviewResult:
        """Run the review for *project* and return a structured result.

        The method builds a prompt from the template, sends it to the
        AI provider, then parses the JSON response into a
        :class:`~src.core.models.ReviewResult`.

        Args:
            project: The project data to review.

        Returns:
            A populated :class:`~src.core.models.ReviewResult`.
        """
        prompt = self._build_prompt(project)
        logger.info("Running %s review for '%s'", self.reviewer_name, project.title)
        raw_response = self._provider.complete(prompt)
        return self._parse_response(raw_response)

    # ------------------------------------------------------------------
    # Protected helpers
    # ------------------------------------------------------------------

    def _load_prompt_template(self) -> str:
        """Read the prompt template file from disk."""
        template_path = self._prompts_dir / self.prompt_file
        if not template_path.exists():
            raise FileNotFoundError(
                f"Prompt template not found: {template_path}"
            )
        return template_path.read_text(encoding="utf-8")

    def _build_prompt(self, project: Project) -> str:
        """Inject project context into the prompt template."""
        context = project.to_context_string()
        return self._prompt_template.replace("{{PROJECT_CONTEXT}}", context)

    def _parse_response(self, raw_response: str) -> ReviewResult:
        """Parse AI response text into a ``ReviewResult``.

        The AI is instructed to return a JSON object.  If parsing fails the
        method falls back gracefully so that a single bad response doesn't
        crash the entire review pipeline.

        Args:
            raw_response: The raw text returned by the AI provider.

        Returns:
            A ``ReviewResult`` instance.
        """
        data = self._extract_json(raw_response)
        if data is None:
            logger.warning(
                "%s: Could not parse JSON from response; using fallback.",
                self.reviewer_name,
            )
            return ReviewResult(
                reviewer_name=self.reviewer_name,
                score=_FALLBACK_SCORE,
                summary=raw_response.strip() or "No summary available.",
                raw_response=raw_response,
            )

        score = self._safe_score(data.get("score", _FALLBACK_SCORE))
        return ReviewResult(
            reviewer_name=self.reviewer_name,
            score=score,
            summary=str(data.get("summary", "")),
            strengths=list(data.get("strengths", [])),
            weaknesses=list(data.get("weaknesses", [])),
            recommendations=list(data.get("recommendations", [])),
            raw_response=raw_response,
        )

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        """Try to extract a JSON object from *text*.

        Handles both bare JSON and JSON wrapped in markdown code fences.
        """
        # Strip markdown code fences if present
        fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        candidate = fenced.group(1).strip() if fenced else text.strip()

        # Attempt to locate the outermost JSON object
        brace_start = candidate.find("{")
        brace_end = candidate.rfind("}")
        if brace_start == -1 or brace_end == -1:
            return None

        try:
            return json.loads(candidate[brace_start : brace_end + 1])
        except json.JSONDecodeError:
            logger.debug("JSON decode failed; raw candidate: %s", candidate[:200])
            return None

    @staticmethod
    def _safe_score(value: object) -> float:
        """Coerce *value* to a valid score in [0, 10]."""
        try:
            score = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return _FALLBACK_SCORE
        lo, hi = _SCORE_RANGE
        return max(lo, min(hi, score))

    # ------------------------------------------------------------------
    # Abstract hook (optional override)
    # ------------------------------------------------------------------

    @abstractmethod
    def get_focus_areas(self) -> list[str]:
        """Return the key areas this reviewer focuses on.

        Used for logging, documentation, and report headers.
        """
