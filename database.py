import aiosqlite
from datetime import datetime


async def create_database():
    async with aiosqlite.connect("users.db") as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                city TEXT,
                birth_date TEXT,
                username TEXT,
                telegram_id INTEGER UNIQUE,
                bonus_balance INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                receipt_number TEXT,
                status TEXT DEFAULT 'Очікує перевірки',
                created_at TEXT
            )
        """)

        await db.commit()


async def add_user(full_name, phone, city, birth_date, username, telegram_id):
    async with aiosqlite.connect("users.db") as db:

        await db.execute("""
            INSERT OR REPLACE INTO users
            (
                full_name,
                phone,
                city,
                birth_date,
                username,
                telegram_id,
                bonus_balance,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name,
            phone,
            city,
            birth_date,
            username,
            telegram_id,
            0,
            datetime.now().strftime("%d.%m.%Y %H:%M")
        ))

        await db.commit()


async def add_receipt(telegram_id, receipt_number):
    async with aiosqlite.connect("users.db") as db:

        await db.execute("""
            INSERT INTO receipts
            (
                telegram_id,
                receipt_number,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            telegram_id,
            receipt_number,
            datetime.now().strftime("%d.%m.%Y %H:%M")
        ))

        await db.commit()


async def user_exists(telegram_id):
    async with aiosqlite.connect("users.db") as db:

        cursor = await db.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )

        user = await cursor.fetchone()

        return user is not None


async def get_user_profile(telegram_id):
    async with aiosqlite.connect("users.db") as db:

        cursor = await db.execute("""
            SELECT
                full_name,
                phone,
                city,
                birth_date,
                bonus_balance
            FROM users
            WHERE telegram_id = ?
        """, (telegram_id,))

        return await cursor.fetchone()