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
        == f"0x30c8d1da{32:0>64x}{4:0>64x}{b'test'.hex():0<64}"
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
    assert encode_with_signature("foo(uint)", 1) == f"0x2fbebd38{1:0>64x}"


def test_int_type_alias():
    assert encode_with_signature("foo(int)", 1) == encode_with_signature(
        "foo(int256)", 1
    )
    assert encode_with_signature("foo(int)", 1) == f"0x4c970b2f{1:0>64x}"


def test_uint_dynamic_array():
    assert (
        encode_with_signature("foo(uint256[])", [23, 32])
        == f"0x8b44cef1{0x20:0>64x}{2:0>64}{23:0>64x}{32:0>64x}"
    )


def test_uint_static_array():
    assert (
        encode_with_signature("foo(uint[2])", [23, 32])
        == f"0x4f5d13ef{23:0>64x}{32:0>64x}"
    )


def test_simple_struct():
    assert (
        encode_with_signature("foo((uint,bytes32))", [233, b"\x33".rjust(32, b"\x00")])
        == f"0x9d8a8ba8{233:0>64x}{0x33:0>64x}"
    )


def test_simple_struct_in_multiple_args():
    assert (
        encode_with_signature(
            "foo(uint256,uint[],(uint,bytes32))",
            1337,
            [23, 32],
            [233, b"\x33".rjust(32, b"\x00")],
        )
        == f"0xf24fcaec{1337:0>64x}{0x80:0>64x}{233:0>64x}{0x33:0>64x}{2:0>64x}{23:0>64x}{32:0>64x}"
    )


def test_nested_struct():
    assert (
        encode_with_signature(
            "foo((uint256,(uint,bytes32)))",
            [233, [332, b"\x33".rjust(32, b"\x00")]],
        )
        == f"0xa49b1396{233:0>64x}{332:0>64x}{0x33:0>64x}"
    )


def test_struct_with_dynamic_types():
    assert (
        encode_with_signature(
            "foo((uint256,bytes))",
            [233, b"hello"],
        )
        == f"0x73be91a3{0x20:0>64x}{233:0>64x}{0x40:0>64x}{5:0>64x}{b'hello'.hex():0<64}"
    )


def test_struct_array():
    address = 0x617F2E2FD72FD9D5503197092AC168C91465E7F2
    assert (
        encode_with_signature(
            "foo((uint256,address)[])",
            [[233, hex(address)], [332, hex(address)]],
        )
        == f"0xbff1570d{0x20:0>64x}{2:0>64x}{233:0>64x}{address:0>64x}{332:0>64x}{address:0>64x}"
    )
