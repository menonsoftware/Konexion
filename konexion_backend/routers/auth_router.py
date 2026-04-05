"""
Auth router — all endpoints under /api/auth.

Endpoints:
  GET  /api/auth/providers               — list enabled providers (public)
  GET  /api/auth/{provider}/login        — start OAuth2 flow
  GET  /api/auth/{provider}/callback     — handle authorization code callback
  GET  /api/auth/me                      — current user info (protected)
  POST /api/auth/refresh                 — rotate refresh token
  POST /api/auth/logout                  — revoke refresh token + clear cookies
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from konexion_backend.config import get_oauth_config
from konexion_backend.dependencies.auth import _get_db_session, get_current_user
from konexion_backend.models.db_model import database
from konexion_backend.models.user_model import OAuthAccount, RefreshToken, User
from konexion_backend.services.auth_service import (
    clear_auth_cookies,
    create_access_token,
    create_and_store_refresh_token,
    hash_token,
    set_auth_cookies,
    upsert_user_from_oauth,
)
from konexion_backend.services.oauth_providers import (
    get_authorize_token_kwargs,
    get_enabled_providers,
    get_oauth_client,
    get_redirect_uri,
    is_valid_provider,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Public: provider list ──────────────────────────────────────────────────────


@router.get("/providers")
async def list_providers():
    """Return the list of configured and enabled OAuth providers."""
    return {"providers": get_enabled_providers()}


# ── OAuth2 initiation ──────────────────────────────────────────────────────────


@router.get("/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """Redirect the browser to the OAuth provider's authorization endpoint."""
    if not is_valid_provider(provider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown or unconfigured provider: '{provider}'",
        )

    client = get_oauth_client(provider)
    redirect_uri = get_redirect_uri(provider)
    return await client.authorize_redirect(request, redirect_uri)


# ── OAuth2 callback ────────────────────────────────────────────────────────────


@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request):
    """
    Handle the authorization code callback from an OAuth provider.
    Exchanges the code for tokens, validates the ID token, upserts the user,
    issues HttpOnly cookies, and redirects to the frontend.
    """
    if not is_valid_provider(provider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown or unconfigured provider: '{provider}'",
        )

    client = get_oauth_client(provider)

    try:
        token = await client.authorize_access_token(request, **get_authorize_token_kwargs(provider))
    except Exception as exc:
        logger.warning("OAuth token exchange failed for %s: %s", provider, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth authorization failed. Please try again.",
        ) from exc

    # authlib populates `userinfo` from the ID token for OIDC providers
    userinfo = token.get("userinfo")
    if not userinfo:
        try:
            userinfo = await client.userinfo(token=token)
        except Exception as exc:
            logger.warning("Failed to fetch userinfo for %s: %s", provider, exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve user information from provider.",
            ) from exc

    provider_sub: str | None = userinfo.get("sub")
    email: str | None = userinfo.get("email")

    if not provider_sub or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider did not return required user information (sub, email).",
        )

    name: str | None = userinfo.get("name")
    avatar_url: str | None = userinfo.get("picture")  # Google; Microsoft uses different claim

    # Microsoft uses 'picture' too via OIDC, but may also expose it differently
    if avatar_url is None:
        avatar_url = userinfo.get("photo")

    async with database.SessionLocal() as session:
        user = await upsert_user_from_oauth(
            session,
            provider=provider,
            provider_sub=provider_sub,
            email=email,
            name=name,
            avatar_url=avatar_url,
        )
        raw_refresh = await create_and_store_refresh_token(session, user.id)

    access_token = create_access_token(user.id, user.email, user.role.value)

    cfg = get_oauth_config()
    response = RedirectResponse(url=cfg.frontend_url, status_code=302)
    set_auth_cookies(response, access_token, raw_refresh)
    logger.info("Successful OAuth login: user=%s provider=%s", user.id, provider)
    return response


# ── Protected: current user ────────────────────────────────────────────────────


@router.get("/me")
async def me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(_get_db_session),
):
    """Return the authenticated user's profile, including linked providers."""
    result = await session.execute(select(OAuthAccount.provider).where(OAuthAccount.user_id == current_user.id))
    linked_providers = [row[0] for row in result.fetchall()]

    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "role": current_user.role.value,
        "linked_providers": linked_providers,
    }


# ── Token refresh ──────────────────────────────────────────────────────────────


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """
    Rotate the refresh token.
    Validates the cookie value against the DB, revokes the old token,
    issues a new pair and sets updated cookies.
    """
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    token_hash = hash_token(raw_token)

    async with database.SessionLocal() as session:
        result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        rt = result.scalar_one_or_none()

        if rt is None or rt.revoked:
            clear_auth_cookies(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or revoked.",
            )

        if rt.expires_at < datetime.now(UTC):
            rt.revoked = True
            await session.commit()
            clear_auth_cookies(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired.",
            )

        # Revoke the old token
        rt.revoked = True
        await session.commit()

        user = await session.get(User, rt.user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive.",
            )

        raw_new_refresh = await create_and_store_refresh_token(session, user.id)

    new_access = create_access_token(user.id, user.email, user.role.value)
    set_auth_cookies(response, new_access, raw_new_refresh)
    return {"detail": "Tokens refreshed"}


# ── Logout ─────────────────────────────────────────────────────────────────────


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Revoke the stored refresh token and clear both auth cookies."""
    raw_token = request.cookies.get("refresh_token")
    if raw_token:
        token_hash = hash_token(raw_token)
        async with database.SessionLocal() as session:
            result = await session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
            rt = result.scalar_one_or_none()
            if rt and not rt.revoked:
                rt.revoked = True
                await session.commit()

    clear_auth_cookies(response)
    return {"detail": "Logged out"}
