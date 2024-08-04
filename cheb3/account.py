from typing import cast, Union
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

    def call(self, to: HexStr, data: HexStr = "0x", **kwargs) -> HexBytes:
        """Interact with a smart contract without creating a new
        transaction on the blockchain.

        :param to: The address of the contract.
        :type to: HexStr
        :param data: The transaction data, defaults to `0x`.
        :type data: HexStr

        Keyword Args:
            state_override (dict): Specify the state override set.
                View `Geth documentation <https://geth.ethereum.org/docs/interacting-with-geth/rpc/ns-eth#eth-call>`_ for more details.

        :rtype: ~hexbytes.main.HexBytes
        """

        to = Web3.to_checksum_address(to)

        return self.w3.eth.call(
            {
                "to": to,
                "from": self.address,
                "data": data,
            },
            state_override=kwargs.get("state_override", None),
        )

    def send_transaction(
        self, to: Union[HexStr, None], value: int = 0, data: HexStr = "0x", **kwargs
    ) -> Union[TxReceipt, HexStr]:
        """Transfer ETH or interact with a smart contract.

        :param to: The address of the receiver.
        :type to: Union[HexStr, None]
        :param value: The amount to transfer, defaults to 0 (wei).
        :type value: int
        :param data: The transaction data, defaults to `0x`.
        :type data: HexStr

        Keyword Args:
            gas_price (int): Specifies the gas price for the transaction.
            gas_limit (int): Specifies the maximum gas the transaction can use.
            nonce (int): Allows to overwrite pending transactions that use
                the same nonce.
            access_list (List[Dict]): Specifies a list of addresses and storage
                keys that the transaction plans to access (EIP-2930).
            wait_for_receipt (bool): Waits for the transaction receipt,
                defaults to :const:`True`.

        :returns: The transaction receipt or the transaction hash if
            `wait_for_receipt` is :const:`False`.
        :rtype: Union[TxReceipt, HexStr]
        """

        if to:
            to = Web3.to_checksum_address(to)

        tx = {
            "from": self.address,
            "to": to,
            "chainId": self.w3.eth.chain_id,
            "nonce": kwargs.get("nonce", self.w3.eth.get_transaction_count(self.address)),
            "value": value,
            "gasPrice": kwargs.get("gas_price", self.w3.eth.gas_price),
            "data": data,
        }
        if kwargs.get("access_list"):
            tx["accessList"] = kwargs["access_list"]
        try:
            estimate_gas = self.w3.eth.estimate_gas(tx) + GAS_BUFFER
        except Exception:
            estimate_gas = 3000000
        tx["gas"] = kwargs.get("gas_limit", estimate_gas)
        tx = self.eth_acct.sign_transaction(tx).rawTransaction
        tx_hash = self.w3.eth.send_raw_transaction(tx).hex()
        logger.info(f"Transaction to {to}: {tx_hash}")
        if not kwargs.get("wait_for_receipt", True):
            return tx_hash
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Transact to {to} failed.")
        return receipt
