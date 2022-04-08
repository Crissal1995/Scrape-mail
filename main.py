import imaplib
import json
import email
import os
import shutil
from typing import Sequence, Union


def is_ok_response(response: str) -> bool:
    return response == "OK"


def assert_response(response: str):
    if not is_ok_response(response):
        raise RuntimeError("Response is not ok!")


def remove_chars(string: str, chars: Union[str, Sequence[str]]) -> str:
    banned_chars = chars
    if isinstance(chars, (list, tuple)):
        banned_chars = "".join(chars)

    cleaned_string = string
    for banned_char in banned_chars:
        cleaned_string = cleaned_string.replace(banned_char, "")

    return cleaned_string


OUTPUT_DIR = "output"

# DEBUG ONLY
shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

imap_host = "imap.gmail.com"
creds = json.load(open("credentials.json"))

# create imap connection to mail server
imap = imaplib.IMAP4_SSL(host=imap_host)
imap.login(user=creds["email"], password=creds["password"])

# the inbox to use
INBOX_TO_SELECT = "INBOX"

# select inbox
response, count_messages_binary = imap.select(mailbox=INBOX_TO_SELECT, readonly=True)

# check if exists
assert_response(response)

# get count of emails in selected inbox
count_messages = int(count_messages_binary[0].decode("utf-8"))

response, email_ids_binary = imap.search(None, "ALL")
assert_response(response)

email_ids = str(email_ids_binary[0]).strip("b'").strip("'").split()

for email_id in email_ids:
    response, data = imap.fetch(email_id, '(RFC822)')
    assert_response(response)
    raw_message = data[0][1].decode("utf-8")
    email_message = email.message_from_string(raw_message)

    for part in email_message.walk():
        filename = part.get_filename()
        if filename:
            subject: str = email_message["Subject"]
            os_subject = remove_chars(subject, "\"\\/:*?|<>")
            path = f"{OUTPUT_DIR}/{os_subject}"
            os.makedirs(path, exist_ok=True)

            os_filename = remove_chars(filename, "\"\\/:*?|<>")
            full_path = f"{path}/{os_filename}"

            with open(full_path, "bw") as f:
                f.write(part.get_payload(decode=True))
            print(f"Downloaded {os_subject}/{os_filename}")
