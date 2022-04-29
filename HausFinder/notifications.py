import logging
from typing import List
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailHandler:
    def __init__(self, sender_email: str, receiver_emails: List[str]) -> None:
        self.sender = sender_email
        self.receivers = receiver_emails
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.email = None

    def build_email(self, subject: str, text: str) -> None:
        email = MIMEMultipart("alternative")
        email["Subject"] = subject
        email["From"] = self.sender
        email["To"] = ", ".join(self.receivers)
        email.attach(MIMEText(text, "html"))
        self.email = email

    def add_attachment(self):
        pass

    def send_email(
        self,
        username: str,
        password: str,
    ) -> None:
        self._auth_with_server(username, password)
        logging.info(f"Sending emails to: {self.receivers}")
        self.server.sendmail(self.sender, self.receivers, self.email.as_string())

    def server_quit(self) -> None:
        self.server.quit()

    def _auth_with_server(self, username: str, password: str) -> None:
        self.server.ehlo()
        self.server.starttls()
        self.server.login(username, password)
