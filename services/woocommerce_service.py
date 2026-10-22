import requests
from datetime import datetime, timezone, timedelta
from utils.logger import get_logger
from config import WC_STORE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET, INVOICE_PAYMENT_METHODS

logger = get_logger(__name__)


def get_pending_orders() -> list[dict]:
    """
    Fetches unpaid orders from the WooCommerce API:
    - "processing" Invoice Payment orders (no payment recorded yet)
    - "pending" orders where the customer left the PayGate payment page
    Orders paid through PayGate also pass through "processing", so the
    payment method decides — those must never get an invoice.
    Returns a list of simplified order dictionaries.
    """
    endpoint = f"{WC_STORE_URL}/wp-json/wc/v3/orders"
    orders   = []
    page     = 1

    while True:
        # Using query string auth instead of Basic Auth
        # (some hosting setups strip the Authorization header)
        # Only fetch orders from the last 15 days
        since = (datetime.now(timezone.utc) - timedelta(days=15)).strftime("%Y-%m-%dT%H:%M:%S")

        params = {
            "consumer_key":    WC_CONSUMER_KEY,
            "consumer_secret": WC_CONSUMER_SECRET,
            "status":          "processing,pending",
            "after":           since,
            "per_page":        100,
            "page":            page,
        }

        try:
            response = requests.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            batch = response.json()

            if not batch:
                break  # No more pages

            orders.extend(batch)
            page += 1

        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to WooCommerce at {WC_STORE_URL}. Check the URL.")
            break
        except requests.exceptions.HTTPError as e:
            logger.error(f"WooCommerce API error: {e}")
            break
        except requests.exceptions.Timeout:
            logger.error("WooCommerce API request timed out.")
            break

    parsed = [_parse_order(o) for o in orders]
    unpaid = [o for o in parsed if is_awaiting_payment(o)]
    logger.info(f"Fetched {len(orders)} processing/pending order(s) from WooCommerce, {len(unpaid)} awaiting payment")
    return unpaid


def is_awaiting_payment(order: dict) -> bool:
    """True for orders we should chase for payment."""
    if order["date_paid"]:
        return False
    if order["status"] == "processing":
        return order["payment_method"] in INVOICE_PAYMENT_METHODS
    # "pending" = checkout reached the payment step but no payment arrived
    return order["status"] == "pending" and bool(order["payment_method"])


def is_invoice_order(order: dict) -> bool:
    return order["payment_method"] in INVOICE_PAYMENT_METHODS


def cancel_order(order_id: str, note: str) -> bool:
    """Cancels an unpaid order in WooCommerce and leaves a note explaining why."""
    endpoint = f"{WC_STORE_URL}/wp-json/wc/v3/orders/{order_id}"
    params   = {"consumer_key": WC_CONSUMER_KEY, "consumer_secret": WC_CONSUMER_SECRET}
    try:
        requests.post(f"{endpoint}/notes", params=params, json={"note": note}, timeout=15).raise_for_status()
        response = requests.put(endpoint, params=params, json={"status": "cancelled"}, timeout=15)
        response.raise_for_status()
        logger.info(f"Order {order_id} | Cancelled in WooCommerce")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Order {order_id} | Could not cancel in WooCommerce: {e}")
        return False


def has_order_since(email: str, since: datetime) -> bool:
    """True if this email placed any WooCommerce order (paid or not) after `since`."""
    params = {
        "consumer_key":    WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET,
        "search":          email,
        "after":           since.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "status":          "any",
        "per_page":        20,
    }
    try:
        response = requests.get(f"{WC_STORE_URL}/wp-json/wc/v3/orders", params=params, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not look up orders for {email}: {e}")
        raise
    return any((o.get("billing", {}).get("email") or "").strip().lower() == email.lower()
               for o in response.json())


def get_product(product_id: str) -> dict:
    """
    Fetches a single product from WooCommerce by ID.
    Returns name, price, and image URL.
    """
    endpoint = f"{WC_STORE_URL}/wp-json/wc/v3/products/{product_id}"
    params = {
        "consumer_key":    WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET,
    }
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        images = data.get("images", [])
        return {
            "name":  data.get("name", ""),
            "price": data.get("price", ""),
            "image": images[0].get("src", "") if images else "",
        }
    except Exception as e:
        logger.error(f"Could not fetch product {product_id}: {e}")
        return {"name": "", "price": "", "image": ""}


def _parse_order(order: dict) -> dict:
    """
    Extracts only the fields we need from a raw WooCommerce order.
    """
    billing  = order.get("billing", {})
    items    = order.get("line_items", [])

    # Get the plan name from the first line item
    plan = items[0].get("name", "Subscription") if items else "Subscription"

    # Full name from billing
    first_name = billing.get("first_name", "")
    last_name  = billing.get("last_name", "")
    full_name  = f"{first_name} {last_name}".strip()

    return {
        "order_id":    str(order.get("id", "")),
        "name":        full_name,
        "email":       billing.get("email", ""),
        "amount":      order.get("total", "0.00"),
        "currency":    order.get("currency", "USD"),
        "plan":        plan,
        "country":     billing.get("country", ""),
        "order_date":  order.get("date_created_gmt", order.get("date_created", "")),
        "status":         order.get("status", ""),
        "payment_method": order.get("payment_method", ""),
        "date_paid":      order.get("date_paid") or "",
        "payment_url":    order.get("payment_url", ""),
    }
