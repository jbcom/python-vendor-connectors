"""AI framework tools for HashiCorp Vault operations.

This module provides tools for Vault operations that work with multiple
AI agent frameworks.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

# =============================================================================
# Input Schemas
# =============================================================================


class ReadSecretSchema(BaseModel):
    """Schema for reading a Vault secret."""

    path: str = Field(..., description="The path to the secret in Vault.")
    mount_point: str = Field("secret", description="The KV engine mount point.")


class WriteSecretSchema(BaseModel):
    """Schema for writing a Vault secret."""

    path: str = Field(..., description="The path to write the secret to.")
    data: dict[str, Any] = Field(..., description="The secret data to write (key-value pairs).")
    mount_point: str = Field("secret", description="The KV engine mount point.")


class ListSecretsSchema(BaseModel):
    """Schema for listing Vault secrets."""

    root_path: str = Field("/", description="The starting path for recursive listing.")
    mount_point: str = Field("secret", description="The KV engine mount point.")
    max_depth: Optional[int] = Field(None, description="Maximum directory depth to traverse.")


class GenerateAWSCredentialsSchema(BaseModel):
    """Schema for generating AWS credentials via Vault."""

    role_name: str = Field(..., description="The AWS role name configured in Vault.")
    mount_point: str = Field("aws", description="The AWS secrets engine mount point.")
    ttl: Optional[str] = Field(None, description="Optional TTL for the credentials (e.g., '1h').")


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def vault_read_secret(
    path: str,
    mount_point: str = "secret",
) -> Optional[dict[str, Any]]:
    """Read a secret from HashiCorp Vault.

    Args:
        path: Secret path.
        mount_point: KV engine mount point.

    Returns:
        Secret data or None if not found.
    """
    from vendor_connectors.vault import VaultConnector

    connector = VaultConnector()
    return connector.read_secret(path=path, mount_point=mount_point)


def vault_write_secret(
    path: str,
    data: dict[str, Any],
    mount_point: str = "secret",
) -> bool:
    """Write a secret to HashiCorp Vault.

    Args:
        path: Secret path.
        data: Secret data.
        mount_point: KV engine mount point.

    Returns:
        True if successful.
    """
    from vendor_connectors.vault import VaultConnector

    connector = VaultConnector()
    return connector.write_secret(path=path, data=data, mount_point=mount_point)


def vault_list_secrets(
    root_path: str = "/",
    mount_point: str = "secret",
    max_depth: Optional[int] = None,
) -> dict[str, dict[str, Any]]:
    """List secrets recursively from HashiCorp Vault.

    Args:
        root_path: Starting path.
        mount_point: KV engine mount point.
        max_depth: Max depth to traverse.

    Returns:
        Dict mapping paths to secret data.
    """
    from vendor_connectors.vault import VaultConnector

    connector = VaultConnector()
    return connector.list_secrets(root_path=root_path, mount_point=mount_point, max_depth=max_depth)


def vault_generate_aws_credentials(
    role_name: str,
    mount_point: str = "aws",
    ttl: Optional[str] = None,
) -> dict[str, Any]:
    """Generate dynamic AWS credentials via Vault's AWS secrets engine.

    Args:
        role_name: AWS role name in Vault.
        mount_point: AWS engine mount point.
        ttl: Optional TTL.

    Returns:
        Generated credentials (access_key, secret_key, session_token).
    """
    from vendor_connectors.vault import VaultConnector

    connector = VaultConnector()
    return connector.generate_aws_credentials(role_name=role_name, mount_point=mount_point, ttl=ttl)


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "vault_read_secret",
        "description": "Read a secret from HashiCorp Vault KV v2 engine.",
        "func": vault_read_secret,
        "args_schema": ReadSecretSchema,
    },
    {
        "name": "vault_write_secret",
        "description": "Write or update a secret in HashiCorp Vault KV v2 engine.",
        "func": vault_write_secret,
        "args_schema": WriteSecretSchema,
    },
    {
        "name": "vault_list_secrets",
        "description": "Recursively list secrets from HashiCorp Vault.",
        "func": vault_list_secrets,
        "args_schema": ListSecretsSchema,
    },
    {
        "name": "vault_generate_aws_credentials",
        "description": "Generate dynamic, short-lived AWS credentials using Vault.",
        "func": vault_generate_aws_credentials,
        "args_schema": GenerateAWSCredentialsSchema,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all Vault tools as LangChain StructuredTools."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as e:
        raise ImportError("langchain-core is required for LangChain tools.") from e

    return [
        StructuredTool.from_function(
            func=defn["func"],
            name=defn["name"],
            description=defn["description"],
            args_schema=defn.get("args_schema"),
        )
        for defn in TOOL_DEFINITIONS
    ]


def get_crewai_tools() -> list[Any]:
    """Get all Vault tools as CrewAI tools."""
    try:
        from crewai.tools import tool as crewai_tool
    except ImportError as e:
        raise ImportError("crewai is required for CrewAI tools.") from e

    tools = []
    for defn in TOOL_DEFINITIONS:
        wrapped = crewai_tool(defn["name"])(defn["func"])
        wrapped.description = defn["description"]
        if "args_schema" in defn:
            wrapped.args_schema = defn["args_schema"]
        tools.append(wrapped)

    return tools


def get_strands_tools() -> list[Any]:
    """Get all Vault tools as plain Python functions."""
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get Vault tools for the specified or auto-detected framework."""
    from vendor_connectors._compat import is_available

    if framework == "auto":
        if is_available("crewai"):
            return get_crewai_tools()
        if is_available("langchain_core"):
            return get_langchain_tools()
        return get_strands_tools()

    if framework == "langchain":
        return get_langchain_tools()
    if framework == "crewai":
        return get_crewai_tools()
    if framework in ("strands", "functions"):
        return get_strands_tools()

    raise ValueError(f"Unknown framework: {framework}")


__all__ = [
    "get_tools",
    "get_langchain_tools",
    "get_crewai_tools",
    "get_strands_tools",
    "vault_read_secret",
    "vault_write_secret",
    "vault_list_secrets",
    "vault_generate_aws_credentials",
    "TOOL_DEFINITIONS",
]
