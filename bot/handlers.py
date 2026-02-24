"""
Telegram command handlers.

Commands
--------
/start          — Welcome & quick help
/chains         — List supported chains
/wallet         — Show wallet address and native balance
/price <addr>   — Quote current price on active chain
/buy <addr> <amount>
                — Buy a token; amount is in native gas token
/positions      — List open positions
/sell <id>      — Manually sell entire position
/sellhalf <id>  — Manually sell half a position
/setchain <chain>
                — Switch active chain for your session
/help           — Repeat help text
"""

import asyncio
import logging
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from config import CHAINS, ALLOWED_USER_IDS, WALLET_PRIVATE_KEY, DEFAULT_CHAIN
from bot.trader import Trader, TradeError
from bot.database import (
    add_position,
    get_open_positions,
    get_all_positions,
    get_position,
    update_position_half_sold,
    close_position,
)

log = logging.getLogger(__name__)

# Per-user active chain (in-memory; resets on restart)
_user_chain: dict[int, str] = {}


# ------------------------------------------------------------------ #
# Auth guard                                                           #
# ------------------------------------------------------------------ #

def restricted(func):
    """Only allow whitelisted users (if ALLOWED_USER_IDS is set)."""
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id  # type: ignore[union-attr]
        if ALLOWED_USER_IDS and uid not in ALLOWED_USER_IDS:
            await update.message.reply_text("Access denied.")  # type: ignore[union-attr]
            return
        return await func(update, ctx)
    return wrapper


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _chain_for(user_id: int) -> str:
    return _user_chain.get(user_id, DEFAULT_CHAIN)


def _trader(user_id: int) -> Trader:
    return Trader(_chain_for(user_id), WALLET_PRIVATE_KEY)


def _status_emoji(status: str) -> str:
    return {"open": "🟢", "half_sold": "🟡", "closed": "🔴"}.get(status, "⚪")


# ------------------------------------------------------------------ #
# /start  /help                                                        #
# ------------------------------------------------------------------ #

HELP_TEXT = """
*Crypto Trading Bot*

Commands:
`/chains` — List supported chains
`/setchain <chain>` — Switch active chain
`/wallet` — Show wallet & balance
`/price <token_address>` — Get current price
`/buy <token_address> <amount>` — Buy with native gas token
`/positions` — List your positions
`/sell <id>` — Sell entire position
`/sellhalf <id>` — Sell 50% of position
`/help` — Show this message

The bot auto-sells *50%* of any position when the token doubles vs your buy price.

*Risk warning*: This bot executes real on-chain transactions using your wallet. Only use funds you can afford to lose.
"""


@restricted
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")  # type: ignore[union-attr]


@restricted
async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")  # type: ignore[union-attr]


# ------------------------------------------------------------------ #
# /chains                                                              #
# ------------------------------------------------------------------ #

