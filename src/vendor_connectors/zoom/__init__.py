"""Zoom Connector using jbcom ecosystem packages."""

from __future__ import annotations

import base64
from typing import Any, Optional

from lifecyclelogging import Logging
from pydantic import BaseModel, Field

from vendor_connectors.base import VendorConnectorBase


class CreateZoomUserSchema(BaseModel):
    """Pydantic schema for creating a Zoom user."""

    email: str = Field(..., description="The email address of the user to create.")
    first_name: str = Field(..., description="The first name of the user.")
    last_name: str = Field(..., description="The last name of the user.")


class RemoveZoomUserSchema(BaseModel):
    """Pydantic schema for removing a Zoom user."""

    email: str = Field(..., description="The email address of the user to remove.")


class GetZoomUserSchema(BaseModel):
    """Pydantic schema for getting a Zoom user."""

    email: str = Field(..., description="The email address of the user to get.")


class ZoomConnector(VendorConnectorBase):
    """Zoom connector for user management.

    Attributes:
        BASE_URL: Zoom API base URL.
    """

    BASE_URL = "https://api.zoom.us/v2"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        account_id: Optional[str] = None,
        logger: Optional[Logging] = None,
        **kwargs,
    ):
        super().__init__(logger=logger, **kwargs)
        self.errors: list[str] = []  # Track errors for programmatic access

        self.client_id = client_id or self.get_input("ZOOM_CLIENT_ID", required=True)
        self.client_secret = client_secret or self.get_input("ZOOM_CLIENT_SECRET", required=True)
        self.account_id = account_id or self.get_input("ZOOM_ACCOUNT_ID", required=True)

        # Register tools
        self.register_pydantic_tool(self.create_zoom_user, CreateZoomUserSchema)
        self.register_pydantic_tool(self.remove_zoom_user, RemoveZoomUserSchema)
        self.register_pydantic_tool(self.get_zoom_user, GetZoomUserSchema)

    def get_access_token(self) -> str:
        """Get an OAuth access token from Zoom."""
        import httpx

        url = "https://zoom.us/oauth/token"
        auth_string = f"{self.client_id}:{self.client_secret}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(auth_string.encode()).decode()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "account_credentials", "account_id": self.account_id}

        try:
            # We use a direct httpx call here because this is for authentication
            # and doesn't use the base URL.
            response = httpx.post(url, headers=headers, data=data, timeout=30.0)
            response.raise_for_status()
            return response.json()["access_token"]
        except (httpx.HTTPError, KeyError) as exc:
            msg = f"Failed to get Zoom access token: {exc}"
            raise RuntimeError(msg) from exc

    def _build_headers(self) -> dict[str, str]:
        """Build request headers with Zoom OAuth token."""
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_zoom_users(self) -> dict[str, dict[str, Any]]:
        """Get all Zoom users."""
        users: dict[str, dict[str, Any]] = {}
        page_size = 300
        next_page_token = None

        while True:
            params: dict[str, Any] = {"page_size": page_size}
            if next_page_token:
                params["next_page_token"] = next_page_token

            response = self.get("/users", params=params)
            data = response.json()
            for user in data.get("users", []):
                users[user["email"]] = user

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

        return users

    def get_zoom_user(self, args: GetZoomUserSchema) -> Optional[dict[str, Any]]:
        """Get a Zoom user by email."""
        try:
            response = self.get(f"/users/{args.email}")
            return response.json()
        except Exception as exc:
            error_msg = f"Failed to get Zoom user {args.email}: {exc}"
            self.errors.append(error_msg)
            self.logger.error(error_msg)
            return None

    def remove_zoom_user(self, args: RemoveZoomUserSchema) -> None:
        """Remove a Zoom user."""
        try:
            self.delete(f"/users/{args.email}")
            self.logger.warning(f"Removed Zoom user {args.email}")
        except Exception as exc:
            error_msg = f"Failed to remove Zoom user {args.email}: {exc}"
            self.errors.append(error_msg)
            self.logger.error(error_msg)

    def create_zoom_user(self, args: CreateZoomUserSchema) -> bool:
        """Create a Zoom user with a paid license."""
        user_info = {
            "action": "create",
            "user_info": {
                "email": args.email,
                "type": 2,
                "first_name": args.first_name,
                "last_name": args.last_name,
            },
        }
        try:
            self.post("/users", json=user_info)
            self.logger.info(f"Created Zoom user {args.email}")
            return True
        except Exception as exc:
            error_msg = f"Failed to create Zoom user {args.email}: {exc}"
            self.errors.append(error_msg)
            self.logger.error(error_msg)
            return False
