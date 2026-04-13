"""
Manual Payment Confirmation Sender
------------------------------------
Run this script from the terminal to send a payment confirmation email
after manually verifying a customer's payment (bank transfer, Interac, etc.).

Usage:
    python send_manual_confirmation.py \
        --email customer@example.com \
        --name  "John Doe" \
        --order 1234 \
        --amount 29.99 \
        --plan  "12-Month Premium" \
        --method "Bank Transfer" \
        --note  "Payment received on April 4, 2026."   # optional

All flags except --note and --method are required.
"""

import argparse
import sys

from services.email_service import send_email
from templates.manual_confirmation_email import get_manual_confirmation_email


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a manual payment confirmation email to a customer."
    )
    parser.add_argument("--email",  required=True, help="Customer email address")
    parser.add_argument("--name",   required=True, help="Customer name")
    parser.add_argument("--order",  required=True, help="WooCommerce order ID")
    parser.add_argument("--amount", required=True, help="Amount paid (e.g. 29.99)")
    parser.add_argument("--plan",   required=True, help="Plan / product name")
    parser.add_argument("--method", default="",    help="Payment method (optional, e.g. Bank Transfer)")
    parser.add_argument("--note",   default="",    help="Extra note shown in the email (optional)")

    args = parser.parse_args()

    email_content = get_manual_confirmation_email(
        name=args.name,
        order_id=args.order,
        amount=args.amount,
        plan=args.plan,
        payment_method=args.method,
        note=args.note,
    )

    print(f"Sending confirmation to {args.email} for order #{args.order}...")

    success = send_email(
        to_email=args.email,
        subject=email_content["subject"],
        body_html=email_content["body"],
    )

    if success:
        print(f"Sent successfully to {args.email}")
    else:
        print("Failed to send email. Check logs for details.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
