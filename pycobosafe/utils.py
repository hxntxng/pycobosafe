import json
import os
import random
import warnings

import eth_abi
import eth_utils
from brownie import Contract, accounts, network, web3
from brownie.network.contract import _ContractMethod, _get_tx

BASE = os.path.dirname(__file__)
ABI_DIR = os.path.join(BASE, "abi")


def printline():
    print("-" * 40)


def load_abi(name):
    path = os.path.join(ABI_DIR, f"{name}.json")
    assert os.path.exists(path), f"{path} not exists"
    return json.load(open(path))


def b32(name):
    if type(name) is str:
        name = bytes(name, "ascii")

    return eth_abi.encode(["bytes32"], [name])


def s32(data):
    if isinstance(data, bytes):
        return data.decode().strip("\x00")
    return data


def func_selector(func_signature: str):
    return eth_utils.keccak(text=func_signature)[:4]


def abi_encode_with_sig(func_signature, args=[]):
    selector = func_selector(func_signature)
    arg_sig = func_signature[func_signature.index("(") :]

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        return selector + eth_abi.encode_single(arg_sig, args)

    # Can NOT replace with eth_abi.encode([arg_sig], [args]) due to dynamic paras abi-encoding.
    # eth_abi.encode will treat `arg_sig` as a tuple, not args list.
    # but encode_single warns DeprecationWarning, catch it.


def rand_salt():
    return random.randbytes(32)


class Operation:
    CALL = 0
    DELEGATE_CALL = 1


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


def load_account(prikey_or_name):
    if not prikey_or_name:
        return None

    try:
        return accounts.load(prikey_or_name)
    except Exception:
        try:
            return accounts.add(prikey_or_name)
        except Exception:
            try:
                return accounts.at(prikey_or_name, True)
            except Exception:
                return prikey_or_name


def get_current_chain():
    return network.show_active()


def connect_new_chain(new_chain):
    current_chain = get_current_chain()
    if new_chain and current_chain != new_chain:
        if network.is_connected():
            network.disconnect()
        network.connect(new_chain)


def get_all_support_chains():
    return list(network.main.CONFIG.networks.keys())


def load_contract(name, address, abi=None, sender=None):
    if abi is None:
        abi = load_abi(name)
    assert type(abi) is list, f"Invalid ABI {abi}"

    if sender is None:
        sender = accounts.default

    return Contract.from_abi(name, address, abi, sender)


FACTORY_ADDRESS = "0xC0B00000e19D71fA50a9BB1fcaC2eC92fac9549C"

network.main.CONFIG.networks["avax-main"]["host"] = "https://rpc.ankr.com/avalanche"
network.main.CONFIG.networks["polygon-main"]["host"] = "https://rpc.ankr.com/polygon"
network.main.CONFIG.networks["mainnet"]["host"] = "https://rpc.ankr.com/eth"


# Add `build()` support to brownie contract container.
def _build_tx(self, *args):
    args, tx = _get_tx(self._owner, args)
    tx["to"] = self._address
    tx["data"] = self.encode_input(*args)
    return tx


_ContractMethod.build = _build_tx

SCAN_URLS = {
    1: "https://etherscan.io/address/",  # mainnet
    10: "https://optimistic.etherscan.io/address/",  # optimism
    56: "https://bscscan.com/address/",  # bsc
    137: "https://polygonscan.com/address/",  # polygon
    42161: "https://arbiscan.io/address/",  # arbitrum
    43114: "https://snowtrace.io/address/",  # avax
}


def get_address_url(addr):
    chainid = web3.chain_id
    assert chainid in SCAN_URLS, f"Unsupport chain {chainid} {get_current_chain()}"
    return SCAN_URLS[chainid] + str(addr)
