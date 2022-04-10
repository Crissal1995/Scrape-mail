import getpass
import json
import os
import typing


def bytes_to_human(
    bytes_count: int, unit: str = "decimal", integer: bool = False
) -> str:
    """Convert an integer (amount of bytes) to its corresponding
    human-readable value.

    It's possible to select the desired unit:
     - decimal: base 10 (10^3 B = 1000 B = 1 KB)
     - binary: base 2 (2^10 B = 1024 B = 1 KiB)"""
    valid_units = ("decimal", "binary")
    unit = unit.lower()
    if unit not in valid_units:
        errmsg = (
            f"Invalid selected unit! Valid are {valid_units}, but {unit} was provided"
        )
        raise ValueError(errmsg)
    if unit == "decimal":
        base = 1000
    else:  # unit == "binary"
        base = 1024

    suffix_index = -1
    suffices = "KMGTPEZY"
    while bytes_count >= base:
        bytes_count /= base
        suffix_index += 1

    suffix = ""
    if suffix_index >= 0:
        suffix = suffices[suffix_index]
        if unit == "binary":
            suffix += "i"
    suffix += "B"

    if integer:
        bytes_count = int(bytes_count)
    return f"{round(bytes_count, 3)} {suffix}"


def get_credentials_from_file(filepath: typing.Union[str, os.PathLike]) -> (str, str):
    """Retrieve username and password for the IMAP server
    using a json object with the schema:

    {
       "username"/"user"/"email": value,

       "password"/"pass": value
    }
    """
    with open(filepath) as f:
        obj: dict = json.load(f)

    username = obj.get("username") or obj.get("user") or obj.get("email")
    password = obj.get("password") or obj.get("pass")
    if not any((username, password)):
        raise ValueError("Missing username and/or password from JSON object")

    return username, password


def get_credentials_from_username(username: str) -> (str, str):
    """Retrieve username and password for the IMAP server
    using the getpass module to securely type in the password,
    then returns the tuple (username, password)"""
    password = getpass.getpass()
    return username, password


def get_credentials() -> (str, str):
    """Retrieve username and password for the IMAP server
    using input and getpass for both username and password"""
    username = input("Username: ")
    return get_credentials_from_username(username)
