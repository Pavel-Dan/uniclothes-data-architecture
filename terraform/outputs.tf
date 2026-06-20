output "streamlit_url" {
  description = "URL portail BI Streamlit"
  value       = "http://localhost:8501"
}

output "grafana_url" {
  description = "URL Grafana monitoring infrastructure"
  value       = "http://localhost:${var.grafana_port}"
}

output "grafana_credentials" {
  description = "Identifiants Grafana par defaut"
  value       = "admin / uniclothes_grafana"
  sensitive   = true
}

output "minio_console_url" {
  description = "URL console MinIO"
  value       = "http://localhost:${var.minio_console_port}"
}

output "postgres_connection" {
  description = "Chaine de connexion PostgreSQL"
  value       = "postgresql://uniclothes:uniclothes_dev_2026@localhost:5432/uniclothes"
  sensitive   = true
}

output "etl_command" {
  description = "Commande pour lancer le pipeline ETL"
  value       = "../scripts/run_etl.ps1"
}

output "docker_network" {
  description = "Reseau Docker cree par Terraform"
  value       = docker_network.uniclothes.name
}
