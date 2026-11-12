"""Issue JWT tokens from username/password. Use with users table."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.db.session import get_session
from src.serving.schemas import TokenRequest, TokenResponse
from src.utils.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)

router = APIRouter(prefix="/auth")


@router.post("/token", response_model=TokenResponse)
async def issue_token(body: TokenRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    stmt = select(User).where(User.email == body.username, User.active.is_(True))
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid_credentials")
    access = create_access_token(user.id, role=user.role, tenant=user.tenant_id)
    refresh = create_refresh_token(user.id, tenant=user.tenant_id)
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=3600)