@restricted
async def cmd_chains(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id  # type: ignore[union-attr]
    active = _chain_for(uid)
    lines = []
    for key, cfg in CHAINS.items():
        marker = " ← active" if key == active else ""
        lines.append(f"`{key}` — {cfg['name']} ({cfg['native']}){marker}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")  # type: ignore[union-attr]


# ------------------------------------------------------------------ #
# /setchain                                                            #
# ------------------------------------------------------------------ #

@restricted
async def cmd_setchain(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id  # type: ignore[union-attr]
    args = ctx.args or []
    if not args:
        await update.message.reply_text("Usage: `/setchain <chain>`\nSee `/chains` for options.", parse_mode="Markdown")  # type: ignore[union-attr]
        return
    chain = args[0].lower()
    if chain not in CHAINS:
        await update.message.reply_text(f"Unknown chain. Choose from: {', '.join(CHAINS)}")  # type: ignore[union-attr]
        return
    _user_chain[uid] = chain
    await update.message.reply_text(f"Active chain set to *{CHAINS[chain]['name']}*", parse_mode="Markdown")  # type: ignore[union-attr]


# ------------------------------------------------------------------ #
# /wallet                                                              #
# ------------------------------------------------------------------ #

@restricted
async def cmd_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id  # type: ignore[union-attr]
    chain = _chain_for(uid)
    msg = await update.message.reply_text("Fetching balance...")  # type: ignore[union-attr]

    loop = asyncio.get_event_loop()
    try:
        trader = _trader(uid)
        balance = await loop.run_in_executor(None, trader.wallet_balance_native)
        native = CHAINS[chain]["native"]
        text = (
            f"*Wallet*: `{trader.wallet}`\n"
            f"*Chain*: {CHAINS[chain]['name']}\n"
            f"*Balance*: {balance:.6f} {native}"
        )
    except TradeError as exc:
        text = f"Error: {exc}"

    await msg.edit_text(text, parse_mode="Markdown")


# ------------------------------------------------------------------ #
# /price                                                               #
# ------------------------------------------------------------------ #

@restricted
async def cmd_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id  # type: ignore[union-attr]
    args = ctx.args or []
    if not args:
        await update.message.reply_text("Usage: `/price <token_address>`", parse_mode="Markdown")  # type: ignore[union-attr]
        return

    token_address = args[0]
    msg = await update.message.reply_text("Fetching price...")  # type: ignore[union-attr]

    loop = asyncio.get_event_loop()
    try:
        trader = _trader(uid)
        info = await loop.run_in_executor(None, trader.token_info, token_address)
        price = await loop.run_in_executor(None, trader.get_price_native, token_address)
        chain = _chain_for(uid)
        native = CHAINS[chain]["native"]
        cost_per_token = 1.0 / price if price else 0
        text = (
            f"*{info['name']}* ({info['symbol']})\n"
            f"Chain: {CHAINS[chain]['name']}\n"
            f"1 {native} = *{price:.4f} {info['symbol']}*\n"
            f"1 {info['symbol']} = *{cost_per_token:.8f} {native}*"
        )
    except (TradeError, Exception) as exc:
        text = f"Error fetching price: {exc}"

    await msg.edit_text(text, parse_mode="Markdown")


# ------------------------------------------------------------------ #
# /buy                                                                 #
# ------------------------------------------------------------------ #

@restricted
async def cmd_buy(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id  # type: ignore[union-attr]
    args = ctx.args or []
    if len(args) < 2:
        await update.message.reply_text(  # type: ignore[union-attr]
            "Usage: `/buy <token_address> <amount_native>`\n"
            "Example: `/buy 0xabc...def 0.1`",
            parse_mode="Markdown",
        )
        return

    token_address = args[0]
    try:
        amount = float(args[1])
    except ValueError:
        await update.message.reply_text("Amount must be a number.")  # type: ignore[union-attr]
        return

    if amount <= 0:
        await update.message.reply_text("Amount must be positive.")  # type: ignore[union-attr]
        return

    chain = _chain_for(uid)
    native = CHAINS[chain]["native"]
    msg = await update.message.reply_text(  # type: ignore[union-attr]
        f"Buying with {amount} {native} on {CHAINS[chain]['name']}..."
    )

    loop = asyncio.get_event_loop()
    try:
        trader = _trader(uid)
        info = await loop.run_in_executor(None, trader.token_info, token_address)
        result = await loop.run_in_executor(
            None, trader.buy, token_address, amount
        )
    except TradeError as exc:
        await msg.edit_text(f"Buy failed: {exc}")
        return
    except Exception as exc:
        log.exception("Unexpected buy error")
        await msg.edit_text(f"Unexpected error: {exc}")
        return

    pos_id = await add_position(
        chat_id=uid,
        chain=chain,
        token_address=token_address,
        token_symbol=info["symbol"],
        token_name=info["name"],
        token_decimals=info["decimals"],
        amount_token=result["amount_token"],
        amount_native=result["amount_native"],
        buy_price=result["buy_price"],
        buy_tx=result["tx_hash"],
    )

    text = (
        f"*Buy executed!* (Position #{pos_id})\n\n"
        f"Token: *{info['name']}* ({info['symbol']})\n"
        f"Spent: *{amount} {native}*\n"
        f"Received: *{result['amount_token']:.6f} {info['symbol']}*\n"
        f"Buy price: *{result['buy_price']:.8f} {native}/{info['symbol']}*\n\n"
        f"Auto-sell at 2x: {result['buy_price'] * 2:.8f} {native}/{info['symbol']}\n"
        f"Tx: `{result['tx_hash']}`"
    )
    await msg.edit_text(text, parse_mode="Markdown")


# ------------------------------------------------------------------ #
# /positions                                                           #
# ------------------------------------------------------------------ #

@restricted
async def cmd_positions(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id  # type: ignore[union-attr]
    positions = await get_all_positions(uid)

    if not positions:
        await update.message.reply_text("No positions yet. Use `/buy` to open one.", parse_mode="Markdown")  # type: ignore[union-attr]
        return

    lines = ["*Your Positions*\n"]
    for pos in positions:
        chain_name = CHAINS.get(pos["chain"], {}).get("name", pos["chain"])
        native = CHAINS.get(pos["chain"], {}).get("native", "?")
        emoji = _status_emoji(pos["status"])
        lines.append(
            f"{emoji} *#{pos['id']}* {pos['token_symbol']} ({chain_name})\n"
            f"  Amount: {pos['amount_token']:.4f} | Spent: {pos['amount_native']:.6f} {native}\n"
            f"  Buy price: {pos['buy_price']:.8f} | Status: {pos['status']}"
        )

    await update.message.reply_text("\n\n".join(lines), parse_mode="Markdown")  # type: ignore[union-attr]


# ------------------------------------------------------------------ #
# /sell  /sellhalf                                                     #
# ------------------------------------------------------------------ #

@restricted
async def cmd_sell(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await _manual_sell(update, ctx, half=False)


@restricted
async def cmd_sellhalf(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await _manual_sell(update, ctx, half=True)


async def _manual_sell(update: Update, ctx: ContextTypes.DEFAULT_TYPE, half: bool) -> None:
    uid = update.effective_user.id  # type: ignore[union-attr]
    args = ctx.args or []
    cmd = "/sellhalf" if half else "/sell"
    if not args:
        await update.message.reply_text(f"Usage: `{cmd} <position_id>`", parse_mode="Markdown")  # type: ignore[union-attr]
        return

    try:
        pos_id = int(args[0])
    except ValueError:
        await update.message.reply_text("Position ID must be an integer.")  # type: ignore[union-attr]
        return

    pos = await get_position(pos_id)
    if pos is None:
        await update.message.reply_text(f"Position #{pos_id} not found.")  # type: ignore[union-attr]
        return
    if pos["chat_id"] != uid:
        await update.message.reply_text("That position doesn't belong to you.")  # type: ignore[union-attr]
        return
    if pos["status"] == "closed":
        await update.message.reply_text("Position is already closed.")  # type: ignore[union-attr]
        return

    amount = pos["amount_token"] / 2 if half else pos["amount_token"]
    chain = pos["chain"]
    native = CHAINS.get(chain, {}).get("native", "?")

    msg = await update.message.reply_text(  # type: ignore[union-attr]
        f"Selling {'50% of' if half else 'all'} position #{pos_id}..."
    )

    loop = asyncio.get_event_loop()
    try:
        trader = Trader(chain, WALLET_PRIVATE_KEY)
        result = await loop.run_in_executor(
            None, trader.sell, pos["token_address"], amount
        )
    except TradeError as exc:
        await msg.edit_text(f"Sell failed: {exc}")
        return

    if half:
        remaining = pos["amount_token"] - amount
        await update_position_half_sold(pos_id, remaining, result["tx_hash"])
        status_text = f"Remaining: {remaining:.4f} {pos['token_symbol']}"
    else:
        await close_position(pos_id, result["tx_hash"])
        status_text = "Position closed."

    text = (
        f"*Sell executed!*\n\n"
        f"Sold: *{amount:.4f} {pos['token_symbol']}*\n"
        f"Received: *{result['amount_native_received']:.6f} {native}*\n"
        f"{status_text}\n\n"
        f"Tx: `{result['tx_hash']}`"
    )
    await msg.edit_text(text, parse_mode="Markdown")
