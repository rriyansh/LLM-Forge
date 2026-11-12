"""Seed a default tenant + admin user. For bootstrap only."""
from __future__ import annotations

import asyncio
import os

from sqlalchemy import select

from src.db.models import Base, Tenant, User
from src.db.session import get_engine, init_db
from src.utils.security import hash_password


async def main() -> None:
    await init_db()
    eng = get_engine()
    if eng is None:
        raise RuntimeError("DATABASE_URL not set")
    from sqlalchemy.ext.asyncio import async_sessionmaker

    factory = async_sessionmaker(eng, expire_on_commit=False)
    async with factory() as s:
        t = (await s.execute(select(Tenant).where(Tenant.name == "default"))).scalar_one_or_none()
        if t is None:
            t = Tenant(name="default", tier="premium")
            s.add(t)
            await s.flush()
        u = (await s.execute(select(User).where(User.email == "admin@local"))).scalar_one_or_none()
        if u is None:
            u = User(
                tenant_id=t.id,
                email="admin@local",
                password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "ChangeMe!123")),
                role="admin",
            )
            s.add(u)
        await s.commit()
    print("Seeded tenant + admin")


if __name__ == "__main__":
    asyncio.run(main())
