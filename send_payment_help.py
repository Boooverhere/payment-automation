"""
One-off personal email to customers whose first order got stuck at payment
--------------------------------------------------------------------------
Offers the payment options that now work for their country:
    US      → their order's payment page (Venmo / Cash App) + PayPal Friends and Family
    EU/EEA  → their order's payment page (Revolut) + personal Revolut link + PayPal
    other   → personal Revolut link + PayPal

Orders that were paid or cancelled in the meantime are skipped, and every
sent order is logged so nobody gets it twice.

Usage:
    python3 send_payment_help.py --dry-run
    python3 send_payment_help.py --test-email you@example.com
    python3 send_payment_help.py
"""

import argparse
import time
from datetime import datetime
from pathlib import Path

import requests

from config import (
    WC_STORE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET,
    PAYPAL_USERNAME, REVOLUT_LINK, EUROPEAN_COUNTRIES,
)
from services.email_service import send_email
from utils.logger import get_logger

logger = get_logger(__name__)

ORDER_IDS = [5302, 5240, 5213, 5207, 5190, 5181, 5158, 5157, 5150, 5154]
SENT_LOG  = Path(__file__).resolve().parent / "payment_help_sent.log"


def get_order(order_id: int) -> dict:
    response = requests.get(
        f"{WC_STORE_URL}/wp-json/wc/v3/orders/{order_id}",
        params={"consumer_key": WC_CONSUMER_KEY, "consumer_secret": WC_CONSUMER_SECRET},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def _link(url: str, label: str) -> str:
    return f'<a href="{url}" style="color:#FF6B35; font-weight:bold;">{label}</a>'


def build_email(order: dict) -> dict:
    billing  = order["billing"]
    name     = (billing.get("first_name") or "").strip().split(" ")[0].title() or "there"
    country  = (billing.get("country") or "").upper()
    plan     = order["line_items"][0]["name"] if order["line_items"] else "your subscription"
    ordered  = datetime.fromisoformat(order["date_created"]).strftime("%B %-d")
    amount   = f"${order['total']}"
    pay_page = order.get("payment_url", "")

    if country == "US":
        options = (f"<p>We've made it much easier now. You can pay in about a minute with Venmo or Cash App here:<br>"
                   f"{_link(pay_page, 'Pay for order #' + str(order['id']))}</p>")
    elif country in EUROPEAN_COUNTRIES:
        options = (f"<p>We've made it much easier now. You can pay in about a minute with Revolut here:<br>"
                   f"{_link(pay_page, 'Pay for order #' + str(order['id']))}</p>"
                   f"<p>Or pay {amount} by card through our Revolut link: {_link(REVOLUT_LINK, REVOLUT_LINK.replace('https://', ''))}</p>")
    else:
        options = (f"<p>We've made it much easier now. You can pay {amount} by card through our Revolut link:<br>"
                   f"{_link(REVOLUT_LINK, REVOLUT_LINK.replace('https://', ''))}</p>")

    body = f"""
    <div style="font-family:Arial, Helvetica, sans-serif; font-size:15px; line-height:1.6; color:#222; max-width:560px;">
        <p>Hi {name},</p>
        <p>You ordered the {plan} with us on {ordered}, but it looks like the payment never went through.
           That's on us. Our old payment options didn't work well for a lot of customers.</p>
        {options}
        <p>Or send {amount} by PayPal to <strong>{PAYPAL_USERNAME}</strong> (please choose <strong>Friends and Family</strong>)
           and reply to this email with your order number.</p>
        <p>As soon as it's paid, your login details arrive by email and WhatsApp. If anything is unclear,
           just reply to this email and we'll get you set up.</p>
        <p>IPTVSup Team</p>
    </div>
    """
    return {"subject": f"Your IPTVSup order #{order['id']}", "body": body}


def load_sent() -> set:
    return set(SENT_LOG.read_text().split()) if SENT_LOG.exists() else set()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-email", help="send the first eligible email to this address instead")
    args = parser.parse_args()

    sent = load_sent()
    total = done = skipped = errors = 0
    for order_id in ORDER_IDS:
        total += 1
        order = get_order(order_id)
        if order.get("date_paid") or order["status"] in ("completed", "cancelled", "refunded", "failed"):
            logger.info(f"Order {order_id} | {order['status']} / paid — skipping")
            skipped += 1
            continue
        if str(order_id) in sent and not args.test_email:
            logger.info(f"Order {order_id} | already sent — skipping")
            skipped += 1
            continue

        content = build_email(order)
        to_email = args.test_email or order["billing"]["email"]
        country = order["billing"].get("country", "")
        if args.dry_run:
            logger.info(f"[DRY RUN] Order {order_id} | {country} | → {to_email} | {content['subject']}")
            done += 1
            continue

        subject = f"[TEST] {content['subject']}" if args.test_email else content["subject"]
        if send_email(to_email, subject, content["body"]):
            done += 1
            if args.test_email:
                break
            with SENT_LOG.open("a") as f:
                f.write(f"{order_id}\n")
            time.sleep(1)
        else:
            errors += 1

    logger.info(f"=== Payment help | Total: {total} | Sent: {done} | Skipped: {skipped} | Errors: {errors} ===")


if __name__ == "__main__":
    main()
