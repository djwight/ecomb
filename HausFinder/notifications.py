import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd


class EmailHandler:
    def __init__(self, sender_email: str, receiver_email: str) -> None:
        self.sender = sender_email
        self.receiver = receiver_email
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.email = None

    def build_email(self, subject: str, text: str) -> None:
        email = MIMEMultipart("alternative")
        email["Subject"] = subject
        email["From"] = self.sender
        email["To"] = self.receiver
        email.attach(MIMEText(text, "html"))
        self.email = email

    def add_attachment(self, attachment: pd.DataFrame):
        pass

    def send_email(
        self,
        username: str,
        password: str,
    ) -> None:
        self._auth_with_server(username, password)
        self.server.sendmail(self.sender, self.receiver, self.email.as_string())

    def _auth_with_server(self, username: str, password: str) -> None:
        self.server.ehlo()
        self.server.starttls()
        self.server.login(username, password)
