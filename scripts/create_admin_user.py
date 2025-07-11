import asyncio
import os
import sys
import uuid
from datetime import datetime

current_dir = os.path.dirname(__file__)
backend_path = os.path.join(current_dir, "..", "backend")
sys.path.append(os.path.abspath(backend_path))

from database import db  # noqa: E402
from auth import hash_password  # noqa: E402

DEFAULT_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
DEFAULT_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")


async def main():
    existing = await db.users.find_one({"email": DEFAULT_EMAIL})
    if existing:
        print(f"User already exists: {DEFAULT_EMAIL}")
        return

    user_doc = {
        "user_id": str(uuid.uuid4()),
        "email": DEFAULT_EMAIL,
        "password": hash_password(DEFAULT_PASSWORD),
        "full_name": "Admin User",
        "age": 30,
        "student_level": "admin",
        "consent_given": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
        "xp": 0,
        "level": 1,
        "memory": {},
        "badges": [],
        "is_admin": True,
    }
    await db.users.insert_one(user_doc)
    print(f"Admin user created: {DEFAULT_EMAIL}")


if __name__ == "__main__":
    asyncio.run(main())
