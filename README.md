# Telegram Crypto Trading Bot

A self-hosted Telegram bot that buys ERC-20 tokens on Uniswap V2-compatible DEXes and **automatically sells 50% when the token doubles** versus the native gas token used to buy it.

## Supported Chains

| Key        | Network       | Native | DEX               |
|------------|---------------|--------|-------------------|
| `ethereum` | Ethereum      | ETH    | Uniswap V2        |
| `bsc`      | BNB Chain     | BNB    | PancakeSwap V2    |
| `polygon`  | Polygon       | MATIC  | QuickSwap         |
| `arbitrum` | Arbitrum One  | ETH    | SushiSwap         |
| `base`     | Base          | ETH    | BaseSwap          |

## How It Works

1. You send `/buy <token_address> <amount>` in Telegram.
2. The bot buys the token via the active chain's DEX router using your wallet.
3. A background monitor checks prices every 30 seconds (configurable).
4. When the token's price **doubles** vs your buy price, the bot sells **50%** and notifies you.
5. The remaining 50% keeps riding — sell it manually with `/sell <id>` whenever you want.

## Setup

### 1. Prerequisites

- Python 3.11+
- A funded EVM wallet (you need its private key)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```
TELEGRAM_BOT_TOKEN=your_bot_token
WALLET_PRIVATE_KEY=your_private_key   # 0x-prefixed or raw hex
DEFAULT_CHAIN=ethereum                # starting chain
SLIPPAGE_PERCENT=5                    # 5% slippage tolerance
PRICE_CHECK_INTERVAL=30               # seconds between price checks
ALLOWED_USER_IDS=123456,789012        # optional whitelist; leave empty = no restriction
```

> **Never commit your `.env` file.** It contains your private key.

### 4. Run

```bash
python main.py
```

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and help |
| `/chains` | List supported chains |
| `/setchain <chain>` | Switch active chain (e.g. `bsc`) |
| `/wallet` | Show wallet address and native balance |
| `/price <token_address>` | Get current token price |
| `/buy <token_address> <amount>` | Buy a token with native gas |
| `/positions` | List all your positions |
| `/sellhalf <id>` | Manually sell 50% of a position |
| `/sell <id>` | Sell an entire position |
| `/help` | Repeat help text |

## Position Statuses

- `open` — full position held, monitoring for 2x
- `half_sold` — 50% auto-sold on 2x, remaining still held
- `closed` — fully sold

## Security Notes

- Your private key is loaded from `.env` at startup and never stored in the database or logged.
- Use `ALLOWED_USER_IDS` to restrict bot access to specific Telegram user IDs.
- Run the bot on a machine you control; avoid shared hosting.
- Test with small amounts first.

## Risk Warning

This bot executes real on-chain transactions with real funds. Crypto markets are volatile. DEX slippage, gas spikes, and smart-contract bugs can all cause losses. Use only funds you can afford to lose entirely.
