from typing import cast

from web3 import Web3
from web3._utils.datatypes import PropertyCheckingFactory
import eth_account

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
            import random, string
            self.eth_acct = eth_account.Account.create(
                ''.join(random.choices(string.ascii_letters, k=3))
            )
        else:
            self.eth_acct = eth_account.Account.from_key(private_key)

        self.address = self.eth_acct.address
        self.private_key = self.eth_acct.key

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