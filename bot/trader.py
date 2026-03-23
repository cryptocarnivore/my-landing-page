"""
DEX trading logic via Uniswap V2-compatible routers.

Supports: Ethereum (Uniswap), BSC (PancakeSwap), Polygon (QuickSwap),
          Arbitrum (SushiSwap), Base (BaseSwap).
"""

import time
import asyncio
import logging
from typing import Any

from web3 import Web3
from web3.exceptions import ContractLogicError

from config import CHAINS, ROUTER_ABI, ERC20_ABI, SLIPPAGE_PERCENT

log = logging.getLogger(__name__)

# Maximum uint256 for unlimited approvals
MAX_UINT256 = 2**256 - 1


class TradeError(Exception):
    """Raised when a trade cannot be executed."""


class Trader:
    def __init__(self, chain: str, private_key: str) -> None:
        if chain not in CHAINS:
            raise TradeError(f"Unknown chain: {chain!r}. Choose from {list(CHAINS)}")

        self.chain = chain
        self.cfg = CHAINS[chain]
        self.w3 = Web3(Web3.HTTPProvider(self.cfg["rpc"]))

        if not self.w3.is_connected():
            raise TradeError(f"Cannot connect to RPC: {self.cfg['rpc']}")

        self.account = self.w3.eth.account.from_key(private_key)
        self.wallet = self.account.address

        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.cfg["router"]),
            abi=ROUTER_ABI,
        )

    # ------------------------------------------------------------------ #
    # Price helpers                                                        #
    # ------------------------------------------------------------------ #

    def get_price_native(self, token_address: str, amount_native_wei: int = 10**18) -> float:
        """
        Return how many tokens you get for `amount_native_wei` of the
        native gas token.  Price is expressed as tokens/native.
        """
        token_address = Web3.to_checksum_address(token_address)
        wnative = Web3.to_checksum_address(self.cfg["wnative"])
        path = [wnative, token_address]
        try:
            amounts = self.router.functions.getAmountsOut(amount_native_wei, path).call()
            decimals = self._decimals(token_address)
            return amounts[1] / (10**decimals)
        except (ContractLogicError, Exception) as exc:
            raise TradeError(f"Price lookup failed: {exc}") from exc

    def get_price_in_native(self, token_address: str, amount_token: float) -> float:
        """
        Return how much native you get for `amount_token` tokens.
        """
        token_address = Web3.to_checksum_address(token_address)
        decimals = self._decimals(token_address)
        amount_wei = int(amount_token * 10**decimals)
        wnative = Web3.to_checksum_address(self.cfg["wnative"])
        path = [token_address, wnative]
        try:
            amounts = self.router.functions.getAmountsOut(amount_wei, path).call()
            return amounts[1] / 10**18
        except (ContractLogicError, Exception) as exc:
            raise TradeError(f"Price lookup failed: {exc}") from exc

    def token_info(self, token_address: str) -> dict[str, Any]:
        """Return symbol, name, decimals for a token."""
        token_address = Web3.to_checksum_address(token_address)
        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        try:
            symbol = contract.functions.symbol().call()
            name = contract.functions.name().call()
            decimals = contract.functions.decimals().call()
        except Exception as exc:
            raise TradeError(f"Could not fetch token info: {exc}") from exc
        return {"symbol": symbol, "name": name, "decimals": decimals}

    def wallet_balance_native(self) -> float:
        """Return wallet balance in native gas token."""
        wei = self.w3.eth.get_balance(self.wallet)
        return wei / 10**18

    def token_balance(self, token_address: str) -> float:
        token_address = Web3.to_checksum_address(token_address)
        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        decimals = self._decimals(token_address)
        raw = contract.functions.balanceOf(self.wallet).call()
        return raw / 10**decimals

    # ------------------------------------------------------------------ #
    # Buy                                                                  #
    # ------------------------------------------------------------------ #

    def buy(
        self,
        token_address: str,
        amount_native: float,
        slippage: float | None = None,
        fee_on_transfer: bool = False,
    ) -> dict[str, Any]:
        """
        Buy `token_address` using `amount_native` of the native gas token.

        Returns a dict with:
            tx_hash, amount_token, amount_native, buy_price
        """
        slippage = slippage if slippage is not None else SLIPPAGE_PERCENT / 100
        token_address = Web3.to_checksum_address(token_address)
        wnative = Web3.to_checksum_address(self.cfg["wnative"])

        amount_wei = self.w3.to_wei(amount_native, "ether")
        path = [wnative, token_address]
        deadline = int(time.time()) + 300  # 5-minute deadline

        # Quote
        try:
            amounts = self.router.functions.getAmountsOut(amount_wei, path).call()
        except Exception as exc:
            raise TradeError(f"Quote failed — token may not be listed on this DEX: {exc}") from exc

        amount_out_expected = amounts[1]
        amount_out_min = int(amount_out_expected * (1 - slippage))

        # Gas estimate
        nonce = self.w3.eth.get_transaction_count(self.wallet)
        gas_price = self._gas_price()

        if fee_on_transfer:
            fn = self.router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                amount_out_min, path, self.wallet, deadline
            )
        else:
            fn = self.router.functions.swapExactETHForTokens(
                amount_out_min, path, self.wallet, deadline
            )

        try:
            gas_limit = fn.estimate_gas({"from": self.wallet, "value": amount_wei})
            gas_limit = int(gas_limit * 1.2)  # 20% buffer
        except Exception:
            gas_limit = 300_000

        tx = fn.build_transaction(
            {
                "from": self.wallet,
                "value": amount_wei,
                "gas": gas_limit,
                "gasPrice": gas_price,
                "nonce": nonce,
            }
        )

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

        if receipt["status"] != 1:
            # Retry with fee-on-transfer variant
            if not fee_on_transfer:
                return self.buy(token_address, amount_native, slippage, fee_on_transfer=True)
            raise TradeError("Buy transaction reverted.")

        decimals = self._decimals(token_address)
        tokens_received = amount_out_expected / 10**decimals
        buy_price = amount_native / tokens_received  # native per token

        return {
            "tx_hash": tx_hash.hex(),
            "amount_token": tokens_received,
            "amount_native": amount_native,
            "buy_price": buy_price,
        }

    # ------------------------------------------------------------------ #
    # Sell                                                                 #
    # ------------------------------------------------------------------ #

    def sell(
        self,
        token_address: str,
        amount_token: float,
        slippage: float | None = None,
        fee_on_transfer: bool = False,
    ) -> dict[str, Any]:
        """
        Sell `amount_token` tokens back to the native gas token.

        Returns a dict with:
            tx_hash, amount_native_received
        """
        slippage = slippage if slippage is not None else SLIPPAGE_PERCENT / 100
        token_address = Web3.to_checksum_address(token_address)
        decimals = self._decimals(token_address)
        wnative = Web3.to_checksum_address(self.cfg["wnative"])

        amount_wei = int(amount_token * 10**decimals)
        path = [token_address, wnative]
        deadline = int(time.time()) + 300

        # Ensure router allowance
        self._approve_if_needed(token_address, self.cfg["router"], amount_wei)

        # Quote
        try:
            amounts = self.router.functions.getAmountsOut(amount_wei, path).call()
        except Exception as exc:
            raise TradeError(f"Sell quote failed: {exc}") from exc

        amount_out_expected = amounts[1]
        amount_out_min = int(amount_out_expected * (1 - slippage))

        nonce = self.w3.eth.get_transaction_count(self.wallet)
        gas_price = self._gas_price()

        if fee_on_transfer:
            fn = self.router.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_wei, amount_out_min, path, self.wallet, deadline
            )
        else:
            fn = self.router.functions.swapExactTokensForETH(
                amount_wei, amount_out_min, path, self.wallet, deadline
            )

        try:
            gas_limit = fn.estimate_gas({"from": self.wallet})
            gas_limit = int(gas_limit * 1.2)
        except Exception:
            gas_limit = 300_000

        tx = fn.build_transaction(
            {
                "from": self.wallet,
                "gas": gas_limit,
                "gasPrice": gas_price,
                "nonce": nonce,
            }
        )

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

        if receipt["status"] != 1:
            if not fee_on_transfer:
                return self.sell(token_address, amount_token, slippage, fee_on_transfer=True)
            raise TradeError("Sell transaction reverted.")

        native_received = amount_out_expected / 10**18

        return {
            "tx_hash": tx_hash.hex(),
            "amount_native_received": native_received,
        }

    # ------------------------------------------------------------------ #
    # Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _decimals(self, token_address: str) -> int:
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(token_address), abi=ERC20_ABI
        )
        return contract.functions.decimals().call()

    def _gas_price(self) -> int:
        try:
            return self.w3.eth.gas_price
        except Exception:
            return self.w3.to_wei(5, "gwei")

    def _approve_if_needed(self, token_address: str, spender: str, amount_wei: int) -> None:
        token_address = Web3.to_checksum_address(token_address)
        spender = Web3.to_checksum_address(spender)
        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        allowance = contract.functions.allowance(self.wallet, spender).call()
        if allowance >= amount_wei:
            return
        nonce = self.w3.eth.get_transaction_count(self.wallet)
        tx = contract.functions.approve(spender, MAX_UINT256).build_transaction(
            {
                "from": self.wallet,
                "gas": 100_000,
                "gasPrice": self._gas_price(),
                "nonce": nonce,
            }
        )
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        log.info("Approved %s for router spending", token_address)
