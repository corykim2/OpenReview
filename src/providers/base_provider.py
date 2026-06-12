"""Abstract base class for AI provider implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Interface contract that every AI provider must satisfy.

    New providers (Anthropic, Gemini, Azure, …) can be added without
    touching the reviewer or report layers — they only need to implement
    :meth:`complete`.
    """

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send *prompt* to the underlying model and return the response text.

        Args:
            prompt: The full prompt string to send.

        Returns:
            The raw text content of the model response.

        Raises:
            ProviderError: If the API call fails in a non-recoverable way.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class ProviderError(RuntimeError):
    """Raised when an AI provider encounters an unrecoverable error."""
