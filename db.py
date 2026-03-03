import aiosqlite
from pathlib import Path
from datetime import datetime, timezone, timedelta


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class DB:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                lang TEXT NOT NULL DEFAULT 'uz'
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS channels(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat TEXT NOT NULL UNIQUE
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS counters(
                year INTEGER PRIMARY KEY,
                seq INTEGER NOT NULL
            )""")

            await db.execute("""
            CREATE TABLE IF NOT EXISTS orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_code TEXT UNIQUE,
                created_at TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                lang TEXT NOT NULL,

                district TEXT,
                address TEXT,
                kg INTEGER,
                lat REAL,
                lon REAL,
                maps_link TEXT,

                receiver_name TEXT,
                receiver_phone TEXT,
                passport_front_file_id TEXT,
                passport_back_file_id TEXT,

                banned_ok INTEGER,
                items_list_file_id TEXT,

                contact_phone TEXT,
                contact_username TEXT,

                usd_part REAL,
                taxi_try REAL,
                total_try REAL,
                total_uzs REAL,

                payment_type TEXT,
                payment_status TEXT,
                payment_screenshot_file_id TEXT,

                status TEXT
            )""")

            await db.commit()

    # -------------------------
    # USERS / LANG
    # -------------------------
    async def get_lang(self, user_id: int) -> str:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
            row = await cur.fetchone()
            return row[0] if row else "uz"

    async def set_lang(self, user_id: int, lang: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO users(user_id, lang) VALUES(?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang",
                (user_id, lang),
            )
            await db.commit()

    # -------------------------
    # CHANNELS
    # -------------------------
    async def list_channels(self) -> list[str]:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT chat FROM channels ORDER BY id ASC")
            rows = await cur.fetchall()
            return [r[0] for r in rows]

    async def add_channel(self, chat: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT OR IGNORE INTO channels(chat) VALUES(?)", (chat,))
            await db.commit()

    async def del_channel(self, chat: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM channels WHERE chat=?", (chat,))
            await db.commit()

    # -------------------------
    # SETTINGS (RATES)
    # -------------------------
    async def set_setting(self, key: str, value: str):
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                "INSERT INTO settings(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
            await db.commit()

    async def get_setting(self, key: str, default: str) -> str:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = await cur.fetchone()
            return row[0] if row else default

    async def get_rates(
        self,
        default_usd_try: float,
        default_usd_uzs: float,
        default_try_uzs: float
    ) -> tuple[float, float, float]:
        usd_try = float(await self.get_setting("USD_TRY_RATE", str(default_usd_try)))
        usd_uzs = float(await self.get_setting("USD_UZS_RATE", str(default_usd_uzs)))
        try_uzs = float(await self.get_setting("TRY_UZS_RATE", str(default_try_uzs)))
        return usd_try, usd_uzs, try_uzs

    # -------------------------
    # ORDERS BASIC
    # -------------------------
    async def create_order(self, user_id: int, lang: str) -> int:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("""
                INSERT INTO orders(created_at, user_id, lang, status, payment_status)
                VALUES(?,?,?,?,?)
            """, (now_iso(), user_id, lang, "NEW", "DRAFT"))
            await db.commit()
            return int(cur.lastrowid)

    async def update_order(self, order_id: int, **fields):
        if not fields:
            return
        cols = ", ".join([f"{k}=?" for k in fields.keys()])
        vals = list(fields.values()) + [order_id]
        async with aiosqlite.connect(self.path) as db:
            await db.execute(f"UPDATE orders SET {cols} WHERE id=?", vals)
            await db.commit()

    async def get_order(self, order_id: int) -> dict | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM orders WHERE id=?", (order_id,))
            row = await cur.fetchone()
            return dict(row) if row else None

    async def next_order_code(self) -> str:
        year = datetime.now().year
        async with aiosqlite.connect(self.path) as db:
            await db.execute("INSERT OR IGNORE INTO counters(year, seq) VALUES(?, 0)", (year,))
            await db.execute("UPDATE counters SET seq = seq + 1 WHERE year=?", (year,))
            cur = await db.execute("SELECT seq FROM counters WHERE year=?", (year,))
            seq = (await cur.fetchone())[0]
            await db.commit()
        return f"NK-{year}-{seq:05d}"

    # -------------------------
    # LISTS
    # -------------------------
    async def list_orders_today(self) -> list[dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM orders WHERE created_at LIKE ? ORDER BY id DESC",
                (f"{today}%",),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def list_orders_limit(self, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,))
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def list_orders_by_district(self, district: str, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM orders WHERE district=? ORDER BY id DESC LIMIT ?",
                (district, limit),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def list_orders_by_payment_type(self, payment_type: str, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM orders WHERE payment_type=? ORDER BY id DESC LIMIT ?",
                (payment_type, limit),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def list_orders_by_payment_status(self, payment_status: str, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM orders WHERE payment_status=? ORDER BY id DESC LIMIT ?",
                (payment_status, limit),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def list_orders_days(self, days: int) -> list[dict]:
        """
        days=0 -> bugun
        days=7 -> oxirgi 7 kun (bugunni ham qo‘shib)
        """
        start = datetime.now() - timedelta(days=days)
        start_str = start.strftime("%Y-%m-%d 00:00:00")

        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM orders WHERE created_at >= ? ORDER BY id DESC",
                (start_str,),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    # -------------------------
    # STATS
    # -------------------------
    async def stats_today_kg(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT COALESCE(SUM(kg),0) FROM orders WHERE created_at LIKE ? AND status != 'CANCELED'",
                (f"{today}%",),
            )
            (total,) = await cur.fetchone()
            return int(total or 0)

    async def stats_month_kg(self) -> int:
        ym = datetime.now().strftime("%Y-%m")
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT COALESCE(SUM(kg),0) FROM orders WHERE created_at LIKE ? AND status != 'CANCELED'",
                (f"{ym}%",),
            )
            (total,) = await cur.fetchone()
            return int(total or 0)