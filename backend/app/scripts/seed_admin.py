"""
CLI seed script to provision the initial Administrator account.

Reads ADMIN_EMAIL, ADMIN_PASSWORD, and ADMIN_FULL_NAME from environment / settings.
Idempotent: if a user with ADMIN_EMAIL already exists, it reports without duplicating.

Usage:
    python -m app.scripts.seed_admin
"""

import asyncio
import sys

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models.user import User, UserRole


async def seed_admin(session_factory=None) -> None:
    settings = get_settings()
    factory = session_factory or async_session_factory
    print(f"[*] Checking for existing admin account ({settings.ADMIN_EMAIL})...")

    async with factory() as session:
        result = await session.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin is not None:
            print(
                f"[OK] Admin account '{settings.ADMIN_EMAIL}' already exists (ID: {existing_admin.user_id}). No action needed."
            )
            return

        # Create new admin
        admin_user = User(
            full_name=settings.ADMIN_FULL_NAME,
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        session.add(admin_user)
        await session.commit()
        print(
            f"[OK] Admin account successfully created!\n"
            f"    Email: {settings.ADMIN_EMAIL}\n"
            f"    User ID: {admin_user.user_id}\n"
            f"    Role: {admin_user.role.value}"
        )


def main() -> None:
    try:
        asyncio.run(seed_admin())
    except Exception as e:
        print(f"[!] Error seeding admin: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
