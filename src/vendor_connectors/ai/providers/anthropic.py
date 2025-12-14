"""Anthropic (Claude) provider using langchain-anthropic.

This module provides Claude model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["AnthropicProvider"]


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider via LangChain.

    Uses langchain-anthropic for Claude API access with full
    tool calling and streaming support.

    Example:
        >>> provider = AnthropicProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.ANTHROPIC

    @property
    def default_model(self) -> str:
        """Get default Claude model."""
        return "claude-sonnet-4-20250514"

    def _create_llm(self) -> Any:
        """Create LangChain ChatAnthropic instance.

        Returns:
            ChatAnthropic instance.

        Raises:
            ImportError: If langchain-anthropic is not installed.
            AIAuthenticationError: If API key is missing.
            AIParameterError: If parameters are invalid.
            AIProviderError: For other provider-specific errors.
        """
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            raise ImportError(
                "langchain-anthropic is required for Anthropic provider. "
                "Install with: pip install vendor-connectors[ai-anthropic]"
            ) from e

        from vendor_connectors.ai.exceptions import (
            AIAuthenticationError,
            AIParameterError,
            AIProviderError,
        )

        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise AIAuthenticationError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        # Validate temperature
        if not 0.0 <= self.temperature <= 1.0:
            raise AIParameterError(f"Temperature must be between 0.0 and 1.0, got {self.temperature}")

        # Validate max_tokens
        if self.max_tokens <= 0:
            raise AIParameterError(f"max_tokens must be positive, got {self.max_tokens}")

        try:
            return ChatAnthropic(
                model=self.model,
                api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **self._kwargs,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "model" in error_msg or "invalid" in error_msg:
                raise AIParameterError(f"Invalid parameters for Anthropic provider: {e}") from e
            raise AIProviderError(f"Failed to create Anthropic provider: {e}") from e
