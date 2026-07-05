"""
SMTP-based email sender for the flight-tracker email service.

Uses aiosmtplib for async SMTP delivery. All credentials are loaded
from environment variables with safe placeholders.
"""

import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Sequence

import aiosmtplib
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── SMTP Configuration (placeholder credentials) ───────────────────────────

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.example.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "your-email@example.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "your-app-password")
SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "Flight Tracker")
SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", SMTP_USERNAME)
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"


async def send_email(
    to_addresses: str | Sequence[str],
    subject: str,
    html_body: str,
) -> bool:
    """
    Send an HTML email to one or more recipients via SMTP.

    Args:
        to_addresses: A single email string, or a comma-separated string,
                      or a list of email addresses.
        subject:      Email subject line.
        html_body:    Full HTML body content.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    # Normalise recipients to a list
    if isinstance(to_addresses, str):
        recipients = [addr.strip() for addr in to_addresses.split(",") if addr.strip()]
    else:
        recipients = list(to_addresses)

    if not recipients:
        logger.warning("send_email called with no recipients — skipping")
        return False

    # Build the MIME message
    message = MIMEMultipart("alternative")
    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    # Attach HTML part
    message.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=SMTP_USE_TLS,
        )
        logger.info(f"Email sent to {recipients} — subject: {subject!r}")
        return True

    except aiosmtplib.SMTPAuthenticationError:
        logger.error(
            "SMTP authentication failed. Check SMTP_USERNAME / SMTP_PASSWORD "
            "in your .env file."
        )
        return False

    except aiosmtplib.SMTPConnectError:
        logger.error(
            f"Cannot connect to SMTP server at {SMTP_HOST}:{SMTP_PORT}. "
            "Check SMTP_HOST / SMTP_PORT in your .env file."
        )
        return False

    except aiosmtplib.SMTPException as e:
        logger.error(f"SMTP error while sending email: {e}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False
