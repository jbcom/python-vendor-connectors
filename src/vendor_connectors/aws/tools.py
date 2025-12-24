"""AI framework tools for AWS operations.

This module provides tools for AWS operations that work with multiple
AI agent frameworks. The core functions are framework-agnostic Python functions,
with native wrappers for each supported framework.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Input Schemas
# =============================================================================


class ListSecretsSchema(BaseModel):
    """Schema for listing AWS secrets."""

    prefix: str = Field("", description="Filter secrets by name prefix.")
    max_results: int = Field(100, description="Maximum number of secrets to return.")


class GetSecretSchema(BaseModel):
    """Schema for getting an AWS secret."""

    secret_name: str = Field(..., description="Name or ARN of the secret.")


class ListS3ObjectsSchema(BaseModel):
    """Schema for listing S3 objects."""

    bucket_name: str = Field(..., description="Name of the S3 bucket.")
    prefix: str = Field("", description="Filter objects by key prefix.")
    max_keys: int = Field(100, description="Maximum number of objects to return.")


class GetS3ObjectSchema(BaseModel):
    """Schema for getting an S3 object."""

    bucket_name: str = Field(..., description="Name of the S3 bucket.")
    key: str = Field(..., description="Object key (path).")


# =============================================================================
# Tool Implementation Functions
# =============================================================================


def list_secrets(
    prefix: str = "",
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List secrets in AWS Secrets Manager.

    Args:
        prefix: Filter secrets by name prefix
        max_results: Maximum number of secrets to return

    Returns:
        List of secret metadata (name, arn, description, last_changed_date)
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()
    secrets = connector.list_secrets(prefix=prefix if prefix else None)

    # Limit results
    result = []
    for name, data in list(secrets.items())[:max_results]:
        result.append(
            {
                "name": name,
                "arn": data.get("arn") or data.get("ARN", ""),
                "description": data.get("description") or data.get("Description", ""),
                "last_changed_date": str(data.get("last_changed_date") or data.get("LastChangedDate", "")),
            }
        )

    return result


def get_secret(
    secret_name: str,
) -> dict[str, Any]:
    """Get a secret value from AWS Secrets Manager.

    Args:
        secret_name: Name or ARN of the secret

    Returns:
        Dict with secret_name, secret_value, and version_id
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()
    value = connector.get_secret(secret_name)

    return {
        "secret_name": secret_name,
        "secret_value": value,
        "status": "retrieved",
    }


def list_s3_buckets() -> list[dict[str, str]]:
    """List S3 buckets in the AWS account.

    Returns:
        List of bucket info (name, creation_date, region)
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()
    buckets = connector.list_s3_buckets()

    result = []
    for name, data in buckets.items():
        result.append(
            {
                "name": name,
                "creation_date": str(data.get("creation_date") or data.get("CreationDate", "")),
                "region": data.get("region", "unknown"),
            }
        )

    return result


def list_s3_objects(
    bucket_name: str,
    prefix: str = "",
    max_keys: int = 100,
) -> list[dict[str, Any]]:
    """List objects in an S3 bucket.

    Args:
        bucket_name: Name of the S3 bucket
        prefix: Filter objects by key prefix
        max_keys: Maximum number of objects to return

    Returns:
        List of object info (key, size, last_modified, storage_class)
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()
    objects = connector.list_objects(
        bucket_name=bucket_name,
        prefix=prefix if prefix else None,
        max_keys=max_keys,
    )

    result = []
    for key, data in objects.items():
        result.append(
            {
                "key": key,
                "size": data.get("size") or data.get("Size", 0),
                "last_modified": str(data.get("last_modified") or data.get("LastModified", "")),
                "storage_class": data.get("storage_class") or data.get("StorageClass", "STANDARD"),
            }
        )

    return result


def get_s3_object(
    bucket_name: str,
    key: str,
) -> dict[str, Any]:
    """Get an object from S3.

    Args:
        bucket_name: Name of the S3 bucket
        key: Object key (path)

    Returns:
        Dict with bucket, key, content_type, size, and body (for text) or status
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()
    obj = connector.get_object(bucket_name=bucket_name, key=key)

    result = {
        "bucket": bucket_name,
        "key": key,
        "content_type": obj.get("content_type") or obj.get("ContentType", ""),
        "size": obj.get("content_length") or obj.get("ContentLength", 0),
    }

    # Include body for text content types
    content_type = result["content_type"]
    if content_type and ("text" in content_type or "json" in content_type or "xml" in content_type):
        body = obj.get("body")
        if body and hasattr(body, "read"):
            result["body"] = body.read().decode("utf-8")
        elif isinstance(body, (str, bytes)):
            result["body"] = body if isinstance(body, str) else body.decode("utf-8")

    return result


def list_accounts() -> list[dict[str, Any]]:
    """List AWS accounts in the organization.

    Returns:
        List of account info (id, name, email, status)
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()

    try:
        accounts = connector.get_accounts()
    except Exception:
        # Fall back to organization accounts if Control Tower not available
        accounts = connector.get_organization_accounts()

    result = []
    for account_id, data in accounts.items():
        result.append(
            {
                "id": account_id,
                "name": data.get("name") or data.get("Name", ""),
                "email": data.get("email") or data.get("Email", ""),
                "status": data.get("status") or data.get("Status", "ACTIVE"),
            }
        )

    return result


