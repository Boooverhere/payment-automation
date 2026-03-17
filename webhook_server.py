"""
WooCommerce Webhook Server
--------------------------
Receives instant order notifications from WooCommerce and fires
the invoice email immediately — no waiting for the hourly cron.

WooCommerce sends a POST to /webhook/order every time an order
is created with status 'processing'.

The hourly cron (app.py) still runs as a fallback for:
- Orders that the webhook may have missed
- Sending 24h / 48h / 72h reminders
"""

import hashlib
import hmac
import base64
import os
from datetime import date
from flask import Flask, request, jsonify

from services.sheets_service import get_sheet, add_order_to_sheet, get_all_tracked_orders
from services.email_service import send_email
from services.woocommerce_service import _parse_order
from templates.email_templates import get_email_content
from utils.logger import get_logger
from config import WEBHOOK_SECRET, COL_ORDER_ID

logger = get_logger(__name__)
app = Flask(__name__)


def _verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verifies the WooCommerce webhook HMAC-SHA256 signature.
    WooCommerce signs the raw body with the webhook secret and
    sends it as a base64 string in X-WC-Webhook-Signature.
    """
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not set — skipping signature verification")
        return True

    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).digest()
    expected_b64 = base64.b64encode(expected).decode()
    logger.debug(f"Signature received : '{signature[:20]}...'")
    logger.debug(f"Signature expected : '{expected_b64[:20]}...'")
    return hmac.compare_digest(expected_b64, signature)


@app.route("/webhook/order", methods=["POST"])
def order_webhook():
    # 1. Verify the request is genuinely from WooCommerce
    logger.debug(f"Headers received: {dict(request.headers)}")
    signature = request.headers.get("X-WC-Webhook-Signature", "")
    if not _verify_signature(request.data, signature):
        logger.warning("Webhook received with invalid signature — rejected")
        return jsonify({"error": "invalid signature"}), 401

    # 2. Parse the order payload
    raw_order = request.get_json(silent=True)
    if not raw_order:
        return jsonify({"error": "empty or invalid JSON"}), 400

    order = _parse_order(raw_order)
    order_id = order["order_id"]
    email = order["email"]

    logger.info(f"Webhook received | Order {order_id} | {email}")

    if not email:
        logger.warning(f"Webhook | Order {order_id} | No email — skipping")
        return jsonify({"ok": True, "note": "no email on order"}), 200

    # 3. Skip if already tracked (prevents duplicate invoice on retry)
    try:
        worksheet = get_sheet()
        tracked = get_all_tracked_orders(worksheet)
        tracked_ids = {str(r[COL_ORDER_ID]) for r in tracked if r.get(COL_ORDER_ID)}

        if order_id in tracked_ids:
            logger.info(f"Webhook | Order {order_id} | Already tracked — skipping invoice")
            return jsonify({"ok": True, "note": "already tracked"}), 200

        # 4. Send invoice immediately
        content = get_email_content(
            stage=0,
            name=order["name"],
            amount=order["amount"],
            plan=order["plan"],
            order_id=order_id,
            country=order["country"],
        )

        success = send_email(email, content["subject"], content["body"])

        if success:
            add_order_to_sheet(worksheet, order, invoice_sent=date.today().strftime("%Y-%m-%d"), stage=0)
            logger.info(f"Webhook | Order {order_id} | Invoice sent → {email}")
            return jsonify({"ok": True}), 200
        else:
            logger.error(f"Webhook | Order {order_id} | Email send failed")
            return jsonify({"error": "email failed"}), 500

    except Exception as e:
        logger.error(f"Webhook | Order {order_id} | Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Simple health check so you can confirm the server is running."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    logger.info(f"Webhook server starting on port {port}")
    app.run(host="0.0.0.0", port=port)
