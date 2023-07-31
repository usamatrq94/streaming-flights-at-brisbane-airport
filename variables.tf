variable "project_id" {
  type        = string
  description = "GCS project ID for Brisbane Airport Streaming data"
}

variable "bucket_name" {
  type        = string
  description = "Name of Google Storage Bucket to create"
}

variable "region" {
  type        = string
  description = "Region for GCP resources"
  default     = "australia-southeast1"
}

variable "storage_class" {
  type        = string
  description = "Storage class type for bucket."
  default     = "STANDARD"
}


variable "registry_id" {
  type        = string
  description = "Name of artifact registry repository."
}
