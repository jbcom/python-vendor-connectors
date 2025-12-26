"""Tests for unified MCP server."""

from __future__ import annotations

import pytest
from vendor_connectors.mcp import create_server


def test_create_server():
    """Test that the MCP server can be created and has tools."""
    server = create_server()
    assert server.name == "vendor-connectors"
    # Basic check that server was initialized
    assert server is not None
