"""Tests for unified CLI."""

from __future__ import annotations

import argparse
from unittest.mock import patch
from vendor_connectors.cli import cmd_list, main


def test_cli_list():
    """Test the list command."""
    args = argparse.Namespace(json=False)
    with patch("builtins.print") as mock_print:
        exit_code = cmd_list(args)
        assert exit_code == 0
        mock_print.assert_called()
        # Verify it lists some connectors
        output = "\n".join(call.args[0] for call in mock_print.call_args_list if call.args)
        assert "aws" in output
        assert "github" in output
        assert "google" in output


def test_cli_main_help():
    """Test main CLI entry point with help."""
    with patch("sys.argv", ["vendor-connectors", "--help"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


import pytest
