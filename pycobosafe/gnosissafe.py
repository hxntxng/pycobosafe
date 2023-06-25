from functools import lru_cache

import eth_abi

from .utils import ZERO_ADDRESS, Operation, abi_encode_with_sig, load_contract


class GnosisSafe(object):
    def __init__(self, cobosafe_addr, owner=None) -> None:
        self.contract = load_contract("GnosisSafe", cobosafe_addr)
        self.owner = owner

        threshold = self.threshold
        owners = self.owners

        if owner:
            assert threshold == 1, f"threshold = {threshold} > 1, not supported now"
            assert (
                str(self.owner).lower() in owners
            ), f"owner {owner} not in safe owners list {owners}"
        else:
            if threshold == 1:
                self.owner = owners[0]

    @property
    @lru_cache(maxsize=1)
    def address(self):
        return self.contract.address

    @property
    @lru_cache(maxsize=1)
    def threshold(self):
        return self.contract.getThreshold()

    @property
    @lru_cache(maxsize=1)
    def owners(self):
        return self.contract.getOwners()

    @classmethod
    def create_single_signature(cls, address):
        return eth_abi.encode(["(address,address)"], [(address, address)]) + b"\x01"

    def exec_transaction(
        self, to, data, value=0, signatures=None, call_type=Operation.CALL
    ):
        if signatures is None:
            assert (
                self.threshold == 1
            ), f"Can not exec as threshold = {self.threshold} > 1"
            signatures = self.create_single_signature(self.owner)

        return self.contract.execTransaction(
            to,
            value,
            data,
            call_type,  # 0 for call, 1 for delegatecall
            0,
            0,
            0,
            ZERO_ADDRESS,
            ZERO_ADDRESS,
            signatures,
            {"from": self.owner},
        )

    def exec_transaction_ex(
        self, to, func_sig, args, value=0, signatures=None, call_type=Operation.CALL
    ):
        data = abi_encode_with_sig(func_sig, args)
        return self.exec_transaction(to, data, value, signatures, call_type)

    def exec_raw_tx(self, tx):
        to = tx["to"]
        value = tx["value"]
        data = tx["data"]
        self.exec_transaction(to, data, value)

    def delegate_call(self, to, func_sig, args):
        data = abi_encode_with_sig(func_sig, args)
        return self.exec_transaction(to, data, 0, call_type=Operation.DELEGATE_CALL)

    def enable_module(self, cobo_safe_module):
        self.exec_transaction_ex(
            self.address, "enableModule(address)", [cobo_safe_module]
        )

    def approve_token(self, token, to, amount=None):
        if amount is None:
            amount = 2**256 - 1

        self.exec_transaction_ex(token, "approve(address,uint256)", (to, amount))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.address}>"
