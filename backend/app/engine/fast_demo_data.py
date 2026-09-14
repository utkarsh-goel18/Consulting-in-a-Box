from __future__ import annotations

import os
import numpy as np
import pandas as pd

DEMO_VERSION = "novamart-v6-coherent-inr"


def generate_fast_demo_datasets(output_dir: str, n_customers: int = 100_000, n_orders: int = 500_000) -> None:
    """Generate a deterministic, internally reconciled NovaMart fixture at enterprise demo scale."""
    os.makedirs(output_dir, exist_ok=True)
    rng = np.random.default_rng(42)

    categories = np.array(["Electronics", "Fashion & Apparel", "Home & Living", "Beauty & Health", "Grocery & Pantry"])
    n_products = 100
    product_ids = np.array([f"PRD-{i:04d}" for i in range(1, n_products + 1)])
    unit_cost = rng.uniform(650, 6500, n_products).round(2)
    unit_price = np.maximum(rng.uniform(1100, 11000, n_products), unit_cost * 1.35).round(2)
    products = pd.DataFrame({
        "product_id": product_ids,
        "sku": [f"SKU-{i:04d}" for i in range(1, n_products + 1)],
        "product_name": [f"NovaMart Product {i}" for i in range(1, n_products + 1)],
        "category": np.tile(categories, n_products // len(categories)),
        "subcategory": [f"Subcategory {i % 10 + 1}" for i in range(n_products)],
        "unit_cost": unit_cost,
        "unit_price": unit_price,
        "supplier_name": [f"Supplier {i % 12 + 1}" for i in range(n_products)],
    })
    products.to_csv(os.path.join(output_dir, "products.csv"), index=False)

    customer_ids = np.arange(1, n_customers + 1)
    regions = np.array(["Tier 1 - West", "Tier 1 - South", "Tier 2 - North", "Tier 2 - Central", "East"])
    segments = np.array(["Consumer", "SMB", "VIP Enterprise"])
    channels = np.array(["Paid Search", "Organic Search", "Paid Social", "Affiliate", "Email Marketing"])
    churn_q2 = (rng.random(n_customers) < 0.080).astype(int)
    churn_q3 = (rng.random(n_customers) < 0.112).astype(int)
    customers = pd.DataFrame({
        "customer_id": [f"CUST-{i:06d}" for i in customer_ids],
        "signup_date": pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, 610, n_customers), unit="D"),
        "customer_name": [f"Customer {i}" for i in customer_ids],
        "email": [f"client_{i}@example.com" for i in customer_ids],
        "region": rng.choice(regions, n_customers, p=[.23, .21, .22, .19, .15]),
        "tier": rng.choice(["Tier 1", "Tier 2"], n_customers, p=[.61, .39]),
        "customer_segment": rng.choice(segments, n_customers, p=[.70, .22, .08]),
        "acquisition_channel": rng.choice(channels, n_customers, p=[.28, .23, .20, .17, .12]),
        "churn_q2_status": churn_q2,
        "churn_q3_status": churn_q3,
        "churn_status": churn_q3,
    })
    customers["signup_date"] = customers["signup_date"].dt.strftime("%Y-%m-%d")
    customers.to_csv(os.path.join(output_dir, "customers.csv"), index=False)

    q2_n = int(n_orders * 0.53)
    q2_dates = pd.Timestamp("2024-04-01") + pd.to_timedelta(rng.integers(0, 91, q2_n), unit="D")
    q3_dates = pd.Timestamp("2024-07-01") + pd.to_timedelta(rng.integers(0, 92, n_orders - q2_n), unit="D")
    dates = np.concatenate([q2_dates.values, q3_dates.values])
    q3_mask = np.arange(n_orders) >= q2_n

    customer_idx = rng.integers(0, n_customers, n_orders)
    partners = np.array(["FastLogistics", "ExpressCargo", "BlueDart"])
    partner = rng.choice(partners, n_orders, p=[.45, .33, .22])
    partner_base = np.select([partner == "FastLogistics", partner == "ExpressCargo"], [180.0, 165.0], default=205.0)
    partner_multiplier = np.select([partner == "FastLogistics", partner == "ExpressCargo"], [1.137, 1.055], default=1.028)
    delivery_cost = np.maximum(partner_base * np.where(q3_mask, partner_multiplier, 1.0) + rng.normal(0, 5, n_orders), 80).round(2)

    item_count = n_orders * 2
    item_order_index = np.repeat(np.arange(n_orders), 2)
    item_product_index = rng.integers(0, n_products, item_count)
    qty = rng.integers(1, 3, item_count)
    item_prices = products.iloc[item_product_index]["unit_price"].to_numpy()
    item_cogs = products.iloc[item_product_index]["unit_cost"].to_numpy()
    item_total = item_prices * qty
    items = pd.DataFrame({
        "order_item_id": [f"ITEM-{i:08d}" for i in range(1, item_count + 1)],
        "order_id": [f"ORD-{i + 1:07d}" for i in item_order_index],
        "product_id": products.iloc[item_product_index]["product_id"].to_numpy(),
        "quantity": qty,
        "unit_price": item_prices,
        "unit_cogs": item_cogs,
        "item_total": item_total.round(2),
    })
    gross_by_order = pd.Series(item_total).groupby(item_order_index).sum().to_numpy()
    discount_rate = np.where(q3_mask, rng.uniform(.095, .145, n_orders), rng.uniform(.055, .090, n_orders))
    discount_amount = gross_by_order * discount_rate
    net_amount = np.maximum(gross_by_order - discount_amount, 100).round(2)
    status = np.where(rng.random(n_orders) < np.where(q3_mask, .91, .955), "Delivered", "Returned")
    orders = pd.DataFrame({
        "order_id": [f"ORD-{i:07d}" for i in range(1, n_orders + 1)],
        "customer_id": customers.iloc[customer_idx]["customer_id"].to_numpy(),
        "order_date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
        "order_status": status,
        "payment_method": rng.choice(["Credit Card", "UPI", "Net Banking", "COD"], n_orders, p=[.37, .38, .12, .13]),
        "shipping_partner": partner,
        "gross_amount": gross_by_order.round(2),
        "discount_amount": discount_amount.round(2),
        "net_amount": net_amount,
        "delivery_fee": np.where(net_amount > 2200, 0.0, 85.0),
        "delivery_cost": delivery_cost,
    })
    orders.to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    items.to_csv(os.path.join(output_dir, "order_items.csv"), index=False)

    day_index = pd.date_range("2024-04-01", "2024-09-30", freq="D")
    channel_base = {"Paid Social": 190_000, "Google Ads": 145_000, "Affiliate": 78_000, "Email Marketing": 42_000}
    channel_cac = {"Paid Social": 1850, "Google Ads": 1150, "Affiliate": 820, "Email Marketing": 410}
    roas_base = {"Paid Social": 2.4, "Google Ads": 3.5, "Affiliate": 4.2, "Email Marketing": 5.1}
    marketing_rows, expense_rows = [], []
    mkt_id = exp_id = 1
    for day in day_index:
        q3 = day.month >= 7
        for channel, monthly_base in channel_base.items():
            spend = monthly_base / 30 * rng.uniform(.94, 1.06)
            if q3 and channel == "Paid Social":
                spend *= 1.12
            effective_cac = channel_cac[channel] * (1.38 if q3 and channel == "Paid Social" else 1)
            attributed_orders = max(1, int(spend / effective_cac))
            roas = roas_base[channel] * (.74 if q3 and channel == "Paid Social" else 1)
            marketing_rows.append({"spend_id": f"MKT-{mkt_id:06d}", "spend_date": day.strftime("%Y-%m-%d"), "channel": channel, "campaign": "NovaMart Performance", "spend_amount": round(spend, 2), "impressions": int(spend * 70), "clicks": int(spend * 2.8), "attributed_orders": attributed_orders, "attributed_revenue": round(spend * roas, 2)})
            mkt_id += 1
        for category, monthly_base in [("Warehousing & Fulfillment", 105_000), ("Technology & Hosting", 66_000), ("General & Admin", 54_000)]:
            amount = monthly_base / 30 * rng.uniform(.96, 1.04)
            if q3 and category == "Warehousing & Fulfillment":
                amount *= 1.10
            expense_rows.append({"expense_id": f"EXP-{exp_id:06d}", "expense_date": day.strftime("%Y-%m-%d"), "category": category, "department": category.split(" & ")[0], "description": "NovaMart operating expense", "amount": round(amount, 2)})
            exp_id += 1
    pd.DataFrame(marketing_rows).to_csv(os.path.join(output_dir, "marketing_spend.csv"), index=False)
    pd.DataFrame(expense_rows).to_csv(os.path.join(output_dir, "expenses.csv"), index=False)

    returned = orders[orders["order_status"] == "Returned"].copy()
    if not returned.empty:
        return_dates = pd.to_datetime(returned["order_date"]).to_numpy() + rng.integers(3, 11, len(returned)).astype("timedelta64[D]")
        return_dates = np.minimum(return_dates, np.datetime64("2024-09-30"))
    else:
        return_dates = np.array([], dtype="datetime64[ns]")
    returns = pd.DataFrame({
        "return_id": [f"RET-{i:07d}" for i in range(1, len(returned) + 1)],
        "order_id": returned["order_id"].to_numpy(),
        "return_date": return_dates,
        "return_reason": rng.choice(["Wrong Size", "Damaged", "Changed Mind", "Not as Expected"], len(returned), p=[.31, .19, .28, .22]),
        "refund_amount": returned["net_amount"].to_numpy(),
        "reverse_logistics_cost": rng.uniform(280, 520, len(returned)).round(2),
    })
    returns.to_csv(os.path.join(output_dir, "returns.csv"), index=False)

    with open(os.path.join(output_dir, ".novamart_demo_version"), "w", encoding="utf-8") as handle:
        handle.write(DEMO_VERSION)
