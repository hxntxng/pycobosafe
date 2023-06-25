from pycobosafe.account import CoboSafeAccount
from pycobosafe.factory import CoboFactory
from pycobosafe.gnosissafe import GnosisSafe

CHAIN = "bsc-main"

COBO_FACTORY = "0x51e6540A5E766EB864aa32F548433D892Fd6008a"
SAFE = "0xeaF95b67170Fca1E5C026880287e77b3638b2F81"
COBO_SAFE = "0x70bcb58b10f24bc2d95E77C9facBB276a7b4c150"


def test_cobo_contract():
    s = GnosisSafe(SAFE)
    assert s.threshold > 0
    assert len(s.owners) > 0

    c = CoboSafeAccount(COBO_SAFE)
    assert len(c.delegates) > 0
    assert c.wallet_address == SAFE

    f = CoboFactory(COBO_FACTORY)
    assert f.get_address("CoboSafeAccount")

    r = f.get_all_impls()
    print(r)
    assert len(r) > 0
