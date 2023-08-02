terraform {
  required_version = ">=1.0"
  backend "local" {}
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "airport_data_lake" {
  name     = var.bucket_name
  location = var.region

  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  force_destroy = true
}

resource "google_storage_bucket" "orchestration" {
  name     = "prefect-deployments-dev"
  location = var.region

  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  force_destroy = true
}

# Artifact registry for containers
resource "google_artifact_registry_repository" "airport-container-registry" {
  location      = var.region
  repository_id = var.registry_id
  format        = "DOCKER"
}

# Bigquery dataset
resource "google_bigquery_dataset" "brisbane-airport" {
  dataset_id                  = "brisbaneairport"
  friendly_name               = "brisbane-airport"
  description                 = "This is a brisbane-airport dataset having list of daily incoming flights"
  location                    = var.region
  default_table_expiration_ms = 3600000
}

resource "google_compute_instance" "prefect-agent" {
  name         = "prefect-agent"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      labels = {
        my_label = "bullseye"
      }
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral public IP
    }
  }

  service_account {
    email  = "prefect@streaming-flights-brisbane.iam.gserviceaccount.com"
    scopes = ["cloud-platform"]
  }
}
