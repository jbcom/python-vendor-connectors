"""Tests for AI connector LangSmith context manager."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch


class TestLangSmithContextManager:
    """Tests for LangSmith environment variable handling."""

    def test_langsmith_context_no_api_key(self):
        """Context manager should do nothing without API key."""
        from vendor_connectors.ai.connector import AIConnector

        # Mock the provider to avoid actual initialization
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(provider="anthropic", api_key="test-key")

            # Save original env state
            original_tracing = os.environ.get("LANGCHAIN_TRACING_V2")
            original_api_key = os.environ.get("LANGCHAIN_API_KEY")
            original_project = os.environ.get("LANGCHAIN_PROJECT")

            # Use context manager without LangSmith API key
            with connector._langsmith_context():
                # Environment should not be modified
                assert os.environ.get("LANGCHAIN_TRACING_V2") == original_tracing
                assert os.environ.get("LANGCHAIN_API_KEY") == original_api_key
                assert os.environ.get("LANGCHAIN_PROJECT") == original_project

    def test_langsmith_context_sets_and_restores_env_vars(self):
        """Context manager should temporarily set and restore environment variables."""
        from vendor_connectors.ai.connector import AIConnector

        # Mock the provider
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                provider="anthropic",
                api_key="test-key",
                langsmith_api_key="ls-test-key",
                langsmith_project="test-project",
            )

            # Clear environment first
            os.environ.pop("LANGCHAIN_TRACING_V2", None)
            os.environ.pop("LANGCHAIN_API_KEY", None)
            os.environ.pop("LANGCHAIN_PROJECT", None)

            # Before context
            assert "LANGCHAIN_TRACING_V2" not in os.environ
            assert "LANGCHAIN_API_KEY" not in os.environ
            assert "LANGCHAIN_PROJECT" not in os.environ

            # Inside context
            with connector._langsmith_context():
                assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
                assert os.environ["LANGCHAIN_API_KEY"] == "ls-test-key"
                assert os.environ["LANGCHAIN_PROJECT"] == "test-project"

            # After context - should be restored
            assert "LANGCHAIN_TRACING_V2" not in os.environ
            assert "LANGCHAIN_API_KEY" not in os.environ
            assert "LANGCHAIN_PROJECT" not in os.environ

    def test_langsmith_context_preserves_existing_env_vars(self):
        """Context manager should preserve existing environment variables."""
        from vendor_connectors.ai.connector import AIConnector

        # Mock the provider
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                provider="anthropic",
                api_key="test-key",
                langsmith_api_key="ls-test-key",
                langsmith_project="test-project",
            )

            # Set existing values
            os.environ["LANGCHAIN_TRACING_V2"] = "false"
            os.environ["LANGCHAIN_API_KEY"] = "original-key"
            os.environ["LANGCHAIN_PROJECT"] = "original-project"

            # Inside context - should be overridden
            with connector._langsmith_context():
                assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
                assert os.environ["LANGCHAIN_API_KEY"] == "ls-test-key"
                assert os.environ["LANGCHAIN_PROJECT"] == "test-project"

            # After context - should be restored to original
            assert os.environ["LANGCHAIN_TRACING_V2"] == "false"
            assert os.environ["LANGCHAIN_API_KEY"] == "original-key"
            assert os.environ["LANGCHAIN_PROJECT"] == "original-project"

            # Clean up
            os.environ.pop("LANGCHAIN_TRACING_V2", None)
            os.environ.pop("LANGCHAIN_API_KEY", None)
            os.environ.pop("LANGCHAIN_PROJECT", None)

    def test_langsmith_context_without_project(self):
        """Context manager should work without project name."""
        from vendor_connectors.ai.connector import AIConnector

        # Mock the provider
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                provider="anthropic",
                api_key="test-key",
                langsmith_api_key="ls-test-key",
                # No langsmith_project specified
            )

            # Clear environment
            os.environ.pop("LANGCHAIN_TRACING_V2", None)
            os.environ.pop("LANGCHAIN_API_KEY", None)
            os.environ.pop("LANGCHAIN_PROJECT", None)

            with connector._langsmith_context():
                assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
                assert os.environ["LANGCHAIN_API_KEY"] == "ls-test-key"
                # Project should not be set
                assert "LANGCHAIN_PROJECT" not in os.environ

            # After context
            assert "LANGCHAIN_TRACING_V2" not in os.environ
            assert "LANGCHAIN_API_KEY" not in os.environ

    def test_chat_uses_langsmith_context(self):
        """chat() method should use LangSmith context manager."""
        from vendor_connectors.ai.connector import AIConnector

        # Mock the provider
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            # Mock the chat method
            from vendor_connectors.ai.base import AIResponse

            mock_response = AIResponse(
                content="test response",
                model="test-model",
                provider="anthropic",
            )
            mock_provider_instance.chat.return_value = mock_response

            connector = AIConnector(
                provider="anthropic",
                api_key="test-key",
                langsmith_api_key="ls-test-key",
            )

            # Clear environment
            os.environ.pop("LANGCHAIN_TRACING_V2", None)
            os.environ.pop("LANGCHAIN_API_KEY", None)

            # Before chat
            assert "LANGCHAIN_TRACING_V2" not in os.environ

            # Call chat
            response = connector.chat("Hello")

            # After chat - environment should be restored
            assert "LANGCHAIN_TRACING_V2" not in os.environ
            assert "LANGCHAIN_API_KEY" not in os.environ
            assert response.content == "test response"

    def test_invoke_uses_langsmith_context(self):
        """invoke() method should use LangSmith context manager."""
        from vendor_connectors.ai.connector import AIConnector

        # Mock the provider
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            # Mock the provider's chat method
            from vendor_connectors.ai.base import AIResponse

            mock_response = AIResponse(
                content="test response",
                model="test-model",
                provider="anthropic",
            )
            mock_provider_instance.chat.return_value = mock_response

            connector = AIConnector(
                provider="anthropic",
                api_key="test-key",
                langsmith_api_key="ls-test-key",
            )

            # Clear environment
            os.environ.pop("LANGCHAIN_TRACING_V2", None)
            os.environ.pop("LANGCHAIN_API_KEY", None)

            # Before invoke
            assert "LANGCHAIN_TRACING_V2" not in os.environ

            # Call invoke (without tools, so it calls chat internally)
            response = connector.invoke("Hello", use_tools=False)

            # After invoke - environment should be restored
            assert "LANGCHAIN_TRACING_V2" not in os.environ
            assert "LANGCHAIN_API_KEY" not in os.environ
            assert response.content == "test response"
