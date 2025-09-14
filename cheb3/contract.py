from typing import cast, Optional, Union, Sequence
from hexbytes import HexBytes

from web3 import Web3, AsyncWeb3
from web3.contract.contract import (
    ContractFunction,
    ContractFunctions,
    ContractCaller,
)
from web3.contract.base_contract import (
    NonExistentFallbackFunction,
    NonExistentReceiveFunction,
)
from web3._utils.datatypes import PropertyCheckingFactory
from web3._utils.abi import (
    filter_abi_by_type,
    fallback_func_abi_exists,
    receive_func_abi_exists,
)
from web3._utils.abi_element_identifiers import FallbackFn, ReceiveFn
from web3.types import TxReceipt, AccessList
from eth_utils import abi_to_signature
from eth_typing import ABI, ABIFunction, ChecksumAddress, HexStr
import eth_account

from cheb3.account import Account
from cheb3.helper import Web3Helper
from cheb3.constants import GAS_BUFFER

from loguru import logger


class Contract:
    """Please use :func:`cheb3.Connection.contract` interface to
    create a contract instance associated with the connection.
    """

    # set during class construction
    w3: Web3Helper = None

    def __init__(self, signer: Account = None, address: str = None, **kwargs) -> None:
        """
        You can read states from the blockchain even if `signer` is not given.

        The keyword arguments follow `web3.py <https://web3py.readthedocs.io/en/stable/web3.contract.html#contract-factories>`_. If the contract address and ABI are
        provided, you can read the contract states; if a signer, contract address, and
        ABI are provided, you can interact with the contract; if a signer, ABI, and
        bytecode are provided, you can deploy the contract and interact with it.
        """

        if self.w3 is None:
            raise AttributeError(
                "The `Contract` class has not been initialized. Please use the "
                "`Connection.contract` interface to create a contract."
            )

        self.signer = signer.eth_acct if signer else None
        if address:
            self.address = address
            self.instance = self.w3.eth.contract(address=address, **kwargs)
            self._init_functions()
        else:
            self.address = None
            self.instance = self.w3.eth.contract(**kwargs)

    def deploy(self, *constructor_args, **kwargs) -> None:
        """Deploys the contract.

        :param constructor_args: Constructor arguments.

        Keyword Args:
            value (int): The amount to transfer, defaults to 0 (wei).
            gas_price (int): Specifies the gas price for the deployment.
            max_priority_fee_per_gas (int): Specifies the fee that goes to the miner,
                defaults to the value of :attr:`~web3.eth.Eth.max_priority_fee`.
            max_fee_per_gas (int): Specifies the maximum amount you are willing to pay,
                inclusive of `baseFeePerGas` and `maxPriorityFeePerGas`. Its default value
                is the sum of `maxPriorityFeePerGas` and twice the `baseFeePerGas` of the latest block.
            gas_limit (int): Specifies the maximum gas the deployment can use.
            proxy (bool): A minimal proxy contract (ERC-1167) will be deployed
                and connected to the logic contract if set to :const:`True`,
                defaults to :const:`False`.
            access_list (List[Dict]): Specifies a list of addresses and storage
                keys that the transaction plans to access (EIP-2930). It will only
                be used in logic contract deployment if `proxy` is :const:`True`.
        """
        if not self.signer:
            raise AttributeError("The `signer` is missing.")

        if self.address:
            logger.info(f"Contract {type(self).__name__} has already been deployed at {self.address}.")
            return

        # EIP-7702 transaction cannot be used to create contract
        if "authorization_list" in kwargs:
            del kwargs["authorization_list"]
        tx = self.w3._build_transaction(self.signer.address, kwargs)
        tx["value"] = kwargs.get("value", 0)
        tx = self.instance.constructor(*constructor_args).build_transaction(tx)
        try:
            estimate_gas = self.w3.eth.estimate_gas(tx) + GAS_BUFFER
        except Exception:
            estimate_gas = 3000000
        tx["gas"] = kwargs.get("gas_limit", estimate_gas)
        tx = self.signer.sign_transaction(tx).raw_transaction
        logger.debug(f"Deploying {type(self).__name__} ...")
        tx_hash = self.w3.eth.send_raw_transaction(tx).hex()
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Failed to deploy {type(self).__name__}.")
        logger.info(
            f"""The {
                "logic " if kwargs.get('proxy', False) else ""
            }{type(self).__name__} is deployed at {receipt.contractAddress}"""
        )
        self.address = receipt.contractAddress

        if kwargs.get("proxy", False):
            proxy_bytecode = f"3d602d80600a3d3981f3363d3d373d3d3d363d73{self.address[2:].lower()}5af43d82803e903d91602b57fd5bf3"
            tx = {
                "from": self.signer.address,
                "to": None,
                "chainId": self.w3.eth.chain_id,
                "nonce": self.w3.eth.get_transaction_count(self.signer.address),
                "gasPrice": kwargs.get("gas_price", self.w3.eth.gas_price),
                "data": proxy_bytecode,
            }
            tx["gas"] = kwargs.get("gas_limit", self.w3.eth.estimate_gas(tx) + GAS_BUFFER)
            tx = self.signer.sign_transaction(tx).raw_transaction
            logger.debug("Deploying the proxy ...")
            tx_hash = self.w3.eth.send_raw_transaction(tx).hex()
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            if not receipt.status:
                raise Exception("Failed to deploy the proxy.")
            logger.info(f"The proxy is deployed at {receipt.contractAddress}")
            self.address = receipt.contractAddress

        self.instance = self.w3.eth.contract(self.address, abi=self.instance.abi)
        self._init_functions()

    @staticmethod
    def get_fallback_function(abi: ABI, w3: Web3Helper, signer: eth_account.Account, address: str):
        if abi and fallback_func_abi_exists(abi):
            fallback_abi = filter_abi_by_type("fallback", abi)[0]
            return ContractFunctionWrapper.factory(
                "fallback",
                w3=w3,
                signer=signer,
                contract_abi=abi,
                address=address,
                abi_element_identifier=FallbackFn,
                abi=fallback_abi,
            )()
        else:
            return cast(ContractFunctionWrapper, NonExistentFallbackFunction())

    @staticmethod
    def get_receive_function(abi: ABI, w3: Web3Helper, signer: eth_account.Account, address: str):
        if abi and receive_func_abi_exists(abi):
            receive_abi = filter_abi_by_type("receive", abi)[0]
            return ContractFunctionWrapper.factory(
                "receive",
                w3=w3,
                signer=signer,
                contract_abi=abi,
                address=address,
                abi_element_identifier=ReceiveFn,
                abi=receive_abi,
            )()
        else:
            return cast(ContractFunctionWrapper, NonExistentReceiveFunction())

    def _init_functions(self) -> None:
        self.functions = ContractFunctionsWrapper(self.signer, self.instance.abi, self.w3, self.address)
        self.caller = ContractCaller(self.instance.abi, self.w3, self.address)

        self.fallback = self.get_fallback_function(self.instance.abi, self.w3, self.signer, self.address)
        self.receive = self.get_receive_function(self.instance.abi, self.w3, self.signer, self.address)

    @classmethod
    def factory(cls, w3: Web3Helper, contract_name: str = "") -> "Contract":
        contract = cast(
            Contract,
            PropertyCheckingFactory(contract_name or cls.__name__.lower(), (cls,), {"w3": w3}),
        )
        return contract

    def get_balance(self) -> int:
        """Returns the balance of the contract instance."""
        return self.w3.eth.get_balance(self.address)

    def get_storage_at(self, slot: int) -> HexBytes:
        """Returns the value from a storage position for the contract instance.

        :param slot: The storage slot.
        :type slot: int

        :rtype: ~hexbytes.main.HexBytes
        """
        return self.w3.eth.get_storage_at(self.address, slot)


