from typing import Any

from web3 import Web3

from cheb3.account import Account
from cheb3.contract import Contract


class Connection:
    r"""
    Creates a connection to a provider.

    Arguments:
        endpoint_uri (str): The full URI to the RPC endpoint.
    """

    def __init__(self, endpoint_uri: str) -> None:
        from web3.middleware import geth_poa_middleware

        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.isConnected():
            raise Exception(f"Could not connect to {endpoint_uri}.")

    def account(self, private_key: str = None) -> Account:
        account_factory = Account.factory(self.w3)
        return account_factory(private_key)

    def contract(self,
                 signer: Account = None,
                 contract_name: str = '',
                 address: str = None,
                 **kwargs: Any) -> Contract:
        contract_factory = Contract.factory(self.w3, contract_name)
        return contract_factory(signer, address, **kwargs)
