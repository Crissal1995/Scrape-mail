import logging
import pathlib
import re
from typing import Optional, Union

from scrapemail import Downloader, utility
from scrapemail.imap_wrapper import ImapWrapperFactory

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
    logger = logging.getLogger("scrapemail")
    logger.setLevel(logging.DEBUG)

    handlers = (stream_handler,)

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def main(
    username: str,
    password: str,
    inbox: Optional[str] = None,
    file_pattern: Union[None, str, re.Pattern] = None,
    subject_pattern: Union[None, str, re.Pattern] = None,
    *,
    verbose: bool = False,
):
    logger = get_logger(verbose=verbose)
    logger.info(f"Execution started for username {username}")

    imap_wrapper = ImapWrapperFactory.get_wrapper(
        username=username, password=password, inbox_to_select=inbox
    )
    downloader = Downloader(
        imap_wrapper=imap_wrapper,
        file_pattern=file_pattern,
        subject_pattern=subject_pattern,
    )
    logger.info(f"Download path: {downloader.output_dir}")
    count, bytes_count = downloader.download_attachments()
    plural = "s" if count != 1 else ""
    bytes_human = utility.bytes_to_human(bytes_count)
    logger.info("Execution finished")
    logger.info(f"{count} attachment{plural} downloaded [{bytes_human} downloaded]")


if __name__ == "__main__":
    import argparse

    description = (
        "ScrapeMail is used to easily download all attachments "
        "from a mailbox via IMAP server, being able to specify individual "
        "filters for both the subject of the mail and the attachments themselves."
    )
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-i",
        "--inbox",
        help="Mail inbox to use; if not provided, the default one will be used",
    )
    default_credentials = "credentials.json"
    parser.add_argument(
        "-c",
        "--credentials",
        default=default_credentials,
        help=f"Credentials file to use, alternative to -u; defaults to {default_credentials}",
    )
    parser.add_argument(
        "-u",
        "--username",
        help="Username for the imap server, alternative to -c",
    )
    parser.add_argument(
        "-sp", "--subject-pattern", help="Regexp pattern for email subjects"
    )
    parser.add_argument(
        "-fp", "--file-pattern", help="Regexp pattern for attachment filenames"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase logging verbosity"
    )

    args = parser.parse_args()
    args_dict = vars(args)

    username = args_dict.get("username")
    uses_username = bool(username)

    credentials_path = pathlib.Path(args_dict["credentials"])
    uses_credentials = credentials_path.is_file()

    if uses_username:
        username, password = utility.get_credentials_from_username(username)
    elif uses_credentials:
        username, password = utility.get_credentials_from_file(credentials_path)
    else:
        username, password = utility.get_credentials()

    main(
        username=username,
        password=password,
        inbox=args_dict.get("inbox"),
        file_pattern=args_dict.get("file_pattern"),
        subject_pattern=args_dict.get("subject_pattern"),
        verbose=args_dict.get("verbose"),
    )
