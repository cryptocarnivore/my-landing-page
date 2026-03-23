import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
DEFAULT_CHAIN = os.getenv("DEFAULT_CHAIN", "ethereum")
SLIPPAGE_PERCENT = float(os.getenv("SLIPPAGE_PERCENT", "5"))
PRICE_CHECK_INTERVAL = int(os.getenv("PRICE_CHECK_INTERVAL", "30"))

_raw_ids = os.getenv("ALLOWED_USER_IDS", "")
ALLOWED_USER_IDS: set[int] = (
    {int(uid.strip()) for uid in _raw_ids.split(",") if uid.strip()}
    if _raw_ids.strip()
    else set()
)

# Chain configs: id, native symbol, wrapped native, Uniswap V2 router, RPC
CHAINS: dict[str, dict] = {
    "ethereum": {
        "id": 1,
        "name": "Ethereum",
        "native": "ETH",
        "wnative": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "rpc": os.getenv("ETH_RPC_URL") or "https://ethereum.publicnode.com",
    },
    "bsc": {
        "id": 56,
        "name": "BNB Chain",
        "native": "BNB",
        "wnative": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",  # PancakeSwap V2
        "rpc": os.getenv("BSC_RPC_URL") or "https://bsc-dataseed.binance.org",
    },
    "polygon": {
        "id": 137,
        "name": "Polygon",
        "native": "MATIC",
        "wnative": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
        "router": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",  # QuickSwap
        "rpc": os.getenv("POLYGON_RPC_URL") or "https://polygon.publicnode.com",
    },
    "arbitrum": {
        "id": 42161,
        "name": "Arbitrum One",
        "native": "ETH",
        "wnative": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",  # SushiSwap
        "rpc": os.getenv("ARBITRUM_RPC_URL") or "https://arb1.arbitrum.io/rpc",
    },
    "base": {
        "id": 8453,
        "name": "Base",
        "native": "ETH",
        "wnative": "0x4200000000000000000000000000000000000006",
        "router": "0x8cFe327CEc66d1C090Dd72bd0FF11d690C33a2Eb",  # BaseSwap
        "rpc": os.getenv("BASE_RPC_URL") or "https://mainnet.base.org",
    },
}

# Minimal Uniswap V2 Router ABI
ROUTER_ABI = [
    {
        "name": "getAmountsOut",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    },
    {
        "name": "swapExactETHForTokens",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    },
    {
        "name": "swapExactETHForTokensSupportingFeeOnTransferTokens",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "outputs": [],
    },
    {
        "name": "swapExactTokensForETH",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
    },
    {
        "name": "swapExactTokensForETHSupportingFeeOnTransferTokens",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "outputs": [],
    },
]

# Minimal ERC-20 ABI
ERC20_ABI = [
    {
        "name": "approve",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    },
    {
        "name": "allowance",
        "type": "function",
        "stateMutability": "view",
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    },
    {
        "name": "decimals",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8"}],
    },
    {
        "name": "symbol",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "string"}],
    },
    {
        "name": "name",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"name": "", "type": "string"}],
    },
]
