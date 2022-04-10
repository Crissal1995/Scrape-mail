from scrapemail.core import Utility


def test_core_utility_decimal():
    base = 1000
    assert Utility.bytes_to_human(base - 1) == "999 B"
    assert Utility.bytes_to_human(base) == "1.0 KB"
    assert Utility.bytes_to_human(base + 1) == "1.001 KB"
    assert Utility.bytes_to_human(base ** 2) == "1.0 MB"
    assert Utility.bytes_to_human(base ** 2, integer=True) == "1 MB"


def test_core_utility_binary():
    base = 1024
    assert Utility.bytes_to_human(base - 1, unit="binary") == "1023 B"
    assert Utility.bytes_to_human(base, unit="binary") == "1.0 KiB"
    assert Utility.bytes_to_human(base + 1, unit="binary") == "1.001 KiB"
    assert Utility.bytes_to_human(base * 2, unit="binary") == "2.0 KiB"
    assert Utility.bytes_to_human(base ** 4, unit="binary") == "1.0 TiB"
    assert Utility.bytes_to_human(base ** 4, unit="binary", integer=True) == "1 TiB"
