terraform {
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
  }
}

provider "docker" {}

resource "docker_network" "uniclothes" {
  name = var.network_name
}

resource "docker_volume" "postgres_data" {
  name = "${var.project_name}_postgres_data"
}

resource "docker_volume" "minio_data" {
  name = "${var.project_name}_minio_data"
}

resource "docker_volume" "prometheus_data" {
  name = "${var.project_name}_prometheus_data"
}

resource "docker_volume" "grafana_data" {
  name = "${var.project_name}_grafana_data"
}

# Deploy the full stack via Docker Compose (Infrastructure as Code orchestration)
resource "null_resource" "docker_compose_up" {
  triggers = {
    compose_hash = filemd5("${path.module}/../docker/docker-compose.yml")
  }

  provisioner "local-exec" {
    working_dir = "${path.module}/../docker"
    command     = "docker compose up -d"
    interpreter = var.shell_interpreter
  }

  provisioner "local-exec" {
    when        = destroy
    working_dir = "${path.module}/../docker"
    command     = "docker compose down"
    interpreter = var.shell_interpreter
  }

  depends_on = [
    docker_network.uniclothes,
    docker_volume.postgres_data,
    docker_volume.minio_data,
    docker_volume.prometheus_data,
    docker_volume.grafana_data,
  ]
}
