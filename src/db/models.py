"""SQLAlchemy models: tenants, users, usage records, API keys."""
from __future__ import annotations

import time
import uuid

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return uuid.uuid4().hex


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    tier: Mapped[str] = mapped_column(String(16), default="default", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=lambda: int(time.time()))

    users: Mapped[list["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_tenant_email"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="readonly", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=lambda: int(time.time()))

    tenant: Mapped[Tenant] = relationship(back_populates="users")


class ApiKey(Base):
    __tablename__ = "api_keys"
    __table_args__ = (Index("ix_apikey_hash", "key_hash", unique=True),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(128), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, default=lambda: int(time.time()))
    last_used_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


class UsageRecord(Base):
    __tablename__ = "usage_records"
    __table_args__ = (Index("ix_usage_tenant_ts", "tenant_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(32), index=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    endpoint: Mapped[str] = mapped_column(String(64))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="ok")
    timestamp: Mapped[int] = mapped_column(BigInteger, default=lambda: int(time.time()))
