import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.logger import get_logger
from config import SENDER_EMAIL, SENDER_NAME, SMTP_LOGIN, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT

logger = get_logger(__name__)


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an HTML email via SMTP.
    Returns True if sent successfully, False if it failed.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"]      = to_email

    msg.attach(MIMEText(body_html, "html"))

    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_LOGIN, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(SMTP_LOGIN, SMTP_PASSWORD)
                server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        logger.info(f"Email sent → {to_email} | Subject: {subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. Check SENDER_EMAIL and SMTP_PASSWORD in .env")
        return False

    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
