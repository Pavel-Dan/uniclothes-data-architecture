# UNICLOTHES ETL pipeline - PowerShell version
param(
    [string]$PostgresUser = "uniclothes",
    [string]$PostgresDb = "uniclothes",
    [string]$Container = "uniclothes-postgres"
)

$ErrorActionPreference = "Stop"

Write-Host "=== UNICLOTHES ETL Pipeline ===" -ForegroundColor Cyan

$running = docker ps --format "{{.Names}}" | Select-String -Pattern "^${Container}$"
if (-not $running) {
    Write-Host "ERROR: Container $Container is not running." -ForegroundColor Red
    Write-Host "Start the stack first: cd docker; docker compose up -d"
    exit 1
}

Write-Host "[1/5] Waiting for PostgreSQL..."
do {
    Start-Sleep -Seconds 2
    $ready = docker exec $Container pg_isready -U $PostgresUser -d $PostgresDb 2>$null
} while ($LASTEXITCODE -ne 0)

Write-Host "[2/5] Truncating raw tables..."
docker exec $Container psql -U $PostgresUser -d $PostgresDb -c @"
TRUNCATE raw.customers_crm, raw.customers_web, raw.customers_pos,
         raw.products_erp, raw.products_web, raw.stores,
         raw.orders_web, raw.orders_pos CASCADE;
"@

Write-Host "[3/5] Loading CSV seed data..."
docker exec $Container psql -U $PostgresUser -d $PostgresDb -f /sql/00_load_raw_data.sql

Write-Host "[4/5] Running ETL (staging + dwh + RGPD)..."
docker exec $Container psql -U $PostgresUser -d $PostgresDb -f /sql/05_build_star_schema.sql
docker exec $Container psql -U $PostgresUser -d $PostgresDb -f /sql/06_rgpd_security.sql

Write-Host "[5/5] Uploading product images to MinIO..."
$uploadScript = Join-Path $PSScriptRoot "ingest\upload_product_images.py"
if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 $uploadScript
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python $uploadScript
} else {
    Write-Host "WARN: Python not found - skip image upload (run manually: py scripts/ingest/upload_product_images.py)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== ETL Complete ===" -ForegroundColor Green
docker exec $Container psql -U $PostgresUser -d $PostgresDb -c @"
SELECT 'raw.customers_crm' AS table_name, COUNT(*) AS rows FROM raw.customers_crm
UNION ALL SELECT 'staging.customers_golden', COUNT(*) FROM staging.customers_golden
UNION ALL SELECT 'dwh.fact_sales', COUNT(*) FROM dwh.fact_sales;
"@

docker exec $Container psql -U $PostgresUser -d $PostgresDb -c @"
SELECT metric_name, metric_value, target_value, status FROM staging.quality_metrics;
"@

Write-Host ""
Write-Host "Streamlit: http://localhost:8501  (portail BI UNICLOTHES)"
Write-Host "Grafana:   http://localhost:3001  (monitoring infra)"
Write-Host "MinIO:     http://localhost:9001"
