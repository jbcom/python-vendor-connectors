"""Tests for AI provider error handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# Import exceptions
from vendor_connectors.ai.exceptions import (
    AIAuthenticationError,
    AIError,
    AIModelError,
    AINetworkError,
    AIParameterError,
    AIProviderError,
    AIRateLimitError,
)


class TestExceptions:
    """Test exception hierarchy."""

    def test_exception_inheritance(self):
        """All AI exceptions should inherit from AIError."""
        assert issubclass(AIProviderError, AIError)
        assert issubclass(AIAuthenticationError, AIError)
        assert issubclass(AINetworkError, AIError)
        assert issubclass(AIParameterError, AIError)
        assert issubclass(AIRateLimitError, AIError)
        assert issubclass(AIModelError, AIError)

    def test_exception_messages(self):
        """Exceptions should preserve error messages."""
        msg = "Test error message"
        exc = AIError(msg)
        assert str(exc) == msg

        exc = AIAuthenticationError(msg)
        assert str(exc) == msg


class TestAnthropicProviderErrorHandling:
    """Test error handling in AnthropicProvider."""

    def test_missing_api_key(self):
        """Should raise AIAuthenticationError when API key is missing."""
        # Mock the langchain_anthropic import to avoid dependency
        with patch.dict("sys.modules", {"langchain_anthropic": MagicMock()}):
            with patch.dict("os.environ", {}, clear=True):
                from vendor_connectors.ai.providers.anthropic import AnthropicProvider

                provider = AnthropicProvider()
                with pytest.raises(AIAuthenticationError, match="API key is required"):
                    _ = provider.llm

    def test_invalid_temperature(self):
        """Should raise AIParameterError for invalid temperature."""
        # Mock the langchain_anthropic import to avoid dependency
        with patch.dict("sys.modules", {"langchain_anthropic": MagicMock()}):
            from vendor_connectors.ai.providers.anthropic import AnthropicProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = AnthropicProvider(api_key="test-key", temperature=2.5)
                _ = provider.llm

    def test_negative_temperature(self):
        """Should raise AIParameterError for negative temperature."""
        # Mock the langchain_anthropic import to avoid dependency
        with patch.dict("sys.modules", {"langchain_anthropic": MagicMock()}):
            from vendor_connectors.ai.providers.anthropic import AnthropicProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = AnthropicProvider(api_key="test-key", temperature=-0.1)
                _ = provider.llm

    def test_invalid_max_tokens(self):
        """Should raise AIParameterError for invalid max_tokens."""
        # Mock the langchain_anthropic import to avoid dependency
        with patch.dict("sys.modules", {"langchain_anthropic": MagicMock()}):
            from vendor_connectors.ai.providers.anthropic import AnthropicProvider

            with pytest.raises(AIParameterError, match="max_tokens must be positive"):
                provider = AnthropicProvider(api_key="test-key", max_tokens=0)
                _ = provider.llm

    def test_negative_max_tokens(self):
        """Should raise AIParameterError for negative max_tokens."""
        # Mock the langchain_anthropic import to avoid dependency
        with patch.dict("sys.modules", {"langchain_anthropic": MagicMock()}):
            from vendor_connectors.ai.providers.anthropic import AnthropicProvider

            with pytest.raises(AIParameterError, match="max_tokens must be positive"):
                provider = AnthropicProvider(api_key="test-key", max_tokens=-100)
                _ = provider.llm


class TestOpenAIProviderErrorHandling:
    """Test error handling in OpenAIProvider."""

    def test_missing_api_key(self):
        """Should raise AIAuthenticationError when API key is missing."""
        # Mock the langchain_openai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_openai": MagicMock()}):
            with patch.dict("os.environ", {}, clear=True):
                from vendor_connectors.ai.providers.openai import OpenAIProvider

                provider = OpenAIProvider()
                with pytest.raises(AIAuthenticationError, match="API key is required"):
                    _ = provider.llm

    def test_invalid_temperature(self):
        """Should raise AIParameterError for invalid temperature."""
        # Mock the langchain_openai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_openai": MagicMock()}):
            from vendor_connectors.ai.providers.openai import OpenAIProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = OpenAIProvider(api_key="test-key", temperature=3.0)
                _ = provider.llm

    def test_negative_temperature(self):
        """Should raise AIParameterError for negative temperature."""
        # Mock the langchain_openai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_openai": MagicMock()}):
            from vendor_connectors.ai.providers.openai import OpenAIProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = OpenAIProvider(api_key="test-key", temperature=-0.1)
                _ = provider.llm

    def test_invalid_max_tokens(self):
        """Should raise AIParameterError for invalid max_tokens."""
        # Mock the langchain_openai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_openai": MagicMock()}):
            from vendor_connectors.ai.providers.openai import OpenAIProvider

            with pytest.raises(AIParameterError, match="max_tokens must be positive"):
                provider = OpenAIProvider(api_key="test-key", max_tokens=0)
                _ = provider.llm


class TestGoogleProviderErrorHandling:
    """Test error handling in GoogleProvider."""

    def test_missing_api_key(self):
        """Should raise AIAuthenticationError when API key is missing."""
        # Mock the langchain_google_genai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_google_genai": MagicMock()}):
            with patch.dict("os.environ", {}, clear=True):
                from vendor_connectors.ai.providers.google import GoogleProvider

                provider = GoogleProvider()
                with pytest.raises(AIAuthenticationError, match="API key is required"):
                    _ = provider.llm

    def test_invalid_temperature(self):
        """Should raise AIParameterError for invalid temperature."""
        # Mock the langchain_google_genai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_google_genai": MagicMock()}):
            from vendor_connectors.ai.providers.google import GoogleProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = GoogleProvider(api_key="test-key", temperature=2.0)
                _ = provider.llm

    def test_negative_temperature(self):
        """Should raise AIParameterError for negative temperature."""
        # Mock the langchain_google_genai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_google_genai": MagicMock()}):
            from vendor_connectors.ai.providers.google import GoogleProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = GoogleProvider(api_key="test-key", temperature=-0.5)
                _ = provider.llm

    def test_invalid_max_tokens(self):
        """Should raise AIParameterError for invalid max_tokens."""
        # Mock the langchain_google_genai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_google_genai": MagicMock()}):
            from vendor_connectors.ai.providers.google import GoogleProvider

            with pytest.raises(AIParameterError, match="max_tokens must be positive"):
                provider = GoogleProvider(api_key="test-key", max_tokens=-50)
                _ = provider.llm


class TestXAIProviderErrorHandling:
    """Test error handling in XAIProvider."""

    def test_missing_api_key(self):
        """Should raise AIAuthenticationError when API key is missing."""
        # Mock the langchain_xai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_xai": MagicMock()}):
            with patch.dict("os.environ", {}, clear=True):
                from vendor_connectors.ai.providers.xai import XAIProvider

                provider = XAIProvider()
                with pytest.raises(AIAuthenticationError, match="API key is required"):
                    _ = provider.llm

    def test_invalid_temperature(self):
        """Should raise AIParameterError for invalid temperature."""
        # Mock the langchain_xai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_xai": MagicMock()}):
            from vendor_connectors.ai.providers.xai import XAIProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = XAIProvider(api_key="test-key", temperature=1.5)
                _ = provider.llm

    def test_negative_temperature(self):
        """Should raise AIParameterError for negative temperature."""
        # Mock the langchain_xai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_xai": MagicMock()}):
            from vendor_connectors.ai.providers.xai import XAIProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = XAIProvider(api_key="test-key", temperature=-1.0)
                _ = provider.llm

    def test_invalid_max_tokens(self):
        """Should raise AIParameterError for invalid max_tokens."""
        # Mock the langchain_xai import to avoid dependency
        with patch.dict("sys.modules", {"langchain_xai": MagicMock()}):
            from vendor_connectors.ai.providers.xai import XAIProvider

            with pytest.raises(AIParameterError, match="max_tokens must be positive"):
                provider = XAIProvider(api_key="test-key", max_tokens=0)
                _ = provider.llm


class TestOllamaProviderErrorHandling:
    """Test error handling in OllamaProvider."""

    def test_invalid_temperature(self):
        """Should raise AIParameterError for invalid temperature."""
        # Mock the langchain_ollama import to avoid dependency
        with patch.dict("sys.modules", {"langchain_ollama": MagicMock()}):
            from vendor_connectors.ai.providers.ollama import OllamaProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = OllamaProvider(temperature=1.5)
                _ = provider.llm

    def test_negative_temperature(self):
        """Should raise AIParameterError for negative temperature."""
        # Mock the langchain_ollama import to avoid dependency
        with patch.dict("sys.modules", {"langchain_ollama": MagicMock()}):
            from vendor_connectors.ai.providers.ollama import OllamaProvider

            with pytest.raises(AIParameterError, match="Temperature must be between"):
                provider = OllamaProvider(temperature=-0.2)
                _ = provider.llm


class TestBaseLLMProviderErrorHandling:
    """Test error handling in BaseLLMProvider methods."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing."""
        # Mock all required dependencies
        mock_langchain = MagicMock()
        mock_anthropic = MagicMock()
        mock_langgraph = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
                "langchain_anthropic": mock_anthropic,
                "langgraph": mock_langgraph,
                "langgraph.prebuilt": mock_langgraph.prebuilt,
            },
        ):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
                from vendor_connectors.ai.providers.anthropic import AnthropicProvider

                provider = AnthropicProvider()
                # Mock the LLM to avoid actual API calls
                mock_llm = MagicMock()
                provider._llm = mock_llm
                return provider, mock_llm

    def test_chat_authentication_error(self, mock_provider):
        """Should raise AIAuthenticationError on authentication failure."""
        provider, mock_llm = mock_provider
        mock_llm.invoke.side_effect = Exception("Authentication failed: Invalid API key")

        # Mock langchain dependencies needed by chat() method
        mock_langchain = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
            },
        ):
            with pytest.raises(AIAuthenticationError, match="Authentication failed"):
                provider.chat("Hello")

    def test_chat_rate_limit_error(self, mock_provider):
        """Should raise AIRateLimitError on rate limit."""
        provider, mock_llm = mock_provider
        mock_llm.invoke.side_effect = Exception("Rate limit exceeded")

        mock_langchain = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
            },
        ):
            with pytest.raises(AIRateLimitError, match="Rate limit exceeded"):
                provider.chat("Hello")

    def test_chat_network_error(self, mock_provider):
        """Should raise AINetworkError on network failure."""
        provider, mock_llm = mock_provider
        mock_llm.invoke.side_effect = Exception("Connection timeout")

        mock_langchain = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
            },
        ):
            with pytest.raises(AINetworkError, match="Network error"):
                provider.chat("Hello")

    def test_chat_generic_error(self, mock_provider):
        """Should raise AIProviderError for other errors."""
        provider, mock_llm = mock_provider
        mock_llm.invoke.side_effect = Exception("Unknown error occurred")

        mock_langchain = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
            },
        ):
            with pytest.raises(AIProviderError, match="Provider error during chat"):
                provider.chat("Hello")

    def test_chat_401_error(self, mock_provider):
        """Should raise AIAuthenticationError on 401 status."""
        provider, mock_llm = mock_provider
        mock_llm.invoke.side_effect = Exception("HTTP 401 Unauthorized")

        mock_langchain = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
            },
        ):
            with pytest.raises(AIAuthenticationError, match="Authentication failed"):
                provider.chat("Hello")

    def test_chat_429_error(self, mock_provider):
        """Should raise AIRateLimitError on 429 status."""
        provider, mock_llm = mock_provider
        mock_llm.invoke.side_effect = Exception("HTTP 429 Too Many Requests")

        mock_langchain = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
            },
        ):
            with pytest.raises(AIRateLimitError, match="Rate limit exceeded"):
                provider.chat("Hello")

    def test_chat_quota_error(self, mock_provider):
        """Should raise AIRateLimitError on quota exceeded."""
        provider, mock_llm = mock_provider
        mock_llm.invoke.side_effect = Exception("Quota exceeded for this project")

        mock_langchain = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langchain_core": mock_langchain,
                "langchain_core.messages": mock_langchain.messages,
            },
        ):
            with pytest.raises(AIRateLimitError, match="Rate limit exceeded"):
                provider.chat("Hello")

    def test_invoke_with_tools_authentication_error(self, mock_provider):
        """Should raise AIAuthenticationError on authentication failure in invoke_with_tools."""
        provider, _ = mock_provider

        # Mock langgraph dependencies
        mock_langgraph = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langgraph": mock_langgraph,
                "langgraph.prebuilt": mock_langgraph.prebuilt,
            },
        ):
            # Mock agent creation and invocation
            mock_agent = MagicMock()
            mock_langgraph.prebuilt.create_react_agent.return_value = mock_agent
            mock_agent.invoke.side_effect = Exception("Unauthorized: Invalid API key")

            with pytest.raises(AIAuthenticationError, match="Authentication failed"):
                provider.invoke_with_tools("Hello", tools=[])

    def test_invoke_with_tools_rate_limit_error(self, mock_provider):
        """Should raise AIRateLimitError on rate limit in invoke_with_tools."""
        provider, _ = mock_provider

        mock_langgraph = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langgraph": mock_langgraph,
                "langgraph.prebuilt": mock_langgraph.prebuilt,
            },
        ):
            mock_agent = MagicMock()
            mock_langgraph.prebuilt.create_react_agent.return_value = mock_agent
            mock_agent.invoke.side_effect = Exception("Rate limit reached")

            with pytest.raises(AIRateLimitError, match="Rate limit exceeded"):
                provider.invoke_with_tools("Hello", tools=[])

    def test_invoke_with_tools_network_error(self, mock_provider):
        """Should raise AINetworkError on network failure in invoke_with_tools."""
        provider, _ = mock_provider

        mock_langgraph = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langgraph": mock_langgraph,
                "langgraph.prebuilt": mock_langgraph.prebuilt,
            },
        ):
            mock_agent = MagicMock()
            mock_langgraph.prebuilt.create_react_agent.return_value = mock_agent
            mock_agent.invoke.side_effect = Exception("Network timeout occurred")

            with pytest.raises(AINetworkError, match="Network error"):
                provider.invoke_with_tools("Hello", tools=[])

    def test_invoke_with_tools_generic_error(self, mock_provider):
        """Should raise AIProviderError for other errors in invoke_with_tools."""
        provider, _ = mock_provider

        mock_langgraph = MagicMock()
        with patch.dict(
            "sys.modules",
            {
                "langgraph": mock_langgraph,
                "langgraph.prebuilt": mock_langgraph.prebuilt,
            },
        ):
            mock_agent = MagicMock()
            mock_langgraph.prebuilt.create_react_agent.return_value = mock_agent
            mock_agent.invoke.side_effect = Exception("Something went wrong")

            with pytest.raises(AIProviderError, match="Provider error during tool invocation"):
                provider.invoke_with_tools("Hello", tools=[])
