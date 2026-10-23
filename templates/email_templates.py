"""
Email Templates — Payment Automation
--------------------------------------
All invoice and reminder email content lives here.
To update copy, edit this file only.

Stages:
    0 → Invoice (sent immediately when order is placed)
    1 → Reminder 1 (24 hours later)
    2 → Reminder 2 (48 hours later)
    3 → Final reminder (72 hours later)
"""

from config import (
    REVOLUT_LINK, INTERAC_EMAIL, ORDER_PAYMENT_LINKS,
    BANK_USD, BANK_EUR, BANK_GBP, EUROPEAN_COUNTRIES
)

LOGO_URL    = "https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
WEBSITE_URL = "https://www.iptvsup.com"


def _pay_now_button_html(payment_url: str) -> str:
    """Link to the order's own WooCommerce payment page (Venmo, Cash App, Revolut)."""
    if not payment_url:
        return ""
    return f"""
    <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 12px 0;" width="100%">
        <tr>
            <td align="center">
                <a href="{payment_url}" style="display:block; width:100%; max-width:320px; box-sizing:border-box;
                   background-color:#00a650; color:#ffffff; text-decoration:none; font-size:16px;
                   font-weight:bold; padding:14px 20px; border-radius:8px;" target="_blank">
                   ⚡ Pay instantly — Venmo, Cash App or Revolut
                </a>
            </td>
        </tr>
    </table>
    """


def _button_html(url: str, label: str, color: str, bottom_margin: int) -> str:
    return f"""
    <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 {bottom_margin}px 0;" width="100%">
        <tr>
            <td align="center">
                <a href="{url}" style="display:block; width:100%; max-width:320px; box-sizing:border-box;
                   background-color:{color}; color:#ffffff; text-decoration:none; font-size:16px;
                   font-weight:bold; padding:14px 20px; border-radius:8px;" target="_blank">
                   {label}
                </a>
            </td>
        </tr>
    </table>
    """


def _logo_html(src: str, alt: str) -> str:
    return (f'<img src="{src}" alt="{alt}" width="22" height="22" '
            f'style="vertical-align:middle; border:0; margin-right:8px;">')


def _payment_buttons_html(order_id: str = "") -> str:
    """Revolut button — shown to all customers. Orders with their own
    Cash App / Venmo links (ORDER_PAYMENT_LINKS) also get those buttons."""
    links = ORDER_PAYMENT_LINKS.get(str(order_id))
    if not links:
        return _button_html(REVOLUT_LINK, "💳 Pay with Credit Card", "#000000", 28)
    return (
        _button_html(REVOLUT_LINK, "💳 Pay with Credit Card", "#000000", 12)
        + _button_html(links["cashapp"],
                       _logo_html("https://img.icons8.com/ios-filled/50/ffffff/cash-app.png", "Cash App") + "Pay with Cash App",
                       "#00d632", 12)
        + _button_html(links["venmo"],
                       _logo_html("https://img.icons8.com/ios-filled/50/ffffff/venmo.png", "Venmo") + "Pay with Venmo",
                       "#008cff", 28)
    )


def _get_bank_for_country(country: str) -> dict:
    """Returns the correct bank details dictionary based on customer country."""
    code = country.upper()
    if code == "GB":
        return BANK_GBP
    if code in EUROPEAN_COUNTRIES:
        return BANK_EUR
    return BANK_USD  # Default: USA + Canada + rest of world


