"""
Authentication service helpers.

Provides:
- JWT access token creation and verification
- Opaque refresh token generation and hashing
- HttpOnly cookie helpers
- User upsert with email-based account linking
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import HTTPException, Response, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from konexion_backend.config import get_security_config
from konexion_backend.models.user_model import OAuthAccount, RefreshToken, User, UserRole

# ── JWT helpers ────────────────────────────────────────────────────────────────


def create_access_token(user_id: str, email: str, role: str) -> str:
    """Issue a short-lived HS256 JWT access token."""
    cfg = get_security_config()
    expire = datetime.now(UTC) + timedelta(minutes=cfg.access_token_expire_minutes)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    return cast(str, jwt.encode(payload, cfg.secret_key, algorithm=cfg.algorithm))


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Raises HTTP 401 on any failure.
    """
    cfg = get_security_config()
    try:
        payload = cast(dict[str, Any], jwt.decode(token, cfg.secret_key, algorithms=[cfg.algorithm]))
        if payload.get("sub") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


# ── Refresh token helpers ──────────────────────────────────────────────────────


def generate_refresh_token() -> tuple[str, str]:
    """
    Generate a cryptographically random refresh token.
    Returns (raw_hex_token, sha256_hash).
    The raw token is set in the cookie; only the hash is stored in the DB.
    """
    raw = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, token_hash


def hash_token(raw: str) -> str:
    """SHA-256 hash of an arbitrary string (used to look up a token from a cookie value)."""
    return hashlib.sha256(raw.encode()).hexdigest()


# ── Cookie helpers ─────────────────────────────────────────────────────────────

_ACCESS_COOKIE = "access_token"
_REFRESH_COOKIE = "refresh_token"


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """
    Set both auth cookies as HttpOnly, SameSite=Lax.
    In production (non-localhost) these should also be Secure.
    """
    cfg = get_security_config()
    access_max_age = cfg.access_token_expire_minutes * 60
    refresh_max_age = cfg.refresh_token_expire_days * 24 * 3600

    response.set_cookie(
        key=_ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=access_max_age,
        path="/",
    )
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=refresh_max_age,
        path="/api/auth",  # Narrow path — only sent to auth endpoints
    )


def clear_auth_cookies(response: Response) -> None:
    """Delete both auth cookies from the browser."""
    response.delete_cookie(key=_ACCESS_COOKIE, path="/")
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/auth")


# ── User upsert with account linking ──────────────────────────────────────────


async def upsert_user_from_oauth(
    session: AsyncSession,
    *,
    provider: str,
    provider_sub: str,
    email: str,
    name: str | None,
    avatar_url: str | None,
) -> User:
    """
    Find or create a User from an OAuth callback.

    Lookup order (email-based account linking):
    1. Find OAuthAccount by (provider, provider_sub) → return linked User.
    2. Find User by email → attach a new OAuthAccount to it (account linking).
    3. Create a new User + OAuthAccount (first login with this email).

    Updates last_login_at and backfills name/avatar_url if previously null.
    """
    now = datetime.now(UTC)

    # 1. Existing OAuth account?
    result = await session.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_sub == provider_sub,
        )
    )
    oauth_account = result.scalar_one_or_none()

    if oauth_account:
        user = cast(User | None, await session.get(User, oauth_account.user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Linked user account not found.",
            )
    else:
        # 2. Existing user with same email?
        result = await session.execute(select(User).where(User.email == email))
        user = cast(User | None, result.scalar_one_or_none())

        if user:
            # Link this provider to the existing account
            new_oauth = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_sub=provider_sub,
            )
            session.add(new_oauth)
        else:
            # 3. Brand new user
            user = User(
                email=email,
                name=name,
                avatar_url=avatar_url,
                role=UserRole.user,
                is_active=True,
                created_at=now,
            )
            session.add(user)
            await session.flush()  # Populate user.id before creating FK row

            new_oauth = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_sub=provider_sub,
            )
            session.add(new_oauth)

    # Backfill profile fields if missing
    if user.name is None and name:
        user.name = name
    if user.avatar_url is None and avatar_url:
        user.avatar_url = avatar_url
    user.last_login_at = now

    await session.commit()
    await session.refresh(user)
    return user


async def create_and_store_refresh_token(session: AsyncSession, user_id: str) -> str:
    """
    Generate a refresh token, persist its hash in the DB, and return the raw value
    to be stored in the browser cookie.
    """
    from konexion_backend.config import get_security_config

    cfg = get_security_config()
    raw, token_hash = generate_refresh_token()
    expires_at = datetime.now(UTC) + timedelta(days=cfg.refresh_token_expire_days)

    rt = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    session.add(rt)
    await session.commit()
    return raw
