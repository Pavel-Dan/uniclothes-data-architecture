#!/usr/bin/env bash
# UNICLOTHES ETL pipeline - load raw data and build star schema
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_DIR="$PROJECT_ROOT/docker"

POSTGRES_USER="${POSTGRES_USER:-uniclothes}"
POSTGRES_DB="${POSTGRES_DB:-uniclothes}"
CONTAINER="${POSTGRES_CONTAINER:-uniclothes-postgres}"

echo "=== UNICLOTHES ETL Pipeline ==="

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "ERROR: Container ${CONTAINER} is not running."
    echo "Start the stack first: cd docker && docker compose up -d"
    exit 1
fi

echo "[1/5] Waiting for PostgreSQL..."
until docker exec "$CONTAINER" pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; do
    sleep 2
done

echo "[2/5] Truncating raw tables..."
docker exec "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    TRUNCATE raw.customers_crm, raw.customers_web, raw.customers_pos,
             raw.products_erp, raw.products_web, raw.stores,
             raw.orders_web, raw.orders_pos CASCADE;
"

echo "[3/5] Loading CSV seed data..."
docker exec "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /sql/00_load_raw_data.sql

echo "[4/5] Running ETL (staging + dwh + RGPD)..."
docker exec "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /sql/05_build_star_schema.sql
docker exec "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /sql/06_rgpd_security.sql

echo "[5/5] Uploading product images to MinIO..."
if command -v python3 &>/dev/null; then
    python3 "$SCRIPT_DIR/ingest/upload_product_images.py"
elif command -v python &>/dev/null; then
    python "$SCRIPT_DIR/ingest/upload_product_images.py"
else
    echo "WARN: Python not found — skip image upload"
fi

echo ""
echo "=== ETL Complete ==="
docker exec "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    SELECT 'raw.customers_crm' AS table_name, COUNT(*) AS rows FROM raw.customers_crm
    UNION ALL SELECT 'staging.customers_golden', COUNT(*) FROM staging.customers_golden
    UNION ALL SELECT 'dwh.fact_sales', COUNT(*) FROM dwh.fact_sales
    UNION ALL SELECT 'staging.quality_metrics', COUNT(*) FROM staging.quality_metrics;
"

docker exec "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    SELECT metric_name, metric_value, target_value, status FROM staging.quality_metrics;
"

echo ""
echo "Streamlit: http://localhost:8501  (portail BI UNICLOTHES)"
echo "Grafana:   http://localhost:3001  (monitoring infra)"
echo "MinIO:     http://localhost:9001"
