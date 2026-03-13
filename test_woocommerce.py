from services.woocommerce_service import get_pending_orders

orders = get_pending_orders()

for order in orders:
    print(f"\n--- Order {order['order_id']} ---")
    for key, value in order.items():
        print(f"  {key}: {value}")
