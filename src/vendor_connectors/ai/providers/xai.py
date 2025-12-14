"""xAI (Grok) provider using langchain-xai.

This module provides Grok model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["XAIProvider"]


class XAIProvider(BaseLLMProvider):
    """xAI Grok provider via LangChain.

    Uses langchain-xai for Grok API access.

    Example:
        >>> provider = XAIProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.XAI

    @property
    def default_model(self) -> str:
        """Get default Grok model."""
        return "grok-2"

    def _create_llm(self) -> Any:
        """Create LangChain ChatXAI instance.

        Returns:
            ChatXAI instance.

        Raises:
            ImportError: If langchain-xai is not installed.
            AIAuthenticationError: If API key is missing.
            AIParameterError: If parameters are invalid.
            AIProviderError: For other provider-specific errors.
        """
        try:
            from langchain_xai import ChatXAI
        except ImportError as e:
            raise ImportError(
                "langchain-xai is required for xAI provider. Install with: pip install vendor-connectors[ai-xai]"
            ) from e

        from vendor_connectors.ai.exceptions import (
            AIAuthenticationError,
            AIParameterError,
            AIProviderError,
        )

        api_key = self.api_key or os.environ.get("XAI_API_KEY")
        if not api_key:
            raise AIAuthenticationError(
                "xAI API key is required. Set XAI_API_KEY environment variable or pass api_key parameter."
            )

        # Validate temperature
        if not 0.0 <= self.temperature <= 1.0:
            raise AIParameterError(f"Temperature must be between 0.0 and 1.0, got {self.temperature}")

        # Validate max_tokens
        if self.max_tokens <= 0:
            raise AIParameterError(f"max_tokens must be positive, got {self.max_tokens}")

        try:
            return ChatXAI(
                model=self.model,
                xai_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **self._kwargs,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "model" in error_msg or "invalid" in error_msg:
                raise AIParameterError(f"Invalid parameters for xAI provider: {e}") from e
            raise AIProviderError(f"Failed to create xAI provider: {e}") from e
