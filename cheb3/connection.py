from typing import Any
from hexbytes import HexBytes

from web3 import Web3
from web3.middleware import geth_poa_middleware

from cheb3.account import Account
from cheb3.contract import Contract


class Connection:
    r"""
    Creates a connection to a provider.

    Arguments:
        endpoint_uri (str): The full URI to the RPC endpoint.
    """

    def __init__(self, endpoint_uri: str) -> None:
        self.w3 = Web3(Web3.HTTPProvider(endpoint_uri))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise Exception(f"Could not connect to {endpoint_uri}.")

    def account(self, private_key: str = None) -> Account:
        account_factory = Account.factory(self.w3)
        return account_factory(private_key)

    def contract(
        self,
        signer: Account = None,
        contract_name: str = "",
        address: str = None,
        **kwargs: Any,
    ) -> Contract:
        contract_factory = Contract.factory(self.w3, contract_name)
        return contract_factory(signer, address, **kwargs)

    def get_balance(self, address: str) -> int:
        return self.w3.eth.get_balance(address)

    def get_storage_at(self, address: str, slot: int) -> HexBytes:
        return self.w3.eth.get_storage_at(address, slot)
