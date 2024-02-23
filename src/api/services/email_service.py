import logging
import smtplib
import ssl
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from settings import email


logger = logging.getLogger("email")


@dataclass
class Message:
    subject: str
    body: str
    receiver: str


def send_email(message: Message) -> dict[str, tuple[int, str]]:
    msg = MIMEMultipart()
    msg["From"] = email.EMAIL_FROM
    msg["To"] = message.receiver
    msg["Subject"] = message.subject
    msg.attach(MIMEText(message.body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(email.EMAIL_SERVER, email.EMAIL_PORT, context=context) as smtp:
        smtp.login(email.EMAIL_USERNAME, email.EMAIL_PASSWORD)
        result = smtp.sendmail(email.EMAIL_FROM, message.receiver, msg.as_string())
    return result


def send_confirmation_code_to_user(email: str, code: str | int) -> bool:
    html = """
    <p>Ваш код подтверждения: <b>{code}</b></p> 
    """
    try:
        logger.info(f"Sending code confirmation to user={email}")
        message = Message(
            subject="Код подтверждения",
            receiver=email,
            body=html.format(code=code),
        )
        send_email(message)
        return True
    except Exception as e:
        logger.error(f"Error sending email to user={email}: {e}")
        return False
