import email
import imaplib
from email.message import Message
from typing import Generator, Optional


class ImapWrapper:
    IMAP4_PORT = 143
    IMAP4_SSL_PORT = 993

    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        *,
        ssl: bool = True,
        port: Optional[int] = None,
        inbox_to_select: Optional[str] = None,
    ):
        """Constructor for the ImapWrapper
        username, password and host are mandatory;
        port, ssl and inbox_to_select are optional.

        Default value for port is None, and the default IMAP port will be used
        based on the value of 'ssl'
        Default value for ssl is True
        Default value for inbox_to_select is None, so default inbox ('INBOX')
        will be selected"""
        if port is None:
            port = self.IMAP4_SSL_PORT if ssl else self.IMAP4_PORT

        if ssl:
            self.imap_conn = imaplib.IMAP4_SSL(host=host, port=port)  # noqa
        else:
            self.imap_conn = imaplib.IMAP4(host=host, port=port)  # noqa

        # will fail if wrong credentials
        self.imap_conn.login(user=username, password=password)

        # select an inbox to read in the __init__ process
        # will select the default mailbox if no one is specified by the user
        self.change_inbox(inbox_to_select)

    @staticmethod
    def assert_response(value: str, expected: str = "OK"):
        if value != expected:
            raise RuntimeError(f"Expected {expected}, got {value}!")

    def change_inbox(self, inbox: Optional[str] = None):
        """Change the current inbox to use to retrieve messages
        If inbox is None, default inbox ('INBOX') will be used"""
        inbox = inbox or "INBOX"
        response, count_messages_binary = self.imap_conn.select(
            mailbox=inbox, readonly=True
        )
        self.assert_response(response)

    def email_messages_gen(self) -> Generator[Message, None, None]:
        """Returns a generator of Email Messages from the selected inbox"""
        response, email_ids_binary = self.imap_conn.search(None, "ALL")
        self.assert_response(response)

        email_ids = str(email_ids_binary[0]).strip("b'").split()

        for email_id in email_ids:
            response, data = self.imap_conn.fetch(email_id, "(RFC822)")
            self.assert_response(response)

            raw_message = data[0][1].decode("utf-8")
            email_message = email.message_from_string(raw_message)
            yield email_message


class GmailImapWrapper(ImapWrapper):
    def __init__(
        self, username: str, password: str, *, inbox_to_select: Optional[str] = None
    ):
        super(GmailImapWrapper, self).__init__(
            username=username,
            password=password,
            host="imap.gmail.com",
            ssl=True,
            port=self.IMAP4_SSL_PORT,
            inbox_to_select=inbox_to_select,
        )
