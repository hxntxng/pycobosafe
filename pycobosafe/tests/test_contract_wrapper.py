from pycobosafe.utils import abi_encode_with_sig, load_contract

CHAIN = "mainnet"

ETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"


def test_contract_wrapper():
    token = load_contract("ERC20", ETH)
    assert token.decimals() == 18
    assert token.balanceOf(token.address) > 0
    assert token.symbol() == "WETH"

    assert token.transfer.call(token.address, 0) is True

    tx = token.transfer.build(token.address, 0, {"from": token.address})

    assert tx["value"] == 0
    assert tx["to"] == token.address
    assert tx["from"] == token.address
    transfer_data = abi_encode_with_sig("transfer(address,uint256)", [token.address, 0])
    assert tx["data"] == "0x" + transfer_data.hex()
