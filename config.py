
import os
from dotenv import load_dotenv

load_dotenv()

# --- WooCommerce API ---
WC_STORE_URL        = os.getenv("WC_STORE_URL", "https://iptvsup.com")
WC_CONSUMER_KEY     = os.getenv("WC_CONSUMER_KEY")
WC_CONSUMER_SECRET  = os.getenv("WC_CONSUMER_SECRET")

# --- Google Sheets ---
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_NAME        = os.getenv("SPREADSHEET_NAME", "Payment Tracker")

# --- Email SMTP ---
SENDER_EMAIL     = os.getenv("SENDER_EMAIL")
SENDER_NAME      = os.getenv("SENDER_NAME", "IPTV Sup")
SMTP_LOGIN       = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD    = os.getenv("SMTP_PASSWORD")
SMTP_HOST        = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
SMTP_PORT        = int(os.getenv("SMTP_PORT", "587"))

# --- Payment links ---
PAYPAL_LINK      = "https://www.paypal.com/paypalme/basmaa175"
REVOLUT_LINK     = "https://revolut.me/basmaa93"
INTERAC_EMAIL    = "elyoussefimehdi@gmail.com"   # Canada only

# --- Per-order Cash App / Venmo links (PayGate links are tied to one customer + amount) ---
# Orders listed here get Credit Card + Cash App + Venmo buttons in every email,
# instead of the "Pay instantly" button.
ORDER_PAYMENT_LINKS = {
    "5302": {
        "cashapp": "https://checkout.paygate.sbs/process-payment.php?address=rerEtiDoe3xbPzjJyWBHySKWr8f%2FebtMfyeYUOzmsAMnKIXicUf1BFm8c3EHrSrX%2BOMwbeXXBFTp%2FKMKsZ5Hew%3D%3D&amount=39.99&provider=cashapp&email=Liammarshwood%40minister.com&currency=USD",
        "venmo":   "https://checkout.paygate.sbs/process-payment.php?address=O3RvGu%2BmECwhSkwdT28vmINZj2Jgb7J2KEqcX67GTBuowXFZOlOXlXhbXqF1x4Bn63mUR2%2BA41nfiSnqHockfQ%3D%3D&amount=39.99&provider=venmo&email=Liammarshwood%40minister.com&currency=USD",
    },
}

# --- Bank transfer — USD (USA + rest of world) ---
BANK_USD = {
    "account_name":   "Mehdi el youssoufi",
    "bank_name":      "Community Federal Savings Bank",
    "account_number": "8312325588",
    "account_type":   "Checking",
    "routing_number": "026073150",
    "swift":          "CMFGUS33",
    "currency":       "USD",
}

# --- Bank transfer — EUR (European customers) ---
BANK_EUR = {
    "account_name": "Mehdi el youssoufi",
    "bank_name":    "Wise",
    "iban":         "BE86 9674 0020 1350",
    "swift":        "TRWIBEB1XXX",
    "currency":     "EUR",
}

# --- Bank transfer — GBP (UK customers) ---
BANK_GBP = {
    "account_name":   "Mehdi el youssoufi",
    "bank_name":      "Wise Payments Limited",
    "account_number": "28680737",
    "sort_code":      "23-14-70",
    "iban":           "GB02 TRWI 2314 7028 6807 37",
    "swift":          "TRWIGB2LXXX",
    "currency":       "GBP",
}

# --- European country codes (show EUR bank details) ---
EUROPEAN_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE", "CH", "NO", "IS"
}

# --- Webhook ---
WEBHOOK_SECRET      = os.getenv("WEBHOOK_SECRET")        # WooCommerce webhook HMAC secret
BREVO_WEBHOOK_TOKEN = os.getenv("BREVO_WEBHOOK_TOKEN")   # Bearer token for Brevo click events
CHECKOUT_SECRET     = os.getenv("CHECKOUT_SECRET")        # Token for /webhook/checkout-started
WEBHOOK_PORT        = int(os.getenv("WEBHOOK_PORT", "8000"))

# --- Brevo API (same key as SMTP_PASSWORD) ---
BREVO_API_KEY = os.getenv("BREVO_API_KEY", SMTP_PASSWORD)

# --- Reminder schedule (hours after order) ---
REMINDER_HOURS = [24, 48, 72]

# --- Which orders get chased ---
# Only "Invoice Payment" orders wait for a manual payment. Orders placed with
# Venmo / Cash App / Revolut (PayGate) are paid instantly; if the customer
# abandons the PayGate page they stay "pending" and get a finish-payment email.
INVOICE_PAYMENT_METHODS = {"cod"}
CARD_PENDING_MIN_HOURS  = 1     # give the customer time to finish on PayGate first

# Cancel the WooCommerce order this many hours after it was placed if it is
# still unpaid and the final reminder has gone out. None = never cancel.
# Customers sometimes pay weeks later, so keep this generous.
CANCEL_UNPAID_AFTER_HOURS = 30 * 24

# How far back to look for unpaid orders; must cover the cancel window above.
ORDER_LOOKBACK_DAYS = 35

# --- Emails to never send to (add lowercase addresses here) ---
EXCLUDED_EMAILS = {
    "isaacontheprize@graduate.org",
}

# --- Sheet column names ---
COL_ORDER_ID        = "order_id"
COL_NAME            = "customer_name"
COL_EMAIL           = "email"
COL_AMOUNT          = "amount"
COL_PLAN            = "plan"
COL_COUNTRY         = "country"
COL_ORDER_DATE      = "order_date"
COL_INVOICE_SENT    = "invoice_sent"
COL_LAST_REMINDER   = "last_reminder_sent"
COL_STAGE           = "reminder_stage"
COL_STATUS          = "status"
