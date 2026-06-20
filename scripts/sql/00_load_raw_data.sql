-- Load seed data from CSV files mounted in /seed
-- Executed by run_etl script after container is up

\echo 'Loading raw.customers_crm...'
\copy raw.customers_crm(source_id,email,first_name,last_name,phone,consent_marketing,consent_date,last_activity) FROM '/seed/customers_crm.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading raw.customers_web...'
\copy raw.customers_web(source_id,email,first_name,last_name,phone,consent_marketing,consent_date,last_activity) FROM '/seed/customers_web.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading raw.customers_pos...'
\copy raw.customers_pos(source_id,email,first_name,last_name,phone,consent_marketing,consent_date,last_activity,store_code) FROM '/seed/customers_pos.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading raw.products_erp...'
\copy raw.products_erp(product_ref,product_name,category,price_eur,stock_qty) FROM '/seed/products_erp.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading raw.products_web...'
\copy raw.products_web(web_sku,product_ref,product_name,category,price_eur) FROM '/seed/products_web.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading raw.stores...'
\copy raw.stores(store_code,store_name,city,region,opened_date) FROM '/seed/stores.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading raw.orders_web...'
\copy raw.orders_web(order_id,customer_email,channel,order_date,product_ref,quantity,unit_price_eur,amount_eur) FROM '/seed/orders_web.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Loading raw.orders_pos...'
\copy raw.orders_pos(order_id,customer_email,store_code,order_date,product_ref,quantity,unit_price_eur,amount_eur) FROM '/seed/orders_pos.csv' WITH (FORMAT csv, HEADER true, NULL '');

\echo 'Raw data loaded successfully.'
