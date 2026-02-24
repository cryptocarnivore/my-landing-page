"""
Entry point for the Telegram crypto trading bot.

Usage:
    python main.py
"""

import asyncio
import logging
import sys

from telegram.ext import Application, CommandHandler

from config import TELEGRAM_BOT_TOKEN, WALLET_PRIVATE_KEY
from bot.database import init_db
from bot.monitor import monitor_loop
from bot.handlers import (
    cmd_start,
    cmd_help,
    cmd_chains,
    cmd_setchain,
    cmd_wallet,
    cmd_price,
    cmd_buy,
    cmd_positions,
    cmd_sell,
    cmd_sellhalf,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def _validate_config() -> None:
    errors = []
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set")
    if not WALLET_PRIVATE_KEY:
        errors.append("WALLET_PRIVATE_KEY is not set")
    if errors:
        for e in errors:
            log.error(e)
        sys.exit(1)


async def post_init(app: Application) -> None:  # type: ignore[type-arg]
    """Called after the application starts. Kick off the monitor loop."""
    asyncio.create_task(monitor_loop(app))
    log.info("Monitor loop scheduled.")


def main() -> None:
    _validate_config()

    # Initialise database (sync call before event loop starts)
    asyncio.run(init_db())
    log.info("Database initialised.")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("chains", cmd_chains))
    app.add_handler(CommandHandler("setchain", cmd_setchain))
    app.add_handler(CommandHandler("wallet", cmd_wallet))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("buy", cmd_buy))
    app.add_handler(CommandHandler("positions", cmd_positions))
    app.add_handler(CommandHandler("sell", cmd_sell))
    app.add_handler(CommandHandler("sellhalf", cmd_sellhalf))

    log.info("Bot starting — polling for updates...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
