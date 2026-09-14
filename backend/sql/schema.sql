-- ============================================================================
-- Consulting in a Box - PostgreSQL Enterprise Schema
-- Industry Standard E-commerce & Decision Intelligence Relational Schema
-- ============================================================================

-- Drop tables if they exist in reverse dependency order
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS marketing_spend CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- 1. CUSTOMERS TABLE
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    signup_date DATE NOT NULL,
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    region VARCHAR(50) NOT NULL,            -- e.g., North, South, East, West, Central
    tier VARCHAR(20) NOT NULL,              -- e.g., Tier 1, Tier 2, Tier 3
    customer_segment VARCHAR(50) NOT NULL,  -- e.g., Enterprise, SMB, Consumer, VIP
    acquisition_channel VARCHAR(50) NOT NULL, -- e.g., Organic Search, Paid Search, Paid Social, Email, Direct
    churn_status BOOLEAN DEFAULT FALSE,
    churn_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_customers_tier ON customers(tier);
CREATE INDEX idx_customers_segment ON customers(customer_segment);
CREATE INDEX idx_customers_signup_date ON customers(signup_date);
CREATE INDEX idx_customers_churn ON customers(churn_status);

-- 2. PRODUCTS TABLE
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,         -- e.g., Electronics, Fashion, Home & Living, Beauty, Grocery
    subcategory VARCHAR(100) NOT NULL,
    unit_cost NUMERIC(12, 2) NOT NULL,      -- Base COGS
    unit_price NUMERIC(12, 2) NOT NULL,     -- Retail Price
    supplier_name VARCHAR(150),
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_subcategory ON products(subcategory);

-- 3. ORDERS TABLE
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date DATE NOT NULL,
    order_status VARCHAR(50) NOT NULL,      -- e.g., Delivered, Returned, Cancelled, Processing
    payment_method VARCHAR(50) NOT NULL,    -- e.g., Credit Card, UPI, Net Banking, COD
    shipping_partner VARCHAR(50) NOT NULL,  -- e.g., FastLogistics, ExpressCargo, BlueDart, StandardPost
    gross_amount NUMERIC(14, 2) NOT NULL,
    discount_amount NUMERIC(14, 2) DEFAULT 0.00,
    net_amount NUMERIC(14, 2) NOT NULL,
    delivery_fee NUMERIC(10, 2) DEFAULT 0.00,
    delivery_cost NUMERIC(10, 2) NOT NULL,  -- Actual logistics cost incurred by company
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_shipping_partner ON orders(shipping_partner);

-- 4. ORDER ITEMS TABLE (Granular basket & COGS tracking)
CREATE TABLE order_items (
    order_item_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    unit_cogs NUMERIC(12, 2) NOT NULL,
    item_total NUMERIC(14, 2) NOT NULL,
    gross_margin NUMERIC(14, 2) GENERATED ALWAYS AS (item_total - (unit_cogs * quantity)) STORED
);

CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- 5. MARKETING SPEND TABLE
CREATE TABLE marketing_spend (
    spend_id VARCHAR(50) PRIMARY KEY,
    spend_date DATE NOT NULL,
    channel VARCHAR(50) NOT NULL,           -- e.g., Paid Social, Google Ads, Affiliate, Email Marketing
    campaign VARCHAR(150) NOT NULL,
    spend_amount NUMERIC(14, 2) NOT NULL,
    impressions INT DEFAULT 0,
    clicks INT DEFAULT 0,
    attributed_orders INT DEFAULT 0,
    attributed_revenue NUMERIC(14, 2) DEFAULT 0.00
);

CREATE INDEX idx_marketing_date ON marketing_spend(spend_date);
CREATE INDEX idx_marketing_channel ON marketing_spend(channel);

-- 6. OPERATING EXPENSES TABLE
CREATE TABLE expenses (
    expense_id VARCHAR(50) PRIMARY KEY,
    expense_date DATE NOT NULL,
    category VARCHAR(100) NOT NULL,         -- Logistics, Warehousing, Payment Gateways, Technology, General & Admin
    department VARCHAR(100) NOT NULL,
    description TEXT,
    amount NUMERIC(14, 2) NOT NULL
);

CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category);

-- 7. RETURNS & REVERSALS TABLE
CREATE TABLE returns (
    return_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    return_date DATE NOT NULL,
    return_reason VARCHAR(150) NOT NULL,    -- Damaged Goods, Defective Item, Wrong Size, Buyer Remorse
    refund_amount NUMERIC(14, 2) NOT NULL,
    reverse_logistics_cost NUMERIC(10, 2) NOT NULL,
    restockable BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_returns_order_id ON returns(order_id);
CREATE INDEX idx_returns_date ON returns(return_date);
CREATE INDEX idx_returns_reason ON returns(return_reason);
