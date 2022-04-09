import json
import logging
import re
import shutil
from typing import Union

from src.core import Downloader, Utility
from src.imap_wrapper import GmailImapWrapper

FORMAT = "%(asctime)s :: %(levelname)s :: [%(module)s.%(funcName)s.%(lineno)d] :: %(message)s"


def get_logger(verbose: bool = False, log_format: str = FORMAT):
    formatter = logging.Formatter(log_format)

    stream_level = logging.DEBUG if verbose else logging.INFO
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(stream_level)

    # file_handler = logging.FileHandler("main.log")
    # file_handler.setLevel(logging.INFO)

    # file_debug_handler = logging.FileHandler("main.debug.log")
    # file_debug_handler.setLevel(logging.DEBUG)

    # set formatters and add handlers to main logger
    logger = logging.getLogger("src")
    logger.setLevel(logging.DEBUG)

    handlers = (stream_handler,)

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def main(
    username: str,
    password: str,
    file_pattern: Union[None, str, re.Pattern] = None,
    subject_pattern: Union[None, str, re.Pattern] = None,
    *,
    logging_verbose: bool = False,
):
    logger = get_logger(verbose=logging_verbose)
    logger.info("Execution started")

    imap = GmailImapWrapper(username=username, password=password)
    downloader = Downloader(
        imap_wrapper=imap, file_pattern=file_pattern, subject_pattern=subject_pattern
    )
    count, bytes_count = downloader.download_attachments()
    bytes_human = Utility.bytes_to_human(bytes_count)
    logger.info("Execution finished")
    logger.info(f"{count} attachments downloaded [{bytes_human} downloaded]")


if __name__ == "__main__":
    # DEBUG, rimuovere quando in prod
    shutil.rmtree("output", ignore_errors=True)

    creds = json.load(open("credentials.json"))

    my_subject_pattern = Downloader.get_pattern(".*seconda.*")
    my_file_pattern = Downloader.get_pattern(".*MODELLO7.*")

    main(
        username=creds["email"],
        password=creds["password"],
        file_pattern=my_file_pattern,
        subject_pattern=my_subject_pattern,
    )
