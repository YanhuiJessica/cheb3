from typing import cast
from hexbytes import HexBytes
import random
import string

from web3 import Web3
from web3._utils.datatypes import PropertyCheckingFactory
from web3.types import TxReceipt
import eth_account

from loguru import logger


class Account:

    w3: Web3 = None

    def __init__(self, private_key: str = None) -> None:
        '''
        It will create a new account if `private_key` is not given.
        '''

        if self.w3 is None:
            raise AttributeError(
                'The `Account` class has not been initialized. Please use the '
                '`Connection.account` interface to create an account.'
            )

        if private_key is None:
            self.eth_acct = eth_account.Account.create(
                ''.join(random.choices(string.ascii_letters, k=3))
            )
        else:
            self.eth_acct = eth_account.Account.from_key(private_key)

        self.address = self.eth_acct.address
        self.private_key = self.eth_acct.key.hex()

    @classmethod
    def factory(cls, w3: Web3) -> 'Account':
        eth_acct = cast(Account, PropertyCheckingFactory(
            cls.__name__,
            (cls,),
            {'w3': w3}
        ))
        return eth_acct

    def get_balance(self) -> int:
        return self.w3.eth.get_balance(self.eth_acct.address)

    def call(self,
             to: str,
             data: str = '0x'
             ) -> HexBytes:
        '''
        Interact with a smart contract without creating a new transaction
        on the blockchain.
        '''

        return self.w3.eth.call({
            'to': to,
            'data': data,
        })

    def send_transaction(self,
                         to: str,
                         value: int = 0,
                         data: str = '0x',
                         **kwargs
                         ) -> TxReceipt:
        '''
        Transfer ETH to another account or interact with a smart contract.

        Arguments:
            to (str): The address of the receiver.
            value (int): The amount to transfer.
            data (str): The transaction data, a hex string starts with '0x'.
            gas_price (int)
            gas_limit (int)
        '''

        tx = {
            'from': self.address,
            'to': to,
            'chainId': self.w3.eth.chain_id,
            'nonce': self.w3.eth.get_transaction_count(self.eth_acct.address),
            'value': value,
            'gasPrice': kwargs.get('gas_price', self.w3.eth.gas_price),
            'data': data,
        }
        tx['gas'] = kwargs.get('gas_limit', self.w3.eth.estimate_gas(tx))
        tx = self.eth_acct.sign_transaction(tx).rawTransaction
        tx_hash = self.w3.eth.send_raw_transaction(tx).hex()
        logger.info(f'Transaction to {to}: {tx_hash}')
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt.status:
            raise Exception(f"Transact to {to} failed.")
        return receipt
