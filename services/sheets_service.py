import gspread
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials
from utils.logger import get_logger
from config import (
    GOOGLE_CREDENTIALS_FILE, SPREADSHEET_NAME,
    COL_ORDER_ID, COL_NAME, COL_EMAIL, COL_AMOUNT, COL_PLAN,
    COL_COUNTRY, COL_ORDER_DATE, COL_INVOICE_SENT, COL_LAST_REMINDER,
    COL_STAGE, COL_STATUS
)

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_sheet():
    """Connects to Google Sheets and returns the Payment Tracker worksheet."""
    try:
        creds       = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
        client      = gspread.authorize(creds)
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet   = spreadsheet.sheet1
        logger.info(f"Connected to Google Sheet: '{SPREADSHEET_NAME}'")
        return worksheet
    except FileNotFoundError:
        logger.error(f"credentials.json not found at: {GOOGLE_CREDENTIALS_FILE}")
        raise
    except gspread.SpreadsheetNotFound:
        logger.error(f"Spreadsheet '{SPREADSHEET_NAME}' not found. Share it with the service account.")
        raise


def get_all_tracked_orders(worksheet) -> list[dict]:
    """Returns all rows in the sheet as a list of dictionaries."""
    expected = [
        COL_ORDER_ID, COL_NAME, COL_EMAIL, COL_AMOUNT, COL_PLAN,
        COL_COUNTRY, COL_ORDER_DATE, COL_INVOICE_SENT, COL_LAST_REMINDER,
        COL_STAGE, COL_STATUS
    ]
    records = worksheet.get_all_records(expected_headers=expected)
    logger.info(f"Loaded {len(records)} tracked order(s) from sheet")
    return records


def add_order_to_sheet(worksheet, order: dict, invoice_sent: str, stage: int):
    """Adds a new order row to the sheet after sending the invoice."""
    new_row = [
        order["order_id"],
        order["name"],
        order["email"],
        order["amount"],
        order["plan"],
        order["country"],
        order["order_date"],
        invoice_sent,
        "",
        str(stage),
        "pending",
    ]
    worksheet.append_row(new_row)
    logger.info(f"Added order {order['order_id']} to sheet")


def update_reminder_info(worksheet, order_id: str, stage: int, date_sent: str):
    """Updates last_reminder_sent and reminder_stage for an existing order."""
    records = worksheet.get_all_records()
    headers = worksheet.row_values(1)

    for index, row in enumerate(records):
        if str(row.get(COL_ORDER_ID)) == str(order_id):
            row_number        = index + 2
            last_reminder_col = headers.index(COL_LAST_REMINDER) + 1
            stage_col         = headers.index(COL_STAGE) + 1

            worksheet.batch_update([
                {"range": rowcol_to_a1(row_number, last_reminder_col), "values": [[date_sent]]},
                {"range": rowcol_to_a1(row_number, stage_col),         "values": [[str(stage)]]},
            ])
            logger.info(f"Updated order {order_id} → stage={stage}, last_reminder_sent={date_sent}")
            return

    logger.warning(f"Order {order_id} not found in sheet for update")


def update_order_status(worksheet, order_id: str, new_status: str):
    """Updates the status column for an order (e.g. 'abandoned')."""
    records = worksheet.get_all_records()
    headers = worksheet.row_values(1)

    for index, row in enumerate(records):
        if str(row.get(COL_ORDER_ID)) == str(order_id):
            row_number = index + 2
            status_col = headers.index(COL_STATUS) + 1

            worksheet.update_cell(row_number, status_col, new_status)
            logger.info(f"Updated order {order_id} → status={new_status}")
            return

    logger.warning(f"Order {order_id} not found in sheet for status update")
