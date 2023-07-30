from typing import cast
from hexbytes import HexBytes
import random
import string

from web3 import Web3
from web3._utils.datatypes import PropertyCheckingFactory
from web3.types import TxReceipt
from eth_typing import HexStr
import eth_account

from cheb3.constants import GAS_BUFFER

from loguru import logger


class Account:
    """Please use :func:`cheb3.Connection.account` interface to
    create an account instance associated with the connection.
    """

    w3: Web3 = None

    def __init__(self, private_key: str = None) -> None:
        """Creates a new account if `private_key` is not given."""

        if self.w3 is None:
            raise AttributeError(
                "The `Account` class has not been initialized. Please use the "
                "`Connection.account` interface to create an account."
            )

        if private_key is None:
            self.eth_acct = eth_account.Account.create("".join(random.choices(string.ascii_letters, k=3)))
        else:
            self.eth_acct = eth_account.Account.from_key(private_key)

        self.address = self.eth_acct.address
        self.private_key = self.eth_acct.key.hex()

    @classmethod
    def factory(cls, w3: Web3) -> "Account":
        eth_acct = cast(Account, PropertyCheckingFactory(cls.__name__, (cls,), {"w3": w3}))
        return eth_acct

    def get_balance(self) -> int:
        """Returns the balance of the account instance."""
        return self.w3.eth.get_balance(self.eth_acct.address)

    def call(self, to: HexStr, data: HexStr = "0x") -> HexBytes:
        """Interact with a smart contract without creating a new
        transaction on the blockchain.

        :param to: The address of the contract.
        :type to: HexStr
        :param data: The transaction data, defaults to `0x`.
        :type data: HexStr

        :rtype: ~hexbytes.main.HexBytes
        """

        to = Web3.to_checksum_address(to)

        return self.w3.eth.call(
            {
                "to": to,
                "from": self.address,
                "data": data,
            }
        )

    def send_transaction(self, to: HexStr, value: int = 0, data: HexStr = "0x", **kwargs) -> TxReceipt:
        """Transfer ETH or interact with a smart contract.

        :param to: The address of the receiver.
        :type to: HexStr
        :param value: The amount to transfer, defaults to 0 (wei).
        :type value: int
        :param data: The transaction data, defaults to `0x`.
        :type data: HexStr

        Keyword Args:
            gas_price (int): Specify the gas price for the transaction.
            gas_limit (int): Specify the maximum gas the transaction can use.

        :rtype: TxReceipt
        """

        to = Web3.to_checksum_address(to)

        tx = {
            "from": self.address,
            "to": to,
            "chainId": self.w3.eth.chain_id,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "value": value,
            "gasPrice": kwargs.get("gas_price", self.w3.eth.gas_price),
            "data": data,
        }
        tx["gas"] = kwargs.get("gas_limit", self.w3.eth.estimate_gas(tx) + GAS_BUFFER)
        tx = self.eth_acct.sign_transaction(tx).rawTransaction
        tx_hash = self.w3.eth.send_raw_transaction(tx).hex()
        logger.info(f"Transaction to {to}: {tx_hash}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Transact to {to} failed.")
        return receipt
