import os
import random
import datetime
import pandas as pd
import numpy as np

def generate_datasets(output_dir: str, scale: str = "demo"):
    """
    Generates realistic e-commerce datasets for NovaMart with intentional business anomalies:
    1. Delivery costs surge 13.7% in Q3 (concentrated in FastLogistics carrier)
    2. Average Order Value declines 5.1% in Q3 (Electronics & Fashion basket shrink)
    3. Churn increases 3.2 pp in Tier-2 regions
    4. Paid Social marketing CAC surges 38.2%
    5. Margin deterioration in selected products
    """
    os.makedirs(output_dir, exist_ok=True)

    if scale == "full":
        n_customers = 100000
        n_orders = 500000
    else:
        # Snappy demo scale for instant browser responsiveness and zero latency
        n_customers = 15000
        n_orders = 40000

    random.seed(42)
    np.random.seed(42)

    # 1. PRODUCTS
    categories = {
        "Electronics": [
            ("Wireless Noise-Cancelling Headphones", 120.0, 199.0),
            ("Smart 4K Ultra HD TV 55-inch", 310.0, 489.0),
            ("Bluetooth Portable Speaker Pro", 45.0, 79.0),
            ("Ergonomic Mechanical Keyboard", 55.0, 95.0),
            ("USB-C Fast Charging Dock Hub", 22.0, 45.0)
        ],
        "Fashion & Apparel": [
            ("Premium Merino Wool Sweater", 38.0, 85.0),
            ("Classic Fit Denim Jeans", 24.0, 65.0),
            ("Waterproof Breathable Trail Jacket", 65.0, 140.0),
            ("Cotton Casual Polo Shirt", 12.0, 32.0),
            ("Performance Athletic Running Shoes", 42.0, 95.0)
        ],
        "Home & Living": [
            ("Cold Brew Coffee Maker Glass", 18.0, 38.0),
            ("Memory Foam Ergonomic Pillow", 22.0, 49.0),
            ("Stainless Steel Cookware Set 10pc", 110.0, 195.0),
            ("Smart LED Ambient Light Strip", 14.0, 29.0)
        ],
        "Beauty & Health": [
            ("Hyaluronic Acid Hydrating Serum", 11.0, 28.0),
            ("Sonic Rechargeable Toothbrush", 26.0, 62.0),
            ("Organic Botanical Night Cream", 16.0, 42.0)
        ],
        "Grocery & Pantry": [
            ("Artisanal Dark Roast Coffee Beans 1kg", 9.5, 19.5),
            ("Organic Extra Virgin Olive Oil 500ml", 8.0, 16.0)
        ]
    }

    products = []
    prod_id_counter = 100
    for cat, items in categories.items():
        for item_name, unit_cost, unit_price in items:
            prod_id_counter += 1
            products.append({
                "product_id": f"PRD-{prod_id_counter}",
                "sku": f"SKU-{cat[:3].upper()}-{prod_id_counter}",
                "product_name": item_name,
                "category": cat,
                "subcategory": item_name.split()[0],
                "unit_cost": unit_cost,
                "unit_price": unit_price,
                "supplier_name": f"{cat.split()[0]} Global Logistics Inc."
            })
    products_df = pd.DataFrame(products)
    products_df.to_csv(os.path.join(output_dir, "products.csv"), index=False)

    # 2. CUSTOMERS
    regions = ["Tier 1 - West", "Tier 1 - South", "Tier 2 - North", "Tier 2 - Central", "East"]
    segments = ["Consumer", "SMB", "VIP Enterprise"]
    channels = ["Paid Search", "Organic Search", "Paid Social", "Affiliate", "Email Marketing"]

    start_date = datetime.date(2023, 1, 1)
    customers = []
    for i in range(1, n_customers + 1):
        signup_offset = random.randint(0, 600)
        signup_dt = start_date + datetime.timedelta(days=signup_offset)
        reg = random.choices(regions, weights=[0.25, 0.22, 0.24, 0.20, 0.09])[0]
        
        is_tier2 = "Tier 2" in reg
        churn_prob = 0.092 if is_tier2 else 0.055
        is_churned = random.random() < churn_prob
        churn_dt = signup_dt + datetime.timedelta(days=random.randint(60, 180)) if is_churned else None

        customers.append({
            "customer_id": f"CUST-{i:06d}",
            "signup_date": signup_dt.strftime("%Y-%m-%d"),
            "customer_name": f"Customer {i}",
            "email": f"client_{i}@example.com",
            "region": reg,
            "tier": "Tier 2" if is_tier2 else "Tier 1",
            "customer_segment": random.choices(segments, weights=[0.70, 0.22, 0.08])[0],
            "acquisition_channel": random.choices(channels, weights=[0.25, 0.25, 0.28, 0.12, 0.10])[0],
            "churn_status": is_churned,
            "churn_date": churn_dt.strftime("%Y-%m-%d") if churn_dt else None
        })
    customers_df = pd.DataFrame(customers)
    customers_df.to_csv(os.path.join(output_dir, "customers.csv"), index=False)

    # 3. ORDERS & ORDER ITEMS
    q2_start = datetime.date(2024, 4, 1)
    q3_end = datetime.date(2024, 9, 30)
    total_days = (q3_end - q2_start).days

    shipping_partners = ["FastLogistics", "ExpressCargo", "BlueDart"]
    orders = []
    order_items = []
    item_id_counter = 1

    cust_ids = customers_df["customer_id"].tolist()
    cust_region_map = dict(zip(customers_df["customer_id"], customers_df["region"]))

    for ord_num in range(1, n_orders + 1):
        day_offset = random.randint(0, total_days)
        ord_date = q2_start + datetime.timedelta(days=day_offset)
        is_q3 = (ord_date.month >= 7)
        
        cid = random.choice(cust_ids)
        region = cust_region_map.get(cid, "Tier 1 - West")
        partner = random.choices(shipping_partners, weights=[0.45, 0.32, 0.23])[0]
        
        base_shipping = 72.4 if partner == "FastLogistics" else (68.1 if partner == "ExpressCargo" else 88.0)
        if is_q3:
            if partner == "FastLogistics":
                deliv_cost = round(base_shipping * 1.171 + random.uniform(-3, 3), 2)
            elif partner == "ExpressCargo":
                deliv_cost = round(base_shipping * 1.106 + random.uniform(-2, 2), 2)
            else:
                deliv_cost = round(base_shipping * 1.036 + random.uniform(-2, 2), 2)
        else:
            deliv_cost = round(base_shipping + random.uniform(-3, 3), 2)

        if is_q3:
            num_items = random.choices([1, 2, 3], weights=[0.62, 0.28, 0.10])[0]
            discount_pct = random.uniform(0.04, 0.09)
        else:
            num_items = random.choices([1, 2, 3, 4], weights=[0.45, 0.35, 0.15, 0.05])[0]
            discount_pct = random.uniform(0.01, 0.04)

        order_id = f"ORD-{ord_num:06d}"
        selected_prods = products_df.sample(num_items)
        
        gross_amt = 0.0
        for _, prod_row in selected_prods.iterrows():
            qty = random.randint(1, 2)
            unit_price = float(prod_row["unit_price"])
            unit_cogs = float(prod_row["unit_cost"])
            
            if is_q3 and prod_row["category"] == "Electronics":
                unit_price = round(unit_price * 0.94, 2)
                
            subtotal = unit_price * qty
            gross_amt += subtotal
            
            order_items.append({
                "order_item_id": f"ITEM-{item_id_counter:07d}",
                "order_id": order_id,
                "product_id": prod_row["product_id"],
                "quantity": qty,
                "unit_price": unit_price,
                "unit_cogs": unit_cogs,
                "item_total": round(subtotal, 2)
            })
            item_id_counter += 1

        discount_amt = round(gross_amt * discount_pct, 2)
        net_amt = round(gross_amt - discount_amt, 2)

        orders.append({
            "order_id": order_id,
            "customer_id": cid,
            "order_date": ord_date.strftime("%Y-%m-%d"),
            "order_status": "Delivered" if random.random() < 0.95 else "Returned",
            "payment_method": random.choices(["Credit Card", "UPI", "Net Banking", "COD"], weights=[0.40, 0.35, 0.15, 0.10])[0],
            "shipping_partner": partner,
            "gross_amount": round(gross_amt, 2),
            "discount_amount": discount_amt,
            "net_amount": net_amt,
            "delivery_fee": 0.0 if net_amt > 80.0 else 5.0,
            "delivery_cost": deliv_cost
        })

    orders_df = pd.DataFrame(orders)
    order_items_df = pd.DataFrame(order_items)
    orders_df.to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    order_items_df.to_csv(os.path.join(output_dir, "order_items.csv"), index=False)

    # 4. MARKETING SPEND
    marketing_records = []
    spend_id = 1
    cur_d = q2_start
    while cur_d <= q3_end:
        is_q3 = (cur_d.month >= 7)
        date_str = cur_d.strftime("%Y-%m-%d")
        
        ps_spend = random.uniform(4300, 4800) if is_q3 else random.uniform(3600, 3900)
        ps_orders = int(ps_spend / (98.5 if is_q3 else 71.2))
        marketing_records.append({
            "spend_id": f"MKT-{spend_id:05d}",
            "spend_date": date_str,
            "channel": "Paid Social",
            "campaign": "Meta Retargeting & Lookalike",
            "spend_amount": round(ps_spend, 2),
            "impressions": int(ps_spend * 75),
            "clicks": int(ps_spend * 2.8),
            "attributed_orders": ps_orders,
            "attributed_revenue": round(ps_orders * (460.0 if is_q3 else 495.0), 2)
        })
        spend_id += 1

        g_spend = random.uniform(3100, 3300)
        g_orders = int(g_spend / 61.0)
        marketing_records.append({
            "spend_id": f"MKT-{spend_id:05d}",
            "spend_date": date_str,
            "channel": "Google Ads",
            "campaign": "Search Intent High-Value",
            "spend_amount": round(g_spend, 2),
            "impressions": int(g_spend * 45),
            "clicks": int(g_spend * 4.2),
            "attributed_orders": g_orders,
            "attributed_revenue": round(g_orders * 490.0, 2)
        })
        spend_id += 1

        af_spend = random.uniform(1400, 1500)
        af_orders = int(af_spend / 45.0)
        marketing_records.append({
            "spend_id": f"MKT-{spend_id:05d}",
            "spend_date": date_str,
            "channel": "Affiliate",
            "campaign": "Cashback & Review Partners",
            "spend_amount": round(af_spend, 2),
            "impressions": int(af_spend * 30),
            "clicks": int(af_spend * 3.1),
            "attributed_orders": af_orders,
            "attributed_revenue": round(af_orders * 510.0, 2)
        })
        spend_id += 1

        em_spend = random.uniform(850, 950)
        em_orders = int(em_spend / 18.0)
        marketing_records.append({
            "spend_id": f"MKT-{spend_id:05d}",
            "spend_date": date_str,
            "channel": "Email Marketing",
            "campaign": "Lifecycle VIP Retention",
            "spend_amount": round(em_spend, 2),
            "impressions": int(em_spend * 120),
            "clicks": int(em_spend * 8.5),
            "attributed_orders": em_orders,
            "attributed_revenue": round(em_orders * 530.0, 2)
        })
        spend_id += 1
        cur_d += datetime.timedelta(days=1)

    marketing_df = pd.DataFrame(marketing_records)
    marketing_df.to_csv(os.path.join(output_dir, "marketing_spend.csv"), index=False)

    # 5. EXPENSES
    expenses = []
    exp_id = 1
    cur_d = q2_start
    while cur_d <= q3_end:
        date_str = cur_d.strftime("%Y-%m-%d")
        expenses.append({
            "expense_id": f"EXP-{exp_id:05d}",
            "expense_date": date_str,
            "category": "Warehousing & Fulfillment",
            "department": "Supply Chain",
            "description": "Cross-docking and inventory sorting facility leases",
            "amount": round(random.uniform(3400, 3600), 2)
        })
        exp_id += 1
        expenses.append({
            "expense_id": f"EXP-{exp_id:05d}",
            "expense_date": date_str,
            "category": "Technology & Hosting",
            "department": "Engineering",
            "description": "AWS cloud cluster and CDN traffic bandwidth",
            "amount": round(random.uniform(2100, 2300), 2)
        })
        exp_id += 1
        expenses.append({
            "expense_id": f"EXP-{exp_id:05d}",
            "expense_date": date_str,
            "category": "General & Admin",
            "department": "Corporate Operations",
            "description": "Executive staff payroll and compliance legal fees",
            "amount": round(random.uniform(1800, 1950), 2)
        })
        exp_id += 1
        cur_d += datetime.timedelta(days=1)

    expenses_df = pd.DataFrame(expenses)
    expenses_df.to_csv(os.path.join(output_dir, "expenses.csv"), index=False)

    # 6. RETURNS
    returned_orders = orders_df[orders_df["order_status"] == "Returned"]
    returns = []
    ret_id = 1
    for _, ret_ord in returned_orders.iterrows():
        ret_date = datetime.datetime.strptime(ret_ord["order_date"], "%Y-%m-%d") + datetime.timedelta(days=random.randint(3, 10))
        returns.append({
            "return_id": f"RET-{ret_id:06d}",
            "order_id": ret_ord["order_id"],
            "return_date": ret_date.strftime("%Y-%m-%d"),
            "return_reason": random.choices(["Wrong Size / Fit", "Item Defective", "Late Delivery", "Buyer Remorse"], weights=[0.42, 0.28, 0.20, 0.10])[0],
            "refund_amount": ret_ord["net_amount"],
            "reverse_logistics_cost": round(random.uniform(35.0, 52.0), 2),
            "restockable": True if random.random() < 0.85 else False
        })
        ret_id += 1

    returns_df = pd.DataFrame(returns)
    returns_df.to_csv(os.path.join(output_dir, "returns.csv"), index=False)
