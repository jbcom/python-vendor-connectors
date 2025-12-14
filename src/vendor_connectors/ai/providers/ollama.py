"""Ollama (local models) provider using langchain-ollama.

This module provides local model access through Ollama.
"""

from __future__ import annotations

from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["OllamaProvider"]


class OllamaProvider(BaseLLMProvider):
    """Ollama local model provider via LangChain.

    Uses langchain-ollama for local model access. Requires
    Ollama to be running locally.

    Example:
        >>> provider = OllamaProvider(model="llama3.2")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        **kwargs,
    ):
        """Initialize Ollama provider.

        Args:
            model: Model name (e.g., "llama3.2", "mistral").
            base_url: Ollama server URL.
            temperature: Sampling temperature.
            **kwargs: Additional arguments.
        """
        self.base_url = base_url
        # Ollama doesn't use max_tokens the same way
        super().__init__(model=model, temperature=temperature, max_tokens=4096, **kwargs)

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.OLLAMA

    @property
    def default_model(self) -> str:
        """Get default Ollama model."""
        return "llama3.2"

    def _create_llm(self) -> Any:
        """Create LangChain ChatOllama instance.

        Returns:
            ChatOllama instance.

        Raises:
            ImportError: If langchain-ollama is not installed.
            AIParameterError: If parameters are invalid.
            AINetworkError: If Ollama server is unreachable.
            AIProviderError: For other provider-specific errors.
        """
        try:
            from langchain_ollama import ChatOllama
        except ImportError as e:
            raise ImportError(
                "langchain-ollama is required for Ollama provider. "
                "Install with: pip install vendor-connectors[ai-ollama]"
            ) from e

        from vendor_connectors.ai.exceptions import (
            AINetworkError,
            AIParameterError,
            AIProviderError,
        )

        # Validate temperature
        if not 0.0 <= self.temperature <= 1.0:
            raise AIParameterError(f"Temperature must be between 0.0 and 1.0, got {self.temperature}")

        try:
            return ChatOllama(
                model=self.model,
                base_url=self.base_url,
                temperature=self.temperature,
                **self._kwargs,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if (
                "connection" in error_msg
                or "unreachable" in error_msg
                or "refused" in error_msg
                or "timeout" in error_msg
            ):
                raise AINetworkError(
                    f"Failed to connect to Ollama server at {self.base_url}. Ensure Ollama is running: {e}"
                ) from e
            if "model" in error_msg or "invalid" in error_msg:
                raise AIParameterError(f"Invalid parameters for Ollama provider: {e}") from e
            raise AIProviderError(f"Failed to create Ollama provider: {e}") from e
