-- UNICLOTHES: ETL Pipeline - raw -> staging -> dwh
-- Golden record rules:
--   Customers: email normalized, priority CRM(1) > web(2) > pos(3)
--   Products: ERP is master source (priority 1)
--   Images: object key = product_ref || '.jpg' in MinIO bucket product-images

-- Schema migration (existing deployments)
ALTER TABLE dwh.dim_product ADD COLUMN IF NOT EXISTS image_object_key VARCHAR(120);
ALTER TABLE dwh.dim_product ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);
ALTER TABLE staging.products_golden ADD COLUMN IF NOT EXISTS image_object_key VARCHAR(120);

-- ============================================================
-- STEP 1: Populate staging.customers_unified from raw sources
-- ============================================================
TRUNCATE staging.customers_unified RESTART IDENTITY;

INSERT INTO staging.customers_unified
    (source_id, source_system, email_normalized, email, first_name, last_name,
     phone, consent_marketing, consent_date, last_activity, store_code, source_priority)
SELECT
    source_id, 'crm',
    LOWER(TRIM(email)),
    email, first_name, last_name, phone,
    consent_marketing, consent_date, last_activity,
    NULL, 1
FROM raw.customers_crm;

INSERT INTO staging.customers_unified
    (source_id, source_system, email_normalized, email, first_name, last_name,
     phone, consent_marketing, consent_date, last_activity, store_code, source_priority)
SELECT
    source_id, 'web',
    LOWER(TRIM(email)),
    email, first_name, last_name, phone,
    consent_marketing, consent_date, last_activity,
    NULL, 2
FROM raw.customers_web;

INSERT INTO staging.customers_unified
    (source_id, source_system, email_normalized, email, first_name, last_name,
     phone, consent_marketing, consent_date, last_activity, store_code, source_priority)
SELECT
    source_id, 'pos',
    LOWER(TRIM(email)),
    email, first_name, last_name, phone,
    consent_marketing, consent_date, last_activity,
    store_code, 3
FROM raw.customers_pos;

-- ============================================================
-- STEP 2: Golden record customers (deduplication by email)
-- ============================================================
TRUNCATE staging.customers_golden RESTART IDENTITY CASCADE;

INSERT INTO staging.customers_golden
    (email_normalized, email, first_name, last_name, phone,
     consent_marketing, consent_date, last_activity,
     is_active_12m, email_valid, duplicate_count)
