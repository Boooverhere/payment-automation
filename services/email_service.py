import requests
from utils.logger import get_logger
from config import SENDER_EMAIL, SENDER_NAME, BREVO_API_KEY

logger = get_logger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, subject: str, body_html: str) -> bool:
    """
    Sends an HTML email via Brevo Transactional API.
    Gives full open/click/delivery tracking in the Brevo dashboard.
    Returns True if sent successfully, False if it failed.
    """
    payload = {
        "sender":      {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to":          [{"email": to_email}],
        "subject":     subject,
        "htmlContent": body_html,
    }

    try:
        response = requests.post(
            BREVO_API_URL,
            json=payload,
            headers={
                "api-key":      BREVO_API_KEY,
                "Content-Type": "application/json",
            },
            timeout=15,
        )

        if response.status_code in (200, 201):
            logger.info(f"Email sent → {to_email} | Subject: {subject}")
            return True

        logger.error(
            f"Brevo API error → {to_email} | "
            f"Status: {response.status_code} | {response.text}"
        )
        return False

    except requests.RequestException as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
