variable "project_name" {
  description = "Nom du projet UNICLOTHES"
  type        = string
  default     = "uniclothes"
}

variable "network_name" {
  description = "Nom du reseau Docker"
  type        = string
  default     = "uniclothes-net-tf"
}

variable "metabase_port" {
  description = "Port expose pour Metabase"
  type        = number
  default     = 3000
}

variable "grafana_port" {
  description = "Port expose pour Grafana"
  type        = number
  default     = 3001
}

variable "minio_console_port" {
  description = "Port console MinIO"
  type        = number
  default     = 9001
}

variable "shell_interpreter" {
  description = "Interprete shell pour local-exec (PowerShell sur Windows)"
  type        = list(string)
  default     = ["PowerShell", "-Command"]
}