class ContractFunctionsWrapper(ContractFunctions):
    def __init__(
        self,
        signer: eth_account.Account,
        abi: ABI,
        w3: Union["Web3", "AsyncWeb3"],
        address: Optional[ChecksumAddress] = None,
    ) -> None:
        self.signer = signer
        self.abi = abi
        self.w3 = w3
        self.address = address
        _functions: Sequence[ABIFunction] = None

        if self.abi:
            _functions = sorted(
                filter_abi_by_type("function", self.abi),
                key=lambda fn: (fn["name"], len(fn.get("inputs", []))),
            )
            for func in _functions:
                abi_signature = abi_to_signature(func)
                function_factory = ContractFunctionWrapper.factory(
                    abi_signature,
                    w3=self.w3,
                    signer=self.signer,
                    contract_abi=self.abi,
                    address=self.address,
                    abi=func,
                )

                if func["name"] not in self.__dict__:
                    setattr(self, func["name"], function_factory)

                setattr(self, f"_{abi_signature}", function_factory)

        if _functions:
            self._functions = _functions


class ContractFunctionWrapper(ContractFunction):
    signer: eth_account.Account = None

    def send_transaction(self, **kwargs) -> Union[TxReceipt, HexStr]:
        """Signs and sends the transaction.

        Keyword Args:
            value (int): The amount to transfer, defaults to 0 (wei).
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

        if not self.signer:
            raise AttributeError("The `signer` is missing.")

        tx = self.w3._build_transaction(self.signer.address, kwargs)
        tx = self.build_transaction(tx)
        tx["value"] = kwargs.get("value", 0)
        try:
            estimate_gas = self.estimate_gas(tx) + GAS_BUFFER
        except Exception:
            estimate_gas = 3000000
        tx["gas"] = kwargs.get("gas_limit", estimate_gas)
        raw_tx = self.signer.sign_transaction(tx).raw_transaction
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx).hex()
        func_name = (
            self.abi_element_identifier
            if isinstance(self.abi_element_identifier, str)
            else self.abi_element_identifier.__name__
        )
        logger.info(f"({self.address}).{func_name} transaction hash: {tx_hash}")
        if not kwargs.get("wait_for_receipt", True):
            return tx_hash
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Transact to ({self.address}).{func_name} errored.")
        return receipt

    def create_access_list(self, **kwargs) -> AccessList:
        """Creates an EIP-2930 type access list based on
        the function call data.
        
        Keyword Args:
            block_identifier (str): A string representing a block number (hexadecimal)
                or `latest` or `pending`, defaults is `latest`.
            value (int): The amount to transfer, defaults to 0 (wei).
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

        if not self.signer:
            raise AttributeError("The `signer` is missing.")

        tx = self.w3._build_transaction(self.signer.address, kwargs)
        tx = self.build_transaction(tx)
        tx["value"] = kwargs.get("value", 0)
        try:
            estimate_gas = self.estimate_gas(tx) + GAS_BUFFER
        except Exception:
            estimate_gas = 3000000
        tx["gas"] = kwargs.get("gas_limit", estimate_gas)
        return self.w3.eth.create_access_list(tx, kwargs.get("block_identifier", "latest"))["accessList"]
