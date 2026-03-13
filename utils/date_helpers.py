from datetime import datetime, timezone
from config import REMINDER_HOURS


def parse_wc_datetime(dt_string: str) -> datetime | None:
    """
    Parses WooCommerce datetime strings into a timezone-aware datetime object.
    WooCommerce returns dates in ISO 8601 format: '2026-03-12T14:30:00'
    """
    if not dt_string:
        return None
    try:
        # WooCommerce dates are in UTC
        return datetime.fromisoformat(dt_string).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def hours_since_order(order_date: datetime) -> float:
    """
    Returns how many hours have passed since the order was placed.
    """
    now = datetime.now(timezone.utc)
    delta = now - order_date
    return delta.total_seconds() / 3600


def get_reminder_stage(hours_elapsed: float) -> int | None:
    """
    Returns the reminder stage based on hours since order was placed.

    REMINDER_HOURS = [24, 48, 72]
    - 0 hours     → stage 0 (send invoice immediately)
    - 24+ hours   → stage 1 (first reminder)
    - 48+ hours   → stage 2 (second reminder)
    - 72+ hours   → stage 3 (final reminder)
    - None        → abandoned (stop emailing)

    Returns None only if already past final reminder AND we've already
    sent stage 3 — caller handles the abandoned logic.
    """
    if hours_elapsed < REMINDER_HOURS[0]:
        return 0  # Invoice stage — order just placed

    for index, threshold in enumerate(REMINDER_HOURS):
        if hours_elapsed < threshold:
            return index  # Still in previous stage window
        if index == len(REMINDER_HOURS) - 1:
            return len(REMINDER_HOURS)  # Past final reminder

    return 0
