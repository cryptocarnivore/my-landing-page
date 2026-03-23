"""
Async SQLite database for tracking open positions.
"""

import aiosqlite
import time
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "positions.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS positions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id         INTEGER NOT NULL,
                chain           TEXT    NOT NULL,
                token_address   TEXT    NOT NULL,
                token_symbol    TEXT    NOT NULL,
                token_name      TEXT    NOT NULL,
                token_decimals  INTEGER NOT NULL DEFAULT 18,
                amount_token    REAL    NOT NULL,
                amount_native   REAL    NOT NULL,
                buy_price       REAL    NOT NULL,
                buy_tx          TEXT,
                status          TEXT    NOT NULL DEFAULT 'open',
                sell_tx         TEXT,
                created_at      INTEGER NOT NULL
            )
            """
        )
        await db.commit()


async def add_position(
    chat_id: int,
    chain: str,
    token_address: str,
    token_symbol: str,
    token_name: str,
    token_decimals: int,
    amount_token: float,
    amount_native: float,
    buy_price: float,
    buy_tx: str,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO positions
                (chat_id, chain, token_address, token_symbol, token_name,
                 token_decimals, amount_token, amount_native, buy_price,
                 buy_tx, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)
            """,
            (
                chat_id,
                chain,
                token_address.lower(),
                token_symbol,
                token_name,
                token_decimals,
                amount_token,
                amount_native,
                buy_price,
                buy_tx,
                int(time.time()),
            ),
        )
        await db.commit()
        return cursor.lastrowid  # type: ignore[return-value]


async def get_open_positions(chat_id: int | None = None) -> list[dict]:
    """Return open positions, optionally filtered by chat_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if chat_id is not None:
            cursor = await db.execute(
                "SELECT * FROM positions WHERE status = 'open' AND chat_id = ?",
                (chat_id,),
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM positions WHERE status = 'open'"
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_position(position_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM positions WHERE id = ?", (position_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def update_position_half_sold(
    position_id: int, remaining_tokens: float, sell_tx: str
) -> None:
    """Mark position as half-sold and update token amount to remaining."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE positions
            SET status = 'half_sold', amount_token = ?, sell_tx = ?
            WHERE id = ?
            """,
            (remaining_tokens, sell_tx, position_id),
        )
        await db.commit()


async def close_position(position_id: int, sell_tx: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE positions SET status = 'closed', sell_tx = ? WHERE id = ?",
            (sell_tx, position_id),
        )
        await db.commit()


async def get_all_positions(chat_id: int) -> list[dict]:
    """Return all positions (open, half_sold, closed) for a user."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM positions WHERE chat_id = ? ORDER BY created_at DESC",
            (chat_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
