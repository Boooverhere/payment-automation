from services.email_service import send_email
from config import REVOLUT_LINK, BANK_GBP

LOGO_URL    = "https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
WEBSITE_URL = "https://www.iptvsup.com"

# --- Edit these details ---
TO_EMAIL   = "animaniacsstew@gmail.com"
NAME       = "TRAVIS"        # Change to customer name if you know it
ORDER_ID   = "4819"             # Add order number if you have it
AMOUNT     = "55.99"             # Add amount if you have it
PLAN       = "12 Months Television Subscription"             # Add plan name if you have it
# --------------------------

order_line = f"<strong>Order Number:</strong> #{ORDER_ID}<br/>" if ORDER_ID else ""
amount_line = f"<strong>Amount Due:</strong> ${AMOUNT} USD<br/>" if AMOUNT else ""

body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/></head>
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
                            <h1 style="margin:0; font-size:22px; color:#ffffff; font-weight:700;">Invoice Payment</h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding:28px 20px;">
                            <p style="margin:0 0 16px 0; font-size:16px; line-height:1.6;">
                                Hello <strong>{NAME}</strong>,
                            </p>
                            <p style="margin:0 0 20px 0; font-size:16px; line-height:1.6;">
                                Thank you for your order. Please find your payment details below.
                            </p>

                            <!-- Order summary -->
                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                   style="border:1px solid #e9ecef; border-radius:8px; overflow:hidden; margin:0 0 24px 0;" width="100%">
                                <tr>
                                    <td style="padding:14px 12px; font-size:15px; line-height:1.8;">
                                        {order_line}
                                        {amount_line}
                                    </td>
                                </tr>
                            </table>

                            <p style="margin:0 0 18px 0; font-size:16px; line-height:1.6;">
                                Complete your payment using one of the methods below:
                            </p>

                            <!-- Revolut button only -->
                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                   style="margin:0 0 28px 0;" width="100%">
                                <tr>
                                    <td align="center">
                                        <a href="{REVOLUT_LINK}" style="display:block; width:100%; max-width:320px;
                                           box-sizing:border-box; background-color:#000000; color:#ffffff;
                                           text-decoration:none; font-size:16px; font-weight:bold;
                                           padding:14px 20px; border-radius:8px;" target="_blank">
                                           Pay with Credit Card
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- GBP Bank details -->
                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                   style="border:1px solid #e9ecef; border-radius:8px; overflow:hidden; margin:0 0 22px 0;" width="100%">
                                <tr>
                                    <td style="padding:14px 12px; background-color:#f8f9fb; border-bottom:1px solid #e9ecef;
                                               font-size:16px; font-weight:700; color:#111111;">
                                        Bank Transfer Details (GBP)
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding:16px 12px; font-size:15px; line-height:1.8; word-break:break-word;">
                                        <strong>Account Name:</strong> {BANK_GBP['account_name']}<br/>
                                        <strong>Bank:</strong> {BANK_GBP['bank_name']}<br/>
                                        <strong>Account Number:</strong> {BANK_GBP['account_number']}<br/>
                                        <strong>Sort Code:</strong> {BANK_GBP['sort_code']}<br/>
                                        <strong>IBAN:</strong> {BANK_GBP['iban']}<br/>
                                        <strong>SWIFT/BIC:</strong> {BANK_GBP['swift']}
                                    </td>
                                </tr>
                            </table>

                            <!-- Note -->
                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                   style="margin:0 0 22px 0;" width="100%">
                                <tr>
                                    <td style="background-color:#fff8e5; border-left:4px solid #f2c94c;
                                               padding:14px 14px; font-size:14px; line-height:1.6; color:#444444;">
                                        <strong>Important:</strong> Please include your <strong>Order Number</strong>
                                        as the payment reference so we can match your payment correctly.
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
                            &copy; IPTVSup &mdash; Invoice Payment Notice
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

send_email(
    to_email=TO_EMAIL,
    subject="Your 12 Month Premium IPTVSup subscription Invoice",
    body_html=body
)
