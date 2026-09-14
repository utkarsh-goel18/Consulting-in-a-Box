import os
import numpy as np
import pandas as pd


DEMO_VERSION = "novamart-v3-inr"


def generate_fast_demo_datasets(
    output_dir: str,
    n_customers: int = 100_000,
    n_orders: int = 500_000,
) -> None:
    """Generate the full NovaMart demo fixture with vectorized pandas/numpy operations.

    The dataset is deliberately synthetic but internally coherent. Q3 contains
    engineered business conditions that arise from the records themselves:
    lower order volume/AOV, higher delivery inflation, weaker paid-social
    efficiency and a higher return rate. No dashboard metric depends on a
    hard-coded narrative value.
    """
    os.makedirs(output_dir, exist_ok=True)
    rng = np.random.default_rng(42)

    categories = np.array([
        "Electronics", "Fashion & Apparel", "Home & Living",
        "Beauty & Health", "Grocery & Pantry"
    ])
    products = pd.DataFrame({
        "product_id": [f"PRD-{i:04d}" for i in range(1, 101)],
        "sku": [f"SKU-{i:04d}" for i in range(1, 101)],
        "product_name": [f"NovaMart Product {i}" for i in range(1, 101)],
        "category": np.tile(categories, 20),
        "subcategory": [f"Subcategory {i % 10 + 1}" for i in range(100)],
        "unit_cost": rng.uniform(650, 6500, 100).round(2),
        "unit_price": rng.uniform(1100, 11000, 100).round(2),
        "supplier_name": [f"Supplier {i % 12 + 1}" for i in range(100)],
    })
    # Keep every product economically sensible.
    products["unit_price"] = np.maximum(products["unit_price"], products["unit_cost"] * 1.35).round(2)
    products.to_csv(os.path.join(output_dir, "products.csv"), index=False)

    customer_ids = np.arange(1, n_customers + 1)
    regions = np.array(["Tier 1 - West", "Tier 1 - South", "Tier 2 - North", "Tier 2 - Central", "East"])
    segments = np.array(["Consumer", "SMB", "VIP Enterprise"])
    channels = np.array(["Paid Search", "Organic Search", "Paid Social", "Affiliate", "Email Marketing"])
    customers = pd.DataFrame({
        "customer_id": [f"CUST-{i:06d}" for i in customer_ids],
        "signup_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 610, n_customers), unit="D"),
        "customer_name": [f"Customer {i}" for i in customer_ids],
        "email": [f"client_{i}@example.com" for i in customer_ids],
        "region": rng.choice(regions, n_customers, p=[0.23, 0.21, 0.22, 0.19, 0.15]),
        "tier": rng.choice(["Tier 1", "Tier 2"], n_customers, p=[0.61, 0.39]),
        "customer_segment": rng.choice(segments, n_customers, p=[0.70, 0.22, 0.08]),
        "acquisition_channel": rng.choice(channels, n_customers, p=[0.28, 0.23, 0.20, 0.17, 0.12]),
        "churn_status": rng.random(n_customers) < 0.10,
        "churn_date": pd.NaT,
    })
    customers["signup_date"] = customers["signup_date"].dt.strftime("%Y-%m-%d")
    customers.to_csv(os.path.join(output_dir, "customers.csv"), index=False)

    # Exactly two quarters, with a deliberate Q3 slowdown.
    q2_n = int(n_orders * 0.53)
    q3_n = n_orders - q2_n
    q2_dates = pd.Timestamp("2024-04-01") + pd.to_timedelta(rng.integers(0, 91, q2_n), unit="D")
    q3_dates = pd.Timestamp("2024-07-01") + pd.to_timedelta(rng.integers(0, 92, q3_n), unit="D")
    dates = np.concatenate([q2_dates.values, q3_dates.values])
    q3_mask = np.arange(n_orders) >= q2_n

    customer_idx = rng.integers(0, n_customers, n_orders)
    partner = rng.choice(["FastLogistics", "ExpressCargo", "BlueDart"], n_orders, p=[0.45, 0.33, 0.22])
    partner_base = np.select(
        [partner == "FastLogistics", partner == "ExpressCargo"],
        [180.0, 165.0],
        default=205.0,
    )
    partner_q3_multiplier = np.select(
        [partner == "FastLogistics", partner == "ExpressCargo"],
        [1.137, 1.055],
        default=1.028,
    )
    delivery_cost = partner_base * np.where(q3_mask, partner_q3_multiplier, 1.0) + rng.normal(0, 5.0, n_orders)
    delivery_cost = np.maximum(delivery_cost, 80).round(2)

    # Order economics: Q3 has lower baskets and more discounting.
    base_gross = rng.lognormal(mean=np.log(2550), sigma=0.38, size=n_orders)
    base_gross = np.clip(base_gross, 650, 15000)
    discount_rate = np.where(
        q3_mask,
        rng.uniform(0.095, 0.145, n_orders),
        rng.uniform(0.055, 0.090, n_orders),
    )
    gross_amount = base_gross
    discount_amount = gross_amount * discount_rate
    net_amount = np.maximum(gross_amount - discount_amount, 100)
    status = np.where(rng.random(n_orders) < np.where(q3_mask, 0.91, 0.955), "Delivered", "Returned")

    orders = pd.DataFrame({
        "order_id": [f"ORD-{i:07d}" for i in range(1, n_orders + 1)],
        "customer_id": customers.iloc[customer_idx]["customer_id"].to_numpy(),
        "order_date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
        "order_status": status,
        "payment_method": rng.choice(["Credit Card", "UPI", "Net Banking", "COD"], n_orders, p=[0.37, 0.38, 0.12, 0.13]),
        "shipping_partner": partner,
        "gross_amount": gross_amount.round(2),
        "discount_amount": discount_amount.round(2),
        "net_amount": net_amount.round(2),
        "delivery_fee": np.where(net_amount > 2200, 0.0, 85.0),
        "delivery_cost": delivery_cost,
    })
    orders.to_csv(os.path.join(output_dir, "orders.csv"), index=False)

    # Two line items per order. COGS is generated from the same product master,
    # so category margin and P&L calculations remain auditable.
    item_count = n_orders * 2
    item_order = np.repeat(orders["order_id"].to_numpy(), 2)
    product_idx = rng.integers(0, len(products), item_count)
    qty = rng.integers(1, 3, item_count)
    unit_price = products.iloc[product_idx]["unit_price"].to_numpy()
    unit_cogs = products.iloc[product_idx]["unit_cost"].to_numpy()
    items = pd.DataFrame({
        "order_item_id": [f"ITEM-{i:08d}" for i in range(1, item_count + 1)],
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
    channel_base = {
        "Paid Social": 190_000,
        "Google Ads": 145_000,
        "Affiliate": 78_000,
        "Email Marketing": 42_000,
    }
    channel_cac = {"Paid Social": 1_850, "Google Ads": 1_150, "Affiliate": 820, "Email Marketing": 410}

    for day in day_index:
        q3 = day.month >= 7
        for channel, monthly_base in channel_base.items():
            base = monthly_base / 30.0
            if q3 and channel == "Paid Social":
                base *= 1.12
            spend = base * rng.uniform(0.94, 1.06)
            efficiency = channel_cac[channel] * (1.38 if q3 and channel == "Paid Social" else 1.0)
            attributed_orders = max(1, int(spend / efficiency))
            roas = {"Paid Social": 2.4, "Google Ads": 3.5, "Affiliate": 4.2, "Email Marketing": 5.1}[channel]
            if q3 and channel == "Paid Social":
                roas *= 0.74
            marketing_rows.append({
                "spend_id": f"MKT-{len(marketing_rows)+1:06d}",
                "spend_date": day.strftime("%Y-%m-%d"),
                "channel": channel,
                "campaign": "NovaMart Performance",
                "spend_amount": round(spend, 2),
                "impressions": int(spend * 70),
                "clicks": int(spend * 2.8),
                "attributed_orders": attributed_orders,
                "attributed_revenue": round(spend * roas, 2),
            })
        for category, monthly_base in [
            ("Warehousing & Fulfillment", 105_000),
            ("Technology & Hosting", 66_000),
            ("General & Admin", 54_000),
        ]:
            amount = monthly_base / 30.0 * rng.uniform(0.96, 1.04)
            if q3 and category == "Warehousing & Fulfillment":
                amount *= 1.10
            expense_rows.append({
                "expense_id": f"EXP-{len(expense_rows)+1:06d}",
                "expense_date": day.strftime("%Y-%m-%d"),
                "category": category,
                "department": category.split(" & ")[0],
                "description": "NovaMart operating expense",
                "amount": round(amount, 2),
            })

    pd.DataFrame(marketing_rows).to_csv(os.path.join(output_dir, "marketing_spend.csv"), index=False)
    pd.DataFrame(expense_rows).to_csv(os.path.join(output_dir, "expenses.csv"), index=False)

    returned = orders[orders["order_status"] == "Returned"]
    return_dates = pd.to_datetime(returned["order_date"]) + pd.to_timedelta(rng.integers(3, 11, len(returned)), unit="D")
    returns = pd.DataFrame({
        "return_id": [f"RET-{i:07d}" for i in range(1, len(returned) + 1)],
        "order_id": returned["order_id"].to_numpy(),
        "return_date": return_dates,
        "return_reason": rng.choice(["Wrong Size", "Damaged", "Changed Mind", "Not as Expected"], len(returned), p=[0.31, 0.19, 0.28, 0.22]),
        "refund_amount": returned["net_amount"].to_numpy(),
        "reverse_logistics_cost": rng.uniform(280, 520, len(returned)).round(2),
    })
    returns.to_csv(os.path.join(output_dir, "returns.csv"), index=False)

    with open(os.path.join(output_dir, ".novamart_demo_version"), "w", encoding="utf-8") as handle:
        handle.write(DEMO_VERSION)
