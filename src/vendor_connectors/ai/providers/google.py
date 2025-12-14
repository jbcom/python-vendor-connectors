"""Google (Gemini) provider using langchain-google-genai.

This module provides Gemini model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["GoogleProvider"]


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider via LangChain.

    Uses langchain-google-genai for Gemini API access with full
    tool calling and streaming support.

    Example:
        >>> provider = GoogleProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.GOOGLE

    @property
    def default_model(self) -> str:
        """Get default Gemini model."""
        return "gemini-1.5-pro"

    def _create_llm(self) -> Any:
        """Create LangChain ChatGoogleGenerativeAI instance.

        Returns:
            ChatGoogleGenerativeAI instance.

        Raises:
            ImportError: If langchain-google-genai is not installed.
            AIAuthenticationError: If API key is missing.
            AIParameterError: If parameters are invalid.
            AIProviderError: For other provider-specific errors.
        """
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as e:
            raise ImportError(
                "langchain-google-genai is required for Google provider. "
                "Install with: pip install vendor-connectors[ai-google]"
            ) from e

        from vendor_connectors.ai.exceptions import (
            AIAuthenticationError,
            AIParameterError,
            AIProviderError,
        )

        api_key = self.api_key or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise AIAuthenticationError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )

        # Validate temperature
        if not 0.0 <= self.temperature <= 1.0:
            raise AIParameterError(f"Temperature must be between 0.0 and 1.0, got {self.temperature}")

        # Validate max_tokens
        if self.max_tokens <= 0:
            raise AIParameterError(f"max_tokens must be positive, got {self.max_tokens}")

        try:
            return ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=api_key,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                **self._kwargs,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "model" in error_msg or "invalid" in error_msg:
                raise AIParameterError(f"Invalid parameters for Google provider: {e}") from e
            raise AIProviderError(f"Failed to create Google provider: {e}") from e
