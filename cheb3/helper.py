from web3 import Web3
from eth_typing import HexStr


class Web3Helper(Web3):
    def _build_transaction(self, signer: HexStr, kwargs: dict) -> dict:
        tx = {
            "from": signer,
            "chainId": self.eth.chain_id,
            "nonce": kwargs.get("nonce", self.eth.get_transaction_count(signer)),
            "gasPrice": kwargs.get("gas_price", self.eth.gas_price),
        }
        if kwargs.get("max_fee_per_gas") or kwargs.get("max_priority_fee_per_gas"):
            del tx["gasPrice"]
            tx["maxPriorityFeePerGas"] = kwargs.get("max_priority_fee_per_gas", self.eth.max_priority_fee)
            tx["maxFeePerGas"] = kwargs.get(
                "max_fee_per_gas", tx["maxPriorityFeePerGas"] + self.eth.get_block("latest")["baseFeePerGas"] * 2
            )
        if kwargs.get("access_list"):
            tx["accessList"] = kwargs["access_list"]
        if kwargs.get("authorization_list"):
            tx["authorizationList"] = kwargs["authorization_list"]
            # Legacy transaction does not support authorization list
            if "gasPrice" in tx:
                del tx["gasPrice"]
                tx["maxPriorityFeePerGas"] = self.eth.max_priority_fee
                tx["maxFeePerGas"] = tx["maxPriorityFeePerGas"] + self.eth.get_block("latest")["baseFeePerGas"] * 2
        return tx
