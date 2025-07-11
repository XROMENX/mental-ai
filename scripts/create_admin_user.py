import asyncio
import os
import uuid
from datetime import datetime

from database import db
from auth import hash_password

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
