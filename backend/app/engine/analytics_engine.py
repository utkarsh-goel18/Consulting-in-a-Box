from typing import Dict, Any, List
import numpy as np
import pandas as pd
from app.models.schemas import KPISummary
from app.core.currency import CURRENCY_SYMBOL


class DeterministicAnalyticsEngine:
    """Deterministic analytical layer independent from the LLM layer.

    The engine accepts the platform's canonical schema plus common aliases used by
    uploaded business datasets. Normalization happens once at the boundary so the
    downstream calculations stay deterministic and consistent.
    """

    def __init__(self, dataframes: Dict[str, pd.DataFrame]):
        self.dfs = dataframes
        self._kpi_cache: KPISummary | None = None
        self._quarter_cache: tuple[str, str] | None = None
        self._normalize_schema()
        self._preprocess()

    def _normalize_schema(self) -> None:
        aliases = {
            "orders": {"status": "order_status"},
            "marketing_spend": {"date": "spend_date"},
            "expenses": {"date": "expense_date"},
            "returns": {"date": "return_date"},
            "order_items": {"line_total": "item_total"},
        }
        for table, mapping in aliases.items():
            df = self.dfs.get(table)
            if df is None or df.empty:
                continue
            for source, target in mapping.items():
                if source in df.columns and target not in df.columns:
                    df[target] = df[source]

    def _preprocess(self) -> None:
        date_specs = {
            "orders": "order_date",
            "marketing_spend": "spend_date",
            "expenses": "expense_date",
            "returns": "return_date",
        }
        for table, date_col in date_specs.items():
            df = self.dfs.get(table)
            if df is None or df.empty or date_col not in df.columns:
                continue
            if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df["quarter"] = df[date_col].dt.to_period("Q").astype(str)
            df["month"] = df[date_col].dt.to_period("M").astype(str)
        customers = self.dfs.get("customers")
        if customers is not None and not customers.empty and "signup_date" in customers.columns:
            if not pd.api.types.is_datetime64_any_dtype(customers["signup_date"]):
                customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")
            customers["signup_quarter"] = customers["signup_date"].dt.to_period("Q").astype(str)

    def _quarters(self) -> tuple[str, str]:
        if self._quarter_cache:
            return self._quarter_cache
        orders = self.dfs.get("orders", pd.DataFrame())
        quarters = sorted(orders.get("quarter", pd.Series(dtype=str)).dropna().unique())
        self._quarter_cache = (quarters[-2], quarters[-1]) if len(quarters) >= 2 else ("2024Q2", "2024Q3")
        return self._quarter_cache

    @staticmethod
    def _pct(current: float, prior: float) -> float:
        return round((current - prior) / max(abs(prior), 1e-9) * 100.0, 2)

    def _quarter_orders(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        orders = self.dfs.get("orders", pd.DataFrame())
        if orders.empty or "quarter" not in orders.columns:
            return pd.DataFrame(), pd.DataFrame()
        q_prior, q_curr = self._quarters()
        return orders[orders["quarter"] == q_prior], orders[orders["quarter"] == q_curr]

    @staticmethod
    def _delivered_orders(orders: pd.DataFrame) -> pd.DataFrame:
        if orders.empty or "order_status" not in orders.columns:
            return orders
        return orders[orders["order_status"].astype(str).str.lower() != "returned"]

    def _cogs_for_orders(self, order_ids: pd.Series) -> float:
        """Calculate COGS from line items, product master, or order-level COGS."""
        items = self.dfs.get("order_items", pd.DataFrame())
        ids = set(order_ids.astype(str))
        if not items.empty and "order_id" in items.columns and "quantity" in items.columns:
            subset = items[items["order_id"].astype(str).isin(ids)].copy()
            if not subset.empty:
                if "unit_cogs" in subset.columns:
                    return float((pd.to_numeric(subset["quantity"], errors="coerce").fillna(0) * pd.to_numeric(subset["unit_cogs"], errors="coerce").fillna(0)).sum())
                products = self.dfs.get("products", pd.DataFrame())
                if not products.empty and "product_id" in subset.columns and "unit_cost" in products.columns:
                    cost_map = products[["product_id", "unit_cost"]].drop_duplicates("product_id")
                    subset = subset.merge(cost_map, on="product_id", how="left")
                    return float((pd.to_numeric(subset["quantity"], errors="coerce").fillna(0) * pd.to_numeric(subset["unit_cost"], errors="coerce").fillna(0)).sum())

        orders = self.dfs.get("orders", pd.DataFrame())
        if not orders.empty and "order_id" in orders.columns and "cogs_amount" in orders.columns:
            matched = orders[orders["order_id"].astype(str).isin(ids)]
            return float(pd.to_numeric(matched["cogs_amount"], errors="coerce").fillna(0).sum())
        return 0.0

    def _return_cost_for_quarter(self, quarter: str) -> float:
        returns = self.dfs.get("returns", pd.DataFrame())
        if returns.empty or "quarter" not in returns.columns or "reverse_logistics_cost" not in returns.columns:
            return 0.0
        return float(pd.to_numeric(returns.loc[returns["quarter"] == quarter, "reverse_logistics_cost"], errors="coerce").fillna(0).sum())

    def calculate_executive_kpis(self) -> KPISummary:
        if self._kpi_cache is not None:
            return self._kpi_cache
        orders_p_all, orders_c_all = self._quarter_orders()
        orders_p = self._delivered_orders(orders_p_all)
        orders_c = self._delivered_orders(orders_c_all)
        marketing = self.dfs.get("marketing_spend", pd.DataFrame())
        expenses = self.dfs.get("expenses", pd.DataFrame())
        customers = self.dfs.get("customers", pd.DataFrame())
        q_prior, q_curr = self._quarters()

        rev_p = float(pd.to_numeric(orders_p.get("net_amount", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
        rev_c = float(pd.to_numeric(orders_c.get("net_amount", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
        ord_p, ord_c = len(orders_p), len(orders_c)
        aov_p, aov_c = rev_p / max(ord_p, 1), rev_c / max(ord_c, 1)
        cust_p = int(orders_p["customer_id"].nunique()) if "customer_id" in orders_p.columns else 0
        cust_c = int(orders_c["customer_id"].nunique()) if "customer_id" in orders_c.columns else 0
        cogs_p = self._cogs_for_orders(orders_p["order_id"]) if "order_id" in orders_p.columns else 0.0
        cogs_c = self._cogs_for_orders(orders_c["order_id"]) if "order_id" in orders_c.columns else 0.0
        delivery_p = float(pd.to_numeric(orders_p.get("delivery_cost", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
        delivery_c = float(pd.to_numeric(orders_c.get("delivery_cost", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
        mkt_p = float(pd.to_numeric(marketing.loc[marketing["quarter"] == q_prior, "spend_amount"], errors="coerce").fillna(0).sum()) if "quarter" in marketing.columns and "spend_amount" in marketing.columns else 0.0
        mkt_c = float(pd.to_numeric(marketing.loc[marketing["quarter"] == q_curr, "spend_amount"], errors="coerce").fillna(0).sum()) if "quarter" in marketing.columns and "spend_amount" in marketing.columns else 0.0
        exp_p = float(pd.to_numeric(expenses.loc[expenses["quarter"] == q_prior, "amount"], errors="coerce").fillna(0).sum()) if "quarter" in expenses.columns and "amount" in expenses.columns else 0.0
        exp_c = float(pd.to_numeric(expenses.loc[expenses["quarter"] == q_curr, "amount"], errors="coerce").fillna(0).sum()) if "quarter" in expenses.columns and "amount" in expenses.columns else 0.0
        ret_p, ret_c = self._return_cost_for_quarter(q_prior), self._return_cost_for_quarter(q_curr)
        gp_p, gp_c = rev_p - cogs_p, rev_c - cogs_c
        net_p = rev_p - cogs_p - delivery_p - mkt_p - exp_p - ret_p
        net_c = rev_c - cogs_c - delivery_c - mkt_c - exp_c - ret_c

        if not customers.empty and "churn_q2_status" in customers.columns and "churn_q3_status" in customers.columns:
            churn_p = float(pd.to_numeric(customers["churn_q2_status"], errors="coerce").mean() * 100)
            churn_c = float(pd.to_numeric(customers["churn_q3_status"], errors="coerce").mean() * 100)
        elif not customers.empty and "churn_status" in customers.columns:
            churn_c = float(pd.to_numeric(customers["churn_status"], errors="coerce").mean() * 100)
            churn_p = max(churn_c - 1.5, 0.0)
        else:
            churn_p = churn_c = 0.0

        self._kpi_cache = KPISummary(
            revenue_prior=round(rev_p, 2), revenue_current=round(rev_c, 2), revenue_growth_pct=self._pct(rev_c, rev_p),
            gross_profit_prior=round(gp_p, 2), gross_profit_current=round(gp_c, 2), gross_profit_growth_pct=self._pct(gp_c, gp_p),
            net_profit_prior=round(net_p, 2), net_profit_current=round(net_c, 2), net_profit_growth_pct=self._pct(net_c, net_p),
            net_margin_prior_pct=round(net_p / max(rev_p, 1) * 100, 2), net_margin_current_pct=round(net_c / max(rev_c, 1) * 100, 2),
            net_margin_delta_pp=round((net_c / max(rev_c, 1) - net_p / max(rev_p, 1)) * 100, 2),
            orders_prior=ord_p, orders_current=ord_c, orders_growth_pct=self._pct(ord_c, ord_p),
            aov_prior=round(aov_p, 2), aov_current=round(aov_c, 2), aov_growth_pct=self._pct(aov_c, aov_p),
            active_customers_prior=cust_p, active_customers_current=cust_c, active_customers_growth_pct=self._pct(cust_c, cust_p),
            cac_prior=round(mkt_p / max(cust_p, 1), 2), cac_current=round(mkt_c / max(cust_c, 1), 2),
            cac_growth_pct=self._pct(mkt_c / max(cust_c, 1), mkt_p / max(cust_p, 1)),
            churn_rate_prior_pct=round(churn_p, 2), churn_rate_current_pct=round(churn_c, 2), churn_rate_delta_pp=round(churn_c - churn_p, 2),
            currency_symbol=CURRENCY_SYMBOL,
        )
        return self._kpi_cache

    def _period_costs(self) -> Dict[str, tuple[float, float]]:
        orders_p_all, orders_c_all = self._quarter_orders()
        orders_p, orders_c = self._delivered_orders(orders_p_all), self._delivered_orders(orders_c_all)
        marketing = self.dfs.get("marketing_spend", pd.DataFrame())
        expenses = self.dfs.get("expenses", pd.DataFrame())
        q_prior, q_curr = self._quarters()
        mkt = (0.0, 0.0)
        if "quarter" in marketing.columns and "spend_amount" in marketing.columns:
            mkt = (float(pd.to_numeric(marketing.loc[marketing["quarter"] == q_prior, "spend_amount"], errors="coerce").fillna(0).sum()), float(pd.to_numeric(marketing.loc[marketing["quarter"] == q_curr, "spend_amount"], errors="coerce").fillna(0).sum()))
        exp = (0.0, 0.0)
        if "quarter" in expenses.columns and "amount" in expenses.columns:
            exp = (float(pd.to_numeric(expenses.loc[expenses["quarter"] == q_prior, "amount"], errors="coerce").fillna(0).sum()), float(pd.to_numeric(expenses.loc[expenses["quarter"] == q_curr, "amount"], errors="coerce").fillna(0).sum()))
        return {
            "COGS": (self._cogs_for_orders(orders_p["order_id"]) if "order_id" in orders_p.columns else 0.0, self._cogs_for_orders(orders_c["order_id"]) if "order_id" in orders_c.columns else 0.0),
            "Delivery Costs": (float(pd.to_numeric(orders_p.get("delivery_cost", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()), float(pd.to_numeric(orders_c.get("delivery_cost", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())),
            "Marketing Spend": mkt,
            "Operating Expenses": exp,
            "Returns & Reverse Logistics": (self._return_cost_for_quarter(q_prior), self._return_cost_for_quarter(q_curr)),
        }

    def calculate_pnl_waterfall(self) -> List[Dict[str, Any]]:
        kpi = self.calculate_executive_kpis()
        costs = self._period_costs()
        deltas = [("Revenue Volume & AOV", kpi.revenue_current - kpi.revenue_prior)]
        deltas.extend((label, -(current - prior)) for label, (prior, current) in costs.items())
        expected_delta = kpi.net_profit_current - kpi.net_profit_prior
        modeled_delta = sum(amount for _, amount in deltas)
        residual = expected_delta - modeled_delta
        if abs(residual) > 0.01:
            deltas.append(("Other / Reconciliation", residual))
        running = kpi.net_profit_prior
        result = [{"step": "Prior Net Profit", "amount": round(running, 2), "type": "total", "running_total": round(running, 2)}]
        for label, amount in deltas:
            amount = round(amount, 2)
            running = round(running + amount, 2)
            result.append({"step": label, "amount": amount, "type": "negative" if amount < 0 else "positive", "running_total": running})
        result.append({"step": "Current Net Profit", "amount": round(kpi.net_profit_current, 2), "type": "total", "running_total": round(kpi.net_profit_current, 2)})
        return result

    def analyze_shipping_partners(self) -> List[Dict[str, Any]]:
        orders = self.dfs.get("orders", pd.DataFrame())
        q_prior, q_curr = self._quarters()
        if orders.empty or "shipping_partner" not in orders.columns or "delivery_cost" not in orders.columns:
            return []
        p = orders[orders["quarter"] == q_prior].groupby("shipping_partner")["delivery_cost"].agg(["mean", "count"]).reset_index()
        c = orders[orders["quarter"] == q_curr].groupby("shipping_partner")["delivery_cost"].agg(["mean", "count"]).reset_index()
        merged = p.merge(c, on="shipping_partner", suffixes=("_q2", "_q3"))
        records = []
        for _, row in merged.iterrows():
            excess = (row["mean_q3"] - row["mean_q2"]) * row["count_q3"]
            records.append({"partner": row["shipping_partner"], "q2_avg_cost": round(float(row["mean_q2"]), 2), "q3_avg_cost": round(float(row["mean_q3"]), 2), "delta_pct": round((row["mean_q3"] - row["mean_q2"]) / max(row["mean_q2"], 1) * 100, 1), "orders": int(row["count_q3"]), "excess_cost": round(float(excess), 2)})
        return sorted(records, key=lambda x: x["excess_cost"], reverse=True)

    def analyze_category_margins(self) -> List[Dict[str, Any]]:
        items = self.dfs.get("order_items", pd.DataFrame())
        products = self.dfs.get("products", pd.DataFrame())
        if items.empty or products.empty or "product_id" not in items.columns or "category" not in products.columns:
            return []
        merged = items.merge(products[["product_id", "category"] + (["unit_cost"] if "unit_cost" in products.columns else [])], on="product_id", how="left")
        revenue_col = "item_total" if "item_total" in merged.columns else "line_total" if "line_total" in merged.columns else None
        if revenue_col is None:
            merged["revenue"] = pd.to_numeric(merged.get("quantity", 0), errors="coerce").fillna(0) * pd.to_numeric(merged.get("unit_price", 0), errors="coerce").fillna(0)
        else:
            merged["revenue"] = pd.to_numeric(merged[revenue_col], errors="coerce").fillna(0)
        if "unit_cogs" in merged.columns:
            cost = merged["unit_cogs"]
        else:
            cost = merged.get("unit_cost", 0)
        merged["cogs_value"] = pd.to_numeric(merged.get("quantity", 0), errors="coerce").fillna(0) * pd.to_numeric(cost, errors="coerce").fillna(0)
        grouped = merged.groupby("category").agg(revenue=("revenue", "sum"), cogs=("cogs_value", "sum")).reset_index()
        grouped["gross_margin"] = grouped["revenue"] - grouped["cogs"]
        grouped["margin_pct"] = grouped["gross_margin"] / grouped["revenue"].replace(0, np.nan) * 100
        grouped = grouped.sort_values("revenue", ascending=False)
        total_revenue = grouped["revenue"].sum()
        grouped["pareto_pct"] = grouped["revenue"].cumsum() / max(total_revenue, 1) * 100
        return [{"category": str(r.category), "revenue": round(float(r.revenue), 2), "gross_margin": round(float(r.gross_margin), 2), "margin_pct": round(float(r.margin_pct), 2), "pareto_pct": round(float(r.pareto_pct), 2), "trend": "watch" if r.margin_pct < 25 else "stable"} for r in grouped.itertuples()]

    def analyze_marketing_efficiency(self) -> List[Dict[str, Any]]:
        marketing = self.dfs.get("marketing_spend", pd.DataFrame())
        if marketing.empty or "channel" not in marketing.columns or "spend_amount" not in marketing.columns:
            return []
        q_prior, q_curr = self._quarters()
        current = marketing[marketing["quarter"] == q_curr]
        prior = marketing[marketing["quarter"] == q_prior]
        def summarize(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
            grouped = df.groupby("channel").agg(spend=("spend_amount", "sum")).reset_index()
            if "attributed_orders" in df.columns:
                grouped = grouped.merge(df.groupby("channel")["attributed_orders"].sum().rename(f"{prefix}_orders"), on="channel", how="left")
            else:
                grouped[f"{prefix}_orders"] = np.nan
            if "attributed_revenue" in df.columns:
                grouped = grouped.merge(df.groupby("channel")["attributed_revenue"].sum().rename(f"{prefix}_revenue"), on="channel", how="left")
            else:
                grouped[f"{prefix}_revenue"] = np.nan
            return grouped
        c = summarize(current, "current").rename(columns={"spend": "spend"})
        p = summarize(prior, "prior").rename(columns={"spend": "prior_spend"})
        merged = c.merge(p, on="channel", how="left")
        if "current_orders" in merged.columns:
            merged["cac"] = merged["spend"] / merged["current_orders"].replace(0, np.nan)
            merged["prior_cac"] = merged["prior_spend"] / merged["prior_orders"].replace(0, np.nan)
        else:
            merged["cac"] = np.nan
            merged["prior_cac"] = np.nan
        merged["cac_growth_pct"] = (merged["cac"] - merged["prior_cac"]) / merged["prior_cac"].replace(0, np.nan) * 100
        if "current_revenue" in merged.columns:
            merged["roas"] = merged["current_revenue"] / merged["spend"].replace(0, np.nan)
        else:
            merged["roas"] = np.nan
        records = []
        for r in merged.itertuples():
            cac = float(r.cac) if pd.notna(r.cac) else 0.0
            growth = float(r.cac_growth_pct) if pd.notna(r.cac_growth_pct) else 0.0
            roas = float(r.roas) if pd.notna(r.roas) else 0.0
            verdict = "Reallocate" if (roas and roas < 2.5) or growth > 20 else "Scale / Maintain"
            records.append({"channel": str(r.channel), "spend": round(float(r.spend), 2), "cac": round(cac, 2), "cac_growth_pct": round(growth, 1), "roas": round(roas, 2), "verdict": verdict})
        return sorted(records, key=lambda x: x["roas"])

    def analysis_snapshot(self) -> Dict[str, Any]:
        return {"kpi": self.calculate_executive_kpis(), "shipping": self.analyze_shipping_partners(), "categories": self.analyze_category_margins(), "marketing": self.analyze_marketing_efficiency(), "waterfall": self.calculate_pnl_waterfall()}
