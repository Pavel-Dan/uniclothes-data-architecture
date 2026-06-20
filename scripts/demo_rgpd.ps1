# Script demo RGPD - UNICLOTHES
# Executer apres run_etl.ps1

Write-Host "=== Demo RGPD UNICLOTHES ===" -ForegroundColor Cyan

$testEmail = "marie.martin0@email.com"

Write-Host "`n[1] Droit d'acces - export des donnees client" -ForegroundColor Yellow
docker exec uniclothes-postgres psql -U uniclothes -d uniclothes -c "SELECT * FROM audit.export_customer_gdpr('$testEmail');"

Write-Host "`n[2] Vue anonymisee (role analyst)" -ForegroundColor Yellow
docker exec uniclothes-postgres psql -U uniclothes -d uniclothes -c "SELECT customer_key, email_masked, first_name_masked, consent_marketing, is_active_12m FROM dwh.dim_customer_anonymized LIMIT 5;"

Write-Host "`n[3] Droit a l'effacement" -ForegroundColor Yellow
docker exec uniclothes-postgres psql -U uniclothes -d uniclothes -c "SELECT * FROM audit.delete_customer_gdpr('$testEmail');"

Write-Host "`n[4] Journal audit RGPD" -ForegroundColor Yellow
docker exec uniclothes-postgres psql -U uniclothes -d uniclothes -c "SELECT request_id, request_type, customer_email, status, processed_at FROM audit.gdpr_requests;"

Write-Host "`nDemo RGPD terminee." -ForegroundColor Green
