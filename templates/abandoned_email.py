"""
Abandoned Checkout Follow-Up Email
------------------------------------
Sent ~2 hours after someone clicks the win-back checkout link but doesn't order.
Short, personal, no pressure — just a nudge with the offer still available.
"""

CHECKOUT_URL = "https://www.iptvsup.com/checkout/"

ABANDONED_SUBJECT = "You left something behind"


def get_abandoned_email(
    checkout_url: str = "",
    product_name: str = "",
    product_price: str = "",
    product_image: str = "",
    discount: str = "",
    discounted_price: str = "",
) -> dict:
    url = checkout_url if checkout_url else CHECKOUT_URL

    if product_name and product_image:
        # Price display — show original struck through + discounted if discount applies
        if discount and discounted_price:
            price_display = f"""
                <p style="margin: 0 0 4px 0; font-size: 13px; color: #999;
                           text-decoration: line-through;">${product_price} USD</p>
                <p style="margin: 0 0 4px 0; font-size: 16px; font-weight: 800; color: #c0392b;">
                    ${discounted_price} USD
                </p>
                <p style="margin: 0; font-size: 12px; color: #c0392b; font-weight: 700;">{discount} OFF — applied at checkout</p>
            """
        elif product_price:
            price_display = f"<p style='margin: 0; font-size: 14px; color: #666;'>${product_price} USD</p>"
        else:
            price_display = ""

        # Discount badge — only shown when discount is provided
        discount_badge = f"""
            <td style="padding: 0 16px 0 0; vertical-align: middle; text-align: center; white-space: nowrap;">
                <table cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="background-color: #c0392b; border-radius: 50px; padding: 5px 12px;">
                            <span style="font-size: 20px; font-weight: 900; color: #ffffff; line-height: 1;">{discount}</span>
                        </td>
                    </tr>
                </table>
            </td>
        """ if discount else ""

        product_card = f"""
        <tr>
            <td style="padding: 0 32px 28px 32px;">
                <table width="100%" cellpadding="0" cellspacing="0"
                       style="border: 1px solid #ebebeb; border-radius: 10px; overflow: hidden; background-color: #fafafa;">
                    <tr>
                        <td width="110" style="padding: 16px; vertical-align: middle; text-align: center;">
                            <a href="{url}">
                                <img src="{product_image}" alt="{product_name}"
                                     style="display: block; width: 90px; height: 90px;
                                            object-fit: cover; border-radius: 8px; border: 0;">
                            </a>
                        </td>
                        <td style="padding: 16px 8px 16px 8px; vertical-align: middle; border-left: 1px solid #ebebeb;">
                            <p style="margin: 0 0 6px 0; font-size: 15px; font-weight: 700; color: #111;">
                                <a href="{url}" style="color: #111; text-decoration: none;">{product_name}</a>
                            </p>
                            {price_display}
                        </td>
                        {discount_badge}
                    </tr>
                </table>
            </td>
        </tr>
        """
    else:
        product_card = ""

    # Urgency bar — only shown when discount is provided
    urgency_bar = """
    <tr>
        <td style="background-color: #fff3cd; border-left: 4px solid #e67e22;
                   padding: 12px 32px; font-size: 13px; color: #7d4e00; font-weight: 600;">
            ⏳ This is your last chance — your discounted price expires in a few hours.
        </td>
    </tr>
    """ if discount else ""

    body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/></head>
<body style="margin: 0; padding: 0; background-color: #f0f0f0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333;">

<table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0f0f0; padding: 40px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width: 580px; width: 100%; background-color: #ffffff; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.07);">

    <!-- HEADER -->
    <tr>
        <td style="background-color: #0d0d1a; padding: 28px 32px; text-align: center;">
            <a href="https://www.iptvsup.com">
                <img src="https://iptvsup.com/wp-content/uploads/2023/04/logo-IPTVSUP_Plan-de-travail-1.png"
                     alt="IPTVSup" style="max-height: 60px; max-width: 200px; border: 0;">
            </a>
        </td>
    </tr>

    <!-- DIVIDER -->
    <tr>
        <td style="background: linear-gradient(90deg, #1a1aff 0%, #0d0d1a 100%); height: 3px; font-size: 0; line-height: 0;">&nbsp;</td>
    </tr>

    {urgency_bar}

    <!-- BODY -->
    <tr>
        <td style="padding: 36px 32px 24px 32px;">
            <h2 style="margin: 0 0 16px 0; font-size: 22px; font-weight: 700; color: #0d0d1a; letter-spacing: -0.3px;">
                Still thinking it over?
            </h2>
            <p style="font-size: 15px; line-height: 1.7; margin: 0 0 12px 0; color: #444;">
                You were this close to completing your order. Your <strong>{discount if discount else "exclusive discount"}</strong> is still waiting for you — just pick up where you left off.
            </p>
            <p style="font-size: 15px; line-height: 1.7; margin: 0; color: #444;">
                Any questions? Just reply or reach out on WhatsApp.
            </p>
        </td>
    </tr>

    {product_card}

    <!-- CTA -->
    <tr>
        <td style="padding: 4px 32px 36px 32px;">
            <a href="{url}"
               style="display: inline-block; background-color: #0d0d1a; color: #ffffff;
                      padding: 14px 32px; text-decoration: none; border-radius: 8px;
                      font-weight: 700; font-size: 15px; letter-spacing: 0.2px;">
                Complete My Order →
            </a>
            <p style="font-size: 14px; color: #888; margin: 20px 0 0 0;">– Nathalie, IPTVSup Support</p>
        </td>
    </tr>

    <!-- FOOTER -->
    <tr>
        <td style="background-color: #0d0d1a; padding: 24px 32px; text-align: center;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="text-align: center; padding-bottom: 14px;">
                        <a href="https://www.iptvsup.com" style="color: #8888bb; text-decoration: none; font-size: 13px; margin: 0 10px;">🌐 iptvsup.com</a>
                        <a href="mailto:contact@iptvsup.com" style="color: #8888bb; text-decoration: none; font-size: 13px; margin: 0 10px;">✉️ contact@iptvsup.com</a>
                        <a href="https://wa.me/message/KYISERSGPOL5K1" style="color: #8888bb; text-decoration: none; font-size: 13px; margin: 0 10px;">💬 WhatsApp</a>
                    </td>
                </tr>
            </table>
            <p style="font-size: 11px; color: #555e8a; margin: 0;">
                You are receiving this email because you previously had a subscription with IPTV Sup.
            </p>
        </td>
    </tr>

</table>
</td></tr>
</table>

</body>
</html>"""
    return {"subject": ABANDONED_SUBJECT, "body": body}
