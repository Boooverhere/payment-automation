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
import json
import os
import time
from datetime import date
from pathlib import Path
from flask import Flask, request, jsonify

from services.sheets_service import get_sheet, add_order_to_sheet, get_all_tracked_orders, update_order_status
from services.email_service import send_email
from services.woocommerce_service import _parse_order
from templates.email_templates import get_email_content, get_confirmation_email
from utils.logger import get_logger
from config import WEBHOOK_SECRET, BREVO_WEBHOOK_TOKEN, CHECKOUT_SECRET, COL_ORDER_ID, COL_STATUS

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
    return hmac.compare_digest(expected_b64, signature)


@app.route("/webhook/order", methods=["POST"])
def order_webhook():
    # 1. Verify the request is genuinely from WooCommerce
    signature = request.headers.get("X-WC-Webhook-Signature", "")

    if not signature:
        # WooCommerce sends an unsigned ping when saving the webhook — just acknowledge it
        logger.info("Webhook ping received (no signature) — acknowledged")
        return jsonify({"ok": True, "note": "ping"}), 200

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


@app.route("/webhook/order-completed", methods=["POST"])
def order_completed_webhook():
    # 1. Verify signature
    signature = request.headers.get("X-WC-Webhook-Signature", "")

    if not signature:
        logger.info("Completed webhook ping received (no signature) — acknowledged")
        return jsonify({"ok": True, "note": "ping"}), 200

    if not _verify_signature(request.data, signature):
        logger.warning("Completed webhook received with invalid signature — rejected")
        return jsonify({"error": "invalid signature"}), 401

    # 2. Parse order
    raw_order = request.get_json(silent=True)
    if not raw_order:
        return jsonify({"error": "empty or invalid JSON"}), 400

    # Only act on completed status
    if raw_order.get("status") != "completed":
        return jsonify({"ok": True, "note": "not completed"}), 200

    order    = _parse_order(raw_order)
    order_id = order["order_id"]
    email    = order["email"]

    logger.info(f"Order completed webhook | Order {order_id} | {email}")

    if not email:
        logger.warning(f"Order completed | Order {order_id} | No email — skipping")
        return jsonify({"ok": True, "note": "no email"}), 200

    try:
        worksheet = get_sheet()

        # 3. Skip if already marked paid (prevents duplicate confirmation emails)
        tracked = get_all_tracked_orders(worksheet)
        for row in tracked:
            if str(row.get(COL_ORDER_ID)) == str(order_id):
                if str(row.get(COL_STATUS, "")).lower() == "paid":
                    logger.info(f"Order completed | Order {order_id} | Already paid — skipping")
                    return jsonify({"ok": True, "note": "already paid"}), 200
                break

        # 4. Send confirmation email
        content = get_confirmation_email(
            name=order["name"],
            order_id=order_id,
            amount=order["amount"],
            plan=order["plan"],
        )
        success = send_email(email, content["subject"], content["body"])

        if success:
            # 4. Mark as paid in the sheet
            update_order_status(worksheet, order_id, "paid")
            logger.info(f"Order completed | Order {order_id} | Confirmation sent → {email}")
            return jsonify({"ok": True}), 200
        else:
            logger.error(f"Order completed | Order {order_id} | Email send failed")
            return jsonify({"error": "email failed"}), 500

    except Exception as e:
        logger.error(f"Order completed | Order {order_id} | Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500


PENDING_FILE      = Path("/app/click_pending.json")
CHECKOUT_LINKS    = {
    "add-to-cart=2708", "add-to-cart=2709", "add-to-cart=2710", "add-to-cart=2711",
    "add-to-cart=714",  "add-to-cart=719",  "add-to-cart=723",  "add-to-cart=728",
}


def _verify_brevo_token(auth_header: str) -> bool:
    if not BREVO_WEBHOOK_TOKEN:
        logger.warning("BREVO_WEBHOOK_TOKEN not set — skipping token verification")
        return True
    expected = f"Bearer {BREVO_WEBHOOK_TOKEN}"
    return hmac.compare_digest(auth_header, expected)


def _append_pending(email: str, checkout_url: str = ""):
    entries = []
    if PENDING_FILE.exists():
        with open(PENDING_FILE) as f:
            entries = json.load(f)

    # Skip if already pending and follow-up not yet sent
    for e in entries:
        if e["email"].lower() == email.lower() and not e.get("follow_up_sent"):
            logger.info(f"Click webhook | {email} | Already pending — skipping duplicate")
            return

    entries.append({
        "email":           email,
        "clicked_at":      time.time(),
        "follow_up_sent":  False,
        "checkout_url":    checkout_url,
    })

    with open(PENDING_FILE, "w") as f:
        json.dump(entries, f, indent=2)

    logger.info(f"Click webhook | {email} | Stored as pending follow-up")


@app.route("/webhook/email-click", methods=["POST"])
def email_click_webhook():
    # 1. Verify Bearer token
    auth = request.headers.get("Authorization", "")
    if not _verify_brevo_token(auth):
        logger.warning("Brevo click webhook | Invalid token — rejected")
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid JSON"}), 400

    event = data.get("event", "")
    email = data.get("email", "").strip()
    link  = data.get("link", "")

    if event != "click":
        return jsonify({"ok": True, "note": "not a click event"}), 200

    if not email:
        return jsonify({"ok": True, "note": "no email in payload"}), 200

    # 2. Only care about checkout link clicks
    if not any(ck in link for ck in CHECKOUT_LINKS):
        logger.info(f"Click webhook | {email} | Non-checkout link — ignored")
        return jsonify({"ok": True, "note": "non-checkout link"}), 200

    # 3. Store for follow-up check
    _append_pending(email, checkout_url=link)
    return jsonify({"ok": True}), 200


@app.route("/webhook/checkout-started", methods=["POST"])
def checkout_started_webhook():
    """
    Receives abandoned checkout signals from two sources:
      1. Brevo automation "Call a webhook" step — payload: {email, ...contact attrs}
      2. WooCommerce JS snippet — payload: {email, checkout_url}

    Stores the contact in click_pending.json so the abandoned checker
    can follow up after 2 hours if no order is placed.
    """
    # Validate secret token passed as ?token= query param
    token = request.args.get("token", "")
    if CHECKOUT_SECRET and not hmac.compare_digest(token, CHECKOUT_SECRET):
        logger.warning("Checkout-started webhook | Invalid token — rejected")
        return jsonify({"error": "unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid JSON"}), 400

    # Brevo sends EMAIL uppercase in some payloads; JS snippet sends lowercase
    email = (
        data.get("email") or data.get("EMAIL") or ""
    ).strip().lower()

    if not email or "@" not in email:
        return jsonify({"ok": True, "note": "no valid email"}), 200

    # checkout_url comes from JS snippet; Brevo doesn't know the cart product
    checkout_url = data.get("checkout_url", "").strip() or "https://www.iptvsup.com/checkout/"

    _append_pending(email, checkout_url=checkout_url)
    return jsonify({"ok": True}), 200


@app.route("/health", methods=["GET"])
def health():
    """Simple health check so you can confirm the server is running."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    logger.info(f"Webhook server starting on port {port}")
    app.run(host="0.0.0.0", port=port)
