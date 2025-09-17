from typing import cast, Union
from hexbytes import HexBytes
import random
import string

from web3 import Web3
from web3._utils.datatypes import PropertyCheckingFactory
from web3.types import TxReceipt, AccessList
from eth_typing import HexStr
import eth_account
from eth_account.datastructures import SignedMessage, SignedSetCodeAuthorization

from cheb3.constants import GAS_BUFFER
from cheb3.helper import Web3Helper

from loguru import logger


class Account:
    """Please use :func:`cheb3.Connection.account` interface to
    create an account instance associated with the connection.

    To create an account instance with the given private key:

       >>> account = conn.account("0xpr1vateK3y")

    If no private key is provided, a randomly generated private key will be used to create an account instance.
    """

    w3: Web3Helper = None

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
    def factory(cls, w3: Web3Helper) -> "Account":
        eth_acct = cast(Account, PropertyCheckingFactory(cls.__name__, (cls,), {"w3": w3}))
        return eth_acct

    def sign_raw_message_hash(self, message_hash: HexStr) -> SignedMessage:
        """Signs a raw message hash with the account's private key.

        Examples:

            >>> msg_hash = Web3.solidity_keccak(["uint256", "address"], [10, account.address])
            >>> sig = account.sign_raw_message_hash(msg_hash)
            >>> sig
            SignedMessage(message_hash=HexBytes('0xe17bbd560054251725995886026ff6de42a496c52d90cc3ba61a5a97e3cda128'),
            r=97529042910999732419272940067647801719735539298841301635952986349446066833551,
            s=1555140386957721792444331594584329432191181296221261541177951220673132507501,
            v=28,
            signature=HexBytes('0xd79f7b6a5c832d450820a60ad7a99c2df98708c417c7c5cb52d0ee270cf7888f03702da2e2862f0d30386d32610c3f833d7dbd8d0ea06b7db2beb83d3656316d1c'))
            >>> sig.signature.hex()
            'd79f7b6a5c832d450820a60ad7a99c2df98708c417c7c5cb52d0ee270cf7888f03702da2e2862f0d30386d32610c3f833d7dbd8d0ea06b7db2beb83d3656316d1c'
            >>> sig.r
            97529042910999732419272940067647801719735539298841301635952986349446066833551


        :param message_hash: The hash of the message to sign.
        :type message_hash: HexStr
        :returns: The signed message as a HexBytes object.
        :returns: Various details about the signature - most
          importantly the fields: v, r, and s
        :rtype: ~eth_account.datastructures.SignedMessage
        """
        return eth_account.Account._sign_hash(message_hash, self.private_key)

    def sign_authorization(self, target: HexStr, is_sender: bool = True, **kwargs) -> SignedSetCodeAuthorization:
        """Signs an authorization to be included in a EIP-7702 transaction.

        Examples:

            >>> # If this account is to sign the EIP-7702 transaction next
            >>> account.sign_authorization(delegate_contract.address)
            >>> # If the EIP-7702 transaction is sent by another account
            >>> account.sign_authorization(delegate_contract.address, is_sender=False)

        :param target: The address of the smart contract code to be associated with the account.
        :type target: HexStr
        :param is_sender: If the account is also the sender of the EIP-7702 transaction.
            Its default value is :const:`True`, which means the nonce to be signed will
            be 1 higher than the current nonce of the account. This is because the nonce
            is increased before the transaction execution and again when processing
            the authorization. It is not used when the keyword argument `nonce` is set.
        :type is_sender: bool

        Keyword Args:
            chain_id (int): The chain ID for the chain where the account is located,
                defaults to the chain ID of the current :class:`Connection <cheb3.connection.Connection>`.
            nonce (int): Allows to sign an authorization with a specific nonce.
        """
        auth = {
            "chainId": kwargs.get("chain_id", self.w3.eth.chain_id),
            "nonce": kwargs.get("nonce", self.w3.eth.get_transaction_count(self.address) + is_sender),
            "address": target,
        }
        return self.eth_acct.sign_authorization(auth)

    def get_balance(self) -> int:
        """Returns the balance of the account instance."""
        return self.w3.eth.get_balance(self.eth_acct.address)

    def create_access_list(self, to: Union[HexStr, None], value: int = 0, data: HexStr = "0x", **kwargs) -> AccessList:
        """Creates an EIP-2930 type access list based on
        the given transaction data.

        :param to: The address of the receiver.
        :type to: Union[HexStr, None]
        :param value: The amount to transfer, defaults to 0 (wei).
        :type value: int
        :param data: The transaction data, defaults to `0x`.
        :type data: HexStr

        Keyword Args:
            block_identifier (str): A string representing a block number (hexadecimal)
                or `latest` or `pending`, defaults is `latest`.
            gas_price (int): Specifies the gas price for the **LEGACY** transaction.
            max_priority_fee_per_gas (int): Specifies the fee that goes to the miner,
                defaults to the value of :attr:`~web3.eth.Eth.max_priority_fee`.
            max_fee_per_gas (int): Specifies the maximum amount you are willing to pay,
                inclusive of `baseFeePerGas` and `maxPriorityFeePerGas`. Its default value
                is the sum of `maxPriorityFeePerGas` and twice the `baseFeePerGas` of the latest block.
            gas_limit (int): Specifies the maximum gas the transaction can use.
            authorization_list (List[SignedSetCodeAuthorization]): Specifies a
                list of signed authorizations (EIP-7702).

        :returns: An access list contains all storage slots and addresses read
            and written by the transaction, except for the sender account and
            the precompiles.
        :rtype: AccessList
        """

        if to:
            to = Web3.to_checksum_address(to)

        tx = self.w3._build_transaction(self.address, kwargs)
        tx.update(
            {
                "to": to,
                "value": value,
                "data": data,
            }
        )
        try:
            estimate_gas = self.w3.eth.estimate_gas(tx) + GAS_BUFFER
        except Exception:
            estimate_gas = 3000000
        tx["gas"] = kwargs.get("gas_limit", estimate_gas)
        return self.w3.eth.create_access_list(tx, kwargs.get("block_identifier", "latest"))["accessList"]

    def call(self, to: HexStr, data: HexStr = "0x", **kwargs) -> HexBytes:
        """Without a :class:`Contract <cheb3.contract.Contract>` instance,
        interacts with a smart contract without creating a new
        transaction on the blockchain.

        :param to: The address of the contract.
        :type to: HexStr
        :param data: The transaction data, defaults to `0x`.
        :type data: HexStr

        Keyword Args:
            state_override (dict): Specify the state override set.
                View `Geth documentation <https://geth.ethereum.org/docs/interacting-with-geth/rpc/ns-eth#eth-call>`_
                for more details.

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
        """Transfers ETH or interacts with a smart contract without a :class:`Contract <cheb3.contract.Contract>` instance.

        :param to: The address of the receiver.
        :type to: Union[HexStr, None]
        :param value: The amount to transfer, defaults to 0 (wei).
        :type value: int
        :param data: The transaction data, defaults to `0x`.
        :type data: HexStr

        Keyword Args:
            gas_price (int): Specifies the gas price for the **LEGACY** transaction.
            max_priority_fee_per_gas (int): Specifies the fee that goes to the miner,
                defaults to the value of :attr:`~web3.eth.Eth.max_priority_fee`.
            max_fee_per_gas (int): Specifies the maximum amount you are willing to pay,
                inclusive of `baseFeePerGas` and `maxPriorityFeePerGas`. Its default value
                is the sum of `maxPriorityFeePerGas` and twice the `baseFeePerGas` of the latest block.
            gas_limit (int): Specifies the maximum gas the transaction can use.
            nonce (int): Allows to overwrite pending transactions that use
                the same nonce.
            access_list (List[Dict]): Specifies a list of addresses and storage
                keys that the transaction plans to access (EIP-2930).
            authorization_list (List[SignedSetCodeAuthorization]): Specifies a
                list of signed authorizations (EIP-7702).
            wait_for_receipt (bool): Waits for the transaction receipt,
                defaults to :const:`True`.

        :returns: The transaction receipt or the transaction hash if
            `wait_for_receipt` is :const:`False`.
        :rtype: Union[TxReceipt, HexStr]
        """

        if to:
            to = Web3.to_checksum_address(to)

        tx = self.w3._build_transaction(self.address, kwargs)
        tx.update(
            {
                "to": to,
                "value": value,
                "data": data,
            }
        )
        try:
            estimate_gas = self.w3.eth.estimate_gas(tx) + GAS_BUFFER
        except Exception:
            estimate_gas = 3000000
        tx["gas"] = kwargs.get("gas_limit", estimate_gas)
        tx = self.eth_acct.sign_transaction(tx).raw_transaction
        tx_hash = self.w3.eth.send_raw_transaction(tx).hex()
        logger.info(f"Transaction to {to}: {tx_hash}")
        if not kwargs.get("wait_for_receipt", True):
            return tx_hash
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Transact to {to} failed.")
        return receipt
