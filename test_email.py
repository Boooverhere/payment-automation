from services.email_service import send_email
from templates.email_templates import get_email_content

# Change country to test different bank sections:
# "US" → USD bank details
# "CA" → USD bank details + Interac
# "GB" → GBP bank details
# "FR" → EUR bank details

content = get_email_content(
    stage=0,
    name="Mehdi",
    amount="39.99",
    plan="6 Months Premium Subscription",
    order_id="4791",
    country="GB"  # Change this to test different countries
)

send_email(
    to_email="elyoussefimehdi@gmail.com",
    subject=content["subject"],
    body_html=content["body"]
)
