-- UNICLOTHES: Exemple d'exercice du droit a l'effacement (RGPD Art. 17)
-- Usage: psql -f delete_customer_gdpr.sql
--   ou: docker exec uniclothes-postgres psql -U uniclothes -d uniclothes -f /sql/delete_customer_gdpr.sql

\set target_email 'marie.martin0@email.com'

\echo 'Demande de suppression RGPD pour:' :target_email

SELECT * FROM audit.delete_customer_gdpr(:'target_email');

\echo 'Journal audit:'
SELECT request_id, request_type, customer_email, status, processed_at, notes
FROM audit.gdpr_requests
ORDER BY request_id DESC
LIMIT 5;
