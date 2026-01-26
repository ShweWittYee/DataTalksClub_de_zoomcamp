terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# -------------------------------
# Postgres Image
# -------------------------------
resource "docker_image" "postgres_image" {
  name = "postgres:18"
}

# -------------------------------
# Postgres Container
# -------------------------------
resource "docker_container" "postgres_container" {
  name  = "ny_taxi_postgres"
  image = docker_image.postgres_image.name  # <- fixed, use .name

  env = [
    "POSTGRES_USER=root",
    "POSTGRES_PASSWORD=root",
    "POSTGRES_DB=ny_taxi"
  ]

  ports {
    internal = 5432
    external = 5433
  }

  volumes {
    host_path      = "${abspath("${path.module}/../ny_taxi_postgres_data")}"
    container_path = "/var/lib/postgresql/data"
  }
}

# -------------------------------
# pgAdmin Image
# -------------------------------
resource "docker_image" "pgadmin_image" {
  name = "dpage/pgadmin4"
}

# -------------------------------
# pgAdmin Container
# -------------------------------
resource "docker_container" "pgadmin_container" {
  name  = "pgadmin"
  image = docker_image.pgadmin_image.name  # <- fixed

  env = [
    "PGADMIN_DEFAULT_EMAIL=admin@admin.com",
    "PGADMIN_DEFAULT_PASSWORD=root"
  ]

  ports {
    internal = 80
    external = 8085
  }

  volumes {
    host_path      = "${abspath("${path.module}/../pgadmin_data")}"
    container_path = "/var/lib/pgadmin"
  }
}
