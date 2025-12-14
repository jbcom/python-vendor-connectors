"""Custom exceptions for AI sub-package.

This module defines a hierarchy of exceptions for better error handling
in AI provider implementations.
"""

from __future__ import annotations

__all__ = [
    "AIError",
    "AIProviderError",
    "AIAuthenticationError",
    "AINetworkError",
    "AIParameterError",
    "AIRateLimitError",
    "AIModelError",
]


class AIError(Exception):
    """Base exception for all AI sub-package errors.

    This is the parent class for all AI-related exceptions.
    """

    pass


class AIProviderError(AIError):
    """Exception raised when a provider operation fails.

    This is a general exception for provider-level errors that don't
    fit into more specific categories.
    """

    pass


class AIAuthenticationError(AIError):
    """Exception raised when authentication fails.

    This includes invalid API keys, expired tokens, and other
    authentication-related failures.
    """

    pass


class AINetworkError(AIError):
    """Exception raised when network operations fail.

    This includes connection timeouts, DNS failures, and other
    network-related issues.
    """

    pass


class AIParameterError(AIError):
    """Exception raised when invalid parameters are provided.

    This includes invalid model names, out-of-range temperature values,
    and other parameter validation failures.
    """

    pass


class AIRateLimitError(AIError):
    """Exception raised when rate limits are exceeded.

    This indicates the provider's API rate limit has been reached.
    """

    pass


class AIModelError(AIError):
    """Exception raised when model operations fail.

    This includes invalid model names, model unavailability, and
    model-specific errors.
    """

    pass
