"""OpenAI (GPT) provider using langchain-openai.

This module provides GPT model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["OpenAIProvider"]


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider via LangChain.

    Uses langchain-openai for GPT API access with full
    tool calling and streaming support.

    Example:
        >>> provider = OpenAIProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.OPENAI

    @property
    def default_model(self) -> str:
        """Get default GPT model."""
        return "gpt-4o"

    def _create_llm(self) -> Any:
        """Create LangChain ChatOpenAI instance.

        Returns:
            ChatOpenAI instance.

        Raises:
            ImportError: If langchain-openai is not installed.
            AIAuthenticationError: If API key is missing.
            AIParameterError: If parameters are invalid.
            AIProviderError: For other provider-specific errors.
        """
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            raise ImportError(
                "langchain-openai is required for OpenAI provider. "
                "Install with: pip install vendor-connectors[ai-openai]"
            ) from e

        from vendor_connectors.ai.exceptions import (
            AIAuthenticationError,
            AIParameterError,
            AIProviderError,
        )

        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise AIAuthenticationError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        # Validate temperature
        if not 0.0 <= self.temperature <= 2.0:
            raise AIParameterError(f"Temperature must be between 0.0 and 2.0, got {self.temperature}")

        # Validate max_tokens
        if self.max_tokens <= 0:
            raise AIParameterError(f"max_tokens must be positive, got {self.max_tokens}")

        try:
            return ChatOpenAI(
                model=self.model,
                api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **self._kwargs,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "model" in error_msg or "invalid" in error_msg:
                raise AIParameterError(f"Invalid parameters for OpenAI provider: {e}") from e
            raise AIProviderError(f"Failed to create OpenAI provider: {e}") from e
