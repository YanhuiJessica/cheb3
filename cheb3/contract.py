from typing import cast, Optional
from hexbytes import HexBytes

from web3 import Web3
from web3.contract import ContractFunction, ContractFunctions, ContractCaller
from web3._utils.datatypes import PropertyCheckingFactory
from web3._utils.abi import filter_by_type
from web3.types import ABI, TxReceipt
from eth_typing import ChecksumAddress
import eth_account

from loguru import logger


class Contract:

    # set during class construction
    w3: Web3 = None

    def __init__(self, signer: eth_account.Account, address: str = None, **kwargs) -> None:

        if self.w3 is None:
            raise AttributeError(
                'The `Contract` class has not been initialized. Please use the '
                '`Connection.contract` interface to create a contract.'
            )

        self.signer = signer
        if address:
            self.address = address
            self.instance = self.w3.eth.contract(address=address, **kwargs)
            self._init_functions()
        else:
            self.instance = self.w3.eth.contract(**kwargs)

    def deploy(self, *constructor_args, **kwargs) -> None:
        tx = self.signer.sign_transaction(
            self.instance.constructor(*constructor_args).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'nonce': self.w3.eth.get_transaction_count(self.signer.address),
                'gas': kwargs.get(
                    'gas_limit',
                    self.instance.constructor(*constructor_args)
                        .estimate_gas({'from': self.signer.address})
                ),
                'gasPrice': kwargs.get('gas_price', self.w3.eth.gas_price),
                'value': kwargs.get('value', 0)
            })).rawTransaction
        logger.debug(f'Deploying {type(self).__name__} ...')
        tx_hash = self.w3.eth.send_raw_transaction(tx).hex()
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Failed to deploy {type(self).__name__}.")
        logger.info(f'Deployed {type(self).__name__} at {receipt.contractAddress}')
        self.address = receipt.contractAddress
        self.instance = self.w3.eth.contract(self.address, abi=self.instance.abi)
        self._init_functions()

    def _init_functions(self) -> None:
        self.functions = ContractFunctionsWrapper(self.signer, self.instance.abi, self.w3, self.address)
        self.caller = ContractCaller(self.instance.abi, self.w3, self.address)

    @classmethod
    def factory(cls, w3: Web3, contract_name: str = '') -> 'Contract':
        contract = cast(Contract, PropertyCheckingFactory(
            contract_name or cls.__name__,
            (cls,),
            {'w3': w3}
        ))
        return contract

    def get_balance(self) -> int:
        return self.w3.eth.get_balance(self.address)

    def get_storage_at(self, slot: int) -> HexBytes:
        return self.w3.eth.get_storage_at(self.address, slot)


class ContractFunctionsWrapper(ContractFunctions):

    def __init__(self,
                 signer: eth_account.Account,
                 abi: ABI,
                 web3: Web3,
                 address: Optional[ChecksumAddress] = None
                 ) -> None:
        self.abi = abi
        self.web3 = web3
        self.address = address
        self.signer = signer

        if self.abi:
            self._functions = filter_by_type('function', self.abi)
            for func in self._functions:
                setattr(
                    self,
                    func['name'],
                    ContractFunctionWrapper.factory(
                        func['name'],
                        web3=self.web3,
                        signer=self.signer,
                        contract_abi=self.abi,
                        address=self.address,
                        function_identifier=func['name']))


class ContractFunctionWrapper(ContractFunction):

    signer: eth_account.Account = None

    def send_transaction(self, **kwargs) -> TxReceipt:
        tx = self.signer.sign_transaction(self.build_transaction({
            'chainId': self.web3.eth.chain_id,
            'nonce': self.web3.eth.get_transaction_count(self.signer.address),
            'gas': kwargs.get('gas_limit', self.estimate_gas({'from': self.signer.address})),
            'gasPrice': kwargs.get('gas_price', self.web3.eth.gas_price),
            'value': kwargs.get('value', 0)
        })).rawTransaction
        tx_hash = self.web3.eth.send_raw_transaction(tx).hex()
        logger.debug(f'Transact to ({self.address}).{self.function_identifier} pending...')
        logger.info(f'({self.address}).{self.function_identifier} transaction hash: {tx_hash}')
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Transact to ({self.address}).{self.function_identifier} errored.")
        return receipt
