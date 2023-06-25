import json
import os

import dotenv
from brownie import Contract, accounts, network
from pycobosafe.account import CoboSafeAccount
from web3 import Web3

# Connect to the network. A fork chain is used for test.
network.connect("polygon-main-fork")

# Load delegate's private key / keystore file and CoboSafe address.
dotenv.load_dotenv()
DELEGATE = accounts.load((os.getenv("DELEGATE")))
COBOSAFE = os.getenv("COBOSAFE")
assert DELEGATE and COBOSAFE, "delegate or cobosafe not set"

cobosafe = CoboSafeAccount(COBOSAFE, DELEGATE)

# You have to ensure the delegate has been correctly authorized by the safe owners before.
# If not, the transactions below will fail.

WMATIC = Web3.toChecksumAddress("0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270")

# (Option 1) Call contract with ABI in the brownie way.
ERC20_ABI = json.load(open(os.path.join(os.path.dirname(__file__), "ERC20.json")))
erc20 = Contract.from_abi("WMATIC", WMATIC, ERC20_ABI)
print(erc20.balanceOf(cobosafe.safe.address))

erc20.transfer(DELEGATE, 1, {"from": cobosafe})
print(erc20.balanceOf(cobosafe.safe.address))

# (Option 2) {"from": cobosafe} means:
tx = erc20.transfer.build(DELEGATE, 1)
cobosafe.exec_raw_tx(tx)
print(erc20.balanceOf(cobosafe.safe.address))

# (Option 3) Call directly with function signature.
cobosafe.exec_transaction_ex(WMATIC, "transfer(address,uint256)", [str(DELEGATE), 1])
print(erc20.balanceOf(cobosafe.safe.address))
