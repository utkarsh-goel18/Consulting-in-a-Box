import os
import numpy as np
import pandas as pd


def generate_fast_demo_datasets(output_dir: str, n_customers: int = 5000, n_orders: int = 10000) -> None:
    """Create a compact deterministic demo dataset using vectorized pandas operations."""
    os.makedirs(output_dir, exist_ok=True)
    rng = np.random.default_rng(42)

    categories = ["Electronics", "Fashion & Apparel", "Home & Living", "Beauty & Health", "Grocery & Pantry"]
    products = pd.DataFrame({
        "product_id": [f"PRD-{i:03d}" for i in range(1, 21)],
        "sku": [f"SKU-{i:03d}" for i in range(1, 21)],
        "product_name": [f"NovaMart Product {i}" for i in range(1, 21)],
        "category": [categories[i % len(categories)] for i in range(20)],
        "subcategory": [f"Subcategory {i % 5 + 1}" for i in range(20)],
        "unit_cost": rng.uniform(12, 120, 20).round(2),
        "unit_price": rng.uniform(30, 220, 20).round(2),
        "supplier_name": [f"Supplier {i % 5 + 1}" for i in range(20)],
    })
    products.to_csv(os.path.join(output_dir, "products.csv"), index=False)

    customer_ids = np.arange(1, n_customers + 1)
    regions = np.array(["Tier 1 - West", "Tier 1 - South", "Tier 2 - North", "Tier 2 - Central", "East"])
    segments = np.array(["Consumer", "SMB", "VIP Enterprise"])
    channels = np.array(["Paid Search", "Organic Search", "Paid Social", "Affiliate", "Email Marketing"])
    customers = pd.DataFrame({
        "customer_id": [f"CUST-{i:06d}" for i in customer_ids],
        "signup_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 600, n_customers), unit="D"),
        "customer_name": [f"Customer {i}" for i in customer_ids],
        "email": [f"client_{i}@example.com" for i in customer_ids],
        "region": rng.choice(regions, n_customers),
        "tier": rng.choice(["Tier 1", "Tier 2"], n_customers, p=[0.6, 0.4]),
        "customer_segment": rng.choice(segments, n_customers, p=[0.70, 0.22, 0.08]),
        "acquisition_channel": rng.choice(channels, n_customers),
        "churn_status": rng.random(n_customers) < 0.08,
        "churn_date": pd.NaT,
    })
    customers["signup_date"] = customers["signup_date"].dt.strftime("%Y-%m-%d")
    customers.to_csv(os.path.join(output_dir, "customers.csv"), index=False)

    dates = pd.date_range("2024-04-01", "2024-09-30", periods=n_orders)
    customer_idx = rng.integers(0, n_customers, n_orders)
    partner = rng.choice(["FastLogistics", "ExpressCargo", "BlueDart"], n_orders, p=[0.45, 0.32, 0.23])
    is_q3 = dates.month >= 7
    base_cost = np.select([partner == "FastLogistics", partner == "ExpressCargo"], [72.4, 68.1], default=88.0)
    multiplier = np.select([partner == "FastLogistics", partner == "ExpressCargo"], [1.171, 1.106], default=1.036)
    delivery_cost = base_cost * np.where(is_q3, multiplier, 1.0) + rng.normal(0, 1.5, n_orders)
    gross = rng.uniform(80, 480, n_orders)
    discount = gross * np.where(is_q3, rng.uniform(0.04, 0.09, n_orders), rng.uniform(0.01, 0.04, n_orders))
    net = gross - discount
    orders = pd.DataFrame({
        "order_id": [f"ORD-{i:06d}" for i in range(1, n_orders + 1)],
        "customer_id": customers.iloc[customer_idx]["customer_id"].to_numpy(),
        "order_date": dates.strftime("%Y-%m-%d"),
        "order_status": np.where(rng.random(n_orders) < 0.95, "Delivered", "Returned"),
        "payment_method": rng.choice(["Credit Card", "UPI", "Net Banking", "COD"], n_orders),
        "shipping_partner": partner,
        "gross_amount": gross.round(2),
        "discount_amount": discount.round(2),
        "net_amount": net.round(2),
        "delivery_fee": np.where(net > 80, 0.0, 5.0),
        "delivery_cost": delivery_cost.round(2),
    })
    orders.to_csv(os.path.join(output_dir, "orders.csv"), index=False)

    item_count = n_orders * 2
    item_order = np.repeat(orders["order_id"].to_numpy(), 2)
    product_idx = rng.integers(0, len(products), item_count)
    qty = rng.integers(1, 3, item_count)
    unit_price = products.iloc[product_idx]["unit_price"].to_numpy()
    unit_cogs = products.iloc[product_idx]["unit_cost"].to_numpy()
    items = pd.DataFrame({
        "order_item_id": [f"ITEM-{i:07d}" for i in range(1, item_count + 1)],
        "order_id": item_order,
        "product_id": products.iloc[product_idx]["product_id"].to_numpy(),
        "quantity": qty,
        "unit_price": unit_price,
        "unit_cogs": unit_cogs,
        "item_total": (unit_price * qty).round(2),
    })
    items.to_csv(os.path.join(output_dir, "order_items.csv"), index=False)

    day_index = pd.date_range("2024-04-01", "2024-09-30", freq="D")
    marketing_rows = []
    expense_rows = []
    for day in day_index:
        q3 = day.month >= 7
        for channel, base in [("Paid Social", 4500), ("Google Ads", 3200), ("Affiliate", 1450), ("Email Marketing", 900)]:
            spend = base * (1.08 if q3 and channel == "Paid Social" else 1.0) * rng.uniform(0.95, 1.05)
            attributed_orders = max(1, int(spend / ({"Paid Social": 98.5, "Google Ads": 61, "Affiliate": 45, "Email Marketing": 18}[channel])))
            marketing_rows.append({"spend_id": f"MKT-{len(marketing_rows)+1:05d}", "spend_date": day.strftime("%Y-%m-%d"), "channel": channel, "campaign": "NovaMart Performance", "spend_amount": round(spend, 2), "impressions": int(spend * 75), "clicks": int(spend * 3), "attributed_orders": attributed_orders, "attributed_revenue": round(attributed_orders * 480, 2)})
        for category, amount in [("Warehousing & Fulfillment", 3500), ("Technology & Hosting", 2200), ("General & Admin", 1850)]:
            expense_rows.append({"expense_id": f"EXP-{len(expense_rows)+1:05d}", "expense_date": day.strftime("%Y-%m-%d"), "category": category, "department": category.split(" & ")[0], "description": "NovaMart operating expense", "amount": round(amount * rng.uniform(0.97, 1.03), 2)})

    pd.DataFrame(marketing_rows).to_csv(os.path.join(output_dir, "marketing_spend.csv"), index=False)
    pd.DataFrame(expense_rows).to_csv(os.path.join(output_dir, "expenses.csv"), index=False)

    returned = orders[orders["order_status"] == "Returned"]
    returns = pd.DataFrame({
        "return_id": [f"RET-{i:06d}" for i in range(1, len(returned) + 1)],
        "order_id": returned["order_id"].to_numpy(),
        "return_date": pd.to_datetime(returned["order_date"]) + pd.to_timedelta(rng.integers(3, 11, len(returned)), unit="D"),
        "return_reason": rng.choice(["Wrong Size", "Damaged", "Changed Mind", "Not as Expected"], len(returned)),
        "refund_amount": returned["net_amount"].to_numpy(),
        "reverse_logistics_cost": rng.uniform(8, 18, len(returned)).round(2),
    })
    returns.to_csv(os.path.join(output_dir, "returns.csv"), index=False)