def list_sso_users(
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List users in IAM Identity Center (SSO).

    Args:
        max_results: Maximum number of users to return

    Returns:
        List of user info (user_id, user_name, display_name, email)
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()
    users = connector.list_sso_users(unhump_users=True)

    result = []
    for user_id, data in list(users.items())[:max_results]:
        result.append(
            {
                "user_id": user_id,
                "user_name": data.get("user_name", ""),
                "display_name": data.get("display_name", ""),
                "email": data.get("primary_email", {}).get("value", "")
                if isinstance(data.get("primary_email"), dict)
                else "",
            }
        )

    return result


def list_sso_groups(
    max_results: int = 100,
) -> list[dict[str, Any]]:
    """List groups in IAM Identity Center (SSO).

    Args:
        max_results: Maximum number of groups to return

    Returns:
        List of group info (group_id, display_name, description, member_count)
    """
    from vendor_connectors.aws import AWSConnectorFull

    connector = AWSConnectorFull()
    groups = connector.list_sso_groups(unhump_groups=True)

    result = []
    for group_id, data in list(groups.items())[:max_results]:
        members = data.get("members", [])
        result.append(
            {
                "group_id": group_id,
                "display_name": data.get("display_name", ""),
                "description": data.get("description", ""),
                "member_count": len(members) if isinstance(members, list) else 0,
            }
        )

    return result


# =============================================================================
# Tool Definitions
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "aws_list_secrets",
        "description": "List secrets in AWS Secrets Manager. Returns secret names, ARNs, and metadata.",
        "func": list_secrets,
        "args_schema": ListSecretsSchema,
    },
    {
        "name": "aws_get_secret",
        "description": "Get a secret value from AWS Secrets Manager by name or ARN.",
        "func": get_secret,
        "args_schema": GetSecretSchema,
    },
    {
        "name": "aws_list_s3_buckets",
        "description": "List S3 buckets in the AWS account with their creation dates and regions.",
        "func": list_s3_buckets,
    },
    {
        "name": "aws_list_s3_objects",
        "description": "List objects in an S3 bucket with optional prefix filter.",
        "func": list_s3_objects,
        "args_schema": ListS3ObjectsSchema,
    },
    {
        "name": "aws_get_s3_object",
        "description": "Get an object from S3. Returns metadata and content for text files.",
        "func": get_s3_object,
        "args_schema": GetS3ObjectSchema,
    },
    {
        "name": "aws_list_accounts",
        "description": "List AWS accounts in the organization with their names and emails.",
        "func": list_accounts,
    },
    {
        "name": "aws_list_sso_users",
        "description": "List users in IAM Identity Center (AWS SSO) with their details.",
        "func": list_sso_users,
    },
    {
        "name": "aws_list_sso_groups",
        "description": "List groups in IAM Identity Center (AWS SSO) with member counts.",
        "func": list_sso_groups,
    },
]


# =============================================================================
# Framework-Specific Getters
# =============================================================================


def get_langchain_tools() -> list[Any]:
    """Get all AWS tools as LangChain StructuredTools.

    Returns:
        List of LangChain StructuredTool objects.

    Raises:
        ImportError: If langchain-core is not installed.
    """
    try:
        from langchain_core.tools import StructuredTool
    except ImportError as e:
        raise ImportError(
            "langchain-core is required for LangChain tools.\nInstall with: pip install vendor-connectors[langchain]"
        ) from e

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
    """Get all AWS tools as CrewAI tools.

    Returns:
        List of CrewAI BaseTool objects.

    Raises:
        ImportError: If crewai is not installed.
    """
    try:
        from crewai.tools import tool as crewai_tool
    except ImportError as e:
        raise ImportError(
            "crewai is required for CrewAI tools.\nInstall with: pip install vendor-connectors[crewai]"
        ) from e

    tools = []
    for defn in TOOL_DEFINITIONS:
        wrapped = crewai_tool(defn["name"])(defn["func"])
        wrapped.description = defn["description"]
        if "args_schema" in defn:
            wrapped.args_schema = defn["args_schema"]
        tools.append(wrapped)

    return tools


def get_strands_tools() -> list[Any]:
    """Get all AWS tools as plain Python functions for AWS Strands.

    Returns:
        List of callable functions.
    """
    return [defn["func"] for defn in TOOL_DEFINITIONS]


def get_tools(framework: str = "auto") -> list[Any]:
    """Get AWS tools for the specified or auto-detected framework.

    Args:
        framework: Framework to use. Options:
            - "auto" (default): Auto-detect based on installed packages
            - "langchain": Force LangChain StructuredTools
            - "crewai": Force CrewAI tools
            - "strands": Force plain functions for Strands
            - "functions": Force plain functions (alias for strands)

    Returns:
        List of tools in the appropriate format for the framework.

    Raises:
        ImportError: If the requested framework is not installed.
        ValueError: If an unknown framework is specified.
    """
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

    raise ValueError(f"Unknown framework: {framework}. Options: auto, langchain, crewai, strands, functions")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Framework-specific getters
    "get_tools",
    "get_langchain_tools",
    "get_crewai_tools",
    "get_strands_tools",
    # Raw functions
    "list_secrets",
    "get_secret",
    "list_s3_buckets",
    "list_s3_objects",
    "get_s3_object",
    "list_accounts",
    "list_sso_users",
    "list_sso_groups",
    # Tool metadata
    "TOOL_DEFINITIONS",
]
