import time
from datetime import date
from utils.logger import get_logger
from utils.date_helpers import parse_wc_datetime, hours_since_order, get_reminder_stage
from services.email_service import send_email
from services.sheets_service import (
    get_all_tracked_orders, add_order_to_sheet,
    update_reminder_info, update_order_status
)
from templates.email_templates import get_email_content
from config import COL_ORDER_ID, COL_STAGE, COL_STATUS, COL_INVOICE_SENT, EXCLUDED_EMAILS

logger = get_logger(__name__)


def process_orders(worksheet, orders: list[dict], dry_run: bool = False):
    """
    Processes all pending WooCommerce orders:
    - Sends invoice immediately for new orders
    - Sends reminders at 24h, 48h, 72h
    - Marks as abandoned after final reminder
    """

    if dry_run:
        logger.info("=== DRY RUN MODE — no emails sent, sheet not updated ===")

    # Load all orders already tracked in the sheet
    tracked     = get_all_tracked_orders(worksheet)
    tracked_ids = {str(row[COL_ORDER_ID]): row for row in tracked if row.get(COL_ORDER_ID)}

    total = len(orders)
    sent = skipped = errors = 0

    for order in orders:
        order_id       = order["order_id"]
        email          = order["email"]
        name           = order["name"]
        amount         = order["amount"]
        plan           = order["plan"]
        country        = order["country"]
        order_date_str = order["order_date"]

        logger.debug(f"Order {order_id} | {name or 'No name'} | {email}")

        if not email:
            logger.warning(f"Order {order_id} | Skipping — no email")
            skipped += 1
            continue

        if email.lower() in EXCLUDED_EMAILS:
            logger.info(f"Order {order_id} | Skipping — {email} is excluded")
            skipped += 1
            continue

        order_date = parse_wc_datetime(order_date_str)
        if not order_date:
            logger.warning(f"Order {order_id} | Skipping — could not parse date")
            skipped += 1
            continue

        hours_elapsed = hours_since_order(order_date)
        stage         = get_reminder_stage(hours_elapsed)
        today_str     = date.today().strftime("%Y-%m-%d")

        # --- New order — not yet in sheet ---
        if order_id not in tracked_ids:
            logger.info(f"Order {order_id} | New order — sending invoice ({hours_elapsed:.0f}h old)")
            content = get_email_content(stage=0, name=name, amount=amount,
                                        plan=plan, order_id=order_id, country=country)
            if dry_run:
                logger.info(f"[DRY RUN] Would send invoice → {email}")
                sent += 1
            else:
                success = send_email(email, content["subject"], content["body"])
                if success:
                    add_order_to_sheet(worksheet, order, invoice_sent=today_str, stage=0)
                    sent += 1
                    time.sleep(1)
                else:
                    errors += 1
            continue

        # --- Existing order — check reminder stage ---
        tracked_row   = tracked_ids[order_id]
        current_stage = int(tracked_row.get(COL_STAGE) or 0)
        status        = str(tracked_row.get(COL_STATUS, "")).lower()

        # Skip if already abandoned
        if status == "abandoned":
            logger.info(f"Order {order_id} | Already abandoned — skipping")
            skipped += 1
            continue

        # Use invoice_sent date for reminder timing, not order creation date.
        # This ensures the customer gets the full 24/48/72h window from when
        # they received the invoice, even if the invoice was sent late.
        invoice_sent_str = tracked_row.get(COL_INVOICE_SENT, "")
        if invoice_sent_str:
            try:
                invoice_date = date.fromisoformat(invoice_sent_str)
                days_since_invoice = (date.today() - invoice_date).days
                hours_since_invoice = days_since_invoice * 24
                stage = get_reminder_stage(hours_since_invoice)
            except ValueError:
                pass  # fall back to order-date-based stage already calculated

        # Mark as abandoned if past 72h since invoice and final reminder already sent
        if hours_elapsed > 72 and current_stage >= 3:
            logger.info(f"Order {order_id} | No payment after 72h — marking abandoned")
            if not dry_run:
                update_order_status(worksheet, order_id, "abandoned")
                time.sleep(1)
            skipped += 1
            continue

        # Skip if this stage was already sent
        if current_stage >= stage:
            logger.info(f"Order {order_id} | Stage {stage} already sent — skipping")
            skipped += 1
            continue

        # Send reminder
        logger.info(f"Order {order_id} | Sending stage {stage} reminder ({hours_elapsed:.0f}h elapsed)")
        content = get_email_content(stage=stage, name=name, amount=amount,
                                    plan=plan, order_id=order_id, country=country)
        if dry_run:
            logger.info(f"[DRY RUN] Would send stage {stage} reminder → {email}")
            sent += 1
        else:
            success = send_email(email, content["subject"], content["body"])
            if success:
                update_reminder_info(worksheet, order_id, stage, today_str)
                sent += 1
                time.sleep(1)
            else:
                errors += 1

    logger.info(f"=== Run complete | Total: {total} | Sent: {sent} | Skipped: {skipped} | Errors: {errors} ===")
