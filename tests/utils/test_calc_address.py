from cheb3.utils import calc_create_address, calc_create2_address

addr = "0x518C2143bDd79d3bc060BC4883d92D545D3E3bb0"


def test_calc_create_address():
    target = "0x53D144BcF44de3DeE630b1CFEabD91AC3d3caF5a"
    assert calc_create_address(addr, 1) == target
    assert calc_create_address(addr.upper(), 1) == target


def test_calc_create2_address():
    target = "0x233030BEE50d246C5E53697B92194B73AceAB62e"
    init_code = (
        "0x6019600c60003960196000f36f06bc8d9e5e9d436617b88de704a9f30760005260206000f3"
    )
    salt = 29151182470403780934905230237472728569385652082807904518183748516236584329707

    assert calc_create2_address(addr, salt, init_code) == target
    assert calc_create2_address(addr.lower(), salt, init_code) == target