def _bank_details_html(country: str) -> str:
    """Bank transfer section — shows USD, EUR, or GBP details based on country."""
    bank = _get_bank_for_country(country)
    currency = bank["currency"]

    if currency == "GBP":
        rows = f"""
            <strong>Account Name:</strong> {bank['account_name']}<br/>
            <strong>Bank:</strong> {bank['bank_name']}<br/>
            <strong>Account Number:</strong> {bank['account_number']}<br/>
            <strong>Sort Code:</strong> {bank['sort_code']}<br/>
            <strong>IBAN:</strong> {bank['iban']}<br/>
            <strong>SWIFT/BIC:</strong> {bank['swift']}
        """
    elif currency == "EUR":
        rows = f"""
            <strong>Account Name:</strong> {bank['account_name']}<br/>
            <strong>Bank:</strong> {bank['bank_name']}<br/>
            <strong>IBAN:</strong> {bank['iban']}<br/>
            <strong>SWIFT/BIC:</strong> {bank['swift']}
        """
    else:  # USD
        rows = f"""
            <strong>Account Name:</strong> {bank['account_name']}<br/>
            <strong>Bank:</strong> {bank['bank_name']}<br/>
            <strong>Account Number:</strong> {bank['account_number']}<br/>
            <strong>Account Type:</strong> {bank['account_type']}<br/>
            <strong>Routing Number:</strong> {bank['routing_number']}<br/>
            <strong>SWIFT/BIC:</strong> {bank['swift']}
        """

    return f"""
    <table border="0" cellpadding="0" cellspacing="0" role="presentation"
           style="border:1px solid #e9ecef; border-radius:8px; overflow:hidden; margin:0 0 22px 0;" width="100%">
        <tr>
            <td style="padding:14px 12px; background-color:#f8f9fb; border-bottom:1px solid #e9ecef;
                       font-size:16px; font-weight:700; color:#111111;">
                Bank Transfer Details ({currency})
            </td>
        </tr>
        <tr>
            <td style="padding:16px 12px; font-size:15px; line-height:1.8; word-break:break-word;">
                {rows}
            </td>
        </tr>
    </table>
    """


def _interac_html() -> str:
    """Interac e-Transfer section — shown to Canadian customers only."""
    return f"""
    <table border="0" cellpadding="0" cellspacing="0" role="presentation"
           style="border:1px solid #e9ecef; border-radius:8px; overflow:hidden; margin:0 0 22px 0;" width="100%">
        <tr>
            <td style="padding:14px 12px; background-color:#f8f9fb; border-bottom:1px solid #e9ecef;
                       font-size:16px; font-weight:700; color:#111111;">
                Interac e-Transfer (Canada)
            </td>
        </tr>
        <tr>
            <td style="padding:16px 12px; font-size:15px; line-height:1.8;">
                Send your Interac e-Transfer to:<br/>
                <strong>{INTERAC_EMAIL}</strong><br/>
                Please include your <strong>Order Number</strong> as the message/reference.
            </td>
        </tr>
    </table>
    """


