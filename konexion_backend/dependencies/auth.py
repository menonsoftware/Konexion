"""
FastAPI dependency factories for authentication and RBAC.
"""

from collections.abc import AsyncGenerator
from typing import cast

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from konexion_backend.models.db_model import database
from konexion_backend.models.user_model import User, UserRole
from konexion_backend.services.auth_service import verify_access_token


async def _get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the request lifetime."""
    async with database.SessionLocal() as session:
        yield session


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(_get_db_session),
) -> User:
    """
    Extract and verify the access_token cookie, then load the User from DB.
    Raises HTTP 401 if missing, invalid, or expired.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = verify_access_token(token)
    user_id: str = payload["sub"]

    user = cast(User | None, await session.get(User, user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


async def optional_current_user(
    request: Request,
    session: AsyncSession = Depends(_get_db_session),
) -> User | None:
    """Like get_current_user but returns None instead of raising when unauthenticated."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = verify_access_token(token)
        user = cast(User | None, await session.get(User, payload["sub"]))
        return user if (user and user.is_active) else None
    except HTTPException:
        return None


def require_role(role: UserRole):
    """
    Dependency factory for RBAC.
    Usage:  Depends(require_role(UserRole.admin))
    Raises HTTP 403 if the authenticated user does not hold the required role.
    """

    async def _check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check_role
