provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project_id
  region      = var.region
}

resource "google_storage_bucket" "db_bucket" {
  name     = var.bucket_name
  location = var.region
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = var.dataset_id
  location                   = var.region
  delete_contents_on_destroy = false
}

resource "google_dataproc_cluster" "cluster" {
  name   = var.cluster_name
  region = var.region

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = "n1-standard-2"
      disk_config {
        boot_disk_size_gb = 500
      }
    }

    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-2"
      disk_config {
        boot_disk_size_gb = 500
      }
    }

  }
}
