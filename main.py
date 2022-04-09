import json
import re
import shutil
from typing import Union

from src.core import Downloader
from src.imap_wrapper import GmailImapWrapper


def main(
    username: str,
    password: str,
    file_pattern: Union[None, str, re.Pattern] = None,
    subject_pattern: Union[None, str, re.Pattern] = None,
):
    imap = GmailImapWrapper(username=username, password=password)
    downloader = Downloader(
        imap_wrapper=imap, file_pattern=file_pattern, subject_pattern=subject_pattern
    )
    downloader.download_attachments()


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
