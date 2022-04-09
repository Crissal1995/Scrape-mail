import email
import logging
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path
from string import ascii_lowercase
from typing import Optional, Sequence, Union

from src.imap_wrapper import ImapWrapper

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = "output"


class Utility:
    @classmethod
    def bytes_to_human(cls, bytes_count: int) -> str:
        suffix_index = -1
        suffices = "KMGTP"
        while bytes_count >= 1024:
            bytes_count //= 1024
            suffix_index += 1
        if suffix_index == -1:
            suffix = "B"
        else:
            suffix = suffices[suffix_index] + "B"
        return f"{bytes_count}{suffix}"


class Cleaner:
    @classmethod
    def remove_chars(cls, string: str, chars: Union[str, Sequence[str]]) -> str:
        banned_chars = chars
        if isinstance(chars, (list, tuple)):
            banned_chars = "".join(chars)

        cleaned_string = string
        for banned_char in banned_chars:
            cleaned_string = cleaned_string.replace(banned_char, "")

        return cleaned_string

    @classmethod
    def is_reserved_name(cls, string: str) -> bool:
        """Check if the stem of the string is a reserved Windows name"""
        return Path(string).stem.upper() in (
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        )

    @classmethod
    def win_compatible_string(cls, string: str) -> str:
        """Get a Windows compatible path-string"""
        # https://stackoverflow.com/questions/1976007

        # remove forbidden chars in name
        s = cls.remove_chars(string, '"\\/:*?|<>')
        # remove spaces and dots from left and right margins
        s = s.strip(" .")
        # add some gibberish if the name is reserved
        if cls.is_reserved_name(s):
            s = "".join(random.choices(ascii_lowercase, k=5)) + "_" + s

        return s


@dataclass
class Attachment:
    """An abstraction for the attachment of a Message
    Filename it's the name of the attachment,
    Payload its content
    Message is optional and it's the original message sent to server"""

    filename: str
    payload: bytes
    message: Optional[email.message.Message] = None

    def __post_init__(self):
        """After created an object, we want it's filename to be windows-compliant"""
        self.filename = Cleaner.win_compatible_string(self.filename)

    @property
    def subject(self):
        """Returns the subject of the email message"""
        return self.message["Subject"]

    def download(
        self, path: Union[str, os.PathLike, None] = None, create_dirs: bool = True
    ):
        if path is None:
            path = Path(f"{DEFAULT_OUTPUT_DIR}/{self.subject}")

        if isinstance(path, str):
            path = Path(path)

        parts = [Cleaner.win_compatible_string(part) for part in path.parts]
        clean_path = Path("/".join(parts))

        # suppose the path provided it's always a directory
        clean_path /= self.filename

        if create_dirs:
            os.makedirs(clean_path.parent, exist_ok=True)

        with open(clean_path, "wb") as f:
            f.write(self.payload)


class Downloader:
    """The interface for the attachments downloader

    - imap_wrapper is the ImapWrapper object obtained, used to retrieve emails

    - file_pattern and subject_pattern are two patterns that can be provided
      as None, string, or re.Pattern; they are utilised to match only a subset of
      messages (filtering for filename and subject respectively);
      if they are None, to match everything the wildcard '.*' will be used"""

    def __init__(
        self,
        imap_wrapper: ImapWrapper,
        file_pattern: Union[None, str, re.Pattern] = None,
        subject_pattern: Union[None, str, re.Pattern] = None,
        output_dir: Union[str, os.PathLike] = DEFAULT_OUTPUT_DIR,
    ):
        self.file_pattern = self.get_pattern(file_pattern)
        self.subject_pattern = self.get_pattern(subject_pattern)
        self.imap_wrapper = imap_wrapper
        self.output_dir = Path(output_dir)

    @staticmethod
    def get_pattern(
        pattern: Union[None, str, re.Pattern], ignore_case: bool = False
    ) -> re.Pattern:
        flag = re.I if ignore_case else 0
        if pattern is None:
            return re.compile(r".*", flag)
        elif isinstance(pattern, str):
            return re.compile(rf"{pattern}", flag)
        else:
            return pattern

    def change_inbox(self, inbox: str):
        self.imap_wrapper.change_inbox(inbox)

    def get_attachments_from_message(
        self, message: email.message.Message
    ) -> Sequence[Attachment]:
        attachments = []

        for i, email_part in enumerate(message.walk()):
            filename = email_part.get_filename()

            if not filename or not self.file_pattern.match(filename):
                continue

            payload = email_part.get_payload(decode=True)
            attachments.append(Attachment(filename, payload, message))

        return attachments

    def get_attachments(self) -> Sequence[Attachment]:
        attachments = []

        for email_message in self.imap_wrapper.email_messages_gen():
            subject = email_message["Subject"]
            if not self.subject_pattern.match(subject):
                continue
            attachments += self.get_attachments_from_message(email_message)

        return attachments

    def download_attachments(self) -> (int, int):
        """Retrieve messages and store them as they go
        For performance and memory reasons, this is done like get_attachments,
        so using the ImapWrapper generator, storing messages to filesystem but not in memory"""
        count = 0
        bytes_count = 0

        for email_message in self.imap_wrapper.email_messages_gen():
            subject = email_message["Subject"]
            if not self.subject_pattern.match(subject):
                continue
            attachments = self.get_attachments_from_message(email_message)

            for attachment in attachments:
                attachment.download(path=self.output_dir / subject)
                count += 1
                bytes_count += len(attachment.payload)

        return count, bytes_count
