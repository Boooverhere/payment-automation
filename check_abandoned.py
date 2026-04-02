"""
Abandoned Checkout Runner
--------------------------
Called every hour by cron. Checks click_pending.json and sends
follow-up emails to anyone who clicked checkout but didn't order.
"""

from utils.logger import get_logger
from services.abandoned_click_checker import run

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("=== Abandoned Checkout Check Started ===")
    run()
    logger.info("=== Abandoned Checkout Check Finished ===")
