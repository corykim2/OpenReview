"""OpenAI-backed AI provider implementation."""

from __future__ import annotations

import logging

from src.providers.base_provider import AIProvider, ProviderError


logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an expert project reviewer. Analyze the given project proposal "
    "from your assigned perspective and return a structured JSON response exactly "
    "as requested.  Do not include any text outside the JSON object."
)


class OpenAIProvider(AIProvider):
    """AI provider that delegates to the OpenAI Chat Completions API.

    Args:
        api_key: OpenAI API key.  If empty, instantiation raises ``ValueError``.
        model: Model identifier (e.g. ``"gpt-4.1"``).
        temperature: Sampling temperature in ``[0, 2]``.
        max_tokens: Maximum completion tokens.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> None:
        if not api_key:
            raise ValueError(
                "OpenAI API key is required.  Set OPENAI_API_KEY or configure "
                "openai_api_key in config.yaml."
            )
        self._api_key = api_key
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = self._build_client()

    # ------------------------------------------------------------------
    # AIProvider interface
    # ------------------------------------------------------------------

    def complete(self, prompt: str) -> str:
        """Call the OpenAI Chat Completions endpoint and return the reply text.

        Args:
            prompt: The user-turn content to send.

        Returns:
            The assistant's reply as a plain string.

        Raises:
            ProviderError: Wraps any ``openai`` SDK exception.
        """
        logger.debug("OpenAI request | model=%s | prompt_len=%d", self._model, len(prompt))
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                response_format={"type": "json_object"},
            )
            content: str = response.choices[0].message.content or ""
            logger.debug("OpenAI response received | length=%d", len(content))
            return content
        except Exception as exc:  # openai.OpenAIError and subclasses
            raise ProviderError(f"OpenAI API call failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_client(self):  # type: ignore[return]
        """Lazily import and instantiate the openai client.

        Importing here (not at module level) avoids a hard dependency crash
        when the package is installed without ``openai`` and ``MockProvider``
        is in use.
        """
        try:
            import openai  # noqa: PLC0415

            return openai.OpenAI(api_key=self._api_key)
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required for OpenAIProvider.  "
                "Install it with: pip install openai"
            ) from exc

    def __repr__(self) -> str:
        return f"OpenAIProvider(model={self._model!r})"