def _base_html(name: str, order_id: str, amount: str, country: str,
               headline: str, intro: str, extra_note: str = "", payment_url: str = "") -> str:
    """
    Builds the full invoice/reminder email layout.
    Automatically adds the Interac section for Canadian customers (country == 'CA').
    """
    name_display  = name if name else "there"
    interac_block = _interac_html() if country.upper() == "CA" else ""
    note_block    = f"""
    <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 22px 0;" width="100%">
        <tr>
            <td style="background-color:#fff8e5; border-left:4px solid #f2c94c; padding:14px 14px;
                       font-size:14px; line-height:1.6; color:#444444;">
                <strong>Important:</strong> Please include your <strong>Order Number #{order_id}</strong>
                as the payment reference so we can match your payment correctly.
            </td>
        </tr>
    </table>
    """ if not extra_note else f"""
    <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 22px 0;" width="100%">
        <tr>
            <td style="background-color:#fff8e5; border-left:4px solid #f2c94c; padding:14px 14px;
                       font-size:14px; line-height:1.6; color:#444444;">
                {extra_note}
            </td>
        </tr>
    </table>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head><meta charset="utf-8"/><meta content="width=device-width, initial-scale=1.0" name="viewport"/></head>
    <body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, Helvetica, sans-serif; color:#333333;">
        <table border="0" cellpadding="0" cellspacing="0" role="presentation"
               style="background-color:#f4f6f9; margin:0; padding:0;" width="100%">
            <tr>
                <td align="center" style="padding:20px 10px;">
                    <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                           style="max-width:600px; background-color:#ffffff; border-radius:12px;
                                  overflow:hidden; box-shadow:0 4px 18px rgba(0,0,0,0.08);" width="100%">

                        <!-- Header -->
                        <tr>
                            <td align="center" style="background-color:#111111; padding:24px 20px;">
                                <a href="{WEBSITE_URL}">
                                    <img alt="IPTV Sup" src="{LOGO_URL}"
                                         style="display:block; max-width:180px; height:auto; max-height:70px;
                                                margin:0 auto 12px auto; border:0;"/>
                                </a>
                                <h1 style="margin:0; font-size:22px; color:#ffffff; font-weight:700;">{headline}</h1>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding:28px 20px;">
                                <p style="margin:0 0 16px 0; font-size:16px; line-height:1.6;">
                                    Hello <strong>{name_display}</strong>,
                                </p>
                                <p style="margin:0 0 20px 0; font-size:16px; line-height:1.6;">{intro}</p>

                                <!-- Order summary -->
                                <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                       style="border:1px solid #e9ecef; border-radius:8px; overflow:hidden; margin:0 0 24px 0;" width="100%">
                                    <tr>
                                        <td style="padding:14px 12px; background-color:#f8f9fb;
                                                   font-size:15px; border-bottom:1px solid #e9ecef;">
                                            <strong>Order Number:</strong> #{order_id}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding:14px 12px; font-size:15px; border-bottom:1px solid #e9ecef;">
                                            <strong>Amount Due:</strong> ${amount} USD
                                        </td>
                                    </tr>
                                </table>

                                <p style="margin:0 0 18px 0; font-size:16px; line-height:1.6;">
                                    Complete your payment using one of the methods below:
                                </p>

                                {"" if str(order_id) in ORDER_PAYMENT_LINKS else _pay_now_button_html(payment_url)}
                                {_payment_buttons_html(order_id)}
                                {interac_block}
                                {_bank_details_html(country)}
                                {note_block}

                                <p style="margin:0 0 16px 0; font-size:15px; line-height:1.6;">
                                    If you have any questions or need help with payment, simply reply to this email.
                                </p>
                                <p style="margin:0; font-size:15px; line-height:1.7;">
                                    Best regards,<br/>
                                    <strong>IPTV Sup</strong><br/>
                                    contact@iptvsup.com
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding:16px 20px; background-color:#fafafa;
                                font-size:12px; color:#777777;">
                                <a href="{WEBSITE_URL}" style="color:#1a1a2e; text-decoration:none; font-weight:bold;">
                                    www.iptvsup.com
                                </a><br/><br/>
                                &copy; IPTV Sup &mdash; Invoice Payment Notice
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ---------------------------------------------------------------------------
# Stage 0 — Invoice (immediate)
# ---------------------------------------------------------------------------

def _stage0(name: str, order_id: str, amount: str, plan: str, country: str,
            payment_url: str = "", kind: str = "invoice") -> dict:
    if kind == "card":
        return {
            "subject": f"Complete your payment — Order #{order_id}",
            "body": _base_html(
                name=name, order_id=order_id, amount=amount, country=country, payment_url=payment_url,
                headline="Finish Your Payment",
                intro=f"It looks like your payment for <strong>{plan}</strong> wasn't completed. You can finish it in one click below, or pay another way if that's easier.",
            )
        }
    return {
        "subject": f"Your IPTV Sup Invoice — Order #{order_id}",
        "body": _base_html(
            name=name, order_id=order_id, amount=amount, country=country, payment_url=payment_url,
            headline="Invoice Payment",
            intro=f"Thank you for your order of <strong>{plan}</strong>. Please find your payment details below.",
        )
    }


# ---------------------------------------------------------------------------
# Stage 1 — Reminder (24h)
# ---------------------------------------------------------------------------

def _stage1(name: str, order_id: str, amount: str, plan: str, country: str,
            payment_url: str = "", kind: str = "invoice") -> dict:
    return {
        "subject": f"Reminder: Your payment for Order #{order_id} is pending",
        "body": _base_html(
            name=name, order_id=order_id, amount=amount, country=country, payment_url=payment_url,
            headline="Payment Reminder",
            intro=f"This is a friendly reminder that your payment for <strong>{plan}</strong> is still pending. Your order is reserved — complete your payment to confirm it.",
        )
    }


# ---------------------------------------------------------------------------
# Stage 2 — Reminder (48h)
# ---------------------------------------------------------------------------

def _stage2(name: str, order_id: str, amount: str, plan: str, country: str,
            payment_url: str = "", kind: str = "invoice") -> dict:
    return {
        "subject": f"Your Order #{order_id} is still unpaid — action needed",
        "body": _base_html(
            name=name, order_id=order_id, amount=amount, country=country, payment_url=payment_url,
            headline="Payment Still Pending",
            intro=f"Your payment for <strong>{plan}</strong> has not been received yet. Please complete your payment as soon as possible to avoid your order being cancelled.",
        )
    }


# ---------------------------------------------------------------------------
# Stage 3 — Final reminder (72h)
# ---------------------------------------------------------------------------

def _stage3(name: str, order_id: str, amount: str, plan: str, country: str,
            payment_url: str = "", kind: str = "invoice") -> dict:
    return {
        "subject": f"Final notice: Order #{order_id} will be cancelled soon",
        "body": _base_html(
            name=name, order_id=order_id, amount=amount, country=country, payment_url=payment_url,
            headline="Final Payment Notice",
            intro=f"This is your final reminder. Your order for <strong>{plan}</strong> will be cancelled if payment is not received shortly. Complete your payment now to keep your order active.",
            extra_note="<strong>Important:</strong> This is your last reminder. If payment is not received, your order will be cancelled automatically."
        )
    }


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

STAGE_FUNCTIONS = {
    0: _stage0,
    1: _stage1,
    2: _stage2,
    3: _stage3,
}


def get_email_content(stage: int, name: str, amount: str,
                      plan: str, order_id: str, country: str,
                      payment_url: str = "", kind: str = "invoice") -> dict | None:
    """kind: "invoice" (Invoice Payment order) or "card" (abandoned PayGate payment)."""
    fn = STAGE_FUNCTIONS.get(stage)
    if fn is None:
        return None
    return fn(name=name, order_id=order_id, amount=amount, plan=plan, country=country,
              payment_url=payment_url, kind=kind)


# ---------------------------------------------------------------------------
# Payment confirmation (sent when WooCommerce order status → completed)
# ---------------------------------------------------------------------------

def get_confirmation_email(name: str, order_id: str, amount: str, plan: str) -> dict:
    name_display = name if name else "there"
    return {
        "subject": f"Payment Confirmed — Order #{order_id} | IPTV Sup",
        "body": f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/><meta content="width=device-width, initial-scale=1.0" name="viewport"/></head>
<body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, Helvetica, sans-serif; color:#333333;">
    <table border="0" cellpadding="0" cellspacing="0" role="presentation"
           style="background-color:#f4f6f9; margin:0; padding:0;" width="100%">
        <tr>
            <td align="center" style="padding:20px 10px;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                       style="max-width:600px; background-color:#ffffff; border-radius:12px;
                              overflow:hidden; box-shadow:0 4px 18px rgba(0,0,0,0.08);" width="100%">

                    <!-- Header -->
                    <tr>
                        <td align="center" style="background-color:#111111; padding:24px 20px;">
                            <a href="{WEBSITE_URL}">
                                <img alt="IPTV Sup" src="{LOGO_URL}"
                                     style="display:block; max-width:180px; height:auto; max-height:70px;
                                            margin:0 auto 12px auto; border:0;"/>
                            </a>
                            <h1 style="margin:0; font-size:22px; color:#ffffff; font-weight:700;">Payment Confirmed</h1>
                        </td>
                    </tr>

                    <!-- Green banner -->
                    <tr>
                        <td align="center" style="background-color:#d4edda; padding:14px 20px;
                            font-size:16px; font-weight:700; color:#155724;">
                            Your payment has been received. Thank you!
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding:28px 20px;">
                            <p style="margin:0 0 16px 0; font-size:16px; line-height:1.6;">
                                Hello <strong>{name_display}</strong>,
                            </p>
                            <p style="margin:0 0 20px 0; font-size:16px; line-height:1.6;">
                                We have received your payment and your order is now confirmed.
                                Your subscription will be activated shortly.
                            </p>

                            <!-- Order summary -->
                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                   style="border:1px solid #e9ecef; border-radius:8px; overflow:hidden; margin:0 0 24px 0;" width="100%">
                                <tr>
                                    <td style="padding:14px 12px; background-color:#f8f9fb;
                                               font-size:15px; border-bottom:1px solid #e9ecef;">
                                        <strong>Order Number:</strong> #{order_id}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:14px 12px; font-size:15px; border-bottom:1px solid #e9ecef;">
                                        <strong>Plan:</strong> {plan}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:14px 12px; font-size:15px;">
                                        <strong>Amount Paid:</strong> ${amount} USD
                                    </td>
                                </tr>
                            </table>

                            <p style="margin:0 0 16px 0; font-size:15px; line-height:1.6;">
                                If you have any questions, simply reply to this email.
                            </p>
                            <p style="margin:0; font-size:15px; line-height:1.7;">
                                Best regards,<br/>
                                <strong>IPTV Sup</strong><br/>
                                contact@iptvsup.com
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center" style="padding:16px 20px; background-color:#fafafa;
                            font-size:12px; color:#777777;">
                            <a href="{WEBSITE_URL}" style="color:#1a1a2e; text-decoration:none; font-weight:bold;">
                                www.iptvsup.com
                            </a><br/><br/>
                            &copy; IPTV Sup &mdash; Payment Confirmation
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    }
