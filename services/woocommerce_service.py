import requests
from datetime import datetime, timezone, timedelta
from utils.logger import get_logger
from config import WC_STORE_URL, WC_CONSUMER_KEY, WC_CONSUMER_SECRET

logger = get_logger(__name__)


def get_pending_orders() -> list[dict]:
    """
    Fetches all orders with status 'pending' from WooCommerce API.
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
            "status":          "processing",
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

    logger.info(f"Fetched {len(orders)} pending order(s) from WooCommerce")
    return [_parse_order(o) for o in orders]


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
    }
