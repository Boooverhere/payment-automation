"""
Payment Automation
-------------------
Fetches unpaid WooCommerce orders and sends invoice + reminder emails.

Usage:
    python3 app.py            # live run
    python3 app.py --dry-run  # test run — no emails sent
"""

import sys
from utils.logger import get_logger
from services.woocommerce_service import get_pending_orders
from services.sheets_service import get_sheet
from services.payment_checker import process_orders

logger = get_logger(__name__)


def main():
    dry_run = "--dry-run" in sys.argv

    logger.info("=== Payment Automation Started ===")

    # Step 1: Fetch unpaid orders from WooCommerce
    orders = get_pending_orders()

    # Step 2: Connect to tracking sheet
    worksheet = get_sheet()

    # Step 3: Process each order
    process_orders(worksheet, orders, dry_run=dry_run)

    logger.info("=== Payment Automation Finished ===")


if __name__ == "__main__":
    main()
