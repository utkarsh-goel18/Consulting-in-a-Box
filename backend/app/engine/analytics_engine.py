from typing import Dict, Any, List
import numpy as np
import pandas as pd
from app.models.schemas import KPISummary
from app.core.currency import CURRENCY_SYMBOL


class DeterministicAnalyticsEngine:
    """Deterministic analytical layer independent from the LLM layer."""

    def __init__(self, dataframes: Dict[str, pd.DataFrame]):
        self.dfs = dataframes
        self._kpi_cache: KPISummary | None = None
        self._quarter_cache: tuple[str, str] | None = None
        self._preprocess()

    def _preprocess(self) -> None:
        date_specs = {"orders": "order_date", "marketing_spend": "spend_date", "expenses": "expense_date", "returns": "return_date"}
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
        q_prior, q_curr = self._quarters()
        return orders[orders["quarter"] == q_prior], orders[orders["quarter"] == q_curr]

    @staticmethod
    def _delivered_orders(orders: pd.DataFrame) -> pd.DataFrame:
        if orders.empty or "order_status" not in orders.columns:
            return orders
        return orders[orders["order_status"].astype(str).str.lower() != "returned"]

    def _cogs_for_orders(self, order_ids: pd.Series) -> float:
        items = self.dfs.get("order_items", pd.DataFrame())
        if items.empty:
            return 0.0
        subset = items[items["order_id"].isin(order_ids)]
        return float((subset["quantity"] * subset["unit_cogs"]).sum()) if not subset.empty else 0.0

    def _return_cost_for_quarter(self, quarter: str) -> float:
        """Return P&L cost after refunds are excluded from recognized net sales.

        orders.net_amount contains the sale value even when an order is later returned.
        Recognized revenue therefore uses delivered orders only; the returns line carries
        reverse-logistics cost only. This prevents refund amounts from being subtracted twice.
        """
        returns = self.dfs.get("returns", pd.DataFrame())
        if returns.empty or "quarter" not in returns.columns:
            return 0.0
        return float(returns.loc[returns["quarter"] == quarter, "reverse_logistics_cost"].sum())

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

        # P&L revenue is recognized on delivered orders. Returned-order refund amounts
        # are therefore not deducted again below; only reverse-logistics cost remains.
        rev_p, rev_c = float(orders_p["net_amount"].sum()), float(orders_c["net_amount"].sum())
        ord_p, ord_c = len(orders_p), len(orders_c)
        aov_p, aov_c = rev_p / max(ord_p, 1), rev_c / max(ord_c, 1)
        cust_p, cust_c = int(orders_p["customer_id"].nunique()), int(orders_c["customer_id"].nunique())
        cogs_p, cogs_c = self._cogs_for_orders(orders_p["order_id"]), self._cogs_for_orders(orders_c["order_id"])
        delivery_p, delivery_c = float(orders_p["delivery_cost"].sum()), float(orders_c["delivery_cost"].sum())
        mkt_p = float(marketing.loc[marketing["quarter"] == q_prior, "spend_amount"].sum()) if not marketing.empty else 0.0
        mkt_c = float(marketing.loc[marketing["quarter"] == q_curr, "spend_amount"].sum()) if not marketing.empty else 0.0
        exp_p = float(expenses.loc[expenses["quarter"] == q_prior, "amount"].sum()) if not expenses.empty else 0.0
        exp_c = float(expenses.loc[expenses["quarter"] == q_curr, "amount"].sum()) if not expenses.empty else 0.0
        ret_p = self._return_cost_for_quarter(q_prior)
        ret_c = self._return_cost_for_quarter(q_curr)
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
        orders_p = self._delivered_orders(orders_p_all)
        orders_c = self._delivered_orders(orders_c_all)
        marketing = self.dfs.get("marketing_spend", pd.DataFrame())
        expenses = self.dfs.get("expenses", pd.DataFrame())
        q_prior, q_curr = self._quarters()
        return {
            "COGS": (self._cogs_for_orders(orders_p["order_id"]), self._cogs_for_orders(orders_c["order_id"])),
            "Delivery Costs": (float(orders_p["delivery_cost"].sum()), float(orders_c["delivery_cost"].sum())),
            "Marketing Spend": (float(marketing.loc[marketing["quarter"] == q_prior, "spend_amount"].sum()), float(marketing.loc[marketing["quarter"] == q_curr, "spend_amount"].sum())),
            "Operating Expenses": (float(expenses.loc[expenses["quarter"] == q_prior, "amount"].sum()), float(expenses.loc[expenses["quarter"] == q_curr, "amount"].sum())),
            "Returns & Reverse Logistics": (self._return_cost_for_quarter(q_prior), self._return_cost_for_quarter(q_curr)),
        }

    def calculate_pnl_waterfall(self) -> List[Dict[str, Any]]:
        """Build an accounting-consistent profit bridge.

        Every non-total bar is a profit impact, not a raw metric delta. The bridge
        reconciles exactly to current net profit minus prior net profit.
        """
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
        if orders.empty or "shipping_partner" not in orders.columns:
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
        if items.empty or products.empty:
            return []
        merged = items.merge(products[["product_id", "category"]], on="product_id", how="left")
        merged["revenue"] = merged["item_total"]
        merged["cogs_value"] = merged["quantity"] * merged["unit_cogs"]
        grouped = merged.groupby("category").agg(revenue=("revenue", "sum"), cogs=("cogs_value", "sum")).reset_index()
        grouped["gross_margin"] = grouped["revenue"] - grouped["cogs"]
        grouped["margin_pct"] = grouped["gross_margin"] / grouped["revenue"].replace(0, np.nan) * 100
        grouped = grouped.sort_values("revenue", ascending=False)
        grouped["pareto_pct"] = grouped["revenue"].cumsum() / grouped["revenue"].sum() * 100
        return [{"category": str(r.category), "revenue": round(float(r.revenue), 2), "gross_margin": round(float(r.gross_margin), 2), "margin_pct": round(float(r.margin_pct), 2), "pareto_pct": round(float(r.pareto_pct), 2), "trend": "watch" if r.margin_pct < 25 else "stable"} for r in grouped.itertuples()]

    def analyze_marketing_efficiency(self) -> List[Dict[str, Any]]:
        marketing = self.dfs.get("marketing_spend", pd.DataFrame())
        if marketing.empty:
            return []
        q_prior, q_curr = self._quarters()
        current = marketing[marketing["quarter"] == q_curr]
        prior = marketing[marketing["quarter"] == q_prior]
        c = current.groupby("channel").agg(spend=("spend_amount", "sum"), attributed_orders=("attributed_orders", "sum"), revenue=("attributed_revenue", "sum")).reset_index()
        p = prior.groupby("channel").agg(prior_spend=("spend_amount", "sum"), prior_orders=("attributed_orders", "sum")).reset_index()
        merged = c.merge(p, on="channel", how="left")
        merged["cac"] = merged["spend"] / merged["attributed_orders"].replace(0, np.nan)
        merged["prior_cac"] = merged["prior_spend"] / merged["prior_orders"].replace(0, np.nan)
        merged["cac_growth_pct"] = (merged["cac"] - merged["prior_cac"]) / merged["prior_cac"].replace(0, np.nan) * 100
        merged["roas"] = merged["revenue"] / merged["spend"].replace(0, np.nan)
        return [{"channel": str(r.channel), "spend": round(float(r.spend), 2), "cac": round(float(r.cac), 2), "cac_growth_pct": round(float(r.cac_growth_pct), 1), "roas": round(float(r.roas), 2), "verdict": "Reallocate" if r.roas < 2.5 or r.cac_growth_pct > 20 else "Scale / Maintain"} for r in merged.sort_values("roas").itertuples()]

    def analysis_snapshot(self) -> Dict[str, Any]:
        return {"kpi": self.calculate_executive_kpis(), "shipping": self.analyze_shipping_partners(), "categories": self.analyze_category_margins(), "marketing": self.analyze_marketing_efficiency(), "waterfall": self.calculate_pnl_waterfall()}
