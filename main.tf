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
  //credentials = file(var.credentials) #use this if you don't want to set env-var GOOGLE_APPLICATION
}

# GCS storage bucket
resource "google_storage_bucket" "airport_data_lake" {
  name     = var.bucket_name
  location = var.region

  # Optional, but recommended settings:
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

# Bigquery table
resource "google_bigquery_table" "flights" {
  dataset_id = google_bigquery_dataset.brisbane-airport.dataset_id
  table_id   = "flights"

  time_partitioning {
    type = "DAY"
  }

  # schema = file("schema.json")
}
