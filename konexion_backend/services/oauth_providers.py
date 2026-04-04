"""
OAuth provider registry for Google and Microsoft.

Each provider entry contains everything authlib needs to build the authorization
URL and exchange the authorization code for tokens.  Adding a new OIDC provider
in the future only requires a new entry here and the corresponding env vars.
"""

from typing import Any

from authlib.integrations.starlette_client import OAuth

from konexion_backend.config import get_oauth_config

# Known provider metadata
_PROVIDER_META: dict[str, dict[str, Any]] = {
    "google": {
        "name": "Google",
        "icon_hint": "google",
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "client_kwargs": {
            "scope": "openid email profile",
        },
    },
    "microsoft": {
        "name": "Microsoft",
        "icon_hint": "microsoft",
        # tenant_id is injected at registration time
        "server_metadata_url_template": (
            "https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration"
        ),
        "client_kwargs": {
            "scope": "openid email profile",
        },
    },
}

# Module-level OAuth registry (populated on first import)
oauth = OAuth()
_registered: set[str] = set()


def _register_providers() -> None:
    """Register all enabled providers with the authlib OAuth registry."""
    cfg = get_oauth_config()

    for provider in cfg.enabled_providers:
        if provider in _registered:
            continue

        meta = _PROVIDER_META.get(provider)
        if meta is None:
            continue  # Unknown provider — skip silently

        if provider == "google":
            if not cfg.google_client_id or not cfg.google_client_secret:
                continue  # Credentials not configured
            oauth.register(
                name="google",
                client_id=cfg.google_client_id,
                client_secret=cfg.google_client_secret,
                server_metadata_url=meta["server_metadata_url"],
                client_kwargs=meta["client_kwargs"],
            )
            _registered.add("google")

        elif provider == "microsoft":
            if not cfg.microsoft_client_id or not cfg.microsoft_client_secret:
                continue
            ms_metadata_url = meta["server_metadata_url_template"].format(tenant_id=cfg.microsoft_tenant_id)
            oauth.register(
                name="microsoft",
                client_id=cfg.microsoft_client_id,
                client_secret=cfg.microsoft_client_secret,
                server_metadata_url=ms_metadata_url,
                client_kwargs=meta["client_kwargs"],
            )
            _registered.add("microsoft")


# Register on import
_register_providers()


def get_oauth_client(provider: str):
    """
    Return the authlib OAuth client for a given provider name.
    Raises KeyError if the provider is unknown or not registered.
    """
    if provider not in _registered:
        raise KeyError(f"OAuth provider '{provider}' is not registered or not configured.")
    return getattr(oauth, provider)


def get_enabled_providers() -> list[dict[str, str]]:
    """
    Return a list of enabled provider descriptors safe for frontend consumption.
    Only providers that are both configured in ENABLED_PROVIDERS *and* have
    credentials set are included.
    """
    return [
        {
            "id": p,
            "name": _PROVIDER_META[p]["name"],
            "icon_hint": _PROVIDER_META[p]["icon_hint"],
        }
        for p in _registered
        if p in _PROVIDER_META
    ]


def is_valid_provider(provider: str) -> bool:
    """Return True if the provider is registered and ready to use."""
    return provider in _registered


def get_redirect_uri(provider: str) -> str:
    """Return the configured redirect URI for a provider."""
    cfg = get_oauth_config()
    if provider == "google":
        return cfg.google_redirect_uri
    if provider == "microsoft":
        return cfg.microsoft_redirect_uri
    raise ValueError(f"No redirect URI configured for provider: {provider}")
