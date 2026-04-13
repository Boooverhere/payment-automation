from services.email_service import send_email
from services.woocommerce_service import get_product
from templates.abandoned_email import get_abandoned_email

# Change product ID to test different plans: 2708, 2709, 2710, 2711
PRODUCT_ID   = "2711"
CHECKOUT_URL = f"https://www.iptvsup.com/checkout/?add-to-cart={PRODUCT_ID}"

product = get_product(PRODUCT_ID)
print(f"Product: {product}")

content = get_abandoned_email(
    checkout_url=CHECKOUT_URL,
    product_name=product["name"],
    product_price=product["price"],
    product_image=product["image"],
)

send_email("elyoussefimehdi@gmail.com", content["subject"], content["body"])
