"""
Abandoned Checkout Follow-Up Email
------------------------------------
Sent ~2 hours after someone clicks the win-back checkout link but doesn't order.
Short, personal, no pressure — just a nudge with the offer still available.
"""

CHECKOUT_URL = "https://www.iptvsup.com"

ABANDONED_SUBJECT = "Did something go wrong at checkout?"


def get_abandoned_email() -> dict:
    body = f"""
    <html>
    <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif; color: #333;">

    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 30px 0;">
    <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">

        <!-- LOGO HEADER -->
        <tr>
            <td style="background-color: #1a1a2e; padding: 24px; text-align: center;">
                <a href="https://www.iptvsup.com">
                    <img src="https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
                         alt="IPTVSup" style="max-height: 70px; max-width: 220px;">
                </a>
            </td>
        </tr>

        <!-- BODY -->
        <tr>
            <td style="padding: 36px 40px;">

                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 16px 0;">Hey,</p>

                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 16px 0;">
                    I noticed you checked out our offer but didn't complete the order.
                    I just wanted to make sure everything went okay — sometimes checkout
                    can be tricky on mobile or there's a question about payment.
                </p>

                <p style="font-size: 15px; line-height: 1.7; margin: 0 0 24px 0;">
                    Your <strong>25% discount is still available</strong> on 6-month and 12-month plans.
                    If you ran into any issue or have a question, just reply to this email
                    or message us on WhatsApp — we'll sort it out in minutes.
                </p>

                <!-- CTA -->
                <div style="margin: 0 0 28px 0;">
                    <a href="{CHECKOUT_URL}"
                       style="display: inline-block; background-color: #e02020; color: white;
                              padding: 13px 28px; text-decoration: none; border-radius: 5px;
                              font-weight: bold; font-size: 15px;">
                        Complete My Order
                    </a>
                </div>

                <p style="margin: 0 0 16px 0;">
                    <a href="https://wa.me/message/KYISERSGPOL5K1"
                       style="display: inline-block; background-color: #25D366; color: #ffffff;
                              padding: 10px 22px; text-decoration: none; border-radius: 5px;
                              font-weight: bold; font-size: 14px;">
                        💬 Chat on WhatsApp
                    </a>
                </p>

                <p style="font-size: 15px; margin: 24px 0 0 0;">– Nathalie</p>

            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td style="background-color: #1a1a2e; padding: 30px 40px; text-align: center;">
                <p style="margin: 0 0 2px 0; color: #ffffff; font-size: 15px; font-weight: bold;">Nathalie</p>
                <p style="margin: 0 0 16px 0; color: #aab4ff; font-size: 12px;">Customer Service — IPTVSup</p>
                <hr style="border: none; border-top: 1px solid #2d2d5e; margin: 0 0 20px 0;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="text-align: center;">
                            <a href="https://www.iptvsup.com" style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">🌐 iptvsup.com</a>
                            <a href="mailto:contact@iptvsup.com" style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">✉️ contact@iptvsup.com</a>
                            <a href="https://wa.me/message/KYISERSGPOL5K1" style="color: #aab4ff; text-decoration: none; font-size: 13px; margin: 0 12px;">💬 WhatsApp</a>
                        </td>
                    </tr>
                </table>
                <p style="font-size: 11px; color: #555e8a; margin: 20px 0 0 0;">
                    You are receiving this email because you previously had a subscription with IPTV Sup.
                </p>
            </td>
        </tr>

    </table>
    </td></tr>
    </table>

    </body>
    </html>
    """
    return {"subject": ABANDONED_SUBJECT, "body": body}
