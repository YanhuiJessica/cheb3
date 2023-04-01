import pytest
from web3.exceptions import MismatchedABI

from cheb3.utils import encode_with_signature


def test_function_with_no_args():
    assert encode_with_signature("foo()") == "0xc2985578"


def test_function_with_multiple_args():
    address = 0x617F2E2FD72FD9D5503197092AC168C91465E7F2
    expected = f"0xbd0d639f{address:0>64x}{10:0>64x}"
    assert encode_with_signature("foo(address,uint256)", hex(address), 10) == expected


def test_function_with_bytes():
    assert (
        encode_with_signature("foo(bytes)", b"test")
        == f"0x30c8d1da{32:0>64x}{4:0>64}{b'test'.hex():0<64}"
    )


def test_provided_args_cnt_less_than_expected():
    with pytest.raises(MismatchedABI):
        encode_with_signature("foo(uint256)")


def test_provided_args_cnt_more_than_expected():
    with pytest.raises(MismatchedABI):
        encode_with_signature("foo()", 1)


def test_uint_type_alias():
    assert encode_with_signature("foo(uint)", 1) == encode_with_signature(
        "foo(uint256)", 1
    )
    assert encode_with_signature("foo(uint)", 1) == f"0x2fbebd38{1:0>64}"


def test_int_type_alias():
    assert encode_with_signature("foo(int)", 1) == encode_with_signature(
        "foo(int256)", 1
    )
    assert encode_with_signature("foo(int)", 1) == f"0x4c970b2f{1:0>64}"
