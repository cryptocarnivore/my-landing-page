"""
Background price monitor.

Every PRICE_CHECK_INTERVAL seconds, checks each open position.
When the current price is >= 2x the buy price, sells 50% of the holding
and notifies the user via Telegram.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

from config import CHAINS, PRICE_CHECK_INTERVAL, WALLET_PRIVATE_KEY
from bot.database import get_open_positions, update_position_half_sold
from bot.trader import Trader, TradeError

if TYPE_CHECKING:
    from telegram.ext import Application

log = logging.getLogger(__name__)


async def monitor_loop(app: "Application") -> None:  # type: ignore[type-arg]
    """Infinite loop that checks prices and fires auto-sells."""
    log.info("Price monitor started (interval=%ds)", PRICE_CHECK_INTERVAL)

    while True:
        await asyncio.sleep(PRICE_CHECK_INTERVAL)
        try:
            await _check_all_positions(app)
        except Exception as exc:
            log.exception("Unexpected error in monitor loop: %s", exc)


async def _check_all_positions(app: "Application") -> None:  # type: ignore[type-arg]
    positions = await get_open_positions()  # all users, all open positions
    if not positions:
        return

    for pos in positions:
        try:
            await _check_position(pos, app)
        except Exception as exc:
            log.warning("Error checking position %d: %s", pos["id"], exc)


async def _check_position(pos: dict, app: "Application") -> None:  # type: ignore[type-arg]
    chain = pos["chain"]
    if chain not in CHAINS:
        return

    # Run blocking web3 calls in executor to not block the event loop
    loop = asyncio.get_event_loop()
    try:
        price_now = await loop.run_in_executor(
            None, _get_price, chain, pos["token_address"]
        )
    except TradeError as exc:
        log.debug("Price check failed for position %d: %s", pos["id"], exc)
        return

    buy_price = pos["buy_price"]           # native per token at buy time
    # buy_price = native_spent / tokens_received  (smaller = cheaper)
    # current value: 1/price_now native per token
    # We compare: current_price_in_native vs buy_price_in_native
    # buy_price is stored as native/token (cost per token)
    # price_now is tokens/native (output per native)
    # current_cost_per_token = 1 / price_now  (native per token now)
    # Doubled when current_cost_per_token <= buy_price / 2
    #  i.e. token value doubled means you need less native to buy 1 token

    current_price_native_per_token = 1.0 / price_now if price_now > 0 else float("inf")

    multiplier = buy_price / current_price_native_per_token if current_price_native_per_token > 0 else 0

    log.debug(
        "Position %d (%s) — buy: %.8f, now: %.8f, mult: %.2fx",
        pos["id"], pos["token_symbol"], buy_price, current_price_native_per_token, multiplier,
    )

    if multiplier < 2.0:
        return  # not doubled yet

    # 2x reached — sell half
    log.info(
        "Position %d (%s) reached %.2fx — auto-selling 50%%",
        pos["id"], pos["token_symbol"], multiplier,
    )

    half = pos["amount_token"] / 2.0
    loop = asyncio.get_event_loop()

    try:
        result = await loop.run_in_executor(
            None, _execute_sell, chain, pos["token_address"], half
        )
    except TradeError as exc:
        log.error("Auto-sell failed for position %d: %s", pos["id"], exc)
        await _notify(
            app,
            pos["chat_id"],
            f"Auto-sell FAILED for {pos['token_symbol']} ({pos['chain'].upper()})\n"
            f"Reached {multiplier:.2f}x but sell errored: {exc}",
        )
        return

    remaining = pos["amount_token"] - half
    await update_position_half_sold(pos["id"], remaining, result["tx_hash"])

    native_sym = CHAINS[chain]["native"]
    msg = (
        f"*Auto-sell triggered!* {pos['token_symbol']} reached *{multiplier:.2f}x*\n\n"
        f"Sold *{half:.4f} {pos['token_symbol']}* for "
        f"*{result['amount_native_received']:.6f} {native_sym}*\n"
        f"Remaining: {remaining:.4f} {pos['token_symbol']} (let it ride)\n\n"
        f"Tx: `{result['tx_hash']}`"
    )
    await _notify(app, pos["chat_id"], msg)


def _get_price(chain: str, token_address: str) -> float:
    """Synchronous price fetch — run in executor."""
    trader = Trader(chain, WALLET_PRIVATE_KEY)
    return trader.get_price_native(token_address)


def _execute_sell(chain: str, token_address: str, amount_token: float) -> dict:
    """Synchronous sell — run in executor."""
    trader = Trader(chain, WALLET_PRIVATE_KEY)
    return trader.sell(token_address, amount_token)


async def _notify(app: "Application", chat_id: int, text: str) -> None:  # type: ignore[type-arg]
    try:
        await app.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
        )
    except Exception as exc:
        log.error("Failed to notify chat %d: %s", chat_id, exc)
