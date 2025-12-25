"""Unified CLI for Vendor Connectors.

This module provides a command-line interface to all vendor connectors
using the central registry for discovery.

Usage:
    # List available connectors
    vendor-connectors list

    # Call any connector method
    vendor-connectors call <connector> <method> [--arg value ...]

    # Interactive mode
    vendor-connectors shell

    # Start MCP server
    vendor-connectors mcp

    # Specific connector shortcuts (if implemented)
    vendor-connectors jules sources
    vendor-connectors cursor agents
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from vendor_connectors.registry import (
    get_connector,
    get_connector_class,
    list_connector_info,
)


def _json_output(data: Any) -> str:
    """Format data as JSON for output."""
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "__iter__") and not isinstance(data, (str, dict)):
        data = [d.model_dump() if hasattr(d, "model_dump") else d for d in data]
    return json.dumps(data, indent=2, default=str)


def _parse_arg_value(value: str) -> Any:
    """Parse a CLI argument value, attempting JSON decode."""
    # Try JSON first
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass

    # Try common conversions
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    return value


# =============================================================================
# Commands
# =============================================================================


def cmd_list(args: argparse.Namespace) -> int:
    """List available connectors."""
    info = list_connector_info()

    if args.json:
        print(_json_output(info))
        return 0

    print("Available connectors:")
    print("-" * 70)
    print(f"{'Name':<15} {'Class':<25} {'Env Var':<25}")
    print("-" * 70)

    for c in info:
        env = c.get("api_key_env") or "-"
        env_set = "✓" if os.environ.get(env) else " "
        print(f"{c['name']:<15} {c['class']:<25} [{env_set}] {env}")

    print("-" * 70)
    print("\nUsage: vendor-connectors call <connector> <method> [--arg value ...]")
    return 0


def cmd_call(args: argparse.Namespace) -> int:
    """Call a connector method."""
    connector_name = args.connector
    method_name = args.method

    # Parse extra arguments
    kwargs = {}
    extra = args.extra or []
    i = 0
    while i < len(extra):
        arg = extra[i]
        if arg.startswith("--"):
            key = arg[2:].replace("-", "_")
            if i + 1 < len(extra) and not extra[i + 1].startswith("--"):
                kwargs[key] = _parse_arg_value(extra[i + 1])
                i += 2
            else:
                kwargs[key] = True
                i += 1
        else:
            i += 1

    try:
        connector = get_connector(connector_name)
        method = getattr(connector, method_name, None)

        if method is None:
            print(f"Error: Method '{method_name}' not found on {connector_name}")
            return 1

        result = method(**kwargs)
        print(_json_output(result))
        return 0

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


def cmd_methods(args: argparse.Namespace) -> int:
    """List methods for a connector."""
    connector_name = args.connector

    try:
        cls = get_connector_class(connector_name)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Methods for {connector_name}:")
    print("-" * 60)

    for name in sorted(dir(cls)):
        if name.startswith("_"):
            continue
        attr = getattr(cls, name, None)
        if not callable(attr) or isinstance(attr, type):
            continue

        # Get first line of docstring
        doc = ""
        if attr.__doc__:
            doc = attr.__doc__.split("\n")[0].strip()[:50]

        print(f"  {name:<30} {doc}")

    print("-" * 60)
    print(f"\nUsage: vendor-connectors call {connector_name} <method> [--arg value ...]")
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    """Start MCP server."""
    from vendor_connectors.mcp import main as mcp_main

    return mcp_main()


def cmd_info(args: argparse.Namespace) -> int:
    """Show info about a specific connector."""
    from vendor_connectors.registry import get_connector_info

    try:
        info = get_connector_info(args.connector)
        print(_json_output(info))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


# =============================================================================
# Main CLI
# =============================================================================


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vendor-connectors",
        description="Unified CLI for all vendor connectors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vendor-connectors list                    # List all connectors
  vendor-connectors methods jules           # List Jules methods
  vendor-connectors call jules list_sources # Call a method
  vendor-connectors call cursor list_agents
  vendor-connectors mcp                     # Start MCP server
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List available connectors")
    list_parser.add_argument("--json", action="store_true", help="JSON output")
    list_parser.set_defaults(func=cmd_list)

    # Methods command
    methods_parser = subparsers.add_parser("methods", help="List methods for a connector")
    methods_parser.add_argument("connector", help="Connector name")
    methods_parser.set_defaults(func=cmd_methods)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show connector info")
    info_parser.add_argument("connector", help="Connector name")
    info_parser.set_defaults(func=cmd_info)

    # Call command
    call_parser = subparsers.add_parser("call", help="Call a connector method")
    call_parser.add_argument("connector", help="Connector name")
    call_parser.add_argument("method", help="Method name")
    call_parser.add_argument("extra", nargs="*", help="Method arguments (--arg value)")
    call_parser.set_defaults(func=cmd_call)

    # MCP command
    mcp_parser = subparsers.add_parser("mcp", help="Start MCP server")
    mcp_parser.set_defaults(func=cmd_mcp)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if hasattr(args, "func"):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            return 130
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
