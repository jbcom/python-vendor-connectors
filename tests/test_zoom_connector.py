"""Tests for ZoomConnector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from vendor_connectors.zoom import ZoomConnector


class TestZoomConnector:
    """Test suite for ZoomConnector."""

    def test_init(self, base_connector_kwargs):
        """Test initialization."""
        connector = ZoomConnector(
            client_id="test-client-id",
            client_secret="test-client-secret",
            account_id="test-account-id",
            **base_connector_kwargs,
        )

        assert connector.client_id == "test-client-id"
        assert connector.client_secret == "test-client-secret"
        assert connector.account_id == "test-account-id"

    @patch("httpx.post")
    def test_get_access_token_success(self, mock_post, base_connector_kwargs):
        """Test successful access token retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "test-access-token"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        connector = ZoomConnector(
            client_id="test-client-id",
            client_secret="test-client-secret",
            account_id="test-account-id",
            **base_connector_kwargs,
        )

        token = connector.get_access_token()
        assert token == "test-access-token"
        mock_post.assert_called_once()

    @patch("httpx.post")
    def test_get_access_token_failure(self, mock_post, base_connector_kwargs):
        """Test failed access token retrieval."""
        import httpx

        mock_post.side_effect = httpx.HTTPError("Connection error")

        connector = ZoomConnector(
            client_id="test-client-id",
            client_secret="test-client-secret",
            account_id="test-account-id",
            **base_connector_kwargs,
        )

        with pytest.raises(RuntimeError, match="Failed to get Zoom access token"):
            connector.get_access_token()

    @patch("vendor_connectors.zoom.ZoomConnector.request")
    def test_get_zoom_users(self, mock_request, base_connector_kwargs):
        """Test getting Zoom users."""
        mock_users_response = MagicMock()
        mock_users_response.json.return_value = {
            "users": [
                {"email": "user1@example.com", "id": "123", "first_name": "User", "last_name": "One"},
                {"email": "user2@example.com", "id": "456", "first_name": "User", "last_name": "Two"},
            ],
            "next_page_token": None,
        }
        mock_request.return_value = mock_users_response

        connector = ZoomConnector(
            client_id="test-client-id",
            client_secret="test-client-secret",
            account_id="test-account-id",
            **base_connector_kwargs,
        )

        users = connector.get_zoom_users()
        assert "user1@example.com" in users
        assert "user2@example.com" in users
        assert len(users) == 2

    @patch("vendor_connectors.zoom.ZoomConnector.request")
    def test_create_zoom_user(self, mock_request, base_connector_kwargs):
        """Test creating a Zoom user."""
        mock_create_response = MagicMock()
        mock_request.return_value = mock_create_response

        connector = ZoomConnector(
            client_id="test-client-id",
            client_secret="test-client-secret",
            account_id="test-account-id",
            **base_connector_kwargs,
        )

        from vendor_connectors.zoom import CreateZoomUserSchema

        result = connector.create_zoom_user(
            CreateZoomUserSchema(email="newuser@example.com", first_name="New", last_name="User")
        )
        assert result is True
        mock_request.assert_called_once()

    def test_get_vercel_ai_tools(self, base_connector_kwargs):
        """Test getting Vercel AI tool definitions."""
        connector = ZoomConnector(
            client_id="test-client-id",
            client_secret="test-client-secret",
            account_id="test-account-id",
            **base_connector_kwargs,
        )

        tools = connector.get_vercel_ai_tools()
        assert len(tools) == 3
        assert tools[0]["function"]["name"] == "create_zoom_user"
        assert tools[1]["function"]["name"] == "remove_zoom_user"
        assert tools[2]["function"]["name"] == "get_zoom_user"
        assert "email" in tools[0]["function"]["parameters"]["properties"]