SELECT DISTINCT ON (cu.email_normalized)
    cu.email_normalized,
    cu.email,
    cu.first_name,
    cu.last_name,
    cu.phone,
    cu.consent_marketing,
    cu.consent_date,
    cu.last_activity,
    (cu.last_activity >= CURRENT_DATE - INTERVAL '12 months') AS is_active_12m,
    (cu.email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') AS email_valid,
    cnt.duplicate_count
FROM staging.customers_unified cu
JOIN (
    SELECT email_normalized, COUNT(*) AS duplicate_count
    FROM staging.customers_unified
    WHERE email_normalized IS NOT NULL AND email_normalized <> ''
    GROUP BY email_normalized
) cnt ON cu.email_normalized = cnt.email_normalized
WHERE cu.email_normalized IS NOT NULL AND cu.email_normalized <> ''
ORDER BY cu.email_normalized, cu.source_priority ASC, cu.last_activity DESC NULLS LAST;

-- ============================================================
-- STEP 3: Golden record products (ERP master)
-- ============================================================
TRUNCATE staging.products_unified RESTART IDENTITY;

INSERT INTO staging.products_unified
    (source_ref, source_system, product_ref, product_name, category, price_eur, stock_qty, source_priority)
SELECT product_ref, 'erp', product_ref, product_name, category, price_eur, stock_qty, 1
FROM raw.products_erp;

INSERT INTO staging.products_unified
    (source_ref, source_system, product_ref, product_name, category, price_eur, stock_qty, source_priority)
SELECT web_sku, 'web', product_ref, product_name, category, price_eur, NULL, 2
FROM raw.products_web;

TRUNCATE staging.products_golden RESTART IDENTITY CASCADE;

INSERT INTO staging.products_golden (product_ref, product_name, category, price_eur, stock_qty, image_object_key)
SELECT DISTINCT ON (product_ref)
    product_ref, product_name, category, price_eur, stock_qty,
    product_ref || '.jpg'
FROM staging.products_unified
WHERE product_ref IS NOT NULL
ORDER BY product_ref, source_priority ASC;

-- ============================================================
-- STEP 4: Unify orders
-- ============================================================
TRUNCATE staging.orders_unified;

INSERT INTO staging.orders_unified
SELECT order_id, customer_email, channel, NULL, order_date, product_ref, quantity, unit_price_eur, amount_eur
FROM raw.orders_web;

INSERT INTO staging.orders_unified
SELECT order_id, customer_email, 'store', store_code, order_date, product_ref, quantity, unit_price_eur, amount_eur
FROM raw.orders_pos;

-- ============================================================
-- STEP 5: Quality metrics
-- ============================================================
TRUNCATE staging.quality_metrics RESTART IDENTITY;

INSERT INTO staging.quality_metrics (metric_name, metric_value, target_value, status)
SELECT
    'duplicate_rate_pct',
    ROUND(100.0 * (SUM(duplicate_count) - COUNT(*)) / NULLIF(SUM(duplicate_count), 0), 2),
    2.0,
    CASE WHEN ROUND(100.0 * (SUM(duplicate_count) - COUNT(*)) / NULLIF(SUM(duplicate_count), 0), 2) <= 2.0
         THEN 'OK' ELSE 'ALERT' END
FROM staging.customers_golden;

INSERT INTO staging.quality_metrics (metric_name, metric_value, target_value, status)
SELECT
    'valid_email_rate_pct',
    ROUND(100.0 * COUNT(*) FILTER (WHERE email_valid) / NULLIF(COUNT(*), 0), 2),
    95.0,
    CASE WHEN ROUND(100.0 * COUNT(*) FILTER (WHERE email_valid) / NULLIF(COUNT(*), 0), 2) >= 95.0
         THEN 'OK' ELSE 'ALERT' END
FROM staging.customers_golden;

INSERT INTO staging.quality_metrics (metric_name, metric_value, target_value, status)
SELECT
    'active_customer_12m_count',
    COUNT(*) FILTER (WHERE is_active_12m),
    NULL,
    'INFO'
FROM staging.customers_golden;

INSERT INTO staging.quality_metrics (metric_name, metric_value, target_value, status)
SELECT
    'products_with_image_pct',
    ROUND(100.0 * COUNT(*) FILTER (WHERE image_object_key IS NOT NULL) / NULLIF(COUNT(*), 0), 2),
    95.0,
    CASE WHEN ROUND(100.0 * COUNT(*) FILTER (WHERE image_object_key IS NOT NULL) / NULLIF(COUNT(*), 0), 2) >= 95.0
         THEN 'OK' ELSE 'ALERT' END
FROM staging.products_golden;

-- ============================================================
-- STEP 6: Populate dimension tables
-- ============================================================

-- dim_date: generate dates for last 400 days
INSERT INTO dwh.dim_date (date_key, full_date, day_of_week, day_name, week_of_year, month_num, month_name, quarter_num, year_num)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER,
    d,
    EXTRACT(DOW FROM d)::INTEGER,
    TO_CHAR(d, 'Day'),
    EXTRACT(WEEK FROM d)::INTEGER,
    EXTRACT(MONTH FROM d)::INTEGER,
    TO_CHAR(d, 'Month'),
    EXTRACT(QUARTER FROM d)::INTEGER,
    EXTRACT(YEAR FROM d)::INTEGER
FROM generate_series(CURRENT_DATE - 400, CURRENT_DATE + 30, '1 day'::interval) AS d
ON CONFLICT (full_date) DO NOTHING;

INSERT INTO dwh.dim_channel (channel_code, channel_name) VALUES
    ('web', 'Site e-commerce'),
    ('app', 'Application mobile'),
    ('store', 'Boutique physique')
ON CONFLICT (channel_code) DO NOTHING;

INSERT INTO dwh.dim_store (store_code, store_name, city, region)
SELECT store_code, store_name, city, region FROM raw.stores
ON CONFLICT (store_code) DO UPDATE SET
    store_name = EXCLUDED.store_name,
    city = EXCLUDED.city,
    region = EXCLUDED.region;

INSERT INTO dwh.dim_store (store_code, store_name, city, region) VALUES
    ('ONLINE', 'En ligne', 'Paris', 'National')
ON CONFLICT (store_code) DO NOTHING;

-- dim_customer from golden record
TRUNCATE dwh.dim_customer RESTART IDENTITY CASCADE;

INSERT INTO dwh.dim_customer
    (golden_id, email, first_name, last_name, phone, consent_marketing,
     consent_date, last_activity, is_active_12m, email_valid)
SELECT
    golden_id, email, first_name, last_name, phone, consent_marketing,
    consent_date, last_activity, is_active_12m, email_valid
FROM staging.customers_golden;

-- dim_product from golden record
TRUNCATE dwh.dim_product RESTART IDENTITY CASCADE;

INSERT INTO dwh.dim_product (product_ref, product_name, category, price_eur, stock_qty, image_object_key, image_url)
SELECT
    product_ref, product_name, category, price_eur, stock_qty,
    image_object_key,
    'http://localhost:9000/product-images/' || image_object_key
FROM staging.products_golden;

-- ============================================================
-- STEP 7: Populate fact_sales
-- ============================================================
TRUNCATE dwh.fact_sales RESTART IDENTITY;

INSERT INTO dwh.fact_sales
    (order_id, date_key, customer_key, product_key, store_key, channel_key,
     quantity, unit_price_eur, amount_eur, order_timestamp)
SELECT
    o.order_id,
    TO_CHAR(o.order_date::DATE, 'YYYYMMDD')::INTEGER,
    dc.customer_key,
    dp.product_key,
    COALESCE(ds.store_key, (SELECT store_key FROM dwh.dim_store WHERE store_code = 'ONLINE')),
    dch.channel_key,
    o.quantity,
    o.unit_price_eur,
    o.amount_eur,
    o.order_date
FROM staging.orders_unified o
LEFT JOIN dwh.dim_customer dc ON LOWER(TRIM(o.customer_email)) = LOWER(TRIM(dc.email))
LEFT JOIN dwh.dim_product dp ON o.product_ref = dp.product_ref
LEFT JOIN dwh.dim_store ds ON o.store_code = ds.store_code
LEFT JOIN dwh.dim_channel dch ON o.channel = dch.channel_code
WHERE dc.customer_key IS NOT NULL AND dp.product_key IS NOT NULL;
