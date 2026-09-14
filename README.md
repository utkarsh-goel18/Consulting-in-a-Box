# Consulting in a Box

> **From raw business data to actionable executive decisions.**  
> A production-quality automated decision-intelligence and consulting platform designed for management consultants, business analysts, and corporate decision-makers.

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![DuckDB](https://img.shields.io/badge/OLAP-DuckDB-FFF000.svg?style=flat&logo=duckdb)](https://duckdb.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_18-4169E1.svg?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/Frontend-React_19_+_TypeScript-61DAFB.svg?style=flat&logo=react)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS_v4-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com/)

---

## 1. What the Product Does

**Consulting in a Box** is not a chatbot, not a dashboard, and not an LLM wrapper. It automates a structured management consulting engagement end-to-end:

1. **Ingests & Profiles Multi-File Business Data**: Loads raw CSV/XLSX files, validates data types, detects missing values and duplicate rows, infers primary keys, discovers relational foreign-key linkages, and computes a composite **Data Quality Score (0–100%)**.
2. **Structures Strategic Problems**: Offers 8 predefined consulting engagement archetypes (Profitability Decline, Customer Churn, Revenue Growth, Cost Optimization, Marketing ROI, Sales Performance, Inventory Optimization, Operational Efficiency) or accepts ad-hoc custom business questions.
3. **Formulates an Analysis Plan**: The AI generates a deterministic multi-step investigation plan with target metrics and methods (Variance Decomposition, Pareto 80/20, Cohort Analysis, Contract Rate Variance).
4. **Executes Deterministic Analytics**: The backend computes all metrics, aggregations, growth rates, margins, and variances using compiled SQL (DuckDB / PostgreSQL) and NumPy/Pandas. **The LLM never performs mathematical calculations.**
5. **Constructs a Root-Cause Driver Tree**: Decomposes top-level financial deltas (e.g. Net Profit ↓ 17.4%) down into parent-child drivers (Revenue vs Costs → AOV/Orders vs Delivery/Marketing/Returns) with clickable nodes, contribution percentages, and affected segments.
6. **Strict Truth Classification**: Every finding is categorized as:
   - **`[FACT]`**: Verifiable mathematical truth directly computed from records.
   - **`[INSIGHT]`**: Analytical interpretation of variance contribution and relational patterns.
   - **`[HYPOTHESIS]`**: Plausible operational explanation requiring field validation.
   - **`[RECOMMENDATION]`**: Actionable business prescription with financial justification.
7. **Transparent Audit Trail**: Every insight and tree node features a **"View Evidence"** button showing the exact mathematical formula, the compiled analytical SQL query, an aggregate period table, and granular sample rows.
8. **What-If Scenario Simulator**: Simulates operational adjustments (retail price, logistics carrier terms, churn rate, marketing reallocation, COGS optimization) using microeconomic elasticity models.
9. **Executive Consulting Report**: Compiles a 10-section McKinsey/Deloitte-style deliverable with one-click **PDF export** and clean print stylesheets.
10. **Zero-API Demo Mode**: Runs immediately out of the box with the synthetic **NovaMart** e-commerce dataset without requiring third-party API keys or local database setup.

---

## 2. Architecture & Pipeline

```
                                  USER WORKFLOW
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
   Upload CSV / XLSX           Select Consulting Case          Click "Try Demo"
   (or seed DB tables)        (or custom text prompt)         (NovaMart 1-Click)
           │                            │                            │
           └────────────────────────────┬────────────────────────────┘
                                        │
                                        ▼
                   ┌─────────────────────────────────────────┐
                   │        AI PLANNING LAYER (LLM)          │
                   │   • Translates question into plan       │
                   │   • Establishes quantitative steps      │
                   │   • Zero arithmetic calculation         │
                   └────────────────────┬────────────────────┘
                                        │ (Analysis Plan)
                                        ▼
                   ┌─────────────────────────────────────────┐
                   │    DETERMINISTIC ANALYTICS ENGINE       │
                   │   • DuckDB / PostgreSQL OLAP queries    │
                   │   • Pandas / NumPy variance & margins   │
                   │   • Pareto 80/20 & anomaly detection    │
                   └────────────────────┬────────────────────┘
                                        │ (Verified Numerical Results)
                                        ▼
     ┌──────────────────────────────────┴──────────────────────────────────┐
     │                                                                     │
     ▼                                                                     ▼
┌───────────────────────────┐                                 ┌───────────────────────────┐
│     ROOT CAUSE ENGINE     │                                 │   SCENARIO SIMULATOR      │
│ • Hierarchical Driver Tree│                                 │ • Microeconomic Elasticity│
│ • Contribution % to delta │                                 │ • Base Case vs Scenario   │
│ • Affected partner routing│                                 │ • Sensitivity Waterfall   │
└────────────┬──────────────┘                                 └─────────────┬─────────────┘
             │                                                              │
             └──────────────────────────┬───────────────────────────────────┘
                                        │
                                        ▼
                   ┌─────────────────────────────────────────┐
                   │      EVIDENCE & GOVERNANCE VAULT        │
                   │   • FACT / INSIGHT / HYPOTHESIS / REC   │
                   │   • SQL query audit trail & formulas    │
                   │   • Underlying record samples           │
                   └────────────────────┬────────────────────┘
                                        │
                                        ▼
                   ┌─────────────────────────────────────────┐
                   │          EXECUTIVE INTERFACES           │
                   │   • Power BI-style Executive Dashboard  │
                   │   • Interactive Driver Tree Explorer    │
                   │   • 10-Section Consulting Deliverable   │
                   │   • One-Click Official PDF Export       │
                   └─────────────────────────────────────────┘
```

---

## 3. Tech Stack

| Layer | Technologies | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Tailwind CSS v4, Lucide Icons | Responsive, Bloomberg/McKinsey-inspired corporate aesthetic |
| **Visualizations** | Recharts, Custom Waterfall & Driver Tree SVG | Power BI-style interactive charts, P&L bridges, hierarchy trees |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, Uvicorn | High-performance asynchronous REST API with strict schemas |
| **Data Engine** | DuckDB, SQLAlchemy, PostgreSQL 18, Pandas, NumPy | Embedded columnar OLAP engine + enterprise relational database |
| **AI Layer** | Clean Provider Abstraction (`Mock`, `Gemini`, `OpenAI`) | Analysis plan generation and executive narrative synthesis |
| **Reporting** | ReportLab 5.0, Custom CSS Print Engine | Server-side vector PDF generation & in-browser print styling |

---

## 4. Relational Data Model

The platform includes a production PostgreSQL schema (`backend/sql/schema.sql`) and sample queries (`backend/sql/analytical_queries.sql`):

```
customers ─────────────< orders ─────────────< order_items >───────────── products
                             │
                             ├───────────────< returns
                             │
                      marketing_spend
                             │
                          expenses
```

- **`customers`**: Customer demographics, signup cohort date, geographic region (Tier-1 Metro vs Tier-2 Regional), customer tier, acquisition channel, churn status.
- **`products`**: SKUs, product name, category, subcategory, unit COGS, retail unit price, supplier.
- **`orders`**: Order date, customer ID, payment method, shipping partner (FastLogistics, ExpressCargo, BlueDart), gross sales, discount amount, net revenue, delivery cost incurred.
- **`order_items`**: Order ID, product ID, item quantity, unit price, unit COGS, line-item gross margin.
- **`marketing_spend`**: Spend date, channel (Paid Social, Google Ads, Affiliate, Email), campaign name, impressions, clicks, attributed orders, attributed revenue.
- **`expenses`**: Expense date, expense category (Warehousing, Hosting, G&A), department, description, amount.
- **`returns`**: Order ID, return date, reason (Fit/Defect/Late/Remorse), refund amount, reverse logistics cost.

---

## 5. The NovaMart Consulting Engagement Case

When launched in **Demo Mode**, the application evaluates **NovaMart**, a mid-market e-commerce enterprise:

- **Target Window**: Q3 2024 vs Q2 2024
- **Reported Challenge**: *"Net operating profit contracted 17.4% QoQ. Isolate the major cost and revenue drivers."*

### Engineered Business Anomalies Detected by Engine:
1. **Logistics Rate Hike**: FastLogistics instituted an unannounced +17.1% regional delivery fee increase on Tier-2 routes, adding $105,400 in direct excess fulfillment costs.
2. **AOV Dilution**: Mid-quarter promotional discounting caused basket size contraction in Electronics (-8.4% units/order) and increased coupon usage, pulling AOV down by 5.1% (-$25.34/order).
3. **Paid Social Diminishing Returns**: Paid Social customer acquisition cost (CAC) jumped 38.2% from $71.20 to $98.50 with a depressed ROAS of 2.1x, while Affiliate and Search remained highly profitable (4.5x and 3.8x ROAS).
4. **Tier-2 Churn Acceleration**: Customer churn increased by 3.2 percentage points, with 74% of newly churned accounts located in Tier-2 zip codes impacted by NovaMart's flat delivery surcharge.

---

## 6. How to Run Locally

### Prerequisites
- **Node.js** (v18+) & **npm**
- **Python** (v3.10+)

### Quick Start (Zero-Configuration Demo Mode)

#### 1. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# Or macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch FastAPI backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend will automatically generate the NovaMart demo datasets in `backend/data/` and load them into memory & DuckDB upon startup.*

#### 2. Frontend Setup
```bash
# Open a second terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Open your browser at: **`http://localhost:5173`**

Click **"Try Demo (NovaMart)"** in the top navigation bar to watch the automated verification sequence load the executive consulting suite!

---

## 7. Connecting to PostgreSQL (Optional Enterprise Setup)

If you wish to run the analytics directly against an enterprise PostgreSQL instance:

1. Create a database:
   ```sql
   CREATE DATABASE consulting_box;
   ```
2. Configure `.env` in `backend/`:
   ```ini
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/consulting_box
   ```
3. Run the PostgreSQL seeder:
   ```bash
   python scripts/seed_postgres.py
   ```
*If PostgreSQL is not running or credentials are not supplied, the platform seamlessly falls back to DuckDB in-process OLAP, guaranteeing zero downtime.*

---

## 8. Enabling Live LLM Reasoning (Optional)

In `.env` or via the **/settings** UI tab:
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyYourKeyHere
AI_MODEL=gemini-1.5-flash
```
Or for OpenAI:
```ini
AI_PROVIDER=openai
OPENAI_API_KEY=sk-YourKeyHere
```
*Note: When no API key is provided, the platform operates in 100% deterministic Mock Strategic Consultant mode, guaranteeing that all analysis plans, root causes, and recommendations are available offline.*

---

## 9. Testing & Quality Assurance

Run the automated backend test suite:
```bash
cd backend
.\venv\Scripts\python.exe -m pytest -o pythonpath=. tests/
```
Tests cover:
- Automated dataset profiling, type inference & PK/FK detection
- Mathematical consistency of the Driver Tree decomposition
- Microeconomic elasticity calculations in the What-If Simulator
- Server-side PDF Report generation with ReportLab
- REST API endpoint contracts and health checks

---

## 10. Limitations & Future Roadmap

- **Data Connectors**: Currently supports CSV, XLSX, and PostgreSQL. Future iterations can integrate Snowflake, BigQuery, and Databricks connectors.
- **Predictive ML**: Adding automated ARIMA/Prophet time-series forecasting for seasonal demand planning.
- **Monte Carlo Simulations**: Upgrading the scenario simulator with probabilistic confidence intervals around price elasticity.
