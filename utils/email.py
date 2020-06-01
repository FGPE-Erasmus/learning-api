import smtplib

from flask_mail import Message
from settings import MAIL


class Mail:
    def __init__(self):
        self.server = smtplib.SMTP(MAIL['MAIL_SERVER'], MAIL['MAIL_PORT'])
        self.server.connect(MAIL['MAIL_SERVER'], MAIL['MAIL_PORT'])
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(MAIL['MAIL_USERNAME'], MAIL['MAIL_PASSWORD'])

    def send_email(self, mail_to, subject, template):
        mail_from = MAIL['MAIL_USERNAME']

        msg = Message(
            subject,
            recipients=[mail_to],
            html=template,
            sender=MAIL['MAIL_USERNAME']
        )
        text = msg.as_string()

        self.server.sendmail(mail_from, mail_to, text)

        return True
