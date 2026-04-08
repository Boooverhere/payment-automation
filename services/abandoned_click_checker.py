"""
Abandoned Checkout Checker
---------------------------
Runs every hour via cron.
For every win-back click stored in click_pending.json that is older than 2 hours,
checks if the customer placed an order. If not → sends a follow-up email.
"""

import json
import time
from pathlib import Path

from urllib.parse import urlparse, parse_qs

from utils.logger import get_logger
from services.sheets_service import get_sheet, get_all_tracked_orders
from services.email_service import send_email
from services.woocommerce_service import get_product
from templates.abandoned_email import get_abandoned_email
from config import COL_EMAIL, COL_ORDER_DATE

# Hardcoded product map — avoids WooCommerce API dependency
# Keyed by the add-to-cart product ID as a string
PRODUCT_MAP = {
    # Standard plans
    "2708": {
        "name":  "1 Month Subscription",
        "price": "14.99",
        "image": "https://iptvsup.com/wp-content/uploads/2023/05/4425137731.png",
    },
    "2709": {
        "name":  "3 Months Subscription",
        "price": "29.99",
        "image": "https://iptvsup.com/wp-content/uploads/2023/05/4489509824.png",
    },
    "2710": {
        "name":  "6 Months Subscription",
        "price": "39.99",
        "image": "https://iptvsup.com/wp-content/uploads/2023/05/4489509831.png",
    },
    "2711": {
        "name":  "12 Months Subscription",
        "price": "55.99",
        "image": "https://iptvsup.com/wp-content/uploads/2023/05/4489506467.png",
    },
    # Premium plans
    "714": {
        "name":  "1 Month Premium Subscription",
        "price": "17.99",
        "image": "https://iptvsup.com/wp-content/uploads/2022/10/1-Month.webp",
    },
    "719": {
        "name":  "3 Months Premium Subscription",
        "price": "34.99",
        "image": "https://iptvsup.com/wp-content/uploads/2022/10/3-months.webp",
    },
    "723": {
        "name":  "6 Months Premium Subscription",
        "price": "49.99",
        "image": "https://iptvsup.com/wp-content/uploads/2022/10/6-months.webp",
    },
    "728": {
        "name":  "12 Months Premium Subscription",
        "price": "79.99",
        "image": "https://iptvsup.com/wp-content/uploads/2022/10/1-year.webp",
    },
}

logger = get_logger(__name__)

PENDING_FILE   = Path("/app/click_pending.json")
FOLLOW_UP_WAIT = 2 * 3600   # 2 hours in seconds
CLEANUP_AFTER  = 48 * 3600  # remove entries older than 48h


def load_pending() -> list[dict]:
    if not PENDING_FILE.exists():
        return []
    with open(PENDING_FILE) as f:
        return json.load(f)


def save_pending(entries: list[dict]):
    with open(PENDING_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def email_ordered_after(email: str, clicked_at: float, orders: list[dict]) -> bool:
    """Returns True if this email placed an order after the click timestamp."""
    for order in orders:
        if order.get(COL_EMAIL, "").strip().lower() != email.lower():
            continue
        # order_date is stored as YYYY-MM-DD — treat any order today as recent enough
        order_ts = order.get("invoice_sent", "") or order.get(COL_ORDER_DATE, "")
        if order_ts:
            try:
                import datetime
                order_dt = datetime.datetime.strptime(str(order_ts)[:10], "%Y-%m-%d")
                click_dt = datetime.datetime.fromtimestamp(clicked_at)
                if order_dt.date() >= click_dt.date():
                    return True
            except ValueError:
                continue
    return False


def run():
    pending = load_pending()
    if not pending:
        logger.info("Abandoned checker | No pending clicks")
        return

    now = time.time()

    # Load Payment Tracker once
    try:
        worksheet = get_sheet()
        orders    = get_all_tracked_orders(worksheet)
    except Exception as e:
        logger.error(f"Abandoned checker | Could not load sheet: {e}")
        return

    updated = []
    for entry in pending:
        email      = entry["email"]
        clicked_at = entry["clicked_at"]
        sent       = entry.get("follow_up_sent", False)
        age        = now - clicked_at

        # Clean up very old entries
        if age > CLEANUP_AFTER:
            logger.info(f"Abandoned checker | {email} | Removing old entry")
            continue

        # Not yet old enough — keep, check later
        if age < FOLLOW_UP_WAIT:
            updated.append(entry)
            continue

        # Already sent follow-up — keep for cleanup window
        if sent:
            updated.append(entry)
            continue

        # Check if they ordered
        if email_ordered_after(email, clicked_at, orders):
            logger.info(f"Abandoned checker | {email} | Order found — no follow-up needed")
            entry["follow_up_sent"] = True
            updated.append(entry)
            continue

        # No order → send follow-up
        checkout_url = entry.get("checkout_url", "")
        product = {}
        if checkout_url:
            qs = parse_qs(urlparse(checkout_url).query)
            product_ids = qs.get("add-to-cart", [])
            if product_ids:
                pid = product_ids[0]
                product = PRODUCT_MAP.get(pid) or get_product(pid)

        content = get_abandoned_email(
            checkout_url=checkout_url,
            product_name=product.get("name", ""),
            product_price=product.get("price", ""),
            product_image=product.get("image", ""),
        )
        success = send_email(
            to_email=email,
            subject=content["subject"],
            body_html=content["body"],
        )

        if success:
            logger.info(f"Abandoned checker | {email} | Follow-up sent")
            entry["follow_up_sent"] = True
        else:
            logger.error(f"Abandoned checker | {email} | Failed to send follow-up")

        updated.append(entry)

    save_pending(updated)
    logger.info(f"Abandoned checker | Done | {len(updated)} entries remaining")
