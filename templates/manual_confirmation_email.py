"""
Manual Payment Confirmation Email
-----------------------------------
Sent by an admin after manually verifying a payment (bank transfer,
Interac, etc.) that was not automatically detected.

Usage:
    from templates.manual_confirmation_email import get_manual_confirmation_email

    email = get_manual_confirmation_email(
        name="John",
        order_id="1234",
        amount="29.99",
        plan="12-Month Premium",
        payment_method="Bank Transfer",   # optional
        note="",                           # optional custom note
    )
"""

LOGO_URL    = "https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
WEBSITE_URL = "https://www.iptvsup.com"


def get_manual_confirmation_email(
    name: str,
    order_id: str,
    amount: str,
    plan: str,
    payment_method: str = "",
    note: str = "",
) -> dict:
    name_display   = name if name else "there"
    method_display = payment_method if payment_method else "Manual Payment"

    method_row = f"""
                <tr>
                    <td style="padding:14px 12px; font-size:15px; border-bottom:1px solid #e9ecef;">
                        <strong>Payment Method:</strong> {method_display}
                    </td>
                </tr>
    """ if payment_method else ""

    note_block = f"""
                <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                       style="margin:0 0 22px 0;" width="100%">
                    <tr>
                        <td style="background-color:#fff8e5; border-left:4px solid #f2c94c;
                                   padding:14px; font-size:14px; line-height:1.6; color:#444444;">
                            {note}
                        </td>
                    </tr>
                </table>
    """ if note else ""

    return {
        "subject": f"Payment Confirmed — Order #{order_id} | IPTV Sup",
        "body": f"""<!DOCTYPE html>
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
                                We have manually verified your payment and your order is now confirmed.
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
                                    <td style="padding:14px 12px; font-size:15px; border-bottom:1px solid #e9ecef;">
                                        <strong>Amount Paid:</strong> ${amount} USD
                                    </td>
                                </tr>
                                {method_row}
                            </table>

                            {note_block}

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
</html>"""
    }
