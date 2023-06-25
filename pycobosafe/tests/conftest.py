import pytest
from brownie import network


@pytest.fixture(scope="module", autouse=True)
def auto_switch_chain(request):
    new_chain = getattr(request.module, "CHAIN", None)

    current_chain = network.show_active()
    if new_chain and current_chain != new_chain:
        if network.is_connected():
            network.disconnect()
        network.connect(new_chain)
        yield
        # switch back.
        if network.is_connected():
            network.disconnect()
        network.connect(current_chain)
    else:
        yield
