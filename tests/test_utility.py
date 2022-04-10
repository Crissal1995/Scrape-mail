from functools import partial

from scrapemail.utility import bytes_to_human

b2h_decimal = partial(bytes_to_human, unit="decimal")
b2h_binary = partial(bytes_to_human, unit="binary")


def test_b2h_decimal():
    base = 1000
    assert b2h_decimal(base - 1) == "999 B"
    assert b2h_decimal(base) == "1.0 KB"
    assert b2h_decimal(base + 1) == "1.001 KB"
    assert b2h_decimal(base**2) == "1.0 MB"
    assert b2h_decimal(base**2, integer=True) == "1 MB"


def test_b2h_binary():
    base = 1024
    assert b2h_binary(base - 1) == "1023 B"
    assert b2h_binary(base) == "1.0 KiB"
    assert b2h_binary(base + 1) == "1.001 KiB"
    assert b2h_binary(base * 2) == "2.0 KiB"
    assert b2h_binary(base**4) == "1.0 TiB"
    assert b2h_binary(base**4, integer=True) == "1 TiB"
