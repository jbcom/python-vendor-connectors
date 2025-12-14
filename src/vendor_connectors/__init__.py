"""Vendor Connectors - Universal vendor connectors for the jbcom ecosystem.

This package provides modular connectors for various cloud providers and services:
- Anthropic: Claude AI API and Agent SDK (NEW)
- AWS: Organizations, SSO/Identity Center, S3, Secrets Manager
- Cursor: Background Agent API for AI coding agents (NEW)
- Google Cloud: Workspace, Cloud Platform, Billing, Services (GKE, Compute, etc.)
- GitHub: Repository operations, PR management
- Meshy: 3D asset generation
- Slack: Channel and message operations
- Vault: HashiCorp Vault secret management
- Zoom: User and meeting management
- Meshy: AI 3D asset generation

Usage:
    # Basic connector (session management + secrets)
    from vendor_connectors import AWSConnector
    connector = AWSConnector()

    # Full connector with all operations
    from vendor_connectors.aws import AWSConnectorFull
    connector = AWSConnectorFull()
    accounts = connector.get_accounts()

    # Cursor AI agents
    from vendor_connectors.cursor import CursorConnector
    cursor = CursorConnector()
    agents = cursor.list_agents()

    # Anthropic Claude AI
    from vendor_connectors.anthropic import AnthropicConnector
    anthropic = AnthropicConnector()
    response = anthropic.create_message(...)

    # Mixin approach for custom connectors
    from vendor_connectors.aws import AWSConnector, AWSOrganizationsMixin

    class MyConnector(AWSConnector, AWSOrganizationsMixin):
        pass

    # Meshy AI 3D generation (functional interface)
    from vendor_connectors.meshy import text3d, image3d, rigging, animate

    model = text3d.generate("a medieval sword")
    rigged = rigging.rig(model.id)
    animated = animate.apply(rigged.id, animation_id=0)

    # AI tools for agents
    from vendor_connectors.meshy.tools import get_tools, get_crewai_tools
    from vendor_connectors.meshy.mcp import create_server, run_server
"""

from __future__ import annotations

__version__ = "0.2.0"

# Core imports (always available)
from vendor_connectors import meshy
from vendor_connectors.base import VendorConnectorBase
from vendor_connectors.cloud_params import (
    get_aws_call_params,
    get_cloud_call_params,
    get_google_call_params,
)
from vendor_connectors.connectors import VendorConnectors

# Connectors with no extra dependencies (always available)
from vendor_connectors.cursor import CursorConnector
from vendor_connectors.zoom import ZoomConnector

# Optional connectors - wrapped in try/except for graceful degradation
# These require optional dependencies: pip install vendor-connectors[<extra>]

# Anthropic connector (requires: pip install vendor-connectors[anthropic])
try:
    from vendor_connectors.anthropic import AnthropicConnector
except ImportError:
    AnthropicConnector = None  # type: ignore[misc, assignment]

# AWS connector (requires: pip install vendor-connectors[aws])
try:
    from vendor_connectors.aws import (
        AWSConnector,
        AWSConnectorFull,
        AWSOrganizationsMixin,
        AWSS3Mixin,
        AWSSSOmixin,
    )
except ImportError:
    AWSConnector = None  # type: ignore[misc, assignment]
    AWSConnectorFull = None  # type: ignore[misc, assignment]
    AWSOrganizationsMixin = None  # type: ignore[misc, assignment]
    AWSS3Mixin = None  # type: ignore[misc, assignment]
    AWSSSOmixin = None  # type: ignore[misc, assignment]

# GitHub connector (requires: pip install vendor-connectors[github])
try:
    from vendor_connectors.github import GithubConnector
except ImportError:
    GithubConnector = None  # type: ignore[misc, assignment]

# Google connector (requires: pip install vendor-connectors[google])
try:
    from vendor_connectors.google import (
        GoogleBillingMixin,
        GoogleCloudMixin,
        GoogleConnector,
        GoogleConnectorFull,
        GoogleServicesMixin,
        GoogleWorkspaceMixin,
    )
except ImportError:
    GoogleConnector = None  # type: ignore[misc, assignment]
    GoogleConnectorFull = None  # type: ignore[misc, assignment]
    GoogleWorkspaceMixin = None  # type: ignore[misc, assignment]
    GoogleCloudMixin = None  # type: ignore[misc, assignment]
    GoogleBillingMixin = None  # type: ignore[misc, assignment]
    GoogleServicesMixin = None  # type: ignore[misc, assignment]

# Slack connector (requires: pip install vendor-connectors[slack])
try:
    from vendor_connectors.slack import SlackConnector
except ImportError:
    SlackConnector = None  # type: ignore[misc, assignment]

# Vault connector (requires: pip install vendor-connectors[vault])
try:
    from vendor_connectors.vault import VaultConnector
except ImportError:
    VaultConnector = None  # type: ignore[misc, assignment]

__all__ = [
    # Base class for all connectors
    "VendorConnectorBase",
    # AI/Agent connectors
    "AnthropicConnector",
    "CursorConnector",
    # AWS
    "AWSConnector",
    "AWSConnectorFull",
    "AWSOrganizationsMixin",
    "AWSSSOmixin",
    "AWSS3Mixin",
    # Google
    "GoogleConnector",
    "GoogleConnectorFull",
    "GoogleWorkspaceMixin",
    "GoogleCloudMixin",
    "GoogleBillingMixin",
    "GoogleServicesMixin",
    # Other connectors
    "GithubConnector",
    "SlackConnector",
    "VaultConnector",
    "ZoomConnector",
    "VendorConnectors",
    # Cloud param utilities
    "get_cloud_call_params",
    "get_aws_call_params",
    "get_google_call_params",
    # Meshy AI (3D asset generation) - functional interface
    "meshy",
]
